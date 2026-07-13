# Pre-registration: ANCHOR_COMPOSE inductive entity-generalizing map-builder (CSKG held-out-ENTITY)

- **Cell:** `experiments/exp_anchor_compose_inductive_entity_cskg_v1.py`
- **Anchor name:** `anchor_compose_inductive_entity_cskg_v1`
- **Metrics path:** `data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json`
- **Filed:** 2026-07-12 (exp_dev). **STAGED / READY-HELD** for a gated pivot; do NOT dispatch until the fork verdict
  (`exp_course_c_heldout_entity_inductive_probe_gpu1024_v2`) lands `oracle_fires=True`.

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

## Pre-registered bands (hits@10 margins; picked BEFORE the run)
- **HARD_PASS** (`HARD_PASS_INDUCTIVE_ANCHOR_COMPOSE`): `ANCHOR - RANDOM >= 0.05` **AND**
  `ANCHOR - max(ADDITIVE, ONESHOT) >= 0.02` (beats the memorize arms on unseen entities) **AND** ORACLE fires
  (`ORACLE - RANDOM >= 0.10`) **AND** scramble controlled (`SCRAMBLE - RANDOM <= 0.02`) **AND** not broken **AND**
  the anchor margin holds on the low+mid degree stratum (fair, non-super-hub; P1 skew HARD_FAIL demands this).
- **MIDDLE_BAND**: `0.02 <= ANCHOR-RANDOM < 0.05`, OR `ANCHOR-RANDOM >= 0.05` but form-margin `< 0.02`, OR a
  scramble/degree confound is present. Localize via the anchor-support-degree stratification.
- **HARD_FAIL** (`HARD_FAIL_ANCHOR_COMPOSE_NO_TRANSFER`): `ANCHOR - RANDOM < 0.02` with ORACLE firing (a genuine
  negative: the right-shaped construction fails on CSKG -> localize to sparsity vs crosstalk).
- Gated **INCONCLUSIVE** if ORACLE does not fire (arena not answerable), `< 20` held-out queries, or a control beats
  POP by `> 0.03` (broken).
- HP_SCOPE: the two inductive HARD_PASS gates apply to **ANCHOR_COMPOSE only**. ORACLE = positive control (must
  fire); RANDOM/ANCHOR_SCRAMBLE = must-not-clear-bar controls; ADDITIVE_TRANSE/ONESHOT_ROTATE = memorize
  head-to-heads; POP = fit-independence sanity.

## Weak-point localization (first-class per cell)
Three stratifications of the mechanism vs controls, reported in `per_seed[*].localization`:
1. **anchor-support degree** bins {cold(0), d1, d2_3, d4_7, d8+} -- does the margin scale with support (SNR ~ local
   degree, GrapHD `5 log(D/d)`)? Cold = the sparse-entity failure mode.
2. **global-degree tertile** (low/mid/high) + `fair_low_mid` -- super-hub vs tail (P1 skew max/mean=164; MEASURED@
   data/exp_cskg_graph_structure_diagnostic_v1/metrics.json:gates.p1).
3. **relation tertile** (hardest vs rest) -- HARDEST set = the diagnostic's cardinality-heavy hardest_tertile
   (isa/synonym/similarto/usedfor/hascontext/antonym/...; CITED@same diagnostic:diagnostic.hardest_tertile).

## Four validity-preflight checks (declared in the self-test via experiments._validity_preflight)
1. **positive_control_passes**: ORACLE_ADDITIVE recovers planted held-out tails and clears RANDOM by the fire margin.
2. **metric_moves**: held-out hits@10 MOVES across [RANDOM, ADDITIVE_TRANSE, ANCHOR_COMPOSE, ORACLE].
3. **negative_control_margin**: RANDOM + ANCHOR_SCRAMBLE sit below ANCHOR by margin, deterministically (>=2 vals).
4. **full_gates_exercised**: `aggregate_and_verdict` runs on the planted per-seed, firing every fail-closed gate.

## Self-test (MEASURED, local .venv, single-thread CPU, 14.4s)
Planted HIGH-intrinsic-dim TransE-consistent arena (`build_planted_transe_arena`, n_ent=300, n_rel=6, k_lat=8,
deg=3) where the RELATION operator is NECESSARY (no smooth low-dim embedding, so plain neighbour-averaging fails).
MEASURED@data/exp_anchor_compose_inductive_entity_cskg_v1_selftest/metrics.json:
- held-out hits@10: **ANCHOR=0.656, ADDITIVE=0.000, ONESHOT=0.033, RANDOM=0.000, SCRAMBLE=0.262, ORACLE=1.000,
  POP=0.000**; anchor_margin=0.656, scramble_margin(ANCHOR-SCRAMBLE)=0.393, oracle_margin=1.000; 7 distinct sigs;
  `validity_preflight_ok=True`; verdict=**SELFTEST_PASS**.
