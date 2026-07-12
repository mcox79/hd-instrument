# Research: next functional-form decision from the first CSKG fair-test result

**Date:** 2026-07-12
**Trigger:** First fair-test result — CSKG genuine-L2 held-out, low+mid-degree stratum, single seed. ONESHOT_ROTATE hits@10=0.077 beats POP=0.044 (scramble collapses to 0.018 — geometry real). ADDITIVE_TRANSE=0.104 beats rotation on this same stratum. Rotation wins HIGH-degree (0.396 vs 0.321) and aggregate MRR (0.089 vs 0.083). g_backdoor gate FAILED; cross_channel geometry-vs-poprank r=0.31.
**Scope:** pure literature synthesis, no local compute, generic public ML/neuro terms only (query-privacy discipline). 4 parallel Sonnet lit-scans dispatched (form-by-degree, best-form-for-commonsense, popularity-leakage, brain direction+magnitude).

---

## HEADLINE

The additive-wins-low-degree / rotation-wins-high-degree split is **not a directly documented head-to-head finding anywhere in the public KGE literature**, but it is the predictable resultant of three separately well-established facts (degree-bias in rotational/lookup-table embeddings, TransE's known 1-to-N cardinality weakness, and ordinary bias-variance scaling). The literature's own answer to "what beats both" on exactly our relation mix (hierarchical / mereological / 1-to-N / asymmetric) is a **phase+modulus hybrid (HAKE-style)** — real, verified gains over plain rotation, with the LARGEST gain appearing on the most hierarchy-skewed benchmark tested (YAGO3-10). Nobody has run a HAKE-style hybrid on a commonsense graph (ConceptNet/ATOMIC/CSKG) — that combination is a genuine open gap, not a filled-in result. Recommend building the phase+modulus hybrid next. The leakage flag (r=0.31, failed g_backdoor) does **not** invalidate the low+mid-degree beat-POP claim — degree-stratified evaluation *is* the field's standard remedy for exactly this concern, and our result already clears that bar — but it does mean the **aggregate** MRR claim (rotation beats additive/POP overall) should not yet be trusted, and it raises a specific NEW risk for the hybrid: a magnitude/modulus term is mechanistically the term MOST likely to re-encode degree (bigger radius for more-connected entities), so the next build must ship with degree-residualization built into its own evaluation, not bolted on after.

---

## A. Why additive wins low/mid-degree, rotation wins high-degree + aggregate

No paper runs this exact TransE-vs-RotatE-by-degree-stratum comparison directly. But three independent, well-sourced literatures triangulate on it:

1. **Rotational/lookup-table degree bias is real and documented.** Shomer, Jin, Wang, Tang, *"Toward Degree Bias in Embedding-Based Knowledge Graph Completion"* (WWW 2023, arXiv:2302.05044): entity in-degree and tail-relation frequency strongly predict per-entity link-prediction accuracy across embedding methods including rotation/complex-family models; low-degree entities cluster together (poorly separated) in embedding space because they get less gradient signal during training, while high-degree entities become well-separated. A second source (arXiv:2405.14985) states explicitly that lookup-table embeddings "such as RotatE" show high accuracy for a small fraction of high-degree entities and poor accuracy in sparse regions. HIGH confidence this literature exists and says this; MED confidence it's been run as an explicit TransE-vs-RotatE pairwise comparison (it wasn't, as far as this scan found).
2. **TransE's structural weakness is orthogonal but compounding.** Wang et al., TransH (AAAI 2014) — the foundational, extremely well-established critique that pure translation (t ≈ h+r) cannot represent 1-to-N/N-to-1/N-to-N relations because it collapses multiple valid tails to one point. This should, if anything, HURT additive on our relation mix (mostly 1-to-N: partof/hasa/causes/hassubevent) — yet additive still wins at low/mid degree. That means the degree/data-sparsity effect below is dominating the cardinality weakness at low degree.
3. **General bias-variance scaling (not KGE-specific, flagged as an inference not a citation):** translation has one degree of freedom per relation (a vector); rotation has one phase per dimension (more effective capacity). With few training triples per entity (low-degree regime), the higher-capacity rotational model has more variance and needs more data to "pay off" before its extra expressiveness beats a lower-variance additive model. This is standard statistical learning theory, applied here as inference, not verified in a KGE-specific ablation.

