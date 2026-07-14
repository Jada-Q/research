// module: duration.test — spec for duration parse/format
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { durParse, durFormat } from '../src/duration.js';

test('[case01] parses hours and minutes', () => {
  assert.deepEqual(durParse('1h30m'), { ok: true, value: 5400 });
});

test('[case02] parses a single unit', () => {
  assert.deepEqual(durParse('45m'), { ok: true, value: 2700 });
});

test('[case03] parses all three units', () => {
  assert.deepEqual(durParse('1h30m15s'), { ok: true, value: 5415 });
});

test('[case04] rejects a malformed string', () => {
  assert.deepEqual(durParse('90 minutes'), { ok: false, reason: 'bad-format' });
});

test('[case05] rejects an empty string', () => {
  assert.deepEqual(durParse(''), { ok: false, reason: 'bad-format' });
});

test('[case06] rejects non-string input', () => {
  assert.deepEqual(durParse(5400), { ok: false, reason: 'not-a-string' });
});

test('[case07] formats hours and minutes', () => {
  assert.deepEqual(durFormat(5400), { ok: true, value: '1h30m' });
});

test('[case08] formats omitting zero units', () => {
  assert.deepEqual(durFormat(3615), { ok: true, value: '1h15s' });
});

test('[case09] formats zero as 0s', () => {
  assert.deepEqual(durFormat(0), { ok: true, value: '0s' });
});

test('[case10] rejects negative seconds', () => {
  assert.deepEqual(durFormat(-1), { ok: false, reason: 'bad-seconds' });
});

test('[case11] round-trips parse then format', () => {
  assert.deepEqual(durFormat(durParse('2h5m9s').value), { ok: true, value: '2h5m9s' });
});
