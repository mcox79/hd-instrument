# exp_dev hand-off -- research: does it scale (reasoning-vs-frequency scaling law)

Filed-by: research sub-agent
Date: 2026-07-12
Trigger: notes/research_does_it_scale_reasoning_vs_frequency_scaling_law_2026-07-12.md
Urgency: HIGH -- this hand-off's Anchor 1 is a cheap, load-bearing prerequisite check that should run BEFORE any
further compute goes into the multi-N scaling ladder or into declaring the current CSKG rotation/additive result a
"win."

---

## Pause state

Anchors below are PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ANCHOR CANDIDATES only.
Experiment design details (cell grids, hyperparameter values, script paths) are to be authored by exp_dev from the
research note + cap_map context. Do NOT treat the descriptions below as implementation specs.

---

## Anchor candidates (rank-ordered)

### Anchor 1: held_out_entity_inductive_probe_v1 (cheapest, highest leverage, run FIRST)

Anchor pointer: Research note's "Cheap decisive test" section + HEADLINE point 5. Reuse the held-out-ENTITY split
methodology already built and landed for `grounding_learned_sr_heldout_reasoning_v1` (3 seeds, FULL, 2026-07-10,
HARD_FAIL) -- apply that SAME split-and-control harness (held-out entities entirely absent from train; a
random-code/`CODEALIAS` control; a memoryless baseline) to the CURRENT `ONESHOT_ROTATE`/`ADDITIVE_TRANSE` fit
codes on the same CSKG-core graph, instead of the entity combinations tested by the existing genuine-L2 harness
(which only tests unseen EDGES between already-known entities, a weaker and different question).
Substrate-product reading: this is the single cheapest possible falsifier of "does the current architecture have
ANY reusable relational signal, independent of scale." The GraIL/NBFNet inductive-KGE literature says fixed
per-entity embedding tables (which is what both `ONESHOT_ROTATE` and `ADDITIVE_TRANSE` are) cannot represent an
unseen entity at all by construction -- and this substrate already ran the analogous test once on a related
mechanism (SR codes) and got a clean HARD_FAIL (held-out reach@2 0.1148 vs random-code 0.104, delta 0.011, below
the 0.05 margin). No new corpus or infra is needed -- reuse the existing 25,752-entity graph and the existing split
harness verbatim, swap only which mechanism's codes are being scored.
Tier hint: remote_cpu_queue (matches existing SR-code cell's compute class; no GPU needed, this is a scoring pass
over already-fit codes, not a new training run) -- cheap, hours not days. Run BEFORE Anchor 2 (the multi-N ladder)
and before any product framing of the current fair-margin result as a durable win.
Why-now: if this fails (the deflated-prior expectation, P=0.15-0.20 per the research note), it means no amount of
additional N will fix the underlying gap -- the fix becomes "build a genuinely inductive/factorized-operator
architecture," not "wait for bigger graphs." Running this FIRST prevents spending the multi-N ladder's compute
budget on a question (does memorized-search scale) that isn't the one that actually matters (does reasoning
scale).

