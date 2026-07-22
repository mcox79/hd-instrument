# Pre-reg: learned_composition_glue_pun_selectional_generalization_v1 (2026-07-22)

CHAIN-GRADE ATTEMPT (USER-authorized). LOCAL-ONLY, no push. Foreground-to-completion.

## Question
Can the substrate's PROVEN atomize+sleep loop (hippocampal case -> continual.replay_cycle NREM
consolidation -> glass_box cleanup readout, from exp_reader_meaning_correction_case_sleep_affectedness_v1)
LEARN a selectional-composition constraint (verb -> required-object-feature) in a GENERALIZING,
grammar-like way that TRANSFERS to HELD-OUT verbs it was not trained on AND that VerbNet lookup
CANNOT cover -- OR does it reduce to selectional-lookup / memorize like the meaning-correction case
did (atom ~aac7856c)?

## Testbed (puns; frequency fails by construction)
- Two verb classes, each requiring a different object-feature:
  - comestible: eat/drink/swallow/... (VerbNet HAS +comestible SELRESTR -> lookup-COVERED)
  - communication: read/recite/sing/quote/narrate/... (VerbNet has NO +communication SELRESTR for
    these -> lookup-UNCOVERED; measured 2026-07-22: read/recite/sing/quote/narrate/chant all req=[]).
- Each verb paired with a curated pun noun of its class whose WordNet-DOMINANT sense lacks the
  required feature and a subordinate sense carries it (comestible pool from the viability probe;
  communication pool score/piece/passage/line/air/round/key/sheet/measure/pitch -- all verified
  dominant-lexname != noun.communication, a subordinate sense == noun.communication).
- Accuracy = fraction of held-out (verb-disjoint) pun items resolved to the correct required feature
  (deterministic sense-resolution given predicted feature). Frequency picks dominant -> 0 by
  construction. Majority-feature baseline reported explicitly.

## Arms (ONE variable = the composition mechanism)
1. FREQUENCY  -- pick dominant sense (MUST-FAIL on puns; ~0 accuracy).
2. LOOKUP     -- VerbNet SELRESTR of the test verb -> required feature; abstain->dominant if
   uncovered (the near-binary MM signal the viability probe showed).
3. LEARNED-REAL -- verb code = bipolar bundle of the verb's WordNet hypernym-path lemma atoms
   (gold-free structural similarity; within/across-class Jaccard measured 0.16/0.025). W consolidated
   over TRAIN (verb-code -> feature-code) via replay_cycle; readout = cleanup_with_margin. THE LEAP.
4. LEARNED-RANDOM (sign-flip control) -- identical loop but verb code = one random atom per lemma
   (identity preserved, cross-verb meaning-similarity DESTROYED).

## Discriminators (pre-registered)
- GENERALIZATION: learned-real held-out accuracy above majority + above frequency + at/above lookup
  ON THE LOOKUP-UNCOVERED subset (communication held-out verbs; lookup=freq=0 there).
- LEARNING CURVE: held-out accuracy rises with # train verbs accrued.
- SCRAMBLE: permute verb->feature train labels -> learned-real collapses (memorization guard).
- SIGN-FLIP (the real-vs-free-algebra test, 29437 inverse): destroying meaning-structure (real->random
  codes) must HURT learned-real (real-beats-random). If random >= real, it is NOT using meaning =
  free-algebra signature = NOT the leap.

## Bands
CHAIN_GRADE_CANDIDATE_PENDING_VET (do NOT self-declare; -> fresh adversarial VET + USER):
- mean learned_real held-out acc >= 0.70 AND every-seed >= 0.60
- learned_real acc on lookup-UNCOVERED subset >= 0.60
- learning-curve rise (full - min_frac) >= 0.15
- scramble collapse (real - scramble) >= 0.20
- SIGN-FLIP (real - random) >= 0.15
MEASURED_MECHANISM (honest likely outcome; a fine, valuable result):
- learned_real held-out <= 0.55 (~majority; no generalization) OR
- sign-flip does NOT fire (random >= real - 0.05 -> free-algebra) OR
- scramble does NOT collapse (real - scramble < 0.10) OR
- no uncovered advantage (uncovered acc <= 0.15 -> reduces to lookup)
MIDDLE_BAND: otherwise.

## Design gate
Real baselines (frequency + VerbNet lookup + majority-feature). Can-fail (learned might memorize /
reduce to lookup / not beat majority / random>=real). Difficulty-on (real held-out verbs disjoint
from train; adversarial puns where frequency fails). One variable (composition mechanism).

## Compute / discipline
sequential-CPU seconds (N=1024, ~36 verbs, W 1024x1024, replay over ~22 train verbs, 5 seeds full /
1 smoke). No storage write, no atom bank, no push, no remote. Determinism OMP/MKL/OPENBLAS=1,
hashlib feature codes, default_rng/torch.Generator, sorted(set) splits. ASCII only. print flush.
DISCRIMINATOR-SURVIVES-SCALE option A: smoke = full corpus, 1 seed (no larger-N regime exists).
final_metrics_atomicity=tmp_replace; SystemExit before Exception; arms_differ asserted; leak-probe
(codes gold-free / label-permutation invariant) asserted.

## Honest conflict-of-interest note
Director/USER WANT the leap. Most likely = MEASURED_MECHANISM. A CG-candidate is NOT self-declared;
caveat pre-registered: the generalization signal (WordNet hypernym similarity) is itself KB-derived,
so even a full-gate pass is a CANDIDATE a VET must adjudicate (learned-generalizing-mapping vs
structured-lookup), not a self-called CG.
