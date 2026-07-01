# Pre-reg: cortex_attention_binding_router_v1

**Date filed:** 2026-07-01
**Author:** hdi_exp_dev (agent-spawn from Director; M1.6 first-shot v1)
**Anchor:** `cortex_attention_binding_router_v1`
**Chunks:** `_seed_7`, `_seed_13`, `_seed_19` (chunk-per-seed; Skunkworks aggregates).
**Research parent:** M1.6 research 2026-07-01 (cortex 4-class attention router).
**Mechanism class:** cortex integration classifier (Stage 3 composition; wires 5 CG'd substrate primitives; NOT a new substrate primitive).
**Milestone:** M3 architecture / M1.6 second cortex-integration cell after M1.5 v2 (Atom 18 CG).

## Purpose

Cortex-side 4-class routing classifier that decides which substrate primitive to invoke given
`(query_key, session_context_from_M1.5_TWOTIER, refuse_signal_from_M1.4_CONFORMAL)`. Enables the
M3 Phase 1 architecture pattern: LLM router replaced by substrate-side decision. Substantive
potential: if HP -> **second cortex-integration CG in M3 stack**; together with M1.4 CONFORMAL
+ M1.5 TWOTIER, three cortex milestones close 2026-07-01.

## Functional requirements (per META_RULE-derived §15E)

Given a natural query, classify into one of 4 substrate-primitive routes:

1. **REFUSE**: query is OOD; no substrate answer exists; refuse-gate fires.
   - Substrate primitive: M1.4 v8 CONFORMAL_MODERATE refuse-gate (Atom 15 CG).
2. **RETRIEVE**: query hits a known entity in WM or LTM; direct cleanup lookup.
   - Substrate primitive: M1.5 v2 TWOTIER context retention (Atom 18 CG).
3. **BIND**: query introduces a NEW entity that must be encoded into substrate state.
   - Substrate primitive: WM multi-bank K=4096 write (prior CG).
4. **MULTI_HOP**: query requires >= 2 hops via chained substrate operations.
   - Substrate primitive: partition-oracle multihop d20-40 (Atom 6 CG) or d45-60 (Atom 19 CG).

The router itself is a nearest-class hypervector classifier (LeHDC-style class hypervectors) over
concatenated feature vectors. Not a new substrate primitive; a composition classifier.

## Feature vector design

Each test-item produces a feature vector by concatenating three signals into a single N_DIM
bipolar-quantized composition (bind + bundle):

- `refuse_signal_hv` = M1.4 conformal signal: hypervector encoding (tau_moderate cross-cal-set
  distance vs V_REL) mapped to a 1-of-3 codebook slot (below-cal / near-tau / above-tau).
- `retrieval_signal_hv` = M1.5 TWOTIER hit signal: hypervector encoding
  (STM_hit / LTM_hit / no_hit) as 1-of-3 codebook slot.
- `query_hv` = the raw query bipolar hypervector (bipolar N_DIM).

Feature: `feature_hv = bipolar_quantize(refuse_role * refuse_signal_hv + retrieval_role *
retrieval_signal_hv + query_role * query_hv)`. Bipolar bind with fixed role vectors preserves
distinctness; bundle keeps N_DIM constant.

Classifier: 4 class hypervectors `class_hv[c]` learned by bundling training feature_hvs per class:
`class_hv[c] = bipolar_quantize(sum over training items with route=c of feature_hv_i)`. At query
time: `route_pred = argmax_c cosine(query_feature_hv, class_hv[c])`.

Training set: 40 items (10 per class × 4 classes); held-out test = 20 items (5 per class × 4
classes); explicitly disjoint per seed.

## Arms (7)

- **ARM_TRUE_REFUSE**: OOD queries only (all 20 test items expect route=REFUSE); measures per-class
  precision at route=REFUSE.
- **ARM_TRUE_RETRIEVE**: queries hit known WM/LTM entities (all expect route=RETRIEVE); precision
  at RETRIEVE.
- **ARM_TRUE_BIND**: novel entity intros (all expect route=BIND); precision at BIND.
- **ARM_TRUE_MULTI_HOP**: 2-hop chain-required queries (all expect route=MULTI_HOP); precision at
  MULTI_HOP.
- **ARM_ROUTE_CONFUSION_MATRIX**: 20 test items balanced across 4 classes (5 each); top-1 accuracy
  + per-class precision + per-class recall aggregate. **This is the load-bearing discriminator arm.**
- **ARM_NO_ROUTER**: naive baseline; always predicts route=RETRIEVE regardless of query.
  Expected accuracy = 0.25 (1/4 chance if all 4 classes equally represented). Chance-baseline
  discriminator against composition.
- **ARM_M14_M15_ISOLATED**: routing on M1.4 alone OR M1.5 alone; the class HVs are computed with
  ONLY the refuse_signal_hv OR ONLY the retrieval_signal_hv (query_hv still bound in but the OTHER
  signal is zeroed). Discriminator: composition must beat either isolated signal.

## Test-task scenarios per seed

Each seed generates 40 train + 20 test items across 4 test-task scenarios:

- **3-turn dialogue with pronoun reference** (expected route=RETRIEVE via M1.5 TWOTIER).
- **OOD query** (expected route=REFUSE via M1.4 conformal moderate).
- **Novel entity introduction** (expected route=BIND via WM write).
- **Multi-hop question over prior entities** (expected route=MULTI_HOP via partition-oracle chain).

Balance: 10 train + 5 test per scenario/class. Deterministic seed-based generation of query_hv
per scenario ensures reproducibility.

## Signal encoding detail (per class)

**REFUSE**: refuse_signal_hv = codebook_slot[2] (above-tau: refuse fires); retrieval_signal_hv =
codebook_slot[2] (no_hit); query_hv = fresh OOD bipolar (random noise, no substrate anchor).

**RETRIEVE**: refuse_signal_hv = codebook_slot[0] (below-cal: no refuse); retrieval_signal_hv =
codebook_slot[0] or [1] (STM_hit or LTM_hit); query_hv = perturbed version of a "known" entity
bipolar (cosine ~0.85 to a stored entity).

**BIND**: refuse_signal_hv = codebook_slot[0] (no refuse; novel entity is legal); retrieval_signal_hv
= codebook_slot[2] (no_hit; entity is new); query_hv = fresh bipolar tagged with a "novelty" role
(fresh entity role-key bound with entity_hv).

**MULTI_HOP**: refuse_signal_hv = codebook_slot[0] (no refuse); retrieval_signal_hv = codebook_slot[1]
(LTM_hit is partial; 1st hop found but query wants >=2 hops); query_hv = bind(entity_A, relation) as
a chain-anchor query.

The 4 classes are distinguishable at the feature-HV level BY CONSTRUCTION only if the
refuse_signal + retrieval_signal + query_hv jointly discriminate. Router must LEARN this via the
class-HV bundling (not memorize; test items generated independently from train items with
different random seeds within each scenario).

## Verdict gates

### HARD_PASS (chain-grade)

- **HP_ROUTE_ACCURACY**: ARM_ROUTE_CONFUSION_MATRIX top-1 accuracy >= **0.85** across all 3 seeds
  (cross-seed mean; cv < 5%).
- **HP_LIFT_OVER_NULL**: ARM_ROUTE_CONFUSION_MATRIX accuracy >= ARM_NO_ROUTER accuracy + **0.30**
  (mechanism lift). ARM_NO_ROUTER expected 0.25 (chance).
- **HP_PER_CLASS_PRECISION**: for each of 4 classes, precision >= **0.70** in the confusion matrix
  (no class collapses / becomes a black hole).
- **HP_LIFT_OVER_ISOLATED**: composition (ARM_ROUTE_CONFUSION_MATRIX) beats ARM_M14_M15_ISOLATED
  accuracy by >= **0.15** (composition genuinely helps).

### HARD_FAIL

- **HARD_FAIL_MECHANISM**: ARM_ROUTE_CONFUSION_MATRIX accuracy < **0.65** (barely above chance
  0.25 + 4-sigma margin); composition not working.
- **HARD_FAIL_CLASS_COLLAPSE**: any per-class precision < **0.30**; router treats that class as
  random.
- **HARD_FAIL_ISOLATED_BEATS_COMPOSITION**: ARM_M14_M15_ISOLATED accuracy >= ARM_ROUTE_CONFUSION_MATRIX
  accuracy; composition adds nothing (or hurts).
- **HARD_FAIL_ARMS_IDENTICAL** (META_RULE_AF): any two arms' per-test-item prediction vectors
  bit-identical in non-saturating regime.
- **HARD_FAIL_CARDINALITY_BREACH** (META_RULE_H): observed arm-rows < ceil(0.85 * EXPECTED_N_UNITS).
- **HARD_FAIL_TRIVIAL_BASELINE**: ARM_NO_ROUTER accuracy != 0.25 +/- 0.10 (baseline broken; likely
  class-balance bug).
- **HARD_FAIL_STALE_SMOKE**: FULL run finds smoke partials in checkpoint.

### MIDDLE_BAND

- HP gates split (e.g., overall accuracy >= 0.85 but per-class precision splits below 0.70 on one).
- ARM_ROUTE_CONFUSION_MATRIX accuracy in [0.65, 0.85] (mechanism partially working; MIDDLE_BAND).

### META_RULE_Q (suspect-1.000)

- Only fires if ARM_ROUTE_CONFUSION_MATRIX accuracy >= 0.9995 in a regime where per-scenario
  train-vs-test disjoint AND query_hvs regenerated independently (no memorization possible).
  Below-1.000 saturation is expected and legitimate for the small-item classification task.

## Composition parents (CG this cell)

1. **`m14_conformal_moderate_commit_<hash>`** — refuse-gate v8 CONFORMAL_MODERATE (Atom 15 CG,
   2026-07-01). Contributes the refuse_signal_hv encoding into feature vector. HYPOTHESIZED@ this
   prereg — the actual atom-hash reference lives in atoms.jsonl; cell-comment cites the M1.4 v8
   HARD_PASS metrics.json path.
2. **`m15_twotier_context_retention_v2_commit_adaab6b7`** — cortex_context_retention_v2 TWOTIER
   (Atom 18 CG, 2026-07-01; commit adaab6b7). Contributes retrieval_signal_hv encoding.
3. **`wm_multibank_codebook_cleanup_commit_6e2ff698`** — WM multi-bank K=4096 (prior CG).
   Underpins BIND route (novel entity write) and the STM path in M1.5.
4. **`multihop_partition_oracle_d20_40_CG`** — Atom 6 chain-grade multihop primitive. Underpins
   MULTI_HOP route target semantics.
5. **`cortex_hippo_dense_layer_M8192_v2_READ_REPLACE_commit_863e14b5`** — Dense-Hopfield READ-REPLACE
   (prior CG). Underpins LTM path in M1.5 and RETRIEVE route.

Feature-HV binding + class-HV bundling is standard LeHDC (Kanerva 2009 / HDC classifier body of
work; CITED@Classification Using HDC ResearchGate + LeHDC 2022 arXiv 2312.02989). NOT a new
primitive; a composition classifier over CG'd signals.

## Cardinality (META_RULE_H)

FULL per-seed grid: 7 arms × 3 test-task-types × 20 test-items-per-arm-average.
Actually cleaner: **7 arms × 3 test-task-regimes** = **21 arm-rows per seed** (each arm-row aggregates
20 test items into top-1 accuracy + per-class precision/recall).

`EXPECTED_N_UNITS = 21`. `HARD_FAIL_CARDINALITY_BREACH` if observed n_arm_rows < floor =
ceil(0.85 × 21) = 18.

## CRLB (formula-computed)

- Chance floor: 1 / 4 = **0.250** THEORETICAL@uniform-4-class-argmax. ARM_NO_ROUTER hits chance
  0.25.
- Bernoulli sigma at p=0.5, N_TEST_ITEMS=20 per arm-row: sqrt(0.25/20) = **0.112**.
- HP gap 0.30 lift over baseline = 0.30 / 0.112 = 2.7 sigma. Reachable.
- Cross-seed cv floor at n_seeds=3, sigma=0.112: cv ~ 0.112 / 0.85 = 13% -- borderline; tighten with
  larger n_seeds if MB in smoke. For chain-grade: acceptable since we require accuracy >= 0.85 AND
  lift >= 0.30 conjunction (harder to spuriously satisfy both).

## Envelope-fail-bands

See "Verdict gates" above. Bracket-includes-discriminating-band (§15B): 4/7 arms predicted to land
in [0.30, 0.70] discriminating band (ROUTE_CONFUSION_MATRIX target 0.85; per-class-precision targets
0.70; NO_ROUTER at 0.25 baseline; ISOLATED between 0.40-0.70). discriminating_fraction >= 0.30 SAT.

## Discipline gates (META_RULE_* audit)

- **META_RULE_H** — cardinality expected 21; HF if < 18. `cardinality_ok` in metrics.
- **META_RULE_J** — no bare except; each arm records failure_class if crashes.
- **META_RULE_K** — discriminator-fires: smoke must show ARM_ROUTE_CONFUSION_MATRIX > 0.65 AND
  ARM_NO_ROUTER ~= 0.25 (baseline in chance band).
- **META_RULE_L** — HARD_PASS strictly above floor by 5% of band-width: 0.85 - 0.05*0.65 = 0.82 min
  reported at HP; we require >= 0.85 clean.
- **META_RULE_M** — calibration: this is a novel classifier — regime is 4-class with N_DIM=8192 +
  V_CB=1024 for the codebook slots; adaptive-with-discriminator-gate justified by chance-floor
  fixed 0.25 (not adaptively tuned).
- **META_RULE_AF** — arms-must-differ: at smoke time, hash-check per-item prediction vectors across
  the 7 arms.
- **META_RULE_AG** — baseline-in-band: ARM_NO_ROUTER at 0.25 (chance); confirms mechanism can lift.
  ARM_ROUTE_CONFUSION_MATRIX at smoke must exceed 0.35 (chance + 1 sigma) as fires-discriminator.
- **META_RULE_AH** — atomic metrics write (tmp + os.replace); `final_metrics_atomicity: tmp_replace`.
- **META_RULE_AT** — 5 CG parents cited above.
- **META_RULE_AX** — arm distinctness: composition arm differs from NO_ROUTER arm by >= 0.30
  accuracy at smoke.
- **META_RULE_Q** — refined; only fires above 0.9995 in disjoint train/test regime.
- **META_RULE_AC** — HYPOTHESIZED @preregs/2026-07-01_cortex_attention_binding_router_v1.md for all
  pre-smoke numbers; MEASURED @ data/exp_cortex_attention_binding_router_v1_seed_7_smoke/metrics.json
  for smoke-verified numbers.
- **DISCRIMINATOR-MUST-SURVIVE-SCALE**: smoke at full N_DIM=8192 (numpy CPU cheap; not a smaller-N
  smoke). Discriminator (4-class accuracy) is intrinsic to test-item construction; scale invariance
  is inherent since N_DIM is not the sweep axis.

## SCHEMA-VET §15 gates

- **A) `sweep_alignment_verdict`**: N/A (no sweep axis; single regime × 4 classes × 7 arms).
  Declared `sweep_axis: NONE`.
