# Prereg: bet_b_tp_hdc_subspace_v1_n2048

Filed: 2026-05-29
Source: research_bet_b_4stage_architectural_exhaustion_2026-05-29.md Anchor A1 / research_surge_synthesis_v276_2026-05-29.md Priority 3.

## Hypothesis
TP-HDC subspace projection (each phase trains in disjoint orthogonal N/4-dim subspace)
prevents catastrophic forgetting by structural isolation. Predicted ret_A 0.85-0.93.

## N-suffix
No _nN suffix; production N = 2048 (smoke anchor). PROT-018: stated explicitly.

## Pre-registered bands (calibration probe)
No prior empirical anchor; bands per +-50% policy.
Theoretical prediction: ret_A 0.85-0.93.
HARD_PASS: mean retention_A >= 0.80 in >= 2/3 seeds.
HARD_FAIL: mean retention_A <= 0.55 across all seeds.
MIDDLE_BAND: retention_A in (0.55, 0.80).

## Smoke result
smoke ret_A=0.9665 at N=512 1-seed. Strongly positive. 1-seed smoke cannot be HARD_PASS.
Walk-back gate: not borderline. FULL 3-seed warranted without n doubling.

## Timeout estimate
Smoke: N=512, 1 seed: ~4s CPU. GPU: ~1s.
FULL: N=2048, 3 seeds. Scale: (2048/512)^1.5 * 3 = 11.3 * 3 = 34. Est: 1.5 * 4 * 34 = 204s.
Safety 2x: 408s. timeout_s = 900.

## Middle-band outcome plan
If MIDDLE_BAND: file note to next cycle to ship full N=8192 5-seed with this arch.
If HARD_PASS: promote to N=8192 5-seed FULL in next cycle.
