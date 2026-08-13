# PRE-REGISTRATION -- exp_grounding_quality_readout_v1 (2026-08-12)

**Filed BEFORE any measurement on this cell.** Author: hdi_exp_dev. Cell:
`experiments/exp_grounding_quality_readout_v1.py`. Substrate: `hdlab/reading_grounding_loop.py`.

## 0. THE QUESTION

**Does a stabler read-out produce BETTER MEANINGS?**

Everything measured in `exp_readout_fix_v1` is argmax STABILITY (flip rate, admission, confirm
rate). The landed-VET (`notes/landed_vet_readout_fix_v1_2026-08-12.md`) states the scope limit
explicitly: "NOT licensed: any statement about grounding quality/correctness." A read-out that
agrees with itself is not a read-out that is RIGHT. This cell produces the material for the only
instrument that can answer the quality question -- a human hand-score -- and **claims no quality
band itself**.

## 1. AUTHORITY / OPERATING CONFIG (not re-litigated here)

`notes/landed_vet_readout_fix_v1_2026-08-12.md` (8de3a9a20) OVERTURNS parts of
`notes/readout_fix_v1_2026-08-12.md`. Dispositions taken as given:

| fix | disposition | this cell |
|---|---|---|
| F3 `ConceptSpace.freeze` / episode freeze | **CONFIRMED** (survives matched retention, retention pushed above baseline, moves `flip_all`, survives the field-SIZE control) | **ON** in the mechanism arm |
| F2 `anchor_center` / `anchor_scale` | **REFUTED -- SHELVED** (its LOO was a retention artifact; at matched retention -0.004 FIXED, **+0.032 = it HURTS** in GROWING) | **OFF everywhere**, guarded by a self-test |
| F1 field-relative z gate | keep as a **stability selector only** (worth -0.048 at equal retention); REFUTED as an informativeness / lemma-specificity gate (AUC 0.5067, enrichment 1.0000x) | **ON** in the mechanism arm, at the retention-matched operating point |

Operating config = **F1 + F3, F2 OFF**, wired as
`hdlab.reading_grounding_loop.operating_readout()` + `make_pbv_fns(..., freeze_episode=True)`.
**Defaults OFF**: every pre-existing caller passes `readout=None` / `freeze_episode=False` and
takes the prior code path byte-for-byte.

F1 threshold `margin_z_min = 3.542496`
MEASURED@`data/exp_readout_fix_v1/metrics.json:fix1.thresholds["grow_epi|f2=0|z_top"].g_match`.
Chosen because it is the z_top threshold **retention-matched** to the legacy `cos >= 0.30` gate in
this cell's regime (grow_epi = growing space + episode freeze, F2 off). Retention-matched is
deliberate: it is the only operating point at which a quality delta is not silently confounded with
admitting fewer encounters, which is the exact defect that made F2 look load-bearing.

## 2. DESIGN

Two arms, same corpus, same seeds, same everything except the read-out.

| arm | readout | freeze | role |
|---|---|---|---|
| `PBV_BASE` | None | off | BASELINE **and** the positive control for the 0.101 gate (sec 5) |
| `PBV_F1F3` | `operating_readout()` | on | mechanism |

**Corpus** = `experiments.exp_definitional_grounding_v5.load_corpus_v5(None, lineaware=True)`,
34169 sentences, 5 segments (bootstrap 4640 / ele_cont 4623 / int_cont 4952 / adv_new 7408 /
bio_new 12546) -- the SAME corpus the 64% hand-scored v5 baseline was built on
(`notes/director_handscore_b3_v5_termboundary_2026-08-12.md`).

**Reference points for the later hand-score** (all CITED@ that note's table, same judge, same
rubric, same seed-42 sampling):

| arm | mechanism | MEANINGFUL | n facts |
|---|---|---|---|
| v2 DIST | distributional read-out, no PBV, no read-out fixes | **8%** | 634 |
| v5 DEF | surface definitional PARSER (a different mechanism entirely) | **64%** | 2092 |

The 64% is a **CEILING REFERENCE, NOT THE COMPARATOR.** It was produced by a hand-written
appositive/copula parser, not by a read-out. The read-out's own prior quality number is the
**8%**. Any framing that scores this cell against 64% is comparing two mechanisms and is refused
in advance.

## 3. BANDS -- PRIMARY (quality; scored later by the director, NOT by this cell)

Discriminator = **MEANINGFUL(PBV_F1F3) - MEANINGFUL(PBV_BASE)**, two 50-row samples from the same
corpus, same rubric, same judge, scored in one sitting, blind-shuffled.

