# ROUTING -- Polynomial-p=4 modern Hopfield upgrade engineering

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Type:** Substrate primitive upgrade + empirical validation test
**Status:** USER AUTHORIZED 2026-06-04 (engineering ~10-20h; experiment ~1-2h CPU; $0).

---

## Capability question

Does upgrading the substrate's retrieval primitive from classical outer-product (energy E ~ -x^T W x) to polynomial-p=4 modern Hopfield (energy E ~ -sum (xi . sigma)^4 / N^3) reduce the substrate-as-training-mechanism N_threshold from ~3000 to <1000, while preserving bipolar {+1,-1}^N native compatibility, O(N*M) compute cost, and all existing observability/composition primitives?

## Pre-reg HP/MID/HF bands

**HARD-PASS:**
- At N=500 with polynomial-p=4 modern Hopfield: char-LM training BPC < uniform - 1.0 nat (substrate-as-training works at much smaller N than classical regime)
- At N=200 with polynomial-p=4: char-LM training BPC < uniform - 0.5 nat (partial learning at even smaller N; confirms super-linear scaling)
- Compute walls at p=4 within 2x of p=2 at matched N (O(N*M) preserved per Demircigil 2017)
- All observability primitives unchanged (cross-layer composition L>=200 still EXACT-1.0000; deletion certificate still works; drift detection still works)
- 3/3 seeds consistent at HP cells

**MIDDLE:**
- HP achieved at N=500 but NOT at N=200
- OR partial learning (BPC < uniform - 0.5 nat) at N=500 only
- OR some observability primitives degrade but not all
- 2/3 seeds consistent

**HARD-FAIL:**
- No learning at N=500 with polynomial-p=4 (refutes the upgrade-path hypothesis)
- OR compute walls > 4x of p=2 baseline (algebraic prediction violated)
- OR observability primitives break (substrate's modern Hopfield class isn't a clean swap)
- OR bipolar quantization fundamentally incompatible despite Demircigil 2017 theorem

## Resource

Local CPU runner (substrate operations; existing infrastructure with single-primitive replacement).

## Cost ceiling

- Engineering: ~10-20h (single-primitive swap + tests + integration validation)
- Experiment: $0 CPU; per-cell wall scales with N (15-60 min)
- Total experiment wall ~2-4h sequential across 3 cells

## P_deflated

