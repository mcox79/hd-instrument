# Research note: full function inventory of consolidation + does "no consolidation" survive re-examination?

**Date:** 2026-07-16
**Trigger:** USER-flagged potential contradiction — we adopted hippocampal DG/CA3 separation+addressing (mapped to
sparse codes + resonator completion) but rejected hippocampal->cortical systems consolidation, on route-closure
grounds that our distributed store has graceful, not catastrophic, crosstalk. But the brain runs separation AND
consolidation together, and consolidation does more than interference-avoidance. This note leads with biology to
build the FULL function inventory, isolate the crux (schema reorganization of already-written memories), and
render a reconcile-or-refute verdict.
**Method:** 3 parallel Sonnet lit-scan sub-agents (public neuroscience/psychology literature only, generic terms,
no substrate specifics off-platform) covering (1) schema-driven consolidation/reorganization (Tse, SLIMM,
reconsolidation-of-old-memory evidence), (2) semanticization/gist extraction + active forgetting/pruning, (3)
sleep-replay creative recombination/inference + reconsolidation triggers and boundary conditions. Cross-checked
against this project's own extensive, already-landed ingest-gate design work
(`research_brain_foundation_ingest_gate_consolidation_loop_2026-07-15.md`,
`research_consolidation_gate_signal_mechanism_and_integration_2026-07-16.md`,
`research_cls_stc_currency_wrong_regime_2026-07-16.md`) to avoid re-deriving what is already built and to
precisely locate what is genuinely untouched.

---

## HEADLINE

**Not a contradiction — a real, previously-unexamined GAP, and it is separable from the interference-avoidance
question we already correctly closed.** The biology decomposes "consolidation" into at least five distinct
functions with different triggers, different neural loci, and different currencies. This project's already-landed
ingest-gate work (schema-fit + surprise + recurrence, decision-tree routing to FAST/SLOW/DISCARD/HOLD) is a
faithful, well-evidenced implementation of exactly ONE of Tse/SLIMM's two schema-consolidation sub-functions — the
fast congruency-gated **write-time integration of new items** into existing structure. It does **not** implement,
and was never designed to implement, the biologically distinct function of **revisiting and re-filing OLD,
already-consolidated memories** when new information recontextualizes them. That second function is real, is
supported by a separate literature (hippocampal reconsolidation, prediction-error-at-reactivation, hierarchical
schema restructuring), and is genuinely absent from a single-pass-exact-write architecture whose only per-item
gate fires once, at the new item's own arrival. This is the gap. Whether it is a *hard problem* or a place the
substrate can beat the brain depends on WHY biological reconsolidation is slow/costly/risky — and the literature
answer is that its cost is a direct consequence of the brain's shared/overlapping/distributed storage substrate
(the same root cause as catastrophic interference), which a glass-box exact-addressed store does not have. The
trigger-DETECTION problem (deciding *what* needs reorganizing and *when*) is a separate, still-open, genuinely
hard piece that exact addressing does not solve by itself.

P_deflated (verdict + recommended cell, novel-synthesis capped): **0.42** — see calibration section.

---

## (a) Full function inventory of consolidation, biology-first, each scored COVERED / GAP against our architecture

### (a1) Interference-avoidance / capacity relief — ALREADY EVALUATED, closed as WRONG-CURRENCY / NOT-NEEDED

McClelland, McNaughton & O'Reilly 1995 (*Psychological Review* 102:419-457); McCloskey & Cohen 1989. The CLS
dual-route (hippocampal fast, cortical slow-interleaved) exists to solve **catastrophic interference**: a single
fast learner overwrites overlapping weights encoding prior items when new, overlapping items are trained into the
*same shared substrate*. Our prior route-closure (`research_cls_stc_currency_wrong_regime_2026-07-16.md`) already
established this is the correct biological reading (not a same-limitation mismeasurement) and that our
distributed-but-exact store exhibits graceful, not catastrophic, crosstalk — so the *specific problem this CLS
route solves* does not exist in the same form on our substrate, contingent on the crosstalk-graceful property
holding at scale. **Status: COVERED-BY-ARCHITECTURE (not needed), contingent — this verdict stands and is NOT
reopened by this note.**

### (a2) Schema integration / reorganization — SPLITS INTO TWO SUB-FUNCTIONS, ONE COVERED, ONE GAP

