# exp_dev hand-off -- research: irreducible multi-drive probe 2x

Filed-by: research sub-agent
Date: 2026-06-11
Trigger: notes/research_drill_irreducible_multidrive_probe_2x_2026-06-11.md
Urgency: HIGH -- the "96% irreducible" claim is an engineering deficit, not a fundamental
  limit. Seven substrate-native rescue mechanisms identified, all testable cheaply.
  The top two (M2: CES utility rho=-1, M6: VSA policy encoding H=3) each take < 2 hr
  CPU and are pre-registered with HARD-PASS/HARD-FAIL thresholds.

---

## Pause state

Experiments below are PROPOSED, not queued. Pause gate applies per normal exp_dev
protocol. Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ANCHOR CANDIDATES only.
Experiment design details (cell grids, hyperparameter values, script paths) are to be
authored by exp_dev from the research note + cap_map context. Do NOT treat the
descriptions below as implementation specs.

---

## Anchor candidates (rank-ordered)

### Anchor 1: ces_utility_harmonic_integration_v1

Anchor pointer: Research note Section "PROBE D: GOAL REFRAMING" + Section "CHEAP DECISIVE TEST: TEST 1"
Substrate-product reading: Replace the linear integration operator sum_k w_k * s_k with
CES utility U = (sum_k s_k^rho)^{1/rho} at rho=-1 (harmonic mean) and rho=-0.5
(intermediate). Compare worst-drive satisfaction vs linear baseline and vs temporal-policy
result (0.094). The harmonic mean is the mathematical approximation to maximin that is
smooth and differentiable, backed by Martinez et al ICML 2020 for minimax Pareto fairness.
Tier hint: Local CPU, < 30 min. NO new architecture needed -- one-line change to the
integration operator. CHEAPEST possible test; must run first.
Why-now: This is the highest-P_deflated substrate-native rescue that requires zero new
infrastructure (P_deflated=0.42). If it HARD-PASS, the "irreducible" framing is
immediately falsified with minimal engineering cost.

Pre-reg bands:
  HARD-PASS: CES_harmonic worst-drive >= 0.12 (>= 28% lift over temporal-policy 0.094)
  MIDDLE-BAND: 0.09-0.12 (marginal improvement; proceed to Anchor 2)
  HARD-FAIL: < 0.09 (no improvement; CES adds nothing for this drive structure)

### Anchor 2: vsa_policy_encoding_multistep_v1

Anchor pointer: Research note Section "PROBE A: LONG-HORIZON TEMPORAL POLICY" + Section "CHEAP DECISIVE TEST: TEST 2"
Substrate-product reading: Encode a 3-step temporal policy as a single VSA composite
vector using temporal role vectors r_t (orthogonal). At each step t, retrieve the action
by querying the composite with r_t. Measure worst-drive average satisfaction over the
3-step horizon. Theory predicts 3x-5x lift over single-step alternation (PP-348 result).
Tier hint: Local CPU, < 2 hr. Can run in parallel with Anchor 1.
Why-now: This is the HIGHEST P_deflated substrate-native rescue overall (P_deflated=0.45).
It extends the proven PP-348 temporal-policy result from alternation to TRUE multi-step
planning. The VSA encoding is substrate-native (role-vector binding is a demonstrated
primitive). Planning horizon H=3 is the minimal non-trivial case.

Pre-reg bands:
  HARD-PASS: worst-drive (3-step avg) >= 0.15 (>= 60% lift over single-step 0.094)
  MIDDLE-BAND: 0.10-0.15 (moderate improvement; test H=5 next)
  HARD-FAIL: < 0.10 (VSA policy encoding loses critical action information)

### Anchor 3: vsa_policy_horizon_sweep_v1

Anchor pointer: Research note Section "SUBSTRATE-PRODUCT IMPLICATIONS, item 4"
Substrate-product reading: Sweep planning horizon H in {2, 3, 5, 10} for VSA policy
encoding. Measure worst-drive average satisfaction at each H. Theory predicts saturation
around H = K (for K=5 drives, H=5 should approach the per-drive maximum). This
characterizes the H-vs-satisfaction curve and sets the product-level minimum horizon.
Tier hint: Local CPU, < 4 hr total for H={2,3,5,10}. Run only if Anchor 2 HARD-PASS.
Why-now: The H-saturation point determines the computational budget needed for session-
level fairness. If saturation is at H=5, the full architecture is very affordable. If
saturation requires H=20+, the design changes.

Pre-reg bands:
  HARD-PASS: worst-drive saturates (< 10% improvement) at H <= 7
  MIDDLE-BAND: saturation at H 7-15 (manageable but not cheap)
  HARD-FAIL: no saturation up to H=10 (worst-drive still climbing; deeper planning needed)

### Anchor 4: ces_horizon_combined_v1

