// module: currency.test — spec for currency parse/format
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { curParse, curFormat } from '../src/currency.js';

test('[case01] parses a plain yen string', () => {
  assert.deepEqual(curParse('¥1,234'), { ok: true, value: 1234 });
});

test('[case02] rejects a malformed string', () => {
  assert.deepEqual(curParse('1234'), { ok: false, reason: 'bad-format' });
});

test('[case03] formats an integer amount', () => {
  assert.deepEqual(curFormat(50000), { ok: true, value: '¥50,000' });
});

test('[case04] rejects negative amounts', () => {
  assert.deepEqual(curFormat(-1), { ok: false, reason: 'bad-amount' });
});
