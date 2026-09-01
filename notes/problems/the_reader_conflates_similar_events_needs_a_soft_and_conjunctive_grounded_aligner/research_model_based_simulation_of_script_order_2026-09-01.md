# FINER drill: is canonical script order SIMULATED (generative state-conditioned forward model) or STORED/LOOKED-UP?

Research drill for `the_reader_conflates_similar_events_needs_a_soft_and_conjunctive_grounded_aligner`.
Date 2026-09-01. Author: hdi_research (Director), ONLINE-literature confirmation drill dispatched by the SOLVER.
Scope: ONLINE literature only; advisory to the solver; **nothing here is measured on our corpus.** Every "should/would/beats"
is a DESIGN HYPOTHESIS pending the solver's own measurement. **Lit-scan calibration penalty applied throughout** (P
deflated 0.15-0.25; novel-synthesis P capped at 0.50). Glass-box / **no external LLM at inference** framing.

## What this drill INHERITS (measured / pinned; do NOT re-derive)
- Event ALIGNMENT is solved: conjunctive role-filler + discrete particle separates similar events; the aligner is validated.
- Co-occurrence / successor-representation order is SYMMETRIC / direction-blind and caps before/after at ~0.591 (+0.07 over
  shuffle). Pinned mechanism (prior drill): the SR is a generalization device that makes co-occurring states SIMILAR and
  its temporal-context match is symmetric — structurally strong on membership, weak on direction.
- Prior drill Q1 verdict: order is fixed by CAUSAL/GOAL ENABLEMENT (Schank & Abelson 1977); one reusable cognitive-map
  integrator (`transitive_ordering`) is the read-out.
- **Prior drill proposed a STATIC ENABLE-EDGE GRAPH + topological ordering.** The `exp_conceptnet_causal_order_foundation_v1`
  prototype tested a STATIC CAUSAL-KB as a FLAT-ORDER LOOKUP: ConceptNet 0.545 < COOCCUR 0.591; only **1 of 301** questioned
  pairs had a direct ConceptNet BEFORE-edge. **That negative is the launch-point of THIS drill:** it is exactly what a
  lookup-of-stored-order predicts when the stored table under-covers, and it is the first evidence FOR the reframe below.

**Prior-arc overlap:** the two sibling files cover (i) the aligner kernel and (ii) the enablement-EDGE hypothesis. Neither
pins the SIMULATE-vs-LOOKUP distinction, the MUTABLE-WORLD-STATE representation, or the forward-sim-vs-topo-sort choice.
This drill is the first pass on those, and it goes one layer BELOW the prior "enable-edge graph" verdict — because a static
enable-graph is itself a LOOKUP structure, and the question here is whether the brain instead RUNS the graph.

---

## THE HYPOTHESIS UNDER TEST (restated)
The brain does not recover "did X happen before or after Y" by reading a STORED order (pairwise table, scalar magnitude
line, or static causal-KB). It instantiates the activity schema, ROLLS IT FORWARD from an initial state while tracking a
MUTABLE WORLD STATE, and order EMERGES because each event's preconditions become satisfied in sequence (each act's effects
enable the next). Order is a by-product of a model-based rollout over world-state, and it is a PARTIAL order.

**One-line verdict:** **CONFIRMED as the SOURCE/CONSTRUCTOR of canonical order; REFUTED as an EXCLUSIVE runtime claim.**
Simulation is how the brain BUILDS order; but the brain also COMPILES the result into two stored read-outs it uses instead
of re-simulating for familiar material — a stored ordinal "mental timeline" and a model-free chunked routine. The reframe
is right about the mechanism that *generates* direction; it over-reaches if it claims order is *never* retrieved. Crucially
for the build, the discriminating value of "mutable state" over the prior static enable-graph is REAL but NARROW — see Q4.

---

## Q1 — IS ORDER SIMULATED OR LOOKED-UP? (FOR, AGAINST, verdict)

### Evidence FOR generative / model-based simulation (strong, convergent)
1. **Event models are GENERATIVE predictors, by construction.** Event Segmentation Theory (Zacks, Speer, Swallow, Braver &
   Reynolds 2007): working event models contain "characters' goals, spatiotemporal information … and CAUSES of actions" and
   exist *to make predictions of what will occur next*; boundaries are transient spikes in PREDICTION ERROR when the model
   stops predicting. Reynolds, Zacks & Braver (2007) implement this as a recurrent network that PREDICTS the next perceptual
   state. A predict-the-next-state model IS a forward model; order is implicit in its rollout, not stored as a table. **PINNED.**
