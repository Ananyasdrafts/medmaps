function RiskPanel({ risk }) {
  return (
    <div className="grid grid-cols-2 gap-3">
      {risk.map((r) => (
        <div
          key={r.horizon_min}
          className={`rounded-xl border p-4 ${
            r.event ? "border-rose-200 bg-rose-50" : "border-slate-200 bg-white"
          }`}
        >
          <div className="text-xs uppercase tracking-wide text-slate-400">
            in {r.horizon_min} min
          </div>
          <div className="mt-1 text-2xl font-semibold text-slate-800">
            {r.pred} <span className="text-sm font-normal text-slate-400">mg/dL</span>
          </div>
          <div className="text-xs text-slate-500">
            range {r.lower} to {r.upper}
          </div>
          {r.event && (
            <div className="mt-2 inline-block rounded-full bg-rose-100 px-2 py-0.5 text-xs font-medium text-rose-700">
              risk of event
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

export default RiskPanel;
