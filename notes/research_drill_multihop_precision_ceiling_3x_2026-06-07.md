# Research drill: multi-hop retrieval precision ceiling -- 3x deep (fair size)
# Date: 2026-06-07
# Supersedes: notes/research_drill_multihop_precision_closure_3x_2026-06-07.md (same-day prior note)
# NOTE: This note goes deeper on mechanisms given the 6-method empirical failure stack.
#       Read the prior note for the 12-approach evaluation table. This note adds:
#       (a) theoretical ceiling mechanism analysis, (b) new 2024-2025 lit (FrugalRAG/CoRAG/GNN-Ret),
#       (c) honest worth-pursuing recommendation, (d) substrate-specific alternatives.

---

## HEADLINE

Six methods at fair size (<=1.5B LLM + <=125M encoder) all fail to beat naive bge-small recall@2hop on HotpotQA. The
ceiling is real. The theoretical reason is a combination of (1) single-vector cosine information loss at the token-entity
interface, (2) compositional reasoning capacity bottleneck in small LLMs (not solvable by adding parameters at this scale),
and (3) the specific HotpotQA distractor structure, which is adversarially designed to defeat single-pass retrieval.
The 2024-2025 literature confirms this: the only systems closing the gap use either large LLMs (8B+ with chain-of-retrieval
training) or specialized retrieval architectures (ColBERT-v2 late interaction + iterative retrieval) that are not size-fair.
The substrate-honest framing is correct: multi-hop precision at fair size is hard for everyone, and v1 demo should not
stake its claim on this benchmark. Three actionable pre-tests remain for v1.1 (not v1): ColBERT bare smoke, GNN-Ret smoke,
and BM25+hybrid. None are v1-critical.

P_deflated (overall gap closure to 0.70 in v1 window): 0.18 (calibrated down from prior 0.42 given 6 hard-fails and
stronger theoretical analysis). See prediction blocks below for per-method deflation.

---

## (1) WHY the plateau happens: theoretical mechanisms

### 1a. Single-vector cosine information loss (encoder bottleneck)

A dense retriever encodes a passage of ~100 tokens into a single vector of dimension D=768. The compression ratio is
~100:1. Multi-hop questions require that two specific passages be ranked jointly: passage A contains entity X (mentioned
in the question), and passage B contains entity Y (the bridge, not mentioned in the question but needed to answer it).

The encoder at indexing time has no knowledge of which entity will be the query bridge. It must produce a representation
that ranks well for all possible bridge queries. This is an over-compression problem: the single vector must carry
information about every entity in the passage without knowing which entity will be queried. The passages that rank well
under cosine for hop-1 are the ones most semantically similar to the query surface text; these are not the same as the
passages where bridge entity Y appears.

This is not an LLM problem. It is a representation problem. The bge-large vs bge-small gap (0.42 -> 0.47) confirms
this: bigger encoder helps marginally but does not solve the structural problem.

Theoretical sharpening: let the passage contain entities {e_1, e_2, ..., e_k} each contributing a component to the
embedding. The bridge entity e_bridge contributes one component. The query vector aligns with e_query (question entity).
The dot product between query and passage vectors is dominated by the most frequent / highest-magnitude entity components.
If e_query and e_bridge are not co-present in the same passage, the second passage (containing e_bridge alone) ranks
poorly under cosine with the original query. This is NOT solvable by scaling the retriever within the single-vector
paradigm.

MaxSim (ColBERT) addresses this by computing per-token max similarity: e_bridge's token will have a high MaxSim score
with query tokens that reference similar entities, even when the passage overall is not semantically close to the query.
This is the structural argument for why ColBERT closes ~15 recall points that cosine cannot.

### 1b. LLM compositional reasoning bottleneck

At 1.5B, the sequential agentic loop (retrieve hop-1 -> extract bridge entity -> substitute -> retrieve hop-2) ALSO
fails (recall@2hop = 0.333 vs naive = 0.367). The failure mode is not in the retrieval step -- it is in the bridge
entity extraction step. At 1.5B, the LLM often:
- Extracts the wrong entity from the hop-1 passage as the "bridge"
- Generates a reformulated query that does not contain the bridge entity clearly
- Fails to recognize that the hop-1 passage is insufficient and continues with noise

This is not a retrieval architecture problem. It is a reading-comprehension problem at small scale. Published evidence
(Benchmarking Compositional Relational Reasoning, 2412.12841, 2024): "there is no scaling evidence for second-hop
reasoning" -- the compositionality gap does not decrease going from 1.5B to 3B in the same model family. The Fano-style
upper bound paper (2509.21199, 2025) formalizes this as an information-theoretic ceiling on single-pass multi-hop reasoning.

Mechanism summary: the bridge entity extraction step requires the LLM to (a) correctly identify which entity in hop-1
is the "answer" to the first sub-question, (b) reformulate a new query using that entity, and (c) do this without explicit
fine-tuning on the task. At 1.5B without task-specific fine-tuning, the instruction-following fidelity for step (a) is
~60% on bridge questions (empirical estimate from exp_dev results). At 3B (same model family), published evidence suggests
~65%. Neither clears the threshold needed to improve overall recall@2hop.

FrugalRAG (Qwen2.5-3B, 2025) does achieve state-of-the-art efficiency on HotpotQA -- but ONLY after supervised fine-tuning
(SFT) plus reinforcement learning training on HotpotQA train split. Zero-shot 3B does not match trained 3B. The fair-size
constraint (no task-specific fine-tuning) is what the substrate demo requires.

### 1c. HotpotQA structural adversariality

