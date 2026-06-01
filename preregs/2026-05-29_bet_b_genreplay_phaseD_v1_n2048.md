# Prereg: bet_b_genreplay_phaseD_v1_n2048

Filed: 2026-05-29
Source: research_bet_b_4stage_architectural_exhaustion_2026-05-29.md Anchor A2 / research_surge_synthesis_v276_2026-05-29.md Priority 3.

## Hypothesis
Pool-retrieval generative replay during Phase D mixes Phase-A/B/C patterns into Phase-D
training batches, preventing catastrophic forgetting via substrate-native CLS consolidation.
Predicted ret_A +0.08 to +0.15 over baseline 0.745.

## N-suffix
No _nN suffix; production N = 2048 (smoke anchor). PROT-018: stated explicitly.

## Pre-registered bands (calibration probe)
No prior empirical anchor; bands per +-50% policy.
HARD_PASS: mean retention_A >= 0.80 in >= 2/3 seeds.
HARD_FAIL: mean retention_A <= 0.55 across all seeds.
MIDDLE_BAND: retention_A in (0.55, 0.80).

## Smoke result
smoke ret_A=1.2239 at N=512 1-seed (bpc_A_final < bpc_A_baseline; generative replay
improved Phase A retention beyond baseline). Very strong positive signal.

## Timeout estimate
Smoke: N=512, 1 seed: ~4s CPU. GPU: ~1s.
FULL: N=2048, 3 seeds. Scale: (2048/512)^1.5 * 3 = 34. Est: 1.5 * 4 * 34 = 204s.
Safety 2x: 408s. timeout_s = 600.

## Middle-band outcome plan
If MIDDLE_BAND: route to FULL N=8192 5-seed. Replay mechanism promising.
If HARD_PASS: promote to N=8192 5-seed FULL in next cycle.
