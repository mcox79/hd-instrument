# exp_dev: gap4_two_tier_generational_W_v1 DISPATCHED to local_cpu_queue

**Filed:** 2026-06-26
**By:** exp_dev (cell-author)
**For:** Research (lead) + Skunkworks (landing VET) + Orchestrator (queue visibility)

## Headline

Gap 4 continual operation Anchor #1 (TWO_TIER generational W) shipped to `local_cpu_queue` at position 10. 4-hr timeout. Cell-spec REMOTE-VERIFIED in queue.json. Pre-flight 5 self-tests PASS + smoke PASS (HARD_FAIL_DOESNT_HELP expected at sub-cliff smoke regime alpha=0.146; promotion code path validated via W_old_util=0.228 on the K=500 arm).

## Artifacts

- Cell: `experiments/exp_gap4_two_tier_generational_W_v1.py`
- Prereg: `preregs/2026-06-26_gap4_two_tier_generational_W_v1.md`
- Smoke metrics: `data/exp_gap4_two_tier_generational_W_v1_smoke/metrics.json` (HARD_FAIL_DOESNT_HELP expected; sub-cliff regime; structural pass only)
- Source research drill: `notes/research_gap4_continual_5x_drill_2026-06-26.md`
- Source handoff: `notes/exp_dev_handoff_research_gap4_continual_5x_2026-06-26.md`
- Commit: 2fb1fd6a

## Design summary

**Mechanism:** Add second W_old matrix alongside W_young. Every K_promote cycles, score atoms-so-far by importance (single-noisy-probe recall accuracy under combined W), promote top tau-fraction into W_old, decay W_young by gamma. Read path uses W_combined = W_old + W_young.

**5 arms (3 seeds [11, 13, 19]):**
1. `ARM_BASELINE_SINGLE_W` -- single W; reproduces a8-class baseline at extended cycles
2. `ARM_TWO_TIER_PROMOTE_500` -- K=500, tau=0.10, gamma=0.90 (frequent promotion)
3. `ARM_TWO_TIER_PROMOTE_1000` -- K=1000, tau=0.10, gamma=0.90 (moderate)
4. `ARM_TWO_TIER_PROMOTE_2000` -- K=2000, tau=0.20, gamma=0.85 (sparse)
5. `ARM_TWO_TIER_RANDOM_PROMOTE` -- K=1000, tau=0.10, gamma=0.90, importance=random (ablation; isolates "is importance scoring load-bearing?")

**Config:** N=4096; 4000 cycles (alpha=0.977 at end ~ 7.1x Hopfield capacity); 3 seeds; RECALL_PROBE_M=100 (first 100 atoms); CHECKPOINT_INTERVAL=250.

## Pre-reg bands (LOCKED at module init)

- **HARD_PASS_TWO_TIER_EXTENDS_CONTINUAL:** best two-tier final_forget <= 0.05 AND baseline curve_max_forget > 0.10 AND best cv <= 0.07 AND strictly better than baseline
- **HARD_PASS_PARTIAL:** drift_reduction >= 0.30 absolute
- **MIDDLE_BAND:** drift_reduction in (0.05, 0.30)
- **HARD_FAIL_TWO_TIER_DOESNT_HELP:** |drift_reduction| <= 0.05

## Smoke pre-flight (load-bearing measurements)

Wall: 346.6s total (5 arms x 600 cycles x 1 seed x N=4096):
- ARM_BASELINE_SINGLE_W: 58.96s
- ARM_TWO_TIER_PROMOTE_500: 86.84s (W_old_util=0.228; promotion path fires once at c=500; scored 500 atoms then promoted 50)
- ARM_TWO_TIER_PROMOTE_1000: 67.80s (K=1000 never fires in 600 cycles; baseline behavior)
- ARM_TWO_TIER_PROMOTE_2000: 79.37s (K=2000 never fires)
- ARM_TWO_TIER_RANDOM_PROMOTE: 53.19s (K=1000 never fires)

Sub-cliff smoke verdict HARD_FAIL_DOESNT_HELP expected; baseline final_forget=0.000 at smoke alpha=0.146 (<< cliff) so there is nothing for TWO_TIER to fix. Promotion code path validated by W_old_util=0.228 + small forget on K=500 arm (0.0333 vs baseline 0.000 -- promotion adds slight noise at sub-cliff, mechanistically expected; relevance is post-cliff regime).

**Full-run wall extrapolation:** ~36 min/seed; 3 seeds = ~108 min ≈ 1.8 hr (well within 14400s = 4hr cap). Per-arm sub-checkpointing caps any hang to ~10 min of compute (NESS-hang prevention USER directed).

## Risk flags + NESS-hang prevention (USER 2026-06-26)

- **Sub-arm checkpointing:** `_write_arm_partial` after each arm completes; any kill loses at most 1 arm of compute (vs whole-seed NESS pattern that lost 51min/0 units).
- **atexit partial-flush:** signals + tracks completed arms.
- **Per-checkpoint progress logs:** every CHECKPOINT_INTERVAL=250 cycles -> liveness signal ~once per 50s nominal.
- **Pre-flight per-unit wall measured:** smoke shows per-arm wall 53-87s at smoke scale; extrapolation comfortably fits 4hr cap.

## REMOTE VERIFY (local queue)

```
{"name": "gap4_two_tier_generational_W_v1",
 "script": "experiments/exp_gap4_two_tier_generational_W_v1.py",
 "prereg": "preregs/2026-06-26_gap4_two_tier_generational_W_v1.md",
 "timeout_s": 14400,
 "status": "pending",
 "gated_at": "2026-06-25T22:52:36"}
```

VERIFIED in `data/local_cpu_queue/queue.json`. Position 10 of 10 pending entries (9 ahead in flight).

## Coordination + next-arc routing

- **On HARD_PASS:** route to Skunkworks landed-VET; Research queues Phase 2 (full hyperparameter grid K x tau x gamma; N=32768 production-scale; composition with BCM rank-2).
- **On HARD_PASS_PARTIAL or MIDDLE_BAND:** Research queues hyperparameter tuning sweep + composition with NREM-replay (Cell A) for the "REPLAY as SOURCE, TWO_TIER as DESTINATION" composition predicted in research drill.
- **On HARD_FAIL_TWO_TIER_DOESNT_HELP:** route to Research for Anchor #3 (`gap4_neurogenesis_capacity_refresh_v1`); architectural pivot from "storage segregation" to "capacity expansion" path per [[research_gap4_continual_5x_drill_2026-06-26]] Prediction 4 + Section "If TWO_TIER HARD-FAIL."
- **On HARD_FAIL_PROMOTION_CORRUPTS_W_OLD (drift_reduction < -0.05):** promotion strategy mis-specified; tune importance scoring (e.g., use accuracy averaged over multiple noisy probes; or refuse-gate-confirmed instead of single-probe recall).

Per USER standing rule [[feedback-route-negatives-to-research-2x-3x-revival-drills]]: any non-HARD_PASS verdict routes a revival-drill ask to Research same cycle.

-- exp_dev (Opus 4.7 1M context)
