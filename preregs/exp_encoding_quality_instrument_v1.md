# Pre-reg: `exp_encoding_quality_instrument_v1` (PLAN STEP 1, COMPONENT #1 word/concept encoding)

STATUS: **PRE-REGISTERED BEFORE ANY RUN.** Every threshold in section 5 was written to disk and
committed before the cell was executed for the first time. No threshold in this file may be edited
after a run; a superseding pre-reg must be a new file with a new version suffix.

Serves `notes/PLAN_NEXT_12H.md` STEP 1 and component-table row 1
(`word/concept encoding | NONE - BUILD FIRST | unmeasured`).

**SCOPE, stated up front so it cannot be misread later.** This cell builds and VALIDATES an
instrument. It does **NOT** score our production encoding. Scoring our encoding is STEP 2 and is
explicitly out of scope here. Every arm in this cell is a *synthetic encoder whose true quality is
known by construction*, because an instrument can only be validated against arms whose answer is
already known.

---

## 0. HOW I ENUMERATED (STANDING RULE 6 / LESSONS 4: an absence claim requires an enumeration)

1. `ls hdlab/` — **full listing read by eye, 141 entries**, not filtered by keyword first. Encoder-
   or measurement-relevant modules found: `char_trigram_encoder`, `char_positional_encoder`,
   `concept_encoder`, `composed_encoder_v3`, `gsbc_graded_encoder`, `ppmi_sparse_encoder`,
   `random_indexing`, `token_vocab`, `hippocampal_encoder`, `dg_pattern_separation`, `whitening`,
   `int8_dense`, `metrics`, `cleanup_family`, `modern_hopfield_readout`, `lexical_similarity`,
   `grounded_similarity`, `kb_encoder_registry`, `encoder_retrain_persist`, `vwfa`, `late_combine`.
2. `ls experiments/` — **5859 files**; filtered by regex
   `encod|discrim|recover|capacit|round.?trip|instrument|quality`. **~430 filenames matched**; the
   full match list is reproduced in the scan-out fragment. I then opened the **headers/docstrings of
   six** closest candidates in full (named in section 2).
3. `data/capability_registry.jsonl` — `tools/capability_registry_audit.py --serves encoding` is
   **not a supported invocation** (`error: unrecognized arguments: --serves encoding`; supported
   flags are `--dry-run --stale-days --json --self-test --skip-hard-pass-scan --run-witnesses
   --append-json`). I therefore enumerated the registry directly in Python: **198 rows total, 42
   rows matching `encod` anywhere in the record.** All 42 are listed in the scan-out fragment.
4. `ls preregs/` — **3794 files**; filtered on `encod|instrument|discrimin|recover`.
5. `ls data/`, `ls data/datasets/`, `ls data/corpora/`, `ls data/encoder_eval_benchmarks/` for
   inputs that are not under the do-not-touch `data/foundation/**`.

**Residue I am NOT claiming to have assigned.** I did not open the bodies of the ~430 matching
experiment files; I opened six. Section 2's claim is therefore: *no module or cell in the
enumerated set presents itself as an isolated encoding-quality instrument with a null arm and a
known-answer arm*, and it is COMPLETE for hdlab (all 141 read) and for the registry (all 198 rows
machine-scanned), but **PARTIAL for the experiment corpus** (filenames + 6 bodies).

---

## 1. WHAT MAKES THIS DIFFERENT FROM EVERY PRIOR ENCODER CELL — and why the prior ones cannot be reused

The single load-bearing design decision, and the one that killed three foundation-validator
versions:

> **A random encoding is near-OPTIMAL on identity metrics and near-CHANCE on structure metrics.**

Random indexing works *because* iid random codes are almost orthogonal, so a random code is close to
the best possible answer for "can I read back which word this was". Any instrument that scores
encoding quality with a single number mixing identity and structure is therefore **unfalsifiable**:
its null is near-ceiling on half the metric. This is the mechanism behind the reported incident that
"a random decoy scored 0.76 where it should have been near zero" — a decoy was measured on an
identity-flavoured metric, where random is *supposed* to score high.

**Consequence, binding on this design:** the instrument reports **two axes, each with its OWN
matched null and its OWN known-answer arm.**

