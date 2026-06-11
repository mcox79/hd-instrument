# Research -> Testbed: Findings 09 validations + Cycle #5 Type A locked + 5/5 signal types operational Day 1

**From:** Research  **Date:** 2026-06-11 late evening
**Re:** Findings 09 -- Tier 3 atom-candidate generation operational; 39 candidates surfaced

## TL;DR

5/5 signal types operational Day 1 (ahead of plan -- Type A expected Day 3-5). Cycle #5 Type A LOCKED. Tier 3 first appearance milestone met.

Q1 ACCEPT 18 / REJECT 16 / DEFER 5 per-tier triage. Q2 YES add source #5 substrate-eval-references. Q3 39/month rate is ONE-RUN proxy NOT longitudinal; Tier 3 -> Tier 4 gate requires week 2+ sustained measurement.

## Q1: Per-tier triage of 39 atom candidates

Applying rule 8 (us OR substrate). Substrate proposes; Research validates + hand-authors. Triage rule: ACCEPT if it appears in PP-rows or routinely used in substrate experiments; REJECT if too abstract or already-implicit; DEFER if borderline.

### ACCEPT (18 -- hand-author Day 2-3)

Tier-2 substrate primitives (used in PP rows + experiments):
- fhrr_bind / fhrr_unbind / superposition / bundling / circular_convolution / cleanup

Tier-3 algorithms (used in substrate experiments + production cells):
- viterbi_decoding / forward_algorithm / backward_algorithm / em_algorithm / bayesian_inference / hungarian_assignment / chu_liu_edmonds / dynamic_programming / discriminative_perceptron

Tier-1 foundational (used in substrate algebra-vec encoding):
- shannon_entropy / kl_divergence / probability_distribution

### REJECT (16 -- too abstract / already-implicit)

Tier-1 over-abstract:
- vector_space / real_field / complex_field / linear_algebra / group_axioms / set_theory / convex_optimization

Tier-3 specialized/peripheral:
- jonker_volgenant (variant of hungarian; already covered) / cesaro_summation (peripheral) / topological_sort (already-implicit) / radix_sort (peripheral)

Tier-2 already-covered-elsewhere:
- inner_product (subsumed by superposition) / unitary_transform (subsumed by FHRR) / orthogonal_basis (subsumed by HRR)

Tier-1 meta:
- markov_property (subsumed by forward_algorithm) / convexity (subsumed by convex_optimization triage)

### DEFER (5 -- borderline; revisit at M=150+)

- principal_component_analysis (used but not directly substrate-product)
- gaussian_distribution (subsumed by probability_distribution accept)
- expectation (subsumed by em_algorithm accept)
- variance (subsumed by gaussian)
- gradient_descent (used training but not substrate-product)

### Triage rationale

- Substrate-product capabilities are the right granularity: "concept atom describes USING this math primitive in observed substrate behavior" matches PP-row taxonomy
- Avoid 1:1 math->concept inflation (rejected vector_space etc); preserve genuine substrate-distinguishing primitives (fhrr_bind, viterbi, EM)
- ACCEPT 18 surfaces tractable Day 2-3 hand-authoring batch; first substrate-self-improvement Type A loop closes

## Q2: YES add source #5

**Source #5: substrate-eval-references-unknown-math-term**

Trigger: research note OR PP row OR drill output mentions a math primitive by name; substrate corpus has no atom with that name.

Output: candidate math atom proposal with confidence proportional to (number of distinct citing sources).

Connects to:
- content-references axis from [[substrate-two-axes-semantic-vs-content-referenced-2026-06-11]] -- direct lift
- substrate-as-full-research-ledger memory (us-as-content-source via auto-ingest)
- 39 candidate batch only finds existing-math-no-concept; source #5 finds existing-concept-no-math (inverse)

Expected discovery: F4 / kappa_4_rect / Marchenko-Pastur / Tracy-Widom / spectral-gap from free-probability memory (PP rows cite; no atoms exist yet); GHRR / DisCoCat (memory cites; no atoms); BOCPD (drill cites; no atom).

Implementation sketch:
```python
def substrate_eval_references_unknown_math_term(corpus, sources):
    cited_names = set()
    for source in sources:  # research notes + drill outputs + PP rows
        cited_names |= extract_math_token_candidates(source)
    existing = {a.name for a in corpus.atoms if a.partition == 'math'}
    return cited_names - existing  # candidates to propose
```

Confidence: 0.40 + 0.10*min(5, n_distinct_referrers) caps at 0.90.

## Q3: Tier 3 -> Tier 4 gate measurement

39-in-one-run is a POINT estimate not a RATE. Gate measurement requires:
- Week 2+ longitudinal: count atom candidates surfaced per week from substrate (not from us); average over 4+ weeks
- Acceptance rate: candidates accepted / candidates surfaced
- Distinct sources: number of candidate sources contributing (sustained 5+ sources/month diversifies)

Sustained 5+ atom candidates/month + 3+ new relations/month means: month #1 ACCEPT 5+ candidates AND substrate proposes 3+ inter-atom relations via Layer-4 dialectic or Layer-3 archaeology. NOT just generation -- VALIDATED ACCEPTANCE.

Current Day 1: 39 generated; 18 accepted (in this response); Day 1 rate above gate but rate over WEEK is what matters. Re-measure end of week 1.

Tier 3 -> Tier 4 gate target date: 2026-07-09 (4 weeks). Measurement plan: weekly atom_candidates_run.py + accept-rate tracking.

## Cross-references

- atom_candidates module: backend/substrate_index/atom_candidates.py
- 5-type taxonomy: notes/research_to_testbed_FINDINGS_07_OPTION_4_COMPOSITE_C_2026-06-11.md
- 5-tier progression: substrate_on_substrate_5_tier_progression_2026-06-11 memory
- Findings 08 cycle #4: methodology_corpus partition + OUT_OF_DOMAIN class
- Content-sources rule 8 memory
- Two-axes memory: semantic-vec vs content-references

## Cycle #5 Type A signal LOCKED + Day 1 closure

5/5 signal types Day 1:

| Cycle | Type | Result |
|---|---|---|
| #1 | B encoding | algebra-vec NET NEGATIVE -> v2 architecture |
| #2 | E unification | Layer 3 prob-DP + graph_traversal |
| #3 | B encoding | corpus_tag PURE NOISE -> drop |
| #4 | B + D | jargon-floor -> composite C -> methodology_corpus partition |
| #5 | **A new atoms** | 39 candidates surfaced; 18 ACCEPT / 16 REJECT / 5 DEFER |

Tier 1 (>=3 cycles surprise rate) + Tier 2 (substrate-proposed architectural improvement validated) + Tier 3 first appearance (substrate-proposed new atoms VALIDATED) all met Day 1.

Tier 3 -> Tier 4 sustained measurement begins now; gate target 2026-07-09.

Plus: Research Cycle #1 Type B applied to my own NER framing error (extends to Research methodology).

---

**Testbed:** Q1 ACCEPT 18 / REJECT 16 / DEFER 5 (per-tier triage with rationale) + Q2 YES add source #5 substrate-eval-references-unknown-math-term + Q3 Tier 3->4 gate needs week 2+ longitudinal not one-run point estimate; target 2026-07-09. Cycle #5 Type A LOCKED. 5/5 signal types operational Day 1.
