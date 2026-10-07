import { scaleBand, scaleLinear } from "d3-scale";
import { motion, useInView, useReducedMotion } from "motion/react";
import { useState } from "react";
import { Chapter, CountUp, EASE, Reveal, Segmented, Slider, useChapterTime, useSize } from "../components/ui";
import { DATA, reverse } from "../model/dcf";
import { eur, eurm, mult, num, pct } from "../lib/format";
import { type Method, TERMINAL, TODAY, useStore, useValuation } from "../state/valuation";

/* ------------------------------------------------------------- Beyond 2030 */
export function Terminal() {
  const ref = useChapterTime(TERMINAL);
  const v = useValuation();
  const { ov, setOv, method, setMethod } = useStore();
  const m: "gordon" | "exit" = method === "exit" ? "exit" : "gordon";
  const r = m === "gordon" ? v.gordon : v.exitM;
  const rev = reverse(v);
  const reduce = useReducedMotion();
  return (
    <Chapter id="terminal" innerRef={ref} className="px-4 py-24 md:px-8 md:py-32">
      <div className="grid gap-14 lg:grid-cols-12">
        <div className="lg:col-span-5">
          <Reveal>
            <h2 className="display text-4xl font-semibold md:text-5xl">Beyond 2030.</h2>
            <p className="mt-5 max-w-[46ch] text-lg leading-relaxed text-muted">
              Five years of cash flow explain less than a quarter of the value. The rest is the terminal value, so its two methods deserve scrutiny.
            </p>
          </Reveal>
          <div className="mt-8">
            <Segmented<"gordon" | "exit"> label="Terminal method" value={m} onChange={(x) => setMethod(x as Method)}
              options={[{ value: "gordon", label: "Gordon Growth" }, { value: "exit", label: "Exit Multiple" }]} />
          </div>
          <div className="mt-8 grid gap-5">
            {m === "gordon" ? (
              <Slider label="Terminal growth rate (g)" value={ov.g ?? v.g} min={0.01} max={0.04} step={0.0025} format={(x) => pct(x, 2)} onChange={(g) => setOv({ g })}
                hint="TV = FCF FY30 x (1 + g) / (WACC - g)" />
            ) : (
              <Slider label="Exit EV/EBITDA multiple" value={ov.exit ?? v.exit} min={12} max={40} step={0.5} format={(x) => mult(x)} onChange={(exit) => setOv({ exit })}
                hint="TV = EBITDA FY30 x multiple" />
            )}
          </div>
          <dl className="mt-8 grid grid-cols-2 gap-x-6 gap-y-5 border-t border-line pt-6">
            <div><dt className="text-xs text-faint">Terminal value (FY30)</dt><dd className="num text-xl">{eurm(r.tv)}</dd></div>
            <div><dt className="text-xs text-faint">Share of enterprise value</dt><dd className="num text-xl">{pct(r.tvShare, 0)}</dd></div>
            <div><dt className="text-xs text-faint">Gordon implies exit multiple of</dt><dd className="num text-xl">{mult(v.impliedExit)}</dd></div>
            <div><dt className="text-xs text-faint">Exit multiple implies perpetual g of</dt><dd className="num text-xl">{pct(v.impliedG, 1)}</dd></div>
          </dl>
        </div>
        <div className="lg:col-span-7">
          <p className="mb-4 text-sm text-muted">Enterprise value, {m === "gordon" ? "Gordon Growth" : "Exit Multiple"} (EUR m)</p>
          <div className="flex h-24 w-full">
            <motion.div className="flex h-full items-end bg-ink p-3 text-xs text-bg" initial={reduce ? false : { width: 0 }}
              animate={{ width: `${(1 - r.tvShare) * 100}%` }} transition={{ duration: 0.8, ease: EASE }}>
              <span className="truncate">PV FY26-30 FCF<br /><span className="num">{eurm(v.sumPv)}</span></span>
            </motion.div>
            <motion.div className="flex h-full flex-1 items-end justify-end border border-accent p-3 text-right text-xs" style={{ background: "repeating-linear-gradient(45deg, var(--accent-soft) 0 6px, transparent 6px 12px)" }}>
              <span>PV of terminal value<br /><span className="num text-accent">{eurm(r.pvTv)}</span></span>
            </motion.div>
          </div>
          <p className="num mt-3 text-right text-sm">EV <CountUp value={r.ev} format={(x) => eurm(x)} /></p>
          <div className="mt-12 border-t border-line pt-6">
            <h3 className="text-xl font-semibold tracking-tight">What is the market paying for?</h3>
            <p className="mt-3 max-w-[60ch] text-[15px] leading-relaxed text-muted">
              Reverse the DCF: to justify {eur(DATA.market.price)} per share with the same forecast and WACC, the market needs an exit multiple of{" "}
              <span className="num text-ink">{mult(rev.multiple)}</span> FY30 EBITDA, or perpetual growth of <span className="num text-ink">{pct(rev.g, 1)}</span>.
              The first is plausible for ASML; the second is not. The share price is betting that growth continues well beyond 2030.
            </p>
          </div>
        </div>
      </div>
    </Chapter>
  );
}

/* ------------------------------------------------------------- EV to equity waterfall */
const SHORT = ["PV FCF", "PV TV", "EV", "Cash", "Debt", "Invest.", "Equity"];

interface Step { label: string; v: number; kind: "add" | "sub" | "total"; f: string }

