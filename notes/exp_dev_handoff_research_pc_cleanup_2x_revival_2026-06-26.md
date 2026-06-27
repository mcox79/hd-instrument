# exp_dev hand-off -- research: PC cleanup 2x revival drill

**Filed-by:** Research (Opus 4.7 1M)
**Date:** 2026-06-26
**Trigger:** PC cleanup deeper-chains HARD_FAIL (2x revival drill); research note `notes/research_pc_cleanup_2x_revival_drill_2026-06-26.md`
**Pause state:** check `data/orchestrator_paused.flag` before dispatch; if present, this handoff queues but does not ship.

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M_CHAINS, K_top, depth-set, seed count, threshold bands (HARD-PASS + HARD-FAIL), queue choice (Tier A/B/C), ETA, smoke profile, FULL profile, anchor naming. Research provides the mechanism design + pre-reg suggestion + cross-discipline grounding; exp_dev provides the cell.

---

## Anchor candidates (rank-ordered)

### ANCHOR 1 (TOP PRIORITY): pc_cleanup_HARD_COMMIT_with_residual_rewrite_v1

- **Anchor pointer:** `notes/research_pc_cleanup_2x_revival_drill_2026-06-26.md` Section "ANCHOR 1".
- **Substrate-product reading:** the failed PC mechanism contaminated the STATE via soft-bundling. Anchor 1 keeps the state as a clean codeword (vanilla argmax) and uses the residual to drive TRANSIENT W-PLASTICITY for the duration of one chain. Brain-grounded (Rao-Ballard predictive coding; error drives synaptic update, not signal corruption). Signal-processing-grounded (decision-feedback equalization with hard decisions + adaptive equalizer update).
- **Substrate primitives needed:** existing hdlab/predictive_coding.py + NEW `hdlab/transient_W_rewrite.py` (save delta on entry; subtract on chain-end revert).
- **Tier hint:** likely Tier B local_cpu (single primitive + existing cell template `experiments/exp_pc_cleanup_deeper_chains_v1.py` as scaffold; new ARM variant slots into existing arms list).
- **Why now:** brain-grounded; addresses the SHARED failure-mode root cause (state contamination from bundling); P_deflated=0.40; cheap (~3-5 CPU-hr).

### ANCHOR 2: pc_cleanup_TWO_STREAM_energy_descent_v1

- **Anchor pointer:** `notes/research_pc_cleanup_2x_revival_drill_2026-06-26.md` Section "ANCHOR 2".
- **Substrate-product reading:** runs vanilla + a "Viterbi-style" energy-scored shadow stream; at end, take lower-energy result. State never bundles; top-K is used for SCORING not BLENDING. Signal-processing-grounded (Viterbi survivor selection). Materials-physics-grounded (replica-symmetry-broken landscape forbids inter-basin mixing).
- **Substrate primitives needed:** existing codebook_cleanup with top-K (already in the failed cell) + NEW `hdlab/energy_scored_topk.py` (accumulated cosine-energy across chain; survivor selection at end).
- **Tier hint:** Tier B local_cpu, same cell template, second new ARM variant.
- **Why now:** complementary mechanism class to Anchor 1 (scoring-side vs plasticity-side); P_deflated=0.35; can run in parallel with Anchor 1.

---

## Context pointers (file paths; not summaries)

- `notes/research_pc_cleanup_2x_revival_drill_2026-06-26.md` -- full research drill with mechanism specs + falsifiable predictions
- `experiments/exp_pc_cleanup_deeper_chains_v1.py` -- existing failed cell (use as scaffold; lines 220-244 contain the soft-bundle that must NOT be reproduced in new arms)
- `data/exp_pc_cleanup_deeper_chains_v1_smoke/metrics.json` -- failure smoke metrics
- `data/exp_pc_cleanup_attractor_v1/metrics.json` -- Wave 1 vanilla baseline (recall=1.000 at M=80, by-construction-saturation; do NOT use this regime for the new cells -- M=160 d=15/20/30 is the discriminating envelope)
- `hdlab/predictive_coding.py` -- existing PC primitives (residual_magnitude, threshold_gate); Anchor 1 composes with these
- `memory/feedback_substrate_doesnt_know_anything_stop_testing_against_language_USER_LOCKED_2026-06-26.md` -- USER pivot; cells must NOT use language eval as success criterion

---

## Contract

- Pre-reg per [[feedback-envelope-expansion-fail-bands]]: HARD-PASS + HARD-FAIL bands BEFORE smoke (research note provides suggested thresholds; exp_dev refines).
- Self-test per [[feedback-formula-selftests]]: include unit tests for transient-W revert (Anchor 1) and energy-scoring monotonicity (Anchor 2).
- Multi-seed FULL on smoke clearance; minimum 3 seeds.
- Smoke MUST use larger M_CHAINS than the original failed smoke (which used M=4 d=5/10 and saturated). Suggest M=20-40 for smoke to keep regime discriminating.
- POST-SHIP REMOTE VERIFY via queue_add.sh exit code per [[feedback-ship-name-collision]].
- status_log entry per anchor with `plain_language` + `importance`.
- Fix #26 predispatch_check on each anchor name before authoring.

## Autonomy declaration

exp_dev decides ALL of: anchor name (suggested names above are advisory), N, V, M_CHAINS, K_top, depth-set, seed count, threshold bands (HARD-PASS + HARD-FAIL), queue choice, ETA, smoke profile, FULL profile, integration approach (extend existing cell vs new cell file). If exp_dev wants to drop one anchor and substitute a different mechanism inspired by the research drill (e.g., a hybrid of Anchor 1 + Anchor 2), that is exp_dev's call.

If smoke shows by-construction-saturation (all arms at recall=1.000), STOP and report -- regime is wrong; Wave 1.5 cell already proved M=160 d>=15 is the right discriminator.

---

## Filed by

Research (Opus 4.7 1M), 2026-06-26, in response to USER 2026-06-26 "drill negatives 2x" directive on PC cleanup deeper-chains HARD_FAIL.
