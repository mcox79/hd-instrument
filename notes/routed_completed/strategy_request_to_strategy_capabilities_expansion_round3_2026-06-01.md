# Strategy request: capabilities expansion Round 3 follow-on (8-drill consolidated routing)

**From**: research
**To**: strategy
**Date**: 2026-06-01
**Source**: `notes/research_capabilities_expansion_round3_8_drills_2026-06-01.md` (full Round 3 synthesis)

## TL;DR

8-drill Round 3 STRENGTHENS the Round 2 convergent finding ("physics-grade not policy-grade"; now 8 drills across Rounds 2+3) AND surfaces THREE new convergences:

1. **SIDECAR / COMPLEMENT positioning** (4 drills): substrate sits ALONGSIDE existing infrastructure (Pinecone/Tecton/Temporal/Neo4j/FAISS) as audit-cert layer, NOT replacement. Reduces eng scope; makes cryptographic-proof differentiator legible to existing buyers.

2. **DELETION CERTIFICATE as universal primitive** (5 drills): single primitive that powers killer features across federated learning, feature store, FAISS hybrid, retrieval explainability, time-series. Highest-leverage engineering investment. Promote to first-class substrate primitive.

3. **Cross-domain W separability shares architecture** (4 drills): per-domain separate W matrices + bridge atoms + separability proofs serve multi-tenant SaaS, cross-modal retrieval, federated learning, AND cross-tenant attribution. ONE production architecture powers 4 capability axes.

**24 total capability drills today across Rounds 1+2+3.** 7 NEW cap_map rows proposed from Round 3 + 2 sub-properties + 4 explicit closures.

## CONVERGENCE-DRIVEN STRATEGIC SHIFTS

### Shift 1: Bundle into unified "audit-grade memory with physics-grade guarantees" positioning

Across 24 drills, the moat description is consistent. Recommendation: stop tracking these as separate features; track as ONE positioning narrative with 11+ named killer-feature instances. The narrative IS the product story:

> Substrate stores facts with intrinsic algebraic certificates for audit, privacy (DP), tenant isolation, edit-impact-prediction, deletion, recovery, attribution, cross-modal provenance, federated unlearning, feature lineage, and bidirectional LLM learning — guarantees that no logging-based system can produce because they are mathematical properties of the storage algebra, not policy enforcement at the API layer.

### Shift 2: Adopt sidecar GTM as primary product framing

Substrate's 19.78ms p99 cannot compete with Redis (~1ms), FAISS (<1ms), or specialized TSDb throughput. It can win on intrinsic cryptographic properties that those systems STRUCTURALLY cannot provide. The sidecar architecture sidesteps the latency/throughput competition entirely:

- ML platform team keeps Feast/Tecton (latency); compliance team gets substrate shadow
- Application stack keeps Pinecone/FAISS (recall); regulator gets substrate audit chain
- DevOps team keeps Temporal (durability); audit team gets substrate per-step cert
- Data engineering keeps Neo4j (query throughput); legal gets substrate triple deletion certs

This sidesteps the "is substrate fast enough?" question that has been a constant drag on positioning. Substrate is NEVER on the hot path; it's always on the compliance path.

### Shift 3: Promote deletion certificate to first-class substrate primitive

Currently distributed across multiple cap_map rows (PP-9, audit-grade-vector-store row, federated learning new row, feature store new row). Convergence across 5 drills argues for treating it as a SHARED PRIMITIVE that powers multiple killer features. Single engineering investment with multi-row downstream impact.

## TIER 1 dispatchable now (Round 3 additions; combined with Round 2 = 10 cheap diagnostics)

| # | Item | Source | Cost |
|---|---|---|---|
| T1.6 | Retrieval explainability cosine-contribution smoke | Drill 7 M2 | <10s CPU |
| T1.7 | Retrieval explainability counterfactual probe smoke | Drill 7 M3 | <5s CPU |
| T1.8 | Effective channel capacity sweep | Drill 8 M4 | ~10 min CPU |
| T1.9 | FAISS hybrid sidecar smoke | Drill 4 A5 | 1-2h CPU |
| T1.10 | Federated deletion certificate smoke | Drill 5 M4 | 60s CPU |

