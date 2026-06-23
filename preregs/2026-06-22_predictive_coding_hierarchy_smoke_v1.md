# Pre-reg: predictive_coding_hierarchy_smoke_v1

**Date:** 2026-06-22
**Author:** exp_dev (subagent spawn under Research/Director)
**Anchor:** `predictive_coding_hierarchy_smoke_v1`
**Script:** `experiments/exp_predictive_coding_hierarchy_smoke_v1.py`
**Queue:** `local_cpu_queue`
**Cell class:** SMOKE-only (this file IS the smoke for the PC-hierarchy mechanism;
                a FULL follow-up would scale N_DIM and corpus if results warrant).

## Scientific question

Brain's canonical learning mechanism (Rao-Ballard 1999, Friston 2005, Bastos 2012)
is hierarchical predictive coding: each cortical layer predicts the next layer's
input; only prediction error propagates upward. Does the substrate exhibit a
chain-grade improvement when stacked into a 3-layer PC hierarchy vs. a flat
single-W Hebbian baseline?

Substrate analog: 3 stacked W matrices `[N_DIM x N_DIM]`; L1 predicts L2's input;
L2 predicts L3's input; local Hebbian on prediction error at each layer;
forward-only (no backprop required at inference).

**Modal expected outcome:** MIDDLE_BAND. The PC literature has prior negative
results on substrate-style discrete-vector encodings, but per USER 2026-06-22
empowerment, lit-scan dismissed-as-impossible is INFORMATION, not a STOP signal;
substrate-native variant (bipolar / sign-quantization + outer-product local
Hebbian) differs from prior failed work and is cost-bounded.

## Design

- N_DIM = 4096 (smoke runs at N_DIM=512 for gate; main runs at 4096)
- N_LAYERS = 3
- SEEDS = [7, 17, 23]
- Synthetic hierarchical corpus: 1000 sequences (4 macro x 5 meso x 50 micro),
  seq_len=10. Planted 3-level hierarchy: identity = sign(macro + 0.5*meso + 0.25*micro).
  Per-token rendering: additive Gaussian noise (std=0.10) + 5% sign-flip.
- 10% stratified held-out for recon_error and L3 clustering metric.
- Capacity probe: train arms at 200 / 500 / 1000 sequences (degradation curve).

### Arms

1. **ARM_FLAT_HEBBIAN** (control): single W; Hebbian outer-product on raw input;
   reconstruction = sign(W @ input).
2. **ARM_PC_HIERARCHY_3LAYER** (test): 3 stacked W matrices; forward propagates
   cleaned signal; Hebbian update on per-layer prediction error
   (`W_Li += lr * outer(error_Li, layer_i_input)`); downward reconstruction
   sweep via W transposes.
3. **ARM_PC_HIERARCHY_LAYERED_CLEANUP** (test): ARM_PC_HIERARCHY_3LAYER + per-layer
   nearest-prototype cleanup gate (64 prototypes per layer).

### Metrics

- (A) **mean_recon_error** = 1 - mean cosine(reconstructed_token, identity)
- (B) **L3 macro-cluster ratio** = mean within-macro L3-similarity / mean across-macro
      L3-similarity. >=1.5 = clustering; <1.05 = no structure.
- (C) **capacity**: recon_error at 200 / 500 / 1000 seqs.

## Pre-registered bands

(Per NEGATIVITY-BIAS rule, both directions specified symmetrically.)

- **HARD-PASS** (PC hierarchy works substrate-native; chain-grade-eligible learning
  primitive): `ARM_PC_HIERARCHY_3LAYER mean_recon_error <= 0.5 * ARM_FLAT_HEBBIAN`
  AND L3 representations show macro-category clustering (`cluster_ratio >= 1.5`).
  PC_LAYERED_CLEANUP arm meeting the same bar ALSO triggers HARD_PASS.

- **HARD-FAIL** (PC adds no value over flat; substrate can't do hierarchical
  prediction at this scale): `ARM_PC_HIERARCHY_3LAYER mean_recon_error >= 0.9 *
  ARM_FLAT_HEBBIAN` AND PC_LAYERED_CLEANUP same.

- **MIDDLE**: partial benefit; characterize. The cleanup arm may close the gap
  even when the bare PC hierarchy does not.

### P estimates (lit-scan calibration penalty applied)

- P(HARD-PASS) = 0.25
- P(MIDDLE)    = 0.55
- P(HARD-FAIL) = 0.20

## Discriminating-regime guard (cert-architecture)

The recon-ratio metric (`ratio_pc_over_flat`) becomes uninformative if the flat
Hebbian baseline saturates (`recon_error < 0.02`) -- the ratio of any number to
near-zero is artificially inflated. Per cert-architecture DISCRIMINATING_REGIME
discipline, when flat saturates we force MIDDLE_BAND and route to characterize
at a corpus size that pushes flat past its capacity cliff.

The hidden capacity threshold for sign-quantized Hebbian retrieval is ~0.14*N.
At N_DIM=4096 the cliff is ~570 patterns; with 1000 train sequences, flat MUST
degrade. At N_DIM=512 with 54 patterns, flat saturates as shown in smoke -- the
gate's --smoke output is therefore expected to be MIDDLE_BAND
(FLAT_SATURATED_REGIME), not HARD_FAIL.

## Sanity self-tests (asserted before main sweep)

1. Trivial 1-sequence input -> all arms reconstruct nearly perfectly
   (recon_error < 0.20 flat / 0.50 PC). PC tolerance is looser because of
   3 stacked nonlinear sign() quantizations.
2. All-noise input -> all arms degrade similarly (no arm spuriously better by
   >=5x).
3. Hebbian sign is correct: W magnitude increases under repeated same-input
   training.
4. Error decomposition is exact: `error_L1 + L1_out == input` within numerical
   tolerance.

## Compute budget

- Per-seed at N_DIM=4096, 3 layers, 1000 seqs, seq_len=10, 3 arms, 3 capacity
  points: ~3 matmuls per token x 10000 tokens x 3 arms x 3 capacity points
  ~ ~10G ops ~ ~150s numpy.
- 3 seeds total: ~7-8 min compute + corpus build / metrics overhead -> realistic
  10-15 min wall.
- Safety 2x -> `--timeout=1800` (30 min). Below PROT-021 threshold (14400s),
  so checkpointing optional, but present anyway via `_seed_checkpoint`.

## PROT discipline

- PROT-018: no `_nN` suffix in anchor name; production N_DIM=4096 stated above
  (anchor name is mechanism-named, not N-bound).
- PROT-019: timeout 1800s < tier floor for _n>=4096 (rule requires _n suffix);
  not applicable here (no _n suffix).
- PROT-020: numpy only; queue=local_cpu_queue (CPU-bound); rule applies only to
  overnight_queue.
- PROT-021: short timeout (1800s); checkpoint helper imported as good practice.

## Risk

- Modal MIDDLE_BAND outcome means we'll need to characterize what fraction of
  PC's value (if any) comes from layered cleanup vs. error-based learning rule.
- If HARD_FAIL: route to Research as a negative result + 2x revival drill per
  USER STANDING rule (try denser per-layer cleanup, larger N_DIM, different
  hierarchy depths).
- If HARD_PASS: substrate-native PC hierarchy is a foundational learning
  primitive; route to atomization + hdlab/ code primitive update SAME CYCLE
  per USER 2026-06-22 results-to-application cadence.
