const BASE = import.meta.env.VITE_API ?? "http://localhost:8000";

export async function getSample(event = false, ood = false) {
  const res = await fetch(`${BASE}/sample?event=${event}&ood=${ood}`);
  if (!res.ok) throw new Error("sample request failed");
  return res.json();
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
