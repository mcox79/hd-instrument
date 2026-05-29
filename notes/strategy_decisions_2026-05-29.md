# Strategy decisions 2026-05-29

## v269 -> v270 BATCHED 6-VERDICT @ 2026-05-29 first post-reset cycle (saad_solla_v16_n8192 4TH-AXIS HARD_PASS at N=8192 RELIABILITY-RECALC + bet_b_4stage_phaseD_aweight_v2 MIDDLE_BAND 3RD SUB-0.80 PERSISTENCE + axis1_mb_chunk8_v1_n4096 MIDDLE_BAND DEEP-OVER-CAP CONTINUATION + 3 KERDOCK-EVEN-LOG2 SCRIPT_BUG NEW SUB-FLAVOR LABEL-VS-HONEST 124th-126th + CONSOLIDATED Kerdock-vuln structural sweep routing)

**Trigger.** Six verdicts arrived in one batch (first post-reset cycle). All readable metrics fetched via remote bridge (`_source=remote` for V1/V2/V3); local-stale-smoke fallback flagged for V4/V5/V6 (production crashed pre-emit). Pause flag check: `data/orchestrator_paused.flag` ABSENT (verified) = ACTIVE state.

### Verdict 1: bet_b_4stage_phaseD_aweight_v2 FOURSTAGE_MIDDLE_BAND (HONEST; 3rd sub-0.80 persistence event)

**Evidence (remote authoritative):**
- verdict_tag=FOURSTAGE_MIDDLE_BAND wall_s=992.
- verdict_msg: `4-stage partial: retention_A=0.751 retention_B=0.852 retention_C=0.801. Phase D adds load but mechanism survives partially.`

**Step 0 honest re-read:** ret_A=0.751 < 0.80 HP bar; ret_B=0.852 ≥ 0.80; ret_C=0.801 ≥ 0.80 (borderline). Caller's framing as "axis-3 A-weighted rescue; classify" was neutral (no over-claim). Stage-A continues to refuse the 0.80 HP bar across 3 axis-rescue variants (v269 rehab_epochs_v3 ret_A=0.742 + v269 batch128_v1 ret_A=0.748 + v270 phaseD_aweight_v2 ret_A=0.751). Phase-D A-weighted axis-3 lifts ret_A by +0.003 vs batch128 and +0.009 vs rehab_epochs, but neither this nor stage-C (0.801, borderline) is a robust pass. Honest reading: STAGE-A SUB-BAR CEILING STRUCTURALLY CONFIRMED across 3 independent rescue axes (epochs, batch-size, loss-weighting); the partial mechanism survival message is HONEST.

**Cap_map move:** Bet B 4-stage 🟡 UNCHANGED at row level. Annotation: "v270 bet_b_4stage_phaseD_aweight_v2 FOURSTAGE_MIDDLE_BAND ret_A=0.751 ret_B=0.852 ret_C=0.801 = 3RD INDEPENDENT AXIS-RESCUE STAGE-A SUB-0.80 PERSISTENCE (after v269 rehab_epochs_v3 ret_A=0.742 and v269 batch128_v1 ret_A=0.748). Stage-A < 0.80 bar is now a STRUCTURALLY CONFIRMED CEILING across (epochs / batch-size / loss-weighting) rescue axes — Bet B 4-stage row is sub-bar-ceiling-confirmed pending stage-A architectural rescue. Stage-B + Stage-C cross the bar on this axis (B=0.852, C=0.801) confirming the partial-survival framing — the mechanism CAN retain at later stages; the bottleneck is specifically the first-stage A consolidation. Product narrative: 4-stage CL is partial (3/4 stages) at all measured rescue axes; for Tier-1 promotion, need stage-A architectural innovation, not training-axis tuning."

### Verdict 2: saad_solla_v16_n8192 SS_V16_HARD_PASS (HONEST; FIRST M-axis HARD_PASS at N=8192 = 4TH INDEPENDENT AXIS — RELIABILITY-RECALC EVENT)

**Evidence (remote authoritative):**
- verdict_tag=SS_V16_HARD_PASS wall_s=6076; N=8192; M_fracs=[0.25, 0.5]; 2/2 seeds at BOTH M_frac.
- verdict_msg: `SAAD-SOLLA PLATEAU M-ROBUST: plateau holds at BOTH M_frac=[0.25, 0.5]. M_fracs=[0.25, 0.5] pass_results={'0.25': {pass_seeds: 2, total: 2}, '0.5': {pass_seeds: 2, total: 2}} N=8192 f_sweep...`

