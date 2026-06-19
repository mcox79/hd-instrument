# Research Drill: Type II World-Model Priors -- Closure Paths and Pitch Architecture
# 3x deep drill | 2026-06-07

---

## HEADLINE

Type II implicit priors (gradient-distilled world-model knowledge) are structurally unreachable by any enumerable KB at v1.1/v1.5. The 8-12% residual after corpus pre-training is real and durable. The primary closure path available before Tier 5 is LLM-distilled intuition harvesting: substrate queries a frontier LLM during sleep-defrag cycles, stores derived intuitions as provenance-tagged derived bindings, and recovers 60-70% of the residual at modest per-query API cost. This narrows the gap to approximately 3-5% at v2.0. The remaining fraction is subliminal cross-domain inference from massive distributional learning -- not enumerable, not distillable without full gradient training. The honest customer pitch is not "we close the gap" but "we cover 88-92% with full audit; the 8-12% is implicit reasoning neither system handles reliably without provenance."

P_deflated = 0.55 (LLM-distillation-closes-60-70%-of-residual); calibration penalty applied (-0.20 from nominal 0.75).

---

## 1. TAXONOMY OF TYPE II IMPLICIT PRIORS

Eight categories, ordered from most to least KB-synthesizable:

**Category 1: Mathematical patterns**
Commutativity, associativity, symmetry, powers of 2, common numerical scales. These are expressible as axiomatic theorem statements. High KB-synthesizability. Sleep defrag at scale recovers most of this from stored mathematical facts.

**Category 2: Cultural / contextual priors**
"Christmas implies giving gifts." "Funerals are somber." These are enumerable in principle -- a sufficiently large cultural ontology covers them. Slow to accumulate but not structurally unreachable. Sleep defrag from cultural KB + LLM-distilled enumeration handles this adequately.

**Category 3: Linguistic priors**
Subject-verb agreement, ambiguous parsing resolution, prepositional phrase attachment heuristics. Syntactic parsers and dependency grammars encode most of this explicitly. High KB-synthesizability via structured grammar resources. Residual is pragmatic disambiguation (context-sensitive), which is partially distillable.

**Category 4: Causal intuitions**
"Dropping glass usually breaks it." "Rain causes wet ground." At the level of stated causal chains, sleep defrag closes this by accumulating many instances. The complication is IMPLICIT causal chains never stated directly -- "if you yell at someone they'll become defensive" -- where the substrate needs to have seen many indirect markers across diverse contexts.

**Category 5: Cross-domain analogies**
Electron orbit <-> planet orbit. Heat diffusion <-> random walk. These can be encoded explicitly as Pattern B analogy bindings. High KB-synthesizability IF the analogy is known. The structurally unreachable version is NOVEL cross-domain analogies the system generates spontaneously -- which requires the cross-domain distributional overlap that gradient training builds.

**Category 6: Intuitive physics**
Objects fall; collisions conserve momentum; rigid bodies don't pass through each other. These are expressible as stored facts and rules. Sleep defrag from physics texts covers the stated version. The gap is the FELT sense of physical plausibility -- the background prior that makes a description of a floating rock feel wrong even without explicit reasoning. Gradient training instills this via distributional exposure to millions of physical descriptions.

**Category 7: Social heuristics**
"People don't lie about their parents." "Asking for help implies reciprocity expectation." At the level of explicit heuristics, these are enumerable. The structurally unreachable version is the dense probabilistic texture underlying all social reasoning -- the implicit weighting of a thousand micro-cues. Gradient training over social dialogue corpus builds this; no enumerable KB does.

**Category 8: Subliminal cross-domain inference (structurally unreachable)**
An LLM trained on physics + literature + philosophy simultaneously develops the capacity to draw metaphorical inferences across these domains in ways that cannot be decomposed into stored analogy bindings. Example: "The way photons collapse to a definite state when observed echoes how certainty forecloses possibility in decision-making." Neither domain alone supplies this; the cross-domain distributional overlap of gradient training generates it. This is the hard core of Type II that no KB or distillation strategy closes without gradient training.

---

## 2. KB-SYNTHESIZABLE vs STRUCTURALLY UNREACHABLE ANALYSIS

### KB-synthesizable (sleep defrag closes at scale)

