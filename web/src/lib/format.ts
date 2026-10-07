const nf = (dp: number) => new Intl.NumberFormat("en-GB", { minimumFractionDigits: dp, maximumFractionDigits: dp });

export const eur = (x: number, dp = 0) => `€${nf(dp).format(x)}`;
export const pct = (x: number, dp = 1) => `${nf(dp).format(x * 100)}%`;
export const signedPct = (x: number, dp = 1) => `${x >= 0 ? "+" : "-"}${nf(dp).format(Math.abs(x) * 100)}%`;
export const mult = (x: number, dp = 1) => `${nf(dp).format(x)}x`;
export const num = (x: number, dp = 0) => nf(dp).format(x);
/** EUR millions to a compact label: 292,553 -> €292.6bn, 9,038 -> €9.0bn, 740 -> €740m */
export const eurm = (m: number, dp = 1) => {
  const s = m < 0 ? "-" : "";
  const a = Math.abs(m);
  return a >= 1000 ? `${s}€${nf(dp).format(a / 1000)}bn` : `${s}€${nf(0).format(a)}m`;
};
export const fyLabel = (y: number) => `FY${String(y).slice(2)}${y <= 2025 ? "A" : "E"}`;
