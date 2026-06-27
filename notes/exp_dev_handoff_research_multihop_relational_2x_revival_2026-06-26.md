# exp_dev hand-off — research: multi-hop + relational composition 2x REVIVAL (6 anchors, 2 per HARD_FAIL)

**filed:** 2026-06-26
**trigger:** research 2x revival drill `notes/research_multihop_relational_2x_revival_drill_2026-06-26.md` filed against 3 HARD_FAILs:
- `data/exp_gap3_lars_vsa_relational_bottleneck_v1_n8192/metrics.json` (LARS-VSA Gap 3 compositional generalization)
- `data/exp_substrate_multihop_pfc_chunked_2hop_decomposition_v1/metrics.json` (PFC chunked 2-hop decomposition)
- `data/exp_substrate_multihop_csp_gated_iterated_cleanup_v1/metrics.json` (CSP-gated iterated cleanup)

The drill identifies THREE DISTINCT mechanism-grounded diagnoses (not one shared cap), each yielding TWO alternative-mechanism anchors that AVOID the specific failure mode. 6 anchors total, rank-ordered. Top-3 dispatch covers all 3 failure-classes once.

**pause state:** check `d:/AI/hd-instrument/data/orchestrator_paused.flag` before shipping any anchor. If paused, this hand-off is read-only structural context for the orchestrator to pick up post-resume; do NOT ship to queue until the flag is cleared and the orchestrator/USER confirms.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off names anchors and substrate-product readings; it does NOT prescribe cell-level experiment parameters. exp_dev owns the design call. The role of this file is to surface pre-registered HARD-PASS/HARD-FAIL bands so exp_dev can ship with confidence.

Per USER STRATEGIC PIVOT 2026-06-26: compositional understanding is the new primary track (language prediction CLOSED). RANK-1 anchor (A1 LARS-VSA + SOLAR + harness-fix) is the most USER-pivot-aligned: it directly tests typed-slot relational composition under a CLEAN harness.

---

## Anchor candidates (rank-ordered)

### ANCHOR 1 (RANK 1, addresses FAILURE 1: LARS-VSA / Gap 3 compositional gen)

**ANCHOR:** SOLAR Slot-Object-Linked Attention with HARNESS-FIX clean-heldout protocol (Webb-Russin-Cohen 2024 NeurIPS).

