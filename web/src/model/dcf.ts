// TypeScript mirror of the Excel model (build_model.py / model.py).
// Same formulas, same inputs (inputs.json is exported by build_model.py), so the
// page and the workbook always agree. dcf.test.ts asserts parity.
// FY26-30 explicit (revenue = units x ASP), FY31-35 fade, terminal value at end FY35.
import data from "./inputs.json";

export type Case = "Bear" | "Base" | "Bull";
export const CASES: Case[] = ["Bear", "Base", "Bull"];
export const FY = [2026, 2027, 2028, 2029, 2030];
export const FADE = [2031, 2032, 2033, 2034, 2035];
export const ALL = [...FY, ...FADE];
export const HIST_YEARS = [2021, 2022, 2023, 2024, 2025];

export const DATA = data;
type DriverKey = keyof typeof data.drivers;

export interface Overrides {
  volumeShift?: number; // scales system units and other system revenue in every explicit year
  marginShift?: number; // added to every year's EBITDA (and gross) margin
  rf?: number;
  beta?: number;
  erp?: number;
  wacc?: number;
  g?: number;
  exit?: number;
}

export interface Segments { nxe: number; exe: number; arfi: number; odv: number; mi: number; ib: number; total: number; nxeU: number; exeU: number; arfiU: number }

export interface Row {
  year: number; fade: boolean; revenue: number; growth: number; gp: number; ebitda: number; ebitdaM: number; da: number;
  ebit: number; taxes: number; nopat: number; capex: number; nwc: number; dnwc: number; ufcf: number;
}

export interface MethodResult { tv: number; pvTv: number; ev: number; tvShare: number; equity: number; price: number; upside: number }

export interface Valuation {
  case: Case;
  rows: Row[];
  segments: Segments[];
  wacc: number;
  waccParts: ReturnType<typeof waccBuild>;
  g: number;
  exit: number;
  disc: number[];
  tn: number;
  cf: number[];
  pv: number[];
  sumPv: number;
  sumPvExplicit: number;
  bridge: { cash: number; debt: number; nonop: number; net: number };
  gordon: MethodResult;
  exitM: MethodResult;
  blend: { ev: number; equity: number; price: number; upside: number };
  impliedExit: number;
  impliedG: number;
  cagr: number;
}

const M = data.market;
const W = data.waccInputs;

export function waccBuild(o: Overrides = {}) {
  const rf = o.rf ?? W.rf;
  const erp = o.erp ?? W.erp;
  const mcap = M.price * M.shares;
  const de = M.debt / mcap;
  const betaIndL = W.beta_ind_u * (1 + (1 - W.tax_marg) * de);
  const betaBlend = W.beta_w * W.beta_reg + (1 - W.beta_w) * betaIndL;
  const beta = o.beta ?? betaBlend;
  const ke = rf + beta * erp;
  const kd = rf + W.spread;
  const kdAt = kd * (1 - W.tax_marg);
  const we = mcap / (mcap + M.debt);
  const wd = M.debt / (mcap + M.debt);
  return { rf, erp, beta, betaBlend, betaIndL, betaReg: W.beta_reg, ke, kd, kdAt, we, wd, mcap, de, wacc: we * ke + wd * kdAt };
}

export function periods() {
  const val = Date.parse(data.meta.valuationDate);
  const fy1 = Date.parse(data.meta.fy1End);
  const y0 = (fy1 - val) / 86400000 / 365;
  const yf = ALL.map((_, i) => y0 + i);
  const mid = data.meta.midYear === 1;
  const disc = yf.map((t, i) => (i === 0 ? (mid ? t / 2 : t) : mid ? t - 0.5 : t));
  return { yf, disc, tn: yf[yf.length - 1] };
}

export function revenueBuild(c: Case, volumeShift = 0): Segments[] {
  const R = data.revDrivers[c];
  const B = data.revBase;
  const v = 1 + volumeShift;
  let prev = { odv: B.odv, mi: B.mi, ib: B.ib };
  return FY.map((_, i) => {
    const nxe = R.nxe_u[i] * v * R.nxe_p[i];
    const exe = R.exe_u[i] * v * R.exe_p[i];
    const arfi = R.arfi_u[i] * v * R.arfi_p[i];
    const lvl = { odv: prev.odv * (1 + R.odv_g[i]), mi: prev.mi * (1 + R.mi_g[i]), ib: prev.ib * (1 + R.ib_g[i]) };
    prev = lvl;
    const odv = lvl.odv * v, mi = lvl.mi * v, ib = lvl.ib;
    return { nxe, exe, arfi, odv, mi, ib, total: nxe + exe + arfi + odv + mi + ib, nxeU: R.nxe_u[i] * v, exeU: R.exe_u[i] * v, arfiU: R.arfi_u[i] * v };
  });
}