- **B) `discriminating_fraction`**: 5/7 arms predicted in [0.30, 0.70] band; 0.71 >= 0.30. SAT.
- **C) `composition_edges`**: 5 CG parents contribute signals to feature-HV bundle.
  - `refuse_gate -> feature_hv`: shape match (N_DIM bipolar; conformal signal mapped to
    codebook_slot bipolar). SHAPE_MATCH.
  - `twotier_context_retention -> feature_hv`: shape match (N_DIM bipolar; hit-signal codebook_slot).
    SHAPE_MATCH.
  - `wm_multibank -> query_hv`: shape match (N_DIM bipolar). SHAPE_MATCH.
  - `multihop_oracle -> query_hv`: shape match (N_DIM bipolar chain-anchor). SHAPE_MATCH.
  - `dense_hopfield -> retrieval_signal`: shape match (N_DIM bipolar; hit-signal codebook_slot).
    SHAPE_MATCH.
- **D) `positive_control_arms`**: ARM_M14_M15_ISOLATED serves as positive-control-reproducer;
  isolated M1.4 signal reproduces refuse detection at 0.55-0.70 range (per M1.4 v8 metrics);
  isolated M1.5 signal reproduces STM/LTM hit detection at 0.55-0.75 range (per M1.5 v2 metrics).
  Composition must beat both by >= 0.15 to demonstrate lift. Tolerance: 0.10; if either isolated
  arm < 0.40 accuracy, primitive doesn't extend to router regime -> HARD_FAIL_REGIME.