| axis | question | correct NULL (must be at chance) | correct KNOWN-ANSWER (must be at ceiling) |
|---|---|---|---|
| **IDENTITY** | is *which word this is* preserved? | `A_COLLAPSE` (all words -> one vector) | `A_ORACLE_ONEHOT` |
| **STRUCTURE** | does the geometry carry anything BEYOND identity? | `A_RANDOM_IID` and `A_SHUFFLED_PLANTED` | `A_PLANTED_STRUCTURE`, `A_ORTHOGRAPHIC` |

`A_RANDOM_IID` is deliberately present in BOTH columns' logic: it is predicted **near-ceiling on
IDENTITY and at chance on STRUCTURE**, and both predictions are gated. An instrument that cannot
reproduce that split is not measuring what it claims.

---

## 2. PRIOR ART — what exists, what it measures, why it is not this (WIRE DON'T ISLAND)

Reused, not reimplemented:

- **`hdlab/char_trigram_encoder.CharTrigramEncoder`** — imported and used verbatim as the
  `A_ORTHOGRAPHIC` arm. Credit: Kanerva-style bag-of-trigrams; the module is pre-existing repo work.
- **`tools/saturation_negative_control.py`** — imported (`nn_recall_at_1`, `iid_gaussian_keys`) and
  its `--self-test` run as a gate, per the STEP 1 brief.
- **`experiments/_seed_checkpoint.py`** (`get_output_dir`, `write_metrics`) and
  **`tools/exp_checkpoint.py`** (`unit_key`/`record_unit`/`load_units`) — repo conventions, per
  `CLAUDE.md` "Multi-unit cell checkpoint/resume (MANDATORY)".
- **`data/encoder_eval_benchmarks/simlex999.txt`** — SimLex-999 (Hill et al. 2015), already on disk,
  cached by `exp_clean_encoder_eval_harness_v1`.
- **`data/corpora/simplewiki/simplewiki_clean_v1.txt`** — real word frequencies (CC BY-SA dump,
  2026-07-02), counted by this cell; no `data/foundation/**` is read.

Closest existing cells, and why none is the instrument (bodies/headers read in full):

| cell | what it measures | why it is not an isolated encoding instrument |
|---|---|---|
| `exp_clean_encoder_eval_harness_v1.py` (851 lines) | Spearman of cosine vs human similarity on WS353/SimLex, 4 encoder arms | **Closest prior art, and genuinely clean** (no substrate state in the loop). But: it is an encoder *bake-off*, not an instrument — no null arm, no known-answer arm, no recoverability, no load sweep, no per-stage accounting. Its "sanity" check is one planted word pair, not a validity gate. |
| `exp_substrate_pp8_learned_discriminability_probe_v1.py` | concept coverage retained after token pruning | measures a *routing/pruning* decision, not a word's code |
| `exp_substrate_embedding_norm_gate_discriminability_v1.py` | VQ coverage under a norm gate on Llama residuals | measures a gate on an external model's activations |
| `exp_substrate_abduction_f1b_..._recoverability_vs_infopreservation_cpu_v1.py` | dissociates recoverability from info-preservation for a *binding operator* | operator-level, synthetic Markov, not word encoding |
| `exp_path_c_substrate_owned_encoder_FAIR_HARNESS_v2.py` (1688 lines) | BPC / top-1 / MRR of an encoder used as a language model | **downstream by construction** — scores an LM head, which is exactly what STEP 1 must exclude |
| `exp_encoder_headtohead_benchmark_gpu_v1.py` | recall@k on HotpotQA | fully downstream (retrieval task) |
| the ~330-file `*capacity*` family | bundle/store capacity of *synthetic random* codes | measures the STORE at fixed random codes; the code itself is not the variable |

Registry: **42 of 198 rows mention `encod`.** Every one is an *encoder* or an encoder-consuming
capability (`char_trigram_encoder`, `concept_encoder`, `gsbc_graded_encoder`,
`random_indexing_open_vocab_encoder`, `char_positional_encoder`, `hippocampal_encoder_dg_ca3_pipeline`,
`kb_encoder_registry`, ...). **Zero rows are an encoding-QUALITY INSTRUMENT.** Also noted, because it
bears on STEP 2: the `char_trigram_encoder` row's status string already carries a 2026-08-15
correction that its "WIRED via reasoner" claim was wrong.

**Conclusion: no usable organ exists to extend. This cell builds one, and reuses the five components
listed above rather than reimplementing them.**

