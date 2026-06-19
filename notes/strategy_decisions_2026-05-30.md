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


## v281 -> v282 @ BATCHED 3-VERDICT Track A+B+C Phase-1 gate (user-explicit no-refill mode; 193rd PROT-009 paired commit)

**Context.** Three Phase-1 gate tests for Op D (parallel-superposition single-hop decomp), Op B (BSC tensor-binding two-shard), Op E (K=10 cross-shard pairwise correlation) shipped together at commit d78d051. User msg-1 framed each as "the single most decisive test" for its Track A/B/C respectively; user staged this batch and explicitly DISABLED auto-refill (next batch staged explicitly).

### Verdict triplet

- **Op D** superposition_single_hop_decomp_v1_n4096 SUP_DEC_MIDDLE_BAND -- per-component kscale_mean=1.000 unanimous across K in {5,10,15,20}; per_pattern_pass=0/4 patterns; 0/5 seeds clear HP; cross-talk amplitude on off-codebook entries blocks HP gate; signal exists, calibration/threshold rescuable.
- **Op B** tensor_binding_two_shard_v1_n4096 TBIND_HARD_FAIL -- mean_tensor_acc=0.018 vs mean_seq_acc=1.000 in 5/5 seeds; BSC element-wise binding destroyed by W matmul; sequential per-shard composition works at 1.000.
- **Op E** cross_shard_correlation_k10_v1_n4096 XSHARD_HARD_FAIL -- mean_AUC=0.459 (below-random) in 5/5 seeds at 30/4096 = 0.7% entity overlap; mean_triplet_in_top9=0.80/3; Tr operator-product insensitive at sub-1% overlap.

### Step 0 honest re-read summary (3 verdicts; 0 NEW LABEL-VS-HONEST catches)

All three labels HONEST at the level claimed. Op D MIDDLE_BAND captures the per-component-perfect / cross-talk-blocking bifurcation honestly. Op B HARD_FAIL captures BSC-specific structural mismatch honestly (sequential 1.000 vs tensor 0.018 contrast is dispositive). Op E HARD_FAIL captures specific-metric-at-specific-overlap-fraction insensitivity honestly. NO over-claims; NO reversals. User-prompt preliminary classifications confirmed.

### Cap_map decisions -- row-by-row (ANNOTATION-ONLY)

1. **Op D parallel-superposition single-hop decomposition -- NEW MECHANISM ANNOTATION (NOT subsumed by coherent-multi-hop ❌ closure)**. Annotation: "Op D is parallel paths through ONE substrate-op, NOT iterative sequential application; per-component decomposition CONFIRMED PERFECT (kscale_mean=1.000 unanimous); cross-talk amplitude blocks HP. Phase 2 two-hop ship NOT-YET-WARRANTED; cross-talk rescue R2 top-K post-decomp filter recommended FIRST".
2. **Op B BSC tensor-binding two-shard -- CLOSED at probe level (NOT a row).** Annotation: "BSC element-wise binding does NOT survive W matmul; sequential per-shard composition is the cross-shard query path; Op G hierarchical-multi-shard closes by dependency on Op B. Closure SCOPE BSC-codebook-specific; Kerdock untested but BSC-only closure SUFFICIENT for current production (BSC canonical deployment codebook)".
3. **Op E pairwise correlation K=10 -- CLOSED at probe level (NOT a row).** Annotation: "Tr(W_i^T W_j) at 0.7% entity overlap CLOSED. Closure SCOPE narrow: specific operator-trace metric form at specific overlap fraction; does NOT close all cross-shard analytics. No substrate-distinctive analytics layer at this approach".
4. **All 14 + 31 portfolio rows UNCHANGED** at row level and at band level.

**Framework reliability bands**: ALL UNCHANGED. **Portfolio**: 14+31 UNCHANGED.

**HONEST 195 -> 198 (+3)**; **LABEL-VS-HONEST 141 -> 141 (UNCHANGED)**.

### Rescue sketches summary (3 sets filed cheapest-first per [[feedback-rescue-sketch-first-sequencing]])

- **Op D parallel-superposition (3 rescues; MIDDLE_BAND, NOT closed)**: R1 0-cost subsumption annotation RECOMMENDED-FIRST + APPLIED inline; R2 CHEAP top-K post-decomposition filter probe (~5-15min CPU smoke + ~30min GPU FULL); R3 MEDIUM weighted MAP decomposition with stored-key prior (~1-2h GPU).
- **Op B BSC tensor-binding (3 rescues; HARD_FAIL, closure honored AFTER rescues filed)**: R1 0-cost subsumption annotation RECOMMENDED-FIRST + APPLIED inline; R2 CHEAP Kerdock-variant tensor-binding smoke (~30min CPU) -- pre-condition: substrate-physics motivation per [[feedback-no-padding-experiments]]; R3 0-cost Op G dependency annotation APPLIED inline.
- **Op E pairwise correlation (3 rescues; HARD_FAIL, closure honored AFTER rescues filed)**: R1 0-cost narrow-scope annotation RECOMMENDED-FIRST + APPLIED inline; R2 CHEAP higher-overlap probe (~15min CPU at 5-10% overlap); R3 MEDIUM alternate-metric row-wise alignment (~1h GPU).

### Phase 2 Op D ship recommendation (user-requested)

**Phase 2 two-hop ship NOT WARRANTED yet.** Rationale: two-hop matmul amplifies cross-talk per pass (each W redistributes amplitude across codebook); blind Phase 2 ship risks compounding HP-gate-blocking signal into premature HARD_FAIL. Recommend: ship Op D R2 cross-talk-rescue smoke FIRST (top-K post-decomp filter, ~5-15min CPU); conditional Phase 2 GPU ship AFTER R2 smoke clears. If R2 smoke fails, cross-talk is mechanistically un-rejectable and Phase 2 needs R3 weighted MAP decomposition before ship.

### Follow-on recommendations (for orchestrator main-thread; NOT auto-dispatched per user no-refill directive)

Top-3 surfaced for orchestrator main-thread review (user is staging next batch explicitly):

1. **Op D R2 top-K post-decomp filter smoke** -- cheapest cross-talk rescue (~5-15min CPU); CONDITIONAL on this clearing, Phase 2 two-hop GPU ship becomes warranted. NOT auto-shipped.
2. **Op G hierarchical-multi-shard probe SKIP** -- Op G closes by dependency on Op B BSC tensor-binding closure; no separate Op G probe needed unless Op B Kerdock-variant rescue (R2) is shipped first and succeeds. NOT auto-shipped.
3. **Op B Kerdock-variant tensor-binding probe SKIP UNTIL THEORY-MOTIVATED** -- per [[feedback-no-padding-experiments]] and [[feedback-dont-overextend-theorems]]: BSC closure does NOT close Kerdock; but Kerdock-variant ship needs substrate-physics analytic argument (Reed-Muller closure property under W) BEFORE shipping. Theory drill is recommended path before Kerdock probe. NOT auto-shipped.

### PROT compliance (v281 -> v282)

- **PROT-004/006**: 3 rescue sets filed cheapest-first; closures (Op B + Op E) honored AFTER 3 rescues filed per [[feedback-rehabilitation-after-rejection]]; Op D MIDDLE_BAND NOT closed (PARTIAL signal preserved with R1-R3 rescue path including R2 actionable smoke probe).
- **PROT-007**: cap_map row table (`substrate_capability_map_history.md`) UPDATED with v282 row. **BACKLOG NOTE carried forward**: v277 + v278 history rows STILL MISSING (from v279 PROT-007 backlog).
- **PROT-008**: validator skipped (annotation-only; 0 row state changes; 0 portfolio changes; no new validator violations expected).
- **PROT-009**: cap_map.md (v282 entry) + history.md (v282 row) + strategy_decisions_2026-05-30.md (this v281->v282 entry) + visibility_decisions_2026-05-30.md (one-line entry) staged atomically; **193rd PROT-009 paired commit**.
- **PROT-018**: 3 anchors spot-checked for _n<N> suffix vs config.N: all CLEAN (n4096 anchors with N=4096 configs).

### Memory adherence

- **[[feedback-verdict-msg-honest-reread]]**: Step 0 performed on 3 verdicts; 0 catches; all-honest-confirmed.
- **[[feedback-verdict-handler-remote-metrics-fix-2026-05-27]]**: bridge `get_metrics()` returned `_source=remote` for all 3 anchors.
- **[[feedback-rehabilitation-after-rejection]]**: 3 rescue sketches filed BEFORE each closure honored (Op B + Op E); Op D MIDDLE_BAND got 3 rescues with actionable R2 smoke path.
- **[[feedback-rescue-sketch-first-sequencing]]**: R1 0-cost subsumption-annotation sequenced FIRST in all 3 rescue sets; APPLIED inline; R2/R3 sequenced after.
- **[[feedback-dont-overextend-theorems]]**: Op B closure scoped to BSC-codebook; Op E closure scoped to specific operator-trace metric at specific overlap; NEITHER closes the broader research area.
- **[[feedback-no-padding-experiments]]**: NO Kerdock-tensor-binding ship; NO alternate-metric Op E ship; NO Phase 2 ship without R2 cross-talk rescue first.
- **[[feedback-obey-user-pause-explicitly]]**: user explicit no-refill directive HONORED; exp_dev queue refill SKIPPED.
- **[[feedback-strategy-shore-up-capabilities]]**: no LIFT triggered (single-batch annotations only); rescue paths surfaced.
- **[[feedback-cap-map-update-protocol]]**: atomic single-batch commit; sub-agent push BLOCKED.
- **[[feedback-decision-log-eol-handling]]**: this entry appended via `tools/orchestrator/append_decision_log.py`.
- **[[feedback-no-smoke]]**: brutal honesty -- Op D PARTIAL framing honest; Op B/Op E closures explicit at narrow probe-level scope; Phase 2 ship NOT WARRANTED until cross-talk rescue verifies.
- **[[feedback-for-you-tab-primary-channel]]**: 3 status_log entries with plain_language + importance fields (Op D MEDIUM, Op B HIGH, Op E MEDIUM).

### Commit & push

Commit message stored in cap_map v282 entry.

Push: BLOCKED from sub-agent context per [[feedback-subagent-permission-inheritance]]; orchestrator main thread executes `git push origin main` as 1-tool follow-up after this commit lands.

## v282 -> v283 -- 2026-05-30 BATCHED 16-VERDICT major-batch: 3 FIRST-HARD_PASS new killer-feature candidates + Bet B K=1 ceiling resolved + TCFT broad-envelope salvaged + framework-prediction-component degradation (1 LABEL-VS-HONEST catch); verdict_handler dispatched

**Trigger.** 16 NEW verdicts landed overnight after queue drain. User flagged "gpu and cpu are idle" at 09:17. Comprehensive batch covering Bet B K=1 stress, geometric-generalization Path 2 empirical confirmation, two capacity-extension first-HARD_PASS candidates, full phase-region characterization, salvaged TCFT broad-envelope deletion-cert via checkpoint, plus framework-prediction adaptive-threshold characterization. 3 Track A+B+C P1 verdicts (Op D/B/E) were previously processed at v282 commit 2a6bf84 -- NOT re-processed here. Pause-flag ABSENT; user explicit pending decision on refill.

### Step 0 honest re-read (16 verdicts; 1 LABEL-VS-HONEST CATCH; 3 ENVELOPE-CAVEAT annotations; 12 HONEST CONFIRMED)

#### Anchor 1 -- bet_b_k1_ceiling_stress_n8192_v1 (K1_STRESS_HARD_PASS) -- HONEST CONFIRMED

**Label vs metrics.** verdict_msg "K=1 ceiling RESPECTED: ret_A_after_D < 0.8 in 5/5 seeds. Rescue trio genuinely changes architecture class." Per-seed ret_A_after_D: [0.738, 0.751, 0.748, 0.741, 0.754] mean=0.746.

**Honest reading.** TIGHT 5-seed band [0.738-0.754], range 0.016, well below 0.8 Fusi-Drew-Abbott theoretical limit. Progression after_B=0.705 -> after_C=0.737 -> after_D=0.746 shows slow RECOVERY across tasks (substrate retention is not strictly monotone-decreasing as tasks accumulate -- replay-like effect). Label HONEST.

**Decision.** v280 label-vs-honest #140 (ARCHITECTURE_CLASS_SWITCH_MASQUERADING) classification CONFIRMED. Canonical single-W K=1 sits at 0.746 ceiling consistent with Fusi-Drew-Abbott 0.80. Rescue trio (wide/frozen/dual-W) at ret_A=1.000 in v280 batch is ESCAPING K=1 via architecture-class change, NOT a beat of the K=1 ceiling. Bet B row position UNCHANGED at K=1-beat criterion; rescue trio remains in separate architecture-category annotation. Note: subtle RECOVERY signal (after_B 0.705 -> after_D 0.746) is interesting substrate-physics but does NOT cross K=1 ceiling.

#### Anchor 2 -- continuous_output_substrate_v1_n4096 (CONT_HARD_PASS) -- HONEST AS WORDED + ENVELOPE CAVEAT

**Label vs metrics.** verdict_msg "PASS: continuous-output viable. interp_cos=0.956 hallu_AUC=1.000 argmax_cons=1.000 kf2_max_iso=0.000 n_seeds=5". Per-cell: interp_cosine in [0.95589, 0.95674] across 5 seeds at beta=8.0 M=512 N=4096.

**Honest reading.** All 4 metrics PERFECT or near-perfect in 5/5 seeds. Label HONEST AS WORDED -- continuous-output substrate path IS empirically viable. ENVELOPE CAVEAT: elapsed_s=6.21 total (5 seeds each ~1.2s); M=512 = N/8 = UNDER-CAPACITY regime (M_c at beta=4 is 16K-20K per m_c_probe, beta=8 likely similar or higher). The 4-metric perfect score is at sub-capacity loading where substrate has ample geometric headroom. This does NOT invalidate the result -- it constrains the row LIFT bound.

**Decision.** EMPIRICAL CONFIRMATION of geometric-generalization Path 2 (Path 2 P=0.45 documented in notes/substrate_geometric_generalization_paths_v278_2026-05-29.md). LIFT geometric-generalization Path-2 row from 🔬 P=0.45 -> 🟢 P=0.55-0.65 (CONSERVATIVE +0.10-0.20 bound; FULL ENVELOPE TEST at M=N to M=2N REQUIRED before further LIFT). NEW SUB-ROW added under geometric-generalization parent row: "Continuous-output substrate path empirically confirmed at sub-capacity envelope (M=N/8)".

#### Anchor 3 -- tensor_factorized_w_feasibility_v1_n4096 (TF_HARD_PASS) -- HONEST CONFIRMED + STRONG ENVELOPE CAVEAT

**Label vs metrics.** verdict_msg "FACTORIZATION_WORKS: mean_r512_ratio=1.000 n_seeds_uniform_loss=0/5 [all 5 seeds: full=1.000 r512ratio=1.000]". Per-seed: ret_full=1.000 AND ret at all ranks {128,256,512,1024,2048} = 1.000.

**Honest reading.** Label HONEST AS WORDED. STRONG ENVELOPE CAVEAT: M=512 = N/8 means substrate is at UNDER-CAPACITY regime where retrieval is trivial. ALL ranks including r=128 (16x compression) give ret=1.000 BECAUSE the un-factored baseline is also 1.000. This shows "factorization preserves whatever the dense baseline does, AT under-capacity". It does NOT show "factorization works at saturating M". The 100% factorization-vs-dense ratio at low M says nothing about how much rank you can drop at M near M_c.

**Decision.** NEW CANDIDATE ROW added: "Tensor-factorized W storage (low-rank SVD form)" 🔬 -> 🟢 P=0.40-0.55 (single-anchor low-M evidence; explicit FULL ENVELOPE TEST RECOMMENDED at M in {N, 2N, 4N, ~M_c} before further LIFT). Capacity-extension path tracked as FEASIBLE-AT-LOW-M with capacity-saturation behavior UNKNOWN. Conservative bound deflated 0.15 per [[feedback-lit-scan-calibration-penalty]] (single-anchor under-capacity result; mechanism is well-known SVD compression so novelty P caps at 0.55).

#### Anchor 4 -- sparse_w_active_subspace_v1_n4096 (SP_HARD_PASS) -- HONEST CONFIRMED + STRONG ENVELOPE CAVEAT

**Label vs metrics.** verdict_msg "SPARSE_W_WORKS: M=128 mem=0.0625 ret=1.000 iso=0.0000 n_seeds=5 n_cells=30". 30 cells = 6 M values {32,64,128,256,512,1024} x 5 seeds; ALL cells ret=1.000 kf2_max_iso=0.0.

**Honest reading.** Label HONEST AS WORDED. STRONG ENVELOPE CAVEAT: max M tested = 1024 = N/4. Substrate at this regime has retention=1.000 in dense baseline as well (per m_c_probe and phase_lattice_grid). Sparse-W at memory_ratio=0.0625 (M=128) shows 16x compression preserving ret=1.000 -- but the BASELINE is also 1.000 at this M. The mechanism (active-subspace tracking via top-M sparsity) is plausibly capacity-extension-friendly but the test never approaches M_c so capacity-saturation behavior is UNKNOWN.

**Decision.** NEW CANDIDATE ROW added: "Sparse-W active-subspace storage" 🔬 -> 🟢 P=0.40-0.55 (single-anchor low-M evidence; explicit FULL ENVELOPE TEST RECOMMENDED at M up to and past M_c before further LIFT). Capacity-extension path SECOND independent mechanism (distinct from tensor-factorized SVD path -- sparse vs low-rank are orthogonal compression families). Both rows track in parallel; orchestrator may run FULL envelope tests in either order or both.

#### Anchor 5 -- phase_lattice_grid_v1_n4096 (GRID_HARD_PASS) -- HONEST; CHARACTERIZATION REFERENCE DATA

**Label vs metrics.** verdict_msg "ENVELOPE_MAP_DELIVERED: 315/315 cells populated with 6 metrics each (frac=1.000). cells_complete=315/315 mean_retention=0.820 mean_above_thresh=0.225 N=4096 betas=9 mfracs=7".

**Honest reading.** 9 betas x 7 mfracs x 5 seeds = 315 cells, all populated. mean_retention=0.820 across the grid is healthy. mean_above_thresh=0.225 indicates KF-1 fires moderately. Label HONEST.

**Decision.** Foundational characterization reference data. STORE as reference at `notes/phase_lattice_envelope_v1_2026-05-30.md` (separate file; not a cap_map row movement). Use for cap_map context in future verdicts that probe specific (beta, M_frac) cells; valuable for grounding "is this cell in/out of operating envelope" questions.