This is the literature's single most important nuance for this drill, and it resolves the "contradiction" framing
directly: **Tse/SLIMM-style schema consolidation is fundamentally about how NEW information gets filed, not about
rewriting OLD memories.** Tse et al. 2007 (*Science* 316:76-82) and Tse et al. 2011 (*Science* 333:891-895): once
a stable schema exists (built from weeks of prior learning), a **single novel schema-consistent item** becomes
hippocampus-independent within ~48h instead of weeks, driven by mPFC immediate-early-gene activation. van
Kesteren, Ruiter, Fernandez & Henson 2012 (SLIMM, *Trends in Neurosciences* 35:211-219): mPFC computes a
congruency/"resonance" signal and, when high, **down-gates hippocampal engagement and routes the new item directly
to fast cortical integration**; the trigger is **congruency detection** (does this new item fit an existing
schema), not prediction-error/mismatch — items that violate the schema instead engage different circuitry
(anterior cingulate; Wang, Tse & Morris 2012, *Learning & Memory* 19:315-318).

**Sub-function (2a) — fast write-time integration of schema-congruent new items: COVERED.** This project's
already-landed ingest-gate design (`research_brain_foundation_ingest_gate_consolidation_loop_2026-07-15.md`,
Section 4) is a structurally faithful implementation of exactly this: `schema_fit(e) >= SCHEMA_FIT_MIN` routes a
new candidate to FAST-TRACK direct fold-in (no full re-fit needed), below-threshold routes to SLOW-TRACK
(interleaved re-fit) — this is the mPFC congruency-gate, reused as the write-time router for new items. The
follow-up drill (`research_consolidation_gate_signal_mechanism_and_integration_2026-07-16.md`) further confirmed
the schema-fit signal must be **pairwise/relational** (specific configuration, not node-generic familiarity) —
matching the O'Reilly & McClelland 1994 CA3 attractor-basin mechanism and Tse's own operationalization (the
specific flavor-place *pairing*, not either element's individual familiarity). **This function is genuinely
covered, not merely superficially named** — the mechanism, the trigger (congruency of the specific new
configuration), and the routing consequence (bypass slow path) all match.

**Sub-function (2b) — reorganization of OLD, already-consolidated memories when new information recontextualizes
them: GAP.** This is functionally and evidentially distinct from (2a), and is the biological basis of the "whale"
example in the task. Direct evidence this is a real, separate process, not a restatement of (2a):
- Zeithamova & Preston 2012 (*Neuron* 75:168-179): OLD, related memories are **reactivated** during new,
  overlapping learning, and the degree of reactivation predicts subsequent inference — the old trace is revisited,
  not left untouched while a new link is merely appended.
- McKenzie et al. 2014 (*Neuron* 83:202-215): hippocampal ensembles **reorganize into new hierarchical "neural
  schemas"** as related memories accumulate — existing representations are restructured, not just supplemented.
- Sinclair, Manalili, Brunec, Adcock & Barense 2021 (*PNAS* 118:e2117625122): **prediction error at retrieval
  disrupts ongoing hippocampal pattern continuity and licenses updating of the OLD memory** — this is a genuine
  reconsolidation-style event, gated by a mismatch signal computed when the old memory is *reactivated by new,
  conflicting information*, not by the new item's own congruency to a schema.
- Sinclair & Barense 2018 (*Learning & Memory* 25:369-381, review): synthesizes this as prediction-error-driven
  episodic memory reconsolidation — a named, distinct literature from Tse/SLIMM's fast-integration-of-new-items
  account.

**Neither of this project's two deep ingest-gate drills (2026-07-15, 2026-07-16) contains any trigger, mechanism,
or design element that revisits an already-consolidated OLD record.** `insert_entity`/`compose_entity` are
append-only; the ingest-gate decision tree (`research_brain_foundation_ingest_gate_consolidation_loop_2026-07-15`,
Section 4) is evaluated once, on the new candidate's own arrival, against the *current* fitted `(X,D)` — it never
asks "does this new item imply something already-stored elsewhere is now wrong." **This is the genuine, confirmed
architectural gap.** (Full detail and reconcile-or-refute verdict in Section (b)/(c) below.)

### (a3) Gist / generalization extraction (semanticization) — LIKELY COVERED-BY-DESIGN, one open verification

Winocur & Moscovitch's Trace Transformation Theory and Nadel/Moscovitch's Multiple Trace Theory: episodic traces
are progressively transformed into semantic, decontextualized "gist" representations over consolidation, with some
detail lost while central/shared structure is retained and generalized. McClelland/Kumaran-Hassabis-McClelland
frame gist-extraction as the **product** of the same slow interleaved-integration process that solves interference
— no source we found treats gist-extraction as a mechanistically separate process requiring its own dedicated
machinery; it is the emergent output of integrating many episodes into shared, overlapping cortical structure.
**Minimum-data caveat, directly relevant to our architecture:** building a schema/gist categorization in the first
place requires statistical regularity across MANY prior episodes (a corpus, not one event) — but Tse 2007
demonstrates that, given an EXISTING schema, assimilating one new *consistent* instance requires only a single
exposure. **Mapping:** if our `schema_fit`/`reachability_audit` computation is queried against the CURRENT, live,
continuously-growing graph state at every write (rather than against a fixed, hand-authored, frozen ontology),
then gist-sensitivity is structurally ongoing and emergent by construction — every new item's fit-check is already
being scored against whatever generalized structure the graph has accumulated so far, without needing a dedicated
offline "extract the gist now" pass the way sleep-replay does. **This is plausible and likely true given the
project's description of schema-fit as a live reachability/pairwise-structure computation, but was not directly
re-verified in this drill** (would need to confirm `reachability_audit.py`/`schema_fit` is computed against
live `(X,D)`/graph state, not a static snapshot) — flagged as a cheap verification, not assumed. **Status:
LIKELY-COVERED, one verification step outstanding, not the crux of this note.**

### (a4) Creative recombination / relational inference via replay — LIKELY COVERED-BY-DESIGN (different mechanism,
same function), with an honest open seam in the biology itself

