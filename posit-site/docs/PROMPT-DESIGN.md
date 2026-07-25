---
title: "Prompt Design"
---

> **Document version:** 1.0  
> **Last updated:** February 2026  
> **Audience:** Developers modifying prompt logic, product owners evaluating LLM behavior, contributors adding new goal types or parameters

-----

## Table of Contents

1. [Overview & Philosophy](#1-overview--philosophy)
1. [The Two-Prompt Structure](#2-the-two-prompt-structure)
1. [System Prompt Design](#3-system-prompt-design)
- 3.1 [Role Framing](#31-role-framing)
- 3.2 [Reasoning Methodology](#32-reasoning-methodology)
- 3.3 [Output Contract](#33-output-contract)
- 3.4 [Hard Constraints](#34-hard-constraints)
- 3.5 [Tone Calibration](#35-tone-calibration)
1. [User Prompt Design](#4-user-prompt-design)
- 4.1 [Dataset Block](#41-dataset-block)
- 4.2 [Goal Block](#42-goal-block)
- 4.3 [Constraints Block](#43-constraints-block)
1. [Output Schema Reference](#5-output-schema-reference)
1. [Prompt Engineering Principles Applied](#6-prompt-engineering-principles-applied)
1. [Token Budget & Cost Management](#7-token-budget--cost-management)
1. [Multi-Turn Conversation Design](#8-multi-turn-conversation-design)
1. [Failure Modes & Mitigations](#9-failure-modes--mitigations)
1. [Testing & Evaluating Prompt Quality](#10-testing--evaluating-prompt-quality)
1. [Versioning & Change Management](#11-versioning--change-management)
1. [Prompt Iteration Roadmap](#12-prompt-iteration-roadmap)

-----

## 1. Overview & Philosophy

The prompt is the most critical engineering artifact in VizAdvisor. It is the specification the LLM receives, the contract it must fulfill, and the primary lever for improving recommendation quality. A poorly designed prompt produces generic, un-trustworthy, or unparseable output regardless of how good the underlying model is.

VizAdvisor’s prompt design follows three core principles:

**Specificity over generality.** The LLM must be given enough context to produce recommendations that are specific to the user’s actual data. Generic advice (“use a bar chart for comparisons”) is a failure mode, not a success. The prompt is designed so that two users with different datasets and different goals always receive meaningfully different responses.

**Structure constrains behavior.** The LLM is instructed to return a strict JSON schema, not free-form markdown. This is a deliberate choice that forces the model to commit to named fields, prevents discursive padding, and enables reliable programmatic rendering. Every field in the schema has a specific UI component consuming it.

**The system prompt owns the expertise; the user prompt owns the context.** The system prompt defines who the model is, how it reasons, and what it may and may not say. The user prompt injects session-specific data. These two responsibilities must never bleed into each other — the system prompt must not contain data-specific instructions, and the user prompt must not redefine the model’s role or reasoning process.

-----

## 2. The Two-Prompt Structure

VizAdvisor uses the standard system + user message structure supported by all major LLM APIs.

```
API Request
├── system:   SYSTEM_PROMPT          (static per deployment)
└── messages:
    ├── { role: "user",      content: buildUserPrompt(context) }
    │                                  (dynamic per session)
    │
    │   [ multi-turn sessions only ]
    ├── { role: "assistant", content: "<prior JSON response>" }
    └── { role: "user",      content: "<follow-up question>" }
```

The system prompt is loaded once per session and does not change. The user prompt is assembled fresh for every submission from the current `SessionContext`. In multi-turn sessions, the full prior conversation history is prepended to preserve context.

### Why not a single combined prompt?

Single-prompt designs (stuffing everything into the user turn) produce less consistent behavior across models. The `system` field in modern LLM APIs is given special weight by the model’s RLHF training — it is treated as configuration and instruction, not as conversational input. Using it correctly produces more reliable adherence to output format requirements and persona constraints.

-----

## 3. System Prompt Design

### 3.1 Role Framing

The system prompt opens by establishing the model’s identity, name, and domain expertise. This is not cosmetic — role framing measurably improves domain-appropriate behavior.

```
You are VizAdvisor, a world-class senior data visualization consultant
with deep expertise across the full spectrum of data communication,
visual encoding theory, and applied charting implementation.
```

The framing is followed immediately by a citation of the canonical literature the model is expected to draw from. This serves two purposes: it activates the model’s knowledge of specific frameworks (Munzner’s What-Why-How, Tufte’s data-ink ratio, Cairo’s truthfulness principle), and it provides a vocabulary that the model uses consistently in its rationale output.

**Authors cited and their primary contribution to the prompt’s reasoning:**

|Author        |Framework / Concept                       |Applied In                    |
|--------------|------------------------------------------|------------------------------|
|Edward Tufte  |Data-ink ratio, chartjunk, small multiples|Design decisions, pitfalls    |
|Tamara Munzner|What-Why-How, channel effectiveness       |Stage 2 task abstraction      |
|Alberto Cairo |Truthfulness, functionality, beauty       |Rationale framing             |
|Stephen Few   |Perceptual efficiency, dashboard design   |Output panel guidance         |
|Colin Ware    |Pre-attentive attributes, visual memory   |Color and encoding choices    |
|Claus Wilke   |Scientific figure design                  |Annotation and scale decisions|

The framing closes with a statement of the model’s primary responsibility: to explain *why* before recommending *what*. This is critical — without this instruction, models tend to lead with chart type names rather than reasoning.

### 3.2 Reasoning Methodology

The system prompt defines a four-stage reasoning process that the model must complete before producing output. The instruction to do this silently (“do not show this internal work in your output unless explicitly asked”) is essential — without it, models include verbose stage-by-stage commentary in the output, which clutters the JSON and increases token cost.

**Stage 1 — Data Analysis** instructs the model to interrogate the dataset metadata before making any assumptions. This prevents the common failure mode of ignoring provided schema information and producing generic recommendations.

**Stage 2 — Task Abstraction** applies Munzner’s formal framework to translate the user’s natural language goal into a structured task specification. This is the most important stage. It forces the model to distinguish between “compare” tasks (which favor position encoding) and “correlation” tasks (which may favor scatter plots), rather than collapsing all questions into the first chart type that comes to mind.

**Stage 3 — Constraint Integration** ensures every user-specified parameter affects the output. Without explicit instruction to integrate constraints, models routinely ignore parameters like accessibility requirements or audience type when they do not obviously contradict the primary recommendation.

**Stage 4 — Candidate Evaluation** requires the model to generate and score multiple options before committing to one. The five scoring criteria map directly to well-established visualization selection heuristics and force the model to justify its primary recommendation comparatively, not in isolation.

### 3.3 Output Contract

The output contract is the most precisely specified section of the system prompt. It defines the exact JSON schema the model must return, field by field, with inline documentation of required content for each field.

Key design decisions in the contract:

**Every field has a content specification, not just a type.** Saying `"rationale": string` is insufficient — it produces one-sentence rationale fields. The prompt specifies: `"rationale": "<3–5 sentences explaining WHY this chart type is the best match. Reference data properties, task type, and perceptual principles. Be specific."` This is what produces substantive rationale text.

**The contract is presented inside a code block with backtick escaping.** This signals to the model that the schema is inviolable specification, not a conversational example. It also prevents the model from treating schema field names as prose to be varied.

**The instruction “Do not wrap it in markdown fences” is explicit.** Without this, models frequently return ````json` blocks even when instructed to return JSON. This breaks `JSON.parse()`. The instruction must be present.

**Optional vs. required fields are documented inline.** Required fields use language like “MUST be present.” Optional fields use “should be included when you have meaningful content.” This calibration prevents the model from padding optional fields with placeholder content.

### 3.4 Hard Constraints

The ten hard constraints are the most impactful lines in the entire system prompt. They encode the most common and costly visualization errors as absolute rules the model cannot override through reasoning.

Each constraint is formatted as a direct prohibition (“Never recommend…”, “Always flag…”) rather than a guideline (“Consider avoiding…”). The distinction matters: soft guidelines are routinely overridden when the model finds a plausible justification. Hard prohibitions are not.

**Constraint design rationale:**

|Constraint                        |Why it exists                                                                                |Without it                                                                                                |
|----------------------------------|---------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|
|No pie charts for > 5 categories  |Angle comparison is perceptually inaccurate; bar charts are strictly superior for > 5 slices |Models frequently suggest pie charts for any part-of-whole task regardless of category count              |
|Flag dual-axis charts             |Dual axes are consistently misread by viewers; two separate charts are almost always clearer |Models suggest dual-axis charts whenever two series with different scales appear                          |
|Zero baseline default             |Truncated axes systematically mislead; the burden of justification should be on the exception|Models omit zero baseline warnings for log-scale recommendations                                          |
|No rainbow/jet color              |Rainbow scales are perceptually non-monotonic and inaccessible to color-blind viewers        |Models default to rainbow/jet for heatmaps without accessibility flags                                    |
|No 3D charts                      |3D charts introduce perspective distortion that makes accurate value reading impossible      |Models suggest 3D charts for “impressive” executive presentations                                         |
|Overplotting flag                 |Scatter plots with thousands of points are unreadable without mitigation                     |Models never volunteer this warning without explicit instruction                                          |
|Use real column names             |Code scaffolds with placeholder names cannot be copy-pasted                                  |Models default to generic variable names when column names require camelCase conversion                   |
|Redundant encoding for a11y       |Color alone is never sufficient for accessibility                                            |Models satisfy `color_blind_safe: true` with palette swaps but no encoding redundancy                     |
|Low confidence for ambiguous goals|Prevents confident-sounding but unreliable recommendations                                   |Models produce confident output even with insufficient information                                        |
|No hallucinated data values       |Models occasionally invent plausible-sounding statistics                                     |Without this constraint, sample statistics appear in rationale that are not derived from the provided data|

### 3.5 Tone Calibration

The tone instruction is the final section of the system prompt. It governs how the model writes the rationale fields — the only free-text output the user reads directly.

The key instruction is audience calibration based on the *user’s* sophistication, not the *chart audience’s* sophistication. These are different: a data scientist building a chart for executives needs technical implementation guidance, not a simplified explanation of what a bar chart is. A business analyst building a chart for their own use needs clear guidance without assuming Python familiarity.

The prohibition on generic advice (“Every recommendation must be specific to the user’s data. Generic advice is a failure mode.”) is one of the highest-leverage lines in the prompt. It creates a verifiable quality criterion for evaluating outputs.

-----

## 4. User Prompt Design

The user prompt is assembled by `promptTemplates.buildUserPrompt(context)`. It is a structured plaintext document, not a conversational message. It is organized into three clearly labeled blocks.

### 4.1 Dataset Block

```
SESSION ID: <id>

DATASET METADATA

TOTAL ROWS: <n>
SCHEMA (column name | inferred type | additional info):
  - "column_name" | type: quantitative | range: 0–10,000
  - "column_name" | type: nominal | cardinality: 12 | has nulls
  ...

SAMPLE ROWS (first 3):
[{ "col": val, ... }, ...]
```

**Design decisions:**

The schema is presented as a labeled list, not a JSON object. Labeled lists are easier for models to parse and reference than nested JSON — the column name is immediately readable, and all metadata for that column is on one line.

The sample rows are presented as JSON because they are structured data and JSON is the natural representation. The limit of 3–5 rows is sufficient for the model to understand value formats, nullability, and data quality without contributing significant token cost.

The `range` field is computed during parsing and is critical for scale recommendations. A column with range 0–100 warrants a linear scale; a column with range 0.001–1,000,000 warrants a log scale. Without this information, the model defaults to linear scales universally.

### 4.2 Goal Block

```
VISUALIZATION GOAL

The user wants to: "<free-text description>"

Goal category (user-selected): <category>
Primary question this chart must answer: "<question>"
```

The primary question field is optional but high-value when provided. It is the most direct specification of what the chart must communicate. When a user writes “Show sales over time by region,” the primary question “Which region is growing fastest in Q4?” transforms the recommendation from a generic multi-line chart into a specific small-multiples or highlighted-series design.

The goal category is provided by `GoalSelector.jsx` to give the model a structured hint, but the system prompt instructs the model to treat it as a starting point for analysis, not a final answer. This allows the model to correctly identify that a “comparison” task involving time data may still benefit from a trend-oriented encoding.

### 4.3 Constraints Block

```
CONSTRAINTS & PARAMETERS

Intended audience:        <value>
Preferred chart library:  <value>
Language:                 <value>
Interactivity required:   <value>
Accessibility needs:      <value>
Additional context:       <value>
```

The constraints block is intentionally simple and flat. Every parameter is a single line. The labels are human-readable and unambiguous. This structure is easy to extend: adding a new parameter requires one line in the template and one field in the `ParameterPanel` UI.

**Handling missing parameters:** When a parameter is null, the template substitutes a specific default string rather than omitting the line. “Not specified” tells the model the field exists but the user made no choice. “No preference — recommend the best fit” tells the model it has full latitude. This distinction prevents the model from assuming a null field means “don’t consider this dimension.”

-----

## 5. Output Schema Reference

The full schema is defined in `promptTemplates.js`. This section provides field-level documentation for developers rendering or consuming the response.

### `meta`

|Field                 |Type                           |Notes                                 |
|----------------------|-------------------------------|--------------------------------------|
|`advisor_version`     |string                         |Always `"1.0"` in this version        |
|`session_id`          |string | null                  |Echo of the session ID for correlation|
|`goal_category`       |string                         |One of the 8 canonical categories     |
|`confidence`          |`"high"` | `"medium"` | `"low"`|Model’s self-assessed reliability     |
|`confidence_rationale`|string                         |1–2 sentence explanation              |

Use `confidence` to conditionally render a warning banner in the UI when the value is `"low"`. A low confidence response always has `follow_up_questions` content.

### `primary_recommendation`

|Field                             |Type         |Notes                                     |
|----------------------------------|-------------|------------------------------------------|
|`chart_type`                      |string       |Canonical name, e.g. `"grouped bar chart"`|
|`rationale`                       |string       |3–5 sentence justification                |
|`data_mapping`                    |object       |Maps encoding channels to column names    |
|`data_mapping.x_axis`             |string | null|Column name + role                        |
|`data_mapping.y_axis`             |string | null|Column name + role                        |
|`data_mapping.color`              |string | null|Column name + encoding rationale          |
|`data_mapping.size`               |string | null|Column name + encoding rationale          |
|`data_mapping.facet`              |string | null|Column name + small-multiples rationale   |
|`data_mapping.tooltip`            |string[]     |Columns to include in hover state         |
|`data_mapping.additional_channels`|string | null|Shape, opacity, animation, etc.           |

### `design_decisions`

|Field                  |Subfield        |Type   |Notes                                              |
|-----------------------|----------------|-------|---------------------------------------------------|
|`color_palette`        |`type`          |string |`sequential | diverging | qualitative | single-hue`|
|`color_palette`        |`recommendation`|string |Palette name or hex values                         |
|`color_palette`        |`rationale`     |string |Why this palette fits                              |
|`scale`                |`x`             |string |Scale type + rationale                             |
|`scale`                |`y`             |string |Scale type + rationale                             |
|`scale`                |`zero_baseline` |boolean|`false` must always have justification             |
|`annotations`          |—               |string |Recommended annotation strategy                    |
|`sorting`              |—               |string |Sort order + rationale                             |
|`aspect_ratio`         |—               |string |e.g. `"16:9 — wide format suits time series"`      |
|`data_density_strategy`|—               |string |How to handle data volume                          |

### `accessibility`

|Field                 |Type                                 |Notes                                       |
|----------------------|-------------------------------------|--------------------------------------------|
|`color_blind_safe`    |boolean                              |Must be `true` if a11y params are set       |
|`redundant_encoding`  |string                               |Non-color encoding for critical distinctions|
|`aria_recommendations`|string | null                        |Specific ARIA roles/labels                  |
|`wcag_level`          |`"AA"` | `"AAA"` | `"not_applicable"`|Compliance target                           |

### `alternative_options`

Array of 2 objects, each with:

|Field           |Type  |Notes                                          |
|----------------|------|-----------------------------------------------|
|`chart_type`    |string|Alternative chart name                         |
|`use_when`      |string|Specific condition for choosing this           |
|`tradeoff`      |string|What you gain and lose vs. primary             |
|`key_difference`|string|Single most important implementation difference|

### `pitfalls`

Array of objects, each with:

|Field        |Type  |Notes                       |
|-------------|------|----------------------------|
|`risk`       |string|Short name of the pitfall   |
|`description`|string|What it is and why it occurs|
|`mitigation` |string|Specific, actionable fix    |

### `code_scaffold`

|Field     |Type  |Notes                                          |
|----------|------|-----------------------------------------------|
|`library` |string|Echo of user’s preferred library               |
|`language`|string|`javascript | typescript | python | r`         |
|`notes`   |string|Data transformation steps, performance notes   |
|`snippet` |string|Complete, runnable code using real column names|

### `follow_up_questions`

String array of 1–3 questions. Empty array `[]` when confidence is high and no ambiguity exists. Only include meaningful, targeted questions — never generic ones.

-----

## 6. Prompt Engineering Principles Applied

This section maps the prompt’s design choices to established prompt engineering techniques for traceability and future iteration.

### Role Prompting

**Applied in:** System prompt opening paragraph and literature citations.  
**Effect:** Activates domain-specific knowledge and constrains response style to expert register.

### Chain-of-Thought (Silent)

**Applied in:** The four-stage reasoning methodology (`SILENTLY work through...`).  
**Effect:** Improves recommendation quality by forcing structured analysis before output. The “silent” instruction prevents the reasoning from appearing in the output, which would increase token cost and break JSON parsing.

### Output Format Specification

**Applied in:** The full JSON schema in the output contract.  
**Effect:** Produces reliably parseable, consistently structured responses. The level of field-level documentation in the schema specification directly determines how well the model fills each field.

### Few-Shot Examples

**Not currently applied.** Future versions should add 1–2 complete example request/response pairs to the system prompt to anchor the model’s understanding of quality. This is the single highest-ROI improvement available.

### Negative Prompting

**Applied in:** Hard constraints section.  
**Effect:** Prevents specific, known failure modes. Negative constraints (“never do X”) are more reliable than positive guidelines (“prefer Y”) for high-stakes behavioral requirements.

### Constraint Specification

**Applied in:** Hard constraints + output contract required/optional designations.  
**Effect:** Creates verifiable evaluation criteria. A response either satisfies all 10 hard constraints or it does not — this is measurable.

### Persona Consistency

**Applied in:** Named identity (“VizAdvisor”), mission statement, tone instructions.  
**Effect:** Reduces response variability across sessions and models. A named, described persona produces more consistent output than an unnamed, generic one.

-----

## 7. Token Budget & Cost Management

### Estimated Token Counts

|Component                                  |Tokens (approx.)|
|-------------------------------------------|----------------|
|System prompt                              |~1,200          |
|User prompt — schema (10 columns)          |~200            |
|User prompt — sample rows (3 rows × 5 cols)|~150            |
|User prompt — goal + parameters            |~100            |
|**Total input**                            |**~1,650**      |
|LLM response (full recommendation)         |~800–1,500      |
|**Total per request**                      |**~2,500–3,000**|

At Claude Sonnet pricing (approximate), a full recommendation costs roughly $0.01–0.015 per request. This is negligible for individual use and manageable at scale.

### Cost Control Levers

The following parameters in `promptTemplates.js` can be tuned to reduce token cost at the expense of recommendation detail:

- **Schema columns cap:** Currently 50. Reducing to 20 saves ~250 tokens for wide datasets.
- **Sample row count:** Currently 5. Reducing to 3 saves ~60–100 tokens.
- **Sample value truncation:** Currently 100 chars. Reducing to 50 chars saves ~50 tokens.
- **`max_tokens` in API call:** Currently set to accommodate full responses (~1,500). Do not reduce below 1,000 — truncated JSON breaks the parser.

### Streaming vs. Buffered

Streaming does not change token cost. It improves perceived performance only. The full response is always generated regardless of whether streaming is enabled.

-----

## 8. Multi-Turn Conversation Design

VizAdvisor supports multi-turn refinement sessions. After the initial recommendation, users can ask follow-up questions or request modifications. The conversation history is maintained in `SessionContext.conversationHistory`.

### Turn Structure

```
Turn 1 (initial):
  User:      buildUserPrompt(context)          ← full dataset + goal + params
  Assistant: <JSON recommendation>

Turn 2 (refinement):
  User:      "Can you adjust for a colorblind audience?"
  Assistant: <updated JSON recommendation>

Turn 3 (follow-up):
  User:      "Show me a D3 implementation instead of Recharts"
  Assistant: <updated JSON recommendation with new code_scaffold>
```

The assistant’s prior response is always included in the message history as a raw JSON string. This ensures the model knows its prior recommendation and can produce diffs or updates coherently.

### Follow-Up Prompt Design Guidelines

Follow-up questions should be natural language — users should not need to repeat schema information or goal statements. The conversation history provides that context. The model is expected to produce a complete updated JSON response (not a partial patch) on every turn, so the output panel can re-render fully without merging logic.

**Good follow-up patterns:**

- “Make this colorblind safe” → updates `color_palette`, `accessibility`
- “Show me the Python version” → updates `code_scaffold`
- “What if I have 50,000 rows?” → updates `data_density_strategy`, `pitfalls`
- “Add an alternative using a heatmap” → modifies `alternative_options`

**Anti-patterns to communicate to users:**

- Uploading a different dataset in a follow-up (start a new session instead)
- Asking for completely different chart types without contextual reason (the model will comply but the history becomes incoherent)

-----

## 9. Failure Modes & Mitigations

### Mode 1: JSON Wrapping in Markdown Fences

**Symptom:** Response begins with ````json` and ends with `````.  
**Cause:** Model’s RLHF training for human-readable output overrides the “no fences” instruction.  
**Mitigation in `llmService.parseResponse()`:** Strip ````json`, ````` and leading/trailing whitespace before `JSON.parse()`. Log the occurrence for monitoring — high frequency indicates the system prompt instruction needs strengthening.

### Mode 2: Partial JSON (Response Truncated)

**Symptom:** `JSON.parse()` fails with “Unexpected end of JSON input.”  
**Cause:** `max_tokens` limit reached before response completed.  
**Mitigation:** Increase `max_tokens` to 2,048. Monitor response lengths — if routinely hitting limits, add a `code_scaffold.snippet` length cap in the system prompt.

### Mode 3: Generic Recommendations

**Symptom:** Rationale fields contain boilerplate (“Bar charts are great for comparisons”) with no reference to the user’s specific columns or data characteristics.  
**Cause:** System prompt role framing or reasoning methodology not being followed.  
**Detection:** Automated check: if the rationale does not contain any column name from the schema, flag as generic.  
**Mitigation:** Strengthen Stage 1 (Data Analysis) instruction. Consider adding a few-shot example showing a specific vs. generic rationale.

### Mode 4: Violated Hard Constraints

**Symptom:** Response recommends a pie chart for 8 categories, or includes a rainbow color palette.  
**Cause:** Hard constraints are not being followed.  
**Detection:** Post-parse validation checks in `llmService.parseResponse()`.  
**Mitigation:** Add constraint violations to the validation layer and re-prompt with the violation flagged. If persistent, move the constraint to a post-processing rule enforced in code rather than relying on the model.

### Mode 5: Missing Required Fields

**Symptom:** Validation fails because `primary_recommendation.rationale` or `code_scaffold.snippet` is absent.  
**Cause:** Model chose to omit a field it found irrelevant or couldn’t fill.  
**Mitigation:** The `MUST be present` language in the output contract. If missing fields persist for specific field types, add an explicit check and re-prompt with “Your previous response was missing the `{field}` field. Please provide a complete response.”

### Mode 6: Hallucinated Column References

**Symptom:** Code scaffold references column names that don’t exist in the schema.  
**Cause:** Model invented plausible-sounding column names rather than using provided ones.  
**Detection:** Post-parse: check every column name in `data_mapping` against the provided schema.  
**Mitigation:** Hard constraint 7 addresses this. Post-parse validation can catch and flag it.

-----

## 10. Testing & Evaluating Prompt Quality

### Unit Testing

The `promptTemplates.js` module is pure JavaScript with no side effects. Unit tests in `tests/unit/promptTemplates.test.js` should cover:

- `buildUserPrompt()` produces the expected string structure for a complete context
- `buildUserPrompt()` handles null parameters gracefully
- `buildUserPrompt()` truncates schema at 50 columns
- `buildUserPrompt()` truncates sample values at 100 characters
- `buildMessages()` includes the system prompt in the return value
- `buildFollowUpMessages()` correctly appends history turns

### Prompt Regression Testing

Maintain a set of golden-path test cases in `tests/prompts/`. Each case is a JSON file with:

```json
{
  "description": "10-column sales dataset, trend goal, D3 preferred",
  "input": { "dataset": {...}, "goal": {...}, "parameters": {...} },
  "expected": {
    "goal_category": "trend",
    "primary_chart_type": "line chart",
    "must_include_column": "order_date",
    "code_library": "d3",
    "confidence": "high"
  },
  "must_not_include": ["pie chart", "rainbow", "3D"]
}
```

Run these against the live API periodically (not on every CI build, due to cost and latency). Compare outputs to expected values using the scoring criteria in Section 6.

### Quality Scoring Rubric

Each LLM response can be scored on a 0–10 scale across five dimensions:

|Dimension                     |Score 0                     |Score 10                                       |
|------------------------------|----------------------------|-----------------------------------------------|
|**Specificity**               |No column names referenced  |Every key decision references a specific column|
|**Rationale depth**           |One-sentence rationale      |3–5 sentences citing perceptual principles     |
|**Constraint adherence**      |Accessibility ignored       |All constraints reflected in output            |
|**Code usability**            |Placeholder column names    |Copy-pasteable with real column names          |
|**Hard constraint compliance**|Any hard constraint violated|All 10 constraints satisfied                   |

Target average: 8.0+. Below 7.0 warrants a prompt revision.

-----

## 11. Versioning & Change Management

The system prompt version is stored in the `meta.advisor_version` field of every response. When the system prompt changes materially, increment this version.

**Patch changes** (no version bump needed): Typo fixes, clarified wording that doesn’t change behavior.

**Minor changes** (increment patch: 1.0 → 1.1): New hard constraints, tone adjustments, output schema fields added (backward compatible).

**Major changes** (increment major: 1.x → 2.0): Output schema breaking changes, fundamental reasoning methodology changes, complete role reframing.

Maintain a `CHANGELOG.md` in `docs/prompts/` with dated entries for every system prompt change. Each entry should document what changed, why, and what improvement in output quality was observed.

### Change Testing Protocol

Before deploying any system prompt change:

1. Run the full golden-path test suite against both the old and new prompt
1. Score all outputs on the quality rubric
1. Verify the new prompt scores ≥ 0.5 points higher on average
1. Verify no golden-path test regresses
1. Deploy to a staging environment and test with 5 real user sessions before production rollout

-----

## 12. Prompt Iteration Roadmap

The following improvements are prioritized for future prompt versions, ranked by expected impact:

**High impact:**

1. **Add 2 few-shot examples** to the system prompt — one for a comparison task, one for a distribution task. Full request + response pairs demonstrating the ideal output quality. Estimated improvement: +1.5 points on specificity and rationale depth rubric scores.
1. **Add a “data quality” analysis stage** in the reasoning methodology. The model currently receives nullability and range metadata but is not explicitly instructed to flag data quality issues (high null rates, extreme outliers, suspicious uniform distributions) that affect visualization reliability.
1. **Structured code scaffold validation.** Implement a post-processing step that parses the `code_scaffold.snippet` and verifies every `data_mapping` column name appears in the code. Auto-correct if not.

**Medium impact:**

1. **Goal clarification micro-prompt.** If the user’s goal description is under 10 words or does not contain a verb, run a lightweight pre-prompt that asks 1–2 targeted clarifying questions before the full recommendation prompt. This reduces low-confidence responses.
1. **Audience-adaptive verbosity.** Add an explicit verbosity parameter (`"technical" | "explanatory" | "executive"`) that controls rationale length and jargon level, separate from the audience field.

**Lower impact:**

1. **Chart type canonicalization.** Maintain a controlled vocabulary of chart type names in the prompt to prevent inconsistent naming (`"bar chart"` vs. `"bar graph"` vs. `"column chart"`).
1. **Library-specific prompt extensions.** Add library-specific instructions for the most common libraries (D3, Recharts, Plotly) so the model knows idioms specific to each — e.g., D3’s data join pattern, Recharts’ `<ResponsiveContainer>` requirement, Plotly’s trace/layout structure.