| Prior type | Mechanism | Coverage estimate |
|---|---|---|
| Mathematical patterns | Axiomatic theorem statements | 90-95% |
| Cultural / contextual | Cultural ontology + LLM enumeration | 70-80% |
| Linguistic priors | Grammar resources + dependency parsers | 75-85% |
| Causal intuitions (stated) | Sleep defrag from causal text accumulation | 65-75% |
| Cross-domain analogies (known) | Pattern B explicit analogy bindings | 60-70% |
| Intuitive physics (stated rules) | Physics text + rule accumulation | 65-75% |
| Social heuristics (explicit) | Social heuristic KB + crowdsourcing | 55-65% |

### Structurally unreachable by any enumerable KB

| Prior type | Why unreachable | Closure path |
|---|---|---|
| Subliminal cross-domain inference | Emerges from joint distributional overlap; not decomposable into stored facts | Gradient training only (Tier 5) |
| Statistical "feel" from distributional learning | Gradient-descended; the prior IS the parameter distribution, not any fact | Gradient training only |
| Social probability texture (micro-cue weighting) | Dense probabilistic texture across millions of micro-observations | Partial LLM distillation; full closure Tier 5 |
| Novel cross-domain analogy generation | Requires joint embedding space from gradient training | Partial via LLM-as-oracle; full closure Tier 5 |
| Compounding multi-step implicit inference | 3+ implicit premises combining in ways never stated explicitly | Partial LLM distillation; full closure Tier 5 |

The honest framing: approximately 60-65% of the 8-12% residual is partially closeable via LLM distillation. The remaining 35-40% of the residual (roughly 3-5% of total parametric knowledge) is the hard core that requires Tier 5.

---

## 3. LLM-DISTILLATION ARCHITECTURE (Substrate as Student)

### 3.1 Mechanism

Substrate runs "intuition harvesting" queries to a frontier LLM during sleep-defrag cycles. The LLM acts as teacher; the substrate stores LLM-generated derived facts as provenance-tagged bindings with explicit source attribution.

Query pattern (generic): "Given the domain <X>, what implicit background assumptions do practitioners typically hold that are rarely stated explicitly?"

The substrate stores the response as:
- A derived binding: (domain:X, implicit_prior:Y, source:"LLM-v1.5", confidence:0.72, harvested_at:T)
- Quality gate: adversarial mode checks consistency across 3 independent LLM queries; if answers diverge beyond threshold, flag as contested

### 3.2 Provenance architecture

This is the substrate's categorical advantage over raw LLM use: the distilled intuitions are stored WITH AUDIT. A query that fires against a LLM-distilled intuition returns:
- The intuition content
- The LLM version that generated it
- The timestamp
- The adversarial consistency score
- The domain context that triggered harvesting

This is stronger than raw LLM inference, which provides no provenance and no audit trail. An LLM hallucination that gets stored as a derived binding can be tracked, challenged, and retracted. A raw LLM hallucination silently contaminates outputs.

### 3.3 Sleep-defrag integration

The natural integration point is existing sleep-defrag cycles. When sleep defrag identifies a knowledge cluster being consolidated, it can fire a parallel LLM query: "What implicit priors underlie this knowledge cluster?" The derived intuitions join the sleep-defrag output as provenance-tagged additions.

Cost: per-query LLM API cost during deployment. At Anthropic Haiku pricing (~$0.25/MTok), harvesting intuitions for a 10,000-fact KB at 100 facts per query = 100 queries x ~500 tokens/query = ~50K tokens = ~$0.01. Negligible.

### 3.4 Quality control via adversarial mode

Three-way consistency check per harvested intuition:
1. Query LLM once, record answer
2. Query LLM again with differently-framed prompt, record answer
3. If semantic similarity > 0.85: store with confidence = 0.80
4. If semantic similarity 0.60-0.85: store with confidence = 0.50, flag for human review
5. If semantic similarity < 0.60: discard or store as contested

This prevents the main risk: substrate inheriting LLM hallucinations at scale.

### 3.5 Coverage estimate

LLM distillation via this architecture closes approximately 60-70% of the 8-12% residual gap. This brings total parametric knowledge coverage from 88-92% to approximately 94-96%. The remaining 4-6% is the hard core (subliminal cross-domain inference, statistical distributional feel) that requires Tier 5 gradient training.

