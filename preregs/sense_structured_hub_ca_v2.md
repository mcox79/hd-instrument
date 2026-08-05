# Pre-reg: C-A v2 sense-structured lexical-semantic hub -- corpus-scale, count vs error-driven
# (sense_structured_hub_ca_v2)

Status: PRE-REGISTERED 2026-08-05 before running. Cell: `experiments/exp_sense_structured_hub_ca_v2.py`.
Route: `notes/director_POST_COMPACTION_BACKUP_2026-08-04.md` top entry, C-A v1 HARD_FAIL diagnosis
(commit c1358cdce). v1 metrics: `data/exp_sense_structured_hub_ca_v1/metrics.json` --
held_out=0.5667, single_proto_control=0.6, same_sense=0.5, HARD_FAIL. LINCHPIN diagnostic:
mean_fit_same_sense_residual=0.4358 ~= mean_fit_diff_sense_residual=0.4474 (near-identical) -- the
context REPRESENTATION carried ~no sense signal because it was fit on only ~60 hand-written probe
sentences. The (faithfully-running) error-driven clustering had nothing to differentiate.

## Prior-work check (substrate-KB, USER-locked gate)
`bash tools/substrate_query.sh "sense structured hub error-driven context representation predictive
coding count PPMI corpus scale sense discrimination"` -- top hit cosine=0.3379
(`notes/research_teacher_free_relational_encoder_objective_2026-07-08.md`, a lit-scan finding that
plain co-occurrence/Hebbian pairing alone produces BLURRED/merged codes, not discriminative ones --
directly relevant grounding for why the error-driven arm is hypothesized to beat count, not a prior
cell attempting this build). No prior-arc cell at cosine>0.30 builds a corpus-scale count-vs-
error-driven sense-induction comparison. Genuinely novel re-attempt of C-A, not a rediscovery.

## Root-cause fix (what changed vs v1)
ONLY the context-representation FITTING DATA + MECHANISM changes. The labeled probe (10 forms, 2
senses each, disjoint FIT/TEST content-word vocabulary, machine-checked) is REUSED VERBATIM from v1
(same `PROBE` dict) -- ground truth requires hand labels, so the probe cannot come from raw corpus
text. What is new: the CONTEXT ENCODER used to turn probe FIT/TEST sentences into vectors is now fit
on a REAL BACKGROUND CORPUS (thousands of real sentences from `data/corpora/*/cleaned/*.clean.txt`),
not the ~60 probe sentences themselves. The induction mechanism (`_induce_senses`, online competitive
clustering gated by `hdlab.predictive_coding.threshold_gate`) is REUSED UNCHANGED from v1 for BOTH
arms -- only the upstream ctx_vec function differs per arm. This isolates count-vs-error-driven AND
the scale effect from v1's featureless-representation failure.

## Functional requirement decomposition (SCHEMA-VET item E)
- Requirement: the context representation must carry recurring, corpus-scale distributional
  structure (not starved on 60 sentences). Fix: `PPMISparseEncoder` (ARM-COUNT) and a newly-trained
  `predictive_coding`-gated associative memory (ARM-ERRORDRIVEN) are BOTH fit on the SAME background
  corpus subset (Section "Background corpus" below), not on probe sentences.
- Requirement: answer whether count-based content CAPS while error-driven differentiation is the
  brain-right answer (standing research note). Fix: two arms sharing everything (probe, induction
  mechanism, thresholds-recomputed-per-arm, controls) except the context-representation MECHANISM
  (count/PPMI-SVD vs error-driven/predictive-coding-learned).

## Background corpus (real, corpus-scale; built once per cell run)
Source: all 13 files under `data/corpora/*/cleaned/*.clean.txt` (alice_in_wonderland,
anne_of_green_gables, little_women, sherlock_holmes x2, tom_sawyer, wizard_of_oz,
graded_readers_grade1 x2, graded_readers_graded x3, textbook_concepts_biology; ~5.4M raw chars).
Sentence extraction: regex split on `.!?` boundaries after ASCII-only cleanup (non-ASCII bytes
dropped at decode time via `errors="ignore"`); filtered to 5-30 tokens, no digits, <=30% ALLCAPS
tokens (drops chapter headers / TOC junk), >=90% alphabetic tokens.

