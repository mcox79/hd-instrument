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

## Pending — from 2026-05-18 materials-physics dive (iterations 1+2)

### MX1. Parallel tempering with K=4 W replicas (highest predicted single-experiment payoff)
Run K=4 W matrices simultaneously at geometrically spaced decay rates. Periodic Metropolis swaps using validation loss. Ensemble readout weighted by exp(-beta_i L_i^val).
- Setup per Earl-Deem 2005 PCCP and Hukushima-Nemoto 1996 JPSJ:
  - Decay rates {0, 1e-4, 3e-4, 1e-3} (geometric on our tested range)
  - Swap attempts every 5 batches, Metropolis on validation loss
  - Target 23% swap acceptance (Roberts-Rosenthal optimal scaling)
  - K=4 means 4x W memory (~512MB at N=4096)
- Predicted: 0.05-0.10 bits/char
- Why it should work: provably accelerates escape from local minima in glassy regimes; we are very likely in such a regime per iter-1 analysis
- Source: iter-1 + iter-2 materials science deep dive

### MX2. Two-step relaxation diagnostic (long-epoch glass probe)
Train at fixed hyperparameters for 500+ epochs. Plot loss on log-log scale. Look for: fast initial drop (beta-relaxation in glass) -> plateau over O(10) epochs -> slow secondary decay following stretched exponential exp(-(t/tau_alpha)^beta_KWW) with beta_KWW in [0.4, 0.8].
- If observed: confirms glassy dynamics; informs optimal annealing schedule (isothermal plateau just below Tc)
- If not observed: distinguishes crystalline (boring, converged) vs spin-glass (no convergence)
- Predicted: 0.02-0.05 bits/char (via annealing schedule informed by diagnostic)
- Implementation: just rerun combined config to 500 epochs at constant hyperparameters
- Source: Goetze mode-coupling theory; Berthier-Biroli 2011 Rev. Mod. Phys.

### MX3. Empirical Hessian via fluctuation-dissipation
Measure Var(W_ij) per element at training stationarity. FDR2: Var(W_ij) = (eta/2) * H_ij^(-1).
- Yields empirical Hessian without computing one
- Sagun-Bottou prediction: ~30-100 outlier eigenvalues (matching number of distinct character types). If true, low-rank W parameterization possible (40x memory reduction)
- Predicted bits effect: marginal (0-0.01) but enables 16-replica PT at same memory budget
- Source: Yaida 2018 arXiv 1810.00004; Kunin et al. 2021 PRE 104:034126

### MX4. Tc scan (find the critical learning rate)
Sweep eta in log-spaced values {5e-5, 1e-4, 2e-4, 5e-4, 1e-3, 2e-3, 5e-3, 1e-2}. At each, train to stationarity, measure Var(loss) and Var(W). Find chi (susceptibility) peak.
- Agent predicts our current arousal=0.3 is slightly SUBCRITICAL; bumping to 0.5 should put us in supercritical fast-mixing regime
- This is falsifiable: if Tc is above 0.3, sweeping arousal {0.3, 0.4, 0.5, 0.6, 0.7} should show non-monotonic behavior
- Predicted bits effect: 0.01-0.05 once optimal operating point found
- Source: Bragg-Williams + Cu3Au critical slowing down literature

### MX5. Yaida FDT test (equilibrium status diagnostic)
Track running ratio r = <W:G> / <|G|^2_F> over a stationary window. Equilibrated if |r-1| < 0.05.
Also measure kurtosis of element-wise dW (Gaussian = 3; higher = heavy-tailed Simsekli regime).
- Pure diagnostic; tells us whether temperature analogies apply
- Predicted bits effect: 0 (informs other experiments)
- Source: Yaida 2018 ICLR; Simsekli et al. 2019 ICML for heavy-tail diagnostic

### MX6. Asymmetric / Schottky-inspired Hebbian rule
Replace symmetric `dw = eta * pre * post` with asymmetric:
  `dw = eta * sign(pre*post) * |pre*post|^beta` with beta=1.3 forward, beta=1.0 reverse
- Thermionic emission asymmetry has specific functional form (J = J_s(exp(qV/kT) - 1))
- Predicted: 0.01-0.03 bits/char
- Source: Sze "Physics of Semiconductor Devices"