**POWER, stated before the bands so the bands are honest.** Two independent n=50 samples give
SE(delta) ~ sqrt(2 * 0.25 / 50) = 0.10 at p ~ 0.5. **This design cannot resolve a delta below
~0.20 at 2 SE.** The bands below respect that; anything finer is pre-declared unresolvable rather
than reported as a result.

| band | criterion | meaning |
|---|---|---|
| **HARD_PASS** | delta >= **+0.20** AND F1F3 MEANINGFUL >= **0.25** | a stabler read-out DOES produce better meanings; stability was a binding constraint on quality |
| **MIDDLE_BAND** | delta in **[+0.08, +0.20)** | directionally positive but UNDER-POWERED at n=50; licenses only a larger re-score, never a claim |
| **NULL (see sec 3.1)** | \|delta\| < **0.08** | **a stabler read-out does NOT produce better meanings** |
| **HARD_FAIL_HURTS** | delta <= **-0.08** | F1+F3 makes meanings WORSE -- the z-gate is selecting generic-context encounters |

### 3.1 THE NULL OUTCOME IS LIVE AND ACCEPTABLE -- stated as an outcome, not a hedge

If |delta| < 0.08, the pre-registered reading is:

> **Read-out stability and meaning quality are DECOUPLED.** F1+F3 demonstrably reduce argmax flip
> (landed-VET, chain-grade) and demonstrably do not buy meaning. The read-out was therefore NOT the
> binding constraint on grounding quality; the 8% floor is set somewhere else -- most likely in the
> PROPOSER'S METRIC (distributional relatedness is not reference; the PBV cell's own limitation #2),
> not in the stability of reading it. Correct disposition: keep F1+F3 as a stability knob, default
> OFF, and stop spending on read-out stability as a quality route.

This is a **fully acceptable and genuinely expected** result. It is the outcome I would bet on: the
landed-VET's own most durable finding is that F1 is blind to whether the context belongs to the
lemma (enrichment 1.0000x), and nothing in F3 supplies reference either. A NULL here is a route
CLOSED cleanly, which is worth more than an under-powered positive. **No part of this cell is
tuned, framed, or sized to avoid the NULL.**

### 3.2 SELECTIVITY CONFOUND -- a can-fail interpretive cap

Higher quality on a smaller, easier survivor set is not higher quality. **If
`n_facts(F1F3) / n_facts(BASE)` falls outside [0.5, 2.0], the quality delta is CONFOUNDED WITH
SELECTIVITY and the verdict is CAPPED AT MIDDLE_BAND regardless of its size.** The cell computes
and reports this ratio plus the shared-lemma overlap so the cap is machine-checkable, not a
judgement call made after seeing the delta.

## 4. BANDS -- STRUCTURAL (machine-checked, this cell's own verdict)

The cell's verdict is `STRUCTURAL_PASS_PENDING_B3` at best. It never emits a quality tier.

| id | gate | HARD_FAIL if |
|---|---|---|
| S1 | cardinality: 2 arms x 5 segments = **EXPECTED_N_UNITS = 10** | any unit missing |
| S2 | integrity per arm: 0 tautology facts, 0 closed-class objects, 0 seed-leak violations | any > 0 |
| S3 | ARMS-MUST-DIFFER (META_RULE_AF): sha256 over each arm's sorted (subject, object) set | digests equal |
| S4 | backward-compat: `data/foundation/reading_grounding_v1` and `reading_grounding_v2_qualityfix` load unchanged; `readout=None` path bit-identical | either fails |
| S5 | **calibration / positive control** (sec 5) | -- (demotes the 0.101 claim, does not fail the cell) |
| S6 | yield floor: each arm banks >= 50 GROUNDED_MEANING facts | either < 50 (a 50-row sample would not be a sample) |
| S7 | F3 memory: peak live snapshot bytes reported; cap 4 GB | over cap |
| S8 | F1 admission drift: measured admission rate vs the 0.403405 the threshold was matched at | -- (reported; drift > 0.10 voids the "retention-matched" claim, sec 3.2 cap then applies) |

**`baseline_in_band` (META_RULE_AG):** the discriminating quantity is a hand-scored proportion with
a 0.08 baseline (v2 DIST) and a 0.64 ceiling reference -- 0.05 < 0.08 < 0.95, in band, and there is
a measured 0.56 of headroom. Not saturated in either direction.

**`crlb_n/a`:** the discriminator is a human-bucketed proportion over a finite sample, not an
estimator against a noise floor. The binding limit is BINOMIAL, and it is stated in sec 3 (SE 0.10
at n=50) and enforced by the 0.20 HARD_PASS band rather than left implicit.

