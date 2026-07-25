---
title: "Routes & Sitemap"
---

> All application routes and navigation. Last updated: February 2026

---

## Client Routes

| Path | Component | Description |
|------|-----------|-------------|
| `/` | `HomePage` | Landing page. Intro to VizAdvisor, call-to-action to start advising |
| `/advisor` | `AdvisorPage` | Main tool. Upload data, set goal, get LLM recommendations. Pre/post analysis panels |
| `/about` | `AboutPage` | What the tool does, how it works, data handling |
| `*` | — | Redirects to `/` (404 fallback) |

---

## Navigation

### Header Links

- **VizAdvisor** (logo) → `/`
- **Advisor** → `/advisor`
- **About** → `/about`
- **Theme toggle** — Light/dark mode
- **GitHub** — External link (`VITE_REPO_URL`)

### Footer

- Footer content (varies by implementation)

---

## API Endpoints (Server)

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/recommend` | Proxy to LLM (Anthropic/OpenAI). Forwards messages, returns completion |
| `POST` | `/api/analyze` | Run R or Python analysis. Body: `{ engine, analysisType, data, config }` |

---

## Route Configuration

Defined in `src/App.jsx`:

```jsx
<Routes>
  <Route path="/"        element={<HomePage />} />
  <Route path="/advisor" element={<AdvisorPage />} />
  <Route path="/about"   element={<AboutPage />} />
  <Route path="*"        element={<Navigate to="/" replace />} />
</Routes>
```

Pages are lazy-loaded for code splitting.

---

## Default Entry

- `run.sh` opens `http://localhost:5173/advisor` by default
- Vite dev server: `http://localhost:5173`
