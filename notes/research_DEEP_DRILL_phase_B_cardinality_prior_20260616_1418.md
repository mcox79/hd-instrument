# Research DEEP DRILL — Phase B cardinality C2 prior (literature-grounded)

Date: 2026-06-16 14:18 local
Owner: research (Opus synthesis over 3 parallel Sonnet lit-scans)
Routing trigger: Strategy / Exp-Dev pre-build deep-drill request — Phase B BUILD firing imminent.
Companion deliverables this drill:
- `notes/research_cardinality_fpe_rns_counting_accuracy_2026-06-16.md` (sub-agent 1)
- `notes/research_bundle_norm_null_hypothesis_2026-06-16.md` (sub-agent 3)
- `notes/exp_dev_handoff_research_cardinality_fpe_rns_2026-06-16.md` (sub-agent 1 companion)

## (a) HEADLINE

The literature does NOT have a published direct precedent for "added cardinality primitive HARD-PASSes vs binder-only basis at N=4096 multi-seed." Three convergent findings from the parallel lit-scans:

1. **No paper reports exact-count RMSE or quantifier accuracy at N=4096 for FPE / RNS-HDC / NEF-integrator / SSP cardinality.** Kymn et al. 2024 (RNS-HDC, arXiv:2311.04872) reports factorization-capacity scaling only, not numerosity readout. Frady-Sommer FPE lineage reports continuous-magnitude / sequence-index decoding, not exact-count or quantifier accuracy. The only direct VSA-cardinality precedent surfaced is Alam 2023 (subitizing-with-HRR, arXiv:2312.15310), which lives at small K and small N.
2. **The bundle-norm-only null hypothesis is ANALYTICALLY strong** (Frady-Sommer bundle SNR ~ sqrt(N/M); Clarkson et al. 2023 arXiv:2301.10352 give formal bundle-capacity bounds for set cardinality). The norm-as-cardinality-readout is unposed in canonical VSA but NOT excluded — and at N=4096 the basis null has room to perform.
3. **NEF / SSP literature documents drift-to-attractor + synapse-order error as canonical failure modes** (Singh-Eliasmith 2006; Voelker-Eliasmith 2018). These are NOT cured by raising N alone — they cap multi-seed reliability of the added primitive at high counts.

Net: the prior for "C2 HARD-PASS at full N=4096 n>=3 seeds" is LOWER than the 0.45 baseline. The most-likely outcome is **MIDDLE_BAND** — C2 beats C1 on a strict subset of count regimes, but does not cleanly close cardinality at quantifier-level accuracy across all configurations and seeds. Sub-agent 3 named MIDDLE_BAND explicitly as the most-likely Phase-B outcome.

## (b) Cheap decisive test

Pre-registered for Phase B build (run BEFORE the full 4-config × n>=3-seed sweep):

**Smoke gate (under 30 min CPU at N=4096, n=2 seeds):**
- C1 (basis-only) bundle-norm exact-count RMSE on small K (K=1..16) across vocab M=200.
- C2 (added cardinality primitive) exact-count RMSE on same K-range.
- If C2 RMSE / C1 RMSE > 0.85 at K=8: ABORT full sweep, dispatch a primitive-design rescue drill before committing GPU cycles. Lit prior says basis null is likely close-to-strong; if the primitive cannot beat it on the cheap range, the full sweep at large K is wasted spend.

**Decisive test (full sweep, n>=3 seeds):**
- 4 configurations (C0 graph-walk-trace, C1 basis-only, C2 +cardinality-primitive, C3 +internal-abstraction-discovery).
- Three task families: EXACT-COUNT (RMSE), AT-LEAST-K quantifier (accuracy), MAJORITY / MOST (accuracy).
- K-range: 1..1024 sampled log-spaced; expect basis-null collapse past K~N/4=1024 per Kleyko 2020 / Clarkson 2023.
- Cleanup vocab M in {200, 2000} (probe cleanup-noise interaction flagged by sub-agent 1).

## (c) Falsifiable predictions

### HARD-PASS bands (C2 vs C1 must clear ALL THREE)

1. **EXACT-COUNT RMSE:** C2 RMSE <= 0.5 counts at K in {4, 16, 64} (mid-range); C1 RMSE > 1.5 counts at the same K. Ratio C2/C1 <= 0.33.
2. **AT-LEAST-K quantifier accuracy:** C2 >= 0.90 across K in {4, 16, 64}; C1 < 0.70 at K=16. Gap >= 0.20.
3. **MAJORITY / MOST accuracy:** C2 >= 0.85 on majority-of-two task; C1 < 0.65. Gap >= 0.20.
4. **Multi-seed std:** C2 std across n>=3 seeds <= 0.40 standard-deviations of the mean accuracy (or RMSE std <= 0.5 counts).

### HARD-FAIL bands (any ONE triggers structural-closure of C2)

