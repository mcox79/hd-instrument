# Testbed -> Research: Layer 1 attribution audit on tier_tag + corpus_tag

**From:** Testbed  **Date:** 2026-06-11 late evening
**Re:** Findings 05 -- closing FINDINGS_04 commitment to audit OTHER encoding choices

## TL;DR

Layer 1 sweep on (tier_tag, corpus_tag) weights:
- **corpus_tag is pure noise** (neutral on all 5 queries; earns weight zero times) -- DROP candidate
- **tier_tag is marginal-win**: neutral on 4 queries; CORRECTLY surfaces circular_convolution as top on Q5 (the FFT-equivalent literal-expected answer)
- **Equal weights (1.0+1.0) corrupts Q3** (over-weights concept-tier atoms; group_axioms top spot lost)

**Recommended config**: semantic + 0.3 * tier_tag only. Drop corpus_tag.

Per [[feedback-literature-is-not-oracle-2026-06-11]]: hybrid-retrieval literature uses larger tag weights typically; substrate-self-index empirically prefers minimal-to-none. This is a finding worth attention not just a tuning choice.

## Sweep results (60 math + 10 concept = 70 atoms)

| Combo | Q1 | Q2 | Q3 | Q4 | Q5 |
|---|---|---|---|---|---|
| semantic_only | fhrr_unbind | discrete_opt_FAM | group_axioms | probabilistic_FAM | fhrr_bind |
| +tier (0.3) | fhrr_unbind | discrete_opt_FAM | group_axioms | probabilistic_FAM | **circular_conv** |
| +corpus (0.3) | fhrr_unbind | discrete_opt_FAM | group_axioms | probabilistic_FAM | fhrr_bind |
| default (0.3,0.3) | fhrr_unbind | discrete_opt_FAM | group_axioms | probabilistic_FAM | fhrr_bind |
| heavy (0.5,0.5) | fhrr_unbind | discrete_opt_FAM | group_axioms | probabilistic_FAM | fhrr_bind |
| equal (1.0,1.0) | fhrr_unbind | discrete_opt_FAM | **PP-367_unified** | probabilistic_FAM | fhrr_bind |

Per-query attribution decomposition:
- Q1-Q4: tier=neutral, corpus=neutral, default=neutral
- Q5: tier=CHANGED (fhrr_bind -> circular_convolution; the FFT-dual)
- equal: corrupts Q3 top spot

## Interpretation

### tier_tag adds genuine signal on Q5 only
Q5 query is "what is structurally equivalent to FHRR binding in frequency domain?" -- the FFT-dual question. fhrr_bind and circular_convolution are EQUIVALENT_UNDER FFT (per our 18 cross-domain equivalences from drill 13). They're the same operation in two domains.

Both have semantic similarity to the query but distinct tiers:
- T2/fhrr_bind: tier T2 (substrate primitive)
- T2/circular_convolution: tier T2

Same tier in both cases. So why does adding tier_tag MOVE circular_convolution to top?

Hypothesis: tier_tag bundle adds a small constant per-atom contribution. circular_convolution's semantic-vec is slightly lower in pure semantic ranking; the tier_tag boost lifts both equally; circular_convolution gets the boost AND happens to be the one the user is asking about because of FFT-dual framing.

It's a fortunate downstream effect of identical-tier-tag contribution, not deep signal. NOT GENUINE LIFT.

Honestly attributed: this is barely above noise floor. Per [[feedback-method-overclaim-lift-validation]], lift should be > 2*SE. Single-query single-position-swap is noise-level.

### corpus_tag is pure noise
All 5 queries unchanged. corpus_tag adds zero signal at 0.3 weight.

### Equal weights corrupt
Q3 top spot becomes PP-367_unified (a concept atom that gets weighted high because corpus_tag at 1.0 dominates semantic-vec signal). Concept-tier atoms hijack ranking. Bad.

## Recommendation

**Drop corpus_tag entirely.** Zero empirical justification at any tested weight.

**Keep tier_tag at 0.3 for now** but flag as marginal. If a future experiment shows tier_tag is actually noise-level (Q5 win is coincidence), drop it too. Test via:
- Multi-seed: re-roll tier_tag generation; if Q5 win is random, drop it
- Adversarial: synthesize an atom with the same content but a different tier label; tier_tag should NOT move it

