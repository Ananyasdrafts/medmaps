import { useCallback, useEffect, useRef, useState } from "react";
import { getScenario } from "./api";
import AlertBanner from "./components/AlertBanner";
import DriftPanel from "./components/DriftPanel";
import LiveChart from "./components/LiveChart";
import WhyPanel from "./components/WhyPanel";

function Shell({ children }) {
  return (
    <div className="mx-auto max-w-4xl px-4 py-10">
      <header className="mb-6">
        <h1 className="text-2xl font-semibold text-slate-800">MedMaps</h1>
        <p className="text-slate-500">
          A continuous glucose monitor that warns before trouble, says why, and stays calm
          otherwise.
        </p>
      </header>
      {children}
    </div>
  );
}

function Legend() {
  const item = (color, label, dashed) => (
    <span className="flex items-center gap-1.5">
      <span
        className="inline-block h-0.5 w-4"
        style={{
          background: dashed ? "none" : color,
          borderTop: dashed ? `2px dashed ${color}` : "none",
        }}
      />
      {label}
    </span>
  );
  return (
    <div className="mt-2 flex flex-wrap gap-x-5 gap-y-1 text-xs text-slate-400">
      {item("#334155", "so far", false)}
      {item("#6366f1", "forecast", true)}
      {item("#cbd5e1", "what happens next", true)}
    </div>
  );
}

export default function App() {
  const [sc, setSc] = useState(null);
  const [idx, setIdx] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [error, setError] = useState(null);
  const timer = useRef(null);

  const load = useCallback(async () => {
    setError(null);
    setPlaying(false);
    setIdx(0);
    try {
      const data = await getScenario("event");
      setSc(data);
      setPlaying(true);
    } catch {
      setError("Could not reach the MedMaps API. Is the backend running?");
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (!playing || !sc) return undefined;
    timer.current = setInterval(() => {
      setIdx((i) => {
        if (i >= sc.frames.length - 1) {
          setPlaying(false);
          return i;
        }
        return i + 1;
      });
    }, 650);
    return () => clearInterval(timer.current);
  }, [playing, sc]);

  if (error) {
    return (
      <Shell>
        <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
          {error}
        </div>
      </Shell>
    );
  }
  if (!sc) {
    return (
      <Shell>
        <div className="text-slate-400">loading...</div>
      </Shell>
    );
  }

  const frame = sc.frames[idx];
  const atEnd = idx >= sc.frames.length - 1;

  return (
    <Shell>
      <div className="mb-4 flex items-center gap-3">
        <button
          onClick={() => (atEnd ? load() : setPlaying((p) => !p))}
          className="w-20 rounded-lg bg-slate-800 px-3 py-1.5 text-sm font-medium text-white hover:bg-slate-700"
        >
          {atEnd ? "Replay" : playing ? "Pause" : "Play"}
        </button>
        <input
          type="range"
          min={0}
          max={sc.frames.length - 1}
          value={idx}
          onChange={(e) => {
            setPlaying(false);
            setIdx(Number(e.target.value));
          }}
          className="flex-1 accent-slate-700"
        />
        <span className="w-16 text-right text-xs tabular-nums text-slate-400">{frame.now_min}m</span>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <LiveChart
          actual={sc.actual}
          nowMin={frame.now_min}
          horizon={sc.horizon_minutes}
          forecast={frame.forecast}
          lower={frame.lower}
          upper={frame.upper}
          hypo={sc.thresholds.hypo}
          hyper={sc.thresholds.hyper}
          level={frame.alert.level}
        />
        <Legend />
      </div>

      <div className="mt-5 grid gap-5 md:grid-cols-2">
        <div className="space-y-5">
          <AlertBanner alert={frame.alert} />
          <DriftPanel drift={frame.drift} />
        </div>
        <div>
          <h2 className="mb-2 text-sm font-semibold text-slate-700">Why</h2>
          <WhyPanel drivers={frame.drivers} />
        </div>
      </div>
    </Shell>
  );
}
