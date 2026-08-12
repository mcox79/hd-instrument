# Research drill: the missing utility/preference-function leg for glass-box goal-achievement (2026-08-09)

Filed by: Research (Sonnet), director-requested all-night drill. Trigger:
`notes/director_brain_fidelity_SYNTHESIS_and_direction_verdict_2026-08-09.md` — 3x brain-fidelity synthesis
concluded the #1 architecture gap is representing a character's goal as a binary class-token instead of an
inferred UTILITY/PREFERENCE FUNCTION scored against the outcome, and named Chandra et al. 2024 "Storytelling
as Inverse Inverse Planning" + Baker/Saxe/Tenenbaum + Jara-Ettinger Naive Utility Calculus as the concrete
prior art to drill. Complements (does not duplicate) the already-landed
`notes/research_drill_biology_led_unstated_goal_inference_inverse_planning_2026-08-03.md`, which covers a
DIFFERENT problem (inferring an UNSTATED goal from observed action). This drill is the missing companion:
given an ALREADY-STATED goal (DesireDB supplies the desire text directly), how does the brain SCORE whether
an outcome satisfies it, and can that be built glass-box on FHRR.

Companion substrate grounding (read before dispatching, not re-derived): `hdlab/goal_achievement.py` (current
3-channel binary/lexical organ, 0.686 macro-F1 vs 0.620 rule on DesireDB n=80, disk-verified this session);
`hdlab/binding.py` (`bind`/`unbind`), `hdlab/bundling.py` (`bundle`), `hdlab/glass_box_loop.py`
(`cleanup_with_margin` — margin-based refuse-gate primitive), `experiments/exp_multidrive_vsa_policy_h3_cpu_v1.py`
(PP-360, HARD_PASS: CES-harmonic scalar multi-attribute utility optimization over a VSA-encoded multi-step
policy — proves the substrate already optimizes a weighted multi-component scalar utility end-to-end, but the
utility there is over externally-simulated drive-satisfaction scalars, not extracted from text via FHRR
predicate binding — that extraction is the actual novel piece this drill targets). Capability registry query
(`tools/capability_registry_query.py --serves "utility function scoring"` / `"goal achievement"`) returned
**0/73 matches** — confirmed genuine build gap, not a rediscovery.

---

## 1. Corrected citation + full mechanism: Chandra et al., "Storytelling as/Acting as Inverse Inverse Planning"

**Citation correction (verified via PubMed PMID 37962526 + DBLP + the paper itself, high confidence):** the
paper is **Kartik Chandra, Tzu-Mao Li, Joshua B. Tenenbaum, Jonathan Ragan-Kelley**, "Storytelling as Inverse
Inverse Planning," *Topics in Cognitive Science* 16(1):54-70, 2024 (DOI 10.1111/tops.12710) — the archival
version of the SIGGRAPH 2023 paper "Acting as Inverse Inverse Planning" (same 4 authors, arXiv:2305.16913,
fully read primary source). The 8-author list in the task prompt does not exist; none of Chen/Grand/
Pinto/Wu/Kleiman-Weiner/Andreas appear on this paper (Kleiman-Weiner co-authors a *different*, unrelated
Chandra paper on emotion/ToM). Flagging this correction because it changes nothing about the mechanism content
below (independently re-derived from the actual paper + its public code) but the citation itself should be
fixed at the source.

**Mechanism, read from primary source (SIGGRAPH 2023 full text) + independently corroborated against the
public GitHub code (`github.com/kach/acting-as-inverse-inverse-planning`):**

- **World/planner model**: a standard finite MDP (gridworld: robot + a semi-autonomous "cheese" agent + goal
  tiles). Reward = fixed bonus for reaching own goal tile, small per-move cost, plus a **social-alignment
  term**: robot gets bonus `ρ·r_cheese` when the cheese scores reward, `ρ ∈ {-3,-1,0,+1,+3}` (help/hinder/
  neutral). Solved by **exact value iteration** (hand-written Bellman DP, no learning). Boltzmann-rational
  action selection: `P(a|s,H) ∝ exp(β·Q(s,a))`.
- **Inverse planning (1st inversion, the audience)**: exact enumerative Bayes over the small discrete
  hypothesis space `H = ⟨goal, ρ, rationality-flags⟩` — table update, no sampling, no PPL.
