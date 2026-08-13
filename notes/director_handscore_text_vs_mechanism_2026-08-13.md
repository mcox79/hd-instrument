# Director hand-score: TEXT vs MECHANISM, NEWS arm vs TEXTBOOK arm (2026-08-13)

**Scorer:** Director, single judge, BLIND (arm labels stripped, shuffle seed 42), one sitting.
Sample: `data/exp_grounding_text_vs_mechanism/blind_sample.json` (100 rows = 2 arms x 50),
sheet `data/exp_grounding_text_vs_mechanism/SCORING_SHEET.txt`, key
`data/exp_grounding_text_vs_mechanism/arm_key.json` (unsealed only after scoring).
Pre-reg: `preregs/2026-08-13_grounding_text_vs_mechanism.md`.
Join: 100/100 rows matched on sheet index -> `blind_id` with subject AND object agreeing --
**zero join failures**, arms **exactly 50/50** as designed (NEWS 50, TEXTBOOK 50).

## RESULT: the corpus swap did NOT buy meaning

| arm | corpus | MEANINGFUL | RELATED | NOISE | n | banked facts |
|---|---|---|---|---|---|---|
| NEWS | OneStopEnglish Ele+Int+Adv | **4%** (2/50) | 20% (10/50) | 76% (38/50) | 50 | 387 |
| TEXTBOOK | OpenStax bio_2e / a&p_2e / psych_2e / micro / chem_2e | **0%** (0/50) | 30% (15/50) | 70% (35/50) | 50 | 212 |
| **pooled** | -- | **2%** (2/100) | **25%** (25/100) | **73%** (73/100) | 100 | 599 |

MEASURED@`data/exp_grounding_text_vs_mechanism/metrics.json:per_arm` for fact counts and corpora;
buckets from the Director's sheet joined to `arm_key.json`.

Matched N held: 20,394 sentences read per arm (S4 ok). Equal sentences, unequal yield -- TEXTBOOK
banked 212 facts to NEWS's 387, with refusals 7,899 vs 20,058.

### Pre-registered bands, quoted verbatim (prereg sec 3)

> Primary statistic: **MEANINGFUL rate on the TEXTBOOK arm.**
>
> - **TEXT_HYPOTHESIS_SUPPORTED** -- MEANINGFUL >= 0.20. A >5x rise over tonight's 2-4% means the
>   text was the binding constraint.
> - **MIXED** -- MEANINGFUL in [0.10, 0.20).
> - **MECHANISM_IS_BINDING** -- MEANINGFUL < 0.10 **AND** RELATED materially above the NEWS arm
>   (>= +0.10 absolute). Better text buys topical adjacency but NOT meaning. Pre-declared,
>   expected, fully acceptable.
> - If MEANINGFUL < 0.10 and RELATED is NOT above NEWS by >= 0.10, the outcome is
>   **NULL_NO_TEXT_EFFECT** (the corpus swap moved nothing at all); it licenses no claim about
>   which hypothesis is right, only that this manipulation failed to discriminate.

**Primary discriminator value: MEANINGFUL(TEXTBOOK) = 0/50 = 0.0000.**
Second clause: RELATED(TEXTBOOK) - RELATED(NEWS) = 15/50 - 10/50 = **+0.1000**, exactly the
>= +0.10 threshold.

**BAND: MECHANISM_IS_BINDING.** Both clauses are met on the letter of the prereg
(0.0000 < 0.10; +0.1000 >= +0.10).

Honest caveat on the second clause, stated because it is one row wide: the RELATED gap is exactly
5 rows. Fourteen RELATED rows in TEXTBOOK instead of fifteen gives +0.08 and the outcome would
have been NULL_NO_TEXT_EFFECT. The prereg's own power note ("differences below ~0.10 are
unresolvable") puts +0.10 at the resolution limit, ~1.1 SE of the difference (SE 0.0886). The
FIRST clause is not marginal in any reading: TEXTBOOK MEANINGFUL is zero, and both candidate
bands (MECHANISM_IS_BINDING, NULL_NO_TEXT_EFFECT) agree that the TEXT hypothesis failed. Nothing
here reaches MIXED, let alone TEXT_HYPOTHESIS_SUPPORTED.

### Secondary, reported not gated (prereg sec 3.1)

| arm | RELATED rate | MEANINGFUL:RELATED |
|---|---|---|
| NEWS | 0.20 | 2:10 = 0.20 |
| TEXTBOOK | 0.30 | 0:15 = 0.00 |

