# exp_dev hand-off -- research: optimal shard granularity 5x

Filed-by: research sub-agent (Sonnet 4.6), 2026-06-08
Trigger: d:/AI/hd-instrument/notes/research_drill_optimal_shard_granularity_5x_2026-06-08.md
Pause state: check data/orchestrator_paused.flag before dispatching any anchor

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchor candidates,
substrate-product readings, tier hints, and why-now context. exp_dev designs all sweep
parameters, thresholds, queue routing, and pre-reg bands autonomously.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist
(or confirm with orchestrator). Do not ship if paused.

---

## Context summary

Cycle-183 sharding architecture (PP-127..PP-132) validated the horizontal scaling law:
per-shard recall = 1.000 at S=1..256 with zero cross-contamination. This drill addresses
the vertical dimension: optimal per-shard granularity and density.

Key empirical inputs:
- Cycle-178 PP-100: D = M/1.2 linear capacity law (per-shard empirical)
- Cycle-178 iterative_regime_crossover_cpu_v1: rho=0.5 gives recall 0.93 vs rho=0.0 gives 0.80
- Cycle-167/170 sleep-defrag: HP, offline shard reorganization validated, no retraining needed
- PP-129: live overflow shard split (0.16 -> 1.000, no retraining)

Research conclusion: per-subject sharding (current) is correct as a correctness floor;
per-concept semantic-cluster sharding at N=65,536 is the density-optimal tier (500-5,000
facts/shard target); shard MERGE is the missing complement to PP-129 split; sleep-defrag
reclustering via query co-access is the long-term dynamic optimizer.

The dominant capacity lever is N-scaling (~16x from N=4,096 to N=65,536), not semantic
clustering (~1.15-1.30x bonus). Research note explicitly deflates the 2-5x semantic claim.

---

## Anchor candidates (rank-ordered by P_actionable x effort)

### 1. Shard merge primitive (HIGHEST PRIORITY -- complement to PP-129 split)

Anchor pointer: SHARD-MERGE-A1 (new; not yet queued)
Substrate-product reading: If merge works (recall > 0.90 after merging 10 per-subject shards
  of 20 facts each into one 200-fact shard at N=4,096), the substrate has both directions of
  elastic sharding: split (PP-129 HP) and merge (A1). This unlocks the shard utilization
  upgrade path: aggregate under-loaded per-subject shards into concept-level shards overnight.
  At N=4,096, 200 combined facts is comfortably below the N/(2 ln N) safe floor of ~290.
Tier hint: CPU queue; ~1 hr wall; no cloud.
Why-now: PP-129 split was validated at cycle-183. Merge is the natural dual. No prior test
  exists. Low risk -- the 200-fact merged shard is below the safe floor. Clean gate for
  the sleep-defrag reclustering architecture.

Pre-reg bands (research recommendation; exp_dev validates before dispatch):
  HARD-PASS: recall > 0.90 after merge. Merge primitive confirmed; unlock reclustering.
  MIDDLE-BAND: recall 0.75-0.90. Merge works but with headroom reduction; usable with smaller merge ratio.
  HARD-FAIL: recall < 0.75 after merge. W-matrix renorm step has a correctness issue; investigate insertion order or re-use pseudoinverse update.

---

### 2. Per-concept shard capacity validation at N=65,536

Anchor pointer: CONCEPT-SHARD-B1 (new; not yet queued)
Substrate-product reading: Tests the D=M/1.2 law at N=65,536 with semantically-clustered
  (rho=0.5) patterns. If recall > 0.85 at M=5,000 facts, per-concept sharding at production
  N is empirically validated and the per-shard capacity target of 500-5,000 facts is correct.
  M=5,000 is ~26% of the empirical ceiling estimate (19,660 at D_eff=N for N=65,536).
  This is the gate that determines whether the Level-3 N-scaling ladder extrapolates to
  production N.
Tier hint: GPU queue; ~1-2 hr wall; likely needs runner or cloud due to N=65,536.
Why-now: No current experiment has validated D=M/1.2 at N=65,536. The law is established
  at N=4,096 (cycle-178 PP-100 empirical). This extrapolation is the highest-value gap
  in the per-shard capacity model. If it fails, the entire higher-N capacity ladder needs
  recalibration.

Pre-reg bands (research recommendation; exp_dev validates):
  HARD-PASS: recall > 0.85 at M=5,000, N=65,536, rho=0.5. D=M/1.2 extrapolates cleanly.
  MIDDLE-BAND: recall 0.70-0.85. D=M/1.2 holds but with higher constant (C > 1.2).
  HARD-FAIL: recall < 0.70 at M=5,000 OR recall > 0.85 but at M=1,000 only (not scaling
    to M=5,000). Requires re-deriving capacity-vs-N curve at N=65,536.

---

### 3. rho=0.5 vs rho=0.0 capacity comparison sweep (honest capacity bonus measurement)

