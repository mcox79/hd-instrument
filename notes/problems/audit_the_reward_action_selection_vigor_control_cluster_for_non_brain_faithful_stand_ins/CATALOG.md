# CATALOG -- brain-fidelity of the reward / action-selection / vigor control cluster

**Slug:** `audit_the_reward_action_selection_vigor_control_cluster_for_non_brain_faithful_stand_ins` -- **solver session, 2026-09-09.**

**Denominator (the absence claim requires an ENUMERATION, not a search).** The import closure of the 7
brief-named seed organs (`action_selection`, `successor_representation`, `self_manager`,
`goal_achievement`, `consequence_learning_loop`, `goal_typing`, `state_of_mind`), computed by a
pure-disk AST import-graph trace over the current bytes of all **249** `hdlab/*.py` modules
(`experiments/exp_audit_reward_cluster_denominator_v1.py`): **40 organs** in the closure. Liveness is
by REVERSE reachability -- for each organ, is there a MODULE-LEVEL import path from a live entry point
(`situation_reader`, `reading_grounding_loop`, `grounding_acquisition_loop`, `three_tier_loop`,
`gap_driven_reader`, `substrate`, `glass_box_loop`)? -- reconciled against the ACTUAL import graph and
call sites, NOT the docstring comments (several "default OFF" comments are stale; the reader audit
catalogued that trap as C-STALE). **Witness:** `verification/test_audit_reward_cluster_standins.py`
(**20/20**) reproduces every liveness / stand-in / fidelity claim below on the current bytes, plus the
#1 powered localization, plus a positive control that the byte-search guard fires.

**Legend.** BF = brain-foundational. PINNED = the brain's computation is fixed by evidence;
OUR-INVENTION = a placeholder/model we chose. LIVE-CALLED = a live loop calls it under default flags;
LIVE-IMPORTED-INERT = a live loop imports the module (top-level code runs) but does NOT call its
decision functions in any default path; DORMANT-ISLANDED = no live entry point reaches it.

**HEADLINE (disk-verified).** The reward/action-selection/vigor cluster's PINNED decision core is
**faithful, and DORMANT.** The three organs with a pinned brain equation --
`action_selection` (basal-ganglia Go/NoGo + TD/RPE), `successor_representation` (M=(I-gamma*P)^-1),
`self_manager` DIAL #1 (ACC/EVC halting) -- each copy the brain's OPERATION correctly and have **zero
`hdlab` importers** (off every live loop). The goal-COMPREHENSION organs (`goal_typing`,
`goal_achievement`, `result_type_induction`, `consequence_learning_loop`) are honestly-labelled
OUR-INVENTIONS with no pinned neural equation (already dispositioned UNSCORABLE by the prior audit).
**The one genuine fidelity defect is a MISSING organ, not a stubbed one: the cluster is named "vigor
control" and NO vigor computation exists** -- the string "vigor" occurs in all of `hdlab/` exactly
once, as a docstring mention in `self_manager.py:6`.

---

## TOP-K (ranked by blast x severity)

