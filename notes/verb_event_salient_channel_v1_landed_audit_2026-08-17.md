# Audit: `exp_verb_event_salient_channel_v1` -- the verb-channel run nobody had read

**Auditor: Skunkworks (cert-owner). AUDIT ONLY -- I did not run, re-run, edit or dispatch anything.**
**Date: 2026-08-17. Status at time of writing: THE RUN IS STILL IN FLIGHT.**

---

## 1. The plain-language answer

**Short version: the verb gap is NOT concreteness in disguise, and it is NOT just "more numbers per
word". Adding three emotion-ish ratings (how pleasant, how exciting, how in-control a verb feels) to
our existing 12-number word description lifts verb-similarity scoring from about 44% of what humans
themselves manage to about 60%. Two different "cheat" controls that widen the description by exactly
the same amount with junk both came out WORSE than the original 12, so the lift is coming from what
the new numbers MEAN, not from having more of them. That is a real result and it is the first thing
in this arc that has survived its own controls.**

**But there is one honest hole, and it is not a small one.** The winning arm was scored on 3,161
word-pairs and the incumbent it beat was scored on 3,317 word-pairs -- *different sets of items*.
This project has a hard, retraction-bought rule that a number may not be compared across different
populations. So the headline "+0.1008" is **not yet a valid margin**. The fix is cheap (score the old
12-number version on the same 3,161 pairs and compare like with like) and until it is done the
correct statement is: *"the lift is very probably real and the dimensionality explanation is dead,
but the exact size of the lift is not established."*

**And a scope limit:** the arm that won is testing emotion ratings only. The brain drill that
licensed this asked for a fuller "event-salient" feature set including how consequential an action
is; that feature was **dropped before the run** because we only had it for 55% of the words and the
pre-registered threshold was 70%. So this is a result about *emotion norms*, not about the full
event-salient idea.

**Direct answer to "do verbs need their own channel, or was the gap concreteness all along, or do we
still not know":** *the gap was not concreteness (the concreteness control was run on every arm and
the signal survives it), and verbs do appear to benefit from feature dimensions the noun-tuned
12-number space does not carry -- but the size of that benefit is not yet measured on a valid
comparison, and the winning channel is narrower than the one that was proposed.*

---

## 2. What actually exists on disk, and how I enumerated it

**How I enumerated (not "I searched and did not find"):**

1. `ls -d experiments/*verb* experiments/*event* experiments/*salient*` -- 46 hits, exactly one
   matching the described cell: `experiments/exp_verb_event_salient_channel_v1.py`.
2. `ls -la data/ | grep -iE "verb|event|salient"` -- one output dir
   `data/exp_verb_event_salient_channel_v1/` plus its asset dir
   `data/verb_event_salient_channel_v1_assets/`.
3. Read `/tmp/vesc_full.log` (exists, 2,385 bytes).
4. Listed pid files (`*.pid`, `data/*.pid`, `/tmp/*.pid`) -- **no pid file for this run**; the PID was
   only ever in the launching agent's head. Confirmed liveness from the process table instead.
5. Parsed `units.jsonl` by `unit_key` (the resumable-per-unit checkpoint), not by grepping the log.

**Verdict on run state: STILL RUNNING, not dead, not complete.**

| Evidence | Reading |
|---|---|
| Process table | PIDs 112697 (shell) / **112698 (`.venv/Scripts/python.exe exp_verb_event_salient_channel_v1.py --grid full`)** both alive, started 13:55:35, still present at 15:46 |
| `/tmp/vesc_full.log` mtime | 15:34:40, last line `[arm] K_WORDNET_ORACLE_V ... (94.85s)` |
| `data/exp_verb_event_salient_channel_v1/units.jsonl` | mtime 15:34, **18 units** |
| `data/exp_verb_event_salient_channel_v1/metrics.json` | mtime **13:55** -- see the trap below |

**THE TRAP -- the `metrics.json` sitting in that directory is `run_mode: "reduced"`.** It is the
output of an *earlier, lower-precision grid*, not of the run in flight. Anyone who opens
`data/exp_verb_event_salient_channel_v1/metrics.json` today and quotes it is quoting the reduced
grid. The full run has **not yet written its metrics.json** -- that happens only after the last arm.

