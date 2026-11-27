# 待核与待补清单

更新于 2026 年 11 月 27 日，对应文章《Agent 怎样分工，Skill 该拆多细？》第二版。

本轮调研在云端会话中进行，arxiv.org、huggingface.co、alphaxiv.org、timelinebench.tensortest.com、developers.openai.com、cognition.ai 等站点无法直接打开，网页搜索额度在后段也用尽。所以，一部分 2026 年预印本的数字只来自搜索摘要或二手转述。正文给这些数字加了 †。本清单写明每一项要核什么、核完怎样回填，供后续用 Codex 或人工补齐。

## 一、这篇文章需要哪些知识，哪些已经落实

| 知识模块 | 文章用来回答什么 | 当前状态 | 能否在本环境补齐 |
| --- | --- | --- | --- |
| 基本概念：Agent、工作流、Skill、工具、子代理、状态、MCP | 名词表与改稿流程 | 已核：官方文档与规范，第一版已逐条核对 | 已完成 |
| 知识拆分：技能是否有用、发现与路由损失、组织方式 | 第三节 | 主体已核（SkillsBench v4、SWE-Skills-Bench v2、2604.04323、2610.08875 为第一版核过的表格）；负迁移、SkillSeek 等新增数字为摘要级 | 部分；新增项需打开 arXiv 原文 |
| 接口拆分：工具粒度、嵌套、代码化调用 | 第四节 | MCP-GRANITE、SkillCraft 主数字已核；Anthropic 工具检索与程序化调用为一手阅读；Cassette-Editor 与 SkillCraft 无技能基线为摘要级 | 部分 |
| 执行拆分：多代理收益、公平基线、交接 | 第五节 | 2512.08296 v3、MM-ContextFold、PACE（GitHub 一手）、Anthropic 多代理系统（一手）已核；Google 博客的 45% 与 17.2×/4.4× 为博客原文，未对照论文表格 | 大体完成 |
| 状态与写入安全 | 第六节 | 开源项目（Resolve MCP、Premiere MCP）为一手阅读；Descript 为厂商自述；幂等键与逐笔撤销的量化研究未写进正文 | 正文已避开未核数字 |
| 剪辑评测与模型感知能力 | 第七节 | Timeline-Bench 主数字已核；Gemini 抽帧、TemporalBench、EBU R128 为一手或成熟文献；VEBench、MEDit-Bench 与“836 次自称成功”为摘要级 | 部分 |
| 评测统计：pass^k、样本量、聚类、成对分差 | 第八节 | 全部为公式计算或已有复算脚本 | 已完成 |
| 真实案例：短剧付费试拍、影述技能库 | 第九、十节 | 来自本组织公开仓库的原始记录 | 已完成 |
| 商业剪辑产品的内部架构与可靠性 | 未进正文 | 只有 Descript 的厂商案例；Adobe、CapCut/剪映、Kapwing、OpusClip 等缺一手资料 | 不能，需放行对应站点或人工调研 |
| 中文行业数据（AI 短剧产量、成本、良品率） | 未进正文 | 多为券商测算与媒体转述，口径互相矛盾 | 不能，需原始报告 |
| 剪辑领域的受控对照（原子工具 vs 时间线中间表示 vs 代码） | 正文作为推论处理 | 未找到同预算的公开对照实验 | 不能，需自己做实验 |

## 二、正文标 † 的数字

每项核对完成后：数值一致就删去正文的 †，并在[证据附录](evidence-review.md)补上版本和表号；数值不同就按原文改正文，并在本表“结果”列写明改动；原文找不到就删去该句或改成定性表述。

