# PRE-REG: reader_learned_clauseseg_shared_subject_v1

LEARNED CLAUSE-SEG w/ SHARED-SUBJECT PROPAGATION -- the VET-mapped reader UNLOCK. A glass-box clause
segmenter that HOLDS the subject across a coordinating conjunction ("X v1-ed and v2-ed Y" -> X subject of
BOTH) and re-binds it to the coordinated verb lacking an explicit subject, REUSING the discourse overlay's
working-memory. Replaces the hand-rule splitter's ORPHANING behavior. Glass-box, NO external LLM, local.

- Cell: `experiments/exp_reader_learned_clauseseg_shared_subject_v1.py`
- Metrics: `data/exp_reader_learned_clauseseg_shared_subject_v1/metrics.json`
- Compute: sequential-CPU, wall < 90s (glass-box POS + averaged perceptron + symbolic overlay; NO torch/GPU/LLM)
- Provenance: envelope 3rd store (00c6688b6; VET a7ecb244) + cheap wins (VET a5ef7435) + gold clause-seg
  ceiling (oracle b85422616; VET a220d138). Prior-work check: substrate concept-query top hit cosine=0.3174
  (unrelated self-cert regime-gate notes) -> genuinely NOVEL component, not a rediscovery.

## Mechanism (transparent overlay-reuse rule; brain-faithful drill a9c6465a)
Track ACTIVE_SUBJECT = resolved agent head of the most recent clause with an EXPLICIT pre-verbal subject
(the overlay's held subject; a pronoun subject is held as its RESOLVED head, e.g. "he"->"george"). A clause
is a BARE-VP CONJUNCT when preceded by a COORDINATION boundary (coordinator in {and,but,or}) AND has a main
verb AND has NO argument candidate before it (candidate_indices counts subject pronouns, so "he stopped" is
NOT bare). On a bare-VP conjunct, PREPEND the held ACTIVE_SUBJECT as a pre-verb AGENT candidate -- identical
prepend to the gold-inject ceiling, sourced from working memory instead of the oracle INJECT_SUBJ. Boundary
kinds come from re-running the SAME split regex (ORC._CLAUSE_SPLIT) with boundary tracking -> boundaries
byte-identical to the baseline splitter (asserted). ONE variable = the propagation.

## Arms (one variable = segmenter; cheap wins ON for the 3 comparison arms)
- envelope_floor    : cheap wins OFF, seg=orphan  [POSITIVE CONTROL -> byte-reproduces envelope 3rd store]
- handrule_orphan   : cheap wins ON,  seg=orphan   [FLOOR for the segmenter comparison]
- learned_clauseseg : cheap wins ON,  seg=learned  [MECHANISM]
- gold_clauseseg    : cheap wins ON,  seg=gold     [CEILING = oracle INJECT_SUBJ]

## Pre-registered bands (HYPOTHESIZED; set BEFORE the final run; can-fail)
- N5 recovered = svo(killed,wolf,sheep) RELATION in store (NOTE: N5 comprehension ANSWER stays False even
  at the gold ceiling -- orthogonal "great many" answer-engine artifact; "recovers N5" = the relation).
- all_gold_matched: learned matches oracle INJECT_SUBJ on both shared-subject sites (under=0, wrong=0).
- cmp_reaches_ceiling: learned CMP >= gold CMP - 1e-6.
- recall_reaches_ceiling: learned RELF1-recall >= gold RELF1-recall - 1e-6.
- prec_bounded: learned strict precision >= gold strict precision - 0.10 (over-propagation FP cost bound).
- Regression floors: passive == 1.00, reversal == 1.00, ref_acc identical across arms, overlay witness exit 0.

## Verdict branches (decisive, can-fail)
- CLAUSE_SEG_UNLOCK = N5 recovered + all_gold_matched + CMP & recall reach ceiling + prec_bounded + no regression.
- PARTIAL_OVERPROP  = N5 recovered but precision beyond the bound (over-fires false subjects).
- PARTIAL_UNDERDET  = N5 NOT recovered (coordination under-detected, still orphaned).
- REGRESSION        = a control regressed.
- INVALID_POSITIVE_CONTROL_FAIL = envelope_floor / gold ceiling do not reproduce their known state.

## Fairness / design-gate
- Same REAL grade-3 McGuffey passages + independent gold + COMPLETE_TRUTH + INJECT_SUBJ, imported VERBATIM.
- orphan/gold arms of MY extract byte-reproduce CFX.extract_passage_fixed at matched config (anti-copy-divergence).
- Discriminator fires (learned injects >=2 bare-VP COORD conjuncts). Determinism OMP=1, fixed seed, NO randomness.
- Real code path: self-test constructs/exercises the REAL perceptron + POS tagger + overlay + controls + witness.

## RESULT (MEASURED@data/exp_reader_learned_clauseseg_shared_subject_v1/metrics.json)
VERDICT = CLAUSE_SEG_UNLOCK (met all pre-registered bands). CLAIM-VET-pending; strategic read DEFLATED below.
- N5 relation: floor=False -> learned=True -> gold=True (recovered). N5 answer False at learned AND ceiling.
- CMP: floor 0.333 -> learned 0.667 -> gold 0.667 (reaches ceiling; gap recovered 100%).
- RELF1-recall: floor 0.800 -> learned 0.933 -> gold 0.933 (reaches ceiling; gap recovered 100%).
- Propagation vs oracle: correct=2 (both sites, correct subjects), over=2, under=0, wrong_subj=0 on gold sites.
- Controls: passive 1.00, reversal 1.00, ref_acc 0.833 identical across arms, overlay witness green.
- HONEST CAVEAT (VET-load-bearing): strict precision learned 0.465 < orphan-floor 0.514 < gold 0.526 --
  the oracle pays NO precision cost, the heuristic does (regress_below_floor=True). Of the 2 over-firings, 1
  carries a WRONG (inanimate/stale) held subject: "wished for a cool place ..." -> "time" (from a mis-parsed
  prior-clause agent). The unlock is REAL on the bounded prize (composition + orphaned-relation recall reach
  the ceiling) but NOT precision-clean. Clean version: Centering-Theory topical-ANIMATE held subject (overlay
  already exposes _topical_ranked) + tighter coordination detection (restrict to transitive direct-object VPs).
- Brain-check: text-only ceiling is below human; the brain holds the animate protagonist (backward-looking
  center) + prosody, which would fix the "time" staleness. NP-head + argument-structure remain deferred.
