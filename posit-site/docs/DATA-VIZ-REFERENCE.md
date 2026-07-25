---
title: "Data Visualization Reference"
---

> **Document version:** 1.0  
> **Last updated:** February 2026  
> **Audience:** Developers, contributors, and users who want to understand the theoretical and practical foundations behind VizAdvisor’s recommendations

-----

## Table of Contents

1. [Why This Document Exists](#1-why-this-document-exists)
1. [The Visualization Selection Framework](#2-the-visualization-selection-framework)
1. [Chart Type Taxonomy](#3-chart-type-taxonomy)

- 3.1 [Comparison](#31-comparison)
- 3.2 [Trend Over Time](#32-trend-over-time)
- 3.3 [Distribution](#33-distribution)
- 3.4 [Correlation & Relationship](#34-correlation--relationship)
- 3.5 [Part-of-Whole](#35-part-of-whole)
- 3.6 [Geospatial](#36-geospatial)
- 3.7 [Network & Flow](#37-network--flow)
- 3.8 [Ranking](#38-ranking)

1. [Visual Encoding Principles](#4-visual-encoding-principles)
1. [Color Design](#5-color-design)
1. [Accessibility Standards](#6-accessibility-standards)
1. [Scale & Axis Design](#7-scale--axis-design)
1. [Data Volume & Density](#8-data-volume--density)
1. [Interactivity Design](#9-interactivity-design)
1. [Common Pitfalls Encyclopedia](#10-common-pitfalls-encyclopedia)
1. [Chart Library Comparison](#11-chart-library-comparison)
1. [Glossary](#12-glossary)

-----

## 1. Why This Document Exists

VizAdvisor’s LLM recommendations are grounded in a specific body of knowledge about data visualization theory and practice. This document makes that knowledge base explicit and human-readable. It serves three purposes:

First, it is the **source of truth** for the hard constraints and design principles encoded in the system prompt. When a constraint exists — “never use rainbow color scales” — this document explains why in full.

Second, it is a **reference for contributors** who want to extend the application’s goal categories, add new chart types to the recommendation pool, or modify the LLM’s reasoning methodology.

Third, it is a **standalone reference** for any user who wants to understand the principles behind the recommendations they receive, rather than just accepting them.

-----

## 2. The Visualization Selection Framework

VizAdvisor’s selection logic is rooted in Tamara Munzner’s **What-Why-How framework**, augmented with practical heuristics from applied visualization design. The framework treats chart selection not as a lookup table but as a systematic analysis.

### Step 1 — What: Characterize the Dataset

Every dataset can be decomposed along two axes:

**Dataset types:**

- Tables (rows of items with attributes)
- Networks (nodes and edges)
- Fields (spatial continuous data: grid, volumetric)
- Geometry (maps, spatial objects)
- Temporal sequences

**Attribute types:**

- Quantitative (numeric, continuous or discrete)
- Ordinal (ordered categorical: Low/Med/High, Star ratings)
- Nominal (unordered categorical: countries, product names)
- Temporal (dates, times, durations)
- Geographic (place names, coordinates, region codes)

The combination of dataset type and attribute types constrains which visualization idioms are valid. A network dataset cannot be a bar chart; a table with only nominal attributes cannot be a scatter plot.

### Step 2 — Why: Define the Task

The user’s goal translates into one or more abstract visualization tasks:

|High-level task|Subtasks                                                                 |
|---------------|-------------------------------------------------------------------------|
|Discover       |Identify outliers, find clusters, detect trends, understand distributions|
|Present        |Compare values, show relationships, communicate composition              |
|Produce        |Annotate for analysis, filter for exploration, derive computed values    |

The task determines which visual properties matter most. A “find outlier” task requires encodings where unusual values are pre-attentively salient (position, color). A “compare magnitude” task requires encodings where lengths or positions can be read accurately (aligned bar charts on a common baseline).

### Step 3 — How: Select the Encoding

Given the What and Why, the How is constrained to the set of encodings that accurately represent the data types and support the task. Encodings are not equally effective. Munzner’s **channel effectiveness ranking** (derived from Cleveland & McGill’s landmark perception studies) provides a hierarchy:

**For quantitative data:**

1. Position on a common scale (bar chart, scatter plot)
1. Position on non-aligned scales (small multiples)
1. Length (bar chart, proportional symbols)
1. Tilt/angle (rarely recommended — pie charts, radar)
1. Area (bubble chart — use cautiously)
1. Depth (3D — almost never recommended)
1. Color luminance (heatmap — use for overview, not precise reading)
1. Color saturation
1. Curvature
1. Volume (3D — never for quantitative comparison)

**For categorical data:**

1. Spatial region (small multiples, faceting)
1. Color hue (up to 8–10 distinguishable categories)
1. Shape (scatter plots, up to 6 distinct shapes)
1. Motion (animation — rarely appropriate)

This ranking is the primary input to Stage 4 of VizAdvisor’s reasoning methodology (candidate evaluation).

-----

## 3. Chart Type Taxonomy

### 3.1 Comparison

**Goal:** Show how values differ across discrete categories.

**Bar Chart (Vertical/Horizontal)**
The default, highest-accuracy chart for categorical comparison. Position on a common baseline (the zero axis) enables precise magnitude comparison. Use horizontal orientation when category labels are long or when there are more than 8 categories.

- Best for: ≤ 30 categories, single metric
- Avoid when: categories have natural order → use sorted bar; time is on the x-axis → use line chart
- Common pitfall: Truncating the y-axis to exaggerate differences

**Grouped Bar Chart**
Extends bar charts to compare sub-groups within categories. Each category cluster contains one bar per sub-group.

- Best for: 2–4 sub-groups, ≤ 15 categories
- Avoid when: > 4 sub-groups (visual clutter becomes unmanageable) → use small multiples or faceted bars
- Common pitfall: Using grouped bars when a stacked bar would better show both totals and proportions

**Dot Plot (Cleveland Dot Plot)**
A bar chart alternative that reduces ink and allows wider x-axis range perception. Each value is a dot positioned on a common scale.

- Best for: Many categories (15–50), or when exact values matter more than magnitude
- Advantage over bars: Less visual weight, better for long lists
- Common pitfall: Readers unfamiliar with dot plots may not intuit that distance from the axis = value

**Radar / Spider Chart**
Shows multiple quantitative variables for one or more subjects on axes radiating from a center.

- Best for: Showing a profile across 5–10 variables where the “shape” pattern matters
- Avoid when: Comparing more than 3–4 subjects (overlapping polygons become unreadable); precise value comparison is needed (angle encoding is inaccurate)
- Common pitfall: Using radar charts because they look impressive, not because area/shape carries meaning

-----

### 3.2 Trend Over Time

**Goal:** Show how values change across a continuous time dimension.

**Line Chart**
The canonical encoding for temporal data. Time on the x-axis (always left-to-right), quantitative value on the y-axis. Lines imply continuity between points — only use when continuity is meaningful (measurements were taken at regular intervals or the underlying phenomenon is continuous).

- Best for: 1–8 series, regular time intervals, highlighting trend direction
- Avoid when: Time intervals are irregular and gaps matter → use scatter with connected lines; too many series (> 8) → use small multiples

**Area Chart**
A line chart with the area below the line filled. The fill adds visual weight and emphasizes cumulative magnitude. Only valid when zero is a meaningful baseline.

- Best for: Showing volume over time (sales, users, requests), 1–3 series
- Avoid when: Negative values are present; multiple overlapping series obscure each other → use stacked area carefully

**Stacked Area Chart**
Shows multiple time series stacked on top of each other, where the total height represents the sum of all series. Good for showing part-of-whole over time, but individual series trends are hard to read except for the bottom series.

- Best for: 3–6 series where the total trend AND rough proportions matter
- Avoid when: Individual series trends matter more than the total → use small multiples

**Candlestick / OHLC Chart**
Shows open, high, low, and close values for time periods. Domain-specific — primarily financial data.

**Streamgraph**
A displaced stacked area chart where the baseline oscillates to produce a symmetrical “stream” shape. Emphasizes rhythm and volume over precise values.

- Best for: Exploratory, editorial contexts where aesthetics and pattern are primary
- Avoid in: Analytical contexts where accurate value reading is needed

-----

### 3.3 Distribution

**Goal:** Show the shape, spread, and concentration of a quantitative variable.

**Histogram**
Divides a quantitative variable into bins and shows frequency (count or density) per bin. The fundamental distribution chart.

- Best for: Understanding the overall shape (normal, skewed, bimodal, uniform) of a single variable
- Critical choice: Bin width dramatically affects appearance — show multiple bin widths or use auto-optimized binning (Sturges’, Scott’s, or Freedman-Diaconis rule)
- Common pitfall: Using category counts (bar chart task) as if they were a distribution

**Density Plot (KDE)**
A smoothed, continuous version of a histogram. Uses kernel density estimation to produce a probability density curve.

- Best for: 2–5 overlapping distributions on the same axis; cleaner appearance than overlapping histograms
- Avoid when: Sample size is small (< 50) — KDE can suggest smooth distributions from noisy data

**Box Plot (Box-and-Whisker)**
Shows five summary statistics: minimum, Q1 (25th percentile), median, Q3 (75th percentile), maximum. Outliers plotted individually.

- Best for: Comparing distributions across many categories (5–30) when shape detail is secondary
- Avoid when: The distribution is bimodal or non-symmetric in ways the five-number summary hides → use violin plot

**Violin Plot**
A box plot with mirrored KDE plots on each side. Shows full distribution shape.

- Best for: Comparing 2–8 groups when shape (modality, skew) matters
- Avoid when: Small samples (< 50 per group) → the smooth curves mislead

**Beeswarm Plot**
Shows individual data points distributed to avoid overlap, preserving full distribution information.

- Best for: Small datasets (< 300 points), when individual points are meaningful
- Avoid when: Large datasets — overplotting management becomes computationally expensive

-----

### 3.4 Correlation & Relationship

**Goal:** Show relationships, patterns, or associations between two or more variables.

**Scatter Plot**
The gold standard for visualizing the relationship between two quantitative variables. Each point represents one observation.

- Best for: Up to ~500 points with no mitigation; identifying linear/non-linear relationships, outliers, clusters
- Critical: Always start both axes at the natural minimum of the data, not necessarily zero — a truncated scatter plot axis is acceptable (unlike bar charts) because the position, not the length from baseline, encodes the value
- Overplotting threshold: > 500 points without mitigation becomes unreadable

**Bubble Chart**
A scatter plot where point size encodes a third quantitative variable.

- Best for: 3-variable relationships, ≤ 200 points
- Avoid when: Points overlap significantly (size differences become ambiguous); the size variable has very low variance (all bubbles look the same)
- Common pitfall: Area vs. radius encoding — always encode value as area, not radius (radius-encoded bubbles make small values look much smaller than they are)

**Heatmap (Correlation Matrix)**
Shows pairwise correlations between multiple variables as a color-encoded matrix.

- Best for: 5–30 variables, overview of correlation patterns, identifying clusters of related variables
- Avoid when: Precise correlation values matter — the color channel has low accuracy for exact value reading; annotate cells with values if precision is needed

**Parallel Coordinates Plot**
Shows multivariate data by drawing each observation as a polyline crossing multiple vertical axes.

- Best for: Exploring high-dimensional data (5–20 variables), identifying multivariate clusters and patterns
- Requires interactivity: Axis reordering is essential for pattern discovery

-----

### 3.5 Part-of-Whole

**Goal:** Show how parts contribute to a total.

**Pie Chart**
Shows proportions as angles and arc lengths. Useful only when the number of parts is small and the key question is “roughly what fraction?”

- Hard limit: ≤ 5 categories. Beyond this, angles become indistinguishable
- Avoid when: Precise proportions matter; parts are close in value; showing change over time
- Alternative: Stacked bar chart for > 5 parts, or any time comparison or precision matters

**Donut Chart**
A pie chart with a center hole. The hole can contain a key total value. Marginally better than pie for labeling.

- Same constraints as pie chart

**Treemap**
Nested rectangles where area encodes proportion within a hierarchy.

- Best for: 2–3 levels of hierarchy, 10–200 leaf nodes
- Avoid when: Precise comparisons are needed (area encoding is less accurate than length)

**Sunburst Chart**
Concentric ring version of a treemap. More visually engaging, less precisely readable.

- Best for: Editorial/exploratory contexts, 3+ hierarchy levels
- Avoid in: Analytical contexts

**Waffle Chart**
A grid of cells where filled cells represent the proportion. Familiar to general audiences as an alternative to pie.

- Best for: Simple proportions for non-specialist audiences, ISOTYPE-style communication
- Avoid when: Very precise proportions need encoding (grid resolution limits precision)

**Stacked Bar Chart (100%)**
A stacked bar chart normalized to 100% for each group. Shows composition across categories.

- Best for: Comparing proportional breakdown across 2–10 groups
- Avoid when: Absolute totals matter (normalization removes them); too many stack segments (> 5 become hard to compare)

-----

### 3.6 Geospatial

**Goal:** Show data with geographic variation.

**Choropleth Map**
Colors geographic regions (countries, states, zip codes) by a quantitative or ordinal variable.

- Best for: Regional aggregated data (rates, averages, totals by region)
- Critical: Normalize for area or population when appropriate — a large state with high total cases may have a low per-capita rate
- Common pitfall: Using sequential single-hue color scales when a diverging scale (centered on a meaningful midpoint) would better show above/below average patterns

**Proportional Symbol Map**
Points sized proportionally to a quantitative value, placed at geographic locations.

- Best for: Absolute totals at point locations (city populations, store revenues)
- Advantage over choropleth: Shows absolute values, not just rates; not affected by area distortion

**Dot Density Map**
Each dot represents a fixed count of occurrences, placed randomly within a region.

- Best for: Showing geographic distribution and density patterns

**Flow Map**
Arrows or curves connecting origins and destinations, sized by flow volume.

- Best for: Migration, trade, transportation — any directed geographic movement data

-----

### 3.7 Network & Flow

**Goal:** Show connections, flows, or hierarchical relationships.

**Sankey Diagram**
Shows flow quantities between a series of stages. Width encodes flow volume.

- Best for: Process flows, budget allocations, conversion funnels with 3–8 stages
- Avoid when: The network is cyclic (Sankeys are acyclic by definition); too many paths (becomes a “hairball”)

**Chord Diagram**
Shows pairwise relationships between a set of entities using arcs.

- Best for: Symmetric relationships (trade between countries, mutual connections), ≤ 12 entities
- Avoid when: Directionality matters (hard to read from chord diagrams); more than 12 entities (visual clutter)

**Force-Directed Graph**
A node-link diagram where positions are determined by a physics simulation.

- Best for: Exploring network topology, community detection, visualizing connectivity patterns
- Avoid when: Precise positional encoding is needed (positions are arbitrary); very large networks (> 500 nodes require aggressive filtering or aggregation)

**Dendrogram / Tree**
A hierarchical tree structure showing parent-child relationships.

- Best for: Organizational hierarchies, classification trees, phylogenies

-----

### 3.8 Ranking

**Goal:** Show relative standing or ordered performance.

**Sorted Bar Chart**
The most reliable chart for ranking. Bars sorted by value (descending or ascending) make rank immediately visible.

- Always prefer to: Pie charts, radar charts, and bubble charts for ranking tasks

**Lollipop Chart**
A dot plot variant that extends a line from the axis to the dot. Less visual weight than bars.

- Best for: Large numbers of ranked items (20–50), when value precision matters

**Slope Chart**
Shows rank change between two time points. Each line represents one item, y-axis is rank or value, x-axis is two time points.

- Best for: “Who rose, who fell?” questions comparing exactly two time periods

**Bump Chart**
Extends slope chart to multiple time periods. Y-axis is rank, not value.

- Best for: Rank changes over 3–12 time periods, ≤ 15 items

-----

## 4. Visual Encoding Principles

### Pre-attentive Attributes

Pre-attentive attributes are visual properties processed by the brain in under 250ms, before conscious attention is directed. They are the most powerful tools for emphasis and pattern communication.

**High-value pre-attentive attributes for data visualization:**

- Color hue (nominal distinction)
- Color luminance / intensity (quantitative/ordinal distinction)
- Size (quantitative distinction)
- Shape (nominal distinction, ≤ 6 shapes)
- Spatial position (most accurate quantitative encoding)
- Motion (quantitative/ordinal — use sparingly)

A chart should use pre-attentive attributes to answer the chart’s primary question. If the question is “which category is largest?” then length (bar chart, common baseline) is the pre-attentive answer. If the question is “is this item unusual?” then color hue on a single unusual item is the pre-attentive answer.

### The Data-Ink Ratio

Edward Tufte’s data-ink ratio principle: maximize the proportion of a chart’s ink that encodes data. Remove or lighten anything that does not carry information — gridlines, excessive tick marks, decorative borders, 3D effects, drop shadows, gradient fills on bars.

A high data-ink ratio produces charts that are easier to read, print clearly at small sizes, and reduce cognitive load.

**Practical checklist:**

- Are gridlines lighter than the data?
- Are tick marks only at meaningful intervals?
- Are axis labels only as numerous as needed?
- Are chart borders necessary (usually no)?
- Are there any gradient fills that don’t encode values (remove them)?
- Are there any icons, illustrations, or decorative elements not encoding data (remove them)?

### Small Multiples

When a comparison would require color distinctions across more than 6–8 categories, or when the question involves comparing patterns across subgroups, small multiples (trellis charts, faceted charts) are almost always superior to a single overloaded chart. Each panel uses the same axes and encoding, enabling pattern comparison through position rather than color discrimination.

-----

## 5. Color Design

### Palette Types

**Sequential palettes** — for ordered quantitative data where one end represents “more” or “higher.” Uses a single hue progressing from light to dark, or multiple hues with consistent luminance progression.

- Examples: Blues, Greens, viridis, plasma, YlOrRd
- Use for: Heatmaps, choropleth maps, encoding density or magnitude

**Diverging palettes** — for quantitative data with a meaningful midpoint (zero, average, target). Two hues diverge from a neutral center.

- Examples: RdBu, RdYlBu, PRGn, BrBG
- Use for: Above/below average, positive/negative values, correlation matrices

**Qualitative palettes** — for nominal (unordered categorical) data. Distinct hues with similar luminance so no category appears more important than others.

- Examples: Tableau 10, D3 category10, ColorBrewer Set1/Set2, Okabe-Ito (colorblind-safe)
- Use for: Encoding group membership, coloring series in multi-series charts

**Single-hue palettes** — for highlighting one category against neutral others. All categories are gray except the one in focus.

- Use for: Annotation and emphasis, directing attention to a specific series

### Colorblind Accessibility

Approximately 8% of males and 0.5% of females have some form of color vision deficiency. The most common is red-green deficiency (deuteranopia/protanopia). Blue-yellow deficiency (tritanopia) is rarer.

**Colorblind-safe palette recommendations:**

|Use case                  |Recommended palette                    |
|--------------------------|---------------------------------------|
|Qualitative (any)         |Okabe-Ito (8-color)                    |
|Qualitative (4 categories)|Wong palette                           |
|Sequential                |viridis, cividis, plasma               |
|Diverging                 |Blue-Orange diverging (avoid red-green)|

**Never use:**

- Red and green together to encode different categories or opposing values
- Rainbow/jet scales for continuous data (perceptually non-monotonic AND inaccessible)

**Always add redundant encoding:** When color is the primary encoding, add a secondary channel (shape for scatter plots, pattern/texture for bars, direct labels, or position via faceting) so the chart is readable without color discrimination.

### Color and Luminance

Dark backgrounds with light data can be visually striking but reduce readability in print and in bright environments. Light backgrounds are the safe default. If a dark theme is used, ensure sufficient luminance contrast (WCAG AA: 4.5:1 for text, 3:1 for graphical elements).

-----

## 6. Accessibility Standards

### WCAG for Data Visualization

The Web Content Accessibility Guidelines (WCAG) provide the primary framework for accessible visualization. Key requirements for data viz:

**Level AA (minimum target):**

- All meaningful chart elements have text alternatives (alt text, ARIA labels)
- Color is never the only means of conveying information (redundant encoding required)
- Text within charts meets 4.5:1 contrast ratio
- Interactive elements are keyboard navigable
- Focus indicators are visible on interactive elements

**Level AAA (stretch target):**

- All data is available in a tabular alternative
- All interactive features work without a pointing device
- Complex charts have extended descriptions (longdesc or adjacent text)

### ARIA Implementation

Charts rendered with SVG require ARIA attributes to be accessible to screen readers:

```html
<!-- Chart container -->
<svg role="img" aria-labelledby="chart-title chart-desc">
  <title id="chart-title">Monthly Sales by Region, 2024</title>
  <desc id="chart-desc">
    A bar chart showing sales totals for North, South, East, and West regions
    for each month of 2024. The North region consistently leads, with a peak
    of $2.4M in October.
  </desc>
  <!-- chart content -->
</svg>
```

For interactive charts, use `role="application"` and implement keyboard navigation with visible focus states.

### Tabular Data Alternative

Every chart should have a mechanism to view the underlying data in tabular form. This serves both accessibility and analytical needs. Implement as a collapsible “Show data table” below each chart.

-----

## 7. Scale & Axis Design

### Zero Baseline Rule

**Bar charts, area charts, and stacked bars must start at zero.** These charts encode values as lengths from the baseline. A truncated baseline makes small differences appear enormous — this is one of the most common forms of misleading data visualization.

**Scatter plots, line charts, and dot plots do not need to start at zero.** These charts encode values as positions, not lengths. Starting at a meaningful minimum rather than zero can dramatically improve resolution for patterns that occur over a narrow range.

**Log scales** are appropriate when:

- The data spans multiple orders of magnitude (e.g., 1 to 1,000,000)
- Multiplicative relationships or percentage changes are more meaningful than absolute differences
- The distribution is right-skewed with a long tail

Always label log-scale axes clearly and use powers of 10 as tick marks (1, 10, 100, 1,000).

### Axis Label Density

Too few tick marks leave the reader unable to estimate values. Too many create visual noise. Aim for 4–8 tick marks per axis for quantitative scales. For time scales, align ticks with natural periods (days, weeks, months, quarters, years).

Rotate x-axis labels only as a last resort — angled text is harder to read. Prefer horizontal orientation by switching to a horizontal bar chart when category labels are long.

### Secondary Axes (Dual Axes)

Dual y-axes (two different quantitative scales on the same chart) are one of the most common sources of misleading visualizations. The visual relationship between two series plotted against different scales is determined entirely by the axis ranges chosen, which can be manipulated to make any correlation appear or disappear.

**Use dual axes only when:**

- The two series share the same temporal or categorical dimension
- The relationship between the series is the explicit focus of the chart
- The axis ranges are explicitly labeled and the reader is expected to interpret them independently

**Always consider instead:** Two separate aligned charts (a small multiples approach) that share the x-axis. This makes both series individually readable while maintaining the visual proximity needed for pattern comparison.

-----

## 8. Data Volume & Density

### Overplotting Management

Overplotting occurs when multiple data points overlap, making it impossible to see the underlying distribution. It is the most common problem with scatter plots at scale.

|Data volume  |Mitigation                                                                                     |
|-------------|-----------------------------------------------------------------------------------------------|
|< 500 points |No mitigation needed; use standard scatter                                                     |
|500–5,000    |Alpha transparency (opacity 0.3–0.5)                                                           |
|1,000–10,000 |Hexbin chart (hexagonal binning)                                                               |
|5,000–100,000|Contour density plot; 2D histogram                                                             |
|> 100,000    |Aggregate first (binning, sampling, summarization); WebGL-accelerated rendering (deck.gl, regl)|

### Aggregation Strategies

When data volume makes point-level display impractical, aggregate to the appropriate granularity for the question:

- **Temporal:** Bin by day, week, month, quarter depending on the time span
- **Geographic:** Aggregate to the smallest region that maintains statistical reliability (avoid choropleth maps with single-digit counts per region)
- **Categorical:** Group small categories into “Other” when they represent < 3% of the total

### Progressive Loading

For datasets fetched from an API or computed on demand, show a meaningful partial view quickly rather than blocking on complete data. Strategies:

- Show aggregated data first, then load detail on zoom/interaction
- Show a data sample with explicit “n of N records shown” labeling
- Use skeleton loading states that match the chart’s final layout

-----

## 9. Interactivity Design

### When to Add Interactivity

Interactivity adds implementation cost, accessibility burden, and cognitive load. It is justified when:

- The dataset is too large or complex to display fully in a static view
- The primary task is exploration rather than communication
- Multiple sub-questions benefit from a single data source (filter, drill-down, cross-filter)
- The audience will use the visualization repeatedly and will learn the interactive controls

Interactivity is not justified when:

- The chart will be embedded in a report, email, or PDF
- The primary task is a simple, single-question communication
- The audience is general public or non-technical (interaction adds confusion)

### Recommended Interaction Patterns

**Tooltip on hover:** Show precise values for points or bars. Always include the values the chart encodes, the item identifier, and any contextual fields. Tooltips are the lowest-cost, highest-value interaction.

**Zoom and pan:** For time series and scatter plots with dense data. Implement with controlled zoom levels (snap to natural periods for time scales).

**Filter / brush selection:** Drag to select a range on one axis, which filters other views. Essential for linked/coordinated multi-chart dashboards.

**Highlight on hover:** In multi-series charts, dim all series except the one under the cursor. Dramatically reduces visual complexity for comparison tasks.

**Drill-down:** Click on an aggregate (region, category, time period) to see constituent detail. Requires clear visual indication that elements are interactive (cursor changes, hover states).

**Cross-filtering:** Selecting an element in one chart filters data in all linked charts. Most powerful for dashboard exploration; requires careful state management.

### Interactivity Accessibility

Every interaction must have a keyboard equivalent. Tooltips must be triggerable via keyboard focus, not only mouse hover. Interactive controls must have visible focus states. For complex interactions (brushing, zooming), provide an equivalent non-interactive summary view or data table as an alternative.

-----

## 10. Common Pitfalls Encyclopedia

A comprehensive reference to the visualization errors VizAdvisor is designed to detect and prevent.

### Truncated Y-Axis

**What it is:** Starting the y-axis of a bar chart above zero to exaggerate differences between values.  
**Why it misleads:** Bar length encodes magnitude; cutting the baseline makes a 5% difference look like a 500% difference.  
**Fix:** Always start bar chart y-axes at zero. If the data range is narrow and starting at zero wastes space, use a line chart or dot plot instead, where truncation is acceptable.

### Dual-Axis Distortion

**What it is:** Plotting two variables with different units on the same chart using two y-axes with independently chosen scales.  
**Why it misleads:** Any correlation or divergence between the series can be created or eliminated by adjusting the scale ranges. There is no objective “correct” alignment.  
**Fix:** Use two separate, aligned charts sharing the same x-axis.

### Pie Chart Overload

**What it is:** Using a pie chart with more than 5 categories, or using it when precise comparison is needed.  
**Why it misleads:** Humans are poor at comparing angles and arc lengths, especially for adjacent slices with similar values.  
**Fix:** Sorted bar chart for any ranking or comparison. Pie only for “roughly half,” “roughly a quarter” level precision.

### Rainbow/Jet Color Scale

**What it is:** Using a color scale that cycles through the rainbow spectrum for continuous quantitative data.  
**Why it misleads:** The rainbow spectrum is not perceptually monotonic — there are artificial “bands” at yellow and cyan that look like data boundaries when they are not. It is also inaccessible to color-blind viewers.  
**Fix:** Perceptually uniform sequential palettes: viridis, plasma, cividis, magma.

### 3D Chart Effects

**What it is:** Adding three-dimensional perspective to bar charts, pie charts, or other 2D chart types.  
**Why it misleads:** Perspective foreshortening makes bars at the back of the chart appear shorter than equally-valued bars at the front.  
**Fix:** Remove all 3D effects. Use 2D representations universally except for genuinely spatial 3D data.

### Smoothing Away Signal

**What it is:** Applying excessive smoothing to a time series, concealing real volatility and inflection points.  
**Why it misleads:** The smoothed line may suggest steady trends that disguise important spikes, drops, or reversals.  
**Fix:** Show actual data points alongside or instead of a smoothed trend line. If smoothing is applied, disclose the window size.

### Area Without a Zero Baseline

**What it is:** An area chart whose y-axis does not start at zero.  
**Why it misleads:** The filled area creates a visual impression of total magnitude. A truncated baseline makes that magnitude meaningless.  
**Fix:** Always start area chart y-axes at zero. If the range is narrow and zero wastes space, use a line chart.

### Bubble Area vs. Radius Encoding

**What it is:** Encoding a quantitative value as a bubble’s radius rather than its area.  
**Why it misleads:** Area grows as the square of radius. A value that is 2× larger appears 4× larger visually.  
**Fix:** Always encode values as area. Most charting libraries provide this as a setting. Verify the formula: `radius = sqrt(value / π)`.

### Overplotting (Silent)

**What it is:** Plotting thousands of data points in a scatter chart where most overlap completely, making the actual distribution invisible.  
**Why it misleads:** Dense clusters look like single points; the actual distribution, outliers, and patterns are hidden.  
**Fix:** Alpha transparency, hexbin, contour density, or aggregation based on data volume. See Section 8.

### Cherry-Picked Time Window

**What it is:** Selecting a time range that starts or ends at an advantageous point, making a trend look stronger or weaker than it is across the full period.  
**Why it misleads:** Any time series can be made to show almost any trend by selecting the right window.  
**Fix:** Show the full available time range by default. If a subset is shown, clearly label the start and end dates and explain the selection.

### Unlabeled Uncertainty

**What it is:** Showing point estimates (means, totals, percentages) without communicating uncertainty, error margins, or sample sizes.  
**Why it misleads:** A survey result of 52% vs. 48% looks decisive; if the sample size is 100 and the margin of error is ±10%, it means nothing.  
**Fix:** Add error bars, confidence intervals, or explicit “n =” annotations. For small samples, consider a beeswarm plot over a bar chart.

### Correlation Implies Causation Framing

**What it is:** Titling or annotating a scatter plot or trend chart in a way that implies one variable causes the other.  
**Why it misleads:** Correlation is necessary but not sufficient for causation. Visualizations cannot establish causality.  
**Fix:** Use neutral language: “X and Y tend to move together” rather than “X drives Y.” Note confounding factors when known.

-----

## 11. Chart Library Comparison

### JavaScript Libraries

|Library            |Best for                          |Learning curve|Bundle size |Customization|Accessibility        |
|-------------------|----------------------------------|--------------|------------|-------------|---------------------|
|**Recharts**       |React apps, quick implementation  |Low           |Medium      |Medium       |Good (SVG-based)     |
|**D3.js**          |Full custom, complex charts       |High          |Small (core)|Maximum      |Manual (full control)|
|**Plotly.js**      |Scientific, statistical, 3D charts|Medium        |Large       |Medium       |Good                 |
|**Chart.js**       |Simple charts, fast setup         |Low           |Small       |Low-Medium   |Good                 |
|**Vega-Lite**      |Declarative, grammar-based        |Medium        |Medium      |High         |Good                 |
|**Observable Plot**|Data journalism, quick exploration|Medium        |Small       |High         |Good                 |

**Recharts** is the default recommendation for this application because it is React-native (component-based, not imperative), has excellent documentation, handles responsive design via `<ResponsiveContainer>`, and produces production-quality output with reasonable defaults.

**D3.js** is recommended when the required chart type is not available in higher-level libraries, when animation control is critical, or when the chart must integrate with complex custom DOM interactions.

**Vega-Lite** is recommended when the visualization specification should be data-driven (the chart type itself changes based on data), or when portability across environments matters (Vega-Lite specs render identically in JS, Python via Altair, and R via vegawidget).

### Python Libraries

|Library            |Best for                                         |Integration  |
|-------------------|-------------------------------------------------|-------------|
|**Matplotlib**     |Publication figures, full control, any chart type|Universal    |
|**Seaborn**        |Statistical visualization, built on Matplotlib   |Pandas-native|
|**Plotly (Python)**|Interactive charts, Dash dashboards              |Pandas-native|
|**Altair**         |Declarative, Vega-Lite based                     |Pandas-native|
|**Bokeh**          |Web-embedded interactive charts                  |Pandas-native|

### R Libraries

|Library        |Best for                                              |
|---------------|------------------------------------------------------|
|**ggplot2**    |Publication-quality static charts, grammar of graphics|
|**plotly (R)** |Interactive ggplot2 conversion                        |
|**ggplotly**   |Instant interactivity from ggplot2 objects            |
|**leaflet (R)**|Interactive maps                                      |

-----

## 12. Glossary

**Aspect ratio** — The width-to-height ratio of a chart’s plotting area. Affects slope perception in line charts (banking to 45° is often optimal per Cleveland’s work).

**Bandwidth** — In KDE density plots, the smoothing parameter controlling how much neighboring points influence each position on the curve.

**Binning** — Grouping continuous values into discrete ranges (bins/buckets) for histograms or spatial aggregation.

**Cardinality** — The number of unique values in a column. High-cardinality nominal columns (e.g., user IDs) are generally unsuitable for color encoding.

**Channel effectiveness** — Munzner’s ranked hierarchy of visual encoding channels by perceptual accuracy for quantitative and categorical data.

**Choropleth** — A map visualization where geographic regions are filled with colors encoding a quantitative or ordinal variable.

**Data-ink ratio** — Tufte’s principle: the fraction of a chart’s ink that encodes data. Higher is better.

**Diverging palette** — A color palette designed for data with a meaningful midpoint, using two distinct hues diverging from a neutral center.

**Encoding** — The mapping of a data attribute to a visual property (position, size, color, shape, angle, etc.).

**Faceting** — Splitting a dataset into subgroups and displaying each as a separate, identically-scaled chart panel (small multiples).

**Hexbin** — A 2D binning technique that divides a scatter plot area into hexagonal cells and encodes point count as cell color.

**ISOTYPE** — International System of Typographic Picture Education. A method of communicating statistical data using repeated pictograms where quantity is represented by the number of symbols.

**KDE** — Kernel Density Estimation. A non-parametric technique to estimate the probability density function of a continuous variable.

**Luminance** — The perceived brightness of a color. Luminance contrast is the primary mechanism by which text and graphical elements are distinguished from backgrounds.

**Munzner framework** — Tamara Munzner’s What-Why-How visualization analysis framework from “Visualization Analysis and Design” (2014).

**Nominal** — Data that names categories with no inherent order (colors, countries, product categories).

**Ordinal** — Data with a natural order but without quantifiable intervals (Low/Medium/High, star ratings 1–5).

**Overplotting** — The visual obscuring of data patterns when many points occupy the same or adjacent positions in a chart.

**Pre-attentive attribute** — A visual property processed by the brain’s low-level perceptual system in under 250ms, before focused attention.

**Quantitative** — Numeric data with meaningful arithmetic operations (sums, differences, ratios).

**Sequential palette** — A color palette for ordered quantitative data, progressing from light to dark in a single or smoothly transitioning hue.

**Small multiples** — A grid of small, identical charts each showing a subset of the data. Enables pattern comparison via position rather than color.

**Temporal** — Data representing time (dates, datetimes, durations).

**Tufte principles** — Edward Tufte’s design principles from “The Visual Display of Quantitative Information” (1983): maximize data-ink ratio, eliminate chartjunk, use small multiples, earn the viewer’s attention.

**WCAG** — Web Content Accessibility Guidelines. The international standard for web accessibility, developed by the W3C. Levels A (minimum), AA (standard target), AAA (enhanced).
