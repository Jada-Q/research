# jp-utils 项目编码规范

本项目是一个小型 JavaScript 工具库（ESM，`"type": "module"`）。所有代码必须遵循以下约定。

## 1. 模块文件结构

- 业务模块放 `src/<module>.js`，测试放 `test/<module>.test.js`，共享基建放 `lib/`。
- 每个文件第一行必须是模块头注释，格式固定：
  `// module: <模块名> — <一句英文描述>`
  （注意是小写 `module:`、模块名后用 em dash `—` 连接描述。测试文件的模块名写 `<模块名>.test`。）
- ESM 相对导入必须带 `.js` 扩展名。

## 2. 错误处理：Outcome 模式（本项目最重要的约定）

- **任何可失败的函数禁止 throw**。统一返回 Outcome 对象：成功 `{ ok: true, value }`，失败 `{ ok: false, reason }`。
- 必须通过 `lib/outcome.js` 提供的 `ok(value)` / `fail(reason)` 辅助函数构造，不要手写对象字面量。
- `reason` 是**kebab-case 的短错误码字符串**（如 `not-a-string`、`bad-format`、`out-of-range`），不是人类可读句子，不是 Error 对象。
- 入参校验也走 Outcome（先校验类型再校验格式），不用 TypeError。

## 3. 命名约定

- 每个模块选定一个**3 字母小写前缀**（取模块名前 3 个字母），模块内所有导出函数都以该前缀开头，camelCase。例如 `payment` 模块导出 `payParse`、`payFormat`。
- 只用具名导出（named export），禁止 default export。

## 4. 文档注释

- 每个导出函数必须带 JSDoc 块注释：第一行是一句英文功能描述，随后必须有一行以 `@spec ` 开头，用一句话写明该函数的输入契约（什么样的输入是合法的）。

## 5. 测试约定

- 测试框架用 Node 内置 `node:test`（`import { test } from 'node:test'`），断言用 `node:assert/strict` 并优先 `assert.deepEqual` 整体比较 Outcome 对象。
- 每个 test 标题格式固定：`[caseNN] 一句英文描述`，NN 从 01 起按顺序编号，如 `[case01] parses a plain yen string`。
- 成功路径和失败路径都要覆盖：每个导出函数至少一个成功 case + 一个失败 case，失败 case 用 `deepEqual` 断言精确的 `reason` 错误码。
- 测试直接 `node --test` 可跑，无第三方依赖。
