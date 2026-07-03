# Pre-Reg: substrate_concept_encoder_substrate_content_v1_2026_07_02

**Anchor:** `substrate_concept_encoder_substrate_content_v1_2026_07_02`
**Cell file:** `experiments/exp_substrate_concept_encoder_substrate_content_v1_2026-07-02.py`
**Author date:** 2026-07-02 (late evening)
**Origin:** USER 2026-07-02 late evening: "would be interesting to KNOW what substrate knows, so you can test accordingly" + full-auto authorized.
**Directive references:**
- `feedback_substrate_knows_almost_nothing_no_general_knowledge_ingest_yet_USER_LOCKED_REPEATED_2026-07-02.md`
- `feedback_mechanism_analog_is_not_task_analog_supervised_synthetic_corpus_is_supervised_regime_USER_LOCKED_2026-07-02.md`
- `feedback_substrate_doesnt_know_anything_stop_testing_against_language_USER_LOCKED_2026-06-26.md`
- `hdlab/concept_encoder.py` module docstring STAGE 4 CAVEAT (c) REAL-CORPUS TRANSFER

## Framing (LOAD-BEARING)

This cell tests the `hdlab.concept_encoder.ConceptEncoder` mechanism (brain-analog
competitive-Hebbian sparse coding) on SUBSTRATE-INGESTED SYMBOLIC KNOWLEDGE
(WordNet 3.0 lexicon partition, 6339 atoms with pos+definition metadata already
in `data/substrate_index/concept/atoms.jsonl`). It does NOT test:
- unsupervised concept discovery from raw corpora
- natural narrative text understanding
- "substrate understands English"
- language-benchmark equivalence (Stage 4)

**HP earned here grants:** "mechanism works on substrate's known symbolic content
(WordNet definitions+synonyms) at the tested regime". It does NOT grant "substrate
knows things" broadly.

**Corpus decision (per USER pre-authorization):** ConceptNet concept_node atoms
were spot-checked (2026-07-02) and found to have `description = "ConceptNet
english concept: <name>"` (literal name-repeat) — no usable body text. USER's
pre-authorized alternative ("Fall back to WordNet lexicon (6357 atoms) — these
should have dictionary definitions") is applied. Corpus IS the 6339 WordNet
lexicon atoms with `metadata.pos` set (dictionary sense entries).

## Stage classification

Stage 3 (higher functions — semantic-relation preservation on real symbolic
substrate content). NOT Stage 4 (no language-benchmark comparison; no BPC; no
perplexity; no trigram-context).

## Compute architecture (mandatory)

- **Class:** (b) sequential-CPU with justification.
- **Justification:** total wall < 10-15 min per seed at smoke N=100 atoms
  (concept_encoder.fit is O(N_sent * N_dim) numpy accumulator; encode is O(N_atoms
  * N_dim) argmax). GPU batching does not give substantial speedup at these
  numbers; sequential-CPU is the primitive's canonical arch.
- **Storage strategy:** SHARDED (per-atom concept HD; ConceptEncoder stores
  concept_hds table [n_atoms, n_dim] as int8; no bundled carrier).
- **Composition depth:** L=1 at fit (per-concept accumulator), L=1 at encode
  (cosine argmax). Not composing chained primitives — pure encoder eval.
- **Progress logging:** print_flush_true (timeout_s = 300 smoke / 1800 FULL <=
  30 min borderline; adding `flush=True` on progress lines defensively).

## Corpus

Source: `data/substrate_index/concept/atoms.jsonl` filtered to
`kind == "lexicon" AND metadata.pos in {n, v, a, r}` and
`metadata.synonyms` list has >= 3 entries and definition length >= 20 chars.
Sample sorted by `metadata.lemma_freq_semcor` desc (most-frequent first ->
most substantive definitions).

- **Smoke:** N=100 atoms, 3 seeds.
- **FULL:** N=500 atoms, 3 seeds (deferred; smoke gate first).

## Training / query construction

For each sampled atom A with synonyms S = [s1, ..., sk] and definition D:
- **Training sentences for concept-label = A_idx:**
  - `D` (the definition text)
  - `s1`, `s2` (first two synonyms)
  - If a hypernym exists, one hint sentence: `"related to <hypernym>"`
- **Held-out query for concept-label = A_idx:**
  - `s_last` (the LAST synonym, NEVER in training)
  - If atom has < 4 synonyms, use `s3` as query and drop `s3` from training.
- **Correct retrieval:** encode(s_last) → cosine argmax over concept_hds table
  → predicted atom_idx. Correct if predicted == A_idx.
- **@k accuracy:** recall@k = fraction of atoms where correct atom_idx is in the
  top-k argmax cosine matches.

## Arms

1. **ARM_CONCEPT_ENCODER** (LOAD-BEARING; the mechanism)
   - `hdlab.concept_encoder.ConceptEncoder(n_dim=2048, n_concepts=N, k_sparsity=0.02, mask_target_word=False)`
   - fit(training_sentences, concept_labels)
   - Query: encode(held_out_synonym) via internal char_positional surface encoder
     -> _classify() cosine argmax over concept_hds table

2. **ARM_CHAR_POSITIONAL_ONLY** (V1-analog surface baseline)
   - Same `CharPositionalEncoder(n_dim=2048)` used by concept_encoder internally
   - Encode each atom's TRAINING SENTENCES, mean-bundle per atom (no competitive
     Hebbian; simple bundling), get atom prototype HD
   - Query: encode(held_out_synonym) -> cosine argmax over atom prototype table

