# Pre-registration: ANCHOR_COMPOSE inductive entity-generalizing map-builder (CSKG held-out-ENTITY)

- **Cell:** `experiments/exp_anchor_compose_inductive_entity_cskg_v1.py`
- **Anchor name:** `anchor_compose_inductive_entity_cskg_v1`
- **Metrics path:** `data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json`
- **Filed:** 2026-07-12 (exp_dev). **Upgraded:** 2026-07-12 (exp_dev) -- ceiling-aware, degree-unbiased multi-metric
  eval (the INFO-CEILING fix). **STAGED / READY-HELD**; do NOT `queue_add` -- the Director fires the FULL.
- **Ceiling fix rationale:** the fork (`exp_course_c_heldout_entity_inductive_probe_gpu1024_v2`) landed
  `INCONCLUSIVE_ORACLE_UNDERFIT` NOT because the arena is unanswerable but because the fire-gate
  (`ORACLE - RANDOM >= 0.10` on hits@10-vs-all-25.7k) was **copied from the easier held-out-EDGE arena** (oracle
  fired 0.107 there) WITHOUT computing THIS arena's info-ceiling. MEASURED off-disk
  (`data/exp_course_c_heldout_entity_inductive_probe_gpu1024_v2/metrics.json`): ORACLE **mrr=0.01280** vs RANDOM
  **mrr=0.00039** = a **32.8x** separation (arena IS answerable) but hits@10 headroom only **0.0139** (below the 0.10
  gate; even PERFECT codes score ~0.014 hits@10 vs all 25.7k candidates). 2.5x-ing epochs (v1 0.0123 -> v2 0.0143)
  barely moved it: NOT epoch-underfit, an ARENA/METRIC ceiling. This upgrade computes the ceiling in-run and gates
  RELATIVE to it, so ONE FULL yields (a) which metric makes the oracle fire and (b) does ANCHOR beat the 0.0
  memorize arms under that metric.

## Prior-work check (mandatory)
`bash tools/substrate_query.sh "anchor compose inductive entity held-out bundle relation operator neighbor
zero-training map builder"` -> top hit cosine **0.2793** (generic composition-operator notes), **NONE at
cosine>0.30**. ANCHOR_COMPOSE (zero-training held-out-entity code as an additive bundle of relation-operator-bound
anchor-neighbour estimates) is genuinely novel on this substrate, not a rediscovery.

## Question
Does a ZERO-training entity representation -- a new entity's code built as the degree-invariant additive BUNDLE of
its support edges' relation-operator-bound anchor estimates, `E_derived[t] = mean_i (X[h_i] + D[r_i])` -- let the
substrate rank held-out-ENTITY edges (entities absent from every train edge) above a random-code control AND above
the per-entity-fit (memorize) arms on the SAME unseen entities?

## Mechanism / construction
- Reuse the native additive store geometry (`fit_kge_anchor1` -> `X` anchor codes, `D` per-type relation operators;
  `additive_direct_scores` readout). Operator = **ADDITIVE, not rotation** (VET skunkworks a7688ea3: on the fair
  held-out test additive beats rotation and rotation's win is popularity/degree-confounded; additive is the
  degree-invariant / geometric code). CITED@notes research_inductive_entity_generalizing_factorized_map_builder_2026-07-12.
- `X`, `D` are the FROZEN scaffold, trained ONLY on both-seen train edges. `E_derived` is pure arithmetic computed
  AFTER the fit is frozen, from a held-out entity's OWN test-time-visible SUPPORT edges -> genuine zero-shot, no
  leakage (SUPPORT and QUERY edges are disjoint per held-out entity).
- ANCHOR_COMPOSE and the ADDITIVE_TRANSE memorize control SHARE the SAME additive fit (X,D); the ONLY difference is
  whether a held-out entity's code is the anchor-composed bundle (inductive) or its random-init table row (memorize)
  -> isolates the entity-representation mechanism to a single knob.

