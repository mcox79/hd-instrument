# exp_dev -> research: CELL-AAA-1 (Reservation A) HARD_FAIL/REFUTED -- keep hard tier labels; AAA battery status

**Filed-by:** exp_dev (Opus) 2026-06-13 (USER-away full-auto). Verified the highest-priority reservation per your steer + the 7th USER-LOCKED reconsider-as-we-go rule. Cell: `exp_substrate_aaa1_bayesian_tier_overlay_cpu_v1.py` (HEAD 26f60418).

## CELL-AAA-1 (Reservation A: Bayesian posterior over tier) -- HARD_FAIL
5-fold CV tier-prediction from structural features (in-deg/out-deg/content-type/n-caps/has-domain), 447 tiered atoms (T1 261 / T2 76 / T3 110):
- **BAYESIAN (naive-Bayes posterior) = 0.591** vs **HARD (cell-majority) = 0.615** -> delta **-0.025** (Bayesian WORSE). Majority-baseline 0.584.
- No +3pp anywhere. Per your pre-reg (HARD-FAIL = Bayesian worse than hard): **Reservation A REFUTED for tier-prediction.** KEEP hard tier labels; the overlay does not earn its place.
- WHY: features only weakly determine tier (both models ~baseline); naive-Bayes's feature-independence assumption is violated (in-degree correlates with content-type), costing it vs exact cell-majority.
- **HONEST caveat / scope:** I tested prediction-ACCURACY, not decision-CALIBRATION/uncertainty-quantification. A Bayesian posterior's value (if any) would be in calibrated promotion-DECISIONS under uncertainty, which this cell does not test. So A is closed for the predictive use; a calibration-specific task could revisit. Flagging rather than over-claiming a full refutation.
- This is the anti-lock-in rule working in BOTH directions: we considered the alternative and the data says don't adopt it -- as valid an outcome as adopting it.

## AAA battery status (all three reservations)
- **A (Bayesian tier overlay)** -- DONE: HARD_FAIL / refuted-for-prediction (this cell). Keep hard labels.
- **B (content-type FIRST-CLASS storage)** -- AAA-2 needs a RETRIEVAL benchmark (+0.05 precision OR -50% latency). On SYNTHETIC data it would be a relabel (any partition key behaves the same; my SC/FPRS already showed partition-routing survives + flat collapses). The question "does CONTENT-TYPE specifically help" needs REAL content-typed retrieval -> recommend FOLDING AAA-2 into post-mapper Option-B SC run, exactly as you folded FPRS-content-type. Defer to post-mapper.
- **C (load-bearing axis falsifier)** -- AAA-3 GATED on SHARES_MATH edges (still 0; TOOLS:MATERIALS SHARES_MATH out-degree ratio >=1.4x). Fires once Testbed authors SHARES_MATH (from P4 clusters / my auto-discovery candidates). Deferred per your sequence.

## Net
Reservation A (highest priority) empirically closed (keep hard labels). B + C are deferred/gated (B->post-mapper Option-B; C->SHARES_MATH). I've now exhausted the UNGATED alternatives-audit work. Standing for: Testbed SHARES_MATH authoring (unblocks AAA-3 + P3) + BATCH 18 ingest (unblocks P5_v1 + FINDER re-run) + mapper (unblocks Option-B: SC-real + FPRS-content-type + AAA-2) + your next steer. Per reconsider-as-we-go: 1 of 3 reservations tested + closed honestly; not locked into adding it.
