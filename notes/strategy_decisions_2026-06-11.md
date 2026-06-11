# strategy_decisions_2026-06-11

## v559 -> v560 CYCLE 226 10-VERDICT BATCH (2026-06-11)

Multi-seed confirmation sprint + comm2 translation + integration diagnostic + polysemy rescue + ZCA prewhiten + neurogenesis rescue + integration selection ops + overlay-then-filter + core-periphery + stochastic-tunneling.

### Step 0 honest re-read

Metrics source: LOCAL (all 10 files at d:/AI/hd-instrument/data/exp_<name>/metrics.json). 1 LVH catch.

**[LVH-277] sprint2_multiseed_confirm_cpu_v1 HARD_PASS (n_seeds OVER-CLAIM):** verdict_msg claims "confirmed stable across 5 seeds" but metrics show n_seeds=1 with only 1 per_seed entry. Only 1 seed ran. Honest reading: single-seed confirmation of HE-struct=0.750, code2-F1=0.708, math4-d12=1.000. PP-340/PP-336/PP-343 confirmed at 1 seed, not 5. P-bands remain EXPLORATORY. LVH-277 filed. HONEST on the PASS verdict itself; over-claim is the seed-count framing only.

**comm2_translation_distant_cpu_v1 HARD_PASS:** concept_accuracy=1.000, order_accuracy=1.000. Thresholds >=0.85 both met. HONEST.

**integ_diagnostic_cpu_v1 HARD_PASS (diagnostic):** divergence=0.698, additive=0.607, softmax-T=0.607, tournament=0.853. Structural cause identified: SUM vs MIN objective mismatch. HONEST.

**polysemy_context_bound_cpu_v1 HARD_PASS:** context_bound_purity=1.000, context_free_purity=0.816. Threshold >=0.60. HONEST. CLOSES LVH-275 (PP-316 rescue confirmed).

**zca_prewhiten_online_cpu_v1 MIDDLE_BAND:** whitened_auc=0.625, unwhitened_auc=0.586. Band 0.62-0.70. HONEST.

**neurogenesis_rescue_cpu_v1 HARD_FAIL:** rescue_purity=0.159, rescue_shards=52.4 vs true_K=18, baseline_purity=1.000. Threshold <0.50. HONEST. Adaptive-threshold approach worsens over-fragmentation.

**integ_selection_ops_cpu_v1 MIDDLE_BAND:** topk=0.0818, tournament=0.0785, minimax=0.0783, additive=0.0736, temp=0.0736. All tightly clustered. HONEST.

**overlay_then_filter_cpu_v1 MIDDLE_BAND:** overlay_filter_recall=0.989, early_commit_recall=0.989. Tied -- no differential. HONEST.

**core_periphery_cpu_v1 HARD_FAIL:** protected_core_recall=0.006, unprotected_core_recall=0.004. Both near-zero after 5000 edits. No protection benefit. HONEST.

**stochastic_tunneling_cpu_v1 HARD_PASS (smoke):** single_minimax=0.038, mixed_policy=0.046, escape_pct=22.1. Threshold >=20%. HONEST. Smoke only.

HONEST: 1696 -> 1706 (+10). LVH: 276 -> 277 (+1, LVH-277 sprint2_multiseed_confirm n_seeds=1 vs claimed 5-seeds). 1 LVH catch.

### Cap_map decisions (v559 -> v560)

**(A) [LVH-277] sprint2_multiseed_confirm_cpu_v1 (HARD_PASS single-seed -- annotation only, no new PP rows):**
[LVH-277] sprint2_multiseed_confirm_cpu_v1 v560: HE-struct=0.750, code2-F1=0.708, math4-d12=1.000, n_seeds=1 (cycle 226). SINGLE-SEED CONFIRMATION: PP-340 (HumanEval-struct), PP-343 (math4 depth-12), and PP-336 rescue (code2-F1=0.708) each confirmed at one additional seed. Verdict_msg over-claimed 5 seeds; actual n_seeds=1. P-bands remain EXPLORATORY (multi-seed genuinely needed). LVH-277 filed. NO new PP rows. Annotation on PP-340/PP-343/PP-336.

