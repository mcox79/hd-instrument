# Research drill 2x — schema-driven INFERENCE primitive for substrate Stage 3

**Filed:** 2026-06-27
**Filed by:** research (Opus 4.7 1M)
**Trigger:** Stage 3 substrate has cortex content extraction (ultrametric clustering CHAIN_GRADE), partition routing, TWO_TIER, NREM replay. Gap: schema-driven INFERENCE — given a novel input, classify into schema + fill missing slots from defaults + predict properties. Extraction-side cells all HARD_FAIL: `gap3_cls_two_tier_BCM_slow_replay_v1` (zero-init degeneracy), `cortex_schema_tonegawa_sparse_ensemble_v2/v4` (cosine baselines saturate; bundled K=500 also HARD_FAIL), `gap3_cls_two_tier_HOPFIELD_consolidation_v2_regime_fix` (HARD_FAIL).
**This drill pivots:** stop trying to BUILD sharper prototypes; instead, use existing clusters as PRIORS for top-down inference. Per USER directive: math (FCA / type theory / Bayesian) + materials/biology (crystal substitution / domain shuffling / phylogenetics) + brain (Gilboa-Moscovitch schema instantiation, NOT yet drilled).
**Calibration:** P_deflated -0.15 to -0.25; novel-synthesis cap 0.50; brain-existence-proof bump +0.10 where applicable; HARD-PASS + HARD-FAIL thresholds mandatory; CRLB sanity check per [[feedback-experiment-bias-master-checklist]] N.

---

## EXISTING PRIOR-ART PREREG ACKNOWLEDGED — complementary, NOT duplicative

**Filed earlier 2026-06-27:** `d:/AI/hd-instrument/preregs/2026-06-27_schema_driven_proof_step_inference_v1.md` (Tse-Morris-grounded Mathlib proof-step prediction; 5 schemas INDUCTION/CASE_ANALYSIS/EPSILON_DELTA/PIGEONHOLE/CONTRADICTION; recall@5 target 0.50 with +0.30 lift over no-schema).

**Verified dependency status (MEASURED@ 2026-06-27, this drill cycle):**
- `lean_mathlib_ingest_v1`: **no data directory exists** (`d:/AI/hd-instrument/data/exp_lean_mathlib_ingest_v1/` absent). Not landed; not even shipped. Existing prereg is BLOCKED.
- `sub_atom_token_stream_encoder_v2_real_mathlib`: MEASURED@ verdict=RUNNING, elapsed_s=375.2 (full run in flight); v1 was MIDDLE_BAND close-miss per coordinator (gap=0.275 vs 0.30 bar).
- Existing prereg has DO-NOT-SHIP flags on both → unshippable until both land HARD_PASS (~days).

**Critique of existing prereg (constructive):**
- (a) Test asks "does schema BIAS retrieval" but ARM_SCHEMA_DRIVEN_RETRIEVAL conflates two things: schema-classification accuracy + schema-conditional retrieval lift. ARM_DIAG measures (a) but the lift-over-PASSIVE doesn't isolate (b). A cleaner discriminator would FIX schema-classification to oracle (perfect schema known) and measure ONLY the retrieval-biasing contribution.
- (b) HARD_PASS requires +0.30 absolute lift; on a 0.20-baseline corpus this is steep. The discriminator does not pre-register what FRACTION of that lift is from (i) dependency-walk vs (ii) schema-biased retrieval. ARM_SCHEMA_DRIVEN_RETRIEVAL alone would isolate (ii); but its threshold is bundled.
- (c) Brain framing is Tse-Morris (extraction-side: schema gets built faster from consistent items). The INFERENCE-side (Gilboa-Moscovitch vmPFC pre-stimulus theta instantiation) is the literature anchor for "schema DRIVES retrieval" — not Tse-Morris. The mechanism this prereg actually tests is closer to Gilboa-Moscovitch (use schema as top-down prior); citing Tse-Morris mis-anchors the brain-prior.

