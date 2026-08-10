# Pre-reg: exp_wiqa_causal_chain_learned_signs_v1

Filed by: exp_dev (Sonnet, foreground, no nested sub-agents, no queue dispatch -- CPU-only
glass-box text processing on the real WIQA train/dev/test splits, per Director's task Contract,
run FOREGROUND TO COMPLETION locally, no queue_add). All bands/thresholds below are fixed in
`experiments/exp_wiqa_causal_chain_learned_signs_v1.py` BEFORE the full-dev run executes -- no
post-hoc tuning against observed numbers (same discipline as v1/v2/oracle_structure).

## Prior-work check (mandatory, 2026-07-01 USER-locked)

`bash tools/substrate_query.sh "learned glass-box edge polarity classifier causal composition
WIQA multihop hdlab learner MDL"` -> top hits are generic concept-KB atoms (`entity='learner'`
cosine=0.3809, `entity='learned'` cosine=0.3467 -- WordNet/VerbNet-level lexical entries, not
prior experiment cells) and, below the 0.30 novelty threshold, `learned_role_assigner_reader_
composition_v3` (cosine=0.2715, `preregs/reader_composition_cg_revival_v3.md` -- a DIFFERENT
domain: reader-composition role assignment, not WIQA edge-polarity). **Prior-work check verdict:
NOVEL** -- no prior WIQA-learned-edge-sign cell exists at cosine>0.30.

## Question (Director task, standing rule b: missing-LEARNING -> reuse/expand hdlab/learner)

Every prior WIQA causal-chain-loop attempt (`exp_wiqa_causal_chain_loop_v1/v2`,
`exp_wiqa_causal_chain_oracle_structure_v1`, all HARD_FAIL/MIDDLE_BAND) extracted per-edge
polarity with a HAND-WRITTEN regex lexicon (`has_negating_word`, checked only against the
downstream step's text). This cell tests the MISSING-LEARNING hypothesis: can `hdlab/learner`
(the centralized MDL model-selection engine) instead LEARN a glass-box edge-polarity classifier
from WIQA's own official gold-explanation TRAIN split, and does composing those LEARNED signs
through the SAME `propagate_sign` chain-composition loop beat the baselines on a LEAK-SAFE
MULTI-HOP held-out DEV subset?

## Supervision source + leak-safety design (VET section, mandatory -- read before trusting HARD_PASS)

WIQA's official EMNLP-2019 "with_explanation" release exists for all three splits (`train.jsonl`
2,3023 records / `test.jsonl` 2,471 / `dev.jsonl` 5,005 -- same S3 bucket `oracle_structure_v1`
already vetted for dev; this cell additionally downloads train/test, cached at
`data/corpora/wiqa/raw_official/{train,test}_with_expl.jsonl`). MEASURED this session: `train`
and `test` and `dev` official `para_id` sets are PAIRWISE DISJOINT (0/0/0 overlap) -- no
paragraph-level cross-split leakage is possible.

Each record's `explanation.dj` (RESULTS_IN / RESULTS_IN_OPP / NO_EFFECT) is WIQA's own net-effect
judgement of X on Y over the WHOLE (i,j) span -- CITED@oracle_structure_v1's own leak-check:
`dj` reproduces `answer_label` at 5005/5005=1.0000 on dev, at EVERY hop distance (this is
definitional, not hop-specific: `dj` IS the composite path label). Consequences for this cell's
design:

1. `dj` can **never** be used as an edge-level label for a multi-hop (hop>=2) item -- it is the
   COMPOSITE label, not a per-edge one. This cell only reads `dj` for hop=1 (`|i-j|==1`) records,
   where the path IS a single edge, so the composite label mechanically coincides with that one
   edge's own polarity -- a legitimate, non-circular supervision source for THAT record.
2. The DECISIVE evaluation (see Bands) is restricted to DEV `oracle_covered_multihop`
   (gold-anchor-covered AND hop>=2) and always compares composed PREDICTIONS to `answer_label`,
   never to `dj`. TRAIN/TEST hop=1 supervision and DEV hop>=2 evaluation are drawn from disjoint
   official splits with 0 paragraph overlap (MEASURED above) -- no item-level leak is possible
   either.
3. `dj_leak_check_by_hop()` (self-test + full run) reconfirms, on a real DEV sample, that the
   `dj`->`answer_label` identity holds UNIFORMLY across hop buckets (`hop_le_1` and `hop_ge_2`
   both expected ~1.0) -- documenting numerically WHY `dj` stays excluded from decisive scoring
   at every hop, not merely hop<=1.
