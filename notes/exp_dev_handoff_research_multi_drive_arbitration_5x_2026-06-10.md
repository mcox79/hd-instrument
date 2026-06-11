# exp_dev hand-off -- research: multi-drive arbitration 5x drill

Filed-by: research sub-agent
Date: 2026-06-10
Trigger: notes/research_drill_multi_drive_arbitration_5x_2026-06-10.md
Urgency: HIGH -- Sprint 2 INTEGRATION-ALGEBRA+FLOW reported WEAK; 5 competing drives cannot be cleanly arbitrated; concrete mechanism candidates now available for empirical test.

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

### Anchor 1: drive_frustration_index_diagnostic_v1

Anchor pointer: Research note Section F3 Test 4 (Frustration Index Diagnostic)
Substrate-product reading: Given the 5 Sprint 2 drives, hand-specify the 5x5 compatibility matrix C and compute the frustration index F = (frustrated triangles) / C(5,3). F < 0.2 routes to softmax arbitration (simplest); F = 0.2-0.5 routes to BG-analog lateral inhibition; F > 0.5 routes to active inference or Bayesian posterior. This gates all other anchors.
Tier hint: Local CPU, < 5 min compute (mostly design work to specify compatibility matrix). CHEAPEST. Must run first as it routes subsequent implementation decisions.
Why-now: The frustration structure of the drive set determines which of the 10 math systems (F2.1-F2.10) is needed. Without this, exp_dev risks implementing the wrong mechanism.

Pre-reg bands:
  HARD-PASS: F < 0.2 (softmax suffices; simple to implement)
  MIDDLE-BAND: F = 0.2-0.5 (BG-analog WTA needed; Anchor 2 is the fix)
  HARD-FAIL: Not applicable -- any F value is informative and routes to an actionable mechanism.

### Anchor 2: bg_analog_lateral_inhibition_v1

Anchor pointer: Research note Section F2.2 + Section F3 Test 2
Substrate-product reading: Implement the BG-analog selection rule output_i = u_i - lambda * mean(u_{j!=i}) for K=3-5 drives. Test on 3 canonical scenarios: (a) dominant drive u_1=0.9, others=0.1; (b) two-way tie u_1=u_2=0.5, u_3=0.1; (c) all-equal u_i=1/K. Measure: selection accuracy on scenario (a), tie-detection on scenario (b), conflict-flag trigger on scenario (c). Lambda sweep in {0.5, 1.0, 1.5}.
Tier hint: Local CPU, < 2 hr. Run after Anchor 1. Does not require substrate modifications -- salience vector and urgency scores are existing substrate outputs.
Why-now: BG-analog has the highest P_deflated (0.38) among all 10 candidate mechanisms and is the most tractable implementation for Sprint 2 integration fix.

Pre-reg bands:
  HARD-PASS: Dominant drive selected with >= 85% accuracy on scenario (a); lambda calibration within {0.5, 1.5} range; scenario (c) conflict flag fires.
  MIDDLE-BAND: Accuracy 60-85%; lambda requires per-drive-pair calibration.
  HARD-FAIL: Accuracy < 60% on scenario (a), OR lambda requires search > 1 order of magnitude outside {0.5, 1.5}.

### Anchor 3: conflict_detector_acc_analog_v1

Anchor pointer: Research note Section B4 + Section F3 Test 1
Substrate-product reading: Implement ACC-analog conflict detector: conflict = sum_{i!=j} s_i * s_j where s_i is the salience of drive i (dot product of drive query vector with its best substrate candidate). Validate: conflict peaks when two drives are equally urgent AND their action candidates are near-orthogonal. Test on 100 synthetic drive vector pairs drawn from the existing substrate codebook.
Tier hint: Local CPU, < 30 min. Can run in parallel with Anchor 2.
Why-now: Conflict detector is needed as a gating signal for the BG-analog mechanism: only engage full lateral inhibition when conflict is above threshold. Without conflict detection, the BG-analog runs on every query, adding unnecessary overhead for single-drive scenarios.

Pre-reg bands:
  HARD-PASS: Conflict score peaks (> mean + 2 std) when u_i ~ u_j AND cos(a_i, a_j) < 0.3.
  MIDDLE-BAND: Conflict peaks for equal urgency but not conditioned on action orthogonality (partial detector).
  HARD-FAIL: Conflict signal is constant regardless of urgency distribution or action similarity.

### Anchor 4: boltzmann_drive_energy_v1

