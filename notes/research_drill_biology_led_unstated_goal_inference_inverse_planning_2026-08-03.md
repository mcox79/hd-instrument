# Research drill: biology-led unstated-goal-inference mechanism (inverse planning / Bayesian ToM) (2026-08-03)

Filed by: Director. Complements (does not duplicate) the same-day SR/TD drill
(`notes/research_drill_biology_led_predictive_learning_mechanism_successor_representation_2026-08-03.md`,
commit 7c679fe10), which covers the CAUSAL/PREDICTIVE axis (what follows from what) and flagged
"SR-as-inverse-policy-goal-inference" as its own novel-synthesis idea (P=0.35, uncertain). This
drill supplies the GOAL/INTENTION axis: how the brain infers an UNSTATED goal from observed action,
whether that literally IS "invert the SR", and how it composes with the SR/predictive stage.

## 0. KB-check (mandatory, run before writing)

`bash tools/substrate_query.sh` run four times pre-drill (schema v2, chunk-content, tau=0.15, k=5):

- `"inverse planning bayesian theory of mind goal inference from action"` -> top hit cosine=0.3213
  (math-atoms "Bayesian inference" node — a generic math/lexical atom, not conceptual ToM content).
  No inverse-planning content in KB.
- `"action understanding rational agent goal inference mentalizing network TPJ mPFC"` -> top hits
  cosine 0.30-0.32, WordNet lexical nodes + `research_decisions_2026-07-09.md` (relational-graph vs
  grounded-meaning drill, a DIFFERENT question). No mentalizing-network mechanism content.
- `"sally anne theory of mind nested belief representation"` -> top hit cosine=0.4639, the
  **`theory_of_mind_sally_anne_nested_hrr_v1` cell itself** (HARD_PASS; metrics.json + prereg
  `preregs/2026-06-27_theory_of_mind_sally_anne_nested_hrr_v1.md`). This is prior art directly on
  point — disk-verified below (section 3).
- `"successor representation goal state predictive map policy"` -> top hit cosine=0.39, WordNet
  "representative"/"representational" lexical nodes. No SR content (confirms same-day companion
  drill's finding: SR/TD is genuinely new territory, and by extension so is
  SR-as-inverse-policy-for-goals).

**Verdict: genuinely new territory for the MECHANISM question.** The only prior art is the
already-landed `theory_of_mind_sally_anne_nested_hrr_v1` cell, which builds per-agent BELIEF
representation (nested HRR bind/unbind + agent-partitioned banks + refuse-gate), not goal
INFERENCE from action. Disk-verified below: the cell's own prereg (Q5/ARM_DIAG_TOM_LITE,
"goal-attribution" diagnostic arm) explicitly frames goal representation as **supplied**
(`"agent has bound goal-vector in per-agent bank"` — the goal-vector is WRITTEN INTO the bank by
the trial generator, then READ OUT), not INFERRED from an action trajectory. That is the precise
gap this drill addresses: the existing organ can REPRESENT a goal once told; it does not yet
INFER an unstated one from behavior. Not a re-derivation — a genuinely new mechanism question
building on a verified, reusable organ shape.

---

## 1. PRIMARY: inverse planning / Bayesian theory of mind

**Definition and origin.** Baker, Saxe & Tenenbaum, 2009, *Cognition* 113(3):329-349, "Action
understanding as inverse planning" (verified via MIT 9.s915 course PDF + ScienceDirect abstract,
directly fetched). Extended to joint belief-desire-percept attribution in Baker, Jara-Ettinger,
Saxe & Tenenbaum, 2017, *Nature Human Behaviour* 1(4), article 0064, "Rational quantitative
attribution of beliefs, desires and percepts in human mentalizing" (verified via compdevlab.yale.edu
PDF + Semantic Scholar).