| 编号 | 正文位置 | 当前说法 | 来源 | 要核什么 | 结果 |
| --- | --- | --- | --- | --- | --- |
| T1 | 知识拆分 · 好方法有用 | 模型自生成的技能中约四分之一出现负迁移 | [arXiv 2605.23899](https://arxiv.org/pdf/2605.23899) | 25% 的分母（技能条目还是任务×配置）、所用模型 | 待核 |
| T2 | 同上 | 同一 Skill 在不同配置下效应符号会翻转 | [arXiv 2610.08875](https://arxiv.org/html/2610.08875) | 36.78% 的出处表格与定义 | 待核 |
| T3 | 同上 | 技能诱发的失败中，选了完全无关技能的只占很小一部分 | [arXiv 2608.11888](https://arxiv.org/html/2608.11888v1) | 307 个失败、1.6% 的分类口径 | 待核 |
| T4 | 同上 | Timeline-Bench 约 1,900 词剪辑指导无可检出提升 | [Timeline-Bench](https://arxiv.org/abs/2609.35143) | 指导字数、对照组设计与置信区间 | 待核 |
| T5 | 长路由规则 | 朴素 BM25 在 4 个设置中 3 个持平或超过精修循环 | [SkillSeek](https://arxiv.org/html/2609.38822) | 设置定义、指标、同行评审出处（AACL 2026） | 待核 |
| T6 | 一次成功留下什么 | 预算对齐后自动积累经验的方法优势不明显 | [EMNLP 2026](https://aclanthology.org/2026.emnlp-main.1657/) | 比较的方法（AWM、ASI、ReasoningBank）与预算口径 | 待核 |
| T7 | 嵌套也有代价 | SkillCraft 中 GPT-5.2 不用技能为 109/126 | [项目页](https://skillcraft-website.github.io/page/) · [论文](https://arxiv.org/html/2603.00718v2) | 表 3 的无技能基线 | 待核 |
| T8 | 内部原子，外部收窄 | Cassette-Editor 完整环境 92/93，基础工具 48/93 | [arXiv 2610.37690](https://arxiv.org/abs/2610.37690) | 版本号与表格；另有 100% 对 55%、89% 对 47% 两种读法 | 待核 |
| T9 | 剪辑的难点 | 896 次运行中 Agent 自称成功 836 次 | [Timeline-Bench](https://arxiv.org/abs/2609.35143) | 原文是否给出该数、定义是什么 | 待核 |
| T10 | 机器的眼睛 | 剪辑技法识别最好的商用模型约三成多 | [VEBench](https://arxiv.org/abs/2605.03276) | 34.65% 的任务定义与模型 | 待核 |
| T11 | 同上 | 叙事剪辑 A/B 评审存在明显位置偏差 | [MEDit-Bench](https://arxiv.org/html/2607.25300) | 偏差幅度（转述称约 35.4 个百分点）与评审模型 | 待核 |
| T12 | 真实案例 | 自动评审逐条挑选与人的一致率中等 | [arXiv 2608.26105](https://arxiv.org/pdf/2608.26105) | 0.60 / 0.54 / 0.77 三个数的定义 | 待核 |

## 三、第一版引用需要复核

| 编号 | 第一版说法 | 本轮发现 | 要做什么 |
| --- | --- | --- | --- |
| R1 | SkillRouter 引用 v5 | 本轮只检索到 v1 与 v4 | 打开 arXiv 版本历史，确认最新版本号后改链接 |
| R2 | SkillLearnBench 正式论文（COLM 2026）10.17% / 31.08% / 74.50% | 本轮只找到预印本 2604.20087，未找到 COLM 录用页 | 打开正文引用的 proceedings PDF，核对表 2；失效则改引预印本并注明版本 |
| R3 | SkillsBench v4 中 13/87 项任务下降 | 只在本仓库附录中出现，本轮未核到原表 | 对照 v4 逐任务表 |
| R4 | Graph-of-Skills 奖励 +7.0、token −56.7% | arXiv 摘要另有 +43.6% 的说法，两者口径不同 | 写明各自的指标与比较对象 |
| R5 | MCP-GRANITE 四档约 36/42/49/42% | 正文新增“单一总入口时 28.2% 未调用工具”，来自论文结论段 | 对照表 II 和失败分析，确认 28.2% 的分母 |
| R6 | 2604.04323 中“按任务精修可找回部分损失” | 二手转述给出 48.2%，摘要只给出 Terminal-Bench 2.0 上 57.7% 到 65.5% | 确认 SkillsBench 条件下的精修数字后，决定是否把具体数写进正文 |

## 四、本轮没能调查清楚的问题

1. **商业剪辑 Agent 的真实做法。** Descript Underlord、Adobe Premiere 的 AI 助手、CapCut/剪映的 AI 功能、Kapwing、OpusClip、Captions 等，缺少一手的架构说明和可靠性数据。
2. **剪辑领域的同预算对照。** 原子工具直调、时间线中间表示加编译器、让模型写代码，三种方式在同一剪辑任务上的对比，至今没有公开实验。这需要我们自己设计实验，见影述仓库的迭代方案。
3. **自动评审与专业剪辑师的一致率。** 特别是在商用模型（Seedance、Kling、Veo 等）生成的候选上，模型选片与剪辑师选片的一致率。
4. **多机位、访谈类剪辑的 Agent 研究。** 本轮没有找到可靠的学术工作。
5. **多代理失败分类的比例。** MAST 的 14 类失败中，各类占比在二手来源之间不一致。
6. **长上下文退化的定量数据。** Chroma 的 context rot 报告和 NoLiMa 的模型数量，在不同版本之间存在出入。
7. **中文 AI 短剧行业数据。** 市场规模、良品率、每分钟成本的口径互相矛盾，需要原始报告。

## 五、交给 Codex 时的执行说明

- 运行环境需能访问 arxiv.org、aclanthology.org、proceedings.colm.cc、timelinebench.tensortest.com、github.com。
- 一次只处理一个编号。打开原文，记录版本号（如 v2）、表号或页码、原文数字，再按第二节的规则回填。
- 修改正文后在仓库根目录重新构建阅读页：

```sh
python3 scripts/build_site.py --source articles/agent-and-skill-orchestration.md --out docs --repo-url https://github.com/dengxianghua888-ops/agent-architecture-notes
```

- 不改动没有新证据支持的判断句；如果某项核对结果会改变文中的结论（例如 Cassette-Editor 的差距大幅缩小），在本表“结果”列写明，并在正文对应段落补一句限定。
