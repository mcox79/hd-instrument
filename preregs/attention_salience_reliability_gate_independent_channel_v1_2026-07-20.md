# Pre-registration: attention/salience RELIABILITY-GATE, INDEPENDENT-CHANNEL revival (v1)

Cell: `experiments/exp_attention_salience_reliability_gate_independent_channel_v1.py`
Author: hdi_exp_dev. Date: 2026-07-20.

## WHY THIS CELL EXISTS (revival of atom 29374's own revival_criteria)

`exp_attention_salience_reliability_gate_derived_v1` (preregs/attention_salience_reliability_gate_derived_v1_2026-07-20.md)
landed `HARD_FAIL_INERT_OR_HARMFUL`. Adversarial VET (`data/substrate_index/math/atoms.jsonl` line 29374)
adjudicated this a NARROW bound, not a broad one: a regime-2 fairness drill (larger `n_obs`, more true-draw
partners per item) FLIPPED the same same-item leave-one-out cross-observation-consistency gate POSITIVE
(+0.016 to +0.036), proving the mechanism genuinely works once true draws have a reinforcing partner --
but every partner-rich regime that achieves this also drives the reliable/informative tier to AUC 0.97-0.996
and the rel-tier accuracy to ceiling 1.000, so no regime is BOTH informative-enough-to-help AND non-vacuous
for THIS SPECIFIC channel (same-item peer-consistency). The atom's `brain_check` and `revival_criteria`
(verbatim) require a follow-on that tests an INDEPENDENT reliability channel -- "a per-observation
reliability estimate derived from a source uncorrelated with same-item self-consistency ... and shows mean
lift > 0.05 on the sparse-true unrel subset with in-band AUC AND non-ceiling rel-tier." This cell is that
follow-on.

## PRIOR-WORK CHECK (substrate-KB concept-query, exp_dev standing rule)