- Polynomial-p=4 upgrade lowers N_threshold to <1000 in empirical test: **0.32** (per Modern Hopfield 3x drill; BCM-SNR floor independence is the conditional)
- Engineering succeeds (single-primitive swap as predicted): **0.55** (Demircigil 2017 + BinaryAttention + Hamming Attention precedents are strong)
- Compute cost stays O(N*M) at p=4: **0.65** (algebraically predicted; well-documented in lit)
- Observability primitives unchanged: **0.55** (the substrate's composition + audit primitives are independent of the retrieval energy; should preserve)

Net joint P (substrate-as-training works at N<1000): 0.30-0.35 (conditional on BCM-SNR drill outcome; lower bound).

---

## What this is (plain language)

Modern Hopfield drill identified the polynomial-p=4 upgrade path: replace `sign(W @ sigma)` with `sign(Xi.T @ (Xi @ sigma) ** (p-1))` (normalized by 1/N^(p-1)). Algebraic predictions:

- Hopfield capacity floor: drops from N ~ 3000 to N ~ 100-200 at p=4
- Compute cost: UNCHANGED at O(N*M) for ALL polynomial degrees (polynomial applied to overlap vector, not to pattern matrix)
- Bipolar {+1,-1} compatibility: native (Demircigil 2017 exact theorem proves exponential capacity in pure bipolar setting)
- Observability primitives: should be unchanged (composition + audit + drift detection are all retrieval-independent)
- Engineering: single primitive swap; ~10-20h

**The asterisk:** the BCM-SNR learning-rule floor is an INDEPENDENT constraint, also at N ~ 2000-4000 classical. Whether the polynomial-p upgrade reduces this floor too is the prerequisite question being drilled in parallel (`research_drill_bcm_snr_vs_polynomial_p_2x_2026-06-04.md`, in-flight). If BCM-SNR is p-independent, the upgrade frees capacity but doesn't fully rescue substrate-as-training at small N. If p-dependent, both floors fall together and substrate becomes viable at N ~ 100-500.

## Sequencing recommendation

**Engineering can START NOW** (in parallel with BCM-SNR drill landing). Even if BCM-SNR drill shows the learning-rule floor is p-independent:

1. The polynomial-p=4 upgrade STILL reduces the Hopfield capacity floor (useful for substrate-physics composition + audit moats)
2. The upgrade STILL achieves bipolar attention equivalence (Ramsauer 2020) — useful regardless of BCM outcome
3. The capacity headroom enables larger M storage at same N for the composition + drift-detection killer features

So engineering is low-risk regardless of BCM drill outcome. Recommend dispatch in parallel.

**Experiment dispatch waits for BCM drill landing.** If BCM-SNR is p-independent, the empirical test design should include comparison cells at p=2 N=3000 (the BCM-SNR floor; substrate-as-training works there empirically per Exp-Dev preview) AND p=4 N=500 (capacity floor freed; tests whether BCM-SNR alone is binding).

---

## Cell list for empirical validation (after engineering complete)

Anchor name template: `substrate_polynomial_p4_modern_hopfield_v1_N{N}`

Cells:
- N=200, p=4: most aggressive scale reduction; tests super-linear N_threshold reduction
- N=500, p=4: mid-range scale reduction; matches Demircigil predicted floor
- N=3000, p=2: classical-regime baseline (matches Exp-Dev preview HP at higher N)
- Optional: N=500, p=2 (classical at small N; should FAIL per existing N=512 HF; confirms baseline)

3 seeds per cell. Same LM scaffold (~10k char-LM params), same corpus, calibrated readout temp=0.2, fixed cf-RPE no-cache discipline.

Substrate primitive: polynomial-p modern Hopfield retrieval with even p; normalization 1/N^(p-1); all other substrate primitives unchanged.

---

## Engineering checklist (~10-20h)

- [ ] Replace retrieval primitive: `sign(W @ sigma)` -> `sign(Xi.T @ (Xi @ sigma) ** (p-1))`
- [ ] Add normalization factor 1/N^(p-1) (numerical stability)
- [ ] Even-p restriction (p=4 default; expose p as config parameter)
- [ ] PROT-022 self-tests at new energy class: verify Lyapunov-decreasing update at p=4
- [ ] Capacity-tracking instrumentation: report effective M_eff vs alpha_p * N^(p-1) / log(N)
- [ ] Compatibility tests: run existing PP-12/Q-A3 composition at p=4 to verify L>=50 EXACT fidelity preserved
- [ ] Compatibility tests: run existing deletion-cert experiment at p=4 to verify cos=1 for non-target queries
- [ ] Compatibility tests: run existing PP-50 drift detection at p=4 to verify kappa_3 ratio behavior

If observability primitives break at p=4, this is itself an important finding (substrate's modern Hopfield class has different observability properties than classical; informs capability claims).

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-small-scale-first-methodology]]: rung-1 LM scaffold; tests substrate primitive upgrade at smallest viable LM
- Per [[feedback-no-padding-experiments]]: 3 cells discriminate (a) polynomial-p reduces N_threshold (b) classical baseline (c) bipolar quantization at small N still fails at classical p
- Per [[feedback-no-smoke-preframing-in-task-prompts]]: HP/MID/HF bands tied to drill predictions
- Per [[feedback-keep-research-exploratory-not-narrowing]]: opens substrate's modern-Hopfield-class as a new design dimension
- Per [[feedback-verify-implementations]]: verify Demircigil 2017 exact-bound mechanism matches the implementation
- ASCII-only output enforced

PROT-018: anchor names use _N{N} suffix
PROT-021: source=local CPU, run_mode=full, n_seeds=3

---

**END.**

**Exp-Dev:** start engineering polynomial-p=4 retrieval primitive in parallel with BCM-SNR drill landing. Engineering scope: ~10-20h single-primitive swap + integration tests on existing observability primitives. Experiment dispatch waits for BCM drill output to refine cell list.

**Orchestrator:** informed. If experiment HP: substrate modern-Hopfield-class identified empirically; cap_map sub-property founding under substrate's algebraic regime classification. If HF: substrate is classical-Hopfield-bound; engineering effort still useful for cap_map characterization.

**Research session:** holds for BCM-SNR drill landing (parallel; ~30-45 min) + N-sweep verdict (parallel; 3-5h) + this empirical test verdict (after engineering ~10-20h + experiment ~2-4h).
