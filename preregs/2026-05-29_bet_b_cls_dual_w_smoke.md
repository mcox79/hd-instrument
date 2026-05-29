# Pre-registration: bet_b_cls_dual_w_smoke

**Date:** 2026-05-29
**Anchor:** bet_b_cls_dual_w_smoke
**Script:** experiments/exp_bet_b_cls_dual_w_smoke.py
**Queue:** overnight_queue
**Trigger:** gamma-1 architectural Bet B alternative (McClelland-McNaughton-O'Reilly CLS)

## Hypothesis
Dual-W complementary learning systems (CLS) with W_fast (rapid plasticity) + W_slow
(slow consolidation via replay) can cross the 0.80 retention_A bar where single-W fails.
W_slow is frozen during Phases B/C/D, preserving Phase A memory.

## Config
- N_FULL = 2048 (no _nN suffix; production N = 2048 stated per PROT-018)
- Seeds: [7, 17, 23]
- eta_fast = 0.30 (rapid plasticity rate)
- eta_slow = 0.01 (consolidation smoothing rate per step)
- N_replay = 500 (consolidation steps after Phase A)
- BSC codebook (Kerdock-safe at any N)
- 4-stage CL protocol: Phase A train W_fast, consolidate -> W_slow, Phases B/C/D train W_fast only, W_slow frozen

## N-suffix
No _nN suffix; production N = 2048; rationale: smoke-profile anchor for gamma-1 CLS
architecture test; N chosen for speed vs depth.

## Pre-registered bands
- HARD_PASS: retention_A(W_slow) >= 0.80 in >= 2/3 seeds.
- HARD_FAIL: retention_A(W_slow) <= 0.50 across all seeds (catastrophic forgetting not resolved).
- MIDDLE_BAND: retention_A in (0.50, 0.80).

Calibration probe (no prior dual-W CLS substrate anchor).
"no prior empirical anchor; bands per calibration-probe policy: +-50% of theory."

## Timeout estimate
Parent N=8192 5-seeds ~600s. N=2048 scale: (2048/8192)^1.5 = 0.125x. Seeds: 3/5 = 0.6x.
Dual-W overhead: 1.5x. estimate = 600 * 0.125 * 0.6 * 1.5 = 67s. GPU 10x faster: 7s.
Safety margin. timeout_s = 7200.

## Smoke result
SELFTEST PASS. ret_A=1.000 at smoke scale. consolidation_decay=0.634.
OOM check: 33.6MB < 6GB. Ship allowed.

## Downstream cap_map move
- HARD_PASS: Bet B architectural bottleneck solved by CLS dual-W; row upgrades
- HARD_FAIL: CLS insufficient; architectural dimension still unsolved
- MIDDLE_BAND: partial progress; FULL at N=8192 needed
