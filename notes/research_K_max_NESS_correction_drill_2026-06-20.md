# Research drill: K_max NESS correction (closed-form vs partial vs gap)

**Topic:** Non-equilibrium steady-state (NESS) correction to the equilibrium Hopfield retrieval-depth formula `K_max ≈ 3.3 × (1 − α/α_c)² / α`, with focus on whether the literature publishes a closed-form K_max(α, write_rate, decay_rate) for write × decay NESS Hopfield-class associative memory.

**Filed:** 2026-06-20  (USER directive 2026-06-20: recommendation B from negatives discussion; drill-until-solutions on K_max-pessimistic open negative).

**Method:** 3 parallel Sonnet lit-scan sub-agents (non-eq Hopfield depth bounds / iterated-cleanup VSA depth theory / DMFT-NESS framework). Generic math terms only off-platform per [[feedback-query-privacy-decomposition]]. 0.15-0.25 calibration deflation per [[feedback-lit-scan-calibration-penalty]]; novel-synthesis cap 0.50.

---

## (a) HEADLINE

**No published closed-form K_max(α, write_rate, decay_rate) for write × decay NESS Hopfield-class memory exists.** All three sub-agents independently converged on P_deflated ≈ 0.10–0.15 that such a closed-form lives in the literature undiscovered. The substrate's empirical 2-6× depth extension over the equilibrium prediction sits in a genuine literature gap. The DMFT building blocks (Crisanti-Sompolinsky 1988 + Cugliandolo-Kurchan 1993 + Helias-Dahmen MSRDJ + Kalaj 2026 + Betteti 2026 input-driven) are SUFFICIENT to derive one in-house (P ≈ 0.40–0.50 the synthesis is tractable in ~weeks-of-theory); the substrate's K=12 / K=24 / 6× empirical anchors are CONSISTENT with the qualitatively-known transient-basin-remnant boost (arXiv:2506.05303, Science Adv. 2024 adu6991), which has not been closed analytically.

**Productization implication:** depth-bound K is a substrate-product capability that has **empirical envelope + qualitative-mechanism backing** but NOT a closed-form theoretical proof. We can promise "substrate operates above the equilibrium K_max bound by 2-6× via NESS-and-cleanup mechanisms validated empirically across multiple anchors (single-substrate K=12, hierarchical 24-hop, cleanup-augmented 6×)" but we cannot promise "K_max formula tells you exactly how deep before deploying." This is honest scorecard framing per [[feedback-measured-bounds-are-method-config-contingent]].

---

## (b) Cheap decisive test

Three tiers, ordered by cost (cheapest first):

**Tier 1 — Empirical envelope sweep (CPU, ~2 hr).** Vary write_rate and decay_rate at fixed α across [10⁻⁴, 10⁻¹], measure K_max empirically. Fit K_max_observed / K_max_equilibrium as a function of (write_rate / decay_rate) ratio. **Decisive output:** is there a power-law / log relationship that the equilibrium formula misses? If yes, that's the substrate-product depth-bound envelope (parametric, not formula).

**Tier 2 — Algebraic re-derivation (theory + smoke, ~1 week).** Couple Kalaj's Λ-feedback recursion (arXiv:2510.19146 Eqs. 33-37) with Betteti's escape-time integral (arXiv:2603.03201) to write a SUBSTRATE-SPECIFIC K_max(α, write, decay) closed-form. Validate against the empirical envelope from Tier 1. **Decisive output:** does the synthesized formula match Tier 1 within ±30% across 5 (write, decay) operating points? If yes, that's a substrate-novel theoretical contribution + a closed-form depth-bound for productization.

**Tier 3 — Cell-build: NESS-Hopfield K_max validation cell (GPU, ~4 hr).** A single dispatched cell at substrate's actual operating point (α ≈ 0.03, the empirical K=12 anchor), sweep N ∈ [256, 1024, 4096], measure depth-at-failure across 10 seeds × 3 noise levels. **Decisive output:** confirms the empirical envelope from Tier 1 holds at production scale; gives the substrate-product depth-bound a 30-data-point statistical backing.

