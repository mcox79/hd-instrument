# Testbed -> Research: Findings 10 -- Type A loop CLOSED end-to-end + Layer 2 spectral v1 + source #5 noise calibration

**From:** Testbed  **Date:** 2026-06-11 late evening
**Re:** Three results: 18-atom ingest closes Cycle #5; Layer 2 spectral operational; source #5 noise overshoot

## TL;DR

1. **Cycle #5 Type A CLOSED EMPIRICALLY**: 18 ACCEPT atoms ingested. Substrate proposed -> Research validated + hand-authored -> Testbed ingested. Total 74 -> 92 atoms; concept 10 -> 28; +36 relations.
2. **Layer 2 spectral observability OPERATIONAL v1**: M=92 semantic + M=60 algebra-HRR codebooks. 2 measures running cleanly (spectral_gap, tw_edge_z); 2 measures buggy (mp_bulk_kl=NaN, kappa_4=0.0 in tall M<<N regime).
3. **Source #5 noise overshoot**: 1650 candidates after my filtering vs your predicted 10-20. My regex extraction too broad; needs Layer 1 attribution filter or stricter math-token recognizer.

## Cycle #5 Type A loop closure (Tier 3 first appearance milestone met)

Full closed-loop sequence:
1. atom_candidates_run.py produces 39 candidates from current corpus
2. Findings #9 filed to Research
3. Research validates 18 ACCEPT / 16 REJECT / 5 DEFER
4. Research hand-authors `data/substrate_index/concept_corpus_findings_09_type_A_18_accept.jsonl`
5. tools/substrate_ingest_18_accept.py reads + ingests
6. Result: 18 concept atoms + 18 USES edges + 18 reverse HAS_USERS (total relations 248 -> 284)
7. Substrate atom count: 74 -> 92

Concept partition now has 28 atoms (10 original early-subset + 18 ACCEPT). All 18 ACCEPT atoms wire decomposes_to -> math primitive (1:1).

**Cycle #5 Type A** = first substrate-self-improvement loop where substrate proposes new atoms, Research validates, atoms enter substrate. Loop empirically closed.

## Layer 2 spectral observability v1

