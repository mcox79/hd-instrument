# Pre-registration: schema_bundle_real_corpus_transfer_v1

**Filed:** 2026-07-05 by exp_dev (cell author)
**Anchor:** `schema_bundle_real_corpus_transfer_v1`
**Cell:** `experiments/exp_schema_bundle_real_corpus_transfer_v1.py`
**Queue:** remote_cpu_queue (CPU, numpy, N=8192; FULL is canonical)
**Prior-work check (substrate-KB concept-query):** top hits at cosine ~0.32 are the
WordNet dictionary entries "transferral"/"transferable", a generic "Transfer learning"
science atom, and a domain-adaptation lit-scan note chunk. NONE is a prior HDI cell
testing real-relation schema transfer. This cell is genuinely novel (it is the
explicit real-corpus follow-up named inside the synthetic cell's WHAT_THIS_DOES_NOT_SHOW).

## Question

The synthetic schema cell (`schema_bundle_structural_transfer_v1`) HARD_PASSED at FULL
(transfer +0.590 at M=200) proving the holistic/analogical-map MECHANISM
`M_R = mean_i bind(B_i, inv(A_i))` ; `D_hat = bind(C_novel, M_R)` ; argmax cleanup,
works WHEN entities carry dial-able shared structure. The decisive open question:
does it help on REAL knowledge? Can the substrate turn many stored facts of a relation
into TRANSFERABLE knowledge -- answer correctly for a NOVEL same-relation entity pair it
never saw? This cell reuses the EXACT validated mechanism and changes ONLY the data:
real ConceptNet relation triples encoded with the substrate's zero-LLM encodings.
Constructive build; ZERO LLM calls; not vs-LLM.

## Interpretation matrix (PRE-REGISTERED -- the point of the cell)

| Outcome | Meaning |
|---|---|
| real-relation HARD_PASS | substrate turns stored facts into transferable knowledge in the current encoding (the GOAL). |
| real HARD_FAIL AND synth-positive PASS | MECHANISM works but real relations lack learnable structure IN THE CURRENT ENCODING -> points at ENCODER/INGEST, NOT the mechanism. A DIAGNOSTIC that feeds the encoder-primary program, not a mechanism failure. |
| real HARD_FAIL AND synth-positive FAIL | HARNESS_SUSPECT: cleanup/algebra broke at this regime; downstream real arms uninterpretable. |

## Data + encodings (both ZERO-LLM, deterministic, self-contained, restartable)

- Corpus: `data/datasets/conceptnet5_en_100k.jsonl` (real ConceptNet-5 English triples;
  git-tracked; VERIFIED present on remote C:/dev/hd-instrument, size 7847071 identical).
- `char-trigram phasor` (ARM_REAL): entity string -> boundary-marked char-trigrams ->
  each trigram md5-hashed (platform-stable) to a random unit phasor -> bundle (sum) ->
  phase-only projection `exp(i*angle(.))` to a unit-modulus FHRR phasor. Captures SURFACE
  (morphological) structure only. Cheapest zero-LLM encoding the substrate could ingest.
- `random phasor` (ARM_RANDENC): entity -> hash(entity,seed) -> random unit phasor. This
  is the substrate's ACTUAL current KG-store entity encoding (KG atoms are random
  hypervectors; ref exp_u1_fb15k237 / exp_n8_conceptnet ingest cells). Structureless by
  construction -> mechanism MUST give ~chance.

## Relations (3, spanning the structure spectrum; object-concentration measured on disk)

| relation | pairs | n_obj | top-100 coverage | object-reuse | expected |
|---|---|---|---|---|---|
| AtLocation | 27797 | 7771 | 0.337 | 93.7 subj/obj | flagship; pure semantic; char-trigram carries NOTHING |
| CausesDesire | 4688 | 598 | 0.304 | 14.2 | small codebook; semantic |
| DerivedFrom | 6535 | 3150 | 0.232 | 15.1 | surface-morphological; ONLY relation char-trigram could carry |

Codebook = top-V (V=100) objects per relation; `random_baseline = 1/V_eff` (THEORETICAL).
Novel-subject held-out: split by SUBJECT (train subjects disjoint from test subjects);
test objects are in the codebook (seen with OTHER subjects) -> genuine novel-subject transfer.