## Arms (7; scored PAIRED on the SAME held-out QUERY edges + candidate set)
| arm | held-out entity code | role |
|---|---|---|
| ANCHOR_COMPOSE | additive fit; code = E_derived bundle | MECHANISM |
| ADDITIVE_TRANSE | same additive fit; code = random-init row | per-entity-fit memorize control (direct comparison) |
| ONESHOT_ROTATE | rotation fit; code = random-init | 2nd memorize control (functional-form variety) |
| RANDOM_CODES | random X + random D | null (the bar) |
| ANCHOR_SCRAMBLE | E_derived with support relation ids SCRAMBLED | must-fail (degree/anchor-identity confound control) |
| ORACLE_ADDITIVE | additive fit with held-out folded in (codes learned) | positive control / arena-answerable |
| BASELINE_POP | frequency incumbent | fit-independence sanity |

## Ceiling-aware metric set (the info-ceiling fix)
Every arm is scored under the **full FILTERED rank spectrum, rank-vs-ALL-N candidates** (the KGE standard; other true
tails of the same `(h,r)` masked): **hits@{1,3,10,100} + MRR**. The scoring is **DEGREE-UNBIASED**: it ranks against
ALL candidates, with **NO sampled-negative pool** -- a uniform-negative pool would reintroduce the popularity/degree
bias that the in-flight degree-debias cell is removing, so it is deliberately NOT used (the ceiling under rank-vs-all
is already the fair best-possible; a sampled pool would only inflate it with a known bias). **Primary metric =
FILTERED MRR** (smooth, uses the full rank distribution, standard, degree-unbiased). The per-arm spectrum + a
per-metric `oracle_fire_by_metric` table are written to `gates` = the info-ceiling made explicit.

## Pre-registered bands (primary metric = FILTERED MRR; `H` = MEASURED oracle headroom `= ORACLE_mrr - RANDOM_mrr`; picked BEFORE the run)
Bands are **CEILING-RELATIVE** (fractions of the in-run-measured `H`) so ONE FULL computes the ceiling AND scores
ANCHOR against a fair fraction of it -- no hardcoded absolute margin copied from another arena.
- **ORACLE-FIRES** (arena answerable): `ORACLE_mrr >= 3x RANDOM_mrr` (scale-free ratio) **AND**
  `ORACLE_mrr - RANDOM_mrr >= 0.003` (non-noise absolute floor at nq>=3000). Replaces the copied `0.10`-hits@10 gate.
  MEASURED fork ratio = **32.8x** -> fires. The `oracle_fire_by_metric` table reports which metric fires.
- **HARD_PASS** (`HARD_PASS_INDUCTIVE_ANCHOR_COMPOSE`): `(ANCHOR - RANDOM)_mrr >= max(0.50*H, 0.002)` (recovers >=50%
  of the oracle's achievable rank-headroom) **AND** `(ANCHOR - max(ADDITIVE, ONESHOT))_mrr >= 0.10*H` (beats the
  memorize arms) **AND** ORACLE fires **AND** scramble controlled (`(SCRAMBLE - RANDOM)_mrr <= 0.25*H`) **AND** not
  broken **AND** the anchor MRR margin holds on the low+mid degree stratum (fair, non-super-hub; P1 skew).
- **MIDDLE_BAND**: `(ANCHOR-RANDOM)_mrr >= 0.20*H` but not HARD_PASS (form-margin short, scramble/degree confound, or
  fair-stratum fails). Localize via the anchor-support-degree stratification.
- **HARD_FAIL** (`HARD_FAIL_ANCHOR_COMPOSE_NO_TRANSFER`): `(ANCHOR - RANDOM)_mrr < 0.20*H` with ORACLE firing (a
  genuine negative: the right-shaped construction fails on CSKG -> localize to sparsity vs crosstalk).
- Gated **INCONCLUSIVE** if ORACLE does not fire (arena not answerable), `< 20` held-out queries, or a null beats POP
  by `> max(0.005, 0.25*H)` mrr (broken; ceiling-relative so it does not false-trip when POP is at the structural
  held-out floor).
- HP_SCOPE: the inductive HARD_PASS gates apply to **ANCHOR_COMPOSE only**. ORACLE = positive control (must fire);
  RANDOM/ANCHOR_SCRAMBLE = must-not-clear-bar controls; ADDITIVE_TRANSE/ONESHOT_ROTATE = memorize head-to-heads;
  POP = fit-independence sanity.

## Weak-point localization (first-class per cell)
Three stratifications of the mechanism vs controls, reported in `per_seed[*].localization`:
1. **anchor-support degree** bins {cold(0), d1, d2_3, d4_7, d8+} -- does the margin scale with support (SNR ~ local
   degree, GrapHD `5 log(D/d)`)? Cold = the sparse-entity failure mode.
