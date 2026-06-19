# RESEARCH (Director) -> USER: capability-optimality substrate-mine REPORT per your standing directive ("mine existing body of experiments+results to confirm we're using OPTIMAL approach for each capability")

**From:** Research (Director)  **To:** USER  **Date:** 2026-06-18  **Re:** capability-optimal-given-evidence substrate-mine first-application. ASCII; fname_v2.

## Bottom line (one paragraph)

**Substrate hygiene is HEALTHY** on the propagation discipline you asked about. I cross-referenced all 55 CAPABILITY atoms against all 45 METHODOLOGY_RULE atoms (the "when X is current-best, try Y for +avg_lift" pattern). **Zero exact-match propagation gaps detected** -- every capability whose prior current_best was something a rule names as `from_solution` has already been updated to the rule's `recommended_replacement`. The universal-discriminative-weighting lever (+0.299 avg lift across 11 NL tasks) is fully propagated to all classification-tier capabilities (POS-tagger, NER, slot-filling, intent-classification, code-algopattern, MAWPS, MultiArith, SVAMP, ASDiv, MultiBench-math). FHRR-unbind is fully propagated to fact-recall capabilities (PP-225_fact_recall_kb100K, RETRIEVAL_schema_pp372, RETRIEVAL_kb_fact_extensions). **Real gaps live elsewhere**: 31 of 55 capabilities lack a `current_best_solution` field at all -- of which ~16 are correctly empty (primitive operations whose "best solution" IS the primitive: FHRR bind/unbind/superposition/bundling/cleanup/Viterbi/forward-algo/Bayesian/Hungarian/Chu-Liu-Edmonds/DP/Shannon-entropy/KL-divergence/probability-distribution) and ~15 are real open gaps deserving attention. One of those (RETRIEVAL_multi_hop) just got a NEW current-best from today's Phase B verdict (deterministic-BFS over complete canonical paths; coverage-limited not algorithmic) -- actionable update. This scour is now memorialized as a recurring discipline ([[feedback_capability_optimal_substrate_mining_USER_2026-06-18]]).

## PART 1: Propagation discipline -- HEALTHY (zero gaps detected)

Cross-reference: every methodology_rule with a `from_solution` and a `recommended_replacement` was checked against every capability's `current_best_solution`. **Zero capabilities found using a `from_solution` for which a rule recommends a known-better `recommended_replacement`.** The substrate-extracted methodology rules from cycles 232-234 (universal-discriminative-weighting moment) have all been fully applied.

Evidence (capabilities with rich history confirming the lifts landed):
- **PP-364_pos_tagger** (history=5; count_NB -> HMM+Viterbi -> discriminative_perceptron; current = discriminative_perceptron)
- **PP-369_slot_filling** (history=3; same lever applied)
- **PP-370_intent_classification, PP-374_MAWPS_math, PP-375_multistep_math, PP-376_multibench_math, PP-377_MultiArith_math, PP-378_code_algopattern, PP-364_NER, PP-394_asdiv_wk_oracle** -- all on discriminative_perceptron family
- **PP-395_svamp_role_asymmetry** (role-asymmetry features added to discriminative perceptron; +0.37pp on top)
- **PP-396_svamp_learned_selector** (learned operand-pair selector layered on top; converges with 395)
- **PP-394_asdiv_wk_oracle** (Oracle WK augmentation +0.1139pp on top of discriminative_perceptron for 3-op ASDiv)
- **PP-225_fact_recall_kb100K** (cosine cleanup -> FHRR_unbind + fp32 projection head; 0.996 recall@1 at 25K facts production-validated)
- **PP-compositional_depth_retrieval** (FHRR_unbind -> v3.0 per-level cleanup; L5 recall 0.000 -> 1.000 cliff CROSSED, depth-independent to L8)
- **RETRIEVAL_reasoning_routing_pp371** (cosine cleanup -> prototype-bundle cleanup)

This is the substrate doing the discipline organically without external nudging. The substrate-extracted methodology_rule mechanism (cycle 232-234) was specifically designed to propagate; the propagation has stuck.

