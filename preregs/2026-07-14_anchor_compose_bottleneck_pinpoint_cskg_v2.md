# Pre-registration: ANCHOR_COMPOSE BOTTLENECK-PINPOINT v2 (tail-oversampled; CSKG held-out-ENTITY)

- **Cell:** `experiments/exp_anchor_compose_bottleneck_pinpoint_cskg_v2.py`
- **Anchor name:** `anchor_compose_bottleneck_pinpoint_cskg_v2`
- **Metrics path:** `data/exp_anchor_compose_bottleneck_pinpoint_cskg_v2/metrics.json`
- **Filed:** 2026-07-14 (exp_dev). **Re-author of** `..._v1` (commit cc8819044) which TIMEOUT-KILLED (14461s>14400s)
  after only seed-7 Test-2; Test-3 + final metrics never persisted; and the natural uniform `n_heldout_eval=3000` draw
  scored only cold=15 + d1=4 tail query edges -> the sparse-tail redirect was UNANSWERABLE.
- **Target queue:** `overnight_queue` (GPU; device=auto->cuda, the k-sweep SGD fits are GPU-friendly).
- **Dependency (MUST land on remote with this cell):** `experiments/exp_anchor_compose_scaling_ladder_cskg_v3.py` was
  edited to add a BACKWARD-COMPATIBLE `query_selector=None` kwarg to `run_corpus` (base positional signature unchanged;
  every existing caller keeps identical behavior). Both files are in the same local commit.

