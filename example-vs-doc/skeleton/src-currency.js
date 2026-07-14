// module: currency — parse and format yen amount strings
import { ok, fail } from '../lib/outcome.js';

/**
 * Parse a currency string like "¥1,234" into an integer amount.
 * @spec currency strings are yen, comma-grouped, prefixed with ¥
 */
export function curParse(input) {
  if (typeof input !== 'string') return fail('not-a-string');
  const m = input.trim().match(/^¥([0-9][0-9,]*)$/);
  if (!m) return fail('bad-format');
  const n = Number(m[1].replaceAll(',', ''));
  if (!Number.isSafeInteger(n)) return fail('out-of-range');
  return ok(n);
}

/**
 * Format an integer amount into "¥1,234" form.
 * @spec amounts are non-negative safe integers
 */
export function curFormat(amount) {
  if (!Number.isSafeInteger(amount) || amount < 0) return fail('bad-amount');
  return ok('¥' + amount.toLocaleString('en-US'));
}
