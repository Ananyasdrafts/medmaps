const W = 760;
const H = 320;
const PAD = { l: 44, r: 16, t: 16, b: 28 };
const innerW = W - PAD.l - PAD.r;
const innerH = H - PAD.t - PAD.b;

const LEVEL_COLOR = { alert: "#e11d48", watch: "#f59e0b", verify: "#7c3aed", ok: "#6366f1" };

const path = (pts, s) =>
  pts.map((p, i) => `${i ? "L" : "M"}${s.x(p.t)},${s.y(p.v)}`).join(" ");

function LiveChart({ actual, nowMin, horizon, forecast, lower, upper, hypo, hyper, level }) {
  const color = LEVEL_COLOR[level] ?? LEVEL_COLOR.ok;

  // fixed domains across the whole scenario so the chart doesn't jump while playing
  const allCgm = actual.map((a) => a.cgm);
  const xMin = actual[0].min;
  const xMax = actual[actual.length - 1].min;
  const yMin = Math.min(...allCgm, hypo) - 10;
  const yMax = Math.max(...allCgm, hyper) + 10;
  const s = {
    x: (t) => PAD.l + ((t - xMin) / (xMax - xMin)) * innerW,
    y: (v) => PAD.t + ((yMax - v) / (yMax - yMin)) * innerH,
  };

  const revealed = actual.filter((a) => a.min <= nowMin).map((a) => ({ t: a.min, v: a.cgm }));
  const future = actual.filter((a) => a.min >= nowMin).map((a) => ({ t: a.min, v: a.cgm }));
  const lastV = revealed.length ? revealed[revealed.length - 1].v : actual[0].cgm;
  const fc = [{ t: nowMin, v: lastV }, ...horizon.map((h, i) => ({ t: nowMin + h, v: forecast[i] }))];
  const up = [{ t: nowMin, v: lastV }, ...horizon.map((h, i) => ({ t: nowMin + h, v: upper[i] }))];
  const lo = [{ t: nowMin, v: lastV }, ...horizon.map((h, i) => ({ t: nowMin + h, v: lower[i] }))];

  const band = `${path(up, s)} ${lo.slice().reverse().map((p) => `L${s.x(p.t)},${s.y(p.v)}`).join(" ")} Z`;

  const yTicks = [];
  for (let v = Math.ceil(yMin / 50) * 50; v <= yMax; v += 50) yTicks.push(v);

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full">
      {yTicks.map((v) => (
        <g key={v}>
          <line x1={PAD.l} x2={W - PAD.r} y1={s.y(v)} y2={s.y(v)} stroke="#f1f5f9" />
          <text x={PAD.l - 6} y={s.y(v) + 3} textAnchor="end" fontSize="10" fill="#94a3b8">{v}</text>
        </g>
      ))}

      <line x1={PAD.l} x2={W - PAD.r} y1={s.y(hypo)} y2={s.y(hypo)} stroke="#ef4444" strokeDasharray="4 4" />
      <line x1={PAD.l} x2={W - PAD.r} y1={s.y(hyper)} y2={s.y(hyper)} stroke="#f59e0b" strokeDasharray="4 4" />

      <path d={band} fill={color} fillOpacity="0.12" />

      <path d={path(future, s)} fill="none" stroke="#cbd5e1" strokeWidth="1.5" strokeDasharray="1 4" />
      <path d={path(revealed, s)} fill="none" stroke="#334155" strokeWidth="2.5" />
      <path d={path(fc, s)} fill="none" stroke={color} strokeWidth="2.5" strokeDasharray="6 4" />

      <line x1={s.x(nowMin)} x2={s.x(nowMin)} y1={PAD.t} y2={H - PAD.b} stroke="#cbd5e1" strokeDasharray="2 3" />
      <text x={s.x(nowMin)} y={H - 8} textAnchor="middle" fontSize="10" fill="#64748b">now</text>
    </svg>
  );
}

export default LiveChart;
