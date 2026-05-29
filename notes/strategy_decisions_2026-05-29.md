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