Under hypothesis (A) the ratio shifts toward MEANINGFUL. It moved the other way: TEXTBOOK is
purely adjacency, with no MEANINGFUL rows at all. This is the (B)-shaped outcome the prereg
pre-declared as expected and acceptable.

## THE PRIOR HYPOTHESIS -- **REFUTED**

The claim under test, from a post-hoc n=17 observation in
`notes/director_handscore_readout_v1_2026-08-13.md`: OpenStax-Biology rows score
9/17 = **52.94%** MEANINGFUL+RELATED vs OneStopEnglish news 13/81 = **16.05%**,
Fisher exact p = 0.0024, OR 5.88. That doc recorded the hypothesis as VERIFIED.

This cell is the proper pre-registered, matched-N, one-variable test of it. Side by side:

| | expository/textbook | news | delta | Fisher p | OR | design |
|---|---|---|---|---|---|---|
| prior (readout_v1) | 9/17 = **0.5294** | 13/81 = **0.1605** | **+0.3689** | 0.0024 | 5.88 | post-hoc split of an already-scored sample, n=17 |
| **this cell** | 15/50 = **0.3000** | 12/50 = **0.2400** | **+0.0600** | **0.6529** | **1.357** | pre-registered, blind, matched N=20,394 sentences/arm, n=50/arm |

**VERDICT: REFUTED.** The 52.9%-vs-16.0% result does not replicate. Under pre-registration the
textbook advantage on MEANINGFUL+RELATED collapses from +36.9 points to +6.0 points, an odds
ratio of 1.36 against 5.88, and p = 0.6529 -- indistinguishable from no effect. The textbook arm's
30% is well below the prior 52.9%; the news arm's 24% is well above the prior 16.1%; the two
segments have largely converged. Stated plainly and without softening: **switching the corpus from
news to textbook did not raise grounded-meaning quality, and the earlier enrichment claim does not
survive a matched test.**

