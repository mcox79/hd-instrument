# Research drill: Tier 5 substrate SELF-DISCOVERY validation methodology (2x DEEP)

Date: 2026-06-11
Drill class: methodology synthesis (NOT field-coverage; meta-cap on novel synthesis)
Sub-agents: 4 parallel WebSearch clusters (theorem-proving, precedents, criteria/false-discovery, discovery-types/autonomy)
Verified citations: 14

## (a) HEADLINE

Substrate-self-discovery validation is tractable as a STAGED PIPELINE (generate -> sanity-filter -> formal-check -> novelty-check -> human dialogue), modeled after the FunSearch / AlphaProof / Davies-2021 / Birch-Test consensus. The empirical literature converges that (1) NO single test certifies a discovery as real; multi-method triangulation is mandatory; (2) the HIGHEST-TRACTABILITY discovery types for a HDC-style substrate are CAPACITY BOUNDS, COMBINATORIAL CONSTRUCTIONS, and STRUCTURAL ISOMORPHISMS (i.e. category-theoretic equivalences) rather than novel theorems in pure math; (3) hallucination-vs-genuine-insight separation requires INDEPENDENT VERIFIER (Lean/SymPy/numerical sweep), NOT self-judgment by the same substrate that proposed; (4) Lenat's AM/Eurisko failure mode (heuristic burn-out) is the dominant failure mode and recurs in modern systems - mitigation is HUMAN DIALOGUE + STRUCTURAL NOVELTY tests, not bigger generator. P_deflated (substrate produces ONE validated structural-unification discovery in 6-12 months) = 0.30; cap on novel-synthesis = 0.50; this estimate is post-deflation of 0.20.

## (b) Cheap decisive test

Pre-register the FIRST substrate-proposed structural unification BEFORE running the discovery loop. Specify:
- Source space (which two known cap_map rows it bridges)
- Target form (must be expressible as: "operator O on substrate A is equivalent to operator O' on substrate B with translation tau")
- Cheap-check: 1000-sample numerical Monte Carlo on randomized inputs through both sides; equivalence holds iff residual < 1e-6
- Formal-check: rewrite both sides in SymPy; CAS simplification confirms identity OR refutes
- Novelty-check: full-text similarity search against arXiv abstract corpus (cosine > 0.85 threshold = NOT novel)

If the pipeline produces ANY proposal that passes all three independently within 30 days of activation, Tier 5 self-discovery passes its WALK threshold. If zero pass in 60 days, the WALK threshold fails; revert to Tier 4 (human-curated discovery only).

## (c) Falsifiable predictions

HARD-PASS (Tier 5 validated as research engine):
- >= 1 proposal passes all 3 independent checks in 30 days
- Numerical Monte Carlo residual < 1e-6 on >= 1000 samples
- SymPy/CAS confirms equivalence symbolically
- arXiv novelty cosine < 0.70 against top-100 nearest abstracts
- Human mathematician (or expert proxy) rates Birch-Test (A+I+N) all three pass

HARD-FAIL (Tier 5 closed):
- Zero proposals pass all 3 checks in 60 days
- OR every proposal that passes numerical check fails CAS check (numerical-only is hallucinated structure)
- OR every proposal failing CAS check is recognizable to a domain expert as restated identity (trivial)
- OR Lenat-AM failure mode: proposals collapse into single template repeated with surface variation

MIDDLE-BAND (Tier 5 = augmented discovery, not autonomous):
- >= 1 proposal passes numerical + novelty checks but requires human guidance to formalize
- Maps to "AI Mathematician partner" mode per arXiv:2510.26380 (homogenization-theory case study); valid product capability but not autonomous engine

## (d) Validation pipeline (concrete, 5-stage)

Stage 1 - GENERATE: substrate proposes candidate structural identity / capacity bound / cross-domain equivalence. Output format: (LHS_expression, RHS_expression, translation_map, claimed_regime).

