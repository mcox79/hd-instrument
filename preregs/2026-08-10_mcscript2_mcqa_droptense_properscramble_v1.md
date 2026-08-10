# Pre-reg: exp_mcscript2_mcqa_droptense_properscramble_v1

Filed by: exp_dev (Sonnet, foreground, no nested sub-agents, no queue dispatch -- cheap local cell,
runs in seconds per Director's task contract).

Prior-work check (mandatory, 2026-07-01 USER-locked): `bash tools/substrate_query.sh "MCScript2 multiple
choice QA comprehension drop-tense grounded structured representation role scramble control"` -> top hit
cosine=0.3379, entity="Scramble control", source=`preregs/2026-08-06_grounded_word_acquisition_
increment1b_v1.md` -- a DIFFERENT arc (DesireDB word-acquisition OOV scramble control over verb-feature
entries, not event role-binding, not MCQA). Second hit cosine=0.3105, entity="comprehension" (generic
concept node, not a cell). No prior cell at cosine>0.30 runs an MCQA pick-the-answer test on MCScript2.0
using the event-bundle role-binding representation, and no prior cell implements a per-instance-
independent-random-key scramble (E3/E3b both used a single GLOBAL fixed derangement, the exact flaw this
cell fixes). This is genuinely the NEXT cell in the E3/E3b lineage on the REAL downstream task, not a
rediscovery.

## Question

E3 (`exp_focus_encode_grounded_event_discrimination_realprose_v1`, HARD_FAIL) and E3b
(`exp_focus_encode_shapefix_realprose_v1`, HARD_FAIL, landed
`data/exp_focus_encode_shapefix_realprose_v1/metrics.json`) both measured a PROXY task (same-scenario vs
different-scenario narrative discrimination) that BoW is structurally favored on (topic content-words
alone separate scenarios). Neither cell's scramble control ever collapsed: E3's SCRAMBLE gap (0.0551) was
slightly ABOVE its grounded gap (0.0542); E3b's GROUNDED_DROP_TENSE_SCRAMBLE gap (0.1337) was
statistically IDENTICAL to its own arm's gap (0.1336, delta 0.00007) -- both used `codec.
encode_scrambled_event(rf, perm)` with ONE FIXED derangement shared by every instance in the corpus.

**Diagnosed root cause (this cell's methodological fix, not previously identified in E3/E3b):** bipolar
bind is an elementwise-multiply ISOMETRY. Applying the SAME permutation of role keys to every instance in
a corpus is a global RELABELING, not a scramble -- `cosine(v'_A, v'_B)` under a shared fixed derangement
equals `cosine` under the ORIGINAL keys with a correspondingly relabeled role-assignment applied
identically to A and B, so cross-instance role-alignment structure (the very thing that would make
same-role fillers correlate across matched instances) survives the "scramble" intact, just living under
different key labels. A derangement only destroys cross-instance alignment if it is drawn INDEPENDENTLY
per instance (so instance A's role r and instance B's role r end up bound to DIFFERENT physical keys).
Additionally, with only `roles_subset=(PRED,AGENT,PATIENT)` (3 elements), the discrete derangement group
has only 2 members (`[1,2,0]`, `[2,0,1]`) -- independent per-unit draws from a 2-element space collide
~50% of the time by chance, diluting rather than cleanly collapsing the signal. This cell's scramble
mechanism (see Design) uses per-instance INDEPENDENT RANDOM ROLE KEYS (fresh `n_dim=8192` bipolar vectors,
near-orthogonal by concentration, not a draw from a small permutation group) to avoid this collision
confound and give the cleanest possible collapse test.

**The task question:** on the REAL MCScript2.0 dev multiple-choice QA task (pick the correct 1-of-2
answer for a question about a narrative -- a task that GENUINELY needs role/causal structure, unlike the
BoW-favorable scenario-discrimination proxy), does the DROP-TENSE grounded structured representation
(reused verbatim from E3b's `encode_flat_subset` over `roles_subset=(PRED,AGENT,PATIENT)`) pick the
correct answer better than plain bag-of-words, AND does a PROPER (collision-free, per-instance-independent)
role-scramble collapse that advantage toward chance -- proving the win is genuinely role-structural, not
vocabulary co-occurrence?

## Design

REUSE, not re-implement: imports `build_instance_role_events`, `build_grounded_codec`, `encode_instance_bow`,
`cosine`, `CORPUS_PATH`-sibling (this cell reads `dev-data.xml`, not `train`), `N_DIM=8192`, `SEED=7`,
`HYPERNYM_DEPTH=3`, `DECAY=0.7`, `NONE_FILLER` DIRECTLY from
`experiments.exp_focus_encode_grounded_event_discrimination_realprose_v1` (E3), and `encode_flat_subset`,
`DROP_TENSE_ROLES=("PRED","AGENT","PATIENT")` DIRECTLY from `experiments.exp_focus_encode_shapefix_
realprose_v1` (E3b) -- the exact grounded DROP_TENSE aggregation, not a re-transcription. `parse_mcscript_
xml` is reused unmodified from `hdlab.mcscript_extraction` (it already parses `<questions><question>
<answer correct=...>` -- the real MCQA schema -- no new XML parsing code).

**Corpus:** `data/corpora/mcscript2/extracted/dev-data.xml` -- 355 instances, 2020 questions, exactly 2
answers/question, exactly 1 correct (schema-enforced by `parse_mcscript_xml`, which raises loudly on any
breach). Question types: text=844, commonsense=966, positive-merged=210 (all three reported separately).

**Coverage measurement (informs sample sizing, run live 2026-08-10 against the real corpus before
finalizing bands):**
- Passage role-event extraction: 0/355 instances yield zero events (100% coverage). MEASURED@this session's
  pre-dispatch probe (full-corpus scan, not a subsample).
- Candidate (question-text + " " + answer-text) role-event extraction: 1084/2020 questions (53.66%) have
  >=1 role event on BOTH candidates AND a non-empty passage (a question is "SCORABLE" for the structured/
  scramble arms iff passage + both candidates all extract >=1 PRED event). The miss cases are dominated by
  interrogative "did X <bare-verb>" constructions, where `extract_events`'s existing MODAL_LEMMA set does
  not include the do-support auxiliary "did" (a known, documented extraction-coverage gap, not a new bug
  introduced by this cell -- see `experiments/_temporal_ordering.py` module docstring's MODAL_LEMMAS list).
  N=1084 scorable questions is well-powered (binomial std at p=0.5 is ~0.0152; a 5pp margin is >3 std devs).
- Full-corpus extraction wall time: passages 1.06s + candidates 0.77s (measured, all 355 instances / 4040
  candidates). Grounding-table construction (WordNet lookups over the resulting vocab) is the dominant
  remaining cost, expected single-digit seconds by analogy to E3's 8.4s FULL elapsed at ~800-word vocab.

**Sample:** `--full` runs the ENTIRE dev-data.xml (no subsampling -- cheap enough, per Director's "encode
runs in seconds" framing, to just use the whole dev set rather than a stratified subset). `--smoke` runs
the first 40 instances by sorted `id` (a real subset of the real corpus, not synthetic) to prove the full
pipeline runs end-to-end on real data before trusting the 355-instance run.

**Three arms**, each producing a `(passage_vec, cand0_vec, cand1_vec)` triple per SCORABLE question
(BOW is additionally scored on the FULL unfiltered question set for context):

1. **BOW** (the bar to beat): `encode_instance_bow(content_words, codec_ungrounded)` where
   `codec_ungrounded = EventBundleCodec(n_dim=8192, seed=7)` (random per-surface-string fillers, no
   grounding, no role structure -- literal lexical-overlap baseline, identical convention to E3/E3b's own
   BOW arm). `content_words` for the passage = `build_instance_role_events(passage_text)[1]`; for a
   candidate = `build_instance_role_events(question_text + " " + answer_text)[1]`. Scored on BOTH the full
   2020-question set (`BOW_full`, context only) and the SAME scorable 1084-question subset the structured
   arms use (`BOW_matched`, the actual comparison baseline for the HARD-PASS/FAIL bands).
2. **GROUNDED_DROP_TENSE** (the structured arm under test): `encode_flat_subset(role_events, codec_grounded,
   DROP_TENSE_ROLES, scrambled=False)` -- E3b's own function, imported verbatim. `codec_grounded` is built
   ONCE over the combined PRED/AGENT/PATIENT vocabulary of every scorable question's passage + both
   candidates (deterministic `sorted(set(...))`, no `hash()`), via E3's `build_grounded_codec` (Tier-1
   `hdlab.lexical_similarity` / Tier-2 WordNet-hypernym-chain / Tier-3 random-fallback grounding, unchanged).
3. **PROPER_SCRAMBLE** (the load-bearing fix): same `roles_subset=DROP_TENSE_ROLES` flat-sum aggregation
   and the SAME `codec_grounded` fillers, but role KEYS are NOT drawn from the codec's small fixed
   `role_keys` array under a permutation. Instead, for EACH encoded unit (the passage's encode for a given
   instance; each candidate's encode for a given `(instance_id, question_id, answer_id)`), a FRESH,
   INDEPENDENTLY drawn set of 3 random bipolar `n_dim=8192` role keys is generated from a
   `hashlib.sha256`-seeded `torch.Generator` (seed derived from the unit's own stable id string -- NEVER
   Python `hash()`, per PROT-023 / gate F.5). Passage and each of its candidates get DIFFERENT seeds (the
   passage's key-set is fixed per INSTANCE, i.e. shared across that instance's sibling questions since it
   is literally one passage; each candidate's key-set is fixed per `(instance_id, question_id, answer_id)`)
   -- by construction, passage and candidate NEVER share a key-set within one comparison, so the
   cancellation failure mode diagnosed above (an isometry applied identically to both sides of a cosine
   comparison approximately preserves that comparison's similarity) cannot occur here. At `n_dim=8192`,
   two independently-drawn bipolar vectors have expected dot product magnitude ~`1/sqrt(8192)` (~1.1%) --
   effectively orthogonal, giving a clean (not partial/diluted) decorrelation, unlike a 2-member discrete
   permutation group.

**Scorer:** for each scorable question, `predicted_i = argmax_i cosine(passage_vec, cand_i_vec)`; ties
(exact float equality, expected ~never) count as WRONG (conservative, no lucky-guess credit). Accuracy =
fraction of scorable questions where `predicted == the XML's correct answer id`. Reported overall AND
broken out per question `type` (text / commonsense / positive-merged).

## Compute architecture

Sequential-CPU. Justification: full-corpus extraction measured at 1.06s (passages) + 0.77s (candidates) =
1.83s for ALL 355 instances / 4040 candidates (see Coverage measurement above); grounding-table WordNet
lookups scale with unique-vocab count, expected single-digit seconds by direct analogy to E3's 8.4s FULL
at a smaller vocab. No GPU benefit at this N; matmul-heavy substrate primitives (bind/bundle/cleanup) are
not the bottleneck here, tokenization + WordNet dictionary lookups are. Storage: no persistent store
writes; this is a diagnostic-gate measurement cell (metrics.json only).

## Bands (per Director's task contract -- reproduced here verbatim, thresholds are this cell's own choice
per "you set it")