**P_deflated = 0.40** (synthesis across 3 literatures, no single paper confirms the exact comparison; capped as novel-synthesis).

**Falsifiable prediction / hard bands for this explanation:**
- HARD-PASS: if we bucket entities into degree quartiles and additive's hits@10 advantage over rotation monotonically shrinks (and eventually reverses) from Q1→Q4, that confirms the bias-variance/degree-bias reading.
- HARD-FAIL: if the additive-vs-rotation gap is flat across degree quartiles (no monotonic trend), the "it's a degree/data effect" story is wrong and the split is driven by something else (e.g. specific relation types clustering by degree, not degree itself) — falls back to a relation-type explanation instead.

---

## B. Best functional form for OUR relation mix (commonsense: 1-to-N, asymmetric, inverse-paired, causal, mereological)

- **Malaviya, Bhagavatula, Bosselut, Choi (AAAI 2020), CN-100k/ATOMIC benchmark** — real numbers (fetched from paper table, HIGH confidence): plain bilinear/translational scorers (DistMult, ComplEx, ConvE, ConvTransE) are all weak and close to each other on CN-100k (MRR 9–21%) and ATOMIC (MRR 10–14%); their big win (MRR 51% on CN-100k) comes from **graph-structure (GCN over local neighborhood) + pretrained-LM semantics**, NOT from swapping the scoring geometry. RotatE/HAKE were never benchmarked in this paper — **commonsense-graph KGE literature has never tested rotation-family or phase+modulus models at all.** This is the single biggest gap this scan found.
- **HAKE (Zhang, Cai, Zhang, Wang, AAAI 2020, arXiv:1911.09419)** — verified numbers from the paper: beats RotatE on every benchmark tested (WN18RR MRR .497 vs .476; FB15k-237 MRR .346 vs .338; YAGO3-10 MRR +0.050/+6.0%H@1/+4.6%H@3 over RotatE — the LARGEST gain, on the most hierarchy-skewed dataset of the three). HAKE's own theory: radius/modulus = hierarchy depth or generality level; angle/phase = which sibling/branch at that level. Ablation: modulus-alone underperforms phase-alone (RotatE), but phase+modulus together beats either alone on every dataset — the magnitude term is necessary-but-not-sufficient, it works BY INTERACTING with direction, not standalone.
- **PairRE (Chao et al., ACL 2021, arXiv:2011.03798)** — separate head/tail relation-vector pairs, explicitly motivated by the same "plain rotation struggles with high in/out-degree relations" problem; reports gains over RotatE on FB15k-237 (MRR .351 vs .338, approximate/paraphrased numbers, MED confidence). This is a lighter-weight alternative to HAKE's explicit scalar-modulus if degree-leakage in the modulus term (see C) turns out to be a problem.
- HAKE/PairRE-style models have **never been run on ConceptNet/ATOMIC/CSKG with a relation-type breakdown.** Treat "modulus helps commonsense 1-to-N/mereological relations" as theoretically well-motivated (matches HAKE's own largest-gain-on-most-hierarchical-benchmark pattern, and our relation mix IS hierarchical/mereological: partof/hasa are literally a generality-level relation) but empirically unverified on this graph family.

**P_deflated = 0.40, capped at 0.50 per novel-synthesis rule** (strong theoretical fit + real HAKE numbers on adjacent benchmarks, but zero direct commonsense-graph evidence).

**Falsifiable prediction:**
- HARD-PASS: HAKE-style hybrid on our CSKG fair low+mid-degree stratum >= max(additive 0.104, rotation 0.077) hits@10, AND on high-degree stratum >= rotation's 0.396 (within small tolerance, e.g. >=0.35), AND aggregate MRR > 0.089, AND its own scramble control collapses (confirms geometry, not artifact).
- HARD-FAIL: hybrid underperforms BOTH pure forms in any stratum — this would directly contradict HAKE's own mechanism (phase+modulus beating either alone was true on every one of HAKE's 3 benchmarks; if it fails here, our relation mix doesn't behave like WN18RR/FB15k-237/YAGO3-10 hierarchy despite superficially looking mereological, and the HAKE analogy should be dropped in favor of PairRE or a plain capacity-matched rotation).

---

## C. Is the r=0.31 / failed g_backdoor gate a real leak, or benign?

The literature's consistent framing is that entity-degree correlating with prediction quality is treated as **an artifact requiring correction, not a benign expected coupling**:
- Mohamed et al., *"Popularity Agnostic Evaluation of Knowledge Graph Embeddings"* (AISTATS 2020) — built strat-hits@k/strat-mrr precisely because standard hits@k/MRR are shown biased toward popular entities/relations under power-law degree distributions.
- Shomer et al. (WWW 2023, above) — traces the mechanism (more gradient signal for high-degree entities during training) and builds KG-Mixup to correct it.
- Arduini et al. (MLG 2020, arXiv:2006.16309) — adversarial debiasing of KGE against degree/frequency.
- Toutanova & Chen / "Knowledge Base Completion: Baselines Strike Back" (arXiv:1705.10744) — the WN18/FB15k inverse-relation leakage story: this is a DIFFERENT, more severe failure mode (near-duplicate test/train triples), not the same claim as ours — flagging this distinction explicitly so as not to over-read our r=0.31 as being that bad.
- **No universal r-threshold exists in either the KGE or recommender-systems literature** for "how much correlation = confounded." The recommender-systems popularity-bias survey (arXiv:2308.01118) and the KGE-specific papers above both substitute **degree-stratified evaluation** (report performance on low-degree/long-tail bucket specifically, check the win survives there) as the standard remedy, not a correlation cutoff. No paper was found doing exact residualization/partial-correlation of an embedding score against a popularity score by that name — this is a gap in the field, not evidence the technique is unnecessary.

**Concrete bearing on our result:** our claimed win ("rotation beats POP on the fair low+mid-degree stratum, 0.077 vs 0.044") is **already the exact standard remedy the field prescribes** — it IS the degree-stratified check. That specific claim should be trusted more than the aggregate MRR claim (0.089 vs 0.083), because aggregate metrics on power-law-degree graphs are dominated by high-degree entities and are exactly what the field's bias papers warn against reading naively. **Recommendation: keep the stratified low+mid-degree beat-POP result; do NOT yet claim "rotation wins overall" from the aggregate MRR number without residualization or finer degree-quartile stratification.**

**New risk this raises for B (the HAKE hybrid):** a scalar modulus/magnitude term is mechanistically the MOST likely component to re-encode degree — an entity that needs to satisfy more distinct triples plausibly needs a larger radius almost by construction, independent of any real hierarchical structure. This is a genuine tension: the same magnitude term that HAKE's theory says should help mereological/hierarchical relations is also the term most likely to inflate the leakage correlation further. **This must be pre-registered as an explicit hard-fail band on the next build, not discovered after the fact.**

**P_deflated = 0.55** for "stratified result is robust / aggregate result is not yet trustworthy" (applying an established methodology, not inventing one — less discount than a novel-synthesis claim). **P_deflated = 0.35** for "the new magnitude term will measurably worsen the leak correlation" (directional risk flag, not yet observed — deflated as speculative-but-motivated).

**Falsifiable prediction / hard bands:**
- HARD-PASS (debiasing holds): hybrid's cross_channel geometry-vs-poprank r stays <= 0.31 (does not increase) AND g_backdoor gate passes on the hybrid.
- HARD-FAIL (leak risk confirmed): hybrid's r increases materially (e.g. > 0.40) relative to plain rotation's 0.31 — this would mean the modulus term is substituting a degree-proxy for genuine hierarchy signal, and the hybrid's gains (if any) should be presumed confounded until residualized.

---

## D. Brain grounding: does biology support a phase (direction) + modulus (magnitude/scale) dual code?

- **Dorsoventral grid-scale gradient** (Brun et al. 2008): grid spacing increases systematically from dorsal (~50cm) to ventral (~3m) MEC — scale is topographically organized, independent of phase.
- **Discrete modules, not continuum** (Stensola et al. 2012, *Nature*): grid cells cluster into a small number of discrete scale modules (~4-5 recorded per animal), ratio ~1.4x between adjacent modules, each independently rescalable — a residue-number-system-like combinatorial code: **which module (discrete magnitude/zoom-level) x phase-within-module (continuous 2D direction)**. This is a real, well-replicated, tight dual-code architecture — not a loose analogy in the spatial domain.
- **Generalizes to abstract conceptual space, but only the phase/direction half:** Constantinescu, O'Reilly, Behrens (2016, *Science*) found hexagonal grid-cell-like fMRI signals for a non-spatial 2D conceptual feature space (bird leg/neck length). This supports "direction in feature space is coded grid-like" generalizing beyond physical space — but this study did NOT test or find a Stensola-style discrete-module/scale-hierarchy code in that conceptual space. That half of the analogy is not directly demonstrated, only extrapolated.
- **Best bridge for "magnitude = conceptual generality/hierarchy":** Poppenk et al. 2013 (anterior-posterior hippocampal long-axis granularity gradient — coarse/gist representation anteriorly, fine-grained posteriorly), linked to the same dorsal/ventral MEC module gradient anatomically. This IS a real, separate-axis granularity gradient, but it's a continuous granularity dial, not a KGE-style scalar magnitude per entity, and "granularity of representation" is not identical to "hierarchy depth of a concept" in the IS-A/taxonomy sense HAKE's modulus targets.

**Self-skeptical bottom line:** the phase+discrete-scale-module dual code is biologically solid and well-replicated FOR SPACE. Extending "scale module" to mean "conceptual-hierarchy-depth" (which is what would ground a HAKE-style modulus term) is a motivated, cross-literature-bridging analogy (combining the spatial grid-module literature with the separate hippocampal long-axis granularity literature) — not a directly observed single finding. Treat this as design-motivation-grade evidence, not confirmation-grade.

**P_deflated = 0.35** for "biology directly grounds a phase+modulus hybrid for conceptual hierarchy" (explicitly capped low — this is the most stretched of the four legs, and the sub-agent's own self-skeptical read should be taken seriously rather than smoothed over).

---

## Cheap decisive test (for the next build cycle — not designed here, just specified as a target)

Build a HAKE-style hybrid on top of the existing glass-box ROTATE embedding (add a per-relation modulus/magnitude term alongside the existing phase term). Re-run the IDENTICAL evaluation harness already used for the first result: same CSKG genuine-L2 held-out split, same fair low+mid-degree stratum + high-degree stratum + aggregate MRR + scramble control + g_backdoor gate + cross_channel correlation. No new eval machinery — this is a same-yardstick comparison, which is why it's cheap.

**HARD-PASS bands (all must hold):**
- hits@10 on fair low+mid-degree stratum >= 0.104 (beats additive, the current stratum leader)
- hits@10 on high-degree stratum >= 0.35 (holds rotation's high-degree strength within tolerance)
- aggregate MRR > 0.089 (beats current rotation aggregate)
- scramble control collapses (< 0.03, confirms geometry not artifact)
- cross_channel r <= 0.31 (does not worsen leak) AND g_backdoor gate passes

**HARD-FAIL bands (any one triggers reject/rethink):**
- hybrid underperforms BOTH pure forms in any stratum (contradicts HAKE's own necessary-interaction mechanism)
- cross_channel r increases beyond ~0.40 (modulus term is re-encoding degree, not hierarchy — pivot to PairRE's paired-vector mechanism instead of a raw scalar modulus, or add residualization before trusting any win)

---

## Cross-thread synthesis with prior entries

This connects directly to the program-spine finding already logged (`project_relational_capability_is_the_core_requirement_make_it_real_USER_2026-07-10.md`): the brain's ADDITIVE/GEOMETRIC relational codes were previously characterized as pure vector-subtraction directional codes. This drill adds a needed correction — the brain's own spatial relational code is not purely directional, it is a joint direction+scale code (grid phase + discrete module), and the HAKE literature independently arrived at the identical joint-code structure from pure KGE benchmarking, with zero cross-pollination between the two literatures. That convergence (biology's grid-module dual-code and KGE's phase+modulus dual-code arising independently for structurally similar reasons — direction alone under-determines position/relation-target when the space has multiple valid scales/generality-levels) is the strongest single piece of triangulating evidence for building the hybrid next, stronger than either literature alone.

This also revises the earlier framing of "additive = memorizing regime, geometric/relational = generalizing regime" from the same prior note: today's result shows it's not that simple — additive currently WINS at low degree specifically, which is exactly where the current substrate has the LEAST data to memorize with, suggesting additive's win there is likely about parameter-count/robustness-with-scarce-data rather than "memorization" in the pejorative sense. Recommend revisiting that framing once the hybrid result is in.

## Substrate-product implications

- The commonsense relation vocabulary (causes/usedfor/partof/hasa/atlocation/hassubevent/desires/madeof/receivesaction) is mereological/causal, not taxonomic — this is GOOD NEWS for the hybrid recommendation, because HAKE's mechanism (modulus = generality/hierarchy-level) maps naturally onto partof/hasa (literally a part-whole generality axis) and plausibly onto causal chains (cause -> effect could be a directed generality/temporal-depth axis, worth testing as its own falsifiable sub-claim in the next cycle).
- If the hybrid passes, the product gets a SINGLE functional form that no longer needs a degree-dependent fallback (currently: use additive for sparse/long-tail entities, rotation for dense ones — a two-model routing burden). A passing hybrid collapses that into one glass-box scoring function, which is a real engineering simplification, not just a capability bump.
- If the hybrid hits the leak hard-fail (r increases), that is itself valuable substrate-product information: it tells us our current entity-embedding infrastructure conflates "well-connected" with "high in a hierarchy," which would need a structural fix (e.g. explicit degree-normalization at embedding-init time) before ANY magnitude-based relational form can be trusted product-wide.

## Citations (verified count)

Directly fetched/paraphrased with source URLs or table numbers (HIGH-MED confidence, not invented):
1. Ruffinelli, Broscheit, Gemulla, "You CAN Teach an Old Dog New Tricks!" ICLR 2020
2. Rossi et al., "Knowledge Graph Embedding for Link Prediction: A Comparative Analysis," ACM TKDD 2021 (specifics not independently re-verified, flagged LOW on exact numbers)
3. Shomer, Jin, Wang, Tang, "Toward Degree Bias in Embedding-Based Knowledge Graph Completion," WWW 2023, arXiv:2302.05044
4. "Implicit Degree Bias in the Link Prediction Task," arXiv:2405.14985
5. Wang, Zhang, Feng, Chen, "Knowledge Graph Embedding by Translating on Hyperplanes" (TransH), AAAI 2014
6. Malaviya, Bhagavatula, Bosselut, Choi, "Commonsense Knowledge Base Completion with Structural and Semantic Context," AAAI 2020, arXiv:1910.02915 (table numbers fetched directly)
7. Zhang, Cai, Zhang, Wang, "Learning Hierarchy-Aware Knowledge Graph Embeddings for Link Prediction" (HAKE), AAAI 2020, arXiv:1911.09419 (table numbers fetched directly)
8. Chao, He, Wang, Ju, "PairRE: Knowledge Graph Embeddings via Paired Relation Vectors," ACL 2021, arXiv:2011.03798 (numbers approximate/paraphrased, MED confidence)
9. Sun, Deng, Nie, Tang, "RotatE: Knowledge Graph Embedding by Relational Rotation in Complex Space," ICLR 2019
10. Mohamed, Nounu, Nováček, "Popularity Agnostic Evaluation of Knowledge Graph Embeddings," AISTATS 2020
11. Arduini et al., "Adversarial Learning for Debiasing Knowledge Graph Embeddings," MLG 2020, arXiv:2006.16309
12. Toutanova & Chen (WN18/FB15k leakage), "Knowledge Base Completion: Baselines Strike Back," arXiv:1705.10744
13. "A Survey on Popularity Bias in Recommender Systems," arXiv:2308.01118
14. CoDEx benchmark, arXiv:2009.07810
15. Brun et al. 2008, "Progressive increase in grid scale from dorsal to ventral medial entorhinal cortex," Hippocampus
16. Stensola et al. 2012, "The entorhinal grid map is discretised," Nature
17. Constantinescu, O'Reilly, Behrens, "Organizing conceptual knowledge in humans with a gridlike code," Science 2016
18. Poppenk et al. 2013, "Long-axis specialization of the human hippocampus," TICS
19. Whittington et al., "The Tolman-Eichenbaum Machine," Cell 2020

**Verified count: 19 distinct sources identified across 4 sub-scans; 3 (Malaviya table, HAKE table, degree-bias papers) independently fetched/confirmed at HIGH confidence; remainder MED-HIGH confidence from search-corroborated bibliographic detail; 0 fabricated — every gap and uncertainty was flagged explicitly by the sub-agents rather than papered over.**

---

## Intuitive summary

We found our first real result: a from-scratch geometric relation-encoder actually beats a "just guess the most popular answer" baseline on genuinely held-out commonsense facts — that's a real signal, not a fluke (a scrambled/randomized version of the same encoder collapses to near-chance, confirming the geometry is doing real work). But we noticed something interesting: a SIMPLER encoder (plain addition) wins for facts about less-common things, while a FANCIER encoder (rotation) wins for facts about well-connected, popular things — and overall aggregate score can hide which one you actually need. We asked: is this a known pattern, and is there a design that gets both? The literature says yes to both: simple/fewer-parameter models are known to generalize better with scarce data, fancier/rotation-style models are known to need more data to earn their keep, and there's a documented "hybrid" design (direction + size/hierarchy-depth, called HAKE) that combines both and wins the biggest specifically on the most hierarchy-heavy public benchmark tested — which matches our fact-types (part-of, has-a, causes) unusually well, since those are inherently "size/generality" relations. Nobody has tried this hybrid on commonsense facts before — that's a real, fillable gap, not a re-tread. We also checked whether "well-connected things get better scores" secretly explains our whole win (a fair worry, since we found a real statistical wrinkle pointing that direction) — the field's answer is that our exact style of check (testing performance separately on the less-common facts) is the standard, accepted way to rule that out, and our result already passes that test; what we should NOT yet trust is the "wins on average" claim, since averages get dominated by the popular stuff. Brain-wise, there's genuine, well-replicated evidence that spatial memory in the brain uses exactly this two-part code (a direction part and a separate "how zoomed in" part) — though stretching that into "concepts have a zoomed-in-ness too" is a reasonable guess, not a proven brain fact. Net recommendation: build the direction+size hybrid next, using the exact same fair test we already have, with an explicit tripwire that kills the idea if the new "size" component turns out to just be sneakily re-measuring popularity instead of real hierarchy.
