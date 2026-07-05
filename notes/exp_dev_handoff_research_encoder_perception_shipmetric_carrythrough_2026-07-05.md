# exp_dev hand-off — research: encoder/perception ship-metric carry-through

**Filed-by:** research sub-agent, 2026-07-05, per encoder-scope task (USER PRIMARY focus).

**Trigger:** `notes/research_encoder_perception_state_buried_win_shipmetric_carrythrough_2026-07-05.md` — inventory of the step1b BGE-distillation chain surfaced a result that already clears the pre-registered 0.85 semantic-fidelity bar with FHRR algebra fully intact (in-batch-RKD-only arm of `exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1`, 5-seed FULL: spearman-to-teacher mean 0.886 range 0.852-0.897, keyed_roundtrip@J5 = 1.000 all 5 seeds) — but it is buried inside a cell whose AGGREGATE verdict reads HARD_FAIL (driven by a co-located, different-objective arm whose algebra broke). This win has never been separately verdicted, never carried through Step2 (full 970K sparse-encode, smoke-only on disk) or Step3 (100-query gold-verify, the literal ship metric — cosine to the right answer — currently CRASHED on a missing input artifact).

**Pause state:** check `data/orchestrator_paused.flag` at dispatch time. If present, this hand-off still stands (research dispatches are allowed while paused) — exp_dev should treat the cell as queued-but-gated until resume.

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off names the ANCHOR + POINTERS only. exp_dev designs ALL of: exact N/seed count for the carry-through run, queue tier (local/CPU/GPU), smoke profile, FULL profile, whether to re-derive checkpoints from the 5 existing seeds or retrain the (cheapest-in-family) in-batch-RKD-only objective if checkpoints were not persisted to disk, and the exact HARD-PASS/HARD-FAIL bands (the research note pre-registers a recommended set below as a starting point, not a binding spec).

---

## Anchor candidates (rank-ordered)

1. **`exp_encoder_step2step3_inbatch_rkd_shipmetric_carrythrough_v1`** (TOP PRIORITY — near-zero marginal cost, resolves the single highest-value open ambiguity in the encoder program)
   - Anchor pointer: `notes/research_encoder_perception_state_buried_win_shipmetric_carrythrough_2026-07-05.md`, section C.
   - Substrate-product reading: if this HARD-PASSes on the real ship metric (Step3 gold-verify top-1 cosine-to-right-answer), the "can't hit 0.85 natively -> distill from BGE" fallback is not just correct, it may already be effectively SHIPPED with an already-trained checkpoint — no new training run required, only pipeline execution. Directly unblocks M4 (consolidation/attention) sooner than the 07-04 record assumed.
   - Tier hint: local/CPU-plausible — Step2 is a single forward pass of an already-small trained MLP over 970K items (no backprop); Step3 is a 100-query eval harness. Likely does not need GPU unless the 970K forward pass is I/O-bound; exp_dev's call.
   - Why now: the checkpoint already exists (or is trivially re-trainable — cheapest arm in the whole family, no landmark term, no InfoNCE); every other candidate encoder move is either lower-EV (native ceiling ~0.65-0.75, not 0.85) or premature (GSBC graded-code training-recipe program assumes the current block-argmax chain is the binding constraint, which this finding calls into question).
   - Recommended bands (exp_dev may adjust): HARD-PASS top-1 cosine-to-gold >= 0.80 AND composed-query FHRR roundtrip >= 0.95 AND ret-agreement@10 >= 0.30; HARD-FAIL top-1 cosine-to-gold < 0.60 OR composed-query roundtrip < 0.85; MIDDLE_BAND in [0.60, 0.80).
   - P_deflated = 0.42 (lit-scan-calibrated; see research note for full reasoning).

