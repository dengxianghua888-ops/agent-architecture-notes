# Agent 架构笔记

面向产品经理、设计师和开发者的中文研究文章。研究 Agent 如何分工、Skill 如何组织，以及这些选择何时能改善用户拿到的结果。

## 首篇 · Agent 怎样分工，Skill 应该拆多细？

剪辑师收到一句改稿意见：“把最后那个拥抱换掉。想让人觉得他们认出了对方，音乐和前面都别动。”找对镜头、读懂表演、守住音轨，是同一次交付里的三个问题。文章从这场戏出发，用软件工程、客服、设备操作和视频剪辑的研究，比较固定工作流、动态委派和技能组合。

**[阅读图解长文 ↗](https://dengxianghua888-ops.github.io/agent-architecture-notes/articles/agent-and-skill-orchestration/)** · [GitHub 正文](articles/agent-and-skill-orchestration.md) · [PDF 与可编辑 Word](https://github.com/dengxianghua888-ops/agent-architecture-notes/releases/tag/v1.0.0)

![同一项改稿中，知识规定观察线索，工具负责等长替换，分工决定谁搜片、谁回看前后镜头作判断。](assets/architecture-overview.svg)

| 如果你在决定…… | 从这里读 |
| --- | --- |
| 单个 Agent、固定流程、动态分工，该用哪一种？ | [同一批素材的三种分工](https://dengxianghua888-ops.github.io/agent-architecture-notes/articles/agent-and-skill-orchestration/#coordination) |
| 该拆知识、拆工具，还是把工作委派出去？ | [拆分改变了什么](https://dengxianghua888-ops.github.io/agent-architecture-notes/articles/agent-and-skill-orchestration/#granularity) |
| 技能库扩大之后，如何找对方法、保住前后依赖？ | [从一份好方法到一个好用的库](https://dengxianghua888-ops.github.io/agent-architecture-notes/articles/agent-and-skill-orchestration/#library) |
| 指标涨了，怎样知道用户真的拿到了更好的作品？ | [公平对照与成片盲评](https://dengxianghua888-ops.github.io/agent-architecture-notes/articles/agent-and-skill-orchestration/#evaluation) |

## 查证与复用

[证据附录](notes/evidence-review.md)记录了论文修订、产品能力的版本和入口、研究共用的样本，以及 23 个视频主题的配对分差。正文中的改稿流程是设计推演；实测数字均指向各自的原始研究。资料核对至 2026 年 11 月 27 日。

可以在仓库根目录运行 `python3 scripts/check_paired_scores.py`，离线复算主题分差和重采样区间。引用文章时，请标明文章标题、项目名称和版本。提出勘误时，请附上涉及的段落、来源版本和能改变判断的证据。

撰写下一篇可从[分析文章模板](templates/article.md)开始。[阅读页排版与构建指南](templates/authoring.md)说明如何从同一份 Markdown 生成支持手机阅读与打印的页面，以及如何保留旧文章的固定地址。

## 许可

原创文章、图解和写作模板采用 [CC BY 4.0](LICENSE-CONTENT)，署名可写“Agent 架构笔记贡献者”并链接仓库。构建与分析脚本、网页模板、样式和交互代码采用 [MIT](LICENSE)。引用的论文、产品文档和第三方材料保留各自的许可。
