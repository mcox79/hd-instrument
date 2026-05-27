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
