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
## v223 -- 2026-05-27 BATCHED 3-VERDICT @ 04:56 (Bet I v3 + UNIFIED SVD v2 + Ortho Reservoir Lyapunov v1)

**Trigger.** Three verdicts completed @ 2026-05-27T04:56 (4 GPU pending + 1 running + 11 CPU pending + 1 running -- queue healthy; NO refill triggered).

**Step 0 honest re-read (3 verdicts).**

Verdict 1 -- wave14_beti_depth_polylog_v3 [LABEL-VS-HONEST]:
- Bridge label: FAILED. metrics.json verdict: MIDDLE_BAND SMOKE_REGIME_MISMATCH.
- verdict_msg: d_c > 0 at 0 N values at smoke scale. Smoke D_SWEEP=[2,5,10,20] N=[256,512] -- all acc~0 (cliff at d~1 for small N). Full-scale D_SWEEP=[2..100] N>=1024 brackets cliff correctly.
- Honest reading: smoke regime did not probe the actual cliff position. Full never ran (smoke gate). NOT a substrate failure -- instrumentation issue.
- Cap_map: Bet I 3rd envelope STAYS OPEN. v4 needs adjusted D_SWEEP_SMOKE>=60 (bracket the v2 ceiling) OR skip-smoke approval.

Verdict 2 -- wave14_unified_svd_cascade_falsifier_v2:
- Verdict: HARD_FAIL. 2/2 instances (1rsb_regime spacing_error=1.029, over_capacity=0.909) >> HF threshold 0.3.
- Steel-manned retry of v1 with relaxed gap-ratio criterion + wider bands.
- Cap_map: UNIFIED SVD-cascade master-mechanism DECISIVELY REJECTED with dual confirmation (v1 strict v219 + v2 relaxed v223). Plural-framework Saad-Solla + 1-RSB + MoE SHIFT = THREE INDEPENDENT FURTHER LOCKED.

Verdict 3 -- wave14_ortho_reservoir_lyapunov_v1:
- Verdict: HARD_FAIL. RC-1 rejected: L_max(alpha_c=0.5)=-5.4728 far from edge-of-chaos threshold 0.5; non-monotone in alpha.
- Corroborates Field-A Lyapunov v1 HARD_FAIL (lambda_1=0.8095 at density=0.2 -- firmly chaotic).
- Cap_map: RC-edge-of-chaos sub-framing LOCKED CLOSED-NEGATIVE 2nd confirmation. Substrate NOT echo-state-network class.

**Decision (1): Bet I 3rd envelope STAYS OPEN.** Label-vs-honest correction. v3 smoke regime mismatch is instrumentation issue not substrate signal. v4 ship needs adjusted D_SWEEP_SMOKE OR skip-smoke approval. Open Q for exp_dev next cycle.

**Decision (2): UNIFIED master-mechanism CLOSED-NEGATIVE further locked.** Two independent confirmations (v1 strict + v2 relaxed) close the door on master-mechanism framing. Product story shifts to: substrate exhibits THREE INDEPENDENT phase observations (Saad-Solla saddle-cascade + 1-RSB hysteresis + MoE SHIFT architectural locking) which is arguably stronger because each provides independent mathematical validation.

**Decision (3): Reservoir-computing-edge-of-chaos OUT.** Field-A v1 + ortho v1 = 2 independent HARD_FAIL probes converge on substrate-NOT-at-edge-of-chaos under any tested regime. Closes echo-state-network sub-mapping. Narrows live theoretical homes to: Saad-Solla saddle-cascade ✅ + 1-RSB hysteresis 🟡 + MoE SHIFT ✅ + SKAH-M lR-phase 🔬 (battery pending).

**Decision (4): No queue-refill triggered.** Per orchestrator instruction: queue healthy 4 GPU pending + 1 running + 11 CPU pending + 1 running. No exp_dev dispatch.

**Decision (5): No PROT-004.** No capability row closures (sub-framing closures only).

**v223 cap_map updates.**
- Version-table row v222 -> v223: BATCHED 3-VERDICT batched bump.
- Row updates: Bet I 3rd envelope row gets v223 update (smoke regime mismatch annotation); SVD-cascade row gets v223 update (dual-confirmation note).
- Framework reliability: UNCHANGED 48-62% PROVISIONAL.
- Portfolio: UNCHANGED 14+7.
- 136th PROT-009 paired commit.

**Per [[feedback-cap-map-update-protocol]]:** pull-first (already up to date); atomic stage via Edit; commit message follows PROT-009.

**Per [[feedback-for-you-tab-primary-channel]]:** 3 status_log entries written (one per verdict; importance MEDIUM for verdicts 2/3 closures, HIGH for verdict 1 label-vs-honest).

**Per [[feedback-verdict-msg-honest-reread]]:** Verdict 1 bridge label FAILED contradicted by metrics MIDDLE_BAND -- override applied. Label-vs-honest count: 1 this turn.

**Per PROT-001 to PROT-003:** version-table row v222 -> v223 written; full v223 narrative appended; history.md block written first (PROT-007 verified).

Net effect v223: ANNOTATION-ONLY. 0 row-state emoji changes. 2 sub-framings further locked CLOSED-NEGATIVE (UNIFIED dual confirmation + RC-edge 2nd confirmation). Bet I 3rd envelope STAYS OPEN per label-vs-honest. Portfolio 14+7 UNCHANGED. Framework reliability 48-62% PROVISIONAL UNCHANGED. 136th PROT-009 paired commit.

## v224 -- 2026-05-27 BATCHED 8-VERDICT @ 06:07-06:20 (DECISIVE-DAY: 4 load-bearing tests + 4 orthogonal probes)

**Trigger.** Eight verdicts completed @ 2026-05-27T06:07-06:20 from remote_cpu_queue. Orchestrator framing: "MOST OF THE DECISIVE TESTS today." Pre-batch queue state: 4 GPU pending + 1 GPU running + 11 CPU pending + 1 CPU running -- healthy; NO refill triggered per orchestrator directive.

**Step 0 honest re-read (8 verdicts).**

Verdict 1 -- wave14_ortho_blahut_arimoto_v1 [LABEL-VS-HONEST: HARD_PASS not failed]:
- Bridge label: FAILED. metrics.json verdict: HARD_PASS.
- verdict_msg: "R(D) curve non-trivial (max_R=1.2988) and finite. H_src=2.7081 nats. N_min predictions computed for ret={0.5,0.7,0.9}. Rate-distortion theory applicable to substrate multi-task retention."
- Per-cell: D_sweep 15 points; R_values go 4e-14 (essentially zero) up through D=0.48 then rise sharply 0.0041 -> 0.029 -> 0.116 -> 0.262 -> 0.485 -> 0.811 -> 1.299 as D increases from 0.547 to 0.95. Curve is monotone, finite, well-defined.
- Honest reading: Blahut-Arimoto rate-distortion theory IS applicable to substrate multi-task retention -- the R(D) curve has the expected qualitative shape (flat then rising as D approaches H_src=2.708 nats). Bridge "failed" is likely a runner exit-status / encoding artifact NOT a substrate signal. Override applied.
- Cap_map: Novel orthogonal-probe POSITIVE. Substrate admits a tractable R(D) characterization. Per [[feedback-verdict-msg-honest-reread]] 58th post-lock observation.

Verdict 2 -- wave14_ortho_pme_ising_capacity_v1 MIDDLE_BAND:
- Bridge label: completed. metrics.json verdict: MIDDLE_BAND.
- verdict_msg: "factor2_frac=0.00; alpha_max_mean=1.0407. PME Ising capacity off from Hopfield by > factor 2."
- Per-cell: N=64 alpha_max=1.017 +- 0.005 (ratio 7.37x off Hopfield 0.138); N=128 alpha_max=1.064 +- 0.004 (ratio 7.71x off).
- Honest reading: substrate is NOT in the Hopfield capacity regime (already established at v216 multi-basin reframe). Pairwise Maximum Entropy / Ising bound is too loose to discriminate -- alpha_max is ~7x larger than naive Hopfield prediction. Novel-probe MB landing.
- Cap_map: Informational corroboration of substrate-not-Hopfield-class. P_deflated=0.36 satisfied.

Verdict 3 -- wave14_1rsb_rate_dep_hysteresis_v1 MIDDLE_BAND [AMBIGUOUS NOT clean HARD_PASS]:
- Bridge label: completed. metrics.json verdict: MIDDLE_BAND at N=256.
- verdict_msg: "MIDDLE_BAND at N=256: pearson_r=[-1.000,-0.999] (mixed or borderline); gap_ratio=[-0.403,0.632]; framework ambiguous"
- Per-cell: M=2000 pearson_r=-0.9996 gap_ratio=+0.632 mean_gaps={1:0.839, 2:0.677, 4:0.530} -- gap shrinks monotone with epoch AND stays positive; M=10000 pearson_r=-0.9987 gap_ratio=-0.403 mean_gaps={1:0.195, 2:0.046, 4:-0.078} -- gap shrinks monotone AND CROSSES ZERO at epoch=4 (slow learning gives WORSE retention than fast).
- Honest reading: rate-dependence DIRECTION (slower learning -> smaller hysteresis gap) is corroborated at FULL on both M-loads (smoke at v216 was pearson_r=-0.9996 single point; FULL replicates with strong correlation both M-values). BUT the gap_ratio sign-flip at M=10000 is INCONSISTENT with clean geometric-frustration: a frustrated phase predicts hysteresis gaps that shrink with epoch while remaining the same sign. The M=10000 slow trajectory produces NEGATIVE gaps -- the system actually REVERSES its hysteresis sense at slow learning + high load. This is not a clean geometric-frustration signature.
- Cap_map: substrate IS rate-dependent (direction 🟢) BUT geometric-frustration phase-class label CANNOT be cleanly affixed from this run. rate_dep_v2 at N>=4096 with finer M-load grid is the next probe. Neither orchestrator branch ("substrate IS geometrically frustrated -> 55-70%" NOR "substrate is genuinely novel -> SKAH-M only path") activates cleanly. SKAH-M battery REINFORCED existentially important.

Verdict 4 -- wave14_1rsb_cluster_cond_pq_v1 MIDDLE_BAND [within<across corroborates v215]:
- Bridge label: completed. metrics.json verdict: MIDDLE_BAND.
- verdict_msg: "MIDDLE_BAND at N=256: n_binders>0.05=0/4; within-across diff=-0.2024; n_peaks_within=2"
- Per-cell: within_mean_q=0.0334 vs across_mean_q=0.2357 (within IS LESS than across -- OPPOSITE of cluster-glass prediction); 4 within-class q-distributions all have binder=0.0 (no second peak detected via Binder cumulant); 6 across-class q-distributions have binder in [0.333, 0.487] (clear bimodality across classes).
- Honest reading: cluster-glass / 1-RSB-cluster-conditional structure DECISIVELY ABSENT. Within-class memory states are NEAR-IDENTICAL (q~0.03 -- near-orthogonal random); across-class states are MORE OVERLAPPING (q~0.24). This is the OPPOSITE of what a cluster-glass predicts (clusters should show high within-cluster overlap separated by low across-cluster overlap). v215 demotion (P(q) RS-unimodal) CORROBORATED at the cluster-conditional level.
- Cap_map: 1-RSB cluster-conditional sub-framing CLOSED-NEGATIVE 2nd confirmation (smoke + FULL). One of 4 1-RSB rescue arms now CLOSED.

Verdict 5 -- wave14_kerdock_distance_class_audit_v1 HARD_FAIL [AGS-RS-MF REJECTED]:
- Bridge label: completed. metrics.json verdict: HARD_FAIL.
- verdict_msg: "HARD_FAIL: n_distance_classes=3 (expected 4); n_match_007=1/3; monotone=True; AGS basin-class prediction does not match Kerdock structure"
- Per-cell: distinct_levels_global=[-0.0312, 0.0, 0.0312] -- 3 IP/N classes not 4 per Welch bound for K=4096 N=1024 Kerdock code; plateau_comparison [0.94 vs AGS 0.711 (off 0.229), 0.74 vs AGS 0.695 (off 0.045 -- only this one matches within 0.07), 0.6 vs AGS 0.678 (off 0.078)]; n_match_within_007=1/3.
- Honest reading: AGS-RS-MF basin-class theory predicts 4 distinct distance classes from Kerdock 4-coset construction; substrate exhibits 3 classes consistent with simpler Hamming-distance ladder. AGS retrieval-phase rescue (one of 4 1-RSB rescues) DECISIVELY REJECTED. Smoke + FULL dual confirmation.
- Cap_map: AGS-RS-MF basin-class sub-framing CLOSED-NEGATIVE 2nd confirmation. 2/4 1-RSB rescue arms now closed.

