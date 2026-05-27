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
## 02:29 -- wave14_moe_shift_K_perarm_v1 M2_DOMINANT (cap_map v220)

Verdict: M2_DOMINANT. LSH gating entropy rises K=2:0.78b->K=64:5.32b (pre-reg threshold 3.0b crossed at K=16). M3 IEC max=0.0006 (ruled out). M1 m_cap=0.694 constant (ruled out). K=4 design point reconfirmed (ent=1.60b healthy, ret=0.809). Engineering fix: replace LSH with learned K-NN router. Cap_map v220 annotation-only. MoE SHIFT row unchanged ✅ engineering-rate-limited. Framework reliability 48-62% PROVISIONAL unchanged. Portfolio 14+7 unchanged.

## 05:00 -- wave14_saddle_cascade_plateau_v5_n4096 HARD_PASS (label-vs-honest: N=512 not N=4096)

Verdict HARD_PASS logged. [label-vs-honest] experiment name claimed N=4096 but actual N=512 smoke run (seeds=[17]). Equal-spacing pattern confirmed at N<=512 (r2=0.770, max_dev=0.0855). N-scaling narrative in verdict_msg over-claimed -- no data above N=512 exists in saddle-cascade series. Saddle-cascade row UNCHANGED ✅. Cap_map v221 ANNOTATION-ONLY committed. Genuine large-N FULL run (N>=4096, multi-seed) remains the open next probe.
PLAIN: The substrate's saddle-cascade memory pattern was confirmed again at the N=512 level. However, the experiment name claimed to test N=4096 -- it didn't; the actual run was N=512 smoke only. The 'N-scaling confirmed' narrative is not supported; equal-spacing holds at small N but we haven't yet tested it at the larger scales the experiment name implied.
IMPORTANCE: MEDIUM
