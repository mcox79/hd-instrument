# PRE-REGISTRATION -- exp_information_foraging_reading_v1

**Filed 2026-08-14, BEFORE any smoke or full run of this cell.**
Cell: `D:/AI/hd-instrument/experiments/exp_information_foraging_reading_v1.py`
Organs under test: `D:/AI/hd-instrument/hdlab/information_foraging.py`,
`D:/AI/hd-instrument/hdlab/corpus_registry.py` (both landed at commit `c97ecbef2`).

---

## 1. The question, in plain language

The reading loop can notice a word it does not understand. It cannot decide what to read next. It
was never able to: the list of readable material was a four-entry Python dict while
`data/corpora/` held thirty-six entries, so Simple Wikipedia sitting on disk since 2026-07-28 was
not a choice the substrate declined to make -- it was not an option the substrate could represent
(`notes/gap_driven_learning_loop_audit_2026-08-13.md`).

**Does letting it choose for itself produce better knowledge than choosing at random over the same
shelf, or than the frozen four-entry schedule?**

## 2. What is already refuted, and why this design is not that

Three routes are closed and this cell must not reduce to any of them:

- **More facts do not help** -- `exp_wire_definitional_v1`: SHUFFLED wrong definitions scored
  identically to correct ones to 6 dp on held-out recall.
- **Better text does not help** -- matched-N prereg: textbook 0% MEANINGFUL vs news 4%.
- **Coverage alone does not help** -- differentia supply moved coverage 2.9% -> 35.0% and stayed
  at chance.

This cell's claim is none of those. It is that a **DECISION ORGAN** is missing, that its absence is
measurable as a 63.9% single-source skew, and that supplying the organ changes WHICH text is read
and therefore the BALANCE and the BLIND QUALITY of what gets banked. If the result reduces to
"read more" or "read better text", it is refuted already and will be reported as such.

## 3. What is measured on disk BEFORE the run (Stage A, retrospective)

`python tools/segment_skew_report.py`, run 2026-08-14 against
`data/foundation/reading_grounding_v5_termboundary/definitional_facts_v5.jsonl`:

| version | distinct terms | dominant segment | share | normalised entropy |
|---|---|---|---|---|
| v3_definitional | 1316 | `bio_new` | 0.546 | 0.804 |
| v4_parsefix | 1698 | `bio_new` | 0.632 | 0.715 |
| **v5_termboundary** | **1734** | **`bio_new`** | **0.639** | **0.707** |

MEASURED@`data/foundation/reading_grounding_v5_termboundary/definitional_facts_v5.jsonl`
(first-segment-wins dedupe on `subject`; 1108/1734). The audit's 64.5% is the same quantity under
a slightly different dedupe convention. **The skew is getting WORSE as the extractor improves** --
a better extractor extracts more from whichever source it is already pointed at.

## 4. Arms

Identical in every respect except the reading POLICY: same seed lexicon (base_vocabulary top-1000),
same encoder, `n_dim=2048`, `chunk=150`, `schema_thresh=0.25`, same total sentence budget, same
substrate seed, a FRESH `HDFactStore` per arm. **The canonical fact store is never opened and never
written** -- growth stays paused.

| arm | corpus choice | patch leaving | role |
|---|---|---|---|
| `FORAGE` | gap-ranked over 28 readable corpora | MVT (Charnov / Constantino & Daw) | treatment |
| `RANDOM` | uniform random over the SAME 28 | MVT | **FLOOR 1 (mandatory)** |
| `FROZEN` | the historical 4 sources, fixed order, equal budget | fixed schedule | **FLOOR 2 (mandatory)** |
| `FIXED_LEAVE` | gap-ranked | FIXED 40-step residence | isolates the leave rule from the choice |

`FROZEN`'s four sources reproduce `SEGMENT_POOL_LOADERS` source-for-source: OneStopEnglish
Ele-Txt / Int-Txt / Adv-Txt plus `textbook_concepts_biology`.

## 5. Currency: uncertainty reduction per unit effort, NOT items

Gain of one harvest step (one sentence) = the summed **posterior-mean shift** of the substrate's
own model over that sentence's content lemmas, read at **two loci**:

- `ConceptSpace._sums[lemma]` -- words already known or grounded;
- `Library.items[lemma].traces` -- words still PENDING, i.e. exactly what the loop is trying to
  learn. (The first draft measured only the first locus and a sentence of entirely-unknown words
  scored 0.0. Caught in the cell self-test before any run.)

`|| S/(n+1) - S/n || / sqrt(d)`; a first encounter contributes the full unit vector. Monotone in
Bayesian surprise for a fixed-variance Gaussian-mean model; decays ~1/n, which supplies the
within-patch depletion curve for free.