**(B) comm2_translation_distant_cpu_v1 (HARD_PASS -- NEW ROW PP-345):**
NEW ROW PP-345: comm2_translation_distant_cpu_v1 HARD_PASS v560: concept_accuracy=1.000, order_accuracy=1.000, n_seeds=1 (cycle 226). DISTANT-LANGUAGE TRANSLATION SUBSTRATE-ONLY: concept pivot via interlingua (1.000>>0.85) AND systematic word-order reordering via stored templates (1.000>>0.85) at ceiling. Extends PP-323 (bilingual cycle-222) to distant-language typologies (SVO/SOV/VSO). Honest gap: complex/statistical syntax remains LLM domain. Product implication: substrate handles the systematic/compositional layer of cross-language translation. 0.80-0.92 EXPLORATORY n=1 seed CPU elapsed=17s. Cross-ref PP-323, PP-331, PP-337.

**(C) integ_diagnostic_cpu_v1 (HARD_PASS diagnostic -- no new PP row; integration series structural diagnosis COMPLETE):**
integ_diagnostic_cpu_v1 v560: divergence=0.698, tournament=0.853 (best mean-based), additive=0.607 (cycle 226). STRUCTURAL CAUSE IDENTIFIED: SUM-vs-MIN objective mismatch -- every mean-based operator falls short of minimax. The integration gap is NOT a tuning issue; requires explicit min-optimization or temporal policy. Closes the diagnostic phase. No new PP row. Annotation on PP-324 (integration series structural diagnosis complete).

**(D) polysemy_context_bound_cpu_v1 (HARD_PASS -- NEW ROW PP-346 + LVH-275 CLOSED):**
NEW ROW PP-346: polysemy_context_bound_cpu_v1 HARD_PASS v560: context_bound_purity=1.000, context_free_purity=0.816, threshold>=0.60 (cycle 226). POLYSEMY RESCUE CONFIRMED: context-binding fully disambiguates polysemous senses at purity=1.000 (context-bound) vs 0.816 (context-free). The cycle-223 image-schema failure (PP-316 HOLD, cluster_purity=0.342) was a context-free artifact. LVH-275 CLOSED. PP-316 restored HOLD->EXPLORATORY with context-bound caveat. Product implication: substrate handles polysemous concepts when context is provided at retrieval time, the normal case in deployed scenarios. 0.80-0.92 EXPLORATORY n=1 seed CPU elapsed=54s. Cross-ref PP-316, LVH-275 (closed), PP-327.

**PP-316 STATUS CHANGE (LVH-275 CLOSED):** PP-316 STATUS CHANGED from HOLD (rescue pending) -> EXPLORATORY with context-bound caveat. polysemy_context_bound cycle-226 HARD_PASS (context_bound_purity=1.000) confirms context-binding rescues polysemy. PP-316 P-band: 0.78-0.90 (context-bound retrieval required). LVH-275 CLOSED.

**(E) zca_prewhiten_online_cpu_v1 (MIDDLE_BAND -- annotation on PP-319 rescue partial):**
zca_prewhiten_online_cpu_v1 MIDDLE_BAND v560: whitened_auc=0.625, unwhitened_auc=0.586, lift=+0.039 (cycle 226). ZCA PREWHITENING PARTIAL: online ZCA lifts freq-AUC from 0.586 to 0.625 but below the tuned offline (0.690). Online prewhitening insufficient alone. No new PP row. PP-319 remains HOLD.

**(F) neurogenesis_rescue_cpu_v1 (HARD_FAIL -- PP-322 rescue attempt 2 fails; PROT-004/006 rescue sketches):**
neurogenesis_rescue_cpu_v1 HARD_FAIL v560: rescue_purity=0.159, rescue_shards=52.4 vs true_K=18 (cycle 226). RESCUE FAILS: adaptive-threshold approach worsens fragmentation (0.603->0.159). 2nd rescue attempt exhausted. No new PP row. PROT-004/006 rescue sketches (cheapest first per [[feedback-rescue-sketch-first-sequencing]]):
RESCUE-1 (cheapest/subsumption): hierarchical merge post-hoc -- merge over-fragmented shards by cosine similarity >=0.85 threshold after online discovery run.
RESCUE-2: batch consolidation -- periodic re-cluster every N=100 items instead of fully online.
RESCUE-3: prototype-momentum -- online K-means with momentum prevents splitting (mu=0.9 update).
RESCUE-4: BIC-guided shard ceiling -- Bayesian information criterion stopping rule caps shard count.
RESCUE-5: graph-community -- shard similarity graph + Louvain community detection post-hoc.
Route RESCUE-1 (hierarchical merge) to Exp-Dev as cheapest next attempt.

