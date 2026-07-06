# Pre-registration: lang_assembly_4layer_svo_v1 -- FIRST 4-layer language assembly

Date: 2026-07-05. Author: exp_dev. Stage-3. Cell:
`experiments/exp_lang_assembly_4layer_svo_v1.py`. Anchor: `lang_assembly_4layer_svo_v1`.
Source spec: `notes/research_language_assembly_composition_scoping_2026-07-05.md` (Section 2).

## Prior-work check (substrate concept-query, mandatory)
`bash tools/substrate_query.sh "4-layer language assembly composition lexicon morphology syntax grammar
structured proposition cross-layer identity"` -> top hits: `proposition` (wordnet, cosine=0.3477, generic
dictionary), `q_a3_l130_cross_layer_composition_v1_n16384` (metrics, cosine=0.3076, a substrate-PHYSICS
cross-layer composition probe -- different sense of "layer"). **No prior 4-layer LANGUAGE assembly cell exists
at cosine>0.30.** This cell is genuinely novel as an assembly; the individual layers are proven in isolation
(this cell composes them). Not a rediscovery.

## What this is (USER-locked framing)
Glass-box STRUCTURED (lemma-level) COMPOSITION: chain 4 independently-proven glass-box language primitives
-- LEXICON (real native GSBC concept codes) + MORPHOLOGY (FHRR dual-route inflection) + SYNTAX/GRAMMAR
(block-local slot-order + function-word operators) -- into ONE end-to-end pipeline that encodes a KNOWN
structured proposition and round-trips it to the structured parse with structure intact + a correctly-inflected
surface string. NOT generation (proposition GIVEN), NOT a language model, NOT semantic understanding.

## HONEST DATA NOTE (load-bearing; MEMORY foundational anchor "SUBSTRATE KNOWS NOTHING")
The 177,899-name concept pool is a TECHNICAL ONTOLOGY (`T1/vector_space`, `T1/inner_product`, ...)
MEASURED@`data/substrate_index/cached_indices/bge_large_v2_name_177899_54f7cf6a.npz:id_order_json` -- it
contains NO English words like cat/dog/chase. Therefore the English words are HUMAN GLOSSES deterministically
bound to REAL native GSBC concept codes (real pool rows carrying the real cos-cone), NOT semantics the
substrate knows. The identity discriminator is about STRUCTURAL identity (same concept-id through every layer),
NOT meaning. Never narrate as the substrate "knowing" cat/dog.

## Compute architecture
- Class: **(b) sequential-CPU** with justification: numpy FHRR + block-local matched-filter; wall time
  MEASURED@smoke 0.7s (< 10s). No GPU-batching candidate (per-unit wall << 10s; total FULL ~a few s).
- Storage strategy: **sharded** (block-disjoint per slot, inherited from grammar). No bundled composition.

## Functional requirements (Gate E)
| requirement | primitive (proven) |
|---|---|
| look up real concept codes for content words | LEXICON: native GSBC pool (decoder cell) |
| place ordered typed slots + function-word operators, round-trip decode | SYNTAX/GRAMMAR block-local (grammar cell) |
| inflect the verb to PAST (allomorphy + irregular dual-route) | MORPHOLOGY FHRR conditioned transform + exception gate (morph cell) |
| verify morphology + syntax agree on WHICH lemma the verb slot holds | **NEW: concept-id -> FHRR-stem bridge + FHRR unbind/cleanup (identity_consistency)** |