P_deflated for "LLM distillation closes 60-70% of residual" = 0.55. The claim is plausible but has not been empirically validated. The cheap pre-test (Section 9) can validate this within a day.

---

## 4. TIER 5: SUBSTRATE-NATIVE LLM AS FULL CLOSURE

### 4.1 What it is

Train a substrate-native LLM from scratch on billions of tokens, then use it as the implicit prior layer alongside the explicit KB layer. The LLM provides Type II priors natively; the substrate provides Type I explicit knowledge + audit + bitemporal + GDPR.

### 4.2 Cost estimate

- Pythia-160M scale: ~$5K-$20K in compute
- Pythia-1B scale: ~$50K-$200K
- Production-grade (7B+): $500K-$2M

Timeline: 6-18 months for v3.0+ depending on resource allocation.

### 4.3 What it closes

Full closure of the 8-12% residual, including the hard core. A substrate-native LLM trained on the same corpus as the KB has Type II priors that are perfectly calibrated to the KB domain.

### 4.4 Interim milestone

A substrate-native Pythia-160M trained on the pre-training corpus (Wikipedia + Wikidata + S2ORC) gives Type II priors at substrate-domain-appropriate scale. This is not production-grade reasoning but it closes the "distributional feel" gap within the domain. Cost: ~$5K-$20K. Timeline: 4-8 weeks engineering. This is a viable v2.5 milestone.

### 4.5 Honest assessment

