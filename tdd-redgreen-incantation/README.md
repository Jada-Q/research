# "red/green TDD" 咒语在当前模型上还有增益吗

- **日期**: 2026-07-14 | **模型**: Opus 4.8（子 agent 显式钉 opus）| **n**: 2/组
- **断言来源**: Simon Willison, Lenny's Podcast 2026-04-02——"prompt 里写 red/green TDD 就显著改善 agent 结果"（断言诞生于 2025-11 Opus 4.5 时代）

## 协议

真实任务：修 eiken-study `merge_banks.py` 的硬编码级别 bug（只处理 3級/4級，静默丢弃 準2級/2級）。
- A 组（n=2）：裸任务 prompt
- B 组（n=2）：同 prompt + 一句 "Use red/green TDD."
- 每个 agent 独立 /tmp 副本（rsync 排除 venv 等），禁碰原目录
- 验收：主循环统一 fixture（每级 1 精确重复 + 1 新词 + 1 个 banks 不存在的幽灵级别），独立跑 4 份实现，不信自报

## 结果

| 维度 | A 对照 | B 咒语 |
|---|---|---|
| 核心修复 | 4/4 一致：`for lvl in banks:` | 同 |
| 统一 fixture 验收 | 2/2 PASS | 2/2 PASS |
| 主动写测试（没人要求） | **2/2** | 2/2 |
| 显式 RED 阶段（先证明测试能抓到 bug） | 0/2 | **2/2**（B1 还做了阴性对照：改前 5 败 5 过） |
| 测试套件行数 | 88 / 101 | 154 / 126 |

## 结论

**字面断言已失效——因为被吸收**：对照组基线已包含"写测试+自验证"。咒语剩余价值 = 强制 RED 阶段，即"验证工具先过阴性测试"的自动化版。关键模块仍值一行 prompt，买的是测试可信度，不是测试存在性。

**元教训**：prompt 技巧的半衰期 = 被模型训练吸收的速度。采纳任何"加这句就变好"前，先用本协议测当前基线。

## 数据与复跑

- `data/test_suite_{A1,A2,B1,B2}.py` — 4 个 agent 各自产出的测试套件（对比 RED 阶段差异读 B1 vs A1）
- `data/merge_banks_fixed.py` — B1 的实现（与其余 3 份仅注释差异）；已进 eiken-study 生产（commit b5fcc2f）
- 复跑：在 Claude 会话中开 4 个 subagent，2 个 prompt 带咒语 2 个不带，换成你手上任何有真 bug 的小模块；验收 fixture 参照本 README 协议自造，别用 agent 自报
- 局限：n=2、单任务、任务偏简单（一行修复）；复杂任务上咒语效果可能回升
