# exp_dev hand-off -- research: reasoning-realization gap closure prep

Filed-by: research sub-agent
Date: 2026-07-11
Trigger: notes/research_reasoning_realization_gap_closure_prep_2026-07-11.md
Urgency: MEDIUM-HIGH -- fire the moment the decisive CSKG map-builder result lands (win OR near-miss); do not wait for a strategy round-trip, the anchors below are pre-cleared regardless of which way that result goes.

---

## Pause state

Anchors below are PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ANCHOR CANDIDATES only.
Experiment design details (cell grids, hyperparameter values, script paths) are to be authored by exp_dev from the research note + cap_map context. Do NOT treat the descriptions below as implementation specs.

---

## Anchor candidates (rank-ordered)

### Anchor 1: training_recipe_tuned_refit_v1 (Part 3 lever 1-2, HIGHEST leverage, cheapest)

Anchor pointer: Research note Part 1 (Ruffinelli et al. track record) + Part 3 levers 1-2 + Cheap decisive test section.
Substrate-product reading: Re-fit whichever arm produced the map-builder's geom number using a cross-entropy loss (not margin/BCE, if not already CE) plus self-adversarial negative sampling (RotatE-native, our phase-rotation operator already qualifies), same seed/split/held-out set. Externally, this exact lever class (holding architecture fixed) bought +25-42% relative MRR in a primary source (Ruffinelli et al. 2020) -- bigger than the entire TransE->RotatE architectural jump (+15% relative). This is the single cheapest, best-precedented, highest-expected-value first move regardless of whether the decisive result is a WIN or a NEAR-MISS.
Tier hint: CPU/local, hours not days -- a training-config change, no new representation or mechanism. Run FIRST, before anything below.
Why-now: If this alone moves the geom number materially, the realized-vs-ceiling gap was partly a training-recipe artifact (exactly the confound Ruffinelli found externally) -- cheapest possible test of the most commonly-confounded variable in this literature, and de-risks or eliminates the need for anything more exotic.

Pre-reg bands:
  HARD-PASS: tuned re-fit improves the geom number by >=10% relative on the SAME held-out genuine-L2 set, random-code/trivial-baseline margins intact (no leak).
  MIDDLE-BAND: improves 3-10% relative -- real but partial; stack lever 2 (N3 reg + reciprocal-relations check) before concluding.
  HARD-FAIL: <3% relative movement AND the frequency-baseline control (must-fail check) also moves comparably -- harness confound, not informative about geometry-vs-frequency; fix harness before any further test.

### Anchor 2: regularization_reciprocal_check_v1 (Part 3 lever 3)

Anchor pointer: Research note Part 3 lever 3 (N3/L3 regularization + reciprocal-relations reformulation).
Substrate-product reading: Add N3/L3-style regularization on the entity/relation phase-coordinates, AND verify the cell already trains both (h,r,t) and (t,r_inv,h) directions -- if not, add it. Reciprocal-relations reformulation showed outsized gains on sparse graphs in the cited literature (Lacroix et al. 2018) and is close to a one-line fix if missing.
Tier hint: CPU/local, low effort. Run in parallel with or immediately after Anchor 1.
Why-now: Modest but reliable, nearly free, and directly checks a specific, cheap, previously-unverified implementation detail (reciprocal direction coverage) that the research note flags as "check first" rather than assumed present.

Pre-reg bands:
  HARD-PASS: combined regularization + reciprocal-direction fix (if missing) adds a further >=3% relative improvement on top of Anchor 1's result.
  MIDDLE-BAND: 1-3% relative improvement -- real, banked, but not load-bearing.
  HARD-FAIL: no measurable improvement AND reciprocal-direction coverage was already present -- rule out this lever, move to Anchor 3/4.

### Anchor 3: dg_decorrelation_front_end_v1 (Part 3 lever 4)

Anchor pointer: Research note Part 3 lever 4 + `notes/research_resonator_decode_capacity_ceiling_crux_v2_2026-07-10.md` (existing, unused `hdlab/hippocampal_encoder.py::DGProjection`).
Substrate-product reading: Wire the substrate's already-built, unit-tested `DGProjection` sparse-decorrelation primitive into whichever resonator/attractor cleanup readout the map-builder uses, ahead of cleanup. Brain math (Treves-Rolls sparse-coding capacity law) is rigorous; on-substrate causal link to basin-count/crosstalk reduction is flagged unproven in two independent prior drills -- cheap to try given the primitive already exists.
Tier hint: CPU/local, wiring only (no new math), low-moderate effort.
Why-now: Cheapest of the "readout precision" levers since the primitive is already built and tested; directly reuses a validated cross-cell law (correlation hurts capacity, decouple store-codes from retrieval-semantics).

Pre-reg bands:
  HARD-PASS: rare/hard-case held-out recall improves >=10% relative with DG front-end wired in, no regression on easy-case recall.
  MIDDLE-BAND: improves 3-10% relative, or improves rare-case but regresses easy-case by <5%.
  HARD-FAIL: no measurable improvement, or regresses aggregate recall -- causal link not confirmed for this substrate; deprioritize.

### Anchor 4: same_split_opaque_gnn_comparator_v1 (Best-in-class Section)