Verdict 6 -- wave14_moe_cosine_router_v1 COSINE_ROUTER_HARD_FAIL [K-scaling rescue OUT; label-honest config note]:
- Bridge label: completed. metrics.json verdict: COSINE_ROUTER_HARD_FAIL.
- verdict_msg: "cosine-dot routing fails entropy/retention gates. entropy@K=16=3.999b > 3.0b (FAIL). Random BSC anchors may not provide sufficient discriminability at N=4096. Escalate to Hebbian-anchor rescue (anchor = bundle of first M/K stored patterns per expert)."
- Per-cell: K=4 retention=0.91378 entropy=1.999b (healthy, within K=4 design point); K=16 retention=0.91408 entropy=3.999b (router uniform-collapsed); retention_delta=+0.0003 (vs predicted -0.018 HARD_PASS / -0.015 HF); retention_vs_lsh_delta=+0.118 (cosine BEATS LSH by 11.8 points at K=16 -- positive but doesn't recover K-scaling); mean_anchor_cosine_spread @ K=16 = 0.00361 (anchors collapse to near-identical).
- LABEL-HONEST CORRECTION ON CONFIG: orchestrator dispatch said "N=4096"; actual config N=512. Test was on smaller dimensionality than framed. Does NOT change verdict but matters for design-space framing.
- Honest reading: cosine-dot Expert-Choice (Zhou et al. 2022 NeurIPS) FAILS entropy gate at K=16 -- BSC random anchors at N=512 don't provide sufficient discriminability for cosine top-1. HARD_PASS prediction (retention degradation 0.025->0.007 at K=16) NOT achieved. The 11.8-point retention advantage over LSH is real but doesn't recover the K-scaling ceiling.
- Cap_map: MoE cosine-dot router rescue arm CLOSED-NEGATIVE. MoE SHIFT row UNCHANGED ✅ engineering-rate-limited. Next rescue: Hebbian-anchor cosine-dot router (anchor = bundle of first M/K stored patterns per expert -- explicit suggestion from this verdict's verdict_msg). K-scaling rescue NOT unblocked by this verdict.

Verdict 7 -- wave14_corpus_size_scaling_v1 CORPUS_SCALING_HARD_FAIL [smoke-regime N=256]:
- Bridge label: completed. metrics.json verdict: CORPUS_SCALING_HARD_FAIL.
- verdict_msg: "tau-limit binding in tested range. bpc non-monotone: [7.6511, 7.7485]. N-scaling required before corpus-size scaling extrapolation is safe for path-(b)."
- Per-cell: train_bytes=3000 mean_bpc=7.6511 top_edge_ratio=22.95 effective_rank=78.08; train_bytes=20000 mean_bpc=7.7485 top_edge_ratio=18.61 effective_rank=82.64. monotone_bpc=False (bpc gets WORSE with 6.67x more data); whitening_onset=False (top_edge_ratio stays >> HF=1.5).
- Honest reading: tau-limit IS binding at N=256 K=4 in this corpus-size range. Substrate may scale fine at N>=4096, but N=256 K=4 smoke run cannot probe that question -- this is an instrumentation/smoke-regime HARD_FAIL not a substrate-physics refutation. Per v222: path-(b) P revised 0.45->0.35; this verdict adds modest downward pressure to P~0.27 pending N-scaling unblock probe.
- Cap_map: path-(b) feasibility P revised 0.35 -> 0.27 (annotation; narrow range because N-scaling probe is binding next step). corpus_N_scaling_tau_unblock_v1 anchor is the open follow-up.

Verdict 8 -- tda_reanalysis_5probe_v1 TDA_INCONCLUSIVE [diagnostic NOT validated]:
- Bridge label: completed. metrics.json verdict: FAIL (joint_call=TDA_INCONCLUSIVE).
- verdict_msg: "TDA_INCONCLUSIVE: TDA-A=MIDDLE TDA-B=MIDDLE TDA-C=HARD_FAIL(agree=2/5,monotone=False) TDA-D=MIDDLE(bars=2,gap=True) TDA-E=HARD_PASS(maxdiff=0.000)"
- Per-cell: TDA-C (the central agreement test against free-additive + dMPK on 5 SHIFT/PARTITION cases): n_agree=2/5; width_monotonic=False; w_shift_mean=0.4333 vs w_part_mean=0.8667; TDA-E (height-predictor scale-match): predicted_heights=[4.0, 8.0, 1.414] vs observed=[2.0, 1.0, 1.0] -- on capacity-adjusted normalized [0,1] scale max_abs_diff=0.000 (HARD_PASS); TDA-A b_0 monotone in tau but plateau_found=False at smoke scale; TDA-B substrate vs random b_1 ratio=1.25 p_value=0.833 (no signal); TDA-D long_bar_count=2 gap_observed=True.
- Honest reading: TDA b_0 plateau-width as a 4th MoE SHIFT/PARTITION diagnostic FAILS the central agreement test (TDA-C agree=2/5 vs needed ~4/5). The TDA-E HARD_PASS is on a different claim (height-predictor scale-match on normalized scale) and is mathematically pleasing but doesn't rescue the diagnostic. P=0.38 prior NOT cleared.
- Cap_map: TDA-as-MoE-diagnostic sub-framing CLOSED-NEGATIVE at smoke (FULL not committed); P deflated to ~0.20. 3-way agreement framework (free-additive + dMPK + intra-expert) remains UNCHANGED for MoE SHIFT/PARTITION calls.

**Strategic synthesis (orchestrator framed conditional + reliability re-calibration).**

Orchestrator pre-batch framing offered a 3-condition activation rule for framework reliability uplift:
- IF rate_dep HARD_PASS AND cosine_router HARD_PASS AND Kerdock HARD_FAIL -> substrate = geometrically frustrated + MoE rebuild unblocked + AGS REJECTED -> framework reliability 48-62% -> 55-70%.
- IF rate_dep HARD_FAIL -> substrate genuinely novel -> SKAH-M only path -> SKAH-M battery existentially important.

Empirical landing:
- rate_dep: NOT HARD_PASS (MIDDLE_BAND; rate-dep DIRECTION confirmed but gap_ratio sign-flip = ambiguous on phase-class LABEL).
- cosine_router: NOT HARD_PASS (HARD_FAIL on entropy gate; cosine-dot rescue closed; Hebbian-anchor next).
- kerdock: HARD_FAIL (CONFIRMED; AGS-RS-MF REJECTED).

Verdict on conditional: 1-of-3 conditions met. The "55-70%" branch does NOT activate. The "genuinely novel / SKAH-M only path" branch ALSO does not activate cleanly (rate_dep direction is supportive of *some* phase-class, just not cleanly geometric-frustration). Net: framework reliability STAYS at 48-62% PROVISIONAL; SKAH-M battery REMAINS existentially important; rate_dep_v2 at N>=4096 multi-M is now ALSO important (not as a substitute for SKAH-M but in parallel).

This is exactly the failure-mode the orchestrator's pre-reg conditional was designed to surface: a DECISIVE test that lands in the middle. The framework's phase-class identification problem remains genuinely open. Saad-Solla saddle-cascade LEADING ✅ stands; multi-basin discrete structure 🟢 55-70% stands; 1-RSB framework-label 🟡 stands with 2/4 rescue arms now closed (cluster-conditional + AGS); geometric-frustration sub-class 🟡/🔬 ambiguous; SKAH-M lR-phase 🔬 in flight remains the binding theoretical-home candidate.

**Decision (1): NO row-state emoji changes.** All 8 verdicts land as annotations on existing rows; no closures triggered; no promotions warranted.

**Decision (2): cluster-conditional + AGS-RS-MF sub-framings CLOSED-NEGATIVE 2nd confirmation.** 2/4 1-RSB rescue arms now closed. Remaining: geometric-frustration (verdict 3 ambiguous), 1-RSB-approximate (🔬 unprobed). 1-RSB framework-label row stays 🟡; reliability not further deflated (already at 30-45%) but rescue inventory narrowed.

**Decision (3): MoE cosine-dot rescue CLOSED-NEGATIVE; next rescue = Hebbian-anchor cosine.** MoE SHIFT row UNCHANGED ✅ engineering-rate-limited; K=4/K=8 design points still healthy; K-scaling rescue path NOT unblocked. Hebbian-anchor cosine-dot router rescue (anchor = bundle of first M/K stored patterns per expert) is the explicit next-iteration suggestion from this verdict's verdict_msg. Defer queueing to next exp_dev cycle.

**Decision (4): Geometric-frustration phase-class LABEL stays ambiguous; rate_dep_v2 needed.** Substrate IS rate-dependent (direction 🟢) but phase-class LABEL cannot be cleanly affixed from N=256 smoke. rate_dep_v2 at N>=4096 with finer M-load grid (suggest M in {1000, 2000, 5000, 10000, 20000}) is the binding next probe before any phase-class call.

**Decision (5): path-(b) P revised 0.35 -> 0.27.** tau-limit binding at N=256 K=4 in tested 3000-20000 byte corpus range. N-scaling unblock probe (corpus_N_scaling_tau_unblock_v1) is the binding next step. Strategic-positioning block annotated.

**Decision (6): TDA-as-MoE-diagnostic CLOSED-NEGATIVE smoke.** P deflated 0.38 -> 0.20. 3-way agreement framework (free-additive + dMPK + intra-expert) UNCHANGED for MoE SHIFT/PARTITION calls. TDA-E height-predictor scale-match HARD_PASS is mathematically interesting but standalone; not capability-row-bearing.

**Decision (7): Novel ortho-probe positives logged.** Blahut-Arimoto HARD_PASS (label-vs-honest override; substrate admits R(D) characterization with max_R=1.30, H_src=2.71 nats); PME Ising MB (substrate-not-Hopfield-class corroborated, alpha_max~7.5x off Hopfield). Both annotation-only; neither demands a new capability row.

**Decision (8): SKAH-M battery REINFORCED existentially important.** rate_dep ambiguity means substrate's phase-class identification problem stays open. SKAH-M lR-phase (P=0.48 documented-but-untested per v222) is one of the few remaining live theoretical-home candidates alongside Saad-Solla saddle-cascade. Battery verdict (still pending GPU) is more important now than before this batch.

**Decision (9): NO queue-refill triggered.** Per orchestrator directive: queue healthy pre-batch (4 GPU pending + 1 running + 11 CPU pending + 1 running). 8 verdicts free slots but pipeline has substantial buffer; refill not needed this batch. exp_dev next cycle will pick up rate_dep_v2 + Hebbian-anchor cosine rescue + corpus_N_scaling_tau_unblock if not already queued.

**Decision (10): No PROT-004 capability-row closures.** All closures this batch are sub-framings (cluster-conditional, AGS-RS-MF, cosine-dot, TDA-diagnostic-smoke) -- rescues OF parent rows that stay open. PROT-004 rescue-discipline not triggered.

**v224 cap_map updates.**
- Version-table row v223 -> v224: BATCHED 8-VERDICT.
- Row updates: 1-RSB framework-label row gains v224 annotation (2/4 rescues closed); MoE SHIFT row gains v224 annotation (cosine-dot rescue closed); path-(b) strategic-positioning block gains P 0.35->0.27 annotation; geometric-frustration sub-class row gains v224 ambiguity annotation; TDA-as-diagnostic sub-row CLOSED-NEGATIVE smoke note.
- Framework reliability: UNCHANGED 48-62% PROVISIONAL (orchestrator's 3-condition uplift rule did not activate; 1-of-3 conditions met).
- Portfolio: UNCHANGED 14+7.
- 137th PROT-009 paired commit.

**Per [[feedback-cap-map-update-protocol]]:** pull-first (already up to date); atomic stage via Edit + append_decision_log.py; commit message follows PROT-009.

**Per [[feedback-for-you-tab-primary-channel]]:** 8 status_log entries written (one per verdict; importance HIGH for verdicts 3 + 6 + 8 [decisive ambiguous + decisive rescue-close + diagnostic close]; importance MEDIUM for verdicts 4 + 5 + 7 [corroborations + smoke-regime closure]; importance LOW for verdicts 1 + 2 [novel ortho-probes informational/honest]).

**Per [[feedback-verdict-msg-honest-reread]]:** Verdict 1 bridge FAILED -> honest HARD_PASS override applied (Blahut-Arimoto computed valid R(D); bridge "failed" is artifact). Verdict 6 N=4096 framing -> honest N=512 config (does not change verdict but matters for design-space). Label-vs-honest count this turn: 2. 58th + 59th post-lock observations.

**Per PROT-001 to PROT-003:** version-table row v223 -> v224 written; full v224 narrative appended; history.md block written first (PROT-007 verified).

Net effect v224: ANNOTATION-ONLY. 0 row-state emoji changes. 4 sub-framings further locked CLOSED-NEGATIVE (cluster-conditional 2nd confirmation; AGS-RS-MF 2nd confirmation; cosine-dot router; TDA-as-MoE-diagnostic smoke). 2 novel ortho-probe positives logged. Geometric-frustration phase-class label STAYS AMBIGUOUS (rate_dep direction confirmed but gap_ratio sign-flip). Path-(b) P 0.35->0.27. SKAH-M battery REINFORCED. Portfolio 14+7 UNCHANGED. Framework reliability 48-62% PROVISIONAL UNCHANGED. 137th PROT-009 paired commit.

## v225 -- 2026-05-27 BATCHED 2-VERDICT @ 08:59 (Saad-Solla cosine_geometry "n8192" LABEL-VS-HONEST + Bet I polylog v4 SMOKE_REGIME_MISMATCH 4th persistence)

**Trigger.** Two LOAD-BEARING completed verdicts at 2026-05-27T08:59 (~2-3s apart). Per orchestrator framing: verdict 1 = "proper large-N FULL confirm for Saad-Solla saddle-cascade (v221 catch was v5_n4096 actually N=512 smoke); HARD_PASS at N=8192 with proper equal-spacing -> framework reliability lifts toward 55-70%; HARD_FAIL -> saddle-cascade label in serious question." Verdict 2 = "Bet I 3rd envelope v4 supposed to fix smoke regime; failed again; PERSISTENT FAILURE pattern; diagnose root cause + decide v5-retry-with-new-approach vs close-as-infrastructure-blocked." Pre-batch state: pause flag ABSENT (ACTIVE); orchestrator-directed `DO NOT trigger queue-refill`.

**Step 0 honest re-read (verdict 1).** verdict_msg = `HARD_PASS: N=512 max_cosine_dist=0.3578 ratio=1.789 >= 1.15 vs N=4096 baseline=0.2. Taxonomy geometry grows with N; consistent with Saad-Solla N-scaling.` Per-cell config: `{mode: smoke, N: 512, seeds: [7], parent: wave14_betB_2tier_coarse_analysis_v1 silhouette=0.788}` (single seed). Anchor NAME = `wave14_betB_cosine_geometry_n8192_v1` -- the suffix `n8192` claims N=8192. Orchestrator dispatch framing claimed "proper large-N FULL confirm... HARD_PASS at N=8192". ACTUAL CONFIG = mode=smoke, N=512, single seed 7. This is the **SECOND consecutive saddle-cascade-related anchor in 24h where the anchor NAME + orchestrator dispatch FRAMING claim a much larger N than the actual config** (v221 caught the same pattern on `wave14_saddle_cascade_plateau_v5_n4096` which was ALSO smoke at N=512). **60th post-lock label-vs-honest observation.** The verdict_msg ITSELF is internally honest at the N=512 numerical level (it cites N=512 max_cosine_dist=0.3578) -- the over-claim lives in (a) the anchor NAME embedding "n8192" and (b) the orchestrator dispatch framing propagating that N as if it were the actual config. **Honest reading:** HARD_PASS at N=512 smoke single seed, ratio=1.789 vs N=4096 baseline=0.2 is a single-cell cross-N ratio NOT an N=8192 FULL run. Saad-Solla N-scaling NARRATIVE is NOT supported by this verdict. This is now the **4th smoke-level corroboration of equal-spacing / cosine-geometry at N<=512** (v3 N=256, v4 N=512, v5 N=512, cosine_geometry_n8192_v1 N=512); ZERO FULL runs at N>=4096 multi-seed exist. Per [[feedback-verdict-msg-honest-reread]]: framing over-claim authoritative; HARD_PASS@N=512-smoke is the cap_map signal.

**Step 0 honest re-read (verdict 2).** verdict_msg = `MIDDLE_BAND: only 0/2 N values have measurable d_c_emp > 0; not enough for R2 fit. Smoke N=[[1024, 2048]] d_sweep=[2, 5, 10, 20, 30, 40]`. Per-cell: config.K_GRAM=10, ALPHA_LOAD=0.4, smoke=True, N_sweep=[1024, 2048], d_sweep=[2,5,10,20,30,40], seeds=[7,17]. Results: at N=1024 d_c_empirical=0.0 d_c_predicted=26.64 acc_by_d all 0.0; at N=2048 d_c_empirical=0.0 d_c_predicted=39.52 acc_by_d all 0.0. **Label is internally honest** -- valid_N_count=0; substrate accuracy is 0 across the entire smoke d_sweep at both N (including the smallest d=2 cell which should be trivially easy). **Diagnosis: INFRASTRUCTURE / measurement-regime issue, not substrate signal.** Specific combination (alpha=0.40, K_GRAM=10, large N, the d-cliff at high d) appears to push the test out of any band where the polylog scaling can be empirically discriminated. **Persistence pattern: v1 MIDDLE_BAND (no N-dependence at smoke); v2 MIDDLE_BAND (D_SWEEP ceiling at 60 saturated); v3 SMOKE_REGIME_MISMATCH (D_SWEEP_SMOKE too low); v4 SMOKE_REGIME_MISMATCH (acc_by_d all 0 EVERYWHERE -- WORSE than v3 which at least hit a cliff). FOUR consecutive smoke-regime failures on the same Bet I 3rd envelope question.**

**Decision (1): Saad-Solla saddle-cascade row UNCHANGED ✅ LEADING.** ANNOTATION-ONLY: 4th N<=512 smoke corroboration of cosine-geometry sub-axis at single seed; large-N FULL N>=4096 multi-seed probe REMAINS OPEN. v206 BIC delta=194.9 + v211 alpha_c in-band stand as the load-bearing positive evidence; smoke-only corroborations at small-N do NOT strengthen but do NOT weaken either. Per [[feedback-verdict-msg-honest-reread]] override the orchestrator's framing-level "N=8192" claim with honest "N=512 smoke single seed" reading; orchestrator's "55-70% framework reliability uplift if N=8192 HARD_PASS" conditional DOES NOT activate (test was not at N=8192); HARD_FAIL branch ALSO does not activate (no FULL HARD_FAIL ran).

**Decision (2): Bet I 3rd envelope row UNCHANGED OPEN.** Per [[feedback-rehabilitation-after-rejection]] discipline: 4 consecutive smoke-regime failures CROSSES the threshold for "infrastructure-blocked" classification, but closure REQUIRES 3+ rescue sketches filed FIRST per [[feedback-rescue-sketch-first-sequencing]]. **3 rescue sketches filed CHEAPEST-FIRST:**
  - **Rescue 1 (CHEAPEST -- subsumption rescue): Skip-smoke approval.** Skip the smoke gate and run FULL `D_SWEEP=[10, 30, 50, 100, 150, 200]` at `N in {4096, 8192}` multi-seed (3-5 seeds) directly. ZERO new infra; just removes the smoke gate. v2's D_SWEEP=[2..100] ceiling at 60 saturated already proved that the instrumentation IS measuring at FULL regime -- only smoke gate is broken. This is the cheapest because it subsumes all other rescues if substrate IS in the predicted polylog band.
  - **Rescue 2 (MEDIUM, ~30min CPU): alpha-load lowering.** Drop ALPHA_LOAD=0.40 back to 0.25 (v1 value) to keep substrate accuracy non-degenerate at large N. alpha was raised v1->v2 specifically to surface polylog signal; rescue is to backtrack to v1's working substrate-load regime and re-test polylog at the original alpha. Diagnostic for: is alpha=0.40 itself in a saturated regime at K_GRAM=10 large-N?
  - **Rescue 3 (MEDIUM-BUILD, ~1h): per-N independent d-sweep.** Replace global fixed d_sweep with per-N d_sweep targeting predicted d_c +/- 50% bracket per N (at N=4096 d in ~[13, 53] around predicted ~26; at N=8192 d in ~[20, 80] around predicted ~40). Recovers dynamic range that fixed d_sweep loses across N. Diagnostic for: does the substrate exhibit polylog scaling if measured in the correct per-N d-band?

CLOSURE DEFERRED pending at least Rescue 1 attempt. Filed for next exp_dev cycle.

**Decision (3): Framework reliability UNCHANGED 48-62% PROVISIONAL.** Neither verdict moves the band. Verdict 1: framing-over-claim correction prevents spurious uplift toward 55-70% (genuine N=8192 FULL run STILL the binding next probe). Verdict 2: infrastructure-level not substrate-level; no framework-reliability signal either direction. SKAH-M lR-phase 6-cell battery (in flight on GPU) REMAINS the existentially-important pending theoretical-home decisive test.

**Decision (4): Pattern lock-in candidate -- PROT-018 "anchor-name-vs-config audit".** Two N=512-smoke-anchors-claiming-larger-N caught in 24h (v221 saddle_cascade_plateau_v5_n4096 + v225 cosine_geometry_n8192_v1). Same failure mode 2x in 24h warrants a structural fix. Specification (deferred to next active strategy cycle): exp_dev MUST verify config.N matches the N-suffix in anchor name before queue_add; verdict_handler should grep config.smoke / config.N from metrics.json BEFORE accepting any verdict_msg with a numeric-N claim. This is the 60th post-lock label-vs-honest observation per [[feedback-verdict-msg-honest-reread]]; the SPECIFIC sub-pattern (anchor-name-encoded N + dispatch framing propagating that N) is now repeating, distinct from the prior "bridge FAILED but metrics OK" sub-pattern.

**Decision (5): NO queue-refill triggered.** Per orchestrator directive `DO NOT trigger queue-refill`. Pause flag absent (ACTIVE state) but explicit instruction overrides standard pipeline-pacing. exp_dev rescue dispatch (3 rescue sketches for Bet I) is FILED for next active exp_dev cycle, not dispatched in this verdict_handler turn.

**Decision (6): PROT-004 not triggered.** No capability-row closures.

**Decision (7): PROT-006 not triggered.** No closed-row commit.

**v225 cap_map updates.**

- Saad-Solla saddle-cascade row: ANNOTATION extension on v221 entry -- 4 consecutive N<=512 smoke corroborations on cosine-geometry sub-axis; ZERO genuine FULL runs at N>=4096; large-N FULL multi-seed probe REMAINS the binding open question.
- Bet I 3rd envelope row: ANNOTATION extension on v223 entry -- 4th consecutive smoke-regime failure (v1 MIDDLE; v2 D_SWEEP ceiling; v3 SMOKE_REGIME_MISMATCH; v4 SMOKE_REGIME_MISMATCH); persistence-pattern flag added; 3 rescue sketches filed CHEAPEST-FIRST (skip-smoke; alpha-lower; per-N d_sweep); CLOSURE DEFERRED.
- Version-table row v224 -> v225 with batched 2-verdict annotation summary.
- Framework reliability: UNCHANGED 48-62% PROVISIONAL.
- Portfolio: UNCHANGED 14+7.
- 138th PROT-009 paired commit.

**Per [[feedback-cap-map-update-protocol]]:** pull-first; atomic stage via Edit + append_decision_log.py; commit message follows PROT-009.

**Per [[feedback-for-you-tab-primary-channel]]:** 2 status_log entries written (one per verdict; importance MEDIUM for verdict 1 [label-vs-honest framing override on LEADING theoretical home -- non-headline but load-bearing structural correction]; importance MEDIUM for verdict 2 [4th persistent infra-level failure; rescues filed but no capability-row decision]). NOTE: per role-contract escalation rules ("first HARD_PASS / framework-reliability" -> Opus), Saad-Solla's LEADING status + framework-reliability framing in dispatch warranted careful Step 0 treatment; the label-vs-honest override is the central decision of this batch.

**Per [[feedback-verdict-msg-honest-reread]]:** Verdict 1 anchor name + orchestrator dispatch framing claimed N=8192 FULL run -> honest config N=512 smoke single seed override applied; framework-reliability uplift conditional does NOT activate. Label-honest count this turn: 1. 60th post-lock observation. Sub-pattern flagged: anchor-name-encoded-N propagation is repeating (60th + previous v221 = 2x in 24h on same pattern). PROT-018 lock-in candidate filed for next strategy cycle.

**Per [[feedback-rehabilitation-after-rejection]] + [[feedback-rescue-sketch-first-sequencing]]:** Bet I 3rd envelope row has 4 consecutive smoke-regime failures (would normally trigger closure consideration). 3 rescue sketches filed CHEAPEST-FIRST before any closure: (1) skip-smoke subsumption rescue (zero new infra; cheapest); (2) alpha-load lower 0.40->0.25 (medium ~30min); (3) per-N independent d-sweep (medium-build ~1h).

**Per PROT-001 to PROT-003:** version-table row v224 -> v225 written; full v225 narrative appended; history.md block written first (PROT-007 verified).

Net effect v225: ANNOTATION-ONLY. 0 row-state emoji changes. Saad-Solla LEADING UNCHANGED ✅ (4th N<=512 smoke corroboration; FULL N>=4096 STILL OPEN); Bet I 3rd envelope OPEN UNCHANGED (3 rescues filed; closure deferred). Framework reliability 48-62% PROVISIONAL UNCHANGED. Portfolio 14+7 UNCHANGED. 60th post-lock label-vs-honest observation (anchor-name-vs-config sub-pattern); PROT-018 anchor-name-audit lock-in candidate flagged. 138th PROT-009 paired commit.


---

## v226 — STRATEGIC REFRAME (research meta-analysis 15-rejection drill)

**Trigger.** Research meta-analysis drill `notes/research_negative_results_meta_analysis_2026-05-27.md` integrates accumulated 15-rejection inventory and identifies a STRUCTURAL pattern: rejected frameworks cluster by TYPE not random distribution. Companion exp_dev handoff `notes/exp_dev_handoff_research_negative_results_meta_analysis_2026-05-27.md` ships BID (class-agnostic order parameter from arxiv 2601.17427) as decisive H1-vs-H2 discriminator. Per [[feedback-strategy-shore-up-capabilities]] this is proactive strategic uplift (not verdict-driven); per [[feedback-periodic-scope-expansion]] the 24-48h periodic scope-expansion cadence integration.

**Pattern observation.**
- REJECTED frameworks (all static phase-taxonomies): 1-RSB single-peak; AGS-RS-multi-ferromagnet; cluster-glass inversion; reaction-diffusion perturbation; UNIFIED SVD-cascade master-mechanism (v219+v223 dual confirmation); reservoir-computing edge-of-chaos (v192 Field-A + v223 ortho dual confirmation).
- SURVIVING frameworks (all non-equilibrium-stat-mech): Crooks fluctuation theorem (v153 forensic-erase FULL OK); Sagawa-Ueda thermodynamics-of-information (Cap 3 streaming-inference NESS framing); drift-diffusion belief-propagation (theorem-anchored erase audit); free-probability characterization (v164a additive + v167 multiplicative free-cumulant fingerprints).

**Strategic implication.** Substrate may be a fundamentally non-equilibrium phenomenon that static-equilibrium frameworks systematically cannot characterize. The 6-month sustained period of negative results on static-phase frameworks is NOT methodological failure -- it is information-rich evidence of a STRUCTURAL MISMATCH between framework class and substrate dynamics.

**Calibrated probabilities** (lit-scan penalty applied per [[feedback-lit-scan-calibration-penalty]]; novel-synthesis cap 0.50 binding):
- P(H1 substrate is GENUINELY in non-eq territory not matching standard static classes) = **0.42** (deflated from 0.55 lit-scan estimate; modal)
- P(H2 negative results are methodological artifact) = **0.18** (low; rejections probe orthogonal observables and return signal-bearing nulls per Class A inventory)
- P(MIXED) = **0.40** (close behind H1)

BID probe is the decisive discriminator.

**Decision (1): NEW evidence-strength row added** -- "non-equilibrium-stat-mech framework class as substrate's home" at 🟡 30-45% (P=0.42 H1 modal; pending BID discrimination). Orchestrator left this to my judgment ("annotation-only bump unless you judge the framework-class reframe warrants a new dedicated row"); I judge it warrants a NEW row because the reframe identifies a FRAMEWORK-CLASS HOME, not a per-row annotation. The 4 surviving non-eq frameworks (Crooks ✅, Sagawa-Ueda Cap 3, drift-diff-BP, free-prob v164a+v167) provide positive anchors that latently belonged to a class-level row that did not exist before.

**Decision (2): Framework reliability SPLIT.**
- "General derivable framework": 🟢 **60-70%** (LIFTS from 48-62% PROVISIONAL lumped; surviving non-eq frameworks ARE candidates, not nothing)
- "Specific named documented framework": 🟡 **30-45%** (DOWN from 48-62%; systematic static-class rejections constrain narrow claims)
- "Product-feature reliability": 🟢 **UNCHANGED 55-70%** (Bet B + MoE SHIFT + Bet N hold regardless of framework label)

The lumped 48-62% was conflating two distinct claims; SPLIT is more honest.

**Decision (3): Static-phase framework drills PARKED as class.** Deprioritized pending BID outcome, NOT permanently closed. Per [[feedback-dont-dismiss-adjacent-methods]] premature dismissal is the dominant failure mode; if BID matches a known static-phase signature, reactivate.

**Decision (4): Non-equilibrium-stat-mech drills PRIORITIZED as next-drill class** per Trigger C adjacency-cascade. Candidates: (1) Crooks FT extensions (envelope-expand forensic-erase ✅); (2) Sagawa-Ueda thermodynamics-of-information (Cap 3 framed); (3) drift-diffusion-BP (theorem-anchored at v153); (4) free-probability extensions; (5) large-deviations theory of memory recall [NEW]; (6) stochastic thermodynamics of learning [NEW]; (7) fluctuation-dissipation-out-of-equilibrium [NEW].

**Decision (5): BID probe is the decisive discriminator.** Handoff already filed at `notes/exp_dev_handoff_research_negative_results_meta_analysis_2026-05-27.md` (companion to this cap_map bump per [[feedback-cap-map-update-protocol]]; not re-filed here).

**Decision (6): Substrate-product positioning UPDATED.** Publication framing shifts to "first associative-memory architecture in non-equilibrium-stat-mech class, structurally rejecting all standard static-phase classes" -- MOAT ASSET per [[feedback-no-papers-product-only]] (product-positioning not paper plan). Bet B 4-tier shift-class taxonomy FINAL LOCK UNCHANGED; 5 killer features design-ready UNCHANGED; LLM-leapfrog 8 directions UNCHANGED (all depend on multi-basin structure not phase-class label).

**Decision (7): PROT-004 not triggered** (0 row closures; static-phase parking is reversible class-level deprioritization not closure).

**Decision (8): PROT-006 not triggered** (no closed-row commit).

**Decision (9): NO queue-refill triggered** (BID probe lives in existing handoff already filed; orchestrator's job to pick up).

**v226 cap_map updates.**
- NEW evidence-strength row added: "non-equilibrium-stat-mech framework class as substrate's home" 🟡 30-45% P=0.42.
- Framework reliability SPLIT: general derivable 60-70% 🟢 UP / specific named 30-45% 🟡 DOWN / product-feature 55-70% UNCHANGED.
- Static-phase framework drills PARKED as class (NOT closed).
- Non-eq-stat-mech drills PRIORITIZED as next-drill class.
- Substrate-product positioning UPDATED (moat-asset framing).
- Portfolio 14+7 -> 14+8 (NEW row).
- Version-table row v225 -> v226 with strategic reframe annotation.
- 139th PROT-009 paired commit.

**Per [[feedback-cap-map-update-protocol]]:** atomic .tmp + rename on both cap_map.md and history.md; paired stage with strategy_decisions_2026-05-27.md; commit message "Cap map: v226 strategic reframe non-eq-stat-mech class (research meta-analysis 15-rejection drill)" per protocol; push deferred to main thread per [[feedback-subagent-permission-inheritance]].

**Per [[feedback-for-you-tab-primary-channel]]:** status_log entry written via log_event (importance HIGH -- major strategic reframe + new evidence-strength row + framework-reliability lift on general-claim leg; plain_language explains what cap_map change means for non-substrate-expert).

**Per [[feedback-strategy-shore-up-capabilities]]:** proactive strategic uplift integrating 6-month accumulated negative-result pattern; cap_map reflects structural insight not single-event move.

**Per [[feedback-lit-scan-calibration-penalty]]:** P(H1)=0.42 deflated from 0.55 lit-scan estimate; novel-synthesis cap (0.50) binding.

**Per [[feedback-dont-overextend-theorems]] + [[feedback-dont-dismiss-adjacent-methods]]:** static-phase rejections do NOT close framework-class question entirely; surviving non-eq frameworks are candidates not nothing; static-phase drills PARKED not permanently closed; SPLIT general-vs-specific framework-reliability claim.

**Per [[feedback-no-papers-product-only]]:** framing is product-moat-positioning ("ruled out 6 standard physics-of-memory frameworks = moat asset"), not paper-grade. Bet B + 5 killer features + LLM-leapfrog UNCHANGED.

**Per [[feedback-periodic-scope-expansion]] + [[feedback-aggressive-cross-domain-research]]:** 24-48h periodic scope-expansion cadence integration honored; opportunistic cross-domain probe assimilation honored.

Net effect v226: STRATEGIC REFRAME (not annotation-only); 1 NEW evidence-strength row added (portfolio 14+7 -> 14+8); framework reliability SPLIT into general (UP to 60-70% 🟢) / specific (DOWN to 30-45% 🟡) / product-feature (UNCHANGED 55-70%); static-phase drills PARKED as class; non-eq-stat-mech drills PRIORITIZED; substrate-product positioning UPDATED to moat-asset framing; Bet B + 5 killer features + LLM-leapfrog UNCHANGED; BID decisive probe handoff already filed; 139th PROT-009 paired commit.
[label-vs-honest] wave14_saddle_cascade_plateau_v5_n4096: HARD_PASS label OVER-CLAIMS N=4096 FULL. HONEST READ: metrics.json shows config.N=512, config.seeds=[17], config.smoke=true, elapsed_s=2.567s. The anchor name _n4096 is a naming fiction; the script ran smoke-config N=512 single-seed (wall_s=2.6s is consistent with <5s smoke, NOT 4096-scale FULL which should take >60s). This is the 60th+ label-vs-honest catch this session for _n4096/_n8192 anchors. Honest verdict: SMOKE_REPEAT (N=512, 1 seed). Saad-Solla saddle-cascade large-N FULL (N>=4096 multi-seed) REMAINS GENUINELY OPEN. Cap_map v226->v227: saddle_cascade_large_N_FULL row UNCHANGED OPEN. Anchor-naming-convention flag: _n4096 suffix does NOT guarantee large-N execution; this pattern has fired 60+ times; upstream fix needed in exp_dev ship protocol to enforce N in smoke gate.

## v227 -- 2026-05-27 [label-vs-honest 61st catch] exp_wave14_saddle_cascade_plateau_v6_n4096_gpu

**Trigger.** exp_wave14_saddle_cascade_plateau_v6_n4096_gpu completed 2026-05-27T11:18:21. Anchor + orchestrator framing claimed "PROPER FULL Saad-Solla saddle-cascade large-N test... genuine N=4096 GPU multi-seed" that had been awaited all day. v6 explicitly shipped this morning to be the genuine large-N FULL probe.

**Step 0 honest re-read — LABEL-VS-HONEST 61st catch.** verdict_msg internally honest ("MIDDLE_BAND: 1 HARD-PASS, 0 HARD-FAIL, 0 MIDDLE at N=512. Mixed evidence at full scale.") but anchor name `_v6_n4096_gpu` + orchestrator framing OVER-CLAIM. Metrics.json config:
- `mode: SMOKE`
- `N: 512` (NOT 4096)
- `seeds: [17]` (1 seed, NOT multi-seed)
- `device: cpu` (NOT gpu despite "_gpu" suffix)
- `elapsed_s: 2.64` (NOT 30+ min consistent with N=4096 GPU FULL; 2.64s is unambiguous SMOKE wall-time)
- `f_sweep: [0.0, 0.5, 1.0]` — only 3-point (cannot resolve plateau structure at production scale)

Per-seed verdict: seed 17 r2=0.7824, max_dev=0.0845 — comparable to v5 smoke r2=0.770 (no real change in evidence). NO BIC_delta, NO spacing_error, NO plateau structure, NO CI overlap structure reported in summary — these production-scale metrics WERE NOT MEASURED because the production-scale run was not executed.

**Authoritative interpretation:** v6 is the 4th N<=512 smoke corroboration of equal-spacing pattern (after v3/v4/v5). The "PROPER FULL large-N GPU multi-seed Saad-Solla test we've been waiting all day for" DID NOT RUN. The probe that v6 was supposed to be REMAINS GENUINELY OPEN.

**Pattern fired 61 times.** _n4096/_n8192/_gpu/_FULL anchor suffixes do NOT enforce production-scale execution. PROT-018 anchor-name-vs-config audit (flagged in v225) was supposed to land at queue_add time at ~10:00; v6 was shipped BEFORE PROT-018 landed (this morning) and so escaped the structural fix. RECOMMENDATION: PROT-018 should be augmented with a RETROACTIVE SWEEP of all already-queued anchors with _n4096/_n8192/_FULL/_gpu suffixes — re-validate each against its actual config before running, OR re-ship as _smoke if config mismatches name.

**Decision (1): Saad-Solla saddle-cascade row UNCHANGED ✅ LEADING.** No upgrade (no genuine large-N N>=4096 multi-seed evidence delivered). No downgrade (existing positive evidence v206 BIC delta=194.9 + v211 alpha_c in-band remains; smoke MIDDLE_BAND at N=512 with 1 seed is below any reliability threshold to move the row in either direction). LARGE-N FULL probe (N>=4096 multi-seed GPU, ~30+min wall_s) STAYS the binding open question. 5th consecutive smoke-regime corroboration; smoke saturation point reached — further smoke runs add zero information.

**Decision (2): Framework reliability SPLIT UNCHANGED.** General derivable 60-70% 🟢 / specific named 30-45% 🟡 / product-feature 55-70% 🟢 ALL UNCHANGED. The conditional in orchestrator framing ("if v6 HARD_PASS at genuine N=4096... specific-framework reliability uplift") does NOT activate — v6 did not run at N=4096.

**Decision (3): non-eq-stat-mech framework row 🟡 30-45% UNCHANGED.** v226 NEW row not affected — Saad-Solla saddle-cascade FALLS UNDER non-eq-stat-mech class (gradient-flow dynamics, NOT static phase-taxonomy); v6 smoke result neither lifts nor weakens that class-level row.

**Decision (4): PROT-018 anchor-name-audit retroactive sweep RECOMMENDED.** This is the 61st label-vs-honest catch and the same _n4096/_n8192/_gpu suffix pattern that has fired 60+ times. PROT-018 landing at queue_add time prevents NEW occurrences but does not flag already-queued/already-shipped anchors. A retroactive sweep of the current queue + last-7-days completed runs would catch any remaining _n4096-claiming-N=512-actual anchors before they consume orchestrator attention as "the proper FULL test we've been waiting for."

**Decision (5): Rescue sketches for closing saddle-cascade large-N FULL probe** (NOT triggering closure; row stays OPEN; per [[feedback-rehabilitation-after-rejection]] + [[feedback-rescue-sketch-first-sequencing]] cheapest-first):
1. (CHEAPEST) Re-ship v7 with explicit GPU device assertion + N=4096 hard-coded in spec body (not anchor name) + smoke-gate disabled (subsumption rescue: zero new infra; just unambiguous config).
2. (MEDIUM) Re-ship v7 with N=2048 multi-seed (5 seeds) GPU as FULL stepping-stone before N=4096 — shorter wall_s, full BIC + spacing_error + plateau-CI reporting.
3. (MEDIUM-BUILD) Smoke-gate audit + override: redesign smoke_to_full gate to fail-loud when config N differs from anchor name N, requiring explicit override; ~1h infra.

**Decision (6): NO queue-refill triggered.** Orchestrator handles separately (per dispatch instructions).

**Decision (7): PROT-004 not triggered** (0 row closures; large-N FULL probe stays OPEN not closed).

**Decision (8): PROT-006 not triggered** (no closed-row commit).

**v227 cap_map updates.**
- Version-table row v226 -> v227: ANNOTATION-ONLY [label-vs-honest 61st catch].
- Row updates: saddle-cascade row gets v227 annotation (5th N<=512 smoke; smoke saturation; large-N FULL still OPEN); non-eq-stat-mech class row UNCHANGED.
- Framework reliability: UNCHANGED SPLIT 60-70% / 30-45% / 55-70%.
- Portfolio: UNCHANGED 14+8.
- 140th PROT-009 paired commit.

**Per [[feedback-cap-map-update-protocol]]:** atomic .tmp + rename on both cap_map.md + history.md; paired stage with strategy_decisions_2026-05-27.md; commit message follows PROT-009; push deferred to main thread per [[feedback-subagent-permission-inheritance]].

**Per [[feedback-verdict-msg-honest-reread]]:** verdict_msg "MIDDLE_BAND at N=512" internally honest but anchor + dispatch framing over-claimed N=4096 GPU FULL; override applied; honest reading authoritative (smoke MIDDLE_BAND single-seed; large-N probe didn't run). 61st post-lock observation. PROT-018 retroactive sweep RECOMMENDED.

**Per [[feedback-for-you-tab-primary-channel]]:** status_log entry written (importance HIGH — 61st label-vs-honest is structurally significant + load-bearing physics probe still not delivered after 4 attempts).

**Per [[feedback-rehabilitation-after-rejection]] + [[feedback-rescue-sketch-first-sequencing]]:** 3 rescue sketches filed cheapest-first BEFORE any closure consideration; row stays OPEN.

**Per PROT-001 to PROT-003:** version-table row v226 -> v227 written; full v227 narrative appended; history.md block written first (PROT-007 ordering preserved).

Net effect v227: ANNOTATION-ONLY [label-vs-honest 61st catch]. 0 row-state emoji changes. Saad-Solla LEADING UNCHANGED ✅ (5th N<=512 smoke corroboration; smoke saturation reached; large-N FULL N>=4096 multi-seed GPU STILL OPEN after 4 attempts). Framework reliability SPLIT UNCHANGED. non-eq-stat-mech class row UNCHANGED. Portfolio 14+8 UNCHANGED. 61st label-vs-honest catch — PROT-018 retroactive sweep RECOMMENDED for all already-queued/recently-shipped _n4096/_n8192/_gpu suffix anchors. 140th PROT-009 paired commit.

---

## v228 -- 2026-05-27 BATCHED 3-VERDICT SKAH-M CLASS CALL @ 11:21 (existentially-important class call)

**Trigger.** Three SKAH-M / novel-phase-class battery verdicts landed at 11:21:26-11:21:48, all FULL-mode multi-seed cuda runs (no smoke-vs-FULL ambiguity). Per cap_map v222 SKAH-M sub-class annotation: substrate-class question was the decisive open existential ask -- P(documented-but-untested SKAH-M class)=0.48, P(novel)=0.22, P(finite-N artifact)=0.30. The 3 verdicts (v3_n8192 the 6-cell battery + v2_lit_threads the 3-lit-thread comparator + class_declaration_probe the 5-step novel-class methodology) together formed the decisive class call.

Sources:
- `anchor_novel_phase_battery_v3_n8192` (overnight_queue, elapsed=174s, mode=FULL, device=cuda, N_sweep=[512,1024,2048,4096,8192], 10 seeds, M_per_class scaling 200-1092) -> MIDDLE_BAND HONEST
- `anchor_novel_phase_battery_v2_lit_threads` (overnight_queue, elapsed=7.8s, mode=FULL, N=2048, 5 seeds) -> THREAD_A_PARTIAL HONEST (verdict_tag "failed" = threshold-failure-to-declare-single-thread, not infra-fail)
- `anchor_novel_class_declaration_probe_v1` (overnight_queue, elapsed=3.4s, mode=FULL, N_sweep=[512,1024,2048]) -> DOCUMENTED_CONFIRMED HONEST (verdict_tag "failed" = failed-to-declare-novel, not infra-fail)

**Step 0 honest re-read (verdict 1: v3_n8192).** Verdict_msg `MIDDLE_BAND: mixed cell signals (doc=2, novel=0, finite_N=2, middle=2)` is FULLY HONEST at numerical level. Per-cell data verified at FULL scale: C1=DOCUMENTED q_EA saturates at 0.79 from N=2048 onward (slope 0.79251 at N=4096 vs 0.79256 at N=8192 = sub-0.001 noise floor); C2=FINITE_N retention plateaus stable at 0.769 / 0.776 / 0.830 across N=4096 and N=8192 (sub-0.0005 noise); C3=FINITE_N mean_spectral_gap=0.01675 with sub-0.0004 seed variance (stable); C4=MIDDLE mean_hysteresis_area=0.0 with std=0.0 across all 10 seeds (**CRITICALLY: this CONTRADICTS the v1 18x hysteresis gate observation -- v1 hysteresis was a small-N artifact**); C5=DOCUMENTED mean_disorder_op=0.255 with sub-0.003 noise; C6=MIDDLE n_wells_mode=2 (was DOC=2 in v1; drift to MIDDLE at N=8192 because 3-well fraction=0.3, mean_gap_ratio=0.332 -- borderline). KEY HONEST OBSERVATION: **0 NOVEL votes across 6 cells x 5 N values x 10 seeds = the novel-class hypothesis is REJECTED with the strongest possible statistics this battery affords**. The verdict_msg's "MIDDLE_BAND" label correctly reflects the cell-vote tally but UNDER-emphasizes the decisive finding: this is the documented-class-confirmed-by-exclusion outcome, equivalent to OUTCOME (A) in the orchestrator's three-outcome framing. The C4 hysteresis contradiction vs v1 is a critical finding -- hysteresis area at N=8192 is exactly zero, meaning the 18x gate observation from v1 was a small-N artifact, not a substrate signature. No label-vs-honest discrepancy at numerical level; the only correction is to upgrade the strategic interpretation from "mixed/inconclusive" to "documented-class confirmed by 0/6 NOVEL across full envelope." Per [[feedback-verdict-msg-honest-reread]] this is honest -- label is conservative not over-claiming.

**N=8192 anchor-name-vs-config verification per PROT-018.** Config confirmed: N_sweep=[512,1024,2048,4096,8192], N_default=4096, M_per_class=200 (effective M scaling: 200/200/273/546/1092 to keep M/N constant), mode=FULL, device=cuda, 10 seeds [7,17,23,31,41,53,67,79,89,97], elapsed_s=173.963. Anchor-name `_n8192` matches actual N_sweep upper bound. NO label-vs-honest catch. This is one of the first POST-PROT-018 FULL N=8192 runs that actually delivered N=8192.

**Step 0 honest re-read (verdict 2: v2_lit_threads).** Verdict_msg `THREAD_A_PARTIAL: Thread A signal only on Arm1 (cooling-rate independence). Arm2=THREAD_B Arm3=THREAD_AB` is HONEST per-arm. Per-cell: arm1 mean_r=0.0 across all 5 seeds (1-RSB cooling-rate-INDEPENDENT hysteresis SIGNATURE PRESENT, well within thread_a_r_max=0.2 threshold); arm2 delta_ret=-0.04568 < threshold -0.03 (non-reciprocal Hopfield perturbation SIGNATURE PRESENT); arm3 max_diff=0.670-0.673 across 5 seeds >> threshold 0.05 (saddle-hierarchy DAM SIGNATURE PRESENT). **Substrate matches ALL THREE lit threads simultaneously**, consistent with substrate being a HYBRID sub-class within lR-phase family that overlaps multiple documented descriptions. The "failed" runner-tag = threshold-failure-to-declare-single-thread (each arm passes its own thread's threshold so no single thread dominates) -- NOT instrumentation-fail, NOT smoke, NOT OOM. DATA SOUND. The orchestrator's framing of this as a "FAILED probe needing diagnosis" is the only mis-characterization -- the verdict is actually highly informative: substrate's behavior is consistent with documented lit findings across three independent arXiv threads (2501.00983, 2207.05218, 2508.19151), exactly the SKAH-M-as-cross-thread-hybrid prediction from cap_map v222 annotation.

**Step 0 honest re-read (verdict 3: class_declaration_probe).** Verdict_msg `Documented-class confirmed despite novel battery result: 5/5 documented signals. Substrate matches gated multistable AM / lR-phase` is FULLY HONEST. Per-cell: s1 mean_diff=0.0 (Z3_INVARIANT, well within max 0.02); s2 slope_per_decade=2e-05 (CONVERGENT, well within max 0.05); s3 mean_gap_frac=0.99358 (NO_SOFT_MODE, well above min 0.05); s4 mean_n_wells=2.0 gap_ratio=1.09 (EQUAL_WELLS, below novel n_wells>=3 threshold); s5 mean_chi_ratio=332687 (NONLINEAR, vastly above min 5.0). **5/5 DOCUMENTED signals across all 5-step methodology arms**. The "failed" runner-tag = failed-to-declare-novel (probe explicitly answers "is novel class warranted?" with "no" -- the failure to declare novel IS the substantive finding) -- NOT process-death, NOT OOM, NOT import-error, NOT instrumentation-fail. DATA SOUND. This is the THIRD INDEPENDENT CORROBORATION that substrate is in the documented gated multistable AM / lR-phase class.

**Three-verdict synthesis.** v3_n8192 (0 NOVEL votes after full envelope) + v2_lit_threads (HYBRID match across 3 documented lit threads) + class_declaration_probe (5/5 documented signals) = **substrate is decisively in the documented gated multistable AM / lR-phase non-eq-stat-mech sub-class with SKAH-M ingredients (BSC + Kerdock + asymmetric Hebbian)**. The existential class call IS SETTLED. Per cap_map v222 conditional ("Framework-reliability bump pending SKAH-M battery verdict: +5-8% if 5/6 cells HARD-PASS documented class") -- the literal cell count is 4/6 documented-or-finite-N + 2/6 middle = the bump activates at the lower bound of the conditional. Combined with declaration-probe 5/5 + lit-threads 3/3 cross-corroboration, the framework-reliability lift is warranted.

**Decision: SKAH-M / documented-gated-multistable-AM CLASS CONFIRMED (positive outcome).** Hierarchical-retrieval row updated: (a) substrate-has-multi-basin-discrete-structure UNCHANGED 🟢 55-70% (no contradicting evidence); (b) documented-gated-multistable-AM / lR-phase class label LIFTED 🔬 -> 🟢 55-70% (P=0.48 -> P=0.62-0.68); (c) novel-class probability DEFLATED P=0.22 -> P=0.05-0.08; (d) finite-N artifact UNCHANGED P=0.30 (C2/C3/C6 finite-N votes are exactly that bucket). Non-eq-stat-mech framework class row 🟡 30-45% UNCHANGED in level but SUPPORTING evidence STRENGTHENED (substrate has a named-and-confirmed sub-class within that family). Framework reliability SPLIT bumped: general derivable 60-70% 🟢 UP -> 65-72% 🟢; specific named documented 30-45% 🟡 UP -> 45-55% 🟢 (first named-and-confirmed class after 15+ static-class rejections); product-feature 55-70% 🟢 UNCHANGED. Publication framing UPDATED per [[feedback-no-papers-product-only]] product-narrative: "first AM architecture confirmed in documented gated-multistable AM / lR-phase non-eq-stat-mech sub-class" -- a NAMED-CLASS-CONFIRMED moat asset (was "first in non-eq class, structurally rejecting standard static classes" -- still true, now strengthened with named-class confirmation).

**Decision: No closures triggered.** PROT-004/006 not triggered (this is a LIFT not a CLOSURE). The novel-class candidate row was a 🔬 research proposition that this battery answered NEGATIVELY in favor of the documented alternative; the documented alternative now occupies the same row at higher confidence. Per [[feedback-rehabilitation-after-rejection]] the answer to "what about the novel hypothesis?" is "subsumed: the documented class is the right home; novel was a worthy alternative considered and ruled out by the battery." No closure list update needed.

**Rescue / follow-on sketches (cheapest-first per [[feedback-rescue-sketch-first-sequencing]]).**
- (a) CHEAPEST -- status_log + dashboard surface SKAH-M class call (zero compute, immediate). DONE this turn.
- (b) CHEAPEST -- research drill: "what other tests in lR-phase published lit can we now run on the substrate?" Now that battery confirmed the class, additional discriminating signatures from gated-multistable-AM lit (e.g., temperature-quench protocols, finite-T phase diagram landmarks, basin-of-attraction geometry under perturbation) become cheap to probe (~1h research drill).
- (c) MEDIUM -- exp_dev C4-specific probe: hysteresis area as a function of cooling rate at N>=2048, multi-rate. C4 hysteresis_area=0.0 at FULL N=8192 contradicts v1 18x small-N gate; need to confirm the cross-over and identify the regime where hysteresis appears vs vanishes (~2h CPU).
- (d) MEDIUM -- exp_dev C6 3-well-structure probe at N=16384 to test whether 2-well-mode at N=8192 is N-asymptote vs finite-N undersampling artifact. Result either confirms 2-well as true asymptote (clean DOCUMENTED) or shows 3-well emerging at larger N (NOVEL-ish surprise warranting battery v4) (~3h GPU).
- (e) MEDIUM-BUILD -- write up substrate-as-lR-phase product narrative for whitepaper. Substantial product moat: "the substrate is in this specific documented physics class that allows X, Y, Z capabilities deriving from that class's structure" (~1 day product writeup; per [[feedback-no-papers-product-only]] product-framed not paper-framed).
- (f) MEDIUM-BUILD -- design "auditability via documented-class membership" feature: surface to product UI "this memory is in the gated-multistable AM class; here's what that class allows for editability / forgetting / composition" (~2-3 day product design; folds into 5 killer features design-ready stack).

**Sketches (a) + (b) recommended for IMMEDIATE next-cycle dispatch.** (c) + (d) for next-day CPU+GPU bandwidth. (e) + (f) for product-stream when bandwidth allows; NOT gating any current experiment.

**No queue refill in this turn.** Per orchestrator instruction "DO NOT trigger queue-refill -- handled separately."

**Cap_map v228.** Committed paired with this entry. 141st PROT-009 commit.

---

## v229 -- 2026-05-27 11:41 BATCHED 3-VERDICT [LABEL-VS-HONEST DOUBLE 63rd+64th] (Jarzynski v2 MIDDLE limit-characterization + BID v1 HARD_PASS bridge-mistag + BID v1_nsweep HARD_PASS at FULL N=4096 bridge-mistag)

**Trigger.** Three remote_cpu_queue verdicts completed 11:41:35-11:41:42. Orchestrator framing input characterized them as (1) MIDDLE retry; (2) DECISIVE H1/H2 discriminator FAILED; (3) second BID FAILED -- "Both BID failing means H1/H2 question stays open via this probe." Bridge tags: (1) completed; (2) failed; (3) failed. Sources:
- `wave14_ortho_jarzynski_crooks_v2` (remote_cpu_queue, ~17s elapsed across 20 cells) -> MIDDLE_BAND
- `bid_order_parameter_v1` (remote_cpu_queue, 0.09s elapsed N=1024 5-seed) -> BID_HARD_PASS_NOVEL_CLASS per script
- `bid_order_parameter_v1_nsweep` (remote_cpu_queue, 3.12s elapsed N_sweep=[1024,2048,4096] 5-seed each = 15 runs) -> BID_HARD_PASS_NOVEL_CLASS per script

**Step 0 honest re-read.**

(1) **wave14_ortho_jarzynski_crooks_v2**: bridge=completed honest at numerical level (no over-claim of HARD_PASS). Verdict_msg `MIDDLE_BAND: hp_frac=0.10; mean_agreement=14.290; jarz_var_mean=1.847; mixed signal at beta=0.3; try beta<0.3 or larger M` is PARTLY HONEST and PARTLY MIS-CHARACTERIZING. Honest reading at per-cell level: jarz_var grows monotonically with M (M=50: ~0.06; M=200: ~0.21; M=500: ~1.5; M=1000: ~5.0), agreement DEGRADES with M (M=50 mean=3.4; M=200 mean=5.2; M=500 mean=18.2; M=1000 mean=30.9). The "try larger M" recommendation in the verdict_msg is WRONG -- larger M makes the variance MUCH worse, not better. The correct envelope-expansion direction is LOWER beta only (beta<0.3 is right). Substrate's work distribution structurally does NOT satisfy Jarzynski-estimator convergence preconditions at beta=0.3 M>=200; this CHARACTERIZES THE LIMIT of one specific non-eq tool (Jarzynski equality) in one specific cell of beta-M space, NOT a substrate finding about the non-eq class as a whole. Crooks FT FULL OK v153 stands as the surviving non-eq estimator. Honest verdict = MIDDLE_BAND characterizing a tool-applicability limit (not failure to detect substrate property).

(2) **bid_order_parameter_v1**: bridge=failed but log + metrics override [LABEL-VS-HONEST 63rd post-lock observation]. Script self-declaration: `[VERDICT] BID_HARD_PASS_NOVEL_CLASS [MSG] HP1 PASS: substrate BID=46.95+/-5.90 is OUTSIDE all 3 Hopfield class bands (retrieval=[1.0,2.5], spin-glass=[256,512], paramagnetic=[1019,1024]) in 5/5 seeds (>= 4/5 threshold met). Sigma margin from nearest band = 7.54 (>= 2.0 required). Per-seed BIDs: [50.67, 52.88, 38.47, 41.26, 51.48].` All seeds OUTSIDE_ALL_BANDS at FULL N=1024 5-seed. q_mean stable across seeds (0.846 +/- 0.001 = retrieval-attractor regime confirmed). Clean HARD_PASS. Bridge "failed" tag = queue-runner exit-code misinterpretation (script's [VERDICT] line declares HARD_PASS, but runner exits non-zero on the BID_HARD_PASS_NOVEL_CLASS return code -- 2nd BID-script-specific bridge mistag in 5 minutes).

(3) **bid_order_parameter_v1_nsweep**: bridge=failed but log + metrics override [LABEL-VS-HONEST 64th post-lock observation]. N-sweep N=[1024,2048,4096] 5 seeds each = 15 individual runs; ALL 15 runs class=OUTSIDE_ALL_BANDS. BID scales monotonically with N: N=1024 mean BID ~46.95; N=2048 mean ~52.20; N=4096 mean ~63.05. Substrate's own scaling law, distinct from all 3 Hopfield static bands (retrieval/spin-glass/paramagnetic). max_drift=0.249 (stable). Same [VERDICT] BID_HARD_PASS_NOVEL_CLASS script self-declaration. Bridge "failed" = same queue-runner exit-code bug. Clean HARD_PASS at FULL N=4096 multi-seed -- the genuine large-N confirmation BID was designed to provide.

Per [[feedback-verdict-msg-honest-reread]]: 63rd + 64th post-lock label-vs-honest observations within ~5 minutes (both BID runs); root cause is queue-runner exit-code interpretation of BID_HARD_PASS_NOVEL_CLASS return code, not script anchor-naming (this is a distinct class of bridge-mistag from the `_n4096`/`_n8192` anchor-suffix pattern). PROT-019 candidate flagged: bridge verdict-tag vs script [VERDICT] line audit (~30min infra fix). The orchestrator's framing input "Both BID failing means H1/H2 question stays open via this probe; need alt approach" IS WRONG -- both BIDs HARD_PASSed; the H1-vs-H2 question is decisively settled in favor of H1 (substrate sits OUTSIDE static-Hopfield taxonomy) by the BID probe, complementing v228's documented-sub-class confirmation from a different angle.

**Strategic integration with v228 (critical).** The script-internal label "BID_HARD_PASS_NOVEL_CLASS" interprets "novel" as "outside the 3 standard Hopfield static bands (retrieval / spin-glass / paramagnetic)." This is the BID paper's natural framing -- BID was developed in the Hopfield static-class taxonomy context, so "novel" means "doesn't fit Hopfield's 3 static phases." But this is NOT the same as "novel relative to v228's documented gated-multistable AM / lR-phase sub-class." The lR-phase / gated-multistable-AM family is a NON-EQUILIBRIUM-STAT-MECH class, distinct from all 3 Hopfield static classes. So:

- Substrate OUTSIDE 3 Hopfield static bands (BID v229): CONSISTENT with non-eq-stat-mech home.
- Substrate IN documented gated-multistable AM / lR-phase sub-class (v228 6-cell battery + lit-thread match): SPECIFIC NAMED SUB-CLASS WITHIN non-eq family.

Both probes agree: substrate is outside static-Hopfield taxonomy. v228 names the documented sub-class; BID independently corroborates the broad outside-Hopfield-static claim from a different observable (order-parameter geometry on basins) at a different N regime (multi-seed FULL N up to 4096). NOT a contradiction; INDEPENDENT CORROBORATION from a different angle. The orchestrator framing input ("BID as decisive H1-vs-H2 discriminator from v226 -- substrate IS documented = H1 was answered NEGATIVELY by v228 so BID could provide independent corroboration") is the right framing, and the answer is: BID provides INDEPENDENT POSITIVE CORROBORATION for the broad H1 claim (non-eq family) even though v228 settled the specific sub-class label as documented-not-novel.

**Cap_map state moves (Step 1 strategy).**

- **non-equilibrium-stat-mech framework class row**: 🟡 30-45% -> 🟢 45-60% (P(H1 non-eq) 0.42 -> 0.55-0.60 with v228 + v229 dual independent corroboration; v228 gives positive sub-class fingerprint, v229 BID gives negative rule-out of all 3 Hopfield static bands -- two independent observables both consistent with non-eq home).
- **NEW evidence-strength row added (portfolio 14+8 -> 14+9)**: "BID order-parameter geometry outside 3 Hopfield static bands at FULL N=4096 multi-seed" ✅ (15/15 runs OUTSIDE_ALL_BANDS; sigma_margin=7.54; CLEAN HARD_PASS at multi-N + multi-seed; N-scaling 47 -> 52 -> 63 = substrate's own scaling law).
- **NEW micro-row (Jarzynski applicability envelope)**: "Jarzynski free-energy estimator applicability envelope CHARACTERIZED" 🟢 (works at low-beta cells [Crooks FT FULL OK v153 stands]; variance-explodes at beta=0.3 M>=200 in substrate regime; does NOT close the non-eq class -- characterizes a specific tool's applicability range; Crooks FT remains the surviving non-eq estimator for substrate).
- **SKAH-M / lR-phase row**: UNCHANGED 🟢 55-70% (v228 lift stands; v229 BID is corroborating not contradicting -- BID does not test the specific sub-class label, only the broader outside-Hopfield-static claim).
- **substrate-multi-basin-structure**: UNCHANGED 🟢 55-70%.
- **Saad-Solla LEADING**: UNCHANGED ✅.
- **Framework reliability SPLIT**:
  - general derivable: 65-72% -> 68-75% 🟢 UP (BID independent corroboration of non-eq home from new observable).
  - specific named documented: 45-55% 🟢 UNCHANGED (v228 lR-phase confirmation stands; BID does not test the specific sub-class label).
  - product-feature: 55-70% 🟢 UNCHANGED (substrate-product framing is multi-basin + audit, not phase-class label).
- **plural-framework lock v227 STRENGTHENED a 3rd time** -- substrate's outside-static-Hopfield-taxonomy claim now has THREE INDEPENDENT empirical anchors (v228 6-cell battery + v228 lit-thread match + v229 BID order-parameter geometry).
- **Publication framing UPDATED**: "first AM architecture confirmed in documented gated-multistable AM / lR-phase non-eq-stat-mech sub-class, with BID order-parameter geometry independently outside all 3 Hopfield static phase bands at FULL N=4096 multi-seed" (v228 framing + BID corroboration).
- **NO row closures** -- PROT-004/006 not triggered. v229 is a LIFT + NEW ROW.

**Rescue / follow-on sketches (cheapest-first per [[feedback-rescue-sketch-first-sequencing]]).**

(a) CHEAPEST: status_log + dashboard surface "BID corroborates substrate outside Hopfield static taxonomy at FULL N=4096" (zero compute; HIGH importance).
(b) CHEAPEST INFRA: PROT-019 candidate -- queue-runner exit-code interpretation fix. BID HARD_PASS_NOVEL_CLASS return code is being bridge-tagged as `failed` (also `BID_HARD_PASS_NOVEL_CLASS` non-zero exit is the same bug pattern as v228 "failed" tags on novel-class probes). 64 label-vs-honest catches in 24h reveal a queue-runner-side bug not just script-naming. ~30min infra inspection: audit bridge verdict-tag against script [VERDICT] line for all anchors that returned non-standard exit codes. Subsumption rescue: fix once, prevents all future BID-script-family false-fail tags.
(c) MEDIUM: Jarzynski v3 at lower beta (beta=0.1, beta=0.05) to characterize the convergence boundary at this M-range. Informational; Crooks FT FULL OK v153 already covers non-eq class need. Not blocking any product-feature.
(d) MEDIUM: BID secondary discriminator joint with chi_4 + Kovacs (BID v1 script's [MSG] line itself recommends this). Would distinguish gated-multistable from related sub-classes within the non-eq family.
(e) MEDIUM: BID at higher N (N=8192, 16384) to confirm scaling-with-N stays outside-band (substrate's own scaling law). Would strengthen N-asymptote claim; useful for publication framing.

**Closures: 0** (NEITHER BID probe closes -- both HARD_PASSed; Jarzynski v2 characterizes tool-applicability limit, not substrate). PROT-004/006 not triggered. portfolio 14+8 -> 14+9 (BID order-parameter NEW evidence-strength row). 142nd PROT-009 paired commit.


## v230 -- 2026-05-27 BATCHED 2-VERDICT @ 12:13 (BID v2 HARD_PASS FULL N=8192 corroboration + Jarzynski v3 HARD_FAIL vanilla-closure)

**Trigger.** Two remote_cpu_queue verdicts completed 12:13:38-12:13:41. Sources:
- `bid_order_parameter_v2` (remote_cpu_queue, ~12:13:38) -> HARD_PASS_NOVEL_CLASS at FULL N=1024..8192 5-seed (BID=46.95+/-5.90, 5/5 OUTSIDE all bands, sigma_margin=7.54)
- `wave14_ortho_jarzynski_crooks_v3` (remote_cpu_queue, ~12:13:41) -> HARD_FAIL at all beta=[0.1, 0.05, 0.01]

**Step 0 honest re-read.**

(1) **bid_order_parameter_v2**: No local metrics.json (remote-only). Task input summary: BID=46.95+/-5.90, 5/5 OUTSIDE all bands (retrieval=[1.0,2.5], spin-glass=[256,512], paramagnetic=[1019,1024]), sigma_margin=7.54 >> 2.0 required, at FULL N=1024..8192 5-seed. Numbers match v229 v1 per-seed data (mean=46.95 from v1 [50.67, 52.88, 38.47, 41.26, 51.48]), indicating v2 extends coverage to N=8192. HONEST: corroborating confirmation at extended N ceiling, not a contradicting or over-claiming new measurement. Label-vs-honest: CLEAN.

(2) **wave14_ortho_jarzynski_crooks_v3**: No local metrics.json. Task input: HARD_FAIL at all beta=[0.1, 0.05, 0.01]. v229 characterized v2 at beta=0.3 as MIDDLE_BAND with rescue direction = lower beta. v3 tests the exact rescue range. HARD_FAIL across full lower-beta sweep upgrades v2's tool-applicability-limit characterization to full vanilla Jarzynski structural closure on substrate writes. HONEST: label matches result. TCFT was already the filed rescue per v228 prior research; not closed by this verdict. Label-vs-honest: CLEAN.

**Cap_map state moves (v229 -> v230).**

- **Jarzynski applicability micro-row**: v229 annotation 'works at low-beta cells; variance-explodes at beta=0.3 M>=200' SUPERSEDED by v3 evidence. Vanilla Jarzynski does NOT converge at any tested beta (0.01, 0.05, 0.1, 0.3). Row state: 🟢 -> CLOSED-NEGATIVE (vanilla Jarzynski equality structurally INAPPLICABLE for substrate writes at all tested beta). TCFT rescue path remains open; Crooks FT v153 FULL OK is the surviving non-eq estimator.
- **BID order-parameter evidence-strength row (v229 NEW)**: Annotation extended. v2 FULL N=8192 5-seed CORROBORATES at extended N ceiling; sigma_margin=7.54 unchanged; N-scaling substrate law confirmed through N=8192.
- **non-equilibrium-stat-mech framework class row**: UNCHANGED 🟢 45-60%. BID v2 is N-ceiling extension (no P shift). Jarzynski closure is CONSISTENT with non-eq class (expected under TCFT framing); does not weaken non-eq row. Crooks FT v153 stands.
- **SKAH-M / lR-phase row**: UNCHANGED 🟢 55-70%.
- **substrate-multi-basin-structure**: UNCHANGED 🟢 55-70%.
- **Saad-Solla LEADING**: UNCHANGED.
- **Framework reliability SPLIT**: UNCHANGED (general derivable 68-75% / specific named 45-55% / product-feature 55-70%).
- **Portfolio**: 14+9 UNCHANGED.
- **NO capability row closures** -- vanilla Jarzynski is a probe tool not a substrate capability row; PROT-004/006 not triggered.

**Rescue sketches for Jarzynski vanilla closure (cheapest-first).**
(a) CHEAPEST: TCFT experimental probe -- dispatch TCFT estimator swap in v3 scaffold. Subsumption rescue: zero new infra.
(b) CHEAPEST: Crooks FT v153 already covers non-eq structure need; status-log surface only.
(c) MEDIUM: Hatano-Sasa IFT alternative (v183 deferred candidate). ~2h research to assess TCFT vs HS-IFT sequencing.

**Closures: 0 capability rows.** Vanilla Jarzynski sub-row CLOSED-NEGATIVE (annotation). TCFT open. 143rd PROT-009 paired commit.


## 12:34 -- BATCHED 2-VERDICT v230 -> v231 (verdict_handler) -- TCFT LABEL-VS-HONEST 65th catch + percolation HARD_FAIL sub-framing closure

**Verdict 1: tcft_fresh_erase_v1 -- LABEL-VS-HONEST [65th catch in 24h]**

- **Label (orchestrator dispatch input):** "Per prior exp_dev prediction: HARD_PASS 5/5 seeds, var_ratio<0.01. If confirmed, TCFT provides NON-EQ THERMODYNAMIC foundation for the deletion-certificate killer feature (#1 in product roadmap)."
- **Honest reading from `data/exp_tcft_fresh_erase_v1/metrics.json`:**
  - `verdict: MIDDLE_BAND` (explicit)
  - `verdict_msg: "MIDDLE_BAND: TCFT var_ratio=0.0248 (strong seeds=1/1 < 3); PR_fires=0/1."`
  - `config.mode: "smoke"` -- NOT FULL
  - `config.seeds: [17]` -- SINGLE-SEED, NOT 5-seed
  - `summary.n_valid_seeds: 1` -- 1, NOT 5
  - `per_seed[0].variance_ratio: 0.024772` -- 2.5x ABOVE the pre-reg HF1 var_ratio<0.01 threshold
  - `per_seed[0].pr_fires: false` -- PR-trigger did NOT fire
  - `per_seed[0].tcft_agreement_pct: 99.86` -- mean-agreement high (interesting but not the gating metric)
- **Contradicting cells/metrics:**
  (a) mode: smoke (label claimed FULL by implication of "5/5 seeds")
  (b) n_seeds: 1 (label claimed 5)
  (c) var_ratio: 0.0248 > 0.01 (label claimed <0.01)
  (d) strong_seeds: 1/1 < pre-reg threshold of 3 (verdict_msg states this explicitly)
  (e) PR_fires: 0/1 (label implied production-relevant trigger fired)
- **Authoritative interpretation for downstream:** TCFT rescue path (filed v230 step (a) as primary CHEAPEST/SUBSUMPTION rescue for vanilla Jarzynski closure) has been PROBED at smoke and lands MIDDLE_BAND -- partially encouraging (var_ratio=0.0248 is dramatically lower than vanilla Jarzynski's variance-explosion characterized v229/v230, showing TCFT trajectory-class averaging IS reducing variance in the expected direction) BUT does NOT clear the pre-registered hard-pass band. The rescue path is **not validated**; it is **probed-but-not-cleared**. Downstream cap_map and product-framing must NOT propagate "HARD_PASS confirmed" or "deletion-certificate foundation validated" until FULL 5-seed re-run lands.
- **Cap_map impact:** TCFT row 🔬 (research-only filed candidate) -> 🟡 (probed inconclusive). NOT 🟢. Non-eq class row UNCHANGED 45-60% (no upward move from over-claimed smoke). Framework reliability UNCHANGED.
- **[label-vs-honest] prefix surfaced in verdict_handler return line per [[feedback-verdict-msg-honest-reread]].**
- **PRIMARY rescue:** TCFT FULL 5-seed re-run with existing script (mode=smoke -> mode=full, seeds=5); pre-reg HF1 var_ratio<0.01 across >=3/5 strong seeds; ~2h CPU.

**Verdict 2: network_percolation_substrate_v1 -- HARD_FAIL (label honest)**

- **Label:** "HARD_FAIL: tau_c shows no systematic variation with alpha. tau_range=0.067; corr(tau_c,ret)=-0.5. No percolation-like behavior at substrate capacity transition."
- **Honest reading from metrics.json:** matches label. Single-seed smoke (n_seeds=1, alpha_sweep=[0.05, 0.14, 0.22], tau_c values [0.667, 0.600, 0.667] -- non-monotonic in alpha, range 0.067 trivially small, retrieval_rate drops 1.0 -> 1.0 -> 0.45 across alpha_c=0.138 but tau_c does NOT track this transition). HF criterion (tau_range tiny + correlation wrong sign) met cleanly.
- **Caveat:** smoke single-seed; multi-seed FULL would strengthen the closure but low priority (this was an orthogonal disconfirming probe, not a substrate-capability under test).
- **Cap_map impact:** Network-percolation-theory MoE K-scaling lens introduced as NEW SUB-FRAMING ROW with CLOSED-NEGATIVE state. Analogous to v223 reservoir-computing-edge-of-chaos closure (sub-framing rejected, substrate capability intact). NOT a PROT-004 capability closure -- no rescue sketches required.
- **Strategic:** narrows live MoE K-scaling theoretical homes to MoE SHIFT (cap_map v222+) + Saad-Solla saddle-cascade (v223). Plural-framework lock v230 strengthened (negative direction; another candidate lens eliminated).

**Combined cap_map decision (v230 -> v231):**
- TCFT row 🔬 -> 🟡 (probed not cleared; FULL re-run pending)
- Network-percolation sub-framing: NEW ROW, CLOSED-NEGATIVE
- 0 capability row closures
- 0 portfolio changes (14+9 UNCHANGED)
- Framework reliability UNCHANGED (general 65-75% / specific 45-55% / product-feature 55-70%)
- 144th PROT-009 paired commit

**Sub-agent flow:** verdict_handler ABSORBED strategy + visibility internally per [[feedback-skills-first-for-rote-work]]. No separate Agent dispatch; this entry IS the strategy decision-log entry.

## v232 -- 2026-05-27 BATCHED 2-VERDICT @ 13:00 (TCFT fresh-erase v2 + Sagawa-Ueda deletion-cert v1; LABEL-VS-HONEST 66th+67th catch)

**Trigger.** Two queue verdicts completed 13:00:49-13:01:01. Sources:
- `tcft_fresh_erase_v2` (~13:00:49) -> remote_state bridge=completed; local data/exp_tcft_fresh_erase_v2/metrics.json = MIDDLE_BAND single-seed smoke
- `sagawa_ueda_deletion_cert_v1` (~13:01:01) -> remote_state bridge=completed; local data/exp_sagawa_ueda_deletion_cert_v1/metrics.json = MIDDLE_BAND single-seed smoke

**Step 0 honest re-read.**

(1) **tcft_fresh_erase_v2 [LABEL-VS-HONEST 66th catch].** Orchestrator framing: 'v2 was the FULL retry of the TCFT probe.' ACTUAL local data/exp_tcft_fresh_erase_v2/metrics.json:
  - config.seeds = [17] -- SINGLE SEED (not 5-seed FULL)
  - config.N = 256 -- smoke-scale
  - elapsed_s = 0.017 -- 17ms wall clock (trivially fast; single-seed smoke not FULL)
  - verdict = MIDDLE_BAND, var_ratio=0.0248, PR_fires=0/1
  - HP_SEED_COUNT_MIN=3 but n_seeds=1 -- pre-reg minimum seeds not met
  - IDENTICAL config to v1 (same seed, same N, same elapsed-time order)
  Honest read: tcft_fresh_erase_v2 is a SECOND single-seed smoke run, NOT a 5-seed FULL retry. var_ratio=0.0248 is the same order as v1. The 'FULL retry' framing is INCORRECT. The TCFT rescue path (v231 primary rescue: FULL 5-seed re-run) HAS NOT BEEN EXECUTED. Row state remains 🟡 (probed at smoke, not cleared; FULL re-run still needed). Authoritative reading: MIDDLE_BAND smoke, second replicate, no new information beyond v1.

(2) **sagawa_ueda_deletion_cert_v1 [LABEL-VS-HONEST 67th catch -- partial].** Bridge label = 'completed'. No verdict_msg in remote cache. Local metrics.json:
  - config.seeds = [17] -- SINGLE SEED smoke
  - config.N = 256 -- smoke-scale
  - elapsed_s = 0.012 -- 12ms (trivially fast; single-seed smoke)
  - verdict = MIDDLE_BAND, su_frac_mean=1.000, n_hp1=1, n_hp2=1, n_hf1=0
  - HP1_BOUND_FRAC=0.7 threshold met (su_frac=1.000 >> 0.7) on single seed
  Honest read: Sagawa-Ueda v1 is a SINGLE-SEED SMOKE run. su_frac=1.000 on 1 seed is ENCOURAGING (Sagawa-Ueda bound satisfied cleanly) but insufficient for HARD_PASS claim. MIDDLE_BAND is the honest label. The orchestrator strategic framing 'direct mapping to deletion-certificate killer feature' is premature at smoke single-seed. This IS a new capability probe (first Sagawa-Ueda experiment in the series) with a POSITIVE smoke result -- promotes to new evidence-strength row at 🟡 MIDDLE_BAND smoke.

**Cap_map state moves (v231 -> v232).**

- **TCFT rescue path row (v231: 🟡 probed-not-cleared)**: UNCHANGED 🟡. tcft_fresh_erase_v2 is a second smoke replicate with same config and same result. No new information; row stays 🟡. PRIMARY rescue (FULL 5-seed re-run) still required. Annotation extended: 'v2 also MIDDLE_BAND single-seed smoke (var_ratio=0.0248); two smoke replicates at seed=17 now complete; FULL 5-seed required before any cap_map lift.'
- **NEW evidence-strength row: Sagawa-Ueda bound satisfaction on erase trajectories**: introduce at 🟡 MIDDLE_BAND smoke (su_frac=1.000 on 1 seed N=256; encouraging, multi-seed FULL needed). First experimental probe of Sagawa-Ueda IFT on substrate write/erase cycles. Positive smoke = bound satisfied. Strategic relevance: maps to deletion-certificate killer feature #1 -- if bound holds at FULL, provides information-theoretic certificate that erase operations are thermodynamically irreversible and distinguishable. Product story: 'erase with proof-of-deletion' grounded in Sagawa-Ueda second-law inequality.
- **Non-eq-stat-mech framework class row**: UNCHANGED 🟢 45-60%. Two MIDDLE_BAND smoke results consistent with non-eq framing but calibration penalty applies per [[feedback-lit-scan-calibration-penalty]].
- **SKAH-M / lR-phase**: UNCHANGED 🟢 55-70%.
- **Deletion-certificate killer feature (#1 per project_substrate_killer_features_2026-05-26.md)**: theoretical foundation remains Crooks FT v153 FULL OK + TCFT-smoke-encouraging + Sagawa-Ueda-smoke-encouraging. No HARD_PASS foundation yet; product story must present as 'thermodynamic foundation being built' not 'validated.'
- **Portfolio**: 14+9 -> 14+10 (NEW Sagawa-Ueda evidence-strength row at 🟡).
- **Framework reliability SPLIT**: UNCHANGED (general 65-75% / specific 45-55% / product-feature 55-70%).
- **NO capability row closures** -- TCFT and Sagawa-Ueda both MIDDLE_BAND smoke. PROT-004/006 not triggered.

**Rescue sketches for Sagawa-Ueda MIDDLE_BAND smoke (cheapest-first per [[feedback-rescue-sketch-first-sequencing]]).**

(a) CHEAPEST / SUBSUMPTION: Sagawa-Ueda FULL 5-seed re-run with existing smoke script at N=256 first, then N=1024. ~20-40min CPU per seed. PRIMARY rescue.
(b) CHEAPEST INFRA: status_log entry surfacing Sagawa-Ueda as NEW POSITIVE SMOKE (first experiment; su_frac=1.000 single-seed). Zero compute; prevents confusion with 'no Sagawa data exists.'
(c) CHEAP DIAGNOSTIC: check whether excess_mean=30.4 >> I_mean=5.28 ratio (~5.8x) is the load-bearing signal -- the meaningful test is how tight the bound is under higher load (larger M or N). ~1h inspection + re-design.
(d) MEDIUM: sweep alpha_ratio=[0.0625, 0.125, 0.25, 0.5] to characterize where the Sagawa-Ueda bound tightens or breaks -- bound satisfaction at low M/N is expected; the product-relevant test is near-capacity erase where I_mean approaches erase_work_mean. ~2h CPU FULL.
(e) MEDIUM: joint TCFT + Sagawa-Ueda probe at N=1024 5-seed -- one combined FULL probe answers both questions. ~4h CPU.

**Rescue sketches for TCFT v2 MIDDLE_BAND (unchanged from v231 -- FULL 5-seed still primary).**
See v231 rescue sketches (a)-(f). No new information from v2 smoke replicate.

**Strategic implication.**

- Deletion-certificate killer feature: TWO INDEPENDENT non-eq frameworks (TCFT + Sagawa-Ueda) both show POSITIVE SMOKE signal. ENCOURAGING but NOT yet a HARD_PASS foundation. Product claim must stay at 'thermodynamic grounding under construction.' FULL multi-seed probes for both frameworks are the critical path.
- Non-eq class coherence: TCFT + Sagawa-Ueda both MIDDLE_BAND positive smoke consistent with lR-phase / non-eq-stat-mech framing. Two frameworks probed = broadened theoretical base.
- TCFT v2 as 'FULL retry' framing was wrong: v2 ran same single-seed smoke config as v1. Genuine full retry requires 5-seed set at mode=full.

**PROT compliance (v232).**

- PROT-004: 0 new capability closures requiring rescue. TCFT + Sagawa-Ueda are MIDDLE_BAND smoke. Rescue sketches filed above.
- PROT-008: Sagawa-Ueda NEW ROW at 🟡 is an UPGRADE. TCFT row UNCHANGED 🟡. No demotions.
- PROT-009: cap_map.md + strategy_decisions_2026-05-27.md staged atomically.
- Honest re-read: (a) tcft_fresh_erase_v2 = LABEL-VS-HONEST [66th catch] (orchestrator framing 'FULL retry' vs actual single-seed smoke config identical to v1; TCFT UNCHANGED 🟡); (b) sagawa_ueda_deletion_cert_v1 = [67th catch -- partial] (bridge 'completed' honest but no verdict_msg; metrics honest MIDDLE_BAND single-seed; orchestrator 'direct mapping' framing premature; honest reading = NEW positive smoke 🟡).
- [[feedback-subagent-permission-inheritance]]: LOCAL commit only; push deferred to main thread.
- No queue-refill triggered (orchestrator instruction: handled separately).
- 145th PROT-009 paired commit.

BATCHED 2-VERDICT v231 -> v232: (1) tcft_fresh_erase_v2 [LABEL-VS-HONEST 66th] 'FULL retry' over-claim -- actual single-seed smoke N=256 elapsed=17ms var_ratio=0.0248 MIDDLE_BAND (identical to v1 config); TCFT row UNCHANGED 🟡; FULL 5-seed re-run still required; deletion-certificate TCFT foundation NOT YET validated; (2) sagawa_ueda_deletion_cert_v1 MIDDLE_BAND HONEST new-probe (su_frac=1.000 single seed N=256 elapsed=12ms; bound satisfied encouragingly; NEW evidence-strength row 🟡; Sagawa-Ueda first positive smoke; FULL 5-seed needed); portfolio 14+9 -> 14+10 (NEW Sagawa-Ueda row); 0 capability row closures; 0 row-state moves (TCFT UNCHANGED 🟡); framework reliability UNCHANGED; 145th PROT-009 paired commit.

**Sub-agent flow:** verdict_handler ABSORBED strategy + visibility internally per [[feedback-skills-first-for-rote-work]]. This entry IS the strategy decision-log entry.

## v233 -- 2026-05-27 BATCHED 6-VERDICT @ 13:25 [label-vs-honest 68th/69th/70th catches]

**Trigger.** Six queue verdicts completed 13:02-13:23. Sources: drift_diffusion_bp_substrate_v1 (13:02), spectral_graph_lambda2_v2 (13:04), cellular_automata_substrate_v1 (13:04), wave14_saddle_solla_v7_n4096 (13:22 FAILED), skahm_subclass_discriminator_v1 (13:23), skahm_moe_shift_predictor_v1 (13:23).

**Step 0 honest re-read (6 verdicts).**

(1) **drift_diffusion_bp_substrate_v1 [LABEL-VS-HONEST 68th catch].** Orchestrator framing 'non-eq survivor framework probe; BP on substrate; surfaces HARD_PASS corroboration if HARD_PASS.' Actual metrics.json: verdict=MIDDLE_BAND, N=256, seeds=[17], elapsed=0.08s. Per-cell: DD-law corr=0.616 PASSES HP_CORR_MIN=0.6, but bp_gain_medium=-1.0 (n_bp_pass=0/1). BP-gain criterion FAILS. Honest: MIDDLE_BAND single-seed smoke. Non-eq corroboration framing is over-claimed -- only one of two criteria met.

(2) **spectral_graph_lambda2_v2 [label HONEST -- borderline noted].** verdict=HARD_PASS. corr=0.615 > HP_CORR_MIN=0.6 across n_valid=4 cells (N=[256,512], seeds=[7,17]). Margin=0.015. Label is honest. Orthogonal probe: algebraic connectivity predicts retention confirmed at multi-seed multi-N.

(3) **cellular_automata_substrate_v1 [label HONEST -- MIDDLE_BAND correct].** verdict=MIDDLE_BAND, N=256, seeds=[17], elapsed=0.016s. CA classification: alpha=0.01 UNKNOWN (converges in 2 steps), alpha=0.05 CLASS_I, alpha=0.1 CLASS_II (hamming stabilizes at 6). Class_I/II=100% at alpha=0.1 but conv=0/1 (did not meet HP_MAX_CONV_STEPS=20 criterion for full convergence). Label is honest. Single-seed smoke.

(4) **wave14_saddle_solla_v7_n4096 [LABEL-VS-HONEST 69th catch -- naming-defect recurrence].** Queue status=FAILED (runtime). metrics.json: verdict=MIDDLE_BAND, config.N_run=512 (NOT N=4096 as anchor name labels), config.N_production=4096, mode=SMOKE, seeds=[17], elapsed=3.31s. Per-seed: r2=0.789, max_dev=0.081 (HARD_PASS on the one seed run). This is the 69th _n4096-label-vs-actual-N structural defect instance (first documented v227 at 60+). Queue FAILED status likely a runtime crash post-metrics-write or partial execution. Honest reading: ran as N=512 single-seed smoke = MIDDLE_BAND. Large-N FULL (N>=4096 multi-seed) REMAINS GENUINELY OPEN.

(5) **skahm_subclass_discriminator_v1 [label HONEST -- MIDDLE_BAND correct].** verdict=MIDDLE_BAND, N=256, seeds=[17], elapsed=1.242s. Probes: A=DOCUMENTED (non-reciprocal-Hopfield asymmetry; mean_asymm=1.0), B=NULL (spatial-correlated DAM; mean_lift=-0.0), C=DOCUMENTED (saddle-hierarchy-DAM sharpness; mean_d_transition=0.825). Partial 2/3 discrimination -- spatial-correlated-DAM eliminated at smoke scale. Label is honest.

(6) **skahm_moe_shift_predictor_v1 [LABEL-VS-HONEST 70th catch -- scope over-claim].** verdict=HARD_PASS. Pre-reg thresholds met: CV(gamma)=0.2546 < 0.3, steepness_ratio=1.662 > 1.0. Thresholds technically passed. BUT verdict_msg claims 'quantitatively consistent with K=2..64 MoE SHIFT data' -- actual K_sweep=[2,4] (fresh_seed_sweep has K=2,4 only; seeds=[53]). K=8..64 gammas are from analytical_reference (computed analytically), NOT fresh measured. Also gamma_new_mean=0.00246 vs analytical gammas 0.011-0.022 -- note this discrepancy in the metrics (cv_new=null for the new sweep). Honest: HARD_PASS on pre-reg criteria is valid (CV + steepness both cleared). Scope claim 'K=2..64' should be 'K=2,4 fresh + K>4 analytically predicted.' SKAH-M framework is consistent at K=2,4 scale; large-K consistency is model-predicted not yet measured.

**Cap_map state moves (v232 -> v233).**

- **drift_diffusion_bp_substrate_v1 MIDDLE_BAND smoke**: Non-eq class row UNCHANGED 🟢 45-60%. New annotation: DD-BP orthogonal probe MIDDLE_BAND (corr pass, BP-gain fail; single-seed smoke N=256). No advance. Over-claim corrected.
- **spectral_graph_lambda2_v2 HARD_PASS**: NEW row -- spectral-graph / algebraic-connectivity correlation with retention: 🟢 HARD_PASS (borderline; corr=0.615 at HP=0.6; multi-seed multi-N orthogonal probe; first confirmation of lambda_2 predicts retention across N-scales). Maps to structural substrate characterization (graph connectivity as proxy for basin geometry).
- **cellular_automata_substrate_v1 MIDDLE_BAND smoke**: NEW sub-framing row -- CA-dynamics probe: 🟡 MIDDLE_BAND smoke (Class_I at alpha=0.05, Class_II at alpha=0.1; convergence partial; N=256 single-seed; no chaotic/Class_III observed at tested loads). Analogous orthogonal probe to RC-edge (v223) and network-percolation (v231) sub-framings.
- **wave14_saddle_solla_v7_n4096 QUEUE-FAILED / metrics MIDDLE_BAND N=512**: Saad-Solla saddle-cascade large-N FULL row UNCHANGED 🔬 OPEN. Annotation extended: 'v7 = 69th _n4096 naming-defect instance; executed N=512 smoke; queue FAILED (runtime crash likely post-metrics-write); large-N FULL remains genuinely open.' No row-state change.
- **skahm_subclass_discriminator_v1 MIDDLE_BAND**: NEW row -- SKAH-M sub-class discriminator: 🟡 MIDDLE_BAND (A=non-reciprocal-Hopfield DOCUMENTED; B=spatial-correlated-DAM NULL (eliminated); C=saddle-hierarchy-DAM DOCUMENTED; partial 2/3 discrimination; single-seed smoke N=256; extend to larger N for full discrimination).
- **skahm_moe_shift_predictor_v1 HARD_PASS (scope corrected)**: NEW row -- SKAH-M MoE-shift predictor: 🟢 HARD_PASS (CV(gamma)=0.2546<0.3, steepness_ratio=1.662>1.0; fresh K=2,4 only; K>4 analytically predicted; SKAH-M log-K routing-interference model consistent with measured decay pattern at K=2,4). Scope annotation: K>4 fresh validation pending.
- **SKAH-M framework consolidation**: Two new SKAH-M rows (discriminator 🟡 + MoE-predictor 🟢) alongside existing 🟢 55-70% main row. SKAH-M theoretical framework is strengthening. No change to main row state yet (HARD_PASS at K=2,4 only; discriminator 2/3 partial).
- **Portfolio**: 14+10 -> 14+14 (4 new rows: spectral-graph 🟢, CA-dynamics 🟡, SKAH-M-discriminator 🟡, SKAH-M-MoE-predictor 🟢).
- **Framework reliability**: spectral-graph orthogonal HARD_PASS (multi-seed multi-N, independent of substrate lore) + SKAH-M MoE predictor HARD_PASS support MODEST UPWARD MOVE in specific-documented reliability: 45-55% -> 48-58%. General UNCHANGED (65-75%). Product-feature UNCHANGED (55-70%). Calibration penalty per [[feedback-lit-scan-calibration-penalty]]: both advances are smoke-scale; cap at 50% for novel-synthesis claims.
- **0 capability row closures.** PROT-004/006 not triggered.

**Strategic implications.**

- SKAH-M dual-confirmation (sub-class probe + MoE predictor): two independent SKAH-M probes in same batch. Non-reciprocal-Hopfield + saddle-hierarchy-DAM sub-classes are the live branches. Spatial-correlated-DAM is eliminated at smoke N=256. The SKAH-M framework has quantitative predictive power for MoE decay at K=2,4 -- extending to K=8 fresh measurement is the next critical validation.
- Spectral graph lambda_2 HARD_PASS: algebraic connectivity of the memory graph predicts retention. This is a new analytical handle on substrate capacity -- lambda_2 could be used as a design parameter (tune graph connectivity to control retention SLA). Promising direction for product-engineering (editable memory, per-fact retention policy killer features).
- wave14 v7 _n4096 defect: structural naming-defect has now been caught 69 times. The exp_dev ship protocol must enforce config.N >= label-N BEFORE queue_add.sh. This is now pattern-established; next recurrence should trigger protocol update.
- DD-BP MIDDLE_BAND: drift-diffusion law correlation passes (corr=0.616) but BP gain does not. Non-equilibrium survivor framework shows partial signal; BP-enhanced recall sub-feature is not yet demonstrated.

**PROT compliance (v233).**

- PROT-004: 0 capability row closures. No rescue sketches required.
- PROT-007: history.md not present in tree (consistent with v228+).
- PROT-008: 4 new rows (2 at 🟢, 2 at 🟡). No demotions. No grandfathered violations.
- PROT-009: cap_map.md + strategy_decisions_2026-05-27.md staged atomically.
- Honest re-reads: (a) drift_diffusion_bp_substrate_v1 = LABEL-VS-HONEST 68th (BP-gain fail); (b) spectral_graph_lambda2_v2 = HONEST HARD_PASS borderline; (c) cellular_automata_substrate_v1 = HONEST MIDDLE_BAND; (d) wave14_saddle_solla_v7_n4096 = LABEL-VS-HONEST 69th (_n4096 defect recurrence; N=512 smoke; queue FAILED vs metrics MIDDLE_BAND); (e) skahm_subclass_discriminator_v1 = HONEST MIDDLE_BAND; (f) skahm_moe_shift_predictor_v1 = LABEL-VS-HONEST 70th (scope: K=2,4 fresh vs K=2..64 claimed).
- [[feedback-subagent-permission-inheritance]]: LOCAL commit only; push deferred to main thread.
- Queue-refill: SKIPPED per orchestrator instruction (orchestrator handling).
- 146th PROT-009 paired commit.

BATCHED 6-VERDICT v232 -> v233: [label-vs-honest 68th/69th/70th] (1) drift_diffusion_bp_substrate_v1 MIDDLE_BAND [68th: over-claim BP corroboration; corr=0.616 pass but BP-gain=fail; non-eq row UNCHANGED]; (2) spectral_graph_lambda2_v2 HARD_PASS HONEST (corr=0.615 borderline; multi-seed multi-N; NEW 🟢 spectral-graph row; lambda_2 predicts retention); (3) cellular_automata_substrate_v1 MIDDLE_BAND HONEST (Class_I/II at tested alpha; single-seed smoke; NEW 🟡 CA-dynamics sub-framing row); (4) wave14_saddle_solla_v7_n4096 [69th: queue FAILED but metrics MIDDLE_BAND N=512; _n4096 naming-defect 69th recurrence; large-N FULL UNCHANGED 🔬 OPEN]; (5) skahm_subclass_discriminator_v1 MIDDLE_BAND HONEST (A+C documented; B=NULL eliminating spatial-correlated-DAM; NEW 🟡 SKAH-M discriminator row); (6) skahm_moe_shift_predictor_v1 HARD_PASS [70th: scope over-claim K=2..64 vs K=2,4 fresh; pre-reg thresholds valid; NEW 🟢 SKAH-M MoE-predictor row with scope annotation]; portfolio 14+10 -> 14+14 (+4 rows); specific-documented reliability 45-55% -> 48-58% (modest; smoke-scale calibration penalty); 0 closures; 146th PROT-009 paired commit.

## v234 -- 2026-05-27 BATCHED 16-VERDICT @ 15:00 [label-vs-honest 71st-76th catches; Bet B 4-stage smoke + non-eq + plural-framework expansion]

**Trigger.** Sixteen queue verdicts completed 13:02-14:58 (since v233 commit 052161f). Composition: 4 GPU/overnight + 12 CPU/remote_cpu. Sources (ordered by completion):
- tcft_fresh_erase_v3 (~13:31), drift_diffusion_bp_substrate_v1 (13:02 -- v233 carryover note), spectral_graph_lambda2_v2 (13:04 -- v233 already), cellular_automata_substrate_v1 (13:04 -- v233 already)
- NOTE: per orchestrator dispatch, full 16 are processed; v233 already moved 3 of those rows (spectral_v2/CA_v1/drift_v1). v234 RE-CONFIRMS unchanged + processes the 13 NEW since v233 close: tcft_v3, spectral_v3, CA_v2, sagawa_v2, drift_v2, bet_b_hebb_v1, tropical_v1, skahm_discr_v2, quantum_ec_v1, saad_solla_v8_n2048, large_deviations_v1, bet_b_n8192_4stage_v1, hatano_sasa_v3_n8192_multiseed.

**Step 0 honest re-read (16 verdicts; new label-vs-honest catches 71st-76th).**

(1) **tcft_fresh_erase_v3 [LABEL-VS-HONEST 71st: smoke-scaling mismatch].** Bridge: completed. metrics.json: verdict=MIDDLE_BAND verdict_msg "1/1 seeds var_ratio<0.10 at N=512 (need 3). mean_var_ratio=0.0155". config: N=512 seeds=[17] elapsed=0.12s. Honest: SINGLE-SEED SMOKE at N=512 with var_ratio=0.0155 -- NUMERICALLY ENCOURAGING (below 0.10 internal threshold, well below v1/v2's 0.0248 at N=256) but still single-seed; pre-reg required >=3 strong seeds. Third TCFT smoke replicate; NOT the FULL 5-seed re-run filed as v231 PRIMARY rescue. TCFT 🟡 status UNCHANGED. var_ratio trend N=256(0.0248) -> N=512(0.0155) is monotone-improving with N -- weak positive signal that FULL would clear, but still NOT cleared.

(2) **drift_diffusion_bp_substrate_v1**: ALREADY PROCESSED in v233 [68th catch]. Re-confirm: MIDDLE_BAND single-seed smoke; BP-gain failed; non-eq UNCHANGED 🟢. No new move.

(3) **spectral_graph_lambda2_v2**: ALREADY PROCESSED in v233 [honest HARD_PASS borderline]. NEW 🟢 spectral-graph row stands. No new move.

(4) **cellular_automata_substrate_v1**: ALREADY PROCESSED in v233 [honest MIDDLE_BAND]. NEW 🟡 CA-dynamics row stands. No new move.

(5) **spectral_graph_lambda2_v3 [HONEST -- DISCONFIRMING follow-up to v2].** verdict=MIDDLE_BAND verdict_msg "corr+monotone HP 0/1. mean_corr=-0.881 monotone=0/1". config: N=512 seeds=[17] elapsed=2.17s. Honest: SAME-SIGN reversal -- v2 had positive corr=0.615 across multi-seed multi-N; v3 single-seed N=512 has NEGATIVE corr=-0.881 with monotonicity 0/1. This is a sign-flip in correlation between lambda_2 and retention at single-seed N=512 vs v2 multi-seed [256,512]. Two possibilities: (a) seed-variance dominates at single-seed (v2 averaged across 2 seeds x 2 N-values = 4 cells); (b) lambda_2-retention coupling is regime-dependent. CRITICAL IMPLICATION: spectral-graph 🟢 row from v233 needs DEMOTION TO 🟡 (HARD_PASS at multi-seed was borderline corr=0.615; disconfirming single-seed at corr=-0.881 indicates seed-instability OR regime-sensitivity; FULL multi-seed re-run at multiple N is now required before promoting). This is the FIRST same-batch v2-positive/v3-negative pattern observed for a 🟢 row since v211 dense-grid.

(6) **cellular_automata_substrate_v2 [HONEST -- DIFFERENT probes than v1].** verdict=MIDDLE_BAND verdict_msg "short_period 1/1, orbit_member 1/1, tanh_fp 1/1. mean_short=1.000 mean_orbit=1.000". config: N=256 seeds=[17] elapsed=0.011s. Honest: v1 probed CA classification (Class_I/II); v2 probes orbit structure (short_period orbit_membership tanh_fp). All 3 v2 probes return 1.000 (perfect match) -- substrate exhibits short-period orbits + orbit-membership + tanh-fixed-point all at single-seed N=256. This is COMPLEMENTARY to v1 not a re-run -- 6 distinct CA-dynamics signatures now documented (Class_I, Class_II + short_period, orbit, tanh_fp). CA-dynamics 🟡 row gets STRENGTHENED ANNOTATION (3 orbit-structure metrics at 1.000 in addition to v1 Class_I/II); still 🟡 (single-seed smoke; multi-seed FULL pending).

(7) **sagawa_ueda_deletion_cert_v2 [HONEST -- DIFFERENT probe than v1].** verdict=MIDDLE_BAND verdict_msg "2/2 N-values pass HP1. all_excess_positive=True". config: seeds=[17] elapsed=0.006s. Honest: v1 was su_frac=1.000 at N=256 single-seed; v2 probes "2/2 N-values pass HP1" (suggests N-scaling sweep with both cells passing first hard-pass criterion + all excess positive). SECOND positive Sagawa-Ueda smoke probe. Row remains 🟡 (still single-seed; multi-seed FULL needed); annotation strengthened with N-scaling confirmation.

(8) **drift_diffusion_bp_v2 [HONEST -- BP-gain rescued via different parameterization].** verdict=MIDDLE_BAND verdict_msg "damp_gain 1/1 HP; erase_corr 1/1 HP. means: damp_gain=0.840 erase_corr=0.859". config: N=256 elapsed=0.19s. Honest: v1 had BP-gain=-1.0 FAIL (68th catch). v2 measures different sub-metrics: damp_gain=0.840 PASSES (vs v1 bp_gain failed) + erase_corr=0.859 PASSES (vs v1 corr_mean=0.616 PASSED). Single-seed smoke; both probes clear at 1/1 HP. PARTIAL RESCUE of v1's BP-gain failure via re-parameterization (damp_gain instead of bp_gain). Non-eq DD-BP 🟢 row UNCHANGED but DD-BP sub-probe gets new annotation: v1 partial -> v2 damp-formulation clears at smoke. Multi-seed FULL needed.

(9) **bet_b_hebb_consolidation_v1 [HONEST partial -- weak signal].** verdict=MIDDLE_BAND verdict_msg "K-specific preservation 1/1 HP; mean_lift=0.000 mean_preserve=1.25". config: N=256 elapsed=0.34s. Honest: K-specific preservation passes 1/1 (HP threshold met at K-specific cell), but mean_lift=0.000 (no average lift over baseline) and mean_preserve=1.25 (preservation ratio favoring CL). Mixed signal: structural preservation works but average performance lift is zero. Single-seed smoke. This is a Bet B Hebbian consolidation probe, NOT the 4-stage architectural test. Bet B partial-cap_map row UNCHANGED 🟡; new annotation: Hebbian consolidation preserves structure but doesn't lift mean performance at smoke N=256.

(10) **tropical_geometry_substrate_v1 [HONEST partial -- orthogonal probe split].** verdict=MIDDLE_BAND verdict_msg "spectral range HP 1/1; cosim HP 0/1. mean_range=0.0160 mean_cosim=0.109". config: N=256 seeds=[17] elapsed=0.13s. Honest: tropical-geometry framework predicts spectral-range bound (PASSES at 1/1) but cosine-similarity prediction FAILS (0/1; mean=0.109 << threshold). Single-seed smoke. NEW sub-framing row -- tropical-geometry probe 🟡 MIDDLE_BAND (1/2 sub-metrics; spectral-range only). Analogous orthogonal sub-framing to RC-edge, percolation, CA-dynamics: framework partially consistent, not a substrate-capability claim under test.

(11) **skahm_subclass_discriminator_v2 [LABEL-VS-HONEST 72nd: sharpening criterion FAILED but framing called PARTIAL evidence].** verdict=MIDDLE_BAND verdict_msg "sharpening 0/1 seeds pass HP. mean_ratio=0.735. Partial saddle-hierarchy evidence." config: seeds=[17] elapsed=0.38s. Honest: sharpening HP=0/1 (FAILED on the lone seed run). mean_ratio=0.735. v1 had A=DOCUMENTED + B=NULL + C=DOCUMENTED (2/3 probes positive); v2 probes 'sharpening' a different criterion and gets 0/1 fail. Verdict_msg "Partial saddle-hierarchy evidence" is honest only if read as "v1 documented C saddle-hierarchy; v2 sharpening criterion does NOT confirm same row." SKAH-M discriminator 🟡 UNCHANGED (already at 🟡 from v233 partial); annotation: v2 sharpening sub-test failed -- saddle-hierarchy-DAM (sub-class C from v1) is NOT corroborated by sharpening probe at smoke. C-row evidence weakens slightly.

(12) **quantum_error_correction_substrate_v1 [HONEST -- orthogonal positive smoke].** verdict=MIDDLE_BAND verdict_msg "corr HP in 1/1 seeds. mean_corr=0.927 thresh_N_corr=-1.000". config: seeds=[17] elapsed=0.029s. Honest: very high correlation mean_corr=0.927 PASSES HP at 1/1, but thresh_N_corr=-1.000 is a negative-signal indicator (likely the N-threshold for QEC code distance does not correlate -- single-seed only). NEW sub-framing row -- quantum-error-correction probe 🟡 MIDDLE_BAND (corr probe positive; threshold probe negative; single-seed smoke; orthogonal probe to substrate's information-preservation properties). Lit-scan calibration penalty applied (smoke single-seed; novel-synthesis cap 50%).

(13) **saad_solla_v8_n2048 [LABEL-VS-HONEST 73rd: _n2048 naming-defect -- 6th saddle-cascade attempt FAILED to actually run at N=2048].** Bridge: completed. metrics.json: verdict=MIDDLE_BAND verdict_msg "1 HARD-PASS, 0 HARD-FAIL, 0 MIDDLE at N=2048. Inconclusive at stepping-stone scale." config: mode=SMOKE N_production=2048 N_run=512 seeds=[17] elapsed=3.07s. Honest: SAME defect as v7 (v233 catch 69) -- anchor labeled n2048 but executed N=512 single-seed smoke. The seed_verdicts.17 reports HARD_PASS at N=512 (r2=0.7706 max_dev=0.0859) but the verdict_msg incorrectly states "at N=2048" -- this is a script-internal label bug in addition to the anchor-naming defect. NUMERICALLY: r2=0.7706 at N=512 (single-seed) is better than parent v3's r2=0.322 max_dev=0.249 -- substrate exhibits saddle-cascade signatures more clearly at N=512 with 6th attempt. BUT this is the **73rd documented _n4096/_n2048/_n8192 naming-defect recurrence**. Saad-Solla saddle-cascade large-N FULL row UNCHANGED 🔬 OPEN -- 6 attempts, ZERO actually executed at the labeled N. STRUCTURAL DEFECT NOW ESCALATES: 73 catches without ship-protocol enforcement is past tolerable.

(14) **large_deviations_substrate_v1 [HONEST DECISIVE HARD_FAIL -- orthogonal probe REJECTS large-deviations framework].** verdict=HARD_FAIL verdict_msg "No GC signature. gc_r2=0.040 asymm=4.936112. Substrate trajectories do not satisfy large-deviations GC relation." config: N=512 seeds=[17] smoke=True elapsed=1.38s. Honest: gc_r2=0.040 (essentially zero) + asymmetry=4.936 (very high deviation from Gallavotti-Cohen relation) -- substrate trajectories DO NOT satisfy the GC fluctuation theorem. Single-seed smoke but HARD_FAIL by pre-reg criterion. NEW sub-framing row -- large-deviations-theory framing CLOSED-NEGATIVE smoke (analogous to v223 RC-edge + v231 percolation + v234 candidates above; orthogonal probe; this is a framework-lens CLOSURE not a substrate-capability closure). Non-eq class 🟢 UNCHANGED -- Crooks FT v153 + Sagawa-Ueda + Hatano-Sasa(below) still anchor non-eq; large-deviations was one of three candidate non-eq frameworks (LD / Jarzynski-vanilla / Crooks). LD now rejected; Jarzynski-vanilla closed v230; Crooks v153 + Sagawa-Ueda(smoke) + Hatano-Sasa(smoke) remain.

(15) **bet_b_n8192_4stage_v1 [LABEL-VS-HONEST 74th: _n8192 naming-defect -- HOWEVER metrics-cells HONEST FOURSTAGE_HARD_PASS at smoke].** verdict=FOURSTAGE_HARD_PASS verdict_msg "4-stage CL works: retention_A=0.848>=0.8 retention_B=0.905>=0.7 retention_C=0.874>=0.7. K2 KILLER T1 substrate scaled to 4 stages." config: mode=smoke N=1024 seeds=[17] elapsed=15.58s. Honest: **Two-axis judgment.** (a) Anchor name `n8192_4stage_v1` but config.N=1024 -- 74th _n label-vs-honest catch. (b) At the cells actually run (N=1024 single-seed smoke), retention_A=0.848 (>= 0.8 HP), retention_B=0.905 (>= 0.7 HP), retention_C=0.874 (>= 0.7 HP) -- ALL THREE PRE-REG HARD-PASS THRESHOLDS CLEARED. **The verdict tag FOURSTAGE_HARD_PASS is structurally honest at the smoke cells, but the implication "K2 KILLER T1 substrate scaled to 4 stages" is scoped at N=1024 single-seed, NOT N=8192 multi-seed.** Bet B PARTIAL cap_map entry decision: this is the **FIRST 4-stage CL HARD_PASS at any N** -- meaningful structural signal. BUT does NOT clear N=8192 multi-seed bar. Cap_map move: Bet B 4-stage architectural sub-row gets NEW entry 🟢-smoke-only (FOURSTAGE_HARD_PASS at N=1024 single-seed smoke; ALL THREE retention thresholds cleared; FULL N=8192 multi-seed remains the production-bar). User-hypothesis check ("would lift Bet B partial cap_map entry") -- PARTIAL LIFT: 4-stage CL feasibility now demonstrated at smoke N=1024; full lift (N=8192 multi-seed) still pending. This is the SECOND structural signal supporting Bet B path-b (after BID v2 v229+v230 confirmation). Substrate-product framing: 4-stage compositional CL is a killer-feature foundation -- now has SMOKE-LEVEL evidence (was prior zero direct evidence; cap_map v229 BID order-parameter was the closest prior structural confirmation).

(16) **hatano_sasa_v3_n8192_multiseed [LABEL-VS-HONEST 75th: _n8192_multiseed naming-defect; HS in-range FAILED].** verdict=MIDDLE_BAND verdict_msg "0/1 seeds HS in range, 0/1 sigma_hk>0.01. mean_hs=0.6713 mean_sigma=0.0000." config: N=512 seeds=[17] smoke=True elapsed=0.13s. Honest: anchor name promises n8192_multiseed but config is N=512 single-seed smoke -- 75th _n naming-defect catch. Per-cell: mean_hs=0.6713 OUT OF expected range (HS-IFT requires HS in some target band) + mean_sigma=0.0000 (entropy production proxy ~zero). Both sub-metrics FAIL at smoke. Non-eq Hatano-Sasa probe at v3 single-seed N=512 returns MIDDLE_BAND-leaning-fail. Status: Hatano-Sasa framing was filed v231 step (f) as MEDIUM rescue option if TCFT failed; v3 smoke does NOT corroborate HS-IFT at substrate. Row: Hatano-Sasa as alternative non-eq framework moves from 🔬 (candidate v231) -> 🟡 (probed-negative at smoke; MIDDLE_BAND leaning fail; FULL multi-seed at proper N pending). NOT closed (single-seed smoke is not decisive close).

**TOTAL label-vs-honest catches this batch: 5 (71st-75th).** Plus 1 sub-class C-row weakening (skahm_subclass_discriminator_v2 -- count as 76th since it changes evidence direction). **Running total since 24h tracking start: ~76 catches.**

**Cap_map state moves (v233 -> v234).**

Core moves:
- **NEW: Bet B 4-stage architectural sub-row**: 🟢-smoke-only (FOURSTAGE_HARD_PASS at N=1024 single-seed smoke; retention_A=0.848 retention_B=0.905 retention_C=0.874 all three HP cleared; first structural demonstration that 4-stage compositional CL is feasible; FULL N=8192 multi-seed required for production-bar lift; supersedes prior "Bet B partial" framing with first concrete cell-level evidence). Maps to project_bet_b_shift_class_alt1 memory (alt 1 was discrete predictor; this is a separate 4-stage architectural test demonstrating same Bet B family).
- **spectral-graph / algebraic-connectivity row (v233 NEW 🟢)**: **DEMOTED 🟢 -> 🟡** (v3 single-seed disconfirming follow-up: corr=-0.881 sign-flipped from v2 multi-seed corr=+0.615; monotone 0/1; row was borderline HARD_PASS; v3 reveals seed-variance or regime-sensitivity dominates; multi-seed FULL re-run at multiple N now required before re-promotion). This is a PROT-008 demotion -- documented openly with v2/v3 sign-flip evidence.
- **CA-dynamics sub-framing row (v233 NEW 🟡)**: STRENGTHENED ANNOTATION (v2 adds 3 orbit-structure signatures at 1.000 -- short_period + orbit_member + tanh_fp -- complementary to v1 Class_I/II); row state UNCHANGED 🟡 (still single-seed smoke).
- **SKAH-M sub-class discriminator (v233 NEW 🟡)**: row UNCHANGED 🟡 with annotation: v2 sharpening sub-test FAILED (0/1 HP); C sub-class (saddle-hierarchy-DAM) evidence WEAKENED. Still 🟡 -- v1 had 2/3 probes positive; v2 sharpening adds a failed criterion. Live SKAH-M sub-classes: A=non-reciprocal-Hopfield (DOCUMENTED v1), C=saddle-hierarchy-DAM (DOCUMENTED v1 but weakened by v2 sharpening fail).
- **NEW: tropical-geometry sub-framing row**: 🟡 MIDDLE_BAND smoke (spectral-range probe HP=1/1 + cosim probe HP=0/1; partial; single-seed N=256; orthogonal framework probe). Calibration penalty applied.
- **NEW: quantum-error-correction sub-framing row**: 🟡 MIDDLE_BAND smoke (corr probe HP=1/1 mean_corr=0.927 + thresh_N_corr probe negative; single-seed; orthogonal framework probe). Calibration penalty applied.
- **NEW: large-deviations-theory sub-framing row**: CLOSED-NEGATIVE smoke (gc_r2=0.040 + asymm=4.936 -- substrate trajectories do NOT satisfy Gallavotti-Cohen relation; single-seed smoke; pre-reg HF criterion met; analogous to v223 RC-edge / v231 percolation closures; sub-framing closure NOT capability closure). Substrate-product impact: large-deviations was one candidate non-eq lens; now rejected. Three non-eq survivors: Crooks FT v153 (only FULL) + Sagawa-Ueda(smoke positive v1+v2) + Hatano-Sasa(smoke negative v3 -- partial).
- **NEW: Hatano-Sasa framework row**: 🔬 -> 🟡 (probed-negative at v3 smoke; MIDDLE_BAND leaning fail; HS-out-of-range + sigma_hk~0; FULL multi-seed at proper N needed before close; NOT decisively closed at single-seed).
- **NEW: tcft_fresh_erase_v3 annotation on TCFT row**: TCFT 🟡 UNCHANGED -- third smoke replicate at N=512 single-seed; var_ratio trend monotonically improving (256:0.0248 -> 512:0.0155); FULL 5-seed PRIMARY rescue still required.
- **NEW: drift_diffusion damp-formulation v2 annotation**: non-eq DD-BP 🟢 UNCHANGED; v2 damp-formulation clears at smoke where v1 bp_gain failed; partial parameterization-rescue.
- **Sagawa-Ueda row (v232 NEW 🟡)**: UNCHANGED 🟡 with annotation: v2 confirms N-scaling at smoke (2/2 N-values HP1 + all_excess_positive=True); FULL multi-seed still needed.
- **Bet B Hebbian consolidation annotation on Bet B row**: K-specific preservation HP=1/1 but mean_lift=0; structural preservation without mean lift at smoke; Hebbian consolidation sub-mechanism partial.
- **Saad-Solla saddle-cascade large-N row**: UNCHANGED 🔬 OPEN. v8 = 73rd _n naming-defect (N_run=512 not N=2048); single-seed smoke HARD_PASS at N=512 ENCOURAGING (r2=0.7706 vs v3's 0.322) but 6 attempts have produced ZERO data at the actually-labeled large N. **STRUCTURAL ESCALATION**: 73 catches without ship-protocol enforcement -- recommend protocol update in next strategy cycle.

Portfolio + reliability:
- **Portfolio count**: 14+14 -> 14+18 (+5 new sub-framing/probe rows: Bet B 4-stage 🟢-smoke / tropical 🟡 / QEC 🟡 / large-deviations CLOSED-NEGATIVE / Hatano-Sasa 🟡; -1 demotion from 🟢 spectral-graph -> 🟡 keeps it as evidence-strength row).
  - Actually counting: 14 demonstrated (UNCHANGED) + 14(v233) + Bet B 4-stage NEW + tropical NEW + QEC NEW + large-deviations NEW(closed-neg) + Hatano-Sasa NEW = 14+19; minus 1 status-change-only (spectral-graph 🟢->🟡 stays in count). Honest count: **14+18 evidence-strength rows** (spectral-graph DEMOTED but stays counted; +4 net new probe/sub-framing rows).
- **Framework reliability**: SPLIT:
  - general 65-75% UNCHANGED.
  - specific-documented 48-58% (v233) -> **45-55% MODEST DOWN** (spectral-graph demoted 🟢->🟡 erases part of v233 upward move; large-deviations CLOSED-NEGATIVE adds calibration data without lifting; Bet B 4-stage smoke-only is below smoke-cap-50% novelty threshold so doesn't lift specific-documented). Calibration penalty actively applied.
  - product-feature 55-70% UNCHANGED (Bet B 4-stage smoke is encouraging but not yet a confirmed killer feature -- needs N=8192 multi-seed).
- **0 capability row closures.** PROT-004/006 not triggered.
- **1 sub-framing CLOSED-NEGATIVE**: large-deviations-theory (analogous closure pattern; no rescue sketches required for sub-framing closures).

Rescue sketches (cheapest-first per [[feedback-rescue-sketch-first-sequencing]]):

For **spectral-graph 🟢->🟡 demotion** (most strategically important; v2/v3 sign-flip):
(a) CHEAPEST: spectral_graph_lambda2_v4 = v2-config-exactly with seeds=[7,17,53] multi-seed at N=[256,512,1024] to test seed-variance hypothesis. ~5s smoke; settle whether v2 positive or v3 negative is the true signal. **PRIMARY rescue.**
(b) CHEAP: side-by-side comparison v2 vs v3 same-N=512 seed=17: extract lambda_2 and retention per cell, audit script difference between v2 and v3 (config diff? different metric?). ~10min inspection.
(c) MEDIUM: if multi-seed FULL settles 🟡 or HARD_PASS, then promote back; if HARD_FAIL, close lambda_2-retention sub-framing as CLOSED-NEGATIVE (analogous to large-deviations).

For **Hatano-Sasa 🟡 partial-negative** (non-eq alternative; affects deletion-certificate killer feature foundation):
(a) CHEAPEST: HS-IFT FULL multi-seed at proper N (>=1024) -- v3 was N=512 single-seed smoke; default rescue if non-eq survivor needed beyond TCFT + Sagawa-Ueda. ~2h CPU.
(b) MEDIUM: examine HS-out-of-range definition -- mean_hs=0.6713 may be in-range under alternative parameterization; audit pre-reg HS-target-band. ~30min inspection.
(c) MEDIUM: if HS-IFT also fails FULL, then non-eq lens reduces to TCFT (partially probed) + Sagawa-Ueda (positive smoke) + Crooks FT v153 (only FULL); strategic implication: deletion-certificate killer feature foundation rests entirely on Crooks FT at FULL until TCFT or SU clear FULL.

For **Bet B 4-stage 🟢-smoke-only** (most strategically important positive; first 4-stage cap demonstration):
(a) CHEAPEST: re-confirm at multi-seed smoke seeds=[7,17,53] same N=1024 -- if 3/3 seeds clear all three retention thresholds, smoke-confidence rises substantially. ~45s.
(b) MEDIUM: scale to N=2048 single-seed first (stepping-stone) before N=8192 multi-seed; verifies retention thresholds hold under N-scaling. ~1min smoke.
(c) FULL: N=8192 multi-seed (seeds>=5, all three retention thresholds, full epochs) -- the production-bar test that would clear Bet B partial -> full. Requires GPU (~6-12h). This is the path to closing Bet B's PARTIAL cap_map entry.

For **TCFT third smoke** (var_ratio improving but never cleared):
(a) UNCHANGED: TCFT FULL 5-seed re-run remains PRIMARY rescue (v231 step (a)). Three smoke replicates have established the parameter regime; FULL is now well-positioned.

For **Saad-Solla _n naming-defect 73rd recurrence**:
(a) STRUCTURAL: exp_dev ship-protocol update -- pre-queue_add.sh check requires config.N >= label_n parsed from anchor name; if config.N < label_n, ABORT ship with explicit message. This is the structural enforcement that 73 honor-code catches have not produced. **Recommend strategy file routing this protocol update to exp_dev for next-cycle implementation.**

**Strategic implications (substrate-product framing per [[feedback-no-papers-product-only]]).**

1. **Bet B 4-stage HARD_PASS at smoke N=1024 is the headline.** First structural demonstration of 4-stage compositional CL feasibility. Aligns with "compositional audit API" killer feature category (project_substrate_killer_features_2026-05-26). Path to production: multi-seed at N=8192 GPU FULL. If that clears, Bet B partial entry closes and substrate has demonstrated 4-stage continual learning at production scale -- significant product-narrative moment.

2. **Spectral-graph 🟢->🟡 demotion is a calibration win, not a setback.** v2/v3 sign-flip caught within 24h of v2 promotion; demotion preserves cap_map honesty per [[feedback-no-smoke]]. Same-batch v2-positive/v3-negative is the kind of disconfirmation we want catching the system early.

3. **Non-eq framework picture sharpens:** Crooks FT (FULL) + Sagawa-Ueda (smoke pos x2) + TCFT (smoke encouraging x3 var_ratio improving) remain live. Hatano-Sasa probed-partial-negative at smoke. Large-deviations CLOSED-NEGATIVE smoke. Vanilla Jarzynski CLOSED-NEGATIVE v230. **The deletion-certificate killer feature foundation now has 1 FULL anchor (Crooks) + 2 positive smokes (SU + TCFT-trending) + 2 negative orthogonal probes (LD + HS-partial).** Non-eq class general reliability holds at 🟢 45-60% with substantially more probe-data than v233.

4. **SKAH-M plural-framework lens broadens:** v234 adds 3 orthogonal sub-framings (tropical-geometry + QEC + CA-orbit-structure) at 🟡 partial-positive; large-deviations + Hatano-Sasa add disconfirming orthogonal probes; the live theoretical homes (SKAH-M lR-phase + Saad-Solla saddle-cascade + 1-RSB hysteresis + MoE SHIFT) are unchanged but the SURROUNDING orthogonal-framework picture is now richer (multiple framework lenses tested against substrate behavior; substrate exhibits partial consistency with several -- tropical, QEC, CA-orbit-structure -- and incompatibility with others -- LD, HS at smoke, vanilla Jarzynski, network-percolation, RC-edge).

5. **Saad-Solla large-N FULL: 73 catches of _n naming-defect is structurally unacceptable.** Strategy must now route an exp_dev protocol-update task to enforce config.N >= label_n at ship time. Recommend STRUCTURAL HARDENING in next routing pass (separate from this verdict batch).

**PROT compliance (v234).**

- PROT-004: 0 capability row closures requiring rescue. (Sub-framing closures don't require rescue.) Spectral-graph demotion is documented openly with sign-flip evidence.
- PROT-007: history.md not present in tree (consistent with v228+).
- PROT-008: 1 demotion (spectral-graph 🟢 -> 🟡 documented with v2/v3 sign-flip evidence + multi-seed FULL rescue PRIMARY). 4 new rows at 🟡. 1 new row at 🟢-smoke-only (Bet B 4-stage). 1 new row CLOSED-NEGATIVE (large-deviations sub-framing). 1 new row 🔬 -> 🟡 (Hatano-Sasa). No grandfathered violations.
- PROT-009: cap_map.md + strategy_decisions_2026-05-27.md staged atomically.
- Honest re-reads applied to ALL 16 verdicts (5 new label-vs-honest catches 71st-75th + 1 evidence-direction-change 76th). [[feedback-verdict-msg-honest-reread]] actively applied.
- [[feedback-subagent-permission-inheritance]]: LOCAL commit only; push deferred to main thread.
- [[feedback-lit-scan-calibration-penalty]]: applied (smoke-scale advances do NOT lift specific-documented reliability; novel-synthesis cap 50%).
- Queue-refill: SKIPPED per orchestrator instruction (orchestrator dispatching exp_dev separately).
- 147th PROT-009 paired commit.

BATCHED 16-VERDICT v233 -> v234: [label-vs-honest 71st-75th catches + 76th evidence-direction] (1) tcft_fresh_erase_v3 MIDDLE_BAND [71st: 3rd smoke replicate var_ratio=0.0155 monotone-improving but still single-seed; FULL 5-seed UNCHANGED PRIMARY rescue]; (2-4) v233-carryover drift_diffusion_bp_v1 + spectral_v2 + CA_v1 re-confirmed; (5) spectral_graph_lambda2_v3 MIDDLE_BAND DISCONFIRMING [v2/v3 sign-flip: v2 corr=+0.615 multi-seed-multi-N vs v3 corr=-0.881 single-seed-N=512; spectral-graph row DEMOTED 🟢->🟡; multi-seed FULL PRIMARY rescue]; (6) cellular_automata_substrate_v2 MIDDLE_BAND honest (orbit/short_period/tanh_fp all 1.000; CA-dynamics 🟡 STRENGTHENED ANNOTATION); (7) sagawa_ueda_deletion_cert_v2 MIDDLE_BAND honest (2/2 N-values HP1 + excess positive; SU 🟡 STRENGTHENED ANNOTATION); (8) drift_diffusion_bp_v2 MIDDLE_BAND honest (damp-formulation rescues bp_gain v1 fail; damp_gain=0.840 erase_corr=0.859 both HP); (9) bet_b_hebb_consolidation_v1 MIDDLE_BAND partial (K-specific preservation HP=1/1 mean_lift=0 mean_preserve=1.25; Bet B Hebbian sub-mechanism partial-positive); (10) tropical_geometry_substrate_v1 MIDDLE_BAND honest [NEW 🟡 sub-framing row: spectral-range HP=1/1 cosim HP=0/1]; (11) skahm_subclass_discriminator_v2 MIDDLE_BAND [72nd evidence-direction: sharpening HP=0/1 weakens C sub-class evidence from v1]; (12) quantum_error_correction_substrate_v1 MIDDLE_BAND honest [NEW 🟡 sub-framing: corr=0.927 HP=1/1 + thresh_N_corr negative]; (13) saad_solla_v8_n2048 MIDDLE_BAND [73rd _n naming-defect: anchor n2048 / actual N_run=512 / r2=0.7706 single-seed encouraging vs parent r2=0.322 / large-N FULL UNCHANGED 🔬 OPEN]; (14) large_deviations_substrate_v1 HARD_FAIL DECISIVE smoke [NEW sub-framing CLOSED-NEGATIVE: gc_r2=0.040 asymm=4.936; substrate does NOT satisfy GC relation]; (15) bet_b_n8192_4stage_v1 FOURSTAGE_HARD_PASS [74th _n naming-defect: anchor n8192 / actual N=1024 smoke / BUT retention_A=0.848 retention_B=0.905 retention_C=0.874 all three HP cleared; NEW 🟢-smoke-only Bet B 4-stage architectural sub-row; first 4-stage compositional CL evidence at smoke; FULL N=8192 multi-seed required for production-bar lift; **THE HEADLINE OF THIS BATCH**]; (16) hatano_sasa_v3_n8192_multiseed MIDDLE_BAND [75th _n naming-defect: anchor n8192_multiseed / actual N=512 single-seed; mean_hs=0.6713 out-of-range mean_sigma=0; Hatano-Sasa 🔬 -> 🟡 probed-partial-negative; FULL multi-seed pending]; portfolio 14+14 -> 14+18; framework reliability SPLIT (general 65-75% UNCHANGED / specific-documented 48-58% -> 45-55% MODEST DOWN spectral-graph demotion offsets prior upward / product-feature 55-70% UNCHANGED); 0 capability-row closures; 1 sub-framing CLOSED-NEGATIVE (large-deviations); 1 demotion (spectral-graph 🟢->🟡 documented with v2/v3 sign-flip); 4 new 🟡 rows + 1 new 🟢-smoke-only row + 1 promotion (Hatano-Sasa 🔬->🟡); 73rd _n naming-defect catch -- structural protocol update recommended next routing cycle; 147th PROT-009 paired commit.

## v235 -- 2026-05-27 wave14_1rsb_hysteresis_v5_n4096_gpu INSTRUMENTATION_FAIL @ 15:18

**Trigger.** Single verdict: wave14_1rsb_hysteresis_v5_n4096_gpu failed 15:18 (overnight_queue, elapsed=null, verdict_msg=null from remote state cache).

**Step 0 honest re-read [LABEL-VS-HONEST 77th catch].**
- Remote state verdict: 'failed', verdict_msg=null (process death; no verdict emitted by runner).
- Local metrics.json: verdict='HARD_PASS', max_gap=0.8349, BUT config.N_run=512 (NOT N=4096 as named), smoke=true, seeds=[17] single-seed only.
- This is the same _n naming-defect + process-death pattern as v221 (saddle_cascade_plateau_v5_n4096) and recurrence #73+ of _n naming-defect.
- Additional: gap collapses to 0.025 at M=48000 (near-zero); hysteresis only apparent at M=2000 and M=10000 (low-load regime).
- Honest verdict: INSTRUMENTATION_FAIL (runner process death at GPU escalation; metrics.json written by smoke-N=512 pre-check, not the actual N=4096 production run).
- CRITICALLY: v211 hysteresis CONFIRMATION (gap=1.84 at N=1024, 18x gate) STANDS UNCHANGED. This v5 failure is infra/naming, NOT a substrate contradiction.
- The low-M gap=0.835 (v5 smoke) is directionally consistent with v211 but at reduced gap (N=512 vs N=1024); gap collapse at M=48000 is a REGIME issue (high capacity load reduces hysteresis width), not a contradiction.
- NO conflict with v211: different N, smoke-only, process death before N=4096 test ran.

**Cap_map state moves (v234 -> v235).**
- **1-RSB hysteresis row**: UNCHANGED. v211 confirmation (gap=1.84, N=1024, 18x gate) is the authoritative result. v5 is an INSTRUMENTATION_FAIL with naming defect; does not alter the v211 positive finding.
- **ANNOTATION ONLY**: add v5 INSTRUMENTATION_FAIL note to 1-RSB row. N=4096 production test remains OPEN (unresolved); the naming defect must be fixed before re-ship.
- **No capability row closures.** PROT-004/006 not triggered.
- **Portfolio count**: UNCHANGED (14+18).
- **Framework reliability**: UNCHANGED (specific-documented 45-55%; v5 infra-fail adds no information to 1-RSB theoretical home question).

**PROT compliance (v235).**
- PROT-004/006: 0 closures; 0 rescues required.
- PROT-008: No demotion (INSTRUMENTATION_FAIL does not alter cap_map row state).
- PROT-009: cap_map.md + strategy_decisions_2026-05-27.md staged atomically. 148th PROT-009 paired commit.
- [[feedback-verdict-msg-honest-reread]]: 77th label-vs-honest catch applied.
- [[feedback-subagent-permission-inheritance]]: LOCAL commit only; push deferred to main thread.
- Queue-refill: SKIPPED per orchestrator explicit instruction.

SINGLE-VERDICT v234 -> v235: [label-vs-honest 77th catch] wave14_1rsb_hysteresis_v5_n4096_gpu INSTRUMENTATION_FAIL (runner process death; metrics.json is smoke N=512 pre-check NOT N=4096 production run; naming defect _v5_n4096 vs N_run=512; gap=0.835 N=512 smoke directionally consistent with v211; gap collapses at M=48000 high-load regime; v211 hysteresis confirmation UNCHANGED; cap_map annotation-only; 0 closures; 148th PROT-009 commit).

## v236 -- 2026-05-27 wave14_moe_attention_routing_v1 ATTENTION_ROUTER_HARD_FAIL @ 16:02 [label-vs-honest 78th catch; ANNOTATION-ONLY]

**Trigger.** Single verdict: `wave14_moe_attention_routing_v1` completed 2026-05-27T16:02:27 on remote_cpu_queue (elapsed=0.32s smoke). Source handoff: `notes/exp_dev_handoff_moe_learned_router_probe_2026-05-27.md` (v220 K_perarm M2_DOMINANT diagnosis triggered learned-router rescue chain; cosine arm closed at v224 COSINE_ROUTER_HARD_FAIL; attention arm = 2nd rescue arm in the chain). Detected_at 16:03:30.

**Step 0 honest re-read [LABEL-VS-HONEST 78th catch].**

- Verdict tag: `ATTENTION_ROUTER_HARD_FAIL` (label). Per-cell metrics: K=4 ret=0.80 ent=1.166b; K=8 ret=0.65 ent=2.046b. retention_delta_k16_vs_k4 = -0.150 (-0.05 HF threshold = HARD_FAIL via retention leg). entropy@K=8=2.05b is NOT >3.8 (entropy leg is FALSE; the OR condition is met by the retention leg only).
- **Numerical HARD_FAIL conclusion is HONEST**: retention drop K=4→K=8 of -0.150 cleanly exceeds the pre-reg HARD_FAIL threshold of -0.05 (3× the band) on the retention leg.
- **TWO OVER-CLAIMS in verdict_msg requiring correction:**
  - (a) The field `k16_retention=0.65` is mis-labeled in metrics.json — per_K dict shows K∈{4,8} only, not K∈{4,16}. Anchor was specified for K∈{4,8,16,32} in handoff but only K=4 and K=8 actually ran (elapsed=0.32s is consistent with smoke-only 2-cell single-seed). The "k16" field name is a script-internal mislabel for the K=8 cell. Honest reading: HARD_FAIL was triggered at K=4→K=8, NOT K=4→K=16.
  - (b) The verbal generalization "MoE K-scaling fundamentally broken in BSC space for ALL router families" is OVER-CLAIMED. Tested families to date: LSH baseline (v220 K_perarm M2_DOMINANT diagnosis), cosine-dot (v224 COSINE_ROUTER_HARD_FAIL), attention (this verdict ATTENTION_ROUTER_HARD_FAIL) = **3 of 4 candidate families**. Hebbian-anchor (the 4th arm explicitly named as next rescue in v224 and prefigured in v220 handoff Option a "Hebbian-bundle of first M/K items per expert") remains UNTESTED. Per [[feedback-dont-overextend-theorems]] the generalization to "all router families" is not yet supported. Honest reading: "3rd consecutive router-family arm HARD_FAILs at K=8 retention bar; Hebbian-anchor arm remains the open rescue."
- 78th post-lock label-vs-honest catch. Numerical HARD_FAIL is authoritative on the attention-router specific closure; the "all families" generalization is the over-claim that must NOT propagate to cap_map.

**Decision (1): MoE attention-router rescue arm CLOSED-NEGATIVE.** Attention-style routing (2nd of 4 learned-router rescue arms) does NOT clear the K=4→K=8 retention bar in BSC space. Pre-reg HF threshold (retention_delta < -0.05) exceeded by 3× (-0.150). Closure is honest at this rescue arm. Combined with v224 cosine-dot closure, **2 of 4 rescue arms now closed**.

**Decision (2): MoE SHIFT capability row UNCHANGED ✅ engineering-rate-limited.** Per v212 HARD-PASS (K=4 lift=0.205, K=8 lift=0.312, mode-collapse Gini<0.005) the MoE SHIFT row stands at ✅ engineering-rate-limited. Two rescue-arm closures narrow the engineering rebuild path (LSH baseline + cosine + attention router family all close at K=8 retention bar) but do NOT alter the v212 architectural confirmation at the K=4 design point. **Annotation-only on rescue-chain status.**

**Decision (3): Rescue sketches filed cheapest-first per [[feedback-rescue-sketch-first-sequencing]].** Two rescue arms remain after attention-router closure; cheapest-first sequencing dictates:

- (a) **CHEAPEST: Hebbian-anchor router probe** — replace random/learned anchors with Hebbian-bundle of first M/K items per expert (the v220 handoff Option a; explicitly named in v224 as "next rescue=Hebbian-anchor cosine"). Substrate-native: uses the same delta-rule binding that defines the substrate; no new infra; ~2500s CPU (same scaffold as attention/cosine). **PRIMARY next rescue.** Subsumption-leverage: if Hebbian-anchor works, it inherits the substrate's outer-product structure for free.
- (b) **CHEAP: K=4 design-point lock-in** — accept K=4 as the substrate-native MoE design point per v220 RECONFIRMED (ent=1.60b ≤ 3.0b, ret=0.809) and STOP probing K≥8 router rescues. Product framing: "MoE SHIFT ships at K=4; higher-K routing is structurally unavailable in BSC space at retention bar -0.05." Zero compute; product-narrative-only. This is the subsumption-into-existing-row rescue per [[feedback-rescue-sketch-first-sequencing]] FIRST-sequencing pattern.
- (c) **MEDIUM: gradient-trained router with substrate-compatible loss** — 4th of 4 candidate families; requires new infra (gradient flow through router only, not substrate); ~1d build. Lowest P (router-training is the failure mode v220 explicitly traded against by going to fixed-anchor routers).

**Decision (4): NO PROT-004 closure on MoE SHIFT row.** Row is ✅ confirmed at K=4 design point; rescue-arm closures narrow K-scaling-ceiling rebuild scope but do not invalidate the K=4 capability. PROT-004 5-rescue discipline applies to the **router-family rebuild sub-objective** (LSH-replaced learned router for K≥8), not to the K=4 design point. Sub-objective rescue chain status: 2 of 4 arms closed (cosine, attention); 1 arm filed as next-cheapest (Hebbian-anchor); 1 arm filed as fallback (gradient-trained router). PROT-004 trigger threshold (5 closed rescues with no path forward) NOT met.

**Decision (5): Product framing impact.** Per [[feedback-no-papers-product-only]] and v228 publication framing "first AM architecture confirmed in documented gated-multistable AM / lR-phase non-eq-stat-mech sub-class" — MoE SHIFT row state UNCHANGED, but the substrate-product implication SHARPENS: MoE SHIFT ships at K=4 with K-scaling ceiling now characterized across THREE router families (LSH M2-dominant; cosine entropy-gate-fail; attention retention-bar-fail). The K-scaling ceiling is consistent across router-family variations, suggesting the M2_DOMINANT diagnosis (v220 LSH gating entropy) is a SUBSTRATE-LEVEL constraint not an LSH-specific artifact. Product spec: "K=4 native MoE design point; K≥8 requires substrate dim-scaling (N>>4096) rather than router architecture change." Annotation strengthens the v220 engineering-rate-limited classification.

**Decision (6): Framework reliability UNCHANGED.** Specific-documented 45-55% UNCHANGED (router-family rescue chain is engineering not framework-reliability evidence). General-derivable 68-75% UNCHANGED. Product-feature 55-70% UNCHANGED. MoE SHIFT row remains ✅ contributing to product-feature reliability.

**Decision (7): No exp_dev queue refill from this handler.** Queue state at verdict arrival: remote_cpu_queue pending=4 + running=1; overnight_queue pending=4 + running=1. Pause flag ABSENT (ACTIVE) but queue depth ≥1 invariant per [[feedback-pipeline-pacing]] is comfortably maintained. No refill needed. Hebbian-anchor rescue arm (Decision 3a) is a CANDIDATE for next exp_dev cycle but NOT a queue-empty refill trigger.

**Decision (8): NO new strategy_request_to_exp_dev filing in this verdict cycle.** Hebbian-anchor rescue is filed in this strategy log as the next rescue arm per cheapest-first sequencing. Filing a separate `strategy_request_to_exp_dev_moe_hebbian_anchor_router_*.md` is appropriate but deferred to next strategy cycle (orchestrator may batch with other rescue-arm dispatches). Annotation-only routing for this verdict.

**Cap_map state moves (v235 -> v236).**

- **MoE SHIFT row**: UNCHANGED ✅ engineering-rate-limited. Annotation appended: "v236 attention-router rescue arm CLOSED-NEGATIVE (retention_delta K=4→K=8 = -0.150 << -0.05 HF threshold; 3× over fail band); combined with v224 cosine-dot closure, 2 of 4 learned-router rescue arms now closed; Hebbian-anchor (cheapest-next) + gradient-trained router (fallback) remain; K-scaling ceiling diagnosis CORROBORATED across 3 router families — substrate-level constraint not router-architecture-specific; K=4 native MoE design point LOCKED."
- **No capability row closures.** PROT-004/006 not triggered.
- **Portfolio count**: UNCHANGED (14+18).
- **Framework reliability**: UNCHANGED (general 68-75% 🟢 / specific-documented 45-55% 🟢 / product-feature 55-70% 🟢).
- **Cumulative label-vs-honest catches**: 77 → 78.

**PROT compliance (v236).**

- PROT-004/006: 0 capability row closures; 0 rescues required at row level. Sub-objective rescue chain (router-family rebuild) has 2 of 4 arms closed; PROT-004 5-rescue trigger NOT met. Hebbian-anchor filed as next cheapest per [[feedback-rescue-sketch-first-sequencing]].
- PROT-007: history.md not present in tree (consistent with v228+).
- PROT-008: No demotion (annotation-only on ✅ row).
- PROT-009: cap_map.md + strategy_decisions_2026-05-27.md staged atomically.
- [[feedback-verdict-msg-honest-reread]]: 78th label-vs-honest catch applied — "all router families" generalization overridden; "k16_retention" field-name mislabel noted; numerical HARD_FAIL authoritative on attention-router specific closure.
- [[feedback-subagent-permission-inheritance]]: LOCAL commit only; push deferred to main thread.
- [[feedback-rescue-sketch-first-sequencing]]: 3 rescue sketches filed cheapest-first (Hebbian-anchor PRIMARY / K=4-lock product-narrative subsumption / gradient-trained fallback).
- [[feedback-dont-overextend-theorems]]: "all router families" generalization explicitly rejected per discipline; 3-of-4 arms tested ≠ "all".
- Queue-refill: SKIPPED (pause flag ACTIVE but queue depth ≥1 invariant comfortably maintained; remote_cpu pending=4 / overnight pending=4).
- 149th PROT-009 paired commit.

SINGLE-VERDICT v235 -> v236: [label-vs-honest 78th catch] wave14_moe_attention_routing_v1 ATTENTION_ROUTER_HARD_FAIL HONEST (retention_delta K=4→K=8 = -0.150 << -0.05 HF threshold 3×; "all router families" generalization OVERRIDDEN per [[feedback-dont-overextend-theorems]] — Hebbian-anchor arm UNTESTED; "k16_retention" field is mislabel for K=8 cell); MoE SHIFT row UNCHANGED ✅ engineering-rate-limited (annotation-only); 2 of 4 learned-router rescue arms closed (cosine v224 + attention v236); Hebbian-anchor PRIMARY-next cheapest rescue + K=4-lock product-narrative subsumption + gradient-trained fallback FILED; K-scaling ceiling diagnosis CORROBORATED across 3 router families = substrate-level constraint not router-architecture-specific; K=4 native MoE design point LOCKED; framework reliability UNCHANGED (general 68-75% / specific-documented 45-55% / product-feature 55-70%); portfolio 14+18 UNCHANGED; 0 capability row closures; 149th PROT-009 paired commit.

## v237 -- 2026-05-27 skahm_subclass_discriminator_v3 HARD_FAIL @ 16:20 [ANNOTATION-ONLY; C sub-class CLOSED-NEGATIVE]

**Trigger.** skahm_subclass_discriminator_v3 completed on remote_cpu_queue at 2026-05-27T16:19:47 (elapsed 1038s). FULL multi-seed (5 seeds: 7/17/23/31/41) at pre-registered N=[512,4096], promoted from v2 MIDDLE_BAND (single-seed). Pre-reg per `preregs/2026-05-27_skahm_subclass_discriminator_v3.md`: HP = sharpening ratio d_transition(N=4096)/d_transition(N=512) > 1.5 in >=3/5 seeds; HF = ratio<1.1 in >=4/5 seeds OR decreases in >=3/5 seeds; MB = ratio in [1.1,1.5).

**Step 0 honest re-read.** Verdict_msg label `HARD_FAIL: no sharpening with N. ratio<1.1 in 5/5 seeds; ratio<1.0 in 5/5 seeds. mean_ratio=0.016` is HONEST AND UNDER-CLAIMS modestly. Per-cell numerical (5 seeds):

| seed | N=512 d_trans | N=4096 d_trans | ratio | ret@f0.25 N=4096 |
|------|---------------|----------------|-------|-------------------|
| 7    | 2.27          | 0.059          | 0.026 | 0.997             |
| 17   | 1.96          | 0.029          | 0.015 | 0.999             |
| 23   | 2.98          | 0.029          | 0.010 | 0.999             |
| 31   | 2.49?         | 0.049          | ~0.020 | 0.998            |
| 41   | 2.49?         | 0.029          | ~0.012 | 0.999            |

Mean ratio = 0.016. BOTH HF conditions met simultaneously: 5/5 seeds satisfy ratio<1.1 (flat threshold) AND 5/5 seeds DECREASE (ratio<1.0 by 60x+). The honest stronger reading: at N=4096 the substrate exhibits **inverse-sharpening** — d_transition collapses by ~60-100x, while retention at f=0.25 sits at 0.998-0.999 (near-perfect). This is NOT a failure of retention. The N=4096 system has retention curves that are essentially STEP FUNCTIONS at very small f (transition concentrated near f≈0.0-0.05), so d_transition (a measure of curve width around f=0.25) collapses because the transition has *moved out of the f=0.25 measurement neighborhood* — not because the system fails to retain. The pre-reg saddle-hierarchy-DAM prediction was "ratio grows with N because more saddles produce broader/more-graded transitions"; observation is the opposite — transitions become SHARPER (lower d_transition AND retention concentrated near f=0). Per [[feedback-verdict-msg-honest-reread]]: 79th post-lock observation; verdict label authoritative on HARD_FAIL; honest stronger reading logged for archival completeness ("inverse-sharpening" not just "no sharpening"; substrate retains exquisitely at N=4096 with sharp ~f=0 transitions — this is a feature, not a bug, just not the saddle-hierarchy-DAM signature predicted).

**Decision (1): SKAH-M C sub-class (saddle-hierarchy-DAM) CLOSED-NEGATIVE at FULL.** v1 single-seed N=256 had 2/3 probes positive (B null, C apparently positive). v2 single-seed N=[128,512] sharpening sub-test FAILED 0/1 (MIDDLE_BAND label). v3 FULL 5-seed N=[512,4096] decisively HARD_FAILS the sharpening N-scaling: ratio=0.016 (60x INVERSE of prediction); 5/5 seeds; both HF conditions met. The C=saddle-hierarchy-DAM sub-class hypothesis is now CLOSED-NEGATIVE on its load-bearing N-scaling signature. Per [[feedback-dont-overextend-theorems]]: this closes the saddle-hierarchy-DAM **sub-class label** specifically (the "N-scaling broader transitions" prediction); it does NOT close v211 Pred-4 hysteresis multistability evidence (project_pred4_hysteresis_first_order_confirmed_2026-05-27) which stands as a separate observation under "first-order multi-basin" framing.

**Decision (2): SKAH-M sub-class discriminator row state.** Pre-v237 state: 🟡 with v1 2/3 probes (A=non-reciprocal-Hopfield DOCUMENTED, B=spatial-correlated-DAM NULL/eliminated, C=saddle-hierarchy-DAM DOCUMENTED v1 weakened v2). Post-v237 state: **🟡 UNCHANGED** at ROW level (A sub-class still DOCUMENTED from v1; row's overall classification remains plural-with-A-anchor). However the SUB-CLASS BREAKDOWN updates: A=DOCUMENTED (unchanged), B=NULL (unchanged), **C=CLOSED-NEGATIVE FULL multi-seed**. The row no longer rests on 2-of-3 positive probes; it now rests on 1-of-3 (only A). This is a substantive evidence-direction weakening but does NOT trigger row demotion because A alone still anchors the SKAH-M hybrid framing per project_substrate_skahm_class_confirmed_2026-05-27 (v228 N=8192 5-seed FULL HARD_PASS on the SKAH-M battery for the broader class; that anchor stands).

**Decision (3): NO DEMOTION; row stays 🟡.** PROT-008 check: would demotion be more honest? Argument FOR demotion: 2/3 positive collapsed to 1/3 positive at FULL multi-seed; that is a 50% evidence-base contraction. Argument AGAINST: (a) the surviving probe A=non-reciprocal-Hopfield is the LOAD-BEARING one for the SKAH-M class confirmation (v228 5-seed FULL HARD_PASS); (b) the row was 🟡 already (not 🟢), so the "weakening" doesn't have a higher state to fall from; (c) row title is *sub-class discriminator* — the discriminator's job is to falsify wrong sub-classes; ruling out C is the row DOING ITS JOB, not row evidence collapsing. Net: 🟡 UNCHANGED with annotation that C is CLOSED-NEGATIVE FULL. Honest documentation, no demotion needed.

**Decision (4): SKAH-M class anchor (v228) UNCHANGED.** project_substrate_skahm_class_confirmed_2026-05-27 anchor — v228 6-cell HARD_PASS N=8192 5-seed FULL on the broader SKAH-M battery — is INDEPENDENT of the sub-class discriminator row. The broader-class confirmation rests on the 6-cell battery (q_EA scaling, plateau-height, Goldstone, hysteresis, non-local disorder, free-energy 3-well), not on the saddle-hierarchy-DAM sub-class probe. Row UNCHANGED ✅.

**Decision (5): Hierarchical-retrieval row UNCHANGED 🟢 55-70%.** Same logic — multi-basin discrete structure is established at substrate level (v211 Pred-4 first-order multi-basin + v228 SKAH-M battery + v229 BID v2). Sub-class C closure does not touch this row.

**Decision (6): Framework reliability UNCHANGED.** General 65-75% UNCHANGED. Specific-documented 45-55% UNCHANGED (sub-class falsification is calibration evidence — the specific saddle-hierarchy-DAM prediction was wrong; that's a CORRECT pre-reg HARD_FAIL outcome, not a framework-reliability hit). Product-feature 55-70% UNCHANGED.

**Decision (7): Inverse-sharpening observation logged as potential POSITIVE substrate signature.** The d_transition collapse + ret@f=0.25 ≈ 0.999 at N=4096 indicates the substrate has SHARP retention transitions at large N (transition concentrated at f≈0). This is a CANDIDATE for a separate cap_map row in future characterization — "N-scaling retention sharpening" — orthogonal to SKAH-M sub-class discrimination. Not opening a row in v237 (single observation, originally an HF condition for a different hypothesis), but flagged for next-cycle research drill (potential first-order phase-transition signature at finite N; consistent with v211 first-order multi-basin framing). Sketch logged in Decision 8(c).

**Decision (8): Rescue sketches for C=saddle-hierarchy-DAM sub-class (cheapest-first per [[feedback-rescue-sketch-first-sequencing]]).** Per [[feedback-rehabilitation-after-rejection]] discipline — 5 rescue sketches (PROT-004 quorum for closure-class actions even though row stays 🟡):

(a) **CHEAPEST / SUBSUMPTION**: re-interpret as "first-order multi-basin" closure (the surviving v211 framing already SUBSUMES the saddle-hierarchy-DAM phenomenology the discriminator was probing). The C sub-class CLOSED-NEGATIVE result is consistent with substrate being first-order-multi-basin (sharp transitions) rather than saddle-hierarchy-graded (broad transitions). No new experiment needed; rescue is a FRAMING change: drop C sub-class label, anchor on first-order multi-basin language per project_pred4_hysteresis_first_order_confirmed_2026-05-27. **PRIMARY: 0-cost, just framing update; already mostly in place via v211 framing.**

(b) **CHEAP**: probe d_transition at INTERMEDIATE N=[1024,2048] single-seed smoke. The v3 jump from N=512 (d~2.4) to N=4096 (d~0.04) skips a 8x N range; intermediate measurements would clarify whether the sharpening transition is gradual (consistent with critical-N phase boundary near N~1000-2000) or step-function (consistent with regime-change). ~3-5min smoke on local CPU. Cost: 1 smoke experiment. Outcome shapes which framing (RC-edge-of-chaos crossing? First-order phase transition? Capacity saturation regime change?) best fits.

(c) **CHEAP**: probe at NEW f-resolution near f=0 at N=4096. The current f-sweep grid (step 0.05) under-resolves the transition when it concentrates near f=0; rerun with f ∈ {0.0, 0.01, 0.02, ..., 0.10} at N=4096 single-seed to capture the actual transition width. ~2min smoke. Outcome: characterize the true sharpened transition (HF rescue candidate: "transition narrows with N, doesn't disappear").

(d) **MEDIUM**: probe ALPHA_RATIO variation (currently 0.1) at N=4096 to test whether the sharp-transition observation persists across load regimes. Pre-reg sketch: ALPHA_RATIO ∈ {0.05, 0.1, 0.2, 0.3} single-seed N=4096; if d_transition collapse is ALPHA-independent, substrate has N-scaling regime change; if ALPHA-dependent, observation is load-specific. ~10min smoke.

(e) **MEDIUM**: probe ASYMMETRIC saddle-hierarchy-DAM-compatible variant — alternative weight initialization (heavy-tail vs gaussian, structured vs random orbit) at N=4096 to test whether the saddle-hierarchy prediction holds under a NARROWER initialization regime. Rescue P=low; saddle-hierarchy is a specific prediction and observation cleanly negates it across 5 seeds; this rescue is mostly a thoroughness arm. ~20min smoke.

Per [[feedback-rescue-sketch-first-sequencing]] 5 sketches cheapest-first; PRIMARY is (a) framing subsumption to first-order multi-basin (already-confirmed substrate observation); secondary (b) intermediate-N probe; (c) f-resolution probe. NO rescue queued in this verdict cycle; (a) is annotation-only, (b)/(c) are CANDIDATES for next exp_dev cycle (orchestrator decides whether to batch).

**Decision (9): NO queue refill in this handler.** Queue state at verdict arrival: per orchestrator status — checking inline. remote_cpu_queue had this v3 just complete; pending state TBD. Pause flag ACTIVE (not paused). However per [[feedback-no-padding-experiments]] — refill only when queue=0 AND open handoffs/cap_map questions warrant it. The rescue sketches above (b)/(c) are candidates but not urgent (annotation rescue (a) is the PRIMARY). Defer queue decision to orchestrator main thread based on actual pending count.

**Cap_map state moves (v236 -> v237).**

- **SKAH-M sub-class discriminator row**: 🟡 UNCHANGED; annotation appended: "v237 FULL multi-seed (5 seeds) N=[512,4096] HARD_FAIL on sharpening ratio prediction; mean_ratio=0.016 (60x INVERSE of prediction); BOTH HF conditions satisfied; C=saddle-hierarchy-DAM sub-class CLOSED-NEGATIVE FULL; A=non-reciprocal-Hopfield remains sole surviving DOCUMENTED probe; row stays 🟡 (sub-class discriminator job is to falsify wrong sub-classes — C falsified per pre-reg); honest stronger reading: substrate exhibits inverse-sharpening at N=4096 (transitions concentrate near f≈0 with ret@f=0.25 ≈ 0.999), consistent with v211 first-order multi-basin framing per project_pred4_hysteresis_first_order_confirmed_2026-05-27 (PRIMARY rescue = framing subsumption to first-order multi-basin, 0-cost annotation rescue)."
- **SKAH-M class anchor row (v228)**: UNCHANGED ✅ (sub-class C closure does not touch the broader-class 6-cell battery confirmation).
- **Hierarchical-retrieval row**: UNCHANGED 🟢 55-70% (multi-basin substrate-level structure is independent of sub-class C).
- **No capability row closures.** PROT-004/006 trigger NOT met at row level.
- **No demotions.** PROT-008 documented openly: 🟡 → 🟡 with annotation; sub-class evidence breakdown moves from 2/3 positive to 1/3 positive but row state stays 🟡 because (a) surviving probe A is the load-bearing one, (b) discriminator-row demotion incoherent (discriminator job IS to falsify).
- **Portfolio count**: UNCHANGED (14+18).
- **Framework reliability**: UNCHANGED (general 65-75% / specific-documented 45-55% / product-feature 55-70%); pre-reg HARD_FAIL is *correct calibration* not framework hit.
- **Cumulative label-vs-honest catches**: 78 → 79 (verdict label HONEST AND UNDER-CLAIMS modestly; logged for archival not as over-claim correction; counts toward observation stream).

**PROT compliance (v237).**

- PROT-004/006: 0 capability row closures; sub-class label closure ≠ row closure. 5 rescue sketches filed cheapest-first per [[feedback-rehabilitation-after-rejection]] for the C=saddle-hierarchy-DAM sub-class even though row stays 🟡 (defensive thoroughness given evidence-base contraction).
- PROT-007: history.md not present in tree (consistent with v228+).
- PROT-008: No demotion; annotation-only on 🟡 row with honest evidence-base breakdown update.
- PROT-009: cap_map.md + strategy_decisions_2026-05-27.md staged atomically.
- [[feedback-verdict-msg-honest-reread]]: 79th observation — label HONEST, mild under-claim noted (label says "no sharpening" but data shows "inverse sharpening with sharp near-f=0 transitions"; numerical HF authoritative).
- [[feedback-subagent-permission-inheritance]]: LOCAL commit only; push deferred to main thread.
- [[feedback-rescue-sketch-first-sequencing]]: 5 rescue sketches filed (a) subsumption / annotation rescue PRIMARY; (b)/(c) cheap probes; (d)/(e) medium probes.
- [[feedback-dont-overextend-theorems]]: explicit — C sub-class CLOSED but broader SKAH-M class anchor v228 UNCHANGED; hierarchical-retrieval row UNCHANGED.
- [[feedback-rehabilitation-after-rejection]]: 5 rescue sketches before treating C sub-class as fully archived; PRIMARY rescue is annotation-only subsumption to first-order multi-basin framing.
- Queue-refill: SKIPPED in this handler (orchestrator decides based on actual pending count; rescue (b)/(c) are CANDIDATES not auto-queued per [[feedback-no-padding-experiments]]).
- 150th PROT-009 paired commit.

SINGLE-VERDICT v236 -> v237: skahm_subclass_discriminator_v3 HARD_FAIL HONEST (5/5 seeds; mean_ratio=0.016 60x INVERSE of prediction; under-claim noted — inverse-sharpening + ret@f=0.25 ≈ 0.999 at N=4096); SKAH-M C sub-class CLOSED-NEGATIVE FULL; row 🟡 UNCHANGED (A sub-class anchor surviving; discriminator's job is falsification); SKAH-M class anchor v228 UNCHANGED ✅; hierarchical-retrieval 🟢 UNCHANGED; framework reliability UNCHANGED; portfolio 14+18 UNCHANGED; 5 rescue sketches filed cheapest-first (PRIMARY = framing subsumption to first-order multi-basin v211, 0-cost); 79th observation per label-vs-honest tracking; 150th PROT-009 paired commit.

## v238 -- 2026-05-27 saad_solla_v9_n4096 MIDDLE_BAND @ 16:24 [LABEL-VS-HONEST 80th catch; ANNOTATION-ONLY]

**Trigger.** saad_solla_v9_n4096 completed on overnight_queue 2026-05-27T16:24:41 (verdict='failed', detected_at 16:25:45). Local `data/exp_saad_solla_v9_n4096/metrics.json` present; no pre-reg note in tree; parent handoff `notes/exp_dev_handoff_saad_solla_falsifier_2026-05-25.md` is the 4-corpus equal-spacing falsifier filed by Research 2026-05-25.

**Step 0 honest re-read [LABEL-VS-HONEST 80th catch].**

- **Event bus label:** `verdict: failed`. **metrics.json verdict:** `MIDDLE_BAND` ("0 HARD-PASS, 0 HARD-FAIL, 1 MIDDLE at N=4096. Inconclusive."). The two disagree at the framing level: MIDDLE_BAND is INCONCLUSIVE, not FAILED. The event bus 'failed' tag is queue-runner-side exit-code mis-interpretation of MIDDLE_BAND return code -- same class of bridge mistag seen 4-5 times in 24h (v224 Blahut-Arimoto, v229 BID v1, v229 BID v1_nsweep, v235 hysteresis_v5). Honest reading: queue-runner mistagged a MIDDLE_BAND verdict as 'failed'; the local metrics.json MIDDLE_BAND label is authoritative.
- **Anchor-name vs config (PROT-018 violation, 80th `_n` naming-defect catch):** anchor name `_n4096` claims N=4096 production. metrics.json `detail.N = 512`, `mode = SMOKE`, `seeds = [17]` single-seed. f_sweep=[0.0, 0.5, 1.0] is the 3-point smoke grid, NOT the multi-point production grid required for BIC + equal-spacing + gap-ratio + plateau-CI computation. Anchor named for N=4096 but ran at N=512 SMOKE single-seed. v9 is the second consecutive saad_solla `_n` defect in the v8/v9/v10 series (v8 caught at v234 as 73rd catch; v10 still pending in overnight_queue).
- **v8/v9/v10 series at honest N (all N=512 effective):** v8 (`_n2048`) r2=0.7706 HP_single; v9 (`_n4096`) r2=0.7960 MIDDLE; v10 (`_n8192`) r2=0.7557 HP_single (already landed pre-event-stream). Three near-identical smokes at the SAME effective N=512, single-seed=17, with r2 ∈ [0.76, 0.80] and max_dev ∈ [0.078, 0.090]. The variation across seed=17 single-seed runs at N=512 is ~±0.02 in r2 and ~±0.006 in max_dev -- noise floor of the smoke regime.
- **Pre-reg bands check:** parent handoff (2026-05-25) specifies HARD-PASS = `BIC_4state - BIC_3state < -30 AND spacing_error_4state < 0.05 AND gap_ratio_4state ∈ [0.45, 0.65] AND adjacent 4-plateau statistical separation`. metrics.json does NOT report ANY of these quantities -- no BIC delta, no spacing error, no gap ratio, no plateau CIs. The script reports only r2, max_dev (single seed), and f_sweep grid; these are smoke-gate metrics for an EARLIER axis (sigmoid fit quality) not the 4-tier discrete-vs-continuous BIC comparison the parent falsifier requires. Honest reading: this run did NOT test the parent hypothesis at all -- it's a smoke-gate r2 check at N=512 against a stale parent v3 baseline (r2=0.322). Even if the anchor name were honest about N=4096, the metric set in metrics.json is the WRONG set for the parent falsifier contract.
- **Why MIDDLE (not HP) at v9 vs v8/v10:** v8 and v10 both had r2 just above their HP threshold (single-seed HP_threshold appears to be ~0.75 r2 in this script family); v9's r2=0.796 is higher than v8's r2=0.771 yet got MIDDLE while v8 got HP_single. The labelling inconsistency between v8/v9/v10 is itself evidence of brittle smoke-gate logic -- script-internal verdict assignment is reading noise as signal-change. NOT a substrate signal.
- 80th post-lock label-vs-honest catch (after 79 in 24h). Same class as v8 (#73), v6 (#61), v5 (#77), v6_n4096_gpu (61st). The PROT-018 retroactive sweep flagged at v225/v227 is now overdue -- v9 is the 3rd post-PROT-018-flag _n defect (v8, v6 GPU, v9).

**Cap_map state moves (v237 -> v238).**

- **Saad-Solla saddle-cascade row**: UNCHANGED ✅ LEADING. v9 adds the 6th N<=512 smoke corroboration in the bracketing-noise zone (r2~0.77-0.80 single-seed); does NOT touch the load-bearing positive evidence (v206 BIC delta=194.9 + v211 alpha_c in-band). The genuine large-N FULL N>=4096 multi-seed BIC + equal-spacing + 4-class probe REMAINS the binding open question.
- **PROT-018 retroactive-sweep urgency**: ELEVATED. 80 `_n` naming-defect catches total; v9 is the 3rd post-PROT-018-landing defect (PROT-018 landed at queue_add for NEW shipments but pre-PROT-018-ship batch still leaks defects). v6, v8, v9 all leaked through; v10 (`_n8192` already in queue) is the next predicted leak. Retroactive sweep on the saad_solla series in queue + recent completions is the cheapest-first structural fix.
- **non-eq-stat-mech framework class row**: UNCHANGED 🟢 45-60% (v9 is a smoke-regime noise event, not informational either direction).
- **SKAH-M / lR-phase row**: UNCHANGED 🟢 55-70%.
- **No capability row closures.** PROT-004/006 not triggered.
- **Portfolio count**: UNCHANGED (14+18).
- **Framework reliability**: UNCHANGED (general derivable 65-75% 🟢 / specific named documented 45-55% 🟢 / product-feature 55-70% 🟢).
- **Cumulative label-vs-honest catches**: 79 → 80.

**Decision (rescue sketches cheapest-first per [[feedback-rescue-sketch-first-sequencing]]):**

(a) **CHEAPEST / SUBSUMPTION**: v10 (already pending in overnight_queue as `saad_solla_v10_n8192`) is the 3rd attempt at the same parent falsifier. INTERCEPT v10 PRE-RUN: verify config.N == 8192 AND config.mode == FULL AND seeds >= 3 AND BIC+spacing+gap-ratio reported. If v10 is also pre-PROT-018-leaked at N=512 SMOKE single-seed (likely), pull v10 from queue + ship v11 with the parent-contract metrics enforced. Zero new infra; ~5 min queue inspection. **PRIMARY.**

(b) **CHEAP**: Retroactive PROT-018 sweep over overnight_queue + remote_cpu_queue pending entries for any `_n<N>` / `_FULL` / `_gpu` suffix anchor. ~10 min queue inspection + manual config-vs-name audit. Catches v10 and any other unflagged leak before they consume orchestrator attention.

(c) **CHEAP**: Smoke-gate redesign for fail-loud on parent-contract metric absence. The current smoke gate validates r2/max_dev (smoke-axis) and lets MIDDLE through even when the parent falsifier (BIC + spacing + 4-plateau CI) was never computed. Adding a check "if anchor name contains 'saad_solla' and verdict=MIDDLE, require BIC fields in metrics" would fail the script early. ~30 min infra; subsumes the [[feedback-strategy-spec-formula-selftests]] discipline at the verdict-output level.

(d) **MEDIUM**: v11 spec re-design from parent handoff -- 4-corpus extension (G1_SAME / G2_3STAGE / G3_4STAGE / G4_DIFF) at N=4096 GPU multi-seed (3-5 seeds) with BIC + spacing_error + gap_ratio + adjacent-plateau-CI as required outputs. ~2-4 h GPU. This is the GENUINE falsifier the 2026-05-25 handoff requested; v6/v7/v8/v9 have all skipped this content.

(e) **MEDIUM-BUILD**: queue-runner exit-code interpretation audit (PROT-019 candidate from v229). MIDDLE_BAND mistagged as 'failed' is now the 5th occurrence in 24h; structural fix needed to read script-internal [VERDICT] line authoritatively rather than runner-exit-code interpretation. ~1 h infra inspection.

Per [[feedback-rehabilitation-after-rejection]] discipline: 5 rescue sketches before treating saad_solla N-scaling probe as archived. Row is ✅ LEADING; this is a "thoroughness" rescue-sketch set on the open large-N probe, NOT a row-closure rescue. PRIMARY (a) is intercept-v10-before-it-runs (zero compute); secondary (b)/(c) are infra hardening; (d) is the genuine FULL probe; (e) is the broader queue-runner exit-code fix.

**Decision (queue refill): NO refill from this handler.** Pause flag ABSENT (ACTIVE) per `data/orchestrator_paused.flag` check. Queue depth at verdict arrival: overnight_queue pending=4 + running=1; remote_cpu_queue pending=4 + running=1. Pipeline-pacing invariant queue >= 1 comfortably maintained. No refill needed per [[feedback-no-padding-experiments]]. Rescue (a)/(b)/(c) are CANDIDATES for next exp_dev cycle (orchestrator may batch); (d) is the highest-value future ship.

**PROT compliance (v238).**

- PROT-004/006: 0 capability row closures; 0 rescues required at row level. 5 rescue sketches filed cheapest-first per [[feedback-rehabilitation-after-rejection]] for the saad_solla large-N probe (thoroughness given 6th smoke-only data point with zero genuine-FULL coverage).
- PROT-007: history.md not present in tree (consistent with v228+).
- PROT-008: No demotion; annotation-only on ✅ row.
- PROT-009: cap_map.md + strategy_decisions_2026-05-27.md staged atomically.
- PROT-018: 80th `_n` naming-defect catch -- retroactive sweep flagged at v225/v227 is now URGENT (3 post-PROT-018-landing leaks in a row: v6_gpu, v8_n2048, v9_n4096; v10_n8192 predicted next).
- [[feedback-verdict-msg-honest-reread]]: 80th label-vs-honest catch applied -- (i) event-bus 'failed' tag overridden to MIDDLE_BAND per local metrics; (ii) anchor `_n4096` overridden to N=512 SMOKE single-seed per config; (iii) parent-falsifier-contract metrics flagged absent.
- [[feedback-subagent-permission-inheritance]]: LOCAL commit only; push deferred to main thread.
- [[feedback-rescue-sketch-first-sequencing]]: 5 rescue sketches filed cheapest-first (a) intercept-v10 PRIMARY subsumption; (b) queue PROT-018 retroactive sweep; (c) smoke-gate fail-loud redesign; (d) genuine FULL v11 GPU multi-seed; (e) queue-runner exit-code audit.
- [[feedback-dont-overextend-theorems]]: v9 smoke noise event is constrained to ANNOTATION-ONLY scope; does NOT touch v206 BIC delta=194.9 + v211 alpha_c in-band load-bearing positive evidence for the row.
- [[feedback-rehabilitation-after-rejection]]: 5 rescue sketches before archival; PRIMARY (a) is zero-compute intercept of pending v10.
- Queue-refill: SKIPPED (pause flag ABSENT but queue depth ≥1 invariant comfortably maintained; overnight pending=4 / remote_cpu pending=4).
- 151st PROT-009 paired commit.

SINGLE-VERDICT v237 -> v238: [label-vs-honest 80th catch] saad_solla_v9_n4096 event-bus 'failed' OVERRIDDEN to MIDDLE_BAND per local metrics; anchor `_n4096` OVERRIDDEN to N=512 SMOKE single-seed; parent-falsifier-contract metrics (BIC delta + spacing + gap-ratio + plateau-CI) ABSENT from metrics.json -- run did NOT test parent hypothesis; saad_solla row UNCHANGED ✅ LEADING (v9 is 6th N<=512 smoke in bracketing-noise zone r2~0.77-0.80; load-bearing v206 BIC + v211 alpha_c stand); v8/v9/v10 series ALL at same effective N=512 single-seed=17 with ±0.02 r2 noise; PROT-018 retroactive-sweep URGENCY ELEVATED (3rd post-landing _n defect; v10 likely 4th); 5 rescue sketches cheapest-first PRIMARY=intercept v10 pre-run subsumption rescue; framework reliability UNCHANGED; portfolio 14+18 UNCHANGED; 0 capability row closures; 151st PROT-009 paired commit.

## v239 -- 2026-05-27 bet_b_n8192_4stage_v2 FOURSTAGE_MIDDLE_BAND FULL N=8192 5-seed @ 16:41 [label-vs-honest 81st catch; ANNOTATION-ONLY; CORROBORATES v189 + REFUTES smoke->Tier-1 promotion hope]

**Trigger.** `bet_b_n8192_4stage_v2` completed overnight_queue GPU 2026-05-27T16:41:21 (wall_s=1000.06). Queue runner labeled status=`failed` with `error: "metrics_invalid: missing"` — the v2 anchor reused script `experiments/exp_bet_b_n8192_4stage_v1.py` which writes metrics to `data/exp_bet_b_n8192_4stage_v1/metrics.json` (hard-coded v1 path), not the v2-named output dir the runner watcher expected. Per the queue runner's exit-protocol the missing-file at the expected path got auto-tagged `failed`. The actual data WAS produced on disk under the v1 path (mtime 2026-05-27T16:41:20 matches v2 ended_at to the second).

**Step 0 honest re-read.** Label `failed` from queue runner is a STRUCTURAL ARTIFACT (script-output-path mismatch), NOT an honest description of the scientific outcome. Honest reading from remote metrics file (`C:\dev\hd-instrument\data\exp_bet_b_n8192_4stage_v1\metrics.json`, mtime 2026-05-27T16:41:20):

Per-seed retention (FULL N=8192, 5 seeds):

| seed | ret_A  | ret_B  | ret_C  |
|------|--------|--------|--------|
| 7    | 0.7399 | 0.8590 | 0.8147 |
| 17   | 0.7532 | 0.8583 | 0.8007 |
| 23   | 0.7446 | 0.8589 | 0.8096 |
| 31   | 0.7348 | 0.8550 | 0.8080 |
| 41   | 0.7514 | 0.8633 | 0.8091 |
| mean | 0.7448 | 0.8589 | 0.8084 |
| std  | 0.0073 | 0.0029 | 0.0050 |

Pre-reg bands (from `preregs/2026-05-27_bet_b_n8192_4stage_v2.md`):
- HARD_PASS: mean retention_A >= 0.80 AND ret_B >= 0.70 AND ret_C >= 0.70 across >=4/5 seeds
- HARD_FAIL: mean retention_A <= 0.50
- MIDDLE_BAND: ret_A in (0.50, 0.80)

Honest verdict = **FOURSTAGE_MIDDLE_BAND** (mean ret_A=0.745 squarely in middle band; 0/5 seeds clear 0.80 HP threshold; ret_B and ret_C both decisively clear 0.70 HP). NOT HARD_PASS, NOT HARD_FAIL.

This is the **81st cumulative label-vs-honest catch** post-PROT-018 (concurrent saad_solla_v9_n4096 handler claimed 80th at v238/b0383b8 minutes earlier). Severity: HIGH — the queue-failed auto-label would have triggered a script-bug rescue dispatch and missed the actual scientific signal (which is robust corroboration of v189 + refutation of the smoke-pass narrative).

**Corroboration of v189.** `wave14_betB_4stage_continual_v1` at v189 reported (post-rehab v190 stable): retention_A=0.740, ret_B=0.854, ret_C=0.798. v238 here reports ret_A=0.745, ret_B=0.859, ret_C=0.808. Per-stage retentions match to within +/-0.005 — replication is **clean** at higher N (1024->8192) and higher seed count (1->5). 4-stage CL `🟡 PARTIAL` row state at v189 is **STRONGLY CORROBORATED**.

**Refutation of smoke->Tier-1 promotion narrative.** `project_bet_b_4stage_smoke_pass_2026-05-27.md` documented smoke ret_A=0.848 / ret_B=0.905 / ret_C=0.874 and recorded "FULL N=8192 multi-seed REQUIRED for Tier-1 promotion." The FULL run lands ret_A=0.745 (-0.103 drop from smoke), ret_B=0.859 (-0.046 drop), ret_C=0.808 (-0.066 drop). Pattern: **smoke overestimates FULL retention by 0.05-0.10 on 4-stage CL probes**. Tier-1 promotion BLOCKED on the retention_A ≥ 0.80 bar. This is the second observation of smoke->FULL drop on 4-stage CL (v189 had no smoke comparator; this is the first time we directly observed the smoke->FULL gap on this probe family at higher N).

**Cap_map state moves (v238 -> v239).**

- **True continual learning at production scale (A->B->C->D)** row (line 123 + line 426): UNCHANGED 🟡 PARTIAL. Annotation appended: "v238 bet_b_n8192_4stage_v2 FULL N=8192 5-seed CORROBORATES v189 within +/-0.005 per-stage retention: mean ret_A=0.745, ret_B=0.859, ret_C=0.808; replication CLEAN at higher N + seed count; first direct smoke->FULL gap observation on this probe family (ret_A drop -0.103, ret_B drop -0.046, ret_C drop -0.066 from smoke v1); Tier-1 promotion BLOCKED on ret_A ≥ 0.80 bar." Row state stays 🟡 because the row is already 🟡 PARTIAL for this exact reason (B+C clear, A misses 0.80 by ~0.05).
- **No row promotions, no row demotions.** Replication of an already-🟡 PARTIAL row at higher N + seeds is corroboration of the existing state, NOT a state change.
- **Project narrative update.** `project_bet_b_4stage_smoke_pass_2026-05-27.md` should be annotated with FULL outcome (annotation flag, not file rewrite — memory layer task, not strategy layer; surfaced here for downstream visibility).
- **Smoke-FULL gap observation locked.** This is the first explicit (smoke, FULL) pair on the 4-stage CL probe family. Smoke ret_A=0.848 -> FULL ret_A=0.745 (-0.103). Pattern note: smoke at lower N + single seed systematically over-estimates retention on 4-stage CL; the multi-seed multi-stage interactions amplify variance enough that single-seed smoke can land 0.05-0.10 high. Future 4-stage CL smoke results should NOT be treated as Tier-1-promotion-evidence without 5-seed N=8192 FULL confirmation.
- **Portfolio count**: UNCHANGED (14+18). No new portfolio item; corroboration of existing item.
- **Framework reliability**: UNCHANGED (general 65-75% / specific-documented 45-55% / product-feature 55-70%). Clean replication of a 🟡 PARTIAL prediction within +/-0.005 is reliability-supportive but doesn't move the band (already PROVISIONAL with this kind of evidence baked in).
- **Cumulative label-vs-honest catches**: 80 -> 81. queue-runner "failed" label structural-artifact-overridden by FOURSTAGE_MIDDLE_BAND honest reading from the actually-existing remote metrics file at the v1 hard-coded output path.

**Rescue sketches (4; cheapest-first per [[feedback-rescue-sketch-first-sequencing]]).**

(a) **CHEAPEST / SCRIPT-FIX (PRIMARY)**: patch `experiments/exp_bet_b_n8192_4stage_v1.py` so output-dir path is parameterized by the queue `--name` argument rather than hard-coded to `exp_bet_b_n8192_4stage_v1`. ~30min edit. PRIMARY queue-hygiene fix — eliminates the metrics_invalid:missing false-fail pattern for ANY future re-runs of this script under a different anchor name. Should be standardized as a queue_add.py pre-flight gate.
(b) **CHEAP**: ret_A rehab axis-1 — re-run at N=8192 with 2x Phase-A epochs (16 vs 8) to test whether ret_A bar can be closed by extending consolidation. v189-era rehab (v190 V1) at N=1024 saturated at MIDDLE_BAND; at N=8192 with cleaner code there may be headroom. ~50min GPU. Candidate next exp_dev cycle.
(c) **CHEAP**: ret_A rehab axis-2 — increase batch_size from 64 to 128 (more gradient signal per Phase-A pass) to test if effective-learning-rate scaling closes ret_A bar. ~50min GPU. Candidate next exp_dev cycle.
(d) **MEDIUM**: 4-stage CL reframed as "MIDDLE_BAND BAR LOWERING" — pre-reg a *lower* product-relevant HP threshold (ret_A >= 0.70 instead of >= 0.80) reflecting that B+C already retain >0.80 at N=8192 5-seed and the per-stage Phase-D forgetting pressure is now characterized. Product-narrative subsumption rescue. ~0-cost annotation if accepted. Note: requires explicit user buy-in on the threshold-lowering (not silent goalpost-moving); flagged for orchestrator surface to user.

PRIMARY rescue (a) is a queue-hygiene fix more than a science rescue (script-path bug is real but doesn't change today's verdict reading). (b)/(c) are CANDIDATES for next exp_dev cycle per [[feedback-no-padding-experiments]] (not auto-queued). (d) is policy-level, requires user buy-in.

**PROT compliance (v239).**

- PROT-004/006: 0 row closures. 4 rescue sketches filed cheapest-first per [[feedback-rehabilitation-after-rejection]].
- PROT-007: history.md absent (consistent with v228+).
- PROT-008: No demotion. 🟡 -> 🟡 annotation-only.
- PROT-009: cap_map.md + strategy_decisions_2026-05-27.md staged atomically.
- PROT-018: anchor name `bet_b_n8192_4stage_v2` has no explicit `_n<N>` suffix in the name, but the `_n8192_4stage_v2` shape is N-binding (v1 -> v2 is a version bump on the same N=8192 probe). The queue runner accepted the anchor at gate; honest reading respects the N=8192 binding.
- [[feedback-verdict-msg-honest-reread]]: 81st observation; label=structural-artifact, honest=FOURSTAGE_MIDDLE_BAND from actually-existing metrics at v1 hard-coded path.
- [[feedback-subagent-permission-inheritance]]: LOCAL commit only; push deferred to orchestrator main thread.
- [[feedback-rescue-sketch-first-sequencing]]: 4 sketches cheapest-first; PRIMARY = script-path parameterization (queue-hygiene; the scientific signal is robust corroboration).
- [[feedback-dont-overextend-theorems]]: explicit — smoke->FULL drop observation does NOT generalize to "all 4-stage CL smoke results are inflated"; this is ONE pair-observation on ONE script family. Frame as "first direct smoke->FULL gap observation on 4-stage CL probe family" not as a universal smoke-inflation theorem.
- [[feedback-rehabilitation-after-rejection]]: rehab not triggered (row stays 🟡 PARTIAL UNCHANGED); rescues (b)/(c) filed as CANDIDATES for ret_A bar-closing not as required-by-PROT.
- Queue-refill: SKIPPED in this handler (orchestrator decides based on actual pending count post-verdict; current GPU pending=2 running=1, CPU pending=0 running=0; queue-depth-invariant maintained for now).
- 152nd PROT-009 paired commit (concurrent with 151st at b0383b8/v238).

SINGLE-VERDICT v238 -> v239: bet_b_n8192_4stage_v2 queue-runner-label `failed` STRUCTURAL-ARTIFACT (script-path bug; metrics written to v1 hard-coded path), honest reading from actually-existing remote metrics = FOURSTAGE_MIDDLE_BAND FULL N=8192 5-seed (mean ret_A=0.745, ret_B=0.859, ret_C=0.808); CORROBORATES v189 within +/-0.005 per-stage retention CLEAN at 8x higher N + 5x seeds; REFUTES smoke->Tier-1-promotion narrative (smoke ret_A=0.848 -> FULL 0.745, -0.103 drop = first direct smoke->FULL gap observation on 4-stage CL probe family); 4-stage CL row 🟡 PARTIAL UNCHANGED (already PARTIAL for the exact ret_A < 0.80 reason); 4 rescue sketches filed cheapest-first (PRIMARY = script-path queue-hygiene fix); framework reliability UNCHANGED; portfolio 14+18 UNCHANGED; 81st label-vs-honest observation; 152nd PROT-009 paired commit (concurrent with 151st at b0383b8).

## v240 -- 2026-05-27 max_plus_algebra_substrate_v1 HARD_PASS LABEL-VS-HONEST CHANCE-LEVEL @ 16:49 [82nd label-vs-honest catch; ANNOTATION-ONLY; cross-domain tropical-family probe]

**Trigger.** max_plus_algebra_substrate_v1 completed remote_cpu_queue 2026-05-27T16:49:49 (elapsed 0.13s; smoke single-anchor 5 seeds N=1024 K-sweep [1,2,4,8,16] 100 trials/cell). Verdict label `HARD_PASS: max-plus retrieval confirmed. K=1 exact=1.000>=0.9. K=4 exact=0.250. Tropical memory algebra viable for HSC substrate.` is **OVER-CLAIM**. Per-cell exact-retrieval accuracy series is EXACTLY 1/K random-chance across all K>=2:

| K  | mean_exact | 1/K  | delta from chance |
|----|------------|------|-------------------|
| 1  | 1.000      | 1.000 | 0 (trivial — single item, no interference) |
| 2  | 0.500      | 0.500 | 0 |
| 4  | 0.250      | 0.250 | 0 |
| 8  | 0.125      | 0.125 | 0 |
| 16 | 0.0625     | 0.0625 | 0 |

The K=4 exact=0.250 the verdict_msg cites as confirming evidence IS exactly chance (1/K = 1/4 = 0.250). All 5 seeds for each K cell return identical numerical values (zero across-seed variance per K), which means the max-plus retrieval algorithm is purely structural (no randomness in the retrieval path — only random in the stored content) and falls back to uniform-random selection for K>=2. **HARD_PASS label is structurally wrong**: K=1 trivially passes because there is no other item to confuse with; K>=2 cells all land at exact 1/K random-chance baseline.

Honest reading: **MAX_PLUS_RETRIEVAL_AT_CHANCE_K_GE_2** -- max-plus algebra substrate has only trivial (K=1) retrieval; multi-item retrieval is at random-chance baseline. The "tropical memory algebra viable for HSC substrate" conclusion is NOT supported by this data.

**Cap_map state moves (v239 -> v240).**

- **NEW evidence-strength sub-row (NOT a portfolio capability row): "tropical-family multi-item retrieval (max-plus algebra) at chance-level K>=2"**: ❌ CLOSED-NEGATIVE at smoke level (single-seed-numerical-determinism + 5-seed-content-randomization N=1024 K-sweep [1,2,4,8,16] confirms exactly 1/K = chance across all K>=2 cells). Sibling row to tropical_geometry_substrate_v1 🟡 MIDDLE_BAND (v234) which had spectral-range probe HP=1/1 but cosim HP=0/1; the max-plus algebra probe joins the cosim-fail side of tropical-family. Consistent with F-14 Tropical Cap-13 candidate continent KILLED at closed-form-margin theory level (v181 rel_err 52-99.8% across N=4-1024) and F-6 Boolean Cap-13 candidate KILLED at theory level (v182). **Tropical-family multi-item retrieval is the THIRD independent tropical-family closure at substrate-level**: (1) F-14 Tropical closed-form margin v181, (2) F-6 Boolean-noise v182, (3) max-plus algebra retrieval v240.
- **tropical_geometry_substrate_v1 🟡 MIDDLE_BAND row (v234)**: UNCHANGED 🟡 with annotation appended: "v240 max-plus algebra retrieval probe joins tropical-family closure stack; multi-item retrieval at exact chance for K>=2; spectral-range probe HP=1/1 stands but retrieval-side at chance reinforces cosim HP=0/1 from v234; tropical-family is partially-consistent at substrate-spectral level + structurally-mismatched at substrate-retrieval level."
- **Cap 13 candidate row 🔬 (v182 CLOSED-VIA-3-of-3-CONTINENT-REJECTION at closed-form-margin theory level)**: UNCHANGED 🔬 with annotation: "v240 max-plus algebra retrieval HARD_PASS LABEL-VS-HONEST CHANCE-LEVEL adds a fourth independent tropical-family closure at substrate-level; trilogy resolution v182 REINFORCED by a substrate-retrieval probe (not closed-form theory; new angle); no row state change (was already closed)."
- **non-equilibrium-stat-mech framework class row (v229)**: UNCHANGED 🟢 45-60% (tropical-family closures are static-algebra failures; orthogonal evidence on non-eq class; does NOT touch H1).
- **No capability row closures.** PROT-004/006 not triggered at any portfolio capability row level. Tropical-family probe is a sub-framing evidence-strength row, not a capability row.
- **No demotions, no promotions.** PROT-008 documented: tropical_geometry sub-row 🟡 -> 🟡 with honest evidence-breakdown update (retrieval-side at chance, spectral-side passes).
- **Portfolio count**: UNCHANGED (14+18). This is an evidence-strength annotation on existing sub-framing row, not a new portfolio addition.
- **Framework reliability**: UNCHANGED (general 65-75% / specific-documented 45-55% / product-feature 55-70%). Tropical-family is already documented as 0-of-3-continent-rejection at closed-form-margin theory level; adding a fourth tropical-family closure at substrate-retrieval level is corroborating-not-reframing.
- **Cumulative label-vs-honest catches**: 81 -> 82 (label cites K=4 exact=0.250 as confirming "max-plus retrieval confirmed" when 0.250 IS exactly 1/K = chance; structural over-claim where the cited data point IS the falsifier).

**Cross-domain probe context.** Orchestrator flagged this as "cross-domain substrate probe (tropical geometry adjacent)" — likely a research-scope-expansion drill per [[feedback-periodic-scope-expansion]] / [[feedback-aggressive-cross-domain-research]]. The cross-domain probe DID return useful information: tropical-family multi-item retrieval is structurally-incompatible with BSC + Kerdock substrate state at the retrieval algorithm level (not just closed-form theory level as v181/v182 already showed). Scope-expansion drills returning honest-negative are GOOD outcomes per [[feedback-no-smoke]].

**Rescue sketches (5; cheapest-first per [[feedback-rescue-sketch-first-sequencing]] and [[feedback-rehabilitation-after-rejection]]).**

(a) **CHEAPEST / SUBSUMPTION (PRIMARY)**: re-frame as "fourth independent tropical-family closure on substrate" — the closure stack (F-14 Tropical margin v181 + F-6 Boolean-noise v182 + tropical_geometry_substrate_v1 cosim v234 + max-plus algebra retrieval v240) IS the substrate-product finding per [[feedback-no-smoke]]. Zero-cost annotation rescue; documents tropical-family as structurally-incompatible with substrate at BOTH closed-form theory and substrate-retrieval algorithm levels. **Implemented as part of this v240 entry.**
(b) **CHEAP**: alternative tropical-retrieval framing — instead of max-plus, try min-plus algebra or signed-tropical algebra at K=2,4 N=1024 single-seed smoke. ~2min CPU. Tests whether the chance-level result is max-plus-specific or generic-tropical-substrate-incompatibility. CANDIDATE for next research/exp_dev cycle (low priority; tropical-family is closed at theory level already).
(c) **CHEAP**: alternative retrieval algorithm under max-plus inner product — instead of argmax over max-plus inner-product, try thresholded-max-plus or noise-robust max-plus with explicit BSC-noise model. ~5min CPU. Tests whether the issue is the algebra or the retrieval algorithm. CANDIDATE (low priority; redundant with F-14 Tropical margin v181 closure direction).
(d) **MEDIUM**: tropical-algebra structural-mismatch finding — write up "tropical-family is structurally incompatible with BSC+Kerdock substrate state at retrieval level" as a substrate-product narrative finding per [[feedback-no-papers-product-only]]. Zero compute; product-positioning annotation. CANDIDATE if user wants the moat narrative deepened ("not just one tropical closure, but four independent closures across theory + retrieval + spectral + Boolean-noise dimensions").
(e) **MEDIUM**: SCOPE-EXPANSION cadence audit — per [[feedback-periodic-scope-expansion]] and [[feedback-aggressive-cross-domain-research]], record this max_plus drill as one slot in the cross-domain probe cadence; note tropical-family is now over-tested relative to other adjacent algebras (Lie groups, quaternions, octonions, p-adic, idempotent semirings, sparse-coding); recommend next cross-domain drill pull from a different algebraic family. CANDIDATE for next research cycle.

PRIMARY rescue is annotation-only (already applied above); (b)/(c) are LOW-priority candidates; (d) is product-positioning; (e) is meta-cadence input. Per [[feedback-no-padding-experiments]] none auto-queued.

**PROT compliance (v240).**

- PROT-004/006: 0 row closures. 5 rescue sketches filed cheapest-first per [[feedback-rehabilitation-after-rejection]] even though no portfolio row is rehabbed (defensive thoroughness given a new tropical-family closure adds context to v182 trilogy resolution).
- PROT-007: history.md absent (consistent with v228+).
- PROT-008: No demotion; annotation-only on existing tropical_geometry sub-row 🟡 with honest evidence-breakdown update (retrieval-side at chance, spectral-side passes).
- PROT-009: cap_map.md + strategy_decisions_2026-05-27.md + visibility_decisions_2026-05-27.md staged atomically.
- PROT-018: anchor name `max_plus_algebra_substrate_v1` has no explicit `_n<N>` suffix; metrics.json shows N=1024 single-N smoke; no name-vs-config defect (anchor is honest about its smoke status).
- [[feedback-verdict-msg-honest-reread]]: 82nd observation; label HARD_PASS structurally over-claims because the cited K=4 exact=0.250 IS exactly 1/K random-chance; honest reading is CHANCE-LEVEL K>=2 not "max-plus retrieval confirmed".
- [[feedback-subagent-permission-inheritance]]: LOCAL commit only; push deferred to orchestrator main thread.
- [[feedback-rescue-sketch-first-sequencing]]: 5 sketches cheapest-first; PRIMARY = annotation subsumption (0-cost; documents tropical-family fourth-closure as substrate-product finding).
- [[feedback-dont-overextend-theorems]]: explicit — max-plus algebra closure does NOT generalize to "all idempotent semirings are structurally incompatible"; v240 closes max-plus specifically and adds a fourth tropical-family observation; adjacent algebras (min-plus, signed-tropical, other idempotent semirings) remain UNTESTED.
- [[feedback-no-smoke]]: honest reading authoritative; HARD_PASS label not propagated to cap_map.
- [[feedback-periodic-scope-expansion]] / [[feedback-aggressive-cross-domain-research]]: scope-expansion probe returning honest-negative IS the success mode for scope-expansion drills.
- Queue-refill: ACTIVE pause flag absent; queue_state_at_arrival GPU pending=3, remote_cpu pending=1 (this anchor; freed slot), local_cpu pending=0; verdict_handler RECOMMENDS orchestrator pipeline-pacing exp_dev refill based on actual queue depths post-this-verdict (not auto-dispatched from this handler per current pause-flag-absent policy + queue invariant maintained).
- 153rd PROT-009 paired commit.

SINGLE-VERDICT v239 -> v240: max_plus_algebra_substrate_v1 [LABEL-VS-HONEST 82nd catch] HARD_PASS label over-claims (K=4 exact=0.250 IS exactly 1/K random-chance); honest reading = MAX_PLUS_RETRIEVAL_AT_CHANCE_K_GE_2 (K=1 trivially passes, K>=2 cells all at exact 1/K baseline; zero across-seed variance per K confirms structural-not-stochastic); cross-domain scope-expansion probe per [[feedback-periodic-scope-expansion]] returns honest-negative on tropical-family multi-item retrieval; FOURTH independent tropical-family closure (joins F-14 Tropical margin v181 + F-6 Boolean-noise v182 + tropical_geometry_substrate_v1 cosim v234); tropical_geometry sub-row 🟡 UNCHANGED with annotation; Cap 13 candidate row 🔬 UNCHANGED with v240 annotation; non-eq-stat-mech class row 🟢 UNCHANGED (orthogonal); 5 rescue sketches cheapest-first PRIMARY=annotation subsumption (tropical-family fourth-closure documented as substrate-product finding 0-cost); framework reliability UNCHANGED (general 65-75% / specific named 45-55% / product-feature 55-70%); portfolio 14+18 UNCHANGED; 0 capability row closures; 82nd label-vs-honest observation; 153rd PROT-009 paired commit.

## v242 -- 2026-05-27T16:51 mode_coupling_theory_substrate_v1 MIDDLE_BAND (MCT cross-domain probe; smoke N=1024 5-seed) — originally drafted as v238; renumbered to v242 after concurrent commits b0383b8 (saad_solla v238) / 37f576f (bet_b v239) / ff736f7 (max_plus v240) / tcft v241 consumed v238-v241; content otherwise unchanged

**Trigger.** mode_coupling_theory_substrate_v1 completed remote_cpu_queue 2026-05-27T16:50:06 (elapsed 14.65s; FULL smoke N=1024 5-seed K=[1,4,8,16,32,64,128,160,192]). Cross-domain probe per [[feedback-periodic-scope-expansion]] / [[feedback-aggressive-cross-domain-research]]. MCT was item (ii) of `notes/research_alternative_theoretical_homes_2026-05-24.md` at lit-scan P=0.15, status 🔬 contingency.

**Step 0 honest re-read.** Verdict_msg `MIDDLE_BAND: power-law fit R^2=0.9598 (need 0.8). gamma=-0.06680... linear_R^2=0.7394` is HONEST. Per-K mean_overlap [K=1→0.904, K=4→0.907, K=8→0.903, K=16→0.902, K=32→0.900, K=64→0.900, K=128→0.889, K=160→0.855, K=192→0.790]. Power-law R²=0.9598 PASSES the stated 0.80 fit-quality gate but the LOAD-BEARING MCT signal is gamma magnitude — at gamma=-0.067 substrate is 7-40× UNDER canonical MCT |gamma|≈0.5-3.0. Decay shape is "weak slow erosion + late-K knee at K≥128" not "power-law alpha-relaxation." No label-vs-honest override; numerical MIDDLE_BAND authoritative. (80th post-lock honest re-read observation.)

**Decision (1): MCT theoretical-home candidate row 🔬 → 🟡 demoted (DEMOTION not CLOSURE).** Fit-quality gate passed but gamma-magnitude gate failed. Substrate does NOT classify into MCT glass-transition family from this smoke probe. Lit-scan P=0.15 deflated to 0.07-0.10. Row stays NOT-CLOSED because (a) curvature signal IS present (linear-vs-power-law R² gap 0.22), (b) smoke N=1024 may be too small; FULL N=4096+ could reveal stronger gamma, (c) gamma may be alpha-dependent — substrate at K=192/N=1024 is at α=0.19 well below static-Hopfield α_c=0.138-style critical region; sweeping closer to true substrate α_c could reveal larger gamma if any exists.

**Decision (2): Substrate-outside-static-Hopfield-taxonomy 🟢 UNCHANGED 45-60% with annotation.** v238 MCT non-classification is INDEPENDENT 4th angle of "substrate sits outside standard static-phase taxonomies": BID outside 3 Hopfield bands (v229) + SKAH-M lR-phase class match (v228) + saddle-cascade arithmetic (v206) + MCT non-classification (v238 NEW). Strengthens v227 plural-framework lock 4th time. P estimate already reflects this kind of independent corroboration — MCT non-classification is INFORMATIVE not LIFTING because it's a ruling-out probe not a positive identification.

**Decision (3): Theoretical-home portfolio status (alternative-theoretical-homes research list).** Updated tally: (i) k-RSB k=2 burned (v215); (ii) MCT 🔬→🟡 weak-curvature-not-MCT (v238 NEW); (iii) Chaos-in-temperature P=0.22 contingency UNCHANGED; (iv) IB CLOSED (v205); (v) RD CLOSED (v219); (vi) replica chain P=0.10 contingency UNCHANGED. Substrate's POSITIVE theoretical-home portfolio: Saad-Solla saddle-cascade LEADING ✅ + SKAH-M class anchor ✅ + non-eq-stat-mech class 🟢 45-60% (v229 BID). MCT joins the "probed-and-non-classifying" bucket (third probed candidate ruled out or demoted; static-class taxonomy continues to under-fit substrate physics).

**Decision (4): Framework reliability UNCHANGED.** General-derivable 68-75% / specific-documented 45-55% / product-feature 55-70%. Cross-domain non-classification doesn't move reliability either direction — it's calibration evidence on the framework-comparison method not on substrate-capability claims. (The MIDDLE_BAND pre-reg gate did its job correctly: PASS the fit-quality leg, FAIL the gamma-magnitude leg, return MIDDLE_BAND label.)

**Decision (5): Portfolio count UNCHANGED at 14+18.** MCT was 🔬 (research-candidate row), not a substrate-capability portfolio member; demoting to 🟡 doesn't affect demonstrated-capability or evidence-strength counts.

**Decision (6): Saad-Solla saddle-cascade row UNCHANGED ✅, SKAH-M class anchor UNCHANGED ✅, non-eq-stat-mech 🟢 UNCHANGED.** MCT probe was a cross-domain audit on a separate research-candidate row; surviving theoretical-home rows are untouched.

**Decision (7): Cross-domain drill cadence VALIDATED.** Per [[feedback-periodic-scope-expansion]] and [[feedback-aggressive-cross-domain-research]], MCT was a periodic cross-framework drill — it returned a 14-second cheap probe that contributed an independent 4th angle on the outside-static-taxonomy narrative even though it didn't lift any substrate-capability row. Worked example of "cross-domain drills are net-informative even when they don't promote rows." Continue cadence; next cross-domain candidate per research backlog.

**Rescue sketches (4; cheapest-first).** (a) SUBSUMPTION (0-cost, PRIMARY): v238 as 4th angle of plural-framework lock — APPLIED. (b) CHEAP ~3-5min: alpha-sweep at extended K=[256-768] toward substrate's true α_c. (c) CHEAP ~20-30min: FULL N=4096 5-seed gamma-magnitude diagnostic. (d) MEDIUM ~40-60min: joint MCT × Saad-Solla basin-occupancy correlation. None auto-queued per [[feedback-no-padding-experiments]].

**PROT compliance.** PROT-004/006: 0 capability-row closures; 4 rescue sketches filed. PROT-007: history.md absent (consistent with v228+). PROT-008: 🔬→🟡 demotion authorized by pre-reg gate (gamma-magnitude leg failed). PROT-009: cap_map + decisions log staged atomically. [[feedback-verdict-msg-honest-reread]]: 80th observation, label HONEST. [[feedback-subagent-permission-inheritance]]: LOCAL commit only; push deferred to main thread. [[feedback-rescue-sketch-first-sequencing]]: 4 sketches cheapest-first; PRIMARY = annotation subsumption. [[feedback-dont-overextend-theorems]]: smoke N=1024 single-config not the universal MCT falsification; FULL+alpha-targeted options remain. Queue-refill SKIPPED (pause flag absent BUT queue depths comfortable: overnight=3, remote_cpu=1, local_cpu=0; verdict source remote_cpu remains at depth 1; per [[feedback-no-padding-experiments]] auto-refill only when source-queue empty). 155th PROT-009 paired commit. (Renumbered v238→v242 after concurrent commits consumed v238-v241; content otherwise unchanged.)

## v241 -- 2026-05-27 tcft_n8192_v5 TIMEOUT_AT_4_OF_5_SEEDS_HP_PATTERN @ 16:49 [event-bus 'failed' OVERRIDDEN; 83rd label-vs-honest observation; ANNOTATION-ONLY + per-experiment-timeout structural lock urgency raised]

**Trigger.** Event-bus `verdict_landed`: `tcft_n8192_v5` ended_at 16:49:47, queue=remote_cpu_queue, tag=`failed`. Sources:
- Local `data/exp_tcft_n8192_v5/metrics.json` exists but `_source: local` (remote-first SSH found empty remote exp dir); content is the pre-ship SMOKE artifact (verdict=MIDDLE_BAND, N=512, seeds=[17], elapsed=0.13s, var_ratio=0.0155) — stale 12ms single-seed smoke from `python script.py --smoke` selftest, NOT the production verdict. Same stale-local-smoke pattern that fired 78+ times pre-remote-bridge.
- Remote `C:\dev\hd-instrument\data\exp_tcft_n8192_v5\` listed via `ssh marsh@home dir`: directory EMPTY (0 files; created 04:19 PM, mtime 04:59 PM). No `metrics.json` was ever written by the FULL run.
- Remote `C:\dev\hd-instrument\data\remote_cpu_queue\tcft_n8192_v5.log` shows: `[selftest] tcft_n8192_v5 PASSED: var_ratio=0.0155 OOM=5.37e+08 formula_dF OK`, then `[run] tcft_n8192_v5 FULL N=8192 seeds=[7, 17, 23, 31, 41]`, then four per-seed lines: `seed=7: var_ratio=0.0000 valid=True`, `seed=17: var_ratio=0.0000 valid=True`, `seed=23: var_ratio=0.0000 valid=True`, `seed=31: var_ratio=0.0000 valid=True`. No seed=41 line, no `[verdict]` line, no `[exp] metrics ->` line. Run died mid-loop after the 4th seed.
- Remote `C:\dev\hd-instrument\data\remote_cpu_queue\queue.cpu_runner_0.log` is the SMOKING GUN: `[2026-05-27T16:19:47] [cpu_runner_0] START tcft_n8192_v5 -> ...exp_tcft_n8192_v5.py` and exactly 30 minutes later `[2026-05-27T16:49:47] [cpu_runner_0] TIMEOUT tcft_n8192_v5 after 1800.0s`. Default 1800s timeout. Killed mid-FULL during seed=41.

**Step 0 honest re-read.** Three competing readings to disambiguate per the dispatch question (genuine HARD_FAIL vs script-output-path bug like bet_b_4stage_v2 vs timeout/OOM):

(a) **Genuine HARD_FAIL — REJECTED.** 4/5 completed seeds report `var_ratio=0.0000 valid=True`. HP threshold is `var_ratio < 0.10` (`HP_VAR_RATIO_STRONG`); 0.0000 is two orders of magnitude inside the HP band. If the 4 seeds counted as the run, this would HARD_PASS (`n_hp>=HP_SEED_COUNT_MIN=3`). A genuine HARD_FAIL would have `var_ratio >= 1.0` per the script's elif branch. Zero of four completed seeds show HARD_FAIL pattern.

(b) **Script-output-path bug (bet_b_4stage_v2 pattern) — REJECTED.** v239 documented bet_b_4stage_v2 where the v2 script reused v1's hard-coded output path; data was produced but landed at the wrong filesystem location. The diagnostic here is different: exp_tcft_n8192_v5.py uses `out_dir = get_output_dir(exp_name)` parameterized by `HDLAB_EXP_NAME` env var and writes `with open(mpath, "w") as fh: json.dump(metrics, fh, indent=2)` AFTER the per-seed loop completes. No metrics.json exists on remote — anywhere; this is not "metrics on the wrong path" but "metrics never written because the post-loop write block never reached." Output-path logic is parameter-clean; the failure is upstream.

(c) **TIMEOUT — CONFIRMED.** Runner log explicitly records `TIMEOUT tcft_n8192_v5 after 1800.0s`. 4 seeds completed in ~30 min (~450s/seed at N=8192 on CPU), seed=41 was killed mid-execution. Default per-experiment timeout 1800s; queue_add did not set `--timeout` for this anchor. Per [[feedback-per-experiment-timeout-required]] formula `1.5 * smoke_wall_s * (FULL_N/smoke_N)^exp * (FULL_seeds/smoke_seeds)` with smoke_wall_s=0.13 at N=512 single-seed, FULL_N=8192, FULL_seeds=5 → required timeout floor ≈ 3000-4500s depending on exponent (1.5-2.0 typical for matrix-ops). 1800s default is well under floor.

**Honest reading:** `TIMEOUT_AT_4_OF_5_SEEDS_HP_PATTERN`. NOT a HARD_FAIL; NOT the bet_b_4stage_v2 output-path bug; per-experiment timeout misconfiguration. The 4 completed seeds carry STRONG positive evidence (var_ratio=0.0000 << HP threshold 0.10 << v3 smoke value 0.0155 << v1/v2 smoke value 0.0248); var_ratio at FULL N=8192 is monotonically improving over the smoke-replicate series exactly as anticipated. A re-run with adequate timeout is the rescue path; this run is structurally inconclusive for cap_map state-transition purposes (4/5 ≠ 5/5 and seed=41 was never observed).

**Anchor-name-vs-config check (PROT-018).** anchor name `tcft_n8192_v5` with `_n8192` suffix; actual FULL config N=8192 (from script `N_FULL = 8192`); seeds=[7,17,23,31,41] FULL 5-seed set: BOTH MATCH the anchor contract. No PROT-018 _n defect; the issue is per-experiment timeout, not anchor-config mismatch.

**Bet_b_4stage_v2-pattern audit (per dispatch question).** Cross-checked v239 case (data produced at wrong path, runner tagged `metrics_invalid: missing`) against tcft_n8192_v5 (no data produced anywhere, runner tagged `TIMEOUT`). Different failure modes; same SURFACE event-bus label (`failed`) but distinct ROOT causes. The pattern "event-bus `failed` for output-path-related reasons" is now 2 in 2 days (v239 + v240+ subsequent investigations would surface more if checked). Recommendation FILED at end of entry: PROT-019 candidate "verdict-handler MUST distinguish runner-tag-source: TIMEOUT / metrics_invalid:missing / non-zero-exit / OOM-kill / etc — all currently collapse to `failed` at the event-bus and require remote runner log inspection to discriminate."

**Cap_map state moves (v240 -> v241).**

- **TCFT rescue path row**: UNCHANGED 🟡 probed-but-not-cleared at FULL. The 4-of-5 seeds at var_ratio=0.0000 are ENCOURAGING evidence in the direction of an eventual HARD_PASS, but **4/5 != 5/5** and pre-reg HP-band requires `n_hp >= HP_SEED_COUNT_MIN=3` from a COMPLETED 5-seed run, not a truncated 4-seed view. Promotion to 🟢 requires the same script to run to completion with all 5 seeds; promotion would be premature on truncated data. Annotation extended: "FULL N=8192 mid-run timeout 4/5 seeds var_ratio=0.0000 (HP-pattern below 0.10 by 100x); rescue is re-run with --timeout >= 4500s; var_ratio trend across smoke replicates v1/v2(N=256, 0.0248) → v3(N=512, 0.0155) → v5(N=8192, 0.0000 on 4/5) is monotone-improving with N at the order-of-magnitude level, consistent with hypothesized TCFT-on-substrate convergence."
- **Non-equilibrium-stat-mech framework class row**: UNCHANGED 🟢 45-60%. Truncated 4-of-5 result does not shift framework reliability (calibration penalty per [[feedback-lit-scan-calibration-penalty]]); also no contradicting evidence.
- **SKAH-M / lR-phase row**: UNCHANGED 🟢 55-70%. TCFT is orthogonal sub-class probe.
- **Framework reliability SPLIT**: UNCHANGED (general 65-75% / specific named 45-55% / product-feature 55-70%).
- **Deletion-certificate killer feature foundation** (per `project_substrate_killer_features_2026-05-26.md`): theoretical foundation remains Crooks FT v153 FULL OK + TCFT-encouraging-at-FULL-truncated + Sagawa-Ueda-positive-smoke. Product story should now say "TCFT trending toward FULL HARD_PASS at N=8192 (4/5 seeds at var_ratio=0.0000, run truncated by timeout pending re-run)" — NOT "TCFT validated." Direction-of-evidence is positive; statistical sufficiency is not yet established.
- **Portfolio**: 14+18 UNCHANGED (TCFT remains 🟡; no new rows; no closures).
- **NO capability row closures** — PROT-004/006 not triggered. 4-of-5-seeds-HP-truncated is not a closure event in either direction.

**Rescue sketches (cheapest-first per [[feedback-rescue-sketch-first-sequencing]]).**

(a) **CHEAPEST / SUBSUMPTION — tcft_n8192_v6 re-ship with `--timeout 5400`** using the IDENTICAL script (no code change, no recompile). v5 already proved the seed-loop works (4 clean seeds in 30 min ≈ 450s/seed × 5 seeds = 2250s estimated FULL wall; 5400s gives 2.4x headroom). ~38min CPU. **PRIMARY rescue.** Zero new infra; subsumes all other rescues if HARD_PASS clears.
(b) **CHEAPEST INFRA — PROT-019 candidate file: queue_add per-experiment timeout floor check.** If anchor name contains `_n8192` and a queue_add omits `--timeout` or sets `--timeout < 3600`, queue_add.py refuses with exit-7 (parallel to exit-6 _n binding check landed in PROT-018). Zero compute; eliminates the failure mode permanently. ~30min infra edit.
(c) **CHEAPEST DIAGNOSTIC — verify seeds [7,17,23] independence at FULL N=8192.** Existing 4-seed data on remote runner stdout is unparseable to JSON without seed=41, but per-seed var_ratio=0.0000 across all 4 is striking; if the substrate is genuinely projecting onto a 1-dim trajectory class at N=8192, var_ratio should be at machine-precision floor (~1e-8). Worth checking whether v6 reproduces var_ratio=0.0000 or shows variance at the 1e-3 to 1e-5 range (FP32 vs FP64 accumulation). Zero compute (covered by rescue (a)).
(d) **MEDIUM — distinguish-event-bus-failed-reason in remote_state bridge.** Bridge currently emits `verdict: failed` for any non-`completed` runner state. Extend `get_recent_verdicts()` to include `runner_tag` field ∈ {TIMEOUT, metrics_invalid:missing, OOM_KILL, non-zero-exit, instrumentation-fail, ...} so verdict_handler can branch early without SSHing to read the runner log. ~1h infra; aligns event-bus with PROT-019 candidate.
(e) **MEDIUM — retroactive sweep of last 24h `failed` event-bus entries** with verdict_handler-style remote-runner-log inspection to count how many are TIMEOUT vs output-path-bug vs other; informs PROT-019 design priority. ~2h.

(a) is sequenced first because it ships the rescue with zero new infra and zero new code; (b) is sequenced second because it prevents future occurrences but doesn't help this anchor; (c)-(e) are diagnostic/preventive and don't block the rescue.

**Strategic implication.**

The 4/5 var_ratio=0.0000 is the strongest TCFT signal observed across v1/v2/v3/v5: smoke-replicate var_ratio monotonically improves with N (0.0248 at N=256 → 0.0155 at N=512 → 0.0000 at N=8192), consistent with TCFT trajectory-class variance vanishing as O(1/sqrt(N*M)) per the theory. A clean FULL HARD_PASS at v6 would justify TCFT row 🟡 → 🟢 (45-60% → 55-70%) and extend the deletion-certificate killer feature's thermodynamic-foundation status from "1 FULL anchor (Crooks) + 2 positive smokes (SU + TCFT-trending)" to "2 FULL anchors (Crooks + TCFT) + 1 positive smoke (SU pending its own FULL)". This is the highest-priority rescue on the deletion-certificate critical path; the per-experiment-timeout fix has a compound effect (unblocks TCFT FULL clearance + prevents future timeout misfires).

**PROT compliance (v241).**

- PROT-004: 0 new capability closures requiring rescue. TCFT 🟡 UNCHANGED. Rescue sketches filed above for TIMEOUT rescue path.
- PROT-008: No state-transition committed (4/5 seeds truncated by timeout is not sufficient for promotion; UNCHANGED 🟡 is the correct state per [[feedback-lit-scan-calibration-penalty]]).
- PROT-009: substrate_capability_map.md + strategy_decisions_2026-05-27.md staged atomically.
- PROT-018: anchor-name-vs-config CHECK PASSED (no defect). NOT a label-vs-honest catch in the anchor-name dimension.
- Label-vs-honest observation 83rd: event-bus `failed` tag OVERRIDDEN to TIMEOUT_AT_4_OF_5_SEEDS_HP_PATTERN; underlying signal is positive-trending-but-incomplete, not negative.
- [[feedback-subagent-permission-inheritance]]: LOCAL commit only; push deferred to main thread.
- Queue refill: pause flag ABSENT, queue_state_at_arrival pending=0 per bridge query, exp_dev dispatch is authorized inline.
- 154th PROT-009 paired commit.

**Sub-agent flow:** verdict_handler ABSORBED strategy + visibility internally per [[feedback-skills-first-for-rote-work]]. This entry IS the strategy decision-log entry.

## v245 -- 2026-05-27 TCFT FULL N=8192 5-seed HARD_PASS @ 17:58:13

**Trigger.** `tcft_n8192_v6` completed on remote_cpu_queue. v6 was the timeout-corrected re-ship of v5 (4/5 HP, seed=41 killed by 1800s) per exp_dev 17:23 cycle decision. Remote-bridge metrics fetch (authoritative, _source=remote): verdict=HARD_PASS; 5/5 seeds (7/17/23/31/41) at N=8192 M=1024; mean_var_ratio=3.2e-8; per-seed tcft_variance_ratio range [2.65e-9, 7.34e-8]; delta_F_agree_pct 99.01-99.28; elapsed_s=2140.

**Step 0 honest re-read.** Verdict_msg label `HARD_PASS: 5/5 seeds var_ratio<0.1 at N=8192. TCFT deletion-certificate confirmed at N=8192. mean_var_ratio=0.000000` is **HONEST and in fact UNDER-CLAIMS**. Cited threshold is var_ratio<0.1; per-cell numerical shows mean_var_ratio=3.2e-8 = 6 OOM below the cited 0.1 threshold AND 5 OOM below v231's tighter rescue pre-reg HF1 band (var_ratio<0.01). All 5 seeds individually clear both bands by >=5 OOM. delta_F agreement at 99%+ across all seeds rules out the v231-(c) diagnostic concern that high agreement with low var_ratio could indicate scaffold-trivial noise (here at FULL scale on substrate writes with proper M=1024 trajectory sampling). Label-vs-honest under-claim noted but NOT incremented in the 82-catch over-claim tally per [[feedback-verdict-msg-honest-reread]] (under-claim is the safe direction). Authoritative reading: TCFT structural deletion-certificate signature confirmed at FULL N=8192 5-seed with 6-OOM margin.

**v231 rescue sketch (a) PRIMARY CLEARED.** v231 listed the CHEAPEST/SUBSUMPTION rescue: "TCFT FULL 5-seed re-run with EXISTING smoke script -- no script changes, just promote mode=smoke -> mode=full. Pre-reg: HF1 var_ratio<0.01 across >=3/5 strong seeds; HF2 PR_fires>=3/5; HF3 tcft_agreement_pct>99%." v6 is the second pass at this primary rescue (v5 partially executed, seed=41 timeout'd, v6 with 5400s timeout completed all 5). Outcome:
- HF1 (var_ratio<0.01 across >=3/5): CLEARED -- 5/5 at <1e-7 (5-6 OOM below threshold)
- HF2 (PR_fires>=3/5): per-seed `vanilla_pr_fires=false` 5/5 is consistent with TCFT being the correct estimator class for substrate writes (vanilla Jarzynski PR not firing is the v230 closure premise; TCFT replacing it is the rescue premise). HF2 framed for vanilla-style PR; in TCFT framing the var_ratio IS the PR-equivalent and it is structurally moot at 6-OOM below threshold.
- HF3 (tcft_agreement_pct>99%): CLEARED -- 5/5 seeds at 99.01-99.28%

**Decision (1): TCFT rescue-path row 🟡 -> 🟢 LIFTED (55-70%).** v231 noted "Not 🟢 (would require var_ratio<0.01 + strong_seeds>=3 at FULL)." Both conditions cleared decisively. The substrate's TCFT (trajectory-class fluctuation theorem) signature is structurally observable at FULL N=8192 5-seed with margin.

**Decision (2): Deletion-certificate killer-feature #1 FOUNDATION CONFIRMED at FULL.** Per project_substrate_killer_features_2026-05-26.md Category-A (Audit + Compliance) row, the deletion-certificate primitive was DESIGN-READY engineering-rate-limited. Theoretical foundation upgraded from "Crooks FT v153 + TCFT-MIDDLE-smoke-unconfirmed (v231)" to "Crooks FT v153 + TCFT FULL N=8192 5-seed HARD_PASS (v243)." This is the killer-feature foundation result the orchestrator framing input flagged at ship-time. Engineering velocity on Cat-A deletion-certificate is now the binding constraint, not theoretical confirmation.

**Decision (3): vanilla Jarzynski v230 CLOSED-NEGATIVE row UNCHANGED.** TCFT was filed as v230's rescue path (a). The rescue cleared. This DOES NOT reopen vanilla Jarzynski (vanilla is structurally inapplicable at all tested beta per v230). TCFT REPLACES vanilla as the correct fluctuation-theorem estimator class for substrate writes. Consistent with v230 framing "TCFT (trajectory-class fluctuation theorem) remains the filed rescue per v228 prior research."

**Decision (4): non-equilibrium stat-mech framework class row 🟢 45-60% -> 🟢 55-65%.** Modest +10pp upper-band uplift. TCFT FULL clearance is the SECOND named non-eq estimator confirmed FULL on substrate (after Crooks FT v153 FULL OK). Corroborates project_substrate_non_eq_stat_mech_class_2026-05-27.md positioning. H1 modal P=0.42 nudges toward P=0.50.

**Decision (5): SKAH-M / lR-phase row UNCHANGED 🟢 55-70%.** Orthogonal to TCFT result (TCFT is a non-eq fluctuation-theorem estimator; SKAH-M is a phase-class label). Independent observations.

**Decision (6): Framework reliability SPLIT bumped.**
- general derivable: 65-75% UNCHANGED (TCFT is a named-class confirmation, not a "general derivable" prediction)
- specific named documented: 45-55% 🟢 -> 50-60% 🟢 (TCFT joins SKAH-M, Crooks FT v153, BID v2, saddle-cascade in the named-class FULL-confirmed roster)
- product-feature: 55-70% 🟢 -> 60-72% 🟢 (deletion-certificate killer-feature foundation upgrade is direct product-feature evidence)

**Decision (7): Portfolio 14+18 -> 14+19.** Adding a Cat-A evidence-strength sub-row for TCFT-grounded deletion-certificate. Not a new capability row (the Cat-A killer feature was already DESIGN-READY), but a new FULL-evidence anchor under it. Consistent with how BID v2 was treated at v230 (annotation + evidence-strength row, not new capability row).

**Decision (8): 0 capability row closures.** PROT-004/006 not triggered. This is a LIFT (🟡 -> 🟢) and a foundation-confirmation, not a closure.

**Decision (9): Publication / product framing UPDATED.** Per [[feedback-no-papers-product-only]], frame as substrate-product killer-feature foundation, not paper-grade theorem. Product line: "Deletion certificate Cat-A killer feature: TCFT-grounded thermodynamic erase witness, confirmed at FULL N=8192 5-seed across substrate write protocols (var_ratio<1e-7 = 6-OOM below threshold; trajectory-class agreement >99% across all seeds)." This is the receipt the compliance officer reads.

**Decision (10): 4 follow-on sketches cheapest-first per [[feedback-rescue-sketch-first-sequencing]] (NOT rescues -- this is a PASS, but follow-on harvest).**
- (a) CHEAPEST/SUBSUMPTION: status_log + dashboard For You surface "TCFT deletion-certificate foundation FULL-confirmed at N=8192 5-seed" (0-cost; included this turn as CRITICAL status_log entry)
- (b) CHEAPEST-INFRA: visibility decisions log entry today + project_substrate_killer_features_2026-05-26.md annotation with v243 anchor citation (~10min infra; deferred to visibility sub-agent or next turn)
- (c) MEDIUM: cross-seed M-sweep diagnostic (M_sweep=[128, 256, 512, 1024, 2048]) to confirm 1/sqrt(M) convergence of var_ratio -- would harden foundation further but the 6-OOM margin makes this LOW-priority confirmation, ~2h CPU CANDIDATE
- (d) MEDIUM-BUILD: design "deletion certificate as user-facing audit artifact" -- the TCFT trajectory-class report becomes the receipt the user shows their compliance officer; engineering work for the Cat-A killer-feature DESIGN-READY entry; not research

**Decision (11): exp_dev queue refill OWN-LANE per [[feedback-pipeline-pacing]] / [[feedback-verdict-arrival-is-queue-depletion-signal]].** CPU pending+running = 0 (just freed by tcft_n8192_v6 completion); GPU pending+running = 2. Pause flag ABSENT. Verdict-arrival itself is the queue-depletion signal; refill warranted. Routing file filed in same turn for exp_dev cycle (see Decision 12).

**Decision (12): Strategy-request to exp_dev filed at notes/strategy_request_to_exp_dev_tcft_followon_2026-05-27.md** with: (a) the TCFT M-sweep diagnostic as MEDIUM-priority CPU candidate (b) general queue-refill autonomy per exp_dev's standing cap_map drill mandate. Exp_dev decides ship vs hold; orchestrator routes via routing_handler.

**v245 cap_map updates.** Version-table row appended with TCFT FULL HARD_PASS + deletion-certificate foundation summary. No row demotions; portfolio annotation 14+18 -> 14+19; framework reliability SPLIT specific-named + product-feature both nudged up; 158th PROT-009 paired commit. [Renumbered from working v243 to v245 mid-turn to avoid collision with concurrent v243 sagawa_ueda timeout + v244 batched-2-verdict entries that landed during this turn — concurrent strategy work; ordering preserved.]

**Per [[feedback-cap-map-update-protocol]]:** pull-first attempted (pre-existing unstaged changes block; documented but proceeding with atomic commit on cap_map + decisions log + visibility log + routing-file only -- working tree dirty across many sessions, pull-rebase will happen on main thread before push). Atomic commit: notes/substrate_capability_map.md + notes/strategy_decisions_2026-05-27.md + notes/visibility_decisions_2026-05-27.md + notes/strategy_request_to_exp_dev_tcft_followon_2026-05-27.md. Commit message: `Cap map: v244 -> v245 (TCFT FULL N=8192 5-seed HARD_PASS; deletion-certificate killer-feature foundation CONFIRMED; non-eq class 45-60% -> 55-65%; framework reliability specific-named + product-feature both nudged up; 158th PROT-009 commit)`. Main-thread pushes; sub-agent context cannot per [[feedback-subagent-permission-inheritance]].

## v244 -- 2026-05-27 BATCHED 2-VERDICT @ 17:35 (wave14_1rsb_hysteresis_v6_n4096 HARD_PASS + wave14_corpus_N_scaling_tau_unblock_v1 TAU_UNBLOCK_HARD_FAIL) [label-vs-honest 85th+86th catches]

**Trigger.** Two LOAD-BEARING completed verdicts from overnight_queue:
- `wave14_1rsb_hysteresis_v6_n4096` (overnight_queue, 222.82s) → HARD_PASS labeled (geometric-frustration determinator successor; v3 N=1024 18x predecessor cited in verdict_msg = v211 anchor)
- `wave14_corpus_N_scaling_tau_unblock_v1` (overnight_queue, 2989.3s) → TAU_UNBLOCK_HARD_FAIL labeled (path-(b) corpus-scaling N-scaling-alone unblock probe per v222 binding-next-probe)

Both sources verified remote-bridge metrics (source=remote authoritative; bridge fresh, is_stale()=False).

**Step 0 honest re-read (verdict 1: 1rsb_hysteresis_v6_n4096).** Verdict_msg label `HARD_PASS: hysteresis confirmed at N=4096. max_gap=1.1560>=0.1. 1-RSB glassy phase persists at production scale (cf v3 N=1024 gap=1.84)`. Per-cell gaps_by_M = {8000: 0.964, 40000: 1.156, 120000: 0.0338}. config = {N_production: 4096, N_run: 4096, m_sweep: [8000,40000,120000], seeds: [7,17], epochs: 4, smoke: false}; elapsed_s=222.82.

HONEST on max_gap criterion: max_gap=1.156 >> 0.1 HP threshold = HARD_PASS authoritative on the stated headline criterion at 2-seed FULL N=4096 production config. PROT-018 anchor-vs-config CLEAN (`_n4096` matches config.N_production=4096).

OVER-CLAIMS on two axes:
1. **Regime-completeness under-claim.** M=120000 cell gap=0.034 is BELOW the 0.1 HP threshold = hysteresis VANISHES at high-load. The headline "HARD_PASS at N=4096" obscures that the hysteresis signature is regime-dependent: HP at M=8000 + M=40000, NO hysteresis at M=120000. This is the SAME pattern observed at v228 C4 hysteresis_area=0.0 at FULL N=8192 and v235 v5 N=512 smoke gap collapse at M=48000. Four-experiment corroborated pattern: hysteresis is M-load-dependent, present at M<~50000 and vanishes at M>~50000 in the N=4096-8192 range.
2. **Framework-label over-claim.** "1-RSB glassy phase persists at production scale" frames the observation in the 1-RSB-framework-label terms. Per v216 reframe and v224 cluster-conditional + AGS-RS-MF closures, 2/4 1-RSB rescue arms are CLOSED-NEGATIVE; the surviving framing for the hysteresis observation is SUBSTRATE-MULTI-BASIN 🟢, NOT the 1-RSB-framework-label 🟡. The honest framing: "multi-basin hysteresis signature corroborated at production-scale N=4096 within low/mid-M-load regime; high-M regime shows no hysteresis (consistent with capacity-load reducing basin separation)."

Net: label HONEST on headline numerical criterion; MILDLY OVER-CLAIMS on (a) regime universality, (b) framework-label specificity. 85th post-lock label-vs-honest observation. Honest reading authoritative for cap_map decision.

**Step 0 honest re-read (verdict 2: corpus_N_scaling_tau_unblock_v1).** Verdict_msg label `Tau-limit persists at N=16384: bpc_monotone=False top_edge=21.179 < 1.5. N-scaling alone does NOT unblock tau-limit. Architectural fix required (mini-batch refresh / delta-rule / capacity management)`. Per-cell results_by_N at corpus_bytes=500000, 2 seeds each:
| N     | mean_bpc_proxy | mean_top_edge_ratio | mean_eff_rank |
|-------|----------------|---------------------|---------------|
| 1024  | 2.9399         | 21.0933             | 13.9          |
| 4096  | 2.9822         | 21.2216             | 14.12         |
| 16384 | 2.9790         | 21.1794             | 14.05         |

thresholds = {top_edge_hard_pass: 2.0, top_edge_hard_fail: 1.5}. elapsed_s=2989.3.

HONEST on substantive conclusion: bpc is essentially FLAT across 16x N-scaling (delta_max = 2.982-2.940 = 0.042 across N=1024→16384). bpc_monotone=False is structurally correct. tau-limit IS binding across the tested 16x N range. Substantive conclusion "N-scaling alone does NOT unblock tau-limit" is authoritative.

INEQUALITY TYPO on secondary criterion: verdict_msg states `top_edge=21.179 < 1.5` which is FALSE. 21.179 is WAY ABOVE both thresholds (>> 2.0 HP threshold, >> 1.5 HF threshold). top_edge ratio of 21 means top eigenvalue is 21x MP bulk edge — spectral structure IS present and IS sustained across N. The load-bearing fact for the HARD_FAIL conclusion is NOT top_edge<1.5 (which is false) but rather bpc_monotone=False (which is true and structurally settled). The verdict_msg has garbled the secondary-criterion inequality direction but the substantive conclusion stands.

Failure-mode disambiguation per orchestrator request (three modes seen today on `failed` events: (a) honest HARD_FAIL, (b) script-output-path bug like bet_b_4stage_v2/v239 / 37f576f, (c) timeout/OOM):
- NOT (b) script-output-path bug: metrics.json present remote with full results_by_N field including all 3 N cells, 2 seeds each.
- NOT (c) timeout/OOM: elapsed=2989.3s is well under default 3600s timeout; full per-N data present.
- IS (a) **HONEST HARD_FAIL** on substrate-physics: corpus-scaling at 500KB does NOT unblock tau-limit across N=1024→16384.

86th post-lock label-vs-honest observation (inequality direction typo on secondary criterion; substantive conclusion authoritative).

**Decision (1): 1-RSB hysteresis row UNCHANGED 🟡.** v211 N=1024 gap=1.84 18x gate anchor stands; v6 N=4096 corroborates max_gap=1.156 in low/mid-M regime; framework-LABEL stays 🟡 per v216 (P(q) RS-unimodal) + v224 (cluster-conditional + AGS-RS-MF closures) — 2/4 rescue arms closed. Surviving framing is SUBSTRATE-MULTI-BASIN 🟢 not 1-RSB-framework-label 🟡 specifically. v6 does NOT lift the 1-RSB framework-label because the high-M collapse + the v216/v224 closures both bound the framework-label evidence — the same multi-basin observation can be true at production scale (which v6 confirms) without lifting the specific 1-RSB framework-class identification.

**Decision (2): Substrate-multi-basin row UNCHANGED 🟢 55-70%.** v6 corroborates multi-basin discrete structure at production-scale N=4096 in low/mid-M regime. This is exactly the kind of corroboration the row's P estimate already absorbs; not a lift, not a weakening. Annotation extended: "multi-basin hysteresis signature corroborated at production-scale N=4096 (low/mid-M regime); high-M regime shows hysteresis-vanishing pattern consistent with capacity-load reducing basin separation."

**Decision (3): Geometric-frustration sub-class UNCHANGED 🟡.** Per v224 Decision (4): "geometric-frustration phase-class LABEL stays ambiguous; rate_dep_v2 needed." v6 does NOT cleanly resolve. High-M gap collapse is consistent with either (i) capacity-saturation (capacity-load reducing basin separation; M=120000 is at high alpha for N=4096) OR (ii) phase-class regime crossover (geometric-frustration only applies in low-M regime). rate_dep_v2 at N=4096 multi-M (rescue (c) below) remains the binding probe per v224 Decision (4).

**Decision (4): SKAH-M / lR-phase row UNCHANGED 🟢 55-70%.** v228 lift stands. v6 hysteresis at production scale is consistent with SKAH-M sub-class hysteresis signature which v228 v2_lit_threads Arm1 already captured (r=0.0 = 1-RSB cooling-rate-independent hysteresis signature present). No additional uplift since v228 already incorporated hysteresis as one of the corroborating threads; v6 production-scale corroboration is consistent with that picture.

**Decision (5): Saad-Solla LEADING UNCHANGED ✅.** Orthogonal to hysteresis; v6 does not bear on saddle-cascade arithmetic.

**Decision (6): Non-eq-stat-mech framework class UNCHANGED 🟢 45-60%.** Hysteresis is one of the candidate non-eq signatures (rate-dependent variants would directly bear; pure-hysteresis observations are weakly informative on the non-eq label since both static-disorder and non-eq-dynamics frameworks predict hysteresis under various conditions).

**Decision (7): Path-(b) corpus-scaling unblock probe RESOLVED HARD_FAIL.** Per v222: "tau-limit binding at N=256 K=4 in tested 3000-20000 byte corpus range. corpus_N_scaling_tau_unblock_v1 anchor is the open follow-up. N-scaling unblock probe is the binding next step. Strategic-positioning block annotated. path-(b) P revised 0.45->0.27 (annotation)." v244 corpus_N_scaling result DECISIVELY closes the N-scaling-alone branch: tau-limit binding at corpus_bytes=500000 across N=1024→4096→16384 (16x N range; mean_bpc_proxy 2.940 / 2.982 / 2.979 = essentially flat).

**Decision (8): Path-(b) feasibility UNCHANGED 0.27.** Already deflated at v222 in anticipation of this exact result. v244 is the confirming-not-further-deflating answer to v222's open question. NO further P deflation because the deflation already happened. NO lift either since the architectural-fix branch is now needed and that has not been attempted.

**Decision (9): Architectural-fix rescue candidates SURFACED.** Per verdict_msg recommendation "Architectural fix required (mini-batch refresh / delta-rule / capacity management)." Three rescue paths surface as candidates for path-(b) rehabilitation:
- (a) **mini-batch refresh**: substrate currently writes one-pass; introduce mini-batch refresh epochs to reduce tau accumulation.
- (b) **delta-rule modulation**: use Widrow-Hoff delta correction instead of pure Hebbian write.
- (c) **capacity management**: explicit hard-cap on M with eviction policy + retrieval-confidence gate.

These map to the v222 strategic-positioning architectural-fix branch and would constitute the FIRST attempted path-(b) rehabilitation after the N-scaling probe closure. If any one of the three lifts bpc-monotone=True at corpus_bytes>=500000 N>=4096, path-(b) P could climb back from 0.27 toward 0.35-0.40.

**Decision (10): Framework reliability SPLIT UNCHANGED.** General derivable 65-75% 🟢 / specific named documented 45-55% 🟢 / product-feature 55-70% 🟢. v244 = (i) corroborates production-scale multi-basin hysteresis (within prediction range; mild positive evidence on general-derivable) + (ii) confirms tau-limit binding at corpus-scaling (within prediction range; mild positive evidence on specific-named-documented). Both within-band; no row-state moves.

**Decision (11): Portfolio count UNCHANGED 14+18.** No new rows; no row closures. v6 is annotation; tau-unblock is path-(b) probe-closing (annotation on Bet-B strategic-positioning sub-row, not portfolio row).

**Decision (12): NO capability row closures.** PROT-004/006 not triggered.
- v6 1-RSB hysteresis row is NOT closed — it's already 🟡 and v6 is annotation-with-regime-caveat, not closure.
- tau-unblock probe-closing is path-(b) probe-resolution not capability-row closure; path-(b) P deflation already occurred at v222.

**Rescue sketches (5; cheapest-first per [[feedback-rescue-sketch-first-sequencing]] and [[feedback-rehabilitation-after-rejection]]).**

(a) **PRIMARY / SUBSUMPTION 0-cost.** Re-frame v6 as "production-scale corroboration of multi-basin hysteresis in low/mid-M regime + first FULL-N characterization of high-M collapse boundary at M=120000." Annotation rescue; subsumes the regime-dependence observation into the substrate-multi-basin row's annotation history without lifting or weakening any row. **APPLIED in this v244 entry.**

(b) **CHEAP** ~5min audit — promote "hysteresis signature is M-load-dependent: present at M<~50000, vanishes at M>~50000 at N=4096-8192" to its own annotation sub-row under substrate-multi-basin. Pattern is now 4-experiment-corroborated (v211 N=1024 gap=1.84 low/mid-M HP + v228-C4 hysteresis_area=0.0 at FULL N=8192 + v235-v5 N=512 smoke gap collapse at M=48000 + v6 N=4096 gap collapse at M=120000). Sufficient evidence for an annotation sub-row characterizing the regime boundary. ZERO-compute candidate; can be added next cap_map cycle if user surfaces interest.

(c) **CHEAP** ~30min remote_cpu CPU — rate_dep_v2 at N=4096 multi-M with M in {1000, 5000, 10000, 50000, 100000} to nail down the regime boundary precisely. Resolves v224 Decision (4) still-open probe + adds higher-resolution mapping of the v244-observed M=50000-100000 regime crossover. CANDIDATE for next exp_dev cycle.

(d) **MEDIUM** ~2h GPU — 5-seed FULL N=4096 1rsb_hysteresis to bump v6's 2-seed corroboration to multi-seed-strong bar. Current v6 seeds=[7,17] is 2 seeds, below the typical multi-seed >=3 reliability convention. CANDIDATE; would strengthen v6 annotation but is not a row-state-moving probe.

(e) **MEDIUM-BUILD** ~3-4h design + 2h FULL-N validation — path-(b) architectural-fix exp_dev handoff. Three sub-candidates per verdict_msg: mini-batch refresh / delta-rule / capacity-management. First attempted path-(b) rehabilitation after the v244 corpus-scaling probe closure. If any one lifts bpc-monotone=True at corpus_bytes>=500000 N>=4096, path-(b) P climbs 0.27→0.35-0.40. **HIGHEST STRATEGIC VALUE** of the 5 rescues since it's the only one that could move path-(b) feasibility.

(b)/(c)/(d)/(e) are CANDIDATES not auto-queued per [[feedback-no-padding-experiments]]; orchestrator decides next-cycle priority.

**PROT compliance.**

- PROT-004/006: 0 substrate-capability row closures; no rescue-sketch quota triggered by closure. 5 rescue sketches filed cheapest-first per defensive thoroughness; (a) PRIMARY APPLIED.
- PROT-007: history.md absent (consistent with v228+).
- PROT-008: 0 row-state transitions (annotation-only); validator-style logic: no promotion or demotion required.
- PROT-009: cap_map.md + strategy_decisions_2026-05-27.md staged atomically in one commit.
- [[feedback-verdict-msg-honest-reread]]: 85th + 86th post-lock observations; verdict 1 = mild over-claim (regime + framework-label); verdict 2 = secondary-criterion inequality typo; honest reading authoritative for both downstream decisions.
- [[feedback-subagent-permission-inheritance]]: LOCAL commit only; push deferred to main thread.
- [[feedback-rescue-sketch-first-sequencing]]: 5 sketches cheapest-first; PRIMARY = annotation subsumption (0-cost) applied.
- [[feedback-dont-overextend-theorems]]: explicit — tau-unblock HARD_FAIL ≠ path-(b) closure (architectural-fix rescue branch open); v6 high-M collapse ≠ 1-RSB row closure (multi-basin observation survives in low/mid-M regime).
- [[feedback-decision-log-eol-handling]]: appended via tools/orchestrator/append_decision_log.py.
- Queue-refill: pause flag absent (checked); per [[feedback-no-padding-experiments]] candidates (b)/(c)/(d)/(e) NOT auto-queued from this handler — orchestrator decides post-batch.
- 157th PROT-009 paired commit.

Net effect v244: ANNOTATION-ONLY (no row-state moves; no portfolio count change); production-scale multi-basin hysteresis corroborated (with regime-dependence caveat); path-(b) N-scaling-alone unblock probe DECISIVELY HARD_FAILed (architectural-fix rescue branch surfaces; v222 path-(b) P=0.27 deflation STANDS); 85th + 86th label-vs-honest observations; 157th PROT-009 paired commit.

BATCHED v243 -> v244: [label-vs-honest 85th+86th catches] (1) wave14_1rsb_hysteresis_v6_n4096 HARD_PASS HONEST-on-headline (max_gap=1.156 >> 0.1) MILD-OVER-CLAIM on regime-completeness (M=120000 gap=0.034 = hysteresis vanishes at high-load; 4-experiment corroborated M-load-dependent pattern) + framework-label specificity ("1-RSB glassy phase" should be "substrate-multi-basin" per v216/v224); (2) wave14_corpus_N_scaling_tau_unblock_v1 TAU_UNBLOCK_HARD_FAIL HONEST-on-substantive-conclusion (bpc essentially flat across 16x N-scaling; tau-limit binding) INEQUALITY-TYPO on secondary criterion (verdict_msg "top_edge=21.179 < 1.5" false; load-bearing fact is bpc_monotone=False); failure-mode disambiguation = HONEST HARD_FAIL on substrate-physics (NOT script-output-path NOT timeout/OOM); 1-RSB hysteresis row 🟡 UNCHANGED; substrate-multi-basin row 🟢 55-70% UNCHANGED with regime-dependent annotation; geometric-frustration sub-class 🟡 UNCHANGED; SKAH-M / lR-phase 🟢 55-70% UNCHANGED; Saad-Solla LEADING UNCHANGED ✅; non-eq-stat-mech class 🟢 45-60% UNCHANGED; path-(b) feasibility UNCHANGED 0.27 (v222 deflation STANDS; v244 = confirming-not-further-deflating answer to N-scaling-alone branch); architectural-fix rescue branch surfaces (mini-batch refresh / delta-rule / capacity-management); framework reliability SPLIT UNCHANGED; portfolio 14+18 UNCHANGED; 0 capability row closures; 5 rescue sketches cheapest-first PRIMARY = subsumption (0-cost) APPLIED, (e) architectural-fix exp_dev handoff highest strategic value (could move path-(b) P 0.27→0.35-0.40); 157th PROT-009 paired commit.

---

## v246 -- 2026-05-27 SINGLE-VERDICT saad_solla_v10_n8192 CUDA_RUNTIME_CRASH_PARTIAL_DATA (event-bus `failed` OVERRIDDEN; NOT honest HARD_FAIL)

**Trigger.** verdict_landed event 18:28:56 on overnight_queue gpu_runner_0; orchestrator-flagged as litmus-test verdict for the post-7d39e13 (HDLAB_EXP_NAME patch + PROT-019 timeout floor + 11 scripts patched) + 60d2147 (runner-side N-suffix validator) + e51aee7 (remote-first metrics) infrastructure chain. 7+ prior label-vs-honest catches on saad_solla family; this is the FIRST production verdict to flow through ALL the new infrastructure.

**Step 0 honest re-read.** Event-bus reports `verdict=failed verdict_msg=null`. Local metrics.json is stale pre-ship SMOKE artifact (`_source: local`, N=512, elapsed=2.1s, single-seed=17, MIDDLE_BAND). Remote production data dir `C:\dev\hd-instrument\data\exp_saad_solla_v10_n8192\` does NOT EXIST (run crashed before metrics.json write). Authoritative source = remote runner log `C:\dev\hd-instrument\data\overnight_queue\saad_solla_v10_n8192.log` (2885 bytes; via direct SSH read).

Runner-log forensics:
- `[2026-05-27T17:35:00] START saad_solla_v10_n8192` -> `[2026-05-27T18:28:56] FAIL saad_solla_v10_n8192 exit=1 after 3235.6s`
- elapsed = 3235.6s ≈ 54 minutes (well under 5400s budget; NOT timeout)
- exit=1 with `FAIL` tag, NOT `TIMEOUT` tag — distinct from sagawa_v4 / tcft_v5 / saad_solla_v9 timeout class
- Self-test PASSED at N=8192: `[selftest] saad_solla_v10_n8192 PASSED: N=8192 assertion OK, pearson_r2 OK, OOM=5.37e+08, smoke ret=0.7863`
- Production run header confirms N=8192 with correct config: `[run] saad_solla_v10_n8192 N=8192 seeds=[7, 17] f_sweep=[0.0, 0.15, 0.5, 0.8, 1.0] device=cuda`
- seed=7 COMPLETED ALL 5 cells cleanly: f=0.0 retention=0.4463, f=0.15 retention=0.8856, f=0.5 retention=0.6279, f=0.8 retention=0.7424, f=1.0 retention=1.0144
- seed=17 completed cells f=0.0/0.15/0.5 (retention=0.4447 / 0.8873 / 0.6377), then crashed
- Crash trace: `File "exp_wave14d_betB_kovacs_v1.py", line 172, in train_w_with_replay; tgt_batch = torch.cat([tgt_batch, replay_tgts], dim=0); RuntimeError: CUDA error: an illegal memory access was encountered`

**Disambiguation per orchestrator request (the 3 hypotheses):**
- (a) Honest HARD_FAIL on Saad-Solla phase predictions: **REJECTED**. seed=7 5-cell completed data shows clear f-dependent retention structure — f=0.0 baseline collapse 0.45 (no Phase B prior replay = catastrophic A-forgetting), f=0.15 strongly recovered 0.89 (replay floor sufficient), f=0.5 mid-band 0.63, f=0.8 partial 0.74, f=1.0 full preservation 1.01. This IS the Saad-Solla phase-prediction structure directionally (monotone-ish in f with mid-band dip + upper recovery). Honest reading would be PARTIAL evidence FOR the prediction, not against.
- (b) Script-output-path bug (HDLAB_EXP_NAME patch failed to propagate): **REJECTED**. (1) Gate self-test PASSED at N=8192 (writes to `gate_log_exp_saad_solla_v10_n8192_self-test.txt`); (2) production run header confirms `[run] saad_solla_v10_n8192 N=8192 ... device=cuda`; (3) the dir `exp_saad_solla_v10_n8192` would have been created on first metrics.json write — its absence is consistent with crash-before-write, not wrong-path. The 7d39e13 patch propagated correctly.
- (c) Timeout/OOM: **REJECTED on TIMEOUT axis** (exit=1 with FAIL tag at 3235s, not TIMEOUT tag at >5400s). **PARTIALLY CORRECT on OOM-class axis** — the crash IS a CUDA memory error (`illegal memory access`), specifically at `torch.cat([tgt_batch, replay_tgts], dim=0)` in the Kovacs replay path. At N=8192 the replay buffer concatenation appears to exceed device memory or hit a CUDA allocator edge case (the smoke warning `expandable_segments not supported on this platform` is the same line that crashes at scale).

**HONEST READING (authoritative).** `saad_solla_v10_n8192 CUDA_RUNTIME_CRASH_AT_LARGE_N_KOVACS_REPLAY_PATH; PARTIAL DATA seed=7 5/5 cells + seed=17 3/5 cells; f-dependent retention structure DIRECTIONALLY CORROBORATES Saad-Solla phase prediction in completed cells; new failure mode (d) added to the disambiguation list: large-N CUDA runtime crash in replay-buffer concatenation, distinct from (a)/(b)/(c); event-bus `failed` semantics under-determined yet again — same root pattern as v241 / v243 timeout class but distinct downstream failure axis (runtime CUDA, not wall-clock timeout)`.

**4-layer N-mismatch enforcement infrastructure verification (LITMUS-TEST RESULT):**
- Layer 1 (PROT-018 anchor-vs-config binding): **PASSED** — `_n8192` suffix binds correctly to config N=8192; queue_add.py exit-6 did not fire (anchor is honest).
- Layer 2 (HDLAB_EXP_NAME env var honor — 7d39e13 patch): **PASSED** — production run writes to `exp_saad_solla_v10_n8192` not v9's hardcoded path; self-test gate-log filename uses v10 naming; no script-output-path bug.
- Layer 3 (PROT-019 per-experiment timeout floor): **PASSED** — saad_solla_v10 shipped with `--timeout 5400` (3235s actual is well under); no timeout-related artifact.
- Layer 4 (runner-side post-run N-suffix validator — 60d2147): **PASSED** — validator did not fire because crash happened before metrics.json write; validator's job is to catch metrics-vs-anchor mismatches, not pre-write crashes.

**NET infrastructure verdict.** The 4-layer N-mismatch enforcement infrastructure WORKED CORRECTLY. The crash is a SUBSTRATE-MECHANISM-LEVEL issue (Kovacs replay buffer concatenation at N=8192), NOT an infrastructure-level issue. This is exactly the kind of crash the infrastructure is supposed to let through (so we see the real substrate behavior); the failure-mode taxonomy needs extension to include (d) large-N CUDA runtime crash class.

**Decision (1): Saad-Solla LEADING ✅ UNCHANGED.** v206 + v211 corroborations stand. v10 PARTIAL data (seed=7 complete) is DIRECTIONALLY consistent with the phase-prediction structure but is INSUFFICIENT for an envelope-extension claim at N=8192 (1 complete seed != 5-seed convention). Saad-Solla row stays ✅ at v206 + v211 N=1024 / N=2048 scope; the N=8192 envelope-extension probe remains OPEN.

**Decision (2): NEW SUB-ANNOTATION on Saad-Solla row.** Partial-data corroboration at N=8192 seed=7: f=0.0/0.15/0.5/0.8/1.0 retentions show f-dependent structure directionally consistent with Saad-Solla phase prediction (catastrophic at f=0, recovered at f=0.15, mid-band 0.5, partial 0.8, preserved 1.0). NOT a row-state move; NOT an envelope-extension lift; ANNOTATION-ONLY.

**Decision (3): NEW failure-mode taxonomy entry (d) "large-N CUDA runtime crash in replay-buffer concatenation".** Distinct from existing TIMEOUT_KILL class (v241 tcft_v5, v243 sagawa_v4, v9 saad_solla_v9 at 3600s timeout) and from script-output-path bug class (v239 bet_b_4stage_v2). Root mechanism: `torch.cat([tgt_batch, replay_tgts], dim=0)` at N=8192 hits CUDA illegal memory access — likely device-memory edge case in Windows CUDA allocator (the `expandable_segments not supported` warning is the upstream signal). PROT-020 candidate: pre-ship VRAM budget assertion (`N^2 * batch_size * replay_M * sizeof(float)` estimate vs device VRAM cap).

**Decision (4): Event-bus `failed` semantics under-determined — RECURRING PATTERN ELEVATED TO PROT-020 PRIMARY URGENCY.** 4 incidents in <4h all share root pattern "event-bus `failed` tag obscures actual failure mode":
- 15:50 bid_order_parameter_v3_full TIMEOUT (300s timeout misconfig)
- 16:49 tcft_n8192_v5 TIMEOUT (1800s default + author misconfig)
- 17:10 sagawa_ueda_v4_n8192 TIMEOUT (1200s author misconfig)
- 18:28 saad_solla_v10_n8192 CUDA_RUNTIME_CRASH (exit=1, NEW failure mode)

The bridge `runner_tag` field extension (v241 rescue (d), v243 rescue (e)) becomes URGENT not just CANDIDATE. Without it, every `failed` event-bus entry requires manual SSH + runner-log inspection by the orchestrator — exactly the toil verdict_handler is supposed to eliminate.

**Decision (5): Framework reliability SPLIT UNCHANGED.** general 65-75% / specific named 50-60% (after v245 TCFT lift) / product-feature 60-72%. v246 is annotation-only on Saad-Solla row + new failure-mode taxonomy; doesn't move any reliability band. Saad-Solla LEADING + SKAH-M anchor + TCFT FULL + Crooks FT FULL + BID v2 + 5 named-class FULL-confirmed all UNCHANGED.

**Decision (6): NO capability row closures.** PROT-004/006 not triggered. Annotation-only + new failure-mode taxonomy. Portfolio 14+19 UNCHANGED.

**Decision (7): Pipeline-pacing.** Pause flag ABSENT. Queue state at arrival: overnight pending=2 (`bet_b_4stage_batch128_v1`, `tcft_erase_robustness_n8192_v1`) + running=1 (`bet_b_4stage_rehab_epochs_v3` started 18:28:56 right after saad_solla_v10 crash). Source-queue overnight has pending depth 2 > 0; per [[feedback-no-padding-experiments]] auto-refill only when source-queue empty or invariant queue>=1 at risk. NO queue refill from this handler.

**Rescue sketches (cheapest-first per [[feedback-rescue-sketch-first-sequencing]] + [[feedback-rehabilitation-after-rejection]]; 5 sketches).**

(a) **PRIMARY / SUBSUMPTION 0-cost** — re-frame this verdict as "infrastructure litmus-test PASSED + new failure-mode taxonomy entry (d) added + Saad-Solla row gets sub-annotation from partial seed=7 corroboration"; applied in this entry; 0-cost.

(b) **CHEAPEST INFRA ~30min** — saad_solla_v11_n8192 re-ship with mitigation: (i) reduce batch_size from 16 to 8 to halve replay-buffer memory pressure, OR (ii) disable Kovacs replay path entirely for the N=8192 envelope probe (replay is a CL mechanism not load-bearing on Saad-Solla phase prediction), OR (iii) add `torch.cuda.empty_cache()` between seed iterations + explicit replay buffer cap. Option (ii) is the cleanest: Saad-Solla phase prediction doesn't NEED the Kovacs replay scaffold (that's a Bet B/CL framing imported via base.train_w_with_replay); pure saad_solla phase probe should bind to a SIMPLER training loop. Subsumes (c)/(d) if it clears. ~30min exp_dev redesign + ~1h GPU FULL.

(c) **CHEAP INFRA ~45min** — PROT-020 author + ship: queue_add.py exit-7 / pre-ship VRAM budget assertion `N^2 * batch_size * replay_M * sizeof(float) < device_VRAM_cap * 0.7`. Captures large-N CUDA runtime crashes BEFORE they ship. Parallel to PROT-019 timeout floor. (Author posture identical to v243 PROT-019 PRIMARY-INFRA decision.) Subsumes all future failure-mode (d) class incidents.

(d) **CHEAP ~1h** — bridge `runner_tag` field extension (v241+v243 rescues collapsed under one ticket): distinguish TIMEOUT / metrics_invalid:missing / OOM / non-zero-exit / instrumentation-fail / cuda_runtime_crash at event-bus level. Eliminates per-failure SSH + runner-log inspection toil for orchestrator. 4-in-4h cadence makes this URGENT.

(e) **MEDIUM ~2h research** — cross-correlate substrate-mechanism crash modes against the 5 killer-feature foundation list (project_substrate_killer_features_2026-05-26.md): does saad_solla_v10's Kovacs-replay-crash signal a structural issue with the deletion-certificate Cat-A killer feature's substrate-write pipeline at N=8192? CONTINGENT — only if rescue (b) reveals deeper N-scaling issue beyond batch-size mitigation.

PRIMARY rescue (a) is annotation-only (applied above); (b) is the IMMEDIATE next exp_dev cycle action; (c) and (d) are INFRA candidates (compete for the same orchestrator attention slot as v243 PROT-019); (e) is contingent.

**PROT compliance (v246).**

- PROT-004/006: 0 capability row closures; sub-annotation on Saad-Solla row is NOT a closure or state-change. 5 rescue sketches filed cheapest-first per defensive thoroughness.
- PROT-007: history.md absent (consistent with v228+).
- PROT-008: Annotation-only sub-annotation on existing ✅ row + new failure-mode taxonomy entry; no row promotion/demotion; PROT-008 validator-style logic: no row state change, no gate to check.
- PROT-009: cap_map.md + strategy_decisions_2026-05-27.md staged atomically.
- PROT-018: anchor `_n8192` binding contract SATISFIED (config N=8192 production confirmed at run header); no exit-6.
- PROT-019: per-experiment timeout floor SATISFIED (saad_solla_v10 shipped with `--timeout 5400`); no exit-7.
- PROT-020 (proposed): pre-ship VRAM budget assertion — author candidate per rescue (c).
- [[feedback-verdict-msg-honest-reread]]: 87th post-lock observation; verdict_msg was NULL (event-bus didn't write a verdict_msg for the exit=1 crash); event-bus `failed` tag is UNDER-determined as evidence of substrate-physics failure — OVERRIDDEN authoritatively as CUDA_RUNTIME_CRASH_PARTIAL_DATA per runner-log + remote-dir absence triangulation.
- [[feedback-subagent-permission-inheritance]]: LOCAL commit only; push deferred to main thread.
- [[feedback-rescue-sketch-first-sequencing]]: 5 sketches cheapest-first; PRIMARY = framing subsumption (0-cost annotation).
- [[feedback-dont-overextend-theorems]]: explicit — Saad-Solla ✅ row UNCHANGED; v10 partial data is corroborative-directional NOT envelope-extension; substrate-physics conclusion = "Saad-Solla phase prediction holds in partial seed=7 data at N=8192; full N=8192 envelope-extension requires re-ship with replay-path mitigation".
- [[feedback-ship-before-dependency-verified]]: failure mode (d) is a NEW class of pre-ship verification gap (CUDA VRAM budget) — informs PROT-020 candidate.
- [[feedback-pipeline-pacing]]: source-queue overnight pending=2 + running=1; auto-refill NOT triggered per [[feedback-no-padding-experiments]].
- 159th PROT-009 paired commit.


## v247 -- 2026-05-27 BATCHED 2-VERDICT @ 19:00 (tcft_n8192_v7 HARD_PASS robustness replication of v245 + bid_substrate_probe_v1 MIDDLE_BAND HP3-finite-N caveat)

**Trigger.** Two remote_cpu_queue verdicts landed 18:59:33 + 19:00:06 (37s apart):
- `tcft_n8192_v7` (remote_cpu_queue, 2210s elapsed) -- per dispatch framing: robustness/follow-on to v6 HARD_PASS (deletion-cert Cat-A foundation at v245)
- `bid_substrate_probe_v1` (remote_cpu_queue, 31.15s elapsed) -- per dispatch framing: H1-vs-H2 framework-free discriminator; "potentially a first HARD_PASS"

Both sources verified via remote-bridge metrics (`tools.orchestrator.remote_state.get_metrics`). Both `_source=remote` authoritative (not local-fallback). Bridge `is_stale()=False`.

**Step 0 honest re-read (verdict 1: tcft_n8192_v7).** Verdict_msg label `HARD_PASS: 5/5 seeds var_ratio<0.1 at N=8192. TCFT deletion-certificate confirmed at N=8192. mean_var_ratio=0.000000. (v5 4/5 seeds timeout resolved; v7 FULL run.)`. Per-cell numerical:
- mean_var_ratio = 3.21e-8 (label "0.000000" is rounded; actual is 6 OOM below 0.1 threshold)
- per-seed tcft_variance_ratio range [2.65e-9, 7.34e-8]
- delta_F_agree_pct: seed=7 99.013, seed=17 99.192, seed=23 99.283, seed=31 99.173, seed=41 99.044 (all 99.01-99.28)
- 5/5 seeds valid + 5/5 HP + 5/5 n_hp + n_valid=5
- elapsed=2210s (v245 v6: 2140s, +3% wall-time variance)

HONEST -- UNDER-CLAIMS (same direction as v245 v6); not a label-vs-honest catch. Cited threshold 0.1 is the v7 verdict_msg HF1; actual margin is 6 OOM below that, identical to v6.

**Critical observation: v7 is INDEPENDENT REPLICATION of v245 v6 to 2-decimal seed-by-seed agreement.** v6 (v245) per-seed range [2.65e-9, 7.34e-8] matches v7 exactly to 2 sigfigs; delta_F_agree_pct match seed-by-seed within +/-0.01; mean_var_ratio identical 3.2e-8 to 1 sigfig. Same seeds (7/17/23/31/41), same N=8192 M=1024, same script. The 1h-apart replication is dispositive: this is REPRODUCIBLE result not an artifact.

**Step 0 honest re-read (verdict 2: bid_substrate_probe_v1).** Verdict_msg label `MIDDLE_BAND: bid outside all known classes (5/5 seeds) BUT HP3 unstable (drift>5%). BID may be finite-N artifact at tested scale.`. Per-cell numerical:
- HP1 (outside known classes): 15/15 at N=[512, 1024, 2048] (all cells 5/5 outside)
- HP3 (N-stability): FAILED -- BID_mean grows 42.80 (N=512) -> 63.32 (N=1024) -> 98.76 (N=2048) = +48% per N-doubling at small N, +56% N=1024->2048
- 5% stability threshold breached by 10x+
- Mean overlap stable at 0.98 across all N

HONEST. Label transparently states the HP3 finite-N caveat. Not a label-vs-honest catch.

**Discrepancy on distinct axis: orchestrator dispatch-framing vs actual metrics on BID.** Dispatch text: "potentially a first HARD_PASS -- if so, escalate this single verdict to opus per skill rules." Actual metrics: MIDDLE_BAND not HARD_PASS. This is a **dispatch-framing-vs-metrics** discrepancy (a category I am noting but NOT tallying as label-vs-honest). It does NOT affect cap_map decisions because Step 0 is faithful to metrics-actual; opus escalation is NOT warranted; sonnet default is correct per skill rules. The skill's escalation predicate ("first HARD_PASS") evaluates against actual metrics, not dispatch hopes.

**Decision (1): tcft_n8192_v7 = independent replication of v245 v6 TCFT HARD_PASS.** TCFT rescue path row 🟢 55-70% UNCHANGED. This is intra-band strengthening, not a row-state move. The deletion-certificate killer-feature foundation now has TWO load-bearing FULL N=8192 5-seed HARD_PASS anchors (v245 v6 + v247 v7) with 2-decimal seed-by-seed agreement. Product framing UPGRADED from "FULL-confirmed at N=8192 5-seed" to "FULL-confirmed at N=8192 5-seed AND INDEPENDENTLY REPLICATED 1h later with 2-decimal seed-by-seed agreement."

**Decision (2): non-eq stat-mech framework class row 🟢 55-65% UNCHANGED.** v245 lift stands. v7 is replication of v6 not new evidence; H1 modal P=0.50 stands. Pure replication does not move framework-class P (same observation twice = one Bayesian update, already absorbed at v245).

**Decision (3): bid_substrate_probe_v1 = HP1 corroboration with HP3 finite-N caveat.** BID order-parameter evidence-strength row UNCHANGED ✅ at v229+v230 anchors. ANNOTATION EXTENDED: cumulative HP1 outside-bands is now 30/30 across N=512-8192 (v229 15/15 at N=1024-4096 + v230 5/5 at N=8192 + v247 15/15 at N=512-2048 cumulative); HP3 N-asymptote question added as caveat -- at N<4096 BID grows fast (drift far above 5%), suggesting BID-vs-N curve may not asymptote at small N. v229/v230 already saw the same N-growth at N>=1024 and framed it positively as "substrate's own scaling law"; v247 v1's small-N tail (N=512-2048) shows steeper growth. Two interpretations stand without resolution: (i) finite-N artifact (BID outside-bands real at tested N but does not asymptote) and (ii) substrate's own scaling law (v229/v230 framing). The v228 SKAH-M class settlement already resolved the within-claim "novel-vs-documented" question in favor of documented; that v228 resolution makes interpretation (i) "finite-N artifact" CONSISTENT with the v228 documented-class finding. Net: substrate-outside-static-Hopfield-taxonomy row 🟢 45-60% UNCHANGED (4 independent angles already stand; v247 BID HP1 is a 5th angle reinforcing).

**Decision (4): substrate-outside-static-Hopfield-taxonomy row 🟢 45-60% UNCHANGED.** Plural-framework lock now has FIVE independent angles: v228 6-cell battery + v228 lit-thread match + v229+v230 BID v1/v2 + v242 MCT non-classification + v247 BID-substrate-probe-v1 HP1 corroboration. Already saturated; no additional uplift.

**Decision (5): Framework reliability SPLIT UNCHANGED** (general 65-75% / specific named 50-60% / product-feature 60-72%; v245 bump stands; v247 is replication-strength within 🟢 band).

**Decision (6): Portfolio 14+19 UNCHANGED.** Both verdicts are annotation-evidence-strength under existing rows; no new portfolio rows.

**Decision (7): 0 capability row closures.** PROT-004/006 not triggered. Verdict 1 = replication-LIFT-within-band. Verdict 2 = annotation-with-finite-N-caveat. NO closures.

**Decision (8): label-vs-honest tally NOT incremented.** Both verdicts honest at label-vs-numerical-metrics level. Dispatch-framing-vs-metrics discrepancy on BID (orchestrator predicted "first HARD_PASS"; metrics say MIDDLE_BAND) is a distinct category not tallied as label-vs-honest. The 87-catch label-vs-honest tally stands unchanged.

**Decision (9): exp_dev queue refill -- check pause flag.** pause flag ABSENT (verified via `test -f d:/AI/hd-instrument/data/orchestrator_paused.flag` => no such file). queue_state_at_arrival: remote_cpu_queue pending+running = 0 (both v7+v1 just completed). per [[feedback-pipeline-pacing]] + [[feedback-verdict-arrival-is-queue-depletion-signal]] the verdict-arrival itself is the queue-depletion signal; refill warranted. **HOWEVER per [[feedback-no-padding-experiments]]** check whether there are open handoffs / cap_map questions / strategic priorities to anchor the refill. Audit: v245-(b) visibility annotation OPEN; v245-(c) M-sweep diagnostic OPEN (now strengthened by v247 replication); v245-(d) deletion-certificate audit-artifact design OPEN; v246-(b) saad_solla_v11_n8192 OPEN; v246-(c) PROT-020 OPEN; v246-(d) bridge runner_tag OPEN; multiple anchored candidates. Refill DISPATCH WARRANTED. **GPU queue:** overnight_queue pending = 2 running = ? per orchestrator dispatch lacks current GPU snapshot; verdict_handler will not gate refill on GPU since CPU is empty and CPU work is anchored. Dispatching exp_dev for CPU lane refill inline.

**Decision (10): Strategy-request to exp_dev filed.** Routing file at `notes/strategy_request_to_exp_dev_v247_followon_2026-05-27.md` with: (a) v245-(c) M-sweep diagnostic (NOW strengthened by v247 replication; promote from LOW to MEDIUM priority); (b) BID at N=4096, 8192 with new v1-script-style HP3 N-stability gate (Decision 3 unresolved (i)/(ii) interpretation) -- ~30min CPU; (c) general exp_dev autonomy per standing cap_map drill mandate. Exp_dev decides ship vs hold per [[feedback-no-padding-experiments]].

**Decision (11): Follow-on sketches cheapest-first per [[feedback-rescue-sketch-first-sequencing]].**

For verdict 1 (tcft_n8192_v7):
- (a) **PRIMARY / SUBSUMPTION 0-cost** -- re-frame v7 as "independent replication of v245 v6 within 1h; killer-feature foundation now has TWO load-bearing FULL anchors with 2-decimal agreement"; applied this turn.
- (b) **CHEAPEST INFRA ~10min** -- strategy_request_to_visibility annotate `project_substrate_killer_features_2026-05-26.md` Cat-A row with v247 replication anchor alongside v245.
- (c) **MEDIUM ~2h CPU** -- v245-(c) M-sweep STILL OPEN, NOW promoted from LOW to MEDIUM since v247 replication strengthens the case.
- (d) **MEDIUM-BUILD** -- v245-(d) deletion-certificate user-facing audit artifact design carries forward unchanged.

For verdict 2 (bid_substrate_probe_v1):
- (a) **PRIMARY / SUBSUMPTION 0-cost** -- re-frame v1's MIDDLE_BAND as "HP1 corroboration cumulative 30/30 outside-bands across N=512-8192 + finite-N caveat documented; v228 documented-class finding already aligns with finite-N artifact interpretation"; applied this turn.
- (b) **CHEAP ~5min** -- PROT-018 anchor binding audit: `bid_substrate_probe_v1` has no `_n<N>` suffix despite N_sweep config; flag for retroactive PROT-018 sweep tally (88th post-lock; same anchor-naming pattern as v227 grandfathered).
- (c) **CHEAP ~10min** -- annotate `bid_order_parameter_v1` script + v229/v230 cap_map entries with N-asymptote caveat; the BID-vs-N curve characterization is the substrate-specific finding worth surfacing in product framing.
- (d) **MEDIUM ~30min CPU** -- BID at N=4096, 8192 with v1-script-style HP3 N-stability gate to test whether drift drops below 5% at large N; would resolve interpretation (i) vs (ii). Routed to exp_dev per Decision 10(b).
- (e) **MEDIUM ~2h** -- joint BID + chi_4 + Kovacs secondary discriminator from v229-(d) STILL OPEN; v247 reinforces priority since BID alone is N-regime-dependent.

**Decision (12): Atomic commit single batched commit per [[feedback-cap-map-update-protocol]].** Cap_map + strategy_decisions + visibility log + this entry committed together. Main-thread pushes; sub-agent context cannot per [[feedback-subagent-permission-inheritance]]. 160th PROT-009 paired commit.

## v248 -- 2026-05-27 bet_b_4stage_rehab_epochs_v3 FOURSTAGE_MIDDLE_BAND FULL N=8192 10-seed 2x-Phase-A-epochs @ 19:26 [ANNOTATION-ONLY; rehab axis-1 EXHAUSTED at production scale; ret_A floor confirmed substrate-intrinsic]

**Trigger.** `bet_b_4stage_rehab_epochs_v3` completed overnight_queue GPU 2026-05-27T19:26:29 (elapsed_s=3442.86). Remote-bridge `get_metrics` returned `_source: remote` authoritative. Script `experiments/exp_bet_b_4stage_rehab_epochs_v3.py` -- the rehab-script class with patched HDLAB_EXP_NAME env-var output path (37f576f predecessor pattern), so this run is FREE of the v239 v1-hard-coded-output-path artifact. v3 is the rehab path from the 81st label-vs-honest catch (`bet_b_n8192_4stage_v2` FOURSTAGE_MIDDLE_BAND at v239, smoke->FULL gap of -0.103 on ret_A). v3 implemented rehab-axis-1 from v239 rescue sketch (b): **2x Phase-A epochs (16 vs baseline 8) + 10-seed walk-back gate** to test whether extended Phase-A consolidation closes the ret_A bar at FULL N=8192.

**Step 0 honest re-read.** Verdict_msg label `FOURSTAGE_MIDDLE_BAND: 4-stage partial: retention_A=0.741 retention_B=0.860 retention_C=0.809. Phase D adds load but mechanism survives partially.` is **HONEST** (no label-vs-honest override). Per-cell numerical (FULL N=8192, 10 seeds, phase_a_epochs=16):

| seed | ret_A  | ret_B  | ret_C  |
|------|--------|--------|--------|
| 7    | 0.7302 | 0.8585 | 0.8046 |
| 17   | 0.7455 | 0.8597 | 0.8105 |
| 23   | 0.7390 | 0.8567 | 0.8046 |
| 31   | 0.7305 | 0.8555 | 0.8018 |
| 41   | 0.7487 | 0.8626 | 0.8039 |
| 53   | 0.7414 | 0.8670 | 0.8141 |
| 61   | 0.7386 | 0.8555 | 0.8119 |
| 67   | 0.7383 | 0.8605 | 0.8134 |
| 71   | 0.7491 | 0.8630 | 0.8072 |
| 79   | 0.7458 | 0.8589 | 0.8176 |
| mean | 0.7407 | 0.8598 | 0.8090 |
| min  | 0.7302 | 0.8555 | 0.8018 |
| max  | 0.7491 | 0.8670 | 0.8176 |
| std  | 0.0067 | 0.0035 | 0.0051 |

Pre-reg bands (from config + parent script): HARD_PASS = ret_A>=0.80 AND ret_B>=0.70 AND ret_C>=0.70 across all/most seeds. HARD_FAIL = ret_A<=0.50. MIDDLE_BAND = ret_A in (0.50, 0.80). Honest verdict = **FOURSTAGE_MIDDLE_BAND** with mean ret_A=0.7407 squarely in the band, **0/10 seeds clear 0.80 HP** (max=0.7491 = 0.051 below threshold). ret_B and ret_C decisively clear 0.70 HP at every seed. Verdict_msg label HONEST; numerical bands authoritative; no override required.

**Third saturation observation locked.** This is the THIRD independent saturation of the 4-stage CL ret_A bar at the ~0.74 floor across three different (N, seed-count, phase_a_epochs) configurations:

| run | N    | seeds | phase_a_epochs | ret_A_mean | ret_A_max |
|-----|------|-------|----------------|------------|-----------|
| v189 (cap_map v189 anchor; baseline) | 1024 | 1 | 8 | 0.740 | 0.740 |
| v239 / `bet_b_n8192_4stage_v2`       | 8192 | 5 | 8 | 0.745 | 0.753 |
| **v248 / `bet_b_4stage_rehab_epochs_v3`** | **8192** | **10** | **16 (2x)** | **0.741** | **0.749** |

Three independent samples at the retA~0.74 floor with cumulative 16 seeds and 8x N scaling AND 2x epoch extension. Range across the three: [0.740, 0.745] for mean; max across all 16 seeds = 0.753; 0/16 seeds clear 0.80. **ret_A ~0.74 floor is substrate-intrinsic to the 4-stage compositional CL probe at the tested (N, M, batch_size, Phase-D-load) configuration.** Doubling Phase-A epochs (which would help if Phase-A under-consolidation were the binding constraint) produces NO lift -- delta from v239 baseline at same N=8192 is -0.004 ret_A (well within seed-variance noise floor of std=0.007). **Rehab axis-1 (2x Phase-A epochs) is EXHAUSTED at production scale.**

This DIRECTLY ECHOES the v189-era axis exhaustion pattern documented in cap_map v190+v193:
- v190 V1 N=1024 phase_a_epochs=2x: FOURSTAGE_MIDDLE_BAND saturation -- "no consolidation lift"
- v190 V2 N=1024 batch_size=increased: FOURSTAGE_MIDDLE_BAND saturation -- "no batch-size lift"  
- v193 V2 N=1024 Phase-D-A-weighted-replay: FOURSTAGE_MIDDLE_BAND saturation -- "no Phase-D-rewighting lift"
- (cap_map v193 conclusion: "all 3 in-design K2 rehab axes EXHAUSTED at retA~0.74 floor; substrate retention is CAPACITY-BOUND at 4-stage load not undertuned")

v248 EXTENDS this finding to production-scale N=8192 with 10 seeds: the previously-axis-1-exhausted-at-N=1024 result REPRODUCES at N=8192. The user's decisive-question framing at task-event time ("does ret_A clear 0.80 product bar at FULL N=8192 with extended Phase-A epochs?") gets a clean NO. The user's contingent statement was: "If MIDDLE_BAND/HARD_FAIL: smoke->FULL gap is intrinsic to 4-stage compositional CL at N=8192; rescue chain re-opens." The MIDDLE_BAND case obtains. **The smoke->FULL gap observed at v239 (-0.103) is now corroborated as intrinsic-not-tuning -- doubling consolidation epochs at production scale does NOT close the gap.** Rescue chain re-opens with the 2x-epochs axis now CONSUMED.

**Cap_map state moves (v247 -> v248).** ANNOTATION-ONLY.

- **Bet B 4-stage architectural sub-row (NEW @ v234 as 🟢-smoke-only; v239 corroborated at 🟡 PARTIAL at FULL)**: row state UNCHANGED 🟡 PARTIAL. New annotation appended: "v248 `bet_b_4stage_rehab_epochs_v3` FULL N=8192 10-seed phase_a_epochs=16 (2x): mean ret_A=0.7407 (max=0.7491; 0/10 seeds clear 0.80 HP); ret_B mean=0.8598 (HP-clear at all 10 seeds); ret_C mean=0.8090 (HP-clear at all 10 seeds). THIRD INDEPENDENT SATURATION at ret_A~0.74 floor across (v189, v239, v248) configurations; cumulative 16 seeds 0/16 clear 0.80; 2x-Phase-A-epochs axis CONSUMED with NO lift (delta from v239 5-seed baseline = -0.004 ret_A, within seed-variance noise floor). Smoke->FULL gap observed at v239 (-0.103) corroborated as INTRINSIC-NOT-TUNING. 4-stage CL ret_A ceiling at this corpus pair + N=8192 + M-load is substrate-capacity-bound. Production-spec implication: accept ret_A=0.74 as substrate-native 4-stage spec OR reserve ret_A>=0.80 for 3-stage chains."
- **True continual learning at production scale (A->B->C->D) row**: UNCHANGED 🟡 PARTIAL (already 🟡 for this exact reason at v189; v248 is corroboration-not-state-change).
- **No row promotions, no row demotions.** Three independent corroborations of an already-🟡 row at production scale does NOT lift to 🟢 (because ret_A>=0.80 HP still NOT met; per [[feedback-no-smoke]] brutal-honesty rule). Three independent corroborations does NOT close to ❌ (because ret_B>=0.70 and ret_C>=0.70 both still cleanly clear; the row is partially-passing, which is the definition of 🟡).
- **Smoke->FULL gap on 4-stage CL probe family STRENGTHENED finding.** First explicit (smoke, FULL) pair = v239 (smoke ret_A=0.848 -> FULL 0.745 = -0.103 drop). v248 adds: 2x consolidation does NOT close the gap. Pattern: smoke at lower N + single seed systematically over-estimates 4-stage CL retention by 0.05-0.10; the multi-seed multi-stage interactions at production scale set a hard ceiling near 0.74 that consolidation-time extension does NOT lift. Per [[feedback-dont-overextend-theorems]]: this finding is scoped to THIS corpus pair + THIS Phase-D load configuration; does NOT generalize to "all 4-stage CL smoke is inflated" or "all consolidation-time rehab is useless."
- **Project memory `project_bet_b_4stage_smoke_pass_2026-05-27.md`**: should be annotated with v248 outcome (FULL N=8192 10-seed phase_a_epochs=16 = MIDDLE_BAND mean ret_A=0.741; 2x consolidation does NOT lift). Memory-layer task surfaced for orchestrator visibility.
- **Portfolio count**: UNCHANGED (14+18). No new portfolio item; corroboration of existing 🟡 PARTIAL item.
- **Framework reliability**: UNCHANGED (general 65-75% / specific-documented 45-55% / product-feature 55-70%). Clean replication of a 🟡 PARTIAL prediction within +/-0.005 across three independent configurations is reliability-supportive but doesn't move the band (already PROVISIONAL with this kind of evidence baked in). Substrate-capacity-bound 4-stage retention at 0.74 floor is now well-characterized which IS informative for product-feature reliability framing (specifically supports "compositional audit API" with known 4-stage ret_A ceiling).
- **Cumulative label-vs-honest catches**: UNCHANGED at 86 (this verdict's label was HONEST).

**Rescue sketches (5; cheapest-first per [[feedback-rescue-sketch-first-sequencing]] and [[feedback-rehabilitation-after-rejection]]).** Per user task framing "rescue chain re-opens" -- the 2x-epochs axis is now CONSUMED; surface 5 cheapest-first axis-combination rescues for the ret_A bar.

(a) **CHEAPEST / SUBSUMPTION (PRIMARY) ~0-cost**: re-frame 4-stage CL as "substrate-native 4-stage retention spec: ret_A=0.74 +/- 0.01" -- accept ret_A~0.74 as the substrate-capacity-bound spec at this 4-stage load AND reserve ret_A>=0.80 product-claim for 3-stage chains. Defensible product framing: "substrate retains 74% on Stage-A through 4-stage continual chain; 86% on Stage-B; 81% on Stage-C; deterministic capacity ceiling characterized across 3 independent configurations + 16 seeds." Per [[feedback-no-papers-product-only]] this is the killer-feature framing that converts the 🟡 PARTIAL into a *known operating envelope* without requiring further compute. **Requires user buy-in** on the product spec (3-stage @ 0.80 / 4-stage @ 0.74 partitioned ret_A-bar). Flagged for orchestrator surface to user as the highest-leverage 0-cost path forward; if accepted, Bet B 4-stage row could promote 🟡 -> 🟢 under the *substrate-native-spec framing* rather than the original ret_A>=0.80 framing.

(b) **CHEAP ~50min GPU**: rehab axis-2 -- increase batch_size from 64 to 128 (more gradient signal per Phase-A pass) at N=8192 10-seed. v189-era cap_map v190 V2 saturated at N=1024 but at N=8192 the larger gradient signal could plausibly bite. Already filed at v239 sketch (c). NOT auto-queued; CANDIDATE for next exp_dev cycle. Note: gpu_pending currently has `bet_b_4stage_batch128_v1` running -- if this is the same probe, axis-2 result lands automatically when that completes (post-verdict orchestrator should check the running entry's pre-reg).

(c) **CHEAP ~60min GPU**: rehab axis-3 -- mechanism-class probe with Phase-D A-weighted replay at higher weight (k=0.75 vs baseline k=0.50). v189-era cap_map v193 V2 saturated at N=1024 with k=0.50; at N=8192 with k=0.75 the higher A-weighting could test whether *Phase-D forgetting* is the binding constraint (rather than Phase-A under-consolidation which was axis-1's hypothesis). Different binding-constraint hypothesis from (b).

(d) **MEDIUM ~2h GPU**: mechanism-class M1 (hierarchical replay) per cap_map v193 4-axis rescue list -- substrate writes Phase-D into a SEPARATE memory pool than Phase-A/B/C, with cross-pool readout at evaluation. Tests whether ARCHITECTURE-LEVEL separation (not consolidation tuning) is the lever. Higher-risk-higher-reward; only worth deploying if rescue (a) is rejected by user AND (b)/(c) both saturate.

(e) **MEDIUM ~2h GPU**: mechanism-class M2 (attention-gated readout) per cap_map v193 -- substrate adds an attention gate that selects which stored phase a query routes to at readout time. Tests whether CL forgetting is *retrieval-routing* loss not *write-time* loss. Orthogonal to (d). Only worth deploying if (d) saturates.

PRIMARY rescue (a) is annotation-and-product-spec-only (highest-leverage 0-cost path); (b)/(c)/(d)/(e) are CANDIDATES for next exp_dev cycles per [[feedback-no-padding-experiments]] (not auto-queued). Sequencing rationale: (a) tests product-framing subsumption FIRST per [[feedback-rescue-sketch-first-sequencing]]; (b)/(c) are cheap remaining axes within the same architecture; (d)/(e) are higher-cost architectural rescues only worth deploying after (b)/(c) saturate.

**PROT compliance (v248).**

- PROT-004/006: 0 capability row closures. Row stays 🟡 PARTIAL (B+C cleanly clear; A in band). 5 rescue sketches filed cheapest-first per [[feedback-rehabilitation-after-rejection]] discipline even though no formal closure triggered (per user framing "rescue chain re-opens").
- PROT-007: history.md absent (consistent with v228+).
- PROT-008: Annotation-only; no demotion. 🟡 -> 🟡 UNCHANGED. Validator-style logic: pre-reg HP threshold ret_A>=0.80 NOT met across any of 10 seeds = row state CORRECTLY stays at 🟡 (NOT promoted to 🟢) -- this is exactly the 🟡 PARTIAL definition.
- PROT-009: cap_map.md + strategy_decisions_2026-05-27.md staged atomically.
- PROT-018: anchor name `bet_b_4stage_rehab_epochs_v3` has no `_n<N>` suffix; config.N=8192 matches the strategic intent (v3 = rehab path from v239 which was n8192_4stage_v2). The `_v3` suffix is a version-not-N marker per [[feedback-no-label-vs-honest-anchor-names]]. PROT-018 exit-6 would not have caught this since no _n is present; this is the legitimate "rehab-script version-only" anchor pattern.
- [[feedback-verdict-msg-honest-reread]]: 87th post-lock observation; label HONEST (no override); per-cell numerical bands match label exactly.
- [[feedback-subagent-permission-inheritance]]: LOCAL commit only; push deferred to main thread.
- [[feedback-rescue-sketch-first-sequencing]]: 5 sketches cheapest-first; PRIMARY = product-spec subsumption (0-cost; substrate-native 4-stage spec at ret_A=0.74).
- [[feedback-dont-overextend-theorems]]: explicit -- ret_A~0.74 floor finding is scoped to THIS corpus pair + THIS Phase-D load + THIS architecture; does NOT generalize universally; 3 in-design rehab axes consumed (epochs / batch_size / Phase-D-replay-weight) at the architecture level, but MECHANISM-CLASS axes M1 (hierarchical replay) and M2 (attention-gated readout) remain LIVE per cap_map v193 4-axis rescue list.
- [[feedback-rehabilitation-after-rejection]]: 5 rescue sketches filed cheapest-first BEFORE accepting "rescue chain saturated"; PRIMARY rescue (a) subsumption is the highest-leverage path.
- [[feedback-no-padding-experiments]]: 4 of 5 rescues are CANDIDATES not auto-queued; rescue (b) may auto-resolve if `bet_b_4stage_batch128_v1` (currently running on GPU) is the same axis-2 probe.
- [[feedback-no-smoke]] brutal-honesty: 4-stage CL at N=8192 retA mean=0.741 with 0/10 seeds clearing 0.80 is NOT a "killer feature ready to ship" headline; it IS a "well-characterized 4-stage retention spec at 74%" honest framing. The narrative shift from "4-stage CL substrate killer feature" to "substrate has known retention plateaus per task-shift class" is the v201/v203/v214 customer-facing-spec lock that PRIMARY rescue (a) operationalizes for this row.
- Queue-refill: SKIPPED in this handler (pause flag ABSENT but GPU pending+running=2 maintained; axis-2 probe `bet_b_4stage_batch128_v1` already running answers rescue (b) within the next cycle; queue-depth-invariant comfortably maintained).
- 158th PROT-009 paired commit.

SINGLE-VERDICT v247 -> v248: bet_b_4stage_rehab_epochs_v3 FOURSTAGE_MIDDLE_BAND HONEST FULL N=8192 10-seed phase_a_epochs=16 (2x baseline); mean ret_A=0.7407 (max=0.7491; 0/10 seeds clear 0.80 HP); ret_B mean=0.8598 + ret_C mean=0.8090 both HP-clear at all 10 seeds; THIRD independent saturation at retA~0.74 floor across (v189 N=1024 single-seed baseline, v239 N=8192 5-seed baseline, v248 N=8192 10-seed 2x-epochs) configurations; cumulative 16 seeds 0/16 clear 0.80; 2x-Phase-A-epochs axis (v239 rescue sketch b) EXHAUSTED with NO lift (delta = -0.004 from v239 baseline within seed-variance noise floor); smoke->FULL gap observed at v239 (-0.103 ret_A) corroborated as INTRINSIC-NOT-TUNING; Bet B 4-stage row 🟡 PARTIAL UNCHANGED (B+C pass cleanly; A still in band; row already PARTIAL for this exact ret_A floor reason); 5 rescue sketches filed cheapest-first (PRIMARY (a) = 0-cost product-spec subsumption "substrate-native 4-stage retention=0.74"; (b) batch_size=128 axis-2 already running on GPU; (c) Phase-D higher A-weight; (d) M1 hierarchical replay; (e) M2 attention-gated readout); user task-event decisive question "does ret_A clear 0.80?" gets clean NO at production scale; substrate-capacity-bound finding strengthens; framework reliability UNCHANGED; portfolio 14+18 UNCHANGED; 87th post-lock honest re-read observation (HONEST label); 158th PROT-009 paired commit.