### MX7. Cooling schedule from order-disorder kinetics
Replace exponential LR decay with: warm-up -> isothermal plateau just below Tc (where ordering rate peaks) -> final exponential cool.
- Geman-Geman optimal schedule is impractical (logarithmic, astronomically slow)
- Real materials practitioners use piecewise-exponential with held plateaus
- Predicted: 0.02-0.05 bits/char
- Source: Cu3Au cowley 1950, Hajek 1988 Math. Oper. Res.

### MX8. Floquet stability diagnostic
Multi-epoch training is periodic. Compute Floquet multipliers from one epoch's linearized W-dynamics. If any |mu| > 1, training is unstable.
- Pure diagnostic but informs whether to push more epochs
- Predicted bits effect: 0-0.03 (stability headroom enabling longer training)
- Source: Floquet 1883; Magnus-Winkler 1966

### MX10. PT with RSB / overlap distribution diagnosis (iter-3, HIGHEST PRIORITY)
Run K=8 parallel-tempering W replicas with geometrically spaced decay rates. At
convergence, compute the empirical overlap distribution P(q) across all replica
pairs, where q = <W_a, W_b>_F / (||W_a|| ||W_b||).
- Unimodal P(q) -> non-glassy; gap is closable by ordinary methods.
- Bimodal P(q) -> 1RSB clustering; PT gives only log speedup, hard floor remains.
- Continuous P(q) -> FRSB ultrametric tree; need substrate change (BSC).
- This is the SINGLE MOST INFORMATIVE experiment in the entire 3-iteration arc.
- Source: Parisi RSB framework; Mei-Montanari random features; Krzakala-Zdeborova
  on PT failure modes in 1RSB.

### MX11. Two-time aging scan (iter-3)
Pick three waiting times t_w in {epoch 2, 5, 15}. Measure two-time autocorrelation
C(t_w + t, t_w) of ||W||_F and pool-retrieval-accuracy at geometric t-grid.
Classify dynamics:
- Curves collapse vs t/t_w -> Bouchaud trap model -> ergodicity breaks, hard loss floor
- Curves collapse vs t/t_w^mu (mu < 1) -> CTRW -> slow but bounded, more epochs help
- No collapse -> not trap-like, mean-field gradient flow
- Source: Bouchaud 1992 trap model; Fielding-Sollich 2002 sub-aging; Ben Arous-Cerny review

### MX12. Reservoir capacity ceiling (Jaeger MC bound)
Measure linear short-term memory capacity of our pool at current spectral radius.
Compare to D (substrate dim). If we're at >0.9 * D, the gap is capacity-bound and
only raising D helps.
- Pure diagnostic
- Source: Jaeger 2001 GMD Report 152; Boedecker et al. 2012 Theory Biosci.

### MX13. Engel-Van den Broeck capacity calculation
Compute alpha_c (storage capacity exponent) for our random-codebook + linear-readout
setup at our N=4096 and corpus length. Compare to measured bits/char.
- If we're at or near alpha_c -> theoretical floor; can't be closed without different architecture
- If significantly above alpha_c -> we're below theoretical optimum and improvements remain
- Source: Engel & Van den Broeck, Statistical Mechanics of Learning, CUP 2001

### MX14. Pennington-Worah random matrix diagnostic
Compute empirical singular-value distribution of W. Fit Marchenko-Pastur with
nonlinearity correction. Predicts test-error asymptotic WITHOUT retraining.
- Pure diagnostic, very cheap
- Source: Pennington-Worah, NeurIPS 2017

### MX15. Lottery ticket on FHRR ATOMS (not weights)
Magnitude-prune atoms by usage during training, retrain with same seeds. Test
whether a sparse subset of the codebook is the "winning ticket."
- Different from standard lottery ticket
- Could enable larger pools at same memory budget
- Source: Frankle-Carbin ICLR 2019 (lottery ticket); novel application to substrate

### MX16. BSC substrate for parallel tempering specifically
BSC dynamics are native to Metropolis MCMC (bit flips have O(1) energy proposals).
FHRR requires Langevin/HMC. Run PT on BSC version of char-LM for cleaner dynamics.
- Overlap q is normalized Hamming similarity - simpler interpretation
- Hardware-aligned (IBM PCM is BSC)
- Source: Karandashev-Kryzhanovsky 2017; iter-3 hardware analysis

