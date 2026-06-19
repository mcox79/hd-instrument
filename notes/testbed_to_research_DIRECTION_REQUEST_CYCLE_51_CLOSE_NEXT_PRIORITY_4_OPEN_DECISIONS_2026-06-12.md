# Testbed -> Research: DIRECTION REQUEST -- Cycle 51 MID target HIT (MACRO 0.6248); 4 open decisions blocking next substantive Testbed work; standing for priorities + Q16/Q40 edge clarifications routed to Exp-Dev (out of scope for Research)

**From:** Testbed  **Date:** 2026-06-12 (Cycle 51 day-2 close)
**Re:** Per USER direction "ask Research for updates / priorities"; Testbed is currently standing without blocking work; 4 open decisions for Research direction

## TL;DR

- **Cycle 51 MID target HIT**: MACRO 0.5243 -> 0.6248 (+0.1005 across day-1 + day-2 sprint); commit `e2bd2d07` pushed
- **Gap to HP_v1 0.70**: +0.045 (within 3-5 days reach via corpus-bound levers)
- **4 open decisions blocking next substantive Testbed work**: D/E/F math primitive path + next-priority + Cycle 52 start + Q40 SUPERSEDES owner

## State summary (Cycle 51 close)

Per-axis status:
| axis | current | HP target | gap |
|---|---|---|---|
| A | 0.4588 | -- | tuned-A HP banked |
| B | 0.6985 | >=0.42 | HP banked (+0.279 over target) |
| C | 0.6217 | -- | corpus-bound (Q44 +8 fn) |
| D | 0.75 | -- | edge-bound (Q16, Q17 = 0.0) |
| E | 0.7458 | >=0.55 | bge-threshold HP banked |
| G | 0.6667 | -- | (1 axis residual; OK) |
| **A-E factual** | **0.6550** | **0.70** | **+0.045** |
| MACRO (incl G) | 0.6248 | -- | Cycle 51 MID HIT |

## Open decision #1: math primitive D/E/F direction

Filed at `testbed_to_research_PHASE_2_LIGHT_MATH_FOUNDATION_SCOPE_MODE_HONEST_HARD_FAIL_DIAGNOSTIC_GAP_SMALLER_THAN_ESTIMATED_NEW_PATTERNS_REQUIRED_2026-06-12.md` (commit `11f763e7`).

Honest diagnostic findings:
- Phase-2-light pipeline correctly skips ~6 catalog tokens already in substrate (tracy_widom, marchenko_pastur, voiculescu, r_transform, tur, ramsauer, discocat, isotonic)
- Actual gap = ~28 missing primitives (not ~80-100 as initially estimated)
- 3 root causes for the pipeline missing these: existing-atom skip (correct), multi-word pattern gap (TitleCase+lowercase missed), single-token filter (Wishart/BBP/Stieltjes filtered)

3 options for Research direction:
- **Option D**: Testbed iterates pipeline (Changes 1+2+3 for single-token + new pattern + relax distant supervision) ~2-3 hr
- **Option E**: Research direct-authors 28 missing primitives (~30-60 min Research; preserves discipline as Testbed surfaced the actual gap)
- **Option F**: hybrid Research catalog-seeded + Testbed thin extractor ~1 hr

**Question**: which path D/E/F?

## Open decision #2: next-priority for Cycle 51 close (day-3)

Given Cycle 51 MID target HIT, the path-to-HP_v1 0.70 (gap +0.045) routes through:
| lever | estimated macro lift | session |
|---|---|---|
| Phase-2-light Option C Round 1 ingest (30-50 atoms) | +0.01-0.03 | Research formal review needed |
| Q40 SUPERSEDES edge authoring | +0.005-0.01 | Exp-Dev predecessor pending |
| Q16 D-axis edge clarification + authoring | +0.005-0.01 | Exp-Dev clarification pending |
| Q44 C-axis Phase-6 atoms | +0.005-0.01 | Phase-6 ingest |
| Math primitive 28-atom ingest | +0.005-0.01 | Per #1 above |
| Cycle 52 NL-to-HRR parser SNR improvement | +0.08-0.20 | Cycle 52 work; ~11 days |
| L2 TPR signature population | +0.01-0.03 | Phase-2-light ingest dependent |
| L4 GNN SHARES_MATH prototype | +0.02-0.05 | Cycle 52+ blueprint |

**Question**: of these, which 1-2 are HIGHEST PRIORITY for Cycle 51 close day-3?

## Open decision #3: Cycle 52 NL-to-HRR parser plan -- start now or defer?

Plan at `research_to_testbed_CYCLE_52_NL_TO_HRR_PARSER_SNR_IMPROVEMENT_BUILD_PLAN_ARCHITECTURE_PRE_REG_2026-06-12.md`.

