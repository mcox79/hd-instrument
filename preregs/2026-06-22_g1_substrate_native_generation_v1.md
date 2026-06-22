# Pre-reg: g1_substrate_native_generation_v1

**Date:** 2026-06-22
**Anchor:** g1_substrate_native_generation_v1
**Cell:** experiments/exp_g1_substrate_native_generation_v1.py
**Source-of-truth pre-reg (brain-drill #4 L4 + L5):** notes/research_brain_generation_cerebellar_forward_prediction_5x_drill_2026-06-22.md
**Task-spec deflated bands (Exp-Dev / Director routing 2026-06-22):** this file (canonical bands for the dispatched cell)

## Scientific question

Can the substrate GENERATE a coherent sequence of states using ONLY substrate
primitives (S matrix from c3 + codebook NN-cleanup + optional Langevin noise),
with ZERO LLM forward calls at generation time?

c3 (CERT 585->586, 2026-06-22) shipped the SequenceMatrix S as a chain-grade
sequence-binding primitive. g1 USES S as the autoregressive engine to test
whether substrate-native generation composes.

## Mechanism

Karuvally-Sejnowski 2023 NeurIPS Long-Sequence-Hopfield + arxiv 2603.06875
Langevin-on-MHN-energy stochastic sampling + DG/CA3 codebook attractor
cleanup. The hetero-associative S matrix from c3 IS the substrate's
cerebellar-forward-model / HVC-synfire-chain analogue.

Generation step:
```
y_raw    = S @ k_{t-1}                                       # hetero-Hebbian retrieval
y_noisy  = y_raw + sigma * randn                             # Langevin sampling
k_t      = codebook_nn(y_noisy)                              # attractor cleanup
```

## 4 arms (discriminator-regime per Fix #16)

1. **NONE (control):** k_t = random codebook index; no S, no cleanup.
2. **S_ONLY:** k_t = S @ k_{t-1} raw (no Langevin, no cleanup). Tests pure
   hetero-associative retrieval.
3. **S_LANGEVIN:** k_t = S @ k_{t-1} + sigma * randn (no cleanup). Tests Langevin
   sampling without the codebook attractor complement.
4. **S_LANGEVIN_CLEANUP (main):** full mechanism. Codebook-snap each step.

The 4 arms ARE the discriminator (Fix #16). One arm must split from the
others. If S_LANGEVIN ~ S_LANGEVIN_CLEANUP, cleanup is null discriminator
(honest per-cell finding). If S_LANGEVIN_CLEANUP >> S_LANGEVIN, cleanup is
the load-bearing complement.

## Config

- N_DIM = 4096
- N_SEQ = 10 sequences of length K_SEQ = 20
- 3 seeds: 7, 17, 23
- T_GENS = [1, 4, 8, 16] (pre-reg primary T=8; T=1 anchor; T=16 super-pass)
- N_PROBES_PER_T = 40
- N_OOD_PROBES = 40
- LANGEVIN_SIGMA_SCALE = 0.10 (sigma = 0.10 * mean_norm(S @ k))
- REFUSE_TAU = 0.10 (cosine threshold for OOD refuse-gate)
- Corpus: synthetic bipolar keys (substrate-primitive isolation; matches c3 / c1 / a8)

## Pre-registered HARD bands (deflated per task-spec)

**HARD_PASS (chain-grade, generation mechanism validated):**
- Arm 4 (S_LANGEVIN_CLEANUP) `trajectory_coherence(T=8) >= 0.60`
- AND Arm 4 `novelty_ratio >= 1.5`
- AND Arm 4 `refuse_OOD >= 0.90`
- AND Arm 1 (NONE) `trajectory_coherence(T=8) <= 0.20` (control is incoherent)
- AND `delta(Arm 4 - Arm 1) >= 0.40` at T=8
- AND `cv <= 0.07` across 3 seeds for Arm 4 at T=8 (looser than c3's 0.05 because
  generation is noisier)
- AND `zero_llm_calls_at_inference == True`
- AND W matrix L2-norm unchanged by generation (assertion)

**MIDDLE_BAND (proven-bound partial):**
- Arm 4 `trajectory_coherence(T=8) in [0.20, 0.60)` AND `delta(Arm4-Arm1) >= 0.20`
- OR `novelty_ratio in [1.0, 1.5)`

**HARD_FAIL:**
- `trajectory_coherence(T=8) < 0.20` at Arm 4
- OR substrate-only-decode gate violated (`n_llm_calls > 0`)
- OR W modified by generation
- OR Arm 4 collapses to a single fixed-point attractor (`distinct_visited <= 2.5`
  at T=8 with coh >= 0.30 -- the "perfect-by-construction saturation" failure
  mode where the rollout falls into a single basin and never moves)
- OR `refuse_OOD < 0.50` (gate broken)
- OR `novelty_ratio < 1.0` (pure memorization, no generation)

## Discriminating-regime requirement (C5 / Fix #16)

The CAN-fail regime IS the 4-arm contrast:
- All arms ~ NONE at T=8 => mechanism null (substrate cannot generate)
- All arms >= 0.99 at all T => harness too easy (mis-specified)
- S_LANGEVIN ~ S_LANGEVIN_CLEANUP => cleanup is null discriminator (substrate
  generates fine without the attractor snap; biological-license-only)
- S_ONLY ~ S_LANGEVIN_CLEANUP => Langevin is null discriminator (noise doesn't
  help or hurt; honest finding)
- S_LANGEVIN_CLEANUP much greater than {S_LANGEVIN, S_ONLY, NONE} => the full
  mechanism is load-bearing (expected; chain-grade primitive)

## Pre-reg direction (Fix #5 / pre-reg-direction-must-honor-intent)

Arm 4 > {Arm 1, Arm 2, Arm 3} at T=8 (cleanup is load-bearing complement). A
large abs-delta in the WRONG direction (e.g. Arm 1 > Arm 4 by 0.30) = HARD_FAIL,
NOT MIDDLE_BAND.

## W vs S separation (c3 invariant)

Writes ONLY mutate S; W (the c3 invariant) is untouched. Assertion enforced
per-arm; HARD_FAIL on violation.

## Honest scope

- Phase 1: synthetic bipolar keys (matches c3 / c1 / a8 substrate-primitive
  isolation pattern). Position-binding via the codebook itself (each step's
  state is a unique codebook entry; no explicit clock vector).
- Phase 2 (deferred, conditional on g1 HARD_PASS): explicit HVC clock-HV
  binding + Pythia-encoded FB15k chains (Karuvally L2 clock-binding ablation;
  L4 cross-corpus test). Brain-drill #4 g2 conditional cell handles SMA-style
  hierarchical generation.
- Phase 2 (deferred, conditional on g1 HARD_FAIL): g1b capacity-vs-pairs
  diagnostic to localize whether the bottleneck is W_seq saturation (35000
  pairs at N_DIM=4096) or harness/cleanup brittleness.

## Pythia/MiniLM/LLM presence

ZERO. No LLM forward calls at generation time. Synthetic-bipolar keys do not
require an encoder. Substrate-only-decode gate asserted `n_llm_calls == 0`.

## Calibrated P (per Director / brain-drill #4)

**P(HARD_PASS) = 0.45** (novel-synthesis cap; deflated from 0.55 because
Langevin sampling + Karuvally-Sejnowski temporally-asymmetric Hebbian
composition has multiple novel-composition layers that may interact
unexpectedly at this substrate's N_DIM / capacity regime).

## What unlocks (USER strategic value)

c3 (chain-grade today) gave the substrate sequence STORAGE. g1 (this cell)
extends to sequence GENERATION. Combined with the substrate-native
char-trigram encoder (shipped today, separate thread), this is the path to
bidirectional conversation with zero external model anywhere -- the L5 MOAT.

## 2x-revival angle (if HARD_FAIL or MIDDLE_BAND; per USER STANDING)

Route to Research for revival drill: capacity-vs-pairs sweep (g1b), or
dense-Hopfield p=3 readout (Karuvally polynomial nonlinearity), or
HDC-binding-factored W_seq (use substrate KG directly instead of dense matrix).
The brain-drill #4 L4 already enumerates these.

## Dispatch routing

**remote_cpu_queue** (matches c3 pattern; pure numpy + np matmul on N_DIM=4096
keys is CPU-friendly; 3 seeds * 4 arms * (write_S + sigma_est + T-eval +
refuse-eval) at K_SEQ=20 N_SEQ=10 is ~30-60min remote total per per-cell
estimate; near-c3 wall).

## Self-tests (formula-selftests)

1. NONE arm at T=3 small seq: `trajectory_coherence <= 0.40` (random)
2. S_LANGEVIN_CLEANUP at T=3 small seq: `trajectory_coherence >= 0.50`
3. `_LLM_CALL_COUNTER == 0` throughout

## Artifacts

- Cell: `experiments/exp_g1_substrate_native_generation_v1.py`
- Pre-reg (source-of-truth, full L1-L5): `notes/research_brain_generation_cerebellar_forward_prediction_5x_drill_2026-06-22.md`
- Pre-reg (deflated bands, this file): `preregs/2026-06-22_g1_substrate_native_generation_v1.md`
- Composes with: c3 SequenceMatrix (`hdlab/sequence_memory.py`); U1 set-readout-top-k;
  c1 CLS replay (deferred for continual-learning composition)

## Atom ID candidate (for Skunkworks A5 if chain-grade)

`research::T1/EXP_g1_substrate_native_generation_v1`

The brain-drill #4 atomization candidate naming follows the c3 / r1 /
brain-drill family convention (drill #4 = research domain).
