# PRE-REG: reader_meaning_correction_case_sleep_affectedness_v1

Date: 2026-07-21
Author: exp_dev (cell author)
Status: pre-registered BEFORE full run; bands + controls fixed here.

## QUESTION (USER/Director-directed, complementary-learning-systems)
Apply the PROVEN grammar CLS (fast hippocampal case + NREM-replay sleep) machinery to
VERB-AFFECTEDNESS meaning corrections. When the who-is-affected GATE (VerbNet-lexicon
modal-graded backend) makes a lexicon-calibration error (under-fires a genuinely-affecting
verb, or over-fires a non-affecting one), log the correction as a fast one-shot CASE, then
a SLEEP pass generalizes accrued cases into a schema store. CORE QUESTION: does the
SLEEP-generalized schema fix HELD-OUT (NEVER-CASED, verb-DISJOINT) gate errors? = the
improving/generalization property, on the MEANING surface.

## FAILURE SURFACE (oracle = independent blind-annotator gold; NON-circular)
Combined who-is-affected gold, 6-class taxonomy {patient, transfer, effected /
target_not_affected, none, negated}:
  - data/ud_ewt_semantic_affectedness_gold_v1/gold.json (56; blind to gate lexicon)
  - data/mcguffey_whoaffected_oracle_gold_v1/gold.json (34)
  - data/mcguffey_whoaffected_oracle_gold_v2_heldout/gold.json (38)
Combined N ~ 128 instances. BINARY gold: gold_yes = type in {patient, transfer, effected}.
BASELINE (loop OFF) = the REAL v2 gate `full_gate(...,"baseline")` (negation -> hand
copula/stative/light -> VerbNet lemma-modal graded<0.35 -> force NONE), reused UNCHANGED
(read-only import). base gate decision = (not base_force_none). base ERROR = decision != gold_yes.

HONEST CAVEAT (designed-around, not hidden): meaning corrections are ORACLE-DEPENDENT (no
self-supervised text-internal signal for "did the verb affect its object", unlike grammar
which had parser-internal coherence). Pre-measured: a build-time VerbNet-aggregation oracle
(max per-sense affecting-sense score) agrees with the blind gold only ~0.46 -> the corrections
CANNOT come from VerbNet aggregation; they MUST come from the gold. So the surface is small
(oracle-scarce) and the generalization is a GENUINE can-fail question. Small-N noise floor is
reported explicitly.

