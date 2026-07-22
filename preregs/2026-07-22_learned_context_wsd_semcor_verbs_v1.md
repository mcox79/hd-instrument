# Pre-reg: Learned glass-box contextual WSD vs MFS on SemCor verbs (v1)

Date: 2026-07-22
Author: exp_dev (hdi_exp_dev)
Cell: experiments/exp_learned_context_wsd_semcor_verbs_v1.py
Class: LOCAL-ONLY foreground analysis cell (no queue dispatch, no substrate KGStore/atoms objects).

## Question

Does a LEARNED, glass-box, in-substrate model over SPECIFIC context (not coarse
type) beat a strong most-frequent-sense (MFS) frequency baseline on real
sense-tagged text, where FIXED features could not?

Context (this session's cross-domain frequency-wall): FIXED features do NOT beat
MFS -- VerbNet-frame gate (atom 29434, N=31 null) and WordNet-supersense typing
(atom 29435, well-powered SemCor null, p=0.81; type signal REDUNDANT with
frequency). The VET's honest bound: any next feature must carry information
ORTHOGONAL to sense-frequency. This cell tests whether a LEARNED model over
SPECIFIC context carries that orthogonal signal.

## Mechanism (glass-box, brain-grounded)

Model = Naive Bayes over specific context content-words (the classic glass-box
WSD model; surfaced by substrate KB: "even simple bag-of-words context windows
achieve 70-80% WSD"). Brain grounding: usage-based, error-driven learning of
selectional/contextual sense-preferences from experience, NOT fixed lookup
(research_brain_precision_lever_selectional_error_driven_loop_2026-07-17.md:
the missing precision lever is MEANING-conditioned co-occurrence, learned from
the corpus, combined via an explicit weighted rule) + learned-front-end /
fixed-composition division of labor
(research_brain_systematicity_binding_learned_frontend_2026-07-20.md).

Naive Bayes DECOMPOSES exactly into the two signals under test:
  score(sense) = log P(sense | lemma)          # PRIOR = the frequency signal
               + sum_w log P(w | sense, lemma)  # CONTEXT = the orthogonal signal
- context-OFF (prior only, argmax) == the supervised MFS baseline (same train counts).
- context-ON (prior + learned context-likelihood tables) == full learned model.
Weights log P(w|sense) are a plain inspectable dict (glass-box; no neural net).

## ONE variable

context ON vs OFF, SAME train/test split, SAME prior. Nothing else differs.

## Prior-work check (mandatory)

substrate_query.sh top hits all cosine < 0.30 (max 0.2979). Closest relevant =
preregs/2026-06-22_contextual_encoding_hrr_binding_smoke_v1.md (0.292) = a
SYNTHETIC 30-word hand-written-context centroid-cosine probe, NOT real SemCor,
NOT learned-vs-MFS. This cell (real SemCor verbs, learned specific-context NB vs
strong MFS + fixed-coarse baseline, learning curve, held-out) is NOVEL relative
to prior arc work; the 2026-06-22 smoke is related-but-distinct (synthetic).

## Data / regime (MEASURED before pre-reg)

- Source: nltk SemCor, WordNet-sense-tagged, verbs (hardest POS). LOCAL.
- MEASURED@probe: 88084 sense-tagged verb instances total; polysemous lemmas
  (>=2 observed senses, >=10 total count) = 915 lemmas / 75456 instances;
  avg 4.55 senses/lemma; MFS full-data upper-bound accuracy = 0.575.
- Regime = polysemous verb lemmas, MIN_COUNT>=10. Supervised lexical-sample
  style: per-lemma stratified 70/30 train/test split (every test lemma is seen
  in train; you cannot disambiguate a lemma never trained). Deterministic
  np.random.RandomState(SEED) over sorted instance order (NO python hash()).

## Arms

- A_MFS (context OFF): argmax_s P(s | lemma) from TRAIN counts. The strong baseline.
- B_LEARNED (context ON): full Naive Bayes, specific context tokens. The mechanism.
- C_FIXED_COARSE: NB but each context word replaced by its WordNet supersense
  (lexname) bucket -- coarse TYPE, reproduces the fixed-feature gate in-cell.
- D_SCRAMBLE (must-fail): B's pipeline, but TRAIN context-bags permuted across
  instances (sense labels untouched -> marginals/prior preserved -> destroys only
  word<->sense co-occurrence). Lift must vanish.

## Metrics (held-out TEST only)

- accuracy per arm on the SAME test instances.
- McNemar paired test B vs A: chi2 = (|b-c|-1)^2/(b+c), b=A-wrong&B-right,
  c=A-right&B-wrong; report chi2 + p-value.
- delta CI: bootstrap 1000x over test instances, 95% CI on (accB - accA).
- Learning curve: train B on fractions [0.1,0.2,0.4,0.6,0.8,1.0] of TRAIN,
  eval on the FIXED held-out test. accA (MFS) reported at each (expected ~flat).
- Glass-box dump: top log-likelihood-ratio context words per sense for >=2
  example lemmas; assert weights are a plain dict (inspectable).

## Design-gate (all 4 + learning curve)

1. REAL baselines: A_MFS (strong frequency) + C_FIXED_COARSE (fixed type). YES.
2. can-fail: learned context might NOT beat MFS (honest frequency-ceiling null),
   or might MEMORIZE (held-out test + scramble control catch it). YES.
3. difficulty-on: SemCor polysemous verbs at scale; MFS=0.575 in-band with
   large headroom. YES.
4. one variable: context ON vs OFF, same split/prior. YES.
5. learning curve measured (flexible/improving property) + held-out (not memorize). YES.

baseline_in_band: 0.05 < 0.575 < 0.95. TRUE.
discriminator headroom: 42% of instances MFS-wrong -> room for context. TRUE.

## Pre-registered bands (BEFORE running)

Let LIFT = accB(context-ON) - accA(MFS) on held-out test at full train.

HARD_PASS (MEASURED_MECHANISM tier -- glass-box learned beats frequency-wall):
- LIFT >= +3.0 pp (absolute, held-out) AND
- McNemar p < 0.01 (B significantly differs from A) AND
- learning curve rising: accB(full) - accB(10% train) >= +2.0 pp AND
- must-fail holds: SCRAMBLE lift (accD - accA) <= +1.0 pp (collapses to MFS) AND
- specific > coarse: (accC - accA) < 0.5 * LIFT (fixed-coarse does not capture
  the learned specific-context signal).

HARD_FAIL (honest frequency-ceiling bound OR invalid):
- LIFT <= 0 OR McNemar p > 0.05  -> reader sense-assignment at frequency ceiling
  even with learning (strong honest bound; brain-check required), OR
- SCRAMBLE lift >= 0.5 * LIFT -> the "lift" is a base-rate artifact, not learned
  context (INVALID, diagnose), OR
- memorization: TRAIN lift >> held-out lift with held-out LIFT ~0 (<1pp).

MIDDLE_BAND: LIFT significant (p<0.05) but < 3.0 pp, OR LIFT>=3pp but learning
curve flat (<2pp rise) -- context helps but not the flexible-improving property.

HONEST FRAMING: supervised context-WSD beating MFS is EXPECTED in the
literature. Novel value = (a) glass-box + in-substrate, (b) the
flexible/improving LEARNING CURVE + held-out generalization (not memorization),
(c) confirming LEARNING breaks the frequency-wall that FIXED features hit. Do
NOT over-claim chain-grade: WSD is assignment, not compositional generalization.

## Discipline fields

- arms_differ_verified: smoke hash-checks A/B/C/D predictions differ.
- baseline_in_band: TRUE (MFS 0.575).
- final_metrics_atomicity: tmp_replace (metrics.json.tmp -> os.replace).
- crlb_n/a: "no HD noise floor; accuracy is a supervised-classifier metric, not
  a capacity/argmax-noise cap. Feasibility set by MFS headroom (measured 0.575)."
- except SystemExit: raise BEFORE except Exception (no BaseException, no bare except).
- nondeterminism: np.random.RandomState(SEED) + sorted order; NO python hash()/list(set()).
- start_marker_written / crash_diagnostic_present: TRUE.
- calibration_check: default_ok_for_this_regime (NB add-alpha=0.1; MFS headroom measured).
- real_code_path: N/A (no substrate KGStore/fit objects; numpy+nltk only).

## Amendments (at smoke gate, before FULL verdict; traceability)

1. SMOKE caught a broken model spec: plain Naive Bayes with per-sense
   denominator (n_s + alpha*V) has a class-imbalance/length bias -> the frequent
   (MFS) sense gets a larger unseen-word penalty, so held-out predictions drift
   to rare senses (smoke: learned 0.263 << MFS 0.505, train-lift +0.395).
   FIX (principled, not tuned vs test): context term -> POSITIVE-EVIDENCE PMI
   vote -- only context words with train co-occurrence count >= MIN_EV=2 add
   log[P(w|sense)/Pbg(w)]; the prior anchors the score so context cannot
   systematically drift below MFS. Still glass-box learned counts; still
   decomposes prior(=MFS) + context. Bands unchanged.
2. FAIRNESS / capable-learner: added the dominant WSD cue (Yarowsky; Ng & Lee) --
   local POSITIONAL COLLOCATIONS L1/L2/R1/R2 alongside the +/-WINDOW=10 content
   bag -- so a null cannot be blamed on a position-blind strawman.
3. Added data-density stratification (test lemmas by train-instance count) to
   distinguish a genuine frequency-ceiling from a thin-per-lemma-data artifact.
   This is load-bearing for the verdict, not decoration.