**DECLARED LIMITATION.** This is Bayesian SURPRISE, not Oudeyer LEARNING PROGRESS (the derivative
of prediction error). Surprise alone cannot separate learnable novelty from unlearnable noise, so a
novelty trap is a live risk. `learning_progress_first_half_minus_second` is recorded so the two can
be compared post hoc. **A forager that camps on the highest-novelty corpus and grounds WORSE is a
real reportable negative, not a bug to be patched away.**

## 6. Discriminators and bands (RANGE BY CONSTRUCTION; no hand-scored MEANINGFUL anywhere)

| id | quantity | PASS band | FAIL band |
|---|---|---|---|
| **D1** | `FROZEN.dominant_source_share - FORAGE.dominant_source_share` | `>= 0.15` | `< 0.15` |
| **D2** | relative gain in held-out everyday-vocab coverage, FORAGE vs RANDOM | `>= +0.10` | `< +0.10` |
| **D3** | blind WordNet agreement of banked pairs, FORAGE vs FROZEN | `delta >= -0.05` (non-inferiority) | `delta < -0.05` |
| **D4** | FORAGE achieved gain-rate / post-hoc oracle MVT rate | `0.70 <= r < 1.00` | outside |

Overall: 3/3 core (D1,D2,D3) = HARD_PASS; 0/3 = HARD_FAIL; else MIDDLE_BAND.

**Range by construction.** D1: `FROZEN` has 4 sources so its dominant share is bounded below by
0.25; `FORAGE` has 28 so its floor is 0.036. **Declared openly: FORAGE is advantaged on D1 partly
BY CONSTRUCTION -- that is what the shelf IS, and D1 measures the shelf, not the foraging.** D2 is
the honest test of foraging, because both arms choose over identical options. D3 is the honest
test of grounding quality.

**Held-out probe** = `base_vocabulary_ordered.csv` ranks 1001..4000, disjoint from the seed
lexicon (ranks 1..1000) and never visible to any arm's decisions.

**Blind quality metric.** A banked `(subject, object)` pair counts as RELATED when the two share a
WordNet synset, one lies in the other's hypernym closure, or their max Wu-Palmer similarity is
`>= 0.5`. Mechanical, not hand-scored (the hand-scored MEANINGFUL read-out sits at 1-3% and made
two cells undecidable this week). **Disclosure: the loop's lemmatiser normalises surface forms, but
no WordNet SEMANTIC relation is consulted anywhere in any arm's decision path.**

**D4 is OBJECTIVE-ALIGNED for FORAGE** (FORAGE optimises the gain rate directly) and is therefore
a MECHANISM check, not a capability claim. An oracle ratio of exactly 1.00 means the post-hoc
oracle leaked into the online policy; 0.85-0.95 is the brain-matched band.

## 7. Mechanism-fired gates (META_RULE_K). Any failure = HARD_FAIL_DISCRIMINATOR_DID_NOT_FIRE

- `gain_distinct_values > 50` (the currency is a value, not a count)
- `n_travel_updates > 0` (rho was updated during travel with r=0)
- `n_patches >= 5`
- `FORAGE.n_distinct_corpora_read >= 3`
- `ranked_choice_frac > 0.10` -- if the gap-ranked selector always falls back to a random draw
  then FORAGE IS RANDOM by construction and the comparison is vacuous
- **META_RULE_AG baseline in band:** `0.05 < FROZEN.dominant_source_share < 0.99`

## 8. The ten silent-failure modes, and where each is checked

| # | failure mode | check |
|---|---|---|
| 1 | travel omitted from rho's denominator | `_selftest_1_travel_time_is_in_the_denominator` |
| 2 | rho not updated during travel with r=0 | `_selftest_2...`; runtime gate `n_travel_updates > 0` |
| 3 | thresholding LAST gain not EXPECTED next | `_selftest_3...` (kappa must be learned and load-bearing) |
| 4 | untimed delta rule | `_selftest_4_timed_delta_rule_is_exact` (exact equality) |
| 5 | fixed threshold | `_selftest_5_threshold_is_not_fixed`; witness `test_leave_threshold_moves_with_travel_time` |
| 6 | counting items | `assert_gain_is_not_a_count` + runtime `gain_distinct_values` gate |
| 7 | hand-coded overstaying bias | `_selftest_7...` scans `should_leave`'s own source |
| 8 | single rho timescale | `rho_fast`/`rho_slow` both tracked; `_selftest_8...` |
| 9 | document = patch | `SurpriseSegmenter`; `_selftest_9_a_document_is_not_a_patch` |
| 10 | citing dACC as a warrant | `DESIGN_WARRANTS` has no dACC row; `_selftest_10...` |

