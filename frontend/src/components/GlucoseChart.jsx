const W = 720;
const H = 320;
const PAD = { l: 44, r: 16, t: 16, b: 28 };
const innerW = W - PAD.l - PAD.r;
const innerH = H - PAD.t - PAD.b;

function buildScales(xs, ys) {
  const xMin = Math.min(...xs);
  const xMax = Math.max(...xs);
  const yMin = Math.min(...ys) - 10;
  const yMax = Math.max(...ys) + 10;
  const x = (t) => PAD.l + ((t - xMin) / (xMax - xMin)) * innerW;
  const y = (v) => PAD.t + ((yMax - v) / (yMax - yMin)) * innerH;
  return { x, y, xMin, xMax, yMin, yMax };
}

const line = (pts, s) => pts.map((p, i) => `${i ? "L" : "M"}${s.x(p.t)},${s.y(p.v)}`).join(" ");

function GlucoseChart({ history, horizon, forecast, lower, upper, trueFuture, hypo, hyper }) {
  const lastV = history.cgm[history.cgm.length - 1];
  const hist = history.minutes.map((t, i) => ({ t, v: history.cgm[i] }));
  const fc = [{ t: 0, v: lastV }, ...horizon.map((t, i) => ({ t, v: forecast[i] }))];
  const up = [{ t: 0, v: lastV }, ...horizon.map((t, i) => ({ t, v: upper[i] }))];
  const lo = [{ t: 0, v: lastV }, ...horizon.map((t, i) => ({ t, v: lower[i] }))];
  const truth = trueFuture
    ? [{ t: 0, v: lastV }, ...horizon.map((t, i) => ({ t, v: trueFuture[i] }))]
    : null;

  const xs = [...hist, ...fc].map((p) => p.t);
  const ys = [...hist.map((p) => p.v), ...up.map((p) => p.v), ...lo.map((p) => p.v), hypo, hyper];
  const s = buildScales(xs, ys);

  const band = `${line(up, s)} L${s.x(lo[lo.length - 1].t)},${s.y(lo[lo.length - 1].v)} ${lo
    .slice()
    .reverse()
    .map((p) => `L${s.x(p.t)},${s.y(p.v)}`)
    .join(" ")} Z`;

  const yTicks = [];
  for (let v = Math.ceil(s.yMin / 50) * 50; v <= s.yMax; v += 50) yTicks.push(v);
  const xTicks = [s.xMin, 0, 30, 60].filter((t) => t >= s.xMin && t <= s.xMax);

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full">
      {yTicks.map((v) => (
        <g key={`y${v}`}>
          <line x1={PAD.l} x2={W - PAD.r} y1={s.y(v)} y2={s.y(v)} stroke="#f1f5f9" />
          <text x={PAD.l - 6} y={s.y(v) + 3} textAnchor="end" fontSize="10" fill="#94a3b8">
            {v}
          </text>
        </g>
      ))}
      {xTicks.map((t) => (
        <text key={`x${t}`} x={s.x(t)} y={H - 8} textAnchor="middle" fontSize="10" fill="#94a3b8">
          {t === 0 ? "now" : `${t > 0 ? "+" : ""}${t}m`}
        </text>
      ))}

      {/* danger thresholds */}
      <line x1={PAD.l} x2={W - PAD.r} y1={s.y(hypo)} y2={s.y(hypo)} stroke="#ef4444"
        strokeDasharray="4 4" strokeWidth="1" />
      <line x1={PAD.l} x2={W - PAD.r} y1={s.y(hyper)} y2={s.y(hyper)} stroke="#f59e0b"
        strokeDasharray="4 4" strokeWidth="1" />

      {/* uncertainty band */}
      <path d={band} fill="#6366f1" fillOpacity="0.12" />

      {/* now marker */}
      <line x1={s.x(0)} x2={s.x(0)} y1={PAD.t} y2={H - PAD.b} stroke="#cbd5e1" strokeDasharray="2 3" />

      {truth && (
        <path d={line(truth, s)} fill="none" stroke="#94a3b8" strokeWidth="1.5"
          strokeDasharray="1 4" />
      )}
      <path d={line(hist, s)} fill="none" stroke="#334155" strokeWidth="2.5" />
      <path d={line(fc, s)} fill="none" stroke="#6366f1" strokeWidth="2.5" strokeDasharray="6 4" />
    </svg>
  );
}

export default GlucoseChart;
