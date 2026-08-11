# Pre-reg: exp_propara_entity_fate_external_knowledge_probe_v1

Type: DECISIVE MEASUREMENT PROBE (not a pipeline-dispatch cell). Runs once, locally, to
completion; no smoke/full escalation; no remote queue dispatch. Compute-proportionality rule
applies (directional go/no-go question -> cheapest decisive method: reuse the existing gam
learner + cached local data sources, no training fit).

## Question
Does any accessible EXTERNAL knowledge source supply entity-level process-role/fate grounding
(participant -> CREATE/MOVE/DESTROY) that GENERALIZES to entities whose SURFACE STRING was never
seen at fit time -- the exact control that killed the learned glass-box binder
(exp_propara_schema_learned_grounded_binder_v1, HARD_FAIL: heldout_surface learned_unseen
pair_f1=0.0 on 29 unseen DEV participants, coarse WordNet supersense collapsed wood/oxygen/ash to
the same noun.substance bucket)?

## Prior-work check (substrate_query.sh)
Query: "entity role fate prediction external knowledge generalization unseen entities process
grounding". Top hit cosine=0.3379 (notes/research_drill_substrate_iterative_multihop_3x_2026-06-07,
HotpotQA bridge-entity co-occurrence PREDICTION for multihop QA -- a different mechanism/question,
not entity->fate generalization). No hit above 0.30 addresses this question directly. Also
confirmed on-disk: `experiments/exp_propara_bridging_conceptnet_coparticipation_v1.py` probed
ConceptNet for CO-PARTICIPATION (does an unmentioned entity link to a surface entity mentioned in
text) -- a DIFFERENT question from entity->FATE generalization tested here. Not a duplicate.

## Sources tested (independent arms, no aggregation)
1. WordNet-rich: hypernym chain (depth<=6) + meronym/holonym + topic/usage domain + lexname on
   participant head tokens (nltk.wordnet, same corpus the binder used, richer feature set).
2. ConceptNet-rich: typed KEEP_RELS edges from the local ConceptNet 5.7.0 assertions dump
   (data/conceptnet/conceptnet-assertions-5.7.0.csv.gz), re-scanned into a TRAIN+DEV-scoped index
   (the shipped propara_conceptnet_index_v1.json is DEV+TEST-scoped and misses almost all TRAIN
   participant heads -- checked: wood/ash/lava/log all MISSING; a genuine data-scope gap, not a
   design choice).
3. Offline embedding-rich: GloVe-300d (gensim-cached, offline, no network) cosine similarity from
   participant-head centroid to CREATE/MOVE/DESTROY anchor-word centroids, bucketed.

## Method
Fit TRAIN (391 paragraphs, 1500 (para,participant) keys) -> evaluate DEV (43 paragraphs, 175
keys, 29 surface-unseen) -- same TRAIN->DEV convention the schema binder used (TEST untouched).
One glass-box gam instance (hdlab.learner.plugins.gam_plugin, reused verbatim -- same learner the
binder used) per (para, participant, candidate effect); features = [effect:E] + source features
ONLY (no raw-surface/memorization feature at all, stricter than the binder). Gold labels from
`_oracle_event_multiset` + `_gold_effects_from_multiset` (reused verbatim); DEV gold never touches
features or training.

## Controls
- MAJORITY baseline: constant "predict the single TRAIN-most-frequent effect for every entity"
  (ignores identity; non-degenerate, ~0.40 pair_f1 on all-DEV by construction, shared across
  sources).
- SCRAMBLE: deterministic (hashlib-seeded, F.5-compliant, no python hash()) permutation of the
  TRAIN entity->fate mapping before fitting; must NOT beat majority on held-out-unseen after
  scrambling, or the "signal" is spurious/leaky.

## Bands (per source)
- `LIFT_HARD_PASS = 0.05` (real_unseen_pair_f1 - majority_unseen_pair_f1)
- `LIFT_HARD_FAIL = 0.02`
- `SCRAMBLE_CLEAN_MARGIN = 0.05` (scramble_unseen_pair_f1 <= majority_unseen_pair_f1 + this)
- HARD_PASS_GENERALIZES: lift >= LIFT_HARD_PASS AND scramble_clean
- HARD_FAIL_SCRAMBLE_LEAK: NOT scramble_clean (regardless of lift)
- HARD_FAIL_NO_GENERALIZATION: lift < LIFT_HARD_FAIL (and scramble_clean)
- MIDDLE_BAND: otherwise

## Overall verdict
HARD_PASS if >=1 source HARD_PASS_GENERALIZES (entity-role knowledge externally sourceable, fork
A/B viable). HARD_FAIL if ALL 3 sources HARD_FAIL (knowledge not in these accessible structured
sources -> corpus-scale distributional learning or LLM-scale needed). Else MIDDLE_BAND, reported
honestly per-source (no aggregation to force a binary call).

## Discipline notes
- crlb_n/a: pair-level P/R/F1 vs a majority baseline over a fixed real corpus; no noise-floor
  threshold applies.
- arms_differ_verified: majority vs 6 non-majority arms (3 sources x real/scramble) hash-compared;
  hard-fails only if ALL 6 collapse to majority (total-pipeline-bug guard), soft-logs incidental
  ties otherwise.
- deterministic_seeding: true (`_deterministic_perm` reused from
  exp_propara_decisive_inference_arm1_oracle_v1, hashlib-seeded).
- self-test: REAL WordNet lookup (2 words, differ) + REAL capped ConceptNet gz scan (800K lines,
  real code path) + REAL tiny-scale gam fit/predict (N=12 paragraphs) + MOCK embedding KV only
  (real GloVe load = 115s offline, same mock-KV precedent as
  experiments/exp_encoder_word2vec_substrate_bind_v1.py's own self-test "T7").
- No remote dispatch; no queue_add; runs foreground-to-completion locally (compute-proportionality
  -- this is a diagnostic/go-no-go question, cheapest decisive method: reuse gam_plugin's fast
  counting-based fit, not a heavy training run).

## HP_SCOPE
`{wordnet: [lift_hard_pass_or_fail, scramble_clean], conceptnet: [lift_hard_pass_or_fail,
scramble_clean], embedding: [lift_hard_pass_or_fail, scramble_clean]}` -- majority_baseline arm is
reference-only (no HP gate).
