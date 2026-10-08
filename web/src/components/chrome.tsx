import { ArrowCounterClockwise, CaretUp, DownloadSimple, GithubLogo, LinkedinLogo, Moon, Sun } from "@phosphor-icons/react";
import { AUTHOR, GITHUB_REPO, LINKEDIN } from "../site";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { useEffect, useState } from "react";
import { DATA } from "../model/dcf";
import { eur, eurm, mult, pct, signedPct } from "../lib/format";
import { type Method, priceFor, evFor, TERMINAL, TODAY, useStore, useValuation } from "../state/valuation";
import { CountUp, EASE, Segmented } from "./ui";

export const XLSX_HREF = "./ASML_DCF_Model.xlsx";

export function Nav() {
  const [theme, setTheme] = useState<"light" | "dark" | null>(null);
  useEffect(() => {
    if (theme) document.documentElement.dataset.theme = theme;
  }, [theme]);
  const isDark = theme ? theme === "dark" : typeof window !== "undefined" && window.matchMedia("(prefers-color-scheme: dark)").matches;
  return (
    <header className="fixed inset-x-0 top-0 z-30 h-16 border-b border-line bg-bg/85 backdrop-blur-md">
      <div className="mx-auto flex h-full max-w-[1440px] items-center justify-between gap-4 px-4 md:px-8">
        <a href="#top" className="flex items-baseline gap-3">
          <span className="text-[15px] font-semibold tracking-tight">ASML</span>
          <span className="hidden text-sm text-muted sm:inline">DCF valuation by {AUTHOR}</span>
        </a>
        <nav className="hidden items-center gap-6 text-sm text-muted lg:flex">
          <a href="#summary" className="hover:text-ink">Summary</a>
          <a href="#reported" className="hover:text-ink">History</a>
          <a href="#forecast" className="hover:text-ink">Forecast</a>
          <a href="#bridge" className="hover:text-ink">Valuation</a>
          <a href="#comps" className="hover:text-ink">Comps</a>
          <a href="#stress" className="hover:text-ink">Sensitivity</a>
          <a href="#verdict" className="hover:text-ink">Verdict</a>
        </nav>
        <div className="flex items-center gap-2">
          {LINKEDIN && (
            <a href={LINKEDIN} target="_blank" rel="noreferrer" aria-label="LinkedIn profile" className="grid size-9 place-items-center border border-line text-muted transition-colors hover:text-ink">
              <LinkedinLogo size={16} />
            </a>
          )}
          <a href={GITHUB_REPO} target="_blank" rel="noreferrer" aria-label="Source code on GitHub" className="grid size-9 place-items-center border border-line text-muted transition-colors hover:text-ink">
            <GithubLogo size={16} />
          </a>
          <button aria-label="Toggle colour theme" onClick={() => setTheme(isDark ? "light" : "dark")}
            className="grid size-9 place-items-center border border-line text-muted transition-colors hover:text-ink active:scale-[0.97]">
            {isDark ? <Sun size={16} /> : <Moon size={16} />}
          </button>
          <a href={XLSX_HREF} download className="flex h-9 items-center gap-2 bg-ink px-3 text-sm font-medium text-bg transition-transform active:scale-[0.98]">
            <DownloadSimple size={16} weight="bold" /> <span className="hidden sm:inline">Excel model</span>
          </a>
        </div>
      </div>
    </header>
  );
}

