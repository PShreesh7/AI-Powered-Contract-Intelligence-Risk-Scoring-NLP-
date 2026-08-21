# Contract Review Frontend (scaffold)

React + Vite scaffold for the contract review tool. Two-pane layout:

- **Left — Contract Viewer**: full contract text with risky clauses highlighted inline (color-coded by risk level), click a highlight to select it.
- **Right — Risk Panel**: an overall risk gauge (styled as a stamped seal) plus a clause list sorted by risk score, with rationale for each flag. Clicking a clause scrolls the viewer to it.

## Setup

```bash
cd frontend
npm install
npm run dev
```

Runs at `http://localhost:5173`. The dev server proxies `/api/*` to `http://localhost:8000` (see `vite.config.js`) — point that at wherever your backend (built on `text_utils.py`) is running.

## Wiring up the real backend

Right now `src/api/client.js` returns mock data (`src/api/mockData.js`) so the UI can be built and demoed without the backend. To connect it:

1. Implement `POST /api/analyze` on the backend, accepting a file or raw text and returning the shape documented at the top of `src/api/client.js` (`overallRisk`, `clauses[]` with offsets, `fullText`).
2. Flip `USE_MOCK = false` in `src/api/client.js`.

## Structure

```
src/
  api/           # backend client + mock data
  components/
    Header.jsx        # top bar + file upload
    ContractViewer.jsx # highlighted contract text
    ClauseList.jsx      # sidebar list of flagged clauses
    RiskGauge.jsx        # overall risk seal/gauge
  styles/
    theme.css      # design tokens (color, type, radii)
    app.css        # layout + component styles
  App.jsx
  main.jsx
```

## Not yet done (next passes)

- Wire `/api/analyze` to the real backend and drop the mock.
- File type handling for `.pdf` / `.docx` uploads (currently just forwarded as a raw file to the backend).
- Deployment config (Render/Railway/Fly.io) — separate task.