| # | finding | live? | blast | fix class |
|---|---------|-------|-------|-----------|
| **1** | **R1 tonic-DA VIGOR channel MISSING** -- the cluster's namesake computation (PINNED: Niv 2007, vigor ~ sqrt(reward-rate)); advertised in `self_manager` docstring, **zero implementation anywhere in `hdlab`** | DORMANT (named-but-absent) | **HIGH** -- the defining function of a "vigor control" cluster is absent; a placeholder-risk the moment an autonomous agent must set effort/rate; **+579 (CI-sep) net reward proven recoverable** by the pinned dial over the strongest fixed baseline | **BUILD** (missing organ; add DIAL #2 to `self_manager`) |
| **2** | **R2 the consequence-learning TEACHER is a symbolic MET/UNMET lexicon vote standing in for a computed affective value** (`consequence_learning_loop`, self-labelled "standing in for the felt affective core") | LIVE-IMPORTED-INERT (grounding) | **MEDIUM** -- it is the reward-cluster's value/teaching signal; honestly labelled; **overlaps the pri-4 grounding closure** (defer its call-liveness reconciliation to pri-4) | RE-ARCH (compute an affective value) |
| **3** | **R3 `self_manager` advertises a 6-channel neuromodulatory bank; 5 of 6 are unbuilt** (NE gain, ACh encode/retrieve, 5HT horizon, tonic-DA vigor=R1, homeostasis+sleep) | DORMANT | **MEDIUM** -- a docstring-vs-code mislabelling / coverage gap (the same "name trap" as `state_of_mind`); each unbuilt dial has a pinned/precedented scalar form in the cited research note | BUILD (the dials) |
| **4** | **R4 `action_selection` reach uses a cosine, not the linear SR value read-out V = M.R** | DORMANT (self-test only) | **LOW** -- RIGHT-OP-WRONG-METRIC; defensible for pure goal-navigation, but drops the reward-vector structure | LOCAL-FIX |
| -- | N1 `action_selection` = FAITHFUL (TD/RPE + SR-transport + Go/NoGo) | DORMANT | positive control (do-not-over-fire) | n/a |
| -- | N2 `successor_representation` = FAITHFUL (M=(I-gamma*P)^-1); MEASURED-AND-LOST is a *capability* finding, not a fidelity flaw | DORMANT | correction | n/a |
| -- | N3 `self_manager` DIAL #1 (ACC/EVC halting) = FAITHFUL (Shenhav EVC) | DORMANT | positive control | n/a |
| -- | N4 `goal_typing`/`goal_achievement`/`result_type_induction` = honestly-labelled OUR-INVENTION-judged-on-task (no pinned equation) | mixed | ADMISSIBLE (prior audit's UNSCORABLE) | n/a |
| -- | N5 `state_of_mind` = coref tracker labelled NOT-ToM | LIVE (coref) | already dispositioned (coref) | n/a |

R1 is the one LIVE-relevant fidelity defect that is not already dispositioned; R2-R4 are located
deviations; N1-N5 are the do-not-over-fire corrections + positive controls. A rigorous result of
"the pinned decision core is faithful + dormant; the one real gap is a MISSING pinned organ" is the
honest finding, and the #1 is localized below with a powered can-fail number.

---

## R1 -- the tonic-DA VIGOR channel is MISSING (the #1; the cluster is named for a computation it lacks)

**(a) Brain structure + computation.** PINNED -- **Niv, Daw, Joel & Dayan 2007, "Tonic dopamine:
opportunity costs and the control of response vigor"** (Psychopharmacology 191(3)). Free-operant
behavior is an average-reward semi-Markov decision process in which the agent chooses a response
LATENCY tau. The vigor cost of a response is `C_v/tau` (hyperbolic -- infinitely fast is infinitely
costly); the opportunity cost of the tau time units spent is `rho*tau`, where `rho` is the long-run
average reward rate, proposed to be reported by **TONIC striatal dopamine** (the opportunity cost of
time itself). Minimising the tau-dependent differential cost `C_v/tau + rho*tau` gives the closed form

    tau*  =  sqrt(C_v / rho)          # optimal latency
    vigor =  1/tau*  =  sqrt(rho/C_v) # response vigor ~ sqrt(average reward rate)

so vigor rises with the SQUARE ROOT of the average reward rate. This is the exact form the substrate's
own research note records (`notes/research_neuromodulatory_self_manager_controller_2026-07-08.md`
line 34-36 / 55 / 70: "optimal response vigor is a monotonic function of the long-run average reward
rate rho ... EMA(reward/compute-time)").

**(b) Why the code is not it (file:line -- the ABSENCE, enumerated).** `self_manager.py:6` advertises
a bank of "**6 separable neuromodulatory channels (NE gain, ACh encode/retrieve, 5HT horizon,
tonic-DA vigor, ACC/EVC halting, homeostasis+sleep)**"; `self_manager.py:9` states "**DIAL #1 (the
only dial promoted here): ACC/EVC ADAPTIVE HALTING**". The implemented API is *only* halting
(`accuracy_per_compute`, `tune_halt_threshold`, `run_halting`, `AdaptiveHaltController`). A pure-disk
scan of ALL 249 `hdlab/*.py` finds the token "vigor" in **exactly one file** (`self_manager.py`, the
docstring) and **zero** vigor IMPLEMENTATIONS (`def optimal_latency` / `class VigorDial` /
`response_rate=` -- 0 hits; witness W6/W6b). Halting (when to STOP deliberating) is a DIFFERENT
computation from vigor (how fast/hard to ACT): halting optimises accuracy-per-compute against a
threshold; vigor sets the response rate from the opportunity cost of time. The cluster's namesake dial
is a docstring promise.

**(c) BF replacement.** BUILD the missing dial as `self_manager` DIAL #2 -- the SIBLING dial in the
same bank, reusing the exact one-scalar-in / one-scalar-out architecture of `AdaptiveHaltController`
(no new bespoke machinery): track `rho_hat` = EMA of net reward-per-unit-time (the tonic-DA signal),
emit `tau = sqrt(C_v/rho_hat)`. Prototyped in `experiments/exp_reward_cluster_vigor_dial_v1.py`
(`VigorDial`), `__bf_status__ = "BF"`.

