# Pre-registration: exp_encoder_swap_behind_fixed_brain_stack_v1

- **Filed:** 2026-08-13, BEFORE the FULL run.
- **Cell:** `experiments/exp_encoder_swap_behind_fixed_brain_stack_v1.py`
- **Output:** `data/exp_encoder_swap_behind_fixed_brain_stack_v1/metrics.json`
  (smoke writes to a SEPARATE dir, `..._smoke/`, via `_seed_checkpoint.get_output_dir`)

## Question

The USER's standing recollection: *"any trained solution was inferior to a simpler ingestion
when paired with brain faithful machinery behind it."* An enumeration of all 7,587 `metrics.json`
on disk found every within-cell trained-vs-simple head-to-head either ties or favours the SIMPLE
arm — but also found that **no cell has ever swapped the encoder while holding a full
brain-faithful downstream stack fixed**. This cell runs that missing comparison.

## Correction to the spawn brief (checked against the code, 2026-08-13)

The brief specified the fixed stack as `hdlab.cleanup_family.iterative_attractor` (CA3) + FHRR
bind/unbind + `hdlab/situation_model_multibank.py`, and directed starting from
`exp_layer_05_production_wiring_skeleton`. Three parts of that did not survive contact:

1. **`exp_layer_05_production_wiring_skeleton` cannot host this question.** Its corpus
   (`build_corpus`, `exp_substrate_stage1_apply_exp3e_layer075_v3_clean_arc_closure_2026_07_03.py:194`)
   is entity names drawn from a fixed nonsense list rendered as `"The <r> of <e> is <v>."`.
   There is no distributional semantics in it for any encoder to have learned. A trained encoder
   **cannot** beat a lexical encoder there *by construction* — the discriminator's positive
   direction is unreachable, which is exactly the "no range by construction" defect this prereg
   is required to rule out. Rejected.
2. **That skeleton does not use `cleanup_family.iterative_attractor`.** Its cleanup is a codebook
   `phase_cos_batch` argmax (lines 502-517). Grep for `cleanup_family` in it returns nothing.
3. **`situation_model_multibank` is imported by no cell in either candidate chain** — only by
   `exp_situation_model_multibank_capacity_v1.py` and the two `exp_causal_link_comprehension_fuller_v*`
   cells.

**Substituted harness:** the situation-model assembly loop
(`exp_continuous_curriculum_learn_as_you_go_v1` -> `..._harder_construction_generalization_v1`
-> `exp_situation_model_assembly_encoder_backed_v1`), whose loop is native FHRR bind/unbind via
`hdlab.binding` (`exp_situation_model_assembly_binding_wm_coref_v1.py:141`). This is chosen because
it is **arm A's home turf**: the tuned checkpoint's certified lift (atom math seq 29596) was
measured on exactly this harness. Steel-manning the trained arm is the point — a simple encoder
matching it *here* is a much stronger result than a simple encoder winning on a corpus rigged
against transformers.

## Fixed stack (bit-identical across all six arms)

Only the token -> vector map varies. Everything below is the same code for every arm:

| component | source |
|---|---|
| v2 BPE tokenizer (16000), `SENT_CAP=16`, pad mask | `eb.EncoderExtractor` |
| `pca_whiten` read-conditioning | `rc.Conditioner` |
| `role_attn` position-free role-cue attention pooling | `eb.EncoderExtractor` |
| context-invariant per-slot colour oracle | `eb.EncoderExtractor.build()` |
| situation-model assembly loop, native FHRR bind/unbind | `hdlab.binding` via `clean` |
| decoded-slot readout, per-query-type scoring | `eb.run_arm_decoded`, `lt.score_extractor` |

Implementation: `_SwapExtractor(eb.EncoderExtractor)` overrides **only** `_encode_raw`'s
token -> vector step and reproduces `V2Transformer.token_reps`' contract exactly (L2-normalize
real tokens, zero pads), so no downstream component can tell which arm produced the reps.

## Arms

