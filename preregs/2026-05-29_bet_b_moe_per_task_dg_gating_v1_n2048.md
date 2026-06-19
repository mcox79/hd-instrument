# Prereg: bet_b_moe_per_task_dg_gating_v1_n2048

Filed: 2026-05-29
Source: research_bet_b_4stage_architectural_exhaustion_2026-05-29.md Anchor A3 / research_surge_synthesis_v276_2026-05-29.md Priority 3.

## Hypothesis
MoE-per-task with DG-gating: 4 dedicated expert W matrices (one per phase), gated via
dentate-gyrus-style pattern separation routing. W_1 frozen after Phase A gives
structurally-guaranteed retention. Predicted ret_A +0.07 to +0.13 (theoretical: ~1.0 for hard gate).

## N-suffix
No _nN suffix; production N = 2048 (smoke anchor). PROT-018: stated explicitly.

## Pre-registered bands (calibration probe)
No prior empirical anchor; bands per +-50% policy.
HARD_PASS: mean retention_A >= 0.80 in >= 2/3 seeds.
HARD_FAIL: mean retention_A <= 0.55 across all seeds.
MIDDLE_BAND: retention_A in (0.55, 0.80).

## Smoke result
smoke ret_A=1.0000 at N=512 1-seed (W_1 frozen -> bpc_A_final == bpc_A_baseline).
Perfect retention confirmed structurally as expected. 1-seed smoke.

## Timeout estimate
Smoke: N=512, 1 seed, 4 experts: ~4s CPU. GPU: ~1s.
FULL: N=2048, 3 seeds. 4x expert overhead.
Scale: (2048/512)^1.5 * 3 * 4 = 11.3 * 12 = 136. But 4x experts ~4x cost.
Est: 1.5 * 4 * (2048/512)^1.5 * 3 = 1.5 * 4 * 11.3 * 3 = 203s.
Safety 2x: 406s. timeout_s = 600.

## Middle-band outcome plan
If MIDDLE_BAND: investigate gate leakage. Try lower GATE_TEMP or hard argmax.
If HARD_PASS: route to N=8192 5-seed FULL with hard-gate variant.