Selection (deterministic, seeded, `sorted(set(...))` discipline -- no `hash()`-seeded ordering):
1. ALL sentences containing a whole-word (case-insensitive) match of any of the 10 probe forms
   (hard, trick, pay, cross, bright, sound, light, bear, bank, bat) -- guarantees the probe forms
   have MANY real corpus occurrences in the background (raw whole-corpus token counts MEASURED
   pre-build: hard=371, trick=17, pay=96, cross=174, bright=176, sound=158, light=454, bear=146,
   bank=84, bat=26 -- `trick`/`bat` are the sparse tail but still >>60x v1's per-form fit-set size).
2. Deterministically sampled filler sentences (from the disjoint remainder, `sorted(set(...))` then
   `random.Random(SEED).sample`) up to `TOTAL_BACKGROUND_TARGET=3000` total, to give the encoders
   broad distributional statistics over common context words (not just probe-word-adjacent text).

Reported at runtime: `background_n_sentences`, `background_n_tokens`, per-probe-word raw occurrence
count in the selected background set (`background_probe_word_counts`).

## Mechanism -- TWO ARMS, same induction, differing ONLY in context representation

**Shared (identical code, both arms):**
- Probe: v1's `PROBE` dict verbatim (10 forms, FIT/TEST, disjoint-vocab machine-checked at runtime
  via `_assert_disjoint_vocab()`, same as v1).
- Induction: `_induce_senses` (online competitive clustering, `hdlab.predictive_coding.threshold_gate`
  gates split-vs-merge on FIT context vectors in seeded-shuffle order, `max_prototypes=4`) -- copied
  verbatim from v1, not reimplemented.
- Threshold calibration: `_calibrate_threshold` (FIT-only, `T = 0.5*(mean_same_sense_residual +
  mean_diff_sense_residual)` via `predictive_coding.residual_magnitude`) -- copied verbatim, computed
  SEPARATELY per arm (the two context spaces have different scales/distributions).
- Single-prototype floor control: `hdlab.concept_encoder.ConceptEncoder` (context-blind, word-FORM
  labels) -- copied verbatim from v1, computed ONCE (shared across arms; it does not depend on the
  arm's context representation, only on the fixed probe).
- Same-sense false-split control + cardinality/discriminator gates -- copied verbatim.

**ARM-COUNT (`count_ppmi`):** `hdlab.ppmi_sparse_encoder.PPMISparseEncoder(n_dim=128,
min_term_freq=3, smoothing=0.75, seed=SEED)` fit on the background corpus with
`concept_labels=arange(n_background_sentences)` (LSA-style: each background sentence its own PPMI
"concept" -- same fitting convention as v1, now at background-corpus scale instead of 60 probe
sentences). `ctx_vec(sentence, word) = ppmi.encode(mask_target(sentence, word))`.

**ARM-ERRORDRIVEN (`error_driven_pc`):** a `predictive_coding`-LEARNED context representation, not a
threshold gate over PPMI. Vocabulary: background-corpus content words with frequency >= 3 (stopwords
excluded) get a deterministic dense bipolar code `hv(word) in {-1,+1}^128` via
`hashlib.blake2b(f"{seed}:{word}")`-seeded `np.random.default_rng` (NOT Python's salted `hash()` --
avoids the F.5 nondeterminism class). Training (Rao-Ballard-style, reusing
`predictive_coding.predict` / `threshold_gate` / `gated_write` directly): for each content-word
occurrence `t` in the background corpus, `context_vec = sign(bundle(hv(c) for c in window(+-4,
excluding t, excluding stopwords, excluding OOV)))`; `predicted = predict(W, context_vec)`;
`decision = threshold_gate(observed=hv(t), predicted=predicted, threshold=0.30)`;
`W, applied = gated_write(W, context_vec, hv(t), decision)`. `W` starts at zeros(128,128) and
accumulates over ALL background-corpus occurrences (one training pass). After training,
`ctx_vec(sentence, word) = predict(W, context_vec_of(sentence, word), sign_cleanup=False)` (the raw
float `W @ context_vec` -- the LEARNED PREDICTIVE LATENT for that specific local context, not a
hand-picked gate over PPMI). This is the genuinely-error-driven representation: it is literally what
the trained associative memory predicts the word-identity pattern to be given this specific context,
and because W was trained with residual-GATED (not vanilla) Hebbian writes, novel/surprising
context-target pairings get written at full strength while already-predicted ones are skipped --
free-energy-minimization-style differentiation pressure during TRAINING, distinct from the
INDUCTION-time clustering gate (which is the same `threshold_gate` call reused for a different
purpose, per contract item 2).

## Controls (mandatory, per contract item 3)
(a) Single-prototype floor (`ConceptEncoder`, context-blind) -- must stay near chance/v1's floor;
    reused verbatim, one shared measurement (does not depend on arm).
(b) Same-sense false-split control -- per arm (each arm's induced hub gets its own held-out
    same-sense pairwise-agreement check).
(c) Induced-not-hand-listed witness -- `per_form.induction_trace` per arm.
(d) `arms_differ_verified`: count_ppmi and error_driven_pc predictions compared item-by-item
    (`n_items_where_arms_disagree > 0` required, logged).

## Pre-registered bands (contract item 4)
Floor reference (reused, MEASURED@data/exp_sense_collapse_floor_v1/metrics.json:honest_floor_accuracy
= 0.5625). This cell's OWN single-prototype control (re-measured fresh on the same probe, same
mechanism class) is the local floor-honesty check; report both.