### MX17. Ferroelectric HfZrO FeFET-inspired multi-timescale W
HfZrO FeFETs have built-in fast/slow weight separation in silicon. Two-pool
analog: maintain W_fast (fast updates, fast decay) and W_slow (slow updates,
no decay), combine at readout. Built-in alpha/beta relaxation by design.
- Source: Mulaosmanovic et al. Nat. Electron. 2020; Halter et al. Comm. Mater. 2023

### MX18. Information bottleneck diagnostic
Estimate mutual information I(pool; next-byte) and I(pool; full-history) over
training. Should grow then plateau on the first; should compress on the second.
- Diagnostic of how the pool's representation evolves
- Source: Tishby-Pereira-Bialek 1999; Tishby-Zaslavsky arXiv:1503.02406

## Pending — from 2026-05-18 brain-science deep dives

### Hypothesis-driven mapping (LLM capacity → brain mechanism → HDC implementation)

| LLM capacity | Brain mechanism | HDC implementation | Status |
|---|---|---|---|
| Next-token prediction | Cortex (semantic memory) | W matrix | done |
| Long-range context retrieval | Hippocampus DG→CA3→CA1 | Pointer pool | done (but no DG step) |
| Short-term coherence | PFC working memory attractor | Persistent state hypervector | NOT DONE |
| Output confidence | Inhibitory plasticity / E-I balance | Inhibitory W_inh matrix | NOT DONE |
| Compositional binding | Cross-cortical projections | Multi-relation matrices | not at LM scale |
| Hierarchical structure | Cortical hierarchical predictive coding | Multi-layer Hebbian | NOT DONE |
| Error correction | Cerebellar climbing fibers | Sparse-supervised error matrix | NOT DONE |
| Long-term consolidation | Sleep replay, schemas | Offline pool replay | NOT DONE |
| Pattern decorrelation | DG sparse expansion | k-WTA pre-storage | NOT DONE |
| Nonlinear feature integration | Dendritic computation | Pointwise NL on W output | RUNNING (this session) |
| Output gating | Thalamus / basal ganglia | Inhibitory gating | NOT DONE |
| Salience-gated learning | Amygdala BLA → NE | Surprise-burst LR boost | reformulation pending |

### BR1. Dendritic nonlinearity on W readout (RUNNING)
Pointwise sigmoid/tanh/relu on q = W @ context BEFORE softmax cleanup. Different from
Krotov (which applies NL to similarity scores; this applies to W output vector).
Six variants in sweep: magnitude_tanh, magnitude_relu, magnitude_sigmoid, real_imag_tanh
- Predicted: -0.04 to -0.08 bits/char
- Effort: low (~1 hour)
- Source: Polsky-Mel-Schiller 2004 Nat Neurosci; Beniaguev-Segev-London 2021 Neuron

### BR2. DG-style sparse projector before pool storage (Module 0)
Apply sparse random k-WTA expansion (e.g., bind context to 4-8 random "DG atoms",
keep top-5% of dimensions) before writing to the pool.
- Predicted: -0.02 to -0.06 bits/char
- Effort: low (~1-2 hours)
- Reduces pool collision rate for similar contexts
- Source: McClelland-McNaughton-O'Reilly 1995 Psych Review; Yassa-Stark 2011 Trends Neurosci

### BR3. Climbing-fiber sparse error matrix C (Module 1)
Second matrix C, same shape as W, updated ONLY by a sparse climbing-fiber channel.
Compute residual e = target - W*x. Update C only on top-k features of x (k≈64).
- Decorrelates fast supervised error from slow Hebbian semantics
- Predicted: -0.02 to -0.04 bits/char
- Effort: medium (~2 hours)
- Source: Marr 1969 J Physiol; Albus 1971; Ito 1984; Raymond-Medina 2018 Annu Rev Neurosci

### BR4. PFC working-memory attractor (Module 4)
Add persistent state hypervector h_t = alpha * h_{t-1} + (1-alpha) * x_t with attractor
cleanup at each step. Fed alongside pool retrieval.
- Carries multi-character context that neither pool keys nor W captures
- Predicted: -0.01 to -0.03 bits/char
- Effort: low
- Source: Wang 2001 Trends Neurosci; Goldman-Rakic 1995 Neuron; Mongillo-Barak-Tsodyks 2008 Science

### BR5. Grid-cell-like fractional-binding position atoms
Replace IID position atoms with fractional binding P^k where P is a unitary base atom.
And/or hexagonal modulation. FHRR was designed for this.
- Predicted: -0.03 to -0.07 bits/char
- Effort: low-medium
- Source: Plate 2003 IEEE TNN; Frady-Kanerva-Sommer 2018 NeurIPS; Frady-Kleyko-Sommer 2022 Neural Comp

