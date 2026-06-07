# exp_dev hand-off -- research: substrate gap native SQL aggregation 3x

**Filed-by:** research sub-agent
**Date:** 2026-06-07
**Trigger:** notes/research_drill_substrate_gap_native_sql_aggregation_3x_2026-06-07.md
**Pause state:** check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchor candidates and
context pointers only. Exp_dev designs the actual experiment scripts.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (TIER-1 CPU SMOKE): hybrid-aggregation-smoke
Why now: cheapest validation of the entire hybrid architecture; confirms Class A (DuckDB),
  Class SA (substrate+DuckDB join), and sync latency in one ~60s smoke run
Substrate-product reading: DuckDB companion is V1 core product component per GOLD finding;
  this smoke gates the decision to promote DuckDB to standard (not optional)
Anchor pointer: implement 3 query classes (S, A, SA) on M=10^4 synthetic facts, N=4096,
  measure latency and correctness per HP-1/HP-2/HP-3 in the research note
Pre-reg bands per note section 6:
  HARD-PASS: Class A <100ms, Class SA correct within 5%, write overhead <15%
  MID: Class SA correct but >200ms
  HARD-FAIL: sync drift >0.5% or Class SA error >50%

### Anchor 2 (TIER-1 CPU SMOKE): hd-aggregation-theoretical-bound
Why now: validates or refutes the Kanerva bundling COUNT theory before it is used in
  any production narrative; cheap to run, eliminates HD-aggregation from consideration
  permanently if HF band confirmed
Anchor pointer: implement Kanerva bundling COUNT on M=[100, 1000, 10^4, 10^5] facts,
  N=[1024, 4096, 16384], measure relative error vs exact DuckDB COUNT
Pre-reg bands per note section 6:
  HARD-PASS (theory confirmed): error in [0.5%, 2.5%] range, monotone in COUNT
  MID: error in [2.5%, 10%] -- theory holds but worse than expected
  HARD-FAIL: error >20% OR non-monotone -- refutes Kanerva concentration claim

### Anchor 3 (TIER-1 CPU, ~5 min): arrow-bridge-overhead
Why now: Arrow zero-copy between PyTorch and DuckDB is Angle 1 in the research note;
  if overhead <10ms per 1000-fact batch, eliminates async write queue from V1 design
Anchor pointer: benchmark torch.Tensor -> Arrow RecordBatch -> DuckDB insert
  using DLPack/Arrow Tensor Exchange; measure per-fact overhead at batch sizes
  [1, 10, 100, 1000, 10000]
Pre-reg bands:
  HARD-PASS: per-fact overhead <0.01ms at batch=1000 (Arrow zero-copy working)
  MID: 0.01-0.5ms per fact (serialization cost; async queue needed above 50k/sec)
  HARD-FAIL: >1ms per fact (Arrow bridge not viable; must use explicit serialize/deserialize)

### Anchor 4 (TIER-2 CPU, ~30 min): rolling-window-aggregation-drift
Why now: validates the drift analysis for HD accumulation under window slides;
  confirms HF-for-HD finding; establishes whether DuckDB or Differential Dataflow is needed
  for streaming windows
Anchor pointer: simulate 365 window slides (daily 30-day rolling SUM) using HD
  accumulation (add/subtract vectors) vs DuckDB incremental, measure drift in both;
  compare to Laplace(sensitivity, epsilon) DP noise floor for reference
Pre-reg bands:
  HARD-PASS for HD: drift grows as O(K/sqrt(N)) matching theory -> HD confirmed broken
  HARD-FAIL for HD: drift is somehow below 0.1% at K=365 -> theory is wrong (surprise)
  HARD-PASS for DuckDB: correct to machine precision for all K

---

## Context pointers

- Research note: notes/research_drill_substrate_gap_native_sql_aggregation_3x_2026-06-07.md
- Chain 2 Drill 3 (DuckDB shadow architecture): notes/research_drill_substrate_developer_experience_5x_chain2_drill3_2026-06-07.md
- Chain 2 Drill 5 (GDPR erasure + sync): notes/research_drill_substrate_developer_experience_5x_chain2_drill5_FINAL_2026-06-07.md
- Datalog honest drill (prior P estimates): notes/research_drill_datalog_substrate_translation_honest_2026-06-07.md
- Production architecture (K-hop + sharding): notes/research_drill_substrate_production_scaling_5x_chain3_drill5_FINAL_2026-06-07.md

---

## Contract

Exp_dev must:
1. Check pause flag before dispatching any anchor
2. Pre-register HP/MID/HF bands per anchor above before coding
3. Run smoke (M=10^4, N=1024) before full scale for Anchor 1
4. Use write_metrics() from _seed_checkpoint for all runs
5. ASCII-only in verdict_msg and print()
6. Report which anchor class (S/A/SA) failed if Anchor 1 does not reach HP

Exp_dev must NOT:
- Design the DuckDB schema without first reading Chain 2 Drill 3 schema spec
- Run full M=10^9 scale without explicit user authorization (cost gate)
- Merge substrate write and DuckDB write in the same transaction (ACID boundary issues at V1)

## Autonomy declaration

Exp_dev owns: script writing, smoke validation, queue dispatch, verdict reporting
Research owns: P estimate updates after empirical results
Orchestrator owns: cap_map row updates, chain continuation decisions