- **HARD_PASS** (per-arm; a cell-level HARD_PASS requires >=1 arm to clear this):
  `held_out_sense_discrimination_accuracy[arm] >= 0.71` (floor 0.5625 + 0.15, clears META_RULE_L's
  5%-of-band-width-above-floor requirement by a wide margin -- band width to ceiling ~0.4375, 5% of
  that ~0.022, so 0.71 is not floor-hugging) AND `single_prototype_control_accuracy <= 0.65` (shared
  control stays near-chance -- rules out a probe-artifact leak, same gate as v1) AND
  `same_sense_agreement[arm] >= 0.60` (no false-split; relaxed from v1's 0.75 aspirational HARD_PASS
  bar to a still-clearly-non-floor-hugging value appropriate for a first corpus-scale attempt --
  chance-level same-sense agreement for a 2-prototype random split is ~0.50, so 0.60 is a real,
  non-trivial margin) AND senses induced not hand-listed (verified via `induction_trace`).
- **HARD_FAIL** (cell-level, both arms must fail): NEITHER arm reaches
  `held_out_sense_discrimination_accuracy >= 0.71`, OR the single-prototype control itself clears
  >=0.80 (control leak invalidates the whole probe), OR both arms show `same_sense_agreement < 0.50`
  (over-splitting/floor).
- **MIDDLE_BAND**: neither HARD_PASS nor HARD_FAIL condition fully met (e.g. an arm lands in
  [0.65, 0.71) -- above v1's number and floor but short of the pre-registered margin; or one arm
  clears held-out-acc but same_sense_agreement sits in [0.50, 0.60)).

`HP_SCOPE`: `{count_ppmi: [held_out_acc_gate, same_sense_agreement_gate, induced_not_hand_listed],
error_driven_pc: [held_out_acc_gate, same_sense_agreement_gate, induced_not_hand_listed],
single_prototype_control_arm: [must_stay_near_chance_gate]}` (shared control gate applies once, not
per-arm, since the control mechanism is identical across arms per SCHEMA-VET item 5b).

`EXPECTED_N_UNITS = 10` forms, evaluated once per arm (2 arms) -> cardinality gate checks
`len(per_form[arm]) == 10` for both arms.