## 5. SECONDARY -- confirm rate vs PBV's 0.101 gate, CALIBRATED IN PBV'S OWN REGIME

The prior projection was **UNCALIBRATED and licensed nothing**: `exp_readout_fix_v1` projected
0.4881 against an observed 0.1006 and demoted itself (`projection_calibrated=false`). Root cause:
it re-scored CACHED encounters against a 5-snapshot space, while PBV ran a LIVE space that grew at
every encounter.

**PBV's gate, re-derived from disk, not quoted:**
MEASURED@`data/exp_pbv_hypothesis_v1_smoke/metrics.json:arms.B_PBV.trajectory` -->
`n_confirm = 788`, `n_disconfirm = 7048`, so
**confirm rate = 788 / (788 + 7048) = 788/7836 = 0.100561**. It is the share of VERDICT-BEARING
encounters that CONFIRM the standing hypothesis. Uninformative encounters are excluded by
construction (they emit no verdict).

This cell computes that identical quantity **in PBV's own regime** -- a live per-encounter space,
the same PBV wiring, the same `PBV_INFORMATIVE_MIN = 0.30`, the same `PBV_COMMIT_STRENGTH = 0.6` --
because it IS a live reading pass, not a re-score of a cache. Calibration is therefore not
asserted, it is **positive-controlled**:

* **S5 gate.** `PBV_BASE`'s confirm rate must land within **0.05** of 0.100561 (i.e. in
  [0.0506, 0.1506]). PBV's own run used a 7500-sentence subsample of these segments and this run
  uses all 34169, so exact reproduction is not expected and is not required -- but a BASE arm far
  outside this window means the regime did not reproduce.
* **If S5 PASSES:** `PBV_F1F3`'s confirm rate is reported against the 0.101 gate and the comparison
  is licensed.
* **If S5 FAILS:** every confirm-rate number in this cell is marked `WITHIN_CELL_RELATIVE_ONLY`,
  `confirm_rate_calibrated = false`, and **no claim is made against the 0.101 gate** -- exactly the
  demotion the prior cell correctly applied to itself. This gate is written to be able to fail and
  the cell is not re-run to make it pass.

Directional note recorded in advance so it cannot be invented afterwards: F1 is a GATE, so it
changes WHICH encounters are informative. A confirm-rate rise under F1F3 is expected on stability
grounds alone (the landed-VET measured F1 as a real stability selector) and is **not** evidence of
better meanings. Only the hand-score speaks to meaning.

## 6. WHAT THIS CELL FIXES IN THE SUBSTRATE (declared, because it is a real deviation)

**F3 as shipped cannot run a live pass. MEASURED, here, before this cell was written.** Instrumented
live pass over the v5 corpus with `freeze_episode=True`:

| sentences | live FrozenAnchorSpace snapshots | distinct matrices | bytes |
|---|---|---|---|
| 500 | 1110 | 1110 | 0.65 GB |
| 1000 | 1768 | 1768 | 1.39 GB |
| 2000 | 3228 | 3228 | 3.40 GB |
| 3000 | 4518 | 4518 | **5.35 GB** |

3000 of 34169 sentences, linear in episodes, zero sharing (ConceptSpace `_version` bumps on every
observed seed-word occurrence, so no two episodes are ever proposed at the same version).
Extrapolates past 50 GB. This is precisely the landed-VET's caveat -- "self-tested but not
exercised in a live reading pass" -- turning out to be load-bearing.

**Fix:** `make_pbv_fns(..., freeze_epoch_fn=...)`, additive, default None = prior semantics
byte-for-byte. Episodes proposed in one EPOCH share one refcounted snapshot; memory becomes
O(live epochs). This cell passes the chunk index, i.e. one snapshot per 150 sentences.

**This is a DECLARED COARSENING, not a free lunch.** An episode proposed mid-epoch is frozen
against the field as it stood at the START of its epoch. It is coarser than true per-episode freeze
-- and strictly FINER than the 5-snapshot (per-SEGMENT) granularity at which F3's confirmed -0.168
was actually measured. So it interpolates between the measured point and the unrunnable ideal
rather than extrapolating past either. Reported as `freeze_stats()` telemetry in metrics, not as a
comment.

## 7. DELIVERABLE

