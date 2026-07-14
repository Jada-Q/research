// module: duration — parse and format duration strings
import { ok, fail } from '../lib/outcome.js';

/**
 * Parse a duration string like "1h30m" into total seconds.
 * @spec durations use h/m/s units in that order, each at most once,
 *       with at least one unit present (e.g. "2h", "45m", "1h30m15s")
 */
export function durParse(input) {
  if (typeof input !== 'string') return fail('not-a-string');
  const m = input.trim().match(/^(?:([0-9]+)h)?(?:([0-9]+)m)?(?:([0-9]+)s)?$/);
  if (!m || (m[1] === undefined && m[2] === undefined && m[3] === undefined)) {
    return fail('bad-format');
  }
  const h = Number(m[1] ?? 0);
  const min = Number(m[2] ?? 0);
  const s = Number(m[3] ?? 0);
  const total = h * 3600 + min * 60 + s;
  if (!Number.isSafeInteger(total)) return fail('out-of-range');
  return ok(total);
}

/**
 * Format total seconds into "1h30m" form, omitting zero units.
 * @spec seconds are non-negative safe integers; zero formats as "0s"
 */
export function durFormat(seconds) {
  if (!Number.isSafeInteger(seconds) || seconds < 0) return fail('bad-seconds');
  if (seconds === 0) return ok('0s');
  const h = Math.floor(seconds / 3600);
  const min = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  let out = '';
  if (h > 0) out += h + 'h';
  if (min > 0) out += min + 'm';
  if (s > 0) out += s + 's';
  return ok(out);
}
