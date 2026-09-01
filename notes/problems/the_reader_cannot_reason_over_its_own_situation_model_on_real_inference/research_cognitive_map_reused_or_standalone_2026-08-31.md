# Is CANONICAL-SCRIPT-ORDER building a REUSED general cognitive-map function, or a STANDALONE mechanism?

Research drill for `the_reader_cannot_reason_over_its_own_situation_model_on_real_inference`.
Date 2026-08-31. Author: solver (finer brain-fidelity drill deciding whether to REUSE the existing
relational-ordering organ or build a bespoke one). ONLINE-literature synthesis; **lit-scan
calibration penalty applied** — every "should"/"is the right move" below is a DESIGN HYPOTHESIS
pending our own measurement, not an inherited number.

**The decision this note settles.** The sibling drill (`research_script_vs_episodic_temporal_order_wall_2026-08-31.md`)
concluded the MCScript2 before/after wall is a KNOWLEDGE gap: the reader models the episodic
hippocampal timeline (works) but has no store of the CANONICAL order of a kind of activity
(mPFC/posterior-medial schema, unbuilt). It sketched a follow-on organ: statistical schema
induction across narratives -> pairwise event-precedence premises -> integrate -> transitive
closure -> before/after, with a schema-default/episodic-override. **This note asks the one question
that decides HOW to build the "integrate + read off before/after" core: is that a REUSED general
function we already have as a validated glass-box organ (`hdlab/transitive_ordering.TransitiveOrderingLine`),
or a domain-dedicated temporal mechanism that must be built from scratch?**

**Builds on** both sibling drills (the online/offline inference split; the two dissociable
temporal-order systems; the KNOWLEDGE-gap verdict). Does NOT rehash them. Goes FINER on the
domain-generality of the RELATIONAL-INTEGRATION machinery specifically.

**Prior-arc work check (three archives, 2026-08-31):**
- `experiment_index.py query`: `"transitive"` 10 cells / 9 landed (the reasoning-primitive lineage);
  `"temporal order"` 6/3; `"cognitive map"` 0; `"canonical order schema"` 0; `"magnitude line"` 0.
- `substrate_query.sh "cognitive map relational structure transitive ordering temporal schema reuse"`:
  no hits (unified-KB returns empty on this concept phrase).
- So: the ORGAN exists and is validated (`transitive_comparison_reasoning...` SOLVED/EXCELLENT,
  owner-DONE, landed to `hdlab/transitive_ordering.py` 2026-08-28), but **the question "is canonical
  script-order a reuse of it" has not been asked before.** This drill is that question.

---

## THE ORGAN UNDER CONSIDERATION (what we would reuse) — verified off-disk

`hdlab/transitive_ordering.py :: TransitiveOrderingLine` (read in full, 2026-08-31). Its computation,
verbatim from the code + module doc:

1. **Read pairwise premises** `(winner_idx, loser_idx)` — a partial/overlapping set of comparisons.
2. **INTEGRATE by delta-rule / value-transfer settling** (`_settle`): the Bradley-Terry ML gradient
   `p = sigmoid(temp*(x_w - x_l)); x_w += eta*(1-p); x_l -= eta*(1-p)`, zero-mean each epoch.
   Overlapping premises couple through their shared middle term, so adjacent comparisons settle into
   ONE integrated scalar ordering.
3. **Place items on a BOUNDED parietal MAGNITUDE LINE** (`_normalize_line` -> [-1,1]) and bind each to
   its magnitude place code via fractional-power encoding, superposed into one FHRR register
   `S = sum_i bind(item_key_i, FPE(scale * x_i))`.
4. **Answer an UN-STATED pair** (`compare(a,b)`) by unbinding each item's key, decoding its coordinate
   off the FPE grid (native resonator read-out), and comparing — the answer is READ off the integrated
   line, never symbolically chained.

