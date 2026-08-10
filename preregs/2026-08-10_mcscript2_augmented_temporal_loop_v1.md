# Pre-reg: exp_mcscript2_augmented_temporal_loop_v1

Filed by: exp_dev (Sonnet, foreground, no nested sub-agents, no queue dispatch -- cheap local cell,
runs in low minutes on the real dev-set per Director's task contract).

Prior-work check (mandatory, 2026-07-01 USER-locked): `bash tools/substrate_query.sh "MCScript2.0 temporal
augment-not-replace BoW gated inference loop event ordering validate"` -> top hit cosine=0.2617
(entity="temporal arrangement", atoms KB), second cosine=0.2617 (WordNet "temporal_arrangement"), third
cosine=0.2607 (FrameNet "Event_initial_state"), fourth cosine=0.252 (`_temporal_ordering.py`, from
`notes/research_brain_event_segmentation_2026-08-05.md`), fifth cosine=0.2422 (inference-leap scoping
note). **All hits below the 0.30 dedup threshold.** No prior cell implements a gated augment-not-replace
BoW+temporal-loop system on MCScript2.0. This is genuinely the next cell in the E3/MCQA/E4 lineage, not a
rediscovery -- confirmed via the 4th hit pointing at the exact reusable module (`_temporal_ordering.py`)
this cell builds on, which is expected (a design pointer, not a prior instance of this cell).

## Question

Director's E4-first-step task (de-risked from the full E4 design in
`notes/research_e4_inference_augmented_comprehension_design_2026-08-10.md`, which found MCScript2.0
content-saturable in aggregate (BoW=0.629) but with a large (32.7%), BoW-provably-order-limited TEMPORAL
subset where a bag-of-words has no representation of event sequence): does an AUGMENT-NOT-REPLACE
two-route system -- Route 1 = always-on BoW (unchanged base), Route 2 = a glass-box PASSAGE-INTERNAL
temporal-order validation loop invoked ONLY when (question is TEMPORAL AND BoW is low-confidence AND both
answer candidates extract >=1 event), else silent -- beat BoW on the TEMPORAL subset, with the gain
COLLAPSING under an order-scramble ablation (proving order, not content, does the work) and NO regression
on the full set (the abstain-gate's anti-regression guarantee, verified empirically not assumed)?

Scope reduction from the full E4 design (explicit, Director-authorized): PASSAGE-INTERNAL only (no CSKG
store lookups -- reserved for a later causal-route increment); temporal subset only (causal/what-next
deferred, per E4 design's own finding that causal-why is only 0.7% of the corpus); 4 arms (BOW, AUGMENTED,
ORDER_SCRAMBLE, CONTENT_ONLY), dropping the full design's separate no-validate ablation (folded into the
scramble/content-only pair as the two load-bearing controls Director's Contract explicitly asked for).

## Design

**Corpus:** `data/corpora/mcscript2/extracted/dev-data.xml` -- 355 instances, 2020 questions, 2 answers
each, 1 correct (schema-enforced by `hdlab.mcscript_extraction.parse_mcscript_xml`, reused unmodified).

**Fixing the two bugs that sank the prior MCQA cell** (`exp_mcscript2_mcqa_droptense_properscramble_v1`,
HARD_FAIL, BoW=0.629 vs structured=0.401 BELOW CHANCE): (a) candidate events are extracted from the ANSWER
SPAN ALONE, never question+answer concatenation (the concatenation anchored both candidates on the shared
question stem, collapsing 404/1084 questions to ties); (b) the abstain-gate means a candidate with zero
extracted events NEVER gets a structured vote -- BoW stands. This is a mathematical (not just intended)
fix: whenever the gate's three AND-conditions are not simultaneously true, `pred_AUGMENTED := pred_BOW`.

**Event extraction (reused + one local additive patch):** `experiments._temporal_ordering.extract_events`
(tense-aware: SIMPLE_PAST/PAST_PERFECT/PASSIVE/MODAL_SUBORDINATE/PARTICIPIAL branches) wrapped by E3's
own present-tense patch (`exp_focus_encode_grounded_event_discrimination_realprose_v1.
extract_events_present_patched`, imported verbatim, additive, unmodified) -- REUSED, not
re-implemented. This cell adds ONE further additive-only local patch on top,
`extract_events_question_patched`: a bare VB preceded (<=3 tokens) by do-support ("do"/"does"/"did") is a
MAIN-CLAUSE event. This closes a KNOWN, DOCUMENTED coverage gap (the prior MCQA prereg's own "Coverage
measurement" section names it explicitly: "the miss cases are dominated by interrogative 'did X <bare-verb>'
constructions... a known, documented extraction-coverage gap"). Without this patch, "When did they get in
the taxi?"-shaped questions (a large fraction of the temporal subset by construction, since "when did X"
is the single most common temporal-question template) would silently fail to yield a question-anchor event,
crippling Route 2 by a fixable artifact rather than a genuine substrate limitation -- fixing it is required
for a fair test of the mechanism, not for tuning toward PASS (the patch is content-blind: it fires on POS
pattern + auxiliary proximity only, never on answer correctness).

**Verb-lemma normalization (found empirically during self-test, disclosed):** `Event.lemma`
(`_temporal_ordering`) is the raw lowercased SURFACE token, not a true lemma -- so a do-support
question's bare infinitive ("did I GET...") never string-equals the passage's simple-past surface form
("I GOT..."), silently starving anchor-matching. Fixed by adding a `vlemma` field (verb-normalized via
`nltk.stem.WordNetLemmatizer`, the SAME tool already used by this codebase's grounding pipeline's own
`_lemma` helper) that matching compares on instead of the raw surface string. Content-blind (a pure
morphological normalization, never touches answer correctness).

**Passage-internal temporal index (reused module, not reinvented):**
`experiments._temporal_ordering.reconstruct_order(events, tagged)` (Zwaan-Radvansky event-indexing:
tense-based flashback demotion + REORDER-connective local swaps) applied PER SENTENCE (matching the
existing `build_instance_role_events` per-sentence-loop convention -- avoids cross-sentence tagger/role-
assignment risk), then sentences concatenated in natural text order (the corpus is simple, chronological
procedural narrative -- global sentence order is the chronology hypothesis; within-sentence compound
clauses get `reconstruct_order`'s local tense/connective correction). AGENT/PATIENT per event via E3's
`assign_roles` (nearest-nominal positional heuristic, reused verbatim) for lemma-tie-break matching.

**Route 2 mechanism (glass-box, deterministic, no LLM):**
1. QUESTION anchor: extract the question's own event(s) (from the question text ALONE); best-match (PRED
   lemma exact = score 1.0; AGENT-or-PATIENT match only = score 0.5; else 0) against the passage's temporal
   sequence -> `anchor_idx` (position in the sequence) or None (anchor unlocatable -> abstain).
2. Each candidate: extract its event(s) from the ANSWER SPAN ALONE; best-match against the passage sequence
   -> `candidate_idx` or None.
3. VALIDATE (the mechanism under test): the answer whose matched event is CLOSER (`abs(candidate_idx -
   anchor_idx)` smaller) to the anchor in the passage's temporal sequence wins -- the brain-motivated
   heuristic that in a procedural script the temporally-relevant referent for "when did X happen" is the
   immediately adjacent scripted event, not a distant one (this is the concrete mechanism the E4 design
   doc's worked example depends on: "hail" (distance 1 from "get in taxi") beats "arrive at restaurant"
   (distance 3)). Ties or double-unmatched -> abstain (None).
4. Gate: Route 2 is INVOKED only when (is_temporal(question) AND BoW margin <= tau_conf AND both candidates
   extract >=1 event); tau_conf = median BoW margin over ALL temporal-subset questions (label-blind,
   computed from scores only, never from correctness -- not p-hacked). Route 2's own pick (possibly None)
   then OVERRIDES BoW only when invoked and non-None; otherwise BoW's pick stands untouched. This is the
   anti-regression guarantee: outside the gate's AND-conjunction, `pred_AUGMENTED == pred_BOW` identically.

**Ablations (same gate, different Route-2 internals -- isolate what does the work):**
- **ORDER_SCRAMBLE**: identical mechanism, but the passage's temporal sequence is permuted (a deterministic
  `hashlib.sha256`-seeded `torch.randperm`, keyed on `(seed, instance_id)` -- PROT-023 compliant, never
  Python `hash()`) before anchor/candidate matching. Event CONTENT is untouched (matching still succeeds
  identically); only POSITION meaning is destroyed. If the gain survives this, it was never about order.