`data/exp_grounding_quality_readout_v1/b3_audit_sample_READOUT_F1F3.json` -- **UNSCORED**, 50 rows,
`random.Random(42).sample` over fid order, envelope and row-field set identical to
`data/exp_definitional_grounding_v5/b3_audit_sample_DEF_V5.json` (fields with no analogue in a
distributional read-out -- `pmi`, `definiendum_surface`, `definiens_surface` -- are present and
`null`, never fabricated). `scored: false`. **The cell assigns no buckets and claims no quality
band.** Plus the same for `PBV_BASE`, plus a blind-shuffled 100-row file and its key, so the
director can score both arms without knowing which is which.

## 8. BANDS THAT COULD NOT FAIL -- named and removed before the run

1. **"F1F3 has a lower flip rate than BASE."** Chain-grade already (landed-VET) and not this
   cell's question. NOT a band here; measured only as a wiring check.
2. **"F1F3 quality > v5 DEF's 64%."** Cross-mechanism; a parser vs a read-out. Refused in advance
   (sec 2).
3. **"the sample is drawable / the cell runs."** A harness gate that can only BLOCK. Zero verdict
   weight; folded into S1/S6.
4. **"F1F3 banks fewer facts, so it is more selective, so it is better."** This is the exact shape
   of the confound that made F2 look load-bearing. Inverted into the failable CAP at sec 3.2.
5. **"confirm rate rose, so meanings improved."** Explicitly refused in sec 5.

## 9. COMPUTE ARCHITECTURE

`(b) sequential-CPU with justification`: the reading loop is irreducibly sequential -- each
encounter's proposal is scored against a ConceptSpace that the PREVIOUS encounter mutated, and the
PBV hypothesis is carried across encounters in order. This is a genuine step-N-depends-on-step-N-1
chain, the sanctioned exemption. The inner anchor scan is already one matvec
(`canonicalize_fast`). Storage strategy: `no_composition` (facts are stored per-subject in
`HDFactStore`, never bundled).

## 10. CELL-TEMPLATE / SCHEMA-VET FIELDS

```yaml
cardinality_ok: true              # EXPECTED_N_UNITS = 10 (2 arms x 5 segments)
cell_chunked: false               # no seed axis; 2 arms, resumable per (arm, segment) unit
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: true
progress_logging: print_flush_true    # MANDATORY: timeout_s >= 1800 (sec 11)
defensive_error_checking: passed_all_4_patterns
final_metrics_atomicity: tmp_replace
arms_differ_verified: true        # S3, sha256 over each arm's sorted (subject, object) set
baseline_in_band: true            # 0.05 < 0.08 (v2 DIST hand-score) < 0.95, 0.56 headroom
calibration_check: default_ok_for_this_regime   # F1 threshold MEASURED@readout_fix_v1, NOT tuned
                                                # here; drift from its matched retention is
                                                # REPORTED (S8), never re-fitted
crlb_n/a: "human-bucketed proportion, not an estimator against a noise floor; the binding limit
           is binomial and is enforced by the 0.20 HARD_PASS band (sec 3)"
discriminator_reachability: true  # 8% -> 64% observed range on this corpus; the 0.28 HARD_PASS
                                  # level sits inside a demonstrated range, not past a ceiling
deterministic_seeding: true       # fixed ints + sorted(set()); no hash(), no list(set())
sweep_alignment_verdict: ALIGNED  # no sweep axis
positive_control_arms:
  - arm: PBV_BASE
    primitive: PBV live reading loop (make_pbv_fns, readout=None)
    cited_prior_metric: 0.100561  # MEASURED@data/exp_pbv_hypothesis_v1_smoke/metrics.json
    tolerance: 0.05
    if_outside_tolerance: confirm_rate_calibrated=false; NO claim against the 0.101 gate
real_code_path_exercised: [HDFactStore, ReadingLoopState, seed_known_words, make_pbv_fns,
                           operating_readout, process_sentence, checkpoint, save_foundation,
                           load_foundation]
substrate_signature_checked: [make_pbv_fns, operating_readout, checkpoint, canonicalize_fast]
guard_baseline_validated: [S5_confirm_rate_calibration]   # gate compared against PBV's MEASURED
                                                          # 0.1006, not against a structural floor
```

## 11. DISPATCH

`local_cpu_queue` is SMOKE-ONLY (USER-locked). The FULL is a **detached local run** on explicit
director instruction (`Start-Process -WindowStyle Hidden -RedirectStandardOutput <log> -PassThru`,
PID written to a file), which overrides the standing inline-local mandate for this task. Estimated
wall time from the instrumented probe: ~90 s per 2000 sentences at 680 anchors, superlinear in
anchors -> **60-150 min per arm, 2-5 h total**. `timeout_s = 21600`. Per-unit resumable via
`tools/exp_checkpoint.py`; heartbeat every 30 s; `flush=True` on every progress line.
