const BASE = import.meta.env.VITE_API ?? "http://localhost:8000";

export async function getSample(event = false, ood = false) {
  const res = await fetch(`${BASE}/sample?event=${event}&ood=${ood}`);
  if (!res.ok) throw new Error("sample request failed");
  return res.json();
}

export async function getScenario(kind = "event") {
  // try the live backend (returns a random scenario each call); fall back to the
  // bundled scenarios so the hosted static site works with no server running.
  try {
    const res = await fetch(`${BASE}/scenario?kind=${kind}`);
    if (res.ok) return res.json();
  } catch {
    // backend not reachable; use the static export below
  }
  const res = await fetch(`${import.meta.env.BASE_URL}scenarios.json`);
  if (!res.ok) throw new Error("no scenario available");
  const list = await res.json();
  return list[Math.floor(Math.random() * list.length)];
}

export async function predict(window) {
  const res = await fetch(`${BASE}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ window }),
  });
  if (!res.ok) throw new Error("predict request failed");
  return res.json();
}
