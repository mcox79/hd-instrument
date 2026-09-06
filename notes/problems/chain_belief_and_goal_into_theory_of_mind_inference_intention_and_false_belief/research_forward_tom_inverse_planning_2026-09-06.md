# Research drill: FORWARD Theory-of-Mind inverse planning (2026-09-06)

Web-verified against primary sources (hdi_research drill). Each finding tagged PINNED-BY-EVIDENCE vs
OUR-INVENTION-UNDER-TEST. Two grounding levels kept separate: NETWORK-level neural (distinct mentalizing
network -- rTPJ belief, dmPFC intention) vs COMPUTATIONAL-level (Bayesian ToM = a rational-analysis model).

## The computation to copy (PINNED)
- FORWARD (belief,desire)->action is the CORE of Bayesian ToM: attribution is the Bayesian *inversion* of a
  forward planner, so running it forward evaluates the model's generative component directly. Policy is a
  soft-max over expected utility evaluated on the BELIEF state: pi(a|b) ~ exp(beta*Q(b,a)), Q = reward-cost;
  beta->inf recovers ARGMAX (correct for the single-goal case). Baker, Saxe & Tenenbaum 2009 (Cognition
  113:329); Baker et al. 2011 (CogSci, POMDP belief-desire); Baker, Jara-Ettinger, Saxe & Tenenbaum 2017
  (Nature Human Behaviour 1:0064, percepts+POMDP predicts human judgments). FORWARD-direction behavioral
  evidence: Southgate, Senju & Csibra 2007 (anticipatory looking to the BELIEVED/empty location before the
  agent acts) -- literally forward action prediction from a false belief.
- ACT-ON-BELIEF read-out (PINNED, the defining commitment): the planner plans over the belief state, so a
  stale/false belief yields an action targeting the BELIEVED value. Wimmer & Perner 1983; Baron-Cohen, Leslie
  & Frith 1985 (Sally-Anne); Leslie 1987 (meta-representation); Onishi & Baillargeon 2005. BigToM's
  forward-action options are exactly {belief-consistent} vs {reality-consistent}.
- PERCEPT-GATED belief (PINNED -- THIS is the false-belief mechanism): update the sample-and-hold ONLY on a
  change the agent PERCEIVED; freeze when unobserved (Baker 2017 percepts; Onishi & Baillargeon 2005; Wimmer
  & Perner "seeing->knowing").
- FIRST-ORDER is sufficient for BigToM/ToMi forward-action (PINNED). Second-order (X's belief about Y's) is a
  separate capability (Perner & Wimmer 1985), OUR-INVENTION if added; out of scope.

## Parameters to SWEEP (not adopt)
- Desire hardness: soft utility (Jara-Ettinger et al. 2016 naive utility calculus, reward-cost) is general;
  ARGMAX = high-beta limit, correct for single-goal items -- soft won't move the BigToM number (no cost
  gradient / competing goals). SWEPT: we use argmax.
- Goal->fact binding: object-indexed utility is PINNED (Jara-Ettinger 2016/2020; Baker 2017 infers WHICH
  object is the goal); the discrete symbolic goal->fact LOOKUP is OUR-INVENTION-UNDER-TEST (prefer utility-
  ranking; here a candidate-in-goal-sentence scan + a believed-good-state fallback).

## The predicted single bottleneck (CONFIRMED on disk)
Belief extraction OVER-UPDATING to reality on an UNOBSERVED change -- if the sample-and-hold fails to HOLD,
belief==reality, the chain degenerates to the reality floor and is wrong on exactly the false-belief items.
Test: (1) split the metric by TB/FB (FB is the can-fail subset); (2) gold-belief positive control (localizes
extraction vs composition); (3) percept-ablation. -> On BigToM the confirmed cause was two-fold: the belief
driver never EXTRACTS BigToM's content/state change (only object-moves + copular status), and the percept gate
(PAL RULE-0) is PAST-tense so it can't read present-tense "sees"/"does not see". Both are register/lexicon
generalizations, not mechanism changes.

## Network-level mapping (PINNED, analogy only)
belief<->rTPJ (Saxe & Kanwisher 2003; Saxe & Powell 2006); goal/intention<->dmPFC (Frith & Frith 2006;
Spunt/Lieberman Why>How). Do NOT cite these as evidence for the soft-max (that is computational-level).

Sources: Baker et al. 2017 (Nature Human Behaviour); Baker/Saxe/Tenenbaum 2009/2011; Jara-Ettinger et al.
2016/2020 (naive utility calculus); Southgate/Senju/Csibra 2007; Onishi & Baillargeon 2005; Leslie 1987;
Wimmer & Perner 1983; Baron-Cohen/Leslie/Frith 1985; Gandhi et al. 2023 (BigToM); Le et al. 2019 (ToMi).