**IMPORTANT (per caller):** queue.json carries a STALE `error: metrics_invalid: missing_fields: ['verdict', 'summary']` from a previous attempt; fresh metrics.json today is CLEAN HARD_PASS. Trust fresh remote metrics, IGNORE stale queue.json error field. This is NOT a DISPATCH_FAILURE_MISCLASSIFICATION catch under the v269 refined criterion (the stale queue.json error pre-dates the fresh metrics.json; the current data clean-passes).

**Step 0 honest re-read:** 2/2 seeds × 2 M_fracs at N=8192 production-scale = 4 cells all PASS. The "M-robust" framing is HONEST: both M_fracs in {0.25, 0.5} = 2x M-density variation passes the plateau gate. Independent-axis count vs prior:
- v15 5-seed plateau (f_sweep / SNR axis); production-scale at N=8192.
- v17 codebook (codebook-axis); production-scale at N=8192.
- v16 M-density (this verdict; M_frac axis); production-scale at N=8192.
- v6/v252 N=8192 2-seed FULL HARD_PASS (foundational axis); production-scale at N=8192.

This is the **4th independent axis** at production-scale N=8192 with multi-seed confirmation. Honest reading: Saad-Solla framework anchor is the strongest-corroborated row in cap_map at this date (production-scale on 4 independent axes), warranting framework-reliability LIFT.

**Cap_map move:** Saad-Solla LEADING ✅ row UNCHANGED at status level (already ✅). RELIABILITY-RECALC: framework-reliability specific 68-81% (v269) → **70-83% LIFT (+2%)** — the 4th-axis production-scale corroboration is the highest-evidence-density single Saad-Solla event since v252. Annotation: "v270 saad_solla_v16_n8192 SS_V16_HARD_PASS 2/2 seeds × 2 M_frac {0.25, 0.5} at N=8192 production-scale = FIRST M-axis HARD_PASS at production scale; 4TH INDEPENDENT AXIS confirmation (after v15 f_sweep/SNR + v17 codebook + v6/v252 foundational). Saad-Solla LEADING ✅ row now production-scale-corroborated on 4 axes — strongest cap_map row evidence-density to date. NOTE: queue.json `metrics_invalid` error field is STALE from a previous attempt; current remote metrics.json clean — NOT a DISPATCH_FAILURE_MISCLASSIFICATION catch under v269 refined criterion (stale-error-with-clean-current-metrics is a new sub-pattern; honest reading dispositive). N=8192 5-seed envelope-extension pending (v15+v17+v16 all 2-seed multi-N; 5-seed defense-in-depth filed for v270 follow-up)."

### Verdict 3: axis1_mb_chunk8_v1_n4096 C8_MIDDLE_BAND (HONEST; DEEP-OVER-CAP CONTINUATION; chunk progression)

**Evidence (remote authoritative):**
- verdict_tag=C8_MIDDLE_BAND wall_s=121; N=4096; M_fracs=[25, 32]; pass_collapse=0/9.
- verdict_msg: `PARTIAL_COLLAPSE: ret_low=0.1600. mean_ret_by_M={25.0: 0.16, 32.0: 0.13} ret_low(M=25.0)=0.1600 ret_high(M=32.0)=0.1300 pass_collapse=0/9 N=4096`

**Step 0 honest re-read:** ret_low=0.16 (M/N=25); ret_high=0.13 (M/N=32); pass_collapse=0/9. The script pre-registers a "collapse" criterion that FAILS (0/9 = no cell passes the collapse threshold) — but the per-cell numerical retention values are DEEP in the over-capacity collapse regime (0.13-0.16 ≈ chance level for 4-class classification). The MIDDLE_BAND verdict_tag accurately reflects: "neither clean HP nor clean HF — substrate is in deep-collapse where retention is barely above chance but the script's collapse criterion has a sharper threshold." Caller's framing as "boundary M-sweep chunk 8; classify" was neutral. Honest reading: DEEP OVER-CAP CONTINUATION of v264 chunk7 TAIL_SIGNAL_DEEP_OVER_CAP at M/N=16-20; chunk8 extends to M/N=25-32 and confirms collapse persists at these tail M_fracs. No new substrate-physics finding beyond corroborating the over-capacity collapse tail.

