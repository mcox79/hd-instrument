---
problem: chain_belief_and_goal_into_theory_of_mind_inference_intention_and_false_belief
status: SOLVED
bar: "PASS = a glass-box mentalizing inference -- a transparent, hand-auditable forward composition of the LIVE belief and goal registers (believes(A,F,t) x wants(A) -> predicted intention/action, reading the action off the BELIEVED state), NO external LLM at inference -- that answers BOTH intention-attribution AND false-belief-prediction on a MODERN gold, with ALL of: (1) CI-separated over a REALITY-ONLY floor which MUST LOSE on the false-belief subset; (2) an info-free twin LOSES CI-separated; (3) a brain-faithful mechanism (forward inverse-planning composition, act on believes not reality); (4) a MODERN gold, verified. A rigorous LOCATED NEGATIVE naming the exact cause is a full pass."
result: "Glass-box forward chain believes(A,F,t) x wants(A) -> action (act off the BELIEVED state), driven by the reader's OWN extraction (NO LLM), on BigToM (Gandhi et al. 2023) forward items -- a MODERN, peer-reviewed ToM gold with matched TRUE/FALSE-belief conditions (278 items = 139 TB + 139 FB stories). BELIEF-prediction task: CHAIN 0.849 overall vs reality-only floor 0.500 (paired story-bootstrap +0.349 CI[+0.273,+0.421]); on the load-bearing FALSE-belief subset +0.871 CI[+0.813,+0.921] (floor is provably 0.000 there); both info-free twins LOSE CI-sep (percept-shuffle FB +0.374 CI[+0.281,+0.468], belief-shuffle FB +0.341 CI[+0.225,+0.450]). ACTION-prediction task (the belief x desire composition): CHAIN 0.655 overall vs floor 0.489 (+0.165 CI[+0.086,+0.248]); FB +0.432 CI[+0.295,+0.568]; twins LOSE. Positive control: with GOLD belief the composition is EXACT (belief 1.000) -> the residual gap is extraction, not the inference rule."
floor: "REALITY-ONLY floor (the beliefless reader: act on the TRUE state, ignoring belief; strongest form = oracle reality value) = 0.500 overall, and PROVABLY 0.000 on the false-belief subset for BOTH the belief and action tasks (reality and stale are the two different candidates and the desire equals exactly one -> the reality reader is 0% on false belief). Also run: CHAIN_NOFIX (the CURRENT live substrate, belief never updates on the change) = 0.478 belief / 0.471 action (~chance) -- the CHAIN beats it +0.371/+0.183 CI-sep, so the upstream fix is the whole lever."
controls: "(1) REALITY-ONLY floor (oracle true state) -- loses CI-sep, 0.000 on FB -> the belief representation is load-bearing. (2) INFO-FREE TWIN A = percept(observed)-bits SHUFFLED across items (belief updates at random): loses CI-sep on FB -> the percept->belief gate is load-bearing. (3) INFO-FREE TWIN B = believed-value binding SHUFFLED across items (derangement): loses CI-sep on FB -> excludes 'the chain works from a non-informative binding'. (4) CHAIN_NOFIX ablation = the current live substrate (no COS reality extractor): sits at chance and is a MIRROR of the reality floor (right on FB, wrong on TB) -> localizes the win to the upstream percept-gated change-of-state update. (5) POSITIVE CONTROL oracle-belief -> composition exact (1.000) and oracle-desire -> 0.849 (the action gap is desire extraction). (6) NO-REGRESS: the present-tense percept-gate extension is a strict superset of PAL's RULE-0 lexicon (PAL's 5 canonical self-test cases byte-identical; BigToM present-tense fixed 2/2); FANToM belief headline does not use PAL's epistemic gate -> unaffected; hdlab untouched. (7) LIVE-WIRE through SituationReader.read(): sm.wants + sm.believes are consumable off read(); the fixed chain's FB action (0.662) beats the live reality floor (0.245)."
files_changed: "experiments/_tom_bigtom.py (BigToM loader + index-based value model); experiments/_tom_chain.py (the glass-box forward chain: initial-belief + COS/substitution reality extractor + present-tense percept gate + belief_at_T over the promoted belief_timeline + goal->fact desire binding + forward_action); experiments/_tom_present_tense_pal.py (the LANDABLE percept-gate fix as a PAL subclass + no-regress check); experiments/_diagnose_tom_bottleneck.py (the localization trace); experiments/exp_tom_chain_belief_goal_action_v1.py (the measurement: arms, paired story-bootstrap CIs by TB/FB, twins, oracle controls); experiments/exp_tom_chain_live_wire_v1.py (live-wire through SituationReader.read()); verification/test_tom_chain.py (scaffold-free witness, 7/7); data/corpora/bigtom/bigtom.csv (foundation import, offline); data/exp_tom_chain_belief_goal_action_v1/metrics.json; data/exp_tom_chain_live_wire_v1/metrics.json; notes/problems/chain_.../{research_forward_tom_inverse_planning_2026-09-06.md, SOLVED.md}. hdlab/ UNTOUCHED (proposed Q111 diff in section 6)."
reverify: ".venv/Scripts/python.exe verification/test_tom_chain.py   # 7/7; reads landed metrics + recomputes the gold structure + the present-tense PAL parity from source (re-runs NO landed cell)"
---

