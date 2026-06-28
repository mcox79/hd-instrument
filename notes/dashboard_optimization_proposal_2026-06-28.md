# Dashboard optimization proposal 2026-06-28

**Author:** research (dispatched sub-agent)
**Inputs read:**
- `tools/dashboard/server.py` (2620 lines; 38 endpoints — `/api/runs`, `/api/dashboard/v2/*`, `/api/substrate_chat`, etc.)
- `tools/dashboard/static/index.html` (750 lines; single-page vanilla JS; dark theme; 10 sections; 15s polling)
- Live probe of running uvicorn on `http://127.0.0.1:8765`
- Best-practice research: Tufte data-ink + sparklines + small multiples; Shneiderman "overview first, zoom + filter, details on demand"; Grafana drill-down patterns; W&B/MLflow comparison-table UX; WCAG 2.x dark-mode color rules

---

## Audit — current state (Phase 1)

### Existing sections (top-to-bottom)
1. **Header** — CERT N · atoms · refresh time
2. **Headlines** — 4 cards (CERT, commits, in_flight, substrate)
3. **Talk to substrate** — chat window (4 modes: English/structured/substrate-native/walk)
4. **Live experimental data** — running cells per queue (cpu/gpu/local_cpu)
5. **Recent experimental landings** — 15-row history (verdict/mode/wall/when)
6. **Substrate ingest status** — ingested corpora + active + planned
7. **Local processes** — Python procs >10MB or >50s CPU
8. **L3 capability tier** — table from research_master_plan.md
9. **Substrate characteristics** (NEW, testbed 2026-06-28) — 37-row aggregate; expandable
10. **Recent commits** — last 5 git commits

### Top 3 pain points (audit findings)

1. **No "overview-first" health glance.** Per Shneiderman's information-seeking mantra ("Overview first, zoom and filter, then details-on-demand"), the dashboard should answer "is everything OK?" in 1-second. Currently you must scan 4 cards + 3 tables to know if a queue zombied, a session went dark, or an experiment cliff-fell. The `/api/dashboard/v2/health` endpoint EXISTS (lines 1062-1135) with aggregate status OK/WARN/ERROR + drift-detectors, but **the v2 UI doesn't surface it**. Live probe confirms zombie state (`pid_alive=false` `WARNING: ZOMBIE`) is buried in a `title=` tooltip on a row that visually looks like "running".

2. **No per-section freshness indication.** Dashboard polls every 15s, but if the substrate Store hasn't mutated in 4h, no signal tells the user. The `_source_mtime` / `_computed_at` / `_cache_age_s` fields ARE in the API responses but NOT rendered. User must `cat` mtimes externally to disambiguate "fresh state shows nothing" from "stale state shows nothing".

3. **Information-density inefficiency in `Substrate characteristics` tab.** 37 capability rows render inline immediately + expansion panels hold per-test arrays (up to ~25 tests each = ~600 DOM nodes preloaded). Per Tufte's sparkline principle ("data-intense, design simple, word-sized graphics"), a 7-day verdict-distribution sparkline per row would compress the same info into 1/10th the space and let the eye scan for cliffs/trends without expanding each row. Currently the per-row `verdict_distribution` field is fetched but unused in the UI.

### Other findings (lower priority)

