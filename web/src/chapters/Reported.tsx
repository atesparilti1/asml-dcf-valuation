import { scaleBand, scaleLinear } from "d3-scale";
import { line } from "d3-shape";
import { AnimatePresence, motion, useMotionValueEvent, useReducedMotion, useScroll } from "motion/react";
import { useRef, useState } from "react";
import { Chapter, CountUp, EASE, Segmented, useSize } from "../components/ui";
import { DATA, HIST } from "../model/dcf";
import { eurm, pct, signedPct } from "../lib/format";
import { useStore } from "../state/valuation";

type Metric = "revenue" | "ufcf" | "margins";

const NOTES: Record<number, string> = {
  2021: `Revenue +${Math.round(HIST[0].growth * 100)}% as EUV demand accelerates. ASML still returns EUR 8.6bn through buybacks.`,
  2022: "Demand outruns output. Gross margin dips to 50.5% as costs rise faster than prices.",
  2023: "Revenue +30% to EUR 27.6bn, but customer down payments are consumed: a EUR 3.1bn working-capital outflow halves FCF.",
  2024: "Digestion year: +2.6% growth. China becomes the largest region at EUR 10.2bn of sales.",
  2025: "Record EUR 32.7bn of sales, a 37.7% EBITDA margin and a EUR 38.8bn backlog: the base year of the forecast.",
};

function Chart({ active, metric }: { active: number; metric: Metric }) {
  const [ref, w] = useSize<HTMLDivElement>();
  const reduce = useReducedMotion();
  const h = Math.min(420, Math.max(260, w * 0.5));
  const m = { t: 28, r: 8, b: 28, l: 8 };
  const x = scaleBand<number>().domain(HIST.map((d) => d.year)).range([m.l, w - m.r]).padding(0.28);
  const key = metric === "ufcf" ? "ufcf" : "revenue";
  const yb = scaleLinear().domain([0, 34000]).range([h - m.b, m.t]);
  const ym = scaleLinear().domain([0.25, 0.6]).range([h - m.b, m.t]);
  const series: { k: "gm" | "ebitda_m" | "ebit_m"; label: string; dash?: string }[] = [
    { k: "gm", label: "Gross" }, { k: "ebitda_m", label: "EBITDA", dash: "5 4" }, { k: "ebit_m", label: "EBIT", dash: "1 4" },
  ];
  const mk = (k: "gm" | "ebitda_m" | "ebit_m") =>
    line<(typeof HIST)[number]>().x((d) => x(d.year)! + x.bandwidth() / 2).y((d) => ym(d[k] as number))(HIST.slice(0, active + 1)) ?? "";
  return (
    <div ref={ref}>
      <svg width={w} height={h} role="img" aria-label={`ASML ${metric} FY2021 to FY2025`}>
        {HIST.map((d, i) => {
          const val = d[key] as number;
          const on = i <= active;
          return (
            <g key={d.year}>
              <text x={x(d.year)! + x.bandwidth() / 2} y={h - 8} textAnchor="middle" fontSize={12} className="num" fill={i === active ? "var(--ink)" : "var(--faint)"}>FY{String(d.year).slice(2)}A</text>
              {metric !== "margins" && (
                <>
                  <rect x={x(d.year)} width={x.bandwidth()} y={yb(val)} height={yb(0) - yb(val)} fill="none" stroke="var(--line)" strokeDasharray="3 3" />
                  <motion.rect x={x(d.year)} width={x.bandwidth()} fill={i === active ? "var(--accent)" : "var(--ink)"}
                    initial={false} animate={{ y: on ? yb(val) : yb(0), height: on ? yb(0) - yb(val) : 0 }} transition={{ duration: reduce ? 0 : 0.7, ease: EASE }} />
                  <motion.text x={x(d.year)! + x.bandwidth() / 2} textAnchor="middle" fontSize={12} className="num" fill="var(--ink)"
                    initial={false} animate={{ opacity: on ? 1 : 0, y: yb(val) - 8 }} transition={{ duration: 0.5 }}>{eurm(val)}</motion.text>
                </>
              )}
            </g>
          );
        })}
        {metric === "margins" && (
          <>
            {[0.3, 0.4, 0.5].map((t) => (
              <g key={t}><line x1={m.l} x2={w - m.r} y1={ym(t)} y2={ym(t)} stroke="var(--line)" /><text x={m.l} y={ym(t) - 4} fontSize={11} fill="var(--faint)" className="num">{pct(t, 0)}</text></g>
            ))}
            {series.map((s) => (
              <g key={s.k}>
                <motion.path d={mk(s.k)} fill="none" stroke={s.k === "ebitda_m" ? "var(--accent)" : "var(--ink)"} strokeWidth={2} strokeDasharray={s.dash} initial={false} animate={{ d: mk(s.k) }} transition={{ duration: 0.5 }} />
                {HIST.slice(0, active + 1).map((d) => (
                  <circle key={d.year} cx={x(d.year)! + x.bandwidth() / 2} cy={ym(d[s.k] as number)} r={3} fill={s.k === "ebitda_m" ? "var(--accent)" : "var(--ink)"} />
                ))}
                <text x={w - m.r} y={ym(HIST[active][s.k] as number) - 8} textAnchor="end" fontSize={12} className="num" fill="var(--muted)">{s.label} {pct(HIST[active][s.k] as number)}</text>
              </g>
            ))}
          </>
        )}
      </svg>
    </div>
  );
}

