# Research drill — continuous SHARES_MATH + threshold-robustness (INV-3 support)

date: 2026-06-13
model: opus-4-7 (synthesis) + sonnet (4x parallel lit-scan)
budget used: ~35 min
trigger: Skunkworks INV-3 — SHARES_MATH is boolean (332 edges over 61 atoms -> 12 archetype classes); skunkworks flagged that mathematical equivalence is naturally graded; 12 classes may be a boolean-threshold artifact.

---

## (a) HEADLINE

Continuous-valued SHARES_MATH is a well-supported design move. Fuzzy/quantale-valued bisimulation is the right formal scaffold (substrate becomes a [0,1]-valued coalgebra rather than a boolean one); the 12-archetype number IS testable as a threshold artifact by a Markov-stability / plateau sweep over the score threshold tau; a *robust plateau* in the archetype count over a wide tau-band is the falsifiable claim. Three concrete score formulations are proposed below; INV-3 cell is a sweep + plateau-width measurement; HARD-PASS = >= 1-decade tau plateau with stable archetype count +/- 1. Substrate-product upside is non-trivial: continuous SHARES_MATH unlocks behavioral-distance queries (how-much-math do two atoms share) that boolean cannot answer, and aligns the substrate with the coalgebraic-bisimulation literature (LLMs have no such formal scaffold).

P_continuous_score_works (deflated, novel-synth-capped) = 0.45
P_robust_plateau_at_current_tau (deflated) = 0.40
P_12_archetypes_survive_threshold_robustness_test (deflated) = 0.35

(Plateau survival probability is lower than score-works because boolean cutoffs are exactly the kind of threshold most likely to land at a non-plateau edge unless the substrate authoring biased SHARES_MATH toward all-or-nothing decisions, which would re-validate the boolean choice.)

---

## (b) Cheap decisive test

Sweep the continuous SHARES_MATH threshold tau across ~2 decades; for each tau, recompute archetype partition (e.g. coalgebraic bisimulation closure on the thresholded graph or modularity-max on the weighted graph); plot {archetype_count(tau), partition_distance_to_canonical(tau)} vs log(tau). Look for a plateau: a tau-band [tau_lo, tau_hi] over which the partition is stable (Adjusted Rand Index >= 0.95 vs central tau) AND archetype count varies by <= 1.

Total cost: ~1-2 hr CPU after the continuous score is authored (re-uses existing 61 atoms + 332 boolean edges as a sparsity skeleton). NO new ingest required.

---

## (c) Falsifiable predictions

### Continuous score formulations (3 candidates ranked by feasibility)

**Score #1: Definition-text Jaccard + formal-symbol overlap (cheap, substrate-native).**
For atoms a, b:
- J_def(a,b) = |D(a) cap D(b)| / |D(a) cup D(b)| over tokenized definition text (filtered for math content)
- S_sym(a,b) = |Sym(a) cap Sym(b)| / sqrt(|Sym(a)| * |Sym(b)|) over the set of formal symbols/operators each atom references
- SHARES_MATH_cont_1(a,b) = alpha * J_def + (1-alpha) * S_sym, alpha tunable but secondary

Grading rationale: This mirrors ontology-alignment standard practice (Tushkanova et al. 2017, Probabilistic Similarity Logic). Continuous, bounded [0,1], reproducible, no embeddings.

**Score #2: Lemma-dependency / DEPENDS_ON overlap (structural).**
For atoms a, b with DEPENDS_ON closures C(a), C(b) in the substrate graph:
- SHARES_MATH_cont_2(a,b) = |C(a) cap C(b)| / |C(a) cup C(b)| (Jaccard of dependency closures)

Grading rationale: Curry-Howard-friendly — atoms that share lemma-dependency closures share proof-content; reuses BATCH 17 generalized typing context (6 edge types, 2491 edges). Naturally continuous because closure sizes are integer ratios.

**Score #3: Type-signature similarity (Curry-Howard / coalgebraic).**
For atoms a, b with type signatures sigma(a), sigma(b):
- SHARES_MATH_cont_3(a,b) = sim_type(sigma(a), sigma(b)) where sim_type is a graded match over (input type, output type, axiom dependencies) — discrete components combined with weights summing to 1.

Grading rationale: Maps directly onto Wild & Schroeder 2024 quantale-valued logic; substrate atoms become objects in a [0,1]-valued coalgebra; the threshold sweep is then a sweep over the quantale's truncation level.

### HARD-PASS thresholds

- **HP-1 (score validity):** Spearman rank correlation between SHARES_MATH_cont and the existing boolean SHARES_MATH is >= 0.75 (continuous score recovers the boolean signal as a coarsening).
- **HP-2 (robust plateau):** There exists a tau-band [tau_lo, tau_hi] with tau_hi / tau_lo >= 10 (>= 1 decade) over which archetype_count(tau) varies by <= 1 AND ARI vs central-tau partition >= 0.95.
- **HP-3 (existing 12-archetypes preserved):** The plateau partition is consistent (ARI >= 0.85) with the existing 12-archetype boolean partition; if both HP-2 and HP-3 pass, then the 12 archetypes are vindicated as a structural feature, NOT a threshold artifact.

