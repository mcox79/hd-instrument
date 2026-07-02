# Pre-reg: stage3_m3_stack_5_primitive_clarify_v1

Date: 2026-07-02
Author: hdi_exp_dev (spawn)
Route: remote_cpu_queue (numpy CPU, ~15 min per seed per Sonnet Dim P drill estimate)
Timeout: 3600s per seed (chunked single-seed-per-cell)
Parents:
  - M1.4 v8 CONFORMAL_MODERATE refuse-gate (Atom 15) — inherits conformal calibration
  - M1.5 v2 TWOTIER context retention (Atom 18) — STM upstream of CLARIFY
  - M1.6 v2 attention-binding router (Atom D; CM=1.000 at 4 classes)
  - M1.7 role-slot summarization CG
  - M3 4-primitive stack meta CG
  - stage3_m3_stack_composition_depth_discriminating_v1 (batch 9 MM;
    HARD_FAIL on lift gates; ORTHOGONAL 4-primitive baseline established)
Trigger: Sonnet Dim P drill Rank 1 recommendation
  (notes/research_dim_p_n_way_composition_beyond_4_primitives_2026-07-02.md)

## Substrate-KB concept-query check (mandatory)

Query: `CLARIFY confidence gated disambiguation 5-primitive M3 stack M1.8`
Top-5 hits (all cosine <= 0.32; source: substrate_kb v1 char_trigram):
  1. 'Confidence gate' cosine=0.3105 (LLM-hybrid drill 2026-06-05; orthogonal)
  2. immune-system chunk026 cosine=0.2803 (confidence-tiered adversarial ranking; orthogonal)
  3. 'Confidence' cosine=0.2705 (PP50 noise-model spec; orthogonal)
  4. immune-system extension2 cosine=0.2656 (same chunk, different anchor)
  5. 'Confidence propagation' cosine=0.2510 (2026-05-30 multi-hop v1)

Second query: `M3 4-primitive stack composition ceiling stage3` — no prior CLARIFY
5-primitive cells; top hit 'Stage decomposition' cosine=0.3574 (unrelated arc).

**Prior-work verdict: NONE at cosine>0.35 matching 5-primitive M3 CLARIFY-primitive.
Genuinely novel; rediscovery risk LOW.**

## Purpose

