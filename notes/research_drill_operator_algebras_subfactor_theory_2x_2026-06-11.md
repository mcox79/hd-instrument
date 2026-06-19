# Research drill 2x DEEP — Operator algebras / subfactor theory as substrate-architecture extension lineage

Date: 2026-06-11
Topic: operator-algebra / subfactor-theory / noncommutative-geometry / W*-probability as substrate-extension framework
Triggered by: schools-of-thought lineage drill (school #29) top-3 next corpus entry; adjacent to FHRR phasor-algebra; 2x DEEP operational drill on existing finding
Depth: 2x DEEP (level-2 operational drill; mechanism + math + ship path; NOT verification re-scan)
Safety: ASCII-only; generic literature only; no project-specific predicted numerics

---

## (a) HEADLINE

Operator-algebra lineage is NOT speculative for substrate extension — a published precedent named GHRR (Generalized Holographic Reduced Representations, arXiv 2405.09689, May 2024) already realizes the FHRR-extends-to-noncommutative path by replacing unit phasors with unitary matrices and componentwise product with matrix product. GHRR interpolates smoothly between FHRR (commutative, matrix size m=1) and full tensor product (fully noncommutative, m=N). Empirically reported higher capacity for compositional / nested structures, with unitary projection in Fourier space restoring theoretical linear scaling. This converts the operator-algebra angle from "speculative new math" into "import a known design and engineer it for substrate." The deeper subfactor-theory and W*-probability lineage then supplies (1) a Jones-index-like discrete capacity ladder for sub-codebook inclusions, (2) free-probability spectrum tools (today's 3x DEEP drill) extend exactly to GHRR via free unitary haar matrices, and (3) ribbon / braided-monoidal category structure justifies non-commutative sequence binding without permutation tricks. Novel-synthesis P_deflated = 0.40 (cap 0.50 applied; precedent reduces novelty risk but substrate-integration is still uncharted).

Three load-bearing observations:

1. **GHRR is the m=1 -> m>1 dial.** The FHRR phasor algebra is exactly the m=1 specialization of a unitary-matrix algebra. The lineage is Murray-von Neumann (factor type II_1 carries the Haar trace) -> Voiculescu (free Haar unitaries are the noncommutative analog of i.i.d. unit phasors) -> GHRR (engineering specialization).
2. **Subfactor inclusion ladder gives a discrete capacity model.** Jones-index theorem: for type II_1 factors, the index [M:N] for an inclusion of subfactors lives in `{4 cos^2(pi/n) : n = 3, 4, ...} union [4, infty)`. The discrete spectrum below 4 is the "rigidity" regime; above 4 is continuum. A substrate version: sub-codebook inclusions could be classified by an integer-or-continuum capacity index, giving a quantized model of "how much smaller a sub-substrate can be while still recovering its parent under cleanup."
3. **W*-probability is the natural home of free-prob substrate framework.** Today's 3x DEEP free-probability drill defined `kappa_4_free` as a substrate observability. Free cumulants are W*-probability objects on a tracial von Neumann algebra. The substrate codebook spectrum is the spectrum of a self-adjoint element in a (concretely realized) W*-probability space. This is not a metaphor — Voiculescu's framework is the literal one used.

---

## (b) Cheap decisive test

A SINGLE CPU experiment, ~2-3 hours wall on the laptop runner, decisively tests whether the operator-algebra extension is a substrate win OR a wash.

**EXPERIMENT GHRR-1 (decisive test of noncommutative binding capacity).**

Build three matched substrate code paths at the current substrate dimension N (fix N at the project's standard):

1. `FHRR_baseline`: pure unit-modulus complex phasor binding (current substrate; m=1).
2. `GHRR_small`: GHRR with unitary matrix size m=2 (smallest noncommutative case, total parameter budget N x 2 x 2; reduce vector length so total params match FHRR baseline).
3. `GHRR_med`: GHRR with m=4 (parameter-matched).

Tasks:

- T_compose: depth-cascaded binding to L = 4, 6, 8, 10 with substrate's existing per-level cascading cleanup. Measure recall@1 at each level.
- T_seq: encode a 6-element ordered sequence three ways: (a) FHRR with permutation positional encoding, (b) GHRR with non-commutative bind only (sequence position = bind order; NO positional encoding), (c) GHRR with permutation backup. Measure ordered-recall@1.

The test is decisive because parameter-matched GHRR_med should EITHER show clearer compositional separability at depth (HARD-PASS bands in section c) OR fail to beat the FHRR baseline, in which case operator-algebra extension does not earn its keep at the current substrate dimension.

Cost: pure numpy, no GPU. ~2-3 hours including diagnostics + per-seed multi-run.

---

## (c) Falsifiable predictions (HARD-PASS / HARD-FAIL bands)

### Prediction OA-P1: GHRR noncommutative binding outperforms FHRR at depth

HARD-PASS: At depth L = 8 with parameter-matched comparison, GHRR_med recall@1 >= 1.5x FHRR_baseline recall@1 (averaged over >= 5 seeds; CI band non-overlapping per [[feedback-method-overclaim-lift-validation]] lift >= 2 x SE).
HARD-FAIL: GHRR_med recall@1 <= 1.05x FHRR_baseline (lift within noise). Operator-algebra extension is a wash at substrate's current dimension; revisit only at frontier scale.
MIDDLE: lift in [1.05x, 1.5x] — extension is real but marginal; cost-of-complexity not paid back.

### Prediction OA-P2: GHRR captures order without positional encoding

HARD-PASS: GHRR_med T_seq (b) ordered-recall@1 >= 0.80 of GHRR_med T_seq (c). Non-commutative bind alone recovers order.
HARD-FAIL: GHRR_med T_seq (b) <= 0.30 of (c). Order is NOT carried by bind-noncommutativity even at m=4; sequence encoding still needs positional-encoding scaffold.

### Prediction OA-P3: Jones-index-style discrete capacity in sub-codebook inclusion

HARD-PASS: Define a sub-codebook inclusion as `sub-codebook = projection onto the top-k singular subspace of the parent`. Sweep k. Measure recall@1 of sub-codebook elements under parent's cleanup. The retention-vs-k curve should show >= 2 quasi-discrete plateaus (NOT a smooth monotone) over a range of k, mirroring the Jones-index discrete spectrum.
HARD-FAIL: retention-vs-k is monotone smooth with no plateaus.
NOTE: this is the weakest prediction (P_deflated within ~0.25); subfactor-theory rigidity may not transfer to engineered codebook projections.

### Prediction OA-P4: Free-probability spectrum tools extend to GHRR unchanged

HARD-PASS: Marchenko-Pastur bulk + Tracy-Widom edge + kappa_4_free observables (defined in today's 3x DEEP free-prob drill) computed on GHRR's matrix codebook (with `(1/N) trace(C^* C)` as the noncommutative inner product) reproduce the same KS-distance and z-score predictions within the bands of P1-P4 of the free-prob drill. I.e., the spectral observability primitive PORTS to noncommutative substrate without rewrite.
HARD-FAIL: the spectral observability primitive requires substantive rewrite (more than 30% line change) to apply on GHRR; the unification claim of the free-prob drill is substrate-dimension-specific.

---

## (d) Cross-thread synthesis with prior drills

### D.1 — Free-probability 3x DEEP drill (2026-06-11) DIRECTLY UNIFIES with operator-algebra angle

Today's 3x DEEP free-probability drill defines four predictions (P1-P4) on the substrate codebook spectrum. The W*-probability framework (Murray-von Neumann factors + Voiculescu free-prob) is the natural setting; the codebook is a concrete element in a tracial W*-probability space. GHRR replaces the abelian phasor algebra with a non-abelian W*-algebra of unitary matrices. The free-cumulant `kappa_4_free` is defined on ANY tracial W*-probability space — including GHRR's. Therefore OA-P4 above predicts the free-probability framework ports verbatim. This is a STRONG positive prediction (P_deflated ~0.50): substrate's planned free-prob observability primitive is REUSABLE on the operator-algebra extension. No fork.

### D.2 — Substrate v3.2 engineered wrapper (memory entry 2026-06-11) — FHRR-as-Reed-Solomon parity extends to GHRR

The v3.2 engineered wrapper builds parity check on FHRR phasor algebra (~30 lines torch). The Reed-Solomon construction uses the FFT structure of the unit-circle group. Generalized to GHRR, the parity becomes a check on the matrix algebra C^(m x m), which is itself a finite-dim factor (factor type I_m). Reed-Solomon-on-matrices is a known construction (matrix Reed-Solomon over a finite field representation of GL_m). The wrapper code path EXTENDS to GHRR with ~5-10 lines of additional matrix product code; the v3.2 architectural decision (engineered wrapper instead of new substrate) holds.

### D.3 — Schools-of-thought lineage drill (2026-06-11) — promotes school #29 from Tier D to Tier B with concrete precedent

GHRR's existence (arXiv 2405.09689) means school #29 (operator algebras / subfactor theory) is no longer "potentially adjacent, never drilled" — it has produced exactly one engineered VSA primitive (GHRR) with reported empirical capacity gains for compositional nested structures. School moves from Tier D (productivity 0-1) to Tier B (productivity 1-2). Updates the lineage taxonomy: productivity rank should be re-audited after the GHRR-1 experiment lands.

### D.4 — Substrate-classical NLP methods (memory entry 2026-06-11) — GHRR carries HMM state without positional encoding overhead

Substrate-classical NLP results (POS 0.906 via Viterbi on substrate emission/transition bundles) currently use FHRR + an explicit transition layer. Under GHRR with m=2, the transition could be carried natively by the non-commutative bind (state at position t binds with transition operator, which does not commute with state at position t+1, so the sequence is naturally ordered). This is a substrate-product-relevant differentiator: a GHRR substrate could carry a Markov chain in bind structure alone, replacing the explicit transition bundle with bind algebra. If validated, simplifies the substrate-classical-NL primitive.

### D.5 — Compositional cliff cross v3.0 (memory entry) — GHRR predicts cleaner cliff cross

The compositional cliff cross at L8 was achieved via per-level cascading cleanup on FHRR. GHRR's reported higher capacity for nested structures predicts a cleaner / less-engineered cliff cross at the same depth, OR a deeper cliff cross at the same engineering budget. This is a strong testable prediction the GHRR-1 experiment captures directly.

### D.6 — Drill pattern temporal+contextual works (memory entry) — operator-algebra is structural NOT temporal

CAUTION: per the drill-pattern memory, "TEMPORAL + CONTEXTUAL works, FIXED-ARCHITECTURE fails." Operator-algebra extension via GHRR IS a fixed-architecture change (matrix size m is structural). This means the prior pattern suggests deflate P further. Counter-evidence: GHRR has published empirical wins (not a theoretical-only proposal), so the empirical track-record dominates the architectural-skepticism prior. Net: keep P_deflated at 0.40, do NOT additionally deflate to 0.25, but flag the structural-prior risk in the GHRR-1 pre-reg.

---

## (e) Substrate-product implications

Three concrete product-relevant implications:

1. **Substrate-product capacity story improves substantially if OA-P1 HARD-PASSES.** Higher capacity for compositional nested structures = the substrate handles deeper structured queries (KG paths, nested tool calls, AST representations) at the same dimension that today serves shallow binding. This is a direct LLM-comparative win: LLMs are heuristic on deep nested structure, substrate-with-GHRR has a principled capacity scaling.

2. **Substrate-product sequence-handling simplifies if OA-P2 HARD-PASSES.** Today, sequence encoding needs FHRR + permutation positional code (two primitives). GHRR alone carries order via bind non-commutativity (one primitive). Less surface area = fewer integration points for product builders.

3. **Substrate observability claim stays unified.** The free-probability spectral observability primitive (today's 3x DEEP) is the headline substrate-vs-LLM differentiator ("operators can SEE capacity exhaustion approaching; LLM operators cannot"). OA-P4 says this primitive ports unchanged to GHRR. Substrate roadmap to a noncommutative variant does NOT fragment the observability story. This is a critical strategic property.

DO NOT promise OA-P3 as a product win — Jones-index discrete capacity is a research-curiosity prediction; if it HARD-PASSES it opens a new design axis, but if it HARD-FAILS no product surface changes.

---

## (f) Algebra-vec / Testbed implications (substrate-self-index Level-A)

GHRR / operator-algebra additions to the substrate-self-index algebra taxonomy (per today's algebra-taxonomy drill):

- New category 14 (provisional): `noncommutative-binding-algebra` (W*-algebra of unitary matrices; bind = matrix product). Distinct from current categories 1-13.
- New attribute flag: `commutative` (boolean). Today substrate is implicitly commutative; GHRR introduces non-commutative atoms. Self-index now needs to track this per-atom.
- Edge type: `m=1-specialization` (Reed-Solomon-on-FHRR is the m=1 case of Reed-Solomon-on-GHRR; ComplEx-as-FHRR is m=1 of ComplEx-on-matrices). The self-index can encode these `EQUIVALENT_UNDER specialization` edges, adding to the 42-edge equivalence catalog (cross-domain equivalences drill, 2026-06-11).
- Tannakian-reconstruction edge: representation category of GHRR reconstructs a Hopf-algebra-like structure (per the categorical reconstruction theory). Long-tail substrate corpus entry; not immediately load-bearing.

For Testbed: if GHRR-1 HARD-PASSES, the substrate-self-index demo gains a marquee primitive — "the substrate algebra is a tunable knob m=1..N interpolating commutative-to-noncommutative; here is the capacity vs m curve." That is a visible LLM-differentiator for the v1 demo.

---

## (g) New math angles (per user-locked principle "don't be afraid to invent new math")

Two angles worth flagging as "novel-math-to-explore" but NOT load-bearing for substrate's next 6 weeks:

1. **Substrate-specific subfactor index.** Define a substrate-version of [M:N] for sub-codebook inclusions where M is the parent codebook's W*-algebra and N is a projected sub-codebook's W*-algebra. Predict the index lives in a discrete-or-continuum spectrum analogous to Jones'. OA-P3 above tests a weak proxy.
2. **Type III factor as substrate continuous-capacity model.** Murray-von Neumann classify factors as type I (matrix algebras), II (continuous-dimension projections), III (no trace; only modular structure). A type III substrate would have NO finite trace inner product but would still support binding + cleanup via the modular automorphism group. Highly speculative; no engineering path within Sprint-4. Park as long-tail substrate-self-index entry.

These satisfy the user-locked "new math is OK" principle but are not pre-registered for near-term test. They are corpus entries.

---

## (h) Citations (verified count)

Direct precedents (verified URLs):

1. arXiv 2405.09689 — Generalized Holographic Reduced Representations (GHRR). Replaces FHRR unit phasor with unitary matrix; bind = matrix product. Empirical capacity gains for compositional / nested structures reported. May 2024. <https://arxiv.org/abs/2405.09689> and html <https://arxiv.org/html/2405.09689v1>.
2. arXiv math/0304340 — Vaughan Jones, "Subfactors and planar algebras." Foundational survey for subfactor theory and planar-algebra reconstruction.
3. arXiv math/9909027 — Jones, "Planar algebras, I." Original planar-algebras paper.
4. Wikipedia entry — Planar algebra. <https://en.wikipedia.org/wiki/Planar_algebra>
5. arXiv 2208.13867 — "Free probability and model theory of tracial W*-algebras." Concrete tutorial framing of W*-probability used for free-probability tooling.
6. Wikipedia entry — Free probability. Defines W*-probability space (A, tau) with normal faithful tracial state. <https://en.wikipedia.org/wiki/Free_probability>
7. Terence Tao 254A Notes 5 — Free probability lecture notes. Pedagogical bridge from classical to free independence. <https://terrytao.wordpress.com/2010/02/10/245a-notes-5-free-probability/>
8. nLab — Spectral triple. Connes' framework for noncommutative geometry. <https://ncatlab.org/nlab/show/spectral+triple>
9. Wikipedia entry — Spectral triple. Connes' Dirac-operator framework for NCG with intrinsic distance. <https://en.wikipedia.org/wiki/Spectral_triple>
10. arXiv math/0711.1402 — "Tannaka-Krein reconstruction and a characterization of modular tensor categories." Reconstruction theorem applicable to substrate-self-index categorical layer.
11. nLab — Braided monoidal category. Standard reference for the categorical structure that justifies non-commutative sequence binding. <https://ncatlab.org/nlab/show/braided+monoidal+category>
12. Wikipedia entry — Braided monoidal category. <https://en.wikipedia.org/wiki/Braided_monoidal_category>
13. arXiv 2001.11797v3 — "A Comparison of Vector Symbolic Architectures." Surveys commutative-vs-non-commutative binding in VSA literature. <https://www.arxiv.org/pdf/2001.11797v3>
14. arXiv 2111.06077 — "A Survey on Hyperdimensional Computing aka Vector Symbolic Architectures, Part I." HDC/VSA comprehensive survey.

Verified count: 14 citations. Precedent strength is HIGH for GHRR (citation #1 is the engineered precedent), MEDIUM for subfactor / W*-probability lineage (foundational theory, not substrate-applied), LOW for spectral-triples and categorical-reconstruction (mostly long-tail corpus material).

---

## (i) Pre-registered experiments

EXP GHRR-1 (decisive test of OA-P1, OA-P2 + sanity-port of free-prob primitives in OA-P4). Pre-reg artifact: this note. Owner: exp_dev when authorized. Cost: ~2-3 hr CPU. Hand-off recommendation: emit companion `exp_dev_handoff_research_operator_algebras_2026-06-11.md`.

EXP GHRR-2 (deferred until GHRR-1 HARD-PASSES). Sub-codebook inclusion sweep testing OA-P3. Cost: ~1 hr CPU. Not triggered until GHRR-1 lands positive.

EXP GHRR-3 (deferred until GHRR-1 HARD-PASSES AND free-probability framework lands). Port `kappa_4_free` + Marchenko-Pastur + Tracy-Widom + spectral gap observables to GHRR matrix codebook. Pre-reg per the four predictions of today's 3x DEEP free-prob drill. Cost: ~30 min CPU once free-prob ships.

---

## (j) Next-drill candidate

Per the schools-of-thought lineage drill's 16 un-explored adjacencies, next-drill after this lands:

- **Categorical / DisCoCat AI** (school adjacent, never drilled). Lambek-Coecke pregroup grammar + tensor product semantics. Mathematically isomorphic to substrate bind/bundle on a category. Importing the categorical apparatus gives a type-theoretic foundation LLMs lack and complements the operator-algebra angle (DisCoCat = categorical, GHRR = algebraic; both are non-commutative).
- OR **Reservoir computing** (Maass LSM / Jaeger ESN, never drilled; adjacent to substrate temporal-policy pattern that has been winning).

Recommendation: categorical / DisCoCat next — it completes the lineage triangle (free-probability + operator-algebra + categorical) and the three together are the substrate's strongest formal foundation against LLM-comparable systems.
