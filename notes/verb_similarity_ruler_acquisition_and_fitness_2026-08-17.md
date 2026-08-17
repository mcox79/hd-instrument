# The verb measuring stick: acquired, and checked before use (2026-08-17)

## THE ANSWER, IN PLAIN LANGUAGE

**Yes. We now have a good enough measuring stick for verbs, and it is a big improvement -- but it
does not measure something new, it measures the same thing far more precisely, and one of the two
things we wanted to check with it turns out to be mostly the same test we already ran.**

Here is the situation in ordinary words. Earlier today we tested whether our 12-number description
of word meaning can tell which verbs mean similar things. It scored 0.26 where pure chance scores
0.12 -- looks like a real gap -- but our error bar on that gap was plus-or-minus 0.19, wider than
the 0.145 gap itself. So we could not tell a real effect from noise. The problem was not the model;
it was that 222 verb pairs is too few to measure anything that small. We needed a longer ruler.

We downloaded one: **SimVerb-3500**, the standard 3,500-pair verb-similarity set, from the
authors' own university repository. It is real, it checksums, and it is the genuine 2016 release.
Almost all of it is usable: **3,487 of the 3,500 pairs** have both verbs in our vocabulary -- only
three verbs are missing (*capitulate*, *perspire*, *repress*). That is a 16-fold increase in data
and it shrinks our error bar from **+/-0.19 to about +/-0.05**, which is roughly **three times
narrower than the 0.145 effect we are trying to see.** The power problem is solved. If the effect
is real, this ruler will show it; if it is not, this ruler will say so, and either answer will be
trustworthy. On the old ruler neither answer would have been.

Three warnings come with it, and they matter.

**First, the ruler has a ceiling, and it is much lower than advertised.** The people who built
SimVerb originally reported that their human raters agreed with each other at 0.84. That number was
wrong and was later corrected to 0.61. We did not take anyone's word for this: the release includes
the raw score of every individual rater, so we recomputed the agreement ourselves and got
**0.6121** -- the corrected figure, not the published one. Practically, this means humans only
agree with each other about verb similarity at around 0.61, so **0.61 is the realistic ceiling for
any system on this test.** Our current 0.26 should be read against 0.61, not against a perfect 1.0.
Verb similarity is genuinely hard, for people too.

**Second, the new ruler and the old ruler are largely the same ruler.** 170 of the old set's 222
verb pairs are *also in* SimVerb -- 77% of them -- and on those shared pairs the two sets' human
scores agree at 0.91. So SimVerb is not an independent second opinion on our earlier result; it
mostly contains that result. Keeping the old 222 pairs as a separate "replication" would be
re-marking the same exam and calling it a second exam. The honest version is to use the **3,317
pairs that are NOT in the old set** as the primary measurement -- that is a genuinely independent
stratum, and it is still large enough (error bar +/-0.050) to settle the question.

**Third, the control we have never run is now runnable, and it might overturn the whole framing.**
Our 12-number description includes a "how concrete is this word" number. Verbs are less concrete
than nouns. So the noun-beats-verb result we have been treating as being about grammar might just
be about concreteness. The norms needed to strip that out are already on disk and cover **every
single one** of the 3,487 usable pairs, so this control costs nothing extra to run. The related
"imageability" control is **not** runnable -- the only imageability numbers we hold cover 2 of
3,500 pairs -- and it would need a new dataset acquired first.

**Bottom line: the ruler is acquired and fit for purpose. The channel build is licensed on power
grounds -- but it should not start until the concreteness control has run, because that control can
still show the thing we are trying to fix is not the thing we think it is.**

---

## 1. HOW ABSENCE WAS ESTABLISHED (enumeration, not search)

The claim "SimVerb-3500 is not on disk" was re-verified before acting on it, by enumeration:

```
python -c "import os; [print(os.path.getsize(os.path.join(dp,f)), os.path.join(dp,f))
           for dp,dn,fn in os.walk('data/encoder_eval_benchmarks') for f in sorted(fn)]"
```