| arm | encoder | role |
|---|---|---|
| **A** `A_tuned_ckpt` | LANDED asset via `hdlab.encoder_retrain_persist.load_improved_encoder(seed)` | treatment |
| A0 `A0_frozen_base` | `eb.V2_CKPT` frozen base v2 | provenance / positive control, **not** in the discriminator |
| **B** `B_char_trigram` | `hdlab.char_trigram_encoder.CharTrigramEncoder(n_dim=512)` per token surface | the simple comparator |
| C `C_ppmi` | `hdlab.ppmi_sparse_encoder.PPMISparseEncoder(n_dim=512)`, PPMI+SVD on an unsupervised render corpus | second simple comparator |
| D `D_random_init_twin` | freshly constructed `base.V2Transformer` with **arm A's exact `model_cfg`**, untrained | architecture-matched null |
| E `E_scramble_floor` | arm A's tuned weights, token ids through a fixed random vocab bijection | scramble floor |

Arm D is a genuine twin: same class, same `vocab/max_len/d_model/n_layers/n_heads/ffn_mult/pad_id`,
asserted to have an identical `state_dict` key set to arm A. (First implementation hand-zeroed all
`dim<2` parameters, which zeroed the LayerNorm gains and produced an all-zero forward pass; the
self-test's dead-rep gate caught it. Fixed by using the module's own default init.)

## Checkpoint provenance (fail-loud, verified by content hash)

`exp_diag_learned_encoder_synonym_sibling_deep_wall_v1.py:104-105` hardcodes its checkpoint to
`data/exp_scale_meaning_learn_arc_heldout_v3_relobj/ckpt_seed_7.pt` — the weights of a
`HARD_FAIL_ARCHITECTURE_BOUND` run — and that one wrong path produced a headline "the encoder
fails" result. This cell therefore pins arm A by sha256, not by path:

```
seed  7  data/exp_encoder_retrain_persist_v1/ckpt_seed_7.pt   29fbefbcb89c7b547e1f271f9e2afadb3c7a6084f86b9eef13d10165135bfdfc
seed 13  data/exp_encoder_retrain_persist_v1/ckpt_seed_13.pt  9460ed648870f637a1ea27594dfdac10f25af1ef8d5b9485502437324ea90763
seed 19  data/exp_encoder_retrain_persist_v1/ckpt_seed_19.pt  97de6d1d6b728efa9e9f23d8ca07acc060d10fbad187a637efdc9a55e07167fe
FORBIDDEN data/exp_scale_meaning_learn_arc_heldout_v3_relobj/ckpt_seed_7.pt  f03051248c26a756d09d0076697cb470b477405cbaa289376e4a876bef3cb17a
```

`verify_arm_a_checkpoint()` raises `PROVENANCE_VIOLATION` on a mismatch or on the forbidden hash,
and `build_arm` additionally asserts arm A's loaded `state_dict` **differs** from the frozen base's.
The hash actually loaded is written to `metrics.json` (`arm_a_ckpt_sha256`, and per-unit `diag`).

## AMENDMENT (2026-08-13, after the smoke gate, BEFORE the FULL run)

The smoke gate did its job twice. **The delta bands below were NOT touched** — what changed is the
readout and the floor predicate, both because a control failed. Disclosed in full:

**A1. The first scramble floor was invalid and was replaced.** Arm E was originally "arm A's tuned
weights, token ids through a fixed random vocab bijection". At `EVAL_N=12` it scored **0.7652 —
the HIGHEST of all six arms**, above the tuned encoder. Diagnosis: the colour oracle is built by
`EncoderExtractor.build()` *using the same encoder*, so a deterministic relabeling of the input
alphabet is absorbed by the oracle and the pipeline is invariant to it. It was not a floor at all.
Replaced with a **text scramble**: `_encode_raw` deranges the unique-text batch, destroying the
request<->sentence correspondence, which nothing downstream can compensate. Arm E now reads
0.028-0.035, a genuine floor.