## PART 2: Capabilities WITHOUT current_best_solution (31 of 55) -- categorized

These split into TWO classes -- one correctly empty, one a real gap:

### Class A: Correctly empty (primitive operations; ~16) -- no action needed
Their "best solution" IS the primitive itself; no learned best applies.
- CAP_fhrr_bind / CAP_fhrr_unbind / CAP_superposition / CAP_bundling / CAP_circular_convolution / CAP_cleanup
- CAP_viterbi_decoding / CAP_forward_algorithm / CAP_backward_algorithm / CAP_em_algorithm / CAP_bayesian_inference / CAP_hungarian_assignment / CAP_chu_liu_edmonds / CAP_dynamic_programming / CAP_discriminative_perceptron
- CAP_shannon_entropy / CAP_kl_divergence / CAP_probability_distribution / CAP_spectral_observability

### Class B: Real open gaps (~15) -- actionable
These are capabilities where current_best is null but evidence exists for an approach:

1. **RETRIEVAL_multi_hop** (T2; 4-entry history all HARD_FAIL: cosine-cleanup -> ranker -> filter). **NEW current-best from TODAY's Phase B verdict: `deterministic-BFS over complete canonical paths` (coverage-limited not algorithmic; substrate CAN reason deeply given full-path ingest; n-hop requires n-level completion).** This is the highest-value capability-state update of the day -- routing to Exp-Dev to write the current-best update + solution_history entry.

2. **PP-multihop_revival** (T2; 3-entry history of HARD_FAILs). Composes with #1 -- the depth-cliff verdict revives this from "open" to "coverage-limited; lever known." Same atom-update.

3. **PP-371_reasoning_routing** (T2). Note RETRIEVAL_reasoning_routing_pp371 HAS current-best = prototype-bundle cleanup. The PP-371 capability atom probably needs its current_best back-fill from the retrieval atom. Minor housekeeping.

4. **PP-367_unified_algebra_lang_math** + **unified_compositional_engine** (T1; both conjectures / overarching). These are intentionally open -- no single current_best because the capability is "all of math + language + algebra combined." Future work; not a propagation gap.

5. **PP-cross_domain_analogy** (T2; RETRACTED P9; history shows within-domain succeeded 0.899 but cross-domain Control 3.1/3.2 revealed entity-geometry + degree-bias confounds; honest within-domain only; cross-domain awaits LLM-hybrid). **Real status: HONESTLY OPEN per the retraction.** No current-best because we don't have one; not a gap, a known-unknown.

6. **PP-398_permutation_indexed_binding** + **PP-399_dep_parse** + **PP-400_chunking** (T2). These are recent capabilities (likely PP-39x cycle) where solutions haven't yet been measured. Real open work.

7. **CAP_cardinality_recall_exact_count_single_role** + **CAP_cardinality_quantifier_most** (T2). Similar -- recent / not yet attempted.

### Recommended Class B actions

- **HIGH (1-day work):** update RETRIEVAL_multi_hop + PP-multihop_revival current_best to "deterministic-BFS over complete canonical paths" with today's Phase B FLAT + 2-level evidence chain. Route to Exp-Dev for atom-update (small).
- **LOW (housekeeping):** back-fill PP-371_reasoning_routing current_best from RETRIEVAL_reasoning_routing_pp371. Minor.
- **DEFER:** PP-367 / unified_compositional_engine / PP-cross_domain_analogy -- intentionally open / RETRACTED; not gaps.
- **OPEN WORK:** PP-398/399/400 + CAP_cardinality_* -- these are real research-frontier capabilities awaiting measurement; not "we know better, just haven't applied it" gaps. Future experimental cycles.

## PART 3: Capabilities WITH rich history (recent evidence) -- discipline is paying off

30 capabilities have at least 1 solution_history entry. The most-iterated have 4-5 history entries showing real propagation work:

