# Director hand-score: grounding-quality READ-OUT sample, PBV_BASE vs PBV_F1F3 (2026-08-13)

**Scorer:** Director, single judge, BLIND (arm labels stripped, shuffle seed 42), one sitting.
Sample: `data/exp_grounding_quality_readout_v1/blind_sample.json` (100 rows = 2 arms x 50),
sheet `data/exp_grounding_quality_readout_v1/SCORING_SHEET.txt`, key
`data/exp_grounding_quality_readout_v1/arm_key.json` (unsealed only after scoring).
Pre-reg: `preregs/2026-08-12_grounding_quality_readout_v1.md`.
Join: 100/100 rows matched on `blind_id` with subject/object/fid agreeing -- **zero join failures**,
arms **exactly 50/50** as designed.

## RESULT: NULL -- and the null is FLOOR-LIMITED, not a clean matched null

| arm | MEANINGFUL | RELATED | NOISE | n | banked facts |
|---|---|---|---|---|---|
| PBV_BASE | **2%** (1/50) | 24% (12/50) | 74% (37/50) | 50 | 384 |
| PBV_F1F3 | **4%** (2/50) | 14% (7/50) | 82% (41/50) | 50 | 369 |
| **pooled** | **3%** (3/100) | **19%** (19/100) | **78%** (78/100) | 100 | -- |

**Pre-registered discriminator** = MEANINGFUL(PBV_F1F3) - MEANINGFUL(PBV_BASE)
= 0.04 - 0.02 = **+0.0200**.

Bands applied verbatim (prereg sec 3): HARD_PASS delta >= +0.20 AND F1F3 >= 0.25 -- not met
(delta +0.02, F1F3 0.04). MIDDLE_BAND [+0.08, +0.20) -- not met. HARD_FAIL_HURTS <= -0.08 --
not met. **|delta| = 0.02 < 0.08 -> NULL.**

Secondary, reported not banded: MEANINGFUL+RELATED delta = 0.18 - 0.26 = **-0.0800** (F1F3 lower).
At n=50/arm this is inside binomial noise (SE ~0.08) and the prereg declares nothing finer than
0.20 resolvable, so it licenses **no** claim that F1+F3 hurts. It does licence the negative
statement that no positive quality signal is visible on either bucket.

### THE FLOOR EFFECT -- state this before anyone reads "NULL" as "the arms are equivalent"

Three MEANINGFUL rows exist in the entire 100-row sample. Even in the most extreme allocation
(all 3 in one arm, 0 in the other) the discriminator could only have reached
**3/50 - 0/50 = 0.06**, which is INSIDE the NULL band. The experiment therefore
**could not have produced any non-NULL verdict** given the observed MEANINGFUL supply.

> **UNDERPOWERED BY FLOOR.** Both arms are pinned at the noise floor (2% and 4% against a
> v2 DIST reference of 8%), so the comparison is non-discriminating by construction. The correct
> reading is NOT "read-out stabilization is neutral, all is well." It is: **the read-out's output
> is nearly all noise in both configurations, and read-out stability cannot be shown to matter
> because there is no quality signal for it to move.** The prereg's sec 3.1 disposition -- keep
> F1+F3 as a stability knob, default OFF, stop spending on read-out stability as a quality route
> -- stands, but it is reached by a floor, not by a matched null.

### S8 ADMISSION-DRIFT CAVEAT -- the retention-matched claim is VOID

MEASURED@`data/exp_grounding_quality_readout_v1/metrics.json:structural_gates.S8_f1_admission_drift`:

| quantity | value |
|---|---|
| matched-retention cited (threshold's calibration point) | 0.403405 |
| PBV_BASE admission rate | 0.317547 |
| PBV_F1F3 admission rate | 0.165153 |
| drift | **-0.238252** |
| retention_ratio F1F3/BASE | 0.520090 |
| `retention_match_holds` | **False** |

Drift far exceeds the 0.10 that voids the retention-matched claim, so per S8's own note the
sec 3.2 interpretive cap applies: any quality delta from this run is **capped at MIDDLE_BAND**
regardless of size. The F1F3 arm admitted roughly half the encounters BASE did, which is exactly
the selectivity confound that made F2 look load-bearing. Moot here (the verdict is below the cap),
but it means a re-run of this comparison at a genuinely matched operating point is a DIFFERENT
experiment, not a repeat.

The sec 3.2 **fact-count** ratio is separately clean:
`n_facts(F1F3)/n_facts(BASE) = 369/384 = 0.960938`, inside [0.5, 2.0] -- **no cap from that
clause**. The two arms banked near-identical fact counts while admitting very different encounter
volumes.

S5 positive control PASSED: PBV_BASE confirm rate 0.066779 vs PBV's cited 0.100561 (|diff| 0.0338
< 0.05 tolerance), `confirm_rate_calibrated = true`. PBV_F1F3's confirm rate rose to 0.129654 --
per prereg sec 5 this is expected from F1 being a gate and is **not** evidence of better meanings.
The hand-score says it is not: quality did not move.

## SEGMENT ANALYSIS -- the Director's technical-vs-news hypothesis, TESTED

Provenance (verified in code, not assumed): `bio_new` = OpenStax *Concepts of Biology*
(`experiments/exp_definitional_grounding_v5.py:load_biology_sentences_lineaware`,
`data/corpora/textbook_concepts_biology/cleaned/concepts_biology.clean.txt`);
`ele_cont` / `int_cont` / `adv_new` = OneStopEnglish news at Ele/Int/Adv reading levels
(`experiments/exp_reading_grounding_loop_cycle2_v1.py:SEGMENT_POOL_LOADERS`);
`bootstrap` = cycle-1 curriculum pool.

| segment | source | n | M | R | N | MEANINGFUL+RELATED |
|---|---|---|---|---|---|---|
| **bio_new** | OpenStax Biology | 17 | 1 | 8 | 8 | **9/17 = 52.94%** |
| ele_cont | OneStop news (Ele) | 18 | 0 | 4 | 14 | 4/18 = 22.22% |
| int_cont | OneStop news (Int) | 21 | 0 | 3 | 18 | 3/21 = 14.29% |
| adv_new | OneStop news (Adv) | 42 | 2 | 4 | 36 | 6/42 = 14.29% |
| bootstrap | curriculum pool | 2 | 0 | 0 | 2 | 0/2 = 0.00% |

Collapsed by provenance:

| provenance | M+R | rate |
|---|---|---|
| OpenStax-Biology-derived (`bio_new`) | 9/17 | **0.5294** |
| OneStopEnglish-news-derived (`ele_cont`+`int_cont`+`adv_new`) | 13/81 | **0.1605** |
| whole sample | 22/100 | **0.2200** |

Fisher exact on [[9,8],[13,68]]: odds ratio 5.88, **p = 0.0024**.

**VERDICT ON THE HYPOTHESIS: VERIFIED.** The Director's rough estimate of ~53% technical vs 22%
overall lands on 52.94% vs 22.00% off disk -- a 3.3x enrichment over news-derived rows and not
a sampling accident at p=0.0024. Caveats that keep it honest: n=17 for bio_new (95% CI on 9/17 is
roughly 0.28-0.77); and this is MEANINGFUL+RELATED, driven by RELATED (8 of the 9) -- the
MEANINGFUL count in bio_new is 1. The enrichment is real; what it buys is *topical relatedness*,
not yet reference. Both arms show it (bio_new M+R: BASE 4/7, F1F3 5/10), so it is a property of
the TEXT, not of the read-out configuration.

## FAILURE EXAMPLES -- the shape of the 78% NOISE

- `whisky -> wedding` (row 016, PBV_BASE, int_cont, cos 0.4475) -- "nine cases of Japanese whisky
  ... for a wedding reception". Co-occurrence in one narrated event, read as meaning.
- `aphotic -> marry` (row 011, PBV_F1F3, bio_new, cos 0.1875) -- "the lake or pond becomes aphotic
  and photosynthetic plants cannot survive". A technical term collapsed onto an unrelated verb.
- `confidence -> talking` (row 015, PBV_F1F3, adv_new, cos 0.2189) -- abstract noun pulled to a
  generic speech verb; the context sentence is a quotation frame.
- `banana -> people` (row 086, PBV_BASE, int_cont, cos 0.4219) -- highest-frequency co-occurring
  animate noun wins.
