# Pre-reg: construction->integration relation-inference (2026-08-03)

## Origin
Synthesized per `notes/research_synthesis_brain_fidelity_gap_event_prediction_relation_inference_2026-08-03.md`
(fidelity-gap root cause across 4 negatives: grading a Kintsch CONSTRUCTION-stage mechanism as if it
were a first-pass classifier) + `notes/research_drill_biology_led_unstated_goal_inference_inverse_planning_2026-08-03.md`
(inverse-planning candidate scoring for the goal axis). This is a re-purposing (pure reuse of the
MECHANISM SHAPE: overgenerate loose candidates -> coherence-filter picks), not a 5th predictor.

## Scope decision (MINIMAL VIABLE, stated up front, not hidden)
The two source docs recommend literally re-wiring the existing `exp_event_level_sr_td_contrastive_...`
predictor, `hdlab/situation_model_accumulate.py`'s `CausalLinkRegister`, and
`exp_theory_of_mind_sally_anne_nested_hrr_v1`'s per-agent bank. Those modules operate over a SINGLE
narrative's accumulated event/entity register built by an ingestion pipeline; the 25-item gold eval
(`data/eval_gold_mention_role_mcguffey_v1/gold_relation_inference_v1.jsonl`) is ISOLATED cross-novel
snippets with no accumulated register behind them. Literally importing those classes would require
first building a full per-item chapter-ingestion harness -- out of scope for this pass and exactly the
"context-stripped" caveat the task asks to report on, not to silently paper over.
**Decision: reuse the PRIMITIVE SHAPE (bind=elementwise complex multiply, bundle=sum+normalize,
cleanup=cosine-argmax, refuse-gate=margin-over-runner-up) and the CONSTRUCTION -> INTEGRATION
architecture pattern (Kintsch: loose overgenerate -> coherence-filter pick), freshly instantiated for
this eval's item shape.** No new learning machinery (no gradient-trained map, no borrowed embedding);
all vectors are the same hash-seeded random-phase FHRR word-vectors already used elsewhere in this
project's cells. Flagged explicitly as scope-narrowing, not silently claimed as literal class reuse.

## Axes measured (clean axes per task instruction)
- `unstated_goal` (n=12): pick correct goal-category from {correct + 3 distractors} given in gold.
- `satisfy_restate` (n=7): pick which of {restate_text, satisfy_text} is the TRUE resolution of goal_text.
`thwart_cause` (n=6, CAUSE items) present in the gold file but NOT scored here (task scopes to the two
clean axes only); left for a follow-on pass.

