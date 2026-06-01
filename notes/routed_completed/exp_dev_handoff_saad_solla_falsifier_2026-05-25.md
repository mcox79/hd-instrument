# exp_dev hand-off: Saad-Solla saddle-cascade falsifier (4-corpus equal-spacing)

**Filed:** 2026-05-25 by Research sub-agent (Opus synthesis, parallel WebSearch lit-scan).
**Routing:** exp_dev queue pickup (pause-gated; orchestrator owns dispatch decision).
**Parent research:** `notes/research_saad_solla_saddle_cascade_deep_2026-05-25.md` (P=0.48, leading theoretical home; reanalysis CASCADE_PASS BIC=194.9).
**Discipline:** per [[feedback-no-experiment-design-in-prompts]] — this handoff specifies TASK SHAPE + WHY + CONTRACT + AUTONOMY only; exp_dev decides all numerical sweep grids, seeds, queue placement, ETA.

---

## TASK

Falsify or confirm the Saad-Solla saddle-cascade theory's prediction that adding a 4th categorical-similarity class to the substrate Bet B retention protocol produces a 4th equal-spaced plateau with statistically discrete structure.

## WHY

Tonight's reanalysis (CASCADE_PASS, `data/exp_wave14_betB_saddle_cascade_reanalysis_v1/metrics.json`) elevated Saad-Solla saddle-cascade from Tier-1 candidate to LEADING theoretical home for the substrate's three-plateau retention structure. BIC delta=194.9 over sigmoid; equal-spacing prediction error=0.0378 within tolerance. The reanalysis evidence is **necessary but not sufficient** — Mechanism A (linear + stratified codebook overlap, primitive-decision note P=0.45) explains the same evidence equally well, and the gap is within calibration noise.

The cheapest decisive test that distinguishes Saad-Solla from alternative mechanisms is the **4-corpus equal-spacing extension**. Saad-Solla predicts: adding a 4th categorical-similarity class produces a 4th plateau at the next equal-spaced height. Mechanism A and other alternatives do NOT make this sharp prediction. A HARD-PASS / HARD-FAIL outcome here resolves the framework choice for the substrate retention story.

Strategic importance:
- If HARD-PASS: Saad-Solla becomes confirmed primary framework (P > 0.55, above novel-synthesis cap because lit-PROVEN). Cap_map row "theoretical home for retention plateaus" can flip from 🔬 to 🟢. The 3-plateau audit signal scales to N-plateau for free.
- If HARD-FAIL: Saad-Solla downgrades to P ~ 0.30; substrate retention story pivots to "exactly 3 audit tiers as a hard-coded design feature" (still valid, less impressive product narrative). Mechanism A becomes leading.
- If MIDDLE-BAND: needs higher-N or higher-stage-count reship; document as inconclusive.

## CONTRACT (pre-registered fail bands)

### Design constraint

4-corpus extension of the existing Bet B 3-corpus retention protocol. Add a 4th similarity class strictly between the existing 3-stage-overlap class (G2_MID) and the disjoint class (G3_DIFF). Concretely: 4 similarity classes ordered by overlap-fraction:

1. **G1_SAME** (full overlap) — existing class.
2. **G2_3STAGE** (3-stage partial overlap) — existing G2_MID class. **NB**: existing G2_MID actually combines two overlap levels in the reanalysis; for this falsifier, split them into G2_3STAGE and G3_4STAGE explicitly.
3. **G3_4STAGE** (4-stage partial overlap) — NEW class to add.
4. **G4_DIFF** (disjoint corpora) — existing G3_DIFF class.

