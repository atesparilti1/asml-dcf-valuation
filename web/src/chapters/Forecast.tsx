import { CaretDown } from "@phosphor-icons/react";
import { scaleBand, scaleLinear } from "d3-scale";
import { line } from "d3-shape";
import { AnimatePresence, motion, useInView, useMotionValueEvent, useReducedMotion, useScroll } from "motion/react";
import { useRef, useState } from "react";
import { Chapter, EASE, Reveal, Slider, useSize } from "../components/ui";
import { DATA, HIST, type Valuation } from "../model/dcf";
import { eurm, fyLabel, pct } from "../lib/format";
import { TODAY, useBaseline, useStore, useValuation } from "../state/valuation";

/** Ten years on one axis: reported bars in ink, forecast bars hatched in accent, ghost = untouched base. */
function TimelineChart({ v, base }: { v: Valuation; base: Valuation }) {
  const [ref, w] = useSize<HTMLDivElement>();
  const reduce = useReducedMotion();
  const seen = useInView(ref, { once: true, amount: 0.3 }) || !!reduce;
  const h = Math.min(400, Math.max(260, w * 0.46));
  const m = { t: 30, r: 8, b: 30, l: 8 };
  const data = [
    ...HIST.map((d) => ({ year: d.year, rev: d.revenue, em: d.ebitda_m, f: false })),
    ...v.rows.map((r) => ({ year: r.year, rev: r.revenue, em: r.ebitdaM, f: true })),
  ];
  const x = scaleBand<number>().domain(data.map((d) => d.year)).range([m.l, w - m.r]).padding(0.25);
  const maxRev = Math.max(90000, ...data.map((d) => d.rev)) * 1.05;
  const y = scaleLinear().domain([0, maxRev]).range([h - m.b, m.t]);
  const ym = scaleLinear().domain([0.2, 0.55]).range([h - m.b, m.t]);
  const cx = (yr: number) => x(yr)! + x.bandwidth() / 2;
  const path = line<(typeof data)[number]>().x((d) => cx(d.year)).y((d) => ym(d.em))(data) ?? "";
  const todayX = (x(2025)! + x.bandwidth() + x(2026)!) / 2;
  return (
    <div ref={ref}>
      <svg width={w} height={h} role="img" aria-label="Revenue and EBITDA margin, FY21A to FY30E">
        <defs>
          <pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
            <rect width="6" height="6" fill="var(--accent-soft)" />
            <line x1="0" y1="0" x2="0" y2="6" stroke="var(--hatch)" strokeWidth="2" />
          </pattern>
        </defs>
        <line x1={todayX} x2={todayX} y1={m.t - 18} y2={h - m.b} stroke="var(--accent)" strokeDasharray="3 3" />
        <text x={todayX + 6} y={m.t - 8} fontSize={11} fill="var(--accent)">Today</text>
        <text x={todayX - 6} y={m.t - 8} fontSize={11} fill="var(--faint)" textAnchor="end">Reported</text>
        {data.map((d, i) => {
          const b = d.f ? base.rows[i - 5].revenue : d.rev;
          return (
            <g key={d.year}>
              {d.f && <rect x={x(d.year)} width={x.bandwidth()} y={y(b)} height={y(0) - y(b)} fill="none" stroke="var(--faint)" strokeDasharray="2 3" />}
              <motion.rect x={x(d.year)} width={x.bandwidth()} fill={d.f ? "url(#hatch)" : "var(--ink)"} stroke={d.f ? "var(--accent)" : "none"}
                initial={reduce ? false : { y: y(0), height: 0 }} animate={seen ? { y: y(d.rev), height: y(0) - y(d.rev) } : { y: y(0), height: 0 }}
                transition={{ duration: 0.7, delay: reduce ? 0 : seen ? Math.max(0, i * 0.06) : 0, ease: EASE }} />
              <text x={cx(d.year)} y={h - 10} textAnchor="middle" fontSize={11} className="num" fill={d.f ? "var(--accent)" : "var(--faint)"}>{fyLabel(d.year)}</text>
              {(d.year === 2025 || d.year === 2030) && (
                <motion.text x={cx(d.year)} textAnchor="middle" fontSize={12} className="num" fill={d.f ? "var(--accent)" : "var(--bg)"} animate={{ y: y(0) - 10 }} transition={{ duration: 0.5 }}>{eurm(d.rev)}</motion.text>
              )}
            </g>
          );
        })}
        <motion.path d={path} animate={{ d: path }} transition={{ duration: 0.5 }} fill="none" stroke="var(--accent)" strokeWidth={2} />
        {data.map((d) => <motion.circle key={d.year} cx={cx(d.year)} r={3} fill={d.f ? "var(--bg)" : "var(--accent)"} stroke="var(--accent)" strokeWidth={1.5} animate={{ cy: ym(d.em) }} transition={{ duration: 0.5 }} />)}
        <text x={cx(2021) - x.bandwidth() / 2} y={ym(data[0].em) - 12} fontSize={12} fill="var(--accent)" className="num">EBITDA margin {pct(data[0].em)}</text>
        <text x={cx(2030) + x.bandwidth() / 2} y={ym(data[9].em) - 12} textAnchor="end" fontSize={12} fill="var(--accent)" className="num">{pct(data[9].em)}</text>
      </svg>
      <p className="mt-2 text-xs text-faint">Bars: revenue (EUR m). Dotted outline: unadjusted {base.case} case. Line: EBITDA margin.</p>
    </div>
  );
}

