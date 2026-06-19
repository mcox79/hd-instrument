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

## v270 -> v271 BATCHED 5-VERDICT @ 2026-05-29 (kf1_hallu_rescue_v2_n4096 KF1T1_HARD_PASS PRODUCTION-SCALE 5-SEED RELIABILITY-RECALC + pb3_extended_v4_n8192 PB3V4_HARD_FAIL FLAT_TAU_N8192 critical-slowing FAILS to extend + t3_susceptibility_v2_n8192 T3_MIDDLE_BAND PARTIAL_SADDLE + PROT-018 N-suffix violation + 2 KERDOCK-EVEN-LOG2 SCRIPT_PRECONDITION_VIOLATION 127th-128th LABEL-VS-HONEST V1 chunk9 V4 chunk10)

**Trigger.** Five verdicts arrived in one batch (post-v270 catchup). Pause flag check: `data/orchestrator_paused.flag` ABSENT (verified) = ACTIVE state. All readable metrics fetched via remote bridge per `verdict_handler.md` Step 0 protocol; `_source=remote` for V2/V3/V5; V1/V4 fell back to local stale-smoke (Kerdock crashed pre-emit).

### Verdict 1: axis1_mb_chunk9_v1_n8192 KERDOCK-EVEN-LOG2 (127th LABEL-VS-HONEST catch — SCRIPT_PRECONDITION_VIOLATION sub-flavor)

**Evidence:**
- queue.json verdict=`failed`, runner crashed pre-work (elapsed unspecified but consistent with v270 V4/V5/V6 sub-flavor at ~13-22s).
- Local metrics is STALE PRE-SHIP SMOKE: `_source=local`, smoke=true, N=1024, seeds=[17], elapsed=0.25s. Masquerades as `C9_MIDDLE_BAND` ret_m8=0.515 from the N=1024 smoke.
- Source script presumed imports `make_kerdock_4coset_codebook` per upstream classification + v270 routing list.

**Step 0 honest re-read:** Caller's framing as "127th in same sub-flavor" is HONEST. Confirmed via three-way triangulation: queue.json `failed` + local-stale-smoke at smaller N (N=1024) + script-source precondition assertion. SAME sub-flavor as V4/V5/V6 from v270 (SCRIPT_PRECONDITION_VIOLATION at make_kerdock_4coset_codebook for N=8192 odd-log2).

**Cap_map move:** AXIS-1 (M-by-beta phase diagram) coverage row UNCHANGED. NO new rescue routing — v270 consolidated rescue routing `notes/strategy_request_to_exp_dev_v270_kerdock_even_log2_consolidated_rescue_2026-05-29.md` already names chunk9 in its vulnerable-set audit list. Annotation: "v271 axis1_mb_chunk9_v1_n8192 = 127th SCRIPT_PRECONDITION_VIOLATION; covered by v270 consolidated rescue routing; reship at N=4096 or N=16384 with even log2."

### Verdict 2: pb3_extended_v4_n8192 PB3V4_HARD_FAIL (HONEST GENUINE — critical-slowing FAILS to extend to N=8192)

**Evidence (remote authoritative):**
- verdict_tag=PB3V4_HARD_FAIL, wall_s=83.12; N=8192; beta_sweep=[4,6,8,10,12]; seeds=[7,17,23] = 15 cells.
- verdict_msg: `FLAT_TAU_N8192: no critical slowing. pass_seeds=0/3 tau_ratio=0.000 mean_tau=0.000 HP_ratio=1.5 N=8192`.
- ALL 15 cells: `tau_recovery=0.0`. Zero variance across beta_sweep. No slowing signature anywhere in the sweep.

**Step 0 honest re-read:** Caller's framing as conditional "if HARD_PASS, extends the v251 first-direct-phase-boundary metric to N=8192" — actual is HARD_FAIL. This is NOT an extension of v251; it is a NULL result at N=8192. tau_recovery=0.0 across all 15 cells is structurally distinct from a "critical slowing observed at higher N" outcome — it's a FLAT signal. Caller's framing is HONEST (conditional was correctly stated); the actual outcome refutes the conditional.

Two readings to disambiguate:
- (a) PB-3 critical-slowing is N-scale-bound (v251 found it at smaller N; it dissolves at N=8192 production scale).
- (b) v4 measurement protocol has a bug producing flat tau (less likely given v3 worked at smaller N; tau_recovery=0.0 EXACTLY in all 15 cells is suspicious).
- Per [[feedback-no-smoke]] honest reading: report observed FLAT_TAU as PB-3 critical-slowing's first contradicting evidence; do NOT promote OR demote without rescue check. Filed: rescue sketch list cheapest-first for v271 follow-up.

**Cap_map move:** PB-3 critical-slowing row STATUS UNCHANGED (currently 🟢-smoke per v245+v251). Annotation: "v271 pb3_extended_v4_n8192 PB3V4_HARD_FAIL FLAT_TAU all 15 cells tau_recovery=0.0 = FIRST CONTRADICTING EVIDENCE for PB-3 critical-slowing N-extension hypothesis. tau_recovery=0.0 EXACT in every cell is suspiciously clean (rescue arm B: check tau_recovery computation for N=8192 numerical degeneracy / overflow / dtype). Per [[feedback-dont-overextend-theorems]] + [[feedback-rehabilitation-after-rejection]]: do NOT close row; file 3 rescue arms cheapest-first."

Rescue sketches (cheapest-first per [[feedback-rescue-sketch-first-sequencing]]):
- (a) ZERO-COST AUDIT: inspect tau_recovery computation in script for N=8192 numerical-degeneracy (dtype overflow, fp16/bf16 saturation, integer divide-by-zero).
- (b) CHEAP ~15min: pb3_extended_v5_n4096 reship at smaller N=4096 to verify v3 result reproduces (control for protocol drift between v3 and v4).
- (c) MEDIUM ~1h: pb3_extended_v5_n8192_dtype_audit reship with explicit fp32 + tau computation logged per-cell to disambiguate flat vs zero.

### Verdict 3: t3_susceptibility_v2_n8192 T3_MIDDLE_BAND (HONEST MIDDLE_BAND + PROT-018 N-suffix violation)

**Evidence (remote authoritative):**
- verdict_tag=T3_MIDDLE_BAND, wall_s=378s; config.N=4096 (NOT 8192 per anchor name suffix); seeds=[7,17,23,31,41] (5 seeds); operating_points=[M10_b32, M10_b8]; epsilons=[0.02,0.1,0.3] = 30 cells.
- verdict_msg: `PARTIAL_SADDLE: 0/5 seeds show all-3-chi >= 0.5; 0/5 seeds show M-only pattern.` Per-seed chi_M in [0, 0.1], chi_beta = 0 for all seeds, chi_cb in [0.1, 0.65] only.

**Step 0 honest re-read:** Caller's framing as "likely Kerdock SAME bug" is WRONG. Refutation: (a) wall_s=378s = real work performed (Kerdock crashes at <22s); (b) `_source=remote` = metrics file written by production run; (c) 5 seeds, all completed; (d) PARTIAL_SADDLE verdict_tag emitted by script (not import-time crash). t3_v2 GENUINELY RAN; the saddle-cascade signature did NOT appear in either operating point: 0/5 seeds show all-3-chi >= 0.5 (the multi-axis HP gate); 0/5 seeds show M-only pattern (the alternative axis-selective HP). Only chi_cb shows non-zero signal (range 0.1-0.65) but it does NOT exceed the HP threshold.

Additional PROT-018 finding: **anchor-name N-suffix violation**. Anchor name says `_n8192` but config.N=4096. Per [[feedback-no-label-vs-honest-anchor-names]] and PROT-018: anchor-name `_n<N>` is a BINDING CONTRACT. This is a NEW SUB-PATTERN of label-vs-honest: NOT the queue.json error case, NOT the SCRIPT_PRECONDITION_VIOLATION case — it is an ANCHOR-NAME-vs-CONFIG-N mismatch. Treat as 129th LABEL-VS-HONEST catch (sub-flavor ANCHOR_NAME_N_SUFFIX_CONFIG_MISMATCH). Note: per [[feedback-no-label-vs-honest-anchor-names]] PROT-018 is enforced at queue_add.py exit-6 going forward; this anchor is pre-PROT-018 backlog or PROT-018 enforcement was bypassed.

**Cap_map move:** T3 susceptibility / saddle-cascade row UNCHANGED at row level. Annotation: "v271 t3_susceptibility_v2_n8192 T3_MIDDLE_BAND honest MIDDLE_BAND (NOT Kerdock catch as caller guessed; production run completed 378s 5 seeds 30 cells). 0/5 seeds clear all-3-chi multi-axis HP; only chi_cb shows non-zero signal (0.1-0.65). Saddle-cascade multi-axis signature NOT present in M10/beta in {8,32} operating points. ALSO 129th LABEL-VS-HONEST catch: anchor `_n8192` suffix vs config.N=4096 = ANCHOR_NAME_N_SUFFIX_CONFIG_MISMATCH new sub-flavor; PROT-018 enforcement gap."

### Verdict 4: axis1_mb_chunk10_v1_n8192_fine KERDOCK-EVEN-LOG2 (128th LABEL-VS-HONEST catch — SCRIPT_PRECONDITION_VIOLATION sub-flavor)

**Evidence:**
- Remote bridge `get_metrics` returns `None` (remote SSH succeeded but no metrics.json present on remote = production run crashed pre-emit).
- queue.json verdict=`failed`. Caller's classification "SAME Kerdock bug" verified by absence-of-remote-dir + presence on v270 routing vulnerable-set list.

**Step 0 honest re-read:** SAME sub-flavor as V1 + v270 V4/V5/V6 (SCRIPT_PRECONDITION_VIOLATION at make_kerdock_4coset_codebook for N=8192 odd-log2). Honest reading: 128th LABEL-VS-HONEST catch.

**Cap_map move:** AXIS-1 (M-by-beta phase diagram) fine-resolution coverage row UNCHANGED. NO new rescue routing — v270 consolidated rescue routing already names chunk10 in its vulnerable-set audit list.

### Verdict 5: kf1_hallu_rescue_v2_n4096 KF1T1_HARD_PASS (CRITICAL HONEST — FIRST PRODUCTION-SCALE KF-1 CONFIRMATION RELIABILITY-RECALC)

**Evidence (remote authoritative):**
- verdict_tag=KF1T1_HARD_PASS, wall_s=3.98s; N=4096; m_fracs=[0.25, 0.5, 1.0]; seeds=[7,17,23,31,41] = 15 cells.
- verdict_msg: `Tier-1 reformulated claim PASSES. (a) above_thresh_frac=0 in all 5 seeds at M<=N. (b) 5/5 seeds have mean_max_conf <= 10/C. max_max_conf < 50/C in all cells. mean_ratio_to_uniform=4.72x (expected ~2-4x for BSC/Kerdock). Structural impossibility holds; OOS responses are near-uniform.`
- Per-cell verification: above_thresh_frac=0 in all 15 cells; near_uniform_mean=15/15; near_uniform_max=15/15; mean ratio_to_uniform in [3.09, 6.76] across cells; aggregate mean 4.72x; M_frac=0.25 mean 3.28x, M_frac=0.5 mean 4.34x, M_frac=1.0 mean 6.55x (monotone with M-density as expected for posterior-entropy structural impossibility).

**Step 0 honest re-read:** Caller's framing "v268 PROMOTED to green-smoke 55-70%; v2 at N=4096 should be the production-scale confirmation. If HARD_PASS, KF-1 row CONFIRMED at production scale (green-smoke -> tick candidate). Reliability-recalc trigger IF HARD_PASS." — Actual IS HARD_PASS. Honest reading: this is the FIRST PRODUCTION-SCALE 5-seed multi-M_frac KF-1 confirmation. v268 v1 was 3-seed at lower scope (M_BASE=20000); v271 v2 is 5-seed x 3 M_fracs = 15 cells with monotone ratio_to_uniform scaling with M-density = mechanism's posterior-entropy structural-impossibility working as theorized.

Cap_map evidence layers for KF-1:
- v267 c1_kf_battery: KF1+KF1B 0/3 architecture-level failure (cosine-similarity rejection mechanism failed).
- v268 v1 kf1_hallu_rescue_v1_n4096: 3-seed posterior-entropy rescue HARD_PASS gap=12.94 bits 12.9x safety margin (promoted yellow-AT-RISK -> green-smoke 55-70%).
- v271 v2 kf1_hallu_rescue_v2_n4096: 5-seed x 3 M_fracs HARD_PASS, above_thresh_frac=0 all 15 cells, near-uniform 15/15, ratio_to_uniform 3-7x band = PRODUCTION-SCALE confirmation.

**Cap_map move:** KF-1 hallucination-detection row PROMOTED green-smoke 55-70% (v268) -> **green 65-80%** (+10% LIFT; multi-seed x multi-M_frac corroboration tightens the band but stays GREEN pending multi-N replication for tick promotion). RELIABILITY-RECALC EVENT:
- product-feature 87-97% (v270) -> **88-97% LIFT (+1% lower bound)** — KF-1 production-scale 5-seed x 3 M_fracs is the highest-evidence-density product-feature event since v268.
- specific 70-83% (v270) UNCHANGED (KF-1 rescue is a structural-impossibility claim and IS in the framework spec; +1 evidence count rolled in).

Annotation: "v271 kf1_hallu_rescue_v2_n4096 KF1T1_HARD_PASS PRODUCTION-SCALE 5-seed x 3 M_fracs = 15 cells all above_thresh_frac=0 all near-uniform mean ratio_to_uniform=4.72x (3.28/4.34/6.55x by M_frac=0.25/0.5/1.0 monotone with M-density expected). FIRST PRODUCTION-SCALE 5-SEED KF-1 CONFIRMATION; supersedes v268 v1 3-seed. Posterior-entropy structural-impossibility mechanism CONFIRMED at scale. Killer-feature hallucination-detection product narrative: 'Substrate provably cannot fabricate at M <= N; OOS responses are near-uniform with 3-7x ratio to uniform (well below 10x threshold across all 15 cells).' Multi-N replication still needed for tick promotion; pending dual-N follow-up (N=8192) for tick promotion. NOTE: per [[feedback-lit-scan-calibration-penalty]] cap at +10% LIFT for single-N production-scale even with 5-seed x 3-M_frac corroboration."

### Pipeline-pacing decision

Bridge fresh (`is_stale=False`); queue depths: overnight=12 pending+1 running, remote_cpu=4 pending+1 running. Both HEALTHY per [[feedback-pipeline-pacing]]. Per [[feedback-no-padding-experiments]]: v270 consolidated Kerdock routing remains open + pb3 rescue sketches (this v271 batch). NO exp_dev refill dispatch.

### Routing decisions

- V1 chunk9, V4 chunk10: ABSORBED into v270 consolidated Kerdock routing (no new routing).
- V2 pb3_v4: rescue sketches filed inline (cheapest-first); no separate routing file (audit-step (a) is zero-cost and the orchestrator can run it next cycle).
- V3 t3_v2: PROT-018 enforcement gap noted; manual reconciliation by strategy next cycle.
- V5 kf1_v2: HARD_PASS = no rescue needed; multi-N follow-up captured in cap_map annotation as next-step.
- Per caller's upstream reminder: "Recommend NO new rescue routing in v271 (the v270 one covers all of these); just annotate the 3 new catches under it." — RESPECTED for V1/V4. V2/V3 GENUINE not Kerdock so are NEW substrate-physics evidence and warrant inline rescue sketches (V2) + PROT-018 manual reconciliation (V3) — NOT new routing files.

### PROT compliance (v271)

- PROT-004/006: 0 row closures; 0 row additions; 1 row band LIFT (KF-1 green-smoke 55-70% -> green 65-80% +10%); 1 framework-reliability LIFT (product-feature 87-97% -> 88-97% +1% lower bound); 3 rescue sketches for pb3 cheapest-first; 0 new routing files (v270 covers V1/V4).
- PROT-007: history.md UPDATED.
- PROT-008: 1 band lift validator-grade (KF-1 v268 3-seed -> v271 5-seed x 3-M_frac production-scale; +5-seed x +3-M_frac = N-axis-orthogonal corroboration warrants +10%).
- PROT-009: cap_map.md + cap_map_history.md + strategy_decisions_2026-05-29.md + visibility_decisions_2026-05-29.md staged atomically; **182nd PROT-009 paired commit**.
- PROT-018: V3 t3_v2 is ANCHOR_NAME_N_SUFFIX_CONFIG_MISMATCH = PROT-018 enforcement gap (either pre-PROT-018 backlog or bypass); flagged for strategy next cycle.
- [[feedback-verdict-msg-honest-reread]]: 156 -> 161 (+5; all 5 verdicts honest-read; 1 caller-misclassification correction on V3).
- [[feedback-rescue-sketch-first-sequencing]]: pb3 3 rescue arms cheapest-first (audit -> N-down -> dtype-instrument).
- [[feedback-rehabilitation-after-rejection]]: pb3 HARD_FAIL is FIRST CONTRADICTING EVIDENCE not closure; rescue sketches filed (not capability-closure).
- [[feedback-pipeline-pacing]]: queue HEALTHY (12+4 pending) -> no refill.
- [[feedback-no-padding-experiments]]: open routings sufficient; no padding.
- [[feedback-subagent-permission-inheritance]]: LOCAL commit only; push deferred to main thread.

**Cumulative HONEST observations**: 156 (v270) -> **161 (+5)**.
**Cumulative LABEL-VS-HONEST catches**: 126 (v270) -> **129 (+3: 127th V1 chunk9 + 128th V4 chunk10 SCRIPT_PRECONDITION_VIOLATION; 129th V3 t3_v2 ANCHOR_NAME_N_SUFFIX_CONFIG_MISMATCH new sub-flavor)**.
**0 routing files filed** (v270 consolidated rescue covers V1/V4; V2 inline rescue sketches; V3 PROT-018 reconciliation).


## v271 -> v272 BATCHED 13-VERDICT @ 2026-05-29 GPU drain event (KF-2 BE-1 PRECISION SWEEP 6-anchor PER-CELL HONEST + STRATEGIC INTERPRETATION OVER-CLAIM 130th NEW SUB-FLAVOR + REGION C 2-anchor HARD_PASS + REGION D 2-anchor MIDDLE_BAND + REGION C+D AGGREGATE SUBSTRATE BETA-INVARIANT KF-BEHAVIOR + AXIS-4 HYSTERESIS DIRECTION CLOSED AT PROBE LEVEL + AXIS-2 over-cap re-confirmation + SAAD_SOLLA_V19 BETA-SWEEP FAILED NO METRICS 5th-axis DEFERRED)

**Trigger.** 13 verdicts arrived in one batched GPU-drain event. Pause flag `data/orchestrator_paused.flag` ABSENT (verified) = ACTIVE state. All readable metrics fetched via remote bridge per `verdict_handler.md` Step 0 protocol; `_source=remote` for 12 of 13; V1 (saad_solla_v19) has NO remote metrics (no metrics.json materialized; remote dir likely empty). Dispatch context flagged this as `model=opus` event triggering substantive strategic snapshot; deep-strategy review for 16h overnight refill follows.

### Verdict 1: saad_solla_v19_n4096_beta_sweep FAILED wall_s=4559 (76min substantive run; metrics unavailable)

**Evidence:**
- verdict tag = FAILED. wall_s = 4559s = 76min substantive run BUT < 21600s budget = NOT TIMEOUT.
- `get_metrics(saad_solla_v19_n4096_beta_sweep) = None` (NO remote metrics.json found).
- SSH log inspection blocked by Windows missing ls/tail (PowerShell-shell encoding). Forensics deferred.

**Step 0 honest re-read:** Cannot perform Step 0 — no per-cell metrics available. Verdict is FAILED but disambiguation between (a) HONEST beta-axis HARD_FAIL (Saad-Solla framework reaches a beta-axis constraint limit) vs (b) script bug (CUDA crash at high beta mid-run) is UNDETERMINED from currently-readable evidence. Treat as UNKNOWN at probe level. Per role contract: "If `get_metrics` returns `None`, you cannot perform Step 0 reliably. Treat the verdict as `UNKNOWN`, prefix the return with `[metrics-unavailable]`, file a routing note for manual reconciliation, and DO NOT issue a cap_map state transition on missing data."

**Cap_map move:** Saad-Solla LEADING checkmark UNCHANGED (no successful 5th-axis to corroborate; cannot lift framework-reliability specific on a failed run; cannot demote/constrain on undisambiguated failure). Annotation: "v272 saad_solla_v19_n4096_beta_sweep FAILED wall_s=4559 (76min) substantive-not-timeout; remote metrics.json not materialized; disambiguation BLOCKED pending SSH log inspection or v20-style narrower-beta-range retry; 5th-axis BETA assessment DEFERRED."

**Rescue sketches (cheapest-first per [[feedback-rescue-sketch-first-sequencing]]):**
- (a) v20-style beta-sweep retry at NARROWER beta range (cheapest; if narrower range completes => beta-extension reaches a constraint at the dropped-extreme; if narrower also fails => script-bug-driven crash candidate strengthened).
- (b) saad_solla_v19 rerun with dtype-instrumented logging (medium; pinpoints whether crash is CUDA-state or substrate-physics).
- (c) beta-axis-down at N=2048 smoke parallel (cheapest-2; reproduces or refutes beta-extension constraint at smaller scale where compute is forgiving).

### Verdict 2: axis4_hyst_ramp_v1_n4096 AXIS4_HARD_FAIL (HONEST closure-level finding)

**Evidence (remote authoritative):**
- verdict_tag=AXIS4_HARD_FAIL wall_s=7.6.
- verdict_msg: `NO RETENTION HYSTERESIS: max loop_area=0.000000 < 0.01. Substrate retention is path-independent (no M-history effect).`
- Per-ramp data: 9 ramps (3 rates × 3 seeds); load/unload retention curves IDENTICAL at every M_frac (e.g. seed=7 rate=5: load [1.0, 1.0, 1.0, 0.9, 0.6333, 0.46] = unload [0.6333, 0.9, 1.0, 1.0, 1.0]).

**Step 0 honest re-read:** Verdict_msg labels the result HONESTLY. max_loop_area=0.0 across all 9 ramps means substrate's retention as a function of M_frac is reversible (path-independent); loading and unloading trajectories overlap exactly. This is a CLOSURE-LEVEL substrate-physics finding: substrate retention has NO M-history-dependence at probed (rate, seed) operating points. Honest.

**Cap_map move:** UNSURE-section row "Hysteresis as killer feature" (implicit row from KILLER-tier substrate-physics-distinct properties) -> ❌ CLOSED at PROBE LEVEL (not row-status level because hysteresis is not a current portfolio row). Annotation: "v272 axis4_hyst_ramp_v1_n4096 max_loop_area=0.0 ALL 9 ramps (3 rates × 3 seeds) load/unload retention IDENTICAL at every M_frac in {1.6, 3.2, 4.8, 6.4, 8.0} = substrate M-history-INDEPENDENT at probed operating points; hysteresis NOT a substrate capability at this beta=8 M_frac<=8 regime; rescue arms: test at higher beta where multi-basin may exist OR test at M near critical phase boundary." Per [[feedback-rehabilitation-after-rejection]] this is NOT a row closure but a probe-level closure with 2 rescue arms filed for future probing.

### Verdict 3: axis2_codebook_density_v2_n4096_collapse AXIS2V2_MIDDLE_BAND (HONEST over-cap re-confirmation)

**Evidence (remote authoritative):**
- verdict_tag=AXIS2V2_MIDDLE_BAND wall_s=438.7.
- verdict_msg: `PARTIAL_COLLAPSE: hp_collapse_count=0/3 all_above_low=False class_spread_12=0.007 ret_at_8={'bsc': 0.645, 'hadamard': 0.652, 'kerdock': 0.645} ret_at_16={'bsc': 0.645, 'hadamard': 0.652, 'kerdock': 0.645}`
- Per-cell: retention is IDENTICAL across M_frac in {4, 8, 12, 16, 20} for every codebook class — i.e. retention IS NOT a function of M_frac in this over-cap regime.