### BR6. Sleep-replay offline consolidation
Between epochs, run reverse-order and shuffled passes over the pool to update W
(no new data). Redistributes Hebbian credit, reduces recency bias.
- Predicted: -0.03 to -0.06 bits/char
- Effort: low
- Source: Wilson-McNaughton 1994 Science; Ji-Wilson 2007 Nat Neurosci; Káli-Dayan 2004 Nat Neurosci

### BR7. Phasic dopamine reformulation of surprise modulation
Only modulate updates when prediction error exceeds 90th percentile of recent errors,
with short exponential decay window (~10 tokens). NOT uniform scaling (which failed).
- Predicted: -0.01 to -0.03 bits/char
- Effort: low
- Source: Schultz-Dayan-Montague 1997 Science; Aston-Jones-Cohen 2005 Annu Rev Neurosci

### BR8. Theta-gamma temporal multiplexing for multi-relation W
Maintain k=4-7 W matrices, one per "gamma slot"; rotate which slot is read/written per
token based on a position-modulo clock. Implicit multi-relation channel.
- Predicted: -0.02 to -0.05 bits/char
- Effort: medium
- Source: Lisman-Jensen 2013 Neuron

### BR9. Basal-ganglia gating G (Module 2)
Inhibitory mask vector g in [0,1]^M over pool slots, computed from a scoring head.
Suppresses non-selected entries via subtractive inhibition before readout.
- Predicted: -0.01 to -0.02 bits/char
- Effort: medium
- Source: Daw-Niv-Dayan 2005 Nat Neurosci; Sherman-Guillery 2011

### BR10. Thalamic router T (Module 3)
Learned 3-way mixture over {W, pool, C} contributions, conditioned on low-dim context
summary. Dynamic per-step routing.
- Predicted: -0.01 to -0.02 bits/char
- Effort: low (after C exists)
- Source: Sherman-Guillery 2002 Phil Trans R Soc B; Halassa-Kastner 2017 Nat Neurosci

### BR11. Inhibitory W_inh matrix
Parallel inhibitory matrix with anti-Hebbian update. Final readout = W_exc*x - W_inh*x.
- Predicted: -0.01 to -0.02 bits/char
- Effort: low
- Source: Vogels-Sprekeler-Zenke-Clopath-Gerstner 2011 Science

### BR13. Sparse k-WTA atoms (substrate-level sparsity)
Make each FHRR atom mostly zero with only ~5% nonzero components. Mimics sparse
coding in cortex (~2-5% activity). Could combine with DG-projector (BR2) for
additional sparsity at the pool layer.
- Risk: may break the binding orthogonality that makes FHRR work; bind(a, b)
  on sparse atoms gives even sparser results that may not generalize
- Predicted: uncertain, ±0.05 bits/char
- Effort: low (one-line atom-generation change)
- Source: Olshausen-Field 1996 Nature on sparse coding; brain-inspired discussion 2026-05-18

### BR14. Multi-scale hierarchical atoms (grid-cell-module style)
Position atoms at sqrt(2)-spaced scales — multiple "modules" of position codes
operating at different effective ranges. Each scale captures different temporal
context. Natural extension of BR5 (single-scale grid-cell positions).
- Only useful if BR5 succeeds; do it as follow-up
- Predicted: -0.02 to -0.05 bits/char on top of BR5
- Effort: medium
- Source: Stensola et al. 2012 Nature on grid-cell modules; Hafting-Fyhn-Moser-Moser 2005 Nature

### BR15. Tuning-curve atoms for bytes (population code)
Generate byte atoms with explicit overlap structure between similar bytes
(e.g., 'e' atom close to 'a' atom; punctuation closer to other punctuation).
Bio-style population code with multiple atoms activated per stimulus.
- Hard to define "similar" for arbitrary byte vocabularies without prior
- Cleaner with linguistic tokenization (subword/word level)
- Predicted: 0.01-0.04 bits/char if "similar" can be defined well
- Effort: low to medium depending on similarity definition
- Source: tuning-curve literature; population code papers