Why the earlier figure was weaker by design: it came from slicing a sample the Director had
already scored, choosing the cut after seeing the buckets, on n=17 in the bio cell (95% CI on
9/17 roughly 0.28-0.77 -- which contains this cell's 0.30). It was never a matched comparison:
the segments there differed in volume, reading order and position in the growth curve, not only
in genre. One further difference of scope: the prior bio_new segment was OpenStax *Concepts of
Biology* alone, whereas this TEXTBOOK arm draws on five OpenStax titles (biology_2e,
anatomy_physiology_2e, psychology_2e, microbiology, chemistry_2e). If someone wants to argue that
*Concepts of Biology* specifically is special, that is a new, narrower, still-untested claim -- it
is not what the prior doc asserted, and it is not licensed by anything measured here.

## FLOOR CHECK -- the MEANINGFUL measure is UNDERPOWERED BY FLOOR

Two MEANINGFUL rows exist in the entire 100-row pooled sample, and both fell in NEWS.

- Maximum attainable value of the primary statistic, MEANINGFUL(TEXTBOOK), given a supply of 2
  MEANINGFUL rows pooled: **2/50 = 0.04.** That is below the MIXED floor (0.10) and far below
  TEXT_HYPOTHESIS_SUPPORTED (0.20). Even in the most extreme allocation -- both MEANINGFUL rows
  landing in TEXTBOOK -- the cell **could not have reached MIXED, let alone supported the text
  hypothesis.**
- Maximum attainable |delta| between arms on MEANINGFUL: **2/50 = 0.04.**

> **UNDERPOWERED BY FLOOR on MEANINGFUL** -- the same condition that made
> `exp_grounding_quality_readout_v1` non-discriminating (there: 3 MEANINGFUL rows, max attainable
> |delta| 0.06, inside its own NULL band). The correct reading of "TEXTBOOK MEANINGFUL = 0%" is
> NOT "textbooks are worse than news." It is: **the read-out emits almost no MEANINGFUL output on
> either corpus, so the MEANINGFUL channel had no signal for the corpus swap to move.** The
> pre-registered bands were reachable only via the RELATED clause, and that is the clause the
> verdict actually turned on.

**Does the secondary MEANINGFUL+RELATED measure escape the floor? Partly -- yes.** 27 pooled rows
(2 M + 25 R) give it real room: the maximum attainable |delta| on M+R is 27/50 = 0.54, more than
13x the MEANINGFUL ceiling, so an effect of the prior claim's size (+0.37) was fully detectable
here and did not appear. Observed delta **+0.0600** (TEXTBOOK 0.30 - NEWS 0.24), SE of the
difference 0.0886, i.e. **0.68 SE** -- inside binomial noise, and below the prereg's declared
~0.10 resolution. So M+R escapes the floor in the sense that the test COULD have fired and did
not; it licenses the negative statement (no textbook advantage of the claimed magnitude) and
nothing positive.

**Caveat that must travel with the M+R measure:** RELATED is the WEAKER criterion. It certifies
topical adjacency, not reference -- `irv -> air`, `bubonic -> black`, `gradient -> high` are all
RELATED and none of them is a meaning. Every one of the 15 TEXTBOOK non-NOISE rows is RELATED.
Reading a textbook advantage off M+R would be reading it off exactly the bucket that (B) predicts
better text should inflate. That is why the prereg made MEANINGFUL primary and left M+R ungated.

## RECONCILIATION WITH THE CO-OCCURRENCE CONTROL

MEASURED@`data/exp_grounding_text_vs_mechanism/metrics.json:cooccurrence_control_per_arm`:

| arm | either_top1 | floor | top5 containment | floor | band |
|---|---|---|---|---|---|
| NEWS | 0.12 | 0.02 | 0.44 | 0.04 | **COOC_PARTIAL** (top5 in [0.40,0.70), above floor) |
| TEXTBOOK | 0.04 | 0.00 | 0.20 | 0.02 | **COOC_DOES_NOT_EXPLAIN** (top1 < 0.20 AND top5 < 0.40) |

The combined picture, in one paragraph. The output is largely NOISE on both corpora (73% pooled,
and 0% MEANINGFUL on the textbook arm), and at the same time it is NOT what a plain sentence-window
co-occurrence baseline predicts: on the textbook arm the substrate's object matches the PMI-or-
frequency argmax on 2 rows in 50 and sits in the top-5 on 10 in 50, which is the pre-registered
COOC_DOES_NOT_EXPLAIN band; on the news arm it is COOC_PARTIAL, reproducible in top-5 about
44% of the time but at top-1 only 12%. So the naive reading of hypothesis (B) -- "the read-out IS
a co-occurrence table" -- is not supported as a literal account, most clearly on the arm where
quality is worst. What is explicitly **NOT ruled out** is the general form of (B): a DIFFERENT
MEANING-FREE MECHANISM. Sentence-window PMI/frequency is only one such mechanism. The read-out
operates over an accumulated ConceptSpace with chunk-level context vectors, decay and
attestation weighting -- a distributional-similarity process whose statistics differ from a flat
per-sentence co-occurrence count while still containing no reference relation. Failing to
reproduce the output from PMI narrows WHICH meaning-free mechanism is at work; it does not show
that the mechanism tracks meaning. Nothing measured here distinguishes "wrong distributional
statistic" from "right statistic, wrong kind of relation."

## FAILURE EXAMPLES -- the shape of the 73% NOISE

- `vesicle -> wonder` (row 072, TEXTBOOK, cos 0.3672, 24 attestations) -- context:
  *"A vesicle is a membranous sac-a spherical and hollow organelle bounded by a lipid bilayer
  membrane"*. The sentence is an explicit copular definition, printed on the sheet, and states the
  answer: a vesicle is a sac. The read-out returned `wonder`. This single row is the cleanest
  refutation of the text hypothesis in the sample -- the text supplied the definition and the
  mechanism did not take it.
- `bronchiole -> beat` (row 013, TEXTBOOK, cos 0.7578, 20 attestations) -- context:
  *"5 mm are the respiratory bronchioles"*. Highest cosine among the quoted rows, and the object is
  unrelated to the anatomy. Cosine does not separate the buckets.
- `erythrocyte -> body` (row 084, TEXTBOOK, cos 0.3359, 6 attestations) -- context:
  *"Hemoglobin, or Hb, is a protein molecule found in red blood cells (erythrocytes) made of four
  subunits..."*. The parenthetical gloss "red blood cells (erythrocytes)" is present in the
  sentence; the read-out landed on the most generic available noun.
- `nutrient -> cute` (row 036, NEWS, cos 0.7891, 6 attestations) -- context:
  *"Never mind how cute a panda is or how stunning a tiger ... it's worms that are grinding up our
  waste and taking it deep into the soil to turn into nutrients"*. Same-sentence adjacency to an
  adjective at cos 0.79.

## HIT EXAMPLES -- both MEANINGFUL rows in the sample

- `quinn -> elizabeth` (row 045, **NEWS**, cos 0.3304, 6 attestations) -- context:
  *"Elizabeth Gallagher, who calls herself Quinn, replied to an online posting from Axani and she
  was chosen"*. Correct identity resolution for an alias, stated explicitly in the sentence.
- `konstantinos -> agent` (row 096, **NEWS**, cos 0.3789, 6 attestations) -- context:
  *"...said Atzamis Konstantinos, a travel agent in Lemnos who used to earn..."*. Correct type
  assignment for a proper noun from an appositive.

Both MEANINGFUL rows are proper-noun cases from an explicit appositive or alias construction, and
both are in the NEWS arm. The TEXTBOOK arm produced no MEANINGFUL row of any kind. Note the
inversion this creates against the text hypothesis: the technical terms whose definitions are
spelled out in the corpus (`vesicle`, `erythrocyte`) failed, while the two successes are ordinary
news appositives.

## LIMITS

Single judge, one sitting, label-blind. n=50 per arm; the prereg declares differences below ~0.10
unresolvable and the MEANINGFUL floor makes even that generous. **The blind is PARTIAL and this is
declared in the prereg (sec 6): the corpus IS the variable, so the printed context sentence reveals
the genre.** The hand-score is GENRE-VISIBLE-BUT-LABEL-BLIND; the co-occurrence control is the
label-free, machine-computed evidence in this cell. One pass, one seed per arm, no variance
estimate. The arms differ in vocabulary, sentence length and repetition as well as in expository
density, so "textbooks do not help" here cannot be separated from "textbook genre statistics do
not help" (prereg sec 8). The read-out is noun-only upstream, so no verb meaning was reachable in
either arm.

## SCOPE -- what this licenses and what it does NOT

**This measures the SUBSTRATE'S OWN `GROUNDED_MEANING` READ-OUT on text it read** -- a live PBV
reading pass proposing a meaning per encounter from a growing ConceptSpace, at the current default
read-out configuration (`readout=None`, `freeze_episode=False`; F1+F3 OFF and not varied here).
Nothing in this cell is banked, wired or written to any canonical foundation path
(`wire_status: EXPERIMENT_LOCAL_NOT_WIRED`); growth remains paused.

LICENSED:
1. On matched N, the read-out is 4% M / 20% R / 76% N on news and 0% M / 30% R / 70% N on
   OpenStax textbook prose.
2. The pre-registered band is MECHANISM_IS_BINDING (MEANINGFUL(TEXTBOOK) 0.0000 < 0.10; RELATED
   +0.1000 >= +0.10), with the second clause exactly at threshold and at the declared resolution
   limit; the first clause is unambiguous.
3. The prior 52.9%-vs-16.0% expository-enrichment claim is REFUTED under pre-registration
   (+0.06, p=0.6529, OR 1.36).
4. The substrate's output is not reproducible from a plain sentence-window co-occurrence baseline
   on the textbook arm (COOC_DOES_NOT_EXPLAIN) and only partially on the news arm (COOC_PARTIAL).

**NOT LICENSED:**
- **No cross-comparison with the definitional-extraction parsers.** The v5 term-boundary
  hand-score, the predicate v6 hand-score and the v6.1 hand-score come from hand-written parsers
  SUPPLYING facts from surface syntax. This number comes from the substrate's own distributional
  read-out ACQUIRING a meaning. They are not on one scale and no ratio, delta or "gap" between
  them is meaningful. **Nowhere in this document are those numbers compared to these.**
- No claim that textbooks are WORSE than news: MEANINGFUL is floor-limited (max attainable 0.04)
  and the M+R difference is 0.68 SE.
- No claim that the mechanism is a co-occurrence table -- the control says it is not, literally.
- No claim about which meaning-free mechanism IS operating; that is unidentified.
- No claim that a larger textbook dose, a different textbook, or a different read-out
  configuration would behave this way -- none were run.
- No claim about the canonical foundation: nothing here is banked or wired.

## DISPOSITION

The TEXT route -- "swap the corpus to dense expository prose and the read-out will find meanings"
-- is **CLOSED as a standalone remedy**. It was the one empirical lead handed over by
`notes/director_handscore_readout_v1_2026-08-13.md`, it was tested pre-registered and matched, and
it did not survive. The binding constraint remains the PROPOSER'S METRIC: distributional
relatedness is not reference, and `vesicle -> wonder` on a sentence that says a vesicle is a sac
is the cleanest evidence in this sample that the text was never the limiting ingredient.