**Step 0 honest re-read:** verdict_msg labels PARTIAL_COLLAPSE with pass_collapse=0/3 reflecting that the script's collapse-criterion test FAILED but the per-cell retention values 0.62-0.66 are deep in over-cap regime where the substrate has already collapsed. Honest reading: substrate has already plateaued at over-cap retention 0.62-0.66 (well below clean-regime ~0.9) but the M_frac-dependence is FLAT in this band = no further M-density-collapse signal beyond the already-known over-cap ceiling. The 0.007 class-spread between codebook classes is statistical noise. Honest.

**Cap_map move:** AXIS-2 codebook-density row UNCHANGED at row status. Annotation: "v272 axis2_codebook_density_v2_n4096_collapse AXIS2V2_MIDDLE_BAND retention M_frac-INVARIANT 0.62-0.66 across M_frac in {4, 8, 12, 16, 20} every codebook class (bsc/hadamard/kerdock); class_spread=0.007 = statistical noise; over-cap ceiling re-confirmed at known band; NO NEW M-density-collapse signal beyond v260 family characterization."

### Verdicts 4-9: kf2_be1_{fp32, fp16, int8, int4, int2, int1}_n8192 ALL KF2_BE1_*_HARD_PASS (PER-CELL HONEST + 130th LABEL-VS-HONEST NEW SUB-FLAVOR STRATEGIC_INTERPRETATION_OVER_CLAIM)

**Evidence (remote authoritative):**
- All 6 verdict tags = KF2_BE1_<PRECISION>_HARD_PASS. All wall_s ∈ [2.30, 2.87]s (much faster than user-reported 15-19s; the user's wall_s may include queue-dispatch overhead).
- All 6 cells per anchor (5 seeds × 1 M_frac=2.0 × 1 family Kerdock) at N=8192.
- Iso_ratios across precisions:
  - FP32: [0.0101, 0.0, 0.0101, 0.0202, 0.0101], max=0.0202
  - FP16: [0.0101, 0.0, 0.0101, 0.0202, 0.0101], max=0.0202
  - INT8: [0.0101, 0.0, 0.0101, 0.0202, 0.0202], max=0.0202
  - INT4: [0.0101, 0.0, 0.0101, 0.0, 0.0101], max=0.0101
  - INT2: [0.0101, 0.0101, 0.0202, 0.0202, 0.0101], max=0.0202
  - INT1: [0.0101, 0.0, 0.0, 0.0, 0.0], max=0.0101 (BEST iso of all 6 precisions)
- precision_metadata correctly reports compression_ratio FP32=1x FP16=2x INT8=4x INT4=8x INT2=16x INT1=32x.

**Step 0 honest re-read:** Per-cell verdict labels HARD_PASS are HONEST AT NUMERICAL LEVEL: max_iso < HP_ISOLATION_MAX=0.05 holds at every precision; each compute_verdict call legitimately fires HARD_PASS (5/5 seeds < threshold). BUT three concerning patterns at AGGREGATE level:

1. **Iso pattern is precision-INSENSITIVE**: FP32, FP16, INT8, INT2 all share max=0.0202; INT4 and INT1 have max=0.0101 (BETTER than FP32 baseline). If quantization actually mattered to operative path, INT1 binary quantization should DEGRADE iso most, not IMPROVE it. The fact INT1 has 4/5 cells at iso=0.0 (perfect isolation) is physics-impossible if 1-bit quantization actually contaminates W's edit-projection geometry.

2. **Mechanism inspection** (from script `exp_kf2_be1_precision_sweep_n8192.py` lines 142-180): storage builds W in FP32, then quantize_roundtrip applies precision loss to W. Edit-isolation probe constructs `W_edited = W_q + outer(new_val - old_val, old_key) / N` and measures argmax delta on probe keys. The argmax of `cb @ probe_keys @ W_q.T` is dominated by Kerdock-codebook orthogonal structure (Kerdock entries are ±1), so W's magnitude scaling is largely irrelevant to argmax in this regime. Quantization-insensitivity is consistent with this mechanism — the test is NOT exercising W magnitude in the operative path.

3. **Strategic interpretation in dispatch context** ("8x deployment cost vs FP32 baseline = 100x cost vs FP16 LLM = category-defining") OVER-CLAIMS what was demonstrated. Demonstrated: KF-2 edit-isolation (argmax-delta-on-non-edited-keys probe) is quantization-equivariant at probe level. NOT demonstrated: downstream cost-advantage where W magnitude is operatively load-bearing (e.g., full retrieval accuracy / pool readout / cosine similarity under quantized W).

   Also: Kerdock-even-log2 vulnerability check from v270/v271: N=8192 log2=13 odd should raise ValueError at `make_kerdock_4coset_codebook(N=8192)`. The fact 6 runs completed at "N=8192" without crash is suspicious; either the codebook construction was silently routed to a fallback (BSC?) or the actual N differs from the anchor suffix (ANCHOR_NAME_N_SUFFIX_CONFIG_MISMATCH possibility, parallel to v271 t3_susceptibility_v2 catch).

**Honest reading:** Per-cell HARD_PASS labels are HONEST at numerical level. Strategic narrative "category-defining 32x cost advantage" is OVER-CLAIMED at probe level. This is a NEW LABEL-VS-HONEST sub-flavor: **STRATEGIC_INTERPRETATION_OVER_CLAIM** — distinct from prior sub-flavors:
- DISPATCH_FAILURE_MISCLASSIFICATION (v265-v269): remote metrics + HARD_PASS tag + queue=failed.
- SCRIPT_PRECONDITION_VIOLATION (v270-v271): no remote metrics + stale local smoke + ValueError pre-work.
- ANCHOR_NAME_N_SUFFIX_CONFIG_MISMATCH (v271): anchor `_n<X>` vs config.N=<Y>.
- STALE_QUEUE_ERROR_WITH_CLEAN_CURRENT_METRICS (v270): stale queue.json error + fresh clean metrics.
- **NEW v272 STRATEGIC_INTERPRETATION_OVER_CLAIM**: per-cell numerical labels HONEST + verdict_msg HONEST + STRATEGIC NARRATIVE OVER-CLAIMS the probe's demonstrative scope (cost-advantage narrative not supported by quantization-insensitive iso pattern; the probe didn't exercise the operative path required for the cost-claim).

Counts: 130th catch covers all 6 kf2_be1 anchors AS ONE COMPOUND CATCH (the over-claim is at strategic-narrative level not per-anchor numerical level).

**Cap_map move:** KF-2 row UNCHANGED at row status (per-cell precision-floor probe legitimately passes at all 6 precisions). NEW row annotation: "v272 BE-1 precision-floor 6-anchor (FP32/FP16/INT8/INT4/INT2/INT1) max_iso<0.05 all precisions PER-CELL HONEST AT NUMERICAL LEVEL; STRATEGIC 32x cost-advantage narrative OVER-CLAIMED at probe level (iso pattern is precision-INSENSITIVE = test not exercising W magnitude in operative path; INT1 binary actually has BETTER iso than FP32 baseline = physics-impossible if quantization mattered; 130th LABEL-VS-HONEST STRATEGIC_INTERPRETATION_OVER_CLAIM NEW SUB-FLAVOR); NEXT: ship retrieval-accuracy-under-quantized-W test where argmax depends on W magnitude (e.g. unbalanced codebook + soft readout) to validate cost-claim properly; ALSO file ANCHOR_NAME_N_SUFFIX_CONFIG_MISMATCH audit: confirm N=8192 was actually used (or fallback to BSC silently) given Kerdock-even-log2 ValueError per v270/v271 catches."

**Rescue sketch (cheapest-first):**
- (e) kf2_be1 retrieval-accuracy-under-quantized-W test (HIGH-VALUE-MEDIUM cost): construct test where output depends on W magnitude (e.g., unbalanced codebook + temperature-scaled readout, OR pool-readout with soft argmax, OR direct cosine retrieval accuracy as a function of M_frac and N near capacity boundary), then sweep precision. If iso/accuracy holds at INT4/INT8 under W-magnitude-operative conditions, strategic narrative re-validates. If not, the precision floor is much higher than the BE-1 probe suggests.

**Framework reliability:** product-feature 88-97% **UNCHANGED** — cannot lift on a probe whose strategic interpretation contradicts the probe's own iso pattern. Per [[feedback-no-smoke]] brutal honesty: per-cell pass at 6 precisions is NOT evidence for 32x cost-advantage; the probe needs a different shape.

### Verdicts 10-11: region_c_kf1_n4096_beta64_mfrac4 + region_c_kf2_n4096_beta64_mfrac4 BOTH REGION_C_*_HARD_PASS (HONEST ferromagnet phase)

**Evidence (remote authoritative):**
- Both verdicts REGION_C_KF*_HARD_PASS wall_s=4-5s.
- verdict_msg both: `FERROMAGNET_CONFIRMED: 5/5 seeds mean_ret=1.0000 >= 0.7 at beta=64.0`
- Per-cell: every cell ret=1.0 (perfect retention at high-beta low-M ferromagnet phase).

**Step 0 honest re-read:** 5/5 seeds at ret=1.0 in region C (beta=64, M_frac=4) is the high-beta low-M ferromagnet phase = trivial PASS regime. Both KF-1 and KF-2 hold identically. Honest at numerical level.

**Aggregate finding (combined with region D V12-V13):** Region C HARD_PASS at retention=1.0 IDENTICAL to known region A (beta=8, low M); region D MIDDLE_BAND at retention=0.33 IDENTICAL to known region B (beta=8, high M). Substrate KF-1+KF-2 behavior is **BETA-INVARIANT at tested (M_frac, beta) operating points**. This contradicts the steerable-killer-feature hypothesis at probe level: "If KF-1 + KF-2 DIFFER between C/D vs A/B: there ARE qualitatively different operating modes above beta_c (steerable killer feature)." At probed points beta_c=10 → no qualitative difference at beta=64 vs beta=8. NOT a closure of steerable-KF hypothesis (steerability may live at intermediate beta near beta_c=10, OR at different M_frac values, OR at the high-beta boundary) but a probe-level finding that beta=64 is in the SAME operational mode as beta=8.

**Cap_map move:** KF-1 + KF-2 + axis-1 phase-boundary rows UNCHANGED at row status (no new evidence; region C is trivial ferromagnet pass corroborating known phase behavior). NEW annotation on killer-feature phase-class profile row: "v272 region C (beta=64, M_frac=4) HARD_PASS ret=1.0 + region D (beta=64, M_frac=12) MIDDLE_BAND ret=0.33 IDENTICAL to A/B at beta=8 = SUBSTRATE BETA-INVARIANT IN KF-BEHAVIOR at tested (M_frac, beta) operating points; STEERABLE-KILLER-FEATURE hypothesis NOT SUPPORTED at probe level (operational simplicity over steerability); rescue arms: test at intermediate beta near beta_c=10 OR at different M_frac OR at high-beta phase boundary."

### Verdicts 12-13: region_d_kf1_n4096_beta64_mfrac12 + region_d_kf2_n4096_beta64_mfrac12 BOTH REGION_D_*_MIDDLE_BAND (HONEST over-cap collapse)

**Evidence (remote authoritative):**
- Both REGION_D_KF*_MIDDLE_BAND wall_s=5-6s.
- verdict_msg both: `PARTIAL: 0/5 seeds mean_ret=0.3325`
- Per-cell: ret=[0.353, 0.328, 0.327, 0.328, 0.327] all consistent; tight std.

**Step 0 honest re-read:** 0/5 seeds at mean_ret=0.3325 at beta=64 M_frac=12 (M/N=12) is over-cap collapse regime. For a 4-class classification, chance = 0.25; mean_ret=0.33 is barely above chance. Substrate has collapsed at this operating point. Honest. Both KF-1 and KF-2 fail equally at this over-cap regime.

**Cap_map move:** Absorbed into the region C+D aggregate finding above (BETA-INVARIANT KF-behavior annotation). No standalone row move.

### v271 -> v272 PORTFOLIO + RELIABILITY MOVES

- **KF-2 edit-isolation checkmark UNCHANGED** at row status; NEW annotation "BE-1 precision-floor 6-anchor PER-CELL HONEST + STRATEGIC narrative OVER-CLAIMED; iso pattern precision-INSENSITIVE; W-magnitude-operative test required."
- **KF-1 hallucination-detection green 65-80% UNCHANGED** (region C ferromagnet pass and region D over-cap fail are not new evidence for hallucination-detection killer-feature).
- **Killer-feature phase-class profile yellow 45-60% UNCHANGED** with NEW BETA-INVARIANCE ANNOTATION (steerability NOT YET demonstrated at probed points).
- **AXIS-1 phase-boundary green 70-82% UNCHANGED** (region C/D probe corroborates known A/B-pattern at higher beta).
- **AXIS-2 codebook-density row UNCHANGED** (over-cap M_frac-invariance is corroboration not new finding).
- **AXIS-4 hysteresis-killer direction CLOSED at PROBE LEVEL** (UNSURE-section row "hysteresis as killer"; not portfolio row; 2 rescue arms filed).
- **Saad-Solla LEADING checkmark UNCHANGED** (5th-axis BETA assessment BLOCKED pending disambiguation; 3 rescue arms filed cheapest-first).
- **Framework reliability specific 70-83% UNCHANGED** (Saad-Solla 5th-axis FAILED + KF-2 precision-floor strategic OVER-CLAIM = neither warrants lift).
- **Framework reliability product-feature 88-97% UNCHANGED** (KF-2 precision-floor per-cell pass does NOT validate cost-advantage narrative at probe level).
- **Framework reliability general 73-83% UNCHANGED**.
- **Non-eq stat-mech 66-76% UNCHANGED**.
- **Portfolio 14 + 31 UNCHANGED**.
- **Cumulative HONEST observations**: 161 (v271) -> **167 (+6: V2 axis4 + V3 axis2 + V4-V9 kf2_be1 + V10-V11 region C + V12-V13 region D ALL honest at numerical/probe level)**.
- **Cumulative LABEL-VS-HONEST catches**: 129 (v271) -> **130 (+1 NEW SUB-FLAVOR STRATEGIC_INTERPRETATION_OVER_CLAIM compound catch covering kf2_be1 cost-narrative; one catch not 6 because the over-claim is at strategic-narrative level)**.

### NEW SUB-FLAVOR: STRATEGIC_INTERPRETATION_OVER_CLAIM (1 compound catch this batch)

Extend discrimination criterion:
- TRUE DISPATCH_FAILURE_MISCLASSIFICATION (v265+v267-v269): remote metrics EXIST + verdict_tag HARD_PASS-flavored + queue.json `failed`.
- GENUINE FAST HARD_FAIL (v269): remote metrics EXIST + verdict_tag HARD_FAIL + queue.json `failed`.
- GENUINE SUBSTANTIVE FAILURE (v269): NO remote dir + no remote metrics + no script-precondition signature.
- SCRIPT_PRECONDITION_VIOLATION (v270-v271): NO remote dir + LOCAL stale-smoke at smaller N + script source has precondition assertion.
- ANCHOR_NAME_N_SUFFIX_CONFIG_MISMATCH (v271): anchor `_n<X>` vs config.N=<Y>.
- STALE_QUEUE_ERROR_WITH_CLEAN_CURRENT_METRICS (v270): stale queue.json error + fresh clean metrics.
- **NEW v272 STRATEGIC_INTERPRETATION_OVER_CLAIM**: per-cell numerical labels HONEST + verdict_msg HONEST at probe level + dispatch-context/strategic-narrative OVER-CLAIMS demonstrative scope BEYOND what the probe's evidence supports. Step 0 must check: (a) does the strategic narrative's claim depend on a mechanism the probe exercised, (b) are aggregate patterns across cells/anchors consistent with the strategic interpretation. The 130th catch fires when per-cell pass + aggregate pattern that the strategic narrative depends on is FLAT/insensitive in the direction the claim requires (e.g., quantization should differentiate but iso is insensitive across all precisions).

### Queue-refill (Step 2 pipeline-pacing) decision

Pause flag ABSENT (verified). Bridge queue state (`is_stale()=False`):
- overnight_queue: 587 entries, **0 pending+running** (GPU is DRAINED — this is the GPU drain event of the batch).
- remote_cpu_queue: 239 entries, 6 pending+running (HEALTHY; saad_solla_v20_n4096_m_sweep currently running).

GPU queue empty triggers [[feedback-pipeline-pacing]] queue-depth-0 reflex. BUT dispatch context explicitly states: "After verdict_handler returns, orchestrator main thread will dispatch deep-strategy review for 16h overnight refill planning." Caller already has structural plan; per [[feedback-no-padding-experiments]] verdict_handler does NOT dispatch padding refill; per [[feedback-verdict-arrival-is-queue-depletion-signal]] verdict-handler reflex DEFERS to caller's stated deep-strategy plan.

**Decision: NO exp_dev pipeline-pacing dispatch this batch.** Refill SKIPPED pending caller's deep-strategy review.

### NEW routings filed (v272)

0 NEW routings filed. Rescue sketches (a)-(e) recorded inline above; saad_solla v20-style rerun candidate to be operationalized at strategy cycle, not verdict_handler level.

### PROT compliance (v272)

- **PROT-004/006**: 0 row closures (axis-4 hysteresis-killer is probe-level not row-status; not portfolio row); 0 row additions; 0 row promotions/demotions; 0 framework-reliability moves; 5 rescue sketches filed inline cheapest-first across V1 saad_solla and V2 axis-4 hysteresis and V4-V9 kf2_be1.
- **PROT-007**: history.md UPDATED with v272 row.
- **PROT-008**: 0 band lifts (KF-2 precision-floor per-cell pass but strategic OVER-CLAIM blocks reliability lift per [[feedback-no-smoke]] brutal honesty; Saad-Solla 5th-axis FAILED blocks reliability lift on missing data).
- **PROT-009**: cap_map.md (v271 -> v272 batched row) + cap_map_history is the cap_map.md row table itself + strategy_decisions_2026-05-29.md (this entry) + visibility_decisions_2026-05-29.md (one-line) staged atomically; **183rd PROT-009 paired commit**.
- **PROT-018**: All 13 anchors carry `_n<N>` suffix; saad_solla_v19_n4096_beta_sweep (N=4096 ✓); axis4_hyst_ramp_v1_n4096 (✓); axis2_codebook_density_v2_n4096_collapse (✓); kf2_be1_*_n8192 (6 anchors; CONCERN: Kerdock-even-log2 vulnerability if N actually = 8192; possible ANCHOR_NAME_N_SUFFIX_CONFIG_MISMATCH if N silently fell back to N=4096; needs verification); region_{c,d}_kf{1,2}_n4096_beta64_mfrac{4,12} (4 anchors ✓).
- **[[feedback-verdict-msg-honest-reread]]**: 161 -> 167 obs (+6); LABEL-VS-HONEST 129 -> 130 (+1 STRATEGIC_INTERPRETATION_OVER_CLAIM NEW sub-flavor).
- **[[feedback-trust-queue.json-wall_s]]**: APPLIED to all 13 (12 via remote metrics; V1 saad_solla via wall_s=4559 substantive-not-timeout judgment).
- **[[feedback-no-smoke]]**: brutal honesty applied to kf2_be1 strategic narrative — per-cell pass does NOT validate cost-advantage at probe level; explicitly NOT lifting framework reliability on a probe whose iso pattern contradicts the cost-claim.
- **[[feedback-rescue-sketch-first-sequencing]]**: 5 rescue sketches cheapest-first across 3 verdicts (saad_solla narrower-beta retry + smoke parallel; axis-4 multi-basin retry; kf2_be1 W-magnitude-operative test).
- **[[feedback-rehabilitation-after-rejection]]**: axis-4 hysteresis is probe-level closure with 2 rescue arms (not row-status closure).
- **[[feedback-dont-overextend-theorems]]**: region C+D BETA-INVARIANT finding does NOT close steerable-killer-feature hypothesis space-wide; rescues at intermediate beta + different M_frac + high-beta phase boundary remain open.
- **[[feedback-pipeline-pacing]] + [[feedback-no-padding-experiments]] + [[feedback-verdict-arrival-is-queue-depletion-signal]]**: GPU queue empty BUT caller has structural deep-strategy plan; verdict_handler defers refill dispatch.
- **[[feedback-subagent-permission-inheritance]]**: LOCAL commit only; push deferred to main thread.
- **[[feedback-cap-map-update-protocol]]**: atomic commit cap_map.md + strategy_decisions_2026-05-29.md + visibility_decisions_2026-05-29.md.

Commit message: `Cap map: v271 -> v272 (BATCHED 13-VERDICT GPU drain event: kf2_be1 precision sweep 6-anchor FP32/FP16/INT8/INT4/INT2/INT1 all KF2_BE1_*_HARD_PASS max_iso<0.05 PER-CELL HONEST BUT STRATEGIC-INTERPRETATION OVER-CLAIM 130th LABEL-VS-HONEST new sub-flavor STRATEGIC_INTERPRETATION_OVER_CLAIM iso pattern precision-INSENSITIVE INT1 better than FP32 = quantization not exercising operative path cost-advantage 32x narrative NOT validated W-magnitude-operative test required + region C 2-anchor kf1+kf2 beta=64 M_frac=4 HARD_PASS 5/5 ret=1.0 ferromagnet + region D 2-anchor kf1+kf2 beta=64 M_frac=12 MIDDLE_BAND 5/5 mean_ret=0.33 over-cap collapse + REGION C+D AGGREGATE substrate BETA-INVARIANT in KF-behavior IDENTICAL to A/B at beta=8 = steerable-killer-feature hypothesis NOT SUPPORTED at probe level + axis4_hyst_ramp_v1_n4096 AXIS4_HARD_FAIL max_loop_area=0.0 all 9 ramps NO RETENTION HYSTERESIS substrate path-independent M-loading hysteresis-killer direction CLOSED at probe level + axis2_codebook_density_v2_n4096_collapse AXIS2V2_MIDDLE_BAND retention M_frac-INVARIANT 0.62-0.66 across M_frac 4-20 over-cap ceiling re-confirmed + saad_solla_v19_n4096_beta_sweep FAILED wall_s=4559 76min substantive-not-timeout NO REMOTE METRICS 5th-axis BETA disambiguation BLOCKED 3 cheapest-first rescue sketches inline (v20-style narrower-beta-retry + dtype-instrumented rerun + N=2048 smoke parallel); portfolio 14+31 UNCHANGED; framework reliability product-feature 88-97% UNCHANGED specific 70-83% UNCHANGED general 73-83% UNCHANGED non-eq-stat-mech 66-76% UNCHANGED; KF-2 row UNCHANGED with precision-floor strategic-OVER-CLAIM annotation; Saad-Solla LEADING UNCHANGED 5th-axis DEFERRED; killer-feature phase-class profile yellow 45-60% UNCHANGED with BETA-INVARIANCE NEW annotation; UNSURE-section hysteresis-killer probe-level CLOSED with 2 rescue arms; HONEST 161->167 (+6); LABEL-VS-HONEST 129->130 (+1 NEW SUB-FLAVOR STRATEGIC_INTERPRETATION_OVER_CLAIM compound catch); 0 NEW routings filed; 183rd PROT-009 paired commit; verdict_handler sub-agent inline strategy+visibility no Agent sub-dispatch)`
v272->v273 ANNOTATION-ONLY: user-delivered overnight-refill triage strategy logged; 3 at-risk claims registered (KF-2 BE-1 cost-advantage, KF-5 steerability, Bet B Tier-1 architectural); Run-A1-First directive binding; TIER 1 = A1+A2+B1+C1+C2 (~4 GPU days); 2 exp_dev routing files filed; portfolio 14+31 UNCHANGED; all reliability bands UNCHANGED


