# Pre-reg: exp_coherence_aggregate_discriminates_goal_outcome_v1 (2026-08-04)

## Question
Prior cell `exp_coherence_margin_discriminates_goal_outcome_v1` (commit 15d8fd627) HARD_FAILED
with a MORE GENERAL finding: the ATOMIC single-position `decode_coherence_margins` carries ZERO
identity information (coref included, load-matched delta EXACTLY 0.0). Production coref
discrimination (67% oracle-gain recovery, atom 29609) must be an EMERGENT property of
`route_passage`'s WHOLE-PASSAGE AGGREGATE (mean delta over many flagged positions), not the atomic
read. THIS cell tests the PRODUCTION AGGREGATE mechanism itself (`hdlab/self_improving_loop.py::
route_passage`, unmodified, called directly -- not the atomic formula inlined) at the grain where
coref is known to work: does it discriminate a coherent goal-owner whole-resolution from a
recency-driven whole-resolution on the goal-outcome instance?

## Prior-work check (SUBSTRATE-KB, USER-locked 2026-07-01)
`bash tools/substrate_query.sh "coherence margin aggregate route_passage goal outcome binding"` ->
top hit cosine=0.2871 (FN_Aggregate, FrameNet concept edge, unrelated). No prior arc cell at
cosine>0.30. Verdict: NOVEL, not a rediscovery of an already-answered question.

## Compute architecture
(b) sequential-CPU with justification: `route_passage` calls `decode_coherence_margins` which
builds a small (<=16-slot) FHRR AccumulateRegister per candidate per item -- microsecond-scale ops
on d<=1024 vectors, dozens of items x 3 sub-arms x 5 seeds. Wall time <10s total (measured in
smoke). Not a batching candidate.