### BR16. Frequency-stratified atoms (cortical magnification analog)
Common characters (space, 'e', 't') get higher-magnitude atoms or denser
representational space; rare characters get smaller-volume representations.
Brain's cortical magnification analog where high-acuity areas get more cortex.
- Likely small effect — unigram statistics are already captured by the
  cerebellar-nuclei tonic bias (BR12)
- Predicted: <0.02 bits/char
- Effort: low
- Source: cortical magnification literature

## Dimensions of bio-inspiration (taxonomy)

Bio-inspiration in our system has four independent axes. Each is a separate
lever:

1. **Atom CONTENT** (random IID vs structured/sparse/tuned)
   - Current: random IID FHRR phases
   - Experiments: BR13 sparse, BR15 tuning, BR16 stratified
   - Position-specific: BR5 grid-cell, BR14 multi-scale

2. **CONNECTIONS** (single W vs federated multi-module)
   - Current: single W matrix
   - Experiments: BR3 climbing-fiber C, BR11 inhibitory W_inh, BR2 DG projector

3. **UPDATE RULES** (delta vs phasic-tonic, supervised vs unsupervised)
   - Current: three-factor delta rule
   - Experiments: BR7 phasic DA reformulation, BR4 PFC attractor dynamics

4. **READOUT** (linear softmax vs nonlinear, sharpened, gated)
   - Current: softmax over linear cosine similarities
   - Experiments: BR1 dendritic NL (failed/failing — magnitude-based bounds
     destabilize), BR9 BG inhibitory gating, BR10 thalamic router

Honest pattern from experiments so far: changing the READOUT (BR1, Krotov,
surprise) tends to destabilize at our SNR. Changing CONNECTIONS or adding
modules with INDEPENDENT INFORMATION (pool, multi-epoch) compounds well.
Changing ATOMS or UPDATE RULES is mostly untested but theoretical predictions
favor structured positions (BR5) over content changes (BR13-16).

The 0.115-bit gap is most likely to close via additional INDEPENDENT modules
(per iteration-3 conclusion: "optimizer choice dominates capacity choice").
Atom content changes are secondary unless we hit a clear ceiling that capacity
analysis confirms.

### BR12. Cerebellar-nuclei tonic bias
Add learned global bias vector b in R^V to readout, updated by unigram-EMA.
- Often the cheapest bits to recover (unigram + position frequency)
- Predicted: -0.005 bits/char
- Effort: trivial
- Source: Telgkamp-Raman 2002 J Neurosci; Person-Raman 2012

## Single principle to walk away with from the brain dive

**The brain wins by separating substrates that do different jobs, then arbitrating
between them — not by making one substrate cleverer.** Single-W-matrix architectures
are exactly what evolution rejected by adding cerebellum, hippocampus, basal ganglia,
and PFC. Our 0.115-bit gap is almost certainly not a tuning gap inside W — it's the
absence of a second substrate doing a job W structurally cannot. The high-leverage
experiments are not "make W better" but "add a second module with a different job."

## The single most important takeaway from the 3-iteration arc

The 0.115 bits/char gap is most likely a quenched-disorder / clustering
phenomenon, not a representational shortcoming. The FHRR atoms are quenched
disorder, the pool dynamics are slow, and the loss landscape has the structural
signatures of either a non-convex 1RSB system or a Bouchaud trap system.

This means the gap is NOT closed by adding parameters - it is closed by changing
the SAMPLING DYNAMICS (PT, population annealing) or the SUBSTRATE (BSC, where
moves are native). Optimizer choice dominates capacity choice in this regime.

Experiment MX10 (PT + P(q) measurement) is the definitive empirical test of this
hypothesis.

## Genuinely open theoretical question

Is there a Parisi-style overlap order parameter for vector symbolic architectures
with random fixed codebooks under local Hebbian learning? The Mei-Montanari
random-features analysis assumes ridge regression (convex). The Krzakala-Zdeborova
cavity method assumes sparse factor graphs. Neither covers the HDC case: dense
random codebook + non-convex local update + multi-epoch. We do not have a
rigorous theory predicting whether P(q) is uni-, bi-, or continuously-supported
for this class. MX10 would be the first empirical measurement.

### MX9. Lyapunov-Krasovskii spectral check for pool+W system
Compute lambda_max(pool-feedback Jacobian). System provably exponentially stable if lambda_max < 1 - decay.
- Diagnostic, tells us if pool size is too large for stability
- Predicted bits effect: marginal
- Source: Hale 1977; Razumikhin theorems

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

## Lower-priority experiments and additional angles (from iter-1/2/3 gap check)

