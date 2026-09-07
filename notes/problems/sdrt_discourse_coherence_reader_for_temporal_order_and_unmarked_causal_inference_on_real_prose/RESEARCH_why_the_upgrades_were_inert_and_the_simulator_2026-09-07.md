# Research + measurement: were the two upgrades genuinely inert, and can the simulator fix it?

Owner's challenge (2026-09-07): "does it make sense that this system isn't doing anything?" Drilled with a
theory research drill + direct instrumentation + a built simulator. Saved here so the SOLVED.md citation is
not dangling. Answer: the two "upgrades" were DEGENERATE (owner's skepticism correct); the properly-built
structural simulator DOES do something (cuts over-firing, beats the twin) but is coverage-bound.

## 1. The Kintsch settling was a PROVEN mathematical no-op (not "inert-but-correct")
Research (Amari 1977 Biol.Cyb. 27; Grossberg competitive dynamics; Kintsch 1988 Psych.Rev. 95; McClelland &
Rumelhart 1981 Psych.Rev. 88; Hopfield 1982 PNAS 79): with UNIFORM lateral inhibition and NO cross-node
excitatory links, the settled winner is ALWAYS argmax(evidence). Proof: a_i(t+1) = relu(e_i + inhib*a_i(t) -
inhib*S(t)) where S(t) is a scalar common to all units -> activation is a common MONOTONE transform of each
node's own evidence, which can never reorder. CONFIRMED empirically: base-argmax vs my kintsch_select differ
on 3/68 predictions (all ties). To change a winner the integration matrix needs SIGNED, PAIRWISE-SPECIFIC
off-diagonal terms (positive between mutually-consistent cues / same-causal-chain candidates; negative
between contradictory) -- a scalar -inhib*Sum fails both conditions. Kintsch's actual power (convergent
coalition beats lone signal; disambiguation of near-tied candidates) lives in those content-specific edges.

## 2. The scalar means-end gate measured the WRONG AXIS
Research (Csibra-Gergely 2003 TiCS 7; Baker-Saxe-Tenenbaum 2009 Cognition 113; Schank-Abelson 1977): means-end
"does THIS action serve THAT goal" is a STRUCTURAL/geometric judgement (is the action on an efficient causal
path to the goal-state, judged against alternatives) -- an inverse-planning computation over a state/action
space, NOT a lexical-relatedness distance. "hungry"/"kitchen renovation" are topically close but not means-end
related; "hungry"/"went to the kitchen" are means-end related and only modestly closer topically -- the two
relations are not even monotonically correlated. CONFIRMED: my scalar gate (threshold 0.05) fired on 97.3% of
goal pairs -- it never suppressed. Raising the threshold cannot fix a confound on the wrong axis. The fix: a
TYPED causal/enabling-edge membership test (ConceptNet/CSKG MotivatedByGoal/UsedFor/HasSubevent/
HasPrerequisite/Causes) or an explicit alternative-action cost comparison.

## 3. The SIMULATOR (typed-edge inverse-planning means-end) -- built, measured, coverage-bound
Replaced scalar relatedness with the CSKG typed-edge membership test (a STATIC offline asset; the invariant is
NO external LLM AT INFERENCE) as the goal engine's means-end gate. On TellMeWhy non-adjacent (n=256):
  - goal fires: raw 302 -> typed 102 (34% -- CSKG covers the goal->action typed edge for only ~1/3 of goals);
  - OVER-FIRE CUT (the intended effect): OTHER subset raw 0.139 -> typed 0.208 (recovers toward base 0.247);
  - GOAL subset partially kept: base 0.293 -> typed 0.391 (raw got 0.533 by firing on all);
  - overall ties base (0.277) BUT the typed version now BEATS the info-free twin CI-sep (+0.0742 [0.004,0.144])
    -- which the raw goal engine did NOT. The structural gate makes the goal signal SELECTIVE.
So the typed means-end is the CORRECT fix (right axis, cuts over-firing, beats the twin) -- but COVERAGE-BOUND:
CSKG has the goal->action typed edge for only ~34%, so gating on it loses the 66% of true goals CSKG can't see.
This is the SAME coverage wall the causal reasoner hit at CSKG 17.3%, now confirmed from the goal-SELECTION
side (a THIRD angle).

## 4. Verdict + the route past
The system is NOT "doing nothing": the raw goal engine works on its category (+0.239), and the typed-edge
simulator cuts over-firing and beats the twin. Both theory-prescribed fixes are now BUILT: the settling needs
cross-node causal-CHAIN coherence (= coupling to the causal_reasoner's densified graph, which the causal SOLVED
already showed is CORRECTNESS-bound), and the typed means-end is RETRIEVAL-bound (CSKG 34%). RETRIEVAL cannot
cross the wall (coverage-bounded by construction, from three angles: CSKG cause-pairs 17.3%, newswire
flip-precision, goal->action edges 34%). The brain does not RETRIEVE the means-end link; it GENERATES it by
SIMULATION (does the action, rolled forward, achieve the goal-state?) -- the causal reasoner's own P1
(content-sensitive generative rollout over force_dynamics + goal_register + belief_partition + affect_register).
That is the one remaining lever, shared by three consumers, and it needs the meaning channel -- a large build,
the RIGHT one, and NOT a retrieval fix.

P_deflated: ~0.75 (the settling no-op is a closed-form proof); ~0.6 (the means-end-axis + coverage-bound
claims, corroborated by CSKG measurement from three angles).