4. **Director's specific ask** ("confirm the per-edge sign target does NOT trivially reproduce
   the multi-hop answer ... if a single edge's sign predicts the multi-hop answer >~0.9 ...
   exclude") is operationalized mechanistically by `leak_check_single_edge()`: for every
   `oracle_covered_multihop` DEV item, isolate the LEARNED classifier's first (resp. last) edge
   of the gold path (force every other edge to neutral sign=+1) and check whether that ONE edge's
   solo-composed prediction alone already reproduces `answer_label`. `leak_match_rate` = max of
   the two endpoint match rates; the HARD_PASS gate is refused if
   `leak_match_rate >= LEAK_MATCH_RATE_THRESH=0.9`.

## Edge-pool construction + classifier

`build_edge_pool(split)`: TRAIN/TEST hop=1 records with a valid in-bounds gold anchor and
`dj in {RESULTS_IN, RESULTS_IN_OPP}` (excludes `NO_EFFECT` -- `CausalLinkRegister.add_causal_link`
only accepts polarity in {+1,-1}, matching the hand-rule mechanism's own binary output), DEDUPED
by `(para_id, lo, hi)` taking the majority `dj`-class over duplicate `graph_id` variants of the
SAME physical adjacent-step edge (MEASURED this session: train hop=1 raw=5096 records -> 503
unique deduped edges, class balance {neg:258,pos:245}; test hop=1 raw -> 68 unique deduped edges,
{neg:40,pos:28}). Features per edge = stemmed content words of step_i (`i:word`) and step_j
(`j:word`) (Director's pointer: text of step_i + step_j, glass-box/inspectable -- richer than the
hand-rule's step_j-only lexicon by design).

`fit_edge_classifier()` calls `hdlab.learner.registry.learn()` with `candidate_plugins=["ruleind",
"estimation", "gam"]` (MDL two-part-code auto-select across three real hypothesis classes: MDL
rule-conjunction search / frequency-key lookup / additive graded log-odds). `proginduction`
(PLUGIN 4) is deliberately excluded -- it searches a bounded boolean DSL over a small set of
NAMED predicates (shape mismatch for an open sparse vocabulary of hundreds of content-word
features); the other three all natively accept `feat_fn(inst)->iterable[str]`. All plugin
hyperparameters are each plugin's own MODULE DEFAULTS (`calibration_check:
default_ok_for_this_regime`) -- not tuned against dev numbers.

`build_register_learned()`: same edge topology as v2's `build_register` (edge i->i+1 for every
adjacent step pair), polarity from the fitted classifier instead of `has_negating_word`. The
scramble control (`check_order`) permutes ONLY which step's text feeds the downstream/j-side of
the pair feature (cause-side i stays true) -- the direct generalization of v1/v2/oracle's own
scramble scheme.

## Arms (all subsets)

majority, polecho, bow, `loop_hand_rule` (= oracle_structure_v1's `score_item_oracle`, gold
anchors + the UNCHANGED regex hand-rule -- reused verbatim, not re-implemented, as the "old
mechanism, reference"), `loop_learned` (gold anchors + the LEARNED classifier -- the new arm,
ONE-VARIABLE-CHANGED from `loop_hand_rule`: same anchor source, different edge-sign source),
`loop_learned_scramble` (learned-sign-scramble control, median of 3 seeds [7,17,29]).

Both loop arms use WIQA's own gold `(i,j)` anchors (from `oracle_structure_v1.load_gold_map`/
`gold_lookup`, reused unchanged) -- this isolates the ONE variable Director asked about
(edge-sign source: hand-rule vs learned) rather than conflating it with the already-separately-
tested anchor-retrieval question (`oracle_structure_v1` HARD_FAILed on that axis independently).

## Subsets

- **all** (n=6894) / **oracle_covered** (n MEASURED=2893): context only, reported but not gating
  (oracle_covered includes hop<=1 items, which are individually leak-adjacent per the dj-identity
  discussion above -- not appropriate as the decisive gate).
- **oracle_covered_multihop** (n MEASURED=996, gold-covered AND `|j-i|>=2`): **PRIMARY decisive
  subset** per Director's explicit framing ("restrict the decisive evaluation to the LEAK-SAFE
  MULTI-HOP held-out DEV subset").

## Pre-reg bands (Director's task contract)

Evaluated on `oracle_covered_multihop` (primary), gates checked in this order (first failing
gate determines the HARD_FAIL reason):

1. `learner_fit_ok`: chosen plugin != `KEEP_EPISODIC` (some candidate plugin compressed the
   TRAIN edge pool past the null code). Fails -> **HARD_FAIL** (`LEARNER_COULD_NOT_FIT`).
2. `leak_safe`: `leak_match_rate < LEAK_MATCH_RATE_THRESH=0.9`. Fails -> **HARD_FAIL**
   (`LEAK_DETECTED`).
3. `generalizes`: held-out TEST-split edge accuracy `edge_test_acc >=
   EDGE_GENERALIZATION_THRESH=0.60` (binary pos/neg chance=0.5; HYPOTHESIZED@this cell: "chance +
   0.10" as "meaningfully above chance") AND `edge_test_n >= MIN_EDGE_DEV_N=20`. Fails ->
   **HARD_FAIL** (`LEARNER_DOES_NOT_GENERALIZE`).
4. `beats_all_3_baselines`: `loop_learned` beats majority AND polecho AND bow each by
   `>= DECISIVE_MARGIN=0.05` on `oracle_covered_multihop`. Fails -> **HARD_FAIL**
   (`DOES_NOT_BEAT_BASELINES`).
5. `scramble_collapses`: `collapse_frac = (loop_learned - loop_learned_scramble_median) /
   (loop_learned - polecho) >= DECISIVE_COLLAPSE_FRACTION=0.5`. Fails -> **MIDDLE_BAND**
   (`BEATS_BASELINES_BUT_GAIN_NOT_CAUSAL`); passes all 5 -> **HARD_PASS**
   (`LEARNED_SIGNS_RESCUE_THE_LOOP`).

`arms_differ_verified` (6-arm hash-differ: majority/polecho/bow/loop_hand_rule/loop_learned/
loop_learned_scramble) overrides any tier to HARD_FAIL if arms collapse to identical predictions
(META_RULE_AF).

## Controls (Director-mandated)

1. **Learned-sign-scramble** (gate 5 above): loop gain over polecho must collapse >=50% under the
   scramble, or the gain is topological/structural not genuinely edge-content-driven.
2. **Generalization** (gate 3): learner TRAIN acc (on the 503-edge TRAIN pool) vs held-out TEST
   acc (68-edge, official TEST split, never touched by TRAIN fitting or DEV evaluation) reported
   side-by-side, not just TRAIN acc alone -- catches pure memorization.
3. **Leak-check** (gate 2): `leak_check_single_edge` + `dj_leak_check_by_hop`, both reported
   numerically in metrics.json (not just asserted).

## SCHEMA-VET fields

`arms_differ_verified` (6 arms), `final_metrics_atomicity=tmp_replace` (via
`_seed_checkpoint.write_metrics`), no bare `except:`/`except BaseException:` (grep-verified
clean), `crlb_n/a` declared (discrete classification accuracy, no capacity/noise-floor
threshold), `cardinality_ok` (`EXPECTED_N_UNITS=len(SEEDS_FULL)=3`), per-unit failure-class
instrumentation (`DEGRADED_BUDGET=0.02`), `calibration_check=default_ok_for_this_regime`
(plugin module defaults, GATE_THRESH/lexicon unchanged from v2), `deterministic_seeding=true`
(hashlib-based `_deterministic_perm`, `sorted()` not `hash()`/`list(set())` for pool
construction -- grep-verified), `progress_logging=print_flush_true`,
`real_code_path_and_signature_preflight` (self-test constructs the REAL `CausalLinkRegister` +
the REAL `hdlab.learner.registry.learn()` end-to-end at N=16-20 synthetic episodes + loads a real
sample of the official train/dev releases; binds `CausalLinkRegister.__init__`/`.add_causal_link`
and `learner_registry.learn`/`ruleind_plugin.learn`/`estimation_plugin.learn`/`gam_plugin.learn`
against `inspect.signature`).

Self-test additions specific to this cell: `_hand_case_pool_dedup` (hand-built raw records verify
dedup+majority-vote grouping), `_hand_case_classifier_fit_and_apply` (REAL
`hdlab.learner.registry.learn()` call on a clear-signal N=20 synthetic pool, verifies correct
generalization to unseen probe words), `_hand_case_register_learned_sign_flip` (hand-built 3-step
chain + a hand-fitted classifier, verifies `build_register_learned`+`propagate_sign` compose
correctly through the REAL `CausalLinkRegister`), `_hand_case_leak_check_logic` (contrived rows
verify `leak_check_single_edge`'s arithmetic on both a leaky and a non-leaky case).

## Results (MEASURED, full dev, 6894 items, 3 seeds [7,17,29], elapsed_s=16.003)

**Classifier fit:** `hdlab.learner.registry.learn()` auto-selected **ruleind** (MDL two-part-code
compression_ratio marginally >1.0; estimation and gam both scored compression_ratio<1.0 on this
pool and were correctly refused by `per_cluster_gate`) -- `n_rules=2`, `n_episodic=464` (of 503
TRAIN edges). **Generalization control (gate 3): `edge_train_acc=0.9821` (n=503) vs
`edge_test_acc=0.4118` (n=68, official TEST split, never touched by fitting or DEV evaluation)** --
severe overfitting. Root cause (diagnosed, not just observed): only 2 of 503 edges are covered by
genuine word-conjunction RULES; the remaining 464 are memorized in the `residual_lookup`
(exact-full-feature-set-match episodic table), which -- exactly as `ruleind_plugin`'s own
docstring predicts ("on a verb-disjoint held-out split this cannot exact-match by construction")
-- essentially never fires on held-out paragraphs. The classifier therefore defaults to
`default_class="pos"` for nearly every held-out edge; TEST split is 28 pos / 40 neg, so
"always-pos" scores ~28/68=0.4118 -- **matches the measured number exactly**, confirming the
classifier degenerated to a constant predictor on unseen text, materially WORSE than TEST's own
40/68=0.588 majority-class floor.

| subset | n | majority | polecho | bow | loop_hand_rule | loop_learned | scramble (median/3) | learned-polecho | collapse_frac |
|---|---|---|---|---|---|---|---|---|---|
| all | 6894 | 0.3333 | 0.3420 | 0.3281 | 0.3567 | 0.3541 | 0.3541 | +0.0120 | n/a (scramble==learned) |
| oracle_covered | 2893 | 0.5064 | 0.4075 | 0.4673 | 0.4424 | 0.4362 | 0.4362 | +0.0287 | n/a |
| **oracle_covered_multihop (primary)** | **996** | **0.5100** | **0.4137** | **0.4578** | **0.4588** | **0.4458** | **0.4428** | **+0.0321** | **0.094** |

**Leak checks (both clean):** `leak_check_single_edge` (Director-mandated): n=457 multihop items
with a fired learned edge-sign, `first_edge_match_rate=0.5295`, `last_edge_match_rate=0.5208`,
headline `leak_match_rate=0.5295` -- **well below `LEAK_MATCH_RATE_THRESH=0.9`**, confirming the
multihop subset genuinely requires multi-edge composition (no single edge dominates).
`dj_leak_check_by_hop`: `hop_le_1` 1897/1897=1.0000, `hop_ge_2` 996/996=1.0000 -- reconfirms `dj`
IS the answer at every hop distance (definitional), which is exactly why decisive scoring never
reads `dj` and instead always compares composed predictions to `answer_label`.

**Verdict: HARD_FAIL / `LEARNER_DOES_NOT_GENERALIZE`** (gate 3 of 5, the FIRST failing gate in
pre-registered order -- gates 4 and 5 were also independently checked and ALSO would have failed:
`beats_all_3_baselines=False` -- `loop_learned=0.4458` loses to majority (`-0.0643`) and to bow
(`-0.0120`), only beats polecho by `+0.0321` (below the `0.05` margin); `scramble_collapses=False`
-- `collapse_frac=0.094`, far below `0.5`, the SAME "topology not causality" signature v1/v2/
oracle_structure all found for the hand-rule mechanism). `loop_learned` vs `loop_hand_rule`
(reference): `-0.0131` on the primary subset -- the LEARNED classifier is (slightly) WORSE than
the fixed hand-written regex lexicon, not better.

**Honest reading (missing-learning hypothesis: REFUTED for this configuration).** The most basic
gate failed first: on 503 real training edges (deduped, non-trivial: 245/258 class balance), the
CENTRALIZED `hdlab/learner` MDL auto-select picked a hypothesis that memorizes rather than
generalizes -- a genuine, diagnosed (not hand-waved) failure mode: two-part-code compression
measured ONLY on the training pool cannot distinguish "genuinely predictive rule" from "exact-key
memorization that happens to cost few bits on data it was fit to," and `ruleind`'s residual/
episodic fallback is architecturally exactly this trap on small, lexically sparse pools. This is
NOT the same failure as prior WIQA cells (which failed at the COMPOSITION/extraction-approach
level, with hand-rule signs that never overfit because they were never fit at all) -- it is a
NEW, DEEPER finding: the standing rule's premise ("missing LEARNING -> reuse hdlab/learner") is
directionally right (the module IS usable end-to-end on this task, self-test proves it: coverage-
satisfying synthetic pools DO fit and generalize correctly to novel probe words), but the
REAL WIQA TRAIN edge-pool (503 unique adjacent-step edges from 261 paragraphs) is too small and
lexically sparse for the auto-selected hypothesis class to escape memorization on THIS pool size,
with THESE default hyperparameters. Even setting generalization aside as a hypothetical (gate 3
overridden), the downstream composition still would not have cleared gates 4/5 -- so even a
perfectly-generalizing learned classifier is not guaranteed to rescue the composition mechanism,
consistent with the oracle_structure_v1 finding that GOLD-anchor + hand-rule signs already lose to
majority on this exact subset. Decisively answers the Director's honest-negative framing: a clean
HARD_FAIL with full leak/generalization diagnostics, not an engineered collapse.
