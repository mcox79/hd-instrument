# PROPOSED hdlab LANDING (Q111 -- strategy applies + witnesses; solver never writes hdlab)

Turnkey diff for `chain_belief_and_goal_into_theory_of_mind_inference_intention_and_false_belief`. All additive,
all mirroring the existing `_read_belief` / `_read_goals` lazy-adapter pattern. Reverify each step with
`verification/test_tom_chain.py` (9/9) + the named per-step witness. NO external LLM at inference.

Order matters: 0 and 1 are the upstream reading fixes that make the belief dimension read MODERN present-tense
content-change ToM prose; 2 is the chain read-out that composes the two live registers; 3 is the desire-value
lever (Phase-1-gated, filed not landed). Land 0-2 together; hold 3 for the meaning channel.

## 0. Present-tense RULE-0 percept-gate extension  (hdlab/perceptual_access_ledger.py)
The RULE-0 explicit-epistemic lexicon (`_epistemic_patterns`) is PAST-tense only; extend it with the present-
tense / progressive superset in `experiments/_tom_present_tense_pal._epistemic_patterns_present`. Concretely, add
to `neg`: `X does not|doesn't|is not ... (see|notice|observe|perceive|witness|realize|hear|know)`, `X is|are|
remains unaware|oblivious|ignorant|in the dark`, `without X seeing|noticing|knowing`; add to `pos`: `X sees|
notices|observes|watches|witnesses|perceives|spots|hears|realizes`, `X is|are seeing|watching|noticing`.
STRICT SUPERSET -- every past-tense form retained.
WITNESS: PAL `_self_test` byte-identical (5/5) + `experiments/_tom_present_tense_pal.check_no_regress()` (base
cases identical; present-tense fixed). This is the register-generalization the belief dimension needs to read
modern ToM prose; it does NOT touch FANToM (presence-interval path, no epistemic gate) or 19c LitBank (past-tense).

## 1. Change-of-state / substitution reality branch  (experiments/_belief_reader.py :: extract_reality_events)
The belief PERCEPTION channel extracts object-MOVES + copular STATUS but MISSES content/state changes ("swap/
replace X with Y", causative "rainfall opens the valve", "leaving the pot empty", "tearing it apart"). Add a COS/
substitution/causative branch modelled on `experiments/_tom_chain.extract_reality_change` + `_COS_CUES`: a
post-initial, non-subject-agent clause carrying a change-of-state cue whose resultant names the fact's new value.
Gate it (a `cos_reality=True` kwarg) so it fires only when the location/status extractors return nothing.
WITNESS: no-regress on the belief dimension's LitBank slice (the COS branch must not change the existing
knowledge-state numbers) + the BigToM chain lift (change coverage 0.62->0.94). This is change-of-state event
segmentation (Dowty 1979; the state_register organ's COS territory).

## 2. predict_action / will_act_on read-out  (hdlab/situation_reader.py, default-off track_tom_action)
Add a default-off flag `track_tom_action` and a `_read_tom_action(sm, sents)` that mirrors `_read_belief`:
binds `sm.predict_action(agent, fact, t)` and `sm.will_act_on(agent, fact, t)` composing the two LIVE registers:
```
believed = sm.believes(agent_aliases, fact, t)          # TPJ-analog (post steps 0-1: updates on modern changes)
desire   = <desired value of fact from sm.wants(agent)> # dmPFC-analog goal register
action   = 'PROCEED' if believed == desire else 'FETCH' # forward inverse-planning (Baker/Leslie), argmax
```
Also bind `sm.attribute_belief(agent, fact, observed_action, t)` = `experiments._tom_chain.attribute_belief_
from_action` (the SAME engine INVERSE -- Baker 2017 attribution; validated `exp_tom_inverse_attribution_v1`,
FB 0.741 vs floor 0.000). Lazy imports; additive (byte-identical other dimensions off-vs-on -- witness a
pure-hdlab landing test like `test_goal_register_landing_organ`).
WITNESS: `verification/test_tom_chain.py` W2-W9 + a landing test asserting other dimensions byte-identical.

## 3. Goal->fact desired-VALUE binding  (FILED, Phase-1-gated -- do NOT land a heuristic)
`sm.wants` returns the goal HEAD, not the fine desired VALUE of F (live recovery 0.353), and this is the entire
action ceiling (oracle-desire 0.849 vs chain 0.655). The FAITHFUL fix is naive-utility-calculus (desire = argmax
candidate of associative relatedness to the goal, over the ATL meaning hub) -- BUILT + TESTED in
`experiments/_tom_desire_meaning.py` and it is a LOCATED NEGATIVE (does not beat the heuristic; the meaning
channel is too thin). So this rides with the Phase-1 MEANING CHANNEL; a valence/sentiment heuristic would lower
fidelity and must NOT be landed. File as a meaning-channel consumer.

## AUDIT UPDATE (fold into notes/BRAIN_FOUNDATIONAL_AUDIT.md -- ToM/mentalizing)
Add: the mentalizing INFERENCE chaining belief x goal -> action (forward inverse planning; act-on-believes;
percept-gated update) is now DEMONSTRATED on a MODERN gold (BigToM) -- belief FB +0.871 CI-sep, action FB +0.432
CI-sep over a reality floor that is provably 0% on false belief, twins lose, composition EXACT (oracle belief
1.000), AND the SAME engine runs INVERSE (attribute belief from action, FB 0.741 vs 0.000). NEW MEASURED
DEVIATION: the belief PERCEPTION front-end was 19c/past-tense + location/status-only, so the live substrate was
INERT on modern content-change ToM prose (a MIRROR of the reality floor); fixed by a present-tense RULE-0 gate +
a COS/substitution reality branch (both additive). Remaining fidelity gap = the goal->fact desired-VALUE binding
= naive utility over the meaning channel (Phase-1 located negative). This is the filed "goal x belief
composition" / "inverse-planning organ unifies goal-attachment and belief" follow-on, now built + validated.