### MX19. Control-theory-style adaptive learning rate (PI feedback)
Replace fixed decay with PI feedback on validation loss: `decay_t = decay_0 + K_p * loss_error + K_i * integrated_error`. Adaptive control reduces need for hyperparameter tuning.
- Source: Astrom-Murray Feedback Systems 2008; iter-3 gap check

### MX20. TD(lambda)-style replacing traces (not accumulating)
Our eligibility-trace experiment used accumulating traces (E += pre*post). Replacing-trace version sets E_ij = (max(E_ij, pre_i * post_j)). Different dynamics; well-studied in RL.
- Could rescue eligibility traces from their null result
- Source: Sutton-Barto Ch.12; Singh-Sutton ML 22 (1996)

### MX21. Sparse coding L1 penalty on pool activations
Add L1 penalty on pool slot weights during retrieval. Predicts "phoneme-like" localized representations vs distributed ones.
- Implementation: simple regularization in retrieval softmax
- Source: Olshausen-Field Nature 1996

### MX22. Continuous attractor analysis of pool dynamics
Visualize pool slot trajectories under fixed prefix. Check for Tsodyks-Sejnowski drift (bumps moving with context) vs Amari static attractors.
- Diagnostic: predicts ordering, not bits
- Source: Amari Biol. Cybern. 1977; Tsodyks-Sejnowski Neural Comp. 1995

### MX23. Population annealing instead of parallel tempering
If MX10 reveals 1RSB clustering, ordinary PT fails. Population annealing maintains many walkers + resampling, escapes barriers PT cannot.
- Higher implementation cost than PT
- Falls back option if MX10 shows RSB
- Source: Hukushima-Iba 2003; Wang-Machta-Katzgraber 2015

### MX24. Quiet planting / Population dynamics for non-RSB regimes
Another fallback if PT plateaus before achieving uniformity in P(q).
- Source: Krzakala-Zdeborova EPFL lectures 2021

### MX25. Substrate co-design: combine FHRR + BSC + permutation in one model
Multi-substrate VSA where different binding roles use different substrate types. Roles: content=FHRR (rich phase info), position=BSC (cheap), relation=permutation (cycle structure).
- Big design space; effort high
- Source: own analysis + iter-3 hardware section

### MX26. Random matrix theory diagnostic of W spectrum (Pennington-Worah, restated as separate experiment)
Already listed as MX14 but worth restating: cheap to compute, predicts test-error asymptotic from W's singular spectrum without retraining.

### MX27. Frady-Kleyko-Sommer working memory capacity test
We've used pointer-chain but not measured its working memory capacity per Frady et al. 2018 Neural Computation. Direct test: how many items can we reliably retrieve from the pool at our pool size and substrate dim?

### MX28. Spike-timing-dependent plasticity (STDP) variant
Not Hebbian (correlation) but STDP (causal asymmetry). Pre-before-post strengthens; reverse weakens. Time-windowed update rule.
- Different update class; might escape the symmetry-related failure modes
- Source: Bi-Poo Nature Neurosci. 2001; Markram et al. Science 1997

### MX29. Energy-based / Boltzmann-machine-style stochastic readout
Sample byte predictions from a Boltzmann distribution over connection-energy values rather than softmax(W*ctx). Stochastic readout might explore output space better.
- Slightly different paradigm; testable
- Source: Hinton-Sejnowski 1986; modern reformulations

### MX30. Hierarchical / mixture-of-experts pooling
Multi-tier pool: tier 1 = recent (M=128), tier 2 = consolidated medium-term (M=512), tier 3 = long-term (M=2048). Use TIER 1 first; fall back to deeper tiers when retrieval similarity is low.
- Combines MX1 (hierarchical pool) with explicit fallback mechanism
- Source: own; loosely related to hippocampal indexing theory

## Angles of inquiry (research questions not yet operationalized)

These are research questions surfaced across the 3-iteration arc that we haven't turned into specific experiments yet, but which could each generate a family of experiments:

### Q-A. What is the kernel that our random-features model implicitly defines?
Per Mei-Montanari random-features framework, we're a random-features approximation to a specific kernel induced by FHRR atoms + cleanup. Characterizing this kernel rigorously would let us predict the asymptotic accuracy ceiling. Specifically: is it shift-invariant? What's its decay? Does it match natural-language kernels well or poorly?