**Mechanism (the "how").** The brain represents an intuitive theory of intentional agents built on
a **principle of rational action**: an agent is expected to plan approximately optimally
(POMDP/MDP-style sequential decision process) to achieve ITS goals given ITS beliefs about the
world. Goal inference is then literally **Bayesian inversion of this forward planning model**:

```
P(goal | observed_action) proportional_to P(observed_action | goal, rational_planning) * P(goal)
```

i.e. the observer runs (or approximates) the SAME forward planning process the actor would use FOR
EACH CANDIDATE GOAL, scores how well the actual observed trajectory matches what THAT goal would
have produced under near-optimal planning, and weights by a prior over goals. The 2017 extension
generalizes this from a single scalar goal to a JOINT posterior over (belief, desire, percept)
triples, inverting a POMDP forward model rather than a fully-observed MDP — this is the
generalization that also handles FALSE BELIEF (the actor can act "irrationally" relative to true
world-state while acting perfectly rationally relative to ITS OWN, possibly wrong, belief state) —
i.e. Baker et al.'s BToM is the Sally-Anne-capable generalization of inverse planning, not a
separate mechanism. **Noisy/suboptimal action** is handled via a softmax/Boltzmann-rational
likelihood (agents are BETTER-than-chance, not perfectly optimal, planners) rather than a hard
argmax match — this is what lets the model degrade gracefully rather than requiring exact plan
match, and is the calibrated-uncertainty analog to a refuse-gate.

**Modern operational form.** Zhi-Xuan et al., arXiv:2006.07532, "Online Bayesian Goal Inference for
Boundedly-Rational Planning Agents" (found this session) is the direct temporal/incremental update
of the same framework: goal posterior is updated SEQUENTIALLY as each new action arrives (not
batch-inferred after the fact), which is the operationally relevant form for a reader accumulating
evidence sentence-by-sentence rather than seeing a full trajectory upfront — directly compatible
with the substrate's `situation_model_accumulate` register (see section 4).

**Neural substrate — mentalizing network.** Mar 2011 (*Annual Review of Psychology* 62:103-134,
carried forward from the SR drill, not re-verified here) plus 2024-2025 refinements found this
session (He et al. 2025, `scan.psych.columbia.edu/papers/He_et_al_2025.pdf`; ScienceDirect
2024 ALE meta-analysis "Mapping the mentalizing brain"): core network = bilateral **TPJ**/pSTS +
**mPFC**/dmPFC + precuneus/PCC, substantially overlapping the default-mode network. Functional
division of labor (converging across sources, contested in degree but not in direction): **TPJ**
tracks transient/momentary belief-and-perspective content (reorienting to WHAT the other currently
believes/attends to); **mPFC** extracts abstractions over action — enduring traits, and (per the
2025 refinement already noted in the companion SR drill) inferential UNCERTAINTY about others'
mental states specifically, rather than mental content per se; **precuneus** is recruited for
imagining the SCENE underlying the other's action (the situation-model substrate for the inference,
not the inference itself). This is the same three-way split (transient content / stable
abstraction / scene-context) the companion drill already flagged, now confirmed with an independent
2024-2025 citation set, not merely carried forward.

### (a) Mechanism answer, direct

