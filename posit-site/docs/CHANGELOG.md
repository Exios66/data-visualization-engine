# Changelog

All notable changes to VizAdvisor are documented here.

---

## [1.0.0] — February 2026

### Added

#### Core Features

- **LLM-powered visualization recommendations** — Upload CSV/JSON, select goal, receive structured recommendations (chart type, rationale, design decisions, code scaffold)
- **CSV/JSON upload** — Drag-and-drop or paste; PapaParse for parsing
- **Auto column type inference** — Quantitative, ordinal, nominal, temporal, geographic
- **Goal selector** — Compare, trend, distribution, correlation, part-of-whole, geospatial, network, ranking
- **Parameter panel** — Audience, chart library, interactivity, accessibility, extra notes
- **Streaming response** — Progressive display of LLM output
- **Export** — Copy to clipboard or download as Markdown/JSON

#### Analysis Features

- **Pre-visualization analysis** — Optional statistical analysis before getting recommendations
- **Post-visualization analysis** — Same analysis after recommendations
- **Analysis types** — Descriptive, regression, power, mediation, factorial
- **Dual engine support** — R or Python via server-side scripts
- **Analysis panel** — Engine selector, analysis type, config forms per type

#### UI & UX

- **Dark mode** — Theme toggle with persistent preference (localStorage)
- **GitHub link** — Header link to repository (`VITE_REPO_URL`)
- **Lazy-loaded pages** — Code splitting for HomePage, AdvisorPage, AboutPage
- **Responsive layout** — Tailwind-based responsive design

#### Infrastructure

- **Express proxy server** — `/api/recommend` (LLM), `/api/analyze` (R/Python)
- **Concurrent dev** — `npm run dev:full` runs Vite + server
- **run.sh** — One-command install, start, and open browser
- **Content Security Policy** — CSP in index.html
- **Manual chunking** — React, Prism, PapaParse in separate chunks

#### Output Components

- **RecommendationCard** — Primary recommendation, rationale, data mapping
- **AlternativeOptions** — Alternative chart options
- **DesignDecisionsPanel** — Color, scale, annotations, accessibility
- **PitfallWarnings** — Pitfalls and mitigations
- **FollowUpQuestions** — Suggested follow-up questions
- **CodeSnippet** — Syntax-highlighted code with copy button
- **MetaBadges** — Confidence, goal category

#### Session & State

- **Session history** — `useSessionHistory` for save/load (localStorage)
- **SessionContext** — Pre/post analysis state, dataset.rows for analysis

### Changed

- **AboutPage** — Clarified data handling during analysis
- **Prompt templates** — Integration of pre-analysis results when available
- **SessionContext** — Added `rows` to dataset for analysis; `preAnalysis`, `postAnalysis` state

### Security

- API keys routed through proxy in production
- CSP headers for XSS mitigation

---

## Pre-1.0 (Scaffold)

- Initial project scaffold (Vite + React)
- Core architecture (ARCHITECTURE.md, PROMPT-DESIGN.md, DATA-VIZ-REFERENCE.md)
- Basic components and services
- Unit tests (columnTypeInferrer, chartTypeMapper, promptTemplates, responseValidator)
- Integration test (AdvisorFlow)