/* ----------------------------------------------------------- time rail */
const SEG: [number, number, number, number][] = [
  [1984, 2020, 0, 0.27],
  [2020, TODAY, 0.27, 0.52],
  [TODAY, 2030.6, 0.52, 0.76],
  [2030.6, 2035.6, 0.76, 0.93],
  [2035.6, TERMINAL, 0.93, 1],
];
export function timeToX(t: number) {
  const c = Math.min(TERMINAL, Math.max(1984, t));
  for (const [a, b, x0, x1] of SEG) if (c <= b) return x0 + ((c - a) / (b - a)) * (x1 - x0);
  return 1;
}
const TICKS = [
  { t: 1984, l: "1984", id: "origins" }, { t: 1995, l: "1995", id: "origins" }, { t: 2001, l: "2001", id: "origins" },
  { t: 2010, l: "2010", id: "origins" }, { t: 2019, l: "2019", id: "origins" },
  ...[2021, 2022, 2023, 2024, 2025].map((y) => ({ t: y + 0.5, l: `${String(y).slice(2)}A`, id: "reported" })),
  { t: TODAY, l: "Today", id: "top" },
  ...[2027, 2028, 2029, 2030].map((y) => ({ t: y + 0.5, l: `${String(y).slice(2)}E`, id: "forecast" })),
  ...[2031, 2033, 2035].map((y) => ({ t: y + 0.5, l: `${String(y).slice(2)}E`, id: "forecast" })),
  { t: TERMINAL, l: "∞", id: "terminal" },
];

export function TimeRail() {
  const time = useStore((s) => s.time);
  const reduce = useReducedMotion();
  const x = timeToX(time) * 100;
  const today = timeToX(TODAY) * 100;
  const go = (id: string) => document.getElementById(id)?.scrollIntoView({ behavior: reduce ? "auto" : "smooth" });
  return (
    <div className="fixed inset-x-0 bottom-0 z-20 hidden border-t border-line bg-bg/90 backdrop-blur-md md:block">
      <div className="mx-auto max-w-[1440px] px-8 pb-2 pt-1.5">
        <div className="relative h-10">
          <div className="absolute left-0 right-0 top-3 flex text-[10px] uppercase tracking-[0.14em] text-faint">
            <span className="absolute" style={{ left: 0 }}>History</span>
            <span className="absolute" style={{ left: "27%" }}>Reported</span>
            <span className="absolute text-accent" style={{ left: `${today}%` }}>Forecast</span>
            <span className="absolute text-accent/70" style={{ left: "76%" }}>Fade</span>
            <span className="absolute" style={{ left: "93%" }}>Terminal</span>
          </div>
          {/* past = ink, future = dashed accent */}
          <div className="absolute top-[26px] h-px bg-ink/60" style={{ left: 0, width: `${today}%` }} />
          <div className="absolute top-[26px] h-0 border-t border-dashed border-accent" style={{ left: `${today}%`, right: 0 }} />
          <div className="absolute top-[18px] h-4 w-px bg-accent" style={{ left: `${today}%` }} />
          {TICKS.map((k) => {
            const p = timeToX(k.t) * 100;
            const past = k.t <= time + 0.01;
            return (
              <button key={k.l} onClick={() => go(k.id)} aria-label={`Jump to ${k.l}`} className="group absolute top-[22px] -translate-x-1/2 px-1" style={{ left: `${p}%` }}>
                <span className={`mx-auto block h-2 w-px ${past ? "bg-ink" : "bg-faint"}`} />
                <span className={`num mt-0.5 block text-[10px] leading-none transition-colors group-hover:text-ink ${k.l === "Today" ? "text-accent" : "text-faint"}`}>{k.l}</span>
              </button>
            );
          })}
          <motion.div aria-hidden className="pointer-events-none absolute top-[21px] size-[11px] -translate-x-1/2 border-2 border-bg bg-accent shadow-[0_0_0_1px_var(--accent)]"
            animate={{ left: `${x}%` }} transition={reduce ? { duration: 0 } : { type: "spring", stiffness: 120, damping: 22 }} />
        </div>
      </div>
    </div>
  );
}

/* ----------------------------------------------------------- valuation ticker */
const METHODS: { value: Method; label: string }[] = [
  { value: "blend", label: "Blend" }, { value: "gordon", label: "Gordon" }, { value: "exit", label: "Exit" },
];
const CASE_OPTS = [{ value: "Bear" as const, label: "Bear" }, { value: "Base" as const, label: "Base" }, { value: "Bull" as const, label: "Bull" }];