- `checklist -> joe` (row 021, PBV_BASE, adv_new, cos 0.3451) -- "went through a checklist of 40
  things with his mentor Joe Kittinger". A proper name adjacent in one sentence.

The common mechanism is the one the prereg predicted (sec 3.1): the PROPOSER'S METRIC is
distributional relatedness, and distributional relatedness is not reference. Note that cosine does
not separate the buckets -- the worst rows above carry cos 0.42-0.45 while the best row below
carries 0.2431.

## HIT EXAMPLES -- all three MEANINGFUL rows plus the best RELATED

- `plasma -> bilayer` (row 047, **PBV_F1F3**, bio_new, cos 0.2431, 94 attestations) -- "A particle
  enveloped in membrane fuses with the interior of the plasma membrane". The only technically
  correct meaning in the sample, and it comes from the most-attested row in it.
- `ninian -> school` (row 036, **PBV_BASE**, adv_new, cos 0.3241, 8 attestations) -- "At St
  Ninian's, teachers take their pupils out of lessons ... around the school's playing field".
  Correct type assignment for a proper noun.
- `hitting -> beat` (row 003, **PBV_F1F3**, adv_new, cos 0.2734, 4 attestations) -- a genuine
  verb-sense match.
- `synthase -> plasma` (row 018, PBV_F1F3, bio_new, RELATED) -- right domain, wrong referent;
  representative of the bio_new RELATED band that drives the segment effect.

Two of three MEANINGFUL rows fall in F1F3 and one in BASE: that is the entire basis of the +0.02,
and it is one row of difference.

## LIMITS

Single judge, one sitting, blind to arm. n=50 per arm; the prereg pre-declared that nothing below
delta 0.20 is resolvable at 2 SE, and the observed floor makes even that generous. Segment cells
are small (bio_new n=17, bootstrap n=2). The F1F3 arm ran at an admission rate 0.238 below its
calibration point, so it is not the retention-matched configuration the threshold was chosen for.

## SCOPE -- what this licenses and what it does NOT

**This measures the SUBSTRATE'S OWN `GROUNDED_MEANING` READ-OUT on text it read** -- a live PBV
reading pass proposing a meaning per encounter from a growing ConceptSpace, with the read-out
either legacy (`readout=None`, freeze off) or F1+F3 (`operating_readout()`, episode freeze on).

LICENSED:
1. On this corpus, the read-out's meanings are 3% MEANINGFUL / 19% RELATED / 78% NOISE.
2. Read-out stabilization (F1+F3) does not measurably improve them: delta +0.02, NULL band --
   and the sample could not have shown otherwise, so the honest statement is "no quality signal
   was available for stability to move," not "stability is neutral."
3. Grounding QUALITY, not read-out stability, is the binding constraint. Argmax stability was
   confirmed to improve (landed-VET, -0.168 flip at matched retention); meaning did not follow.
4. Expository/technical text yields 3.3x the M+R rate of news text on the SAME read-out
   (52.94% vs 16.05%, p=0.0024) -- a property of the source text, not of the mechanism.

**NOT LICENSED -- do not cross-compare:**
- This is a **DIFFERENT PIPELINE** from definitional extraction. The 64% v5 term-boundary
  hand-score and the 70% predicate hand-score come from **hand-written parsers SUPPLYING facts**
  from surface syntax. This number comes from the substrate's own distributional read-out
  ACQUIRING a meaning. The two are not on one scale and no ratio, delta, or "gap" between them is
  meaningful. The prereg refused that comparison in advance (sec 2, sec 8 item 2) and it is
  refused here. **Nowhere in this document is this 3% compared to those numbers.**
- No claim about F1+F3 HURTING quality (the -0.08 M+R delta is inside binomial noise).
- No retention-matched claim of any kind (S8 drift -0.238252).
- No claim that the bio_new enrichment would hold at scale (n=17).
- No claim about the confirm-rate rise (0.0668 -> 0.1297) meaning anything about quality; the
  prereg refuses that inference and the hand-score independently contradicts it.

## DISPOSITION

Read-out stabilization as a route to better meanings is **CLOSED**. Keep F1+F3 wired default-OFF
as a stability knob (192521a7f). The next binding question is the PROPOSER'S METRIC -- reference
rather than distributional relatedness -- and the one empirical lead this sample hands over is
that dense expository text is where the read-out is least wrong.
