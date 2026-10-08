import { CaretDown } from "@phosphor-icons/react";
import { scaleBand, scaleLinear } from "d3-scale";
import { line } from "d3-shape";
import { AnimatePresence, motion, useInView, useMotionValueEvent, useReducedMotion, useScroll } from "motion/react";
import { useRef, useState } from "react";
import { Chapter, EASE, Reveal, Slider, useSize } from "../components/ui";
import { DATA, HIST, type Valuation } from "../model/dcf";
import { eurm, fyLabel, num, pct } from "../lib/format";
import { TODAY, useBaseline, useStore, useValuation } from "../state/valuation";

const SEG = [
  { k: "ib", label: "Installed base", fill: "var(--muted)" },
  { k: "other", label: "Other DUV, metrology", fill: "var(--faint)" },
  { k: "arfi", label: "DUV immersion", fill: "var(--ink)" },
  { k: "euv", label: "EUV (low-NA + High-NA)", fill: "var(--accent)" },
] as const;

/** Fifteen years on one axis: reported (ink), forecast built by segment, fade (hatched). Ghost = untouched case. */
function TimelineChart({ v, base }: { v: Valuation; base: Valuation }) {
  const [ref, w] = useSize<HTMLDivElement>();
  const reduce = useReducedMotion();
  const seen = useInView(ref, { once: true, amount: 0.3 }) || !!reduce;
  const h = Math.min(420, Math.max(280, w * 0.5));
  const m = { t: 34, r: 8, b: 30, l: 8 };
  const years = [...HIST.map((d) => d.year), ...v.rows.map((r) => r.year)];
  const x = scaleBand<number>().domain(years).range([m.l, w - m.r]).padding(0.22);
  const maxRev = Math.max(95000, ...v.rows.map((r) => r.revenue)) * 1.05;
  const y = scaleLinear().domain([0, maxRev]).range([h - m.b, m.t]);
  const ym = scaleLinear().domain([0.2, 0.55]).range([h - m.b, m.t]);
  const cx = (yr: number) => x(yr)! + x.bandwidth() / 2;
  const marg = [...HIST.map((d) => ({ year: d.year, em: d.ebitda_m })), ...v.rows.map((r) => ({ year: r.year, em: r.ebitdaM }))];
  const path = line<(typeof marg)[number]>().x((d) => cx(d.year)).y((d) => ym(d.em))(marg) ?? "";
  const div = (a: number, b: number) => (x(a)! + x.bandwidth() + x(b)!) / 2;
  const small = w < 640;
  const t = (i: number) => ({ duration: 0.7, delay: reduce ? 0 : seen ? i * 0.04 : 0, ease: EASE });
  return (
    <div ref={ref}>
      <svg width={w} height={h} role="img" aria-label="Revenue by segment and EBITDA margin, FY21A to FY35E">
        <defs>
          <pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
            <rect width="6" height="6" fill="var(--accent-soft)" />
            <line x1="0" y1="0" x2="0" y2="6" stroke="var(--hatch)" strokeWidth="2" />
          </pattern>
        </defs>
        {[[2025, 2026, "Today", "var(--accent)"], [2030, 2031, "Fade", "var(--faint)"]].map(([a, b, l, c]) => (
          <g key={l as string}>
            <line x1={div(a as number, b as number)} x2={div(a as number, b as number)} y1={m.t - 22} y2={h - m.b} stroke={c as string} strokeDasharray="3 3" />
            <text x={div(a as number, b as number) + 5} y={m.t - 12} fontSize={11} fill={c as string}>{l}</text>
          </g>
        ))}
        {HIST.map((d, i) => (
          <motion.rect key={d.year} x={x(d.year)} width={x.bandwidth()} fill="var(--ink)" opacity={0.85}
            initial={reduce ? false : { y: y(0), height: 0 }} animate={seen ? { y: y(d.revenue), height: y(0) - y(d.revenue) } : { y: y(0), height: 0 }} transition={t(i)} />
        ))}
        {v.segments.map((s, i) => {
          const yr = 2026 + i;
          const parts = { ib: s.ib, other: s.odv + s.mi, arfi: s.arfi, euv: s.nxe + s.exe };
          let acc = 0;
          return (
            <g key={yr}>
              <rect x={x(yr)} width={x.bandwidth()} y={y(base.rows[i].revenue)} height={y(0) - y(base.rows[i].revenue)} fill="none" stroke="var(--faint)" strokeDasharray="2 3" />
              {SEG.map((sg) => {
                const v0 = acc;
                acc += parts[sg.k];
                return (
                  <motion.rect key={sg.k} x={x(yr)} width={x.bandwidth()} fill={sg.fill}
                    initial={reduce ? false : { y: y(0), height: 0 }} animate={seen ? { y: y(acc), height: y(v0) - y(acc) } : { y: y(0), height: 0 }} transition={t(5 + i)} />
                );
              })}
            </g>
          );
        })}
        {v.rows.slice(5).map((r, i) => (
          <motion.rect key={r.year} x={x(r.year)} width={x.bandwidth()} fill="url(#hatch)" stroke="var(--accent)" strokeOpacity={0.5}
            initial={reduce ? false : { y: y(0), height: 0 }} animate={seen ? { y: y(r.revenue), height: y(0) - y(r.revenue) } : { y: y(0), height: 0 }} transition={t(10 + i)} />
        ))}
        {years.map((yr, i) => (!small || i % 2 === 0) && (
          <text key={yr} x={cx(yr)} y={h - 10} textAnchor="middle" fontSize={11} className="num" fill={yr > 2025 ? "var(--accent)" : "var(--faint)"}>{fyLabel(yr)}</text>
        ))}
        {[2025, 2030, 2035].map((yr) => {
          const val = yr === 2025 ? DATA.revenue2025 : v.rows.find((r) => r.year === yr)!.revenue;
          return <motion.text key={yr} x={cx(yr)} textAnchor="middle" fontSize={12} className="num" fill="var(--ink)" animate={{ y: y(val) - 8 }} transition={{ duration: 0.5 }}>{eurm(val, 0)}</motion.text>;
        })}
        <motion.path d={path} animate={{ d: path }} transition={{ duration: 0.5 }} fill="none" stroke="var(--accent)" strokeWidth={1.5} strokeDasharray="5 3" />
        <text x={cx(2021) - x.bandwidth() / 2} y={ym(marg[0].em) - 10} fontSize={11} fill="var(--accent)" className="num">EBITDA margin {pct(marg[0].em)}</text>
      </svg>
      <div className="mt-2 flex flex-wrap gap-x-5 gap-y-1 text-xs text-muted">
        {[...SEG].reverse().map((s) => (
          <span key={s.k} className="flex items-center gap-1.5"><span className="inline-block size-2.5" style={{ background: s.fill }} />{s.label}</span>
        ))}
        <span className="flex items-center gap-1.5"><span className="inline-block size-2.5 border border-accent" style={{ background: "var(--accent-soft)" }} />Fade FY31-35</span>
        <span>Dotted outline: unadjusted {base.case} case. Dashed line: EBITDA margin.</span>
      </div>
    </div>
  );
}