**(d) Blast / live.** DORMANT (named-but-absent). No live loop needs a vigor signal today, so the
present blast is a completed-map gap; but it is exactly the placeholder-risk this audit exists to
catch -- the moment an autonomous-reading agent must choose HOW HARD / HOW FAST to work (effort per
decision, search depth, sample count), there is nothing there, and the "bank of 6 channels" docstring
invites a downstream author to assume it exists. **The cost is proven, not asserted (localization
below): the current no-vigor-dial state (one fixed effort setting) leaves +579 net reward (CI[574,584],
~29% of the adaptive dial's total) on the table under a non-stationary reward rate.**

**(e) BUILD (missing organ).** Not a local edit and not a re-architecture of an existing computation
-- the organ does not exist. Add DIAL #2 to `self_manager` behind the same content-free-scalar
telemetry contract as DIAL #1. Regresses nothing (`self_manager` has 0 importers).

### R1 -- POWERED LOCALIZATION on the dial's OWN metric (can-fail, strongest floor, info-free twin)

`experiments/exp_reward_cluster_vigor_dial_v1.py` -- a fixed-TIME-budget free-operant environment
whose reward rate SWITCHES between rich and sparse regimes (a non-stationary `rho`). Metric = total
NET reward collected per session (the SMDP objective; reward per response minus vigor cost `C_v/tau`,
time advances by `tau`). Arms (paired by session seed, 240 sessions, 2000-sample paired bootstrap):

| arm | tau policy | total net reward / session |
|---|---|---|
| **NIV** (the pinned dial) | `tau = sqrt(C_v / rho_hat)`, `rho_hat`=EMA of net rate | **2000.9** |
| FIXED (strongest floor) | one best `tau` tuned once by argmax net reward = the current no-dial state | 1422.0 |
| TWIN (info-free) | same dial driven by a SHUFFLED reward history (no live rate signal) | 1293.2 |
| ORACLE (ceiling) | `tau = sqrt(C_v / rho_true_local)` | 2419.7 |
| SCRAMBLE | dial driven by a time-scrambled reward stream | 1089.5 |

- **NIV - FIXED = +578.9, CI[574.2, 583.6], CI-separated** -- the missing dial COSTS reward; the
  brain-faithful dial recovers it.
- **NIV - TWIN = +707.8, CI[697.6, 718.5], CI-separated** -- the reward-rate SIGNAL is load-bearing,
  not mere tau-variance (the info-free twin, matched tau-scale, loses).
- **SCRAMBLE (1089.5) < FIXED (1422.0)** -- destroying the telemetry collapses the dial *below* the
  fixed floor (signal-driven, not adaptivity-for-its-own-sake).
- **Mechanism identity:** the closed form `tau*=sqrt(C_v/rho)` matches a grid-argmax of the analytic
  reward rate to rel-err 0.047 (< 0.20).
- **Pinned prediction confirmed:** optimal tau strictly DECREASES as rho rises (vigor ~ sqrt(rho)),
  {0.25:1.414, 0.5:1.0, 1.0:0.707, 2.0:0.5, 4.0:0.354, 8.0:0.25, 16.0:0.177}.

This is both the #1 localization AND the full-stack prototype the owner requested: the component is
built, shown to EXCEL (beats the strongest floor) and the reward-rate signal it needs is the same
`reward/compute-time` telemetry `self_manager` DIAL #1 already consumes -- no upstream organ must
change, and the only downstream consumer (`self_manager` itself) has zero importers, so nothing
regresses.

---

## R2 -- the consequence-learning TEACHER is a symbolic MET/UNMET lexicon vote for a computed affective value

**(a) Brain structure + computation.** PINNED-ish: the teaching signal for consequence / outcome
learning in the brain is a **computed affective VALUE** (OFC/vmPFC outcome value; amygdala; the RPE
carried by phasic dopamine from felt reward) -- a graded value, not a symbolic category read off a
word list.

**(b) Why the code is not it (file:line).** `consequence_learning_loop.py:8` states the design
verbatim: the loop is "bootstrapped by **the seed outcome lexicon standing in for the felt affective
core**." The teacher (`teacher_verdict`, `consequence_learning_loop.py:211-235`) is Signal A =
`goal_typing.congruence_decision` (a structural referent-linked MET/UNMET verdict) AND-gated by
Signal B = `goal_typing.lexicon_predict` (a flat bag-of-words polarity vote). Both are SYMBOLIC
category decisions over hand-declared verb classes; neither computes a graded value. The design
DELIBERATELY excludes the reward-earned appraisal theta (`pfc_gate_cfrpe` /
`context_grounded_valence`), which were VET-confirmed the wrong mechanism (`:11-13`).

**(c) BF replacement.** Feed the loop a graded computed value (an OFC-style outcome-value read / the
force-dynamics valence organ already in the substrate), not a MET/UNMET lexicon category -- OR accept
it as an honestly-labelled bootstrap SUPPLY (a seed affective core the child later refines), which is
the current framing. The distinction that matters: it is admissible as a *bootstrap seed*, a defect if
it becomes the *permanent* value signal.

**(d) Blast / live.** LIVE-IMPORTED-INERT. `grounding_acquisition_loop` imports and re-exports
`credit_window`/`teacher_verdict`/`_credit_targets` (`grounding_acquisition_loop.py:71-72`), but calls
them ONLY inside its own self-test (`:730/:735/:740`), never in the production `consolidation_pass`
path (witness W10b: all 3 call sites are inside a `*self-test*` function). So the module's top-level
code runs on the live grounding path, but its decision functions are inert in production. **This organ
sits in the pri-4 grounding-acquisition closure; its full call-liveness reconciliation belongs to
pri-4** -- catalogued here as the reward-cluster's value-signal fidelity angle, not re-adjudicated.

**(e) RE-ARCHITECTURE** (swap the teacher to a computed value) OR keep-as-labelled-bootstrap.

---

## R3 -- `self_manager` advertises a 6-channel bank; 5 of 6 are unbuilt (the name trap)

**(a) Brain structure + computation.** The 6 neuromodulatory channels are each a real, separately
pinned/precedented scalar controller (per the research note): NE gain (Aston-Jones/Cohen adaptive
gain), ACh encode-vs-retrieve gate, 5HT time-horizon (Doya meta-learning gamma), tonic-DA vigor
(=R1, Niv 2007), ACC/EVC halting (Shenhav 2013 -- the one built), homeostasis+sleep (wake-sleep
renormalisation).

**(b) Why the code is not it (file:line).** `self_manager.py:1` calls the module a "bank of
content-free scalar meta-controllers" and `:6` lists all six, but `:9` admits "DIAL #1 (the only dial
promoted here)". Five of six channels are named-but-absent. This is the same docstring-vs-code
mislabelling the reader audit catalogued for `state_of_mind` (a "state-of-mind" module that is
actually coref).