**What has completed in the FULL grid (8 of 10 units):** A0, A1, A2, A3, A4, S1, S2, K_WORDNET_ORACLE_V.
**Outstanding in the FULL grid:** `N2_RANDOM_GAUSSIAN` (in progress since ~15:34) and
`A0_OVERLAP_REPLICATION`, then the metrics write and the verdict.
ETA: N2 does 4 widths x 5 seeds at `N_BOOT=10000` (full) vs `2000` (reduced, where it took 231.6s),
so roughly 15-20 minutes, then the 170-pair overlap arm is quick. **Expected completion ~15:55-16:00.**

**Reassurance about the pending arms:** both already completed on the reduced grid and are in
`units.jsonl`, so their answers are known in substance (Section 5).

---

## 3. THE CONTROL THAT DECIDES IT -- A3 and A4 (lead item)

The question that kills or keeps this result: *does the lift come from the meaning of the new
columns, or merely from making the vector wider?* Three independent width controls were run.

| control | what it adds to the 12-dim incumbent | width | n | rho | % of 0.6121 ceiling |
|---|---|---|---|---|---|
| **A0 incumbent** | (nothing) | 12 | 3317 | **0.2696** | 44.1% |
| **A3 WIDTH_MATCHED_NOISE** | 3 Lancaster **rater-disagreement SD** columns (Auditory.SD, Gustatory.SD, Haptic.SD) | 15 | 3317 | **0.2550** | 41.7% |
| **A4 WIDTH_MATCHED_WRONG** | 3 **real-but-wrong** scalars (age-of-acquisition, log corpus frequency, word length) | 15 | 3303 | **0.2290** | 37.4% |
| **A1 EVENT_SALIENT** | 3 **Warriner VAD** columns (Valence_z, Arousal_z, Dominance_z) | 15 | 3161 | **0.3705** | 60.5% |
| *N2 random Gaussian (reduced grid)* | pure random code at each width, 5 seeds, MAX draw reported | 15 | 3317 | *0.0194* | *3.2%* |

**A3 and A4 did NOT match A1. They did not even match A0.** Widening the incumbent by three columns
of rater-noise *cost* 0.0146; widening it by three real-but-irrelevant scalars *cost* 0.0406. A pure
random 15-dim code scores 0.019 at its luckiest of five seeds. The pre-registered
`STOP_IF_iii_CONTROL_FIRES_DIMENSIONALITY_NOT_CHANNEL` therefore **did not fire**.

This is the same control that killed the earlier lookalike claim (+11 rater-SD columns and +6 derived
columns both scoring *below* the 12-dim incumbent). **It fired then. It did not fire now, and it
reproduced its own earlier behaviour while not firing** -- A3/A4 landing below A0 is exactly the
earlier negative result recurring, which is a good sign that the control is working rather than
asleep.

A3's comparison to A0 is **population-clean**: A3 is scored on the identical 3,317 pairs (A3 is A0
widened, and the Lancaster SD columns cover the entire vocabulary). A4 is on 3,303 of the same 3,317
(99.6%). So *"junk columns do not help, they hurt"* is established on a valid comparison. What is
**not** established on a valid comparison is the size of A1's advantage over them -- see next.

---

## 4. THE POPULATION PROBLEM (the one thing that is actually wrong)

**A1 and A2 are scored on n=3,161. A0, A3 are on n=3,317; A4 on n=3,303. Those are different item
sets, and the cell compared point estimates across them.**

The relevant code compares bare point estimates:

```python
a1_gain = a1.get("margin_over_strongest_floor", {}).get("point")
a3_gain = a3.get("margin_over_strongest_floor", {}).get("point")
a3_matches = bool(... a3_gain >= a1_gain)
stop_ifs["iii_CONTROL_FIRES"] = bool(a1_clears and (a3_matches or a4_matches))
```

There is **no paired comparison and no common-subset rescoring anywhere in the cell.** The cell does
compute the common subset -- `joint intersection across ALL 7 vector arms: n=2433` -- but the log
line and the code comment both label it *"informational (D7), NOT a hard abort -- each arm is scored
on its OWN achievable intersection (documented deviation)"*. **The common subset was computed and
then not used.**

So, plainly:

- **The +0.1008 A1-over-A0 headline is NOT a valid margin.** It is two point estimates on two
  different item sets. It must not be quoted as a margin.
- The A1-over-A3 (+0.1155) and A1-over-A4 (+0.1414) gaps are likewise cross-population.
- **A1 vs A2 IS valid** -- both on the identical 3,161 pairs. On that comparison, 12-base + 3-VAD
  (0.3705) beats 3-VAD alone (0.3081) by 0.0624. That is a real, population-clean statement: the
  VAD columns are not simply replacing the incumbent, they are adding to it.

