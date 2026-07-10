# Research: prior-art scan — offline consolidation + cross-channel agreement for degree-invariant relational generalization

Date: 2026-07-10
Mode: self-executed lit-scan (no sub-agent fan-out per explicit dispatch instruction). Generic math/CS terms only used in all external queries — no substrate-novel mechanism names, configs, or numbers went off-platform.

## HEADLINE

Fragments of this architecture exist scattered across three unconnected literatures (computational CLS/replay-for-generalization, co-training/multi-view theory, KG degree-bias), but **no prior-art match was found for the full combination**: an offline loop that iteratively rearranges embeddings to honor agreement between *genuinely independent* channels, specifically targeting degree/popularity-shortcut removal in relational inference. Closest single-paper analogs are (a) DEAL (dual-encoder structure+attribute alignment for inductive link prediction) and (b) Sun/McClelland-style predictability-gated consolidation ("Go-CLS"). Nobody combines both. Per lit-scan calibration discipline this is genuine novel-synthesis territory — P capped at 0.50, deflated further below given how thin the direct evidence is for the specific claim ("iterative cross-channel agreement removes degree-shortcut, not just noise"). Treat everything below as directional, not validating.

## Thread 1 — Offline consolidation / replay for representation reorganization

**What was done / what worked:**
- McClelland, McNaughton & O'Reilly (1995) originated Complementary Learning Systems (CLS): hippocampus = fast, sparse, pattern-separated episodic store; neocortex = slow, distributed, interleaved-learning system that extracts "gist"/semantic structure across episodes. This is the direct biological analog cited in our motivation. [Wiley: O'Reilly 2014 review](https://onlinelibrary.wiley.com/doi/10.1111/j.1551-6709.2011.01214.x), [RSocPubl CLS-hippocampus review](https://royalsocietypublishing.org/rstb/article/372/1711/20160049/23089/Complementary-learning-systems-within-the)
- Sun, Yamins et al., "Organizing memories for generalization in complementary learning systems" (Nat. Neurosci. 2023) — closest direct hit. Simulated interleaved replay/consolidation that **rebalances** representation: generalization improved for *weakly-learned* items, attenuated for *strongly-learned* (already-consolidated) items. This is the first result that says consolidation actively reshapes the generalization geometry, not merely preserves old memories. [Nature Neuroscience](https://www.nature.com/articles/s41593-023-01382-9), [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10400413/)
- A related/companion line ("Go-CLS" framing, predictability-gated consolidation) makes an important and under-cited claim: **consolidation should be regulated by predictability/SNR, not indiscriminately applied.** Predictable, high-SNR experience gets transferred to the "slow" system; noisy/unpredictable experience should *stay* episodic. Unregulated transfer overfits the slow system to noise. The paper explicitly frames this as resolving the tension "replay helps generalization vs. replay just memorizes garbage." No validation dataset exists in the brain — the mechanism for estimating predictability is left unidentified. (biorxiv/Cerebral Cortex line — "neural network account of memory replay and knowledge consolidation")
- In ML directly: Sleep Replay Consolidation (SRC) — maps a trained ANN to a spiking network driven by Poisson input reflecting the training distribution; empirically reduces catastrophic forgetting AND improves generalization/robustness, especially helpful when data are limited/unbalanced. [Nature Communications](https://www.nature.com/articles/s41467-022-34938-7), [PMC unbalanced-data follow-up](https://pmc.ncbi.nlm.nih.gov/articles/PMC9755223/)
- Generative replay (Shin et al., NeurIPS 2017) works well on toy/class-incremental benchmarks but **scaling to complex, many-task settings is an open, acknowledged weakness** — the generator itself has to be learned and can drift/degrade.

**What failed / pitfalls:**
- Nobody in this thread reports a clean, isolated test of "does replay reduce frequency/popularity shortcut bias" — that specific question is NOT directly asked in the CLS-replay literature. The Sun et al. weak/strong-item rebalancing result is the nearest proxy (frequency of exposure ~ analogous to degree), and it is encouraging, but it's a toy simulation, not a KG/relational-inference benchmark. Treat the mapping "weakly-learned items ~ low-degree entities" as an *analogy*, not an established equivalence.
- Unregulated consolidation reliably overfits to noise in these models. If our consolidation loop lacks an analogous "is this cross-channel agreement predictable/reliable, or is it noise" gate, this is a known failure mode with a name in the literature, not a hypothetical risk.
- Generative replay quality bounds the whole system — a degraded generator silently degrades consolidation without an obvious symptom (this is the ML-side version of "unregulated transfer").

**Takeaway:** Build in an explicit predictability/reliability gate on what gets consolidated (not "consolidate everything the channels agree on" — consolidate only where agreement is *statistically reliable*, with a mechanism to detect and exclude noisy/spurious agreement). This is the single most concrete, actionable idea from Thread 1.

## Thread 2 — Multi-view / multi-channel agreement as grounding signal

**Theory baseline:** Blum & Mitchell (1998) co-training proves correctness *under* the assumption that views are conditionally independent given the label: P(X1|Y,X2) = P(X1|Y). This is exactly the "genuinely independent channels" premise our design leans on. [Understanding the Behavior of Co-training](https://www.researchgate.net/publication/2243517_Understanding_the_Behavior_of_Co-training)

**Where it breaks (load-bearing finding):**
- Nigam & Ghani (2000) showed empirically that when the independence assumption is violated, co-training performance suffers significantly — this is not a minor footnote, it's the dominant real-world failure mode since real "views" are rarely truly independent.
- Abney (2002) and Balcan et al. (2004, epsilon-expansion) offer *weaker* sufficient conditions than full independence, but these are still nontrivial to verify in practice and don't come with a cheap diagnostic.
- Deep CCA / multi-view theory (2025 info-theoretic generalization bounds) formalizes "each view acts as a regularizer constraining what can be learned" — consistent with our motivation — but the generalization-bound literature is recent (2024-2025), thin, and mostly bounds-in-principle, not "this fixes X in practice" empirical wins.
- **CLIP-style caveat (explicitly requested):** image/text "independence" in CLIP is *not* Blum-Mitchell independence. Both channels are generated by the *same underlying process* (a human looked at the image and wrote a caption) — they share conventions, co-occurrence statistics, and web-frequency biases. This is why CLIP suffers a well-documented "modality gap" and cross-modal shortcut/spurious-correlation problems: the two "views" leak the same biases through a shared generative process, so agreement between them does NOT guarantee grounding in anything outside that process. [Mitigate the Gap](https://arxiv.org/html/2406.17639v1), [Exposing spurious correlations in cross-modal retrieval](https://arxiv.org/pdf/2304.03391)
- Contrastive multi-view learning has a documented "easy-feature suppression" failure: when multiple redundant cues predict the match between views, the model latches onto the *easiest* shared feature and suppresses everything else, even when more task-relevant information is present in both views. This is a shortcut mechanism specific to multi-view contrastive setups, distinct from single-view shortcut learning.

**Takeaway:** The graph-structural channel and the attribute/empirical channel must be checked for *actual* statistical independence (or at least non-redundancy) before trusting their agreement as a grounding signal — e.g. verify neither channel can be predicted from the other above chance on held-out data. If structural degree correlates with attribute richness (very plausible — popular entities tend to have MORE recorded attributes too), the "independence" premise is already compromised and agreement will just re-launder the popularity signal rather than remove it. This is the single biggest structural risk to the whole design.

## Thread 3 — Degree / frequency / popularity bias in KG embeddings

**Established facts:**
- Degree bias is a named, recognized problem: KG embeddings systematically produce worse representations for low-degree entities, and (per Shomer et al., WWW 2023 "Toward Degree Bias in Embedding-Based KG Completion") this is directional — in KGE models, prediction accuracy tends to correlate *positively* with degree (popular = better predicted), the opposite direction from what's reported for some node2vec-style graph embeddings. [arXiv 2302.05044](https://arxiv.org/pdf/2302.05044), [ACM WWW'23](https://dl.acm.org/doi/10.1145/3543507.3583544)
- TransE and its one-shot direct-fit relatives are known to struggle with 1-N/N-1/N-N and symmetric/transitive relations — exactly the class of relations where a popularity shortcut (predict the globally-frequent tail entity regardless of head) is cheapest to exploit.
- Proposed fixes: KG-Mixup (synthetic-triple augmentation targeting low-degree entities), adversarial debiasing, degree-aware contrastive losses, meta-learning/GNN approaches for long-tail entities (GEN, MaKEr, MTKGE, MorsE). All report benchmark wins. **None of the search results surfaced a rigorous ablation proving these fixes remove the *shortcut mechanism* rather than just reweighting the loss toward the tail** (i.e. cosmetic reweighting that trades high-degree accuracy for low-degree accuracy without changing what's actually learned).

**The load-bearing warning (things-not-to-do caliber):** Sun et al. (2019/2020), "A Re-evaluation of Knowledge Graph Completion Methods" — showed that widely-used benchmarks (FB15k, WN18) have massive test leakage via inverse/duplicate relations and Cartesian-product relations, where **link prediction is trivially solvable by simple rules (including popularity-adjacent heuristics), not genuine relational reasoning**, inflating reported accuracy by an estimated 19%-175%. This is a directly relevant "how success gets faked" precedent: any benchmark that doesn't explicitly control for inverse-relation leakage and near-Cartesian relations will make a degree-bias fix (or our consolidation loop) look like it's "generalizing" when it's exploiting a benchmark artifact. [arXiv 1911.03903](https://arxiv.org/pdf/1911.03903), [SIGMOD 2020](https://dl.acm.org/doi/abs/10.1145/3318464.3380599)

**Takeaway:** Any held-out eval for our cell MUST be checked for inverse/duplicate-relation leakage and Cartesian-product relations before trusting a rare-entity MRR improvement. Also: prefer an eval that reports the *rare-vs-frequent gap*, not just aggregate MRR, since aggregate MRR is dominated by high-degree entities and can improve while doing nothing for the actual target population.

## Thread 4 — Grounding via non-LLM exterior sources

**Executable/verifiable oracle grounding (strongest, most legitimate class found):**
- Code-world-models / "generate-and-verify" pattern: LLM proposes, an external deterministic engine (code execution, symbolic solver) verifies. AlphaCode (execution-filtered), AlphaGeometry (symbolic engine verifies neural proposals) are the credible success stories — reliability comes from the *external, non-learned* verifier, not from the model's own confidence. [Executable World Models survey](https://arxiv.org/pdf/2605.05138)
- This is the strongest form of "genuinely independent channel" available in the current literature — a symbolic/executable oracle is independent of the learned representation by construction (it doesn't share the model's inductive biases or training-data frequency artifacts).

**Embodied/active grounding:**
- Held & Hein (1963) kitten-carousel: active kitten (self-produced movement + concurrent visual feedback) developed normal visually-guided behavior; passive kitten (identical visual input, no self-produced movement) did not. **Identical sensory data is not sufficient — the causal/active-intervention structure of the signal matters, not just its content.** This is a strong, old, well-replicated result and it's the single cleanest empirical case for "passively-agreeing channels are not enough; the grounding channel needs an active/interventional component." [PMC review](https://pmc.ncbi.nlm.nih.gov/articles/PMC7248214/)

**The "borrowed grounding" problem (Harnad, 1990, symbol grounding problem):**
- Formal symbol systems that only ever exchange symbols with other symbol systems (no matter how sophisticated the exchange) risk grounding that is "parasitic on the meanings in our heads" rather than intrinsic. 35+ years on, no consensus solution exists. Recent critique goes further: embodiment/sensorimotor grounding may be *necessary but not sufficient* — a system can have full sensorimotor grounding and still lack whatever "genuine understanding" requires. [Harnad 1990 PDF](https://www.southampton.ac.uk/~harnad/Temp/HarnadAncrage.pdf)

**Takeaway:** The honest bar for "grounding" is a spectrum: (weakest) two learned channels trained on correlated/co-generated data (CLIP-style — looks grounded, isn't) < (middle) two channels trained on genuinely disjoint data-generating processes < (strongest) at least one channel is an executable/symbolic oracle or involves active intervention, not passive observation. Our "attribute/empirical view" channel should be evaluated against this spectrum honestly — if the attribute data ultimately derives from the same corpus/process as the structural graph (e.g. both scraped from the same source), it is CLIP-tier, not oracle-tier, grounding.

## Thread 5 — The failure literature (shortcut survival, collapse, faked success)

- **Shortcut learning survives naive fixes.** Standard data augmentation has been shown to *fail* at counteracting simplicity-biased shortcut learning; regularization interacts with simplicity bias in non-trivial (sometimes counterproductive) ways. Purpose-built fixes (feature sieves, diverse ensembles trained to disagree, IRM/REx/Group-DRO style objectives) are needed — naive "more data" or "more replay" is not automatically a fix. [Feature Sieve](https://arxiv.org/pdf/2301.13293), [Evading Simplicity Bias via Diverse Ensembles](https://arxiv.org/pdf/2105.05612)
- **Representation collapse taxonomy** (directly applicable to any iterative self-refinement loop): (1) *complete collapse* — all outputs converge to a constant; (2) *dimensional collapse* — embeddings span a lower-dim subspace than the nominal dimensionality (measurable via singular-value spectrum of the representation covariance); (3) *informational collapse* — dimensions become correlated/redundant even without literal collapse. All three are known failure modes of self-supervised/iterative bootstrap training (no external labels), which is exactly our situation (offline loop with no external supervisory signal beyond cross-channel agreement). [Understanding Dimensional Collapse (Meta AI)](https://ai.meta.com/blog/understanding-dimensional-collapse/)
- **Multi-view-specific collapse:** in multi-view contrastive/fusion setups, a documented trivial solution is the fusion function degenerating to a constant map, or one channel's representation degenerating into a near-copy of the other (destroying the independence that was supposed to give the agreement signal meaning). This is the precise failure mode Thread 2's "takeaway" warns about, now confirmed as an empirically observed pathology, not a theoretical worry. [Preventing Dimensional Collapse in Multi-View Clustering](https://arxiv.org/abs/2303.12241)
- **Iterative self-training can silently drift/overfit to its own artifacts** — self-distillation methods require deliberate architectural asymmetry (stop-gradient, momentum encoders, whitening) specifically to prevent collapse; naive "iterate until fixed point" is exactly the setup known to collapse without such safeguards.

## THINGS NOT TO DO (pitfalls that would fake success or sink the cell)

1. **Don't trust aggregate MRR/accuracy as the success metric.** Report rare-entity (bottom-decile degree) held-out performance *separately* from aggregate — aggregate is dominated by high-degree entities and can look great while doing nothing for the target population (Thread 3).
2. **Don't evaluate on a benchmark with inverse/duplicate-relation leakage or Cartesian-product relations without checking first** — these make trivial rules look like generalization (Sun et al. 2019 precedent, Thread 3).
3. **Don't assume the two channels are independent just because they're "structural" vs "attribute."** Test it: verify neither channel predicts the other above chance on held-out data. If attribute-richness correlates with degree (very likely a priori), the independence premise is already broken before the loop starts (Thread 2).
4. **Don't consolidate indiscriminately.** Gate acceptance of cross-channel agreement by some analog of predictability/reliability — unregulated consolidation is a documented overfit-to-noise failure mode in the CLS literature (Thread 1, Go-CLS).
5. **Don't let one channel collapse into a copy of the other.** Monitor for dimensional/informational collapse (singular-value spectrum of each channel's representation, cross-channel predictability) at every consolidation iteration — this is a known, empirically observed multi-view failure, not hypothetical (Thread 5).
6. **Don't treat "two views agree" as inherently meaningful** if both views were ultimately derived from the same underlying data-generating/labeling process (the CLIP modality-gap lesson, Thread 2/4) — that's borrowed grounding, not independent grounding.
7. **Don't assume naive iteration converges to something useful; it can converge to a trivial fixed point** (constant map, degenerate agreement) without explicit anti-collapse machinery (Thread 5).
8. **Don't assume degree-bias "fixes" from the KG literature (Mixup, adversarial debiasing, degree-aware losses) are validated mechanisms** — the search did not surface rigorous evidence separating "genuinely learned tail relations" from "cosmetic reweighting"; treat all of them as unproven precedent, not endorsed technique (Thread 3).

## USABLE IDEAS (worth stealing, flagged unproven)

1. **Predictability/reliability gating on what gets consolidated** (steal from Go-CLS): only lock in cross-channel agreement that is statistically reliable across replay iterations, not agreement seen once. Unproven for our exact setting but directly addresses the #1 identified risk (noise overfitting). [UNPROVEN — theory-only precedent]
2. **Explicit non-redundancy / independence check as a pre-flight gate**, not just a post-hoc worry: before trusting agreement as signal, measure cross-channel predictability on held-out data and refuse to proceed (or discount agreement weight) if predictability is high. Directly operationalizes the Blum-Mitchell load-bearing assumption instead of just hoping it holds. [UNPROVEN, but cheap to implement and directly testable]
3. **Anti-collapse instrumentation borrowed from SSL practice**: track singular-value spectrum / effective rank of each channel's embedding space per consolidation iteration; alarm on dimensional collapse. Cheap, well-precedented diagnostic (Thread 5). [Well-precedented as a diagnostic, unproven as a fix]
4. **DEAL-style dual-encoder alignment** (structure encoder + attribute encoder, kept aligned via an explicit alignment loss/mechanism) is the closest existing architecture skeleton to "two-channel agreement for inductive link prediction" — worth reading in full as a structural starting point, even though it's one-shot (not iterative/offline-consolidation) and doesn't address degree-bias explicitly. [Directly adjacent, worth deep-reading — not yet drilled to full-text depth this cycle]
5. **Rare-vs-frequent gap as the PRIMARY reported metric**, with a Sun-et-al-2019-style leakage audit of the eval set as a mandatory pre-registration step — turns two "things not to do" into one positive eval protocol. [Directly actionable, cheap]
6. **Held-Hein-style active/interventional component for at least one channel**, if at all feasible — e.g., the attribute/empirical channel is populated via some form of active querying/intervention rather than passive corpus scraping, to move up the grounding-strength spectrum in Thread 4. [Highest-value, hardest to implement — flagged as aspirational, not near-term]

## Cheap decisive test (pre-registered)

**Setup:** synthetic relational graph with a controlled (e.g. Zipfian) degree distribution, split into a held-out set stratified by entity degree (bottom-decile "rare" vs top-decile "popular"). Build two channels believed a priori to be non-redundant (verify this with a held-out cross-predictability check — Pitfall #3 above — before trusting the setup). Compare: (a) one-shot direct-fit baseline (TransE-style) vs (b) the iterative consolidation loop with agreement-gating.

**Falsifiable predictions:**

- **HARD-PASS** (all four must hold):
  1. Rare-entity held-out MRR improves by >=15% relative over the one-shot baseline.
  2. High-degree/aggregate MRR does not regress by more than 5% relative (no "fixing tail by breaking head").
  3. Single-channel ablation (zero out either channel's contribution at inference) degrades combined performance by >=10% for BOTH channels (proves non-redundant, non-collapsed agreement — directly tests Pitfall #5).
  4. Injected-noise/corrupted triples (a held-out fraction of synthetically wrong "agreements") are accepted into the consolidated representation at a rate <30% relative to clean triples (evidence the predictability/reliability gate is doing something, per Thread 1).

- **HARD-FAIL** (any one triggers rejection of the mechanism as tested):
  1. Rare-entity MRR improvement <5% relative (no real degree-invariance gain).
  2. Either channel's ablation changes combined performance by <=2% (channel has collapsed / become redundant — agreement was trivial, per Thread 5).
  3. Noise-triple acceptance rate is statistically indistinguishable from clean-triple acceptance rate (no predictability gating — pure indiscriminate consolidation, the Go-CLS-warned failure mode).
  4. The rare-entity improvement disappears once inverse/duplicate-relation and Cartesian-product-relation leakage is removed from the eval set (Sun-et-al-2019-style audit) — i.e. the "win" was a benchmark artifact, not real generalization.

## Cross-thread synthesis

The five threads triangulate on one structural risk that recurs everywhere: **agreement/consolidation mechanisms are only as good as the independence and reliability of what they operate on, and every literature here has documented ways that independence and reliability silently fail** (CLIP's shared-generative-process leakage, co-training's real-world independence violations, KG benchmark leakage, SSL dimensional collapse, unregulated-consolidation overfitting). None of these literatures individually anticipated our exact combination (offline consolidation + cross-channel agreement + degree-invariance target), which is why this is genuine novel-synthesis — but every one of them independently arrived at "verify the independence/reliability premise explicitly, don't assume it," which is the single actionable through-line for our build. This also means our first internal cheap test should be the pre-flight independence check (Pitfall #3 / Usable Idea #2) before spending any compute on the full consolidation loop — if the two channels are already correlated with degree, the whole architecture is moot before it starts.

## Substrate-product implications

For the consolidation cell we are about to build: treat this as license to build the mechanism (three literatures converge on the *shape* being reasonable — CLS-replay-for-generalization, dual-encoder structure+attribute alignment, predictability-gated consolidation), but the FIRST artifact should be diagnostic instrumentation, not the consolidation loop itself: (1) a cross-channel predictability probe (are the channels actually independent of degree and of each other, measured, not assumed), (2) a per-iteration collapse monitor (singular-value spectrum / effective rank per channel), (3) a rare-vs-frequent stratified eval with an explicit leakage audit modeled on Sun et al. 2019. None of this is a substrate-physics claim — it's an engineering discipline the literature says is necessary to avoid building something that fakes success. We do not adopt any of these papers' architectures wholesale; we adopt their documented failure modes as our pre-registered risk list.

## Anchor candidates for cell-author (rank-ordered, no inline experiment design)

Per [[feedback-no-experiment-design-in-prompts]] these are pointers, not prescriptions — cell design, pre-reg, smoke gate, and thresholds-adaptation remain the cell-author's call.

1. **Pre-flight cross-channel independence probe (do this first).** Before building anything else: measure held-out cross-predictability between the graph-structural channel and the attribute/empirical channel, and each channel's own correlation with degree. This is the cheapest possible falsifier — Thread 2 / Pitfall #3 above identifies unverified channel independence as the single biggest structural risk to the whole design. If channels are already degree-correlated or mutually predictable, the architecture is moot before the consolidation loop is built.
2. **Rare-vs-frequent stratified eval harness with a Sun-et-al-2019-style leakage audit.** Build alongside or just after (1) — infrastructure, not a claim-bearing experiment. Without it, any later "win" is unfalsifiable per HARD-FAIL criterion #4 below (benchmark-artifact false positive).
3. **Minimal offline consolidation loop with agreement-gating + anti-collapse instrumentation.** The actual cell under test — iterative offline rearrangement gated by a predictability/reliability analog (Thread 1, Go-CLS precedent), instrumented with per-iteration singular-value-spectrum / effective-rank tracking per channel (Thread 5 collapse diagnostics). Reuse the pre-registered HARD-PASS/HARD-FAIL criteria above rather than re-deriving new ones; adapt units/thresholds to whatever concrete representation is actually used, preserving the spirit of each criterion. Only worth dispatching after (1) and (2) pass their own gates.

## Citations (verified count)

24 distinct sources found and read (search-snippet or fetched) across the five threads:
1. Sun, Yamins et al., "Organizing memories for generalization in complementary learning systems," Nat. Neurosci. 2023 (Nature + PMC)
2. "A neural network account of memory replay and knowledge consolidation" (bioRxiv/Cerebral Cortex, Go-CLS predictability-gating)
3. O'Reilly 2014, CLS review (Wiley)
4. Royal Society CLS-within-hippocampus review
5. Golden et al. / Sleep Replay Consolidation, Nature Communications 2022
6. Sleep-like unsupervised replay, limited/unbalanced data follow-up (PMC/AAAI)
7. Shin et al., "Continual Learning with Deep Generative Replay," NeurIPS 2017
8. Blum & Mitchell co-training behavior analysis (ResearchGate secondary)
9. Deep Generalized CCA (arXiv 1702.02519)
10. "Towards the Generalization of Multi-view Learning" info-theoretic bounds (arXiv 2501.16768)
11. Generalization Guarantees for Multi-View Representation Learning (arXiv 2504.18455)
12. "Demonstrating and Reducing Shortcuts in Vision-Language Representation Learning" (arXiv 2402.17510)
13. "A Principled Framework for Multi-View Contrastive Learning" (arXiv 2507.06979)
14. Shomer et al., "Toward Degree Bias in Embedding-Based Knowledge Graph Completion," WWW 2023 (arXiv 2302.05044 / ACM DL)
15. KG-Mixup / degree-aware contrastive loss (from Shomer et al. context)
16. Adversarial Learning for Debiasing Knowledge Graph Embeddings (arXiv 2006.16309)
17. Sun et al., "A Re-evaluation of Knowledge Graph Completion Methods" (arXiv 1911.03903 / SIGMOD 2020)
18. GIF-MCTS / WorldCoder / executable world models survey (arXiv 2605.05138)
19. AlphaGeometry / AlphaCode generate-and-verify pattern (via executable world models survey)
20. Held & Hein 1963 kitten-carousel, "Rediscovering Richard Held" (PMC 7248214)
21. Harnad 1990, "The Symbol Grounding Problem" (Southampton PDF)
22. "Overcoming Simplicity Bias in Deep Networks using a Feature Sieve" (arXiv 2301.13293)
23. "Evading the Simplicity Bias... Diverse Ensembles" (arXiv 2105.05612)
24. "Understanding Dimensional Collapse in Contrastive Self-Supervised Learning" + Meta AI blog (arXiv 2110.09348 / ai.meta.com)
25. "Preventing Dimensional Collapse of Incomplete Multi-View Clustering via Direct Contrastive Learning" (arXiv 2303.12241)
26. DEAL — "Inductive Link Prediction for Nodes Having Only Attribute Information" (arXiv 2007.08053 / IJCAI 2020)
27. CLIP modality gap — "Mitigate the Gap" (arXiv 2406.17639) + "Exposing and Mitigating Spurious Correlations for Cross-Modal Retrieval" (arXiv 2304.03391)

(27 sources; several thread-2/3 claims are corroborated by 2+ independent sources, satisfying single-source-citation caution.)

P_deflated = 0.35 (novel-synthesis cap 0.50 minus additional 0.15 deflation for thin direct evidence on the specific "iterative agreement removes degree-shortcut" claim — no source tested that exact claim; all support is analogical).
