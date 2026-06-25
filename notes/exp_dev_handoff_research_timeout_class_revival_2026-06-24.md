# exp_dev hand-off -- research: TIMEOUT class revival drill

**Filed:** 2026-06-24 by research (sub-agent context; main thread will dispatch exp_dev wrapper).

**Trigger:** 2x+3x revival drill on 5 local-CPU timeouts today (cross-layer compose / heterogeneous routing / cross-biology mappings / sequence v2 / A1 test-design audit) plus PCGrad v1 earlier. Source research note: `notes/research_timeout_class_revival_disparate_fields_2026-06-24.md`.

**Pause state:** check `data/orchestrator_paused.flag` at dispatch time; this hand-off filed as recommendations not unconditional ships.

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off names ANCHORS + POINTERS + SCOPE-REDUCTION DIRECTION only. exp_dev designs ALL of: exact N, exact M, exact arms-to-drop, smoke profile, FULL profile, threshold bands, queue choice, anchor name, ETA. Research does NOT specify numerical parameters.

---

## What the research drill found

The 5 timeouts share a single root-cause signature: cell-author wall estimates anchored on smoke-N are in the WRONG roofline regime than full-N. Smoke is bandwidth-bound (working set fits L3); full-N is compute-bound (matmul scales as N^2 or N^3 with cleanup top-K). A 4x scope-up at the regime boundary can mean 16-64x wall blowup. Three of the cells are load-bearing and rescue-able via roofline-aware scope reduction. The disparate-fields drill (HPC roofline / queueing theory / Erlang OTP / K-SAT phase transitions / brain energy budget) all converge on the same fix pattern: smaller units, partial results, sparse computation, no global synchronization.

---

## Anchor candidates (rank-ordered; exp_dev picks 1-3)

### 1. cross_layer_composition_RESCUE_v1 (LOAD-BEARING; pick this first)

- **Anchor pointer:** the `exp_q_a3_l*_cross_layer_composition_v1_n*.py` family in experiments/; identify largest `(L, N)` combo that completed in `data/recent_landings.jsonl`, then scope the rescue to that-plus-ONE-step (L+1 OR N x 2, not both).
- **Substrate-product reading:** Track-A cap_int integration test; load-bearing for cross-layer composition cap_map row. Original cell timed out at 3600s.
- **Scope-reduction direction:** ONE-step expansion from last completed `(L, N)`, not the original frontier jump. Per Angle 4 (K-SAT phase boundary), the discriminating regime IS the wall-time hard regime; rescue scopes JUST PAST the cliff, not deep into it.
- **Discipline-add required:** D1 mandatory roofline probe (3-point at smoke_N / 2x / 4x; fit power-law; refuse dispatch if extrapolated wall > 0.8 x timeout). D2 atexit partial-results flush + per-seed checkpoint.
- **Tier:** local_cpu_queue OR remote_cpu_queue (exp_dev decides per Tier A/B/C in `agents/exp_dev.md`).
- **Why now:** cross-layer composition is the third-arc strategic priority; 100+ family-member cells suggest the sweep is actively driving cap_map. Rescuing the failed frontier cell unblocks the sweep.

### 2. heterogeneous_routing_RESCUE_v1 (LOAD-BEARING)