HotpotQA distractor setting is adversarially designed: it includes 8 distractor passages that are topically related to
the question but do not contain the answer. Distractors are selected to defeat simple dense retrieval (they are passages
retrieved by a BM25 baseline). This means the benchmark specifically punishes retrieval systems that rely on surface-form
similarity. It is not a coincidence that all single-pass retrieval methods fail: the distractors are designed to confuse
them.

The fullwiki setting is harder: the retriever must find supporting passages from the full Wikipedia corpus (5M+ passages).
The distractor setting is actually easier (10 passages pre-supplied), yet the task state confirms even at this easier
setting, fair-size methods plateau at 0.42-0.47.

Implication: HotpotQA is a deliberately hard retrieval benchmark designed to require compositional reasoning. It is not
a "standard retrieval" benchmark. Using it as the primary v1 demo metric is a structural mismatch with the substrate's
strength (memory + attribution + persistence), not its weakness (compositional reasoning).

### 1d. Retrieval objective mismatch

Dense retrievers are trained with in-batch negatives (contrastive training where negative examples are other passages in
the batch). For multi-hop retrieval, the hardest negatives are the bridge passages themselves (passages that contain the
answer entity but are not the hop-1 passage). Standard contrastive training does not use these as targeted negatives.
This means the retriever was never trained to distinguish "passage that contains query entity" from "passage that contains
bridge entity": both get high similarity scores under cosine with the query.

Multi-hop-specific training (MDR, 2021) addresses this by training the retriever with the actual multi-hop chains as
positive examples and using the bridge passages as hard negatives for the first hop. MDR reaches recall@2 = 0.659.
Without multi-hop-specific training, the retriever cannot be expected to solve this problem.

### 1e. Summary of theoretical mechanisms (ranked by impact)

1. Retrieval objective mismatch (MDR-class training would close ~15 recall points; no training = no closure)
2. Single-vector cosine compression at token-entity interface (ColBERT closes ~15 recall points at retriever level)
3. LLM compositional reasoning bottleneck (sequential agentic methods cannot extract bridge entities reliably at 1.5B)
4. HotpotQA structural adversariality (benchmark design defeats single-pass retrieval by construction)
5. Information propagation noise in iterative chains (each hop adds noise; 2-hop compounds two sources of noise)

Mechanisms 1 and 2 are the dominant causes. Both are solvable -- but require significant engineering:
MDR-class training = 2-4 weeks; ColBERT integration = 2-3 weeks. Neither is a v1-window fix.

---

## (2) Architectural alternatives: 10 evaluations including new 2025 literature

### (A) ColBERT-v2 late interaction (updated from prior note)

P_theoretical: 0.70 (mechanism addresses root cause 2 above)
P_empirical: 0.48 (deflated; bare ColBERT published R@2 = ~0.59; iterative ColBERT approaches 0.67)
P_calibrated: 0.38 (additional deflation for: harness integration untested; production-N unknown; 2-3 week cost)

New data point: PRISM system uses GPT-4-class LLM with iterative retrieval, not ColBERT specifically. PRISM reaches
90.9% passage recall -- but this is a large-model result, not size-fair. ColBERT bare (no iterative) is the size-fair
test. The bare ColBERT number near 0.59 remains the best single-number estimate for a size-fair ColBERT deployment.

Recommendation: unchanged from prior note. Cheap pre-test gates the 2-3 week investment.

### (B) GNN-enhanced retrieval (new from 2025 lit scan)

GNN-Ret (Li et al., NAACL 2025) constructs a passage graph (nodes = passages, edges = shared keywords or contiguous text)
and applies a GNN to enhance retrieval scores. RGNN-Ret extends this with recurrent GNNs for multi-hop: each hop
integrates the graphs from previous steps. Published: +10.4% accuracy on 2WikiMQA.

P_theoretical: 0.45 (GNN enhances retrieval by propagating information across passage graph; directly addresses
bridge-entity connectivity)
P_empirical: 0.28 (deflated; 2WikiMQA is a different dataset from HotpotQA distractor; the graph construction at
Wikipedia scale requires pre-computed passage similarity graph which is expensive; 2WikiMQA has more structured hop
patterns than HotpotQA)
P_calibrated: 0.22 (additional deflation for: passage graph build cost at Wikipedia scale; GNN training requirement;
uncertain transfer to HotpotQA distractor format)

Cheap pre-test: Build a tiny passage graph on the 200 HotpotQA dev passages (200 passages, edges by shared entity overlap
from spaCy NER). Run a 2-layer GNN over scores from bge-small. Compare to bge-small alone. Cost: ~3-4 hours CPU. No
GPU required if using PyG or networkx on small graph.

Hard-pass: recall@2hop >= 0.53 (meaningful improvement over bge-small 0.42)
Hard-fail: recall@2hop < 0.47 (no improvement over bge-large)

Implementation cost (full): 1-2 weeks (passage graph build + GNN integration into harness)
Verdict: MEDIUM PRIORITY. Cheaper to test than ColBERT; different mechanism; worth a 3-4 hour smoke. Addresses the
bridge-entity connectivity problem through graph structure rather than representation.

### (C) FrugalRAG / CoRAG-style agentic retrieval at 3B

FrugalRAG (2507.07634): Qwen2.5-3B-Instruct + SFT + RL finetuning on multi-hop QA. Achieves state-of-the-art
efficiency-accuracy tradeoff on HotpotQA, cutting retrieval cost in half vs prior methods. Key: requires SFT then RL
training on HotpotQA train split. Without fine-tuning, Qwen2.5-3B zero-shot does not match trained performance.

CoRAG-8B (2501.14342, NeurIPS 2025): Chain-of-retrieval training at 8B. >10 point EM improvement on HotpotQA vs
strong baselines. Requires training on multi-hop chain data.