Combined Tier 1 from Rounds 2+3: 10 diagnostics across 10 cap_map rows. Wall ~4-5 hours total.

## TIER 2 (1-2 eng-week scope each)

- Bidirectional learning M4 in-context distillation prototype (~1 week eng)
- Knowledge graph M1 triple binding at K=100 atoms (~30 min CPU)
- Cross-modal M3 multi-substrate + bridge smoke (~30 min CPU)
- Feature store M5 deletion certificate prototype (~1 week eng)
- Info-theory M5 entropy-rate drift detection (extends Round 1 PP-4; ~30 min CPU)
- Retrieval explainability M5 cross-tenant attribution (depends on multi-tenant Arch 1)

## CAP_MAP IMPLICATIONS

**7 NEW rows proposed** (Round 3):

| Row | Initial state |
|---|---|
| Audit-grade knowledge graph | 🔬 0.45-0.60 |
| Audit-grade ML feature store (sidecar) | 🔬 0.40-0.55 |
| Cross-modal substrate provenance | 🔬 0.40-0.55 |
| Federated learning substrate | 🔬 0.45-0.60 |
| Substrate retrieval explainability primitives | 🟡 0.55-0.70 |
| Substrate-LLM bidirectional learning | 🔬 0.40-0.55 |
| Information-theory readout suite | 🔬 0.35-0.50 |

**Combined with Round 2's 4 new rows**: 11 new rows proposed across both rounds. Cap_map grows from ~28 to ~39 rows after authorization.

**Sub-properties** (no new row):
- Channel capacity monitoring → PP-2 storage efficiency sub-property
- Renyi entropy data-minimization cert → PP-3 audit rotation sub-property

**Explicit CLOSURES recommended** (Round 3, 4 additions):
- Cross-modal M2 (shared embedding) — no audit moat
- FAISS Angle 1 (ANN parity) — physics constraint
- Knowledge graph M4 (property-graph encoding) — weakest diff
- Info-theory M3 (mutual information across atoms) — expensive + competitor served

Combined with Round 2's 5 closures: 9 explicit close-recommendations across both rounds.

## CONTRACT FOR STRATEGY

1. **Adopt unified "audit-grade memory with physics-grade guarantees" positioning?** (per 24-drill convergence)
2. **Adopt sidecar GTM as primary?** (per 6-drill complement-not-replace convergence across Rounds 2+3)
3. **Promote deletion certificate to first-class shared primitive?** (per 5-drill convergence)
4. **Authorize 7 NEW cap_map rows from Round 3** + 2 sub-properties + 4 closures?
5. **Tier 1 dispatch sequencing**: Rounds 2+3 combined = 10 cheap smokes across 10 rows
6. **Engineering priority**: which Tier 2 / Tier 3 multi-week items to greenlight first?

## METHOD NOTES

- 8 parallel Sonnet drills + main-thread synthesis ≈ ~155K tokens
- 24 total capability drills today across Rounds 1+2+3
- Per [[feedback-dont-recommend-research-pause]]: continuing capability mapping per user direction
- Per [[feedback-no-padding-experiments]]: each drill on distinct capability axis
- Per [[feedback-aggressive-cross-domain-research]]: cross-domain probes covered (info theory, federated learning, knowledge graphs)

## CLOSING

Move to `routed_completed/` when strategy:
1. Authorizes (or amends) the 3 strategic shifts (unified positioning / sidecar GTM / deletion-cert primitive)
2. Approves NEW cap_map rows + sub-properties
3. Confirms CLOSURES on the 4 directions
4. Decides Tier 1 dispatch + Tier 2/3 priorities

Acted-on 2026-06-01: 3 strategic shifts + 7 NEW rows + 2 sub-properties + 4 closures ADOPTED in cap_map v315; Tier 1 dispatch routing filed for exp_dev
