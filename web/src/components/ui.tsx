import { animate, motion, useInView, useMotionValue, useReducedMotion, useTransform } from "motion/react";
import { type ReactNode, useEffect, useLayoutEffect, useRef, useState } from "react";
import { useStore } from "../state/valuation";

export const EASE = [0.16, 1, 0.3, 1] as const;

/** Number that tweens to its new value: feedback that the model recomputed. */
export function CountUp({ value, format, className }: { value: number; format: (x: number) => string; className?: string }) {
  const reduce = useReducedMotion();
  const mv = useMotionValue(value);
  const text = useTransform(mv, format);
  useEffect(() => {
    if (reduce) {
      mv.set(value);
      return;
    }
    const c = animate(mv, value, { duration: 0.7, ease: EASE });
    return () => c.stop();
  }, [value, reduce, mv]);
  return <motion.span className={className}>{text}</motion.span>;
}

export function Slider({ label, value, min, max, step, format, onChange, hint }: {
  label: string; value: number; min: number; max: number; step: number; format: (x: number) => string; onChange: (x: number) => void; hint?: string;
}) {
  const id = label.replace(/\W+/g, "-").toLowerCase();
  return (
    <div className="grid gap-1">
      <div className="flex items-baseline justify-between gap-4">
        <label htmlFor={id} className="text-sm text-muted">{label}</label>
        <span className="num text-sm text-ink">{format(value)}</span>
      </div>
      <input id={id} className="rng" type="range" min={min} max={max} step={step} value={value} onChange={(e) => onChange(parseFloat(e.target.value))} />
      {hint && <p className="text-xs text-faint">{hint}</p>}
    </div>
  );
}

export function Segmented<T extends string>({ options, value, onChange, label }: {
  options: { value: T; label: string }[]; value: T; onChange: (v: T) => void; label: string;
}) {
  return (
    <div role="radiogroup" aria-label={label} className="inline-grid auto-cols-fr grid-flow-col border border-line">
      {options.map((o) => {
        const on = o.value === value;
        return (
          <button key={o.value} role="radio" aria-checked={on} onClick={() => onChange(o.value)}
            className={`relative px-3 py-1.5 text-xs font-medium transition-colors duration-200 active:scale-[0.98] ${on ? "text-accent-ink" : "text-muted hover:text-ink"}`}>
            {on && <motion.span layoutId={`seg-${label}`} className="absolute inset-0 bg-accent" transition={{ type: "spring", stiffness: 420, damping: 36 }} />}
            <span className="relative">{o.label}</span>
          </button>
        );
      })}
    </div>
  );
}

/** Container width for pixel-exact SVG charts. */
export function useSize<T extends HTMLElement>() {
  const ref = useRef<T>(null);
  const [w, setW] = useState(0);
  useLayoutEffect(() => {
    if (!ref.current) return;
    setW(Math.max(280, Math.round(ref.current.getBoundingClientRect().width)));
    const ro = new ResizeObserver(([e]) => setW(Math.max(280, Math.round(e.contentRect.width))));
    ro.observe(ref.current);
    return () => ro.disconnect();
  }, []);
  return [ref, w] as const;
}

/** Moves the time-rail playhead to `time` while this chapter is in view. */
export function useChapterTime(time: number) {
  const ref = useRef<HTMLElement>(null);
  const inView = useInView(ref, { amount: 0.45 });
  const setTime = useStore((s) => s.setTime);
  useEffect(() => {
    if (inView) setTime(time);
  }, [inView, time, setTime]);
  return ref;
}

export function Chapter({ id, children, className = "", innerRef }: { id: string; children: ReactNode; className?: string; innerRef?: React.Ref<HTMLElement> }) {
  return (
    <section id={id} ref={innerRef} className={`scroll-mt-20 border-t border-line ${className}`}>
      {children}
    </section>
  );
}

export function Reveal({ children, delay = 0, className }: { children: ReactNode; delay?: number; className?: string }) {
  const reduce = useReducedMotion();
  return (
    <motion.div className={className} initial={reduce ? false : { opacity: 0, y: 24 }} whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.3 }} transition={{ duration: 0.7, delay, ease: EASE }}>
      {children}
    </motion.div>
  );
}

export function Tag({ children }: { children: ReactNode }) {
  return <span className="inline-block border border-line px-1.5 py-0.5 text-[11px] text-muted">{children}</span>;
}
