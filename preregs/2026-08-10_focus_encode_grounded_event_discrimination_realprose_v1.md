# Pre-reg: exp_focus_encode_grounded_event_discrimination_realprose_v1 (E3 binding-constraint gate)

Filed by: exp_dev (Sonnet, foreground, no nested sub-agents). Dispatched by Director/hdi_research with
task-shape + the scoping drill's pre-designed gate (`notes/research_e3_realprose_extraction_feasibility_
scope_2026-08-10.md` Section 4). This pre-reg refines that design into concrete implementation decisions
(exp_dev owns: exact grounding mechanism, n_dim, hypernym depth/decay, sample selection, band values).

Prior-work check (mandatory, 2026-07-01 USER-locked): `bash tools/substrate_query.sh "grounded event
bundle symbol layer semantic similarity fillers real prose discrimination"` -> top hit cosine=0.3662,
entity="reverse discrimination" (fairness/bias sense of "discrimination", unrelated domain). No hit above
noise on this exact concept -- confirms novel ground, matches the scoping drill's own KB-check finding.

## Question

Does GROUNDING `hdlab.event_bundle.EventBundleCodec`'s symbol layer (fillers = real semantic-similarity
vectors instead of `_bipolar_random` on first sight) make the structured {PRED,AGENT,PATIENT,TENSE}
event representation discriminate same-scenario vs different-scenario REAL MCScript2.0 dev narratives
BETTER than (a) plain bag-of-words and (b) today's ungrounded-structured baseline?

## Design (all three arms + scramble control RE-MEASURED in-cell, not cited)

Corpus: `data/corpora/mcscript2/extracted/dev-data.xml` (355 real crowd-sourced narratives, 162
scenarios) -- same corpus the scoping drill traced live.

Sample selection (deterministic, `sorted()`, no `hash()`/`list(set())`): scenarios with >=2 instances
(109 of 162), ranked by instance-count desc then scenario-name asc; take top N_SCENARIOS, up to
MAX_PER_SCENARIO instances per scenario (id-sorted). FULL: N_SCENARIOS=15, MAX_PER_SCENARIO=4 -> up to
60 instances across >=12 scenarios (matches contract). SMOKE: N_SCENARIOS=5, MAX_PER_SCENARIO=3 -> up to
15 instances (same code path, smaller N; DISCRIMINATOR-MUST-SURVIVE-SCALE: full corpus is itself small
and cheap, so smoke and full use IDENTICAL mechanism/parameters, only N differs -- Option A "smoke at
full-N parameters" is satisfied trivially since full N is already <1 min wall time).

Front end (ONE tokenizer throughout, deliberate simplification vs the scoping drill's Section 4 sketch):
`experiments._temporal_ordering.extract_events`'s own tagger (NLTK PerceptronTagger via
`exp_oracle_mention_upperbound_reader_v1.pos_tag_sentence`, Penn Treebank tags) is used for BOTH
event/tense detection AND positional AGENT/PATIENT extraction (nearest preceding/following nominal
POS-tag {NN,NNS,NNP,NNPS,PRP}, mirroring `hdlab.mcscript_extraction.extract_args`'s pre-verbal=subj /
post-verbal=obj / closest-to-verb convention, executed on the SAME token stream). This avoids composing
two different tokenizations' token indices (`CandidateGenerator`'s UD arc-parse + the fine-grained Penn
tagger `extract_events` needs) -- a real cross-tokenizer alignment risk, not exercised or needed since
B2 (arc-parse robustness) was already independently confirmed in the MCScript2.0 arc and is not the
variable under test here. AGENT/PATIENT quality is held IDENTICAL across all 4 arms.

Tense-fix (Section 3(ii)/Section 5's named fix, held constant across arms, isolates grounding as the
ONE variable): a CELL-LOCAL additive wrapper `extract_events_present_patched` adds a SIMPLE_PRESENT
branch for VBP/VBZ tokens extract_events's tagger already tags but the base function has no branch for
(mirrors the five existing branches; ADDITIVE ONLY -- ships as a cell-local patch, not a production edit
to `experiments/_temporal_ordering.py`, to avoid unreviewed side effects on other consumers; promote to
the shared module as a follow-up if E3 HARD_PASSes).