1. **EXACT-COUNT:** C2 RMSE > 1.0 at K=16 OR C2 RMSE / C1 RMSE > 0.85.
2. **Quantifier:** C2 at-least-K accuracy < 0.75 at K=16 OR no gap > 0.10 vs C1.
3. **Multi-seed instability:** C2 std > 0.40 (acc) OR > 0.8 counts (RMSE) across n>=3 seeds — drift-to-attractor signature.
4. **Cleanup-noise breakdown:** C2 at M=2000 degrades > 20% absolute relative to M=200 — flagged in sub-agent 1 as the binding-constraint adjacent risk.

### MIDDLE_BAND (most-likely outcome per lit prior)

- C2 beats C1 on EXACT-COUNT at small K (K<=8) but fails AT-LEAST-K quantifier OR fails multi-seed std band.
- Or C2 wins on synthetic but fails the cleanup-noise robustness gate at M=2000.
- Treat MIDDLE_BAND as a PARTIAL — do NOT auto-promote C2 to "cardinality primitive integrated" without explicit Strategy review of which sub-task families it actually closes.

## (d) Cross-thread synthesis (with prior drill #1 — binding-orthogonality)

Drill #1 (this session, earlier) found:
- Cardinality is BINDING-ORTHOGONAL across 4 VSA author clusters (Plate / Kanerva-Kleyko / Eliasmith-Komer / Frady-Sommer-Kymn) — the binders do not encode set size; a separate mechanism must.
- P_deflated for "added primitive HELPS" = 0.45 (cap_map row prior).

