# exp_dev hand-off — research: multi-hop test fairness / goal-directed traversal redesign

**Filed by:** research sub-agent. **Trigger:** `notes/research_multihop_test_fairness_brain_goal_directed_traversal_2026-07-09.md` — foundational drill on whether the reader win-cell v3 (decoupled-codes) failure reflects a genuine substrate wall or an UNDERDETERMINED test query. Brain-mechanism convergence (PFC goal-maintenance + hippocampal goal-modulated replay/VTE) plus formal-logic convergence (functional-dependency theory, Hadamard well-posedness, KG query-embedding set-semantics) all say `(source_node, relation) -> single sibling` has no unique answer when a node has multiple true R-neighbors, UNLESS a goal/target or accumulated path-context is added to the query.

**Pause state:** check `data/orchestrator_paused.flag` at dispatch time; this hand-off proposes a ZERO-NEW-DISPATCH re-analysis pass first (Prediction 1), which should be allowed even if experiments are paused (it is analysis of already-landed data, not a new experiment), followed by an optional small new smoke cell (Prediction 2/3) which IS pause-gated.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off names ANCHOR + POINTERS + the falsifiable predictions from the research note only. exp_dev designs ALL of: exact re-scoring script, N, seed count, threshold implementation detail, queue choice, smoke profile, FULL profile.

---

## Anchor candidates (rank-ordered)

1. **Zero-compute re-scoring pass on already-landed v3 decoupled-codes data (Prediction 1)**
   - Anchor pointer: `notes/research_multihop_test_fairness_brain_goal_directed_traversal_2026-07-09.md`, "Cheap decisive test" + "Falsifiable predictions" Prediction 1.
   - Substrate-product reading: re-score the EXISTING v3 output two ways without touching the encoder/decoder at all — (a) SET-ACCEPTING: count a hit if the top prediction is a member of the true sibling set, not only if it matches one arbitrarily pre-chosen sibling; (b) compare that hit-rate to the current NAIVE single-target hit-rate, scaled by the relation's mean branching factor. This is pure analysis on disk-resident metrics/predictions already produced by the v3 cell — no new dispatch, no pause-gate concern.
   - Tier: local/analyzer-only (near-zero compute).
   - Why now: this is the cheapest possible test of the drill's core hypothesis and should run BEFORE any new architecture cell is funded in the sibling win-engineering threads, since a positive result here could retroactively reinterpret several of those threads' null results (see research note's Cross-thread synthesis, "first drill to question the TEST rather than the MECHANISM" paragraph).

2. **GOAL-CARRYING query smoke cell (Prediction 2) — small, pause-gated**
   - Anchor pointer: same research note, Prediction 2 + "Fair brain-aligned redesign" implication section.
   - Substrate-product reading: re-run retrieval on the v3 decoupled codes (and, as a control, the original non-decoupled codes) with the query augmented by ONE additional piece of already-available path-context (e.g. the downstream hop-2 relation, or an explicit target node from the traversal task) — analogous to A*'s goal node / UVFA's goal-conditioning. Tests whether decoupling's apparent harm reverses once the query supplies its own disambiguating signal instead of relying on incidental code correlation.
   - Tier: local/CPU smoke first (small matched subgraph, few hundred nodes, 1 seed) before any FULL dispatch.
   - Why now: directly tests whether v3's regression was "decoupling is wrong" or "the test was quietly relying on correlation to paper over an underdetermined query" — a load-bearing distinction for whether the win-engineering threads should keep pursuing decoupled-code architectures or abandon that direction.

3. **Calibration-curve check (Prediction 3) — analysis-only, low priority, run alongside #1**
   - Anchor pointer: same research note, Prediction 3.
   - Substrate-product reading: once a redesigned (goal-carrying or set-accepting) scoring is in place, check that accuracy declines smoothly with branching factor rather than being flat (over-corrected/trivial) or cliff-shaped (still unfair). Cheap to compute alongside #1/#2, no separate dispatch needed.
   - Tier: local/analyzer-only.
   - Why now: prevents over-correcting into a trivial test; keeps the redesigned test brain-aligned (graded residual error, not perfect determinacy) rather than swinging to the opposite failure mode.

---

## Context pointers (file paths, not summaries)

- `notes/research_multihop_test_fairness_brain_goal_directed_traversal_2026-07-09.md` — this drill's full note (HEADLINE, cheap decisive test, all 3 falsifiable predictions with HARD-PASS/HARD-FAIL bands, cross-thread synthesis, citations).
- `notes/research_reader_load_reduction_feasible_dim_win_path_2026-07-09.md` — same-day sibling drill; the two-layer local-index design and the `D_f/N<=0.056` capacity formula this drill's re-interpretation may affect.
- `notes/research_reader_decisive_multihop_win_engineering_2026-07-09.md` — same-day sibling drill; the `exp_grounding_multihop_decisive_win_v1` cell whose arms (esp. DENSE_HOPFIELD_CLEANUP, N_SCALE_8X) may need re-reading through this drill's lens per the Cross-thread synthesis re-interpretation note.
- `data/exp_grounding_multihop_decisive_win_v1/metrics.json` — the already-landed data Prediction 1's re-scoring pass should run against directly (v3 decoupled-codes arm's raw predictions/candidate rankings, if retained; if raw per-query candidate lists were NOT persisted, that itself is a finding — flag to skunkworks per [[feedback-probes-persist-metrics-retain-ckpts-until-vet]]).
- `notes/substrate_capability_map.md` — current cap_map; this thread's cell rows.

---

## Contract

- Pre-reg per [[feedback-envelope-expansion-fail-bands]]: HARD-PASS + HARD-FAIL bands are already specified in the research note (Predictions 1-3); exp_dev may sharpen implementation detail but the bands themselves came from research and should not be loosened.
- Self-test per [[feedback-formula-selftests]].
- Anchor 1 (re-scoring) requires NO new dispatch — verify whether it can run entirely off already-persisted files before treating it as pause-gated.
- Anchor 2 (goal-carrying smoke cell) IS pause-gated per standard exp_dev discipline; smoke on CPU/local before any FULL/GPU dispatch.
- Multi-seed FULL on smoke clearance for Anchor 2 if it proceeds past smoke.
- status_log entry per anchor with `plain_language` + `importance`.

## Autonomy declaration

exp_dev decides ALL of: exact re-scoring script/implementation, anchor name, N, M, K, seed count, precise threshold implementation (the bands are pre-specified in the research note; exp_dev implements them), queue choice (Tier A/B/C), ETA, smoke profile, FULL profile. If exp_dev judges that raw per-query candidate rankings from the v3 cell were not persisted and Anchor 1 cannot run as pure re-analysis, exp_dev's call whether to re-run a minimal smoke-scale version of the v3 cell instead (still cheap, still not the full architecture-change cells in the sibling threads) — that substitution is exp_dev's to make, not pre-baked here.

---

## Filed by

Research sub-agent, 2026-07-09, foundational test-fairness drill (Director-requested, brain-first). Hand-off ready for exp_dev pickup on next queue-refill or dedicated dispatch cycle.
