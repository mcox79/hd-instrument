# RESEARCH STRATEGIC PIVOT: language-prediction track CLOSED — compositional understanding track OPENS

**Filed-by:** Research (Opus 4.7 1M)
**Date:** 2026-06-26
**Trigger:** USER directive 2026-06-26 (REPEAT correction; standing memory locked at `feedback_substrate_doesnt_know_anything_stop_testing_against_language_USER_LOCKED_2026-06-26.md`).
**USER words verbatim (Q2):** "understanding is just that substrate has a basic understanding of things. we can understand language as more or less a mathematical system, but we need to ingest that info and understand how it works with combinatorial meaning before we can predict anything. the prediction comes from the combined meaning in substrate — NOT statistics"
**USER words verbatim (Q1):** "yes - it should come after conceptual"

---

## What changes (effective immediately)

**CLOSED tracks (do NOT dispatch; existing handoffs SUPERSEDED):**
- Language ingest drill 1 (n5 trigram / n6 V_C-sweep / n7 top-K cleanup / n8 5-gram / n9 partition-routed-trigram) — `exp_dev_handoff_research_language_ingest_drill1_vocab_scale_glass_box_LM_math_2026-06-26.md`
- Language ingest drill 2 (text8 sentence-block / enwik8 paragraph-break / wikipedia segmented) — `exp_dev_handoff_research_language_ingest_drill2_segmentation_block_size_2026-06-26.md`
- Language ingest drill 3 (lang_ingest_vocab_bigram_meta_m7_v1 + INFRA_1/2/3 LM eval harness + token_vocab + bigram_gap_measurement) — `exp_dev_handoff_research_language_ingest_drill3_pipeline_composition_substrate_native_2026-06-26.md`
- Just-filed partition-routed-trigram handoff (n9_partition_routed_trigram + n11_freq_stratified_VQ) — `exp_dev_handoff_research_lm_pipeline_partition_routed_trigram_2026-06-26.md`
- bigram-gap-closure as a progress metric. The 1.13-bit gap to text8 word-bigram is no longer a target.
- text8 BPC as primary eval. It returns ONLY as a downstream check AFTER compositional understanding is built.

**OPENED track (new primary work):**
- **Compositional-understanding-first.** Substrate ingests structured semantic info, learns to compose meanings via mathematical operations on representations, and only LATER does prediction emerge from composed meaning (not from co-occurrence statistics).

## Why (intuitive frame)

Language has mathematical structure: words combine into phrases combine into sentences via rules that operate on typed components. "Big red ball" = compose [SIZE-MOD: big] + [COLOR-MOD: red] + [N: ball] into a composite meaning. A child who has never seen "big red dinosaur" can still understand the phrase because composition is RULE-DRIVEN, not memorized.

We've been doing the opposite: trying to make the substrate memorize co-occurrence statistics and hoping meaning would emerge. It cannot. Bigram-prediction is the wrong test because bigram itself doesn't understand — it just memorizes. Beating it via more elaborate statistical machinery is meaningless. We were cargo-culting LLM benchmarks on a substrate that isn't an LLM and shouldn't be evaluated like one.

The right work:
1. **Build compositional primitives.** Substrate ingests typed concepts + typed relations. Concept composition is a defined mathematical operation (HRR role-filler binding when it's the right tool; partition routing when it's the right tool; direct vector arithmetic when that's right).
2. **Test composition fidelity, not prediction accuracy.** Can the substrate combine atomic meanings into composite meanings and recover the composite when queried? Can it detect type-incompatible compositions? Can it fill compositional gaps from structural constraints?
3. **THEN, much later, attach language.** Once the compositional scaffold exists, language prediction becomes "map text to compositional structure, predict next token from composed meaning." The composition does the heavy lifting; statistics is a thin shell on top.

## What's already in the substrate that's relevant (substrate-mine first)

The substrate has bones we've been ignoring while chasing BPC scores:
- **KG ingest** (FB15k-237 ch_584 / ConceptNet ch_585 / HotpotQA ch_588): subject-relation-object triples ARE compositional semantics in atomic form. We've tested RETRIEVAL on them; we have NOT tested COMPOSITION.
- **Multi-hop primitive** (chain-grade): chains atomic relations into multi-step composition. We test it for retrieval accuracy; we have NOT tested whether the chained meaning is a valid composition vs a confused chain.
- **HRR binding**: designed for role-filler composition (the n5 failure was using it for sequential context — wrong tool; for typed role-filler it's THE tool).
- **concept codebook V_C=1024**: rough semantic clusters built from co-occurrence. We could re-derive these from EXPLICIT semantic structure (definitions, taxonomies) instead of statistical neighborhood.
- **refuse-gate**: epistemic humility primitive. Essential for compositional systems that should refuse type-incompatible queries rather than confabulate.

## What's MISSING (the work)

- **Explicit type system.** What KIND of thing is each concept? (object / event / property / relation / quantifier). Without types, composition has no constraints.
- **Compositional rules.** Which concept combinations are valid? What does composition produce? (red + ball → red_ball property-attached representation; red + run → TYPE ERROR or coercion).
- **Compositional eval harness.** Test composition fidelity, not retrieval. Metrics: can the substrate recover composed meaning from its components? Can it detect type errors? Can it fill compositional gaps?
- **Structured semantic ingest.** Beyond raw KG triples — incorporate ontological structure (isa / partof / hasattribute taxonomies; WordNet sense structure; FrameNet roles; or custom-curated typed predicates).

## The first drill (under separate handoff today)

Concrete first cell: **Compositional KG query answering with type-aware composition** — extends existing KG primitives (chain-grade) to test composition fidelity rather than retrieval accuracy. Uses substrate's existing chain-grade KG ingest as the conceptual scaffold; adds typed predicates + compositional query operators; eval is composition-fidelity not BPC. See sibling handoff `exp_dev_handoff_research_compositional_understanding_drill1_typed_KG_composition_2026-06-26.md`.

---

## Reframing in one sentence

We stop trying to make the substrate predict language. We start teaching it to combine atomic meanings into composite meanings via mathematical operations on typed representations. Language prediction returns ONLY when composed meaning can drive it — and even then, it's a downstream eval, not the goal.

-- Research (Opus 4.7-1M)