2. **global-degree tertile** (low/mid/high) + `fair_low_mid` -- super-hub vs tail (P1 skew max/mean=164; MEASURED@
   data/exp_cskg_graph_structure_diagnostic_v1/metrics.json:gates.p1).
3. **relation tertile** (hardest vs rest) -- HARDEST set = the diagnostic's cardinality-heavy hardest_tertile
   (isa/synonym/similarto/usedfor/hascontext/antonym/...; CITED@same diagnostic:diagnostic.hardest_tertile).

## Four validity-preflight checks (declared in the self-test via experiments._validity_preflight)
1. **positive_control_passes**: ORACLE_ADDITIVE recovers planted held-out tails and clears RANDOM by the ceiling-aware ratio+abs fire gate on MRR.
2. **metric_moves**: held-out MRR MOVES across [RANDOM, ADDITIVE_TRANSE, ANCHOR_COMPOSE, ORACLE].
3. **negative_control_margin**: RANDOM + ANCHOR_SCRAMBLE sit below ANCHOR by margin, deterministically (>=2 vals).
4. **full_gates_exercised**: `aggregate_and_verdict` runs on the planted per-seed, firing every fail-closed gate.

## Self-test (MEASURED, local .venv, single-thread CPU, 10.5s) -- PASS
Planted HIGH-intrinsic-dim TransE-consistent arena (`build_planted_transe_arena`, n_ent=300, n_rel=6, k_lat=8,
deg=3) where the RELATION operator is NECESSARY (no smooth low-dim embedding, so plain neighbour-averaging fails).
MEASURED@data/exp_anchor_compose_inductive_entity_cskg_v1_selftest/metrics.json:mechanism_selftest:
- held-out **MRR** (primary): **ANCHOR=0.4047, ADDITIVE=0.0047, ONESHOT=0.0182, RANDOM=0.0134, SCRAMBLE=0.1360,
  ORACLE=0.9317, POP=0.0083**; anchor_margin(MRR)=**0.391**, scramble_margin(ANCHOR-SCRAMBLE, MRR)=**0.269**,
  oracle ratio=**69.6x**; 7 distinct sigs; `validity_preflight_ok=True`; verdict=**SELFTEST_PASS**.
- held-out hits@10 (legacy display): ANCHOR=0.656, ADDITIVE=0.000, ONESHOT=0.033, RANDOM=0.000, SCRAMBLE=0.262,
  ORACLE=1.000, POP=0.000.
- **which metric fires the oracle** (`oracle_fire_by_metric`, planted arena): hits@1 / hits@3 / hits@10 / hits@100 /
  **MRR all fire** (`fires_ratio=True`) -- the planted arena registers strong signal under every metric, proving the
  ceiling-relative bands are ACHIEVABLE-in-principle when the entity code exists/can be composed.
- The construction RECOVERS a planted held-out entity's edges ZERO-training (MRR 0.405 vs random 0.013); the
  relation-scramble must-fail FIRES with margin (0.269 MRR); the additive ORACLE fires (arena answerable).
- Internal `aggregate_and_verdict` on the planted seed = **MIDDLE_BAND_PARTIAL_ANCHOR_TRANSFER** (ANCHOR recovers 42%
  of `H` on the planted arena -> below the 50% HARD_PASS fraction; band gate exercised, not short-circuited).
- Note: on a 2D grid the scramble did NOT fail (neighbour-averaging recovers a spatially-smooth target without the
  relation) -- the planted arena was redesigned to high intrinsic dim so the relational signal is provable.

## Which metric fires the oracle on the REAL arena (MEASURED off-disk, fork)
On the real CSKG held-out-entity arena (fork metrics), under the upgraded ceiling-aware gate:
- **MRR (primary): ORACLE 0.01280 vs RANDOM 0.00039 = 32.8x, headroom 0.01241 -> FIRES** (>=3x and >=0.003).
- hits@10 by the ratio gate: 0.01433 vs 0.00045 = 31.8x -> fires by ratio; but the **legacy absolute 0.10-hits@10
  gate does NOT fire** (headroom 0.0139) -- this is exactly the info-ceiling artifact that made the fork INCONCLUSIVE.
