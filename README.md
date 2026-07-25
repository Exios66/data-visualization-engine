# VizAdvisor — A Subject Matter Expert (SME) Data Visualization Consultant

A full-stack web application that helps users describe their dataset and visualization goals, then receives tailored, LLM-powered recommendations on the best visualization strategies, chart types, and parameters. Includes optional pre- and post-visualization statistical analysis via R or Python.

## Live documentation (Posit Connect Cloud)

**Public URL:** https://019f9a69-7c76-3f0a-e2b1-c586d1b61682.share.connect.posit.cloud/

**Dashboard:** https://connect.posit.cloud/jackjburleson/content/019f9a69-7c76-3f0a-e2b1-c586d1b61682

This is a Quarto website documenting the full VizAdvisor product — architecture, prompt design, chart taxonomy, analysis service, API routes, and contribution guides — published as a **new** content instance on the Jack J. Burleson Posit Connect Cloud account. Source: `index.qmd`, `_quarto.yml`, `docs/`.

```bash
cd posit-site
quarto render
# Publish updates to the VizAdvisor content id (see _publish.yml):
python3 scripts/publish_posit_new.py --content-id 019f9a69-7c76-3f0a-e2b1-c586d1b61682
```

---

## Features

| Feature | Description |
|---------|-------------|
| **CSV/JSON Upload** | Drag-and-drop or paste data; automatic schema inference |
| **Goal Selection** | Compare, trend, distribution, correlation, part-of-whole, geospatial, network, ranking |
| **LLM Recommendations** | Structured output: chart type, rationale, design decisions, code scaffold |
| **Pre-Viz Analysis** | Optional descriptive stats, regression, power, mediation, factorial (R or Python) |
| **Post-Viz Analysis** | Same analysis types after receiving recommendations |
| **Dark Mode** | Theme toggle with persistent preference |
| **Export** | Copy or download recommendations as Markdown/JSON |
| **Session History** | Save and load past sessions (localStorage) |

---

## Repository Map

```bash
vizadvisor/
├── README.md                    # This file
├── CHANGELOG.md                 # Version history
├── run.sh                       # One-command dev launcher (npm install + dev:full + open browser)
├── .env.example                 # Client env template
├── package.json
├── vite.config.js
├── index.html
├── mermaid-map.md               # Mermaid flowchart of repo structure
├── posit-site/                  # Quarto → Posit Connect Cloud documentation site
│   ├── index.qmd                # Site homepage
│   ├── _quarto.yml              # Quarto website config
│   ├── _publish.yml             # Posit Connect Cloud content id / URL
│   ├── styles.scss              # UW Badger red theme
│   ├── references.bib
│   ├── docs/                    # Quarto pages (+ includes of ../docs)
│   └── scripts/publish_posit_new.py
│
├── public/
│   └── vite.svg
│
├── src/
│   ├── main.jsx                 # App entry point
│   ├── App.jsx                  # Root component, routing, theme wrapper
│   │
│   ├── components/
│   │   ├── layout/              # Header, Footer, Sidebar
│   │   ├── input/               # DataUploader, DataPreview, GoalSelector, ParameterPanel, PromptBuilder
│   │   ├── output/              # RecommendationList, RecommendationCard, CodeSnippet, ExportButton, etc.
│   │   ├── analysis/            # AnalysisPanel, AnalysisResults
│   │   └── common/              # Button, Spinner, Modal, Tooltip, ErrorBanner, CopyButton, Badge
│   │
│   ├── pages/                   # HomePage, AdvisorPage, AboutPage
│   ├── hooks/                   # useLLM, useDataParser, useSessionHistory, useAnalysis
│   ├── services/                # llmService, dataService, promptTemplates, analysisService
│   ├── context/                 # SessionContext, SettingsContext
│   ├── utils/                   # columnTypeInferrer, chartTypeMapper, formatters, responseValidator
│   └── styles/                  # global.css, theme.js
│
├── server/                      # Express API proxy + analysis runner
│   ├── index.js                 # /api/recommend (LLM), /api/analyze (R/Python)
│   ├── .env.example
│   ├── requirements.txt         # Python analysis deps
│   └── analysis/
│       ├── runner.js            # Spawns R/Python scripts, validates input
│       ├── README.md
│       ├── r/                   # descriptive.R, regression.R, power.R, mediation.R, factorial.R
│       └── python/              # descriptive.py, regression.py, power.py, mediation.py, factorial.py
│
├── tests/
│   ├── unit/                    # columnTypeInferrer, chartTypeMapper, promptTemplates, responseValidator
│   ├── integration/             # AdvisorFlow
│   └── prompts/                 # Golden-path JSON fixtures
│
└── docs/
    ├── ARCHITECTURE.md          # System design, layers, data flow
    ├── PROMPT-DESIGN.md         # Prompt construction, output schema
    ├── DATA-VIZ-REFERENCE.md    # Chart taxonomy, encoding principles
    ├── CONTRIBUTING.md          # Contribution guidelines
    ├── STRUCTURE.md             # Directory structure reference
    └── ROUTES.md                # Routes and sitemap
```

---

## Core Data Flow

```
User Input
    │
    ├─ [1] Upload or paste dataset (CSV / JSON)
    ├─ [2] (Optional) Run pre-viz analysis (descriptive, regression, etc.)
    ├─ [3] Select visualization goal
    ├─ [4] Set parameters (audience, library, interactivity, accessibility)
    │
    ▼
PromptBuilder → promptTemplates.buildMessages()
    │
    ▼
llmService → POST /api/recommend (proxy) → Anthropic / OpenAI
    │
    ▼
RecommendationList (RecommendationCard, AlternativeOptions, DesignDecisionsPanel,
                   PitfallWarnings, CodeSnippet, FollowUpQuestions, ExportButton)
    │
    ▼
(Optional) Run post-viz analysis
```