**Recommended:** **Tier 1 first**, then Tier 2 (theory) and Tier 3 (cell) in parallel after Tier 1 establishes the envelope shape.

---

## (c) Falsifiable predictions

**HARD-PASS thresholds (substrate-product depth-bound is real and parametric):**

| Prediction | HARD-PASS | Mechanism |
|---|---|---|
| P1: K_max_observed > equilibrium K_max formula by ≥2× at substrate operating point | observed / formula ≥ 2.0 across 4+ of 5 swept (write, decay) points | NESS basin-remnant transient retrieval (arXiv:2506.05303, 2024) |
| P2: K_max grows with cleanup re-sharpening events | cleanup-on K_max / cleanup-off K_max ≥ 5.0 (current empirical 6×) | per-hop SNR resharpening; Plate-Frady-Sommer single-step bound iterated |
| P3: K_max depends on (write_rate / decay_rate) ratio, NOT on either separately | partial-correlation slope of K_max vs log(write/decay) > 0.5 across 5 points | NESS dimensional analysis: only the ratio survives in stationary correlator |

**HARD-FAIL thresholds (depth-bound is NOT robust; equilibrium formula is correct after all):**

| Prediction | HARD-FAIL | Implication |
|---|---|---|
| F1: K_max_observed ≤ 1.3× equilibrium formula at substrate operating point | observed / formula < 1.3 across ≥3 of 5 points | Prior 6× empirical was a config-luck artifact; revise scorecard |
| F2: cleanup-on / cleanup-off ratio drops below 2× at the sweep operating point | ratio < 2.0 across ≥3 points | The 6× was a single-operating-point fluke; cleanup-boost is regime-narrow |
| F3: K_max varies independently with write_rate AND decay_rate (not just ratio) | partial-correlations of K_max vs log(write) and vs log(decay) are statistically independent (|R| > 0.5 both, opposite signs) | NESS dimensional analysis is wrong; substrate's depth-bound has 2 independent knobs not 1 |

**MIDDLE-BAND (between HP and HF):** the empirical envelope is real but narrower than 2-6× (e.g., 1.5× boost across a moderate write/decay range). Productization: "substrate operates 1.5× above equilibrium prediction; precise depth-bound is workload-dependent."

P_deflated of full HARD-PASS triad (P1 ∧ P2 ∧ P3): **0.30** (each individually ~0.50; conjunctive). Lit-scan calibration cap 0.50 satisfied.

---

## (d) Cross-thread synthesis

**With prior internal findings:**

1. **2026-06-05 SQ2 K=12 single-substrate HP + 24-hop hierarchical HP:** these are the load-bearing empirical anchors this drill is trying to predict. Equilibrium formula at substrate operating point predicts K ≈ 3-5; observed K = 12 (single) and 24 (hierarchical) is 2.5-5× above equilibrium. **Consistent with this drill's finding:** the gap is a real NESS effect, mechanism qualitatively known (transient-basin-remnant + cleanup-resharpen) but not analytically closed.

2. **2026-06-05 cleanup-augmented 6× depth boost (drill predicted 2.7×):** the 2.2× prediction-vs-empirical gap is itself NESS-related. The 2.7× prediction came from a worst-case Plate-style single-step SNR argument; the 6× empirical sits in a regime where cleanup residual collapses once SNR clears the codebook-separation margin. **This drill explains the gap:** there is no closed-form for the cleanup-augmented depth multiplier; the worst-case bound is what we predicted; the empirical is the actual regime-dependent value.

3. **2026-06-19 N6 Resonator dense V=100 HF 2x:** the resonator family is a factorization mechanism, NOT a depth-extension mechanism (Frady-Sommer-Kent-Olshausen 2020). It does NOT predict our 6× depth boost. This drill closes the question of whether resonator capacity bounds inform the K_max formula — they don't.

4. **2026-06-17 Modern Hopfield variants + PCN-AM 2x:** Modern Hopfield (Ramsauer 2020) is ONE-SHOT by design — K=1 attractor convergence. The depth-bound question is moot in that framework. PCN-AM is iterative-relaxation but on a single composite (factorization), not K-hop sequential. **Neither family informs the substrate's NESS K_max question.**

