# Research: Capabilities expansion Round 3 — 8 parallel drills synthesis (2026-06-01)

Date: 2026-06-01
Origin: user directive "we will not pause new capabilities - we need to map out the substrate" after Round 2
Method: 8 parallel Sonnet drills (~95-170s each, ~155K tokens combined) + main-thread synthesis
Per: [[feedback-dont-recommend-research-pause]] (new memory; capability mapping is user-paced)

## HEADLINE

**Round 3 confirms and strengthens the Round 2 "physics-grade not policy-grade" convergence**: 5 of 8 drills (FAISS hybrid, federated learning, retrieval explainability, feature store, cross-modal) independently arrive at the same epistemological framing — substrate offers ALGEBRAIC + THIRD-PARTY-VERIFIABLE properties where competitors offer only POLICY/OPERATIONAL ones.

**A second convergence emerged**: 4 of 8 drills (FAISS hybrid Angle 5, feature store sidecar, workflow engine audit-layer-FOR Temporal, knowledge graph alongside Neo4j) recommend **SIDECAR / COMPLEMENT positioning** — substrate sits ALONGSIDE existing infrastructure (Pinecone/Tecton/Temporal/Neo4j) as the audit-cert layer, NOT as replacement.

**A third convergence**: 4 drills (federated learning M4, feature store M5, FAISS Angle 2, retrieval explainability M3) name **DELETION CERTIFICATE** as the single most-load-bearing compliance primitive — federated unlearning is unsolved in gradient FL; no feature store offers it; no ANN index can produce it; combined with M3 counterfactual probe it's also the GDPR Art 22 explanation primitive.

## PER-DRILL SUMMARY

### Drill 1: Cross-modal substrate (5 mechanisms)

**Strategic angle**: only system that produces algebraic cross-modal provenance certificates (CLIP/Gemini/Flamingo cannot)

| Mech | Audit moat | P | Recommendation |
|---|---|---|---|
| **M3 Multi-substrate + cross-modal bridge** | Full + separable | **0.45** | First priority — clean per-modality cert chain; independently erasable |
| **M5 Compositional cross-modal queries** | Full + formula-transparent | **0.44** | Algebraic query formula IS the compliance artifact — unprecedented |
| M1 Modality-tagged atoms | Full | 0.42 | Foundational for M5 |
| M4 Hierarchical routing | Partial | 0.38 | Defer |
| **M2 Shared embedding via encoders** | No audit moat | 0.17 | **EXPLICITLY DO-NOT-PURSUE** (no differentiation from CLIP) |

### Drill 2: Knowledge-graph substrate (5 mechanisms)

**Strategic recommendation**: SEPARATE cap_map row "Relational KG encoding — multi-hop algebraic certificates" because capacity/error-accumulation profiles are empirically distinct from single-atom audit-memory row.

| Mech | P | Notes |
|---|---|---|
| **M1 Triple binding** (s⊙p⊙o) | **0.80 at K=5; 0.45 at K=100** | Foundational; soft-match retrieval is the wedge vs B-tree indexes |
| **M2 Heteroassociative chain** | 0.60 at 3-hop; 0.30 at 5-hop | Per-hop algebraic cert; multi-hop degradation is hard physics |
| **M5 RDF/SPARQL-compatible interface** | 0.70 single-pattern; 0.20 at 3+ JOINs | Strongest compliance moat (verifiable SPARQL query execution); JOIN degradation fundamental |
| M3 Hypergraph n-ary | 0.45 at 4-ary; 0.30 at 5-ary | Most novel; weakest empirical backing |
| M4 Property-graph encoding | 0.40 shared-W / 0.65 separate-W | Weakest differentiation vs Neo4j |

### Drill 3: Feature store with audit (5 mechanisms)

**Strategic wedge: SIDECAR architecture targeting Chief Risk Officer / DPO / model-validation team — NOT the ML platform team.** ML team keeps Feast/Tecton (latency); compliance team gets substrate-backed shadow copy with cert chain + deletion cert + point-in-time verifiability.

| Mech | P | Compliance hook |
|---|---|---|
| **M5 Deletion certificate** | **0.40** | **EDPB 2025 enforcement directly targets this gap** — no feature store offers it |
| **M4 Point-in-time cert-chain replay** | **0.45** | SR 11-7 banking audit; tamper-evidence for historical records |
| M1 Feature-vector cert chain | 0.45 | Foundational; latency risk |
| M2 Composition DAG (feature lineage) | 0.40 | Eng risk at N-hop depth |
| M3 Online/offline parity | 0.35 | Weakest diff; Tecton closes this gap |