## SIGNATURE (glass-box, GOLD-FREE, mutation-probed)
Dense bipolar HD bundle (N_SIG=512, deterministic hashlib feature codes, NO PYTHONHASHSEED) of:
  - VerbNet structural fingerprint of the verb lemma (from lexicon per_sense): tokens
    vn:{vn_class}, vntype:{affectedness_type}, levin:{n}, pred:{predicate_name} across ALL
    senses; modal:{modal_type}; nsenses:{bucket}; gradedbucket:{modal_score_bucket}.
    (The base gate uses only the MODAL score; the corrector may lean on the FULL per-sense
    structure the modal aggregation discarded -- a legitimate structural cue, NOT a gold leak.)
  - argument-context (gold-free, from the reader's own parse): frame:{parse_sig},
    objanim:{T/F/None}, neg:{0/1}, hasloc:{0/1}.
The signature NEVER reads the gold type / gold affected-span / gold_yes.
LEAK DISCIPLINE (hard): mutation-probe permutes gold type+affected across instances -> every
signature byte-identical. Self-test asserts it.

## MECHANISM (RECOMBINATION of certified primitives; NO production-hdlab or lexicon mutation)
  - FAST case (hippocampus): hdlab.hippocampal_encoder.HippocampalEncoder (DG sparse + CA3
    one-shot) over SEEN base-error signatures -> SEEN recall sanity.
  - SLEEP / cortex (generalize): dense Hebbian W [role x sig] via hdlab.continual.replay_cycle
    (NREM re-Hebb) over (signature, correction) case pairs. Correction = binary {AFFECTED, NONE}
    role code. (The additive/superposition PRINCIPLE realized as the Hebbian W the certified
    NREM-replay primitive consolidates; AdditiveKGMap KGE-SGD is the WRONG tool for a
    signature->role associative store -- same call as the grammar template.)
  - SCHEMA (report): hdlab.schema_exemplar_bayes.SchemaExemplarBayesIndex clusters SEEN case
    signatures -> glass-box rules (are the meaning-errors coherent clusters? role purity).
  - GATE (vigilance): hdlab.glass_box_loop.cleanup_with_margin -> override the base decision
    ONLY when readout margin >= tau. tau = the ONE KNOB (ART-vigilance), calibrated on SEEN
    only to maximize SEEN net_gain = fixes - breaks (the regression-constraint sets vigilance).

## CORRECTION TARGET = binary gate decision (AFFECTED vs NONE). This is the lexicon meaning-fact
being corrected (isolated from reader-extraction noise). 2-class -> SCRAMBLE control can fire.

## DESIGN-GATE (pre-registered, verified at smoke)
  (1) REAL baseline = the actual v2 gate `full_gate(...,"baseline")` decision (loop OFF),
      base_gate_acc in-band (0.05..0.95).
  (2) CAN-FAIL: cases may NOT transfer across verbs -> held-out fix-rate ~ 0 (or scramble does
      not collapse) = clean honest NEGATIVE. (Pre-measured 0.46 VerbNet-vs-gold agreement makes
      this a live possibility.)
  (3) DIFFICULTY-ON: held-out verbs genuinely unseen (verb-DISJOINT split; per-seed).
  (4) ONE-VARIABLE: loop on/off, then coherent vs scrambled cases; then vigilance vs blind.

## MUST-FAIL CONTROLS (BOTH required; must FIRE at smoke)
  (a) SCRAMBLE case<->correction (shuffle the binary correction among cases) -> held-out
      generalization gain MUST COLLAPSE toward base-rate (learning is coherence-driven, not
      exposure). Gate: coherent_fix - scramble_fix >= 0.15.
  (b) REGRESSION GUARD (vigilance): the tau vigilance must PREVENT over-broad rules from
      re-grading already-correct held-out verbs. Compare held-out regressions (breaks on the
      correct-set) at the calibrated tau vs a BLIND override (tau=0, always apply store readout).
      Guard HOLDS iff regression_rate_at_tau <= 0.20 AND regression_rate_at_tau is lower than
      the blind regression_rate by >= 0.10 (vigilance demonstrably bounds over-broad rules).

## BANDS (LOAD-BEARING tier gate)
  REAL_IMPROVING_PROPERTY : scramble collapses held-out fix by >= 0.15 (coherent - scramble)
        AND mean net_gain > 0 AND every seed net_gain > 0 AND rescue_precision
        (fixes/(fixes+breaks)) >= 0.60 AND regression-guard HOLDS AND leak-clean.
  MEMORIZATION_OR_NO_TRANSFER : held-out fix-rate < 0.10 (no transfer) OR scramble does NOT
        collapse (mean collapse < 0.05) OR mean net_gain <= 0 OR regression-guard FAILS.
  MIDDLE_BAND : between. (Expected non-trivial probability given oracle-scarcity + 0.46 VerbNet
        agreement; a MIDDLE/NEGATIVE result is a VALID informative outcome, not a cell failure.)
  base_rate = majority-decision base-rate among held-out errors (diagnostic reference only).

## CELL-TEMPLATE MANDATORY
  - arms_differ_verified at smoke gate (coherent vs scramble store readouts differ; base vs loop)
  - final_metrics_atomicity: tmp_replace
  - except SystemExit: raise BEFORE except Exception (no BaseException)
  - crlb_n/a: generalization fix-rate measurement (no matmul noise floor); small-N noise floor
    reported = 1/n_heldout_err
  - baseline_in_band: base_gate_acc in (0.05, 0.95) verified at run
  - discriminator survives scale: smoke = FULL combined surface (N~128), 1 seed (option A)
  - cardinality_ok: EXPECTED per-seed rows = len(seeds); verdict counts len(per_seed)
  - calibration_check: adaptive_with_discriminator_gate (tau on SEEN net_gain; scramble/guard
    controls verify discriminator still fires)
  - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
  - deterministic_seeding: true (OMP/MKL/OPENBLAS=1; fixed int seeds; default_rng; hashlib codes;
    sorted(set) splits; NO hash()-seeded RNG)
  - progress_logging: print_flush_true

## COMPUTE / OPS
Compute class (b) sequential-CPU (justified: ~128 gold rows through the persisted glass-box
front-end + tiny numpy/torch matmuls, 3 seeds, wall < ~180s; no matmul inner loop -> not a GPU
candidate). Storage: sharded episodic (hippocampal per-case) + dense superposition (cortical W).
LOCAL-only, foreground-to-completion; NO queue, NO origin push, NO remote-persist, NO git add of
the store, NO production hdlab mutation, NO mutation of the production lexicon (read-only; the
"additive-map lexicon fold" is realized IN-CELL as the Hebbian W, never writing lexicon.json).
NO atom bank (skunkworks VETs + banks after land).

## PRIOR-WORK CHECK
substrate_query.sh "verb affectedness lexicon correction case sleep consolidation meaning" ->
top hits generic lexical nodes (CN_correction 0.3916, consolidation 0.3906, affection 0.3896;
no built cell) at cosine < 0.40. Direct template = exp_reader_selfimprove_case_sleep_udewt_v1
(GRAMMAR arc-labeler surface) -> this ADAPTS it to the MEANING/verb-affectedness surface (novel).
Adjacent exp_affectedness_weak_sup_revival_loop_v1 = contrastive-PERCEPTRON weak-sup on NP-patient
SELECTION with a WordNet-lexname signal -> DIFFERENT mechanism (perceptron, not hippocampal+replay)
and DIFFERENT target (NP-selection, not verb-lexicon decision). Genuinely novel. CITED@KB 2026-07-21.
