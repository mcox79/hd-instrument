# RESEARCH (Director) -> USER + Skunkworks: online drills DONE during freeze. (1) KG benchmark held-out protocols + (2) HDC/FHRR 2024-2025 reasoning literature. Both READ-ONLY web research; substantive findings consumable when freeze lifts. Key actionables below.

(Filename has to_USER per refined cap.)

## Drill 1: KG benchmark held-out protocols (for ConceptNet eval design)

**Key actionables for the ConceptNet Track-B pilot eval cell:**

1. **Transitive closure filtering is load-bearing** — the leakage we most need to prevent. If A is_a B and B is_a C, asking "A is_a C?" leaks unless transitive closure is filtered. The substrate's existing HYPERNYM/PART_OF held-out cert atoms (Item-1 PART_OF + M1 HYPERNYM + HYP-5) used this discipline; ConceptNet eval needs the same. The CommonSense->DomainSense distillation work formalizes this for ConceptNet specifically.

2. **Leakage-free chronological splits** are the modern protocol — split edges by publication date, NOT random. Temporal cross-validation (5-fold). Symmetric-edge co-assignment guards against the symmetry-via-co-occurrence leak.

3. **Filtered metrics standard:** MRR + Hits@{1,3,10} + AUROC. Filtering = remove other true positives from the ranked candidate list before scoring (so a model isn't penalized for ranking ANOTHER correct answer above the held-out one). The substrate's existing AUROC-based eval (A2 v6: 0.9628) maps cleanly to this.

4. **Baseline candidates:** random KG completion + nearest-neighbor + frozen embedding (bge). The substrate's existing bge-cosine separates gap from in-cov at AUROC 0.9628 (A2 v6) — that's the "frozen embedding" baseline. ConceptNet eval should compare against AT LEAST this.

**Pre-reg implication:** ConceptNet capability eval should pre-register: (a) filtered MRR + Hits@10 + AUROC as primary metrics; (b) transitive closure filtering applied to held-out set; (c) chronological split (not random); (d) baselines = frozen-bge + nearest-neighbor on the bounded-v1 set.

## Drill 2: HDC/FHRR 2024-2025 reasoning literature (for cap-int proven-bound discipline)

**Three papers directly relevant to the substrate's positioning + ConceptNet eval:**

1. **HDReason (2024)** — algorithm+hardware codesign for HDC knowledge graph reasoning. This is the PRIOR ART for what the substrate is doing. Likely the natural cite-baseline for any KG cert claim. Worth a deep-read pre-ConceptNet-dispatch.

2. **Hyperdimensional representation learning for node classification + link prediction (WSDM 2025)** — DIRECT competition for the substrate's KG capability. If their results are at our cert-grade, we cite as the established baseline. If we beat them at the held-out + transitive-closure-filtered protocol, that's the cert-grade claim.

3. **ConformalHDC (uncertainty-aware HDC, 2025)** — relevant to the substrate's cert-architecture. Conformal prediction provides probabilistic guarantees on HDC predictions. Worth surfacing whether the substrate's refuse-gate (A2 v6) is doing something kindred OR distinct.

**Strategic implication:** the substrate is NOT operating in a vacuum — HDC + KG reasoning is an active 2024-2025 research area. The substrate's distinctive contribution = **the cert-architecture on top** (not the HDC math underneath; that's well-established). Position cap-int outputs accordingly: "X capability at cert-grade with honest-scoped bound" is the substrate's value-add over the HDC baseline papers.

## Two cross-cutting observations

**1. The substrate's "honest-scoped proven bound" discipline composes the KG protocol literature.** The Item-1/M1/HYP-5 cert-arc (FACT-FABRICATION bound on held-out edges) IS the transitive-closure-filtered held-out test the KG-benchmark literature recommends. We can position this in any paper / writeup as "the substrate applies the leakage-free split protocol with honest-scope discipline."

**2. The ConceptNet eval design should explicitly cite + compare against HDReason + WSDM-2025 HDC rep learning.** Not for adversarial reasons — the substrate's contribution is the cert-architecture layer, not the HDC encoding. Comparing transparently positions the substrate honestly + makes the cert claim defensible.

## What this changes in the 20h plan

- **Track-B pilot (ConceptNet eval)** — incorporate transitive closure filtering + chronological split + filtered metrics + the 2 baseline papers as comparators. This is what Skunkworks's SCHEMA-VET would have demanded; pre-staging it makes the pilot cert-VET likely-PASS.
- **Strategic positioning** — the substrate's product story has cleaner edges now (HDC math + cert-architecture; the cert-architecture is the distinctive layer; HDC baselines are well-known + we cite them).
- **No change to** Track-A completion + atomizer refactor primary paths.

## Routing
- **USER:** these drills surface useful pre-launch input; consumable post-lift. The ConceptNet eval design pre-reg will benefit from drill 1's protocols; the substrate-positioning gains clarity from drill 2's competition map.
- **Skunkworks:** at-bandwidth review for the eval pre-reg + the positioning observations.
- **Me:** standing on freeze; these are the only research outputs filed.

## Sources

- [CommonSense to DomainSense: Distilling Commonsense Reasoning to Domain-specific Knowledge Graphs (2025)](https://dl.acm.org/doi/10.1145/3731443.3771360)
- [THOR: Inductive Link Prediction over Hyper-Relational Knowledge Graphs](https://arxiv.org/pdf/2602.05424)
- [ConceptNet 5.5: An Open Multilingual Graph of General Knowledge](https://arxiv.org/abs/1612.03975)
- [Knowledge graphs for empirical concept retrieval](https://arxiv.org/pdf/2404.07008)
- [Hyperdimensional representation learning for node classification + link prediction (WSDM 2025)](https://arxiv.org/pdf/2506.09282)
- [MissionHD: Hyperdimensional Refinement of Distribution-Deficient Reasoning Graphs (2025)](https://arxiv.org/pdf/2508.14746)
- [ConformalHDC: Uncertainty-Aware Hyperdimensional Computing (2025)](https://arxiv.org/pdf/2602.21446)
- [Hyperdimensional Computing with Holographic and Adaptive Encoder (Frontiers 2024)](https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2024.1371988/full)
- [Cross-Layer Design of Vector-Symbolic Computing (2025)](https://arxiv.org/pdf/2508.14245)
- [Efficient Hyperdimensional Computing with Modular Composite Representations (2025)](https://arxiv.org/pdf/2511.09708)

-- Research (Director)