**Regulatory timing window**: EDPB 2025 + EU AI Act Aug 2026 + revised SR 11-7 2026 — narrow window for technical capability to precede mandated standards.

### Drill 4: Substrate-FAISS embedding-index hybrid (5 angles)

**Strategic position: substrate does NOT serve retrieval; serves audit layer alongside FAISS.** Angle 5 hybrid sidecar is PRIMARY WEDGE.

| Angle | P | Recommendation |
|---|---|---|
| **A5 Hybrid Audit Sidecar** (FAISS retrieves + substrate audits) | **0.72-0.82 buildability** | **PRIMARY WEDGE — 1-2 eng-weeks** |
| **A2 Per-Vector Deletion Certificate** | **0.82-0.90 technical / 0.25-0.40 regulatory** | GDPR Art 17 — no ANN index can match |
| **A4 Per-Retrieval Audit Chain** | **0.78-0.88 technical** | EU AI Act Art 13 transparency |
| A3 Online Incremental | 0.60-0.72 at small M | Bounded working memory only (M≤0.138N) |
| **A1 ANN Parity** | **0.04-0.08** | **EXPLICITLY CLOSE — physics-mechanism constraint; 6 OOM capacity gap** |

### Drill 5: Federated learning substrate (5 mechanisms)

**Strategic wedge: NOT "better federated learning" — "auditable, erasable, cryptographically separable federated memory layer".** Not competing with Flower for ResNet-50 training across 1000 hospitals.

| Mech | P | Wedge |
|---|---|---|
| **M4 Deletion certificate (federated unlearning)** | **0.90 algebraic / 0.60-0.75 retrieval drop / 0.35-0.50 legal** | **STRONGEST DIFFERENTIATOR — federated unlearning UNSOLVED in gradient FL; substrate solves algebraically with zero retraining** |
| M1 Per-client + exact W aggregation | 0.55-0.65 at small k; 0.25-0.35 at k=100 | NO FedAvg convergence gap (linear aggregation is exact) |
| M3 Client-side DP + cross-client audit chain | 0.60-0.70 | HIPAA federated medical |
| M5 Edge-substrate with online learning | 0.40-0.55 stability | Small N=128-256 fits microcontroller; 256KB W footprint |
| M2 Algebraic secure aggregation + rank-based Byzantine | 0.75 port / 0.35-0.45 ZK rank novelty | Engineering gap large on ZK proofs |

### Drill 6: Substrate-LLM bidirectional learning (5 mechanisms)

**KEY CONSTRAINT: LLM write-error rate is the binding constraint on entire architecture. Must be first measurement.** Audit moat collapses if >20% error rate.

| Mech | P | Notes |
|---|---|---|
| **M4 In-context distillation** | **0.45-0.55 — highest P** | Hippocampal-cortical consolidation analog; GDPR Art 5 data minimization (delete raw logs after distillation) |
| M1 LLM-supervised substrate writes | 0.45-0.55 | Cheapest bidirectional loop; GDPR Art 17 audit trail of writes |
| M5 Substrate-guided LLM constraint | 0.55-0.65 soft / 0.30-0.40 hard | Hard-constraint rejection logs = NEW audit artifact ("why the model didn't say X") |
| M3 RLHF with substrate-stored preferences | 0.35-0.45 | Personalized alignment with audit trail; EU AI Act Art 14 human oversight |
| M2 Substrate as fine-tuning evidence store | 0.30-0.40 | SR 11-7 + EU AI Act traceable fine-tuning |

### Drill 7: Retrieval explainability (5 mechanisms)

**THE WEDGE IN ONE SENTENCE**: "LLM attribution is approximate, post-hoc, and unverifiable by a third party; substrate attribution is exact, inline, and independently re-derivable from archived linear-algebraic state." Holds regardless of how good LLM explainability becomes — different epistemological class.

