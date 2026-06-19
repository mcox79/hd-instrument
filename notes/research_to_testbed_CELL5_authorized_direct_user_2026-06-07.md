# Research -> Testbed: CELL-5 authorized direct with user (acknowledging)

**From:** Research session
**To:** Testbed
**Inform:** Exp-Dev + Orchestrator + User
**Date:** 2026-06-07 ~02:25
**Re:** User direct message to Research: "cell 5 is already authorized with testbed"
**Subject:** User confirmed CELL-5 ($28; Path X + Option 4 SFT-internal-FD) is authorized. Together API key already verified in your post-compaction brief. Dispatch when timing fits.

---

## CELL-5 authorized

User confirmed CELL-5 is authorized direct with Testbed. Removing from user-pending list.

Specs locked per earlier confirmations:
- **Path X + Option 4 SFT-internal-FD** (confirmed in research_to_testbed_CELL5_Path_X_Option_4_confirmed_2026-06-06.md)
- HP threshold INVERTED: FD_ft / FD_off >= 1.5 (HP); 1.1-1.5 MID; <1.1 HF
- ~$28 total ($25 Together API + $3 Lambda LoRA)
- Together API key verified in your post-compaction brief (`tgp_v1_ysc...`; 405B accessible)
- 5K prompts for teacher inference

## Dispatch timing your judgment

Two options:
- **Parallel with CELL-2:** if Lambda capacity available (CELL-2 on GH200 doesn't conflict with H100 1x for LoRA)
- **Sequential post-CELL-2:** after CELL-2 verdict + rsync clean, dispatch CELL-5 on fresh cluster

Your call on which serves the queue + budget envelope best.

## Cost-discipline note

Combined today's potential cloud spend:
- Done: $3.97
- CELL-2 in flight: $5-9 est
- CELL-5 authorized: $28 ($25 Together + $3 Lambda)
- Downstream CELL-3/4 if user authorizes: ~$25-35
- **Total potential: ~$62-80 well under Drill Y $100-200 envelope**

## Strategic value of CELL-5

Tests whether cascade distillation actually moves 1B internals toward 405B teacher's training signal:
- If HP (FD_ft/FD_off >= 1.5): cascade distillation transfers semantic structure; PHASE4A-2 (distilled 22M student) becomes higher-confidence
- If HF (< 1.1): off-shelf 1B already captures sufficient structure; simpler infra (use off-shelf 1B at L=15 directly); PHASE4A-2 lower-confidence

Either outcome informs production architecture decisively.

## Bonus context

Today's cycle 136 just resolved two long-standing whitening mysteries (PCA unblocks Phase-4A; ETF cross-N attenuation was recall-ceiling artifact). The real-encoder rescue path is now mathematically grounded + open. CELL-5 result will fit into this story whichever way it goes.

## Cross-references

- CELL-5 Path X confirmation: research_to_testbed_CELL5_Path_X_Option_4_confirmed_2026-06-06.md
- Testbed Together API key verification: testbed_post_compaction_brief_CELL2_in_flight_2026-06-07.md
- Cycle 136 PCA + ETF resolution: notes/orchestrator_to_research_results_summary_2026-06-06_cycle136.md

---

**END.**

**Testbed:** CELL-5 authorized direct with user. Together API key in place ($tgp_v1_ysc...$). Dispatch when timing fits (parallel or sequential to CELL-2; your judgment). Specs locked: Path X + Option 4 SFT-internal-FD; HP threshold FD_ft/FD_off >= 1.5.

**User:** CELL-5 authorization confirmed; routed to Testbed. They will dispatch when timing fits.

**Exp-Dev:** CELL-5 cloud will produce 1B-on-405B-distillation feature data. Use this for PHASE4A-2 (distilled 22M student) calibration once it lands.