All fourteen pass at commit `c97ecbef2`.

## 9. SCHEMA-VET fields

```yaml
cardinality_ok: true                  # EXPECTED_N_UNITS = 4 arms; verdict counts len(per_unit)
arms_differ_verified: true            # sha256 over each arm's read-sentence stream
final_metrics_atomicity: tmp_replace
baseline_in_band: true                # gated at runtime on FROZEN dominant_source_share
calibration_check: default_ok_for_this_regime   # schema_thresh 0.25 = cycle-1's calibrated value
crlb_n/a: "no quantitative noise floor applies; D1 reachability argued from construction (1/28 vs 1/4)"
discriminator_reachability: true
sweep_alignment_verdict: ALIGNED      # no swept parameter; policy is the only manipulated variable
discriminating_fraction: 1.0          # the single manipulated variable is the policy itself
composition_edges:
  - {from: corpus_registry.CorpusHandle, to: reading_grounding_loop.process_sentence,
     A_natural_output_shape: "List[str] sentences", B_natural_input_shape: "str sentence",
     verdict: SHAPE_MATCH}
  - {from: gap_driven_reader.next_read_target, to: gap_driven_reader.rank_material,
     A_natural_output_shape: "target lemma str", B_natural_input_shape: "target lemma str + docs",
     verdict: SHAPE_MATCH}
  - {from: UncertaintyMeter.score, to: information_foraging.ForagingController.harvest,
     A_natural_output_shape: "float gain", B_natural_input_shape: "float gain",
     verdict: SHAPE_MATCH}
positive_control_arms:
  - arm: FROZEN
    primitive: the historical 4-entry reading schedule
    cited_prior_artifact: data/foundation/reading_grounding_v5_termboundary/definitional_facts_v5.jsonl
    cited_prior_metric: 0.639           # dominant_source_share, bio_new
    if_outside_tolerance: "report; FROZEN here reads a smaller budget from a fresh store, so an
                           exact reproduction of 0.639 is NOT expected -- the DIRECTION (bio
                           dominant, entropy well below 1.0) is what must reproduce"
functional_requirements:
  - "represent the set of readable material"       -> hdlab.corpus_registry (NEW; nothing supplied it)
  - "name the specific concept a blocked word needs" -> gap_driven_reader.next_read_target (exists, HARD_PASS)
  - "score candidate material for that concept"    -> gap_driven_reader.rank_material (exists, HARD_PASS)
  - "decide when the current source is exhausted"  -> hdlab.information_foraging (NEW; ORGAN_MAP: MISSING)
  - "measure uncertainty reduction"                -> UncertaintyMeter (cell-local observer, writes nothing)
real_code_path_exercised: [CorpusRegistry, ReadingLoopState, checkpoint, read_and_track,
                           choose_gap_ranked, frozen_shelf, wordnet_scorer]
substrate_signature_checked: [HDFactStore, checkpoint, rank_material]
guard_baseline_validated: [baseline_in_band_META_RULE_AG]
deterministic_seeding: true           # AST scan in self_test: no built-in hash(), no set-order dedupe
cell_chunked: false                   # single seed; per-ARM resume via tools/exp_checkpoint
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: true
defensive_error_checking: passed_all_4_patterns
progress_logging: line_buffered_stdout
progress_cadence_expected_s: 60
compute_architecture: sequential-CPU with justification
```

**Compute architecture justification.** Genuinely sequential: every sentence's gain depends on the
model state left by the previous sentence, and the leave decision depends on the gain. There is no
independent phase-point grid to batch. Measured throughput
MEASURED@`scratch/probe_yield.py` 2026-08-14: 2400 sentences in 63 s. GPU batching buys nothing
here.

## 10. Storage strategy

`no_composition` -- this cell stores facts in an `HDFactStore` with `use_index=True` (sharded by
construction, one fact per row) and performs no bundled multi-hop composition. The sharded-storage
default is satisfied trivially.

## 11. What would make me abandon the route

- `ranked_choice_frac` near 0 -> the gap-ranked selector has no signal on real corpora and FORAGE
  is RANDOM wearing a costume. Report as such; do not tune the ranker to rescue the arm.
- D2 negative with D1 positive -> the SHELF is the whole effect and FORAGING adds nothing. That is
  a genuine, publishable-internally negative and it is the single most likely outcome.
- FORAGE concentrates on one high-novelty corpus and grounds worse -> the novelty trap in section 5
  fired; the fix is learning progress, not a bias term.

---