Anchor pointer: Research note Section F2.1 + Section F3 Test 3
Substrate-product reading: Construct a K=5 drive energy function using substrate similarity scores as v_i(a). Set compatibility matrix c_ij from frustration diagnostic result (Anchor 1). Run 100 Gibbs sampling steps at T=1.0. Measure: number of distinct stable states; frequency of incompatible drive co-activation; energy landscape entropy (flat vs structured).
Tier hint: Local CPU, < 4 hr. Run only if Anchor 2 HARD-FAILS or MIDDLE-BAND with accuracy < 70%.
Why-now: Boltzmann mechanism handles compatibility structure explicitly (via c_ij) whereas BG-analog uses only urgency magnitudes. If BG-analog fails due to complex compatibility structure (e.g., F > 0.5), Boltzmann is the next natural implementation.

Pre-reg bands:
  HARD-PASS: >= 5 distinct stable states across 100 seeds; incompatible drive co-activation < 5% of samples; energy landscape has clear structure (std > 0.1 * mean).
  MIDDLE-BAND: 2-4 stable states; incompatible co-activation 5-15%.
  HARD-FAIL: Energy landscape flat (< 2 stable states) OR incompatible co-activation > 20%.

### Anchor 5: tensor_product_drive_representation_v1

Anchor pointer: Research note Section F2.10 + Section F3 Test 5
Substrate-product reading: Store K=5 drive fillers in a tensor product representation (N=1024, orthogonal role vectors). Retrieve each filler via inner product with its role vector. Measure SNR = norm(retrieved - true) / norm(true) for each drive. Verify that the soft weighted mean of fillers is a valid substrate query vector (similarity to intended target >= similarity threshold).
Tier hint: Local CPU, < 1 hr. Independent of other anchors; can run anytime.
Why-now: If Sprint 2 requires simultaneous partial activation of multiple drives (not WTA), tensor product representation is the cleanest compositional mechanism. SNR < 0.05 would make it a no-cost extension of existing VSA infrastructure.

Pre-reg bands:
  HARD-PASS: SNR < 0.05 for all K=5 drives; weighted mean vector similarity to target >= 0.7.
  MIDDLE-BAND: SNR < 0.20 (usable with noise); mean vector similarity 0.5-0.7.
  HARD-FAIL: SNR > 0.30 OR role vectors cannot be made sufficiently orthogonal in practice.

---

## Context pointers (file paths, not summaries)

- Research note (this drill): d:/AI/hd-instrument/notes/research_drill_multi_drive_arbitration_5x_2026-06-10.md
- Sprint 2 integration context: review cap_map for INTEGRATION-ALGEBRA+FLOW row
- Prior sprint 1 synthetic gap: d:/AI/hd-instrument/notes/research_drill_synthetic_vs_real_prediction_gap_2x_2026-06-07.md
- Production architecture lock: C:/Users/marsh/.claude/projects/d--AI/memory/production_architecture_locked_2026-06-07.md
- Post-compaction brief (exp_dev): d:/AI/hd-instrument/notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-09_evening.md

---

## Contract section

This handoff proposes 5 anchor candidates. Exp_dev selects from these based on current queue state, runner availability, and pause flag. Exp_dev does NOT need to implement all 5.

SEQUENCING CONSTRAINT: Anchor 1 (frustration diagnostic) MUST run before Anchor 2 (BG-analog) and Anchor 4 (Boltzmann). Anchor 1 gates the routing decision. Anchors 2, 3, and 5 can run in parallel once Anchor 1 is complete. Anchor 4 runs only if Anchor 2 HARD-FAILS or MIDDLE-BAND < 70%.

PRIORITY ORDER: 1 -> (2 and 3 in parallel) -> 4 (conditional) -> 5 (independent).

---

## Autonomy declaration

Exp_dev is autonomous in:
- Choosing which anchors to dispatch first (subject to sequencing constraint above)
- Choosing cell grid dimensions, seed counts, and specific parameter values for each anchor
- Choosing local CPU vs remote CPU routing per feedback_route_gpu_vs_cpu_by_torch_not_N.md
- Writing experiment scripts following feedback_metrics_required_fields_write_metrics.md
- Deciding whether to implement BG-analog or Boltzmann based on frustration index F from Anchor 1

Exp_dev is NOT autonomous in:
- Making cap_map decisions from verdicts (orchestrator / verdict_handler owns this)
- Declaring the Sprint 2 integration mechanism "fixed" without orchestrator confirmation
- Modifying the production architecture lock
- Specifying which drives are the Sprint 2 drives (this requires user or orchestrator direction)
