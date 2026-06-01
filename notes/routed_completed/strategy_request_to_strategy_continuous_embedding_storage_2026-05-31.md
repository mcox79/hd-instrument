# Strategy request: continuous-embedding storage experiment (2x-deep-synthesized; ONE new experiment from 5 proposed)

## Trigger: research 2x deep drill 2026-05-31 (2 parallel Sonnet drills synthesized)

Origin: user 2026-05-31 -- shared 5 experiments (R-1 through R-5) framing substrate as "continuous, relational, compositional knowledge store with audit, edit isolation, deletion certificates, and real-time learning." Per [[feedback-2x-means-depth]] = operational deepening on prerequisites. Full audit at `notes/research_continuous_embedding_storage_audit_v1_2026-05-31.md`.

## Finding (one paragraph)

The 5 experiments collapse to ONE genuinely-new experiment + duplicates of in-flight work. The doc's framing ("Stores any continuous representation") oversold: substrate is BIPOLAR ({-1,+1}^N MAP-B algebra), NOT a continuous-representation store. Ingesting continuous embeddings requires a PROJECTION SCHEME (continuous R^d → bipolar {-1,+1}^N), and the projection layer is where the algebraic moat properties may DEGRADE. Drill A established SimHash (random Gaussian + sign) at N=16384 is the recommended projection — native bipolar, no training, moat-compatible structurally, recall@10 75-82% unaided vs FAISS 92-95% (closes to 85-90% with over-sampling). Drill B established the moat survives unevenly: real-time learning SURVIVES INTACT (P_def 0.92), algebraic audit DEGRADES (with mitigation P_def 0.70), edit isolation DEGRADES for semantic neighbors (P_def 0.40 unmitigated, 0.55-0.70 with mitigation), deletion certificates DEGRADE/BREAK for strict GDPR compliance without side-data (P_def 0.35 unmitigated, 0.50-0.60 with hash side-data). Joint P_def for full-moat-survives-with-mitigations: **0.35-0.45**. The honest product reframing replaces "substrate stores any continuous representation" with: "**substrate is an audit-grade vector store with 10-20x retrieval speedup and 1.5x storage compactness at ~10-15pp recall cost vs float FAISS; algebraic moat operates at the projection layer with documented mitigations for compliance**."

## Recommended action

**1. Cap_map: NEW row proposed (research-only 🔬).**

Row name: "Substrate as audit-grade continuous-embedding store via SimHash projection"

Initial P-band: 0.35-0.45 (full-moat-with-mitigations); narrower band 0.50-0.65 for retrieval-recall-only (no moat constraint)

Caveats:
- Real-time learning survives intact under projection (P_def 0.92)
- Algebraic audit + edit isolation + deletion-cert DEGRADE under projection in characterizable ways; mitigations available
- Edit isolation gap: semantic neighbors at cos>0.75 experience collateral edit effects
- Deletion-cert for GDPR strict-compliance requires sha256(x) + W_seed + timestamp side-data
- Recall@10 expected ~10-15pp below float FAISS without re-ranking; 5-7pp with over-sampling

**2. NEW experiment to dispatch.**

**Anchor**: `continuous_embedding_storage_substrate_v1_n16384`

**Spec sketch (exp_dev refines)**:

Setup:
- Substrate: N=16384, BSC codebook
- Projection: SimHash (`bipolar_code = sign(W_proj @ continuous_embedding)`) with W_proj a fixed Gaussian R^{N × d}
- Embedding source: pre-trained sentence-transformer (recommend BGE-small or MPNet, d=768) -- no Anthropic API required
- Benchmark: standard retrieval task subset (MS MARCO passage retrieval, BEIR SciFact, BEIR NFCorpus) at corpus size 10K-100K
- Side-data for moat preservation: store sha256(original_embedding) + W_seed alongside each substrate entry

Arms (4):
- **Arm 1: Retrieval recall**: SimHash N=16384 substrate vs FAISS FlatIP over original continuous embeddings. Measure recall@10, recall@100, MAP@10. With and without over-sampling (2x, 4x candidate retrieval + re-rank on substrate codewords).
- **Arm 2: Algebraic audit preservation**: for each substrate retrieval, decompose via unbinding to recover (key_codeword, value_codeword). Verify codeword decomposition exact for 100% of stored entries. Verify side-data hash links back to original embedding identity for compliance audit.
- **Arm 3: Edit isolation under projection**: edit 100 stored entries; measure MAP@10 delta on (a) semantically dissimilar entries (cos < 0.5; expect <5% delta) vs (b) semantic-neighbor entries (cos 0.7-0.85; expect <20% delta) vs (c) near-duplicate entries (cos > 0.85; expect potentially larger delta, document).
- **Arm 4: Deletion cert under projection**: delete 100 entries; verifier checks (i) projected codeword absent from substrate, (ii) sha256 in cert matches stored hash. Validate cert across collision regimes.