**How worried should we be?** I ran a population-comparability diagnostic off the benchmark files
alone (no vectors, no cell re-run). Reconstructing A1's item set independently reproduces **exactly
n=3,161**, with 169 disjoint-stratum pairs dropped for missing Warriner VAD (156 after the cell's
additional 12-dim-vocab filter -- 4.7% of the stratum). The dropped pairs are **not** distinguishable
from the kept ones:

- gold mean/sd: kept 4.287 / 2.655 vs dropped 4.314 / 2.563; Mann-Whitney **p = 0.849**
- relation mix near-identical (NONE 59.8% vs 63.3%; SYNONYMS 8.7% vs 11.8%; ANTONYMS 3.0% vs 4.1%)
- dropped examples: `tap/pat`, `erode/destroy`, `bake/broil`, `sing/hum`, `upset/frustrate`

So the two populations look interchangeable on every property I can measure without scoring them.
**That lowers the risk substantially but does not discharge the rule** -- the property that matters
is how the *incumbent code* scores those 156 pairs, and that was not measured.

**Required fix (one cheap arm, not a redesign): rescore A0, A3 and A4 on A1's 3,161 pairs and report
the paired differences with a paired bootstrap.** Until then the honest headline is *"A1 clears every
floor at 60.5% of ceiling and no width control comes near it; the exact margin over the incumbent is
pending a same-population rescore."*

---

## 5. Full arm table (FULL grid, PRIMARY 3,317-pair disjoint stratum unless noted)

Every score both as absolute rho and as a fraction of the **0.6121** ceiling. Null p95 and CI
half-width sit beside every margin, because a width is not an effect.

| arm | width | n | rho | **% of ceiling** | null p95 | rho CI hw | strongest floor | margin CI lo | band |
|---|---|---|---|---|---|---|---|---|---|
| A0_INCUMBENT_12 | 12 | 3317 | 0.2696 | **44.1%** | 0.0298 | 0.0340 | SCRAMBLE_P95 | +0.1919 | ABOVE |
| **A1_EVENT_SALIENT** | 15 | 3161 | **0.3705** | **60.5%** | 0.0295 | 0.0349 | SCRAMBLE_P95 | +0.2937 | ABOVE |
| A2_EVENT_ONLY | 3 | 3161 | 0.3081 | **50.3%** | 0.0302 | 0.0349 | SCRAMBLE_P95 | +0.2310 | ABOVE |
| A3_WIDTH_MATCHED_NOISE | 15 | 3317 | 0.2550 | **41.7%** | 0.0297 | 0.0340 | SCRAMBLE_P95 | +0.1792 | ABOVE |
| A4_WIDTH_MATCHED_WRONG | 15 | 3303 | 0.2290 | **37.4%** | 0.0310 | 0.0341 | SCRAMBLE_P95 | +0.1508 | ABOVE |
| S1_SLOT_FRAME | 24 | 2517 | 0.0442 | **7.2%** | 0.0412 | 0.0391 | SCRAMBLE_P95 | **-0.0537** | NOT_SEPARATED |
| S2_SLOT_DELTA | 12 | 2517 | 0.0798 | **13.0%** | 0.0339 | 0.0391 | SCRAMBLE_P95 | **-0.0093** | NOT_SEPARATED |
| K_WORDNET_ORACLE_V *(oracle, no verdict weight)* | -- | 3317 | 0.4364 | **71.3%** | 0.0282 | -- | GOLD_PERM_P95 | +0.3631 | ABOVE |

