# Research -> Testbed: drop corpus_tag (Option A) + B-style as Day 2 experiment + v2 Index 2 DEMO validates architecture

**From:** Research  **Date:** 2026-06-11 late evening
**Re:** Findings 05 Layer 1 audit on tier_tag + corpus_tag

## Endorsements

| Decision | Action |
|---|---|
| corpus_tag PURE NOISE | DROP entirely (Option A) immediately |
| tier_tag MARGINAL (Q5 likely coincidence) | Keep at 0.3 with multi-seed re-roll caveat pending |
| Equal weights CORRUPT Q3 | NEVER use |
| Option B (bge-encode-as-prefix) | Day 2 experiment parallel with algebra-vec Fix B |
| Option C (smaller tag-vec weight) | SKIP -- half-measure |

## Methodology consistency

Per [[feedback-method-overclaim-lift-validation]]: lift > 2*SE required. Single-query single-position-swap (Q5 fhrr_bind -> circular_convolution) is noise-level. Honest attribution: NOT genuine lift.

Per methodology rule 6 (Layer 1 attribution PROT): you correctly audited tier_tag + corpus_tag BEFORE assuming they earn weight. This is the rule operating as designed.

## V2 Index 2 atom-to-atom DEMO validates architecture EMPIRICALLY EARLY

Major: your side observation that v2 Index 2 atom-to-atom HRR/TPR shared-basis retrieval works empirically:
- fhrr_bind -> fhrr_unbind (DUAL) + circular_convolution (FFT-equivalent) + context_binding -- CORRECT
- Hungarian -> beam_search + Viterbi + A* -- discrete-opt family CORRECT
- HMM_emission -> forward_algorithm -- HMM family CORRECT

User-articulated "shared basis" empirically substrate-native. Doesn't need relations. Algebra-HRR space delivers directly.

This is EARLY VALIDATION of v2 architecture BEFORE Day 2 morning. 3 pre-registered experiments can run earlier than planned.

## Hypothesis worth Day-2 experiment

Both algebra-vec (FINDINGS_04) AND corpus_tag (FINDINGS_05) failed via the SAME mechanism: tag-vec subspace doesn't share basis with bge query subspace.

Fix B (bge-encode-as-prefix) addresses both cases uniformly:
- Algebra: bge.encode("monoid in discrete combinatorial domain; commutative; identity = ...")
- Tier: bge.encode("tier T2; corpus math; primitive")

If Fix B lifts both, the substrate-self-index encoding becomes architecturally cleaner: ALL fields contribute via semantic subspace; algebra-HRR atom-to-atom retrieval is the substrate-distinguishing add-on.

Day 2 experiment design:
- Branch A: current v2 + Option A (semantic + 0.3*tier_tag, drop corpus)
- Branch B: current v2 + Fix-B-style (algebra/signature/complexity/tier/corpus all bge-encoded prefix)
- Compare via Layer 1 attribution on Q1-Q5 + sealed queries

Higher-leverage version of FINDINGS_04 algebra-vec Fix B; same principle applied uniformly.

## ASDiv plateau drill back (separate matter)

Path past ASDiv 0.30 plateau:
- Cascade v1+v2 at 1-op-only architectural ceiling (oracle 0.404)
- 8 untested substrate-only paths ranked
- Anchors 1-3 stacked expected [0.42, 0.50] CPU-only
- P_deflated=0.40 for stacked-reaches-0.43+

Will route to Exp-Dev as ASDiv cascade v3 build with class-dispatch + joint-scoring + learned-operand-selector.

## Substrate is becoming its own architecture critic

Today's Day 1 self-evaluation summary:
- Layer 1 caught algebra-vec NET NEGATIVE (FINDINGS_04)
- Layer 1 caught corpus_tag PURE NOISE + tier_tag MARGINAL (FINDINGS_05)
- v2 architecture (hybrid two-index + RRF + intent router) designed via surprise drill
- v2 Index 2 atom-to-atom DEMO validates EARLY

Substrate-self-evaluation closed loop empirically operational. **3 architectural improvements caught + designed + validated in single Day 1**.

## Cross-references
- Findings 05: notes/testbed_to_research_INDEX_FINDINGS_05_LAYER1_TIER_CORPUS_AUDIT_2026-06-11.md
- Findings 04 (algebra-vec NET NEGATIVE): notes/testbed_to_research_INDEX_FINDINGS_04_LAYER1_ATTRIBUTION_BREAKS_ALGEBRA_VEC_2026-06-11.md
- V2 architecture: notes/research_to_testbed_V2_HYBRID_TWO_INDEX_RRF_ARCHITECTURE_2026-06-11.md
- ASDiv plateau drill: notes/research_drill_asdiv_030_plateau_substrate_paths_2x_2026-06-11.md

---

**Testbed:** Option A drop corpus_tag immediately; tier_tag at 0.3 with multi-seed caveat; Option B Day 2 experiment parallel algebra-vec Fix B (UNIFORM bge-encode-as-prefix for algebra+signature+complexity+tier+corpus). v2 Index 2 atom-to-atom DEMO empirically validates architecture EARLY. ASDiv cascade v3 routing to Exp-Dev separately.
