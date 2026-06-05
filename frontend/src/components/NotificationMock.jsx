function NotificationMock({ alert }) {
  if (!alert || alert.level === "ok") return null;
  const title =
    alert.level === "verify"
      ? "Check your glucose"
      : alert.kind === "hypo"
        ? "Low glucose predicted"
        : "High glucose predicted";

  return (
    <div>
      <div className="mb-1.5 text-xs text-slate-400">what you'd get on your phone</div>
      <div className="flex items-start gap-3 rounded-2xl border border-slate-200 bg-white p-3 shadow-md">
        <div className="flex h-9 w-9 flex-none items-center justify-center rounded-xl bg-slate-800 text-xs font-bold text-white">
          MM
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-center justify-between gap-2">
            <span className="text-xs font-semibold text-slate-500">MedMaps</span>
            <span className="text-xs text-slate-400">now</span>
          </div>
          <div className="text-sm font-semibold text-slate-800">{title}</div>
          <div className="text-sm text-slate-600">{alert.reason}</div>
        </div>
      </div>
    </div>
  );
}

export default NotificationMock;
