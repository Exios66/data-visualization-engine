---
title: "Directory Structure"
---

> Reference for navigating the codebase. Last updated: February 2026

---

## Root

| File | Purpose |
|------|---------|
| `README.md` | Project overview, setup, features |
| `run.sh` | One-command dev launcher |
| `package.json` | Dependencies, scripts |
| `vite.config.js` | Vite config, chunking, test setup |
| `index.html` | HTML entry, CSP |
| `.env.example` | Client env template |
| `mermaid-map.md` | Mermaid flowchart of repo structure |
| `IMPLEMENTATION-PLAN.md` | Phased build specification |
| `CHANGELOG.md` | Version history |

---

## `src/`

### Entry & App

| File | Purpose |
|------|---------|
| `main.jsx` | React root, StrictMode |
| `App.jsx` | Providers, routing, theme wrapper, lazy-loaded pages |

### `src/pages/`

| File | Route | Purpose |
|------|-------|---------|
| `HomePage.jsx` | `/` | Landing, intro, CTA to Advisor |
| `AdvisorPage.jsx` | `/advisor` | Main tool: input + output panels |
| `AboutPage.jsx` | `/about` | What the tool does, data handling |

### `src/components/`

#### `layout/`

| File | Purpose |
|------|---------|
| `Header.jsx` | Logo, nav (Advisor, About), theme toggle, GitHub link |
| `Footer.jsx` | Footer content |
| `Sidebar.jsx` | Optional history / saved sessions |

#### `input/`

| File | Purpose |
|------|---------|
| `DataUploader.jsx` | CSV/JSON file drop or paste |
| `DataPreview.jsx` | Schema table, type override |
| `GoalSelector.jsx` | Goal category dropdown + description |
| `ParameterPanel.jsx` | Audience, library, interactivity, accessibility, notes |
| `PromptBuilder.jsx` | Submit / Reset buttons, readiness state |

#### `output/`

| File | Purpose |
|------|---------|
| `RecommendationList.jsx` | Container: loading, error, or full recommendation view |
| `RecommendationCard.jsx` | Primary chart type, rationale, data mapping |
| `AlternativeOptions.jsx` | Alternative chart options |
| `DesignDecisionsPanel.jsx` | Color, scale, annotations, accessibility |
| `PitfallWarnings.jsx` | Pitfalls and mitigations |
| `CodeSnippet.jsx` | Syntax-highlighted code with copy |
| `FollowUpQuestions.jsx` | Suggested follow-up questions |
| `ExportButton.jsx` | Copy / download as Markdown or JSON |
| `MetaBadges.jsx` | Confidence, goal category badges |

#### `analysis/`

| File | Purpose |
|------|---------|
| `AnalysisPanel.jsx` | Engine (R/Python), analysis type, config form, Run button |
| `AnalysisResults.jsx` | Renders analysis output |

#### `common/`

| File | Purpose |
|------|---------|
| `Button.jsx` | Primary/secondary/ghost, loading state |
| `Spinner.jsx` | Loading indicator |
| `Modal.jsx` | Modal dialog |
| `Tooltip.jsx` | Tooltip |
| `ErrorBanner.jsx` | Error display with retry |
| `CopyButton.jsx` | Copy-to-clipboard |
| `Badge.jsx` | Badge/chip |

### `src/hooks/`

| File | Purpose |
|------|---------|
| `useLLM.js` | LLM request lifecycle: submit, status, recommendation, error |
| `useDataParser.js` | File parsing, schema inference |
| `useSessionHistory.js` | Save/load sessions from localStorage |
| `useAnalysis.js` | Pre/post analysis: run, status, results, error |

### `src/services/`

| File | Purpose |
|------|---------|
| `llmService.js` | LLM API calls, streaming, response parsing |
| `dataService.js` | CSV/JSON parsing via PapaParse |
| `promptTemplates.js` | System prompt, buildMessages, buildFollowUpMessages |
| `analysisService.js` | POST /api/analyze client |

### `src/context/`

| File | Purpose |
|------|---------|
| `SessionContext.jsx` | Dataset, goal, parameters, recommendation, analysis state |
| `SettingsContext.jsx` | Model, library, theme, verbosity (persisted) |

### `src/utils/`

| File | Purpose |
|------|---------|
| `columnTypeInferrer.js` | Infer quantitative, ordinal, nominal, temporal, geographic |
| `chartTypeMapper.js` | Map goal + data types → candidate chart types |
| `formatters.js` | Number, date, file size formatting |
| `responseValidator.js` | Validate LLM JSON response schema |

### `src/styles/`

| File | Purpose |
|------|---------|
| `global.css` | Tailwind imports, base styles |
| `theme.js` | Design tokens (colors, spacing) |

---

## `server/`

| File | Purpose |
|------|---------|
| `index.js` | Express app: CORS, /api/recommend, /api/analyze |
| `.env.example` | Server env template |
| `requirements.txt` | Python analysis dependencies |

### `server/analysis/`

| File | Purpose |
|------|---------|
| `runner.js` | Validate request, spawn R/Python, parse JSON stdout |
| `README.md` | R/Python setup, endpoint docs |

#### `server/analysis/r/`

| File | Purpose |
|------|---------|
| `descriptive.R` | Descriptive statistics |
| `regression.R` | Linear regression / ANOVA |
| `power.R` | Power analysis |
| `mediation.R` | Mediation analysis |
| `factorial.R` | Factorial ANOVA |

#### `server/analysis/python/`

| File | Purpose |
|------|---------|
| `descriptive.py` | Descriptive statistics |
| `regression.py` | Linear regression / ANOVA |
| `power.py` | Power analysis |
| `mediation.py` | Mediation analysis |
| `factorial.py` | Factorial ANOVA |

---

## `tests/`

| Path | Purpose |
|------|---------|
| `setup.js` | Vitest setup, jsdom |
| `unit/` | Unit tests for utils, services |
| `integration/` | AdvisorFlow integration test |
| `prompts/` | Golden-path JSON fixtures |

---

## `docs/`

| File | Purpose |
|------|---------|
| `ARCHITECTURE.md` | System design, layers, data flow |
| `PROMPT-DESIGN.md` | Prompt construction, output schema |
| `DATA-VIZ-REFERENCE.md` | Chart taxonomy, encoding principles |
| `CONTRIBUTING.md` | Contribution guidelines |
| `STRUCTURE.md` | This file |
| `ROUTES.md` | Routes and sitemap |