/** UFCF built per forecast year: NOPAT + D&A - CapEx - change in NWC. */
function UfcfBuild({ v }: { v: Valuation }) {
  const max = Math.max(...v.rows.map((r) => r.nopat + r.da + Math.max(0, -r.dnwc)));
  const s = (x: number) => `${(Math.abs(x) / max) * 100}%`;
  return (
    <div className="grid grid-cols-5 gap-3">
      {v.rows.map((r) => (
        <div key={r.year} className="grid gap-1.5">
          <p className="num text-xs text-accent">{fyLabel(r.year)}</p>
          {[
            ["NOPAT", r.nopat, "var(--ink)"], ["+ D&A", r.da, "var(--muted)"], ["- CapEx", -r.capex, "var(--faint)"], ["- ΔNWC", -r.dnwc, "var(--faint)"],
          ].map(([k, val, c]) => (
            <div key={k as string} title={`${k} ${eurm(val as number)}`}>
              <motion.div className="h-2 origin-left" style={{ background: c as string, opacity: (val as number) < 0 ? 0.6 : 1 }} animate={{ width: s(val as number) }} transition={{ duration: 0.5, ease: EASE }} />
            </div>
          ))}
          <div className="border-t border-line pt-1">
            <motion.div className="h-3 origin-left bg-accent" animate={{ width: s(r.ufcf) }} transition={{ duration: 0.5, ease: EASE }} />
            <p className="num mt-1 text-sm">{eurm(r.ufcf)}</p>
          </div>
        </div>
      ))}
    </div>
  );
}

const WHY: { k: keyof typeof DATA.driverWhy; label: string }[] = [
  { k: "growth", label: "Revenue growth" }, { k: "gm", label: "Gross margin" }, { k: "ebitda_m", label: "EBITDA margin" },
  { k: "capex_pct", label: "CapEx" }, { k: "nwc_pct", label: "Working capital" }, { k: "tax", label: "Tax rate" }, { k: "da_pct", label: "D&A" },
];

