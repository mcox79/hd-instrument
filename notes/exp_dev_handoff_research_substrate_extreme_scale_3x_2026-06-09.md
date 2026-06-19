# exp_dev hand-off -- research: substrate extreme scale 3x (depth + population + facts)

Filed-by: research sub-agent (2026-06-09)
Trigger: notes/research_drill_substrate_extreme_scale_3x_2026-06-09.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates,
context pointers, and strategic rationale. exp_dev designs actual anchors, sweep grids,
thresholds, and queue assignment autonomously. Pre-reg bands below are RESEARCH
recommendations -- exp_dev validates and may refine before queue dispatch.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist (or
confirm with orchestrator). Do not ship if paused.

---

## Context summary

Eight empirical anchors are proposed spanning K-hop depth (10/20/50), population ensemble
(N=100/1000), fact-count (1B), and federated K-hop. All are ranked by P_actionable x
compute-cost x strategic leverage. The critical gate is Anchor 1 (DEPTH-10-CHAIN, CPU, 1h,
$0): it determines whether all deeper-K anchors (2, 3) are operating in the feasible regime.
If Anchor 1 hard-fails, Anchors 2 and 3 are not worth running until architecture changes.

Three novel findings from this research cycle (not in prior notes):
1. GHRR block-diagonal gives sqrt(N_predicates) K_max improvement within predicate-bounded
   chains -- a potential 37x gain for FB15K-237 (1345 predicates) at zero algorithmic cost.
2. Population ensemble gain saturates at N=50-100; N=20-50 is the practical optimum
   balancing gain (4-7x noise reduction) against compute cost.
3. Tracy-Widom spectral gap monitoring is a more precise capacity cliff warning than fill_pct;
   the spectral gap alert can be implemented in Component 4 with ~50 LOC.

---

## Anchor Candidates (rank-ordered)

### 1. DEPTH-10-CHAIN (HIGHEST PRIORITY -- gate for all depth anchors)

Anchor pointer: DEPTH-10-CHAIN (new; not yet queued)
Substrate-product reading: Confirms per-hop epsilon at K=10; determines whether K=20 is
  in the feasible regime. Depth-5 recall=1.000 implies epsilon < 0.001; K=10 with that
  epsilon gives 0.990 expected chain success. If chain success < 0.75 at K=10, epsilon
  is 3x higher than expected and all depth extension claims are capped at K <= 8.
Tier hint: Local CPU; ~1h wall; uses existing K-hop harness on current KB (FB15K-237)
Why-now: Cheapest possible gate ($0, 1h). Blocks Anchors 2 and 3. Without this, depth-20
  and depth-50 claims have no empirical grounding. This is the single highest-leverage
  investment of 1 hour in the project.

Pre-reg bands (research recommendation; exp_dev validates):
  HARD-PASS: chain success >= 0.90 at K=10 on FB15K-237 or equivalent KB
  HARD-FAIL: chain success < 0.75 (epsilon > 0.029; all K > 8 claims suspended)
  MID-BAND: 0.75-0.90 (K=15 may be achievable; K=20 is not without epsilon reduction)

### 2. DEPTH-20-CHAIN (HIGH PRIORITY -- requires Anchor 1 HARD-PASS)

Anchor pointer: DEPTH-20-CHAIN (new; not yet queued)
Substrate-product reading: Validates the sparse-KEY K_max gain (GOLD 4.0) at K=20.
  Two conditions: (A) dense intermediates, (B) sparse-KEY intermediates. If sparse >= 1.5x
  dense at K=20, GOLD 4.0 is confirmed in the multi-hop regime (not just single-shard).
  This is the empirical gate for the "K=20 product claim" which is the most directly
  marketable depth extension beyond the current K=12 validated.
Tier hint: Local CPU; ~2h wall; depends on Anchor 1 confirming feasible regime
Why-now: If Anchor 1 passes, this is the next-cheapest gate ($0, 2h). It directly upgrades
  the product claim from K=12 to K=20 if it passes.

Pre-reg bands:
  HARD-PASS: sparse success >= 0.80 at K=20 AND sparse >= 1.5x dense success at K=20
  HARD-FAIL: sparse success < 0.55 OR sparse < 1.1x dense (GOLD 4.0 does not generalize)
  MID-BAND: sparse 0.55-0.80, sparse >= 1.5x dense (K=15 is the new boundary, not K=20)

### 3. POPULATION-N100 (HIGH PRIORITY -- independent of depth anchors)

Anchor pointer: POPULATION-N100 (new; not yet queued)
Substrate-product reading: Tests whether population ensemble gain scales as 1/sqrt(N_pop)
  from N=10 to N=100. Two conditions are essential: (A) same codebook for all copies
  (expected: correlated errors, plateau), (B) different random seeds per copy (expected:
  IID errors, continued gain). This determines the engineering design for production
  ensemble: shared codebook is cheaper (less memory) but may not gain beyond N=10.
Tier hint: Local GPU; ~3h wall; uses existing ensemble infrastructure
Why-now: Independent of depth anchors; can run in parallel with Anchor 1. Directly
  settles the "N=100 ensemble" product claim. P_deflated=0.52 -- moderate confidence
  but outcome bifurcates strongly (plateau vs continued gain).