- substrate-product reading: keep the LARS-VSA RELBOTTLENECK relational-bottleneck binding (substrate has this primitive ch_587-588 chain-grade). REPLACE the leaky test harness: heldout (color, shape, position) tuples are CONSTRUCTED disjoint from train (no feature-level overlap). Add ARM_SOLAR_SLOT = SOLAR-style cross-attention slot-binding where learned slots independently bind to object-features via substrate's role-filler primitive (cleanup over slot-population x object-population independently rather than jointly). This tests TRUE compositional generalization with no harness contamination.
- tier hint: TIER-2 (wiring change + harness rewrite on existing relational-bottleneck primitive).
- why-now: RANK-1 across 6 candidates; highest USER-pivot alignment (compositional-understanding-first track); LARS-VSA cell was misclassified as failed due to harness leak — re-test under SOLAR clean harness IS the decisive cell. P_deflated=0.40.
- pre-registered HARD-PASS: ARM_RELBOTTLENECK_CLEAN mean >= 0.40 AND ARM_BASELINE_CLEAN <= 0.25 (chance) AND sd <= 0.06; ARM_SOLAR_SLOT > ARM_RELBOTTLENECK_CLEAN + 0.05.
- pre-registered HARD-FAIL: ARM_RELBOTTLENECK_CLEAN <= 0.22 (no detectable lift over chance) AND ARM_SOLAR_SLOT <= 0.30. If true, the relational-bottleneck does not generalize on substrate at production scale.
- pre-registered MIDDLE_BAND: 0.25 < ARM_RELBOTTLENECK_CLEAN < 0.40 (some generalization but not robust); follow up with capacity sweep.
- cost: ~3-4 hr CPU at N=8192 x 200 train x 100 heldout x 5 seeds (matmul-bound; route via remote_cpu per Fix #24 if matmul dominates).
- risk class: structural-test-rewrite. LOW (no new primitive; harness construction is the load-bearing change).
- lane: COMPOSITIONAL_TEST_synthetic_clean_heldout.
- corpus_provenance: synthetic_5cat_200train_100heldout_VC200_VP10_K64_N8192_seeds_0_to_4 with GUARANTEED disjoint-feature heldout.

### ANCHOR 2 (RANK 2, addresses FAILURE 2: PFC chunked 2-hop multi-hop extension)

**ANCHOR:** HOLOGRAPHIC CHUNK PACKING via Plate pre-computed chunk convolution (TRAINING-TIME ORTHOGONALIZATION).

- substrate-product reading: during chain ingest, in ADDITION to storing single-hop (s, p, o) triples in W, ALSO store 2-hop CHUNK ATOMS: chunk_atom = bind(s, p1, intermediate, p2, o) for each 2-hop sub-chain in the training corpus, bound to a chunk-role identifier. Query-time 5-hop = lookup 2 chunk atoms (covering hops 1-2 and 3-4) + 1 single hop (hop 5). Chunks are PRE-CLEANED at storage time — query is direct chunk-role lookup with single-step accuracy. Brain analog: Eichenbaum 2017 hippocampal relational memory (events stored as chunked episodes addressable by event-id, NOT reconstructed from per-step traversal).
- tier hint: TIER-2 (training-time orthogonalization on top of existing W storage; no new primitive).
- why-now: RANK-2 across 6 candidates; addresses the per-2-hop primitive saturation cap (chunk-1 acc 0.54 at production V_C=200) by moving the load-bearing computation from query-time to training-time; complementary to RANK-1 (different failure mode). P_deflated=0.40.
- pre-registered HARD-PASS: ARM_HOLOGRAPHIC_CHUNK_PACKED depth-5 >= 0.50 AND sd <= 0.06 AND > ARM_PFC_CHUNKED_RAIL + 0.30.
- pre-registered HARD-FAIL: ARM_HOLOGRAPHIC_CHUNK_PACKED depth-5 <= 0.25 OR adds <= 0.05 over PFC_CHUNKED_RAIL (refutes chunk-packing advantage).
- pre-registered MIDDLE_BAND: 0.30-0.50.
- cost: ~3-4 hr CPU (one-time training pre-compute chunks ~1hr; query is fast).
- risk class: structural-storage-extension. LOW (chunks stored in same W format).
- lane: PRIMITIVE_TEST_synthetic_apples_to_apples.
- corpus_provenance: substrate_multihop_pfc_chunked rail config (V_C=200, V_P=10, K_SET=20, n_chains=200, N=8192).

### ANCHOR 3 (RANK 3, addresses FAILURE 3: CSP-gated iterated cleanup)

**ANCHOR:** ANNEALED LANGEVIN / REVERSE DIFFUSION CLEANUP (DDPM-style monotone denoising).

- substrate-product reading: replace CSP-gated iter-cleanup-with-additive-noise with N=10 REVERSE DIFFUSION STEPS per hop. Each step: x_{t-1} = x_t - step_size * (x_t - argmax_atom_similarity(x_t)) + noise_t where noise_t decreases linearly from initial to 0. The "score function" is the substrate's W-cleanup; the noise schedule is the new control. NO refuse-gate — readout always returns the diffusion final state (eliminates the refuse-as-wrong penalty). Brain analog: CA3 attractor dynamics (Rolls 2013) are exactly annealed Langevin — recurrent collateral IS a learned score function; basin descent IS reverse-diffusion; theta-gamma annealing implements the temperature schedule.
- tier hint: TIER-2 (replaces cleanup primitive with diffusion variant; no new dependency).
- why-now: RANK-3 across 6 candidates; addresses both CSP-gated failures simultaneously (refuse-gate punishment AND additive iter-noise) by replacing with a mechanism that has MONOTONE noise-reduction guarantees. P_deflated=0.35.
- pre-registered HARD-PASS: ARM_DIFFUSION_DENOISE depth-2 >= 0.65 (matches baseline; no penalty from denoising) AND depth-5 >= 0.40 AND no refuse mechanism.
- pre-registered HARD-FAIL: ARM_DIFFUSION_DENOISE depth-2 <= 0.50 (denoising HURTS the well-resolved 2hop case) OR depth-5 <= 0.20.
- pre-registered MIDDLE_BAND: depth-5 in 0.25-0.40.
- cost: ~4-5 hr CPU (10 diffusion steps per hop x depth x chains).
- risk class: structural-cleanup-replacement. MEDIUM (cleanup primitive replacement risks; mitigated by depth-2 sanity rail).
- lane: PRIMITIVE_TEST_synthetic_apples_to_apples.
- corpus_provenance: substrate_multihop_csp_gated rail config (V_C=200, V_P=10, K_SET=20, n_chains=200, N=8192, depths 2/5/10).

### ANCHOR 4 (RANK 4, dispatch CONDITIONAL on RANK-1 outcomes; FAILURE 1 complementary)

**ANCHOR:** TENSOR-PRODUCT REPRESENTATION (TPR) with Smolensky-Schlag 2020 attention readout.

- substrate-product reading: substrate currently uses HRR convolution-bind as default. TPR is the OUTER-PRODUCT alternative: store atom outer products in W of shape (N_DIM, N_DIM) where each W = sum_k filler_k tensor role_k. Unbind via W @ role_query then cleanup over filler codebook. For composition: composite = sum over slots of (slot_filler tensor slot_role). Query for filler in slot X = (composite @ role_X.T) cleaned up. ARM_TPR_ATTENTION adds Schlag-Schmidhuber fast-weight attention readout. Brain analog: cortical conjunctive coding via dendritic tensor-product (Larkum 2013).
- tier hint: TIER-2/TIER-3 boundary (TPR storage at N=8192 needs N x N matrix per relation = 64M floats; memory-heavy).
- why-now: dispatch ONLY if RANK-1 SOLAR HARD_PASSes (validates compositional generalization mechanism); TPR then demonstrates that outer-product binding may exceed HRR convolution for slot-binding. Alternatively dispatch if RANK-1 MIDDLE_BAND (TPR provides higher-capacity alternative). P_deflated=0.35.
- pre-registered HARD-PASS: ARM_TPR_OUTER_PRODUCT mean >= 0.45 on CLEAN heldout AND ARM_TPR_ATTENTION > ARM_TPR_OUTER_PRODUCT + 0.05.
- pre-registered HARD-FAIL: ARM_TPR_OUTER_PRODUCT <= 0.25 OR TPR adds <= 0.05 over HRR (refutes outer-product advantage).
- pre-registered MIDDLE_BAND: 0.28-0.45.
- cost: ~4-5 hr CPU (W = N x N outer product is memory-heavy at N=8192; route via remote_cpu).
- risk class: structural-storage-format-change. MEDIUM (storage scaling).
- lane: COMPOSITIONAL_TEST_synthetic_clean_heldout.
- corpus_provenance: as ANCHOR 1.

### ANCHOR 5 (RANK 5, dispatch CONDITIONAL on RANK-3 outcomes; FAILURE 3 complementary)

**ANCHOR:** PREDICTIVE-CODING HIERARCHICAL FREE-ENERGY MINIMIZATION (Friston-Bastos canonical microcircuit).

- substrate-product reading: treat each hop as a predictive-coding layer. Forward pass: hop-k generates prediction for hop-k+1 via W; hop-k+1 cleans up and produces prediction error e_{k+1} = (actual - predicted); error propagates back to refine hop-k's state. Iterate 5-8 PC sweeps until prediction errors converge. Final readout = MAP estimate (argmax over endpoint cleanup). NO refuse mechanism, NO additive noise; uses GRADIENT-DESCENT on free energy (monotone descent guaranteed). Per-layer free-energy IS the confidence signal (no separate CSP gate needed). Brain analog: cortical predictive coding (Bastos-Friston 2012, Keller-Mrsic-Flogel 2018).
- tier hint: TIER-2 (PC sweeps add iteration cost; substrate has W cleanup as the prediction primitive).
- why-now: dispatch ONLY if RANK-3 DIFFUSION HARD_PASSes (validates monotone-descent denoising direction); PC then demonstrates brain-validated extension with built-in confidence-readout. Alternatively dispatch if RANK-3 MIDDLE_BAND. P_deflated=0.35.
- pre-registered HARD-PASS: ARM_PC_HIERARCHICAL depth-5 >= 0.40 AND depth-2 >= 0.65 (no degradation on well-resolved case) AND free-energy-correlation-with-correctness > 0.5.
- pre-registered HARD-FAIL: depth-5 <= 0.20 OR free-energy uninformative (correlation < 0.2).
- pre-registered MIDDLE_BAND: depth-5 in 0.25-0.40.
- cost: ~4-5 hr CPU (8 PC sweeps per chain x depth x chains).
- risk class: structural-iteration-loop. MEDIUM (PC convergence tuning).
- lane: PRIMITIVE_TEST_synthetic_apples_to_apples.
- corpus_provenance: as ANCHOR 3.

### ANCHOR 6 (RANK 6, dispatch CONDITIONAL on RANK-2 outcomes; FAILURE 2 complementary)

**ANCHOR:** HIERARCHICAL SUCCESSOR REPRESENTATION (HSR) with multi-scale W^k.

- substrate-product reading: at training time, compute STACK of closure matrices at different temporal scales: M_1=W; M_3 = W + 0.5 W^2 + 0.25 W^3; M_5 = W + 0.5 W^2 + 0.25 W^3 + 0.125 W^4 + 0.0625 W^5; M_7 similarly. Query depth-k uses M_k that matches query depth. Per-relation variant: M_5^p = (W_p)^5 for relation-specific 5-hop. Brain analog: dorsal-to-ventral hippocampal axis encodes increasing spatial scale (Strange-Witter 2014); multi-scale grid modules (Hafting 2005).
- tier hint: TIER-2 (multi-scale closure extends prior SR-closure single-aggregate angle 2026-06-22).
- why-now: dispatch ONLY if RANK-2 HOLOGRAPHIC-CHUNK-PACK HARD_PASSes (validates training-time pre-computation direction); HSR then provides multi-scale composition that combines with chunks. Alternatively dispatch if RANK-2 MIDDLE_BAND. P_deflated=0.35.
- pre-registered HARD-PASS: ARM_HSR_MULTISCALE depth-5 >= 0.45 AND > ARM_SR_CLOSURE_SHARED + 0.10.
- pre-registered HARD-FAIL: ARM_HSR_MULTISCALE depth-5 <= 0.20 OR adds <= 0.05 over single-M SR.
- pre-registered MIDDLE_BAND: 0.25-0.45.
- cost: ~3-4 hr CPU (4 closure matrices stored).
- risk class: structural-storage-extension. LOW.
- lane: PRIMITIVE_TEST_synthetic_apples_to_apples.
- corpus_provenance: as ANCHOR 2.

---

## Recommended dispatch sequence

1. **IMMEDIATE (1 cycle, highest USER-pivot alignment):** RANK-1 A1 SOLAR + HARNESS-FIX. Compositional understanding is the new primary track per USER pivot 2026-06-26; this is the most direct decisive test. Single 3-arm cell.

2. **PARALLEL (1 cycle, complementary failure modes):** RANK-2 P1 HOLOGRAPHIC-CHUNK-PACK + RANK-3 C1 ANNEALED-LANGEVIN-DIFFUSION. Both target the per-hop primitive itself (P1 via training-time orthogonalization, C1 via monotone-descent denoising). Combined verdicts diagnose primitive-replacement vs composition-restructure. Two separate 3-arm cells (different infrastructure).

3. **CONDITIONAL (cycle 2-3):**
   - RANK-4 A2 TPR: dispatch if RANK-1 HARD_PASSes (demonstrate TPR > HRR for slot-binding).
   - RANK-5 C2 PC HIERARCHICAL: dispatch if RANK-3 HARD_PASSes (PC = brain-validated extension of monotone denoising with built-in confidence).
   - RANK-6 P2 HSR MULTI-SCALE: dispatch if RANK-2 HARD_PASSes (multi-scale closure composes with chunks).

4. **PIVOT:** if RANK-1 + RANK-2 + RANK-3 ALL HARD_FAIL, the conclusion is per-hop primitive itself is the structural cap. Re-route to gap1 5x ANCHOR 6 (dense Hopfield + sparse-bipolar dictionary primitive replacement) per the gap1 drill's PIVOT path.

---

## Context pointers (file paths, not summaries)

- Research drill: `d:/AI/hd-instrument/notes/research_multihop_relational_2x_revival_drill_2026-06-26.md`
- Three HARD_FAIL metrics:
  - `d:/AI/hd-instrument/data/exp_gap3_lars_vsa_relational_bottleneck_v1_n8192/metrics.json`
  - `d:/AI/hd-instrument/data/exp_substrate_multihop_pfc_chunked_2hop_decomposition_v1/metrics.json`
  - `d:/AI/hd-instrument/data/exp_substrate_multihop_csp_gated_iterated_cleanup_v1/metrics.json`
- Parent drills (deconflict; do NOT re-cover):
  - `d:/AI/hd-instrument/notes/research_gap1_multihop_5x_drill_2026-06-26.md` (LDPC-bidir / RTS smoother / VTE-MCTS / MPS / particle-filter / dense-Hopfield PIVOT)
  - `d:/AI/hd-instrument/notes/exp_dev_handoff_research_gap1_multihop_5x_drill_2026-06-26.md` (gap1 dispatch hand-off)
  - `d:/AI/hd-instrument/notes/research_multihop_revival_5x_drill_2026-06-25.md` (4-for-4 HARD_FAIL diagnosis)
  - `d:/AI/hd-instrument/notes/research_resonator_hard_fail_revival_disparate_fields_2026-06-24.md` (soft-DFE / K-beam / PageRank / turbo / RG / resonator-fact)
  - `d:/AI/hd-instrument/notes/research_brain_drill_substrate_native_relational_semantic_encoding_5x_DEEPER_2026-06-22.md` (Random Indexing + BEAGLE + ATL hub-spoke)
- USER pivot frame:
  - `d:/AI/hd-instrument/notes/research_STRATEGIC_PIVOT_language_track_closed_compositional_understanding_opens_2026-06-26.md`
- Companion drill (already dispatched today):
  - `d:/AI/hd-instrument/notes/exp_dev_handoff_research_compositional_understanding_drill1_typed_KG_composition_2026-06-26.md` (composable with RANK-1 A1; both test compositional generalization)

---

## Contract section

- All 6 anchors carry pre-registered HARD-PASS + HARD-FAIL.
- Sanity rail MANDATORY for every cell (per failure-specific anchor — LARS chance=0.20 for clean-harness baseline; multi-hop 0.122-0.145 at depth-5 single-chain; multi-hop 0.65+/-0.03 at depth-2 naive). If sanity rail fails, the cell is REJECTED before any anchor verdict is computed (test-design discipline per [[feedback-fix28-recurring-skunkworks-correct-more-than-director]]).
- Per-arm metrics.json must be readable independently; verdict_msg framing must NOT propagate cross-arm narratives without per-arm metric verification (Fix #28).
- Cell-author smoke is MANDATORY before full dispatch (Fix #17 measurement; per [[feedback-cell-author-smoke-and-dispatch-route-via-orchestrator-for-heavy-cells]] route via remote_cpu/orchestrator for matmul-bound TPR / SOLAR cells at N_DIM=8192).
- Use `tools/peek_arm_metrics.py` before any tier/framing claim (per [[feedback-use-peek-arm-metrics-before-framing]]).
- Default UNDER-claim classification (per [[feedback-fix28-violation-count-internalize-harder]]); let Skunkworks tier UP.
- CSP-gated revival anchors (C1, C2) MUST NOT use refuse-as-wrong scoring — readout must distinguish refused / correct / wrong (META finding from this drill).
- LARS harness anchors (A1, A2) MUST construct heldout with VERIFIED zero feature-overlap with train; baseline arm on heldout MUST be at chance +/-0.05 or the harness is rejected.

## Autonomy declaration

exp_dev owns:
- Cell-author parameter selection (within pre-registered bands).
- Smoke vs full-run dispatch decision (per Fix #17 measurement-strict).
- Combine-into-one-cell vs separate-cells decision (recommend SEPARATE cells per anchor — different infrastructure; RANK-1 = LARS harness; RANK-2 = chunk storage; RANK-3 = diffusion loop).
- Dispatch routing (local_cpu vs remote_cpu vs overnight_queue per Fix #24 GPU-must-use-GPU + Fix #14 spawn-budget <= 3 in-flight).
- Sanity-rail rejection logic (if BASELINE doesn't reproduce its anchor, REJECT the cell and re-author).
- Cell-name convention per anchor.

Research does NOT own:
- Cell parameters (defer to exp_dev).
- Dispatch timing (defer to orchestrator pause-state).
- Per-cell hyperparameter tuning (defer to exp_dev).
- Verdict classification (defer to Skunkworks per A5 role-separation).
- Read-out scoring schema (defer to Skunkworks for the refuse/correct/wrong tri-class).
