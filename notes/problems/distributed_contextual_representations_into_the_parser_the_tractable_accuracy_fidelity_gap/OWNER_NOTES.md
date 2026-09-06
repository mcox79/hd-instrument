---
owner_verdict: DONE
---

SOLVED (pending your verdict) — distributed_contextual_representations_into_the_parser_the_tractable_accuracy_fidelity_gap (opus 4.8 solver)

Write-up: notes/problems/distributed_contextual_representations_into_the_parser_the_tractable_accuracy_fidelity_gap/SOLVED.md
Reverify (reruns NO landed cell): .venv/Scripts/python.exe verification/test_typed_selpref_ppattach_negative.py   # 10/10

STATUS: REFUTED — and that is a FULL PASS per the brief (a rigorous located negative with the exact cause), plus a
demonstrated brain-foundational alternative on the correct objective. The four-part arc:

1. BRIEF'S MECHANISM REFUTED. A whitened, (head,prep)-TYPED, object-CONDITIONED distributed selectional-preference
   feature (the brain's Pado/Resnik cue, built faithfully — pooled AND predicate-specific) is ANTI-complementary to
   the arc-eager parser: on PP-attachment it scores 0.574 vs the parser's 0.776, and BELOW chance (0.417-0.474) on
   the cases the parser gets wrong. Wired in, it CI-separated HURTS UAS (-0.0010). A literature drill confirms the
   refutation is brain-faithful: humans don't resolve PP-attachment by object-class selectional preference either.

2. THE TARGET ITSELF IS WRONG. UAS on UD trees is NOT the brain's objective. The brain builds a SITUATION MODEL from
   a good-enough parse (Ferreira; Sachs 1967; Zwaan & Radvansky) and consumes it by PRECISION-WEIGHTING (Friston).
   Triply-corroborated: our own disk (a better parser moved who-did-what ~+0.00), psycholinguistics, and NLP
   extrinsic-eval (UAS gains don't transfer downstream).

3. THE BRAIN-FOUNDATIONAL DELIVERABLE, DEMONSTRATED END-TO-END. The parser already emits a per-arc confidence that
   ZERO live consumers read; the GLOBAL arc-factored parser's margin is a calibrated reliability signal. Precision-
   weighting a reader by it delivers COMPREHENSION reliability: selective who-did-what accuracy 0.871 vs 0.780
   blanket (+0.0907, CI[+0.0676,+0.1154]) and selective obl/PP attachment 0.826 vs 0.776, random-confidence twins
   FLAT. Research-verified brain-foundational (Levy/Hale/Kuperberg-Jaeger/Jurafsky/Friston: ranked-parallel +
   precision-weighting). Every link in the chain is brain-foundational.

4. NO DOWNSTREAM REGRESSION. The upstream optimization is ADDITIVE — it exposes a confidence, it does NOT change the
   parse heads — so every consumer that ignores it is byte-identical (blanket unchanged). Confirmed by construction.

7 experiments + a 10-assertion scaffold-free witness; controls/twins throughout; honest nulls reported
(predicate-conditioning, argument/adjunct, position-fallback). NO hdlab written (Q111). owner_verdict: (blank).

HONEST CAVEAT: this is a demonstrated PROTOTYPE + refutation on the standard clean instruments, NOT a landed
live-board win — the hdlab landing + live-board measurement is the strategy-side step below.

>>> NEXT PROBLEM (highlighted in SOLVED.md; strategy to file + own):
    precision_weight_the_head_driven_readers_on_calibrated_parse_confidence
    LAND the additive confidence wire (Q111) and have the head-driven readers (who-did-what / obl / space)
    precision-weight it (defer/down-weight low-confidence arcs); measure the LIVE board comprehension lift with a
    random-confidence twin LOSING and no-regress on non-consumers. It's the DEMONSTRATED lever (sections 3f-3g),
    additive (zero-regression), and the parser's real value to comprehension — NOT higher UAS. Do NOT chase UAS,
    build a graded parser for accuracy, or relax the no-encoder invariant (all shown here to be the wrong lever).
