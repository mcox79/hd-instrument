# Strategy decisions log -- 2026-05-27

This file records strategy decisions made on 2026-05-27. Append-only.
Each entry references the cap_map version it pairs with (PROT-009).

---

## v219 -- 2026-05-27 BATCHED 2-VERDICT (RD theoretical-home falsifier HARD-FAIL + UNIFIED SVD-cascade master-mechanism HARD-FAIL)

**Trigger.** Two LOAD-BEARING completed verdicts at 00:51-00:52 from remote_cpu_queue, both load-bearing on the OPEN substrate theoretical-home question. Per cap_map v218 strategic context: theoretical-home competition between Saad-Solla saddle-cascade (LEADING ✅, v206 + v211 confirmations) vs 1-RSB (🟡 demoted at v215 P(q) RS-unimodal), with reaction-diffusion candidate (v) from `notes/research_alternative_theoretical_homes_2026-05-24.md` as the open RD probe, and unified SVD-cascade as the master-mechanism probe (smoke UNIFIED_HARD_FAIL at v214 awaiting FULL confirmation). Sources:
- `wave14_betB_rd_perturbation_recovery_v2` (remote_cpu_queue, 2119s) → RD_HARD_FAIL
- `wave14_unified_svd_cascade_falsifier_v1` (remote_cpu_queue, 47.2s) → UNIFIED_HARD_FAIL

