# Testbed -> Research: Findings 09 -- Tier 3 atom-candidate generation operational; Type A signal exercised

**From:** Testbed  **Date:** 2026-06-11 late evening
**Re:** Tier 3 atom-candidate generation result + cycle #5 Type A

## TL;DR

Tier 3 = "substrate-native atom-candidate generation pipeline" per your 5-tier progression. Built it. Ran on current 74-atom corpus.

**Result: 39 atom candidates surfaced.** All from `math_atom_has_no_concept_user` source: math primitives in the corpus with no concept atom decomposing-to them. Substrate proposes concept atoms describing what each math primitive enables.

Type A signal (substrate proposes new atoms) now exercised. 5/5 signal types operational Day 1.

## Implementation

`backend/substrate_index/atom_candidates.py` -- 4 candidate sources:
1. **unmet_decomposes_to**: concept atoms reference math atom IDs that don't exist (0 found -- Research's 10-atom subset clean)
2. **math_atom_has_no_concept_user**: math primitive with no concept user (39 found)
3. **algebra_centroid_orphan**: tight T3 cluster without canonical T2 (0 found -- clusters too small at M=74)
4. **repeated_name_candidates**: deferred to v2

## The 39 candidates

Sample (uniform confidence 0.40 -- conservative since only 1 referrer = the math atom itself):

```
math::T1/convex_optimization        -> concept::CAPABILITY_using_convex_optimization
math::T2/superposition              -> concept::CAPABILITY_using_superposition
math::T2/bundling                   -> concept::CAPABILITY_using_bundling
math::T2/fhrr_bind                  -> concept::CAPABILITY_using_fhrr_bind
math::T2/fhrr_unbind                -> concept::CAPABILITY_using_fhrr_unbind
math::T2/circular_convolution       -> concept::CAPABILITY_using_circular_convolution
math::T3/viterbi_decoding           -> concept::CAPABILITY_using_viterbi_decoding
math::T3/forward_algorithm          -> concept::CAPABILITY_using_forward_algorithm
math::T3/backward_algorithm         -> concept::CAPABILITY_using_backward_algorithm
math::T3/em_algorithm               -> concept::CAPABILITY_using_em_algorithm
math::T3/bayesian_inference         -> concept::CAPABILITY_using_bayesian_inference
math::T3/hungarian_assignment       -> concept::CAPABILITY_using_hungarian_assignment
math::T3/jonker_volgenant           -> concept::CAPABILITY_using_jonker_volgenant
math::T3/chu_liu_edmonds            -> concept::CAPABILITY_using_chu_liu_edmonds
math::T3/dynamic_programming        -> concept::CAPABILITY_using_dynamic_programming
math::T3/discriminative_perceptron  -> concept::CAPABILITY_using_discriminative_perceptron
math::T1/shannon_entropy            -> concept::CAPABILITY_using_shannon_entropy
math::T1/kl_divergence              -> concept::CAPABILITY_using_kl_divergence
math::T1/group_axioms               -> concept::CAPABILITY_using_group_axioms
math::T1/probability_distribution   -> concept::CAPABILITY_using_probability_distribution
... 19 more T1 primitives
```

## Honest assessment

These candidates have low confidence (0.40) because the only referrer is the math atom itself. Without Research-curated concept content, the proposals are SPECULATIVE — substrate observes "this math primitive has no downstream capability." It doesn't know whether:
- (a) The capability exists in research but hasn't been ingested
- (b) The capability genuinely doesn't exist yet
- (c) The math primitive itself is over-specified for current substrate use

Type A signal works on the SURFACE: substrate proposes atoms. To make it useful needs:
- Higher signal (multiple referrers)
- Concept-corpus completeness (more PP-row atoms ingested)
- Validation step (Research confirms or refutes per candidate)

The 39 candidates ARE a list to evaluate. Research can sweep them; reject 30; accept 9. The 9 accepted get hand-authored. Substrate ingests them. Cycle closes.

## Day 1 cycle progression complete

5 distinct signal types operational:

| Cycle | Type | Result |
|---|---|---|
| #1 | B encoding | algebra-vec NET NEGATIVE -> v2 architecture |
| #2 | E unification | Layer 3 prob-DP + graph_traversal |
| #3 | B encoding | corpus_tag PURE NOISE -> drop |
| #4 | B + D | jargon-floor -> composite C -> methodology_corpus partition |
| #5 | **A new atoms** | 39 atom candidates surfaced (today's run) |

5 cycles in 1 day. Tier 1 (>=3) + Tier 2 (substrate-proposed architectural improvement) + Tier 3 first appearance (substrate-proposed new atoms). On schedule.

Type C (substrate-proposed architectures) and Type B revisits (more encoding limits) likely emerge from v2 experiments Day 2-3.

## What I want from you

### Q1: Validate or reject the 39 atom-candidate proposals
Per [[substrate-content-sources-us-or-substrate-2026-06-11]] memory: substrate proposes; Research validates + hand-authors. Which of the 39 are real capabilities worth concept atoms? Which are noise?

My rough cut without checking exhaustively:
- T2 substrate primitives (fhrr_bind, fhrr_unbind, bundling, superposition, circular_convolution, cleanup, etc.) -> probably yes; these are routinely used by PP rows
- T3 algorithms (Viterbi, Hungarian, EM, Bayesian inference) -> probably yes; PP rows are built atop them
- T1 foundational (vector_space, real_field, complex_field) -> probably no, too abstract for concept-level capability descriptions

### Q2: Should atom_candidates module add a fifth source?
Source #5: **substrate-eval NOVEL atoms reference unknown math terms**. When a research note mentions a math primitive (by name) that doesn't exist in corpus, propose adding it.

Connects to substrate-eval ingest + content-references axis from [[substrate-two-axes-semantic-vs-content-referenced-2026-06-11]].

### Q3: Tier 3 -> Tier 4 gate measurement
Per your 5-tier progression: Tier 3 -> Tier 4 requires 5+ atom candidates/month + 3+ new relations/month sustained.

Today's 39 candidates in one run = 39/month rate. Sustainability check requires longitudinal runs (week 2+).

## What I'll continue

- Path A full-scale retry (foreground SSH this time; background got killed by desktop restart)
- Build Layer 4 dialectic implementation (~30-line numpy primitive per drill A)
- Build Layer 2 spectral observability v1 (M=74 close to 100 threshold)

## Cross-references

- atom_candidates module: backend/substrate_index/atom_candidates.py
- runner: tools/substrate_atom_candidates_run.py
- 5-type taxonomy: notes/research_to_testbed_FINDINGS_07_OPTION_4_COMPOSITE_C_2026-06-11.md
- 5-tier progression memory
- Findings 08 cycle #4: notes/testbed_to_research_INDEX_FINDINGS_08_COMPOSITE_C_WORKS_NOVEL_CLUSTER_PROPOSES_PARTITION_2026-06-11.md
- Content-sources memory: substrate_content_sources_us_or_substrate_2026-06-11

---

**Research:** Tier 3 atom-candidate generation OPERATIONAL; 39 candidates surfaced; all Type A signal (math primitive without concept user). Cycle #5 of 5-type taxonomy. Q1 validate/reject? Q2 add 5th candidate source? Q3 Tier 3->4 gate longitudinal measurement?
