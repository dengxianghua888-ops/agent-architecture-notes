# Agent 架构研究的证据与适用范围

核对日期为 2026 年 11 月 27 日。推理投入、任务通过率、成片偏好是三种不同的指标。下面按产品版本、实验对照和视频评审方式列出关键证据，供引用时核对。

## 产品能力取决于版本与入口

|问题|原始资料支持的结论|
|---|---|
|Claude 的思考强度能换来多少效果？|在 Anthropic 的 SWE-bench Pro 编程子集上，Opus 5.5 从 high 调至 xhigh，解题率从 95.3% 到 96.7%，每题平均费用从 0.29 到 0.74 美元。high 汇总两次运行，xhigh 只跑一次。该表未给 max，也不能据此推算订阅用量。[厂商原表](https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence#tune-effort)|
|Ultracode 和推理档位能否分别设置？|v2.1.284 起，会话内的 `/effort ultracode` 保持当前档位；启动参数 `claude --effort ultracode` 同时设置 xhigh，仍受显式环境设置和上限影响。运行时可按脚本并行派活、分支与重跑。脚本可以明确哪些条目进入复核，复核者仍须回到证据判断。[配置](https://code.claude.com/docs/en/model-config#adjust-effort-level) · [工作流运行规则](https://code.claude.com/docs/en/workflows)|
|示例中有多少条声明被复核？|Claude Agent SDK 教程先核验十条声明，再让怀疑者重读其中初判获支持的四条，四条均维持原判。单次运行耗时约 1.3 分钟、花费 0.60 美元。198,723 tokens 是最后显示的进度采样。教程缺少等预算单代理对照。[提示、输出与答案](https://platform.claude.com/cookbook/claude-agent-sdk-08-dynamic-workflows)|
|Codex、ChatGPT Work 和 API 能否视作同一个产品？|Work 的 Ultra 在合资格环境可主动委派；OpenAI 的程序化工具调用让 JavaScript 组合获准工具。Codex v0.172.0 的集成测试还覆盖了特定配置下由程序派生子代理。CSV 批量 Agent Jobs 曾在 2 月合入，7 月被移除。单个旧 PR 无法证明今天的客户端仍有该功能。[Work 与 Codex](https://learn.chatgpt.com/docs/agent-configuration/subagents) · [程序化工具调用](https://developers.openai.com/api/docs/guides/tools-programmatic-tool-calling) · [实现测试](https://github.com/openai/codex/blob/3d86e43b075adeba2193ec5c22ac92f55afd82e6/codex-rs/core/tests/suite/code_mode_agent_message_tests.rs#L29-L72) · [引入](https://github.com/openai/codex/pull/10935) · [移除](https://github.com/openai/codex/pull/34413)|
|Skill 能否随 MCP 服务一起提供？|SEP-2640 已定稿。扩展规格仍处于 Beta，可列出 Skill、获取信息并以资源形式读取文件。使用还取决于宿主支持，知识的交付渠道与执行质量需要分别验收。[扩展固定版本说明](https://github.com/modelcontextprotocol/ext-skills/blob/v0.1.0/README.md)|

## 技能实验有哪些独立证据

- **先选好技能。** SkillsBench v1 的平均增益为 16.2 个百分点。v4 扩展到 87 项任务、18 组模型与执行环境，任务宏平均通过率由 33.9% 升至 50.5%，13/87 项下降。后续滚动榜已有 27 配置，不能把论文均值套到新榜。两个版本共享实验来源，不能计作两次独立验证。[v1](https://arxiv.org/abs/2602.12670v1) · [v4](https://arxiv.org/html/2602.12670v4) · [榜单](https://www.skillsbench.ai/)
- **换成公开库中的工程技能。** SWE-Skills-Bench v1 测了 49 枚；10 月 27 日的 v2 测 98 枚，在仓库绑定的需求上完成 3,920 对有无 Skill 的比较。需求检查平均通过率 76.6%→76.9%，4 枚显著正向、2 枚显著负向、92 枚未检出显著效应。没检出差异仍允许存在较小效应。[v1](https://arxiv.org/abs/2603.15401v1) · [v2](https://arxiv.org/html/2603.15401v2)
- **再测如何发现与组织技能。** 一项研究复用 84 项 SkillsBench 任务。Opus 4.6 强制预载精选技能为 55.4%，在含精选技能的约 3.4 万候选池中检索为 40.1%，无技能为 35.4%。另一项固定 Skill 与配套资源，在 41 项任务上改变组织说明，GPT＋Codex 的平铺说明为 52.03%，显式依赖为 58.54%；DeepSeek＋OpenClaw 的阶段说明与依赖图同为 51.22%。两项都用了 SkillsBench 系列任务，不能作为两个独立业务场景，也未随机改变同一知识的拆分粒度。[模拟生产检索](https://arxiv.org/html/2604.04323) · [组织说明对照表 7](https://arxiv.org/html/2610.08875v2)
- **检索、复用与学习各有任务边界。** Graph-of-Skills 的奖励提高 7.0 点、总 token 下降 56.7%，对应 GPT-5.2 Codex 在 SkillsBench 相对全量加载的结果。Voyager 在 Minecraft 中根据环境反馈累积可执行技能库，证明这种环境里能复用行为。电影剪辑的技能是否还能迁移到陌生素材，需要另测；检索出同名技能、成功运行工具和做出观众喜欢的成片应分别记录。[图检索](https://aclanthology.org/2026.emnlp-main.2614/) · [Voyager](https://arxiv.org/abs/2305.16291)

## 视频研究让谁看了什么

**AgentSkillOS 与 VideoAgent。** 前者 30 项制品任务中有六项教育动画，模型裁判读取抽帧和文件属性。后者在 Claude Sonnet 3.7 的视频任务上移除图优化后，任务图成功率从 0.93 降至 0.69。另有 26 人参与成片评价。24 个百分点是任务图指标，不能当作观众偏好的变化。[AgentSkillOS 方法](https://arxiv.org/html/2603.02176) · [VideoAgent 正式发表版](https://aclanthology.org/2026.emnlp-main.949/) · [消融与人评](https://arxiv.org/html/2606.23327v2)

**Crayotter 的 23 个主题。** 三位评审分别为四套系统打分。五分制均分依次为 Crayotter 3.40、ChatCut 3.23、CapCut-Mate 2.44、CutClaw 1.70。这里比较的是论文中的具体配置。我们以表 3 每位评审的原始分计算主题内的系统差，避开了表中展示均值的四舍五入。Crayotter 相比 ChatCut 有 15 个主题得分更高、1 个持平、7 个更低，平均差为 **+0.1681 分**。[论文评测设置与附录 B 表 3](https://arxiv.org/html/2606.07636v2#A2)

从 23 个主题中有放回抽取 23 个，每次保留原主题的系统和评审配对。重复 20,000 次，百分位法的近似 95% 区间为 **−0.2059 至 +0.5507 分**，含零。这项补算描述主题之间的波动，沿用同三位评审；更换评审、基础模型或任务集合带来的不确定性未被估计。仓库根目录运行 `python3 scripts/check_paired_scores.py` 即可复算。脚本保存按主题顺序排列的差值，无需联网。[复算脚本](../scripts/check_paired_scores.py)

**Timeline-Bench 的原论文与后续榜单。** 9 月论文有 16 组配置、56 项真实编辑任务、896 次尝试，125 次通过。771 次失败中，562 次只在质量测试失分。43 位剪辑师做出 2,589 次盲选，2,582 次可判；据此校准了自动质量指标。论文最佳配置完成 15/56，评分时留出该配置自身的投票。11 月 27 日的榜有 19 组，新增配置最高达 18/56，使用冻结阈值，未做这批成片的人工盲评。两个分数各有适用范围，它们的差无法说明观众偏好改变了多少。[论文](https://arxiv.org/abs/2609.35143) · [盲评方法](https://timelinebench.tensortest.com/docs/human-study) · [榜单阈值与新增配置](https://timelinebench.tensortest.com/leaderboard)
