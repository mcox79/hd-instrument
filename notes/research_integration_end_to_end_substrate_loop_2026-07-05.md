# Research: does perception->memory->reasoning->generation compose end-to-end?

Date: 2026-07-05. Owner: research (Opus synthesis over substrate scour + 2 parallel Sonnet lit-scans).

## HEADLINE

**Partial compose, one real seam.** Three of four hand-offs are clean or smoke-verified same-algebra;
the fourth (reasoning-output -> generation-input) is a genuine cross-algebra seam that has never been
tested end-to-end, and both external literatures (neuroscience + VSA/HDC) independently say naive/fixed
bridges across mismatched codes lose real fidelity (measured: up to 16.2 points in a directly-analogous
published system) while co-trained/learned bridges do not. This is not a fundamental algebra-incompatibility
(compose-forever-impossible); it is an unbuilt/untested bridge, with a strong prior on which bridge design
survives.

## Interface-bridge map (4 hand-offs)

1. **Encoder (GSBC sparse block, ~2.3% active) -> Memory store.** CLEAN, smoke-verified.
   `exp_regime_switch_encoder_instore_integration_verify_v1` (HARD_PASS, smoke) proves the sparse-key
   algebra survives real Store serialization + reload (Gate B delta=0.0000) and in-store retrieval matches
   offline within 0.001, using real `hdlab.binding` HRR circular-conv key algebra. Caveat: verified for the
   *regime-switch* encoder variant on a smoke checkpoint, not yet the current GSBC_EXPAND2X encoder at FULL.
   No transform needed -- same key algebra in and out.
2. **Memory -> Reasoning.** SAME algebra, no bridge. `exp_deep_reasoning_hub_robustness_v1` (CHAIN_GRADE)
   runs chained bind/unbind/cleanup directly over REAL stored atoms in bipolar-BSC -- the reasoning
   codebook IS the stored-atom codebook. This is the strongest joint in the pipeline.