Anchor pointer: Research note "Best-in-class reference definition," point 1.
Substrate-product reading: Run a single, appropriately-scoped GNN/path-aggregation baseline (e.g. a minimal NBFNet-style or RED-GNN-style comparator) on the SAME genuine-L2 held-out CSKG split used for the map-builder's own numbers -- NOT a borrowed external FB15k-237 number. This is the only way to make the "glass-box is within X% of opaque SOTA" claim honest for THIS task/graph rather than an analogy from a different benchmark.
Tier hint: Moderate effort (needs a GNN implementation or a well-tested off-the-shelf one); GPU-preferred but small-scale feasible on CPU. Lower urgency than Anchors 1-3 -- this is a MEASUREMENT/calibration anchor, not an optimization lever. Run once Anchors 1-3 have produced a settled glass-box number, so the comparison is against the BEST glass-box result, not a preliminary one.
Why-now: Without this, any "best-in-class glass-box" claim rests on an external-literature analogy (Part 1's FB15k-237 numbers), which the research note explicitly flags as not apples-to-apples (different graph, different task difficulty, 2-hop vs 1-hop). This anchor converts an analogy into a measurement.

Pre-reg bands:
  HARD-PASS: glass-box best result reaches >=85% of the same-split GNN comparator's score -- confirms the external ~90-95% precedent transfers to this task/graph.
  MIDDLE-BAND: 60-85% -- gap larger than external precedent suggests; investigate whether it's architecture-dependent or a fixable glass-box gap.
  HARD-FAIL: <60% -- this task/graph may have a genuine architecture-dependent expressiveness requirement the external comparison did not predict; escalate to strategy before further glass-box tuning investment.

### Anchor 5: replay_consolidation_build_v1 (Part 3 lever 7, Course C -- ONLY after 1-3 are exhausted)

Anchor pointer: `notes/research_course_c_map_builder_replay_consolidation_design_2026-07-10.md` (full design, already pre-registered with its own 5-arm cheap decisive test) + this note's Part 3 lever 7.
Substrate-product reading: The iterative replay/consolidation build (recall-consistency gate + validation early-stop). P_deflated=0.20-0.25, unchanged and independently corroborated this cycle by thin brain-literature support for the specific "replay depth sharpens precision, not just retention" claim. This is the genuinely exploratory, novel-synthesis lever -- sequence LAST, after Anchors 1-3 have been run and their contribution to closing the gap is known, so that whatever residual replay-consolidation is asked to close is the genuine residual, not training-recipe noise.
Tier hint: Highest engineering lift of all 5 anchors (full iterative training-loop redesign with reliability gating). Do not front-load.
Why-now: Only IF Anchors 1-3 leave a material gap unclosed. If they close most of it, this anchor's priority drops and it becomes a lower-urgency exploratory follow-up rather than the main Phase-2 bet.

Pre-reg bands: reuse Course C note's own pre-registered 5-arm HARD-PASS/HARD-FAIL scaffold verbatim (do not re-derive) -- see that note's "Cheap decisive test" and "Falsifiable predictions" sections.

---

## Context pointers (file paths, not summaries)

- Research note (this drill): d:/AI/hd-instrument/notes/research_reasoning_realization_gap_closure_prep_2026-07-11.md
- Course C map-builder design (replay-consolidation full spec): d:/AI/hd-instrument/notes/research_course_c_map_builder_replay_consolidation_design_2026-07-10.md
- CSKG density gate (foundation PASS verdict): d:/AI/hd-instrument/notes/cskg_commonsense_core_kcore_density_gate_2026-07-10.md
- Convergence architecture (grounded verifier design): d:/AI/hd-instrument/notes/convergence_architecture_grounding_is_the_verifier_2026-07-10.md
- Resonator decode capacity ceiling (readout-precision levers, ACF, restarts): d:/AI/hd-instrument/notes/research_resonator_decode_capacity_ceiling_crux_v2_2026-07-10.md
- Resonator reachability ceiling (restart-budget law): d:/AI/hd-instrument/notes/research_resonator_reachability_ceiling_2026-07-07.md
- Knowledge-density information ceiling (matrix-completion/SBM floor): d:/AI/hd-instrument/notes/research_knowledge_density_information_ceiling_relational_inference_2026-07-10.md
- DGProjection primitive (unused, ready to wire): hdlab/hippocampal_encoder.py

---

## Contract section

This handoff proposes 5 anchor candidates, sequenced. Exp_dev selects based on current queue state, runner availability, and pause flag. Exp_dev does NOT need to implement all 5.

SEQUENCING CONSTRAINT: Anchor 1 MUST run before Anchor 5 (replay-consolidation). Anchors 1-2 are cheap and should run together or back-to-back first. Anchor 4 (same-split comparator) should run once Anchors 1-3 have produced a settled glass-box number, not before. Anchor 5 is gated on Anchors 1-3 leaving a material residual gap.

GATING: none of these anchors depend on the decisive CSKG map-builder result being a WIN specifically -- per this note's HEADLINE point 4, Anchor 1 is the correct first move whether the result is a WIN (push toward ceiling) or a NEAR-MISS (rule out training-recipe confound before concluding the mechanism failed).

---

## Autonomy declaration

Exp_dev is autonomous in:
- Choosing which anchors to dispatch first (subject to sequencing constraint above)
- Choosing cell grid dimensions, seed counts, and parameter values for each anchor
- Choosing local CPU vs remote CPU/GPU routing per feedback_route_gpu_vs_cpu_by_torch_not_N.md
- Writing experiment scripts that follow the feedback_metrics_required_fields_write_metrics.md convention
- Deciding whether Anchor 5 (replay-consolidation) is warranted at all, based on how much gap Anchors 1-3 close

Exp_dev is NOT autonomous in:
- Making cap_map decisions from verdicts (orchestrator / verdict_handler owns this)
- Making external/customer-facing "best-in-class" claims without the calibration caveat from this note's HEADLINE point 3 attached (ceiling is architecturally TransE-tier in absolute terms for a harder 2-hop task, not NBFNet-tier)
- Reopening the Course C replay-consolidation design's own pre-registered scaffold (reuse verbatim, per that note's own instruction)