---

## Getting Started

### Prerequisites

- **Node.js** 18+
- **npm** or yarn
- **(Optional)** R and Python 3 for analysis features

### Quick Start

```bash
# Clone the repo
git clone https://github.com/your-username/vizadvisor.git
cd vizadvisor

# Install dependencies
npm install

# Copy env and add your API key
cp .env.example .env
# Edit .env: set VITE_ANTHROPIC_API_KEY or VITE_OPENAI_API_KEY

# Option A: Frontend only (API key in client — dev only, not recommended)
npm run dev

# Option B: Full stack (recommended — API key on server)
cp server/.env.example server/.env
# Edit server/.env: set ANTHROPIC_API_KEY
npm run dev:full
# Opens http://localhost:5173
```

### One-Command Launch

```bash
./run.sh
```

Installs dependencies, starts Vite dev server + API proxy, waits for readiness, and opens `http://localhost:5173/advisor` in the default browser. On macOS this uses `open`; on Linux use `xdg-open` or run manually after the server starts.

### Production Build

```bash
npm run build
npm run preview
```

For production, run the Express server separately and serve the built assets (or use a reverse proxy). Set `VITE_API_PROXY_URL` to your production API URL.

---

## Environment Variables

### Client (`.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_LLM_PROVIDER` | `anthropic` or `openai` | `anthropic` |
| `VITE_ANTHROPIC_API_KEY` | Anthropic API key | — |
| `VITE_OPENAI_API_KEY` | OpenAI API key | — |
| `VITE_DEFAULT_MODEL` | Model name | `claude-sonnet-4-6` |
| `VITE_API_PROXY_URL` | Proxy URL for LLM + analysis | — (use `http://localhost:3001` with `dev:full`) |
| `VITE_ANALYSIS_TIMEOUT_MS` | Analysis request timeout | `60000` |
| `VITE_MAX_TOKENS` | LLM max tokens | `2048` |
| `VITE_REQUEST_TIMEOUT_MS` | LLM request timeout | `30000` |
| `VITE_APP_ENV` | App environment | `development` |
| `VITE_REPO_URL` | GitHub repo link in header | — |

### Server (`server/.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Anthropic API key (server-side) | — |
| `LLM_PROVIDER` | `anthropic` or `openai` | `anthropic` |
| `PORT` | Server port | `3001` |
| `ALLOWED_ORIGIN` | CORS origin | `http://localhost:5173` |
| `ANALYSIS_TIMEOUT_MS` | Analysis script timeout | `60000` |
| `R_PATH` | Path to Rscript | `Rscript` |
| `PYTHON_PATH` | Path to python3 | `python3` |

> **Production:** Route all API calls through the proxy so API keys are never exposed client-side. Set `VITE_API_PROXY_URL` and keep keys only in `server/.env`.

---

## Analysis Service (Optional)

The server runs R or Python scripts for statistical analysis. Data stays in the browser; only schema and rows are sent to the server.

### R Setup

```r
install.packages(c("jsonlite", "dplyr", "tidyr", "broom", "car", "pwr", "lavaan"), repos="https://cloud.r-project.org")
```

### Python Setup

```bash
pip install -r server/requirements.txt
```

### Analysis Types

| Type | Description |
|------|-------------|
| **Descriptive** | Summary stats, optional group-by |
| **Regression** | Linear regression / ANOVA |
| **Power** | Power analysis (u, v, f², power) |
| **Mediation** | X → M → Y mediation |
| **Factorial** | Factorial ANOVA (2–3 factors) |

---

## Tech Stack

| Layer | Choice |
|-------|--------|
| Framework | React 18 + Vite 6 |
| Styling | Tailwind CSS |
| State | React Context + useReducer |
| Routing | React Router v6 |
| LLM | Anthropic Claude / OpenAI (via proxy) |
| Data parsing | PapaParse |
| Code highlighting | Prism.js |
| Testing | Vitest, Testing Library |

---

## Routes

| Path | Description |
|------|-------------|
| `/` | Landing page |
| `/advisor` | Main tool — upload data, set goal, get recommendations |
| `/about` | What the tool does, data handling |

**API endpoints:** `POST /api/recommend` (LLM proxy), `POST /api/analyze` (R/Python analysis)

---

## Documentation

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) — System design, layers, data flow
- [PROMPT-DESIGN.md](docs/PROMPT-DESIGN.md) — Prompt construction, output schema
- [DATA-VIZ-REFERENCE.md](docs/DATA-VIZ-REFERENCE.md) — Chart taxonomy, encoding principles
- [STRUCTURE.md](docs/STRUCTURE.md) — Directory structure
- [ROUTES.md](docs/ROUTES.md) — Routes and sitemap
- [CONTRIBUTING.md](docs/CONTRIBUTING.md) — Contribution guidelines
- [CHANGELOG.md](CHANGELOG.md) — Version history

---

## Testing

```bash
npm test              # Run tests
npm run test:watch    # Watch mode
npm run test:ui       # Vitest UI
npm run test:coverage # Coverage report
npm run test:prompts  # Golden-path prompt fixtures
```

---

## Scripts

| Script | Description |
|--------|-------------|
| `npm run dev` | Vite dev server only |
| `npm run dev:full` | Vite + Express proxy (concurrent) |
| `npm run server` | Express proxy only |
| `npm run build` | Production build |
| `npm run preview` | Preview production build |
| `npm run lint` | ESLint |
| `npm run lint:fix` | ESLint with auto-fix |
| `npm run format` | Prettier format |

---

## License

Personal development project. See repository for details.

---

*Last updated: March 9, 2026*
