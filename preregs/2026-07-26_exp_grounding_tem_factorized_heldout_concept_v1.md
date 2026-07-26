# Pre-registration: exp_grounding_tem_factorized_heldout_concept_v1

**Design-of-record (the contract):** `notes/research_structure_content_factorization_generalizing_meaning_2026-07-26.md`
**Filed by:** hdi_exp_dev. **LOCAL-only, no push. Do NOT bank (skunkworks VETs on the generalization bar).**

## Question (classify: CAPABILITY / structural)
Does a TRAINED, content-blind structural code `g(relation_type, slot)` (TEM structure/content
factorization) let the substrate GENERALIZE meaning to concepts NEVER seen in training -- the one
mechanism 29556 (entangled MLP, `ho_lift=0`) and 29557 (fixed-random role, never trained) skipped?

This is a CAPABILITY / magnitude claim about the exact substrate mechanism on the real WorldTree
corpus, so a real train-and-measure fit is proportionate (NOT a light directional gate).

## Load-bearing brain-true constraints (violation = void test)
1. `g(relation-type, slot)` is trained ONLY on (relation-type name, argument-slot index). It NEVER
   sees / is conditioned on filler or concept identity. Content-blindness is the entire brain-true
   claim; if g saw the filler it could memorize and the test would be void.
2. Content `x(concept)`: PRIMARY/DECISIVE arm = RANDOM-ID unit vector per concept (zero pretrained
   semantics). NO GloVe/word2vec/BERT/any distributional embedding as content, ever. Binder-2016
   experiential norms = SECONDARY ablation arm only (expected to add little).
3. `g` trained via contrastive INVARIANCE (same (relation,slot) across different fillers -> pull
   together) + DISTINCTNESS (different (relation,slot) -> push apart) across the WorldTree corpus.
   Fillers are represented content-blindly as feature-perturbation views of the relation-name code;
   g never receives a concept vector.
4. SUCCESS = held-out-to-NEW-CONCEPT generalization (Split A) + held-out role-combos (Split B),
   top-1/top-10 retrieval. MEMORIZING = HARD-FAIL, not a win.

## Substrate + reuse
- Real WorldTree typed-relation tables (`data/corpora/worldtree/.../tablestore/v2.1/tables/`), a
  curated set of ~15 clean binary-relation tables (KINDOF 2137, SYNONYMY 1232, CAUSE 381, PARTOF 236,
  MADEOF 221, REQUIRES 216, SOURCEOF 179, CONTAINS 169, LOCATIONS 155, EXAMPLES 104, AFFORDANCES 103,
  OPPOSITES 66, HABITAT 45, PREDATOR-PREY 14, PROP-CHEM-ELEMSYMB 18, INSTANCES 40) -- each row parsed
  to a typed triple (relation_type, slot0_filler, slot1_filler) via an explicit per-table slot map.
- REUSE VERBATIM: `hdlab/binding.py::bind/unbind` (HRR circular convolution over REAL unit vectors --
  content dtype is real; single representation, no 3rd added). `char_trigram_features` / `ProjHead` /
  `info_nce` / `vicreg_repulsion` pattern copied verbatim (with attribution) from
  `experiments/exp_teacher_free_relational_encoder_cn_subgraph_v1.py`. `data/corpora/binder/binder2016_ratings.csv`
  for the SECONDARY arm.

## Mechanism (glass-box, two representations separate from the start)
- Content `x(concept)`: RANDOM-ID (primary) = fixed random Gaussian unit vector per concept;
  BINDER-GROUNDED (secondary) = Binder-2016 65-attribute vector projected to N with random-ID fallback.
- Structure `g(relation,slot)`: `ProjHead(char_trigram(relation_name) ++ onehot(slot)) -> N`,
  L2-normed. Trained by supervised-contrastive over (relation,slot) labels: two perturbation views
  per item -> info_nce (invariance) + vicreg_repulsion (distinctness). Content-blind by construction.