returned exactly two files -- `simlex999.txt` (44,050 B) and `wordsim353_combined.csv` (7,433 B),
`TOTAL FILES: 2` -- confirmed independently by `ls -la` on the absolute path. This is a full walk of
the directory, not a keyword search, so it supports the absence claim.

**Recoverability was checked before concluding absence**, per the standing rule that "never
persisted" and "not recoverable" are different claims. A separate `os.walk` of `data/` (excluding
the read-only `data/foundation/`, which was never opened) filtered on
`imag|concrete|norms|binder|sensorimotor|aoa|warriner|brysbaert|glasgow|cortese|mrc` returned 25
matches. **No verb-similarity gold was derivable from anything we hold.** WordNet can produce a verb
*taxonomy* similarity, but that is a structured-resource oracle (the drill already schedules it as
`K_WORDNET_ORACLE_V`, a labelled ceiling reference), not human similarity judgements, and it cannot
serve as gold. The CSKG (`data/grounding_testbed/cskg.tsv.gz`) holds relational edges, not graded
similarity. So acquisition was genuinely required.

**One correction to the drill fell out of that enumeration.** The drill records *"Binder-65 norms --
absent"*. **That is wrong: `data/corpora/binder/binder2016_ratings.csv` exists (357,370 B, 535 rows,
85 columns)**, carrying all 65 Binder dimensions plus `LEN`, `FREQ`, `L10 FREQ`, `Orth` and an
**`IMG` (imageability)** column. This does not change the drill's *ruling* -- Binder-535 remains
unusable as a verb space, for the measured reason below rather than the assumed one -- but the
absence claim itself was incorrect, and this is the second time in 48h that an unenumerated absence
claim has been found false. It is corrected here rather than routed around.

## 2. PROVENANCE RECORD

Full record: `data/encoder_eval_benchmarks/PROVENANCE_simverb.md`. Summary:

| field | value |
|---|---|
| **Source URL** | `https://www.repository.cam.ac.uk/bitstream/handle/1810/264124/simverb-3500-data.zip` (authors' institutional repository; redirects to the Cambridge DSpace bitstream API) |
| **Landing page** | `https://www.repository.cam.ac.uk/items/8a568201-0fa4-4e54-81b1-f920102492ea` |
| **Retrieved** | 2026-08-17 UTC, `curl -sSL`, HTTP 200 |
| **Archive size** | 246,965 bytes |
| **Archive sha256** | `dcd3d5a43724d4e763b9c7f7f28f3785c5cc73e79144346c3b5904c667719530` |
| **Main file** | `data/encoder_eval_benchmarks/simverb3500.txt`, 97,778 B, sha256 `b58f68454cf9354b94ecd8bfd778ff2cc784a25fc7dca02bc695319ad2b4157e` |
| **Internal timestamp** | 2016-08-01, consistent with EMNLP 2016 |

**Citation, with credit.** Daniela Gerz, Ivan Vulic, Felix Hill, Roi Reichart and Anna Korhonen
(2016), *SimVerb-3500: A Large-Scale Evaluation Set of Verb Similarity*, EMNLP 2016, pp. 2173-2182
(ACL `D16-1235`; arXiv `1608.00869`). The corrected agreement figure is due to Pilehvar, Kartsaklis,
Prokhorov and Collier (2018), *Card-660*, EMNLP 2018 (arXiv `1808.09308`). The dataset was
deliberately built format-compatible with SimLex-999 (Hill, Reichart & Korhonen 2015) -- that is the
authors' design decision and it is why our existing loaders nearly work on it.

Six files were placed, renamed to the flat lowercase convention of `simlex999.txt` but otherwise
**byte-identical to the release**, so every checksum stays checkable against the source archive.
Beyond the main file: the standard `dev500`/`test3000` splits, the upstream README, a per-lemma
**BNC frequency + VerbNet class** stats file, and the **3,520 x 702 per-annotator ratings matrix**
(the evidence for section 4).

**Two format traps**, both verified from the bytes, both capable of silently corrupting a run:
`simlex999.txt` **has a header line and CRLF endings**; `simverb3500.txt` **has no header line and
LF endings**. Skipping line 1 of SimVerb silently drops the pair `take/remove`; not skipping line 1
of SimLex crashes on `float("SimLex999")`.

### Two flags on the placement

- **Licence is UNRESOLVED.** The drill assumed CC-BY. That was **not verified** during acquisition
  and is recorded as unresolved. It does not affect local evaluation use, and the files are
  gitignored, so we redistribute nothing.
- **The files are NOT committed, and this deviates from the instruction I was given.** The
  instruction was to commit the benchmark file. Enumeration shows the repo convention is the
  opposite: `data/encoder_eval_benchmarks/` is gitignored at `.gitignore:53` (`data/*/**`),
  `git ls-files` returns **nothing** for that directory -- `simlex999.txt` itself is untracked --
  and nothing under `data/grounding_testbed/` is tracked either, **including its `PROVENANCE_*.md`
  files**. The allowlist at `.gitignore:51-58` is explicit and narrow (`metrics.json`,
  `results.json`, `provenance.json`, `verdict.json`, `recent_verdicts.json`). Committing would have
  required `git add -f` against a deliberate exclusion. I did not do that silently. Durability is
  instead carried by two tracked files: this note, and
  `verification/verify_simverb_ruler_fitness.py`, which re-checks the checksums and every number
  below. **If the intent was genuinely to track the data, that is a one-line `.gitignore` allowlist
  change and it is the operator's call, not mine.**

## 3. FITNESS -- USABLE n AND THE POWER QUESTION

All figures from `verification/verify_simverb_ruler_fitness.py`; machine-readable copy at
`data/simverb_ruler_fitness.json`.

**Our vocabulary** is `hdlab.grounded_similarity._table()` -- the 36,810-word, 12-dimension
Lancaster-11 + Brysbaert-`Conc.M` table that `exp_verb_target_space_n222_v1` uses for its
`K1_OWN_NORMS` arm. This is the same table the licensing measurement used, so the intersection below
is the correct one and not a proxy.

| quantity | value |
|---|---|
| headline pairs | 3,500 |
| POS tags present | `V` only |
| distinct verb lemmas | 827 |
| **usable pairs (BOTH members in our vocabulary)** | **3,487** |
| retention | 99.63% |
| verbs missing from our vocabulary | 3 (`capitulate`, `perspire`, `repress`) |

**The usable n is 3,487, not the headline 3,500.** The loss is negligible, which is itself worth
stating: intersection with our vocabulary is *not* the binding constraint here, unlike most assets
we have evaluated.

### CI half-width at the usable n, against the +0.1452 effect

The quantity that has to shrink is the half-width on the **margin** (treatment minus strongest
floor), not on a single correlation -- that is what returned `NOT_SEPARATED`. Measured on the n=222
run: margin CI `[-0.0496, +0.3379]`, half-width **0.1937**; single-rho half-width 0.1280. The margin
half-width is **1.51x** the single-rho half-width. Projecting the *measured* margin half-width by
`1/sqrt(n-3)`:

| stratum | n | projected margin CI half-width | vs the +0.1452 effect |
|---|---|---|---|
| n=222 SimLex-V (what we ran) | 222 | **0.1937** | **WIDER than the effect -- why it was unresolvable** |
| SimVerb, usable | 3,487 | **0.0486** | **3.0x NARROWER -- resolvable** |
| SimVerb minus SimLex-V pairs | 3,317 | **0.0498** | **2.9x NARROWER -- resolvable** |
| SimLex-V under the same filter | 222 | 0.1937 | still wider; unchanged |

Single-rho half-width at n=3,487 is 0.0332. Power gain over n=222 is **3.99x**. The minimum n at
which the margin half-width drops below 0.1452 is **393** -- we clear it by a factor of nearly nine.

**Plainly: the ruler does solve the problem it was acquired to solve.** A real improvement will now
come back as a separated result rather than as another null, and -- symmetrically -- a null at this
n is informative rather than an artifact of width. The `POWER_INSUFFICIENT` fallback the drill
pre-registered for the no-SimVerb branch is **not** needed.

Two honest limits on that claim. The projection assumes the `1/sqrt(n-3)` scaling of the *measured*
n=222 margin half-width holds on a different population; the cell must report its own measured
bootstrap CI and not this projection. And a narrower CI does not make the effect real -- it only
makes the answer trustworthy either way.

## 4. INTER-ANNOTATOR AGREEMENT -- VERIFIED, NOT ADOPTED

The drill records that SimVerb's reliability was corrected downward from 84.0 to 61.2. **Verified
from source, three independent ways:**

1. **The paper's original claim.** SimVerb-3500 reports pairwise IAA rho = **0.84** (and 0.86 for
   the mean-based variant).