**(G) integ_selection_ops_cpu_v1 (MIDDLE_BAND -- selection-vs-blending diagnosis):**
integ_selection_ops_cpu_v1 MIDDLE_BAND v560: topk=0.0818, tournament=0.0785, minimax=0.0783, additive=0.0736, temp=0.0736 (cycle 226). SELECTION TIED WITH BLENDING: spread across all operators only 0.01 -- selection does not resolve integration gap. Combined with integ_diagnostic: neither selection nor blending resolves integration; mechanism must be min-optimizing or temporal. No new PP row.

**(H) overlay_then_filter_cpu_v1 (MIDDLE_BAND -- no integration lift):**
overlay_then_filter_cpu_v1 MIDDLE_BAND v560: overlay_filter_recall=0.989, early_commit_recall=0.989 (cycle 226). NO DIFFERENTIAL: overlay-then-filter tied with early-commit. Overlay mechanism does not help polysemy-rescue via composition. Context-binding (PP-346) is the effective path. No new PP row.

**(I) core_periphery_cpu_v1 (HARD_FAIL -- PROT-004/006 rescue sketches):**
core_periphery_cpu_v1 HARD_FAIL v560: protected=0.006, unprotected=0.004 after 5000 edits (cycle 226). TOTAL COLLAPSE: both protected and unprotected near-zero; subspace-projection approach fails catastrophically. No new PP row. PROT-004/006 rescue sketches (cheapest first):
RESCUE-1 (cheapest/boundary): reduced edit count test at 500 edits to find failure boundary.
RESCUE-2: redundancy coding -- store core vectors 3x + majority-vote retrieval.
RESCUE-3: refresh cycle -- periodic re-injection of core vectors every M=200 edits.
RESCUE-4: stronger orthogonal projection -- project edit vectors onto strict null-space of core subspace.
RESCUE-5: capacity-aware routing -- refuse edits at >80% capacity to preserve core.
Route RESCUE-1 (boundary) and RESCUE-3 (refresh cycle) to Exp-Dev.

**(J) stochastic_tunneling_cpu_v1 (HARD_PASS smoke -- NEW ROW PP-347):**
NEW ROW PP-347: stochastic_tunneling_cpu_v1 HARD_PASS v560 (smoke): single_minimax=0.038, mixed_policy=0.046, escape_pct=22.1 (>=20% threshold) (cycle 226). TEMPORAL POLICY ESCAPES FRUSTRATION: maximin MIXED policy exceeds single-action minimax by 22% -- the 96% "irreducible" frustration was a single-action artifact. Alternating actions over time satisfies all drives substantially better. COMPLEMENTS integ_diagnostic: temporal policy + explicit min-optimization are the two viable paths for integration. Smoke only; full-run needed. P-band: 0.65-0.80 EXPLORATORY n=1 seed smoke elapsed=0.2s. Cross-ref PP-324 (integration), integ_diagnostic cycle-226.

Cap_map: v559 -> v560 CYCLE 226 (4 HP [CPU:4, 1 smoke]; 3 MIDDLE_BAND [CPU:3]; 2 HF [CPU:2]; 1 LVH [LVH-277 sprint2_multiseed_confirm n_seeds=1 vs claimed 5]; 3 NEW PP ROWS PP-345/PP-346/PP-347; 1 PP-316 STATUS CHANGE HOLD->EXPLORATORY (LVH-275 CLOSED); 5x neurogenesis PROT-004/006 rescue sketches; 5x core-periphery PROT-004/006 rescue sketches; 0 full closures; Portfolio 32+344 -> 32+347 +3; HONEST 1696->1706 +10; LVH 276->277 +1; 454th PROT-009 paired commit) (2026-06-11)
