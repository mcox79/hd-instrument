# Design space (HDC-LM, byte-level)

Per research playbook item 4: instead of single-axis ablations, maintain a
written enumeration of the full design space. Spot-check cells; fit a small
surrogate over accumulated runs; target surrogate-disagreement cells next.

Date: 2026-05-18 (initial enumeration)

## Axes and levels

| Axis | Levels | Notes |
|---|---|---|
| **Substrate** | FHRR (current), HRR, BSC, Sparse Block Codes (Laiho 2015), GHRR (Alam 2024 non-commutative) | FHRR is current; BSC and sparse-VSA are bio/hardware-relevant; GHRR captures sequence-order natively |
| **Substrate dim N** | 1024, 4096 (current best), 8192 (2.477), 16384 (running) | Capacity bound per Frady-Kleyko-Sommer log2(M) ≤ N/(2 SNR) |
| **Context size K** | 2, 4 (current), 8, 16 | Bundle capacity: K/N ratio bounds destructive interference |
| **Binding op** | HRR commutative (current), permutation, GHRR non-commutative, vector-tensor binding | Sequence order requires non-commutative or position-binding |
| **Position code** | random FHRR per position (current), fractional binding (Frady-Kanerva-Sommer grid), permutation | Grid tested, slightly hurt at K=4 |
| **Training rule** | pure Hebbian, delta with raw error, delta with softmax cleanup (current), DeltaNet explicit erase | DeltaNet variants experiment queued |
| **Readout NL** | identity, modReLU (current, b=0.5), tanh-magnitude, sigmoid-magnitude | modReLU is current best; PMS-style sigmoid sum-of-subunits untested |
| **Pool write policy** | unconditional (current), surprise-gated (Titans), prioritized-by-loss, none | Surprise-gated experiment queued |
| **Pool retrieval** | softmax weighted (current), top-1 hard, mixture of experts | |
| **Pool size** | 256, 1024 (current), 4096, full-corpus | |
| **Pool blend α** | 0.0, 0.1, 0.3 (current), 0.5, 0.7, 1.0 (pool-only) | |
| **Readout temp β** | 1, 4, 8 (current), 16, 32 | |
| **Arousal (LR) α** | 0.1, 0.3 (current), 0.5, 0.7, 1.0 | |
| **Decay** | 0, 1e-5, 1e-4 (current), 1e-3, 1e-2 | |
| **Epochs** | 1, 5, 10, 15 (current), 30, 50 with early stopping | |
| **Replay policy** | none (current), random shuffle, trajectory-sequence, prioritized-by-loss | Need trajectory buffer for faithful Wilson-McNaughton |
| **Surprise modulator** | none (current), loss-threshold, gradient-norm, deviation-from-running-mean (NE-like) | |

**Combinatorial size:** 5 × 4 × 4 × 4 × 3 × 4 × 4 × 4 × 3 × 6 × 5 × 5 × 5 × 5 × 4 × 4
≈ 92 billion combinations. Obviously infeasible to sweep.

## Surrogate plan

After we accumulate ~50 runs across the queued experiments, fit a small GP
or random-forest surrogate on `(axis_levels) → test_bpc` and use it to:
1. Identify cells where the surrogate is uncertain (high variance) — those
   are candidates for next single-axis spot-checks.
2. Identify cells where the surrogate predicts a regime change — those are
   candidates for hypothesis tests.
3. Identify axis interactions (e.g., "modReLU helps only at large N", or
   "surprise gate hurts at small pool but helps at large pool").

The current 9 single-axis-tested results from the Session 2026-05-18 tracker
are not yet enough for a meaningful surrogate. Target: post-Wave-1, fit
surrogate, redirect Wave 2/3 based on its predictions.

## Cells explicitly tested so far

| Run | Substrate | N | K | Bind | NL | PoolGate | TrainRule | Result |
|---|---|---|---|---|---|---|---|---|
| baseline single-pass | FHRR | 1024 | 4 | HRR | none | uncond | cleaned-delta | 3.16 |
| pointer-chain | FHRR | 1024 | 4 | HRR | none | uncond | cleaned-delta | 2.91 |
| N=4096 | FHRR | 4096 | 4 | HRR | none | uncond | cleaned-delta | 3.02 |
| combined N=4096 + pointer-chain | FHRR | 4096 | 4 | HRR | none | uncond | cleaned-delta | 2.84 |
| eligibility traces | FHRR | 1024 | 4 | HRR | none | uncond | cleaned-delta | 3.11 |
| Krotov polynomial cleanup | FHRR | 4096 | 4 | HRR | poly | uncond | cleaned-delta | 4.15 (fail) |
| randomized DFT (Bloch) | DFT | 4096 | 4 | HRR | none | uncond | cleaned-delta | 3.14 |
| surprise mod (uniform) | FHRR | 1024 | 4 | HRR | none | uncond | cleaned-delta + scale | 4.27 (fail) |
| homeostatic decay 1e-4 | FHRR | 1024 | 4 | HRR | none | uncond | cleaned-delta + decay | 3.16 |
| multi-epoch (3 epochs) | FHRR | 1024 | 4 | HRR | none | uncond | cleaned-delta | 3.005 |
| multi-epoch (5+ overfit) | FHRR | 1024 | 4 | HRR | none | uncond | cleaned-delta | 3.07 → 3.71 |
| multi-epoch + decay | FHRR | 1024 | 4 | HRR | none | uncond | cleaned-delta + decay | 2.985 |
| **combined: multi-epoch + decay + pool** | **FHRR** | **4096** | **4** | **HRR** | **none** | **uncond** | **cleaned-delta + decay** | **2.505** |
| GPU verification of CPU best | FHRR | 4096 | 4 | HRR | none | uncond | cleaned-delta | 2.522 |
| **combined + modReLU** | **FHRR** | **4096** | **4** | **HRR** | **modReLU b=0.5** | **uncond** | **cleaned-delta** | **2.4994** |
| grid positions (BR5) | FHRR | 4096 | 4 | HRR+frac | modReLU | uncond | cleaned-delta | 2.5094 |
| climbing fiber (BR3) | FHRR | 4096 | 4 | HRR | modReLU | uncond | cleaned-delta+C | 2.5008 |
| PFC attractor (BR4) | FHRR | 4096 | 4 | HRR | modReLU | uncond | cleaned-delta+h | 2.7841 |
| DG projector v1 (broken) | FHRR | 4096 | 4 | HRR | modReLU | uncond | cleaned-delta+DG | 2.95 |
| **parallel tempering K=8** | **FHRR** | **4096** | **4** | **HRR** | **modReLU** | **uncond** | **cleaned-delta+PT** | **2.4963** |
| N=8192 | FHRR | 8192 | 4 | HRR | modReLU | uncond | cleaned-delta | **2.4774** |

## Queued and pre-registered

| Run | Pre-reg | Status |
|---|---|---|
| N=16384 | (part of N-scaling sweep) | Running |
| Surprise-gated pool sweep | [2026-05-18_surprise-gated-pool.md](../preregs/2026-05-18_surprise-gated-pool.md) | Pre-registered |
| DeltaNet variants | TBD | Needs pre-reg |
| GHRR non-commutative binding | TBD | Needs implementation + pre-reg |
| 1MB corpus scaling | TBD | Wave 2 |
| BSC substrate port | TBD | Wave 2 |
| Continual learning test | TBD | Wave 3 |
| Few-shot ICL test | TBD | Wave 3 |
