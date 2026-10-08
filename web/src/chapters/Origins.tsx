import { motion, useMotionValueEvent, useReducedMotion, useScroll, useTransform } from "motion/react";
import { useLayoutEffect, useRef, useState } from "react";
import { Chapter } from "../components/ui";
import { DATA } from "../model/dcf";
import { useStore } from "../state/valuation";

// Why each milestone matters for the valuation (the moat behind the cash flows)
const VALUE_LINK: Record<number, string> = {
  1984: "Origin of the Philips optics and precision-mechanics know-how.",
  1995: "Capital-market access that funded decades of R&D before profits.",
  2001: "Scale that later pushed Nikon and Canon out of the leading edge.",
  2010: "Start of the only commercial EUV platform.",
  2012: "Customers financed the moat, so switching away is not realistic.",
  2013: "Vertical control of the light source: a barrier no rival has crossed.",
  2016: "More software and metrology content per wafer means higher margins.",
  2019: "EUV became mandatory, which gives ASML pricing power.",
  2023: "High-NA extends the roadmap and the terminal value case.",
  2025: "The base year of this forecast.",
};

// six milestones that explain the moat; the full list lives in inputs.py
const M = DATA.milestones.filter((m) => [1984, 2010, 2012, 2013, 2019, 2023].includes(m.year));

function Card({ m }: { m: (typeof M)[number] }) {
  return (
    <article className="flex w-[78vw] shrink-0 flex-col border-l border-line px-6 py-2 sm:w-[380px] lg:w-[420px]">
      <span className="num display block text-[88px] font-medium text-ink lg:text-[132px]">{m.year}</span>
      <div className="mt-6 grid gap-3">
        <h3 className="text-xl font-semibold tracking-tight">{m.title}</h3>
        <p className="max-w-[40ch] text-[15px] leading-relaxed text-muted">{m.text}</p>
        <p className="max-w-[40ch] border-t border-line pt-3 text-sm leading-relaxed">
          <span className="text-accent">Value link. </span>{VALUE_LINK[m.year]}
        </p>
      </div>
    </article>
  );
}

function Intro() {
  return (
    <div className="flex w-[84vw] shrink-0 flex-col justify-center pr-10 sm:w-[460px]">
      <h2 className="display text-4xl font-semibold md:text-5xl">Forty years to build one monopoly.</h2>
      <p className="mt-5 max-w-[38ch] text-lg leading-relaxed text-muted">
        A DCF values cash flows, but the cash flows rest on a moat. This is how the moat was built.
      </p>
    </div>
  );
}

export function Origins() {
  const reduce = useReducedMotion();
  const wrap = useRef<HTMLElement>(null);
  const track = useRef<HTMLDivElement>(null);
  const [dist, setDist] = useState(0);
  const setTime = useStore((s) => s.setTime);

  useLayoutEffect(() => {
    if (!track.current) return;
    const ro = new ResizeObserver(() => {
      if (!track.current) return;
      setDist(Math.max(0, track.current.scrollWidth - track.current.clientWidth));
    });
    ro.observe(track.current);
    return () => ro.disconnect();
  }, []);

  const { scrollYProgress } = useScroll({ target: wrap, offset: ["start start", "end end"] });
  const x = useTransform(scrollYProgress, [0, 1], [0, -dist]);
  const bar = useTransform(scrollYProgress, [0, 1], ["0%", "100%"]);
  useMotionValueEvent(scrollYProgress, "change", (p) => {
    if (p > 0 && p < 1) setTime(1984 + p * (2023.5 - 1984));
  });

  if (reduce) {
    return (
      <Chapter id="origins" className="px-4 py-24 md:px-8">
        <Intro />
        <div className="no-scrollbar mt-12 flex gap-0 overflow-x-auto pb-4">{M.map((m) => <Card key={m.year} m={m} />)}</div>
      </Chapter>
    );
  }
  return (
    <Chapter id="origins" innerRef={wrap} className="relative" >
      <div style={{ height: `calc(100dvh + ${dist}px)` }}>
        <div className="sticky top-0 flex h-[100dvh] flex-col justify-center overflow-x-clip pb-16 pt-20">
          <motion.div ref={track} style={{ x }} className="flex px-4 md:px-8">
            <Intro />
            {M.map((m) => <Card key={m.year} m={m} />)}
            <div className="w-[10vw] shrink-0" />
          </motion.div>
          <div className="mx-4 mt-10 h-px bg-line md:mx-8">
            <motion.div className="h-px bg-accent" style={{ width: bar }} />
          </div>
        </div>
      </div>
    </Chapter>
  );
}