Four arms per instance (all built from the SAME extracted role_events + content_words):
  - **BOW**: `codec_ungrounded.encode_bag_of_args(content_words)` -- all VB*/nominal tokens across the
    whole narrative, unstructured, random per-word vectors (Stage-1c's real baseline, RE-MEASURED here).
  - **UNGROUNDED_STRUCTURED**: per-clause `EventBundleCodec.encode_event({PRED,AGENT,PATIENT,TENSE})`,
    fillers = `_bipolar_random` on first sight (today's production default), aggregated across the
    narrative's events via bipolar sum + `_bipolar_quantize` (Stage-1b's real baseline, RE-MEASURED).
  - **GROUNDED_STRUCTURED**: identical structured pipeline, fillers sourced via a TIERED grounding
    lookup (Tier 1: `hdlab.lexical_similarity.concept_vector` when the word is in its 89-concept
    lexicon, complex64 unit-phase bipolarized via `sign(Re(.))`, REUSE of the exact organ the scoping
    drill names; Tier 2: NEW this cell, WordNet hypernym-chain bipolar bag -- `nltk.corpus.wordnet`
    synset + up to HYPERNYM_DEPTH=3 ancestor hypernyms, deterministically seeded per synset name via
    `hashlib.sha256` (never `hash()`), decay-weighted 0.7^depth before sign-quantize (closer concepts
    dominate, ATL-hub graded-activation framing), reusing the already-promoted nltk-wordnet substrate
    dependency per `hdlab.animacy_lexicon`/`hdlab.wordnet_polarity_propagation` precedent -- gives real
    open-vocabulary coverage the 89-word lexicon cannot; Tier 3: `_bipolar_random` fallback, identical
    to the ungrounded arm's behavior, for WordNet-OOV words -- never crashes, never fabricates meaning).
  - **SCRAMBLE**: same GROUNDED pipeline but `EventBundleCodec.encode_scrambled_event` with a fixed
    derangement perm=[1,2,3,0] over (PRED,AGENT,PATIENT,TENSE) -- role<->filler binding destroyed.
    Mandatory control per the contract; if discrimination does NOT collapse, the win is grounding-alone
    (vocabulary co-occurrence), not structure.

N_DIM=8192 (matches `hdlab.lexical_similarity.N_DIM` so Tier-1 grounding needs no resize adapter).
SEED=7. Missing AGENT/PATIENT filled with a shared "_NONE_" placeholder symbol (random in both arms) so
every event has all 4 roles present (uniform perm length for the scramble control).

Discriminator (identical to the scoping drill's own metric): matched-pair (same-scenario) mean cosine
minus wrong-pair (different-scenario) mean cosine, over ALL pairwise instance comparisons within the
sample (not a sub-sample -- cheap at N<=60, ~1770 pairs).

## Compute architecture

Sequential-CPU (numpy/torch small ops; justification per exp_dev.md GPU-batching gate: wall time <10s
total measured this session for 545 sentences of extraction; WordNet lookups add low-single-digit
seconds; no GPU benefit at this N). Storage strategy: no persistent storage (a diagnostic-gate
measurement cell, not a store-write cell) -- N/A per storage-strategy gate.

## Bands (adopted from the scoping drill's Section 4, unchanged -- justification: the drill already
derived these against the SAME corpus and SAME baselines this cell re-measures, so no re-derivation
needed)

- **HARD-PASS**: grounded gap >= 0.153 (matches/beats the RE-MEASURED BoW gap) AND grounded gap >= 3x
  the RE-MEASURED ungrounded-structured gap AND scramble gap <= 0.02.
- **HARD-FAIL**: grounded gap < 0.05 OR scramble gap > 0.5x the grounded gap.
- **MIDDLE_BAND**: between the two (grounding helps but not enough to fully recover BoW, or scramble
  partially-but-not-fully collapses) -- routes to building the raw-text coref/reader adapter next
  (situation_reader's structural gap, Section 3(iii) of the scoping drill).

HP_SCOPE: all 4 bands apply to the GROUNDED/SCRAMBLE arms only; BOW/UNGROUNDED are RE-MEASURED reference
arms, not gated (their role is comparison, not pass/fail).

## Self-test / discriminator-fires gates

- `extract_events_present_patched` fires SIMPLE_PRESENT additively (present-tense text gets an event
  the base function misses) AND reproduces the base function bit-for-bit on past-tense text (no
  existing branch altered).
- Tier-1 grounding fires at n_dim=8192 (a known lexicon word returns a vector, tier="lexical_similarity").
- Tier-2 grounding fires on common open-vocabulary words WordNet covers (tier="wordnet_hypernym");
  total-OOV nonsense string returns None (never crashes, never fabricates).
- Same-lemma pair (deterministic, e.g. "places"/"placed" -> both -> `put.v.01`) grounds to cosine 1.0
  (mechanism sanity floor).
- `arms_differ_verified`: BOW/UNGROUNDED/GROUNDED/SCRAMBLE instance-vector hashes pairwise differ
  (META_RULE_AF) on a tiny synthetic 2-instance/2-scenario corpus.
- `baseline_in_band`: BOW and UNGROUNDED gaps must be in a measurable (non-degenerate, non-NaN) range
  at the sample size chosen -- if either baseline gap is NaN/degenerate (too few matched pairs), abort
  before interpreting the grounded arm.

## Schema-vet fields

- `cardinality_ok`: EXPECTED_N_UNITS = len(sample) (instances processed in pass 1); verdict logic
  compares `len(processed)` against `len(sample)`, HARD_FAIL_CARDINALITY_BREACH if short.
- `arms_differ_verified`: bool, set at self-test AND at full/smoke via hash check on real instance
  vectors (not just the tiny synthetic corpus).
- `final_metrics_atomicity`: "tmp_replace" (single-shot cell, tmp + os.replace at the one final write).
- `except SystemExit: raise` before `except Exception` (no BaseException, no bare except).
- `crlb_n/a`: "cosine-gap discrimination measurement on real narrative text; no capacity/noise-floor
  discriminator threshold to CRLB-check (the bands are drawn from a prior real measurement on the same
  corpus, not a synthetic capacity envelope)".
- `calibration_check`: "adaptive_with_discriminator_gate" -- HYPERNYM_DEPTH=3 / DECAY=0.7 are FIXED
  before running smoke or full (chosen from the manual chain-inspection done during design, not tuned
  post-hoc against the gap numbers); if smoke reveals over-genericity collapse (grounded gap far below
  ungrounded despite mechanism-fires self-test passing), that is reported as a MIDDLE_BAND/HARD_FAIL
  finding, NOT silently re-tuned to force PASS.
- `deterministic_seeding`: true (hashlib-derived synset seeds, `sorted()` sample selection, fixed SEED,
  fixed scramble perm -- no `hash()`/`list(set())` anywhere).
- `cell_chunked`: false (single instance-sample run, not a multi-seed sweep); per-instance pass-1
  extraction IS checkpointed via `tools/exp_checkpoint.py` (unit_key=instance id) per CLAUDE.md's
  multi-unit-loop mandate; pass-2 vector encoding (grounding-table-dependent, <1s total) is not
  separately checkpointed -- documented scope decision, wall time makes it unnecessary.
- `progress_logging`: "print_flush_true" (declared for template parity; actual wall time is seconds,
  well under the 30-min mandatory threshold).

## Report contract

All 4 gaps (BOW / UNGROUNDED_STRUCTURED / GROUNDED_STRUCTURED / SCRAMBLE), grounding coverage stats
(fraction of PRED/AGENT/PATIENT filler tokens grounded per tier), 2-3 concrete example passages with
their extracted role_events, and the verdict per the bands above.
