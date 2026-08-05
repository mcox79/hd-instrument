# PRE-REG: sense_collapse_floor_v1 (C-A STEP 0 measurement cell)

Status: PRE-REGISTERED before run. Filed 2026-08-05.

## Purpose
Cheap MEASUREMENT (not a build) establishing the HONEST FLOOR for the future sense-structured
hub (C-A). Runs the EXISTING glass-box encoders on a sense-minimal-pair probe and measures whether
they collapse word senses into one vector per surface form. Sets the baseline every downstream C-A
gate is judged against. Mandated by notes/design_vet_semantic_organ_plan.md Axis 2 ("insert a
MEASUREMENT cell ... run random_indexing/composed_encoder_v3 on the sense probe, show single-prototype
collapses senses") and notes/PLAN_grounded_semantic_organ_build.md C-A STEP 0.

Prior-work check (substrate_query.sh "word sense disambiguation polysemy sense collapse
single-vector-per-form"): top hits cosine 0.32-0.38, all WordNet/VerbNet lexical entries (word_sense,
disambiguation-of-sense definitions), NOT prior experiment cells. No prior arc cell measuring this
exists on this substrate -> genuinely novel measurement, not a rediscovery.

## Compute architecture
Class (b) sequential-CPU with justification: N=8 words x 4 sentences = 32 short strings, 4 encoders,
no training loop beyond small closed-form fits (SVD on an 8x32-ish PPMI matrix, one Hebbian pass).
Wall time << 10s total. No GPU benefit; this is the "cell IS a lightweight measurement" exemption.
Storage strategy: no_storage / no_composition (single-shot representation comparison, no chained
retrieval).

## Encoders under test (all glass-box, own-substrate, no borrowed embedding)
1. `hdlab.random_indexing.RandomIndexingEncoder` -- single-prototype BY CONSTRUCTION: `encode(word)`
   takes no context argument; one context vector per surface form, accumulated over all occurrences
   at fit time. Architecturally cannot vary by sentence.
2. `hdlab.concept_encoder.ConceptEncoder` -- single-prototype BY CONSTRUCTION: `encode(sentence)`
   classifies into one of `n_concepts` discrete concept-HD slots and returns that slot's fixed HD
   (`self._concept_hds[best].copy()`). Output space is a finite lookup table indexed by word identity
   (labels = word id, both senses share one label, matching how this encoder is actually used in the
   substrate today); a correctly-classified sentence returns literally the SAME vector regardless of
   sense.
3. `hdlab.composed_encoder_v3.ComposedEncoderV3` -- HAS a context path: `encode_streams(text)` computes
   a fresh VWFA hash-composition + a fresh PPMI trigram-bag sum PER SENTENCE (fit-free at the raw
   stream level once PPMI vocab exists). This is the one candidate that MIGHT show partial
   sense-sensitivity; measured honestly, reported whichever way it lands.
4. `hdlab.ppmi_sparse_encoder.PPMISparseEncoder` -- `encode(text)` sums trigram embeddings over the
   WHOLE sentence per call (also a live per-sentence bag, not a lookup table); same "might partially
   discriminate" candidate class as (3), measured independently since it's a distinct on-disk asset.

## Probe design
N=8 polysemous target forms (includes the exact 4 audit-flagged collision tokens: hard, trick, pay,
cross; +4 more classic polysemy items: bright, sound, light, bear). Each form has 2 senses (A, B),
each sense has 2 disambiguating context sentences (A1/A2, B1/B2) -- 32 sentences total. Content
vocabulary is DISJOINT between sense A and sense B for every form (no shared non-target content word),
so any separation signal reflects sense content, not incidental lexical overlap. Gold sense label
attached to every sentence.

Forced-choice discrimination trial (2AFC, chance = 0.5): for each word, two reference configurations
are used -- ref=(A1,B1) with test={A2 (gold A), B2 (gold B)}, and ref=(A2,B2) with test={A1 (gold A),
B1 (gold B)} -- giving 4 trials/word x 8 words = 32 trials total per encoder. A trial predicts
`argmax_{s in {A,B}} cosine(rep(test), rep(ref_s))`; exact ties (|cos_A - cos_B| < 1e-9, expected for
architecturally-collapsed encoders) are broken by a seeded coinflip (seed=1234), not by index order,
so a truly-collapsed encoder converges to chance rather than being gameable by tie-break order.

Same-sense control (positive control): per word, `cos(rep(A1), rep(A2))` and `cos(rep(B1), rep(B2))`
(same sense, different sentence). Separation scalar per word = mean(same-sense cos) -
mean(different-sense cos over all 4 A-vs-B pairs). Separation ~= 0 (and rep_A == rep_B near-exactly)
is the single-prototype collapse signature; separation > 0 is genuine sense-sensitivity.

## Fit corpus
All 4 supervised encoders (concept_encoder, composed_encoder_v3, ppmi_sparse_encoder) are fit on all
32 probe sentences with `concept_labels = word_index` (0..7) -- i.e. BOTH senses of a form share one
label, because that is how these encoders are actually invoked in the substrate today (word
identification, no sense awareness). `random_indexing.RandomIndexingEncoder` is fit unsupervised via
`fit_corpus()` on the tokenized concatenation of all 32 sentences.

## Pre-registered expected bands (HONEST FLOOR, can-fail)
- HARD-FLOOR (expected, architecturally forced): random_indexing and concept_encoder --
  `cos(rep_A_ref, rep_B_ref) ~= 1.0` (bit-identical or near-identical vector reuse) and forced-choice
  accuracy within `[0.5 - 2*SE, 0.5 + 2*SE]` where `SE = sqrt(0.25/32) ~= 0.088`, i.e. band
  `[0.324, 0.676]` at n=32 binomial trials -- consistent with chance, not a real discriminator.
- CAN-FAIL / positive-surprise band: composed_encoder_v3 (either stream or the alpha=beta=0.5
  combine) or ppmi_sparse_encoder scoring forced-choice accuracy `> 0.676` (>2 SE above chance) AND
  separation scalar clearly `> 0` is a genuine positive surprise -- narrows what C-A must add and
  changes the honest floor. Report exactly which arm crosses this, do not suppress it.
- If ANY encoder's accuracy falls BELOW `0.324` (systematically anti-correlated), flag as an
  implementation anomaly requiring investigation before trusting the floor number.

## Discriminator-fires check
This is a measurement cell, not a pass/fail mechanism cell -- there's no mechanism under test that
needs to "fire." The check that stands in for it here: verify concept_encoder and random_indexing
representations for the SAME target word are bit-identical (or cosine >= 0.999) across both senses,
confirming the collapse is real and not an encoder bug (e.g. a broken argmax that never converges to
the same slot). If concept_encoder misclassifies enough test sentences that `rep_A_ref != rep(A2)`'s
resolved slot, that is reported as a classifier-noise caveat on the floor number, not silently hidden.

## Output
`data/exp_sense_collapse_floor_v1/metrics.json`: per-encoder forced-choice accuracy (+ binomial
p-value vs 0.5), per-encoder separation scalar, per-word raw cosines, and the single headline "honest
floor" number(s) C-A must beat + which encoder is the best existing starting point for the C-A
extension.

## Cell hygiene
- ASCII-only.
- `except SystemExit: raise` / `except KeyboardInterrupt: raise` before `except Exception` (no bare
  except, no `except BaseException`).
- Atomic metrics write (`metrics.json.tmp` -> `os.replace`).
- Start-marker + crash-diagnostic writer (single-shot cell; heartbeat/chunking exempted --
  `cell_chunked: false`, wall time << 10s, no seed axis, `defensive_error_checking:
  "exempt_short_singleshot_cell_start_marker_and_crash_diagnostic_present"`).
- `final_metrics_atomicity: "tmp_replace"`.
- `crlb_n/a: "no quantitative noise-floor formula applies; this is a representational-collapse
  measurement, not a capacity/CRLB cell"`.
- Self-test constructs the real encoder objects at tiny scale (2 words) before the full 8-word probe
  runs, per SCHEMA-VET real_code_path gate.
- Dispatch: LOCAL-only, in-process/foreground `python experiments/exp_sense_collapse_floor_v1.py`.
  No queue_add.sh, no remote, no background/nested execution. Commit locally; NO origin push
  (per task instruction).
