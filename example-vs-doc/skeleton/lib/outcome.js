// module: outcome — shared result type helpers
export const ok = (value) => ({ ok: true, value });
export const fail = (reason) => ({ ok: false, reason });