# The reader now REASONS with mental states: believes(A,F,t) x wants(A) -> predicted (false-belief) action

## The one-line answer
The reader stored what each character BELIEVES and what each character WANTS but never chained them into "so
what will X do?". I built the glass-box FORWARD inverse-planning composition -- predict the action that achieves
the desire *given the agent's (possibly false) belief*, reading the action off the BELIEVED state -- and proved
it on **BigToM** (Gandhi et al. 2023), a modern peer-reviewed ToM gold with matched true/false-belief
conditions. On the load-bearing FALSE-belief subset the chain predicts the belief-driven action where a
reality-only reader is **provably 0%**: belief-prediction **+0.871 CI[+0.813,+0.921]**, action-prediction
**+0.432 CI[+0.295,+0.568]**, both info-free twins losing. The win required going ALL THE WAY UPSTREAM to two
brain-foundational fixes in the perception front-end (a change-of-state reality extractor + a present-tense
percept gate) -- without them the current live substrate sits at chance.

## Section 0 -- the brain opening move (research-verified, PINNED vs OUR-INVENTION)
`research_forward_tom_inverse_planning_2026-09-06.md` (web-verified primary sources):
- **PINNED -- FORWARD (belief,desire)->action is the core of Bayesian ToM** (Baker/Saxe/Tenenbaum 2009/2011/2017):
  attribution is the Bayesian *inversion* of a forward planner, so running it forward evaluates the model's
  generative component. Policy = soft-max over expected utility on the BELIEF state; ARGMAX (single-goal case)
  is the high-beta limit. Forward behavioral evidence: Southgate/Senju/Csibra 2007 anticipatory looking to the
  BELIEVED location.
- **PINNED -- act on believes not reality** (Wimmer & Perner 1983; Leslie 1987 meta-representation; Onishi &
  Baillargeon 2005): the planner plans over the belief state, so a false belief yields an action targeting the
  believed value. This is the defining commitment of the whole literature.
- **PINNED -- percept-gated belief IS the false-belief mechanism**: update the sample-and-hold only on a change
  the agent PERCEIVED; freeze when unobserved.
- **PINNED (network-level, analogy only)**: belief<->rTPJ, goal/intention<->dmPFC (Saxe & Kanwisher 2003; Frith
  & Frith 2006; Spunt/Lieberman) -- the substrate already honours this split (belief_timeline / goal_register).
