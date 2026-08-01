# PRE-REG: encoder_alltype_transfer_v1

Filed: 2026-07-31. Cell: `experiments/exp_encoder_alltype_transfer_v1.py`.
Director spawn: does the certified minimal-unfreeze encoder retrain (atom 29593) lift held-ahead
comprehension BROADLY (all 3 situation-model query types) or only competitive-coref (already shown by
`exp_coref_encoder_transfer_v1.py`)?

## Question
Is the encoder the UNIVERSAL absolute-comprehension lever for the growing library, or is it coref/entity-
specific?

## One variable
Which encoder checkpoint `eb.EncoderExtractor` loads: frozen v2 default vs the persisted certified-break
retrained checkpoint (`data/exp_encoder_retrain_persist_v1/ckpt_seed_{7,13,19}.pt`). Implemented via the
SAME `__init__.__defaults__` monkeypatch pattern already used and VET'd in `exp_coref_encoder_transfer_v1.py`
(frozen-vs-frozen 0.0-drift control already certified there). Everything else -- eval_structs, tables,
train/held split, target hardness, the FHRR reader (`base_loop._eval_heldahead`, verbatim, unmodified) -- is
identical across arms.

## Measurement
Per seed (SEEDS_LITE=(7,13,19)), three encoder builds: frozen1, frozen2 (drift control, independent
instance, same default ckpt), tuned (encoder-swapped). Per query type in QUERY_TYPES =
(a_name_maintenance, b_competitive_coref, c_overwrite): frozen accuracy, tuned accuracy, lift = tuned -
frozen1, drift = frozen2 - frozen1 (must be ~0, proves the eval is deterministic and the swap is the only
variable).

## Pre-registered bands (fixed before running)
- **UNIVERSAL (HARD_PASS)**: mean per-type lift >= `LIFT_MIN = 0.05` on >= `N_TYPES_MIN = 2` of the 3 types,
  AND at least one of those types is non-coref (a_name_maintenance or c_overwrite).
- **COREF_SPECIFIC (HARD_FAIL, informative negative)**: only b_competitive_coref clears LIFT_MIN;
  a_name_maintenance and c_overwrite both stay < LIFT_MIN. Matches the prior A-TYPE DIAGNOSIS prediction
  (`exp_situation_model_assembly_encoder_retrain_scale_v1`: role/state decode is orthogonal to this
  entity-consistency retrain). If c_overwrite ALSO stays flat despite being entity-addressed like b, flagged
  as a narrower finding, not silently folded into "coref-specific".
- **MIDDLE**: mixed pattern clearing neither pole cleanly. Full per-type trajectory reported.
- **INVALID**: drift-control fails (max |frozen2-frozen1| > `DRIFT_MAX = 0.01`) OR
  `clean.audit_construction` flags fails OR a required persisted retrained ckpt is missing.

## Grounding (not re-derived)
`exp_situation_model_assembly_encoder_retrain_scale_v1`'s A-TYPE DIAGNOSIS (cited verbatim by
`exp_multi_competency_growing_library_v1.py`'s docstring) already found this SAME entity-consistency retrain
recipe lifts b/c (entity-addressed) but leaves a flat (role/state decode, orthogonal). This cell tests that
prediction directly and quantitatively on `base_loop`'s held-ahead harness (distinct from the coref-ablation
harness `exp_coref_encoder_transfer_v1.py` uses), across all three types in one measurement per seed.

## Prior-work check
`substrate_query.sh "situation model comprehension encoder retrain universal lever query type"` -- top hit
cosine=0.3887 (general architecture note, not a prior measurement of this specific question). Not a
rediscovery.

## Scope / parallel-safety
Writes only to `data/exp_encoder_alltype_transfer_v1/` (new dir). Reads
`data/exp_encoder_retrain_persist_v1/ckpt_seed_*.pt` read-only. Does not touch
`data/exp_coref_encoder_transfer_v1` or its cell (a VET is auditing those in parallel). Does not modify
`base_loop` (`exp_continuous_curriculum_learn_as_you_go_v1.py`) or the growing-library cell.
