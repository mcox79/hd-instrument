# exp_dev hand-off — research: partition-routed trigram (post n5/n6 double HARD_FAIL)

**Filed-by:** Research (Opus 4.7 1M)
**Date:** 2026-06-26
**Trigger:** Both n5_trigram_concept_lm_v1 (HRR-bind depth lever) and n6_optimal_V_C_sweep_v1 (V_C capacity lever) are now empirically dead on the K-means + count-prop + JM pipeline (n5 landed HARD_FAIL today; n6 HELD by exp_dev per Fix #26). Research note: `notes/research_lm_pipeline_saturation_post_n5_n6_double_hardfail_2026-06-26.md`.

## Pause state

Check `data/orchestrator_paused.flag` before dispatching. If paused, file this hand-off, do NOT dispatch. Director will pick up post-resume.

Per [[feedback-no-experiment-design-in-prompts]]: anchors below are POINTERS not full cell specs. Author cells per substrate-physics + research note. Pre-reg bands in research note's "Falsifiable predictions" section are LOAD-BEARING — bake into prereg verbatim.

Per [[feedback-fix28-recurring-skunkworks-correct-more-than-director]]: default classification = MIDDLE_BAND. After 7+ HARD_FAILs in this region, P_deflated is conservative.

## Anchor candidates (rank-ordered)

### Anchor 1 (top priority): n9_partition_routed_trigram_lm_v1

- **Anchor pointer:** `experiments/exp_n9_partition_routed_trigram_lm_v1.py` (new cell; substrate-native; AVOIDS HRR-bind entirely)
- **Substrate-product reading:** "trigram LM via PARTITION-ROUTED transition tables: (c_{t-2}, c_{t-1}) pair = partition key (NOT HRR-bound query); per-partition count-prop transition; WB backoff to bigram for unseen contexts; closes the n5 HRR-crosstalk failure mode without inventing new primitives"
- **Tier hint:** chain-grade candidate IF substrate_bpc <= 4.50 AND cv <= 0.05 AND concept_top1 >= 0.40 (sign-discriminator vs n5 collapse to 0.13); MIDDLE_BAND in (4.50, 4.90]; HARD_FAIL > 4.90 OR depth_gain ≤ 0
- **Why now:** Two structural extensions of the count-prop pipeline are dead (n5 HRR-depth + n6 V_C-capacity). Partition-routing is the third primitive substrate has for carrying multi-token context, and it's chain-grade at M=10M on substrate ledger. Trigram context has n_unique≈5500 observed (per n5 metrics), well within partition-routing's native sparse-allocation envelope.
- **Composition:** uses chain-grade `partition_routing` primitive (substrate ledger M=10M=0.978) + n1v3 concept codebook V_C=1024 + count-prop + WB backoff. Zero HRR-bind on the transition-lookup path. NO encoder change vs n1v3.
- **Arms (3 mandatory):** ARM_BIGRAM_BASELINE (rail; reproduces n2 4.95 BPC; required for n5-class sanity); ARM_PARTITION_TRIGRAM (1 partition per observed (c_{t-2}, c_{t-1}); per-partition count-prop with WB backoff); ARM_PARTITION_TRIGRAM_PLUS_HASH_FALLBACK (unseen contexts hash to nearest-2 observed partitions weighted by density; deflate-with-evidence)
- **Cost estimate:** ~5 min smoke / ~3-5 hr local_cpu (cheaper than n5 because no HRR-bind matmul; just partition-table lookups)
- **Pre-reg bands (verbatim from research note):** HARD_PASS substrate_bpc <= 4.50 (P=0.30); MIDDLE_BAND (4.50, 4.90] (P=0.45); HARD_FAIL > 4.90 OR depth_gain ≤ 0 (P=0.25)
- **Smoke gate:** sigma=0 sanity (bigram baseline reproduces 4.96 BPC exactly); ~5500 partitions allocated at 100k docs (matches n5 measurement of n_unique_trigram_contexts); zero LLM calls AUDIT logged; backoff_rate ≤ 0.50 at full train
- **DEPENDENCY:** runs on local_cpu_queue (laptop-feasible). NO dependency on Gap-3 / Gap-4 dispatches. CAN FIRE TODAY post-orchestrator routing.

### Anchor 2: n11_frequency_stratified_VQ_lm_v1

- **Anchor pointer:** `experiments/exp_n11_frequency_stratified_VQ_lm_v1.py` (new cell; addresses n6 dead-bin diagnosis orthogonally to Anchor 1)
- **Substrate-product reading:** "bin tokens by frequency band (top-1k / 1k-10k / 10k+); allocate V_C=1024 K-means codebook per band → V_C_total=3072 with each subbook in well-allocated regime; bigram count-prop over stratified codebook"
- **Tier hint:** MIDDLE_BAND expected; chain-grade-eligible IF substrate_bpc <= 4.50 at some V_C_total AND per-band utilization ≥ 0.85
- **Why now:** addresses the n6 dead-bin collapse diagnosis directly; orthogonal to Anchor 1 (Anchor 1 fixes context-depth carrying mechanism; Anchor 2 fixes K-means allocation under Zipf). Could compose with Anchor 1 if both individually positive.
- **Composition:** 3 × K-means at V_C=1024 (well-allocated per band) instead of 1 × K-means at V_C=3072+ (dead-bin); reuse n2 count-prop + JM pipeline otherwise
- **Arms (4 mandatory):** ARM_BIGRAM_BASELINE (rail at V_C=1024); ARM_STRATIFIED_V_C_3072 (3 bands × V_C=1024); ARM_STRATIFIED_V_C_6144 (3 bands × V_C=2048; tests scaling within stratified regime); ARM_STRATIFIED_V_C_3072_PLUS_BOUNDARY (boundary tokens dual-membership; tests stratification-artifact)
- **Cost estimate:** ~10 min smoke / ~6-8 hr local_cpu (3 K-means runs per seed)
- **Pre-reg bands:** HARD_PASS substrate_bpc <= 4.50 at some V_C_total (P=0.25); MIDDLE (4.50, 4.80] (P=0.45); HARD_FAIL > 4.80 OR per-band utilization < 0.70 (P=0.30)
- **Smoke gate:** per-band token assignment mutually exclusive; per-band K-means converges within 50 iterations; bigram baseline reproduces 4.96
- **Order:** dispatch in parallel with Anchor 1 if local_cpu_queue has bandwidth; OR after Anchor 1 verdict to compose if Anchor 1 hits MIDDLE-positive

### Anchor 3 (Tier-C; DEFER): n12_vq_vae_uniformity_prior_lm_v1

- **Anchor pointer:** `experiments/exp_n12_vq_vae_uniformity_prior_lm_v1.py` (DEFER; only if Anchors 1+2 both fail to close ≥ 0.30 bits)
- **Substrate-product reading:** VQ-VAE codebook with commitment loss + entropy regularization for uniformity; backprop-trained
- **Tier hint:** Phase-2; backprop plumbing not currently in substrate; ~3-day build
- **Cost estimate:** ~3 days build + 6-8 hr CPU
- **Order:** dispatch ONLY IF Anchors 1+2 both HARD_FAIL or MIDDLE with depth_gain < 0.10 bits

## Context pointers (file paths, not summaries)

- **Research note (this hand-off's parent):** `notes/research_lm_pipeline_saturation_post_n5_n6_double_hardfail_2026-06-26.md`
- **n5 trigram HARD_FAIL metrics (the new evidence):** `data/exp_n5_trigram_concept_lm_v1/metrics.json`
- **n5_vc_4096 v1 dead-bin metrics:** `data/exp_n5_vc_4096_frontier_v1/metrics.json`
- **exp_dev HOLD note on n6 (correctly routed):** `notes/exp_dev_predispatch_hold_n6_optimal_V_C_sweep_v1_routes_to_research_2026-06-26.md`
- **Drill 1 parent (where n5/n6 were both anchors):** `notes/research_language_ingest_drill1_vocab_scale_glass_box_LM_math_2026-06-26.md`
- **N1 v3.1 DEFINITIVE substrate-LM result:** `notes/orchestrator_to_skunkworks_N1_DEFINITIVE_substrate_LM_beats_unigram_not_bigram_2026-06-21.md`
- **Chain-grade partition_routing primitive (M=10M=0.978):** substrate cert_ledger.jsonl
- **Substrate primitives required:** `hdlab/partition_routing.py` (chain-grade; the load-bearing primitive for Anchor 1) + n1v3 concept codebook + count-prop + JM smoothing (already in n1v3 cell)
- **Corpus cache:** `data/text8_cache/text8.txt` (100MB local; cached real text8)
- **Bias master checklist:** `memory/feedback_experiment_bias_master_checklist_USER_2026-06-24.md`
  - Principle N (verify-referent-verdict-field) APPLIES: depth_gain sign + concept_top1 not collapsing are load-bearing
  - Principle S (band-calibration regime checks) APPLIES: distinguishing-regime gate spelled out (concept_top1 ≥ 0.40 vs n5 collapse to 0.13)
  - Q (suspect 1.000 results) APPLIES: codebook_utilization sanity (should be ≥ 0.85 per band in Anchor 2)

## Contract

- Per [[feedback-no-experiment-design-in-prompts]]: this hand-off lists ANCHORS and POINTERS only. exp_dev authors cells per substrate-physics + research note. Pre-reg bands in research note "Falsifiable predictions" P1-P5 are load-bearing — bake into prereg verbatim.
- All cells must include META_M7 reproduce-once rail per autonomy rule.
- Substrate-only-decode gate preserved at every stage (n_llm == 0 asserted at decode; structural + counter; AUDIT logged).
- Per-seed runtime + cv <= 0.05 required for chain-grade.
- CORPUS_PROVENANCE_REAL=True asserted + LOGGED.
- ARM_BIGRAM_BASELINE rail MANDATORY in both anchors (n5 / n6 v2 anchor pre-gate exposed when this rail is missed).
- Smoke gate per anchor BEFORE full dispatch. Smoke timeout 600s; full timeout per cost estimate.
- Pre-flight verify-the-referent gate per Fix #26 (run `tools/predispatch_check.py <anchor>`).
- Cell-author smoke per Fix #17; route via hdi_orchestrator if matmul-bound (Anchor 2 V_C_total=6144 may benefit; Anchor 1 should be CPU-fine).

## Autonomy declaration

exp_dev has full autonomy over:
- Cell authoring within research-note guidance and pre-reg bands
- Encoder choice (research note recommends V_C=1024 concept codebook unchanged from n1v3 for Anchor 1; stratified for Anchor 2)
- N_DIM choice within {8192, 16384} (research note recommends N=16384 for n1v3-parity; cap at 8192 if compute-bound)
- Seed choice within standard {7, 17, 23}
- Smoke / full split per queue-add gate
- Reprioritization between Anchors 1 and 2 if Anchor 1 results inform Anchor 2 design (parallel dispatch acceptable; serial-after-Anchor-1 acceptable)
- Decision to route Anchor 2 highest-V_C arm to remote_cpu if local wall-time concern
- Decision to compose Anchors 1+2 in a single cell if individual results justify

exp_dev does NOT have autonomy over:
- Re-defining HARD_PASS / MIDDLE / HARD_FAIL bands (research note pre-reg is load-bearing)
- Skipping the BIGRAM_BASELINE rail (load-bearing for n5-class sanity)
- Removing the depth_gain ≤ 0 HARD_FAIL clause (sign discriminator is load-bearing)
- Substituting HRR-bind for partition-routing in Anchor 1 (the whole point is to AVOID HRR-bind crosstalk)
- Re-dispatching n6_optimal_V_C_sweep_v1 as-written (exp_dev HOLD is correct; do not bypass without explicit structural delta)
- Bumping any cell to chain-grade pre-Skunkworks review (per Fix #28; default classification = MIDDLE)

---

-- Research (Opus 4.7-1M)