**Yes — inverse planning IS the brain's mechanism for unstated-goal inference from action,** and it
generalizes (not a separate mechanism) to false-belief cases via POMDP inversion. This is
well-established, not novel synthesis (unlike the SR drill's flagged item) — Baker et al. 2009/2017
is foundational, widely replicated, and the mainstream computational-ToM account; treat with normal
(not lit-scan-deflated-to-0.35) confidence, calibration-penalty applied per discipline (deflate
0.15-0.25 for our OWN implementation uncertainty, not for the underlying biology, which is
well-supported): **P=0.65 for "this is the right brain-mechanism class"**, deflated from what would
otherwise be a very high-confidence literature consensus, specifically to price in the gap between
"established in continuous-domain/spatial-navigation ToM tasks" and "not yet demonstrated on
narrative/textual event sequences at our substrate's grain" — that generalization gap is real and
unverified, not the core mechanism claim.

### (b) Does goal inference literally = "invert the SR" (confirms or corrects the SR drill's P=0.35)?

**Corrects, upward, with a precise distinction.** The SR drill was right that this is a real,
promising synthesis and correctly flagged it as not-yet-found-combined-in-one-source; this
session's search found the missing combination: **Machado, Barreto et al.-line successor FEATURES
+ inverse-RL work, concretely the BASIS algorithm** (Wang et al., "Basis for Intentions: Efficient
Inverse Reinforcement Learning using Past Experience", found this session at openreview /
researchgate) and **"Successor Representation Active Inference"** (arXiv:2207.09897, found this
session) both explicitly combine SR/successor-feature machinery with goal/intention/reward
inference. The mechanism is precisely the SR drill's proposed decomposition: SR/successor-features
factor `V(s) = M(s) . w` into a policy-dependent reachability map `M` (the "what follows" /
predictive-axis content) and a LOW-DIMENSIONAL reward/goal weight vector `w`. **Goal inference under
this decomposition is NOT "invert the whole SR" — it is "hold the already-learned/observed M fixed
and infer only the small `w`"** (BASIS's actual mechanism: multi-task pretraining gives a basis of
`M`'s spanning the environment's dynamics; a NEW agent's intention is recovered by inferring `w` in
that fixed basis from a handful of observed transitions). This is a materially different (and
CHEAPER) computation than Bayesian inverse planning's "replan under each candidate goal and compare
trajectories" — it is closer to a coordinate-projection than a per-candidate forward simulation. **P
for this SPECIFIC formalization raised to 0.50** (from the SR drill's 0.35) given the found
combination is real published work, not synthesized here for the first time — but still capped
below established-literature confidence because BASIS/SR-active-inference are ONGOING/recent (2022,
2024-era) research lines, not textbook-established like Baker et al. 2009, and neither has been
applied to narrative/event-relation domains (both are spatial-navigation/robotics settings).

**Practical reading for the substrate**: these are TWO COMPLEMENTARY mechanisms at different
grain, not competitors — (i) Baker-et-al inverse planning = the FULL, generative,
candidate-goal-scored-by-simulated-replanning account, brain-verified as the general-purpose
mechanism (handles false-belief, arbitrary novel goals, small-N observation); (ii)
SR/successor-feature-decomposition inverse-RL = a CHEAPER, amortized special case that works when
the dynamics/reachability-map `M` is ALREADY LEARNED (stable environment, many past agents observed
in it) and only the goal-weight `w` differs across agents/episodes — the brain's plausible
fast-path once the environment is familiar, inverse planning being the slow/general fallback for
novel/complex cases. This maps onto a real behavioral distinction (familiar vs novel-environment ToM
judgments) though this drill did not find a citation demonstrating the brain literally
switches mechanisms this way — flag as an ARCHITECTURAL hypothesis for the substrate, not a
verified neuroscience claim, P=0.40 on the dual-mechanism framing specifically.

### (c) Relation to the ALREADY-VALIDATED `theory_of_mind_sally_anne_nested_hrr_v1` organ

Disk-verified (metrics.json + prereg read above): the organ's SHAPE is per-agent partitioned banks
+ nested HRR bind/unbind (`bind(agent, bind(believes, bind(object, location)))`) + a refuse-gate for
"insufficient evidence" (Q4). **This shape hosts inverse-planning goal inference directly, with one
addition, not a redesign.** Today the organ's ARM_DIAG_TOM_LITE goal-tracking arm SUPPLIES the goal
vector (written by the trial generator into the agent's bank) and only tests READOUT. To make goal
inference EARNED rather than supplied: replace the write-in step with a **candidate-goal-scoring
loop** — for each candidate goal-schema `g` (see section 2 for where these come from), bind a
HYPOTHETICAL trajectory-vector `bind(agent, bind(pursues, g))`, compare (via the SAME cosine-cleanup
readout the organ already uses) against the ACTUALLY-OBSERVED bound action-sequence vector for that
agent, and write into the agent's bank only the highest-scoring (or refuse if no candidate clears
threshold, reusing Q4's refuse-gate mechanism exactly). This is architecturally a drop-in extension:
same per-agent bank partition, same nested-bind primitive, same refuse-gate, same cosine-cleanup
readout — the only new piece is the "score candidates, take argmax-or-refuse" loop, which is a
software wrapper around the existing bind/readout ops, not a new HRR primitive.

---

## 2. GLASS-BOX + EARNED fit: candidate goal-schemas, scoring, refuse-gate

**Where do candidate goal-schemas come from (the load-bearing lock-compatibility question)?**
Three tiers, ranked by lock-compatibility:

1. **Best (fully earned): schemas induced from the substrate's OWN accumulated experience.**
   The `situation_model_multibank` / `CausalLinkRegister` organs already track, per narrative,
   WHAT STATES actually got reached (disk-verified WIRED_AND_PIPELINE_USED per MEMORY). A candidate
   goal-schema is simply "a state this-or-similar agents have been observed to pursue/reach before,
   in this or similar situation-contexts" — i.e. candidate goals are HYPOTHESES DRAWN FROM THE
   SUBSTRATE'S OWN REPLAY BUFFER of previously-encountered agent trajectories (same replay
   mechanism the companion SR drill proposes for negative-sampling, reused here for POSITIVE
   candidate generation instead). This requires zero external supply — it is the Kintsch
   "construction" overgenerate step (companion drill section 3) specialized to goal-content: the
   construction stage proposes candidate goal-vectors from associative/replay memory, inverse
   planning scores them, refuse-gate handles insufficient evidence.
2. **Acceptable (earned, narrower): a small closed set of DOMAIN-GENERIC goal PRIMITIVES**
   (approach/avoid/acquire/protect/inform — schema-theoretic universals with direct developmental-
   psych grounding, e.g. Woodward's infant goal-attribution literature on reach-actions, not
   independently re-verified this session but consistent with the already-cited Tomasello 2005 in
   the sally-anne prereg) bound with situation-specific FILLERS (the object/location/agent slots the
   organ already has) rather than schemas literally read off external text. This is a small,
   fixed, HAND-SPECIFIED primitive inventory (the "bootstrap primitive by hand, then hand
   rule-learning to the loop" pattern already standing per MEMORY's error-routing discipline) —
   lock-compatible as a BOOTSTRAP, with the expectation the loop later learns to propose novel
   schema COMBINATIONS from the tier-1 replay mechanism.
3. **Flag, do NOT do by default: schemas supplied from an external knowledge base/LLM-generated
   goal list.** This is the disallowed borrowed-reader pattern (no bolt-on parser/reader per
   MEMORY); explicitly flagged here because it is the easiest shortcut and the one most likely to
   be reached for under implementation pressure — same caution the companion SR drill raised about
   external negative-sample banks.

**Scoring = the inverse-planning likelihood, made glass-box.** `P(action_sequence | goal_g)` is
approximated, per Baker et al.'s Boltzmann-rational softmax, as
`cosine_similarity(observed_bound_action_vector, hypothetical_bound_vector_under_g)` raised through
a temperature-scaled softmax over candidates — this is a direct, auditable substitute for "simulate
the plan a rational agent pursuing g would take and compare", appropriate because the substrate does
not have (and per lock-compatibility disciplines should not borrow) a full forward planner/simulator;
the SIMILARITY-TO-HYPOTHETICAL-BOUND-STRUCTURE proxy is the same class of move the organ already
uses for belief-readout, so it is architecturally consistent, not a new kind of approximation.

**Refuse-gate = honest "insufficient evidence".** Reuse the sally-anne organ's existing Q4 refuse
mechanism directly: if the top candidate's softmax-normalized score does not clear a threshold
margin over the SECOND candidate (not just over a fixed cosine floor — margin-over-runner-up is the
correct honesty criterion, since a single close-flat distribution over many candidates should refuse
even if the top score is nominally high), emit REFUSE rather than a forced pick. This is the same
principle the mPFC/dmPFC uncertainty-tracking finding (section 1, and the companion drill section 3)
argues the brain itself does — uncertainty gating is not a substrate-only add-on, it has a
neural-mechanism analog.

**Fair / can-fail test.** Three-arm minimum, per envelope-fail-band convention:
- **ARM_RANDOM_BASELINE**: pick uniformly among candidate goal-schemas. Expected accuracy = 1/|G|.
- **ARM_LEXICAL_BASELINE**: pick the goal-schema whose surface-word overlap with the action
  description is highest (bag-of-words proxy) — this is the "does the substrate need ANY inference
  at all, or is goal-word leakage doing the work" fairness check, directly analogous to the
  sally-anne organ's ARM_NO_PARTITION_BASELINE and the copy-context distractor discipline already
  standing for event-relation cells.
- **ARM_INVERSE_PLANNING (mechanism arm)**: the candidate-scoring + refuse-gate mechanism above.
- **HARD_PASS bands (draft, matching the sally-anne organ's calibration convention)**: mechanism-arm
  accuracy on GOAL_CORRECT >= lexical-baseline + 0.20 absolute AND >= random + 0.30 absolute;
  refuse-gate honesty measure: on a held-out set of INSUFFICIENT-EVIDENCE trials (goal genuinely
  ambiguous given the observed action prefix), refuse-rate >= 0.60 (mirrors Q4's existing
  refuse-control design, not a new discipline).
- **HARD_FAIL**: mechanism arm within 0.05 of lexical baseline (no goal-content signal beyond
  word-overlap) OR refuse-gate never fires on genuinely-ambiguous trials (dishonest overconfidence,
  the same failure class already caught 4+ times per MEMORY's "vet negatives as hard as positives"
  standing discipline).

---

## 3. COMPOSITION: SR (causal axis) + inverse-planning (goal axis) into one relation-inference stage

Both drills converge on the SAME two-stage Kintsch construction-integration architecture (companion
drill section 3), which is the natural composition point, not two bolted-together modules:

- **Construction (overgenerate candidates)**: the SR/TD-contrastive predictive map (companion
  drill) overgenerates candidate SUCCESSOR STATES (the causal/predictive axis: what happens next).
  The inverse-planning mechanism (this drill) overgenerates candidate GOAL-SCHEMAS (the
  intentional axis: why the agent is acting), scored via the SAME cosine-similarity-to-hypothetical-
  bound-structure primitive used throughout the substrate's readout layer — the two candidate
  streams are structurally homogeneous (both are ranked lists of FHRR-bound hypotheses), which is
  what makes them composable rather than requiring separate machinery.
- **Integration (coherence-filter)**: the already-validated `CausalLinkRegister`
  (0.9722 vs 0.0 baseline cross-chapter, per MEMORY) is the natural single filter for BOTH streams:
  a candidate goal `g` is favored if it renders the candidate causal chain COHERENT (the SR-map's
  predicted successor states line up with what pursuing `g` would produce) — i.e. **goal inference
  and causal/predictive inference are not independent estimates to be separately thresholded and
  combined; they mutually constrain each other inside ONE integration/coherence-filter pass**: a
  goal hypothesis that makes the observed causal chain more coherent (Trabasso antecedent-consequent
  terms line up) is evidence FOR that goal, and conversely the SR/TD map's successor predictions
  should be reweighted toward trajectories consistent with the highest-scoring goal (Baker et al.'s
  own point — desire/goal and belief attribution are JOINTLY inferred, not sequentially). This is
  the same "joint belief-desire-percept attribution" structure Baker et al. 2017 generalized to
  (section 1), now mapped onto the substrate's existing coherence-loop rather than proposed as new
  machinery.
- **Concrete wiring**: predictive-map candidates (companion drill) feed the SAME
  coherence-gated integration pass that goal-schema candidates (this drill) feed; the
  `CausalLinkRegister`'s existing coherence score is extended to take BOTH candidate types as input
  and jointly re-rank them, rather than building two independent single-axis integration passes.
  This is architecture reuse, not a new organ.

---

## 4. Lock-compatibility summary

- **Inverse-planning goal-scoring mechanism**: EARNED. Uses the substrate's own bound
  action/hypothetical-goal FHRR vectors and cosine-cleanup readout, both already-built primitives
  (same class the sally-anne organ already uses). No borrowed planner, reader, or LLM.
- **Candidate goal-schema SOURCE — the one place external supply is tempting**: tier-1 (replay-drawn
  from own accumulated experience) and tier-2 (small hand-specified universal primitive set,
  bootstrap-by-hand per standing error-routing discipline) are BOTH lock-compatible. Tier-3
  (externally-supplied/LLM-generated schema list) is flagged explicitly as the disallowed pattern —
  Director's recommendation is tier-2 bootstrap (5-10 domain-generic primitives, hand-specified) to
  get the mechanism running, with tier-1 (replay-induced novel schema combinations) as the
  loop-learned generalization path, mirroring the MEMORY-standing "bootstrap primitive by hand, then
  hand rule-learning to the loop" pattern exactly.
- **Refuse-gate**: reuses the already-certified sally-anne Q4 mechanism; no new lock concern.
- **SR/goal-weight decomposition (section 1b)**: EARNED if `M` (reachability map) and `w` (goal
  weight) are BOTH learned from the substrate's own encountered trajectories (as in the companion
  drill's TD/contrastive spec) — no borrowed component required, but this is the LOWER-confidence
  (P=0.50) mechanism of the two on offer; recommend it as a later OPTIMIZATION over the full
  inverse-planning mechanism (higher P=0.65), not the first thing built.

## 5. RANKED RECOMMENDATION

**Rank 1 (P=0.65, established biology, new to our substrate): build inverse-planning goal inference
as a direct extension of the already-validated `theory_of_mind_sally_anne_nested_hrr_v1` organ** —
replace its ARM_DIAG_TOM_LITE supplied-goal-vector write with a candidate-scoring-and-refuse loop
over tier-2 hand-specified goal primitives (bootstrap), reusing the organ's existing per-agent
partition + nested-bind + cosine-cleanup-readout + refuse-gate machinery unchanged. This is the
GENERAL-PURPOSE mechanism, handles novel goals and false-belief interaction, and is the
best-supported brain account (Baker et al. 2009/2017, replicated widely).

**Rank 2 (P=0.50, real but newer/narrower literature, cheaper): SR/successor-feature-decomposition
goal inference** (infer only the low-dimensional goal-weight `w` against an already-learned
reachability map `M`) as a FAST-PATH optimization once the companion SR drill's predictive map is
built and stable for a given narrative-domain — recommend as a follow-on efficiency pass, not the
first build, since it presumes rank-1's (or the companion drill's) predictive map already exists and
is stable enough to hold fixed.

**Rank 3 (architecture, not new mechanism, P=0.55 matching companion drill's rank-2): wire both
rank-1 (goal axis) and the companion drill's rank-1 (causal/predictive axis) into ONE
Kintsch-style construction-integration pass**, with the already-validated `CausalLinkRegister` as
the shared integration/coherence filter, per section 3 above — do this AT THE SAME TIME as building
rank-1's mechanism rather than bolting the composition on afterward, since the two candidate streams
are designed to be structurally homogeneous from the start.

## Citations (verified this session)

Baker, Saxe & Tenenbaum, 2009, *Cognition* 113(3):329-349, "Action understanding as inverse
planning" (MIT 9.s915 PDF + ScienceDirect abstract, directly accessed); Baker, Jara-Ettinger, Saxe &
Tenenbaum, 2017, *Nature Human Behaviour* 1(4):0064, "Rational quantitative attribution of beliefs,
desires and percepts in human mentalizing" (compdevlab.yale.edu PDF + Semantic Scholar, directly
accessed); Zhi-Xuan et al., arXiv:2006.07532, "Online Bayesian Goal Inference for
Boundedly-Rational Planning Agents" (sequential/incremental BToM, found this session); Wang et al.,
"Basis for Intentions: Efficient Inverse Reinforcement Learning using Past Experience" (BASIS
algorithm, OpenReview/ResearchGate, found this session — the direct SR/successor-feature +
inverse-RL combination that upgrades the companion drill's P=0.35 flag to P=0.50); "Successor
Representation Active Inference", arXiv:2207.09897 (found this session, corroborates the SR-as-
Bayesian-filtering / goal-decomposition framing); Mar 2011, *Annual Review of Psychology*
62:103-134 (carried forward from companion drill, not re-verified); He et al. 2025,
scan.psych.columbia.edu/papers/He_et_al_2025.pdf, and a 2024 ScienceDirect ALE meta-analysis
("Mapping the mentalizing brain") — both found this session, confirming/refining the TPJ-transient
vs mPFC-stable-trait vs precuneus-scene division of labor. Sally-Anne organ (disk-verified, not
re-derived): `data/exp_theory_of_mind_sally_anne_nested_hrr_v1/metrics.json` (VERDICT=HARD_PASS),
`preregs/2026-06-27_theory_of_mind_sally_anne_nested_hrr_v1.md`, citing Wimmer & Perner 1983,
Saxe & Kanwisher 2003, Apperly & Butterfill 2009, Tomasello et al. 2005.

## HEADLINE

Biology says unstated-goal inference is **Bayesian inverse planning**: the observer runs the SAME
rational-planning model the actor would use, for each candidate goal, and picks (or Boltzmann-
weights) the goal whose implied plan best explains the observed action — Baker, Saxe & Tenenbaum
2009, generalized to joint belief-desire-percept POMDP inversion in 2017 (handles false-belief for
free, the same generalization that makes it Sally-Anne-compatible). This CORRECTS the companion SR
drill's P=0.35 "SR-as-inverse-policy" flag upward to P=0.50: a real, if newer and narrower, published
line (BASIS; SR-active-inference) DOES combine successor-representation/successor-feature
decomposition with intention/reward inference — but as a cheaper FAST-PATH special case (infer only
the low-dimensional goal-weight against an already-learned reachability map), not as the primary
mechanism, which remains full inverse planning (P=0.65, established literature). The
already-validated `theory_of_mind_sally_anne_nested_hrr_v1` organ's SHAPE (per-agent bank + nested
bind/unbind + refuse-gate) hosts this directly: swap its supplied-goal-vector write for a
candidate-scoring-and-refuse loop over a small hand-specified goal-primitive set (lock-compatible
bootstrap tier), with replay-induced novel schema combinations as the loop-learned generalization
path (tier 1) — never an externally-supplied schema list (tier 3, flagged, disallowed). Composition
with the companion SR drill's predictive axis is natural, not bolted-on: both drills independently
converged on the SAME Kintsch construction-integration frame, so goal-candidates (this drill) and
successor-state-candidates (companion drill) are structurally homogeneous inputs to the SAME
already-validated `CausalLinkRegister` coherence-filter, jointly re-ranking each other exactly as
Baker et al.'s own joint belief-desire attribution does. Fair test: beat a lexical-overlap baseline
by >=0.20 and random by >=0.30 on goal-schema selection, with an honest refuse-rate >=0.60 on
genuinely-ambiguous held-out trials — mirroring the sally-anne organ's own calibration convention,
not a new discipline.
