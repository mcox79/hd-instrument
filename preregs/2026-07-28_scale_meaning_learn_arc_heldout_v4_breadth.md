# PRE-REG: SCALE meaning-learning v4 breadth -- ARC+SimpleWiki+breadth_v1 corpus, fair-tested via
# cosine-NN AND the learned relational readout

## ADDENDUM (post-authoring Director design-verification, 2026-07-28): 3 risks closed before ship
The Director's design-verification pass (after this pre-reg's initial draft + smoke) found 3 risks.
All 3 addressed; code + evidence updated below. Summary (full detail inline in the relevant sections):

1. **TOKEN-BUDGET CONFOUND** -- FIXED. `train_token_budget` was already held at a CONSTANT nominal
   value equal to v2's own cfg (130,000,000), but v2's OWN run never reached that nominal target
   (measured `trained_tokens=121,082,196` both seeds -- v2's ARC-only pool exhausted `max_lines=
   10,000,000` before hitting 130M). Changed `train_token_budget` to v2's exact MEASURED realized
   value (121,082,196), plus a runtime guard (`trained_tokens >= 0.98*budget` on FULL runs) so the
   breadth arm cannot end up with either a larger OR a meaningfully smaller pool than v2 actually
   trained on. `mlm_steps`/`mlm_batch` were already unchanged (training COMPUTE was never confounded);
   this closes the WINDOW-DIVERSITY/pool-size confound specifically.
2. **LEAK-WITNESS CIRCULARITY** -- FIXED. The original witness reused `_scrub_variants` (the SAME
   regex generator as the scrub) to decide "is this excluded," so any morphology `_scrub_variants`
   can't generate (irregular plurals, irregular verbs) leaked past BOTH the scrub and the witness.
   Fix, two parts: (a) the ACTUAL scrub (`_is_heldline`/`_build_scrub_set`) is now strengthened with a
   curated irregular-plural table + NLTK WordNet `morphy` (dictionary-based, independent of the regex
   generator) applied BIDIRECTIONALLY (candidate-word-to-heldout-surface AND heldout-surface-to-its-
   own-base, closing e.g. "argues"/"argue" and "asked"/"asks" where the held-out surface itself is an
   inflected form); (b) a genuinely INDEPENDENT witness (`_stem_leak_witness`, Porter stemming --
   algorithmically unrelated to both the regex generator and morphy) re-scans residual "train" lines.
   IMPORTANT CALIBRATION FINDING (evidence-based, not a silent downgrade): an inline debug run showed
   raw Porter-stem equality has a high false-positive rate at this vocabulary scale -- ALL of
   allow/allowance, assist/assistant, atoms/atomic, accusation/accused collide under Porter but are
   VERIFIED (via wn.morphy returning them unchanged) to be genuinely DIFFERENT WordNet lemmas, not
   concept leaks. Treating raw stem-equality as a hard "any collision = invalid" gate would false-fail
   this cell on essentially every run (guaranteed spurious collisions at ~800 held-out concepts x
   hundreds of millions of corpus tokens) without reflecting real exposure. The stem witness is
   therefore DIAGNOSTIC (reports `leaks_raw` + a stricter `leaks_strict` sub-count per corpus, logged
   loudly, included in metrics.json) rather than a blind hard-fail gate; the EXACT-SURFACE witness
   (unambiguous, zero false-positive-risk) remains the hard blocking gate, unchanged. Both witnesses
   confirmed iterating and reporting per-corpus counts for all 3 files (risk #3 below).
3. **MULTI-SOURCE COVERAGE CONFIRMED** -- already satisfied in the original design (this cell's
   `collect_pass`/`tokenize_train_stream`/both witnesses all accept a `sources` list and loop over it,
   unlike v2's hardcoded single-`ARC_CORPUS` versions). Re-verified after the above fixes: self-test
   witness output shows nonzero `checked`/`n_read` for `simplewiki`, `breadth_v1`, AND `arc` in BOTH
   the exact-surface witness and the independent stem witness (see Evidence section, updated).

**Interpretation note (per Director's explicit framing, stated here as instructed):** held-out concepts
have ZERO train mentions BY CONSTRUCTION (the held-out split excludes their own mentions from every
training pass). Breadth can therefore only help held-out-NEW placement via better GENERAL
representations/transfer that happen to generalize better to an unseen concept's grounding+text
signature -- NEVER via direct exposure to that concept's own content. A leak would illicitly add
exactly that forbidden direct exposure, which is why the exact-surface witness is a hard gate and why
even the diagnostic-only stem witness's findings are reviewed (not ignored) before trusting a HARD_PASS.

- anchor: `scale_meaning_learn_arc_heldout_v4_breadth`
- cell: `experiments/exp_scale_meaning_learn_arc_heldout_v4_breadth.py`
- date: 2026-07-28
- author: exp_dev (hdi_exp_dev), per Director task "build the BREADTH-scaled encoder run -- the one
  lever we have never pulled"
- base: derived from `experiments/exp_scale_meaning_learn_arc_heldout_v2.py` (copy+adapt, project
  convention -- v3_relobj and v3_grounding are the other siblings in this family, one by copy one by
  import). REUSES v2's exact leak-proof pipeline (concept-level scrub, BPE build, controls, semantic+
  relational eval code) verbatim except for the corpus-reading layer, which is generalized from a
  single ARC_CORPUS path to a list of 3 sources. ONE VARIABLE = training-corpus breadth. Architecture
  (d_model=512/6L/8H), objective (pure MLM), steps (60000), token budget (130M) all UNCHANGED from v2.
- plan: `notes/research_encoder_breadth_vs_relational_objective_scoping_2026-07-27.md` (original
  scoping; deferred breadth pending corpus staging -- now staged, this cell executes the deferred test),
  `notes/WHERE_WE_ARE_NOW.md` (LEG 1 scale-win + data-limited diagnosis, atom 29591),
  `data/exp_scale_meaning_learn_arc_heldout_v3_relobj/metrics.json` (relational-OBJECTIVE axis already
  HARD_FAIL_ARCHITECTURE_BOUND both seeds -- this cell tests the OTHER untested axis, does not re-spin
  the objective)
- target queue: `overnight_queue` (GPU) -- SMOKE + self-test landed LOCALLY (this doc, CPU, see
  Evidence section). FULL is a HAND-OFF: per the canonical `exp_dev.md` LOCKED process (2026-07-08),
  exp_dev authors + smokes locally and RETURNS the exact `queue_add.sh` command; the ORCHESTRATOR ships
  (SCP/SSH) + owns post-ship REMOTE VERIFY. exp_dev does not push / SSH-dispatch itself.
- compute class: (a) batched-GPU (MLM forward/backward + concept encode all batched; AMP on cuda).
  Corpus-scanning passes (count/collect/tokenize/witness) are sequential-CPU line processing --
  justified: this IS the leak-scrub primitive being validated (line-by-line scrub must see every line;
  vectorizing risks silently breaking the scrub-before-append invariant) and wall time is a small
  fraction of the ~3h/seed GPU training (measured at SMOKE scale: corpus passes took ~15s of the 82s
  total smoke wall time, i.e. ~18%; scales sub-linearly relative to the GPU-bound MLM step count which
  is UNCHANGED from v2).
- storage strategy: no_composition (learned-encoder cell; no HD store / no bundled composition)

## Prior-work check (substrate-KB concept-query, mandatory before authoring)
Two queries run this session:
1. `bash tools/substrate_query.sh "breadth corpus training data scale encoder held-out relational
   learned readout fair test"` -> top hit cosine=0.3311,
   `preregs/2026-07-09_grounding_learned_sr_heldout_STRONG_readout_v1.md` (READOUT-vs-ENCODER
   separation on learned-SR held-out REASONING -- a different substantive question: symbolic-rule
   reasoning readout strength, not concept-placement encoder breadth). Read; NOT the same question.
2. `bash tools/substrate_query.sh "breadth corpus simple english wikipedia scale meaning encoder ARC
   combined training data breadth lever"` -> top hit cosine=0.3223, entity=`breadth` (a generic
   WordNet/atoms concept node, not a research doc). No real prior-art hit above 0.30 for the actual
   breadth-corpus lever question.
VERDICT: this cell is genuinely novel / the next planned step, not a rediscovery. The actual real prior
art is `notes/research_encoder_breadth_vs_relational_objective_scoping_2026-07-27.md` itself (already
cited above as the design basis this cell executes -- it explicitly deferred breadth pending corpus
staging, which has since completed per `data/corpora/breadth_v1/COMBINED_MANIFEST.md`).

## What v4 adds/changes vs v2 (v2 unchanged otherwise; ONE variable = data breadth)
- **Corpus generalization**: `CORPUS_SOURCES = [simplewiki, breadth_v1, arc]` (small/broad sources
  FIRST -- deliberate upsample from their natural ~14.8% combined-pool share to ~34% of the 130M-token
  FULL training stream at FULL_CFG, per the small-first fill-order; measured@smoke:
  `per_source_tokens={'simplewiki': 1031418, 'breadth_v1': 340772, 'arc': 2627831}` out of 4M total =
  34.3% non-ARC at SMOKE_CFG, consistent with the design intent). This is the "drop-in leak-safe
  integration" recipe from `COMBINED_MANIFEST.md`: point the existing per-line reader at all 3 files,
  same per-line quality-filter + scrub-before-append, never `cat` the files together.
- **LEAK-PROOF RUNTIME ASSERT (mandatory correctness gate, this cell's #1 risk per task contract)**:
  `_zero_overlap_witness_per_source` scans an INDEPENDENT sample budget from EACH of the 3 files (not
  one shared budget a large source could exhaust before the others are ever checked), returns
  per-source `{checked, leaks, n_read}`, and `prepare_data` RAISES if `total_leaks != 0` OR if any
  source's `checked == 0` (proves the scrub-fires-across-all-3-files property, not just a green total).
  MEASURED@self-test: `{'simplewiki': {'checked': 200, 'leaks': 0}, 'breadth_v1': {'checked': 200,
  'leaks': 0}, 'arc': {'checked': 200, 'leaks': 0}}`. MEASURED@smoke: `{'simplewiki': {'checked': 2000,
  'leaks': 0}, 'breadth_v1': {'checked': 2000, 'leaks': 0}, 'arc': {'checked': 2000, 'leaks': 0}}`.
  ADDITIONALLY: `prepare_data` and `_selftest_assertions` both raise if any source contributes 0 tokens
  to `count_pass` or `tokenize_train_stream` (`per_source_tokens`), separately from the leak-witness --
  this is the "breadth lever genuinely exercised" gate, distinct from "breadth lever leak-safe."
- **CHECKPOINT-ALWAYS + RESUMABLE**: `_save_inprogress_ckpt` every `ckpt_every_steps` (atomic
  tmp+os.replace); `mlm_train_resumable` reloads it and continues from the saved step on a restart.
  MEASURED@self-test: `ckpt_diag={'n_ckpt_saves': 3, 'start_step': 0, 'resumed': False}` over 15 steps
  at `ckpt_every_steps=5`. MEASURED (dedicated unit test, see Evidence section): a fabricated
  in-progress checkpoint at step=9 is correctly reloaded and training resumes at step=10
  (`ckpt_diag={'resumed': True, 'start_step': 10}`), confirming the resume path (not just the save
  path). Known limitation: RNG on resume is deterministically reseeded from the resume step, NOT a
  bit-identical continuation of the interrupted RNG stream -- weights/step ARE preserved (the
  load-bearing property against losing a multi-hour run), documented not silently claimed exact.
- **OOM-SAFETY CARRY-FORWARD** (reused from v3_relobj's SH-5 VRAM-fit fix): `TinyTransformer.pooled` /
  `.mlm_logits` accept `use_checkpoint=True` (gradient checkpointing, mathematically identical output,
  no dropout); wired via cfg `mlm_grad_checkpoint` (default False -- pure MLM at this model size never
  OOM'd in v2's own FULL run; wired as an available escape valve, not forced overhead since v4 adds no
  extra pooling forward pass vs v2). `encode_concept_text_reps` already batches (`encode_batch`), the
  chunking property v3_relobj's `_pooled_for_rows` added for its OWN extra joint-loss forward pass --
  inherited for free here (v4's ONE variable is data, not an added objective/forward-pass).
- **LEARNED-READOUT FAIR TEST** (this cell's headline addition beyond the v2/v3_relobj family):
  relational placement is measured BOTH via cosine-NN (v2/v3_relobj convention, `relational_eval`'s
  `TEXT_ARM`) AND via the promoted learned relational readout
  (`experiments/_learned_relational_readout.py`, registry status `HARD_PASS_MAJORITY` 2026-07-28,
  rank-32 bilinear projection fit TRAIN-TRAIN only, leak-proof) for BOTH the breadth arm and the
  v2-baseline arm, per seed. `run_readout_probe` fits `PROBE_DIAG`/`PROBE_BILINEAR` via
  `build_train_pairs`/`fit_diag_probe`/`fit_bilinear_probe` (imported, not reimplemented) and evaluates
  via `eval_relational_all_arms` (imported). PLUMBING VERIFIED@synthetic unit test (see Evidence): on
  synthetic 400-concept data with a real graph, `run_readout_probe` returns
  `available=True, BASELINE_COSINE=0.527, PROBE_DIAG=0.507, PROBE_BILINEAR=0.527` and the
  arms-must-differ hash check passes -- confirms the fair-test computation path is wired correctly,
  independent of whether a real FULL-scale v2 checkpoint is available on THIS machine (which is
  inherently a FULL-scale-only comparison, same accepted limitation as v3_relobj's own smoke, whose
  own prereg records `baseline_source=cited_reference(0.56)` at smoke scale for the identical reason:
  smoke's reduced d_model/vocab/max_len cannot config-match a real FULL checkpoint).
- **BASELINE = v2's OWN trained encoder, REUSED not retrained** (store discipline; v3_relobj
  precedent): `_load_v2_baseline_encoder` reloads `data/exp_scale_meaning_learn_arc_heldout_v2/
  ckpt_seed_<seed>.pt` (VERIFIED on disk: `ckpt_seed_7.pt` exists, 109MB, `run_mode=full`,
  `model_cfg` matches v2's FULL_CFG exactly -> baseline reuse activates for seed 7 at FULL scale;
  `ckpt_seed_13.pt` is NOT present on THIS machine, but v3_relobj's own actual FULL landed run
  (`data/exp_scale_meaning_learn_arc_heldout_v3_relobj/metrics.json`, `baseline_source:
  ["reused_checkpoint","reused_checkpoint"]` for BOTH seeds, values EXACT-matching v2's own per-seed
  numbers) proves seed 13's checkpoint DOES exist on the remote GPU box where FULL actually runs --
  the local/remote asymmetry is expected store-discipline behavior, not a bug). Re-encodes on an
  ARC-ONLY postings pass built from THIS run's own split (`collect_pass(..., sources=ARC_ONLY_SOURCES)`)
  so the comparison is apples-to-apples on the identical held-out concept set, not v2's own historical
  postings. Falls back to a CITED reference (v2's own metrics.json per-seed numbers, tagged per seed:
  seed7=0.6407445089333272, seed13=0.6247552038153069 relational) if a given seed's checkpoint is
  absent; `baseline_source` distinguishes `reused_checkpoint` vs `cited_reference`, never conflated.

## Pre-registered bands (BEFORE running)
**Real baseline**: v2's own trained encoder (reused checkpoint, re-encoded on this run's ARC-only
postings+split; CITED fallback if unavailable), NOT random-init or chance. THE PRIMARY gate is the
learned-readout (`PROBE_BILINEAR`) relational-AUC margin, since a cosine-only lift can be a readout
artifact, not a genuine placement-capability lift (the exact confound the task contract names).

- **HARD_PASS_BREADTH_CLEAN_WIN**: `PROBE_BILINEAR` relational-AUC margin (breadth arm - v2 baseline
  arm) `>= +0.03` on BOTH seeds (per-seed strictly `> 0`), readout reload succeeds on BOTH seeds
  (`baseline_source=reused_checkpoint` both seeds, not CITED), AND the cosine-NN margin
  (`TEXT_ARM` relational AUC, breadth - baseline) is also `> 0` (directionally consistent -- if cosine
  and readout disagree in direction, that is NOT a clean win, see MIDDLE_BAND below), AND validity
  holds (collapse/popularity in `[0.44,0.56]`, raw_grounding `>=0.55`, `n_query_min>=120`).
- **HARD_FAIL_DATA_LEVER_REFUTED**: `PROBE_BILINEAR` margin stays within `+/-0.02` of the v2 baseline on
  BOTH seeds DESPITE genuine training (per-source token stats confirm all 3 corpora entered the train
  stream at FULL scale; MLM loss finite/decreasing). Reported PLAINLY per task contract: the breadth
  (training-data) lever does not move the fair-test relational ceiling; redirect off further
  corpus-breadth work. Combined with v3_relobj's HARD_FAIL_ARCHITECTURE_BOUND (relational-OBJECTIVE axis
  ALSO already refuted), this would mean BOTH untested axes named in `notes/WHERE_WE_ARE_NOW.md`'s
  "scale works but is DATA-LIMITED" diagnosis are refuted, pointing decisively at the readout/pooling
  mechanism (`encode_concept_text_reps`'s mean-pool order-blindness, already flagged once this session
  in the reader loop) as the real bottleneck.
- **MIDDLE_BAND_READOUT_UNAVAILABLE**: readout reload fails for >=1 seed (falls back to CITED) -- only
  partial (cosine-only) evidence available; cannot render the primary fair-test verdict. (This is the
  EXPECTED outcome at SMOKE/self-test scale per the config-match limitation above; it must NOT recur at
  FULL scale for a decisive verdict -- if it does, investigate why v2's checkpoint(s) are unreachable on
  the FULL run's execution host before trusting any margin number.)
- **MIDDLE_BAND_BREADTH_PARTIAL**: `PROBE_BILINEAR` margin positive but `< +0.03`, or per-seed min not
  strictly positive, or cosine/readout disagree in direction.
- **HARD_FAIL_INVALID**: validity gate fails (collapse/popularity/raw-grounding/power controls).

## Discriminator-must-survive-scale (option B analytical + C smoke preview, hybrid -- v3_relobj precedent)
The PRIMARY discriminator (the breadth-vs-baseline `PROBE_BILINEAR` margin) can ONLY be measured when
the baseline-reload's `model_cfg` exactly matches the running cfg's `vocab`/`max_len`/`d_model` etc --
i.e. it is inherently a FULL-scale-only comparison (v2's real checkpoint IS the FULL_CFG architecture).
This is the SAME accepted limitation as v3_relobj's own smoke (its prereg records
`baseline_source=cited_reference(0.56)` at smoke scale for the identical reason). Hybrid justification:
- (B) THEORETICAL/analytical: the learned-readout mechanism itself is independently validated
  (registry `learned_relational_readout`, `HARD_PASS_MAJORITY`, rank-32 bilinear beats cosine-NN by
  ~+0.038 mean on the real v2 mlm_v2_seed7 checkpoint per `data/exp_relational_readout_promote_v1/
  metrics.json`) -- the ONLY new question this cell adds is whether the MARGIN (breadth vs baseline)
  moves, which structurally requires FULL-scale matching configs on both arms.
- (C) SMOKE + dedicated unit-test preview of the MECHANISM firing (not the FULL-scale comparison
  itself): (i) MEASURED@smoke: all 3 corpus sources genuinely contribute tokens
  (`per_source_tokens={'simplewiki': 1031418, 'breadth_v1': 340772, 'arc': 2627831}`) and the
  per-source leak witness is clean (0 leaks, nonzero checked, all 3 sources) -- proves the BREADTH
  lever itself is genuinely exercised and leak-safe, the #1 correctness risk. (ii) MEASURED@dedicated
  synthetic unit test (not landed as a cell artifact, run inline this session): `run_readout_probe` on
  a 400-concept synthetic graph returns differentiated, sane AUCs (`BASELINE_COSINE=0.527,
  PROBE_BILINEAR=0.527`, arms-must-differ hash check passes) -- proves the fair-test FITTING/EVAL
  code path (imported from the already-HARD_PASS_MAJORITY-promoted module, not reimplemented) is wired
  correctly and will fire the moment FULL-scale baseline reload succeeds. (iii) MEASURED@dedicated
  resume unit test: a fabricated in-progress checkpoint at step=9 is correctly reloaded and resumes at
  step=10 -- proves CHECKPOINT-ALWAYS is not just a save-path no-op.
Both (B) and (C) apply: the mechanism that WILL differentiate (the readout module) is independently
proven to differentiate on real reps elsewhere in the substrate; this cell's own smoke proves every
OTHER moving part (multi-source breadth, leak-scrub, checkpoint/resume, fair-test plumbing) is correct;
only the actual FULL-scale margin number is necessarily deferred to the FULL run.

## Leak-proofness
- Concept-level held-out split (sha256, PYTHONHASHSEED-free) + per-source zero-overlap witness
  (NEW this cell, extends v2's single-file witness to 3 independent per-file samples) -- unchanged
  scrub logic (`_scrub_variants`) applied identically regardless of which file a line came from.
- Tokenizer/MLM/postings never see held-out text, across ALL 3 sources (scrub applied inside
  `count_pass`/`collect_pass`/`tokenize_train_stream`'s per-source inner loops, not a post-hoc filter).
- The v2-baseline reuse path introduces NO additional leak surface: it re-encodes v2's ALREADY-trained
  (leak-proof per v2's own pre-reg) weights on an ARC-only postings pass built from THIS run's split
  (same scrub, same held-out set) -- no new information reaches the baseline model.
- Readout fair-test fitting (`build_train_pairs`) is itself leak-proof by construction (imported,
  unmodified, already-promoted module): both pair endpoints are asserted inside `train_eval_idx` and
  disjoint from `held_idx` (raises, not warns, on violation).

## SCHEMA-VET declarations
- cardinality_ok: `EXPECTED_N_UNITS = n_seeds` (2 for FULL); verdict checks `len(per_seed)==n_seeds`.
- final_metrics_atomicity: tmp_replace (`write_metrics` + per-seed partials via `_seed_checkpoint`)
  PLUS periodic mid-training in-progress checkpoint (tmp+os.replace, every `ckpt_every_steps`) --
  CHECKPOINT-ALWAYS, resumable (see Evidence).
- except-ordering: `except SystemExit: raise` / `except KeyboardInterrupt: raise` BEFORE
  `except Exception` (no `BaseException` / no bare `except`). VERIFIED by grep gate: 0 matches for
  `except\s+BaseException` and `except\s*:` in the cell file.
- crlb_n/a: AUC discriminator base = 0.5 exactly; collapse+popularity+random-init witness the floor
  empirically (unchanged from v2).
- baseline_in_band: smoke collapse=0.4904 pop=0.4959 raw=0.6110 (0.05 < baseline < 0.95). PASS.
- HP_SCOPE: HARD_PASS gates apply to the learned-readout `PROBE_BILINEAR` relational-AUC margin
  (breadth arm vs v2-baseline arm), PRIMARY; cosine-NN margin is a directional-consistency guard, not
  independently sufficient; semantic arms (RAW/TEXT/FUSED/ZAVG/WTUNED/SELECTED) reported per v2
  convention, not gated (semantic was v2's own headline; this cell's headline is the relational
  fair-test per the task's load-bearing question).
- arms_differ_verified: True (sha256 hash-test over RAW/TEXT/RANDINIT held-out rep matrices, AND
  separately over the readout module's per-query score vectors via `arms_must_differ_hashes`
  -- both raise, not warn, on a bit-identical collision).
- calibration_check: default_ok_for_this_regime (AUC base 0.5 analytic; controls witness it).
- defensive_error_checking: passed_all_4_patterns (start_marker + CELL_CRASHED crash-diag w/
  traceback + `_heartbeat.jsonl` incl. mlm_loss + specific-exception classes throughout, e.g.
  `FloatingPointError` for non-finite loss, `(OSError, RuntimeError, KeyError, ValueError)` for
  checkpoint I/O). `cell_chunked: false` (2 seeds run sequentially in one process per FULL_CFG,
  matching v2/v3_relobj convention; per-seed partials still written via `write_partial` so a
  crash after seed 7 preserves that seed's result).
- real_code_path: `--self-test` constructs the REAL objects at N~16-1500 scale: multi-source
  `count_pass`/`collect_pass`/`tokenize_train_stream` (all 3 files), `build_bpe`, `mlm_train_resumable`
  (incl. the resumable-checkpoint mechanism), `TinyTransformer`, `encode_concept_text_reps`,
  `_zero_overlap_witness_per_source`, semantic+relational eval, `eval_baseline_arm_v2` (CITED-fallback
  path exercised by design at this scale, confirming the fallback is live not just the happy path).
  `run_readout_probe`/the learned-readout module are exercised via a DEDICATED synthetic unit test
  (not inside `--self-test` itself, since self-test's tiny model cfg cannot config-match a real v2
  checkpoint and so never reaches the readout code path through the main self-test flow -- flagged
  here explicitly per the real_code_path gate's intent: the readout MODULE'S real functions
  (`build_train_pairs`/`fit_diag_probe`/`fit_bilinear_probe`/`eval_relational_all_arms`) ARE exercised,
  just via a standalone script rather than through `main()`'s self-test branch).
- progress_logging: print_flush_true (MLM step logs + eval logs use `flush=True` throughout;
  `_heartbeat.jsonl` written every `log_every` MLM steps). `timeout_s` for the FULL dispatch will be
  >>1800s (see Timeout below), so this field is MANDATORY and satisfied.
- deterministic seeding: sha256 concept split (freq-stratified, sha256-ranked, `CONCEPT_SPLIT_SALT`
  unchanged from v2) + fixed int seeds (`seed`, `seed+5`, `seed+71`, `seed+999`, `seed+5001` for the
  readout diag-seed) + `sorted()` throughout; NO `hash()` or `list(set())` ordering anywhere in the
  cell (grep-verified: no bare `hash(` calls; all sets are consumed via `sorted()` or iterated without
  order-dependence on collection membership only, matching v2's own already-audited pattern).

## Capability-integration note (gate applies on landing)
Intended wire target if HARD_PASS: promote the breadth-corpus-reader pattern (multi-source small-first
interleave + per-source proportional BPE quota + per-source leak witness) as a reusable corpus-mixing
utility for future encoder-scale work, registered alongside `scale_win_tinytransformer_encoder` in
`data/capability_registry.jsonl` (current entry points at v3_relobj as "the project's best-validated
from-scratch concept encoder" -- if v4_breadth HARD_PASSes, that pointer should update to v4_breadth's
checkpoint as the new best-validated encoder). If HARD_FAIL_DATA_LEVER_REFUTED: register the negative
result (breadth-corpus-mixing tested and refuted as a lever for THIS ceiling) so a future session does
not re-spin the same axis; SHELVE the corpus-mixing utility with revival criteria "if a genuinely larger
(10x+) breadth corpus becomes available, or if the readout/architecture bottleneck is fixed first,
re-test breadth against the NEW ceiling."

## Evidence (this session, local CPU; MEASURED per META_RULE_AC tagging)
- Self-test (post-fix, all 3 risks addressed): `MEASURED@data/exp_scale_meaning_learn_arc_heldout_v4_
  breadth_selftest/metrics.json`: `verdict=SMOKE_PASS`, elapsed wall ~73-95s (morphy lookups add real
  but bounded overhead vs the pre-fix ~57s), `per_source_tokens` nonzero all 3 sources, exact-surface
  witness `{'simplewiki': {'checked': 200, 'leaks': 0}, 'breadth_v1': {'checked': 200, 'leaks': 0},
  'arc': {'checked': 200, 'leaks': 0}}`, independent stem-witness (diagnostic) `leaks_raw` totaling
  6-8 across a 600-line sample, `leaks_strict` 2-3, `ckpt_diag={'n_ckpt_saves': 3, 'start_step': 0}`.
- Smoke (post-fix): `MEASURED@data/exp_scale_meaning_learn_arc_heldout_v4_breadth_smoke/metrics.json`:
  `verdict=SMOKE_PASS`, elapsed_s~85 (per seed), `per_source_tokens={'simplewiki': 1031418,
  'breadth_v1': 340772, 'arc': 2627831}`, exact-surface witness all-3-sources checked=2000/leaks=0,
  independent stem-witness (diagnostic) `leaks_raw` totaling 292 / `leaks_strict` 181 across a
  6000-line sample (250 held-out concepts vs self-test's 60 -- collision count scales with held-out
  count, as expected for a stemmer-based check), collapse=0.4928 pop=0.4959 raw=0.6110
  (baseline_in_band PASS), n_query_min=243 (>=120), `baseline_source=cited_reference` (expected at
  smoke scale per the config-match limitation).
- **Stem-witness precision audit (inline, this session, not a landed artifact)**: manually inspected
  15 `leaks_strict` hits at SMOKE scale (250 held-out concepts) beyond the earlier 11 at self-test
  scale (60 concepts) -- 26/26 total inspected are confirmed, via direct `wn.morphy` lookup, to be
  DIFFERENT WordNet lemmas (e.g. `accusation`(base=accusation)/`accused`(base={accuse,accused}),
  `allowed`(base=allow)/`allowance`(base=allowance), `atoms`(base=atom)/`atomic`(base=atomic),
  `archaeological`(base=archaeological)/`archaeology`(base=archaeology)) -- ZERO of the 26 sampled hits,
  including the "strict" (length-ratio + prefix-filtered) subset, were genuine concept-identity leaks.
  This is direct empirical support for the diagnostic-not-blocking design of `_stem_leak_witness`:
  Porter stemming's derivational over-collapse (- ance/-ic/-ly/-ant/-able/-tion/-al suffix families)
  produces a per-corpus-scale-growing false-positive rate with (in this sample) 0% precision for the
  concept-identity question this cell actually cares about; the bidirectional-morphy-enhanced scrub
  (verified separately to correctly exclude genuine same-lemma variants: mouse/mice, argue/argues,
  ask/asks/asked, ability/abilities) plus the exact-surface hard-gated witness are the load-bearing
  leak-proofness mechanisms; the stem witness is retained as a transparency/audit trail per the task
  ask, not as an additional blocking gate.
- Resume unit test (inline, this session, not a landed cell artifact): fabricated in-progress
  checkpoint at step=9 -> `mlm_train_resumable` returns `ckpt_diag={'resumed': True, 'start_step': 10}`.
- Readout-plumbing unit test (inline, this session): `run_readout_probe` on synthetic 400-concept data
  returns `available=True, BASELINE_COSINE=0.527, PROBE_DIAG=0.507, PROBE_BILINEAR=0.527,
  n_query=60`, arms-must-differ hash check passes.
- Grep gate: `except\s+BaseException` and `except\s*:` -> 0 matches. `python -c "import ast; ast.parse(...)"`
  -> syntax OK.

## Timeout (queue_add.sh `timeout_s`)
v2's own FULL run: `elapsed_s=10206.5` per seed (2.83h), 2 seeds sequential in one process ->
`~20411s` total (measured, `data/exp_scale_meaning_learn_arc_heldout_v2/metrics.json`). v4_breadth adds:
(a) ~3x corpus-scanning cost for count_pass/collect_pass/tokenize_train_stream/witness (measured@smoke:
corpus passes ~15s of 82s total = ~18%, scaling with corpus lines not GPU steps -- at FULL scale this
is CPU-bound file I/O over ~2.9M extra lines (simplewiki+breadth_v1), a few extra minutes, not hours);
(b) a second ARC-only `collect_pass` for baseline-reuse postings (~ same cost as ONE of v2's own
`collect_pass` calls); (c) the learned-readout fit+eval per seed (probe fitting is `readout_probe_steps`
gradient steps over a low-rank `d->32` projection on `~2000` anchors -- seconds, not minutes, per the
smoke-scale synthetic unit test's near-instant runtime); (d) `wn.morphy`-based scrub enhancement
(bidirectional) + the two leak witnesses -- module-level cached per unique word TYPE (not per token
occurrence), measured overhead at self-test scale was ~15-35s added to a ~60-95s total run; at FULL
scale (bounded by distinct vocabulary size, not corpus token count, thanks to caching) this is
expected to add low-single-digit minutes, generously budgeted below. Estimated FULL overhead vs v2:
~20-25 minutes total across both seeds (padded up from the original ~10-15 min estimate to cover the
morphy-caching uncertainty at FULL vocabulary scale). `timeout_s = ceil(1.5 * (20411 + 1500)) = 32900`
(1.5x safety margin per queue_add.sh's own formula, using v2's own measured FULL wall time as the
closest real analog plus a conservative 25-min overhead allowance).

## Queue dispatch (exp_dev hand-off; orchestrator ships + REMOTE VERIFIES)
```
bash tools/orchestrator/queue_add.sh overnight_queue scale_meaning_learn_arc_heldout_v4_breadth \
  experiments/exp_scale_meaning_learn_arc_heldout_v4_breadth.py \
  preregs/2026-07-28_scale_meaning_learn_arc_heldout_v4_breadth.md 32900
```
Sequencing: route AFTER any currently-running GPU job on the single remote box (do not contend);
confirm via `python tools/inflight_monitor.py` before ship.
