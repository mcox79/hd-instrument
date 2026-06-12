# Research drill 2x DEEP -- substrate-eval self-recognition gap architectural alternatives

date: 2026-06-11
topic: composite_C novelty classifier saturation -- architectural alternatives beyond Option B (file_id metadata)
trigger: Findings 17 HARD_FAIL -- post-ingest 449 drill files NOVEL=68.2% vs pre-ingest 67.9% (delta ~0.3 pp; expected <10 pp drop)
mode: 2x DEEP literature-anchored architectural drill, ASCII only
P_deflated: stated per-option, capped 0.50 per novel-synthesis cap
calibration penalty applied: -0.15 to -0.25 across the board

## HEADLINE

The composite_C = max(semantic_novelty, algebra_novelty) classifier saturates on cross-cutting math-atom-rich content because algebra_novelty measures **spread of math atoms a document references** rather than **whether the document's bundle has been ingested into the corpus**. The MAX gate then masks the semantic_novelty signal that DOES drop after ingest. This is a classic **familiarity / recollection conflation** in recognition-memory terms: substrate currently has neither channel cleanly -- algebra_novelty is a structural spread statistic, semantic_novelty is a top-k similarity blend, and neither is an explicit "is this document in my corpus" test. Brain-can-do-it solves this with **two distinct neural circuits** (hippocampal recollection + perirhinal/cortical familiarity) and substrate has analogous primitives available. Top recommendation: **Option B + Option H combined** (file_id explicit recollection AND atom retrieval confidence as familiarity), with Option E (weighted-avg replacing max) as a cheap day-1 partial fix; Option G (redefine algebra_novelty in BUNDLE space, not atom-reference space) as the highest-leverage structural redesign because it directly attacks the root cause.

## Cheap decisive test (per option)

For each architectural alternative below, the decisive test is the **same gold-labeled probe set**:
- Set A: 449 post-Phase-1 drill files KNOWN ingested into research_history partition (gold label = IN_CORPUS)
- Set B: 50-100 held-out drill-like files NOT ingested (gold label = NOVEL)
- Metric: AUROC of classifier output on A vs B
- Cost: substrate-only CPU eval, no GPU, <30 min per option

HARD_PASS: AUROC >= 0.85 (clean separation, classifier discriminates ingested vs novel)
MIDDLE_BAND: AUROC 0.65 - 0.85 (classifier helps but is noisy; needs ensembling)
HARD_FAIL: AUROC < 0.65 (architectural alternative does not address the root cause)

Pre-register: any option that passes MIDDLE_BAND on Set A vs B but FAILS on a secondary stress probe (Set A_perturbed: same files with paraphrase-level surface rewrites) reveals it is a surface-form classifier rather than substrate-recognition, and should be tier-demoted.

## Q1 + Q4 + Q5 -- Architectural alternatives ranked

### Ranking criteria

score = P_deflated x cost_efficiency x substrate_product_leverage
  P_deflated:           literature + substrate evidence the option fixes Findings 17
  cost_efficiency:      1 / (impl_cost_LOC x integration_risk)
  substrate_product:    does this also strengthen the v3 indexes / retrieval / classification head-to-head story

### Option H (atom retrieval confidence as familiarity signal) -- RANK 1

**Brain analogue.** Perirhinal cortex / cortical familiarity. Familiarity in dual-process recognition memory (Yonelinas 2002; Diana Yonelinas Ranganath 2007) is a **continuous-strength signal** with no episodic-detail recovery -- precisely the shape of "top-k retrieval returned an atom with high score." The hippocampal recollection channel (Option B) is precise but binary (yes/no on episodic identity); familiarity is graded and inexpensive.

**Substrate primitive map.** For each candidate document D:
- run substrate retrieval: top-k atoms from research_history partition matched to D's content-reference set + D's semantic-vec
- familiarity_score(D) = mean of top-k cosine to nearest atoms in BOTH the content-reference index AND the semantic-vec index (substrate_two_axes memory)
- this is **NOT** the algebra_novelty path -- algebra_novelty is a spread statistic on math atoms named in D; familiarity_score is a retrieval-strength statistic on document-as-query

