# exp_dev hand-off — research: static sense-embedding input swap (LOW-PRIORITY confirmatory test)

**Filed by:** research sub-agent, 2026-09-03.

**Trigger:** `notes/research_wsd_input_representation_sense_embeddings_2026-09-03.md` — tested whether
replacing the frozen word2vec input (one vector per surface form) with a static per-WordNet-synset
embedding is a cheap glass-box upstream fix for rare-sense selection. Finding: NO, do not build this as
a primary direction — three independently-converging signals (brain-fidelity mismatch for this
project's actual failure population, which is polysemy not homonymy; one clean empirical number showing
sense-embeddings-alone underperform a plain supervised WSD baseline; confirmed circularity — every real
system falls back to the same frozen sense-conflated context vector). This hand-off exists only because
the note also names ONE cheap, well-controlled confirmatory test worth keeping on file, ranked well
below the two live anchors from the companion `research_wsd_contextual_encoding_glassbox_mechanisms_
2026-09-03.md` and `research_wsd_bem_lite_biencoder_design_validation_2026-09-03.md` hand-offs.

**Pause state:** ACTIVE (`data/orchestrator_paused.flag` absent as of this filing).

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off names an ANCHOR + POINTERS only.
exp_dev designs ALL of: N, seed count, threshold bands, corpus split sizes, queue choice, cell name,
smoke profile, FULL profile.

---

## Priority note (read before dispatching)

**Do NOT pull this anchor ahead of the two already-registered arms from the companion hand-offs**
(`exp_dev_handoff_research_wsd_contextual_encoding_2026-09-03.md` P_deflated 0.40/0.35;
`exp_dev_handoff_research_wsd_bem_lite_biencoder_2026-09-03.md` P_deflated 0.35). This anchor is
P_deflated **0.10** — a confirmatory/deprioritization test, not a promising build. Its value is in
CLOSING OFF a representational family with substrate-specific evidence, not in an expected gain. Build
it only when the higher-priority arms are already in flight or blocked, and capacity is otherwise idle.

## Anchor candidate

1. **WordNet-only static sense-embedding input swap (DeConf-style Personalized PageRank sense-biasing),
   stratified by homonym-type vs polyseme-type items.**
   - Anchor pointer: `notes/research_wsd_input_representation_sense_embeddings_2026-09-03.md`,
     "Cheap decisive test" + "Falsifiable predictions" sections.
   - Substrate-product reading: push each WordNet synset's existing frozen w2v-derived seed toward its
     WordNet-neighborhood region via Personalized PageRank over the WordNet graph (no BabelNet/Babelfy/
     Wikipedia-scale corpus needed — WordNet + existing word2vec only), producing one static vector per
     candidate sense. Feed this AS THE INPUT to the SAME diagnostic-query readout already used for the
     0.33-0.35 bag-of-words ceiling (same gloss targets, same argmax decision) — do not also change
     query construction; this test isolates the INPUT layer only.
   - Mandatory controls (both required, not optional): (a) same-dimensionality RANDOM-vector
     perturbation in place of the PPR push (rules out "any perturbation off the base vector helps");
     (b) stratify results by TOPIC-CONFOUNDED/POLYSEME-type vs TOPIC-DISTINCT/HOMONYM-type items (new
     split this drill's brain-fidelity finding requires) — report both splits, not just the aggregate.
   - Why now: cheap (WordNet + existing word2vec only, no new corpus/training), but explicitly
     low-expected-value; the predicted diagnostic pattern (gain confined to homonym-type items, none/
     negative on polyseme-type items) is itself a positive, actionable finding even inside an overall
     HARD-FAIL, per the research note's falsifiable predictions.
   - Tier: local/CPU (PPR over the existing WordNet graph + static vector arithmetic, no GPU need).

## Context pointers (pointers, not summaries)

- `notes/research_wsd_input_representation_sense_embeddings_2026-09-03.md` — this drill, full mechanism
  comparison (unsupervised vs knowledge-based multi-sense embeddings; retrofitting/KG-embedding;
  homonymy/polysemy brain dissociation; circularity numbers), citations.
- `notes/research_wsd_contextual_encoding_glassbox_mechanisms_2026-09-03.md` +
  `exp_dev_handoff_research_wsd_contextual_encoding_2026-09-03.md` — the higher-priority parallel
  thread (query construction, not input representation); unaffected by this note's finding.
- `notes/research_wsd_bem_lite_biencoder_design_validation_2026-09-03.md` +
  `exp_dev_handoff_research_wsd_bem_lite_biencoder_2026-09-03.md` — the highest-priority live anchor
  (contextual encoder); unaffected by this note's finding.
- `notes/STATUS.md` (search "reader_meaning_channel") — current bag-of-words ceiling numbers
  (0.33-0.35 rare-sense accuracy) this test's cheap decisive test scores against.

## Contract

- Pre-reg per [[feedback-envelope-expansion-fail-bands]]: HARD-PASS + HARD-FAIL bands already drafted
  in the research note; exp_dev finalizes exact N / seed count / thresholds before smoke.
- Self-test per [[feedback-formula-selftests]].
- Mandatory: both controls (random-vector perturbation; homonym/polyseme stratification) must run —
  the stratified asymmetry, not just the aggregate gain/no-gain, is the falsifiable prediction.
- status_log entry with `plain_language` + `importance` on completion.

## Autonomy declaration

exp_dev decides ALL of: cell name, N, seed count, threshold bands (within the HARD-PASS/HARD-FAIL logic
pre-registered above), queue choice, ETA, smoke profile, FULL profile, and WHETHER to build this anchor
at all this cycle given its low priority relative to the two live higher-P anchors. This hand-off passes
the anchor POINTER + mandatory-control design only — not numerical parameters, not a priority override.