---

## 3. THE OBJECT UNDER TEST

An **encoder** is any function `encode(word: str) -> np.ndarray[float32, D]`. The instrument is a
pure function of an encoder and a fixed word list; it touches no store, no reader, no selection
stage, no retrieval index. Codes are L2-normalised before every measurement.

**Vocabulary (fixed rule, no post-hoc filtering).** Word frequencies counted from the first
`CORPUS_BYTES` of `simplewiki_clean_v1.txt` (`CORPUS_BYTES = 64_000_000` full, `8_000_000` smoke;
read as bytes, truncated at the last newline so the count is deterministic). Tokens lowercased,
`[a-z]+` only, length >= 3. Rank by count descending, **drop the top 100** (function words), take
the next `V`. `V = 4096` (full) / `512` (smoke). `D = 1024` (full) / `256` (smoke), per the
`CLAUDE.md` default-N convention.

**Probe noise.** A probe for word `w` at level `sigma` is `code(w) + n` where `n` is Gaussian with
**L2 norm exactly `sigma`** (norm-matched, so `sigma` is directly interpretable as a noise-to-signal
ratio against unit-norm codes). `SIGMAS = [1.0, 4.0, 8.0, 16.0, 32.0]` full, `[1.0, 8.0, 32.0]`
smoke. These were fixed analytically, not tuned: the identification cliff for dense unit codes sits
near `sigma ~ sqrt(D / (2 ln V))` = `sqrt(1024/16.6)` ~ **7.9**, so the grid brackets the cliff by
about a factor of 4 on each side.

---

## 4. THE FOUR MEASURES

**M1 DISCRIMINABILITY.** For word `w`, argmax cosine of a noise-corrupted probe against a pool of
`w` plus `K = 31` distractors (chance `1/32 = 0.03125`), for two independently-built pools:
- **(a) orthographic near-neighbours** — the 31 vocabulary words with highest character-trigram
  Jaccard similarity to `w`, computed **from the strings only**, never from any code.
- **(b) frequency-matched controls** — the 31 vocabulary words nearest to `w` in `log(count)`,
  excluding any word already in pool (a).
Reported as `disc_ortho` and `disc_freq`.

**M2 RECOVERABILITY.** Round-trip identity with no reader and no selection: encode `w`, probe with
its noise-corrupted code, argmax cosine over the **whole store of `N` codes**. Chance `1/N`.

**M3 STABILITY UNDER LOAD.** M2 swept over `N_SWEEP = [128, 512, 1024, 4096]` full /
`[64, 128, 512]` smoke. Reported: the curve, and `knee_N` = the largest swept `N` at which
recoverability >= 0.50 (`None` if never).

**M4 INFORMATION DESTROYED PER STAGE.** A fixed 5-stage chain, each stage measured with the SAME
probe construction at `sigma = 1.0`, `N = N_GATE`:

| stage | representation |
|---|---|
| `S0_ORACLE` | one-hot over the vocabulary (`D = V`) — the full-information reference |
| `S1_ENCODE` | the encoder's own output, L2-normalised |
| `S2_ENCODE_SIGN` | `sign(S1)` — the quantisation stage |
| `S3_BUNDLE` | `S1` codes summed in groups of `B = 8`; `w` counts as recovered iff it is in the top-`B` of cosine against the bundle containing it |
| `S4_BUNDLE_SIGN` | `sign(S3)` |

Accuracy is converted to bits by the Fano lower bound
`I(p, N) = max(0, log2(N) - H_b(p) - (1-p)*log2(N-1))`; `destroyed_bits` for a stage is the drop
from the preceding stage. This is a LOWER BOUND on information retained, and is labelled as such in
the metrics.

**M5 STRUCTURE (the second axis).** `structure_ap(codes, labels)` = mean average precision of
same-label words when every other word is ranked by cosine, averaged over `AP_PROBES = 1024` (full)
/ `128` (smoke) probe words drawn with a fixed seed. `lift = ap / chance`, chance being the same-label
base rate. Three golds, none of which touches our substrate:
- `GOLD_ORTHO` — shared first 3 characters (surface only; groups of size < 3 excluded from scoring
  but retained as distractors).
