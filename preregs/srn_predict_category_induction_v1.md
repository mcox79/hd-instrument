# Pre-reg: srn_predict_category_v1 -- glass-box next-word prediction-learning induces lexical category structure?

Anchor: `srn_predict_category_v1`
Cell: `experiments/exp_srn_predict_category_v1.py`
Compute: sequential-CPU, inline local (< 2 min full). Glass-box: numpy/torch(cpu)/sklearn/nltk. No runtime LLM, no spaCy-default/Stanza/torch-transformers.
Prior-work check (substrate_query): top hits = KB CONCEPT atoms ('Self-supervised learning' cos=0.31, 'lexical category' 0.31) + note 'Field 5: Hebbian/predictive-coding self-supervised representation learning' 0.26. NO prior arc experiment cell runs this contrast -> genuinely novel as an experiment (KB knows the concepts; no prior cell).

## Decisive question
Does self-supervised NEXT-WORD PREDICTION-LEARNING induce LEXICAL-CATEGORY structure in the learned word
representations, significantly BETTER than a STATIC co-occurrence/count representation of the SAME text?
Isolates what error-driven prediction-LEARNING adds over static distributional counting (the thing that keeps
tying frequency in the reading arc). Glass-box VSA analog of Elman (1990) SRN category induction.

## Arms (ONE variable = prediction-LEARNING on/off, identical text + identical causal window k)
- LEARNER_POS (primary mechanism): learned embeddings E, Adam-SGD next-word CE; context = VSA position-bind
  (fixed +/-1 role per relative position) then bundle(mean) of previous-k input codes. ORDER-SENSITIVE
  (Elman/SRN-faithful). Prediction = score-all vs output codes W (cleanup); update = surprisal gradient.
- LEARNER_BAG (ablation): same, but order-BLIND (mean of prev-k, no position bind). Isolates order-sensitivity.
- STATIC_PPMI (REAL baseline): directional (causal, window k) co-occurrence COUNTS -> PPMI -> truncated SVD to d.
  Levy-Goldberg (2014) count analog of word2vec; best-in-class static distributional rep, NOT a strawman.
- RANDOM_CODE (must-fail floor / metric-fires control): fixed random Gaussian codes.

## Corpus + gold (difficulty-on)
NLTK Brown, universal POS tagset. Gold = per-word MAJORITY POS category (9 cats: NOUN/VERB/ADJ/ADV/DET/ADP/PRON/PRT/NUM).
Full: 8000 sentences (~100k tokens), V=900, d=128, k=5, epochs=16, seeds [7,13,19], KMeans K=n_cats n_init=10.
Gold labels NEVER touch representation learning (unsupervised clustering) -> held-out-fair.

## Metric
PRIMARY = AMI (adjusted_mutual_info_score), chance-CORRECTED (random ~ 0). Raw NMI carries finite-sample upward
bias that mis-fires the metric-fires gate; AMI is the correct choice. KMeans(K=n_cats) on L2-normalized rows.
Discriminator = delta_ami = AMI(LEARNER_POS) - AMI(STATIC_PPMI), per seed.

## Bands (envelope-fail; strictly-above-floor per META_RULE_L)
- Gates (regime-valid): metric_fires = |AMI_random| < 0.03; baseline_in_band = 0.03 < AMI_static < 0.95.
- HARD_PASS: delta_ami >= +0.02 on >= 2/3 seeds (learner induces category structure BEYOND static counting).
- HARD_FAIL: delta_ami <= 0 on >= 2/3 seeds (prediction-learning adds nothing beyond counting; FIRST-CLASS
  negative -> drills "what does the brain's predictor have that ours lacks?").
- MIDDLE_BAND: otherwise (marginal / split).

## Can-fail (design-gate)
word2vec ~ PPMI-SVD (Levy-Goldberg 2014) -> LEARNER beating STATIC is a genuine empirical question, NOT
by-construction. LEARNER_BAG (order-blind) is EXPECTED to ~ tie static (both order-blind); the ablation staying
at tie is the honest control that any LEARNER_POS win is attributable to order-sensitivity, not to tuning.
We do NOT torture toward pass: bands/corpus/gold/metric fixed; only the mechanism arm was given its correct
(order-sensitive) form after the order-blind ablation tied.

## Confounds watched
Absolute AMI is modest (both arms weak in absolute terms; purity ~0.55 vs 0.50 majority-class NOUN base rate).
The load-bearing claim is the COMPARATIVE contrast (LEARNER_POS > STATIC), not absolute POS induction, and not
absolute next-word bpc (expected weak; SECONDARY only, non-load-bearing).

## RESULT (MEASURED @ data/exp_srn_predict_category_v1/metrics.json)
VERDICT = HARD_PASS (regime valid: metric_fires=True, baseline_in_band=True, arms_differ=True).
- AMI: LEARNER_POS=0.158, LEARNER_BAG=0.094, STATIC_PPMI=0.098, RANDOM=-0.000.
- delta_ami (LEARNER_POS - STATIC) = +0.060 mean, on 3/3 seeds (+0.055..+0.065). delta_ami_bag = -0.005 (tie).
- LOCALIZATION: order-BLIND learner ties static (Levy-Goldberg); order-SENSITIVE learner beats static by ~60%
  relative AMI. What prediction-LEARNING adds over static counting = ORDER/SEQUENCE-sensitivity (Elman's SRN insight).
- SECONDARY next-word top-1 (probe-bug fixed, trained W): learner 0.136 vs bigram 0.168 (weak, expected, NOT load-bearing).
CLAIM-VET-pending; NOT self-declared chain-grade. Construction-proof that order-sensitive prediction-learning CAN
induce category structure beyond counting on real prose; does NOT prove downstream reading capability.
