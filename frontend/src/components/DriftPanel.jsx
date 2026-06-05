function DriftPanel({ drift }) {
  if (!drift) return null;
  const slipping = drift.status === "slipping";
  const badge = slipping
    ? "bg-amber-100 text-amber-700"
    : drift.status === "improving"
      ? "bg-emerald-100 text-emerald-700"
      : "bg-slate-100 text-slate-600";

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-700">This stretch</h3>
        <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${badge}`}>{drift.status}</span>
      </div>
      <div className="mt-3 flex gap-8 text-sm">
        <div>
          <div className="text-xs text-slate-400">time in range</div>
          <div className="text-lg font-semibold text-slate-800">{drift.time_in_range}%</div>
        </div>
        <div>
          <div className="text-xs text-slate-400">variability (CV)</div>
          <div className="text-lg font-semibold text-slate-800">{drift.cv}</div>
        </div>
      </div>
      {drift.reasons?.length > 0 && (
        <ul className="mt-3 list-disc space-y-0.5 pl-4 text-xs text-amber-700">
          {drift.reasons.map((r) => (
            <li key={r}>{r}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default DriftPanel;
