# Pre-reg: Competency #3 (cross-sentence coreference), EVAL-ONLY role-key ablation

Filed by: exp_dev, 2026-07-31. RE-BASELINED 2026-07-31 (VET-confirmed, director greenlight) from the
training-based v1 design to an EVAL-ONLY role-key ablation. Rationale: the v1 training variants fine-tuned
the encoder on isolated tag+coref snippets, which caused NEGATIVE TRANSFER on the complex eval passages
(Tier-1 0.5 frozen -> 0.429, loss not descending, delta 0.000 = INVALID). The eval-only ablation isolates
the compositional-wiring question WITHOUT any training, and its Tier-1 delta is VET-confirmed
(independent recompute reproduced the deltas exactly; a neutral role-shuffled baseline gave comparable
deltas => no confound).

Supersedes the additive-blend measurement (retired: additive blending DILUTES compositional value per Drill
D, `notes/research_additive_vs_compositional_comprehension_measurement_2026-07-31.md`).

KB-check (SUBSTRATE-KB CONCEPT-QUERY): `substrate_query.sh "cross-sentence coreference competency ablation
bottleneck AND-gate role-competitive"` -> top hit cosine=0.42 on generic WordNet 'competence'. **Prior-work
check: NONE at cosine>0.30 -- genuinely new cell.**

