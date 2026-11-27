# 从一篇 Markdown 生成阅读页

编辑仓库里的文章源文件，再从仓库根目录构建。下例会将阅读页、样式、脚本和文中的本地图片写入 `docs/`。将该目录作为静态站点根目录即可，站点可以放在域名下任意子路径。构建依赖 Python 3.9 或更高版本及其标准库。

```sh
python3 scripts/build_site.py \
  --source articles/agent-and-skill-orchestration.md \
  --out docs \
  --repo-url https://github.com/dengxianghua888-ops/agent-architecture-notes
```

`--branch` 默认为 `main`。`--collection` 设置站点名称。若从仓库以外的目录构建，可用 `--source-path` 指定 Markdown 在仓库中的相对路径，让“查看 Markdown 原文”指向正确文件。

## 文章结构

文章以一级标题开始。日期用 `<!-- date: 2026 年 11 月 27 日 -->`，紧随其后的第一个引用段作为导语。二级标题自动进入导航。标题自带链接，若希望改标题后仍能沿用旧链接，在标题前单写 `<!-- id: control-flow -->`，填写短而稳定的标识。

支持普通段落、二级和三级标题、引用、单层列表、加粗、行内代码、代码块、链接和标准 Markdown 表格。图片单独成行，例如 `![技能检索流程](../assets/skill-discovery.svg)`。图片替代文本说明图中的结论或动作。网络与本地图片都可用，优先采用仓库中能随文章一起查看的原图。

来源链接放在其支持的主张旁边。阅读页保留内联链接，并在文末汇集出处。若正文另设“参考资料”“参考来源”“资料来源”或“文献索引”章节，就用该章节代替自动目录。

## 让同一张表成为图解

在标准表格之前加入独立的图示指令。表头和单元格来自文章，GitHub 读者直接看到原表。阅读页为同一份数据提供不同读法。

| 指令 | 表格按顺序填写 | 呈现方式 |
|---|---|---|
| `<!-- figure: control -->` | 阶段、谁决定、判断依据或动作 | 有序流程，每一步注明控制者和依据 |
| `<!-- figure: compare -->` | 路线名、处理方式、收益、代价 | 同一组素材上，按共同维度比较多条路线 |
| `<!-- figure: recut -->` | 步骤、依赖或受影响对象、验证方法 | 可逐步检视，也可直接选择步骤。禁用脚本或打印时展示全部步骤 |
| `<!-- figure: paired -->` | 主题名、带符号的数值差 | 零线及相同分差的堆叠点，附可展开原表 |

例如，在两列分差表的第二列表头中写“平均分差（A 减 B，分）”，在邻近正文交代计分尺度、正负方向、样本和出处。每一行只放一个主题及其实际差值。程序会在构建时检查数值和各图示所需的列数。

预览时打开 `docs/index.html`，也可运行以下命令，然后通过浏览器访问本地服务。

```sh
python3 -m http.server --directory docs 8000
```

## 再发布一篇，保留前文链接

每篇文章第一次构建就有固定地址 `articles/<slug>/`。把这个地址用于分享、书签和 README 的目录，首页用于当期文章。文件名（或首次构建时指定的 `--slug`）决定地址。文章改标题时保留原 slug。

发布第二篇时，先用 `--archive-only` 构建旧文，再正常构建本期。两篇固定地址将同时存在，首页显示本期。这两行也能从空输出目录完整重建文章。增加更多旧文时按同样方式逐篇构建。`--archive-only` 只写指定文章和共用站点文件。

```sh
python3 scripts/build_site.py --source articles/agent-and-skill-orchestration.md --archive-only --out docs --repo-url https://github.com/dengxianghua888-ops/agent-architecture-notes
python3 scripts/build_site.py --source articles/next-study.md --out docs --repo-url https://github.com/dengxianghua888-ops/agent-architecture-notes
```

本地配图使用与本主题有关的独立文件名，让旧文原有的图片链接持续有效。

## 分享预览与本期下载

页面使用中文标题和导语生成分享预览。要单独撰写预览摘要或为某篇文章提供封面、版本下载，在该篇 Markdown 的日期下方填写对应注释，未提供的字段可以略去。

```markdown
<!-- share-description: 这篇文章解决的问题与它采用的证据。 -->
<!-- share-image: ../assets/本篇分享封面.png -->
<!-- release: https://github.com/OWNER/REPO/releases/tag/v1.0.0 -->
```

聊天应用读取固定文章地址的 Open Graph 元数据。本地 PNG 会复制到公开媒体目录，尺寸从文件读取。项目采用自有域名时，构建命令加 `--site-url https://example.org/journal`，让分享图片和文章的规范链接指向正确站点。标准 GitHub Pages 地址会按 GitHub 仓库地址推导。下载项只出现在声明版本地址的文章页尾。
