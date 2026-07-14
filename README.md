# research

可跑的、已验证的实验条目——不是笔记，不是未验证的 deep research 报告。

模式来自 Simon Willison（simonw/research，Lenny's Podcast 2026-04-02 @64:46）：
> "如果我发布一仓库未验证的 research 报告，对谁都没价值。但一旦 coding agent 写了代码、跑了代码——它就变成 actionable 的东西。"

## 条目规则

每个条目一个目录，必含三件：
1. `README.md` — 研究问题 / 协议 / 结果表 / 局限 / 怎么复跑
2. 可跑的 harness（脚本或骨架项目）
3. `data/` 或 `outputs/` — 当次实验的原始产物（判定可被复核，不是只信结论）

复用方式（Simon 的用法）：在任何 Claude 会话里说
"读 ~/Desktop/Projects/research/<条目> 的方法，测一下 <新问题>"。

## 索引

| 条目 | 日期 | 问题 | 一句话结论 |
|---|---|---|---|
| [tdd-redgreen-incantation](tdd-redgreen-incantation/) | 2026-07-14 | "red/green TDD" 咒语还有增益吗（Opus 4.8） | 已被吸收：对照组也默认写测试；咒语剩余价值 = 强制 RED 阶段（测试的阴性对照） |
| [claudemd-absorption-audit](claudemd-absorption-audit/) | 2026-07-14 | CLAUDE.md 行为条款哪些已被模型默认行为吸收（Opus 4.8） | 4 测 3 吸收；唯一在做真功的是"数字事实标注"（裸模型自信编成套税率表） |
| [example-vs-doc](example-vs-doc/) | 2026-07-14 | 单范例文件 vs 详尽风格文档，哪个更能让 agent 跟随项目约定（Fable 5） | 成文约定打平（好文档=范例=100%）；范例额外传递**不成文**微风格；项目约定不会被吸收，必须在上下文里 |
| [loop-ready-score-audit](loop-ready-score-audit/) | 2026-07-14 | loop-engineering（7676★）的 Loop Ready 分数量的是什么 | 假仓库 100/100 L3，真生产循环 26/100 L0——量的是文件命名服从度不是循环真实性（预注册预测成立） |

## 方法论共性（三条实验同一 harness 家族）

- 2×2 或双层 A/B，n=2/格（只出方向性判定，不出置信度）
- /tmp 副本隔离，agent 禁碰原目录
- **统一 fixture 独立验收，不信 agent 自报**（tdd 实验中 4 agent 全自报通过，独立验收才算数）
- 验证器自身先过阴性测试（example-vs-doc 的范例先跑 4/4；absorption 的干净房间先探针确认零注入）
- 判分器也会错：example-vs-doc 初判的 9/10 是判分正则假阳性，靠回读原始产物纠正——所以 outputs/ 必须入库