**Pre-reg HARD-PASS** (combined; both retrieval AND moat must hold):
- Arm 1: recall@10 ≥ 0.82 on MS MARCO at N=16384 with 2x over-sampling (within 10-15pp of FAISS baseline 0.92-0.95)
- Arm 2: audit decomposition exact for 100% of stored entries; sha256 side-data links back to original at 100%
- Arm 3: MAP@10 delta < 5% for semantically dissimilar entries (cos < 0.5); < 20% for semantic neighbors (cos 0.7-0.85)
- Arm 4: 100% cert verification rate; 0 false-positive certs (no cert verifies for non-deleted entry)

**Pre-reg HARD-FAIL** (any of):
- Arm 1: recall@10 < 0.50 at N=16384 with over-sampling (substrate fundamentally incompatible with sentence-embedding geometry)
- Arm 2: audit decomposition fails > 1% (collision-induced algebra corruption)
- Arm 3: MAP@10 delta > 15% for semantically dissimilar entries (edit isolation broken even with high-N mitigation)
- Arm 4: false-positive cert rate > 0 (cert verifies for non-deleted entry; compliance break)

**Pre-reg MIDDLE-BAND** (some pass, some don't):
- Recall in [0.50, 0.82] -- substrate is below product threshold but above failure floor; consider learned binarization arm
- Edit isolation in MIDDLE-BAND zone (some leakage at semantic neighbors but bounded) -- documented as known caveat in product positioning
- Audit passes but at projection layer only -- product framing must explicitly reframe "audit shows projected lineage + side-data hash" not "audit shows exact stored embeddings"

**Cost**: ~2 weeks engineering + ~2-4h GPU per full run. Local 8GB GPU sufficient at N=16384 (Modern Hopfield validated v297). NO CLOUD SPEND (uses pre-trained embeddings, no API).

**Routing**: orchestrator → exp_dev → queue.

**3. Sequencing recommendation.**

Recommended dispatch:
- Parallel to substrate-LLM Phase 1 build (different GPU workload pattern; minimal contention)
- After substrate-LLM Week 0 Missing 7 verdict (~tonight)
- Before substrate-LLM Phase 1 Week 5 evaluation (which uses Pattern B + LLM+substrate; this experiment's recall numbers INFORM whether the substrate's bridge-output retrieval is meaningful for RAG-replacement use case)
- In parallel with D1 compositional binding + D7 Bet B ret_A rescue (different machine workload patterns)

**4. Reject 4 of 5 proposed experiments (with explicit cross-refs).**

| Proposed | Why rejected | Cross-ref |
|---|---|---|
| **R-2** relational reasoning over embeddings | Continuous-projection ANGLE on D1 compositional binding (filed today); R-1 establishes whether projection works for retrieval; R-2 then reduces to "does compositional binding work in projected codeword space" which is D1 with a different corpus | `notes/strategy_request_to_strategy_capability_exploration_3_drills_2026-05-31.md` (D1); `notes/strategy_request_to_strategy_reasoning_storage_phase1_smoke_2026-05-31.md` |
| **R-3** edit isolation on embeddings | T2 validated edit isolation at bipolar atom level (v290 cap_map 45/45 cells unanimous); R-1 Arm 3 tests the projection-layer degradation; no separate experiment needed | `notes/substrate_capability_map.md` v290 T2 |
| **R-4** substrate as RAG replacement | Substantially duplicates substrate-LLM Phase 1 Week 5 4-way comparison (LLM-only / LLM-only-control / LLM+text-RAG / LLM+substrate); already locked in testbed handoff | `notes/testbed_handoff_substrate_llm_deep_integration_2026-05-31.md` Week 5 eval suite |
| **R-5** compositional embedding reasoning | Continuous-projection applied to D1 + reasoning storage Phase 1; doesn't add substantively new content; same logic as R-2 | Same as R-2 |

**5. Honest product reframing for cap_map + go-to-market.**

REPLACE the doc's strategic framing:
- Original: "Substrate is a continuous, relational, compositional knowledge store" / "Stores any continuous representation"
- Revised: **"Substrate is an audit-grade vector store + reasoning sidecar. Native representation is bipolar codewords with algebraic moat; continuous embeddings ingested via SimHash projection layer with documented moat-degradation characteristics."**

This narrower framing is more defensible and aligns with what the substrate ACTUALLY delivers. The product moat that survives projection:
- Real-time learning (intact)
- Algebraic audit at projection layer + side-data identity link (degraded but mitigable)
- Edit isolation for semantically distinct keys (intact); near-semantic-neighbor leakage documented (degraded)
- Deletion-cert with sha256 side-data for compliance use cases (mitigated)
- 10-20x retrieval latency advantage via XOR-popcount
- 1.5x storage compactness vs fp32 FAISS

The competitive positioning:
- vs FAISS: trades ~10-15pp recall for algebraic moat + 10-20x speed + 1.5x compactness + real-time updates without rebuild
- vs vector DBs (Pinecone, Weaviate): trades retrieval-recall for compliance-grade audit + cryptographic deletion
- vs LLM-only memory: substrate adds verifiable provenance + edit semantics + real-time updates

## Confidence

P_deflated (calibration-applied):
- **Full retrieval-and-moat HARD-PASS as defined above**: 0.35-0.45 with mitigations applied
- **Retrieval-recall HARD-PASS alone** (Arm 1 within 10-15pp of FAISS at N=16384 with over-sampling): 0.55-0.65
- **Real-time learning intact under projection**: 0.92 (near-certain; write mechanism unchanged)
- **Algebraic audit at projection layer with sha256 side-data**: 0.70 (structural argument is exact; mitigation cost is +32 bytes per entry)
- **Edit isolation for semantically dissimilar entries**: 0.65 (N=16384 pushes near-orthogonality)
- **Edit isolation for semantic neighbors at cos > 0.75**: 0.40 (degraded; mitigation requires learned binarization OR VQ-style codebook)
- **Deletion-cert for strict GDPR with side-data + key destruction**: 0.55 (mitigable; needs careful infrastructure)
- **Deletion-cert WITHOUT side-data**: 0.25 (collision ambiguity breaks compliance use case)

## Critical open empirical risks

1. **Projection collision rate at production scale**: at corpus size 1M with d=768 sentence embeddings, what's the expected number of exact bipolar collisions? The sign-RP collision probability formula gives per-bit rate; joint N-bit rate depends on embedding distribution's intrinsic dimensionality (typically much less than 768 for typical sentence corpora).
2. **Optimal projection design for isolation**: is there a projection scheme that jointly maximizes retrieval (similar embeddings → similar codes) AND edit isolation (edited key → low inner product with unrelated keys)? These are in direct tension; the Pareto frontier is unknown.
3. **VQ-style codebook as full mitigation**: if VQ outer tier + bipolar inner tier preserves all 4 moat properties at competitive recall, what's the codebook size needed? Drill A suggests K=512-2048 may be enough but empirical needed.
4. **Audit adversarial robustness**: if attacker knows W_proj, can they craft two continuous embeddings that project to the same bipolar code? Computational cost of attack vs GDPR-enforcement timescales is open.
5. **Long-tail behavior on retrieval recall**: kNN literature shows retrieval helps high-frequency contexts, fails on long-tail. SimHash at N=16384 may inherit this. Does substrate's algebraic structure differentiate long-tail behavior?

## Files of interest

- `notes/research_continuous_embedding_storage_audit_v1_2026-05-31.md` (full 5-experiment overlap audit + continuous-vs-bipolar gap analysis)
- Drill A return: projection schemes (SimHash recommended; 6 schemes evaluated; recall predictions; moat preservation per scheme)
- Drill B return: per-property moat analysis under projection (4 properties; survives/degrades/breaks; mitigations per degraded property)
- `notes/strategy_request_to_strategy_capability_exploration_3_drills_2026-05-31.md` (D1 compositional binding -- closely related to R-2/R-5)
- `notes/strategy_request_to_strategy_reasoning_storage_phase1_smoke_2026-05-31.md` (Scheme B reasoning storage -- related substrate-physics question)
- `notes/testbed_handoff_substrate_llm_deep_integration_2026-05-31.md` (Week 5 4-way comparison -- substantively R-4)
- `notes/substrate_capability_map.md` v290 T2 (edit isolation 45/45 cells unanimous -- R-3 ground truth)
- Memory: [[feedback-2x-means-depth]], [[feedback-no-padding-experiments]], [[feedback-no-smoke]], [[feedback-lit-scan-calibration-penalty]]

## Not auto-dispatched

This is a research delivery + recommendation. Orchestrator decides:
- (a) Whether to add cap_map row at 0.35-0.45 (full-moat) / 0.55-0.65 (retrieval-only) bands
- (b) Whether to ADOPT the honest product reframing for cap_map + product positioning
- (c) Experiment dispatch timing (recommended: after Week 0, parallel to substrate-LLM Phase 1)
- (d) Whether to REJECT R-2/R-3/R-4/R-5 explicitly OR leave as documented-duplicates without formal rejection
- (e) Engineering ownership (exp_dev for substrate + projection layer; testbed for FAISS baseline harness)

No engineering work begins without orchestrator queueing.

---
BULK-ARCHIVED 2026-06-01: previously processed (cap_map v311+ reflects acted-on work); routing closed retroactively per dashboard inbox-clearance Path A.