5. **Pattern from this drill:** the substrate's "operates above the equilibrium bound by NESS dynamics + cleanup" is exactly the kind of substrate-novel mechanism flagged by [[feedback-substrate-standalone-capability-first]] — a capability where the lit has the building blocks but nobody has assembled them. Substrate's empirical envelope is the substrate-product story; a closed-form theoretical backing is a future-research artifact, not a productization requirement.

**Field-coverage updates (for next research_meta_map):**
- `nonequilibrium-stat-mech` field: drill-1 in this scope expansion. Yield: PARTIAL (no closed-form found; partial frameworks identified; productization path opened). Anchors: Crisanti-Sompolinsky 1988, Cugliandolo-Kurchan 1993, Helias-Dahmen 2020, Kalaj 2026, Betteti 2026.
- `modern-hopfield` adjacency: ratified that one-shot framing does not address depth-extension question; this is a closure on a previously-open ambiguity.
- New adjacency surfaced: **input-driven-Hopfield** (Betteti-Baggio-Zampieri 2026) — closest live work to substrate's write × decay regime; not previously in adjacency map.

---

## (e) Substrate-product implications

**Productization framing (recommended for scorecard / external):**

> "Substrate depth-bound K is validated empirically at K=12 (single substrate), K=24 (hierarchical), and 6× extension under iterated cleanup. These observations exceed the equilibrium K_max formula by 2-6×, consistent with NESS-corrected dynamics and basin-remnant transient retrieval (qualitatively published; closed-form derivation an open theoretical question). Productization commits to the empirical envelope, not a closed-form K predictor."

**What can be promised:**
- K=12 single-substrate at α≈0.03 (load-bearing, HARD-PASS anchor)
- K=24 hierarchical (HARD-PASS anchor, mechanism: stacked NESS layers)
- 6× depth boost with cleanup-augmentation (HARD-PASS anchor, mechanism: per-hop SNR resharpening)
- Operating regime where the envelope holds: α ∈ [0.01, 0.05]; write_rate < decay_rate × 10 (untested at higher ratios)

**What CANNOT be promised (yet):**
- A closed-form K_max formula valid across (α, write_rate, decay_rate)
- Depth-bound prediction in untested regimes (α > 0.05; write > decay)
- Worst-case adversarial depth bound (lit has no NESS PAC-Bayes analog)

**Scorecard recommendation:** flip the 2026-06-05 01:20 note from "future-drill candidate" to "drilled 2026-06-20: lit-gap confirmed; productization on empirical envelope; closed-form derivation OPEN as substrate-novel theory work (Tier 2 in this note)."

**Audit-discipline candidate:** **EMPIRICAL-ENVELOPE-NOT-FORMULA** — when a substrate capability operates above a published equilibrium bound, the productization story is the validated empirical envelope, not a closed-form derivation we don't have. The closed-form is a future-theory artifact; the envelope is what ships. This is the K_max-class-specific instance of [[feedback-measured-bounds-are-method-config-contingent]].

---

## (f) Citations (verified count: 22 across 3 angles)

**Equilibrium baselines:**
1. Amit, Gutfreund, Sompolinsky 1985 — equilibrium α_c=0.138 (the formula being corrected).
2. Hertz, Krogh, Palmer 1991 — Intro to Theory of Neural Computation Ch. 7 (α_c tables).

**Asymmetric / NESS Hopfield closed-forms (partial):**
3. Crisanti & Sompolinsky 1988, PRA 37, 4865 — DMFT for asymmetric Hopfield; paramagnetic at all T in fully-asymmetric limit.
4. Derrida, Gardner & Zippelius 1987, EPL 4, 167 — extremely-dilute asymmetric: α_c=2/π (closed-form CAPACITY, not depth).
5. Sompolinsky & Kanter 1986, PRL 57, 2861 — temporal-association, capacity ~0.1N (numerics, no closed-form).
6. Sommers, Crisanti, Sompolinsky, Stein 1988, PRL 60, 1895 — elliptic spectrum of asymmetric matrices.
7. Sompolinsky, Crisanti, Sommers 1988, PRL 61, 259 — "Chaos in random neural networks"; DMFT closure.