**(c) BF replacement.** BUILD the remaining dials as content-free scalar siblings (R1 is the
highest-value one; the vigor prototype shows the pattern). Each is a one-scalar-in/one-scalar-out loop
on telemetry already available -- not new bespoke machinery.

**(d) Blast / live.** DORMANT (0 importers). Coverage/mislabelling risk; low present blast.

**(e) BUILD (the dials), starting with R1.**

---

## R4 -- `action_selection` reach uses a cosine, not the linear SR value read-out V = M.R

**(a) Brain structure + computation.** PINNED: successor-representation value is a LINEAR read-out of
the successor matrix against a reward vector, `V(s) = sum_s' M(s,s') R(s')` (Dayan 1993). The reward
vector R is what makes it a *value*.

**(b) Why the code is not it (file:line).** `action_selection.py:186-190` `reach_value` computes
`cos(E[cand] @ M, E[goal])` -- it treats the GOAL vector as if it were the reward and reads value as a
cosine similarity, dropping the reward-weighting the linear read-out carries. This is
RIGHT-OP-WRONG-METRIC (the transport M is trained faithfully by TD/RPE at `:164-167`; only the value
read-out substitutes a cosine).

**(c) BF replacement.** Read `V = M @ R` for an explicit reward vector R where one exists; keep the
goal-cosine only for the pure goal-directed-navigation special case (goal == reward).

**(d) Blast / live.** DORMANT (self-test only; 0 importers). LOW -- defensible for the navigation task
it was certified on.

**(e) LOCAL-FIX** (add the linear read-out; keep the cosine for the goal==reward case).

---

## ADMISSIBLE -- checked and deliberately NOT flagged (the do-not-over-fire discipline; a false positive is a failure)

