# 单范例文件 vs 详尽风格文档——哪个更能让 agent 跟随项目约定

- **日期**: 2026-07-14 | **模型**: Fable 5（会话默认继承）| **n**: 2/臂
- **断言来源**: Simon Willison——"single example file proves more effective than lengthy documentation; agents are phenomenally good at sticking to existing patterns"

## 协议

骨架项目 `skeleton/`（jp-utils）内嵌**故意任意、模型猜不出**的约定：自定义 Outcome 类型（不是 {data,error}）、3 字母函数前缀、kebab-case 错误码、`@spec` JSDoc、`[caseNN]` 测试标题。
- EX 臂：给单范例模块 `currency.js` + 其测试，**无文档**
- DOC 臂：给详尽 `STYLE.md`（steelman，约定全枚举），**无范例**
- 同 prompt（"新增 duration 模块…遵循项目现有约定"），零约定泄漏
- 范例先过阴性测试（自身 4/4 pass）再开跑

## 结果

| | EX（范例） | DOC（文档） |
|---|---|---|
| 成文约定 10 marker | 10/10, 10/10 | 10/10, 10/10 |
| 测试实跑 | 15/15 pass | 15/15, 12/12 pass |
| **不成文微风格** | 2/2 `export function`（同范例） | 2/2 `export const` 箭头（文档没写这条，他们模仿了目录里唯一可见代码 lib/outcome.js 的风格） |

## 结论

1. **成文层打平**：好文档=单范例=100% 跟随，Simon 断言在强模型+steelman 文档下效应量≈0（现实文档很少这么全，现实中范例优势应更大）
2. **范例的真优势**：传递作者没想到要写的约定——agent 会照抄目录里能看到的任何代码
3. 结合 absorption-audit：项目约定**不会被吸收**，必须在上下文里；最优形态 = 1 个好范例 + 猜不出的硬约定（禁 throw/自定义类型）1 行文字点名

## 数据与复跑

- `skeleton/` — 完整骨架（STYLE.md + src-currency.js 范例 + outcome.js；组臂时二选一放入）
- `arms/{EX1,EX2,DOC1,DOC2}/` — 4 臂原始产物（对比 EX1 与 DOC1 的 duration.js 开头即见微风格分叉）
- `grade.py` — 判分器（**已修正初版 bug**：`export const durX` 也算 M3 合规；初判 9/10 是正则假阳性——判分器自身要被原始产物复核）
- 复跑：cp skeleton 组出两臂各 2 份 → 4 个 subagent 同 prompt → `python3 grade.py arms/*`；换任务（如 percentage 模块）防我这次的题目特化
- 局限：n=2/臂、单任务、DOC 是 steelman；未测第三臂（范例+文档叠加）