- `GOLD_FREQBAND` — frequency decile.
- `GOLD_PLANTED` — `index mod 32`, the synthetic gold that `A_PLANTED_STRUCTURE` is built from.
Plus a pair-based semantic readout: **`simlex_rho`** = Spearman between cosine and human similarity
over SimLex-999 pairs with both words in vocabulary.

---

## 5. ARMS AND PRE-REGISTERED THRESHOLDS (fixed before any run)

### 5a. Arms (all synthetic; truth known by construction)

| arm | construction | predicted IDENTITY | predicted STRUCTURE |
|---|---|---|---|
| `A_ORACLE_ONEHOT` | one-hot, `D = V` | **ceiling** | none (by construction) |
| `A_RANDOM_IID` | deterministic blake2b(word+seed) -> Gaussian, `D` | near-ceiling | **chance** |
| `A_COLLAPSE` | one shared vector + 1e-3 idiosyncratic noise | **chance** | chance |
| `A_ORTHOGRAPHIC` | `hdlab.char_trigram_encoder.CharTrigramEncoder(n_dim=D)` | high, but **low vs pool (a)** | **high on GOLD_ORTHO** |
| `A_PLANTED_STRUCTURE` | `normalize(g[label] + 0.3 * eps_word)`, label = `GOLD_PLANTED` | partial | **ceiling on GOLD_PLANTED** |
| `A_SHUFFLED_PLANTED` | `A_PLANTED_STRUCTURE` codes, word->code assignment permuted | unchanged from planted | **chance on GOLD_PLANTED** |
| `A_PLANTED_SEMANTIC` | codes fitted by gradient descent to the SimLex gold, on covered words only | n/a | **ceiling on `simlex_rho`** |

Seeds `[7, 17, 23]` full / `[7]` smoke; the seed salts every deterministic hash. Reported values are
seed means; gates are evaluated on seed means. `N_GATE = 1024` full / `512` smoke.

### 5b. NULL GATE — if ANY of these fails, verdict is `INSTRUMENT_STILL_LOOSE`, **no quality number is published, and the run stops.**

| id | condition | chance |
|---|---|---|
| **N1** | `A_COLLAPSE` recoverability at `N_GATE`, `sigma = 1.0` **<= 0.05** | 1/1024 |
| **N2** | `A_RANDOM_IID` `GOLD_ORTHO` lift **<= 1.15** | 1.0 |
| **N3** | `A_RANDOM_IID` `GOLD_FREQBAND` lift **<= 1.15** | 1.0 |
| **N4** | `A_RANDOM_IID` `abs(simlex_rho)` **<= 0.10** | 0.0 |
| **N5** | `A_SHUFFLED_PLANTED` `GOLD_PLANTED` lift **<= 1.15** AND its recoverability **>= 0.90** | — |
| **N6** | `A_COLLAPSE` `disc_ortho` and `disc_freq` both **<= 0.10** | 0.03125 |

N5 is the sharpest of the six: it demands the two axes be *independent* — a permutation that
destroys structure while leaving identity untouched must move the structure readout to chance and
leave the identity readout at ceiling. An instrument that fails N5 is measuring one thing and calling
it two.

### 5c. KNOWN-ANSWER GATE — an instrument that passes the null but fails here cannot detect quality at all.

| id | condition |
|---|---|
| **K1** | `A_ORACLE_ONEHOT` recoverability at `N_GATE`, `sigma = 1.0` **>= 0.95** |
| **K2** | `A_ORTHOGRAPHIC` `GOLD_ORTHO` lift **>= 3.0** |
| **K3** | `A_PLANTED_STRUCTURE` `GOLD_PLANTED` lift **>= 5.0** |
| **K4** | `A_PLANTED_SEMANTIC` `simlex_rho` **>= 0.50** (gates the SEMANTIC READOUT only, see 5e) |
| **K5** | `A_RANDOM_IID` recoverability at `N_GATE`, `sigma = 1.0` **>= 0.90** — the explicit statement that random is GOOD on the identity axis, which is the whole reason the two axes are separated |

### 5d. SATURATION / CAN-GO-DOWN GATE (a metric that cannot go down is not a measurement)