2. **The third-party correction.** Card-660 (Pilehvar et al. 2018) reports SimVerb-3500's pairwise
   IAA as **0.61**, alongside 0.67 for SimLex-999 and 0.90 for Card-660 itself.
3. **Our own recomputation from the raw release -- the load-bearing evidence.** The release ships
   `SimVerb-3520-annotator-ratings.csv`, a 3,520 x 702 pairs-by-annotators matrix. Recomputing
   average pairwise inter-annotator Spearman over all **246,051** annotator pairs, with average
   ranks for ties, gives **APIAA = 0.6121**. That reproduces the corrected figure and **not** the
   published 0.84. The mean-based variant (each annotator vs the mean of the other 701) gives
   **0.7533**.

Neither published number was taken on trust; the third route is a from-source recomputation and it
settles it.

**A caveat on what this statistic can be, which applies equally to the published 0.84.** Each
annotator rated exactly 70 items, 20 of which are the shared consistency set. **98.7% of annotator
pairs overlap on exactly those 20 items and nothing else** (measured: median annotator-pair overlap
20, mean 20.68, max 70). Pairwise IAA on this release is therefore unavoidably a ~20-item statistic
per annotator pair. That is a property of the annotation design, not of our computation.

**What it implies for the highest achievable score.** The realistic ceiling on this ruler is
**~0.61**, not 1.0. A system at rho 0.61 is at human-agreement level and there is no headroom above
it that can be distinguished from annotator noise. Consequences for how we report:

- Our verb rho of **0.2607 should be read against 0.61**, where it is ~43% of the ceiling -- not
  against 1.0, and not against 0.84.
- **Never quote 0.84.** It is a withdrawn number.
- A gain of +0.145 is a large fraction of the *available* range once the 0.12 floor and 0.61 ceiling
  are both accounted for. This makes the effect more interesting, not less -- but it is also a
  reason the ceiling must be stated every time, since a fixed absolute gain looks much larger
  against a 0.61 ceiling than against 1.0.

## 5. OVERLAP WITH SIMLEX'S 222 VERB PAIRS -- THE TWO ARE NOT INDEPENDENT

Measured on unordered, lowercased pairs:

| quantity | value |
|---|---|
| SimLex-999 verb pairs | 222 |
| **shared with SimVerb-3500** | **170** |
| **fraction of SimLex's 222 also in SimVerb** | **76.6%** |
| fraction of SimVerb's 3,500 also in SimLex | 4.9% |
| SimLex-V verb vocabulary | 170 words |
| shared vocabulary | 148 of those 170 words |
| **agreement of the two gold scores on the 170 shared pairs** | **Spearman 0.9121** |

**The overlap is large, so the two are not independent measurements and no number may be compared
across them as though they were.** Three specific consequences:

1. **The drill's plan is not sufficient as written.** It schedules SimVerb as primary with SimLex-V
   as a 222-pair "replication stratum ... never pooled". *Never pooled* prevents double-counting in
   a combined estimate but **does not create independence**: 170 of the 222 replication pairs are
   literally inside the primary, and the two gold sets agree at 0.91 on them. A "replication" on
   those pairs would re-mark the same exam. It must not be reported as independent confirmation.
2. **Use the disjoint stratum as primary.** The 3,317 usable SimVerb pairs not in SimLex-V are
   genuinely independent of everything measured today, and at half-width **0.0498** they are ample.
   This costs almost nothing (3,317 vs 3,487) and buys a claim that survives scrutiny.