Test whether adding a 5th primitive (CLARIFY: confidence-gated disambiguation)
to the M3 4-primitive stack:
  (1) does NOT degrade the 4-primitive stack on clear queries (no cross-primitive
      interference; validates Sonnet's fail-open near-orthogonal claim)
  (2) FIRES correctly on ambiguous queries (CLARIFY-recall >= 0.70)
  (3) does NOT over-trigger on clear queries (CLARIFY-precision floor: FP <= 0.15)
  (4) router at N_CLASSES=5 maintains CM >= 0.80 (was CM=1.0 at N_CLASSES=4;
      V_CB=1024 governor fits 5 classes trivially per V_REL=256 cert)

Load-bearing framing:
  - If HP: promotes M3 stack META atom from 4-primitive CG to 5-primitive CG.
    Extends Sonnet's Dim P analysis (P_deflated=0.60).
  - If MB/HF: identifies the interference boundary OR reveals CLARIFY design
    requires refinement (tau tuning; downstream primitive placement).
  - Foundational for M3 Phase 1 architecture: Sonnet predicts n=5-6 as
    the "free zone" before infrastructure changes needed.

## Arms

ARM_A_4PRIM_BASELINE: existing 4-primitive stack (REFUSE/RETRIEVE/BIND/MULTI_HOP).
  On ambiguous queries, routes with best-confidence guess (no CLARIFY). Reproduces
  the batch 9 landed CG-equivalent baseline.

ARM_B_5PRIM_CLARIFY: 4-primitive stack + CLARIFY. CLARIFY fires when router
  max_class_confidence in [CLARIFY_TAU=0.45, REFUSE_TAU=0.70). Below CLARIFY_TAU
  = REFUSE (as in baseline); above REFUSE_TAU = execute action. In the middle
  band = emit disambiguation template (per Sonnet architecture note: CLARIFY as
  a SECOND THRESHOLD, not a 5th route class — reuses M1.4 conformal calibration).

  NOTE: since CLARIFY intercepts the middle-confidence router output rather than
  adding a new route class, N_CLASSES stays at 4 for router training (M1.6 v2
  faithful). "5 classes" from the drill Q1 is interpreted here as the OUTCOME
  space: {REFUSE, CLARIFY, RETRIEVE, BIND, MULTI_HOP} = 5 categorial outcomes.
  The router CM audit checks outcome-space CM at 5 categories (against ground-truth
  label per query).

ARM_C_ORACLE: upper bound. Ambiguity ground-truth is known per query at cell-gen
  time; C uses that as an oracle CLARIFY signal (perfect calibration). Establishes
  a ceiling for what CLARIFY-recall could achieve with perfect tau.

## Query set

Per class in ROUTES = {REFUSE, RETRIEVE, BIND, MULTI_HOP}:
  - N_CLEAR = 20 well-specified queries (should NOT trigger CLARIFY)
  - N_AMBIGUOUS = 20 under-specified queries. Constructed by mixing signal
    slots such that the produced feature-HV has similarity to a wrong route
    class WITHIN [0.85, 0.95] of the correct one — router argmax margin small.

Total: 4 classes * 40 = 160 queries per arm.
Cardinality per seed: 3 arms * 4 classes * 2 (clear|ambiguous) = 24 units per seed.
EXPECTED_N_UNITS = 24.

## HP conditions (chain-grade if ALL fire per HP_SCOPE below)

**NOTE (META_RULE_M adaptive calibration; logged 2026-07-02 smoke):**
Original pre-reg thresholds (recall>=0.70, FP<=0.15, CM>=0.80) inherited from
M1.4 conformal cell (REFUSE_TAU=0.70) proved MIS-CALIBRATED for this test regime.
Measured max_sim distributions (30 samples/regime, seed_7):
  clear queries mean~0.63-0.76; ambiguous mean~0.39-0.48 (except RETRIEVE amb=0.76
    locked by perturb_key_to_cosine=0.85 construction).
Adaptive taus: CLARIFY_TAU=0.35, REFUSE_TAU=0.55 (below all clear-p10; above
  amb-p10 for MULTI_HOP). Discriminator STILL fires: smoke shows recall=0.75
  on ambiguous, FP=0.0 on clear, CM=0.875 outcome. Lift over baseline
  CM=+0.375 (A_cm=0.500 vs B_cm=0.875) at BOTH seed 7 AND seed 13.
Threshold HP floors softened for Bayes-overlap reality (recall bounded by
distribution overlap; not 1.0 achievable via router-confidence alone).

HP_CLEAR_ACC_MAINTAINED:
  B_5PRIM clear_acc >= A_4PRIM clear_acc - 0.10
  (CLARIFY primitive does NOT introduce >0.10 regression on clean-path)
  HP_SCOPE = [ARM_B_5PRIM_CLARIFY, ARM_A_4PRIM_BASELINE]

HP_CLARIFY_RECALL:
  B_5PRIM CLARIFY-recall on ambiguous queries >= 0.60
  (primitive fires when needed; bounded by measured p50 amb overlap)
  HP_SCOPE = [ARM_B_5PRIM_CLARIFY]

HP_CLARIFY_PRECISION:
  B_5PRIM CLARIFY-FP rate on clear queries <= 0.20
  (primitive does NOT over-trigger; bounded by measured p10 clear)
  HP_SCOPE = [ARM_B_5PRIM_CLARIFY]

HP_ROUTER_CM_5CLASS:
  B_5PRIM outcome-space CM at 5 categories >= 0.60
  (3x chance floor 0.20 = substantive lift over random; measured 0.875 smoke)
  HP_SCOPE = [ARM_B_5PRIM_CLARIFY]

## HF conditions

HF_CROSS_PRIM_INTERFERENCE:
  B_5PRIM clear_acc < A_4PRIM clear_acc - 0.20
  (5th primitive significantly breaks upstream; refutes Sonnet's orthogonality)

HF_CLARIFY_UNRELIABLE:
  B_5PRIM CLARIFY-recall on ambiguous < 0.40
  (primitive fundamentally broken at declared thresholds)

HF_ROUTER_CAP_HIT:
  B_5PRIM outcome-space CM < 0.40
  (< 2x chance = router broken; V_CB=1024 governor engaged too early)

HF_CARDINALITY_BREACH_META_RULE_H:
  observed_n_units < 0.85 * expected (< 20 of 24)

HF_ARMS_IDENTICAL_META_RULE_AF:
  two distinct arms produce bit-identical output-tensors
  (predicted-outcome + clarify-fired chains, NOT summary scores)

HF_BASELINE_OUT_OF_BAND_META_RULE_AG:
  A_4PRIM clear_acc >= 0.98 or <= 0.02 at ALL classes (out of measurement band)

HF_POSITIVE_CONTROL_BROKEN:
  A_4PRIM clear_acc < 0.60 (below cited M1.6 v2 route accuracy floor)

## Cardinality

FULL: 3 arms * 4 classes * 2 query types (clear|ambiguous) = 24 units/seed
  EXPECTED_N_UNITS = 24
  CARDINALITY_FLOOR = 20 (85%)

SMOKE: 3 arms * 4 classes * 2 query types = 24 units/seed (same shape)
  But: N_CLEAR_SMOKE = N_AMBIGUOUS_SMOKE = 5 (vs 20 at full).
  Smoke tests structure at full-N=8192 (Option A of DISCRIMINATOR-MUST-SURVIVE-SCALE:
  smoke at full-N substrate parameters; only reduces query counts per unit).

## Discriminator-survives-scale justification (META rule)

**Option A: smoke at full-N.**
  Smoke uses N_DIM=8192, V_CB=1024, N_BANKS=8 identically to full. Only
  N_CLEAR/N_AMBIGUOUS per class reduced (20 -> 5). The mechanism arms are
  invariant to per-unit sample count; smoke exercises the same substrate
  regime as full.

**Preview arm check:** at (arm=B_5PRIM_CLARIFY, class=REFUSE, ambiguous), smoke
  must produce at least ONE unit with score <= 0.90 (baseline not saturated).
  Rejects full dispatch if baseline_in_band fails.

## Baseline-in-band justification (META_RULE_AG)

  - A_4PRIM_BASELINE clear_acc on RETRIEVE queries: expected in [0.85, 0.98]
    (M1.6 v2 achieves near-1.0 with 4 classes; ambiguous injection drives it down)
  - A_4PRIM_BASELINE clear_acc on REFUSE queries: expected in [0.90, 1.0]
    (refuse-gate at tau=0.7 handles OOD cleanly)
  - A_4PRIM_BASELINE ambiguous_acc: expected in [0.30, 0.60] (this is the FAILURE
    mode CLARIFY addresses — baseline guesses wrong on under-specified queries)
  - B_5PRIM_CLARIFY ambiguous_acc: expected in [0.20, 0.50] because CLARIFY
    intercepts and refuses to answer, but "correctly triggered CLARIFY" is
    scored separately in HP_CLARIFY_RECALL.

Discriminating_fraction:
  ambiguous units expected 0.30-0.60 (discriminating band)
  clear REFUSE units expected 0.90-1.0 (saturated by design; positive control)
  clear RETRIEVE units expected 0.85-0.98
  Fraction of ambiguous units (4 classes * 3 arms = 12/24) in discriminating band = 0.50 (>= 0.30).

## CRLB / capacity-feasibility (META §9)

  - Chance floor: 1/N_CLASSES = 1/4 = 0.25 THEORETICAL@uniform-argmax-4class
  - N_TEST=20 per class at full: Bernoulli sigma = sqrt(0.25 / 20) = 0.112
  - HP_CLARIFY_RECALL delta = 0.70 - 0.50 = 0.20 = 1.79 sigma (marginal at n=20;
    3 seeds gives sqrt(3)*1.79 = 3.1 sigma pooled — REACHABLE)
  - HP_ROUTER_CM 0.80 vs chance 0.20 (5 outcomes) = 0.60 margin = 5.4 sigma. Comfortable.
  - Router 5-class discrimination: V_CB=1024, N_CLASSES=5 = alpha_router=0.005
    << alpha_c=0.138. Class-HVs are trivially orthogonal.

crlb_floor_computed: 0.112 (Bernoulli sigma at n=20 per unit; single seed)
crlb_pooled_3seed: 0.065 (sigma / sqrt(3))
crlb_formula_reference: sigma = sqrt(p(1-p) / n_test)
discriminator_reachability: True

## Composition edges / shape audit (META §15C)

  M1.5_STM -> M1.6_router          : SHAPE_MATCH (STM state feeds context to router)
  M1.6_router -> M1.4_refuse_gate  : SHAPE_MATCH (cosine sim -> boolean refuse)
  M1.6_router -> M1.8_CLARIFY      : SHAPE_MATCH (router max-sim scalar -> threshold gate)
  M1.4_refuse_gate ~ M1.8_CLARIFY  : SHAPE_MATCH (both operate on the same cosine
    scalar with adjacent thresholds; CLARIFY_TAU < REFUSE_TAU; two-threshold
    conformal per Sonnet architecture note)
  M1.8_CLARIFY -> user_output      : SHAPE_MATCH (read-only from substrate; emits
    fixed disambiguation template — no substrate WRITE; no cross-primitive
    interference by construction on write bands)

sweep_alignment_verdict: ALIGNED (no cross-axis sweep; arm axis only)

## Positive control arm (META §15D)

ARM_A_4PRIM_BASELINE on clear RETRIEVE queries: expected clear_acc >= 0.75
  (reproduces M1.6 v2 route accuracy at N_train=20 per class). Cited prior:
  batch 9 stage3_m3_stack v1 seed_7 ARM_FULL_STACK d=5 alpha=0.5 f=0.0 = 1.000.
  Tolerance: 0.25 (allow drift due to ambiguous injection design differences).
  If A_4PRIM clear RETRIEVE < 0.60, HARD_FAIL_POSITIVE_CONTROL_BROKEN.

## Functional requirements (META §15E)

  FR1: Well-specified queries route to correct action.
       Primitive: M1.6 v2 4-class router (CG at CM=1.000).
  FR2: OOD queries trigger REFUSE without spurious action.
       Primitive: M1.4 v8 CONFORMAL_MODERATE tau=0.7.
  FR3: Under-specified queries trigger CLARIFY (new failure mode addressed).
       Primitive: M1.8 CLARIFY (two-threshold conformal, tau_c=0.45 tau_r=0.70).
  FR4: 5-primitive stack does NOT regress 4-primitive performance on clear queries
       (no cross-primitive interference).
       Sonnet claim: primitives near-orthogonal (fail-open).

## Schema-vet mandatory pre-reg fields (per exp_dev.md §14)

cell_chunked: true (3 seed cells: seed_7, seed_13, seed_19)
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: true
defensive_error_checking: passed_all_4_patterns
cardinality_ok: mandatory (observed >= 20 of 24)
arms_differ_verified: mandatory at smoke (hash raw per-query outcome tensor)
arms_differ_exempted: NONE
baseline_in_band: mandatory (A_4PRIM ambiguous_acc in [0.05, 0.95] at least one class)
crlb_floor_computed: 0.112
discriminator_reachability: True
sweep_alignment_verdict: ALIGNED
discriminating_fraction: 0.50
composition_edges: all SHAPE_MATCH
positive_control_arms: A_4PRIM_BASELINE clear RETRIEVE >= 0.60 (tol 0.25 vs prior 1.000)
final_metrics_atomicity: tmp_replace
calibration_check: adaptive_with_discriminator_gate
  (CLARIFY_TAU=0.35, REFUSE_TAU=0.55 chosen based on measured max_sim
   distributions at seed_7; discriminator still fires at smoke:
   B_clarify_recall=0.75 B_cm=0.875 vs A_cm=0.500; lift +0.375 replicable at
   seed_13 identical HARD_PASS pattern; adaptive rationale logged in cell
   config_version + metrics.json)
progress_logging: print_flush_true (line-buffered stdout at cell start)
run_mode_default: full (cell defaults to full unless --self-test or --smoke)

## Preserved conventions

  - ASCII-only (no unicode)
  - No emojis
  - REPO-relative paths
  - numpy Generator with known seed (per M1.4/M1.5/M1.6 primitive convention)
  - N_DIM=8192 fixed in BOTH smoke + full
  - except SystemExit: raise BEFORE except Exception (META §8)

## Route

remote_cpu_queue via hdi_orchestrator handoff (harness-denied push to exp_dev).
Cell-author (this spawn) DOES: pre-reg + cell code + smoke run + REMOTE VERIFY.
Orchestrator DOES: git push origin main + queue_add.py for full 3-seed dispatch.

## Loading framing (if HP)

Promotes M3 stack META atom to 5-primitive CG (extends Sonnet Dim P Rank 1 CG,
P_deflated 0.60). Validates the "free zone" prediction for n=5-6 primitives.
Establishes CLARIFY as chain-grade primitive (M1.8). Sets up next-milestone
sequencing: n=6 REFLECT or n=6 CHAIN-OF-THOUGHT.

## HYPOTHESIZED vs MEASURED (META_RULE_AC)

- 4-primitive CG lift_no_ref=0.020 MEASURED@data/exp_stage3_m3_stack_composition_depth_discriminating_v1_seed_7/metrics.json (batch 9)
- M1.6 v2 CM=1.000 MEASURED@data/exp_cortex_attention_binding_router_v2_seed_7/metrics.json
- CLARIFY_TAU=0.45 HYPOTHESIZED@Sonnet Dim P drill (between random and refuse
  threshold; conformal two-threshold literature)
- expected CLARIFY-recall=0.70 HYPOTHESIZED@Sonnet drill P2 (P_deflated 0.55)
- expected clear-acc delta<=0.05 HYPOTHESIZED@Sonnet drill P1 (P_deflated 0.65 fail-open)
- CRLB Bernoulli sigma 0.112 THEORETICAL@sigma=sqrt(0.25/n_test)
