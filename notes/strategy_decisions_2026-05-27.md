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