- hits@100 was not computed by the fork; the upgraded FULL will report it (expected the clearest-firing metric).
- **Headline: FILTERED MRR (ceiling-aware ratio gate) makes the oracle fire; the copied absolute 0.10-hits@10 gate
  did not.** The arena is answerable; the fork's INCONCLUSIVE was a metric artifact, not a substrate wall.

## SCHEMA-VET / cell-template fields
```json
{
  "cell": "experiments/exp_anchor_compose_inductive_entity_cskg_v1.py",
  "anchor_name": "anchor_compose_inductive_entity_cskg_v1",
  "arms_differ_verified": true,
  "arms_differ_note": "7 arms; self-test measured 7 distinct score signatures (>=5 gate)",
  "final_metrics_atomicity": "tmp_replace",
  "cardinality_ok": true,
  "EXPECTED_N_UNITS": "n_seeds (per-seed all-7-arms + >=5 distinct sigs asserted; HARD_FAIL_CARDINALITY_BREACH_META_RULE_H on shortfall)",
  "crlb_floor_computed": 0.0004,
  "crlb_formula_reference": "chance hits@10 = k/N = 10/25752 ~ 0.0004; INFO-CEILING: filtered hits@10-vs-all-N caps ~0.014 even for the ORACLE at N~25.7k (MEASURED fork) -> raw hits@10 unusable; primary metric switched to FILTERED MRR + ceiling-RELATIVE bands",
  "discriminator_reachability": true,
  "discriminator_reachability_note": "bands are FRACTIONS of the MEASURED oracle MRR headroom H (in-run), not fixed absolutes -> reachable by construction whenever ORACLE fires; ORACLE fires under MRR at 32.8x on the real arena (MEASURED fork) and 69.6x on the planted self-test",
  "baseline_in_band": true,
  "baseline_in_band_note": "RANDOM/POP near the 1/N floor on held-out; ORACLE-fires gate = ORACLE_mrr >= 3x RANDOM_mrr AND headroom >= 0.003 (scale-free ratio + non-noise floor), NOT a copied absolute margin",
  "discriminator_survives_scale": "analytical_B_plus_selftest",
  "discriminator_survives_scale_note": "a per-entity embedding table cannot encode an unseen entity by construction (GraIL/NBFNet), so the memorize null persists at ANY N; the ORACLE-fires control proves the metric can move at scale; the self-test fires the ANCHOR-beats-RANDOM + scramble-fails discriminators deterministically",
  "hard_pass_strictly_above_floor": true,
  "hp_scope": {"ANCHOR_COMPOSE": ["anchor_margin_vs_random", "form_margin_vs_memorize", "fair_lowmid_anchor_margin"], "ORACLE_ADDITIVE": ["oracle_fires"], "RANDOM_CODES": ["must_not_clear_bar"], "ANCHOR_SCRAMBLE": ["scramble_controlled"], "BASELINE_POP": ["fit_independence"]},
  "calibration_check": "adaptive_with_discriminator_gate",
  "calibration_check_note": "HELDOUT_ENTITY_FRAC=0.15 / SUPPORT_FRAC=0.5 / ORACLE_FIRE_RATIO=3.0 / ORACLE_FIRE_ABS=0.003 / HP_CEIL_FRAC=0.50 / FORM_CEIL_FRAC=0.10 / HF_CEIL_FRAC=0.20 / SCRAMBLE_CEIL_FRAC=0.25 pre-registered, NOT tuned on real data; ANCHOR bands are FRACTIONS OF THE MEASURED oracle headroom H (computed in-run) -> the compute-info-ceiling-before-iterating discipline baked into the verdict logic; the planted self-test verifies ORACLE+ANCHOR recover on additive-consistent structure",
  "per_unit_failure_class": true,
  "cell_chunked": false,
  "cell_chunked_note": "in-process seed loop with FitCheckpoint (ckpt_every=20, outage-resumable per arm) + write_partial per-seed persistence; a crash loses at most the in-progress seed which resumes from its last fit checkpoint (family pattern, matches exp_heldout_entity_inductive_probe_cskg_v1)",
  "start_marker_written": true,
  "crash_diagnostic_present": true,
  "heartbeat_present": true,
  "defensive_error_checking": "start_marker + crash_diagnostic + heartbeat + per-seed failure_class; per-seed FitCheckpoint resume replaces per-seed chunking",
  "except_ordering": "SystemExit/KeyboardInterrupt re-raised before except Exception; no bare except / no BaseException (grep-clean)",
  "progress_logging": "print_flush_true",
  "sweep_alignment_verdict": "ALIGNED",
  "discriminating_fraction": "n/a (not a parameter sweep; single held-out-entity split per seed)",
  "composition_edges": "additive fit (X,D) -> E_derived bundle -> additive_direct_scores; SHAPE_MATCH (all in the additive TransE geometry; the bundle mean is dimension-preserving)",
  "positive_control_arms": "ORACLE_ADDITIVE (additive fit, held-out folded in) reproduces the arena-answerable ceiling AT THE TEST REGIME; must fire under the ceiling-aware gate (ORACLE_mrr >= 3x RANDOM_mrr AND headroom >= 0.003) -> the ORACLE score IS the measured ceiling H against which ANCHOR bands are set",
  "functional_requirements": "represent an unseen entity (E_derived bundle) | rank its held-out edges (additive_direct_scores) | prove signal is relational not degree/anchor (ANCHOR_SCRAMBLE) | prove arena answerable (ORACLE_ADDITIVE) | fit-independence (BASELINE_POP)",
  "final_metrics_write": "write_metrics(...) -> os.replace atomic"
}
```

