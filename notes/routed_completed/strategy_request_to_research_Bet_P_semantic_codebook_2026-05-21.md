# Strategy → Research: Bet P (semantic-locality codebook) — NEW multi-hop rescue axis

**Sender**: Strategy session (session 1)
**Recipient**: Research session
**Date**: 2026-05-21 ~15:48 EDT
**Topic**: User-proposed NEW multi-hop rescue mechanism (cycle 45 followup) — semantic-locality codebook construction

## What the user proposed

"For multihop — why couldn't related items be arranged in similar
directions? Since there's basically unlimited dimensions, couldn't
they be arranged in this fashion?"

## Strategy analysis

This is a **NEW mechanism axis** (codebook geometry) distinct from the
R8 list and Bet N/O. Every prior rescue kept the **random-codebook
assumption** and modified binding (Hadamard/FHRR/hybrid), cleanup
(Modern Hopfield, soft cleanup, adaptive-β), or storage (Cooper-pair).
This axis modifies the codebook itself.

### Mechanism (working name: Bet P)

Construct codebook so that **semantically-related items have high
pairwise cosine similarity**, while items in different "topics" remain
near-orthogonal. Concretely:

- N=4096 split into N/k orthogonal super-clusters (each k-dim subspace)
- Within each super-cluster, related items cluster in semantic similarity
- Chained reasoning within a super-cluster benefits from per-hop
  locality (cleanup at each hop has smaller displacement to resolve)
- Cross-super-cluster relations remain near-orthogonal (preserves
  substrate capacity at cluster granularity)

### Why this might work

1. **Per-hop noise accumulates less**: if cos(a, b) = 0.9 instead of
   cos(a, b) ≈ 0, then b is "closer" to a in substrate geometry. Each
   cleanup operation has smaller uncertainty range. Compounds less
   over 50 hops.
2. **Substrate-physics anchor (load-bearing per
   [[feedback-materials-science-probe]])**: ferromagnetic domain
   organization IS this geometry. Within domain: aligned spins (local
   similarity). Cross domain: misaligned (orthogonality). R29 already
   established substrate is in modern-Hopfield-rescue regime above
   α_c. Adding domain structure to codebook is the natural extension.
3. **External lit prior art is robust**: knowledge-graph embeddings
   (TransE, RotatE, ComplEx), word2vec / GloVe semantic clusters,
   topographic cortical maps, hyperbolic embeddings (Poincaré). All
   demonstrate semantic locality + sparse-orthogonal organization at
   different scales.
4. **Buildable at current architecture**: no V2 substrate needed.
   Construct codewords differently and substrate's existing pipeline
   handles them.

### Brutal-honesty tradeoffs per [[feedback-no-smoke]]

- Substrate's M/N=8 capacity (Bet C) was derived under
  near-orthogonal codebooks. Clustering related items reduces
  effective orthogonality → capacity bound likely DROPS. Quantitative
  question: by how much?
- Cross-talk among clustered items goes UP (the price of locality).
  Substrate's multi-probe robustness (Mirage probes) might degrade
  for within-cluster items.
- Requires knowing chain structure at codebook-construction time.
  For statically-known fact bases this is fine; for runtime-discovered
  chains it requires re-clustering (online structure-learning).
- The capacity-vs-locality tradeoff is real; finding the right
  hierarchical structure is non-trivial.

### Probability estimates (per [[feedback-no-smoke]])

- P(beats FHRR 0.22 floor at d=50 for chained items): 40-55%
- P(beats FHRR floor while preserving Bet C capacity within 20%): 25-35%
- P(produces substrate-novel mechanism understanding): 60% (regardless
  of beating FHRR, the geometry-of-codebook framing IS substrate-novel)
- P(mechanism is captured/dominated by existing knowledge-graph-embedding
  techniques rather than substrate-novel): 35%

## Per PROT-004 + [[feedback-rehabilitation-after-rejection]]: 5 axis-combination rescue sketches (DRAFT — Research vets in 2x deep pass)

Strategy DRAFT only; Research's Pass 2 expected to GENERATE the rescue
list per [[feedback-unbiased-research]].