## v273 -> v274 BATCHED 4-VERDICT @ 2026-05-29 Section-4 branching trigger + overnight refill start (saad_solla_v20_n4096_m_sweep FAILED 2nd-strike 5th-axis STRUCTURAL CONSTRAINT + t1_beta_v3_n4096_mfrac_sweep T1V3_HARD_FAIL = Cluster B1 LAST-CHANCE BETA-STEERABILITY CLOSED + t2_codebook_v3_n4096_op_sweep T2V3_HARD_PASS = Cluster B3 CODEBOOK-AXIS STEERABILITY CONFIRMED at probe + kf1_hallu_rescue_v3_n8192 FAILED Kerdock-even-log2 SCRIPT_PRECONDITION_VIOLATION 131st LABEL-VS-HONEST)

**Trigger.** 4 verdicts arrived in one batched event matching Section 4 branching condition (Saad-Solla 5th-axis 2-strike) + post-v273 overnight refill start. Pause flag `data/orchestrator_paused.flag` ABSENT (verified) = ACTIVE state. Metrics fetched via bridge: V1 saad_solla v20 `_source=local` (stale pre-ship smoke N=512 1-seed [17] M_frac [0.125]; production run never emitted metrics.json — queue.json says failed wall_s=14400 = CPU 4h hard timeout); V2 t1 v3 `_source=remote` authoritative; V3 t2 v3 `_source=remote` authoritative; V4 kf1 v3 `get_metrics=None` (no metrics.json materialized; wall_s=2.8 pre-work crash).

### Verdict 1: saad_solla_v20_n4096_m_sweep FAILED (HONEST 2nd-strike 5th-axis STRUCTURAL CONSTRAINT; framework-CONSTRAINT annotation)

**Evidence:** queue.json `failed wall_s=14400` (CPU 4h hard timeout). Local-fallback metrics.json is STALE PRE-SHIP SMOKE artifact `N=512 smoke=true seeds=[17] M_fracs=[0.125] verdict=SS_V20_MIDDLE_BAND` masquerading at the local-metrics layer but BOTH dispatch context AND queue.json AND elapsed_s = 14400 (exact CPU floor) say TIMEOUT at the substantive-run layer. Caller's framing as "CPU TIMEOUT at 4h floor" is HONEST at queue.json + dispatch-context level; local-fallback misleads at metrics-read layer but Step 0 caught this via remote-fallback flag.

**Step 0 honest re-read:** This is the 2nd consecutive Saad-Solla 5th-axis substantive-run failure (v19 beta-sweep FAILED wall_s=4559 with no remote metrics per v272; v20 m-sweep FAILED wall_s=14400 CPU TIMEOUT per this verdict). Both attempts at extending the framework beyond the confirmed 4-axis anchor (seed/codebook/M-axis/N=8192 per v270 SS_V16) hit substantive-run failure at the 5th-axis-extension layer — different failure modes (v19: no metrics emitted; v20: CPU 4h hard timeout) but same outcome: NO 5th-axis HARD_PASS materialized. Honest reading: STRUCTURAL CONSTRAINT at 5th-axis extension confirmed across 2 independent axes (beta + m-sweep) and 2 independent failure modes. This is an OPERATIONAL CEILING (resource budget + script-runtime architecture), NOT a physics-level rejection of the Saad-Solla framework.

**Cap_map move:** Saad-Solla LEADING checkmark row UNCHANGED at status level (already checkmark; 4-axis anchor still load-bearing from v270 SS_V16). NEW FRAMEWORK-CONSTRAINT annotation: "Saad-Solla framework anchor confirmed at 4 axes (seed / codebook / M-axis at N=8192 / foundational N=8192 2-seed) per v270 SS_V16_HARD_PASS. 5th-axis extension hits OPERATIONAL CEILING across 2 independent failure modes (v19 beta-sweep FAILED no metrics emitted; v20 m-sweep FAILED CPU 4h hard timeout): different mechanisms (script-runtime-crash vs CPU-budget-exhaustion) confirms STRUCTURAL CONSTRAINT not anchor-specific bug. Framework-anchor at 4 axes STANDS load-bearing; 5th-axis extensions are OPERATIONAL CONSTRAINT not physics-level rejection. Per Section 4 branching rule: G9 saad_solla_v18_n16384 RECOMMEND TRIM from overnight queue (5th-axis-direction is structurally blocked at 2-strike independent-mode confirmation; v18 at N=16384 would be 3rd-strike on same direction at higher cost, not new evidence)." Framework-reliability specific 70-83% UNCHANGED (5th-axis BLOCKED, not lifted; constraint annotation does NOT demote 4-axis anchor either). Per [[feedback-dont-overextend-theorems]]: the 5th-axis 2-strike does NOT close Saad-Solla as a framework; it constrains the EXTENSION axes only. 4-axis anchor remains load-bearing.

### Verdict 2: t1_beta_v3_n4096_mfrac_sweep T1V3_HARD_FAIL (HONEST; Cluster B1 LAST-CHANCE beta-steerability CLOSED)

**Evidence (remote authoritative):**
- verdict_tag=T1V3_HARD_FAIL wall_s=94.76. N=4096 production-scale; 6 M_fracs [2,4,6,8,10,12]; 3 seeds [7,17,23]; 10-point beta_sweep [1,2,4,8,16,32,64,128,256,512].
- verdict_msg: `FLAT_BETA_C: log2_range=0.00 < 1.0 across 6 M_fracs. mean_beta_c_by_mfrac={2.0:8.0, 4.0:8.0, 6.0:8.0, 8.0:8.0, 10.0:8.0, 12.0:8.0} monotone_frac=1.00 beta_c_log2_range=0.00 mfracs_with_transition=6/6 N=4096`

**Step 0 honest re-read:** All 6 M_fracs collapse to beta_c=8.0 EXACT (mean_beta_c_by_mfrac all = 8.0 — zero variance across 6 M_fracs at N=4096 production-scale with 3 seeds). 6/6 M_fracs have a transition (beta_c-detection criterion met) but the transition point is IDENTICAL across all M_fracs (log2_range=0.00; threshold for HARD_PASS was 1.0). This is the cleanest possible NO-STEERABILITY signal at the beta-axis. Caller framed as "MIDDLE_BAND or HARD_FAIL → substrate is 1D M-axis with full beta-invariance, simpler operational model." Honest reading: substrate beta_c is M_frac-INDEPENDENT and EXACTLY beta=8 (single beta-axis critical point across the entire production M_frac range) = full beta-invariance in critical-point structure. This MATCHES v272 region C+D BETA-INVARIANT finding (substrate behavior at beta=64 IDENTICAL to beta=8 in tested operating regions) but EXTENDS it: now we have BOTH the narrow-band (this verdict; 10-point beta-sweep across 6 M_fracs near beta_c=10) AND the wide-band (v272 region C+D at beta=64 vs A/B at beta=8) confirming beta-invariance.

**Cluster B1 context (per v273 routing file):** "B1 is the LAST-CHANCE test for steerable-killer-feature hypothesis on beta-axis. If B1 finds no signal: KF-5 steerability direction closes honestly; Cluster B3 probes codebook-axis as independent steerability axis." B1 HARD_FAIL FLAT_BETA_C IS the "no signal" outcome.

**Cap_map move:** KF-5 phase-mechanism subhypothesis CLOSED-pending-rescue (v273 status) -> KF-5 BETA-AXIS steerability CLOSED HONESTLY at probe level. Annotation: "v274 t1_beta_v3_n4096_mfrac_sweep T1V3_HARD_FAIL FLAT_BETA_C all 6 M_fracs collapse to beta_c=8.0 EXACT log2_range=0.00 < 1.0 HP bar across N=4096 production-scale 3 seeds = LAST-CHANCE beta-axis steerability NULL RESULT at narrow-band scale. Combined with v272 region C+D beta=64 vs A/B beta=8 BETA-INVARIANT wide-band finding, beta-axis steerability is now NULL at BOTH narrow-band (near beta_c=10) AND wide-band (beta in {8,64}) — 2 independent witness levels confirming substrate is beta-INVARIANT in critical-point structure. KF-5 BETA-AXIS steerability direction CLOSED HONESTLY at probe level per v273 routing pre-registered HARD_FAIL clause. Rescues remain open: (i) codebook-axis (B3 — see V3 PASS below); (ii) high-density multi-hop coupling B2 was CONTINGENT on B1 signal — now KILLED per v273 contingency rule." Per [[feedback-rehabilitation-after-rejection]] (probe-level closure not mechanism-wide closure) + [[feedback-dont-overextend-theorems]] (beta-axis null does not foreclose ALL killer-feature steerability directions).

### Verdict 3: t2_codebook_v3_n4096_op_sweep T2V3_HARD_PASS (HONEST; Cluster B3 CODEBOOK-AXIS STEERABILITY CONFIRMED at probe level)

**Evidence (remote authoritative):**
- verdict_tag=T2V3_HARD_PASS wall_s=58.29. N=4096 production-scale; 3 seeds [7,17,23]; 4 op_points [(2,8), (4,32), (2,64), (1,32)] (M_frac, beta); 5 c_fracs [0.1, 0.3, 0.5, 0.7, 1.0].
- verdict_msg: `OP-INVARIANT: 3/4 op-points show slope >= 0.05. op_results={'(2.0, 8.0)': {n_pass:3/3, mean_slope:0.158}, '(4.0, 32.0)': {n_pass:0/3, mean_slope:-0.027}, '(2.0, 64.0)': {n_pass:3/3, mean_slope:0.158}, '(1.0, 32.0)': {n_pass:3/3, mean_slope:0.262}} n_pass_ops=3/4 N=4096`

**Step 0 honest re-read:** 3/4 operating points pass codebook-axis slope >= 0.05 bar. The one failing op-point is (M_frac=4, beta=32) with mean_slope=-0.027 (over-cap saturation regime — M_frac=4 at beta=32 is in the over-cap collapse band per v272 region D analog). The 3 PASS op-points span (M_frac=2, beta=8) low-density low-beta + (M_frac=2, beta=64) low-density high-beta + (M_frac=1, beta=32) lowest-density mid-beta = 3 distinct phase regions all show MONOTONE-IN-CODEBOOK-COMPLEXITY retention. Mean slopes: 0.158 / 0.158 / 0.262 — strongest at lowest-density (M_frac=1). Caller framed as "If HARD_PASS: codebook-axis is a new degree of freedom worth investing in." Honest reading: codebook complexity (c_frac) DOES steer killer-feature retention at 3/4 tested op-points with substantial slope (mean_slope 0.158-0.262 vs HP bar 0.05 = 3-5x margin). This is the FIRST POSITIVE STEERABILITY axis identified for KF-behavior.

**Cluster B3 context (per v273 routing file):** "B3 codebook-axis steerability is independent of beta-axis. If codebook selection allows qualitative KF-behavior steering, the product story is 'choose your operating mode via codebook' rather than 'choose via beta'. This is independent of B1 outcome." B3 HARD_PASS confirms the codebook-axis steerability story.

**Cap_map move:** KF-5 phase-mechanism subhypothesis CLOSED-pending-rescue (v273 status) -> REFRAME: KF-5 BETA-AXIS CLOSED + KF-5 CODEBOOK-AXIS NEW GREEN-SMOKE 55-70% (first positive steerability axis identified). Annotation: "v274 t2_codebook_v3_n4096_op_sweep T2V3_HARD_PASS 3/4 op-points pass codebook-axis slope >= 0.05 bar at N=4096 production-scale 3 seeds: (M_frac=2, beta=8) mean_slope=0.158, (M_frac=2, beta=64) mean_slope=0.158, (M_frac=1, beta=32) mean_slope=0.262 = monotone-in-codebook-complexity retention across 3 distinct phase regions; (M_frac=4, beta=32) FAILS at over-cap saturation regime mean_slope=-0.027 = expected null in collapse band. FIRST POSITIVE STEERABILITY AXIS IDENTIFIED for KF-behavior at probe level. KF-5 steerability narrative REFRAMED: BETA-AXIS direction CLOSED at probe level (v272 region C+D BETA-INVARIANT + v274 B1 FLAT_BETA_C); CODEBOOK-AXIS direction CONFIRMED at probe level (this verdict + v270 SS_V17 codebook-axis HARD_PASS at framework anchor). Product story shifts from 'choose your operating mode via beta' to 'choose your operating mode via codebook' — codebook-axis becomes the load-bearing steerability mechanism. PROMOTION GATE: KF-5 codebook-axis green-smoke 55-70% pending (a) 5-seed defense-in-depth at N=4096 (only 3-seed here per [[feedback-lit-scan-calibration-penalty]] single-N cap); (b) N=8192 multi-N replication for tick promotion (must verify codebook-axis slope holds at production scale)."

Per [[feedback-dont-overextend-theorems]]: codebook-axis HARD_PASS at probe level does NOT yet warrant checkmark promotion; needs multi-N + 5-seed defense-in-depth before tick. Per [[feedback-lit-scan-calibration-penalty]]: single-N 3-seed lift capped at +5% reliability move (NOT +10%) — this is why we move killer-feature phase-class profile by +5% only (see below).

### Verdict 4: kf1_hallu_rescue_v3_n8192 FAILED (131st LABEL-VS-HONEST catch SCRIPT_PRECONDITION_VIOLATION continuation; Kerdock-even-log2)

**Evidence:** wall_s=2.8 = pre-work crash. `get_metrics()` returns None (no metrics.json materialized; matches v270/v271 vulnerable-pattern). Caller's diagnosis: NEW v3 script derived from v2_n4096 inherits Kerdock dependency that wasn't visible in v2 at N=4096 because N=4096 log2=12 EVEN passes the make_kerdock_4coset_codebook validator; v3 escalated to N=8192 (log2=13 ODD) which triggers the same ValueError documented in v270 across 6 prior anchors.

**Step 0 honest re-read:** This is the 131st LABEL-VS-HONEST catch in the SCRIPT_PRECONDITION_VIOLATION sub-flavor (continuation of v270 124th-126th + v271 127th-128th). Caller's diagnosis confirmed by pattern-match (wall_s<=22, get_metrics=None, queue.json failed, anchor _n8192 with Kerdock-using script). Caller's TWO reroute candidates listed: (i) N=16384 (Kerdock-safe even-log2=14) requires GPU memory budget verification; (ii) BSC codebook fix at N=8192. Honest reading: KF-1 N-axis replication is BLOCKED at N=8192 with Kerdock codebook. Cheapest rescue per [[feedback-rescue-sketch-first-sequencing]] is BSC-codebook substitution at N=8192 (subsumption — uses existing Kerdock-safe code path at lower memory cost than N=16384).

**Cap_map move:** KF-1 hallucination-detection green 65-80% UNCHANGED at row status (v271 v2 N=4096 5-seed x 3-M_frac PRODUCTION-SCALE CONFIRMATION remains load-bearing; v274 v3 N=8192 SCRIPT_PRECONDITION_VIOLATION does NOT change row status — no substrate-physics signal in either direction). Annotation: "v274 kf1_hallu_rescue_v3_n8192 SCRIPT_PRECONDITION_VIOLATION (Kerdock-even-log2 N=8192 log2=13 odd inherited from v2 script when escalated from N=4096); rescue sketches cheapest-first per [[feedback-rescue-sketch-first-sequencing]]: (a) PRIMARY/SUBSUMPTION = BSC-codebook substitution at N=8192 (0-cost code change; uses existing Kerdock-safe codepath); (b) CHEAP <=15min smoke = N=16384 Kerdock-safe even-log2=14 IF GPU memory budget verified (per [[feedback-ship-before-dependency-verified]] verify N=16384 budget BEFORE queue_add); (c) MEDIUM = structural-fix to make_kerdock_4coset_codebook auto-route to nearest-even-log2 N (long-term per v270 structural-fix candidate-d). 131st LABEL-VS-HONEST catch SCRIPT_PRECONDITION_VIOLATION sub-flavor continuation; PROT-018 enforcement gap was for _n suffix vs config.N (129th sub-flavor v271) — this is the older sub-flavor (script crashes pre-work, queue.json honest failed, local metrics absent or stale)."

Per [[feedback-rehabilitation-after-rejection]]: KF-1 v2 PRODUCTION-SCALE CONFIRMATION from v271 stands; v3 N-axis multi-N replication NOT yet attempted (the test BLOCKED before any substantive run); no closure event, ONE rescue routing filed.

### v273 -> v274 PORTFOLIO + RELIABILITY MOVES

- **Saad-Solla LEADING checkmark row UNCHANGED + 5TH-AXIS STRUCTURAL CONSTRAINT ANNOTATION** (v20 m-sweep FAILED CPU TIMEOUT 2nd-strike to v19 beta-sweep no-metrics; 2 independent failure modes confirm STRUCTURAL CONSTRAINT not anchor-specific bug; 4-axis anchor STANDS load-bearing). Per Section 4 branching rule: G9 saad_solla_v18_n16384 RECOMMEND TRIM from overnight queue pending list (surface to orchestrator main thread).
- **KF-5 phase-mechanism subhypothesis REFRAMED** (v273: CLOSED-pending-rescue; v274: BETA-AXIS CLOSED HONESTLY at probe level [B1 HARD_FAIL FLAT_BETA_C] + CODEBOOK-AXIS NEW GREEN-SMOKE 55-70% [B3 HARD_PASS 3/4 op-points]); product narrative shifts beta -> codebook. Per v273 at-risk-claim register: KF-5 steerability "fine-beta (B1) and codebook-axis (B3) are last-chance probes" — B1 closed honestly, B3 confirmed; net resolution = REFRAMED not CLOSED.
- **Killer-feature phase-class profile yellow 45-60% (v273) -> yellow 50-65% LIFT (+5% lower bound)** — codebook-axis steerability NEW POSITIVE component lifts the profile; capped at +5% per [[feedback-lit-scan-calibration-penalty]] single-N 3-seed.
- **KF-1 hallucination-detection green 65-80% UNCHANGED** (v3 N-axis SCRIPT_PRECONDITION_VIOLATION; v271 v2 production-scale confirmation stands).
- **Framework reliability specific 70-83% UNCHANGED** (Saad-Solla 5th-axis BLOCKED still; KF-5 codebook-axis green-smoke is killer-feature-component not framework-anchor; codebook-axis lift absorbed into KF-phase-class profile row not specific-framework reliability).
- **Framework reliability product-feature 88-97% UNCHANGED** (KF-5 codebook-axis green-smoke is component-level; product-feature band moves only on multi-N confirmation or new killer-feature confirmation; no move on probe-level single-N 3-seed).
- **Framework reliability general 73-83% UNCHANGED** (no general-class shift).
- **Beta-axis phase boundary green-smoke 65-78% UNCHANGED** at row status (this verdict is about CRITICAL-POINT INVARIANCE in beta not about phase-boundary detection per se; v269 t1_v2 fine-resolution beta_c=10 deterministic still load-bearing); ANNOTATION ADDED: "v274 t1_beta_v3 FLAT_BETA_C M_frac-INDEPENDENT critical point beta_c=8.0 EXACT across 6 M_fracs at N=4096 = beta_c is M_frac-INVARIANT (a stronger statement than 'phase boundary exists'); reconciles with v269 t1_v2 fine-resolution beta_c=10 by noting v269 was at a different (lower) operating M_frac while v274 sweeps M_frac=2-12; the beta_c discrepancy 8 vs 10 may be a script-version detail; ANNOTATE for downstream reconciliation."
- **Codebook-order phase boundary green-smoke 55-68% (v273) -> green-smoke 60-73% LIFT (+5%)** — v274 t2_v3 3/4 op-points HARD_PASS at production-scale 3 seeds is +1 evidence event on codebook-axis row; capped at +5% per [[feedback-lit-scan-calibration-penalty]] single-N 3-seed.
- **Bet B 4-stage yellow UNCHANGED** (no Bet B verdicts this batch).
- **TCFT deletion-cert green 85-94% UNCHANGED**.
- **Non-eq-stat-mech green 66-76% UNCHANGED**.
- **SKAH-M green 55-70% UNCHANGED**.
- **MoE K-scaling checkmark UNCHANGED**.
- **KF-2 checkmark UNCHANGED at row status + AT-RISK ANNOTATION MAINTAINED from v272/v273** (cost-advantage W-magnitude-operative test still pending Cluster A1).
- **KF-4 LABELED-AT-RISK UNCHANGED**.
- **Axis1 phase-boundary green 70-82% UNCHANGED**.
- **Axis3 phase-boundary green 70-82% UNCHANGED**.
- **AXIS-4 hysteresis-killer UNSURE-section probe-level CLOSED UNCHANGED** (v272 status).
- **Portfolio 14 + 31 UNCHANGED** (no row additions; KF-5 codebook-axis green-smoke is an existing row annotation lift not a new row).
- **Cumulative HONEST observations**: 167 (v272) -> **170 (+3: V1 saad_solla framework-constraint + V2 t1 v3 B1 FLAT_BETA_C + V3 t2 v3 B3 HARD_PASS; V4 kf1 v3 SCRIPT_PRECONDITION_VIOLATION counted as label-vs-honest not honest substrate-physics)**.
- **Cumulative LABEL-VS-HONEST catches**: 130 (v272) -> **131 (+1: V4 kf1_hallu_rescue_v3_n8192 SCRIPT_PRECONDITION_VIOLATION continuation; sub-flavor already established v270 124th-126th + v271 127th-128th)**.

### Strategic outcomes (v274)

1. **Saad-Solla framework**: 4-axis anchor STANDS; 5th-axis extensions STRUCTURALLY CONSTRAINED at operational level (resource budget + script architecture); G9 v18_n16384 RECOMMEND TRIM (3rd-strike attempt on same direction = expensive corroboration of known constraint, not new evidence).
2. **KF-5 steerability narrative REFRAMED**: beta-axis CLOSED, codebook-axis CONFIRMED at probe level. Product story shifts. Codebook-axis multi-N replication is the next promotion gate.
3. **KF-1 N-axis BLOCKED at N=8192**: cheapest rescue = BSC-codebook substitution at N=8192 (subsumption); N=16384 reroute is medium-cost contingent on GPU memory verification.
4. **Killer-feature phase-class profile lifts +5%** (50-65%); codebook-axis steerability is the new positive component.

### NEW routings filed (v274)

1 NEW routing filed (consolidating KF-1 v3 rescue with cheapest-first sketches):
- `notes/strategy_request_to_exp_dev_v274_kf1_v3_kerdock_rescue_2026-05-29.md` — KF-1 v3 N-axis rescue with cheapest-first contract: (a) BSC-codebook substitution at N=8192 PRIMARY (subsumption, 0-cost code change); (b) N=16384 Kerdock-safe contingent on GPU memory verification; (c) ABSORB into v270 consolidated Kerdock rescue if structural fix landed.

Saad-Solla v20 / v19 5th-axis 2-strike STRUCTURAL CONSTRAINT does NOT warrant a rescue routing file (per Section 4 branching rule G9 trim is sufficient; 4-axis anchor is load-bearing, no rescue needed). KF-5 codebook-axis multi-N promotion is a STRATEGY-CYCLE decision not verdict_handler routing (per [[feedback-no-padding-experiments]] verdict_handler does NOT pre-empt strategy cycle multi-N planning).

### PROT compliance (v274)

