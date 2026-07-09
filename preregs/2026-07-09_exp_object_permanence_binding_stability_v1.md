# Pre-reg: Object-permanence bake-in probe (binding-stability default)

- anchor_name: exp_object_permanence_binding_stability_v1
- script: experiments/exp_object_permanence_binding_stability_v1.py
- date: 2026-07-09
- source design: notes/research_innate_scaffolding_core_knowledge_kernel_2026-07-09.md (S2 bake-in #1)
- sibling: exp_dual_number_double_dissociation_v1 (bake-in #3; banked pattern reused)
- run_mode dispatched: full (3 seeds); smoke = full-N single seed
- queue (target): remote_cpu_queue (light CPU; bind=elementwise, cleanup tiny matmul; no GPU benefit)

## Prior-work check (substrate concept-query, USER-locked 2026-07-01)
Query: "object permanence persistence binding stability occlusion identity recovery holographic
distributed localist redundancy" -> top cosine 0.3213, all generic WordNet "persistence" lexemes +
unrelated preregs (schema-relation richness, encoder-objective swap). Lexical false-positive on the
token "persistence"; NO prior object-permanence / occlusion-recovery / holographic-vs-localist
binding-stability cell. GENUINELY NOVEL, not a rediscovery. Distinct mechanism from the dual-number
sibling (binding-stability under structured occlusion, NOT number-system dissociation).

## Question
Does baking in "object-persistence as a binding-stability default" (a bound entity-identity spread
holographically across the substrate) give the substrate infant-like object permanence -- identity
SURVIVES an occlusion-like corruption unless ACTIVELY broken -- where a naive localist representation
loses the entity under the same corruption? Brain-grounded: Baillargeon/Spelke violation-of-expectation
(object continuity/solidity/cohesion, pre-linguistic ~2.5-4.5mo).

## Mechanism (arms; PAIRED on identical id/feature/occlusion draws)
- PERSISTENCE (bake-in): holographic bound bundle E_p = bind(role_id,id_tok) + sum_f bind(role_f,ft_f)
  over all N dims. Identity DISTRIBUTED across every dim by binding (cohesion). Recover via
  cleanup(unbind(occ(E_p), role_id)).
- NAIVE (baseline): localist concatenation -- each token stored RAW in its own disjoint dim-block
  (id in block 0). No binding, no cross-field redundancy. Recover via cleanup(E_n[block0]).
- Neither is a strawman; localist per-field storage is a standard structured-record encoding. The claim
  is the biological one: holographic distribution (cohesion) yields occlusion-robustness localist lacks.

## Corruption (matched, paired)
- STRUCTURED occlusion (object-permanence-relevant; an occluder covers whole parts): zero K_OCC=5 of
  P=8 dim-blocks, chosen uniformly. Correlated loss.
- Diagnostic i.i.d. occlusion (same total fraction, scattered): expected to show NO gap -> pins the
  advantage to STRUCTURED corruption (honest scope; holographic redundancy only helps correlated loss).

## Must-fail controls (vacuous-guard; anti-tautology)
- REMOVED: actively subtract the identity binding before query (naive: zero block 0). Entity taken away
  -> recovery MUST fall to chance. Persistence recovering it above chance = LEAK/tautology -> HARD_FAIL.
- SCRAMBLED: bind id_tok to a WRONG role -> recovery MUST be at chance (needs correct binding).

## Config
N_DIM=8192; F_FEAT=7; P_BLOCKS=8; B_WIDTH=1024; V_TOK=64; K_OCC=5 (F_OCC=0.625);
SEEDS_FULL=(7,17,23); M_TRIALS_FULL=600; SEEDS_SMOKE=(7,); M_TRIALS_SMOKE=200. chance=1/V_TOK=0.0156.

## Bands (pre-registered BEFORE run)
Discriminator: ratio_structured = rec_persist_structured / rec_naive_structured.
- HARD_PASS: ratio_structured >= 2.0 AND rec_persist_structured >= 0.70 (strict floor, META_RULE_L)
  AND gap(persist-naive) >= 0.15 AND naive in [chance+0.03, 0.90] AND must-fail controls recover
  <= chance+0.10 (removed & scrambled correctly FAIL). Majority seed-agreement (>=2/3).
- HARD_FAIL: a must-fail control RECOVERS > chance+0.20 (tautology/leak) regardless of ratio, OR
  ratio_structured <= 1.3 with a real occlusion effect (naive already persists; prior adds nothing).
- MIDDLE_BAND: ratio in (1.3, 2.0), or controls marginal.
- INCONCLUSIVE: no occlusion effect (structured occlusion does not degrade naive by >= 0.15).

Both outcomes gold: PASS = object-permanence-as-binding-stability transfers (structural bake-in, composes
with dual-number); FAIL = naive already persists / prior adds nothing. Architectural-support result;
mechanism-analog NOT task-analog (like dual-number: supports, not spontaneous-learning).

## SCHEMA-VET fields
- cardinality_ok: true. EXPECTED_N_UNITS = len(SEEDS) = 3 (full) / 1 (smoke); verdict counts len(per_seed);
  short -> HARD_FAIL_CARDINALITY_BREACH_META_RULE_H.
- arms_differ_verified: true at smoke (persist vs naive structured-occluded scenes bit-distinct, sha256).
- final_metrics_atomicity: tmp_replace (write_metrics) + per-seed write_partial (checkpoint/resume).
- baseline_in_band: true (naive_structured must be in [0.046, 0.90]; META_RULE_AG).
- discriminator_reachability: true. crlb_n/a: discriminator is a paired recovery-accuracy RATIO, not a
  noise-floor estimation; no Cramer-Rao floor applies. HARD_PASS ratio 2.0 is analytically reachable:
  persist_structured -> 1.0 (SNR z~12), naive_structured -> (P-K)/P = 0.375 by block-survival.
- calibration_check: default_ok_for_this_regime (clean synthetic corpus, no substrate-state
  contamination; analytical SNR + block-survival probability computed in self-test).
- effective_vs_nominal_parameter_audit: no swept param (fixed regime); sweep_alignment_verdict: ALIGNED (n/a).
- bracket_includes_discriminating_band / discriminating_fraction: n/a (no sweep); naive baseline
  analytically placed at 0.375 (in discriminating band, not saturated, not floor).
- composition_edges: SHAPE_MATCH (bind -> bundle -> unbind -> cleanup, standard bipolar BSC pipeline).
- positive_control_arms: no-occlusion arm reproduces perfect recovery (>=0.95) for BOTH arms = the
  primitive-works-at-test-regime control; i.i.d.-occlusion arm = structural-specificity control.
- functional_requirements: (1) bound identity survives partial occlusion -> holographic bind+bundle;
  (2) recover identity from corrupted store -> unbind+cleanup argmax; (3) do NOT hallucinate a removed
  entity -> removed/scrambled must-fail controls. All map to existing chain-grade primitives.
- HP_SCOPE: {persist_structured: [ratio_ge_2, persist_ge_floor, gap_ge_min_effect];
  naive_structured: [in_band]; removed/scrambled: [le_chance_margin]}. No chain-grade gate on controls.

## Defensive error-checking (SCHEMA-VET §13)
- cell_chunked: false (3 seeds within one cell; fast <30s total; per-seed write_partial checkpoint).
- start_marker_written: true. crash_diagnostic_present: true (Exception -> CELL_CRASHED metrics + tb;
  except SystemExit/KeyboardInterrupt raised before except Exception; no bare/BaseException).
- heartbeat_present: true (CellHeartbeat interval_s=30).
- defensive_error_checking: passed_all_4_patterns.
- progress_logging: print_flush_true (all progress lines flush=True; cell wall < 30s so <1800s threshold,
  field provided anyway).

## Compute architecture
class: (b) sequential-CPU with justification. bind = elementwise mul, bundle = sum, cleanup =
(V_TOK=64 x N=8192) matmul per query. Per-seed wall ~2s (smoke M=200 measured 1.9s); FULL 3 seeds
M=600 ~ under 30s total. Well under the 10s/phase-point batching-candidate threshold; no GPU benefit.
storage strategy: no_composition (single-hop bind/unbind recovery; no chained retrieval) -- bundled
holographic store IS the mechanism under test (persistence arm), localist is the baseline arm.

## MEASURED smoke evidence (this pre-reg dispatched AFTER smoke=HARD_PASS)
- MEASURED@data/exp_object_permanence_binding_stability_v1_smoke/metrics.json (N=8192, 1 seed, M=200):
  verdict=HARD_PASS; ratio_structured=2.70; persist_structured=1.000; naive_structured=0.370
  (~ (P-K)/P=0.375 THEORETICAL); ratio_iid=1.00 (no gap, structural-specific); removed_persist=0.015,
  scrambled_persist=0.005 (both ~ chance 0.016 -> controls correctly FAIL); no-occ persist=naive=1.000;
  arms_differ_verified=True; smoke_discriminator_fires=True; baseline_in_band=True; control_leak=False.
- Self-test: naive_structured=0.367 matches analytical (P-K)/P=0.375 within 0.01; telemetry-sensitive
  (seed17 naive=0.340 differs); i.i.d. ratio<1.5 (structural specificity).

## FULL expectation (HYPOTHESIZED)
HARD_PASS with ratio_structured ~2.6-2.7, persist ~1.0, naive ~0.375, controls at chance. Genuine FAIL
possible if 3-seed variance pushes naive up or persistence down; both outcomes banked.
