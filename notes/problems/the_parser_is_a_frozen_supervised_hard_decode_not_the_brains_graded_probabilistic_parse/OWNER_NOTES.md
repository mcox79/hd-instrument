---
owner_verdict: DONE
---

SOLVER SUBMISSION — the_parser_is_a_frozen_supervised_hard_decode_not_the_brains_graded_probabilistic_parse

STATUS: PARTIAL (a rigorous located result + genuine BF wins + a fully-characterized ceiling; the bar's
"located-negative-with-a-number" clause is a full pass). Glass-box, NO LLM, NO hdlab/ writes (Q111 — results +
proposed diffs; strategy lands). Threads capped. Reverify: .venv/Scripts/python.exe
verification/test_parser_graded_route_through.py  (66 checks). READ FIRST in the problem folder: SOLVED.md
(§6 what-to-improve, §7 BF-findings), DEVIATION_LEDGER.md (the top-down signal-loss trace + the corrected
reframe), CHAIN_VS_BRAIN_EVALUATION.md, COMPONENT_REGISTER.md (26 cells), HDLAB_INTEGRATION_SPEC.md.

THE BAR RESULT. Routed the reader's parse through the exact graded probabilistic parse (Chu-Liu/Edmonds +
single-root Matrix-Tree marginals, brute-force-verified) replacing the hard-decode. On UD-EWT (+ a 2nd
out-of-domain gold, GUM): the graded decode beats the greedy hard-decode CI-sep but only +0.002 UAS —
because ~99% of head error is SCORER error the exact decode cannot touch (the located wall, with a number).
Downstream: the true argument the single parse drops is almost always alive in the posterior (patient recall
0.951->0.991); reliability-gated top-2 competition is a net win. ACQUISITION answered: a treebank-supervised
scorer is an admissible offline FOUNDATION consumed as the graded posterior; the blocking defect is the
hard-decode (fixed), and reading-learned acquisition is prototyped (Brown POS 0.745; reading scorer 0.46) but
caps at the text-only ceiling.

LAND NOW (BF, recall path byte-identical; HDLAB_INTEGRATION_SPEC.md):
  1) ArcParser.parse(decode="exact") on the read path (+0.002 UAS CI-sep, heads change only on 7.2% invalid
     trees) + swap the NOT_BF fitted-logistic parse_confidence -> the raw graded MARGINAL (AUC 0.855 > 0.736;
     removes a fitted component). graded_parser: DORMANT -> LIVE.
  2) reliability-gated top-2 marginal reach into graded_competition (net patient-arc F1 win, twin loses).
  3) the stacked BF STRUCTURAL cues on the reading-learned scorer: incremental left-corner (verb-arg recall
     0.627->0.740) + coordination-parallelism (cc/conj 0.078->0.218); complementary, UAS 0.464->0.476.

KEY FINDINGS / CORRECTIONS (the enabling moves):
  * The parser's remaining loss is STRUCTURAL + CONFIDENT supervised-acquisition errors — NOT semantics/
    grounding. Refuted for attachment (all twin-controlled): lexical, distributed embeddings, DMV valence
    (faithful soft-EM, brute-verified), GEK grounding, thematic-fit, coarse-class supersense coherence,
    bootstrapping, world-model rescoring. Attachment is locality-dominated; semantic signals HURT it.
  * CORRECTED (owner challenge): "the only lever is a generative world model" was an over-claim by
    elimination — RETRACTED. DIFFERENT losses need DIFFERENT task-specific BF mechanisms at the right grain:
    parse attachment -> incremental STRUCTURE (this solution); discourse-identity coref -> situation-model
    focus + coarse-class coherence (a sibling solver's win, verified NOT to transfer to attachment).
  * UNIFYING INSIGHT: the frozen supervised organs' errors are CONFIDENT (POS 87% confident-wrong; parse:
    only 1.3% of tokens uncertain but 21% wrong) — so NO reliability-gated/defer/arbitrate mechanism can
    reach them; they are acquisition-baked.
  * Down-to-the-math BF: only the graded decode + Matrix-Tree marginals + forward-backward POS posterior +
    inside-outside DMV + Brown MI-exchange are exact-BF (all brute-force-verified); the scorer/POS/labeler
    WEIGHTS are supervised (admissible foundation, not brain-acquired).

WHAT THE COMPONENT NEEDS (SOLVED.md §6): land 1-3; then the SCORER ACQUISITION (20.7-pt dominant loss) is the
filed follow-on (reading-learned scaling; residual to human = missing PERCEPTUAL grounding, a separate
main-event program — NOT text-derivable). POS acquisition (3.0 pt) fixable via reading-learned categories.

AUDIT UPDATES (SOLVED.md §7 + BF_AUDIT_UPDATE.md): graded_parser DORMANT->LIVE; parse_confidence fitted-logistic
-> marginal (fitted component removable); arc_parser/arceager NOT_BF re-pointed (decode BF-fixable; the residual
NOT_BF is the SCORER ACQUISITION, not the decode); pos_tagger loss is 100% acquisition (hard-decode BF-equivalent).

HONEST BOUNDS: nothing beats the supervised foundation (0.78) or a competent reader (~0.96) — that gap is the
text-only acquisition ceiling + missing grounding, rigorously characterized, not an implementation gap. The
BF wins are real but modest in UAS; the value is a fully-BF decode + task-specific structural levers + a
precisely-drawn line where the grounded-world-model program must take over. QUESTIONS: none blocking.
Awaiting owner_verdict: DONE.