## Arms (all paired: SAME relation triples / split / seed; only the manipulation differs)

- `ARM_REAL` -- char-trigram enc, TRUE pairs. PRIMARY. HP gates apply.
- `ARM_SHUFFLED` -- char-trigram enc, object labels permuted within the M-sample (breaks
  subject->object correspondence). Structureless-RELATION / codebook-artifact discriminator.
  Director-mandated control (a). Expected ~chance.
- `ARM_RANDENC` -- random-phasor enc, TRUE pairs. Structureless-ENCODING discriminator.
  Director-mandated structureless arm (b). Expected ~chance.
- `ARM_MEAN_OBJECT` -- char-trigram, C-INDEPENDENT readout D_hat = M_R (no bind with novel
  subject C). Catches low-cardinality "return the popular object". Expected below ARM_REAL.

M-sweep (Director-mandated control (c)): M in {25, 50, 100, 150, 200} training pairs
bundled; transfer should CLIMB with M if real structure exists. M_OP=200 respects the
~200-items/bundle reliable-recall budget at N=8192.

Positive control (Gate D; harness reproduces the mechanism AT THIS REGIME):
`ARM_SYNTH_POSITIVE` = the validated synthetic clustered generator (K=10, sigma=2.0, M=200)
run at N=8192. cited prior MEASURED@data/exp_schema_bundle_structural_transfer_v1/metrics.json
real M=200 gain=+0.590 at N=4096; expect >= 0.15 gain at N=8192. Smoke measured +0.77.

## Pre-registered bands (LOCKED before smoke)

Per relation, primary arm = ARM_REAL; `gain(arm) = arm_acc - random_baseline`:

- **HARD_PASS**: `gain(ARM_REAL) >= 0.2075` (0.20 floor + 5% band-width, META_RULE_L) AND
  `gain(ARM_SHUFFLED) <= 0.05` AND `gain(ARM_RANDENC) <= 0.05` AND
  `(ARM_REAL - ARM_MEAN_OBJECT) >= 0.05` (subject-conditional) AND
  `(ARM_REAL - ARM_SHUFFLED) >= 0.2075` (correspondence-dependent; NOT a shuffle-invariant
  encoding artifact).
- **HARD_FAIL**: `gain(ARM_REAL) <= 0.05` (real at chance) OR
  `(ARM_REAL - ARM_SHUFFLED) <= 0.05` (real not separated from the pairing-shuffled control
  -> the accuracy is a codebook/encoding artifact, e.g. DerivedFrom "nearest-substring-object",
  not schema transfer).
- **MIDDLE_BAND**: `0.05 < gain(ARM_REAL) < 0.2075` or partial gates.

OVERALL verdict: HARD_PASS if ANY relation HP (and synth-positive OK); HARD_FAIL if ALL
relations HF (and synth-positive OK -- the genuine encoder-diagnostic null); MIDDLE otherwise.
synth-positive gain < 0.15 -> HARNESS_SUSPECT (MIDDLE_BAND; real arms uninterpretable).

Sanity rails: FHRR bind-roundtrip >= 0.90; ARM_REAL not saturated (< 0.95 unless
shuffle-invariant confound -> HARD_FAIL).

## HP_SCOPE

HARD_PASS/HARD_FAIL gates apply to `ARM_REAL` ONLY (per relation). ARM_SHUFFLED / ARM_RANDENC
/ ARM_MEAN_OBJECT are controls (expected ~chance; inherit no chain-grade gate).
ARM_SYNTH_POSITIVE is a harness sanity gate, not a substrate-capability claim.

## SCHEMA-VET mandatory fields

- `cardinality_ok`: EXPECTED_N_UNITS = relations(3) x arms(4) x M(5) x seeds(3) = 180
  (smoke 120 at 2 seeds). Verdict emits HARD_FAIL_CARDINALITY_BREACH if under.
- `arms_differ_verified`: True (hash of per-arm accuracy curves; smoke 4/4 distinct).
- `final_metrics_atomicity`: `tmp_replace` (os.replace).
- `except SystemExit: raise` before `except Exception` (no BaseException; no bare except).
- `crlb_n/a`: argmax-transfer has no CRLB noise-floor; chance floor = 1/V_eff (~0.01);
  `discriminator_reachability`: True (HP abs threshold ~0.22 lies strictly between chance
  and saturation).
