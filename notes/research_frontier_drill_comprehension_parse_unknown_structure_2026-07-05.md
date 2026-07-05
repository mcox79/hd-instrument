# Frontier drill: COMPREHENSION — parsing an unknown bound proposition into its role-filler structure

**Filed-by:** research
**Filed-at:** 2026-07-05
**Trigger:** USER frontier-drill directive — "open the COMPREHENSION capability, the substrate's missing complement to the now-working generation mouth." Brain-first per standing steer.

---

## (a) HEADLINE

The measured 0.000 blind-factorization collapse on real correlated fillers is an **algebra/geometry artifact**, not an information-theoretic wall — the identical content decodes to 1.000 under IID synthetic fillers with the *same* dense algebra, and decodes to 1.000 (synthetic) / 0.86 (real, V=8192/D=26) once the frame is KNOWN and the geometry is sparse-block. What has never been tested is whether frame RECOVERY itself (not just frame-conditioned decode) survives real filler correlation when no external position cue is given. Three independent literature strands converge on the same fix: split "blind factorization" into (1) a cheap discrete frame-classifier (recognition step, brain-grounded as the ventral/comprehension pathway or Helmholtz-machine recognition net) followed by (2) the ALREADY-PROVEN frame-known decoder (the generation "mouth," reused as the generative/synthesis half). This is the Helmholtz-machine / analysis-by-synthesis split and the FrameNet frame-ID-then-argument-extraction pattern, applied to VSA role-filler parsing for the first time. Genuinely untested; not yet a proven wall, not yet a proven capability.

---

## (b) Cheap decisive test

**Cell (first attempt): `frame_classify_then_known_decode_v1`**

Reuse the existing real correlated-filler dataset/config from `exp_generation_decoder_gsbc_native_blocklocal_v1` (native GSBC fillers, sparse block-local geometry, the same real content that collapsed to 0.000 under the dense blind resonator and hit 1.000/0.86 under known-frame block-local decode).

