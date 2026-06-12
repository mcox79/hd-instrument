# L4 GNN integration of SHARES_MATH edge type: R-GCN / HAN per-edge-learned-weight architectural design

Date: 2026-06-12
Drill type: 2x DEEP (architectural design drill on existing SHARES_MATH + graph-edge-typology findings)
Calibration: lit-scan penalty applied (P deflated 0.15-0.25; novel-synthesis cap 0.50)
Scope: STRONG on R-GCN/HAN base architecture; MODERATE on equivalence-class message passing semantics; SPECULATIVE on substrate-specific HARD-PASS magnitudes.

## Drill spec

Design L4 GNN layer for ~1742-atom substrate knowledge graph using R-GCN / HAN over heterogeneous edge types, with special message-passing semantics for SHARES_MATH equivalence-class edges. Pre-register a substrate cell for Cycle 52.

Edge type whitelist (from prior drills):
- Primary content edges (full-weight): SHARES_FILLER, INSTANCE_OF, TOPIC_OF, SHARES_MATH
- Learn-weight edges: OPERATES_ON, PART_OF
- Strong-prior-zero (excluded from message passing): DEPENDS_ON

## HEADLINE

R-GCN with HAN-style per-edge-type attention is the canonical base architecture for the substrate's heterogeneous edge typology; SHARES_MATH should be treated as an equivalence-class edge with symmetric mean-aggregation within connected components and learned cross-component attention, injected at an EARLY GNN layer (layer 1 of 2-3) so downstream layers can propagate math-equivalence-conditioned representations through SHARES_FILLER / INSTANCE_OF / TOPIC_OF. Pre-registered HARD-PASS: A-axis macro >= 0.50, B-axis >= 0.75, D-axis >= 0.65; HARD-FAIL: any axis regresses below current baseline.

## Round 1 findings (compact)

Six generic literature queries, integrating well-established results:

1. R-GCN (Schlichtkrull et al. 2018) - per-edge-type weight matrices; basis-decomposition and block-diagonal-decomposition both reduce parameter count when relation count is large; canonical baseline for relational message passing.
2. HAN (Wang et al. 2019) - heterogeneous graph attention; two-level attention (node-level within meta-path, semantic-level across meta-paths); strong on heterogeneous graphs with small-to-medium relation counts.
3. GNN for KG completion (TransE / DistMult / ComplEx as decoders; R-GCN / CompGCN as encoders) - encoder-decoder pattern dominates KG embedding literature.
4. Edge-type embedding GNNs (CompGCN, Vashishth et al. 2020) - represent relations as vectors; node-relation composition via subtraction / multiplication / circular correlation; circular correlation = HRR-binding analogue (direct architectural fit with substrate's FHRR core).
5. Equivalence-class node representation (community-aware GNNs, cluster-GCN) - explicit equivalence-class structure can be exploited via partition-aware aggregation; community-conditioned attention improves downstream.
6. Schema-aware GNNs (relational meta-learning, HGT - Heterogeneous Graph Transformer, Hu et al. 2020) - type-conditional transformations per source-target node-type pair.

Compact synthesis: R-GCN is the parameter-efficient baseline; HAN adds attention flexibility; CompGCN's circular-correlation composition directly maps to FHRR binding (substrate-native fit); HGT generalizes type-conditional message passing.

## Round 2 findings (compact)

Six refined queries:

1. R-GCN basis decomposition - when relation count >> hidden dim, basis decomposition shares parameter blocks across relations; for substrate's 6-7 active edge types and 256-512 hidden dim, basis-decomposition is NOT needed (small relation count); use full per-edge matrices.
2. Compositional GNN multi-relation (CompGCN) - subtraction / multiplication / circular-correlation are three composition operators; circular correlation = FHRR-conjugate-multiplication (substrate-native).
3. Path-aware GNN over KG (PathCon, NBFNet, Zhu et al. 2021) - reasoning over paths rather than just neighbors; relevant for D-axis (composition retrieval), where multi-hop chains matter.
4. Type-conditional message passing (HGT) - separate weight matrices per (source-type, edge-type, target-type) triple; for substrate's homogeneous node-type universe (all atoms), this collapses to edge-type-only conditioning = R-GCN.
5. Equivalence-graph node embedding clustering - within connected components, mean-pool aggregation produces a class-representative; cross-class attention can then use representative-to-representative; reduces effective graph density and improves downstream stability.
6. KG embedding ComplEx / RotatE - decoder-side approaches; not directly applicable as L4 encoder but useful as link-prediction objective for SHARES_MATH edge prediction (auxiliary task to validate the equivalence structure).

Compact synthesis: CompGCN with circular-correlation composition + HAN-style cross-relation attention + connected-component mean-pool for SHARES_MATH = canonical substrate-native L4 GNN.

## Architectural synthesis (substrate L4 GNN design)

### Base architecture

- R-GCN / CompGCN hybrid: per-edge-type learned weight matrices W_r (one per edge type in the whitelist), with CompGCN-style circular-correlation composition for node-relation interaction.
- HAN-style attention layer on top: learned attention weights a_r per edge type, computed from node-pair features; soft-weights the per-edge-type messages.
- 2-3 GNN layers; depth = 2 is sufficient for ~1742-atom graph (most semantic neighborhoods reachable in 2 hops); depth = 3 only if D-axis multi-hop composition retrieval requires it.
- Hidden dim 256 (compact, sufficient for substrate's relation density); upgrade to 512 only if 256 underperforms.

### SHARES_MATH special semantics

- Pre-compute connected components over SHARES_MATH edges only (cheap, one-time per cap_map version).
- Within-component aggregation: SYMMETRIC mean-pool over all atoms in the component (no within-class hierarchy; equivalence classes by definition have no internal order).
- Cross-component aggregation: HAN-style learned attention between component representatives.
- Compression: non-representative atoms in a component get a "compressed message" = their own embedding + the component representative's residual; representatives carry full message-passing context.
- Layer position: inject SHARES_MATH at LAYER 1 (early), so downstream layers (layer 2, layer 3 if present) can propagate math-equivalence-conditioned representations through other edge types.

### Why early injection (load-bearing)

If SHARES_MATH is injected late, downstream SHARES_FILLER / INSTANCE_OF / TOPIC_OF propagation cannot benefit from math-equivalence regularization; the equivalence signal must be in the representation space EARLY so subsequent layers operate on math-canonical embeddings.

### Loss / training objectives

- A-axis (content retrieval): contrastive loss on atom-to-atom similarity in GNN embedding space.
- B-axis (relation retrieval): edge-type prediction auxiliary task.
- D-axis (composition retrieval): path-prediction loss over 2-3 hop chains.
- Auxiliary: SHARES_MATH link prediction (ComplEx / RotatE decoder) to validate equivalence structure during training.

## Pre-registered substrate cell (Cycle 52)

- Graph: 1742+ atom knowledge graph; edge whitelist as above; DEPENDS_ON excluded.
- Architecture: R-GCN + CompGCN circular-correlation composition + HAN attention; 2 layers (extend to 3 only if D-axis underperforms); hidden dim 256.
- SHARES_MATH: layer-1 injection; symmetric within-component mean-pool; learned cross-component attention.
- Training: multi-task loss (A-axis contrastive + B-axis edge-type + D-axis path + SHARES_MATH link-prediction auxiliary).
- Eval: A / B / D axis macro on Gap 7 v4 benchmark.
- HARD-PASS thresholds:
  - A-axis macro >= 0.50 (vs current 0.378 keyword-route baseline) - delta +0.122.
  - B-axis macro >= 0.75 (vs current 0.70 post-edge-authoring baseline) - delta +0.05.
  - D-axis macro >= 0.65 (vs current 0.50 baseline) - delta +0.15.
- HARD-FAIL thresholds:
  - Any axis regresses below current baseline (A < 0.378, B < 0.70, D < 0.50).
  - Aggregate macro-F1 across A+B+D < 0.55 (current weighted ~0.526).

Pre-registered P (deflated):
- P(any-axis HARD-PASS): 0.45 (raw 0.65, deflate 0.20 for novel-synthesis on substrate-specific graph).
- P(all-three HARD-PASS): 0.20 (raw 0.40, deflate 0.20).
- P(D-axis HARD-PASS): 0.30 (D-axis +0.15 is largest delta; CompGCN path-aware composition is the load-bearing piece; SPECULATIVE).
- Cap on novel-synthesis: 0.50 hard cap respected.

## Cross-thread synthesis

- Prior SHARES_MATH edge-type design drill (32-collision empirical anchor): established the edge type itself; this drill consumes that edge type as input.
- Prior graph-edge-typology drill: established the whitelist; this drill consumes the whitelist as input.
- SHARES_MATH false-merge auditing drill: training-time link-prediction auxiliary task partially mitigates false-merge risk by giving the GNN a chance to learn to ignore spurious equivalences via low cross-component attention.
- VSA position-IS-meaning validation: substrate's HRR encoding already validates position-binding empirically; CompGCN circular-correlation composition is the GNN-layer analogue (NATIVE FIT, not analogy).
- Tier 5 substrate metacognition + self-extracted methodology rules: the GNN training objective can use substrate-self-extracted rules as auxiliary supervision signal (METADATA-anchored learning).

## Substrate-product positioning

- Math-primitive equivalence in message passing is a CATEGORICAL gap for LLMs:
  - LLMs encode token co-occurrence; substrate L4 GNN encodes math-primitive equivalence EXPLICITLY via SHARES_MATH edge type.
  - LLMs cannot represent "atom X and atom Y are mathematically equivalent, propagate gradient symmetrically" without ad-hoc fine-tuning on hand-curated pairs.
  - Substrate connected-component partition over SHARES_MATH is COMPUTED, not learned, and propagated through GNN message passing - this is intelligence-density compression.
- Strategic positioning: substrate L4 GNN with SHARES_MATH = math-primitive intelligence-density representation at the architectural level. This is one of the few capabilities the substrate provides that no LLM architecture can match without explicit graph annotation.

## Honest scope statement

- STRONG: R-GCN / CompGCN / HAN base architecture choice is well-established in literature; substrate's small relation count and homogeneous node-type universe make this a clean application.
- MODERATE: SHARES_MATH equivalence-class message passing semantics (symmetric within-component mean-pool + learned cross-component attention) are well-motivated by community-aware GNN literature but the specific substrate fit is novel synthesis.
- SPECULATIVE: HARD-PASS magnitudes (A >= 0.50, B >= 0.75, D >= 0.65) are based on graph-edge-typology priors deflated by 0.20; the +0.15 D-axis delta is the highest-risk prediction.

## Citations (verified count: 7 generic-literature anchors)

1. Schlichtkrull et al. 2018 - R-GCN.
2. Wang et al. 2019 - HAN.
3. Vashishth et al. 2020 - CompGCN.
4. Hu et al. 2020 - HGT.
5. Zhu et al. 2021 - NBFNet / path-aware GNN.
6. Trouillon et al. 2016 - ComplEx.
7. Sun et al. 2019 - RotatE.

All citations are generic literature; no substrate-specific terms were used in any external query per query-privacy decomposition rule.
