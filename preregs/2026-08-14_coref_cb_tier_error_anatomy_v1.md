# PRE-REGISTRATION -- exp_coref_cb_tier_error_anatomy_v1

DATE: 2026-08-14
ORGAN: E3 (coreference), ORGAN_MAP row E3; SUBSTRATE_STRATEGY step "coreference as competitive
retrieval".
PHASE: 1 of 2. DIAGNOSE BEFORE BUILDING. This cell proposes NO mechanism and changes NO resolver.
It characterises the errors and PRE-COMMITS the decision rule that decides whether a Phase-2
mechanism is licensed at all.

STATUS OF THIS FILE: written and committed BEFORE any arm was run.

---

## 1. WHAT IS ALREADY SETTLED (do not re-litigate; cited, not re-measured here)

- `base_principle_b` P_competitive = **0.7191** on n=89 competitive decisions (136 pronouns,
  54 passages, two gold sets).
  MEASURED@d:/AI/hd-instrument/data/exp_coref_actr_tiebreak_under_centering_v2/metrics.json:P_competitive_by_arm.base_principle_b
- Same-run floors ON THIS METRIC: `floor_most_recent` **0.5281**, `floor_singleton` **0.0000**.
  MEASURED@ same file, same key.
- ACT-R base-level activation as a REPLACEMENT for the pick: HARD_FAIL
  (base_principle_b 0.7191 > actr_base 0.6180 > actr_parallel 0.5843; the parallel arm's own
  scramble control 0.5938 > ordered 0.5843, i.e. it was not order-sensitive).
  MEASURED@d:/AI/hd-instrument/data/exp_coref_cue_based_retrieval_actr_activation_v1/metrics.json:P_competitive_by_arm
  SHELVED. Not re-proposed.
- ACT-R as a TIEBREAK under the Cb tier: VACUOUS by construction and declared so in advance --
  only **17 of 89** competitive decisions ever reach the tiebreak, and the arms differed on 2.
  MEASURED@d:/AI/hd-instrument/data/exp_coref_actr_tiebreak_under_centering_v2/metrics.json:discriminators
- The salience arithmetic defect (`count + 0.5*exp(-0.1*d)` bounded in (0,0.5], so recency can
  never overturn a count gap of 1) is REAL and machine-confirmed on 89/89 decisions
  (`D2_salience_equals_argmax_count_fraction` = 1.0), but it is NOT on the canonical resolver's
  path -- `run_principle_b` does not call `salience()` at all.

**CROSS-RUN HYGIENE, restated so this cell cannot repeat the error ORGAN_MAP already corrected
once.** The pair recency **0.5614** / singleton **0.3860**, our resolver **0.7193**, earned
**0.6842**, oracle **0.9298** belongs to `exp_wire_coref_accumulate_situation_model_v1` --
identity-demanding QUERY accuracy over 36 McGuffey passages. It is a DIFFERENT metric from
`P_competitive` (link-level pronoun accuracy on the >=2-compatible-candidate subset). Both pairs
are real; neither may be placed beside the other's arm scores. This cell reports
`P_competitive` and therefore quotes 0.5281 / 0.0000 as ITS floors, and states the 0.5614 / 0.3860
/ 0.9298 triple only as organ-level context with its provenance attached.

## 2. THE QUESTION

`base_principle_b` gets **25 of 89** competitive decisions wrong. Both prior cells established that
those errors are NOT in the tiebreak and NOT in the salience arithmetic. They are inside the Cb
tier's own decisions. **What are they?**

Specifically, and pre-committed as the primary split:

**RETRIEVAL failure** -- at the moment of decision, NO entity in the candidate pool the pick
actually ranks over was gold-coreferent with the pronoun. No ranking rule, however good, could have
answered correctly. The fault is upstream: agreement filter, Principle-B filter, or the entity was
never allocated / was merged wrongly by the name branch.

**RANKING failure** -- a gold-coreferent entity WAS in the pool and was not chosen. This is the only
class a better pick rule can fix.

This distinction is the finding regardless of whether any Phase-2 fix succeeds.

## 3. DEFINITIONS (fixed here so they cannot be chosen after seeing the numbers)

- Competitive decision: `competitive_mask` from the v1 cell, unchanged -- a pronoun mention facing
  >=2 gn-compatible tracked entities, replayed over the arm-independent registry.
- Correctness: `hdlab.coreference_resolver.mention_link_wrong`, unchanged. Link-level, judged at
  mention i's own decision time.
- **Gold-correct entity** at decision i: a tracked entity e such that the MOST RECENT prior mention
  assigned to e has `gold_entity == stream[i]["gold_entity"]`. This is exactly the antecedent
  `mention_link_wrong` will accept, so "a gold-correct entity was in the pool" and "choosing it
  would have scored correct" are the same statement by construction, not by approximation.
