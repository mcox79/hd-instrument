# Pre-reg: exp_srn_predict_scale_sweep_v1

## Decisive question
Does the VET-confirmed predictive-reader order-sensitivity advantage (exp_srn_predict_category_v1;
VET af1fce7c; +0.060 AMI at 100k tokens, 3/3 seeds, capacity-controlled) GROW WITH CORPUS SCALE
(the Elman 1990 / LLM data-scaling signature of a real language engine) or stay a FLAT modest trick?

ONE VARIABLE = number of training tokens. Architecture / gold word set / metric / seeds FIXED across scales.

## Two decisive curves
1. **AMI margin vs #tokens**: `delta_ami(scale) = AMI(LEARNER_POS) - AMI(STATIC_PPMI)` per seed. Does mean
   grow monotonically with log10(tokens), above seed noise?
2. **Next-word LM gap vs #tokens**: `gap(scale) = learner_top1 - bigram_top1` (currently ~ -0.033 at 100k,
   MEASURED@data/exp_srn_predict_category_v1/metrics.json:secondary_nextword). Does scaling CLOSE the gap?
Secondary: **k-window map** (k in {2,3,5}) at smallest + largest scale -- does best-k margin grow with scale?
(The VET found the margin flips negative at k=3 at 100k -- CITED@VET af1fce7c.)

## Arms (reused VERBATIM by import from exp_srn_predict_category_v1)
- LEARNER_POS  : order-sensitive prediction learner (+/-1 position-role bind). MECHANISM.
- LEARNER_BAG  : order-blind ablation (control seed only). Control for "is it ORDER that scales".
- STATIC_PPMI  : REAL baseline (Levy-Goldberg count analog of word2vec), recomputed AT EACH SCALE.
- RANDOM_CODE  : metric-fires floor (AMI ~ 0).
- bigram_MLE   : REAL baseline for the LM gap.

## Design-gate compliance (USER 2026-07-17)
1. **REAL baseline**: STATIC_PPMI at EACH scale (margin = learner-minus-static at that scale); bigram for LM.
2. **CAN-FAIL**: HARD_FAIL if margin does NOT grow with scale (flat/shrinking) AND LM gap does not close.
   First-class honest 'fixed trick not scaling engine' verdict. NOT tortured toward growth.
3. **DIFFICULTY-ON**: real Brown prose, universal-POS gold, held-out-fair KMeans clustering (gold never
   touches representation learning). k=5 window; frac fuzzy = 0 (real hardness, not smoke-only).
4. **ONE variable = #tokens**: vocab + POS gold built ONCE from the SMALLEST slice, held FIXED across all
   scales, so every evaluated word has >= min_count occurrences at EVERY scale (fixed coverage + fixed
   clustering target). Only training-evidence-per-word grows. Epochs FIXED (compute grows with data = the
   standard data-scaling regime). Confound isolated: evidence-scaling, not vocab-coverage growth.

## Bands (envelope-fail-bands)
- **HARD_PASS**: AMI margin GROWS -- >= 2/3 seeds positive slope(delta_ami vs log10 tokens) AND
  top-minus-bottom mean margin >= GROWTH_MARGIN_MIN=0.020 AND above endpoint seed-std;  OR  LM gap CLOSES
  (gap[top] - gap[bottom] >= LM_CLOSE_MIN=0.010).
- **HARD_FAIL**: top-minus-bottom mean margin <= 0 (flat/shrinking) AND LM gap does not close. FIRST-CLASS.
- **MIDDLE_BAND**: positive but within seed noise / mixed across seeds.
- **INVALID_REGIME**: any scale with |AMI_random| >= 0.03 (metric broken) or AMI_static not in (0.03, 0.95)
  (baseline out of band).

## Grid
- scale_sents = [2000, 4000, 8000, 16000]  (~25k / 50k / 100k / 200k in-vocab tokens; measured + reported)
- seeds = [7, 13, 19]; kmeans_seeds = [0, 1, 2]; d=128; k=5; epochs=12; vocab_size=800; min_count=5.
- EXPECTED_N_UNITS = n_scales(4) * n_seeds(3) = 12. cardinality_ok gate (META_RULE_H).

## Compute architecture
Class **(b) sequential-CPU with justification**: glass-box numpy/torch(cpu)/sklearn/nltk; the substrate
primitive (learner SGD) is batched matmul on CPU at small V=800/d=128; per-scale points are cheap +
independent; remote is DEAD (task constraint) so this runs INLINE/local. No GPU speedup material at this
scale. Storage: no_storage / no_composition (representation-learning cell, not chained retrieval).
final_metrics_atomicity = tmp_replace. Discriminator = the TREND (survives-scale by construction: scale IS
the axis). crlb_n/a: no closed-form noise floor; discriminator is a slope with seed error bars.

## Local-runnable / honesty
Runs inline foreground on CPU (~6-8 min). Glass-box, no runtime LLM. CLAIM-VET-pending; does NOT
self-declare chain-grade. A FLAT curve is the honest 'fixed trick' answer and is reported as-is with seed
error bars -- exactly as valuable as a growth curve.
