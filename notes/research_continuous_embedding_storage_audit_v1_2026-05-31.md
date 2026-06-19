# Research: continuous-embedding storage proposal audit (v1)

Date: 2026-05-31
Origin: user 2026-05-31 -- shared 5 experiments (R-1 through R-5) framing substrate as "continuous, relational, compositional knowledge store"; "do 2x deep research"
Method: main-thread audit + 2 parallel Sonnet drills on the load-bearing prerequisite question (continuous-to-bipolar projection + moat preservation under projection). Synthesis pending drill returns.

## HEADLINE

The doc's framing has a fundamental representation gap: substrate is BIPOLAR ({-1,+1}^N with MAP-B element-wise binding), NOT a continuous-representation store. Storing continuous embeddings requires a projection scheme; the projection scheme is the load-bearing engineering question that determines whether R-1 through R-5 are feasible. The 5 proposed experiments collapse to ONE substantive new question (continuous-to-bipolar projection at substrate's validated envelope) + several duplicates of existing in-flight work. 4 of 5 substantially overlap. Drills resolve the projection question + moat-preservation question; synthesis routing will propose ONE genuinely-new experiment.

## The fundamental representation gap

The doc claims substrate "Stores any continuous representation (embeddings, vectors, hyperdimensional objects)." This is not what the substrate as built / validated does. The substrate stores BIPOLAR codewords in {-1,+1}^N drawn from a structured codebook (BSC or Kerdock). Validated capabilities (multi-hop, edit isolation, deletion certs, audit, real-time learning) operate at THIS LAYER — atomic bipolar codewords.

Continuous embeddings (sentence-transformer R^768, OpenAI R^1536, Cohere R^3072) are NOT native to this algebra. To ingest them, the substrate needs a PROJECTION SCHEME continuous-R^d → bipolar {-1,+1}^N. Each scheme has different:
- Information loss (cosine-similarity preservation rate)
- Storage cost
- Algebraic-moat preservation (does audit / edit-iso / deletion-cert survive?)
- Implementation complexity

The doc treats this as trivial. It's not. It's the load-bearing engineering question for the entire "continuous knowledge store" framing.

Projection scheme options (drill A is evaluating):
1. Random Gaussian projection + sign() (Johnson-Lindenstrauss + binarization; SimHash-class)
2. LSH variants (random hyperplane, p-stable, spherical)
3. VQ-style projection (continuous → nearest centroid in learned codebook)
4. Learned binarization / deep hashing networks
5. Spectral projection (PCA + sign)
6. Hybrid (random projection + learned residual)

Moat-preservation question (drill B is evaluating):
- Audit decomposition: exact for atomic codewords; under projection, decomposes to PROJECTED REPRESENTATIVES not original embeddings — DEGRADED
- Edit isolation: validated at near-orthogonal random keys; under projection, semantically similar embeddings → bit-close codewords → potential collateral edits — POTENTIALLY DEGRADED
- Deletion certificate: certificate over PROJECTED codeword, not original embedding; collisions break "specific user data erasure" semantics — POTENTIALLY BREAKS for compliance use case
- Real-time learning: SURVIVES INTACT (same rank-1 outer-product write)

## Overlap matrix: 5 experiments vs in-flight/filed work

| Doc's experiment | Genuinely new content | Substantially overlaps with |
|---|---|---|
| **R-1 continuous embedding storage** | **The projection scheme question — THIS IS THE LOAD-BEARING NEW WORK** | -- |
| R-2 relational reasoning over embeddings | Continuous-projection ANGLE applied to relational queries | D1 compositional binding production-scope (filed today); reasoning storage Phase 1 smoke (filed today) |
| R-3 edit isolation on embeddings | Continuous-projection-preserves-edit-isolation question | T2 validated edit isolation at bipolar atom level (v290 cap_map 45/45 cells unanimous) |
| R-4 substrate as RAG replacement | NONE | **Substrate-LLM Phase 1 Week 5 4-way comparison** is exactly this test (LLM-only / LLM-only-control / LLM+text-RAG / LLM+substrate); already locked in testbed handoff |
| R-5 compositional embedding reasoning | Continuous-projection applied to D1 | D1 compositional binding + reasoning storage Phase 1 |

