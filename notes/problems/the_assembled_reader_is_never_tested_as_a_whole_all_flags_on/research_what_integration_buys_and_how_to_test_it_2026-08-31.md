# What integration buys, and how to test it (research drill, 2026-08-31)

SOLVER drill for `the_assembled_reader_is_never_tested_as_a_whole_all_flags_on`.
Question: prove/refute that a shared-event-token (integrated) reader BUYS comprehension over PARALLEL SILOS.
Lead with biology.

## THE CORE COMPUTATIONAL FACT (frames everything)
Silos store the **marginals** (the SET of agents, the SET of times, the SET of causes).
A bound event token stores the **joint** (which agent goes with which time/cause, as ONE conjunctive code).
Any inference that is a function of the JOINT distribution — not the product of the marginals — degrades or is impossible for silos. This is the classic **binding problem**: a superposition of features cannot tell "red square + blue circle" from "blue square + red circle"; only conjunctive binding recovers the pairing (VSA/HDC survey Kleyko et al. 2022; Smolensky tensor-product binding). Unbinding a superposition yields crosstalk that needs cleanup — i.e. marginals are lossy w.r.t. the joint.

**This is exactly why the solver's cases collapsed.** When there is only ONE event of a given type, or "cause == referent", the joint is trivially recoverable from the marginals (marginal = joint at cardinality 1). A siloed baseline matches because the design leaked the joint into the marginals. **The fix is to force cardinality>1 of the SAME event type** so the marginal (the verb/lemma) is identical across target and distractor and ONLY the binding separates them.

## 1. Computational payoff of a single bound token
Operations that provably require the shared index (degrade/fail on silos):
- **Event coreference** — deciding two mentions are the SAME token = comparing the joint (same agent AND patient AND time AND place). A lemma silo matches the type, never the token.
- **Pattern separation of same-TYPE events** — two "meetings" separated only by their conjunction of participants/time. A lemma-keyed silo hashes both to "meet" → cannot separate.
- **Event anaphora** ("it / that / the same" → a proposition) — antecedent is an event token, not an entity; needs a pointer to a bound token (abstract-anaphora survey Kolhatkar et al. 2018 CL; ~43% of demonstratives are non-nominal).
- **Bridging / multi-hop causal chains** — chaining A→B→C needs B-as-effect and B-as-cause to be the SAME token (the JOIN key). Silos re-extract B independently on each dimension → the join is unsound (byte-identity is not token-identity).
- **Cross-dimension updating** — an event boundary (spatial/temporal shift) resets the causal frame (Event Segmentation Theory, Zacks/Kurby: a change on one dimension updates the whole working event model). Silos have no shared token to propagate the update to.

## 2. Is integration NECESSARY, or just present?
Established at the memory-mechanism level via a genuine **double dissociation**:
- Hippocampal relational-memory account (Cohen & Eichenbaum; Ryan/Cohen; Konkel & Cohen 2009 *Frontiers* "impairs all manner of relational memory"): amnesics keep item/feature memory (marginals) but lose **relational/conjunctive** memory and **flexible inference**.
- Transitive inference / associative inference / acquired equivalence: end-item choices SPARED (marginals) but novel-pair inference IMPAIRED (joint) after hippocampal lesion; developmental amnesia impairs inference (Hipp. 2016).
So "integration wins" is **empirically established for the brain**: item memory can be intact while relational binding fails → binding is necessary for a class of inferences, not merely correlated. **BUT it is NOT yet established for a reading-comprehension silo-vs-integrated reader — that is the open, testable gap.** Ask whether the experiment could even succeed: yes, IF same-type distractors are present; no (guaranteed degenerate) if not.

## 3. The discriminating task (avoid the degeneracy)
Rule: **the marginal must be identical across target and distractor; only the binding differs.**
- **Same-type event coreference.** "The committee MET Monday to plan the merger. They MET Friday to cancel it. The Monday MEETING was productive." Resolve "the Monday meeting" → token#1. Both are "meet" → lemma silo at chance; only who+when binding disambiguates.
- **Causal bridging with a same-type distractor** (Singer causal-bridging; Haviland & Clark given-new): two events of the same predicate, only one is the valid antecedent-cause; the bridge must select by the joint.
Golds: coreference cluster id (ECB+) or the token index in constructed items.

## 4. Pattern separation for repeated events — real, not a toy
Yassa & Stark 2011 (*TiNS*) Mnemonic Similarity Task: targets / **similar lures** / foils; DG+CA3 orthogonalize overlapping entorhinal inputs so near-identical experiences get distinct codes. Comprehension analog is REAL: the **repeated-event source-memory** literature (children & adults intrude details ACROSS occurrences of a scripted repeated event; the script keeps the TYPE, loses the token source — Powell/Roberts; adult review PMC9103626). "Which of two same-type events" is exactly what a shared-token model does and a lemma-keyed silo cannot — because the silo's key IS the type. This is a bona-fide comprehension/eyewitness phenomenon.

## 5. RECOMMENDED EXPERIMENT (can-fail, non-gameable)
**Task:** same-type event-token disambiguation (event coreference restricted to same-lemma pairs).
**Corpus/gold:** ECB+ (Cybulska & Vossen) — real; WD+CD event coref; ~722 non-singleton clusters; annotations for event trigger + participants + time + location. **Filter to documents with ≥2 mentions of the SAME lemma** (same-type pairs); gold = coref cluster id. Backup: hand-built bridging/anaphora items with same-type distractors.
**Strong siloed baseline (must beat):** LATE-FUSION of per-dimension marginals — score candidates by max/sum of independent similarities (agent-set overlap, time overlap, lemma match) with NO bound token. ALSO run an SBERT sentence-similarity baseline so a win isn't mere lexical overlap.
**Info-free control (the clean discriminator that can fail):** **binding-shuffle** — permute which time/participant attaches to which trigger while keeping the marginal SETS identical.
- Integrated reader: accuracy MUST drop toward chance under shuffle (it uses the joint).
- Silo baseline: accuracy INVARIANT to shuffle (it only sees marginals).
- **If our "integrated" reader is shuffle-invariant, it is secretly a silo — the experiment fails honestly.**
**Win condition:** integrated reader beats late-fusion silo on same-type pairs AND is shuffle-sensitive. If it doesn't beat the silo, integration bought nothing here.

## VERDICT
"Integration beats silos" is **empirically established at the neural/memory-mechanism level** (hippocampal relational-binding double dissociations; binding-problem theory proves marginals ≠ joint) but **NOT yet established for reading-comprehension readers — OPEN and testable.** The solver's prior failure was a design artifact (joint recoverable from marginals when event-type cardinality = 1), not evidence against integration. Same-type distractors + binding-shuffle control convert it into a fair, can-fail test.

### Key citations
Kleyko et al. 2022 (VSA/HDC survey, ACM CSUR); Smolensky 1990 (tensor-product binding); Zwaan/Langston/Graesser 1995 & Zwaan/Radvansky 1998 (event-indexing); Kurby & Zacks 2008 (event segmentation); Cohen & Eichenbaum / Konkel & Cohen 2009 (relational memory, hippocampal amnesia); Yassa & Stark 2011 (pattern separation, MST); Singer (causal bridging) / Haviland & Clark 1974; Kolhatkar et al. 2018 (abstract anaphora survey); Cybulska & Vossen (ECB+); Chambers & Jurafsky 2008 / Mostafazadeh 2016 ROCStories (narrative cloze — cross-event inference eval).