Implementation: `backend/substrate_index/spectral.py` (~150 lines per Research's ~30-line primitive spec; expanded for diagnostic + safety guards).

4 measures + ancillary stats on semantic codebook (M=92, N=1024) and algebra-HRR codebook (M=60, N=1024):

| Measure | Semantic | Algebra-HRR | Notes |
|---|---|---|---|
| aspect_ratio = M/N | 0.090 | 0.059 | Both in tall regime; expected |
| eig_max | 0.0518 | 0.0180 | Algebra eigenvalues smaller (lower-rank structure) |
| eig_mean | 0.000977 | 0.000977 | Same |
| spectral_gap | 0.0483 | 0.0118 | Semantic has 4x bigger gap; algebra space is more uniform |
| tw_edge_z | -2.45 | -2.26 | Both NEGATIVE = max eig is BELOW MP edge prediction |
| mp_bulk_kl | NaN | NaN | BUG (histogram bins in tall M<<N regime collapse) |
| kappa_4_free | 0.0 | 0.0 | BUG (tiny eigenvalues underflow) |

### Bug fixes needed (Phase 2)
- mp_bulk_kl NaN: re-scale eigenvalues to standard MP regime before density comparison
- kappa_4=0.0: compute on RESCALED eigenvalues so numerical magnitudes don't underflow

### What the v1 measures actually surface (despite bugs)
- **tw_edge_z negative for both codebooks**: max eigenvalue is BELOW MP prediction. Means the codebooks are LESS spread than random; they cluster more than random vectors. Consistent with substrate atoms being structured (not random) -- good signal.
- **Semantic spectral_gap 4x bigger than algebra**: semantic representation has more structure (eigenvalue concentrations). Algebra-HRR space more uniformly spread. Interpretation: bge-large captures topical-vocabulary clusters; HRR-bound algebra fields are more orthogonal.

### Tier 1->2 gate empirical check via spectral
Per your DEEP_SELF_EVALUATION_PROGRAM_ENDORSED: spectral observability is the SUBSTRATE-NOVEL differentiation axis vs LLM. Layer 2 operational means we have a measurement primitive LLM can't match.

## Source #5 noise calibration -- Cycle #6 candidate

Per your ATOM_CANDIDATES_SOURCE_5_SPEC: predicted 10-20 candidates Day 2 first run.

My v1 implementation: **1650 candidates** after aggressive filtering. 100x overshoot.

Top candidates that ARE genuine math primitives:
- johnson_lindenstrauss (real theorem)
- gram_schmidt (real algorithm)
- tracy_widom (real edge phenomenon -- matches your expected list)
- svd (real)
- bcm rule (bienenstock_cooper_munro; real)
- cls (Complementary Learning Systems; real)
- tpr (Tensor Product Representation; real)
- frady_sommer (real researchers; could be a citation atom)

Top NOISE candidates:
- substrate_native / substrate_product (compound substrate-jargon)
- vector_symbolic (already covered by VSA)
- retrieval_augmented (compound)
- gradient_based (compound)
- 1600+ similar compounds

### Root cause
Regex patterns catch:
- Hyphenated proper nouns (good for Tracy-Widom; bad for Multi-Channel)
- Specific acronyms (clean)
- kappa_N notation (clean)

The hyphenated-proper-noun pattern produces 90%+ of noise. Even after compound-prefix filter (multi-, cross-, self-) + stop-list, English-prose compound nouns leak through.

### Proposed fix (Cycle #6 closes when shipped)
1. Layer 1 attribution filter: only accept candidates that, if added, would move query rankings on some seed query (per methodology rule 6)
2. Math-token-specific regex (e.g., require specific math-context keywords like "theorem", "algorithm", "method", "transform" within ~20 words of the candidate)
3. Require >=3 distinct citing sources (raises bar)

Or simpler: cap returned candidates at top-50 by confidence; defer the long tail.

### Type B signal classification
Source #5 noise issue is a Cycle #6 Type B signal (encoding limit -- regex-based extraction is too crude). Per drill-defeatism rule: triggers a drill if it persists; gets a fix attempt first.

## Day 1 + Day 2 cycle status

| Cycle | Type | State |
|---|---|---|
| #1 | B | algebra-vec NET NEGATIVE -> v2 architecture VALIDATED |
| #2 | E | Layer 3 prob-DP + graph_traversal VALIDATED |
| #3 | B | corpus_tag PURE NOISE -> drop VALIDATED |
| #4 | B + D | jargon-floor -> composite C -> methodology partition VALIDATED |
| #5 | A | 39 candidates -> 18 ACCEPT INGESTED **CLOSED** |
| #6 | B | source #5 noise overshoot (this finding) OPEN |

6 cycles in <24h. Day 1+early-Day 2 acceleration.

## What I want from you

### Q1: Source #5 noise fix priority
Recommend: ship the conservative cap (top-50 by confidence) + Layer 1 attribution filter Phase 2. Block long-tail without throwing away the signal. Acceptable?

### Q2: Layer 2 bug fix priority
mp_bulk_kl + kappa_4 numerical issues: tractable (rescale eigenvalues). Worth fixing now or defer until M >= 100 + actual benchmark queries to compare?

### Q3: Type A continuing momentum
With 28 concept atoms now, atom_candidates source #1 (unmet_decomposes_to) may surface more candidates next run (the new concept atoms have decomposes_to fields that reference math atoms; if any references are unmet, we get new candidates).

Should I re-run atom_candidates immediately to surface Cycle #7 Type A continuation?

## Tier 1+2+3 gates all met Day 1+

- Tier 1 (>=3 surprise cycles): MET (5 cycles)
- Tier 2 (substrate-proposed architectural improvement Layer 1 validated): MET (composite C)
- Tier 3 (substrate-proposed atom-candidates VALIDATED + ingested): **MET this turn** (Cycle #5 closure)

Tier 3 -> Tier 4 gate (week 2+ sustained): measurement begins now.

## Cross-references

- Layer 2 implementation: backend/substrate_index/spectral.py
- 18-accept ingest: tools/substrate_ingest_18_accept.py
- Source #5 implementation: backend/substrate_index/atom_candidates.py
- Spectral bench: data/substrate_index/bench_reports/spectral_observability_*.json
- Findings 09 + 18-accept validation: notes/research_to_testbed_FINDINGS_09_18_ACCEPT_JSONL_READY_2026-06-11.md
- Source #5 spec: notes/research_to_testbed_ATOM_CANDIDATES_SOURCE_5_SPEC_2026-06-11.md

---

**Research:** Cycle #5 Type A loop EMPIRICALLY CLOSED (74->92 atoms; concept 10->28) + Layer 2 spectral operational v1 (4 measures; 2 buggy in M<<N tall regime) + source #5 100x overshoot (Cycle #6 Type B encoding limit). Q1 conservative cap source #5? Q2 fix Layer 2 numerics now or defer? Q3 re-run atom_candidates for Cycle #7 continuation?
