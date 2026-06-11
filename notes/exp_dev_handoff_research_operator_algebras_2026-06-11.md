# exp_dev hand-off -- research: operator-algebras / subfactor-theory 2x DEEP drill

Filed-by: research sub-agent
Date: 2026-06-11
Trigger: notes/research_drill_operator_algebras_subfactor_theory_2x_2026-06-11.md
Urgency: MEDIUM -- not blocking current Sprint-4; opens a new substrate-product capacity story IF GHRR-1 HARD-PASSES; cheap CPU test

---

## Pause state

Experiments below are PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ANCHOR CANDIDATES only.
Experiment design details (cell grids, dimension N, matrix size m, seed count, dataset construction) are to be authored by exp_dev from the research note + cap_map context. Do NOT treat the descriptions below as implementation specs.

---

## Anchor candidates (rank-ordered)

### Anchor 1: ghrr1_noncommutative_binding_v1 (decisive)

Anchor pointer: Research note section (b) EXPERIMENT GHRR-1 + section (c) predictions OA-P1, OA-P2, OA-P4.
Substrate-product reading: Parameter-matched comparison of FHRR baseline (m=1) vs GHRR_small (m=2) vs GHRR_med (m=4) on compositional depth cascading (T_compose to L = 4, 6, 8, 10) + ordered-sequence encoding (T_seq with and without positional code). Decides whether operator-algebra extension is a substrate win (HARD-PASS OA-P1 >=1.5x lift at L=8) or a wash (HARD-FAIL <=1.05x). Also sanity-ports free-probability spectral observability primitives (Marchenko-Pastur bulk + kappa_4_free + spectral gap) to the GHRR matrix codebook.
Tier hint: CPU laptop, ~2-3 hr. Pure numpy / pure torch. No GPU needed.
Why-now: GHRR (arXiv 2405.09689) is a published precedent. Decisive cheap test exists today. If HARD-PASSES, substrate roadmap gains a new capacity-vs-m dial and a marquee Testbed v1 demo primitive. If HARD-FAILS, operator-algebra angle parks and free-probability framework owns the spectral observability story alone.

Pre-reg bands (OA-P1 binding capacity):
  HARD-PASS: GHRR_med recall@1 at L=8 >= 1.5x FHRR_baseline recall@1 (>=5 seeds, lift >= 2 x SE per method-overclaim feedback)
  MIDDLE-BAND: lift in [1.05x, 1.5x]
  HARD-FAIL: lift <= 1.05x

Pre-reg bands (OA-P2 noncommutative sequence ordering):
  HARD-PASS: GHRR_med ordered-recall@1 without positional encoding >= 0.80 x GHRR_med ordered-recall@1 with positional encoding
  HARD-FAIL: ratio <= 0.30

Pre-reg bands (OA-P4 free-prob primitive portability):
  HARD-PASS: MP bulk + TW edge + kappa_4_free port to GHRR matrix codebook with <30% line change AND reproduce the free-prob drill's KS / z-score predictions within their bands
  HARD-FAIL: requires >30% line change OR predictions outside bands on GHRR

### Anchor 2: ghrr2_subfactor_index_sweep_v1 (deferred until GHRR-1 lands)

Anchor pointer: Research note section (c) prediction OA-P3 + section (g) new-math angle 1.
Substrate-product reading: Sub-codebook inclusion sweep: project parent codebook onto top-k singular subspace for k in a sweep; measure retention curve. Tests whether substrate sub-codebook inclusions exhibit Jones-index-like discrete plateaus (P_deflated weak ~0.25).
Tier hint: CPU laptop, ~1 hr. Pure numpy.
Why-now: Only dispatch after GHRR-1 HARD-PASSES. Otherwise the noncommutative algebra question is parked.

Pre-reg bands:
  HARD-PASS: retention-vs-k shows >= 2 quasi-discrete plateaus over the sweep range
  HARD-FAIL: retention-vs-k is monotone smooth with no plateaus

### Anchor 3: ghrr3_freeprob_port_v1 (deferred until GHRR-1 AND free-prob framework ship)

Anchor pointer: Research note section (i) EXP GHRR-3 + free-prob 3x DEEP drill predictions P1-P4.
Substrate-product reading: Once free-probability primitives ship (MP bulk + TW edge + kappa_4_free + spectral gap), port the 30-line code to GHRR matrix codebook. Validate the unification claim that substrate observability is dimension-and-algebra agnostic.
Tier hint: CPU laptop, ~30 min once free-prob ships.
Why-now: Sequential dependency on free-prob substrate framework experiment. Not blocked by Sprint-4 timeline.

Pre-reg bands: identical to free-prob drill P1-P4 but on GHRR matrix codebook.

---

## Context pointers (file paths, not summaries)

- d:/AI/hd-instrument/notes/research_drill_operator_algebras_subfactor_theory_2x_2026-06-11.md (this drill's research note)
- d:/AI/hd-instrument/notes/research_drill_free_probability_substrate_framework_3x_2026-06-11.md (free-prob 3x DEEP; OA-P4 ports its primitives)
- d:/AI/hd-instrument/notes/research_drill_schools_of_thought_lineage_2x_2026-06-11.md (lineage drill that flagged operator-algebra as top-3 next corpus entry)
- d:/AI/hd-instrument/notes/research_drill_algebra_taxonomy_formal_systems_2x_2026-06-11.md (substrate-self-index taxonomy; GHRR adds new category 14)
- arXiv 2405.09689 (GHRR paper; the engineered precedent for noncommutative VSA binding)
- Memory: substrate_v32_engineered_wrapper_2026-06-11.md (Reed-Solomon-on-FHRR extends to matrix-Reed-Solomon-on-GHRR)
- Memory: drill_pattern_temporal_contextual_not_structural_2026-06-11.md (CAUTION: GHRR is structural; this prior suggests skepticism BUT GHRR has published empirical wins so deflate less)
- Memory: feedback_method_overclaim_lift_validation.md (lift >= 2 x SE required for HARD-PASS, not absolute threshold)

---

## Contract section

This hand-off is consumed by exp_dev on an emergency-refill or hand-off-pickup cycle. exp_dev:
1. Reads the research note + this hand-off in full.
2. Authors a concrete experiment design (cell scripts, dimension N choice, seed sweep, dataset construction for T_compose and T_seq) consistent with the pre-reg bands above.
3. Submits cells via queue_add to local_cpu_queue (this is a pure-CPU experiment).
4. Verifies remote dispatch + binds to the standard substrate verification harness (verification/run_certification.py style).
5. Returns verdict via standard verdict_handler path.

---

## Autonomy declaration

exp_dev owns implementation choices in full:
- N (vector dimension) chosen to parameter-match across FHRR vs GHRR_small vs GHRR_med
- Seed count >= 5 (per method-overclaim lift discipline)
- Dataset for T_compose: synthetic compositional binding tree (anchored to substrate's existing per-level cascading cleanup harness; reuse if compatible)
- Dataset for T_seq: substrate's existing sequence-encoding benchmark, OR a 6-element ordered sequence sanity bench if no clean reuse
- Cleanup harness: substrate's standard cleanup; do NOT introduce method changes mid-experiment
- Smoke gate before full sweep per standard exp_dev protocol
- Self-test per formula-selftests
- REMOTE VERIFY after queue_add

Research does NOT pre-specify these. exp_dev chooses, executes, returns verdict.