2. **Re-verdict `step1b_v3c` in-batch-RKD arm on its own pre-registered bands** (near-zero cost, should happen regardless of #1's dispatch timing)
   - Anchor pointer: same research note, section A (numeric timeline table) and CROSS-THREAD SYNTHESIS.
   - Substrate-product reading: a metrics-re-read / cap_map annotation fix, not a new experiment — corrects a per-arm-vs-aggregate-verdict masking bug (per [[feedback-fix28-verify-per-arm-metrics-not-summary-verdict-text]]) that has left a passing result invisible for an unknown number of days since the cell landed (single commit, no promotion).

3. **Native RI/BEAGLE-on-KB cheap decisive test** (lower priority, SEPARATE thread, already spec'd elsewhere)
   - Anchor pointer: `notes/research_5x_drill_perception_encoder_spec_and_brain_mechanism_2026-07-05.md`, cell `exp_n11b_random_indexing_kb_native_dualgate_v1`.
   - Substrate-product reading: answers whether teacher-free grounding is viable as a SECOND, complementary encoder family (honest ~0.65-0.75 target, not a 0.85 substitute). Does not gate or block anchor #1.
   - Tier hint: CPU-only, ~1-2 hrs (single-pass co-occurrence accumulation).
   - Why now: lower priority than #1 because it addresses a different, lower-ceiling question; include only if exp_dev has queue bandwidth.

4. **GSBC graded-code training-recipe program (Lever 1+2c: annealed soft-global-top-k + absolute-cosine anchor)** (deprioritized pending #1's outcome, not cancelled)
   - Anchor pointer: `notes/research_drill_graded_global_topk_gsbc_training_recipe_2026-07-04.md`.
   - Substrate-product reading: solves a DIFFERENT problem (cashing a higher ceiling via graded/global-top-k codes on the block-argmax chain) that may not be the binding constraint if #1 HARD-PASSes. If #1 HARD-FAILs or lands MIDDLE, this becomes the next lever, now informed by exactly where the proxy-to-real-metric gap lives.
   - P_deflated = 0.44 (from the source memo; novel-synthesis-capped).

---

## Context pointers (pointers, not summaries)

- `notes/research_encoder_perception_state_buried_win_shipmetric_carrythrough_2026-07-05.md` — this cycle's full inventory + spec (read this first, in full).
- `notes/research_5x_drill_perception_encoder_spec_and_brain_mechanism_2026-07-05.md` — same-day prior drill on native-vs-distilled framing; complementary, not superseded.
- `notes/research_drill_graded_global_topk_gsbc_training_recipe_2026-07-04.md` — GSBC graded-code training-recipe memo (anchor #4).
- `notes/research_drill_sparse_distill_fidelity_lever_ladder_2026-07-04.md` — lever-ladder ranking for the block-argmax/GLOBAL chain's training-fidelity gap.
- `data/exp_encoder_migration_step1b_v3c_paired_rkd_only_seed_{7,13,23,29,31}/metrics.json` — the 5 seed metrics files containing the buried in-batch-RKD win; check adjacent paths for persisted model checkpoints before assuming retrain is required.
- `experiments/exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1_core.py` — source cell to adapt/extend for the carry-through.
- `experiments/exp_encoder_migration_step2_sparse_encode_970K_KB_v1_core.py` — existing Step2 infra (smoke-only; needs the in-batch-RKD checkpoint wired in).
- `experiments/exp_encoder_migration_step3_gold_verify_100_queries_A_B_v1_core.py` — existing Step3 harness (H1-H4 criteria; currently crashes on missing `E_concept.pt` — needs a valid input artifact from a completed Step2 run).
- `preregs/2026-07-04_exp_encoder_migration_step1b_v2_mlp_distill_concept_encoder_v1.md` — prior pre-reg convention to follow for band format.
- `notes/substrate_capability_map.md` v597 — current cap_map state (no v598+ exists); the BGE-distillation step1b chain has no cap_map row yet — this carry-through's verdict would be the first.
- Pause state line: check `data/orchestrator_paused.flag` at dispatch time.

---

## Contract

- Pre-reg per [[feedback-envelope-expansion-fail-bands]]: HARD-PASS + HARD-FAIL bands BEFORE smoke (starting bands recommended above; exp_dev owns final numbers).
- Smoke gate exercises the SAME code path as FULL per [[feedback-smoke-code-path-must-exercise-same-branches]].
- Self-test per [[feedback-formula-selftests]].
- Multi-seed FULL on smoke clearance (the existing 5-seed convention from v3c should carry forward if retraining; if reusing persisted checkpoints, report per-seed metrics individually, not just the mean).
- JOINT gate discipline: per the GSBC training-recipe memo's own META rule, gate on semantic-fidelity AND algebra AND (for this cell) the real ship metric jointly — a rank/spearman win with a real-query miss is a FALSE PASS, not a HARD-PASS.
- Queue routing per Tier A/B/C in `agents/exp_dev.md` Section 0.
- Ship via `bash tools/orchestrator/queue_add.sh <queue> <name> <script> <prereg> <timeout>`.
- POST-SHIP REMOTE VERIFY via queue_add.sh exit code.
- status_log entry with `plain_language` + `importance`.

## Autonomy declaration

exp_dev decides ALL of: whether to reuse persisted v3c seed checkpoints or retrain the in-batch-RKD-only objective, exact N/seed count for the carry-through run, queue tier, ETA, smoke profile, FULL profile, and final HARD-PASS/HARD-FAIL/MIDDLE bands (the research note's bands are a starting recommendation, not binding). If exp_dev's own pre-flight check finds the buried-win claim doesn't hold up under direct re-read of the v3c metrics.json files (independent verification is expected, not optional), that supersedes this hand-off's framing — report the discrepancy rather than proceeding on a stale premise.
