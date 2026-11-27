#!/usr/bin/env python3
"""Build a portable article reader from an ordinary Markdown source. Python 3.9+."""
import argparse
import hashlib
import html
import math
import mimetypes
import struct
import re
import shutil
import unicodedata
from collections import Counter, OrderedDict
from decimal import Decimal, InvalidOperation
from pathlib import Path
from string import Template
from urllib.parse import quote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
ESC = html.escape
TOKEN = re.compile(r'\[([^\]]+)\]\(([^()\s]*(?:\([^()\s]*\)[^()\s]*)*)\)|`([^`]+)`|\*\*(.+?)\*\*')
COMMENT = re.compile(r'^<!--\s*([\w-]+)\s*:\s*(.*?)\s*-->$')
HEAD = re.compile(r'^(#{1,6})\s+(.+?)\s*#*\s*$')
LIST = re.compile(r'^\s*(?:(\d+)[.)]|([-*+]))\s+(.+)$')
IMAGE = re.compile(r'^!\[([^\]]*)\]\(([^()\s]*(?:\([^()\s]*\)[^()\s]*)*)\)$')
SAFE_ID = re.compile(r'^[\w.-]+$', re.UNICODE)
FIGURES = {"control": 3, "compare": 4, "recut": 3, "paired": 2}


def plain(text):
    return TOKEN.sub(lambda m: m.group(1) or m.group(3) or m.group(4), text).strip()


def valid_url(url):
    parts = urlsplit(url)
    if parts.scheme:
        return parts.scheme in {"https", "http", "mailto"} and (
            parts.scheme == "mailto" or bool(parts.netloc))
    return not (url.startswith(("/", "\\")) or "\\" in url)


def heading_id(title):
    text = unicodedata.normalize("NFKC", plain(title)).lower().strip()
    text = "".join(c for c in text if c.isalnum() or c.isspace() or c in "_-")
    result = re.sub(r"\s+", "-", text)[:90].strip("-")
    return result or "section-" + hashlib.sha256(title.encode()).hexdigest()[:8]


def cells(text):
    return [s.strip().replace("\\|", "|") for s in re.split(r'(?<!\\)\|', text.strip().strip('|'))]


def table_start(lines, i):
    if i + 1 >= len(lines) or "|" not in lines[i]:
        return False
    sep = cells(lines[i+1])
    return len(sep) == len(cells(lines[i])) and all(re.fullmatch(r':?-{3,}:?', s) for s in sep)


def parse(text):
    lines = text.splitlines()
    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line:
            continue
        if COMMENT.match(line):
            blocks.append(("meta", COMMENT.match(line).groups()))
        elif line.startswith("<!--"):
            # Ordinary editorial comments stay in the Markdown source.
            while "-->" not in line and i < len(lines):
                line = lines[i]
                i += 1
        elif line.startswith("```"):
            code = []
            while i < len(lines) and not lines[i].lstrip().startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            blocks.append(("code", "\n".join(code)))
        elif IMAGE.fullmatch(line):
            blocks.append(("image", IMAGE.fullmatch(line).groups()))
        elif HEAD.match(line):
            mark, label = HEAD.match(line).groups()
            blocks.append(("heading", (len(mark), label)))
        elif line in ("---", "***"):
            blocks.append(("rule", None))
        elif table_start(lines, i - 1):
            head = cells(line)
            rows = []
            i += 1
            while i < len(lines) and "|" in lines[i] and lines[i].strip() and not lines[i].lstrip().startswith(('<!--', '#')):
                row = cells(lines[i])
                if len(row) != len(head):
                    raise ValueError(f"Table row {i + 1} has {len(row)} cells; expected {len(head)}")
                rows.append(row)
                i += 1
            blocks.append(("table", (head, rows)))
        elif line.startswith(">"):
            parts = [line[1:].strip()]
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                parts.append(lines[i].lstrip()[1:].strip())
                i += 1
            blocks.append(("quote", " ".join(parts)))
        elif LIST.match(line):
            pattern = LIST.match(line)
            numbered = bool(pattern.group(1))
            items = [pattern.group(3)]
            while i < len(lines):
                follow = LIST.match(lines[i])
                if not follow or bool(follow.group(1)) != numbered:
                    break
                items.append(follow.group(3))
                i += 1
            blocks.append(("list", (numbered, items)))
        else:
            parts = [line]
            while i < len(lines) and lines[i].strip():
                follow = lines[i].strip()
                if (HEAD.match(follow) or IMAGE.fullmatch(follow) or LIST.match(follow) or follow.startswith(("<!--", ">", "```"))
                        or table_start(lines, i) or follow in ("---","***")):
                    break
                parts.append(follow)
                i += 1
            blocks.append(("text", " ".join(parts)))
    return blocks