2. **SEM is literally a generative model of event DYNAMICS.** Franklin, Norman, Ranganath, Zacks & Gershman (2020),
   *Psych. Review*: SEM is "derived from a probabilistic generative model of event dynamics defined over structured symbolic
   scenes"; it "parametrizes the scene dynamics" and does "probabilistic reasoning over this generative model" to infer
   boundaries, learn schemata, and RECONSTRUCT past experience. This is the most direct pinned statement that event
   schemas are RUN (next-scene generation), not indexed. **PINNED.**
3. **Consolidation TRAINS a generative sequence model.** Spens & Burgess (2024), *Nat. Hum. Behav.*: hippocampal replay
   trains neocortical generative models (VAEs in EC/mPFC/ATL); memories are RECONSTRUCTED, share substrate with imagination,
   and show schema-based distortion that INCREASES with consolidation. Follow-on work (bioRxiv 2024, "Consolidation of
   sequential experience into a deep generative network") frames the consolidated store as a generative network for
   "memory, prediction and planning." Consolidation's product is a GENERATOR, not a lookup table. **PINNED.**
4. **Planning = forward rollout over an internal model.** Model-based control "employs an internal model that enables
   simulation of the future state reached by a hypothetical action" (Daw, Niv & Dayan 2005; DLPFC disruption shifts control
   toward model-free — Smittenaar et al. 2013). Hippocampal forward replay/preplay is a rollout toward goals (Pfeiffer &
   Foster 2013); Mattar & Daw (2018) unify replay as prioritized memory access that "propagates" value along trajectories —
   a simulation, not a read. **PINNED** (that the machinery for forward rollout exists and is recruited for prospection).
5. **DIRECT behavioral evidence that temporal-order JUDGMENT uses forward replay.** Macaques "use a forward-replay
   mechanism during judgment of temporal-order between episodes" — a non-linear, time-compressed forward replay at the
   moment of the order decision (eLife 2020, memory replay of video episodes). Human work frames temporal-order decisions
   as forward "mental scanning"/serial replay (PLOS Biol. 2016, temporal signature of memories). **PINNED — this is the
   single strongest FOR: order questions are answered by RUNNING a sequence, not by reading a stored index.**

### Evidence AGAINST (the honest ceiling on the hypothesis)
6. **A stored ordinal "mental timeline" supports fast order judgments — the SYMBOLIC DISTANCE EFFECT.** Order comparisons
   are FASTER for items far apart on the judged dimension (Moyer & Landauer; alphabetic/temporal order judgments), the
   canonical signature of reading a STORED analog magnitude/ordinal code, not of running a simulation. The perceived
   temporal-distance effect "could rely on an over-learned or well-stored representation of temporal orders on the mental
   timeline" (mental-time-travel work, PMC11078804; Wagelmans & van Wassenhove, "mental navigation in time"). **PINNED that
   a stored ordinal read-out exists.** *But note the framing is "mental NAVIGATION / self-projection" — a SCAN over the
   line — and the line is described as a COMPILED product of learning; and a 1-D line is a TOTAL order (see Q2).*
7. **Overlearned routine order is CACHED as a model-free chunk.** Basal-ganglia chunking (Graybiel 1998; Jog et al. 1999):
   overlearned action sequences are "glued into a routine triggered as a whole," with striatal activity bracketing the
   chunk — order runs off automatically, WITHOUT re-simulation, model-free. **PINNED — the sharpest AGAINST:** for a highly
   familiar script, the brain does NOT roll a forward model each time; it fires a cached sequence.
8. **The corpus's scripts are EXACTLY the overlearned kind.** MCScript2 tests everyday routines; humans hit ~97% because
   the canonical order is over-learned and RETRIEVABLE (Bower, Black & Turner 1979: people AGREE on canonical order and on
   scene segmentation; scrambled text is recalled in canonical order). So for our benchmark the human read is plausibly the
   CACHED/STORED route, not a fresh simulation.