- **Inverse-INVERSE planning (2nd inversion, the storyteller/author)**: the author's objective (e.g.
  "make the audience believe the robot is helping," "produce an ironic reveal," "shape a narrative arc") is
  a **hand-written closed-form functional of the audience's posterior trajectory** — quoted verbatim from the
  paper, e.g. `f_help(σ) = Σ_t P(ρ>0 | σ_1:t)`, `f_irony(σ) = Σ_t[P(G=green|σ_1:t) + P(ρ<0|σ_1:t,G=green) +
  P(ρ>0|σ_1:t,G=pink)]`. This objective is **NOT inferred by any further Bayesian layer** — it is supplied
  directly by the researcher/artist. Optimized via beam search (discrete domain) or gradient descent through
  a differentiable physics sim + RL value function (continuous "hill" domain — the one place a neural net
  appears, an ordinary actor-critic, not an LLM).
- **Zero LLM anywhere in the pipeline**, confirmed both from the paper's own Limitations section (frames
  future scaling as needing SMC/amortized-neural approximations to the *exact* Bayesian machinery — i.e. they
  discuss adding neural approximation as unbuilt future work, not as something already there) and from direct
  code inspection.
- **Predecessor, reused near-verbatim as the base inverse-planning engine**: Ullman, Baker, Macindoe, Evans,
  Goodman & Tenenbaum (2009), "Help or Hinder: Bayesian Models of Social Goal Inference," NeurIPS 22 — the
  `H=⟨goal,ρ⟩` hypothesis tuple, the value-iteration planner, the hierarchical softmax, and the ε-hypothesis-
  reset trick are all taken from this paper. Fully symbolic, no neural/learned component, predates the deep
  learning era of this subfield entirely.
- **RSA as the single-utterance sibling**: the paper explicitly frames itself as generalizing Frank & Goodman's
  Rational Speech Acts (RSA) — literal-listener/pragmatic-speaker/pragmatic-listener recursive softmax-Bayes —
  from a single utterance choice to a temporally-extended belief *trajectory*. `problang.org`'s RSA formalism
  (`U_S1(u;s) = log L0(s|u) - C(u)`, softmax speaker choice) and `agentmodels.org`'s WebPPL "agents as
  programs" tutorial (utility as an explicit `state -> real` function, `factor(alpha*expectedUtility(action))`
  for Boltzmann-rational choice, `Infer()`-based Bayesian goal inference) were both fetched directly and are
  literal, off-the-shelf, non-LLM symbolic substrates for the "inverse planning" half of this lineage.

**What this mechanism is FOR, precisely** — this matters for feasibility (section 3): inverse (-inverse)
planning as built by Chandra/Ullman/Baker infers **who wants what from what they DID** (an unstated goal from
an action trajectory), and, one layer up, **what actions an author should choose to shape a reader's
belief-formation process**. It does not, anywhere in this lineage, contain a "does this outcome satisfy this
already-known goal" scoring rule — see section 3, this is a load-bearing finding, not an oversight in my
reading.

---

## 2. The utility/preference-function formalism: Baker/Saxe/Tenenbaum + Naive Utility Calculus

**Base form** (Baker Saxe Tenenbaum 2009, *Cognition* 113(3):329-349, primary source read in full; formalized
explicitly as an equation in the 2016 TiCS review and the 2020 Cognitive Psychology paper, Box 1 Eq. I /
Eq. 1): **`U(plan, outcome) = R(outcome) - C(plan)`** — reward of the achieved state minus cost of the actions
taken to reach it. Inference: `P(goal|actions) ∝ P(actions|goal)·P(goal)`, with `P(actions|goal)` a softmax
over the planner's Q-values (β = rationality/determinism parameter).

**Multi-attribute generalization — TWO distinct forms found, not one:**
1. **Sequential/hierarchical sum** (Jara-Ettinger, Schulz & Tenenbaum 2020, *Cognitive Psychology* 123:101334,
   primary source read in full — the fullest quantitative treatment, explicitly supersedes the 2016 TiCS
   sketch): an *intention* is an ordered sequence of goals; `U(intention) = Σ(rewards of goals pursued) -
   Σ(costs of reaching them)`. Tested AGAINST and beat a multiplicative/rate alternative `U=R/C` (r=0.85 vs
   0.70 on cost-fit, r=0.95 vs 0.87 on reward-fit) — direct empirical evidence for additive-difference over
   ratio form. NOT a flat weighted sum over independent attributes.
