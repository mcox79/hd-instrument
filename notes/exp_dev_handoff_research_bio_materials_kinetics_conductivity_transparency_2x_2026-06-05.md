# exp_dev hand-off -- research: bio_materials_kinetics_conductivity_transparency_2x

Filed-by: research sub-agent
Date: 2026-06-05
Trigger: notes/research_drill_bio_materials_kinetics_conductivity_transparency_2x_2026-06-05.md
Pause state: check data/orchestrator_paused.flag before dispatching

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchor candidates and WHY, not how to implement them. Exp_dev designs the anchors autonomously.

---

## Anchor candidates (rank-ordered)

### Rank 1: Matthiessen dominant-scatterer diagnosis
- Anchor pointer: V2-Cell 2 in research note
- Substrate-product reading: Matthiessen's rule decomposition of retrieval error into additive channels (write-crosstalk, noise, index-collision). Identifies WHICH channel dominates at each operating point (M/N, sigma_noise). Directly informs which optimization is worth doing. No new mechanism -- pure diagnostic.
- Tier hint: CPU, smoke-level, wall < 90 s at N=4096
- Why now: highest-actionability cell; determines where to direct all subsequent Phase 4 optimization work; needed BEFORE any of the other V2 cells to avoid optimizing the wrong scattering channel

### Rank 2: Hadamard ETF codebook initialization vs random Rademacher
- Anchor pointer: V2-Cell 1 in research note (also ARCH-1 in architecture changes)
- Substrate-product reading: ETF/Hadamard init minimizes maximum pairwise cross-correlation (Welch bound), reducing retrieval activation barrier. Zero-architecture-change, just initialization. Product-ships independently.
- Tier hint: CPU, smoke-level, wall < 60 s at N=4096, M/N = 0.10/0.20/0.30
- Why now: cheapest cell with clean algebraic prediction; if delta_accuracy < 0.03 at M/N=0.20, abandon codebook geometry axis; if >= 0.10, codebook init is a free lunch

### Rank 3: Allosteric write gate (G register, frequency-weighted write)
- Anchor pointer: V2-Cell 3 in research note (also ARCH-3)
- Substrate-product reading: write amplification lambda_i = 1/sqrt(p_i) for rare facts. Simulates LLM partner signaling "this is important." Directly improves rare-fact retrieval accuracy.
- Tier hint: CPU, wall < 30 s at N=4096
- Why now: highest user-visible product value (explicit memory prioritization); depends on Matthiessen diagnosis confirming write-crosstalk is dominant channel (else lambda_i weighting hits the wrong scattering term)

### Rank 4: Rotation cert channel (Hadamard W_cert)
- Anchor pointer: V2-Cell 4 in research note (also ARCH-2 partial)
- Substrate-product reading: W_cert = H W H^T via Hadamard rotation separates cert audit reads from write-crosstalk subspace. Cert reliability curve decouples from load-dependent retrieval curve.
- Tier hint: CPU, wall < 60 s at N=4096, M=512
- Why now: cert channel is a structural moat; if rotation cert reduces cert error slope by >= 30%, it is a product-differentiated audit path that ships before full W_scaffold frozen architecture

### Rank 5: Dense local codebook packing vs ETF for cert-style reads
- Anchor pointer: V2-Cell 5 in research note
- Substrate-product reading: for cert queries (small epsilon noise, exact pattern match), corneal-analog dense packing may outperform ETF max-separation. Most surprising / uncertain finding; deserves empirical test.
- Tier hint: CPU, wall < 60 s at N=4096
- Why now: lowest P_deflated (0.23) but highest surprise value; if confirmed, overturns standard codebook design principle for cert channels

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_bio_materials_kinetics_conductivity_transparency_2x_2026-06-05.md
- Cap map: d:/AI/hd-instrument/notes/substrate_capability_map.md
- Priorities: most recent d:/AI/hd-instrument/notes/priorities_*.md
- Active protocols: d:/AI/hd-instrument/notes/active_protocols.md

---

## Contract

Exp_dev autonomously designs anchor names, sweep grids, threshold formulas, queue assignments, and pre-reg bands. This file provides TASK + WHY + CONTRACT only.

## Autonomy declaration

Exp_dev chooses: (a) which subset of the 5 ranked anchors to ship in this cycle, (b) exact N/M/V_c grid, (c) pre-reg HP/MID/HF bands, (d) queue assignment (laptop CPU vs remote CPU), (e) timeout formula per [[feedback-per-experiment-timeout-required]]. Orchestrator does not pre-commit cap_map decisions.