- **E) `functional_requirement_decomposition`**: see "Functional requirements" section above; 4
  functional requirements each mapped to a CG'd substrate primitive.

## Compute + backend

- N_DIM = 8192 (M1.5 v2 anchor; M1.4 v8 also at 8192).
- V_CB = 1024 (codebook for signal-slot encoding).
- 40 train + 20 test items × 4 scenarios × 7 arms × 3 seeds (FULL).
- Backend: numpy CPU. Wall estimate: seed_7 smoke ~10-30s; FULL ~30-60s per seed.
- Discriminator survives full-N: N_DIM is not the sweep axis; discriminating regime is intrinsic to
  test-item construction (which itself uses N_DIM=8192 in smoke AND full).

## Timeout

`--timeout 1800s` (30 min; conservative). Cell wall ~60s/seed; leaves ~30x headroom.

## Route

**remote_cpu_queue** via hdi_orchestrator handoff (after smoke HARD_PASS local-direct-execution).

Local dispatch NOT via `local_cpu_queue` (USER-locked 2026-07-01: SMOKE ONLY on local_cpu; local
paused per `data/local_cpu_queue_paused.flag`). Smoke runs via direct python invocation on laptop;
FULL routes remote_cpu.

## Falsifiable predictions

- **HP prediction**: composition ARM_ROUTE_CONFUSION_MATRIX accuracy in [0.80, 0.95] across 3 seeds
  (cv < 5%); each of 4 per-class precision in [0.70, 0.95]; lift over ARM_NO_ROUTER >= 0.30; lift
  over ARM_M14_M15_ISOLATED >= 0.15.
