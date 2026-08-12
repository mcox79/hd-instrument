# PRE-REG -- definitional grounding as a SECOND grounding signal (v3)

Anchor: `definitional_grounding_v3`
Cell: `experiments/exp_definitional_grounding_v3.py`
Author: exp_dev, 2026-08-12. **Written and committed BEFORE the run.**
Output foundation (NEW dir; the v1 and v2 evidence stores are READ-ONLY and untouched):
`data/foundation/reading_grounding_v3_definitional/`
Metrics: `data/exp_definitional_grounding_v3/metrics.json`

## Question

The existing grounding signal (`reading_grounding_loop.canonicalize`: bundle a word's
bag-of-words context over all exposures, take the cosine-nearest anchor above
SENSE_MATCH_THRESH=0.45) is definition-BLIND -- MEASURED, 14/634 = 2.2% of its facts are linked
by a definitional construction even though 58.5% have a definitional sentence sitting in their
own evidence set (`data/analysis_definitional_pattern_association_v1/metrics.json`). Does
grounding read off EXPLICIT DEFINITIONAL STRUCTURE (copula / appositive / glossary-colon /
"called" / "known as" / "refers to") produce a HIGHER-QUALITY set of meanings on the same
hand-scored rubric?

## Arms (all three sampled identically; NONE auto-scored)

| arm | what it is | facts |
|---|---|---|
| `DIST_ASIS` | existing signal, already on disk, already hand-scored 8/26/66 | 634 |
| `DIST_LOWINFO` | existing signal + the fault-2b PMI low-information gate ONLY | measured |
| `DEF` | **the new signal**: definitional extraction, same store, same gates | measured |

`DIST_LOWINFO` is the CONTROL that isolates how much of any change comes from the step-2 FIXES
rather than from definitional structure. Without it a DEF win is uninterpretable.

## Gates applied to the DEF arm (all pre-declared)

1. `lemma_word` normalization (never emits a non-word) -- fault 2a fix.
2. definiendum and head both open-class (`closed_class_lexicon.is_closed_class`).
3. head != definiendum (tautology refusal, same rule as v2).
4. low-information gate: `PMI(definiendum, head) > pmi_floor`, floor calibrated at the p75 of the
   closed-class reference PMI distribution -- fault 2b fix.
5. SENSE_MATCH_THRESH is **NOT** touched (fault 2c: no independent justification to move it; see
   notes/definitional_grounding_v3_2026-08-12.md section 3c).
6. Single attestation is sufficient to bank a definitional fact. This is the HYPOTHESIS UNDER
   TEST, declared as such: explicit definitional statements are one-shot relational encodings
   (hippocampal), unlike the multi-exposure distributional accumulator. `n_attestations` is
   recorded per fact so the director can retro-filter.

## Sampling (identical to the v2 B3 audit, so the numbers are comparable)

```python
gm_facts = [f for f in store._facts if f.relation == "GROUNDED_MEANING"]   # fid order
random.seed(42)
sample50_idx = random.sample(range(len(gm_facts)), 50)
```
Rubric: MEANINGFUL / RELATED / NOISE per `notes/foundation_grounding_sample_2026-08-12.md`.

## PRE-REGISTERED BANDS -- primary metric = MEANINGFUL share on the 50-pair DEF sample

Baseline to beat: **8%** (4/50), the director's hand-score of the v2 sample.
Reference ceiling: 35%, the v1 CROSS-grounded subset.

Statistical basis for the band edges (n=50, one-sided binomial vs p0=0.08, sd=1.92 facts):
9/50 = 18% is 2.6 sd above the baseline (p ~ 0.008); 6/50 = 12% is 1.0 sd (p ~ 0.16, i.e. NOT
distinguishable from 8% at this sample size). The bands are placed on those two points, not on
round numbers.

