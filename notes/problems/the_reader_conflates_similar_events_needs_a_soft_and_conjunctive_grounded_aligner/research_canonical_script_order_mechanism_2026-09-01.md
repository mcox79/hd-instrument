# Research drill: HOW THE BRAIN BUILDS CANONICAL EVENT/SCRIPT ORDER

Date: 2026-09-01. Author: hdi_research (Director), online-literature drill dispatched by the SOLVER on this problem.
Scope: ONLINE literature only. This file is advisory to the SOLVER; nothing here is measured on our corpus. Every "should/would" is a DESIGN HYPOTHESIS pending the solver's measurement. Lit-scan calibration penalty applied (P deflated 0.15-0.25; novel-synthesis P capped at 0.50).

## What this drill INHERITS (measured; not re-derived)
- The reasoning read-out works: `hdlab.transitive_ordering` (a cognitive-map magnitude line) beats a shuffled-order twin CI-sep on isolated transitive inference.
- Event ALIGNMENT is not the wall: conjunctive role-filler identity + a discrete path/particle separates similar events ~0.98 at the type level (ablation/scramble CI-sep). The brief's soft-AND PRODUCT kernel is refuted (product ~= additive ~= coarse).
- THE WALL is the CANONICAL-ORDER signal. Learning order from CO-OCCURRENCE / told-order across ~13 narratives per scenario caps before/after at ~0.59 (+0.07 over shuffle). This route is EXHAUSTED: pairwise-precedence + transitive fill-in (0.591) beats a positional-mean prior (0.548); ~67% of eval pairs have no direct consensus and are answered by transitive inference; p6's aggregator ablation (tally / precision-weighted / successor-representation) all PLATEAUED. Co-occurrence statistics are done. A DIFFERENT, brain-faithful signal is needed.

Substrate prior-work check (`experiment_index.py query`): 0 matching cells for "canonical script event order enablement causal" and for "successor representation temporal community structure". No prior arc work on this mechanism. The sibling research file (`research_combination_rule_and_path_slot_2026-09-01.md`) covers the aligner KERNEL, a distinct question; no overlap.

---

## Q1 — HOW THE BRAIN ACQUIRES/REPRESENTS CANONICAL ORDER, WHICH MECHANISM DOMINATES, AND WHY CO-OCCURRENCE CAPS OUT

### The four candidates, weighed

**(a) Statistical / temporal-co-occurrence learning & the successor representation (SR).**
PINNED as a real hippocampal mechanism: the hippocampus performs statistical learning of temporal community structure (Schapiro, Turk-Browne, Norman & Botvinick 2016) and represents state as a temporally-discounted prediction of future states — the SR / predictive map (Stachenfeld, Botvinick & Gershman 2017; Dayan 1993). **But this is precisely the mechanism the solver has already exhausted, and the literature explains WHY it caps — mechanistically, not just empirically:**

1. **The SR is a GENERALIZATION device: it makes states with similar successors SIMILAR.** Dayan (1993) introduced the SR expressly "to facilitate generalization between states with similar successors." Schapiro (2016) confirms the neural signature: "states with similar successors were represented similarly" — hippocampal pattern similarity mirrored community structure. So a co-occurrence code actively pulls script events that occur together toward a shared community centroid. **This is not neutral to our problem — it is the SAME force that causes the reader to CONFLATE similar events.** Co-occurrence learning improves "these belong together" while ACTIVELY BLURRING "which came first."
2. **Temporal-context matching is SYMMETRIC.** Gershman, Moore, Todd, Norman & Sederberg (2012), "The successor representation and temporal context": a reinstated temporal context "will (symmetrically) match the contexts associated with items studied before AND after," and a simple local learning rule "can be made insensitive to the temporal order." The asymmetric (directional) component of an SR is the fragile part; under noise and few exposures it washes toward the symmetrized transition structure.

Net: a co-occurrence/SR signal is STRUCTURALLY STRONG on set-membership and STRUCTURALLY WEAK on direction. The observed +0.07-over-shuffle cap is the expected ceiling of this mechanism, not a tuning failure. This is a clean, PINNED explanation of the wall.