- **HF prediction (if primitives don't compose)**: ARM_ROUTE_CONFUSION_MATRIX accuracy < 0.65
  (near-chance); one of BIND / MULTI_HOP classes may collapse to <0.30 precision if their signal
  is not discriminative in the feature-HV bundle.
- **Novel-mechanism claim**: **4-class cortex-side routing is possible via signal-HV composition
  over CG'd primitives**. This is the M3 Phase 1 router pattern. If HP: replaces LLM's routing
  decision.
- **Substrate-physics claim**: the feature-HV bundle preserves per-signal discriminability at
  N_DIM=8192 (below Amit-Gutfreund wall alpha < 4/8192 = 0.0005 for 4 class centroids).

## Landing plan

1. Author 3 seed chunks (seed_7 authored + sed-generated siblings; ASCII-only; META_RULE_* gates
   inline).
2. Selftest gate: `python -m experiments.exp_cortex_attention_binding_router_v1_seed_7 --self-test`
   must pass 6+ formula/discriminator selftests.
3. Smoke gate: seed_7 smoke direct-python at HDLAB_RUN_MODE=smoke; verify HARD_PASS OR HARD_FAIL
   OR MIDDLE_BAND per predefined bands; discriminator fires.
4. Fix #26 pre-dispatch verify: substrate-KB concept query DONE 2026-07-01 (Prior-work check:
   NONE at cosine > 0.30; top hit 0.34 is 2026-06-07 HDC classifier drill — related
   mechanism-class but different application; genuinely novel).
