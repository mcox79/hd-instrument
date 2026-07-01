# Research: Axis H hierarchical_bank HF revival options (a/b/c ranked)

**Date:** 2026-07-01
**Topic:** Which of {(a) content-addressable hash router, (b) S independent router workspaces, (c) revisit PC regime where flat >= 0.80 first} has highest CG probability + payoff?
**Substrate context:** v1 HF at S=8. v2 S=32 revival FALSIFIED (routing_acc=0.055 vs SNR-predicted 2.024). Positive-control (flat @ M=4K) BROKEN at 0.0085 vs 0.80 required. partition_by_source @ M=4K achieves recall=0.9998, routing_acc=1.0 (oracle-partition workspace WORKS).

## HEADLINE
**Rank (c) > (b) > (a).** Path (c) is mandatory-precondition — the test rig has a broken positive-control that makes (a) and (b) untestable. Path (b) is the highest-payoff mechanism-class change once rig is fixed. Path (a) is highest-risk / lowest-payoff — content-addressable hash routing on bipolar codebooks reproduces the router-SNR bottleneck under a different name.

## Ranked options

### (c) Revisit PC regime — CG=0.75, payoff=CRITICAL (unblocks a/b)
- **Design one-liner:** `hierarchical_bank_v3_PC_calibration` — sweep CUE_COS in {0.70, 0.85, 0.95, 0.99} and M in {200, 1K, 4K, 16K, 64K} on flat-only structure; find (CUE_COS, M) regime where flat@M >= 0.80 recall; **only then** re-run hierarchical_2level in that regime.
- **Why highest CG:** substrate context PROVES the rig is broken (partition@M=4K=0.9998 shows the decoder itself works; flat@M=4K=0.0085 with SAME decoder means the flat readout has a threshold/cue-noise mismatch). Positive-control-first is META_RULE_S band-calibration; ~1hr CPU smoke.
- **Cross-domain support:** Willshaw (1969)/Palm — associative capacity gated by sparse-code density AND cue overlap; bipolar dense codes at CUE_COS=0.85 fall in a known dead-zone (below sparse-code threshold, above dense-code linearity).

### (b) S independent router workspaces — CG=0.55, payoff=HIGH (post-(c))
- **Design one-liner:** `hierarchical_bank_v3_S_indep_router` — replace the "single shared bundle-workspace routes into S super-banks" mechanism with **S independent router-vectors** (one per super-bank), each learned/binding-derived independent of the others; route by argmax_s cos(cue, router_s); no cross-workspace interference term.
- **Why HIGH payoff:** partition_by_source@M=4K achieves 1.0 recall with oracle routing — the payoff structure is CG-eligible IF routing_acc reaches even 0.90. The v2 falsification (SNR-predicted 2.02 → observed 0.055) shows the shared-bundle router has a hidden interference term the SNR analysis missed. Independent router-vectors eliminate that interference by construction.
- **Cross-domain support:** MoE literature (Shazeer 2017, Fedus 2022, Zoph 2022) — sparse routing works when experts are independent modules; Expert Choice Routing (Zhou 2022) shows load-balance/interference IS the routing failure mode. Hippocampal mossy-fiber sparse dilution (0.000046) = biology's answer to router interference (Rolls, Treves).

### (a) Content-addressable hash router — CG=0.30, payoff=MEDIUM
- **Design one-liner:** `hierarchical_bank_v3_CAM_hash_router` — LSH-style random hyperplane hash of the cue → super-bank index; no learned routing state; deterministic content→address.
- **Why LOWER CG:** LSH on bipolar codebooks reproduces the router-SNR bottleneck — hash collisions scale with M/2^b (b=log2(S) bits); at S=32 that's 5 hash bits, giving ~M/32 collisions per bucket regardless of cue quality. Same math as v2 shared-bundle SNR analysis — different name, same physics.
- **Cross-domain support:** Willshaw sparse-CAM CAN work (Knoblauch 2010 shows log(2) capacity) — BUT only at extreme sparsity (density <0.001), incompatible with dense bipolar codebooks. Would require substrate storage-primitive change to sparse-projected, not just router change.

## Cheap decisive test (path c first)
Fix positive-control: sweep CUE_COS on flat @ M=4K. HARD_PASS: exists CUE_COS such that flat recall >= 0.80 AND partition recall >= 0.80. HARD_FAIL: no CUE_COS in [0.5, 0.99] achieves flat >= 0.80 → substrate storage-primitive is the bottleneck, not routing (escalates entire Axis H to storage redesign).

## 5x-drill escalation eligibility
Path **(b) has 3 cross-domain support pillars**: (1) MoE sparse-routing independence principle, (2) hippocampal mossy-fiber sparse dilution, (3) partition_by_source@M=4K@1.0 direct substrate evidence. **Eligible for 5x-drill** if path (c) unblocks the rig.

Paths (a) and (c) each have 1-2 pillars — not eligible for 5x escalation.

## Substrate-product implications
If (b) succeeds: Axis H becomes CG-outer-axis, unblocking hierarchical planning for M3 cortex layer (per director_TRUE_PHASE_DIAGRAM_COVERAGE). If (c) shows the rig is fundamentally broken (no CUE_COS works), Axis H closes as substrate-storage-limited rather than routing-limited — pivots effort to storage primitive research.

## Calibration
Deflated P estimates (lit-scan penalty 0.15-0.25 applied): (c) P=0.75, (b) P=0.55, (a) P=0.30. Novel-synthesis capped at 0.50 for (b) since substrate context provides direct evidence (partition@M=4K=1.0) — but held at 0.55 given oracle-routing is not learned-routing.

## Citations (verified)
- Willshaw, Buneman & Longuet-Higgins 1969 — non-holographic associative memory
- Knoblauch, Palm, Sommer 2010 — Memory Capacities for Synaptic and Structural Plasticity
- Shazeer et al. 2017 — Outrageously Large Neural Networks (sparse MoE)
- Zhou et al. 2022 — Mixture-of-Experts with Expert Choice Routing (NeurIPS)
- Rolls 2013 — mechanisms for pattern completion and pattern separation in hippocampus
- Treves & Rolls — DG-CA3 sparse projection
- Substrate: `d:/AI/hd-instrument/data/exp_substrate_hierarchical_bank_v2_S32_seed_7_smoke/metrics.json` (verified 2026-07-01)

Verified count: 6 external + 1 substrate = 7.