**A2. The headline readout moved from `span` to `role_attn`, because `span` saturates.** Under
`span` the harness supplies each slot's character offsets, and **every encoder arm scores exactly
1.000 — including `D_random_init_twin`, an UNTRAINED transformer**. That triggers both
`META_RULE_AG` (baseline out of band) and `META_RULE_AF` (bit-identical predictions). A readout on
which an untrained model is at ceiling discriminates nothing. `role_attn` is in-band
(arm B = 0.09-0.15, inside (0.05, 0.95)) and is now the headline. `span` is retained and reported
as a **ceiling control**, ungated.

**A2 caveat, stated up front and carried into the verdict:** `role_attn` requires the encoder's own
*contextual* reps to locate the filler. Arms B and C are non-contextual bag-of-token encoders and
cannot express role attention. So a large positive `delta_AB` under this readout is **NOT** clean
evidence about representation quality in general; it is evidence that a trained contextual encoder
beats a bag-of-token encoder at *role-addressed extraction*. Read together with the span control,
the honest statement is: **the trained encoder's entire advantage is in LOCALIZATION, not in colour
identity** — when localization is given, all five encoder arms tie at ceiling.

**A3. The floor predicate was mis-specified relative to this prereg's own wording and was fixed.**
It required D and E below `min(A, B)`. But `D_random_init_twin` (0.162-0.172) legitimately scores
slightly *above* `B_char_trigram` (0.092-0.147) — an untrained transformer matching a bag-of-token
encoder is a result, not a broken control. Corrected to the brief's actual wording ("D near floor"):
`D <= A - 0.05` AND `E <= A - 0.05` AND `E <= D + 0.05`.

**Smoke evidence (single seed, gate only, NOT the verdict):**

| arm | role_attn @12 | role_attn @48 | span @48 |
|---|---|---|---|
| A_tuned_ckpt | 0.5429 | 0.5990 | 1.000 |
| A0_frozen_base | 0.4520 | 0.3859 | 1.000 |
| B_char_trigram | 0.1465 | 0.0924 | 1.000 |
| C_ppmi | 0.0278 | 0.0208 | 1.000 |
| D_random_init_twin | 0.1717 | 0.1618 | 1.000 |
| E_scramble_floor | 0.0278 | 0.0347 | 0.049 |

`delta_AB` = +0.397 at `EVAL_N=12`, +0.507 at `EVAL_N=48` — the discriminator grows with scale
rather than collapsing, so DISCRIMINATOR-MUST-SURVIVE-SCALE is satisfied by the multi-scale smoke
(condition A/C). Effect size is far above the walk-back threshold, so `EVAL_N=80` stands.

## Metric

`loop_mean` = mean over `QUERY_TYPES = ("a_name_maintenance", "b_competitive_coref", "c_overwrite")`
of `eb.run_arm_decoded(eb.build_decoded_dataset(..., "role_attn"), ...)[qt]["acc"]` (HEADLINE;
`"span"` computed identically as the ungated ceiling control), on eval structures whose tracked entities are
drawn **only from the held-out colour split** (`ih.color_split(SPLIT_SEED)`; asserted per item in
`run_unit`). Plain accuracy in [0,1]. No hand-scoring anywhere in the path.

## Discriminator (fixed before running; not adjusted after seeing results)

`delta_AB = mean_over_seeds( loop_mean[A] - loop_mean[B] )`

| band | condition | meaning |
|---|---|---|
| **REFUTES_USER_CLAIM** | `delta_AB >= +0.05` AND floors hold (see A3: `D <= A-0.05`, `E <= A-0.05`, `E <= D+0.05`) | training the encoder buys accuracy |
| **CONFIRMS_USER_CLAIM** | `delta_AB < +0.03` (includes `B > A`) | the simple encoder matches or beats the trained one |
| **MIDDLE_BAND** | otherwise | licenses nothing |

HALT / fail-closed gates, all exercised at self-test scale:
`PROVENANCE_VIOLATION`; `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H` (expected 6 arms x n_seeds);
`HARD_FAIL_META_RULE_AF` (no two arms bit-identical);
`HARD_FAIL_BASELINE_OUT_OF_BAND_META_RULE_AG` (arm B must satisfy `0.05 < B < 0.95`).

**HP_SCOPE:** the discriminator applies ONLY to the pair (A, B). A0 is a provenance control and
inherits no band. C is reported, not gated. D and E are floors.

