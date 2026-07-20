# Base-First Reader: How the Brain Comprehends Text, and What It Must Already Know

Biology-led research drill, 2026-07-18. Director. Grounds the strategic decision: **build a base of understood content before attempting complex prose.** Lead with biology; prior work is credited and built on, never taken.

Prior arc check (substrate concept-query, max cosine 0.26): no prior arc work on a base-first comprehension developmental blueprint. Adjacent nodes only (frustration-context-disambig; a WordNet `comprehension` node; a `learn from books` concept node). This is new ground for the arc.

---

## TL;DR

Comprehension is **not extraction from a blank slate**. A competent reader recognizes ~98% of the words as already-known, and spends its scarce effort on the sparse ~2% that is new — flagging it (a prediction-error/surprise signal), inferring its meaning from the surrounding known context plus prior world-knowledge, holding it as a **provisional entry**, checking it for coherence against what is already known, and only then consolidating it durably. The whole machine **runs on a pre-existing base** of spoken language, vocabulary, grammar, and world-model that is built BEFORE reading, largely through oral language and lived experience. Below a hard lexical-coverage threshold (~95-98% of words known) the loop breaks: too many unknowns, no stable context to infer from, comprehension collapses. **The substrate has been trying to read at ~0% coverage — structurally impossible for any reader, brain included.** The fix is not a better extractor; it is to **build the minimal base first**, then read very-early / high-known-ratio material, and let the base grow to unlock progressively harder text (the Matthew effect).

---

## (a) The minimal base required BEFORE reading can work

Reading is a **secondary, culturally-invented skill bolted onto spoken language**, which is the primary, biologically-prepared system. The reading-science consensus is the **Simple View of Reading** (Gough & Tunmer 1986; Hoover & Gough 1990):

> **Reading Comprehension = Decoding × Language Comprehension**  (RC = D × LC)

It is **multiplicative, not additive** — if either factor is zero, comprehension is zero. Decoding (mapping print → spoken words) is the part unique to reading; **Language Comprehension is almost entirely pre-built before literacy** and is the same faculty used to understand speech. Over 150 empirical studies support the framework. Scarborough's Reading Rope unpacks LC into background knowledge, vocabulary, language structures, verbal reasoning, and literacy knowledge — all of which a child develops orally, years before decoding.

What a typical child already has at the START of reading instruction (age ~5-6), all built WITHOUT reading:
- **Spoken language**: near-complete phonology and core grammar/syntax by ~4-5 years, acquired from ambient speech.
- **Vocabulary**: on the order of ~5,000-10,000 known word *meanings* (spoken), grown at thousands of words/year through oral exposure and fast-mapping.
- **World-model / common concepts**: object permanence, agency, causality, space/time, social scripts, folk physics and folk psychology — a dense web of grounded concepts from ~5 years of embodied, multimodal experience.
- **Grammar as expectation**: predictive syntactic/semantic machinery that anticipates the next word.

**Key consequence for us:** the reader's job at the page is mostly *recognition and confirmation of the already-known*, with a thin margin of genuine novelty. Decoding converts print to the sound-form; the **heavy lifting of meaning is done by the pre-built LC system.** A system with no LC base cannot read regardless of how good its decoder/extractor is — exactly the RC = D × LC = (D × 0) = 0 failure mode. This is the biological grounding for "build the base first."

The **Perfetti Lexical Quality Hypothesis** (Perfetti & Hart) sharpens what "knowing a word" means: comprehension depends on high-quality lexical representations — tightly bound orthography + phonology + **meaning**. Low-quality (fuzzy, partially-known) entries are the bottleneck; fluent comprehension requires that the vast majority of words be *high-quality and automatically retrieved*, freeing working memory for integrating the new. A base isn't just "many words" — it is **many well-bound words**.

---

## (b) The read-loop, grounded in biology

The requested loop — **recognize-known → surprise-flag-new → build-meaning-from-context+prior → provisional-atom → coherence-check → consolidate** — maps cleanly onto known mechanisms:

**1. Recognize the known (the ~98%).** Skilled reading is highly *predictive*: context pre-activates likely upcoming words and their semantic features. Recognition of a high-quality lexical entry is fast, automatic, low-cost. This is why the known majority costs almost nothing — it is confirmed prediction, not fresh computation.

