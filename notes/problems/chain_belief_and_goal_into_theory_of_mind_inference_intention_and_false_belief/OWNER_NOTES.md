---
owner_verdict: DONE
---

SUBMISSION — chain_belief_and_goal_into_theory_of_mind_inference_intention_and_false_belief
status: SOLVED (WIP until owner_verdict: DONE). Glass-box, NO LLM at inference. NO hdlab/ written (Q111: strategy
lands the wire — turnkey diff in PROPOSED_HDLAB_LANDING.md). Witness 9/9. Ledger malformed/incomplete: 0.
reverify: .venv/Scripts/python.exe verification/test_tom_chain.py   # 9/9, deterministic

THE CORE RESULT
The reader stored per-agent BELIEF and per-agent GOALS but never CHAINED them into "given what X believes and
wants, what will X do?". I built the glass-box FORWARD inverse-planning composition — predict the action that
achieves the desire GIVEN the agent's (possibly false) belief, reading the action off the BELIEVED state — and
proved it on BigToM (Gandhi et al. 2023), a MODERN peer-reviewed ToM gold with matched true/false-belief
conditions (278 items = 139 TB + 139 FB stories; offline foundation import).
- BELIEF-prediction: chain 0.849 vs reality-only floor 0.500 (paired story-bootstrap +0.349 CI[+0.273,+0.421]);
  on the load-bearing FALSE-belief subset +0.871 CI[+0.813,+0.921] (the floor is provably 0.000 there — reality
  and stale are the two candidates and desire equals exactly one). Both info-free twins LOSE CI-sep
  (percept-shuffle, belief-shuffle).
- ACTION-prediction (the belief x desire composition): chain 0.655 vs floor 0.489 (+0.165 CI[+0.086,+0.248]);
  FB +0.432 CI[+0.295,+0.568]. Twins LOSE.
- INVERSE (same engine backward, Baker 2017): attribute BELIEF from the OBSERVED ACTION — FB 0.741 vs
  reality-attributer floor 0.000 (+0.741 CI[+0.669,+0.806]); shuffled-action twin LOSES. The substrate now both
  PREDICTS and EXPLAINS behavior from one engine.
- POSITIVE CONTROL: with gold belief the composition is EXACT (belief 1.000) -> every lost point is EXTRACTION,
  never the inference rule.

THE UPSTREAM BRAIN-FOUNDATIONAL FIX (owner: "every component, you and upstream, brain-foundational")
The current live substrate composed naively sits at CHANCE (belief 0.478 / action 0.471) — a MIRROR of the
reality floor. Diagnosis (research-predicted, then confirmed on disk): the belief PERCEPTION channel could not
read modern present-tense content-change ToM prose. Two fixes, both additive register/lexicon GENERALIZATIONS of
the SAME brain operation (not new mechanisms):
  (1) a CHANGE-OF-STATE / substitution reality extractor (the belief driver extracted object-MOVES + copular
      STATUS but MISSED "swaps X with Y" / "rainfall opens the valve" / "tearing it apart" / "leaving it empty";
      Dowty 1979 COS segmentation) -> change coverage 0.62->0.94, belief can finally UPDATE;
  (2) a PRESENT-TENSE percept gate: PAL's RULE-0 lexicon is PAST-tense ("saw"/"did not see", 19c LitBank), so
      BigToM's "sees"/"does not see" matched neither pattern -> RULE-0 never fired -> observed=True for BOTH
      conditions. A present-tense SUPERSET (Wimmer & Perner seeing->knowing) fixes it.
CHAIN beats CHAIN_NOFIX (current live substrate) +0.371 belief / +0.183 action CI-sep — the upstream fix is the
whole lever.

100% BRAIN-FOUNDATIONAL? The INFERENCE is (composition exact, 1.000; forward inverse planning + act-on-believes
+ percept-gated sample-and-hold all PINNED — Baker/Saxe/Tenenbaum, Leslie, Wimmer & Perner; research-verified).
The one OUR-INVENTION mechanism, the goal->fact DESIRE binding, I rebuilt in its FAITHFUL form (naive-utility-
calculus: desire = argmax candidate of associative relatedness to the goal, over the ATL meaning hub) and TESTED
it -> LOCATED NEGATIVE: it does NOT beat the extraction heuristic at any margin (utility 0.540, best hybrid 0.655
= heuristic 0.655, oracle ceiling 0.849) because the meaning-channel margins are too thin. So the last ~15% is
EXTRACTION whose biggest piece (desire utility) routes into the project's Phase-1 MEANING CHANNEL — the fidelity
boundary is correctly LOCATED, not hacked.

WHERE WE LOSE SIGNAL (itemized; inference is exact, so all loss is extraction)
- belief extraction 1.000->0.849 (-0.151): initial-belief-miss 38% / value-normalize 33% / percept-cue-absent-or
  -indirect 29%.
- desire extraction is the action ceiling: oracle-desire -> action 0.849 == belief recovery; 100% of belief-
  correct action errors are wrong-desired-candidate; live sm.wants recovers the fine value at only 0.353 (stores
  goal HEADS not fact-values). This is the meaning-channel (Phase-1) gate.