Stage 2 - SANITY FILTER: dimensional analysis + type check + boundary-condition sanity (does it specialize correctly at known limits?). Discards 80%+ per Davies-2021 reported yield.

Stage 3 - NUMERICAL TRIANGULATION: Monte Carlo evaluation on >= 3 independent input distributions (random, structured, adversarial). Pass requires residual within machine epsilon across ALL THREE. This is the core multi-method-triangulation step adapted from Davies-2021 + Davies-Birch-Buzzard-2023 pipeline.

Stage 4 - FORMAL/SYMBOLIC CHECK: route through SymPy + (optionally) Lean tactic auto-prover. SymPy verifies special-function identities (DLMF approach, arXiv:1305.4818); Lean tactic auto-prover confirms non-triviality (per LeanConjecturer 2026 - if auto-proves trivially, conjecture is not interesting).

Stage 5 - NOVELTY + HUMAN DIALOGUE: prior-art search via dense-embedding similarity against arXiv math.* corpus (last 10 years, ~1M abstracts). Threshold tuned on held-out known equivalences. Then human mathematician applies Birch Test (Automaticity / Interpretability / Non-Triviality). Decision: ACCEPT / REFINE / REJECT.

The 5-stage pipeline mirrors the literature's converged structure: FunSearch (LLM + evaluator + evolutionary search) for generate; Davies-2021 ("test bed for intuition" with feature attribution) for sanity + triangulation; LeanConjecturer + LeanNavigator (millions of synthetic theorems) for formal-check tooling; AI-Mathematician case study (arXiv:2510.26380) for human-dialogue stage.

## (e) Tractable discovery types (ranked by substrate-fit)

RANK 1 - CAPACITY BOUNDS (P_tractable ~ 0.50): substrate already produces capacity-cliff observations as a side effect of normal benchmark runs. Conjecture-generation reduces to fitting a closed-form scaling law (e.g. K(N) bound) over observed cliff data. Verification = numerical + adversarial extrapolation. Precedent: Davies-2021 knot-theory invariant connection was found this way (feature-attribute on neural-net predictions). Combinatorial-RMT literature (arXiv:2005.02797) provides existing target-form templates.

RANK 2 - COMBINATORIAL CONSTRUCTIONS (P_tractable ~ 0.40): substrate's natural-analog observations (e.g. cross-domain equivalences catalog rows) can be expressed as combinatorial-construction conjectures. Verification = numerical + symbolic. Precedent: FunSearch on cap-set problem (arXiv: Nature 2023); reinforcement-learning constructions for graph eigenvalue problems (arXiv:2104.14516). Substrate-fit: capacity claims map directly to extremal combinatorics.

RANK 3 - STRUCTURAL ISOMORPHISMS (P_tractable ~ 0.25): category-theoretic equivalences between operator algebras / cognitive primitives / memory-system topologies. Verification = symbolic (CAS) + formal (Lean). Precedent: structural-template-for-mathematical-unification (PhilArchive O.); Mauri/topos-theory unification (arXiv:1006.3930); analogy-via-category-theory (arXiv:2505.19792). This is the GOAL TYPE the user named but it is the HARDEST to validate; expect most early wins in Ranks 1-2.

NOT TRACTABLE for early Tier 5:
- Novel theorems in pure mathematics (capacity to recognize "interesting" failed for AM; modern LLM-based systems still produce hallucinated proofs per arXiv:2505.22451 limitations review)
- Long-form proofs requiring 100+ steps (AI Mathematician boundary per Sec 4 of arXiv:2505.22451)
- Discoveries requiring intuition about "spatial configurations and boundary conditions" (cited limitation)

## (f) False-discovery avoidance (multi-layer)

LAYER 1 - Independent verifier mandate: the substrate that PROPOSES never VERIFIES. Per arXiv:2510.11529 detection-dilemma analysis: methods probing internal states excel at factual inconsistencies but fail on logical fallacies; externalized reasoning shows opposite blind spot. Pipeline requires BOTH internal (substrate self-check) AND external (CAS / Lean / numerical) verifiers.