## Question (the redirect this must produce)
Per bucket (cold=0-support / d1=1-support / d2_3plus=2+), is the residual deficit DECODER/BUDGET-limited (Test-2:
k-budget recovers the bucket toward its own oracle), DATA-limited (Test-3: the held-out answer is graph-UNREACHABLE
from the entity's support via TRAIN edges), or REPRESENTATION-limited (neither)? This decides where all further
`anchor_compose` work aims. The confirmed bottleneck IS the sparse tail, so the tail buckets MUST be conclusively
sampled.

## Three fixes (all three, this cell)
1. **OVERSAMPLE THE TAIL (crux).** Replace the uniform 3000-draw with a STRATIFIED query-edge SELECTOR
   (`make_tail_oversample_selector`, passed to `run_corpus`'s new `query_selector` kwarg): take ALL cold + ALL d1 +
   a capped `D23_CAP=2000` reference sample of d2_3plus. The SPLIT is bit-identical to the scaling-ladder v3 arena
   (held-out entities tail-only, support/query disjoint, seed-deterministic); ONLY which held-out query edges get
   SCORED changes -> leak-free. Buckets by support-EDGE count per tail (matches `build_anchor_compose_codes`).
   MEASURED tail supply (split-only diagnostic, no fit, 2026-07-14, VERIFIED on real CSKG core):
   - seed7 SELECTED nq=2253: cold=154 d1=99 d2_3plus=2000
   - seed13 SELECTED nq=2264: cold=180 d1=84 d2_3plus=2000
   - **POOLED over 2 seeds: cold=334 d1=183** (both >> the ~150-300 target and >> MIN_BUCKET_Q=8; conclusive by
     construction, not a natural-draw gamble). MEASURED@scratchpad selector-verify 2026-07-14.
2. **RUN + PERSIST TEST-3.** Reachability BFS (~13s/seed, MEASURED) runs per-seed BEFORE the k-sweep and is
   `write_partial`'d immediately, so a late timeout cannot lose it. cold = unreachable by construction; the KEY new
   signal is d1 reachability.
3. **FIT THE COMPUTE BUDGET + RESUME.** (a) K_GRID cut to `{24,96}` -- the per-bucket classifier reads ONLY
   `traj[kmin]` + `traj[kmax]`, so dropping the illustrative k=48 loses ZERO verdict info while cutting fits 6->4.
   (b) 2 seeds `[7,13]` unchanged (needed for pooled tail n + cross-seed robustness). (c) CHECKPOINT-RESUME: every
   completed `(seed,k)` Test-2 unit + per-seed Test-3 reach is loaded from `partial_metrics_*.json` if present, so a
   re-dispatch after ANY kill CONTINUES instead of restarting. **Timeout = 32400s (9h)** -- headroom over the task's
   >=28800 floor given the prior 4h-was-too-low kill + any CPU-fallback risk (4 CPU fits est ~20660s
   THEORETICAL@ v1 seed-7 3-fit 14461s scaled 168->120 by-k; << 32400). GPU expected far faster; resume covers overflow.

## Pre-registered bands (primary metric = FILTERED MRR; picked BEFORE the run; NOT tuned on real data)
**Test-2 per-bucket k-trajectory (kmin=24 -> kmax=96), applied to the ANCHOR_COMPOSE arm per bucket:**
- **BUDGET_RECOVERS**: `anchor_mrr(96)/anchor_mrr(24) >= D1_RISE_RECOVER(1.30)` AND the rise closes
  `>= D1_GAP_CLOSE_RECOVER(0.30)` of the `(oracle_mrr - anchor_mrr(24))` gap AND `abs_rise >= MIN_SIG_MRR(0.002)`.
- **BUDGET_FLAT**: `rise_ratio < D1_RISE_FLAT(1.15)`.
- **BUDGET_MIDDLE**: between the two.
- **INCONCLUSIVE_TOO_FEW**: pooled bucket n `< MIN_BUCKET_Q(8)` (NOT expected at the tail given FIX-1 supply).

**Test-3 per-bucket reachability (reach_frac at REACH_H=3 hops, train graph, excludes held edge):**
- **DATA_LIMITED**: `reach_frac(3) < REACH_DATA_FRAC(0.30)` (most queries have NO independent ingested path).
- **DECODABLE**: `reach_frac(3) >= REACH_DECODE_FRAC(0.60)` (signal present; mechanism not using it).
- **MIXED**: between.

**Per-bucket redirect (the fused answer -- see `_bucket_redirect`):**
- **cold**: Test-3 -> `DATA_LIMITED_EVIDENCE_ABSENT` (expected; 0 support by construction) | `DECODABLE_BUT_UNSCORED_ANOMALY` (flag).
- **d1 (decisive)**: Test-2 `BUDGET_RECOVERS` -> `BUDGET_CAPACITY_RECOVERABLE`; else Test-3 adjudicates:
  `DATA_LIMITED_INGEST_LEVER` | `REPRESENTATION_INFERENCE_WALL` | `MIXED_DATA_AND_REPRESENTATION`.
- **d2_3plus (reference)**: Test-2 flat/middle -> `NOT_BUDGET_LIMITED_NEAR_CEILING` (expected, the reframe finding);
  `BUDGET_RECOVERS_UNEXPECTED` (flag, contradicts reframe).

**Fail-closed preamble (any -> INCONCLUSIVE overall, no bucket verdict trusted):**
- `enough_heldout`: every Test-2 unit `n_query_scored >= MIN_HELDOUT(20)` (FIX-1 gives ~2250; always true).
- `oracle_fires_all`: ORACLE clears the ceiling-aware ratio(>=3x)+abs(>=0.003) gate at every k (arena answerable).
  This IS the discriminator-survives-scale proof (analytical option B): the per-bucket ORACLE is the MEASURED ceiling
  the anchor trajectory is scored against; if it does not fire at FULL, the run is INCONCLUSIVE_ORACLE_UNDERFIT.
- `broken_any`: no control (RANDOM/SCRAMBLE) beats ORACLE_best by > CONTROL_LOSE_EPS -> `BROKEN_TEST_CONTROL_BEATS_ORACLE`.
- cardinality `EXPECTED_N_UNITS = n_seeds*len(k_grid) = 2*2 = 4` Test-2 units + 2 Test-3 passes (META_RULE_H).

## Compute architecture
class (c) MIXED. Test-2 = run_corpus VERBATIM (batched minibatch-SGD fits + query-chunked batched-matmul readouts);
the v2 selector = deterministic pure-Python leak-free index selection; Test-3 = pure-Python BFS on tiny cold/d1 buckets
+ capped d2_3plus reference. SHARDED storage. device=auto (cuda on GPU host); remote_cpu forces cpu. No MEMSMOKE needed
(k<=96 same footprint family as the confirmed k=24 scaling ladder that ran overnight); discriminator-fires proven by
the self-test + the analytical oracle-fires FULL gate.

## Validity-preflight (7 checks; F.1-F.4 = ENFORCE) -- SELF-TEST PASSED
positive_control (ORACLE recovers+fires) | metric_moves (oracle mrr moves across budget) | negative_control_margin
(RANDOM+SCRAMBLE below ANCHOR, >=2) | full_gates_exercised (aggregate verdict fires every fail-closed gate) |
real_code_path F.1 (self-test runs run_corpus WITH the tail-oversample selector + reachability BFS on REAL objects at
>=2 budgets) | substrate_signature F.2/F.3 (run_corpus/build_anchor_compose_codes/additive_direct_scores/
build_heldout_entity_split_ac bind live sigs, base/portable positional args; query_selector is OPTIONAL so args_count=5
unchanged) | guard_baseline_valid F.4 (broken guard fires vs ORACLE_best above the RANDOM floor, not POP).

## SMOKE VERDICT (self-test on planted TransE arena, CPU single-thread, 17.7s)
`ok=True SELFTEST_PASS`: anchor_margin=0.39129, scramble_margin=0.26872, oracle_fires=True,
oracle_across_budget=[0.62037, 0.93169] (metric MOVES), tail_n={cold:10, d1:5, d2_3plus:46} (selector oversampled the
tail), reach_ok=True, validity_preflight_ok=True.
MEASURED@data/exp_anchor_compose_bottleneck_pinpoint_cskg_v2_selftest/metrics.json.
Selector on REAL CSKG core VERIFIED (split+select, no fit): seed7 cold=154/d1=99/d23=2000, seed13 cold=180/d1=84/d23=2000.

## Dispatch (REMOTE -> handed to orchestrator; exp_dev does not SCP)
```
bash tools/orchestrator/queue_add.sh overnight_queue anchor_compose_bottleneck_pinpoint_cskg_v2 \
  experiments/exp_anchor_compose_bottleneck_pinpoint_cskg_v2.py \
  preregs/2026-07-14_anchor_compose_bottleneck_pinpoint_cskg_v2.md 32400
```
NOTE to orchestrator: the edited `exp_anchor_compose_scaling_ladder_cskg_v3.py` (new `query_selector` kwarg) MUST be on
the remote runner's code (git push OR sync) before this cell runs, else `run_corpus() got an unexpected keyword
argument 'query_selector'` at the remote. Both files are in the same local commit.
