# Pre-reg: Online W Noise Envelope CPU Sweep (Strategy v158 Pick 1 — Cap 5 expansion)

**Date**: 2026-05-23
**Experiment**: `wave14_online_W_noise_envelope_v1`
**Script**: `experiments/exp_wave14_online_W_noise_envelope_v1.py`
**Capability**: Cap 5 (Gap B Online W Robbins-Monro+SNAP, cycle 173 v153 FULL PASS)

## Background

Cap 1 (Crooks-FT) and Cap 3 (NESS streaming) have both demonstrated PASS under bit-flip
noise at p in {0.05, 0.10, 0.20} (v157/v158). This experiment applies the same noise
probe to Cap 5: does Online W retention (Robbins-Monro lr schedule + SNAP saturation
guard) hold when query keys are corrupted by bit-flip noise at retrieval time?

## Config

- Mode: CPU exploratory sweep (local runner)
- N: 4096
- n_writes: 50 (matched to v153 FULL config)
- Robbins-Monro lr: 1/(1+step/10) (matched to v153)
- SNAP threshold: 1.0 (matched to v153)
- Retention threshold: min_acc >= 0.95 across all writes (matched to ONLINE_W_RESISTS_CF)
- Noise model: i.i.d. bit-flip on query key at retrieval (p_flip per bit)
- Noise levels: p in {0.0, 0.05, 0.10, 0.20, 0.30, 0.40}
- n_seeds: 3 (per noise level; mean_min_acc used for pass/fail)

## Memory budget

- W: N x N float32 = 4096 x 4096 x 4 = **64 MB** per seed (sequential, CPU)
- Noise mask: negligible (1D vector operations)
- Total peak: ~64 MB. Well under any limit.
- Wall budget: target < 30 min CPU (50 writes x 50 retrieval checks x 6 levels x 3 seeds)

## Verdicts

- `ONLINE_W_NOISE_ENVELOPE_FULL_PASS` — all 5 noise cells (p > 0) pass mean_min_acc >= 0.95; envelope fully robust at tested noise levels (p up to 0.40).
- `ONLINE_W_NOISE_ENVELOPE_NARROW` — subset of noise cells pass; boundary p identified (first p where mean_min_acc drops below threshold). Partial noise robustness; informs GPU follow-up noise band.
- `ONLINE_W_NOISE_ENVELOPE_KILL` — 0/5 noise cells pass; online W retrieval not robust to any bit-flip noise level tested.
- `ONLINE_W_NOISE_INCONCLUSIVE` — insufficient data.

## Falsifiable prediction

If Cap 5 shares the same noise-robustness mechanism as Cap 1 and Cap 3 (pattern vectors
are close to BSC codewords so bit-flip noise is small in Hamming distance), then we
predict ENVELOPE_NARROW with boundary somewhere in p in [0.20, 0.40], not KILL at p=0.05.

Hard-fail threshold: if KILL at p=0.05, the online W retrieval mechanism is fundamentally
more brittle than Crooks-FT or streaming inference. This would be unexpected and warrants
a rehabilitation sweep (larger N, different SNAP threshold, or retrieval protocol change).

## Output

Noise-band map for Cap 5. Informs whether a GPU FULL follow-up at N=8192 or N=16384 is
worthwhile, and at which noise levels.