### Sketch 1 — Hierarchical orthogonal-cluster codebook
N=4096 split into N/k orthogonal super-clusters. Within each cluster
use semantic-locality codewords (related items closer). Substrate-
physics: ferromagnetic domains (R29 anchor).

### Sketch 2 — Knowledge-graph-embedding initialization (TransE / RotatE)
Initialize codewords via knowledge-graph training on the fact base
(predict h + r ≈ t in TransE; or rotation form in RotatE). Substrate
inherits the learned semantic geometry. May combine with FHRR
(continuous-rotation binding) naturally.

### Sketch 3 — Continuous-geodesic codebook (manifold embedding)
Embed facts on a continuous manifold (sphere, hyperbolic ball, torus)
such that geodesic distance reflects semantic similarity. Substrate-
physics: Riemannian structure on bundle space.

### Sketch 4 — Magnon-coupled codebook (extends R32)
Codewords constructed as standing-wave modes of a substrate-Hamiltonian
with locally-aligned spin-spin couplings. Substrate-physics:
spin-wave / magnon dynamics R29/R32 framework.

### Sketch 5 — Hyperbolic-tree codebook (Poincaré embedding)
Hierarchical concept tree embedded in hyperbolic space; chained
inference traverses tree branches. Each hop is a tree-branch step,
not a random-direction step. Substrate-physics: hyperbolic-tiling
proximity to R34 V2 substrate.

## What Research should produce

Per [[feedback-unbiased-research]] + [[project-research-playbook]] item 9:

1. **Pass 1 (external lit-scan, broad)**:
   - Knowledge-graph embedding (TransE, RotatE, ComplEx, RESCAL, DistMult)
   - Manifold learning (LLE, IsoMap, t-SNE, UMAP)
   - Hyperbolic embedding (Poincaré, Nickel-Kiela 2017, hyperbolic
     attention)
   - Word embeddings semantic-cluster structure (word2vec, GloVe)
   - Topographic cortical-column models
   - Vector quantization with semantic-aware codebooks
2. **Pass 2 (substrate drill)**:
   - Which mechanism transfers cleanly to BSC ±1 substrate?
   - What is the capacity tradeoff for structured codebook vs Bet C
     near-orthogonal Kerdock M/N=8 bound?
   - Does R29 ferromagnetic-domain structure give a substrate-physics-
     load-bearing mechanism for Sketch 1?
   - Probability estimates per [[feedback-no-smoke]]
3. **Output format**: research note enumerating actual mechanisms with
   substrate-compatible variants; honest-negative tagging if family
   closes.

## Sequencing recommendation

This is the FIRST substrate-novel multi-hop rescue axis that emerged
WITHOUT direct R8/META/R17 enumeration. Promote to **HIGH PRIORITY**.

Priority order suggestion:
1. **Bet P (this; codebook geometry) — HIGH priority**, new substrate-
   novel axis
2. R33 quantum-repeater (temporal EC; existing priority)
3. Bet N / Bet O rehab (closure-followup; lower urgency)
4. R31 soliton, R32 magnon (research backlog)

Bet P and R32 magnon may combine in Sketch 4; Bet P and R34 V2 may
combine in Sketch 5. Research's Pass 2 should articulate where Bet P
is independent vs where it complements other rescues.

## Cross-references

- `notes/substrate_capability_map.md` v64 (incoming) for Bet P promotion
- `notes/research_R29_ferromagnetism_domains_2026-05-21.md` (anchor)
- `notes/research_R17_holographic_principle_2026-05-21.md` (R34 V2 connection)
- This file (request log)

## What you need from me

Nothing — the user's prompt is the spec. Sketches above are starting
points only. Research's Pass 2 should generate the rescue mechanism
list independently per [[feedback-unbiased-research]].

---
BULK-ARCHIVED 2026-06-01: Pre-2026-05-25 backlog; predates routed_completed discipline; bulk-archived per `notes/routed_completed/strategy_request_to_strategy_research_inbox_backlog_triage_2026-06-01.md` Path A. Cap_map v312 reflects the evidence of acted-on work.