- **N1 `action_selection` = FAITHFUL (positive control).** TD(0) delta-rule whose error IS the RPE
  (`:164-167` `boot = Enxt + gamma*(Enxt @ M); error = boot - pred  # TD-error == RPE`), an SR-transport
  critic M (Dayan 1993 / Stachenfeld 2017), and a Go/NoGo winner-take-all actor
  (`class GoNoGoActionGate`, `:202-262`, `argmax`) with a clean `w_reach==0` null reduction and an
  anti-tautology identity control (`reach_control_targetcos`). This is PBWM (Frank/O'Reilly). SAME
  op-class; no stand-in.
- **N2 `successor_representation` = FAITHFUL (correction).** `successor_matrix` is the closed form
  `M = (I - gamma*P)^-1` (`:89-98`, `np.linalg.solve(np.eye(n) - gamma*P, I)`), with a TD online rule
  that provably converges to it, a `gamma=0 -> identity` degeneracy check, a planted-positive control,
  and a Neumann-series sparse form for scale. Its "MEASURED-AND-LOST / degrades with scale" verdict is
  a CAPABILITY finding about running SR over lemma states -- NOT a fidelity flaw; the organ IS the
  brain's pinned equation. Do not read "SR is a stand-in."
- **N3 `self_manager` DIAL #1 (ACC/EVC halting) = FAITHFUL (positive control).** EVC value-per-effort
  (Shenhav-Botvinick-Cohen 2013): `accuracy_per_compute` tuned once by argmax accuracy-per-compute,
  frozen, applied as a local reflex, with a scramble control that collapses the gain. Content-free
  scalar; SAME op-class.
- **N4 `goal_typing` / `goal_achievement` / `result_type_induction` = OUR-INVENTION-judged-on-task
  (ADMISSIBLE).** Goal / means-end / outcome comprehension is a cognitive-level function with NO
  pinned neural equation, so these are inventions judged on TASK, not brain-fidelity (like the POS /
  parse organs). They are honestly labelled: `goal_achievement`'s vote weights (`_IDIOM_VOTE_WEIGHT=2`
  etc., `:752/:1038/:1337`) are "a FIXED design choice declared before any scoring run, not tuned per
  item"; `result_type_induction` is a glass-box decision-list learner whose class definitions are
  authored from WordNet glosses "NEVER by checking which DesireDB item it would flip"
  (`result_type_induction.py:59-62`). The prior audit already dispositioned these UNSCORABLE.
- **N5 `state_of_mind` = coref tracker, labelled NOT-ToM (already dispositioned).** The docstring
  disambiguates it (`:1-8` "NOT THEORY-OF-MIND ... a COREFERENCE entity-tracker") and it is LIVE via
  the coref path (`event_centrality_coref` importer), already dispositioned in the reader audit +
  ORGAN_MAP as coref (the invented `count + beta*exp(-lam*dist)` salience). The real ToM gap
  (false-belief, TPJ/mPFC) is a clean unbuilt-organ target, not a stand-in.

## POSITIVE CONTROL (the enumeration + the guard fire on known structure -- witness W1, W13)

The denominator's own positive controls recover known-true structure (`action_selection` /
`successor_representation` / `self_manager` have provably 0 importers; `state_of_mind` IS reached by
the reader via coref; `consequence_learning_loop` IS imported by the grounding loop). The witness's
byte-search guard (W13) is shown to FIRE on a token that IS present (`AdaptiveHaltController` in
`self_manager`) while correctly reporting vigor ABSENT -- so W6/W6b's "vigor is missing" is not a
vacuous pass of a broken search.

## COMPLETENESS SCAN -- the closure organs not individually named above (scanned, all clean or dispositioned)

The 40-organ closure was scanned for decision-standing stand-in signatures (fitted-at-inference
weights, surface-only decisions, hand-lexicon-as-decision, external tool). The non-cluster organs in
the closure are (i) already-dispositioned reader/parse/coref organs (`arc_parser`, `pos_tagger`,
`thematic_role_labeler`, `coreference_resolver`, `event_bundle`, `binding`, `situation_model_accumulate`,
`graded_parser`, ...); (ii) FOUNDATION supply (`verb_lexical_similarity`, `lexical_similarity`,
`grounded_similarity`, `wordnet_polarity_propagation`, `idiom_grounding`, `animacy_lexicon`,
`closed_class_lexicon`, `frame_induction`); (iii) grounding-subsystem organs owned by pri-4
(`grounding_acquisition_loop`, `reading_grounding_loop`, `hd_fact_store`, `cleanup_family`,
`gap_detector`, `self_improving_loop`). None introduces a NEW decision-standing stand-in in the
reward/action-selection/vigor DECISION path beyond R1-R4. So R1-R4 + N1-N5 are the full set on the
cluster's own closure.
