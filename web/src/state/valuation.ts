import { useMemo } from "react";
import { create } from "zustand";
import { type Case, type Overrides, value } from "../model/dcf";

export type Method = "blend" | "gordon" | "exit";

interface State {
  scenario: Case;
  method: Method;
  ov: Overrides;
  /** Position on the time axis (fractional year; 2032 = terminal). Set by chapters. */
  time: number;
  setScenario: (c: Case) => void;
  setMethod: (m: Method) => void;
  setOv: (o: Partial<Overrides>) => void;
  reset: () => void;
  setTime: (t: number) => void;
}

export const TODAY = 2026 + (31 + 28 + 31 + 30 + 31 + 30 + 31 + 31 + 30 + 7) / 365;
export const TERMINAL = 2032;

export const useStore = create<State>((set) => ({
  scenario: "Base",
  method: "blend",
  ov: {},
  time: TODAY,
  setScenario: (scenario) => set({ scenario }),
  setMethod: (method) => set({ method }),
  setOv: (o) => set((s) => ({ ov: { ...s.ov, ...o } })),
  reset: () => set({ ov: {}, scenario: "Base", method: "blend" }),
  setTime: (time) => set((s) => (Math.abs(s.time - time) > 0.01 ? { time } : s)),
}));

/** Live valuation for the current scenario and user overrides. */
export function useValuation() {
  const scenario = useStore((s) => s.scenario);
  const ov = useStore((s) => s.ov);
  return useMemo(() => value(scenario, ov), [scenario, ov]);
}

/** Untouched model for the current scenario (ghost comparison). */
export function useBaseline() {
  const scenario = useStore((s) => s.scenario);
  return useMemo(() => value(scenario), [scenario]);
}

export function priceFor(v: ReturnType<typeof value>, m: Method) {
  return m === "blend" ? v.blend.price : m === "gordon" ? v.gordon.price : v.exitM.price;
}
export function evFor(v: ReturnType<typeof value>, m: Method) {
  return m === "blend" ? v.blend.ev : m === "gordon" ? v.gordon.ev : v.exitM.ev;
}