Anchor pointer: RHO-CAPACITY-C1 (new; not yet queued)
Substrate-product reading: Cycle-178 showed rho=0.5 gives +16% recall AT FIXED M vs rho=0.0.
  But the CAPACITY bonus (how much MORE M can be stored at rho=0.5 before hitting the same
  recall threshold) has NOT been measured. This anchor sweeps M from 100 to 1,000 at N=4,096
  for both rho=0.0 and rho=0.5 and compares the M-at-recall-threshold for each.
  If rho=0.5 allows M=400 at recall 0.90 and rho=0.0 allows only M=300 at recall 0.90,
  the capacity bonus is 1.33x. Research predicts 1.15-1.30x; if > 1.50x the semantic
  clustering pitch gets stronger.
Tier hint: CPU queue; ~1-2 hr wall; M sweep.
Why-now: This directly tests the semantic-clustering capacity claim. Research note deflated
  the 2-5x claim to 1.15-1.30x; this measurement either confirms the deflated estimate or
  falsifies it. A 2x result would motivate accelerating the semantic-cluster sharding
  middleware investment.

Pre-reg bands (research recommendation):
  HARD-PASS: capacity bonus > 1.40x (rho=0.5 stores 40%+ more at same recall threshold).
    Would upgrade semantic clustering from "modest bonus" to "meaningful architecture lever."
  MIDDLE-BAND: capacity bonus 1.10-1.40x. Consistent with research prediction.
  HARD-FAIL: capacity bonus < 1.05x. Semantic clustering provides negligible capacity gain;
    routing cost outweighs benefit; skip semantic-cluster sharding architecture.

---

### 4. Query co-access logging infrastructure (observability primitive)

Anchor pointer: COACCCESS-LOG-D1 (new; infrastructure, not experiment)
Substrate-product reading: Implements per-query (query_id, shard_id) logging for a
  multi-shard workload. Generates a co-occurrence matrix C(A,B) = # queries that hit
  both shard A and shard B. This is the input to Louvain reclustering (Level 5 in
  research note). Even before reclustering, the co-occurrence matrix is a substrate-level
  observability primitive: it shows which shards are semantically related by actual usage,
  independent of any a priori ontology.
Tier hint: CPU; infrastructure code; ~1 eng-day.
Why-now: Zero-cost observability. The co-occurrence matrix is useful even without
  implementing the full dynamic reclustering. Useful for: validating whether per-concept
  cluster assignments from k-means match actual co-query patterns.

---

### 5. Shard utilization histogram (diagnostic)

Anchor pointer: SHARD-UTILIZATION-E1 (new; diagnostic)
Substrate-product reading: For a realistic KG (e.g., the 5,000-entity KG from cycle-183),
  measure the distribution of per-shard fact counts under per-subject sharding. Expected:
  heavy power-law tail (most shards have 1-5 facts; a few have 100+). This histogram
  quantifies the utilization waste from pure per-subject sharding and motivates the
  merge/reclustering investment.
Tier hint: CPU; ~30 min; diagnostic only.
Why-now: Provides concrete utilization numbers for the customer pitch upgrade:
  "Current per-subject sharding uses X% of shard capacity on average; semantic clustering
  raises this to Y%." Without this measurement, the pitch upgrade is theoretical.

---

## Context pointers

- Research note (full drill): d:/AI/hd-instrument/notes/research_drill_optimal_shard_granularity_5x_2026-06-08.md
- Cycle-183 sharding architecture (PP-127..PP-132): notes/orchestrator_to_research_results_summary_2026-06-08_cycle183.md
- Cycle-183 empirical data: exp_dev_to_research_sharding_scaling_law_validated_2026-06-08.md
- Cycle-178 rho=0.5 finding: orchestrator_to_research_results_summary_2026-06-08_cycle178.md
- PP-129 overflow split: cycle-183 finding; PP-129 HP validated
- Sleep-defrag: cycle 167+170 HP
- v1.5 architecture invariant: notes/research_to_exp_dev_v1.5_sharded_KG_architecture_INVARIANT_2026-06-08.md
- D=M/1.2 capacity law: cycle-180 PP-100
- cap_map: d:/AI/hd-instrument/data/cap_map.csv (check before dispatch)

---

## Contract

The research note provides the falsifiable prediction bands and P_deflated estimates for
each anchor. exp_dev is responsible for:
- Designing sweep parameters, N choices, rho values, M ranges independently
- Pre-registering HARD-PASS / MIDDLE-BAND / HARD-FAIL per envelope-fail-bands feedback
- Routing to correct queue (GPU only when torch.cuda required; CPU otherwise per
  feedback-route-gpu-vs-cpu-by-torch-not-N)
- Post-ship remote verification
- Reporting measured capacity values back so verdict_handler can compare to
  research note predictions

## Autonomy declaration

exp_dev has FULL autonomy over anchor naming, sweep design, queue routing, threshold
formulas, and order of dispatch. This file names the WHAT and WHY; exp_dev decides the HOW.
Rank-1 (SHARD-MERGE-A1) is highest priority and cheapest; dispatch first.
