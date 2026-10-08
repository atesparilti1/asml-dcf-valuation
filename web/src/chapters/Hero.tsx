import { ArrowDown, DownloadSimple } from "@phosphor-icons/react";
import { scaleLinear } from "d3-scale";
import { motion, useReducedMotion } from "motion/react";
import { useMemo, useState } from "react";
import { XLSX_HREF } from "../components/chrome";
import { Chapter, CountUp, EASE, useChapterTime, useSize } from "../components/ui";
import { COMPS, DATA, gridPrice, reverse, value } from "../model/dcf";
import { AUTHOR, AUTHOR_LINE } from "../site";
import { eur, mult, pct, signedPct } from "../lib/format";
import { priceFor, TODAY, useStore, useValuation } from "../state/valuation";

interface Band { key: string; label: string; lo: number; hi: number; mid: number; note: string }

function FootballField() {
  const v = useValuation();
  const ov = useStore((s) => s.ov);
  const reduce = useReducedMotion();
  const [ref, w] = useSize<HTMLDivElement>();
  const [hover, setHover] = useState<string | null>(null);

  const bands: Band[] = useMemo(() => {
    const ws = [v.wacc - 0.005, v.wacc + 0.005];
    const gord = ws.flatMap((x) => [v.g - 0.0025, v.g + 0.0025].map((g) => gridPrice(v, x, { g })));
    const ex = ws.flatMap((x) => [v.exit - 2, v.exit + 2].map((m) => gridPrice(v, x, { exit: m })));
    const bear = value("Bear", ov).blend.price, base = value("Base", ov).blend.price, bull = value("Bull", ov).blend.price;
    const M = DATA.market;
    return [
      { key: "w52", label: "52-week range", lo: M.low52, hi: M.high52, mid: M.price, note: "Euronext closing prices, Oct-25 to Oct-26" },
      { key: "comps", label: "Trading comps", lo: COMPS.pLow, hi: COMPS.pHigh, mid: COMPS.pMed, note: `peer EV / LTM EBITDA ${mult(COMPS.low)}-${mult(COMPS.high)}, median ${mult(COMPS.median)}` },
      { key: "gordon", label: "DCF, Gordon Growth", lo: Math.min(...gord), hi: Math.max(...gord), mid: v.gordon.price, note: `WACC ${pct(ws[0], 1)}-${pct(ws[1], 1)}, g ${pct(v.g - 0.0025, 2)}-${pct(v.g + 0.0025, 2)}` },
      { key: "exit", label: "DCF, Exit Multiple", lo: Math.min(...ex), hi: Math.max(...ex), mid: v.exitM.price, note: `WACC ${pct(ws[0], 1)}-${pct(ws[1], 1)}, ${mult(v.exit - 2, 0)}-${mult(v.exit + 2, 0)} EBITDA` },
      { key: "blend", label: "DCF, blended", lo: (Math.min(...gord) + Math.min(...ex)) / 2, hi: (Math.max(...gord) + Math.max(...ex)) / 2, mid: v.blend.price, note: "50% Gordon, 50% Exit" },
      { key: "scen", label: "Scenarios, Bear to Bull", lo: bear, hi: bull, mid: base, note: `Bear ${eur(bear)}, Base ${eur(base)}, Bull ${eur(bull)}` },
    ];
  }, [v, ov]);

  const mkt = DATA.market.price;
  const lab = w < 560 ? 0 : 168;
  const max = Math.max(mkt, ...bands.map((b) => b.hi)) * 1.08;
  const x = scaleLinear().domain([0, max]).range([lab, w - 8]);
  const rowH = lab === 0 ? 58 : 46;
  const off = lab === 0 ? 22 : 8;
  const h = bands.length * rowH + off + 26;
  const ticks = x.ticks(w < 560 ? 4 : 6);

  return (
    <div ref={ref} className="relative">
      <svg width={w} height={h} role="img" aria-label="Football field of implied share price ranges against the current share price">
        {ticks.map((t) => (
          <g key={t}>
            <line x1={x(t)} x2={x(t)} y1={0} y2={h - 22} stroke="var(--line)" />
            <text x={x(t)} y={h - 6} textAnchor="middle" className="num" fontSize={11} fill="var(--faint)">€{t.toLocaleString("en-GB")}</text>
          </g>
        ))}
        {bands.map((b, i) => {
          const y = i * rowH + off;
          const active = hover === b.key;
          return (
            <g key={b.key} onMouseEnter={() => setHover(b.key)} onMouseLeave={() => setHover(null)}>
              {lab > 0 && <text x={0} y={y + 19} fontSize={13} fill="var(--ink)">{b.label}</text>}
              {lab === 0 && <text x={x(0)} y={y + 2} fontSize={11} fill="var(--muted)">{b.label}</text>}
              <motion.rect y={y + 6} height={20} fill={b.key === "blend" ? "var(--accent)" : b.key === "w52" || b.key === "comps" ? "var(--faint)" : "var(--ink)"} opacity={active ? 1 : b.key === "blend" ? 0.9 : 0.78}
                initial={reduce ? false : { x: x(b.lo), width: 0 }} animate={{ x: x(b.lo), width: Math.max(2, x(b.hi) - x(b.lo)) }}
                transition={{ duration: 0.9, delay: reduce ? 0 : 0.35 + i * 0.12, ease: EASE }} />
              <motion.line y1={y + 2} y2={y + 30} stroke="var(--bg)" strokeWidth={2} animate={{ x1: x(b.mid), x2: x(b.mid) }} transition={{ duration: 0.6, ease: EASE }} />
              <rect x={lab} y={y} width={w - lab} height={rowH - 6} fill="transparent" />
            </g>
          );
        })}
        <motion.g initial={reduce ? false : { opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 1.1, duration: 0.6, ease: EASE }}>
          <line x1={x(mkt)} x2={x(mkt)} y1={0} y2={h - 22} stroke="var(--accent)" strokeWidth={1.5} strokeDasharray="4 3" />
          <text x={x(mkt) + 6} y={10} fontSize={11} fill="var(--accent)" className="num">Market {eur(mkt)}</text>
        </motion.g>
      </svg>
      <div className="mt-2 h-5 text-xs text-muted">
        {hover ? (() => { const b = bands.find((z) => z.key === hover)!; return <span className="num">{b.label}: {eur(b.lo)} to {eur(b.hi)} ({b.note})</span>; })() : "Hover a bar for its assumptions. White tick = point estimate."}
      </div>
    </div>
  );
}

