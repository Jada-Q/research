// module: duration.test — tests for duration parse and format
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { durParse, durFormat } from '../src/duration.js';

test('[case01] parses hours and minutes into total seconds', () => {
  assert.deepEqual(durParse('1h30m'), { ok: true, value: 5400 });
});

test('[case02] parses a single unit string', () => {
  assert.deepEqual(durParse('45s'), { ok: true, value: 45 });
});

test('[case03] parses all three units combined', () => {
  assert.deepEqual(durParse('2h5m10s'), { ok: true, value: 7510 });
});

test('[case04] fails on non-string input', () => {
  assert.deepEqual(durParse(90), { ok: false, reason: 'not-a-string' });
});

test('[case05] fails on malformed duration string', () => {
  assert.deepEqual(durParse('30m1h'), { ok: false, reason: 'bad-format' });
});

test('[case06] fails on empty string', () => {
  assert.deepEqual(durParse(''), { ok: false, reason: 'bad-format' });
});

test('[case07] formats seconds into hours and minutes', () => {
  assert.deepEqual(durFormat(5400), { ok: true, value: '1h30m' });
});

test('[case08] formats zero seconds as 0s', () => {
  assert.deepEqual(durFormat(0), { ok: true, value: '0s' });
});

test('[case09] formats a full hour without empty units', () => {
  assert.deepEqual(durFormat(3600), { ok: true, value: '1h' });
});

test('[case10] fails on non-number input', () => {
  assert.deepEqual(durFormat('5400'), { ok: false, reason: 'not-a-number' });
});

test('[case11] fails on negative seconds', () => {
  assert.deepEqual(durFormat(-1), { ok: false, reason: 'out-of-range' });
});

test('[case12] round-trips parse and format', () => {
  const parsed = durParse('2h5m10s');
  assert.deepEqual(durFormat(parsed.value), { ok: true, value: '2h5m10s' });
});
