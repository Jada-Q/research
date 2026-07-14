// module: duration.test — spec for duration parse/format
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { durParse, durFormat } from '../src/duration.js';

test('[case01] parses an hour-minute string', () => {
  assert.deepEqual(durParse('1h30m'), { ok: true, value: 5400 });
});

test('[case02] parses single-unit strings', () => {
  assert.deepEqual(durParse('90m'), { ok: true, value: 5400 });
  assert.deepEqual(durParse('45s'), { ok: true, value: 45 });
});

test('[case03] parses a full h/m/s string', () => {
  assert.deepEqual(durParse('1h2m3s'), { ok: true, value: 3723 });
});

test('[case04] rejects a malformed string', () => {
  assert.deepEqual(durParse('1x30m'), { ok: false, reason: 'bad-format' });
});

test('[case05] rejects an empty string', () => {
  assert.deepEqual(durParse(''), { ok: false, reason: 'bad-format' });
});

test('[case06] rejects non-string input', () => {
  assert.deepEqual(durParse(5400), { ok: false, reason: 'not-a-string' });
});

test('[case07] formats seconds into hour-minute form', () => {
  assert.deepEqual(durFormat(5400), { ok: true, value: '1h30m' });
});

test('[case08] formats a full h/m/s value', () => {
  assert.deepEqual(durFormat(3723), { ok: true, value: '1h2m3s' });
});

test('[case09] formats zero as 0s', () => {
  assert.deepEqual(durFormat(0), { ok: true, value: '0s' });
});

test('[case10] rejects negative amounts', () => {
  assert.deepEqual(durFormat(-1), { ok: false, reason: 'bad-amount' });
});

test('[case11] round-trips parse and format', () => {
  const parsed = durParse('2h5s');
  assert.equal(parsed.ok, true);
  assert.deepEqual(durFormat(parsed.value), { ok: true, value: '2h5s' });
});
