import { ArrowCounterClockwise, CaretDown, DownloadSimple } from "@phosphor-icons/react";
import { scaleLinear } from "d3-scale";
import { line } from "d3-shape";
import { AnimatePresence, motion, useInView, useReducedMotion } from "motion/react";
import { useMemo, useRef, useState } from "react";
import { XLSX_HREF } from "../components/chrome";
import { Chapter, CountUp, EASE, Reveal, Segmented, useChapterTime, useSize } from "../components/ui";
import { type Case, CASES, DATA, gridPrice, HIST, reverse, value } from "../model/dcf";
import { eur, eurm, fyLabel, mult, pct, signedPct } from "../lib/format";
import { TODAY, useBaseline, useStore, useValuation } from "../state/valuation";

const MKT = DATA.market.price;

/* ------------------------------------------------------------- Stress test heatmap */
export function StressTest() {
  const ref = useChapterTime(TODAY);
  const v = useValuation();
  const base = useBaseline();
  const { ov, setOv } = useStore();
  const [table, setTable] = useState<"g" | "exit">("g");
  const [hover, setHover] = useState<[number, number] | null>(null);
  const gridRef = useRef<HTMLDivElement>(null);
  const seen = useInView(gridRef, { once: true, amount: 0.3 });
  const reduce = useReducedMotion();

  const waccs = Array.from({ length: 9 }, (_, i) => base.wacc + (i - 4) * 0.005);
  const rows = table === "g" ? Array.from({ length: 9 }, (_, i) => base.g + (i - 4) * 0.0025) : Array.from({ length: 9 }, (_, i) => base.exit + (i - 4) * 2);
  const grid = useMemo(() => rows.map((r) => waccs.map((w) => gridPrice(v, w, table === "g" ? { g: r } : { exit: r }))), [v, table, base]); // eslint-disable-line
  const liveW = v.wacc, liveR = table === "g" ? v.g : v.exit;
  const isLive = (i: number, j: number) => Math.abs(waccs[j] - liveW) < 1e-6 && Math.abs(rows[i] - liveR) < 1e-6;
  const shade = (p: number) => {
    const r = p / MKT;
    if (r >= 1) { const a = Math.min(1, 0.25 + (r - 1) / 0.6); return { bg: `color-mix(in srgb, var(--accent) ${a * 100}%, transparent)`, fg: a > 0.55 ? "var(--accent-ink)" : "var(--ink)" }; }
    const a = Math.min(0.85, (1 - r) / 0.75);
    return { bg: `color-mix(in srgb, var(--ink) ${a * 70}%, transparent)`, fg: a > 0.6 ? "var(--bg)" : "var(--ink)" };
  };
  const fmtR = (r: number) => (table === "g" ? pct(r, 2) : mult(r, 0));
  const hv = hover ? { w: waccs[hover[1]], r: rows[hover[0]], p: grid[hover[0]][hover[1]] } : null;
  const above = grid.flat().filter((p) => p >= MKT).length;

  return (
    <Chapter id="stress" innerRef={ref} className="px-4 py-24 md:px-8 md:py-32">
      <div className="flex flex-wrap items-end justify-between gap-6">
        <Reveal>
          <h2 className="display max-w-[16ch] text-4xl font-semibold md:text-5xl">Stress test.</h2>
          <p className="mt-5 max-w-[56ch] text-lg leading-relaxed text-muted">
            81 valuations at once. Blue cells clear today's {eur(MKT)}; grey cells do not. Click a cell to run the whole page on those inputs.
          </p>
        </Reveal>
        <Segmented<"g" | "exit"> label="Sensitivity table" value={table} onChange={setTable}
          options={[{ value: "g", label: "WACC x growth" }, { value: "exit", label: "WACC x multiple" }]} />
      </div>
      <div className="mt-12 grid gap-10 lg:grid-cols-12">
        <div ref={gridRef} className="overflow-x-auto lg:col-span-9">
          <table className="num w-full min-w-[620px] border-collapse text-center text-[13px]">
            <thead>
              <tr>
                <th className="p-2 text-left text-xs font-normal text-faint">{table === "g" ? "g" : "EV/EBITDA"} \ WACC</th>
                {waccs.map((w, j) => <th key={j} className={`p-2 text-xs font-normal ${j === 4 ? "text-ink" : "text-faint"}`}>{pct(w, 2)}</th>)}
              </tr>
            </thead>
            <tbody>
              {grid.map((row, i) => (
                <tr key={i}>
                  <th className={`p-2 text-left text-xs font-normal ${i === 4 ? "text-ink" : "text-faint"}`}>{fmtR(rows[i])}</th>
                  {row.map((p, j) => {
                    const s = shade(p);
                    const center = i === 4 && j === 4;
                    return (
                      <td key={j} className="p-0.5">
                        <motion.button onMouseEnter={() => setHover([i, j])} onMouseLeave={() => setHover(null)} onFocus={() => setHover([i, j])}
                          onClick={() => setOv(table === "g" ? { wacc: waccs[j], g: rows[i] } : { wacc: waccs[j], exit: rows[i] })}
                          aria-label={`WACC ${pct(waccs[j], 2)}, ${fmtR(rows[i])}: ${eur(p)}`}
                          className={`relative block h-10 w-full transition-transform active:scale-[0.97] ${isLive(i, j) ? "outline-2 outline-offset-1 outline-accent" : ""}`}
                          style={{ background: s.bg, color: s.fg, boxShadow: center ? "inset 0 0 0 2px var(--ink)" : undefined }}
                          initial={reduce ? false : { opacity: 0, scale: 0.85 }} animate={seen || reduce ? { opacity: 1, scale: 1 } : {}}
                          transition={{ duration: 0.4, delay: reduce ? 0 : (i + j) * 0.035, ease: EASE }}>
                          {Math.round(p).toLocaleString("en-GB")}
                        </motion.button>
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
          <p className="mt-3 text-xs text-faint">Implied price (EUR) using the live forecast. Black frame = {base.case} case centre; blue outline = inputs currently applied. Grid steps: WACC 0.5%, {table === "g" ? "g 0.25%" : "multiple 2.0x"}.</p>
        </div>
        <aside className="grid content-start gap-4 lg:col-span-3">
          <AnimatePresence mode="wait">
            {hv ? (
              <motion.div key="h" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.15 }} className="grid gap-3">
                <p className="text-sm text-muted">Cell</p>
                <p className="num display text-6xl font-medium">{eur(hv.p)}</p>
                <p className="num text-sm">{signedPct(hv.p / MKT - 1)} vs market</p>
                <dl className="num grid grid-cols-2 gap-3 border-t border-line pt-3 text-sm">
                  <div><dt className="text-xs text-faint">WACC</dt><dd>{pct(hv.w, 2)}</dd></div>
                  <div><dt className="text-xs text-faint">{table === "g" ? "Terminal g" : "Exit multiple"}</dt><dd>{fmtR(hv.r)}</dd></div>
                </dl>
              </motion.div>
            ) : (
              <motion.div key="s" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.15 }} className="grid gap-3">
                <p className="text-sm text-muted">Cells at or above market</p>
                <p className="num display text-6xl font-medium">{above}<span className="text-2xl text-faint"> / 81</span></p>
                <p className="text-sm leading-relaxed text-muted">
                  {table === "g" ? "The Gordon method needs a far lower WACC and higher growth than the base case before value reaches the share price." :
                    "The Exit method reaches the share price once multiples approach the high 20s, close to ASML's own 5-year average of ~30x."}
                </p>
              </motion.div>
            )}
          </AnimatePresence>
          {(ov.wacc !== undefined) && (
            <button onClick={() => setOv({ wacc: undefined, g: undefined, exit: undefined })} className="flex items-center gap-2 text-sm text-accent hover:underline">
              <ArrowCounterClockwise size={14} /> Clear cell selection
            </button>
          )}
        </aside>
      </div>
    </Chapter>
  );
}

/* ------------------------------------------------------------- Three futures */
export function Futures() {
  const ref = useChapterTime(2028.5);
  const { scenario, setScenario, ov } = useStore();
  const all = useMemo(() => Object.fromEntries(CASES.map((c) => [c, value(c, ov)])) as Record<Case, ReturnType<typeof value>>, [ov]);
  const [cref, w] = useSize<HTMLDivElement>();
  const seen = useInView(cref, { once: true, amount: 0.4 });
  const reduce = useReducedMotion();
  const h = Math.min(380, Math.max(260, w * 0.45));
  const m = { t: 20, r: 96, b: 28, l: 28 };
  const years = [2021, 2022, 2023, 2024, 2025, ...[2026, 2027, 2028, 2029, 2030]];
  const x = scaleLinear().domain([2021, 2030]).range([m.l, w - m.r]);
  const y = scaleLinear().domain([0, 85000]).range([h - m.b, m.t]);
  const histPts = HIST.map((d) => [d.year, d.revenue] as [number, number]);
  const mk = line<[number, number]>().x((d) => x(d[0])).y((d) => y(d[1]));
  const g = DATA.guidance2030;
  return (
    <Chapter id="futures" innerRef={ref} className="px-4 py-24 md:px-8 md:py-32">
      <Reveal>
        <h2 className="display max-w-[16ch] text-4xl font-semibold md:text-5xl">Three futures.</h2>
        <p className="mt-5 max-w-[56ch] text-lg leading-relaxed text-muted">
          One reported past, three internally consistent forecasts. Pick a case to run the whole page on it.
        </p>
      </Reveal>
      <div ref={cref} className="mt-12">
        <svg width={w} height={h} role="img" aria-label="Revenue paths for Bear, Base and Bull cases">
          <rect x={x(2029.6)} width={x(2030) - x(2029.6) + 6} y={y(g.rev_high)} height={y(g.rev_low) - y(g.rev_high)} fill="var(--surface-2)" />
          <text x={x(2030) + 6} y={y(g.rev_low) + 16} fontSize={11} fill="var(--faint)">2030 target</text>
          <text x={x(2030) + 6} y={y(g.rev_low) + 30} fontSize={11} fill="var(--faint)">€44-60bn</text>
          {[20000, 40000, 60000, 80000].map((t) => <g key={t}><line x1={m.l - 20} x2={w - m.r} y1={y(t)} y2={y(t)} stroke="var(--line)" /><text x={m.l - 20} y={y(t) - 4} fontSize={11} fill="var(--faint)" className="num">€{t / 1000}bn</text></g>)}
          {years.map((yr) => <text key={yr} x={x(yr)} y={h - 8} textAnchor="middle" fontSize={11} className="num" fill="var(--faint)">{fyLabel(yr)}</text>)}
          <path d={mk(histPts) ?? ""} fill="none" stroke="var(--ink)" strokeWidth={2.5} />
          {CASES.map((c, i) => {
            const pts: [number, number][] = [[2025, DATA.revenue2025], ...all[c].rows.map((r) => [r.year, r.revenue] as [number, number])];
            const on = c === scenario;
            const last = pts[pts.length - 1];
            return (
              <g key={c} onClick={() => setScenario(c)} className="cursor-pointer">
                <motion.path d={mk(pts) ?? ""} fill="none" stroke={on ? "var(--accent)" : "var(--faint)"} strokeWidth={on ? 3 : 1.5} strokeDasharray={on ? undefined : "4 4"}
                  initial={reduce ? false : { pathLength: 0 }} animate={{ pathLength: seen || reduce ? 1 : 0, d: mk(pts) ?? "" }}
                  transition={{ pathLength: { duration: 1.2, delay: reduce ? 0 : 0.3 + i * 0.2, ease: EASE }, d: { duration: 0.5 } }} />
                <motion.text x={x(last[0]) + 8} fontSize={12} fill={on ? "var(--accent)" : "var(--muted)"} className="num" initial={false} animate={{ y: y(last[1]) + 4, opacity: seen || reduce ? 1 : 0 }}
                  transition={{ delay: reduce ? 0 : 1.2 + i * 0.2 }}>{c} {eurm(last[1], 0)}</motion.text>
              </g>
            );
          })}
        </svg>
      </div>
      <div className="mt-10 grid gap-px bg-line md:grid-cols-3">
        {CASES.map((c) => {
          const r = all[c];
          const on = c === scenario;
          return (
            <button key={c} onClick={() => setScenario(c)} aria-pressed={on}
              className={`grid content-start gap-3 p-6 text-left transition-colors duration-300 active:scale-[0.99] ${on ? "bg-ink text-bg" : "bg-bg hover:bg-surface"}`}>
              <div className="flex items-baseline justify-between">
                <span className="text-lg font-semibold">{c}</span>
                <span className={`num text-sm ${on ? "text-bg/70" : "text-muted"}`}>CAGR {pct(r.cagr)}</span>
              </div>
              <span className="num text-4xl font-medium">{eur(r.blend.price)}</span>
              <span className={`num text-sm ${on ? "text-bg/80" : "text-muted"}`}>{signedPct(r.blend.upside)} vs market | WACC {pct(r.wacc, 1)} | g {pct(r.g, 1)} | {mult(r.exit, 0)}</span>
              <span className={`text-sm leading-relaxed ${on ? "text-bg/80" : "text-muted"}`}>{DATA.story[c]}</span>
            </button>
          );
        })}
      </div>
    </Chapter>
  );
}

/* ------------------------------------------------------------- Verdict */
const RISKS = [
  ["Cyclicality", "Four customers are 61% of sales. One capex pause, like FY24, flattens revenue."],
  ["Export controls", "China was 29% of FY25 sales. Wider DUV or service restrictions hit the Bear case directly."],
  ["Terminal value", "76% of the Gordon EV and 87% of the Exit EV sit beyond 2030, so small changes in g or the multiple swing the result."],
  ["Working capital", "Customer down payments are volatile. A EUR 3-5bn swing changes near-term FCF materially."],
];

export function Verdict() {
  const ref = useChapterTime(TODAY);
  const v = useValuation();
  const reset = useStore((s) => s.reset);
  const [open, setOpen] = useState<string | null>(null);
  const up = v.blend.upside;
  const call = up > 0.15 ? "Undervalued" : up < -0.15 ? "Overvalued" : "Fairly valued";
  const method = [
    ["Forecast", "Five explicit years (FY26-30) driven by revenue growth, EBITDA margin, D&A, CapEx, NWC and tax assumptions per scenario. UFCF = EBIT x (1 - t) + D&A - CapEx - change in NWC."],
    ["Timing", "Valuation date 7 Oct 2026 on the 28 Jun 2026 balance sheet. FY26 counts only the H2 cash flow (FY26E less H1 actual). Mid-year discounting; terminal value discounted from end FY30."],
    ["WACC", "CAPM with a 10Y Bund risk-free rate (3.51%), a 50/50 blend of regression and relevered industry beta, and Damodaran's 4.23% ERP. Debt at Rf + 0.60%. Market-value weights; ASML is 99% equity."],
    ["Terminal value", "Gordon Growth (g 2.5%) and Exit Multiple (25x EBITDA), blended 50/50 for the headline. Each is cross-checked through the other's implied multiple or growth rate."],
    ["Bridge", "EV + cash and short-term investments - bonds and commercial paper + equity investments = equity value, divided by 384.9m diluted shares."],
  ];
  return (
    <Chapter id="verdict" innerRef={ref} className="px-4 pb-40 pt-24 md:px-8 md:pt-32">
      <div className="grid gap-14 lg:grid-cols-12">
        <div className="lg:col-span-7">
          <Reveal>
            <p className="text-sm text-muted">Verdict, {v.case} case, blended DCF</p>
            <h2 className="display mt-4 text-6xl font-semibold md:text-8xl">{call}.</h2>
            <p className="mt-6 max-w-[60ch] text-lg leading-relaxed text-muted">
              The model values ASML at <span className="num text-ink"><CountUp value={v.blend.price} format={(x) => eur(x)} /></span> per share against {eur(MKT, 2)},
              a <span className="num text-ink">{signedPct(up)}</span> gap. ASML is an exceptional business. The question is the price: today's market value needs either a terminal multiple of {mult(reverse(v).multiple)} or growth that persists well past 2030.
              The Exit method ({eur(v.exitM.price)}) is close to the market; the Gordon method ({eur(v.gordon.price)}) is not.
            </p>
          </Reveal>
          <div className="mt-10 grid gap-px bg-line sm:grid-cols-2">
            {RISKS.map(([k, t]) => (
              <div key={k} className="bg-bg p-5">
                <h3 className="font-semibold">{k}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted">{t}</p>
              </div>
            ))}
          </div>
          <div className="mt-10 flex flex-wrap gap-3">
            <a href={XLSX_HREF} download className="flex h-11 items-center gap-2 bg-accent px-5 text-sm font-medium text-accent-ink active:scale-[0.98]"><DownloadSimple size={16} weight="bold" /> Download .xlsx</a>
            <button onClick={reset} className="flex h-11 items-center gap-2 border border-ink px-5 text-sm font-medium transition-colors hover:bg-ink hover:text-bg active:scale-[0.98]"><ArrowCounterClockwise size={16} /> Reset to base</button>
          </div>
        </div>
        <div className="lg:col-span-5">
          <h3 className="mb-2 text-sm text-muted">Methodology</h3>
          <div className="border-t border-line">
            {method.map(([k, t]) => (
              <div key={k} className="border-b border-line">
                <button onClick={() => setOpen(open === k ? null : k)} aria-expanded={open === k} className="flex w-full items-center justify-between py-3 text-left text-sm">
                  {k}<CaretDown size={14} className={`text-muted transition-transform duration-300 ${open === k ? "rotate-180" : ""}`} />
                </button>
                <AnimatePresence initial={false}>
                  {open === k && (
                    <motion.p initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.3, ease: EASE }}
                      className="overflow-hidden pb-3 text-sm leading-relaxed text-muted">{t}</motion.p>
                  )}
                </AnimatePresence>
              </div>
            ))}
          </div>
          <h3 className="mb-2 mt-10 text-sm text-muted">Sources</h3>
          <ol className="grid gap-2 text-xs leading-relaxed text-muted">
            {Object.entries(DATA.sources).map(([k, s]) => (
              <li key={k}><span className="num text-faint">{k} </span><a href={s.url} target="_blank" rel="noreferrer" className="underline decoration-line underline-offset-2 hover:text-ink">{s.title}</a></li>
            ))}
          </ol>
        </div>
      </div>
      <footer className="mt-24 flex flex-wrap justify-between gap-4 border-t border-line pt-6 text-xs text-faint">
        <span>Built by {DATA.meta.analyst}. Data as of 7 October 2026.</span>
        <span>Educational project. Not investment advice.</span>
      </footer>
    </Chapter>
  );
}