**Cap_map move:** AXIS-1 (M×β phase diagram) coverage row UNCHANGED at row level (annotation extends chunk-progression). Annotation: "v270 axis1_mb_chunk8_v1_n4096 C8_MIDDLE_BAND M/N∈{25, 32} = DEEP-OVER-CAP TAIL CONTINUATION of v264 chunk7 TAIL_SIGNAL DEEP_OVER_CAP at M/N=16-20; chunk8 ret ∈ [0.13, 0.16] confirms deep-collapse persistence at M/N∈[25, 32]. Pattern: M/N=4-8 clean (chunk5 mono [0.605→0.315→0.202]), M/N=16-20 tail-signal (chunk7), M/N=25-32 deep-collapse (chunk8). Over-capacity ceiling at M/N≈8-12 with smooth degradation into chance level by M/N=25+. AXIS-1 coverage row band UNCHANGED (chunks are ongoing scan, not closure event)."

### Verdicts 4-6: kf3_multisub_v3_n8192 + t1_beta_sweep_v2_n8192 + t2_codebook_boundary_v2_n8192 — KERDOCK-EVEN-LOG2 SCRIPT_BUG (3 NEW LABEL-VS-HONEST CATCHES — sub-flavor SCRIPT_PRECONDITION_VIOLATION 124th-126th)

**Evidence (caller forensics + script inspection):**
- All 3 anchors ran wall_s ∈ [13, 22] = pre-work crash.
- All 3 source scripts import `make_kerdock_4coset_codebook` from `exp_wave14y_erase_kerdock_v3.py`.
- Inspection of `make_kerdock_4coset_codebook` (lines 159-172): explicitly raises `ValueError(f"N={N} requires even log2(N) for MM construction (got n_log2={n_log2})")` when `n_log2 % 2 != 0`.
- N=8192 has log2(8192)=13 (ODD) → ValueError raised pre-work for all 3 anchors.
- Local metrics.json for all 3 are STALE PRE-SHIP SMOKE artifacts at N=1024 (`_source=local`), MASQUERADING as MIDDLE_BAND because the smoke runs DID work at N=1024 (log2=10, even).

**Step 0 honest re-read:** Caller correctly identified all 3 as Kerdock-even-log2 SCRIPT_BUGs — NOT misclassifications of the v269 DISPATCH_FAILURE_MISCLASSIFICATION type (those had remote metrics with HARD_PASS-flavored verdict_tag). These are a NEW SUB-FLAVOR: SCRIPT_PRECONDITION_VIOLATION — the script's input-validation assertion fails BEFORE any production work; queue.json `failed` is honest but the LOCAL metrics.json is STALE PRE-SHIP SMOKE that misleadingly carries MIDDLE_BAND verdict_tag.

Honest readings:
- V4 kf3_multisub_v3_n8192: SCRIPT_PRECONDITION_VIOLATION (Kerdock-even-log2). Local metrics is stale N=1024 smoke. Rescue: reship at N=4096 (log2=12) or N=16384 (log2=14).
- V5 t1_beta_sweep_v2_n8192: SAME SCRIPT_PRECONDITION_VIOLATION. Same rescue.
- V6 t2_codebook_boundary_v2_n8192: SAME SCRIPT_PRECONDITION_VIOLATION. Same rescue.

3 NEW LABEL-VS-HONEST CATCHES sub-flavor SCRIPT_PRECONDITION_VIOLATION (124th-126th). Distinct from DISPATCH_FAILURE_MISCLASSIFICATION:
- DISPATCH_FAILURE_MISCLASSIFICATION (v265+v267+v268+v269): remote metrics EXIST + verdict_tag is HARD_PASS-flavored + queue.json status=failed.
- SCRIPT_PRECONDITION_VIOLATION (v270 NEW): remote metrics DO NOT exist + LOCAL metrics are STALE pre-ship smoke at smaller N + verdict_tag in local-stale is MIDDLE_BAND/HARD_FAIL flavored (misleading caller into reading them as real substrate verdicts).

**Cap_map move:** NO row-level moves for V4-V6 (no substrate-physics signal; pre-work crashes). 0 substrate-physics signal in any direction. ROW STATUS UNCHANGED across all touched rows (KF-3 multi-substrate, β-axis phase-boundary, codebook-axis row).

### CONSOLIDATED Kerdock-even-log2 vulnerability STRUCTURAL ROUTING (per caller's upstream context)

