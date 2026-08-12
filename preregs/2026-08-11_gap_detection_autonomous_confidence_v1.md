# gap_detection_autonomous_confidence_v1 -- pre-registration

Author: exp_dev (Agent-Teams). Task source: hdi_research/USER "shore up architecture audit
finding #3" (notes/architecture_audit_2026-08-11.md TIER-2 item 3, VERY HIGH impact):
"gap-DETECTION has no autonomous component (MISLABEL): every 'gap' is an offline KB
set-difference (build_gap_set) or a hand-picked curriculum. No online prediction-error/surprise/
confidence -- the machinery has never run on a gap it found itself." This cell builds and proves
the missing organ.

**Prior-work check** (`bash tools/substrate_query.sh --k 8 "autonomous online gap detection
confidence familiarity signal CA1 comparator prediction error novelty floor decision"`,
cosine>0.30 threshold): top hit cosine=0.377, entity `Anchor 1:
novelty_detection_prediction_error_v1` (`notes/exp_dev_handoff_research_realtime_multimodal_
biology_3x_2026-06-09.md`) -- a 2026-06-09 DESIGN PROPOSAL ("distance-to-nearest-neighbor IS
prediction error ... implemented as distance from nearest codebook vector", `P_deflated=0.45`,
never run) that predates `hdlab.hd_fact_store` / `hdlab.three_tier_loop` (both promoted THIS
session, 2026-08-11, per the architecture audit's own dated findings) by over two months --
there was no live glass-box KB for it to run against at the time. This cell is the first REAL
implementation of that old anchor's idea, wired to the organs that exist today. Genuinely novel
closure, not a rediscovery (second hit cosine=0.317, `signal_detection`/WordNet, generic
dictionary noise).

## Mechanism

`hdlab/gap_detector.py` (new module). For a probe `(subject, relation, candidate_object)`:

1. **Content signature**: `content_key(store, s, r, o) = quantize(bind(REL,r) + bind(ARG0,s) +
   bind(ARG1,o))` -- a direct 3-pair extension of `HDFactStore._sr_key`'s existing 2-pair
   `(subject,relation)` signature (same `_bipolar_bind`/`_bipolar_quantize` primitives, same
   shared symbol codec). Deterministic; identical `(s,r,o)` strings -> bit-identical vector.
2. **CA3/DG pattern completion**: `hdlab.cleanup_family.iterative_attractor` (imported verbatim,
   not reimplemented) picks the best-matching row in a codebook rebuilt fresh, on every
   `refresh()`, from `HDFactStore.live_facts()` (i.e. from the store's OWN current
   `ACTIVE_STATUSES` bookkeeping -- no separate "known-set" is ever cached statically).
3. **CA1 match/mismatch comparator**: the familiarity **margin** is the RAW cosine between the
   *untouched* probe vector and its CA3-selected winner, computed BEFORE the attractor's
   iterative pull -- reading the attractor's post-settle state instead would be uninformative
   (the softmax dynamics blend toward *some* winner on every call, converged or not).
4. **Decision**: `is_gap = margin < FLOOR`. `FLOOR = 0.625` (THEORETICAL, see below).

No pre-computed gap-set (`build_gap_set` or any hand-curated list) is ever constructed or
consulted anywhere in this mechanism.

## FLOOR derivation (THEORETICAL@module docstring; bipolar bind/quantize algebra)

For a 3-pair bipolar bundle `q = quantize(A+B+C)` with each term an independent random bipolar
vector, per-component agreement probability between two such bundles sharing `k` of 3 terms:

| shared terms | P(bit agree) | expected cosine (`2P-1`) |
|---|---|---|
| 3 (exact match) | 1.0 | **1.0** |
| 2 (e.g. same subject+relation, diff object) | 0.75 | **0.5** |
| 1 (e.g. same relation only) | 0.625 | **0.25** |
| 0 | 0.5 | **0.0** |

`FLOOR = midpoint(1.0, 0.25) = 0.625` -- strictly between "known" and the "shares-1-of-3" novel
construction (test 1) with ~0.35 headroom either side, and strictly below the harder
"shares-2-of-3" construction (test 1b / test 3's post-lesion state, ~0.5) with ~0.125 headroom.
Not tuned on the graded test data.

**Empirical confirmation** (`hdlab/gap_detector.py`'s own formula self-tests, `n_dim=2048/4096`,
`_run_all_selftests`, all PASS):
`exact_match_margin_1.0`, `wholly_novel_low_margin` (<0.20), `shares_two_of_three_intermediate`
(0.30-0.70 band), `ablation_collapses_to_noise`, `scramble_flips_known_to_gap`,
`empty_kb_all_gap`.

## Tests (4 independently-graded axes + 1 honest secondary diagnostic)

### Test 1 -- CORRECT DETECTION (signal-detection)
`FULL`: 240 facts across 6 relations (`capital_of, made_of, part_of, located_in, produces,
born_in`) stored in a live `HDFactStore(n_dim=4096)`; 100 KNOWN probes (exact stored triples,
disjoint slice), 100 NOVEL-EASY probes (fresh entities never registered, verified absent by
construction -- deterministic `NOVEL_SUBJ_*`/`NOVEL_OBJ_*` namespace never used for real
entities). `hit_rate`, `false_alarm_rate`, `d_prime`, `AUC` (Mann-Whitney rank-sum, pure numpy)
reported, not a single number.

**Bands**: HARD_PASS: `auc>=0.90` AND `d_prime>=2.0` AND `hit_rate>=0.90` AND
`false_alarm_rate<=0.10`. HARD_FAIL: `auc<=0.65` OR `d_prime<=0.5`. Else MIDDLE_BAND.

### Test 1b -- harder novel condition (HONEST SECONDARY, does not gate the cell verdict)
60 NOVEL-HARD probes: real `(subject,relation)` pairs (disjoint slice from test 1's known probes)
paired with a wrong, never-stored object (`WRONG_OBJ_*`). Theory predicts margin~0.5 (shares
2/3), a genuinely tougher discrimination than test 1's ~0.25. Reported for honesty per the task's
own "report hit-rate/FA/d-prime, not a single number" instruction; not a HARD_PASS gate.

### Test 2 -- NOT-A-LOOKUP (the decisive control vs the mislabel it replaces)
`GapDetector.familiarity(..., use_confidence_signal=False)`: the REAL margin is computed (so
codebook state + attractor diagnostics are exercised identically) then DISCARDED and replaced by
fixed-seed uniform noise (`ABLATION_SEED=20260811`, a separate deterministic RNG stream,
consumed in call order, uncorrelated with true label). Recomputes AUC/d-prime on the SAME 200
probes.

**Bands**: HARD_PASS: `arms_differ_verified` (real vs ablated margin vectors non-identical,
META_RULE_AF-style) AND `delta_auc (real - ablated) >= 0.35` AND `ablated_auc in [0.35, 0.65]`
(chance-ish band). HARD_FAIL: `not arms_differ_verified` OR `delta_auc < 0.15` OR
`ablated_auc >= 0.75` (signal survives ablation -> a hidden shortcut/leak). Else MIDDLE_BAND.

### Test 3 -- SCRAMBLE / KB-STATE-SENSITIVITY
40 lesion-target facts stored at `TRUST_MID` (everything else `TRUST_HIGH`). After confirming
`is_gap=False` (correctly recognized) for all 40 pre-lesion, each is REPLACE-lesioned via the
store's OWN `store()`-ingest-vet mechanism: `store.store(subject, relation,
"LESION_REPLACEMENT_OBJ_<i>", "lesion_source", "TRUST_HIGH")` -- a genuine live-KB-state mutation
(a higher-trust conflicting fact naturally supersedes the old one via `HDFactStore`'s own
documented conflict resolution, NOT a private-field hack). `detector.refresh()` re-reads the
live state; `flip_rate` = fraction of previously-correctly-known facts that become detected gaps.

**Bands**: HARD_PASS: `flip_rate>=0.90` AND all lesion stores resolved `REPLACE`. HARD_FAIL:
`flip_rate<0.50` OR any lesion store did not resolve `REPLACE` (setup failure). Else MIDDLE_BAND.

### Test 4 -- END-TO-END (detect -> gather -> reason -> gate, zero hand-fed gap-set)
A small "world": 10 subjects, each with a real 1:1 `USES` edge to one of 10 materials (hop1
`KGStore`) and each material with a real `BELONGS_TO` edge to one of 3 categories (hop2
`KGStore`) -- classic `hdlab.gather_reason` 2-hop shape. A `ThreeTierLoop`'s own
`foundation_store` is pre-seeded with the TRUE category fact for the 5 EVEN-indexed subjects
(`store.store(subject, "BELONGS_TO_CATEGORY", true_category, ...)`); the 5 ODD-indexed subjects
have nothing stored -- the TRUE gaps, known only to the test harness for grading.

`GapDetector` (wrapping `loop.foundation_store`) scans all 10 subjects x 3 candidate categories
each; a subject is `AUTONOMOUS_GAP_DETECTED` iff NO candidate clears `FLOOR`. The GATHER
(`hdlab.gather_reason.fanout_two_hop`, `k1=1` -- see note below) + GATE
(`ThreeTierLoop.encounter`/`consolidate`, the exact 8-encounter + 2-consolidate intervening-pass
pattern proven in `verification/test_three_tier_loop_e2e.py`'s own GAP_A case) steps run
EXCLUSIVELY over `autonomous_detected_gap_subjects` -- the detector's own runtime output. The
true odd-subject list is used ONLY for grading (`detection_recall`,
`detection_false_positives`), never passed to the loop.

**`k1=1` note** (found during authoring, disclosed): this world's subject->material edge is a
clean 1:1 mapping (branching factor 1, no real fan-out) by construction, so restricting hop-1 to
its single best candidate is the structurally correct parameter for THIS domain, not a tuned
fix. MEASURED@diagnostic (pre-fix, `k1=5`): an unrelated noise hop-1 candidate (a different
material with its OWN strong, unrelated hop-2 edge) out-scored the true material's hop-2 edge
under max-aggregate for 1/5 (self-test/smoke) subjects -- the same hub-competition phenomenon
`hdlab.gather_reason.fanout_two_hop`'s own `restrict_hop1_to` parameter exists to remove.
Verified hop1's own top-1 vs top-2 margin is >10x for every subject in this world, so `k1=1`
loses no real recall.

**Bands**: HARD_PASS: `detection_recall>=0.80` AND `detection_false_positives==0` AND
`reasoning_accuracy>=0.80` AND `resolution_accuracy>=0.80`. HARD_FAIL: `detection_recall<0.50`
OR `resolution_accuracy<0.50`. Else MIDDLE_BAND.

## Overall cell verdict
HARD_PASS iff ALL 4 gated tests (1, 2, 3, 4) individually HARD_PASS. HARD_FAIL if ANY
individually HARD_FAIL. Else MIDDLE_BAND. Test 1b is reported but does not gate.

## Functional requirements (Gate E)

| Requirement | Owned primitive |
|---|---|
| Content signature (probe + known-fact encoding) | `hdlab.gap_detector.content_key` (new, extends `HDFactStore._sr_key`'s existing 2-pair pattern) |
| CA3/DG completion (best-match pick) | `hdlab.cleanup_family.iterative_attractor` (reused verbatim) |
| CA1 comparator margin | `hdlab.gap_detector.ca3_match_score` (new; factors out the dot/norm cosine `hdlab.gather_reason.ca3_relevance_gather`'s own peel-loop computes internally but does not expose) |
| Live consolidation-status-aware KB | `hdlab.hd_fact_store.HDFactStore` / `ACTIVE_STATUSES` / `live_facts()` (reused verbatim) |
| GATHER + REASON (test 4) | `hdlab.gather_reason.fanout_two_hop` (reused verbatim) |
| GATE / assembled loop (test 4) | `hdlab.three_tier_loop.ThreeTierLoop.encounter/consolidate/answer`, `gap_item_key` (reused verbatim) |

## Compute architecture
(b) sequential-CPU with justification: single deterministic pass, no independent phase-point
grid to batch; every attractor call is an M(hundreds)xN_DIM(4096) numpy matmul, sub-ms.
MEASURED@`data/exp_gap_detection_autonomous_confidence_v1/metrics.json:elapsed_s`: FULL = 6.10s
total (all 4 tests). No GPU-batching benefit available.

## Schema-vet declarations

```yaml
sweep_alignment_verdict: ALIGNED           # gate A -- no swept parameter axis (3 fixed scale profiles: self_test/smoke/full)
discriminating_fraction: 1.0               # gate B -- single regime per profile, situated well inside [0.30,0.70] discriminating band per the FLOOR derivation table above
composition_edges:                         # gate C
  - {from: hdlab.gap_detector.content_key, to: hdlab.cleanup_family.iterative_attractor, verdict: SHAPE_MATCH}
  - {from: hdlab.gap_detector.GapDetector, to: hdlab.hd_fact_store.HDFactStore.live_facts, verdict: SHAPE_MATCH}
  - {from: gap_detector-flagged subject list, to: hdlab.gather_reason.fanout_two_hop, verdict: SHAPE_MATCH}
  - {from: hdlab.gather_reason.fanout_two_hop, to: hdlab.three_tier_loop.ThreeTierLoop.encounter, verdict: SHAPE_MATCH}
positive_control_arms: N/A                 # gate D -- this cell introduces the primitive (gap_detector); it does not re-invoke a prior chain-grade primitive under a new name. hdlab.gather_reason/hdlab.three_tier_loop ARE reused verbatim (test 4), matching verification/test_three_tier_loop_e2e.py's own proven 8-encounter/2-consolidate pattern byte-for-byte (see k1=1 note for the one parameter this cell had to choose itself)
functional_requirements: [see table above]  # gate E
real_code_path_exercised: [HDFactStore, iterative_attractor, KGStore, ThreeTierLoop, fanout_two_hop]  # gate F.1
substrate_signature_checked: [HDFactStore(n_dim,seed,relation_cardinality), KGStore(n_ent,n_rel,n_dim,generator), ThreeTierLoop(foundation_store,seed_base,n_dim,relation)]  # gate F.2/F.3, base kwargs only (no init_entities)
guard_baseline_validated: N/A              # gate F.4 -- no control-beats-baseline (POP-vs-RANDOM-shaped) guard in this cell
deterministic_seeding: true                # gate F.5 -- fixed integer seeds throughout; lesion_keys uses a python set ONLY for O(1) membership test (not iteration order), PROT-023-safe
cell_chunked: false                        # single deterministic pass per mode, not a resumable multi-unit sweep
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: false                   # MEASURED wall time 6.10s (FULL), far under the 15-min heartbeat bar; print-progress used instead
defensive_error_checking: "passed_start_marker+crash_diagnostic+no_bare_except; heartbeat exempted (est./measured wall time << 15-min bar)"
progress_logging: "print_flush_true"       # not mandated (elapsed << 1800s) but implemented for auditability
arms_differ_verified: true                 # test 2's real-vs-ablated margin vectors asserted non-identical at runtime (byte comparison)
final_metrics_atomicity: tmp_replace
crlb_n/a: "discrete signal-detection metric (hit/FA/d-prime/AUC), not a Gaussian noise-floor capacity metric; FLOOR derivation table above is the THEORETICAL discriminator_reachability analysis"
baseline_in_band: "N/A -- signal-detection cell; trivial baseline = chance AUC 0.5, reported explicitly as auc_vs_chance_baseline_0.5 in every stats block"
calibration_check: "default_ok_for_this_regime -- FLOOR=0.625 is THEORETICAL (bipolar bind/quantize algebra, see table above), not tuned on the graded probes; cross-checked empirically by hdlab/gap_detector.py's own formula self-tests before this cell was authored"
cardinality_ok: true                       # EXPECTED_N_UNITS = 4 gated tests + 1 honest secondary + 1 multi-seed variance probe (smoke only); verified present in every metrics.json
```

## Modes

`--self-test`: tiny fixture (18 facts, 6/6/3/3 probes, n_dim=1024, 6-subject e2e world),
real `HDFactStore`/`iterative_attractor`/`KGStore`/`ThreeTierLoop` objects, <0.2s.
MEASURED@`data/exp_gap_detection_autonomous_confidence_v1_selftest/metrics.json`: MIDDLE_BAND
(test1/test3/test4 HARD_PASS; test2 MIDDLE_BAND -- ablated AUC=0.25 at n=6 vs n=6 is a plausible
chance fluctuation, standard error ~0.127 at this tiny N; self-test's job is real-code-path
exercise per SCHEMA-VET F.1, not clearing production bands).

`--smoke`: 3-seed variance probe (Skunkworks META CG multi-seed-smoke rule for
confidence/AUC-shaped discriminators) on test 1 at reduced scale (60 facts, 20/20/15/10 probes,
n_dim=2048) BEFORE trusting a single-seed FULL run, plus one full pass of all 4 tests at smoke
scale. MEASURED@`data/exp_gap_detection_autonomous_confidence_v1_smoke/metrics.json`:
`auc_min=auc_max=1.0` across seeds 20260811001/002/003 (`auc_stable=true`); overall verdict
HARD_PASS.

(no flag) FULL: 240 facts, 100/100/60/40 probes, n_dim=4096, 10-subject e2e world.
MEASURED@`data/exp_gap_detection_autonomous_confidence_v1/metrics.json`: HARD_PASS on all 4
gated tests -- `t1: auc=1.0, d_prime=5.15, hit=1.0, FA=0.0`; `t1b (honest, non-gating):
auc=1.0, d_prime=4.97, novel_margin_mean=0.502` (matches the ~0.5 theoretical prediction almost
exactly); `t2: delta_auc=0.520, ablated_auc=0.480` (collapses to chance); `t3: flip_rate=1.0`
(all 40 lesioned facts flip known->gap); `t4: detection_recall=1.0, false_positives=0,
reasoning_accuracy=1.0, resolution_accuracy=1.0` (after the `k1=1` fix). No `--timeout` needed
(inline foreground, MEASURED elapsed_s: self_test=0.07s, smoke=0.81s, full=6.10s).

## Verification
`verification/test_gap_detector.py` (new, scaffold-free witness, 4 tests, all PASS):
signal-detection zero-false-alarm/all-novel-flagged, not-a-lookup ablation collapse,
scramble-flips-known-to-gap, empty-KB edge case. `python -m pytest verification/ -q`: 260
passed, 3 skipped in 70.78s (full suite, including the new file and the pre-existing
`test_three_tier_loop_e2e.py` -- no regression on any reused organ).
