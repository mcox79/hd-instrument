# exp_dev hand-off -- research: substrate-native coordination 3x drill

Filed-by: research sub-agent
Date: 2026-06-07
Trigger: notes/research_drill_substrate_native_coordination_3x_2026-06-07.md
Urgency: MEDIUM -- v1 architecture direction (coordinator design); not blocking current experiments but informs distributed deployment decisions

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

### Anchor 1: bundle_relay_fault_tolerance_v1

Anchor pointer: Research note Section 2 Pattern A + Section 5 HARD-PASS/HARD-FAIL
Substrate-product reading: Measures retrieval accuracy degradation as a function of shard dropout rate (0%, 10%, 30%, 50%). Validates that accuracy degrades as sqrt(k/K) (graceful linear degradation) rather than catastrophically (2PC-abort-analog). Demonstrates the pure-relay coordinator in a multi-shard setup.
Tier hint: CPU laptop, ~30-60 min. CHEAPEST. Run first -- gates v1 coordinator design decision.
Why-now: The pure-relay coordinator is the v1 architecture choice (50-LOC coordinator vs ~500-LOC 2PC). This anchor validates that the fault-tolerance claim holds empirically, not just algebraically. If SNR degrades faster than sqrt(k), the algebraic model has a gap that must be found before deployment.

Pre-reg bands:
  HARD-PASS: accuracy at 10% shard dropout >= 0.92 * full-shard accuracy (consistent with sqrt(0.9/1.0) = 0.95 SNR factor); no abort behavior observed
  MIDDLE-BAND: accuracy = 0.85-0.92 at 10% dropout (moderate noise from false positives or threshold effects)
  HARD-FAIL: accuracy < 0.75 at 10% dropout (catastrophic degradation; algebraic model has gap; must investigate before deploying Pattern A)

### Anchor 2: confidence_quorum_snr_v1

Anchor pointer: Research note Section 2 Pattern C + Section 1 Property 8 (formal analysis)
Substrate-product reading: Deploys a multi-shard scenario where some shards know the answer (cosine > 0.70), some don't (cosine < 0.20). Measures whether the bundled answer is dominated by knowing shards. Validates the "implicit quorum" property: null-returning shards contribute exactly zero signal.
Tier hint: CPU laptop, ~30-60 min.
Why-now: Pattern C is the second v1 coordination primitive (alongside Pattern A). Without empirical validation that null-returning shards are genuinely zero-contribution (not small positive noise), the implicit quorum claim is theoretical only.

Pre-reg bands:
  HARD-PASS: bundled answer cosine to correct target >= 0.80 when >= 50% of shards know the answer; below-threshold shards contribute < 0.01 additional noise amplitude to bundle
  MIDDLE-BAND: bundled cosine = 0.60-0.80 (knowing shards still dominate but with visible noise floor from interactions)
  HARD-FAIL: below-threshold shards contribute >= 0.05 noise amplitude OR bundled cosine < 0.60 at 50% knowing-shard fraction (implicit quorum fails; must investigate threshold calibration)

### Anchor 3: bitemporal_bundle_pointintime_v1

Anchor pointer: Research note Section 2 Pattern E + Section 7 v2 implications
Substrate-product reading: Uses the substrate's existing bitemporal addressability to issue a multi-shard point-in-time query (all shards return their as_of(T) bundle). Coordinator sums the bundles. Measures whether the bundled result matches the expected system state at T (some shards may have been updated after T and should NOT contribute post-T facts).
Tier hint: CPU laptop, ~1-2 hr (requires multi-shard setup with write-index tracking).
Why-now: Pattern E (bitemporal bundle) is described as "snapshot-free distributed query." Validating that the write-index rollback per shard composes correctly under bundling is the cheapest confirmation before v2 engineering investment.

Pre-reg bands:
  HARD-PASS: bundled as_of(T) answer exactly matches expected state at T; facts written after T are NOT present in the bundle
  MIDDLE-BAND: as_of(T) matches for >= 90% of queries; <= 10% exhibit post-T fact leakage (timestamp boundary effects)
  HARD-FAIL: post-T fact leakage >= 20% of queries OR coordinator incorrectly sums mixed-time bundles

---

## Context pointers (file paths, not summaries)

- Research note (this drill): d:/AI/hd-instrument/notes/research_drill_substrate_native_coordination_3x_2026-06-07.md
- Chain 3 Drill 3 (noise model): d:/AI/hd-instrument/notes/research_drill_substrate_production_scaling_5x_chain3_drill3_2026-06-07.md
- Chain 3 Drill 1 (scaling gaps): d:/AI/hd-instrument/notes/research_drill_substrate_production_scaling_5x_chain3_drill1_2026-06-07.md
- Federated privacy note (composes with Pattern B): d:/AI/hd-instrument/notes/research_drill_federated_privacy_substrate_2x_2026-06-07.md
- Production architecture lock: C:/Users/marsh/.claude/projects/d--AI/memory/production_architecture_locked_2026-06-07.md

---

## Contract section

This handoff proposes 3 anchor candidates. Exp_dev selects from these based on current queue state, runner availability, and pause flag. Exp_dev does NOT need to implement all 3.

SEQUENCING: Anchor 1 (bundle_relay_fault_tolerance) is cheapest and gates the overall coordinator architecture choice. Run first. Anchors 2 and 3 can run in parallel if queue depth allows.

PRIORITY: Anchor 1 and 2 are v1-relevant (deploy soon). Anchor 3 is v2-relevant (can wait).

---

## Autonomy declaration

Exp_dev is autonomous in:
- Choosing which anchors to dispatch first
- Choosing cell grid dimensions, seed counts, N values (recommend N=4096 or N=16384 for cheap run; N=65536 for validation)
- Choosing number of simulated shards (recommend 10-100 for v1 validation)
- Writing experiment scripts following feedback_metrics_required_fields_write_metrics.md

Exp_dev is NOT autonomous in:
- Making cap_map decisions from verdicts (orchestrator / verdict_handler owns)
- Committing to v1 coordinator architecture before Anchor 1 verdict (orchestrator owns that decision)
- Reopening the PRODUCTION ARCHITECTURE LOCK (requires explicit user authorization)
