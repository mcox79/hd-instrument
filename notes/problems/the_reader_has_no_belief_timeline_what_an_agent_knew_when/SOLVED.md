---
problem: the_reader_has_no_belief_timeline_what_an_agent_knew_when
status: SOLVED
bar: "PASSES only with ALL of: 1. A per-agent BELIEF TIMELINE (built in experiments/): each agent's belief about a tracked fact (e.g. an object's location) over reading-time, updated ONLY on events the agent OBSERVED (via belief_partition's observation cue), ordered by the temporal_order_register; a false belief = last-observed-value != current-true-value. Copy the computation; SWEEP the representation + threshold. NO external LLM. 2. Answers false-belief-over-time queries CI-separated over the timeline-agnostic floor -- a false-belief population: 'where does A think X is?' / 'does A hold a false belief here?'; the floor = a timeline-agnostic CURRENT-belief tracker (or last-mention) recomputed on the same population. The info-free twin (shuffled observation/event order) LOSES CI-separated; report CI half-width + null p95. A POSITIVE control the metric can move (a scene where A's belief is stale because A left BEFORE the change, which the current-belief floor misses). 3. Isolates the TIME composition -- hold the belief-partition/observation cue fixed and show the lift is the TIMELINE (order-aware) part, not a better observation cue (an ablation to the timeline-agnostic tracker with the SAME cue). 4. One-screen summary. A rigorous NEGATIVE is a FULL PASS."
result: "Belief-question accuracy (belief 'where does A think X is' + false_belief 'does A hold a false belief', decoded on the substrate's OWN belief_partition FHRR organs) over a construction gold of false-belief-OVER-TIME narratives (60 scenarios, 542 queries, 404 belief/false-belief): the per-agent BELIEF TIMELINE = 1.000 [1.000,1.000] vs the strongest timeline-agnostic floor (current-belief-only, SAME observation cue) 0.460 [0.411,0.510], CI-separated. Info-free twin (shuffled event/observation order) null p95 = 0.535 (< 1.000). Positive control (the belief queries the current-belief floor CANNOT get -- belief-at-T != final-observed, n=218): timeline 1.000 vs floor 0.000. COMPOSED WITH THE REAL temporal-order register on flashback prose: register-ordered belief 1.000 vs narration-ordered 0.000 (n=5 flashback), tie 1.0==1.0 on linear controls, extraction coverage 0.80."
floor: "Strongest floor actually run = the TIMELINE-AGNOSTIC current-belief tracker (holds the latest observed value, SAME observation cue, no reading-time axis) recomputed on the same population = 0.460 [0.411,0.510]; timeline lower CI 1.000 > floor upper CI 0.510. Other floors: omniscient/reality-reading 0.767 [0.725,0.809] (fails false belief -- leaks reality to the agent), always-initial 0.545 [0.495,0.592], empty-register 0.384 [0.337,0.431], info-free twin mean 0.461 / p95 0.535. Narration-ordered timeline 0.911 overall but 0.000 on the flashback subset (isolates the temporal-order register)."
controls: "(1) INFO-FREE TWIN (event/observation ORDER shuffled over 200 seeds) -> p95 0.535, LOSES CI-separated (timeline 1.000 > 0.535) -- excludes 'the timeline works from a non-informative order signal'. (2) POSITIVE CONTROL (the floor-cannot-get subset, belief-at-T != final-observed, n=218): timeline 1.000 vs current-belief 0.000 -- the metric CAN move / the floor provably cannot get these. (3) ISOLATION of the TIME composition: current-belief floor uses the SAME observation bits as the timeline; the ONLY difference is the order-aware read-at-T, so the +0.540 lift is the TIMELINE part, not a better cue. (4) DISTANCE robustness: timeline flat 1.000 at event-distance 0..3 while the floor collapses 1.00->0.00 for distance>=1. (5) REALITY+MEMORY controls 1.000 (n=138) -- the belief partition does not corrupt world/initial tracking. (6) EMPTY register 0.384 (degenerate control, not gameable). (7) HINDSIGHT-DECOUPLING (research drill #1): a later UNOBSERVED world change leaves 'what A believed at T' invariant (1.000, n=41) -- a clean store beats the brain's curse-of-knowledge. (8) REP-B timescale stress: the swept FHRR temporal-context representation is exact (1.000) at inter-event gap>=0.5 and degrades to 0.812 at gap 0.1 while discrete rep-A stays 1.000 -- honest representation sweep (discrete = accuracy layer, graded = order-uncertainty/confidence). (9) REGISTER COMPOSITION: register-ordered 1.000 vs narration-ordered 0.000 on flashback prose, tie on linear controls -- excludes 'narration position is enough'."
files_changed: "experiments/belief_timeline.py (core: sample-and-hold rep A + FHRR temporal-context rep B + floors + twin + testimony/deception edges + hindsight control + belief-gap queries, on hdlab.belief_partition/binding/graded_temporal_context); experiments/belief_timeline_gold.py (construction gold); experiments/exp_belief_timeline_query_v1.py (CI-sep proof); experiments/exp_belief_timeline_flashback_register_v1.py (composition with the REAL temporal-order register); experiments/exp_belief_timeline_gap_v1.py (knowledge-gap / dramatic-irony over time); experiments/exp_belief_timeline_real_prose_v1.py (incidence bound); verification/test_belief_timeline.py (witness, 39/39 PASS); notes/problems/the_reader_has_no_belief_timeline_what_an_agent_knew_when/{research_belief_timeline_brain_mechanism_2026-08-29.md, SOLVED.md}; data/{exp_belief_timeline_query_v1,exp_belief_timeline_flashback_register_v1,exp_belief_timeline_gap_v1,exp_belief_timeline_real_prose_v1}/metrics.json. hdlab/ UNTOUCHED (proposed diff below, Q111)."
reverify: ".venv/Scripts/python.exe verification/test_belief_timeline.py   # 39/39 ; then .venv/Scripts/python.exe experiments/exp_belief_timeline_query_v1.py --mode full  # timeline 1.000 vs floor 0.460 ; .venv/Scripts/python.exe experiments/exp_belief_timeline_flashback_register_v1.py  # register 1.0 vs narration 0.0 on flashback ; and .venv/Scripts/python.exe experiments/exp_belief_timeline_gap_v1.py  # gap 1.000 vs floor 0.667, divergence-window 1.0 vs 0.0"
---