## Honest can-fail routing (contract item 5)
If BOTH arms fail: re-run the v1 glass-box diagnostic (`mean_fit_same_sense_residual` vs
`mean_fit_diff_sense_residual` from `threshold_calibration`, per arm) on this cell's real-corpus-fit
representations. If STILL near-identical at corpus scale -> the probe forms/eval design itself may be
too hard (report, do not force a win) or the encoders' effective_n_dim/window settings are
mis-sized -- name the concrete parameter, not a vague ceiling. If error-driven clears the gate and
count does not (or vice versa) -> report that comparison explicitly as the finding, even if the
absolute accuracy is MIDDLE_BAND-adjacent; a clean count-caps/error-driven-wins split at modest
absolute accuracy is a WIN for the "count caps, error-driven is brain-right" research direction and
should be reported as such, not forced into a HARD_PASS frame it does not meet.

## Compute architecture / storage / atomicity / defensive-checking (SCHEMA-VET declarations)
- Compute architecture: **(b) sequential-CPU with justification** -- background corpus ~3000
  sentences / ~35k tokens; PPMI/SVD is a one-time fit on a (V, ~3000) matrix (V bounded by
  min_term_freq=3); error-driven training is one pass of small (128x128) matrix-vector ops over
  background-corpus content-word occurrences (tens of thousands of iterations, ~1e9 flops total).
  Expected wall time: tens of seconds to a few minutes, single foreground Bash call with
  `timeout: 600000`. GPU batching would add complexity for no benefit at this one-shot scale.
- Storage strategy: `no_storage` (representation-induction/measurement cell; the trained W and PPMI
  term-embeddings are transient in-process objects, not persisted associative-memory stores).
- `cell_chunked: false` (single-shot measurement, no seed axis; corpus build + both arms run in one
  process). Per-arm progress is logged via `print(..., flush=True)` (background-corpus build,
  PPMI fit, error-driven training loop every 5000 occurrences, per-form induction) --
  `progress_logging: "print_flush_true"` (this cell may exceed the 30-min §17 threshold on a slow
  machine; declared defensively even though expected wall is much shorter).
- `start_marker_written: true`, `crash_diagnostic_present: true`, `heartbeat_present: false`
  (`defensive_error_checking: "exempt_short_singleshot_cell_start_marker_and_crash_diagnostic_present"`,
  same precedent as v1/Step-0; if wall time empirically exceeds ~5 min this exemption is revisited).
- `final_metrics_atomicity: "tmp_replace"`.
- `crlb_n/a`: "representational sense-induction measurement; no quantitative noise-floor formula
  applies" (same as v1).
- `arms_differ_verified`: count_ppmi vs error_driven_pc predictions compared directly per item
  (`n_items_where_arms_disagree` logged, must be > 0).
- `calibration_check: "adaptive_with_discriminator_gate"` -- threshold `T` computed FIT-only, per arm,
  same formula as v1.
- `real_code_path_and_signature_preflight`: self-test (`--self-test`) builds a REAL tiny background
  corpus (one file, ~20 sentences), fits a REAL `PPMISparseEncoder`, trains a REAL (tiny) error-driven
  `W` via real `predictive_coding.predict/threshold_gate/gated_write` calls, and runs a real
  `_induce_senses` + `_calibrate_threshold` pass on both -- not a synthetic-only branch.
- Discriminator-fires gate: self-test/main asserts induction produces >=2 prototypes for at least one
  form, for EACH arm independently.
- Deterministic seeding (F.5): no `hash()`-seeded RNG anywhere in this cell (background-corpus filler
  sampling uses `random.Random(SEED)` over a `sorted(set(...))` pool; `hv(word)` uses
  `hashlib.blake2b` digest, not builtin `hash()`; the v1 single-prototype-control tie-break RNG that
  used `hash(w) % 10000` is FIXED in v2 to a `hashlib.sha256` digest instead).

ASCII-only. LOCAL-only, in-process/foreground execution (no queue dispatch, no background/nesting),
per task contract.
