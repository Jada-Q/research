// module: duration — parse and format duration strings like "1h30m"
import { ok, fail } from '../lib/outcome.js';

const DURATION_RE = /^(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?$/;

/**
 * Parses a duration string into total seconds.
 * @spec input must be a non-empty string of ordered unit segments `<digits>h<digits>m<digits>s`, each unit optional but at least one present (e.g. "1h30m", "45s").
 */
export const durParse = (input) => {
  if (typeof input !== 'string') return fail('not-a-string');
  const match = DURATION_RE.exec(input);
  if (!match || input === '') return fail('bad-format');
  const [, hours = '0', minutes = '0', seconds = '0'] = match;
  return ok(Number(hours) * 3600 + Number(minutes) * 60 + Number(seconds));
};

/**
 * Formats a total number of seconds into a duration string like "1h30m".
 * @spec input must be a non-negative integer number of seconds; zero formats as "0s".
 */
export const durFormat = (input) => {
  if (typeof input !== 'number' || Number.isNaN(input)) return fail('not-a-number');
  if (!Number.isInteger(input) || input < 0) return fail('out-of-range');
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