# The reader now has a per-agent BELIEF TIMELINE -- "what did A know AT THIS POINT?"

## The one-line answer
The integrated ToM organ (`hdlab/belief_partition.py`) tracked a SINGLE belief per agent -- a snapshot of ONE
change (`final if observed else initial`). The integrated temporal-order register gave event ORDER but knew
nothing about agents. NOTHING composed them, so the reader could not answer "what did A believe at an EARLIER
point?", could not handle a SEQUENCE of observed/unobserved changes, and could not represent a STALE belief that
is later corrected -- i.e. no dramatic irony, no deception over time. I built the missing composition: a per-agent
belief that is a function of reading-time, updated ONLY on observed events, ordered by the temporal-order
register, and read out on the substrate's own FHRR organs. It answers false-belief-over-time queries **1.000**
vs a timeline-agnostic current-belief floor **0.460** (CI-separated), the info-free order-shuffle twin loses
(p95 0.535), and the composition is proven end-to-end on real flashback prose with the LANDED temporal-order
register (register-ordered 1.000 vs narration-ordered 0.000).

## What I built (the mechanism)
A per-agent belief is a PIECEWISE-CONSTANT (sample-and-hold) function of story-time: it JUMPS at an observed
event and PERSISTS unchanged between events (default-persist / temporal inertia, Dowty 1986 -- the same
persistence the SPACE location register and the entity state register use). "What did A know at time T" is that
function read at T:

    belief_A(X, T) = value of the LATEST event about X that A OBSERVED with order(X-event) <= T   (else None)
    false_belief_A(X, T) = belief_A(X, T) != reality(X, T)

- **Order** comes from the integrated `temporal_order_register` (Reichenbach reference time carried across
  discourse; episodic/relational temporal memory).
- **The observation cue** (does A witness event E?) is REUSED as an INPUT from the integrated ToM front-end
  (`belief_partition` + the perceptual-access ledger), held FIXED across the timeline and the floor -- so the
  measured lift is the ORDER-AWARE read, not a better cue.
