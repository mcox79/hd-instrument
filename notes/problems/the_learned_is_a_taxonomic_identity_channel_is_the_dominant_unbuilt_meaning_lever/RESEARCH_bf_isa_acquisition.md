# RESEARCH — brain-foundational acquisition of is-a / taxonomic identity FROM READING (de-risking drill for pri-1)

**Who/why:** strategy-session research drill (2026-09-10, CONT-115), folded for the eventual pri-1 solver. NOT a solution and NOT code — a literature+mechanism scan that names the brain-foundational route to the one thing the prototype is missing: **directed, labelled read is-a (genus) EDGES**. The disk outranks this note; verify the prototype's construction first-hand before building.

**Provenance / confidence:** synthesized from two search-verified literature scans (hypernym-extraction; consolidation/word-learning) captured in full, plus the well-established hierarchy-emergence literature the pri-1 brief already cites (Rogers-McClelland; Saxe-McClelland-Ganguli; Lambon-Ralph). The dedicated ATL/hierarchy sub-scan did not report back cleanly (a sub-agent coordination failure); its content here is from established literature + the brief, so treat the Rogers-McClelland / Saxe citations as PINNED-by-the-brief and re-confirm exact claims if a citation becomes load-bearing.

---

## (a) HOW THE BRAIN ACQUIRES SUPERORDINATE / is-a IDENTITY FROM READING

The key distinction the prototype has half-built: **category STRUCTURE** (which things pattern alike) vs the **directed, labelled superordinate EDGE** (robin →IS-A→ bird →IS-A→ animal). These come from two complementary mechanisms, and the brain uses BOTH.

1. **STRUCTURE from property-covariance — PINNED (Rogers-McClelland 2004, semantic-cognition; Saxe-McClelland-Ganguli 2019, deep linear networks).** Coherent covariation of properties across items makes categories emerge, and — critically — Saxe et al. show an error-driven learner over the item→property matrix learns hierarchical structure **in ordered stages, by singular-value magnitude**: broadest distinctions (animal/plant) differentiate first, finer ones (bird/fish, robin/canary) later. This is exactly the "ordered SVD" the prototype uses, and it is genuinely brain-foundational. **But property-covariance yields UNDIRECTED clusters, not directed labelled genus edges** — this is why the brief's genus-by-clustering was measured NEGATIVE. Covariance tells you robin and canary are similar; it does not, by itself, tell you the superordinate LABEL is "bird" or that the edge points up.

2. **The DIRECTED GENUS EDGE from explicit linguistic PREDICATION — the missing channel.** The brain gets the labelled superordinate from language: copular ("a robin **is a** bird"), appositive ("the robin, **a** small **bird**"), and set-inclusion frames ("robins **and other** birds", "birds **such as** robins"). In NLP these are the Hearst patterns (Hearst 1992, search-verified). The claim this note makes: **the Hearst-pattern family is brain-foundational-COMPATIBLE** — reading "a robin is a bird" as evidence that robin IS-A bird is a computation a competent reader plainly performs (it is not an engineering shortcut like consulting a dictionary). What is NOT brain-foundational is the *engineering* around them (hard-count thresholds, gold supervision). The BF form keeps the pattern-as-evidence and swaps the accumulation rule (see below).