- **`/api/dashboard/v2/capabilities_view` returns 404 on the live server** — running uvicorn pre-dates the testbed's endpoint addition. Restart needed. NOT a code bug; ops issue.
- **Negative `elapsed_s` from clock-skew** handled inline in `loadRuns()` (good); a similar fallback needed for `tail_age_s` to surface ZOMBIE state.
- **`history-grid` columns `cell | verdict | mode | wall | when`** — wide cell-name column dominates; verdict color-coding is good (chain-grade green / fail red / middle yellow). No way to sort or filter by verdict.
- **Tooltip-trapped knowledge:** the per-verdict "intuit" tooltip explainer (lines 2196-2208 of server.py) is excellent but hidden behind hover; never visible on first scan.
- **No URL state.** Filters in Substrate characteristics tab (stage/tier/peak/search/show-other/gaps-only) reset on refresh; reload doesn't preserve view.
- **15s polling is unconditional** — even when tab is hidden (no `Page Visibility API` use), wasting CPU + bandwidth.
- **No keyboard shortcuts** — power-user gap (research user checks dashboard 10-50x/day per directive).
- **No "since last visit" highlight** — research dashboards used for overnight checks should highlight NEW landings since user's last open (cf. Rubin Observatory alert pipeline; W&B "new since" markers).
- **Headlines cards have no sparkline trend** — "CERT 590" tells you the number but not "+5 today / -2 demoted". The `motion_7d` data is computed (lines 451-506) but never reaches the UI.
- **Chat window** at the top occupies prime real-estate but is the most-occasional-use feature; should be collapsible or moved.
- **No dark-mode contrast verification** — the categorical colors (#3fb950 success / #d29922 warn / #f85149 error / #58a6ff accent) on `#161b22` card-bg need WCAG-AA verification.

---

## Research highlights (Phase 2)

1. **Shneiderman's mantra** — "Overview first, zoom and filter, then details-on-demand" — applies directly: a top-of-page aggregate panel should answer "is the substrate healthy + are sessions alive + is anything zombied?" in <1 second. The `_compute_substrate_trust` + `_compute_project_health` backend functions already produce this; it's not surfaced.

2. **Tufte's sparklines** — "data-intense, design simple, word-sized graphics" suit per-capability verdict-distribution + 7-day delta perfectly. Inline `<span>` SVG sparklines avoid Chart.js overhead (vanilla-JS stays).

3. **Grafana drill-down + table-with-sparkline pattern** — "Use the time series-to-table transformation to display a time series field in a sparkline ... you can track the overall health of your infrastructure's components in one table." Direct analog: the Substrate Characteristics table becomes a sparkline-grid of capability health.

4. **WCAG AA contrast** — Pure black `#000000` is too harsh; the current `#0d1117` is good (matches GitHub dark). Categorical badges need text + icon (not color-only) — currently rely solely on color, which fails for ~8% of male users with red-green deficiency. **Action: pair tier-color with a 2-letter prefix glyph (CG/MM/HN/EX).**

5. **W&B comparison UX** — "every feature designed around comparing results across runs, users, and time" — implies the history-table needs sortable columns + multi-select for diffing. Lower priority for now (single-user dashboard) but worth banking as a future direction.

6. **"What changed since last visit"** (Rubin Observatory + W&B "new" markers) — store last-visit timestamp in `localStorage`; highlight rows newer than that. Cheap to implement.

---

## Proposal — top 10 changes (Phase 3)

Ranked by `(value × low-effort) / risk`. **Bold** rows ship in Phase 4 of this dispatch.

| # | Change | Rationale | Effort | Risk | Replaces / augments |
|---|--------|-----------|--------|------|---------------------|
| **1** | **Health banner at top of page** — OK/WARN/ERROR pill + 1-line summary (n_dead, n_stale, n_zombie, n_user_pending) from `/api/dashboard/v2/health` | Shneiderman overview-first; backend already exists | ~25 LOC HTML+JS | Low | Augments header |
| **2** | **Per-section "freshness" badges** — "fresh / 2m / 10m / 4h" stamp next to each `<h2>` using `_source_mtime` or section's data mtime | Disambiguates "nothing happening" from "data stale" | ~30 LOC | Low | Augments existing h2s |
| **3** | **ZOMBIE state surfaced in Runs section** — when `pid_alive=false` AND `queue_marks_running=true`, render red badge + tooltip with `warning` field | Currently buried in `title=` tooltip; ZOMBIE is critical | ~10 LOC | Low | Augments existing render |
| **4** | **Verdict-distribution sparkline per row in Substrate Characteristics** — inline 80×16 SVG bar showing HARD_PASS / MIDDLE_BAND / HARD_FAIL counts | Tufte sparklines; data already in `verdict_distribution` | ~40 LOC | Low | Augments existing table |
| **5** | **Tier-glyph prefix (`CG`/`MM`/`HN`/`EX`)** on the tier badge + accessible-by-shape (not color-only) | WCAG color-not-alone | ~5 LOC | Low | Augments existing tier render |
| 6 | "New since last visit" markers — `localStorage.lastVisitTs` highlights history rows newer + count badge | overnight-research UX pattern | ~30 LOC | Low | Augments history section |
| 7 | URL hash for Substrate Characteristics filters (`#stage=2&tier=chain-grade`) — `pushState`/`hashchange` round-trip | Deep-link + reload-survives | ~25 LOC | Low | Augments charcap controls |
| 8 | Page Visibility API — pause 15s polling when tab hidden; resume on focus | Saves CPU + bandwidth | ~15 LOC | Low | Replaces unconditional `setInterval` |
| 9 | Sparkline of CERT-promotion 7d motion in headline CERT card (using already-computed `motion_7d`) | Tufte sparkline in card | ~40 LOC | Low | Augments CERT card |
| 10 | Keyboard shortcuts — `/` focus chat, `r` refresh, `f` focus charcap search | Power-user UX | ~20 LOC | Low | New |

### Open questions for USER

- **Q1: Color scheme?** Current GitHub-dark (`#0d1117` bg, `#58a6ff` blue). Want to keep? Or shift to a non-blue accent so the "blue" peak-glyph in charcap doesn't collide?
- **Q2: Move chat window?** Currently top-center prime real-estate; would you prefer it collapsible (closed-by-default with `▶ Talk to substrate`), or keep open?
- **Q3: Persistent USER preferences (filter state, last-visit ts) in `localStorage` vs server-side?** Default plan = localStorage (zero backend churn). OK?

---

## Implementation status (Phase 4)

**Shipped this dispatch (top 5):**
1. Health banner from `/api/dashboard/v2/health`
2. Per-section freshness badges
3. ZOMBIE-state surfacing
4. Sparkline per Substrate Characteristics row
5. Tier-glyph prefix (CG/MM/HN/EX)

**Deferred (filed for next dispatch or USER input on Q1-Q3 above):**
- 6 (last-visit marker), 7 (URL state), 8 (Page Visibility), 9 (CERT sparkline in card), 10 (keyboard shortcuts)

**Regression-test plan:** all 10 existing tabs continue to load identically with shipped changes; new elements are additive. Cards/tables retain original column structure. No backend endpoints renamed or removed (one helper endpoint `/api/dashboard/v2/health_summary` already exists in source).

---

## Sources

- Edward Tufte, [Sparkline theory and practice](https://www.edwardtufte.com/notebook/sparkline-theory-and-practice-edward-tufte/) — "data-intense, design simple, word-sized graphics"
- Tufte data-ink ratio + small multiples — [Designing efficient dashboards with the Tufte way (Medium)](https://medium.com/design-bootcamp/designing-efficient-dashboards-with-the-tufte-way-9209e79f2ffb)
- Ben Shneiderman — "Overview first, zoom and filter, then details-on-demand" (information-seeking mantra; widely cited)
- [Grafana dashboard best practices](https://grafana.com/docs/grafana/latest/visualizations/dashboards/build-dashboards/best-practices/) — sparklines + drill-down patterns
- [Grafana table panel docs](https://grafana.com/docs/grafana/latest/visualizations/panels-visualizations/visualizations/table/) — sparkline-in-table pattern
- [W&B vs MLflow experiment-tracking UX 2026](https://contracollective.com/blog/weights-biases-vs-mlflow-mlops-experiment-tracking-2026) — comparison-table UX
- [Dashboard Design Principles (UXPin 2026)](https://www.uxpin.com/studio/blog/dashboard-design-principles/)
- [WebAIM contrast & color accessibility](https://webaim.org/articles/contrast/)
- [WCAG color contrast guide 2026](https://www.studiolimb.com/guides/wcag-color-contrast-guide.html) — dark-mode + color-not-alone
- [Designer's guide to dark mode accessibility](https://www.accessibilitychecker.org/blog/dark-mode-accessibility/) — soft-black + tinted-surfaces

---

**End of proposal. See git diff for implementation.**
