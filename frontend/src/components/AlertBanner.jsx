const STYLES = {
  alert: { box: "border-rose-300 bg-rose-50", dot: "bg-rose-500", title: "text-rose-800", text: "text-rose-700", label: "Alert" },
  watch: { box: "border-amber-300 bg-amber-50", dot: "bg-amber-500", title: "text-amber-800", text: "text-amber-700", label: "Watch" },
  verify: { box: "border-violet-300 bg-violet-50", dot: "bg-violet-500", title: "text-violet-800", text: "text-violet-700", label: "Check manually" },
  ok: { box: "border-emerald-200 bg-emerald-50", dot: "bg-emerald-500", title: "text-emerald-800", text: "text-emerald-700", label: "All clear" },
};

function AlertBanner({ alert }) {
  const s = STYLES[alert.level] ?? STYLES.ok;
  const kind = alert.kind ? ` · ${alert.kind === "hypo" ? "low" : "high"}` : "";
  return (
    <div className={`flex items-start gap-3 rounded-xl border p-4 ${s.box}`}>
      <span className={`mt-1.5 h-2.5 w-2.5 flex-none rounded-full ${s.dot}`} />
      <div>
        <div className={`text-sm font-semibold ${s.title}`}>
          {s.label}
          {kind}
        </div>
        <div className={`text-sm ${s.text}`}>{alert.reason}</div>
      </div>
    </div>
  );
}

export default AlertBanner;