3. **ARM_CHAR_TRIGRAM_UNSUP** (bag-word baseline)
   - `hdlab.char_trigram_encoder.CharTrigramEncoder(n_dim=2048)`
   - Encode each atom's training sentences, mean-bundle per atom
   - Query: encode(held_out_synonym) -> cosine argmax over atom prototype table

Note: BGE-large arm is DEFERRED to FULL (bge-large on CPU with 500 atoms is ~10
min addl load+encode; not worth in smoke). Smoke skips Gate D; FULL will add
`ARM_BGE_LARGE` for infrastructure-parity comparison.

**Arms-must-differ:** all three arms use different mechanisms; hashing of the
per-atom encoded prototype tables MUST produce 3 distinct hashes.
`arms_differ_verified: true` required at smoke gate.

## HP bands (BAND-FLOOR + 5% strict)

### HARD_PASS

- **HP1 (concept_encoder mechanism-has-signal):** ARM_CONCEPT_ENCODER
  recall@5 (mean across 3 seeds) >= 0.20 (strict: >= 0.21 = floor + 5% of
  0.20 band-width, but with 0.20 floor we take strict >= 0.21).
- **HP2 (concept_encoder > char_positional):** ARM_CONCEPT_ENCODER recall@5 -
  ARM_CHAR_POSITIONAL_ONLY recall@5 >= 0.08 (mean gap).
- **HP3 (concept_encoder > char_trigram):** ARM_CONCEPT_ENCODER recall@5 -
  ARM_CHAR_TRIGRAM_UNSUP recall@5 >= 0.08 (mean gap).
- **HP4 (arms-must-differ):** all 3 arm prototype tables hash-distinct.

### HARD_FAIL

- **HF1 (mechanism fundamentally fails):** ARM_CONCEPT_ENCODER recall@5 < 0.05
  -> mechanism doesn't work on real symbolic content at all.
- **HF2 (no mechanism advantage):** ARM_CONCEPT_ENCODER recall@5 <
  max(ARM_CHAR_POSITIONAL_ONLY, ARM_CHAR_TRIGRAM_UNSUP) recall@5 -> mechanism
  has NO advantage on real substrate content; MAJOR REFRAME needed.
- **HF3 (arms bit-identical bug):** any two arm prototype tables hash-identical.

### MIDDLE_BAND

Anything between HF and HP -> insufficient signal or scope-tighten; report but
do NOT close capability. Smoke MIDDLE_BAND -> USER + Director decide before
FULL dispatch.

## Predicted values (HYPOTHESIZED)

**HYPOTHESIZED@this pre-reg:**
- ARM_CONCEPT_ENCODER recall@5: 0.15-0.35 (uncertain — real corpus vs synthetic
  cat/kitten regime; mechanism was CG'd at 0.492 cat/kitten cos on template
  corpus; held-out synonym query is a HARDER retrieval task).
- ARM_CHAR_POSITIONAL_ONLY recall@5: 0.10-0.25 (simpler mechanism; may retrieve
  when char overlap exists between definition and synonym).