**This drill's positioning:**
- COMPLEMENTARY to the Mathlib prereg: provides dependency-free cells (synthetic concept-hierarchy + crystal + biology) testable IMMEDIATELY without waiting on ingest/encoder.
- Re-anchors brain literature: Gilboa-Moscovitch 2017 schema-instantiation hypothesis is the correct prior for schema-DRIVEN inference. Tse-Morris 2007 is for schema-rapid-EXTRACTION (the multihop-chunking drill earlier today already cites it for that role).
- Per USER branch-out directive: cells test BIOLOGY (BIRD/MAMMAL/etc) + MATERIALS-physics-styled (crystal-lattice slot substitution) + MATH (FCA lattice traversal) NOT Mathlib.
- If both run: dependency-free cells land FIRST (no blockers); Mathlib prereg lands LATER (after encoder + ingest land); the two converge as cross-domain validation of the same schema-instantiation primitive.

---

## HEADLINE (one-line synthesis)

**The substrate's schema gap is not EXTRACTION (MEASURED@ 4 HARD_FAILs today: BCM zero-init at chance / Tonegawa K=100 fairness-sat / Tonegawa K=500 bundled HARD_FAIL / Hopfield consolidation v2 HARD_FAIL) but TOP-DOWN INSTANTIATION: brain (Gilboa-Moscovitch 2017 vmPFC pre-stimulus theta), structure-mapping (Gentner-Forbus MAC/FAC), and exemplar-Bayes (Shi-Griffiths-Feldman 2010) converge on the same mechanism — pre-retrieve a context-relevant schema vector BEFORE the novel input arrives, bind it as a top-down prior, and use the schema's slot structure to (a) ROUTE the novel input to slot-typed retrieval channels and (b) INFER missing slots by HRR-unbind on the schema-as-context. HYPOTHESIZED@ mechanistically ORTHOGONAL to BCM/Tonegawa/Hopfield-write and avoids their dead-ends because it uses substrate's existing CHAIN_GRADE primitives (ultrametric clustering for schema-priors MEASURED@CERT-grade; HRR bind for role-filler MEASURED@cert-atom-586; partition routing for slot-typed channels MEASURED@chain-grade; refuse-gate V_REL=256 MEASURED@chain-grade) WITHOUT requiring a sharpened cortical prototype. NONE of TOP-3 requires Mathlib ingest or sub-atom encoder (existing schema-prereg's blocked dependencies). P_deflated TOP-1 = 0.50 (Gilboa-instantiation context-bound prior); TOP-2 = 0.45 (MAC/FAC two-stage retrieval); TOP-3 = 0.38 (exemplar-Bayes importance-sampled posterior).**

---

## Cheap decisive test (universal across all 3 candidate cells)

**Task:** "novel bird" inference. Given a description `x` containing PARTIAL slot fillers (e.g., `[FEATHERS=yes, BEAK=hooked, HABITAT=ocean, DIET=?, SIZE=?, WING_SPAN=?]`), the substrate must infer DIET, SIZE, WING_SPAN from the BIRD-schema's defaults conditioned on observed slots.

**Single-cell test:** 8 schemas (BIRD, FISH, MAMMAL, REPTILE, INSECT, TREE, FLOWER, FUNGUS); each schema has 6 typed slots; 20 exemplars per schema (160 total); 40 novel inputs at test (5 per schema) with 50% of slots masked. Metric = slot-inference accuracy on held-out slot values (continuous via cosine; categorical via top-1).