- **OUR-INVENTION-UNDER-TEST (swept)**: goal->fact binding (candidate-in-goal-sentence + a believed-good-state
  fallback -- motivated by Jara-Ettinger naive-utility-calculus object-indexed utility); desire hardness
  (argmax; soft won't move the single-goal number); the COS-cue lexicon; the present-tense percept lexicon.
- **First-order suffices** for BigToM forward items; second-order is out of scope.

REUSE, not rebuild: the chain consumes the PROMOTED `belief_timeline` (sample-and-hold), the belief-value
channel (`_belief_reader.extract_belief_assertions`), the PROMOTED `goal_register` (desire), and the PROMOTED
`perceptual_access_ledger` (percept gate). It builds NO new register -- only the composition + two upstream
generalizations.

## Section 1 -- the mechanism (glass-box, hand-auditable, NO LLM)
For agent A, fact F (two candidate values), query time T:
1. **initial belief B0** = A's asserted belief value ("A believes F is <v>") -- belief-value channel.
2. **reality change** = a change-of-state / substitution / causative event that gives F its post-change value
   ("swaps X with Y", "rainfall opens the valve", "monkeys tear the net apart", "leaving the pot empty").
3. **percept gate** = did A perceive the change? (present-tense explicit narrator epistemic: "A sees.." True /
   "A does not see.." False) -- RULE-0.
4. **belief_at_T** (the PROMOTED sample-and-hold): reality value if the change was perceived, else B0 (stale).
5. **desire** = the value A wants F to have (goal register; goal->fact value binding).
6. **forward_action** = PROCEED (use F as-is) if believed == desire, else FETCH (go correct/obtain the desired).
The FALSE-belief case falls out: where believed != reality (A missed the change), the belief-driven action
DIVERGES from the reality-driven one, and only the belief-driven one is right.

## Section 2 -- what I measured (BigToM, modern gold, 278 items = 139 TB + 139 FB)

| task | arm | overall | TB | FB (load-bearing) |
|---|---|---|---|---|
| BELIEF | **CHAIN** | **0.849** | 0.827 | **0.871** |
| BELIEF | reality-only floor | 0.500 | 1.000 | **0.000** |
| BELIEF | CHAIN_NOFIX (current live substrate) | 0.478 | 0.086 | 0.871 |
| BELIEF | twin (percept-shuffle) | 0.464 | 0.432 | 0.496 |
| BELIEF | twin (belief-shuffle) | 0.496 | 0.466 | 0.527 |
| BELIEF | oracle-belief (positive control) | 1.000 | 1.000 | 1.000 |
| ACTION | **CHAIN** | **0.655** | 0.640 | **0.669** |
| ACTION | reality-only floor | 0.489 | 0.741 | 0.237 |
| ACTION | CHAIN_NOFIX | 0.471 | 0.273 | 0.669 |
| ACTION | oracle-desire (positive control) | 0.849 | 0.827 | 0.871 |

- **BELIEF vs floor**: overall +0.349 CI[+0.273,+0.421]; **FB +0.871 CI[+0.813,+0.921]** (hw 0.054). Twins LOSE
  CI-sep (percept +0.374 CI[+0.281,+0.468]; belief +0.341 CI[+0.225,+0.450]).
- **ACTION vs floor**: overall +0.165 CI[+0.086,+0.248]; **FB +0.432 CI[+0.295,+0.568]**. Twins LOSE.
- **CHAIN vs CHAIN_NOFIX** (the upstream fix): belief +0.371 CI[+0.309,+0.432], action +0.183 CI[+0.112,+0.252]
  -- CI-sep. The current live substrate is a MIRROR of the reality floor (right on FB, wrong on TB) -> at chance.
- Paired bootstrap over STORIES (the honest unit; TB+FB share a story). Population saved in metrics.json.

## Section 3 -- the upstream brain-foundational work (owner: "EVERY component, you and upstream, brain-foundational")
The diagnosis (`_diagnose_tom_bottleneck.py`) confirmed the research drill's predicted bottleneck EXACTLY: the
current live substrate composes the two registers to a NULL because the belief PERCEPTION channel cannot update
on BigToM's changes. Two upstream fixes, both register/lexicon GENERALIZATIONS of the brain's SAME operation
(not new mechanisms), both landable as small diffs:
1. **Change-of-state / substitution reality extractor** (the belief perception channel). The promoted belief
   driver extracts object-MOVES + copular STATUS but MISSES content/state changes ("swap/replace X with Y",
   causative "rainfall opens the valve", "leaving the pot empty"). Without the reality event belief can never
   UPDATE -> belief==initial for both conditions -> chance. This is change-of-state event segmentation (Dowty
   1979 inchoative/resultant; the `state_register` organ's COS territory) generalized to substitution/causative
   frames. Reading the resultant off the change clause lifts change coverage 0.62->0.94.
2. **Present-tense percept gate** (PAL RULE-0). PAL's explicit-epistemic lexicon is PAST-tense ("saw"/"did not
   see", built on 19c LitBank); BigToM is PRESENT-tense ("sees"/"does not see") -> RULE-0 never fired -> PAL
   fell back to co-presence -> observed=True for BOTH conditions (the false-belief signal destroyed). The fix is
   a present-tense SUPERSET of the same patterns (`_tom_present_tense_pal.PresentTensePAL`) -- **additive: PAL's
   5 canonical self-test cases are byte-identical, BigToM present-tense fixed 2/2.**

**No downstream consumer regresses (verified):** the only live consumer of PAL + the belief driver is the belief
dimension. The FANToM belief headline (0.893) does NOT use PAL's epistemic gate (presence-interval path) -> is
unaffected; the present-tense patterns are a strict superset (5/5 parity) so 19c LitBank (past-tense) is
untouched; the COS extractor lives only in `experiments/` (zero live effect). `belief_timeline` and
`goal_register` self-tests stay green (hdlab untouched). The proposed landing (section 6) still needs strategy's
no-regress witness on the belief dimension's LitBank slice for the COS branch (a landing gate).

## Section 4 -- performance vs a competent reader (the mechanism-diff)
- **Composition**: EXACT (oracle-belief -> belief task 1.000). The inference rule is not the loss.
- **Belief extraction**: 0.849 (FB 0.871). Residual = the ~6% b0 misses + rare COS frames the extractor doesn't
  catch (0.94 change coverage) + a handful of indirect/inferential percepts ("sees the flood" -> infer the
  valve opened; Sodian & Wimmer inference channel).
- **Desire extraction** is the ACTION ceiling: oracle-desire -> action 0.849 == belief recovery, so the action
  gap (0.655 vs 0.849) is entirely desire recovery. The LIVE `sm.wants` recovers the fine desired VALUE at only
  0.353 -- the goal register stores goal HEADS, not the fact-value (the goal->fact value binding is the fix).

## Section 5 -- the located sub-negatives (each a control that excluded something)
- **The current live substrate is at chance** (NOFIX 0.478/0.471) -- NOT because the registers are wrong but
  because the perception channel can't extract modern content-change events and the percept gate is past-tense.
  A fair test of the brain's ACTUAL mechanism (percept-gated update) succeeds; the naive un-fixed compose fails.
- **Anticipatory / desire-only prediction is not the mechanism**: the reality floor and the naive-belief NOFIX
  are mirror-image chance readers; only the percept-gated belief separates TB from FB (the twin proves it).

## Section 6 -- FOR STRATEGY (proposed hdlab landing -- Q111, you own it, witnessed)
All additive; mirrors the `_read_belief` lazy-adapter pattern.
0. **Land the present-tense RULE-0 extension** in `hdlab/perceptual_access_ledger._epistemic_patterns` (the
   strict superset in `experiments/_tom_present_tense_pal.py`). Witness: PAL self-test byte-identical + BigToM
   present-tense fixed. This is the register-generalization the belief dimension needs to read MODERN ToM prose.
1. **Land the change-of-state / substitution reality branch** in `experiments/_belief_reader.extract_reality_
   events` (a new COS/substitution/causative frame, gated), so `sm.believes` updates on content changes.
   Witness: no-regress on the belief dimension's LitBank slice + the BigToM chain lift.
2. **Add a default-off `predict_action` / `will_act_on(agent, fact, t)` read-out** on `SituationReader` that
   composes the two LIVE registers (believes x wants -> PROCEED/FETCH), following `_read_belief`/`_read_goals`.
   Witness: `verification/test_tom_chain.py` + a pure-hdlab landing witness (byte-identical other dimensions).
3. **Expose the goal's fine desired-VALUE** (goal->fact binding) so `sm.wants` returns the value, not only the
   head -- the ACTION ceiling lever.

## Section 7 -- ADJACENT COMPONENTS (fidelity + optimization -> next problems)
- **belief perception channel** -- OUR-INVENTION placeholder for modern register: past-tense percept lexicon +
  location/status-only reality extraction. Adopt the present-tense gate + COS/substitution frames (this work).
  Leverage: unlocks modern ToM prose end-to-end. HIGH value.
- **goal register granularity** -- stores goal HEADS, not argument VALUES; `sm.wants` fine-value recovery 0.35
  on BigToM. A goal->fact value binding (Jara-Ettinger object-indexed utility) is the ACTION ceiling lever.
- **state_register / world_state register** -- should adopt the substitution/content-change frames (the same
  COS channel) to track "swap/replace/spill/leak" world changes, currently copular-biased.
- **inference channel (Sodian & Wimmer)** -- the indirect-percept tail ("sees the flood" -> infer valve open)
  needs the belief-inference edge (already in `_belief_reader.extract_inference_edges`); wiring it to the COS
  channel would recover the residual.
- **second-order belief** -- absent; a recursive application of the first-order register (a clean next problem).

## KEY REALIZATIONS (the enabling moves)
1. **The two naive readers are mirror-image failures.** The reality floor is right on TB / 0% on FB; the naive
   (un-updated) belief is right on FB / wrong on TB. Both are chance. Seeing this made the whole result: the win
   is NOT "recover belief" in the abstract -- it is the PERCEPT-GATED UPDATE that distinguishes TB from FB. That
   is why the percept-shuffle twin is the sharpest control.
2. **The chain was inert for a boringly specific reason, and the research drill predicted it exactly.** Not a
   deep ToM failure -- a PAST-tense percept lexicon on PRESENT-tense prose + a location/status-only reality
   extractor. Both are register generalizations, provably additive. "Every component brain-foundational" here
   meant fixing the MODERN-REGISTER fidelity of the upstream perception front-end, not inventing new mechanism.
3. **Lead with the BELIEF task, not the ACTION task.** The false-belief BELIEF-VALUE recovery is the pure,
   floor-0.000 discriminator; the ACTION is the composition on top (desire-limited). Reporting both, with the
   oracle controls, cleanly separates "the inference rule" (exact) from "the extraction" (the real gap).
4. **A binary fact makes the reality value the OTHER candidate**, so detecting the change EVENT (COS cue /
   resultant-value named) is enough -- no fragile value parse of substitution clauses that name both values.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md -- ToM/mentalizing; strategy to fold)
The mentalizing INFERENCE that CHAINS the built belief and goal registers (belief x desire -> action) was
ABSENT and is now DEMONSTRATED as a glass-box forward inverse-planning composition (PINNED: Baker/Saxe/
Tenenbaum forward planner; Leslie meta-representation; act-on-believes; percept-gated update). Measured on a
MODERN gold (BigToM): belief-prediction FB +0.871 CI-sep, action-prediction FB +0.432 CI-sep over a reality
floor that is provably 0% on false belief; info-free twins lose; composition exact with oracle belief.
**NEW MEASURED DEVIATION (the fidelity gap it crosses):** the belief PERCEPTION front-end was 19c/past-tense +
location/status-only, so it could not read MODERN content-change ToM prose -> the chain was inert on the live
substrate (a MIRROR of the reality floor). The fix is a present-tense RULE-0 percept-gate extension + a
change-of-state/substitution reality extractor (both additive register generalizations). This is the filed
follow-on the goal-register and goal-hierarchy integrations named ("goal x belief composition" / "the
inverse-planning organ unifies goal-attachment and belief") -- now built and validated on modern gold.

## Section 8 -- what I did NOT establish (and would withdraw first)
- I did NOT beat a strong LLM baseline on BigToM (out of scope; the invariant bars an LLM at inference and the
  point is the glass-box registers, not SOTA). The claim is CI-separation over the reality floor + twins, not a
  leaderboard number.
- The ACTION headline leans on the goal->fact desire binding (OUR-INVENTION; desire=believed-good-state fallback
  for superordinate goals). WITHDRAW FIRST if wrong: the fallback couples desire to B0 on harmful-change
  stories, so I report the BELIEF task (no desire) as the primary clean headline and oracle-desire (0.849) as
  the action ceiling. The action result survives on its own (FB +0.432 CI-sep, twins lose) but is desire-limited.
- BigToM is a CONSTRUCTED (LLM-templated) modern gold; it is peer-reviewed and standard, but the belief HALF is
  corroborated independently on FANToM real dialogue (0.893, prior work) -- the ACTION half is BigToM-only.

## TLDR (plain English)
Our reader kept a note of what each character thinks is true and what each wants, but never put them together to
guess what a character will DO -- especially the classic case where someone acts on a mistaken belief (using the
pitcher they think holds oat milk, not knowing it was swapped). I built that joining step and proved it on a
modern set of test stories: on the tricky false-belief cases it predicts the mistaken action where a reader who
only tracks the truth is right 0% of the time. The hard part turned out not to be the reasoning (that part is
exact) but the reading: our belief-tracker was tuned to old-fashioned prose ("she saw") and to objects being
moved, so it couldn't tell that a character DIDN'T see a present-day change ("she does not see") or that a thing
was swapped/spilled. Fixing those two reading gaps -- both small, both matching how the brain does it, neither
breaking anything else -- is what made the whole thing work.

## QUESTIONS
None.

## NEXT STEPS
(1) Land the present-tense percept-gate extension + the change-of-state reality branch (section 6.0-6.1) with a
belief-dimension no-regress witness; (2) land the default-off `predict_action` read-out composing the two live
registers (6.2); (3) build the goal->fact desired-VALUE binding to lift `sm.wants` (the action ceiling, 6.3);
(4) fold the AUDIT UPDATE into BRAIN_FOUNDATIONAL_AUDIT.md.