Storage strategy: no_storage (in-memory FHRR registers constructed fresh per item/seed via
`route_passage`'s own `generator_factory` contract; nothing persisted to PartitionedStore).

## Mechanism under test (reused verbatim, WIRE-DON'T-ISLAND)
`hdlab/self_improving_loop.py::route_passage` (line 105) -- imported and called directly, NOT
reimplemented. Signature: `route_passage(role_seq, event_slots, baseline_cluster_ids,
candidate_cluster_ids: Dict[str, Sequence[str]], flagged_positions, role_vocab, d,
generator_factory, max_event_slots, abstain_band=0.02)` -> `{"adopt": name_or_None,
"adopted_cluster_ids": ..., "per_candidate": {...}}`. Internally: `decode_coherence_margins` (line
56) + `decide_keep_or_revert` (line 92), both reused verbatim (same functions the atomic HARD_FAIL
cell probed in isolation; here they run through the REAL aggregate caller, over REAL multi-position
whole-resolutions, exactly as production `exp_coref_autonomous_fix_router_v1` / atom 29609 use it).

## 3 arms

### ARM A -- coref POSITIVE CONTROL (MUST fire; harness-liveness gate)
Reproduces atom 29609's validated aggregate discrimination via `route_passage` directly (not the
cell's own inlined `_decide_autonomous`/`_decide_oracle`, though those are the same formulas --
this calls the WIRED hdlab function). Source: all 18 real McGuffey passages in
`data/eval_gold_mention_role_mcguffey_v1/gold_g5g6_dense_pronoun_verbatim_v1_reviewed.jsonl` (the
dense eval atom 29609 reports 67% oracle-gain recovery on). Config matches atom 29609 exactly:
`role_vocab=ROLE_VOCAB` (9 roles, from `exp_wire_coref_accumulate_situation_model_v1`), `d=1024`,
`max_event_slots=16`, `generator_factory=lambda: torch.Generator().manual_seed(SEED + p_idx*100)`
(same per-passage seed formula as atom 29609). Baseline = `run_strict_cb_instrumented`; candidate =
`{"principle_b_deixis": run_principle_b_deixis(stream)}`; flagged = pronoun positions with
`n_compatible>=2` (`FLAG_MIN_N_COMPATIBLE=2`, atom 29609's earned-flag rule). Per passage, score
`route_passage`'s `adopt` decision against the GOLD oracle decision (`mention_link_wrong`,
identical to atom 29609's `_decide_oracle`) restricted to passages where the candidate is
`applicable` (changed >=1 flagged position).

**Gate: MUST FIRE.** HARD requirement for ANY other arm to be interpretable: aggregate net
(corrected-broken via `route_passage`'s adopt decisions) > 0 on applicable passages, AND
`recover_frac = net_auto / net_oracle >= 0.5` (RECOVER_FRAC_BAND, atom 29609's own bar) when
`net_oracle > 0`. If this does not fire, the harness itself is dead (route_passage import/call
bug, config drift, or item construction bug) and the goal_outcome arms below are UNINTERPRETABLE
-- verdict forces `HARNESS_DEAD_POSITIVE_CONTROL_FAILED` regardless of the other arms' numbers.

### ARM B -- goal_outcome TREATMENT (multi-position, anti-recency by construction)
Synthetic multi-position items (role_vocab = `["GOAL","ACTION_AGAINST","OUTCOME_UNMET",
"OUTCOME_MET"]`, `d=1024`, `max_event_slots=8`, mirrors `GoalOutcomeRegister` role vocab from
`exp_situation_model_goal_outcome_dimension_v1.py`, sourced not re-derived). Each item = ONE
`route_passage` call (one "passage") with:
  - non-flagged context: owner has `GOAL` (slot0) + `ACTION_AGAINST` (slot1) bound to `owner` in
    BOTH baseline and candidate (identical, establishes the goal-blocked narrative); foil has its
    own unrelated `GOAL` event(s) mentioned MORE RECENTLY (later position) than the owner's context
    -- this is what makes foil the "recency pick."
  - 2 FLAGGED `OUTCOME_UNMET` positions (slots 2,3) -- the goal-owner referenced at >=2 positions
    across the dispersed block, per the situation-model cell's naturalistic dispersed design.
    baseline (recency): both bound to `foil` (the most-recently-mentioned entity). candidate
    (coherent): both bound to `owner` (the TRUE goal-owner) -- ANTI-RECENCY BY CONSTRUCTION (owner
    is never the most-recent entity at the outcome positions).
3 sub-arms (12 items total, N small + DIRECTIONAL, declared):
  - `go_matched` (4 items, owner/foil symmetric): owner and foil each carry an EQUAL count of
    non-flagged supporting events (2 each) -- the load-fair primary test.
  - `go_asym_foilheavy` (4 items): foil carries MORE supporting events than owner in the shared
    context (foil heavier); TRUE side (owner) stays the lighter side -- the direction that
    superficially "looks like" a load-artifact win.
  - `go_asym_ownerheavy` (4 items): REVERSED -- owner carries MORE supporting events than foil;
    TRUE side (owner) is now the HEAVIER side. A genuine identity/coherence signal must NOT flip
    between foilheavy and ownerheavy (both must still favor the TRUE resolution); a pure
    register-load artifact WOULD flip (favor whichever side is lighter, independent of truth).
Per sub-arm, per seed: `adopt_rate = fraction of items where route_passage(...)["adopt"] ==
"coherent"`.

**LOAD-ARTIFACT GATE (the make-or-break VET, per prior cell's lesson):**
`load_artifact_ruled_out = (adopt_rate(go_matched) and adopt_rate(go_asym_foilheavy) and
adopt_rate(go_asym_ownerheavy) are all >= 0.5, pairwise range <= 0.35)`. If ownerheavy collapses
relative to foilheavy (range > 0.35, esp. ownerheavy << foilheavy), that reproduces the prior
cell's load-artifact signature at aggregate grain -> explicit HARD_FAIL, not silently absorbed into
a headline number.

### ARM C -- SHUFFLED-STRUCTURE CONTROL (must collapse)
Same `go_matched` items, but `role_seq` is REVERSED (deterministic, no `hash()`/RNG -- pure index
reversal: position i's role becomes original position `len-1-i`'s role) while `event_slots`,
`baseline_cluster_ids`, `candidate_cluster_ids`, and `flagged_positions` are UNCHANGED. This
decouples which semantic role (GOAL/ACTION_AGAINST/OUTCOME_UNMET) is bound to which entity's event
slot -- destroys the "owner stated a GOAL, suffered ACTION_AGAINST, ended OUTCOME_UNMET" narrative
coherence while preserving entity identity, load, and position structure exactly.
`go_shuffled_adopt_rate` computed identically to Arm B.

**Rule:** a real structural-coherence signal must COLLAPSE on shuffled structure
(`go_shuffled_adopt_rate <= 0.25`). If shuffled ALSO "adopts coherent" at a rate comparable to
intact (`>= 0.75`, or within 0.25 of the intact `go_matched` rate), the aggregate signal is a
position/load artifact, not structural coherence -> explicit HARD-FAIL for that finding.

## Bands (finalized, spine per task contract)
- **HARD_PASS** (`AGGREGATE_DECODABILITY_EXTENDS_TO_GOAL_OUTCOME`): Arm A fires (net_auto>0 AND
  recover_frac>=0.5) AND `adopt_rate(go_matched) >= 0.75` AND `load_artifact_ruled_out == True` AND
  `go_shuffled_adopt_rate <= 0.25`.
- **HARD_FAIL_GOAL_OUTCOME_DOES_NOT_EXTEND** (Arm A fires, but `adopt_rate(go_matched) <= 0.25`):
  goal-outcome patterns with the causal instance -- needs a relational REACH quantity
  (reach_value/M_backward-style), not a decodability-coherence signal. A real, build-reshaping
  negative.
- **HARD_FAIL_LOAD_ARTIFACT** (Arm A fires, `adopt_rate(go_matched) >= 0.75`, but
  `load_artifact_ruled_out == False` OR `go_shuffled_adopt_rate >= 0.75`): the apparent
  discrimination is a register-load or role-position artifact, not real structural coherence --
  reproduces the prior cell's lesson at the aggregate grain.
- **HARNESS_DEAD_POSITIVE_CONTROL_FAILED**: Arm A does not fire. Goal-outcome arms uninterpretable
  regardless of their numbers; investigate the route_passage call / config / item construction
  before re-running.
- **MIDDLE_BAND**: any other combination (e.g., go_matched fires and load-artifact ruled out, but
  shuffled control lands strictly between 0.25 and 0.75 -- partial structural dependence, not a
  clean collapse).

## Discriminator-fires / scale
`route_passage` is called on ITEMS SIZED FOR PRODUCTION (d=1024 matches atom 29609 exactly for Arm
A; d=1024 for the goal-outcome arms matches `GoalOutcomeRegister`'s D2). No smaller-N smoke variant
of `d` -- smoke uses fewer SEEDS (2 instead of 5) and the SAME item construction, satisfying
DISCRIMINATOR-MUST-SURVIVE-SCALE option (A) (full-N parameters in smoke).

## Schema-vet gates
- `cardinality_ok`: EXPECTED_N_UNITS = 5 seeds (n_units = 5; SEEDS=[0..4]).
- `cell_chunked`: true (per-seed checkpoint via `exp_checkpoint.py`).
- `arms_differ_verified`: true -- baseline_cluster_ids != candidate_cluster_ids on every item at
  its flagged positions (asserted in self-test); shuffled role_seq != intact role_seq (asserted).
- `final_metrics_atomicity`: "tmp_replace".
- `except SystemExit / KeyboardInterrupt` before bare `except Exception` (no `except:`/
  `except BaseException`).
- `crlb_n/a`: "adoption-rate discriminator, not a capacity/noise-floor metric; no CRLB applies."
- `baseline_in_band`: n/a -- this cell's "baseline" arms are DELIBERATE recency-resolutions (a
  mechanism arm, not a null/random control needing an in-band check); the null-equivalent check is
  the shuffled-structure control (Arm C) instead.
- `deterministic_seeding`: true -- all seeding via `torch.Generator().manual_seed(int)` with fixed
  integer/formula seeds (`SEED + p_idx*100` for Arm A per atom 29609's own convention; `SEED_GO +
  seed*1000 + item_idx` for Arm B/C); shuffled-structure permutation is a pure deterministic index
  reversal, no `hash()`/`list(set())` anywhere.
- `progress_logging`: n/a -- estimated wall time <30s total (well under the 1800s/30min gate).
- HYPOTHESIZED/MEASURED/CITED tags: atom 29609's "67% oracle-gain recovery" and "RECOVER_FRAC_BAND
  =0.5" are CITED@data/exp_coref_autonomous_fix_router_v1/metrics.json (verified on disk before
  authoring this pre-reg). All other numbers below are MEASURED in this cell's own run.

## Brain-fidelity caveat (mandatory, task contract)
`route_passage`'s aggregate is a SINGLE-PASS integration over the whole passage/item -- a
brain-COMPATIBLE approximation of iterative Kintsch construction-integration / CA3 recurrent
attractor settling, not the full recurrent fixed-point. This cell's HARD_PASS (if it lands) shows
the discrimination is ALREADY carried by the one-shot aggregate for goal-outcome (no settling
needed to see it); a HARD_FAIL_GOAL_OUTCOME_DOES_NOT_EXTEND would leave open whether a settling
mechanism (not yet built) recovers it -- report explicitly, do not conflate "one-shot aggregate
insufficient" with "no mechanism could ever work."

## Queue / dispatch
LOCAL/CPU only (`local_cpu_queue`), per USER-lock (SMOKE-and-full-light-cells only on local; this
is a <30s wall-time cell, appropriate for local). No push, no remote.

## VET discipline
Positive control (Arm A) and shuffled control (Arm C) are MANDATORY, not optional -- a bare Arm B
number is uninterpretable without both. Self-test constructs the REAL `route_passage` call (real
code path, not a synthetic-only branch) on a tiny fixture before the full run. Verify metrics.json
on disk before reporting; do not report a number that was not measured.
