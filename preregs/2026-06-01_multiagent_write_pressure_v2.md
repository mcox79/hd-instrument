# Pre-registration: multiagent_write_pressure_v2

**Date:** 2026-06-01
**Anchor:** multiagent_write_pressure_v2
**Script:** experiments/exp_multiagent_write_pressure_v2.py
**Queue:** remote_cpu_queue
**N:** 4096, N_B_WRITES=50 (harder than v1 which used 10)

## Hypothesis

Extends multiagent_coord_v1 to 50 agent-B writes. Active repulsion deletion
W_new = W - strength * outer(p_target, p_target) / N isolates agent-A patterns
from agent-B writes at high write pressure. final_del_cos < 0.10 = isolated.
Complements v1 result (which used only 10 writes).

## Pre-registered thresholds

- **HARD-PASS:** final_del_cos < 0.10 AND fraction of seeds passing > 0.80 AND retain_frac > 0.90
- **HARD-FAIL:** final_del_cos > 0.20 (deletion leaks into other patterns)
- **MIDDLE-BAND:** final_del_cos in [0.10, 0.20] or seeds_pass < 0.80

## Smoke result (2026-06-01)

Smoke HARD_PASS: final_del_cos=0.052, seeds_pass=2/2=1.0, retain=1.000. Wall ~7.8s.

## Cap-map rows

- Multi-agent write isolation under high pressure
- Per-agent deletion certificate capability