- **Read-out on the substrate's own organs:** the believed value is stored/recovered via `belief_partition`'s
  FHRR codebook + `hdlab.binding.bind/unbind` + `cleanup_argmax` -- glass-box, no LLM.
- **Representation SWEEP (OUR-INVENTION-UNDER-TEST):** rep A = discrete interval sample-and-hold (the accuracy
  layer); rep B = an FHRR temporal-context superposition `sum_e bind(bind(obj,val), ctx(order_e))` read at
  ctx(T) (`hdlab.graded_temporal_context`). Rep B is exact when events are well-separated and degrades near
  boundaries (order-uncertainty), so it is the confidence/recency layer -- discrete beats graded, matching the
  temporal-order problem's finding.

This is a faithful GENERALIZATION of `belief_partition` from n=1 change (a snapshot) to n changes over the
register's ordered timeline, queryable at any story-time.

## What I measured (construction gold, 60 scenarios / 542 queries)
| arm | belief-acc | note |
|---|---|---|
| **BELIEF TIMELINE (rep A)** | **1.000 [1.000,1.000]** | the mechanism |
| current-belief floor (SAME cue, no time axis) | 0.460 [0.411,0.510] | strongest floor -- CI-separated below |
| omniscient (reality-reading) | 0.767 [0.725,0.809] | fails false belief (leaks reality to the agent) |
| always-initial | 0.545 [0.495,0.592] | fails updated/multi-change |
| empty register | 0.384 [0.337,0.431] | degenerate control, not gameable |
| info-free twin (order shuffled) | mean 0.461 / p95 0.535 | LOSES CI-separated |
| rep B (FHRR temporal-context) | 1.000 (gap>=0.5) -> 0.812 (gap 0.1) | order-uncertainty layer |

Positive control (the floor CANNOT get -- belief-at-T != final-observed, n=218): timeline **1.000** vs floor
**0.000**. Distance-robust: timeline flat 1.000 at event-distance 0..3 while the floor collapses to 0.000 for
distance>=1. Reality+memory controls intact 1.000 (n=138).

## Composition with the REAL temporal-order register (flashback prose, not oracle)
The belief timeline's chrono axis is supplied by the LANDED `_temporal_order_register` reconstructing
chronology from PROSE. On flashback micro-narratives (an agent's belief-setting observation revealed by a
past-perfect clause AFTER the query event), a narration-ordered timeline has not encountered the observation yet
at the query's text position; the register places it earlier: **register-ordered belief 1.000 vs
narration-ordered 0.000** (n=5 extracted flashbacks), tie 1.0==1.0 on the linear controls (no over-reorder),
register extraction coverage 0.80 (2 authored sentences the shared extractor missed -- honest). This is the
"compose the two integrated organs, don't island" deliverable.