- The construction RECOVERS a planted held-out entity's edges ZERO-training (0.656 vs random 0.000); the
  relation-scramble must-fail FIRES with margin (0.393); the additive ORACLE fires (arena answerable).
- Note: on a 2D grid the scramble did NOT fail (neighbour-averaging recovers a spatially-smooth target without the
  relation) -- the planted arena was redesigned to high intrinsic dim so the relational signal is provable.

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
  "crlb_formula_reference": "chance hits@10 = k/N = 10/25752 ~ 0.0004 at CSKG core N~25.7k",
  "discriminator_reachability": true,
  "discriminator_reachability_note": "HARD_PASS 0.05-above-random is on the achievable side; ORACLE positive control demonstrates the metric reaches 1.0 when the code is learned (self-test) -> the >=0.05 bar is attainable",
  "baseline_in_band": true,
  "baseline_in_band_note": "RANDOM/POP near the 10/N floor on held-out; ORACLE must fire in (RANDOM+0.10, 1.0]",
  "discriminator_survives_scale": "analytical_B_plus_selftest",
  "discriminator_survives_scale_note": "a per-entity embedding table cannot encode an unseen entity by construction (GraIL/NBFNet), so the memorize null persists at ANY N; the ORACLE-fires control proves the metric can move at scale; the self-test fires the ANCHOR-beats-RANDOM + scramble-fails discriminators deterministically",
  "hard_pass_strictly_above_floor": true,
  "hp_scope": {"ANCHOR_COMPOSE": ["anchor_margin_vs_random", "form_margin_vs_memorize", "fair_lowmid_anchor_margin"], "ORACLE_ADDITIVE": ["oracle_fires"], "RANDOM_CODES": ["must_not_clear_bar"], "ANCHOR_SCRAMBLE": ["scramble_controlled"], "BASELINE_POP": ["fit_independence"]},
  "calibration_check": "adaptive_with_discriminator_gate",
  "calibration_check_note": "HELDOUT_ENTITY_FRAC=0.15 / SUPPORT_FRAC=0.5 / ORACLE_FIRE_MARGIN=0.10 pre-registered, NOT tuned on real data; the planted self-test verifies ORACLE+ANCHOR recover on additive-consistent structure",
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
  "positive_control_arms": "ORACLE_ADDITIVE (additive fit, held-out folded in) reproduces the arena-answerable ceiling AT THE TEST REGIME; must fire >= ORACLE_FIRE_MARGIN",
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
- **self_test** (LOCAL .venv gate, PASSED): k=12, ep=350, 1 seed, planted arena, single-thread CPU, ~14s.
- **memsmoke** (multi-seed MEMORY pre-flight, GPU host one-shot `--memsmoke`): FULL footprint (full CSKG core N,
  k=24, n_neg=128, neg_chunk=16) but ep=25 + 2 seeds [7,13] IN-PROCESS -> proves no-OOM + per-seed empty_cache
  BEFORE the multi-hour FULL. NOT a discriminator gate (few epochs under-train the oracle by design).
- **full** (REMOTE GPU, gated on fork verdict): k=24, ep=500, n_neg=128, neg_chunk=16, ckpt_every=20,
  heldout_entity_frac=0.15, support_frac=0.5, CSKG core k_core=12 (N~25.7k), n_heldout_eval=3000, seeds=[7,13,17].

## Numbers provenance
- N~25752, deg_mean 36.8, 12-core, max/mean=164 (P1 skew), hardest_tertile relations: MEASURED@data/exp_cskg_graph_structure_diagnostic_v1/metrics.json.
- self-test held-out hits: MEASURED@data/exp_anchor_compose_inductive_entity_cskg_v1_selftest/metrics.json.
- HARD_PASS P~0.30 / beats-memorize P~0.35-0.40: CITED@notes research_inductive_entity_generalizing_factorized_map_builder_2026-07-12 (deflated; capped under the 0.50 novel-synthesis ceiling).
- Additive fit lr=0.05 (A1_LR), rotate lr=5e-3 (ROT_LR): the additive geometry needs its tuned lr to converge (MEASURED: transductive h@10 0.041 @ lr=5e-3 vs 0.97 @ lr=0.05 on the planted arena).
