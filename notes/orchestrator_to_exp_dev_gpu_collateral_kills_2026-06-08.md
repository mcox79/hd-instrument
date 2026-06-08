# Orchestrator -> Exp-Dev: 4 GPU experiments failed at 01:32, 3 likely collateral

**From:** Orchestrator  **To:** Exp-Dev  **Date:** 2026-06-08 ~08:00

## Summary

User asked if experiments failed in the last run. 4 GPU anchors failed within a 44-second window starting with the zkl 4h timeout:

| Time | Status | Anchor | Error |
|---|---|---|---|
| 01:32:04 | failed | zkl_methodology_variance_v1 | timeout |
| 01:32:13 | failed | stella400m_encoder_headtohead_v1 | (blank) |
| 01:32:45 | failed | precision_recall_5M_gpu_v1 | (blank) |
| 01:32:48 | failed | patternb_composition_1M_gpu_v1 | (blank) |

All four have **no data directories** on disk — none produced metrics or even partial output.

## Diagnosis

zkl timed out at 4h legitimately (verified earlier — actively progressing 1:1 CPU:wall until the cap).

The other 3 appear to be collateral kills — they failed within ~44s after zkl, with blank error fields and no data dirs. Most likely they were queued GPU jobs that got killed during the runner's post-timeout cleanup, before any of them got to actually start.

Specifically these are NOT in any prior cycle's verdict batch — `stella400m_encoder_headtohead`, `precision_recall_5M_gpu`, and `patternb_composition_1M_gpu` don't appear in cycle-178 (which had `sign_recall_5M_gpu`, `sign_recall_10M_gpu`, `patternb_largescale_composition`, but those are different anchors).

## Request

Re-queue these 3 if they're still wanted:
- `stella400m_encoder_headtohead_v1` — stella 400M encoder head-to-head
- `precision_recall_5M_gpu_v1` — precision/recall at M=5M (extends cycle-178 sign_recall_5M which was on a different anchor)
- `patternb_composition_1M_gpu_v1` — Pattern B composition at 1M (cycle 173 hit V=100k HP; this would extend further)

If they're obsolete now (cycle 178 covered the question), no action needed.

## Side note: zkl LIGHT variant timing

The LIGHT variant timed out at exactly 4h with the 8h-tier scripts presumably needing the same number of seeds × per-seed cost as anticipated × actual per-seed cost being ~80 min not 13.5 min. Next zkl attempt needs either a higher timeout cap (5-6h) or a per-seed scope reduction.

---

END.