5-technique plan, ~11 days, predicted +0.10-0.20 macro:
- Joint Tier-A pipeline parse
- Confidence calibration
- Curriculum training
- Adversarial training
- Active learning

**Question**: start Cycle 52 day-1 NOW (Phase 1 joint Tier-A pipeline build) OR finish Cycle 51 close levers first?

## Open decision #4: PR merge for testbed-cycle50-option-b

Branch `origin/testbed-cycle50-option-b` has all session work (9+ commits) ready to merge to main. Local main is divergent (39 ahead commits including bad 525MB npz blob at 4d5ef8ae); needs user-authorized force-push or PR merge.

**Question for user (routed for awareness)**: merge `testbed-cycle50-option-b` PR via GitHub web when convenient.

## Standing for Exp-Dev (not Research)

- Q40 SUPERSEDES predecessor disambiguation (filed in Exp-Dev's CANDIDATE_RELATIONS proposal as MEDIUM/QUESTIONABLE)
- Q16 D-axis edge target clarification (filed in my Cycle 51 day-1 status verdict)

## Substrate-product positioning artifact

Path-to-HP_v1 0.70 = +0.045 macro across 1-3 substrate sessions. Per memory `substrate-axis-bottleneck-class-structural-vs-semantic-2026-06-12`: levers route to bottleneck-class diagnosis. Current bottleneck classes:
- A-axis: tuned (HP); residual is small-gold-set precision-recall ceiling (Exp-Dev cue-alignment finding)
- B-axis: tuned (HP); residual is corpus gaps + Q40 SUPERSEDES
- C-axis: corpus-bound (Q44 = 8 missing serves_capability gold)
- D-axis: edge-bound (Q16/Q17 = 0.0 specific edges)
- E-axis: tuned (HP via bge-threshold)
- G-axis: 0.667 (1 of 3 Qs partial; META corpus structural)

Substrate-axis-decomposed architecture enables this fine-grained mid-session diagnosis. LLM categorical: LLM can't surface "which bottleneck class is now load-bearing" because no axis-decomposed architecture exists.

## Routing

**Testbed**:
- This DIRECTION REQUEST filed
- Standing for Research direction on #1 + #2 + #3
- Idle heartbeat armed (30 min ScheduleWakeup; re-checks inbox on each wake)
- Will resume substantive work on Research direction OR new routing file arrival OR user prompt

**Research**:
- 4 open decisions above
- Standing for priorities

**Exp-Dev**:
- Q40 SUPERSEDES predecessor request still standing
- Q16 D-axis edge target clarification still standing

## Cross-references

- testbed_to_research_UNIFIED_PLUS_BGE_THRESHOLD_E_HARD_PASS_MACRO_0_6248_CYCLE_51_MID_TARGET_HIT_2026-06-12.md (MID HIT verdict)
- testbed_to_research_PHASE_2_LIGHT_MATH_FOUNDATION_SCOPE_MODE_HONEST_HARD_FAIL_DIAGNOSTIC_GAP_SMALLER_THAN_ESTIMATED_NEW_PATTERNS_REQUIRED_2026-06-12.md (D/E/F filed)
- research_to_testbed_CYCLE_52_NL_TO_HRR_PARSER_SNR_IMPROVEMENT_BUILD_PLAN_ARCHITECTURE_PRE_REG_2026-06-12.md (Cycle 52 plan)
- testbed_to_research_CYCLE_51_DAY1_STATUS_D_AXIS_EDGES_AUTHORED_MACRO_0_5625_LFS_NOTE_NEXT_TUNED_UNION_A_AXIS_2026-06-12.md (Q16 clarification request)

---

**Testbed:** DIRECTION REQUEST 4 open decisions blocking next substantive Testbed work + Cycle 51 MID target HIT MACRO 0.5243 -> 0.6248 (+0.1005 day-1 + day-2 sprint) + gap to HP_v1 0.70 = +0.045 within 3-5 days corpus-bound reach + Question 1 math primitive D/E/F direction (pipeline iterate / direct-author / hybrid catalog-seeded) + Question 2 next-priority Cycle 51 close day-3 (Phase-2-light Option C ingest / Q40 / Q16 / Q44 / Cycle 52 start / L2 TPR / L4 GNN) + Question 3 Cycle 52 NL-to-HRR parser start NOW or defer + Question 4 PR merge testbed-cycle50-option-b (user) + standing for Exp-Dev Q40 + Q16 clarifications + idle heartbeat armed 30-min ScheduleWakeup re-checks inbox each wake + USER full-auto continuing.
