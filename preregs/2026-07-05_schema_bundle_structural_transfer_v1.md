# Pre-registration: schema_bundle_structural_transfer_v1

**Filed:** 2026-07-05 by exp_dev (cell author). **Locked BEFORE smoke.**
**Cell:** `experiments/exp_schema_bundle_structural_transfer_v1.py`
**Hand-off:** `notes/research_continual_learning_schema_formation_experiment_proposal_2026-07-05.md` (anchor #1, PRIMARY).
**Prior-work check (substrate-KB concept-query, cosine>0.30):** top hits are lit-anchor
research notes (Random-Features-Hopfield "generalization phase" arXiv 2407.05658;
compositional-creativity drill) + wordnet 'generalization' entity. NO prior
experiment CELL tests bundle-based relational structural transfer. The nearest cell,
`exp_substrate_cortical_schema_extraction_compositional_generalization_v1` (MIDDLE_BAND,
best-arm 0.47), tests a DIFFERENT mechanism (category->shared-property lookup where
novel instances bind to a shared category vector), NOT subject->object relational
transfer via a bundled holistic map. Genuinely novel; consistent with the research
note's "0/80 cells test this" claim.

## Scientific question
Bundling many episodes of ONE relation-type into a segregated one-way-fed schema
store -- does it produce generalization to NOVEL, never-seen same-relation entity
pairs above random? Forgetting-prevention is DONE (c3: 0.678->0.011) but structural
transfer stayed at EXACTLY 0.000 (a separate, untouched mechanism).

## Mechanism (author revision of research draft)
The research draft's literal role-filler bundle
`S_R = bundle_i[bind(role_subj,A_i)+bind(role_obj,B_i)]` CANNOT do subject-conditional
retrieval (unbinding role_obj returns the C-independent mean object). The correct VSA
primitive for novel-subject->object transfer is the HOLISTIC / ANALOGICAL MAPPING
(Kanerva "Dollar of Mexico" 2010; Plate holistic mapping):
`M_R = mean_i bind(B_i, inv(A_i))` (one-way-fed segregated schema store; written once,
never writes back). Query novel C: `D_hat = bind(C, M_R)`; `pred = argmax_o Re<o,D_hat>`
(cleanup vs object codebook). This IS the concept-query's surfaced mechanism-class
(RF-Hopfield generalization phase) and prototype-abstraction (Posner-Keele).

## Corpus decision (author autonomy; deliberate)
SYNTHETIC clean generator with DIAL-ABLE shared structure, NOT random-encoded real KG
atoms. Rationale: structural transfer is only POSSIBLE if entities carry a systematic
subject->object transform. Random/char-trigram-encoded real KG atoms have NO such
transform (Obama*inv(USA) and Merkel*inv(Germany) are unrelated) -> transfer impossible
BY CONSTRUCTION -> an uninformative HARD_FAIL testing the ENCODER, not the schema
MECHANISM. Per `feedback_clean_encoder_tests_no_contamination` +
`feedback_smoke_clean_synthetic_data_not_substrate_state`. A real-corpus follow-up
(does the substrate's actual entity encoding carry the requisite structure?) is the
explicit NEXT cell. This cell isolates the MECHANISM given structure exists.

## Generator (FHRR complex64 phasors)
- N_DIM = 4096. K = 10 object classes / subject-cluster prototypes. SIGMA = 2.0 rad.
- Subject instance of class k = phase-jittered copy of prototype MU[k] (per-subject
  correlation with prototype ~ exp(-sigma^2/2), so any single subject WEAKLY signals
  class; the SCHEMA bundle over many subjects sharpens the mapping).
- Object o_k = distinct random phasor. Relation R: class-k subject -> object o_k.
- Training: M pairs, M/K distinct instances per class. Held-out test: FRESH jittered
  NOVEL subjects, never in training (no leakage).

## Arms (all PAIRED: identical MU/O/subjects/seed; only manipulation differs)
- `ARM_REAL` -- true class->object pairing. PRIMARY.
- `ARM_SHUFFLED` -- training object labels randomly permuted (breaks class->object
  correspondence). Genuine-structure discriminator (paired-trials). CONTROL.
- `ARM_MEAN_OBJECT` -- C-INDEPENDENT readout D_hat=M_R (no bind with C). Shows transfer
  is subject-conditional, not "return the popular object". CONTROL.

## Sweep axis
M in {10, 30, 50, 100, 200} (episodes bundled; per-class redundancy M/K in {1,3,5,10,20}).
SNR / sample-size axis (research Prediction-3 null-bracket at M/K=1). Operating point
M_OP = 200.

## Pre-registered bands (LOCKED)
random_baseline = 1/K = 0.100 (THEORETICAL, K distinct object classes).
- **HARD_PASS** (ARM_REAL only): real_gain(M200) >= 0.30 AND cv_real(M200) <= 0.30 AND
  shuffled_gain(M200) <= 0.05 AND (real - mean_object)(M200) >= 0.20.
- **HARD_FAIL** (ARM_REAL): real_gain(M200) <= 0.05 (no usable structure extracted).
- **MIDDLE_BAND**: 0.05 < real_gain(M200) < 0.30, or partial gates -> sweep M.
- **SUSPICION demote-to-MIDDLE**: real_gain(M10) >= 0.30 (transfer maxed at 1
  example/class => codebook artifact, not sample-driven schema).
- **Sanity rails**: FHRR bind-roundtrip >= 0.90; shuffled_M200 in (0.05,0.95) AND
  real_M200 < 0.95 (baseline_in_band; not saturated).

**META_RULE_L margin:** HARD_PASS gain floor 0.30; MEASURED smoke gain 0.618 (margin
0.318, >> 5% band width). Not floor-hugging.

## SCHEMA-VET fields
- `cardinality_ok`: EXPECTED_N_UNITS = n_seeds x n_M x n_arms = 3 x 5 x 3 = 45 (full);
  30 (smoke, 2 seeds). Verdict emits HARD_FAIL_CARDINALITY_BREACH if n_units < expected.
- `arms_differ_verified`: hash of per-arm novel-prediction vectors at M_OP; asserted
  distinct (MEASURED smoke: 3 distinct SHA256).
- `final_metrics_atomicity`: `tmp_replace` (metrics.json.tmp + os.replace).
- `discriminator_survives_scale`: SMOKE runs at FULL N=4096 (the discriminating regime;
  N>=8192 saturates). Smoke IS the full-N discriminator-preview. (Option A.)
- `baseline_in_band`: shuffled ~0.10 in (0.05,0.95); real not saturated (<0.95).
- `crlb`: n/a -- no CRLB noise-floor for argmax transfer. Chance floor 0.100;
  observed ceiling ~0.69 (prototype); HP abs threshold 0.400 strictly between =>
  `discriminator_reachability` = True.
- `calibration_check`: `default_ok_for_this_regime` -- (K, sigma, M, N) chosen from a
  numerical prototype band-find (scratchpad proto_confirm.py) so the sweep lands in the
  discriminating band; not tuned per-arm for PASS.
- `progress_logging`: `print_flush_true` (every seed/M line flush=True). timeout_s < 1800
  and measured wall < 60s so heartbeat exempt (defensive: start_marker + crash_diagnostic).
- `cell_chunked`: false -- runtime < 60s; runner-zombie window negligible; per-seed
  checkpoint (_seed_checkpoint write_partial) still used so a mid-run death loses <=1
  ~0.5s seed. `defensive_error_checking`: start_marker + crash_diagnostic +
  print_flush; heartbeat exempt (<60s wall).
- `run_mode_verification`: default full; smoke via --smoke / HDLAB `_smoke` / --self-test.
  Post-dispatch verify landed run_mode == full.

### Gate A -- effective vs nominal parameter audit
Swept param M; effective per-primitive: schema-bundle experiences per-class redundancy
`effective_R = M / K` (varies 1..20 across sweep). `sweep_alignment_verdict: ALIGNED`
(the discriminator directly measures per-class SNR which genuinely varies with M).

### Gate B -- bracket includes discriminating band
Predicted (prototype, complex128, N=4096 sigma=2.0):
M10=0.189, M30=0.319, M50=0.394, M100=0.512, M200=0.690. Points in [0.30,0.70]:
{M30,M50,M100,M200} = 4/5. `discriminating_fraction = 0.80 >= 0.30`.

### Gate C -- signal-shape compatibility
Composition edges (all operate on length-N phasor vectors): bind(SHAPE_MATCH) ->
bundle/mean(SHAPE_MATCH) -> bind(SHAPE_MATCH) -> cleanup-argmax(SHAPE_MATCH). No
SHAPE_MISMATCH.

### Gate D -- positive control
Novel mechanism (no prior chain-grade atom to reproduce at test regime). Positive
controls in-cell: (1) FHRR bind/unbind roundtrip self-test (cos>=0.90; MEASURED 1.000);
(2) clean sigma=0 shared-transform self-test -> ARM_REAL transfer == 1.0 (MEASURED 1.000)
+ ARM_SHUFFLED at chance (MEASURED 0.200 for K=5); (3) shuffled paired control at
operating regime (MEASURED smoke ~0.10). `regime_extension_audit`: synthetic clean
generator IS the test regime (no synthetic->narrative drift).

### Gate E -- functional requirements
1. "Form a reusable schema from many facts of one relation" -> bundle (Hebbian
   superposition) into segregated one-way store M_R.
2. "Recover the object of a NOVEL subject via learned structure" -> holistic map
   bind(C, M_R) + codebook cleanup (analogical retrieval primitive).
3. "Distinguish genuine structure from codebook collision" -> paired SHUFFLED control.
4. "Confirm subject-conditionality" -> C-independent MEAN_OBJECT control.
5. "Confirm sample-size dependence (not by-construction)" -> M-sweep + null-bracket.

## Compute architecture
Class (b) sequential-CPU with justification: substrate primitives are elementwise
complex mul (bind), vector sum (bundle), K x N cleanup (K=10 tiny). Measured full wall
~2s local (3 seeds x 5 M x 3 arms). Per-unit wall << 10s, total < 60s -> below GPU-
batching threshold. No N x N matrices. Storage strategy: BUNDLED, intentional (the
schema = bundled prototype IS the mechanism under test; not a chained-composition cell,
so META_STORAGE sharded-default does not apply).

## HP_SCOPE
`{ARM_REAL: [HARD_PASS, HARD_FAIL], ARM_SHUFFLED: [], ARM_MEAN_OBJECT: []}`. Controls
inherit no chain-grade gate (expected at ~chance).

## SMOKE RESULT (full-N=4096, 2 seeds, MEASURED, HARD_PASS)
`MEASURED@data/exp_schema_bundle_structural_transfer_v1_smoke/metrics.json`:
- curve real: M10=0.227, M30=0.310, M50=0.368, M100=0.528, M200=0.718
- real_gain(M200)=+0.618, cv=0.005, shuffled_gain(M200)=+0.003, real-cind(M200)=+0.618
- null-bracket: real_gain(M10)=+0.127 (< 0.30; genuine sample-size dependence)
- controls flat at chance: mean_object=0.100 all M; shuffled ~0.08-0.12 all M
- cardinality 30/30; arms_differ True (3 distinct digests); bind_roundtrip 1.000;
  n_llm_calls 0; elapsed 1.3s.

## FULL dispatch
Queue: `remote_cpu_queue`. Seeds [7,13,19]. timeout_s=600 (measured full wall ~2s
local; 600s = ~300x safety for remote cold-start + runner overhead; << 14400 cap).
Expected FULL (3 seeds, from prototype): real_gain(M200) ~ +0.57, cv ~ 0.07 -> HARD_PASS.

## What this does NOT show
NOT a vs-LLM comparison. NOT a claim that real KG encodings carry the structure
(explicit follow-up). NOT multi-relation coexistence (anchor #2, conditional). NOT a
language/BPC test. Zero LLM calls.
