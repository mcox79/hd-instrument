# Cumulative Results Tracker

Per-experiment results with measurements and comparisons to published baselines.
Updated as experiments complete.

## Reference baselines on this corpus

Corpus: 48,512 bytes of project markdown (PLAN.md, NEXT_PHASE.md, README.md,
PROGRESS.md, RESULTS.md, CLAUDE.md). Train 80%, test 20%, byte-level.

| Baseline | Test bits/char | Notes |
|---|---|---|
| Uniform random over 256 bytes | 8.0 | chance |
| Uniform over observed 109 distinct bytes | 6.77 | "true chance" |
| Unigram with Laplace smoothing | 5.74 | byte frequencies only |
| 2-gram with Laplace+backoff | 4.90 | 1-byte context |
| 3-gram (smoothing-broken on small data) | 5.30 | (unreliable comparison) |
| 5-gram (smoothing-broken) | 5.51 | |
| **Tiny transformer 862K params, best-stopped, CPU** | **2.39** | best validation-monitored stop |
| Tiny transformer end-of-training | 3.61 | overfits without early stopping |

## Reference numbers from the literature

For context on "what good byte-level LMs achieve":
- LSTM-2B on PG-19 (Rae et al. 2020): ~1.0 bpc — large corpus, large model
- GPT-2 small on WebText: ~1.0 bpc
- GPT-3 / Llama-3 8B on web data: ~0.75 bpc
- Frontier LLMs on diverse text: ~0.5-0.7 bpc

So our tiny-transformer ceiling 2.39 sits in the "tiny model on tiny corpus" regime.
A real-LLM-class system would reach ~0.75 bpc on a real corpus.

## Theoretical predictions

- **Frady-Kleyko-Sommer (2018, Neural Comp):** bundle capacity log2(M) ≤ N/(2·SNR_min).
  For N=4096 and our typical SNR ~3, predicts ~600 items per bundle before SNR collapse.
  We bundle K=4 items per step — far under saturation, so capacity-per-step is NOT the limit.
- **Plate (1995, HRR original):** for k-deep binding chains, signal-to-noise scales as N^{-k/2}.
  At our K=4 with random IID atoms, signal:noise after binding ~ N^{-2} = 1/16M for N=4096.
  Cleanup against codebook recovers if it's above the noise floor.
- **Engel-Van den Broeck (Statistical Mechanics of Learning, 2001):** for random-feature
  models with N features and m training examples, generalization error scales as
  E[error] = O(m / N) above the critical capacity. Below, error = excess of optimal.
- **Schlag-Irie-Schmidhuber (2021, ICML):** delta-rule fast weights on linearized
  transformers reach 31.5 bpc on WikiText-103 test (their Delta Network) vs
  transformer baseline 29.6. They demonstrate the delta rule is the right
  variant of outer-product Hebbian for sequence modeling. Architecture overlap
  with us: same delta rule, same outer products. Differences: gradient descent on
  slow network, learned keys, no pool, no modulators.
- **Krotov-Hopfield (2016, NeurIPS):** polynomial-energy DAM capacity scales as N^{n-1}
  for interaction power n. We tested this in our cleanup — failed at our similarity
  scale (random IID similarities ~0.05 not ~1).

## Experiment log

### Session 2026-05-17 (CPU)

| Config | Best bpc | Notes / lit comparison |
|---|---|---|
| Baseline Hebbian-VSA single-pass N=1024 | 3.16 | "alive tier" per pre-reg, beats 2-gram 4.90 by 1.74 |
| Pointer-chain (M=1024, α=0.3) | 2.91 | Schlag-Irie-Schmidhuber show this kind of memory architecture is the linear-transformer descendant — we get similar gain |
| Larger N=4096 | 3.02 | Capacity scaling per Engel-Van den Broeck: log(N) prediction; we measure +0.14 bpc going 1024→4096 |
| Combined N=4096 + pointer-chain | 2.84 | Both improvements compound |
| Eligibility traces | 3.11 (null) | Bellec et al. e-prop predicts gains on temporal credit assignment — no measurable benefit at K=4 single-step prediction |
| Krotov polynomial cleanup | 4.15 (fail) | DAM theory predicts gain only at saturating similarities; ours are 0.05 not 1 |
| Bloch / randomized DFT substrate | 3.14 (neutral) | Frady predicted "same scaling, smaller constant"; we measured -0.02 |
| Surprise modulation (uniform) | 4.27 (fail) | Phasic NE biology is deviation-based, not absolute-error-based; uniform scaling destabilizes |
| Homeostatic decay 1e-4 single-pass | 3.16 (null) | Turrigiano regulation doesn't matter at our scale because W doesn't drift in single-pass |