**(b) CAUSAL / GOAL-ENABLEMENT structure.** PINNED as the classical account of what FIXES script order: Schank & Abelson (1977). A script's actions are chained because "each action results in conditions that enable the next to occur; to perform the next act, the previous acts must be completed satisfactorily." Scenes carry entry conditions (preconditions) and results (effects): the mug must be obtained BEFORE you can pour. This is the candidate that RESOLVES the under-determination co-occurrence leaves behind (see verdict).

**(c) Replay-driven schema consolidation into mPFC/PMC.** PINNED: mPFC holds abstract event schemas that INCLUDE order — Baldassano, Hasson & Norman (2018): mPFC schematic patterns are "sensitive to overall script structure, such that temporally scrambled events evoked weaker schematic representations" (i.e., mPFC confers ordinality). Consolidation mechanism: Spens & Burgess (2024), "A generative model of memory construction and consolidation" — hippocampal replay trains a neocortical generative model; "schema-based distortions increase with consolidation," and follow-on work models consolidation as training autoregressive SEQUENCE models on hippocampal memories. **Interpretation (design-relevant): replay is a DENOISER/order-cleaner that AMPLIFIES whatever structural skeleton it is fed — it does not invent order from nothing.** If the skeleton is co-occurrence, replay sharpens a symmetric blur; if the skeleton is causal enablement, replay sharpens a directed chain. So (c) is a force-multiplier on (a) or (b), not an independent source of canonical order.

**(d) Temporal/tense/discourse cues.** PINNED but SECONDARY and largely a READ-OUT cue: comprehenders infer order from event dynamicity via a Figure-Ground principle — states are backgrounded before events (Marx & Wittenberg 2025, "Dynamicity Predicts Inferred Temporal Order…", Cognitive Science; "The State-Before-Event Inference Emerges Across Tenses", Open Mind 2025). Critically for us, the discourse literature carries the causality-vs-order distinction the brief flagged: **for CAUSAL events a mental model of temporal order already exists (it is read off the causal relation), whereas for arbitrarily-related events order must be CONSTRUCTED.** (The specific "Dixon 2019 causality != order" citation was not independently verified in this drill — flagged OUR-INVENTION on the exact reference; the underlying claim is well supported by the eventuality-type / dynamicity discourse work above.)

### Q1 VERDICT
**PINNED:** Canonical order is UNDER-DETERMINED by co-occurrence. Everyday scripts admit many valid told-orders and contain genuinely parallel/unordered steps; a symmetric, generalization-biased co-occurrence code (SR) cannot distinguish "co-present" from "precedes," which is exactly the measured cap. The mechanism that DOMINATES in fixing order for everyday scripts is CAUSAL / GOAL-ENABLEMENT structure (Schank & Abelson): an event's effect establishes the precondition of the next. Co-occurrence supplies membership; enablement supplies direction; replay/consolidation (mPFC) sharpens whichever skeleton it is given. Discourse/tense cues are a secondary read-out.

**OUR-INVENTION-UNDER-TEST:** that our specific corpus's residual is dominated by enablement-recoverable direction (measured next).

---

## Q2 — THE ENABLEMENT HYPOTHESIS, MADE CONCRETE

**Claim (PINNED at the cognitive/computational level):** script order is primarily fixed by goal-subgoal ENABLEMENT — each event's PRECONDITIONS and EFFECTS, where one event's effect enables the next's precondition.

How the brain represents preconditions/effects and chains them:
- **Event models carry the ingredients.** Event Segmentation Theory (Zacks, Speer, Swallow, Braver & Reynolds 2007; Reynolds, Zacks & Braver 2007) — working-memory event models contain "characters' goals, spatiotemporal information … and CAUSES of actions," and drive predictions of what comes next. Event boundaries are triggered by prediction error AND by shifts in goal/space/cause. So the brain segments and links events by their causal/goal structure, not just their surface co-occurrence.
- **Goal-subgoal enablement is a prefrontal hierarchy.** Botvinick, Niv & Barto (2009) — hierarchical RL: "options" (temporally-extended subroutines) terminate at SUBGOAL states; PFC represents option/subgoal identifiers; the current subgoal is decodable in vmPFC/insula. A subgoal's achievement (an effect/state change) is exactly what licenses the next option — the neural form of "effect enables next precondition."
- **The partial order.** In a plan, ONLY causally-dependent steps are ordered; independent steps are unordered (the classic partial-order-plan structure). This maps onto script cognition: obligatory-ordered pairs are the enablement-linked ones; free/parallel pairs are unconstrained.