Pre-reg bands:
  HARD-PASS: held-out-entity performance for `ONESHOT_ROTATE` and/or `ADDITIVE_TRANSE` clears the random-code
  control by >=0.05 absolute (same bar the SR-code cell used) -- real transferable relational signal to genuinely
  unseen entities exists in the current fit; proceed to Anchor 2 with the inductive-generalization question folded
  into every N-rung.
  MIDDLE-BAND: 0.02-0.05 margin over random-code control -- weak but nonzero signal; flag for a second seed/split
  before either declaring pass or fail; proceed to Anchor 2 but treat the inductive claim as unresolved.
  HARD-FAIL: delta < 0.02 vs random-code control (replicates the SR-code cell's finding) -- the current architecture
  does memorized search, not reasoning, independent of N. This does not block Anchor 2 (the in-sample-composition
  scaling question is still worth answering) but it DOES mean Anchor 2's results must never be reported as
  "reasoning scales" -- only as "in-sample composition scales" -- and it elevates the brain-grounded
  factorized-operator redesign (research note's brain-grounding section) from a someday-idea to the actual next
  architecture bet.

### Anchor 2: multi_n_scaling_ladder_cskg_v1 (the main scaling-curve experiment, sequence AFTER Anchor 1)

Anchor pointer: Research note's "Falsifiable predictions (the multi-N scaling-curve experiment)" section, full
design (N ~5k/25k/100k rungs, existing 7-arm harness reused verbatim at each rung, degree-stratified fair Hits@10 +
backdoor correlation + a graph-level skew statistic (Gini or max-degree/mean-degree ratio) reported at every rung).
Substrate-product reading: measures whether the fair (low+mid degree) margin over `BASELINE_POP` holds, shrinks, or
grows as N increases 4x, and whether the backdoor correlation improves or worsens with scale -- the two central
open questions this drill could not answer from the literature alone (no paper reports an accuracy-vs-N
degradation curve for KGE at fixed dimension; no paper measures backdoor-correlation trend with scale).
Tier hint: remote_cpu_queue for the 5k/25k rungs (CPU-safe, matches current compute class), overnight_queue (GPU)
for the 100k rung. Plan explicit memory headroom for the 100k rung BEFORE running it live -- a related cell
(`exp_course_c_map_builder_cskg_l2_genuine_gpu_v1`) already hit a 3/3-seed CUDA OOM HARD_FAIL at a comparable
entity count; the 100k rung must not discover this live, size the negative-sampling batch/adaptive-batch strategy
for the larger N up front. Per-rung atomic checkpointing (reuse the `oracle_capacity_ladder` cell's rung-checkpoint
pattern) so a dropped remote connection loses at most one rung, per cron-redispatch discipline.
Why-now: this is the mission's central ask (a concrete, remote-runnable, resumable scaling-curve design) and the
two open questions it answers (does fair-margin hold at bigger N; does backdoor correlation trend with scale) have
no literature precedent to substitute for direct measurement.

Pre-reg bands: reuse the research note's own "Falsifiable predictions" HARD-PASS (4 conditions: margin within 30%
relative of N=25k value; backdoor r not stuck above 0.20 at every rung; low+mid absolute entity count grows with N;
held-out-entity test -- from Anchor 1 -- clears its margin at every rung) / HARD-FAIL (4 conditions: margin
shrinks toward zero or flips negative; backdoor r climbs monotonically; held-out-entity test fails at any rung;
compute/memory cost scales worse than near-linear, distinguished explicitly from a reasoning-quality wall) bands
verbatim -- do not re-derive.

---

## Context pointers (file paths, not summaries)

- Research note (this drill): d:/AI/hd-instrument/notes/research_does_it_scale_reasoning_vs_frequency_scaling_law_2026-07-12.md
- Current fair-test result (re-read in full this cycle): d:/AI/hd-instrument/data/exp_course_c_rotate_cskg_l2_seed_17_gpu1024_v1/metrics.json
- Prior held-out-entity HARD_FAIL (the harness Anchor 1 reuses): grounding_learned_sr_heldout_reasoning_v1 (see d:/AI/hd-instrument/notes/relational_capability_track_record_scour_2026-07-10.md, Section E)
- OOM cross-check (for Anchor 2's 100k-rung memory planning): d:/AI/hd-instrument/data/exp_course_c_map_builder_cskg_l2_genuine_gpu_v1/metrics.json
- Functional-form sibling note (additive-vs-rotation reconciliation needed, per Cross-thread synthesis): d:/AI/hd-instrument/notes/research_how_others_beat_frequency_dissect_training_glassbox_recreate_functional_form_gap_2026-07-11.md
- Relational capability track record (full off-disk cert inventory): d:/AI/hd-instrument/notes/relational_capability_track_record_scour_2026-07-10.md
- CSKG prior-art / corpus survey: d:/AI/hd-instrument/notes/research_cskg_prior_art_novelty_due_diligence_2026-07-10.md

---

## Contract section

This handoff proposes 2 anchor candidates, sequenced. Exp_dev selects based on current queue state, runner
availability, and pause flag.

SEQUENCING CONSTRAINT: Anchor 1 MUST run (or at minimum be explicitly deferred with a stated reason) before Anchor
2's results are given any product-facing "reasoning scales" framing -- Anchor 2 alone only measures whether
in-sample composition scales, which is a materially weaker and different claim.

GATING: neither anchor depends on the additive-vs-rotation reconciliation (Cross-thread synthesis note) being
resolved first -- both anchors can run on whichever fit code is currently in `ONESHOT_ROTATE`/`ADDITIVE_TRANSE` as
of today; if that reconciliation changes which arm is "the" glass-box candidate, re-point Anchor 1/2 at the
corrected arm rather than re-designing the harness.

---

## Autonomy declaration

Exp_dev is autonomous in:
- Choosing which anchor to dispatch first (subject to the sequencing constraint above)
- Choosing cell grid dimensions, seed counts, N-rung exact values (5k/25k/100k are suggestions, not requirements),
  and corpus-merge sourcing for the 100k rung
- Choosing local CPU vs remote CPU/GPU routing per feedback_route_gpu_vs_cpu_by_torch_not_N.md
- Writing experiment scripts that follow the feedback_metrics_required_fields_write_metrics.md convention
- Deciding whether to run Anchor 2 at all if Anchor 1 HARD_FAILs (the research note's own reading is that Anchor 2
  is still informative even under an Anchor-1 HARD_FAIL, but exp_dev may reasonably reprioritize toward the
  brain-grounded factorized-operator redesign instead if capacity is scarce)

Exp_dev is NOT autonomous in:
- Making cap_map decisions from verdicts (orchestrator / verdict_handler owns this)
- Reporting a fair-margin win from Anchor 2 as "reasoning scales" without the Anchor-1 held-out-entity result
  attached (per the calibration discipline in the research note's Substrate-product implications section)
- Reopening the multi-N ladder's own pre-registered HARD-PASS/HARD-FAIL scaffold (reuse the research note's bands
  verbatim, per that note's own instruction)