**DMFT / NESS frameworks (machinery, no K_max):**
8. Cugliandolo & Kurchan 1993, PRL 71, 173 — weak-ergodicity-breaking aging dynamics; principled NESS extension.
9. Crisanti, Horner, Sommers 1993, Z. Phys. B 92, 257 — spherical p-spin dynamics; integrodifferential closure.
10. Roudi & Hertz 2011, PRL 106, 048702 — dynamical TAP for asymmetric kinetic-Ising NESS.
11. Helias & Dahmen 2020, Springer LNP 970 — *Statistical Field Theory for Neural Networks*; MSRDJ machinery.
12. Aguilera et al. 2021, Nat. Commun. — unifying mean-field for asymmetric kinetic Ising NESS.

**Forgetful / palimpsest (decay enters as load-shift, not depth-multiplier):**
13. Parisi 1986, J. Phys. A 19, L617 — "A memory which forgets"; α_palimpsest ≈ 0.05.
14. Mézard, Nadal, Toulouse 1986, J. Physique 47 — solvable working memory models; bounded-synapse capacity α_c(ε).

**Recent (2024-2026) — closest live work:**
15. Betteti, Baggio, Zampieri 2026, arXiv:2603.03201 — input-driven Hopfield: explicit gain thresholds + escape times + collapse regimes for sequential retrieval (CLOSEST LIVE WORK TO WRITE × DECAY NESS).
16. Kalaj / Agliari et al. 2026, arXiv:2510.19146 — DMFT with non-monotonic transfer; α_c ≈ 0.36 (2.6× boost over symmetric equilibrium).
17. "Transient dynamics of associative memory models" 2026, arXiv:2506.05303 — DMFT for transient (pre-equilibrium) retrieval; above-capacity transient.
18. "Input-Driven Dynamics for Robust Memory Retrieval in Hopfield Networks" 2024, Science Adv. adu6991 / arXiv:2411.05849 — continuous-drive retrieval boost (numerical).

**Modern Hopfield (one-shot; not depth-extension):**
19. Ramsauer et al. 2020, arXiv:2008.02217 — Hopfield Networks is All You Need; one-shot retrieval.

**VSA / cleanup (no closed-form depth-multiplier):**
20. Frady, Kent, Olshausen, Sommer 2020, Neural Computation 32(12):2311 — Resonator Networks 1.
21. Kent, Frady, Sommer, Olshausen 2020, Neural Computation 32(12):2332 — Resonator Networks 2.
22. Plate 2003 — Holographic Reduced Representation; single-step unbind SNR.

---

## (g) Recommended next-step

**PRIMARY (highest-value, exp_dev-actionable, CPU-cheap):**

**Tier 1 empirical envelope sweep** — pre-flight CPU cell that varies (write_rate, decay_rate) at fixed α, measures K_max_observed, fits the envelope shape. Output: parametric envelope ready to ship as substrate-product depth-bound claim. ~2 hr CPU; pre-reg HARD-PASS/HARD-FAIL per (c) above.

**SECONDARY (parallel, in-house theory, not on critical path):**

**Tier 2 algebraic re-derivation** — couple Kalaj-Λ + Betteti-escape-time to attempt a substrate-specific closed-form K_max(α, write, decay). ~1 week theory work; novel-synthesis P_deflated 0.40-0.50. Validate against Tier 1 empirical envelope. If it works, substrate gets a closed-form depth-bound for productization. If it fails, the empirical envelope is the load-bearing story (which is what we ship anyway).

**Companion file:** `exp_dev_handoff_research_K_max_NESS_correction_drill_2026-06-20.md` — anchor candidates for Tier 1 envelope sweep + Tier 3 GPU validation.

**Field-advisor next-drill candidate:** `nonequilibrium-stat-mech` (Tier-1b new field, drill_count=1 after this) → next adjacency: Hatano-Sasa entropy-production identity applied to Hopfield basin escape (drill candidate A3 in field advisor). Could close a structural gap on whether NESS dimensional analysis gives the (write/decay)-ratio dependency claimed in P3.

P_deflated overall: **0.30** for full HARD-PASS triad (Tier 1 envelope sweep finds robust 2-6× boost with single-knob ratio dependency).
