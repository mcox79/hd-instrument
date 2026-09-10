---
problem: audit_the_reward_action_selection_vigor_control_cluster_for_non_brain_faithful_stand_ins
status: SOLVED
bar: "PASS = a CATALOG.md in this folder of the reward/action-selection/vigor cluster, with (a) an ENUMERATED DENOMINATOR (every organ in the cluster's import closure, reconciled against actual flag defaults, not comments -- state HOW you enumerated); (b) for EACH organ the five disk-verified fields -- brain structure+computation (PINNED cite or OUR-INVENTION), why-the-code-is/isn't-it at file:line, the BF replacement, LIVE-vs-DORMANT with the proving grep, LOCAL-FIX-vs-RE-ARCHITECTURE; (c) a TOP-K ranked by blast x severity; (d) ONE powered localization of the #1 stand-in (a can-fail measurement on its own metric with the strongest floor + an info-free twin LOSING, on the organ's own population -- no cross-population number); and (e) a machine-checkable PURE-DISK witness verification/test_*.py that reproduces every LIVE/DORMANT/stand-in claim on the current bytes (a positive control that the guard fires). ... A rigorous result of 'this cluster is fully brain-foundational / all dormant, here is the enumerated proof' is a FULL PASS."
result: "ENUMERATED DENOMINATOR = 40-organ import closure of the 7 seeds (AST trace over 249 hdlab modules); 3/7 seed decision organs (action_selection, successor_representation, self_manager) are DORMANT-ISLANDED with 0 hdlab importers, goal_achievement DORMANT (1 non-live importer), consequence_learning_loop+goal_typing LIVE-IMPORTED-INERT via the grounding subsystem, state_of_mind LIVE via coref. #1 finding = the tonic-DA VIGOR channel is MISSING (the cluster's namesake computation; 'vigor' occurs in all of hdlab exactly once, a docstring mention in self_manager.py:6). POWERED LOCALIZATION (Niv 2007 tau*=sqrt(C_v/rho) prototype, own metric = total net reward per fixed-time free-operant session, n=240 sessions, 2000-sample paired bootstrap): the brain-faithful vigor dial earns +578.9 net reward/session CI[574.2, 583.6] over the strongest fixed floor -- CI-separated -- and +707.8 CI[697.6, 718.5] over the info-free twin."
floor: "strongest FIXED floor = one best fixed latency tuned once by argmax net reward on a held-out calibration session (the current no-vigor-dial state) = 1422.0 net reward/session; the vigor dial NIV = 2000.9 (+578.9 CI-sep). Info-free TWIN floor (same dial driven by a shuffled reward history) = 1293.2 (NIV +707.8 CI-sep). ORACLE ceiling = 2419.7."
controls: "info-free TWIN (dial driven by a SHUFFLED reward history, matched tau-scale) LOSES to NIV +707.8 CI-sep -> the reward-rate signal is load-bearing, not tau-variance; SCRAMBLE (dial driven by a time-scrambled reward stream) = 1089.5 collapses BELOW the fixed floor -> signal-driven; ORACLE (tau from the true local rate) = 2419.7 is the ceiling (>= NIV); closed-form identity tau*=sqrt(C_v/rho) matches a grid-argmax of the reward rate to rel-err 0.047; monotonicity vigor~sqrt(rho) confirmed; JOINT-EVC COMPOSITION (exp_reward_cluster_joint_evc_v1.py, using the REAL shipped AdaptiveHaltController) -- BOTH-dials beats halting-only +664.8 CI-sep and vigor-only +992.1 CI-sep, and the halting decisions are byte-identical under a vigor toggle (separability proven); denominator positive controls fire (0-importer dormancy of the 3 pinned organs, state_of_mind reached via coref, cll imported by grounding); witness byte-search guard shown to FIRE on a present token (AdaptiveHaltController) while reporting vigor absent."
files_changed: "experiments/exp_audit_reward_cluster_denominator_v1.py, experiments/exp_reward_cluster_vigor_dial_v1.py, experiments/exp_reward_cluster_joint_evc_v1.py, experiments/exp_self_manager_neuromodulatory_bank_v1.py, experiments/exp_action_selection_linear_sr_value_v1.py, experiments/exp_theory_of_mind_belief_partition_v1.py, experiments/exp_consequence_graded_value_teacher_v1.py, experiments/exp_successor_features_state_abstraction_v1.py, verification/test_audit_reward_cluster_standins.py, notes/problems/audit_the_reward_action_selection_vigor_control_cluster_for_non_brain_faithful_stand_ins/CATALOG.md, notes/problems/audit_the_reward_action_selection_vigor_control_cluster_for_non_brain_faithful_stand_ins/SOLVED.md. NO hdlab/ writes (Q111)."
reverify: ".venv/Scripts/python.exe verification/test_audit_reward_cluster_standins.py  (28/28 PASS)"
---

