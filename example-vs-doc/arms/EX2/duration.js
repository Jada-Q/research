// module: duration — parse and format duration strings
import { ok, fail } from '../lib/outcome.js';

/**
 * Parse a duration string like "1h30m" into total seconds.
 * @spec durations are h/m/s units in descending order, each at most once,
 *       at least one unit present (e.g. "2h", "90m", "1h30m", "1h2m3s")
 */
export function durParse(input) {
  if (typeof input !== 'string') return fail('not-a-string');
  const m = input.trim().match(/^(?:([0-9]+)h)?(?:([0-9]+)m)?(?:([0-9]+)s)?$/);
  if (!m || (m[1] === undefined && m[2] === undefined && m[3] === undefined)) {
    return fail('bad-format');
  }
  const hours = Number(m[1] ?? 0);
  const minutes = Number(m[2] ?? 0);
  const seconds = Number(m[3] ?? 0);
  const total = hours * 3600 + minutes * 60 + seconds;
  if (!Number.isSafeInteger(total)) return fail('out-of-range');
  return ok(total);
}

/**
 * Format total seconds into "1h30m" form, omitting zero units.
 * @spec amounts are non-negative safe integers; zero formats as "0s"
 */
export function durFormat(totalSeconds) {
  if (!Number.isSafeInteger(totalSeconds) || totalSeconds < 0) {
    return fail('bad-amount');
  }
  if (totalSeconds === 0) return ok('0s');
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  let out = '';
  if (hours > 0) out += hours + 'h';
  if (minutes > 0) out += minutes + 'm';
  if (seconds > 0) out += seconds + 's';
  return ok(out);
}