2. **Flat weighted-sum discrete-choice form** (Lucas, Griffiths, Xu, Fawcett et al. 2014 "The Child as
   Econometrician"; Jern, Lucas & Kemp 2017 "People learn other people's preferences through inverse
   decision-making" — both secondary/WebFetch-summarized confidence, not independently primary-verified this
   session): for NON-sequential multi-attribute choice, `U_i = Σ_f w_f·x_{i,f}` — literally the attribute-
   weighted-sum form the director's synthesis doc hypothesized. This is the closer analog to "decompose a
   desire into 2-4 attribute-predicates and sum weighted satisfaction."

**Inference method — the load-bearing finding for feasibility**: across Baker 2009 (M1/M2/M3/H model
comparison), Baker Jara-Ettinger Saxe Tenenbaum 2017 *Nature Human Behaviour* 1:0064 (BToM vs TrueBelief vs
NoCost vs MotionHeuristic comparison, primary source read), and the 2020 Cognitive Psychology paper (Monte
Carlo likelihood-weighting over a SMALL enumerable intention set, e.g. 5 candidate intentions in their worked
example) — **a small number of hand-specified candidate hypotheses + Bayesian model comparison is not a
simplification of this literature, it IS the field's own standard practice.** This directly licenses a
tier-2 hand-specified attribute-primitive bootstrap (same pattern the 08-03 drill already recommended for
candidate goal-schemas) as literature-faithful, not corner-cutting.

**Genuine gap in this literature (flag honestly, do not paper over)**: **no graded/normalized
partial-satisfaction scoring function was found anywhere in this cluster.** Utility is reported as a raw
scalar reward-minus-cost sum, never as a normalized 0-1 "fraction of preference structure satisfied." If we
want "satisfies-2-of-3-attributes = partial credit," that specific piece is **our own addition**, not borrowed
from the literature — treat it as novel synthesis, capped P=0.50 per calibration discipline (see section 5).

**Scaling caveat**: even Baker 2017's modest 24-world hypothesis space needed approximate POMDP solvers
(grid-based approximation, SARSOP) because exact POMDP planning is intractable in general — a primary-source,
explicit acknowledgment that this apparatus does not scale to open-ended hypothesis sets without approximation
machinery. Relevant to section 3's feasibility read.

---

## 3. THE REFRAME — we need the EASIER problem, not the one the apparatus was built for

This is the single most important finding of the drill, independently surfaced by the third lit-scan and
directly checked against DesireDB's actual task shape:

**Every mechanism found (Ramirez & Geffner classical-planning cost-difference; Baker/Ullman value-iteration +
Bayes; agentmodels.org's WebPPL `Infer()` pattern) scores a candidate goal by the COST/PROBABILITY OF THE
OBSERVED ACTION SEQUENCE under a policy for that goal — never by matching the final outcome-state's
description against the goal's description.** The literature's implicit claim: goal inference is inference
over *behavior-generating processes*, not outcome pattern-matching. A pure "does the final state look like it
satisfies goal G" check is explicitly a DIFFERENT, EASIER problem in this literature's own terms — closer to
classical STRIPS **goal-satisfaction checking** (`state ⊨ goal`, an O(1)-ish symbolic test), not
goal-inference-from-behavior (which requires a planner/value-iteration/POMDP-solve per candidate).

**DesireDB is exactly the easier problem.** The desire text IS the stated goal (Rahimtoroghi et al. hand it to
us directly — "I wanted to save him"); we are never asked to infer an unstated goal from an action trajectory.
What's missing (per the director's SYNTHESIS doc) is a graded SCORING of the outcome against that
already-known goal, replacing the current binary class-token match. **This means the heavy, months-scale part
of the inverse-planning literature — exact value iteration, POMDP solving, SMC particle filters over action
sequences (Zhi-Xuan et al. 2020 arXiv:2006.07532's SIPS, confirmed via its Gen.jl/`SymbolicPlanners`
dependency to require a real classical-planner call per candidate, not O(1)) — is NOT required for this leg.**
That apparatus is for the ALREADY-DRILLED, separate, deferred competency (unstated-goal inference from
behavior, `research_drill_biology_led_unstated_goal_inference_inverse_planning_2026-08-03.md`), not for
today's gap. What we actually need to borrow from this literature is narrower and cheaper: the UTILITY-FUNCTION
REPRESENTATION (attribute-weighted decomposition, section 2) applied as a satisfaction check against a stated
goal, no planner, no value iteration, no per-hypothesis MDP solve.