Anchor pointer: Research note Section "HONEST REASSESSMENT" -- combined mechanisms
Substrate-product reading: Combine CES utility (rho=-1) with multi-step temporal policy
(H=3). Measure combined worst-drive satisfaction. Theory predicts additive lift: if CES
alone gives +30% and temporal policy alone gives +60%, combined should give +80-100%.
Tier hint: Local CPU, < 2 hr. Run only if both Anchor 1 and Anchor 2 HARD-PASS.
Why-now: The research note predicts that CES + temporal policy combined are the strongest
pair of substrate-native rescues. This test determines whether their effects compound or
are partially redundant.

Pre-reg bands:
  HARD-PASS: combined worst-drive >= 0.18 (>= 2x lift over single-step 0.094)
  MIDDLE-BAND: 0.12-0.18 (partial compounding)
  HARD-FAIL: < 0.12 (mechanisms are redundant; CES and temporal policy target same bottleneck)

### Anchor 5: hierarchical_session_fairness_v1

Anchor pointer: Research note Section "PROBE B: HIERARCHICAL DECOMPOSITION" + Section "FALSIFIABLE PREDICTIONS, P3"
Substrate-product reading: Implement the three-level hierarchy (M4) with satiation decay
and deficit tracking (M5). Test: 50 sequential queries with K=5 drives. Track cumulative
worst-drive satisfaction over the session. Measure: does deficit tracking cause the system
to compensate for drives that were starved in earlier queries?
Tier hint: Local CPU, < 4 hr. Run after Anchors 1-2 complete (this tests the full
session-level architecture, while Anchors 1-2 test single-step or short-horizon upgrades).
Why-now: Session-level fairness is the product claim that matters. Instantaneous worst-drive
satisfaction is not the right metric for a deployed system. This test directly measures the
product-relevant outcome.

Pre-reg bands:
  HARD-PASS: cumulative worst-drive over 50 queries >= 0.30
  MIDDLE-BAND: 0.15-0.30 (partial fairness; hierarchy helps but doesn't fully close gap)
  HARD-FAIL: cumulative worst-drive over 50 queries < 0.15 (no better than single-step)

---

## Context pointers (file paths, not summaries)

- Research note (this drill): d:/AI/hd-instrument/notes/research_drill_irreducible_multidrive_probe_2x_2026-06-11.md
- Prior 5x multi-drive arbitration drill: d:/AI/hd-instrument/notes/research_drill_multi_drive_arbitration_5x_2026-06-10.md
- PP-348 temporal policy HARD_PASS metrics: d:/AI/hd-instrument/data/exp_integ_temporal_policy_cpu_v1/metrics.json
- Diagnostic experiment metrics (objective mismatch confirmed): d:/AI/hd-instrument/data/exp_integ_diagnostic_cpu_v1/metrics.json
- Renorm experiment (HARD_FAIL, for context): d:/AI/hd-instrument/data/exp_integ_renorm_t1_cpu_v1/metrics.json
- Post-compaction brief (exp_dev): d:/AI/hd-instrument/notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-09_evening.md

---

## Contract section

This handoff proposes 5 anchor candidates. Exp_dev selects from these based on current
queue state, runner availability, and pause flag. Exp_dev does NOT need to implement all 5.

PRIORITY ORDER: 1 -> (2 in parallel) -> 3 (conditional on 2 HARD-PASS) -> 4 (conditional
on both 1 and 2 HARD-PASS) -> 5 (independent, full-session test).

SEQUENCING CONSTRAINT: Anchor 5 requires a session-simulation framework; run only after
Anchors 1-2 establish which integration operator to use. Anchor 3 requires Anchor 2 HARD-PASS.
Anchor 4 requires both Anchor 1 and Anchor 2 HARD-PASS.

KEY DECISION GATE: If BOTH Anchor 1 AND Anchor 2 HARD-FAIL, report back to Research.
The L1 fundamental limit (instantaneous maximin) may be tighter than estimated; this
would warrant a mechanism-level investigation rather than continued engineering.

---

## Autonomy declaration

Exp_dev is autonomous in:
- Choosing which anchors to dispatch first (subject to sequencing constraint above)
- Choosing cell grid dimensions, seed counts, and specific parameter values
- Choosing local CPU vs remote CPU routing per feedback_route_gpu_vs_cpu_by_torch_not_N.md
- Writing experiment scripts following feedback_metrics_required_fields_write_metrics.md
- Deciding the specific form of the VSA role-vector encoding (there are several valid choices)
- Deciding whether to use Vickrey or proportional softmax for the auction-style tests

Exp_dev is NOT autonomous in:
- Making cap_map decisions from verdicts (orchestrator / verdict_handler owns this)
- Declaring the multi-drive arbitration problem "solved" without orchestrator confirmation
- Modifying the production architecture lock
- Changing the pre-registered HARD-PASS / HARD-FAIL thresholds defined above