### Q1 VERDICT (PINNED vs OUR-INVENTION)
- **PINNED — simulation is the SOURCE.** The brain's canonical event-order machinery is a generative, predictive forward
  model (EST, SEM, consolidation-as-generator, replay-as-rollout), and order-JUDGMENTS recruit forward replay (macaque
  eLife 2020). "Order is a by-product of a state-conditioned rollout" is well supported as the CONSTRUCTOR of direction.
- **PINNED — retrieval is the RUNTIME shortcut for familiar material.** A stored ordinal timeline (distance effect) and a
  model-free chunk (basal ganglia) let the brain ANSWER order without re-simulating once a routine is over-learned.
- **REFUTED (over-reach) — "order is never stored/looked-up."** It is, for familiar scripts. The reconciliation is a
  Dyna-like division of labor: **SIMULATION builds and consolidates the order; the stored line / chunk is the compiled
  read-out; arbitration is by reliability/cost** (Daw 2005). This is not a weakness for us — it says the faithful move can
  be to SIMULATE OFFLINE and FREEZE the result (the FOUNDATION-is-free strategy), or to simulate at inference; both are
  brain-faithful, and our regime (arbitrary before/after pairs, ~13 stories, no overlearning, ~67% non-adjacent pairs)
  is precisely the one where the cached/stored shortcut is UNAVAILABLE, so a constructive route is required.
- **OUR-INVENTION-UNDER-TEST:** that on OUR corpus the operative gap is the constructive route (must be measured, Q4).
- **⚠️ ADVERSARIAL FLAG (load-bearing):** the solver's kept read-out `transitive_ordering` IS a stored ordinal magnitude
  line — i.e. it is mechanism (6), the STORED side. So the architecture is not "simulation INSTEAD OF the line"; it is
  "**simulation GENERATES the directed premises; the line INTEGRATES them.**" The genuinely new thing the hypothesis buys
  over the prior enable-edge drill is the MUTABLE STATE that produces the premises — and whether that buys anything
  measurable over a static enable-graph is the real question (Q4).

---

## Q2 — THE MUTABLE WORLD-STATE, AND WHY A SCALAR TOTAL ORDER STRUCTURALLY CAPS

### How the brain represents the mutable state that gates the next event
- **The situation model's "here-and-now" IS the world-state, and it is UPDATED per event.** Event-indexing model (Zwaan,
  Langston & Graesser 1995; Zwaan & Radvansky 1998, *Psych. Bulletin*): comprehenders track and update FIVE dimensions —
  TIME, SPACE, CAUSATION, ENTITY/OBJECT, and INTENTIONALITY/GOAL — as each event arrives. Situation models are explicitly
  mental SIMULATIONS (Zwaan 2025 review; Psychonomic Bull. Rev. 2016 "situation models, mental simulations"). This is the
  mutable predicate state the hypothesis needs, and it is PINNED that the brain maintains and updates it. **PINNED.**
- **DIRECT evidence the current state GATES accessibility — the doorway/location-updating effect.** "Walking through
  doorways causes forgetting" (Radvansky & Copeland): information from the room just left is less available than
  information in the CURRENT room, because the current event model gates retrieval. This is the neural correlate of "an
  event's EFFECT (you are now in room B / the cup is now empty) changes the state its successor's PRECONDITION checks."
  **PINNED — the strongest evidence that state is mutable and gates what comes next.**
- **Order is read off a CAUSAL NETWORK, and causal connectivity drives recall ORDER.** Trabasso & van den Broek (1985);
  Trabasso, van den Broek & Suh (1989): events with more causal connections are recalled MORE and recalled FIRST, and
  connectivity predicts importance; the narrative's main causal chain is the backbone (see also TiCS 2024, "the causal
  structure and computational value of narratives"). Order tracks the causal/enablement network, not surface co-occurrence.
  **PINNED.**

### Is order a PARTIAL order, and does that explain the scalar-line cap?
- **PINNED — script order is a PARTIAL order.** Bower, Black & Turner (1979): people agree on order for many actions AND
  segment into scenes (hierarchy), but scripts contain optional / unordered actions — agreement is NOT total. Schank &
  Abelson's scenes are chunks whose INTERNAL steps are ordered by enablement while some cross-scene / within-scene steps
  are free. This is the cognitive form of partial-order planning (Sacerdoti NOAH 1975; McAllester & Rosenblitt SNLP 1991;
  Weld 1994): a plan orders ONLY causally-dependent steps and leaves independent steps unordered (least commitment).
