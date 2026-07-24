# Pre-reg: RACE passage-QA reading-comprehension measure (the reading RUNG + ARC de-confound)

- anchor_name: `race_reading_comprehension_measure_v1`
- cell: `experiments/exp_race_reading_comprehension_measure_v1.py`
- author: hdi_exp_dev
- date: 2026-07-24
- VET_PENDING: true (agent-reported)

## Question
Does the substrate's OWN reading/retrieval mechanism (char-trigram HD encode -> max-cosine over a
store -> argmax; the SAME mechanism the ARC cell used) read a 4-way MC passage-QA task (RACE) above
chance when the answer is IN the passage? This establishes the FOUNDATIONAL reading RUNG (reading
before knowledge) and DE-CONFOUNDS the ARC science number: if RACE (answer in-context) >> ARC
(knowledge not in-context), the ARC miss is definitively a KNOWLEDGE gap, not a reading/mechanism
gap. USER-steered: reading-comp comes first.

## Design / harness (mirrors the ARC glass-box MC-QA harness)
Per question Q with passage P (sentences s_1..s_m) and options o_1..o_4:
`store={encode(s_j)}`; `query_i=encode(Q+" "+o_i)`; `score_i=max_j cos(query_i,s_j)`; pick argmax.
LEAN by design (USER-authorized): establishes the reading RUNG + a can-fail measure + the
de-confound, NOT a SOTA QA system. Same `CharTrigramEncoder` as ARC (n_dim=2048) so the RACE-vs-ARC
comparison is apples-to-apples.

## Arms / controls (can-fail MANDATORY)
- `chance` = 0.25 (4-way) + random-pick + majority-letter controls (must land ~0.25).
- `lexical_overlap_only` = pick option with max content-word overlap w/ passage (naive, NO HD).
- `hd_support` = the harness above (the reading arm; primary).
- `word_scramble` = shuffle passage word order, re-chunk into pseudo-sentences, then encode. For a
  bag-of-char-trigrams encoder this is EXPECTED to barely collapse -> an HONEST reveal that the
  "reading" is lexical-overlap, not order-sensitive comprehension (the task's own framing).
- `mismatched_passage` = use a DIFFERENT question's passage as the store (deterministic cyclic
  derangement). MUST collapse to ~chance; if not, the gain is an artifact/leak. THE genuineness
  discriminator.

## Envelope / bands (PASS is on the HD reading arm; primary target = RACE-middle)
- PASS (`READING_RUNG_ESTABLISHED`): `hd_support_acc_middle - 0.25 >= 0.08` (>= ~0.33)
  AND `hd_support_acc - mismatched_passage_acc >= 0.05` AND `|mismatched - 0.25| < 0.06`
  AND not leak AND baseline_in_band.
- MIDDLE (`PARTIAL_READING`): HD moved above chance but below PASS band OR mismatched did not fully
  collapse.
- FLAT (`FLAT_AT_CHANCE`, can-fail): `|hd_above_chance| < 0.05` -> retrieval does not lift 4-way MC
  even with the answer in-passage (genuine can-fail; would indicate the mechanism cannot read).
- FAIL (`LEAK_FLAG`): `mismatched_passage_acc >= hd_support_acc - 0.05` -> gain is a lexical
  artifact, not reading THIS passage.

HYPOTHESIZED expectation (HYPOTHESIZED@this prereg): RACE-middle hd ~0.35-0.45, RACE-high lower
(longer/more inferential), mismatched ~chance, word-scramble ~near-zero collapse (bag-of-trigrams).
All FAR below a real student (~0.85+; CITED Lai et al. 2017 EMNLP). Even a modest 0.40 is +0.15 over
chance and >> ARC's ~chance+0.04 -> the de-confound holds.

## Compute architecture
- class: `(b) sequential-CPU with justification` -- per-question char-trigram numpy matmuls
  (encode + QV@SV.T) are tiny; total wall << a few min at the FULL slice. No GPU speedup available
  (no large shared matmul; ephemeral per-question stores). No batching candidate.
- storage strategy: `no_storage` -- per-question ephemeral passage store; no composition, no chained
  retrieval, no bundle. (Not a compositional cell.)
- CRLB: `crlb_n/a` -- accuracy over 4-way MC with ephemeral per-question stores; no associative
  capacity/noise floor governs the discriminator (it is telemetry-driven, not analytically pinned).

## SCHEMA-VET / CELL-TEMPLATE fields
- final_metrics_atomicity: `tmp_replace`
- start_marker_written: true ; crash_diagnostic_present: true ; heartbeat_present: true
- cell_chunked: false (single foreground run; no seed axis)
- arms_differ_verified: true (hd vs scramble vs mismatched stores hash-differ; checked at smoke)
- baseline_in_band: true (chance/random ~0.25; hd arm 0.05<acc<0.95)
- discriminator_fires (META_RULE_K): genuineness = mismatched_passage collapses to ~chance;
  order-sensitivity = word_scramble delta (near-zero is the honest reveal, not a failure).
- calibration_check: `default_ok_for_this_regime` (no primitive threshold inherited; bands are
  chance-relative and set here).
- effective_vs_nominal: n/a (no sweep axis). sweep_alignment_verdict: ALIGNED (no sweep).
- discriminating_fraction: n/a (no sweep); the single HD arm is predicted in [0.30,0.50] band
  (in the discriminating band, not saturated).
- composition_edges: none (no primitive->primitive composition). SHAPE_MATCH trivially.
- positive_control_arms: n/a (does NOT compose a prior chain-grade primitive; reuses the ARC
  harness pattern + the base CharTrigramEncoder, both re-exercised in self_test).
- real_code_path_exercised: [`CharTrigramEncoder`, `_encode_queries`, `_build_stores`, `_score_hd`,
  `_score_lexical_overlap`] -- self_test constructs the REAL encoder + runs the REAL scoring on a
  toy where the answer is in-passage (must score 1.0).
- deterministic_seeding: true (fixed int seeds; numpy default_rng; sorted iteration; `_art_hash`
  uses hashlib.sha1 NOT builtin hash; scramble RNG seeded from sha1-derived int, not builtin hash).
- progress_logging: `line_buffered_stdout` + `print_flush_true` (FULL wall << 30min but flushing on;
  section-17 compliant regardless).
- functional_requirements: (1) encode text->HD [CharTrigramEncoder]; (2) retrieve best-supporting
  passage sentence per option [max-cosine]; (3) decide answer [argmax + seeded tie-break];
  (4) genuineness control [mismatched-passage derangement]; (5) order-sensitivity control
  [word-scramble].

## Dispatch
- Contract: INLINE-LOCAL foreground-to-completion (mirrors the ARC sibling
  `exp_arc_knowledge_scale_ingest_climb_v1` contract exactly). RACE cached LOCAL-ONLY + UNCOMMITTED
  under `data/corpora/race/` (RACE redistribution restricted; we cache, do not commit).
- Rationale for NOT remote-queuing: RACE is not on the remote runner and remote network access is
  network-gated/uncertain; the char-trigram harness is fast enough to run FULL foreground-to-
  completion, producing an actual VERDICT today (complete-or-handoff = option a: verdict-with-numbers).
- Smoke: `--mode smoke` (60 middle + 40 high) verifies runs + discriminator fires + controls sane.
- Full: `--mode full` (1000 middle + 1000 high), foreground with a long timeout.