class Reader:
    def __init__(self, repo, source_path, branch, source_dir):
        self.source_dir = source_dir
        self.metadata = {}
        self.images = {}
        self.repo = repo
        self.source_path = source_path
        self.branch = branch
        self.sources = OrderedDict()
        self.headings = []
        self.ids = set()
        self.figures = 0

    def link(self, url):
        if not valid_url(url):
            raise ValueError(f"Unsupported Markdown link target: {url!r}")
        if url.startswith(("#","http://","https://","mailto:")) or not self.repo:
            return url
        return f"{self.repo}/blob/{quote(self.branch, safe='')}/{self.source_path.parent.as_posix()}/{url}"

    def inline(self, text):
        result = []
        end = 0
        for item in TOKEN.finditer(text):
            result.append(ESC(text[end:item.start()]))
            label, target, code, strong = item.groups()
            if label is not None:
                href = self.link(target)
                result.append(f'<a href="{ESC(href, quote=True)}">{ESC(label)}</a>')
                if href.startswith(("https://","http://")):
                    self.sources.setdefault(href, label)
            elif code is not None:
                result.append(f"<code>{ESC(code)}</code>")
            else:
                result.append(f"<strong>{self.inline(strong)}</strong>")
            end = item.end()
        result.append(ESC(text[end:]))
        return "".join(result)

    def media_url(self, src):
        if not valid_url(src):
            raise ValueError(f"Unsupported image URL: {src!r}")
        if src.startswith("https://"):
            return src
        path = (self.source_dir / src).resolve()
        if not path.is_file() or path.suffix.lower() not in {".svg",".png",".webp",".jpg",".jpeg",".gif",".avif"}:
            raise ValueError(f"Missing or unsupported local image: {src!r}")
        name = path.name
        if name in self.images and self.images[name] != path:
            name = f"{path.stem}-{hashlib.sha256(path.read_bytes()).hexdigest()[:8]}{path.suffix}"
        self.images[name] = path
        return "./assets/media/" + quote(name)

    def image(self, alt, src):
        href = self.media_url(src)
        return (f'<figure class="illustration"><a href="{ESC(href)}" aria-label="查看原图：{ESC(alt)}"><img src="{ESC(href)}" '
                f'loading="lazy" decoding="async" alt="{ESC(alt)}"></a></figure>')

    def get_id(self, title, explicit):
        if explicit and not SAFE_ID.fullmatch(explicit):
            raise ValueError(f"Invalid heading id: {explicit}")
        base = explicit or heading_id(title)
        key = base
        suffix = 2
        while key in self.ids:
            if explicit:
                raise ValueError(f"Duplicate heading id: {key}")
            key = f"{base}-{suffix}"
            suffix += 1
        self.ids.add(key)
        return key

    def table(self, headers, rows):
        th = "".join(f'<th scope="col">{self.inline(cell)}</th>' for cell in headers)
        body = "".join("<tr>"+"".join(f"<td>{self.inline(cell)}</td>" for cell in row)+"</tr>" for row in rows)
        return f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'

    def diagram(self, kind, headers, rows):
        if kind not in FIGURES or len(headers) != FIGURES[kind] or not rows:
            raise ValueError(f"figure: {kind} needs a body and {FIGURES.get(kind, '?')} columns")
        self.figures += 1
        prefix = f"figure-{self.figures}"
        if kind == "paired":
            return self.paired(headers, rows)
        h = [self.inline(s) for s in headers]
        entries = [[self.inline(s) for s in row] for row in rows]
        if kind == "control":
            items = "".join(f'<li><strong>{a}</strong><div class="owner">{b}</div><div class="desc">{c}</div></li>' for a,b,c in entries)
            if len(rows) > 3:
                labels = "".join(f"<span>{label}</span>" for label in h)
                return (f'<figure class="diagram" aria-label="控制权流程"><div class="flow-labels" aria-hidden="true">{labels}</div>'
                        f'<ol class="flow vertical">{items}</ol></figure>')
            return f'<figure class="diagram" aria-label="控制权流程"><ol class="flow">{items}</ol></figure>'
        if kind == "compare":
            items = []
            for row in entries:
                fields = "".join(f'<dt>{label}</dt><dd>{value}</dd>' for label, value in zip(h[1:],row[1:]))
                items.append(f'<div class="route"><strong>{row[0]}</strong><dl>{fields}</dl></div>')
            return '<figure class="diagram" aria-label="同一素材的方案比较"><div class="routes">' + "".join(items) + '</div></figure>'
        tabs, panels = [], []
        for i,row in enumerate(entries,1):
            key = f"{prefix}-step-{i}"
            tabs.append(f'<button id="{key}-button" type="button" aria-controls="{key}">{ESC(plain(rows[i-1][0]))}</button>')
            fields = "".join(f'<div><dt>{label}</dt><dd>{value}</dd></div>' for label,value in zip(h[1:],row[1:]))
            panels.append(f'<div class="step-info" id="{key}" data-step-panel><strong>{row[0]}</strong><dl>{fields}</dl></div>')
        return (f'<figure class="diagram" data-recut aria-label="局部重剪步骤"><div class="step-nav" aria-label="选择重剪步骤" hidden>{"".join(tabs)}</div>'
                + "".join(panels) + '<div class="step-actions" hidden><button type="button" data-prev>← 上一步</button>'
                + '<span class="position" aria-live="polite"></span><button type="button" data-next>下一步 →</button></div></figure>')

    def paired(self, headers, rows):
        points = []
        for label, score in rows:
            try:
                value = Decimal(score.replace("−","-").strip())
                if not value.is_finite():
                    raise InvalidOperation
            except InvalidOperation:
                raise ValueError(f"Paired chart expects a finite signed decimal, got {score!r}")
            points.append((value,label))
        points.sort()
        low,high = min(points[0][0],0),max(points[-1][0],0)
        span = float(high-low) or 1
        estimate = span/7
        scale = 10**math.floor(math.log10(estimate))
        step = next(v*scale for v in (1,2,2.5,5,10) if v*scale>=estimate)
        left = math.floor(float(low)/step)*step - .18*step
        right = math.ceil(float(high)/step)*step + .18*step
        if right-left<step:
            left,right=-step,step
        xpos = lambda x: (float(x)-left)/(right-left)*100
        def score(v, decimals=None):
            return (f"{v:+.{decimals}f}" if decimals is not None else f"{v:+g}").replace("-","−") if v else "0"
        ticks = []
        for i in range(math.ceil(left/step),math.floor(right/step)+1):
            x = i*step
            cls = "zero" if i==0 else "crowded" if i%2 else ""
            ticks.append(f'<span class="plot-tick {cls}" style="--x:{xpos(x):.4f}%"><span>{score(x)}</span></span>')
        dots = []
        counts = Counter()
        for x,label in points:
            kind = "neg" if x<0 else "zero" if x==0 else "pos"
            dots.append(f'<span class="plot-dot {kind}" title="{ESC(plain(label))} {score(x,2)}" style="--x:{xpos(x):.4f}%;--stack:{counts[x]}"></span>')
            counts[x]+=1
        tails = []
        for x,label in (points[0],points[-1]):
            tails.append(f'<span class="{"negative" if x<0 else "positive"}">{self.inline(label)}　{score(x,2)}</span>')
        return (f'<figure class="diagram"><div class="chart-top">{"".join(tails)}</div><div class="dotplot-wrap">'
                + '<div class="dotplot" aria-hidden="true">'+"".join(ticks+dots)+'</div>'
                + f'<div class="axis-label">{self.inline(headers[1])}</div></div>'
                + '<figcaption>每个点代表一个主题。相同分差的点向上堆叠。</figcaption>'
                + f'<details class="fig-details"><summary>查看 {len(points)} 个主题的分差</summary>'
                + self.table(headers,rows)+'</details></figure>')

    def render(self, blocks):
        title, date, lead = "", "", ""
        content = []
        pending_id = pending_figure = None
        opened = False
        for kind, obj in blocks:
            if kind == "meta":
                key,value = obj
                if key in ("share-description", "share-image", "release"):
                    self.metadata[key] = value
                if key=="date": date=value
                if key=="id": pending_id=value
                if key=="figure": pending_figure=value
                continue
            if pending_figure and kind!="table":
                raise ValueError("figure directive must be followed by a Markdown table")
            if kind == "heading":
                level,label=obj
                if level==1:
                    if title:
                        raise ValueError("An article may have only one H1")
                    title=plain(label)
                    continue
                key=self.get_id(label,pending_id)
                pending_id=None
                if level==2:
                    if opened: content.append("</section>")
                    content.append(f'<section class="chapter" id="{ESC(key)}">')
                    opened=True
                    self.headings.append((key,plain(label)))
                tag=min(level,6)
                addr=f' id="{ESC(key)}"' if level!=2 else ""
                content.append(f'<h{tag}{addr}>{self.inline(label)}<a class="anchor" href="#{ESC(key)}" aria-label="本节链接">#</a></h{tag}>')
            elif kind=="quote":
                if title and not content and not lead:
                    lead=f'<div class="lead"><p>{self.inline(obj)}</p></div>'
                else: content.append(f'<blockquote><p>{self.inline(obj)}</p></blockquote>')
            elif kind=="table":
                content.append(self.diagram(pending_figure,*obj) if pending_figure else self.table(*obj))
                pending_figure=None
            elif kind=="image": content.append(self.image(*obj))
            elif kind=="text": content.append(f'<p>{self.inline(obj)}</p>')
            elif kind=="rule": content.append("<hr>")
            elif kind=="code": content.append(f"<pre><code>{ESC(obj)}</code></pre>")
            elif kind=="list":
                numbered,items=obj
                tag="ol" if numbered else "ul"
                content.append(f'<{tag}>'+ "".join(f'<li>{self.inline(x)}</li>' for x in items)+f'</{tag}>')
        if opened: content.append("</section>")
        if not title or pending_figure or pending_id:
            raise ValueError("Missing H1 or unfinished figure/heading directive")
        return title,date,lead,"\n".join(content)


