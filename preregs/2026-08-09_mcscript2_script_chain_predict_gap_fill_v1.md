# Pre-reg: mcscript2_script_chain_predict_gap_fill_v1 (anchor #3 -- the decisive
# genuine-inference-vs-content-matching-ceiling test)

**Filed-by:** exp_dev, 2026-08-09.
**Task:** Director task -- decisive, staged test of the ONLY lever past the MCScript2.0
content-matching ceiling (~0.61, established `data/exp_mcscript2_oracle_clustering_probe_v1/
metrics.json`, `q_a_oracle_upper_bound.oracle_bow_commonsense_acc=0.6180`, `q_b_representation_
fairness.oracle_fhrr_commonsense_acc=0.5507` -- BOTH BoW-cluster and FHRR-structure content-
matching cap around ~0.55-0.62; `scoring_locus_anchor1` separately shows passage's-OWN-content
scoring closes >=80% of the system's gap vs baseline at every pass): does GENUINE SCRIPT-
INFERENCE (SequenceMatrix.chain_predict, seeded from a DEV passage's own last-observed
per-sentence event, queried against a TRAIN-only per-scenario-type script-transition model)
add signal beyond passage-own content-matching, specifically on items where passage-own
content-matching does not confidently resolve?

**Parent anchors (context, not reused code):** `experiments/exp_mcscript2_oracle_clustering_
probe_v1.py` (oracle-routing convention, `context_vector`/`_cos` scoring primitives),
`experiments/exp_mcscript2_real_benchmark_validation_v1.py` (ORIG: `load_split`,
`restrict_to_scenarios`, `compute_majority_answer_id`, `baseline_accuracies`,
`text_overlap_decide`). `notes/exp_dev_handoff_research_brain_fidelity_mcqa_task_shape_
2026-08-09.md` anchor #3 (`exp_mcscript2_script_chain_predict_gap_fill_v1`) is the research
hand-off this pre-reg operationalizes.

## Prior-work check (SUBSTRATE-KB CONCEPT-QUERY, mandatory before authoring)

`bash tools/substrate_query.sh "script inference chain predict situation model MCScript
passage-own content fallback staged scoring"` -- top hit cosine=0.3047 (notes/research_drill_
substrate_novel_concept_formation_2x_2026-06-10.md, "Schank script invention vs script
application", general classical-AI script literature, not a prior CELL). Second hit
cosine=0.2979 (generic "script" concept atom). Neither is a prior implementation of this
chain-predict + staged-fallback design on MCScript2.0 -- genuinely novel cell, not a
rediscovery. All other hits < 0.30.

## CONTRACT (fixed by Director/hand-off, not exp_dev's to loosen)

- Staged scoring: passage-own content-matching PRIMARY, script-chain-inference FALLBACK,
  fallback NEVER overrides a confident primary (Bower/Black/Turner "Partial Copy", not "Full
  Copy").
- Mandatory controls: anti-circularity (TRAIN-only SequenceMatrix construction; DEV instances
  are NEVER bound into any type's S matrix, only queried read-only from their own last-observed
  event) + SCRAMBLE control (deterministic hashlib-seeded per-instance permutation of each
  TRAIN instance's own sentence order before binding, same content distribution, destroyed
  adjacency).
- Mandatory pre-check: chain_predict must be shown to fire + discriminate on a hand-built
  coherent-vs-scrambled toy script sequence BEFORE any HARD-FAIL from the real corpus is
  trusted.
- Report residual-item (primary WRONG) inference accuracy vs chance (0.50).
- Glass-box, no-LLM-at-inference invariant.

## exp_dev autonomy (this pre-reg's operationalization)

**Per-passage event representation:** `context_vector(sentence_text)` (the SAME whole-narrative
BoW bipolar-bundle primitive already measured, Amendment 1 of the parent cells, to dominate the
FHRR (verb,subj,obj) structural representation on this corpus -- gap 0.153 vs 0.028 on the
matched/wrong scenario-discrimination precheck), applied PER-SENTENCE instead of per-passage.
`hdlab.situation_model_accumulate.AccumulateRegister` is deliberately NOT used here: its job is
order-agnostic multi-event bundling for ONE entity (a different functional slot -- see its own
docstring, "Kintsch C-I / Zwaan multi-event indexing" for entity-tracking), whereas
`hdlab.sequence_memory.SequenceMatrix` (`bind_sequence`/`chain_predict`) IS the substrate's
dedicated ORDERED-transition primitive and is the architecturally correct organ for a script's
next-event expectation -- using AccumulateRegister here would be swapping in the wrong-shaped
primitive for the job, not a cost-saving corner-cut. `hdlab/mcscript_extraction.split_sentences`
is reused verbatim for sentence boundaries; `CandidateGenerator`/dependency-parse front end is
NOT invoked (no per-sentence verb/arg extraction) -- this keeps the whole cell BoW/hashlib-only
(seconds, not the ~250s CandidateGenerator front-end cost of the sibling cells), appropriate for
a "coarse but decisive" isolating probe per compute-proportionality, and consistent with the
already-measured finding that structural extraction does not win on this corpus.

**Chain-predict query pattern (reuse of `exp_substrate_native_qa_hotpotqa_v1/v2`'s
`build_sequence_matrix_from_items` precedent):** one shared `SequenceMatrix(n_dim=256)` PER
scenario TYPE (oracle-routed via `inst["scenario"]`, isolating chain-inference from the
keying/clustering problem which is the separate anchor-#4 concern), built by `bind_sequence`-ing
EVERY TRAIN instance of that type's own per-sentence event-vector sequence into the SAME shared
matrix (accumulating a "typical transition" structure across many tellings, exactly the
hotpotqa cells' "write pairs from many items into one shared S" pattern). At DEV time: k_start =
the DEV passage's OWN last-sentence event vector (never added to any TRAIN matrix);
`chain_predict(k_start, depth=3, codebook=None)` (depth=1 is the pre-registered PRIMARY-fallback
gate below; depths 2-3 are logged as non-gating bonus diagnostics). Candidate answers scored by
`cos(context_vector(answer_text), predicted_vector)`.

**Primary-doesn't-resolve threshold:** `PRIMARY_MARGIN_THRESH = 0.02` -- `|score_0 - score_1| <
0.02` on the passage-own primary (dominant case: both scores exactly 0.0, i.e. neither
candidate shares a content word with the narrative) triggers the fallback consult. Below-margin
ties where the fallback ALSO fails to discriminate fall through to the primary's own (weak)
argmax -- never "no answer".

**Bands (PRE-REGISTERED, using the Director's suggested numbers verbatim):**
- **HARD-PASS**: `staged_accuracy - primary_only_accuracy >= +0.02` on full commonsense DEV,
  AND `fallback_accuracy_on_residual > 0.55` (residual = items where primary_pred != correct,
  post-hoc diagnostic set, NOT the deployed margin-gate), AND REAL residual-fallback-accuracy
  edge-over-chance (`acc - 0.50`) > SCRAMBLE residual-fallback-accuracy edge-over-chance.
- **HARD-FAIL**: `staged_accuracy - primary_only_accuracy <= 0`, OR
  `0.45 <= fallback_accuracy_on_residual <= 0.55` (chance-level), OR REAL edge <= SCRAMBLE edge.
  If the mandatory pre-check did NOT fire+discriminate on the toy sequence, ANY HARD-FAIL is
  relabeled `HARD_FAIL_UNTRUSTED_PRECHECK_FAILED` (verdict withheld pending a chain_predict
  wiring fix) rather than accepted as a genuine negative.
- **MIDDLE_BAND**: everything else.
- Honest scope (carried from the hand-off): a HARD-FAIL here means "script-inference gap-filling
  adds negligible signal over passage-grounded scoring on THIS corpus specifically" (TEXT_OVERLAP
  /content-matching is unusually strong on this lexically-grounded corpus) -- NOT a general
  refutation of chain-based script inference (independent positive precedent:
  `exp_substrate_native_qa_hotpotqa_v1`/`v2`).

## Compute architecture

Sequential-CPU, justified: (b) is a hashlib-seeded deterministic BoW-vector build + torch
outer-product accumulation over ~2500 TRAIN / 355 DEV short narratives (~6 sentences each);
`SequenceMatrix` ops are 256x256 outer-products (matmul-trivial at this N_DIM, no GPU-batching
candidate -- (c) also: this cell IS composed of already chain-grade-certified primitives, not a
fresh large matmul sweep). No CandidateGenerator front end invoked (BoW-only). Estimated wall
<60s total for the FULL run (no parser load, no multi-pass consolidation loop -- one-shot
per-type matrix accumulation). Single INLINE-LOCAL foreground run; no push/remote-persist
authorized for this task ("Local if light" per Director).

## Determinism / anti-circularity / no-padding

- `deterministic_seeding: true` -- hashlib-only (context_vector, the scramble permutation),
  `sorted(..., key=lambda x: x["id"])` for all TRAIN/DEV iteration order, no `hash()`, no
  `list(set())`.
- Anti-circularity: DEV instances are NEVER bound into any TRAIN type's SequenceMatrix; only
  read via `chain_predict` (S is never mutated by a DEV query).
- SCRAMBLE arm uses the SAME per-instance sentence-vectors as REAL, only their WITHIN-INSTANCE
  bind order is permuted (hashlib-seeded on instance id) -- isolates "is it the ORDER structure"
  from "is it just more/different content in S".
- No filler: this is the single decisive probe the Director requested; a HARD-FAIL is reported
  as a valuable, honest negative (content-matching ceiling confirmed), not hidden or re-run
  fishing for a different result.

## Self-test / smoke / full

- `--self-test`: (1) `precheck_chain_predict_toy()` -- hand-built 4-step coherent script vs
  hashlib-permuted scramble, 40 noisy repeats each, asserts chain_predict's real-order
  prediction is closer to the true next symbol than the scrambled-order prediction AND clears
  an absolute floor (>0.30 cosine); exercises real `SequenceMatrix.bind_sequence`/
  `chain_predict` at production `n_dim=256`. (2) tiny 2-scenario/12-TRAIN/2-DEV toy corpus
  exercising `build_type_sequence_matrices`, `compute_arm`, `build_commonsense_questions`,
  `compute_primary` end-to-end at N~12, real code path per SCHEMA-VET F.1.
- `--smoke`: first 20 TRAIN/DEV scenarios (mirrors sibling cells' smoke convention) at FULL
  representation fidelity (same `n_dim=256`, same margin/band thresholds) -- DISCRIMINATOR-
  MUST-SURVIVE-SCALE option (A): smoke regime differs only in scenario COUNT, not in any
  parameter the mechanism's tolerance scales with.
- full: all 2500 TRAIN / 355 DEV (966 commonsense questions), single foreground run,
  `final_metrics_atomicity: tmp_replace`, resumable per-arm (`real`/`scramble`) via
  `experiments._seed_checkpoint`.

## CELL-TEMPLATE MANDATORY checklist (subset applied to this cell's shape)

- `arms_differ_verified`: real vs scramble arm result-tuples hashed distinct.
- `cardinality_ok`: `len(per_arm) == 2` (real, scramble).
- `except SystemExit: raise` before `except Exception` (no bare except, no BaseException).
- `final_metrics_atomicity: tmp_replace` (+ per-arm partial checkpoints, resumable).
- `crlb_n_a`: content-matching + chain-prediction cosine-scoring cell; no argmax/top-k
  associative-recall capacity ceiling applies.
- `calibration_check: adaptive_with_discriminator_gate` -- `PRIMARY_MARGIN_THRESH` is a fixed,
  pre-registered constant (not tuned post-hoc); the mandatory toy pre-check is the discriminator-
  fires gate for the chain_predict mechanism specifically.
- All numbers in the cell's docstring/comments tagged MEASURED@ / HYPOTHESIZED@ / CITED@.
- ASCII-only; no unicode; no emojis.