Let `chance = 0.5`, `gap_struct = acc_STRUCT - chance`, `gap_scramble = acc_SCRAMBLE - chance`,
`margin_over_bow = acc_STRUCT - acc_BOW_matched` (all measured on the SAME `N=1084` scorable-subset for an
apples-to-apples comparison; `acc_BOW_full` on `N=2020` is reported as additional context, not gated).

- `reaches_margin = margin_over_bow >= HARD_PASS_MARGIN` where `HARD_PASS_MARGIN = 0.05` (5 percentage
  points; at `N=1084` scorable questions, binomial std ~0.0152, so 0.05 is >3 std devs -- not noise) AND
  `acc_STRUCT >= 0.55` (at least 5pp above chance in absolute terms, so a "margin over a below-chance BoW"
  cannot masquerade as a real win).
- `collapses = gap_struct > 0 AND gap_scramble < SCRAMBLE_COLLAPSE_FRAC * gap_struct` where
  `SCRAMBLE_COLLAPSE_FRAC = 0.5` (identical convention to E3b's own scramble-collapse threshold).

**HARD-PASS**: `reaches_margin AND collapses`.
**HARD-FAIL**: `margin_over_bow <= 0 OR NOT collapses` (per Director's literal contract: ANY non-collapse
is HARD-FAIL regardless of margin size -- a large margin with a non-collapsing scramble means the win is
NOT coming from role structure, so the mechanism claim under test fails even if the raw accuracy number
looks good).
**MIDDLE-BAND**: everything else (i.e. `0 < margin_over_bow < 0.05` AND `collapses` holds -- a genuine but
small, role-structure-attributable gain; "structured ~ BoW").

This is an exhaustive 3-way partition (HARD_PASS / HARD_FAIL / MIDDLE_BAND cover all `(reaches_margin,
collapses)` combinations with no gap).

HP_SCOPE: bands apply to `GROUNDED_DROP_TENSE` (gated on `acc_STRUCT`, `margin_over_bow`) and
`PROPER_SCRAMBLE` (gated on `collapses`) jointly. `BOW` is the reference/baseline arm, not independently
gated.

## Self-test / discriminator-fires gates

- Real-code-path: self-test writes a tiny REAL MCScript-XML-schema temp file (2 instances, 2 scenarios, a
  question with 2 answers each) and parses it through the REAL `hdlab.mcscript_extraction.parse_mcscript_
  xml` (not a synthetic-dict bypass) -- proves the XML schema path is genuinely exercised.
- Reproduction check: this cell's structured encode on a probe `role_events` list must be BIT-IDENTICAL to
  E3b's own `encode_flat_subset(..., DROP_TENSE_ROLES, scrambled=False)` on the same inputs (trivial by
  direct import, not re-transcription -- asserted anyway per META_RULE_AC discipline).