- Bind: `p = bind(g(relation,slot), x(concept))` (HRR).
- Sharded associative memory (SHARDED per META_STORAGE_STRATEGY -- this is a compositional multi-hop
  cell; NOT bundled): one trace per fact `T_i = bind(g[r,0],x_A) + bind(g[r,1],x_B)`.
- Retrieve tail given (relation, head): probe `= bind(g[r,0], x_head)`; select fact `i*` = argmax
  cosine(probe, traces); unbind tail `x_hat = unbind(T_i*, g[r,1])`; cleanup vs concept dictionary
  (includes held-out concepts as valid answers) -> top-1/top-10.
- Multi-hop: X --r1--> Y, Y --r2--> Z; hop2 query content = hop1 RETRIEVED concept. Bridge/tail novel.

## Arms (paired; identical corpus + splits + seeds; only the encoder/mechanism differs)
- `FLAT` -- reproduces 29556: `MLP(concat(x, relation-onehot)) -> predicted x_tail`, cleanup.
  Single-hop. Expected `ho_lift ~ 0` on novel content (cannot emit an unseen content vector).
- `SINGLE_HOP_RANDOM_BIND` -- reproduces 29557: fixed-RANDOM g per (relation,slot), single-hop bind.
- `FACTORIZED_G` -- TEM-style trained-invariant g; single-hop AND 2+-hop; Splits A and B.
- Must-fail controls (all four must collapse to chance/base-rate floor):
  - `SHUFFLED_STRUCTURE` -- permute which concept fills which slot across facts.
  - `SCRAMBLED_ROLES` -- permute relation-type labels across rows (train g against WRONG identity).
  - `RANDOM_G` -- identical bind/retrieval pipeline but g randomized (isolates whether LEARNED
    invariance, not merely having a tag, does the work).
  - `CONTENT_SCRAMBLED` -- x(concept) vectors permuted across identities (must collapse to chance).

## Primary metric + splits
- Split A (primary, decisive): HELD-OUT NEW CONCEPTS -- concept set partitioned SEEN/NOVEL; training
  memory + FLAT-MLP fit use SEEN-only facts; NOVEL concepts introduced ONLY at test via their edges
  with FROZEN g. Report single-hop novel-content top-1/top-10 (all arms comparable) AND
  FACTORIZED_G 2-hop composition (answer never stored, bridge NOVEL).
- Split B (secondary): HELD-OUT ROLE-COMBINATIONS -- a concept seen in some relations withheld from
  one relation-type/slot.
- Reported: top-1 (and top-10) nearest-neighbor-cleanup retrieval on held-out queries vs a full
  concept dictionary that includes held-out concepts as valid answers.

## Learning-curve diagnostic
Held-out top-1 vs number of distinct relation-TYPES receiving distinctness training in g (per Saxe
2019 diversity-drives-differentiation). Monotone-increasing predicted; flat/non-monotone = disqualifying.

## Pre-registered bands
- **HARD_PASS:** FACTORIZED_G held-out (pooled Split A+B, on 2+-hop chains) top-1 clears FLAT by
  >= 15-20pp AND clears SINGLE_HOP_RANDOM_BIND by a clear separately-reported margin AND all four
  must-fail controls collapse to within noise of the chance/base-rate floor AND a positive
  (monotone-increasing) learning curve. (strictly above floor + 5% band-width per META_RULE_L.)
- **HARD_FAIL:** FACTORIZED_G ties FLAT and/or SINGLE_HOP_RANDOM_BIND on held-out (within ~5pp) OR
  any must-fail control fails to collapse (construction/leakage bug -> respec, NOT a mechanism
  refutation) OR the learning curve is flat/non-monotonic.
- **MIDDLE_BAND:** FACTORIZED_G clears FLAT by 5-15pp with controls holding, OR clears the accuracy
  bar but Binder-grounded content adds nothing over random-ID (expected, informative:
  "structure carries generalization, content-richness does not").