## The knowledge GAP over time (dramatic irony + deception -- deepening cron, 2026-08-30)
Per-agent beliefs are necessary but the decision-relevant quantity for dramatic irony / deception is the
DIFFERENCE between two knowledge states (Frontiers 2023/2025: readers actively track the reader-character and
character-character GAP, and it drives real-time attention). I added two first-class GAP queries over time:
`divergence(A,B,X,T)` (do A and B disagree about X at T?) and `knowledge_advantage(A,B,X,T)` (at T, does A hold
the TRUE belief while B holds a FALSE/stale one -- the asymmetry a deceiver exploits). On divergence-over-time
scenarios (both see the start; B departs; the object moves while A watches and B is absent -> DIVERGE; B returns
and sees -> RE-CONVERGE): the belief timeline scores gap-acc **1.000 [1.000,1.000]** vs the timeline-agnostic
current-belief floor **0.667 [0.625,0.708]** (CI-separated), beating the info-free order-shuffle twin p95
**0.600**. The discriminator is the DIVERGENCE WINDOW (t during B's absence): timeline **1.000** vs floor
**0.000** (n=160) -- the current-belief tracker sees only the final agreed state and misses the entire window
where A knows something B does not. This is the substrate of a secret, a lie, and dramatic irony, and it is
recoverable only with the timeline.

## Real-narrative incidence (the honest bound)
Belief-STALENESS ingredients are COMMON: 170/991 (17.2%) of the corpus-mined observation events (LitBank, reused
from the observation-cue problem) are non-observations where a belief can go stale; 75/92 books carry multi-event
structure. But COMPLETE, gold-labelable false-belief-OVER-TIME SCENES (a tracked object + ordered moves +
observation state + a past-time query) are NOT automatically minable -- the corpus yields observation cue-CLAUSES,
not the full ordered scene, which is why the integrated ToM organ AUTHORED its gold (26/26 authored passages are
single-change snapshots, 0 over-time; explicit dramatic-irony markers 7/991 = 0.7%). So the mechanism is proven
on construction gold + real flashback prose; the real-corpus AGGREGATE lift is bounded by the annotation gap, NOT
by the mechanism -- a coverage-bounded result with the positive controls confirming the mechanism.

## KEY REALIZATIONS (the enabling moves)
1. **The gap is a GENERALIZATION, not a new organ.** `belief_partition` already computes `final if observed else
   initial` -- that IS the sample-and-hold for n=1. The whole problem is lifting it to n ordered events with a
   query-time axis. Once framed that way, the mechanism is `argmax_{observed events <= T} order`.
2. **The discriminator is the PAST-T / RE-OBSERVE query, not "false belief" per se.** A pure Sally-Anne (one
   unobserved move) does NOT separate the timeline from a current-belief tracker -- both correctly report the
   stale value. The separation appears only when belief-at-T differs from the agent's FINAL belief (a past-time
   query, or a stale belief later corrected). That is literally "what did A know AT THIS POINT," and a
   current-belief-only reader structurally cannot rewind.
3. **The research drill corrected the STORAGE, not the computation.** My sample-and-hold is the right idealized
   readout, but the brain STORES sparse time-tagged observation events and RECONSTRUCTS the past (and that
   reconstruction is corrupted by current knowledge -- hindsight bias). Rep A already stores sparse events and
   computes the step function at readout, so it is the faithful design -- and because it is a CLEAN decoupled
   store, it BEATS the brain's curse-of-knowledge (the hindsight-invariance control = 1.000). A place where the
   right software is better than the wetware, and the drill told me to take it.
4. **Belief updates by TESTIMONY, not only observation -- this is what makes deception representable.** Adding a
   communicated-assertion edge (which may be FALSE, and does NOT move the world) gave the deception capability
   the brief names, for near-zero cost, via an `affects_reality=False` pseudo-event.
5. **The graded FHRR temporal-context rep is honest only when you probe at the query time, not the resolved
   index.** My first rep B scored a fake 1.000 because I pre-resolved the exact event with the same
   sample-and-hold logic. Rebuilding it as a genuine causal contiguity read (build up to T, probe at ctx(T))
   exposed the real regime: exact when events are separated, lossy near boundaries.

## What I did NOT establish (and would withdraw first)
- **No corpus-mined false-belief-over-time gold.** The CI-separated numbers are on construction gold + authored
  flashback prose (the definitional basis the integrated ToM + temporal organs also used). I would withdraw any
  implied claim of a real-corpus aggregate lift first -- the incidence cell bounds it explicitly.
- **First-order belief only.** Higher-order "A thinks B knew X at T" is out of scope (matches `belief_partition`;
  the human recursion cap is ~2 orders -- a noted adjacent problem, not a claim here).
- **Register extraction is 0.80 on the authored flashback prose** (the shared temporal-order/spaCy extraction
  wall on some verbs), not 1.0 -- the composition is proven on the extracted subset; I do not claim
  extraction-complete real-prose coverage.
- **Rep B is a confidence/order-uncertainty layer, not an accuracy gain** over rep A -- I would not claim the
  graded representation improves accuracy.

## FOR STRATEGY (proposed hdlab landing -- Q111, you own it)
1. Promote the spaCy-free core to `hdlab/belief_timeline.py` (composes `belief_partition` +
   `_temporal_order_register` + `graded_temporal_context`): `BeliefTimeline` with `belief(agent,obj,T)` /
   `false_belief(agent,obj,T)`, rep A as the value/change-point layer, rep B as the recency/order-uncertainty
   layer. Keep the store DECOUPLED (a world update writes an agent slot ONLY through an observed/communicated
   edge -- the anti-hindsight invariant, which is also the best can-fail control).