- **CONTENT_ONLY**: identical gate, but Route 2 picks by raw match SCORE (does this candidate's event
  literally appear content-wise in the passage at all) with NO distance/position computation -- ties
  (including the common 1.0-vs-1.0 case where both candidates' events are literally present in the passage,
  e.g. the E4 design doc's own worked example) abstain. Controls for "the augmentation just adds more
  content-matching power" vs "the augmentation specifically exploits order."

**Multi-seed:** extraction (the expensive step: POS-tagging via `pos_tag_sentence`) is computed ONCE,
seed-independent (deterministic parsing). SEED varies only (a) the ungrounded `EventBundleCodec`'s random
per-word BoW symbol vectors (hence BoW margins, hence which questions clear `tau_conf`) and (b) the
ORDER_SCRAMBLE permutation. SEEDS = [7, 13, 19] (project convention). Verdict bands are applied to the
MEDIAN across seeds; per-seed accuracy reported for transparency.

**Scoring denominator (deliberate, documented departure from the prior MCQA cell's two-different-BOW-
denominators inconsistency):** a question is SCORED iff its passage BOW vector and both candidate BOW
vectors are non-None (content words exist) -- IDENTICAL denominator for all 4 arms (BOW/AUGMENTED/
ORDER_SCRAMBLE/CONTENT_ONLY), so the comparison is apples-to-apples; a BoW tie counts as WRONG for whichever
arm does not override it (never silently skipped), so no arm can inflate its accuracy by shrinking its own
denominator. TEMPORAL_SUBSET = the SCORED set further filtered by `is_temporal_question(question_text)`
(question-only, computed before any scoring, no label leakage): `"when" in words OR words &
{after,before,next,first,last,then}`.

## Compute architecture

Sequential-CPU. Justification: the prior MCQA cell's analogous extraction (355 passages + 4040 candidates,
similar POS-tagging cost) measured 1.06s+0.77s=1.83s for the full corpus; this cell's candidate texts are
SHORTER (answer span alone, not question+answer concatenation) so extraction is expected comparable-or-
faster; the added question-only extraction pass (2020 more short units) is the same order of magnitude.
Full-corpus reference-cell run (`exp_mcscript2_mcqa_droptense_properscramble_v1 --full`) landed at
elapsed_s=71.085 for a similar-scale pipeline (MEASURED@data/exp_mcscript2_mcqa_droptense_properscramble_v1/
metrics.json:elapsed_s). No GPU benefit at this N (tokenization + small-list index matching, not matmul).
Extraction checkpointed via `tools/exp_checkpoint.py` (mandatory per CLAUDE.md multi-unit convention);
BoW-encode + Route-2 matching + gating are cheap in-memory operations, not separately checkpointed. Storage:
no persistent store writes; diagnostic-gate cell (metrics.json only).