## Composition edges (Gate C: signal_shape_compatibility_audit)
| from | to | edge | verdict |
|---|---|---|---|
| LEXICON (GSBC 8192, 192-active) | SYNTAX block (bs=1024 sparse bipolar) | `_blocklocal_codebook_gsbc` projection | SHAPE_MATCH_adapter_gsbc_blocklocal_projection (decoder-proven) |
| LEXICON concept-id | MORPHOLOGY FHRR stem (8192 phasor) | `fhrr_stem_for_id` hash-seed | SHAPE_MATCH_adapter_concept_id_to_fhrr_stem (NEW glue, mismatch #2) |
| MORPHOLOGY surface | SYNTAX verb id | discrete concept-id symbol | SHAPE_MATCH_adapter_discrete_symbol_bridge (decode-to-symbol; NOT vector fusion) |
No `SHAPE_MISMATCH_no_adapter`.

## Positive-control arms (Gate D: reproduce prior chain-grade AT TEST REGIME)
- Morphology conditioned transform reproduced at test regime (FHRR N=8192): structured_joint verb allomorph
  selection MEASURED@selftest=1.000; naive collapses to 0.333 -- reproduces morph cell's conditioned>>naive
  contrast. cited_prior_atom: `data/exp_morph_ruleset_wug_v2_cpu` (HARD_PASS all 8 rules). tolerance 0.10.
- Block-local syntax reproduced at LEVELS=1 bs=1024: structured_joint exact_ordered MEASURED@smoke=1.000 --
  reproduces decoder blocklocal exact_ordered=1.000. cited_prior_atom:
  `data/exp_generation_decoder_gsbc_native_blocklocal_v1` (HARD_PASS). tolerance 0.10.
- regime_extension_audit: SHAPE_MATCH (all reuses at their proven regimes: N=8192, bs=1024 within decoder's
  proven D<=12 bs>=683 window; FHRR N=8192 == morph cell's regime).

## Sweep-axis gates (A/B)
- No parameter sweep in demo #1 (fixed LEVELS=1, V_CONTENT=64). `sweep_alignment_verdict: N/A_no_sweep`.
  `discriminating_fraction: N/A_no_sweep` -- the discriminating structure is carried by the 4 CONTROLS (each
  collapses vs the mechanism), not by a sweep bracket.

## CRLB / capacity-feasibility
- Block-local LEVELS=1 disjoint-block recovery: exact-by-construction (bs=1024, one code per disjoint block,
  no within-block superposition; no argmax-noise floor). `crlb_n_a: "disjoint-block recovery has no
  within-block superposition at LEVELS=1"`.
- FHRR identity cleanup: candidate stems are independent unit-phasors; self-cos=1.0, cross-cos
  ~1/sqrt(2N)~0.0078 THEORETICAL@FHRR -> argmax separation exact-by-construction over the ~8-candidate set.
- `discriminator_reachability: True` -- HP thresholds (0.90/0.95/0.90) are below the exact-by-construction
  ceiling; the falsification weight is on the CONTROLS, not on reaching a hard floor.

## Arms (PAIRED: same sentences + codebooks across arms)
- `structured_joint` (PRIMARY, mechanism): full 4-layer pipeline, bridge intact.
- `flat_bag` (control): syntax collapse (superpose all slots into block 0; reuse grammar arm).
- `scrambled_roles` (control): syntax collapse (permuted address; reuse grammar arm).
- `naive_morphology` (control): morphology allomorph collapse (single blurred transform).
- `identity_scrambled` (control, THE NOVEL DISCRIMINATOR): morphology processes a WRONG concept-id vs the one
  syntax decoded for the VERB slot -- slot recovery AND surface string still look correct, but the two
  subsystems secretly disagree on the lemma -> caught ONLY by identity_consistency.

## Metrics (report SEPARATELY per Fix #28)
- `exact_ordered_slot_match`: recovered ordered slot-content-id sequence == gold (chance ~0 for flat/scrambled).
- `identity_consistency`: P[FHRR-cleanup of the unbound morphology stem == the concept-id syntax decoded for
  the VERB slot], over {syntax-decoded subj/verb/obj ids} + K=5 distractors (chance = 1/8 = 0.125). NOVEL joint.
- `surface_string_exact`: final assembled + inflected string == gold, over the curated sentence set.
- diagnostics: `naive_morphology.allomorph_selection_acc` (chance 0.333).

## Pre-registered bands (HYPOTHESIZED@this-prereg; deflated per lit-scan calibration)
HP_SCOPE: chain-grade HP gates apply ONLY to `structured_joint`; controls carry ONLY their collapse gate.

- **HARD-PASS** (structured_joint): `exact_ordered_slot_match >= 0.90` AND `identity_consistency >= 0.95` AND
  `surface_string_exact >= 0.90` AND ALL 4 controls collapse:
  `flat_bag.exact_ordered <= 0.30`, `scrambled_roles.exact_ordered <= 0.30`,
  `naive_morphology.allomorph_selection_acc <= 0.55`, `identity_scrambled.identity_consistency <= 0.30`.
- **HARD-FAIL**: `exact_ordered_slot_match < 0.50` (undiagnosed integration-joint bug, mismatch #3 leading
  suspect) OR `identity_consistency < 0.50` (the concept-id->FHRR-stem bridge itself broken, mismatch #2) OR
  any control fails to collapse (vacuous test).
- **MIDDLE**: in between -- diagnostic: exact weak => block-projection (mismatch #3); identity weak => id->FHRR
  bridge (mismatch #2); surface weak while both vector metrics pass => string-lookup bug (cheapest).
- **OVER-CLAIM GUARD (HARD-FAIL regardless of number)**: framing a pass as "the substrate composes/generates/
  understands sentences" in any general sense, or as a step toward fluent language, or narrating the GSBC codes
  as English semantics. Honest scope: four proven glass-box PRIMITIVES chain via a discrete symbolic bridge on
  a KNOWN proposition over a curated GLOSS set. Watch for by-construction saturation (the parts are all proven;
  a HARD-PASS is a COMPOSITION DEMONSTRATION -- the NEW content is the bridge wiring + the identity joint).

Predicted (deflated): P(HARD-PASS)~0.40, P(MIDDLE)~0.40, P(HARD-FAIL)~0.20 (research note headline).

## META_RULE / SCHEMA-VET fields
- `cardinality_ok: true` -- EXPECTED_N_UNITS = n_seeds * n_sent = 3 * 22 = 66 (FULL); verdict emits
  HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if `n_units < expected`.
- `arms_differ_verified` (META_RULE_AF): the 5 arm per-sentence recovered signatures are hash-distinct
  (asserted at run; MEASURED@smoke=True).
- `final_metrics_atomicity: "tmp_replace"` (META_RULE_AH).
- `except SystemExit: raise` BEFORE `except Exception` (no BaseException; no bare except).
- `baseline_in_band` (META_RULE_AG): the 4 controls are NEGATIVE controls expected to COLLAPSE by construction
  -- EXEMPT from 0.05<baseline<0.95 (HP_SCOPE); they carry ONLY the collapse gate.
- `calibration_check: "default_ok_for_this_regime"` -- reuses the exact algebra + constants of the 3 source
  cells (N=8192, F_SPARSE=0.02, IRREG_THRESH=0.5) at their proven regimes; discriminators verified to fire in
  smoke.
- Defensive error-checking: `cell_chunked: false` (single-file multi-seed loop; sub-second, low zombie risk),
  `start_marker_written: true`, `crash_diagnostic_present: true` (Exception -> CELL_CRASHED metrics + traceback),
  `heartbeat_present: true`, `defensive_error_checking: "passed_all_4_patterns"`.
- `progress_logging: "print_flush_true"` (line_buffered stdout + flush; cell wall < 1s so timeout_s well below
  the 1800s mandatory-progress threshold, but flushing is present anyway).
- RUN_MODE verification: cell asserts landed `run_mode == mode`; separate smoke dir
  `data/exp_lang_assembly_4layer_svo_v1_smoke` vs full `data/exp_lang_assembly_4layer_svo_v1`.

## Discriminator survives scale
ALL arms run at FULL N=8192 in smoke (smoke reduces sentence count + seeds only, NEVER N). The 4 control
collapses are STRUCTURAL / N-independent (Option A full-N smoke + Option B analytical): flat superposition
merges disjoint blocks regardless of N; scrambled mis-addresses regardless of N; naive averages 3 allomorph
tags into a blurred centroid regardless of N; a wrong-id FHRR stem is orthogonal to the candidate set
regardless of N.

## Smoke result (MEASURED@`data/exp_lang_assembly_4layer_svo_v1_smoke/metrics.json`, seed 7, 12 sentences, N=8192)
`HARD_PASS` (SMOKE_MACHINERY_OK). structured_joint exact_ordered=1.000 identity=1.000 surface=1.000;
flat_bag.exact=0.000, scrambled.exact=0.000, naive.allo=0.333 (chance), identity_scrambled.identity=0.000
(chance 0.125). bag_blind=True. arms_differ_verified=True. cardinality_ok=True (12/12). elapsed 0.7s.
Self-test: PASS.

## Dispatch
- SMOKE: run LOCAL (done, direct python; local_cpu_queue is paused + USER-lock is smoke-only-local).
- FULL: staged for orchestrator. Config: seeds (7,13,19), n_sent=22, expected_units=66; sub-second CPU.
  **Dependency:** the untracked pool npz `data/gen_decoder_gsbc_fillers/gsbc_expand2x_pool_v1.npz` MUST be
  present wherever FULL runs (present locally; SCP'd to remote by the decoder cell). No origin push required
  for a local FULL; remote FULL needs the pool on remote.
