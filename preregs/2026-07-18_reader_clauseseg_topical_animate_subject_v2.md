# PRE-REG: reader_clauseseg_topical_animate_subject_v2

CLAUSE-SEG w/ TOPICAL-ANIMATE HELD SUBJECT -- the VET-recomputed clean version of the v1 clause-seg unlock.
Replaces the v1 LAST-ACTIVE held subject (which over-fires precision BELOW the do-nothing floor because it
can hold a STALE INANIMATE noun, e.g. "time") with a CENTERING-THEORY TOPICAL-ANIMATE held subject sourced
from the discourse overlay (_topical_ranked, animate-filtered via grounded animacy). Glass-box, NO external
LLM, local foreground-to-completion. NO push / NO remote-persist.

- Cell: `experiments/exp_reader_clauseseg_topical_animate_subject_v2.py`
- Metrics: `data/exp_reader_clauseseg_topical_animate_subject_v2/metrics.json`
- Compute: sequential-CPU, wall ~60s (glass-box POS + averaged perceptron + symbolic overlay; NO torch/GPU/LLM)
- Provenance: v1 clause-seg unlock (775c6085c; VET acc75e96) + cheap wins (VET a5ef7435) + gold clause-seg
  ceiling (oracle b85422616; VET a220d138) + envelope 3rd store (00c6688b6; VET a7ecb244).
- Prior-work check: substrate concept-query top hits are generic WordNet atoms ("propagation" cos 0.40,
  "coordination" cos 0.38) + an unrelated ferry note -> NO prior arc-cell at cosine>0.30; genuine continuation
  of 775c6085c, not a rediscovery.

## Mechanism (transparent overlay-reuse rule; brain-faithful Centering drill a9c6465a)
ONE variable vs v1 = the held-subject SOURCE at a bare-VP COORD conjunct:
- learned_lastactive (v1): ACTIVE_SUBJECT = resolved agent head of the most recent explicit-subject clause.
- learned_topical (this): TOPICAL-ANIMATE protagonist = among the overlay's ANIMATE entities (grounded
  animacy via ORC.is_animate), the WorkingOverlay._topical_ranked backward-looking center = max by
  (frequency count, then FIRST-mention primacy). None if no animate entity is held (-> do NOT inject).
Boundaries byte-identical to the hand-rule splitter (asserted); cheap wins (self-loop + role-fix) ON;
coref/role unchanged. Only the held-subject source differs across the two learned arms.

## Arms (one variable = held-subject source; cheap wins ON for the 3 comparison arms)
- envelope_floor     : cheap wins OFF, seg=orphan            [POSITIVE CONTROL -> byte-reproduces envelope 3rd store]
- handrule_orphan    : cheap wins ON,  seg=orphan            [FLOOR for the segmenter comparison, no recovery]
- learned_lastactive : cheap wins ON,  seg=learned_lastactive [v1 BASELINE: recovery yes, precision below floor]
- learned_topical    : cheap wins ON,  seg=learned_topical    [MECHANISM: topical-animate held subject]
- gold_clauseseg     : cheap wins ON,  seg=gold              [CEILING = oracle INJECT_SUBJ]

## Pre-registered bands (HYPOTHESIZED; set BEFORE the final run; can-fail)
- keeps_recovery: learned_topical n5_relation True AND CMP >= gold CMP - 1e-6 AND RELF1-recall >= gold - 1e-6.
- precision_neutral: learned_topical strict precision >= orphan floor - 0.005 (restored to the do-nothing floor).
- no_inanimate_overfire: zero over-firings whose held subject is inanimate (ORC.is_animate == False).
- Regression floors: passive == 1.00, reversal == 1.00, ref_acc identical across arms, overlay witness exit 0.

## Verdict branches (decisive, can-fail)
- CLAUSE_SEG_CLEAN        = keeps_recovery + precision_neutral + no_inanimate_overfire + no regression.
- PARTIAL_LOST_RECOVERY   = precision fixed but recovery lost (topical held wrong subject for a coordinated verb).
- PARTIAL_PRECISION_STUCK = recovery kept but precision still below floor.
- REGRESSION              = a control regressed.
- INVALID_POSITIVE_CONTROL_FAIL = envelope_floor / gold ceiling / v1 do not reproduce their known state.