| id | condition |
|---|---|
| **S1** | recoverability spread at `N_GATE`, `sigma = 1.0` across arms **>= 0.50** (max - min) |
| **S2** | `A_ORACLE_ONEHOT` recoverability at `sigma = 32.0`, `N_GATE` **<= 0.80** — the ceiling arm must be pushed off the ceiling by the instrument's own noise axis |
| **S3** | `structure_ap` lift spread on `GOLD_ORTHO` across arms **>= 2.0` |
| **S4** | `tools/saturation_negative_control.py --self-test` exits 0, AND its `nn_recall_at_1` on `iid_gaussian_keys` is recorded in the metrics as the documented null-input reference |

### 5e. VERDICT LOGIC (evaluated in this order, no exceptions)

1. any NULL gate fails -> **`INSTRUMENT_STILL_LOOSE`**. No quality number published. STOP.
2. else any of K1/K2/K3/K5 fails -> **`INSTRUMENT_CANNOT_DETECT_QUALITY`**. STOP.
3. else any SATURATION gate fails -> **`INSTRUMENT_SATURATED`**. STOP.
4. else -> **`INSTRUMENT_VALIDATED`**, with `semantic_readout_validated = (K4 passed)` reported as a
   separate boolean. If K4 fails, the identity and structure axes are still validated and the
   semantic readout is marked NOT VALIDATED and must not be quoted.

**No arm of this cell is our production encoder, so no number produced here is a score of our
encoding.** Any future citation of this cell as evidence about our encoding is a misreading.

---

## 6. WHAT THIS INSTRUMENT DOES NOT MEASURE (stated before the run so it cannot be quietly claimed later)

- **Meaning beyond SimLex-999 similarity judgements.** `GOLD_ORTHO` and `GOLD_FREQBAND` are surface
  and statistical golds; they are validity scaffolding, not meaning. The only semantic gold here is
  SimLex, it is pair-based, and it is gated separately for exactly that reason.
- **Compositionality, binding, roles, polysemy, context-sensitivity.** One word -> one static code.
- **Anything downstream.** No store, no reader, no selection, no retrieval.
- **Our production encoder.** STEP 2.
- **`A_ORACLE_ONEHOT` runs at `D = V`, not `D`.** It is an information-theoretic reference, and it is
  not dimension-matched to the other arms. Any comparison that treats it as a same-`D` competitor is
  invalid.
- The Fano number is a **lower bound** on retained information, not an estimate of it.

## 7. AMENDMENTS (both made BEFORE the cell was ever executed on real data; self-test evidence only)

Two definitional defects were found by the cell's own formula self-tests, before any
experimental run. Both are recorded here rather than silently fixed, and both TIGHTEN the
instrument (each made a null arm score LOWER, never higher). No threshold in section 5 changed.

**A1 - argmax tie-breaking put a NULL arm at the ceiling.** With a degenerate encoder every code
is bit-identical, so every similarity is exactly equal and `np.argmax` returns index 0
deterministically. Because the target sits at candidate position 0 of the discriminability pool,
`A_COLLAPSE` scored **`disc = 1.0000`** — a metric pinned at the ceiling with zero information
anywhere in the path, which is precisely the failure this cell exists to prevent. Fix: `_tiebreak()`
adds uniform noise of magnitude `1e-12` to float64 similarities in all four readouts
(recoverability, discriminability, bundle survival, structure AP). `1e-12` breaks exact ties
without touching any real difference (float32 cosine resolution is ~`1e-7`). A regression guard is
now self-test #8.

**A2 - `chance` for the AP readout is now an EMPIRICAL permutation baseline, not the base rate.**
Average precision of a *random* ranking exceeds the same-label prevalence on short lists. With the
base-rate denominator a genuinely null encoder scored `lift = 1.51` in self-test, which would have
tripped the `<= 1.15` null gates for a reason that has nothing to do with the encoder. `chance` is
therefore the mean AP of `AP_RAND_REPEATS = 4` random score draws over the identical probes and
labels. A null encoder now scores `lift = 1.00` by construction, which is the property N2/N3/N5a
depend on. This is a permutation control in the denominator; it does not touch any threshold.

## 8. RESOURCES

CPU only, numpy, single-threaded (`OMP_NUM_THREADS=1` set in-file before numpy import, per
`CLAUDE.md`). No GPU, no queue dispatch, no network. Expected runtime: smoke < 2 min, full
< 40 min. Per-unit checkpointing via `tools/exp_checkpoint.py`. Output
`data/exp_encoding_quality_instrument_v1/metrics.json` (smoke: `..._smoke/`).
