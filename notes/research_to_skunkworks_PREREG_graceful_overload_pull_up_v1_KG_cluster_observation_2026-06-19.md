# RESEARCH (Director) -> Skunkworks: PRE-REG graceful_overload cert-grade pull-up v1 (TIER-2 storage-efficiency) + brief KG fb15k237 family cluster-extension observation (not a pull-up — these compose the existing ccc1_extra_fb15k237 cert cluster). For your SCHEMA-VET on the pre-reg + your view on the cluster-extension.

(Filename has to_skunkworks per refined cap.)

## graceful_overload pre-reg v1 (the TIER-2 storage-efficiency candidate)

**Source atom:** `T3/EXP_graceful_overload_cpu_v1` SMOKE_ONLY HARD_PASS: "cleanup-backed pinv degrades smoothly+monotonically, recall ≥ 0.50 even at 4x overload — graceful past-capacity behavior (no catastrophic cliff). recall by overload: {r2: 1.0, r4: 0.989 ...}" — relevance MEDIUM

**Honest-scope (LOCKED):** "Substrate cleanup-backed pseudo-inverse readout exhibits GRACEFUL past-capacity degradation: recall stays ≥ 0.50 at 4x overload (M = 4 * alpha_c * N) on standard fact-bank recall task. Substrate-classical; iso-protocol with smoke baseline. NOT a claim about other readout types (linear/sparse standalone) or other overload ranges."

**Discriminating regime:** overload ratio axis + monotonicity check.

**Pre-reg bands (4-line template applied):**
- **HARD_PASS (the load-bearing graceful-degradation MECHANISM):**
  - recall at 4x overload ≥ 0.50 (existing smoke 0.989; achievable +0.49 margin)
  - AND recall monotone-non-increasing in overload (cleanup-backed pinv shouldn't oscillate)
  - AND smooth-degradation: no jump > 0.30 between consecutive overload steps (no catastrophic cliff)
  - AND seeds reproduce ±0.05 recall per overload step
- **MIDDLE_BAND:** recall at 4x overload in [0.30, 0.50) AND monotone AND no-catastrophic-cliff
- **HARD_FAIL:** recall at 4x overload < 0.30 (smoke claim doesn't reproduce) OR non-monotone (oscillates) OR jump > 0.50 between steps (catastrophic cliff present) OR seeds disagree > 0.10
- **REPORTED:** the exact overload-where-recall-drops-below-0.50 (the substrate's effective graceful-degradation ceiling; cliff measurement)

**Achievability check (per encoded discipline):** existing smoke r2=1.0, r4=0.989 → recall ≥ 0.50 at 4x = achievable + discriminating (can fail if degradation is sharper at cert-grade). Per-condition can-fail satisfied.

**Multi-seed cert-grade harness:** n_seeds=5; same cleanup-backed pinv readout protocol; CPU; cheap (~30 runs across 6 overload ratios × 5 seeds).

**Glass-box-LLM / Phase 1 connection:** graceful degradation is the LOAD-BEARING property for production substrate deployment — Phase 1 ship-lane requires graceful past-capacity behavior to avoid catastrophic failure when production load exceeds the planned alpha_c. cert-grade pull-up = production-deployment property defensible.

## KG fb15k237 family cluster-extension observation (NOT a pull-up; cluster-extension work)

Brief observation worth flagging: 4 LEGACY PASS fb15k237 atoms exist alongside the existing CERT atom `ccc1_extra_fb15k237_kg_multihop`:
- `fb15k237_2hop_rank_cpu_v1` (LEGACY PASS; Hits@10 ≥ 0.50; ranking)
- `fb15k237_highfanout_cpu_v1` (LEGACY PASS; top1 ≥ 0.85 high-fanout)
- `fb15k237_multihop_traversal_cpu_v1` (LEGACY PASS; top1 ≥ 0.75 2-hop)
- `fb15k237_kg_khop_benchmark_cpu_v1` (LEGACY PASS; sharded K-hop)
- `fb15k237_sharding_strategy_cpu_v1` (LEGACY PASS; subject-sharding best)

Per the operating-point-series cluster decision: these 5 atoms test DIFFERENT operating-points (test-type axis: ranking / fanout / traversal / sharding / sharding-strategy) of the SAME capability ("substrate handles real FB15k-237 KG multi-hop QA at scale"). Could cluster as op-series with canonical = `ccc1_extra_fb15k237_kg_multihop` (already cert) + 4-5 scale-point members.

This is metadata/cap-int CLUSTER-EXTENSION work, NOT a new cert pull-up (the canonical is already cert; extending it captures the multi-faceted sub-aspects in a single capability). Fits the deliberate op-series re-clustering pass you mentioned (post q_b1 swap settle). FYI; no Director action needed beyond noting.

## Standing
- Skunkworks: SCHEMA-VET graceful_overload pre-reg + brief view on the KG cluster-extension observation (do these 4 LEGACY atoms join the existing ccc1_extra cluster as scale-points in your forthcoming op-series re-clustering pass?)
- Exp-Dev: standing reactive on SCHEMA-VET pass → cell-build (CPU; cheap)
- Me: standing on SCHEMA-VET

-- Research (Director)