3. **Reasoning -> Generation. THE SEAM.** Reasoning composes/binds in bipolar-BSC (elementwise product,
   wave14b/e). The dense generation decoder (`exp_generation_decoder_roundtrip_v1`) is algebra-matched to
   this (no transform) but its own header flags binding directly in GSBC's sparse-block geometry as
   explicitly "OUT OF SCOPE... v2 STRATEGIC path" -- and per the COMPREHENSION frontier drill it collapses
   to 0.000 on blind/frame-unknown factorization, cliffing hard at F>=3 factors (0.217) and dead at F=4.
   The NEW block-local decoder (today's HARD_PASS, exact-ordered up to 1.000) is algebra-matched to the
   *encoder* instead (GSBC-native block-local), not to reasoning's bipolar-BSC output -- and its own
   HARD_PASS still assumes a *known* frame/block-index, i.e. it has not been fed genuine reasoning-composed
   output either. No cell has ever wired reasoning's bipolar-BSC composed output into either decoder as a
   true end-to-end chain.
4. **Cross-domain caution.** `substrate_kg_khop_gpu_scale_v1` shows a *same-algebra* CPU->GPU hand-off can
   silently collapse to 0.000 from a setup mismatch alone -- hand-offs fail quietly even without an algebra
   change; every seam needs its own gate, not just component-level verification.

## Brain grounding (2 parallel lit-scans, generic terms, calibration-penalized)

Both scans converge: biology does NOT use one shared code across regions -- it uses explicit, often
**learned** bridge transforms, and cascaded translation compounds error.
- **Communication subspace** (Semedo et al., *Neuron* 2019): downstream areas read a fixed low-rank linear
  projection of upstream activity, not the full code -- bridge-transform, not shared code.
- **Thalamic relay** (Sherman & Guillery; Halassa & Kastner, *Nat. Neurosci.* 2017): thalamus is an actively
  gated switchboard/basis-change layer between cortical areas, not a passive pass-through.
- **Hippocampal-neocortical dialogue** (McClelland/McNaughton/O'Reilly 1995; Kumaran/Hassabis/McClelland,
  *TICS* 2016; Teyler & DiScenna indexing theory): sparse hippocampal code is reformatted into distributed
  cortical code via replay-driven interleaved learning over time -- a trained bridge, converging toward
  shared code only asymptotically.
- **Alignment/compounding** (Procrustes/CCA literature; BCI realignment: Degenhart 2020, Farshchian 2023;
  concatenated-coding theory): each bridge hop is lossy; stacking hops compounds loss (data-processing
  inequality) unless errors are decorrelated by design.
VSA/HDC lit-scan (independent second agent) reaches the SAME structural conclusion with a directly
quantitative analog: Hersche et al. (*Nat. Nanotech.* 2023; NAI 2025) bridge a dense CNN embedding into a
sparse block-code resonator and measure the cost of a naive/analytic bridge vs a co-trained one -- naive
bridging cost **16.22 accuracy points** (54.54% vs 65.09%) on the SAME task. Resonator Networks (Frady/Kent/
Olshausen/Sommer 2020) assume one fixed algebra end-to-end; RNS-HDC (Kymn et al. 2024) is a shared-format
success case (same algebra, only moduli differ). Consistent verdict across both scans: bridge-transform is
viable, but only when co-trained/learned, not when bolted on as a fixed analytic map.

## Cheap decisive end-to-end test (spec)

Minimal glass-box loop, CPU-only, reusing already-built primitives (no new mechanism):
encode SVO fact (GSBC) -> store (proven interface #1) -> 1-hop query+reason in bipolar-BSC over real
atoms (proven interface #2) -> feed the reasoning-recovered atom into BOTH generation decoders as separate
arms -> measure spoken-answer-matches-stored-fact.
- **Arm A (no-bridge, dense-matched):** reasoning output straight into `exp_generation_decoder_roundtrip_v1`
  (same bipolar-BSC algebra, zero transform).
- **Arm B (naive analytic bridge):** reasoning output re-projected into block-local GSBC geometry via a
  fixed argmax-into-nearest-codebook-atom step (the cheapest possible bridge, matching the "naive" arm the
  literature says loses ~16pts), then fed to the block-local decoder.
- **Arm C (positive control):** skip reasoning, feed the STORED atom directly to each decoder (isolates
  reasoning-induced degradation from bridge-induced degradation).
Metric: end-to-end exact round-trip accuracy (spoken tokens == stored SVO), 3 seeds, real correlated
concept fillers (not synthetic iid).

## Falsifiable predictions

- **HARD-PASS (compose now, no new mechanism):** Arm A or B >= 0.70 exact round-trip, matching Arm C within
  0.10 (reasoning doesn't add material degradation on top of the known decoder ceiling). Ship the pipeline.
- **HARD-FAIL (real bridge tax, build co-trained bridge first):** both Arm A and B < 0.40 while Arm C (no
  reasoning) is >= 0.70 -- proves the degradation is the HAND-OFF, not any single component, exactly
  matching the literature's naive-bridge-tax finding. Next step is a co-trained (not analytic) bridge, per
  Hersche et al.'s working fix.
- **MIDDLE-BAND:** Arm A/B in [0.40, 0.70) -- partial compose; quantify per-seed cv before deciding.

## Substrate-product implications

Not a stop-the-line finding: 2 of 3 tested joints (encoder->store, store->reasoning) are proven or
smoke-proven clean; only the reasoning->generation seam is unbuilt. The literature gives a concrete,
falsifiable next design (co-trained bridge beats analytic bridge) rather than an open-ended search. Product
framing: the substrate's glass-box property means every seam gets its own inspectable gate cell (per the
GPU K-hop cautionary case) -- integration testing is a per-seam discipline, not a one-time "it composes"
checkbox.

## Citations (verified count: 20 distinct sources across 2 independent Sonnet WebSearch lit-scans; not
independently cross-checked against primary text -- lit-scan tier, calibration penalty applied)

Neuro/bridge-transform scan: Semedo et al. *Neuron* 2019; Perich & Rajan *Curr. Opin. Neurobiol.* 2020;
Perich et al. *Nat. Commun.* 2020; Sherman *Compr. Physiol.* 2017; transthalamic-pathway reviews (*J.
Neurosci.* 2019/2024, *Nat. Commun.* 2024); Halassa & Kastner *Nat. Neurosci.* 2017; McClelland/McNaughton/
O'Reilly 1995; Kumaran/Hassabis/McClelland *TICS* 2016; Teyler & DiScenna 1986/2007; Degenhart et al. *Nat.
Biomed. Eng.* 2020; Farshchian et al. *eLife* 2023; RSA/CKA/Procrustes equivalence, bioRxiv 2024 (preprint).

VSA/HDC scan: Frady/Kleyko/Sommer *IEEE TNNLS* 2021 (arXiv:2009.06734); Frady/Kent/Olshausen/Sommer *Neural
Comp.* 2020 (arXiv:1906.11684, 2007.03748); Hersche et al. *Nat. Nanotech.* 2023 (arXiv:2211.05052); Hersche
et al. *NAI* 2025 (arXiv:2303.13957); Kymn/Kleyko/Frady/Sommer *Neural Comp.* 2024 (arXiv:2311.04872);
Schlegel/Neubert/Protzel 2022 (arXiv:2001.11797); Forney concatenated-coding theory (Scholarpedia).

## Prior integration cells flagged (substrate scour)

- `exp_cortex_integration_end_to_end_v1` (HARD_PASS, commit landed 2026-07-02): a DIFFERENT integration axis
  -- composes 4 M3 conversational-cortex primitives (refuse-gate, TwoTierContext, RoleSlotSummarizer,
  clarify-gate) all within ONE algebra via `Cortex.forward()`. Corroborates the pattern here: same-algebra
  composition is already proven clean; this note's gap is specifically the cross-algebra seam.
- `substrate_capability_map.md` PP-39 (neural-symbolic bridge, HARD_PASS N=8192): symbolic rule-fire +
  connectionist similarity + deletion-cert compose in ONE algebra -- again corroborates "within-algebra
  composes; cross-algebra is the open seam."
- `substrate_kg_khop_gpu_scale_v1` (HARD-FAIL, 0.000): cross-domain caution cited above.
