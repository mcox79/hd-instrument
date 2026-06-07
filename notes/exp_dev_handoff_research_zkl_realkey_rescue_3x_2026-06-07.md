# exp_dev hand-off -- research: ZKL real-key rescue 3x drill

Filed-by: research sub-agent
Date: 2026-06-07
Trigger: notes/research_drill_zkl_realkey_rescue_3x_2026-06-07.md
Urgency: CRITICAL -- absolute HIPAA privacy claim invalidated on real keys; must not be made to customers until rescue path validated

---

## Pause state

Experiments below are PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ANCHOR CANDIDATES only.
Experiment design details (cell grids, hyperparameter values, script paths) are to be authored by exp_dev from the research note + cap_map context. Do NOT treat the descriptions below as implementation specs.

---

## Anchor candidates (rank-ordered)

### Anchor 1: zkl_encoder_correlation_analysis_v1 (R3)

Anchor pointer: Research note Section 1 Hypothesis A + Section 3 R3 (Cheapest Decisive Test)
Substrate-product reading: Measures empirical pairwise cosine between random real-key pairs before and after sign-quantization. If rho_0 > 0.15, Hypothesis A (encoder anisotropy as dominant ZKL leak source) is confirmed and SRHT rescue is warranted. If rho_0 < 0.05, routes to sign-quant isolation.
Tier hint: CPU laptop, ~1 hr. CHEAPEST. Must run first -- gates all other rescue paths.
Why-now: The 11x ZKL gap from cycle 151 is unexplained at mechanism level without this measurement. All downstream engineering decisions (SRHT, mean-centering, encoder swap) depend on knowing rho_0.

Pre-reg bands:
  HARD-PASS: rho_0 (continuous) = 0.15-0.35; rho_bip = (2/pi)*arcsin(rho_0) matches within 20%
  MIDDLE-BAND: rho_0 = 0.05-0.15 (partial anisotropy; mixed rescue needed)
  HARD-FAIL: rho_0 < 0.05 (Hypothesis A refuted; route to R4)

### Anchor 2: zkl_realkey_k_sweep_full_v1 (R2)

Anchor pointer: Research note Section 3 R2
Substrate-product reading: Full k-sweep {1, 10, 40, 50, 100, 500, 1000, 5000} on real encoder keys. Characterizes ZKL(k) shape and confirms or denies the linear-regime prediction (ZKL(k) ~ 0.008*k for k < 105). Determines whether ZKL(40) ~ 0.32 (honest claim possible as tiered) or worse.
Tier hint: CPU laptop, ~2 hr. Run second (can run in parallel with R3 if both cheap enough).
Why-now: Needed to issue honest tiered customer claim. Even without engineering rescue, knowing ZKL(k) shape lets the product team write defensible language about the rate-limited adversary posture.

Pre-reg bands:
  HARD-PASS: ZKL(40) < 0.30 AND sublinear growth (beta < 0.8) across k <= 500
  MIDDLE-BAND: linear growth k <= 100, saturation 0.40-0.60 at k > 100
  HARD-FAIL: ZKL(40) > 0.50 OR super-linear growth at any k range

### Anchor 3: zkl_rag_comparison_realkeys_v1 (re-measurement of cycle 150 zkl_substrate_vs_rag_v1)

Anchor pointer: Research note Section 7 (23x advantage analysis)
Substrate-product reading: Re-run zkl_substrate_vs_rag_v1 comparison on REAL encoder keys for both substrate and RAG. Confirms or denies whether 23x synthetic-key advantage survives on real keys. Critical: research analysis (Section 7) shows the 23x may be REVERSED because RAG exact-match member score is preserved while substrate bipolar member score degrades by (2/pi).
Tier hint: CPU laptop, ~2-4 hr. HIGH URGENCY -- 23x is a customer-facing claim.
Why-now: If 23x reverses on real keys, this is a MAJOR product claim correction that must be made before any regulated-industry customer conversations.

Pre-reg bands:
  HARD-PASS: ZKL_RAG_real / ZKL_substrate_real >= 10 (relative advantage survives)
  MIDDLE-BAND: ratio = 5-10 (degraded but still favorable)
  HARD-FAIL: ZKL_RAG_real / ZKL_substrate_real < 5 (relative advantage collapses or reverses)

### Anchor 4: zkl_srht_mixing_v1 (R1 engineering)

