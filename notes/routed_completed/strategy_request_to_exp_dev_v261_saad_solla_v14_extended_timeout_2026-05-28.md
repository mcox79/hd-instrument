# Strategy → Exp Dev — Saad-Solla v14 extended-timeout reship (v260→v261 follow-on; 2nd consecutive infrastructure timeout)

**Date:** 2026-05-28
**Trigger:** `saad_solla_v13_n4096_5seed` FAILED — TIMEOUT (wall_s=3600.02 ≡ timeout_s=3600; per v259 sketch (b) `--timeout` was set to 3600s with anticipated wall ~1875s; actual wall hit budget at ~240s/cell × 15 cells; v259 wall estimate was ~2x light).
**Cap_map context:** Saad-Solla LEADING ✅ row at v261 UNCHANGED. v252 2-seed N=8192 FULL HARD_PASS evidence STANDS as load-bearing for the row; v13 5-seed envelope-extension hit timeout BEFORE producing any honest physics signal (remote metrics.json MISSING; local metrics.json STALE pre-ship smoke). NO cap_map state move; this is **2nd consecutive INFRA reship**, not capability rescue.
**Pattern:** This is the 3rd consecutive saad_solla 5-seed FULL probe attempt to fail at the infrastructure layer (v12 timeout 1800s → v13 timeout 3600s → v14 pending). Per [[feedback-no-padding-experiments]] one more attempt is justified ONLY if it ships at the proper budget; further attempts after a (b)-class failure would constitute padding.

## TASK

Reship Saad-Solla 5-seed envelope-extension probe at full timeout budget per v259 sketch (c).

## WHY

Defense-in-depth corroboration of v252 LARGE-N FULL HARD_PASS (2-seed). 5-seed evidence at N=8192 would provide canonical cross-seed reproducibility at the production scale. **NOT load-bearing for cap_map state** (v252 already closes envelope-extension gap for substrate-product purposes per v200 ELEVATED-TO-LEADING annotation framing). If v14 also fails infrastructure, PARK the 5-seed envelope-extension entirely per v261 rescue (e) — v252 2-seed evidence becomes the closing evidence.

## CONTRACT

- Anchor name MUST include `_n<N>` AND `_<seeds>seed` suffix per PROT-018.
- `--timeout` flag MUST be explicit per [[feedback-per-experiment-timeout-required]]; recommended ceiling 14400s (4hr GPU); >14400s blocks pre-ship per existing PROT.
- Per-experiment pre-reg note required with HF1/HF2/HF3 thresholds.
- Smoke gate N=1024 5-seed first; production only if smoke shows multi-seed consistency.
- Self-test cell required (pearson_r2 computation on synthetic).
- Pre-reg per [[feedback-envelope-expansion-fail-bands]] (envelope-extension probe; cannot reuse v252 thresholds verbatim — extend).

## AUTONOMY

Exp_dev picks the variant based on current GPU queue depth + per-cell wall calibration:

### Option (b) RECOMMENDED — N=8192 5-seed with extended timeout
- Anchor: `saad_solla_v14_n8192_5seed_extended_timeout`
- timeout_s=14400 (4hr ceiling — at the [[feedback-per-experiment-timeout-required]] cap)
- Per v13 calibration: per-cell wall ≈ 240s at N=4096; at N=8192 expect ~960s/cell (4x scaling) × 15 cells = ~14400s = SCRATCHING THE CEILING. Risk that this is tight.
- Direct envelope-extension at N=8192 = strongest evidence

### Option (c) SAFER MARGIN — N=8192 3-seed at extended timeout
- Anchor: `saad_solla_v14_n8192_3seed`
- 3 seeds {7, 17, 23} × 3 f-cells × 960s/cell = ~8640s; timeout_s=12600 (45% headroom)
- Compromise: produces 3-seed evidence at N=8192 (envelope-extends v252's 2-seed by +1 seed at correct N) without tight ceiling

### Option (d) BACKUP — N=8192 5-seed sharded into 5 single-seed jobs
- 5 single-seed jobs each timeout_s=3000 (~25% headroom over 960s × 3 = 2880s/seed)
- Highest queue traffic + post-hoc aggregation step
- Use ONLY if (b) and (c) both at-risk for ceiling

## RECOMMENDATION

(c) 3-seed at N=8192 with timeout_s=12600 is the safest bet given v12/v13 wall-estimate misses. Produces +1 seed evidence at production N; v252 2-seed combined with v14 3-seed = 5-seed-equivalent at N=8192 via union. Avoids the 14400s tight ceiling.

If exp_dev wants maximal direct envelope-extension and accepts ceiling risk, ship (b).

## Pre-reg requirements

- HF1: per-seed r2 ≥ 0.85 in ≥ 3/5 (or 2/3) seeds at each f ∈ {0.0, 0.5, 1.0} (or other f-grid per script)
- HF2: per-seed max_dev ≤ 0.08 in ≥ 3/5 (or 2/3) seeds at each f
- HF3: seed-spread (max - min) on mean_r2 ≤ 0.04
- HARD_PASS if all 3 HF clear; MIDDLE_BAND if HF1+HF2 borderline; HARD_FAIL only if substantial cell collapse
- Smoke gate: N=1024 5-seed must show qualitatively consistent r2 > 0.7 across seeds before ship

## Trigger for cap_map move (v14)

- HARD_PASS at N=8192 5-seed (option b): envelope-extension gap CLOSED at LARGE-N 5-seed scope; consider LIFT on Saad-Solla product-feature reliability band +1-2%
- HARD_PASS at N=8192 3-seed (option c): scope-spanning corroboration; annotation only (still defense-in-depth)
- INFRA-FAIL (3rd consecutive): PARK 5-seed envelope-extension per v261 rescue (e); v252 2-seed evidence stays as closing evidence; future scope-spanning explored only with cheaper instrumentation (e.g., shared-state run accumulating seeds across jobs)

## Reference

- v258 → v259 routing: `notes/strategy_request_to_exp_dev_v259_saad_solla_v13_reship_2026-05-28.md` (original sketch (c) framing)
- v260 → v261 decision: `notes/strategy_decisions_2026-05-28.md` (v261 entry with full forensics on v13 timeout pattern)

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