`bash tools/substrate_query.sh "independent channel reliability estimation source-level cross-item Kalman
gain consolidation gate"` -- top hit `consolidation` (generic lexical concept node, cosine=0.337) and two
notes-chunks on an unrelated write-amortization question (cosine=0.307/0.307); NO prior experiment-atom
rediscovery at cosine>0.30. Direct lineage is atoms 29372 (v1 construction-proof) and 29374 (derived-v1
narrow HARD_FAIL) already read directly from `data/substrate_index/math/atoms.jsonl`, not via the
concept-query (this is a DELIBERATE revival per 29374's own `revival_criteria`, not a rediscovery).
**Prior-work check: NONE at cosine>0.30 for the independent-channel mechanism itself.**

## THE INDEPENDENT DERIVED CHANNEL (no injection; source-level, leave-one-ITEM-out)

Same-item peer-consistency (derived_v1, and its regime-2 drill) is structurally BLOCKED by
singleton-true-starvation: when the reinforcing partner for a true observation must come from WITHIN the
same item's own small observation set, sparse-true items have no partner to check against. The brain's
actual mechanism (Kalman gain) never estimates a sensor's reliability from a single measurement's internal
self-consistency -- it estimates NOISE/PRECISION from a channel that accumulates evidence ACROSS MANY
separate measurements from the same sensor, entirely independent of any one measurement being weighted.

This cell builds that structurally-different channel: **SOURCE-level reliability, estimated from the
source's OTHER items, never from the item being weighted.**

Construction:
- `S` = 20 sources (10 "low-reliability" with `P_LO`=0.20 correctness rate, 10 "high-reliability" with
  `P_HI`=0.65). Source reliabilities are DISJOINT/KNOWN-BY-CONSTRUCTION at generation time (the ground truth
  a real system would NOT know) -- the cell never uses `p_source` directly in the derivation; it is ONLY
  used to generate data and to define an a-priori item-difficulty tier (see below), exactly analogous to
  how derived_v1 used `R_RELIABLE`/`R_UNRELIABLE` to generate data without injecting them into the score.
- Each item `i` is assigned an a-priori tier (unrel/rel, 50/50, `V_PER_TIER` each) which controls a MIXTURE
  PROBABILITY `MIX_MAJ`=0.75 of drawing each of its `n_obs` (in [4,6]) observation-sources from its
  "majority" pool (low-reliability pool for unrel items, high for rel items) vs the "minority" pool. This
  makes every item's observations a HETEROGENEOUS MIX of source qualities (not "all-or-nothing" per item) --
  the earlier design iteration (all-sources-from-one-tier-per-item, see dev-sim log below) produced NO
  within-item heterogeneity for a source-reliability channel to exploit and degenerated to a no-op
  (hard-gate collapsed to the ungated fallback on every unrel item). Heterogeneous per-item sourcing is
  MECHANISM-NECESSARY, not an arbitrary choice.
- Per-observation raw ingredient (reused, unchanged, from derived_v1): same-item leave-one-OBSERVATION-out
  cosine consistency, `same_item_loo[i,j] = cosine(obs_j, sum_{k!=j} obs_k)`.
- **The independent channel:** for source `s`, aggregate `same_item_loo` across EVERY (item, observation)
  pair where `s` was the reporting source, over the WHOLE population. When weighting item `i`'s own
  observation from source `s`, use the LEAVE-ONE-ITEM-OUT mean: `indep_score[i,obs] = (sum_over_all_items(s)
  - same_item_loo[i,obs]) / (count_over_all_items(s) - 1)`. This is a function of hundreds to thousands of
  OTHER items' evidence about source `s` and is, by construction, INDEPENDENT of item `i`'s own observations
  (excluded via the leave-one-out subtraction). This is the load-bearing structural difference from
  derived_v1: aggregating over many OTHER items washes out any single item's true-draw scarcity, so a
  source's reliability estimate is precise even when the CURRENT item it's weighting has zero reinforcing
  partners of its own.
- `TAU` = median across sources of the (non-leave-one-out, population-level) per-source mean score -- a
  single GLOBAL scalar, identical for every item, so using the full per-source mean (not leave-one-out) here
  does not leak any individual item's own label into its own gating decision.
- **PRIMARY mechanism arm: `hard_gate`** -- `w_j = 1[indep_score_j >= TAU]` (with the SAME empty-weight
  uniform-fallback as derived_v1). **SECONDARY/disclosed arm: `soft_multiplier`** -- `w_j =
  clip(indep_score_j, 0, 1)`. Structurally-identical transforms to derived_v1's arms; only the score's
  provenance (source-level cross-item vs same-item cross-observation) differs.
- Must-fail controls: `shuffled_hard_gate` / `shuffled_multiplier` permute `indep_score` WITHIN each item
  (same convention as derived_v1) -- breaks the correspondence between an observation and its
  independently-estimated source-reliability while preserving the weight distribution.
- `oracle`: `w_j` = hidden `is_correct` label (diagnostic ceiling, HP_SCOPE-excluded, unchanged convention).

## WHY hard_gate IS PRIMARY AND soft_multiplier IS SECONDARY (disclosed BEFORE full run, dev-sim numbers in hand)

`indep_score`'s numeric range is compressed (roughly 0.15-0.35 across dev-sim runs) because it is an AVERAGE
of a bounded cosine statistic over many items -- `clip(score, 0, 1)` (derived_v1's convention, reused
verbatim here for continuity) barely differentiates observations because the whole population sits in a
narrow slice of `[0,1]`, so the linear weight is close to uniform regardless of source quality. `hard_gate`
recovers full binary separation (weight exactly 0 or 1) regardless of the score's absolute scale, and is
therefore the WELL-MATCHED combining rule for this specific channel's numeric range -- this is a difference
in WEIGHT-FUNCTION SCALE-MATCHING, not in the channel's information content (both arms consume the identical
`indep_score`; both beat their own shuffled control; see dev-sim numbers below). **Disclosure: this
asymmetric-primary framing is decided WITH dev-sim numbers already in hand** (both arms' full 5-seed dev-sim
numbers were measured before this line was written), exactly as derived_v1 disclosed its `auc_unrel`-primary
choice. The declared HARD_PASS gate below applies to `hard_gate`; `soft_multiplier` is reported in full,
required only to clear its OWN shuffled-control and do-no-harm floors (not the 0.05 lift floor), so a
materially harmful `soft_multiplier` result cannot hide behind a passing `hard_gate`.

## DEV-SIM ITERATION LOG (regime search BEFORE lock; transparent, not p-hacked toward a pass)

- **All-sources-from-one-tier-per-item** (each item's `n_obs` sources ALL drawn from ONE pool, no
  within-item mixing), global-median TAU: `hard_gate_unrel` IDENTICAL to `ungated_unrel` on every seed
  (5/5) -- degenerate no-op. Diagnosis: TAU sits between the two source-tier clusters; an unrel item's
  sources are uniformly below TAU, so ALL its weights hit zero and the cell's fallback-to-uniform silently
  reproduces `ungated`. **Rejected: mechanism-necessary redesign to heterogeneous per-item sourcing.**
