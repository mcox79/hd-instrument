# Research drill: Stage 1 regime-map — 4 negatives, 2x lit-scan (2026-07-03)

Trigger: USER standing rule `feedback_route_negatives_to_research_2x_3x_revival_drills`. 2x discipline: broad lit-scan (4 parallel Sonnet sub-agents) then focused synthesis. All queries generic-math-term only per query-privacy rule; no substrate-internal identifiers used off-platform.

## HEADLINE

Lit-scan closes 3 of 4 negatives with existing theory (no novel experiment needed to explain the *mechanism*, only to locate the substrate's operating point within known theory); NEG1 (N x depth cross-term) requires an in-band follow-up cell because the prior test sat at saturation extremes, not the theoretically interesting crossover zone. K-axis question resolves toward "fold into cleanup-mechanism," not a 6th CG_META axis.

## NEG 1 — N x TOPOLOGY (chain-depth) interaction

**Lit synthesis (5 sources):**
- Plate, *Holographic Reduced Representations*, IEEE TNN 1995 (Tier1, classic). Single-level bind/unbind: SNR ~ sqrt(N)/m, additive noise per binding — clean separable law, no cross-term, for shallow composition.
- Frady, Kleyko & Sommer, *A Theory of Sequence Indexing and Working Memory in RNNs*, Neural Computation 2018 (Tier2). Extends to chained/recurrent retrieval: "extensive capacity" (linear in N) requires a decay/forgetting parameter *jointly tuned* against N — not a fixed additive f(L).
- Frady, Kleyko & Sommer, *Resonator Networks I/II*, Neural Computation 2020 (Tier2). Joint N-vs-number-of-factors combinatorial capacity bounds — non-separable near capacity.
- Clarkson, Ubaru & Yang, *Capacity Analysis of VSA*, arXiv:2301.10352 (2023, Tier2). Formal dimension bounds for membership/composition tasks.
- Kleyko et al., HDC/VSA survey Part I, arXiv:2111.06077 (Tier2).

**Theory vs empirical:** Classical theory (Plate) predicts separability, and that IS what was found at floor N=256 / ceiling N=2048 (both far from any capacity boundary — cross-term=0 is the theoretically UNSURPRISING regime, consistent with "saturation-vacuous" framing already flagged). But later work (Frady/Sommer, resonator networks) shows the interesting cross-term is a near-capacity phenomenon: as L approaches a threshold fraction of N, degradation becomes non-additive/non-smooth. So today's null at the extremes is not evidence against a mid-band cross-term — it's simply outside the regime where lit predicts one would appear.

**Concrete deliverable — follow-up cell design (b):** Target axis-crossing: N held near the empirically-known cliff value (not floor/ceiling) x L in {2,4,8,16}, expressed as ratio L/N_cliff rather than raw L. Expected discriminator: correlation(N, L) on retrieval accuracy should rise as L/N_cliff ratio increases (cross-term should be near-zero at low L/N_cliff, non-zero as L/N_cliff grows). HARD-PASS: measured cross-term coefficient > 0.15 in the top L/N_cliff bucket vs < 0.05 in bottom bucket. HARD-FAIL: cross-term stays < 0.05 across all buckets tested — would indicate the substrate's per-step cleanup resets noise (consistent with prior-arc STORAGE finding that SHARDED supports arbitrary depth) and N/L truly are separable in this substrate's chain mechanism, at least for the storage primitive tested.

**P_deflated:** raw confidence in the lit-based prediction ~0.55-0.60 (Frady/Sommer result is real but the "near capacity" framing is an inference, not a proven universal law); apply calibration penalty -0.20 → **P=0.37**.

## NEG 2 — STORAGE x ALGEBRA (non-superimposable) theoretical foundation

**Lit synthesis (4 source clusters):**
- Kanerva, *Sparse Distributed Memory*, MIT Press 1988 (Tier1). SDM capacity scales with number of hard-location storage elements (hardware, extensive) — independent of vector dimension N — vs Hopfield capped at ~0.14N (fixed fraction of one shared vector's dimension).
- Willshaw 1969 / Amari-style sparse associative net literature (surveyed in arXiv "On associative NNs for sparse patterns with huge capacities" and arXiv:1512.08892 "Comparative Study of Sparse Associative Memories") (Tier1/Tier2). Sparse-coded local models: N^2/(log N)^2 capacity vs dense Hopfield N/(log N) — qualitatively different scaling class tied to coding locality/sparsity.
- Sphere-packing / channel-coding information-theoretic bound literature on Kanerva-style memory (Tier1/Tier2 generic). Universal ceiling 1 - h2(delta); local/hash schemes approach it by adding independent sites; superposition schemes are capped by one shared vector's crosstalk budget.
- Plate 1995 (Tier1, cross-referenced): bundling capacity is exponential in D but is a single-shared-vector limit — crosstalk grows with number of co-superposed items.

**Theory vs empirical:** This is well-established, not contested, textbook associative-memory theory. Today's finding (SHARDED-per-antecedent handles arbitrary chain depth; global BUNDLED collapses at L>=4, NPROP>=20) is exactly what this theory predicts: local/per-key storage buys capacity by adding independent storage sites (degrees-of-freedom multiplication), while global superposition forces all items to share one fixed-dimensional noise budget (crosstalk scales with item count). The accepted explanation is **crosstalk-noise-scaling-with-shared-vector-occupancy** (superposition) vs **extensive-capacity-via-independent-addressable-sites** (local/sharded) — both ultimately bounded by the same sphere-packing ceiling, but reached via different routes. Not a surprise; a confirmation.

**Concrete deliverable — research memo (a), 190 words:** STORAGE non-superimposability is not an empirical curiosity requiring a bespoke theory — it recapitulates the 55-year-old Willshaw/Kanerva-vs-Hopfield distinction. Local/hash-keyed storage (SHARDED) is capacity-extensive because each key gets its own storage site; failures are per-site coding-density failures (Willshaw N^2/(log N)^2 regime), not shared-vector crosstalk. Global superposition (BUNDLED) forces every stored item into one fixed-N vector; capacity is bounded by that vector's crosstalk budget, which grows with item count and, per NEG1, may also interact with compositional depth. Product implication: STORAGE choice is not a free/exchangeable dial in the CG_META axis set — it fundamentally picks which of two theoretically distinct capacity regimes (extensive vs shared-budget) the substrate operates in. Any capacity claim must state which regime it is measuring, not report SHARDED and BUNDLED cliffs as though comparable on a single axis. No new cell needed to explain the mechanism; a cell IS still useful to locate the substrate's specific crossover constants (analogous to measuring alpha_c empirically) — but that's parameter-fitting, not foundational discovery.

**P_deflated:** raw confidence very high (~0.80, convergent Tier1 sources, textbook result) but capped per novel-synthesis rule at **P=0.50** (applying 55-year-old theory to this substrate's specific implementation is a synthesis step, not a direct citation).

## NEG 3 — BUNDLED cliff geometry (step-function vs continuous)

**Lit synthesis (4 sources):**
- Amit, Gutfreund & Sompolinsky 1985 (Tier1, classic). Standard Hopfield: discontinuous first-order transition at alpha_c ~ 0.138N — high-overlap solution persists then vanishes entirely; no smooth interpolation.
- Krotov & Hopfield, *Dense Associative Memory*, 2016 (Tier1), + Lucibello & Mézard, *Exponential Capacity of Dense Associative Memories* (Tier2/3). Higher interaction order (quadratic -> polynomial -> exponential/log-sum-exp) makes storage capacity scale super-linearly then exponentially, and basins stay large/well-separated — higher order sharpens the transition further, does not soften it.
- Ramsauer et al., *Hopfield Networks is All You Need*, 2020 (Tier1/2, via secondary sources). Log-sum-exp energy produces distinctly separated broad-low-energy vs sharp-high-energy basins — reinforcing retrieve-or-fail character.
- Counter-example: scale-free-topology Hopfield study, PLOS ONE (Tier2/3). Found GRADUAL error-rate rise (< 0.3 even near capacity) instead of a jump — topology/structure can convert sharp to gradual.

**Theory vs empirical:** Theory PREDICTS exactly what was found — modern/dense Hopfield on BUNDLED storage is expected to show a sharp, near-step capacity transition, especially as interaction order increases (softmax-like energy = high effective order). The absence of any M in {100,200,400,800} landing in the [0.30, 0.95] mid-band at N=2048 is the textbook first-order-transition signature, not an anomaly requiring explanation. The one documented exception (topology-altered networks showing gradual degradation) is NOT applicable here since BUNDLED has no altered connectivity topology.

**Concrete deliverable — cell design suggestion (b):** If a mid-band IS wanted for discriminator purposes, don't search M at fixed N — instead sweep N *near* alpha_c*M (i.e., pick M then scan N across a narrow window straddling M/alpha_c) since the transition is sharp in the *ratio* M/N, not in M alone at fixed large N. Expected discriminator: accuracy vs M/N ratio should show the same first-order jump — HARD-PASS: transition width (90%->10% accuracy) spans < 0.05 in M/N; HARD-FAIL: transition width > 0.20 in M/N (would contradict the sharp-transition literature and be the actually novel finding).

**P_deflated:** raw confidence high (~0.70, Tier1 AGS + Krotov-Hopfield convergent, and it explains rather than surprises) minus calibration -0.20 → **P=0.50** (capped, also touches novel-synthesis territory for softmax-cleanup specifically vs classical outer-product Hopfield).

## NEG 4 — K axis: separable dimension or retrieval-mechanism detail?

**Lit synthesis (4 sources):**
- Kanerva 1988 SDM (Tier1). K (expected active hard locations) is DERIVED from N and an activation radius r via Hamming-sphere intersection volume — tuned to hit a target activation fraction, not chosen independently of N.
- Majani, Erlanson & Abu-Mostafa, *On the K-Winners-Take-All Network*, NeurIPS 1988 (Tier1). K treated purely as a circuit-design/mechanism parameter; no capacity-scaling claim tying it to a storage formula.
- kWTA / sparse-coding literature, e.g. PMC6597036 (Tier2). K/N frames the classic local-code (K=1) vs dense-code (K=N) tradeoff; optimal sparsity K* ~ Theta(log N) in Willshaw-style nets — an explicit K-N coupling, not an independent axis.
- General KNN / curse-of-dimensionality literature (Tier2/3). For fixed K, retrieval quality degrades as N grows (distance concentration); compensating requires M to scale with N.

**Theory vs empirical:** Convergent across all 4 sources: K is never treated as an independent orthogonal capacity axis in the literature. It's either (a) derived from N + a target SNR/radius (Kanerva), (b) a free mechanism knob with no capacity-formula role (Majani et al.), or (c) tightly coupled to N via an optimal-sparsity law (K* ~ log N). USER's observation that "K matters on retrieval" is consistent with this literature — K matters BECAUSE it's coupled to N/cleanup-mechanism choice, not because it's an independent 6th capacity axis.

**Concrete deliverable — decision (b/c hybrid):** Restrict K to the retrieval arc, parameterized as K/N or K vs log(N) rather than swept as a raw independent integer alongside M and N. Do not promote to 6th CG_META axis.

**P_deflated:** raw confidence medium (~0.55, generic literature convergent but not substrate-specific) minus calibration -0.15 → **P=0.40**.

## Overall NEG4 K-sweep decision

**(b)+(c) hybrid: restrict K to the retrieval arc, and within that arc, collapse it into the cleanup-mechanism parameterization (K/N or K vs log N ratio), not a free-standing 6th CG_META axis.** Rationale: every source found treats K as either derived from N or as an artifact of mechanism choice (WTA circuit design, SDM radius tuning, sparse-coding density). Promoting it to a 6th orthogonal axis alongside STORAGE/N/TOPOLOGY/ALGEBRA/MECHANISM would misrepresent a coupled parameter as an independent one — the same category error the STORAGE-non-superimposability finding (NEG2) warns against in reverse (there, two things that looked comparable turned out to be different regimes; here, something that looks like it needs its own axis turns out to be a derived quantity of an axis that already exists).

## Cross-thread synthesis

NEG1-3 form one coherent picture: separability/independence claims (N x depth, STORAGE regimes, BUNDLED cliff shape) are governed by 40-70-year-old associative-memory and VSA capacity theory. The substrate's job in each case is to locate ITS OWN operating constants (alpha_c-equivalent, crossover N, L/N_cliff ratio) within known theoretical shapes, not to discover new shapes. NEG4 extends this: K is a derived/coupled quantity across every source scanned, reinforcing that CG_META's existing 5-axis structure should stay at 5, with K folded into MECHANISM (cleanup choice) within the retrieval arc specifically.

## Substrate-product implications

1. Capacity claims for the substrate MUST state which storage regime (extensive/local vs shared-budget/superposition) is being measured — they are not comparable on one cliff, by 55-year-old theory, not a substrate quirk. This affects how capacity numbers are reported to users/product (two different "capacity" concepts, not one dial).
2. The N x depth-L cross-term question is NOT closed by the floor/ceiling test already run — a real follow-up cell targeting the in-band crossover is warranted (design given above) before claiming independence as a general property.
3. BUNDLED's step-function cliff means product-facing capacity guidance for BUNDLED-backed features should message "works reliably up to M items, degrades sharply after" rather than "gradual degradation" — matches theory, informs UX/reliability framing.
4. K should not appear as a user-facing/product "5th knob" independent of cleanup-mechanism selection — bundling it into mechanism choice keeps the product's mental model aligned with the theory.

## Citations (verified count)

16 distinct sources across 4 negatives: Tier1 = 7 (Plate 1995, Kanerva 1988, Willshaw 1969, Amit-Gutfreund-Sompolinsky 1985, Krotov-Hopfield 2016, Ramsauer et al. 2020, Majani-Erlanson-Abu-Mostafa 1988), Tier2 = 8 (Frady-Kleyko-Sommer 2018 + 2020 x2, Clarkson-Ubaru-Yang 2023, Kleyko survey 2021, arXiv:1512.08892, sphere-packing/info-theoretic bound literature, kWTA/PMC6597036, KNN curse-of-dimensionality literature), Tier3 = 1 (scale-free-topology PLOS ONE counter-example, Lucibello-Mézard treated as Tier2/3 borderline).

## Cheap decisive test (single follow-up if only one is funded)

NEG1's in-band L/N_cliff sweep is the highest-value follow-up: it is the only one of the 4 negatives where lit does NOT already predict today's specific result (the other 3 are theory-confirms-empirics). Design: hold N at the empirically-known BUNDLED cliff value, sweep L in {2,4,8,16} expressed as L/N_cliff ratio, measure cross-term coefficient. HARD-PASS: cross-term > 0.15 in top bucket. HARD-FAIL: cross-term < 0.05 in all buckets (confirms separability holds even near capacity for this substrate's chain mechanism — a genuinely novel, substrate-specific finding since it would contradict the Frady/Sommer near-capacity coupling literature).