## Fairness / design-gate (self-test verified BEFORE full)
- Same REAL grade-3 McGuffey passages + independent gold + COMPLETE_TRUTH + INJECT_SUBJ, imported VERBATIM.
- REAL baselines: handrule_orphan (do-nothing floor 0.514) AND learned_lastactive (v1, below floor) -- not strawman.
- orphan/gold arms byte-reproduce CFX.extract_passage_fixed (anti-copy-divergence). Discriminator fires
  (topical injects 4 bare-VP COORD conjuncts). ONE variable = held-subject source. Determinism OMP=1, NO randomness.
- Real code path: self-test constructs/exercises the REAL perceptron + POS tagger + overlay animacy + controls + witness.

## RESULT (MEASURED@data/exp_reader_clauseseg_topical_animate_subject_v2/metrics.json)
VERDICT = PARTIAL_PRECISION_STUCK. CLAIM-VET-pending; strategic read DEFLATED below.
- KEEPS RECOVERY (as designed): N5 relation floor=False -> topical=True -> gold=True. CMP 0.333 -> 0.667
  (ceiling; gap 100%). RELF1-recall 0.800 -> 0.933 (ceiling; gap 100%). Controls: passive 1.00, reversal 1.00,
  ref_acc 0.833 identical across arms, overlay witness green. NO regression.
- HELD-SUBJECT SOURCE FIXED (brain-faithful, as designed): the v1 stale INANIMATE hold is GONE. On L34_geo2
  the held subject changed "time" (inanimate) -> "george" (the animate topical protagonist); inanimate_overfire
  1 (v1) -> 0 (topical). This is the correct Centering backward-looking-center behavior.
- PRECISION NOT RESTORED TO FLOOR (the pre-registered band that FAILED): strict precision floor 0.5143,
  v1_lastactive 0.4651, topical 0.4762 (delta_vs_v1 +0.0111), gold 0.5263. Topical stays BELOW floor by 0.038.

## Honest deflate + localization (VET-load-bearing; REFINES the acc75e96 decomposition)
The task's premise (from VET acc75e96) predicted the held-subject source change ALONE would remove "exactly the
4 'time' FPs" -> precision 0.5128 = at floor. The faithful implementation shows this is NOT the case, and WHY:
- The geo2 FP is NOT caused by the WRONG (inanimate) subject. Even with the CORRECT animate subject "george",
  the clause "wished for a cool place where he might rest and eat his dinner" yields junk svo relations
  svo(wished, george, {cool, place, dinner}) = 3 FPs. "wished" is non-factive; cool/place/dinner are not real
  patients. v1's "time" produced 4 such FPs; topical's "george" produces 3 (one self-loop removed). Both below floor.
- So the residual precision gap is NOT the held-subject source -- it is the coordination DETECTION over-firing on
  non-factive coordinated verbs (geo2 "wished", susie2 "thought"), whose downstream complement/argument parse
  yields FPs REGARDLESS of the (now-correct) subject. This is the SAME class the VET flagged for susie2
  ("correct-subject downstream complement mis-parse, a different workstream") -- geo2 belongs to it TOO once the
  subject is corrected. The gold oracle omits both clauses (they recover nothing wanted), which is why it pays no
  precision cost.
- NET: topical-animate is the correct brain-faithful held-subject mechanism (Centering; zero inanimate holds;
  keeps recovery) and it CLEANLY ISOLATES the residual precision gap to a DIFFERENT component -- coordination
  detection / argument-structure parsing of non-factive coordinated verbs (restrict injection to clauses whose
  verb is transitive with a real direct object). That is the next (precision-GAIN) component, out of scope for
  this one-variable cell. Precision-neutrality is NOT reachable by the held-subject source alone.
- Brain-check: the brain holds the animate protagonist (topical is correct) AND uses lexical/aspectual knowledge
  that "wished for a cool place" is a mental-state complement, not a factual svo -- our reader lacks that verb-class
  filter (the argument-structure component), so it over-extracts. Same-limitation direction => the fix is the
  argument-structure component, consistent with the roadmap (NP-head + arg-structure = next components).