Per caller's UPSTREAM CONTEXT analysis: 5-6 more pending anchors at N=8192 share the same SCRIPT_PRECONDITION_VIOLATION vulnerability:
- axis1_mb_chunk9_v1_n8192 (confirmed via grep: imports make_kerdock_4coset_codebook).
- axis1_mb_chunk10_v1_n8192_fine (confirmed via grep: imports make_kerdock_4coset_codebook).
- t3_susceptibility_v2 (per caller — currently running per queue state).
- pb3_extended_v4 (per caller).
- possibly kf2_be1_n8192 family (6 anchors: fp32/fp16/int8/int4/int2/int1 — DOMAIN check needed; if they use Kerdock, they'll all crash).

File ONE CONSOLIDATED routing note: `notes/strategy_request_to_exp_dev_v270_kerdock_even_log2_consolidated_rescue_2026-05-29.md` covering ALL pending Kerdock-N=8192 anchors at once (not per-anchor reships), per [[feedback-rescue-sketch-first-sequencing]] (cheapest = batch the structural rescue, not 6 individual rescue routings).

Rescue contract for exp_dev (cheapest-first):
- (a) **Audit** pending N=8192 anchors for `make_kerdock_4coset_codebook` usage (grep). Identify the COMPLETE vulnerable set BEFORE reshipping.
- (b) **Reship at N=4096** (log2=12, even) — cheaper than N=16384 (log2=14, even); use as default unless the experiment SPECIFICALLY needs N=8192 production-scale corroboration of a prior N=4096 finding.
- (c) **Reship at N=16384** ONLY for anchors that demand production-scale (N=8192 was the original target precisely because N=4096 was already done).
- (d) **Structural fix candidate** (longer-term, NOT this rescue): modify `make_kerdock_4coset_codebook` to GRACEFULLY DOWNGRADE to nearest-even-log2 N (e.g., N=8192 → use codebook at effective N=4096 embedded in N=8192 with padding) OR have the script auto-route to nearest-even-N at queue-add time.

NOT autonomous (d) selection at verdict_handler layer — flag (d) as STRATEGY-level architectural question for next strategy cycle.

### v269 -> v270 PORTFOLIO + RELIABILITY MOVES

- **Saad-Solla LEADING ✅ row UNCHANGED + 4TH AXIS PRODUCTION-SCALE STRONGEST-EVIDENCE-DENSITY-TO-DATE** (v16 SS_V16_HARD_PASS 2/2×2-M_frac N=8192).
- **Framework reliability specific 68-81% (v269) → 70-83% LIFT (+2%)** — Saad-Solla 4th-axis production-scale is a single-event reliability-recalc trigger (per dispatch model=opus designation).
- **Framework reliability product-feature 87-97% UNCHANGED** — Saad-Solla is a framework-anchor row not directly a killer-feature; product-narrative spillover at +0% for this batch.
- **Framework reliability general 73-83% UNCHANGED** — no general-class shift.
- **Bet B 4-stage 🟡 UNCHANGED + STAGE-A SUB-0.80-BAR CEILING STRUCTURALLY CONFIRMED** (v270 phaseD_aweight_v2 = 3rd independent axis-rescue all sub-bar on stage A; v269 rehab_epochs_v3 + v269 batch128_v1 + v270 phaseD_aweight_v2). Annotation only.
- **AXIS-1 (M×β phase diagram) row UNCHANGED + DEEP-OVER-CAP TAIL CHUNK-PROGRESSION** (v270 chunk8 M/N∈{25, 32} ret∈[0.13, 0.16] continues v264 chunk7 tail). Annotation only.
- **KF-3 multi-substrate row UNCHANGED** (V4 SCRIPT_BUG, no signal). Annotation: "v270 kf3_multisub_v3 SCRIPT_PRECONDITION_VIOLATION (Kerdock-even-log2 N=8192); rescue routing filed for N=4096 or N=16384 reship; v2 DUAL-framing from v262 STANDS as load-bearing row evidence."
- **β-axis phase-boundary row UNCHANGED** (V5 SCRIPT_BUG, no signal). Annotation: "v270 t1_beta_sweep_v2_n8192 SCRIPT_PRECONDITION_VIOLATION (Kerdock-even-log2); rescue routing filed; v269 t1_v2 fine-resolution β_c=10 deterministic STANDS as load-bearing."
- **Codebook-axis row UNCHANGED** (V6 SCRIPT_BUG, no signal). Annotation: "v270 t2_codebook_boundary_v2_n8192 SCRIPT_PRECONDITION_VIOLATION (Kerdock-even-log2); rescue routing filed; v267 t2 codebook-axis HARD_PASS STANDS as load-bearing."
- **Non-eq stat-mech class UNCHANGED 66-76%** (no non-eq probe this batch).
- **Portfolio 14 + 31 UNCHANGED** (no row additions, no portfolio-count moves; Bet B partial-survival on stage-B/C continues but does not warrant 4-stage row promotion).
- **Cumulative HONEST observations**: 150 (v269) → **156 (+6: 3 honest substrate-physics + 3 SCRIPT_BUG honest-failures all read correctly via Step 0)**.
- **Cumulative LABEL-VS-HONEST catches**: 123 (v269) → **126 (+3: V4 + V5 + V6 all SCRIPT_PRECONDITION_VIOLATION new sub-flavor 124th-126th)**.

### NEW SUB-FLAVOR: SCRIPT_PRECONDITION_VIOLATION (3 catches this batch)

Add to discrimination criterion (extending v269 refinement):
- **TRUE DISPATCH_FAILURE_MISCLASSIFICATION** (v265+v267+v268+v269): remote metrics EXIST + verdict_tag HARD_PASS-flavored + queue.json `failed`.
- **GENUINE FAST HARD_FAIL** (v269): remote metrics EXIST + verdict_tag HARD_FAIL + queue.json `failed`.
- **GENUINE SUBSTANTIVE FAILURE** (v269): NO remote dir + no remote metrics + no script-precondition signature in runner.log.
- **NEW v270 SCRIPT_PRECONDITION_VIOLATION**: NO remote dir + LOCAL metrics is STALE PRE-SHIP SMOKE at smaller N + runner.log shows pre-work ValueError/assertion + script source has explicit precondition assertion. This sub-flavor is distinct because the LOCAL stale-smoke verdict_tag (typically MIDDLE_BAND) MASQUERADES as a real verdict — Step 0 must check (a) `_source` field and (b) script source for precondition assertions before accepting any local-stale-smoke reading.

PROT-019 candidate v270: extend the verdict_handler Step 0 auto-cross-check from "remote metrics existence" (v267 candidate) to ALSO include "script-precondition source inspection when local-stale fallback is used and N mismatches anchor suffix". Defer to next strategy cycle for PROT-019 lock vote.

### NEW routings filed (v270)

1. `notes/strategy_request_to_exp_dev_v270_kerdock_even_log2_consolidated_rescue_2026-05-29.md` — CONSOLIDATED rescue for all pending Kerdock-N=8192 anchors (V4/V5/V6 reships + upstream chunk9/chunk10/pb3_v4/t3_susceptibility_v2 audit + kf2_be1 family audit).

(NO separate per-anchor reship routings — per caller's structural diagnosis, ONE consolidated note is the correct level of granularity per [[feedback-rescue-sketch-first-sequencing]] cheapest-first.)

### Queue-refill (Step 2 pipeline-pacing) decision

Pause flag `data/orchestrator_paused.flag` ABSENT (verified). Queue state via bridge (not stale, `is_stale()=False`):
- `overnight_queue`: 16 pending+running (NOT empty).
- `cpu_queue`: 0.
- `local_cpu_queue`: 0.

Per [[feedback-pipeline-pacing]]: queue-depth-0 trigger is the loudest signal; `overnight_queue` has 16 pending → NOT empty → NO exp_dev pipeline-pacing dispatch. The 6 verdicts arriving did free slots, but the queue is not yet empty.

Per [[feedback-no-padding-experiments]]: do NOT add marginal variants; the Kerdock consolidated rescue routing (filed above) is the proper next-batch work via routing_handler pickup.

**Decision: NO exp_dev pipeline-pacing dispatch this batch.** Queue refill NOT triggered (overnight=16 pending; conditions for pipeline-pacing dispatch not met).

### PROT compliance (v270)

- **PROT-004/006**: 0 row closures; 0 row addition; 0 row promotions/demotions; 1 framework-reliability LIFT (specific +2%). 1 rescue routing filed CONSOLIDATED (cheapest-first per [[feedback-rescue-sketch-first-sequencing]]: ONE structural note over 6 per-anchor notes).
- **PROT-007**: history.md UPDATED with v270 row.
- **PROT-008**: 1 band lift validator-grade (Saad-Solla 4th-axis production-scale N=8192 2/2×2-M_frac = highest single-event evidence density to date for the row).
- **PROT-009**: cap_map.md (v269 → v270 batched line; row annotations) + cap_map_history.md (v270 row) + strategy_decisions_2026-05-29.md (this entry) + visibility_decisions_2026-05-29.md (one-line) + 1 routing file staged atomically; **181st PROT-009 paired commit**.
- **PROT-018**: 6 anchors — 5 honor `_n<N>` binding contract (bet_b_4stage_phaseD_aweight_v2 has `_v2` not `_n<N>` = pre-PROT-018 backlog; saad_solla_v16_n8192 ✓; axis1_mb_chunk8_v1_n4096 ✓; kf3_multisub_v3_n8192 ✓; t1_beta_sweep_v2_n8192 ✓; t2_codebook_boundary_v2_n8192 ✓). All 6 anchor N suffixes match queue-claim; 1 lacks suffix entirely (bet_b_4stage).
- **[[feedback-verdict-msg-honest-reread]]**: 150 → 156 obs (+6); LABEL-VS-HONEST 123 → 126 (+3 SCRIPT_PRECONDITION_VIOLATION new sub-flavor 124th-126th).
- **[[feedback-trust-queue.json-wall_s]]**: APPLIED to all 6 (V1/V2/V3 via remote metrics; V4/V5/V6 via runner.log + remote-dir absence + script-source inspection three-way triangulation).
- **[[feedback-dispatch-context-trust]]**: V2 caller's note ("queue.json has stale error field; trust fresh metrics") VERIFIED — fresh remote metrics.json clean, stale-error is a previous-attempt artifact; new sub-pattern STALE_QUEUE_ERROR_WITH_CLEAN_CURRENT_METRICS distinct from DISPATCH_FAILURE_MISCLASSIFICATION.
- **[[feedback-rescue-sketch-first-sequencing]]**: ONE consolidated structural rescue routing > 6 per-anchor reships; cheapest-first applied at structural-batching level.
- **[[feedback-rehabilitation-after-rejection]]**: V4/V5/V6 SCRIPT_BUGs are NOT rejection events (no substrate-physics signal); rescue sketches at script-precondition level not capability-rejection level; no 3-5 rescue arms required.
- **[[feedback-subagent-permission-inheritance]]**: LOCAL commit only; push deferred to main thread (orchestrator).
- **[[feedback-no-experiment-design-in-prompts]]**: routing file specifies TASK + WHY + CONTRACT + AUTONOMY only.
- **[[feedback-pipeline-pacing]] + [[feedback-no-padding-experiments]]**: overnight_queue=16 NOT empty → NO refill dispatch.
- **[[feedback-cap-map-update-protocol]]**: atomic commit of cap_map.md + cap_map_history.md + strategy_decisions_2026-05-29.md + visibility_decisions_2026-05-29.md + 1 routing file. Commit message: `Cap map: v269 -> v270 (BATCHED 6-VERDICT: saad_solla_v16_n8192 SS_V16_HARD_PASS 4TH-AXIS PRODUCTION-SCALE N=8192 2/2x2-M_frac framework-reliability specific 68-81%->70-83% LIFT +2% RELIABILITY-RECALC + bet_b_4stage_phaseD_aweight_v2 FOURSTAGE_MIDDLE_BAND ret_A=0.751 3RD-INDEPENDENT-AXIS STAGE-A SUB-0.80-BAR CEILING STRUCTURALLY CONFIRMED + axis1_mb_chunk8_v1_n4096 C8_MIDDLE_BAND M/N=25-32 DEEP-OVER-CAP TAIL chunk-progression + 3 KERDOCK-EVEN-LOG2 SCRIPT_PRECONDITION_VIOLATION new sub-flavor LABEL-VS-HONEST catches 124th-126th V4 kf3_multisub_v3 V5 t1_beta_sweep_v2 V6 t2_codebook_boundary_v2 all N=8192 odd-log2 ValueError-at-import pre-work crash with local-stale-smoke at N=1024 masquerading as MIDDLE_BAND; 1 CONSOLIDATED Kerdock-vuln structural rescue routing filed covering V4/V5/V6 + upstream chunk9/chunk10/pb3_v4/t3_susceptibility_v2/kf2_be1-family audit at N=4096 or N=16384; portfolio 14+31 UNCHANGED; framework reliability specific 68-81%->70-83% LIFT product-feature 87-97% UNCHANGED general 73-83% UNCHANGED; HONEST 150->156 (+6); LABEL-VS-HONEST 123->126 (+3); 181st PROT-009 paired commit; verdict_handler sub-agent inline strategy+visibility no Agent sub-dispatch)`.
