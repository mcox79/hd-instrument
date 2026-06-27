# PRE-REG: stage3_hrr_involutive_systematic_generalization_v1

Author: exp_dev (Cell Author / Prover; spawn under Research lead)
Date: 2026-06-27
Anchor: `stage3_hrr_involutive_systematic_generalization_v1`
Source: research drill `notes/research_drill_typed_multibank_actively_hurts_3x_2026-06-27.md` STUB C
Authorization: USER 2026-06-27 NO LOCAL (cell-author smoke + dispatch on remote only)
Wave: Stage 3 compositional understanding (new mechanism, not typed routing)

## Scientific question

Stage 3 compositional understanding via HRR involutive operations. Brain
analog: hippocampal sequence binding + cortical schema extraction (Plate
1995 + Kanerva 1988). Tests if substrate can compose NEW facts from known
facts via involutive HRR binding (NOT typed routing).

Given training facts (subj, verb, obj_known) for many known objects, can
substrate generalize to recover the correct subject for queries
(?, verb, obj_NEW) where obj_NEW shares features with known objects via
HRR unbind chain? AND does it beat simple nearest-neighbor interpolation
(showing composition is more than feature interpolation)?

## Mechanism class

Symbolic predicate composition via HRR role-filler binding (involutive).
Composes on:
- chain-grade `hdlab/binding.py` HRR (circular convolution via FFT, exact
  inverse via conjugate); proven involutive in 2026-06-23 audit
- bipolar quantized substrate (chain-grade)
- nearest-neighbor cleanup over fact codebook

No magnitude-coupling (META_RULE_F): HRR bind/unbind are unitary-magnitude
operations on FFT spectrum; no per-fact |W| signal.

## Config

- N_DIM = 8192 (full); N_DIM (smoke) = 2048
- N_ENTITIES = 200 (full subjects + objects pool); 50 (smoke)
- N_VERBS = 10 (full); 4 (smoke)
- N_TRAIN_FACTS = 500 (full); 100 (smoke)
- N_HELDOUT_FACTS = 100 (full); 20 (smoke)
- HELDOUT_OBJ_FRACTION = 0.20 (20% of objects appear only in heldout)
- N_FEATURE_PROTOTYPES = 16 (each entity is convex combo of ~3 prototypes
  drawn from feature pool of 16; allows feature-overlap for generalization)
- FEATURE_OVERLAP_FRAC = 0.30 (each entity shares 30% of bits with ~3 prototypes)
- seeds: smoke=[11], full=[11, 13, 19] (3 seeds chain-grade)

## Arms (3 mandatory)

1. **ARM_BASELINE** — lookup-only, no composition. Stores all training facts
   as atomic bindings; tests on heldout — should fail to generalize
   (heldout objects not seen). Sanity rail: heldout accuracy < 0.15 (near
   chance for N_ENTITIES=200 sufficiently random subject choice space; for
   N_VERBS=10 across 200 entities chance is ~1/200 = 0.005 for exact-subj,
   ~0.05 for top-5; arm tests EXACT subject recall so target < 0.15).
2. **ARM_HRR_INVOLUTIVE** — the mechanism. Stores facts as
   F = sum_i bind(verb_i, bind(subj_i, obj_i)). Queries via
   unbind(verb, unbind(obj, F)) -> candidate cleanup over subject codebook.
   For obj_NEW (unseen), use HRR's superposition+unbind to extract subject
   from nearby-feature objects' bindings. Tests systematic compositional
   generalization.
3. **ARM_NEAREST_NEIGHBOR_INTERPOLATION** — control: for query (?, verb, obj_NEW),
   find k=3 nearest known obj_known by cosine, retrieve their (subj, verb)
   from training, return modal subject. Tests if substrate composition is
   more than simple feature-NN interpolation.

## Metric

Primary endpoints per arm (per-arm in metrics.json):
- `heldout_acc_mean` across 3 seeds (exact-subject recall on (?, verb, obj_NEW) queries)
- `heldout_acc_cv` across 3 seeds
- `composition_lift` = ARM_HRR_INVOLUTIVE.heldout_acc - ARM_NEAREST_NEIGHBOR.heldout_acc
- `mechanism_lift_over_chance` = ARM_HRR_INVOLUTIVE.heldout_acc - 0.05 (chance for N_ENTITIES=200)

## Pre-registered bands (strictly-above-floor per META_RULE_L)

**HARD_PASS** (chain-grade-eligible compositional HRR generalization):
- `ARM_HRR_INVOLUTIVE.heldout_acc_mean >= 0.50` (10x lift over chance=0.05)
- AND `ARM_HRR_INVOLUTIVE.heldout_acc_mean >= ARM_NEAREST_NEIGHBOR.heldout_acc_mean + 0.10`
  (composition is MORE than interpolation)
- AND `ARM_BASELINE.heldout_acc_mean < 0.15` (sanity rail: lookup cannot
  generalize without composition)
- AND `heldout_acc_cv <= 0.10` across 3 seeds for HRR arm
- AND `cardinality_ok`

**MIDDLE_BAND**:
- ARM_HRR_INVOLUTIVE.heldout_acc in [0.25, 0.50] (lift over chance but below
  10x bar)
- OR ARM_HRR_INVOLUTIVE > ARM_NEAREST_NEIGHBOR by [0.03, 0.10] (composition
  marginally above interpolation)
- OR cv in [0.10, 0.20]

**HARD_FAIL**:
- `ARM_HRR_INVOLUTIVE.heldout_acc_mean < 0.15` (mechanism null; HRR involutive
  did not enable generalization)
