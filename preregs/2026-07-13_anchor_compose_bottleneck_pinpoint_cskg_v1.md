# PRE-REG: anchor_compose_bottleneck_pinpoint_cskg_v1 (guardrail-1: confirm the wall BEFORE building)

- **Cell:** `experiments/exp_anchor_compose_bottleneck_pinpoint_cskg_v1.py`
- **Anchor name:** `anchor_compose_bottleneck_pinpoint_cskg_v1`
- **Filed:** 2026-07-13 (exp_dev). **Trigger:** Director hand-off from the reframe drill.
- **Prior-work check (substrate-KB concept-query):** top hits all cosine<0.30 (max 0.2402) -> NONE at cosine>0.30; genuinely novel decomposition, not a rediscovery.

## Question
The aggregate ~0.13 MRR is a degree-stratified MIXTURE, not a uniform representation wall (reframe drill,
on-disk-verified: mid/high-support buckets at 60-133% of their OWN oracle; entire deficit in COLD (0 support, below
random) + D1 (1 support, ~85%-of-oracle headroom)). This DIAGNOSTIC (not a capability chase) decides, per support-degree
bucket (cold=0 / d1=1 / d2_3plus=2+), whether the residual deficit is DECODER/BUDGET-limited, DATA-limited, or a hard
REPRESENTATION wall -- the answer that aims ALL further work.

## Two decisive sub-tests (both stratified into 3 buckets)
- **TEST 2 (decoder/budget-limited?):** sweep the capacity/readout budget k in {24,48,96} (reuse `run_corpus` VERBATIM
  from scaling_ladder_v3; split is seed-determined -> bit-identical query edges across k). Score STRATIFIED per bucket.
  Does D1 anchor_mrr rise toward its bucket-oracle as budget grows?
  - Honest labelling: the frozen-scaffold KGE readout is single-shot nearest-neighbour (no iterative decoder), so
    "decode/readout budget" is realized as the code/fit dimension k. Sweeping k refits per budget (NOT zero-retrain);
    the seed-determined split keeps scored edges bit-identical across k -> clean per-k per-bucket comparison.
- **TEST 3 (data-limited?):** reconstruct the seed-deterministic split, build the TRAIN-graph adjacency, BFS from each
  query-head to the entity's SUPPORT-anchor set (<= 3 hops, train edges only, never the held edge). COLD (empty support)
  = unreachable by construction. Near-zero compute (cold/d1 buckets tiny; d2_3plus capped reference sample).

## Pre-reg bands (picked BEFORE the run; primary metric = FILTERED MRR rank-vs-ALL; NOT tuned on real data)
**Test-2 per-bucket k-trajectory (kmin=24 -> kmax=96):**
- `BUDGET_RECOVERS`: anchor_mrr(kmax)/anchor_mrr(kmin) >= 1.30 AND k-rise closes >= 0.30 of the (oracle-anchor@kmin)
  gap AND abs rise >= 0.002. -> budget/capacity-recoverable.
- `BUDGET_FLAT`: rise ratio < 1.15. -> budget not the lever.
- `BUDGET_MIDDLE`: between. (bucket with < 8 pooled query edges -> INCONCLUSIVE_TOO_FEW.)

**Test-3 per-bucket reachability (reach_frac at H=3):**
- `DATA_LIMITED`: reach_frac < 0.30 (no independent ingested path). `DECODABLE`: reach_frac >= 0.60. `MIXED`: between.

**Per-bucket redirect (the answer):**
- cold: Test3 -> `DATA_LIMITED_EVIDENCE_ABSENT` (expected; 0 support by construction).
- d1: Test2 recovers -> `BUDGET_CAPACITY_RECOVERABLE`; Test2 flat + Test3 data-limited -> `DATA_LIMITED_INGEST_LEVER`;
  Test2 flat + Test3 decodable -> `REPRESENTATION_INFERENCE_WALL`.
- d2_3plus (reference): expect `NOT_BUDGET_LIMITED_NEAR_CEILING` (confirms majority is near its own oracle).

**Fail-closed preamble (any -> INCONCLUSIVE, no bucket verdict trusted):** ORACLE must fire at every k (arena
answerable); cardinality EXPECTED_N_UNITS = n_seeds*len(k_grid) Test-2 units + n_seeds Test-3 passes; no control
(RANDOM/SCRAMBLE) beats the ORACLE ceiling (broken guard, F.4-valid vs the RANDOM floor).

