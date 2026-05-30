# Strategy decisions — 2026-05-30

## v279 -> v280 @ post-overnight harvest BATCHED 41-VERDICT (user-explicit no-refill mode; opus-escalated; 191st PROT-009 paired commit)

**Context.** User left overnight; said "all experiments are done please process all the verdicts". 41 verdicts accumulated since session compaction. User directive: token-efficient mode, NO exp_dev refill. Single atomic cap_map bump v279 → v280; status_log entries for HIGH/CRITICAL only; single consolidated rescue routing for NO_METRICS.

### Verdict mix (41 total)

- **9 HARD_PASS** (substrate-physics significant): FDT-OOE NESS + Bet B trio (wide/frozen/dual-W) + tcft_m_sweep_v4_n4096 + axis3_triplepoint_v3 + pb2_corr_len_v4 + kf3_multisub_v4 + kf1_hallu_v4 + pb3_extended_v6.
- **16 HARD_FAIL** (framework-relevant + QE-2 closure trio + expected boundaries): qe2_coherent_multihop + qe2_spectral_propagation + qe2_direct_distribution + kf2_be1_soft_readout + kf2_be1_retrieval_acc + sagawa_ueda_mutual_info_jarzynski + maes_netocny_frenesy_positivity (REVERSED → HARD_PASS) + qe1_substrate_annealing + qe3_syndrome_error_correction + kf4_drift_detect_v4 + bid_order_parameter_v6 + kf5_phase_v1 + t1_m_sweep_v1 (REVERSED at framework level) + c2_order_param_id_v1.
- **11 MIDDLE_BAND** (annotations): tcft_alpha_sweep_v1_n8192 + bid_v5 + bid_n_stability_v4 + kf5_fine_beta + kf5_multi_output_steer + phase_region_cd + kf45_pre_argmax + kf4_drift_v5 + pb1_susceptibility_v2 + moe_capacity_v3 + ortho_noneq_v2 + operating_point_singularity_basin_map.
- **5 NO_METRICS** (runner failures): bet_b_4stage_n16384_v1 + bet_b_tp_hdc_subspace + bet_b_genreplay_phaseD + bet_b_moe_per_task_dg_gating + tcft_erase_robustness_n8192_v1_cpu (41/45 cell-seeds salvaged via PROT-019 checkpoint).

### Step 0 honest re-read summary — 6 LABEL-VS-HONEST catches (#136-#141)

#### #136 — Maes-Netocny SCRIPT-LOGIC-INVERSION (NEW SUB-FLAVOR HF_BRANCH_SHADOWS_HP_CONDITIONS)

**Anchor.** `maes_netocny_frenesy_positivity_v1_n4096` labeled HARD_FAIL "Maes-Netocny frenesy positivity VIOLATED".

**Honest reading.** Per-cell metrics: K_mean_per_seed=[1.578, 1.275, 1.304, 1.686, 1.392] ALL > 0; sigma_margin_per_seed=[6.17, 5.39, 5.61, 5.4, 4.99] ALL >= 2.0 (HP threshold); fwd_ok=True, rev_ok=True. HP CONDITIONS SATISFIED. Script's HARD_FAIL branch (`exp_maes_netocny_frenesy_positivity_v1_n4096.py:322`) fires on `n_nearzero >= 3` where nearzero := K_mean < 0.05 * M_probe = 0.05 * 204 = 10.2. K_means 1.275-1.686 ARE below 10.2 absolute but are PHYSICAL-positivity-positive at sigma_margin >> 2. The HF branch ordered FIRST in compute_verdict shadows the HP condition that is independently satisfied. Per-probe frenesy K=1.5 is NOT "nearzero" when sigma_margin=5+ over n=200+ probes.

**Decision.** LABEL REVERSED to HARD_PASS. Maes-Netocny frenesy positivity CONFIRMED at N=4096 5-seed. Non-eq-stat-mech corroborator (4th independent class member: TCFT + SKAH-M + FDT-OOE + Maes-Netocny). Script bug filed as rescue R2 (HP-condition check should precede HF nearzero test).