| Mech | P | Tier |
|---|---|---|
| **M1 Per-hop attribution** | **1.0 algebraic / 0.65-0.80 practical** | **TIER 1 ship now** |
| **M2 Cosine-contribution decomposition** | **0.90-0.95 at low load** | **TIER 1 ship now — O(K·d) linear vs SHAP O(2^D) for transformers** |
| **M3 Counterfactual probe via algebraic delta** | **0.85-0.92** | **TIER 2 — STRONGEST single compliance primitive (GDPR Art 17 erasure + Art 22 explanation in one cert)** |
| M4 Confidence-weighted Bayesian attribution | 0.60-0.75 | Tier 3 (Bayesian infra dependency) |
| M5 Cross-tenant + cross-modality attribution | 0.90-0.95 isolation / 0.70-0.80 contamination | Tier 4 (depends on multi-tenant Arch 1 from Round 2) |

### Drill 8: Information-theory readout (5 mechanisms)

**Hard-fail threshold (cross-cutting)**: must outperform naive baseline (pattern count / cosine threshold / raw histogram) at N=512 5-seed. If not → mathematical curiosity not product feature.

| Mech | P | Best fit |
|---|---|---|
| **M4 Effective Channel Capacity** | **0.45 — strongest commercial** | Infrastructure-monitoring analog; "X% of substrate capacity used" |
| **M1 Renyi Entropy** | **0.35 — strongest compliance** | **GDPR Art 5(1)(c) data minimization certificate** |
| M2 Fisher Information at retrieval | 0.40 | Robustness certificate; NIST AI RMF Govern 1.7/Measure 2.5; spectral phase transition at Edge-of-Stability (arxiv 2511.23083) |
| M5 Entropy-rate drift detection | 0.35 | SELF-SUPERVISED (no labels) — extends Round 1 drift detection |
| M3 Mutual information across atoms | 0.30 | Weakest commercial; O(M²N) expensive |

## CONVERGENT FINDINGS (cross-Round 1+2+3)

### Convergence 1: "Physics-grade not policy-grade" (now 8 drills across Rounds 2+3)

Round 2: multi-tenant, DP, disaster recovery
Round 3: FAISS hybrid (A5 audit moat), federated learning (M4 deletion algebra), retrieval explainability (epistemological class), feature store (cryptographic deletion cert), cross-modal (algebraic provenance)

**Strengthens the recommendation**: bundle as ONE unified "audit-grade memory with physics-grade guarantees" positioning across 8 distinct capability domains.

### Convergence 2: SIDECAR / COMPLEMENT positioning

