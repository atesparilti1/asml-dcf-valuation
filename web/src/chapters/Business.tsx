import { motion, useReducedMotion } from "motion/react";
import { useState } from "react";
import { Chapter, EASE, Reveal, useChapterTime } from "../components/ui";
import { DATA } from "../model/dcf";
import { eurm, pct } from "../lib/format";

const B = DATA.business;
const totalSales = DATA.revenue2025;

function Bar({ items, colorFor }: { items: [string, number][]; colorFor: (i: number, label: string) => string }) {
  const reduce = useReducedMotion();
  const [hover, setHover] = useState<number | null>(null);
  const total = items.reduce((a, [, v]) => a + v, 0);
  return (
    <div>
      <div className="flex h-12 w-full" role="img" aria-label="Revenue mix bar">
        {items.map(([l, v], i) => (
          <motion.div key={l} onMouseEnter={() => setHover(i)} onMouseLeave={() => setHover(null)} onFocus={() => setHover(i)} onBlur={() => setHover(null)} tabIndex={0}
            aria-label={`${l} ${pct(v / total)}`}
            className="h-full border-r-2 border-bg transition-opacity duration-200"
            style={{ width: `${(v / total) * 100}%`, background: colorFor(i, l), opacity: hover === null || hover === i ? 1 : 0.45, transformOrigin: "left" }}
            initial={reduce ? false : { scaleX: 0 }} whileInView={{ scaleX: 1 }} viewport={{ once: true }}
            transition={{ duration: 0.8, delay: i * 0.08, ease: EASE }} />
        ))}
      </div>
      <p className="num mt-2 h-5 text-xs text-muted">
        {hover !== null ? `${items[hover][0]}: ${eurm(items[hover][1])} (${pct(items[hover][1] / total)})` : "Hover a segment"}
      </p>
    </div>
  );
}

export function Business() {
  const ref = useChapterTime(2025.9);
  const tech = B.technology as [string, number, number][];
  const euv = tech[0][2] + tech[1][2];
  const sys = tech.reduce((a, t) => a + t[2], 0);
  const mix: [string, number][] = [["EUV (NXE + High-NA EXE)", euv], ["DUV immersion", tech[2][2]], ["Other DUV", tech[3][2] + tech[4][2] + tech[5][2]], ["Metrology & inspection", tech[6][2]], ["Installed base (service, upgrades)", B.installed_base]];
  const regions = B.region as [string, number][];
  const maxR = regions[0][1];
  return (
    <Chapter id="business" innerRef={ref} className="px-4 py-24 md:px-8 md:py-32">
      <Reveal>
        <h2 className="display max-w-[18ch] text-4xl font-semibold md:text-5xl">Where the EUR 32.7bn comes from.</h2>
        <p className="mt-5 max-w-[60ch] text-lg leading-relaxed text-muted">
          ASML sells lithography systems, then earns recurring revenue servicing and upgrading them. Two things drive valuation: EUV pricing power and the cyclical capex of a handful of chipmakers.
        </p>
      </Reveal>
      <div className="mt-14 grid gap-px bg-line lg:grid-cols-3">
        <Reveal className="bg-bg p-6 lg:col-span-2 lg:p-8">
          <h3 className="text-sm text-muted">FY25 revenue by product</h3>
          <p className="num mt-2 text-4xl font-medium">{pct(euv / sys, 0)} <span className="text-base text-muted">of system sales is EUV</span></p>
          <div className="mt-8">
            <Bar items={mix} colorFor={(i) => (i === 0 ? "var(--accent)" : i === 4 ? "var(--muted)" : i === 1 ? "var(--ink)" : "var(--faint)")} />
          </div>
          <div className="mt-6 grid grid-cols-2 gap-4 text-sm sm:grid-cols-4">
            {[["EUV systems recognised", `${B.euv_units["2025"]}`], ["Installed base share", pct(B.installed_base / totalSales, 0)],
              ["Logic / Memory", `${pct(B.end_use[0][1] as number / sys, 0)} / ${pct(B.end_use[1][1] as number / sys, 0)}`], ["Backlog", `€${B.backlog_eur_bn}bn`]].map(([k, v]) => (
              <div key={k} className="border-t border-line pt-2"><p className="text-xs text-faint">{k}</p><p className="num text-lg">{v}</p></div>
            ))}
          </div>
        </Reveal>
        <Reveal delay={0.1} className="bg-accent p-6 text-accent-ink lg:p-8">
          <h3 className="text-sm opacity-80">Customer concentration</h3>
          <p className="num display mt-4 text-8xl font-medium">{pct(B.top4_pct, 0)}</p>
          <p className="mt-4 max-w-[30ch] text-[15px] leading-relaxed opacity-90">
            of FY25 sales came from four customers. The largest alone was {pct(B.largest_customer_pct)}. Their capex plans are ASML's revenue forecast.
          </p>
        </Reveal>
        <Reveal delay={0.15} className="bg-surface p-6 lg:col-span-3 lg:p-8">
          <div className="grid gap-8 lg:grid-cols-3">
            <div>
              <h3 className="text-sm text-muted">FY25 sales by customer location</h3>
              <p className="mt-3 max-w-[34ch] text-[15px] leading-relaxed text-muted">
                China, Taiwan and South Korea account for {pct((regions[0][1] + regions[1][1] + regions[2][1]) / totalSales, 0)} of sales. Export controls on China are the largest single policy risk in the model.
              </p>
            </div>
            <div className="grid gap-2 lg:col-span-2">
              {regions.slice(0, 7).map(([l, v], i) => (
                <div key={l} className="grid grid-cols-[110px_1fr_70px] items-center gap-3 text-sm">
                  <span className="text-muted">{l}</span>
                  <motion.div className="h-3 origin-left" style={{ width: `${(v / maxR) * 100}%`, background: i === 0 ? "var(--ink)" : "var(--faint)" }}
                    initial={{ scaleX: 0 }} whileInView={{ scaleX: 1 }} viewport={{ once: true }} transition={{ duration: 0.8, delay: 0.05 * i, ease: EASE }} />
                  <span className="num text-right">{pct(v / totalSales)}</span>
                </div>
              ))}
            </div>
          </div>
        </Reveal>
      </div>
      <p className="mt-4 text-xs text-faint">Source: ASML Annual Report 2025, revenue disaggregation and geographic notes [S1].</p>
    </Chapter>
  );
}
