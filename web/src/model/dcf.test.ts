import { describe, expect, it } from "vitest";
import { CASES, COMPS, DATA, gridPrice, value } from "./dcf";

// Expected values are computed by model.py, which verify_model.py proves equal to the Excel workbook.
describe("TS model matches the Excel / Python model", () => {
  for (const c of CASES) {
    it(`${c} case`, () => {
      const v = value(c);
      const e = DATA.expected[c];
      expect(v.wacc).toBeCloseTo(e.wacc, 10);
      expect(v.rows[4].revenue).toBeCloseTo(e.rev30, 6);
      expect(v.gordon.price).toBeCloseTo(e.gordon, 6);
      expect(v.exitM.price).toBeCloseTo(e.exit, 6);
      expect(v.blend.price).toBeCloseTo(e.blend, 6);
    });
  }

  it("fade ends at terminal growth", () => {
    const v = value("Base");
    expect(v.rows[9].growth).toBeCloseTo(v.g, 12);
  });

  it("sensitivity centre equals model price", () => {
    const v = value("Base");
    expect(gridPrice(v, v.wacc, { g: v.g })).toBeCloseTo(v.gordon.price, 8);
    expect(gridPrice(v, v.wacc, { exit: v.exit })).toBeCloseTo(v.exitM.price, 8);
  });

  it("comps range is ordered", () => {
    expect(COMPS.pLow).toBeLessThan(COMPS.pMed);
    expect(COMPS.pMed).toBeLessThan(COMPS.pHigh);
  });

  it("moves logically with assumptions", () => {
    const b = value("Base");
    expect(value("Base", { wacc: b.wacc + 0.01 }).gordon.price).toBeLessThan(b.gordon.price);
    expect(value("Base", { g: b.g + 0.005 }).gordon.price).toBeGreaterThan(b.gordon.price);
    expect(value("Base", { marginShift: -0.02 }).blend.price).toBeLessThan(b.blend.price);
    expect(value("Base", { volumeShift: 0.1 }).blend.price).toBeGreaterThan(b.blend.price);
    expect(value("Bear").blend.price).toBeLessThan(b.blend.price);
    expect(value("Bull").blend.price).toBeGreaterThan(b.blend.price);
  });
});
