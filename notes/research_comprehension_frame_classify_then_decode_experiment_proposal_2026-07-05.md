# exp_dev hand-off — research: COMPREHENSION frontier drill (frame-classify-then-known-decode)

**Filed-by:** research
**Filed-at:** 2026-07-05
**Trigger:** USER frontier-drill directive to open the COMPREHENSION capability (substrate's missing complement to the working generation "mouth"). Source research note: `notes/research_frontier_drill_comprehension_parse_unknown_structure_2026-07-05.md`.

**Pause state:** check `data/orchestrator_paused.flag` per standard exp_dev contract.

**Per [[feedback-no-experiment-design-in-prompts]]** — this hand-off ranks the anchor candidate and points at the research note for the full cell spec (arms, metric, HARD-PASS/HARD-FAIL bands, brain-mechanism math, lit citations, per-arm disk evidence). It does NOT re-specify the cell design here; exp_dev authors the cell per its autonomy declaration below.

---

## Source research note

`notes/research_frontier_drill_comprehension_parse_unknown_structure_2026-07-05.md`

Read it FIRST for: the exact gap diagnosis (frame-unknown blind factorization has only ever been tried with the DENSE algebra — 0.000 twice — never with sparse-block geometry in a truly frame-unknown configuration); the 3-strand literature convergence (analysis-by-synthesis/Helmholtz-machine recognition+generation split; block-sparse RIP relaxing correlated-component coherence; classify-then-decode structured-prediction precedent); pre-registered HARD-PASS/HARD-FAIL bands; brain analogs (dual-stream ventral/dorsal); citations (12, verified); calibrated P_deflated = 0.42.

---

## Anchor candidate — single, ranked TOP (only one anchor this cycle; it is the decisive first-attempt test)

### ANCHOR_1 (TOP — cheapest decisive test, opens the comprehension capability class): frame_classify_then_known_decode_v1

- **Anchor pointer:** research note section "(b) Cheap decisive test," arm spec + falsifiable predictions.
- **Substrate-product reading:** ships a **frame-recognition step composed with the already-proven frame-known decoder** — together these form the substrate's first COMPREHENSION primitive (parse unknown input into role-filler structure), the missing complement to the working generation "mouth." The predicted frame is an inspectable intermediate object (glass-box, not a black-box embedding) — directly extensible to a confidence-gated refuse path (low frame-margin -> decline to parse), which composes with the substrate's existing epistemic-humility refuse-gate story and is a categorical LLM differentiator.
- **Tier hint:** **CONCEPTUAL_PROBE** until smoke; promotes to **MEASURED_MECHANISM** on any clean signal above the HARD-FAIL floor; promotes to **CHAIN_GRADE** only if HARD-PASS bands below are hit on FULL multi-seed. Default tier MIDDLE per Fix #28 — let cert-owner tier UP from observed metrics, do not self-promote from smoke.
- **Why now:** reuses TWO already-proven substrate assets (the block-local known-frame decoder, HARD_PASS 1.000 synthetic / 0.86 real-at-scale; and the dense-algebra blind-collapse baseline, HARD_FAIL 0.000, both already on disk — do NOT rerun these, cite them). The only new component is a cheap CPU-only matched-filter/centroid frame classifier. This is the single cheapest test that could open the entire comprehension capability class.
- **HARD-PASS:** frame_classification_accuracy >= 0.90 at F=8-16 candidate frames AND chained parse_accuracy >= 0.75, cv <= 0.05, >=3 seeds.
- **HARD-FAIL:** frame_classification_accuracy <= 0.40 OR chained parse_accuracy <= 0.15.
- **MIDDLE (informative, non-gating):** frame classification succeeds but chained decode underperforms (error-propagation / wrong-frame poisoning downstream — documented MoE-router-collapse-style failure mode in the lit scan); or frame accuracy degrades sharply with candidate count (this is Arm 4, the scaling sweep — run only after Arm 1-3 land, not gating the first HARD-PASS).
- **P_HARD-PASS / P_MIDDLE / P_HARD-FAIL = 0.42 / 0.33 / 0.25** (lit-scan calibrated per research note; novel-synthesis cap 0.50 honored; raw estimate 0.65 deflated 0.20 for uncharted-regime risk — no direct precedent tests VSA frame-recovery under real correlated fillers specifically).

---

## Recommended dispatch order

1. **Arm 1 (frame-classifier + known-decode, PRIMARY) + Arm 2/3 as CITED BASELINES (do not rerun — already on disk)** — ship as ONE cell first: `local_cpu_queue`, CPU-only smoke (~10-30 min), no GPU needed (classifier is a matched-filter/centroid comparison, not a trained network).
2. **Arm 4 (frame-count scaling sweep, 8/16/32/64...)** — DEFER until Arm 1 lands with a clean signal (either HARD-PASS or informative MIDDLE); this locates the classification-becomes-bottleneck transition the literature could not supply a number for.

---

## Context pointers

- Source research note (full math + mechanism + bands + brain analogs + citations + calibration):
  `notes/research_frontier_drill_comprehension_parse_unknown_structure_2026-07-05.md`
- Baseline collapse already on disk (cite, do not rerun):
  `data/exp_generation_decoder_roundtrip_v1/metrics.json` (`real_fullreso_hi` = 0.000, 3 seeds; `synth_fullreso_hi` = 1.000 IID control; `correlation_cone.real_mean_pair_cos` ~= 0.34)
  `data/exp_generation_decoder_gsbc_native_blocklocal_v1/metrics.json` (`dense_gsbc_fullreso` = 0.000; `blocklocal_gsbc` KNOWN-frame = 1.000 / 0.86 real-at-scale)
- Prior remedy flag (dense-to-sparse direction pre-registered BEFORE the 0.000 was measured — NOT novel; the novel part is the frame-unknown classify-then-decode hybrid test):
  `notes/decoder_design_stage_A_factor_B_order_C_cleanup_generation_readout_2026-07-05.md`
- Adjacent same-day synthesis (capacity-cliff location focus, does not cover the parsing/frame-unknown question):
  `notes/research_mechanism_envelope_blocklocal_generation_decoder_2026-07-05.md`
- Foundational envelope cell (the resonator machinery both above cells build on; F=3/F=4 factor-count wall, V=4096 vocabulary wall):
  `data/exp_factorization_envelope_v1/metrics.json`
- Proven-ceiling ancestor for the sparse block-local mechanism itself:
  `data/exp_substrate_sparse_resonator_blocklocal_K26_v1_n5000/metrics.json` (K=4/8/16/26 all 1.000, 3-seed)
- Bias master checklist (regime mismatch / basis-vs-use-case / saturation / band-calibration audits):
  `memory/feedback_experiment_bias_master_checklist_USER_2026-06-24.md`

---

## Contract section

- Pre-reg discipline per `[[feedback-envelope-expansion-fail-bands]]`: HARD-PASS + HARD-FAIL bands above are pre-registered HERE; exp_dev MUST lift them into the cell's prereg note verbatim before dispatch.
- Self-test per `[[feedback-formula-selftests]]`.
- Multi-seed FULL on smoke clearance (>=3 seeds).
- Queue routing: `local_cpu_queue` (CPU-only, cheap) for Arm 1 cell; defer Arm 4 to its own cell after Arm 1 lands.
- Ship via `bash tools/orchestrator/queue_add.sh <queue> <name> <script> <prereg> <timeout>`.
- Per-arm metrics-read per Fix #28 — DO NOT trust verdict_msg framing; read metrics.json per-arm (report frame-classification accuracy and conditional decode accuracy SEPARATELY, never collapsed to one aggregate) before any convergence claim.
- Post-ship REMOTE VERIFY per Fix #11 pipeline template (if dispatched remote; local_cpu_queue recommended here so this may not apply).
- Default tier MIDDLE per Fix #28; let cert-owner tier UP from observed metrics.
- BIAS-13 + BIAS-S regime audit MANDATORY in prereg: verify the frame-classifier's signal source is non-trivial before trusting a HARD-PASS — i.e. confirm the per-block occupancy signature is NOT degenerate/uniform across candidate frames at F=8-16 BEFORE running the full smoke (a regime-sanity self-test analogous to the WM-FM / soft-topK false-positive lessons: aggregate accuracy can look fine while the real signal source is degenerate).

---

## Autonomy declaration

exp_dev decides:
- Cell author (manual vs spawn cell-author sub-agent)
- Smoke seed + smoke timeout
- Exact F (candidate frame count) for the first attempt — recommend F=8 for the cheapest first smoke, F=16 for the FULL landing, consistent with the research note's "moderate cardinality" framing
- Classifier implementation detail (matched-filter vs nearest-centroid vs simple learned linear readout) — recommend the simplest non-learned option first (matched-filter/centroid) since the research note's mechanism claim rests on the geometry, not on a trained classifier
- N_DIM / V / D to match the existing `exp_generation_decoder_gsbc_native_blocklocal_v1` config (reuse for apples-to-apples comparison against the cited baselines) or extend if a smoke wall is hit
- Whether to bundle Arms 1-3 into one cell (recommended — Arms 2/3 are CITED, not rerun, so the cell only needs to execute Arm 1 and read the cited metrics.json files for comparison) or ship as fully separate cells
- Whether Arm 4 (scaling sweep) dispatch is gated on Arm 1 HARD-PASS or on any clean (non-degenerate) signal (recommend: any clean signal, including informative MIDDLE, since Arm 4 answers an open scaling question independently of whether Arm 1 itself clears HARD-PASS)

Research's authority ends at the anchor + bands + brain-mechanism math + lit citations + failure diagnosis. exp_dev is the cell-design authority.

Recommended FIRST dispatch: Arm 1 cell (frame-classify + known-decode, citing Arms 2/3 from disk) on `local_cpu_queue`. Arm 4 deferred until Arm 1 lands.

---

-- research