**The testable prediction this yields for our corpus (OUR-INVENTION-UNDER-TEST, high-value):**
> The ANSWERABLE before/after pairs are exactly the causally-DEPENDENT (enablement-linked) pairs; the ~10-20% irreducible residual is the causally-INDEPENDENT (parallel) pairs, whose order is genuinely under-determined and SHOULD NOT be forced.

If true, this reframes the wall: the ceiling is not "our order signal is weak," it is "some pairs have no canonical order and the eval treats a free order as an error." The right move is (i) recover the causally-dependent pairs with an enablement signal, and (ii) ENUMERATE the residual as parallel/unordered and report it as irreducible rather than chasing it. This is directly measurable: tag each eval pair as enablement-linked vs independent (via the Q3 signal), and check whether accuracy on enablement-linked pairs is high while the residual concentrates in independent pairs.

**Calibration:** this is the most attractive hypothesis in the drill AND the one most at risk of over-fitting a story to a plateau. It must be a can-fail test: if enablement-linked pairs are NOT answered better than independent ones, the hypothesis is dead.

---

## Q3 — GLASS-BOX REPLICATION (no LLM at inference): the concrete enablement signal

**The signal to build:** an ENABLE-edge graph over the already-extracted conjunctive event types. Put a directed edge A -> B when A's EFFECT establishes (or supplies a token for) a PRECONDITION of B; then order the graph with the existing `transitive_ordering` read-out. This replaces the co-occurrence tally as the PREMISE source and keeps the proven integrator (see Q4).

**Method template from the literature (offline extraction is standard and pre-neural-LM):** ProPara / "Tracking State Changes in Procedural Text" (Dalvi, Huang, Tandon, Yih & Clark 2018, NAACL) tracks entity state with four operations — Move / Create / Destroy / no-change — and predicts a "dependency explanation graph between steps, which describes WHICH STEPS ENABLE WHICH other steps and how." NaRuto-style pipelines extract events + argument structure from narrative text and induce preconditions/effects. We do not need their neural inducers; we need the deterministic state-change skeleton, which spaCy can approximate offline.

**Minimal brain-faithful enablement features to extract deterministically (spaCy allowed, no LLM):**
1. **Object-availability rule (strongest, most reliable).** An event that ACQUIRES/PRODUCES object X (get, take, buy, pour-into, fill, open) must precede an event that USES/CONSUMES X (drink, eat, pour-from, close). Track possession via has/possess/get vs consume/use, and object identity via the conjunctive filler tokens already extracted. Mug-before-pour; ticket-before-board; ingredients-before-mix.
2. **Location gating.** be-at/enter-X precedes act-at-X; exit-X follows act-at-X. Detect enter/exit/go/arrive/leave + locative prepositional objects.
3. **State-toggle gating.** open-before-take-from; turn-on-before-use; unlock-before-open. Detect the toggle verb + its patient, and require the enabling toggle before the dependent action on the same patient.
4. **Force-dynamic verb typing.** Map verbs to CAUSE / ENABLE / PREVENT (Talmy 2000 force dynamics; Wolff 2007 vector model; Wolff & Song 2003 — force-dynamic model beats focal-set models for causal verbs). ENABLE edges are exactly the ordering edges; PREVENT edges gate ordering the other way.
5. **Instrument availability.** An event that makes an instrument available precedes events that require it.

**Reuse the substrate, do not rebuild:** `hdlab.causation_typing` already emits within-clause CAUSE/ENABLE/PREVENT — lift it from within-clause to CROSS-EVENT edges keyed on the shared object/location/state token. `hdlab.goal_outcome_relation` and `hdlab.consequence_learning_loop` supply effect->goal linkage. The new organ is thin: an edge-builder that joins each event's extracted EFFECT predicates to another event's PRECONDITION predicates on a shared entity, emitting a directed enable-edge; the ordering is then the existing read-out.

