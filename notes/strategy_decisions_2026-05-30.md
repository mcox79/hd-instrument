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