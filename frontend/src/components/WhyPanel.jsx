const LABELS = {
  last_cgm: "current glucose",
  mean_cgm: "recent average",
  std_cgm: "variability",
  range_cgm: "spread",
  slope_short: "recent trend",
  slope_long: "longer trend",
  carbs_recent: "recent carbs",
  bolus_recent: "recent insulin",
  basal_mean: "basal insulin",
  steps_since_bolus: "time since insulin",
};

function WhyPanel({ drivers }) {
  const max = Math.max(...drivers.map((d) => Math.abs(d.contribution)), 1);
  return (
    <div className="space-y-3 rounded-xl border border-slate-200 bg-white p-4">
      {drivers.map((d) => {
        const positive = d.contribution >= 0;
        const width = (Math.abs(d.contribution) / max) * 100;
        return (
          <div key={d.feature}>
            <div className="flex justify-between text-sm">
              <span className="text-slate-600">{LABELS[d.feature] ?? d.feature}</span>
              <span className={positive ? "text-emerald-600" : "text-rose-600"}>
                {positive ? "+" : ""}
                {d.contribution}
              </span>
            </div>
            <div className="mt-1 h-1.5 rounded bg-slate-100">
              <div
                className={`h-1.5 rounded ${positive ? "bg-emerald-400" : "bg-rose-400"}`}
                style={{ width: `${width}%` }}
              />
            </div>
          </div>
        );
      })}
      <p className="pt-1 text-xs text-slate-400">
        Each number is how much that signal pushed this 30-minute call up or down.
      </p>
    </div>
  );
}

export default WhyPanel;