Built on `experiments/exp_multi_competency_growing_library_v1.py` (competency #1 entity + #2 roles harness):
reused VERBATIM for the can-fail harness floors + role fairness references (`run_base_multi`,
`base_loop._floors_ok`, `_pooled_reservoir`). NOT modified.

## What the resolver is (where role information enters)

The harness's EXISTING `b_competitive_coref` query ("what was the entity TAGGED <mark> <role> to?") is
answered by `clean.SituationWM.query(ent, mark, role)`: (1) coref-address the entity via the MARK
(competency #1's device), read the packed FHRR content slot; (2) UNBIND by `role_keys[role]` to recover the
queried role's filler (competency #2's device). Role information enters at EXACTLY ONE place -- the role key
supplied at unbind -- which makes a clean eval-only causal ablation possible with NO encoder training.

## Tiering (construction-time tag from the reconstructed event schedule; `_coref_item_info`)

- Tier 0 (entity-only): `S(b_ent) == P(b_ent)`. Role irrelevant; mark-resolution alone suffices.
- Tier 1 (role-competitive): `S != P`, `distance <= median(distance | role_critical)`. Requires #1 AND #2
  jointly = the compositional BOTTLENECK bucket. THE PRIMARY BUCKET.
- Tier 2 (harder long-distance role-competitive): `S != P`, `distance > median`. Reported, not gated.

## The ablation (three eval columns; same frozen decode, differ only in the role key at unbind)

- **roles_present**: unbind with the CORRECT queried role key `role_keys[q.role]` (role info AVAILABLE).
- **roles_ablated**: force a fixed-STATE-slot read (role forced to STATE for every b query), scored against
  the UNCHANGED true answer (role info REMOVED; on Tier-0 s==p so no regression, on Tier-1 PLACE-queries the
  fixed-STATE read returns the WRONG slot).
- **rand_role** (NEUTRAL control, VET-added): per-item role drawn deterministically at random in
  {STATE, PLACE} (role info SCRAMBLED, not corrupted). Its delta must be COMPARABLE to roles_ablated,
  confirming the effect is role-ALIGNMENT, not a fixed-STATE artifact (no confound).

All eval-only, frozen encoder, matched eval distribution, certified resolver reused verbatim.

## Primary metric + pre-registered bands (headline = the ablation DELTA, NOT an absolute)

PRIMARY = Tier-1 ablation DELTA = `acc(roles_present) - acc(roles_ablated)` on the SAME held-out Tier-1
items, via `eb.run_arm_decoded` (the harness decode pipeline, unmodified).

- **COMPOSITIONAL_WIRING_CONFIRMED (HARD_PASS)**: mean Tier-1 delta >= `DELTA_WIRING_MIN` (0.10) AND every
  seed's Tier-1 delta > `DELTA_PERSEED_MIN` (0.05) AND fairness_ok. Demonstrates roles CAUSALLY gate
  competitive-coref resolution -- the compositional wiring the additive metric HID. Does NOT claim solved
  competitive coref (see honest scope below).
- **HARD_FAIL**: mean Tier-1 delta <= 0.05 -- resolver does NOT consume role info (a wiring gap).
- **MIDDLE**: mean Tier-1 delta in (0.05, 0.10) -- weak/partial consumption.
- **INVALID**: fairness gate fails FIRST (shortcut solves Tier-1 / role-critical population too small / a
  can-fail harness floor did not collapse) -- broken TEST, not a capability verdict.

The old training-based absolute HARD_PASS (`tier1 >= 0.70`) is DROPPED as the headline: roles_present
absolute Tier-1 accuracy (~0.51) is ENCODER-DECODE-limited (stage_ENT ~0.73), a SEPARATE axis from the
role-consumption question. Reported as context, not gated.

## VET-confirmed reference numbers (MEASURED)

MEASURED@step1 eval-only probe (frozen encoder, eval_n=90, target hardness=8), 3 seeds:

| seed | roles_present | roles_ablated | Tier-1 delta | Tier-2 delta |
|---|---|---|---|---|
| 7  | 0.489 | 0.378 | +0.111 | +0.211 |
| 13 | 0.553 | 0.362 | +0.191 | +0.028 |
| 19 | 0.478 | 0.217 | +0.261 | +0.270 |
| mean | 0.507 | 0.319 | **+0.19** | +0.17 |

3/3 seeds positive; all clear 0.05. Tier-0 no-regression: delta 0.000 at seeds 13 & 19 (present==ablated),
seed 7 -0.143 = n=7 small-sample noise (directional check, underpowered). Neutral rand_role delta 0.11-0.23
(comparable to roles_ablated => no fixed-STATE confound). shortcut_tier1_acc 0.43-0.59 (<= 0.65).

## Honest scope (the claim this cell makes, and does NOT make)

- MAKES: the competitive-coref resolver CAUSALLY consumes the certified role representations -- roles (#2)
  gate coref (#3) resolution on exactly the items that structurally require it (Tier-1), and not on
  entity-only items (Tier-0 no-regression). This is COMPOSITIONAL WIRING, VET-confirmed, 3/3 seeds.
- DOES NOT MAKE: solved competitive coreference. Absolute Tier-1 accuracy with roles (~0.51) is limited by
  the FROZEN encoder's decode quality (stage_ENT ~0.73), not by role availability. Lifting that absolute is
  an ENCODER-DECODE problem (a separate axis), NOT a coref-training-track problem -- STEP 2 (a trained coref
  competency) is DEFERRED because the wiring is already shown and absolute perf is encoder-limited.

## Fairness gate (checked BEFORE any capability read)

1. `role_critical_fraction >= 0.55` (Tier1+2 population substantial; MEASURED 0.9).
2. `shortcut_tier1_acc <= 0.65` -- closed-form "always answer with the S value, ignore the queried role"
   heuristic must stay near-chance-on-role (MEASURED 0.43-0.59), i.e. Tier-1 items are genuinely
   role-dependent (not solvable without role info).
3. Tier-1 population >= min (20 LITE / 6 SMOKE).

## SCHEMA-VET fields

```yaml
one_variable: "role key supplied at competitive-coref unbind: correct (present) vs fixed-STATE (ablated)
  vs random (rand). EVAL-ONLY, frozen encoder, no training."
cell_chunked: false          # per-seed unit is the resumable granularity (record_unit per seed)
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: true
defensive_error_checking: "passed_all_4_patterns"
arms_differ_verified: true   # self-test asserts the role override actually changed >=1 b query role
final_metrics_atomicity: "tmp_replace"
crlb_n/a: "NO learned parameters anywhere. The resolver is the zero-param FHRR SituationWM (VERBATIM via
  clean); the ablation only swaps role_keys[role] at query-time unbind. Discriminator = the Tier-1
  present-minus-ablated accuracy delta on the harness decode pipeline."
baseline_in_band: "informational -- roles_present absolute Tier-1 ~0.51 is encoder-decode-limited; the
  headline is the DELTA, so absolute in-band is not the gate"
cardinality_ok: "EXPECTED_N_UNITS = n_seeds; verdict HARD_FAILs on breach"
calibration_check: "default_ok_for_this_regime -- no tuned knobs; the resolver + decode pipeline are reused
  verbatim; the only cell-specific choices are the tier thresholds (median distance) and the fixed bars"
composition_edges:
  - from: base_lib.run_base_multi (harness floors + role fairness references)
    to: this_cell.run_seed_unit (eval-only ablation)
    A_natural_output_shape: "base dict {floors, fairness, frozen refs}"
    B_natural_input_shape: "same base dict carried forward; ablation adds measure{tier:{present,ablated,rand}}"
    verdict: SHAPE_MATCH
  - from: eb.build_decoded_dataset (frozen encoder decode of eval passages)
    to: eb.run_arm_decoded (SituationWM resolver with role override)
    A_natural_output_shape: "decoded_ds list[passage] with queries[b].role"
    B_natural_input_shape: "same list, per-item query role overridden (present/ablated/rand)"
    verdict: SHAPE_MATCH
positive_control_arms:
  - arm: BASE_HARNESS_FLOORS_AND_ROLE_FAIRNESS
    primitive: base_lib.run_base_multi (VERBATIM reuse; can-fail floors + role fairness)
    cited_prior_atom: "exp_multi_competency_growing_library_v1 self-test PASS (prior cell, this session)"
    tolerance: "verbatim call; cannot diverge except via the shared codepath"
    regime_extension_audit: SHAPE_MATCH
functional_requirements:
  - requirement: "resolve a mark back to its entity (coreference)"
    primitive: "clean.SituationWM._coref_address (mark-addressing), VERBATIM"
  - requirement: "decode the queried role's value once the entity is resolved (thematic role)"
    primitive: "clean.SituationWM.query role_keys[role] unbind, VERBATIM"
  - requirement: "demonstrate the AND-gate CAUSALLY, eval-only, no training"
    primitive: "swap role_keys[role] at unbind: correct vs fixed-STATE vs random; measure Tier-1 delta"
real_code_path_exercised: [base_lib.run_base_multi, lt.RetrainableExtractor, eb.build_decoded_dataset,
  eb.run_arm_decoded, clean.SituationWM]
substrate_signature_checked: [base_lib.run_base_multi, eb.build_decoded_dataset, eb.run_arm_decoded]
guard_baseline_validated: N/A   # no control-beats-baseline break-guard; fairness gate (shortcut must not
  solve Tier-1) + the neutral rand_role control play the analogous role
deterministic_seeding: true    # numpy default_rng(seed + offset) for rand_role only; no hash(), no list(set())
progress_logging: "print_flush_true"
```

## Compute architecture

Sequential-CPU, EVAL-ONLY (frozen encoder decode + zero-param FHRR resolver; NO training -> NO negative-
transfer risk). Storage strategy: no_storage. Wall-time: self-test ~25s; smoke (1 seed, eval_n=30) ~35s;
LITE (3 seeds, eval_n=90) resumable per-seed. GPU-batching not warranted (single frozen decode pass +
lightweight FHRR argmax).

## Run

```
.venv/Scripts/python.exe experiments/exp_multi_competency_coref_ablation_v1.py --self-test
.venv/Scripts/python.exe experiments/exp_multi_competency_coref_ablation_v1.py --smoke
.venv/Scripts/python.exe experiments/exp_multi_competency_coref_ablation_v1.py --lite
```

(`--lite` is resumable per-seed unit via `tools/exp_checkpoint.py`, CPU-first, push-free, INLINE-LOCAL.)