- **Setup:** construct a MODERATE candidate frame-set (start with F=8-16 distinct block-to-role assignments — literature's comfort zone for classify-then-decode is "tens," not thousands; going bigger is Arm 4, not the first attempt). Each trial: bind real correlated fillers under one frame drawn from the candidate set, present the bound vector WITHOUT the frame label.
- **Arm 1 (PRIMARY, new):** Frame-classifier + known-decode hybrid. Classifier = cheap matched-filter / nearest-centroid over per-block occupancy signature (block energy or block-sparsity pattern read directly off the bound vector — no learned weights needed for the first attempt; this is the "coarse" recognition step). Feed the predicted frame into the already-proven block-local decoder.
- **Arm 2 (baseline, ALREADY ON DISK — cite, do not rerun):** dense blind full-resonator, `real_fullreso_hi` / `dense_gsbc_fullreso` arms of `exp_generation_decoder_roundtrip_v1` / `exp_generation_decoder_gsbc_native_blocklocal_v1` — exact_ordered = 0.000 (3 seeds each).
- **Arm 3 (ceiling, ALREADY ON DISK — cite, do not rerun):** known-frame block-local decode — `blocklocal_gsbc` arm, exact_ordered = 1.000 (synthetic-scale) / 0.86 (real, V8192/D26).
- **Arm 4 (second attempt, scaling sweep — not gating the first HARD-PASS):** frame-classification accuracy vs candidate-frame-count (8/16/32/64/…) to locate the "classification becomes the bottleneck" transition that the classify-then-decode literature flags as real but numerically uncharted.

**Metric:** `parse_accuracy` = P(frame_predicted == frame_true AND exact_ordered_decode == 1 | frame_predicted). Report frame-classification accuracy and conditional decode accuracy SEPARATELY (per Fix #28 — never collapse to one aggregate number).

**Compute:** CPU-only, ~10-30 min smoke. The classifier is a matched-filter/centroid comparison (O(V·F) per trial, F small) — no GPU needed for the first attempt; this is what makes it the CHEAP decisive test rather than a training run.

---

## (c) Falsifiable predictions

**HARD-PASS:** frame_classification_accuracy ≥ 0.90 on real correlated fillers at F=8-16 AND chained `parse_accuracy` ≥ 0.75, cv ≤ 0.05 across ≥3 seeds. (Slack below the 0.86-1.00 known-frame ceiling is expected — chaining two stages costs some accuracy per the classify-then-decode literature, but should stay close.)

**HARD-FAIL:** frame_classification_accuracy ≤ 0.40 (well above chance-for-8 = 0.125, but not useful) OR chained `parse_accuracy` ≤ 0.15 (no meaningfully better than the blind-resonator 0.000 floor). This would mean real-filler correlation confounds the frame SIGNAL itself, not just the dense decode algebra — a genuinely harder finding than anything measured so far.

**MIDDLE/PARTIAL (informative, not gating):** frame-classification succeeds but chained decode underperforms → error-propagation from wrong-frame poisoning downstream decode (the MoE-router-collapse failure mode, documented in the classify-then-decode literature). OR frame accuracy degrades sharply with candidate count (Arm 4) → locates the real numeric threshold literature could not supply.

---

## (d) Cross-thread synthesis

**Substrate corpus (verified this session):**
- `data/exp_generation_decoder_roundtrip_v1/metrics.json` (HARD_PASS overall, 3 seeds {7,13,19}, V1024/D3/N8192): `real_fullreso_hi` (dense, positions unknown, real fillers) = exact_ordered 0.000/0.000/0.000, identical across seeds. `synth_fullreso_hi` (same dense algebra, IID fillers) = 1.000 — proves the collapse is filler-correlation-driven, not a wiring bug. `correlation_cone.real_mean_pair_cos` ≈ 0.34 across seeds.
- `data/exp_generation_decoder_gsbc_native_blocklocal_v1/metrics.json` (HARD_PASS): `dense_gsbc_fullreso` (dense, positions unknown, native GSBC fillers) = 0.000, reproducing the collapse with a second filler source. `blocklocal_gsbc` (sparse block-local, KNOWN frame — position IS the block index, fixed at decode) = 1.000; real-content boundary run V8192/D26 = 0.86.
- **Critical gap identified by the corpus scour:** the block-local HARD_PASS is NOT a frame-unknown test — the block index carries position, known at decode. The genuinely frame-unknown ("recover both WHAT and HOW") task has ONLY ever been run with the dense algebra (0.000, twice). It has never been attempted with sparse-block geometry in a truly frame-unknown configuration. That is the gap this cell closes.
- `notes/decoder_design_stage_A_factor_B_order_C_cleanup_generation_readout_2026-07-05.md` already flagged sparse-block as the expected remedy BEFORE the 0.000 was measured — so the dense→sparse direction is NOT novel. What IS novel: the frame-unknown classify-then-decode hybrid test itself, and the analysis-by-synthesis/Helmholtz-machine framing (absent from the same-day adjacent note `research_mechanism_envelope_blocklocal_generation_decoder_2026-07-05.md`, which focused on capacity-cliff location, not the parsing problem).
- cap_map has no row yet for comprehension/parsing (latest v597 predates this arc). An unrelated "comprehension wall" exists for ASDiv math-word-problem operand-selection (closed at 0.385) — different problem class, not role-filler VSA parsing.

**Literature (3 parallel Sonnet lit-scans, generic-term search only):**
1. **Analysis-by-synthesis / Bayesian brain** (Yuille & Kersten 2006; Bever & Poeppel 2010; Rao & Ballard 1999; Friston free-energy; Dayan/Hinton/Neal/Zemel 1995 Helmholtz machine; Hickok & Poeppel dual-stream). Consistent finding: naive generate-and-check does NOT scale — every working system pairs a cheap recognition/amortized front end with the generative model as verifier. Dual-stream anatomy (ventral=comprehension, dorsal=production) is textbook-level support for architecturally separating a comprehension pathway from the production pathway already built.
2. **Correlated-component factorization** (sparse component analysis vs ICA; Donoho/Elad/Tropp mutual coherence; Eldar & Mishali block-RIP; Frady/Kent/Olshausen/Sommer 2020 resonator networks). Well-established: correlation between dictionary/filler components raises effective coherence and shrinks recoverable sparsity in DENSE unstructured codes; block/local-support structure provably relaxes this penalty. Counter-calibration: Hopfield/dense-associative-memory literature (Bielmeier & Friedland 2026) shows correlation-driven capacity loss is typically SMOOTH/graded via reduced effective dimensionality, not a sharp cliff — temper expectation of a clean pass/fail boundary.
3. **Classify-then-decode structured prediction** (FrameNet frame-ID-then-argument-extraction; intent+slot filling; Petrov & Klein coarse-to-fine parsing; HMM known-vs-unknown topology; MoE gating). Well-established, ~15-year-old engineering pattern. Coarse-to-fine parsing loses near-zero accuracy vs. full joint search while cutting cost by orders of magnitude — the strongest positive evidence for this drill. Documented failure mode: wrong-frame classification poisons downstream decode (MoE router collapse) — this is the real risk, matched to the MIDDLE-band prediction above. No paper gives a numeric template-count threshold before classification itself becomes the bottleneck — flagged explicitly as open/speculative, hence Arm 4.

**Why this beats the plain resonator's 0.000, mechanistically:** the plain/dense resonator fails for two compounding reasons — (i) it uses a dense multiplicative-binding algebra that entangles all fillers into one interference-prone representation, and correlated real fillers collapse into an indistinguishable cone (cos≈0.34); (ii) it tries to solve a continuous combinatorial SEARCH problem (find the unknown binding) rather than a finite CLASSIFICATION problem. The hybrid fixes both at once: sparse block-local geometry is the mechanism the block-RIP literature says relaxes correlated-component coherence (independently already proven to reach 1.000/0.86 once frame is known), and classify-then-decode converts blind search into finite discrete classification, the exact pattern shown to cost near-zero accuracy in NLP structured prediction. It also reuses, rather than reinvents, the proven decoder — literally the Helmholtz-machine recognition/generation split.

---

## (e) Substrate-product implications

Comprehension is the substrate's missing complement to generation — together they form a full read/write capability: recognition (classify frame) + generation (already-proven decoder used as the synthesis/verification step). If the hybrid clears HARD-PASS, the substrate ships an auditable, glass-box parse pipeline: the predicted frame is an inspectable intermediate object (not a black-box embedding), and a confidence-gated refuse path is a direct extension (low frame-classification margin → decline to parse rather than confabulate a wrong structure) — this composes with the substrate's existing epistemic-humility refuse-gate story and is a categorical LLM differentiator (LLMs do not expose an inspectable "which frame did I choose" step). If it lands only PARTIAL, the substrate still gains a concrete, quantified boundary (frame cardinality vs. classification accuracy) that upper-bounds near-term comprehension claims honestly rather than by assertion.

**Achievability — honest read:** not proven a wall, not proven solved. The ceiling for CONTENT decode is proven (1.000 synthetic, 0.86 real-at-scale) once frame is known, and the dense-algebra collapse is demonstrably an encoding artifact rather than an info-theoretic limit (identical content survives under IID fillers with the same algebra). What's unproven is whether FRAME recovery specifically survives real filler correlation absent an external position cue. Brain existence-proof (dual-stream separation of comprehension from production, implemented via a recognition+generative split per Helmholtz-machine theory) establishes this is achievable in at least one working system — but only demonstrated at moderate structural cardinality; the literature explicitly does not establish where large-cardinality frame-search becomes intractable again, so scaling past a small candidate set is a real, uncharted engineering risk, not a resolved question either way.

---

## (f) Citations (verified count: 12)

1. Yuille & Kersten, "Vision as Bayesian inference: analysis by synthesis?", TICS 2006
2. Bever & Poeppel, "Analysis by Synthesis: A (Re-)Emerging Program for Language and Vision," Biolinguistics 2010
3. Rao & Ballard, hierarchical predictive coding, 1999
4. Friston, free-energy/variational Bayesian-brain framework (2005-2010s)
5. Dayan, Hinton, Neal, Zemel, "The Helmholtz Machine," 1995
6. Hickok & Poeppel, dual-stream model of speech/language, ventral/dorsal
7. Donoho / Elad / Tropp, mutual coherence and sparse recovery (~2003-2006)
8. Eldar & Mishali, block-sparse RIP (~2009)
9. Frady, Kent, Olshausen & Sommer, resonator networks for VSA factorization, Neural Computation 2020 (Parts 1-2)
10. Bielmeier & Friedland, correlated-pattern capacity in dense associative memory, arXiv:2508.01395 (2026)
11. Petrov & Klein, coarse-to-fine parsing, EECS-2009-116; Rush & Petrov, vine pruning, NAACL 2012
12. FrameNet frame-identification-then-argument-extraction pipeline literature (Das et al. lineage; arXiv:1901.07475, arXiv:2212.02036)

Calibration note per lit-scan-calibration-penalty: raw estimate for this novel-synthesis hybrid (~0.65, based on independently-proven ceiling + well-established coherence-relaxation mechanism + near-zero-cost classify-then-decode precedent) deflated by 0.20 for uncharted-regime risk (no direct precedent tests VSA frame-recovery under real correlated fillers specifically) → **P_deflated = 0.42**, under the 0.50 novel-synthesis cap.

---

-- research
