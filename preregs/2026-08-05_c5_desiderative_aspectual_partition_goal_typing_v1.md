# PRE-REG: c5_desiderative_aspectual_partition_goal_typing_v1 (2026-08-05, LOCAL-ONLY, task-brief)

## Why
`exp_c5_real_coref_endtoend_purpose_infinitival_v1` (commit 78294a2c6) solved action_implied
end-to-end (0/10 -> 10/10) but pre-registered (and measured) that explicit_psych stays at 16/18
because its `CONTROL_VERB_STOP` list (in the reused
`exp_c5_generative_goal_typing_action_frame_v1.action_frame_feats`) deliberately excludes ALL
control verbs, including desiderative ones (hope/want/wish/...), from firing the purpose-infinitival
construction feature. C3's own EXPERIENCER-frame lexicon is OOV on "hoped" for t03_beth and t12_jo
(MEASURED@notes/deep_vet_comprehension_organ_vs_brain_2026-08-05.md "LANDED-2"), so those two items
fall in the gap BETWEEN two individually-correct mechanisms.

## Fix (this cell)
Partition `CONTROL_VERB_STOP` into DESIDERATIVE (goal-signaling: hope/hoped, want/wants/wanted,
wish/wishes/wished, mean/means/meant, plan/plans/planned, intend/intends/intended, aim/aims/aimed,
long/longs/longed, yearn/yearns/yearned, desire/desires/desired) vs ASPECTUAL/IMPLICATIVE (NOT
goal-signaling: begin/begins/began, start/starts/started, try/tries/tried, fail/fails/failed,
manage/manages/managed, happen/happens/happened, cease/ceases/ceased, stop/stops/stopped,
continue/continues/continued). Verbs not named in the task brief (decide, need, seem, get, choose)
are conservatively LEFT IN the stop set (OTHER_STOP_UNCHANGED) -- unclassified, no behavior change,
precision-safe default.

DESIDERATIVE verbs are REMOVED from the stop set so `action_frame_feats_partitioned` fires
`purpose_to_no_det` on "X hoped/wanted/... to VP" (the construction path), NOT added to the C3
EXPERIENCER lexicon (per task brief: desirers are not emotion-undergoers; fire GOAL via the
construction, not by mislabeling as EXPERIENCER). ASPECTUAL verbs STAY in the stop set (implicative
"began/tried/failed to VP" is not a goal-ownership signal per the brief).

This is parameterized ENTIRELY inside the new cell file
`experiments/exp_c5_desiderative_aspectual_partition_goal_typing_v1.py`. No modification to
`hdlab/`, `exp_component5_wired_endtoend_v1.py`,
`exp_c5_generative_goal_typing_action_frame_v1.py`, or
`exp_c5_real_coref_endtoend_purpose_infinitival_v1.py` -- all four are imported/reused bit-identical
(generic helpers: `load_bank`, `item_to_mentions`, `resolve_outcome_coref`,
`resolve_outcome_recency_positional`, `build_role_seq`, `_outcome_pos`, the three positional
baselines, `type_sentence_events_c3`, `induce_hypothesis` -- the MDL hypothesis is reused verbatim
since the feature NAME `purpose_to_no_det` is unchanged, only which sentences make it fire).

## Arms
`typing_mode in {"c3_only", "c3_plus_purpose_original", "c3_plus_purpose_partitioned"}`. The middle
arm reproduces the prior cell's own result (positive-control reproduction at the SAME regime, per
Gate D discipline) so the partitioned arm's delta is attributable to the partition, not to drift.

## Subsets
`explicit_psych` (N_core=18, N_divergent MEASURED before dispatch) and `action_implied` (N_core=10,
N_divergent MEASURED before dispatch), `trap_type=="recency"` bank, same as the predecessor cell.
Plus a NEW `aspectual_precision_probe` subset (N=7, hand-authored, NOT part of
`goal_owner_fair_v1.jsonl`): one item per ASPECTUAL verb (began/started/tried/failed/managed/
ceased/continued -- "stopped"/"happened" excluded from the probe sentences themselves because
"stopped to VP" and "happened to VP" are genuinely construction-ambiguous in English and would make
a false-fire inconclusive by construction; both verbs remain in the ASPECTUAL_STOP set regardless),
each item structurally identical to a real bank item (owner + foil + recency-trap pronoun outcome,
S1/S2 outcome-clause templates reused VERBATIM from real bank items known to trigger R_UNMET) with
the desiderative/psych verb replaced by an aspectual one.