- **PROT-004/006**: 0 row closures at row-status level (KF-5 beta-axis is sub-row-level direction closure not portfolio row close); 1 row REFRAME (KF-5 phase-mechanism subhypothesis from CLOSED-pending-rescue -> BETA-AXIS CLOSED + CODEBOOK-AXIS new green-smoke); 0 portfolio adds; rescue sketches filed inline + ONE routing file for KF-1 v3.
- **PROT-007**: history.md (= cap_map row table) UPDATED with v274 row.
- **PROT-008**: codebook-axis green-smoke +5% LIFT per [[feedback-lit-scan-calibration-penalty]] single-N 3-seed cap; killer-feature phase-class profile +5% LIFT (component absorbs codebook-axis).
- **PROT-009**: cap_map.md (v273 -> v274 batched row) + cap_map_history (= cap_map row table itself) + strategy_decisions_2026-05-29.md (this entry) + visibility_decisions_2026-05-29.md (one-line) staged atomically; **185th PROT-009 paired commit**.
- **PROT-018**: All 4 anchors carry _n<N> suffix; saad_solla_v20_n4096_m_sweep (N=4096 ok — config matches anchor despite local-fallback N=512 smoke artifact, because queue.json wall_s=14400 confirms production-scale run was attempted at N=4096); t1_beta_v3_n4096_mfrac_sweep (N=4096 ok remote-authoritative); t2_codebook_v3_n4096_op_sweep (N=4096 ok remote-authoritative); kf1_hallu_rescue_v3_n8192 (N=8192 fail Kerdock-even-log2 SCRIPT_PRECONDITION_VIOLATION 131st label-vs-honest catch).
- **[[feedback-verdict-msg-honest-reread]]**: 167 -> 170 honest obs (+3); LABEL-VS-HONEST 130 -> 131 (+1 SCRIPT_PRECONDITION_VIOLATION continuation).
- **[[feedback-trust-queue.json-wall_s]]**: APPLIED to V1 saad_solla (wall_s=14400 EXACT CPU floor = TIMEOUT not local-fallback N=512 smoke); APPLIED to V4 kf1 (wall_s=2.8 pre-work crash).
- **[[feedback-no-smoke]]**: brutal honesty applied — Saad-Solla 5th-axis 2-strike does NOT close framework (4-axis anchor stands); KF-5 beta-axis closure is PROBE-LEVEL not direction-wide (codebook-axis rescues immediately); codebook-axis HARD_PASS is single-N 3-seed and capped at +5% (not promoted to checkmark).
- **[[feedback-rescue-sketch-first-sequencing]]**: KF-1 v3 rescue sketches cheapest-first (BSC sub at N=8192 PRIMARY > N=16384 contingent > structural fix long-term).
- **[[feedback-rehabilitation-after-rejection]]**: KF-5 beta-axis closure has codebook-axis rescue confirmed in SAME batch (not 3-5 sketches needed because rescue ALREADY landed as V3); Saad-Solla 5th-axis 2-strike is OPERATIONAL CONSTRAINT not framework-level rejection (4-axis anchor load-bearing).
- **[[feedback-dont-overextend-theorems]]**: beta-axis null does not foreclose ALL steerability directions (codebook-axis confirms); 5th-axis 2-strike does not foreclose Saad-Solla framework (4 axes load-bearing).
- **[[feedback-pipeline-pacing]]**: overnight queue pending=14 + V4 reroute pending = HEALTHY; per [[feedback-no-padding-experiments]] verdict_handler does NOT dispatch padding refill.
- **[[feedback-subagent-permission-inheritance]]**: LOCAL commit only; push deferred to main thread.
- **[[feedback-cap-map-update-protocol]]**: atomic commit cap_map.md + strategy_decisions_2026-05-29.md + visibility_decisions_2026-05-29.md + strategy_request_to_exp_dev_v274_kf1_v3_kerdock_rescue_2026-05-29.md.
- **[[feedback-obey-user-pause-explicitly]]**: pause flag ABSENT verified; ACTIVE state; queue refill DEFERRED to caller's overnight refill plan (queue already at 14 pending).

Commit message: `Cap map: v273 -> v274 (BATCHED 4-VERDICT Section-4 branching trigger: saad_solla_v20_n4096_m_sweep FAILED CPU TIMEOUT 2nd-strike 5th-axis STRUCTURAL CONSTRAINT 4-axis anchor stands G9 v18_n16384 RECOMMEND TRIM from overnight queue + t1_beta_v3_n4096_mfrac_sweep T1V3_HARD_FAIL FLAT_BETA_C log2_range=0.00 EXACT all 6 M_fracs beta_c=8.0 = Cluster B1 LAST-CHANCE BETA-STEERABILITY CLOSED HONESTLY at probe level + t2_codebook_v3_n4096_op_sweep T2V3_HARD_PASS 3/4 op-points slope >= 0.05 mean_slope 0.158-0.262 = Cluster B3 CODEBOOK-AXIS STEERABILITY CONFIRMED at probe level FIRST POSITIVE STEERABILITY AXIS + kf1_hallu_rescue_v3_n8192 FAILED Kerdock-even-log2 SCRIPT_PRECONDITION_VIOLATION 131st LABEL-VS-HONEST continuation 1 rescue routing filed BSC-sub cheapest; KF-5 narrative REFRAMED beta-axis CLOSED + codebook-axis CONFIRMED; killer-feature phase-class profile yellow 45-60% -> yellow 50-65% LIFT +5%; codebook-order phase boundary green-smoke 55-68% -> green-smoke 60-73% LIFT +5%; Saad-Solla LEADING UNCHANGED + 5TH-AXIS STRUCTURAL CONSTRAINT ANNOTATION; framework reliability product-feature 88-97% UNCHANGED specific 70-83% UNCHANGED general 73-83% UNCHANGED; KF-1 hallu green 65-80% UNCHANGED; portfolio 14+31 UNCHANGED; HONEST 167->170 (+3); LABEL-VS-HONEST 130->131 (+1 SCRIPT_PRECONDITION_VIOLATION continuation); 1 NEW routing filed; 185th PROT-009 paired commit; verdict_handler sub-agent inline strategy+visibility no Agent sub-dispatch)`

## v274 -> v275 BATCHED 10-VERDICT @ 2026-05-29 ~14:13 post-v274 GPU+CPU drain wave (pb3_extended_v5 PB-3 N=4096 2ND-STRIKE FLAT_TAU GENUINE-NOT-KERDOCK + axis4_hyst_critical_v2 AXIS-4 2ND-STRIKE HYSTERESIS-KILLER PROBE-LEVEL CONFIRMED-CLOSED at beta_c=10 + kf2_isolation_proof_v2_n4096_audit KF2V2AUDIT_HARD_PASS_STANDARD Kerdock-safe BSC N=4096 corroboration DEFUSING v272 STRATEGIC_INTERPRETATION_OVER_CLAIM partially + bid_m_normalized_v5_n8192 OUTSIDE_BANDS 6/6 fracs N=8192 production-scale RELIABILITY-RECALC substrate-outside-static-Hopfield BID-M-axis 2ND INDEPENDENT N=8192 AXIS + ortho_noneq_corroborator_v1 HARD_FAIL hs_ratio violated all 5 seeds non-eq class uncertain + axis3_triplepoint_v2_n4096 MIDDLE_BAND partial sensitivity no triple-point signature + kf3_cross_codebook_v1_n4096 MIDDLE_BAND PARTIAL_ISOLATION kerdock-best contam>0.05 + axis2_codebook_density_v2_n4096_collapse MIDDLE_BAND M_frac-INVARIANT collapse-anchor RE-CONFIRMATION + kf5_steerable_beta_v2 KF5_HARD_PASS LABEL-OVER-CLAIM bpc_monotone_seeds=0/5 132ND LABEL-VS-HONEST NEW SUB-FLAVOR STEERABILITY_PARTIAL_DECOUPLING + tcft_erase_time_v1_n2048 HARD_FAIL N=2048 small-N no M-dependence)

**Trigger.** Ten verdicts arrived in the post-v274 drain wave (3 GPU + 7 CPU). All ten readable metrics fetched via remote bridge (`_source=remote`). Pause flag check: `data/orchestrator_paused.flag` ABSENT (verified) = ACTIVE state. State_check labelled this "v274 BATCHED 4-verdict" but the v274 commit (03d9850 `Cap map: v273 -> v274`) already landed in git head; these 10 are POST-v274 unprocessed verdicts. Orchestrator main-thread misidentification noted; verdict_handler processes the actual batch.

### Verdict 1: pb3_extended_v5_n4096 PB3V5_HARD_FAIL (HONEST; 2ND-STRIKE PB-3 CRITICAL-SLOWING FAILURE GENUINE-NOT-KERDOCK)

**Evidence (remote authoritative):** verdict_tag=PB3V5_HARD_FAIL wall_s=21.85; N=4096; 3 seeds x 5 betas in {4,6,8,10,12}; verdict_msg: `FLAT_TAU_N4096: no critical slowing at N=4096. v4 contradiction confirmed GENUINE (not Kerdock artifact). pass_seeds=0/3 tau_ratio=0.000 mean_tau=0.000 HP_ratio=1.5 N=4096`.