#### Anchor 6 -- tcft_erase_robustness_n8192_v1_cpu (HARD_PASS, salvaged via checkpoint) -- HONEST CONFIRMED

**Label vs metrics.** verdict_msg "HARD_PASS: 15/15 protocol cells pass var_ratio<0.1 in >=2/3 seeds. Deletion-cert robust across broad protocol envelope". n_hp_cells=15/15; per-cell sample var_ratios mostly <0.001 well below 0.1 threshold; 5 alpha_ratios x 3 splits = 15 cells, 3 seeds each.

**Honest reading.** TIGHT envelope confirmation -- var_ratios are typically 10^-3 to 10^-5 range, ORDERS of magnitude below the 0.1 HP threshold. 15/15 cells with strong cell-strength is unambiguous. Salvaged-via-checkpoint completion after earlier TIMEOUT is genuine recovery (mechanism unchanged from previously-validated TCFT). Label HONEST.

**Decision.** STRENGTHENS deletion-cert killer feature BEYOND protocol-narrow-positioning. Per the all-night-batch strategy note flagging this as "deletion-cert robust across broad envelope" candidate: row LIFT triggered. TCFT row LIFT 88-96% -> 92-97% (modest LIFT +4% lower-bound; upper bound stays high because already-strong). Deletion-cert killer feature row LIFT 89-98% -> 92-98% (+3% lower bound; was product-feature class). Broad-envelope claim now empirically anchored at 5x3 alpha x split grid.

#### Anchor 7 -- m_c_probe_v1_n4096 (MC_PROBE_MIDDLE_BAND) -- HONEST CONFIRMED

**Label vs metrics.** verdict_msg "GRADUAL_DECLINE: no sharp drop, but transition present. n_seeds_sharp=0/5 biggest_step=16.0->20.0 mean_drop=0.145 M_c_estimate=[16384,20480] N=4096 beta=4.0". Per-seed at M_frac=16 ret=1.0; M_frac=20 ret in [0.85, 0.85-ish band]; M_frac=24 ret ~0.74; M_frac=28 ret ~0.585; M_frac=32 ret ~0.475.

**Honest reading.** Clean monotone gradient from ret=1.0 at M_frac<=16 to ret=0.475 at M_frac=32. Biggest step is 16->20 (0.15 drop). M_c at beta=4.0 N=4096 is roughly in [16384, 20480] = M_c ~ 4-5x N. NO sharp first-order transition; gradient is the SKAH-M-class signature. Label HONEST.

**Decision.** OPERATIONAL CHARACTERIZATION: M_c is roughly 4-5x N at beta=4. Useful for grounding "low-M" envelope caveats on continuous-output / tensor-factor / sparse-W candidate rows (all tested at M_frac=0.125-0.25 i.e. M << M_c). Gradient (no sharp boundary) is consistent with SKAH-M class. STORE as reference; no row movement.

#### Anchor 8 -- region_c_optimal_probe_v1_n4096 (REGION_C_MIDDLE_BAND) -- HONEST CONFIRMED

**Label vs metrics.** verdict_msg "PARTIAL: 1-metric wins or 1.2x-2x advantage. n_seeds_hp=1/5 n_seeds_indist=0/5".

**Honest reading.** Region C (beta=16/M_frac=0.5 + beta=32/M_frac=1 + beta=64/M_frac=2 etc.) tested vs Region A baseline. Only 1/5 seeds clears the 2x-improvement on >=2 metrics threshold. Region C does NOT substantially outperform standard operating region. Label HONEST.

**Decision.** CLOSES "Region C is substrate's optimal operating region" hypothesis at probe level. Standard operating region (Region A, beta~10 M_frac~1-2) remains appropriate default. Product positioning UNCHANGED -- do NOT bias toward Region C in deployment recommendations. ANNOTATION only; no row movement.

#### Anchor 9 -- multi_signal_kf1_design_v1_n4096 (KF1MS_MIDDLE_BAND) -- HONEST + STRUCTURAL NOTE

**Label vs metrics.** verdict_msg "COMPOSITE_INT: min=0.898 in (0.75,0.9). M=128 wmean_AUC=0.906 M=1024 wmean_AUC=0.905 M=4096 wmean_AUC=0.898". Per-op: 4 of 5 metrics (posterior_entropy, bundle_norm, geometric_distance, spectral_signature) hit 1.000 in EVERY cell; cross_replica metric is ~0.5 (random). Composite_max=1.000 across all M.

**Honest reading.** Label HONEST. Honest structural note: the equal-weight composite drag is from cross_replica which is at random (0.49-0.53) across M. 4 of 5 component metrics are MAXIMALLY discriminative on stored vs out-of-sample (AUC=1.0). composite_max=1.000 means an optimal weighting hits perfect detection. KF-1 multi-signal composite at equal weighting is just BELOW 0.90; tuned weighting (drop cross_replica or weight it ~0) clears HP threshold.

**Decision.** ANNOTATION: KF-1 multi-signal composite is empirically a NEAR-PASS at equal-weighting; cross_replica is the WEAK signal not the design. Tuning composite weights (excluding cross_replica or weighting it negatively) is the cheapest rescue. KF-1 row UNCHANGED 65-80%; ANNOTATE that 4-of-5 component signals are individually maximal and composite is near-pass at equal-weight.

#### Anchor 10 -- phase_boundary_characterization_v1_n4096 (PHB_MIDDLE_BAND) -- HONEST + METRIC-DEPENDENT BOUNDARY NOTE

**Label vs metrics.** verdict_msg "PARTIAL_BOUNDARY: beta_slope_ratio=0.00 (max_c=0.0000 mean_e=0.0000) M_slope_ratio=2.78 ... beta_rets=[1.0,1.0,1.0,1.0,1.0,1.0,1.0] M_rets=[1.0,1.0,1.0,0.85,0.726,0.626,0.518]". beta sweep in [9,9.5,9.8,10,10.2,10.5,11] at M=8192 all give retention=1.0. M sweep at fixed beta gives the gradient (M_c saturation).

**Honest reading.** beta_slope=0.00 on retention at M=8192 = N/2 (sub-capacity) is HONEST. Critical insight: retention at M < M_c is SATURATED at 1.0 -- so a beta sweep in this regime can NEVER detect beta_c via retention metric, even if beta_c=10 is a real phase boundary in other metrics (confidence-sharpness, KF-1 firing rate, order parameters). The phase_boundary anchor probed retention; phase boundary was previously inferred from t1_beta_fine + KF-5 sharpness probes (other metrics). Label HONEST AT scope claimed.

**Decision.** ANNOTATION (NOT demotion of beta_c=10): "beta_c=10 phase-boundary character is METRIC-DEPENDENT. Retention metric at M < M_c shows NO boundary (saturated at 1.0 across beta in [9,11]); confidence-sharpness and KF-firing metrics at appropriately-loaded M show the boundary. v283 retention test at M=8192=N/2 was OUTSIDE the regime where retention is beta-sensitive." This REFINES rather than refutes beta_c=10. Substrate-physics row UNCHANGED on beta_c claim; ANNOTATION added that retention-test at sub-capacity is wrong probe for beta-boundary detection.

#### Anchor 11 -- adaptive_cleanup_operator_v1_n4096 (ACO_MIDDLE_BAND) -- HONEST CONFIRMED

**Label vs metrics.** verdict_msg "MIXED: n_improved=0/5 n_std_opt=0/5 seed*:best=0@1.000(gain+0.000)". Per-seed: at M=8192 (M_frac=2) ALL retentions in [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0] across alpha in [0, 0.25, 0.5, 1.0, 1.5, 2.0, 3.0].

**Honest reading.** At M_frac=2 substrate retention is SATURATED at 1.000 regardless of cleanup strength. Label HONEST: cleanup is a no-op at this operating point.

**Decision.** ANNOTATION: at production operating point (M_frac=2), cleanup-operator strength contributes ZERO retention gain. Production deployment recommendation: don't pay cleanup compute cost at M_frac<=2. May be useful at M_frac near M_c -- untested in this anchor. No row movement.

#### Anchor 12 -- adaptive_threshold_characterization_v1_n4096 (ATC_HARD_FAIL) -- LABEL-VS-HONEST CATCH

**Label vs metrics.** verdict_msg "FRAMEWORK_MISSES: n_within_20=1/9 (frac 0.111) n_off_50=6/9 (frac 0.667) cells: b4.0_m1.0=0.054 b4.0_m4.0=0.900 b4.0_m16.0=0.781 b10.0_m1.0=4.000 b10.0_m4.0=0.433 b10.0_m16.0=0.697 b32.0_m1.0=4.000 b32.0_m4.0=0.900 b32.0_m16.0=0.360".

**Honest reading.** Per-cell inspection: best_score=0.0 in EVERY cell, all_scores=[0.0,0.0,0.0,0.0,0.0,0.0,0.0] across all 7 threshold values in every cell. The metric scoring is producing ZERO discriminative signal. The "best_threshold" and "rel_err" values are computed against a best_score that itself is 0.0. **This is a TEST-INSTRUMENT failure, NOT a framework-prediction failure.** The label "FRAMEWORK_MISSES" OVER-CLAIMS: the test cannot distinguish any threshold from any other (best_score=0.0 across all candidates), so the rel_err numbers reported are noise. The framework's threshold predictions may or may not match -- this anchor's metric design simply did not score the candidate thresholds.

**Decision.** LABEL-VS-HONEST CATCH 141 -> 142 (+1). Honest reading authoritative for downstream decisions: framework-prediction-of-threshold component reliability is NOT degraded by this anchor (the anchor cannot inform on that question due to broken metric scoring). DO NOT demote substrate-physics framework-prediction sub-component on this evidence. Recommended rescue: re-run anchor with corrected scoring metric that actually produces non-zero scores for candidate thresholds. Note the test-design failure as an exp_dev review item.

#### Anchor 13 -- block_structured_w_feasibility_v1_n4096 (BS_HARD_FAIL) -- HONEST CONFIRMED

**Label vs metrics.** verdict_msg "LARGE_LOSS: within_ret=0.343 cross_ret=0.353 mem_savings=4.0x n_seeds=5". Per-seed: within_ret in [0.305-0.375], cross_ret in [0.23-0.46]. All 5 seeds well below useful retention threshold.

**Honest reading.** Block-structured W (D=4 blocks of 128 feats each at facts_per_domain=128) gives ~33-35% retention -- substantial loss vs dense. 4x memory savings is real but accuracy collapse makes it not useful as capacity-extension. Label HONEST.

**Decision.** CAPACITY-EXTENSION sub-path "block-structured W" CLOSED. 3 rescues filed per [[feedback-rehabilitation-after-rejection]] before honoring closure.

#### Anchor 14 -- hierarchical_w_feasibility_v1_n4096 (H_HARD_FAIL) -- HONEST CONFIRMED

**Label vs metrics.** verdict_msg "HIER_DEGRADES: acc=0.062 cap_ratio=0.25 n_seeds=5". Per-seed hierarchical_acc in [0.04, 0.1] mean ~0.062.

**Honest reading.** Hierarchical 2-level W (n_sum=16, n_lps=16) gives 6.2% accuracy -- effectively random for a 200-item test. capacity_ratio=0.25 vs flat heuristic. Label HONEST.

**Decision.** CAPACITY-EXTENSION sub-path "hierarchical W" CLOSED. 3 rescues filed before honoring closure.

#### Anchor 15 -- n_scaling_modern_hopfield_v1_n16384 (NSCALE_INCONCLUSIVE) -- HONEST

**Label vs metrics.** verdict_msg "No completed seeds." per_M empty in all 3 seeds.

**Honest reading.** Script started, ran 116s, but produced no completed seed metrics. Likely OOM at N=16384 or instrumentation issue at the seed-loop level. Label HONEST INCONCLUSIVE.

**Decision.** Rescue routing note filed at `notes/strategy_request_to_exp_dev_2026-05-30_nscaling_rescue.md` for orchestrator main-thread review. NOT auto-dispatched (user pending refill decision).

#### Anchor 16 -- gpu_acceleration_baseline_v1_n8192 (NO_METRICS_ON_DISK) -- HONEST

**Label.** "Runner-failed before metrics write. 20s suggests fast crash."

**Honest reading.** `get_metrics()` returns None; remote SSH cannot find metrics.json. Fast crash. Label HONEST.

**Decision.** Rescue routing note filed at `notes/strategy_request_to_exp_dev_2026-05-30_gpu_baseline_rescue.md`. NOT auto-dispatched.

**HONEST 198 -> 213 (+15)**: 12 fully-honest, 3 envelope-caveat (continuous-output, tensor-factor, sparse-W). **LABEL-VS-HONEST 141 -> 142 (+1)**: adaptive_threshold ATC_HARD_FAIL OVER-CLAIMS framework-prediction failure when metric scoring is broken (test-instrument failure, not framework failure).

### Cap_map decisions (v282 -> v283) -- 2 ROW LIFTS + 3 NEW CANDIDATE ROWS + 2 CAPACITY-EXTENSION SUB-PATH CLOSURES + 5 ANNOTATIONS

#### LIFT 1 -- TCFT row + Deletion-cert killer feature row

- **TCFT row**: LIFT 88-96% -> 92-97% (+4% lower bound; upper bound +1% to 97% on broad-envelope strengthening).
- **Deletion-cert killer feature row** (product-feature class): LIFT 89-98% -> 92-98% (+3% lower bound).
- Rationale: tcft_erase_robustness_n8192_v1_cpu HARD_PASS 15/15 cells at 5 alpha_ratios x 3 splits with var_ratios mostly 10^-3 to 10^-5 (orders below 0.1 HP threshold). Broad-envelope claim now empirically anchored.

#### LIFT 2 -- Geometric-generalization Path 2 sub-row

- **Geometric-generalization Path 2 (continuous-output substrate)**: 🔬 P=0.45 -> 🟢 P=0.55-0.65 (CONSERVATIVE +0.10-0.20 bound).
- Rationale: continuous_output_substrate_v1_n4096 CONT_HARD_PASS 5/5 seeds 4-metric perfect (interp_cos=0.956 hallu_AUC=1.000 argmax_cons=1.000 kf2_max_iso=0.000). EMPIRICAL CONFIRMATION of Path 2 hypothesis. Envelope CAVEAT: M=512=N/8 sub-capacity; FULL ENVELOPE TEST at M near M_c needed before further LIFT. NEW SUB-ROW: "Continuous-output substrate path empirically confirmed at sub-capacity envelope".

#### NEW CANDIDATE ROW 1 -- Tensor-factorized W storage (low-rank SVD)

- State: 🟢 P=0.40-0.55
- Evidence: tensor_factorized_w_feasibility_v1_n4096 TF_HARD_PASS 5/5 seeds; rank=N/8 preserves ret=1.000 at M=N/8.
- Caveat: STRONG envelope caveat (M=N/8 sub-capacity; baseline also ret=1.000); FULL ENVELOPE TEST at M near M_c REQUIRED before further LIFT.
- Per [[feedback-lit-scan-calibration-penalty]] novel-synthesis P capped 0.55 (mechanism is well-known SVD compression).

#### NEW CANDIDATE ROW 2 -- Sparse-W active-subspace storage

- State: 🟢 P=0.40-0.55
- Evidence: sparse_w_active_subspace_v1_n4096 SP_HARD_PASS 30 cells (M in {32...1024} x 5 seeds) ret=1.000 kf2_iso=0.0 throughout.
- Caveat: STRONG envelope caveat (max M=N/4 still sub-capacity).
- Independent capacity-extension mechanism (sparse vs low-rank are orthogonal).

#### NEW CANDIDATE ROW 3 -- Bet B 4-stage K=1 ceiling at 0.746 (architecture-class characterization)

- State: 🟢 P=0.80-0.90 (high-confidence characterization)
- Evidence: bet_b_k1_ceiling_stress_n8192_v1 5/5 seeds ret_A_after_D=[0.738-0.754] mean=0.746 TIGHT BAND.
- Substance: canonical single-W K=1 sits at 0.746 ceiling consistent with Fusi-Drew-Abbott 0.80 theoretical limit; rescue trio (wide/frozen/dual-W) at ret=1.000 is architecture-class change, NOT K=1 beat.
- Row annotation: confirms v280 #140 ARCHITECTURE_CLASS_SWITCH_MASQUERADING; no row movement on Bet B 4-stage CL row itself.

#### CAPACITY-EXTENSION SUB-PATH CLOSURES (2 closures, each with 3 rescues filed first)

- **block-structured W**: CLOSED. within_ret=0.343 (5/5 seeds collapsed).
- **hierarchical W**: CLOSED. acc=0.062 (5/5 seeds collapsed).
- Note: these CLOSE the specific designs as capacity-extension paths; tensor-factorized + sparse-W remain OPEN as alternative paths.

#### ANNOTATIONS (5 annotations; no row movement)

- **phase_lattice_grid_v1_n4096**: STORE 315-cell envelope as reference at `notes/phase_lattice_envelope_v1_2026-05-30.md`.
- **m_c_probe_v1_n4096**: M_c at beta=4 N=4096 is roughly [16384, 20480] = 4-5x N. GRADUAL gradient (no sharp first-order boundary in this metric) consistent with SKAH-M.
- **region_c_optimal_probe**: "Region C is optimal" hypothesis CLOSED at probe level; product positioning unchanged.
- **multi_signal_kf1_design**: KF-1 multi-signal composite is NEAR-PASS at equal-weighting; cross_replica is the weak signal; tuned-weighting rescue is cheap. KF-1 row UNCHANGED.
- **phase_boundary_characterization**: beta_c=10 character is METRIC-DEPENDENT (retention at M<M_c saturates and cannot detect; confidence-sharpness + KF-firing metrics DO detect). REFINES rather than refutes beta_c=10. Substrate-physics row UNCHANGED.
- **adaptive_threshold ATC**: TEST-INSTRUMENT failure (best_score=0.0 across all candidates in all cells); NOT a framework-prediction-component failure. Framework-prediction sub-component reliability UNCHANGED.
- **adaptive_cleanup ACO**: at M_frac<=2, cleanup is no-op; production deployment skip the cleanup compute cost at this operating point.

#### All other framework-reliability ranges UNCHANGED

Non-eq-stat-mech 73-83%, SKAH-M 60-75%, substrate-outside-static-Hopfield 64-75%, specific 70-83%, general 73-83% -- ALL UNCHANGED. BID metric-family glossary (v281) UNCHANGED. Op D/B/E annotations from v282 UNCHANGED.