**2. Surprise-flag the new.** When a word is unexpected or its meaning cannot be resolved from the current model, the brain emits a **prediction-error / surprise** signal. The **N400** ERP component is the well-established index: its amplitude scales with how *unexpected/unintegrated* a word's meaning is (large N400 = surprising/hard-to-access; reduced N400 = predicted). Recent work models N400 as a **Bayesian/semantic prediction-error signal** (semantic surprise predicts N400 amplitude single-trial; also framed as lexical surprisal / prediction error). Critically, **novelty-flagging is at least partially separable from meaning-building**: the N400 indexes lexical-semantic access/prediction-error, while a *later* positivity (post-N400 positivity, "P600-family") indexes the effortful **integration/revision** step. So the brain has distinct stages for *"this is new/surprising"* vs *"now integrate/repair my model."* — evidence that flag ≠ build.

**3. Build meaning from context + prior knowledge.** New word meanings are acquired **incidentally from context**: the surrounding known words + world-model constrain what the unknown item can mean. **Fast-mapping** (Carey & Bartlett 1978) shows a single rich exposure can seed a partial entry immediately. But a first encounter yields only a **thin, provisional** meaning; the meaning is **grown over repeated, varied encounters** ("incremental / partial word learning", Nagy, Herman & Anderson). Evidence on exposures: a lexical form can be seeded in **1-2 exposures** (native L1 faster than L2), with meaning enriched over **~8+ encounters**, and — importantly — **context QUALITY / contextual diversity matters more than raw count**: highly-constraining, varied contexts teach faster than many uninformative repetitions. This is the distributional-semantics insight (Landauer & Dumais LSA; Firth "know a word by the company it keeps"): meaning accretes from the pattern of contexts. **Explicit definitions/glossaries are a HELPER that accelerates and disambiguates the first pass — not the core mechanism.** The core mechanism is contextual inference against a prior base; a definition is a high-quality single context that jump-starts it.

