# Prereg — wave14_sellke_marginal_stability_v1

## Hypothesis

Per Sellke 2025 (marginal-stability framework for spin-glass landscapes),
under a small ferromagnetic drift Delta_W = epsilon * J (J symmetric iid
+/-1/sqrt(N)), the substrate's Hebbian-trained weight matrix W will
remain replica-symmetric (single overlap peak |q| ~ q*) so long as
epsilon < epsilon_c, then transition to RSB (multi-peak or heavy-tail q
distribution) above the threshold.

If the substrate carries this Sellke-style marginal-stability transition
under uniform ferromagnetic Delta_W, characterize epsilon_c.

## Pre-registered bands

- **HARD PASS RS-STABLE** (`SELLKE_RS_STABLE`):
  - Baseline (eps=0) single overlap peak (n_modes <= 1).
  - Highest eps (eps=0.40) still single-mode AND overlap std <= 0.20.
  - No detectable threshold in [0, 0.40].

- **HARD PASS RS-BREAKS** (`SELLKE_RS_BREAKS`):
  - Baseline (eps=0) single overlap peak.
  - Some eps in {0.01, 0.05, 0.10, 0.20, 0.40} has n_modes >= 2 OR overlap std > 0.20.
  - Report first crossing as eps_c estimate.

- **HARD FAIL / INCONCLUSIVE** (`SELLKE_INCONCLUSIVE`):
  - Baseline already multi-mode (cannot infer threshold).

## Design

- N = 512, M = 64 patterns (alpha = M/N = 0.125, well below Hopfield critical 0.138).
- 200 overlap samples per (eps, seed), 30 Glauber steps to fixed point.
- 6 epsilon levels: {0.0, 0.01, 0.05, 0.10, 0.20, 0.40}.
- 3 seeds per cell.
- ETA: ~45-60 min CPU.

Mode count uses 0.05-wide histogram bins on [-1, 1]; peak = bin > both
neighbors AND >= max(counts)/4.

## Citations

- Sellke 2025 (arXiv pending; marginal-stability in spin-glass landscapes).
- Hopfield 1982; Amit-Gutfreund-Sompolinsky 1985 (RSB capacity).

## Routing

- Queue: `remote_cpu_queue`.
- Timeout: 3600 s.
- Pure CPU numpy (no CUDA).
