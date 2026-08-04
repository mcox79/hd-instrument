# Pre-reg: exp_coherence_role_conflict_crosstalk_v1

Filed by: exp_dev sub-agent, 2026-08-04. Endorsed-with-corrections by
`notes/research_goal_owner_coherence_vs_mentalizing_framing_audit.md` (commit aeceefe1d, Level 5
+ Falsifiable predictions). Cell: `experiments/exp_coherence_role_conflict_crosstalk_v1.py`.

## Prior-work check (mandatory, USER-locked 2026-07-01)

`bash tools/substrate_query.sh "role conflict crosstalk goal owner coherence decode margin"` ->
top hit cosine=0.3076 (generic WordNet/concept-KB node "coherence", antonym incoherence) -- NOT a
duplicate of this specific mechanism-capacity probe. NONE at cosine>0.30 that constitute prior
work on this exact question. The relevant prior-work context is the DIRECTOR-KB drills already
cited inline in the cell docstring (the framing audit + the two prior coherence cells this one
extends), not a substrate-KB concept-node hit.

## What this cell IS

A mechanism-capacity probe: does `route_passage`/`decode_coherence_margins`
(hdlab/self_improving_loop.py, reused verbatim) discriminate the TRUE goal-owner from a foil once
the foil's error is embedded as a ROLE-CONFLICT -- the foil already holds another established
role at the SAME (cluster,event_slot) key elsewhere in the real passage, so binding the outcome
to it creates genuine crosstalk in `hdlab.situation_model_accumulate.AccumulateRegister` (which
bundles ALL of an entity's role,slot bindings and decodes by unbind-then-cleanup-argmax; two
different roles sharing one slot for one entity IS a real superposition collision, not a proxy).

## What this cell is NOT (scope, per correction 1)

NOT a test of general goal-owner attribution. NOT a test of general role-content coherence. A
HARD-PASS is a single-item (N=1 real passage, Henry/old_gentleman, 2-direction
identity-flip-tested) existence proof that the validated identity-merge crosstalk mechanism
(fair-test commit 46662d47b) generalizes to role-conflict crosstalk -- nothing more. This label
is embedded in the cell's `SCOPE_LABEL` constant and carried into `verdict_msg` +
`metrics.json["scope_label"]` so no downstream reader can over-read a pass as general capability.

## Items (both built from g5v_henry_wilkins_cherries, reused per
exp_coherence_fair_load_matched_retest_v1.py lines 271-300)

- **original**: conflict embedded on foil (old_gentleman, cluster '0'); coherent candidate =
  true owner (Henry, cluster '1'). Prediction if crosstalk-generalization is real:
  `agg_coherence_delta > 0`.
- **flipped** (load-direction/identity-flip control, correction 2): SAME construction with
  conflicted/clean swapped -- conflict embedded on Henry instead, coherent candidate =
  old_gentleman. Prediction if the "original" pass is genuine (not identity bias):
  `agg_coherence_delta > 0` ALSO -- the conflict-free side wins regardless of WHICH real entity
  plays that role.
- **shuffled** (structural control): `_shuffle_role_seq` (reused verbatim) reverses
  `role_seq` on "original"; entities/loads/event_slots/flagged_positions unchanged. A real
  structural-coherence signal must collapse (not still adopt the coherent candidate).

## Load discipline (correction 3, MANDATORY, asserted inline not just declared)

`_build_role_conflict_item` asserts `conflicted_load == clean_load` computed from the REAL
(pre-extension) `base_ids` alone, BEFORE any conflict-embedding extension is appended. A
violation raises `AssertionError` (crash), not a silent pass. Verified for BOTH directions
(original: foil_load==owner_load==3; flipped: owner_load==foil_load==3, same real counts,
direction-swapped labels).

## Pre-registered bands

- **POSITIVE CONTROL** (sanity gate): `exp_coherence_aggregate_discriminates_goal_outcome_v1.
  _coref_arm(seed)` reused unmodified MUST reproduce `net_auto=1.0` all 5 seeds. Failure ->
  `HARNESS_DEAD_POSITIVE_CONTROL_FAILED`, stop, do not trust bands below.
- **HARD_FAIL_ARTIFACT_SIGNATURE_CROSSTALK_DOES_NOT_GENERALIZE** (decisive even at N=1, per
  correction 2 -- this is the KNOWN artifact signature from
  `exp_coherence_aggregate_discriminates_goal_outcome_v1` commit 925897d74 and
  `exp_coherence_fair_load_matched_retest_v1`): fires if, in ANY seed, `orig_delta == 0.0`
  EXACTLY, OR `flip_delta <= 0` (sign flips/collapses under the identity-flip -- the same
  artifact class as a load-direction-flip reversing the original session's raw-aggregate result).
- **HARD_FAIL_SIGNAL_IS_POSITIONAL_NOT_STRUCTURAL**: fires if the SHUFFLED control still adopts
  the coherent candidate, or shows `shuffled_delta > 0` in any seed -- the effect would be
  positional (registrar-order artifact), not structural/crosstalk-driven.
- **HARD_PASS_CROSSTALK_GENERALIZATION_EXISTENCE_PROOF_SINGLE_ITEM**: fires iff, in EVERY seed,
  `orig_delta > 0` AND `flip_delta > 0` AND the shuffled control collapses
  (`adopt_coherent==False` and `shuffled_delta <= 0`). Framed per SCOPE_LABEL above -- a
  single-item existence proof, not a general capability claim.
- **MIDDLE_BAND_N1_INCONCLUSIVE**: none of the above decisive signatures fire. Not expected given
  the decisive-at-N=1 discipline in correction 2 (every plausible outcome maps to one of the
  three decisive verdicts above), but retained as an honest fallback if per-seed results
  genuinely split in a way not covered by the artifact-signature check.

## Compute architecture

(b) sequential-CPU with justification: 5 seeds x (positive-control 18-passage pass + 3
single-item route_passage calls), all closed-form small-D FHRR ops on CPU, <30s total wall time
measured in prior sibling cell (`exp_coherence_fair_load_matched_retest_v1`, same scale). Not a
batching candidate.

## Storage strategy

no_storage / no_composition: single-shot decode-margin reads, no multi-hop chained retrieval, no
PartitionedStore writes.

## Cardinality

`EXPECTED_N_SEEDS = 5`. Verdict logic emits `HARD_FAIL_CARDINALITY_BREACH` if
`len(per_seed) < EXPECTED_N_SEEDS`.

## Dispatch

LOCAL/CPU only (`local_cpu_queue`, or direct `.venv/Scripts/python.exe` invocation if
local_cpu_queue is paused -- either satisfies the LOCAL-ONLY mandate). No push. No remote.

## final_metrics_atomicity

`tmp_replace` (`_write_json` writes to `.tmp` then `os.replace`, same pattern as the sibling
cell and every cell in this family).

## defensive_error_checking

`passed_all_4_patterns`: start-marker write, crash-diagnostic (`except SystemExit: raise` /
`except KeyboardInterrupt: raise` / `except Exception` before crash-metrics write), per-unit
checkpoint via `tools/exp_checkpoint.py` (resumable per seed), print-progress with `flush=True`
(exempt from the >=1800s mandate at this cell's <30s scale, included anyway as good practice).