**The four floors, recomputed on this population** (they are weak here -- worth stating plainly, a
verb-similarity pair-correlation instrument gives the constant/prototype floor almost nothing to
work with, exactly as the standing rule predicts a floor's strength is a property of the scorer):

| arm | F_ORTHOGRAPHIC | F_FREQUENCY_HARDENED | F_CONSTANT_PROTOTYPE | F_SCRAMBLE_PERM_P95 |
|---|---|---|---|---|
| A0 | -0.0159 | -0.0425 | +0.0149 | **+0.0298** |
| A1 | -0.0090 | -0.0500 | +0.0131 | **+0.0295** |
| A2 | -0.0090 | -0.0500 | +0.0195 | **+0.0302** |
| A3 | -0.0159 | -0.0425 | +0.0123 | **+0.0297** |
| A4 | -0.0153 | -0.0426 | +0.0141 | **+0.0310** |
| S1 | -0.0218 | -0.0670 | -0.0327 | **+0.0412** |
| S2 | -0.0218 | -0.0670 | -0.0068 | **+0.0339** |

The scramble floor is the binding one for every arm. It sits at ~0.030 at n~3,300 and ~0.041 at
n=2,517 -- that is the null's own width at this n, and it is the right thing to beat.

**Not-yet-in-the-full-grid, reported from the reduced grid (labelled, never pooled):**

- **`N2_RANDOM_GAUSSIAN`** -- pure random codes, 5 seeds per width, **MAX draw reported never the
  mean** (correct policy). Max draws: w3 **+0.0083**, w12 **+0.0063**, w15 **+0.0194**,
  w24 **+0.0177**. Random width buys nothing at any width. This is the cleanest possible statement
  that A1's 15 dims are not a width artefact.
- **`A0_OVERLAP_REPLICATION`** -- see Section 7.

---

## 6. The ceiling: 0.6121, and its own uncertainty (I recomputed it myself)

I recomputed the ceiling from the released annotator matrix
`data/encoder_eval_benchmarks/simverb3520_annotator_ratings.csv` (3,520 pairs x 702 annotators,
sentinel `-1` for not-rated):

- median ratings per pair **10.0**, mean 13.96; every annotator rated exactly **70** pairs
- exactly **20** pairs were rated by all 702 annotators -- the consistency set
- **APIAA over all C(702,2) = 246,051 annotator pairs on that 20-item block = 0.6121** -- an exact
  match to the value the cell hardcodes. AIAA vs mean-of-others = 0.7549 (their 0.7533; tie handling).

**Two things the fitness file's presentation hides, which I am flagging:**

1. `APIAA_consistency_set_only` and `APIAA_all_pairs_min_overlap_10` are both reported as 0.6121 with
   both `n_annotator_pairs = 246051`. **These are the same statistic, not two corroborating ones.**
   Because each annotator rated only 70 pairs and 20 of those are the shared consistency set, *any*
   two annotators overlap on ~20 items, essentially all of them the consistency set. The
   "min-overlap-10 over all pairs" variant reduces to the consistency-set variant. **The ceiling
   rests on 20 items and one computation.**
2. **I item-bootstrapped it** (resample the 20 items, 400 reps): mean 0.6026,
   **95% CI [0.4964, 0.6926], half-width 0.0981.**

So every "% of ceiling" figure carries about +/-16% *relative* uncertainty from the denominator alone.
Stated honestly:

| arm | % of 0.6121 | range across the ceiling's own CI |
|---|---|---|
| A0 | 44.1% | 38.9% -- 54.3% |
| **A1** | **60.5%** | **53.5% -- 74.6%** |
| A2 | 50.3% | 44.5% -- 62.1% |
| A3 | 41.7% | 36.8% -- 51.4% |
| A4 | 37.4% | 33.1% -- 46.1% |
| K oracle | 71.3% | 63.0% -- 87.9% |

**Never quote a % of ceiling without this range.** The ceiling is the least well measured number in
the whole report.

---

## 7. The two strata, kept separate

- **PRIMARY (all headline numbers above): the 3,317-pair SimVerb stratum disjoint from SimLex-V.**
- **REPLICATION / NOT INDEPENDENT: `A0_OVERLAP_REPLICATION`, 170 pairs.** 170 of SimLex-999's 222
  verb pairs are also in SimVerb. **I verified this independently off the raw release files: 170
  shared unordered pairs, and the two gold sets agree at Spearman rho = 0.9121** -- an exact
  reproduction of the recorded figure. These pairs are *not* an independent measurement.
  On the reduced grid: **rho 0.2290 (37.4% of ceiling), n=170, CI [0.0875, 0.3610], scramble p95
  0.1293, band NOT_SEPARATED, and its concreteness control FAILS (`survives_partial: false`).**
  At n=170 the null's own width is 0.129 and the margin is 0.0997 -- **a width, not an effect.**
  The cell labels it correctly with a `NEVER_POOLED_WARNING`. **Do not pool it, do not compare across.**

Population arithmetic, independently reproduced by me from the release files: SimVerb 3,500 rows
(3,499 unique unordered pairs -- one duplicate), 3,487 usable in our 12-dim vocabulary, minus the 170
SimLex-V overlap = **3,317 primary**. Matches the cell's log exactly.

---

## 8. C1_PARTIAL -- the concreteness control, for EVERY arm

This build was licensed only on condition this control ran, because dimension 12 of our own incumbent
space *is* a concreteness rating, so the noun/verb gap could have been a concreteness gap wearing a
disguise. It ran on every arm. Covariates partialled out: `mean_conc, absdiff_conc, mean_log10freq,
absdiff_log10freq`, 2,000 bootstrap reps (full grid).

| arm | raw rho | partial rho | strongest partial floor | partial margin (CI) | **survives** |
|---|---|---|---|---|---|
| A0 | 0.2696 | **0.2586** | CONSTANT_PROTOTYPE 0.0450 | +0.2136 [0.1693, 0.2572] | **TRUE** |
| **A1** | 0.3705 | **0.3655** | CONSTANT_PROTOTYPE 0.0460 | +0.3195 [0.2756, 0.3641] | **TRUE** |
| A2 | 0.3081 | **0.3030** | CONSTANT_PROTOTYPE 0.0381 | +0.2648 [0.2168, 0.3133] | **TRUE** |
| A3 | 0.2550 | **0.2439** | CONSTANT_PROTOTYPE 0.0431 | +0.2008 [0.1572, 0.2444] | **TRUE** |
| A4 | 0.2290 | **0.2299** | CONSTANT_PROTOTYPE 0.0442 | +0.1856 [0.1417, 0.2283] | **TRUE** |
| S1 | 0.0442 | 0.0584 | SCRAMBLE_P95 0.0438 | +0.0146 [-0.0392, 0.0681] | **FALSE** |
| S2 | 0.0798 | 0.0916 | SCRAMBLE_P95 0.0311 | +0.0605 [-0.0007, 0.1173] | **FALSE** |
| A0_OVERLAP (170, reduced) | 0.2290 | 0.2116 | SCRAMBLE_P95 0.1297 | +0.0820 [-0.1217, 0.2878] | **FALSE** |
| K oracle | 0.4364 | 0.4762 | -- | (context only, no verdict weight) | n/a |

**Read-out: A1 loses only 0.0050 rho when concreteness and frequency are partialled out (0.3705 ->
0.3655). The incumbent A0 loses 0.0110. The signal is not concreteness.**
`STOP_IF_vi_CONFOUND_CONCRETENESS_ARTIFACT` did not fire. **This is the audit point I was most
prepared to see fail, and it did not.**

Note the two arms whose C1 control *fails* are exactly the two arms that fail everything else (S1/S2,
the slot-frame arms) -- their partial rho going *up* while remaining inseparable from the scramble
floor is what a null looks like, not a confound.

---

## 9. Which STOP-IF fired

**None.** From the reduced grid's written metrics and reproduced by my read of the full-grid units:

```
stop_ifs = {'i_STRATUM_SHIFT': False, 'iii_CONTROL_FIRES': False, 'iv_DISSOCIATION': False,
            'v_INSTRUMENT_LIMIT': False, 'vi_CONFOUND': False}
```

- **i_STRATUM_SHIFT** (incumbent falls below its own scramble null on the new stratum): did not fire.
  A0 = 0.2696 vs scramble p95 0.0298. The instrument transferred from n=222 to n=3,317 intact.
- **iii_CONTROL_FIRES** (a width control matches A1): did not fire -- Section 3. *Caveat: evaluated
  cross-population, Section 4.*
- **iv_DISSOCIATION** (A2 within 0.03 of A1, i.e. the 12 base dims contribute nothing): did not fire.
  A1 gain 0.3410 vs A2 gain 0.2778, difference **0.0632** -- more than double the 0.03 trigger. This
  is the one comparison that is fully population-clean, and it says the base space and the new
  columns are doing different work.
- **v_INSTRUMENT_LIMIT** (no arm clears its own floor): did not fire.
- **vi_CONFOUND** (incumbent does not survive the concreteness partial): did not fire -- Section 8.

**Regression gate, verified in the full run's own log:** landed n=222 SimLex-V rho **0.2607**,
recomputed **0.260664623528911**, `reproduced=True`. The gate is on the point estimate only (correct:
rho is deterministic given the data; the null and CI carry a per-process seed). **Reproduced.**

**Reduced-grid verdict string (the full grid has not written one yet): `EVENT_SALIENT_CHANNEL_REAL`.**

---

## 10. Scope limits and audit gaps

1. **A1 IS NARROWER THAN THE BRIEF LICENSED.** From the run's own log:
   `event_col_names=['Valence_z','Arousal_z','Dominance_z'] keep_conseq=False (coverage 0.5473,
   threshold 0.7)`. **ATOMIC-derived consequentiality was dropped at the pre-registered coverage
   gate** (0.547 < 0.70) -- which is the gate behaving correctly, not a failure. Separately, the
   metrics note records that Diveica et al. 2022 **socialness norms are not on disk** (re-enumerated
   this pass; only `data/corpora/social_iqa/`, a QA corpus, exists -- no word-level ratings).
   **A1 is 12+3 = 15 dims, not the drill's hypothesised 17.** Any claim from this run is a claim
   about *affective (VAD) norms*, not about the full event-salient feature set.
2. **Cross-population comparison** -- Section 4. The single blocking defect.
3. **Tie conventions are NOT reported both ways.** The cell uses `rankdata(method="average")`
   throughout, one convention only. Honest severity assessment: **low.** Average-midrank is the
   standard and essentially the only sensible convention for a Spearman pair-correlation, and the
   both-ways rule was earned on hit@1-style scorers where tie policy swings the number. But the rule
   is formally unmet and I am recording that rather than waving it through.
4. **The ceiling is a 20-item statistic with a +/-0.098 CI, and its two reported forms are one
   statistic** -- Section 6.
5. **The stale `metrics.json`** -- Section 2. It says `reduced`. Until the run finishes, that file is
   a mis-citation waiting to happen.
6. **Cross-arc overlap check (substrate KB):** the nearest prior work is this cell's own licensing
   cell `exp_verb_target_space_n222_v1` (the n=222 SimLex-V measurement, rho 0.2607), which is
   *reused as the regression gate here rather than rediscovered* -- the correct pattern. This run is
   a genuine extension (new stratum at 15x the n, new arms, new controls), not a rediscovery.

## 11. Reproducibility finding (unlooked-for, and good)

`units.jsonl` contains **two independent runs**: a completed `reduced` grid (N_PERM=400,
N_BOOT=2000, N_BOOT_PARTIAL=300) and the in-flight `full` grid (N_PERM=2000, N_BOOT=10000,
N_BOOT_PARTIAL=2000). **Every arm's point estimate is identical between them to all 15 decimal
places** -- A0 0.269631, A1 0.370455, A2 0.308088, A3 0.254997, A4 0.229012, S1 0.044168,
S2 0.079823, K 0.436430. The scramble nulls converge to ~0.030 under both (400 and 2,000 perms).

**Implication: the substantive answer is already in hand and is stable. The full run is a precision
upgrade on the nulls, CIs and partials -- it is not going to change the ranking of the arms.** That
is also why the pending N2 and overlap arms carry no suspense: both already ran on the reduced grid
and are reported above.

---

## 12. What is missing, and exactly what would finish this

**Do not extrapolate a verdict. Two things are outstanding and one is a defect.**

**To finish the run (no action needed -- just let it land, ~15:55-16:00):**
1. `N2_RANDOM_GAUSSIAN` at full N_BOOT.
2. `A0_OVERLAP_REPLICATION` at full N_PERM.
3. The metrics.json write, which will overwrite the stale `reduced` file with the `full` one.

**To make the headline quotable (the one real gap):**
4. **A paired, same-population comparison.** Rescore A0, A3 and A4 on A1's exact 3,161 pairs and
   report paired bootstrap differences. Cheap; it is a rescoring of arms already built. Until it
   exists, the +0.1008 must not be quoted as a margin.

**To make the claim match the brief:**
5. Either acquire consequentiality coverage above the 0.70 gate and the Diveica socialness norms, or
   **restate the claim as "VAD norms", which is what was actually tested.**

**Files**
- cell: `d:/AI/hd-instrument/experiments/exp_verb_event_salient_channel_v1.py`
- output: `d:/AI/hd-instrument/data/exp_verb_event_salient_channel_v1/{units.jsonl,metrics.json}`
- log: `/tmp/vesc_full.log`
- ruler fitness: `d:/AI/hd-instrument/data/simverb_ruler_fitness.json`
- benchmark (gitignored, read-only, do NOT `git add -f`): `d:/AI/hd-instrument/data/encoder_eval_benchmarks/`

**Credit:** SimVerb-3500 is Gerz, Vulic, Hill, Reichart & Korhonen (EMNLP 2016). SimLex-999 is Hill,
Reichart & Korhonen (2015). The corrected inter-annotator agreement framing is due to Pilehvar,
Kartsaklis, Prokhorov & Collier (EMNLP 2018). The VAD norms are Warriner, Kuperman & Brysbaert (2013);
concreteness Brysbaert, Warriner & Kuperman (2014); AoA Kuperman et al. (2012); sensorimotor norms
Lynott, Connell, Brysbaert et al. (Lancaster, 2020). We are building on their work.