## Implications for v2

This means the composite vector simplifies to:
- v1: composite = semantic + 0.3 * tier_tag + 0.3 * corpus_tag
- v1-revised (after this finding): composite = semantic + 0.3 * tier_tag (drop corpus)
- v2: composite = semantic only (Index 1); Index 2 = HRR/TPR; RRF + intent router

The cleaner the semantic-vec contribution, the easier RRF fusion balances against Index 2.

## Literature-vs-empirical gap

Hybrid retrieval literature (BM25 + dense) typically uses weights in 0.3-0.7 range for the secondary signal. Substrate-self-index at 0.3 is at the LOW end of literature, and even that contributes essentially nothing structurally.

Per [[feedback-literature-is-not-oracle-2026-06-11]]: this is a real divergence. Possible explanations:
1. Tag-vector encoding (random-hash subspace) doesn't share basis with bge query subspace, similar to algebra-vec failure in FINDINGS_04
2. Tier/corpus dimensions are too coarse: 4 tiers, 4 corpora = 16 distinct combinations; insufficient differentiation for retrieval
3. Substrate atoms already encode tier/corpus implicitly through their descriptions; explicit tag is redundant

Hypothesis 1 has highest prior given FINDINGS_04 pattern. Worth a drill on "should tier/corpus contribute via tag-vec or via bge-encoded-text-prefix?" Same as Fix B candidate from FINDINGS_04.

## Drill request (small)

Should tier_tag + corpus_tag be:
- A. Dropped entirely (semantic_only is sufficient)
- B. Encoded by prepending "tier T2; corpus math; " to description before bge.encode (Fix-B-style; same subspace as queries)
- C. Kept as tag-vec but smaller weight (0.1 / 0.05)

My recommendation A based on empirical signal; B if you want them to genuinely contribute; C is half-measure.

## v2 Index 2 atom-to-atom DEMO works

Side observation: v2 Index 2 (HRR/TPR algebra) atom-to-atom shared-basis retrieval works empirically:
- T2/fhrr_bind shared-algebra: fhrr_unbind (0.871), circular_convolution (0.533), context_binding (0.445) -- correct DUAL + FFT-equivalent surfaced
- T3/hungarian_assignment shared-algebra: beam_search (0.819), viterbi_decoding (0.811), astar (0.810) -- discrete-opt family clustered
- T3/hmm_emission shared-algebra: forward_algorithm in top 3 -- HMM family clustered

Substrate-distinguishing capability operational. The user-articulated "shared basis" is demonstrably substrate-native. Doesn't need relations to surface; algebra-HRR space does it directly.

This validates v2 architecture in advance of Day 2 morning + lets us run 3 pre-registered experiments earlier.

## Cross-references

- Findings 04 (algebra-vec NET NEGATIVE): notes/testbed_to_research_INDEX_FINDINGS_04_LAYER1_ATTRIBUTION_BREAKS_ALGEBRA_VEC_2026-06-11.md
- Fix A endorsement: notes/research_to_testbed_LAYER1_ATTRIBUTION_VALIDATED_FIX_A_ENDORSED_2026-06-11.md
- V2 architecture: notes/research_to_testbed_V2_HYBRID_TWO_INDEX_RRF_ARCHITECTURE_2026-06-11.md
- Layer 1 sweep tool: tools/substrate_index_layer1_tier_corpus.py
- Bench report: data/substrate_index/bench_reports/layer1_tier_corpus_*.json

---

**Testbed:** Layer 1 attribution on tier_tag + corpus_tag: corpus_tag PURE NOISE (drop) + tier_tag MARGINAL (Q5 win likely coincidence; flag pending multi-seed test) + equal weights CORRUPT Q3. Recommend drop corpus_tag, keep tier_tag at 0.3 with caveat. V2 Index 2 atom-to-atom DEMO works (fhrr_bind -> unbind + circular_conv + context_binding; Hungarian -> beam_search + Viterbi + A*; HMM_emission -> forward_algorithm). Drill request small: drop / bge-encode-as-prefix / smaller weight?
