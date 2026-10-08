import { motion, useInView, useReducedMotion } from "motion/react";
import { useRef } from "react";
import { Chapter, CountUp, EASE, Reveal, Slider, useChapterTime } from "../components/ui";
import { DATA } from "../model/dcf";
import { eurm, pct } from "../lib/format";
import { TODAY, useStore, useValuation } from "../state/valuation";

const W = DATA.waccInputs;

/** WACC drawn as a stack that assembles itself: rf, then beta x ERP, then the weights. */
function Stack() {
  const v = useValuation();
  const p = v.waccParts;
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, amount: 0.5 });
  const reduce = useReducedMotion();
  const H = 300;
  const scale = H / 0.14; // 14% = full height
  const show = inView || reduce;
  const blocks = [
    { label: "Risk-free rate", sub: "10Y Bund", v: p.rf, fill: "var(--faint)" },
    { label: "Beta x ERP", sub: `${p.beta.toFixed(2)} x ${pct(p.erp, 2)}`, v: p.beta * p.erp, fill: "var(--ink)" },
  ];
  let acc = 0;
  return (
    <div ref={ref} className="grid grid-cols-[1fr_auto_1fr] items-end gap-4 sm:gap-8">
      <div>
        <p className="mb-3 text-sm text-muted">Cost of equity</p>
        <div className="relative w-full" style={{ height: H }}>
          {blocks.map((b, i) => {
            const y = acc;
            acc += b.v;
            return (
              <motion.div key={b.label} className="absolute inset-x-0 flex items-start justify-between px-3 py-2 text-xs"
                style={{ background: b.fill, color: i === 0 ? "var(--ink)" : "var(--bg)" }}
                initial={false} animate={{ bottom: show ? y * scale : H, height: b.v * scale, opacity: show ? 1 : 0 }}
                transition={{ duration: 0.8, delay: reduce ? 0 : i * 0.45, ease: EASE }}>
                <span>{b.label}<span className="block opacity-70">{b.sub}</span></span>
                <span className="num">{pct(b.v, 2)}</span>
              </motion.div>
            );
          })}
          <motion.div className="absolute inset-x-0 border-t-2 border-dashed border-accent" initial={false} animate={{ bottom: show ? p.ke * scale : 0, opacity: show ? 1 : 0 }} transition={{ delay: reduce ? 0 : 1, duration: 0.6, ease: EASE }}>
            <span className="num absolute -top-6 right-0 text-sm text-accent">Ke {pct(p.ke, 2)}</span>
          </motion.div>
        </div>
      </div>
      <div className="pb-2 text-2xl text-faint">→</div>
      <div>
        <p className="mb-9 text-sm text-muted">Capital weights at market value</p>
        <div className="relative w-full" style={{ height: H }}>
          <motion.div className="absolute inset-x-0 bottom-0 flex items-end justify-between bg-accent px-3 py-2 text-xs text-accent-ink" initial={false}
            animate={{ height: show ? p.we * H : 0 }} transition={{ delay: reduce ? 0 : 1.3, duration: 0.8, ease: EASE }}>
            <span>Equity {eurm(p.mcap)}</span><span className="num">{pct(p.we, 1)}</span>
          </motion.div>
          <motion.div className="absolute inset-x-0 top-0 bg-ink" initial={false}
            animate={{ height: show ? Math.max(3, p.wd * H) : 0 }} transition={{ delay: reduce ? 0 : 1.6, duration: 0.5 }} />
          <motion.p className="absolute inset-x-0 -top-6 flex justify-between text-xs" initial={false} animate={{ opacity: show ? 1 : 0 }} transition={{ delay: reduce ? 0 : 1.8 }}>
            <span>Debt {eurm(DATA.market.debt)}</span><span className="num">{pct(p.wd, 1)} at {pct(p.kdAt, 2)} after tax</span>
          </motion.p>
        </div>
      </div>
    </div>
  );
}

export function CostOfCapital() {
  const ref = useChapterTime(TODAY);
  const v = useValuation();
  const p = v.waccParts;
  const ov = useStore((s) => s.ov);
  const setOv = useStore((s) => s.setOv);
  return (
    <Chapter id="wacc" innerRef={ref} className="px-4 py-24 md:px-8 md:py-32">
      <div className="grid gap-14 lg:grid-cols-12">
        <div className="lg:col-span-5">
          <Reveal>
            <h2 className="display text-4xl font-semibold md:text-5xl">The price of time and risk.</h2>
            <p className="mt-5 max-w-[48ch] text-lg leading-relaxed text-muted">
              Future cash flows are discounted at the weighted average cost of capital. ASML is almost all equity, so WACC is in practice its cost of equity.
            </p>
          </Reveal>
          <div className="mt-10 flex items-baseline gap-4 border-t border-line pt-6">
            <span className="text-sm text-muted">WACC applied</span>
            <CountUp value={v.wacc} format={(x) => pct(x, 2)} className="num display text-6xl font-medium text-accent" />
          </div>
          <div className="mt-8 grid gap-5">
            <Slider label="Risk-free rate" value={ov.rf ?? W.rf} min={0.02} max={0.05} step={0.0005} format={(x) => pct(x, 2)} onChange={(rf) => setOv({ rf, wacc: undefined })}
              hint="German 10Y Bund, 3.51% on 7 Oct 2026" />
            <Slider label="Beta" value={ov.beta ?? p.betaBlend} min={0.8} max={2.2} step={0.01} format={(x) => x.toFixed(2)} onChange={(beta) => setOv({ beta, wacc: undefined })}
              hint={`Bottom-up semiconductor-equipment beta, relevered: ${p.betaIndL.toFixed(2)}. Regression vs STOXX Europe 600 gives ${W.beta_reg.toFixed(2)} (R² 0.33), too noisy to use alone.`} />
            <Slider label="Equity risk premium" value={ov.erp ?? W.erp} min={0.03} max={0.06} step={0.0005} format={(x) => pct(x, 2)} onChange={(erp) => setOv({ erp, wacc: undefined })}
              hint="Damodaran implied ERP, January 2026" />
          </div>
        </div>
        <div className="lg:col-span-7 lg:pt-6">
          <Stack />
          <p className="mt-6 text-xs leading-relaxed text-faint">
            WACC = E/(D+E) x Ke + D/(D+E) x Kd x (1 - t). Ke = Rf + beta x ERP. Kd = Rf + 0.60% spread (A1/A+ rating), tax shield at the 25.8% Dutch statutory rate. Scenario cases add +/-0.5%.
          </p>
        </div>
      </div>
    </Chapter>
  );
}