## Bands (Director's task contract, reproduced verbatim with this cell's own numeric operationalization)

Let `full_delta = acc_AUGMENTED_full - acc_BOW_full`, `subset_lift = acc_AUGMENTED_temporal -
acc_BOW_temporal`, `scramble_gain = acc_SCRAMBLE_temporal - acc_BOW_temporal`, `content_shortfall =
acc_AUGMENTED_temporal - acc_CONTENT_ONLY_temporal` (all median-over-3-seeds).

- `no_regression = full_delta >= -0.01`
- `scramble_collapses = (scramble_gain <= 0.01) AND ((subset_lift - scramble_gain) >= 0.02)`
- `content_fails_to_reach = content_shortfall >= 0.03`

**HARD-PASS** (all four, matching Director's Contract exactly): `no_regression AND subset_lift >= 0.05 AND
scramble_collapses AND content_fails_to_reach`.

**HARD-FAIL**: `NOT no_regression` (full-set regresses below BoW-0.01) OR `subset_lift <= 0` (no gain) OR
`NOT scramble_collapses` (any gain survives scrambling -> it was content, not the loop).

**MIDDLE-BAND**: everything else -- i.e. `no_regression` holds, `subset_lift > 0`, and `scramble_collapses`
holds, but EITHER `subset_lift` is between 0 and 0.05 (thin-but-real, genuinely order-attributable gain) OR
`subset_lift >= 0.05` but `content_fails_to_reach` is False (content-only nearly matches the loop, so the
win is not cleanly order-specific even though scramble collapses it -- an honest "partial collapse /
partial attribution" case per Director's Contract wording). Pre-committed exit per Director's framing:
routes to the flagship-benchmark pivot recommendation (TORQUE/MCTACO/WIQA), keeping the augment machinery.

HP_SCOPE: bands apply jointly to AUGMENTED (subset_lift, full_delta) and its two ablations SCRAMBLE
(scramble_gain) and CONTENT_ONLY (content_shortfall). BOW is the reference arm, not independently gated.

## Self-test / discriminator-fires gates

- Real-code-path: writes a tiny REAL MCScript-XML-schema temp file (2 instances -- one temporal, one
  non-temporal control) and parses it through the REAL `parse_mcscript_xml`; runs the REAL `run_pipeline`
  end-to-end at `n_dim=512` with `tau_conf` forced high (999.0) so the gate's margin condition cannot mask
  the mechanism, isolating whether Route 2 itself resolves the order question correctly.
- **Mechanism-fires assertion (deterministic, not just hash-differ)**: on a hand-built temporal narrative
  ("walk -> wait -> hail -> get-in-taxi -> pay", question "When did I get in the taxi?", correct answer
  "After I hailed a taxi" (distance 1 from anchor), wrong answer "When I walked to the corner" (distance 3
  from anchor)) -- asserts (a) AUGMENTED picks the CORRECT answer via the distance mechanism; (b)
  CONTENT_ONLY ABSTAINS on this exact case (both candidates' events are literal PRED-lemma matches, score
  1.0 each -> tie), proving order-sensitivity is doing work content-matching cannot; (c) a MANUALLY
  hand-constructed adversarial passage-order permutation (swapping "hail" and "walk" positions) FLIPS
  AUGMENTED's pick to WRONG while leaving CONTENT_ONLY's tie/abstain unchanged -- a direct, deterministic
  proof that the mechanism's correctness is order-dependent (not a probabilistic scramble-run hope).
- Non-temporal control question in the same tiny corpus: asserts Route 2 never fires (`is_temporal_question`
  False) and `pred_AUGMENTED == pred_BOW` exactly (abstain-gate no-regression property, unit-level).
- ORDER_SCRAMBLE determinism: same `(seed, instance_id)` -> bit-identical permutation across two calls;
  different `instance_id` -> different permutation.
- `arms_differ_verified` (META_RULE_AF): BOW / AUGMENTED / ORDER_SCRAMBLE / CONTENT_ONLY pairwise
  prediction-vector hash-differ on the tiny corpus.
- `is_temporal_question` unit checks: "when"/"after"/"before"/"next"/"first"/"last"/"then" fire; "what"/
  "where"/"who" do not.
- Band-logic sanity: hand-built accuracy dicts hitting HARD_PASS / HARD_FAIL (each of the three fail modes)
  / MIDDLE_BAND corners.
- `substrate_signature` check (F.2): `EventBundleCodec.__init__` kwargs (`n_dim`, `seed`) bound against the
  live signature, base/portable kwargs only.

## Schema-vet fields

- `cardinality_ok`: `EXPECTED_N_UNITS = n_instances` (passages) + `n_questions` (question-only extraction)
  + `n_questions*2` (candidates, answer-span-alone), all checkpointed.
- `arms_differ_verified`: bool, prediction-vector hash-differ across all 4 arms on the real full-corpus run
  (not just the tiny self-test corpus).
- `final_metrics_atomicity`: "tmp_replace".
- `except SystemExit: raise` before `except Exception` (no `BaseException`, no bare `except:`).
- `crlb_n/a`: "MCQA pick-accuracy measurement on real dev-set questions; band thresholds are Director's task
  contract values (this cell's own numeric operationalization), not a synthetic capacity envelope."
- `calibration_check`: "adaptive_with_discriminator_gate" -- `tau_conf` = median BoW margin on the temporal
  subset, computed from SCORES only (never from correctness labels), logged per seed in metrics.
- `deterministic_seeding`: true -- all RNG (`EventBundleCodec` symbol fallback, ORDER_SCRAMBLE permutation)
  seeded via fixed integers or `hashlib.sha256` digests of stable id strings; `sorted(set(...))` for all
  vocab/id ordering; no Python `hash()`.
- `cell_chunked`: false (single dev-set run per seed; extraction checkpointed once, shared across seeds).
- `progress_logging`: "print_flush_true".

## Report contract

Accuracy per arm (BOW/AUGMENTED/ORDER_SCRAMBLE/CONTENT_ONLY) on FULL set and TEMPORAL subset, per seed and
median; gate-fire-rate, override-rate, and abstain-rate on the temporal subset; empirical confirmation of
the no-regression property (AUGMENTED_full vs BOW_full, per seed); 3-5 concrete temporal examples where
AUGMENTED overrides BoW correctly (with the anchor/candidate distances shown, per the design's auditable-
trace goal) and 3-5 where the gate fires but Route 2 abstains (or overrides incorrectly); overall verdict
per the bands above. Report plainly whether this is HARD-PASS (temporal augment validated -> demonstrate on
MCScript2.0 temporal subset directly), MIDDLE-BAND (pre-committed: recommend flagship pivot to TORQUE/
MCTACO/WIQA, keep the augment machinery), or HARD-FAIL (augment-not-replace does not yet clear BoW here --
still routes to the same flagship-pivot recommendation, with the added finding that even passage-internal
temporal validation does not help). Do not engineer toward a preferred outcome.