- **Why a scalar magnitude-line TOTAL order structurally caps (the mechanistic argument):** a 1-D analog line is a TOTAL
  order — every pair gets an order whether or not one is licensed. It CANNOT represent "A and B are parallel / unordered";
  it must project the partial order onto a line, inventing an order for independent pairs. That invented order is
  unrecoverable from data, so it degrades to noise — the same failure the symmetric SR shows statistically (prior drill).
  **The cap is a REPRESENTATIONAL type-error: fitting a partial order with a total order.** (This is CONSISTENT with,
  and refines, the prior drill's "symmetric SR" account — same disease, described at the representation level.)
- **⚠️ HONESTY — the kept read-out is a total-order line.** `transitive_ordering` is exactly the scalar total order this
  argument indicts. So the design consequence is NOT "replace the line" but "**feed the line ONLY the causally-dependent
  edges and let it ABSTAIN on independent pairs**" — the simulation's job is to SELECT which pairs are orderable and supply
  their direction; the residual parallel pairs must be enumerated as irreducible, not forced onto the line.

### Q2 VERDICT
- **PINNED:** the mutable world-state is the situation model's here-and-now (5 event-indexing dimensions), it is updated
  per event, and the CURRENT state gates the next (doorway effect). Order is a PARTIAL order over states (Bower et al.;
  partial-order planning); a scalar total-order line structurally cannot hold it — the type-error that caps.
- **OUR-INVENTION-UNDER-TEST:** that OUR corpus's residual concentrates on the parallel/independent pairs, and that a coarse
  state (object-availability + location + a few toggles) is enough to gate the DEPENDENT pairs (measured, Q4).

---

## Q3 — GLASS-BOX REPLICATION (no LLM at inference)

### The faithful computational-level model
**A STRIPS/PDDL-style OPERATOR model.** Each event TYPE = (parameters; PRECONDITION set; ADD/DELETE EFFECT set) over a
state of predicates (Fikes & Nilsson 1971; PDDL, McDermott 1998). Order is recovered by FORWARD SIMULATION from an initial
state (apply an operator only when its preconditions hold in the current state; its effects update the state; the next
operator becomes applicable), OR — equivalently for the ordering question — by a TOPOLOGICAL SORT of the operator
dependency graph (edge A→B when A's effect establishes a precondition of B). **PINNED at the computational level.**

**⚠️ THE CENTRAL ADVERSARIAL POINT — forward-sim ≡ topo-sort except in four cases.** For a deterministic, acyclic operator
set where each precondition is established exactly once, a forward simulation and a topological sort of the static
enable-graph produce the SAME ordering. They DIVERGE only when the MUTABLE state genuinely matters:
  (i) a predicate is RE-TOGGLED (open→close→open; wet→dry→wet) so "which establishment" matters;
  (ii) a resource is CONSUMED (a token used up blocks a later step — non-monotonic delete effects);
  (iii) CONDITIONAL/branching preconditions (state-dependent applicability);
  (iv) a NOVEL initial state / counterfactual query.
**If our corpus's residual pairs are NOT of these kinds, then the simulation hypothesis, though more brain-faithful in
principle, buys NOTHING MEASURABLE over the prior drill's cheaper static enable-graph + topo-sort.** Honesty demands
leading with the topo-sort (cheap, deterministic) and reaching for full forward-simulation ONLY if re-toggle/consumption
pairs exist and matter. This is the sharpest place the hypothesis can over-reach operationally — it must be can-failed (Q4c').

### The minimal glass-box state (predicate set)
Directly from ProPara (Dalvi et al. 2018, NAACL — the pinned template): a participant × step GRID tracking each entity's
EXISTENCE and LOCATION, with operations Move / Create / Destroy. The minimal faithful state for everyday-script ordering:
1. **object-availability / existence** `has(agent,X)` / `exists(X)` — get/buy/make before use/consume (the strongest, most
   reliable gate; prior drill's object-availability rule);
2. **location** `at(agent, L)` — enter/arrive before act-at-L; exit after;
3. **a few state-toggles** `open(X)` / `on(X)` / `clean(X)` — open before take-from; turn-on before use; unlock before open.
This is the coarse state the hypothesis names; ProPara's own caveat bounds it: "the causal effects of actions are often
IMPLICIT and need to be inferred" — the recall ceiling for a shallow extractor.

### How the operators are LEARNED from text deterministically (no LLM at inference)
- **LOCM (Cresswell, McCluskey & West 2009/2013)** — induces operator schemas AND the hidden object-lifecycle state
  machines from OBSERVED ACTION SEQUENCES ALONE, "without needing predicates, state trajectory, or initial/final state."
  This is the deterministic, glass-box, non-LLM learner that fits our data best: we HAVE narrated action sequences per
  scenario. **This is the pinned method to try first.**
- **ARMS (Yang, Wu & Jiang 2007, AIJ)** — MAX-SAT over frequent action pairs + occasional intermediate states → pre/effects.
- **ProPara state-tracking** — supplies the state-change skeleton (Move/Create/Destroy over existence+location).

### How a STATIC KB SEEDS operators (the precise fix for the ConceptNet negative)
**This is the load-bearing Q3 result.** The failed prototype QUERIED ConceptNet for a flat order ("is A before B?") and got
1/301 hits. The reframe: **do NOT query the KB for order — use it to POPULATE each operator's PRECONDITION and EFFECT sets,
then let order EMERGE from simulation.** The KB relations ARE precondition/effect predicates:
- **ConceptNet:** `HasPrerequisite` → PRECONDITION; `Causes` / `HasFirstSubevent` / `HasLastSubevent` → EFFECT / ordering.
- **ATOMIC (Sap et al. 2019; ATOMIC-2020):** `xNeed` is literally a PRECONDITION ("for X to give gifts, X must first buy
  the presents"); `xEffect`/`oEffect` are EFFECTS. This is exactly the operator schema, pre-labeled.
- **PRECEDENT: NaRuto (arXiv 2307.10247, "Automated Action Model Acquisition from Narrative Texts")** builds PDDL operators
  from narrative by SRL + dependency rules (symbolic event extraction) then assigns pre/effects by ATOMIC relation:
  *"Phrases that have the xNeed relation with the event become candidate preconditions, and the others candidate effects."*
  **CAVEAT (invariant):** NaRuto's pre/effect GENERATION uses COMET (a fine-tuned LM) — NOT admissible at inference. The
  clean reconciliation with our no-LLM invariant AND the FOUNDATION-is-free rule (a static offline-built asset is
  admissible): run the KB/COMET seeding OFFLINE, FREEZE a static operator library (event-type → pre/effect predicates),
  and at inference do ONLY the deterministic forward-sim/topo-sort over that frozen library. No LM in the loop at read time.

### Q3 VERDICT
- **PINNED:** the faithful model is a STRIPS/PDDL operator set over a coarse existence+location+toggle predicate state;
  order = forward simulation or topo-sort of the operator dependency graph; operators are learnable deterministically from
  action sequences (LOCM/ARMS/ProPara); the static KB SEEDS pre/effects (ConceptNet `HasPrerequisite`, ATOMIC `xNeed`/
  `xEffect`), it is NOT a flat-order lookup.
- **OUR-INVENTION-UNDER-TEST (build):** the exact predicate set; whether LOCM-induced operators or KB-seeded operators (or
  both) give higher coverage on our scenarios; whether forward-sim beats topo-sort (the mutable-state test); the offline
  freezing of the operator library.
- **⚠️ the diagnosis of the ConceptNet negative is itself a design hypothesis:** "KB-as-operator-seed beats KB-as-flat-lookup"
  must be measured — it is plausible AND it could still under-cover (the seeds may miss the same specific event-pairs).

---

## Q4 — FALSIFIABLE PREDICTIONS ON OUR CORPUS + THE CHEAPEST DECISIVE TEST FOR EACH

**(a) Answerable pairs = causally state-DEPENDENT; irreducible residual = state-INDEPENDENT / parallel.**
- Cheapest decisive test: tag each eval before/after pair INDEPENDENTLY of the ordering signal — does a shared-entity state
  dependency exist between the two events (one produces/consumes an object the other uses; one enters/exits a location the
  other acts in; one toggles a state the other checks)? Then check accuracy CONCENTRATES on state-dependent pairs and the
  RESIDUAL concentrates on independent pairs. **Can-fail:** if accuracy is FLAT across the tag, the hypothesis is dead.
- ⚠️ **This test does NOT discriminate simulation from the prior static enable-graph** — both make this identical split.
  It confirms the enablement FRAMING, not the SIMULATION-specific claim. Necessary but not sufficient for THIS drill.

**(b) A forward-simulation / operator order beats the co-occurrence 0.591 ceiling where a total-order magnitude line cannot.**
- Cheapest decisive test: run the KB-seeded operator order (topo-sort first — cheapest) on the state-gated subset vs the
  0.591 co-occurrence floor AND a shuffled-order twin; report CI half-width + null p95 beside the margin. **Can-fail:** if
  it does not clear 0.591 CI-separated on the state-gated subset, the operator premise is not better-conditioned than
  co-occurrence on our data (likely a coverage failure — report pair-hit rate, per the forward-problem proposal).

**(c) Tracking even a COARSE world state recovers order on the state-gated subset.**
- Cheapest decisive test: STATE-ABLATION. Three arms on the SAME pairs — full state-tracking sim / directed-edge-only (no
  state) / co-occurrence. The state-tracking arm must WIN on the state-gated subset. **Can-fail:** if no-state ≈ full-state,
  the state is idle.

**(c′) THE DISCRIMINATING TEST THIS DRILL ADDS — does MUTABLE state (rollout) beat a STATIC enable-graph (topo-sort)?**
- This is the ONLY test that isolates the SIMULATION hypothesis from the prior enable-edge drill. First ENUMERATE the
  re-toggle / resource-consumption pairs in the corpus (predicate toggled >1×, or a token consumed). Then compare forward
  simulation vs static topo-sort ON THOSE PAIRS. **Can-fail / honest prior:** if that subset is EMPTY or tiny (very likely
  for short everyday-script narratives), then forward-sim ≡ topo-sort here, and the faithful-AND-cheap move is the static
  topo-sort — the mutable-state rollout is more brain-faithful but MEASURABLY IDLE on this corpus. Reporting that honestly
  is a full PASS (a located negative on the simulation-specific claim), and it prevents over-investing in a rollout engine.

---

## PINNED vs OUR-INVENTION (summary)

| Claim | Status |
|---|---|
| Event models are generative predictors; boundaries = prediction error | PINNED (EST, Zacks/Reynolds 2007) |
| Event schemas are RUN (next-scene generation), not indexed | PINNED (SEM, Franklin 2020) |
| Consolidation trains a GENERATIVE sequence model (not a lookup table) | PINNED (Spens & Burgess 2024) |
| Planning/order-judgment recruit forward ROLLOUT / replay | PINNED (Daw 2005; Mattar & Daw 2018; macaque eLife 2020) |
| Simulation is the SOURCE of canonical order | PINNED |
| Order is NEVER stored/looked-up | REFUTED — stored ordinal timeline (distance effect) + model-free chunk (basal ganglia) |
| Runtime for FAMILIAR scripts is a compiled read-out, not fresh sim | PINNED (Graybiel chunking; mental-timeline distance effect) |
| Mutable world-state = situation-model here-and-now; current state gates next | PINNED (event-indexing; doorway effect) |
| Order is a PARTIAL order; scalar total-order line structurally caps | PINNED (Bower 1979; partial-order planning) — refines prior "symmetric SR" |
| Faithful model = STRIPS/PDDL operators; order via forward-sim OR topo-sort | PINNED (Fikes&Nilsson; PDDL) |
| Operators learnable deterministically from action sequences (no LLM) | PINNED (LOCM; ARMS; ProPara) |
| Static KB SEEDS pre/effects (`HasPrerequisite`/`xNeed`→pre; `Causes`/`xEffect`→effect), not a flat-order lookup | PINNED as method (ATOMIC; NaRuto) |
| "KB-as-operator-seed beats KB-as-flat-lookup on OUR pairs" | OUR-INVENTION-UNDER-TEST |
| Answerable = state-dependent; residual = parallel | OUR-INVENTION-UNDER-TEST (does NOT isolate simulation) |
| Forward-sim (mutable state) beats static topo-sort on OUR corpus | OUR-INVENTION-UNDER-TEST — **honest prior: likely IDLE on short scripts** |

## Confidence (calibrated, deflated)
- P(enablement/operator FRAMING is the right axis — answerable pairs are state-dependent, residual is parallel): **~0.60**
  (well-pinned mechanism; the split is measurable and the prior drill already leans this way).
- P(a KB-seeded operator order, topo-sorted, beats the 0.591 co-occurrence floor CI-sep on OUR corpus): **~0.30-0.40**
  (novel synthesis capped at 0.50, then deflated hard for the SAME coverage/granularity risk that sank the flat-lookup
  prototype — seeding fixes the LOOKUP error but not necessarily the COVERAGE of specific event-pairs).
- P(MUTABLE-STATE forward simulation beats a STATIC topo-sort measurably on OUR corpus): **~0.15-0.25** (short everyday
  narratives rarely re-toggle a predicate or consume a resource in a query-relevant way; most gains, if any, come from the
  directed edges, which the cheaper topo-sort already captures). **Build the cheap version first; can-fail the expensive one.**

## Key citations
- Zacks, Speer, Swallow, Braver & Reynolds (2007). Event perception: a mind-brain perspective. *Psych. Bulletin*. / Reynolds, Zacks & Braver (2007). A computational model of event segmentation from perceptual prediction. *Cognitive Science*.
- Franklin, Norman, Ranganath, Zacks & Gershman (2020). Structured Event Memory: a neuro-symbolic model of event cognition. *Psych. Review*. (gershmanlab.com/pubs/Franklin20.pdf)
- Spens & Burgess (2024). A generative model of memory construction and consolidation. *Nat. Hum. Behav.* / bioRxiv 2024, consolidation of sequential experience into a deep generative network.
- Daw, Niv & Dayan (2005). Uncertainty-based competition between prefrontal and dorsolateral striatal systems. *Nat. Neurosci.* / Smittenaar et al. (2013), DLPFC disruption → model-free.
- Pfeiffer & Foster (2013). Hippocampal place-cell sequences depict future paths. *Nature*. / Mattar & Daw (2018). Prioritized memory access explains planning and hippocampal replay. *Nat. Neurosci.*
- (2020) Behavioral evidence for memory replay of video episodes in the macaque — forward-replay during temporal-order judgment. *eLife*. / (2016) The temporal signature of memories. *PLOS Biology*.
- Symbolic distance effect / mental timeline: Moyer & Landauer; Hamilton & Sanford (1978) alphabetic order; Wagelmans & van Wassenhove (mental navigation in time); PMC11078804 (perceived temporal distance, MTT).
- Graybiel (1998). The basal ganglia and chunking of action repertoires. / Jog et al. (1999) *Science*; Graybiel (2008) *Annu. Rev. Neurosci.*
- Zwaan, Langston & Graesser (1995); Zwaan & Radvansky (1998). Situation models in language comprehension and memory. *Psych. Bulletin*. / Radvansky & Copeland (doorway/location-updating).
- Trabasso & van den Broek (1985); Trabasso, van den Broek & Suh (1989). Causal network model. / TiCS (2024) The causal structure and computational value of narratives.
- Bower, Black & Turner (1979). Scripts in memory for text. *Cognitive Psychology*.
- Fikes & Nilsson (1971) STRIPS; McDermott (1998) PDDL; Sacerdoti (1975) NOAH; McAllester & Rosenblitt (1991) SNLP; Weld (1994) least-commitment planning.
- Dalvi, Huang, Tandon, Yih & Clark (2018). Tracking State Changes in Procedural Text (ProPara). NAACL.
- Cresswell, McCluskey & West (2009/2013). Acquiring planning domain models using LOCM. / Yang, Wu & Jiang (2007). Learning action models from plan examples using weighted MAX-SAT (ARMS). *AIJ*.
- Sap et al. (2019). ATOMIC: an atlas of machine commonsense for if-then reasoning. *AAAI*. / Hwang et al. (2021) (COMET-)ATOMIC-2020. / Feng et al. (2023) NaRuto: automated action model acquisition from narrative texts. arXiv 2307.10247.
- Speer, Chin & Havasi (2017). ConceptNet 5.5. *AAAI*.

---

## TLDR (plain English)
We asked whether the brain figures out "which step comes first" in a routine by looking up a stored order, or by mentally
RUNNING the routine forward and watching the steps fall into place (you can't pour until you've got the mug; you can't get
out until you've got in). The neuroscience strongly supports the RUNNING-IT-FORWARD picture as the way the order is
originally FIGURED OUT: the brain builds little predictive models of what happens next, trains them up during sleep/replay,
and — shown directly in animals — literally replays a sequence forward when asked which of two things came first. BUT the
hypothesis over-reaches if it says order is NEVER just looked up: once a routine is very familiar, the brain files the
order away and reads it off fast (that's why "far-apart" order questions are answered quicker), or runs it as a single
automatic habit without thinking. So the honest picture is: RUNNING-IT-FORWARD is how the order gets built; a stored
short-cut is how a FAMILIAR routine gets answered. Our reader is in the hard case (a dozen short stories, questions about
step-pairs that were never adjacent), so it needs the constructive route — either run the model at read-time, or, better,
run it OFFLINE once and freeze the answer (allowed: an offline-built reference asset is fine; a live outside AI is not).

The concrete build this points to: represent each kind of step as a little "recipe card" — what must be TRUE before it can
happen (preconditions) and what it makes true afterward (effects) — over a tiny world-state (do you have the object, where
are you, is it open/on). Get those recipe cards deterministically from the stories themselves (a classic method called LOCM
does this from action sequences alone, no AI) and/or by re-using our on-disk commonsense reference the RIGHT way: its
"needs" links fill in preconditions and its "results/causes" links fill in effects — NOT as a flat "is A before B" lookup,
which is exactly why our earlier ConceptNet try failed (it hit only 1 of 301 pairs). Then the order simply falls out of the
recipe cards, and our existing ordering read-out integrates it. Two honest cautions: (1) with only a dozen short stories
the recipe cards may miss the same specific step-pairs the flat lookup missed — coverage, not cleverness, is the risk; and
(2) the fancy "mutable world-state simulation" only beats the cheap "arrow-chart + sort" when a routine UNDOES and REDOES
something or USES SOMETHING UP mid-way — which short everyday stories rarely do — so build the cheap version first and only
reach for the simulator if those cases actually show up.

## QUESTIONS
None for the owner. Every "beats/should" above is flagged as a design hypothesis for the solver to measure; no decision here
needs an owner call. (One internal steer for the solver, not a question: this drill's own novelty — mutable-state simulation
over a static enable-graph — is the LEAST likely piece to pay off on this corpus; lead with the cheap topo-sort.)

## NEXT STEPS (for the solver — design hypotheses to MEASURE, not adopt)
1. Build the OPERATOR library: event-type → {precondition predicates, add/delete effect predicates} over a coarse state
   (existence/`has`, `at`-location, a few toggles: open/on/clean). Seed pre/effects TWO ways and compare coverage: (i)
   deterministic LOCM-style induction from the narrated action sequences (no LLM), and (ii) static-KB seeding — ConceptNet
   `HasPrerequisite`→precondition, `Causes`/`HasFirst/LastSubevent`→effect; ATOMIC `xNeed`→precondition, `xEffect`→effect.
   If you use COMET/ATOMIC generation, do it OFFLINE and FREEZE the library (no LM at inference — the invariant + the
   FOUNDATION-is-free rule).
2. Recover order by TOPOLOGICAL SORT of the operator dependency graph FIRST (cheapest, deterministic), feeding the directed
   premises into the EXISTING `transitive_ordering` read-out (one-variable; premise type is the only change).
3. Can-fail vs BOTH floors + the 0.591 co-occurrence ceiling + the shuffled-order twin; report CI half-width + null p95.
4. Tag each eval pair (independently of the ordering signal) as state-dependent vs parallel; check accuracy concentrates on
   dependent pairs and the residual on parallel pairs; ENUMERATE the parallel residual as irreducible rather than forcing it
   onto the total-order line (make the read-out ABSTAIN on independent pairs).
5. STATE-ABLATION (c): full-state vs no-state vs co-occurrence on the same pairs — the state must not be idle.
6. THE DISCRIMINATING TEST (c′): enumerate re-toggle / resource-consumption pairs; only if that subset is non-trivial,
   build the forward SIMULATION and compare it to the topo-sort ON THOSE PAIRS. If the subset is empty/tiny, report that
   mutable-state simulation is brain-faithful-but-idle here and STOP at the topo-sort — a located negative on the
   simulation-specific claim is a full PASS, and it prevents over-building a rollout engine.
7. If coverage (pair-hit rate) is the wall — as the ConceptNet flat-lookup prototype showed — that is a FOUNDATION gap to
   BUILD across (grounded/paraphrase-matched KB lookup to nearest concept; finer-grained ATOMIC; multi-source consolidated
   script KB), NOT a ceiling. Report the pair-hit rate as the headline coverage number before any "route exhausted."
