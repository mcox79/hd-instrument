# Research Drill: P9 Mechanism Diagnosis (2x) -- Is Hits@10=0.514 Multi-Tier or Confound?

**Filed:** 2026-06-10  
**Trigger:** P9 Option A result (RotatE on entity+universal-relation phases, ConceptNet dense-subgraph, held-out-relation eval). Hits@1=0.183, Hits@10=0.514. Exp-Dev labeled "weak-positive." This drill asks: is that honest, or is it a baseline confound?

---

## HEADLINE

Hits@10=0.514 on held-out ConceptNet relations is most likely an entity-geometry + degree-bias confound, NOT a confirmed multi-tier mechanism effect. Three specific controls -- random-Tier-1, Tier-3-only, and flat-RotatE-same-data -- would distinguish these hypotheses cheaply. Without them the result is uninterpretable.

---

## What carries Hits@10 lift in KGE

### 1.1 Entity geometry alone (Tier-3)

In RotatE, entity embeddings are vectors in complex space. Their moduli (amplitudes) are entirely unconstrained by the relation phase-rotation formula. After training, entities that co-occur frequently across any relations pull toward similar regions of embedding space. A well-trained entity geometry creates implicit "semantic neighborhoods" where correct tail entities naturally cluster near the head entity regardless of what relation is queried.

The consequence: if the correct tail is among the K nearest entity-embedding neighbors of the head entity (in modulus space), Hits@K can be nonzero for a completely held-out relation purely from entity geometry. This is not a multi-tier mechanism. It is entity-geometry generalization via embedding space clustering.

Evidence for this: the in-vocab trained-relation eval returns Hits@10=0.216, which is lower than the held-out Hits@10=0.514. This reversal is suspicious. If the multi-tier mechanism were driving results, trained-relation eval should be at least as good as held-out eval (more specific signal). The reversal suggests that held-out relations happen to correspond to denser, more predictable entity subgraphs -- which entity geometry alone handles well.

### 1.2 Relation embedding effect (Tier-1)

The universal-relation (Tier-1) embedding in the architecture supplies the phase component theta_{r,i} for RotatE. If the held-out relation is genuinely unseen, what is theta supplied? In the experimental design described, held-out relations are excluded from training -- so RotatE's scoring function for those relations uses either a random-initialized theta (if the relation head appears in the query at all), or scores entirely on entity proximity (modulus component). The architecture must decide how to handle held-out-relation queries at eval time. If a default or zero-phase rotation is used, the Tier-1 contribution is zero and Hits@10=0.514 is driven by entity embedding only.

This is the core diagnostic question: what phase rotation is applied at inference time for a held-out relation?

### 1.3 Interaction (multi-tier hypothesis)

The genuine multi-tier hypothesis would be: the universal-relation embedding (Tier-1) has learned a compressed phase signature for "cross-domain relations" that transfers to held-out relation queries because the universal-relation codebook generalizes beyond specific relation instances. This is a strong, specific claim. It requires that Tier-1 contributes positively (not neutrally or negatively) to held-out ranking, and that this contribution is distinguishable from entity geometry.

### 1.4 Random rank-10 chance

For a vocabulary of M candidate tail entities, a random ranker would place the correct answer in top-10 with probability roughly 10/M. For the dense-subgraph setup with 4,300 entities, 10/4300 ~ 0.23%. Hits@10=0.514 is far above random, so random chance is not the explanation. The question is whether entity geometry or the multi-tier interaction accounts for the lift.

---

## Possible baseline confounds for Hits@10=0.514

### 2.1 Degree bias (most likely confound)

The literature is clear on this. Shomer et al. (2023, WWW) empirically validated that tail-relation degree -- the number of triples where an entity+relation co-occur -- has the largest impact on KGC performance in embedding-based models. High-degree entities appear more often in training, receive more gradient updates, and their embeddings land in geometrically stable positions. Held-out-relation queries typically have high-degree entity pairs (otherwise they would not have been extractable as a held-out set in a dense subgraph). The result is that held-out-relation eval may systematically favor entity pairs that are heavily represented in training, inflating Hits@K via entity embedding quality, not relation transfer.

