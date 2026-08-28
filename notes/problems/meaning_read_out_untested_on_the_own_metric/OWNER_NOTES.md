---
owner_verdict: DONE
---

SUBMISSION — SOLVER RESULT for problem: meaning_read_out_untested_on_the_own_metric
STATUS: PARTIAL  (brief's inferred hypothesis REFUTED on its own top-1 metric; a brain-foundational
                  ALTERNATIVE framing established and fully controlled; forward mechanisms specified)
LEDGER: malformed/incomplete 0; already re-verified + integrated (rated EXCELLENT); this is the
        COMPLETE record incl. the post-integration alternative-framing + fidelity work.
REVERIFY (scaffold-free; reproduces the top-1 headline + re-confirms the instrument to the digit):
    .venv/Scripts/python.exe verification/test_meaning_readout_own_metric.py

================================================================================
WHAT WAS ASKED
================================================================================
Two meaning read-outs won on BORROWED scorers (meaning_fusion ~0.45 WordSim; taught-direction
distributional_meaning_channel ~0.84 substitutability). The substrate's OWN metric -- grounding
precision (for each grounded term, pick ONE anchor; hit = it is a gold ConceptNet neighbour) -- is
where the stage is declared broken and where plain co-occurrence COUNTING beats the live rule 2-3x.
Nobody had scored the new read-outs there. Bar: a read-out, through the read-out path, must beat
first-order COUNTING CI-separated over the floor's UPPER bound, with an info-free twin LOSING.

================================================================================
THE ANSWER
================================================================================
On the brief's TOP-1 metric: NO -- the read-outs LOSE to counting, CI-separated below it, on every
seed. Decisions the brief gates: (a) stage 2 is NOT fixed by these read-outs; (b) WIRING = NO -- do
not wire either read-out into the reader for meaning assignment.
BUT the top-1 metric is the wrong instrument: scored the brain-faithful way (graded DISCRIMINATION,
not a single argmax), the read-outs -- especially the grounded spoke -- BEAT counting decisively, and
a targeted brain-fidelity drill independently predicts every result from pinned neuroscience.

================================================================================
KEY REALIZATIONS (the enabling moves, not just the result)
================================================================================
1. THE OWN METRIC IS FREQUENCY-DOMINATED, AND THAT IS WHY EVERY MEANING TRANSFORM LOSES TOP-1.
   Raw counting 0.057 vs PMI-NORMALISED counting 0.007 (pooled): removing the frequency confound --
   the textbook first step toward "meaning" -- makes the score 8x WORSE. The metric rewards
   syntagmatic frequency; the read-outs compute paradigmatic similarity, near-orthogonal to it.
   Adding TOP_PPMI as a second floor is the measurement that made this visible.
2. THE READ-OUTS' WINS ARE PAIRWISE/RANKING; THE OWN METRIC IS TOP-1 RETRIEVAL. So I scored the SAME
   gold as DISCRIMINATION (rank neighbours above non-neighbours) -- and the read-outs win. A count
   (the ORACLE ceiling: gold neighbour reachable among co-occurrents ~0.48, in vocab ~0.80, while
   counting lands it ~0.06) proved the top-1 misses are RANKING failures, not coverage -- which
   licensed the reframe instead of giving up.
3. LAYERED CONTROLS CAUGHT A REAL CONFOUND INSTEAD OF HIDING IT. The grounded discrimination (0.73 on
   hard negatives) is HALF a concreteness effect (concreteness-alone scores 0.71). Matching negatives
   to positives on concreteness (gap 0.018 z-units) stripped it out -- and a REAL residual
   sensorimotor-meaning signal SURVIVED at 0.65 while the distributional spoke collapsed to 0.36.
4. EQUAL-WEIGHT FUSION IS SUBOPTIMAL BY THE HUB'S OWN LOGIC. On hard negatives, fusion (0.59) sits
   BETWEEN good grounded (0.73) and bad reading (0.35) -- the signature of an additive average with a
   bad summand. The fix ("weight grounded more for concrete concepts") is what the pinned ATL
   control-gating mechanism predicts, not a hack.
5. THE READ-OUTS' LIVE STORE HAS ZERO COVERAGE OF THE SCORED TERMS. ConceptSpace.observe_context_counts
   fires only for SEED vocab -- 0 of the 441 grounded terms. Reading what a resource COVERS (not just
   what it scores) caught that the read-outs could not even address the task as wired.