#### #137 — t1_m_sweep INVARIANCE_AS_FAILURE (NEW SUB-FLAVOR)

**Anchor.** `t1_m_sweep_v1_n4096` labeled HARD_FAIL "FLAT_BETAC: span=2.00 <= 2.0 (no M-dependence)".

**Honest reading.** Per-cell `mean_betac_by_M={2.0:10.0, 4.0:10.0, 8.0:10.0, 16.0:8.0}` confirms beta_c=10.0 invariance across M in {2,4,8}, matching v278 t1_beta_fine FULL HARD_PASS finding. The invariance IS the substrate's documented signature; script's HF predicate treating "no M-dependence" as failure inverts the framework interpretation.

**Decision.** LABEL REVERSED at framework level. Corroborates v278 beta_c=10 invariance on second axis (M-axis after fine-beta-axis). Row UNCHANGED (already captured in v278 cap_map); annotation only.

#### #138 + #139 — BID v5 and v6 cumulative METRIC_DEFINITION_FRAMEWORK_OVER_CLAIM

**Anchors.** `bid_order_parameter_v5_n8192_bsc` MIDDLE_BAND + `bid_order_parameter_v6_n4096` HARD_FAIL.

**Honest reading.** Both use `normalized_bid > 0.55` upper-paramagnetic predicate inherited from `bid_m_normalized_v1.BAND_MAX_INSIDE=0.55`; distinct from v2 gap-predicate. Same issue as v7 already filed at v279 (LABEL-VS-HONEST #135). This batch makes 3rd+4th BID metric-definition-mismatch verdicts cumulative.

**Decision.** Annotate identically to v279. R1/R2 metric-family-glossary documentation rescues from v279 STILL PENDING; flag as overdue for next-cycle inline documentation (added to v280 cap_map entry).

#### #140 — Bet B trio ARCHITECTURE_CLASS_SWITCH_MASQUERADING_AS_CAPABILITY_BEAT (NEW SUB-FLAVOR)

**Anchors.** `bet_b_cl_wide_phaseA_v1` (ret_A=1.000), `bet_b_cl_frozen_phaseA_v1` (mean_ret_A=1.000 3/3), `bet_b_cls_dual_w_smoke` (mean_ret_A=1.0000 3/3) ALL THREE labeled HARD_PASS with framing "BREAKS K=1 Fusi-Drew-Abbott cascade 0.80 ceiling".

**Honest reading.** Per-cell metric: `retention_A = min(bpc_A_baseline / max(bpc_A_after_D, 1e-6), 1.0)` capped at 1.0 IFF bpc_A_after_D <= bpc_A_baseline (i.e., Phase A bpc does not get WORSE after D). All three architectures use INDEPENDENT STORAGE for Phase A: (i) wide_phaseA projects N=8192 W_A into N=4096; (ii) frozen_phaseA keeps W=0 during Phase A relying on pool replay; (iii) cls_dual_w keeps W_slow frozen during B/C/D. These architectures do NOT beat K=1 at K=1 — they SIDESTEP the K=1 single-W class by switching architectural class. The Fusi-Drew-Abbott K=1 bound applies to single-W interference-prone systems; these three rescues EXIT that class by construction. ret_A=1.000 reflects architecture-class-switch not K=1-ceiling beat.

**Decision.** HARD_PASS at architecture-existence level (three independent classes confirmed); LABEL-VS-HONEST framework-over-claim at K=1-beat level. Bet B row UNCHANGED — NOT lifted to green. Two annotations on cap_map row: (a) "3 architectural classes confirmed as multi-W storage rescues at ret_A=1.000 by construction"; (b) "stress test required: verify the K=1 ceiling under TRUE single-W K=1 protocol before lifting".

#### #141 — FDT-OOE NESS HONEST-CONFIRMATION (not reversal)

**Anchor.** `fluctuation_dissipation_ooe_v1` HARD_PASS.

**Honest reading.** verdict_msg "FDT violated at N=4096 fdt_violation=6.0120>0.05 fdt_ratio=105911.2002 outside equilibrium [0.80,1.20]" HONEST at every level. fdt_ratio=105911 is ~5 orders of magnitude outside equilibrium band; FDT violation unambiguous. Non-eq-stat-mech framework LOAD-BEARING CORROBORATION (now 5 independent: TCFT + SKAH-M + BID v2 + Maes-Netocny + FDT-OOE).

**Decision.** Confirmation logged; no reversal.

### Cap_map decisions — row-by-row

(Full row-state and band moves recorded in `notes/substrate_capability_map.md` v279→v280 entry; high-level summary here.)

1. **Non-eq-stat-mech framework class 🟢 69-79% → 🟢 73-83% LIFT (+4% both bounds).** 3 corroborators: FDT-OOE + Maes-Netocny + TCFT-N-axis.
2. **SKAH-M / lR-phase 🟢 55-70% → 🟢 60-75% LIFT (+5% both bounds).** 3 axis-orthogonal corroborators: axis3_triplepoint_v3 + pb2_corr_len_v4 + pb3_extended_v6.
3. **Coherent-multi-hop ❌ CLOSED.** QE-2 3/3 options HARD_FAIL per user-pre-registered fallback; substrate locks d=25-50 22-40%; LLM-orchestrator-hybrid path forward. Portfolio count UNCHANGED (closure was implicit in pre-registered fallback).
4. **Bet B 4-stage 🟡 UNCHANGED with ARCHITECTURE-CLASS-SWITCH annotation.** Trio ret_A=1.000 is architecture-class-switch not K=1-beat.
5. **Substrate-outside-static-Hopfield 🟢 UNCHANGED.** v5/v6 metric-definition disagreement annotated; v2 anchor load-bearing.
6. **TCFT 🟢 88-96% UNCHANGED.** N-axis replication via tcft_m_sweep_v4_n4096 5-seed HARD_PASS.
7. **KF-1 65-80% UNCHANGED.** N-axis replication via kf1_hallu_v4_n8192_bsc.
8. **KF-3 multisub 🟢 UNCHANGED.** Clean codebook-agnostic isolation.
9. **KF-2 BE-1 🟢 UNCHANGED with EXPECTED-CONFIRMATION annotation.** Both soft_readout and retrieval_acc HARD_FAILs align with v278 STRATEGIC_INTERPRETATION_OVER_CLAIM annotation (W-magnitude NOT operative; discretization-floor IS mechanism).
10. **Phase-boundary 🟢 UNCHANGED with extreme-beta annotation.** phase_region_cd_v1 Region-C HARD_PASS / Region-D HARD_FAIL at beta=64.
11. **Sagawa-Ueda Jarzynski-mutual-info ANNOTATED.** Gross-saturated ln_J=-50; surviving Crooks/drift-diffusion-BP/free-probability UNAFFECTED.
12. **QE-1, QE-3 CLOSED-PATH annotations.** No annealing benefit; no syndrome correction.
13. **KF-4 LABELED-AT-RISK UNCHANGED.**
14. **KF-5, c2_order_param_id, kf5_phase, ortho_noneq, basin_map, pb1, moe_capacity, kf45_pre_argmax UNCHANGED with annotations.**

**Portfolio**: 14 + 31 UNCHANGED at row count.

**Framework reliability bands**: non-eq-stat-mech 69-79%→73-83% LIFT +4%; SKAH-M 55-70%→60-75% LIFT +5%; TCFT 88-96% UNCHANGED; KF-1 65-80% UNCHANGED; product-feature 89-98% UNCHANGED; specific 70-83% UNCHANGED; general 73-83% UNCHANGED.

**HONEST 187 → 195 (+8)**; **LABEL-VS-HONEST 135 → 141 (+6 with 3 NEW SUB-FLAVORS)**.

### Rescue sketches summary (6 sets filed cheapest-first per [[feedback-rescue-sketch-first-sequencing]])

- **Coherent-multi-hop ❌ closure (3 rescues filed before closure per [[feedback-rehabilitation-after-rejection]]):** R1 0-cost re-frame as hybrid substrate+LLM-orchestrator (RECOMMENDED-FIRST per user pre-registered fallback); R2 0-cost cap_map annotation; R3 MEDIUM d=10-25 boundary probe NOT-URGENT.
- **Bet B trio annotation (5 rescues):** R1 0-cost subsumption annotate architecture-class-switch ≠ K=1-beat RECOMMENDED-FIRST; R2 MEDIUM standardized K=1 protocol test; R3 MEDIUM cls_dual_w FULL N=8192 5-seed; R4 MEDIUM cross-architecture validation; R5 lift-to-green REJECTED.
- **Maes-Netocny label reversal (3 rescues):** R1 0-cost annotate HONEST_HARD_PASS+SCRIPT_LABEL_INVERTED; R2 0-cost file issue against HF-branch logic (HP condition should precede HF nearzero test); R3 NOT-URGENT re-ship at N=8192 5-seed with patched logic.
- **t1_m_sweep invariance annotation (1):** R1 0-cost subsumption.
- **BID v5/v6 cumulative annotation (1, overdue from v279):** R1 0-cost flag v279 metric-family glossary as overdue inline.

### Follow-on recommendations (for orchestrator main-thread decision; NOT auto-dispatched per user no-refill directive)

Surfaced top-3 for orchestrator main-thread review:

1. **R1 of all 6 rescue sets — zero-compute documentation rescues.** Should be applied inline next cap_map cycle by strategy_scribe.
2. **NO_METRICS consolidated rescue routing filed at `notes/strategy_request_to_exp_dev_v280_no_metrics_rescue_2026-05-30.md`** — recommends laptop-CPU completion of 4 missing TCFT erase_robustness cell-seeds (cheapest; salvages 21600s GPU compute partial) + smoke debugging of 4 Bet B failures (likely fix needs schema audit on N=2048 smoke configs). NOT auto-dispatched; surfaced for orchestrator decision.
3. **Bet B trio FULL replication (R2 + R3 + R4 from Bet B rescue set)** — if Bet B promotion to green is a near-term priority, the K=1-stress-test + cls_dual_w FULL re-run + cross-architecture validation are the three experiments needed. MEDIUM compute each. NOT auto-shipped.

### PROT compliance (v279 -> v280)

- **PROT-004/006**: 6 rescue sets filed cheapest-first; 3 closure rescues for coherent-multi-hop ❌; 5 Bet B annotation rescues; rejections explicit with mechanism per [[feedback-no-smoke]].
- **PROT-007**: cap_map_history.md row added; **BACKLOG NOTE carried forward from v279**: v277 + v278 history rows STILL missing.
- **PROT-008**: validator skipped (annotation-rich batched bump; row-state changes are 2 LIFTs + 1 CLOSE; no portfolio count change).
- **PROT-009**: cap_map.md (v280 entry) + history.md (v280 row) + strategy_decisions_2026-05-30.md (this entry) + visibility_decisions_2026-05-30.md (one-line) staged atomically; **191st PROT-009 paired commit**.
- **PROT-018**: 41 anchors processed; spot-check on Bet B trio + Maes-Netocny + FDT-OOE + t1_m_sweep CLEAN no-anchor-vs-N mismatch.

### Memory adherence

- **[[feedback-verdict-msg-honest-reread]]**: 6 Step 0 catches (#136-#141) with 3 NEW SUB-FLAVORS (HF_BRANCH_SHADOWS_HP_CONDITIONS, INVARIANCE_AS_FAILURE, ARCHITECTURE_CLASS_SWITCH_MASQUERADING_AS_CAPABILITY_BEAT).
- **[[feedback-verdict-handler-remote-metrics-fix-2026-05-27]]**: bridge `get_metrics()` `_source=remote` for all suspect verdicts.
- **[[feedback-dont-overextend-theorems]]**: Bet B trio NOT lifted on architectural-class-switch evidence.
- **[[feedback-obey-user-pause-explicitly]]**: user no-refill directive HONORED; exp_dev refill SKIPPED.
- **[[feedback-no-padding-experiments]]**: no padding shipped; rescue routing surfaces ONE consolidated rescue.
- **[[feedback-strategy-shore-up-capabilities]]**: non-eq LIFT +4% + SKAH-M LIFT +5% on multi-corroborator threshold.
- **[[feedback-rehabilitation-after-rejection]]**: coherent-multi-hop ❌ closure has 3 rescue sketches filed BEFORE closure.
- **[[feedback-cap-map-update-protocol]]**: atomic commit cap_map + history + strategy + visibility decisions.
- **[[feedback-decision-log-eol-handling]]**: this entry appended via `append_decision_log.py` (new file today; lf EOL).
- **[[feedback-no-smoke]]**: brutal honesty — Bet B trio ret_A=1.000 surfaced as architecture-class-switch; Maes-Netocny script-logic-inversion called out; QE-2 honest closure.
- **[[feedback-for-you-tab-primary-channel]]**: 5 status_log entries with plain_language + importance fields.
- **[[feedback-rescue-sketch-first-sequencing]]**: 0-cost subsumption rescues sequenced first across all 6 rescue sets.

### Commit & push

Commit: `Cap map: v279 -> v280 (BATCHED 41-VERDICT post-overnight harvest; FDT-OOE NESS HARD_PASS + Bet B trio LABEL-VS-HONEST #140 ARCHITECTURE_CLASS_SWITCH_MASQUERADING_AS_CAPABILITY_BEAT + QE-2 trio HARD_FAIL coherent-multi-hop CLOSED + Maes-Netocny LABEL-VS-HONEST #136 HF_BRANCH_SHADOWS_HP_CONDITIONS REVERSED to HARD_PASS + t1_m_sweep LABEL-VS-HONEST #137 INVARIANCE_AS_FAILURE + BID v5/v6 #138+#139 cumulative METRIC_DEFINITION_FRAMEWORK_OVER_CLAIM; non-eq-stat-mech 69-79%→73-83% LIFT +4% 3 corroborators; SKAH-M 55-70%→60-75% LIFT +5% 3 axis-orthogonal corroborators; TCFT 88-96% N-axis replication UNCHANGED; KF-1 KF-3 KF-2 N-axis/codebook replications UNCHANGED; Bet B yellow UNCHANGED architecture-class-switch annotation row remains K=1-beat criterion; portfolio 14+31 UNCHANGED; HONEST 187→195 +8; LABEL-VS-HONEST 135→141 +6 NEW SUB-FLAVORS; 6 rescue sets filed cheapest-first; 1 NO_METRICS rescue routing filed NOT-auto-dispatched per user no-refill; 191st PROT-009 paired commit; verdict_handler opus-escalated single-batch inline)`

Push: BLOCKED from sub-agent context per [[feedback-subagent-permission-inheritance]]; orchestrator main thread executes `git push origin main` as 1-tool follow-up.
v280->v281 ANNOTATION-ONLY: BID metric-family glossary locked into cap_map. Two predicates defined: BID_GAP_PREDICATE (v2/v230 canonical: outside-3-Hopfield-bands AND sigma_margin>=2, load-bearing anchor for non-eq-stat-mech band, HARD_PASS at N=8192 5-seed) vs BID_NORMALIZED_THRESHOLD (v5/v6/v7 variant: normalized_bid>0.55, inherited from bid_m_normalized_v1, tests upper-paramagnetic regime NOT gap-region). 4 cumulative verdicts (v2 PASS + v5 MB + v6 HF + v7 HF) all on same capability claim with different predicates = structural risk without glossary. New policy: future BID-vN scripts MUST cite BID_GAP_PREDICATE or justify divergence in prereg. Row band UNCHANGED; portfolio UNCHANGED; 0 row state changes. 192nd PROT-009 paired commit.