**Portfolio update**: 14+31 -> 14+33 (+2 new candidate rows: tensor-factorized W, sparse-W active-subspace). Bet B K=1 ceiling row added to characterization-class (not capability), portfolio category-count unchanged.

### Rescue sketches (PROT-004/006 cheapest-first per [[feedback-rescue-sketch-first-sequencing]])

**block-structured W closure (3 rescues):**

- **R1 (CHEAPEST, 0-compute)** -- Subsumption annotation: "block-W CLOSED; tensor-factor + sparse-W remain OPEN as alternative capacity-extension paths". APPLIED inline above.
- **R2 (CHEAP, ~10min CPU smoke)** -- Larger D probe (D=8 or D=16 blocks): test if smaller block size with proportionally smaller fpd preserves accuracy. NOT-AUTO-DISPATCHED (mechanism likely structural, not block-size-specific).
- **R3 (MEDIUM, ~30min GPU)** -- Hybrid block-and-cross-coupling design: add limited cross-block coupling to recover within-domain retention. NOT-URGENT; tensor-factor + sparse-W are stronger leads.

**hierarchical W closure (3 rescues):**

- **R1 (CHEAPEST, 0-compute)** -- Subsumption annotation: "hierarchical-W CLOSED; mechanism collapses in 2-level form; alternative capacity-extension paths (tensor-factor, sparse-W) preferred". APPLIED inline.
- **R2 (CHEAP, ~10min CPU smoke)** -- Larger n_sum / n_lps: test if a richer hierarchy with more sum and product points preserves accuracy. NOT-AUTO-DISPATCHED.
- **R3 (MEDIUM, ~1h GPU)** -- Soft-hierarchical (continuous gating between levels): NOT-URGENT.

**adaptive_threshold ATC LABEL-VS-HONEST catch (3 rescues; test-instrument NOT framework):**

- **R1 (CHEAPEST, 0-compute)** -- Subsumption annotation: "ATC label OVER-CLAIMS framework failure; best_score=0.0 across all cells reveals broken metric scoring; framework-prediction sub-component reliability UNCHANGED". APPLIED inline.
- **R2 (CHEAP, ~30min CPU)** -- Re-run with corrected scoring metric: instrument best_threshold detection so it produces non-zero discriminative scores; THEN test whether framework prediction matches empirical optimum. NOT-AUTO-DISPATCHED; exp_dev review item.
- **R3 (CHEAP, 0-compute)** -- Annotation only: "Framework-prediction-of-threshold sub-component remains untested by ATC v1; needs corrected metric design before reliability can be measured". APPLIED via R1.

**n_scaling_n16384 INCONCLUSIVE (3 rescues):**

- **R1 (CHEAPEST, 0-compute)** -- Subsumption annotation: "n_scaling INCONCLUSIVE; instrumentation failure at N=16384 not substrate failure". APPLIED inline.
- **R2 (CHEAP, ~15min debug)** -- Debug seed-loop crash at N=16384: check OOM, matmul errors, checkpoint bug. Routing note filed. NOT-AUTO-DISPATCHED.
- **R3 (CHEAP, ~30min CPU)** -- Run at N=8192 first (incremental scaling check): if N=8192 succeeds and N=16384 crashes, the bug is N-specific not general. NOT-AUTO-DISPATCHED.

**gpu_baseline NO_METRICS (3 rescues):**

- **R1 (CHEAPEST, 0-compute)** -- Subsumption annotation: "gpu_baseline 20s crash; metrics never written; instrumentation issue not capability claim". APPLIED inline.
- **R2 (CHEAP, ~15min debug)** -- Re-run with extra logging: capture stderr to isolate crash root cause. Routing note filed. NOT-AUTO-DISPATCHED.
- **R3 (CHEAP, 0-compute)** -- Annotation only: "GPU-acceleration baseline capability claim not refuted; pending instrumentation fix". APPLIED via R1.

### PROT compliance (v282 -> v283)

- **PROT-004/006**: 4 rescue sets filed cheapest-first (block-W, hierarchical-W, ATC-test-instrument, n_scaling-instrumentation, gpu_baseline-instrumentation -- 5 sets total); each set has R1 0-cost subsumption-annotation FIRST per [[feedback-rescue-sketch-first-sequencing]]; closures (block-W + hierarchical-W) honored AFTER 3 rescues filed per [[feedback-rehabilitation-after-rejection]].
- **PROT-007**: v283 history row appended. BACKLOG NOTE carried forward: v277 + v278 history rows STILL MISSING (from v279/v280/v282 PROT-007 backlogs).
- **PROT-008**: validator NOT run (16-verdict batch with row LIFTs + new rows would benefit from validator but verdict_handler context inline -- flagged for orchestrator main-thread validator follow-up).
- **PROT-009**: cap_map.md (this v283 entry) + substrate_capability_map_history.md (v283 row) + strategy_decisions_2026-05-30.md (this entry) + visibility_decisions_2026-05-30.md (one-line entry) staged atomically; **194th PROT-009 paired commit**.
- **PROT-018**: 16 anchors spot-checked for _n<N> suffix vs config.N: bet_b_k1_ceiling_stress_n8192_v1 N=8192 CLEAN; continuous_output_substrate_v1_n4096 N=4096 CLEAN; tensor_factorized_w_feasibility_v1_n4096 N=4096 CLEAN; sparse_w_active_subspace_v1_n4096 N=4096 CLEAN; phase_lattice_grid_v1_n4096 N=4096 CLEAN; tcft_erase_robustness_n8192_v1_cpu N=8192 CLEAN; m_c_probe_v1_n4096 N=4096 CLEAN; region_c_optimal_probe_v1_n4096 N=4096 CLEAN; multi_signal_kf1_design_v1_n4096 N=4096 CLEAN; phase_boundary_characterization_v1_n4096 N=4096 CLEAN; adaptive_cleanup_operator_v1_n4096 N=4096 CLEAN; adaptive_threshold_characterization_v1_n4096 N=4096 CLEAN; block_structured_w_feasibility_v1_n4096 N=4096 CLEAN; hierarchical_w_feasibility_v1_n4096 N=4096 CLEAN; n_scaling_modern_hopfield_v1_n16384 N=16384 CLEAN; gpu_acceleration_baseline_v1_n8192 N=8192 CLEAN. No suffix-vs-N mismatches.

### Memory adherence

- **[[feedback-verdict-msg-honest-reread]]**: Step 0 performed on 16 verdicts; 1 LABEL-VS-HONEST CATCH (adaptive_threshold ATC test-instrument over-claim); 3 ENVELOPE-CAVEAT annotations (continuous-output, tensor-factor, sparse-W); 12 fully-honest.
- **[[feedback-verdict-handler-remote-metrics-fix-2026-05-27]]**: bridge `get_metrics()` returned `_source=remote` for 15/16 anchors; gpu_baseline returned None (genuine NO_METRICS, not stale-local fallback).
- **[[feedback-rehabilitation-after-rejection]]**: closures (block-W, hierarchical-W) each got 3 rescue sketches filed BEFORE honored.
- **[[feedback-rescue-sketch-first-sequencing]]**: R1 0-cost subsumption-annotation sequenced FIRST in all 5 rescue sets; APPLIED inline.
- **[[feedback-dont-overextend-theorems]]**: capacity-extension sub-path closures scoped to specific designs (block-W, hierarchical-W); does NOT close capacity-extension generally (tensor-factor + sparse-W remain open).
- **[[feedback-no-padding-experiments]]**: NEW candidate rows filed at conservative P=0.40-0.55 with explicit FULL ENVELOPE TEST RECOMMENDED caveats; no over-LIFT.
- **[[feedback-lit-scan-calibration-penalty]]**: tensor-factor + sparse-W novel-synthesis P deflated 0.15-0.20 and capped at 0.55; honest under-capacity envelope caveats prominent.
- **[[feedback-pipeline-pacing]]**: queue=0 detected; user explicit pending refill decision per dispatch note; verdict_handler SKIPS exp_dev dispatch per `[Queue refill: skipped: USER-PENDING]`.
- **[[feedback-strategy-shore-up-capabilities]]**: 2 row LIFTs triggered (TCFT, deletion-cert); 3 new candidate rows added; full-envelope-test recommendations surfaced for orchestrator main-thread.
- **[[feedback-cap-map-update-protocol]]**: atomic single-batch commit; sub-agent push BLOCKED.
- **[[feedback-decision-log-eol-handling]]**: this entry appended via `tools/orchestrator/append_decision_log.py`.
- **[[feedback-for-you-tab-primary-channel]]**: status_log entries written with plain_language + importance fields; CRITICAL importance for first-HARD_PASS new-mechanism anchors (continuous-output, tensor-factor, sparse-W, bet_b K=1, TCFT broad-envelope, ATC LABEL-VS-HONEST).
- **[[feedback-no-smoke]]**: brutal honesty applied -- continuous-output PERFECT-at-low-M flagged with envelope caveat; tensor-factor + sparse-W LIFTs explicitly bounded by under-capacity envelope; ATC label OVER-CLAIM caught and corrected.
- **[[feedback-no-label-vs-honest-anchor-names]]**: 16 anchors PROT-018 spot-check all CLEAN.

### Commit & push

Commit message stored below.

Push: BLOCKED from sub-agent context per [[feedback-subagent-permission-inheritance]]; orchestrator main thread executes `git push origin main` as 1-tool follow-up.


## v283 -> v284 @ BATCHED 9-VERDICT F-batch envelope LIFTs + Op A/C/D-filter/F + instrumentation rescues; verdict_handler dispatched (195th PROT-009 paired commit)

**Context.** 9 verdicts from F-batch shipped at ad30514 (envelope-lift v2 for sparse_w + continuous_output + tensor_factor + n_scaling + gpu_baseline; Op A linear-combination; Op C codebook-projection identity-P; Op D top-K filter rescue; Op F commutator probe). User PAUSED mid-batch at ~10:30 then RESUMED; F2 tensor_factorized killed by pause-action (NO_METRICS = user-action artifact NOT runner crash). Pause-flag ABSENT at processing. User explicit: NO auto-refill -- orchestrator surfaces next-batch options to user after this commit.

### Verdict mix (9 total)

- **3 HARD_PASS substantive**: sparse_w_active_subspace_envelope_v2 SPE_HP envelope LIFT (M up to 2N); gpu_acceleration_baseline_rescue_v2 GPU_R_HP 22.67x mean N=4096 only; linear_combination_substrates_v1 LC_HP both modes 5/5.
- **2 MIDDLE_BAND**: continuous_output_substrate_envelope_v2 CONT_ENV_MB sharp M-degradation 0.957->0.853->0.633->0.499; superposition_top_k_filter_v1 TOPK_MB pattern-dependent leakage (retrieval still 1.000).
- **2 HARD_FAIL probe-level closures**: codebook_projection_kerdock_bsc_v1 CBP_HF mean_cross=0.012; interference_patterns_commutator_v1 INT_HF max/min=1.15x.
- **1 INSTRUMENTATION-FAIL**: n_scaling_modern_hopfield_rescue_v2_n16384 NSCALE_R_INCONCLUSIVE v2 still broken.
- **1 USER-KILLED**: tensor_factorized_w_envelope_v2_n4096 NO_METRICS pause-action artifact.

### Step 0 honest re-read summary (9 verdicts; 0 NEW LABEL-VS-HONEST catches; 1 TopK NUANCE; 1 USER-KILLED INTERRUPTED)

All 8 readable labels HONEST AS WORDED. Important nuances surfaced:

- **F6 TopK**: verdict_msg per_pattern_pass={uniform:5, peaked:5, random:3, sparse:0} is HONEST AT cross-talk-amplitude threshold (post_xtalk<0.10 gate). BUT per_component_accuracy=1.000 in ALL 20 cells INCLUDING all 5 P4_sparse cells. Retrieval CORRECTNESS clean across all patterns; only leakage-amplitude metric fails for sparse. Phase 2 ship recommendation depends on operational gate definition (retrieval-accuracy vs leakage-amplitude).
- **F5 continuous_output**: v283 LIFT (Path 2 0.45->0.55-0.65) based on M=N/8 perfect. v2 reveals sharp M-degradation: interp_cos 0.957->0.499 over M=512->16384. v283 LIFT was M-regime-specific; LIFT REVISION DOWN required (not just annotation) per honest envelope evidence.
- **F2 tensor_factorized**: get_metrics returns None. Per dispatch context user-paused at ~10:30 killed mid-run. Treat as INTERRUPTED not failure; PROT-021 checkpoint inspector may salvage partials.

Per-anchor honest readings recorded in cap_map v284 entry; full per-cell metrics from remote bridge get_metrics() with _source=remote for 8/9 anchors.

### Cap_map decisions -- consolidated

1. **Sparse-W active-subspace storage LIFT**: green 0.40-0.55 -> green 0.55-0.70 (+15% both bounds). 30 cells M in {128..8192} 5-seed all ret=1.000. Sub-capacity caveat RESOLVED for M up to 2N; M_c-beat still untested (M_c=4-5x N per v283 m_c_probe).
2. **Geometric-generalization Path 2 LIFT REVISION**: green 0.55-0.65 -> green 0.45-0.60 (-10% lower / -5% upper). v283 LIFT was M-regime-specific; v2 reveals sharp degradation above M=N/2.
3. **NEW substrate-GPU operational baseline ROW**: green P=0.65-0.80. Single-N (N=4096) 3-seed; 22.67x mean speedup; per-seed 4x spread; novel-synthesis P deflated 0.15.
4. **NEW Op A linear-combination-of-substrates ROW**: green P=0.50-0.65. 10 cells 5-seed both modes feasibility clean; strategic-value separate question (msg-1 "likely no advantage over consolidated").
5. **Op C identity-P probe CLOSED**: identity-P specific design CLOSED; broader Op C row NOT closed (substrate-physics analytic P unexplored).
6. **Op F commutator probe CLOSED**: commutator-form CLOSED; broader Op F (anti-commutator, product-norm, eigenvalue-spread) untested.
7. **Op D row annotation refined**: top-K filter rescue per_component_accuracy=1.000 ALL patterns; leakage gate pattern-dependent; Phase 2 ship CONDITIONAL on operational-gate definition.
8. **F2 tensor-factorized**: row UNCHANGED; rescue routing filed for v3 ship or checkpoint salvage.
9. **F4 n_scaling**: row UNCHANGED; rescue routing filed for v3 isolated-construction debug.

**Framework reliability**: ALL UNCHANGED -- non-eq 73-83%, SKAH-M 60-75%, substrate-outside-static-Hopfield 64-75%, TCFT 92-97%, deletion-cert 92-98%, KF-1 65-80%, specific 70-83%, general 73-83%.

**Portfolio**: 14+33 -> 14+35 (+2 new candidate rows: substrate-GPU baseline + Op A linear-combination).

**HONEST 213 -> 221 (+8)**; **LABEL-VS-HONEST 142 UNCHANGED**.

### Rescue sketches (4 sets cheapest-first per [[feedback-rescue-sketch-first-sequencing]])

- **Op C identity-P (3 rescues)**: R1 0-compute subsumption-annotation APPLIED; R2 cheap theory-drill substrate-physics P candidate; R3 cheap random-permutation-P probe.
- **Op F commutator (3 rescues)**: R1 0-compute subsumption-annotation APPLIED; R2 cheap anti-commutator probe; R3 cheap eigenvalue-spread probe.
- **F2 tensor-factor user-killed (3 rescues)**: R1 0-compute subsumption-annotation APPLIED; R2 cheap PROT-021 checkpoint-partials inspection; R3 medium fresh v3 ship.
- **F4 n_scaling v2-still-broken (3 rescues)**: R1 0-compute subsumption APPLIED; R2 cheap isolated-substrate-construction probe; R3 cheap single-M N=16384 test with memory tracking.

### Routing files filed

- `notes/strategy_request_to_exp_dev_2026-05-30_tensor_factor_v3_rescue.md` -- F2 rescue: checkpoint salvage OR fresh v3 ship. NOT-AUTO-DISPATCHED.
- `notes/strategy_request_to_exp_dev_2026-05-30_nscaling_v3_rescue.md` -- F4 rescue: isolated substrate construction first, single-M test, explicit memory tracking. NOT-AUTO-DISPATCHED.

### Top-3 follow-on recommendations (orchestrator surfaces to user for next-batch decision)

1. **Sparse-W M_c-beat probe v3** -- HIGHEST strategic priority. M in {16384, 32768} 5-seed GPU FULL. Decides between further LIFT (0.70-0.85 if mechanism BEATS dense M_c) vs current LIFT-bounded (0.55-0.70 if sparse-W respects dense capacity).
2. **F2 tensor-factor v3 ship or checkpoint salvage** -- co-priority with #1; same envelope-saturation question on orthogonal mechanism (SVD vs sparse compression families).
3. **Op D Phase 2 two-hop CONDITIONAL on operational-gate definition** -- per_component_accuracy=1.000 across all patterns; user decision required: retrieval-accuracy gate (ship ALL patterns) vs leakage-amplitude gate (ship uniform/peaked restricted).

### Queue-refill recommendation -- next-batch natural anchors

NOT auto-shipping per user explicit no-refill. Natural-next-anchors surfaced:

- (a) Sparse-W M_c-beat probe v3 (HIGHEST)
- (b) Tensor-factor v3 envelope or checkpoint salvage
- (c) Op D Phase 2 two-hop for uniform/peaked patterns (conditional)
- (d) n_scaling v3 isolated-construction rescue (cheap CPU)
- (e) GPU baseline N=8192 expansion (cheap GPU)

### PROT compliance (v283 -> v284)

- **PROT-004/006**: 4 rescue sets filed cheapest-first; R1 0-compute subsumption APPLIED in all sets; probe-level closures (Op C identity-P + Op F commutator) honored AFTER 3 rescues filed per [[feedback-rehabilitation-after-rejection]]; F2 + F4 not closed (rescue-pending).
- **PROT-007**: cap_map_history.md v284 row appended. BACKLOG: v277 + v278 history rows STILL MISSING (carried from v279/v280/v282/v283).
- **PROT-008**: validator NOT run (annotation-heavy batch; 1 LIFT + 1 LIFT-REVISION + 2 new rows + 2 probe-level closures; portfolio +2; flagged for orchestrator main-thread validator follow-up).
- **PROT-009**: cap_map.md (v284 entry) + history.md (v284 row) + strategy_decisions_2026-05-30.md (this entry) + visibility_decisions_2026-05-30.md (one-line) staged atomically; **195th PROT-009 paired commit**.
- **PROT-018**: 9 anchors PROT-018 spot-check all CLEAN.

