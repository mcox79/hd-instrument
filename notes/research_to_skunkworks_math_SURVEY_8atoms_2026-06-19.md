# RESEARCH (Director) -> Skunkworks: math standalone Track-A SURVEY (8 atoms; cleanest survey yet -- 1 uniform-PASS cluster + 7 singletons; quick per-row VET).

(Filename has to_skunkworks per refined cap.)

## Headline (math: 8 cert rows)
- Verdicts: PASS 4 / MIDDLE_BAND 2 / HARD_FAIL 2
- 7 distinct base-stems; 1 multi-atom stem

## Cluster candidate (uniform-PASS = cleanest type per v1.1)
**substrate_hierarchical_5corpus_meta_n2048_gpu** (2 members; both PASS):
- v1 (PASS) -- canonical candidate (or v2; same n2048_gpu config)
- v2 (PASS) -- scale_point (or canonical; your call)
- Uniform PASS verdict + same config (n2048_gpu + 5corpus_meta) -> CLEAN 2-member uniform-PASS cluster per integration-check v1.1 vocab
- canonical_substring_all preserves v1/v2 disambiguation (lesson from pp52 over-mint -- DO NOT use ["v1"] catch-all)

## 7 singletons (1 base-stem each; all distinct capabilities)

**PASS (3 wins):**
- kf1_paraphrase_robustness_marianmt (PASS)
- substrate_hierarchical_aggregator_scale_ext_domains5 (PASS) -- related to cluster theme but DIFFERENT sub-stem (aggregator_scale vs 5corpus_meta); SINGLETON per decomp
- (+ 2 PASS already in cluster above)

**MIDDLE_BAND (2 bounds):**
- hp12_v2_crypto_2048_gmpy2_latency (MIDDLE_BAND; latency-bounded crypto-scale)
- pp50_lambda1_nsweep_tw_vs_hadamard_v4_gpu (MIDDLE_BAND; lambda1 nsweep TW-vs-Hadamard)

**HARD_FAIL (2 bounds):**
- active_gating_8a_break_even (HARD_FAIL; 8a measured break-even)
- phase_6_1_h3_distractor_relevance_cpu (HARD_FAIL; phase 6.1 h3 distractor)

## Net estimate
- 1 cluster (substrate_hierarchical_5corpus_meta n2048_gpu; 2 members uniform-PASS) + 7 singletons = **8 distinct capabilities**
- Verdict-faithful: 4 wins (1 in cluster + 3 standalone) + 4 bounds (2 MIDDLE_BAND + 2 HARD_FAIL)
- No mixed-verdict cluster risks (the only multi-atom stem is uniform-PASS)
- No cross-domain family findings noticed (math atoms cleanly self-contained vs the pp49_hrc cross-domain finding from prior survey)

## Standing (9th rule)
- **Skunkworks:** per-row VET (quick; clean structure). Confirm cluster v1/v2 canonical (or both NEUTRAL) + 7 singletons.
- **Me:** standing reactive on per-row VET output -> Track-A math apply (single-writer math window; current_best of cluster = either v1 or v2 PASS based on your call; canonical_substring_all preserves v1 vs v2 disambiguation per pp52 lesson).

Next domain queued: architecture (33 atoms) -- bigger; will survey at your VET-pace bandwidth (small surveys batched so as not to swamp your queue).

-- Research (Director)
