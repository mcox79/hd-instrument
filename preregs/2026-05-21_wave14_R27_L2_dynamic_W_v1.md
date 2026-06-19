# Pre-registration: wave14_R27_L2_dynamic_W_v1

Date: 2026-05-21 (build); 2026-05-22 prereg-hygiene rewrite per Strategy
Status: Pre-registered, gated
Priority: Strategy pipeline-fill #5 — R27 L.2 dynamic W reconfigurability

## Why

Per R27 + Marsh et al. 2025 quantum-optical spin glass (7x over Hopfield via
atomic-position reconfiguration). Substrate analog: dynamically update W via
sliding-window EMA toward recent queries.

  W_{t+1} = (1 - alpha) * W_t + alpha * (1/m) * sum_recent xi @ xi.T

Test capacity gain vs static W baseline at M/N > 1 (over-capacity regime).

## Mechanism

For each seed:
  Build random +/-1 keys, values; W = (values.T @ keys)/N (static baseline)
  Static run: argmax retrieval on a query set
  Dynamic run: same query set, but W updated per query via sliding-window
               EMA (alpha=0.1, window=50) — re-weights toward recent items

## Multi-probe success criteria

- Dynamic acc / static acc >= 1.3x at M/N > 1 (capacity boost)
- 3 seeds
- N=4096 (full), N=512 (smoke)

## Verdict labels

- R27_L2_PASS (ratio >= 1.3)
- R27_L2_PARTIAL (0.9 < ratio < 1.3)
- R27_L2_KILLED (ratio < 0.9; dynamic hurts vs static)
- R27_L2_INCONCLUSIVE

## Runtime: ~10 min