3. **Accumulation is GRADED and reliability-weighted, never hard-count — PINNED (Complementary Learning Systems: McClelland-McNaughton-O'Reilly 1995; Davis-Gaskell 2009; Xu-Tenenbaum 2007 Bayesian few-shot; Yu-Smith 2007 cross-situational; all search-verified).** Every strand converges: the neocortical semantic system integrates evidence with small incremental (reliability-/frequency-weighted) updates, not a binary count/discard; a single strong exposure buys only a provisional placeholder (fast-mapping, Carey-Bartlett 1978), refined slowly over many encounters. McCloskey-Cohen (1989) catastrophic-interference is the computational reason a large hard update is unsafe. **Markman (1990/94) taxonomic-constraint** adds a structural PRIOR (a novel noun labels a category, not a theme) that narrows the hypothesis space independent of count — i.e., a prior on top of graded evidence.

4. **Senses stay separate, resolved by context — PINNED-ish (hippocampal pattern-separation-by-meaning, PNAS 2026 [authorship unconfirmed]; homonymy/polysemy psycholinguistics).** Unrelated senses (bank₁/bank₂) are stored as competing discrete traces, resolved by sentential-context gating; related senses overlap gradedly. The is-a channel must therefore attach edges to the CONTEXT-SELECTED sense, not pool a word's edges across senses.

**Summary of the mechanism:** genus (directed is-a edge) is READ from copular/appositive/set-inclusion predication as graded, reliability-weighted, context-gated evidence, accumulated across reading; differentia + category structure come from property-covariance (ordered SVD). Genus + differentia = the Collins-Quillian hierarchy. The brain does both; the prototype built only the second.

---

## (b) THE CONCRETE BF BUILD — FIRST SOLVER STEP

**Build the read is-a-EDGE channel the prototype is missing, and feed it through the SAME ordered-SVD the prototype already has.** Direct evidence this is the right shape: **Roller-Kiela-Nickel 2018 (search-verified)** built a Hearst-pattern-co-occurrence PPMI matrix and **SVD-densified it** (their "SPMI") — BLESS average-precision 0.45→0.76, direction accuracy 0.46→0.96, HyperLex 0.53 Spearman. The prototype has the SVD densifier but is feeding it the wrong matrix (distributional/property co-occurrence). Feed it an **is-a-predication** matrix instead.

Concrete steps (all BF, reuse-first, no WordNet at inference):
1. **Extract read is-a edges from the in-substrate parse.** From each read sentence, harvest genus edges via copular ("X is a/an Y"), appositive ("X, a Y,"), and set-inclusion ("X and other Y", "Y such as X", "Y including X") constructions, using the existing `hdlab` parse (pos_tagger + arc_parser; `causation_typing` already extracts constructions this way — reuse that machinery, do not re-derive). Emit `(hyponym_lemma, hypernym_lemma, pattern_type)` triples, attached to the context-selected sense.
2. **Accumulate into a graded, reliability-weighted is-a store — reuse the landed directional grow-by-reading store (`reading_grounding_loop.track_directional_context_counts` / `ConceptSpace` ROUTE-B).** Weight each edge by its PATTERN's reliability (the lit-scan gives the ordering: "and other"/"any other" > 0.7 precision; copular mid; "like" < 0.2) and by CROSS-OCCURRENCE agreement (Probase noisy-OR / NELL ≥0.9-coupled-agreement is the BF-compatible confirmation rule: trust an edge that recurs across independent contexts, discount one seen once). This is the graded CLS accumulation, not a hard count.
3. **Densify with the prototype's ordered SVD.** Build the is-a-edge PPMI matrix and run the SAME Rogers-McClelland/Saxe ordered SVD the prototype already uses → dense taxonomic vectors that generalize the sparse read edges to unseen pairs (this is the Roller-Kiela-Nickel move, and it is where coverage comes from).
4. **Compose genus + differentia.** The read is-a edge = the directed genus; the existing property-SVD = the differentia/structure. Fuse (genus vector ⊕ property-SVD) and fuse THAT into the live meaning read alongside grounded + distributional.
5. **SWEEP, never adopt:** pattern-reliability weights, the cross-occurrence agreement threshold, SVD rank, the genus/differentia mix, reading volume. Report the grow-by-reading curve toward the taxonomic ceiling (0.65).

---

## (c) DIAGNOSIS OF THE 0.26 → 0.65 GAP (crisp)

**The dominant missing factor is the directed read is-a EDGE (genus), not reading volume.** The prototype sits at 0.26 because it feeds the ordered SVD a property-covariance/distributional matrix, which yields category STRUCTURE (clusters) but not directed labelled superordinate edges — precisely why genus-by-clustering was measured negative. The 0.65 ceiling was reached by the WordNet lever, whose signal IS directed is-a edges. Roller-Kiela-Nickel is the quantitative analogue: sparse property/distributional signal ≈ the low arm; adding pattern-extracted is-a edges + SVD densification ≈ the jump to ~0.76 on BLESS. So the primary lever is **extracting the is-a-predication edges from reading and densifying them**, with reading VOLUME and OOV coverage as the SECOND-order lever (Hearst edges are sparse per-document → must pool across a large corpus; SVD densification helps but, per Roller et al., still fails on pure-OOV terms, where fusion with the distributional channel backfills). Predicted order of impact: (1) add read is-a edges + SVD densify [dominant], (2) reliability + cross-occurrence weighting to clean pooled noise, (3) reading volume, (4) grounded/distributional fusion for OOV.

---

## (d) RISKS / WHAT NOT TO DO

- **NO WordNet / ontology / dictionary AT INFERENCE** — circular with the SimLex eval and not brain-foundational. (A static offline FOUNDATION asset is fine to build from; the inference-time channel must be learned-from-reading.)
- **Do NOT re-run genus-by-clustering** — measured negative; covariance gives clusters, not directed edges. The fix is READ edges, not better clustering.
- **Pooled Hearst edges ARE noisy** — polysemy/sense-conflation (attach edges to the context-selected sense, don't pool across senses), loose/metaphorical copula ("time is money"), and NP-head/parse errors. Clean via reliability-by-pattern + cross-occurrence agreement (BF: CLS graded accumulation + Probase/NELL-style multi-source confirmation), NOT single-pass trust.
- **OOV coverage is the known limit of SVD-densified patterns** — do not claim full coverage from patterns alone; report the curve and backfill OOV with the distributional channel.
- **Do NOT hard-count / threshold edges** — the brain accumulates graded reliability-weighted evidence (CLS); a hard-count rule is both non-BF and unsafe (catastrophic interference).
- **A rigorous located negative is a full pass** — if, built faithfully (read edges + ordered SVD + graded accumulation), the channel still cannot approach 0.65 without WordNet, name exactly why WITH a number.

---

## TLDR (plain language)

The reader needs to learn "what kind of thing a word is" (a robin is a bird is an animal) from reading, without a dictionary. The current prototype learns which words are SIMILAR (robins pattern like canaries) but never learns the actual upward "is-a" LINK — which is why it's stuck at about a quarter of the achievable score while the dictionary-based proof hit two-thirds. The brain gets that upward link from the way things are said — "a robin is a bird," "robins and other birds," "birds such as robins" — and it trusts such statements gradually, more when they recur and come from reliable phrasings, keeping different senses of a word apart. The concrete fix: pull those "is-a" statements out of the text the reader already parses, accumulate them with reliability weighting, then run the SAME dimensionality-reduction the prototype already uses on THAT (is-a) evidence instead of on mere word-similarity — a published result shows exactly this jump (roughly 0.45→0.76 on a standard is-a benchmark). Volume of reading and coverage of rare words are the second-order levers. Do not use a dictionary at read time, do not go back to clustering, and expect the pulled-out statements to be noisy (clean them by trusting what recurs).