### HARD-FAIL thresholds

- **HF-1:** No tau-band of width >= 0.3 decades shows stable archetype count (partition is hyper-sensitive to tau -> the discovered partition IS a threshold artifact; substrate must report archetypes as a tau-dependent observable, not a categorical claim).
- **HF-2:** Continuous-score archetype count at the modal plateau is >= 20 or <= 5 (boolean 12 was dramatically wrong; either over- or under-collapsing equivalence).
- **HF-3:** Spearman vs boolean SHARES_MATH < 0.50 (continuous score is measuring something different, NOT a refinement; pick a different score and rerun).

### MIDDLE-BAND (PARTIAL outcome)

- HP-1 passes (continuous score is a real refinement), HP-2 fails OR plateau width < 1 decade BUT > 0.3 decade. This means there IS a graded structure but it is sensitive enough that "archetype count" should be reported with a tau-band confidence interval, not as a single integer. Substrate-product implication: report archetypes as a function of tau, with the modal plateau width as a robustness statistic (mirroring the two-vector alpha plateau pattern in MEMORY.md).

---

## (d) Cross-thread synthesis

**Prior-art mapping:**

1. **Fuzzy / quantale-valued bisimulation** (Wild & Schroeder 2024 STACS; Bonchi et al. on quantitative bisimulation; arXiv 2007.01033 on fuzzy lax extensions): the coalgebra community has been doing exactly this for ~10 years. Bisimilarity is generalized from a boolean equivalence relation to a [0,1]-valued hemimetric (or quantale-valued relation). Substrate authoring its SHARES_MATH as a quantale-valued relation puts us on first-class coalgebraic ground. Key technical: fuzzy bisimulations need NOT themselves be hemimetrics (Wild-Schroeder analog of "classical bisimulations need not be equivalence relations") — this means we can author a noisy continuous SHARES_MATH and still get clean bisimilarity closure.

2. **Ontology alignment continuous scores** (Tushkanova et al. 2017, Springer; Probabilistic Similarity Logic arXiv 1203.3469): the standard practice for "how much shared mathematical content between two concepts" is a continuous theta in [0,1] over (definition overlap, symbol overlap, structural similarity). Direct precedent for our Score #1.

3. **Markov-stability / multi-scale community detection** (Delvenne, Yaliraki, Barahona 2010; arXiv 1109.5593): partition stability via a Markov diffusion process gives an explicit framework for "communities at different scales" — the substrate threshold tau is essentially a zoom level. Crucially: "a relevant partition should be both persistent over a comparably long timescale and robust with respect to slight variations in graph structure" — this IS the plateau test (HP-2 above).

4. **Resolution-parameter plateaus in modularity** (Fortunato 2010 survey arXiv 0906.0612; Reichardt-Bornholdt; Lambiotte): "the length of a plateau gives a measure of the stability of the partition" — this is the direct methodological analog to substrate's `two_vector_alpha_wide_robust_plateau` memory entry (MEMORY.md). Robust-plateau methodology is a publication-standard test for "result X holds across a wide parameter band of width W."

5. **Cross-link with substrate prior:** the existing memory entry [substrate_two_vector_alpha_wide_robust_plateau_high_d_orthogonality_2026-06-12.md] established robust-plateau as a substrate methodology pattern (alpha in [0.15, 10] for two-vector composite; ~70x band; substrate documented the band-width as a robustness statistic). INV-3 inherits this methodology verbatim — same plateau-detection logic, same band-width reporting.

6. **Cross-link with KP P6 + 13th methodology rule (USER craftsman 2026-06-13):** if continuous SHARES_MATH HARD-PASSes with a robust plateau, the substrate gains TWO new observability dimensions (continuous score distribution + plateau width); these add to the 9d spectral observability pillar as graph-level structural observables independent of the spectral ones. Substrate observability dimension count: 9d spectral + 2d SHARES_MATH = 11d. LLM observability = 0.

7. **Cross-link with don't-lock-in-frameworks (USER 7th rule, 2026-06-13):** Skunkworks flag itself is an instance of this rule — questioning whether the boolean SHARES_MATH choice was premature lock-in. The right outcome of INV-3 is to either RE-AFFIRM boolean (if HP-2 + HP-3 pass, 12 archetypes survive threshold-robustness) or REFACTOR to continuous (if HF-1 fires). Either outcome is structurally valuable.

---

## (e) Substrate-product implications

**If INV-3 HARD-PASS (HP-1 + HP-2 + HP-3):**

- Substrate gains *graded* SHARES_MATH that supports behavioral-distance queries ("how much math do atom a and atom b share?" -> [0,1] answer, not just yes/no).
- The 12 archetypes are vindicated as a *structural* partition (not a threshold artifact). This becomes a substrate-product positioning claim: "substrate archetypes survive a 1-decade threshold-robustness sweep" — quantitative robustness statement LLMs cannot match.
- Substrate is now formally a quantale-valued coalgebra. This is a new technical positioning lane: "substrate atoms form a fuzzy-bisimilarity quotient with empirically-validated robust plateau." Aligns substrate with ~10 years of coalgebraic-bisimulation literature.
- New capability surface: GRADED_EQUIVALENCE_QUERY ("rank atoms by how-much-math-they-share with X") — analogous to but distinct from cosine similarity (graded mathematical equivalence is structural, not semantic).

