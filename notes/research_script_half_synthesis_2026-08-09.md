# Script-half prior-art synthesis (2026-08-09) — the goal<->outcome RELATION has a glass-box, on-disk answer

Synthesis of a 3-lane prior-art drill (Yale-school scripts / FrameNet+VerbNet event-structure / unsupervised
script induction). All citations verified by the lanes (WebSearch/WebFetch); [UNVERIFIED] flags preserved.
Prior work = LEARN-FROM + BUILD-ON + CREDIT.

## THE ACTIONABLE CORE (answers the arc's residual)

The whole comprehension arc's residual = the **goal<->outcome RELATION** (does the described end-state
SATISFY the goal) -- not captured by valence, discourse-contrast, or concept-grounding alone. The drill
found the glass-box structure that encodes it, already on disk:

**VerbNet event predicates = STRIPS-like precondition/effect per verb sense, with an explicit OUTCOME slot.**
Each VerbNet frame scopes semantic predicates to `start(E)` / `during(E)` / `end(E)`. Example give-13.1:
`has_possession(start(E),Agent,Theme); transfer(during(E),Theme); cause(Agent,E); has_possession(end(E),Recipient,Theme)`.
=> `start(E)` = preconditions, `end(E)`/`result(E)` = EFFECTS/EXPECTED OUTCOME. **Goal-achievement becomes
end-state matching: does the OUTCOME verb's end(E) state match the GOAL verb's desired end(E) state.** This is
the goal<->outcome relation grounded in event-effect structure -- exactly the residual. On disk via nltk `verbnet`.
(Kipper-Schuler 2005 PhD UPenn; Kipper et al. 2008 LREV 42(1); subevent predicates ACL W19-3318.)

## FUSION (answers "how to combine the dictionaries", partly the concept-half too)

- **SemLink** (Palmer/CU-CLEAR, github cu-clear/semlink) = ready-made GLASS-BOX mapping PropBank<->VerbNet<->FrameNet
  (pb-vn2.json / pb-fn2.json). USE THIS as the join key instead of hand-building a VerbNet<->FrameNet map.
- **FrameNet Subframe + Precedes** relations = ordered sub-event scenarios (Criminal_process -> Arrest->Trial->Sentencing;
  Cooking Precedes Eating). Glass-box, on disk (nltk framenet_v17). The closest existing "script via frame relations."
  (Ruppenhofer et al. 2006 FrameNet II; Petruck & de Melo 2012 LREC-WS "Precedes".)
- **ATOMIC (NOT COMET)** = if-then event knowledge, `xIntent`~goal / `xEffect`,`oEffect`~outcome; the STATIC graph is a
  glass-box lookup usable WITHOUT the neural COMET generator. (Sap et al. AAAI 2019; ATOMIC-2020 Hwang et al. AAAI 2021.)
  COMET itself = neural/opaque -> SKIP at inference (correctly flagged).

## EXPECTATION-SATISFACTION mechanism (maps to our collapse)

- **Kintsch construction-integration (1988, Psych Review 95(2))**: build an over-generated proposition net, then
  spreading-activation REINFORCES context-fitting props + INHIBITS conflicting ones -> settle. A matched expected-outcome
  prop settles high (=satisfied); a conflicting one is inhibited to ~0 (=violated). This is a GLASS-BOX settle mechanism
  for "does end-state satisfy goal" -- and it maps onto our owned situation-model accumulate/collapse (cleanup) directly.
- Psych existence-proof that scripts drive goal->outcome inference: Bower, Black & Turner 1979 (Cog Psych 11).

## SCRIPT REPRESENTATION lineage (glass-box, for the acquisition target)

Schank & Abelson 1977 scripts (name/track/roles/props/entry-conditions/scenes/**results**-slot = the pre-stored
expected outcome); SAM (Cullingford 1978), PAM (Wilensky 1978, goal-conflict), FRUMP sketchy-scripts (DeJong 1979),
BORIS/TAUs (Dyer 1983), MOPs/TOPs (Schank 1982, reusable shared scenes). Modern glass-box revivals: Mueller event-calculus
scripts (2004/2006); Inclezan et al. ASP theory-of-intentions restaurant scripts (ICLP 2017, TPLP ~2019).

## TWO GENUINE OPEN GAPS = our novel-synthesis angle (not reinventing)

1. **Self-extending / online / incremental script induction = UNFILLED** in the classical literature (all of
   Chambers&Jurafsky 2008/2009, Regneri 2010, Frermann 2014, Balasubramanian 2013, Chambers 2013, Pichotta 2014 are
   ONE-SHOT BATCH over a fixed corpus). Our read->propose->consolidate self-extension loop (consequence_learning_loop
   pattern) applied to scripts is genuinely novel.
2. **MDL / Bayesian structural-form selection for scripts = UNFILLED** (Kemp & Tenenbaum 2008 "Discovery of Structural
   Form" never applied to scripts; closest = Orr et al. AAAI 2014 "Scripts as HMMs" EM structure learning). We OWN an MDL
   learner (hdlab.learner). MDL-selected script structure over VerbNet-seeded events = a novel, fit-to-substrate angle.

Eval to adopt if benchmarking the script mechanism: Multiple-Choice Narrative Cloze (Granroth-Wilding & Clark AAAI 2016).

## RECOMMENDED NEXT BUILD (script half, ranked by elegance x fit-to-substrate x glass-box x addresses-residual)

**#1 VerbNet-predicate goal<->outcome END-STATE MATCHING** (test-first): extract the GOAL verb's desired `end(E)` state +
the OUTCOME verb's actual `end(E)` state from VerbNet (SemLink for coverage); goal-achievement = do the end-state
predicates MATCH (fulfilled) / conflict (unfulfilled). CAN-FAIL: PAIRSCRAMBLE MUST COLLAPSE (the standing relation gate).
This directly attacks the residual the whole arc has hit, is glass-box + on-disk, and reuses goal_typing + the collapse.
Then: (a) fuse ATOMIC xEffect for OOV/non-VerbNet verbs; (b) wrap in the self-extension loop (novel gap #1); (c) MDL-select
script structure (novel gap #2).