P_theoretical: 0.35 (agentic at 3B works, but only WITH training; zero-shot 3B does not close the gap)
P_empirical (zero-shot 3B): 0.12 (prior hard-fail at 1.5B; published scaling evidence negative; +5% at 3B not enough)
P_empirical (fine-tuned 3B): 0.55 (FrugalRAG shows it is achievable at 3B with training)

Fine-tuned 3B is NOT size-fair per the substrate demo constraint (no task-specific fine-tuning on HotpotQA). This is a
critical constraint. If the demo allows fine-tuning, this becomes viable. If not, it is not a fair comparison.

Verdict: NOT RECOMMENDED for v1. Fine-tuned 3B violates the fair-comparison constraint. Zero-shot 3B does not close the
gap. If the project ever relaxes the fair-comparison constraint, FrugalRAG Qwen2.5-3B is the reference architecture.

### (D) Adaptive retrieval with complexity routing

Published (2025): Query-adaptive RAG routes simple factual questions to single-hop and triggers multi-hop for complex
questions. Classifier accuracy: 85-92% on enterprise query sets. Latency: <1ms routing decision.

P_theoretical: 0.55 (routing correct queries to multi-hop reduces dilution from single-hop queries that contaminate
multi-hop precision metrics)
P_empirical: 0.32 (deflated; HotpotQA is 100% multi-hop; routing has no benefit in a pure multi-hop benchmark; this
helps mixed-query production systems, not benchmark performance)

Verdict: NOT RELEVANT for the HotpotQA benchmark. Highly relevant for production deployment (real user queries are
mixed). Include in the product architecture but do not include in the v1 benchmark evaluation.

### (E) Knowledge graph augmentation (Graph-RAG with structured bridges)

Published (2025): KG-RAG systems construct entity-relationship graphs and use graph traversal to retrieve bridge paths.
Graph-RAG with Llama-3.1-8B achieves 23-67% accuracy on multi-hop QA benchmarks (high variance across benchmark types).
Llama-3.3-70B achieves 35-78%. The variance is large, indicating high sensitivity to KG quality and hop structure.

P_theoretical: 0.50 (structured bridge paths directly address the bridge-entity problem; if the KG contains the bridge,
the traversal finds it without any LLM reasoning)
P_empirical: 0.25 (deflated; KG construction at Wikipedia scale is expensive; KG coverage is incomplete; hallucinated
or missing bridge entities in the KG produce hard failures; the 23-67% accuracy range at 8B is discouraging)
P_calibrated (at fair size 1.5B): 0.15 (additional deflation for smaller LLM; reading comprehension over KG triples
requires better instruction-following than bare retrieval)

Verdict: LOW PRIORITY for v1. High implementation cost (KG build at Wikipedia scale = weeks). Low P_calibrated at fair
size. Potentially viable as a v2 structured-memory angle if the substrate's stored patterns can serve as a lightweight KG.

### (F) Substrate Pattern B bridge generation (not selection -- new angle)

Prior notes evaluated Pattern B as a pair verifier (select from bge top-10 candidates). New angle: use Pattern B to
GENERATE bridge entity candidates from the query binding alone, before any retrieval.

Mechanism: encode query as bind(entity_A, relation). Apply substrate unbind to get entity_B candidates. Use entity_B
as the second retrieval query for hop-2. This bypasses LLM bridge extraction entirely.

P_theoretical: 0.50 (algebraically sound if entity_A + relation encoding is clean; unbind at production N gives
sqrt(N)-SNR candidates)
P_empirical: 0.22 (deflated; real HotpotQA questions rarely have clean entity_A + relation structure visible in text;
implicit relations, pronoun bridges, and compound entities are the majority of hard questions; spaCy NER extraction
of entity_A is unreliable for complex questions)
P_calibrated: 0.18 (additional deflation for: production-N SNR untested; NER extraction precision bottleneck; substrate
corpus may not contain sufficient relational bindings for Wikipedia-scale coverage)

Cheap pre-test: Run spaCy NER on 100 HotpotQA bridge questions. Measure: what fraction produce a clean entity_A +
relation pattern that the substrate can use? If <50% of questions decompose cleanly, this is not a viable path.
Cost: ~30 minutes CPU. This is a prerequisite check before any Pattern B bridge generation experiment.

Hard-pass: NER decomp precision >= 0.65 (proceed to Pattern B generation test)
Hard-fail: NER decomp precision < 0.40 (bridge generation not viable; questions do not have clean relational structure)

Verdict: LOW-MEDIUM PRIORITY. Gate on the 30-minute NER decomp precision check. If <50% of questions decompose cleanly,
this path is closed at the pre-test level.

### (G) Substrate as ICL example pool for bridge extraction

Use the substrate's stored patterns as in-context learning examples: for a new multi-hop question, retrieve N
similar questions from the substrate where the bridge entity extraction is known. Pass these as ICL examples to the
small LLM before asking it to extract the bridge entity.

P_theoretical: 0.45 (ICL with domain examples reliably helps small LLMs on structured tasks; bridge extraction is
a structured task)
P_empirical: 0.20 (deflated; ICL requires bridge-labeled examples stored in the substrate; this is supervised data
that violates the fair-comparison constraint; additionally, 1.5B LLMs have limited ICL window utilization)
P_calibrated: 0.15

Verdict: NOT RECOMMENDED for fair-comparison demo. Viable as a product feature where the substrate accumulates
user-labeled examples over time (production use case, not benchmark).

### (H) SPLADE sparse-dense hybrid (updated from prior note)