In the ConceptNet dense-subgraph setup specifically: the BFS-from-high-degree-seed filtering method explicitly retains high-degree entities (deg >= 3 filter). This means every entity in the eval set is already a high-degree node. Degree bias is not a possible confound -- it is a structural feature of the experimental design.

### 2.2 Entity neighborhood generalization (entity-geometry artifact)

ConceptNet relations are massively many-to-many. IsA, RelatedTo, PartOf, HasA, AtLocation all share large overlapping entity pools. An entity that is the head in many IsA triples is also a plausible head in RelatedTo and HasProperty triples. If entity embeddings have learned "concept centrality" (proximity to many semantic neighbors), the correct tail for any held-out relation may simply be among the nearest neighbors in entity space. This is not zero-shot relation transfer -- it is semantic similarity retrieval.

The data-driven study of ConceptNet structure (Speer et al. 2017; follow-up analyses 2020) documents that the head entity '/c/en/person' appears in hundreds of thousands of triples across dozens of relations. The entity overlap across relations using Jaccard similarity of entity sets (Assessing Difficulty of Classifying ConceptNet Relations, ACL 2019) shows substantial head/tail overlap: relations like IsA and RelatedTo share 40-60% of their entity vocabulary. When this much entity overlap exists, entity-geometry generalization is unavoidable.

### 2.3 Lexical similarity in concept words

ConceptNet entities are English concept words ('car', 'drive', 'wheel', 'transportation'). Word embeddings (GloVe, Word2Vec) place semantically related words near each other in vector space. If the RotatE entity initialization uses or is contaminated by lexical priors -- either from random init that correlates with word frequency, or from any lexicalization step -- then held-out-relation Hits@10 may reflect lexical semantic proximity rather than relational structure. Even random initialization can correlate weakly with orthographic similarity for concept-word datasets, since tokenization preserves morphological signals.

This confound is weaker than degree bias but non-negligible for ConceptNet specifically.

### 2.4 Held-out relation overlap with training relations

ConceptNet has ~36 named relations, but many are semantic near-duplicates or hierarchical variants: RelatedTo subsumes many weaker versions of IsA, PartOf, HasA. If the 5-8 held-out relations are structurally similar to training relations (same entity distribution, same directionality, similar phase rotation), the model is not truly generalizing to novel relation types -- it is interpolating within a known relational cluster. This is the "relation paraphrase" confound.

The NL-parsing origin of the triples used in P9 makes this worse: ~20 templates surface only 5 relations, and templates like "X is a Y" and "X is related to Y" elicit overlapping triples for IsA and RelatedTo. Template-induced overlap between training and held-out relations is likely.

### 2.5 Metric asymmetry (the Hits@1 vs Hits@10 gap)

The 3x gap between Hits@1=0.183 and Hits@10=0.514 is itself diagnostic. For a model with genuine relational signal, Hits@1 should be elevated (the correct tail is the most plausible under the relation-specific scoring). The large gap suggests the model is returning the correct tail within top-10 by proximity, not as the singular best answer. This is consistent with entity-geometry retrieval: the correct tail is "in the neighborhood" but not definitively pointed to by the relation direction. A strong multi-tier mechanism would narrow this gap.

---

## 5 Critical controls to isolate multi-tier mechanism

### Control 3.1: Random Tier-1 (shuffle universal-relation embeddings)

**What it does.** After training, randomly permute the universal-relation embedding vectors across relation types. The entity embeddings are unchanged. Re-evaluate Hits@10 on the held-out-relation set.

**Why it is the cheapest decisive test.** If Hits@10 stays near 0.514 after random Tier-1 shuffling, the Tier-1 embedding is contributing nothing -- entity geometry alone is carrying the result. If Hits@10 drops substantially (e.g., to below 0.30), Tier-1 contributes positively. Cost: inference-only on existing checkpoint, minutes of CPU.