/** Units against ASML's stated capacity: the anchor of the revenue build. */
function Units({ v }: { v: Valuation }) {
  const cap = (base: number, i: number) => (i < 3 ? base * 1.3 ** i : null);
  const rows = [
    { l: "Low-NA EUV systems", u: v.segments.map((s) => s.nxeU), cap: 65 },
    { l: "High-NA EUV systems", u: v.segments.map((s) => s.exeU), cap: 0 },
    { l: "DUV immersion systems", u: v.segments.map((s) => s.arfiU), cap: 130 },
  ];
  return (
    <div className="overflow-x-auto">
      <table className="num w-full min-w-[460px] text-sm">
        <thead>
          <tr className="text-xs text-faint">
            <th className="py-2 text-left font-normal">Units shipped</th>
            <th className="py-2 text-right font-normal">FY25A</th>
            {v.segments.map((_, i) => <th key={i} className="py-2 text-right font-normal text-accent">{fyLabel(2026 + i)}</th>)}
          </tr>
        </thead>
        <tbody className="divide-y divide-line border-t border-line">
          {rows.map((r, ri) => (
            <tr key={r.l}>
              <td className="py-2 text-muted">{r.l}</td>
              <td className="py-2 text-right">{[DATA.revBase.nxe_u, DATA.revBase.exe_u, DATA.revBase.arfi_u][ri]}</td>
              {r.u.map((u, i) => {
                const c = r.cap ? cap(r.cap, i) : null;
                const over = c !== null && u > c + 1e-9;
                return (
                  <td key={i} className={`py-2 text-right ${over ? "text-accent underline decoration-2" : ""}`} title={c ? `Stated capacity ~${num(c)}` : undefined}>
                    {num(u)}{c !== null && <span className="text-faint"> /{num(c)}</span>}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
      <p className="mt-2 text-xs text-faint">"/ n" = capacity ASML has stated: ~65 low-NA EUV and ~130 DUV immersion in 2026, +30% planned for 2027, +30% studied for 2028 (Q2-26 release). Underlined = above stated capacity.</p>
    </div>
  );
}

/** UFCF built per explicit forecast year: NOPAT + D&A - CapEx - change in NWC. */
function UfcfBuild({ v }: { v: Valuation }) {
  const rows = v.rows.slice(0, 5);
  const max = Math.max(...rows.map((r) => r.nopat + r.da + Math.max(0, -r.dnwc)));
  const s = (x: number) => `${(Math.abs(x) / max) * 100}%`;
  return (
    <div className="grid grid-cols-5 gap-3">
      {rows.map((r) => (
        <div key={r.year} className="grid gap-1.5">
          <p className="num text-xs text-accent">{fyLabel(r.year)}</p>
          {[["NOPAT", r.nopat, "var(--ink)"], ["+ D&A", r.da, "var(--muted)"], ["- CapEx", -r.capex, "var(--faint)"], ["- ΔNWC", -r.dnwc, "var(--faint)"]].map(([k, val, c]) => (
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

const WHY: { k: string; label: string }[] = [
  { k: "rev", label: "Revenue build (units x price)" }, { k: "fade", label: "Fade period FY31-35" }, { k: "gm", label: "Gross margin" },
  { k: "ebitda_m", label: "EBITDA margin" }, { k: "capex_pct", label: "CapEx" }, { k: "nwc_pct", label: "Working capital" }, { k: "tax", label: "Tax rate" },
];
const whyText = (k: string) =>
  k === "rev" ? DATA.revWhy
    : k === "fade" ? "A five-year jump from ~6% growth straight to a 2.5% perpetuity understates a compounder. Growth instead steps down linearly to the terminal rate over FY31-35, with margins, capex and working capital held at FY30 levels."
      : DATA.driverWhy[k as keyof typeof DATA.driverWhy];

function Why() {
  const [open, setOpen] = useState<string | null>("rev");
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
                className="overflow-hidden pb-3 text-sm leading-relaxed text-muted">{whyText(w.k)}</motion.p>
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
    if (p > 0 && p < 1) setTime(TODAY + p * (2035.5 - TODAY));
  });
  const s0 = v.segments[0];
  return (
    <Chapter id="forecast" innerRef={wrap} className="px-4 py-24 md:px-8 md:py-32">
      <Reveal>
        <h2 className="display max-w-[16ch] text-4xl font-semibold md:text-5xl">Crossing into the forecast.</h2>
        <p className="mt-5 max-w-[60ch] text-lg leading-relaxed text-muted">
          Revenue is built from systems shipped times price, against the capacity ASML has announced. FY26 lands on the €43-45bn guidance. A five-year fade then hands over to the perpetuity.
        </p>
      </Reveal>
      <div className="mt-12 grid gap-12 lg:grid-cols-12">
        <div className="lg:col-span-8"><TimelineChart v={v} base={base} /></div>
        <div className="grid content-start gap-6 lg:col-span-4">
          <p className="text-sm font-medium">Bend the future</p>
          <Slider label="System shipments vs case, every year" value={ov.volumeShift ?? 0} min={-0.25} max={0.2} step={0.01}
            format={(x) => `${x >= 0 ? "+" : "-"}${pct(Math.abs(x), 0)}`} onChange={(volumeShift) => setOv({ volumeShift })}
            hint="Scales EUV, DUV and metrology volumes. Installed base follows the existing fleet." />
          <Slider label="EBITDA margin vs case, every year" value={ov.marginShift ?? 0} min={-0.08} max={0.06} step={0.0025}
            format={(x) => `${x >= 0 ? "+" : "-"}${pct(Math.abs(x))}`} onChange={(marginShift) => setOv({ marginShift })} />
          <dl className="grid grid-cols-2 gap-4 border-t border-line pt-4 text-sm">
            <div><dt className="text-xs text-faint">FY26E revenue</dt><dd className="num text-lg">{eurm(s0.total)}</dd></div>
            <div><dt className="text-xs text-faint">FY30E revenue</dt><dd className="num text-lg">{eurm(v.rows[4].revenue)}</dd></div>
            <div><dt className="text-xs text-faint">EUV share of FY30 systems</dt><dd className="num text-lg">{pct((v.segments[4].nxe + v.segments[4].exe) / (v.segments[4].total - v.segments[4].ib), 0)}</dd></div>
            <div><dt className="text-xs text-faint">FY25-30 CAGR</dt><dd className="num text-lg">{pct(v.cagr)}</dd></div>
          </dl>
        </div>
      </div>
      <div className="mt-16 grid gap-12 lg:grid-cols-12">
        <div className="grid content-start gap-12 lg:col-span-8">
          <div>
            <h3 className="mb-4 text-sm text-muted">Systems shipped versus stated capacity</h3>
            <Units v={v} />
          </div>
          <div>
            <h3 className="mb-6 text-sm text-muted">From profit to free cash flow, per explicit year</h3>
            <UfcfBuild v={v} />
            <p className="mt-4 text-xs text-faint">FY26 includes a working-capital outflow as customer down payments normalise from -27% of sales (FY25) toward -12%.</p>
          </div>
        </div>
        <div className="lg:col-span-4">
          <h3 className="mb-2 text-sm text-muted">Why these assumptions</h3>
          <Why />
        </div>
      </div>
    </Chapter>
  );
}