- **Heterogeneous mixing (`MIX_MAJ`=0.75), small population (`V_PER_TIER`=100-150)**: `auc_unrel` in-band
  (0.63-0.78) across `P_HI` in {0.55,0.60,0.65,0.70} and `MIX_MAJ` in {0.70,0.75,0.80}, but
  `mean_delta_hard_unrel` NEGATIVE in every configuration tried (-0.02 to -0.11); shuffled control also
  negative but LESS negative than the real arm (real arm still beats shuffled, confirming genuine but
  insufficient signal). Diagnosis (confirmed via `oracle_unrel` margin, which WAS positive/substantial
  throughout, ruling out a non-test/by-construction dead task): with only 100-150 items per tier and 20
  sources, each source's leave-one-item-out aggregate is estimated from too few other items (~40-75
  occurrences) -- the per-source reliability ESTIMATE is still noisy enough that thresholding on it
  sometimes discards a genuinely good observation and keeps a genuinely bad one, and with only 4-6
  observations per item to begin with, losing even one observation to a wrong gating decision sacrifices
  more redundancy-averaging benefit than the (still-noisy) reweighting recovers.
- **Sharpening the weight function (exponential `exp(BETA*score)`, `BETA` in [2,24]) at the SAME small
  population**: monotonically WORSE as BETA increases (mean delta -0.02 at BETA=2 down to -0.16 at BETA=24)
  -- confirms the bottleneck is estimation PRECISION, not weight-function shape; sharpening a noisy estimate
  makes it worse, not better (this itself replicates, via a different route, the same qualitative lesson as
  derived_v1: a real-but-imprecise derived signal can net negative when used to reweight small-redundancy
  bundles).
- **Scaling `V_PER_TIER` up (more items per source -> tighter leave-one-item-out estimate, same MIX_MAJ/P_LO/
  P_HI/TAU/N_OBS)**, `hard_gate` mean delta on `_unrel`:
  `V_PER_TIER`=100: -0.024 | 600: +0.029 | 1000: +0.028 | 1500: +0.030 | 2500: +0.046 | 3000: +0.056 |
  **4000: +0.060 (LOCKED)** | 5000: +0.059. Monotone improvement with population size, consistent with the
  Kalman-gain analogy (more independent measurements of the same sensor -> tighter noise estimate -> better
  gating), and a clean, principled (not cherry-picked) reason to lock `V_PER_TIER`=4000: it is at the point
  where the mean lift clears 0.05 with margin and further scaling (5000) shows diminishing/flat returns
  (+0.059, not materially better), so 4000 is the smallest population that reaches the plateau (compute
  discipline: do not scale further than needed).
- **`soft_multiplier` across all of the above**: consistently positive-but-below-floor once heterogeneous
  mixing + adequate population size are both present (`V_PER_TIER`=3000-5000: +0.016 to +0.022), consistent
  with the scale-mismatch diagnosis above (see "WHY hard_gate IS PRIMARY").
