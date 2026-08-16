# PRE-REGISTRATION -- exp_meaning_asset_fair_test_v1

Written BEFORE any arm was scored. Bands in section 5 are fixed and are not edited after any run.

Parent instruments (UNCHANGED, imported as libraries, never edited):
- `experiments/exp_encoding_quality_instrument_v2.py` at `542e1fc0d` (21/21 gates)
- `preregs/exp_encoding_quality_instrument_v2.md` (thresholds carried forward)
- `preregs/exp_encoding_quality_instrument_v1.md` (FROZEN parent)

## 0. WHY THIS CELL EXISTS

`exp_encoding_quality_instrument_v2` measured the DEFAULT LIVE word encoder (a sha256 -> bipolar
hash) and found it is the structure-axis null BY CONSTRUCTION. That is a correct statement about
the DEFAULT PATH and an incorrect statement about the PROJECT: meaning-bearing encoder assets were
BUILT and left UNWIRED, and were not arms in v2 (v2's own disclosure list says so verbatim:
"NOT SCORED: ... any of the 11 encoder-named hdlab modules that are not on the live path").

A fair test of a WEAK implementation proves that setup failed, not that the capability is
impossible. This cell gives the BUILT assets the strong version of the test.

## 1. THE ASSETS UNDER TEST (enumerated from disk, reconciled to the registry afterwards)

| arm family | asset | native d |
|---|---|---|
| `ASSET_V2_*` | TinyTransformer v2, `data/exp_scale_meaning_learn_arc_heldout_v2/ckpt_seed_7.pt` | 512 |
| `ASSET_RETRAIN_*` | minimal-unfreeze successor, `data/exp_encoder_retrain_persist_v1/ckpt_seed_7.pt` | 512 |
| `CTRL_RANDINIT_*` | SAME architecture + SAME tokenizer, UNTRAINED (STEP C random-init arm) | 512 |
| `ASSET_NORMS12` | Lancaster sensorimotor + Brysbaert concreteness via `hdlab/grounded_similarity.py` | 12 |

`data/exp_scale_meaning_learn_arc_heldout_v3_relobj/ckpt_seed_7.pt` is the WRONG checkpoint
(correction C6, `HARD_FAIL_ARCHITECTURE_BOUND`). It is loaded ONLY to assert by sha256 that the
arms under test are NOT it.

Three read-out variants per learned checkpoint, because "the asset failed" must not mean "one
weak read-out failed":
- `_TOKEMB`  mean of the input-embedding rows of the word's BPE pieces (no transformer)
- `_ISOL`    mean-pool of the contextual token reps of the word encoded ALONE
- `_CTX`     type vector = mean over up to K corpus occurrences of the word's OWN token-span
             contextual reps. THE STRONG VERSION, and the exact analogue of how the live
             `P_LIVE_CONCEPT` profile is accumulated.

## 2. WHAT IS HELD IDENTICAL TO THE HASH-ENCODER RUN

Vocabulary, golds, distractor pools, sigmas, N sweep, AP probe count, seeds, tie-break, chance
baseline and every metric function are IMPORTED from the v2 module, not reimplemented.
Gate REG1 (section 5) requires that re-running an instrument arm through this harness reproduces
the published v2 number EXACTLY; if it does not, no asset number is published.

Deviation, declared here: this cell adds d = 512 and d = 12 blocks (the assets' NATIVE
dimensionalities). Every floor and reference arm is RE-RUN at the same d inside each block, so
every comparison is d-matched. No comparison is made across blocks.

## 3. THE FLOOR (standing rule: a gate is a CI-separated margin over the strongest floor)

`max(A_ORTHOGRAPHIC, A_FREQUENCY, <arm>_SHUFFLED)` on the IDENTICAL scorer / n / pool / gold:
- `A_ORTHOGRAPHIC` -- `hdlab.char_trigram_encoder`, spelling only. THIS FLOOR HAS BEATEN THE
  SYSTEM BEFORE (8.70% vs 4.80%, `exp_orthographic_floor_vet_v1`).
- `A_FREQUENCY` -- NEW standalone floor: 64 RBF bumps over log corpus frequency, fixed random
  projection to d. Zero spelling, zero meaning, frequency only. Standalone, not a shortcut added
  on top of the system under test.