# AMENDMENT 1 -- 2026-08-14, filed AFTER the smoke gate and BEFORE any full run

Two changes. The superseded prediction is **retained and still scored**, per the amendment
discipline recorded in `notes/ORGAN_MAP.md` sec 3 correction 1. **No PASS/FAIL band in section 6
is altered.** The smoke's own numbers are recorded below so that what was known at amendment time
is on the record.

## 12.1 What the smoke measured (900 sentences/arm, `data/exp_information_foraging_reading_v1_smoke/metrics.json`)

| arm | grounded | corpora read | banked from | dominant share | held-out cov | WordNet agr |
|---|---|---|---|---|---|---|
| FORAGE | 64 | 8 | 4 | 0.594 | 0.0093 | 0.267 |
| RANDOM | 25 | 8 | 3 | 0.720 | 0.0033 | 0.591 |
| FROZEN | 265 | 4 | 3 | 0.381 | 0.0410 | 0.367 |
| FIXED_LEAVE | 126 | 9 | 3 | 0.603 | 0.0190 | 0.279 |

Verdict MIDDLE_BAND. **D2 passed (+180% over RANDOM). D1 failed and in the WRONG DIRECTION**
(FORAGE concentrated MORE than FROZEN). **FROZEN grounded 4x what FORAGE grounded.**

## 12.2 BUG FIXED (not a band change): the oracle was not an upper bound

All four arms reported an oracle ratio ABOVE 1.0 (1.92 / 1.78 / 1.47 / 1.11). An online policy
cannot beat a post-hoc oracle, so the oracle was wrong. Root cause: `oracle_mvt_optimum`
implemented Charnov's FIRST-CROSSING stopping rule, which is optimal only for MONOTONE DECREASING
gain. Real per-sentence gains are noisy, so first-crossing stops at the first dip and discards
every later peak -- a WORSE policy than harvesting everything, not a bound on the best one.
Replaced with the Dinkelbach fractional-programming form: each patch takes the residence
maximising `cumsum(n) - rho*h*n`, rho driven to its fixed point, which makes `G/T <= rho*` for
every feasible policy. Regression test `_selftest_oracle_is_a_true_upper_bound_on_noisy_gains`
asserts the corrected oracle dominates seven fixed-residence policies AND "harvest everything" on
noisy sequences; the old version fails it by ~1.9x.

## 12.3 AMENDMENT: a fifth arm, `FORAGE_REFUSAL`

The smoke shows what the pre-registered primary-selection rule actually selects on real corpora.
`example_ranked_choices` for FORAGE: target `bbm`, target `blackberry`, target `page`, `page`,
`page`. The rule was "the most-attempted still-PENDING Library item", and on real text
"most-attempted" is very nearly a frequency ranking, so it surfaces high-frequency nouns that are
barely knowledge gaps.

`FORAGE_REFUSAL` is identical to `FORAGE` except that the primary blocked concept is the
**most-REFUSED lemma that is still not banked**. A refusal means the item reached the consolidation
gate and FAILED there -- a far stronger signal of a genuinely blocked concept than raw exposure.
This also makes the refusal ledger drive a DECISION for the first time, which is precisely what
`notes/gap_driven_learning_loop_audit_2026-08-13.md` sec 5 found nothing on disk does: 11,122 rows
written, counted, reloaded, and never consulted by any branch.

`FORAGE` (the superseded rule) remains in the arm list and remains the arm scored against D1-D4.
`FORAGE_REFUSAL` is reported alongside and is explicitly EXPLORATORY: it was designed after seeing
smoke numbers and its result carries that discount.

## 12.4 ADDED INSTRUMENTATION (no band changes)

FROZEN grounded 265 against FORAGE's 64 on an identical budget. The obvious candidate mechanism is
**exposure fragmentation**: grounding requires `MIN_CONFIRM = 4` coherent encounters of the SAME
lemma, and a forager that hops sources may never accumulate them. That is a testable claim, so it
is now measured rather than argued: `exposure.{mean_traces_per_item, median_traces_per_item,
max_traces, n_items_at_min_confirm, frac_items_at_min_confirm}` per arm. `heldout_precision`
(held-out hits per banked fact) is added alongside `heldout_coverage` so volume and everyday-ness
can be separated.

**Prediction, recorded now:** if exposure fragmentation is the mechanism, FORAGE's
`frac_items_at_min_confirm` will be materially below FROZEN's. If it is NOT, the grounding deficit
has some other cause and I should not claim fragmentation.

## 12.5 Budget

`FULL_BUDGET` 12000 -> 10000 sentences per arm, because the arm count went 4 -> 5. Total sentences
read across the experiment is unchanged to within 4%.