- PROPER_SCRAMBLE determinism + independence: (a) the SAME unit-id seed must reproduce the IDENTICAL
  scrambled vector across two separate calls (determinism); (b) two DIFFERENT unit-id seeds must produce
  DIFFERENT key sets AND different output vectors on the SAME `role_events` (independence -- the mechanism
  actually varies per unit, not a no-op); (c) a passage and its own candidate, encoded with their
  respectively-independent seeds, must NOT be bit-identical even when `role_events` are identical (proves
  the "passage and candidate never share a key-set" design property holds in code, not just on paper).
- `arms_differ_verified` (META_RULE_AF): BOW / GROUNDED_DROP_TENSE / PROPER_SCRAMBLE pairwise hash-differ
  on a tiny synthetic 2-instance / 4-question corpus (real code path, not the XML-schema probe above).
- `cardinality_ok` + `deterministic_seeding` (hashlib-only, no Python `hash()`/`list(set())` anywhere in
  seed derivation -- statically scanned by `queue_add.py`'s PROT-023 gate; this cell is not queue-dispatched
  but the source-scan discipline still applies as a self-check).
- `substrate_signature` check (SS15 F.2): `EventBundleCodec.__init__` kwargs bound against the live
  signature.

## Schema-vet fields

- `cardinality_ok`: `EXPECTED_N_UNITS = n_instances` (pass-1 passage extraction) + `n_questions * 2` (pass-1b
  candidate extraction), both checkpointed via `tools/exp_checkpoint.py` per CLAUDE.md's multi-unit
  checkpoint mandate.