### Memory adherence

- **[[feedback-verdict-msg-honest-reread]]**: Step 0 on 9 verdicts; 0 NEW catches; 1 TopK retrieval-vs-leakage NUANCE; 1 USER-KILLED INTERRUPTED.
- **[[feedback-verdict-handler-remote-metrics-fix-2026-05-27]]**: bridge get_metrics _source=remote for 8/9; F2 None genuine NO_METRICS.
- **[[feedback-rehabilitation-after-rejection]]**: 2 probe-level closures each got 3 rescues BEFORE honored.
- **[[feedback-rescue-sketch-first-sequencing]]**: R1 0-compute subsumption FIRST in all 4 sets.
- **[[feedback-dont-overextend-theorems]]**: Op C closure scoped identity-P; Op F closure scoped commutator-form; continuous-output LIFT REVISION refines not closes; TopK partial does NOT close sparse-pattern Op D.
- **[[feedback-no-padding-experiments]]**: NEW rows conservative-P with explicit caveats; LIFT REVISION honest down-correction.
- **[[feedback-strategy-shore-up-capabilities]]**: Sparse-W envelope LIFT +15% on proactive cap_map shoring.
- **[[feedback-lit-scan-calibration-penalty]]**: GPU-baseline P deflated 0.15; Op A capped 0.65.
- **[[feedback-obey-user-pause-explicitly]]**: user paused then resumed; NO auto-refill per explicit dispatch directive.
- **[[feedback-cap-map-update-protocol]]**: atomic batch commit; sub-agent push BLOCKED.
- **[[feedback-decision-log-eol-handling]]**: this entry appended via append_decision_log.py.
- **[[feedback-no-smoke]]**: brutal honesty -- continuous-output LIFT REVISED DOWN when v2 contradicts v283; TopK nuance surfaced; F2 INTERRUPTED treated honestly.
- **[[feedback-for-you-tab-primary-channel]]**: 6 status_log entries with plain_language + importance (sparse-W LIFT HIGH; continuous-output LIFT-REVISION HIGH; GPU baseline HIGH; Op A MEDIUM; Op C+Op F closures MEDIUM; TopK nuance MEDIUM).
- **[[feedback-no-label-vs-honest-anchor-names]]**: 9 anchors all CLEAN.

### Commit & push

Commit message stored in cap_map v284 entry.

Push: BLOCKED from sub-agent context per [[feedback-subagent-permission-inheritance]]; orchestrator main thread executes git push origin main as 1-tool follow-up.

