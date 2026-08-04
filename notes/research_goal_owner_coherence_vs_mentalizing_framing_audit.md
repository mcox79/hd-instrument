# Framing audit: is goal-owner attribution a coherence-selection problem, or mentalizing? (targeted, no-cell drill)

Filed by: research sub-agent, 2026-08-04. Design/analysis only — no experiment dispatched.
Trigger: Director about to run a mechanism-capacity probe (does `decode_coherence_margins`
discriminate a goal-owner once the foil's error is embedded as a role-CONFLICT). USER asked
for a biology-first stress-test of the WHOLE reasoning chain before that cell ships.

## KB-check (mandatory)

`substrate_query.sh` for "theory of mind mentalizing goal attribution" returned nothing above
the 0.30 dup-threshold (top hit 0.3428, `theory_of_mind_sally_anne_nes...` snippet — itself a
pointer to the prior audit re-surfaced below, not a duplicate of this analysis). Direct disk
search found the load-bearing prior art directly: `experiments/exp_theory_of_mind_sally_anne_
nested_hrr_v1.py` + `notes/research_drill_brain_fidelity_audit_event_relation_inference_
phase1_2026-08-03.md`. This audit builds on, and materially corrects, that prior drill's
citations rather than re-deriving them (Mar 2011 mentalizing ALE meta-analysis; Zwaan &
Radvansky 1998 five-index situation model; Trabasso & van den Broek 1985 causal-network;
Zacks & Swallow 2007 event segmentation; Ferstl/von Cramon coherence-vs-mentalizing
dissociation — all previously verified, cited there, not re-checked here).

## HEADLINE

**The reasoning chain holds at 4 of 5 levels; Level 1 is a COMPOSITE, not a clean either/or,
and the composite resolution changes what "the probe" is allowed to claim.** For THIS SPECIFIC
item (Henry/cherries: goal is EXPLICITLY STATED in text, no divergent belief-state, single
shared world), goal-owner attribution is a same-entity relational/situation-model BINDING
problem (Zwaan's intentionality index, tracked by the same hippocampal/DMN system as coref) —
the coherence-selector family is category-CORRECT for it, and the pending probe is the right
next step, WITH a scope correction (below) so a pass is not mis-sold as "solves goal
attribution" generally. Separately, and this is the most important disk-finding of this
audit: **the substrate ALREADY OWNS a disk-verified HARD_PASS mentalizing organ**
(`theory_of_mind_sally_anne_nested_hrr_v1`, per-agent multi-bank + refuse-gate, Q2 false-belief
0.806 vs 0.138 no-partition baseline, gap 0.668, oracle 1.0, 5 seeds) that is sitting UNWIRED
to the reading pipeline. `notes/brain_component_functional_map_2026-08-04.md` row "ToM /
mentalizing" says "GAP (thin) — no wired organ," which undersells this: the organ is not a
gap, it is an ISLANDED capability. The moment goal-attribution work moves from
stated-and-single-shared-world to UNSTATED/abductive or divergent-epistemic-access (the
general mentalizing case), the correct move is WIRE that organ (per "wire don't island" +
"reuse organs don't island"), not extend `decode_coherence_margins`. Do that reframe NOW in
the note so the Director does not later re-derive it as a "new" gap.

## Level-by-level verdicts

### Level 1 — FRAMING (highest value): binding-selection or mentalizing?

**Verdict: COMPOSITE, resolved by a concrete criterion, not a coin-flip.**

Biology first. Two dissociable systems both touch "whose goal was X":
- **Situation-model relational binding** (hippocampal relational memory + posterior-medial/DMN
  event model; Zwaan & Radvansky 1998's five indices — space, time, causation,
  **intentionality/goal**, protagonist — are tracked CONTINUOUSLY and CONCURRENTLY as ONE
  event-model update, the same system that also does causal-chain and entity-identity
  tracking). This is the SAME family as coref (Eichenbaum: hippocampus does arbitrary
  item-in-context relational binding generally, entity-identity is one instance, goal-role is
  another).
- **Mentalizing** (mPFC/dmPFC, bilateral TPJ, precuneus/PCC, temporal poles; Mar 2011 ALE
  meta-analysis). This is recruited specifically when the goal/intention is UNSTATED and must
  be inferred abductively from observed action (best-explanation inference), and — per the
  false-belief/Sally-Anne literature already validated on this substrate — when the task
  requires tracking WHOSE epistemic access differs from the true world state (a
  PARTITIONED, agent-indexed representation). Ferstl/von Cramon's coherence-vs-mentalizing
  dissociation is contested in degree but the two are separable in at least some studies —
  the prior audit already flagged this as "not identical, layered."

The discriminating question is not "which ONE mechanism does goal-attribution" — it's
**"is the goal stated, and is there a divergence between what's true and what some agent
believes/wants that a wrong reading would need to track separately?"** If NO to both (goal is
explicit, single shared world, e.g. "Henry wanted the cherries... [later] Henry got in
trouble"), the task reduces to: does the LATER event bind back to the SAME entity-cluster that
HAD the goal — this is relational/entity-persistence binding, not mentalizing, and the
hippocampal/DMN situation-model machinery (which the coherence-selector arc targets) is the
correct organ family. If YES to either (goal must be INFERRED from action, or two agents have
DIFFERENT beliefs/wants about the same object), the task is mentalizing and the correct organ
is the ALREADY-BUILT Sally-Anne-class primitive (per-agent bank partition + refuse-gate),
adapted per the prior audit's Correction 1 (partition by narrative protagonist, not literal
dialogue-participant).

**Disk-check on the actual pending item:** `experiments/exp_coherence_fair_load_matched_
retest_v1.py` ARM2 (`_arm2_go`, lines 271-300) uses the ONE clean real g5g6 item,
`g5v_henry_wilkins_cherries` — goal is stated in-text (Henry's forbidden-cherry episode),
owner=Henry (cluster '1', 3 real prior mentions) vs foil=old_gentleman (cluster '0'), and the
test is whether the OUTCOME event correctly re-binds to Henry rather than the foil. No belief
divergence, no unstated/abductive inference, single shared world. **This item sits on the
binding-selection side of the split, not the mentalizing side.** So: the coherence-selector
family is NOT category-wrong for this probe. But — this is a narrow instance, and the
"goal-outcome = one of the 3 unified coherence-selector instances" framing in the backup
(director doc) is accurate ONLY for stated/single-world goal items; it does not generalize to
goal-attribution broadly the moment unstated intent or belief-divergence enters (which most
narrative goal content eventually does — Zwaan's intentionality index and Mar's mentalizing
literature both exist because real narratives constantly require exactly that). **Scope
correction for the pre-reg: label the upcoming cell's claim as "stated/single-world goal-owner
binding," not "goal-owner attribution" unqualified — this prevents a future over-read the same
way the aggregate-vs-load-matched confound was caught this session.**

### Level 2 — COHERENCE SIGNAL: cleanliness proxy vs constraint-satisfaction

**Verdict: proxy, already correctly flagged, and the specific rescue is a faithful (if
discrete) instance of a validated mechanism class — not a smuggle.**

Kintsch construction-integration and CA3 pattern-completion/settling both score coherence as
MUTUAL reinforcement across a connectivity structure (Kintsch: a(t+1) = norm(C·a(t)), settled
to a fixed point; the well-connected node wins). `decode_coherence_margins` is a single-shot
(cluster,slot)->role decode margin — no iteration, no pairwise connectivity matrix among
established propositions about an entity. This is a genuine SHAPE gap versus the brain
mechanism, and the session's own biology-convergence note (`research_coherence_over_recency_
selection_biology_2026-08-04.md`, cited in the director backup) already reached the same
conclusion and correctly demoted true iterative settling to a stretch goal rather than hiding
the gap. That is the right call to have made — flag-and-defer, not flag-and-ignore.

Is embedding the foil's error as a role-CONFLICT ("foil already holds another role, so binding
the outcome to it collides two role-bindings on the same cluster slot") a legitimate
constraint-satisfaction test, or a hack that smuggles a constraint into a metric that
structurally isn't one? **It is legitimate, because it reuses the SAME mechanism class that
already made coref's signal real: the fair-test finding this session (commit 46662d47b)
established that decode-margin sensitivity comes from register-LOAD/CROSSTALK when an entity
cluster absorbs conflicting content (coref: wrong clustering over-merges two people into one
busy register -> lower cleanliness). A role-conflict-embedded foil creates the EXACT SAME
kind of crosstalk — two incompatible role-bindings sharing one cluster slot — so the rescue is
not inventing a new signal, it is testing whether the validated crosstalk-collision mechanism
GENERALIZES from identity-merge collisions to role-conflict collisions.** That is a fair,
falsifiable, non-arbitrary hypothesis. It is still a ONE-SHOT approximation of Kintsch settling
(a discrete instance, not the iterative fixed-point), which is fine as a shippable stepping
stone as long as it is not sold as "we built the settling organ" — it tests one predicted
CONSEQUENCE of settling-style coherence (conflicting bindings interfere), not the full
mechanism.

### Level 3 — IDENTITY vs ROLE-CONTENT: real brain distinction?

**Verdict: yes, well-grounded, and our finding is brain-consistent, not a substrate quirk.**
Hippocampal CA3 pattern-completion / recollection binds ITEM identity (entity persistence
across mentions — coref's actual operation) via a documented, separable mechanism from
relational/thematic ROLE assignment, which per Eichenbaum's relational-memory framework and
Halford's relational-complexity work requires additional prefrontal-parietal control to bind
MULTIPLE relations correctly (who-did-what-to-whom is a higher relational-complexity operation
than who-is-this). The double dissociation the prior audit cited (recollection vs familiarity,
case NB) plus this session's own fair-test result (identity/cleanliness signal real and
load-matched-robust; role-content signal exactly 0.0 at matched load) triangulate cleanly: two
different operations, the substrate currently only has the identity one wired into
`decode_coherence_margins`, and that is a real, not spurious, capability boundary.

### Level 4 — THE RESCUE: brain-faithful?

**Verdict: partially — faithful AS A DISCRETE CROSSTALK TEST, not as a role-binding-detection
mechanism in general.** The brain would very likely ALSO need something closer to Level 1's
mentalizing/relational-control layer to catch role-binding errors that do NOT happen to
collide two bindings on the same physical slot (e.g., a wrong owner in a sparsely-loaded
register with no other role held by the foil — no crosstalk to detect, and the brain's PFC
relational-control system, not raw pattern-completion crosstalk, is what would catch that).
So: this rescue will only ever detect a SUBSET of role-binding errors — specifically the
subset where the foil is already "busy" elsewhere in the register. That subset happens to
match the one available real item (Henry/old_gentleman), which is a green flag for
testability but a caveat for generality — a pass here says "crosstalk-based role-conflict
detection works when the foil is independently busy," not "role-content coherence is solved."

### Level 5 — THE PROBE: right next step?

**Verdict: YES, run it, with three design corrections (not a reframe-and-abort):**

1. **Scope the claim.** Pre-register the HARD-PASS criterion as "stated/single-world
   role-conflict-embedded goal-owner discrimination," explicitly NOT as general goal-owner
   attribution or mentalizing. Carry forward the same load-matching discipline that rescued
   coref this session (assert `owner_load == foil_load` pre-conflict-embedding, so a pass
   can't be re-explained as a raw load asymmetry the way the first aggregate result was).
2. **Pre-register a HARD-FAIL band that reuses the fair-test's exact signature**: if
   margin-delta on the role-conflict-embedded item is EXACTLY 0.0 or moves only under a
   load-direction flip (the same artifact-signature already characterized in
   `exp_coherence_fair_load_matched_retest_v1`), that is HARD-FAIL, not "inconclusive N=1" —
   the mechanism (signature) is already known well enough from this session's own prior work
   to call it decisively even at N=1.
3. **File the ToM-organ reframe as a standing note now, not as a future re-discovery.** Add
   an explicit line to whatever tracking doc governs the coherence-selector arc: "the moment
   goal-attribution needs UNSTATED/abductive inference or belief-divergence, route to
   `theory_of_mind_sally_anne_nested_hrr_v1` (adapt per Correction 1 of the 2026-08-03 audit:
   partition by narrative protagonist, write goal-state into that agent's bank, decode via the
   same refuse-gate), do NOT extend `decode_coherence_margins` further for that case."
   This is a **documentation-correction deliverable of this audit**, independent of the probe's
   outcome: `notes/brain_component_functional_map_2026-08-04.md`'s ToM row should be updated
   from "GAP (thin) — no wired organ" to "ISLANDED (HARD_PASS organ exists, unwired) — wire
   target: goal-owner inference under unstated/divergent-belief conditions."

## Cheap decisive test (already the one about to ship — endorsed with corrections above)

Ship the pending probe AS-IS mechanically (route_passage/decode_coherence_margins on the
role-conflict-embedded Henry/old_gentleman item, load-matched pre-conflict), but attach the
scope label from Level 5 correction 1 to its pre-reg, and treat the HARD-FAIL signature from
correction 2 as decisive even at N=1 (this session already has the ground-truth artifact
signature to check against — no need to wait for more data to call a 0.0-exact result
HARD-FAIL).

## Falsifiable predictions

- **HARD-PASS** (crosstalk-generalization confirmed): true-owner margin-delta with
  role-conflict-embedded foil is positive and load-matching-robust (survives a load-direction
  flip check analogous to the fair test), AND shuffled/role-seq-reversed control does not
  reproduce the effect. Interpretation: crosstalk-based coherence generalizes from
  identity-merge to role-conflict — extend `decode_coherence_margins`'s use to
  crosstalk-inducible role errors specifically (still requires per-item load-collision
  engineering, not a general role-content detector).
- **HARD-FAIL** (crosstalk does not generalize): margin-delta is exactly 0.0, OR flips sign
  under a load-direction reversal the way the raw aggregate result did in
  `exp_coherence_aggregate_discriminates_goal_outcome_v1` (commit 925897d74). Interpretation:
  role-CONTENT coherence needs the settling/constraint-satisfaction mechanism (Level 2 stretch
  goal) or the mentalizing/PFC-relational-control organ (Level 1/4), not a one-shot
  cleanliness read under any framing — de-prioritize further one-shot rescues of
  `decode_coherence_margins` for role-content and move directly to (a) the settling-organ
  build or (b) wiring the Sally-Anne ToM organ for the cases that actually need it.
- **MIDDLE** (fires on this one item, mechanism-class unclear at N=1): treat as
  hypothesis-generating only; do not promote to "coherence handles role-content" until a
  second independently-collidable real item is sourced (ties to the standing data-availability
  blocker already logged in the director backup).

## Cross-thread synthesis with prior entries

- Confirms and sharpens `notes/research_relational_backward_reach_coherence_selector.md` +
  `notes/research_coherence_based_binding_selector_build_spec_2026-08-04.md`: SELECT
  (`decide_keep_or_revert`) remains sound and anti-recency by construction; SCORE is where the
  instance-specific work lives, and this audit adds a THIRD instance-specific fork the prior
  synthesis missed — some goal-attribution items are actually mentalizing-class and route
  OFF the coherence-selector arc entirely, not onto a to-be-built SCORE.
- Corrects `notes/brain_component_functional_map_2026-08-04.md`'s ToM row (see Level 5,
  correction 3) — the map currently reads as "nothing exists," but a HARD_PASS organ exists
  and is simply unwired. This is a "wire don't island" miss, not a capability gap, and should
  be fixed in the map directly.
- Agrees with, and extends, the prior audit's Deviation 1
  (`research_drill_brain_fidelity_audit_event_relation_inference_phase1_2026-08-03.md`):
  that audit targeted a DIFFERENT cell (event-relation-inference Phase 1's prototype-overlap
  readout) but reached the identical structural conclusion — unstated/abductive goal content
  needs the Sally-Anne-class organ, not a similarity/margin proxy. Two independent audits of
  two different cells converging on the same fix is a meaningful cross-check, not a
  coincidence — it is the same underlying brain fact (mentalizing is a partially separate
  computation) surfacing wherever goal-inference is attempted with a pooled/proxy readout.

## Substrate-product implications

A user-facing reading substrate that can track "Henry wanted the cherries, then got caught"
correctly (binding-selection case) will still confidently mis-attribute intent whenever a
story requires inferring an UNSTATED want or tracking two characters' differing beliefs
(mentalizing case) UNLESS the Sally-Anne organ gets wired into the reading pipeline for that
subclass. Shipping only the binding-selection fix would look like a narrow, real win
(handles explicit goal/outcome persistence) but would silently fail on the more narratively
common case (implied motive, dramatic irony, deception) — exactly the cases that make
narrative comprehension feel intelligent. The wire-the-existing-organ path is CHEAPER than it
looks (no new build, it is disk-verified HARD_PASS already) and should be sequenced as a
near-term product win independent of how the pending probe lands.

## Citations (verified count: 0 new external; 7 reused-verified from prior drills)

Reused, previously verified on disk in cited prior notes (not re-fetched this cycle): Mar 2011
mentalizing ALE meta-analysis; Zwaan & Radvansky 1998 situation-model five-index model;
Trabasso & van den Broek 1985 causal-network story grammar; Zacks & Swallow 2007 event
segmentation; Ferstl & von Cramon coherence-vs-mentalizing dissociation; Eichenbaum relational
memory theory (hippocampal item-in-context binding); Halford relational-complexity framework.
Disk-verified numeric claims this cycle (all read directly, not recalled): `data/
exp_theory_of_mind_sally_anne_nested_hrr_v1/metrics.json` (HARD_PASS, Q2_full=0.806,
Q2_base=0.138, gap=0.668, oracle_avg=1.0, n_seeds=5); `data/exp_coherence_fair_load_matched_
retest_v1/metrics.json` (arm1_net_auto=2.0 survives, arm2 N=1 directional-only, positive
control reproduces 1.0); `experiments/exp_coherence_fair_load_matched_retest_v1.py` lines
271-300 (Henry/old_gentleman item construction, load-matched, real g5g6 passage);
`hdlab/self_improving_loop.py` lines 56-89 (decode_coherence_margins is a
(cluster,slot)->role decode with no gold-role comparison, confirming the "cleanliness not
content" characterization); `notes/brain_component_functional_map_2026-08-04.md` line 133
(ToM row text quoted verbatim above).

## P_deflated and biggest risk

P_deflated = 0.40 (novel-synthesis component — the Level-1 composite-resolution criterion and
the crosstalk-generalization hypothesis in Level 2/4 are this audit's own synthesis, not
directly lit-verified for this exact substrate; capped per lit-scan calibration discipline,
deflated an additional notch because the decisive real-data test remains N=1). The disk-facts
(HARD_PASS ToM organ exists+unwired; decode_coherence_margins is gold-free
identity-cleanliness only; Henry item is stated/single-world) are P=0.95+ (directly read off
disk this cycle).

**Biggest risk:** the N=1 real-item constraint means even a clean HARD-PASS on the pending
probe is a single-item existence proof of crosstalk-generalization, not a general
role-content-coherence capability — the same over-read risk this session already caught twice
(aggregate-grain confound; role_seq-reversal control mismatch). The Level-5 corrections above
are specifically designed to prevent a third instance of that failure mode on this probe's
result.