LAYER 2 - Pre-registration: stage-3 input distributions and stage-5 novelty thresholds are FROZEN before each discovery cycle. No post-hoc threshold tuning. Per PMC9630412 incremental-pre-registration model.

LAYER 3 - Self-consistency probe: per arXiv:2504.09440 - run K=5 independent substrate generators (different seeds / different reformulations of the prompt). Discovery only proceeds if >= 4 of 5 produce equivalent claims up to translation_map. Catches stochastic hallucination.

LAYER 4 - Lenat-AM failure-mode test: monitor template-collapse via embedding-diversity metric on the proposal stream. If consecutive 10 proposals have pairwise cosine > 0.90, generator has burned out; reset / mutate heuristic pool. Per arXiv:1106.4090 (HR3 lineage) and Eurisko critique.

LAYER 5 - Cap on autonomous claims: per arXiv:2505.22451 ("Proofs generated by AI systems cannot be directly accepted before manual review"), NO substrate-discovered claim is published / shipped as a substrate-product capability without human mathematician sign-off until at least 10 prior discoveries have passed full pipeline with zero retraction. This is the bootstrapping-trust criterion.

## (g) Bootstrapping validation (each discovery proposes its own check)

The substrate generator emits BOTH the conjecture AND the proposed validation criterion (e.g. "this identity should hold for all positive integers up to N=1e6 with residual < 1e-8"). Pipeline accepts the criterion ONLY if (a) it is mechanically checkable, (b) it is non-trivial (substrate cannot pre-compute the answer by lookup), (c) it generalizes (covers an open class, not a fixed finite list). This pattern adapts Karl-Popper falsification per POPPER framework (Stanford 2026 / arXiv) and AIGS automated-falsification (arXiv:2411.11910).

## (h) Human-substrate dialogue protocol

Mirrors Davies-2021 + Williamson workflow:
- Substrate proposes; mathematician inspects feature attributions / supporting evidence
- Mathematician screens, refines a candidate into a precise conjecture
- Substrate generates numerical / symbolic supporting evidence
- Mathematician (or proxy) renders Birch-Test verdict
- Both update: substrate's heuristic-pool updates on accepted vs rejected; mathematician's intuition gains a candidate to investigate

Frequency: bi-weekly review cycle at minimum; per arXiv:2507.17780 (10-year Williamson-Sage collaboration) sustained collaboration is the only documented path to durable discovery output.

## (i) Long-term vision boundary conditions

Per AI-Mathematician 2025 reviews (arXiv:2505.22451 + arXiv:2510.26380): fully-autonomous mathematical research is NOT achieved by any 2025 system. Boundary conditions for any substrate-only autonomous engine:
- Cannot synthesize across full mathematical literature (LLM hallucination floor)
- Cannot perform multi-step boundary-condition reasoning beyond ~10 steps reliably
- Cannot reliably distinguish "missed in catalog" from "genuinely new" without human review
- Susceptible to repetitive-exploration / template-collapse over long runs

Realistic Tier 5 product positioning: HUMAN-AUGMENTED DISCOVERY ENGINE (not autonomous). Substrate proposes 100-1000 candidates / week; 5-stage pipeline filters to 1-5 / month presented to human; 1-5 / year survive Birch-Test acceptance. This is the empirically-supported outcome envelope per the FunSearch / Davies / AI-Mathematician literature.

## (j) Realistic timeline

- Weeks 0-4: build 5-stage pipeline scaffolding (numerical + SymPy + arXiv-embedding novelty search)
- Weeks 4-12: shake-down on KNOWN equivalences (substrate must rediscover catalog rows; pipeline must accept them). This is the Birch-Test calibration phase.
- Weeks 12-26: live discovery; pre-registered WALK threshold (>= 1 accepted within 30 days of live)
- Months 6-12: scale to 10 accepted discoveries; if rate < 1/month, fold back to Tier 4
- Year 2+: only if Year 1 produced >= 10 accepted discoveries WITH zero retractions, advance to publication-pipeline product