| band | condition |
|---|---|
| HARD_PASS | MEANINGFUL >= 35% (>=18/50) **AND** total DEF facts >= 200 |
| PASS | MEANINGFUL >= 18% (>=9/50) **AND** total DEF facts >= 200 |
| MIDDLE_BAND | 12% <= MEANINGFUL < 18%, **OR** MEANINGFUL >= 18% but total DEF facts < 200 |
| FAIL | MEANINGFUL < 12% (<6/50) |
| HARD_FAIL | MEANINGFUL < 12% **AND** total DEF facts < 100 |

## STATED UP FRONT -- what result means DEFINITIONAL EXTRACTION IS NOT THE ANSWER

**Definitional extraction is NOT the answer if EITHER:**
- (i) MEANINGFUL < 12% on the 50-pair DEF sample -- i.e. reading explicit definitions produces
  meanings no better than reading co-occurrence, which would say the problem is not the SIGNAL
  but the whole lemma-to-lemma "meaning is another word" representation; **or**
- (ii) MEANINGFUL >= 18% but the total DEF fact count is < 100 -- a high rate on a handful of
  facts is a curiosity, not a foundation. Explicitly: a 40% rate on 40 facts (16 meaningful) is
  NOT better than an 8% rate on 634 (51 meaningful), and I will report the ABSOLUTE MEANINGFUL
  COUNT alongside the rate for exactly this reason. If DEF wins on rate and loses on count, the
  honest verdict is MIDDLE_BAND, not PASS.
- (iii) Additionally, if `DIST_LOWINFO` scores as well as `DEF`, then the improvement is
  attributable to the step-2 FIXES and NOT to definitional structure, and the definitional
  signal has not been shown to add anything. This is a CONTROL failure and must be reported as
  such even if DEF clears its band.

## Compute architecture

Class **(b) sequential-CPU with justification**: the whole cell is regex extraction + dictionary
counting over 32,955 sentences plus ~2k HDFactStore writes at n_dim=2048. Measured wall time of
the constituent measurements already run: under 3 minutes. There is no matmul-heavy inner loop
to batch (the one matmul, the 1415x1415 cosine, is a single numpy call). GPU batching would be
pure overhead. Storage strategy: **sharded** (each fact its own vector in HDFactStore), which is
the mandated default and is what the existing loop already does.

## Schema-vet fields

- `cardinality_ok`: true -- EXPECTED_N_ARMS = 3; verdict logic counts arms and HARD_FAILs on a
  shortfall.
- `arms_differ_verified`: true -- DEF and DIST_LOWINFO fact sets are hash-compared; identical
  sets would mean an arm-wiring bug.
- `final_metrics_atomicity`: `tmp_replace`.
- `crlb_n/a`: no quantitative noise floor applies -- the primary metric is a HUMAN bucket count,
  not an estimator against a signal-in-noise bound. The relevant feasibility bound is the
  BINOMIAL one, which is computed above and is what the band edges are placed on.
- `baseline_in_band`: the baseline (DIST_ASIS) scored 0.08, inside (0.05, 0.95). Satisfied.
- `discriminator_fires`: the DEF arm must produce >= 100 facts that the DIST arm does NOT
  produce; measured overlap with the v2 store is currently 14/634, so disjointness is expected
  and is asserted in the cell.
- `calibration_check`: `adaptive_with_discriminator_gate` -- the PMI floor is calibrated off the
  closed-class lexicon (formula + reference percentiles in `hdlab/low_information_filter.py`);
  the calibration is logged to metrics and the known-meaningful control pairs are asserted to
  survive it.
- `defensive_error_checking`: start marker + crash metrics + `except SystemExit: raise` ordering
  + no bare except. Cell is single-pass and short; `heartbeat_present`: false with reason
  (wall time < 5 min, well under the 30-min heartbeat mandate).
- `progress_logging`: n/a, `timeout_s` < 1800.

## NOT auto-scored

The cell writes `b3_audit_sample_DEF.json` and `b3_audit_sample_DIST_LOWINFO.json` to disk and
emits verdict `STRUCTURAL_PASS_PENDING_B3`. It does **not** assign MEANINGFUL/RELATED/NOISE
labels and does not claim a band. The director hand-scores, exactly as the v2 cell correctly did.