- Pool: the list `_pick_strict_cb` actually ranks -- i.e. `compat` after `_principle_b_filter`.
- Cb tier outcome, three mutually exclusive and exhaustive values:
  - `cb_unique` -- >=1 candidate has subject history and exactly ONE holds the max
    most-recent-subject-clause. The Cb tier alone decided.
  - `cb_tied` -- >=2 candidates tie at the max most-recent-subject-clause; `last_pos` decided.
  - `cb_none` -- no candidate has subject history; `last_pos` decided over the whole pool.

## 4. PRE-COMMITTED ERROR CATEGORIES

Every one of the 25 errors is assigned to exactly one PRIMARY cause, in this fixed precedence order
(first match wins). The order is fixed now:

1. `RETRIEVAL_pb_filter_removed_gold` -- gold-correct entity was in `compat` but the Principle-B
   filter removed it.
2. `RETRIEVAL_agreement_filter_removed_gold` -- a gold-correct entity existed in the registry but
   `gn_compatible` excluded it.
3. `RETRIEVAL_no_gold_entity_in_registry` -- no gold-correct entity existed at all (upstream
   name-branch allocation/merge failure).
4. `RANKING_cb_unique_wrong` -- gold-correct entity in pool; Cb tier uniquely picked a different one.
5. `RANKING_cb_tied_wrong` -- gold-correct entity in pool; Cb tie, `last_pos` picked wrong.
6. `RANKING_cb_none_wrong` -- gold-correct entity in pool; no subject history, `last_pos` picked
   wrong.

Cross-cutting descriptors recorded for EVERY competitive decision (not just errors), so the error
rate per stratum is computable against its own base rate:
`n_compat`, `n_pool`, `pb_action`, pronoun surface + gender + number, pronoun's own role,
`same_gender_all_pool` (all pool entities with a known gender share it), mention distance
`pos - last_pos` for chosen and for gold, clause distance, `gold_is_prev_clause_subject`,
`chosen_is_prev_clause_subject`, `gold_ever_subject`, `gold_is_most_recent_in_pool`, dataset,
passage_id.

## 5. DISCRIMINATORS -- RANGE BY CONSTRUCTION, NO HAND SCORING

Every quantity below is computed by machine from the gold files. Nothing is hand-scored.

- **D1 `n_errors`** must equal 25 (89 * (1 - 0.7191)). If it does not, the replay has drifted from
  the scored arm and the cell FAILS as `REPLAY_DRIFT` regardless of any other number. Range: 0..89.
- **D2 `P_ceiling_ranking`** = (89 - n_retrieval_failures) / 89. The best score ANY pure ranking fix
  could reach. Range [0,1] by construction; equals 1.0 only if every error is a ranking error.
- **D3 `top_cause_share`** = largest single PRIMARY cause / n_errors. Range [1/6, 1].
- **D4 `n_cb_unique_wrong`** -- errors where the Cb tier uniquely and wrongly decided. This is the
  cell's own target-size estimate for a Cb-tier fix. Range 0..25.

## 6. BANDS -- CAN FAIL, COMMITTED BEFORE THE RUN

This cell's verdict is about WHERE THE ERRORS ARE, not about beating a baseline. The bands gate
whether Phase 2 is licensed:

- **`RANKING_DOMINATED`** (Phase-2 ranking cell LICENSED): `P_ceiling_ranking - 0.7191 >= 0.05`,
  i.e. at least 5 of the 25 errors are ranking errors AND the resulting headroom clears the
  standing HARD_PASS delta band of 0.05 used by both prior cells. A ranking fix can in principle
  reach HARD_PASS.
- **`RETRIEVAL_DOMINATED`** (Phase-2 ranking cell REFUSED): `P_ceiling_ranking - 0.7191 < 0.05`.
  The pick rule is capped below the band by the pool it is handed. Any ranking mechanism is
  DISCRIMINATOR-UNREACHABLE at this regime and must not be dispatched; Phase 2 must target the
  pool (agreement filter / Principle-B filter / name-branch allocation) or nothing.
- **`DIFFUSE_UNPINNED`** (Phase 2 PARKED): `top_cause_share < 0.32` (fewer than 8 of 25 in the
  largest single cause). No single characterised cause is large enough to aim a brain-faithful
  mechanism at; the honest answer is UNPINNED and the step is parked rather than a mechanism
  invented. Reported even when RANKING_DOMINATED also holds -- the two are orthogonal and both
  are stated.
- **`REPLAY_DRIFT`** (cell invalid): D1 != 25.