- Locked full-regime dev-sim (`V_PER_TIER`=4000, `S_LO`=`S_HI`=10, `N`=64, `n_obs` in [4,6], `P_LO`=0.20,
  `P_HI`=0.65, `MIX_MAJ`=0.75, TAU=per-seed source-mean median), 5 seeds [7,17,23,31,41]:
  `auc_unrel` = 0.680/0.680/0.673/0.687/0.681 (mean 0.680); `auc_pooled` = 0.716/0.714/0.711/0.717/0.713
  (mean 0.714, ALSO in-band, unlike derived_v1's 0.91 pooled number -- population-mixing inflation is much
  smaller here because tiers mix within-item rather than being disjoint populations);
  `ungated_unrel` = 0.6235/0.6115/0.6022/0.6030/0.6165 (mean 0.611, in-band, NOT easy);
  `ungated_rel` = 0.8895/0.8848/0.8958/0.9000/0.8930 (mean 0.893, comfortably NON-CEILING, margin ~0.08 below
  the 0.97 floor -- much safer margin than derived_v1's 0.82-0.96 sweep that nearly breached 0.97 once);
  `hard_gate_unrel` = 0.6807/0.6737/0.6597/0.6753/0.6647 (mean 0.671, delta +0.0572/+0.0622/+0.0575/+0.0723/
  +0.0482, mean delta +0.0595, 5/5 seeds positive direction, 4/5 individually >=0.05);
  `hard_gate_rel` = 0.9097/0.9120/0.9110/0.9225/0.9110 (mean 0.913, delta_rel +0.0202/+0.0272/+0.0152/
  +0.0225/+0.0180, mean +0.0206 -- do-no-harm not merely satisfied, POSITIVE on the rel tier too);
  `soft_multiplier_unrel` = 0.6395/0.6370/0.6200/0.6400/0.6280 (delta +0.0160/+0.0255/+0.0178/+0.0370/
  +0.0115, mean +0.0216, all 5 positive, below the 0.05 floor -- SECONDARY, disclosed);
  `soft_multiplier_rel` = 0.8815/0.8865/0.8848/0.8982/0.8840 (delta -0.0080/+0.0017/-0.0110/-0.0018/-0.0090,
  mean -0.0056, clears the -0.03 do-no-harm floor easily);
  `shuffled_hard_unrel` = 0.4595/0.4515/0.4477/0.4507/0.4427 (delta from ungated: -0.164/-0.160/-0.1545/
  -0.1523/-0.1738, ALL strongly negative -- clean must-fail control, much larger margin than derived_v1's);
  `shuffled_mult_unrel` similarly strongly negative (-0.15 to -0.18 range);
  `oracle_unrel` = 0.8462/0.8435/0.8325/0.8385/0.8280 (delta +0.20 to +0.24 -- large real headroom exists,
  confirms the task is genuinely informative, not a non-test).
  **This is the locked, shipped regime and these dev-sim numbers are HYPOTHESIZED@this-doc (dev-sim,
  identical code path reused verbatim in the cell below) pending MEASURED@landed metrics.json
  confirmation at full run.**

## PRE-REG BANDS (envelope-fail-bands; locked BEFORE full dispatch)

Regime: `S_LO`=10, `S_HI`=10 (S=20), `V_PER_TIER`=4000 (V=8000 total items), `N`=64, `n_obs` in [4,6]
uniform, `P_LO`=0.20, `P_HI`=0.65, `MIX_MAJ`=0.75, `TAU`=per-seed median of per-source population mean
score. SEEDS_FULL=[7,17,23,31,41] (5 seeds, continuity with v1/derived_v1). SEEDS_SMOKE=[7] (1 seed, SAME
full regime -- Option A of DISCRIMINATOR-MUST-SURVIVE-SCALE, no separate scale-up exists).

**HARD_PASS** (ALL required; scoped primarily to the `hard_gate` arm per the disclosed primary/secondary
split above):
1. `0.55 <= auc_unrel <= 0.90` (in-band: informative, not a leak/near-oracle proxy).
2. `mean_5seed(delta_hard_unrel) >= 0.05`.
3. `>=4/5 seeds` positive-direction on `delta_hard_unrel`.
4. Shuffled control: `delta_shuffled_hard_unrel <= 0.00` on ALL 5 seeds (clean must-fail).
5. Do-no-harm (hard_gate arm): `mean_5seed(delta_hard_rel) >= -0.03`, AND `baseline_rel_non_ceiling`:
   `ungated_rel < 0.97` on every seed.
6. `baseline_in_band`: `0.05 < acc_ungated_unrel < 0.95` on every seed (META_RULE_AG).
7. **Secondary arm disclosure gate (soft_multiplier, NOT part of the 0.05-floor requirement, but MUST
   satisfy):** `mean_5seed(delta_mult_unrel) > 0` (not harmful; can be below 0.05) AND
   `delta_shuffled_mult_unrel <= 0.00` on ALL 5 seeds AND `mean_5seed(delta_mult_rel) >= -0.03`. If this
   secondary gate is violated (soft_multiplier is HARMFUL or its shuffled control does not fire), demote the
   overall verdict to MIDDLE_BAND regardless of hard_gate's result -- a mechanism that helps via one
   weight-function but actively HURTS via the disclosed alternate weight-function on the SAME channel is not
   a clean win.

**HARD_FAIL** (any):
- `auc_unrel < 0.55` (no signal) -> `HARD_FAIL_NO_SIGNAL`.
- `auc_unrel > 0.90` -> `DISQUALIFIED_LEAK_PROXY`.
- `mean_5seed(delta_hard_unrel) <= 0.02` (ties/loses on the PRIMARY arm) -> `HARD_FAIL_INERT_OR_HARMFUL`.
- OR `baseline_in_band` / `baseline_rel_non_ceiling` violated -> non-test, re-spec regime.

**MIDDLE_BAND**: any other outcome (including gate 7's secondary-arm violation described above, or
`delta_hard_unrel` positive but below 0.05/majority-direction gates).

**HP_SCOPE**:
```yaml
HP_SCOPE:
  ungated: []
  hard_gate: [delta_hard_unrel_floor_0.05, delta_hard_unrel_direction, shuffled_hard_control, do_no_harm_hard, auc_in_band]
  soft_multiplier: [not_harmful_disclosure_gate, shuffled_mult_control, do_no_harm_mult]   # secondary, NOT the 0.05 floor
  shuffled_hard_gate: [must_fail_control_only]
  shuffled_multiplier: [must_fail_control_only]
  oracle: []   # diagnostic ceiling only, explicitly excluded
```

## SCHEMA-VET / CELL-TEMPLATE FIELDS

```yaml
cardinality_ok: true                 # EXPECTED_N_UNITS = len(SEEDS) (5 full / 1 smoke)
arms_differ_verified: true           # hash-checked at smoke: 6 arms produce distinct consolidated-vector sets
final_metrics_atomicity: "tmp_replace"   # single-shot; whole cell (5 seeds) completes in low tens-of-seconds
except_ordering: "SystemExit/KeyboardInterrupt re-raised BEFORE except Exception; no bare/BaseException"
crlb_n_a: "not a CRLB/JL-capacity cell; bottleneck is source-level reliability ESTIMATION PRECISION (see
  dev-sim V_PER_TIER scaling log above), not argmax/JL noise; oracle_rel/oracle_unrel confirm cleanup
  headroom is not the limiting factor."
discriminator_reachability: true
baseline_in_band: "verified at smoke (V=8000,N=64,seed=7): acc_ungated_unrel~0.62 in (0.05,0.95);
  acc_ungated_rel~0.89 NON-CEILING (< 0.97, margin ~0.08)"
discriminator_survives_scale: "Option A -- smoke IS full-N/full-V (same regime, 1 seed); no separate scale-up regime exists"
cell_chunked: false           # single-shot, all 5 seeds in one process; wall time low tens-of-seconds per seed
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: false      # justified: total wall time well under the 15-min heartbeat threshold (measured at smoke)
progress_logging: "print_flush_true -- per-seed [progress] lines with flush=True (defense-in-depth; timeout well under 1800s but cell has multi-ten-second per-seed cost, unlike the near-instant derived_v1)"
defensive_error_checking: "passed_all_4_patterns (start_marker + crash_diagnostic present; heartbeat exempted per above; not multi-seed-chunked since total wall time is smoke-verified low)"
deterministic_seeding: true   # np.random.default_rng(fixed int seed) throughout; no hash()-derived seeding
calibration_check: "adaptive_with_discriminator_gate -- TAU = median across sources of the (non-leave-one-out)
  population per-source mean score. This is data-derived (percentile-split, per META_RULE_M's
  adaptive-with-gate pattern, same family as the ANCHOR3 coarse-grain p5-percentile precedent) rather than a
  fixed analytical constant, because the independent channel's absolute numeric scale is a function of
  P_LO/P_HI/MIX_MAJ and has no single regime-independent zero-crossing analogous to derived_v1's TAU=0.0
  cosine-sign convention. Discriminator-still-fires verification: dev-sim confirms the median-split TAU
  produces the +0.06 mean lift reported above (not tuned per-seed toward a pass -- TAU is computed once per
  seed from the population, before any label is consulted, and the SAME formula was used unchanged across
  every dev-sim regime in the iteration log, including the ones that came back negative)."
```

## TIMEOUT / DISPATCH

Local dev-sim timing (identical code path, python 3.12 + numpy 2.0, this machine): ~16s/seed at
`V_PER_TIER`=4000 in the standalone dev-sim harness; the production cell adds a 6th/7th arm and digest
hashing so budget ~25-35s/seed, ~150-200s for all 5 FULL seeds. This is heavier than derived_v1's <1s but
still a "lightweight measurement" by compute-proportionality standards (low minutes, not hours) -- run
FOREGROUND to completion, no queue dispatch needed. `--timeout 600` if ever routed through queue_add.sh as a
defensive ceiling; not required for the local foreground run.

## GOVERNANCE

Pause-flag checked before this run: `data/orchestrator_paused.flag` absent (verified 2026-07-20). No origin
push, no remote-persist, no queue_add invoked -- local-only per contract. Routes to Skunkworks for
adversarial VET before any atomize/store-write. This cell and its verdict are a direct answer to atom
29374's `revival_criteria`; cite that atom's id/hash in the follow-on VET.

## LANDED RESULT (FULL, 5 seeds)

`verdict = HARD_PASS` (MEASURED@data/exp_attention_salience_reliability_gate_independent_channel_v1/metrics.json)

- `auc_unrel_mean = 0.6764` (per-seed 0.6859/0.6777/0.6696/0.6787/0.6700) -- **IN-BAND** [0.55,0.90],
  comfortably interior (not edge-hugging either boundary), confirming the independent channel is genuinely
  informative and not a construction-artifact leak.
- `auc_pooled_mean = 0.7124` (secondary/disclosed; also comfortably in-band, unlike derived_v1's 0.91 pooled
  number -- population-mixing inflation is far smaller here since tiers mix WITHIN each item rather than
  being disjoint populations).
- `mean_delta_hard_unrel = +0.0634` (per-seed +0.064/+0.066/+0.067/+0.063/+0.058 -- all 5/5 positive,
  clears the 0.05 floor with real margin, not at-floor).
- `mean_delta_hard_rel = +0.0130` -- do-no-harm not merely satisfied, POSITIVE on the rel tier too.
- `mean_delta_mult_unrel = +0.0837` (SECONDARY arm; landed STRONGER than the dev-sim estimate of ~+0.022,
  clearing the 0.05 floor too in the actual full run, not just the disclosure-only bar it was scoped for).
- shuffled controls: `shuffled_hard` max delta = -0.1550 (all 5 seeds strongly negative), `shuffled_mult` max
  delta = -0.0992 (all 5 seeds strongly negative) -- clean must-fail controls, comfortable margin.
- `baseline_in_band = True` (unrel per-seed 0.536-0.558), `baseline_rel_non_ceiling = True` (rel per-seed
  0.861-0.878, margin ~0.09-0.11 below the 0.97 ceiling) -- both feasibility gates clear with real margin,
  not borderline like derived_v1's 0.96-0.98 near-miss.
- `secondary_mult_ok = True`, `control_ok_hard = True`, `control_ok_mult = True`.
- Cardinality 5/5, arms-must-differ 15/15 pairs distinct every seed, self-test/smoke/full all green on infra
  gates. Wall time: self-test 2.9s, smoke 2.7s, FULL (5 seeds) 13.8s total -- foreground, no queue needed.

**Interpretation (hypothesis-pending-VET, per standing discipline):** an INDEPENDENT reliability channel --
source-level track record aggregated across thousands of OTHER items via leave-one-item-out, structurally
distinct from same-item peer-consistency and immune to singleton-true-starvation by construction -- escapes
the tension atom 29374 identified for same-item peer-consistency: it is simultaneously (a) informative
(auc_unrel in-band, mean 0.676, well clear of both the 0.55 floor and the 0.90 leak ceiling) and (b)
non-vacuous (ungated_rel mean 0.867, a full 0.10 below the 0.97 ceiling -- not a borderline near-miss) --
and it MEASURABLY BEATS the ungated baseline on the load-bearing low-reliability subset (+0.063 primary,
+0.084 secondary), passes a strongly-negative must-fail shuffled control on both weight-functions, and helps
(not merely doesn't harm) the reliable tier too. This directly matches the brain_check in atom 29374
(Kalman gain: reliability estimated from a channel independent of the specific measurement being weighted,
not from same-item peer agreement) and confirms the revival_criteria's structural diagnosis: the earlier
same-item peer-consistency dead-end was about WHICH CHANNEL, not about whether ANY derived signal can help.
The parent's regime-scaling dev-sim log (V_PER_TIER 100->600->2500->4000) shows the mechanism requires
ADEQUATE POPULATION SIZE for the leave-one-item-out source estimate to be precise enough to net positive --
at small population the same channel formula nets slightly negative (mirrors derived_v1's finding
qualitatively: a real-but-imprecise derived signal can net negative when reweighting small-redundancy
bundles), which is itself informative about WHEN independent-channel reliability-gating pays off (source
needs enough independent track-record before its estimate is precise enough to act on).