Pre-reg bands:
  HARD-PASS (Condition B): recall@1 gain vs N=10 >= 3pp additional at N=100
  HARD-PASS (Condition A): recall gain vs N=10 < 1pp (confirms shared-codebook plateau)
  HARD-FAIL: Condition B gain < 1pp (IID model fails; 1/sqrt(N) does not hold for substrate)

### 4. DEPTH-50-CHAIN-STRESS (MEDIUM PRIORITY -- requires Anchor 2 HARD-PASS)

Anchor pointer: DEPTH-50-CHAIN-STRESS (new; not yet queued)
Substrate-product reading: Maps K_max curve empirically by measuring chain success at
  K=30, 40, 50. Tests whether the corrected K_max range (25-44 from GOLD 3.0/4.0) is
  accurate. If K=30 achieves >= 0.50 success, the lower bound K_max=33 is confirmed.
  This is the extreme depth stress test.
Tier hint: Local CPU; ~4h wall; depends on Anchor 2 confirming K=20 regime
Why-now: Only run if Anchor 2 passes AND confirms sparse-KEY K_max gain extends to K=20.
  This converts the theoretical K_max range into a measured K_max point.

Pre-reg bands:
  HARD-PASS: chain success at K=30 >= 0.50 (confirms K_max_corrected >= 33)
  HARD-FAIL: chain success < 0.10 at K=30 (K_max_corrected < 20; additive model is wrong)
  MID-BAND: chain success 0.10-0.50 at K=30 (K_max_corrected 20-33)

### 5. POPULATION-N1000-STRESS (MEDIUM PRIORITY -- requires Anchor 3 confirming IID)

Anchor pointer: POPULATION-N1000-STRESS (new; not yet queued)
Substrate-product reading: Maps ensemble gain curve to N=1000; confirms diminishing
  returns above N=100 (research prediction: < 1pp additional gain from N=100 to N=1000).
  Also measures aggregation latency for N=1000 vote to confirm sub-1ms on GPU batch.
Tier hint: Local GPU; ~4h wall; depends on Anchor 3 Condition B confirming IID behavior
Why-now: Only run if Anchor 3 confirms IID errors under different seeds. If plateau is
  observed at N=100 (Condition A), this anchor is not needed.

Pre-reg bands:
  HARD-PASS: gain from N=100 to N=1000 < 1pp (practical optimum confirmed at N=100)
  HARD-FAIL: gain >= 3pp from N=100 to N=1000 (IID model continues; N=500 may be optimal)

### 6. 1B-FACTS-LATENCY (LOWER PRIORITY -- cloud GPU required)

Anchor pointer: 1B-FACTS-LATENCY (extends prior Anchor E5 from emergent-extreme-scale handoff)
Substrate-product reading: Measures mean + p99 retrieval latency at 100M, 300M, 1B facts
  to confirm O(1) invariance across 10x scale increase. Prior E5 (from emergent-extreme-scale
  handoff, 2026-06-08) covers 10M-100M. This anchor extends to 1B. Together they cover
  4 decades (10M to 10B via extrapolation) and confirm or refute the O(1) scaling law.
Tier hint: Cloud GPU (A100 or GH200 recommended); ~8h wall; ~$50-80 cost
Why-now: This is the gate for all 1B-scale product claims. Recommend only after E2 and E5
  from the prior handoff confirm the architecture holds at 100M scale. Do not dispatch
  this anchor concurrently with the 100M-scale anchors; sequence after those complete.

Pre-reg bands (carried forward from prior E5; extended):
  HARD-PASS: mean latency within 2x of 10M baseline; p99 < 5ms at 1B facts
  HARD-FAIL: latency grows O(log N_facts) from 100M to 1B (retrieval is NOT O(1) structurally)

### 7. GHRR-BLOCK-DIAGONAL-SMOKE (MEDIUM PRIORITY -- novel architecture probe)

Anchor pointer: GHRR-BLOCK-DIAGONAL-SMOKE (new; not yet queued)
Substrate-product reading: Tests whether GHRR block-diagonal encoding within a per-predicate
  shard improves K_max versus flat FHRR at the same shard fill. Research prediction: K_max
  improvement = sqrt(B) where B is the number of blocks per shard (equal to number of
  predicates sharing the shard space). For a 2-predicate block-diagonal: 1.41x K_max.
  This is a zero-code-change probe (toggle the block structure in existing FHRR encoding).
Tier hint: Local CPU; ~2h wall; $0; requires per-predicate KB partition (subset of FB15K-237)
Why-now: If validated, this is the largest unexplored K_max multiplier in the current
  architecture. 37x K_max gain for 1345 predicates is a major product claim upgrade.
  The smoke test at 2 predicates (1.41x) is cheap and decisive.

Pre-reg bands:
  HARD-PASS: K_max(2-block GHRR) >= 1.3x K_max(flat FHRR) at same fill
  HARD-FAIL: K_max(2-block GHRR) < 1.05x flat FHRR (no noise isolation across predicates)