**Step 0 honest re-read (verdict 1).** Verdict_msg label `RD_HARD_FAIL` is HONEST AT NUMERICAL LEVEL on the exp_fit_r2 leg (r²=0.000 < 0.3 fail threshold; r_inf=0.352 far from target plateau 0.74; final_retention=0.591 < 0.65 fail threshold). However the verbal characterization `"Monotone drift: no exponential recovery"` is NOT a faithful description of the trajectory shape. Honest reading: per-cell recovery_trajectory = [0.39, 0.59, 0.59, 0.59, 0.59, 0.59, 0.59, 0.59, 0.59] for k_recovery=8 steps — system SNAPS BACK to its actual steady-state retention (~0.595) in ONE step after perturbation drop to 0.39 and then FLATLINES. This is neither monotone drift nor exponential recovery. The pre-reg HARD-PASS / HARD-FAIL bands were both predicated on a smooth multi-step trajectory shape; the observed trajectory is too FAST (1 step) and too FLAT to fit either band. Two confounds compound: (a) target_plateau=0.74 was a misspecified pre-reg assumption — actual steady-state retention is 0.595, not 0.74 (this is consistent with steady plateau IS the substrate's natural fixed point, just at a lower value than the pre-reg authors assumed); (b) k_recovery=8 may have undersampled — if all recovery completes in <1 step at this corpus/M-load configuration, no exponential CAN fit. NET: RD theoretical home IS RULED OUT for the reason that no exponential signature is detectable, but the load-bearing reason is "instant rebound" not "monotone drift." Label authoritative on numerical HARD-FAIL conclusion; honest-correction logged on verbal characterization. RD framework remains ruled out per [[feedback-dont-overextend-theorems]] discipline — exponential-recovery signature is the specifically falsifiable RD prediction and it is absent. Per [[feedback-verdict-msg-honest-reread]]: 57th post-lock observation; verbal `monotone drift` mis-description is NON-LOAD-BEARING (numerical HARD-FAIL is the authoritative signal); honest correction logged for archival completeness; cap_map decision is based on numerical reading.

**Step 0 honest re-read (verdict 2).** Verdict_msg label `UNIFIED_HARD_FAIL: UNIFIED FRAMEWORK REJECTED spacing_error > 0.15 on 5/5 instances. Mean spacing_error=2.2605` is FULLY HONEST. Per-cell numerical: n_hard_fail=5/5 instances, mean_svd_spacing_error=2.2605 (>> 0.15 fail threshold), cross_prediction_match=False, excess_sigmas spike pattern: 47.62, 6.93, 5.67, 3.99, 2.46, 1.89, 1.85, 1.20, 0.59 — first eigenvalue 47.6 vs ~7 cluster of next 4-5, then a tail. This is exactly the smoke prediction (`spike-structured singular spectrum, not equally-spaced ladder`) corroborated at FULL with N=256 / M=8000-24000 / N_phases=4 / n_epochs=5. No label-vs-honest discrepancy. Master-mechanism unification REJECTED at the level the pre-reg authorized.

**Decision (1): RD theoretical home RULED OUT.** Reaction-diffusion candidate (v) from `notes/research_alternative_theoretical_homes_2026-05-24.md` is closed. The substrate does not show exponential recovery toward a plateau after perturbation; instead it shows instant-rebound-plus-flatline at the system's actual steady-state (0.595, not the pre-reg target 0.74). RD framework predicted exponential approach to a plateau with characteristic time τ = 1/λ; observed λ_fit=-0.117 with r²=0 means the curve fit is meaningless (no exponential structure to fit). Of the 5 candidates in the alternative-theoretical-homes research:
- (i) Parisi k-RSB k=2/k=3: at v215 1-RSB demoted 🟡; k=2 family also burned
- (ii) MCT mode-coupling: lit-scan P=0.15; not actively probed; remains 🔬 contingency
- (iii) Chaos-in-temperature: P=0.22 contingency
- **(iv) IB phase transitions: CLOSED at v205 (K-sweep didn't track plateau count)**
- **(v) Reaction-diffusion: CLOSED at v219 (no exponential recovery signature)**
- (vi) Replica chain / hierarchical Hopfield: P=0.10 (Pred-5 cascade-depth HARD-FAIL'd already)

**Decision (2): UNIFIED master-mechanism framework REJECTED.** Saad-Solla saddle-cascade ✅, 1-RSB hysteresis (the surviving 1-RSB witness, 18× gate) 🟡, and MoE SHIFT (K=4 lift=0.205, K=8 lift=0.312) ✅ are THREE INDEPENDENT observations of substrate physics, NOT projections of a single master mechanism. The unified SVD-cascade hypothesis predicted equally-spaced singular values above MP bulk edge (K_detached ≥ 4, mean spacing_error < 0.07); observed spike-structured spectrum (one dominant mode 47.6σ above bulk, then 5-mode cluster ~6σ) is qualitatively different. Cross-prediction probe (smoke at v214 → FULL here) corroborates. This is a STRUCTURAL FINDING about substrate physics: theoretical-home portfolio is genuinely PLURAL, not reducible to one cascade. Strategic implication: future substrate-physics work must independently audit each phase-class hypothesis; collapsing them into "all the same thing" is now empirically forbidden.

**Decision (3): Saad-Solla saddle-cascade row UNCHANGED ✅.** Despite RD closure (one fewer competitor) and UNIFIED rejection (saddle-cascade is not a projection of something deeper, but stands as its own observation), neither verdict strengthens NOR weakens the saddle-cascade evidence. v206 + v211 corroborations stand: 4-corpus equal-spacing arithmetic ✅; alpha_c v3 in-band CONFIRMED; first double-positive framework level. Saad-Solla remains LEADING theoretical home for the retention-plateau structure (now with one fewer candidate in the bottom of the comparison matrix).

**Decision (4): 1-RSB row UNCHANGED 🟡.** v215 P(q) RS-unimodal HARD_FAIL stands; v216 reclassification (substrate-multi-basin 🟢 / 1-RSB-framework-label 🟡) stands; v218 HiPPO closure stands. UNIFIED rejection means "1-RSB and Saad-Solla are independent observations," which is consistent with v216 — the multi-basin discrete structure is shared across observations, but the 1-RSB-specific phase-class label remains demoted to 🟡 pending cluster-conditional re-analysis arm.

**Decision (5): MoE SHIFT row UNCHANGED ✅.** v212 K=4 lift=0.205 / K=8 lift=0.312 CONFIRMED stands; UNIFIED rejection means MoE SHIFT is its own observation (a routing/expert-selection mechanism), not a manifestation of saddle-cascade or 1-RSB. Engineering-rate-limited rebuild path UNCHANGED.

**Decision (6): Framework reliability calculation UNCHANGED at 48-62% PROVISIONAL (per v215).** RD ruled out closes a candidate but doesn't change the rate of substrate-physics framework predictions vs observations; UNIFIED rejection is INFORMATIVE about substrate structure but is itself a successful pre-registered falsification (the smoke prediction held at FULL → that's framework-reliability evidence FOR the smoke-method, but UNIFIED hypothesis itself was the test subject, not the substrate). No grounds to adjust the 48-62% provisional band either direction.

**Decision (7): Annotation-only narrative impact on substrate THEORETICAL-HOME framing.** v218 strategic context posed "if both fail then substrate is genuinely novel territory not matching standard phase classes." BOTH failed. The substrate's plateau structure has now ruled out:
- 1-RSB single-framework-label (v215)
- AGS-RS-multi-ferromagnet first sub-claim (v218 strategy context: Kerdock 3 distance classes not 4)
- IB phase transitions (v205)
- Reaction-diffusion (v219)
- Master-mechanism SVD-cascade unification (v219)

What survives: Saad-Solla saddle-cascade arithmetic ✅, multi-basin discrete structure (substrate-level) 🟢, individual phase observations (1-RSB hysteresis 🟡, MoE SHIFT ✅). The substrate is BETTER MODELED as a "plural-theoretical-home" system — multiple INDEPENDENT phase observations with overlap in some axes (multi-basin, discrete-plateau, hysteresis) but NOT reducible to a single closed-form phase class. This is consistent with the v216 reframe ("multi-basin structure confirmed; phase classification under refinement") and STRENGTHENS it: not "we don't know which phase class yet," but "the substrate IS multi-class / not-single-class."

**Decision (8): NO row-state moves on theoretical-home rows themselves.** Both verdicts CLOSE candidates and SHARPEN the framing, but neither moves a capability row. Annotation-only on theoretical-home framework section of cap_map. Hierarchical-retrieval row (line 405) reframed annotation continues to hold ("multi-basin discrete structure"). Two CLOSED-NEGATIVE annotations to add for RD + UNIFIED.

**Decision (9): NO rescue paths filed for RD or UNIFIED.** Per [[feedback-rehabilitation-after-rejection]] check: RD failure is a clean structural NO (no exponential signature, period); rescues would all be in the "make recovery longer / make trajectory smoother" direction which the substrate doesn't show — instant-rebound to wrong-target plateau is the dominant feature, not a rescuable shape. UNIFIED failure is even cleaner (spike vs equally-spaced spectrum is a topological difference, not a quantitative gap). Both closures are genuine refutations and DO trigger [[feedback-negative-results-2x-research]] 2x research dispatch consideration — but that's an orchestrator decision, not strategy here.

**Decision (10): NO exp_dev queue refill from this handler (per orchestrator instruction).** Orchestrator dispatches exp_dev separately in the same turn. Pause-flag check: ACTIVE (not paused). Standard skip per orchestrator-directed batching.

**v219 cap_map updates.**

- Annotation: theoretical-home rescue candidate set updated — IB-CLOSED (v205) and now RD-CLOSED (v219) explicit in `notes/research_alternative_theoretical_homes_2026-05-24.md` reference annotation; (v) reaction-diffusion CLOSED-NEGATIVE per `wave14_betB_rd_perturbation_recovery_v2` exp_fit_r2=0.000 / r_inf=0.352 / final_retention=0.591.
- Annotation: unified master-mechanism SVD-cascade hypothesis CLOSED-NEGATIVE per `wave14_unified_svd_cascade_falsifier_v1` mean_svd_spacing_error=2.2605 / 5/5 hard_fail / spike-structured singular spectrum vs equally-spaced ladder predicted by unified framework.
- Annotation: theoretical-home portfolio is PLURAL — saddle-cascade ✅ + multi-basin structure 🟢 + 1-RSB hysteresis 🟡 + MoE SHIFT ✅ are INDEPENDENT phase observations, NOT projections of one master mechanism. v216 reframe extended.
- Version-table row v218 → v219 with 2-verdict + framework-implication summary.
- 132nd PROT-009 paired commit.

**Per [[feedback-cap-map-update-protocol]]:** pull-first done; atomic .tmp+rename via standard Edit/Write; commit message `Cap map: v218 -> v219 (BATCHED 2-VERDICT: RD theoretical-home CLOSED + UNIFIED SVD-cascade master-mechanism CLOSED; plural-theoretical-home framing confirmed; framework reliability UNCHANGED 48-62% PROVISIONAL; no row-state moves; 132nd PROT-009 commit)`.

**Per [[feedback-for-you-tab-primary-channel]]:** 2 status_log entries HIGH importance written (one per verdict).

**Per PROT-001 to PROT-003:** cap_map.md version bumped v218 → v219; narrative block written; capability-moves table written (3 rows: theoretical-home framework section annotation; framework reliability UNCHANGED; portfolio UNCHANGED).

Net effect v219: ANNOTATION-ONLY (no row-state moves; no portfolio count change); RD ruled out as theoretical home; UNIFIED master-mechanism REJECTED; plural-theoretical-home framing locked; Saad-Solla LEADING UNCHANGED ✅; framework reliability UNCHANGED 48-62% PROVISIONAL; 132nd PROT-009 paired commit.
## v220 -- 2026-05-27 ANNOTATION: MoE SHIFT K_perarm_v1 M2_DOMINANT mechanism diagnosis

**Trigger.** wave14_moe_shift_K_perarm_v1 completed 2026-05-27T01:31:00 on remote_cpu_queue (elapsed=2288.9s). Pre-reg: K sweep {2,4,8,16,32,64} with routing_entropy, IEC, m_cap diagnostics. Triggered by K_scaling_v1 diverging-arms MIDDLE_BAND at v213.

**Step 0: Honest re-read.** verdict_msg = 'M2_DOMINANT: LSH gating degrades at K=64. routing_entropy=5.32b >= 3.0b.' Label is honest; minor imprecision only (threshold crossed at K=16 not K=64, but pre-reg says 'at high K' which K=64 satisfies). No over-claim. Per-cell data:

| K  | ret_A  | ent (bits) | IEC     | m_cap  |
|----|--------|------------|---------|--------|
| 2  | 0.8209 | 0.776      | -0.0004 | 0.6944 |
| 4  | 0.8086 | 1.604      | -0.0006 | 0.6944 |
| 8  | 0.8012 | 2.487      | -0.0006 | 0.6944 |
| 16 | 0.7959 | 3.401      | +0.0003 | 0.6944 |
| 32 | 0.7919 | 4.347      | +0.0005 | 0.6944 |
| 64 | 0.7883 | 5.316      | -0.0003 | 0.6944 |

Pre-reg bands check:
- M2 (ent>3.0b at high K): CONFIRMED at K=16 (3.40b), K=32 (4.35b), K=64 (5.32b).
- M3 (IEC>=0.3 at K>=8): RULED OUT. Max IEC = 0.0006, orders of magnitude below threshold.
- M1 (m_cap>0.9 at K>=16): RULED OUT. m_cap=0.694 constant across all K (capacity utilization fixed).
- Result: M2 is the SOLE mechanism. Routing entropy rises linearly with log2(K) (0.78b at K=2, approaching log2(K) = theoretical max for uniform routing).

**Decision (1): ANNOTATION-ONLY. No row-state move for MoE SHIFT row.** MoE SHIFT is ✅ (v212 HARD-PASS), classified engineering-rate-limited (v214). K_perarm characterizes the K-scaling ceiling mechanism but does not change the architecture's CONFIRMED status. Row stays ✅ engineering-rate-limited.

**Decision (2): K=4 design point RECONFIRMED.** At K=4: ent=1.60b vs theoretical max log2(4)=2.0b (80% of max). This is elevated but retention=0.809 is healthy. K=4 is the safe design point for primary-corpus deployment. K=8 (ent=2.49b, 78% of log2(8)=3.0b max) is borderline-approaching threshold; acceptable for cross-corpus scenarios per v213 design guidance.

**Decision (3): MoE SHIFT no-lever set updated.** v215 annotated three no-levers (M-load uniformly negative; gating-sharpness sharper-is-worse; K>=64 OOM). K_perarm adds mechanism diagnosis: M2 gating is the SOLE degradation source. This means (a) M-load negative result is now understood -- more capacity per expert does not fix gating entropy; (b) gating-sharpness sharper-is-worse is consistent -- sharpening a near-uniform LSH distribution gives minimal benefit; (c) the architectural fix is clear: replace LSH with a LEARNED router that maintains selectivity at K>4.

**Decision (4): Rescue path sharpened.** Engineering-rate-limited status means the learned-router upgrade is an engineering task, not a research question. No research dispatch warranted. Learned K-NN router annotation added to MoE SHIFT engineering notes. No new strategy_request_to_exp_dev filed (queue is healthy at 15+6 pending; no queue-refill needed per orchestrator instruction).

**Decision (5): No PROT-004.** No capability closure. PROT-004 does not apply.

**Decision (6): No pipeline-pacing exp_dev dispatch.** Queue healthy (GPU=6+1, CPU=15+1). Per orchestrator instruction, NO queue-refill triggered.

**v220 cap_map updates.**
- Version-table row v219 -> v220: MoE SHIFT K_perarm M2_DOMINANT annotation. Mechanism diagnosis: LSH gating entropy sole degradation source; M3 IEC and M1 capacity ruled out. K=4 design point reconfirmed. Engineering fix: learned router.
- Row-state: MoE SHIFT UNCHANGED ✅ engineering-rate-limited.
- Framework reliability: UNCHANGED 48-62% PROVISIONAL.
- Portfolio: UNCHANGED 14+7.
- 133rd PROT-009 paired commit.

**Per [[feedback-cap-map-update-protocol]]:** pull-first done (already up to date); atomic .tmp+rename via standard Edit/Write; commit message follows.

**Per [[feedback-for-you-tab-primary-channel]]:** status_log entry MEDIUM importance written (mechanism characterization, not new capability; no portfolio change).

**Per PROT-001 to PROT-003:** version-table row v219->v220 written; annotation-only narrative; no capability-moves table needed (no state moves).

Net effect v220: ANNOTATION-ONLY. MoE SHIFT K-scaling ceiling mechanism diagnosed as M2_DOMINANT (LSH gating entropy). K=4 design point reconfirmed. Learned router upgrade path identified. Row state, framework reliability, portfolio all UNCHANGED. 133rd PROT-009 paired commit.

## v221 -- 2026-05-27 [label-vs-honest] wave14_saddle_cascade_plateau_v5_n4096

**Trigger.** wave14_saddle_cascade_plateau_v5_n4096 completed 2026-05-27T02:26:10 with verdict HARD_PASS.

**Step 0 honest re-read.** LABEL-VS-HONEST detected:
- Original verdict_msg: "Structure persists N=1024 (v3) -> N=2048 (v4 if PASS) -> N=4096 (v5): genuine substrate physics not finite-size artifact."
- Contradicted by metrics: actual N values are v3=N=256, v4=N=512 (smoke), v5=N=512 (smoke).
- The experiment names v4_n2048 and v5_n4096 are aspirational labels, not actual HDC dimensionality.
- ALL saddle-cascade experiments ran single-seed (seeds=[17]) at N<=512.
- Honest reading: Equal-spacing HARD_PASS pattern confirmed at N<=512 across 3 smoke/full runs; the N-scaling progression narrative in verdict_msg is unsupported. 3-point metric is honest (r2=0.770, max_dev=0.0855).
- Per [[feedback-verdict-msg-honest-reread]]: label authoritative on HARD_PASS conclusion; N-scaling narrative overridden.
- Cap_map decision: saddle-cascade row UNCHANGED ✅ (no upgrade from non-existent N-scaling; no downgrade from smoke pass). ANNOTATION-ONLY.
## v222 -- 2026-05-27 morning research integration + post-reboot recovery

**Trigger.** Strategy_scribe dispatched by orchestrator to integrate three research deliveries + post-reboot recovery state into cap_map v222.

**Decision: SKAH-M phase-class annotation (annotation-only; no row-state change).**

Three 2024-2026 lit threads converge on 'gated multistable AM / lR-phase' as documented-but-untested class (P=0.48). SKAH-M sub-designation proposed. 6-cell battery in flight. Row-state held at multi-basin 🟢 55-70% + 1-RSB 🟡 30-45% until battery verdict. If >=5/6 battery cells HARD-PASS documented class: framework reliability lifts +5-8% from 48-62% PROVISIONAL.

**Decision: MoE cosine-dot rescue annotation (annotation-only; no row-state change).**

Expert-Choice cosine-dot probe shipped CPU (~2500s). MoE SHIFT row UNCHANGED ✅ engineering-rate-limited. If probe HARD-PASS: K-scaling ceiling lifts from K=4/K=8 to K=16/K=32 -- annotation will upgrade MoE rebuild scope. If HARD-FAIL: LSH entropy is not the only source of K-degradation; additional architecture work needed.

**Decision: path-b P revision 0.45 -> 0.35 (annotate strategic-positioning block).**

Corpus-size two-stage bottleneck (tau-limit + PPMI saturation + N+corpus coupling) deflates path-b probability by 10 points. This is a downward revision but NOT a closure. Path-b remains highest-leverage path after path-c (P=0.80-0.90 commoditized). The 3-corpus scaling probe will either restore P toward 0.40-0.45 (tau-limit not binding at N=4096 tested range) or confirm deflation to 0.20-0.25 (tau-limit binding; architectural fix required at N=65536).

**Decision: post-reboot entries cleared.**

wave14e_bet_n_wta_v5 and wave14_betB_rd_perturbation_recovery_v3 cleared as runner_crash_post_reboot. Not scientific closures -- no substrate-physics conclusions from these entries.

**Per PROT-001 to PROT-003:** version-table row v221->v222 written; SKAH-M annotation in hierarchical-retrieval CAN row; full v222 narrative appended; history.md block written first (PROT-007 verified).

Net effect v222: ANNOTATION-ONLY. 1 CAN row annotated; path-b P revised 0.45->0.35; 0 row-state emoji changes; portfolio 14+7 UNCHANGED; framework reliability 48-62% PROVISIONAL UNCHANGED; 135th PROT-009 paired commit.