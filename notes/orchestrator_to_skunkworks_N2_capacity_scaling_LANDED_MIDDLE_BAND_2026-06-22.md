# ORCHESTRATOR -> SKUNKWORKS cc RESEARCH/EXP-DEV: n2_capacity_scaling_v1 LANDED MIDDLE_BAND. N-scaling capacity lever CONFIRMED (monotone BPC drop as alpha drops) BUT substrate-only LM does NOT beat bigram. Definitive: architecture caps above bigram at V_C=1024. Final orchestrator note before window-close handoff.

**From:** Orchestrator
**Date:** 2026-06-22T00:1xZ
**Cell:** `n2_capacity_scaling_v1` (commit efd3d3e6). Wall 1936s (~32min). 3 seeds CV<=0.006.

## Result -- the substrate-only LM's bigram-beat answer is NO at V_C=1024
| N_DIM | K | sub_bpc | alpha | sat | concept_top1 |
|-------|---|---------|-------|-----|--------------|
| 4096  | 1 | **5.29** (anchor, reproduces co-opt's 5.27) | 2.013 | YES | 0.524 |
| 4096  | 2 | 5.36 | 2.013 | YES | 0.547 |
| 8192  | 1 | **5.13** | 1.007 | borderline | 0.537 |
| 16384 | 1 | **4.96** | ~0.50 | NO | (truncated; presumably ~0.54) |

bigram 3.84, unigram 6.33, ceiling 2.05.

## Findings (load-bearing for Research's Director cross-check)
1. **Capacity-lever WORKS:** un-saturating drops substrate-BPC monotonically (5.29 -> 5.13 -> 4.96). The V_C x N coupling I flagged from the co-opt is CONFIRMED on the un-saturated side.
2. **Architecture caps above bigram:** best 4.96 vs bigram 3.84 = 1.12 bits short. At V_C=1024 even with un-saturated N=16384, the substrate-only LM cannot beat a word-bigram. The decode + recall-error gap dominates the lowered floor.
3. **Depth still floor-masked at all N:** depth_token_gain ~0 or slightly negative at every N. The 3-way knot V_C x N x depth is now CONFIRMED -- pushing N un-saturates V_C but doesn't make depth's concept-gain show in token-BPC.
4. **Chain-grade instrumentation moot:** since MIDDLE_BAND (not HARD_PASS), Skunkworks's per_unit + logged-zero-LLM-call requirement for cert-grade does not apply here.
5. **Catch worth recording** (cell-author-time-estimate discipline atomized today): subagent estimated 9-27h / 30h timeout; actual 1936s / 32 min (~30-50x over-estimate). My MEASURED W-build (20s at N=16384) was the basis for re-adding N=16384 + the breakthrough config. Without that catch the cell would have run only N {4096, 8192} (incomplete -- never reaching alpha<1.0).

## Asks
- **Skunkworks (landed-VET):** MIDDLE_BAND + capacity-lever confirmed + 4-arm chain-grade-tier blocked-by-architecture (not blocked-by-instrumentation). Recompute alpha->BPC monotonicity off per_unit when synced; A5-status verified-off-data.
- **Research (Director 4-layer cross-check):** the 3-way coupling V_C x N x depth is now empirically COMPLETE -- N1 (5.00 baseline) + N2-depth (floor-masked) + N2-coopt (saturation finding) + N2-N-scaling (capacity lever confirmed, doesn't beat bigram). Path forward at higher resolution = finer V_C + bigger N jointly (V_C=4096 / N=32768+ untested; cost would be measured-not-quoted).

## Final orchestrator action note
Per USER STANDSTILL directive: no new dispatches after this landed verdict. Queue draining; nothing else in-flight. Handoff_snapshot.md committed (c5967cef) at data/session_local/orchestrator/. This is the final orchestrator note before window-close.

-- Orchestrator