- OR `ARM_HRR_INVOLUTIVE.heldout_acc_mean <= ARM_NEAREST_NEIGHBOR.heldout_acc_mean + 0.02`
  (HRR no better than feature-NN; mechanism is interpolation in disguise)
- OR `ARM_BASELINE.heldout_acc_mean >= 0.30` (sanity rail violated; lookup
  arm should NOT generalize; data leak)
- OR `cardinality_ok=False` (silent unit drop per META_RULE_H)

## Discriminator survives full-N (META_RULE_K — Option A + B)

Option A (smoke at full-N regime ratios): smoke at N_DIM=2048 with same
HELDOUT_OBJ_FRACTION=0.20 and same FEATURE_OVERLAP_FRAC=0.30. The
discriminator (ARM_HRR vs ARM_NN) is regime-invariant (HRR composition
properties don't change with N as long as N >> log2(N_ENTITIES * N_VERBS)).
At N_DIM=2048 with N_ENTITIES=50, N_VERBS=4, we still have N >> log2(200) ~= 8.

Option B (analytical scale justification): HRR involutive unbind has SNR
~ 1/sqrt(K_facts_in_bundle) per Plate 1995. At smoke K_facts=100 SNR is
1/10 = 0.10; at full K=500 SNR is 1/sqrt(500) ~= 0.045. Cleanup over
N_ENTITIES=200 (full) vs 50 (smoke) codebook scales as log(N_ENTITIES);
expected cleanup accuracy degrades by ~5-10% from smoke to full. If smoke
HRR HARD_PASSes (>=0.50), full should land in [0.40, 0.55] (still
discriminating).

Per USER 2026-06-27 NO LOCAL: smoke runs on remote_cpu_queue same as full.

## Cardinality (META_RULE_H)

- EXPECTED_N_UNITS = 3 seeds * 3 arms = 9 (full)
- EXPECTED_N_UNITS_SMOKE = 1 seed * 3 arms = 3
- `cardinality_ok` MANDATORY field in metrics.json
- HARD_FAIL_CARDINALITY_BREACH if observed < expected

## No silent except (META_RULE_J)

All per-unit exceptions captured into `failures[]` list AND halt the loop.

## Q-discipline by-construction-saturation check

If `ARM_HRR_INVOLUTIVE.heldout_acc >= 0.95`, suspect saturation
(N_FEATURE_PROTOTYPES=16 might make heldout objects too easy to recover via
prototype overlap). Auto-demote MM regardless of arithmetic if saturated.

## NO-MAGNITUDE-COUPLING regression (META_RULE_F)

HRR bind/unbind are unitary-magnitude operations on FFT spectrum (Plate 1995).
Per-fact F bundle magnitude grows as sqrt(K) but cleanup is normalized cosine.
Sanity check: `cor(per_query_heldout_score, ||F||_per_query)` < 0.5.
If correlation > 0.5, demote regardless of arithmetic.

## Formula self-tests (run at module import)

1. HRR bind/unbind involution sanity: `unbind(bind(a, b), b) ~= a` at cosine
   >= 0.95 for random bipolar a, b at N_DIM=1024 (synthetic)
2. HRR superposition unbind: with F = sum_i bind(a_i, b_i),
   `unbind(F, b_j) ~= a_j` at cosine >= 0.30 for K=10 random pairs at N_DIM=1024
3. Verdict-machinery selftest: HP / HF / MB / cardinality breach synthetic cases
4. Codebook nearest-neighbor cleanup correctness (small synthetic)
5. Heldout object generation: assert HELDOUT_OBJ_FRACTION * N_ENTITIES
   entities appear ONLY in heldout (no train contamination)
6. Pre-reg envelope locks (HP_HELDOUT_FLOOR, HP_COMPOSITION_LIFT_MIN frozen)

## Queue / Dispatch

- Queue: `remote_cpu_queue` (CPU-only; HRR FFT compose fits on CPU at N_DIM=8192)
- Estimated full wall: 2-4 hr (3 seeds * 3 arms * 500 train + 100 heldout
  HRR bind/unbind cycles at N_DIM=8192)
- Per-experiment `--timeout`: 18000s (5 hr; 1.5x slack on 3-hr midpoint)
- Smoke wall budget: ~120s (1 seed * 3 arms at N_DIM=2048 with 100/20 facts)
- USER 2026-06-27 NO LOCAL: smoke gate runs on remote, not laptop

## Brain-grounding

STRONG-MEDIUM. HRR is Plate 1995 + Kanerva 1988 explicitly. Systematic
generalization is the CORE Stage 3 test per Lake-Baroni 2018 SCAN benchmark
and Fodor-Pylyshyn 1988 cognitive architecture. Brain operationalizes via
parietal binding (Singer 1999) + IFG composition (Pylkkanen 2019).

## P_deflated (lit-scan calibration)

P_deflated = 0.45 (raw 0.60, calibration -0.15 because mechanism is
established algebraic property of HRR; not novel-synthesis). Per drill STUB C.

## Honest scope

The HARD_PASS claim is bounded to: N_DIM=8192, N_ENTITIES=200, N_VERBS=10,
N_TRAIN_FACTS=500, N_HELDOUT_FACTS=100, HELDOUT_OBJ_FRACTION=0.20,
FEATURE_OVERLAP_FRAC=0.30, 3 seeds.

Mechanistically distinct from STUB A predicate composition (which composes
TWO predicates into a new one). STUB C is single-predicate generalization
via shared object features unbound through HRR involutive property.

Zero LLM calls at inference (`zero_llm_calls_at_inference=True`).