3. **The 0.2607 figure may not be carried across.** Already required by the drill (`A0` must re-earn
   its baseline), and the overlap makes it sharper: a SimVerb `A0` result is partly a re-measurement
   of the same pairs, so agreement between them is expected and is **not** evidence of
   generalisation.

The 0.9121 gold agreement is reassuring about *quality* -- the two annotation efforts converge --
while being exactly what forbids treating them as independent.

## 6. SPECIFICATION FOR `C1_PARTIAL` (for exp_dev; not run here)

### 6.1 Norms on disk for these items -- enumerated, with measured coverage

Coverage counted as *pairs where BOTH members are covered*, over the 3,487-pair usable stratum:

| covariate source | file | words | pairs covered | fraction |
|---|---|---|---|---|
| **Concreteness** `Conc.M` (Brysbaert 2014) | `data/grounding_testbed/Concreteness_ratings_Brysbaert_et_al_BRM.txt` | 39,954 | **3,487** | **1.0000** |
| **Frequency** `BNCFREQ` (ships with SimVerb) | `data/encoder_eval_benchmarks/simverb3500_stats.txt` | 827 | **3,487** | **1.0000** |
| AoA `AoA_Kup` (Kuperman 2012) | `data/grounding_testbed/AoA_51715_words.csv` | 51,715 | 3,473 | 0.9960 |
| Valence/Arousal/Dominance (Warriner 2013) | `data/grounding_testbed/Ratings_Warriner_et_al.csv` | 13,905 | 3,326 | 0.9538 |
| **Imageability** `IMG` (Binder 2016) | `data/corpora/binder/binder2016_ratings.csv` | 486 | **2** | **0.0006** |

**Verdicts:**

- **Concreteness partial: RUNNABLE NOW at full n=3,487, zero coverage loss.** No acquisition needed.
- **Log-frequency partial: RUNNABLE NOW at full n=3,487.** The benchmark ships its own BNC
  frequency, so no corpus counting and no simplewiki budget is required for this covariate.
- **Imageability partial: NOT RUNNABLE.** Binder-535's `IMG` is the only imageability column on disk
  and it covers **2 of 3,487 pairs**. This is a measured verdict, replacing the drill's assumed one.
  Running it requires acquiring the **English Verbs Semantic Norms Database** (3,512 verbs;
  *Behav Res Methods* 2025, `10.3758/s13428-025-02675-6`; on OSF), which is not on disk. That is a
  separate acquisition task and **should be dispatched**, because imageability -- not concreteness
  -- is the variable the aphasia literature actually implicates.

Until it is acquired, the cell must state that **imageability is UNCONTROLLED**, and must not claim
the grammatical-class reading survives an imageability confound. Concreteness and imageability
correlate strongly but are not the same variable; controlling one is not controlling the other.

### 6.2 The exact computation

For each arm independently, over the intersection stratum, with **no zero-fill** (barred):

