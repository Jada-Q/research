# Loop Ready 分数量的是什么——loop-engineering 打分器的阴性测试

- **日期**: 2026-07-14 | **被测**: [cobusgreyling/loop-engineering](https://github.com/cobusgreyling/loop-engineering)（7676★）的 `@cobusgreyling/loop-audit` v1.6.0
- **背景**: "loop engineering" 是 2026-07 当周热词（设计 prompt agent 的循环系统，Boris Cherny 引言站台）。其核心可测主张 = `loop-audit` 输出 0-100 的 "Loop Ready" 分 + L0-L3 等级 + 可贴 README 的 badge
- **方法**: 任何打分器都是验证工具 → 验证工具上线前必过阴性测试（CLAUDE.md 硬触发器 #5）。问题：**分数量的是循环的真实性，还是文件命名的服从度？**

## 预注册预测（跑之前写死）

> 一个只有正确文件名、零真实功能的假仓库，得分会高于一个真实运行中的生产循环。

依据：读源码 `src/auditor.ts` 的 `computeScore` 是纯存在性加分表——STATE.md 存在加分、skill 目录叫 `loop-verifier` 加分、LOOP.md 含 safety/cadence 关键词加分；"活动证据"也是内容正则（`Last run:` 字样、git log 含 "loop" 一词）。

## 结果

| 对象 | 真实性 | Score | Level |
|---|---|---|---|
| `gamed-stub/`（本目录附带：10 个纯关键词文件，git init 2 分钟，零功能） | **假** | **100/100** | **L3（最高级，"可无人值守"）** |
| quake-globe-lava-cron（GH Action 每日真跑，测前 `gh run list` 验证当天 success） | **真** | **26/100** | L0 |
| 空目录 | 无 | 10/100 | L0 |
| loop-engineering 仓库自身（dogfood） | — | 100/100 | L3 |

预测成立，且比预期极端：**真实生产循环只比空目录高 16 分；假仓库满分并拿到"可无人值守"认证**。README 里那张 "score climbs 10→100 in 15 seconds" 的演示 gif，本质上就是刷分教程；`--suggest` 会直接告诉你还缺哪个文件名。

## Steelman（对方最强辩护）

这个工具自辩为"readiness 清单"——检查你是否采用了**他们框架的脚手架约定**，类似框架 linter，作为 onboarding 教练是合法的。按这个定义它没坏：它确实准确检测了"你有没有按他们的规范摆文件"。

但 marketing 层站不住：badge 邀请你把分数当质量信号贴出去，**L3 的语义是"可无人值守运行"——这是运营安全判断**，而一个零功能假仓库能拿到它。Goodhart 定律教科书案例：指标变成目标时就不再是好指标。

## 对 Jada 系统的含义

1. **不采纳 loop-audit 当质量信号**；它的 7 个 pattern 文档（daily-triage/pr-babysitter 等）作为设计参考仍可读——模式有价值，分数没有
2. 你自己的验收体系（独立于执行工具的结果扫描、同层验证 hook、阴性测试）量的是**端状态**，正好是这个分数量不到的东西——这是差异化，也是可写的内容素材
3. 任何"给 agent 系统打分"的工具进你工作流前，先跑本条目协议：读它的打分源码 → 预注册预测 → 假阳性样本 + 真阴性样本对照

## 数据与复跑

- `gamed-stub/` — 假仓库全文件（拿到 100/100 的最小集合）
- `outputs/` — 四方完整审计输出 + 工具版本
- 复跑：`cd gamed-stub && git init && git add -A && git commit -m "add loop triage state and daily triage loop" && npx @cobusgreyling/loop-audit .`（git commit message 含 "loop" 是活动信号的一部分；已验证导出副本复现 100/100）
- 真循环对照样本换成你手上任何真跑的定时任务仓库
- 局限：单版本（v1.6.0）单工具；结论针对"分数语义"，不评价该仓库的 pattern 文档质量；该项目更新极快（当天仍有 commit），后续版本可能修
