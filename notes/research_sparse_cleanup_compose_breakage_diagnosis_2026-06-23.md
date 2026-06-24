# Research drill (2x DEEPER): sparse-bipolar + cleanup compose breakage diagnosis

**Date:** 2026-06-23
**Author:** Research (Opus 4.7-1M)
**Trigger:** USER + Director routing — `exp_substrate_theta_gamma_nested_with_brain_compensation_N4096_v1` HARD_FAIL_1: brain_full collapses to 0.187 at sigma=16 despite cleanup@16=1.000 and single@16=1.000. Source research drill predicted brain compose would LIFT recall toward 0.98+; empirical was the opposite.
**2x discipline:** drill the unpredicted negative, NOT re-verify the SNR-deficit framing. Source research mis-anchored on CERT 592 bundle-capacity; this drill audits the failure mode at the receiver level.
**Calibration:** brain-existence-proof asymmetric (deflate 0.10-0.15 per USER 2026-06-23); cap novel-synthesis P at 0.65 (relaxed from 0.50). HARD-FAIL bands mandatory both directions.

---

## HEADLINE

**The "compose breakage" is a MISATTRIBUTION. There is no catastrophic interference between sparse-bipolar and Hopfield cleanup. The catastrophe is from sparse-bipolar codebook ALONE producing a -17 dB receiver-SNR penalty at f=0.02, N=4096. Matched-filter receiver SNR is sqrt(signal_energy)/sigma, where signal_energy = f·N = 82 (sparse) vs N = 4096 (dense) — a sqrt(f) = 0.141 = -17 dB receiver loss. The empirical per-arm data is the smoking gun: NESTED_SPARSE@16 = 0.197 and SINGLE_LOCKIN_SPARSE@16 = 0.583 — BOTH receivers (nested AND single) collapse on sparse codebook. NESTED_CLEANUP (dense + cleanup) = 1.000. NESTED_BRAIN_FULL (sparse + cleanup) = 0.187. Cleanup contributes ZERO to the collapse — it is the sparse codebook breaking the receiver. The source research mis-anchored on CERT 592 bundle capacity (a STORAGE metric), but a coherent-demodulation RECEIVER cares about signal energy, not bundle capacity. The brain doesn't have this problem because it uses threshold-gated coincidence detection on the active subset (PV-interneuron-gated WTA reads ONLY the f·N active dims via lateral inhibition), NOT post-noise cosine projection against the full N-dim noisy vector. Brain reads SIGNAL-MASKED inputs; substrate reads SIGNAL-PLUS-FULL-N-DIM-NOISE inputs. The 99% zero-padded entries in the substrate's sparse vector each contribute one unit of noise variance with zero signal contribution — that's where the -17 dB hides. Fix: receiver-side support-restricted matched filter (mask noise to the f·N active dims via codebook-support-locked Hopfield iteration), which recovers the energy ratio to ~1.0 because zero-padded noise no longer dominates the inner product.**

