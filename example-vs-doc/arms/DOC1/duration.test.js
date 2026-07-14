// module: duration.test — tests for duration parsing and formatting
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { durParse, durFormat } from '../src/duration.js';

test('[case01] parses a combined hours and minutes string', () => {
  assert.deepEqual(durParse('1h30m'), { ok: true, value: 5400 });
});

test('[case02] parses a single-unit hours string', () => {
  assert.deepEqual(durParse('2h'), { ok: true, value: 7200 });
});

test('[case03] parses a full hours, minutes and seconds string', () => {
  assert.deepEqual(durParse('1h2m3s'), { ok: true, value: 3723 });
});

test('[case04] parses a seconds-only string', () => {
  assert.deepEqual(durParse('45s'), { ok: true, value: 45 });
});

test('[case05] fails on non-string input', () => {
  assert.deepEqual(durParse(90), { ok: false, reason: 'not-a-string' });
});

test('[case06] fails on an empty string', () => {
  assert.deepEqual(durParse(''), { ok: false, reason: 'bad-format' });
});

test('[case07] fails on units in the wrong order', () => {
  assert.deepEqual(durParse('30m1h'), { ok: false, reason: 'bad-format' });
});

test('[case08] fails on garbage input', () => {
  assert.deepEqual(durParse('abc'), { ok: false, reason: 'bad-format' });
});

test('[case09] formats seconds into hours and minutes', () => {
  assert.deepEqual(durFormat(5400), { ok: true, value: '1h30m' });
});

test('[case10] formats seconds into a full h/m/s string', () => {
  assert.deepEqual(durFormat(3723), { ok: true, value: '1h2m3s' });
});

test('[case11] formats zero seconds as 0s', () => {
  assert.deepEqual(durFormat(0), { ok: true, value: '0s' });
});

test('[case12] omits zero-valued middle components', () => {
  assert.deepEqual(durFormat(3601), { ok: true, value: '1h1s' });
});

test('[case13] fails on non-integer input', () => {
  assert.deepEqual(durFormat('5400'), { ok: false, reason: 'not-an-integer' });
});

test('[case14] fails on negative input', () => {
  assert.deepEqual(durFormat(-1), { ok: false, reason: 'out-of-range' });
});

test('[case15] round-trips parse and format', () => {
  const parsed = durParse('12h5m9s');
  assert.deepEqual(durFormat(parsed.value), { ok: true, value: '12h5m9s' });
});
