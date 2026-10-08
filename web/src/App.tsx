import { Nav, TickerAside, TickerSheet, TimeRail } from "./components/chrome";
import { Business } from "./chapters/Business";
import { CostOfCapital } from "./chapters/CostOfCapital";
import { Forecast } from "./chapters/Forecast";
import { Comps } from "./chapters/Comps";
import { Hero, Summary } from "./chapters/Hero";
import { Origins } from "./chapters/Origins";
import { Futures, StressTest, Verdict } from "./chapters/Outcomes";
import { Reported } from "./chapters/Reported";
import { Bridge, Terminal } from "./chapters/Valuation";

export default function App() {
  return (
    <>
      <Nav />
      <div className="mx-auto grid max-w-[1440px] xl:grid-cols-[minmax(0,1fr)_300px]">
        <main className="min-w-0 overflow-x-clip">
          <Hero />
          <Summary />
          <Origins />
          <Reported />
          <Business />
          <CostOfCapital />
          <Forecast />
          <Terminal />
          <Bridge />
          <Comps />
          <StressTest />
          <Futures />
          <Verdict />
        </main>
        <TickerAside />
      </div>
      <TickerSheet />
      <TimeRail />
    </>
  );
}