### 8. FEDERATED-SUBSTRATE-2TENANT (LOWER PRIORITY -- v3 feasibility gate)

Anchor pointer: FEDERATED-SUBSTRATE-2TENANT (new; not yet queued)
Substrate-product reading: Tests ZKP-backed cross-tenant K=3 K-hop query at small scale
  (2 tenants, 10K facts each). Measures ZKP proof generation time and total query latency.
  If proof generation > 30s: ZKP approach is infeasible for real-time use; fallback to
  hash-commitment (weaker) protocol required for v3. If < 5s: federated K-hop is viable.
Tier hint: Local CPU; ~6h wall; $0; requires ZKP library (circom + snarkjs or bellman)
Why-now: Blocks the v3 product claim on EU AI Act Article 12 compliance by construction.
  The ZKP feasibility question is load-bearing for v3 architecture decisions. Early
  determination prevents investing in Component 10 (Chain3: 8000 LOC, 45 eng-days) if
  the ZKP overhead makes it infeasible.

Pre-reg bands:
  HARD-PASS: ZKP proof generation < 5s per hop; total K=3 query < 15s (acceptable for
             offline/batch compliance use case)
  HARD-FAIL: proof generation > 30s per hop (ZKP approach infeasible for K > 1; use
             hash-commitment fallback for v3 compliance)
  MID-BAND: 5-30s per hop (acceptable for audit-log-only use case; not real-time)

---

## Context pointers

- Research note (this drill): d:/AI/hd-instrument/notes/research_drill_substrate_extreme_scale_3x_2026-06-09.md
- Prior extreme-scale analysis: d:/AI/hd-instrument/notes/research_drill_substrate_emergent_extreme_scale_5x_2026-06-08.md
- Prior extreme-scale handoff (Anchors E1-E5): d:/AI/hd-instrument/notes/exp_dev_handoff_research_emergent_extreme_scale_5x_2026-06-08.md
- Chain3 GOLD consolidation (K-hop architecture, additive noise, sparse-KEY): d:/AI/hd-instrument/notes/research_drill_substrate_production_scaling_5x_chain3_drill5_FINAL_2026-06-07.md
- Bundle noise K-hop handoff: d:/AI/hd-instrument/notes/exp_dev_handoff_research_bundle_noise_khop_2026-06-07.md
- Depth-5 recall=1.000 empirical: PP row (current PP number to be confirmed in cap_map)
- Population N=10 +12pp empirical: PP row (current PP number to be confirmed in cap_map)
- PP-150 (0.21ms at 1M facts): cap_map
- PP-166 (O(1) scaling validated): cap_map
- PP-200 (1-bit at 100M validated): cap_map

---

## Sequencing recommendation

Parallelizable batch 1 (no dependencies, all $0, both should run immediately):
  - Anchor 1: DEPTH-10-CHAIN (1h CPU)
  - Anchor 3: POPULATION-N100 (3h GPU)

Parallelizable batch 2 (depends on Anchor 1 HARD-PASS):
  - Anchor 2: DEPTH-20-CHAIN (2h CPU)
  - Anchor 7: GHRR-BLOCK-DIAGONAL-SMOKE (2h CPU)

Sequential after batch 2:
  - Anchor 4: DEPTH-50-CHAIN-STRESS (depends on Anchor 2 HARD-PASS; 4h CPU)

Sequential after Anchor 3:
  - Anchor 5: POPULATION-N1000-STRESS (depends on Anchor 3 IID confirmation; 4h GPU)

Cloud (dispatch after all local anchors confirm architecture holds):
  - Anchor 6: 1B-FACTS-LATENCY (8h cloud GPU; ~$50-80)

Deferred (v3 feasibility; can run anytime independently):
  - Anchor 8: FEDERATED-SUBSTRATE-2TENANT (6h CPU; ZKP library required)

---

## Contract section

Research has characterized 3 extreme-scale axes (depth, population, fact-count) with
theoretical bounds, P_deflated estimates, and 8 ranked empirical anchors. The research
note contains hard-pass and hard-fail bands for each anchor. exp_dev is responsible for:
  (1) Validating anchor designs against current substrate harness API
  (2) Refining pre-reg bands based on current empirical baselines
  (3) Assigning to correct queue (local CPU, local GPU, or cloud)
  (4) Not dispatching cloud Anchor 6 until local Anchors 1+3 confirm the architecture
  (5) Treating Anchor 1 as the immediate priority -- 1h CPU, zero cost, gates 3 other anchors

Research does NOT prescribe sweep grids, exact KB configurations, or queue assignments.
Those are exp_dev's autonomous domain per [[feedback-no-experiment-design-in-prompts]].

---

## Autonomy declaration

exp_dev acts autonomously on all 8 anchors subject to pause gate check and sequencing
dependencies above. The most important sequencing constraint is: Anchor 1 before Anchors
2 and 4 (hard dependency); Anchors 3 and 7 can run in parallel with Anchor 1 immediately.
Research does not need to be consulted before dispatch unless a new finding changes the
strategic context or a hard-fail reverses the architecture direction.