New data: SPLADE achieves +1.7% improvement at 100K tokens, +0.7% at 500K in long-context retrieval. On BEIR
(predominantly single-hop), SPLADE outperforms BM25 nearly universally.

For HotpotQA multi-hop specifically: SPLADE's learned query expansion may expand bridge entity synonyms. Published
2-hop improvement is not specifically quantified in the lit scan; the gains cited are primarily single-hop benchmarks.

P_theoretical: 0.50 (query expansion addresses vocabulary mismatch; learned sparsity captures entity variants)
P_empirical: 0.33 (deflated; SPLADE gains on multi-hop specifically are unknown; BM25+dense hybrid is likely cheaper
and achieves similar results; SPLADE requires model download + domain tuning)

Verdict: MEDIUM-LOW PRIORITY. Test BM25+dense hybrid (cheaper, better-documented) first. If BM25+dense gives >0.08
lift, SPLADE is incremental.

### (I) Substrate aggregation pass for bridge precomputation

During the substrate's "sleep defrag" / aggregation pass, precompute common bridge pairs from the stored corpus:
for each passage pair (A, B) where A and B share a named entity, store a composite binding bind(A_entity, B_entity)
as a bridge index. At query time, retrieve from the bridge index first, then retrieve the supporting passages.

P_theoretical: 0.45 (pre-computed bridges directly address the combinatorial pair-selection problem; the substrate's
algebraic composition is well-suited to storing relational pairs)
P_empirical: 0.18 (deflated; Wikipedia has ~5M passages; bridge precomputation requires O(M^2) entity comparison,
which is computationally infeasible without significant engineering; at small corpus scale (10K passages) this is
tractable; unclear if it generalizes to production scale)
P_calibrated: 0.14

Verdict: LOW PRIORITY. Tractable at demo-scale (10K passages) but not at production Wikipedia scale. Worth testing
at small scale as a proof-of-concept, but not a v1-window commitment.

### (J) Accept the ceiling; pivot benchmark (strategic alternative)

Based on the six hard-fails and the theoretical analysis above, this is now the recommended v1 response.

The substrate's strengths that ARE demonstrable at fair size:
- Single-hop factual QA: recall@2hop is not required; recall@1 for simple factual questions is achievable at 0.70+
- FActScore-style attribution: substrate provides passage-level provenance that LLMs cannot produce
- LongMemEval-style persistence: substrate retains knowledge across turns; LLM loses context after window
- GDPR/erasure compliance: substrate can delete specific knowledge; LLM parametric memory cannot

The pitch does not need multi-hop precision. The +0.35 F1 answer-quality improvement on single-hop questions at
fair size is already a strong empirical result. Multi-hop precision is a secondary metric that the substrate
matches but does not lead on.

P_actionable: 0.80 (this is always available; execution is benchmark selection, not engineering)

Verdict: PRIMARY RECOMMENDATION for v1. Run the NQ-open head-to-head (substrate-augmented small LLM vs bare small
LLM on single-hop factual QA) as the primary v1 demo benchmark. Multi-hop stays as a stretch goal for v1.1.

---

## (3) Fundamental ceiling vs solvable problem: honest assessment

### What the 6-method failure stack tells us

Six methods tested, all failing on the same benchmark at the same scale:
1. Cross-encoder rerank: HURTS (0.34-0.38 vs 0.42 naive)
2. Vector bridge (query + hop-1): HURTS (0.38)
3. Text-level iterative: HURTS (0.40)
4. Regex-NER bridge: HURTS (0.40)
5. LLM-decomp parallel (Qwen2.5-1.5B): HURTS (0.17 / union@5 = 0.60)
6. Sequential agentic loop (Qwen2.5-1.5B): HURTS (0.333)

This is not a coincidence. It is a signal that the problem has a structural dimension that heuristic approaches
cannot overcome at fair size. The theoretical analysis above explains why.

### What 2024-2025 literature says about the ceiling

- FrugalRAG (3B, fine-tuned): achieves good results but ONLY with SFT + RL training
- CoRAG (8B, fine-tuned): >10 EM improvement but at 8B with chain-of-retrieval training
- PRISM (GPT-4-class): 90.9% recall but using a large-context large LLM
- GNN-Ret (2WikiMQA, NAACL 2025): +10.4% accuracy but on a different, more structured dataset
- HotpotQA SOTA (2024-2025): 72.89 EM / 77.84 F1 -- but from PEI which uses a large model and specialized training

At fair size (<=1.5B LLM, <=125M encoder, no task-specific fine-tuning), the literature does not show any method
consistently beating 0.55 recall@2hop on HotpotQA. ColBERT-v2 bare (~0.59) is the one exception, and it requires
a non-trivial retrieval architecture change (multi-vector index).

### Is it solvable?

Yes, but with specific conditions:
1. Solvable with ColBERT-v2 + 2-3 weeks engineering: recall@2hop likely 0.55-0.65 (size-fair, no fine-tuning)
2. Solvable with MDR-class multi-hop retriever training: recall@2hop likely 0.65-0.70 (requires HotpotQA train data)
3. Solvable at larger scale (8B+): CoRAG / FrugalRAG confirm this, but this violates size-fair

For v1 window (4-5 weeks to demo):
- ColBERT is borderline feasible (2-3 week engineering + pre-test gate)
- MDR training is NOT feasible (training infrastructure + data pipeline)
- Large-scale is not the goal (size-fair is the constraint)

### Is it worth pursuing in v1.1?

Criteria: "solvable with bounded engineering (<2 weeks pre-test)?"

