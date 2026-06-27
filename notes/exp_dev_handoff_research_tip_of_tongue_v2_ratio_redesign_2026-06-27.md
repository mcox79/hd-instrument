# exp_dev hand-off — research: tip-of-tongue v2 ratio criterion redesign

**Filed by:** research (Opus 4.7) 2026-06-27
**Trigger:** Skunkworks audit a0534a89 / commit 22f8d905 ruled `meta_knowledge_tip_of_tongue_v1` TEST_DESIGN_FAILURE per META_RULE_AA fairness-before-tier. Research drill 2x at `d:/AI/hd-instrument/notes/research_drill_2x_tip_of_tongue_criterion_redesign_2026-06-27.md` delivers TOP-1 = Option C (ratio criterion) with brain-grounding.

**Pause state:** check `d:/AI/hd-instrument/data/orchestrator_paused.flag` before dispatch. If paused, file as queued anchor; do not ship.

**Per [[feedback-no-experiment-design-in-prompts]]:** research delivers WHY + WHAT (criterion choice, thresholds, brain-grounding). exp_dev owns HOW (cell authoring, smoke gate, dispatch). The research note's "Cheap decisive test" section is operational guidance, NOT a finished cell spec.

---

## Anchor candidates (rank-ordered)

### ANCHOR 1 (TOP-1): `meta_knowledge_tip_of_tongue_v2_ratio_smoke`

- **Anchor pointer:** redesign of `experiments/exp_meta_knowledge_tip_of_tongue_v1.py`
- **Substrate-product reading:** Wave-2 metacognitive primitive #1 — TOT detection unblocks lateral-retrieval recovery loop (M3 conversational glass-box dependency)
- **Tier hint:** SMOKE first; if HARD_PASS, queue Wave-2 chain-grade with V_ATOMS=2000 n=3 seeds 5000 queries per arm
- **Why-now:** v1 smoke ALREADY ran the codebook construction (HC=1.000, LC=0.992 are real); criterion is post-hoc on signal stream that's already engineered correctly. Cheapest possible redesign — ~22 sec laptop CPU.
- **P_deflated:** 0.42

### ANCHOR 2 (TOP-2): `meta_knowledge_tip_of_tongue_v2_absolute_smoke`

- **Anchor pointer:** parallel variant testing absolute thresholds (Discr_B)
- **Substrate-product reading:** fallback if ratio criterion has substrate-specific numerator/denominator instability
- **Tier hint:** can be evaluated AS A THIRD ARM inside ANCHOR 1's cell (Discr_v1, Discr_B, Discr_C on same query stream — zero added compute). Recommend MERGE into ANCHOR 1 unless exp_dev judges separation cleaner.
- **Why-now:** same query-stream piggyback; provides robustness check on Option C
- **P_deflated:** 0.32

### ANCHOR 3 (REJECTED — do not ship): per-SNR-bin quantile (Option A)

- **Reason:** circular w/ diag_tot_rate_vs_snr arm; embeds the falsification axis into the discriminator (BIAS-13 contamination). Research note section (d) details refutation.

---

## Context pointers (file paths only — no summaries)

- Research note (load-bearing; read end-to-end): `d:/AI/hd-instrument/notes/research_drill_2x_tip_of_tongue_criterion_redesign_2026-06-27.md`
- v1 source (preserve codebook construction VERBATIM; change only criterion): `d:/AI/hd-instrument/experiments/exp_meta_knowledge_tip_of_tongue_v1.py`
- v1 metrics (compare against; v2 must agree on peak-SNR within ±1 sweep step): `d:/AI/hd-instrument/data/exp_meta_knowledge_tip_of_tongue_v1_smoke/metrics.json`
- META_RULE_AA fairness pattern (apply self-check pre-dispatch): `d:/AI/hd-instrument/notes/META_FAIRNESS_PATTERN_wave1_test_design_failures_2026-06-27.md`
- Predispatch verifier (mandatory pre-flight): `d:/AI/hd-instrument/tools/predispatch_check.py meta_knowledge_tip_of_tongue_v2_ratio`
- META_RULE_AC discipline (hypothesized vs measured tagging): per research note final section

---

## Contract section

1. **Pre-dispatch:** run `python d:/AI/hd-instrument/tools/predispatch_check.py meta_knowledge_tip_of_tongue_v2_ratio` to check for prior dispatch + recent-HARD_FAIL re-dispatch (Fix #26).
2. **Author cell** preserving v1 codebook + query-stream construction verbatim. Add Discr_B and Discr_C as parallel evaluations on the same query stream. Per META_RULE_H, declare `EXPECTED_N_UNITS_SMOKE = 4 arms * 2 seeds * 300 = 2400`; HARD_FAIL_CARDINALITY_BREACH if observed < expected.
3. **Pre-reg bands** from research note section (c) — pin verbatim into the cell `CONFIG_VERSION` and `HP_*` constants. Critical: peak-SNR-interior AND Discr_C peak-TOT >= 0.30 AND cluster_acc_in_TOT @ peak >= 0.65 AND HC_recall >= 0.80 AND LC_refuse >= 0.90 AND Discr_C vs Discr_v1 peak agreement ±1 sweep step.
4. **Smoke gate** before full: confirm Discr_C fires (NOT just verify cell runs) per three smoke disciplines [[feedback-three-smoke-disciplines]]. Smoke at full smoke-N (no further reduction).
5. **Self-test mode** (`--self-test`) preserved from v1 structure.
6. **Dispatch** via `queue_add.sh` — laptop CPU is fine (cell runs ~22 sec; remote GPU is overkill).
7. **Post-ship REMOTE VERIFY** per Fix #17 — confirm metrics.json landed with cardinality_ok=true.

## Autonomy declaration

- exp_dev owns: cell authoring style, exact threshold constants if minor calibration is needed, self-test specifics, dispatch target queue, smoke vs full sequencing
- exp_dev does NOT change: codebook construction (preserved from v1); brain-grounded discriminator definitions (Discr_C ratio > 2.0 with cluster_cos floor 0.30; Discr_B absolute bands); pre-reg HP bands above; SNR sweep (preserve v1's `[0.2, 0.3, 0.5, 0.7, 1.0]` so peak-comparison is apples-to-apples)
- Research delivers WHY + WHAT (this hand-off + research note). HOW is yours.

## Cascading work (queue after ANCHOR 1 lands)

- If HARD_PASS: Wave-2 `meta_knowledge_tot_lateral_retrieval_v1` (TOT-fire triggers cluster-mate proposal; brain-grounded metacognitive recovery loop)
- If HARD_FAIL but Discr_v1 / Discr_B HARD_PASS: file as Discr_C-refuted; ship Discr_B as the canonical criterion
- If all three HARD_FAIL: substrate cannot distinguish TOT from random — escalate to research for codebook re-design drill (Wave-2 deeper cluster hierarchy)
- If MIDDLE_BAND: queue Wave-2 chain-grade with V_ATOMS=2000 n=3 seeds Q=5000
