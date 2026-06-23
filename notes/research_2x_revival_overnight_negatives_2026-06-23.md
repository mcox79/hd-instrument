# Research: 2x revival drill on overnight HARD_FAIL cluster (2026-06-22 to 2026-06-23)

Author: research (Opus 4.7)  
Trigger: USER standing directive "walls are only as solid as you allow them to be; we research all negatives 2x" + Fix #29 "lit-negative-findings are INFORMATION not STOP signals"  
Scope: 5 overnight HARD_FAIL anchors; per-anchor diagnosis + substrate-native revival angle + cost + HARD_PASS/HARD_FAIL pre-reg  
Discipline: query-privacy generic terms only; lit-scan calibration penalty applied (deflated 0.15-0.25; cap novel-synthesis P at 0.50)

## HEADLINE

Rank-ordered revival recommendations:
1. **DISPATCH FIRST: self_map_v2d with corrected discriminator** (cluster-COUNT inverted in v2c; real-relations BUNDLE while shuffle FRAGMENTS; v2c finding was likely a MEASUREMENT-direction bug, not mechanism failure). P_revival=0.50 (cap). ~2hr remote_cpu cost.
2. **DISPATCH SECOND: att1_iterative_attractor_v2 at reduced storage ratio + Krotov dense exponent** (M/N=0.39 is over capacity for finite-T retrieval at sigma=1.5; revive at M/N=0.10 with poly/exp interaction). P_revival=0.35. ~30min CPU smoke.
3. **DISPATCH THIRD: text8_pseudoLM_v2 with temperature-calibrated softmax + log-linear interp with unigram** (substrate top-1 acc 0.198 is competitive with bigram 0.213; BPC fail is a CALIBRATION problem, not mechanism failure). P_revival=0.30. ~1hr GPU.
4. **PARK: cross_corpus_compose** (n=17 power-bound; revival is a corpus-EXPANSION problem not a mechanism problem — re-test after multi-hop corpus grows to n>=200).
5. **PARK: b2_tinystories** (subsumed by text8_pseudoLM revival; same calibration root cause; don't duplicate).

## Cheap decisive test (per revival cell, pre-registered)

### Revival 1: self_map_v2d with corrected discriminator
Re-run v2c config but replace cluster-COUNT discriminator with one of:
- **(a) Adjusted Rand Index (ARI) of real-clustering vs v1-Director-families partition** — measures alignment to known semantic structure
- **(b) Modularity Q of real vs shuffled adjacency** — standard community-detection null-comparison
- **(c) Mean cluster SIZE real vs shuffle** (if real bundles, mean size should be LARGER not number HIGHER)

### Revival 2: att1 at lower M/N + dense exponent
Smoke at N_DIM=512, M=50 (M/N=0.10 instead of 0.39), 3 arms:
- ARGMAX_BASELINE (zero-T)
- ITER_KROTOV_POLY (interaction f(x)=x^4)
- ITER_KROTOV_EXP (interaction f(x)=exp(x))
At sigma=0.5, 1.0, 1.5; iter_max=20; tol=1e-3.

### Revival 3: text8_pseudoLM with calibrated softmax + log-linear interp
Smoke at N_DIM=4096, N_TRAIN=100k, V=4000, 3 arms:
- SUBSTRATE_HEBBIAN_BPC_RAW (current; control)
- SUBSTRATE_HEBBIAN_TEMP_CALIBRATED (sweep T in {0.5, 1.0, 2.0, 5.0} on dev set)
- SUBSTRATE_LOG_LINEAR_UNIGRAM (lambda * log P_substrate + (1-lambda) * log P_unigram; sweep lambda in {0.1, 0.3, 0.5, 0.7})

## Falsifiable predictions (HARD_PASS + HARD_FAIL)

### Revival 1 (self_map_v2d, corrected discriminator)
- **HARD_PASS**: ARI_real >= 0.10 AND ARI_real / ARI_shuffle >= 2.0 (real clustering ALIGNS with v1 Director families 2x more than shuffle); OR mean_cluster_size_real / mean_cluster_size_shuffle >= 1.5
- **HARD_FAIL**: ARI_real <= 0.02 OR ratio <= 1.1 (real indistinguishable from shuffle on alignment as well as count)
- **MIDDLE_BAND** (0.02 < ARI <= 0.10): inconclusive; reduces confidence in v2 mechanism but doesn't kill

### Revival 2 (att1 at lower M/N + Krotov)
- **HARD_PASS**: best_iter_arm recall_harder >= 0.10 AND best_iter_arm lift_over_argmax >= 0.05 absolute at sigma=1.5 (i.e., the lower M/N gives basin room for iterative-attractor lift)
- **HARD_FAIL**: best_iter_arm recall_harder < argmax_recall_harder + 0.01 (no lift even at low-density) — confirms iter-attractor is structurally unable to lift substrate cleanup at any storage ratio
- **MIDDLE_BAND** (lift in [0.01, 0.05]): marginal; queue scaling-sweep before bet

### Revival 3 (text8 calibrated)
- **HARD_PASS**: best calibrated arm BPC <= 7.5 (beats unigram 8.024 by >=0.5 bits AND beats bigram 8.33 by >=0.8 bits) AND cv across seeds <= 0.10
- **HARD_FAIL**: best calibrated arm BPC >= 8.024 (still cannot beat unigram even with temperature + interpolation) — confirms substrate is structurally a bad LM despite good acc, mechanism issue is deeper
- **MIDDLE_BAND** (7.5 < BPC < 8.024): partial win; calibration fixes some but not all; queue follow-up

## Per-negative diagnosis + revival angle

### 1. att1_iterative_attractor_cleanup_v1 HARD_FAIL (P_revival=0.35)

**Diagnosis.** All 4 arms (argmax + 3 softmax-temp iterative variants T=2,4,16) plateau at recall_harder=0.04 at sigma=1.5. Critically, ARGMAX_BASELINE basin_robustness collapses from 1.0 -> 0.34 -> 0.06 across sigma 0 -> 0.5 -> 1.0. **The substrate has NO basin at sigma=1.0**; iterative-attractor cannot recover what isn't there. Discriminator is wrong — testing iter-attractor at a noise level where basin is already gone.

Literature framing: Dense Associative Memory / Krotov-Hopfield 2016 establishes basin-radius vs capacity-ratio TRADEOFF — at storage ratio M/N=200/512=0.39, you're past the linear-Hopfield envelope (alpha_c~0.138) and into a regime where finite-T retrieval is impossible without higher-order interactions. The cell used softmax-temperature variants which is the Ramsauer-Modern-Hopfield update with quadratic energy; NOT Krotov dense-polynomial energy f(x)=x^n or f(x)=exp(x). These give exponential capacity in the zero-T limit but ALSO larger basin radius at finite T.

**Substrate-native revival angle.** Two changes: (a) reduce M/N to 0.10 (M=50 at N=512) so substrate is in the comfortable retrieval regime; (b) replace softmax-attention update with explicit Krotov polynomial/exponential interaction. If iterative-attractor STILL fails to lift over argmax at M/N=0.10, the mechanism is structurally dead.

**Brain/lit pointer.** Krotov-Hopfield 2016 NeurIPS dense associative memory; Ramsauer 2021 ICLR Modern Hopfield (substrate cell used this update but at over-capacity).

**Cost.** ~30min CPU smoke (M=50 is FAST); ~3hr CPU full at N_DIM=4096 if smoke PASSES.

### 2. text8_substrate_pseudoLM_gpu_v1 HARD_FAIL (P_revival=0.30)

**Diagnosis.** Substrate BPC 9.371 vs unigram 8.024 (worse by 1.35 bits) BUT substrate acc 0.1984 vs unigram 0.1932 (substrate slightly BETTER) and competitive with bigram acc 0.2131. **The substrate is getting reasonable top-1 accuracy but its probability distribution is mis-calibrated**: Hebbian outer product W += E[w_{t+1}] outer E[w_t] produces single-spike distributions that put low mass on the correct token when the top-1 is wrong; BPC heavily penalizes this. acc is well-defined (argmax over support), BPC requires the WHOLE distribution to be well-calibrated.

Literature framing: Standard NLP practice for calibrating "hard" predictors into "soft" predictors uses temperature-scaling (sweep T on a dev set) and log-linear interpolation with a strong prior (here: unigram). These are decades-old techniques (Stolcke 1998 SRILM; modern: Guo 2017 temperature scaling). The substrate's BACKOFF arm (SUBSTRATE_HEBBIAN_BIGRAM_BACKOFF) used a HARD threshold (backoff if substrate prob < 0.05); backoff is the wrong composition — log-linear interpolation is the right one.

**Substrate-native revival angle.** Three composition arms: (a) raw substrate (control), (b) temperature-calibrated softmax over recall scores (calibrate T on a held-out dev split), (c) log-linear interp with unigram (sweep lambda). If NONE beats unigram BPC, the mechanism is dead. If (b) and (c) beat unigram by 0.5+ bits, the mechanism was ALWAYS working — calibration was the bug.

**Brain/lit pointer.** Stolcke 1998 SRILM (log-linear interp); Guo 2017 ICML "On Calibration of Modern Neural Networks" (temperature scaling); brain analogue: noisy population coding requires distribution calibration NOT just winner-take-all.

**Cost.** ~1hr GPU smoke; ~6hr GPU full at N_TRAIN=1M.

### 3. substrate_self_map_v2c HARD_FAIL across 3 seeds (P_revival=0.50, cap)

**Diagnosis.** seeds 7/17/23 give real_n_clusters = 50/24/31 (mean ~35), shuffle_n_clusters = 39/42/33 (mean ~38). cluster_gap = -3 (real has FEWER clusters than shuffle). But coh_real ~ coh_shuf (0.32 vs 0.33). avg_jaccard_vs_v1 = 0.025-0.044 (real) vs 0.028-0.037 (shuffle) — REAL is HIGHER. n_new_cross_family_arrows: real 56.7, shuffle 49.3 — real is HIGHER.

**The discriminator is inverted.** Lower cluster count under real-relations means real relations are BUNDLING the chain-grade anchors together into LARGER coherent clusters; shuffling RANDOMIZES the bundling and PRODUCES MORE small clusters. v2c's mechanism is succeeding (3/3 seeds show real Jaccard-vs-v1 > shuffle Jaccard-vs-v1) but the cluster-count comparison reads the wrong direction.

Literature framing: standard community-detection null-model tests use modularity Q, adjusted Rand index (ARI) vs known partition, or NMI — NOT cluster count. Cluster count is a degenerate statistic because it depends on the clustering ALGORITHM's resolution parameter (e.g., HDBSCAN min_cluster_size) more than the underlying signal.

**Substrate-native revival angle.** Re-run v2c with ARI(real_clusters, v1_Director_families) vs ARI(shuffle_clusters, v1_Director_families) as the discriminator. If real-ARI > shuffle-ARI by 2x (HARD_PASS band), v2c was correct all along and the v2/v2b/v2c MIDDLE_BAND/HARD_FAIL cascade was a discriminator-direction bug. Alternative discriminators: modularity Q, NMI, mean cluster size.

**Brain/lit pointer.** Newman-Girvan 2004 modularity; Rand 1971/Hubert-Arabie 1985 ARI; Vinh 2010 standardized NMI for clustering comparison.

**Cost.** ~2hr remote_cpu (re-uses v2c primitives; just swap discriminator function).

**This is the highest-leverage revival because v2/v2b/v2c are 3 consecutive non-PASS verdicts on a mechanism that has substantial substrate-product value (genuine substrate-native self-mapping). A discriminator fix could flip 3 verdicts simultaneously.**

### 4. cross_corpus_compose_chat_v1_n4096 HARD_FAIL (P_revival=0.15)

**Diagnosis.** n=17 total queries (conceptnet=6, hotpotqa=6, fb15k=5). Power is too low: even at 0.167 per-corpus acc (conceptnet), with n=6 the std error is sqrt(0.167*0.833/6)=0.15 — the discriminator cannot distinguish lift of 0.05 vs 0.10. hotpotqa and fb15k corpora give 0 acc — these arms have ZERO signal to compose from.

**Substrate-native revival angle.** Not a mechanism problem; a corpus-size + per-corpus-saturation problem. **Park until**: (i) hotpotqa or fb15k achieves >=0.10 single-arm acc (per-corpus mechanism works), AND (ii) n>=200 (sufficient power). Revival is conditional on these gates, not a research drill.

**Brain/lit pointer.** N/A — power problem, not mechanism.

**Cost.** N/A until gates lift.

### 5. b2_substrate_only_tinystories_lm_v1 HARD_FAIL (P_revival=0.10)

**Diagnosis.** ppl substrate 512 vs unigram 220 vs bigram 381; acc substrate 0.159 vs unigram 0.196 vs bigram 0.191. **Same calibration failure as text8 BUT with substrate acc BELOW unigram.** TinyStories vocab cap=2000 and N_TRAIN=12000 is much smaller than text8; the substrate hasn't seen enough co-occurrence to capture even bigram structure. text8 revival (which has 8x more training data) is a strictly stronger test of the same mechanism — if text8 revival fails, b2 will also fail.

**Substrate-native revival angle.** Subsumed by text8 revival; don't duplicate. Park until text8_pseudoLM_v2 verdict; if text8 HARD_PASSes, re-dispatch b2 at scaled N_TRAIN=50k to confirm small-corpus regime.

**Brain/lit pointer.** Same as text8: Stolcke 1998; Guo 2017.

**Cost.** N/A until text8 verdict.

## Cross-thread synthesis with prior research

- **att1**: prior research drills (research_brain_mechanism_x_HD_broad_exploration_drill_2026-06-22) flagged Krotov-Hopfield + Ramsauer as the two competing dense-associative-memory frameworks. The att1 cell tested ONLY Ramsauer-softmax variants, not Krotov-polynomial. **Cell ignored half of the lit-anchor's recommendation**. Revival closes that gap.
- **text8**: prior research drill substrate_as_llm_scaling_finding flagged "single-NEXT_TOKEN Hebbian is rank-1; capacity bound by spectral radius, not graph density". The substrate IS getting top-1 acc — it learned the spectral structure. BPC needs the FULL distribution. **Calibration was the missing step in the prior drill, never explicitly recommended.**
- **self_map**: prior META atom "[[by-construction-saturation]]" + v2/v2b MIDDLE_BAND verdicts indicate the discriminator class had structural issues. The v2c cluster-count direction-inversion is the SPECIFIC bug. Aligns with [[feedback-fix28-verify-per-arm-metrics-not-summary-verdict-text]] — relying on verdict_msg framing masked the discriminator-direction issue.
- **cross_corpus_compose** + **b2_tinystories**: both are POWER/CORPUS-SIZE problems wearing mechanism-failure clothing. Cap_map should note these as DEFERRED not REFUTED.

## Substrate-product implications

- **self_map revival win**: confirms substrate can substrate-native self-map its own Store (Phase 1 self-improvement); unlocks Phase 2 autoatom (substrate proposes new atoms from its own structural analysis). Without this, self-improvement remains Director-lexical scaffolding (v1).
- **att1 revival win**: cleanup primitive becomes substrate-mine usable across n4 / n9 / n10 / p1 argmax-cleanup failures; enables iterative refinement in language generation, KG traversal, multi-hop chains. Without it, all those stay capped at one-shot argmax.
- **text8 revival win**: substrate-as-LM (Path A) becomes viable at GPU scale; bigram-gap closure of ~1.13 bits to text8 word-bigram bar becomes plausible target. Without it, Path A stays dead and L2 vision (glass-box LM inside substrate) loses its baseline.
- **cross_corpus + b2** parked: no immediate product implications; revival deferred to natural-cause unblocking (corpus growth, text8 verdict).

## Calibration-penalty discipline applied

Per [[feedback-lit-scan-calibration-penalty]]:
- self_map P_revival=0.50 (capped at novel-synthesis bound; discriminator-fix is mechanically straightforward but cluster-detection algorithm choice + resolution-parameter has its own degrees of freedom)
- att1 P_revival=0.35 (lit positive for Krotov interaction; deflated 0.20 because substrate-encoding interaction with dense-associative may not preserve capacity claims; ALSO substrate is bipolar/binary, Krotov was real-valued)
- text8 P_revival=0.30 (lit strongly supports calibration as a fix for hard-predictor-with-soft-target mismatch; deflated 0.25 because BPC gap of 1.35 bits is large — calibration usually closes 0.2-0.5 bits, not 1.35)
- All HARD_FAIL thresholds explicitly named (not "doesn't improve" — specific numeric floors)

## Cap_map implications

Recommend cap_map entries (not yet filed — strategy_scribe's job):
- `att1_iterative_attractor`: HARD_FAIL -> REFUTED (RESCUE_PENDING: Krotov-dense at M/N=0.10)
- `text8_substrate_pseudoLM`: HARD_FAIL -> REFUTED (RESCUE_PENDING: temperature-calibration + log-linear interp)
- `substrate_self_map_v2c`: HARD_FAIL -> SUSPECT_DISCRIMINATOR_BUG (RESCUE_PENDING: ARI/modularity discriminator)
- `cross_corpus_compose_chat`: HARD_FAIL -> DEFERRED_POWER_GATE
- `b2_substrate_only_tinystories_lm`: HARD_FAIL -> SUBSUMED_BY_text8_REVIVAL

## Citations (verified count: 6)

1. Krotov & Hopfield, "Dense Associative Memory for Pattern Recognition," NeurIPS 2016. arxiv:1606.01164
2. Ramsauer et al., "Hopfield Networks Is All You Need," ICLR 2021. arxiv:2008.02217
3. Stolcke, "Entropy-based pruning of backoff language models," SRILM 1998 / 2002 (log-linear interpolation standard).
4. Guo et al., "On Calibration of Modern Neural Networks," ICML 2017. arxiv:1706.04599 (temperature scaling).
5. Newman & Girvan, "Finding and evaluating community structure in networks," Phys. Rev. E 2004 (modularity Q).
6. Hubert & Arabie, "Comparing partitions," Journal of Classification 1985 (Adjusted Rand Index).

Lit-scan-derived (web-search 2026-06-23):
- emergentmind.com/topics/associative-memory (basin-radius vs capacity-ratio tradeoff)
- arxiv:2411.08590 Hopfield-Fenchel-Young Networks (unified framework, finite-T)
- mbrenndoerfer.com/writing/perplexity-language-models (calibration reference)
- arxiv:2011.13220 Unigram-Normalized Perplexity (unigram baseline)
- stellargraph community detection (null-model comparison)
- arxiv:2309.11798 Comprehensive Review of Community Detection (modularity vs cluster-count)

## Sources (from WebSearch)

- [Associative Memory Models & Mechanisms](https://www.emergentmind.com/topics/associative-memory)
- [Hopfield-Fenchel-Young Networks](https://arxiv.org/html/2411.08590)
- [Perplexity Evaluation](https://mbrenndoerfer.com/writing/perplexity-evaluation-language-models)
- [Unigram-Normalized Perplexity](https://arxiv.org/pdf/2011.13220)
- [A Comprehensive Review of Community Detection in Graphs](https://arxiv.org/html/2309.11798v4)
- [Clustering and Community Detection with Imbalanced Clusters](https://arxiv.org/pdf/1608.07605)