**Expected effect on H1.** For 449 ingested drills, every D should retrieve itself (or a high-cosine sibling) as top-1 -- familiarity_score saturates near 1.0. For 50 held-out drills, familiarity_score falls into the bulk distribution of cross-document cosines (~0.3-0.6 typical for unrelated drills). Expected AUROC: 0.90+. Literature on dense retrieval (Karpukhin DPR 2020; Khattab ColBERT 2020) consistently shows that within-corpus query-document retrieval is near-perfect when the document was indexed; this is a different regime from cross-document semantic similarity.

**Implementation cost.** ~50 LOC -- substrate already has retrieval primitives; this is a wrapper that runs retrieval as a classifier feature and computes mean top-k cosine. Zero new tensors, zero new indexes.

**Side-effects.** None negative. POSITIVE: forces substrate to validate that its retrieval-by-content actually distinguishes ingested vs novel -- a Tier-1 self-evaluation primitive per substrate-deep-self-evaluation-program memory (Layer 2 spectral / Layer 6 weight-sweep). If retrieval fails on this probe, that is ALSO an empirical finding worth knowing.

**P_deflated.** 0.55 -> deflated to **0.45** (above novel-synthesis cap because this is composing existing primitives, not novel synthesis; but staying conservative since we have not yet measured top-k retrieval AUROC on this set).

### Option B + H combined (dual-process recognition) -- RANK 1-tied / RECOMMENDED ARCHITECTURE

**Brain analogue.** Dual-process recognition memory -- recollection (hippocampus, episodic precision, threshold + identity-match) PLUS familiarity (perirhinal, graded strength). The brain uses both because each fails in different regimes: pure recollection is brittle to surface change; pure familiarity is fooled by similar-but-novel content. Combining them is what makes biological recognition robust.

