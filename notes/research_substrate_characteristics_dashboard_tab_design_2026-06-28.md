# Design: Substrate Characteristics dashboard tab

**Date:** 2026-06-28
**Directive:** USER 2026-06-28 — add a tab to the dashboard with substrate capabilities in a queryable table; columns: characteristic name + mouseover description / tier / how-good (peak assessment) / phase-diagram coverage. Draw from centralized datastore. Drill first.

## Sources audited

1. `data/substrate_capability_registry.jsonl` — 4449 rows, per-test. Each row: `{anchor_name, verdict, run_mode, axes_tested (dict), per_arm_metrics, stage, capability_family, saturation, cardinality_ok, ts_iso, mtime, elapsed_s, verdict_msg_head}`. Tagged with `stage` (-1/1/2/3/4) and `capability_family` (37 distinct families).
2. `data/substrate_index/atoms.jsonl` — 1 row (sparse). NOT load-bearing for descriptions.
3. `data/recent_landings.jsonl` — 4679 lighter rows. Useful for fallback ts_iso recency but registry already has mtime.
4. `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-06-27.md` UPDATE #22 (Stage 1 portfolio + Stage 2 + Stage 3 audit text; ~line 62-1900).
5. `notes/research_strategic_phase_diagram_framework_all_chain_grade_capabilities_2026-06-27.md` — phase-axes per capability.

## Three load-bearing representation decisions

**1. One row per `capability_family` (NOT per test).** Registry is per-test; aggregation = pick the latest HARD_PASS as canonical tier; aggregate `axes_tested` across all tests in family for phase coverage. Click-to-expand shows per-test array. Rationale: 4449 rows would drown the user; 37 families is scannable. The `stage=-1, capability_family="other"` bucket (2884 rows) is filtered out by default — it's the un-classified backlog and would dominate; a "show unclassified" toggle exposes it.

**2. Tier derived from verdict-mix, not single test.** Heuristic: `chain-grade` = ≥1 HARD_PASS at run_mode=full AND no recent HARD_FAIL since; `measured-mechanism` = ≥1 HARD_PASS at smoke but full HARD_FAIL or saturation=true; `honest-negative` = ≥3 HARD_FAIL with no PASS in last 30d (capability box closed per Wave 2 third-failure-gate convention); else `exploring`. Computed deterministically in the aggregator; surfaced as cell color.

**3. Peak assessment per yesterday's audit color rubric:**
   - 🔵 **saturated default** — observed metric ≥0.95 AND `saturation=true` somewhere in family AND no harder-axis test landed. Means "we hit the ceiling; the easy regime doesn't discriminate."
   - 🟢 **mid-range** — metric in [0.50, 0.95] OR a harder-axis test discriminated.
   - 🟡 **just-above-bar** — metric in [0.30, 0.50] — band-floor results per META_RULE_L.

   Phase-coverage % uses a coarse rubric: count distinct values per axis (across all tests in family), then:
   - ~5%: single point only (0 axes swept)
   - ~25%: one axis with ≥3 distinct values
   - ~50%: two axes with ≥3 values each
   - ~80%: 3+ axes swept and at least one HARD_FAIL boundary observed (cliff found)

   Sort default: `stage ASC, tier (chain-grade-first), phase_pct ASC` — surfaces gaps (low coverage on chain-grade primitives) at top.

## Failure modes the design avoids

- Mouseover descriptions live in **editable** `data/substrate_capability_descriptions.json` — keyed by capability_family; not hardcoded in JS. Default = best-effort summary derived from family name + most-common-axis hints; USER + I can hand-curate over time.
- Click-row expansion shows full per-test array (anchor_name + verdict + run_mode + axes_tested + elapsed_s + ts_iso) — drill-down preserved.
- The aggregator is **idempotent** — runs every 15 min via scheduled task; atomic-write (tmp + replace) so dashboard never reads partial JSON.
- New-since-24h badge: per-family count of tests with mtime in last 24h; surfaces what's actively being explored.

## Filters / search

- Stage dropdown (1/2/3/4/-1)
- Tier dropdown (chain-grade / measured-mechanism / honest-negative / exploring / all)
- Search box on capability_family + anchor_name substring
- Toggle: "show un-classified (stage=-1)" — default off
- Toggle: "phase_pct < 30% only" — gap-surfacing

## Aggregator output schema

`data/substrate_capabilities_view.json`:
```
{
  "generated_at": "<iso>",
  "n_tests_total": 4449,
  "n_capabilities": 37,
  "rows": [
    {"capability_family": "multi_hop_reasoning",
     "stage": 3,
     "tier": "chain-grade",
     "tier_evidence": "anchor_X HARD_PASS @ full, last 24h",
     "peak_assessment": "green",
     "peak_explanation": "best=0.808 depth=15 (un-saturated)",
     "phase_pct": 50,
     "phase_axes_observed": {"N":[1024,8192], "depth":[5,15,30], "V_C":[4000,16000]},
     "n_tests": 262,
     "n_tests_24h": 4,
     "latest_test_ts": "2026-06-28T14:30Z",
     "tests": [/* per-test array */]}]
}
```

## Integration

- Endpoint: `/api/dashboard/v2/capabilities_view` reads + returns the JSON
- New `<section>` "Substrate characteristics" added to existing `index.html` — same `.row-grid` table pattern as existing tabs; sortable column headers; click-to-expand row
- Description mouseover via `title=` attribute (cheap, no JS tooltip lib)
- Scheduled task `hd_substrate_capabilities_aggregate` every 15 min mirrors registry cadence