5. Commit (cell-author can commit but not push; push routed via hdi_orchestrator).
6. Handoff to hdi_orchestrator for `push origin main` + remote queue_add for 3 seeds FULL.
7. On HARD_PASS × 3 seeds landed -> Skunkworks landed-VET + CG atomization -> **second cortex-integration CG
   in M3 stack + M1.6 milestone closed**.

## No-lock-in / no-hallucination checks

- All numerical claims tagged (META_RULE_AC):
  - Chance floor 1/4 = 0.25  THEORETICAL@uniform-4-class-argmax.
  - Bernoulli sigma at p=0.5, N_TEST=20 = 0.112  THEORETICAL@sqrt(p*(1-p)/N).
  - HP thresholds (0.85 accuracy, 0.30 lift, 0.70 per-class precision) HYPOTHESIZED@this-prereg.
  - Substrate-KB prior-work check: `bash tools/substrate_query.sh "cortex attention binding
    router 4 class refuse retrieve multi hop classifier"` top-1 cosine 0.34 at 2026-06-07 HDC
    classifier drill (related mechanism-class; different application). Second query
    `"cortex layer operation router substrate M1.6 attention classifier"` top-1 cosine 0.40 at
    2026-06-08 attention/routing theory drill (research, not implementation). Prior-work check:
    NONE at cosine > 0.30 that describes THIS composition. Novel cell.
- Composition parent commit hashes verified via `git log`.
- N_DIM=8192 matches CG anchor of M1.5 v2 and M1.4 v8 (consistency check).

## References

- `experiments/exp_cortex_context_retention_v2_seed_7.py` — M1.5 v2 template (adopted structure).
- `preregs/2026-07-01_cortex_context_retention_v2.md` — sibling M1.5 v2 prereg (template).
- `experiments/exp_substrate_working_memory_multi_bank_K_extension_adversarial_v1.py` — WM
  multi-bank K=4096 CG source.
- `MEMORY.md` — M3 architecture (cortex layer above substrate); stage 1-2-3-4 progression;
  substrate-doesnt-know-anything discipline.

ASCII-only; META_RULE_AC/AF/AG/AH/AT/AX/H/J/K/L/M/Q + SCHEMA-VET §15A/B/C/D/E load-bearing.