**If INV-3 HARD-FAIL (HF-1):**

- 12-archetype claim is downgraded from "categorical structural feature" to "tau-dependent observable." Substrate documentation must report archetype count as a function of tau.
- Substrate-product positioning loses a categorical claim but gains a *robustness-statistic claim*: "substrate archetypes vary smoothly with continuous equivalence threshold; ARI vs canonical = f(tau)." Still LLM-uncomparable, but weaker.
- INV-3 fail does NOT invalidate KP P6 (12 distinct combination-cells >= 3 atoms is a structural-orthogonality claim independent of SHARES_MATH archetypes; the two are different partition functions).

**If INV-3 PARTIAL (HP-1 passes, HP-2 marginal):**

- Substrate adopts continuous SHARES_MATH as the primary representation; boolean is a derived view at the modal plateau tau. Report archetype count with tau-band confidence interval. This is the most likely outcome (P_PARTIAL ~ 0.40).

**Honest framing per "we may be first to build a system like ours":**

The prior work cited above informs but does not govern. Wild-Schroeder 2024 gives quantale-valued bisimulation for *labeled transition systems* — not for typed-derivation graphs over math atoms. Ontology alignment gives continuous similarity scores for *concept-pair matching* — not for whole-graph archetype induction. Markov-stability gives multi-scale community detection for *modularity-based partitions* — not for bisimilarity-based partitions. Substrate is composing all three into a use-case the literature has not directly addressed. The plateau-robustness methodology IS standard practice (Fortunato survey) and we inherit it cleanly. The score formulations ARE adapted from standard ontology-alignment practice. The bisimilarity scaffold IS adapted from quantale-valued coalgebra. The composition is novel; the components are not. Calibration penalty applied accordingly (novel-synth cap at 0.50; P_HARD_PASS deflated to 0.35).

---

## (f) Citations (verified count: 8 distinct sources)

1. Wild, P. & Schroder, L. (2024). "Expressive Quantale-Valued Logics for Coalgebras: An Adjunction-Based Approach." LIPIcs STACS 2024 vol 289. https://drops.dagstuhl.de/storage/00lipics/lipics-vol289-stacs2024/LIPIcs.STACS.2024.10/LIPIcs.STACS.2024.10.pdf
2. Forster, J. et al. (2022). "Characteristic Logics for Behavioural Hemimetrics via Fuzzy Lax Extensions." Logical Methods in Computer Science 18(2). https://arxiv.org/html/2007.01033
3. Bonchi, F. et al. (2015). "A Definition Scheme for Quantitative Bisimulation." https://arxiv.org/pdf/1509.08563
4. Tushkanova, O. et al. (2017). "Classification of Alignments Between Concepts of Formal Mathematical Systems." Springer LNCS. https://link.springer.com/chapter/10.1007/978-3-319-62075-6_7
5. Broecheler, M. et al. (2012). "Probabilistic Similarity Logic." https://arxiv.org/pdf/1203.3469
6. Karrer, B. et al. (2015). "Measuring robustness of community structure in complex networks." https://arxiv.org/pdf/1503.08012
7. Delvenne, J-C. et al. (2011). "Markov dynamics as a zooming lens for multiscale community detection." https://arxiv.org/pdf/1109.5593
8. Fortunato, S. (2009). "Community detection in graphs." Phys Reports survey, arXiv 0906.0612. https://arxiv.org/pdf/0906.0612

Cross-cited substrate notes:
- notes/MEMORY entry: substrate_two_vector_alpha_wide_robust_plateau_high_d_orthogonality_2026-06-12.md (plateau methodology precedent)
- notes/MEMORY entry: substrate_architecture_3_axis_EMPIRICALLY_ORTHOGONAL_Cell_3_KP_P6_HARD_PASS_USER_craftsman_VERBATIM_corroborated_13th_rule_2nd_appearance_2026-06-13.md (KP P6 archetype-cell relationship)
- notes/MEMORY entry: feedback_always_reconsider_frameworks_dont_lock_in_prematurely_USER_LOCKED_2026-06-13.md (skunkworks INV-3 IS this rule firing)

---

## Pre-registered fail bands (for INV-3 cell envelope)

- ARI_vs_central_tau on plateau >= 0.95 -> HARD-PASS
- ARI_vs_central_tau on plateau in [0.80, 0.95) -> PARTIAL
- ARI_vs_central_tau on plateau < 0.80 -> HARD-FAIL
- Spearman(continuous, boolean) >= 0.75 -> score-valid
- Spearman in [0.50, 0.75) -> score-marginal (report but use cautiously)
- Spearman < 0.50 -> score-invalid (HF-3)
- Plateau width >= 1 decade -> robust
- Plateau width in [0.3, 1.0) decades -> marginal-robust
- Plateau width < 0.3 decades -> threshold-artifact (HF-1)
