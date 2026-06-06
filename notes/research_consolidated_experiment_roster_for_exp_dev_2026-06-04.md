# Research consolidated experiment roster for Exp-Dev

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Type:** Roster + gap-fill for in-flight/pending/missing experiments

---

## What this is (plain language)

Audit of all experiments referenced in today's research drills + Exp-Dev unblock work + brain-inspired re-evals. Identifies what's on-disk-routed vs only-in-chat. Provides spec for any missing or under-specified items. Establishes priority order so Exp-Dev can dispatch in coherent sequence as CPU/GPU slots free.

---

## Section A -- Fully routed experiments (no action needed)

These have complete disk-ready routings:

| Anchor | Routing | Status |
|---|---|---|
| substrate_trained_mini_lm_readout_fix_N_sweep | routing_substrate_training_n_sweep_readout_fix_2026-06-04.md | DESIGN-READY |
| polynomial-p=4 modern Hopfield (2x2 factorial cells) | change_request_polynomial_p_engineering_2x2_factorial_bcm_informed_2026-06-04.md | ENGINEERING-READY |
| substrate capacity-stress (M-sweep at fixed L=50) | routing_redirect_depth_to_capacity_stress_test_2026-06-04.md | DESIGN-READY |
| Phase 0.5 v1 Rung A (Llama-3.2-1B on 4060 Ti) | change_request_phase05_v1_final_8gb_4060ti_2026-06-03.md | ENGINEERING-READY |
| kappa3_nlo_formula_validation_v1 | (already running per Exp-Dev's note) | RUNNING |
| kappa3_nlo_formula_validation_v2 | research_clarification_noise_model_kappa3_pp50_after_2x_drill_2026-06-04.md + research_answers_to_exp_dev_q1_q2_q3_2026-06-04.md | DESIGN-READY |
| PP-50 N-sweep (Tracy-Widom-vs-Hadamard discriminator) | research_answers_to_exp_dev_q1_q2_q3_2026-06-04.md | DESIGN-READY |
| substrate_modern_hopfield_2x2_factorial_v1 | change_request_polynomial_p_engineering_2x2_factorial_bcm_informed_2026-06-04.md | ENGINEERING-READY |
| q_f5_oscillating_envelope_v2 | (already shipped per Exp-Dev's note) | RUNNING/QUEUED |
| NHSE tau_crit boundary probe | exp_dev_handoff_research_drift_detection_lyapunov_framework_2026-06-04.md (auto-written) | DESIGN-READY |
| NHSE Anchor 2 (per Exp-Dev's note) | (already in Exp-Dev's queue per their status) | QUEUED |

12 experiments fully routed.

---

## Section B -- Missing or under-specified -- spec provided below

These were referenced in research but lack complete disk-ready specs. Filling in here.

### B1. Brain-inspired HF re-evals at higher N (curriculum + ICL + 8channel)

The N=512 mini LM re-eval already ran (HF). The N-sweep (Section A) will cover mini LM at higher N. But the OTHER 3 brain-inspired HFs (curriculum + pre-loaded ICL + 8channel orchestration) were never re-routed at higher N. The original readout-fix routing covered all 4 at N=512; should extend to higher N for the remaining 3.

**Decision: route as low-priority follow-ups after the 2x2 factorial (Section A) lands.**

Rationale:
- The 2x2 factorial isolates architectural variables (p, write mode). If it HP at p=4 episodic, the same architecture should rescue curriculum + ICL + 8channel.
- If 2x2 factorial reveals which architectural change is binding, apply that to the other 3 tasks rather than running them all separately.
- Don't pre-commit to 12 more cells (3 tasks × 4 N values) before the 2x2 factorial verdict guides the design.

**Anchor names (when dispatched, post-factorial-verdict):**
- `substrate_curriculum_learning_post_factorial_v1`
- `substrate_preloaded_icl_post_factorial_v1`
- `substrate_8channel_orchestration_post_factorial_v1`

Cell list TBD per factorial outcome:
- If p=2 episodic alone rescues: run 3 tasks at N=512 p=2 episodic
- If p=4 episodic required: run 3 tasks at N=512 p=4 episodic
- If neither rescues: 3 tasks stay HF; surface to research for redesign

Estimated wall when dispatched: ~3-4h CPU total.

### B2. Spectral monitor Tier 2 -- erank(Cov(h)) + Hessian trace primitives

My prior routing (`routing_spectral_monitor_full_cycle_reframe_2026-06-04.md`) had Tier 2 as "future engineering" without explicit cell spec. Filling in now.

**Anchor name:** `substrate_full_cycle_phase_monitor_v1_n4096`

**Cells:**
- 4-layer char-LM, ~50-100k params, N=4096 substrate
- TRAIN_CHARS=200k (sufficient to reach val_overfit; v3 already validated 400k works)
- N_STEPS=8000
- Three substrate primitive channels measured per training step (every 50 steps):
  - Existing: weight kappa_2 / kappa_3 / kappa_4_excess
  - NEW: erank(Cov(h_t)) of residual activations (standard linear algebra; ~2h engineering)
  - NEW: Hessian trace proxy via Hutchinson estimator (Hessian-vector product; PyHessian-class library; ~2-4h engineering)
- 3 seeds

**Measurements:**
- Per-channel lead/lag time at convergence onset (val_loss curve crosses convergence threshold)
- Per-channel lead/lag time at overfitting onset (val_loss curve diverges)
- Per-channel signal noise ratio

**Pre-reg HP/MID/HF:**
- **HP:** erank(Cov(h)) leads val_loss convergence by >= 15 steps (3/3 seeds) AND Hessian trace leads convergence by >= 10 steps AND weight kappa retains >= 200 step overfitting lead
- **MIDDLE:** partial coverage (one phase leads cleanly, other lags)
- **HF:** erank lead < 5 steps OR Hessian trace shows zero lead (refutes Drill B 3x prediction)

**Engineering scope:** ~4-6h (erank: 2h; Hutchinson Hessian trace: 2-4h; integration: 1h). All CPU. $0.

**Sequencing:** dispatch AFTER 2x2 factorial verdict. If factorial HP at p=4, run Tier 2 at p=4 architecture; if factorial HF, run Tier 2 at classical p=2 + current substrate scale.

### B3. Anti-Hebbian kappa_3 sign-signature empirical (future cap_map annotation)

The kappa_3-NLO drill noted: `kappa_3(W_eff) = alpha_write - gamma^3 * alpha_repulse` when anti-Hebbian active repulsion is engaged. Empirical test would measure this signature directly.

**Decision: defer to future cycle.** Not urgent; cap_map annotation candidate; lower priority than substrate-as-training-mechanism resolution.

**If dispatched in future:**
- Anchor: `substrate_anti_hebbian_kappa3_signature_v1_n8192`
- Test: measure kappa_3 with and without anti-Hebbian repulsion at varying gamma
- Predicted: kappa_3 with repulsion = alpha_write - gamma^3 * alpha_repulse (negative signed contribution from anti-Hebbian term)
- HP: linear fit of kappa_3 vs gamma^3 gives correct slope = -alpha_repulse within 20%
- HF: kappa_3 doesn't scale as gamma^3 (substrate doesn't follow formula)

Engineering: ~2-4h. CPU. $0.

### B4. DeltaNet Design B fallback -- conditional dispatch update

My prior routing (`routing_deltanet_pattern_fallback_design_b_2026-06-04.md`) had this as "conditional on joint D+H HF." Joint D+H has been REPLACED by the 2x2 factorial design. Update the conditional:

**Updated condition:** dispatch DeltaNet Design B fallback ONLY IF:
- 2x2 factorial all 4 cells (B + C + D + E) HF
- AND no other rescue path (curriculum + ICL + 8channel post-factorial re-evals all HF)
- AND substrate-as-training-mechanism story still needs an empirical anchor

Per the DeltaNet routing, scaffold pre-staging (~4-6h) can happen in parallel with the 2x2 factorial; dispatch only on the dual-HF condition above.

---

## Section C -- Future drill candidates (not yet empirical experiments)

These are research-next-step candidates flagged by today's drills. NOT empirical experiments to queue; documenting for completeness.

| Candidate | Source drill | Priority |
|---|---|---|
| Tracy-Widom edge fluctuations sharpening | Drill B 3x | Medium (after spectral Tier 2 lands) |
| Free-probability F4 kappa_n higher-order resummation | kappa3-NLO 2x | Medium (deepens noise-sensitivity characterization) |
| NESS hidden objective for substrate (Maes-Netocny non-eq) | META 3x+ | High (potentially dissolves Constraint 2 if hidden scalar exists) |
| Eigenvalue convergence under bounded episodic write | BCM-SNR 2x | High (validates 2x2 factorial algebraic prediction) |
| Sparse-coding-compressed-sensing RIP transitions | Grouped 2x | Low (deepens bipolar quantization analysis) |
| Three-factor discrete STDP on bipolar Hopfield | Multiplicative gating 2x | Medium (Klampfl-Maass extension) |
| Modern Hopfield exponential capacity bridge | Modern Hopfield 3x | Medium (after p=4 empirical) |

---

## Section D -- Recommended dispatch sequence

Given CPU queue guard (pending <= 5) and current CPU running state:

**Wave 1 (cheap empirical; high information per hour):**
1. kappa3-NLO v2 (build + dispatch; ~1-2h CPU per cell)
2. PP-50 N-sweep (build + dispatch; ~1-3h CPU per cell)
3. substrate-trained mini LM readout-fix N-sweep (6 cells; ~3-5h sequential)
4. substrate capacity-stress M-sweep (7 cells; ~35 min)
5. NHSE tau-sweep (7 cells; ~2-4h)

**Wave 2 (engineering-then-dispatch; depends on Wave 1 verdicts):**
6. polynomial-p=4 engineering + 2x2 factorial cells (~10-12h engineering + 3-4h experiment)
7. Phase 0.5 v1 Rung A on Llama-3.2-1B (per separate engineering timeline)

**Wave 3 (post-factorial-verdict; conditional):**
8. Spectral monitor Tier 2 (erank + Hessian trace; ~4-6h engineering + ~1h experiment)
9. Brain-inspired HF re-evals at 2x2-informed architecture (3 tasks; ~3-4h)
10. DeltaNet Design B fallback (conditional dispatch only)

**Wave 4 (deferred / future cap_map annotation):**
11. Anti-Hebbian kappa_3 sign-signature empirical
12. Future drill candidates (Tracy-Widom, NESS, etc.)

---

## Section E -- Compute budget summary

All experiments above are $0 (CPU) or already-authorized remote GPU (4060 Ti for Phase 0.5 v1 + substrate-physics queue).

NO cloud GPU planned. Per [[feedback-cloud-only-when-absolutely-necessary]].

Total CPU wall budget across all waves: ~30-50h sequential. Faster with parallelism.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-no-padding-experiments]]: each experiment in roster ties to a specific drill finding or empirical question
- Per [[feedback-rescue-sketch-first-sequencing]]: cheapest decisive tests first (Wave 1)
- Per [[feedback-small-scale-first-methodology]]: rung-1 + rung-2 scale throughout; cloud reserved
- Per [[feedback-change-request-protocol]]: this is consolidation, not silent edit; existing routings unchanged
- ASCII-only output

---

**END.**

**Exp-Dev:** roster is consolidated reference. Dispatch by wave order as CPU/GPU slots free. Wave 1 has all builds + specs disk-ready (cross-reference routings cited in Section A). Wave 2 requires engineering. Waves 3-4 are conditional.

**Orchestrator:** informed. Cap_map sub-property founding pending verdicts across waves.

**Research session:** roster captures all my open empirical requests as of 2026-06-04. Standing for Wave 1 verdicts as they land.