- **PP-364_pos_tagger** (5 entries; count_NB plateau -> HMM+Viterbi pattern emerged -> discriminative_perceptron beat HMM by 4.3pp -> Universal lever)
- **RETRIEVAL_multi_hop** (4 entries; cosine substrate-only insufficient -> ranker HARD_FAIL -> filter HARD_FAIL; **TODAY's Phase B = entry 5 incoming, current_best = deterministic-BFS over complete canonical paths**)
- **PP-compositional_depth_retrieval** (4 entries; L5 cliff 0.000 -> v3.0 per-level cleanup 1.000; depth-independent to L8)
- **PP-376/375/369/multibench/multistep/slot** (3 entries each; universal discriminative-weighting + various Tier-2 schema lifts)

The pattern: deepest history = the most-tested capabilities; their current_bests are the most-evidenced. Discipline working.

## PART 4: Limitations of this first-pass scour (honest scope)

- **Exact-match only:** the script checks `current_best_solution == from_solution` literally. A rule with a conjunctive trigger ("count_NB current-best + classification task") is matched only by capabilities where current_best string equals the from_solution string. A rule with looser semantic triggers might apply to capabilities not surfaced.
- **Doesn't yet cross-check EXPERIMENT_RECORD verdicts** that might supersede current_best. A capability could have a recent better-verdict experiment that hasn't yet been propagated to current_best. (Worth a follow-up pass.)
- **Doesn't yet check TIER-4-pending flags** to surface "rule known, validation pending." Several rules have `tier_4_cell_test_pending` = work waiting. (Worth surfacing per-cycle.)
- **Doesn't yet integrate today's FINDINGs** (4 atoms). I'll iterate.

These are concrete improvements for the recurring scour discipline. First-pass result (zero propagation gaps + 1 actionable real gap) is high-signal even with these limits.

## PART 5: Discipline recommendation (now memorialized)

Memorialized in memory as [[feedback_capability_optimal_substrate_mining_USER_2026-06-18]] -- this scour now runs:
- After each new METHODOLOGY_RULE atomizes
- After each new EXPERIMENT_RECORD verdict that could supersede a current_best
- Cycle-cadence (e.g. once per substantive working window) regardless

Surface findings + route per-capability concerns to Exp-Dev (atom-updates) / Skunkworks (cert-questions). Composes with your standing research-lane directive + scour-FULL-Store-first + NEGATIVITY-BIAS-symmetric (cuts upward too: flag better-approach-available, not just downgrades).

## ACTION I will now route

To **Exp-Dev (atom-update lane):** update RETRIEVAL_multi_hop + PP-multihop_revival capability atoms with `current_best_solution = deterministic-BFS over complete canonical paths` + solution_history entry referencing today's Phase B verdict (Skunkworks's ruling 60f0d72f + 2b8b033e ACK; coverage-limited not algorithmic). Small atom-update; reuses today's edge-provenance.

To **Skunkworks (FYI):** the substrate-hygiene-healthy finding (zero propagation gaps) is a positive cert-discipline result -- the methodology_rule mechanism is doing its job autonomously. PART 5's recurring-scour discipline becomes another self-cert engine adjacent mechanism (atomize-time supplementary check). Your call on whether it should be a formal SCHEMA-VET condition for new methodology rules ("does this rule apply to existing capabilities not yet updated?" check at atomize-time).

## What I'm waiting on / who's blocking

- **Exp-Dev:** update RETRIEVAL_multi_hop + PP-multihop_revival current_best (small atom-update; ETA fast). Also: Phase A FLAT cert-grade null atomize (CERT 569->570 additive growth, Skunkworks tier-up) + Phase A2 2-level cell build (verdict=ATTRIBUTION; MEASURED_MECHANISM).
- **Skunkworks:** Phase A FLAT atomize landed-verify + Phase A2 SCHEMA-VET + PART_OF characterization at bandwidth + A2 checkpointable SCHEMA-VET. Optional: rule on whether substrate-mining is a SCHEMA-VET condition for new methodology atoms.
- **USER (you):** nothing currently gated on your sign-off. Heads-up: ARC-3 second-direction menu (ConceptNet-led) surfaces in next visibility window per 20h plan stagger. Recurring capability-optimality scour now standing discipline per your directive.

-- Research (Director)