function Why() {
  const [open, setOpen] = useState<string | null>("growth");
  return (
    <div className="border-t border-line">
      {WHY.map((w) => (
        <div key={w.k} className="border-b border-line">
          <button onClick={() => setOpen(open === w.k ? null : w.k)} aria-expanded={open === w.k} className="flex w-full items-center justify-between py-3 text-left text-sm">
            {w.label}<CaretDown size={14} className={`text-muted transition-transform duration-300 ${open === w.k ? "rotate-180" : ""}`} />
          </button>
          <AnimatePresence initial={false}>
            {open === w.k && (
              <motion.p initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.3, ease: EASE }}
                className="overflow-hidden pb-3 text-sm leading-relaxed text-muted">{DATA.driverWhy[w.k]}</motion.p>
            )}
          </AnimatePresence>
        </div>
      ))}
    </div>
  );
}

export function Forecast() {
  const wrap = useRef<HTMLElement>(null);
  const v = useValuation();
  const base = useBaseline();
  const { ov, setOv, setTime } = useStore();
  const { scrollYProgress } = useScroll({ target: wrap, offset: ["start 60%", "end end"] });
  useMotionValueEvent(scrollYProgress, "change", (p) => {
    if (p > 0 && p < 1) setTime(TODAY + p * (2030.5 - TODAY));
  });
  return (
    <Chapter id="forecast" innerRef={wrap} className="px-4 py-24 md:px-8 md:py-32">
      <Reveal>
        <h2 className="display max-w-[16ch] text-4xl font-semibold md:text-5xl">Crossing into the forecast.</h2>
        <p className="mt-5 max-w-[58ch] text-lg leading-relaxed text-muted">
          FY26 starts from company guidance of EUR 43-45bn. Growth then fades toward the cycle average. The future is the only part you can change.
        </p>
      </Reveal>
      <div className="mt-12 grid gap-12 lg:grid-cols-12">
        <div className="lg:col-span-8"><TimelineChart v={v} base={base} /></div>
        <div className="grid content-start gap-6 lg:col-span-4">
          <p className="text-sm font-medium">Bend the future</p>
          <Slider label="Revenue growth vs case, every year" value={ov.growthShift ?? 0} min={-0.1} max={0.1} step={0.005}
            format={(x) => `${x >= 0 ? "+" : "-"}${pct(Math.abs(x))}`} onChange={(growthShift) => setOv({ growthShift })} />
          <Slider label="EBITDA margin vs case, every year" value={ov.marginShift ?? 0} min={-0.08} max={0.06} step={0.0025}
            format={(x) => `${x >= 0 ? "+" : "-"}${pct(Math.abs(x))}`} onChange={(marginShift) => setOv({ marginShift })} />
          <dl className="grid grid-cols-2 gap-4 border-t border-line pt-4 text-sm">
            <div><dt className="text-xs text-faint">FY30E revenue</dt><dd className="num text-lg">{eurm(v.rows[4].revenue)}</dd></div>
            <div><dt className="text-xs text-faint">vs 2030 target range</dt><dd className="num text-lg">{v.rows[4].revenue > DATA.guidance2030.rev_high ? "Above" : v.rows[4].revenue < DATA.guidance2030.rev_low ? "Below" : "Within"} €44-60bn</dd></div>
            <div><dt className="text-xs text-faint">5-yr CAGR</dt><dd className="num text-lg">{pct(v.cagr)}</dd></div>
            <div><dt className="text-xs text-faint">FY30E EBITDA margin</dt><dd className="num text-lg">{pct(v.rows[4].ebitdaM)}</dd></div>
          </dl>
        </div>
      </div>
      <div className="mt-16 grid gap-12 lg:grid-cols-12">
        <div className="lg:col-span-8">
          <h3 className="mb-6 text-sm text-muted">From profit to free cash flow, per forecast year</h3>
          <UfcfBuild v={v} />
          <p className="mt-4 text-xs text-faint">FY26 includes a working-capital outflow as customer down payments normalise from -27% of sales (FY25) toward -12%.</p>
        </div>
        <div className="lg:col-span-4">
          <h3 className="mb-2 text-sm text-muted">Why these assumptions</h3>
          <Why />
        </div>
      </div>
    </Chapter>
  );
}