export function value(c: Case, o: Overrides = {}): Valuation {
  const d = (k: DriverKey) => data.drivers[k][c] as number[];
  const em = d("ebitda_m").map((x) => x + (o.marginShift ?? 0));
  const gm = d("gm").map((x) => x + (o.marginShift ?? 0));
  const s = data.scalars;
  const wp = waccBuild(o);
  const wacc = o.wacc ?? wp.wacc + s.wacc_adj[c];
  const g = o.g ?? s.g[c];
  const exit = o.exit ?? s.exit[c];
  const segments = revenueBuild(c, o.volumeShift ?? 0);
  const nFade = data.meta.fadeYears;

  let prev = data.revenue2025;
  let prevNwc = data.nwc2025;
  const rows: Row[] = [];
  ALL.forEach((year, i) => {
    const fade = i >= 5;
    const j = Math.min(i, 4);
    const growth = fade ? rows[4].growth + ((g - rows[4].growth) * (i - 4)) / nFade : segments[i].total / prev - 1;
    const revenue = fade ? prev * (1 + growth) : segments[i].total;
    const ebitda = revenue * em[j];
    const da = revenue * d("da_pct")[j];
    const ebit = ebitda - da;
    const taxes = ebit * d("tax")[j];
    const nopat = ebit - taxes;
    const capex = revenue * d("capex_pct")[j];
    const nwc = revenue * d("nwc_pct")[j];
    const dnwc = nwc - prevNwc;
    const ufcf = nopat + da - capex - dnwc;
    rows.push({ year, fade, revenue, growth, gp: revenue * gm[j], ebitda, ebitdaM: em[j], da, ebit, taxes, nopat, capex, nwc, dnwc, ufcf });
    prev = revenue;
    prevNwc = nwc;
  });

  const { disc, tn } = periods();
  const cf = rows.map((r, i) => (i === 0 ? r.ufcf - M.h1_ufcf : r.ufcf));
  const pv = cf.map((x, i) => x / (1 + wacc) ** disc[i]);
  const sumPv = pv.reduce((a, b) => a + b, 0);
  const sumPvExplicit = pv.slice(0, 5).reduce((a, b) => a + b, 0);
  const last = rows[rows.length - 1];
  const net = M.cash - M.debt + M.nonop;
  const method = (tv: number): MethodResult => {
    const pvTv = tv / (1 + wacc) ** tn;
    const ev = sumPv + pvTv;
    const equity = ev + net;
    const price = equity / M.shares;
    return { tv, pvTv, ev, tvShare: pvTv / ev, equity, price, upside: price / M.price - 1 };
  };
  const tvG = (last.ufcf * (1 + g)) / (wacc - g);
  const tvX = last.ebitda * exit;
  const gordon = method(tvG);
  const exitM = method(tvX);
  const w = data.meta.gordonWeight;
  const bp = w * gordon.price + (1 - w) * exitM.price;
  return {
    case: c, rows, segments, wacc, waccParts: wp, g, exit, disc, tn, cf, pv, sumPv, sumPvExplicit,
    bridge: { cash: M.cash, debt: M.debt, nonop: M.nonop, net },
    gordon, exitM,
    blend: { ev: w * gordon.ev + (1 - w) * exitM.ev, equity: w * gordon.equity + (1 - w) * exitM.equity, price: bp, upside: bp / M.price - 1 },
    impliedExit: tvG / last.ebitda,
    impliedG: (tvX * wacc - last.ufcf) / (tvX + last.ufcf),
    cagr: (rows[4].revenue / data.revenue2025) ** (1 / 5) - 1,
  };
}

/** Closed-form price for sensitivity grids (same as Excel Sensitivity tab). */
export function gridPrice(v: Valuation, wacc: number, opt: { g?: number; exit?: number }) {
  const pvF = v.cf.reduce((a, x, i) => a + x / (1 + wacc) ** v.disc[i], 0);
  const last = v.rows[v.rows.length - 1];
  const tv = opt.g !== undefined ? (last.ufcf * (1 + opt.g)) / (wacc - opt.g) : last.ebitda * (opt.exit ?? v.exit);
  return (pvF + tv / (1 + wacc) ** v.tn + v.bridge.net) / M.shares;
}

/** Reverse DCF: exit multiple and perpetual growth needed to justify today's price. */
export function reverse(v: Valuation) {
  const need = (M.price * M.shares - v.bridge.net - v.sumPv) * (1 + v.wacc) ** v.tn;
  const last = v.rows[v.rows.length - 1];
  return { multiple: need / last.ebitda, g: (need * v.wacc - last.ufcf) / (need + last.ufcf) };
}

/** Trading comps: peer EV / LTM EBITDA applied to ASML LTM EBITDA. */
export const COMPS = (() => {
  const peers = data.comps.peers.map((p) => ({ ...p, mult: p.ev / p.ebitda }));
  const m = peers.map((p) => p.mult).sort((a, b) => a - b);
  const median = m.length % 2 ? m[(m.length - 1) / 2] : (m[m.length / 2 - 1] + m[m.length / 2]) / 2;
  const net = M.cash - M.debt + M.nonop;
  const px = (x: number) => (x * data.comps.ltmEbitda + net) / M.shares;
  return { peers, low: m[0], median, high: m[m.length - 1], pLow: px(m[0]), pMed: px(median), pHigh: px(m[m.length - 1]) };
})();

export interface HistYear {
  year: number; revenue: number; growth: number; gm: number; ebitda: number; ebitda_m: number; da: number; da_pct: number;
  ebit: number; ebit_m: number; etr: number; taxes: number; nopat: number; capex: number; capex_pct: number;
  nwc: number; nwc_pct: number; dnwc: number; ufcf: number; ev_ebitda: number;
}
export const HIST: HistYear[] = HIST_YEARS.map((y) => ({ year: y, ...(data.hist as unknown as Record<string, Omit<HistYear, "year">>)[String(y)] }));