## Compute architecture
class (c) MIXED. Split + support/query partition + POP = sequential-CPU graph ops (no matmul); additive/rotate fits
= minibatch SGD (batched, neg-chunked on FULL, neg_chunk=16); E_derived = one vectorized `index_add_` bundle (no
training, seconds); readouts = query-chunked batched matmul (the (nq,N) map never materialized whole). Storage
SHARDED (each entity its own code; relations per-TYPE additive displacements; the ONLY bundle is the per-ENTITY
anchor mean). device=auto (cuda on GPU host); remote_cpu forces cpu. FULL fits fit-checkpointed (ckpt_every=20 ->
outage-resumable).

## Run profiles
- **self_test** (LOCAL .venv gate, PASSED 10.5s): k=12, ep=350, 1 seed, planted arena, single-thread CPU.
- **memsmoke** (multi-seed MEMORY pre-flight, GPU host one-shot `--memsmoke`): FULL footprint (full CSKG core N,
  k=24, n_neg=128, neg_chunk=16) but ep=25 + 2 seeds [7,13] IN-PROCESS -> proves no-OOM + per-seed empty_cache
  BEFORE the multi-hour FULL. NOT a discriminator gate (few epochs under-train the oracle by design).
- **full** (REMOTE GPU, READY-HELD; Director fires): k=24, ep=500, n_neg=128, neg_chunk=16, ckpt_every=20,
  heldout_entity_frac=0.15, support_frac=0.5, CSKG core k_core=12 (N~25.7k), n_heldout_eval=3000, seeds=[7,13,17].
  NOTE: epochs unchanged from the fork (proven NOT epoch-limited: v1 0.0123 -> v2 0.0143 at 2.5x epochs). The fix is
  the METRIC, not more compute.

## Numbers provenance
- N~25752, deg_mean 36.8, 12-core, max/mean=164 (P1 skew), hardest_tertile relations: MEASURED@data/exp_cskg_graph_structure_diagnostic_v1/metrics.json.
- INFO-CEILING (real arena): ORACLE mrr=0.01280, RANDOM mrr=0.00039 (32.8x), ORACLE hits@10=0.01433 (legacy 0.10 gate does NOT fire): MEASURED@data/exp_course_c_heldout_entity_inductive_probe_gpu1024_v2/metrics.json:per_seed[*].arm_hits.
- self-test held-out MRR + oracle_fire_by_metric: MEASURED@data/exp_anchor_compose_inductive_entity_cskg_v1_selftest/metrics.json:mechanism_selftest.
- HARD_PASS P~0.30 / beats-memorize P~0.35-0.40: CITED@notes research_inductive_entity_generalizing_factorized_map_builder_2026-07-12 (deflated; capped under the 0.50 novel-synthesis ceiling).
- Additive fit lr=0.05 (A1_LR), rotate lr=5e-3 (ROT_LR): the additive geometry needs its tuned lr to converge (MEASURED: transductive h@10 0.041 @ lr=5e-3 vs 0.97 @ lr=0.05 on the planted arena).