**Substrate primitive map.**
- recollection_score(D) = 1 if (top-1 semantic-similarity > 0.95) AND (file_id metadata match) else 0  -- Option B as stated
- familiarity_score(D) = mean top-k retrieval cosine, as Option H
- combined classifier: in_corpus_likelihood = max(recollection_score, sigmoid(familiarity_score - tau))
  where tau is calibrated on Set B held-out probes (the substrate's own bulk cross-document cosine distribution; conformal calibration per substrate-uncertainty-quantification work, ECE 0.044 precedent)

**Expected effect on H1.** Best of both -- for paraphrase-stable ingested files Option B captures them at AUROC ~1.0; for paraphrase-perturbed or partial-overlap content Option H still flags them. Expected AUROC on Set A vs B: 0.93+; on Set A_perturbed: 0.80+ (Option B falls back to Option H).

**Implementation cost.** ~80 LOC total (50 Option H + 20 Option B + 10 combiner). Adds **one** new metadata field (file_id provenance) per atom write -- modest invariant addition aligned with substrate-content-sources-us-or-substrate methodology rule.

**Side-effects.** POSITIVE: explicit two-channel recognition memory is a **substrate-product differentiator** -- LLM systems do not have structural recollection-vs-familiarity decomposition (they only have continuous logprob signals). Makes the auditable-memory-subsystem product story stronger (auditor can ask: "did substrate RECOLLECT this fact or merely FAMILIAR-recognize it?").

**P_deflated.** 0.60 -> deflated to **0.50** (caps at novel-synthesis cap; combines two independent primitives so independence-failure risk is the main deflation source).

### Option G (redefine algebra_novelty in BUNDLE space) -- RANK 2 / HIGHEST STRUCTURAL LEVERAGE

**Root cause attack.** The Findings 17 diagnosis says algebra_novelty saturates near 1.0+ on cross-cutting drill content because it measures **spread of math atoms referenced** rather than **bundle composition novelty**. This is a definitional bug. The fix is to redefine:

OLD: algebra_novelty(D) = 1 - avg_pairwise_HRR_cosine(math atoms NAMED in D)
NEW: algebra_novelty(D) = 1 - max over corpus atoms A of HRR_cosine(bundle(D), A)
     where bundle(D) is the HRR sum / superposition / cleanup-projected sum of math atoms named in D
     -- the document's CHARACTERISTIC algebraic signature, not its spread

**Brain analogue.** Composition-as-binding (Eliasmith semantic pointers; Plate HRR). A document is not characterized by HOW SPREAD its concepts are -- it is characterized by WHAT THEIR COMPOSITE is. Brain superposition + cleanup is precisely this. The current substrate algebra_novelty answers "is this document diverse?" instead of "have I seen this composite before?"

**Substrate primitive map.** Substrate has bundle / cleanup / superposition primitives (the substrate v3.0 compositional cliff result confirms they work). Compute bundle vector for D, retrieve nearest bundle vector in research_history partition, return 1 - cosine.

**Expected effect on H1.** This DIRECTLY attacks why algebra_novelty saturates. After redefinition:
- 449 ingested drills: their bundles ARE in the corpus -- algebra_novelty drops to ~0 for them (max-cosine to a stored bundle is near 1)
- held-out novel drills: their bundles are NOT in the corpus -- algebra_novelty stays high
- composite_C max(sem, alg) now correctly drops post-ingest

Expected AUROC: 0.88+.

**Implementation cost.** ~150 LOC -- requires computing and storing per-document bundle vectors as a new index partition. Bigger change than H or B but still substrate-only.

**Side-effects.** POSITIVE: a per-document bundle index is itself a Tier-1 substrate-self-evaluation tool (substrate-self-index foundational tool memory). NEGATIVE: redefining a core classifier metric means re-validating all upstream uses of algebra_novelty -- not just Findings 17. Migration risk is the main deflation.

**P_deflated.** 0.60 -> deflated to **0.45** (highest structural leverage but migration risk on existing call-sites).

### Option E (weighted-average instead of max) -- RANK 3 / CHEAPEST DAY-1 PARTIAL FIX

**Mechanism.** Replace max(sem, alg) with w_s * semantic_novelty + w_a * algebra_novelty, with w_s + w_a = 1 and w_s calibrated to dominate when algebra_novelty saturates.

**Why it partially works.** Empirically per Findings 17 semantic_novelty DOES drop post-ingest; only the MAX gate hides it. A weighted avg lets semantic carry signal even when algebra saturates. But: it does NOT fix the root cause that algebra_novelty does not measure ingest-recognition.

**Expected effect on H1.** Reduces NOVEL fraction post-ingest from 68.2% -> estimated 45-55% (still well above 10% target but a real change). AUROC on Set A vs B: 0.70-0.78 (middle band).

**Implementation cost.** ~5 LOC. Lowest cost option in the space.

**Side-effects.** Hides the underlying definitional bug rather than fixing it -- but bought time is real. Pairs well with G or H as a day-1 + day-N strategy.

**P_deflated.** 0.45 -> deflated to **0.32** (partial fix at best; will not pass HARD_PASS bar alone but will move the needle).

### Option F (parallel in_corpus_likelihood classifier) -- RANK 4

**Mechanism.** Train a supervised classifier on (D, label in_corpus={0,1}) using substrate features (semantic-vec + algebra-vec + content-reference features) and gold labels. Run in parallel to novelty score; route decisions through both.

**Brain analogue.** Cortical familiarity is in part a learned signal-detection criterion (Wixted Mickes signal-detection 2010); not just raw similarity. A supervised classifier IS that criterion-learning step.

**Expected effect on H1.** With 449 ingested + 50 held-out as gold labels, a small logistic / linear classifier on substrate features should saturate AUROC 0.90+ -- but ONLY in-distribution. Generalization to future drills depends on feature stability.

**Implementation cost.** ~100 LOC + gold-label curation. Modest.

**Side-effects.** NEGATIVE: introduces a supervised-learning artifact in a substrate that prides itself on similarity / algebraic primitives (no LLM-as-judge per substrate methodology rules; supervised classifier is a softer version of the same concern). POSITIVE: explicit task framing creates a baseline for self-recognition that other options can be benchmarked against.

**P_deflated.** 0.50 -> deflated to **0.35** (works but introduces supervised artifact; lower long-term leverage than B+H or G).

### Option I (substrate as supervised novelty classifier end-to-end) -- RANK 5

Closely related to F but trains the WHOLE novelty pipeline (not a parallel head) on supervised labels. Same brain analogue (criterion learning) but more invasive. Higher migration risk. P_deflated: 0.30.

### Option J (hierarchical 4-level novelty: semantic + algebra + content-reference + meta) -- RANK 3-tied with E

**Mechanism.** Decompose composite_C into FOUR explicit channels matching the four substrate axes:
- semantic_novelty (current)
- algebra_novelty (current, but possibly fixed per G)
- content_reference_novelty (1 - max over corpus of jaccard or weighted set-cosine over named atoms in D)
- meta_novelty (1 - cosine to corpus over meta features: drill_type, agent_kind, partition tags)

then combine via learned or hand-tuned weights / Mondrian conformal layering.

**Brain analogue.** Multi-channel recognition memory -- visual + semantic + episodic + temporal context all feed the recognition decision (Eichenbaum-Yonelinas-Ranganath review). Brain does not have a SINGLE recognition signal.

**Expected effect on H1.** Content_reference_novelty alone should crash to near-zero on 449 ingested drills (substrate KNOWS which atoms were named in each ingested file). This single channel could push AUROC to 0.90+ even without changing algebra. Composite over four channels would be even more robust.

**Implementation cost.** ~120 LOC. Comparable to G.

**Side-effects.** POSITIVE: aligns with substrate-two-axes memory finding (semantic + content-reference are ORTHOGONAL axes per empirical FINDINGS_08); the v3 architectural target is already 3 indexes + RRF + intent router. J operationalizes the same insight for novelty classification.

**P_deflated.** 0.55 -> deflated to **0.40**.

## Q2 -- Literature mapping (anchored by topic; no project-internal numerics)

### Anomaly detection / one-class SVM / isolation forest / autoencoder reconstruction
- Scholkopf one-class SVM (2001): defines novelty as outside a learned support boundary. Substrate analogue: store all atoms; novel = outside cleanup support manifold. Maps directly to Option H (retrieval support boundary) and Option G (bundle support).
- Isolation forest (Liu Ting Zhou 2008): novel points isolate quickly in random partition trees. Less aligned with substrate primitives.
- Autoencoder reconstruction (Hawkins 2002; Zong 2018 DAGMM): novelty = high reconstruction error. Substrate analogue: bundle-then-cleanup reconstruction error -- this is the bundle-recovery primitive substrate already has. Strongly supports Option G (recovery from bundle = recognition of bundle).
- KEY INSIGHT for substrate: anomaly-detection literature consistently warns that **a metric that saturates on diverse-but-in-distribution content is not an anomaly metric** -- it is a diversity metric. Algebra_novelty as currently defined is in this trap.

### Open-set recognition (OSR) -- gallery vs probe
- Scheirer 2013 / Bendale-Boult 2016 OpenMax: explicit reject option built from softmax tail behavior, not max(scores). Strongly supports replacing max gate.
- Yang Zhou Chen Hong 2021 OSR survey: best-performing OSR methods combine prototype matching (Option B analogue) with reconstruction (Option H / G analogue). Dual-channel is the field standard.
- KEY INSIGHT: gallery + probe formulation IS exactly what substrate has (research_history partition = gallery; new content = probe). Substrate has been failing to formalize itself as an OSR problem; once it does, the literature gives clean recipes.

### Self-supervised contrastive / identity classification
- SimCLR (Chen 2020), MoCo (He 2020): contrastive identity is the inductive bias that makes representations distinguish "same instance" from "other instance." Substrate analogue: per-file bundle vector trained to be retrievable as itself -- Option G with contrastive objective.
- Substrate already has the bundle primitive but does NOT have an identity-contrastive objective on it. This is a clean future direction.

### Dense retrieval / cross-encoder rerank / MIPS
- DPR (Karpukhin 2020), ColBERT (Khattab 2020), Reimers SBERT 2019: top-k retrieval is the workhorse of identity recognition in modern IR. Reliable AUROC 0.95+ on within-corpus probes.
- KEY INSIGHT: Option H is directly this literature; expected high P given decades of IR precedent.

### Cognitive science of recognition memory (DUAL-PROCESS)
- Yonelinas 2002 dual-process review: recognition memory has TWO distinct signals -- recollection (threshold-like, episodic-detail) and familiarity (continuous, no detail).
- Diana Yonelinas Ranganath 2007: hippocampal recollection vs perirhinal familiarity in human fMRI -- distinct neural substrates.
- Wixted Mickes 2010 signal-detection critique: continuous strength model can fit data but two-signal model fits ROC curves better.
- KEY INSIGHT: Option B + H combined is the brain's documented architecture. Strong prior.

### Hippocampal pattern separation vs pattern completion
- Marr 1971 / McNaughton-Morris 1987 / Yassa-Stark 2011 review: dentate gyrus pattern-separates similar inputs to distinct representations; CA3 pattern-completes partial cues to stored representations.
- Substrate analogue: cleanup-to-prototype = pattern completion (already present); per-atom-id distinctiveness = pattern separation (related to capacity / interference work).
- KEY INSIGHT: substrate familiarity (Option H) is pattern-completion-based; substrate recollection (Option B) requires pattern-separation-grade distinctiveness. Both are biologically grounded substrate primitives.

## Q3 -- Algebra-HRR codebook structural bias

The Findings 11 Layer 2 v2.1 observation that algebra-HRR mp_bulk_kl is 12x semantic-bge (algebra codebook is MORE structured than semantic) is mechanistically important here. A more-structured codebook means:

- M math atoms occupy a LOWER effective dimensionality in the N-dim algebra-HRR space (per Marchenko-Pastur deviation -- bulk-KL away from random-matrix prediction signals structure)
- Pairwise cosines among RANDOMLY-DRAWN sets of math atoms tend to a STABLE typical-cosine that is OFFSET from zero (concentration of measure on a structured manifold)
- The avg-pairwise-cosine statistic used in algebra_novelty therefore concentrates near a structural attractor whenever a document references ENOUGH cross-cutting atoms -- driving 1 - avg-pairwise-cosine to a saturated value INDEPENDENT of corpus content

This is the **structural-saturation mechanism** beneath Findings 15's algebra_novelty 1.04+. It is not a bug in the implementation -- it is a property of the metric on a structured codebook. The 13-category taxonomy + concept_links structure plausibly amplifies this (cross-cutting drills hit multiple categories; cross-category math-atom cosines are dominated by category-centroid geometry, not atom-specificity).

**Implication for option ranking.** Options B, F, H, J ALL avoid this metric. Option G replaces the metric with a bundle-space metric whose saturation behavior must be re-derived. Option E weights past it. Option I would learn around it. **Any option that keeps the avg-pairwise-cosine-of-named-atoms primitive will inherit this saturation regardless of other fixes.**

Relevant literature:
- Marchenko-Pastur deviation in structured codebooks (free-probability literature in the Tier-1 fields list above)
- Tracy-Widom edge fluctuations in random ensembles
- Concentration of measure on high-dim manifolds (Ledoux 2001; Vershynin 2018 high-dim probability)
- Substrate free-probability observability framework memory connects directly here: the mp_bulk_kl statistic IS a measurement of this structural bias.

## Falsifiable predictions

### Pre-registered thresholds (mandatory per lit-scan calibration penalty)

HARD_PASS for the recommended Option B+H architecture: AUROC on Set A vs Set B >= 0.85 AND AUROC on Set A_perturbed (paraphrase-rewritten ingested files) vs Set B >= 0.75.

HARD_FAIL for Option B+H: AUROC on Set A vs Set B < 0.65. This would refute the dual-process hypothesis for substrate-internal recognition; the failure mode would imply substrate retrieval is NOT distinguishing within-corpus from out-of-corpus content -- a much deeper finding worth its own drill.

HARD_PASS for Option G: AUROC on Set A vs Set B >= 0.85 AND backward-compat sanity check (algebra_novelty under new bundle-space definition still correlates positively with the OLD definition on cross-cutting content, r > 0.3) so we know we did not break upstream uses.

HARD_FAIL for Option G: AUROC < 0.65 OR backward-compat correlation < 0.0 (sign flip means we broke a different metric).

HARD_PASS for Option E (cheap day-1): post-ingest NOVEL fraction drops from 68.2% to below 50%. Mechanical, low-bar -- this is a partial fix not a structural one.

### Secondary structural prediction

If Q3's structural-saturation hypothesis is correct, ANY option that keeps avg-pairwise-cosine-of-named-atoms will show **algebra_novelty distribution invariant under corpus addition** when we ingest a second batch of drill files. We should observe pre-ingest-second-batch algebra_novelty distribution matches post-ingest-second-batch distribution within KS-test p > 0.5 -- confirming the metric is corpus-blind.

## Q5 -- Empirical signal that classification self-recognition WORKS

Beyond the AUROC primary metric, the **substrate-product** signal of working self-recognition is:

1. **Tier-A automatic for in-corpus content.** When substrate is asked to evaluate a research drill that IS in its corpus, the eval should return TIER-A without prompting. Currently substrate-eval cannot do this -- Findings 17 shows 68.2% NOVEL fraction on KNOWN-ingested content.

2. **Recollection-vs-familiarity decomposition is auditable.** A product user / auditor asks "did substrate recollect this fact (precise ingest record) or familiar-recognize it (similar to ingested content)?" -- substrate can answer because the two channels are explicit.

3. **5-tier progression Tier-4 self-extension gate.** Per substrate-on-substrate-5-tier-deliberate-progression memory, Tier 4 = self-extension. CLASSIFICATION self-recognition is a pre-req: if substrate cannot recognize that content X is already in its corpus, it cannot evaluate whether a self-proposed extension is NOVEL or RE-DERIVATION. Passing AUROC HARD_PASS on the recall_gap probe set is a STRUCTURAL gate for advancing to Tier 4.

4. **Stress probe -- adversarial paraphrase.** A self-recognition system that only matches surface form is brittle. Set A_perturbed (paraphrased ingested files) tests whether substrate recognizes its own knowledge under linguistic variation. Brain dual-process recognition handles this; substrate Option B alone will not; Option H alone may not; Option B+H is the architecture that the literature predicts will.

## Cross-thread synthesis

- **vs FINDINGS_08 + substrate-two-axes memory.** That finding showed semantic-vec and content-reference are ORTHOGONAL axes; substrate-distinguishing retrieval exploits BOTH. Option J operationalizes this for novelty. Option H + Option B operationalizes the recollection/familiarity dual-process which is a different decomposition of the same multi-channel intuition.
- **vs substrate-free-probability-observability-framework memory.** The mp_bulk_kl primitive that diagnosed algebra codebook structure also predicts WHY algebra_novelty saturates -- structural concentration. The same framework gives us a HARD_PASS check on Option G (recomputed mp_bulk_kl on bundle space should remain bounded; if it saturates similarly we have not actually fixed the geometry, just moved it).
- **vs benchmark-must-break-symmetry methodology rule.** The probe set (Set A vs Set B) must break the symmetry the mechanism targets. If Set A and Set B are drawn from the same surface-form distribution, recognition is testing surface form not substrate ingest-recall. Use mixed-source held-out drills (different agents, different dates) for Set B.
- **vs literature-is-not-oracle rule.** Dual-process recognition memory is the WELL-DOCUMENTED brain architecture -- but substrate is not a brain. The literature gives a STRONG PRIOR not an oracle. If empirical AUROC on Option B+H underperforms expectation, that is a DISCOVERY about substrate-specific recognition geometry, not a fix-the-bug failure.
- **vs drill-defeatism rule.** The original Findings 17 framing might be tempting to read as "self-recognition is architecturally hard" -- but FOUR independent option families (B, G, H, J) each have plausible substrate primitives and literature precedent. We have not exhausted the substrate-only path inventory; no architectural-ceiling claim is warranted.

## Substrate-product implications

- **Auditable AI memory subsystem differentiator.** Explicit recollection/familiarity decomposition is something LLM-based memory systems do not have. LLMs have continuous logprobs; substrate can have a STRUCTURED two-channel recognition primitive. This is direct product value for the auditable-memory thesis.
- **Self-recognition as Tier-4 gate.** Per 5-tier progression: cannot do self-extension without self-recognition. Closing Findings 17 is on the critical path.
- **v3 indexes architecture (3 indexes + RRF + intent router) absorbs Option J naturally.** Building the recognition classifier on top of the v3 indexes architecture is the unifying path.
- **Substrate-eval cycles speed up.** If self-recognition works, drills that re-derive previously-found results are caught BEFORE running -- saves compute.

## Citations (verified count)

- Yonelinas A.P. 2002. The nature of recollection and familiarity: A review of 30 years of research. Journal of Memory and Language 46:441-517. [recollection vs familiarity dual-process]
- Diana R.A., Yonelinas A.P., Ranganath C. 2007. Imaging recollection and familiarity in the medial temporal lobe: a three-component model. Trends in Cognitive Sciences 11:379-386.
- Wixted J.T., Mickes L. 2010. A continuous dual-process model of remember/know judgments. Psychological Review 117:1025-1054.
- Yassa M.A., Stark C.E.L. 2011. Pattern separation in the hippocampus. Trends in Neurosciences 34:515-525.
- Marr D. 1971. Simple memory: a theory for archicortex. Philosophical Transactions of the Royal Society B 262:23-81. [pattern completion]
- Scholkopf B., Platt J., Shawe-Taylor J., Smola A., Williamson R. 2001. Estimating the support of a high-dimensional distribution. Neural Computation 13:1443-1471. [one-class SVM]
- Scheirer W.J., de Rezende Rocha A., Sapkota A., Boult T.E. 2013. Toward open set recognition. IEEE TPAMI 35:1757-1772.
- Bendale A., Boult T.E. 2016. Towards open set deep networks (OpenMax). CVPR.
- Karpukhin V. et al. 2020. Dense passage retrieval for open-domain question answering (DPR). EMNLP.
- Khattab O., Zaharia M. 2020. ColBERT: Efficient and effective passage search via contextualized late interaction over BERT. SIGIR.
- Reimers N., Gurevych I. 2019. Sentence-BERT: Sentence embeddings using Siamese BERT-networks. EMNLP.
- Chen T., Kornblith S., Norouzi M., Hinton G. 2020. A simple framework for contrastive learning of visual representations (SimCLR). ICML.
- He K. et al. 2020. Momentum contrast for unsupervised visual representation learning (MoCo). CVPR.
- Plate T.A. 2003. Holographic reduced representations. CSLI publications. [HRR superposition + cleanup]
- Eliasmith C. 2013. How to build a brain: A neural architecture for biological cognition. Oxford. [semantic pointer architecture]
- Vershynin R. 2018. High-Dimensional Probability: An Introduction with Applications in Data Science. [concentration of measure]
- Ledoux M. 2001. The Concentration of Measure Phenomenon. AMS.
- Yang J., Zhou K., Li Y., Liu Z. 2021. Generalized out-of-distribution detection: a survey. [OSR + OOD]

Verified count: 18.

## Recommendation -- beyond Option B

**Ship Option E as immediate day-1 fix (5 LOC, partial; clears the MAX gate hiding semantic_novelty).**
**Build Option B + Option H combined as the architectural fix (dual-process recognition, ~80 LOC, brain-validated, lit-anchored). This is RANK 1.**
**Plan Option G (bundle-space algebra_novelty redefinition) as a Tier-1 structural cleanup next sprint -- highest structural leverage, addresses Q3 root cause; sequence after B+H lands so B+H gives us ground truth to validate G against.**

Do NOT do Option I alone (supervised end-to-end) -- introduces LLM-as-judge-adjacent supervised artifact. Option F (parallel supervised head) is OK as a benchmark only.

Recommended pre-registered next experiment: build Set A (449 ingested) + Set B (50 held-out drills, mixed-source) + Set A_perturbed (paraphrase rewrites of 50 ingested), measure AUROC for Options E, B, H, B+H, G in a single CPU eval pass. Anchor: `substrate_eval_recall_gap_option_eval_2026-06-11`. Decisive within 30 minutes substrate-CPU.

Anchor candidate names (rank-ordered) -- handed off to exp_dev:
1. substrate_eval_recall_gap_dual_process_B_plus_H_2026-06-11  (RANK 1 -- ship)
2. substrate_eval_recall_gap_bundle_space_G_2026-06-11        (RANK 2 -- structural cleanup)
3. substrate_eval_recall_gap_weighted_avg_E_2026-06-11        (day-1 partial, ship in parallel)
4. substrate_eval_recall_gap_hierarchical_J_2026-06-11        (option J -- 4-channel ablation)
5. substrate_eval_recall_gap_supervised_F_2026-06-11          (benchmark only)