- `arms_differ_verified`: bool, hash-differ across all 3 arms' per-unit vectors (passage + both candidates,
  every scorable question) -- not just the tiny synthetic self-test corpus.
- `final_metrics_atomicity`: "tmp_replace".
- `except SystemExit: raise` before `except Exception` (no `BaseException`, no bare `except:`).
- `crlb_n/a`: "MCQA pick-accuracy measurement on real dev-set questions; HARD_PASS_MARGIN/SCRAMBLE_COLLAPSE_
  FRAC are this cell's own declared thresholds (per task contract 'you set it'), not a synthetic capacity
  envelope -- no CRLB applies".
- `calibration_check`: "adaptive_with_discriminator_gate" -- `HYPERNYM_DEPTH=3`/`DECAY=0.7` inherited
  unchanged from E3/E3b (not re-tuned; grounding quality is explicitly NOT the variable under test here).
- `deterministic_seeding`: true (all scramble-key seeds derived via `hashlib.sha256` digests of stable unit
  id strings; `sorted(set(...))` for all vocab/id ordering; no Python `hash()`).
- `cell_chunked`: false (single dev-set run, both extraction passes checkpointed).
- `progress_logging`: "print_flush_true".

## Report contract

Accuracy per arm (`BOW_full` on N=2020, `BOW_matched` / `GROUNDED_DROP_TENSE` / `PROPER_SCRAMBLE` all on
the SAME N=1084 scorable subset), broken out by question type; `margin_over_bow`, `gap_struct`,
`gap_scramble`, `collapses`, `reaches_margin`, overall verdict per the bands above; 3-5 concrete example
questions where GROUNDED_DROP_TENSE picked correctly and BOW did not ("structure helps"), and 3-5 where
GROUNDED_DROP_TENSE picked WRONG and BOW picked correctly ("structure hurts"), each with the passage
role-events, the two candidates' role-events, and per-arm cosine scores -- per Director's explicit request
to see WHAT the structure is/isn't capturing, not just the aggregate numbers. Report plainly whether the
result is HARD-PASS (structured representation validated on real comprehension), HARD-FAIL (structure
alone does not yet add comprehension value -> routes to the retrieve-VALIDATE-advance inference loop, E4,
per Director's framing), or MIDDLE-BAND -- do not engineer toward a preferred outcome.
