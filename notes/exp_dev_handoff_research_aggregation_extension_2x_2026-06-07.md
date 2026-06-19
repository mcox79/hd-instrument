# exp_dev hand-off -- research: substrate aggregation extension 2x

**Filed-by:** research sub-agent
**Date:** 2026-06-07
**Trigger:** research_drill_substrate_aggregation_extension_2x_2026-06-07.md
**Pause state:** check data/orchestrator_paused.flag before dispatching

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev designs the experiments;
this file provides anchor candidates and pointers only.

---

## Anchor candidates (rank-ordered)

### 1. Corrected GROUP BY COUNT formula fix (HIGHEST PRIORITY -- 30 min, CPU)

**Why now:** The Cycle 155 a_err=0.9998 was caused by an off-by-N division in the HD COUNT
estimator (divides by N for unit vectors, should not). Fixing one line will likely show
1-3% relative error, changing the cap_map row from "native aggregation fails" to
"approximate GROUP BY COUNT works."

**Anchor pointer:** exp_sql_hybrid_aggregation_v1.py line 60 -- formula fix.
**Substrate-product reading:** Corrects a false negative; restores approximate COUNT capability.
**Tier hint:** CPU smoke, 30 min, single line change.
**Pre-reg bands (research recommendation, exp_dev pre-registers final):**
  HARD-PASS: a_err in [0.000, 0.030] at M=1000, N=4096
  HARD-FAIL: a_err > 0.10 at M=1000, N=4096

### 2. Pattern B exact AVG via stored aggregate facts (2-3 hours, CPU)

**Why now:** Pattern B stores pre-computed aggregates as substrate facts (key="AVG_amount_region_West",
value=precomputed_avg). This gives EXACT AVG/MIN/MAX for templated query types. Highly
product-relevant for dashboard use cases. Cheap to test.

**Anchor pointer:** New experiment -- writes aggregate facts, queries by semantic proximity,
compares retrieved value to DuckDB ground truth.
**Substrate-product reading:** Enables exact aggregation for predefined query schemas.
**Tier hint:** CPU smoke, 2-3 hours, new script.
**Pre-reg bands:**
  HARD-PASS: S_recall >= 0.90 AND value_rel_error < 0.02
  HARD-FAIL: S_recall < 0.70 OR value_rel_error > 0.10

### 3. SA-class AVG validation (extends Cycle 155, 2-3 hours, CPU)

**Why now:** Cycle 155 sa_err=0.0000 for COUNT in SA-class. Need validation that AVG(scalar)
in SA-class works correctly: substrate retrieves top-k semantically-similar fact IDs,
DuckDB computes AVG(amount) over those IDs. This is the core product capability.

**Anchor pointer:** Extend exp_sql_hybrid_aggregation_v1.py to include scalar amount field
and compute DuckDB AVG over semantically-retrieved IDs.
**Substrate-product reading:** Validates the joint semantic+aggregate query moat.
**Tier hint:** CPU smoke, 2-3 hours.
**Pre-reg bands:**
  HARD-PASS: sa_avg_rel_err < 0.05 for k=100 semantic matches at M=1000, N=4096
  HARD-FAIL: sa_avg_rel_err > 0.30 (DuckDB-substrate integration broken)

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_substrate_aggregation_extension_2x_2026-06-07.md
- Prior 3x drill: d:/AI/hd-instrument/notes/research_drill_substrate_gap_native_sql_aggregation_3x_2026-06-07.md
- Cycle 155 metrics: d:/AI/hd-instrument/data/exp_sql_hybrid_aggregation_v1/metrics.json
- Cycle 155 script: d:/AI/hd-instrument/experiments/exp_sql_hybrid_aggregation_v1.py
- HARD_PASS substrate aggregation: d:/AI/hd-instrument/data/exp_substrate_structured_aggregates_v1/metrics.json

---

## Contract

exp_dev owns: pre-registration of specific bands, script design, queue routing, smoke gate.
Research provided: root cause analysis, P_deflated estimates, pre-test design, anchor ranking.
exp_dev does NOT need to re-run the 2x research drill.

## Autonomy declaration

exp_dev may dispatch anchor 1 (formula fix) as a local CPU smoke without further orchestrator
approval -- it is a correction to an existing experiment, not a new direction.
Anchors 2-3 require orchestrator queue-slot authorization if queue depth >= 6.