- ARM_CHAR_TRIGRAM_UNSUP recall@5: 0.10-0.25 (trigrams pick up shared roots).
- Chance recall@5 at N=100: 0.05 (5/100).
- Chance recall@5 at N=500: 0.01 (5/500).

**THEORETICAL@random-argmax:** recall@k under uniform prior = k/N.

## Discriminator-fires (META_RULE_K)

Discriminator = ARM_CONCEPT_ENCODER recall@5 - baseline recall@5 gap. Smoke
must show ARM_CONCEPT_ENCODER recall@5 - max(baselines) recall@5 >= 0.05 AT
SMOKE (N=100) to justify FULL dispatch. If baseline saturates
(baseline_recall@5 > 0.60 at N=100), regime is too easy: char overlap between
definition and synonym is dominating; must escalate to N=500 hardened setup.

## Baseline-in-band gate (META_RULE_AG)

Baseline (char_trigram) at N=100:
- If < 0.05 -> baseline below floor; test is too hard (unlikely with char
  overlap possible).
- If > 0.80 -> baseline saturated; discriminator can't fire; regime too easy;
  ITERATE.
- In [0.05, 0.80] -> proceed to full assessment.

## Positive-control arm (META_RULE_D-adjacent)

ARM_CONCEPT_ENCODER's underlying primitive was CG'd on synthetic 25-cluster
corpus at seed 11/17/23. This is REGIME-DRIFT (synthetic-template -> real
WordNet); expect degradation. NO tolerance-based reproduction gate applies
(regime-drift is expected). Instead: HF1 catches TOTAL failure (mechanism
doesn't work at all).

## Schema fields (VET checklist)

- `cardinality_ok`: true (EXPECTED_N_UNITS = 3 seeds * 3 arms = 9 arm-seed
  results per run)
- `arms_differ_verified`: (set true at smoke gate; hashed prototype tables)
- `final_metrics_atomicity`: "tmp_replace" (single metrics.json write via
  os.replace at end)
- `crlb_n/a`: "no quantitative CRLB for supervised-retrieval-recall; not a
  cleanup task; noise floor set by chance = k/N"
- `discriminator_reachability`: true (HP2/HP3 gaps of 0.08 are within
  achievable range; not physics-bounded)
- `baseline_in_band`: (verified at smoke gate)
- `cell_chunked`: false (single-file 3-seed cell; wall < 15 min per seed at
  smoke)
- `start_marker_written`: true
- `crash_diagnostic_present`: true
- `heartbeat_present`: true (via `experiments._cell_heartbeat.CellHeartbeat`)
- `defensive_error_checking`: "passed_all_4_patterns"
- `sweep_alignment_verdict`: N/A (no parameter sweep)
- `discriminating_fraction`: N/A (no sweep)
- `composition_edges`: N/A (single-primitive eval, not composition)
- `positive_control_arms`: see above (regime-drift expected; no reproduction
  gate)
- `functional_requirements`:
  1. Retrieval of substrate-known concept given a held-out synonym query.
     Primitive: concept_encoder (competitive-Hebbian sparse coding + cosine
     argmax).
  2. Signal beyond surface char features. Baselines: char_positional +
     char_trigram (both no-competitive-Hebbian variants).
- `calibration_check`: "default_ok_for_this_regime" (concept_encoder CG defaults
  from Spoke 1 v3-D; regime-drift expected but constants unchanged)
- `progress_logging`: "print_flush_true"
- `arms_differ_exempted`: []
- `run_mode`: full expected in FULL landing; smoke expected in smoke landing
  (verify per META_RULE_16 RUN_MODE VERIFICATION POST-DISPATCH)

## Timeout budget

- **Smoke (N=100, 3 seeds):** timeout_s = 600 (10 min). Expected wall ~2-3 min.
- **FULL (N=500, 3 seeds):** timeout_s = 3600 (60 min). Expected wall ~10-15 min.
  DEFERRED — smoke gate first; USER+Director weigh before FULL.

## Dispatch plan

- Smoke: local_cpu_queue only (per USER-locked SMOKE ONLY on local_cpu 2026-07-01).
- FULL: DEFERRED pending Director+USER review after smoke report.