export function Bridge() {
  const ref = useChapterTime(TODAY);
  const v = useValuation();
  const method = useStore((s) => s.method);
  const [wref, w] = useSize<HTMLDivElement>();
  const seen = useInView(wref, { once: true, amount: 0.4 });
  const reduce = useReducedMotion();
  const [hover, setHover] = useState<number | null>(null);
  const gw = DATA.meta.gordonWeight;
  const pvTv = method === "blend" ? gw * v.gordon.pvTv + (1 - gw) * v.exitM.pvTv : method === "gordon" ? v.gordon.pvTv : v.exitM.pvTv;
  const ev = v.sumPv + pvTv;
  const eq = ev + v.bridge.net;
  const steps: Step[] = [
    { label: "PV of FCF", v: v.sumPv, kind: "add", f: "Sum of discounted FY26-30 cash flows (FY26 stub net of H1 actual)" },
    { label: "PV of TV", v: pvTv, kind: "add", f: method === "blend" ? "50% Gordon + 50% Exit, discounted from end FY30" : "Terminal value discounted from end FY30" },
    { label: "Enterprise value", v: ev, kind: "total", f: "PV of FCF + PV of terminal value" },
    { label: "+ Cash & STI", v: v.bridge.cash, kind: "add", f: "Cash 6,672 + short-term investments 910 at 28 Jun 2026" },
    { label: "- Debt", v: -v.bridge.debt, kind: "sub", f: "Eurobonds after H1-26 commercial paper repayment" },
    { label: "+ Investments", v: v.bridge.nonop, kind: "add", f: "Equity stakes and equity-method investments (income outside EBIT)" },
    { label: "Equity value", v: eq, kind: "total", f: "EV + cash - debt + non-operating investments" },
  ];
  let run = 0;
  const bars = steps.map((s) => {
    if (s.kind === "total") { run = s.v; return { ...s, a: 0, b: s.v }; }
    const a = run; run += s.v; return { ...s, a: Math.min(a, run), b: Math.max(a, run) };
  });
  const h = Math.min(420, Math.max(280, w * 0.48));
  const mg = { t: 28, b: 54 };
  const x = scaleBand<number>().domain(bars.map((_, i) => i)).range([0, w]).padding(0.22);
  const y = scaleLinear().domain([0, Math.max(...bars.map((b) => b.b)) * 1.08]).range([h - mg.b, mg.t]);
  return (
    <Chapter id="bridge" innerRef={ref} className="px-4 py-24 md:px-8 md:py-32">
      <Reveal>
        <h2 className="display max-w-[18ch] text-4xl font-semibold md:text-5xl">From enterprise to equity.</h2>
        <p className="mt-5 max-w-[56ch] text-lg leading-relaxed text-muted">
          Enterprise value belongs to all capital providers. Add net cash and investments, and divide by diluted shares, to get a value per share.
        </p>
      </Reveal>
      <div ref={wref} className="mt-12">
        <svg width={w} height={h} role="img" aria-label="Waterfall from present value of cash flows to equity value">
          {bars.map((b, i) => {
            const on = seen || reduce;
            return (
              <g key={b.label} onMouseEnter={() => setHover(i)} onMouseLeave={() => setHover(null)}>
                <motion.rect x={x(i)} width={x.bandwidth()} fill={b.kind === "total" ? "var(--accent)" : b.kind === "sub" ? "var(--faint)" : "var(--ink)"}
                  opacity={hover === null || hover === i ? 1 : 0.5}
                  initial={false} animate={{ y: on ? y(b.b) : y(b.a), height: on ? Math.max(1.5, y(b.a) - y(b.b)) : 0 }}
                  transition={{ duration: 0.7, delay: reduce ? 0 : seen ? i * 0.22 : 0, ease: EASE }} />
                {i < bars.length - 1 && <line x1={x(i)! + x.bandwidth()} x2={x(i + 1)} y1={y(b.kind === "sub" ? b.a : b.b)} y2={y(b.kind === "sub" ? b.a : b.b)} stroke="var(--line)" strokeDasharray="2 2" />}
                <motion.text x={x(i)! + x.bandwidth() / 2} textAnchor="middle" className="num" fill="var(--ink)" initial={false}
                  fontSize={w < 640 ? 9 : 12} animate={{ y: y(b.b) - 8, opacity: seen || reduce ? 1 : 0 }} transition={{ delay: reduce ? 0 : i * 0.22 + 0.4 }}>{eurm(b.v, w < 640 ? 0 : 1)}</motion.text>
                <text x={x(i)! + x.bandwidth() / 2} y={h - mg.b + 18} textAnchor="middle" fontSize={w < 640 ? 10 : 12} fill={b.kind === "total" ? "var(--ink)" : "var(--muted)"}>{w < 640 ? SHORT[i] : b.label}</text>
                <rect x={x(i)} width={x.bandwidth()} y={0} height={h - mg.b} fill="transparent" />
              </g>
            );
          })}
        </svg>
        <div className="mt-2 flex flex-wrap items-baseline justify-between gap-4 border-t border-line pt-4">
          <p className="h-5 text-xs text-muted">{hover !== null ? `${steps[hover].label}: ${steps[hover].f}` : "Hover a bar for its definition."}</p>
          <p className="num text-lg">
            {eurm(eq)} / {num(DATA.market.shares, 1)}m shares = <CountUp value={eq / DATA.market.shares} format={(z) => eur(z)} className="text-2xl text-accent" />
          </p>
        </div>
      </div>
    </Chapter>
  );
}