- `<arm>_SHUFFLED` -- the arm's own rows permuted across words. Preserves identity and norms
  exactly, destroys structure.
Additional non-floor control: `CTRL_CONCRETENESS_ONLY` (Brysbaert concreteness alone), because a
concreteness confound has inflated a learned-encoder result on this project before.

## 4. THE THREE REPORTED AXES, NEVER AVERAGED

1. IDENTITY -- recoverability curve, `sigma_half`, discriminability vs orthographic and
   frequency-matched pools. A RANDOM CODE IS NEAR-OPTIMAL HERE BY DESIGN; a high score is not a win.
2. STRUCTURE -- AP lift on GOLD_ORTHO (spelling), GOLD_FREQBAND (frequency), GOLD_PLANTED
   (must be ~1.0 for every real arm), and SimLex-999 rho, WHICH IS THE ONLY SEMANTIC GOLD.
3. BUNDLING SURVIVAL -- the v2 single-criterion top-B stage chain; the reported quantity is bits
   destroyed by the SUM (S2 -> S3) out of the log2(N_GATE/B) ceiling.

## 5. BANDS AND GATES, FIXED NOW

VALIDITY GATES (if any fails, NO asset number is published):
- `REG1` P_LIVE_WORD at d=256, seed 7 reproduces the published v2 `simlex_rho` and three golds'
  `lift` to within 1e-9.
- `REG2` `A_RANDOM_IID` |SimLex rho| <= 0.10 and GOLD_ORTHO lift <= 1.15 at every block d.
- `REG3` `A_COLLAPSE` recoverability <= 0.05 at every block d.
- `REG4` `A_ORTHOGRAPHIC` GOLD_ORTHO lift >= 3.0 at every block d.
- `REG5` sha256 of every loaded checkpoint matches the recorded value AND differs from the
  `v3_relobj` checkpoint's sha256.
- `REG6` `CTRL_RANDINIT_*` codes differ from `ASSET_V2_*` codes (arms-must-differ).

HEADLINE BAND, per asset arm, on the STRUCTURE axis, SimLex rho, paired bootstrap
(10,000 resamples over the covered pairs) of the DIFFERENCE `arm - max_floor`:
- **CLEARS THE FLOOR**: 95% CI of the difference lies entirely above 0 AND point margin >= 0.05.
- **MIDDLE_BAND / NOT ESTABLISHED**: CI contains 0.
- **BELOW THE FLOOR**: 95% CI lies entirely below 0.
The same three-way band is applied, and reported separately, to each gold's AP lift (paired
bootstrap over the shared probe set) and to the trained-vs-random-init difference.

BUNDLING BAND (reported, not gated): bits retained through S2 -> S3 out of the 7.000-bit ceiling.
An asset retaining < 0.5 bits has not solved the flat-sum problem regardless of its structure score.

## 6. DISQUALIFIERS

Any asset requiring an EXTERNAL LLM in the runtime path is disqualified regardless of score. The
TinyTransformer is from-scratch, 27.17M params, trained by this project on ARC text with a
from-scratch 16k BPE; it is not an external LLM. Its per-word codes are computed ONCE offline into
a static table, so nothing is called at inference. `data/lambda_batch_results/**` Llama QLoRA
checkpoints ARE external-LLM artifacts and are enumerated but NOT scored.

## 7. RESUME KEY

`tools/exp_checkpoint.py` is used for per-unit resume. Its known defect (`unit_key` ignores N) is
avoided by putting the FULL config fingerprint -- run mode, V, D, CORPUS_BYTES, N_SWEEP, SIGMAS,
AP_PROBES, K_CTX and a code version tag -- into every unit key, so a smoke unit can never be
reloaded by a full run. `tools/exp_checkpoint.py` is NOT edited by this cell.

## 8. AMENDMENTS

**A1, 2026-08-15, BEFORE ANY RUN.** `REG1` is a FULL-SCALE-ONLY gate. The published v2 numbers are
the MEAN over the three seeds at V=4096; a smoke run uses V=512 (a different vocabulary) and one
seed, so the reproduction is not evaluable there. At smoke scale REG1 is recorded as
`SKIPPED_SMOKE_SCALE` and is never counted as a pass. Reason: found while wiring the gate, not
after seeing any result. No threshold changed.