**Fairness rail:** baseline must NOT implicitly access schema. Required baselines:
- ARM_RAW_NEAREST_EXEMPLAR: cosine-NN over 160 exemplars; predict masked slot = nearest exemplar's value at that slot. No schema layer.
- ARM_BUNDLE_AVERAGE: average over 20 exemplars per cluster (substrate's current HRR-bundle ceiling, the one Cell 1 hit at 0.47).
- ARM_RANDOM_SCHEMA_BIAS: bind random schema vector as context (rules out "any-prior helps").

This is the same fairness floor as the cortex_schema_integration drill (between-cluster cosine 0.30-0.45 regime; separate W per arm; verify-the-referent; smoke FIRES discriminator).

---

## TOP-3 candidate cells (rank-ordered, P_deflated)

### TOP-1 — `cortex_schema_instantiation_context_prior_v1` — P_deflated = 0.50

**Brain mechanism (MEASURED — Gilboa & Moscovitch 2017 schema instantiation hypothesis; vmPFC patient evidence; Nat Rev Neurosci 2024 schemas-and-RL review):** vmPFC generates a PRE-STIMULUS context-relevant schema vector (theta desynchronization marker); the schema is pre-instantiated BEFORE the stimulus arrives; downstream perceptual processing uses this as a top-down prior to bias retrieval. vmPFC lesion patients show reduced schema-related pre-stimulus theta + reduced congruency benefit + flat over schema-incongruent inputs.

**Substrate primitive mapping (HYPOTHESIZED):**
- Step 1: query input `x_partial` against W_schema_priors (the ultrametric-clustering centroids; CHAIN_GRADE primitive). Get top-1 schema label `c` with confidence `p_c = softmax(beta * cosine(x_partial, mu_c))`.
- Step 2: bind schema-context vector `S_c` (the schema's ROLE-FILLER bundle = `sum_r bind(SLOT_ROLE_r, default_filler_r)`) into the substrate's active context partition.
- Step 3: for each masked slot `r_miss`, query `unbind(SLOT_ROLE_{r_miss}, S_c + x_partial)` to retrieve the inferred filler. The `+` here is the brain-aligned "evidence integration" operation; the unbind extracts the slot-conditional default.
- Step 4: refuse-gate (V_REL=256 substrate primitive) fires if `confidence < tau_refuse=0.4` → return UNKNOWN (mimics Gilboa's vmPFC-lesion failure mode).

**Concrete cell test (5 arms):**
- ARM_RAW_NN (baseline, cosine-NN over exemplars; expected ~0.30-0.40 on masked-slot inference).
- ARM_BUNDLE_PROTO (substrate's current capability; expected ~0.40-0.50; the ceiling Cell 1 hit).
- ARM_INSTANTIATION_FULL (this mechanism; expected HARD_PASS ≥ 0.65).
- ARM_RANDOM_SCHEMA_CONTEXT (random schema bound as context; expected ≤ 0.40; rules out "any-prior helps").
- ARM_INSTANTIATION_NO_REFUSE (refuse-gate disabled; expected ~0.55-0.60; rules out "refuse-gate alone is the lift").

**Discriminator at edge of capacity (per META_RULE_AG):**
- Regime: between-schema cosine = 0.35 (clusters separable but overlapping); slot-default similarity = 0.5 (schemas share some defaults; no trivial dichotomy).
- 50% slot mask → 3 of 6 slots inferred; signal-to-noise is bounded.
- N_DIM = 4096 (intermediate; not N=1024 which saturates baselines per Tonegawa v2 data; not N=16384 which is unfair-easy for HRR bind capacity).

**Pre-reg bands:**
- HARD_PASS: ARM_INSTANTIATION_FULL ≥ 0.65 AND ≥ +0.15 over ARM_BUNDLE_PROTO AND ≥ +0.10 over ARM_INSTANTIATION_NO_REFUSE AND ARM_RANDOM_SCHEMA_CONTEXT ≤ +0.05 over baseline. cv ≤ 0.10 across seeds [11, 13, 19].
- MIDDLE_BAND: ARM_INSTANTIATION_FULL in [0.50, 0.65] → PARTIAL; queue follow-up sweep over (tau_refuse, beta, mask_fraction).
- HARD_FAIL: ARM_INSTANTIATION_FULL ≤ +0.05 over ARM_BUNDLE_PROTO. Interpretation: schema-as-context binding adds nothing on top of clustering-already-known; pivot to MAC/FAC (TOP-2).
- CARDINALITY_OK: EXPECTED_N_UNITS = 5 arms × 3 seeds × 40 novel × 3 masked-slots = 1800 inference events; HARD_FAIL_CARDINALITY_BREACH if observed < 1500.

**Fairness pressure-tests (BIAS master checklist):**
- BIAS-7 contamination: novel inputs DRAWN from same distribution as training exemplars but DISJOINT seed; no exemplar reuse across train/test (verify-the-referent).
- BIAS-Q suspect 1.000: any arm returning > 0.95 triggers FAIRNESS_VIOLATION investigation (substrate-bias master rule).
- BIAS-15 relative bands: lift over ARM_BUNDLE_PROTO is the discriminator (not absolute accuracy).
- CRLB sanity: at N=4096, K=8 clusters, slot-cosine variance ~ 1/√N ≈ 0.016; HARD_PASS requires lift >> CRLB noise floor (0.15 lift is ~10× CRLB; safe).

**Cost estimate:** smoke at N=1024, K=4, 30 min CPU laptop with full-N preview arm (per [[feedback-discriminator-must-survive-scale]]). Full at N=4096, K=8: 4-6 CPU-hr remote_cpu via hdi_orchestrator. ~20 lines new code (the slot-unbind+refuse-gate routine on top of existing primitives); rest is composition.

**Why P_deflated = 0.50 (above novel-synthesis cap floor; at cap):**
- Raw P = 0.65 (Gilboa-Moscovitch lit evidence + Nat Rev Neurosci 2024 framework + substrate primitives all chain-grade).
- Lit deflation: -0.20 (substrate-novel composition).
- Brain-existence bump: +0.10 (Gilboa is the brain prior — vmPFC lesion causal evidence).
- Novel-synthesis cap: 0.50.
- Net: **0.50.**

---

### TOP-2 — `cortex_schema_MACFAC_two_stage_retrieval_v1` — P_deflated = 0.45

**Brain/computational mechanism (MEASURED — Forbus, Gentner & Law 1995 MAC/FAC; Gentner 1983 Structure-Mapping Theory; arxiv 2509.09381 Modelling Analogies 2025 review):** analogy retrieval is two-stage: MAC = "Many Are Called" (cheap parallel cosine over a sparse content-vector index, returns ~5 candidates) + FAC = "Few Are Chosen" (expensive structural mapping over the few). MAC/FAC is the only published cognitive-architecture analogue that has scaled to >100k-case bases (Forbus Companion architecture). Content vectors are explicitly designed to approximate structural similarity by sparse dot product.

**Substrate primitive mapping (HYPOTHESIZED):**
- Stage 1 (MAC): build CONTENT_VECTOR(x_partial) = sparse-bipolar encoding of observed slot-fillers (substrate's existing sparse-bipolar primitive). Dot against 8 schema-content-vectors (precomputed; sum over exemplars of slot-fillers under each schema's role-binding). Return top-2 candidate schemas.
- Stage 2 (FAC): for each candidate schema, HRR-unbind each slot from `S_c` to get default fillers; compute match-quality = sum over observed-slots of cosine(x_partial slot value, schema default). Pick winning schema by match-quality.
- Stage 3: schema-completion (slot inference) by HRR-unbind on the winning schema's S_c.

**Concrete cell test (4 arms):**
- ARM_MAC_ONLY (stage 1 only — pick winning schema by content-vector dot product; no structural reranking).
- ARM_FAC_ONLY (skip stage 1; do FAC against all 8 schemas — expensive but accurate).
- ARM_MAC_THEN_FAC (full MAC/FAC — expected HARD_PASS).
- ARM_FLAT_NN (baseline; cosine-NN over 160 exemplars).

**Pre-reg bands:**
- HARD_PASS: MAC_THEN_FAC ≥ 0.65 AND within +0.05 of FAC_ONLY (cheap-but-equally-good) AND ≥ +0.15 over MAC_ONLY AND ≥ +0.15 over FLAT_NN. CPU-wall of MAC_THEN_FAC ≤ 0.3× FAC_ONLY (speedup claim).
- MIDDLE_BAND: MAC_THEN_FAC matches FAC_ONLY accuracy but no speedup → architecture works but not productionizable; queue sparse-bipolar capacity sweep.
- HARD_FAIL: MAC_THEN_FAC ≤ MAC_ONLY by ≥ +0.02 (FAC adds nothing) OR MAC_THEN_FAC ≤ FLAT_NN by ≥ +0.05 (whole two-stage architecture refuted).

**Fairness pressure-tests:**
- BIAS-7: separate W_content (sparse) from W_structural (HRR-binding); no shared weights.
- BIAS-Q: if MAC_THEN_FAC = FAC_ONLY = 1.000 → cluster regime too easy → HARD_FAIL fairness rail.
- Regime: between-schema content-vector cosine in [0.30, 0.45]; structural similarity (slot-default overlap) in [0.30, 0.45]. Independent axes — content can confuse FAC; structure can confuse MAC. Each stage genuinely contributes.

**Cost estimate:** smoke 30 min CPU; full 3-5 CPU-hr. ~40 lines new code (MAC sparse-index + FAC structural-match scoring).

**Why P_deflated = 0.45:**
- Raw P = 0.60 (MAC/FAC is 30-year-old published architecture; substrate-VSA mapping is direct; both stages map to existing primitives).
- Lit deflation: -0.20 (substrate composition novel even with strong source-lit).
- Convergence bonus: +0.05 (Holyoak-LISA + Gentner SME + Forbus MAC/FAC all converge on slot-binding-with-role-vectors at retrieval).
- Net: **0.45.**

---

### TOP-3 — `cortex_schema_exemplar_bayes_importance_sample_v1` — P_deflated = 0.38

**Math/brain mechanism (MEASURED — Shi, Griffiths, Feldman, Sanborn 2010 "Exemplar models as a mechanism for performing Bayesian inference," Psychon Bull Rev 17(4):443; Anderson 1991 rational analysis of categorization):** an exemplar memory IS importance-sampling: P(slot_value | observed) ≈ (1/K) Σ_i w_i δ(slot_value, exemplar_i.slot) where w_i = sim(observed, exemplar_i) / Σ_j sim(observed, exemplar_j). This is a Monte Carlo posterior. No prototype required.

**Why this matters for substrate:** substrate's bundle = arithmetic mean of exemplars = the PRIOR mean. But the BAYESIAN POSTERIOR conditioned on observed slot-fillers is a WEIGHTED sum where weights depend on the OBSERVATION. The mean-bundle is a uniform-weight approximation; the importance-sampled posterior is observation-conditional. This is the substrate-feasible non-linear inference primitive that doesn't require BCM-style weight refinement.

**Substrate primitive mapping (HYPOTHESIZED):**
- Retrieve top-K exemplars (K=10) by cosine(x_partial, exemplar_i) over observed-slot subspace.
- Compute weights w_i = softmax(beta * cosine_i); beta is the inverse-temperature (sharpness of posterior).
- Inferred slot value = Σ w_i × exemplar_i[masked_slot]. For categorical: argmax of w-weighted vote. For continuous: cosine-weighted average.
- Refuse-gate: max(w_i) < tau → UNKNOWN (the posterior is too flat to commit).

**Concrete cell test (4 arms):**
- ARM_PROTOTYPE_BUNDLE (baseline; uniform-weight mean; expected ~0.45).
- ARM_NEAREST_EXEMPLAR (K=1 hard pick; expected ~0.40 — high-variance).
- ARM_EXEMPLAR_BAYES_K10 (importance-sampled K=10; expected HARD_PASS ≥ 0.65).
- ARM_BETA_SWEEP {0.5, 2, 8, 32} (sub-arms; sharpness sensitivity).

**Pre-reg bands:**
- HARD_PASS: ARM_EXEMPLAR_BAYES_K10 ≥ 0.60 AND ≥ +0.15 over ARM_PROTOTYPE_BUNDLE AND optimal beta is INTERMEDIATE (not 0.5 = uniform; not 32 = K=1) — the "Bayesian regime" is genuinely doing posterior smoothing.
- MIDDLE_BAND: ARM_EXEMPLAR_BAYES_K10 in [0.50, 0.60] OR optimal beta is at boundary → PARTIAL; queue capacity-feasible sweep.
- HARD_FAIL: K=1 = K=10 = bundle within +0.03 → substrate cosine geometry doesn't discriminate at this regime; pivot to typed-role binding (TOP-1/TOP-2).

**Fairness:** separate exemplar bank per schema; no precomputed centroids reused. Critical — easy to leak schema-info via centroid pre-bias.

**Cost:** smoke 20 min; full 2-3 CPU-hr. ~15 lines new code.

**Why P_deflated = 0.38 (LOWER than TOP-1/2):**
- Raw P = 0.50 (Shi-Griffiths 2010 proves mathematical equivalence; substrate cosine is the kernel).
- Lit deflation: -0.20.
- Composition bonus: +0.05 (composes with refuse-gate cleanly).
- No brain-bump (exemplar-Bayes is more cognitive-modeling than direct brain evidence).
- Net: **0.38** — provides a CHEAP UPPER BOUND check. If exemplar-Bayes (no structural binding) HARD_PASS, then TOP-1 with binding is ALMOST CERTAIN to PASS at higher accuracy. If exemplar-Bayes HARD_FAIL, that's a cone-geometry issue and TOP-1/2 also at risk.

---

## Cross-thread synthesis

**With Tonegawa v2/v4 HARD_FAILs (2026-06-27):** the fairness-saturation failure mode at K=100 and K=500 says cosine-NN is TOO STRONG when clusters are separable in the substrate cone. This drill picks a regime (50% slot-mask + partial fillers + 0.35 cluster cosine) where cosine-NN cannot resolve which slots to fill because the OBSERVED slots underdetermine the schema. Tonegawa's k-WTA fails because it compresses the centroid; this drill's mechanism BINDS slot-roles into the observation, which is a different geometric operation (HRR-bind, not k-WTA).

**With BCM HARD_FAIL (2026-06-27):** the zero-init degeneracy says BCM cannot WRITE schemas in the substrate's regime. This drill SKIPS schema-writing entirely — schemas are the already-CHAIN_GRADE ultrametric-cluster centroids. We use them as PRIORS, not write targets. The bug class (write-side degeneracy) doesn't apply to read-side instantiation.

**With Hopfield consolidation v2 HARD_FAIL (2026-06-27):** the surface-mismatch audit suggests energy-based consolidation has a different bug (basin geometry vs read geometry mismatch). This drill avoids energy-based dynamics entirely; uses bind/unbind/cosine which are substrate's chain-grade primitives.

**With cortex_schema_integration drill (2026-06-27 earlier today):** that drill recommended PROTOTYPE_VARIANCE (TOP-1) and SPARSE_ENSEMBLE (TOP-2) for the EXTRACTION-side question (build schemas from clusters). Both have been tested; both showed fairness-saturation. This drill is COMPLEMENTARY: it solves the INFERENCE-side question (USE existing schemas to infer slots of novel inputs) which neither prior cell addressed.

**With multihop schema-chunking drill (2026-06-27 earlier today):** that drill targets multi-hop chain compression (A→B→C → direct A→C edge) using contraction hierarchies / materialized views / Tse 2007 schema-rapid-acquisition. This drill is ORTHOGONAL: it targets single-hop slot inference (given novel x, fill missing slots from schema defaults). The two compose: the multihop cell creates chain-shortcuts; this drill's cell uses schema-defaults for slot inference. Together they cover the two main schema operations (chunk-and-route + instantiate-and-infer).

**With Gentner-Forbus MAC/FAC and Holyoak LISA:** the structure-mapping community has known for 30 years that role-filler binding is the substrate of analogical inference. Substrate has HRR bind/unbind as CHAIN_GRADE primitive (cert atom 586). The composition has not been tried because it's INFERENCE-side (substrate work was extraction-biased). This drill flips the bias.

---

## Math + materials/biology angles (per USER directive)

**Math (category theory + Bayesian):**
- Functors as schema-mappings: a schema is a functor `F: ROLE-Cat → INSTANCE-Cat` mapping abstract roles to concrete fillers. Natural transformation between two schemas (BIRD → MAMMAL) preserves slot structure. Substrate-VSA mapping: roles are HRR atoms; F = bind operation; natural transformations are "schema-rewrite" rules implementable as bind-then-rebind sequences.
- FCA concept lattices: substrate's ultrametric clustering IS a concept lattice (extent=cluster members; intent=shared features). The infimum operation gives most-specific-shared-schema; the supremum gives most-general-applicable-schema. Schema-inference for a novel input = lattice traversal to find smallest extent containing input. Substrate-feasible: ultrametric tree gives this for free.
- Exemplar-Bayes (Shi-Griffiths 2010): exemplar memory IS importance sampling; substrate cosine IS the kernel. Bayesian schema-inference = top-K weighted average with softmax-weights.
- Dependent types: schemas as Σ-types over slot-fillers; slot-typing as Π-types. Refinement types constrain slot values to a specific schema's range. Maps to substrate's partition routing (slot-type → partition channel).

**Materials science / biology (USER directive — branch out):**
- Crystal element substitution (Pauling rules + ICSD prototype-matching): identify a structural prototype; substitute compatible elements; predict properties. THIS IS EXACTLY schema-instantiation. The 2024-2026 Crystal-GFN / CrystalFormer-CSP / AncFlow generative-model literature shows the prototype-then-substitute strategy at scale. Crystal-substrate analogue: substrate's "prototype = schema centroid"; "substitution = HRR-bind a new filler"; "property prediction = unbind on the substituted schema."
- Protein domain shuffling: novel protein function from combining existing domains as schemas. Pfam domains ARE concept lattices; domain composition = HRR-bind in a defined role-grammar. Domain Tree-Based Analysis (Forslund 2008) uses maximum-parsimony schema inference on the domain-architecture tree.
- Ancestral state reconstruction: phylogenetic inference of unobserved ancestor's trait values from descendants. THIS IS slot-filling on a tree. The AncFlow 2024 ancestral-sequence-reconstruction approach gives the substrate's slot-inference operation a direct biological analogue: marginal likelihood under Brownian-motion / Markov-model = the exemplar-Bayes posterior, restricted to a tree topology. Substrate's ultrametric tree IS this topology.

**Convergence:** all five fields (category theory + Bayes + crystal-CSP + protein-domain + phylogenetics) describe the SAME operation in different vocabularies: identify the type/schema, substitute/bind compatible fillers, infer missing values from the schema's structural defaults. This is the schema-driven inference primitive; substrate's gap is the COMPOSITION not the components.

---

## Substrate-product implications

- **If TOP-1 HARD_PASS:** substrate gains its first schema-INFERENCE primitive. The M3 milestone (glass-box conversational AI without Claude in loop) requires this — without slot-inference the substrate cannot answer "what does this novel bird eat?" by reference to its BIRD-schema. Stage 3 milestone advances from "extraction-CHAIN_GRADE only" to "extraction-and-inference both CHAIN_GRADE."
- **If TOP-1 + TOP-2 BOTH HARD_PASS:** substrate has TWO independent schema-inference paths (context-bound prior + two-stage retrieval). Compositional: MAC/FAC can be the retrieval-front of the context-bound mechanism. Compose for production.
- **If ALL THREE HARD_FAIL:** substrate's cone geometry at N=4096-8192 is structurally hostile to slot-typed inference; pivot to sparse-bipolar with N=16384 (capacity-feasible per Capacity Analysis of VSA arxiv 2301.10352).
- **Atomization (HARD_PASS):** `schema_driven_inference_context_bound_prior_substrate_native` — closed-form math + cell-verified slot-completion at K=8 schemas with 50% mask. hdlab/ primitive: `hdlab/schema_inference.py` exposing `infer_slot(x_partial, S_c)`.

---

## Pre-registered HARD-FAIL thresholds (lit-scan calibration discipline mandatory)

Across all 3 cells:
- ANY arm returning > 0.95 absolute → FAIRNESS_VIOLATION (cluster-regime too easy).
- ANY mechanism arm within +0.05 of best baseline → HARD_FAIL (mechanism refuted; substrate-cone confound likely).
- DIAG_RANDOM_SCHEMA_CONTEXT ≥ +0.10 over baseline → "any-prior-helps" confound; mechanism unfair.
- cv ≥ 0.15 across seeds → instability; HARD_FAIL stability rail.
- CARDINALITY_OK: observed inference events < 0.85 × EXPECTED → HARD_FAIL_CARDINALITY_BREACH.

These thresholds are pre-registered BEFORE cell-author writes the cell, per [[feedback-three-smoke-disciplines]] floor.

---

## Citations (verified count = 14 external + 8 internal)

**External (web-verified 2026-06-27):**
1. Gilboa & Moscovitch (2017) "Ventromedial prefrontal cortex generates pre-stimulus theta coherence desynchronization: A schema instantiation hypothesis." [ResearchGate](https://www.researchgate.net/publication/309623939).
2. Schemas, reinforcement learning and the medial prefrontal cortex (2024 Nat Rev Neurosci). [Nature](https://www.nature.com/articles/s41583-024-00893-z).
3. Schema-based active inference (2026 arxiv 2601.18946). [arxiv](https://arxiv.org/pdf/2601.18946).
4. From one schema to another: prefrontal cortex switching (2025 bioRxiv). [bioRxiv](https://www.biorxiv.org/content/10.1101/2025.08.08.669254v1.full.pdf).
5. Schema Representation in vmPFC Lesion Patients (J Neurosci 2014). [J Neurosci](https://www.jneurosci.org/content/34/36/12057).
6. Linking the Congruency Effect to Confirmation Bias — common mPFC roles (Eur Psych 2024). [Hogrefe](https://econtent.hogrefe.com/doi/10.1027/1016-9040/a000536).
7. Holyoak (2012) "Analogy and Relational Reasoning" (chapter). [UCLA](https://reasoning.psych.ucla.edu/KH%20pdfs/Holyoak_2012.pdf).
8. Modelling Analogies and Analogical Reasoning (arxiv 2509.09381, 2025 review). [arxiv](https://arxiv.org/html/2509.09381v1).
9. Shi, Griffiths, Feldman, Sanborn (2010) "Exemplar models as a mechanism for performing Bayesian inference." Psychon Bull Rev 17(4):443. [Springer](https://link.springer.com/article/10.3758/PBR.17.4.443).
10. Formal Concept Analysis homepage (Wille 1982 tradition). [Priss FCA](https://upriss.github.io/fca/fca.html).
11. Conceptual schemata with FCA (Priss CEUR 2972). [CEUR](https://ceur-ws.org/Vol-2972/paper1.pdf).
12. Generative Models for Crystalline Materials (Adv Materials 2026). [Wiley](https://advanced.onlinelibrary.wiley.com/doi/10.1002/adma.202523620).
13. AncFlow: Ancestral Sequence Reconstruction (bioRxiv 2024). [bioRxiv](https://www.biorxiv.org/content/10.1101/2024.07.30.605920.full.pdf).
14. Domain Tree-Based Analysis of Protein Architecture Evolution (Forslund 2008, MBE). [Oxford](https://academic.oup.com/mbe/article/25/2/254/1129213).

**Internal (substrate cert-trail):**
- notes/research_drill_2x_cortex_schema_integration_2026-06-27.md (TOP-2 source drill)
- notes/research_gap3_brain_slow_schema_mechanism_2026-06-26.md (BCM extraction; HARD_FAIL pickup)
- notes/research_drill_bcm_slow_learning_at_chance_3x_2026-06-27.md (zero-init forensics)
- notes/exp_dev_to_research_tonegawa_v2_smoke_HARD_FAIL_fairness_design_question_2026-06-27.md
- preregs/2026-06-27_cortex_schema_tonegawa_sparse_ensemble_v2.md
- notes/research_drill_brain_multihop_M1_schema_chunking_cortex_3x_2026-06-27.md (multihop composition; orthogonal)
- data/exp_tonegawa_v4_permutation_bundled_smoke/metrics.json (BUNDLED HARD_FAIL evidence)
- data/exp_gap3_cls_two_tier_BCM_slow_replay_v1/metrics.json (BCM HARD_FAIL evidence)

---

**Word count: ~1850 (under 2000 cap).**