NO DOWNSTREAM CONSUMER REGRESSES (verified): the only live consumer of PAL + the belief driver is the belief
dimension. The present-tense gate is a STRICT superset (PAL's 5 canonical cases byte-identical; 19c LitBank is
past-tense -> untouched); the FANToM belief headline 0.893 does NOT use PAL's epistemic gate (presence-interval
path) -> unaffected; the COS extractor lives only in experiments/ (zero live effect); belief_timeline +
goal_register self-tests green (hdlab untouched).

LIVE-WIRE (through SituationReader.read()): sm.wants + sm.believes are consumable off read(); the goal register
wires live TODAY (fine-value recovery 0.353 — a located limitation); the stock sm.believes is wrong/null on 55%
of BigToM (past-tense gate + no COS = the located gap); the upstream-fixed chain reproduces the headline
(FB action 0.662 vs live floor 0.245).

PROPOSED hdlab DIFF (Q111 — turnkey in PROPOSED_HDLAB_LANDING.md; strategy lands + witnesses):
(0) present-tense RULE-0 superset in hdlab/perceptual_access_ledger._epistemic_patterns; (1) a COS/substitution
reality branch in experiments/_belief_reader.extract_reality_events (gated); (2) a default-off predict_action /
attribute_belief read-out on SituationReader composing the two live registers (forward + inverse). Land 0-2 ON
with the named witnesses. (3) the goal->fact desired-VALUE binding is FILED not landed — Phase-1-gated.

DO NOT LAND / DO NOT QUOTE: a valence/sentiment desire heuristic (LOWERS fidelity — desire utility must ride
Phase-1); the belief read-out numbers (FANToM 0.893) as an action result; any chain gain without the info-free
twins LOSING; the ACTION 0.655 as CI-sep-over-floor without noting it is desire-limited (belief task is the clean
headline).

FILES (all experiments/ + verification/ + notes/ + data/; NO hdlab/):
experiments/_tom_bigtom.py, _tom_chain.py, _tom_present_tense_pal.py, _tom_desire_meaning.py,
_diagnose_tom_bottleneck.py, exp_tom_chain_belief_goal_action_v1.py, exp_tom_chain_live_wire_v1.py,
exp_tom_inverse_attribution_v1.py; verification/test_tom_chain.py (9/9);
data/corpora/bigtom/bigtom.csv + data/exp_tom_*/metrics.json;
notes/problems/chain_.../{research_forward_tom_inverse_planning_2026-09-06.md, PROPOSED_HDLAB_LANDING.md, SOLVED.md}.

KEY REALIZATIONS (the enabling moves): (1) the two naive readers are MIRROR-IMAGE failures — reality-floor right
on TB/0% on FB, un-updated belief right on FB/wrong on TB, both chance; the win is the PERCEPT-GATED UPDATE that
distinguishes them (why the percept-shuffle twin is the sharpest control). (2) the chain was inert for a boringly
specific reason the research drill predicted exactly — a PAST-tense percept lexicon on PRESENT-tense prose + a
location/status-only reality extractor — "every component brain-foundational" here meant fixing the MODERN-
REGISTER fidelity of the perception front-end, not inventing mechanism. (3) lead with the BELIEF task (pure
false-belief, floor 0.000) not the desire-limited ACTION; the oracle controls cleanly separate "inference"
(exact) from "extraction" (the real gap). (4) the faithful desire mechanism being a LOCATED NEGATIVE is the
finding — the ToM chain is not blocked by ToM, it's blocked by the meaning channel Phase 1 is building.

ADJACENT COMPONENTS / NEXT PROBLEMS: belief perception channel (adopt present-tense gate + COS frames — this
work); goal register granularity (expose fine desired-VALUE / goal->fact binding — the action ceiling);
state_register/world_state (adopt substitution/content-change frames); the inference channel (Sodian & Wimmer)
for indirect percepts; second-order belief (recursive first-order register); the unified inverse-planning organ
(one engine: goal-attachment + belief + abduction).

TLDR (plain English): our reader kept a note of what each character thinks is true and what each wants, but never
put them together to guess what a character will DO — especially when someone acts on a mistaken belief. I built
that joining step and proved it on modern test stories: on the tricky false-belief cases it predicts the mistaken
action where a reader who only tracks the truth is right 0% of the time, and it also works backward (figure out
what someone believes from what they did). The reasoning itself is a flawless brain-copy — hand it clean inputs
and it's 100%. What's left is reading: mostly recovering what a character wants the thing to be, and I proved
that specific gap needs the general "meaning" understanding the project is already building, not a shortcut.

QUESTIONS: none.

NEXT STEPS: strategy applies PROPOSED_HDLAB_LANDING.md steps 0-2 with the named witnesses; the desire->value
lever rides with Phase-1's meaning channel; fold the AUDIT UPDATE into BRAIN_FOUNDATIONAL_AUDIT.md.