# SOLVED -- brain-fidelity audit of the reward / action-selection / vigor control cluster

## WHAT WAS BUILT
A disk-verified CATALOG of the reward/action-selection/vigor cluster (`CATALOG.md`), an enumerated
import-closure denominator (`exp_audit_reward_cluster_denominator_v1.py`), a brain-foundational
prototype of the ONE genuine fidelity defect the audit found -- the MISSING tonic-DA vigor dial
(`exp_reward_cluster_vigor_dial_v1.py`) -- with a powered can-fail localization, and a machine-checkable
pure-disk witness (`verification/test_audit_reward_cluster_standins.py`, **20/20**). NO `hdlab/` writes
(Q111): the fixes are proposed diffs + a prototype; strategy lands them.

## WHAT WAS MEASURED (and what the disk said vs the brief)
- **The prior audit's paragraph-level scoring HELD, and the disk confirmed it at file:line.** The
  three cluster organs with a pinned brain equation are FAITHFUL, not stand-ins: `action_selection`
  (TD/RPE + SR-transport + Go/NoGo; `action_selection.py:164-167`, `:202-262`),
  `successor_representation` (M=(I-gamma*P)^-1; `:89-98`), `self_manager` DIAL #1 (Shenhav EVC halting).
  The goal-COMPREHENSION organs are honestly-labelled OUR-INVENTIONS with no pinned neural equation
  (UNSCORABLE), and `state_of_mind` is a correctly-labelled coref tracker. So there is **no live,
  unflagged, non-brain-faithful DECISION stand-in of the reader-audit-C1 kind** in this cluster.
- **The one genuine fidelity defect is a MISSING organ, not a stubbed one.** The cluster is named
  "vigor control" and no vigor computation exists: the token "vigor" occurs in all 249 `hdlab/*.py`
  exactly once, as a docstring mention (`self_manager.py:6`), which advertises a "bank of 6
  neuromodulatory channels" while `:9` builds only DIAL #1. The vigor channel was DESIGNED on disk
  (`notes/research_neuromodulatory_self_manager_controller_2026-07-08.md` line 34-36/55/70, with its
  exact form) and never built.
- **The #1 finding is localized with a powered, can-fail number on the dial's own metric.** I copied
  the PINNED Niv 2007 computation exactly (`tau* = sqrt(C_v/rho)`, vigor ~ sqrt(average reward rate))
  and measured it on a non-stationary free-operant environment. The brain-faithful dial beats the
  strongest fixed baseline (the current no-dial state) by **+578.9 net reward/session CI[574.2,583.6],
  CI-separated**, and beats an **info-free twin by +707.8 CI-sep**; scramble collapses below the fixed
  floor; the closed form matches a grid-argmax (rel-err 0.047); vigor ~ sqrt(rho) monotonicity holds.
  This proves the missing dial is a REAL, pinned, buildable computation whose absence COSTS reward --
  not a benchmark artifact.
- **The vigor dial COMPOSES with the SHIPPED halting dial (joint EVC), proving the separable-scalar-
  bank architecture the substrate's research note argues for.** `exp_reward_cluster_joint_evc_v1.py`
  imports the REAL `hdlab.self_manager.AdaptiveHaltController` and runs a 2x2 factorial on a task
  heterogeneous in both item difficulty and reward rate: the full bank (BOTH dials) beats halting-only
  by +664.8 CI-sep and vigor-only by +992.1 CI-sep, and the halting hop-decisions are BYTE-IDENTICAL
  whether vigor is off or on (each dial reads only its own telemetry). So building the remaining
  neuromodulatory dials (R3) is a low-risk ADDITIVE program, not a re-architecture. Honest regime note:
  vigor's marginal is material only when response latency is a material fraction of total trial time
  (when deliberation dominates, halting carries the win) -- the correct EVC prediction, not a defect.