**Net**: the 5 experiments collapse to 1 genuinely-new question (continuous-to-bipolar projection at substrate's envelope, applied across multiple use cases) + R-4 duplicates substrate-LLM build's Week 5 evaluation.

## What this means for the strategic framing

The doc's framing — "substrate is a fundamentally new kind of system that stores any continuous representation" — overshoots the substrate's actual capability:
- The validated substrate stores BIPOLAR ATOMS from a structured codebook
- Continuous-embedding storage requires an additional engineering layer (projection)
- The moat properties (audit, edit-iso, deletion-cert) operate at the BIPOLAR layer; they DEGRADE under projection at varying rates

A more honest framing:
> "Substrate is a bipolar associative memory with algebraic audit + edit isolation + deletion certificates. It can be EXTENDED to ingest continuous embeddings via a projection layer, but the moat properties operate at the projection layer (not at the original continuous embedding layer), and degrade by mechanism-specific amounts."

This narrower framing is more defensible. The "continuous, relational, compositional knowledge store" framing requires the projection question to be resolved empirically AND the moat to be shown to survive at sufficient fidelity for product positioning.

## What I'll file when drills return

The synthesis will propose ONE genuinely-new experiment:

**Anchor (tentative)**: `continuous_embedding_storage_substrate_v1_n16384`

**Spec sketch** (drills will refine):
- Ingest pre-trained sentence-transformer embeddings (e.g., MPNet or BGE small) for a standard retrieval benchmark (MS MARCO passage subset, BEIR)
- Apply the drill-A-recommended projection scheme(s)
- Store in substrate at N=16384
- Measure retrieval recall@10 vs FAISS baseline over original continuous embeddings
- Test 3 moat properties under projection: audit-trace-completeness, edit-then-query-consistency, deletion-cert-verification
- Compare to FAISS k-NN (which has none of the moat properties)

**Pre-reg HARD-PASS**:
- Recall@10 within 5pp of FAISS at substrate's capacity
- Audit-trace-completeness 100%
- Edit-consistency >0.95 (mitigations applied per drill B)
- Deletion-cert verifies for projected codeword + side-data hash (per drill B mitigation)

**Pre-reg HARD-FAIL**:
- Recall@10 below 0.5× FAISS (substrate retrieval substantially worse on continuous embeddings)
- OR any moat property breaks irrecoverably (e.g., edit operations propagate collaterally beyond mitigation)

**Pre-reg MIDDLE-BAND**:
- Recall@10 in [0.5× FAISS, FAISS-5pp]
- Or moat partially preserved at degraded fidelity

**Cost**: ~2 weeks engineering + ~1-2h GPU per full run. Local 8GB sufficient. Anthropic API not required (uses pre-trained embeddings).

**What to REJECT (4 of 5)**:
- R-4 as duplicate of substrate-LLM Phase 1 Week 5
- R-2 / R-3 / R-5 as continuous-projection-applied-to-existing-work; the projection question is what this experiment resolves; once resolved, R-2/R-3/R-5 reduce to applications

## Strategic implications

If the continuous-projection experiment PASSES (substrate matches FAISS recall@10 with moat preserved):
- Substrate IS a viable continuous-knowledge store with algebraic moat
- The doc's framing is empirically supported (with the projection-layer caveat)
- Substrate-as-RAG-replacement is a real product direction

If PARTIAL pass (moat preserved at degraded fidelity):
- Substrate is positioned as audit-grade vector store for use cases where some moat properties matter more than perfect-retrieval
- Narrower product positioning than the doc claims

If FAIL (recall <0.5× FAISS or moat breaks):
- Substrate is NOT a continuous-embedding store; the doc's framing oversold
- Memory-layer / fact-store positioning remains right; the continuous-embedding direction closes

All three outcomes are strategically informative.

## Method note

Audit FIRST (this note); 2 parallel Sonnet drills on the load-bearing prerequisite questions; synthesis when drills return. Pattern reconfirmed per [[feedback-2x-means-depth]]: the deepening is on the underlying ENGINEERING QUESTION (projection scheme), not re-running the 5 experiments as separate drills.

The doc's 5 experiments were product-positioning questions; the substantive empirical question that gates all 5 is the projection question. Drilling at THAT level — the actual physics + engineering — is the depth-2 work. Per [[feedback-no-padding-experiments]] not dispatching 5 drills when 2 deeper drills resolve the prerequisite.