- **Anchor pointer:** `experiments/exp_substrate_compose_heterogeneous_routing_v1.py`. Original cell timed out at 3600s.
- **Substrate-product reading:** 3-architecture cross-comparison (Tonegawa-sparse / dense-Hebbian / k-WTA-VQ or similar); cannot split arms (cross-arm comparison IS the value).
- **Scope-reduction direction:** halve N_DIM (typically 8192 -> 4096, but exp_dev confirms from the cell); single seed pre-flight first; if HARD-PASS or HARD-FAIL on 1 seed, ship; if MIDDLE_BAND escalate to 3-seed at reduced N. Per c2_postmortem pattern (proven precedent for 4x outer-product cost reduction).
- **Discipline-add required:** same D1 + D2 as above.
- **Tier:** local_cpu_queue or remote_cpu_queue.
- **Why now:** heterogeneous-plasticity / heterogeneous-architecture composition is on the gap framework; 3-arm discriminator design is brittle to N changes (per Fix #28 lesson: read per-arm metrics not verdict_msg).
- **Risk:** at N=4096 the heterogeneous discriminator may be weaker. Pre-reg HARD bands stay; if mechanism fails to discriminate at reduced N, that itself is signal.

### 3. cross_biology_mappings_RESCUE_v1 (LOAD-BEARING + MINI-CELL ARCHITECTURE PILOT)

- **Anchor pointer:** cell ID `cross_biology_composition_mappings` family; original cell timed out at 4500s.
- **Substrate-product reading:** 3 biology mappings (likely cortex / hippocampus / cerebellum analogs); mappings are INDEPENDENT (each mapping is a self-contained test).
- **Scope-reduction direction:** SPLIT into 3 sub-cells (one per biology mapping) + 1 aggregator cell. Each sub-cell runs full 3-seed at full N (since cost is now 1/3). Aggregator cell reads the 3 metrics.json files and computes cross-mapping comparison.
- **Discipline-add required:** D1 + D2 + sub-cell dependency chain (aggregator waits on 3 sub-cells; reads partial results if any sub-cell fails). Use existing aggregator pattern from `substrate_brain_full_compose_LM_v1` if applicable.
- **Tier:** local_cpu_queue (per-sub-cell wall 30-40min fits comfortably).
- **Why now:** this is the mini-cell architecture PILOT. If it works smoothly, generalize the pattern to the cell-author template. Erlang-OTP discipline analog: failures of any one sub-cell do not cascade.

---

## Stretch candidates (if exp_dev has bandwidth for >3)

4. **sequence_v2_RESCUE** -- queue 2x revival research drill first; deferred.
5. **A1_test_design_audit_RESCUE** -- queue 2x revival research drill first; deferred.
6. **PCGrad_v1_RESCUE** -- queue 2x revival research drill first; deferred.

Per the source research note's L3 framing, the top-3 above are load-bearing; the remaining 3 should wait for fresh research drills on their underlying mechanisms before re-spec'ing.

---

## Context pointers (pointers, not summaries)

- `notes/research_timeout_class_revival_disparate_fields_2026-06-24.md` -- THIS DRILL's source note; HARD-PASS / HARD-FAIL bands + falsifiable predictions defined there.
- `notes/c2_cascade_stc_swr_timeout_postmortem_and_reauthor_spec_2026-06-22.md` -- prior single-cell timeout post-mortem; the c2 rescue spec there is the structural template for heterogeneous_routing rescue (Option A: smaller N + Option C: drop redundant arm).
- `data/recent_landings.jsonl` -- read this for last-completed `(L, N)` in cross_layer_composition family.
- `data/orchestrator_status_log.jsonl` -- read last 50 entries for queue state + recent verdicts.
- `notes/feedback_fix24_gpu_dispatch_must_actually_use_gpu_USER_2026-06-22.md` -- GPU routing rule; rescues likely belong on CPU not GPU but exp_dev decides.
- `tools/predispatch_check.py <anchor>` -- Fix #26 verify-the-referent gate; MUST run for each rescue before ship.

---

## New disciplines this drill recommends (cell-author template addition)

**D1 (mandatory pre-dispatch roofline probe).** For any cell with N_DIM >= 4096 OR M_pattern >= 1000 OR n_arms x n_seeds >= 9: run a 3-point timing probe at (smoke_N, 2x smoke_N, 4x smoke_N) on single arm + single seed. Fit `t = a*N^k`. Extrapolate to full-N. Refuse dispatch if `extrapolated_wall > 0.8 * timeout`. Probe cost ~3-5min CPU. Gates >90% of timeout failures by construction.

**D2 (mandatory partial-result atexit + per-seed checkpoint).** All cells with `n_seeds * n_arms >= 4` ship with:
- `atexit` handler flushing current per-arm per-seed metrics dict to `partial_metrics.json` (separate path from final write)
- Per-seed checkpoint resume (PROT-021 wired explicitly, not optionally)
- Execution order: iterate `(seed_idx, arm_idx)` so 1-seed-all-arms lands FIRST (partial-result value)

Both disciplines are NEW; they should be added to `tools/spawn_templates/experiment_pipeline_agent_template.md` (Fix #11). exp_dev confirms with cell-author team before generalizing.

---

## Contract

- Pre-reg per [[feedback-envelope-expansion-fail-bands]]: HARD-PASS + HARD-FAIL bands BEFORE smoke. Bands inherit from original (timed-out) cell's pre-reg; do NOT loosen.
- Self-test per [[feedback-formula-selftests]].
- Multi-seed FULL on smoke clearance.
- Queue routing per Tier A/B/C in `agents/exp_dev.md` Section 0.
- Ship via `bash tools/orchestrator/queue_add.sh <queue> <name> <script> <prereg> <timeout>`.
- POST-SHIP REMOTE VERIFY via the queue_add.sh exit code (5 = post-ship verification failed).
- Fix #26 predispatch_check.py REQUIRED for each rescue.
- status_log entry per anchor with `plain_language` + `importance`.
- D1 roofline probe REQUIRED for each rescue (new discipline this drill recommends).
- D2 atexit + per-seed checkpoint REQUIRED for each rescue.

## Autonomy declaration

exp_dev decides ALL of: anchor name, exact N, exact M, exact arms-to-drop, smoke profile, FULL profile, threshold bands inheritance vs adjustment, queue choice (Tier A/B/C), ETA. Research passes anchor POINTERS + SCOPE-REDUCTION DIRECTION only. If exp_dev finds a better rescue framing (e.g., split heterogeneous_routing instead of halving N), that is exp_dev's call. If exp_dev decides the rescues should wait for the D1+D2 discipline-add to land in the cell-author template first, that is also exp_dev's call.

---

## Filed by

research sub-agent, 2026-06-24, post 5-cell timeout drill cycle. Source note: `notes/research_timeout_class_revival_disparate_fields_2026-06-24.md`. Hand-off ready for `/exp_dev notes/exp_dev_handoff_research_timeout_class_revival_2026-06-24.md` dispatch.