This drill (#2, deeper):
- The added primitive is **architecturally licensed** (binding-orthogonal -> separate mechanism is the right shape) BUT empirically **un-precedented at N=4096 multi-seed** (no published HARD-PASS analog).
- The bundle-norm null is **stronger than drill #1 suggested** — Clarkson 2023 gives bundle-only cardinality capacity bounds that are non-trivial. The null hypothesis is not vacuous.
- Failure modes (drift-to-attractor, synapse-order error, bundle capacity collapse past K~N/4) are well-documented in adjacent NEF/SSP literature and do NOT vanish at N=4096.

Synthesis: drill #1 said "it's the right SHAPE of fix." Drill #2 says "the right shape is necessary but does not entail HARD-PASS-level magnitude at N=4096 multi-seed." Magnitude must be earned empirically.

## (e) Substrate-product implications

For Phase B build:
1. **Run the smoke gate before the full sweep.** Sub-30min decision-cheap check. If basis-null is close, save the GPU sweep and dispatch primitive-redesign first.
2. **Pre-register HARD-PASS / HARD-FAIL / MIDDLE_BAND bands in the experiment cell** so the verdict_handler doesn't get to back-fit a winning narrative. Bands above.
3. **Always probe at M=200 AND M=2000** (cleanup vocab) — sub-agent 1 flagged this twice as the binding-constraint adjacency that is most likely to surprise.
4. **For substrate-product positioning:** even a MIDDLE_BAND C2 is product-meaningful — it shows the substrate refuses to over-claim quantifier-level mastery without empirical evidence (composes with [[feedback-substrate-standalone-capability-first-before-LLM-positioning]] 11th USER-LOCKED rule and 18th methodology rule refuses-what-cannot-prove). The honest middle is a credibility asset, not a failure.
5. **C3 internal-abstraction-discovery prior:** lit gives ZERO precedent for "100-step unsupervised discovery of cardinality abstraction from binder-only basis." This is novel-synthesis at the cap_map level — P capped at 0.50 per [[feedback-lit-scan-calibration-penalty]], deflated to 0.25-0.30.

## Updated P_deflated estimates

| Claim | Prior baseline | Updated P_deflated | Reasoning |
|---|---|---|---|
| Phase B cardinality C2 HARD-PASSes at full N=4096 n>=3 (all 3 bands) | 0.45 | **0.22** | No published precedent at N=4096 multi-seed; basis null analytically strong; drift-to-attractor + cleanup-noise risks; MIDDLE_BAND most-likely. Sub-agent 1 said 0.18; sub-agent 3 said 0.40 (bundle-null analysis); midpoint 0.22 honoring the calibration penalty. |
| C2 EXACT-COUNT band passes (only) | n/a | 0.50 | Easiest sub-band; lit prior says added primitive likely beats basis on exact count at small K. |
| C2 AT-LEAST-K quantifier band passes (only) | n/a | 0.30 | Quantifier accuracy is the gap in the literature; no precedent guarantees >=0.90. |
| C2 MAJORITY band passes (only) | n/a | 0.28 | Same gap; majority is structurally harder than at-least-K because it requires relative comparison, not absolute readout. |
| C2 multi-seed std band passes (only) | n/a | 0.55 | Furlong 2024 + Kleyko 2020 multi-seed precedents show tight std at N>=1024; std band is the most achievable. |
| C3 internal-abstraction HARD-PASSes within 100-step budget | 0.40 | **0.18** | Zero literature precedent; novel-synthesis; 100-step budget is tight for unsupervised discovery; deflate hard. |

## TOP 3 RISKS that could cause C2 HARD-FAIL despite literature support

1. **Bundle-norm null is closer to C2 than expected at N=4096.** Clarkson 2023 capacity bound says basis-only is non-trivially strong; at N=4096 the basis null has 4x more headroom than the N=1024 lit baseline. If C2's primitive is itself bundle-flavored (not orthogonal carrier), the null may capture most of the count signal and C2's marginal gain falls under the ratio gate. **Mitigation:** ensure the primitive uses an orthogonal carrier (FPE phase / RNS modulus / NEF integrator state) NOT a bundle-mode addition.
2. **Cleanup-noise breakdown at M=2000.** Sub-agent 1 flagged this twice; FPE/RNS readout is known to degrade with codebook size. If C2 works at M=200 but breaks at M=2000, that's a structural-closure signal for "primitive is fragile to vocab scale" — the substrate's vocab is going to grow, so this gate is product-load-bearing. **Mitigation:** test M=2000 in the smoke gate, not the full sweep — failing late is more expensive.
3. **Multi-seed drift-to-attractor (Singh-Eliasmith 2006).** If the cardinality primitive has any integrator-flavored dynamic (accumulator state, recurrent loop, fixed-point cleanup), n>=3 seeds may bifurcate to spurious attractors at high K, blowing the std band. Lit says raising N does NOT cure this. **Mitigation:** seed-stability pre-screen — run n=5 seeds on K=64 only as a 5-min sanity check before committing the full sweep.

## RECOMMENDED specific benchmarks (real-corpus options vs synthetic)

Per sub-agent 1, the only canonical external benchmark is bAbI Task 7 (counting) / Task 8 (lists). All other candidates require synthesis-glue:

- **bAbI Task 7 (counting)** — Facebook 2015, 1K-version: direct numerosity benchmark, well-studied, gives a published comparator floor.
- **bAbI Task 8 (lists / sets)** — adjacent to cardinality, tests set-membership which is the dual.
- **Steinert-Threlkeld 2019 quantifier-RNN suite** (arXiv:1809.05733) — quantifier conservativity / monotonicity benchmark. Sub-agent 1 named this as the cheap decisive test.
- **dSprites count-of-shape** — synthetic but standardized, used in disentanglement lit; lets the substrate report against a non-VSA baseline.
- **give-N task** — cog-psych standard for numerosity (Halberda, Piazza); useful external comparator for Weber-fraction degradation curves.

**Recommendation:** synthetic constructions are FINE for the smoke gate + the full sweep's main sub-task families (the substrate is calibrated to its own basis). Layer bAbI-7 + Steinert-Threlkeld as a SINGLE supplementary cell AFTER the main sweep completes — DO NOT block the main sweep on real-corpus port (sub-agent 2 explicitly named "no standard cardinality benchmark exists in NEF/SSP — adoption is novel-synthesis"; force-fitting can introduce confounds that obscure the C0/C1/C2/C3 contrast).

## (f) Citations (verified count: 16 distinct sources across the 3 sub-scans)

From sub-agent 1 (FPE / RNS-HDC):
- Kymn et al. 2024 RNS-HDC (arXiv:2311.04872) — factorization capacity, not numerosity at N=4096.
- Frady-Kanerva-Sommer-Olshausen 2021/2022 "Computing on Functions Using Randomized Vector Representations" — FPE foundations.
- Alam et al. 2023 (arXiv:2312.15310) — only direct VSA-cardinality precedent (subitizing, small K).
- Frady-Kent-Olshausen-Sommer 2020 resonator networks — factorization bounds vs N.
- Steinert-Threlkeld 2019 (arXiv:1809.05733) — quantifier-RNN suite for cheap decisive test.

From sub-agent 2 (NEF / SSP):
- Singh & Eliasmith 2006 J. Neurosci. — drift-to-attractor failure mode.
- Voelker & Eliasmith 2018 Neural Computation (DOI:10.1162/neco_a_01046) — synapse-order error framing.
- Eliasmith et al. 2012 Science 338:1202 — Spaun list-recall + RPM (qualitative).
- Rasmussen & Eliasmith 2014 Intelligence — spiking RPM, single-seed.
- Komer, Stewart, Voelker, Eliasmith 2019 CogSci — SSPs N=512.
- Dumont & Eliasmith 2020 (arXiv:2007.13462) — SSP grid-cell, N<=1024.
- Furlong et al. 2024 (arXiv:2412.00488) — CLE+MLE FPE cleanup, multi-seed at N up to 2048.
- Stoianov & Zorzi 2012 (DOI:10.1038/nn.2996) — Weber-law numerosity from generative models.

From sub-agent 3 (bundle-norm null):
- Plate 1995 IEEE TNN + Plate 2003 book — bundle capacity / superposition norm.
- Kanerva 2009 — HDC capacity Cap ~ N/log.
- Kleyko et al. 2020 (arXiv:2001.11797) — bundle accuracy collapse past D/4 items.
- Clarkson et al. 2023 (arXiv:2301.10352) — formal bundle-only cardinality capacity bound (strongest null evidence).

Total: 16 verified citations; 5 are directly load-bearing (Kymn 2024, Alam 2023, Steinert-Threlkeld 2019, Singh-Eliasmith 2006, Clarkson 2023). Lit-scan calibration penalty applied (deflated each cluster P by 0.15-0.25; novel-synthesis P capped at 0.50).