### Q-B. Where does eligibility-traces become useful (corpus / task threshold)?
Null on 38KB. Biology + theory say they should help with multi-step credit assignment. Is there a corpus-size threshold? Task-structure threshold (e.g., explicit long-range dependencies)?

### Q-C. Why does K=4 win over K=16 at our N=1024 baseline?
Frady bundle capacity log_2(M) <= N/(2*SNR_min) gives ~300 items at N=4096. We bundle K=4 items per step - far below capacity. The bottleneck must be subtler than raw capacity. What is it?

### Q-D. What does the brain actually use as "atoms"?
Real neurons aren't random IID. Place cells, grid cells, head-direction cells have structured tuning. Could biological codebook structure inform substrate design? Specifically: are biological "atoms" more like our random IID or more like a learned spike-timing code?

### Q-E. Multi-modal substrate combinations
Random IID for content + DFT for position + sparse for relation type. Is there a principled way to choose substrate per role from first principles, or is this experimental?

### Q-F. Is the FHRR atom random ensemble equivalent to a spin glass in some limit?
The Mei-Montanari random-features regime is convex (no RSB). But our setup is non-convex (delta rule + multi-epoch + pool feedback). Where in parameter space does the transition from non-glassy to glassy happen?

### Q-G. What does it mean that single-pass Hebbian had "structural anti-overfitting" but multi-epoch broke it?
We thought this was a property of the learning rule. Multi-epoch revealed it was an artifact of single-pass exposure. Is there a way to get the anti-overfit property while still iterating? (Maybe: continuous online learning on never-repeating data — but that just requires more data.)

### Q-H. Hardware co-design as a real engineering target
PCM exists for cleanup; FeFET multi-timescale; STT-MRAM endurance; HfZrO ferroelectric for analog symmetry. Which substrate is the deployment target if our algorithm proves out? Different substrates favor different algorithmic choices.

### Q-I. The "transformer attention IS Hopfield retrieval" framing
Ramsauer-Schlag-Hochreiter 2020 showed modern Hopfield = attention. Our cleanup IS Hopfield retrieval at finite beta. What is the missing ingredient that transformer attention has and we don't? Most likely: LEARNED keys/queries vs random fixed keys.

### Q-J. Scaling laws for HDC architectures
Our prior work established beta ~ 1.0 for depth scaling across six VSA substrates. Bundle capacity scales linearly with N. What's the THIRD scaling law - how does effective performance scale with substrate N, corpus size T, training compute C? Need a 3D scan to know.

## Theoretical questions we have NOT addressed (deep open problems)

These are open even in the published literature. Solving any would be publishable.

- **Parisi-style overlap order parameter for VSA with random fixed codebooks under local Hebbian learning.** Mei-Montanari assumes ridge regression (convex). Krzakala-Zdeborova assumes sparse factor graphs. Neither covers dense random codebook + non-convex local update + multi-epoch. MX10 (P(q) measurement) would be the first empirical data point.

- **Information-theoretic capacity of HDC with explicit pointer-chain memory.** Frady gives bundle capacity. We have no theory for bundle + addressable pool together. What's the joint capacity?

- **Closed-form prediction of when sampling-dynamics changes matter more than capacity changes.** Our iter-3 conclusion was "optimizer choice dominates capacity choice in this regime" but the regime boundary isn't characterized. Is there a phase diagram?

- **The role of the Schlag-Irie-Schmidhuber "slow network" in their fast-weight programmer.** They use gradient descent on a slow network controlling fast Hebbian writes. We removed the slow network entirely. Can the slow-network function be replaced by something local-rule? If so what?

---

## Notes on priority

The signal-stage profiling (D1) is the single most important next data point because it tells us where in the pipeline the gap lives. After D1 lands:

- If gap is at Stage A (bundle): focus on substrate (S1, S2) + larger N + better bundling
- If gap is at Stage B (W's predictions): focus on update rules (U1, U2, U3) + multi-epoch (D2) + multi-head (A2)
- If gap is at Stage C (cleanup): focus on readout (R1, R2, R3) — and R1 (modern Hopfield over pool) is the highest predicted single-experiment payoff

Multi-epoch (D2) is a high-priority cheap experiment regardless of profile outcome because it addresses a methodology gap, not an architecture gap.

Re-testing K with N=4096 (D4) is also cheap and could give a free 0.1+ bits.

After those land, ranking among the rest depends on profile result + how much gap remains.
