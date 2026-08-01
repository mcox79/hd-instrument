# Prereg: grammar-learner earn-mechanism -- encounter accumulation -> rule uncovering ->
# generalization to novel instances (FIRST cell on the USER-greenlit EARN path)

Filed alongside `experiments/exp_grammar_learner_encounter_rule_uncover_generalize_v1.py`.
CHEAP/CPU by design (measurement-first diagnostic, not a GPU build); run LOCAL-ONLY,
foreground-to-completion. Bands below were declared for the ORIGINAL symbolic-primary design;
the mid-build Director brain-fidelity steer (2026-08-01) re-centered the PRIMARY mechanism onto
an FHRR structural-binding store (structure-content factorization, TEM/CLS-faithful) with
proginduction demoted to a secondary legibility readout -- this file documents both the original
declared bands (unchanged numerically) and which arm they now gate.

## What this build tests

The USER's grammar-learner loop: encounter an unseen instance -> LOG it + give it an EXACT
answer (assignment/lookup) -> accumulate encounters -> the discovery/learning system identifies
the pattern across logged encounters -> GENERALIZES -> the induced rule applies correctly to
NOVEL instances never given answers. Tested on a SMALL SYNTHETIC PLANTED rule (author-known
ground truth) so the discovery claim is falsifiable.

## Reused machinery (no invent-from-scratch)

- `hdlab/learner/plugins/proginduction_plugin.py` (bounded boolean-DSL program synthesis,
  MDL-selected) -- SECONDARY legibility readout (human-readable formula view).
- `hdlab/learner/plugins/estimation_plugin.py` 'generic_mdl' mode (Laplace per-key counting,
  fixed-default fallback on unseen keys) -- CAN-FAIL FLOOR (pure lookup, no generalization).
- `hdlab/atoms.py` (`make_atom_fhrr`, `similarity`) + `hdlab/bundling.py` (`bundle`) -- PRIMARY
  mechanism: FHRR structure-content-factored store (new assembly of existing primitives, no new
  hdlab module).

## Planted rule (ground truth)

4 boolean atoms: `precedes_verb, is_definite, is_proper_noun, follows_comma`.
`label = AGENT if XOR(precedes_verb, is_definite) or (is_proper_noun and not follows_comma) else
PATIENT`. Genuinely relational (XOR term, not conjunction-representable). Full 16-combo truth
table computed + regression-asserted in `_instrumentation_selftest`.

## Splits (declared, deterministic -- not hash()/random-drawn)

HELD_OUT_INDICES = [1, 2, 12, 14] of the sorted 16-combo enumeration -> 4 combos, balanced
2xAGENT / 2xPATIENT (asserted). TRAIN = remaining 12 combos. Held-out combos NEVER appear (with
an answer) anywhere in the encounter stream -- asserted (leakage guard) at self-test and full.

## Encounter stream