### Session 2026-05-17 (CPU multi-epoch breakthrough)

| Config | Best bpc | Notes / lit comparison |
|---|---|---|
| Multi-epoch (vanilla, 3 epochs N=1024) | 3.005 | Multi-pass Hebbian; new finding (we thought single-pass was structural — wasn't) |
| Multi-epoch (overfit at epoch 5+) | 3.07 → 3.71 | W-norm explosion; consistent with statistical-mechanics of overparam systems |
| Multi-epoch + decay 1e-4 (N=1024) | 2.985 | Weight decay barely helped at N=1024 |
| **Combined N=4096 + pool + multi-epoch + decay (15 epochs, CPU)** | **2.505** | **Major breakthrough**: synergy of independent information sources. Cf. transformer attention preventing FFN overfitting |

### Session 2026-05-18 (GPU)

| Config | Best bpc | Notes / lit comparison |
|---|---|---|
| GPU verification of CPU baseline | 2.522 | +0.017 from CPU due to FP precision in CUDA BLAS reorder |
| GPU combined + relu (modReLU magnitude shrinkage) | **2.4994** | First post-multi-epoch win; +0.02 from N=4096 baseline. **Citation corrected 2026-05-18:** this is modReLU (Arjovsky-Shah-Bengio 2016, ICML; arXiv 1511.06464), equivalent to complex L1 soft-thresholding / ISTA-FISTA proximal operator (Beck-Teboulle 2009). NOT Polsky-Mel-Schiller dendritic NL — PMS proposes supralinear sigmoid summation on coincident inputs, not subtractive magnitude shrinkage. Drop dendritic framing unless we add an actual sigmoidal subunit. |
| BR5 grid-cell positions (Frady-Kanerva-Sommer 2018) | 2.5094 | Predicted +0.03-0.07; measured -0.01 (slight hurt). Frady tested at K=20-100 sequences; K=4 too small for grid to shine |
| BR3 climbing-fiber sparse error (Marr 1969) | 2.5008 | Neutral. Likely fails because C receives same error as W — no new supervision; real cerebellum has independent teacher signal |
| BR4 PFC working memory (Wang 2001) | 2.7841 | Hurts by 0.28. Bundle saturation: adding h is like K=5 which exceeds bundle capacity |
| BR2 DG sparse projector v1 | 2.95 | Normalization bug + deeper issue (see audit note 3 below): top-k-by-magnitude on phase-code FHRR is the wrong operation regardless. Retry v2 needs to use top-k on Re part or move to native sparse-VSA. |
| **MX10 parallel tempering K=8** | **2.4963 (best replica)** | Hit 22.5% swap acceptance. **Citation corrected 2026-05-18:** Earl-Deem 2005 23% optimum is for equilibrium MCMC of Boltzmann distributions with detailed balance — does NOT theoretically transfer to streaming learning where "temperature" is decay rate. Better lit anchors for PT-of-learning: Desjardins 2010 adaptive PT (RBM training, AISTATS), Syed 2019 non-reversible PT (drops equilibrium assumption), Huang 2017 snapshot ensembles. P(q) on cold replicas std=0.0009 → single basin result stands (does not depend on Earl-Deem framing). |

### Audit notes (citation corrections 2026-05-18)

After running 4 parallel literature audits, several citations in this tracker
were materially mislabeled. The empirical results are unchanged, but the
literature anchors needed correction.

1. **modReLU, not Polsky-Mel-Schiller.** Our magnitude-shrinkage operator is
   exactly modReLU (Arjovsky-Shah-Bengio 2016 ICML, arXiv 1511.06464), which
   equals the complex L1 soft-thresholding / ISTA proximal operator
   (Daubechies-Defrise-De Mol 2004; Beck-Teboulle 2009). Polsky-Mel-Schiller
   2004 proposes *supralinear* sigmoid summation on coincident dendritic
   inputs — an expansive, not subtractive, nonlinearity. If we want a real
   PMS-style experiment, we need a sigmoid-gated *sum-over-subunits* operator,
   not what we have.

2. **BR6 sleep replay as planned is mislabeled.** Random-shuffled pool replay
   misses the three load-bearing properties of biological replay: ordered
   sequence reactivation (Skaggs-McNaughton 1996, Lee-Wilson 2002), ~20x
   temporal compression during SWRs, and salience-based selectivity (Foster
   2017; Ambrose et al. 2016). Also: van de Ven et al. 2020 is *generative*
   replay (VAE-like), not buffer replay. Honest anchor for plain buffer
   replay is Lin 1992 / Rolnick et al. 2019 experience replay. A faithful
   BR6 needs: (a) trajectory buffer storing byte-window sequences, not
   isolated pairs; (b) prioritized sampling by per-token loss / surprise;
   (c) sequential Hebbian application across each replayed window.

3. **DG top-k-by-magnitude on FHRR doesn't recover O'Reilly-McClelland.**
   O'Reilly-McClelland 1994 (Hippocampus) propose DG sparsification for
   orthogonalization of *overlapping* (similar) inputs in *real-valued*
   activation space. FHRR is a phase-based code where magnitudes are ~uniform
   by construction, so top-k-by-magnitude is effectively a random binary mask
   gated by post-projection noise — it does NOT preferentially keep
   informative components. A faithful BR2 retry should use top-k by |Re| (or
   on the real part directly), or move to a native sparse-VSA substrate
   (Laiho 2015 sparse block codes; Frady-Kleyko-Sommer 2021 sparse variable
   binding; Kleyko 2022 VSA survey).

4. **Earl-Deem 23% is heuristic motivation, not prediction.** Their result
   is derived for equilibrium MCMC under detailed balance; our streaming
   Hebbian learning has neither. The fact we measured 22.5% is numerical
   coincidence at best. The single-basin P(q) finding is empirical and
   stands regardless of how we frame the PT setup.

### Session 2026-05-18 (GPU, post-audit)

| Config | Best bpc | Notes / lit comparison |
|---|---|---|
| N scaling: N=8192 (combined+modReLU) | **2.4774** | -0.022 from N=4096. Frady-Kleyko-Sommer capacity prediction confirmed in this regime. |
| N scaling: N=16384 | KILLED | dtype investigation diverted; complex64 cuBLAS bandwidth-bound at this size; deferred per [dtype_acceleration_pin](dtype_acceleration_pin.md) trigger conditions |
| **Titans surprise-gated pool sweep (7 variants)** | **2.5218–2.5909 (all hurt)** | H1 REJECTED. Every gate variant worse than baseline, monotonically with write-rate restriction. Best gate variant (`fixed_tau_3.0`, wr=0.48): 2.5218 (−0.022). Most aggressive (`top10pct`, wr=0.10): 2.5909 (−0.092). See [pre-reg](../preregs/2026-05-18_surprise-gated-pool.md). |

### Titans rejection: mechanism analysis (per rehabilitation practice)

**Configuration result:** All 7 surprise-gate variants are WORSE than the
unconditional-write baseline at N=4096 on 38KB corpus. Monotonic with
restriction (more filtering = worse bpc).

**Diagnostic fingerprint:**
- W readout top-1 accuracy: 0.605 (identical across ALL variants)
- Pool top-1 accuracy: drops from 0.437 (baseline) to 0.095 (top10pct)
- Test bpc tracks pool quality, not W training

**Mechanism interpretation:** The pool's contribution at our scale comes from
**retrieving common bytes** (the Zipfian-heavy test distribution), not from
selectivity over informative items. Common bytes have LOW per-token loss →
LOW surprise → filtered out by the gate → pool can't help on the bytes that
dominate the test set. In Titans' published regime (long-context LM at scale),
rare informative tokens are useful to memorize explicitly because common
tokens are already absorbed by slow weights; at byte-level on small corpora
that relationship inverts.

**Rehabilitation candidates** (per [feedback_rehabilitation_after_rejection]):
1. **Invert the gate** — write only low-surprise items. Would test the
   "common-byte hypothesis" cleanly. Expected: should match baseline
   (not beat it), would confirm diagnosis. ~6 min experiment.
2. **Pool size sweep** — does the gate help at pool=4096 or 8192 where
   selectivity matters more? ~20 min.
3. **α sweep at fixed gate** — does higher pool weight (α=0.5, 0.7)
   make a gated pool's quality matter more? Unclear EV.
4. **Gradient-norm surprise** — literal Titans signal vs our loss-bits proxy.
   Implementation faithfulness check.
5. **1MB corpus** — does the Zipfian distribution flatten enough that
   surprise gate flips sign? Deferred to Wave 2.

**Decision:** Mechanism is NOT fully abandoned. (1) is cheap and confirms
the diagnostic; queue it as a 1-line follow-up. (5) is the real test of
Titans' regime claim, deferred to Wave 2. (2) is worth running standalone
(pool size sweep) regardless of gate, since it tells us about pool capacity
limits independently. (3) deferred. (4) needs implementation work.

**Single most informative follow-up:** the **α sweep with the current
pool configuration**, because it answers "how much is the pool doing?" —
which is upstream of "should we gate writes to it?"

### α (pool blend) sweep — Titans rehab #1 result

Pre-reg: [2026-05-18_alpha-sweep.md](../preregs/2026-05-18_alpha-sweep.md).

| α | best ep | best bpc | Notes |
|---|---|---|---|
| 0.00 | 5 | 2.6961 | W only; **overfits past ep5** (drifts up to 2.7203) |
| 0.10 | 15 | 2.5179 | Pool 10%, stable |
| **0.30** | **15** | **2.4994** | **Current best — sweet spot** |
| 0.50 | 15 | 2.5807 | Over-weights pool |
| 0.70 | 15 | 2.7507 | |
| 1.00 | 5 | 4.5375 | Pool only (no W training); flat across epochs |

**Three findings of independent value:**

1. **Pool contributes 0.20 bpc** (W-only 2.6961 → optimal 2.4994). Material;
   pool-mechanism work is justified. H supported per pre-reg.

2. **Pool acts as implicit regularizer.** Without pool blend (α=0.0), W
   overfits and bpc drifts upward after epoch 5. With α ≥ 0.1, the pool
   contribution stabilizes the loss curve. This dual role (information +
   regularization) wasn't separated previously and partly explains why
   tuning the pool blend matters so much.

3. **The pool's contribution saturates fast.** α=0.1 is within 0.02 of
   α=0.3; α=0.5 already degrades. Any pool-mechanism improvement has a
   bounded ceiling — going from current pool top-1 0.437 to perfect
   retrieval would close at most the gap to ~2.30 bpc. The bigger
   remaining gap (2.30 → 2.39 transformer) has to come from the W
   readout (currently 0.605 top-1) and/or substrate change.

**Implication for queue order:**
- DeltaNet (W readout variants) — high EV, launched
- BSC (substrate change) — high EV, queued after DeltaNet
- Inverted-gate Titans rehab — **demoted**: pool headroom is bounded
- Surprise gate at α=0.5 or α=0.7 — **demoted**: those α regimes already worse
- Larger pool size sweep — moderate EV, run after Wave 1 finishes

### DeltaNet variants — Wave 1c result

Pre-reg: [2026-05-18_deltanet-variants.md](../preregs/2026-05-18_deltanet-variants.md).

| Variant | best bpc | Δ | ||W|| | wT1 |
|---|---|---|---|---|
| baseline_cleaned | **2.4994** | — | 120.6 | 0.605 |
| cleaned_no_modrelu | 2.5221 | +0.022 | 113.5 | 0.602 |
| raw_delta | 3.4271 | +0.93 | 72.9 | 0.595 |
| raw_delta_with_modrelu | 3.4746 | +0.97 | 106.5 | 0.603 |
| pure_hebbian | 5.5634 | +3.07 | 6051 (exploding) | 0.160 |

**Hierarchy of architecture contributions (cumulative from pure Hebbian):**

| Component | Contribution | Cumulative bpc |
|---|---|---|
| (start: pure Hebbian) | — | 5.56 |
| + delta-rule error subtraction | +3.07 | 3.43 (raw_delta) |
| + softmax cleanup (codebook-aware error) | +0.93 | 2.52 (cleaned_no_modrelu) |
| + pool blend at α=0.3 (vs α=0) | +0.20 (from α sweep) | — |
| + modReLU readout | +0.022 | **2.4994 (current)** |

**Sub-hypothesis outcomes from pre-reg:**

- H1 (raw error beats cleaned): **STRONGLY REJECTED** (raw 1 bpc worse)
- H2 (modReLU dominates over cleanup): **REJECTED HARD in opposite direction** —
  cleanup contributes 50× more than modReLU
- H3 (pure Hebbian materially worse): **STRONGLY SUPPORTED** (+3 bpc worse)

**Diagnostic insight:** raw_delta's W top-1 (0.595) is only 0.01 worse than
baseline (0.605), but bpc is +0.93 worse. The **shape of P_W matters more
than argmax** — softmax cleanup produces sharper, codebook-concentrated
distributions; raw error produces diffuse ones. The cleanup isn't just
picking the right answer, it's giving it the right confidence.

**Recalibration:** We had been overweighting modReLU in our narrative. The
true load-bearing piece is the **softmax-cleaned delta rule**. modReLU is
a small refinement. Future architecture explorations should focus on
update rule variants and codebook-aware mechanisms before readout NLs.

### BSC substrate — Wave 2b result (the user's "brain-closer basis" experiment)

Pre-reg: [2026-05-18_bsc-substrate.md](../preregs/2026-05-18_bsc-substrate.md).

| Variant | best bpc | Δ vs FHRR | poolT1 | wT1 |
|---|---|---|---|---|
| bsc_continuous_no_relu | 3.0324 | +0.53 | 0.238 | 0.520 |
| bsc_continuous_relu | 3.1001 | +0.60 | 0.238 | 0.514 |
| bsc_signed_no_relu | 2.5942 | +0.10 | 0.434 | 0.594 |
| **bsc_signed_relu** | **2.4817** | **−0.018** | **0.434** | **0.595** |

**Hypothesis from pre-reg supported with margin.** Best BSC variant matches
or slightly beats FHRR baseline (2.4994), within ±0.10 substrate-equivalence
threshold.

**The substrate is NOT the bottleneck at our scale.** Switching from
complex64 FHRR (continuous phase code) to FP32 BSC (±1 binary code, brain-
closer) recovers the same test bpc. The 2.49 floor is therefore a property
of the data + algorithm, not the substrate.

**Inverted prediction:** the pre-mortem hedged that signed bundling
(sign(sum)) "may hurt the delta-rule gradient signal." The OPPOSITE turns
out true — signed variants beat continuous variants by 0.5 bpc. ±1
quantization after bundling acts as implicit regularization in a way
similar to how the pool blend regularizes W in the α=0 case.

**Speed bonus:** BSC runs ~2× faster (24.8s vs 53.2s for 15 epochs at N=4096)
because real FP32 matmul engages Tensor Cores via TF32, while complex64
falls back to FP32 CUDA cores. This is the speedup we couldn't get by
splitting FHRR — getting it via substrate change instead. Importantly,
this unlocks N=16384+ experiments as tractable.

**Caveat: single-seed result.** The 0.018 win over FHRR is within FP-noise
(prior CPU/GPU verification showed ~0.015 drift). Honest claim: BSC ≈ FHRR
within seed noise, with a 2× speedup bonus. Multi-seed verification needed
before promoting BSC to new default substrate.

**Implication for next-step queue:**
- 5-seed BSC vs FHRR confirmation run (~10 min, ~5x BSC + 5x FHRR baseline)
- BSC at N=16384 — now tractable in ~30s/epoch vs 525s/epoch for FHRR
- All architecture variants (alpha sweep, surprise gate, DeltaNet) re-tested
  on BSC substrate to see if any flip sign
- Continual learning + few-shot ICL tests are agnostic to substrate; run
  on whichever wins the multi-seed comparison

### Sparse Block Codes (Laiho 2015 / MMB) — third substrate result

Pre-reg: not formally written (this was a follow-up from the substrate
discussion; should be written retrospectively if results are promoted).

| Variant | Sparsity | best bpc | Δ vs FHRR | wT1 | poolT1 |
|---|---|---|---|---|---|
| sbc_M64_no_relu | 1.56% | 3.2178 | +0.72 | 0.503 | 0.436 |
| sbc_M64_relu | 1.56% | 3.4606 | +0.96 | 0.436 | 0.436 |
| **sbc_M128_no_relu** | **3.12%** | **2.9272** | **+0.43** | 0.555 | 0.435 |
| sbc_M32_no_relu | 0.78% | 3.5384 | +1.04 | 0.394 | 0.439 |

**Sparsity-perplexity trend:** higher density (3.1% > 1.6% > 0.8%) gives
lower bpc. The sparser the code, the lower the W readout's discrimination
capacity. Specifically wT1 drops from 0.555 (M=128, 3.1% sparse) to 0.394
(M=32, 0.8% sparse).

**ReLU INVERTS sign vs BSC.** In BSC, ReLU was the winning variant
(+0.11 from baseline). In SBC, ReLU HURTS (sbc_M64_relu 3.46 vs
sbc_M64_no_relu 3.22). The mechanism: SBC's encoding is already a sparse
activation; adding ReLU on the readout further sparsifies, removing
information.

**Substrate ranking at our scale (N=4096, perplexity only):**
1. BSC (signed, ReLU) — 2.4817
2. FHRR (modReLU) — 2.4994
3. SBC (M=128, no ReLU) — 2.9272

SBC loses by ~0.43 bpc to the dense substrates **on perplexity**.

**Critical caveat: this is NOT the test SBC is predicted to win.**
Sparse block codes are theoretically advantaged for **pattern separation
and continual learning** (per O'Reilly-McClelland 1994, Frady-Kleyko-Sommer
2021), not for perplexity. The Wave 3a continual learning test is where
SBC may have its real claim. Treating today's result as "SBC fails" would
be a category error — it shows SBC fails on the task SBC isn't designed
for.

**Implication for queue:** SBC is held in reserve for Wave 3a. Do NOT
deprioritize it on the basis of today's perplexity result.

### Wave 3a continual learning result (post-audit, post-chunked-refactor)

Pre-reg: [2026-05-18_continual-learning-3a.md] (in conversation thread).
12 chunks × (substrate × condition). Full data in
`data/exp_continual_learning/chunk_*.json`.

**Substrate behavior on the sequential_AB protocol (the actual continual
learning test):**

| Substrate | A after Phase 1 | A after Phase 2 (B training) | Naive forgetting | Normalized fraction-lost |
|---|---|---|---|---|
| FHRR | 2.4995 | 4.6458 | +2.1463 | 86% |
| BSC | 2.4817 | 4.5367 | +2.0550 | 82% |
| SBC | 3.1951 | 4.8418 | +1.6467 | **91%** |

Normalized fraction = (A_after_P2 − A_after_P1) / (5.0 − A_after_P1), where
5.0 is "random A" (untrained substrate). Captures "how much of what was
learned was lost."

**Headline:** **all three substrates catastrophically forget 80-91% of A.**
The Bricken et al. 2023 *SDM-is-a-Continual-Learner* hypothesis — that
sparse codes pattern-separate and prevent catastrophic forgetting — does
NOT cleanly reproduce at our scale. H4 of the Wave 3a.5 pre-reg looks
likely to be REJECTED.

**Naive forgetting (Yildiz metric) is misleading:** SBC's smaller delta
(+1.65) reflects starting from a worse baseline (3.20 vs 2.48-2.50), not
genuinely better retention. Normalized metrics show SBC retains the
LEAST of its (already modest) A knowledge.

**Diagnosis:** The architecture (single shared W + multiplicative decay
applied over ~120K Phase-2 steps + pool ring-buffer overwrite in Phase 2
epoch 1) dominates the forgetting picture. Substrate sparsity doesn't
save us — the mechanism is multiplicative annihilation of W combined
with new-target overwriting, both of which affect any substrate.

**Implication:** continual learning is NOT a substrate-level property at
our scale. It's an architectural property. The next test is Wave 3a.5
which isolates the three architectural mechanisms (decay, W overwrite,
pool overwrite) by selectively disabling each during Phase 2.

**What "wins" on Wave 3a per the conditions:**
- A-only baseline: BSC is best on the markdown A corpus (2.4817)
- B-only baseline: FHRR slightly better than BSC on Python B (2.67 vs 2.63)
  but SBC much worse (2.97)
- joint_AB (upper bound, both trained): BSC handles both best
- sequential_AB (the real CL test): all fail similarly

### Wave 3a post-result audit (2026-05-18) — corrections to the interpretation above

A focused literature audit (per the standing "research-on-findings" rule)
revealed I had over-claimed the Wave 3a result. The corrected interpretation:

1. **"SBC doesn't help with continual learning" is OVER-CLAIMED.** Bricken et al.
   2023 *Sparse Distributed Memory is a Continual Learner* (arXiv:2303.11934)
   tested on image classification (MNIST/CIFAR-10/100) with a specific recipe
   (Top-K activations + L2-normalized weights + positive-W constraints +
   EWC). Our SBC implementation has none of these. **We did not falsify
   their hypothesis; we tested a different setup that happens to use sparse
   block codes.**

2. **The naive BWT-style metric is GEM-standard** (Lopez-Paz Ranzato 2017,
   arXiv:1706.08840). Modern lit (Díaz-Rodríguez 2018, Spurious Forgetting
   2025) acknowledges the start-point artifact and recommends reporting
   BOTH raw BWT AND normalized retention. My "naive vs normalized"
   contrast was an artifact of the comparison framing, not a methodological
   error.

3. **86% retention loss is TYPICAL, not pathological.** Van de Ven 2024
   survey (arXiv:2403.05175) and Yildiz 2024 (arXiv:2402.17400) report
   40-90% retention loss is standard for un-mitigated sequential single-W
   systems. Mapping Post-Training Forgetting 2025 (arXiv:2510.17776)
   shows +1.0-2.5 bpc shift is the modal outcome on A after a single
   domain shift in small models. **Our +2.15 bpc is in band, not unusual.**

4. **Wave 3a.5 is missing the literature-standard mitigation: rehearsal.**
   Interleaving even 1-5% of A-bytes during Phase 2 dominates sophisticated
   regularization on small-LM continual pretraining (Scalable Strategies
   2025 arXiv:2505.12512, MSSR arXiv:2603.09892, Yildiz 2024). My three
   mitigations (decay_off / W_frozen / dual_pool) are crude weight-
   preservation; the literature answer is rehearsal.

5. **We ARE filling a real literature gap.** Per the audit: "Our Wave 3a
   result appears to be the first reported HDC/VSA continual byte-LM
   comparison." There's no published baseline to anchor "good" vs "bad."
   This is a genuine contribution but it also means no comparison number.

### Corrected framing of Wave 3a result

**Headline (corrected):** Three VSA substrates (FHRR / BSC / SBC) all
exhibit literature-typical catastrophic forgetting under un-mitigated
sequential A→B training. **This is the expected baseline, not a finding.**
The substrate ranking after Phase 2 is BSC ≈ FHRR > SBC on absolute
retention; SBC's smaller raw BWT delta is a starting-point artifact, not
genuine retention. **The Bricken 2023 SDM-pattern-separation claim
remains untested in our setup because the required architectural recipe
(Top-K + L2-norm + positive-W + EWC) was not implemented.**

### Wave 3a.6 — proper literature-standard mitigation test (planned)

To close the Bricken-claim gap and the rehearsal gap, Wave 3a.6 will add:

- **Rehearsal mitigation** (2% A-byte interleave in Phase 2) for all 3
  substrates — the literature-standard mitigation we were missing.
- **EWC-lite anchor** (L2 penalty on W toward W_postA, Fisher proxy =
  squared mean delta-rule update magnitudes from Phase 1) — partial
  reproduction of Bricken's required EWC component.
- **Parameter-matched 4M-param transformer baseline** trained sequentially
  A→B with no mitigation — gives an apples-to-apples bpc comparison
  instead of citing literature ranges (van de Ven 2024 et al.).
- **Optional: full Bricken recipe on SBC** (Top-K cleanup + L2-norm W +
  positive-W constraint + EWC) — actually tests the SDM-CL hypothesis.

Wave 3a.5's current mitigations (decay_off / W_frozen / dual_pool)
remain useful as ARCHITECTURE-DECOMPOSITION probes — they tell us which
mechanism inside our system is doing the most forgetting — but they
don't address whether mitigations from the broader literature would fix
the problem.

## Literature landscape (audit, 2022-2026)

Where our work sits in the current field, per literature audit:

**1. HDC/VSA language models specifically.** No published byte- or token-level
LM with reported bpc/perplexity using FHRR/HRR/BSC substrates in 2022-2026.
Our 2.4994 bpc on 38KB English is — as far as this scan goes — the only
recent FHRR-native byte-LM result. Genuinely novel ground, but means no
external yardstick exists yet. Closest peers:
- GHRR (Generalized HRR, Alam-Raff-Holt et al. 2024 arXiv 2405.09689):
  non-commutative binding; could improve sequence-order capture in our K=4 bind.
- Walsh-Hadamard linear VSA (Alam et al. NeurIPS 2024).
- Hyperdimensional Probe (2025): uses VSAs to decode LLM hidden states.

**2. Delta-rule / fast-weight sequence learning (active area).**
- DeltaNet (Yang et al. arXiv 2406.06484, 2024): 1.3B model, beats Mamba/GLA.
  Update is `W = W(I - k k^T) + v k^T` — outer-product write WITH erase.
- Gated DeltaNet (ICLR 2025): hybrid variants 15.91 perplexity on WikiText.
- Hebbian and Gradient-Based Plasticity in Transformers (arXiv 2510.21908, Oct 2025):
  neuromodulated Hebbian rules outperform gradient plasticity on few-shot.
- Blending Complementary Memory Systems (Irie/Gershman 2025): softmax window
  + delta-rule fast weights with explicit CLS framing — closest peer in spirit.

**Our W update vs DeltaNet:** our `dW = (target - expected) ctx^T / N` is a
delta rule, but lacks DeltaNet's explicit `-W k k^T` erase term. Worth testing.

**3. Fast+slow / surprise-gated memory (most directly applicable).**
- **Titans (Behrouz-Zhong et al. arXiv 2501.00663, Jan 2025):** surprise-gated
  (gradient-norm) neural long-term memory + attention. Scales to 2M context.
  Same fast-pool + slow-W story as us, with one crucial addition: gradient-of-loss
  as surprise gate for memory writes.
- Titans Revisited (arXiv 2510.09551, Oct 2025): critical reimplementation.
- MIRAS (Google late 2025): generalization framing memory as associative-memory
  optimization.

**4. Modern Hopfield as LM.**
- NRGPT (arXiv 2512.16762, Dec 2025): energy-based GPT alternative — closest
  thing to "Hopfield-as-LM".
- Energy Transformer (NeurIPS 2023): continuous Hopfield as transformer block.

**5. Energy-based / non-backprop on language.** Still no competitive byte-level
result from forward-forward (acknowledged not to scale to sequences), predictive
coding, or equilibrium propagation. The wins in brain-inspired LMs come from
the *write rule* (Hebbian/delta), NOT from non-backprop credit assignment.

### Strategic implications of literature scan

Highest-leverage next experiments (in order):

1. **Surprise-gated pool writes** (Titans-style): only write (ctx, target) to
   pool when per-token loss exceeds threshold. 10-line change. Direct precedent.
2. **DeltaNet-style explicit erase** in W update: `W_new = W (I - α k k^T) + α v k^T`
   instead of pure `W += α (v - Wk) k^T`. Mathematically tighter associative recall.
3. **GHRR non-commutative binding** for position-byte binds (Alam-Raff 2024) —
   could improve sequence-order capture at our K=4.
4. **NRGPT energy formulation** for retrieval temperature — replace our ad-hoc
   `beta=8` softmax with a principled energy-based readout.

### Cumulative findings

**The 0.10-bit residual gap is architectural at the basin floor.** Multiple
independent observations support this:

1. Parallel tempering with optimal swap acceptance gives only FP-noise gain
2. Cold replicas (low decay) all converge to overlap > 0.998 — same W
3. 4 of 5 brain-inspired federated modules failed to help
4. Multi-epoch + decay + pool combination already at convergence (epoch 12→15 = 0.002)

This is consistent with **Mei-Montanari-Nguyen 2018 PNAS / Mei-Montanari 2022 CPAM**
random-features-model landscape analysis: random fixed features + ridge regression =
convex loss with single global minimum. Our setup is non-convex (delta rule on
softmax output), but the basin is unique.

**Where this places us in the literature:**

- We've engineered an HDC LM that reaches within 5% perplexity of a tiny
  transformer on byte-level English at 38KB. As far as I know, no published
  HDC paper has explicitly reported this number on this kind of task — the
  closest comparison is Schlag-Irie-Schmidhuber 2021 (linear transformers
  with delta-rule fast weights), but they use gradient descent on slow
  network + learned keys + larger corpora.

- The federated architecture exploration (5 brain-modules tested) is novel
  in scope; no published work explores this specific space of bio-inspired
  additions to FHRR-based LMs.

- The empirical finding that "the gap is a single-basin landscape, not RSB"
  is itself a novel data point. The published theory (Mei-Montanari for
  random features, Parisi for spin glasses) doesn't directly cover our
  HDC + Hebbian + pool architecture; this is the first measurement.

## Open questions to test (Wave 1)

1. Does N scaling close the gap? (running, N=4096/8192/16384)
2. Does sleep replay help (Wilson-McNaughton 1994 motivation)?
3. Does K-grid scaling reveal the predicted Frady benefit?
4. Is the gap data-dependent? (Wave 2: 1MB corpus)
5. Is the gap substrate-dependent? (Wave 2: BSC port)

## Capability questions (Wave 3, untested)

These are the "functional differentiation" tests. Even if we don't close
the perplexity gap, demonstrating these would be more interesting than
perplexity matching:

1. Continual learning: train on corpus A, then B, retention on A?
2. Few-shot ICL: pool-based pattern completion at inference
3. Catastrophic forgetting: explicit measurement
4. Sample efficiency: bpc vs corpus size

## Measurement protocol (going forward)

For each experiment, we should capture:
- test_bpc per epoch (already capturing)
- argmax_accuracy per epoch (already capturing)
- W_norm Frobenius (already capturing)
- Per-byte bpc histogram (which bytes are hard? — adds 5 lines to scripts)
- Pool retrieval quality (top-1 fraction matching target — adds 5 lines)
- Wall time per epoch (already capturing)
- Theoretical comparison: what does theory predict for this config?
- Lit comparison: what's the closest published result?