## FOLLOW-ON PROTOTYPES (owner-directed 2026-09-09: "prototype all of those now, brain foundationally")
Every follow-on the audit named is now prototyped, each copying its brain computation and each passing a
can-fail gate (faithful arm beats the strongest tuned floor CI-sep + an info-free twin loses). Witness
W15-W18. All BF-audited and honestly labelled PINNED vs BF_UNPINNED. NO hdlab writes (Q111).
- **The self_manager BANK completed (R3):** the 4 missing neuromodulatory dials -- NE gain-on-plasticity
  (adaptive learning rate, Yu & Dayan 2005 / Behrens 2007), ACh encode/retrieve (Hasselmo 2006), 5HT
  time-horizon (Doya 2002), homeostasis/sleep (Tononi-Cirelli SHY) -- each a content-free scalar dial,
  each beating its tuned fixed floor + info-free twin CI-sep (`exp_self_manager_neuromodulatory_bank_v1.py`).
  With DIAL #1 (shipped halting) + DIAL #2 (vigor, prototyped) that is the full 6-channel bank, and the
  joint-EVC proof shows the dials compose additively (separable) -- so landing the bank is additive, not
  a re-architecture. **BF.**
- **R4 (`action_selection` value read-out):** the linear SR value V = M @ R (Dayan 1993) beats the
  shipped cosine-to-one-goal stand-in on agreement with the Monte-Carlo true value (Spearman 0.80 vs
  0.39, +0.42 CI-sep), uses the REAL `successor_representation` M, identity M@R==definition to 1e-4.
  **BF.** (`exp_action_selection_linear_sr_value_v1.py`)
- **ToM (the ABSENT TIER-6 organ):** a per-agent OBSERVATION-GATED belief partition (decoupled
  metarepresentation, Leslie 1987 / Wimmer & Perner 1983) over the FHRR algebra reproduces Sally-Anne
  false belief: 1.00 vs a reality-only floor 0.00 (+1.00 CI-sep), info-free twin 0.36, and a true-belief
  control confirms it agrees with reality when the agent witnessed. **BF_UNPINNED** (ToM has no pinned
  neural equation -- labelled honestly, not as PINNED). (`exp_theory_of_mind_belief_partition_v1.py`)
- **R2 (the consequence-learning teacher):** a graded OFC/vmPFC value teacher (Padoa-Schioppa 2006)
  beats the binary MET/UNMET category the loop ships -- Pearson 0.90 vs 0.86 (+0.044 CI-sep) and, on the
  decision the binary category cannot make (pick the more extreme of two same-sign outcomes), 0.75 vs
  0.68 (+0.061 CI-sep). **BF.** (`exp_consequence_graded_value_teacher_v1.py`)
- **NE located sub-finding (reported, not hidden):** the pure gain-as-inverse-temperature reading of NE
  is only a marginal, config-dependent win over a well-tuned fixed gain (a delta-rule value estimate is
  itself adaptive), so the ROBUST pinned NE win is the plasticity / learning-rate one built above.
- **THE #1 PERFORMANCE-VS-BRAIN GAP CLOSED (owner "keep pushing"): the state-representation lever.** The
  audit's honest perf-vs-brain diff named `successor_representation`'s MEASURED-AND-LOST /
  degrades-with-scale as the biggest signal loss -- caused (its own docstring) by tabular SR over atomic
  lemmas with "median ONE observed successor per word". The brain avoids this because place fields ARE
  the SR over a shared OVERLAPPING feature basis and grid cells are its eigenvectors (Stachenfeld 2017).
  `exp_successor_features_state_abstraction_v1.py` runs the SR as SUCCESSOR FEATURES (Barreto 2017)
  psi=(I-gamma A)^-1 phi, TD-learned with linear FA, and GENERALIZES to held-out states (cos-to-MC-truth
  0.89) where the REAL tabular organ collapses (0.82; +0.070 CI-sep), beating an info-free twin +0.52
  CI-sep, with the TD-learned operator matching the closed form (rel-err 0.018) and a rank-d/2 grid-cell
  eigen-basis still generalizing. **This is the deepest follow-on: the right fix at the level the signal
  is actually lost, and the one that unblocks model-based / hierarchical control.** **BF.**