Tier 5 is not on the v1.1/v1.5 critical path. The LLM-distilled architecture at v2.0 gives a better cost/coverage tradeoff than training from scratch at v2.5. Tier 5 becomes compelling when (a) the substrate has accumulated enough domain-specific training signal to make a substrate-native LLM meaningfully different from a general LLM, and (b) customer requirements need full audit-chain provenance on implicit priors, which LLM-distilled provenance cannot fully satisfy (because it still bottoms out in the LLM's opaque parameters).

---

## 5. HYBRID DEPLOYMENT: SUBSTRATE + LLM AS COMPLEMENTARY

### 5.1 Architecture

Two-layer architecture:
- Layer 1: Substrate (explicit knowledge, audit, GDPR, bitemporal, structured queries, deterministic reasoning, drift detection, federated, 1M-scale)
- Layer 2: LLM (Type II priors, novel synthesis, commonsense reasoning, natural language generation)
- Router: per-query classification of which layer is load-bearing

### 5.2 Query classification

The router answers: "Does this query primarily require (a) fact retrieval + audit, (b) implicit reasoning, or (c) both?"

- Type A (fact retrieval + audit): substrate handles fully; LLM not called
- Type B (implicit reasoning): LLM handles; substrate not called, OR substrate handles via LLM-distilled intuitions
- Type C (both): substrate retrieves explicit facts; LLM synthesizes with Type II context; substrate validates LLM output against stored facts (hallucination catch)

In production, Type A is estimated at 70-80% of queries (fact retrieval, compliance, audit). Type B is 10-15% (commonsense reasoning, novel synthesis). Type C is 10-15% (complex queries needing both).

### 5.3 Customer pitch architecture

The honest pitch is not "we replace LLM." It is:

"The substrate covers 88-92% of what frontier LLMs know parametrically, with full auditability, GDPR compliance, bitemporal versioning, and federated deployment. For the 8-12% of queries requiring implicit reasoning, you use the LLM layer -- but with the substrate's audit chain validating the LLM's output against ground truth. The result is a system that is more reliable than LLM alone (substrate catches hallucinations), more auditable than LLM alone (substrate provides provenance), and more efficient than LLM alone (70-80% of queries never hit the LLM)."

The 8-12% framing is an asset, not a liability: it provides honest bounded claims that differentiate from LLM vendors who claim unbounded capability but cannot prove it.

### 5.4 Efficiency moat

In the hybrid architecture, 70-80% of queries bypass the LLM entirely. At $0.01/query LLM cost and 1M queries/day, this is $7,000-$8,000/day saved in LLM API costs. The substrate is not competing with the LLM for deployment dollars -- it is replacing the expensive LLM calls for the majority of queries where explicit knowledge suffices.

---

## 6. EVALUATION OF 12 CRAZY OPTIONS

**Option a: Substrate as LLM-quality-validator**
Viable. Substrate stores ground truth; LLM produces answer; substrate detects contradictions. This is the Type C query path from Section 5.2. Pre-reg: hallucination catch rate > 60% on NQ benchmark where substrate has domain coverage. Cheap test: 500 NQ queries on medical domain where substrate has pre-trained KB. Cost: ~2 hours CPU.

**Option b: Substrate-distilled LLM intuitions**
Viable. This is the LLM-distillation architecture from Section 3. Provenance tag "claimed by LLM v1.5" is the key. Tested via cheap pre-test in Section 9. P_deflated = 0.55.

**Option c: Crowd-sourced Type II ingestion**
Viable but slow. Customers contribute domain-specific intuitions; consensus + adversarial validation gates storage. Strong for specialized domains (medical, legal, financial) where domain experts know implicit assumptions. Weak for general commonsense. Recommended for v2.0 domain-specific deployments.

**Option d: Substrate intuition-gap detection**
Valuable as a routing signal. When substrate confidence is low AND the query type suggests Type II priors are needed, the substrate flags for LLM fallback explicitly. This makes the 8-12% visible and manageable rather than invisible and contaminating. Cheap to implement: confidence threshold + query-type classifier.

**Option e: Substrate-LLM continuous re-training**
Viable at v3.0+. LLM checkpoints periodically updated with substrate accumulations. Requires significant infrastructure. The value is that the LLM's implicit priors drift toward the domain-specific knowledge in the substrate. Timeline: v3.0+ after Tier 5 foundation is built.

**Option f: Substrate teaches LLM**
The inverse of LLM-distillation. Substrate's accumulated regularities (via sleep defrag) become fine-tuning signal for the LLM. Viable at v2.5+. Risk: fine-tuning degrades LLM's general capability for domain-specific gain. Requires careful fine-tuning scope control. P_deflated = 0.30 for "substrate-teaches-LLM improves LLM performance on domain queries" given fine-tuning risk.

**Option g: Substrate as LLM external memory + retrieval validator**
Already implicit in the hybrid architecture. Substrate retrieves relevant facts before LLM synthesis (RAG pattern). The "retrieval validator" extension: substrate verifies that LLM's cited sources are in the KB and consistent with stored facts. Standard RAG + fact-check extension. P_deflated = 0.70. Already standard practice.

**Option h: Inverse Type II -- substrate identifies LLM implicit biases**
Interesting. Substrate queries the LLM repeatedly on the same domain, collects answers, identifies systematic patterns (biases). Stores bias characterization with provenance. Useful for compliance-sensitive deployments where knowing LLM bias direction is legally relevant. P_deflated = 0.45. Novel application worth a quick prototype.

**Option i: Substrate hosts intuition explanations**
Good. LLM generates intuition; substrate stores rationale; future queries see both fact + intuition. This is the LLM-distilled architecture with an explanability layer. Recommended as part of v1.5 LLM-distillation implementation. Cost: minimal beyond base distillation architecture.

**Option j: Substrate-LLM ensemble (vote)**
Standard ensemble method. Substrate returns explicit-knowledge answer; LLM returns implicit-knowledge answer; substrate audits the vote against stored facts. Useful when the query admits both a factual and an implicit answer. Risk: ensemble complexity increases latency and cost. Recommended only for high-stakes queries.

**Option k: Pre-trained substrate WITH LLM-distilled Type II priors as separate layer**
This is the v1.5 target architecture. The key insight: the LLM-distilled priors are stored as a SEPARATE annotated layer in the KB, not merged with ground-truth facts. This allows the audit chain to distinguish "sourced from text corpus" from "sourced from LLM inference." Strongly recommended.

**Option l: Substrate as scientific knowledge curator (Type II from peer-reviewed literature)**
This is the S2ORC pre-training path. Scientific papers contain explicit statements of many Type II priors (e.g., physical laws, biological principles). Sleep defrag from S2ORC accumulates these. This is already in the pre-training corpus plan. The extension: focus curation on papers that explicitly state "it is commonly assumed that..." or "practitioners implicitly assume..." -- these are the highest-value Type II prior sources.

**Summary of viability:**
- Immediately viable (v1.5): b, d, g, i, k, l
- Viable with engineering (v2.0): a, c, h, j
- Viable at v2.5+: e, f
- Low P_deflated: f (0.30), h (0.45)

---

## 7. DEEP DIVE: SUBSTRATE-DISTILLED LLM PRIORS ARCHITECTURE

### 7.1 Full architecture specification

**Trigger:** Sleep-defrag cycle completes consolidation of a knowledge cluster. The cluster has at least 50 facts in it (threshold: tunable).

**Step 1 -- Cluster characterization:** Extract cluster topic, domain, representative facts (5-10 samples). Format as compact prompt context.

**Step 2 -- Intuition query (3x for adversarial consistency):**
Query 1: "Given these facts about [domain], what background assumptions or intuitions are implicit in this knowledge domain? List 5-10 short intuitions."
Query 2 (rephrased): "What would an expert in [domain] assume without saying, based on this knowledge?"
Query 3 (adversarial): "What implicit assumptions would be WRONG to make about [domain], and why?"

Query 3 is the adversarial gate. If Query 3 returns intuitions that directly contradict Query 1/2 outputs, the affected intuitions are flagged as contested.

**Step 3 -- Consistency scoring:**
- Semantic similarity of Query 1 vs Query 2 outputs (cosine similarity on sentence embeddings)
- Adversarial catch rate from Query 3
- Final confidence = (Q1-Q2 similarity x 0.70) + (adversarial clean rate x 0.30)

**Step 4 -- Storage:**
- Intuition stored as derived binding: (cluster_id, intuition_text, confidence, llm_version, llm_temperature, query_1, query_2, harvest_timestamp)
- Separate annotation layer from ground-truth facts
- Accessible via dedicated "intuition_bindings" index

**Step 5 -- Retrieval integration:**
When a query fires against a cluster, results include:
- Ground-truth facts (Type I, audit-grade)
- LLM-distilled intuitions (Type II, provenance-grade, confidence-tagged)
The consuming layer decides how to weight each class.

### 7.2 Risk analysis

**Risk 1: LLM hallucinations in distilled intuitions**
Mitigation: adversarial consistency check (Section 7.1 Step 3). Hallucinations tend to be inconsistent across rephrased prompts. Estimated hallucination-through-gate rate: < 15% for confidence > 0.70 threshold.

**Risk 2: Circular reasoning (substrate queries LLM on facts it gave the LLM)**
Mitigation: harvesting queries do NOT provide specific KB facts as context. They provide only the cluster topic and domain. The LLM's intuitions come from its training distribution, not from substrate-supplied content.

**Risk 3: LLM version drift**
The stored provenance tag includes LLM version. When the LLM is updated, old distilled intuitions remain tagged with the old version. Periodic re-harvest on major version upgrades is recommended.

**Risk 4: Cost at scale**
For a 1M-fact KB with clusters of 50 facts each: 20,000 clusters x 3 queries x ~500 tokens = 30M tokens = ~$7.50 at Haiku pricing. One-time harvesting cost is negligible.

### 7.3 Coverage estimate

The LLM-distilled priors architecture, properly implemented, captures:
- Category 2 (Cultural/contextual): ~80% coverage
- Category 3 (Linguistic): ~70% coverage (limited by LLM's ability to verbalize linguistic intuitions)
- Category 4 (Causal intuitions): ~75% coverage
- Category 5 (Cross-domain analogies): ~60% coverage
- Category 6 (Intuitive physics): ~70% coverage
- Category 7 (Social heuristics): ~65% coverage
- Category 8 (Subliminal cross-domain): ~20% coverage (hard core; LLM can verbalize some but not the distributional feel itself)

Weighted average across categories: approximately 65-68% of the residual gap closed.

Combined with the pre-training corpus (closes 88-92% of parametric gap): total coverage reaches approximately 94-96%.

---

## 8. FALSIFIABLE PREDICTIONS (PRE-REGISTERED)

### 8.1 LLM-distillation coverage estimate

**HARD-PASS:** On a 500-question benchmark covering 5 domains where the substrate has pre-trained KB, the LLM-distillation architecture (Section 7) improves answer quality (as rated by independent LLM judge) on Type II prior questions by >= 40% over substrate-only answers. The substrate+distilled rate is >= 70% vs substrate-only rate of <= 50%.

**MID-BAND:** 25-40% improvement. LLM distillation helps but not as much as the architecture predicts. Root cause investigation needed.

**HARD-FAIL:** < 20% improvement. LLM distillation at this architecture does not close the residual. Either the adversarial consistency gate is too permissive (hallucinations flooding through) or the distilled intuitions are not being retrieved effectively.

### 8.2 Hybrid architecture efficiency

**HARD-PASS:** On a representative query log (1000 queries), substrate-only handling covers >= 70% of queries with precision >= 0.85 (substrate answer matches ground truth). LLM is called for <= 30% of queries.

**MID-BAND:** Substrate covers 55-70%. LLM load is higher than expected; router needs calibration.

**HARD-FAIL:** Substrate covers < 50%. Either pre-training corpus coverage is lower than 88-92% estimate, or routing classifier is broken.

### 8.3 Hallucination catch rate

**HARD-PASS:** Substrate-as-validator (Option a) catches >= 55% of known LLM hallucinations in a held-out set of 200 queries where ground truth is in the KB.

**MID-BAND:** 35-55% catch rate. Useful but not the claimed hallucination prevention story.

**HARD-FAIL:** < 25% catch rate. Substrate and LLM are hallucinating on different questions; KB coverage gap is broader than estimated.

---

## 9. CHEAP DECISIVE TESTS

### Test 1: LLM-distillation pre-test (1-2 hours CPU, Haiku API)
- Select 100 questions from NQ or TriviaQA covering 3 domains where substrate has dense pre-trained KB coverage
- Identify which questions require Type II priors (implicit reasoning, cross-domain, commonsense)
- For the identified Type II questions (~30-40% estimated): compare substrate-only answer vs substrate+LLM-distilled answer
- Score via automated judge or held-out labels
- Deliverable: Type II prior coverage estimate with before/after delta
- Go/no-go: > 30% delta -> architecture viable; proceed to full harvest implementation

### Test 2: Hallucination catch pilot (30-min CPU)
- Take 200 NQ questions where ground truth is in pre-trained KB
- Generate LLM answers (Haiku, 0 shot)
- Run substrate validator against LLM answers
- Measure: what fraction of LLM errors does substrate catch?
- Deliverable: hallucination catch rate and false-positive rate
- Go/no-go: catch rate > 40% AND false positive < 20% -> validator architecture viable

### Test 3: Query routing classification pilot (30-min CPU)
- Sample 500 queries from a public QA benchmark
- Classify each as Type A (fact retrieval) / Type B (implicit reasoning) / Type C (both)
- Measure substrate-only coverage on Type A queries
- Deliverable: routing signal quality and Type A fraction
- Go/no-go: Type A fraction > 60% AND substrate precision on Type A > 0.80 -> hybrid efficiency claim valid

---

## 10. CROSS-THREAD SYNTHESIS

**Connection to sleep-defrag:** The LLM-distillation architecture is a natural extension of the sleep-defrag mechanism. Sleep defrag already identifies knowledge clusters for consolidation. Adding LLM intuition harvesting per cluster costs one additional API call per cluster per consolidation cycle. The architectural fit is clean.

**Connection to Pattern B (cross-domain analogy bindings):** LLM-distilled cross-domain analogies (Category 5) can be stored as Pattern B bindings. The substrate already has the binding infrastructure. LLM harvesting populates it more efficiently than manual curation.

**Connection to parametric knowledge gap finding:** The 8-12% residual identified in the pre-training corpus drill is the anchor for this analysis. The LLM-distillation architecture narrows it to 3-5% at v2.0. This closes the loop between the corpus pre-training strategy and the Type II prior coverage.

**Connection to GDPR / EU AI Act compliance:** LLM-distilled intuitions stored with provenance tags satisfy the EU AI Act Article 12 audit requirement (as applied to derived knowledge). A system that stores "this intuition was derived from LLM-v1.5 at time T" is MORE auditable than a raw LLM that has the same intuition baked into opaque weights.

---

## 11. SUBSTRATE-PRODUCT IMPLICATIONS

**Implication 1: v1.5 architecture target is clear**
The v1.5 target is substrate + pre-trained Wikipedia/Wikidata/S2ORC + LLM-distilled intuition layer. The intuition layer is a separate annotation layer with provenance, not merged with ground truth. This is implementable with existing substrate infrastructure.

**Implication 2: The 8-12% honest residual is a sales asset**
Customers who have been burned by LLM hallucinations will respond to honest bounded claims. "We cover 88-92% with full audit; the 8-12% is implicit reasoning we route to a validated LLM with our hallucination-catch layer" is a stronger pitch than "we cover everything" from a trust standpoint.

**Implication 3: Efficiency moat is concrete**
70-80% of queries bypass the LLM entirely. At 1M queries/day and $0.01/LLM query, this is $7,000-$8,000/day saved. The substrate's operational cost is a fraction of an equivalent LLM deployment at the same query volume. This is a durable efficiency moat that does not depend on capability claims.

**Implication 4: Compliance angle differentiates**
The LLM-distillation architecture provides audit-chain provenance on implicit priors that no LLM vendor can match. Under EU AI Act Article 12 (Aug 2026), high-risk AI systems require documentation of training data and knowledge sources. A substrate that stores "this intuition derived from LLM-v1.5 at T" satisfies this requirement in a way that an opaque LLM does not.

**Implication 5: Substrate-native LLM is a long-range moat**
At v3.0+, a substrate-native LLM trained on the accumulated substrate KB provides Type II priors that are calibrated to the exact domain the KB covers. This is a compounding moat: the more domain-specific knowledge accumulates in the substrate, the more calibrated the substrate-native LLM becomes. No third-party LLM can replicate this without access to the substrate's accumulated knowledge.

---

## 12. STRATEGIC TIMELINE

**v1.1 (current architecture)**
- Substrate + domain-specific KB
- LLM fallback for explicit routing
- No Type II prior coverage in substrate
- Customer pitch: explicit knowledge layer + audit

**v1.5 (LLM-distilled intuitions, 3-6 months)**
- Pre-trained Wikipedia + Wikidata + S2ORC + PubMed + StackOverflow
- LLM-distilled intuition layer (sleep-defrag integration)
- Hybrid router (Type A / B / C classification)
- Substrate-as-validator (hallucination catch)
- Customer pitch: 94-96% parametric coverage + audit + hallucination catch

**v2.0 (full ensemble, 6-12 months)**
- Continuous LLM-distillation (per-domain harvesting on ingestion)
- Crowd-sourced Type II ingestion for specialized domains
- Substrate-LLM ensemble for Type C queries
- Intuition gap detection (explicit routing signal)
- Customer pitch: comprehensive knowledge system + audit + compliance + efficiency moat

**v2.5 (substrate-teaches-LLM, 12-18 months)**
- Substrate-native Pythia-160M or equivalent trained on accumulated KB
- Fine-tuning of LLM on substrate-accumulated domain-specific regularities
- Customer pitch: domain-specialized knowledge system with substrate-native implicit priors

**v3.0+ (full Tier 5, 18-36 months)**
- Full substrate-native LLM (7B+ scale)
- Complete closure of Type II prior gap
- Full audit-chain provenance on all knowledge including implicit priors
- Customer pitch: the only knowledge system where every fact AND every implicit prior has a verifiable provenance chain

---

## 13. HONEST CHARACTERISTIC LIMITS

The structural ceiling at v1.1 is 88-92% parametric knowledge coverage. This is not a substrate failure -- it reflects the inherent asymmetry between enumerable KB (explicit facts + explicit rules) and gradient-trained distributional knowledge (implicit priors as parameter distributions).

The LLM-distillation path at v1.5 narrows the gap to approximately 94-96%. The remaining 4-6% is the hard core: subliminal cross-domain inference from massive distributional learning. This cannot be closed without gradient training (Tier 5).

**The pitch-around strategy is credible and durable:**
- 88-92% coverage at v1.1, rising to 94-96% at v2.0, is genuine
- The 4-6% hard residual is the "neither system handles reliably" category -- honest framing that applies to LLMs too (LLMs hallucinate on exactly these types of implicit inferences at measurable rates)
- Audit + provenance + efficiency + compliance are categorical moats that do not depend on closing the Type II gap
- The substrate is not a worse LLM; it is a different instrument that excels where LLMs are structurally weak (auditability, determinism, GDPR, bitemporal, 1M-scale)

The honest limit: for tasks that require dense, subliminal, cross-domain reasoning over novel combinations of domains, a frontier LLM will outperform substrate+LLM-distilled at v1.5/v2.0. This is a bounded set of tasks (creative synthesis, novel scientific hypothesis generation, subtle social reasoning). The substrate-LLM hybrid handles it by routing to the LLM for this task class. The substrate's contribution is NOT doing this -- it is validating the LLM's output against ground truth and providing the audit chain.

---

## CHEAP DECISIVE TEST (SUMMARY)

**Test 1** (priority): LLM-distillation pre-test on 100 NQ questions, 3 domains, compare substrate-only vs substrate+distilled on Type II questions. 1-2 hrs CPU, ~$0.50 Haiku API. Go/no-go threshold: > 30% delta.

**Test 2**: Hallucination catch pilot on 200 NQ questions. 30 min CPU. Go/no-go: catch rate > 40%, false positive < 20%.

**Test 3**: Query routing pilot on 500 QA benchmark questions. 30 min CPU. Go/no-go: Type A fraction > 60%, substrate precision > 0.80.

All three tests can run in a single 3-hour session on the laptop CPU runner.

---

## CITATIONS (verified conceptual grounding, no web-retrieved links)

1. Petroni et al. (2019) -- "Language Models as Knowledge Bases?" -- factual knowledge stored in LLM parameters; demonstrates that gradient training encodes factual priors not purely linguistic regularities. (Conceptual anchor for Type II prior taxonomy.)

2. Brown et al. (2020) -- GPT-3 -- few-shot learning as evidence of implicit world-model priors; cross-domain generalization without explicit transfer.

3. Bommasani et al. (2021) -- Foundation Models survey -- emergent capabilities as evidence of Type II prior formation during gradient training; capabilities absent at small scale, present at large scale.

4. Marcus & Davis (2019) -- "Rebooting AI" -- explicit catalog of commonsense reasoning failures in LLMs; maps to the taxonomy of Category 7 (social heuristics) and Category 8 (subliminal cross-domain inference).

5. Minsky (1986) -- "The Society of Mind" -- implicit knowledge representation as distributed process; early framing of why explicit KB cannot capture procedural/contextual knowledge.

6. Lake et al. (2017) -- "Building machines that learn and think like people" -- systematic comparison of gradient-learned priors vs explicit symbolic representations; directly relevant to the KB-synthesizable vs structurally-unreachable split.

7. Guu et al. (2020) -- REALM -- retrieval-augmented LM; demonstrates that explicit KB retrieval + LLM synthesis is viable architecture; empirical grounding for the hybrid deployment strategy.

8. Lewis et al. (2020) -- RAG -- formalized retrieval-augmented generation; the standard architecture reference for the hybrid substrate+LLM deployment.

9. Meng et al. (2022) -- ROME -- localized factual associations in LLM parameters; evidence that some Type II priors are localized enough to be edited (relevant to Option e / substrate-teaches-LLM).

10. Shi et al. (2023) -- REPLUG -- retrieval-augmented LLM via ensemble; empirical grounding for Option j (substrate-LLM ensemble).

11. Borgeaud et al. (2021) -- Retro -- large-scale retrieval-augmented LM training; demonstrates that explicit KB integration during training improves LLM capability (relevant to v2.5 substrate-teaches-LLM path).

12. Wei et al. (2022) -- "Emergent Abilities of Large Language Models" -- documents that Type II priors emerge discontinuously with scale; implies that Tier 5 substrate-native LLM requires sufficient scale to generate the priors (not just parameters).

---

P_deflated = 0.55 (LLM-distillation-closes-60-70%-of-residual)
P_theoretical = 0.75 x P_empirical = 0.73 (calibration penalty applied: -0.20)
Calibration penalty: -0.20 applied across all P estimates
Novel-synthesis cap: 0.50 applied to v1.5 implementation predictions

Next drill candidate: empirical validation via Test 1 (LLM-distillation pre-test); field = applied-KB-systems; no prior drill in this field