**Inputs, per pair i:**
- `x_i` = that arm's cosine similarity between the two words' codes (the arm's existing score).
- `y_i` = the gold similarity from `simverb3500.txt` column 4.
- Covariate matrix `Z`, **four columns**:
  - `z1` = mean concreteness = `(ConcM(w1) + ConcM(w2)) / 2`
  - `z2` = **absolute difference** in concreteness = `|ConcM(w1) - ConcM(w2)|`
  - `z3` = mean log-frequency = `(log10(1+BNCFREQ(w1)) + log10(1+BNCFREQ(w2))) / 2`
  - `z4` = **absolute difference** in log-frequency = `|log10(1+f1) - log10(1+f2)|`

**The absolute-difference columns are required, not optional, and this is a deliberate change from
the drill's wording** ("the pair's mean concreteness and mean log-frequency"). The mean alone cannot
capture the confound: a *similarity* instrument is sensitive to how CLOSE two items are on a
covariate, and two words that are both mid-concrete score differently from one concrete and one
abstract word with the same mean. Partialling only the mean leaves the actual confounding channel
in. Include all four.

**Method -- partial Spearman by residualisation:**
1. Rank-transform `x`, `y`, and each column of `Z` independently using **average ranks for ties**
   (ties are pervasive: gold scores and integer-derived covariates both repeat).
2. Regress `rank(x)` on `[1, rank(Z)]` by ordinary least squares; keep the residual `rx`.
3. Regress `rank(y)` on `[1, rank(Z)]` likewise; keep the residual `ry`.
4. `partial_rho = Pearson(rx, ry)`.

Use `numpy.linalg.lstsq` and check the design matrix's condition number; if `z1` and `z3` are
near-collinear, report it rather than silently dropping a column.

**Confidence intervals -- the one place this is easy to get wrong:**
Use the **same paired bootstrap** already used for the raw margin (`FT.boot_rho_diff`,
`N_BOOT=10000`, fixed `BOOT_SEED`, resampling PAIRS with replacement). **The residualisation in
steps 1-3 must be recomputed INSIDE each bootstrap replicate**, on that replicate's resampled rows.
Residualising once outside the loop treats the estimated regression coefficients as known constants
and understates the variance. This is the standard failure mode for bootstrapped partial
correlations and would manufacture a false separation.

**Partial-vs-partial, never partial-vs-raw:**
The four floors (`F_ORTHOGRAPHIC`, `F_FREQUENCY_HARDENED`, `F_CONSTANT_PROTOTYPE`,
`F_SCRAMBLE_PERM_P95`) **must be partialled through the identical covariates on the identical rows**,
and the margin computed as `partial(arm) - max(partial(floors))`. Comparing a partialled treatment
against a raw floor is not a valid margin. Note `F_FREQUENCY_HARDENED` will be strongly attenuated
by construction once frequency is partialled out -- that is correct and expected, and the *strongest*
floor may change identity after partialling. Recompute which floor is strongest; do not assume it is
still the scramble.

**Reporting -- pre-register both, report both whatever they say:**
- Raw rho, partial rho, and the difference, per arm.
- The margin, its bootstrap CI half-width, and the null p95 at that n, for **both** raw and
  partialled versions (a width is not an effect).
- The intersection n after covariate join (expected **3,487**, i.e. no loss) reported explicitly.
- `"imageability_controlled": false` as an explicit field in `metrics.json`, with the coverage
  figure 2/3,487 as its reason.
- Tie conventions, both ways.

**The interpretation, fixed in advance:** our 12-dimension space **contains `Conc.M` as dimension
12**. So partialling concreteness asks whether the space carries verb meaning **beyond its own
concreteness channel**. If `A0`'s verb rho does not survive, the licensing negative was a
concreteness artifact, the noun/verb framing is wrong, and the channel build should not proceed on
its current rationale.

**One recommended addition, flagged as mine and not from the drill.** Add an arm
`A0_MINUS_CONC_11`: the same space with `Conc.M` **removed** (the 11 Lancaster dimensions only). The
partial correlation is a statistical adjustment; dropping the dimension is the structural version of
the identical question, and the two agreeing is much stronger evidence than either alone. It is
width-mismatched to `A0` by one dimension, so it needs the same `N2_RANDOM_GAUSSIAN` width control
the other arms get. Cheap -- no new data.

## 7. WHAT THIS LICENSES

- **Power: SOLVED.** Half-width 0.049 against a 0.145 effect, on 3,317 independent pairs. The
  channel build is licensed on power grounds and `POWER_INSUFFICIENT` is off the table.
- **Confound: OPEN, and now cheap to close.** `C1_PARTIAL` on concreteness and log-frequency is
  runnable today at full n with zero coverage loss. **It should run before, or in the same cell as,
  any channel build** -- it can invalidate the rationale.
- **Imageability: still uncontrolled**, and it is the variable the literature actually implicates.
  Acquisition of the 3,512-verb norms is a separate, small, worthwhile task.
- **Ceiling: 0.61**, verified by recomputation. Quote it beside every SimVerb number. Never quote
  0.84.

## Files

- `data/encoder_eval_benchmarks/simverb3500.txt` (+ dev/test splits, stats, annotator matrix,
  upstream README)
- `data/encoder_eval_benchmarks/PROVENANCE_simverb.md`
- `verification/verify_simverb_ruler_fitness.py`
- `data/simverb_ruler_fitness.json`
