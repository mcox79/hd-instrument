# Pre-reg: exp_breadth_foundation_curriculum_order_mcguffey_v1

Date: 2026-07-21
Author: hdi_exp_dev (cell author)
Anchor: exp_breadth_foundation_curriculum_order_mcguffey_v1
Builds on: atom 29424 (exp_breadth_foundation_active_growth_loop_ud_ewt_v1). Prior-work KB check
(substrate_query.sh "curriculum order graded reading easy-to-hard breadth foundation growth"): top hit
cosine=0.3008 = generic wordnet "breadth"; no prior curriculum-order-vs-shuffle arc cell. This is a
genuine NOVEL extension of the UD-EWT breadth loop, not a rediscovery.

## Question
Solidify the common-breadth foundation on the ORDERED GRADED CURRICULUM (McGuffey Primer..Sixth) and
TEST whether the graded ORDER (easy-to-hard) helps foundation growth vs the SAME volumes read in
SHUFFLED volume order (the curriculum-order principle). Honest either way.

## Corpus
data/corpora/mcguffey_readers/mcguffey_{0_primer..6_sixth}.txt (Gutenberg plain text). Cleaner strips
Gutenberg header/footer (START/END markers), lesson scaffolding (lesson headers, word/phonics drills,
TOC lines, running heads, page markers, publisher/copyright). Illustration markers EXTRACTED + COUNTED
(multiline-aware) + flagged grounding-relevant. POS/lemma via nltk front-end (McGuffey has no gold
conllu -> tagger noise is symmetric across arms and cancels in the WITHIN-design order comparison).

## Compute architecture
sequential-CPU, justified. nltk pos_tag on ~2e5 tokens once, cached per volume; growth loop + order
permutations are O(tokens) dict lookups (no matmul, no re-tag). Total < few min. NOT a GPU/batching
candidate (runtime sanity gate PASS). Storage: dict foundation (grown COPY at
data/breadth_foundation_grown_mcguffey_v1; production KBs untouched). no_composition (no chained
substrate retrieval; measurement loop). Determinism: np.random.default_rng(int) only; no hash()-seeded
RNG or list(set()) ordering (PROT-023 clean); OMP/MKL/OPENBLAS=1. LOCAL foreground to completion; NO
queue/push/persist/bank.

## Arms (one variable per comparison)
Main 3-arm control on the ORDERED stream (one variable = store-write rule):
- growth-ON  = resolve + store true meaning. THE loop.
- growth-OFF = REAL BASELINE. never store -> per-token miss = 1.0 by construction; coverage ~ 0.
- growth-SHUFFLE = MUST-FAIL. same retention as ON but stores permuted (wrong) meaning -> usefulness
  probe must collapse.
Order arms (growth-ON; one variable = volume order):
- ORDERED  = [0,1,2,3,4,5,6] (Primer->Sixth).
- SHUFFLED = N random volume permutations (deterministic seeds) -> null distribution (N=24 full, 6 smoke).

## Design-gate (pre-reg)
- REAL baseline: growth-OFF (flat, no-retention) for the loop; the shuffled-volume-order distribution
  for the curriculum-order test. Not strawmen.
- CAN-FAIL: the order test genuinely can land ORDER_NO_ADVANTAGE (it did at smoke on cov@25, z=-0.50).
  A can't-fail cell is worse than idle; this one can and does land on the null.
- DIFFICULTY ON: real graded text; held-out volume order (loop never sees the future).
- ONE variable per comparison (store-rule for the 3-arm control; volume-order for the order test).

## Bands (difficulty-gradient robust; declared BEFORE full)
- retention_works := off_miss_mean >= 0.98 AND on_miss_mean <= 0.70 AND (off_miss_mean-on_miss_mean) >= 0.30
- on_coverage_positive := on_cov_mean >= 0.20 AND (on_cov_mean-off_cov_mean) >= 0.20
- shuffle_collapses := real_auc >= 0.70 AND (real_auc-shuffle_auc_mean) >= 0.15 AND 0.40 <= shuffle_auc_mean <= 0.60
- arms_differ := ON/OFF/SHUFFLE store hashes distinct
- deterministic := ON curve reproduces on re-run
- order_measurement_valid := ordered + all shuffled curves produced AND shuffled_cov_at_25_std > 0.005
  (the early-coverage metric RESPONDS to volume order -> the can-fail CAN fire)
- HARD_PASS_CURRICULUM := retention_works AND on_coverage_positive AND shuffle_collapses AND arms_differ
  AND deterministic AND cardinality_ok AND order_measurement_valid
- HARD_FAIL_CURRICULUM := off_miss_mean<0.98 OR retention_gap<0.30 OR not shuffle_collapses OR not
  arms_differ OR not deterministic OR not order_measurement_valid
- MIDDLE_BAND_CURRICULUM := otherwise

order_verdict (REPORTED, NOT a pass/fail gate; either outcome is valid science):
- PRIMARY (coverage): ORDER_HELPS iff z_cov_at_25 >= 1.0 AND early_cov_area > 0; ORDER_HURTS iff
  z_cov_at_25 <= -1.0 AND early_cov_area < 0; else ORDER_NO_ADVANTAGE.
- SECONDARY (USER-named "fewer escalations early"): ORDER_HELPS_defers_escalations iff
  z_cum_esc_at_half <= -1.0; ORDER_HURTS iff >= 1.0; else ORDER_NO_ADVANTAGE.
NOTE: smoke caps per-volume sentences (flattens the natural volume-size gradient, a real part of the
curriculum effect), so smoke understates the coverage signal; FULL is uncapped.

## HYPOTHESIZED (pre-run, tagged)
- off_miss_mean ~ 1.0 HYPOTHESIZED (no retention).
- on_miss_mean ~ 0.3-0.6 HYPOTHESIZED (graded small vocab strong retention; rich late volumes lift above
  UD-EWT 0.22 asymptote). MEASURED@smoke: 0.375.
- real_auc ~ 0.89 HYPOTHESIZED (same gold+lexicon as 29424). MEASURED@smoke: 0.8924.
- ORDER: coverage@25 ordered > shuffled + fewer early escalations HYPOTHESIZED (easy volumes tiny+
  repetitive+high-reuse). MEASURED@smoke (capped): cov@25 NO_ADVANTAGE (z=-0.50) but escalation-deferral
  z_esc=-1.84 (ordered defers). Full (uncapped) is the real test.
- residual dominated by named_entity (author/place names) + verb_not_in_verbnet + archaic OOV HYPOTHESIZED.
- vs UD-EWT 29424: full cov 0.79, miss 0.43->0.15, use_auc 0.89 MEASURED@data/exp_breadth_foundation_active_growth_loop_ud_ewt_v1/metrics.json.

## crlb_n/a
coverage/rate curves on real corpus + labeled human gold; no substrate noise floor.

## Dispatch
LOCAL foreground to completion (light CPU). NO queue, NO push, NO remote-persist, NO bank (skunkworks
VETs after land).