- **100% brain-foundational check (owner 2026-09-09):** every prototype copies the brain's actual
  computation with a citation; the one component without a pinned neural equation (ToM) is labelled
  BF_UNPINNED and built on the accepted FHRR algebra + the accepted cognitive false-belief computation;
  parameters are swept, never adopted; no external LLM / off-the-shelf model / eval-fitted classifier is
  used anywhere.

## WHAT WAS NOT ESTABLISHED (and what I would withdraw first if wrong)
- **The vigor localization is measured on a MODEL free-operant environment, not a live substrate
  loop.** No live loop currently consumes a vigor signal, so there is no end-to-end substrate number
  -- the +578.9 is the cost of a fixed vs adaptive effort policy in a faithful reproduction of the
  Niv physics, the same construction-proof status `self_manager`'s shipped DIAL #1 witness carries.
  **This is the first thing I would withdraw** if challenged: it demonstrates the dial is real and
  separable, not that any live board number moves today (nothing consumes it yet).
- **R2 (the consequence-learning teacher) overlaps the pri-4 grounding closure.** I catalogued it as
  the reward-cluster's value-signal fidelity angle and proved it LIVE-IMPORTED-INERT (its decision
  functions are called only inside self-tests, witness W10b), but its full call-liveness reconciliation
  belongs to pri-4, which owns that closure. I did not re-adjudicate it.
- **"DORMANT-ISLANDED" is module-level import reachability**, an upper bound on liveness that I
  reconciled by hand for the one borderline call edge (the grounding teacher). I did not build a full
  runtime call-graph; the AST import closure + the call-site reconciliation is the precedent's method.

## KEY REALIZATIONS (the enabling moves)
1. **A missing organ can be the #1 audit finding, and it is provable the same way a stand-in is** --
   by building the brain's actual computation and showing its ABSENCE costs something (the fixed-vigor
   floor is the current state; the adaptive dial beats it CI-separated). "Test 4" (does the DEFECT cost
   us, vs does an ALTERNATIVE exist) is answered by making the current no-dial state the FLOOR arm.
2. **The reward cluster's characteristic computation is not in its pinned decision organs at all** --
   those (BG/TD/SR/EVC) are faithful and dormant. The defect is one docstring line up: a "bank of 6
   channels" that builds 1. Reading the module's OWN cited research note surfaced the exact missing
   form (vigor ~ sqrt(rho)) that the code never implemented.
3. **The Niv self-consistency trap:** the optimal latency `tau*=sqrt(C_v/rho)` uses rho = the average
   reward RATE (opportunity cost), NOT the reward MAGNITUDE. Conflating them (feeding magnitude as rho)
   made the oracle lose to a fixed policy; separating them (rho = mu^2/(4 C_v) at the self-consistent
   fixed point) made the oracle dominate and the identity check pass. And the objective must be a
   FIXED-TIME budget, not fixed-#-responses -- otherwise a fast policy games the ratio-of-sums.

## SUBSTRATE INCORPORATION MANIFEST (for strategy, per owner 2026-09-09)
- **INCORPORATE (proposed hdlab diffs -- strategy lands; all prototyped + can-fail here):**
  (1) `self_manager` DIALS #2-6 -- the tonic-DA VIGOR dial (`VigorDial`) plus NE/ACh/5HT/homeostasis,
  each a content-free scalar controller byte-portable from the prototype cells, reusing the exact
  architecture of `AdaptiveHaltController`; land as sibling dials so the "bank of 6" docstring stops
  being a promise (regresses nothing -- `self_manager` has 0 importers). (2) `action_selection` linear
  SR value read-out `V = M @ R` alongside the cosine (R4). (3) a graded-value teacher option for
  `consequence_learning_loop` (R2). (4) a NEW `hdlab/theory_of_mind.py` organ (the per-agent
  observation-gated belief partition; fills the ABSENT TIER-6 ToM gap). Wire nothing live yet where
  there is no consumer; each is `__bf_status__` BF (BF_UNPINNED for ToM).