Ellenbogen et al. 2007 (*PNAS* 104:7723-7728): human transitive-inference task — subjects tested immediately after
learning premise pairs perform at chance on inferred (never-directly-taught) relations; after sleep, performance
on the SAME inferred relations rises above chance, while accuracy on the directly-trained premise pairs themselves
does not change. Wagner et al. 2004 (*Nature* 427:352-355): sleep roughly doubles explicit-rule discovery in a
hidden-structure task. **The mechanistic locus is a genuine, unresolved seam in the literature itself** (confirmed
by this drill's lit-scan, not just our reading): Kumaran & McClelland 2012 (*Psychological Review* 119) propose
inference is computed **at retrieval time**, via recurrent pattern-completion/associative chaining across
separately-stored, intact premise traces — the relational structure was latently present at encoding, and sleep's
role is to **stabilize/disambiguate the individual noisy traces** well enough for this retrieval-time computation
to converge reliably. Newer generative-replay accounts (2022-2023) instead propose traces are **actively
recombined/integrated during offline replay itself**. No study cleanly separates these two loci experimentally.
**Mapping:** whichever account is correct in biology, both converge on the SAME underlying bottleneck being solved
— noisy/degraded individual traces that need to be cleaned up before a multi-hop retrieval-time computation can
reliably chain across them. **Our substrate's traces are exact by construction (single-pass-exact-write, no
decay/noise accumulation)** — the specific problem sleep is solving (denoising traces enough for retrieval-time
recombination to work) does not exist for us in the same form, because there is nothing to denoise. Multi-hop
relational inference (transitive-style chaining) is directly computable at query time via the existing
bind/unbind + resonator completion machinery on exact, never-degraded stored premises — this is the Kumaran &
McClelland retrieval-time account, made trivial by exact storage rather than requiring a sleep-equivalent
stabilization step. **Caveat, explicitly NOT part of the correctness gap:** if multi-hop/transitive queries become
expensive to recompute fresh at every query as the store grows, there may be a legitimate PERFORMANCE argument
for caching/precomputing some multi-hop relations offline — a cost-engineering question, not a capability gap, and
should not be conflated with the schema-reorganization crux in (b)/(c). **Status: LIKELY-COVERED (the underlying
problem sleep solves is structurally absent from exact storage); caching is a separate, lower-priority, purely
economic question.**

### (a5) Memory selection / pruning / active forgetting — NOT YET NEEDED (deferred, contingent on future capacity
pressure), partially anticipated in existing design

Tononi & Cirelli's Synaptic Homeostasis Hypothesis (sleep-dependent global synaptic downscaling, framed primarily
as renormalization of a capacity-limited, energetically-costly substrate, not selective semantic pruning); active
forgetting via Rac1/cofilin-driven dopaminergic "forgetting cells" (Drosophila mushroom body; Berry,
Cervantes-Sandoval, Davis and colleagues) and adult-neurogenesis-driven forgetting (Frankland & Josselyn, *Science*
2014) — both are mechanisms that exist because biological storage capacity is fundamentally, physically limited
(finite synapses, shared/overlapping weight substrate). The clearest documented SELECTIVITY signal is not a
generic "importance scorer" applied to the whole store but a **temporal-proximity rescue** mechanism (synaptic
tag-and-capture / behavioral tagging — already covered in the prior CLS/STC route-closure note): a salient/novel
event occurring near-in-time to a weak trace can rescue it from decay, not a scan-and-delete-the-unimportant
process. **Mapping:** our architecture is described as a GROWING, single-pass-exact-write foundation, not a
fixed-capacity shared-weight substrate — the specific pressure that necessitates biological pruning (finite,
shared, energetically-costly synapses) is not structurally present in the same form (storage growth cost is
closer to linear-in-content than exponential-collision-in-shared-weights). This project's own ingest-gate design
already anticipates a *provisional-tier* version of this (`research_brain_foundation_ingest_gate_consolidation_loop
_2026-07-15.md` Step 4, "HOMEOSTASIS" — provisional candidates failing the gate for N cycles age out/discard), but
this only touches never-fully-consolidated candidates, not already-foundationalized records. **Status:
NOT-YET-NEEDED / deferred — a real function, but gated on future capacity/retrieval-quality pressure (a DIFFERENT,
already-flagged research thread: DG-style addressing crosstalk caps at large N), not part of this crux.**