2. Wire the update-edge TYPES (observed / communicated-may-be-false) so deception and testimony are first-class.
3. Wire the belief-vs-reality and belief-vs-belief GAP queries (dramatic-irony / deception detector over time) --
   BUILT + proven in `experiments/exp_belief_timeline_gap_v1.py` (gap 1.000 vs floor 0.667, divergence-window
   1.0 vs 0.0); promote `divergence` / `knowledge_advantage` alongside the timeline.
4. It consumes the temporal-order register's chronology and the perceptual-access observation cue -- both already
   integrated/proven; this is the composition site, not a new island.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md, GOALS/ToM entry)
The GOALS/ToM section should gain a **belief-TIMELINE** sub-entry: **PINNED** (per-agent belief separate from
reality, TPJ/mPFC; observation-gated update; sample-and-hold persistence = Dowty temporal inertia; composition of
a dissociable mentalizing system x an episodic/temporal-order system, bound at event boundaries -- Saxe &
Kanwisher 2003; Zwaan & Radvansky event-indexing; Howard/Eichenbaum). **OUR-INVENTION-UNDER-TEST:** the timeline
REPRESENTATION (discrete interval sample-and-hold beats graded FHRR temporal-context, which is the
order-uncertainty layer). **Corrections folded from the research drill:** the brain STORES sparse events +
RECONSTRUCTS the past (a clean decoupled store BEATS the brain's curse-of-knowledge -- proven, invariance 1.000);
belief also updates by TESTIMONY/communication (deception), not only observation; first-order only (recursion cap
~2). The prior audit note "goal-timeline (what an agent knew WHEN) not composed with TIME" is now CLOSED at the
mechanism level (proposed hdlab landing pending, Q111).

## ADJACENT COMPONENTS evaluated (candidate next problems -- fidelity + optimization)
- **Observation-cue front-end (`perceptual_access_ledger`)** -- PINNED (sticky registration ledger) and PROVEN
  (end-to-end 0.988) but lives in experiments/, not `hdlab/`. Leverage: it is the INPUT this timeline holds
  fixed; wiring it live is the end-to-end enabler. Optimization: integrate it; the belief timeline is a first
  consumer.
- **Intensionality / guise-keying (Superman-Clark; Apperly & Butterfill signature limit)** -- our codes are
  seeded from TEXT SURFACE forms, so distinct guises already get distinct codes (accidentally guise-correct); a
  genuine intensional store (belief keyed by mode-of-presentation with a co-referring guise link) is a
  higher-fidelity follow-on. OUR-INVENTION placeholder today.
- **Higher-order / recursive belief** -- capacity-limited in humans (~2 orders); a nested belief-file store could
  exceed the human cap (OUR-INVENTION-acceptable, validate against combinatorial blow-up). A clean next problem.
- **rep B event-boundary alignment** -- `graded_temporal_context.EventSegmentedContext` already exists; aligning
  belief change-points to segmented event boundaries (Zacks) is a fidelity refinement to the recency layer.
- **Curse-of-knowledge intrusion term** -- optional: a controllable anchor to MODEL human hindsight error when
  human-likeness (not correctness) is the goal.

## TLDR
Understanding a story means tracking not just what is true, but what each character THINKS is true -- and that
changes as they see (or miss) things. Our reader could track a character's belief RIGHT NOW and could order
events in time, but could not put them together to answer "what did she think a moment ago?" I built that: each
character's knowledge is a little step-function over story-time that only changes when they actually witness (or
are told) something, so the reader can hold a character's stale, wrong belief -- the basis of dramatic irony and
deception. It answers "where does she think it is / does she have a false belief here?" perfectly where a reader
without the timeline gets it wrong about half the time, the win survives every control including an
order-scramble, and it works on real flashback sentences using the existing time-order organ. It is proven as a
mechanism on built-for-purpose examples; fully gold-labeled examples of this exact structure are rare in raw
novels, which I measured and report honestly.

## QUESTIONS
None.

## NEXT STEPS
Land the composition in hdlab (proposed diff above, Q111), wire the observation-cue ledger live (its integration
is the end-to-end enabler), and pick the next reasoning problem from the adjacent list -- the intensional/guise
store or higher-order belief are the highest-fidelity follow-ons.
