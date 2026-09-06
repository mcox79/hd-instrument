# Research: the two walls the OCC appraisal hit (2026-09-06) — fully drilled, with buildable mechanisms

Two walls surfaced after the appraisal PASSED. Both were research-drilled (2 parallel lit-scans, primary sources).
The headline: **wall 1 is NOT the distributional meaning channel and IS partly buildable now (measured); wall 2 needs
a NEW organ, not a patch to the existing surprisal channel.**

## WALL 1 — event<->goal OUTCOME MATCHING (satisfy vs thwart on converse/world-knowledge outcomes)
**The wall:** to appraise, decide whether an outcome event SATISFIES or THWARTS a goal when they share no word
("wanted to SELL ... a collector BOUGHT it" = satisfied; "hoped to GET the prize ... they GAVE it to another team"
= thwarted; "wanted to CATCH the train ... its tail lights shrank into the dark" = thwarted). The distributional hub
is POLARITY-BLIND: rel(sell,buy)=0.29 but rel(win,lose)=0.26 too.

**Research verdict (Cruse 1986 converseness; FrameNet Perspective_on [Fillmore/Baker]; Schank CD ATRANS 1972;
Talmy force dynamics 1988; Trabasso & van den Broek 1985 causal-network Goal->Attempt->OUTCOME; Zwaan & Radvansky
1998; Frankland & Greene 2015 PNAS role-binding in L-mid-STG; Dowty 1991 proto-roles; Jara-Ettinger 2016 naive-
utility; Gratch & Marsella 2009 EMA; Lehnert 1981 plot units):** this is a MISSING-REPRESENTATION problem, not a
meaning-strength one. Similarity answers "do these share a scene"; appraisal needs "who ends up in the goal-holder's
valued role." FOUR independent literatures converge on: run appraisal on a ROLE-FILLER / STATE representation, NOT a
similarity score. It is a SEPARABLE STRUCTURAL layer (converse-perspective lexicon + role-filler match), buildable
now from FREE resources (WordNet verb-antonymy; the closed-class FrameNet Perspective_on converse set) — **NOT the
project's Phase-1 meaning-channel bottleneck.** EMA is an existence-proof that a symbolic causal/role graph computes
appraisal "desirability" with zero word-level sentiment.

**DECISIVE TEST (built + measured — `exp_occ_converse_matching_v1.py`, n=12 converse gold):** a role-filler layer
(`_occ_upstream_goal_status.track_status_thwart converse=True`): CONVERSE-SATISFY (sell<->buy, lend<->borrow,
teach<->learn, give<->receive: goal-holder keeps their valued role), ANTONYM-THWART (WordNet antonyms + win/lose,
remember/forget: the goal-holder's own outcome is the opposite), BENEFICIARY-DISPOSSESS (an ACQUIRE goal whose theme
goes TO A DIFFERENT beneficiary). Result: baseline (head-match only) 0.417 -> **converse 0.833 (+0.417)**, fire
0.50->0.92, the goal<->event-shuffle TWIN LOSES (0.333). So the closed-class converse/perspective slice is a real,
buildable win. Residuals: a give/receive extraction quirk; a hope+beneficiary collision (the prospect branch is
theme-blind to beneficiary).

**The remaining residual is DISTINCT and open-ended:** ~10/12 of the SPARSE gold's failures are SCENE-INFERENCE
("stood on the top step of the podium" = won; "keys were in his hand" = bought; "tail lights shrank into the dark" =
missed) — Talmy force-dynamic / Schank-script world-knowledge, NOT a closed-class lexicon. That layer is the genuine
bigger build (a small library of goal-completion/failure situation templates), and IS meaning-channel-adjacent.

**Verdict:** the event<->goal wall DECOMPOSES: (a) converse/perspective/role-filler = a separable structural layer,
buildable now (measured +0.417); (b) scene-inference = an open-ended force-dynamic/script layer (the next problem).
This CORRECTS the SOLVED §5 framing ("Phase-1-gated"): only (b) is; (a) is a symbolic patch. Falsifiable prediction
from the research (HARD-PASS if a <=30-entry converse table recovers a slice to >=0.60): CONFIRMED on the converse
slice (0.83).

## WALL 2 — emotion INTENSITY (OCC likelihood / unexpectedness)
**The wall (measured):** OCC intensity is modulated by outcome UNEXPECTEDNESS. The reader's N400 surprisal channel is
ARGUMENT-LEVEL self-information P(word|local context) and is INVARIANT to the discourse expectation: "certain to pass
... he failed" and "expected to fail ... he failed" give the SAME surprisal on "failed" (1.007 both).

**Research verdict (Kutas & Hillyard 1980/1984; DeLong/Urbach/Kutas 2005 N400=cloze; Kuperberg & Jaeger 2016
hierarchical prediction; Kumar/Zacks/Hasson/Norman 2023 Cog Sci; Zacks & Swallow 2007 EST; Donchin & Coles 1988 P3b;
Schultz/Dayan/Montague 1997 reward-PE; Mellers et al. 1997 decision affect theory; Roseman 1991; Frijda/Ortony/
Sonnemans/Clore 1992; Barrett & Simmons 2015 EPIC; Seth 2013):** lexical surprisal and situation/belief-level
prediction error are DIFFERENT computations that DISSOCIATE in narrative comprehension. LOAD-BEARING: **Kumar et al.
2023** — human event boundaries in story listening track BAYESIAN surprise (KL over the model's belief distribution),
NOT next-word self-information — a clean double dissociation in narrative comprehension. Reward-PE (Schultz) +
decision affect theory (Mellers: a surprising loss feels MORE disappointing than an equal expected one) ground OCC's
likelihood variable behaviorally.

**CONCRETE FIX = a DISTINCT ORGAN, not a patch to the N400 channel:** (1) per-character belief-state extraction from
explicit stance markers ("certain","expected","doubted","hoped","feared","modal hedges") -> a coarse expected-outcome
likelihood; (2) a default base-rate prior per goal-type; (3) on goal resolution, `surprise = -log P_believed(realized
outcome)` (a coarse ordinal table avoids fake precision) -- the Schultz/Mellers compare-to-expectation shape; (4)
feed as the OCC likelihood term. Keep the argument-level N400 channel for what it is good at (local plausibility).

**CRITICAL CAVEAT (why intensity is NOT just surprise):** OCC's OWN empirical audit — Frijda, Ortony, Sonnemans &
Clore 1992 — finds unexpectedness is a REAL but SECONDARY contributor to intensity, smaller than goal-IMPORTANCE
(concern relevance). So a faithful intensity = importance (primary) + unexpectedness (secondary), NOT surprise alone.
This mirrors the substrate's own signed-value vs unsigned-salience separation (Matsumoto & Hikosaka 2009). Building
intensity from surprise alone would repeat the "surprise real but uninformative about value" failure.

**Verdict:** intensity is a clean, brain-foundational NEXT-PROBLEM (a discourse-level belief/likelihood organ +
goal-importance), NOT reusable from the N400 channel, NOT worth a cheap surprise-only hack. Deflated P(the discourse-
PE->intensity pipeline beats argument-surprisal on a fair test) ~0.45-0.50; P(the surprisal-vs-belief-shift
dissociation itself is real) high (Kumar 2023 is direct).