## Mechanism (CONSTRUCTION then INTEGRATION)
**Construction** (loose, lexical, overgenerate -- Kintsch's associative-spread stage): bag-of-words
FHRR-bundle cosine similarity between the query text and each candidate's representation.
- Goal axis: candidate representation = bundle of a small hand-authored tier-2 keyword prototype per
  category (9 categories total spanning the gold file; keywords are generic English synonyms of the
  category name, NOT fit to any individual item's exact wording -- avoids item-level overfit).
- Satisfy/restate axis: candidate representation = bundle of the candidate text itself; query =
  bundle of goal_text.
Construction narrows the candidate set to top-K (goal axis: K=3 of 4 given candidates) -- this is
scored SEPARATELY as **construction top-K recall**, not as end-to-end accuracy (per the task's
explicit measurement split).

**Integration** (coherence-filter -- reused SHAPE, not reused class instance, per Scope decision
above): a small spreading-activation relaxation over the surviving candidates. Weight matrix
`W[i][j] = cos(candidate_i_repr, candidate_j_repr)` for i != j (structural relatedness among
candidates, a genuine second signal beyond raw query-candidate cosine). Activation initialized from
construction's cosine scores (softmax), then relaxed for T=5 steps:
`a_(t+1) = softmax(constr_scores + gamma * W @ a_t)`, gamma=0.5. On the satisfy/restate axis the
relaxation additionally folds in a small hand-authored WISH-vs-RESOLUTION marker signal (Zwaan
intentional-state-shift proxy: modal/want-language counts favor "still pending" == restate;
past-tense/achieved-state-noun counts favor "resolved" == satisfy) -- this is the one place a
non-lexical structural cue is available without accumulated chapter context.
Final pick = argmax of the relaxed activation; REFUSE if margin(top1, top2) < REFUSE_MARGIN (declared
0.05 on softmax-normalized activation).

## Arms (4, matching the synthesis doc's spec)
- **MECHANISM**: construction (top-K narrow) -> integration (relaxation over top-K).
- **BASELINE_INTEGRATION_ONLY**: integration relaxation run directly over the FULL given candidate set
  with UNIFORM initial activation (construction/lexical-narrowing step skipped entirely) -- isolates
  whether integration alone (no construction stream) suffices.
- **BASELINE_LEXICAL**: argmax of raw construction cosine score only (no integration relaxation at all).
- **BASELINE_RANDOM**: uniform pick over the given candidate set, seeded (no `hash()`; digest-seeded).

## Fair / can-fail bands (pre-registered, deflated per novel-synthesis discipline, P capped 0.50)
- **MECHANISM_WORKS** iff: mechanism accuracy >= BASELINE_LEXICAL + 0.15 absolute AND
  mechanism accuracy >= BASELINE_RANDOM + 0.20 absolute (both axes combined AND each axis individually
  reported), AND refuse-gate fires (REFUSE rate) on the bottom-quartile-margin items >= a materially
  higher rate than on the top-quartile-margin items (proxy for "fires when genuinely uncertain," since
  no separate hand-labeled ambiguous-gold subset exists for this pass -- flagged as a proxy, not the
  gold-standard refuse-honesty test).
- **MECHANISM_INSUFFICIENT** (pre-registered, NOT relabeled as "impossible"): mechanism does not clear
  BASELINE_INTEGRATION_ONLY and BASELINE_LEXICAL by the above margins -> sharpens (does not reopen) the
  already-logged content-encoding deep-earn fork; report which axis specifically.
- Paraphrase-robustness (task's item iv): NOT measured this pass -- no paraphrase gold subset exists
  and fabricating one ad hoc would violate the MEASURED-not-hallucinated discipline. Flagged as an
  explicit follow-up, not silently skipped.

## Compute architecture
Sequential-CPU, in-process, <5s total wall time (19 items x 4 arms, D=256 complex vectors, no matmul
sweep) -- justification (c) cell IS a diagnostic measurement, not a training fit; GPU batching would
add engineering overhead disproportionate to the ~seconds of compute involved (compute-proportionality
rule). No storage/composition beyond the in-memory per-item candidate sets (no_storage).

## Cell-template mandatory declarations
- `cell_chunked`: false (single-shot measurement, no seed axis, <5s).
- `start_marker_written`: true.
- `crash_diagnostic_present`: true (Exception -> CELL_CRASHED metrics.json + traceback; SystemExit/
  KeyboardInterrupt re-raised first).
- `heartbeat_present`: n/a (cell completes in seconds, well under the 60s/15min heartbeat threshold).
- `defensive_error_checking`: "passed_all_4_patterns" (start-marker + crash-diagnostic + no-bare-except;
  heartbeat exempted as above).
- `arms_differ_verified`: true (hash-compare the 4 arms' per-item prediction vectors at smoke gate).
- `final_metrics_atomicity`: "tmp_replace".
- `deterministic_seeding`: true (digest-seeded per-word vectors via hashlib.sha256; RNG for
  BASELINE_RANDOM seeded from a fixed integer, never `hash()` or `list(set())`).
- `crlb_n/a`: "no quantitative capacity/noise-floor claim; discriminator is accuracy-vs-baseline on a
  fixed 19-item gold set, not a capacity sweep".
- `cardinality_ok`: n/a (no sweep axis; EXPECTED_N_UNITS = 19 items x 4 arms = 76, asserted directly).
- `real_code_path_and_signature_preflight`: n/a (cell does not call any live substrate class
  (KGStore/fit-module); it builds its own FHRR primitives inline per the Scope decision above -- no
  substrate_signature binding applicable).
- `progress_logging`: n/a (elapsed well under 1800s threshold).

## Numbers tag discipline
All numbers in the completion report will be tagged MEASURED@<path> (this cell's own metrics.json) or
explicitly THEORETICAL/HYPOTHESIZED where they are pre-reg thresholds, not measurements.