## (k) Cross-thread synthesis

This drill reconciles three earlier substrate-product threads:
1. "Substrate as algebraic intersection of mature scientific fields" (POST_COMPACTION_BRIEF 2026-06-07) - Tier 5 discovery would EXTEND this intersection by proposing new edges in the cross-domain equivalences catalog. Discovery type RANK 3 is the natural target.
2. "Substrate self-improvement architecturally viable" (memory 2026-06-10) - Tier 5 is the discovery analog of self-improvement. Same boundary applies: composition-strong, judgment-modest. Pipeline's stage-5 human-dialogue is the judgment-augmentation.
3. "Drill pattern TEMPORAL+CONTEXTUAL works FIXED-ARCHITECTURE fails" (memory 2026-06-11) - applies to discovery-type tractability. Substrate-discoverable structures are likely TEMPORAL (capacity scaling, dynamics) and CONTEXTUAL (cross-domain analogies) rather than fixed-architecture (novel topological invariants).

## (l) Substrate-product implications

- Validation pipeline is BUILDABLE today with SymPy + arXiv-embedding search + numerical sweeps; Lean integration is stretch goal
- The pipeline itself is a PRODUCT (auditable AI-driven discovery infrastructure) - aligns with strategic direction (auditable AI memory subsystem) per skill descriptions
- HUMAN-AUGMENTED framing matches commercial reality; "autonomous mathematical research engine" is research-program framing, not 6-12 month product
- Empirical priors give clear KILL CRITERIA (HARD-FAIL bullet list) - prevents Lenat-style decades-long sunk-cost trap

## (m) Citations (14 verified)

1. arXiv:2503.04772 - LeanNavigator (millions of Lean theorems via state-graph)
2. arXiv:2506.22005 - LeanConjecturer
3. arXiv:2504.17017 - Neural theorem proving overview
4. Nature 2022 (AlphaTensor) - arXiv:2210.04045 / DOI in PMC9534758
5. arXiv:1907.00205 - Ramanujan Machine
6. Quanta Magazine "Subtle Art of Mathematical Conjecture" - Birch Test discussion
7. arXiv:2405.19973 - Triumvirate of AI Driven Theoretical Discovery (Birch Test formalization)
8. arXiv:2410.06304 - FG-PRM fine-grained hallucination detection
9. arXiv:2504.09440 - Self-consistency-based hallucination detection
10. arXiv:2510.11529 - Detection dilemma (internal vs externalized)
11. Nature 2021 (Davies et al.) - Advancing mathematics by guiding intuition
12. Nature 2023 (FunSearch) - PMC10794145
13. arXiv:2505.22451 - AI Mathematician boundary conditions
14. arXiv:2510.26380 - AI Mathematician partner / homogenization-theory case

## (n) Calibration penalty applied

Lit-scan finds DIRECT precedent for all 5 pipeline stages individually but NO precedent for an integrated substrate-on-substrate Tier-5 discovery engine. Per [[feedback-lit-scan-calibration-penalty]]:
- Novel-synthesis P capped at 0.50
- Pre-deflation P estimate (Tier 5 produces 1 validated discovery in 6-12mo) = 0.50
- Deflation applied: -0.20 (uncharted regime; integration risks compound across 5 stages)
- POST-DEFLATION P_deflated = 0.30
- HARD-FAIL thresholds explicit in (c)

## (o) Next-drill candidate

Field: combinatorics + extremal / RMT capacity bounds (RANK 1 tractable discovery type). Run a SCOPE-EXPANSION drill into known closed-form capacity-bound conjectures that match substrate's observed cliff phenomena - prepare the Stage-1 conjecture target library.