---

## (b) THE CRUX — schema reorganization of already-written memories

### What triggers it, and who decides (biology)

The convergent trigger across the Zeithamova/McKenzie/Sinclair reconsolidation literature and the classical
reconsolidation-boundary-conditions literature (Nader, Schafe & LeDoux 2000, *Nature* 406:722-726; Pedreira,
Perez-Cuesta & Maldonado 2004; Sevenster, Beckers & Kindt human fear-conditioning studies) is **prediction-error at
reactivation**: an old memory must first be REACTIVATED (by a retrieval cue that overlaps with new incoming
information), and the new information must generate a genuine MISMATCH against what the old memory predicted —
simple re-exposure/reactivation with no informational surprise leaves the old memory stable (does not
destabilize/update it). This prediction-error-as-trigger account is **necessary but contested as *sufficient*** —
there are published, direct replication failures (Frontiers in Behavioral Neuroscience 2017; Scientific Reports
2022) showing the same nominal prediction-error manipulation sometimes fails to destabilize a memory; strength/age
of the old memory and arousal state also gate whether reactivation triggers reorganization. **Selectivity is
real and well-supported**: reactivating one component of a compound memory can destabilize just that component
while sparing co-stored associations (though some "bleed" to co-active traces is a documented, only partially
quantified risk); older/stronger memories require a bigger mismatch to destabilize than younger/weaker ones
(*Learning & Memory* 2009). **Cost is universally and unambiguously framed as HIGH in the biology**: destabilization
opens a genuinely labile, protein-synthesis-dependent window during which the memory is vulnerable to disruption
or loss if restabilization fails (Sara 2000; Nader & Hardt 2009, *Nature Reviews Neuroscience*; Lee, Nader &
Schiller 2017, *Trends in Cognitive Sciences* 21:531-545) — no paper in this literature frames reconsolidation as a
cheap, surgical, low-risk edit. It is consistently described as an all-or-nothing risky operation, not incremental
targeted patching.

### Is this a genuine architectural gap for a growing foundation?

**Yes, and it is separable and distinct from the interference-avoidance question we already correctly closed.**
The two functions have different triggers (capacity/interleaving-driven vs. prediction-error-at-reactivation),
different literatures (CLS/McClelland-McNaughton-O'Reilly vs. Nader/reconsolidation), and different currencies
(retention-under-continued-training vs. correctness-of-an-existing-record after new, conflicting information
arrives). Rejecting the first does not logically touch the second, and adopting DG/CA3 separation+addressing
(which governs how items get STORED and RETRIEVED) does not by itself provide any mechanism for revisiting
something already stored. **Single-pass-exact-write, by construction, never re-examines an old record once
written** — the current ingest-gate design (Section a2, sub-function 2a) only evaluates the NEW candidate's own
fit; it has zero mechanism, trigger, or hook for asking "does this new item imply something already-consolidated
elsewhere is now stale, miscategorized, or wrong." This is a real, confirmed, previously-unexamined gap, not
resolved by anything already built or by the prior CLS/STC route-closure.

### Could a glass-box substrate do this CHEAPLY where the brain cannot?

**Plausibly yes for the EDIT itself, but NOT for the harder trigger-detection half of the problem, which remains
genuinely open.** The reason biological reconsolidation is slow, risky, and effortful is that the brain must
destabilize and carefully re-stabilize a memory trace living in a SHARED, DISTRIBUTED, OVERLAPPING weight
substrate — exactly the same root constraint (shared, overlapping storage) that makes catastrophic interference a
problem in the first place, and exactly the constraint our prior route-closure argued our exact-addressed store
does not share. If a stored record's location is EXACTLY addressable (per the project's own DG/CA3-style
addressing work,
`research_learned_noise_robust_addressing_page_routing_2026-07-16.md`), then updating that record's fields or
schema-membership does not require a slow, careful, collateral-damage-avoiding destabilization process — it can
in principle be a direct, targeted, exact edit at that address, with no risk to unrelated records (which the brain
cannot do, because its storage is not addressable this way). This is exactly the kind of native-affordance
advantage flagged in the two-frontiers framing (brain needs a costly route to solve a problem our substrate may
not structurally have). **However**, exact addressing only solves the "how to edit without collateral damage"
half of the problem. It does **not** solve the other, harder half: **deciding WHAT needs re-examination and WHEN**
— the trigger-detection problem. The brain's answer relies on associative reactivation being automatic and
cheap (a retrieval cue naturally reactivates overlapping traces because storage is content-addressable and
distributed) — mismatch is only ever checked for what gets reactivated in the course of ordinary retrieval, not
computed by exhaustively re-scanning the whole memory store. A glass-box substrate does not get this for free:
exact addressing tells you how to locate and edit a SPECIFIC known record cheaply, but it does not tell you WHICH
existing records a brand-new incoming item might contradict, without either (i) an expensive exhaustive
consistency check against the whole store on every write, or (ii) some targeted, cheap candidate-generation step
(e.g., reusing the existing schema-fit/reachability query — which already retrieves the locally-relevant
neighborhood of an incoming item as a side effect of computing its own congruency score — to ALSO check that
neighborhood for now-contradicted old records). Option (ii) is cheap because it is a reuse of machinery already
built and already paid for (the schema-fit pairwise/reachability query), not a new expensive mechanism — but this
is an unverified, untested hypothesis, not yet a demonstrated capability. **Net read: the EDIT side of
reorganization is plausibly a place we can do better than the brain (address-based targeted overwrite vs.
distributed careful destabilization); the TRIGGER-DETECTION side is a genuinely open problem that borrows
plausibility from already-built machinery but has never been tested for this specific use.**