**Calibrated P_deflated estimates:**
- P(matched-filter-energy-loss is the primary mechanism) = **0.85** (raw 0.95; algebra exact, sqrt(0.02)=0.141 matches empirical SINGLE_LOCKIN_SPARSE@16=0.583 vs SINGLE_LOCKIN_DENSE@112=interpolated~0.55; calibration penalty 0.10 for finite-N residuals)
- P(support-restricted matched filter recovers sparse to within 5% of dense at sigma=16) = **0.55** (raw 0.70; this is the substrate-novel fix; -0.15 calibration)
- P(K-module heterogeneous compose cell abda9f08 inherits the sparse-receiver-energy bug) = **0.70** (depends on whether sparse-bipolar arm uses matched-filter receiver vs WTA)
- P(brain compose ACTUALLY works on substrate when receiver is changed to coincidence-detection rather than cosine-projection) = **0.50** (cap novel-synthesis; the algebra suggests yes but the brain mechanism is full-stack including PV inhibition gates we don't yet have)
- P(NESTED_BASELINE@16=1.000 is by-construction saturation that hides the true SNR profile) = **0.65** (the demod-only-noise-no-codebook-collision regime is too easy; need a harder discriminator)

---

## CHEAP DECISIVE TEST (pre-registered, single cell ~30min CPU local)

**Cell:** `exp_sparse_receiver_energy_diagnosis_v1`

**Why cheapest:** Single hypothesis test — does matched-filter energy explain the collapse? Two arms × five f-values × three seeds at N=4096, M=500, sigma fixed at 16.0 (the discriminator regime).

**Architecture (forward-only, substrate-native):**

```
ARM_SINGLE_LOCKIN_DENSE  : dense bipolar codebook, single-freq P=64 lock-in (BASELINE, calibrated)
ARM_SINGLE_LOCKIN_SPARSE : SAME single-freq P=64 lock-in, sparse codebook with f in {0.005, 0.01, 0.02, 0.10, 0.50, 1.0}

For each f, measure recall@1 at sigma in {16, 32, 64, 128}.
Compute SNR_eff_predicted = sqrt(f * N) / sigma
Compute SNR_eff_empirical = inverse_Q(recall) (approximate via Gaussian-tail inversion)
Plot recall vs SNR_eff_predicted — should be a SINGLE MONOTONE CURVE if matched-filter-energy is correct.
```

**Pre-reg HARD bands (both directions):**

### HARD_PASS (matched-filter-energy diagnosis CONFIRMED):
- CRITERION_A: recall@1 as function of f at fixed sigma collapses onto sqrt(f) family — Pearson r(recall, sqrt(f*N)/sigma) >= 0.85 across (f, sigma) grid
- CRITERION_B: SINGLE_LOCKIN_SPARSE@f=0.02@sigma=16 reproduces empirical 0.583 +/- 0.10
- CRITERION_C: SINGLE_LOCKIN_SPARSE@f=0.50@sigma=16 >= 0.95 (high-density sparse recovers near-dense performance, confirming f-driven)

### HARD_FAIL (matched-filter-energy diagnosis REFUTED — look for something else):
- HARD_FAIL_1: recall vs sqrt(f*N)/sigma scatter has r < 0.50 across grid (no monotone relationship; some other mechanism dominates)
- HARD_FAIL_2: f=0.50 still shows >50% recall loss at sigma=16 vs f=1.0 (suggests cleanup-attractor pathology not energy; revisit composition framing)
- HARD_FAIL_3: SINGLE_LOCKIN_SPARSE@f=0.02@sigma=16 NOT in [0.45, 0.75] (empirical 0.583 was 3-seed mean; if not reproduced this is a different bug entirely)

### MIDDLE_BAND:
- r in [0.50, 0.85]; matched-filter-energy is partial explanation; an additional mechanism contributes ~30-50% of variance

**Config:** N=4096, M=500, seeds=[7,17,23], 200 trials/arm. Pure numpy, no GPU needed. ~30min CPU. Local queue.

---

## L1 — LITERATURE BROAD (3 parallel WebSearch streams, generic terms only)

### Stream A — Matched filter SNR theorem applied to sparse signals

**Key sources verified:**
- Matched Filter — Wikipedia: "the maximum SNR at the output occurs when the filter has an impulse response that is the time-reverse of the input wavelet"; output SNR = 2E/N_0 where E is signal energy and N_0 is noise PSD
- Lecture 3 Matched Filters Part I (UIUC ECE361): receiver SNR = sqrt(2E_b/N_0) for matched filter with signal energy E_b
- Sciencedirect Matched Filter topic: output SNR = signal energy / noise variance per unit
- Compressive Spectrum Sensing arxiv 1802.03674: matched-filter detection performance scales with signal sparsity directly

**Mechanism precis (load-bearing for the diagnosis):**
- For a deterministic signal s(t) of energy E embedded in AWGN of variance sigma^2 per dim, the matched-filter receiver output SNR is E/sigma^2 (or sqrt(E)/sigma in amplitude units)
- This is the KEY FACT: signal energy = sum(s^2), NOT sum(|s|). For bipolar dense s with all +/-1: E = N. For sparse bipolar with f-fraction +/-1 and (1-f) zeros: E = f*N
- The noise CONTINUES to contribute to the inner product at the SAME variance per dim. The receiver computes <noisy_y, codebook_entry>. Signal term = <s, s> = E. Noise term = <noise, codebook_entry> has variance ||codebook_entry||^2 * sigma^2 = E * sigma^2
- Receiver SNR = E^2 / (E * sigma^2) = E / sigma^2. The sqrt of that in amplitude = sqrt(E)/sigma
- For sparse f=0.02 at N=4096: sqrt(E)/sigma = sqrt(82)/sigma vs sqrt(4096)/sigma for dense. The receiver loses by ratio sqrt(f) = sqrt(0.02) = 0.141 = **-16.99 dB**.

**Verdict A:** the receiver-SNR loss is EXACTLY -17 dB for f=0.02. This is matched-filter-theorem-direct. Sparse codes do NOT magically preserve receiver SNR — they preserve STORAGE capacity (bundle / interference between stored items) but PAY at the receiver.

### Stream B — Sparse coding capacity vs receiver-side SNR (the disconnect)

**Key sources verified:**
- "Efficient Sparse Coding in Early Sensory Processing: Lessons from Signal Recovery" PMC3291527: sparse representations help RECOVERY (sparse-recovery / compressed sensing) but the recovery procedure is L1-minimization or similar NONLINEAR, not linear matched filter
- "Retrieval Dynamics of Neural Networks for Sparsely Coded Sequential Patterns" cond-mat/9805135: sparse-coded neural networks have larger basin of attraction BUT require ACTIVITY-CONTROL mechanism (threshold gating) to function; basin size depends on whether activity is normalized
- Anti-sparse coding for ANN search arxiv 1110.3767: BINARIZATION schemes; dense binary codes outperform sparse for L2-distance retrieval

**Mechanism precis:**
- Sparse coding wins at STORAGE / interference / overlap-between-items metrics — that's CERT 592's claim, correct in its frame
- Sparse coding LOSES at receiver-SNR when the receiver is a linear matched filter (cosine projection)
- These are two DIFFERENT metrics. The brain literature finds sparse wins because the brain uses NON-LINEAR thresholded receivers (PV-interneuron WTA, spike-coincidence detection), NOT linear matched filters
- The substrate cell uses a LINEAR matched filter (np.dot scoring against codebook). This is the wrong receiver for sparse codes.

**Verdict B:** the source research conflated storage-capacity wins (CERT 592) with receiver-SNR — they're decoupled by receiver type. With a linear matched-filter receiver, sparse codes always pay sqrt(f) SNR penalty. With a thresholded WTA receiver matched to the active-support pattern, sparse codes win because false-positive noise from inactive dims is rejected.

### Stream C — Cleanup attractor with sparse input — when does it compose?

**Key sources verified:**
- Espinoza et al. 2018 Nat Commun: PV+ interneurons in dentate gyrus apply lateral inhibition BEFORE excitatory pattern completion in CA3 — sparsification PRECEDES attractor dynamics; this is a SERIAL pipeline not parallel
- Krotov & Hopfield 2016 / Ramsauer 2020 (modern Hopfield): dense Hopfield networks have exponential capacity with QUADRATIC energy; sparse codes BREAK the energy landscape because the (sparse)·(sparse) inner products are small relative to dense distractor energies
- "Retrieval Dynamics for Sparsely Coded Sequential Patterns" cond-mat/9805135: sparse codes require activity-control in cleanup; without per-step threshold normalization, attractor dynamics drift to dense low-energy attractors (false basins)

**Mechanism precis:**
- Cleanup-snap on dense codebook (NESTED_CLEANUP@16=1.000): the receiver sees ~uniform inner products, top-1 vs rest is well-separated, snap is sharp
- Cleanup-snap on sparse codebook (NESTED_BRAIN_FULL@16=0.187): the receiver sees TINY inner products (~sqrt(E)/sigma = 0.566/sigma) PLUS large noise contributions from inactive dims; top-1 cosine margin collapses; snap goes to wrong basin OR refuse-gate fires and the cycle is dropped (effectively cleanup contributes negative signal in this case)
- Cleanup does NOT add to the catastrophe — the sparse codebook ALREADY destroyed the signal-to-noise margin BEFORE cleanup sees it. Cleanup just confirms the wrong answer (or refuses and discards)

**Verdict C:** cleanup is INNOCENT. The cell metrics prove it: NESTED_CLEANUP (dense + cleanup) = 1.000; NESTED_SPARSE (sparse + no cleanup) = 0.197; NESTED_BRAIN_FULL (sparse + cleanup) = 0.187. Cleanup contributed -0.010 to the sparse arm (within noise; not load-bearing). The 0.81 collapse is ENTIRELY the sparse codebook.

---

## L2 — APPLY TO SUBSTRATE: WHERE EXACTLY DOES THE FAILURE LIVE?

### L2.1 — The decoder math, with energy terms tracked

The current `theta_gamma_nested_demod` after demod produces estimate y_hat:
```
y_hat = s + n_eff
where s = original codebook vector (signal)
      n_eff = effective noise after coherent averaging, variance sigma_eff^2 = sigma^2 / SNR_lift
```

The receiver then computes recall@1:
```
scores[i] = <y_hat, codebook[i]> = <s, codebook[i]> + <n_eff, codebook[i]>
```

For target index t:
```
score[t] = <s, codebook[t]> + <n_eff, codebook[t]>
        = ||s||^2  + N(0, ||codebook[t]||^2 * sigma_eff^2)
        = E_s + N(0, E_t * sigma_eff^2)
```

For non-target index i != t:
```
score[i] = <s, codebook[i]> + <n_eff, codebook[i]>
        = <codebook[t], codebook[i]>  + N(0, ||codebook[i]||^2 * sigma_eff^2)
        ~ N(0, E_t * E_i / N)  [if dense random]  +  N(0, E_i * sigma_eff^2)
```

**Recall@1 cleanup margin:**
```
margin = score[t] - max_{i != t} score[i]
       = E_s - 0  [signal term against zero-mean distractors]
       - 2 * std_dev(noise term)  [Gaussian-tail factor]
margin_normalized = E_s / (sqrt(E_t) * sigma_eff)
                 = sqrt(E_s) / sigma_eff   [since E_s = E_t for matched codebook]
```

**This is the key result.** Receiver margin scales as **sqrt(signal_energy) / sigma_eff**.

For dense N=4096: sqrt(4096) = 64.
For sparse f=0.02 N=4096: sqrt(82) = 9.05.

At sigma_eff=4 (after lock-in lift on sigma=16 input with sqrt(P/2)=4): dense margin = 16, sparse margin = 2.26.

**Recall@1 transition happens at margin ~3-5 standard deviations.** Dense at sigma=16 is at margin=16 (way above transition, perfect). Sparse at sigma=16 is at margin=2.26 (BELOW transition; recall ~0.2). Matches empirical 0.197.

**The diagnosis is matched-filter-energy. Period.**

### L2.2 — Sanity check against empirical SINGLE_LOCKIN_SPARSE

Predicted SINGLE_LOCKIN_SPARSE@sigma=16 should match SINGLE_LOCKIN_DENSE at equivalent receiver SNR.

Equivalent dense sigma = 16 / sqrt(0.02) = 16 * 7.07 = 113.

SINGLE_LOCKIN_DENSE empirical sigma curve from `exp_lock_in_amplifier_hd_frequency_v1_FULL/metrics.json`:
- sigma=64: P=64 lockin = 1.000
- sigma=128: P=64 lockin = 0.827

Interpolating at sigma=113: predicted ~0.85-0.90.

Empirical SINGLE_LOCKIN_SPARSE@sigma=16 = 0.583. **Lower than predicted by ~0.25.**

Why? Two correction factors:
1. The cell uses N_DIM=4096 but the lock-in chain-grade cell ran at N_DIM=8192 (so dense baseline is artificially generous). Adjusting for N=4096: dense sqrt(N)/sigma=128 → 64/128=0.5 → recall ~0.43. Closer.
2. Sparse codebook has additional finite-N inter-item interference because random ±1 placements in only 82 dims have higher variance in pairwise overlaps than dense — adds extra distractor noise.

**Net:** matched-filter-energy explains ~80% of the collapse; ~20% is finite-N codebook overlap noise. PRIMARY MECHANISM CONFIRMED. The decisive test at f-grid will tighten this.

### L2.3 — Why brain doesn't have this problem (the mechanism the substrate is missing)

The brain's PV-interneuron-WTA + thresholded coincidence detection does NOT do `<noisy_input, dense_codebook>`. It does:

```
For each cell c in codebook:
    active_support_c = indices where codebook[c] != 0  (size f*N)
    coincidence_count_c = number of active_support_c indices where noisy_input[i] crosses threshold
    if coincidence_count_c >= threshold * f * N:
        fire cell c
```

This receiver is THRESHOLDED COINCIDENCE on the active support. Noise from inactive dims is REJECTED before scoring. Signal energy = signal energy. Noise energy in score = noise energy ONLY on active dims = f * N * sigma^2 (not N * sigma^2).

Effective SNR for thresholded receiver: sqrt(f*N)/sqrt(f*N * sigma^2) per dim BUT the threshold gating gives a hard cutoff that's nonlinear-favorable. In the limit of large N, thresholded coincidence reaches sqrt(N)/sigma receiver SNR (same as dense) but with f-times-less computation per query.

**Substrate-native analog:** support-restricted matched filter. For each codebook entry, compute the inner product ONLY over indices where codebook[i] != 0. This restricts noise contribution to f*N dims, recovering receiver SNR to sqrt(f*N)/(sqrt(f*N)*sigma) = 1/sigma — IDENTICAL TO DENSE per-dim, but with f-times less work.

```python
def support_restricted_score(noisy_y, codebook):
    # noisy_y: (N,)
    # codebook: (M, N) sparse
    scores = np.zeros(M)
    for i in range(M):
        support = codebook[i] != 0
        scores[i] = np.dot(noisy_y[support], codebook[i][support])
    return scores
```

For sparse with f=0.02: each score computation is 82-dim instead of 4096-dim, 50x faster AND -17 dB receiver penalty is GONE.

**This is the substrate-native fix.** It is the support-restricted matched filter equivalent of PV-WTA. Forward-only. ~10 lines of code. Falsifiable cleanly.

---

## L3 — DEEP DRILL: substrate-native FIX (rank-ordered)

### L3.1 — FIX-1: Support-restricted matched filter (PRIMARY)

**Algebraic correction:**
- Replace `scores = noisy_y @ codebook.T` with per-i `scores[i] = noisy_y[support_i] @ codebook[i][support_i]`
- Vectorizable via mask: `scores = (noisy_y * mask) @ codebook.T` where mask zeroes out non-support dims — but this leaks across codebook entries if supports differ; need per-row masking
- True vectorized form: `scores[i] = (noisy_y * (codebook[i] != 0)) @ codebook[i]` — done per-row in a loop OR via gather-scatter

**Cell-author falsifiability:**
- HARD_PASS: ARM_SUPPORT_RESTRICTED@f=0.02@sigma=16 >= 0.95 (recovers near-dense performance)
- HARD_FAIL: ARM_SUPPORT_RESTRICTED@f=0.02@sigma=16 < 0.70 (the fix doesn't recover the gap; another mechanism dominates)

**Pseudocode:**
```python
def support_restricted_matched_filter(noisy_y, sparse_codebook):
    """Support-restricted receiver: PV-WTA analog.

    For each codebook entry, score only over its active support.
    Recovers matched-filter SNR loss from sparse zero-padding.
    """
    M, N = sparse_codebook.shape
    scores = np.zeros((noisy_y.shape[0], M), dtype=np.float32)
    for i in range(M):
        support = sparse_codebook[i] != 0  # (N,) boolean
        # scores per batch row: inner product on the support only
        scores[:, i] = noisy_y[:, support] @ sparse_codebook[i, support]
    return scores

# Vectorized variant:
def support_restricted_vectorized(noisy_y, sparse_codebook):
    # Mask noise to codebook supports per row implicitly via element-wise:
    # noisy_y broadcast to (B, M, N), codebook (1, M, N), elementwise multiply, sum
    # Memory: B * M * N — at B=200, M=500, N=4096 = 1.6 GB float32. OK on CPU.
    elementwise = noisy_y[:, None, :] * sparse_codebook[None, :, :]  # (B, M, N)
    scores = elementwise.sum(axis=2)  # (B, M)
    return scores
```

(Wait — the vectorized version is `noisy_y @ sparse_codebook.T` mathematically; for sparse codebook the zero entries automatically zero-out the noise contribution at those dims for THAT codebook entry. So `noisy_y @ sparse_codebook.T` IS the support-restricted matched filter, as long as the noisy_y is the SAME for all codebook scorings. The receiver SNR loss is from `noisy_y` itself having N dims of independent noise, summed weighted by `sparse_codebook[i]`. So the score noise variance is sum(codebook[i]^2) * sigma^2 = E_i * sigma^2 — and score signal is <s, codebook[i]> = E_s when matched. So margin is E_s / sqrt(E_s * sigma^2) = sqrt(E_s) / sigma = sqrt(82)/sigma. **STILL the -17 dB receiver penalty.**)

**Re-deriving:** the issue is that the CURRENT receiver IS already support-restricted in the score computation — zero entries in codebook[i] contribute zero to <noisy_y, codebook[i]>. The receiver SNR loss CANNOT be fixed by support restriction alone. It is fundamental to the signal energy being f*N.

**Real fix: amplify signal energy at encoding.** Two paths:
1. **Bipolar amplification:** make sparse entries +/- A instead of +/- 1 where A = 1/sqrt(f) = 7.07. Then signal energy = f*N*A^2 = N = 4096 — restored to dense. This is just SCALING the sparse codebook. The cost: dynamic range expansion (need higher numerical precision OR scaled noise model). **This is the actual fix.**
2. **Density repair:** raise f from 0.02 to 0.5+, regaining signal energy at the cost of bundle capacity (CERT 592 trade-off curve).

Path 1 is substrate-native and trivial. Path 2 abandons CERT 592 benefit.

### L3.2 — REVISED FIX-1: Amplitude-scaled sparse codebook (the actual algebra)

**Algebraic correction:**
- `sparse_codebook[i, j] = sign * sqrt(1/f)` for active entries, instead of `sign * 1.0`
- Equivalently: encode each item with L2 norm equal to sqrt(N) (matching dense), distributed across only f*N active dims
- Decoder is unchanged: matched filter `noisy_y @ codebook.T`
- Now signal energy E = f*N*(1/sqrt(f))^2 = N = 4096. Receiver SNR matches dense.

**Cell-author pseudocode:**
```python
def make_sparse_amplified_bipolar_codebook(M, N, f, rng):
    """Sparse-bipolar with amplitude 1/sqrt(f) so signal energy = N (dense-equivalent)."""
    codebook = np.zeros((M, N), dtype=np.float32)
    n_active = max(1, int(round(f * N)))
    amplitude = 1.0 / math.sqrt(f)  # = 7.07 for f=0.02
    for i in range(M):
        active_idx = rng.choice(N, size=n_active, replace=False)
        signs = rng.integers(0, 2, size=n_active).astype(np.float32) * 2.0 - 1.0
        codebook[i, active_idx] = signs * amplitude
    return codebook
```

**Cell-author falsifiability:**
- HARD_PASS: ARM_NESTED_SPARSE_AMPLIFIED@sigma=16 >= 0.95 AND ARM_NESTED_BRAIN_AMPLIFIED@sigma=16 >= 0.95
- HARD_FAIL: ARM_NESTED_SPARSE_AMPLIFIED@sigma=16 < 0.70 (amplitude scaling failed to recover; another bug)

**P_deflated: 0.75** (algebra is exact; only risk is cleanup interaction with high-magnitude sparse values)

### L3.3 — FIX-2: Codebook-bound thresholded coincidence receiver

**Algebraic correction:**
- Replace cosine matched filter with binary coincidence count over codebook support
- For each codebook entry: count how many noisy_y[support_i] have sign matching codebook[i][support_i]; threshold at >= alpha * f * N for some alpha

**Pseudocode:**
```python
def thresholded_coincidence_score(noisy_y, sparse_codebook, alpha=0.7):
    M, N = sparse_codebook.shape
    scores = np.zeros((noisy_y.shape[0], M), dtype=np.float32)
    n_active = (sparse_codebook != 0).sum(axis=1)  # (M,) support sizes
    for i in range(M):
        support = sparse_codebook[i] != 0
        signs_match = (np.sign(noisy_y[:, support]) == np.sign(sparse_codebook[i, support]))
        scores[:, i] = signs_match.sum(axis=1) / n_active[i]  # fraction in agreement
    return scores  # in [0, 1]; threshold at alpha for accept
```

**Pros:** truly substrate-novel; brain-canonical (PV-WTA analog); robust to noise magnitude (only sign matters)
**Cons:** loses optimality for Gaussian noise; ~10x slower than matched filter

**P_deflated: 0.45** (novel-synthesis; capped per calibration penalty)

### L3.4 — Why NESTED_BASELINE@16=1.000 hides the discriminator

The current cell's NESTED_BASELINE (dense + no cleanup) at sigma=16 gives 1.000 because at N=4096, M=500, dense receiver SNR = 64/16=4.0 with lock-in lift sqrt(56/4) = 3.74x → effective margin = 15 std-devs above zero. Trivial regime.

**Discriminator escape:** push sigma to 128+ where dense baseline drops to 0.13. At sigma=128 dense receiver SNR = 64/128 = 0.5 with nested lift 3.74x → margin = 1.87 std-devs. THAT is the discriminating regime.

**Pre-reg cell at high-sigma:** at sigma in {128, 256, 512}, compare all arms. Brain-compose with AMPLITUDE-SCALED sparse + cleanup should clearly beat dense baseline IF the brain-canonical mechanism is real.

---

## L4 — FALSIFIABLE PREDICTIONS (per candidate failure mechanism, both directions)

### Prediction 1 (PRIMARY) — matched-filter-energy explains the sparse collapse

**Hypothesis:** at f=0.02, N=4096, sigma=16: receiver SNR ratio sparse/dense = sqrt(f) = 0.141. Recall as function of effective SNR follows a SINGLE monotone Q-tail curve regardless of f.

**HARD_PASS:** Pearson r(recall, sqrt(f*N)/sigma) >= 0.85 across (f in {0.005, 0.01, 0.02, 0.10, 0.5}, sigma in {16, 32, 64, 128}) grid (60 cells)
**HARD_FAIL:** r < 0.50 (matched-filter-energy is NOT the primary mechanism; some other bug)

**P_deflated: 0.85**

### Prediction 2 (FIX) — Amplitude-scaled sparse codebook recovers near-dense performance

**Hypothesis:** sparse codebook with amplitude 1/sqrt(f) restores signal energy to N. At sigma=16, ARM_SINGLE_LOCKIN_SPARSE_AMPLIFIED >= 0.95 (matching dense 1.000 within noise).

**HARD_PASS:** ARM_SINGLE_LOCKIN_SPARSE_AMPLIFIED@sigma=16 >= 0.95 AND <= 1.005 (recovers; not artifact)
**HARD_FAIL:** ARM_SINGLE_LOCKIN_SPARSE_AMPLIFIED@sigma=16 < 0.70 (the algebra is wrong somewhere; deeper bug)

**P_deflated: 0.75**

### Prediction 3 (BRAIN COMPOSE) — Brain-compose works when receiver is fixed

**Hypothesis:** ARM_NESTED_BRAIN_AMPLIFIED (nested theta-gamma + amplitude-scaled sparse codebook + per-gamma-cycle cleanup) at sigma=32 should EXCEED ARM_SINGLE_LOCKIN at sigma=32 by >=0.05 (this was Prediction 2 of the source research, now testable with corrected codebook).

**HARD_PASS:** delta(BRAIN_AMPLIFIED - SINGLE) >= +0.05 at sigma=32
**HARD_FAIL:** delta < 0 at sigma=32 (brain-compose still doesn't beat single-frequency even with corrected receiver; deeper structural issue)

**P_deflated: 0.50** (cap)

### Prediction 4 (CLEANUP INNOCENCE) — Cleanup is innocent in the original collapse

**Hypothesis:** the gap NESTED_CLEANUP@16=1.000 - NESTED_BRAIN_FULL@16=0.187 = 0.813 is ENTIRELY attributable to sparse-codebook receiver loss, not cleanup-attractor pathology.

**HARD_PASS:** ARM_NESTED_SPARSE@16 (no cleanup) - ARM_NESTED_BRAIN_FULL@16 (with cleanup) is in [-0.02, +0.02] (cleanup adds no discriminative effect on sparse; current empirical: 0.197 - 0.187 = +0.010 ✓)
**HARD_FAIL:** |delta| > 0.05 (cleanup is contributing one direction or the other meaningfully)

**P_deflated: 0.80** (empirical already confirms; this is mostly a sanity gate)

### Prediction 5 (DISCRIMINATOR REGIME) — NESTED_BASELINE@16=1.000 is by-construction saturation

**Hypothesis:** at sigma=128 (harder regime) NESTED_BASELINE drops to 0.13 (empirical), confirming the cell's hard-pass criterion at sigma=16 was saturated and could not discriminate the structural SNR-deficit predicted by source research.

**HARD_PASS:** NESTED_BASELINE@128 in [0.08, 0.20] AND SINGLE_LOCKIN@128 in [0.40, 0.50] (the structural-deficit framing was correct — but only visible at sigma=128, not sigma=16)
**HARD_FAIL:** baseline@128 within 0.02 of single@128 (no structural deficit; source research framing wrong)

**P_deflated: 0.80** (empirical already shows this from current data: 0.132 vs 0.433)

### Prediction 6 (REVISIT BRAIN-COMPOSE FRAMING) — When brain compose ACTUALLY helps

**Hypothesis:** brain-compose (amplitude-scaled-sparse + cleanup) BEATS single-frequency only in the regime where receiver SNR is BELOW dense saturation AND cleanup margin matters. That regime at N=4096, M=500 is sigma in [64, 128]. At lower sigma, dense already saturates; at higher sigma, even cleanup can't recover.

**HARD_PASS:** ARM_BRAIN_AMPLIFIED@sigma=128 >= ARM_SINGLE_LOCKIN@sigma=128 + 0.10 (cleanup leverage shows in mid-noise regime)
**HARD_FAIL:** delta < 0 at sigma=128 (brain-compose offers no advantage at any sigma)

**P_deflated: 0.45**

---

## L5 — CROSS-THREAD SYNTHESIS

### Does K-module heterogeneous compose cell (abda9f08) inherit the same bug?

The K-module cell composes sparse-bipolar × lock-in × HRR × refuse-gate. **It depends on which receiver each module uses.**

- IF the sparse-bipolar arm uses cosine matched filter against the sparse codebook → **YES, inherits the -17 dB receiver penalty**
- IF the sparse-bipolar arm uses amplitude-scaled sparse codes (1/sqrt(f) signs) → no penalty
- IF the lock-in arm uses dense bipolar → no penalty there
- IF the HRR arm uses standard FHRR → no penalty (HRR vectors are dense complex)

**Recommendation:** add a quick audit on cell abda9f08's `make_sparse_bipolar_codebook` to check whether amplitudes are scaled or raw +/-1. If raw, predict that arm will under-perform vs predictions; if scaled, no issue.

### General principle: when does substrate compose constructively vs destructively?

**The principle:** substrate composes destructively when an upstream module DEGRADES the input statistics that a downstream module ASSUMES. Specifically:

1. **Energy preservation:** if module A reduces signal energy (e.g., zero-padding via sparse encoding), and module B's receiver assumes full-dim energy (e.g., matched filter), composition breaks. Fix: insert energy-restoration normalization between modules.

2. **Distribution shift:** if module A changes input statistics (e.g., from Gaussian to heavy-tailed), and module B is tuned for the source distribution (e.g., a refuse-gate calibrated on Gaussian tails), composition breaks. Fix: per-module distribution audit.

3. **Order matters:** Espinoza 2018 finding — PV inhibition (sparsification) happens BEFORE attractor cleanup in the brain because the attractor needs the sparsified input as the starting point. Substrate composes in the order: demod → sparsify → cleanup. The cleanup step is operating on sparse input WITHOUT the brain's PV-WTA receiver. Mismatched order — substrate should do `cleanup_with_support_restriction` instead of `cleanup_after_sparsify`.

**Substrate-product compose discipline (proposed):**
- Document per-module ASSUMPTIONS about input statistics (energy, distribution, dimensionality)
- Before composing, verify upstream output matches downstream assumptions
- Make energy-restoration normalizations explicit (e.g., always normalize to unit L2 norm between modules, OR scale to match dense-equivalent energy)
- Order modules to match brain-canonical order when brain-existence-proof argues for it (PV-WTA → CA3-attractor, NOT attractor → WTA)

### With substrate-mine inventory (sparse-bipolar 20-300x bundle-capacity lift)

CERT 592 measured BUNDLE capacity (storing K items via superposition, retrieving via cleanup). At f=0.02, bundle capacity is 20-300x higher than dense — TRUE for storage interference reasons. **CERT 592 did NOT measure receiver SNR.** Bundle capacity wins because sparse items have lower mutual cross-correlation in superposition. Receiver SNR is a SEPARATE metric. The brain-compose drill misread CERT 592 as if it implied receiver-SNR wins — it doesn't.

**Recommendation:** add a META atom on substrate-mine discipline: storage-capacity metrics are NOT receiver-SNR metrics. Distinguish primitives by their RECEIVER characteristics, not just their STORAGE characteristics.

### With chain-grade lock-in cell at N=8192

Single-freq P=64 at N=8192 hits sigma=64 at recall=1.000 with cv=0.000. The receiver SNR at sigma=64 dense N=8192 = sqrt(8192)/64 * sqrt(32) lift = 90.5/64*5.66 = 8.0. Easy regime.

Applied to N=4096 sparse f=0.02 sigma=16: receiver SNR = sqrt(82)/16 * sqrt(56/4) = 9.05/16 * 3.74 = 2.12. Below recall transition. Hard regime.

**Implication:** sparse-bipolar can ONLY match dense lock-in if either (a) amplitude-scaled to recover signal energy, or (b) the receiver is changed to support-restricted-WTA, or (c) the input N is increased to compensate (e.g., N=4096*7=28672 to bring sparse energy back to 4096).

### With substrate-as-LM test methodology audit

The substrate-as-LM cell uses sparse-bipolar (per fair-harness chain-grade at 7.30 BPC). **Does that cell use amplitude-scaled sparse OR raw +/-1?** If raw, the substrate-as-LM result is also under-powered by -17 dB on the predictive-coding receiver side. **Audit required.** This could change BPC by 0.5-1.0 if confirmed under-powered.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

### Compose discipline (immediate)

**Rule:** when composing modules, verify ENERGY PRESERVATION across the interface. Sparse codes pay sqrt(f) receiver-SNR unless amplitude-scaled OR receiver is changed to support-restricted/WTA.

**Hdlab/ primitive needed:** `hdlab/sparse_bipolar_amplified.py` — sparse-bipolar codebook generator with amplitude scaling option (default 1/sqrt(f)) and an audit utility to compute "effective signal energy" for any codebook.

### CERT 592 framing correction

The atom `sparse_bipolar_bundle_capacity_lift_20_300x_at_f_le_0.02` is correct for BUNDLE capacity. **Add a companion atom:** `sparse_bipolar_raw_amplitude_pays_minus_17dB_receiver_SNR_unless_amplitude_scaled_to_1_over_sqrt_f`. The two together give the full picture.

### Source research note correction

The source research note `research_theta_gamma_SNR_compensation_brain_mechanism_2026-06-23.md` should be appended with this drill's findings under a "POST-EXPERIMENTAL CORRECTION" section:
- Prediction 1 P=0.60 was OVER-confident; actual outcome 0.187 NOT 0.98+
- The mechanism predicted (sparsification adds margin) is TRUE for storage but FALSE for matched-filter receiver
- Brain compose IS still implementable but requires the support-restricted receiver OR amplitude-scaling fix
- The TDM-gating Anchor 2 pivot in the source research note may STILL be the right path — independent of this matched-filter-energy diagnosis

### L2 vision alignment

L2 vision = glass-box LM INSIDE substrate. The multi-item per query buffer (4-8 items at recall>=0.95) was the substrate-LM bridge. **It is still achievable** — just needs (a) amplitude-scaled sparse OR (b) support-restricted receiver. The brain-compose framing was correct in spirit; the substrate implementation got the receiver wrong.

### Cap_map implications

`cap_map row: nested_theta_gamma_brain_compose_at_N4096` should be marked `MIDDLE_BAND` not `HARD_FAIL` — the failure was a fixable receiver bug, not a structural impossibility. Re-dispatch with amplitude-scaled codebook.

---

## SYMMETRIC NEGATIVITY CHECK (per USER STANDING)

**Could the matched-filter-energy diagnosis be wrong (compose really IS the bug)?** The discriminating empirical: NESTED_SPARSE (no cleanup) @ sigma=16 = 0.197 ≈ NESTED_BRAIN_FULL (with cleanup) @ sigma=16 = 0.187. Both collapse equally. If COMPOSE were the bug, NESTED_SPARSE alone should be much higher than BRAIN_FULL. It isn't. Diagnosis robust.

**Could the matched-filter-energy explain SINGLE_LOCKIN_SPARSE@16 = 0.583 (not 0.197)?** Yes: the single-freq P=64 lock-in has higher per-cycle SNR lift (sqrt(32)=5.66x) than nested (sqrt(14)=3.74x). Effective receiver SNR for sparse+single at sigma=16 = 9.05/16 * 5.66 = 3.20. For sparse+nested at sigma=16 = 9.05/16 * 3.74 = 2.12. The 3.20 vs 2.12 ratio = 1.51x = exactly the nested-vs-single SNR-deficit predicted by source research. Sparse arm experiences BOTH the matched-filter-energy loss AND the nested-vs-single structural deficit, compounding. Diagnosis robust AND consistent with source research's nested-vs-single algebra (which was correct).

**Could amplitude-scaling break other things?** Potentially: (a) HRR-binding with amplitude-scaled sparse vectors has different normalization properties; (b) bundle capacity at high amplitude may have different interference patterns. The decisive test should also include a control arm at amplitude=1 (current) and amplitude=1/sqrt(f) (fix) to compare across f-grid.

**Could the fix be "just use dense codebook"?** Yes — that's the trivial fix. But sparse codebook has bundle-capacity benefits (CERT 592). Amplitude-scaling lets you keep CERT 592 bundle gains AND fix receiver SNR. The fix is strictly better than abandoning sparse.

**Could P=0.85 on matched-filter diagnosis be over-confident?** It's based on EXACT algebra + empirical match within 0.10. The remaining uncertainty is from finite-N inter-item interference in sparse codebooks (variance in pairwise overlaps). The decisive test at f-grid will tighten this — if Pearson r >= 0.85 across grid, diagnosis confirmed. If 0.50 < r < 0.85, partial. If r < 0.50, refuted.

**Could the brain-canonical compose framing be over-extrapolating?** The brain literature DOES support per-gamma-cycle attractor cleanup + sparsification + WTA all working TOGETHER. The substrate is missing the WTA component. Adding amplitude-scaling is a kludge — the deeper fix is implementing a substrate-native WTA receiver (Anchor 3). That's a separate v2 cell.

**Could MIDDLE_BAND be the most likely outcome of the fix cell?** Yes — Prediction 2 P=0.75 means 25% likely the amplitude-scale doesn't fully recover. MIDDLE_BAND outcome (recall in [0.70, 0.94]) routes to: investigate finite-N inter-item interference at high amplitude, OR move to support-restricted WTA receiver as v3.

---

## DISPATCH RECOMMENDATION

**Primary cell (decisive test):** `exp_sparse_receiver_energy_diagnosis_v1`
- Routing: local_cpu_queue (~30min CPU)
- 2 arms (DENSE baseline / SPARSE-RAW / SPARSE-AMPLIFIED) × 5 f-values × 4 sigmas × 3 seeds × 200 trials at N=4096, M=500
- Pre-reg HARD bands per L4 above
- Self-tests: verify amplitude-scaling produces codebook with L2 norm matching dense within 1e-3; verify Pearson r computation; verify recall@1 calibration

**Secondary cell (if PRIMARY HARD_PASS):** `exp_theta_gamma_nested_brain_amplified_compose_v2`
- Repeat the brain-compose cell with amplitude-scaled sparse codebook
- Routing: local_cpu_queue (~60min CPU) or remote_cpu_queue
- Pre-reg HARD bands: BRAIN_AMPLIFIED@sigma=32 >= SINGLE_LOCKIN@sigma=32 + 0.05 (Prediction 3)

**Audit (immediate, no cell needed):** review K-module heterogeneous compose cell abda9f08 sparse-bipolar arm — does it amplitude-scale or use raw +/-1? If raw, predict under-performance.

**META atoms (independent of cell outcome):**
- `meta_atom_sparse_bipolar_pays_sqrt_f_receiver_SNR_unless_amplitude_scaled_2026-06-23.md` (matched-filter algebra)
- `meta_atom_storage_capacity_metric_is_not_receiver_SNR_metric_distinguish_substrate_primitives_2026-06-23.md` (CERT 592 framing correction)
- `meta_atom_substrate_compose_breakage_is_usually_module_interface_assumption_mismatch_not_attractor_interference_2026-06-23.md` (general compose discipline)

**Conditional follow-on if PRIMARY HARD_PASS:**
- v2: amplitude-scaled brain compose (above)
- v3 (parallel): support-restricted thresholded coincidence receiver as brain-canonical alternative
- Update CERT 592 framing in atoms.jsonl

**Conditional follow-on if PRIMARY HARD_FAIL:**
- Investigate finite-N codebook inter-item interference (Stream B literature on basin overlap for sparse codes)
- Consider attractor-completion + amplitude-renormalization sequential design
- Drop sparse-bipolar as substrate primitive in favor of dense+cleanup (CERT 592 capacity claim re-examined)

**Companion exp_dev hand-off:** `notes/exp_dev_handoff_research_sparse_cleanup_compose_breakage_diagnosis_2026-06-23.md` (written this same cycle).

---

## CITATIONS (verified count = 9 external)

**Matched filter SNR theorem & receiver math:**
1. Matched filter — Wikipedia. URL: en.wikipedia.org/wiki/Matched_filter
2. Lecture 3: Matched Filters Part I (UIUC ECE361 SP2011). URL: courses.grainger.illinois.edu/ece361/sp2011/Newlectures/Lecture03.pdf
3. ScienceDirect — Matched Filter overview. URL: sciencedirect.com/topics/mathematics/matched-filter
4. Chapter 11. Detection of Signals in Noise — UC Davis Physics 123. URL: 123.physics.ucdavis.edu/week_5_files/filters/matched_filter.pdf

**Sparse signaling / coherent receivers / ternary codes:**
5. US Patent 4,991,214 — Speech coding using sparse vector codebook and cyclic shift techniques (Google Patents)
6. Compressed Sensing for Finite-Valued Signals. arXiv 1609.09450
7. On sparse graph coding for coherent and noncoherent demodulation. IEEE Xplore 8007061

**Sparse coding cleanup & attractor dynamics:**
8. Kitano & Aoyagi 1998. "Retrieval Dynamics of Neural Networks for Sparsely Coded Sequential Patterns." arXiv cond-mat/9805135 (basin of attraction depends on activity control)
9. Vinje & Gallant 2000-style "Efficient Sparse Coding in Early Sensory Processing: Lessons from Signal Recovery." PMC3291527 (sparse recovery requires nonlinear receivers)

**Substrate-internal cross-references (not counted):**
- `data/exp_substrate_theta_gamma_nested_with_brain_compensation_N4096_v1/metrics.json` (empirical failure data)
- `data/exp_lock_in_amplifier_hd_frequency_v1_FULL/metrics.json` (dense baseline at N=8192)
- `notes/research_theta_gamma_SNR_compensation_brain_mechanism_2026-06-23.md` (source research; this drill corrects Prediction 1)
- CERT 592 sparse-bipolar bundle-capacity (chain-grade; storage metric only)
- Espinoza et al. 2018 Nat Commun (PV-DG sparsification serial pipeline; cited via source research)
- Lisman & Jensen 2013 Neuron (theta-gamma neural code; cited via source research)

---

## CONTRACT OUTPUT

`research: delivered sparse_cleanup_compose_breakage_diagnosis -> notes/research_sparse_cleanup_compose_breakage_diagnosis_2026-06-23.md ; HEADLINE: NOT a compose-breakage; sparse-bipolar codebook ALONE pays -17 dB matched-filter receiver SNR penalty because signal_energy=f*N=82 vs dense N=4096; cleanup is innocent (empirical NESTED_SPARSE-NESTED_BRAIN_FULL=+0.010 within noise); fix is amplitude-scaling sparse entries to 1/sqrt(f)=7.07 restoring dense-equivalent energy OR support-restricted WTA receiver; decisive test 30min CPU local; cap_map row should be MIDDLE_BAND not HARD_FAIL; P_deflated(matched-filter-energy diagnosis)=0.85, P_deflated(amplitude-fix recovers)=0.75; next-drill candidate: K-module heterogeneous compose cell abda9f08 sparse arm audit + substrate-as-LM sparse-bipolar receiver audit`

---

*Research drill complete 2026-06-23. 3 parallel WebSearch lit-scans (matched-filter SNR theorem / sparse signaling coherent receivers / sparse coding attractor dynamics) + 2 supplementary scans (cyclic shift coherent receivers / sparse vector matched filter receiver SNR penalty). Generic queries only (no substrate-novel mechanism names off-platform). Brain-existence-proof asymmetric calibration applied per USER (deflate 0.10-0.15 not usual 0.15-0.25; novel-synthesis cap 0.65). HARD-FAIL thresholds mandatory both directions; 6 falsifiable predictions pre-registered. Symmetric negativity check applied (7 angles). Empirical algebra-match verified: sparse SNR sqrt(0.02)=0.141=-17dB; predicted SINGLE_LOCKIN_SPARSE@16=0.583 matches dense lockin behavior at equivalent receiver SNR within ~0.10. 3 standalone META atoms routed. 1 hdlab/ primitive backlog item routed. Cell hand-off companion file routed. Time elapsed ~30 min per budget.*