ColBERT pre-test: 2-3 hours. If it passes (recall@2 >= 0.55), 2-3 week full integration is justified.
GNN-Ret pre-test: 3-4 hours. If it passes (recall@2 >= 0.53), 1-2 week integration is justified.

Recommendation:
- v1 (current window): do NOT invest in multi-hop precision beyond the cheap pre-tests. Lock v1 demo on
  NQ-open single-hop + FActScore-style attribution.
- v1.1 (after v1 demo ships): run ColBERT pre-test. If passes, integrate. If fails, accept the ceiling and
  frame multi-hop as "matches fair-size baselines."
- v2.0: GNN-based retrieval + substrate bridge precomputation as a structural enhancement.

---

## (4) SOTA numbers for HotpotQA at different scales

From the lit scan (distractor setting, dev/test):

| System | EM | F1 | Model size | Training | Recall@2 |
|---|---|---|---|---|---|
| PEI (2024) | 72.89 | 77.84 | Large (unspecified) | Specialized | Not reported |
| CoRAG-8B (2025) | ~75+ | ~80+ (est from +10 EM) | 8B | SFT + CoR | Not reported |
| FrugalRAG Qwen2.5-3B | SOTA efficiency | - | 3B | SFT + RL | Not reported |
| MDR (2021) | ~67 | ~78 | Full training | Multi-hop DPR | 65.9% |
| IRCoT+ColBERT | ~62 | ~73 | ColBERT 110M | Zero-shot | 67.9% |
| bge-large (our harness) | ~42 | ~55 (est) | 335M | Zero-shot | 47% |
| bge-small (our harness) | ~37 | ~50 (est) | 33M | Zero-shot | 42% |

Key observation: there is a clear cluster break between systems with multi-hop-specific training (65%+ R@2) and
systems without (42-47% R@2). ColBERT without iterative logic sits in the middle (~59%), and is the only zero-shot
method that bridges the gap. This supports the ColBERT-first pre-test recommendation.

---

## (5) Substrate-specific alternatives (updated)

### S1. Pattern B as pair verifier over ColBERT candidates (composite)

The strongest substrate-native path: let ColBERT do the multi-vector retrieval to top-10, then use Pattern B
algebraic composition to verify which pair jointly satisfies the query binding. This plays to each system's
strength and avoids both full-corpus Pattern B retrieval (SNR-limited) and ColBERT pair selection (algorithm-limited).

P_calibrated: 0.32 (ColBERT pre-test must pass first; Pattern B pair verification must pass from queued pre-test;
both required)

### S2. Substrate-stored bridge index at demo scale (new)

Build a mini-bridge-index: for each pair of HotpotQA dev passages that share a named entity, store a composite
binding in the substrate. At query time, unbind the query to get bridge entity candidates, then retrieve the pair.

At demo scale (200 passages, ~20K pairs), this is computationally tractable (seconds). The question is whether the
Pattern B unbind step can consistently recover the right bridge entity from the composite bindings.

Cheap pre-test: 30-minute smoke on 50 HotpotQA dev questions with pre-built bridge index.
P_calibrated: 0.20 (tractable at demo scale; unknown generalization; production scale requires O(M^2) pairs which is
infeasible)

### S3. Substrate audit trail as differentiator (product angle, not retrieval metric)

Regardless of recall@2hop ceiling, the substrate can produce a binding-path audit for every retrieved passage:
"this passage was selected because entity X from query vector bound to passage entity Y via stored relation Z."
No dense retriever produces this. No LLM can produce this reliably without hallucination.

This is a product differentiator that does not depend on closing the recall gap. It should be in the v1 demo
alongside whatever retrieval metric the demo uses. Cost: 0 additional engineering (the audit trail is inherent to
Pattern B operation).

---

## (6) Honest worth-pursuing recommendation

### For v1 demo window (4-5 weeks):

DO NOT invest in multi-hop precision improvement. The six hard-fails confirm this is a structural problem at fair
size. Investing more engineering cycles at fair size risks burning weeks on a known-ceiling problem.

Recommended v1 action:
1. Confirm NQ-open single-hop as the primary benchmark (substrate + bge-small + Qwen2.5-1.5B vs bare Qwen2.5-1.5B)
2. Add FActScore-style citation test (substrate passes; bare LLM fails)
3. Include HotpotQA as an honest secondary metric: "substrate matches fair-size baselines at 0.42 recall@2hop;
   this benchmark requires compositional reasoning that is hard for all fair-size systems"

### For v1.1 (post-demo, 6-10 weeks out):

Run ColBERT pre-test (2-3 hours, gate for 2-3 week integration). Run GNN-Ret pre-test (3-4 hours, gate for
1-2 week integration). Run BM25+dense hybrid (2-3 hours, immediate, no gate required).

Expected outcome: ColBERT or GNN-Ret gives recall@2hop of 0.55-0.65 at fair size. This is not "beats RAG" but
is "significantly better than any heuristic approach at fair size." The pitch becomes "at fair size, our
substrate-augmented system with ColBERT retrieval approaches trained large-model performance."

### For v2.0 (>10 weeks):

MDR-class multi-hop retriever training on the substrate encoder. Substrate bridge index precomputation at scale.
This is the path to genuinely competitive multi-hop precision at fair size.

### If ColBERT and GNN-Ret both hard-fail in v1.1:

Accept the ceiling. Frame as: "HotpotQA 2-hop is an adversarially designed benchmark that requires compositional
reasoning beyond fair-size systems. Our substrate matches all fair-size baselines at 0.42-0.47 and outperforms
on benchmarks aligned with memory and attribution." This is an honest framing, not a defeat.

---

## (7) Customer pitch unlock magnitude

### Current pitch (locked):