================================================================================
THE ARC / WHAT WAS MEASURED (3 seeds; own-metric population reproduced EXACTLY: grounded 572/490/571,
scorable 441/398/441; vectorized scorers reproduce the live organ APIs to <3e-15, asserted every run)
================================================================================
TOP-1 (the brief's scorer) -- reproduced to the digit, read-outs LOSE CI-separated:
  TOP_COOC (counting) 0.0476/0.0653/0.0590  = landed TOP_COOCCURRENT exactly
  SUBSTRATE (live rule) 0.0159/0.0302/0.0272 = landed exactly
  FUSION 0.0068/0.0226/0.0091 | CHANNEL 0.0204/0.0101/0.0136 | READING 0.0091/0.0201/0.0227
      -- all paired-CI below counting on every seed
  TOP_PPMI 0.0045/0.0126/0.0045 (pooled 0.0070, 8x below raw count -> metric is frequency-dominated)
  Best route (halfway-mandate): TOPK_GROUNDED (frequency selects top-K salient co-occurrents; grounded
    hub picks within them) beats counting NUMERICALLY at every K in {5,10,15,20,30} and beats its
    info-free twin CI-separated, but NOT counting CI-separated even pooled n=1280 (best TOPK30_GROUNDED
    d=+0.0133, CI [-0.0008,+0.0273], touches zero). ~26 route families swept; NONE clears the bar.

DISCRIMINATION (the brain-faithful ALTERNATIVE; DIFFERENT scorer -- its AUC does NOT cross to top-1):
  RANDOM negatives:  COUNT 0.639 | READING 0.732 | GROUNDED 0.760 | FUSION 0.795 (read-outs beat
                     counting CI-separated; info-free grounded twin 0.488 = chance)
  HARD negatives (co-occurring non-neighbours, matched on co-occurrence; matched population):
                     COUNT 0.210 (BELOW chance -- prefers co-occurrents) | READING 0.352 (below chance)
                     | GROUNDED 0.728 | FUSION 0.589. GROUNDED & FUSION beat counting CI-separated.
  CONCRETENESS CONTROL (v4): concreteness-alone AUC 0.706 ~= full grounded 0.726 -> ~half confound.
  CONCRETENESS-MATCHED (v5, the decisive control): match gap 0.018 z-units; CONC_ONLY 0.502 (match
                     confirmed), COUNT 0.207, READING 0.360 (does NOT survive), GROUNDED-no-concreteness
                     0.648 [0.639,0.658] SURVIVES, info-free twin 0.486 (chance).
  => the GROUNDED SENSORIMOTOR spoke carries a GENUINE but MODEST conceptual signal (~0.65) that
     co-occurrence (0.21) and the distributional spoke (0.36) cannot; ~half of the raw 0.73 was a
     concreteness/imageability confound (a real but coarse semantic dimension).

================================================================================
CONTROLS (what each EXCLUDED)
================================================================================
- INFO-FREE TWINS ALL LOSE: shuffled-grounding fusion ~= fusion (grounding adds nothing on top-1);
  random-teacher taught direction ~0; random candidate/vocab ~chance; shuffled-grounding TOPK
  CI-separated BELOW the real one; shuffled-grounding discrimination twin at chance (0.49).
- ORACLE CEILINGS separated COVERAGE from RANKING (misses are ranking failures, headroom exists).
- TWO COUNTING FLOORS: raw TOP_COOC and PMI-normalised TOP_PPMI; read-outs must beat the stronger.
- CONCRETENESS control (v4) + concreteness-MATCHED negatives (v5) separated real sensorimotor meaning
  from the concreteness confound -- the control that reproduces the win from the WRONG source.
- Instrument reproduced to the digit vs landed exp_grounding_precision_gold_v1; organ-API fidelity
  <3e-15; population saved (per-item hit vectors) in metrics.json.

================================================================================
BRAIN-FIDELITY AUDIT (independent drill; findings above are what PINNED mechanisms predict)
================================================================================
1. HUB INTEGRATION. PINNED: non-linear, CONTROL-GATED, LEARNED graded spoke weight (semantic-control
   net, L-IFG/pMTG). OUR-INVENTION: fixed equal-weight ADDITIVE z-fusion (largest divergence).
   "Weight grounded more for concrete concepts" is the pinned prediction, not a task artifact.
2. READ-OUT FORM. PINNED: meaning read-out is GRADED goodness-of-fit (N400); winner-take-all is a
   LATER downstream decision. So DISCRIMINATION/AUC is brain-faithful; TOP-1 ARGMAX is the artifact
   (it scores a downstream stage where raw frequency dominates).
3. GROUNDED SPOKE. PINNED: sensorimotor strength predicts better than concreteness (Connell & Lynott
   2012); concreteness is a half-confound. Use the 11 sensorimotor dims as CONTENT; treat concreteness
   as a GATING signal, not a representational dimension. (The drill predicted the v5 result.)
4. SELECTION. PINNED: attractor CLEANUP onto a STORED-CONCEPT inventory (Rogers 2004; Plaut & Shallice;
   Chen 2017), not argmax over raw co-occurrents -- structurally removes the frequency-wins problem.
   NOTE: a weaker form (restrict to grounded concepts, grounded pick; cells v2) was tested and did NOT
   beat counting on top-1, so the full attractor build is a real NEXT experiment with a MODEST prior.

================================================================================
CAVEATS / WHAT I DID NOT ESTABLISH (withdraw first if wrong)
================================================================================
- The discrimination AUC is a DIFFERENT scorer from the brief's top-1 precision; it does NOT overturn
  the top-1 result -- it reframes what the top-1 result MEANS. No number crosses the two.
- The residual sensorimotor signal (0.648) is robust (twin at chance) but MODEST -- do not claim the
  grounded spoke "solves" meaning; claim it carries real conceptual signal frequency/distribution do not.
- The attractor-cleanup mechanism's win margin on this gold is PREDICTED by the drill, not measured;
  its weak form already failed top-1.

================================================================================
FILES
================================================================================
experiments/exp_meaning_readout_own_metric_v1.py              (top-1 cell: base read-outs + floors + oracle + TOPK)
experiments/exp_meaning_readout_own_metric_v1_ksweep.py       (route-completeness K x {grounded,fusion,reading})
experiments/exp_meaning_readout_own_metric_v2_brainfaithful.py(concept-inventory cleanup + fast-map)
experiments/exp_meaning_readout_own_metric_v3_discrimination.py (the DISCRIMINATION reframe; random+hard negs)
experiments/exp_meaning_readout_own_metric_v4_concreteness_control.py (concreteness confound quantified)
experiments/exp_meaning_readout_own_metric_v5_concreteness_matched.py (concreteness-MATCHED -> real residual)
verification/test_meaning_readout_own_metric.py               (scaffold-free witness; REVERIFY)
data/exp_meaning_readout_own_metric_v1/metrics.json           (3-seed; saved hit-vectors)
notes/problems/meaning_read_out_untested_on_the_own_metric/SOLVED.md (full record incl. addendum)

================================================================================
FOR THE STRATEGY SESSION (you own hdlab + integration, board Q111)
================================================================================
1. Re-verify: .venv/Scripts/python.exe verification/test_meaning_readout_own_metric.py
2. WIRING = NO for these read-outs on top-1 meaning assignment (they lose to counting).
3. The METRIC-FAIRNESS follow-up you filed is answered here: the top-1 argmax scorer is the artifact
   (frequency-dominated; the brain's meaning read-out is graded), and the read-outs are more faithful
   than the top-1 metric gives them credit for.
4. FORWARD MECHANISMS (hdlab builds; each with the info-free + concreteness controls this work
   established): (a) control-gated GROUNDED-WEIGHTED fusion (learn/sweep the gain, non-linear
   interaction term -- expect fused AUC to move from 0.59 toward/above 0.73); (b) switch the primary
   meaning-assignment scorer to GRADED goodness-of-fit (AUC/softmax-prob) with a swept decision
   temperature; demote top-1 argmax to a downstream-decision diagnostic; (c) prototype STORED-INVENTORY
   ATTRACTOR CLEANUP (restrict candidates to stored concepts, settle, read graded energy) -- modest
   prior on top-1, but it is the one mechanism that structurally removes the frequency-wins problem.
5. If the distributional spoke is used at all, first extend ConceptSpace.observe_context_counts to
   accumulate for GROUNDED terms (today it covers 0/441 of the scored terms).

================================================================================
PLAIN-LANGUAGE TLDR
================================================================================
Judged the brief's way -- one best guess -- the meaning tools lose to plain word-counting, because
that scoring is hijacked by raw "showed-up-nearby" frequency, which the tools rightly ignore. Judged
the way the brain actually works -- is this a real relative, or just a word that turns up nearby? --
the tools WIN: the "hands-on-feel" sense tells true relatives from co-occurring impostors, while
counting does worse than a coin flip. We checked hard: about half of that win was just "both words are
concrete," but a real, if modest, meaning signal survives after we control for that. A targeted brain-
science drill says our whole picture is exactly what the real brain mechanisms predict -- and it names
the next builds (blend the two senses with a smart, learned weight; score by graded fit not a single
guess; settle onto a known concept). Those are jobs for the integration session, not more analysis.
