---
title: "System Architecture"
---

> **Document version:** 1.0  
> **Last updated:** February 2026  
> **Audience:** Contributors, maintainers, and developers extending the codebase

-----

## Table of Contents

1. [Project Overview](#1-project-overview)
1. [Architecture Philosophy](#2-architecture-philosophy)
1. [System Diagram](#3-system-diagram)
1. [Layer-by-Layer Breakdown](#4-layer-by-layer-breakdown)
- 4.1 [Presentation Layer](#41-presentation-layer)
- 4.2 [State & Context Layer](#42-state--context-layer)
- 4.3 [Business Logic Layer](#43-business-logic-layer)
- 4.4 [Service Layer](#44-service-layer)
- 4.5 [LLM Integration Layer](#45-llm-integration-layer)
1. [Data Flow — End to End](#5-data-flow--end-to-end)
1. [Component Architecture](#6-component-architecture)
1. [State Management Design](#7-state-management-design)
1. [LLM API Integration](#8-llm-api-integration)
1. [Data Parsing Pipeline](#9-data-parsing-pipeline)
1. [Security Model](#10-security-model)
1. [Performance Considerations](#11-performance-considerations)
1. [Error Handling Strategy](#12-error-handling-strategy)
1. [Extensibility & Future Architecture](#13-extensibility--future-architecture)
1. [Decision Log](#14-decision-log)

-----

## 1. Project Overview

VizAdvisor is a client-side React application that accepts a user’s dataset (via file upload or manual schema entry) and visualization goal, then queries a large language model to produce expert-level, context-aware data visualization recommendations. The LLM response is structured as a JSON object that drives a rich output UI including chart type rationale, design decision breakdowns, accessibility guidance, alternative options, pitfall warnings, and ready-to-use code scaffolds.

The application is intentionally **frontend-first**: the primary backend dependency is the LLM API. An optional Express proxy server provides `/api/recommend` (LLM) and `/api/analyze` (R/Python statistical analysis). The proxy is strongly recommended for production to protect API credentials.

-----

## 2. Architecture Philosophy

VizAdvisor is designed around five guiding architectural principles:

**Separation of concerns above all.** The prompt construction logic, the LLM communication, the data parsing, and the UI rendering are entirely decoupled modules. Swapping the LLM provider, changing the output format, or redesigning the UI should each require changes in exactly one layer.

**The LLM is a service, not a framework.** The application owns its domain logic (data schema inference, prompt assembly, output parsing). The LLM receives a fully formed, structured request and returns a fully formed, structured response. It does not drive application state.

**Progressive enhancement for data input.** Users with raw CSV files, users with just a description of their columns, and users with pre-analyzed schemas should all be able to use the tool. The data input pipeline handles all three gracefully.

**Fail loudly, recover gracefully.** LLM API errors, malformed JSON responses, parsing failures, and network timeouts all have explicit error states in the UI with actionable recovery paths. Silent failures are not acceptable.

**No lock-in.** The LLM provider, the charting library recommendations, and the frontend framework are all swappable. No architecture decision should create irreversible coupling to a vendor.

-----

## 3. System Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         BROWSER (CLIENT)                            │
│                                                                     │
│  ┌──────────────┐    ┌───────────────────────────────────────────┐  │
│  │   Pages /    │    │            SessionContext                 │  │
│  │   Routing    │◄───│  (dataset, goal, params, recommendations) │  │
│  └──────┬───────┘    └───────────────────────────────────────────┘  │
│         │                          ▲                                │
│         ▼                          │                                │
│  ┌─────────────────────────────────┴─────────────────────────────┐  │
│  │                     AdvisorPage.jsx                           │  │
│  │                                                               │  │
│  │   ┌──────────────────────┐    ┌──────────────────────────┐   │  │
│  │   │     INPUT PANEL      │    │      OUTPUT PANEL        │   │  │
│  │   │                      │    │                          │   │  │
│  │   │  DataUploader        │    │  RecommendationCard      │   │  │
│  │   │  DataPreview         │    │  AlternativeOptions      │   │  │
│  │   │  GoalSelector        │    │  DesignDecisions         │   │  │
│  │   │  ParameterPanel      │    │  PitfallWarnings         │   │  │
│  │   │  PromptBuilder  ─────┼────┼─►CodeSnippet             │   │  │
│  │   └──────────────────────┘    │  ExportButton            │   │  │
│  │                               └──────────────────────────┘   │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                          │                                          │
│              ┌───────────▼────────────┐                            │
│              │       useLLM.js        │                            │
│              │  (hook: state machine  │                            │
│              │   idle→loading→done    │                            │
│              │   or error)            │                            │
│              └───────────┬────────────┘                            │
│                          │                                          │
│              ┌───────────▼────────────┐                            │
│              │    llmService.js       │                            │
│              │  buildMessages()       │                            │
│              │  fetch() / stream()    │                            │
│              │  parseResponse()       │                            │
│              └───────────┬────────────┘                            │
│                          │                                          │
└──────────────────────────┼──────────────────────────────────────────┘
                           │  HTTPS
                           ▼
              ┌────────────────────────┐
              │   PROXY SERVER         │  ◄── Recommended for production
              │   (optional but        │       Protects API key
              │    recommended)        │       Rate limiting
              └────────────┬───────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   LLM API              │
              │   Anthropic /          │
              │   OpenAI-compatible    │
              └────────────────────────┘
```

-----

## 4. Layer-by-Layer Breakdown

### 4.1 Presentation Layer

**Location:** `src/components/`, `src/pages/`

The presentation layer is composed entirely of React functional components. It is responsible only for rendering state and dispatching user events upward. Components in this layer do not perform API calls, data parsing, or business logic. They receive data via props or context and emit callbacks.

Components are organized into four groups:

- **`layout/`** — structural chrome: Header, Footer, Sidebar. These components are session-unaware; they render the same regardless of application state.
- **`input/`** — the left panel of AdvisorPage. Each component maps to one section of the user’s request: data upload, schema preview, goal selection, and parameter configuration.
- **`output/`** — the right panel of AdvisorPage. Each component maps to one section of the LLM’s JSON response object.
- **`common/`** — shared, stateless primitives: Button, Spinner, Modal, Tooltip, ErrorBanner.

### 4.2 State & Context Layer

**Location:** `src/context/`

Application state is managed with React Context + `useReducer`. Two contexts are maintained:

**`SessionContext`** holds all mutable session data: the current dataset metadata, the assembled goal and parameters, the raw LLM response string, the parsed recommendation object, the loading state, and any error state. This is the single source of truth for one advising session.

**`SettingsContext`** holds user preferences that persist across sessions: preferred LLM model, preferred chart library, preferred language, verbosity level, and theme. Settings are persisted to `localStorage`.

### 4.3 Business Logic Layer

**Location:** `src/hooks/`, `src/utils/`

Custom hooks encapsulate the application’s stateful logic without coupling it to specific UI components:

- **`useLLM.js`** — manages the full lifecycle of an LLM request: idle → loading → streaming → complete → error. Exposes `{ recommendation, status, error, submit, reset }`.
- **`useDataParser.js`** — manages file ingestion and schema inference. Exposes `{ schema, sampleRows, rowCount, parseFile, parseText, reset }`.
- **`useSessionHistory.js`** — manages reading and writing past sessions from `localStorage`.

Pure utility functions in `src/utils/` contain no React dependencies and are fully unit-testable:

- **`columnTypeInferrer.js`** — heuristic logic to infer `quantitative | ordinal | nominal | temporal | geographic | boolean` from a column’s values.
- **`chartTypeMapper.js`** — maps a (goal category × data type profile) tuple to a ranked list of candidate chart types. Used for pre-filtering and UI hints; the LLM makes the final call.
- **`formatters.js`** — display formatting for numbers, dates, file sizes, and cardinalities.

### 4.4 Service Layer

**Location:** `src/services/`

The service layer contains all code that communicates with external systems or performs heavy data transformation. Services are plain JavaScript modules, not React hooks, making them independently testable and importable outside of React.

- **`llmService.js`** — owns the HTTP communication with the LLM API. Exports `sendRequest(messages, options)` and `streamRequest(messages, options, onChunk)`. Handles retries, timeout, and response validation.
- **`dataService.js`** — owns CSV and JSON parsing logic, wrapping PapaParse. Handles encoding detection, delimiter inference, header normalization, and type coercion.
- **`promptTemplates.js`** — owns all prompt construction. Exports `buildMessages(context)`, `buildFollowUpMessages(history, reply, followUp)`, and the `SYSTEM_PROMPT` constant.

### 4.5 LLM Integration Layer

**Location:** `src/services/llmService.js`, `src/services/promptTemplates.js`

The LLM integration layer is designed around two contracts:

**Input contract:** `llmService.sendRequest()` accepts a `{ system, messages }` object produced by `promptTemplates.buildMessages()`. It knows nothing about datasets, goals, or visualization concepts — it only knows how to make an authenticated HTTP request to the configured provider endpoint.

**Output contract:** The LLM is instructed (via system prompt) to return a single JSON object conforming to the recommendation schema. `llmService.js` validates the response is parseable JSON before returning it. If it is not, the error propagates to `useLLM.js` which surfaces it in the UI.

### 4.6 Analysis Service Layer

**Location:** `src/services/analysisService.js`, `server/analysis/`

An optional server-side analysis layer runs R or Python scripts for statistical analysis. The client sends schema + row data to `POST /api/analyze`; the server validates the request, spawns the appropriate script (R or Python), passes JSON via stdin, and returns parsed JSON stdout. Analysis types include descriptive statistics, regression, power analysis, mediation, and factorial ANOVA. Pre-visualization analysis can inform the LLM prompt; post-visualization analysis runs after recommendations. Data is sent only when the user explicitly runs analysis; it is never stored server-side.

-----

## 5. Data Flow — End to End

The following describes a complete user journey from file upload to rendered recommendation.

```
1. User uploads a CSV file
       │
       ▼
2. DataUploader.jsx calls useDataParser.parseFile(file)
       │
       ▼
3. dataService.js:
   - PapaParse reads the file
   - Detects delimiter, encoding, headers
   - Returns raw rows + header array
       │
       ▼
4. columnTypeInferrer.js:
   - Samples each column's values
   - Applies heuristics to infer data type
   - Estimates cardinality, nullability, range
   - Returns schema array
       │
       ▼
5. SessionContext updated:
   { dataset: { schema, sampleRows, rowCount } }
       │
       ▼
6. DataPreview.jsx renders schema table
   User reviews, corrects type overrides if needed
       │
       ▼
7. User selects goal from GoalSelector.jsx
   User sets parameters in ParameterPanel.jsx
   SessionContext updated: { goal, parameters }
       │
       ▼
8. User clicks "Get Recommendations"
   useLLM.submit() is called
       │
       ▼
9. promptTemplates.buildMessages(sessionContext):
   - Injects schema, sample rows, goal, parameters
     into the structured user turn
   - Returns { system: SYSTEM_PROMPT, messages: [...] }
       │
       ▼
10. llmService.sendRequest(messages):
    - Authenticates request
    - POST to /v1/messages (or proxy endpoint)
    - Awaits response (or streams chunks)
       │
       ▼
11. LLM returns JSON string
       │
       ▼
12. llmService.parseResponse():
    - JSON.parse() the content
    - Validate required fields are present
    - Return structured recommendation object
       │
       ▼
13. SessionContext updated:
    { recommendation: <parsed object>, status: 'complete' }
       │
       ▼
14. Output panel re-renders:
    RecommendationCard    ← primary_recommendation
    AlternativeOptions    ← alternative_options
    DesignDecisions       ← design_decisions, accessibility, interactivity
    PitfallWarnings       ← pitfalls
    CodeSnippet           ← code_scaffold.snippet
    FollowUpQuestions     ← follow_up_questions
```

-----

## 6. Component Architecture

### AdvisorPage Layout

```
AdvisorPage.jsx
├── InputPanel.jsx  (left column)
│   ├── DataUploader.jsx
│   │   └── accepts: file drop or paste → calls useDataParser
│   ├── DataPreview.jsx
│   │   └── renders schema table, allows type override
│   ├── GoalSelector.jsx
│   │   └── dropdown of GOAL_CATEGORIES + free-text description
│   ├── ParameterPanel.jsx
│   │   ├── AudienceInput
│   │   ├── LibrarySelector  (from SUPPORTED_LIBRARIES constant)
│   │   ├── InteractivityToggle
│   │   ├── AccessibilityOptions
│   │   └── ExtraNotesTextarea
│   └── SubmitButton.jsx
│       └── disabled until dataset + goal are both present
│
└── OutputPanel.jsx  (right column)
    ├── LoadingState.jsx     (shown while status === 'loading')
    ├── ErrorState.jsx       (shown when status === 'error')
    └── RecommendationView.jsx  (shown when status === 'complete')
        ├── MetaBadges.jsx         ← meta.confidence, meta.goal_category
        ├── RecommendationCard.jsx ← primary_recommendation
        │   ├── ChartTypeHeader
        │   ├── RationaleText
        │   └── DataMappingTable
        ├── DesignDecisionsPanel.jsx
        │   ├── ColorPaletteDisplay
        │   ├── ScaleInfo
        │   ├── AnnotationGuidance
        │   └── AccessibilityChecklist
        ├── AlternativeOptions.jsx
        │   └── AlternativeCard × 2
        ├── PitfallWarnings.jsx
        │   └── PitfallItem × n
        ├── CodeSnippet.jsx
        │   ├── LibraryBadge
        │   ├── SyntaxHighlighter (Prism.js)
        │   └── CopyButton
        ├── FollowUpQuestions.jsx
        └── ExportButton.jsx
```

-----

## 7. State Management Design

### Why Context + useReducer (not Redux or Zustand)

VizAdvisor has a single primary data flow (user input → LLM → output) with no complex cross-cutting state mutations. The total state shape is shallow and predictable. React Context with `useReducer` provides full type-safety, zero dependencies, and sufficient performance for this access pattern. If the application grows to include multi-session management, collaborative features, or complex derived state, migrating to Zustand is the recommended next step.

### SessionContext State Shape

```javascript
{
  // Data input
  dataset: {
    rawFile:     File | null,
    rowCount:    number | null,
    schema:      Array<ColumnSchema> | null,
    sampleRows:  Array<Object> | null,
    parseError:  string | null,
  },

  // User-defined goal & parameters
  goal: {
    description:     string,
    category:        string | null,
    primaryQuestion: string | null,
  },
  parameters: {
    audience:        string | null,
    library:         string | null,
    language:        string,
    interactivity:   string | null,
    accessibility:   string | null,
    extraNotes:      string | null,
  },

  // LLM interaction
  status:         'idle' | 'loading' | 'streaming' | 'complete' | 'error',
  rawResponse:    string | null,
  recommendation: RecommendationSchema | null,
  llmError:       string | null,

  // Multi-turn
  conversationHistory: Array<{ role: string, content: string }>,
}
```

### Reducer Actions

```
SET_DATASET         — update dataset after parsing
SET_SCHEMA_OVERRIDE — user manually corrects a column type
SET_GOAL            — update goal fields
SET_PARAMETERS      — update any parameter field
SUBMIT_REQUEST      — set status to 'loading', clear prior recommendation
STREAM_CHUNK        — append streaming token to rawResponse
REQUEST_COMPLETE    — set status to 'complete', set recommendation
REQUEST_ERROR       — set status to 'error', set llmError
APPEND_HISTORY      — add a turn to conversationHistory
RESET_SESSION       — return to initial state
```

-----

## 8. LLM API Integration

### Provider Configuration

The LLM provider is configured via environment variables. The service layer reads `VITE_LLM_PROVIDER` and selects the appropriate request format and endpoint:

```
anthropic → POST https://api.anthropic.com/v1/messages
            Headers: x-api-key, anthropic-version, content-type
            Body:    { model, max_tokens, system, messages }

openai    → POST https://api.openai.com/v1/chat/completions
            Headers: Authorization: Bearer, content-type
            Body:    { model, messages: [{ role: 'system', content }, ...] }
```

### Streaming

Streaming is strongly recommended for this application because LLM responses can be 800–1500 tokens. Without streaming, the user sees nothing for 5–15 seconds. With streaming, tokens appear within 500ms and the output panel progressively renders.

The streaming implementation uses the Fetch API with `ReadableStream`. As chunks arrive, the `STREAM_CHUNK` action is dispatched. The output panel renders the partial `rawResponse` string as pre-formatted text until `REQUEST_COMPLETE` fires, at which point `rawResponse` is parsed as JSON and the structured output components render.

### Response Validation

After the full response is received, `llmService.parseResponse()` applies the following validation steps before returning:

1. Attempt `JSON.parse()`. If it fails, attempt to extract a JSON object from the string using a regex (handles cases where the model wraps output in markdown fences despite instructions).
1. Verify `meta`, `primary_recommendation`, `alternative_options`, `pitfalls`, and `code_scaffold` keys are present.
1. Verify `primary_recommendation.chart_type` and `primary_recommendation.rationale` are non-empty strings.
1. If validation fails at any step, throw a structured `LLMResponseError` with the raw response attached for debugging.

### Retry Logic

`llmService.sendRequest()` implements exponential backoff for 429 (rate limit) and 5xx errors:

```
Attempt 1: immediate
Attempt 2: 1 second delay
Attempt 3: 2 second delay
Attempt 4: 4 second delay (final)
```

Network errors and 4xx errors (except 429) do not retry.

-----

## 9. Data Parsing Pipeline

### Supported Input Formats

|Format             |Entry Point           |Parser           |
|-------------------|----------------------|-----------------|
|CSV file upload    |DataUploader drag-drop|PapaParse        |
|CSV text paste     |DataUploader textarea |PapaParse        |
|JSON file upload   |DataUploader drag-drop|native JSON.parse|
|JSON text paste    |DataUploader textarea |native JSON.parse|
|Manual schema entry|SchemaBuilder (future)|n/a              |

### Column Type Inference

`columnTypeInferrer.js` applies a heuristic cascade to each column. It samples up to 100 values (or all values if fewer) and applies tests in priority order:

```
1. Boolean test     → if all non-null values are in {true, false, 0, 1, "yes", "no"}
2. Temporal test    → if ≥ 80% of values parse as valid dates (ISO, US, EU, Unix)
3. Geographic test  → if column name matches known geo identifiers OR values match
                       country codes, US state codes, lat/lng ranges
4. Quantitative     → if ≥ 90% of non-null values are parseable as finite numbers
5. Ordinal test     → if cardinality ≤ 12 AND values suggest ordered categories
                       (contains tokens like: low/med/high, 1st/2nd/3rd, etc.)
6. Nominal          → default fallback
```

Users can override inferred types via the DataPreview UI. Type overrides are stored in `SessionContext` and passed through to the prompt so the LLM receives the corrected schema.

### Large File Handling

Files larger than 5MB trigger a warning. Files larger than 20MB are rejected with a message advising the user to summarize or sample their data before uploading. For files between 5–20MB, PapaParse is run in worker mode to avoid blocking the main thread, and only the first 1,000 rows are used for schema inference and sample generation.

-----

## 10. Security Model

### API Key Exposure

**Development:** API keys are stored in `.env` and accessed via `import.meta.env`. They are bundled into the client and therefore visible in browser DevTools. This is acceptable only for local development.

**Production:** API calls must be routed through a proxy server (Node.js/Express, Cloudflare Worker, Vercel Edge Function, etc.) that injects the API key server-side. The frontend sends requests to `/api/recommend` and the proxy forwards them to the LLM provider. The API key is never in the client bundle.

### Data Privacy

User-uploaded data is processed entirely in the browser. It is never stored server-side. Only the schema, sample rows (first 3–5 rows), and row count are sent to the LLM API. Raw data files stay in memory only for the duration of the parsing step.

Users should be warned in the UI if their dataset contains PII column names (names, emails, SSNs, phone numbers, dates of birth) so they can anonymize before uploading. Column name detection for common PII patterns can be implemented in `columnTypeInferrer.js`.

### Content Security Policy

The application should implement a strict CSP header blocking inline scripts and restricting `connect-src` to the proxy endpoint only.

-----

## 11. Performance Considerations

### Token Budget Management

LLM API calls are priced per token. The assembled user prompt can grow large when sample data is verbose. `promptTemplates.js` enforces the following limits before sending:

- Schema: maximum 50 columns (truncated with a note if exceeded)
- Sample rows: maximum 5 rows
- Each sample row: values truncated to 100 characters
- Extra notes: maximum 500 characters

### Rendering Large Recommendations

The code scaffold snippet can be 100–200 lines. Prism.js syntax highlighting is applied lazily (not during streaming) to avoid re-rendering cost on every token. The recommendation object is only parsed and rendered once, after the full response is received.

### Bundle Size

Target total bundle size: < 300KB gzipped. Prism.js language packs should be loaded only for the language in the current `code_scaffold.language` field (dynamic import). PapaParse should be loaded lazily, only when the user triggers file upload.

-----

## 12. Error Handling Strategy

Every failure mode has a defined behavior:

|Error Type              |Detection               |User-Facing Behavior                  |Recovery               |
|------------------------|------------------------|--------------------------------------|-----------------------|
|File parse error        |PapaParse error callback|Inline error under uploader           |Dismiss and try again  |
|Network error           |fetch() rejection       |ErrorBanner with retry button         |Retry button re-submits|
|API auth error (401/403)|HTTP status             |ErrorBanner: “API key issue”          |Link to settings       |
|Rate limit (429)        |HTTP status             |ErrorBanner: “Rate limited — retrying”|Auto-retry with backoff|
|LLM JSON parse error    |JSON.parse() failure    |ErrorBanner with raw response         |Copy raw / retry       |
|LLM missing fields      |Validation failure      |ErrorBanner with field list           |Retry                  |
|Response timeout (30s)  |AbortController         |ErrorBanner: “Request timed out”      |Retry                  |
|Empty response          |content.length === 0    |ErrorBanner                           |Retry                  |

All errors are logged to `console.error` in development. In production, integrate with your error monitoring service (Sentry, Datadog, etc.) via a thin wrapper in `llmService.js`.

-----

## 13. Extensibility & Future Architecture

### Adding a New LLM Provider

1. Add provider config to `SUPPORTED_PROVIDERS` in `llmService.js`
1. Implement `formatRequest(provider, messages)` for the new API shape
1. Add the provider to `.env.example` and the settings UI
1. No changes needed in any other module

### Adding Multi-Turn Refinement

The conversation history array in `SessionContext` and the `buildFollowUpMessages()` export in `promptTemplates.js` are pre-built for this. The UI needs a follow-up input field and the `APPEND_HISTORY` action needs to be wired to the submit flow.

### Adding a Backend / Persistence Layer

If sessions need to be saved server-side, the `SessionContext` state shape maps cleanly to a document schema. Each session object can be serialized and posted to a REST endpoint after a recommendation is received. No changes to the LLM integration layer are needed.

### Adding a Chart Preview

A future enhancement could render a live preview of the recommended chart using the user’s actual data. This would require wiring `recommendation.data_mapping` to a charting library in an `OutputChartPreview` component. The schema is already designed to make this mapping explicit.

-----

## 14. Decision Log

|Decision          |Chosen Approach      |Alternatives Considered       |Rationale                                                     |
|------------------|---------------------|------------------------------|--------------------------------------------------------------|
|Frontend framework|React + Vite         |Next.js, Svelte               |SSR not needed; Vite DX superior for pure SPA                 |
|State management  |Context + useReducer |Redux, Zustand, Jotai         |Sufficient for current complexity; zero deps                  |
|LLM output format |JSON (strict schema) |Markdown                      |Enables reliable component-driven rendering                   |
|Streaming         |Yes, default on      |Request/response only         |Critical for perceived performance at 800–1500 token responses|
|Data sent to LLM  |Schema + samples only|Full dataset                  |Privacy; token cost; LLM doesn’t need all rows to advise      |
|CSS approach      |Tailwind CSS         |CSS Modules, styled-components|Fastest iteration; no runtime cost                            |
|Testing framework |Vitest               |Jest                          |Native Vite integration; faster cold start                    |
|Code highlighting |Prism.js             |Shiki, highlight.js           |Lighter weight; good React ecosystem                          |
|File size limit   |20MB hard cap        |Unlimited                     |Protects main thread; beyond this, users need pre-sampling    |
