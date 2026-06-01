# Pre-registration: qe1_substrate_annealing_v1_n4096

Date: 2026-05-29
Anchor: `qe1_substrate_annealing_v1_n4096`
Script: `experiments/exp_qe1_substrate_annealing_v1_n4096.py`
Queue: `overnight_queue` (GPU)
Timeout: 14400 s (PROT-019 floor for `_n4096`)
Parent: `kf1_hallu_rescue_v2_n4096`

## Scientific question

Quantum-annealer analog: does a beta-annealing schedule during iterative retrieval
improve accuracy on borderline / over-capacity cases (M_frac=4, near M_c) versus
single-pass fixed-beta argmax retrieval?

## Configuration (FULL)

- N = 4096 (PROT-018 binding via `_n4096` suffix)
- Codebook: Kerdock 4-coset, C = 4*N = 16384
- M_frac = 4.0 (borderline / over-capacity regime where retrieval is fragile)
- T = 5 retrieval iterations per probe
- n_probes = 500 stored-key probes per cell
- Schedules tested: fixed (beta=32), linear (2 -> 64), exponential (2 * 2^t),
  inverse_linear (1/beta linear from 1/2 to 1/64)
- Seeds: [7, 17, 23] (3 seeds per spec)
- Total cells: 4 schedules x 3 seeds = 12 cells (3 baseline + 9 schedule)

## Pre-registered envelope-fail-bands

Definitions: per-seed `delta = accuracy(schedule) - accuracy(fixed-beta)`.

- HARD_PASS: at least ONE non-fixed schedule has `delta >= 0.05` on `>= 2/3` seeds.
- MIDDLE_BAND: at least ONE non-fixed schedule has `delta in [0.02, 0.05)` on `>= 2/3` seeds
  AND no schedule satisfies HARD_PASS.
- HARD_FAIL: no schedule has `delta >= 0.02` on `>= 2/3` seeds.

## Formula self-tests (executed at import time)

1. Schedule formulas: linear(t=0)=2, linear(t=4)=64; exp(t=0)=2, exp(t=4)=32;
   inverse_linear(t=0)=2, inverse_linear(t=4)=64; fixed all = 32.
2. C = 4 * N at N=4096 = 16384.
3. Verdict gates: HARD_PASS / HARD_FAIL / MIDDLE_BAND with synthetic per-seed cells.
4. Smoke cell forward pass at N=1024 produces valid accuracy in [0, 1].
5. OOM pre-check: 4096^2 * 4 bytes < 6 GB.

## Timeout justification

- Smoke wall (estimated): 0.5 s/cell at N=1024.
- Scaling: (4096/1024)^1.5 * 5_iter ~= 40x factor; per-cell ~20 s at FULL.
- 12 cells x 20 s = 240 s nominal.
- Safety 10x for GPU cold-start, codebook reuse, probe build: 2400 s.
- PROT-019 floor for `_n4096` = 14400 s. We use the floor.

## Strategic disposition on each outcome

- HARD_PASS: substrate benefits from quantum-annealer-style schedules; new product
  feature candidate (annealed-retrieval mode) for the auditable memory layer.
- MIDDLE_BAND: characterize but do not productize; useful adjunct to broader
  retrieval-stability research.
- HARD_FAIL: substrate operates at saturation under fixed-beta argmax; annealing
  is not in the design space for this substrate class.
