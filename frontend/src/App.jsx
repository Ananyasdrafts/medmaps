import { useCallback, useEffect, useState } from "react";
import { getSample, predict } from "./api";
import GlucoseChart from "./components/GlucoseChart";
import RiskPanel from "./components/RiskPanel";
import WhyPanel from "./components/WhyPanel";
import AbstainPanel from "./components/AbstainPanel";

const LEGEND = [
  ["history", "#334155", 1],
  ["forecast", "#6366f1", 1],
  ["uncertainty", "#6366f1", 0.2],
  ["what actually happened", "#94a3b8", 1],
];

export default function App() {
  const [sample, setSample] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const load = useCallback(async (event) => {
    setLoading(true);
    setError(null);
    try {
      const s = await getSample(event);
      const r = await predict(s.window);
      setSample(s);
      setResult(r);
    } catch {
      setError("Could not reach the MedMaps API. Is the backend running on :8000?");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load(false);
  }, [load]);

  return (
    <div className="mx-auto max-w-4xl px-4 py-10">
      <header className="mb-6">
        <h1 className="text-2xl font-semibold text-slate-800">MedMaps</h1>
        <p className="text-slate-500">A glucose early-warning model that says when it isn't sure.</p>
      </header>

      <div className="mb-4 flex items-center gap-2">
        <button
          onClick={() => load(false)}
          className="rounded-lg bg-slate-800 px-3 py-1.5 text-sm font-medium text-white hover:bg-slate-700"
        >
          New reading
        </button>
        <button
          onClick={() => load(true)}
          className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-100"
        >
          Show an event
        </button>
        {loading && <span className="text-sm text-slate-400">loading...</span>}
      </div>

      {error && (
        <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
          {error}
        </div>
      )}

      {sample && result && (
        <div className="space-y-5">
          <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
            <GlucoseChart
              history={{ minutes: sample.history_minutes, cgm: sample.history_cgm }}
              horizon={result.horizon_minutes}
              forecast={result.forecast}
              lower={result.lower}
              upper={result.upper}
              trueFuture={sample.true_future}
              hypo={result.thresholds.hypo}
              hyper={result.thresholds.hyper}
            />
            <div className="mt-2 flex flex-wrap gap-x-5 gap-y-1 text-xs text-slate-400">
              {LEGEND.map(([label, color, opacity]) => (
                <span key={label} className="flex items-center gap-1">
                  <span
                    className="inline-block h-2 w-3 rounded-sm"
                    style={{ background: color, opacity }}
                  />
                  {label}
                </span>
              ))}
            </div>
          </div>

          {result.abstain ? (
            <AbstainPanel reason={result.reason} />
          ) : (
            <div className="grid gap-5 md:grid-cols-2">
              <section>
                <h2 className="mb-2 text-sm font-semibold text-slate-700">Risk</h2>
                <RiskPanel risk={result.risk} />
              </section>
              <section>
                <h2 className="mb-2 text-sm font-semibold text-slate-700">Why</h2>
                <WhyPanel drivers={result.drivers} />
              </section>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
