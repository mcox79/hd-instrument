# Visibility decisions 2026-05-27

## 01:00 -- v219: BATCHED 2-VERDICT (RD theoretical-home + UNIFIED SVD-cascade master-mechanism)

Source files: data/exp_wave14_betB_rd_perturbation_recovery_v2/metrics.json (remote, 2119s CPU); data/exp_wave14_unified_svd_cascade_falsifier_v1/metrics.json (remote, 47.2s CPU).

Key: (1) RD theoretical home CLOSED-NEGATIVE — `wave14_betB_rd_perturbation_recovery_v2` exp_fit_r2=0.000 < 0.3 fail threshold, r_inf=0.352 not converging to pre-reg target plateau 0.74, recovery trajectory [0.39, 0.59, 0.59, 0.59, ...] = instant-rebound-plus-flatline (NOT monotone drift, NOT exponential). Pre-reg HARD-FAIL condition met on numerical leg; verbal `monotone drift` label corrected to `instant rebound to actual steady-state 0.595 (target_plateau=0.74 mis-specified)`. (2) UNIFIED master-mechanism SVD-cascade CLOSED-NEGATIVE — `wave14_unified_svd_cascade_falsifier_v1` mean_svd_spacing_error=2.2605 >> 0.15 fail threshold on 5/5 instances; spike-structured singular spectrum (47.6σ / 6.9σ / 5.7σ / 3.99σ / 2.46σ / ...) not equally-spaced ladder; cross_prediction_match=False; smoke prediction CORROBORATED at FULL. (3) Strategic implication: theoretical-home portfolio is genuinely PLURAL — Saad-Solla saddle-cascade ✅ + multi-basin structure 🟢 + 1-RSB hysteresis 🟡 + MoE SHIFT ✅ are INDEPENDENT phase observations, NOT projections of one master mechanism. v216 plural-framework reframe extended and strengthened.

Label-honest override: `wave14_betB_rd_perturbation_recovery_v2` verbal characterization `Monotone drift: no exponential recovery` is NON-LOAD-BEARING mis-description (per [[feedback-verdict-msg-honest-reread]] 57th post-lock observation); numerical HARD-FAIL on r²<0.3 leg is the authoritative signal; cap_map decision based on numerical reading. Pre-reg authors' target_plateau=0.74 is mis-specified — substrate's actual steady-state retention is 0.595; future RD-style probes (if any) should re-pre-reg target plateau as the observed steady-state, not assumed value.

Closures: 2 (RD; UNIFIED SVD-cascade). PROT-004 rescue check: NEITHER closure filed rescue paths — RD is a clean structural NO (no exponential signature shape, period); UNIFIED is a topological structural NO (spike vs equally-spaced is a qualitative difference, not a quantitative gap). Both refutations clean enough that rescues would be straw-arms. 2x research consideration deferred to orchestrator.

v219 local commit complete; push deferred to main thread per [[feedback-subagent-permission-inheritance]] (commit hash to be filled in below).

Framework reliability UNCHANGED 48-62% PROVISIONAL (per v215 lock-down). RD closure removes one rescue candidate from the alternative-theoretical-homes set; UNIFIED rejection is itself a successful pre-registered falsification (smoke prediction held at FULL = methodology evidence FOR pre-reg discipline, not against substrate physics). No directional pressure on the 48-62% band.

Portfolio count UNCHANGED 14 demonstrated + 7 evidence-strength rows. No row-state moves. Annotation-only on theoretical-home framework section.

Routing-ratio compliance: this handler executed inline (Agent tool unavailable in environment per system reminders); standard verdict_handler→strategy+visibility pipeline composed in-thread; status_log written via tools/orchestrator/state.py log_event; cap_map atomic commit via standard Edit/Write tools.
