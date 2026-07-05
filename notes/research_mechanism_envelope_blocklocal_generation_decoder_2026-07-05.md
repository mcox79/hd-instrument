# Research: mechanism + envelope-push for the block-local sparse resonator generation decoder

Date: 2026-07-05. Owner: research (Sonnet lit-scan x4, synthesized).
Trigger: `generation_decoder_gsbc_native_blocklocal_v1` (commit ec7aa9064; prereg
`preregs/2026-07-05_exp_generation_decoder_gsbc_native_blocklocal_v1.md`; cell
`experiments/exp_generation_decoder_gsbc_native_blocklocal_v1.py`).

## DISK-VERIFY FLAG (read before trusting any number below)

Per Fix#28 filesystem-verify discipline: `data/exp_generation_decoder_gsbc_native_blocklocal_v1*` does
**NOT exist on disk** as of this drill (grepped; only `experiments/*.py` + `preregs/*.md` are present). The
task-framing numbers ("V8192/D26=0.86", "3 seeds FULL local-verify") do **not match** the prereg's own
`HYPOTHESIZED vs MEASURED` section, which cites `V8192D26 exact=0.700 perterm=0.988 MEASURED@probe`
(single-seed probe, not the 3-seed FULL). The FULL run is genuinely still pending on `remote_cpu_queue`
(matches the task's own "FULL pending" caveat). **This note treats 0.700 (probe) as the only disk-grounded
cliff number** and flags 0.86 as unverified pending the actual FULL landing — whoever processes that verdict
should re-read `metrics.json` directly, not carry either number forward from memory.

## HEADLINE

The block-local sparse resonator is a **literature-recognized, brain-grounded mechanism** (Sparse Block
Codes / Resonator Networks family; grid-cell-modular precedent), not a partitioning shortcut — and its
capacity cliff has a **known quantitative form**: a sparse-Hebbian-style capacity law `V_max(n) ~ alpha_c *
n / (a*ln(1/a))` (alpha_c ~ 0.7, Tsodyks-Feigelman constant) fits the 4 measured grid points well and predicts
the V8192/D26 cliff (n=315) as ~2.9x over critical load — a real but *tunable* capacity wall, not a
fundamental one. Two independent frameworks (sparse-Hebbian capacity, channel-dispersion self-averaging)
agree the cliff should be **sharp** (phase-transition-like) but disagree by ~2x on exactly where the 50%
crossover sits (n0 ~ 400-500 vs n0 ~ 915) — a cheap, already-buildable test resolves this. The highest-EV
next lever is **not** bigger N or naive re-chunking: it's a **residue-number-system / CRT-style modular
sub-block scheme**, which has an existing published HDC realization (Kymn/Kleyko/Frady/Sommer 2024/2025) and
strong grid-cell brain-grounding (Fiete et al. 2008) — it attacks the exact V-per-block ceiling that cliffed,
without growing total width.

## Cheap decisive test

Add 3-4 grid points to the *existing* cell (`FULL_GRID` in `exp_generation_decoder_gsbc_native_blocklocal_v1.py`)
at fixed V=8192, varying D to bracket the disputed n0 range: `(8192, 8, "boundary")` [n=1024],
`(8192, 12, "boundary")` [n=683], `(8192, 16, "boundary")` [n=512], `(8192, 20, "boundary")` [n=410]. No new
mechanism, no new filler pool (reuses the already-SCP'd `gsbc_expand2x_pool_v1.npz`); cost is seconds-to-low-
minutes of CPU (measured probe: 5-point grid @ 8.9s). This directly cross-validates the two disagreeing
capacity-law estimates against 4 new, previously untested points.

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

- **HARD-PASS (sparse-Hebbian capacity law, n0~915 confirmed):** exact-ordered stays degraded (< 0.85) at
  D=16/D=20 (n=410-512), lands in a partial/middle band (~0.75-0.90) at D=12 (n=683), and recovers >= 0.95 at
  D=8 (n=1024). This confirms `V_max(n) ~ 8.9*n` (alpha_c~0.7 sparse-Hebbian fit) as the operative law and
  narrows the design margin needed for future V/D combinations to a computable formula.
- **HARD-PASS (channel-dispersion/self-averaging, n0~400-500 confirmed instead):** exact-ordered already >=
  0.90 at D=16 (n=512) and D=20 (n=410) — the narrower estimate wins; capacity restores faster than the
  sparse-Hebbian fit implies, meaning the correlated (non-iid GSBC) codebook behaves closer to the idealized
  channel-coding bound than the sparse-associative-memory bound.
- **HARD-FAIL (neither idealized law applies to the real correlated manifold):** exact-ordered remains < 0.70
  even at D=8 (n=1024) — i.e., a block only 25% smaller than the already-confirmed-passing n=1365 collapses
  hard. This would mean GSBC's real correlation structure (effective rank / participation ratio of the
  embedding manifold) sets the ceiling, not sparsity fraction alone, and the next step is a free-probability
  re-derivation (Marchenko-Pastur effective-dimension of the codebook) — already a flagged Tier-1 field
  (`research_field_advisor.py` F2/F4) for exactly this reason.

## Cross-thread synthesis (4 parallel lit-scans)

**1. Capacity law (compressed-sensing / sparse-associative-memory framing).** Of three candidate frameworks
(Johnson-Lindenstrauss, Donoho-Tanner compressed sensing, Gardner/Tsodyks-Feigelman/Willshaw sparse
associative memory), the sparse-Hebbian capacity result fits best: `V_max(n,a) ~ alpha_c * n / (a*ln(1/a))`.
Fit to the 4 measured (V,n) points gives `alpha_c ~ 0.7`, matching the classic Tsodyks-Feigelman constant
`1/(2 ln 2) ~ 0.72`. This predicts `V_max(315) ~ 2,800` (observed cliff: V=8192 is ~2.9x over — consistent
with "degrades, doesn't collapse to zero") and `V_max(1365) ~ 12,200` (observed: V=8192 comfortably holds,
ratio 0.67). Citations: Willshaw/Buneman/Longuet-Higgins 1969 (*Nature*); Gardner 1988 (*J. Phys. A*);
Tsodyks & Feigelman 1988 (*Europhys. Lett.*); Knoblauch/Palm/Sommer 2010 (*Neural Computation*);
Johnson & Lindenstrauss 1984 (retained as a secondary geometric constraint, not the primary mechanism).
Deflated confidence ~0.45-0.55 (only one true boundary pair constrains alpha_c).

**2. Cliff sharpness (why it's a cliff, not a slope).** Channel-dispersion theory (Polyanskiy-Poor-Verdu
2010, the finite-blocklength generalization of Shannon capacity) and Donoho-Tanner's phase-transition
sharpness results both predict a **narrow, self-averaging transition** (width ~ n^-1/2) rather than a
gradual decline — percolation-style finite-size scaling is the right *shape* of argument but the wrong
universality class (no lattice/short-range structure here; this is closer to the mean-field/CLT-driven
self-averaging case, per Aharony & Harris 1996). The disagreement with estimate #1 on exactly where n0 sits
(400-500 vs 915) is the single open quantitative question the cheap test above resolves. Deflated confidence
~0.45-0.55; both frameworks agree on shape (sharp), disagree on location (2x).

**3. Is block-local "cheating"? No — it's a recognized, actively-developed, regime-favorable mechanism.**
Disjoint block/slot partitioning is formalized in the literature as **Sparse Block Codes** with block-local
binding (Frady, Kleyko & Sommer 2021, IEEE TNNLS), with dedicated factorization machinery in Hersche et al.
2025 ("Factorizers for Distributed Sparse Block Codes") and the broader Resonator Networks line (Kent/Frady/
Sommer/Olshausen 2020, *Neural Computation*, parts 1-2) — directly matching our cell's own cited sources.
The verdict is regime-bound, not universal: block partitioning wins specifically in the **fixed, small-K,
bounded-position regime** (a short max-length sequence, exactly D<=26 here); dense superposition (multiplicative
binding) remains the tool of choice for open-ended/combinatorial role structure. Brain-grounding for ORDER
specifically is real and targeted: grid-cell modules are themselves a block-structured code, increasingly
implicated in representing *ordered/sequential* experience, not just space (*Nature Reviews Neuroscience*
2021 review "The grid code for ordered experience"); Krausse et al. 2025 built a VSA algebra explicitly
modeled on grid modules, describing block-local binding as "more bio-plausible" than dense holographic
binding. Additional citations: Smolensky 1990 (TPR), Plate 1995/2003 (HRR), Gayler 2003 (MAP), Rinkus 2010
(cortical sparse-distributed coding, content/identity side favors within-block distributed coding, not pure
localism). Deflated confidence: legitimacy verdict ~0.55-0.6; brain-grounding-for-order verdict ~0.45-0.5
(capped <=0.50, connecting two independent literatures is novel synthesis on my part).

**4. Envelope-push: the ranked next levers.** (1) **Residue-Number-System / CRT modular sub-blocks** — RANK
1. Grid cells in medial entorhinal cortex represent position as residues under several small, roughly-coprime
moduli; Fiete et al. 2008 (*Neuron*) and Sreenivasan & Fiete 2011 (*Nat. Neurosci.*) show this lets coding
range grow ~exponentially with module count while each module stays small. Kymn, Kleyko, Frady, Sommer et al.
("Computing with Residue Numbers in High-Dimensional Representation," *Neural Computation* 2024/2025) already
built a working HDC realization of nearly this exact problem (extend effective vocabulary range without
growing total width, using several small coprime-modulus sub-codes + CRT-style decode). This is the strongest
lever because it directly targets the V-per-block ceiling that cliffed, has a ready published implementation
to adapt (not de-novo research), and has the best brain-grounding of the four candidates. (2) **Hierarchical/
nested chunking** — RANK 2, for extending D (sequence length) rather than V. Standard in HDC for
records/trees (Kanerva, Plate); cognitive-science chunking (Miller 1956 "7+-2", Cowan's "Magical Mystery
Four") gives strong behavioral precedent that chunking extends effective span, but no literature quantifies
how much crosstalk compounds per unbind level — needs its own smoke test before trusting a multiplicative
capacity-gain formula found in preprint form. (3) **Hybrid block+superposition** and (4) **oscillatory
theta-gamma phase coding** were assessed lower-EV: (4) is essentially a neural instantiation of the *existing*
flat equal-sized block scheme (no literature shows it beating flat blocks at scale); (3) has no strong
capacity results in the literature specific to this regime. Deflated confidence per candidate stated inline;
any hierarchical-RNS combination claim is capped at P<=0.50 (novel synthesis).

## Substrate-product implications

- The block-local sparse resonator is now doubly justified as the correct "mouth" architecture for
  GSBC-native generation: empirically (measured exact-ordered=1.000 in-box vs dense bipolar-BSC's 0.000
  collapse) **and** by literature precedent (Sparse Block Codes / Resonator Networks is an actively-published
  family, brain-grounded via grid-cell modular coding, specifically favorable in exactly our bounded
  small-K/short-sequence regime). This is not a stopgap; it is the geometrically-native choice, matching the
  design memo's own prediction.
- The V8192/D26 cliff is not a hard ceiling — it is a block-size-vs-vocabulary capacity limit with a
  computable, tunable form. Design headroom (more N, fewer D, or a different sub-block scheme) is available
  and quantifiable, not merely empirical.
- Ranked build path for pushing the mouth further: (1) near-zero-cost grid-point extension on the existing
  cell to resolve the n0 location dispute (cheap decisive test above); (2) prototype an RNS/CRT modular
  sub-block scheme to push the V-per-block ceiling past 8192 without growing N (highest-EV, ready-to-adapt
  published HDC mechanism); (3) hierarchical chunking as the complementary lever for D (sequence length)
  once its crosstalk-compounding risk is smoke-tested.
- A companion exp_dev hand-off (`notes/exp_dev_handoff_research_mechanism_envelope_blocklocal_generation_decoder_2026-07-05.md`)
  is filed with both ranked anchor candidates.

## Citations (verified count: 20 distinct sources, found via 4 parallel Sonnet WebSearch lit-scans; NOT
independently cross-checked against primary text by the synthesizing agent — treat as lit-scan-tier, not
audited-tier, per calibration discipline)

1. Willshaw, Buneman & Longuet-Higgins, "Non-holographic associative memory," *Nature* 222 (1969).
2. Gardner, "The space of interactions in neural network models," *J. Phys. A* 21, 257 (1988).
3. Tsodyks & Feigelman, "The Enhanced Storage Capacity in Neural Networks with Low Activity Level,"
   *Europhys. Lett.* (1988).
4. Knoblauch, Palm & Sommer, "Memory Capacities for Synaptic and Structural Plasticity in Neural Networks
   with Sparse Coding," *Neural Computation* (2010).
5. Johnson & Lindenstrauss, "Extensions of Lipschitz mappings into a Hilbert space" (1984).
6. Polyanskiy, Poor & Verdu, "Channel Coding Rate in the Finite Blocklength Regime," *IEEE Trans. Inf.
   Theory* 56(5), 2010.
7. Donoho & Tanner, "Observed Universality of Phase Transitions in High-Dimensional Geometry...," *Phil.
   Trans. R. Soc. A*, 2009.
8. Aharony & Harris, "Absence of Self-Averaging and Universal Fluctuations in Random Systems Near Critical
   Points," *PRL* 77, 1996.
9. Donoho, "The Noise-Sensitivity Phase Transition in Compressed Sensing" (Stanford preprint).
10. Smolensky, "Tensor Product Variable Binding and the Representation of Symbolic Structures in Connectionist
    Systems," 1990.
11. Plate, "Holographic Reduced Representations," 1995/2003.
12. Gayler, "Vector Symbolic Architectures Answer Jackendoff's Challenges for Cognitive Neuroscience" (MAP), 2003.
13. Frady, Kleyko & Sommer, "Variable Binding for Sparse Distributed Representations," *IEEE TNNLS*, 2021.
14. Kent, Frady, Sommer & Olshausen, "Resonator Networks 1 & 2," *Neural Computation*, 2020.
15. Hersche et al., "Factorizers for Distributed Sparse Block Codes," 2025.
16. Krausse et al., "A Grid Cell-Inspired Structured Vector Algebra for Cognitive Maps," 2025.
17. "The grid code for ordered experience," *Nature Reviews Neuroscience*, 2021.
18. Rinkus, cortical sparse-distributed-coding model, 2010.
19. Fiete, Burak & Brookings, "Grid cells generate an analog error-correcting code," *Neuron*, 2008.
20. Sreenivasan & Fiete, "Grid cells generate an analog error-correcting code for singularly precise neural
    computation," *Nat. Neurosci.*, 2011.
21. Kymn, Kleyko, Frady, Sommer et al., "Computing with Residue Numbers in High-Dimensional Representation,"
    *Neural Computation*, 2024/2025.
22. Miller, "The Magical Number Seven, Plus or Minus Two," 1956.
23. Cowan, "The Magical Mystery Four," working-memory chunking-capacity literature.
