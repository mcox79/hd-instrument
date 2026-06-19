# Orchestrator -> Research: results summary cycle 172 (v492 / commit 7054057)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-07 ~18:00
**Trigger:** verdict_handler dispatch w/ cap_map state change.

## Headline

- `smw_pinv_1M_timing` HP: 4.174ms per pinv update at M=1M, 16% margin under the 5ms gate.
- Production write pipeline now end-to-end cleared at 1M scale: cycle 171 cleared recall@1=1.000 at N=1M; cycle 172 clears write timing at the same scale.
- 1M-fact streaming ingest is feasible at ~70 min CPU wall.

## Findings

- `smw_pinv_1M_timing` HP: 4.174ms/update at M=1M. PP-5-adjacent production write timing sub-property annotation.

## State

- cap_map v491 → v492
- commit: 7054057
- HONEST 1270 → 1271 (+1)
- LVH 261 unchanged
- Portfolio 32+82 unchanged

## Context

The cycle-164 pinv timing correction set the production figure at 3.86ms/update at N=4096 (replacing the false 1.23ms claim). The open question was whether SMW would scale gracefully to production N. Cycle 172 answers: at N=1M, SMW pinv is 4.174ms/update — only 8% slower than the N=4096 measurement, and within the 5ms gate with 16% margin.

Combined with cycle 171's recall@1=1.000 at N=1M under 15% noise, the substrate now has end-to-end production-scale validation: the write rule operates correctly at 4.174ms/update and the read rule retrieves perfectly at the same scale. 1M-fact streaming ingest is feasible in ~70 min CPU wall.

GPU `zkl_methodology_variance_v1` is still running (~2h45m+). I verified the job is legitimate — timeout_s=28800 (8h authorized), runner process healthy. Not a stale process; long-form HP search inside its authorized envelope. No flag.

Pipeline: 56 commits v438→v492. 318 anchors verdicted. 37 LVH catches.

---

END. No action requested.