## Compute architecture
class (c) MIXED. Test-2 = run_corpus reused verbatim (additive/rotate/oracle minibatch-SGD fits, batched+neg-chunked;
E_derived index_add_ bundle; query-chunked readout). Test-3 = pure-Python BFS on train adjacency, cold/d1 only + capped
d2_3plus sample -> negligible. SHARDED storage. device=auto (GPU on host -> overnight_queue is the fast target;
k-sweep SGD is GPU-friendly); remote_cpu forces cpu. No memsmoke needed (k<=96 == confirmed scaling-ladder footprint).

## SCHEMA-VET fields
- `cardinality_ok`: EXPECTED_N_UNITS = 2 seeds x 3 k = 6 Test-2 units + 2 reachability passes; HARD_FAIL_CARDINALITY_BREACH_META_RULE_H otherwise.
- `arms_differ_verified`: run_corpus's 7 arms >=5 distinct sigs per (seed,k) (RuntimeError otherwise).
- `final_metrics_atomicity`: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
- `except SystemExit: raise` BEFORE `except Exception` (no BaseException / no bare except) -- grep-gate CLEAN.
- `crlb / info-ceiling`: per-bucket ORACLE is the MEASURED ceiling each bucket's anchor is scored against; diagnostic
  (all 3 outcomes informative; no unreachable HARD_PASS band).
- `baseline_in_band`: ORACLE fires per k; ANCHOR d1 ~0.06 in-band; RANDOM/POP ~1/N floor.
- `discriminator survives scale`: analytical -- per-bucket ORACLE proves each bucket answerable at scale (confirmed
  scaling_ladder); Test-2 trajectory measured at FULL; self-test fires anchor-beats-random + scramble-fails +
  oracle-fires + metric-moves-across-budget deterministically.
- `calibration_check`: adaptive_with_discriminator_gate (ORACLE_FIRE_RATIO/ABS + RISE/GAP_CLOSE/REACH fractions
  pre-registered, NOT tuned on real data).
- `progress_logging`: print_flush_true (line-buffered stdout + per-(seed,k) + per-seed flush prints); timeout_s > 1800.
- `real_code_path_exercised` (F.1): [run_corpus, build_anchor_compose_codes, additive_direct_scores,
  build_heldout_entity_split_ac, reachability_by_bucket].
- `substrate_signature_checked` (F.2/F.3): run_corpus(args=5), build_anchor_compose_codes(args=4),
  additive_direct_scores(args=4), build_heldout_entity_split_ac(args=5) -- base/portable positional args only.
- `guard_baseline_validated` (F.4): BROKEN_TEST_CONTROL_BEATS_ORACLE fires vs ORACLE_best (above floor), validated vs
  RANDOM floor (not POP, structurally ~0).

## MEASURED anchors (off-disk)
- cold anchor_mrr=0.000041 oracle_mrr=0.650751; d1 anchor_mrr=0.059252 oracle_mrr=0.391866; d2_3 0.078897/0.123391
  MEASURED@data/exp_anchor_compose_scaling_ladder_cskg_v3/metrics.json:scaling_summary.rungs.r0_base.anchor_mrr_by_support_degree
- reframe drill CITED@notes/research_drill_reframe_true_bottleneck_2026-07-13.md

## Self-test (VALIDITY_PREFLIGHT_MODE=enforce) -- PASS (15.5s, CPU)
ok=True | anchor_margin=0.39129 | scramble_margin=0.26872 | oracle_fires=True | oracle_across_budget=[0.620,0.932]
(moves) | reach_ok=True | vp_ok=True (all 7 checks). Planted-arena full-style verdict fires:
cold=DATA_LIMITED_EVIDENCE_ABSENT (reach@3=0.0) | d1=REPRESENTATION_INFERENCE_WALL (reach@3=0.714) |
d2_3plus=NOT_BUDGET_LIMITED_NEAR_CEILING.

## Dispatch
Target: **overnight_queue (GPU)** (SGD k-sweep is GPU-friendly). Timeout 14400s (4h). Commit before dispatch.
`bash tools/orchestrator/queue_add.sh overnight_queue anchor_compose_bottleneck_pinpoint_cskg_v1 experiments/exp_anchor_compose_bottleneck_pinpoint_cskg_v1.py preregs/2026-07-13_anchor_compose_bottleneck_pinpoint_cskg_v1.md 14400`
