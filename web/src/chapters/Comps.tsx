import { scaleLinear } from "d3-scale";
import { motion, useInView, useReducedMotion } from "motion/react";
import { useRef } from "react";
import { Chapter, EASE, Reveal, useChapterTime } from "../components/ui";
import { COMPS, DATA } from "../model/dcf";
import { eur, eurm, mult, pct } from "../lib/format";
import { TODAY, useValuation } from "../state/valuation";

/** Trading comparables: how the market prices ASML's peers today. */
export function Comps() {
  const ref = useChapterTime(TODAY);
  const v = useValuation();
  const box = useRef<HTMLDivElement>(null);
  const seen = useInView(box, { once: true, amount: 0.3 });
  const reduce = useReducedMotion();
  const a = DATA.comps.asml;
  const rows = [
    ...COMPS.peers.map((p) => ({ name: p.name, ticker: p.ticker, mult: p.mult, fpe: p.fpe, gm: p.gm, om: p.om, asml: false })),
    { name: "ASML", ticker: "ASML", mult: a.ev / a.ebitda, fpe: a.fpe, gm: a.gm, om: a.om, asml: true },
  ].sort((p, q) => q.mult - p.mult);
  const x = scaleLinear().domain([0, 50]).range([0, 100]);
  const marks = [
    { l: "Base exit multiple (FY35)", m: v.exit },
    { l: "ASML FY21-25 average", m: DATA.comps.histAvgEvEbitda },
    { l: "Peer median today", m: COMPS.median },
  ];
  return (
    <Chapter id="comps" innerRef={ref} className="px-4 py-24 md:px-8 md:py-32">
      <Reveal>
        <h2 className="display max-w-[16ch] text-4xl font-semibold md:text-5xl">Against the peers.</h2>
        <p className="mt-5 max-w-[60ch] text-lg leading-relaxed text-muted">
          Applied Materials, Lam Research, KLA and Tokyo Electron sell the other tools in the same fabs. Their multiples show how the market prices the whole AI equipment cycle.
        </p>
      </Reveal>
      <div ref={box} className="mt-12 grid gap-12 lg:grid-cols-12">
        <div className="lg:col-span-7">
          <p className="mb-3 text-xs text-faint">EV / trailing EBITDA</p>
          <div className="grid gap-3">
            {rows.map((r, i) => (
              <div key={r.ticker} className="grid grid-cols-[minmax(0,140px)_1fr_56px] items-center gap-4 text-sm">
                <span className={r.asml ? "font-semibold" : "text-muted"}>{r.name}</span>
                <div className="relative h-6">
                  <motion.div className="absolute inset-y-0 left-0 origin-left" style={{ width: `${x(r.mult)}%`, background: r.asml ? "var(--accent)" : "var(--ink)" }}
                    initial={reduce ? false : { scaleX: 0 }} animate={{ scaleX: seen || reduce ? 1 : 0 }} transition={{ duration: 0.8, delay: reduce ? 0 : i * 0.08, ease: EASE }} />
                </div>
                <span className="num text-right">{mult(r.mult)}</span>
              </div>
            ))}
            <div className="grid grid-cols-[minmax(0,140px)_1fr_56px] gap-4">
              <span />
              <div className="relative h-16 border-t border-line">
                {marks.map((mk, i) => (
                  <div key={mk.l} className="absolute" style={x(mk.m) > 50 ? { right: `${100 - x(mk.m)}%`, top: i * 18 } : { left: `${x(mk.m)}%`, top: i * 18 }}>
                    <span className={`absolute -top-1 h-3 w-px bg-accent ${x(mk.m) > 50 ? "right-0" : "left-0"}`} />
                    <span className={`num block whitespace-nowrap text-[11px] text-muted ${x(mk.m) > 50 ? "mr-2 text-right" : "ml-2"}`}>{mk.l} {mult(mk.m, 0)}</span>
                  </div>
                ))}
              </div>
              <span />
            </div>
          </div>
          <div className="mt-6 overflow-x-auto">
            <table className="num w-full min-w-[480px] text-sm">
              <thead>
                <tr className="text-xs text-faint">
                  <th className="py-2 text-left font-normal">Company</th><th className="py-2 text-right font-normal">Forward P/E</th>
                  <th className="py-2 text-right font-normal">Gross margin</th><th className="py-2 text-right font-normal">Operating margin</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line border-t border-line">
                {rows.map((r) => (
                  <tr key={r.ticker} className={r.asml ? "font-semibold" : ""}>
                    <td className="py-2">{r.name} <span className="text-xs font-normal text-faint">{r.ticker}</span></td>
                    <td className="py-2 text-right">{mult(r.fpe)}</td><td className="py-2 text-right">{pct(r.gm)}</td><td className="py-2 text-right">{pct(r.om)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="mt-2 text-xs text-faint">Market data 7-8 Oct 2026 (stockanalysis.com). EV / EBITDA computed from reported EV and trailing-twelve-month EBITDA.</p>
          </div>
        </div>
        <div className="grid content-start gap-6 lg:col-span-5">
          <div>
            <p className="text-sm text-muted">ASML valued on peer multiples</p>
            <p className="num display mt-2 text-6xl font-medium">{eur(COMPS.pMed)}</p>
            <p className="num mt-2 text-sm text-muted">Range {eur(COMPS.pLow)} to {eur(COMPS.pHigh)}: {mult(COMPS.low)}-{mult(COMPS.high)} x {eurm(DATA.comps.ltmEbitda)} LTM EBITDA</p>
          </div>
          <p className="border-t border-line pt-4 text-[15px] leading-relaxed text-muted">
            On today's peer multiples ASML is priced in line with its sector. The DCF asks a different question: can trailing multiples of 35-48x hold once this capex cycle matures? Valuing the cash flows gives {eur(v.blend.price)}, which assumes they cannot.
          </p>
        </div>
      </div>
    </Chapter>
  );
}