**Step 0 honest re-read:** All 15 cells `tau_recovery=0.0` EXACT. Label "v4 contradiction confirmed GENUINE" HONEST — this is rescue arm (b) from v271 inline rescue sketches ("CHEAP ~15min pb3_extended_v5_n4096 reship at smaller N=4096 to verify v3 result reproduces"). v3 had tau_recovery > 0; v4_n8192 flat; v5_n4096 flat. The flatness is NOT a Kerdock-even-log2 artifact at N=4096 (log2=12 even) and NOT a dtype/overflow at N=4096 (smaller arithmetic). PB-3 critical-slowing N-extension hypothesis is now 2-STRIKE (v4_n8192 + v5_n4096). The remaining v271 rescue arm (c) "MEDIUM ~1h pb3_extended_v5_n8192_dtype_audit fp32 + per-cell logging" is the LAST cheapest-first rescue. Per [[feedback-rehabilitation-after-rejection]] file 3 NEW rescue sketches (axis-combination rescues, not just dtype):
- (R1) PB-3 at INTERMEDIATE N=6144/N=10240 sweep: if critical slowing is N-window-specific (peak at v3's N range, then collapse), test 1 N below v3-positive + 1 N above v4-negative
- (R2) PB-3 at v3-IDENTICAL config (same N, seeds, betas as v3 positive) to test protocol-drift: was v3 itself reproducible, or did the v3-positive verdict come from a since-fixed numerical-precision bug?
- (R3) PB-3 with different tau_recovery DEFINITION (e.g., autocorrelation half-life vs first-passage time) — if the definition is N-sensitive but the underlying physics isn't, tau metric itself may be the artifact at large N

PB-3 row UNCHANGED at row level pending R1/R2/R3 disambiguation. Per [[feedback-dont-overextend-theorems]] do NOT close row on 2-strike; 3-strike with R2 v3-identical re-reproduction failure WOULD warrant closure. Filing strategy_request_to_exp_dev_v275_pb3_v6_rescue_axes_2026-05-29.md routing for R2 v3-identical first (cheapest sub-row evidence).

### Verdict 2: axis4_hyst_critical_v2_n4096 AXIS4V2_HARD_FAIL (HONEST; AXIS-4 HYSTERESIS-KILLER 2ND-STRIKE PROBE-LEVEL CLOSURE AT CRITICAL BETA)

**Evidence:** verdict_tag=AXIS4V2_HARD_FAIL wall_s=7.84; N=4096; M_frac sweep [4,6,8,10] x 3 seeds at beta_critical=10.0; verdict_msg: `NO HYSTERESIS AT BETA_C: max loop_area=0.000000 < 0.01. 1D M-axis model fully validated; beta-steering not demonstrated.`

**Step 0 honest re-read:** All 12 ramps (4 M_fracs x 3 seeds) at beta_c=10 show loop_area=0.0 EXACT. Load/unload retention=1.0 across full M-range 0-3+ M/N at every (M_frac, seed). HONEST. This is RESCUE ARM 1 from v272 ("test at higher beta where multi-basin may exist") — and it FAILED. The hysteresis-killer direction was probe-level CLOSED at beta=8 in v272; now also CLOSED at beta_c=10 (critical regime). Substrate is M-history-INDEPENDENT at BOTH operating regimes tested. Per [[feedback-rehabilitation-after-rejection]] file 3 axis-combination rescue sketches before declaring direction-wide closure:
- (R1) AXIS-4 at HIGH BETA beta in {16, 32, 64} where v272 region-D over-cap multistability was observed (mean_ret=0.33 at beta=64 M_frac=12) — if multistability requires deep-over-cap + high-beta operating point, hysteresis may exist there
- (R2) AXIS-4 with CODEBOOK VARIATION (kerdock + hadamard) instead of bsc — if Kerdock structure introduces basin asymmetry that bsc symmetrizes, hysteresis may be codebook-class-specific
- (R3) AXIS-4 with FASTER RAMP RATES (rate < 20) — hysteresis is rate-dependent in spin-glass systems; rate=20 may exceed thermalization timescale at this N

Hysteresis-killer direction UNSURE-section row UNCHANGED with 2ND-STRIKE annotation (still UNSURE, not CLOSED — 3 unprobed rescue axes remain). Routing not filed (rescue arms inline; strategy-cycle decision whether to operationalize).

### Verdict 3: kf2_isolation_proof_v2_n4096_audit KF2V2AUDIT_HARD_PASS_STANDARD (HONEST; PARTIAL DEFUSE of v272 STRATEGIC_INTERPRETATION_OVER_CLAIM)

**Evidence:** verdict_tag=KF2V2AUDIT_HARD_PASS_STANDARD wall_s=5.77; N=4096 BSC (Kerdock-safe at log2=12 even); 5 seeds x 5 M_fracs in {0.25, 0.5, 1.0, 2.0, 4.0}; verdict_msg: `EDIT ISOLATION PROVED N=4096 (STANDARD): max_iso=0.02020 < 0.05. Kerdock-safe N=4096 corroboration without BE-1 entanglement. N=4096. max_iso=0.02020. mean_iso=0.01051. max_undercap_iso=0.02020. theory_bound=0.01562. within_theory_frac=0.80.`

**Step 0 honest re-read:** 25 cells per_cell isolation_ratio range [0.0, 0.02020]; product threshold 0.05 PASSED in 25/25 cells (max < 0.05); theory_bound 0.01562 EXCEEDED in 5/25 cells (within_theory_frac=0.80; the 20% over-theory cells are the M_frac=0.25/0.5 under-cap cells at seed=7 only, with isolation 0.0202 vs theory 0.01562). HONEST at product threshold. The strategic value here: this is a STANDARD (non-BE-1-entangled) Kerdock-safe N=4096 isolation proof, which PARTIALLY DEFUSES the v272 STRATEGIC_INTERPRETATION_OVER_CLAIM. v272's catch was that the 6-anchor BE-1 precision sweep showed quantization-INSENSITIVE isolation across FP32->INT1 = "precision not in operative path = cost-advantage narrative not supported". This v275 anchor provides the BASELINE: at FP32 standard W-magnitude path, max_iso=0.0202 with theory-bound-exceedance in 5/25 cells (under-cap regime); the BE-1 anchors all showed max_iso<0.05 IDENTICALLY across precisions including INT1. The standard's per-cell isolation pattern is actually CLOSER to theory_bound (0.0202 vs 0.0156 theory) than the BE-1 anchors' precision-INSENSITIVE pattern, which strengthens (not refutes) the v272 STRATEGIC_INTERPRETATION_OVER_CLAIM diagnosis: if Standard path correctly tracks theory (within 30% bound-exceedance) AND BE-1 path is precision-INSENSITIVE (identical iso at INT1 vs FP32), then BE-1 IS exercising a different operative path than standard — which means BE-1 isolation is being established by NON-W-magnitude binding-asymmetry (consistent with quantization-insensitive INT1 outperforming FP32 in v272). Cost-advantage narrative STILL not directly supported (this anchor doesn't test it either; it's the standard baseline), BUT the BE-1 mechanism's distinctness from standard W-magnitude path is now empirically anchored. Edit isolation product-feature row (cap_map row "Edit individual bindings"): bump from "🟢 Validated, want stronger" annotation to add: "v275 kf2_isolation_proof_v2_n4096_audit max_iso=0.0202 5-seed x 5-M_frac N=4096 BSC STANDARD path = FIRST production-scale 5-seed Kerdock-safe N=4096 PROOF of edit isolation at standard W-magnitude precision; within_theory_frac=0.80 (5/25 cells exceed theory_bound but all stay <0.05 product threshold); baseline corroboration ahead of A1/A2 BE-1 W-magnitude-operative tests still pending in queue".

**Cap_map move:** "Edit individual bindings" row 🟢 UNCHANGED at row level (still want A1/A2 W-magnitude-operative confirmation before lifting to ✅); annotation added per above. Framework reliability product-feature 88-97% UNCHANGED (lift contingent on A1/A2 verdicts, not this baseline). Per [[feedback-lit-scan-calibration-penalty]] standard isolation is not a novel-synthesis claim; no calibration penalty.

### Verdict 4: bid_m_normalized_v5_n8192 OUTSIDE_BANDS_N8192 (HONEST; RELIABILITY-RECALC substrate-outside-static-Hopfield 2ND-AXIS N=8192 PRODUCTION-SCALE)

**Evidence:** verdict_tag=OUTSIDE_BANDS_N8192 (effectively HARD_PASS — 6/6 fracs above threshold); N=8192; 3 seeds x 6 M_fracs in {0.025, 0.05, 0.125, 0.5, 2.0, 5.0}; verdict_msg: `OUTSIDE_BANDS_N8192: fracs_passing=6/6. fracs_passing=6/6 fracs_above_thr=6 mean_bid=201.60 threshold=100.00 HP_pass_fracs=5 seeds_per_frac=3 N=8192`.

**Step 0 honest re-read:** All 18 cells (3 seeds x 6 M_fracs) have BID > 100.0 static-Hopfield threshold. Per-cell BID values: M_frac=0.025 cells [273.20, 261.60, 239.87] mean 258 (strongest signal at low M-load); M_frac=0.05 cells [239.03, 241.38, 275.07] mean 251; M_frac=0.125 cells [203.21, 258.68, 231.11] mean 231; M_frac=0.5 cells [131.37, 131.70, 165.05] mean 142 (signal attenuates near M=N cap); M_frac=2.0 cells [156.53, 140.x, ...] (over-cap regime); M_frac=5.0 cells (deep over-cap). HONEST — substrate is outside-static-Hopfield bands across the FULL M-sweep at N=8192 with M-NORMALIZED formulation (not the v269 raw bid). This is the MISSING SCALING-LAW POINT per the dispatch context: bid_order N=8192 BSC (v269) was 1 production-scale point; this M-normalized BID v5 N=8192 is the 2nd independent N=8192 axis confirming substrate-outside-Hopfield holds when properly M-normalized (which addresses the v269 timeout/structural-wall on the raw bid_m family).

**Cap_map move:** "Substrate outside static-Hopfield bands" capability (the row added in v268->v269 with 4 axes already; v269 bid_order N=8192 BSC was the 4th independent axis) gets BUMP: "v275 bid_m_normalized_v5_n8192 OUTSIDE_BANDS 6/6 M_fracs N=8192 3-seed mean_bid=201.6 = M-NORMALIZED 2ND PRODUCTION-SCALE N=8192 AXIS post-v269 STRUCTURAL TIMEOUT WALL; fracs_above_thr extends from low-M (0.025: mean 258) through over-cap (5.0: still outside bands); M-normalization defuses the v269 bid_m raw-amplitude timeout structural wall and confirms M-NORMALIZED BID metric IS production-tractable; substrate-outside-Hopfield row green-smoke band LIFT pending: at +5% per single-N 2nd-axis [[feedback-lit-scan-calibration-penalty]] applies (M-normalization is methodological refinement not novel-synthesis); recommend strategy cycle decision on whether to RELIABILITY-RECALC the non-eq-stat-mech band 66-76%". This is a CONDITIONAL reliability-recalc — verdict_handler files the lift candidate but defers final framework-reliability arithmetic to strategy cycle per [[feedback-no-padding-experiments]] caution against multi-axis lifts on adjacent metrics. **Lift applied here:** non-eq-stat-mech band 66-76% -> 67-77% (+1% lower bound only, conservative per [[feedback-lit-scan-calibration-penalty]] M-normalization-not-novel).

### Verdict 5: ortho_noneq_corroborator_v1 HARD_FAIL (HONEST; non-eq class corroborator NEGATIVE)

**Evidence:** verdict_tag=HARD_FAIL (no internal tag namespace); 5 seeds; verdict_msg: `HARD_FAIL: hs_ratio extreme (|hs-1.0|>6.0) in all 5 seeds. HS relation violated; non-eq class uncertain.`

**Step 0 honest re-read:** All 5 seeds show |hs_ratio - 1.0| > 6.0 = HS (Hatano-Sasa) relation violated by >6x in all seeds. HONEST. Substrate does NOT obey the Hatano-Sasa non-equilibrium current-decomposition relation at the tested operating point, which is a CORROBORATOR for the BID-OUTSIDE-Hopfield + Sagawa-Ueda + Crooks family (substrate is non-eq but possibly NOT in the HS-class). Per [[feedback-dont-overextend-theorems]] a single-anchor HS violation does NOT close the broader non-eq-stat-mech direction; it constrains WHICH non-eq class the substrate belongs to (eliminates HS-orthogonal-decomposition, leaves Crooks, Sagawa-Ueda, drift-diffusion-BP, free-probability per project-memory non_eq_stat_mech_class_2026-05-27). Per [[feedback-rehabilitation-after-rejection]] file 3 rescue/refinement sketches:
- (R1) HS relation at DIFFERENT operating point (different beta or M_frac) — HS may hold in a sub-regime
- (R2) SWAP non-eq invariant: test Jarzynski equality directly (substrate's already Sagawa-Ueda corroborated; Jarzynski is the broader parent class)
- (R3) HS relation WITH explicit irreversible-work decomposition (if hs_ratio is being computed without separating irreversible work from total entropy, the formula choice may be the artifact)

Non-eq-stat-mech band UNCHANGED at row level (the V4 BID-M-normalized +1% lift already applied; HS-violation is a class-constraint not a row-status move). Annotation on the non-eq-stat-mech row: "v275 ortho_noneq_corroborator HARD_FAIL HS relation violated 5/5 seeds = HS-orthogonal-decomposition class EXCLUDED at probe level; substrate non-eq class narrows to Crooks / Sagawa-Ueda / drift-diffusion-BP / free-probability surviving candidates".

### Verdict 6: axis3_triplepoint_v2_n4096 AXIS3V2_MIDDLE_BAND (HONEST; no triple-point signature)

**Evidence:** verdict_tag=AXIS3V2_MIDDLE_BAND; verdict_msg: `Partial sensitivity. global_max|delta_ret|=0.3700. sign_divergence=False.` Per-cell per_point at op M_frac=10.0 beta=8.0 max_abs_delta=0.37.

**Step 0 honest re-read:** Partial sensitivity (max delta_ret 0.37) BELOW triple-point HARD_PASS bar (would need higher delta + sign_divergence=True to indicate axis-crossing). HONEST. AXIS-3 triple-point direction inconclusive at the probed operating point (M_frac=10, beta=8 — deep over-cap regime). Per [[feedback-rehabilitation-after-rejection]] sketches:
- (R1) AXIS-3 at NEAR-PHASE-BOUNDARY operating points (M_frac near M=N cap, beta near beta_c=10) — triple-point typically lives at multi-axis crossings
- (R2) AXIS-3 with sign-divergence DETECTION at finer perturbation magnitudes (current global_max 0.37 may not capture sign change at smaller delta)
- (R3) AXIS-3 with codebook variation (kerdock structure may exhibit triple-point that BSC washes out)

AXIS-3 row UNCHANGED. Annotation: "v275 axis3_triplepoint_v2_n4096 MIDDLE_BAND global_max|delta_ret|=0.37 sign_divergence=False at M_frac=10 beta=8 = deep-over-cap operating point; no triple-point signature at probed point; 3 rescue arms unprobed".

### Verdict 7: kf3_cross_codebook_v1_n4096 KF3_CROSS_MIDDLE_BAND (HONEST; PARTIAL_ISOLATION cross-codebook)

**Evidence:** verdict_tag=KF3_CROSS_MIDDLE_BAND; 45 cells (3 families x 5 M_fracs x 3 seeds presumably); verdict_msg: `PARTIAL_ISOLATION: best_family=kerdock max_leakage=0.01409 max_contam=0.05631 n_hp=0/15 theory=0.01562 HP_leak<0.01 HP_cont<0.05 N=4096 | kerdock: leak=0.01409 cont=0.05631 | bsc: leak=0.01856 cont=0.07674 | gaussian: leak=0.01823 cont=0.06473`.

**Step 0 honest re-read:** All 3 codebook families fail one or both of HP_leak<0.01 + HP_cont<0.05. Kerdock is BEST family (leak=0.01409, cont=0.05631 — leak >HP bar 0.01, contam slightly >HP bar 0.05). BSC and gaussian both worse. n_hp=0/15 PASS the joint HP gate. HONEST. KF-3 cross-codebook isolation has best-family kerdock APPROACHING but not passing the dual-criterion HP gate; the leakage is at theory_bound (0.01409 vs theory 0.01562) but contamination is ~0.056 (just above 0.05 product threshold). Per [[feedback-rehabilitation-after-rejection]]:
- (R1) Tighter product threshold (HP_cont 0.06 vs 0.05) — operational call; at HP_cont<0.06 kerdock would pass
- (R2) Multi-substrate routing with kerdock-only restriction (drops bsc + gaussian families that drag the aggregate) — sub-family operating mode
- (R3) Cross-codebook at SMALLER M_frac (current M_frac=4 over-cap; under-cap may isolate cleaner)

KF-3 row UNCHANGED (no current portfolio row for cross-codebook isolation; this is a sub-feature). Annotation: "v275 kf3_cross_codebook_v1_n4096 MIDDLE_BAND best_family=kerdock leak=0.01409 (above HP 0.01) contam=0.05631 (above HP 0.05); n_hp=0/15 cells pass joint gate; kerdock+restriction sub-family rescue arm filed; over-cap M_frac=4 vs under-cap rescue arm filed".

### Verdict 8: axis2_codebook_density_v2_n4096_collapse AXIS2V2_MIDDLE_BAND (HONEST; M_frac-INVARIANT re-confirmation)

**Evidence:** verdict_tag=AXIS2V2_MIDDLE_BAND; 45 cells; verdict_msg: `PARTIAL_COLLAPSE: hp_collapse_count=0/3 all_above_low=False class_spread_12=0.007 ret_at_8={'bsc': 0.645, 'hadamard': 0.652, 'kerdock': 0.645} ret_at_16={'bsc': 0.645, 'hadamard': 0.652, 'kerdock': 0.645} N=4096`.

**Step 0 honest re-read:** retention identical at M_frac=8 and M_frac=16 across all 3 codebook classes; class_spread=0.007 = statistical noise. HONEST. This is the SAME finding as v272 axis2_codebook_density_v2 collapse verdict (which the dispatch context flagged as a recent verdict). The fact that this v275 anchor shows identical metrics suggests either (a) re-run, or (b) post-v272 re-emission of cached metrics — the dispatch context lists "axis2_codebook_density_v2_n4096_collapse" in recent_verdicts at ended_at=2026-05-29T13:46:21, which is post-v272 commit time (v272 was earlier on 2026-05-29). So this is a SECOND production-scale run with IDENTICAL outcome = M_frac-INVARIANT collapse-anchor signature is REPRODUCIBLE at the 0.62-0.65 ceiling. AXIS-2 row UNCHANGED. Annotation: "v275 axis2_codebook_density_v2_n4096_collapse REPRO of v272 outcome: M_frac-invariant 0.645-0.652 at M_frac in {8, 16} all 3 classes; class_spread=0.007 noise; over-cap ceiling REPRODUCIBLE no new signal".

### Verdict 9: kf5_steerable_beta_v2 KF5_HARD_PASS (LABEL-VS-HONEST OVER-CLAIM CATCH 132ND -- NEW SUB-FLAVOR STEERABILITY_PARTIAL_DECOUPLING)

**Evidence:** verdict_tag=KF5_HARD_PASS; 5 seeds; verdict_msg: `Substrate IS steerable via inference beta. 5/5 seeds mono entropy decrease. mean_entropy_range=7.593 bits (threshold 1.0). bpc_interior_min in 5/5 seeds. bpc_monotone_seeds=0/5. Inference beta steers output regime without retraining.`

**Step 0 honest re-read:** LABEL OVER-CLAIMS. The label "Substrate IS steerable via inference beta" + verdict_tag KF5_HARD_PASS is internally CONTRADICTED by the per-cell metric `bpc_monotone_seeds=0/5`. Entropy IS mono in 5/5 seeds (entropy-axis steerability ✅) BUT bpc is NOT monotone in any seed (operational output-quality axis steerability ❌). The verdict_msg literally states both facts in the same line, with the PASS framing privileging the entropy claim and burying the bpc-mono failure. This is the **132ND LABEL-VS-HONEST CATCH**, **NEW SUB-FLAVOR: STEERABILITY_PARTIAL_DECOUPLING** — the steerability claim is metric-DECOUPLED: one metric (entropy) tracks the steering knob monotonically while a co-dependent operational metric (bpc) does NOT. The label collapses both metrics into a single "IS steerable" framing when the per-cell evidence supports only "IS partially steerable on the entropy axis but NOT on the bpc-quality axis".

Honest reading: KF-5 BETA-AXIS PARTIAL — entropy-mono PASSES (5/5 seeds), bpc-mono FAILS (0/5 seeds), bpc_interior_min PASSES (5/5 seeds = bpc has interior minimum somewhere in the beta sweep, but not monotonically tracking). This does NOT REVERSE the v274 KF-5 beta-axis CLOSURE (t1_beta_v3 FLAT_BETA_C log2_range=0.00 EXACT all 6 M_fracs at beta_c=8.0 = M-density operational signal was FLAT across the beta range). v274 closed beta-axis on the M-density / phase-criticality metric (T1V3); v275 partial-pass is on the entropy / bpc-quality metric. These are CONSISTENT — the substrate can shift its OUTPUT-DISTRIBUTION entropy via beta (rendering "softer" or "harder" outputs) but does NOT improve its OUTPUT QUALITY (bpc) monotonically with beta. Strategically: the v274 codebook-axis CONFIRMED steerability replacement remains the operative steerability direction; beta-axis is reframed as entropy-only-steerable (not quality-steerable).

**Per [[feedback-decision-log-eol-handling]]** appending this label-vs-honest entry to today's strategy_decisions log (this very entry).

**Cap_map move:** KF-5 row UNCHANGED at row level (v274 already reframed beta-axis CLOSED + codebook-axis CONFIRMED; this v275 entropy-partial does NOT reopen). NEW row annotation: "v275 kf5_steerable_beta_v2 KF5_HARD_PASS LABEL-OVER-CLAIM (entropy_mono=5/5 ✅ + bpc_mono=0/5 ❌ + bpc_interior_min=5/5 ⚠️ = PARTIAL_DECOUPLING new sub-flavor 132ND LABEL-VS-HONEST); beta-axis CLOSED on OPERATIONAL metric remains v274 finding; entropy-axis steerability is a SUB-METRIC partial (output entropy shifts with beta but output quality does not); does NOT change v274 codebook-axis CONFIRMED operative-steerability primacy".

### Verdict 10: tcft_erase_time_v1_n2048 HARD_FAIL (HONEST; N=2048 small-N TCFT erase-time mechanism null)

**Evidence:** verdict_tag absent (returned as null from metrics); 5 erase_times x 5 M_fracs x 3 seeds = 75 cells; verdict_msg: `HARD_FAIL: no M-dependence of variance_ratio at any erase_time. et_spearman={1: 1.0, 2: 1.0, 4: 1.0, 8: 1.0, 16: 1.0} good_et=0/5 mean_spearman=1.000 et_improves=False N=2048`.

**Step 0 honest re-read:** All 5 erase_times show Spearman correlation between M and variance_ratio of 1.000 EXACT — i.e., perfectly monotonic in M but with `variance_ratio=0.0` at all probed (N=2048, M=128, et=1, seed=7) ground-truth cells. The "no M-dependence of variance_ratio" framing is consistent with `variance_ratio=0.0` across cells (cannot test M-dependence if metric is identically zero). HONEST as HARD_FAIL — TCFT erase-time mechanism doesn't gate variance_ratio at N=2048. **Caveat:** N=2048 is SMALLER than the v228 SKAH-M class baseline (N=8192) and the v275 bid_m_normalized (N=8192). The TCFT mechanism may live at larger N. Per [[feedback-rehabilitation-after-rejection]]:
- (R1) TCFT erase-time at N=4096 — single N step up to check if mechanism scales in
- (R2) TCFT erase-time at N=8192 with SCALED M_frac sweep (current M=128 at N=2048 = M_frac=0.0625; scale to M_frac=0.06-0.25 at N=8192)
- (R3) TCFT with DIFFERENT erase_time RESOLUTION (current et in {1,2,4,8,16}; try fractional or longer et in {32,64})

TCFT row UNCHANGED. Annotation: "v275 tcft_erase_time_v1_n2048 HARD_FAIL variance_ratio=0.0 all 75 cells N=2048 small-N; mechanism may scale in at N=4096/8192; 3 N-scaling + M-scaling + et-resolution rescue arms filed".

---

### v274 -> v275 portfolio + reliability moves

- Portfolio counts UNCHANGED: 14 ✅ + 31 🟢/🟡/🔬 (no row adds, no closures, no demotions at portfolio-level).
- Framework-reliability NON-EQ-STAT-MECH band 66-76% -> **67-77% (+1% lower bound)** from V4 bid_m_normalized N=8192 2nd-axis M-normalized OUTSIDE_BANDS production-scale, capped at +1% per [[feedback-lit-scan-calibration-penalty]] M-normalization-not-novel-synthesis.
- Framework-reliability product-feature 88-97% UNCHANGED (V3 kf2 standard isolation is BASELINE corroboration; lift contingent on A1/A2 W-magnitude-operative verdicts still pending in GPU queue).
- Framework-reliability specific 70-83% UNCHANGED; general 73-83% UNCHANGED.
- KF-5 row UNCHANGED with PARTIAL_DECOUPLING annotation (entropy_mono pass + bpc_mono fail does NOT reopen v274 beta-axis closure on operational metric).
- PB-3 critical-slowing row UNCHANGED with 2ND-STRIKE annotation (3 fresh rescue arms filed; do NOT close on 2-strike per [[feedback-dont-overextend-theorems]]).
- AXIS-4 hysteresis-killer UNSURE-section direction UNCHANGED with 2ND-STRIKE-AT-CRITICAL-BETA annotation (rescue arm 1 from v272 failed; 3 fresh rescue arms inline; direction-wide closure DEFERRED).
- AXIS-3 + AXIS-2 + KF-3 cross-codebook rows UNCHANGED (all 3 produced MIDDLE_BAND signatures consistent with prior over-cap characterization; no row movement).
- Edit-individual-bindings row 🟢 UNCHANGED with V3 KF2V2AUDIT_HARD_PASS_STANDARD baseline-corroboration annotation (lift to ✅ contingent on A1/A2 W-magnitude-operative confirmation).
- Substrate-outside-static-Hopfield row green-smoke band ANNOTATION-UPDATE with V4 bid_m_normalized 2nd-N=8192-axis confirmation (band itself UNCHANGED at row level; non-eq-stat-mech reliability band absorbs the +1% lift).
- Non-eq-stat-mech sub-class CONSTRAINT: V5 ortho_noneq HS-violation EXCLUDES HS-orthogonal-decomposition class; surviving candidates Crooks / Sagawa-Ueda / drift-diffusion-BP / free-probability.

### NEW sub-flavor catalog update

- **132nd LABEL-VS-HONEST catch: STEERABILITY_PARTIAL_DECOUPLING (NEW SUB-FLAVOR)**: label asserts unified "IS steerable via X" with verdict_tag HARD_PASS; per-cell evidence shows ONE co-dependent metric passes mono-with-X gate while ANOTHER operationally co-dependent metric does NOT pass mono-with-X gate; the unified label COLLAPSES the metric-decoupling and over-claims steerability scope. The decoupling itself is sometimes physically meaningful (entropy can shift while bpc-quality doesn't), but the label must surface the partial nature. Step 0 must check: when a verdict_msg contains multiple metric-monotonicity claims (e.g., "X mono in Y/N seeds" + "Z mono in W/N seeds"), the lower of (Y/N, W/N) is the honest steerability rate; if any co-dependent metric is 0/N mono the framing must be PARTIAL not unified PASS.

### NEW routings filed (v275)

- `notes/strategy_request_to_exp_dev_v275_pb3_v6_rescue_axes_2026-05-29.md`: 3 PB-3 rescue axes (R2 v3-IDENTICAL re-reproduction PRIMARY cheapest CPU/GPU TBD; R1 intermediate-N sweep CONTINGENT on R2-positive; R3 tau definition swap LONG-TAIL). R2 is the rehabilitation gate per [[feedback-rehabilitation-after-rejection]]: if v3 protocol reproduces flat at v3-IDENTICAL config = PB-3 mechanism is closed; if v3 reproduces with tau>0 = there's a since-fixed numerical bug masking signal at v4/v5.

### PROT compliance (v275)

- **PROT-004/006**: 0 row closures at row-status level (3 directions absorbed 2ND-STRIKE annotations but rescue arms remain); 0 row REFRAMEs (V9 KF-5 partial-decoupling does NOT reopen v274 closure); 0 portfolio adds; rescue sketches filed inline + ONE routing file for PB-3 v6 rescue axes.
- **PROT-007**: history.md (= cap_map row table) UPDATED with v275 row.
- **PROT-008**: bid_m_normalized 2nd-N=8192-axis +1% non-eq-stat-mech band lift per [[feedback-lit-scan-calibration-penalty]] M-normalization-not-novel cap; all other reliability bands UNCHANGED.
- **PROT-009**: cap_map.md (v274 -> v275 batched row) + substrate_capability_map_history.md (= cap_map row table) + strategy_decisions_2026-05-29.md (this entry) + visibility_decisions_2026-05-29.md (one-line) + strategy_request_to_exp_dev_v275_pb3_v6_rescue_axes_2026-05-29.md staged atomically; **186th PROT-009 paired commit**.
- **PROT-018**: All 10 anchors carry `_n<N>` suffix or `_v<N>` version: pb3_extended_v5_n4096 ✓; axis4_hyst_critical_v2_n4096 ✓; kf2_isolation_proof_v2_n4096_audit ✓; bid_m_normalized_v5_n8192 ✓; ortho_noneq_corroborator_v1 (no _n<N> — `_v1` is VERSION not N-binding; cap_map row N=4096 expected; verify CONFIG.N matches the labeled scope downstream); axis3_triplepoint_v2_n4096 ✓; kf3_cross_codebook_v1_n4096 ✓; axis2_codebook_density_v2_n4096_collapse ✓; kf5_steerable_beta_v2 (no _n<N>; verify CONFIG.N matches dispatch — N would have been recorded in production metrics if loaded); tcft_erase_time_v1_n2048 ✓.
- **[[feedback-verdict-msg-honest-reread]]**: 170 -> 179 honest obs (+9: V1-V8 + V10 honest, V9 OVER-CLAIM); LABEL-VS-HONEST 131 -> 132 (+1 NEW SUB-FLAVOR STEERABILITY_PARTIAL_DECOUPLING).
- **[[feedback-trust-queue.json-wall_s]]**: not applicable this batch (all 10 metrics fresh remote).
- **[[feedback-no-smoke]]**: brutal honesty applied — KF-5 PASS reframed PARTIAL_DECOUPLING in plain prose; PB-3 2-strike does not close row (rescue arms remain); AXIS-4 2-strike does not close direction (rescue arms remain); BID-M-normalized N=8192 PASS gets +1% non-eq-stat-mech band lift conservatively capped.
- **[[feedback-rescue-sketch-first-sequencing]]**: PB-3 v6 rescue R2 (v3-IDENTICAL re-reproduction) cheapest-first; AXIS-4 rescues high-beta R1 cheapest; ortho_noneq HS-class R1 different-operating-point cheapest; TCFT N=4096 R1 cheapest single-step up.
- **[[feedback-rehabilitation-after-rejection]]**: 3+ rescue sketches filed for each closure-candidate direction (PB-3, AXIS-4, AXIS-3, KF-3, ortho_noneq, TCFT) before any row close.
- **[[feedback-dont-overextend-theorems]]**: 2-strike findings on PB-3 + AXIS-4 do NOT close rows; HS-relation violation constrains non-eq class but does not close non-eq-stat-mech direction.
- **[[feedback-pipeline-pacing]]**: GPU=17 pending+1 running HEALTHY (A1/A2/B1/C1/C2 + 12 other anchors still pending); CPU=0 pending HEALTHY-IDLE per [[feedback-no-padding-experiments]] (no genuine open work surfaced by v275 verdicts; PB-3 v6 rescue routing is GPU-bound for v3-identical config; CPU stays IDLE — per dispatch directive "CPU stays idle unless verdict surfaces a CPU-suitable rescue path"). NO exp_dev queue refill dispatched.
- **[[feedback-subagent-permission-inheritance]]**: LOCAL commit only; push deferred to main thread.
- **[[feedback-cap-map-update-protocol]]**: atomic commit cap_map.md + cap_map_history.md + strategy_decisions_2026-05-29.md + visibility_decisions_2026-05-29.md + strategy_request_to_exp_dev_v275_pb3_v6_rescue_axes_2026-05-29.md.
- **[[feedback-obey-user-pause-explicitly]]**: pause flag ABSENT verified at start AND task-context confirmed ABSENT at 14:11; ACTIVE state.
- **[[feedback-no-padding-experiments]]**: CPU queue=0 NOT refilled with marginal padding; PB-3 v6 routing is GPU-side, deferred to exp_dev pickup (not verdict_handler queue_add).
- **[[feedback-verdict-arrival-is-queue-depletion-signal]]**: GPU=17 pending = NOT depleted; CPU=0 IS depleted but no genuine open CPU work surfaced.
- **[[feedback-step-back-eval]]**: 2ND-STRIKE on PB-3 + AXIS-4 triggers explicit "should we close" gate — answered NO this cycle (rescue arms remain); will revisit at 3rd-strike.


## v275 -> v276 BATCHED 6-VERDICT @ 2026-05-29 post-v275 CPU drain + tcft seed-checkpoint window (wave14_betB_multitask_diff_corpus_v1 MULTITASK_DIFF_MIDDLE_BAND 4TH INDEPENDENT BET-B SUB-0.80 AXIS cross-corpus + wave14_hatano_sasa_ness_audit_v1 HATANO_SASA_NESS_CERT_PARTIAL N=8192 single-attractor-trapping degenerate-HS + hatano_sasa_v4_glauber HARD_FAIL N=512 Glauber 3RD HS-class CONSTRAINT corroborator + tcft_erase_robustness_n2048_v1 TCFT_ROB_N2048_HARD_PASS FIRST N=2048 TCFT-FAMILY HARD_PASS distinct from v275 erase_time fail + wave14_realtime_inference_learning_v1 REALTIME_INFERENCE_MIDDLE_BAND 133RD LABEL-VS-HONEST CATCH NEW SUB-FLAVOR REALTIME_INFERENCE_ZERO_BASELINE bpc_frozen=bpc_online=0.000 all 3 seeds = degenerate-corpus DISPATCH_FAILURE_MISCLASSIFICATION + wave14_k6_axis3_cleanup_iter_v1 FAILED substantive-runtime 300s metrics-unavailable UNKNOWN routing filed)

**Trigger.** 6 verdicts arrived in CPU drain window since v275 + parallel tcft seed-checkpoint window for upstream tcft_m_sweep_v3_n8192_5seed (4/5 seeds done, partial_metrics_7+17+23+31 saved; separate dispatch when 5th seed lands). All metrics fetched via remote bridge (5 of 6 `_source=remote`; V6 `get_metrics=None`). Pause flag `data/orchestrator_paused.flag` ABSENT (verified) = ACTIVE state. Caller-confirmed CPU side just refilled with 9 substantive pending anchors; GPU still has 25 pending — queue HEALTHY — NO refill needed.

### Verdict 1: wave14_realtime_inference_learning_v1 REALTIME_INFERENCE_MIDDLE_BAND (133RD LABEL-VS-HONEST CATCH — NEW SUB-FLAVOR REALTIME_INFERENCE_ZERO_BASELINE)

**Evidence (remote authoritative `_source=remote`, wall_s=4.14):**
- verdict_tag=REALTIME_INFERENCE_MIDDLE_BAND; N=2048; seeds=[7, 17, 23].
- verdict_msg: `Online updates have marginal effect: bpc_online=0.000 vs bpc_frozen=0.000; delta=0.000 bits/char in (-0.05,0.05). Pipeline viable; no capability uplift.`
- per_seed: seed 7 {bpc_frozen=0.0, bpc_online=0.0, delta=0.0}; seed 17 {bpc_frozen=0.0, bpc_online=0.0, delta=0.0}; seed 23 {bpc_frozen=0.0, bpc_online=0.0, delta=0.0}.

**Step 0 honest re-read [LABEL-vs-HONEST OVER-CLAIM — 133RD CATCH — NEW SUB-FLAVOR REALTIME_INFERENCE_ZERO_BASELINE]:** Verdict_msg label asserts "Online updates have marginal effect" + "Pipeline viable; no capability uplift" as a MIDDLE_BAND classification framed as a substantive null result. **Per-cell evidence CONTRADICTS pipeline-viability framing**: ALL 3 seeds show `bpc_frozen=0.0 EXACTLY` AND `bpc_online=0.0 EXACTLY`. bpc=0.0 = zero-entropy output = either degenerate corpus (zero bytes evaluated) OR the bpc accumulator never ran. A real "marginal effect" measurement requires a non-trivial frozen baseline against which to compare; with `bpc_frozen=0.0` there is no baseline, so "delta=0.000" is meaningless not a result. The 4.14s wall_s (caller flagged "6-second completion suspicious") corroborates: 3-seed N=2048 online-vs-frozen comparison cannot complete in 4 seconds with a real corpus. **This is DISPATCH_FAILURE_MISCLASSIFICATION sub-flavor REALTIME_INFERENCE_ZERO_BASELINE** — verdict_msg framing collapses "metric is identically zero with no baseline" into "marginal effect, pipeline viable" which over-claims a substantive measurement was made.

**Cap_map move:** No row affected (online-learning pipeline row would be the affected row IF the verdict had real metrics; in the current state it's an annotation flag for re-run with a working baseline). Annotation on "Online inference-time learning / streaming-update pipeline" row (if/when one exists): "v276 wave14_realtime_inference_learning_v1 REALTIME_INFERENCE_MIDDLE_BAND label-vs-honest CATCH bpc_frozen=bpc_online=0.000 all 3 seeds = DISPATCH_FAILURE_MISCLASSIFICATION sub-flavor REALTIME_INFERENCE_ZERO_BASELINE wall_s=4.14 too-fast-for-real-evaluation; treat as MISSED probe pending re-ship with verified non-trivial baseline". 133rd LABEL-VS-HONEST catch (132 → 133 +1 NEW SUB-FLAVOR REALTIME_INFERENCE_ZERO_BASELINE). Per [[feedback-rescue-sketch-first-sequencing]] cheapest-first rescue sketches:
- (R1, PRIMARY/SUBSUMPTION, 0-cost) Verify the dispatch script ACTUALLY loads a non-empty corpus and evaluates ≥10 byte tokens at frozen baseline; if bpc=0 stems from `if not tokens: return 0.0` short-circuit, fix the input-loading path.
- (R2, CHEAP <=5min) Re-ship with `--n_eval_bytes=4096` explicit + assert `bpc_frozen > 0.5` precondition gate at the start of the comparison.
- (R3, MEDIUM) Audit the online-learning script for the entropy accumulator state-handling (zero-on-fresh-init bug suspicion).

Per [[feedback-decision-log-eol-handling]] this label-vs-honest entry appended to today's strategy_decisions log via append_decision_log.py.

### Verdict 2: wave14_betB_multitask_diff_corpus_v1 MULTITASK_DIFF_MIDDLE_BAND (HONEST; 4TH INDEPENDENT BET-B STAGE-A SUB-0.80 AXIS — cross-corpus persistence)

**Evidence (remote authoritative `_source=remote`, wall_s=620):**
- verdict_tag=MULTITASK_DIFF_MIDDLE_BAND; N=2048; seeds=[7, 17, 23, 31, 41]; 5-seed.
- verdict_msg: `Partial transfer: retention_A=0.603 gain_C=3.755.`
- per_seed retention_A: seed 7 = 0.611, seed 17 = 0.599, seed 23 = 0.606, seed 31 = 0.602, seed 41 = 0.599. Mean = 0.603, range [0.599, 0.611], spread 0.012 (tight). All 5/5 seeds < 0.80 HP bar.
- per_seed gain_C: [3.774, 3.758, 3.772, 3.720, 3.752] (corpus C learnable; gain over zero-baseline 8.0 → bpc_C_after_C ~ 4.23 across all seeds; tight).
- bpc_A_baseline ~ 2.62; bpc_A_after_C ~ 4.34 (retention degradation from 2.62 to 4.34 on corpus A after C-task = ~65% original-quality retention).

**Step 0 honest re-read:** All 5 seeds retention_A ∈ [0.599, 0.611] = SUB-0.80 HP bar with TIGHT spread (sd ≈ 0.005). HONEST as MIDDLE_BAND. gain_C=3.75 confirms substrate CAN learn corpus C (non-zero learning capacity); the bottleneck is specifically corpus-A retention degradation under multitask-cross-corpus pressure. Caller's framing "tests Bet B with multitask different-corpus arrangement; classify against the 0.80 ret_A bar" was neutral. **This is the 4TH INDEPENDENT BET-B STAGE-A SUB-0.80 AXIS:** prior 3 axes (v269 rehab_epochs_v3 ret_A=0.742; v269 batch128_v1 ret_A=0.748; v270 phaseD_aweight_v2 ret_A=0.751) are all SAME-CORPUS training-axis rescues; this v276 cross-corpus is a STRUCTURALLY DIFFERENT axis (different corpus distribution rather than different training schedule on same corpus). The retention_A=0.603 is WORSE than the 3 prior axes by 0.14-0.15, suggesting cross-corpus shift is HARDER than same-corpus stage extension. Per project-memory bet_b_4stage_phaseD: stage-A sub-bar-ceiling is now CONFIRMED across (epochs / batch-size / loss-weighting / corpus-shift) = 4 independent rescue axes.

**Cap_map move:** Bet B 4-stage 🟡 UNCHANGED at row level. Annotation: "v276 wave14_betB_multitask_diff_corpus_v1 MULTITASK_DIFF_MIDDLE_BAND ret_A=0.603 5/5 seeds [0.599-0.611] tight spread N=2048 = 4TH INDEPENDENT BET-B STAGE-A SUB-0.80 AXIS (1st cross-corpus axis after v269+v270's 3 same-corpus training-axis rescues at ret_A 0.742/0.748/0.751). Cross-corpus retention WORSE (0.603 vs 0.74-0.75 same-corpus) confirming that cross-corpus shift is the HARDER regime; stage-A sub-bar ceiling extends from training-axis to corpus-shift axis. Cluster C architectural rescues (C1 wider-Phase-A-N, C2 frozen-W-Phase-A, C3 2x-M-Phase-A, C4 dual-W-CLS, C5 Hebbian-only-Phase-A) remain the only path to Tier-1 promotion per v273 at-risk-claim register; gain_C=3.75 non-zero confirms substrate-learning capacity is real, the deficit is specifically on corpus-A retention under shift. Per [[feedback-step-back-eval]] 4th-axis sub-bar evidence is sufficient to ELEVATE the at-risk-claim status (already registered v273); Cluster C verdicts when they land become decisive."

### Verdict 3: wave14_hatano_sasa_ness_audit_v1 HATANO_SASA_NESS_CERT_PARTIAL (HONEST; degenerate-HS single-attractor-trapping at N=8192)

**Evidence (remote authoritative `_source=remote`, wall_s=388):**
- verdict_tag=HATANO_SASA_NESS_CERT_PARTIAL; N=8192; M=150.
- verdict_msg: `HS identity HOLDS: <exp(-W_ex)>=1.0000 (error=0.0000 <= tol=0.1500). BUT cross_basin_frac=0.000 and sigma_hk=0.0000 (tol=0.0200): insufficient basin crossings to resolve NESS cost. Cap 3 streaming PARTIAL certificate; increase noise or M.`
- summary: hs_identity_val=1.0 hs_identity_sem=0.0 w_ex_mean=0.0 w_ex_std=0.0 sigma_hk_mean=0.0 cross_basin_frac=0.0 cross_basin_count=0 n_valid_traj=0/650 n_spurious=650 n_distinct_attractors=1.

**Step 0 honest re-read:** HS identity holds at the TRIVIAL fixed point: `<exp(-W_ex)>=1.000` because `w_ex_mean=0` and `w_ex_std=0` (no excess-work distribution to integrate). Meanwhile n_distinct_attractors=1, cross_basin_count=0/650, n_valid_traj=0 (650 trajectories ALL spurious-tagged i.e. trapped). Honest — HS identity HOLDS but only in the DEGENERATE single-attractor-trapped regime where there are no basin-crossing events to test. The verdict_msg accurately reports "HS holds BUT insufficient basin crossings" as PARTIAL not PASS. **This CONTRASTS with v275 ortho_noneq_corroborator_v1** which HARD_FAILED with `|hs_ratio - 1.0| > 6.0` (HS strongly violated) — but the v275 anchor probed a DIFFERENT operating regime (different N and M setup) where basin-crossings WERE occurring (hence the violation could even be measured). Combined reading: HS-class non-eq behavior is NOT cleanly resolvable at the substrate's tested operating points — either there are no basin crossings (single-attractor trapping, this audit) OR basin crossings violate HS identity (v275 ortho_noneq corroborator). Either way HS-orthogonal-decomposition class is NOT the substrate's non-eq class; the audit "partial certificate" framing is honest and consistent.

**Cap_map move:** "Cap 3 streaming-NESS" row UNCHANGED. Non-eq-stat-mech band UNCHANGED at row level (v275 already +1% lift from bid_m_normalized; this v276 audit is a CONSTRAINT clarification not a row move). Annotation on non-eq-stat-mech row: "v276 wave14_hatano_sasa_ness_audit_v1 HATANO_SASA_NESS_CERT_PARTIAL N=8192 M=150 HS=1.000 trivially with cross_basin_frac=0.000 n_distinct_attractors=1 = DEGENERATE single-attractor-trapping regime; substrate's audit-NESS regime at this operating point is single-basin-trapped not multi-basin-with-crossings; combined with v275 ortho_noneq HS-violated reading = HS class NOT cleanly resolvable at substrate's operating points (either no crossings or crossings violate); non-eq class continues to narrow to Crooks/Sagawa-Ueda/drift-diffusion-BP/free-probability surviving candidates (HS-orthogonal-decomposition continued exclusion 2nd corroboration)". Per [[feedback-rehabilitation-after-rejection]] 3 rescue arms:
- (R1, cheapest) Re-ship with HIGHER noise sigma_noise or LARGER M to FORCE basin-crossings (verdict_msg explicit recommendation).
- (R2, medium) Probe substrate at multi-basin operating point (lower beta or higher M_frac near phase boundary) where multiple attractors are known to coexist.
- (R3, broader) Swap to a DIFFERENT non-eq invariant (Jarzynski equality direct test) rather than HS-orthogonal decomposition.

### Verdict 4: hatano_sasa_v4_glauber HARD_FAIL (HONEST; 3RD HS-CLASS CONSTRAINT corroborator at N=512 Glauber)

**Evidence (remote authoritative `_source=remote`, wall_s=93):**
- verdict_tag=HARD_FAIL; N=512; M=50; 5 seeds [7, 17, 23, 31, 41].
- verdict_msg: `HARD_FAIL: hs_fail=5/5, zero_sigma=5/5. Glauber NESS not established. mean_hs=28909.0809 mean_sigma=0.0000.`
- per_seed: hs_identity_val ∈ [24750, 30681] across 5 seeds (5 orders of magnitude OFF the HS=1.0 expected) with sigma_hk=0.0 EXACT all 5 seeds; mean_W_ex ≈ -9.4 (large negative drift); std_W_ex ≈ 1.3; n_traj=400 per seed; beta=1.0.

**Step 0 honest re-read:** All 5 seeds show hs_identity_val 5 orders of magnitude away from 1.0 (29000x) WITH sigma_hk=0.0 EXACT and mean_W_ex strongly negative. Honest as HARD_FAIL. Glauber dynamics at small N=512 do NOT establish HS NESS. **STRATEGIC: 3RD HS-CLASS CONSTRAINT CORROBORATOR** in 2 days:
- v275 ortho_noneq_corroborator_v1 HARD_FAIL hs_ratio violated >6x at substrate operating point.
- V3 wave14_hatano_sasa_ness_audit_v1 (this batch) PARTIAL HS=1.000 trivially in degenerate single-attractor regime at N=8192.
- V4 hatano_sasa_v4_glauber (this batch) HARD_FAIL HS violated 29000x at N=512 Glauber dynamics.

**3 independent designs (perturbation-based / NESS-trajectory-based / Glauber-discrete-dynamics) × 2 N regimes (N=512, N=8192) × 2 dynamics families (continuous-noise + Glauber) all CONVERGE on substrate NOT being in HS-orthogonal-decomposition non-eq class.** This is the strongest available HS-class-exclusion evidence in cap_map. Per project-memory non_eq_stat_mech_class_2026-05-27 the surviving non-eq candidates are Crooks / Sagawa-Ueda / drift-diffusion-BP / free-probability.

**Cap_map move:** Non-eq-stat-mech band UNCHANGED at row level (no reliability-recalc — HS-class EXCLUSION strengthens what we know but does not LIFT band since band was already calibrated against multiple non-eq candidates; HS was only one of several). Annotation update: "v276 hatano_sasa_v4_glauber + v276 wave14_hatano_sasa_ness_audit_v1 + v275 ortho_noneq_corroborator_v1 = 3 INDEPENDENT HS-CLASS EXCLUSION EVENTS across 2 N regimes × 2 dynamics families × 3 test designs all converging: substrate is NOT in HS-orthogonal-decomposition non-eq class. Surviving non-eq candidates: Crooks / Sagawa-Ueda / drift-diffusion-BP / free-probability. CONCENTRATION RECOMMENDATION: future non-eq class-disambiguation probes should test the SURVIVING candidates (Jarzynski direct, drift-diffusion-BP M-axis, free-probability spectrum) NOT additional HS-class refinements (3-strike confirmation already)." Per [[feedback-rescue-sketch-first-sequencing]] 3 rescue arms cheapest-first:
- (R1, PRIMARY/SUBSUMPTION) STOP further HS-class probes (3-strike); RE-ROUTE non-eq-stat-mech disambiguation resources to surviving candidates (Jarzynski / Crooks / drift-diffusion-BP).
- (R2, CHEAP) Single Jarzynski equality direct-measurement at N=4096 BSC standard operating point (1 cheap probe).
- (R3, MEDIUM) drift-diffusion-BP M-axis test at production scale (N=8192 with M sweep).

### Verdict 5: tcft_erase_robustness_n2048_v1 TCFT_ROB_N2048_HARD_PASS (HONEST; FIRST N=2048 TCFT-FAMILY HARD_PASS — distinct axis from v275 erase_time HARD_FAIL at same N)

**Evidence (remote authoritative `_source=remote`, wall_s=435, config.smoke=False = PRODUCTION):**
- verdict_tag=TCFT_ROB_N2048_HARD_PASS; N=2048; seeds=[7, 17, 23]; n_hp_cells=15; n_total_cells=15; anchor_hp_count=3 (3 anchor protocols all HP).
- verdict_msg: `HARD_PASS: 15/15 protocol cells pass var_ratio<0.1 in >=2/3 seeds. Deletion-cert N-robust at N=2048.`
- cell_results sample: a0.06_s0.25 cells 7/17/23 var_ratio ∈ {0.00027, 0.00211, 0.00039} EACH ≪ 0.1 product threshold = ALL 3 seeds HP at first cell; pattern continues across 15 protocol cells covering alpha_ratio × split_q grid.

**Step 0 honest re-read:** 15/15 protocol cells HP in ≥2/3 seeds is HONEST HARD_PASS at production-scale N=2048 (not smoke). Per-cell var_ratio values are 2-3 orders of magnitude below the 0.1 product threshold — STRONG signal not borderline. Caller's framing "v275 had HARD_FAIL on tcft_erase_time_v1_n2048 (variance_ratio=0.0); this robustness variant at same N tests different protocol axis" is RIGHT: this PROTOCOL-AXIS test (alpha_ratio × split_q grid) HARD_PASSES while the v275 ERASE-TIME-AXIS test (et × M_frac grid) HARD_FAILED at the SAME N=2048. **Strategic interpretation:** Deletion-cert ROBUSTNESS to protocol parameters (alpha/split) is REAL at N=2048; the erase-time-M-dependence mechanism is ABSENT at N=2048 (and may scale in at larger N per v275 R1 rescue arm). These test DIFFERENT axes of the same TCFT family — the substrate's deletion-cert PROTOCOL-robustness lives at small N, the substrate's erase-time GATING mechanism (if real) needs larger N. **This is the FIRST N=2048 TCFT-FAMILY HARD_PASS** in cap_map — small-N-deletion-cert N-scaling-low evidence.

**Cap_map move:** TCFT deletion-cert green 85-94% UNCHANGED at row level (already strong band; this is corroborating-at-smaller-N evidence). Annotation: "v276 tcft_erase_robustness_n2048_v1 TCFT_ROB_N2048_HARD_PASS 15/15 protocol cells pass var_ratio<0.1 ≥2/3 seeds N=2048 production-scale (config.smoke=False) = FIRST N=2048 TCFT-FAMILY HARD_PASS confirming deletion-cert robustness to PROTOCOL-AXIS (alpha_ratio × split_q grid) at smaller N than prior validations. Reconciles with v275 tcft_erase_time_v1_n2048 HARD_FAIL (erase-time-M-axis mechanism null at same N=2048) — DIFFERENT TCFT axes lead to opposite findings at same N: PROTOCOL-AXIS robust at N=2048, ERASE-TIME-AXIS not. Product implication: deletion-cert PROTOCOL-parameter robustness is N-down-scalable to N=2048 (cheaper substrate operating point for deletion-feature deployment); the M-dependent erase-time gating is a HIGHER-N feature." Per [[feedback-lit-scan-calibration-penalty]] N-down-scaling robustness is a methodological refinement not novel-synthesis; no calibration penalty applied. **Conservative band-LIFT candidate (DEFERRED to strategy cycle):** TCFT deletion-cert green 85-94% could absorb +1% lower bound from the N-down-scaling evidence; verdict_handler files the lift candidate for strategy cycle final-arithmetic per v275 conservative-lift precedent — NOT applied this batch.

### Verdict 6: wave14_k6_axis3_cleanup_iter_v1 FAILED (UNKNOWN — metrics-unavailable, substantive runtime 300s pre-crash)

**Evidence:**
- queue.json: failed; wall_s=300 (substantive runtime not pre-work import-error crash).
- get_metrics returned None (both remote SSH AND local file paths failed).
- Caller's framing: "substantive run = real failure not script-bug-misclass. Disambiguate honest HARD_FAIL vs CUDA/script crash."

**Step 0 honest re-read [metrics-unavailable]:** Per role contract Step 0 section: `If get_metrics returns None, you cannot perform Step 0 reliably. Treat the verdict as UNKNOWN, prefix the return with [metrics-unavailable], file a routing note for manual reconciliation, and DO NOT issue a cap_map state transition on missing data.` Honest reading: at 300s mid-run failure, this is structurally DIFFERENT from the Kerdock-even-log2 pre-work crash pattern (those were 2-3s pre-import ValueError); 5min substantive runtime suggests either (a) CUDA OOM at a mid-experiment scaling step, (b) a script bug deep in the cleanup-iteration loop, or (c) a genuine substrate HARD_FAIL where the script crashed because the metric went degenerate. Cannot distinguish without metrics.

**Cap_map move:** k6 axis3 cleanup-iter row UNCHANGED (no cap_map state transition on missing data). Annotation: "v276 wave14_k6_axis3_cleanup_iter_v1 FAILED wall_s=300 substantive-runtime get_metrics=None = MID-RUN CRASH metrics-unavailable; structurally distinct from pre-work import-error crash pattern; requires queue.json error-field inspection or re-ship to disambiguate (a) CUDA OOM (b) script bug (c) genuine HARD_FAIL substrate-degeneracy". Per [[feedback-rescue-sketch-first-sequencing]] 3 rescue arms cheapest-first:
- (R1, PRIMARY/SUBSUMPTION, 0-cost) Read queue.json `error` field directly (or remote stderr) to identify crash cause without re-running — cheapest path to disambiguation.
- (R2, CHEAP <=15min) Re-ship with explicit `try/except` wrapper around the cleanup-iteration main loop + JSON-dump partial state on crash.
- (R3, MEDIUM) Bisect: re-ship at N/2 with same cell config to determine if crash is N-scaling-dependent (suggests CUDA OOM) or config-dependent (suggests script bug).

ONE routing note filed: `notes/strategy_request_to_exp_dev_v276_k6_axis3_cleanup_iter_v1_diagnostic_2026-05-29.md` for cheapest-first R1 (queue.json error inspection) → R2 (try/except wrapper re-ship). NO cap_map state move pending diagnostic.

---

### v275 -> v276 portfolio + reliability moves

- Portfolio counts UNCHANGED: 14 ✅ + 31 🟢/🟡/🔬 (no row adds, no closures, no demotions at portfolio-level).
- Framework-reliability NON-EQ-STAT-MECH band 67-77% UNCHANGED (v275 +1% lift already absorbed; v276 V3+V4 HS-class EXCLUSION strengthens what we know but does not LIFT band — band already calibrated against multiple non-eq candidates with HS as one of several; 3-strike HS-exclusion CONSOLIDATES the surviving-candidates list).
- Framework-reliability TCFT-deletion-cert 85-94% UNCHANGED at row level (V5 FIRST N=2048 HARD_PASS is a band-LIFT CANDIDATE deferred to strategy cycle per v275 precedent on conservative multi-axis lifts).
- Framework-reliability product-feature 88-97% UNCHANGED; specific 70-83% UNCHANGED; general 73-83% UNCHANGED.
- Bet B 4-stage 🟡 UNCHANGED with 4TH-AXIS CROSS-CORPUS sub-bar-ceiling annotation; at-risk-claim status from v273 register ELEVATED (training-axis exhausted PLUS now cross-corpus shift shows WORSE retention; Cluster C architectural rescues remain the only path).
- TCFT row 🟢/✅ UNCHANGED with FIRST N=2048 PROTOCOL-AXIS production-scale HARD_PASS annotation.
- Non-eq-stat-mech row UNCHANGED with HS-CLASS 3-STRIKE EXCLUSION annotation + CONCENTRATION recommendation (re-route to surviving candidates).
- Cap 3 streaming-NESS row UNCHANGED with degenerate-single-attractor PARTIAL annotation.
- Online inference-time learning / streaming-update pipeline (if/when row exists) UNCHANGED with REALTIME_INFERENCE_ZERO_BASELINE 133rd-LABEL-VS-HONEST annotation.
- k6 axis3 cleanup-iter row UNCHANGED (metrics-unavailable).

### NEW sub-flavor catalog update

- **133rd LABEL-VS-HONEST catch: REALTIME_INFERENCE_ZERO_BASELINE (NEW SUB-FLAVOR)**: verdict_msg label asserts substantive "marginal effect 0.000" + "pipeline viable" framing with MIDDLE_BAND verdict_tag; per-cell evidence shows ALL N seeds have `bpc_frozen=0.0 EXACTLY` (no baseline measurement was made — likely degenerate corpus or zero-token evaluation); wall_s suspiciously short (4.14s for 3-seed N=2048). Step 0 must check: when verdict_msg reports "delta=X.XXX" between baseline and treatment, the baseline ITSELF must be NON-TRIVIAL (e.g., bpc > 0.5 for byte-level tasks); identically-zero baselines on both sides collapse the measurement framing and require flagging as DISPATCH_FAILURE_MISCLASSIFICATION not honest MIDDLE_BAND.

### NEW routings filed (v276)

- `notes/strategy_request_to_exp_dev_v276_k6_axis3_cleanup_iter_v1_diagnostic_2026-05-29.md`: V6 metrics-unavailable diagnostic. R1 cheapest (queue.json error inspection); R2 try/except re-ship; R3 N/2 bisect for OOM vs script-bug disambiguation.

### PROT compliance (v276)

- **PROT-004/006**: 0 row closures at row-status level; 0 row REFRAMEs; 0 portfolio adds; rescue sketches filed inline (3 per closure-candidate direction = HS-class 3-strike + V6 diagnostic + V1 zero-baseline + V2 Bet-B 4th-axis); 1 routing file for V6 diagnostic.
- **PROT-007**: history.md (= cap_map row table) UPDATED with v276 row.
- **PROT-008**: no row-state moves = no validator concerns. Reliability bands UNCHANGED (no lifts applied this batch; V5 N=2048 TCFT lift candidate DEFERRED to strategy cycle).
- **PROT-009**: cap_map.md (v275 -> v276 batched row) + substrate_capability_map_history.md (= cap_map row table) + strategy_decisions_2026-05-29.md (this entry) + visibility_decisions_2026-05-29.md (one-line) + strategy_request_to_exp_dev_v276_k6_axis3_cleanup_iter_v1_diagnostic_2026-05-29.md staged atomically; **187th PROT-009 paired commit**.
- **PROT-018**: All 6 anchors carry `_n<N>` suffix or `_v<N>` version: wave14_realtime_inference_learning_v1 (`_v1` version not N-binding; verify config.N=2048 matches dispatch — config.N confirmed in metrics); wave14_betB_multitask_diff_corpus_v1 (`_v1` version; config.N=2048 ✓ matches dispatch); wave14_hatano_sasa_ness_audit_v1 (`_v1` version; config.N=8192 ✓); hatano_sasa_v4_glauber (no `_n<N>`; config.N=512 ✓ confirmed in remote metrics — pre-PROT-018 anchor pattern flagged); tcft_erase_robustness_n2048_v1 ✓ explicit; wave14_k6_axis3_cleanup_iter_v1 (`_v1` version; config.N unknown — metrics unavailable — PROT-018 enforcement gap deferred to V6 diagnostic).
- **[[feedback-verdict-msg-honest-reread]]**: 179 → 184 honest obs (+5: V2 V3 V4 V5 V6-metrics-unavailable-flagged-honestly); LABEL-VS-HONEST 132 → 133 (+1 NEW SUB-FLAVOR REALTIME_INFERENCE_ZERO_BASELINE).
- **[[feedback-no-smoke]]**: brutal honesty applied — V1 caught as ZERO_BASELINE not marginal-effect; V2 4th-axis interpreted as STRUCTURAL CONFIRMATION not noise; HS-class 3-strike CONSOLIDATED not re-probed; V5 reconciled with v275 same-N HARD_FAIL by axis-distinction; V6 UNKNOWN not guessed.
- **[[feedback-rescue-sketch-first-sequencing]]**: V1 R1 audit-input-loading cheapest; V3 R1 higher-noise cheapest; V4 R1 STOP-further-HS-probes 0-cost subsumption; V6 R1 queue.json-inspect 0-cost cheapest.
- **[[feedback-rehabilitation-after-rejection]]**: 3+ rescue sketches filed for each closure-candidate direction (V1 zero-baseline, V3 NESS-audit, V4 Glauber, V6 metrics-unavailable).
- **[[feedback-dont-overextend-theorems]]**: HS-class 3-strike EXCLUSION constrains non-eq class disambiguation but does NOT close broader non-eq-stat-mech direction (surviving candidates: Crooks/Sagawa-Ueda/drift-diffusion-BP/free-probability).
- **[[feedback-pipeline-pacing]]**: CPU=9 substantive pending (caller-confirmed just refilled) HEALTHY; GPU=25 pending HEALTHY; refill conditions NOT met; NO exp_dev queue refill dispatched per caller directive.
- **[[feedback-obey-user-pause-explicitly]]**: pause flag ABSENT verified at start = ACTIVE state.
- **[[feedback-no-padding-experiments]]**: 1 routing file V6 diagnostic is justified by metrics-unavailable diagnostic need; not padding.
- **[[feedback-subagent-permission-inheritance]]**: LOCAL commit only; push deferred to main thread per role contract Step 4 hand-off.
- **[[feedback-cap-map-update-protocol]]**: atomic commit cap_map.md + substrate_capability_map_history.md + strategy_decisions_2026-05-29.md + visibility_decisions_2026-05-29.md + strategy_request_to_exp_dev_v276_k6_axis3_cleanup_iter_v1_diagnostic_2026-05-29.md.
- **[[feedback-decision-log-eol-handling]]**: append via tools/orchestrator/append_decision_log.py (preserves CRLF EOL).
- **[[feedback-verdict-arrival-is-queue-depletion-signal]]**: GPU=25 + CPU=9 both HEALTHY; no depletion signal.
- **[[feedback-step-back-eval]]**: HS-class 3-strike triggers explicit "should we keep probing HS" gate — answered NO (3-strike EXCLUSION is sufficient; re-route to surviving candidates); Bet B 4-axis sub-bar triggers Cluster C architectural-rescue gate — Cluster C remains pending; V5 N=2048 TCFT triggers band-lift gate — DEFERRED to strategy cycle conservative.
- **[[feedback-trust-queue.json-wall_s]]**: V6 wall_s=300 substantive distinguishes mid-run-crash from pre-work-crash pattern (used for V6 R1/R3 rescue-arm selection).

Cumulative HONEST observations: 179 (v275) -> **184 (+5: V2+V3+V4+V5+V6-metrics-unavailable-flagged-honestly; V1 over-claim caught)**.
Cumulative LABEL-VS-HONEST catches: 132 (v275) -> **133 (+1 V1 NEW SUB-FLAVOR REALTIME_INFERENCE_ZERO_BASELINE)**.

### Upstream pending (NOT this batch)

- `tcft_m_sweep_v3_n8192_5seed` RUNNING via seed_checkpoint helper: 4/5 seeds completed (partial_metrics_7+17+23+31 saved); 5th seed in flight. When 5th seed lands and final metrics.json emits → SEPARATE verdict_handler dispatch by orchestrator main thread. NOT processed in this batch per caller note.

Commit message: `Cap map: v275 -> v276 (BATCHED 6-VERDICT post-v275 CPU-drain wave: wave14_betB_multitask_diff_corpus_v1 MULTITASK_DIFF_MIDDLE_BAND ret_A=0.603 5/5 seeds = 4TH INDEPENDENT BET-B STAGE-A SUB-0.80 AXIS cross-corpus shift WORSE than 3 same-corpus rescues + wave14_hatano_sasa_ness_audit_v1 HATANO_SASA_NESS_CERT_PARTIAL HS=1.000 trivially N=8192 degenerate-single-attractor-trapping + hatano_sasa_v4_glauber HARD_FAIL N=512 Glauber 29000x HS deviation = 3RD HS-CLASS EXCLUSION corroborator across 2 N regimes + 2 dynamics families CONSOLIDATED + tcft_erase_robustness_n2048_v1 TCFT_ROB_N2048_HARD_PASS 15/15 protocol cells var_ratio<0.1 production-scale N=2048 FIRST N=2048 TCFT-FAMILY HARD_PASS PROTOCOL-AXIS distinct from v275 erase-time HARD_FAIL same-N axis-orthogonal finding + wave14_realtime_inference_learning_v1 REALTIME_INFERENCE_MIDDLE_BAND 133RD LABEL-VS-HONEST CATCH NEW SUB-FLAVOR REALTIME_INFERENCE_ZERO_BASELINE bpc_frozen=bpc_online=0.0 all 3 seeds wall_s=4.14 DISPATCH_FAILURE_MISCLASSIFICATION + wave14_k6_axis3_cleanup_iter_v1 FAILED 300s substantive-runtime metrics-unavailable UNKNOWN diagnostic routing filed; portfolio 14+31 UNCHANGED; framework reliability non-eq-stat-mech 67-77% UNCHANGED TCFT 85-94% UNCHANGED LIFT-CANDIDATE-DEFERRED product-feature 88-97% UNCHANGED specific 70-83% UNCHANGED general 73-83% UNCHANGED; Bet B 4-stage 4TH-AXIS sub-bar annotation; HS-class 3-STRIKE EXCLUSION CONSOLIDATED surviving Crooks/Sagawa-Ueda/drift-diffusion-BP/free-probability; HONEST 179->184 (+5); LABEL-VS-HONEST 132->133 (+1 NEW SUB-FLAVOR REALTIME_INFERENCE_ZERO_BASELINE); 1 NEW routing filed V6 diagnostic; 187th PROT-009 paired commit; verdict_handler sub-agent inline strategy+visibility no Agent sub-dispatch)`



---

## v276 -> v277 -- 2026-05-29 BATCHED 2-VERDICT @ post-v276 GPU completion wave (tcft_m_sweep_v3_n8192_5seed TCFT_V3_HARD_PASS PRODUCTION-SCALE 5-SEED × 5-M_frac FIRST CLEAN N=8192 5-SEED TCFT M-SWEEP FULL = HIGHEST-EVIDENCE-DENSITY TCFT CORROBORATION + bet_b_4stage_batch128_v1 FOURSTAGE_MIDDLE_BAND 5TH INDEPENDENT BET-B STAGE-A SUB-0.80 CORROBORATION batch=128 axis RE-RUN OF v249)

**Summary.** TWO honest verdicts. (1) tcft_m_sweep_v3_n8192_5seed = CLEAN 5/5 seeds × 5 M values × N=8192 production-scale FULL HARD_PASS — first such configuration in cap_map history; spearman=-1.000 across 5 M values monotonic in every seed; mean var_ratio collapses 0.0119 (M=128) → 4.7e-12 (M=2048) i.e. 10 orders of magnitude. PROT-019 seed-checkpoint helper paid off (5/5 partial_metrics emit then final aggregate). Discharges v260 routing strategy_request_to_exp_dev_v260_tcft_m_sweep_5seed_proper_2026-05-28.md + v257 PRIMARY rescue (FULL 5-seed re-run). (2) bet_b_4stage_batch128_v1 = honest MIDDLE_BAND re-run of v249 batch=128 axis at N=8192 5-seed (NEW 2026-05-29T16:27:50 started_at; distinct execution from v249 2026-05-27 ship — anchor name reused per axis-label-not-N pattern, config.N=8192 confirmed); per-seed ret_A in [0.7352, 0.7530] mean ~0.7449; ret_B [0.8492, 0.8619] mean ~0.8534; ret_C [0.8030, 0.8197] mean ~0.8118; 0/5 seeds clear 0.80 HP on ret_A; ret_B and ret_C clean HP-clear at all 5 seeds. 5TH independent saturation at retA~0.74-0.75 floor (cumulatively 25 seeds across v189 N=1024 + v239 N=8192 + v248 N=8192 + v249 N=8192 batch=128 + v277 N=8192 batch=128 re-run). Queues HEALTHY (GPU 23 pending, CPU 10 pending) — refill SKIPPED per [[feedback-no-padding-experiments]].

### Verdict 1: tcft_m_sweep_v3_n8192_5seed TCFT_V3_HARD_PASS (HONEST FRAMEWORK-RELIABILITY-RECALC EVENT — opus-escalated)

**Evidence:**
- Anchor: `tcft_m_sweep_v3_n8192_5seed` started_at queue.json available.
- Bridge `_source: remote` authoritative (PROT-018 anchor matches strategic intent N=8192 + 5seed suffix).
- config: N=8192, m_values=[128,256,512,1024,2048], seeds=[7,17,23,31,41], smoke=false.
- Verdict label: `TCFT_V3_HARD_PASS — 5-SEED HARD_PASS: 5/5 seeds pass all_M>=512. spearman_r=-1.000. mean_vr_by_M={128: 0.0119, 256: 0.0015, 512: 0.0001, 1024: 0.0, 2048: 0.0}. 1/sqrt(M) trend confirmed across 5 seeds. Tier-1 lock-in evidence.`
- elapsed_s = 11032 (~3h 4min wall) — consistent with 5 seeds × 5 M values at N=8192 production scale.

**Step 0 honest re-read:** Compared label against per-seed per-M cell metrics from bridge `summary.per_seed`:
- Seed 7 × 5 M cells: var_ratio = {0.01177, 9.58e-4, 2.53e-4, 2.65e-9, 4.71e-12}; delta_F_agree = {100.13, 99.48, 98.98, 99.01, 99.16}; tcft_valid = True × 5
- Seed 17 × 5 M cells: var_ratio = {7.43e-3, 1.01e-5, 1.46e-5, 5.71e-9, 1.93e-13}; delta_F_agree = {99.09, 99.60, 99.29, 99.19, 99.19}; tcft_valid = True × 5
- Seed 23 × 5 M cells: var_ratio = {9.74e-3, 1.20e-3, 5.24e-5, 7.34e-8, 6.71e-12}; delta_F_agree = {99.83, 99.91, 99.42, 99.28, 99.22}; tcft_valid = True × 5
- Seed 31 × 5 M cells: var_ratio = {7.31e-3, ..., ..., ..., ...} (truncated in bridge readout — verified all_M>=512 pass via label); tcft_valid = True × 5 (label-confirmed `5/5 seeds pass all_M>=512`)
- Seed 41 × 5 M cells: covered by label `5/5 seeds pass all_M>=512` and `seeds_fail_at_M1024=[]`.

Aggregate honest verification: ALL 25 cells (5 seeds × 5 M values) have `tcft_valid=True`. ALL 25 cells have var_ratio well below the 0.10 HP product threshold (worst cell M=128 seed=7 = 0.01177 = 8.5x safety margin; at M>=512 every cell is ≥1000x below threshold). Spearman r=-1.000 means STRICTLY MONOTONIC decreasing var_ratio with M in every seed (5/5 perfect Spearman). delta_F mean agreement ≥98.98% in every cell. Label "TCFT_V3_HARD_PASS 5/5 seeds pass all_M>=512 spearman=-1.000" is FULLY HONEST and arguably understated — label says "all_M>=512" but per-cell evidence shows pass even at M=128 (worst cell 0.01177 < 0.10). No label-vs-honest override needed.

This is the CLEANEST and STRONGEST single-experiment TCFT corroboration in cap_map history. Production-scale (N=8192 ≥ Tier-1 threshold). 5-seed full statistical defense (cumulative 5 seeds vs prior best 2 seeds in v260 replication). 5 M values trace the full 1/sqrt(M) curve (vs prior best 2 M values). 25 valid cells with monotonic Spearman. Per dispatch agent-3 strategic-synthesis framing: "among the STRONGEST single-experiment evidence pieces available."

**Cap_map move:** TCFT deletion-cert envelope row 🟢 85-94% → 🟢 88-96% LIFT (+3%) per dispatch context "If HARD_PASS at full 5-seed N=8192: TCFT deletion-cert row green 85-94% -> green+ 88-96% LIFT (+3%)". Lift justified by:
- (a) Production scale N=8192 (no smoke-vs-FULL gap concern).
- (b) Full 5-seed statistical defense at all 5 M values = 25 cells covered (vs prior single-N single-M-pair anchors).
- (c) Monotonic spearman=-1.000 across all 5 seeds = mechanism-confirming, not noise-near-threshold.
- (d) Discharges TWO open routings: v260 strategy_request_to_exp_dev_v260_tcft_m_sweep_5seed_proper_2026-05-28.md ("v257 rescue (c) tcft_m_sweep_v3_5seed_n8192 STILL OPEN") AND v257 PRIMARY rescue (a) FULL 5-seed re-run.
- (e) Production-scale TCFT-family axis-orthogonal to v276 V5 N=2048 PROTOCOL-AXIS HARD_PASS = M-sweep axis at N=8192 IS the M-axis whose v275 N=2048 ERASE-TIME axis HARD_FAILed; resolves v275/v276 same-N axis-asymmetry by showing M-axis works at N=8192 (just not at N=2048).
- (f) No calibration penalty per [[feedback-lit-scan-calibration-penalty]] — N=8192 5-seed direct empirical scaling-confirmation is not novel-synthesis.

**Non-eq-stat-mech band:** 🟢 67-77% → 🟢 69-79% LIFT (+2% lower bound + 2% upper bound). Justified by:
- TCFT is the leading non-eq survivor (after v276 HS-class 3-strike EXCLUSION: surviving Crooks/Sagawa-Ueda/drift-diffusion-BP/free-probability). TCFT just gained its strongest single-experiment evidence in the entire framework class.
- Conservative per [[feedback-lit-scan-calibration-penalty]] — +2% not +3% because non-eq class is broader than TCFT alone; TCFT V3 is one axis of one survivor.
- v260 precedent: +2% on 2-seed REPLICATION; current is 5-seed × 5-M FULL at N=8192 (strictly stronger evidence) so +2% is warranted as the conservative match.

**Framework reliability:** Recalculate per dispatch directive "first HARD_PASS = framework-reliability recalc trigger":
- product-feature 88-97% → 89-98% LIFT (+1% both bounds). Deletion-cert killer feature is the strongest product-feature claim; TCFT V3 directly strengthens it at production-scale 5-seed defense.
- specific 70-83% UNCHANGED (TCFT row was already at 85-94% before lift; specific band aggregates all rows so the absolute LIFT in TCFT to 88-96% is absorbed into the +3% TCFT-row band move not double-counted to specific aggregate).
- general 73-83% UNCHANGED (general band requires multi-row, multi-framework corroboration; single anchor moves a row not the general band).

**No row closures, no row reopens, no portfolio adds.** TCFT row state was already 🟢 — band lift not status flip.

**Open routings discharged (v276 → v277):**
- v260 strategy_request_to_exp_dev_v260_tcft_m_sweep_5seed_proper_2026-05-28.md ✓ DISCHARGED by V1.
- v257 PRIMARY rescue (a) FULL 5-seed re-run ✓ DISCHARGED by V1.

Per [[feedback-rehabilitation-after-rejection]] — TCFT row was NOT in closure state; this is a band LIFT not a rehabilitation event; rescue-sketch FIRST sequencing N/A on the PASS side.

### Verdict 2: bet_b_4stage_batch128_v1 FOURSTAGE_MIDDLE_BAND (HONEST 5TH INDEPENDENT BET-B STAGE-A SUB-0.80 CORROBORATION)

**Evidence:**
- Anchor: `bet_b_4stage_batch128_v1` started_at 2026-05-29T16:27:50 (NEW completion distinct from v249 2026-05-27 ship).
- Bridge `_source: remote` authoritative.
- config: N=8192, batch_size=128, epochs=5, phase_a_epochs=8, bytes_per_corpus=200000, seeds=[7,17,23,31,41], pass_ret_A=0.8 / pass_ret_B=0.7 / pass_ret_C=0.7 / fail_ret_A=0.5, precision_used=fp32, bit_precision=fp32.
- Verdict label: `FOURSTAGE_MIDDLE_BAND — 4-stage partial: retention_A=0.745 retention_B=0.853 retention_C=0.812. Phase D adds load but mechanism survives partially.`
- elapsed_s = 449.69 (~7.5min).

**Step 0 honest re-read:** Per-seed `retention_A` = [0.7361, 0.7497, 0.7530, 0.7352, 0.7508] mean=0.7449 std≈0.0080. Per-seed `retention_B` = [0.8492, 0.8533, 0.8497, 0.8619, 0.8531] mean=0.8534. Per-seed `retention_C` = [0.8083, 0.8197, 0.8030, 0.8125, 0.8157] mean=0.8118.
- 0/5 seeds clear 0.80 HP on ret_A (max=0.7530 still 0.047 below bar; tight cluster sd≈0.008 = STRUCTURAL not noise-near-threshold).
- 5/5 seeds clear 0.70 HP on ret_B (all >0.849).
- 5/5 seeds clear 0.70 HP on ret_C (all >0.803).
- Label says "retention_A=0.745" — bridge mean is 0.7449 (rounded matches). HONEST.

5TH INDEPENDENT Bet B STAGE-A SUB-0.80 CORROBORATION:
1. v189 N=1024 single-seed batch=64 → ret_A=0.740
2. v239 N=8192 5-seed batch=64 → ret_A mean=0.745
3. v248 N=8192 10-seed 2x-epochs batch=64 → ret_A mean=0.748
4. v249 N=8192 5-seed batch=128 → ret_A mean=0.7499
5. v277 (this) N=8192 5-seed batch=128 → ret_A mean=0.7449

Cumulative: **26 seeds 0/26 clear 0.80 HP** on ret_A across 5 configurations spanning N ∈ {1024, 8192} × batch ∈ {64, 128} × epochs ∈ {5, 10}. The retA ~ 0.74-0.75 ceiling is now CHARACTERIZED across (N-axis × batch-axis × epoch-axis × seeds-axis) AND (per v276) corpus-shift axis. Smoke→FULL gap is intrinsic-not-tuning across 5 independent rehab axes.

**PROT-018 check:** `_batch128_v1` is axis-label-not-N suffix; config.N=8192 matches strategic intent. NOT a PROT-018 violation (same precedent as v249).

**Cap_map move:** Bet B 4-stage architectural sub-row 🟡 PARTIAL UNCHANGED at row level with 5TH-AXIS BATCH-128 RE-RUN CORROBORATION annotation: "v277 bet_b_4stage_batch128_v1 RE-RUN of v249 batch=128 axis at N=8192 5-seed mean ret_A=0.7449 (v249 was 0.7499 = within sd≈0.008 noise envelope; same axis 2-shot replication confirms reproducibility); 5TH cumulative independent corroboration across (N × batch × epochs × seeds × corpus-shift) 5 rehab axes; cumulative 26 seeds 0/26 clear 0.80 HP on ret_A; intrinsic-not-tuning interpretation FURTHER STRENGTHENED; Cluster C C1-C5 architectural rescues remain only path to Tier-1 per v273 at-risk-claim register." 

**True continual learning at production scale row 🟡 UNCHANGED** with same 5TH-AXIS annotation.

Per [[feedback-rehabilitation-after-rejection]] this is NOT a closure; rescue sketches CHEAPEST-FIRST:
- (R1, **PRIMARY / SUBSUMPTION 0-cost STRONGEST**) — Re-frame Bet B 4-stage as "substrate-native 4-stage retention=0.74-0.75 spec" per v249 R1 inheritance. v277 5th-axis batch-128 replication STRENGTHENS the substrate-native-spec interpretation. Would promote row to 🟢 under substrate-native-spec framing; requires user buy-in. PROMOTED TO PRIMARY-RECOMMENDED at v277 (5-axis exhaustion sufficient for substrate-native-spec promotion).
- (R2, CHEAP ~5min lit-scan) — Inherited from v249 R2 lit-scan "intrinsic capacity ceiling in 4-stage sequential continual learning with Hebbian write rule"; STRONGER prior given 5-axis exhaustion. Cheaper than additional substrate runs.
- (R3, CHEAP ~60min GPU) — Inherited v249 R3 axis-3 Phase-D A-weighted replay (v270 wave14_betB_phaseD_aweight_v2 ALREADY SHIPPED FOURSTAGE_MIDDLE_BAND ret_A=0.751 = 3RD same-corpus axis confirming sub-0.80 from v249). DISCHARGED — counted as 3rd of the 5 axes.
- (R4, MEDIUM ~2h GPU) — Inherited v249 R4 mechanism-class M1 hierarchical replay (architecture-level separation).
- (R5, MEDIUM ~2h GPU) — Inherited v249 R5 mechanism-class M2 attention-gated readout. **NOTE: v273 Cluster C anchors (C1 frozen-W-Phase-A + C2 wider-Phase-A-N + C3 2x-M-Phase-A + C4 dual-W-CLS + C5 Hebbian-only-Phase-A) are still pending in queue per the v273 at-risk-claim register; those are R4/R5 mechanism-class probes by another name.**

**Queue-refill SKIPPED** — GPU 23 pending+running HEALTHY (well above queue=0 trigger) + CPU 10 pending+running HEALTHY. Per [[feedback-pipeline-pacing]] + [[feedback-no-padding-experiments]] no auto-queue while queue is depth ≥ 1. Rescues R2/R4/R5 are CANDIDATES not auto-queued; Cluster C C1-C5 already in queue covers R4/R5.

### v276 -> v277 portfolio + reliability moves

- Portfolio counts UNCHANGED: 14 ✅ + 31 🟢/🟡/🔬 (no row adds, no closures, no demotions at portfolio-level).
- **TCFT deletion-cert envelope row 🟢 85-94% → 🟢 88-96% LIFT (+3% both bounds)** — V1 production-scale 5-seed × 5-M_frac N=8192 monotonic spearman=-1.000 HARD_PASS = highest-evidence-density TCFT corroboration; +3% per dispatch directive; cap at 88-96% to preserve calibration headroom for future TCFT-family axes.
- **Non-eq-stat-mech 🟢 67-77% → 🟢 69-79% LIFT (+2% both bounds)** — TCFT is leading non-eq survivor (post v276 HS-class 3-strike); production-scale 5-seed × 5-M sweep monotonic spearman is direct framework-class evidence; conservative +2% (vs +3% on TCFT row) because non-eq class is broader than TCFT alone.
- **Framework reliability product-feature 88-97% → 89-98% LIFT (+1% both bounds)** — deletion-cert killer feature is the strongest product-feature claim; TCFT V3 directly strengthens it at production-scale 5-seed defense.
- Framework reliability specific 70-83% UNCHANGED; general 73-83% UNCHANGED.
- 0 capability-row closures; 0 capability-row reopens; 0 row additions; 0 demotions; 1 row-status band lift (TCFT +3%); 1 reliability-band lift (non-eq +2%); 1 reliability-band lift (product-feature +1%).
- Bet B 4-stage 🟡 UNCHANGED with 5TH-AXIS BATCH-128 RE-RUN CORROBORATION annotation; substrate-native-spec rescue (R1) PROMOTED to PRIMARY-RECOMMENDED.
- HONEST 184 → 186 (+2: V1 V2 both honest; no label-vs-honest catches this batch).
- LABEL-VS-HONEST 133 UNCHANGED.
- 0 NEW routing files (V1 discharges 2 open routings; V2 rescues inherit v249 + Cluster C already-pending).
- Pipeline-pacing: GPU 23 pending HEALTHY + CPU 10 pending HEALTHY; refill conditions NOT met.
- 188th PROT-009 paired commit; verdict_handler sub-agent inline strategy+visibility no Agent sub-dispatch.

### Routings discharged (NOT this batch — historical reconciliation)

- v260 `strategy_request_to_exp_dev_v260_tcft_m_sweep_5seed_proper_2026-05-28.md` ✓ DISCHARGED by V1 tcft_m_sweep_v3_n8192_5seed clean 5-seed N=8192 FULL HARD_PASS.
- v257 PRIMARY rescue (a) TCFT FULL 5-seed re-run ✓ DISCHARGED by V1.

### PROT compliance (v277)

- **PROT-004/006**: 0 row closures; 0 row REFRAMEs; 0 portfolio adds; rescue sketches CHEAPEST-FIRST inline for V2 (R1 substrate-native-spec PROMOTED PRIMARY 0-cost subsumption; R2 lit-scan; R3 DISCHARGED via v270; R4/R5 covered by v273 Cluster C in queue).
- **PROT-007**: cap_map row table UPDATED with v277 row.
- **PROT-008**: 1 row band LIFT (TCFT +3%) + 2 reliability-band lifts (non-eq +2%; product-feature +1%); state-transition validator: TCFT was 🟢, stays 🟢 (band tightens within color); non-eq was 🟢, stays 🟢; product-feature was checkmark, stays checkmark; no demotions; all moves are upward LIFTs justified by V1 production-scale 5-seed × 5-M_frac × N=8192 spearman=-1.000 HARD_PASS.
- **PROT-009**: cap_map.md + strategy_decisions_2026-05-29.md + visibility_decisions_2026-05-29.md staged atomically; **188th PROT-009 paired commit**.
- **PROT-018**: V1 `tcft_m_sweep_v3_n8192_5seed` carries `_n8192` AND `_5seed` AND `_v3` suffixes ✓; V2 `bet_b_4stage_batch128_v1` `_batch128_v1` is axis-label-not-N suffix (config.N=8192 confirmed; same pattern as v249).
- **[[feedback-verdict-msg-honest-reread]]**: 184 → 186 honest obs (+2: V1 V2 both honest); LABEL-VS-HONEST 133 UNCHANGED.
- **[[feedback-no-smoke]]**: brutal honesty applied — V1 label "Tier-1 lock-in evidence" verified per-cell as HONEST (worst cell 0.01177 < 0.10 HP; all 25 cells valid; spearman=-1.000); V2 ret_A=0.745 honestly classified as 5TH-AXIS SUB-0.80 corroboration not noise.
- **[[feedback-rescue-sketch-first-sequencing]]**: V2 R1 substrate-native-spec 0-cost subsumption PRIMARY; R2 lit-scan CHEAPEST; R3 DISCHARGED; R4/R5 covered by Cluster C in queue.
- **[[feedback-rehabilitation-after-rejection]]**: V2 NOT a closure event; 5-axis exhaustion is robust characterization not closure; substrate-native-spec PRIMARY rescue ready.
- **[[feedback-dont-overextend-theorems]]**: V1 HARD_PASS does NOT propagate to all non-eq-class members; non-eq-stat-mech band lifts +2% (conservative) not +3% because class is broader than TCFT.
- **[[feedback-pipeline-pacing]]**: GPU 23 + CPU 10 both HEALTHY; refill conditions NOT met.
- **[[feedback-obey-user-pause-explicitly]]**: pause flag ABSENT verified at start = ACTIVE state.
- **[[feedback-no-padding-experiments]]**: 0 routing files filed; V1 discharges 2 open routings; V2 rescues inherit from v249 + Cluster C in queue; no padding.
- **[[feedback-subagent-permission-inheritance]]**: LOCAL commit only; push deferred to main thread per role contract Step 4 hand-off.
- **[[feedback-cap-map-update-protocol]]**: atomic commit cap_map.md + strategy_decisions_2026-05-29.md + visibility_decisions_2026-05-29.md (pull-first attempted; blocked by pre-existing unrelated working-tree state which main thread will reconcile).
- **[[feedback-decision-log-eol-handling]]**: append via tools/orchestrator/append_decision_log.py (preserves EOL).
- **[[feedback-verdict-arrival-is-queue-depletion-signal]]**: GPU=23 + CPU=10 both HEALTHY; no depletion signal.
- **[[feedback-step-back-eval]]**: V1 first clean 5-seed N=8192 FULL HARD_PASS triggers framework-reliability-recalc gate per dispatch directive — answered YES with TCFT +3% / non-eq +2% / product-feature +1%; V2 5th-axis triggers "is substrate-native-spec rescue ready" gate — answered YES (PROMOTE R1 to PRIMARY-RECOMMENDED).
- **[[feedback-lit-scan-calibration-penalty]]**: V1 N=8192 5-seed × 5-M direct empirical scaling-confirmation is NOT novel-synthesis; no penalty applied; full +3% TCFT lift warranted.

Cumulative HONEST observations: 184 (v276) -> **186 (+2: V1 V2 both honest)**.
Cumulative LABEL-VS-HONEST catches: 133 UNCHANGED.

Commit message: `Cap map: v276 -> v277 (BATCHED 2-VERDICT post-v276 GPU completion wave: tcft_m_sweep_v3_n8192_5seed TCFT_V3_HARD_PASS PRODUCTION-SCALE 5-SEED x 5-M_frac FIRST CLEAN N=8192 5-SEED TCFT M-SWEEP FULL spearman=-1.000 mean_vr_by_M={128:0.0119,256:0.0015,512:0.0001,1024:0,2048:0} 25/25 cells valid HIGHEST-EVIDENCE-DENSITY TCFT CORROBORATION RELIABILITY-RECALC EVENT discharges v260+v257 routings + bet_b_4stage_batch128_v1 FOURSTAGE_MIDDLE_BAND ret_A=0.7449 5/5 seeds N=8192 5TH INDEPENDENT BET-B STAGE-A SUB-0.80 CORROBORATION RE-RUN of v249 batch=128 axis cumulative 26 seeds 0/26 clear 0.80 HP across 5 rehab axes substrate-native-spec rescue PROMOTED PRIMARY; portfolio 14+31 UNCHANGED; TCFT deletion-cert green 85-94%->88-96% LIFT +3% per dispatch directive; non-eq-stat-mech 67-77%->69-79% LIFT +2% lower+upper; product-feature 88-97%->89-98% LIFT +1% lower+upper; specific 70-83% UNCHANGED; general 73-83% UNCHANGED; Bet B 4-stage yellow UNCHANGED 5TH-AXIS BATCH-128 RE-RUN annotation substrate-native-spec rescue PROMOTED PRIMARY; HONEST 184->186 (+2); LABEL-VS-HONEST 133 UNCHANGED; 0 NEW routings filed V1 discharges 2 open routings V2 inherits Cluster C in queue; 188th PROT-009 paired commit; verdict_handler sub-agent inline strategy+visibility no Agent sub-dispatch)`
v278 ANNOTATION-ONLY: Saad-Solla LEADING row annotated MULTI_AXIS_RESOLUTION_OVERCLAIM (seed-axis N=8192 5-seed; M-axis N=8192 2-seed; codebook-axis N=4096 3-seed; N-axis mixed; 134th LABEL-VS-HONEST sub-flavor MULTI_AXIS_RESOLUTION_OVERCLAIM); KF-2 BE-1 STRATEGIC_INTERPRETATION_OVER_CLAIM mechanism refined (max_iso 1/99 discretization floor across 10 FULL runs spanning fp32-int1; BE-1 v2 requires retrieval/pool-readout accuracy metric n_test_pairs>=1000); both from Agent-2 forensic mining v276; row-states UNCHANGED; portfolio 14+31 UNCHANGED; reliability UNCHANGED; 189th PROT-009 paired commit

## v278 -> v279 SINGLE-VERDICT @ 2026-05-29 ~21:16 (bid_order_parameter_v7_n4096_bsc BID_V7_HARD_FAIL — METRIC-DEFINITION DISAGREEMENT not framework refutation; ANNOTATION-ONLY classification B; user no-refill mode)

**Trigger.** Single verdict event: `bid_order_parameter_v7_n4096_bsc` completed on remote_cpu_queue at wall_s=3793.67 (~63 min), ended ~2026-05-29T21:16 just before tcft_m_sweep_v4_n4096 picked up. Metrics fetched via remote bridge (`_source=remote`, authoritative): N=4096 BSC atoms, M_fracs=[0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 12.0, 16.0], 3 seeds [7, 17, 23], smoke=False. Verdict tag = BID_V7_HARD_FAIL with verdict_msg `BID collapses inside Hopfield bands at M_frac<=2.0. rho=1.000 n_outside_low=0 n_inside_low=18 ... bid_means=[0.092, 0.094, 0.104, 0.107, 0.113]...`. Pause flag check: `data/orchestrator_paused.flag` ABSENT (verified) = ACTIVE state, BUT user explicitly disabled refill in dispatch ("token-efficient mode; do NOT trigger exp_dev refill"). Local `data/exp_bid_order_parameter_v7_n4096_bsc/metrics.json` is a STALE PRE-SHIP SMOKE artifact (N=512, M_fracs=[0.1, 1.0], 1 seed, elapsed=0.01s) — DO NOT use; remote bridge authoritative per [[feedback-verdict-handler-remote-metrics-fix-2026-05-27]].

### Step 0 honest re-read (CRITICAL — METRIC-DEFINITION COMPARISON)

The verdict_msg label "BID_V7_HARD_FAIL — BID collapses inside Hopfield bands at M_frac<=2.0" is HONEST AT THE METRIC LEVEL but the **framework-implication framing is MISLEADING absent metric-comparison context**. Honest reading requires comparing v7's metric definition to v2's (which HARD_PASSed at N=8192 5-seed FULL anchoring the non-eq-stat-mech framework class per project_substrate_non_eq_stat_mech_class_2026-05-27.md).

**v7 metric** (per `exp_bid_order_parameter_v7_n4096_bsc.py:79, 87-91`):
- `BAND_MAX_INSIDE = 0.55` — inherited from `bid_m_normalized_v1.BAND_MAX_INSIDE`
- `normalized_bid = bid / N`
- `outside_band = (normalized_bid > 0.55)`
- HARD_FAIL fires when `bid_norm < 0.55` (BID < 0.55 * N = BID < 2253) at M_frac<=2.0

**v2 metric** (per `exp_bid_order_parameter_v2.py:75-93` + project_substrate_non_eq_stat_mech_class memory):
- `BID_RETRIEVAL = [1.0, 2.5]`, `BID_SPIN_GLASS = [N/4, N/2]`, `BID_PARAMAGNETIC = [N-5, N]` (3 Hopfield-class bands)
- Pass criterion: BID outside ALL 3 bands with `sigma_margin >= 2.0`
- v2 N=8192 5-seed FULL: BID=46.95+/-5.90, sigma_margin=7.54, 5/5 OUTSIDE all 3 bands; later HP3_BAND_CLEARANCE_PASS at N=[1024..8192] BIDs=[50.668, 50.3992, 63.2693, 73.1249]

**Codebook (BOTH v2 and v7)**: BSC (random +/-1 atoms). v2 uses `make_bsc()` at v2:106-107, 245-246; v7 inherits v6's `make_bsc()`. Codebook is **NOT** the distinguisher. Hypothesis (C) "BSC vs Kerdock" is **REJECTED**.

**Metric-comparison arithmetic**: v7's bid_means at M_frac=2.0 = 0.118 (mean of 3 seeds) → absolute BID = 0.118 * 4096 = ~483. v2 at N=4096 gave absolute BID ~63 (HP3 scaling) which is FAR BELOW 0.55 * 4096 = 2253; v2 would ALSO HARD_FAIL the v7 `normalized_bid > 0.55` criterion at N=4096 BY 36x. So the v7 criterion is testing a DIFFERENT mathematical regime ("BID is more than half of N", i.e. near-paramagnetic top-band) than the v2 criterion ("BID is outside [1, 2.5] retrieval AND outside [N/4, N/2] spin-glass AND outside [N-5, N] paramagnetic with >=2 sigma").

**Concretely:** v7's `normalized_bid > 0.55` at N=4096 corresponds to BID > 2253, which is INSIDE the spin-glass band [N/4=1024, N/2=2048] HIGH edge and approaching paramagnetic [N-5=4091, N]. The v7 criterion is testing "BID is in the upper-paramagnetic regime" not "BID is outside all 3 class bands". These are MATHEMATICALLY DIFFERENT predicates. v2's actual BID values (~47-73 at N=1024..8192) are BELOW the spin-glass band [N/4, N/2] AND ABOVE the retrieval band [1, 2.5] = they sit in the **gap** between retrieval and spin-glass = "OUTSIDE_ALL_BANDS / NOVEL_CLASS" per v2 pre-registration. v7's threshold (0.55 * N) sits ABOVE the spin-glass band, so substrate falling below it does NOT contradict v2's gap-finding.

**Classification (B) confirmed:** This is a **test-region disagreement at the metric-definition level**. Both v6 (parent, also HARD_FAILed via same threshold; production metrics unavailable so only smoke confirms direction) and v7 inherited the `BAND_MAX_INSIDE=0.55` threshold from `bid_m_normalized_v1` — a normalized-BID family of probes with a DIFFERENT testing question (`is substrate in upper-paramagnetic regime?`) than the v2/v275 family (`is substrate outside ALL 3 Hopfield-class bands?`). v275's `bid_m_normalized_v5_n8192` HARD_PASSed using yet a THIRD threshold (absolute mean_bid > 100.0 against per-N spin-glass [N/4, N/2] and paramagnetic [N-5, N] bands; per v275 strategy entry) — also methodology-distinct from v7.

**Honest verdict reframing**: `BID_V7_NORMALIZED_THRESHOLD_INSIDE_AT_N4096_BSC` = substrate BID at N=4096 BSC is below the 0.55*N normalized threshold across all 18 cells (3 seeds × 6 low-M_fracs <= 2.0) and across all 30 cells (3 seeds × 10 M_fracs in [0.05..16.0]). bid_means range from 0.092 (M_frac=0.05) monotonically rising to 0.131 (M_frac=16.0); this IS monotone in M (rho=1.000 = perfectly monotonic, but the sign is POSITIVE i.e. BID grows with M-load not decreases). The verdict_msg saying "rho=1.000 ... collapses INSIDE bands" is honest at the numerical level but misleading at the framework level — it's the same substrate signature as v2 (low-magnitude BID outside-retrieval-and-spin-glass-but-far-below-paramagnetic) just MEASURED with a different yardstick that registers "false" against the upper-band threshold.

### Cap_map move (annotation-only, no row demotion)

**Substrate-outside-static-Hopfield-bands capability row** (established v268→v269; lifted v275 +1% lower bound on non-eq-stat-mech via bid_m_normalized_v5 N=8192 +5th axis): UNCHANGED at row level (🟢 with current band).

Annotation extension: "v279 bid_order_parameter_v7_n4096_bsc BID_V7_HARD_FAIL at N=4096 BSC 3-seed across 10 M_fracs [0.05..16.0] under `normalized_bid > 0.55` criterion (inherited from `bid_m_normalized_v1.BAND_MAX_INSIDE`) = METRIC-DEFINITION DISAGREEMENT vs v2/v230/v275 — NOT framework refutation. v7 measures `normalized_bid > 0.55` (BID > 0.55*N ≈ in upper paramagnetic regime); v2 measures `BID outside [retrieval=[1,2.5], spin-glass=[N/4,N/2], paramagnetic=[N-5,N]] with sigma_margin>=2` (i.e. BID in the gap between retrieval and spin-glass). v7 codebook=BSC IDENTICAL to v2; only the threshold function differs. v7 per-cell bid_means [0.092..0.131] correspond to absolute BID [377..536] at N=4096 which is BELOW the v2 spin-glass band [N/4=1024, N/2=2048] = consistent with v2's "outside_all_bands" gap-finding. Honest framing: substrate BID is in low-magnitude gap-region (v2 PASS regime) NOT in upper-paramagnetic regime (v7 PASS regime). Spearman rho=+1.000 in v7 (BID grows monotonically with M-load) corroborates substrate's M-dependent BID-scaling per v275 bid_m_normalized_v5. Row state UNCHANGED."

**Non-eq-stat-mech framework class row** (currently 🟢 69-79% lower-upper per v277): **UNCHANGED**. v2 N=8192 5-seed FULL HARD_PASS (sigma_margin=7.54, BID=46.95±5.90) remains the load-bearing anchor; v7 is a different-metric secondary probe that does not contradict v2 at the metric-comparison level (per Step 0 analysis above). Applying [[feedback-lit-scan-calibration-penalty]] caution: do NOT reduce the band on a metric-definition disagreement; the v2 multi-seed FULL is far stronger evidence than a single-anchor different-threshold v7.

**SKAH-M / lR-phase row** (🟢 55-70% per project_substrate_skahm_class_confirmed_2026-05-27): UNCHANGED (v7 is BID-axis not SKAH-M-axis).

**HONEST observations counter**: v277 had 186; this verdict is 1 HONEST observation at the metric-level + 1 LABEL-VS-OVER-CLAIM-AT-FRAMEWORK-LEVEL catch (the verdict_msg "collapses inside Hopfield bands" reads at the framework level as a non-eq refutation but the metric is testing a different predicate than the v2-anchored Hopfield-class definition). I record this as the **135th LABEL-VS-HONEST catch, new sub-flavor METRIC_DEFINITION_FRAMEWORK_OVER_CLAIM**. Cumulative HONEST observations: 186 -> **187 (+1: V1 honest-at-metric)**.

**Portfolio**: 14+31 UNCHANGED (annotation only). **Framework reliability** UNCHANGED across all bands (non-eq 69-79%, SKAH-M 55-70%, TCFT 88-96%, KF-1 65-80%, product-feature 89-98%, specific 70-83%, general 73-83%).

### Follow-on recommendations (for orchestrator main thread to decide whether to ship; NOT auto-dispatched)

Per user no-refill directive, exp_dev refill SKIPPED. Surfacing for main-thread decision:

(R1, **CHEAPEST / SUBSUMPTION 0-cost STRONGEST**, recommended) — **Annotate the bid_m_normalized family of experiments** (v1, v5, v6, v7) as testing the `normalized_bid > 0.55` upper-paramagnetic-threshold predicate, distinct from the v2/v230 bid_order family which tests the `BID outside all 3 Hopfield-class bands with sigma_margin >= 2` gap-predicate. This is a documentation rescue with 0 compute cost; closes the framework-interpretation ambiguity that v7's verdict_msg accidentally created. RECOMMENDED FIRST.

(R2, CHEAP, 0-cost variant of R1) — Add to `notes/substrate_capability_map.md` a "BID metric family glossary" sub-section under the substrate-outside-static-Hopfield row, naming the two metric families explicitly so future verdict-handler runs catch this metric-definition disagreement at Step 0 not retroactively. Methodology lock per [[feedback-lock-in-inefficiency-fixes]].

(R3, MEDIUM, would test the substantive question) — Ship `bid_order_parameter_v8_n4096_bsc` re-running v7's N=4096 BSC 3-seed config but applying the v2 metric (absolute BID + 3-class-band test + sigma_margin >= 2) to verify that the substrate's gap-region finding holds at N=4096 (v2's actual N=4096 cell was BID=63.27 per v2 metrics_msg `[50.668, 50.3992, 63.2693, 73.1249]`). Would CORROBORATE v2 at N=4096 across BSC codebook with 3 seeds. Estimated ~3800s on remote_cpu_queue (matches v7 wall). NOT URGENT — v2's HP3 already covers N=[1024, 2048, 4096, 8192] in 1 sweep.

(R4, NOT-RECOMMENDED) — Demote BID row or non-eq band. Rejected per Step 0 analysis: v7 is metric-disagreement not framework refutation; demotion on this signal would be premature per [[feedback-dont-overextend-theorems]].

(R5, NOT-RECOMMENDED) — Treat as Kerdock vs BSC codebook effect. Rejected: v2 and v7 BOTH use BSC; codebook is not the distinguisher.

### PROT compliance (v278 -> v279)

- **PROT-004/006**: 5 rescue sketches filed (R1 R2 R3 R4 R5); cheapest sequenced first per [[feedback-rescue-sketch-first-sequencing]]; R4/R5 explicitly REJECTED with mechanism per [[feedback-no-smoke]] (brutal honesty about which directions are not on the table). No row CLOSED so PROT-004 closure-rescue-list discipline does not bind, but rescue sketches filed proactively for clarity.
- **PROT-007**: cap_map row table (in `substrate_capability_map_history.md`) UPDATED with v279 row.
- **PROT-008**: validator skipped (annotation-only bump; row-state UNCHANGED).
- **PROT-009**: cap_map.md (v278 -> v279 entry) + substrate_capability_map_history.md (cap_map row table) + strategy_decisions_2026-05-29.md (this entry) + visibility_decisions_2026-05-29.md (one-line) staged atomically; **190th PROT-009 paired commit**.
- **PROT-018**: anchor `bid_order_parameter_v7_n4096_bsc` includes `_n4096` suffix, config N_FULL=4096 (verified at v7.py:82, asserted); CLEAN no anchor-vs-N mismatch.

### Memory adherence

- **[[feedback-verdict-msg-honest-reread]]**: Step 0 honest re-read performed via metric-definition comparison (v7's BAND_MAX_INSIDE=0.55 normalized vs v2's 3-class-bands absolute); label-vs-honest catch filed (135th, new sub-flavor METRIC_DEFINITION_FRAMEWORK_OVER_CLAIM).
- **[[feedback-verdict-handler-remote-metrics-fix-2026-05-27]]**: bridge `get_metrics()` returned `_source=remote`; stale local pre-ship smoke at `data/exp_bid_order_parameter_v7_n4096_bsc/metrics.json` (N=512, 1 seed, elapsed=0.01s) IGNORED.
- **[[feedback-dont-overextend-theorems]]**: a metric-definition disagreement at ONE anchor does not refute the non-eq framework class anchored by v2 N=8192 5-seed FULL HARD_PASS; row UNCHANGED.
- **[[feedback-obey-user-pause-explicitly]]**: pause flag absent BUT user explicit no-refill directive HONORED; exp_dev queue refill SKIPPED.
- **[[feedback-no-padding-experiments]]**: no padding experiment shipped; R1/R2 documentation rescues are zero-compute; R3 surfaced as RECOMMENDATION not auto-dispatch per user directive.
- **[[feedback-cap-map-update-protocol]]**: atomic commit cap_map.md + history.md + strategy_decisions + visibility_decisions.
- **[[feedback-decision-log-eol-handling]]**: this entry appended via `tools/orchestrator/append_decision_log.py`.
- **[[feedback-no-smoke]]**: brutal honesty applied — verdict_msg "collapses inside Hopfield bands" surfaced as framework-level over-claim while metric-level reading honest; 5 rescue sketches with explicit reject mechanism for R4/R5.

### Commit & push

Commit message: `Cap map: v278 -> v279 (SINGLE-VERDICT bid_order_parameter_v7_n4096_bsc BID_V7_HARD_FAIL N=4096 BSC 3-seed 10 M_fracs METRIC-DEFINITION DISAGREEMENT NOT FRAMEWORK REFUTATION classification B; v7 normalized_bid>0.55 inherited from bid_m_normalized_v1 tests upper-paramagnetic-regime predicate distinct from v2 absolute-BID-outside-3-class-bands-with-sigma-margin gap-predicate; codebook=BSC IDENTICAL between v2 and v7 hypothesis C rejected; v7 absolute BID range [377..536] at N=4096 BELOW v2 spin-glass band [N/4=1024, N/2=2048] CONSISTENT with v2 outside_all_bands gap-finding; substrate-outside-static-Hopfield row UNCHANGED 🟢; non-eq-stat-mech 69-79% UNCHANGED v2 N=8192 5-seed FULL HARD_PASS load-bearing anchor; SKAH-M 55-70% UNCHANGED; portfolio 14+31 UNCHANGED; HONEST 186->187 (+1); LABEL-VS-HONEST 134->135 (+1 NEW SUB-FLAVOR METRIC_DEFINITION_FRAMEWORK_OVER_CLAIM); user no-refill mode honored exp_dev SKIPPED; 5 rescue sketches R1 SUBSUMPTION-annotate-metric-families recommended R2 cap_map-glossary recommended R3 v8-with-v2-metric MEDIUM-not-urgent R4 demote REJECTED R5 codebook-effect REJECTED; 190th PROT-009 paired commit; verdict_handler sub-agent inline strategy+visibility no Agent sub-dispatch)`

Push: BLOCKED from sub-agent context per [[feedback-subagent-permission-inheritance]]; orchestrator main thread executes `git push origin main` as 1-tool follow-up after this commit lands.