Its cited PINNED brain basis (in the module doc): relational integration by delta-rule/value-transfer
(**Frank, Rudy & O'Reilly 2003**; **Dusek & Eichenbaum** hippocampal relational memory) + the
bounded parietal magnitude line (**Zorzi/Dehaene**). The distance effect + end-anchor effect emerge
as read-out noise on the bounded line (a measured human signature; far-pairs-easier rules out serial
chaining).

**This is precisely "settle pairwise relations into a shared ordered line, then read un-stated
relations off it."** The whole question below is whether THAT computation is the domain-general
cognitive-map function — because if it is, canonical script-order is a reuse, and this organ already
implements it.

---

## Q1 — THE COGNITIVE MAP IS A GENERAL, REUSED CODE, not a spatial-only map. PINNED, decisive.

The evidence that the hippocampal-entorhinal system implements a GENERAL relational/structural code,
reused across domains, is now one of the best-supported claims in systems neuroscience. Five
load-bearing pillars, all verified online 2026-08-31:

- **Tolman 1948 / O'Keefe & Nadel 1978 — the origin and the spatial anchor.** Tolman's "cognitive
  map" was proposed as a general representation of relationships; O'Keefe & Nadel localized the
  literal spatial map to the hippocampus (place cells). The open question they left: is the map
  spatial-ONLY, or is space just the best-studied instance of a general code?

- **Behrens, Muller, Whittington, Mark, Baram, Stachenfeld & Kurth-Nelson 2018, *Neuron* 100(2):490
  "What Is a Cognitive Map? Organizing Knowledge for Flexible Behavior" — the canonical synthesis,
  and it answers that question: general.** Its thesis (verified): "map-like representations observed
  in a spatial context may be an instance of GENERAL coding mechanisms capable of organising
  knowledge of ALL kinds," supporting "rapid inferences and flexible behaviour with little direct
  experience." The map is a mechanism for organizing ANY relational knowledge, not a spatial module.

- **Constantinescu, O'Reilly & Behrens 2016, *Science* 352:1464 — a grid-like code for an abstract
  2D CONCEPT space.** Humans navigating a novel 2D space of bird shapes (neck length x leg length)
  showed the SAME hexagonally-symmetric grid signal, in the SAME regions (entorhinal cortex + vmPFC),
  as spatial navigation. The brain re-uses the spatial coordinate code for abstract concept
  dimensions.

- **Whittington, Muller, Mark, Chen, Barry, Burgess & Behrens 2020, *Cell* 183:1249 — the
  Tolman-Eichenbaum Machine: ONE model that generalizes across spatial AND non-spatial.** Verified:
  weights are learnt from sensory experience by FACTORISING structure (medial-entorhinal basis) from
  content (hippocampal conjunction with sensory), "enabling the system to learn abstract map-like
  representations in both spatial problems and ARBITRARY NON-SPATIAL problems." After learning, its
  entorhinal units display grid/band/border/object-vector properties and its hippocampal units are
  place/landmark cells that remap — from ONE factorised relational-memory mechanism. This is the
  computational proof that space and relational memory are the SAME machinery.

- **Park, Miller, Nili, Ranganath & Boorman 2021, *Nat Neurosci* 24:1292 (+ 2020 bioRxiv) — a
  grid-like code for an abstract SOCIAL hierarchy.** Discretely-sampled pairwise relations in an
  unseen 2D social hierarchy were reconstructed into a UNITARY 2D cognitive map in hippocampus +
  entorhinal cortex; a grid-like code in EC + mPFC encoded inferred direct trajectories during
  decisions. Directly analogous to our use-case: pairwise premises -> reconstructed relational map ->
  inferred (un-stated) relations read off it.

- **Aronov, Nevers & Tank 2017, *Nature* 543:719 + Bao et al. 2019, *Neuron* (2D odor space) — a
  purely NON-SPATIAL 1D/2D dimension mapped by the SAME cells.** Rats manipulating a continuous
  sound-FREQUENCY axis produced hippocampal/entorhinal firing fields at particular frequencies, in
  neurons OVERLAPPING the known place/grid cell types. "Common circuit mechanisms are used to
  represent diverse behavioral tasks." A 1D continuum (frequency) is placed on the same map — the
  closest animal analog to a 1D ordinal line.

**Q1 VERDICT (PINNED): "place items on a shared metric line/map and read relations off it" is a
REUSED, domain-general computation** — demonstrated for space, abstract 2D concepts, social
hierarchy, and a non-spatial 1D continuum, by ONE factorised relational-memory mechanism (TEM). This
is exactly the class of computation `TransitiveOrderingLine` implements.

---

## Q2 — TRANSITIVE / ORDINAL INFERENCE IS THE SAME MACHINERY, and our organ copies exactly it. PINNED.

Transitive inference (A>B, B>C -> A>C) is not a separate faculty; it is the domain-general
relational-integration function specialized to a 1D ordinal relation, and it is the canonical
hippocampal-relational-memory assay:

- **Dusek & Eichenbaum 1997, *PNAS* 94:7109 — the hippocampus is required to hold "orderly stimulus
  relations" and answer the un-stated pair.** The founding transitive-inference / relational-memory
  result; already the organ's cited basis.
- **Frank, Rudy & O'Reilly 2003 — value transfer / the delta-rule account** of how overlapping
  premises settle into an integrated ordering. The organ's `_settle` (Bradley-Terry ML gradient) IS
  this computation.
- **Kumaran & McClelland 2012, *Psych Review* 119:573 (REMERGE) — the domain-general model.** Verified:
  a "recurrent similarity computation... allows the hippocampus to support generalization through
  interactions that unfold within a dynamically created memory space," accounting for transitive
  inference, paired-associate inference AND acquired equivalence with ONE mechanism. Our organ's
  iterative settling of pairwise premises into an integrated ordering is a computational-level
  instance of exactly this recurrent-settling family.
- **The symbolic-distance effect (Moyer & Landauer; Dehaene number line) — the magnitude-line
  signature.** Comparisons of far-apart items are FASTER/easier; the effect is the read-out signature
  of a metric mental line. The organ reproduces it (far-pairs-easier, from bounded-line read-out
  noise) — the same signature the brain shows for number, rank, and transitive order.

**Q2 VERDICT (PINNED): transitive/ordinal inference = the domain-general relational-integration +
magnitude-line read-out, and `TransitiveOrderingLine` is a faithful copy of that specific machinery
(REMERGE-family settling + Dusek/Eichenbaum relational memory + the parietal magnitude line).** It is
not merely "a" relational integrator — it copies the exact hippocampal transitive-inference operation
that the cognitive-map literature identifies as a special case of the general map function.

---

## Q3 — DOES CANONICAL EVENT ORDER RIDE THAT SAME MAP? Yes — and it is 1D-ordinal, the magnitude line's native shape. PINNED (computational level).

This is the crux for reuse. Two things must be true: (a) abstract/canonical ORDINAL structure is
carried on the general relational-map machinery, and (b) canonical order abstracted ACROSS episodes
is applied to a specific instance by that machinery.

- **A hierarchical/abstract SEQUENCE-ORDER code sits in the entorhinal-hippocampal map, alongside the
  space and time codes.** The eLife (2024/25) work "A hierarchical coordinate system for sequence
  memory in human entorhinal cortex" tests sequence representations as "abstract and organised on an
  anatomical hierarchy... inspired by spatial grid cells and lateral-entorhinal temporal codes."
  There is an abstract ORDER/position code, distinct from content and from absolute duration
  (consistent with the human order-selective cells the sibling drill cites). **Honest boundary:** that
  study explicitly leaves open whether the sequence-coordinate system "repurposes these [grid/time]
  cells or involves different ones" — so at the NEURAL-IMPLEMENTATION level, same-cells-or-not is
  UNPINNED. At the COMPUTATIONAL level (an abstract ordinal metric read relationally) it is pinned.

- **Bellmund, Deuker et al. (Doeller lab) 2022, *Nat Commun* 13:3646 "Mnemonic construction and
  representation of temporal structure in the hippocampal formation" — the decisive finding for
  canonical-across-episodes.** Verified: "structural knowledge about time patterns, ABSTRACTED FROM
  DIFFERENT SEQUENCES, biased the construction of specific event times," and "temporal relations were
  GENERALIZED ACROSS SEQUENCES." This is literally: a canonical order learned across many instances,
  represented on the hippocampal map, applied to bias a specific instance's event times — the exact
  operation the follow-on organ needs. Its 2021 bioRxiv companion ("the hippocampus constructs
  sequence memories that generalize temporal relations across experiences") is the same claim at the
  trace level.

- **Canonical order at the SEMANTIC/schema pole = mPFC + posterior-medial cortex (Baldassano, Hasson
  & Norman 2018).** The canonical script structure that GENERALIZES across stories lives in the
  mPFC/PMC schema system; scrambling weakens it ("mPFC confers ordinality"). This is the STORE of the
  abstracted structure — the cortical (CLS) end — from which the hippocampal line is loaded
  (McClelland, McNaughton & O'Reilly 1995 CLS: schema default + episodic override).

- **Bellmund, Gärdenfors, Moser & Doeller 2018, *Science* 362:eaat6766 "Navigating cognition:
  spatial codes for human thinking"** — the review pinning that the cognitive-spaces/grid framework
  extends to conceptual AND temporal dimensions generally.

**The dimensionality point that STRENGTHENS the fit:** most cognitive-map results are 2D (grid codes
need >=2D). Canonical EVENT ORDER is fundamentally **1D-ordinal** — a before/after axis (a partial
order projected onto one line). That is exactly the dimensionality of the **1D bounded magnitude
line** the organ implements (and of Aronov's 1D frequency continuum, and of the number line). We do
NOT need the 2D grid; we need the 1D ordinal line, which is what we already have. Temporal order is
the map function at its simplest, most-native dimensionality.

**Q3 VERDICT (PINNED, computational level): canonical event ORDER rides the same general
relational-map machinery as magnitude/space/rank — abstracted across sequences (Nat Commun 2022) and
stored as canonical schema in mPFC (Baldassano 2018) — and it is 1D-ordinal, i.e. the magnitude
line's native shape.** Reusing the 1D magnitude-line organ for canonical order is brain-faithful, not
a hack. (Neural-implementation UNPINNED: whether the ordinal code is literally grid/time cells or a
homologous sequence code — irrelevant to our build, exactly as VSA binding is UNPINNED at the neural
level while FHRR is kept at the computational level.)

---

## Q4 — VERDICT: REUSED. The one general computation to copy, the domain-specific parts to supply, and where mPFC fits.

**ONE-LINE VERDICT: canonical-script-order building is REUSED — a special case of the general
cognitive-map / relational-integration function (transitive inference over a partial order, read off
a shared ordinal line), NOT a standalone domain-dedicated mechanism.**

**The ONE general computation to copy (already implemented by `TransitiveOrderingLine`):** settle a
set of pairwise relations by delta-rule/value-transfer into ONE integrated ordering on a shared
bounded ordinal line; answer any un-stated pair by native read-out of the two coordinates. Do NOT
rebuild this for temporal order — it is the same function, and the organ is a faithful, validated
copy of it.

**The DOMAIN-SPECIFIC parts that must still be supplied per domain (these are what make "restaurant
script order" different from "giraffe height ordering"):**
1. **The premises/observations** — per-scenario pairwise event-PRECEDENCE relations. For temporal
   order these are read off the reader's OWN episodic timeline for the events a narrative DOES narrate
   in order (reliable per the sibling drill's Q2a; this is the `timeline_register` / `sequence_memory`
   episodic tape doing what it already does well).
2. **The item vocabulary** — the canonical event-TYPE slots for the scenario (`pour_drink`,
   `present_check`, ...), i.e. what the integer item indices MEAN.
3. **The ACQUISITION / ABSTRACTION step** — extract the MODAL order across many episodes: aggregate
   the observed within-passage pairwise directions across many narratives of the same scenario, take
   the modal direction as the canonical relation, keep the vote margin as confidence. This is the
   prediction-error-gated statistical schema induction (Reynolds, Zacks & Braver 2007) — **the ONE
   genuinely-new piece with no existing organ**, and it is a first-class North-Star learner target
   (learn structure by reading many instances).

**Where mPFC schema fits vs the hippocampal line (the architecture):** they are the two poles of
Complementary Learning Systems. **mPFC/PMC = the STORE of the abstracted canonical structure** (the
slowly-consolidated schema; Baldassano 2018; Tse 2007), i.e. the durable per-scenario canonical
partial-order + confidences produced by the acquisition step. **The hippocampal magnitude line
(`TransitiveOrderingLine`) = the fast integrator/read-out that instantiates a given scenario's order
at question time**, loaded FROM the mPFC store's premises, and OVERRIDDEN locally where the specific
passage's episodic timeline marks a deviation (the flashback mechanism). So: mPFC stores the learned
canonical order; the line settles+reads it for the specific query; the episodic timeline overrides on
explicit textual deviation. This is exactly the CLS schema-default / episodic-override the sibling
drill pinned.

---

## Q5 — IMPLICATION FOR THE BUILD: REUSE the integrator, COMPOSE the router + tape + cortical store, BUILD only the abstraction glue.

**Recommended organ to REUSE (primary): `hdlab/transitive_ordering.TransitiveOrderingLine`.** Feed it
the per-scenario aggregated pairwise event-precedence premises `(earlier_event_slot, later_event_slot)`
(as winner/loser on the "earlier" axis), `integrate()`, then `compare(a,b)` answers before/after —
including un-stated pairs by transitive read-out. This is the brain-faithful move: it copies the exact
domain-general transitive-inference operation (Q2) that canonical order rides (Q3), at the correct 1D
dimensionality. It is validated (SOLVED/EXCELLENT, owner-DONE) and glass-box (no LLM).

**Compose with (all existing):**
- **`hdlab/schema_exemplar_bayes.SchemaExemplarBayes` — the SCENARIO ROUTER.** LSE-Bayes cluster
  routing = recognize WHICH script a passage instantiates (restaurant vs airport), so the right
  canonical order is retrieved. This is the "schema retrieval is online" hook (Metusalem 2012); it is
  a router, correctly NOT an orderer — pair it with the line, do not overload it.
- **The episodic timeline (`hdlab/sequence_memory.SequenceMatrix` / the reader's `timeline_register`)
  — the EPISODIC TAPE.** Two jobs: (a) at TRAINING time, OBSERVE within-passage pairwise order to feed
  the abstraction step; (b) at QUESTION time, OVERRIDE the canonical default where the text explicitly
  marks a non-canonical order. Reuse as-is; it already works (the +0.036 twin loss, the flashback
  recovery).
- **`hdlab/additive_map.AdditiveKGMap` — OPTIONAL persistent CLS cortical-schema STORE (the mPFC
  analog).** It is explicitly built as "a CLS cortical-schema analog... entity coordinates,
  relations = directions, closed-form Euclidean readout." It is the natural durable home for the
  learned per-scenario canonical order (the mPFC pole of Q4) if the order should persist across
  sessions rather than be re-derived. Use it as the STORE the line is loaded from; it is NOT a
  substitute for the line's settling/ordinal read-out. (For a first can-fail build, an in-memory
  premise table is enough; promote to `additive_map` only if persistence is needed.)

**BUILD only the genuinely-new GLUE — the cross-episode abstraction step (Q4.3):** segment each
training narrative into events (reuse the reader's event extraction) -> slot-map events to canonical
event-types by clustering the reader's OWN gist embeddings (glass-box, no LLM) -> observe each
narrative's within-passage pairwise order off the episodic timeline -> aggregate across many
narratives into modal direction + vote-margin confidence per slot-pair -> emit those as the pairwise
premises for `TransitiveOrderingLine`. This is the ONLY component without an existing organ, and it is
the North-Star learner move. The update rule (majority-vote vs EM/prediction-error), the slot-cluster
granularity, and the confidence/abstain threshold are OUR-INVENTION-UNDER-TEST (sweep).

**One design caveat to test, not a blocker:** a 1D magnitude line forces a TOTAL order, but real
scripts are PARTIAL orders (some steps genuinely unordered/parallel). The organ handles this via the
vote-margin confidence — near-tied coordinates flag "no canonical order, abstain / fall back to
episodic read." Whether that abstention threshold cleanly separates true partial-order pairs from
noise is a sweepable OUR-INVENTION parameter, and the can-fail experiment should report it. (This is
the honest edge of the reuse: the line is the right computation; the partial-order/abstention policy
is the tuning.)

---

## PINNED vs OUR-INVENTION labeling (this drill's contribution)

**PINNED (brain-constrained; replicate the operation):**
- The cognitive map is a GENERAL, reused relational code (Behrens 2018; Constantinescu 2016; TEM
  Whittington 2020; Park 2021; Aronov 2017 / Bao 2019).
- Transitive/ordinal inference = the domain-general relational-integration + magnitude-line read-out
  (Dusek & Eichenbaum 1997; Kumaran & McClelland 2012 REMERGE; Frank/Rudy/O'Reilly 2003; symbolic
  distance effect). `TransitiveOrderingLine` copies this.
- Canonical event ORDER rides that same machinery, at 1D-ordinal dimensionality: abstracted across
  sequences (Bellmund/Doeller Nat Commun 2022) and stored as mPFC/PMC schema (Baldassano 2018);
  instantiated per-instance with episodic override (CLS; McClelland 1995).

**OUR-INVENTION-UNDER-TEST (sweep; glass-box, NO external LLM):**
- The cross-episode abstraction update rule (majority-vote vs EM/prediction-error), slot-cluster
  granularity, confidence/abstain threshold, transitive-closure conflict resolution, and the
  schema-default-vs-episodic-override arbitration policy.

**UNPINNED at the neural-implementation level (does NOT affect the build):** whether the abstract
ordinal/sequence code is literally grid/time cells or a homologous dedicated sequence code (the eLife
sequence-coordinate work leaves this open). We copy the COMPUTATION, not the cells — consistent with
FHRR-binding being UNPINNED at the neural level while kept at the computational level.

---

## Proposed AUDIT UPDATE for `notes/BRAIN_FOUNDATIONAL_AUDIT.md §2b` (NOT applied — surfaced for strategy)
> **Canonical-script-order building is a REUSE of the domain-general cognitive-map / relational-
> integration function, not a standalone mechanism.** The hippocampal-entorhinal map is a general
> reused relational code (Behrens 2018; TEM 2020; grid-like codes for concept space, social
> hierarchy, and non-spatial continua). Transitive/ordinal inference is that function specialized to
> a 1D ordinal line (Dusek & Eichenbaum; Kumaran & McClelland REMERGE), and canonical event order
> rides it (temporal structure abstracted across sequences, Nat Commun 2022; mPFC schema, Baldassano
> 2018). Therefore the "integrate pairwise precedence -> read before/after" core of the
> canonical-order organ should REUSE `hdlab/transitive_ordering.TransitiveOrderingLine` (validated,
> glass-box), composed with `schema_exemplar_bayes` (scenario router) + the episodic timeline
> (observe/override) + optionally `additive_map` (mPFC/CLS store). The ONLY new build is the
> cross-episode statistical-schema-induction glue (Reynolds/Zacks/Braver 2007) — a North-Star learner
> target.

---

## Key citations
- Behrens T.E.J., Muller T.H., Whittington J.C.R., Mark S., Baram A.B., Stachenfeld K.L. & Kurth-Nelson Z. (2018). What is a cognitive map? Organizing knowledge for flexible behavior. *Neuron* 100(2):490-509.
- Constantinescu A.O., O'Reilly J.X. & Behrens T.E.J. (2016). Organizing conceptual knowledge in humans with a gridlike code. *Science* 352(6292):1464-1468.
- Whittington J.C.R., Muller T.H., Mark S., Chen G., Barry C., Burgess N. & Behrens T.E.J. (2020). The Tolman-Eichenbaum Machine: unifying space and relational memory through generalization in the hippocampal formation. *Cell* 183(5):1249-1263.
- Park S.A., Miller D.S., Nili H., Ranganath C. & Boorman E.D. (2021). Inferences on a multidimensional social hierarchy use a grid-like code. *Nature Neuroscience* 24:1292-1301. (2020 bioRxiv preprint.)
- Aronov D., Nevers R. & Tank D.W. (2017). Mapping of a non-spatial dimension by the hippocampal-entorhinal circuit. *Nature* 543:719-722. + Bao X. et al. (2019). Grid-like neural representations support olfactory navigation of a 2D odor space. *Neuron* 102:1066-1075.
- Dusek J.A. & Eichenbaum H. (1997). The hippocampus and memory for orderly stimulus relations. *PNAS* 94:7109-7114.
- Kumaran D. & McClelland J.L. (2012). Generalization through the recurrent interaction of episodic memories (REMERGE): a model of the hippocampal system. *Psychological Review* 119:573-616.
- Frank M.J., Rudy J.W. & O'Reilly R.C. (2003). Transitivity, flexibility, conjunctive representations, and the hippocampus. *Hippocampus* 13:341-354. (Value transfer / relational integration.)
- Bellmund J.L.S., Deuker L. et al. (Doeller lab) (2022). Mnemonic construction and representation of temporal structure in the hippocampal formation. *Nature Communications* 13:3646. + biorxiv 2021 "Structuring time..." companion.
- Baldassano C., Hasson U. & Norman K.A. (2018). Representation of real-world event schemas during narrative perception. *J Neurosci* 38(45):9689-9699.
- Bellmund J.L.S., Gardenfors P., Moser E.I. & Doeller C.F. (2018). Navigating cognition: spatial codes for human thinking. *Science* 362:eaat6766.
- Garvert M.M., Dolan R.J. & Behrens T.E.J. (2017). A map of abstract relational knowledge in the human hippocampal-entorhinal cortex. *eLife* 6:e17086.
- McClelland J.L., McNaughton B.L. & O'Reilly R.C. (1995). Why there are complementary learning systems. *Psychological Review* 102:419-457.
- Reynolds J.R., Zacks J.M. & Braver T.S. (2007). A computational model of event segmentation from perceptual prediction. *Cognitive Science* 31:613-643.

---

## TLDR (plain English)
The brain does not have a separate machine for "the usual order of steps in an activity." It has ONE
general system — the same one it uses for maps, for number, for ranking people, for social pecking
order — that takes a bunch of "this comes before that" facts, settles them into a single line, and
then reads off the order of any pair, even pairs you were never directly told about. Ordering the
steps of a restaurant visit is just that same trick applied to time, and time-order is the SIMPLEST
version of it (a single before/after line). We already BUILT that general trick and validated it: our
`transitive_ordering` organ takes pairwise comparisons, settles them into one line, and answers
un-stated pairs — exactly copying the brain's transitive-inference machinery. So we should NOT build a
new, dedicated "script order" mechanism. We should REUSE the ordering organ we have, feed it
event-before-event facts, and read off before/after. The only genuinely new thing to build is the
learning step that watches many stories about the same activity and works out the USUAL order to feed
in — which is exactly our learn-by-reading direction.

## VERDICT
**REUSED.** Canonical-script-order building is a special case of the general cognitive-map /
relational-integration function (transitive inference over a partial order, read off a shared ordinal
line). Reuse `hdlab/transitive_ordering.TransitiveOrderingLine`; do not build a bespoke temporal
mechanism.

## QUESTIONS
None for the owner. One open DESIGN choice (solver's call): build the persistent canonical-order store
on `additive_map` (the mPFC/CLS analog) now, or start with an in-memory premise table and promote only
if cross-session persistence is needed. Recommendation: in-memory first — it is the cleaner can-fail
step; promote to `additive_map` once the reuse is proven.

## NEXT STEPS
1. **REUSE** `TransitiveOrderingLine` as the canonical-order integrator + before/after read-out (do
   not build a new temporal-order mechanism).
2. **BUILD** the one new organ: the cross-episode abstraction glue (segment -> slot-cluster on the
   reader's own gist embeddings -> observe within-passage order off the episodic timeline -> aggregate
   modal direction + confidence across many narratives -> emit pairwise premises). North-Star learner
   target; glass-box, no LLM.
3. **COMPOSE** at question time: `schema_exemplar_bayes` recognizes the scenario -> load its premises
   into the line -> `compare()` answers before/after -> episodic timeline OVERRIDES where the text
   marks a deviation; abstain on low vote-margin (partial order).
4. **CAN-FAIL test**: answer before/after when a single passage under-determines the order; info-free
   twin = scrambled canonical premises, MUST LOSE CI-separated; report the abstention-threshold
   behavior on genuinely-unordered pairs.
5. Surface the AUDIT UPDATE above to strategy for `BRAIN_FOUNDATIONAL_AUDIT.md §2b`.