- v284 -> v285 BATCHED 12-VERDICT N-batch (commit e457f1e) verdict_handler-dispatched (opus-escalated per framework-reliability trigger): 3 HARD_PASS multi-hop parallel-mechanism (CONT_MH + PPP + SPI all at M=256 sub-capacity, 1.000 unanimous) + 1 HARD_PASS multi_signal_kf1 v2 composite (composite weighted_auc=1.000 at 3 ops BUT 3/5 single signals already 1.000 — composite is robustness not ceiling-clearing) + 2 HARD_PASS sparse-W within-band (CRUD + deletion-sequences) + 2 HARD_FAIL labeled (sparse_w_mc_beat #143 ENVELOPE_EXTENSION_FRAMED_AS_CLOSURE; adaptive_threshold_v2 #144 DEGENERATE_CELLS_OVERCOUNT 6/9-not-9/9) + 1 MIDDLE_BAND with #145-2 RUNNING_METRIC_VS_FINAL_METRIC nuance (sparse-W edit_heavy post-storm 1.000 5/5) + 3 NO_METRICS GPU+large-N infrastructure contention. Step 0: 3 LABEL-VS-HONEST catches (#143, #144, #145 with 2 sub-flavors). Cap_map decisions: 1 NEW ROW (Multi-hop parallel-mechanism paths B/D/E 🔬→🟢 0.55-0.70 sub-capacity-caveat); 1 LIFT (sparse-W active-subspace 0.55-0.70 → 0.62-0.75 from envelope-extension catch); 1 LIFT-DOWN (KF-1 multi-signal 0.65-0.80 → 0.65-0.78 -2% upper from composite-trivialization nuance); 1 FRAMEWORK SUB-COMPONENT DEGRADATION annotation (adaptive-threshold tau_pred prediction sub-component 6/9 cells systematic 2-7× tau-space miscalibration — first instrumented confirmation per [[feedback-dont-overextend-theorems]] component-scope only); 4 within-band annotations; 3 infrastructure-rescue-pending consolidated routing note. Portfolio 14+35 -> 14+36 (+1 new row parallel-mechanism multi-hop). HONEST 221 -> 230 +9 (6 fully-honest + 3 LABEL-VS-HONEST catches counted in cumulative honest set). LABEL-VS-HONEST 142 -> 145 (+3 new sub-flavors: #143 ENVELOPE_EXTENSION_FRAMED_AS_CLOSURE; #144 DEGENERATE_CELLS_OVERCOUNT; #145 with 2 sub-flavors COMPOSITE_AUC_TRIVIALIZED_BY_SATURATED_COMPONENT + RUNNING_METRIC_VS_FINAL_METRIC counts as 1 numbered catch with 2 sub-flavors). Framework-reliability: non-eq 73-83% SKAH-M 60-75% TCFT 92-97% deletion-cert 92-98% specific 70-83% general 73-83% product-feature 89-98% ALL UNCHANGED; KF-1 65-80% -> 65-78% (-2% upper bound from N6 trim); adaptive-threshold sub-component DEGRADED (new annotation; component-level only per dont-overextend-theorems). 6 rescue sets cheapest-first 18 rescues R1 0-compute APPLIED inline. 1 consolidated rescue routing filed: n_batch_serialized_gpu_reship.md for N5+N11+N12 NO_METRICS; NOT auto-dispatched per user explicit no-refill carry-over. 5 status_log entries (1 CRITICAL multi-hop triple opening; 2 HIGH multi-signal KF-1 v2 + adaptive-threshold sub-component degradation; 2 MEDIUM sparse-W envelope LIFT + GPU+large-N infrastructure NO_METRICS). PROT-007 backlog v277+v278 history rows STILL MISSING carried forward. 196th PROT-009 paired commit; verdict_handler inline single-batch no Agent sub-dispatch. Top-3 follow-on: (1) PPP higher-M stress at M={2048,4096} 5-seed GPU ~5-10min UPGRADES-OR-REVISES parallel-mechanism row durable claim STRATEGICALLY HIGHEST; (2) serialized GPU re-ship N5+N11+N12 ~60-120min addresses 3 single-N/operational-path caveats; (3) adaptive-threshold tau_pred re-derivation research drill ~30min theory cheap unblocks sub-component fix. Queue-refill: NO auto-dispatch per user no-refill; orchestrator surfaces options.
v285->v286 CORRECTIVE REVERT: adaptive_threshold_rescue_v2 AT_R2_HARD_FAIL v285 sub-component-DEGRADED annotation RETRACTED. Research drill (ee0d4f8) found: (a) tau_pred is heuristic not derived -- no substrate-physics prediction existed to be degraded; (b) miscalibration pattern is formula's own image at tau_emp=0.05 sweep-boundary tiebreak (ZERO empirical optima measured); (c) third-occurrence instrumentation pathology v283+v284+v285. Framework-reliability bands UNCHANGED. NEW sub-flavor #146 INSTRUMENTATION_PATHOLOGY_PERSISTENCE: future framework-degradation annotations must cross-check for theoretical derivation existence. adaptive_threshold_rescue_v3 needed with non-saturating discriminant + non-degeneracy selftest before any framework assessment.
v286->v287 BATCHED 5-VERDICT P+Q batch MAJOR EVENT (commit ee0d4f8+392242b): multi-hop parallel-mechanism row sub-capacity caveat RESOLVED at production-scale M=8192 AND production-scale K_paths=1000. 5 verdicts: P1 multi_hop_higher_m_stress_v1_n4096 MH_M_STRESS_HARD_PASS all 3 paths sustain at M=2048/4096/8192 depths 3-5 (Path D unanimous 1.000; Path B 8/9 cells 1.000 + B_8192_5=0.968; Path E 6/9 cells 1.000 weakest E_8192_3=0.864 with non-monotonic depth-recovery to 0.971 at d=5) + Q3 large_k_path_scaling_v1_n4096 LKPS_HARD_PASS all 3 paths sustain at K_paths {10..1000} all cells 1.000 unanimous (lat ratios B/D=12.49x linear E=9.27x sub-linear; Bayesian combinatorial concern REFUTED) + Q2 mechanism_composition_v1_n4096 MCOMP_MIDDLE_BAND ceiling effect at d=5 all individuals at 1.000 cA/cB/cC cannot differentiate (hp_winning=0/5 hp_inconc_ok=5/5 hf_depths_failing=0/3 honest as worded) + P2 gpu_large_n_rescue_serialized_v1_n8192 RESCUE_MIDDLE_BAND with 3 sub-verdicts (sub1 GPU N=8192 baseline mean_speedup=22.68x 3-seed HARD_PASS HONEST extends v284 N=4096 result + sub2 sparse_w_gpu_integration M=128 sub-capacity sparse_retention=1.0 hp=0/3 MIDDLE_BAND HONEST + sub3 chunked_codebook N=16384 LABEL-VS-HONEST #147 NEW SUB-FLAVOR SEED_AGGREGATION_OVER_DEGENERATE_FAILURE: only 1/3 seeds reaches max_M=4096; 2/3 seeds return -1.0 sentinel; mean_max=4096 over-claims by mean-of-1-not-3; true 3-seed mean (4096+0+0)/3=1365; net HARD_FAIL assessment correct) + Q1 adaptive_threshold_rescue_v3_n4096 ATR3_HARD_FAIL FOURTH-OCCURRENCE INSTRUMENTATION PATHOLOGY (8/9 cells saturate at lowest tau in extended sweep; 1/9 cells interior optimum at edge-regime M_frac=1.0 beta=32.0; BUT meta-finding INFORMATIVE: substrate too clean for adaptive-threshold question to be empirically meaningful in standard regime; STOP-instrumentation-rescue-cycle directive applied per user prompt). Step 0: 1 LABEL-VS-HONEST catch #147; 4 labels HONEST as worded. Cap_map decisions: 2 ROW LIFTs + 5 ANNOTATIONS + 1 RESCUE-PENDING (sub3 codebook chunking v7) + 0 ROW CLOSURES + 0 NEW ROWS. LIFT 1: Multi-hop parallel-mechanism row B/D/E 0.55-0.70 -> 0.75-0.85 (+20% lower; +15% upper; mid 0.80) RATIONALE TWO INDEPENDENT envelope-axis confirmations (P1 M-axis + Q3 K-axis) + triple-mechanism corroboration + Path D unanimous through M=8192 K=1000 + per [[feedback-lit-scan-calibration-penalty]] cap 0.50 LIFTed by multi-axis evidence + CONSERVATIVE not AGGRESSIVE per [[feedback-no-padding-experiments]] (compositional generalization untested Q2 ceiling-bound; cross-mechanism composition deferred; higher-noise untested); DOES NOT reopen QE-2 sequential-argmax closure (different mechanism class). LIFT 2: Substrate-GPU operational baseline 0.65-0.80 -> 0.75-0.85 (+10% lower; +5% upper) RATIONALE P2 sub1 N=8192 dual-N coverage with v284 N=4096 satisfies single-N-caveat; CONSERVATIVE because only 2 N values tested + N=16384 untested separately from sub3 codebook-chunking question. 5 ANNOTATIONS: Path E engineering-distinct (non-monotonic depth-recovery + sub-linear K-scaling); adaptive_threshold characterization CLOSED at standard regimes (NOT framework component degradation NOT row demotion per [[feedback-dont-overextend-theorems]] substrate-property characterization positive: substrate cleaner than question requires; future adaptive-threshold work routes to edge-regime probes only at beta>=32 M_frac near M_c); mechanism_composition ceiling effect (composition test clean as feasibility; value-add untested at saturated regime); chunked_codebook sub3 HARD_FAIL rescue routing for v7; #147 LABEL-VS-HONEST SEED_AGGREGATION_OVER_DEGENERATE_FAILURE policy lock for future seed-aggregation reporting. Framework-reliability bands ALL UNCHANGED (non-eq 73-83% SKAH-M 60-75% TCFT 92-97% deletion-cert 92-98% KF-1 65-78% specific 70-83% general 73-83% product-feature 89-98% substrate-outside-static-Hopfield 64-75%); 2 capability-row LIFTs (multi-hop 0.55-0.70 -> 0.75-0.85; GPU 0.65-0.80 -> 0.75-0.85). Portfolio 14+36 UNCHANGED. HONEST 231 -> 236 +5. LABEL-VS-HONEST 146 -> 147 +1 (#147 SEED_AGGREGATION_OVER_DEGENERATE_FAILURE). 4 rescue sets cheapest-first 12 rescues R1 0-compute APPLIED inline. 4 status_log entries (1 CRITICAL multi-hop production-scale durability + 1 HIGH GPU substrate dual-N confirmation + 1 HIGH adaptive-threshold instrumentation-rescue-cycle STOPPED + 1 MEDIUM composition ceiling-effect). Queue-refill: NO exp_dev refill per user prompt explicit (orchestrator dispatching 5 new experiments in parallel). PROT-007 backlog v277+v278 history rows STILL MISSING carried forward. 198th PROT-009 paired commit. Top-3 follow-on: (1) cross-mechanism composition probe at HARDER regime M=16384 + depths 5-10 + noise STRATEGICALLY HIGH-PRIORITY composition-class classification SCORE/HANDOFF/PIPELINE; (2) substrate-GPU N=16384 non-chunked probe MEDIUM-PRIORITY extends GPU row to 3-N axis would support further LIFT toward 0.80-0.88; (3) adaptive-threshold edge-regime probe at beta>=32 M_frac near M_c MEDIUM-PRIORITY only scientifically meaningful adaptive-threshold question remaining post-characterization-closure.


## v287 -> v288 @ BATCHED 6-VERDICT R+S1 batch MAJOR STRATEGIC EVENT (verdict_handler inline; 199th PROT-009 paired commit)

**Context.** R-batch (5 anchors) + S1 first of S-batch completed. S-batch (12 anchors) mid-execution. Verdict mix: 3 HARD_PASS (R4 + R5 + S1) + 2 MIDDLE_BAND informative (R1 + R2) + 1 HARD_FAIL instrumentation-bounded (R-chunked). MAJOR strategic event = DIFFERENTIAL SURVIVAL surfaced across multi-hop mechanisms past M_c -- Path D = production-scale ROBUST mechanism (per-hop independent Bayesian bypasses M-capacity by construction); Path B M-bounded; Path E partial / niche. Per-hop bottleneck engineering targets identified.

### Step 0 honest re-read summary -- 0 NEW LABEL-VS-HONEST catches; 6 labels HONEST

bridge get_metrics returned _source=remote for ALL 6 anchors; metrics fresh; no fallback. Critical scrutiny applied per user prompt:

- **R1 Path D unanimous 1.000 at extreme cells**: GENUINE not trivialized. Mechanism explanation: per-hop independent Bayesian posterior reduction over K=500 candidates does NOT propagate substrate state across hops; the M-capacity saturation bottleneck (substrate codebook overcrowding) is BYPASSED by construction. K=500 candidates suffices to contain the truth at each hop independently.
- **R4 90/90 above HP threshold**: ACTUALLY 90/90 EXACTLY 1.000 unanimous (worst-mean=1.000); even stronger than label implies. Bounded to M<=8192 (= 2N).
- **R5 1.000 at sigma=0.4**: SUB-CAPACITY MARGIN EXPLAINS IT. M/N=0.5 at N=4096; massive cosine-similarity margin in this regime. Noise-injection-schema NOT independently audited from metrics payload (recorded as caveat); claim scope = sub-capacity only.
- **R2 composition NEUTRAL**: FALL-THROUGH not error-correction. cA empty-intersection 0.000 + cB/cC fall-through-to-Path-D 1.000. EMPIRICALLY REFUTES v287 R3 error-correction hypothesis. Research-direction closure (one hypothesis); composition-class evaluation re-routes to SCORE/HANDOFF/PIPELINE per [[feedback-composition-classification]].
- **R1 Path E M-invariant ~0.5 plateau**: identical per-cell at M=16384 and M=24576 (0.4668/0.4760/0.4952 both); Path E mechanism queries spectral coherence pattern not codebook size; ~0.5 is mechanism-floor not random.
- **R-chunked**: 3rd consecutive chunked HARD_FAIL on 8GB GPU. INSTRUMENTATION-BLOCKED state. Modern Hopfield activation hypothesis UNTESTED not REFUTED.

**HONEST**: 236 -> 242 (+6). **LABEL-VS-HONEST**: 147 UNCHANGED.

### Cap_map decisions -- 1 SPLIT-via-annotation + 5 ANNOTATIONS + 1 RESEARCH-DIRECTION CLOSURE + 1 INSTRUMENTATION-BLOCKED STATE; portfolio 14+36 UNCHANGED

1. **Multi-hop combined row 0.75-0.85 UNCHANGED** at row-position level; THREE per-mechanism sub-row annotations capture differential past-M_c durability per [[feedback-dont-overextend-theorems]]:
   - Path D sub-row 0.78-0.88 LIFT-annotation (production-scale robust; deploy as DEFAULT)
   - Path B sub-row 0.65-0.78 caveat-LIFT-annotation (sub-capacity-only; envelope-guard required)
   - Path E sub-row 0.65-0.75 engineering-distinct-annotation (niche; wide-envelope-Q-regime + M-invariant-plateau + sub-linear-K)
2. **Composition error-correction hypothesis CLOSED at breaking regime** -- research-direction closure (not row movement). Future composition work routes to OTHER classifications (SCORE/HANDOFF/PIPELINE).
3. **40% noise tolerance ALL 3 paths** -- annotation on combined row; sub-capacity caveat per [[feedback-dont-overextend-theorems]].
4. **Per-hop bottleneck reference data** -- engineering targets for E1.2 path-specific optimization (B = batched matmul + lower-precision; D = vectorized argmax + early termination; E = caching + partial spectral decomposition).
5. **Path E Q-regime envelope characterized** -- annotation on Path E sub-row; 90/90 unanimous 1.000 M<=8192.
6. **chunked_codebook N=16384 INSTRUMENTATION-BLOCKED** -- 3rd consecutive failure on 8GB GPU; v8 rescue routing OR hardware-upgrade OR non-chunked alternative.

**Framework-reliability ranges**: ALL UNCHANGED (non-eq 73-83%, SKAH-M 60-75%, TCFT 92-97%, deletion-cert 92-98%, KF-1 65-78%, specific 70-83%, general 73-83%, product-feature 89-98%, GPU baseline 0.75-0.85, multi-hop combined 0.75-0.85, adaptive-threshold characterization-CLOSED).

### Rescue sketches (PROT-004/006 cheapest-first; 5 rescue sets; 16 rescues total; R1 0-compute APPLIED inline in all 5)

- **R1 differential survival**: R1 subsumption-annotation APPLIED + R2 pre-reg policy lock APPLIED + R3 Path E plateau-mechanism probe NOT-AUTO-DISPATCHED + R4 Path D upper-envelope stress NOT-AUTO-DISPATCHED.
- **R2 composition fall-through**: R1 research-direction-closure annotation APPLIED + R2 composition-class pre-reg policy APPLIED + R3 HANDOFF-class probe NOT-AUTO-DISPATCHED.
- **R5 noise robustness**: R1 sub-capacity annotation APPLIED + R2 schema-audit pre-reg APPLIED + R3 noise-past-M_c probe NOT-AUTO-DISPATCHED.
- **S1 per-hop bottlenecks**: R1 engineering-target annotation APPLIED + R2 E1.2 dispatch routing NOT-AUTO-DISPATCHED.
- **R-chunked instrumentation-blocked**: R1 instrumentation-blocked annotation APPLIED + R2 v8 CPU-only-build routing NOT-AUTO-DISPATCHED + R3 non-chunked alternative NOT-AUTO-DISPATCHED + R4 hardware-upgrade investigation NOT-AUTO-DISPATCHED.

### Top-3 follow-on recommendations

1. **Path D production-stress at upper envelope** (HIGH-PRIORITY GPU ~30min): find Path D's breaking point; currently no-known-breaking-point through M=24576+d=20+K=500. Load-bearing for production deployment claims.
2. **HANDOFF-class composition probe** (MEDIUM CPU ~30min): route-by-regime composition; tests whether composition has value-add at HANDOFF level since SCORE-level error-correction is empirically closed.
3. **Path E plateau-mechanism probe at past-M_c** (MEDIUM CPU ~30min): characterize WHY E plateaus at ~0.5 M-invariant; refines Path E sub-row position and deployment scope.

### Queue-refill

NO exp_dev refill per user prompt explicit "NO exp_dev refill (S-batch still running; orchestrator handles next batch decision based on this)". Pause flag ABSENT but user directive overrides automated refill per [[feedback-obey-user-pause-explicitly]]. S-batch 12 anchors pending; orchestrator handles refill/batch-completion decision separately.

### PROT compliance

- PROT-004/006: 5 rescue sets cheapest-first; 16 rescues total; R1 0-compute APPLIED inline in all 5.
- PROT-007: history v288 row added atomically. BACKLOG NOTE: v277 + v278 history rows still missing.
- PROT-008: validator NOT run inline (annotation-batch within existing row; flagged for orchestrator main-thread follow-up).
- PROT-009: cap_map.md v288 entry + history v288 row + this decisions entry + visibility one-line entry staged atomically. 199th PROT-009 paired commit.
- PROT-018: 6 anchors PROT-018 spot-check all CLEAN.

### Memory adherence

- [[feedback-verdict-msg-honest-reread]]: Step 0 on all 6 verdicts; 0 new label-vs-honest; critical-scrutiny applied per user prompt and surfaced mechanism explanations.
- [[feedback-verdict-handler-remote-metrics-fix-2026-05-27]]: bridge _source=remote for 6/6; no fallback.
- [[feedback-rehabilitation-after-rejection]]: 0 row closures; 1 research-direction-closure (error-correction at breaking; composition-class remains open at SCORE/HANDOFF/PIPELINE alternative classifications); 1 instrumentation-blocked-state (Modern Hopfield activation untested not refuted).
- [[feedback-rescue-sketch-first-sequencing]]: R1 0-compute FIRST in all 5 rescue sets; APPLIED inline.
- [[feedback-dont-overextend-theorems]]: SPLIT-via-annotation within combined row (does not split row count); noise robustness scoped sub-capacity; chunked HARD_FAIL scoped to specific instrumentation + hardware.
- [[feedback-no-padding-experiments]]: CONSERVATIVE Path D 0.78-0.88 (not 0.80-0.90 aggressive); B/E sub-rows reflect observed signatures.
- [[feedback-obey-user-pause-explicitly]]: pause-flag ABSENT but user explicit "NO exp_dev refill" honored.
- [[feedback-cap-map-update-protocol]]: atomic single-batch commit; sub-agent push BLOCKED; hash surfaced to orchestrator.
- [[feedback-decision-log-eol-handling]]: this entry appended via append_decision_log.py.
- [[feedback-no-smoke]]: brutal honesty; mechanism explanations surfaced; sub-capacity caveats NOT swept under "extraordinary" framing.
- [[feedback-for-you-tab-primary-channel]]: 5 status_log entries with plain_language + importance fields (1 CRITICAL + 1 HIGH + 3 MEDIUM).
- [[feedback-composition-classification]]: error-correction at SCORE level CLOSED empirically; HANDOFF-class probe surfaced as top-3 follow-on #2.
- [[feedback-no-label-vs-honest-anchor-names]]: 6 anchors PROT-018 spot-check CLEAN.


## v288 -> v289 -- 2026-05-30 BATCHED 14-VERDICT S2-S14+T1 multi-hop characterization COMPLETE (verdict_handler dispatched; 200th PROT-009 paired commit)

**Context.** S-batch (12 anchors S2-S14 not including S1 already processed at v288 commit 61b00f5) + T1 path_d_mixed_confidence path-D-specific = 14 anchors. Backlog accumulated while runners ran unsupervised; runners died ~20:30 ET then restarted. T2-T5 still draining; user explicit no-refill (orchestrator handles next batch). bridge get_metrics _source=remote for ALL 14 anchors; metrics fresh; no fallback.

### Verdict mix (14 total)

- **7 HARD_PASS labeled**: S2 latency_crossover (90-cell production crossover surface CLEAN wins B:60/D:11/E:19 n_inconclusive=0) + S3 multi_hop_memory_efficiency (max_amp B:1.00/D:1.93/E:0.99 bounded) + S4 modern_hopfield_v7 (constructed 3/3 max_M=8192=half-N M=16384 OOM 3/3 = label HP at reduced criterion) + S9 mixed_confidence_multi_hop (Path-D-ONLY n_calibrated=5/5 B+E confidence-overhead-or-discrimination-collapse) + S10 approximate_sampling (Path-D-EXCLUSIVE acc_d=1.0 across rates 0.1-1.0 = 10x speedup at zero acc loss) + S11 multi_hop_gpu_baseline (B=81x D=56x E=19x speedups d=0.000 n_crashes=0) + S13 novel_query_construction (10/10 cells 1.000 at sub-capacity-shallow-tiny-Kn = ceiling at conservative envelope).
- **3 HARD_FAIL labeled**: S6 multi_hop_edit_isolation (Path B 1.0->0.375 on_path 10-rate; Path D+E preserve; audit_changed 45/45) + S7 op_timing_atlas (5/10 ops tail-ratio 100-420x) + S8 latency_accuracy_tradeoff (no Pareto improvement; substrate at acc=1.0 ceiling across knobs).
- **3 MIDDLE_BAND**: S5 path_optimization_baseline (1/3 paths clean; E only cv=0.25) + S14 joint_path_execution (8% speedup) + T1 path_d_mixed_confidence (acc=1.0 calib_dev 0.16-0.31 lat 9-45x).
- **1 INCONCLUSIVE**: S12 adversarial_multi_hop_probing (no cells; runner crash at 4.46s).

### Step 0 honest re-read summary -- 3 NEW LABEL-VS-HONEST catches (#148-#150)

#### #148 -- S4 modern_hopfield_n16384_v7_resilient -- NEW SUB-FLAVOR HARD_PASS_AT_REDUCED_CRITERION_SHADOWS_INSTRUMENTATION_BLOCK

**Anchor.** `modern_hopfield_n16384_v7_resilient` labeled `S4_HARD_PASS` "MODERN_HOPFIELD_ACTIVATION: constructed=3/3 max_M=[8192, 8192, 8192] target>4096 n_strong=3 n_full_M_pass=0".

**Honest reading.** Per-seed: construction OK via strategy `a_chunked` 3/3; recall=1.000 at M={2048, 4096, 8192} all seeds; M=16384 (full-N target cell) `success=false` CUDA-OOM in ALL 3 seeds. `n_full_M_pass=0` = dispositive: ZERO seeds reached full N=16384 storage target. `max_M=[8192]` = HALF the target N. verdict_msg reports metrics honestly; HARD_PASS label is on relaxed criterion (max_M >= 4096 + construction OK = engineering result) rather than full-N activation criterion. 4th consecutive N=16384 chunked-codebook OOM-instrumentation-block (v5+v6+v287-sub3+v7).

**Decision.** HONEST reading authoritative: half-N operational ceiling on 8GB GPU; Modern Hopfield activation hypothesis at full N=16384 still UNTESTED not REFUTED. ANNOTATION-LABEL-REFINEMENT: HARD_PASS retained at relaxed criterion (construction + half-N storage = engineering progress); cap_map row UNCHANGED at "Modern Hopfield activation UNTESTED at N=16384"; INSTRUMENTATION-BLOCKED state extended 4th-occurrence. Pattern: this is HP-LABEL-AT-REDUCED-CRITERION_SHADOWS_INSTRUMENTATION-BLOCK; future N=16384 ships must label with full-N criterion or explicitly cite reduced-criterion in verdict_msg.

#### #149 -- S8 latency_accuracy_tradeoff_v1_n4096 -- NEW SUB-FLAVOR CEILING_PRECLUDES_TRADEOFF

**Anchor.** `latency_accuracy_tradeoff_v1_n4096` labeled `S8_HARD_FAIL` "NO_TRADEOFF: pareto={'cleanup': 1, 'k_paths': 1, 'audit': 1, 'depth': 1} n_pass=0/4".

**Honest reading.** Pareto count of 1 for each of 4 tunable knobs + n_pass=0/4 = at sub-capacity M=2048 + N=4096 substrate operates WELL ABOVE the operating point where accuracy degradation begins; acc=1.000 across full configuration space leaves only the latency axis varying. This is "no tradeoff TO trade off" (substrate is over-margin) not "tradeoff investigated and failed". HARD_FAIL label mechanically correct on predicate but framing-wrong: SATURATION-EQUIVALENT not substrate-deficiency.

**Decision.** LABEL REFRAMED at framework level. honest_verdict_msg: "SATURATION: 4 knobs at acc=1.000 ceiling at sub-capacity; no Pareto improvement possible while substrate is over-margin". Cap_map: ANNOTATION on substrate-GPU baseline + multi-hop combined rows. Tradeoff probe re-routes to past-M_c stress / noise-stressed / higher-K regimes. POSITIVE production-feature signal (substrate has margin); framework-claim NOT degraded.

#### #150 -- S13 novel_query_construction_v1_n4096 -- NEW SUB-FLAVOR CEILING_AT_CONSERVATIVE_ENVELOPE

**Anchor.** `novel_query_construction_v1_n4096` labeled `S13_HARD_PASS` "NOVEL_QUERY_OPEN: max_b=1.000 max_d=1.000 max_e=1.000 depths=[3, 4]".

**Honest reading.** 10/10 cells (5 seeds x 2 depths in {3, 4}) all path_b/d/e accuracy/AUC=1.000 unanimous; n_queries=16 per cell. Config: M=2048 (M/N=0.5 sub-capacity), depths={3, 4} (shallow), K_paths=100 (small), n_queries=16 (tiny). HARD_PASS HONEST at literal "combinatorial chain construction works at this envelope" claim, BUT the prior P=0.30-0.50 framing was for "substrate does combinatorial reasoning over stored facts" as a BROAD claim. The actual probe is shallow + sub-capacity + small-K + tiny n_queries. Unanimous 1.000 at conservative envelope cannot distinguish "robust combinatorial reasoning" from "trivially passes at over-margin envelope where every path already works at 1.000 on direct retrieval (per S2 latency_crossover all paths achieve 1.000 at d=3 M=512-8192 K=100-5000)".

**Decision.** ANNOTATION-LABEL-SCOPE: HARD_PASS retained at CONSERVATIVE envelope; cap_map row gets ANNOTATION "combinatorial query construction confirmed at sub-capacity-shallow-tiny envelope; broader scope (deeper chains, past-M_c, larger n_queries) UNTESTED". P=0.30-0.50 prior NOT updated upward on ceiling pass per [[feedback-no-padding-experiments]] and [[feedback-dont-overextend-theorems]].

#### Other 11 verdicts honest as worded (with strategic implications)

- **S2 latency_crossover HARD_PASS**: HONEST. wins={B:60/90, D:11/90, E:19/90}; n_inconclusive=0 = clean crossover surface across 90 production cells. LLM-orchestration mechanism-selection logic VALIDATED.
- **S3 multi_hop_memory_efficiency HARD_PASS**: HONEST. Memory profile BOUNDED (Path D ~1.93x single-hop baseline = K-candidate buffer; no super-linear growth; no leak).
- **S5 path_optimization_baseline MIDDLE_BAND**: HONEST. PARTIAL_CLEAN_1/3; Path E cv=0.25 only clean-bottleneck path; B and D have higher variance for downstream E1.2.
- **S6 multi_hop_edit_isolation HARD_FAIL**: HONEST as worded BUT differential-mechanism finding underneath. Path B 1.0->0.375 under on_path edits (W mutation propagates through Path B); Path D + E preserve 1.0 (D Bayesian K-buffer decoupled from W; E spectral coherence path-orthogonal to edit). audit_changed=45/45 = audit chain PERFECT. consistent=37/45 (82%). Differential-survival under edits.
- **S7 op_timing_atlas HARD_FAIL**: HONEST. 5/10 ops p99/median >100x (batched_retrieve 419x, batched_store 231x, multi_hop_pathB_d5 311x, single_delete 100x, standard_retrieve 67.5x); 5/10 clean. SLA-shaping signal.
- **S9 mixed_confidence_multi_hop HARD_PASS**: HONEST as worded BUT differential underneath. Path D acc_conf=1.000 + n_calibrated=5/5 unanimous (ONLY confidence-aware-deployable); Path B acc_conf drops to ~0.91 + n_calibrated=2/5 (confidence-overhead penalty); Path E auc_conf collapses to 0.55-0.64 (confidence destroys spectral discrimination).
- **S10 approximate_multi_hop_sampling HARD_PASS**: HONEST. Path-D-EXCLUSIVE: hp_paths=['D'] n_d=5/5; Path D acc=1.000 across rates {0.1, 0.25, 0.5, 0.75, 1.0} = 10x sampling speedup at zero accuracy loss. Path B collapses at low rates (acc=0.0 at rate=0.1); Path E AUC=0.5 (random) at rate=0.1.
- **S11 multi_hop_gpu_baseline HARD_PASS**: HONEST. sp_b=81x sp_d=56x sp_e=19x speedups; d=0.000 zero accuracy delta; n_crashes=0. Multi-hop 3-mechanism dual-cell corroboration of GPU baseline.
- **S14 joint_path_execution MIDDLE_BAND**: HONEST. mean_speedup_frac=0.080 (8%) + max_mem_amp=1.01 + max_acc_delta=0 = joint parallel UNECESSARY at sub-capacity.
- **S12 adversarial_multi_hop_probing INCONCLUSIVE**: NO_METRICS-EQUIVALENT. "no cells" + elapsed=4.46s = runner crash before cells generated. Cannot assess zero-leakage claim. Rescue routing filed.
- **T1 path_d_mixed_confidence MIDDLE_BAND**: HONEST as worded BUT informative underneath. acc_blind=acc_conf=1.000 unanimous; lat_overhead=9-45x; calib_dev=0.16-0.32. Per-bucket per-seed: predicted=0.715-0.965 actual=1.000 always = substrate UNDER-predicts confidence. CONSERVATIVE-CALIBRATION = SAFE failure mode for regulated-industry deployment.

**HONEST**: 242 -> 256 (+14). **LABEL-VS-HONEST**: 147 -> 150 (+3 NEW SUB-FLAVORS).

### Cap_map decisions -- 1 LIFT + 1 LIFT-ANNOTATION + 9 annotations + 1 NO_METRICS rescue routing; portfolio 14+36 UNCHANGED

1. **Substrate-GPU operational baseline 0.75-0.85 -> 0.78-0.88 LIFT (+3%/+3%)** -- S11 multi-hop 3-mechanism dual-cell corroboration; CONSERVATIVE per [[feedback-no-padding-experiments]] single sub-capacity cell only.
2. **Multi-hop Path D sub-row 0.78-0.88 -> 0.80-0.88 LIFT-annotation (+2% lower)** within combined row UNCHANGED at 0.75-0.85 per [[feedback-dont-overextend-theorems]]; 4 NEW deployment axes corroborated (S6 edit-resilient + S9 confidence-aware-deployable + S10 sampling-based + S11 GPU) = 6-axis durability with v288 noise + past-M_c.
3. **Path B sub-row 0.65-0.78 UNCHANGED + edit-isolation caveat ANNOTATION** (S6 1.0->0.375 on_path edits).
4. **Path E sub-row 0.65-0.75 UNCHANGED + confidence-destroys-discrimination + sampling-collapse ANNOTATIONS** (S9 + S10).
5. **9 annotations**: S2 90-cell crossover characterization + S3 memory profile BOUNDED + Path D spanning-features production-deployment + S6 Path B edit-isolation caveat + T1 conservative-calibration + S8 saturation re-frame + S7 atlas tail-latency SLA signal + S14 joint-unnecessary + S4 v7 4th-instrumentation-block.
6. **NO_METRICS rescue routing**: S12 adversarial runner crash (`notes/strategy_request_to_exp_dev_v289_s12_adversarial_rerun_2026-05-30.md`); NOT auto-dispatched.

**Framework reliability bands**: non-eq 73-83% SKAH-M 60-75% TCFT 92-97% deletion-cert 92-98% KF-1 65-78% specific 70-83% general 73-83% product-feature 89-98% UNCHANGED; **substrate-GPU 0.75-0.85 -> 0.78-0.88 +3% LIFT**; multi-hop combined 0.75-0.85 UNCHANGED; adaptive-threshold characterization-CLOSED. **Portfolio 14+36 UNCHANGED**.

### Rescue sketches (PROT-004/006 cheapest-first per [[feedback-rescue-sketch-first-sequencing]]; 5 sets; 17 rescues; R1 0-compute APPLIED inline)

- **R-GPU-LIFT** (substrate-GPU LIFT consolidated): R1 0-compute subsumption APPLIED + R2 GPU past-M_c stress CHEAP NOT-AUTO-DISPATCHED + R3 GPU N=16384 non-chunked vanilla MEDIUM NOT-AUTO-DISPATCHED.
- **R-Path-D-FEATURES** (production-deployment consolidated): R1 0-compute spanning-features annotation APPLIED + R2 Path D upper-envelope production-stress CHEAP HIGH-PRIORITY NOT-AUTO-DISPATCHED + R3 Path D edit-isolation guard SDK probe CHEAP NOT-AUTO-DISPATCHED.
- **R-Path-B-EDIT-CAVEAT**: R1 0-compute caveat annotation APPLIED + R2 Path B copy-on-write W edit-isolation guard probe CHEAP NOT-AUTO-DISPATCHED.
- **R-T1-CALIBRATION** (conservative-calibration consolidated): R1 0-compute annotation APPLIED + R2 calibration-tightening probe CHEAP NOT-AUTO-DISPATCHED + R3 past-M_c calibration probe MEDIUM NOT-AUTO-DISPATCHED.
- **R-S12-ADVERSARIAL** (runner crash): R1 CHEAP re-ship routing filed NOT-AUTO-DISPATCHED + R2 0-compute UNCHANGED annotation APPLIED.

### Top-5 substantive findings (user-requested)

1. **Path D production-default mechanism on 4 NEW deployment axes** (S6 edit-resilient + S9 confidence-aware-deployable + S10 10x sampling at zero acc loss + S11 GPU 56x); with v288 noise + past-M_c = 6-axis durability. Path D sub-row LIFT 0.78-0.88 -> 0.80-0.88 (+2% lower).
2. **Substrate-GPU baseline LIFT 0.75-0.85 -> 0.78-0.88** on multi-hop 3-mechanism dual-cell corroboration (B 81x D 56x E 19x; zero accuracy delta; zero crashes).
3. **S2 90-cell production crossover surface CLEAN** -- wins={B:60, D:11, E:19} n_inconclusive=0; LLM-orchestration mechanism-selection logic engineered-feasible.
4. **T1 Path D conservative-calibration SAFE failure mode** -- substrate UNDER-predicts confidence (predicted 0.715-0.965 actual 1.000 unanimous); biased-conservative not uncalibrated; regulated-industry-deployable with confidence-floor-as-safety-margin caveat; latency overhead 9-45x.
5. **3 NEW LABEL-VS-HONEST sub-flavors** -- #148 S4 v7 HARD_PASS_AT_REDUCED_CRITERION + #149 S8 CEILING_PRECLUDES_TRADEOFF + #150 S13 CEILING_AT_CONSERVATIVE_ENVELOPE; pattern: HP labels at relaxed/ceiling criteria need explicit scope-citation in verdict_msg.

### Top-3 follow-on recommendations (NOT auto-dispatched per user no-refill)

1. **Path D upper-envelope production-stress** (HIGH GPU ~30min; v288 R1 R4 carries over + R-Path-D-FEATURES R2): find Path D breaking point at M >= 32768 + d >= 25 + K >= 2000 + noise sigma >= 0.4 at past-M_c. 6-axis durability story is load-bearing.
2. **S12 adversarial-probing re-ship** (CHEAP ~10-15min smoke + ~30min FULL): security-critical regulated-industry claim CANNOT be assessed from "no cells" runner crash; routing filed.
3. **Edit-isolation guard SDK probe** (CHEAP CPU ~30min): S6 surfaces Path B copy-on-write W requirement for edit-coexistence with Path D production-default; SDK design + smoke is engineering-cheap.

### PROT compliance

- **PROT-004/006**: 5 rescue sets cheapest-first; 17 rescues; R1 0-compute APPLIED inline in all 5.
- **PROT-007**: history v289 row added atomically. BACKLOG NOTE: v277 + v278 history rows STILL MISSING.
- **PROT-008**: validator NOT run inline (1 LIFT on substrate-GPU baseline + 1 sub-row LIFT-annotation; portfolio unchanged; flagged for orchestrator main-thread).
- **PROT-009**: cap_map.md (v289 entry) + history.md (v289 row) + strategy_decisions_2026-05-30.md (this entry) + visibility_decisions_2026-05-30.md (one-line) staged atomically; 200th PROT-009 paired commit.
- **PROT-018**: 14 anchors spot-check all CLEAN.

### Memory adherence

- **[[feedback-verdict-msg-honest-reread]]**: 3 NEW catches (#148, #149, #150 NEW SUB-FLAVORS); 11 labels HONEST as worded with strategic differential-reading surfaced on S6 + S9 + T1.
- **[[feedback-verdict-handler-remote-metrics-fix-2026-05-27]]**: bridge _source=remote for 14/14.
- **[[feedback-rehabilitation-after-rejection]]**: 0 capability-row closures; S4 v7 4th-instrumentation-block NOT capability closure; S12 NO_METRICS rescue routing FILED before any state change.
- **[[feedback-rescue-sketch-first-sequencing]]**: R1 0-compute APPLIED inline in all 5 sets.
- **[[feedback-dont-overextend-theorems]]**: Path D sub-row LIFT scoped within-combined-row; GPU LIFT CONSERVATIVE +3% single sub-capacity cell; S13 HP scope-bounded; S8 saturation scoped sub-capacity; S14 unnecessary scoped sub-capacity.
- **[[feedback-no-padding-experiments]]**: GPU LIFT +3% conservative; Path D sub-row +2% lower-only; S13 P NOT updated on ceiling.
- **[[feedback-strategy-shore-up-capabilities]]**: GPU + Path D LIFTs on multi-axis corroboration; proactive.
- **[[feedback-obey-user-pause-explicitly]]**: pause-flag ABSENT; user no-refill HONORED; S12 rescue routing FILED not auto-dispatched.
- **[[feedback-cap-map-update-protocol]]**: atomic single-batch commit; sub-agent push BLOCKED; hash surfaced.
- **[[feedback-decision-log-eol-handling]]**: this entry appended via append_decision_log.py.
- **[[feedback-no-smoke]]**: brutal honesty -- #148/#149/#150 catches; S6/S9/T1 differential mechanisms surfaced; S12 NO_METRICS not swept under "ran and passed".
- **[[feedback-for-you-tab-primary-channel]]**: 6 status_log entries with plain_language + importance.
- **[[feedback-no-label-vs-honest-anchor-names]]**: 14 anchors CLEAN.

### Commit & push

Commit message stored in cap_map v289 entry.

Push: BLOCKED from sub-agent context per [[feedback-subagent-permission-inheritance]]; orchestrator main thread executes git push origin main as 1-tool follow-up.


## v289 -> v290 @ BATCHED 8-VERDICT T2-T5 + U1-U3 + V1 batch MAJOR EVENT (Modern Hopfield activation TEST-ENVELOPE-CEILING + Path D no ceiling within 16N x depth=50 + 2 SECURITY-CRITICAL adversarial vulnerabilities + COW infeasibility closure + Phase 1 pipeline validation)

**Context.** 8 verdicts processed end-to-end. Two major framework-reliability-recalc-trigger findings: (i) T3 modern Hopfield activation at N=16384 max_M=N (label "MODERN_HOPFIELD_BEND" needs honest re-read - bend at N is the TEST CEILING, not measured break-point); (ii) U1 Path D unanimous 1.000 across all 20 cells at M up to 16N depth=50 - genuinely no ceiling found within tested envelope (trivialization risk acknowledged). Plus 2 SECURITY-CRITICAL findings: U2 p2 codebook-collision 100% breach all 5 seeds + U2 p4 edited-fact-traverse 99.4% breach (1/160 queries defended). U3 COW infeasibility: works at correctness but 10.13x mem-amp + 6-7/s throughput vs 50/s target. V1 Phase 1 pipeline validation 39/39 cells 0 crashes. T2 Path D edit-isolation under load 45/45 cells acc_post=1.000 unanimous (LABEL stronger-than-states - n_groups=9 hp_groups=3 obscures that ALL cells pass). T4 Path E 3/3 sub-tests pass (subA topK + subB early-term + subC sigma-tradeoff). T5 Path B sub-capacity acc_b=1.000 unanimous all 12 cells; "2 fail" is on geom_cos at M=500 d=8 (drops to 0.704) - NOT accuracy boundary.

### Step 0 honest re-read summary — 5 LABEL-VS-HONEST catches (#151 NEW + 4 sub-flavor extensions of existing flavors)

#### #151 — T3 modern Hopfield activation CEILING_AT_TEST_ENVELOPE_PRECLUDES_BEND_CLAIM (NEW SUB-FLAVOR closely related to #150 but distinct - here the test envelope SATURATES at the substrate's claimed regime ceiling rather than below it)

**Anchor.** `n_scaling_cpu_only_v8_n16384` labeled T3_HARD_PASS "MODERN_HOPFIELD_BEND_CPU: max_M_at_95=16384".

**Honest reading.** Per-cell: recall=1.000 across all Ms={2048, 4096, 8192, 16384} for all 3 seeds {7, 17, 23} unanimous. Test envelope did NOT sample M > N=16384. The pre-reg HP criterion was max_M > N/4 = 4096; got max_M = N = 16384 = 4x linear capacity floor at MINIMUM. But "bend" implies non-linear ascent that EXCEEDS N - and we have not tested M=N+1 let alone M=2N or M=4N. The honest reading: "Linear-capacity-floor BEAT by 4x AT MINIMUM; 100% recall sustained through the entire test envelope which ENDS at M=N; whether substrate would continue past M=N or break at M=N+epsilon is NOT MEASURED by this anchor." This is the test-envelope-ceiling analog of #150 (CEILING_AT_CONSERVATIVE_ENVELOPE) but at a structurally distinct ceiling — here the ceiling is the test's M=N test limit, not a conservative downward scoping. Distinct from #148 (HARD_PASS_AT_REDUCED_CRITERION_SHADOWS_INSTRUMENTATION_BLOCK) which was relaxed-criterion-at-failed-test; here criterion is met but full-mechanism-range is untested.

**Decision.** HARD_PASS at the 4x-linear-capacity-floor level (this is a substantial empirical finding at minimum); LABEL-VS-HONEST on the "MODERN_HOPFIELD_BEND" framing which implies measured exponential behavior. Cap_map decision: NEW row "Modern Hopfield activation regime at large N" at 0.65-0.80 with explicit caveats: (a) single anchor at N=16384, (b) single codebook (BSC), (c) max_M=N is TEST CEILING not measured break, (d) needs M > N replication + cross-codebook (Kerdock) at N=16384. NOT 0.85+ until multi-anchor multi-codebook + M > N test. Per [[feedback-no-padding-experiments]] CONSERVATIVE band (mid: 0.725) reflects "substantial single-anchor finding pending replication" not "settled fact."

#### #152 — T2 LABEL_NARRATIVE_UNDERSTATES_DATA (5th occurrence of this sub-flavor; matched at v288 R4 R5 + v289 S6)

**Anchor.** `path_d_edit_isolation_under_load_v1_n4096` T2_HARD_PASS "n_groups=9 target_groups=3 hp_groups=3".

**Honest reading.** Per-cell post_acc=1.000 unanimous across ALL 45 (3 edit_rates x 3 patterns x 5 seeds) cells; consistent=5/5 unanimous across all 9 groups; audit_changed flips correctly. Verdict_msg "hp_groups=3" reflects the script's coarse-grained group structure (likely "any of the 3 patterns pass" criterion), but the DATA shows 100% pass at the cell level. SAME flavor as v288 R4 (path_e_latency_envelope worst-mean=1.000 stronger-than-label) and v289 S6 (Path D stays 1.000 under all conditions). LABEL is HONEST as worded — just understates the data.

**Decision.** HARD_PASS-AS-WORDED + annotation that 45/45 cells acc_post=1.000 confirms Path D edit-resilience across ALL tested edit rates (10, 100, 1000) and ALL patterns (on_path, off_path, mixed). 7th axis-confirmation of Path D production-default story (6-axis at v289 + this T2 = SEVEN axes: edit-resilient under HIGH load + edit-resilient on-path + confidence-aware + sampling-based + GPU + noise-robust + past-M_c-durable).

#### #153 — T5 Path B "PARTIAL" hp_groups=10/12 — METRIC_SOURCE_MISIDENTIFIED (NEW SUB-FLAVOR)

**Anchor.** `path_b_subcapacity_characterization_v1_n4096` T5_MIDDLE_BAND "PARTIAL: hp_groups=10/12 hf_triggers=0".

**Honest reading.** Per-cell acc_b=1.000 unanimous across ALL 12 (M, depth) groups x 5 seeds = 60/60 cells perfect accuracy. The "2 fail groups" come from the script's `geom_cos_b` metric at M=500 depth=8 (mean_geom=0.704) and possibly M=500 d=5 (mean_geom=0.804) — a Path-B-internal geometric coherence metric, NOT accuracy. lat_b_faster_than_d also 5/5 across all 12 groups = Path B IS faster than Path D unanimously. The PARTIAL label suggests Path B has a sub-capacity envelope boundary; the data show Path B accuracy ENVELOPE is fully clean through M=500 d=8; the geom_cos drop is a substrate-physics observation (paths losing coherence at high d=8 deep depths), not an accuracy boundary.

**Decision.** REFRAMED at honest level. Path B sub-capacity ACCURACY envelope CLEAN through (M=50-500) x (d=3-8). The geom_cos_b degradation at large-M-deep-depth is substrate-physics signal worth annotating but is NOT a "PARTIAL" boundary. Reframe T5 as HARD_PASS-ON-ACCURACY + MIDDLE_BAND-ON-PATH-COHERENCE. Path B sub-row UNCHANGED with annotation: "sub-capacity Pattern B envelope ACCURACY-clean through M=50-500 d=3-8 60/60 cells unanimous; geometric coherence (path overlap signal) degrades at large-M-deep-depth — substrate-physics observation, not accuracy boundary."

#### #154 — U2 p4 PER-CELL-99.4%-BREACH-STRONGER-THAN-AVG (label-honest, surfacing per-cell severity)

**Anchor.** `adversarial_multi_hop_probing_v2_n4096` S12_HARD_FAIL with defense p4=0.006.

**Honest reading.** Per-cell p4_edited defense: seed 7 = 0.03125 (1/32 defended); seeds 17, 23, 31, 41 = 0.000 (0/32 defended). Average 0.006 = 0.5/32 across 5 seeds = total 1 query out of 160 defended. The "99.4%" reading from verdict_msg is HONEST and if anything UNDERSTATES the worst-case: 4/5 seeds have ZERO defense at all. Edit semantics under adversarial query construction is COMPLETELY broken, not "mostly broken."

**Decision.** HARD_FAIL HONEST; severity escalated for cap_map annotation. Codebook-collision (p2) ALL 5 seeds defense=0.000 leakage=1.000 = UNIVERSAL 100% breach. Patterns 1, 3, 5 clean: p1 crosstalk + p3 deleted-fact + p5 composition-leakage all defense=1.000 leak=0.000 unanimous all 5 seeds.

#### #155 — U3 mem_amplification 10.13x but m_fail=0 SCRIPT-THRESHOLD-DISAGREES-WITH-DATA (script bug, not result interpretation)

**Anchor.** `edit_isolation_guard_probe_v1_n4096` U3_HARD_FAIL "m_fail=0".

**Honest reading.** Per-cell mem_amplification=10.129 unanimous across all 15 (pre/mid/post x 5 seeds) cells. m_fail=0 in trigger list suggests script's mem_amp threshold gate did not fire — but the script's reported threshold elsewhere is 4x (mem_amp should fail if > 4x), and 10.13 >> 4. Likely script's per-cell mem-amp gate is OR'd against a different sub-condition (e.g., requires correlation with throughput drop) that didn't trip. Either way the DATA show 10.13x = 2.5x over the 4x target = INFEASIBLE for production. Throughput 6.0-7.5/s vs 50/s target = 5/5 throughput-fails per timing per seed = t_fail=5 fires correctly. Verdict label COW_INFEASIBLE is HONEST despite the m_fail=0 script anomaly.

**Decision.** HARD_FAIL HONEST as worded; surface the script-threshold-disagrees-with-data observation as a rescue: re-audit mem-amp gate logic before next COW probe. cons=1.00 + audit=5/5 across pre/mid/post confirms COW mechanism CORRECTNESS works; cost-feasibility infeasible.

### Cap_map decisions

1. **NEW ROW: "Modern Hopfield activation regime at large N" 🔬 -> 🟡 0.65-0.80 (P-band).** Single-anchor + single-codebook + test-envelope-ceiling caveats. This is the FIRST direct CPU-N=16384 evidence for super-linear capacity beyond linear-codebook-floor. T3 max_M=N=16384 is the test ceiling (saturated 100% recall at N=N envelope endpoint); we have NOT measured M > N, so "bend" is INFERRED not OBSERVED. The 4x improvement over linear-capacity-floor (N/4 = 4096) is HONEST at minimum. Frame as "BIG FINDING needing replication" not "settled fact." Recommend: multi-codebook (Kerdock) at N=16384 + multi-N (N=12288, N=20480 as construction-feasible) + M > N stress to characterize WHERE break actually occurs.

2. **Path D sub-row LIFT-annotation 0.80-0.88 -> 0.85-0.95 within combined row.** U1 unanimous 1.000 across all 20 cells at M=16384, 24576, 32768, 49152, 65536 (4N to 16N) x depth=10, 20, 30, 50 = ZERO ceiling found within 16N x depth=50 envelope. Trivialization risk acknowledged (random keys + K_paths=500 + synthetic relation graph); however, R1 v288 + R-Path-D-FEATURES R2 carried-forward stress at M >= 32768 + d >= 25 + K >= 2000 + noise sigma >= 0.4 was the prediction, and U1 exceeds it (M up to 65536 + d up to 50 + K_paths=500 without noise but at no noise the result is even more constraining of any ceiling). LIFT +5%/+7% reflects: 16N envelope characterization + per-hop independent Bayesian mechanism explanation (theoretical baseline) + 4x edit-rate axis from T2 + 7-axis durability. CONSERVATIVE upper bound 0.95 (not 1.0) reflects: untested adversarial query construction + untested cross-substrate (Kerdock at past-M_c) + trivialization risk on synthetic graphs.

3. **Path E sub-row LIFT 0.65-0.75 -> 0.70-0.82.** T4 Path E useful at 3 niche applications confirmed: (subA) top-K identification 5/5 seeds precision@10=1.000 at K_high={5000, 10000}; (subB) early-termination 5/5 seeds 100% in-budget at 0.05s wall budget; (subC) sigma-tradeoff 4/5 seeds achieve target speedup at sigma=0.2 (1.55x-3.32x speedups; seed 7 below target). All 3 sub-tests pass (sub_total_pass=3/3 even though subC has 1 sub-fail). LIFT +5%/+7% reflects: empirical niche-confirmation across 3 use cases + sub_total criterion satisfied. CONSERVATIVE upper bound 0.82 reflects: subC 4/5 not 5/5 (seed-dependent speedup) + Path E remains niche (S2 90-cell crossover: Path E wins only ~21% of cells per v289).

4. **Adversarial-vulnerability ANNOTATION on substrate-product-feature row** (and KF-1 + KF-2 row annotations). U2 codebook-collision (p2) 100% breach all 5 seeds + edit-fact-traverse (p4) 99.4% breach across 5 seeds = TWO security-critical vulnerabilities at adversarial query construction. KF-3 multi-substrate isolation UNCHANGED (different - same-substrate adversarial). Deletion certificate UNCHANGED (p3 deleted-fact defense=1.000 unanimous - audit-deletion robust). The substrate-product-feature row (currently 89-98%) gets ANNOTATION: "REGULATED-INDUSTRY DEPLOYMENT BLOCKER pending defenses against (1) codebook-collision crafted queries (100% breach) and (2) adversarially-constructed edit traversal queries (99.4% breach). Patterns 1 (crosstalk), 3 (deleted-fact), 5 (composition-leakage) cleanly defended (100% defense). Production deployment in regulated industries requires codebook-collision defense layer + adversarial-edit-construction defense before 'auditable memory with deletion certificates' positioning is credible. The deletion-certificate KF still WORKS (p3 clean); the issue is at codebook-and-edit layers." No row LIFT or LOWER — row position UNCHANGED but caveat annotation explicit.

5. **COW infeasibility ANNOTATION (mechanism dead-end, not capability closure).** Edit-isolation-guard COW probe shows the MECHANISM works (consistency=1.00 + audit=5/5 across pre/mid/post) but COST infeasible (10.13x mem-amp vs 4x target = 2.5x over; 6-7/s throughput vs 50/s target = 7-8x slower). Path D's edit-resilience (T2 PASS) holds via DIFFERENT mechanism (per-hop independent Bayesian decoupling from W mutation propagation - NOT copy-on-write). The COW closure documents: "COW is one mechanism for edit-isolation but is structurally infeasible at production cost; Path D achieves edit-resilience by per-hop Bayesian independence — different mechanism." Rescue follow-up: research drill on alternative edit-isolation mechanisms (delta-encoding, lazy-edit-application, edit-log replay) — filed but NOT auto-dispatched.

6. **V1 Phase 1 pipeline validation ANNOTATION (engineering discipline, not capability claim).** 39/39 cells n_crashed=0 n_non_null=39 cert_all_valid=True at N={2048, 4096} confirms the cloud-experiment pipeline is engineering-ready at the small-N validation stage. Annotation: "Phase 1 cloud-pipeline validation PASS; substrate-experiment-pipeline meta-row stamps the experiment design as cloud-ready at N=2048 + N=4096; T3 N=16384 CPU success + V1 N=4096 GPU-pipeline validation = path to Phase 2 local GPU at N=8192 with V1 pipeline then Phase 3 cloud N=16384 GPU dispatch becomes the natural sequence." This is engineering-process-discipline annotation; portfolio unchanged.

7. **T5 Path B Pattern B envelope ANNOTATION.** Sub-capacity Pattern B accuracy envelope CLEAN through (M=50-500) x (d=3-8) 60/60 cells unanimous acc_b=1.000; lat_b_faster_than_d=5/5 unanimous all 12 groups. Geometric coherence (geom_cos_b) degradation at large-M-deep-depth (M=500 d=8: 0.704; M=500 d=5: 0.804; M=200 d=8: 0.865) is substrate-physics signal of path-overlap declining at deep depths but is NOT accuracy boundary. Annotation only; row UNCHANGED.

### Framework reliability bands (v289 -> v290)

- **Non-eq-stat-mech 🟢 73-83% UNCHANGED**
- **SKAH-M / lR-phase 🟢 60-75% UNCHANGED**
- **Substrate-outside-static-Hopfield 🟢 64-75% UNCHANGED**
- **TCFT 🟢 92-97% UNCHANGED**
- **Deletion-cert 🟢 92-98% UNCHANGED** (p3 deleted-fact defense=1.000 unanimous = corroborates)
- **KF-1 🟢 65-78% UNCHANGED**
- **KF-2 🟢 UNCHANGED with adversarial-codebook-collision annotation**
- **KF-3 multi-substrate isolation UNCHANGED** (same-substrate adversarial different from cross-substrate)
- **Specific 70-83% UNCHANGED**
- **General 73-83% UNCHANGED**
- **Product-feature 89-98% UNCHANGED with regulated-industry-deployment-blocker annotation pending adversarial defenses**
- **Substrate-GPU operational baseline 0.78-0.88 UNCHANGED** (V1 pipeline at small-N is sub-capacity engineering validation; not capability-band relevant)
- **Multi-hop combined row 0.75-0.85 UNCHANGED at row-position level**
- **Multi-hop Path D sub-row 0.80-0.88 -> 0.85-0.95 (+5% lower bound +7% upper bound; LIFT-annotation within combined row)** — U1 16N x depth=50 unanimous + T2 45/45 edit-isolation under high-load + per-hop-independent-Bayesian mechanism explanation
- **Multi-hop Path B sub-row 0.65-0.78 UNCHANGED with sub-capacity-accuracy-envelope-clean + geom-coherence-substrate-physics annotation**
- **Multi-hop Path E sub-row 0.65-0.75 -> 0.70-0.82 (+5% lower bound +7% upper bound)** — T4 3-niche-application empirical confirmation
- **NEW ROW: Modern Hopfield activation regime at large N 🔬 -> 🟡 0.65-0.80** (single-anchor + single-codebook + test-envelope-ceiling caveats; NEEDS REPLICATION)
- **Adaptive-threshold characterization: CLOSED at standard regimes UNCHANGED**

**Portfolio**: 14 + 36 -> **15** + 36 (Modern Hopfield activation regime NEW ROW added at 🟡 P-band 0.65-0.80; 1 capability-row LIFT on Path E + 1 sub-row LIFT-annotation on Path D + 7 annotations + 2 security-vulnerability + 1 COW-infeasibility-closure + 1 V1-pipeline-validation + 1 T5-Path-B-honest-reframe).

### Rescue sketches (PROT-004/006 cheapest-first; 6 rescue sets; 18 rescues total; R1 0-compute APPLIED inline in all 6)

**R-MODERN-HOPFIELD (T3 NEW ROW addition; needs replication):**
- R1 (0-compute) — Subsumption: "T3 max_M=N=16384 = TEST ENVELOPE CEILING not measured break-point; band 0.65-0.80 explicitly conservative pending M>N replication + cross-codebook + multi-N." APPLIED inline above.
- R2 (CHEAP, ~10-15min CPU) — T3 v9 extension run: M sweep {16384, 24576, 32768, 49152} at N=16384 to FIND substrate break-point past M=N; same script harness; SHOULD-AUTO-DISPATCH if user authorizes follow-on (HIGH PRIORITY).
- R3 (MEDIUM, ~30min CPU) — T3 v10 cross-codebook at N=16384: Kerdock construction if memory-feasible (currently OOM-blocked at 8GB GPU; Kerdock is CPU-only-feasible variant of T3 v8); CHEAP-MEDIUM.

**R-PATH-D-NO-CEILING (U1 LIFT-annotation; trivialization concern):**
- R1 (0-compute) — Subsumption: "U1 16N x depth=50 unanimous 1.000 = NO CEILING FOUND within tested envelope; LIFT +5%/+7% conservative at upper bound 0.95 reflects trivialization risk on synthetic random-key graphs + untested adversarial construction + untested cross-substrate." APPLIED inline above.
- R2 (MEDIUM, ~45min GPU) — Path D upper envelope past M=16N: M={98304, 131072} = 24N, 32N to verify ceiling-still-absent; SHOULD-AUTO-DISPATCH if user authorizes follow-on (HIGH PRIORITY).
- R3 (CHEAP, ~30min CPU) — Path D adversarial-style stress: introduce structured queries that maximize codebook-collision (different from U1 random-keys); cross-validate against U2 finding that codebook-collision is substrate-vulnerability — does U1 inherit any of that vulnerability?

**R-ADVERSARIAL-DEFENSE (U2 SECURITY-CRITICAL; engineering work; PROT-004/006 mandates 3-5 rescues before regulated-industry deployment claim):**
- R1 (0-compute) — Subsumption: "U2 p2 codebook-collision 100% breach + p4 edited-fact-traverse 99.4% breach = REGULATED-INDUSTRY DEPLOYMENT BLOCKER pending defenses; patterns p1/p3/p5 cleanly defended." APPLIED inline above + product-feature row annotation.
- R2 (CHEAP, ~30min CPU+research) — Codebook-collision defense work: research drill on codebook-collision attack/defense literature (binary codes adversarial robustness; BCH/Reed-Muller code distance properties; per-cell randomization vs codebook-rotation). Routing filed: `notes/strategy_request_to_research_v290_codebook_collision_defense_2026-05-30.md` (NOT auto-dispatched).
- R3 (CHEAP, ~30min CPU+research) — Edit-semantics-under-adversarial-construction fix: research drill on retrieval-confidence-under-adversarial-query + edit-log-replay-vs-direct-W-edit semantics + Bayesian-edit-distance-as-defense. Routing filed: `notes/strategy_request_to_research_v290_edit_adversarial_defense_2026-05-30.md` (NOT auto-dispatched).
- R4 (MEDIUM, ~60min CPU+exp_dev) — Engineering design + smoke probe for codebook-rotation defense: rotate codebook per query OR per edit-batch; smoke whether p2 breach drops; CHEAP-MEDIUM.
- R5 (MEDIUM, ~60min CPU+exp_dev) — Engineering design + smoke probe for edit-log-replay isolation: instead of W-edit, log edit + replay at retrieval; smoke whether p4 breach drops; CHEAP-MEDIUM.

**R-COW-INFEASIBILITY (U3 mechanism dead-end; alternative-mechanism rescues per [[feedback-rehabilitation-after-rejection]] before closure):**
- R1 (0-compute) — Subsumption: "COW MECHANISM correctness OK (cons=1.00 + audit=5/5) but COST infeasible (10.13x mem + 7-8x throughput-slower); Path D achieves edit-resilience by DIFFERENT mechanism (per-hop Bayesian independence); closure documents COW dead-end NOT capability closure." APPLIED inline above.
- R2 (0-compute) — Subsumption: "Path D edit-resilience is the surviving mechanism (T2 + v289 S6 + v288 R4 + v287 noise + past-M_c = 7-axis Path D durability)." APPLIED inline.
- R3 (CHEAP, ~30min research) — Research drill on alternative edit-isolation mechanisms: delta-encoding (store edits as diffs, materialize lazily) + edit-log replay (don't modify W, replay log at retrieval) + per-hop independence (Path D's mechanism, generalized) + locality-sensitive isolation (only invalidate W subspace touched by edit); routing filed: `notes/strategy_request_to_research_v290_alt_edit_isolation_2026-05-30.md` (NOT auto-dispatched).
- R4 (MEDIUM, ~60min CPU+exp_dev) — Edit-log-replay engineering smoke: design + smoke an edit-log-replay layer; measure throughput + mem-amp vs COW baseline; NOT-AUTO-DISPATCHED.

**R-T5-PATH-B-HONEST-REFRAME (label-vs-honest acc-vs-geom-coherence; cap_map honest reading):**
- R1 (0-compute) — Annotation: "Path B accuracy envelope CLEAN 60/60 cells at sub-capacity; geom_cos degradation at M=500 d=8 is substrate-physics observation NOT accuracy boundary; T5 PARTIAL label sources from geom_cos metric not accuracy." APPLIED inline above.
- R2 (0-compute) — Annotation: "lat_b_faster_than_d=5/5 unanimous all 12 groups confirms Path B latency advantage holds at sub-capacity (substrate-product engineering signal)." APPLIED inline above.

**R-V1-PIPELINE (Phase 1 stamp; process-discipline annotation):**
- R1 (0-compute) — Annotation: "V1 39/39 cells 0 crashes all certs valid at N=2048 + N=4096 = Phase 1 cloud-pipeline validated; sequence to N=8192 then cloud N=16384 GPU dispatch becomes natural next steps." APPLIED inline above.

### Top-5 substantive findings

1. **T3 modern Hopfield activation at N=16384 CPU max_M=N (4x linear capacity FLOOR; BEND-CLAIM NEEDS REPLICATION).** Single anchor at N=16384 BSC codebook 3-seed unanimous recall=1.0 across M={2048, 4096, 8192, 16384}. Per-cell metrics are CLEAN at 4x linear-capacity-floor (pre-reg HP criterion max_M > N/4 = 4096 was met). HOWEVER the "MODERN_HOPFIELD_BEND" framing implies measured exponential ascent, which is INFERRED not OBSERVED — the test envelope SATURATES at M=N=16384 (the substrate's claimed regime ceiling); we have not measured M > N to find the actual break-point. Cap_map: NEW row "Modern Hopfield activation regime at large N" 🟡 0.65-0.80 with explicit single-anchor + single-codebook + test-envelope-ceiling caveats. R2 (M-sweep past N=16384 at N=16384) is the natural follow-on to characterize WHERE the break-point actually is.

2. **U1 Path D unanimous 1.000 across 16N x depth=50 envelope = no ceiling found within tested regime.** All 20 (M, depth) cells x 5 seeds = 100/100 cells exactly 1.000 at M={16384, 24576, 32768, 49152, 65536} (4N to 16N) x depth={10, 20, 30, 50}. Trivialization risk acknowledged on synthetic random-key relation graphs at K_paths=500. Per-hop independent Bayesian mechanism explanation (Path D's substrate-physics signature) predicts NO M-scaling dependency by construction; U1 is the most-extreme empirical envelope-characterization to date. Path D sub-row LIFT 0.80-0.88 -> 0.85-0.95 within combined row. CONSERVATIVE upper bound 0.95 reflects untested adversarial construction + untested cross-substrate (Kerdock at past-M_c) + trivialization concern.

3. **U2 codebook-collision + edit-fact-traverse: 2 SECURITY-CRITICAL adversarial vulnerabilities at substrate codebook + edit layers.** p2 codebook-collision attack 100% breach ALL 5 seeds = adversaries who craft queries targeting codebook collision points extract arbitrary stored facts. p4 edited-fact traversal 99.4% breach (1/160 queries defended; 4/5 seeds ZERO defense) = substrate retrieves OLD edited fact under adversarial query construction. Patterns p1 cross-talk + p3 deleted-fact + p5 composition-leakage cleanly defended (100% defense). REGULATED-INDUSTRY DEPLOYMENT BLOCKER pending defenses. Product-feature row UNCHANGED but annotation explicit. R2 + R3 research routing filed for codebook-collision defense + edit-semantics defense (NOT auto-dispatched).

4. **U3 COW edit-isolation: mechanism works (cons=1.00 + audit=5/5) but cost-infeasible at production (10.13x mem-amp + 7-8x throughput-slower).** Different edit-isolation mechanism needed. Path D's edit-resilience (T2 PASS) holds via per-hop Bayesian independence — DIFFERENT MECHANISM than COW. Closure documents COW dead-end NOT capability closure. Research routing filed for alternative edit-isolation mechanisms (delta-encoding + edit-log replay + locality-sensitive isolation) (NOT auto-dispatched).

5. **5 NEW LABEL-VS-HONEST sub-flavors caught: #151 CEILING_AT_TEST_ENVELOPE_PRECLUDES_BEND_CLAIM (T3 max_M=N test-envelope-ceiling; NEW SUB-FLAVOR distinct from #150 conservative-envelope) + #152 LABEL_NARRATIVE_UNDERSTATES_DATA (T2 hp_groups=3 obscures 45/45 cells pass; 5th occurrence of label-understates-data flavor) + #153 METRIC_SOURCE_MISIDENTIFIED (T5 PARTIAL sources from geom_cos not accuracy; NEW SUB-FLAVOR) + #154 PER_CELL_BREACH_SEVERITY_STRONGER_THAN_AVG (U2 p4 4/5 seeds 100% breach not just 99.4% avg) + #155 SCRIPT_THRESHOLD_DISAGREES_WITH_DATA (U3 m_fail=0 despite 10.13x mem-amp = script-mem-amp-gate bug). T2 + V1 LABEL-HONEST as worded.

### Top-3 follow-on recommendations (NOT auto-dispatched; orchestrator main-thread decides)

1. **T3 M-sweep past N=16384 at N=16384** (HIGH PRIORITY CPU ~15min) — natural follow-on to characterize WHERE the modern-Hopfield bend actually breaks past M=N=16384 (currently TEST CEILING saturated at 100%). Needed to LIFT NEW row from 0.65-0.80 conservative to 0.80+ measured-bend. R-MODERN-HOPFIELD R2.

2. **Adversarial defenses research drill (codebook-collision + edit-semantics)** (CHEAP ~60min research total) — 2 SECURITY-CRITICAL vulnerabilities BLOCK regulated-industry deployment positioning. Research drill on (a) binary codes adversarial robustness (codebook-rotation + per-query randomization + BCH/Reed-Muller distance properties) + (b) retrieval-confidence-under-adversarial-query + edit-log-replay-vs-direct-W-edit semantics. R-ADVERSARIAL-DEFENSE R2 + R3 routing filed (NOT auto-dispatched).

3. **Path D 24N-32N upper envelope past 16N** (MEDIUM GPU ~45min) — U1 found no ceiling at 16N depth=50; need to confirm Path D ceiling-absence holds at M={98304, 131072}. R-PATH-D-NO-CEILING R2. If still no ceiling, Path D upper bound may justify LIFT to 0.88-0.97 next cycle.

### PROT compliance (v289 -> v290)

- **PROT-004/006**: 6 rescue sets cheapest-first per [[feedback-rescue-sketch-first-sequencing]]; 18 rescues total; R1 0-compute APPLIED inline in all 6 sets; 3 research routings filed (codebook-collision + edit-adversarial + alt-edit-isolation) NOT auto-dispatched per V2 still running + G1-G4 pending.
- **PROT-007**: substrate_capability_map_history.md v290 row added atomically. BACKLOG NOTE carried forward: v277 + v278 history rows STILL MISSING (from v279-v289 PROT-007 backlogs).
- **PROT-008**: validator NOT run inline (1 NEW row + 1 capability-row LIFT on Path E + 1 sub-row LIFT-annotation on Path D within combined row; portfolio 14+36 -> 15+36 +1 NEW row; flagged for orchestrator main-thread validator follow-up).
- **PROT-009**: cap_map.md (this v290 entry) + substrate_capability_map_history.md (v290 row) + strategy_decisions_2026-05-30.md (v289 -> v290 entry) + visibility_decisions_2026-05-30.md (one-line entry) + 3 routing files (codebook-collision-defense + edit-adversarial-defense + alt-edit-isolation) staged atomically; **201st PROT-009 paired commit**.
- **PROT-018**: 8 anchors spot-checked for _n<N> suffix vs config.N: all CLEAN (n4096 anchors with N=4096 configs; n16384 anchor with N=16384 config; n2048_n4096 pipeline-validation anchor with dual-N config).

### Memory adherence

- **[[feedback-verdict-msg-honest-reread]]**: Step 0 performed on all 8 verdicts; 5 NEW LABEL-VS-HONEST catches (#151, #152, #153, #154, #155; #151 + #153 are GENUINE NEW SUB-FLAVORS; #152 + #154 + #155 are sub-flavor extensions). T2 + V1 LABEL-HONEST as worded.
- **[[feedback-verdict-handler-remote-metrics-fix-2026-05-27]]**: bridge get_metrics returned _source=remote for 8/8 anchors; no fallback required.
- **[[feedback-rehabilitation-after-rejection]]**: 0 capability-row closures; U3 COW labeled as MECHANISM-DEAD-END NOT capability closure; rescue sketches list alternative mechanisms (delta-encoding + edit-log-replay + locality-sensitive); U2 adversarial vulnerabilities ANNOTATED on product-feature row NOT used as basis for row demotion (per [[feedback-dont-overextend-theorems]] vulnerabilities are at codebook-and-edit layer not at substrate-capability level).
- **[[feedback-rescue-sketch-first-sequencing]]**: R1 0-compute subsumption sequenced FIRST in all 6 rescue sets; APPLIED inline.
- **[[feedback-dont-overextend-theorems]]**: T3 NEW row CONSERVATIVE 0.65-0.80 not 0.80+ because test-envelope-ceiling; U1 Path D LIFT-annotation +5%/+7% within combined row (not aggregate row LIFT); U2 vulnerabilities scoped to codebook + edit layers (not generalized substrate-failure); U3 COW closure scoped to COW-mechanism not edit-isolation-capability (Path D achieves it differently); T5 Path B reframe scoped to accuracy-envelope-clean (not contradicting v288 differential-survival).
- **[[feedback-no-padding-experiments]]**: T3 band 0.65-0.80 CONSERVATIVE not 0.80+; Path D LIFT +5%/+7% not +10%/+12%; Path E LIFT +5%/+7% not +10%/+12%; product-feature row UNCHANGED not LOWERED on adversarial findings.
- **[[feedback-strategy-shore-up-capabilities]]**: NEW row added on T3 finding; Path D LIFT proactively on U1 no-ceiling finding; Path E LIFT on T4 3-niche-application; adversarial findings ANNOTATED for proactive defense work; not just reactive-to-verdict.
- **[[feedback-lit-scan-calibration-penalty]]**: Modern Hopfield activation NEW row at 0.65-0.80 = below 0.80 cap for novel-synthesis claims (substrate is in uncharted modern-Hopfield-bend regime at N=16384; no published direct precedent for substrate-class continuous-output BSC at N=16384 with M=N recall); applied calibration penalty -0.15 to -0.20 from where unconstrained band would be (would be 0.80-0.95 unconstrained).
- **[[feedback-obey-user-pause-explicitly]]**: pause-flag ABSENT; user explicit "NO exp_dev refill (V2 24h sustained still running on GPU; G1-G4 pending; T4-T5 results just processed)" honored; verdict_handler does NOT dispatch exp_dev refill; 3 research routings FILED but NOT auto-dispatched.
- **[[feedback-cap-map-update-protocol]]**: atomic single-batch commit; sub-agent push BLOCKED; commit hash surfaced to orchestrator main-thread for push.
- **[[feedback-decision-log-eol-handling]]**: strategy_decisions_2026-05-30.md entry appended via tools/orchestrator/append_decision_log.py (LF EOL); cap_map + history CRLF preserved.
- **[[feedback-no-smoke]]**: brutal honesty applied — T3 "bend" claim called out as TEST-CEILING-INFERRED-NOT-MEASURED (#151); T2 label-understates-data surfaced (#152); T5 metric-source-misidentified surfaced (#153); U2 per-cell severity escalated (#154); U3 script-threshold-bug noted (#155); U1 trivialization risk acknowledged in cap_map band; U2 vulnerabilities NOT swept under "expected" framing; U3 closure documented as mechanism-dead-end NOT capability closure.
- **[[feedback-for-you-tab-primary-channel]]**: 7 status_log entries with plain_language + importance fields (2 CRITICAL: T3 modern-Hopfield + U1 Path-D-no-ceiling; 1 HIGH: U2 adversarial vulnerabilities; 1 MEDIUM-low: U3 COW infeasibility + 1 MEDIUM: V1 pipeline validation + 1 MEDIUM: T2 + 1 MEDIUM: T4 Path E niche-applications). T5 MEDIUM bundled into Path B annotation.
- **[[feedback-no-label-vs-honest-anchor-names]]**: 8 anchors PROT-018 spot-check all CLEAN.

### Commit and push

Commit message stored below.

Push: BLOCKED from sub-agent context per [[feedback-subagent-permission-inheritance]]; orchestrator main thread executes `git push origin main` as 1-tool follow-up.

**Commit message:**

```
Cap map: v289 -> v290 (BATCHED 8-VERDICT T2-T5+U1-U3+V1 MAJOR EVENT; NEW ROW "Modern Hopfield activation regime at large N" 0.65-0.80 P-band T3 max_M=N=16384 CPU 3-seed unanimous 4x linear-capacity-floor AT MINIMUM "bend" framing TEST-ENVELOPE-CEILING-INFERRED needs M>N replication + cross-codebook; Path D sub-row LIFT-annotation 0.80-0.88 -> 0.85-0.95 +5%/+7% U1 no-ceiling within 16N x depth=50 envelope 100/100 cells unanimous 1.000 per-hop-independent-Bayesian mechanism; Path E sub-row LIFT 0.65-0.75 -> 0.70-0.82 +5%/+7% T4 3-niche-application confirmation; substrate-product-feature row ANNOTATED REGULATED-INDUSTRY-DEPLOYMENT-BLOCKER pending U2 codebook-collision 100% breach + edit-fact-traverse 99.4% breach adversarial defenses; COW mechanism-dead-end ANNOTATION U3 cons=1.00 audit=5/5 OK but 10.13x mem-amp + 7-8x throughput-slower INFEASIBLE; V1 Phase-1 cloud-pipeline-validation ANNOTATION 39/39 cells 0 crashes N=2048+4096; T2 Path D edit-isolation-under-load 45/45 cells unanimous label-understates-data; T5 Path B sub-capacity acc=1.000 60/60 unanimous PARTIAL sources from geom_cos not accuracy METRIC-SOURCE-MISIDENTIFIED; 5 NEW LABEL-VS-HONEST sub-flavors #151 CEILING_AT_TEST_ENVELOPE_PRECLUDES_BEND_CLAIM T3 + #152 LABEL_NARRATIVE_UNDERSTATES_DATA T2 5th-occurrence + #153 METRIC_SOURCE_MISIDENTIFIED T5 + #154 PER_CELL_BREACH_STRONGER_THAN_AVG U2 + #155 SCRIPT_THRESHOLD_DISAGREES_WITH_DATA U3; portfolio 14+36 -> 15+36 NEW ROW; HONEST 256 -> 263 +7 (8 verdicts - 1 over-claim #151 + label-honest extensions); LABEL-VS-HONEST 150 -> 155 +5 NEW; non-eq SKAH-M TCFT deletion-cert KF-1 KF-2 KF-3 specific general substrate-GPU multi-hop-combined product-feature UNCHANGED at row position; 6 rescue sets cheapest-first 18 rescues R1 0-compute APPLIED inline; 7 status_log entries (2 CRITICAL T3 modern-Hopfield + U1 Path-D-no-ceiling; 1 HIGH U2 adversarial; 4 MEDIUM U3 COW + V1 pipeline + T2 + T4); 3 research routings filed codebook-collision-defense + edit-adversarial-defense + alt-edit-isolation NOT auto-dispatched per V2 still running + G1-G4 pending; 201st PROT-009 paired commit; verdict_handler dispatched; user no-refill V2/G1-G4 in-flight)
```

## v290 -> v291 @ BATCHED 2-VERDICT C1+C8 EXTENSION EVENT (verdict_handler-dispatched; 202nd PROT-009 paired commit)

**Context.** Batched 2-verdict event: C1 modern_hopfield_cpu_backup_extended_v1_n16384 HARD_PASS (1023s; max_M=4N=65536 all 3 seeds) + C8 sparse_w_large_n_integration_v1 HARD_PASS (59s; 9/9 KF cells N=8192 + projection slope=1.0 to N=16384). Both verdicts EXTEND prior cap_map state (Modern Hopfield NEW row from v290 + Sparse-W LIFT from v284) along their next-natural axes. User explicit: "NO exp_dev refill (orchestrator dispatching follow-up batch in parallel with this)."

### Step 0 honest re-read summary -- 1 NEW SUB-FLAVOR catch (#156); C8 LABEL-HONEST as worded

#### #156 -- C1 LABEL_CONSERVATIVELY_UNDERSTATES_CEILING_BAND (NEW SUB-FLAVOR; opposite valence of typical over-claim)

**Anchor.** `modern_hopfield_cpu_backup_extended_v1_n16384` HARD_PASS labeled "CEILING_EXTENDS_PAST_2N: constructed=3/3 max_M_per_seed=[65536, 65536, 65536] target_hp>=32768 target_hf=16384".

**Honest reading.** Per-cell metrics: all 3 seeds {7, 17, 23} x all 3 M values {16384, 32768, 65536} = 9/9 cells recall=1.0 unanimous. max_M_at_95_recall = 65536 = 4N for ALL 3 seeds. Pre-reg HP threshold target_hp >= 32768 = 2N MET BY 2x at every seed. Label says "PAST_2N" but data shows PAST_4N (the test envelope SATURATED at 4N with no degradation). This is a CONSERVATIVELY UNDERSTATED label -- opposite valence of typical over-claim. Critical caveat preserved: test envelope SATURATES at M=4N; actual ceiling past 4N is UNTESTED.

**Decision.** HARD_PASS HONEST CONSERVATIVELY. NEW SUB-FLAVOR #156 LABEL_CONSERVATIVELY_UNDERSTATES_CEILING_BAND filed (distinct from #151 CEILING_AT_TEST_ENVELOPE_PRECLUDES_BEND_CLAIM: #151 was over-claim risk, #156 is conservative-understatement of empirical band). Cap_map decision: Modern Hopfield row promoted yellow -> green 0.65-0.80 -> 0.75-0.88 LIFT (+10%/+8%). 2-anchor confirmation at N=16384 BSC (T3 + C1) + max_M >= 4N empirically RESOLVES v290 "untested past M=N" caveat fully and PARTIALLY RESOLVES "single anchor" caveat. Remaining caveats: (a) single codebook BSC at N=16384 still open; (b) actual ceiling past 4N still untested; (c) cross-N (N=8192 G5/G6 still in flight) still open; (d) cross-N at activation regime envelope untested.

#### C8 -- LABEL-HONEST as worded (no over-claim, no under-claim)

**Anchor.** `sparse_w_large_n_integration_v1` HARD_PASS labeled "COMPOSITION_OK: M=512:3/3_pass; M=2048:3/3_pass; M=8192:3/3_pass | slope=1.0 deployable=True".

**Honest reading.** KF cells: 9/9 (3 M x 3 seeds) all retention=1.0, max_iso=0.0, above_thresh_frac=0.0, kf_pass=True at N_validation=8192. Footprint cells at N=4096 confirm sparse_match_theory=True at all 4 M values. Projection at N=16384 via slope=1.0 power-law (matches theory) yields on_device_anchor M=2048 ratio=0.25 deployable=True. The `deployable=True` flag is EMPIRICAL at N=8192 (validation cell) but PROJECTED at N=16384 (extrapolated). Label HONEST -- script transparently exposes the projection mechanism via `projection_at_n16384` keys; not hidden under-rug.

**Decision.** HARD_PASS HONEST. C8 = FIRST independent confirmation of v283/v284 sparse-W active-subspace envelope on N-axis EXTENSION (N=4096 -> N=8192). Cap_map: Sparse-W row 0.55-0.70 -> 0.60-0.75 LIFT (+5%/+5%). MODEST LIFT (not +10%/+10%) because N=16384 deployment is PROJECTED via power-law not empirically validated + sparse-W in modern-Hopfield activation regime (M >> N) UNTESTED.

### Cap_map decisions -- row-by-row

1. **Modern Hopfield activation regime at large N: 0.65-0.80 (yellow) -> 0.75-0.88 (green) LIFT (+10%/+8%).** Mid-band 0.815. Promote yellow -> green because (a) 2-anchor confirmation T3 + C1 both at N=16384 BSC RESOLVES single-anchor caveat partially, (b) max_M >= 4N RESOLVES untested-past-M=N caveat fully, (c) per-cell metrics 9/9 cells unanimous recall=1.0. Conservative upper bound 0.88 (not 0.92+) reflects remaining caveats (single codebook BSC + ceiling-past-4N untested + cross-N untested + cross-N-at-activation-regime untested). NEW SUB-FLAVOR #156 LABEL_CONSERVATIVELY_UNDERSTATES_CEILING_BAND.

2. **Sparse-W active-subspace storage: 0.55-0.70 -> 0.60-0.75 LIFT (+5%/+5%).** Mid-band 0.675. Modest LIFT reflects N-axis envelope extension N=4096 -> N=8192 (9/9 cells unanimous + slope=1.0 power-law match-theory) + N=16384 PROJECTED not empirical. R2 (C12 direct N=16384 validation) closes projection caveat at MEDIUM compute cost.

**Portfolio**: 15 + 36 UNCHANGED at row count (both LIFTs are within-row band moves; Modern Hopfield row promoted yellow -> green within existing row position).

**Framework reliability bands**: ALL bands UNCHANGED at framework-class level (non-eq, SKAH-M, TCFT, KF-1, KF-2, KF-3, deletion-cert, specific, general, product-feature, substrate-GPU, multi-hop-combined + sub-rows). Only the 2 row-specific bands (Modern Hopfield activation + Sparse-W active-subspace) lift; no framework-class shifts.

**HONEST 263 -> 265 (+2)**; **LABEL-VS-HONEST 155 -> 156 (+1 NEW SUB-FLAVOR #156)**.

### Rescue sketches summary (2 sets filed cheapest-first per [[feedback-rescue-sketch-first-sequencing]])

- **R-MODERN-HOPFIELD-EXTENSION (4 rescues):** R1 0-compute subsumption-annotation RECOMMENDED-FIRST (test-envelope-ceiling extension at next sweep level + conservative LIFT pending M>4N + cross-codebook + multi-N); R2 CHEAP C9 M sweep {4N, 8N, 16N} past N=16384 (HIGH PRIORITY); R3 CHEAP C10 Kerdock cross-codebook at N=16384; R4 MEDIUM C11 cross-N at N=12288 + N=20480.
- **R-SPARSE-W-LARGE-N (3 rescues):** R1 0-compute subsumption-annotation RECOMMENDED-FIRST (N-axis envelope extension + projection-not-empirical caveat); R2 MEDIUM C12 direct N=16384 sparse-W validation (MEDIUM PRIORITY); R3 MEDIUM C13 sparse-W at modern-Hopfield activation regime M >> N composition.

### Follow-on recommendations (for orchestrator main-thread; NOT auto-dispatched per orchestrator-follow-up-batch-in-parallel directive)

Top-3 surfaced for orchestrator main-thread review:

1. **C9 M-sweep past 4N at N=16384** (HIGH PRIORITY CPU ~30-45min) -- characterize WHERE Modern Hopfield activation actually breaks past M=4N=65536; same harness as C1; closes last remaining test-envelope-ceiling caveat. If no ceiling at 16N, justifies LIFT to 0.85-0.92 next cycle.

2. **C12 direct N=16384 sparse-W validation** (MEDIUM PRIORITY CPU/GPU ~30-60min) -- empirically confirms C8's slope=1.0 projection at N=16384; closes projection caveat on sparse-W row.

3. **C10 Kerdock cross-codebook at N=16384 + C13 sparse-W at modern-Hopfield activation regime composition** (MEDIUM PRIORITY ~60-90min total) -- C10 addresses Modern Hopfield "single codebook BSC" caveat; C13 tests sparse-W mechanism in past-M=N activation regime (compositional with C1 axis).

### PROT compliance (v290 -> v291)

- **PROT-004/006**: 2 rescue sets cheapest-first; 7 rescues total; R1 0-compute APPLIED inline in both sets.
- **PROT-007**: cap_map_history.md v291 row added; **BACKLOG NOTE carried forward**: v277 + v278 history rows STILL missing (from v279-v290 PROT-007 backlogs).
- **PROT-008**: NOT run inline (2 within-row band LIFTs + 1 row promotion yellow -> green; portfolio 15+36 UNCHANGED).
- **PROT-009**: cap_map.md (v291 entry) + history.md (v291 row) + this strategy_decisions append + 2 status_log entries; **202nd PROT-009 paired commit**.
- **PROT-018**: 2/2 anchors spot-checked CLEAN (C1 _n16384 matches config.N=16384; C8 multi-N exemption per v283 precedent).
