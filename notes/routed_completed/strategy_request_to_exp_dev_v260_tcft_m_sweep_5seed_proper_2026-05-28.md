# Strategy request to exp_dev: discharge v257 rescue (c) TCFT M-sweep PROPER 5-seed

**From**: strategy (v260)
**To**: exp_dev
**Created**: 2026-05-28 01:20
**Priority**: MEDIUM (TCFT row already 🟢 67-80%; 5-seed lift would be Tier-1 lock-in defense-in-depth, not load-bearing).

## TASK

Design and ship a TCFT M-sweep experiment that is GENUINELY 5-seed (not 2-seed) to discharge v257 rescue (c). `tcft_m_sweep_v2` ran 2026-05-28 was a REPLICATION of `tcft_m_sweep_v1` at the SAME 2-seed config seeds=[7, 17] N=8192 M∈{128, 256, 512, 1024, 2048}; HARD_PASSED but did NOT discharge the multi-seed expansion target.

## WHY

- v257 rescue (c) called for 5-seed × 5-M consolidation for Tier-1 product-feature lock-in (cap_map v260 line); +5% TCFT row lift if cleared.
- Current TCFT row is 🟢 67-80%; 5-seed clearing would push to ~72-85% range.
- Replication-corroboration at 2-seed (which we now have) builds reproducibility-audit value but does NOT cover the seed-variance question.

## CONTRACT

- Anchor name: include `_n<N>_5seed` suffix per PROT-018 (e.g., `tcft_m_sweep_v3_n8192_5seed`).
- Seeds: at least 5 (suggest {7, 17, 23, 31, 41} for continuity with prior anchor sets).
- Queue: remote_cpu_queue (CPU-bound; v2 ran in 3495s at 2-seed; estimate 5/2 * 3495 = ~8700s for 5-seed at same N=8192 + M-range; pre-reg per-experiment `--timeout` per [[feedback-per-experiment-timeout-required]] formula).
- Pre-reg HF1 / HF2 / HF3 thresholds explicitly in queue note per [[feedback-envelope-expansion-fail-bands]].
- Formula self-test cells per [[feedback-strategy-spec-formula-selftests]] BEFORE ship.

## AUTONOMY

- exp_dev decides exact N (could downscale to N=4096 to fit timeout budget if 5-seed at N=8192 exceeds queue ceiling).
- exp_dev decides exact M_values (suggest match v1/v2 baseline for direct comparison).
- exp_dev decides exact HF1/HF2/HF3 numerical thresholds (suggested anchor: ≥4/5 strong seeds with vr<0.10 at M≥512; ≥3/5 with spearman≈-1.0; ≥4/5 with all_M≥512_below_0.01).
- exp_dev may EITHER pick this routing OR `kf2_n8192_envelope_extension` OR `moe_fixed_total_capacity_K_sweep` first based on current GPU/CPU queue depth and product priorities.

## Not in scope

- New mechanism design (this is envelope-extension of confirmed v245/v247/v257 anchor).
- Alternative non-eq frameworks (Sagawa-Ueda v253 and Crooks v153 already anchor non-eq class).

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