def default_site(repo):
    parsed = urlsplit(repo)
    parts = parsed.path.strip("/").split("/")
    if parsed.hostname != "github.com" or len(parts) != 2:
        return ""
    owner, name = parts
    if not re.fullmatch(r"[A-Za-z0-9-]+", owner) or not re.fullmatch(r"[A-Za-z0-9._-]+", name):
        return ""
    host = owner.lower() + ".github.io"
    return f"https://{host}" + ("" if name.lower() == host else "/" + name)


def social_metadata(title, description, site_name, canonical, cover, cover_file):
    entries = [
        ("property","og:type","article"), ("property","og:locale","zh_CN"),
        ("property","og:site_name",site_name), ("property","og:title",title),
        ("property","og:description",description),
    ]
    if canonical:
        entries.append(("property","og:url",canonical))
    if cover:
        entries.extend([("property","og:image",cover), ("property","og:image:alt",title),
                        ("name","twitter:image",cover)])
        mime = mimetypes.guess_type(urlsplit(cover).path)[0]
        if mime:
            entries.append(("property","og:image:type",mime))
        if mime == "image/png" and cover_file:
            with cover_file.open("rb") as image:
                header = image.read(24)
            if len(header) != 24 or header[:8] != bytes.fromhex("89504e470d0a1a0a") or header[12:16] != b"IHDR":
                raise ValueError("Share image has an invalid PNG header")
            width, height = struct.unpack(">II", header[16:24])
            entries.extend([("property","og:image:width",str(width)), ("property","og:image:height",str(height))])
    entries.extend([("name","twitter:card","summary_large_image" if cover else "summary"),
                    ("name","twitter:title",title), ("name","twitter:description",description)])
    return "\n  ".join(f'<meta {key}="{ESC(name)}" content="{ESC(value)}">' for key,name,value in entries)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',required=True,type=Path)
    ap.add_argument('--out',type=Path,default=Path('docs'))
    ap.add_argument('--repo-url',default='')
    ap.add_argument('--source-path',help='Markdown file path in the repository; defaults to relative source path')
    ap.add_argument('--branch',default='main')
    ap.add_argument('--site-url',help='Public site root, such as https://example.org/journal; GitHub Pages is inferred from --repo-url')
    ap.add_argument('--slug',help='Stable ASCII article identifier, defaults to the source filename')
    ap.add_argument('--archive-only',action='store_true',help='Build only the permanent article URL; keep the home page')
    ap.add_argument('--collection',default='Agent 架构笔记')
    args=ap.parse_args()
    repo=args.repo_url.rstrip('/')
    if repo and (urlsplit(repo).scheme!='https' or not urlsplit(repo).netloc):
        ap.error('--repo-url must be a public HTTPS repository URL')
    if args.source_path:
        source_path=Path(args.source_path)
    else:
        try: source_path=args.source.resolve().relative_to(Path.cwd())
        except ValueError: source_path=Path(args.source.name)
    if source_path.is_absolute() or '..' in source_path.parts:
        ap.error('--source-path must be repository-relative')
    text=args.source.read_text(encoding='utf-8-sig')
    reader=Reader(repo,source_path,args.branch,args.source.resolve().parent)
    title,date,lead,body=reader.render(parse(text))
    template=Template((ROOT/'templates/reader.html').read_text(encoding='utf-8'))
    toc='<ol class="toc-list">'+''.join(f'<li><a href="#{ESC(k)}" data-section="{ESC(k)}">{ESC(t)}</a></li>' for k,t in reader.headings)+'</ol>'
    references=''
    if reader.sources and not any(any(t in name for t in ('参考资料','参考来源','资料来源','文献索引')) for _,name in reader.headings):
        items="".join(f'<li><a href="{ESC(u)}">{ESC(s)}</a></li>' for u,s in reader.sources.items())
        references=f'<details class="sources"><summary>文中出处（{len(reader.sources)}）</summary><ol>{items}</ol></details>'
    description = reader.metadata.get("share-description") or html.unescape(re.sub("<[^>]*>", "", lead)) or title
    description = description[:200]
    site = (args.site_url or default_site(repo)).rstrip("/")
    if site and (urlsplit(site).scheme != "https" or not urlsplit(site).netloc):
        ap.error("--site-url must be a public HTTPS site root")
    cover = ""
    cover_file = None
    cover_spec = reader.metadata.get("share-image")
    if cover_spec:
        cover = reader.media_url(cover_spec)
        if not cover.startswith("https://"):
            cover_file = (reader.source_dir / cover_spec).resolve()
            cover = site + "/" + cover.removeprefix("./") if site else ""
    release = reader.metadata.get("release")
    if release and (urlsplit(release).scheme != "https" or not urlsplit(release).netloc):
        ap.error("release must be a public HTTPS attachment or release URL")
    download = f'<a href="{ESC(release)}">本版 PDF 与 Word ↗</a>' if release else ""
    source_url=(f'{repo}/blob/{quote(args.branch,safe="")}/{quote(source_path.as_posix(),safe="/")}' if repo else './source.md')
    actions=f'<a href="{ESC(repo)}">GitHub 仓库 ↗</a>' if repo else f'<a href="{ESC(source_url)}">Markdown 原文</a>'
    slug = args.slug or args.source.stem
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
        ap.error("Use a stable lowercase ASCII filename or pass --slug")
    absolute_canonical = f"{site}/articles/{slug}/" if site else ""
    social = social_metadata(title, description, args.collection, absolute_canonical, cover, cover_file)
    archive = args.out / "articles" / slug
    archive.mkdir(parents=True, exist_ok=True)
    destinations = [(archive, "../../", "./")]
    if not args.archive_only:
        destinations.append((args.out, "./", f"./articles/{slug}/"))
    for destination, root_url, permalink in destinations:
        relative_body = body.replace('src="./assets/media/', f'src="{root_url}assets/media/')
        relative_body = relative_body.replace('href="./assets/media/', f'href="{root_url}assets/media/')
        effective_source = source_url if repo else "./source.md"
        rendered = template.substitute(
            title=ESC(title), description=ESC(description[:200]), collection=ESC(args.collection),
            social=social, canonical=ESC(absolute_canonical or permalink), download=download,
            home=root_url, assets=root_url+"assets/", permalink=permalink, actions=actions,
            source_url=ESC(effective_source), toc=toc, lead=lead, article=relative_body, sources=references,
            date=f'<div class="date">{ESC(date)}</div>' if date else '',
        )
        (destination/"index.html").write_text(rendered, encoding="utf-8")
        if not repo:
            (destination/"source.md").write_text(text, encoding="utf-8")
    assets=args.out/'assets'
    assets.mkdir(exist_ok=True)
    for name in ('reader.css','reader.js'):
        shutil.copyfile(ROOT/'assets'/name, assets/name)
    if reader.images:
        media = assets/'media'
        media.mkdir(exist_ok=True)
        for name, path in reader.images.items():
            shutil.copyfile(path, media/name)
    (args.out/'.nojekyll').touch()
    print(f"{archive}/index.html · {len(reader.headings)} sections · {reader.figures} figures · {len(reader.sources)} sources")


if __name__ == '__main__':
    main()
