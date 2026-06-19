# exp_dev -> queue: Clifford-isomorphism test batch (MUB ships; F_4 v2 holds for strategy)

**Date:** 2026-05-23
**From:** exp_dev
**To:** queue (via queue_runner)
**Re:** Strategy's paired ship of 3.A (F_4 v2) + 3.B (MUB distinguishability)
       from notes/strategy_to_exp_dev_F4_v2_symplectic_trace_2026-05-23.md
       and notes/strategy_to_exp_dev_MUB_distinguishability_2026-05-23.md.

## Batch status

| experiment | self-test gate | shipped? |
|---|---|---|
| F_4 v2 (3.A) symplectic-rank | **d=8 exact-enumeration FAILED** (F_4=0.266, expected in [1.5, 4.5]); rank histogram concentrated at full-rank — bug in symplectic-block convention | **NO** — upstream-pushed to strategy in `notes/exp_dev_to_strategy_F4_v2_d8_selftest_failed_2026-05-23.md` |
| MUB distinguishability (3.B) | all three pass (pairwise unbiasedness exact, stab-state uniformity exact, Haar floor ~0.32 at N=4 in expected window) | **YES** — see table below |

## Queue entries (Schema B — markdown table; dispatch.py emits queue_add per row)

| queue            | name                                       | script                                                        | prereg                                                            | timeout(s) |
|------------------|--------------------------------------------|---------------------------------------------------------------|-------------------------------------------------------------------|------------|
| remote_cpu_queue | wave14_kerdock_mub_distinguishability_v1   | experiments/exp_wave14_kerdock_mub_distinguishability_v1.py   | preregs/2026-05-23_wave14_kerdock_mub_distinguishability_v1.md   | 7200       |

## Notes

- Lane `remote_cpu_queue` per the drill spec (pure numpy, no GPU dependency,
  M_4096^3 ~ 7e10 GR(4, m) ops estimated 30-90 min on remote CPU).
- Self-test gate runs inside the script before the m=12 probe; if the Hensel-
  lift search fails at m=12 (low risk; the 2-mask search succeeded at m=4
  smoke), the script will raise and the runner will record a clean failure.
- Substrate-state proxies (`vanilla_stab`, `enriched_kerdock`, `haar`) are
  generated in-script — no on-disk snapshot dependency. The drill spec calls
  for actual beta_A snapshots from v149/v164a/v167; if Strategy confirms those
  exist on the remote runner, a v2 with `--use-snapshots` is a follow-up.
- F_4 v2 is held pending strategy decision on Option E/F/G/H (see upstream-push).
  No queue entry. The script artifact + prereg are filed for reuse once the
  symplectic-block convention is resolved.

## Smoke evidence (MUB)

- Self-test gate at m=2 (N=4): PASS.
- m=4 smoke (N=16, 17 MUBs): builds end-to-end, computes TVs for all 3 states,
  writes valid metrics.json with verdict.
- Spot unbiasedness at m=4: max |P - 1/N| = 0.000e+00 (floating-point exact).

## Decision log

`notes/exp_dev_decisions_2026-05-23.md` via `append_decision_log.py`.