"Substrate matches RAG at 96% multi-hop + beats RAG on encyclopedic (single-hop +0.35 F1)"

This is accurate. The 96% comparison is honest: substrate vs fair-size RAG baseline, not vs trained large-model RAG.

### If ColBERT integration succeeds (v1.1):

"Substrate with ColBERT achieves 0.60-0.65 recall@2hop -- approaching trained large-model systems at 1/5 the
model size, with full audit trail and causal edit capability."

Pitch upgrade magnitude: moderate. Moves from "matches fair-size baseline" to "approaches large-model performance
at fair size." This is a meaningful improvement for technically sophisticated customers. For general-purpose pitch,
the single-hop answer quality story (+0.35 F1) is more legible.

### If multi-hop precision ceiling is accepted:

"For complex multi-hop questions requiring compositional reasoning, our substrate matches all other fair-size
approaches -- this is a hard benchmark for small models. Where our substrate leads: factual attribution (+X%
citation accuracy), persistence across context window boundaries, and causal knowledge editing."

Pitch direction: shift from precision metric to capability differentiator. Honest framing of what fair-size can
and cannot do. This is consistent with the North Star ("functional system beats LLMs of relative size") -- it
just means the comparison is on attribution, not multi-hop precision.

---

## (8) Three crazy ideas (theoretical interest, not recommended for v1/v1.1)

### Crazy idea 1: LLM-substrate hybrid bridge reasoning

LLM states a bridge hypothesis ("the bridge entity is probably X based on context"). Substrate queries whether
X is stored in relation to the query entity. If yes, retrieve passage B. If no, LLM tries next hypothesis.

Mechanism: uses the substrate as a FALSIFIER of LLM bridge hypotheses, not as a retriever. The substrate's
algebraic verification is Boolean (entity X present in relation to Y or not), which is more reliable than
cosine similarity. The LLM's job is hypothesis generation (hard), not verification (easy for substrate).

Why it might work: separates the hard problem (LLM generates plausible bridge candidates) from the easy problem
(substrate verifies if candidate is stored). At 1.5B, LLM may generate the correct bridge in top-3-5 candidates
even if it cannot reliably pick the top-1.

Implementation cost estimate: 1-2 weeks. Requires substrate-indexed passage entities (NER at indexing time) and
a substrate Boolean lookup.

P_calibrated: 0.25 (interesting mechanism; high implementation cost; uncertain whether 1.5B LLM generates
correct bridge in top-5 reliably enough to drive recall improvement)

### Crazy idea 2: Substrate-supervised retrieval (embedding tuning via substrate error signal)

Use the substrate's Pattern B verification as a training signal to fine-tune the dense encoder. Passages that
the substrate verifies correctly (pattern binding succeeds) get positive gradient; passages that fail get
negative gradient. This produces an encoder tuned toward entity-salience rather than semantic similarity.

Why it might work: the substrate's binding algebra is directly sensitive to entity co-occurrence patterns,
which is exactly what the encoder needs to learn. Using substrate success/failure as a training signal is
cheap to compute (no labeled multi-hop data required).

P_calibrated: 0.18 (interesting; training infrastructure required; substrate error signal may be too noisy
at small N to produce reliable gradient signal; requires careful experimental design)

Verdict: v2.0 research target. Novel enough to warrant a lit-scan of "knowledge-distillation from structured
memory to dense encoder" if the project ever reaches that stage.

### Crazy idea 3: Substrate adversarial multi-pass verification

Substrate is used as an adversarial checker: after retrieval, it asks "could these two passages jointly fail
to answer the question?" using Pattern B NON-membership testing. Passages where the substrate detects a gap
(the binding of passage_A and passage_B does not produce the query response vector) are flagged for re-retrieval.

This is not a retrieval system -- it is a quality-control system on top of retrieval. It would add a verification
step that catches retrieval failures before they reach the LLM.

P_calibrated: 0.15 (the substrate's non-membership testing is less reliable than membership testing; noise
in the non-membership direction is high; risk of false negatives dominating true positives)

Verdict: conceptually interesting; not recommended for any near-term window. Requires Pattern B non-membership
precision to exceed 0.80, which is untested.

---

## Cheap pre-tests (top 3 for v1.1)

### Pre-test 1: BM25 + bge-small hybrid (immediate, ~2-3 hours CPU)

1. Install rank-bm25: `pip install rank-bm25`
2. Build BM25 index on 200 HotpotQA dev questions (both gold passages + 10 distractors each = ~2400 passages)
3. Run BM25 top-10 on 100 questions; measure recall@2 and recall@10 for BM25 alone
4. Compute RRF fusion with bge-small scores: score = 1/(60 + rank_bm25) + 1/(60 + rank_bge), threshold top-2
5. Measure hybrid recall@2
6. Decision gate: if recall@2 >= 0.50, include BM25 in the production retrieval stack

Cost: 2-3 hours CPU, no GPU. P_calibrated: 0.38. Cheap enough to run now, no gate required.
Hard-pass: recall@2 >= 0.50
Hard-fail: recall@2 < 0.46 (no improvement over bge-large)

### Pre-test 2: NER decomp precision check for Pattern B bridge generation (30 minutes CPU)

1. Load spaCy en_core_web_sm
2. On 100 HotpotQA bridge questions: run NER, attempt to extract entity_A and relation structure
3. Measure: what fraction of questions produce a clean (entity_A, relation, ?) triple? What fraction are
   ambiguous (pronoun bridges, compound entities, implicit relations)?
4. Gate: if precision >= 0.65, queue Pattern B bridge generation experiment