export function Reported() {
  const wrap = useRef<HTMLElement>(null);
  const reduce = useReducedMotion();
  const [active, setActive] = useState(reduce ? 4 : 0);
  const [metric, setMetric] = useState<Metric>("revenue");
  const setTime = useStore((s) => s.setTime);
  const { scrollYProgress } = useScroll({ target: wrap, offset: ["start start", "end end"] });
  useMotionValueEvent(scrollYProgress, "change", (p) => {
    if (reduce) return;
    const i = Math.min(4, Math.max(0, Math.floor(p * 5)));
    if (i !== active) setActive(i);
    if (p > 0 && p < 1) setTime(2021 + Math.min(1, p) * 5);
  });
  const d = HIST[active];
  const src = DATA.sources.S2;
  return (
    <Chapter id="reported" innerRef={wrap}>
      <div style={{ height: reduce ? "auto" : "320vh" }}>
        <div className={`${reduce ? "" : "sticky top-0 min-h-[100dvh]"} grid content-center gap-10 px-4 pb-20 pt-24 md:px-8`}>
          <div className="flex flex-wrap items-end justify-between gap-4">
            <h2 className="display text-4xl font-semibold md:text-5xl">Five reported years.</h2>
            <Segmented label="Metric" value={metric} onChange={setMetric}
              options={[{ value: "revenue", label: "Revenue" }, { value: "ufcf", label: "Free cash flow" }, { value: "margins", label: "Margins" }]} />
          </div>
          <div className="grid gap-10 lg:grid-cols-12">
            <div className="grid content-start gap-6 lg:col-span-4">
              <CountUp value={d.year} format={(z) => `FY${String(Math.round(z)).slice(2)}`} className="num display text-[88px] font-medium lg:text-[120px]" />
              <dl className="grid grid-cols-2 gap-x-6 gap-y-4">
                {[
                  ["Revenue", <CountUp key="r" value={d.revenue} format={(z) => eurm(z)} />],
                  ["Growth", <CountUp key="g" value={d.growth} format={(z) => signedPct(z)} />],
                  ["EBITDA margin", <CountUp key="m" value={d.ebitda_m} format={(z) => pct(z)} />],
                  ["Unlevered FCF", <CountUp key="u" value={d.ufcf} format={(z) => eurm(z)} />],
                ].map(([k, v]) => (
                  <div key={k as string} className="border-t border-line pt-2">
                    <dt className="text-xs text-muted">{k}</dt>
                    <dd className="num text-xl">{v}</dd>
                  </div>
                ))}
              </dl>
              <AnimatePresence mode="wait">
                <motion.p key={d.year} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} transition={{ duration: 0.35, ease: EASE }}
                  className="max-w-[44ch] text-[15px] leading-relaxed text-muted">{NOTES[d.year]}</motion.p>
              </AnimatePresence>
            </div>
            <div className="lg:col-span-8">
              <Chart active={active} metric={metric} />
              <p className="mt-3 text-xs text-faint">
                Reported US GAAP, EUR m. UFCF = NOPAT + D&A - CapEx - change in NWC. Net cash {eurm(DATA.histRaw.cash["2025"] + DATA.histRaw.sti["2025"] - DATA.histRaw.debt_current["2025"] - DATA.histRaw.debt_noncurrent["2025"])} at FY25.{" "}
                <a className="underline decoration-line underline-offset-2 hover:text-ink" href={src.url} target="_blank" rel="noreferrer">Source: SEC XBRL</a>
              </p>
            </div>
          </div>
        </div>
      </div>
    </Chapter>
  );
}