---

## (c) Reconcile-or-refute verdict

**Rejecting consolidation-as-interference-avoidance IS separable from, and does NOT logically cover, consolidation-
as-reorganization.** These are different functions in the biology (different triggers, different literatures,
different currencies) and different functions in our architecture (the interference-avoidance route-closure is
about storage/write dynamics under continual training load; the reorganization gap is about correctness of
already-written records after new, recontextualizing information arrives). **Verdict: NOT a contradiction — a
genuine, previously-unexamined GAP, confirmed real by this drill, and NOT resolved by any of (i) the CLS/STC
route-closure, (ii) the DG/CA3 addressing adoption, or (iii) the already-landed ingest-gate design (which only
covers fast/slow write-time integration of NEW items, sub-function 2a, not revisiting OLD records, sub-function
2b).** The gap should be tested directly rather than assumed away by either the prior rejection (does not apply)
or by optimism about exact-addressing (solves only half the problem).

### Recommended cell (pointer-only, inline per no-routing-files discipline — this section IS the hand-off; no
separate `exp_dev_handoff_*.md` file is filed)

**Anchor candidate:** `exp_ingest_schema_reorg_conflict_probe_v1` (name is a suggestion, not binding on exp_dev).

**Why this cell, why now:** it is the cheapest test of the one function this drill confirms is genuinely
untested — does staleness in already-consolidated records actually cause measurable downstream error on THIS
substrate's specific read path, and if so, is a targeted exact-reindex cheaper and more effective than doing
nothing (current behavior) or than the coarse alternative already implicitly available (a full periodic re-fit of
`(X,D)`, which touches everything diffusely and expensively rather than the brain's selective, targeted profile).

**Mechanism sketch (ablation ladder, reusing already-certified primitives — no new mechanism required):**
1. Build a foundation with an established schema for entity X (e.g., several supporting edges consistent with
   category/schema A — analogous to the "fish" schema in the whale example), fully write-time-consolidated per the
   existing ingest-gate FAST-TRACK path.
2. Insert a later, recontextualizing item about X that conflicts with schema A (e.g., implies category/schema B),
   through the existing ingest gate exactly as-is today (Arm 1: NO-REORGANIZATION baseline). The new item is
   folded in per today's design; nothing about X's prior stored structure is touched or re-examined.
3. Arm 2 (TARGETED EXACT REORG): on ingest of the recontextualizing item, reuse the existing schema-fit /
   reachability query (already computed as part of congruency-scoring the new item) to retrieve X's directly
   dependent OLD records/cross-links; run a cheap consistency check against the new item; if conflict is detected,
   perform a targeted exact re-index/overwrite of ONLY the directly-implicated old records (not a full re-fit).
4. Arm 3 (control): FULL PERIODIC RE-FIT — re-run the existing whole-graph slow-track SGD re-fit over all edges
   (old + new) as the coarse, already-available alternative, to establish whether the currently-existing mechanism
   already implicitly handles this (diffusely, expensively) or not.
5. Metric: downstream query/inference accuracy on schema-dependent queries touching X (and, ideally, other
   entities sharing X's old schema membership) AFTER the schema-shift, across all three arms; also measure the
   REORG COST (number of records touched / compute) for arm 2 vs. arm 3, to test whether targeted exact reindexing
   is genuinely cheaper than the coarse full re-fit alternative (the core "native affordance beats brain-forced-
   cost" hypothesis).

**Falsifiable predictions (deflated per lit-scan calibration; HARD-PASS/HARD-FAIL mandatory):**
- **HARD-PASS:** Arm 1 (no-reorg) shows a measurable accuracy DROP on schema-dependent downstream queries touching
  X relative to a same-schema-consistent control (confirms staleness is a real, not merely theoretical, problem
  for our specific read path) AND Arm 2 (targeted exact reorg) recovers >= 80% of that accuracy drop AND Arm 2's
  reorg cost is bounded (scales with the number of directly-implicated old records, NOT with total store size) AND
  Arm 2's cost is materially lower (e.g. >= 5x cheaper) than Arm 3's full re-fit cost for an equivalent accuracy
  recovery. This jointly confirms: (i) the gap is real, (ii) targeted reuse of existing schema-fit machinery as a
  trigger-detector is a viable, cheap solution, (iii) the native-affordance advantage over the brain's costly route
  materializes in practice, not just in principle.
- **HARD-FAIL:** Arm 1 (no-reorg) ties the same-schema-consistent control on downstream accuracy (i.e., staleness
  in already-written records does NOT actually propagate into measurable query error on this substrate's specific
  read path — e.g., because reads always do a fresh exact lookup rather than relying on any cached schema-
  membership derivative, meaning there is structurally nothing to go stale) — this would mean the reorganization
  function is MOOT for this architecture's actual read path, a real and useful negative, not a failure to chase
  further. OR: Arm 2's targeted trigger-detection cost is NOT bounded (scales with store size, e.g. because the
  reused schema-fit/reachability query itself is not local/cheap at the relevant scale) — this would mean the
  native-addressing advantage does not materialize as hoped, and the trigger-detection half of the problem remains
  genuinely open and costly even on this substrate.
- **MIDDLE:** Arm 1 shows a real but small accuracy drop, and/or Arm 2 recovers some but not most of it, and/or
  Arm 2's cost advantage over Arm 3 is real but modest (<5x) — informative, route to a v2 tuning the
  candidate-generation step (which old records get flagged for re-examination) before a larger claim.

**Pre-registered HARD-FAIL localization guidance:** if Arm 1 ties the control (no measurable staleness effect),
that is the single most likely outcome given this project's exact-storage discipline and should be treated as a
legitimate, valuable negative — it would mean the brain's reorganization function, unlike interference-avoidance,
genuinely doesn't transfer as a NEED (not merely as a currency mismatch) for an architecture whose reads never
rely on stale cached derivatives. Distinguish this cleanly from the OTHER possible failure (trigger-detection is
real but expensive) before concluding either "no gap" or "gap confirmed but unsolved."

**Context pointers (files, not summaries):**
- `notes/research_cls_stc_currency_wrong_regime_2026-07-16.md` — the interference-avoidance route-closure this
  note explicitly does NOT reopen; cite as the separable, already-settled sibling question.
- `notes/research_learned_noise_robust_addressing_page_routing_2026-07-16.md` — the DG/CA3-analog addressing
  machinery whose exact-addressability is the load-bearing assumption behind the "cheap targeted edit" half of
  this note's hypothesis; reuse its router/completer primitives for Arm 2's exact re-index step.
- `notes/research_brain_foundation_ingest_gate_consolidation_loop_2026-07-15.md` — the existing ingest-gate design
  (schema-fit/surprise/recurrence decision tree); Arm 2 reuses its schema-fit/reachability query as the
  trigger-detection candidate-generator rather than building a new one.
- `notes/research_consolidation_gate_signal_mechanism_and_integration_2026-07-16.md` — confirms schema-fit must be
  pairwise/relational (not node-generic); Arm 2's conflict-check should reuse this corrected, pairwise form, not
  the original node-aggregate percentile.
- `hdlab/additive_map.py` (`insert_entity`, `compose_entity`, `score_all`) — the append-only write primitives whose
  lack of any "revisit old entity" hook is the concrete, in-code confirmation of the architectural gap identified
  in Section (b).

**Autonomy note:** exp_dev owns exact schema-shift construction, exact conflict-detection threshold, exact
candidate-generation radius (how many hops of X's neighborhood get checked), and exact cost-accounting method for
the Arm 2 vs. Arm 3 comparison — this note fixes the falsifiable thresholds, the ablation ladder, and the
mechanism sketch, not the implementation details.

---

## Cross-thread synthesis

- Directly extends and does NOT reopen `research_cls_stc_currency_wrong_regime_2026-07-16.md`: that note closed
  the interference-avoidance function specifically; this note confirms that closure is scoped correctly and
  identifies the separate, still-open reorganization function as the genuine remaining question the user's
  contradiction-check correctly flagged.
- Directly builds on `research_learned_noise_robust_addressing_page_routing_2026-07-16.md`: the DG/CA3-style exact
  addressing that note certifies is precisely the affordance that makes the EDIT half of reorganization plausibly
  cheap on our substrate where it is costly for the brain — this note is the first to name that specific downstream
  use of exact addressing.
- Reconciles with, and sharpens, the two ingest-gate drills
  (`research_brain_foundation_ingest_gate_consolidation_loop_2026-07-15.md`,
  `research_consolidation_gate_signal_mechanism_and_integration_2026-07-16.md`): both are confirmed, on direct
  re-read, to cover ONLY sub-function 2a (fast write-time integration of new schema-congruent items) and contain
  zero mechanism touching sub-function 2b (revisiting old records) — this is a precise, evidence-based scoping of
  what those substantial prior investments do and do not already solve, avoiding both under-crediting them (they
  are NOT irrelevant to consolidation) and over-crediting them (they do NOT already close this note's gap).
- Consistent with the two-frontiers framing (brain-faithful world first, native-substrate-affordance world as a
  later, deliberate thrust, not an escape hatch): this note's recommended cell is explicitly structured to test
  the brain-faithful NEED (does staleness cause real error) before assuming the native EDIT mechanism is the
  answer — Arm 1 vs. control is the brain-faithful-need test; Arm 2 vs. Arm 3 is the native-vs-brain-cost test.
- The "ability vs. accuracy" and "retrieval-time computation vs. offline recombination" seams flagged in Question A
  of the third lit-scan (sleep/replay-driven inference) are consistent with, and reinforce, this project's broader
  emerging pattern (per `research_cls_stc_currency_wrong_regime_2026-07-16.md`'s cross-thread note) that
  single-shot/dense test harnesses can undermeasure brain-analog mechanisms whose function is amortized over
  sequences — but this note's (a4) finding is the reverse and equally important case: some brain mechanisms
  (sleep-driven trace stabilization) solve a problem (noise accumulation) that is structurally ABSENT from an
  exact-write substrate, so the mechanism's absence is not a gap at all, just a non-transferable solution to a
  non-existent local problem. Distinguishing "gap" (a2, sub-function 2b) from "solved-by-construction" (a4) in the
  same function inventory is itself the main analytical contribution of this note.

## Substrate-product implications

- Do not treat the prior CLS/STC interference-avoidance closure as blanket license to ignore consolidation
  research generally — this note demonstrates the biology decomposes into functions with genuinely different
  verdicts (COVERED / GAP / NOT-YET-NEEDED / LIKELY-COVERED) and each must be checked on its own terms, exactly as
  the always-on "brain-check every negative, same-limitation vs. wrong-currency" discipline requires.
- If the recommended cell HARD-PASSes: the product story becomes "the foundation can correct itself when new
  information recontextualizes something already known, cheaply and precisely, via exact addressing" — a
  materially different and stronger claim than "the foundation never forgets" (which follows trivially from
  exact-write) because it additionally claims the foundation stays CORRECT as the world it models changes, not
  merely complete.
- If it HARD-FAILs via the "ties the control" route (staleness doesn't propagate to query error): this is a
  genuinely useful negative — it means the exact-read-path architecture already sidesteps the entire reorganization
  problem by construction (every read is fresh, nothing is cached-and-therefore-stale), and no further investment
  in reorganization machinery is warranted unless/until the read path changes (e.g., if performance pressure later
  forces caching of derived/aggregate views, at which point this exact question should be re-asked).
- If it HARD-FAILs via the "trigger-detection is expensive" route: the product should NOT claim self-correcting
  reorganization without a real solution to the candidate-generation problem — flag reorganization as a known,
  named, deliberately-deferred limitation rather than silently absent.

## Calibration reasoning (P_deflated = 0.42)

Raw confidence in the BIOLOGY claims (Tse/SLIMM fast-integration mechanism and its congruency trigger;
Zeithamova/McKenzie/Sinclair reconsolidation-of-old-memory evidence; the prediction-error-at-reactivation trigger
and its necessary-but-contested-sufficient status, including documented replication failures; the
uniformly-costly/risky framing of biological reconsolidation; the ability-vs-accuracy and retrieval-time-vs-
offline-recombination seams in the sleep/inference literature) is high (~0.80-0.85) — cross-verified across 3
independent lit-scans plus direct re-read of two substantial internal notes, with contested points explicitly
flagged rather than smoothed over (reconsolidation-boundary-condition replication failures; MTT vs. standard
consolidation debate; retrieval-time vs. offline-recombination seam). Standard lit-scan calibration penalty
(-0.15 to -0.25) brings this to ~0.60-0.65 for the biology function-inventory and separability argument alone
(the (a)/(b) analysis, and the "not a contradiction, a separable gap" verdict in (c)). The SUBSTRATE-MAPPING claim
— that exact addressing makes the EDIT half of reorganization genuinely cheap, that the existing schema-fit query
can double as a cheap trigger-detector, and that the recommended cell will show the predicted HARD-PASS pattern —
is the novel-synthesis component, capped at 0.50 per the mandatory novel-synthesis cap, then further discounted to
0.42 because: (i) zero direct empirical precedent exists on this substrate for EITHER half of this problem (no
cell has ever tested whether old-record staleness causes measurable error, nor whether a targeted reindex is
cheaper than the existing full-re-fit alternative); (ii) the trigger-detection reuse-of-schema-fit hypothesis is
plausible but genuinely untested — the schema-fit query was designed and validated for a different purpose (scoring
a new item's own congruency), and repurposing it as a bidirectional conflict-detector for OLD records is an
unverified extension, not a proven capability; (iii) there is a real chance the HARD-FAIL "ties the control" route
is what actually happens (a legitimate, not-unlikely outcome given this project's exact-read-path discipline),
which would be a valuable negative but means the P for the HARD-PASS-shaped claim specifically should not be
inflated by hope that the harder, more interesting outcome is the true one.

## Citations (verified count: 24 distinct external primary/secondary sources across 3 lit-scans, cross-checked
with no contradicting source found on any point represented as well-established; contested points flagged inline
above, not smoothed over; plus 6 internal cross-thread notes/code files)

**Schema-driven consolidation and reorganization:** Tse et al. 2007, *Science* 316:76-82; Tse et al. 2011,
*Science* 333:891-895; van Kesteren, Ruiter, Fernandez & Henson 2012, *Trends in Neurosciences* 35:211-219
(SLIMM); Wang, Tse & Morris 2012, *Learning & Memory* 19:315-318; Bein, Reggev & Maril (hippocampal-mPFC coupling
and prior knowledge, Cerebral Cortex/Neuropsychologia-adjacent series); Zeithamova & Preston 2012, *Neuron*
75:168-179; McKenzie, Frank, Kinsky, Porter, Riviere & Eichenbaum 2014, *Neuron* 83:202-215; Sinclair, Manalili,
Brunec, Adcock & Barense 2021, *PNAS* 118:e2117625122; Sinclair & Barense 2018, *Learning & Memory* 25:369-381;
prediction-error/aversive-learning salience-schema-network fMRI study (Cerebral Cortex, 2022).

**Semanticization/gist and forgetting/pruning:** Winocur & Moscovitch (Trace Transformation Theory); Nadel,
Samsonovich, Ryan & Moscovitch 2000, *Hippocampus* (Multiple Trace Theory); McClelland, McNaughton & O'Reilly
1995, *Psychological Review* 102:419-457; Kumaran, Hassabis & McClelland 2016, *Trends in Cognitive Sciences*
20:512-534; Tononi & Cirelli (Synaptic Homeostasis Hypothesis, multiple years); "Why I Am Not SHY" reply
literature; Drosophila dopaminergic forgetting-cell / Rac1-cofilin literature (Berry, Cervantes-Sandoval, Davis
and colleagues; *Neuron* 2012); Frankland & Josselyn, Akers et al. 2014, *Science* (adult-neurogenesis-driven
forgetting); synaptic tag-and-capture / behavioral tagging review (*Trends in Cognitive Sciences*).

**Sleep-replay inference and reconsolidation triggers:** Ellenbogen, Hu, Payne, Titone & Walker 2007, *PNAS*
104:7723-7728; Wagner, Gais, Haider, Verleger & Born 2004, *Nature* 427:352-355; Kumaran & McClelland 2012,
*Psychological Review* 119; generative-replay/hippocampal-neocortical interaction models (*Nature Human
Behaviour* 2023; *PNAS* 2022); Nader, Schafe & LeDoux 2000, *Nature* 406:722-726; Pedreira, Perez-Cuesta &
Maldonado 2004; Sevenster, Beckers & Kindt (human fear-conditioning prediction-error boundary-condition studies);
Frontiers in Behavioral Neuroscience 2017 (reconsolidation boundary-condition replication failure); Scientific
Reports 2022 (unsuccessful reconsolidation replication); Sara 2000; Nader & Hardt 2009, *Nature Reviews
Neuroscience*; Lee, Nader & Schiller 2017, *Trends in Cognitive Sciences* 21:531-545; *Learning & Memory* 2009
(selective destabilization of older/stronger memories).

**Internal (re-read, not re-derived):** `notes/research_cls_stc_currency_wrong_regime_2026-07-16.md`;
`notes/research_learned_noise_robust_addressing_page_routing_2026-07-16.md`;
`notes/research_brain_foundation_ingest_gate_consolidation_loop_2026-07-15.md`;
`notes/research_consolidation_gate_signal_mechanism_and_integration_2026-07-16.md`; `hdlab/additive_map.py`
(referenced, not re-read in full this cycle — architecture description taken from the two ingest-gate notes'
direct quotes of `insert_entity`/`compose_entity`/`score_all`).