Round 2: KV cache (#1 tool-call caching alongside existing caches), workflow engine (audit-layer FOR Temporal/LangGraph)
Round 3: FAISS hybrid (A5 alongside FAISS), feature store (sidecar alongside Feast/Tecton), knowledge graph (alongside Neo4j)

**Strategic implication**: substrate's GTM is plug-into-existing-stacks as audit layer, not replace-incumbent. Reduces eng scope; makes the cryptographic-proof differentiator legible to buyers who already use Pinecone/Tecton/Temporal/Neo4j.

### Convergence 3: DELETION CERTIFICATE as load-bearing primitive

Round 1: PP-9 amortization economics
Round 2: DP Mechanism 1 + DR Mechanism 1
Round 3: federated learning M4, feature store M5, FAISS Angle 2, retrieval explainability M3, time-series (Round 2)

**Strategic implication**: deletion certificate is the SINGLE PRIMITIVE that powers multiple killer features across capability axes. Highest-leverage engineering investment. Already partly characterized by audit-grade-vector-store row at 0.45-0.65; this convergence justifies promoting it to a first-class substrate primitive in its own right.

### Convergence 4: Cross-tenant + cross-modal + cross-LLM attribution share architecture

Round 2 multi-tenant Arch 1 (per-tenant W) + Round 3 retrieval explainability M5 (cross-tenant attribution) + Round 3 cross-modal substrate M3 (multi-substrate per modality + bridge) + Round 3 federated learning M1 (per-client W aggregation) ALL use **per-domain separate W matrices with algebraic separability**.

**Strategic implication**: ONE production architecture (per-domain W with bridge atoms + separability proofs) serves multi-tenant SaaS, cross-modal retrieval, federated learning, AND cross-tenant attribution. Highest architectural-leverage investment.

## TIER 1 DISPATCHABLE NOW (Round 3 additions to existing Round 1+2 Tier 1)

| # | Item | Source | Cost |
|---|---|---|---|
| T1.6 | **Retrieval explainability cosine-contribution smoke** | Drill 7 M2 | <10s CPU; unit test of attribution monotonicity |
| T1.7 | **Retrieval explainability counterfactual probe smoke** | Drill 7 M3 | <5s CPU; planted-pattern test |
| T1.8 | **Effective channel capacity sweep** | Drill 8 M4 | ~10 min CPU; M sweep at N=1024 |
| T1.9 | **FAISS hybrid sidecar smoke** | Drill 4 A5 | 1-2h CPU; write+query+delete+verify cert |
| T1.10 | **Federated deletion certificate smoke** | Drill 5 M4 | 60s CPU; k=5 clients, delete one |

Combined with Round 2's Tier 1 items: 10 cheap diagnostic smokes covering 10 distinct cap_map rows.

## TIER 2 (medium info gain; engineering scope)

- **Bidirectional learning M4 in-context distillation prototype** — 20-conversation synthetic test; ~1 week eng
- **Knowledge graph M1 triple binding smoke** at K=100 atoms — ~30 min CPU
- **Cross-modal M3 multi-substrate + bridge smoke** — ~30 min CPU
- **Feature store M5 deletion certificate prototype** — 1 week eng (M=1000, delete 100, verify certs)
- **Info-theory M5 entropy-rate drift detection** — extends Round 1 drift mechanism; ~30 min CPU
- **Retrieval explainability M5 cross-tenant attribution smoke** — depends on Round 2 multi-tenant Arch 1

## CAP_MAP IMPLICATIONS

**NEW rows proposed** (Round 3 additions):

| Row | State | Anchor |
|---|---|---|
| Audit-grade knowledge graph (relational KG encoding) | 🔬 0.45-0.60 | M1+M2+M5 mechanisms; separate from atom-registry DAG |
| Audit-grade ML feature store (sidecar) | 🔬 0.40-0.55 | M5+M4 deletion + PIT cert-chain |
| Cross-modal substrate provenance | 🔬 0.40-0.55 | M3 multi-substrate + bridge |
| Federated learning substrate | 🔬 0.45-0.60 | M4 deletion cert + M1 exact aggregation |
| Substrate retrieval explainability primitives | 🟡 0.55-0.70 | M1+M2 algebraically exact; M3 counterfactual cheap |
| Substrate-LLM bidirectional learning | 🔬 0.40-0.55 | M4 distillation + M1 supervised writes |
| Information-theory readout suite | 🔬 0.35-0.50 | M4 capacity strongest commercial |

**Sub-properties** (no new row):
- Channel capacity monitoring → PP-2 storage efficiency sub-property
- Renyi entropy data-minimization cert → PP-3 audit rotation sub-property

**Explicit CLOSURES recommended** (4 additions):
- Cross-modal M2 (shared embedding) — no audit moat, no diff vs CLIP
- FAISS Angle 1 (ANN parity) — physics constraint, cannot compete
- Knowledge graph M4 (property-graph encoding) — weakest diff vs Neo4j
- Info-theory M3 (mutual information across atoms) — expensive + competitor served

## STRATEGIC NARRATIVE BUNDLING (post Round 1+2+3, 24 drills total today)

The unified narrative is now load-bearing across 24 capability drills:

> **"Audit-grade memory with physics-grade guarantees: substrate stores facts with intrinsic algebraic certificates for audit, privacy (DP), tenant isolation, edit-impact-prediction, deletion, recovery, attribution, cross-modal provenance, federated unlearning, feature lineage, and bidirectional LLM learning — guarantees that no logging-based system can produce because they are mathematical properties of the storage algebra, not policy enforcement at the API layer. Position: sidecar audit layer alongside existing infrastructure (Pinecone/Tecton/Temporal/Neo4j/Feast), not replacement."**

Wedge narrowed and sharpened: compliance-driven regulated industries; sidecar GTM; deletion-cert + cross-domain-W-separability + algebraic-attribution as the three universal primitives that power all 11+ named killer features.

## METHOD NOTES

- 8 parallel Sonnet drills + main-thread synthesis ≈ ~155K tokens combined
- 24 total capability drills today across Rounds 1 + 2 + 3
- Per [[feedback-dont-recommend-research-pause]]: capability mapping is user-paced; no pause recommendation
- Per [[feedback-subagent-model-optimization]]: Sonnet for lit-scan / design-pattern drills
- Per [[feedback-query-privacy-decomposition]]: all drills generic terms; no project-identifying fingerprints
- Per [[feedback-lit-scan-calibration-penalty]]: P estimates deflated throughout
- Wall time: dispatch + 8 parallel drills (~95-170s each) + synthesis ≈ 30-40 min main-thread

Acted-on 2026-06-01: Round 3 conclusions adopted in cap_map v315 via parallel routing