This reframe is a synthesis/interpretation on my part (not a claim any cited paper makes directly) — flagged
as such, P=0.65 (the underlying facts — what each mechanism scores, that DesireDB gives a stated goal — are
each independently high-confidence and disk/primary-source verified; the "therefore we don't need the heavy
apparatus" inference is my own, hence not capped at the full literature-established rate, but not novel-
synthesis-capped either since it's a straightforward deduction from verified facts).

---

## 4. Mapping to the owned substrate: minimal glass-box buildable version

**Representation.** A goal's utility function = a **weighted bundle of role-bound attribute-predicates**:
`U_g = bundle_i( w_i * bind(ATTR_ROLE_i, predicate_i) )`, using the existing `hdlab/binding.py` `bind` and
`hdlab/bundling.py` `bundle` primitives unchanged. `predicate_i` values come from a **small, hand-specified,
domain-generic attribute-primitive set** (tier-2 bootstrap, licensed by section 2's finding that this is
literature-standard practice, not a shortcut) — candidates: ACQUIRE/POSSESS, LOCATION-REACHED,
SOCIAL-CONNECTION, AVOID-HARM/SAFETY, ACTIVITY-COMPLETION, EMOTIONAL-STATE-ACHIEVED. This generalizes the
existing `goal_typing._class_relation`'s hand `CLASS_REGISTRY` (currently a BINARY achievement/failure-verb
class list, per `notes/formalize_narrative_part2_goal_achievement_inference_2026-08-08.md`) from one binary
relation into `k` independently-scoreable attribute dimensions — an extension of an owned mechanism, not a new
organ class.

**Attribute activation (which attributes does THIS desire invoke?)**: cosine-cleanup of the desire text's
extracted goal-vector (reuse `goal_typing.find_desired_state`, already owned) against the small
attribute-role codebook — cheap, O(k).