Anchor pointer: Research note Section 3 R1 + Section 6 (R1 SRHT predictions)
Substrate-product reading: Implement SRHT post-quantization mixing and measure ZKL(50) on real encoder keys. If ZKL(50) < 0.05 with SRHT, HIPAA absolute threshold is defensible at k=50.
Tier hint: CPU laptop, ~3-5 days engineering + ~2 hr CPU validation. GATE: run only after R3 confirms rho_0 > 0.15.
Why-now: R1 is the highest-priority engineering fix for the ZKL product line. Uses existing Hadamard infrastructure (cycle 150 context). Decouples privacy isotropy from encoder architecture choice.

Pre-reg bands:
  HARD-PASS: ZKL(50) with SRHT < 0.05 (full rescue; HIPAA threshold defensible)
  MIDDLE-BAND: ZKL(50) with SRHT = 0.05-0.20 (partial rescue; combine with M2 mean-centering)
  HARD-FAIL: ZKL(50) with SRHT > 0.20 (SRHT insufficient; d_eff >> 100; M5 or encoder swap needed)

### Anchor 5: zkl_mean_centering_ablation_v1 (M2 quick win)

Anchor pointer: Research note Section 3 M2
Substrate-product reading: Estimate cone mean mu_cone from calibration queries (output of R3 anchor); subtract from all keys at write/query time; measure ZKL(50).
Tier hint: CPU laptop, ~1-2 days engineering + ~1 hr CPU validation. Zero runtime overhead after calibration. Can run in parallel with R1 SRHT.
Why-now: If mean subtraction gives 50%+ ZKL reduction, it is a zero-overhead quick win deployable immediately ahead of the full SRHT engineering cycle.

Pre-reg bands:
  HARD-PASS: ZKL(50) after mean-centering < 0.15
  MIDDLE-BAND: 0.15-0.30 (partial; confirms cone is primary structure but not perfectly mean-aligned)
  HARD-FAIL: ZKL(50) > 0.30 (multi-modal cone; SRHT needed regardless; mean-centering alone insufficient)

---

## Context pointers (file paths, not summaries)

- Research note (this drill): d:/AI/hd-instrument/notes/research_drill_zkl_realkey_rescue_3x_2026-06-07.md
- Cycle 151 verdict context: d:/AI/hd-instrument/notes/orchestrator_to_research_results_summary_2026-06-06_cycle151.md
- Cycle 150 verdict context (ZKL launch): d:/AI/hd-instrument/notes/orchestrator_to_research_results_summary_2026-06-06_cycle150.md
- Federated privacy note: d:/AI/hd-instrument/notes/research_drill_federated_privacy_substrate_2x_2026-06-07.md
- Prior ZKL handoff: d:/AI/hd-instrument/notes/exp_dev_handoff_research_ZKL_Certificate_10h_battery_2026-06-07.md
- Production architecture memory: C:/Users/marsh/.claude/projects/d--AI/memory/production_architecture_locked_2026-06-07.md

---

## Contract section

This handoff proposes 5 anchor candidates. Exp_dev selects from these based on current queue state, runner availability, and pause flag. Exp_dev does NOT need to implement all 5.

SEQUENCING CONSTRAINT: R3 (zkl_encoder_correlation_analysis_v1) MUST run before R1 SRHT (zkl_srht_mixing_v1). R3 gates the R1 decision. R2 and R3 can run in parallel if queue depth permits.

GATING: zkl_rag_comparison_realkeys_v1 (Anchor 3) is EQUALLY HIGH URGENCY as R3. If the 23x reversal is real, it changes the product story more than the absolute HIPAA threshold.

---

## Autonomy declaration

Exp_dev is autonomous in:
- Choosing which anchors to dispatch first (subject to sequencing constraint above)
- Choosing cell grid dimensions, seed counts, and parameter values for each anchor
- Choosing local CPU vs remote CPU routing per feedback_route_gpu_vs_cpu_by_torch_not_N.md
- Writing experiment scripts that follow the feedback_metrics_required_fields_write_metrics.md convention

Exp_dev is NOT autonomous in:
- Making cap_map decisions from verdicts (orchestrator / verdict_handler owns this)
- Making customer-facing claim revisions (orchestrator owns after verdicts are in)
- Reopening the PRODUCTION ARCHITECTURE LOCK (requires explicit user authorization)