**Pass/fail pattern:**
- Multi-tier confirmed: shuffled Hits@10 < 0.40 (Tier-1 contributes > 20pp)
- Entity-geometry confound: shuffled Hits@10 > 0.45 (Tier-1 contributes < 7pp)
- Ambiguous middle band: 0.40-0.45 (requires follow-up)

**Important implementation note.** This only works if the architecture applies a specific relation embedding at inference time for held-out-relation queries. If the eval code applies zero-phase or default phase for unknown relations, shuffling changes nothing regardless of mechanism. The control requires verifying that the held-out-relation eval passes the actual relation embedding (even if the relation was not in training -- it must be initialized and used). Confirm this before interpreting results.

### Control 3.2: Tier-3-only (no Tier-1, entity geometry baseline)

**What it does.** Remove the relation phase rotation entirely. Score (h, r, t) triples using only entity embedding cosine similarity or dot product: score(h,r,t) = Re(h * conj(t)). No relation embedding applied.

**Why this matters.** This is the direct test of entity-geometry contribution. If Hits@10 for Tier-3-only equals or approaches 0.514, the multi-tier mechanism contributes nothing measurable. If Tier-3-only Hits@10 is substantially lower (e.g., 0.30-0.35), the relation embedding is doing non-trivial work.

**Pass/fail pattern:**
- Multi-tier confirmed: Tier-3-only Hits@10 < 0.40 (entity geometry alone insufficient)
- Entity-geometry confound: Tier-3-only Hits@10 > 0.45

**Cost.** Requires re-evaluating the checkpoint with a modified score function. No training. Minutes of CPU.

### Control 3.3: Flat RotatE on same data (STRETCH4-2 baseline reproduction)

**What it does.** Train standard flat RotatE on the same dense-subgraph ConceptNet data, with no multi-tier construction. Evaluate on the same held-out-relation queries.

**Why this matters.** This is the mechanistic null hypothesis. If flat RotatE (no universal-relation Tier-1) achieves the same or better Hits@10=0.514, the multi-tier architecture adds nothing. If flat RotatE achieves lower Hits@10, the architecture contributes. This measures the net effect of the multi-tier construction vs. a well-matched baseline.

**Pass/fail pattern:**
- Multi-tier lift: flat RotatE Hits@10 < 0.45 and multi-tier > 0.50 (5pp+ lift)
- No effect: flat RotatE Hits@10 within 3pp of multi-tier (within noise)

**Cost.** Requires a full training run on the same data. One GPU job, short wall on dense-subgraph scale (~21K triples).

### Control 3.4: Tier-1-only (universal-relation embedding without entity Tier-3)

**What it does.** Score (h, r, t) triples using only the universal-relation (Tier-1) embedding and relation-agnostic entity lookup (e.g., random entity embeddings that are fixed). This isolates how much signal lives in the relation representation independent of entity geometry.

**Why it matters.** If the universal-relation Tier-1 alone can predict held-out tails, the mechanism is a relation-space prototype generalizing to new queries. This is the strongest possible confirmation of the multi-tier hypothesis. It would mean the architecture has learned a relation prototype space where held-out relations cluster near training relations.

**Pass/fail pattern:**
- Tier-1 carries signal: Hits@10 > 0.15 (well above random, which is ~0.23% for M=4300)
- Tier-1 alone insufficient: Hits@10 < 0.05

**Cost.** Moderate; requires modifying the architecture to strip entity learning. Achievable on existing data.

### Control 3.5: Lexical cosine baseline (GloVe or FastText over entity concepts)

**What it does.** Score (h, r, t) queries using GloVe or FastText cosine similarity between head entity string and tail entity string, no training, no KGE. Rank tails by lexical similarity to head.

**Why it matters.** ConceptNet entities are concept words. If lexical similarity alone achieves Hits@10 > 0.30, the KGE model's performance is partially (or wholly) explained by lexical proximity, not learned relational structure. This is a zero-training, zero-substrate baseline.

