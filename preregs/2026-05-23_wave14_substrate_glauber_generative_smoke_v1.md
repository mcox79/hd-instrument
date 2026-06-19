# Prereg: wave14_substrate_glauber_generative_smoke_v1

**Trigger**: Strategy x Research shore-up matrix 2026-05-23 Weakness #5 (HIGH-strategic / MEDIUM-tactical). Portfolio gap #1 per cycle 188 Task 4: every capability in v168 is a read/retrieve/infer-mode primitive. NO row anchors generative-mode behavior. This is a dead-or-alive test for whether the substrate supports a 12th capability axis.

**Hypothesis**:
Finite-T Glauber dynamics on the Kerdock-Hebbian W operating point validated by v164b bimodal-retrieval (N=4096, t=6), when initialized from RANDOM noise (not target codewords) and sampled at the bimodal-beta regime, produces a sample distribution that satisfies four substrate-generative criteria SIMULTANEOUSLY:
1. **Novelty**: >=30% of post-burn-in samples are NOT in the stored codeword set (min-Hamming > 0.05 N).
2. **Diversity**: median pairwise Hamming distance across samples >= 0.15 N.
3. **Stability under perturbation**: >=70% of samples re-converge to within 0.05 N Hamming of original after 5% bit-flip perturbation + 20 Glauber sweeps.
4. **Binding coherence**: median max-overlap with the Kerdock codebook >= 0.30 (samples lie in the substrate's algebraic envelope).

This is a substrate-generative-mode dead-or-alive test. Either outcome is portfolio-shaping per Pattern 6 / [[feedback-dont-overextend-theorems]] / [[feedback-no-smoke]].

**Operating point**: N=4096 (t=6 Kerdock), alpha=M/N=0.25 (M=1024 codewords), beta in {3.0, 5.0, 7.0} (bimodal regime per v164b), 5 seeds per beta, n_burn=400 sweeps, n_collect=200 samples per chain, sample_stride=5 sweeps, 30 stability checks per cell. Pure CPU.

**Hard PASS** (`SUBSTRATE_GENERATIVE_CAPABLE`):
- At the best (beta, aggregated-over-seeds) cell: novelty >= 0.30 AND diversity >= 0.15 AND stability >= 0.70 AND coherence >= 0.30.

**Hard FAIL** (`SUBSTRATE_GENERATIVE_FAIL`):
- At every beta cell: novelty < 0.05 (collapse to training set) OR diversity < 0.01 (mode collapse to single point) OR stability < 0.20 (noise, not generation).

**PARTIAL** (`SUBSTRATE_GENERATIVE_LIMITED`): in between.

**Closure implication**:
- PASS → portfolio opens a 12th capability axis (generative-mode). Substrate-product story extends from "retrieves" to "retrieves + generates". This is the FIRST non-retrieve capability in the portfolio.
- FAIL → portfolio honestly characterized as RETRIEVAL-ONLY. Substrate-product story sharpens — sells what it is, not what it isn't. Per [[feedback-no-smoke]] this is the brutal-honest closure.
- LIMITED → 12th axis is a partial candidate; needs follow-up at finer beta grid or alternative dynamics (MH on W-perturbation space; score-based reverse diffusion). Filed as next research drill.

**Cost**: ~1 hr CPU on remote_cpu_queue at FULL.

**Smoke result**: N=1024 1-seed at beta in {4, 6}: novelty=1.0 (samples are all novel — possibly TOO novel, i.e. noise-not-generation); at beta=6 stability=0.90 (good); diversity=0.037 (borderline LIMITED at the 0.01 FAIL threshold); coherence=0.21-0.23 (below PASS 0.30). Directional signal mixed — at smoke the chain reaches the stable-but-low-diversity regime, suggesting the 200-sample collection at N=4096 with stride=5 is needed to populate the distribution.

**Novel-territory caveats** (per [[feedback-lit-scan-calibration-penalty]]):
- This is uncharted regime — published Hopfield work focuses on retrieval not generation. P(novel-synthesis) capped at 0.50.
- The Glauber sweep is synchronous (Peretto 1984) which can introduce period-2 attractors at zero T; in the bimodal-finite-T regime this is averaged out, but stability_rate may be inflated if the chain spends time in a 2-cycle. Mitigation: sample_stride=5 sweeps gives at least 5 chances to escape a 2-cycle per sample.
- Binding coherence is a HEURISTIC for "semantic coherence equivalent" — measures algebraic-envelope membership, NOT actual semantic content (the substrate has no semantic ground truth). This is the cleanest substrate-internal coherence metric available without inventing semantics.

**Risks**:
- novelty == 1.0 may indicate the chain is in pure noise (not generation). Mitigation: the stability_rate + coherence gates rule out pure-noise interpretation.
- mode collapse (one sample taken everywhere): diversity gate catches this.

**Lit cross-check**: Hopfield 1982 (Hebbian retrieval); Peretto 1984 / Coolen 2001 (parallel heat-bath Glauber); Amit-Gutfreund-Sompolinsky 1985 (AGS bimodal phase); score-based diffusion (Song et al. 2021) — semantic analog if generation is found. Glauber sampling from a Hopfield Boltzmann is textbook; the substrate-novel question is whether the Kerdock-Hebbian W (NOT iid Gaussian W) preserves the generative property.
