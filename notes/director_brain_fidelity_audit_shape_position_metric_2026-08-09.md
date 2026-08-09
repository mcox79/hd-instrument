# Director brain-fidelity audit — is goal-achievement comprehension on the RIGHT ARCHITECTURE?

**Author:** Director (main thread, opus), 2026-08-09. **Trigger:** USER "do a deep drill... brain
foundational fidelity to be sure we're on the right track" + "brain foundational 3x, the brain can do
it, so can we." This is the DIRECTOR's independent pass (SHAPE+POSITION+METRIC per the 07-24 formalize
discipline), to be synthesized against the 3 in-flight research drills (architecture / OOV-schema /
adversarial). Report-only reasoning; the decision it points to is gated on a can-fail prototype.

## The question

We compute "did the character get what they wanted?" with a BOTTOM-UP, FEED-FORWARD pipeline:
parse goal -> extract goal-state; parse outcome -> **extract the outcome event -> TYPE it (verb-class /
role / valence) -> bind affect to a referent -> compare** outcome-state to goal-state -> discrete
verdict. We keep hitting three walls: (1) OOV — ~90% of real outcome events aren't in our ontology;
(2) referent-binding — the coverage drill (2026-08-09) showed the owned affect-bridge fires 2/39 and
the supply lever tops out at ~+9 because 17/39 are situation-evaluations bound to NO local subject;
(3) affect-relevance — positive words about the situation get mis-read as goal-fulfillment (idx0
"he loves...supportive" while the goal was refused).

## SHAPE + POSITION + METRIC: ours vs the brain (hypothesis, pending drill confirmation)

| Axis | OUR pipeline | BRAIN (hypothesized) | Divergence |
|---|---|---|---|
| **SHAPE** | feed-forward: extract -> type -> compare | recurrent: goal MAINTAINED as active value/expectation, TOP-DOWN biases interpretation of incoming events | ours feed-forward, brain recurrent/predictive |
| **POSITION** | outcome represented INDEPENDENTLY of the goal, then compared | outcome interpreted CONDITIONED ON the maintained goal (goal active DURING outcome reading) | ours goal-free extraction; brain goal-conditioned — **there is no goal-free "outcome event" to extract** |
| **METRIC** | discrete state-match + relation-table lookup (MET/UNMET/NA) | graded prediction-error / fit against the goal-conditioned prediction (RPE-like), verbalized post-hoc | ours discrete/brittle; brain graded/continuous |

Brain positions (to be confirmed by drills): goal-maintenance dlPFC/vmPFC; expected-vs-received value
+ RPE in OFC/vmPFC/ventral striatum/VTA; top-down bias via biased-competition (Desimone & Duncan) /
predictive coding (Rao & Ballard, Friston); situation-model construction-integration (Kintsch) with
prediction-error-driven event segmentation (Zacks); mentalizing (mPFC/TPJ) for the character's goal.

## The load-bearing claim: our THREE walls are all SHAPE-divergence artifacts

Each wall exists ONLY because we extract the outcome BEFORE conditioning on the goal:
1. **OOV wall** — we must TYPE the outcome against a fixed ontology bottom-up. The brain never types
   it independently; it checks FIT against the goal-conditioned prediction, so a never-seen outcome
   phrasing is understood by fit, not by matching a stored type. Goal-conditioning DISSOLVES OOV.
2. **Referent-binding wall** — we must independently determine WHOSE outcome/affect it is (fragile on
   free prose: L32 referent-linking fires 7/80, hurts). The brain has the goal-owner MAINTAINED, so
   the referent is GIVEN by top-down context. The coverage drill's 17 ambiguous items
   ("changed my life", "best ever") are bound to no local subject — only the maintained goal binds them.
3. **Affect-relevance wall** — we bind affect to whoever is syntactically local (idx0 mis-fires on the
   bystander). The brain interprets affect RELATIVE to the maintained goal ("is THIS affect about MY
   goal's resolution?"). Goal-conditioning makes affect goal-relative by construction.

The narrow construction's PRECISION (2/2) is itself the tell: "i am ADJ" works because the construction
SYNTACTICALLY co-locates the referent with the affect — i.e. it accidentally simulates goal-conditioning
for the one case where the owner is local. That is why it can't scale: it's a bottom-up proxy for a
top-down operation.

## The brain-faithful reframe (REUSES owned organs, no new primitives)

Hold the goal as an active hypervector "state of mind" (owned: state_of_mind / focus). As the outcome
text streams: build a goal-conditioned QUERY (bind goal-owner + goal-predicate), and use
superposition-collapse / cleanup (owned) to READ OUT the goal-relevant resolution from the outcome
text — i.e. does the outcome, QUERIED WITH THE GOAL, collapse toward fulfillment or violation? The
METRIC becomes graded fit / prediction-error (owned: biased-competition, cleanup similarity), thresholded
to a discrete verdict only at the end. The grounded concept/script layer (proven earlier this arc:
script_bridge + learned_script_bridge, all gates) supplies the world-knowledge fit-check for novel
outcomes. **No independent outcome-extraction, no independent referent-binding, no fixed-ontology typing.**

Owned parts reused: state_of_mind (maintain goal), cleanup/superposition-collapse (goal-conditioned
readout), biased-competition (top-down bias), grounded concept/script layer (fit for OOV), goal_typing
(goal-state), coreference_resolver (only where genuinely needed). This is WIRE-DON'T-ISLAND compatible.

## Adversarial caveats (the angle-C drill must push these; do not pre-accept the reframe)

- **Hybrid, not pure top-down.** Zacks event-segmentation is prediction-error-driven but there IS
  bottom-up perceptual segmentation. Likely: brain does bottom-up SEGMENTATION (find the outcome
  clause) + top-down EVALUATION. Our error is bottom-up TYPING (fixed ontology), not bottom-up
  segmentation per se. Fix = keep light segmentation, replace typing with goal-conditioned fit.
- **Discrete target.** DesireDB's label is discrete; even if the brain computes graded RPE, we need a
  thresholded readout. Fine — internal graded, external thresholded.
- **Is the discrete label even the right target?** (angle-C) If comprehension is a continuous appraisal
  trajectory + mentalizing simulation, the 45% "deep pragmatic" residual may be the IRREDUCIBLE core,
  not a coverage gap. This would cap ANY architecture's accuracy — the honest bound to keep in view.
- **Falsification risk of the reframe:** goal-conditioned collapse could just re-encode the same
  lexical signal and inherit the same ceiling. The prototype MUST have a can-fail gate: does goal-
  conditioned readout beat the bottom-up pipeline AND the rule baseline on the SAME T2 items, with a
  pairscramble (wrong-goal) collapse? If it doesn't beat bottom-up, the SHAPE story is wrong.

## Director verdict (pending 3-drill synthesis)

STRONG hypothesis that we have a **SHAPE divergence** (bottom-up typing vs top-down goal-conditioned
fit) and that all three walls are artifacts of it. The reframe is brain-foundational, reuses owned
organs, and attacks the walls at their root rather than grinding coverage. IF the 3 drills confirm the
top-down/predictive account (they are testing exactly this), the direction correction is: **stop
extending bottom-up extraction/typing; prototype the top-down goal-conditioned readout with a can-fail
gate.** IF the drills show the brain is meaningfully bottom-up at the relevant stage, or angle-C shows
the target itself is mis-specified, revise accordingly. This audit is one of 4 independent passes
(this + 3 drills); synthesize before committing.