**4. Provisional atom (fast, hippocampal binding).** The newly-inferred meaning is held **provisionally** — a fast, one-shot binding characteristic of the **hippocampus** in Complementary Learning Systems theory (McClelland, McNaughton & O'Reilly 1995). Fast, sparse, pattern-separated, *not yet* woven into cortical semantic memory. This is the direct biological analog of a **"temporary atom that grows before integration."**

**5. Coherence-check before commitment.** Before durable integration, the new item is checked for **consistency against existing knowledge** — does it fit the schema? Schema-consistent information is treated very differently from schema-violating information. This is the gate that prevents committing garbage.

**6. Consolidate (schema-accelerated).** Durable learning = **systems consolidation**: gradual transfer/interleaving from hippocampus into neocortical semantic memory. The rate is **schema-dependent**: **Tse et al. (2007, Science)** showed that when new information fits a **pre-existing schema**, it can become neocortically consolidated and hippocampus-independent in as little as **ONE trial** — vs the slow interleaving normally needed to avoid catastrophic interference. **The richer and more relevant the existing base, the faster new material integrates.** This is a second, independent biological argument for base-first: a strong base is not just needed to *comprehend* the page (part a) — it also **accelerates the consolidation of everything new you learn from the page.**

**Net loop:** predict/recognize (cheap, known) → prediction-error flags the sparse new → infer meaning from constraining context + prior base → hold as fast provisional hippocampal binding → coherence-check against schema → schema-accelerated consolidation into durable semantic memory. Comprehension and learning are the *same* loop running continuously; you comprehend by mostly-confirming, and you learn at the thin margin where prediction fails.

---

## (b′) The known-word threshold — WHY the base must come first (the "99%")

The single most decision-relevant finding. **Hu & Nation (2000)** and the lexical-coverage literature (Nation; Laufer; Hirsch & Nagy; Schmitt; replicated Kremmel et al. 2023):

- **~98% lexical coverage** (knowing 98 of every 100 running words) is the **optimal threshold** for adequate unaided comprehension — corresponding to roughly the **6,000-8,000 most frequent word families**.
- **~95% coverage** is a **minimal threshold** (~4,000-5,000 families) — comprehension is possible but effortful/degraded.
- **Below ~95%**, comprehension **collapses**: too many unknowns per sentence, the context needed to infer any one unknown is itself full of other unknowns, so the inference engine has no stable footing. You cannot bootstrap when nearly everything is novel.

**This is the quantitative heart of the strategic decision.** Learning-new-words-from-context is only reliable *above* the coverage threshold, because contextual inference **requires a known surround**. The Matthew effect (Stanovich 1986) is the dynamic: readers above threshold learn more words from reading, raising coverage, unlocking harder text, compounding — while readers below threshold stall. **The substrate at ~0% coverage is deep in the collapse regime by construction.** No mechanism refinement rescues a reader below threshold; only *raising the base above threshold for the chosen material* does.

---

## (c) Curriculum: very-early → harder (how to actually bootstrap)

The biology prescribes a **coverage-first, low-new-density curriculum**, mirroring how children are taught to read:

1. **Establish the oral/base first (pre-reading).** Before decoding, build the spoken/semantic base: high-frequency vocabulary with high-quality (well-bound) meanings, core grammar, concrete grounded concepts. For the substrate: the base is the **grounded foundation** (the pivot's foundation-build), not text-reading.
2. **Decodable / controlled-vocabulary text.** Earliest readable material is engineered for **high known-word ratio**: controlled, high-frequency vocabulary, simple syntax, **concrete** (not abstract) concepts, short sentences, and heavy redundancy/repetition. New items are introduced **one or few at a time**, each in a **highly-constraining context**, and **repeated** across the text (hitting the "grow over encounters" requirement).
3. **Keep new-density BELOW the collapse threshold at every step.** Sequence material so coverage stays ≥95-98% *given the current base*. Each text should teach a small, bounded set of new items from a known surround — never dump a high-novelty passage on a small base.
4. **Let the base grow, then raise difficulty (Matthew ratchet).** As newly-consolidated words enter the durable base, coverage of the next-harder tier rises above threshold, unlocking it. Difficulty increases by *following the growing base*, not by forcing prose the base can't yet support. Abstract/low-frequency/technical vocabulary and complex syntax come **last**, once the concrete high-frequency base is dense and high-quality.
5. **Definitions/glossaries as accelerant, not substitute.** Provide an explicit definition as a *high-quality first context* for a genuinely new item, then still require multiple contextual encounters to grow a robust entry. The glossary speeds the first pass and disambiguates; it does not replace contextual grounding.

The through-line: **start where new-density is low relative to the base, and expand the base and the difficulty together.** This is the reading-science answer and it is the same shape as the arc's "textbook-after-textbook, base-first" waypoint.

---

## (d) Map to substrate: HAVE vs HAVE-PIECES vs GAP

| Loop stage | Biological mechanism | Substrate status |
|---|---|---|
| Recognize-known / predict | predictive lexical access, high-quality entries | **HAVE-PIECES** — clean-up/recognition + prediction (reading-barrier #3) exist; need them running against a real base |
| Surprise-flag-new | N400 / Bayesian prediction-error; separable from integration | **HAVE** — surprise = confirmed core capability (surprise-decomposition arc); flag-vs-build separation matches our route/branch stance |
| Build-meaning-from-context+prior | incidental contextual inference; distributional semantics; fast-mapping | **GAP (mechanism) + GAP (base)** — the learned-reader/contextual-inference is exactly the in-substrate reading long-game now in flight; and it needs a base to infer against |
| Provisional atom | fast hippocampal one-shot binding | **HAVE-PIECES** — fast binding / temporary-atom analog exists (state-of-mind overlay, hippo-binding threads); "temporary atom that grows" is directly buildable |
| Coherence-check | schema-consistency gate before commitment | **HAVE-PIECES** — schema-fit is one of the 3 ingest signals; needs correct calc + integration (all-3-signals load-bearing) |
| Consolidate | CLS systems consolidation, schema-accelerated (Tse 2007) | **HAVE-PIECES** — consolidation/replay pieces exist unassembled; schema-acceleration argues consolidation SPEED scales with base quality |
| **The pre-existing base** | oral language + vocab + world-model + grammar, pre-built | **THE GAP (foundational)** — "substrate knows almost nothing." This is precisely what the PIVOT (build the ideal knowledge foundation) targets |
| Coverage-threshold curriculum | ~95-98% known-word gate; Matthew ratchet | **NEW LEVER** — a *sequencing/curriculum* discipline we don't yet apply: measure coverage of candidate material vs current base; only read material above threshold |

**Bottom line for the strategic decision:** the biology strongly supports **build the base first, then read easy-first**. Two independent arguments converge — (1) comprehension itself is impossible below the coverage threshold (Simple View × Hu-Nation), and (2) even the *learning* from what you read consolidates far faster when it fits an existing schema (Tse 2007). Both say a small, high-quality, grounded base is the prerequisite and the accelerant. The substrate's have-list (surprise, fast-binding, consolidation pieces, schema-fit, prediction) is most of the *loop*; the load-bearing GAP is the **grounded base** plus the **learned contextual-inference reader** — which is exactly what the pivot + the in-flight learn-to-read work target. The missing *operational* piece is a **coverage-threshold curriculum discipline**: never feed the reader material whose new-density exceeds what its current base can support.

---

## Literature GAPS flagged (science unsettled — our glass-box choice to define later)

1. **The exact combination law across ingest signals** (surprise × schema-fit × recurrence, and importance as a possible 4th axis) is a genuine literature gap — the field describes each signal but not a unifying integration rule. (Consistent with the arc's standing note that this is a GAP to define glass-box.)
2. **N400 = lexical-access-facilitation vs semantic-prediction-error** is actively contested; both may index different sub-processes. We can *choose* our glass-box surprise signal without waiting for resolution, but should not claim the science is settled.
3. **Exposures needed to "know" a word** is highly context-dependent (2 to 8+ to 20+), with contextual *quality/diversity* dominating raw count — no single number. Our curriculum should optimize context constraint, not a fixed repetition count.
4. **Whether schema-fast-consolidation (Tse) is systems- or cellular-consolidation** is debated (it's "not just time"). Doesn't change the base-first implication, but flags that "schema accelerates integration" is the robust claim, not the specific circuit.

---

## Sources (credited; learn-from and build-on)

- Gough & Tunmer (1986); Hoover & Gough (1990) — **Simple View of Reading** (RC = D × LC). Scarborough — Reading Rope. [Reading Rockets](https://www.readingrockets.org/topics/about-reading/articles/simple-view-reading), [Simple View of Reading (Wikipedia)](https://en.wikipedia.org/wiki/Simple_view_of_reading)
- Hu & Nation (2000); replication Kremmel et al. (2023); Laufer; Nation; Hirsch & Nagy — **lexical coverage threshold (95-98%)**. [Hu & Nation replication (Wiley)](https://onlinelibrary.wiley.com/doi/10.1111/lang.12622), [Lexical threshold in elementary reading (Springer)](https://link.springer.com/article/10.1007/s11145-022-10385-0)
- Perfetti & Hart — **Lexical Quality Hypothesis**.
- Carey & Bartlett (1978) — **fast-mapping**; Nagy, Herman & Anderson — incremental word learning from context; Landauer & Dumais — distributional meaning (LSA). [Contextual diversity in incidental learning (Nature Sci Rep)](https://www.nature.com/articles/s41598-020-70922-1), [Repeated multimodal exposure (PMC)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4277705/)
- **N400 / semantic surprise / prediction error**: Kutas & Federmeier (review); "Semantic surprise predicts the N400" (2023). [Semantic surprise predicts N400 (ScienceDirect)](https://www.sciencedirect.com/science/article/pii/S2666956023000065), [N400 prediction-error ANN models (MIT Press)](https://direct.mit.edu/nol/article/5/1/136/118966/)
- **CLS** — McClelland, McNaughton & O'Reilly (1995); generalization update (Nat Neuro 2023). **Schema-accelerated consolidation** — Tse et al. (2007, Science). [Tse 2007 (PDF)](https://confluence.cornell.edu/download/attachments/89461995/Tse_2007_Schemas%20and%20Memory%20Consolidation.pdf), [CLS generalization (Nature Neuroscience)](https://www.nature.com/articles/s41593-023-01382-9)
- Stanovich (1986) — **Matthew effect** in reading.