## Range by construction (explicitly required by the brief)

Two prior experiments here were rendered undecidable because their discriminator's resolution
depended on the hypothesis being true. This one does not:

- The metric is a plain accuracy over held-out items, computed identically for every arm. It is
  defined and finite regardless of which hypothesis holds.
- **Both signs are reachable.** `self_test` step 2 drives `compute_verdict` to REFUTES, to
  CONFIRMS, to CONFIRMS-via-`B > A`, to MIDDLE_BAND and to the saturated-baseline HARD_FAIL from
  synthetic inputs — the band function is surjective onto its outcome set.
- **The metric is not saturated.** Arm A0 (frozen base) on this harness sits around 0.5-0.7
  (`CITED@hdlab/encoder_retrain_persist.py` docstring: coref abs ~0.65 < 0.70 bar), i.e. inside
  the `META_RULE_AG` band (0.05, 0.95) with headroom in both directions. The cell HARD_FAILs if
  arm B lands outside that band.
- **No hand-scored MEANINGFUL delta anywhere.** Nothing in the path requires adjudication.

## Power

- FULL: 3 seeds x `EVAL_N = 80` structures x 3 query types = **~240 scored items per arm per seed,
  ~720 per arm total**, on the *same* items across arms (paired).
- Per-arm SE at p~0.6, unpaired: `sqrt(0.6*0.4/720) = 0.018`. Two-sided alpha=0.05, 80% power,
  unpaired MDE `~2.8 * sqrt(2) * 0.018 = 0.071`. Paired at an assumed inter-arm agreement
  rho=0.5 the paired SE is `0.018 * sqrt(2*(1-0.5)) = 0.018`, giving **MDE ~= 0.037**.
- `0.037 < 0.05`, so the REFUTES boundary is detectable at the pre-registered n.
- `EVAL_N = 80` is **double** `base_loop.EVAL_N_LITE = 40` — the walk-back gate applied up front,
  because the outcome most likely a priori (a near-tie) is the one that needs the most power.

## Multi-scale smoke

`EVAL_N` is a load-bearing count axis, so the smoke runs at `EVAL_N=12` AND `EVAL_N=48` (4x), both
into `data/exp_encoder_swap_behind_fixed_brain_stack_v1_smoke/`, separate from the FULL output dir.

## Compute architecture

`sequential-CPU`, justified: forward passes are `SENT_CAP=16` x `d_model=512` x 4 layers; no matmul
at or above N=8192; GPU batching would not change the wall materially and the harness is CPU-native.
**Storage strategy: sharded** — each colour code is its own vector in the codebook; nothing is
bundled across items, so the composition-depth collapse law does not apply.

## Schema-vet fields

```yaml
cardinality_ok: true                  # EXPECTED_N_UNITS = 6 arms x n_seeds
arms_differ_verified: true            # META_RULE_AF, per-arm prediction sha256 + raw-rep sha256
final_metrics_atomicity: tmp_replace  # single write at end, assembled from ckpt.load_units
crlb_floor_computed: 0.0625           # THEORETICAL@ 1/len(COLORS), chance for a colour argmax
crlb_formula_reference: "chance = 1/len(COLORS)"
discriminator_reachability: true      # bands at +-0.05 on a metric measured in [0.4, 0.8]
baseline_in_band: gated               # 0.05 < loop_mean[B] < 0.95 or HARD_FAIL (META_RULE_AG)
calibration_check: default_ok_for_this_regime   # no threshold is tuned inside this cell
cell_chunked: false                   # per-UNIT resume via tools/exp_checkpoint.py instead
start_marker_written: true
crash_diagnostic_present: true
defensive_error_checking: passed_all_4_patterns
sweep_alignment_verdict: ALIGNED      # the swept axis (encoder type) is the axis every primitive sees
```

## N-suffix

No `_n<N>` suffix in the anchor name. Production config: `EVAL_N = 80`, `SEEDS = (7, 13, 19)`,
`d_model = 512` (fixed by arm A's `model_cfg`; not a free parameter).
