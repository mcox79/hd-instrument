# Pre-registration: exp_multipred_argstruct_enumext_v4

Filed: 2026-07-23. Inline-local FULL run (pause-state ACTIVE at ship time; no queue_add; skunkworks VETs
separately per contract). Full mechanism rationale + citations live in the cell's own module docstring
(`experiments/exp_multipred_argstruct_enumext_v4.py`); this file records the bands as pre-registered BEFORE
the FULL run executed.

## Question

Does extending the parser-integrated multi-predicate reader's candidate-ENUMERATION (not role-assignment) to
two residual structure classes -- (1) DO/HAVE-as-lexical-main-verb, (2) ECM/small-clause subject-sharing --
lift 29483's own `V3_INTEGRATED` (cited: F1=0.5738, recall_ceiling=0.70, precision=0.4861, MEASURED@
data/exp_multipred_argstruct_agentfix_kbgate_v3/metrics.json) past its own ceiling, without precision
collapse? And what fraction of the STILL-missing gold patients (after this extension) are single-sentence
parse-recoverable-in-principle vs genuinely cross-sentence/situation-model-bound?

## Arms

BASELINE, V3_INTEGRATED (cited reproduction), V4_DOHAVE_ONLY, V4_ECM_ONLY, V4_FULL (headline),
V4_ARCSCRAMBLE (must-fail control -- real parse structure vs deterministically scrambled decoded arcs).

## Pre-registered bands (set BEFORE the FULL run)

- HARD_PASS_ENUMEXT_LIFTS_PAST_INTEGRATED: recall_ceiling(V4_FULL) >= 0.72 (0.70 cited + 0.02) AND
  F1(V4_FULL) >= 0.5938 (0.5738 cited + 0.02) AND precision(V4_FULL) >= precision(V3_INTEGRATED) - 0.03 AND
  F1(V4_FULL) > max(F1(V4_DOHAVE_ONLY), F1(V4_ECM_ONLY)) (components combine, neither alone explains the
  full lift) AND F1(V4_ARCSCRAMBLE) <= F1(V4_FULL) - 0.05 (must-fail control).
- HARD_FAIL_ENUMEXT_NO_LIFT_OR_PRECISION_COLLAPSE: ANY of recall_ceiling(V4_FULL) <= 0.70 OR
  F1(V4_FULL) <= 0.5738 OR precision(V4_FULL) < precision(V3_INTEGRATED) - 0.05 OR
  F1(V4_ARCSCRAMBLE) >= F1(V4_FULL) - 0.01 (must-fail control failed to fail).
- MIDDLE_BAND: otherwise.

Delta convention (+0.02 on recall_ceiling and F1) matches the precedent 29483 itself used against its own
29478 citation -- a tight, decisive band appropriate for a cell extending a real MEASURED anchor, NOT the
calibration-probe +/-50% widening reserved for anchor-free theoretical probes.

## Fairness

Same reader/gold/split as 29473/29478/29483 (FULL_SLICE = L04/L05/L07/L08/L09/L10/L12; SMOKE_SLICE =
L04/L05); gold = `data/gold_mcguffey_lccp_argstruct_v1.json` (independent, single-annotator, never read while
authoring the do/have lookahead rule or the ECM-propagation logic). ONE primary axis = candidate-enumeration
extension; parser training / role-assignment clf / subcat-gate formula / knowledge-argmax mechanism all
byte-identical reuse of 29478/29483's own code.

## Compute architecture

Class (b) sequential-CPU with justification (see module docstring). LOCAL-ONLY, foreground-to-completion,
no push / no remote-persist / no queue_add.

## Cell-template gates declared

arms_differ_verified (hash test, all 6 arms), final_metrics_atomicity=tmp_replace, except SystemExit/
KeyboardInterrupt raised before except Exception (no BaseException), baseline_in_band
(0.05 < precision(BASELINE) < 0.95), discriminator-fires at smoke (V4_DOHAVE_ONLY and V4_ECM_ONLY both
differ from V3_INTEGRATED's kept-hash at SMOKE_SLICE scale), two scaffold-free witnesses (do/have-lexical
recovery; ECM subject-sharing recovery -- witness 2 non-fatal WARN at smoke-budget parser per the same
parser-training-budget caveat 29483's own witness 2 documented), deterministic seeding (fixed SEED,
numpy default_rng, sorted(set), no hash()-seeded RNG).

## Residual-miss classification (KEY DELIVERABLE)

For every gold patient still missing after V4_FULL: SINGLE_SENTENCE_PARSE_RECOVERABLE if the gold patient
token appears anywhere in the sentence's own raw text (miss is bounded by parse/tagger/role-assignment
quality, not by information outside the sentence); CROSS_SENTENCE_OR_SITUATION_MODEL_BOUND otherwise (the
fact is only recoverable via cross-sentence coreference/tracking). Reported as counts + the full per-item
list in `metrics.json` (`residual_miss_classification`, `n_single_sent_recoverable`, `n_cross_sent_bound`).

## N-suffix

No `_n<N>` suffix in the anchor name; not applicable (no N-dimensionality axis in this cell).