**Honest risks (calibration — every item below is a reason this could fail):**
- Extraction is SPARSE on ~13 narratives/scenario; enable-edges may be as sparse as the co-occurrence pairs were (~3 strong direct pairs/eval). The win, if any, comes from edges being DIRECTED and CAUSAL (transitively composable with high confidence) where co-occurrence pairs were symmetric and noisy — but sparsity is the live threat.
- spaCy precondition/effect extraction is shallow; implicit state changes ("the causal effects of actions are often implicit and need to be inferred" — ProPara's own caveat) will be missed without commonsense the glass-box cannot import at inference. This bounds recall.
- Do NOT grade-by-what-you-ground-by: if enable-edges are used to both order AND select eval pairs, that is circular. Tag pairs independently.

**P(enablement-edge graph beats the 0.591 co-occurrence floor, CI-separated, on this corpus): ~0.35-0.45** (novel synthesis; capped at 0.50 then further deflated for extraction sparsity and shallow state-change recovery). The stronger, more robust expected win is the Q2 REFRAME — partitioning answerable vs irreducible pairs — which I rate more likely to hold than the raw accuracy lift.

---

## Q4 — GENERALIZATION: one reusable canonical-order operation?

**PINNED:** transitive inference, script/sequence order, spatial reasoning, and planning recruit the SAME cognitive-map / relational-integration machinery in the hippocampal-entorhinal-mPFC system. Behrens et al. (2018), "What is a cognitive map?" — these maps "capture the similarity between symmetric, high-dimensional relationships … satisfying geometric constraints such as betweenness and equidistance," enabling generalization and inference. Whittington et al. (2020), the Tolman-Eichenbaum Machine — a single mechanism unifies spatial navigation, social hierarchies, and transitive inference as structure on a connected graph; structural representations generalize to untrained relations. Parallel cognitive maps (Cerebral Cortex 2024) — multiple relational structures coexist and are selected as needed.

**Implication (design):** feed CAUSAL/ENABLEMENT premises (the A->B enable-edges) as the RELATIONAL PREMISES into the SAME `transitive_ordering` read-out, rather than building a second ordering mechanism. The proven integrator already does betweenness/transitive composition on a magnitude line; enablement edges are just a different, better-conditioned PREMISE TYPE than co-occurrence tallies. The novelty is entirely in the premise (directed causal edges vs symmetric co-occurrence), not the read-out. This is brain-faithful: the brain does not have a separate "script-order module"; it applies relational-integration to whatever relational premises the event schema supplies.

**OUR-INVENTION-UNDER-TEST:** that enablement premises + the existing read-out clear the wall. Keeping the read-out fixed also makes the test clean — only the premise type changes (one-variable).

---

## PINNED vs OUR-INVENTION (summary)

| Claim | Status |
|---|---|
| Hippocampus does temporal-co-occurrence/SR statistical learning | PINNED (Schapiro 2016; Stachenfeld 2017; Dayan 1993) |
| SR makes co-occurring states SIMILAR + temporal-context matching is SYMMETRIC -> co-occurrence is structurally weak on direction (WHY the wall) | PINNED (Dayan 1993; Gershman & Moore 2012) |
| Script order is fixed by precondition->effect ENABLEMENT chains | PINNED at cognitive/computational level (Schank & Abelson 1977; ProPara dependency graph) |
| Preconditions/effects live in event models; goal-subgoal enablement is a PFC hierarchy | PINNED (Zacks/Reynolds 2007; Botvinick, Niv & Barto 2009) |
| Replay/mPFC consolidation confers ordinality by sharpening the given skeleton | PINNED (Baldassano 2018; Spens & Burgess 2024) |
| Canonical order = ONE reusable cognitive-map/relational-integration operation | PINNED (Behrens 2018; Whittington TEM 2020) |
| Answerable pairs = causally-dependent; irreducible residual = causally-independent/parallel | OUR-INVENTION-UNDER-TEST (measure on corpus) |
| An enable-edge graph + transitive_ordering beats the 0.591 co-occurrence floor CI-sep | OUR-INVENTION-UNDER-TEST, P~0.35-0.45 |
| Specific "Dixon 2019 causality != order" reference | OUR-INVENTION (exact ref unverified; the claim is supported by discourse-comprehension work) |

## Key citations
- Dayan (1993). Improving generalization for temporal difference learning: the successor representation. Neural Computation.
- Schapiro, Turk-Browne, Norman & Botvinick (2016). Statistical learning of temporal community structure in the hippocampus. Hippocampus.
- Stachenfeld, Botvinick & Gershman (2017). The hippocampus as a predictive map. Nature Neuroscience. (gershmanlab.com/pubs/Stachenfeld17.pdf)
- Gershman, Moore, Todd, Norman & Sederberg (2012). The successor representation and temporal context. Neural Computation. (gershmanlab.com/pubs/Gershman12.pdf)
- Schank & Abelson (1977). Scripts, Plans, Goals and Understanding.
- Zacks, Speer, Swallow, Braver & Reynolds (2007). Event perception: a mind-brain perspective. Psychological Bulletin. / Reynolds, Zacks & Braver (2007). A computational model of event segmentation from perceptual prediction.
- Botvinick, Niv & Barto (2009). Hierarchically organized behavior and its neural foundations: a reinforcement learning perspective. Cognition.
- Baldassano, Hasson & Norman (2018). Representation of Real-World Event Schemas during Narrative Perception. J Neurosci 38(45):9689.
- Spens & Burgess (2024). A generative model of memory construction and consolidation. Nature Human Behaviour.
- Talmy (2000) force dynamics; Wolff (2007) Representing causation, JEP:General; Wolff & Song (2003) Models of causation and the semantics of causal verbs, Cognitive Psychology.
- Dalvi, Huang, Tandon, Yih & Clark (2018). Tracking State Changes in Procedural Text (ProPara). NAACL.
- Marx & Wittenberg (2025). Dynamicity Predicts Inferred Temporal Order in Complex Sentences. Cognitive Science. / The State-Before-Event Inference Emerges Across Tenses (2025), Open Mind.
- Behrens et al. (2018). What is a cognitive map? Organizing knowledge for flexible behavior. Neuron. / Whittington et al. (2020). The Tolman-Eichenbaum Machine. Cell.

---

## TLDR (plain English)
The brain does not learn the order of a routine's steps mainly by noticing which steps tend to show up together. Counting co-occurrence tells you the steps BELONG together, but it is a fuzzy, direction-blind signal — the very same mechanism that makes similar steps hard to tell apart — which is exactly why counting-based order stalls just above chance. What actually pins down "first this, then that" is CAUSE-and-ENABLING: you have to get the mug before you can pour, get the ticket before you can board. Each step produces a condition the next step needs. That is a directed, reliable signal. The brain reuses ONE general "put things in order" ability for this, for logical ranking, and for planning — so we do not need a new ordering machine, just a better kind of clue fed into the one we already have. The concrete next move: read simple cause-and-enable clues straight out of the text offline (who gets/uses an object, who enters/leaves a place, what must be opened first), build a "this enables that" arrow-chart, and order THAT with our existing ordering read-out. Two honest cautions: with only ~13 stories per scenario these clues may be as sparse as the counts were, and some step-pairs genuinely have no fixed order (they happen in parallel) — those we should identify and stop treating as mistakes.

## QUESTIONS
None. The direction is clear and the tests are the solver's to run.

## NEXT STEPS (design hypotheses to MEASURE, not adopt)
1. Build the thin enable-edge organ: join each event's extracted EFFECT predicates to another event's PRECONDITION predicates on a shared entity (object-availability, location-gating, state-toggle, force-dynamic verb type), reusing `hdlab.causation_typing` / `goal_outcome_relation` / `consequence_learning_loop`. Emit directed A->B edges.
2. Order the enable-graph with the EXISTING `transitive_ordering` read-out (change only the premise type; one-variable).
3. Can-fail test vs BOTH floors: the shuffled-order twin AND the 0.591 co-occurrence estimator. Report CI half-width + null p95 beside the margin.
4. Test the Q2 reframe directly: tag each eval pair as enablement-linked vs causally-independent; check that accuracy concentrates on enablement-linked pairs and the residual concentrates on independent pairs. If so, ENUMERATE the independent pairs as irreducible rather than chasing them.
5. Guard against circularity: tag pairs independently of the ordering signal (no ground-by-X + grade-by-X).
6. If edges are too sparse to separate, that is a fidelity/extraction gap to BUILD across (richer state-change recovery), NOT a ceiling — state the stronger version tested before any "route exhausted" claim.