N_STREAM=256, sampled WITH REPLACEMENT from the 12 TRAIN combos under a fixed Zipf-like weighting
(`weight[i] = 1/(i+1)` over a fixed sorted TRAIN order) via `random.Random(20260801)` (fixed int
seed, not hash()-derived, PROT-023). 2 decoy boolean literals per encounter (present in the raw
feature stream, not in either plugin's declared atom/key set) -- distractor-robustness check.

## Learning curve

CHECKPOINTS = [4, 8, 16, 32, 64, 128, 256] cumulative encounters. Both/all arms re-fit from
scratch on `stream[:N]` at each checkpoint and evaluated on the SAME 4 held-out-novel combos.

## Pre-registered bands (PRIMARY mechanism = FHRR structural-binding arm, post-steer)

- `MECHANISM_FINAL_ACC_HARD_PASS_MIN = 0.95` (held-out-novel accuracy at N=256)
- `MECHANISM_FINAL_ACC_MIDDLE_MIN = 0.70`
- `FLOOR_MUST_FAIL_MAX = 0.60` (estimation-plugin floor, ANY checkpoint; THEORETICAL=0.50 exactly,
  fixed-default guess on the balanced 2/2 held-out set)
- `RISE_REQUIRED`: mechanism accuracy at smallest checkpoint (N=4) strictly less than at largest
  (N=256) -- the accumulate-then-generalize signature.

HARD_FAIL if: mechanism final < 0.70, OR floor exceeds 0.60 at any checkpoint (can-fail floor did
not fail -> test broken), OR a held-out combo leaks into the stream, OR the FHRR-mechanism and
floor arms produce identical predictions at every checkpoint (META_RULE_AF).

If mechanism final lands in [0.70, 0.95) with rise_ok=True and floor_flat=True: MIDDLE_BAND, not
a broken test -- report the specific held-out combo(s) missed and whether the legibility readout
(proginduction) independently converges on the SAME missed combo(s) (convergent-diagnosis check
for a genuine information-theoretic identifiability gap in the TRAIN/HELD-OUT split, vs a
mechanism-specific defect).

## Compute architecture

Class (b) sequential-CPU. proginduction: n_atoms=4 boolean DSL search, MEASURED 6732 functions
enumerated at max_nodes=9 in ~1.1s (local .venv probe, 2026-08-01). FHRR: N_DIM=2048 complex64
vectors, 10 bind terms (4 atom + 6 pair) per encoding, <=12 distinct combos bundled per class per
checkpoint. 7 checkpoints x up to 3 arms = <=21 learn+eval units, all sub-second. Wall time
MEASURED ~4-6s self-test, full run same order of magnitude. LOCAL-ONLY, foreground-to-completion,
NO queue, NO push, NO remote-persist, NO atom bank (skunkworks VETs separately if this is
promoted to a capability). Deterministic: OMP/MKL/OPENBLAS_NUM_THREADS=1, fixed int seeds
(20260801) throughout, no hash()-derived RNG/ordering (PROT-023).

## Cell-template mandates (applicable subset)

- `arms_differ_verified` at full (hash test, FHRR-mechanism vs floor predicted-class tuples
  across all checkpoints).
- `final_metrics_atomicity: tmp_replace` (`os.replace`).
- `except SystemExit`/`KeyboardInterrupt`: raise BEFORE `except Exception` (no `BaseException`).
- `crlb_n/a`: accuracy/generalization-curve measurement, not a capacity/CRLB-bound cell.
- `baseline_in_band: n/a` (estimation-lookup IS the discriminating must-fail floor under test).
- `discriminator survives scale: n/a` (fixed small synthetic domain; discriminator is the
  held-out-novel generalization gap itself).
- `cardinality_ok`: `EXPECTED_N_UNITS = len(CHECKPOINTS) * 3 arms = 21`.
- `calibration_check: default_ok_for_this_regime`.
- `deterministic_seeding: true`.
- All numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ in the cell docstring.

## Prior-work check (substrate_query.sh, run before authoring)

Top hits at cosine>0.30: (1) 0.337 "Induction heads and OOD generalization" (research lit-scan
note, background reading); (2) 0.320 "Usage-based construction induction" (research lit-scan
note, background reading). Neither is a built/run experiment. Closest BUILT prior work:
`experiments/exp_learner_program_induction_symbolic_extrapolation_v1.py` (banked, prereg
`preregs/2026-07-23_learner_program_induction_symbolic_extrapolation.md`) -- validated
proginduction_plugin mechanism-soundness via a single real missing-cell fill + two
FULL-DOMAIN-COVERED synthetic generality tasks (no held-out-novel test, no learning curve, no
FHRR arm). This cell is NOT a rediscovery: new held-out-novel-combo design + accumulate-encounters
learning curve + explicit reused-machinery can-fail floor + (post-steer) brain-faithful FHRR
structural-binding primary mechanism, all new angles building on the existing plugin machinery.