function TickerBody() {
  const v = useValuation();
  const { method, setMethod, scenario, setScenario, ov, reset } = useStore();
  const price = priceFor(v, method);
  const up = price / DATA.market.price - 1;
  const touched = Object.keys(ov).length > 0;
  return (
    <div className="grid gap-5">
      <div>
        <p className="text-xs text-muted">Implied value per share</p>
        <CountUp value={price} format={(x) => eur(x)} className="num block text-5xl font-medium tracking-tight" />
        <p className="num mt-1 text-sm">
          <span className={up >= 0 ? "text-accent" : "text-ink"}><CountUp value={up} format={(x) => signedPct(x)} /></span>
          <span className="text-muted"> vs {eur(DATA.market.price, 2)} market</span>
        </p>
      </div>
      <div className="grid gap-2">
        <Segmented label="Terminal value method" options={METHODS} value={method} onChange={setMethod} />
        <Segmented label="Scenario" options={CASE_OPTS} value={scenario} onChange={setScenario} />
      </div>
      <dl className="grid grid-cols-2 gap-x-4 gap-y-3 border-t border-line pt-4 text-sm">
        {[
          ["WACC", pct(v.wacc, 2)], ["Terminal g", pct(v.g, 2)], ["Exit multiple", mult(v.exit)], ["Enterprise value", eurm(evFor(v, method))],
          ["Revenue CAGR", pct(v.cagr)], ["TV share of EV", pct(method === "exit" ? v.exitM.tvShare : v.gordon.tvShare, 0)],
        ].map(([k, val]) => (
          <div key={k}>
            <dt className="text-xs text-faint">{k}</dt>
            <dd className="num">{val}</dd>
          </div>
        ))}
      </dl>
      <AnimatePresence>
        {touched && (
          <motion.button initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 6 }} transition={{ duration: 0.25, ease: EASE }}
            onClick={reset} className="flex items-center justify-center gap-2 border border-accent py-2 text-sm text-accent transition-colors hover:bg-accent-soft active:scale-[0.98]">
            <ArrowCounterClockwise size={15} /> Reset to base model
          </motion.button>
        )}
      </AnimatePresence>
    </div>
  );
}

export function TickerAside() {
  return (
    <aside className="hidden xl:block">
      <div className="sticky top-24 border-l border-line pl-6 pr-2">
        <TickerBody />
        <p className="mt-6 text-xs leading-relaxed text-faint">Every number on this page is computed live from the same model as the Excel workbook.</p>
      </div>
    </aside>
  );
}

export function TickerSheet() {
  const [open, setOpen] = useState(false);
  const v = useValuation();
  const method = useStore((s) => s.method);
  const price = priceFor(v, method);
  return (
    <div className="fixed inset-x-0 bottom-0 z-20 border-t border-line bg-bg/95 backdrop-blur-md md:bottom-[58px] xl:hidden">
      <AnimatePresence initial={false}>
        {open && (
          <motion.div initial={{ height: 0 }} animate={{ height: "auto" }} exit={{ height: 0 }} transition={{ duration: 0.35, ease: EASE }} className="overflow-hidden">
            <div className="mx-auto max-w-xl px-4 pt-5"><TickerBody /></div>
          </motion.div>
        )}
      </AnimatePresence>
      <button onClick={() => setOpen((o) => !o)} aria-expanded={open} className="mx-auto flex w-full max-w-xl items-center justify-between px-4 py-3">
        <span className="text-xs text-muted">Implied value</span>
        <span className="num flex items-center gap-3 text-lg">
          <CountUp value={price} format={(x) => eur(x)} />
          <span className="text-xs text-muted">{signedPct(price / DATA.market.price - 1)}</span>
          <CaretUp size={14} className={`transition-transform duration-300 ${open ? "rotate-180" : ""}`} />
        </span>
      </button>
    </div>
  );
}