If the existing 3-corpus reanalysis ALREADY contains 4 distinguishable overlap levels (i.e., the G2_MID class can be split into 3-stage and 4-stage subclasses by exp_dev's inspection), exp_dev MAY use the existing data for the falsifier rather than re-running. **Spot-check this first** before queueing a new full experiment.

### Pre-registered bands

**HARD-PASS (Saad-Solla 4-plateau CONFIRMED):**
- `BIC_4state - BIC_3state < -30` (4-state model strongly preferred over 3-state) AND
- `spacing_error_4state < 0.05` (equal-spacing tolerance, same as parent 3-state result) AND
- `gap_ratio_4state ∈ [0.45, 0.65]` (consistent with 3-corpus reanalysis gap_ratio=0.556 ± reasonable variation) AND
- All 4 plateau heights are statistically distinct from neighbors (e.g., 95% CI non-overlap; or t-test p < 0.01 between adjacent groups).

**HARD-FAIL (Saad-Solla DOWNGRADED):**
- `BIC_4state > BIC_3state` (3-state still preferred — no new plateau emerged despite new categorical level) OR
- `spacing_error_4state > 0.10` (equal-spacing fails) OR
- The 4th plateau height collapses into one of the existing 3 (statistical indistinguishability between adjacent groups, e.g., 95% CI overlap > 50%).

**MIDDLE BAND (INCONCLUSIVE — needs reship):**
- `BIC_4state - BIC_3state ∈ (-30, 0)` (4-state marginally preferred but weak) AND
- `spacing_error_4state ∈ [0.05, 0.10]` (equal-spacing within wider tolerance).

**INSTRUMENTATION-FAIL (procedural):**
- The 4-stage and 3-stage overlap classes cannot be statistically separated in the corpus construction (i.e., the experimental design did not produce 4 distinguishable overlap levels). Re-design corpus before re-shipping; do NOT close the question on this failure mode.

### Mandatory measurements

1. Per-class retention mean, variance, sample size (G1, G2, G3, G4).
2. BIC for discrete-4-state, discrete-3-state, and continuous-sigmoid models. Report all three.
3. Equal-spacing prediction error: under equal-spacing, predict G2 = (G1+G4)/2 + ... compute predicted G2, G3 from G1 and G4 endpoints with equal gaps; report L2 error vs measured.
4. Gap ratios: gap(G1-G2), gap(G2-G3), gap(G3-G4); report pairwise ratios.
5. Discretization ratio (variance-of-2nd-derivative / variance-of-1st-derivative) — matches reanalysis metric.

### Optional but valuable

- Plateau-height predictability from a codebook-overlap-histogram fit: compute the empirical codebook-overlap distribution at the 4 operating points; report mode count and mode positions. If 4 modes visible matching the 4 plateau cosines within ±0.05, this is supporting evidence for Mechanism A (linear + stratified codebook) — and the two mechanisms can be DISTINGUISHED only by PPMI-sparsity sweep (separate future experiment).

## CONTEXT POINTERS

- `notes/research_saad_solla_saddle_cascade_deep_2026-05-25.md` — parent research note (full theoretical justification).
- `notes/research_alternative_theoretical_homes_2026-05-24.md` — original Saad-Solla candidate-rating drill (P=0.46 baseline).
- `notes/research_primitive_decision_linear_vs_recurrent_2026-05-25.md` — primitive lock LINEAR-HETEROASSOC; Mechanism A alternative.
- `data/exp_wave14_betB_saddle_cascade_reanalysis_v1/metrics.json` — CASCADE_PASS verdict that triggered this drill.
- `experiments/` — existing Bet B 4-stage continual experiment scripts (search for `exp_wave14_betB_4stage_continual` or similar) — likely starting point for the 4-corpus extension.

## AUTONOMY DECLARATION

exp_dev decides:
- Exact corpus construction for the 4-stage-overlap class (e.g., shared atoms ratio, stage count, retrieval probe count).
- Number of seeds per class.
- N value (recommend N=4096 per existing Bet B convention; exp_dev may override).
- Whether to use existing reanalysis data (if it already contains 4 distinguishable classes) or queue a new experiment.
- Queue placement (recommend remote-cpu given CPU-cheapness of BIC computation; exp_dev decides per the laptop-cpu / remote-cpu / GPU three-tier policy).
- ETA estimate.
- Smoke-scale parameters.
- Code structure.

exp_dev does NOT decide:
- The 4-class structure (SAME / 3-STAGE / 4-STAGE / DIFF) — that IS the testable design.
- The HARD-PASS / HARD-FAIL / MIDDLE / INSTRUMENTATION-FAIL band thresholds — pre-registered above per [[feedback-envelope-expansion-fail-bands]].
- The BIC + spacing + gap-ratio + discretization-ratio measurement set — required.

## DISCIPLINE CITATIONS

- per [[feedback-2x-means-depth]] — falsifier drills DEEPER into the saddle-cascade framework, not a re-verification of the reanalysis result.
- per [[feedback-no-experiment-design-in-prompts]] — task SHAPE only; exp_dev decides all numerical knobs.
- per [[feedback-envelope-expansion-fail-bands]] — HARD-PASS / HARD-FAIL / MIDDLE / INSTRUMENTATION-FAIL bands pre-registered with explicit numerical thresholds.
- per [[feedback-lit-scan-calibration-penalty]] — parent note P=0.48 deflated per uncharted-substrate-regime rule; this falsifier provides the lit-PROOF that would lift the cap.
- per [[feedback-rescue-sketch-first-sequencing]] — falsifier is CPU-cheap and addresses the cheapest-decisive-question first.
- per [[feedback-composition-classification]] — this is a SCORE-level falsifier (single test against a pre-registered band).

## EXPECTED VERDICT BANDS (calibrated)

- P(HARD-PASS): 0.42 — equal-spacing has held within 3 classes (reanalysis spacing_error=0.038); extending to 4 classes is plausible if Saad-Solla framework is correct.
- P(HARD-FAIL): 0.35 — if 3-plateau structure is hard-coded into the substrate design (e.g., from a structural feature like a 3-mode codebook-overlap histogram), no 4th plateau will emerge.
- P(MIDDLE BAND): 0.18 — marginal preference for 4-state; would need higher-N reship.
- P(INSTRUMENTATION-FAIL): 0.05 — corpus construction may fail to produce 4 distinguishable classes; re-design needed.

All P deflated per calibration penalty. Sum to 1.00.

---
BULK-ARCHIVED 2026-06-01: orchestrator-filed handoff to exp_dev; acted on (cap_map v312+ reflects evidence of completed work); bulk-archived per dashboard inbox-clearance Path A pattern.