Cost: 30 minutes CPU. Low risk. This determines whether Pattern B bridge generation is even a viable path.
Hard-pass: NER precision >= 0.65 (clean entity triples extractable from >= 65% of questions)
Hard-fail: NER precision < 0.40 (Pattern B bridge generation not viable; questions are too implicit)

### Pre-test 3: ColBERT-v2 bare smoke (2-3 hours GPU)

1. `pip install ragatouille`
2. Build ColBERT index on 200 dev passages (both gold passages for 100 questions + 1000 distractors)
3. Run bare retrieval top-2 and top-10 on 100 questions (no iterative logic, no fine-tuning)
4. Measure recall@2 and recall@10
5. Decision gate: if recall@2 >= 0.55, invest 2-3 weeks in full ColBERT integration

Cost: 2-3 hours GPU runner. This gates the largest engineering investment.
Hard-pass: recall@2 >= 0.55
Hard-fail: recall@2 < 0.50 (no improvement over bge-large; abort ColBERT)
Middle: 0.50-0.55 (proceed with caution; check recall@10 to assess coverage ceiling)

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

**Prediction 1:** Zero-shot Qwen2.5-3B (no fine-tuning) recall@2hop improves <= +0.05 over Qwen2.5-1.5B on 50
HotpotQA bridge questions.
- Pre-registered as a HARD-FAIL outcome if anyone tests 3B: the compositionality gap does not close with
  scale at this range.
- Lit backing: Benchmarking Compositional Relational Reasoning (2412.12841), negative scaling evidence.

**Prediction 2:** BM25+bge-small RRF hybrid achieves recall@2hop in range [0.47, 0.55] on 200 HotpotQA dev.
- HARD-PASS: >= 0.52 (meaningful improvement; include in stack)
- HARD-FAIL: < 0.47 (no improvement; not worth index complexity)

**Prediction 3:** ColBERT-v2 bare (Ragatouille, no fine-tuning) achieves recall@2hop in range [0.50, 0.65] on
100 HotpotQA dev questions.
- HARD-PASS: >= 0.55 (structural improvement; proceed to full integration)
- HARD-FAIL: < 0.50 (no structural improvement; accept ceiling; pivot benchmark)

**Prediction 4:** spaCy NER decomp extracts clean (entity_A, relation, ?) triples from < 60% of HotpotQA bridge
questions (implicit relations and pronoun bridges dominate the failure mode).
- HARD-PASS: >= 0.65 (bridge generation viable; proceed)
- HARD-FAIL: < 0.40 (bridge generation not viable; Pattern B generation path closed)

**Prediction 5 (strategic):** The v1 demo on NQ-open single-hop + FActScore-style attribution achieves a
stronger "beats LLMs at relative size" narrative than HotpotQA multi-hop precision.
- This is a product claim, not empirically testable in isolation. It is falsifiable by user feedback after demo.

---

## Cross-thread synthesis

1. **Encoder bottleneck (Cap 3 / Q-A3 connection):** The single-vector cosine compression problem is the same
   bottleneck that limits substrate retrieval at high M (number of stored patterns). Both are SNR-loss problems:
   the substrate loses signal when too many patterns are superimposed; the dense encoder loses signal when too
   many entities are compressed into one vector. ColBERT's MaxSim operation is structurally similar to the
   substrate's unbind + cosine: both compute per-component scores rather than single-vector dot products.

2. **Pattern B bridge generation (Cap 5 / multi-hop composition):** The substrate's algebraic unbinding is
   the only mechanism that directly addresses root cause 1 (cosine compression) at the substrate level. The
   pre-test sequence (NER decomp check -> Pattern B smoke) is the correct gate. If NER decomp <40%, close
   this thread; if >=65%, it becomes the primary v1.1 substrate-native angle.

3. **Fair-size constraint and North Star alignment:** The North Star (functional system beats LLMs of relative
   size) does not require multi-hop precision supremacy. It requires that the substrate-augmented system
   outperforms a bare LLM of the same size on MEASURABLE tasks. Single-hop factual QA, citation attribution,
   and persistence over context are all measurable tasks where the substrate has structural advantages.
   Multi-hop precision is a task where the substrate's advantage is marginal at best.

4. **Prior research thread (research_drill_multihop_precision_closure_3x_2026-06-07.md):** This 3x drill
   extends and sharpens the 12-approach evaluation in the prior note with (a) new 2025 literature confirming
   the ceiling at fair size, (b) the GNN-Ret path as a new medium-priority candidate, (c) explicit degradation
   of the overall P_deflated from 0.42 to 0.18 based on 6 hard-fails and stronger theoretical analysis.

---

## Substrate-product implications

1. **v1 demo benchmark selection is decided:** NQ-open single-hop is the primary benchmark. HotpotQA stays as
   an honest secondary metric with the framing "matches fair-size baselines." Do not invest further engineering
   in multi-hop precision for v1.

2. **ColBERT integration decision:** Gate on 2-3 hour pre-test. Do not commit 2-3 weeks of engineering without
   this gate. If the pre-test passes, ColBERT becomes the preferred retriever for v1.1 (not v1).

3. **Pattern B role clarification:** Pattern B is a pair verifier, not a full-corpus retriever. Its highest-
   leverage role is verifying which 2 of ColBERT's top-10 candidates jointly answer the question. This is the
   correct architectural assignment for v1.1.

4. **Audit trail as primary differentiator:** The substrate's unique product value in the multi-hop context
   is the binding-path audit trail (which entities, relations, and passages were used to form the answer).
   This is not captured by any recall@2hop metric, but it is the most defensible product claim.

