// module: duration — parse and format duration strings like "1h30m"
import { ok, fail } from '../lib/outcome.js';

const PARSE_RE = /^(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?$/;

/**
 * Parses a duration string such as "1h30m" into total seconds.
 * @spec input must be a non-empty string of h/m/s components in that order, each a non-negative integer with at least one component present (e.g. "2h", "1h30m", "45s").
 */
export const durParse = (input) => {
  if (typeof input !== 'string') return fail('not-a-string');
  if (input === '') return fail('bad-format');
  const match = PARSE_RE.exec(input);
  if (!match) return fail('bad-format');
  const [, hours, minutes, seconds] = match;
  const total =
    Number(hours ?? 0) * 3600 + Number(minutes ?? 0) * 60 + Number(seconds ?? 0);
  return ok(total);
};

/**
 * Formats a total number of seconds into a duration string such as "1h30m".
 * @spec input must be a non-negative integer number of seconds (zero formats as "0s"; zero-valued components are omitted).
 */
export const durFormat = (input) => {
  if (typeof input !== 'number' || !Number.isInteger(input)) {
    return fail('not-an-integer');
  }
  if (input < 0) return fail('out-of-range');
  if (input === 0) return ok('0s');
  const hours = Math.floor(input / 3600);
  const minutes = Math.floor((input % 3600) / 60);
  const seconds = input % 60;
  let result = '';
  if (hours > 0) result += `${hours}h`;
  if (minutes > 0) result += `${minutes}m`;
  if (seconds > 0) result += `${seconds}s`;
  return ok(result);
};