## Discriminator-fires self-test (mechanism CAN fire)
Planted clean-factorizable synthetic graph at small N with many relation types where random g
accidentally collides: assert trained FACTORIZED_G held-out retrieval > RANDOM_G held-out retrieval
by a clear margin (trained-g generalizes; RANDOM_G does not). If the instrument cannot make trained-g
beat random-g on a clean planted graph, the discriminator is vacuous -> STOP, do not dispatch.

## SCHEMA-VET / cell-template fields
- `arms_differ_verified: true` (hash-test at smoke; SHUFFLED/SCRAMBLED/RANDOM/CONTENT vs FACTORIZED)
- `final_metrics_atomicity: tmp_replace`
- `except SystemExit: raise` BEFORE `except Exception` (no BaseException; no bare except)
- `crlb_n/a: "retrieval-accuracy discriminator; chance floor = 1/n_concept_dictionary computed and
  reported as base_rate_floor; no Gaussian noise CRLB applies"`
- `discriminator_reachability: true` (planted self-test shows trained-g > random-g reachable)
- `baseline_in_band: true` (FLAT novel-content accuracy expected ~chance, well below 0.95; smoke
  verifies 0.05 < mechanism band; FLAT-at-floor is the intended memorizing baseline, exempted from
  the >0.05 lower gate as a known-floor baseline)
- `HP_SCOPE: {FACTORIZED_G: [beats_FLAT_15pp, beats_random_bind, controls_collapse, positive_curve]}`
  (controls + FLAT + random-bind are NOT held to the FACTORIZED_G HP gates)
- `cardinality_ok: true` -- EXPECTED_N_UNITS = n_seeds * n_arms (+ learning-curve points); verdict
  logic counts per-arm units and emits HARD_FAIL_CARDINALITY_BREACH if short.
- `per-unit failure-class instrumentation: true` (specific except classes, failure_class field)
- `calibration_check: "default_ok_for_this_regime"` -- retrieval/cleanup are parameter-free
  (cosine + argmax); no tunable threshold.
- Compute architecture: **sequential-CPU with justification** -- multi-hop chained retrieval has a
  genuine sequential dependency (hop N depends on hop N-1); models are small; binds are batched via
  torch.fft; wall-time target < 10 min FULL foreground. Storage strategy: **SHARDED**.
- `cell_chunked: false` (single-file; seeds looped in one process, each seed self-contained + logged)
- `start_marker_written: true`, `crash_diagnostic_present: true`, `heartbeat_present: true`,
  `defensive_error_checking: "passed_all_4_patterns"`
- `progress_logging: "print_flush_true"` (sys.stdout line-buffered + flush on progress lines)
- `deterministic_seeding: true` -- fixed integer seeds, `sorted(set())`, blake2b/sha256 only; no
  builtin `hash()`-seeded RNG, no `list(set())` ordering.
- Gate B `discriminating_fraction`: FLAT novel-content ~ chance (floor) BY DESIGN as the memorizing
  baseline; the DISCRIMINATING axis is the learning-curve (relation-type diversity), predicted to
  span floor->above-floor; >= 3 of 5 curve points predicted in a discriminating band.
- Gate F real_code_path: self-test constructs + calls `hdlab.binding.bind/unbind` at N~64 and asserts
  the batched cell binder is bit-close to the reference primitive. substrate_signature: binds bind/unbind.

## HYPOTHESIZED vs MEASURED (all numbers below are HYPOTHESIZED / CITED, none measured yet)
- FLAT novel-content top-1: ~ base-rate floor  HYPOTHESIZED@this prereg (29556 `ho_lift=0` analog)
- 29556 `ho_lift`: 0.0  MEASURED@data/exp_learned_meaning_frontend_differentiation_v1/metrics.json
- 29557 `shuffle_sep`: 0.111  MEASURED@data/exp_native_binding_compositional_generalization_v1/metrics.json
- P(HARD_PASS): 0.18  CITED@notes/research_structure_content_factorization_generalizing_meaning_2026-07-26.md
