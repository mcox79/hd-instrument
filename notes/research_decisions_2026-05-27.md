# Research decisions — 2026-05-27

- novel_phase_class_methodology DEEP DRILL closure → `notes/research_novel_phase_class_methodology_2026-05-27.md` — Substrate has rejected 5 standard phase-class labels (1-RSB, AGS-RS-multi-ferromagnet, cluster-glass, RD-terrace, unified-SVD-cascade). Lit-scan finds 2024-2026 documented class **"gated multistable AM / lR-phase"** matches 4 of 5 empirical signatures (discrete plateaus + first-order hysteresis + multi-basin without ergodicity break + asymmetric weights + structured codebook). P(DOCUMENTED-BUT-UNTESTED, gated multistable AM with Kerdock + asymmetric Hebbian sub-ingredients = SKAH-M sub-class) = **0.48** (modal). P(genuinely NOVEL phase class requiring multi-year community precedent) = **0.22** (deflated; novel-synthesis cap 0.50 not breached). P(FINITE-N artifact, dissolves at N→∞) = **0.30**. 5-step methodology gates pre-registered (symmetry-breaking pattern, order-parameter manifold, Goldstone modes, free-energy fingerprint, response-function structure). 6-cell positive-identifier battery designed as decisive test (~3-4h GPU OR ~8-10h remote CPU): C1 q_EA(N), C2 plateau-N-scaling, C3 Goldstone absence, C4 hysteresis-area-scaling, C5 non-local disorder operator, C6 free-energy 3-well structure. Joint outcome → class call (≥5/6 documented = DOCUMENTED ship; ≥4/6 novel + anomaly = NOVEL declare SKAH-M; ≥4/6 finite-N = artifact, cap product at N=1024). Killer-feature roadmap UNAFFECTED by class call (deletion certificate / per-fact retention / etc. ship regardless). Companion handoff: `notes/exp_dev_handoff_novel_phase_class_battery_2026-05-27.md`.
- 2026-05-27 corpus-size scaling drill (R26 weakest-assumption followup): HEADLINE P(path-b) revised DOWN from 0.45 to 0.35. Two-stage bottleneck: (1) tau-limit -- Hebbian W accumulates interference when M_stored > alpha_c*N; at N=4096 threshold crossed at ~100MB-1GB corpus per Heaps law + PPMI sparsity analysis; (2) PPMI vocabulary saturation at ~1-10B tokens is FAVORABLE (atomic diversity saturates, substrate need not scale to 100B tokens). Coupled N+corpus finding: substrate at N=65536 trained on 10GB corpus keeps M_stored within capacity with ~1.2x margin; N=131072 recommended for robust 10GB target. Closest published analog: kNN-LM trillion-token datastore (Shi et al. 2024) shows log-linear perplexity scaling -- upper bound for substrate. Chinchilla analog predicts ~10B tokens as compute-optimal corpus for N=65536. Cheapest falsifier: 3-corpus-size CPU probe at fixed N; HARD-PASS=monotone bpc + no whitening onset; HARD-FAIL=bpc stagnates + W top-edge ratio < 1.5. Note: notes/research_corpus_size_scaling_2026-05-27.md. Companion handoff: notes/exp_dev_handoff_corpus_size_scaling_probe_2026-05-27.md.
## MoE learned-router architectures drill -- 2026-05-27

Trigger: v220 K_perarm M2_DOMINANT -- LSH gating entropy sole K-scaling degradation source.

Delivered: notes/research_moe_learned_router_2026-05-27.md

RECOMMENDED ARCHITECTURE: Expert-Choice cosine-dot routing with random or Hebbian-bundle per-expert anchors.

P(rescue lifts K-scaling ceiling) = 0.45 (deflated 0.15 from raw 0.60; calibration penalty for substrate-specific BSC bipolar regime; direct lit-precedent from Expert-Choice NeurIPS 2022 + ReMoE ICLR 2025 + Cosine-Anchor SRA arXiv 2509.14255 justifies lower deflation vs pure novel-synthesis).

RULED OUT for substrate: Soft MoE (destroys auditability), DirMoE/Bingham (high engineering cost + no BSC fit), hash routing (content-independent = same entropy problem), Switch/GShard W_gate (expensive training, no semantic anchor).

COMPATIBLE: Expert-Choice cosine-dot (best), ReMoE ReLU-on-cosine (second), cosine-anchor top-k (third).

Companion handoff: notes/exp_dev_handoff_moe_learned_router_probe_2026-05-27.md
Cheapest probe: swap LSH for cosine-dot in K_perarm sweep; 3 seeds; K={4,8,16,32}; ~2500s CPU.
## Persistent homology / TDA orthogonal-lens drill -- 2026-05-27

Trigger: substrate rejected all standard phase-class labels; SKAH-M battery v1 MIDDLE_BAND; orchestrator requested orthogonal lens to check whether substrate W has meaningful topological invariants explaining multi-basin discrete structure WITHOUT phase-class framework.

Delivered: notes/research_persistent_homology_substrate_2026-05-27.md

DISPATCH CALL: OVERLAPPING (with one ORTHOGONAL sub-question). TDA is not a wholly orthogonal framework; it is a re-axiomatization of the same observables (spectrum, connectivity, multistability) through filtration index tau. The persistent-spectral-graph theorem (Wang-Nguyen-Wei 2020) shows persistent Laplacian harmonic 0-eigenvalues recover the persistence barcode, making TDA isomorphic to spectral graph theory at the harmonic level. **Pattern 4 Tier-3 "DO NOT drill algebraic-topo" closure was overly broad** -- it was for infinite-dim operator-algebraic frameworks (Connes-Kreimer / Tomita-Takesaki / Steenrod); finite-dim point-cloud TDA is structurally identical to free-prob sample-covariance (Bet I survivor).

P assignments (deflated):
- P(TDA-C SHIFT-vs-PARTITION agrees with free-additive on >=4/5 cases, ships as 4th MoE diagnostic) = **0.38** (load-bearing finding)
- P(TDA reveals novel substrate fingerprint via b_1 cycle structure + plateau-trajectory persistence) = **0.10** (joint, deflated)
- P(TDA confirms but adds no novelty -- redundant with spectral gap) = **0.32**
- P(TDA inconclusive / disagrees with established diagnostics) = **0.20**
- P(overall NEW predictive content beyond SKAH-M / phase-class) = **0.30**

Cheapest falsifier: 5-probe re-analysis on existing W artifacts (TDA-A b_0-trajectory, TDA-B Kerdock-vs-random b_1 ratio, TDA-C MoE SHIFT/PARTITION b_0-plateau width, TDA-D long-bar count vs plateau count, TDA-E persistence-predicted plateau heights). Total CPU budget 15-30 min; ZERO new W generation; ZERO GPU. Companion handoff: notes/exp_dev_handoff_tda_reanalysis_substrate_W_2026-05-27.md.

Citations (8 verified): Rieck Neural Persistence ICLR 2019 (arxiv 1812.09764); Naitzat Topology of DNN JMLR 2020 (arxiv 2004.06093); Wang-Nguyen-Wei Persistent Spectral Graph 2020 (arxiv 1912.04135); Galindo-Hugo Filtrations Indexed by Attracting Levels 2025 (arxiv 2506.18250); Garrido New Topological Tool Multistable 2018 Chaos 28; Modern Hopfield + topology PMC9713410; ripser/giotto-ph computation tooling. Calibration penalty 0.15-0.25 applied; novel-synthesis cap 0.50 enforced on joint TDA-NOVEL-USEFUL outcome (capped at 0.10).
