# Strategy → Exp Dev — Saad-Solla v13 reship (v258→v259 follow-on)

**Date:** 2026-05-28
**Trigger:** saad_solla_v12_n8192_5seed FAILED — TIMEOUT (wall_s=1800.0037 ≡ timeout_s=1800; per-cell wall ~500s; 5seed × 3f = 15 cells × 500s = 7500s budget required, 1800s allotted = ~24%).
**Cap_map context:** Saad-Solla LEADING ✅ row at v258. v252 2-seed N=8192 FULL HARD_PASS evidence STANDS; v12 5-seed envelope-extension hit timeout BEFORE producing any honest physics signal. NO cap_map state move; this is INFRA reship, not capability rescue.

## TASK

Reship Saad-Solla 5-seed envelope-extension probe with adequate timeout budget.

## WHY

Defense-in-depth corroboration of v252 LARGE-N FULL HARD_PASS (2-seed). Multi-seed evidence at N=8192 would consolidate v252's seed-spread bound. NOT load-bearing for cap_map state (v252 already CLOSES envelope-extension gap for substrate-product purposes per the v252 annotation framing).

## CONTRACT

- Anchor name MUST include `_n<N>` and `_<seeds>seed` suffix per PROT-018.
- `--timeout` flag MUST be explicit per [[feedback-per-experiment-timeout-required]].
- Per-experiment pre-reg note required.

## AUTONOMY

Exp_dev picks the variant based on current GPU queue depth + envelope-extension priority:

### Option (b) CHEAPEST — N=4096 5-seed substitute (~5min design)
- Anchor: `saad_solla_v13_n4096_5seed`
- N=4096 (vs 8192) → ~4x wall savings → ~1875s for 15 cells; fits comfortably in 1800s timeout
- Trade-off: lower-N gives less direct envelope-extension of v252's N=8192 evidence; mitigates by scope-spanning (combined with v252 2-seed N=8192 = 7-seed equivalent breadth across N regimes)
- Pre-reg HF1/HF2/HF3 thresholds per envelope-fail-bands; use v252 5-cell-pass HF formula as baseline

### Option (c) MOST-FAITHFUL — N=8192 5-seed with extended timeout (~10min design)
- Anchor: `saad_solla_v13_n8192_5seed_extended_timeout`
- timeout_s=14400 (4hr ceiling; well above 7500s estimated wall)
- Per [[feedback-per-experiment-timeout-required]] formula: `1.5 * smoke_wall_s * (FULL_N/smoke_N)^exp * (FULL_seeds/smoke_seeds)` = 1.5 × 500 × 1 × (5/2) ≈ 3750s per f-cell × 3 = 11250s → 14400s = 28% headroom (acceptable)
- timeout_s > 14400 would block pre-ship per [[feedback-per-experiment-timeout-required]]; this stays at the ceiling
- Direct envelope-extension at N=8192 = strongest evidence

### Option (d) MEDIUM — N=8192 3-seed (~15min design)
- Anchor: `saad_solla_v13_n8192_3seed`
- Drop to seeds {7, 17, 23}; 3 seeds × 3 f = 9 cells × 500s = 4500s; timeout_s=5400 (20% headroom)
- Compromise between coverage and budget; produces 3-seed evidence at N=8192 (envelope-extends v252's 2-seed by +1 seed)

### Option (e) LAST RESORT — 5 single-seed jobs
- Ship as 5 separate single-seed jobs each timeout_s=2000; aggregate offline
- Highest queue traffic; only if (b)/(c)/(d) all blocked

## RECOMMENDATION

(c) extended-timeout is the most faithful to original intent and produces the strongest evidence; if exp_dev can fit it in the GPU queue without pushing other work past their timeout budgets, prefer (c). If GPU queue is congested or user prefers fast turnaround, (b) is acceptable substitute.

## Pre-reg requirements

- HF1/HF2/HF3 thresholds (re-use v12 pre-reg with seed-spread and per-cell r2 / max_dev bounds)
- Smoke gate at N=1024 5-seed first; production only if smoke shows multi-seed consistency
- Self-test cell required (formula check that pearson_r2 computation correct on synthetic data)

## Trigger for cap_map move

If HARD_PASS at N=8192 5-seed (option c) — envelope-extension gap CLOSED at LARGE-N 5-seed scope; consider LIFT on Saad-Solla product-feature reliability band +1-2%. If HARD_PASS at N=4096 5-seed (option b) — scope-spanning corroboration; annotation only.

If HARD_FAIL — THEN trigger honest physics review (multiple seeds at HF threshold across multiple f-cells = genuine refutation; would trigger PROT-004 5-rescue at sub-objective level).

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