- **INCORPORATE-AS-DURABLE-NEGATIVE / AUDIT UPDATE:** fold into `notes/BRAIN_FOUNDATIONAL_AUDIT.md`
  the corrected TIER-6 verdicts (see AUDIT UPDATE below) -- especially that the reward cluster's pinned
  decision core is FAITHFUL+DORMANT and the one real gap is MISSING-not-stubbed vigor.
- **DO-NOT-INCORPORATE:** do not wire the vigor dial into a live loop yet (no consumer -> would be a
  latent island); do not re-flag `goal_typing`/`goal_achievement`/`result_type_induction` as fidelity
  defects (they are honestly-labelled OUR-INVENTIONS, UNSCORABLE); do not touch the pri-4 grounding
  reconciliation of `consequence_learning_loop`.
- **No load-bearing external CORPUS** was used or needs ingesting (the vigor prototype is a synthetic
  environment; the brain grounding is the Niv 2007 closed form, already in the research note on disk).

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md TIER 6, per the SOLVER PROTOCOL)
- The 2026-08-26 paragraph "GOALS/REWARD & METACOGNITION tiers fidelity-scored" is CONFIRMED and now
  disk-verified at file:line, with one SHARPENING: `self_manager`'s "DA vigor / ACC-EVC halting"
  line conflates two channels -- **only ACC/EVC halting is built; tonic-DA VIGOR is MISSING** (the
  cluster's namesake, PINNED Niv 2007, `self_manager.py:6` docstring only). Prototyped brain-faithfully
  here (+578.9 CI-sep). Recommend TIER 6 record vigor as **MISSING (pinned equation exists)**, not
  as part of `self_manager`'s built deviation.
- `action_selection` / `successor_representation` remain **SAME op-class / FULLY-PINNED FAITHFUL**;
  the audit doc's "MEASURED-AND-LOST" for SR is a capability note, not a fidelity flaw (re-affirmed).

## TLDR (plain English)
We have been checking, part by part, whether each piece of the system works the way a brain actually
does, and fixing or removing the fakes. Until now that check had never covered the parts that handle
motivation and choice -- learning from reward, deciding what to do, and how hard to try. I went through
that cluster carefully and proved every claim against the code on disk. The good news: the core
decision pieces that have a known brain formula are built correctly, and they're mostly switched off
(dormant), so there's no hidden fake cheating in a live path. The one real gap is that the cluster is
named for "how hard to try" (vigor) but that piece was never actually built -- the code only mentions
it in a comment. I built the missing piece the way the brain does it (try harder when the environment
is rewarding, ease off when it's lean) and showed, with a careful can-fail test, that having it earns
about 40% more reward than the current fixed-effort setting, and that the win genuinely comes from
reading the reward signal (a scrambled version loses). Nothing was wired into the live system; this is
a map plus a proven prototype for the strategy session to land.

## QUESTIONS
None -- the deliverable shape is met (enumerated denominator, per-organ fields, TOP-K, powered #1
localization, pure-disk witness 20/20) and the honest finding (faithful+dormant core; one MISSING
pinned organ, prototyped) is a full pass under the bar.

## NEXT STEPS (candidate follow-on problems, not done here)
1. **Land the vigor dial** as `self_manager` DIAL #2 (proposed diff above); then the higher-value
   build: a live autonomous-reading control loop that CONSUMES it (effort/depth per read) so the gain
   becomes board-visible -- today nothing consumes vigor, so it would land latent.
2. **Build the other 4 unbuilt neuromodulatory dials** (NE gain, ACh encode/retrieve, 5HT horizon,
   homeostasis) -- each a pinned/precedented content-free scalar; R3.
3. **The consequence-learning value signal** (R2): decide whether the MET/UNMET lexicon teacher stays
   a labelled bootstrap or is replaced by a computed OFC-style outcome value -- coordinate with pri-4.
4. **`action_selection` linear SR value read-out** (R4): add `V = M @ R` alongside the goal-cosine.
5. **Theory of Mind is a clean unbuilt-organ target** (TPJ/mPFC false-belief; the Sally-Anne nested-HRR
   work sits in `experiments/`, never promoted) -- surfaced by the `state_of_mind` name trap.
