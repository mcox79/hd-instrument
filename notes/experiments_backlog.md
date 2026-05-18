# Experiments backlog

Snapshot taken 2026-05-17 to make sure we don't lose any of the candidate experiments accumulated across:
- Track 0.1 follow-up sweeps (architectural)
- Cross-field research (math/quantum/physics/economics) passes 1 and 2
- Materials-science research passes 1 and 2
- Empirical diagnostics
- Methodology gaps we've identified

Format for each item:
- **Name** — what it does — predicted bits/char effect at our scale — effort to implement — risk/notes — source

Items are categorized, not strictly priority-ordered within categories (priority depends on profile results).

---

## Already done (results landed)

| Experiment | Best result | Δ vs baseline (3.16) | Verdict |
|---|---|---|---|
| Baseline Hebbian-VSA (Track 0.1) | 3.16 | — | Alive tier |
| Pointer-chain pool (M=1024, α=0.3) | 2.91 | −0.25 | Real win |
| Larger N=4096 alone | 3.02 | −0.14 | Real win |
| **Combined N=4096 + pointer-chain** | **2.84** | **−0.32** | **Current best** |
| Eligibility traces (γ ∈ {0..0.95}) | 3.11 | ~0 | Null at this corpus |
| Homeostatic decay (1e-4) | 3.16 | 0 | Null |
| Surprise-modulated arousal (as imp'd) | 4.27 | +1.1 | Hurt — wrong formula |
| Krotov polynomial cleanup (n ∈ {2,3,5,7}) | 3.05 | +noise | Hurt at every n>1 |
| Bloch / randomized DFT substrate | 3.14 | −0.02 | Noise |
| Tiny transformer (862K, ceiling) | 2.39 | (gap 0.45) | Reference |

---

## Pending — diagnostic / methodology

### D1. Signal-stage profiling (RUNNING)
Decomposes loss into Stage A (bundle recovery), Stage B (W's argmax accuracy + margin), Stage C (softmax cleanup). Tells us where in the pipeline the 0.45 bits live.
- Predicted: not bits/char — it's a diagnostic that informs all other priorities.
- Effort: done (running)
- Source: own analysis after Krotov / Bloch failures

### D2. Multi-epoch Hebbian
Iterate over training corpus multiple times. Every experiment so far has been single-pass. Hebbian locality doesn't require single-pass — the brain replays during sleep.
- Predicted: 0.05–0.20 bits/char (high uncertainty; could be 0 if W converges in one pass, or substantial)
- Effort: 5-line change (wrap training loop in epoch counter)
- Risk: low; Hebbian's anti-overfit property might still hold across epochs but should verify
- Source: own analysis — strongest methodological gap I noticed

### D3. Multi-seed runs for variance bounds
Every single number we have is one seed. Variance on these reported gaps is unknown.
- Predicted: not a bits/char effect; promotes single-seed claims to mean±std
- Effort: small (run each best config with 3-5 seeds)
- Risk: low

### D4. Re-test K (context window) with N=4096
K=4 > K=8 > K=16 at N=1024 (bundle saturation). With N=4096 the saturation point is later. Maybe K=8 or K=16 wins now.
- Predicted: 0.05–0.20 bits/char if K=16 or K=32 becomes viable at N=4096
- Effort: small (one parameter change, sweep)
- Risk: low

---

## Pending — readout / cleanup modifications

### R1. Modern Hopfield over the pointer pool (Ramsauer-style)
Replace softmax(β · W·h) with softmax(β · ⟨h, stored_context_μ⟩) over the M pool entries directly, β-tuned by score-distribution entropy. Effectively treats the pool as a continuous Hopfield network.
- Predicted: **0.10–0.20 bits/char** (per pass-2 materials, highest predicted single-experiment payoff)
- Effort: medium (~1 hour; modify pool retrieval to use this energy form)
- Risk: medium — β tuning may re-encounter the destabilization we hit with high β; mitigate with adaptive β
- Source: pass-2 materials-science dive; Hu et al. 2024 NeurIPS

### R2. Krotov polynomial with z-scored similarities
Krotov failed because our similarities are 0.01–0.1 and cubing crushes them. Fix: z-score similarities (sim − mean) / std to roughly [−3, +3], then polynomial, then softmax.
- Predicted: 0.05–0.15 bits/char if the dynamic-range fix saves the technique
- Effort: small (3-line change in cleanup)
- Risk: medium — may still fail if our SNR is too low for ranking-based amplification
- Source: own analysis of why Krotov failed

### R3. Iterative cleanup (multi-step Ramsauer)
Modern Hopfield does multiple update steps to converge to a fixed point. We did single-shot. Iterative refinement might naturally produce the saturating similarities that polynomial nonlinearities need.
- Predicted: 0.05–0.15 bits/char
- Effort: small (loop the prediction step 3-5 times before final softmax)
- Risk: low; can ablate cleanly
- Source: own analysis; Ramsauer et al. 2021 ICLR

### R4. Two-stage cleanup (broad then sharp)
First standard softmax → identifies a candidate region. Then Krotov polynomial / sharper temperature on the top-K candidates only, where similarities are larger.
- Predicted: 0.05–0.10 bits/char
- Effort: small-medium (top-K selection + second softmax)
- Risk: low
- Source: own analysis

### R5. LDPC + belief propagation cleanup
Impose a Tanner-graph parity-check structure on which atom combinations are legal bundles; cleanup becomes iterative message passing on a sparse graph. Provably approaches Shannon capacity.
- Predicted: high but uncertain (could be 0.1–0.4 bits if the analogy ports)
- Effort: high (designing the parity structure for HDC bundles; implementing BP iterations)
- Risk: high — coding theory math may not port cleanly to continuous-valued atoms
- Source: pass-1 cross-field research; Gallager 1963; Richardson-Urbanke 2001

### R6. CDMA MMSE multi-user detection
Replace argmax-cosine cleanup with MMSE decoder using a running estimate of the atom Gram matrix. Verdú's central result: MMSE strictly dominates matched-filter cleanup at the same dimensionality.
- Predicted: 0.05–0.15 bits/char
- Effort: medium (~2 hours; estimate Gram matrix, modify cleanup formula)
- Risk: medium — works in CDMA where atoms are spreading codes; our setting differs subtly
- Source: pass-1 cross-field; Verdú 1998 Multiuser Detection

---

## Pending — substrate / atom design

### S1. Stealthy hyperuniform FHRR atoms
Optimize atom phases so structure factor S(k) = 0 for k < K. Anti-correlated low-frequency noise gives reduced bundle variance.
- Predicted: 0.04–0.08 bits/char
- Effort: medium (gradient descent on phases under unit-modulus constraint; ~30 min compute to generate)
- Risk: low; well-grounded in Torquato 2018 *Physics Reports* 745
- Source: pass-2 materials science

### S2. DFT for position atoms only, IID for byte atoms
Position roles have natural ordering — orthogonal codes are sensible. Bytes are unordered content — random IID keeps aliasing resistance. Mixed substrate.
- Predicted: 0.02–0.08 bits/char (small but predicted positive)
- Effort: tiny (5-line split in atom generation)
- Risk: low
- Source: own analysis of why Bloch failed as a uniform substrate

### S3. DFT for intermediate concept codebook in a multi-layer setup
Use DFT atoms only as the intermediate-layer codebook, where orthogonality has meaning. Random IID still at input/output.
- Predicted: depends on multi-layer working at all; bonus 0.02–0.05 bits/char on top of multi-layer
- Effort: depends on multi-layer implementation
- Risk: contingent on M1 succeeding
- Source: own analysis

### S4. FFT-based fast cleanup with DFT atoms
Computational, not accuracy: if atoms are DFT columns, cleanup is O(N log N) via FFT instead of O(N²) matmul. Matters for scaling N to 16K+.
- Predicted: zero accuracy effect; ~10-100× speedup at large N
- Effort: medium (rewrite cleanup using torch.fft)
- Risk: low
- Source: own analysis

### S5. Sparse / structured atoms
Beyond DFT — Grassmannian / equiangular tight frames (ETFs) from frame theory. Minimize worst-case correlation. Frame-theory perspective on the substrate.
- Predicted: 0.02–0.06 bits/char (similar to hyperuniform — variance reduction at constant rate)
- Effort: high (constructing ETFs of arbitrary size is hard; approximate Grassmannian packings)
- Risk: medium
- Source: pass-1 math research; Strohmer-Heath 2003

---

## Pending — update rule modifications

### U1. Cahn-Hilliard / conservative Hebbian update
Project ΔW onto trace-preserving subspace each step: ΔW ← ΔW − (tr(ΔW)/N²)·I. Prevents rare-character weights from bleeding into common-character weights.
- Predicted: 0.03–0.07 bits/char
- Effort: tiny (~5 lines)
- Risk: low
- Source: pass-2 materials; Hohenberg-Halperin Model B

### U2. Nucleation-threshold gated updates
Apply Hebbian update only when ‖ΔW_step‖_F > θ_c (empirical median of recent updates). Suppresses noise-driven drift.
- Predicted: 0.02–0.05 bits/char
- Effort: tiny (~3 lines)
- Risk: low
- Source: pass-2 materials; classical nucleation theory

### U3. Predictive-coding-style surprise modulation
Our v2 surprise-modulation hurt because the formula scaled arousal up uniformly. Fix: surprise = deviation from running EMA of surprise (not absolute log-prob). NE response analog.
- Predicted: 0.05–0.10 bits/char if the deviation formula works
- Effort: small (modify modulator formula; track EMA)
- Risk: medium — might still destabilize if predictions remain in low-SNR regime
- Source: own analysis of v2 surprise failure

### U4. Higher-order Kuramoto coupling (4-phase tensor)
Promote outer-product W to a 4-tensor that couples four phases (rather than two). Superlinear capacity via energy-barriered phase-locked states.
- Predicted: 0.1–0.3 bits/char if it works
- Effort: very high (memory and compute go from N² to N⁴; need low-rank truncation)
- Risk: high
- Source: pass-2 materials; Bick et al. 2025 arXiv 2507.21984

### U5. Equilibrium propagation
Energy-based RNN with free and clamped phases; weight update = local contrastive Hebbian. In the limit equals BPTT but trains layer-wise locally.
- Predicted: depends on multi-layer; 0.1–0.3 bits/char if works
- Effort: high
- Risk: medium-high — relaxation dynamics need careful design
- Source: pass-1; Scellier-Bengio 2017

### U6. Eligibility traces, retest at scale
Eligibility traces gave null on 38KB corpus (no long-range structure). Retest on a corpus with multi-sentence consistency.
- Predicted: 0.05–0.15 bits/char on appropriate corpus
- Effort: small (already implemented in exp_eligibility_charlm.py)
- Risk: low; just contingent on corpus choice
- Source: pre-registered note exp_track0_1c.md

---

## Pending — memory hierarchy / pointer-chain variants

### M1. Hierarchical pointer-chain pool (multi-ring)
Three rings at geometric scales: M=1024 short-term, M=128 medium, M=16 long. Different retrieval temperatures per ring. Implements RSB ultrametric memory.
- Predicted: 0.05–0.10 bits/char
- Effort: medium (~1 hour; extend pool module)
- Risk: low — incremental on known-good mechanism
- Source: pass-2 materials; Mezard-Parisi-Virasoro RSB

### M2. Larger pool with longer retrieval window
Test M ∈ {2048, 4096, 8192}. We saw M=1024 > M=256, monotonic so far.
- Predicted: 0.02–0.10 bits/char per doubling, diminishing returns
- Effort: tiny
- Risk: low
- Source: extrapolation from 0.1b results

### M3. Learned attention over pool (controversial)
Replace fixed softmax retrieval with learned attention weights per stored memory, updated by Hebbian when retrieval was correct. Slight violation of "no gradient descent" if we count this as learned weights.
- Predicted: 0.10–0.20 bits/char potentially
- Effort: medium
- Risk: high (philosophically tricky — is this still "pure local"?)
- Source: own analysis; close to transformer attention

### M4. Variable-range hopping cleanup over pool
Use Mott VRH retrieval dynamics: select next pool entry by maximizing exp(−d_ij/σ − ΔE_ij/T). Diagnostic of pool structure; could be retrieval rule.
- Predicted: unclear — possibly bits effect via better retrieval, possibly just diagnostic
- Effort: medium
- Risk: medium
- Source: pass-1 materials; Mott 1969

### M5. Sleep-style replay buffer
Store recent (context, target) tuples; periodically replay them offline using delta rule. Standard fix for catastrophic forgetting in non-i.i.d. streams.
- Predicted: 0.02–0.10 bits/char at corpus scale; bigger effect for continual learning
- Effort: medium
- Risk: low
- Source: pass-1 cross-field; Bellec et al. e-prop; Diekelmann-Born sleep consolidation

---

## Pending — architecture (depth and parallelism)

### A1. Multi-layer Hebbian with target propagation
Two W matrices: context → W1 → intermediate codebook cleanup → W2 → byte. Target propagation (or feedback alignment) for layer-1 updates. Local rule.
- Predicted: 0.10–0.30 bits/char if it works at all; could be 0 if random intermediate codebook can't form useful representations
- Effort: high (~3-4 hours)
- Risk: medium-high — predictive coding shows it can work but empirical performance varies
- Source: own; Lillicrap et al. 2016 (FA); Lee et al. 2015 (TP); Whittington-Bogacz 2017

### A2. Multi-head / parallel W matrices
Multiple parallel W matrices, each trained by Hebbian with its own modulator profile. Specialize on different patterns. HDC analog of multi-head attention.
- Predicted: 0.05–0.20 bits/char
- Effort: medium (~2 hours)
- Risk: medium — needs design of how to combine heads
- Source: own analysis

### A3. Tensor-network / DMRG-style local sweeps
Stack outer-product matrices as a tensor train with DMRG-like local sweep optimization. Local-rule version of global coordination.
- Predicted: high but uncertain — 0.1–0.4 bits/char
- Effort: high (~5-10 hours)
- Risk: high
- Source: pass-1 cross-field; Stoudenmire-Schwab 2016

### A4. Variational RG / block-spin stacking
Stack W matrices where each layer is a block-spin coarse-graining of the layer below. Mehta-Schwab 2014 proved this maps to RBM layer-wise training but is purely local at each scale.
- Predicted: 0.05–0.20 bits/char
- Effort: high (~5 hours)
- Risk: medium — assumes scale-invariant structure in text (approximately true via Zipf)
- Source: pass-2 materials; Mehta-Schwab 2014

---

## Pending — scaling experiments

### Sc1. Scale corpus to 1 MB
Retest baseline + best configs on a tiny-shakespeare-class corpus (~1 MB). Transformer no longer overfits at this size; we'd see the true ceiling.
- Predicted: not bits effect per se; tells us if gap closes/widens at scale
- Effort: medium — pick corpus, re-run experiments (~hours of compute on CPU)
- Risk: low
- Source: original Track 0 plan, option (a)

### Sc2. Scale corpus to 10 MB
Same but bigger. At this size CPU compute time becomes the bottleneck; would push us to cloud GPU.
- Predicted: definitive picture of architecture's scaling behavior
- Effort: medium-high (compute + possibly cloud setup)
- Risk: low if compute available
- Source: own

### Sc3. Scale to BPE token vocab
Currently byte-level (256 atoms). BPE vocab (~32K-50K atoms) reduces ambiguity per prediction but enlarges codebook for cleanup.
- Predicted: 0.2–0.5 bits/char potential; tradeoff with cleanup cost
- Effort: high — need tokenizer, larger codebook, careful evaluation
- Risk: medium
- Source: own

### Sc4. Compute and memory characterization
Profile current ops (FHRR bind, BSC bind, cleanup, Hebbian update) for FLOPs, bytes-moved, ops-per-token. Project onto CPU / GPU / in-memory analog. Half-done in `notes/hardware_characterization.md`; deeper measurement still pending.
- Predicted: provides the energy story for any external claim
- Effort: medium
- Risk: low
- Source: Track 0.2 plan in NEXT_PHASE.md

---

## Pending — strategic / writeup

### W1. Build proper validation set + multi-seed protocol
Currently train/test 80/20. Add proper val split + 3+ seeds per config to promote single-number claims to confidence intervals.
- Effort: small-medium
- Risk: low

### W2. Compare against fairly-stopped tiny transformer
Currently our transformer baseline cites the best-stopped value (2.39). For full fairness should report end-of-training, mid-training, and best-stopped separately.
- Effort: small
- Risk: low

### W3. Ship hd-instrument v0.1.0 to PyPI
Original Bet A plan. The library has standalone value regardless of LM results.
- Effort: medium (~few hours)
- Risk: low

### W4. Methods preprint
Substrate scaling laws + architectural sweep + observability framework + hardware projection. Real methods contribution at small scale.
- Effort: high (~1-2 weeks)
- Risk: low

---

## Theoretical questions we have NOT addressed

These don't fit cleanly into experiments but are open research questions worth flagging:

- **What is the kernel that our random-features model implicitly defines?** Per the Q5 framing of pass-2 materials, we're a random-features approximation to a specific kernel induced by FHRR atoms. Characterizing this kernel rigorously would let us predict the asymptotic accuracy ceiling.
- **Where exactly does eligibility traces become useful?** Null on 38KB, but biology + theory say they should help with multi-step credit assignment. Is there a corpus-size or task-structure threshold above which they start to matter?
- **Information-theoretic capacity bound:** Frady et al. bundle capacity log_2(M) ≤ N/(2·SNR_min) gives ~300 items at N=4096. We bundle K=4 items per step — far below this. Why does K=4 win over K=16? Subtler tradeoff than raw capacity.
- **What does the brain actually use as "atoms"?** Real neurons aren't random IID — they have known correlation structure, place fields, grid cells. Could biological codebook structure inform substrate design?
- **Multi-modal substrate combinations** — e.g., random IID for content + DFT for position + sparse for relation type. Is there a principled way to choose substrate per role?

---

## Notes on priority

The signal-stage profiling (D1) is the single most important next data point because it tells us where in the pipeline the gap lives. After D1 lands:

- If gap is at Stage A (bundle): focus on substrate (S1, S2) + larger N + better bundling
- If gap is at Stage B (W's predictions): focus on update rules (U1, U2, U3) + multi-epoch (D2) + multi-head (A2)
- If gap is at Stage C (cleanup): focus on readout (R1, R2, R3) — and R1 (modern Hopfield over pool) is the highest predicted single-experiment payoff

Multi-epoch (D2) is a high-priority cheap experiment regardless of profile outcome because it addresses a methodology gap, not an architecture gap.

Re-testing K with N=4096 (D4) is also cheap and could give a free 0.1+ bits.

After those land, ranking among the rest depends on profile result + how much gap remains.