export function Hero() {
  const ref = useChapterTime(TODAY);
  const v = useValuation();
  const method = useStore((s) => s.method);
  const price = priceFor(v, method);
  const reduce = useReducedMotion();
  const up = price / DATA.market.price - 1;
  return (
    <Chapter id="top" innerRef={ref} className="border-t-0">
      <div className="grid min-h-[86dvh] content-center gap-12 px-4 pb-12 pt-24 md:px-8 lg:pt-28">
        <div className="grid items-end gap-10 lg:grid-cols-12">
          <motion.div className="lg:col-span-7" initial={reduce ? false : { opacity: 0, y: 28 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.9, ease: EASE }}>
            <p className="mb-6 text-[11px] uppercase tracking-[0.18em] text-muted">ASML Holding N.V. | Equity valuation by {AUTHOR}</p>
            <h1 className="display max-w-[14ch] text-5xl font-semibold md:text-6xl lg:text-7xl">What is the EUV monopoly worth?</h1>
            <p className="mt-6 max-w-[46ch] text-lg leading-relaxed text-muted">
              A ten-year DCF built from reported filings and checked against peers. Change any assumption and watch the price respond.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <a href="#origins" className="flex h-11 items-center gap-2 bg-accent px-5 text-sm font-medium text-accent-ink transition-transform active:scale-[0.98]">
                Explore the model <ArrowDown size={16} weight="bold" />
              </a>
              <a href={XLSX_HREF} download className="flex h-11 items-center gap-2 border border-ink px-5 text-sm font-medium transition-colors hover:bg-ink hover:text-bg active:scale-[0.98]">
                <DownloadSimple size={16} weight="bold" /> Download .xlsx
              </a>
            </div>
          </motion.div>
          <motion.div className="lg:col-span-5 lg:text-right" initial={reduce ? false : { opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 1, delay: 0.2 }}>
            <p className="text-sm text-muted">Implied value per share ({method === "blend" ? "blended" : method === "gordon" ? "Gordon Growth" : "Exit Multiple"})</p>
            <CountUp value={price} format={(z) => eur(z)} className="num display block text-[19vw] font-medium sm:text-8xl lg:text-[6.5rem] xl:text-[7.5rem]" />
            <p className="num mt-3 text-lg">
              <span className={up >= 0 ? "text-accent" : ""}>{signedPct(up)}</span>
              <span className="text-muted"> vs {eur(DATA.market.price, 2)} close on 7 Oct 2026</span>
            </p>
          </motion.div>
        </div>
      </div>
    </Chapter>
  );
}

/** Executive summary: the three things to know, then the football field. */
export function Summary() {
  const ref = useChapterTime(TODAY);
  const v = useValuation();
  const rev = reverse(v);
  const findings = [
    { fig: eur(v.blend.price), text: `Blended ten-year DCF (Gordon ${eur(v.gordon.price)}, exit multiple ${eur(v.exitM.price)}): ${signedPct(v.blend.upside, 0)} versus the ${eur(DATA.market.price)} share price.` },
    { fig: mult(rev.multiple, 0), text: `The FY35 EBITDA multiple today's price requires. ASML has averaged ${mult(DATA.comps.histAvgEvEbitda, 0)} in a high-growth decade; the base case uses ${mult(v.exit, 0)}.` },
    { fig: `${eur(COMPS.pLow)}-${eur(COMPS.pHigh).slice(1)}`, text: `Peers at ${mult(COMPS.low, 0)}-${mult(COMPS.high, 0)} trailing EBITDA put ASML near its price. The whole sector, not ASML alone, is priced for the AI cycle.` },
  ];
  return (
    <Chapter id="summary" innerRef={ref} className="px-4 py-20 md:px-8 md:py-24">
      <div className="grid gap-10 lg:grid-cols-12">
        <div className="lg:col-span-4">
          <h2 className="display text-4xl font-semibold md:text-5xl">The short version.</h2>
          <p className="mt-4 max-w-[34ch] text-[15px] leading-relaxed text-muted">{AUTHOR}, {AUTHOR_LINE}. Model and data as of 7 October 2026.</p>
        </div>
        <dl className="divide-y divide-line border-y border-line lg:col-span-8">
          {findings.map((f) => (
            <div key={f.fig} className="grid gap-2 py-5 sm:grid-cols-[minmax(0,250px)_1fr] sm:gap-8">
              <dt className="num display whitespace-nowrap text-4xl font-medium">{f.fig}</dt>
              <dd className="max-w-[56ch] self-center text-[15px] leading-relaxed text-muted">{f.text}</dd>
            </div>
          ))}
        </dl>
      </div>
      <div className="mt-14">
        <h3 className="mb-4 text-sm text-muted">Valuation range, EUR per share</h3>
        <FootballField />
      </div>
    </Chapter>
  );
}
