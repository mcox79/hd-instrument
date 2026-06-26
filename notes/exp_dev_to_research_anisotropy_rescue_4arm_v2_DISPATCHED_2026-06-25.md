# Anisotropy-rescue 4-arm sweep v2 calibrated-meter DISPATCHED to overnight_queue

**From:** exp_dev
**To:** research (lead); cc orchestrator, skunkworks
**Date:** 2026-06-25 (UTC 2026-06-26T00:45Z)
**Status:** DISPATCHED + REMOTE VERIFIED

## Summary

USER-approved re-dispatch of v1 anisotropy-rescue 4-arm sweep with calibrated meter and full mode (3 seeds). Cell + prereg
committed (commit b2af908f, path-scoped); SCP'd + queued via `tools/orchestrator/queue_add.sh` to `overnight_queue`. Remote
`--self-test` PASSED in 6.1s (meter beta-sweep recovers D=1.000 on isotropic synthetic); entry verified present in remote
`data/overnight_queue/queue.json`.

## Anchor / artefacts

- **Anchor:** `substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full`
- **Script:** `experiments/exp_substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full.py`
- **Prereg:** `preregs/2026-06-25_substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full.md`
- **Queue:** `overnight_queue` (GPU runner; Fix #24 torch.cuda active)
- **Timeout:** 5400s (90 min) -- below 14400s PROT-021 threshold; checkpoint wired
- **Seeds:** [11, 13, 19] (cross-cell consistent with this arc)
- **Encoder:** EleutherAI/pythia-2.8b (full); pythia-160m (smoke)
- **M_SWEEP:** [1000, 3000, 10000] (full); [400, 1000] (smoke)

## v2 fixes vs v1 (load-bearing)

1. **Calibrated meter** — Arm D = MAX over attention-beta-multiplier sweep `[1, 4, 16, 64] * (1/sqrt(d))`. v1 was locked
   at beta=1/sqrt(d) which is flat-softmax at d=768, M=1000 -> Arm D collapsed to 0.445 -> cell uninterpretable absolute.
2. **3 seeds [11, 13, 19] + cv ceilings** (cv <= 0.05 for HARD_PASS_SOLVED; cv <= 0.07 for partial).
3. **Bands locked at module init via assert** (META_PROSPECTIVE_BANDS_FRESH_SEEDS).
4. **Fix #24 torch.cuda actively used** on all big matmuls; encoder hoisted; CPU fallback only in self-test.
5. **Relative-promise safety net** — verdict reports arm_X / arm_D ratios; MIDDLE_BAND_RELATIVE_PROMISE catches real
   mechanism even when meter still struggles.
6. **Arm renaming for honesty** — `B_fly_lsh` and `B_charikar` are PEERS, not control + control-of-control. v1's intended
   negative control (Charikar) was 0.982 at smoke -- v2 tests fairly with a 3-seed full to see if that survives at
   pythia-2.8b regime.
7. **Q-discipline** — `[Q-DISCIPLINE: suspect saturation]` flag if any arm >= 0.995.
8. **Self-test asserts meter calibrated** -- isotropic synthetic at M=400/d=128 must give Arm D >= 0.80 after beta sweep.
   Catches v1 meter-bug regression BEFORE dispatch. (Passed locally + on remote.)
9. **Flagship encoder override fix** — explicitly set `_probe.ENCODER` after import so v2 RUN_MODE controls encoder choice
   (v1 inherited flagship's pythia-2.8b default since flagship's RUN_MODE detection happens at module-load time).

## Pre-registered bands (per prereg)

- **HARD_PASS_ANISOTROPY_SOLVED_VIA_LSH_FANOUT:** arm_B_fly_lsh >= 0.80 + D >= 0.80 + cv <= 0.05 at M=10k
- **HARD_PASS_CHARIKAR_RESCUE:** arm_B_charikar >= 0.80 + D >= 0.80 + cv <= 0.05 at M=10k (v1's 0.982 winner test)
- **HARD_PASS_PARTIAL_LSH:** either LSH arm >= 0.60 + D >= 0.80 + cv <= 0.07
- **MIDDLE_BAND_RELATIVE_PROMISE:** arm_X / arm_D >= 0.80 even if absolute < 0.80
- **HARD_FAIL_LSH_DOESNT_HOLD:** BOTH LSH arms <= 0.40 at M=10k (would invalidate v1 smoke)
- **METER_UNDER_CALIBRATED:** arm_D < 0.80 even with beta sweep + no relative-promise

## Strategic significance

If chain-grade pass at v2 full: substrate has a REAL solution to anisotropy on real Pythia keys (vs being bypassed via
partition-routing + KV-learned-projection). Stage 4 LM-equivalence deferral could be revisited; three distinct KG retrieval
paths (dense-KV + partition-routing + LSH-fanout).

If HARD_FAIL or persistent METER_UNDER_CALIBRATED: v1 smoke 0.982 was noise/single-seed/pythia-160m artifact; anisotropy
remains bypassed; existing positioning stands. Close with honest negative.

Either outcome decision-grade; current v1 smoke MIDDLE_BAND is uninterpretable; v2 calibrated is the test that matters.

## Dispatch evidence

```
[gate] entry_name=substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full
[gate] PROT-020 OK: script imports torch (GPU queue routing justified)
[gate] running --self-test... OK in 6.1s
[gate] OK: queued substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full
[gate] queue pending now (1): [...the cell...]
[queue-add] VERIFIED: substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full present in remote overnight_queue/queue.json
[queue-add] OK: substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full queued to overnight_queue
```

## Next-cycle expectations

- GPU runner picks up entry on its next claim cycle (overnight_queue runner)
- Per timeout estimate: ~10-15 min compute wall (encoder one-shot per seed + 6 arms x 3 M-points x 3 seeds)
- Metrics land at `data/exp_substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full/metrics.json` on remote
- Per Fix #25, landing notifier should detect + ping; Skunkworks landed-VET to follow on tier classification
- Per Fix #28, verdict consumer must read per-arm metrics not just verdict_msg framing

## Cross-cell context

- v1 (smoke MIDDLE_BAND meter-bug) lives at `data/exp_anisotropy_rescue_4arm_sweep_v1_gpu/metrics.json`
- Related: `data/exp_dense_kv_whitening_revival_v1_gpu/metrics.json` (whitening HARD_FAIL on Pythia keys -> anisotropy is real)
- Related: today's deep dive `notes/research_deep_dive_partial_and_open_capabilities_intuitive_2026-06-25.md`

— exp_dev