**Scoring the outcome (does it satisfy the activated attributes?)**: for each ACTIVE attribute role, `unbind`
it from an FHRR encoding of the outcome text, then `cleanup_with_margin` (already owned,
`hdlab/glass_box_loop.py`) against a 3-way filler codebook {SATISFIED, VIOLATED, ABSENT}. Concretely this
reuses `goal_achievement.py`'s EXISTING `relation_channel` (recurrence/negation detection) and
`valence_channel` (polarity) logic, run PER-ATTRIBUTE instead of holistically over the whole outcome string —
i.e. the new build is "the same two channels, gated by attribute-relevance" not new NLP machinery. Sum signed,
weighted per-attribute contributions into a scalar `Û`; sign(`Û`) + margin decides Fulfilled/Unfulfilled;
refuse-to-majority if margin too small (reuses `cleanup_with_margin`'s margin output directly, same shape as
the already-certified sally-anne organ's Q4 refuse-gate).

**What's genuinely new** (the one real build): (a) the small attribute-primitive vocabulary + role codebook
(hand-specified, ~1 day), (b) wiring the existing relation/valence channels to run per-attribute instead of
whole-string (refactor, ~1-2 days), (c) the weighted-sum combination + margin-refuse decision (new, small,
~1 day). Everything else — bind/unbind/bundle/cleanup_with_margin, negation-scope detection, WordNet
verb-synonym expansion — is 100% reused, unmodified, owned machinery.

**Honest gap vs. literature**: scoring via FHRR bind/unbind + cosine-cleanup, instead of an actual Bayesian
probability computation, is a **substrate-native reinterpretation** of the literature's discrete
enumerate-and-score pattern (section 2's "small candidate set + Bayesian comparison IS the standard" finding
licenses the enumerate-and-score SHAPE; it does not license the specific cosine-similarity substitution for
the scoring arithmetic, which is our own choice, same class of move the already-certified sally-anne organ and
the 08-03 inverse-planning drill's proposed scoring already make). Flagged, deflated accordingly (section 5).
Partial-satisfaction/weighted-sum-of-graded-attribute-scores is, per section 2, **not literature-precedented**
at all — this piece is genuinely novel synthesis, capped P=0.50.

---

## 5. Cheap decisive test (run FIRST, before committing to the fuller build)

**Single cheapest experiment**: a CPU-only `exp_dev` cell, reusing the EXISTING DesireDB n=80 fair bench that
`goal_achievement.py`'s 3-channel organ was validated on (no new data needed):

1. Hand-specify 5-6 attribute primitives (bootstrap, tier-2, ~1 day) as FHRR role/filler codebooks.
2. Wire `relation_channel`/`valence_channel` to run per-attribute (reuse, refactor — no new NLP).
3. Add the utility-leg as a **4th channel**, inserted into `goal_achievement_verdict`'s precedence chain
   ONLY on the cohort where the current 3 channels currently ABSTAIN-TO-MAJORITY (`channel == "majority"`,
   i.e. both `relation_channel` and `valence_channel` returned `None`) — this isolates the leg's OWN
   contribution rather than letting it override channels that already work, matching the
   anti-premature-HARD_FAIL / strict-ADD discipline already standing this arc.
4. Score on: (a) the abstain-to-majority cohort specifically (recovery rate), (b) full n=80 macro-F1 vs the
   current 0.686 organ and the 0.620 rule baseline, (c) a **wrong-goal pairscramble control** (shuffle
   outcome<->desire pairing; the utility score must collapse toward chance/majority, or the leg is reading
   outcome-valence alone and ignoring the goal, the same failure class already caught 4+ times this arc).

Estimated build: ~2-4 days end to end for a first cheap version (well inside "weeks," see section 6), fully
reusing owned primitives, CPU, no new external dependency.

---

## Falsifiable predictions — HARD-PASS / HARD-FAIL (pre-registered here for the exp_dev cell)

**HARD-PASS** (build the fuller weighted/learned version): utility-leg recovers **>=40%** of the
abstain-to-majority cohort correctly (matches the director's SYNTHESIS Probe-2 bar) **AND** full-bench
macro-F1 >= 0.686 (no regression vs the current organ) **AND** pairscramble macro-F1 collapses to within 0.05
of the majority-class-only baseline (confirms goal-conditioning, not outcome-valence leakage).

**MIDDLE_BAND** (real but partial signal — iterate on attribute vocabulary/weights, don't commit to full
build yet): recovers 15-40% of the cohort, full-bench macro-F1 does not regress, pairscramble collapses.

**HARD-FAIL** (utility-leg is not adding real signal — deprioritize, do not force a rescue): recovers **<15%**
of the abstain-to-majority cohort (no signal beyond noise) **OR** full-bench macro-F1 drops below 0.620 (the
plain rule baseline — actively worse than doing nothing) **OR** pairscramble score stays within 0.03 of the
real-goal score (the leg is scoring outcome valence alone, ignoring the goal — same dishonest-overconfidence
failure class the sally-anne Q4 refuse-gate and 08-03 drill's refuse-gate design both exist to catch).

---

## 6. Honest feasibility verdict (adversarial, as requested)

**Weeks-scale, not months-scale — but ONLY because of the reframe in section 3.** If the task were "infer an
unstated goal from a character's action sequence" (the 08-03 drill's territory), the honest answer would be
months: that requires the FULL apparatus (value iteration or classical-planner calls per candidate hypothesis,
POMDP-scale approximate solvers per Baker 2017's own admission, potentially SMC per Zhi-Xuan 2020 to avoid
exponential blowup as the hypothesis space grows) — real computational machinery, not a lookup, and none of
the three lit-scans found a way to avoid this cost for THAT problem. Because DesireDB hands us the goal as
stated text, we sidestep that entire cost structure: no planner, no value iteration, no per-hypothesis MDP
solve — just attribute-predicate extraction (cheap, existing organs) + per-attribute cosine-cleanup scoring
(cheap, existing primitive) + a weighted sum (new, trivial arithmetic). The genuinely novel, unprecedented
piece (graded partial-satisfaction scoring, section 2's gap) is also small in engineering terms even though
it's un-precedented in the literature — it's a sum-and-normalize over an already-small attribute set, not a
new inference algorithm.

**Adversarial check requested by the task — does the apparatus fundamentally need a neural LM?** No, confirmed
independently by all three lit-scans, primary-source and code-level for the Chandra et al. lineage: the entire
inverse-(inverse-)planning stack as published is value iteration + exact/enumerative Bayes + beam
search/gradient descent, zero LLM anywhere. The only neural components found in the ENTIRE search (across
9+ papers/frameworks) are (a) an actor-critic RL value/policy net in Chandra et al.'s unrelated continuous-
physics "hill" domain variant, and (b) none at all in the Baker/Ullman/Jara-Ettinger/Ramirez-Geffner/
agentmodels.org lines. So the glass-box invariant is not at risk from this literature's own design — the risk,
if any, is scope creep toward building the FULL (unstated-goal-inference) apparatus when only the narrower
(stated-goal-satisfaction) piece is needed for the currently-identified gap.

---

## Cross-thread synthesis

- Directly extends `notes/director_brain_fidelity_SYNTHESIS_and_direction_verdict_2026-08-09.md`'s Probe 2
  (utility-predicate leg) from a named-but-unspecified axis into a concrete, cited, buildable mechanism spec
  with pre-registered HARD-PASS/HARD-FAIL bands.
- Sharpens (does not contradict) `research_drill_biology_led_unstated_goal_inference_inverse_planning_2026-08-03.md`:
  that drill's inverse-planning machinery (candidate-goal-scoring loop reusing the sally-anne organ) targets
  UNSTATED-goal inference from action — a genuinely harder, separate, still-deferred competency. This drill's
  finding (section 3) explains WHY it's harder: it needs the full planner/POMDP apparatus that the
  stated-goal-satisfaction problem does not.
- Extends `notes/formalize_narrative_part2_goal_achievement_inference_2026-08-08.md`'s diagnosis (the
  achievement comparison currently resolves via a hand `CLASS_REGISTRY` that doesn't generalize) by giving the
  specific literature-grounded generalization target: multi-attribute weighted utility (section 2), not a
  bigger hand list.
- Corroborated by `hdlab/goal_achievement.py`'s own docstring finding this arc: "crude high-coverage beats
  principled-narrow on messy prose (3x)" — motivates keeping the utility-leg as an ADDITIVE 4th channel
  targeting the abstain cohort specifically, not a wholesale replacement of the working relation/valence
  channels (section 5's test design follows this directly).

## Substrate-product implications

A working utility-scoring leg would let the product make an auditable, per-attribute-decomposed claim about
*why* a narrative outcome does or doesn't satisfy a stated goal (e.g. "satisfied SAFETY and LOCATION but
violated SOCIAL-CONNECTION") rather than a single opaque Fulfilled/Unfulfilled flag — a genuine differentiator
for any application needing inspectable narrative/behavioral-log comprehension (support-ticket resolution
tracking, goal-directed dialogue evaluation, procedural-content QA) where "did the user's request get
satisfied, and specifically how/how not" is the actual customer question, not just a binary label. This is the
same auditability differentiator already identified as the field-parity-beating edge for the current 3-channel
organ (glass-box trace beats accuracy-parity as the product story) — the utility leg deepens that trace from
"which lexical channel fired" to "which specific goal-attribute was satisfied or violated," which is a more
defensible product claim than accuracy numbers alone given the corpus-specific (non-general) nature of the
current accuracy edge.

## Citations (verified count: 11 primary-source-read, 4 secondary/corroborated, 2 code repositories inspected)

**Primary source read in full this session:**
1. Chandra, Li, Tenenbaum & Ragan-Kelley, "Acting as Inverse Inverse Planning," SIGGRAPH 2023 (arXiv:2305.16913, full PDF read).
2. Chandra, Li, Tenenbaum & Ragan-Kelley, "Storytelling as Inverse Inverse Planning," CogSci 2023 proceedings (escholarship.org, full PDF read).
3. Baker, Saxe & Tenenbaum (2009), "Action understanding as inverse planning," *Cognition* 113(3):329-349 (saxelab.mit.edu PDF, full read).
4. Jara-Ettinger, Gweon, Schulz & Tenenbaum (2016), "The Naive Utility Calculus," *TiCS* 20(8):589-604 (sll.stanford.edu PDF, full read).
5. Jara-Ettinger, Schulz & Tenenbaum (2020), "The Naive Utility Calculus as a unified, quantitative framework for action understanding," *Cognitive Psychology* 123:101334 (cscl.yale.edu PDF, full read).
6. Baker, Jara-Ettinger, Saxe & Tenenbaum (2017), *Nature Human Behaviour* 1:0064 (cscl.yale.edu PDF, full read).
7. agentmodels.org Chapter 3, "Agents as programs" (WebPPL, code verified verbatim).
8. agentmodels.org Chapter 4, "Reasoning about agents" (WebPPL, code verified verbatim).
9. problang.org Chapter 1, RSA introduction (equations verified verbatim).
10. PubMed record PMID 37962526 (author-list verification for TopiCS 2024).
11. DBLP publication list for Kartik Chandra (author-list cross-check).

**Secondary / corroborated (WebFetch-summarized or cross-confirmed across 2+ independent fetches, not verbatim primary read):**
12. Ullman, Baker, Macindoe, Evans, Goodman & Tenenbaum (2009), "Help or Hinder," NeurIPS 22.
13. Ramirez & Geffner (2010), "Probabilistic Plan Recognition Using Off-the-Shelf Classical Planners," AAAI (cross-confirmed against a JAIR 2019 paper restating the same formula).
14. Zhi-Xuan, Mann, Silver, Tenenbaum & Mansinghka (2020), "Online Bayesian Goal Inference for Boundedly-Rational Planning Agents," NeurIPS 33 / arXiv:2006.07532 (abstract + `Plinf.jl` repo dependency structure).
15. Lucas, Griffiths, Xu, Fawcett et al. (2014), "The Child as Econometrician," *PLoS ONE* 9(3):e92160; Jern, Lucas & Kemp (2017), *Cognition* 168:46-64.

**Code repositories inspected directly:**
- `github.com/kach/acting-as-inverse-inverse-planning` (Chandra et al.'s public implementation — confirmed no LLM, confirmed exact value-iteration + softmax + beam-search structure matches the paper's equations).
- `github.com/ztangent/Plinf.jl` (Zhi-Xuan et al.'s implementation — confirmed `SymbolicPlanners`/Gen.jl dependency, no neural component).

---

## HEADLINE

The brain-fidelity gap is real and the fix is buildable glass-box, cheaply — but the task is narrower than the
named literature suggests. Chandra et al. 2024's "inverse inverse planning" (corrected citation: Chandra, Li,
Tenenbaum, Ragan-Kelley) and its Baker/Ullman/Jara-Ettinger ancestry are **entirely non-LLM** (exact value
iteration + enumerative Bayes + beam-search/gradient-descent, confirmed via primary source AND public code —
the only neural component anywhere in 9+ papers is an unrelated actor-critic RL net in a continuous-physics
side-domain), so the glass-box invariant is not at risk. But that whole apparatus is built to solve **goal
inference from an action trajectory** — a different, harder problem than the one DesireDB actually poses,
which is **goal-satisfaction checking against an already-stated goal**, explicitly the EASIER problem in this
literature's own terms (no planner/value-iteration/POMDP-solve required). What we should borrow is narrower:
the multi-attribute weighted-utility REPRESENTATION (Naive Utility Calculus's `U=R-C` / discrete-choice
`U=Σw_i·f_i`) and the field's own validated practice that a small hand-specified candidate set + Bayesian-style
comparison is a faithful minimal instance, not a shortcut. Mapped onto the owned substrate: represent a goal's
utility as a weighted `bundle` of role-`bind`-attribute-predicates (5-6 hand-specified, domain-generic
dimensions), score an outcome by per-attribute `unbind` + `cleanup_with_margin` against
{SATISFIED,VIOLATED,ABSENT} — reusing `goal_achievement.py`'s existing relation/valence channels per-attribute
rather than holistically, and `bind`/`unbind`/`bundle`/`cleanup_with_margin` unchanged. Genuinely novel (not
literature-precedented, capped P=0.50): the graded/normalized partial-satisfaction combination itself — this
literature reports raw scalar reward-cost sums, never a 0-1 satisfaction fraction. Feasibility: **weeks, not
months**, specifically because the reframe removes the need for the apparatus's expensive part (per-hypothesis
planning); the cheapest decisive test is a ~2-4 day exp_dev cell adding the utility-leg as a 4th channel
targeting ONLY the current organ's abstain-to-majority cohort, pre-registered HARD-PASS >=40% cohort recovery
+ no full-bench regression below 0.686 + pairscramble collapse to within 0.05 of majority baseline, HARD-FAIL
<15% recovery or any regression below the 0.620 rule floor or pairscramble non-collapse.

P_deflated=0.45 (blended: literature-grounding of the representation form and small-candidate-set methodology
is high-confidence/primary-source, 0.65-0.85; the FHRR bind/unbind operationalization and the reframe
inference are substrate-native synthesis, un-capped-but-deflated per calibration discipline; the graded
partial-satisfaction combination specifically is novel-synthesis-capped at 0.50).