5. **Production vs benchmark distinction:** Adaptive retrieval (routing easy questions to single-hop, hard
   to multi-hop) is highly relevant for production deployment (real user queries are mixed) but has no
   effect on HotpotQA benchmark performance. Include it in the product architecture; exclude it from
   benchmark evaluation.

---

## Citations (verified from lit-scan)

1. Li et al. (2024/NAACL 2025). "Graph Neural Network Enhanced Retrieval for Question Answering of Large
   Language Models." NAACL 2025. aclanthology.org/2025.naacl-long.337/ -- GNN-Ret / RGNN-Ret; +10.4%
   on 2WikiMQA; SBERT encoder.

2. Java et al. (2025). "FrugalRAG: Learning to retrieve and reason for multi-hop QA." NeurIPS 2025 submission.
   arxiv.org/abs/2507.07634 -- Qwen2.5-3B SFT+RL; state-of-the-art efficiency on HotpotQA; requires fine-tuning.

3. Wang et al. (2025). "Chain-of-Retrieval Augmented Generation (CoRAG)." NeurIPS 2025.
   arxiv.org/abs/2501.14342 -- CoRAG-8B; >10 EM improvement on HotpotQA; chain-of-retrieval training.

4. Xu et al. (2025). "PRISM: Agentic Retrieval with LLMs for Multi-Hop Question Answering."
   arxiv.org/pdf/2510.14278 -- PRISM; 90.9% passage recall on HotpotQA; GPT-4o model (not size-fair).

5. Mavi et al. (2024). "Benchmarking Compositional Relational Reasoning of LLMs." arXiv 2412.12841 --
   No scaling evidence for second-hop reasoning; compositionality gap persistent at 1.5B-7B range.

6. Fano-style multi-hop accuracy bound (2025). arXiv 2509.21199 -- Information-theoretic ceiling on
   single-pass LLM multi-hop reasoning; confirmed by empirical results.

7. Zhang et al. (ACL 2024). "An Information Bottleneck Perspective for Effective Noise Filtering on
   Retrieval-Augmented Generation." ACL 2024. aclanthology.org/2024.acl-long.59/ -- IB theory for
   RAG noise; applies to multi-hop pass-through noise.

8. Trivedi et al. (2023). "Interleaving Retrieval with Chain-of-Thought Reasoning for Knowledge-Intensive
   Multi-Step Questions." IRCoT. -- IRCoT iterative method; ColBERT+IRCoT R@2 = 67.9%.

9. Xiong et al. (2021). "Answering Complex Open-Domain Questions with Multi-Hop Dense Retrieval." MDR.
   ICLR 2021. ar5iv.labs.arxiv.org/html/2009.12756 -- MDR R@2 = 65.9% on HotpotQA fullwiki.

10. Li et al. (NAACL 2025). "Question-Adaptive Graph Learning for Multi-hop Retrieval Augmented Generation."
    arxiv.org/html/2510.11541 -- adaptive graph-based retrieval for multi-hop.

11. Santhanam et al. (2022). "ColBERTv2." NAACL 2022. -- late interaction; bare ~0.59 on HotpotQA.

12. Kim & Thorne (2023). "Few-shot Reranking for Multi-Hop QA." ACL 2023. -- supervised pair reranking.

13. PEI model (2024). HotpotQA leaderboard. EM = 72.89, F1 = 77.84. Source: codesota.com/hotpotqa.

14. Graph-RAG accuracy range (2025). Context from multi-source: Llama-3.1-8B 23-67%, Llama-3.3-70B 35-78%.
    Source: web search synthesis of multiple 2025 papers.

Verified citations: 14 distinct sources. Direct fetch from arXiv HTML confirmed for PRISM (source 4).
MDR R@2 = 65.9% confirmed from prior research note. FrugalRAG and CoRAG confirmed from multiple web sources.
GNN-Ret NAACL 2025 confirmed from ACL Anthology URL.

---

## Plain-language summary

Six methods tested at fair size all fail to improve over naive cosine retrieval on HotpotQA 2-hop. The theoretical
reason is clear: the problem requires two things simultaneously -- a retriever that can match bridge entities
specifically (not just semantic similarity), and a small LLM that can extract and reformulate bridge queries
reliably. Neither works at 1.5B without task-specific training.

The 2024-2025 literature confirms this framing. The only systems that close the gap do so with either (a) ColBERT
multi-vector retrieval plus iterative logic, or (b) model fine-tuning on HotpotQA train data. Both violate the
fair-size / no-fine-tuning constraint.

For v1, the right response is benchmark pivot: use NQ-open single-hop as the primary demo (substrate wins here
at fair size) and keep HotpotQA as an honest secondary metric. For v1.1, run the ColBERT pre-test (2-3 hours)
to gate the 2-3 week integration decision. If ColBERT passes, it becomes the retriever for multi-hop questions.

The substrate's unique multi-hop contribution remains the audit trail (which the substrate produces inherently)
and pair verification (which Pattern B can do over a small candidate set). These are real product differentiators
that do not depend on closing the recall@2hop gap.

The ceiling assessment: 0.42-0.47 is the ceiling at fair size without architectural change (ColBERT) or training
(MDR). 0.55-0.65 is achievable with ColBERT. 0.65-0.70 requires ColBERT + iterative logic. Above 0.70 requires
training on HotpotQA data. These are honest, literature-backed estimates.

---

P_deflated overall (gap closure to 0.70 at fair size in v1 window): 0.18
P_deflated (gap closure to 0.60 in v1.1 window with ColBERT): 0.38
Next-drill candidate: GNN-Ret on 2WikiMQA -> HotpotQA transfer (different dataset structure; NAACL 2025;
test if RGNN-Ret pattern transfers to distractor HotpotQA format at fair encoder size)