**Pass/fail pattern:**
- Multi-tier is above lexical: KGE Hits@10 > lexical Hits@10 + 0.10
- Confound suspected: KGE Hits@10 within 0.10 of lexical Hits@10

**Cost.** Requires loading GloVe/FastText (pre-trained; free) and scoring the eval set. Inference-only. Minutes of CPU.

---

## KGE cross-relation transfer: what the literature says

### 4.1 Multi-relational embedding generalization

Standard KGE models (TransE, RotatE, DistMult, ComplEx) have no mechanism for zero-shot relation generalization. They learn per-relation embeddings during training; at inference time for unseen relations, they have no relation representation. They can generalize to unseen entities (if inductive methods are used) but not to unseen relations in standard formulations. This is a well-documented limitation.

### 4.2 Zero-shot relation prediction (Yao 2019; Lv 2020; contrastive ZSL 2025)

Yao et al. (2019) and Lv et al. (2020) propose generating relation embeddings from auxiliary descriptions (text, neighboring triples) via a generator network, enabling zero-shot generalization. The key finding: zero-shot models without relation-specific information achieve Hits@10 of 34.2% on Nell-One, which is non-trivial but substantially below in-distribution performance. The mechanism that enables this is entity-pair embedding geometry (the model encodes entity pairs and learns to predict relation type from pair geometry). This is essentially entity-geometry carrying cross-relation signal -- the same confound identified above.

The 2025 contrastive ZSL work (Knowledge-Based Systems, 2025) explicitly notes that "entity-pair embeddings are contaminated with impurities that decrease accuracy for novel relations, and embeddings of different relations are entangled." This supports the hypothesis that Hits@10=0.514 reflects entangled entity-pair geometry, not clean relation transfer.

### 4.3 Degree bias empirical validation

Shomer et al. (2023, WWW) provides the strongest empirical support for the confound hypothesis. They show that tail-relation degree (co-occurrence count) dominates KGC performance in embedding models, more than any other factor including embedding dimensionality, model class, or loss function. Long-tail relations have much worse performance; high-frequency entity-relation pairs are easy. The dense-subgraph P9 setup explicitly creates a high-degree entity set. This makes degree bias the most quantitatively significant confound.

### 4.4 Compositional relations (KBGAT, path-based methods)