**Power, stated in advance and not to be forgotten downstream.** n=89 with 25 errors. A fix moving
4 decisions is +0.045 and will NOT separate from zero on a 54-passage paired cluster bootstrap.
This cell therefore ALSO reports, for the largest cause, the number of decisions a perfect fix to
that cause would move, and pre-commits: **if the largest fixable cause is < 5 decisions, no Phase-2
cell is dispatched on this corpus** -- the honest report is "characterised but underpowered here",
not a tuned win.

## 7. CONTROLS AND HYGIENE

- No mechanism is introduced, so there is no treatment arm and no tuning surface. The cell cannot
  be tuned to reach a band because its outputs are counts of a fixed partition of a fixed set.
- Positive control: the replayed decision sequence must reproduce `run_principle_b`'s assignment
  BYTE-IDENTICALLY on every passage (self-test check 1). If the replay drifts, every category is
  meaningless -- this is the `REPLAY_DRIFT` guard, enforced at self-test AND at run time.
- Base-rate control: every descriptor is tallied over ALL 89 competitive decisions, not only the 25
  errors, so "errors are same-gender" cannot be reported without "so are N of the correct ones".
- Reported alongside: `run_strict_cb` (no Principle-B filter) on the same decisions, so any cause
  attributed to the Principle-B filter is checkable against the resolver that lacks it.

## 8. COMPUTE ARCHITECTURE

Class: **(b) sequential-CPU with justification.** Pure symbolic replay over 54 short passages;
total wall time is seconds. No matmul, no GPU-batchable work. numpy is used only for the
descriptive tallies. Storage: `no_storage` (no hypervector store is involved).
Route: LOCAL foreground to completion. `crlb_n/a`: no noise floor -- every quantity is an exact
count over a finite fixed set, not an estimate from a noisy channel. The band-reachability analysis
that CRLB normally serves is done directly by D2 (`P_ceiling_ranking`), which IS the exact
attainability bound for the Phase-2 mechanism class.

## 9. SCHEMA-VET FIELDS

```yaml
cell_chunked: false                  # single unit, seconds; no seed axis
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: false             # exempt: total wall time < 10s, far under the 15-min rule
defensive_error_checking: "passed_all_4_patterns (heartbeat exempt: <10s cell)"
cardinality_ok: true                 # EXPECTED_N_UNITS = 2 datasets x 1 analysis = 2
arms_differ_verified: n/a_single_analysis_no_treatment_arm
final_metrics_atomicity: "tmp_replace"
calibration_check: "default_ok_for_this_regime"   # no thresholds are calibrated; all counts exact
baseline_in_band: true               # base_principle_b = 0.7191, inside (0.05, 0.95)
discriminator_reachability: true     # D1-D4 are counts over a finite set; all values attainable
crlb_n/a: "exact counts over a fixed finite decision set; no estimator noise floor applies"
sweep_alignment_verdict: ALIGNED     # no sweep
discriminating_fraction: n/a_no_sweep
composition_edges: []                # no primitive composition; single symbolic replay
positive_control_arms:
  - arm: REPLAY_REPRODUCES_RUN_PRINCIPLE_B
    primitive: hdlab.coreference_resolver.run_principle_b
    cited_prior_metric: 0.7191       # P_competitive, same corpus, same metric, same code
    tolerance: 0.0                   # byte-identical assignment required, not a tolerance
    if_outside_tolerance: REPLAY_DRIFT (cell invalid, no categories reported)
functional_requirements:
  - "separate errors a better pick could fix from errors it could not" -> the pool-membership test
  - "size the fixable class" -> D2 P_ceiling_ranking
  - "decide whether any mechanism is licensed" -> section 6 bands
real_code_path_exercised: [run_principle_b, _principle_b_filter, _pick_strict_cb,
                           _resolve_name_branch, gn_compatible, mention_link_wrong, build_mention_stream]
substrate_signature_checked: [run_principle_b, _principle_b_filter, _pick_strict_cb]
guard_baseline_validated: n/a_no_break_guard
deterministic_seeding: true          # no RNG at all in this cell; sorted(set()) ordering throughout
progress_logging: n/a                # timeout_s well under 1800
```

## 10. WHAT PHASE 2 WOULD BE, AND WHAT WOULD FORBID IT

Recorded now so the Phase-2 decision cannot be reverse-engineered from the Phase-1 numbers.

- `RETRIEVAL_DOMINATED` -> no ranking cell. Report the pool defect and stop.
- `DIFFUSE_UNPINNED` -> no cell. Report UNPINNED and park, per the standing rule that an honest
  UNPINNED beats an invented mechanism.
- largest fixable cause < 5 decisions -> no cell (underpowered on this corpus).
- Otherwise -> ONE cell, one variable, aimed at the largest characterised cause, reusing the
  existing organ (Centering backbone + the existing margin-gated abstention), with both floors, the
  paired bootstrap, and a control isolating that one variable. A negative there is a result and is
  reported as one.
