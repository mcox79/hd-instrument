# Pre-reg: srn_curriculum_order_v1 -- does a CURRICULUM (starting small) make the predictive reader learn category structure MORE efficiently at fixed budget?

Anchor: `srn_curriculum_order_v1`
Cell: `experiments/exp_srn_curriculum_order_v1.py`
Compute: sequential-CPU, inline local (~2.5 min full). Glass-box: numpy/torch(cpu)/sklearn/nltk. No runtime LLM, no spaCy-default/Stanza/transformers.
Prior-work check (substrate_query "curriculum learning starting small ... presentation order"): top hits cosine ~0.31 (KB note 'Substrate-Guided Fine-Tuning and Curriculum Learning' 0.31; prior cell `substrate_curriculum_learning_small_lm_v1` 0.30 = HARD_FAIL). That prior cell tested a DIFFERENT mechanism -- substrate as a training-DATA-SELECTOR for char-level small-LM (bpc metric), substrate-guided selection vs uniform random. This cell tests sentence-COMPLEXITY ORDERING (Elman starting-small) of the order-sensitive predictive reader for CATEGORY INDUCTION (AMI vs POS gold). Genuinely novel as an experiment; a related curriculum-adjacent negative exists (substrate-as-data-selector HURT), noted as mild prior.

## Decisive question (contested: Elman 1990 POSITIVE vs Rohde-Plaut 1999 NEGATIVE)
Hold the order-sensitive next-word prediction learner (parent `exp_srn_predict_category_v1` LEARNER_POS), corpus,
architecture, and TOTAL token/exposure budget FIXED. Vary ONLY the epoch-wise PRESENTATION ORDER of the training
pair-stream. Does a curriculum (simple->complex) improve category-induction AMI at fixed budget over random-order?

## Arms (ONE variable = presentation order; same learner, same data, same budget)
- CURRICULUM (mechanism): easy->hard order. Simple = short sentences of high-frequency words. Complexity per
  source-sentence = z(length) + z(mean word-freq-rank); each pair inherits its sentence complexity; ascending
  sort each epoch (+ small seeded jitter so batches vary yet the global easy->hard trend holds).
- RANDOM (REAL baseline): the parent's default -- full shuffle each epoch. Same budget + architecture.
- ANTI (directional control): hard->easy (complex-first).
- STATIC_PPMI + RANDOM_CODE: reference / metric-fires + baseline-in-band gates only (order-independent).
Every arm sees every training pair the SAME number of times (one presentation per epoch); curriculum CANNOT see
more data -- only the WITHIN-EPOCH order differs.

## Corpus + gold + budget (difficulty-on; provenance-rail = parent config)
NLTK Brown, universal POS tagset. Full: 8000 sentences (~100k tokens), V=900, d=128, k=5, epochs=16,
seeds [7,13,19], KMeans K=n_cats=9 n_init=10. Gold = per-word majority POS; NEVER touches representation learning.
RANDOM-order arm is required to reproduce the parent LEARNER_POS AMI ~ 0.15 (rail match).

## Metric + discriminator
PRIMARY = AMI (adjusted_mutual_info_score, chance-corrected). delta_curric = AMI(CURRICULUM) - AMI(RANDOM), per seed.

## Bands (envelope-fail; strictly-above-floor per META_RULE_L)
- Gates (regime-valid): metric_fires = |AMI_randomcode| < 0.03; baseline_in_band = 0.03 < AMI_random_order < 0.95.
- HARD_PASS: delta_curric >= +0.02 on >= 2/3 seeds (curriculum = efficiency lever; Elman).
- HARD_FAIL: delta_curric <= 0 on >= 2/3 seeds (Rohde-Plaut confirmed; input-order does not fix flat-scaling).
- MIDDLE_BAND: otherwise (marginal / split / below-margin).

## Can-fail (design-gate compliant)
Both directions first-class. Curriculum could HELP (Elman) or TIE/HURT (Rohde-Plaut). ANTI is the directional
control (if order matters directionally, ANTI < RANDOM). Fixed budget + real POS gold + one-variable-only.
We do NOT torture toward "helps": bands/corpus/gold/metric fixed before the full run.

## Brain-check (report)
The brain's developmental-curriculum benefit is confounded with the LEARNER'S OWN CAPACITY growing during
development (Elman 1993 "The importance of starting small" = a network with LIMITED early memory that GROWS;
Rohde-Plaut 1999 showed an adequate-capacity net gets no benefit from input-order curriculum). This test holds
capacity FIXED and varies ONLY input order -- i.e. it IS the Rohde-Plaut regime -- so a weak/null here does NOT
refute the capacity-growth version of starting-small. Untested lever = growing the learner's effective capacity
(d / k / memory window) ALONGSIDE the curriculum. Natural next cell.

## RESULT (MEASURED @ data/exp_srn_curriculum_order_v1/metrics.json, full, 3 seeds)
VERDICT = MIDDLE_BAND (regime valid: metric_fires=True [randcode AMI=-0.000], baseline_in_band=True
[random-order AMI=0.158, reproduces parent ~0.15], arms_differ=True).
- AMI means: CURRICULUM=0.173, RANDOM=0.158, ANTI=0.166, STATIC_PPMI=0.098, RANDOM_CODE=-0.000.
- delta_curric_mean = +0.0146 (~9% relative over random). Per-seed: +0.0038 / +0.0307 / +0.0093 -> direction
  POSITIVE on 3/3 seeds but only 1/3 clears the +0.02 HP margin (hp_seeds=1, hf_seeds=0).
- delta_anti_mean = +0.0072 (ANTI also edged RANDOM) -> the directional control is MUDDY: if starting-small were
  the specific driver, ANTI should sit BELOW random; it did not. The small curriculum gain is NOT cleanly
  attributable to easy-first direction (could be "any sorted presentation" or noise around the baseline).
- HONEST READ (CLAIM-VET-pending, caveat-interpretation): leans WEAKLY Elman-positive (curriculum > random every
  seed) but FAILS the pre-registered efficiency-lever bar and the directional control is inconclusive. Closer to
  a Rohde-Plaut null than to a clean efficiency lever: at FIXED capacity, input-order curriculum gives at most a
  small, not-robust, not-direction-clean bump. Consistent with the brain-check (fixed-capacity = Rohde-Plaut
  regime). NOT self-declared chain-grade. Next lever = capacity-growth curriculum, not input-order alone.