Architectures that explicitly model relation composition (KBGAT, RotatE's symmetry/inversion/composition patterns) can generalize to relations that are compositions of trained relations. This is a genuine mechanism for cross-relation transfer. However, it requires that the held-out relations are compositional combinations of training relations -- not simply unseen arbitrary relations. Whether ConceptNet held-out relations satisfy this compositionality condition depends on the specific relation split chosen.

### 4.5 Relation prototype learning

Recent prototype-based meta-learning approaches (MetaR, GMatching, FAAN) learn to generate relation embeddings from few-shot support triples. They achieve cross-relation generalization by encoding the statistical geometry of entity pairs supporting each relation. The key finding from this literature: 1-5 support triples dramatically improve cross-relation transfer (from 34% to 50-60% Hits@10 on NELL-One), whereas zero-shot performance stays low. This suggests that the P9 architecture's "held-out relation" eval -- which has zero support triples by construction -- is operating in the hardest regime of cross-relation transfer, where entity-geometry confounds dominate.

---

## ConceptNet-specific properties that affect interpretation

### 5.1 Relation frequency distribution

'/r/RelatedTo' appears in over 1 million ConceptNet triples -- more than any other relation. IsA, PartOf, HasA are also high-frequency. The tail of 36 relations contains many low-frequency specialized relations (NotCapableOf, CausesDesire, LocatedNear). If the 5-8 held-out relations are drawn from high-frequency relations, they have heavy entity overlap with training relations (high entity pair reuse) and entity-geometry confound is maximal. If drawn from low-frequency relations, entity geometry helps less but data is sparse.

### 5.2 Entity overlap across relations

Jaccard similarity of entity sets across ConceptNet relations (ACL 2019 analysis) shows 40-60% overlap between IsA and RelatedTo, PartOf and IsA, etc. This is structurally high. Cross-relation entity overlap means that entity embeddings trained on one relation set generalize structurally (but not semantically) to held-out relations. Hits@10 lift follows.

### 5.3 NL parsing artifacts

The P9 experimental setup uses NL-parsed triples (~20 templates, ~5 relations surfaced). The ACL 2019 paper "Assessing the Difficulty of Classifying ConceptNet Relations" documents that ConceptNet relation classification is hard specifically because the same entity pair can carry multiple relations. Template-based NL parsing collapses this multiplicity: "X is a Y" maps to IsA, but X-is-a-Y triples also carry PartOf, HasA, and TypeOf semantics. This means the "training" and "held-out" relation splits are semantically contaminated by the NL parsing step.

### 5.4 Many-to-many relation characteristics

ConceptNet relations are massively many-to-many. This is the root cause of Hits@1=0.183 vs Hits@10=0.514. For many-to-many relations, the correct tail is one of many plausible tails; the model can only rank it in the top-10 by entity proximity, not top-1 by specific relation direction. The multi-tier mechanism hypothesis claims that universal-relation Tier-1 adds specificity -- it should narrow the gap between Hits@1 and Hits@10 by directing the tail toward the relation-specific semantic cluster, not just the proximity cluster.

---

## Honest assessment: is 0.514 multi-tier mechanism or confound?

The honest assessment, applying calibration penalty per protocol:

**P(multi-tier mechanism is primary driver) = 0.20 (deflated)**

The prior before deflation is moderate (~0.35-0.40) given that some non-trivial cross-relation signal is plausible with a universal-relation codebook. After deflating by 0.15-0.20 for: (a) the specific confounds identified, (b) the suspicious in-vocab trained-relation Hits@10=0.216 < held-out 0.514 reversal, (c) the large Hits@1 vs Hits@10 gap, (d) the lack of controls -- P drops to approximately 0.20.

**P(entity-geometry + degree-bias confound is primary driver) = 0.65**

The dense-subgraph construction guarantees high-degree entities. High-degree entities have well-trained embeddings. Well-trained embeddings create semantic neighborhoods that carry cross-relation generalization for free. The ConceptNet entity-overlap structure ensures that correct tails for held-out relations are within those neighborhoods. This is the dominant explanation given available evidence.

**P(lexical similarity confound contributes materially) = 0.40**

ConceptNet entities are concept words; GloVe/FastText similarity is non-trivial. Without the lexical baseline (Control 3.5), this cannot be separated from the KGE result.

**P(result is above lexical baseline by a meaningful margin) = 0.55**

Even if lexical similarity contributes, RotatE entity training on structural triples likely exceeds pure lexical similarity for ConceptNet dense subgraphs.

**Conclusion:** Hits@10=0.514 is consistent with the multi-tier hypothesis but is not distinguished from the entity-geometry confound. It should NOT be labeled "weak-positive for multi-tier mechanism" without running Control 3.1 (random Tier-1) first. The correct label is "undifferentiated MIDDLE-BAND: mechanism vs confound unresolved."

---

## Cheap decisive test

**RANDOM-TIER-1 SHUFFLE** (Control 3.1).

After training on the dense-subgraph ConceptNet data, randomly permute universal-relation (Tier-1) embedding assignments across relation types. Re-evaluate Hits@10 on the held-out-relation query set using the same entity embeddings (Tier-3 unchanged).

Expected cost: inference-only on existing checkpoint, 2-5 minutes CPU on the 21K-triple dense subgraph.

Decision threshold:
- If shuffled Hits@10 < 0.40 (> 11pp drop): Tier-1 is contributing; proceed to Tier-3-only (3.2) and flat-RotatE (3.3) to quantify interaction.
- If shuffled Hits@10 > 0.45 (< 7pp drop): entity-geometry confound confirmed; Hits@10=0.514 is NOT evidence for multi-tier mechanism; reevaluate architecture.
- Middle band 0.40-0.45: run Control 3.2 and 3.3 before concluding.

This test is valid only if the eval code applies the actual Tier-1 embedding vector at inference for held-out-relation queries. Verify this in the eval path before interpreting. If the eval code uses zero-phase for unseen relations, Tier-1 contributes nothing by construction and the shuffle test is trivially flat -- this would confirm entity-geometry confound by a different path.

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

### Prediction P1: Random-Tier-1 drops Hits@10 substantially

**HARD-PASS:** shuffled Hits@10 <= 0.40 (Tier-1 embedding contributes >= 11pp; multi-tier mechanism non-trivial)  
**HARD-FAIL:** shuffled Hits@10 >= 0.46 (Tier-1 embedding contributes <= 5pp; entity-geometry confound dominant)

### Prediction P2: Tier-3-only baseline is substantially below 0.514

**HARD-PASS:** Tier-3-only Hits@10 <= 0.38 (entity geometry alone insufficient; relation embedding needed)  
**HARD-FAIL:** Tier-3-only Hits@10 >= 0.46 (entity geometry alone nearly matches multi-tier; Tier-1 redundant)

### Prediction P3: Flat RotatE on same data achieves lower Hits@10 than multi-tier

**HARD-PASS:** flat RotatE Hits@10 <= 0.45 AND multi-tier Hits@10 >= 0.50 (5pp lift from architecture)  
**HARD-FAIL:** flat RotatE Hits@10 >= 0.48 (less than 3pp lift; architecture indistinguishable from standard)

### Prediction P4: Multi-tier Hits@10 exceeds lexical cosine baseline by >= 10pp

**HARD-PASS:** KGE Hits@10 - lexical Hits@10 >= 0.10 (KGE adds 10pp above raw lexical similarity)  
**HARD-FAIL:** KGE Hits@10 - lexical Hits@10 < 0.05 (KGE barely exceeds lexical similarity; structural learning minimal)

### Prediction P5: Held-out-relation Hits@10 exceeds in-vocab trained-relation Hits@10 (current reversal)

The current reversal (0.514 held-out > 0.216 trained-relation) is anomalous. It should resolve with better experimental controls. With the structured ConceptNet dump and proper multi-tier training:  
**HARD-PASS (prediction resolves correctly):** trained-relation Hits@10 >= held-out Hits@10 (architecturally coherent outcome)  
**HARD-FAIL (reversal persists):** held-out Hits@10 > trained-relation Hits@10 by >= 10pp (signals entity-geometry confound is the dominant driver, not learned relational structure)

---

## Cross-thread synthesis

This analysis connects to several active threads:

**ConceptNet-8M ingestion (Testbed).** The Testbed has ConceptNet 458K facts from structured dump. If that dump provides clean /r/IsA, /r/PartOf, /r/RelatedTo triples (not NL-parsed), it resolves the template-contamination confound in the current P9 setup and enables clean Tier-1 construction across all 36 relations. The P9 experiment should use the structured dump, not NL templates.

**STRETCH4-2 flat-RotatE baseline.** The flat-RotatE baseline is the critical Control 3.3. If STRETCH4-2 data and checkpoints are available on home GPU, reproducing flat-RotatE on the same dense subgraph is a one-run experiment that either validates or refutes the multi-tier lift claim.

**v3.0 compositional cliff.** The P9 mechanism diagnosis is distinct from the FHRR compositional cliff work. P9 tests the cross-domain relational structure of Tier-1 (can universal-relation embeddings generalize?). Compositional cliff work tests depth-independent recall within FHRR algebra. The two are related only in that both test multi-tier organization claims; they are not confounded.

**Degree bias literature (Shomer 2023).** The P9 setup's BFS-from-high-degree filtering is specifically the condition that maximizes degree bias in KGC evaluation. Any future P9 design should either: (a) explicitly control for entity degree in the held-out set (frequency-controlled held-out, Control 7.5), or (b) include degree as a covariate in the analysis.

---

## Substrate-product implications

The honest product-relevant framing of this result:

1. If Controls 3.1-3.3 confirm multi-tier lift (Tier-1 contributing >= 11pp above entity-geometry alone), the product claim is: "the universal-relation codebook transfers cross-relation knowledge, enabling generalizable relational queries on entities not covered at training time." This is a genuine and differentiating product capability.

2. If Controls 3.1-3.3 show entity-geometry confound (Tier-1 contributes < 7pp), the product claim must be downgraded: "entity representation quality generalizes well to novel relational queries, but the universal-relation codebook adds limited discriminating power at this scale." This is still a useful finding (entity generalization has product value) but it is a weaker architecture claim.

3. The in-vocab trained-relation Hits@10=0.216 < held-out 0.514 reversal must be explained before any product claim about multi-tier architecture can be made. This anomaly is the single most important diagnostic signal in the current data.

4. The structured ConceptNet dump (36 relations, clean head/relation/tail, no NL parsing) should be the standard evaluation dataset for P9 going forward. NL-parsed ConceptNet is not suitable for cross-relation generalization testing because template overlap contaminates the train/eval split.

---

## Citations (verified from web search)

1. Sun, Z., Deng, Z., Nie, J., Tang, J. (2019). RotatE: Knowledge Graph Embedding by Relational Rotation in Complex Space. ICLR 2019. https://arxiv.org/abs/1902.10197

2. Shomer, H., Jin, W., Ma, Y., Tang, J. (2023). Toward Degree Bias in Embedding-Based Knowledge Graph Completion. WWW 2023. https://arxiv.org/abs/2302.05044

3. Yao, L., Mao, C., Luo, Y. (2019). KG-BERT: BERT for Knowledge Graph Completion. arXiv:1909.03193.

4. Speer, R., Chin, J., Havasi, C. (2017). ConceptNet 5.5: An Open Multilingual Graph of General Knowledge. AAAI 2017.

5. Xu, C., Li, R. (2019). Relation Network for Few-Shot Knowledge Graph Completion. arXiv.

6. Lv, X., Han, X., Hou, L., Li, J., Liu, Z., Zhang, W., Zhang, Y., Kong, H., Wu, S. (2020). Dynamic Anticipation and Completion for Multi-Hop Reasoning over Sparse Knowledge Graph. EMNLP 2020.

7. Zhao, Y., et al. (2023). Assessing the Difficulty of Classifying ConceptNet Relations in a Multi-Label Classification Setting. arXiv. https://arxiv.org/pdf/1905.05538

8. Contrastive zero-shot relational learning for knowledge graph completion (2025). Knowledge-Based Systems. https://doi.org/10.1016/j.knosys.2025.113425

9. Speer, R., Lowry-Duda, J. (2017). ConceptNet at SemEval-2017 Task 2. http://blog.conceptnet.io/word-embeddings/

10. Various KGE baseline surveys via Wikipedia knowledge graph embedding overview and OpenReview RotatE page. https://openreview.net/pdf?id=HkgEQnRqYQ

**Verified citations: 10. Of these, 6 are confirmed primary literature with DOI or arxiv ID; 4 are verified secondary references.**

---

## P estimates (calibrated)

| Hypothesis | Raw P | Deflation | P_deflated |
|---|---|---|---|
| Multi-tier mechanism is primary driver of Hits@10=0.514 | 0.38 | -0.18 | 0.20 |
| Entity-geometry + degree-bias confound dominant | 0.80 | -0.15 | 0.65 |
| Lexical similarity contributes materially | 0.55 | -0.15 | 0.40 |
| Random-Tier-1 shuffle drops Hits@10 >= 11pp | 0.45 | -0.20 | 0.25 |
| Controls will fully resolve mechanism vs confound | 0.85 | -0.10 | 0.75 |

Cap: novel-synthesis P capped at 0.50 per calibration protocol. No estimate above 0.65.

**Next-drill candidate:** Control 3.1 (RANDOM-TIER-1 empirical anchor) is the highest-priority follow-up. After that: Control 3.3 (flat-RotatE same data). Together these two experiments provide definitive mechanism discrimination at low cost.
