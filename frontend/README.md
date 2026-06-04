# MedMaps dashboard

A small React + Vite + Tailwind UI for the MedMaps API. It shows the recent glucose
curve, the forecast with a shaded uncertainty band, the risk readout, the
plain-language drivers, and the honest "not enough signal" state when the model
abstains.

```bash
npm install
npm run dev      # http://localhost:5173, expects the API on http://localhost:8000
```

Point it at a different API with `VITE_API`:

```bash
VITE_API=http://localhost:9000 npm run dev
```

The chart is hand-drawn SVG (no chart library) so it is easy to restyle.