- `baseline_in_band` (META_RULE_AG): controls ~chance (not saturated); ARM_REAL not
  saturated unless flagged shuffle-invariant confound.
- `calibration_check`: `adaptive_with_discriminator_gate` -- baseline = 1/V_eff computed per
  relation; synth-positive (+0.77 smoke) is the discriminator-fires proof.
- `discriminator survives scale`: SMOKE runs at FULL N=8192 (only seeds 2->3, N_TEST 60->150,
  pool 400->1500 differ). Smoke synth-positive fired +0.77; controls fired (exposed the
  DerivedFrom shuffle-invariant confound).
- `positive_control_arms` (Gate D): ARM_SYNTH_POSITIVE reproduces the validated mechanism at
  the test regime (N=8192), tolerance gate >= 0.15.
- `effective_vs_nominal_parameter_audit`: M is the # training pairs bundled = the actual
  parameter each schema-map mean experiences (ALIGNED; no partition routing).
- `discriminating_fraction`: not a saturation-bracket cell; the M-sweep is the SNR axis and
  the synthetic prior confirms points span [chance, ~0.7] under structure. Gate n/a for real
  relations whose expected outcome is the chance-vs-structure discriminator, not a saturation
  curve.
- `composition_edges`: single mechanism (encode -> holistic-map -> cleanup); SHAPE_MATCH
  (unit phasors throughout; cleanup over unit-phasor codebook).
- `functional_requirements`: (1) encode real entities zero-LLM [char-trigram/random phasor];
  (2) extract shared relation transform [holistic map, validated primitive]; (3) generalize
  to novel subject [bind + codebook cleanup, validated]; (4) discriminate genuine structure
  from artifact [shuffled + randenc + mean-object controls].
- `progress_logging`: `print_flush_true` (all progress lines flush=True; expected wall < 15min
  so timeout < 1800; field included for completeness).
- `cell_chunked`: false (3 seeds in one cell; per-seed checkpoint via _seed_checkpoint;
  total wall tiny). `start_marker_written`: true. `crash_diagnostic_present`: true.
  `heartbeat_present`: n/a (sub-minute per seed; per-seed checkpoint + start-marker suffice).
- `defensive_error_checking`: per-unit failure-class instrumentation (META_RULE_J); specific
  `except Exception` records failure-class + halts seed; no silent continue.

## Compute architecture

Class (b) sequential-CPU with justification: primitives are elementwise complex mul (bind),
vector mean (bundle), V x N cleanup matmul (V<=100 tiny). Per-unit wall << 10s; total smoke
~8s (2 seeds), FULL est ~1-2 min. No N x N matrices; below GPU-batching threshold ->
sequential CPU correct. Storage strategy: bundled (mean) -- the schema map IS a bundle and is
the object under test; NOT a chained-composition cell (META_STORAGE sharded-default n/a).

## Smoke result (LOCAL preview at FULL N=8192, 2 seeds; CANONICAL is remote FULL)

- verdict: HARD_FAIL_NO_REAL_TRANSFER (DIAGNOSTIC).
- synth_positive_gain_mean = +0.77 (mechanism reproduces at N=8192; > 0.15 gate).
- AtLocation: real_acc=0.05 real_gain=+0.04 -> HARD_FAIL (semantic; encoding carries nothing).
- CausesDesire: real_acc=0.05 real_gain=+0.04 -> HARD_FAIL (semantic).
- DerivedFrom: real_acc=0.95 BUT real-shuf=+0.00 -> HARD_FAIL CONFOUND(shuffle-invariant):
  the high number is a nearest-substring-object encoding artifact, NOT subject-conditional
  schema transfer -- the shuffled control correctly exposes it.
- cardinality 120/120, arms_differ 4/4 distinct, zero_llm_calls=0, allow_synthetic=False.

Small-metrics caveat: like the synthetic cell, FULL metrics may be modest in size; legitimacy
gated on run_mode==full + elapsed>1 + the M-curve + synth_positive_gain, not raw byte size.