## Compute architecture
Sequential-CPU, in-process, LOCAL-ONLY (task brief mandate: "do NOT modify production hdlab/",
"do NOT dispatch queue", "run to completion IN-PROCESS this turn"). Wall time << 10s (bank has
<50 sentences total across both subsets + 7 probe items; no matmul, pure string/dict logic
identical in cost profile to the two reused predecessor cells, both of which ran in well under a
second).

## Storage strategy
no_storage / no_composition (pure Python dict scoring over a static JSONL bank + 7 hand-authored
probe items; not a substrate-composition cell).

## Discriminator-fires / baseline-in-band
N/A in the AG/scale sense (boolean-match discriminator over a fixed small bank, same as the
predecessor cell's own `crlb_n/a` declaration) -- reused verbatim rationale:
`crlb_n/a: "boolean-match discriminator (owner-selection accuracy), not SNR-shaped"`.

## Bands (HARD_PASS strictly declared BEFORE running)
**HARD-PASS** (ALL of):
  - `explicit_psych` divergent accuracy under `c3_plus_purpose_partitioned` >= 17/18 (0.9444)
    (recovers t03_beth and t12_jo).
  - `action_implied` divergent accuracy under `c3_plus_purpose_partitioned` == 1.0 (stays at
    the predecessor cell's landed 10/10, MEASURED@data/exp_c5_real_coref_endtoend_purpose_infinitival_v1/metrics.json,
    no regression vs `c3_plus_purpose_original`).
  - Aspectual precision probe: `false_goal_count == 0` across all 7 probe items under
    `c3_plus_purpose_partitioned` (no `R_GOAL` role manufactured for the aspectual-verb subject)
    AND `matches_gold`/`final_owner` identical to `c3_only` on every probe item (no side-effect on
    owner selection either).
  - Scramble control collapses (>=50% of the unscrambled gain lost) on both `explicit_psych` and
    `action_implied` divergent subsets under `c3_plus_purpose_partitioned`, non-vacuously where the
    unscrambled gain is nonzero.
  - Gated positional baselines (recency, nearest_subject) stay near-zero on both divergent subsets
    (reused bank-structural fact, unaffected by typing mode).

**HARD-FAIL** (ANY of):
  - `false_goal_count > 0` on the aspectual precision probe (partition over-fires -- the
    make-or-break risk named in the task brief).
  - `action_implied` divergent accuracy under `c3_plus_purpose_partitioned` < 1.0 (regression vs the
    landed predecessor result).
  - `explicit_psych` divergent accuracy under `c3_plus_purpose_partitioned` < the
    `c3_plus_purpose_original` accuracy (regression from the partition itself, distinct from simply
    "did not recover").
  - Scramble does not collapse on either subset where the unscrambled gain is nonzero.

**MIDDLE_BAND**: anything else, e.g. explicit_psych improves but lands below 17/18 (partial
recovery, e.g. only one of t03/t12 recovers), or stays at 16/18 unchanged (recovery attempt failed
for a reason other than over-firing) while action_implied holds and precision probe is clean.

Small-N (<30) HARD_PASS bands are capped to MIDDLE_BAND_SMALL_N_WOULD_BE_HARD_PASS per this arc's
own standing convention (reused verbatim from the predecessor cell), reported alongside the raw
gate outcome so the underlying HARD_PASS-gate result is not lost.

## Cell-template mandates
- `arms_differ_verified`: hash-digest ARMS-MUST-DIFFER check at smoke/self-test gate between
  `c3_only` and `c3_plus_purpose_partitioned` on `action_implied` core rows.
- `final_metrics_atomicity`: tmp_replace.
- `except SystemExit: raise` before `except Exception` (no bare `except:` / `BaseException`).
- `cardinality_ok`: EXPECTED_N_UNITS = 3 seeds x 1 combined-run-per-seed (all subsets computed
  per-seed inside one unit), gated in verdict logic.
- `calibration_check`: default_ok_for_this_regime (all thresholds reused verbatim from the already
  VET'd predecessor cells; only the CONTROL_VERB_STOP partition is new).
- Numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ in the cell docstring.
- Resumable per-unit via `tools/exp_checkpoint.py`.

## Guards
Glass-box; deterministic given seed; ASCII-only; no push; no queue dispatch; no modification to
`hdlab/` or any of the three reused cell files (all reused via import only).
