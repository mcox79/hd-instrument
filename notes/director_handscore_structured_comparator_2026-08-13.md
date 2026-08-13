# Director hand-score: structured-comparator ablation, CONTROL vs STRUCTURED (2026-08-13)

**Scorer:** Director, single judge, BLIND (arm labels sealed, shuffle seed 42), one sitting.
Sample: `data/exp_structured_comparator_v1/blind_sample.json` (100 rows = 2 arms x 50),
sheet `data/exp_structured_comparator_v1/SCORING_SHEET.txt`, key
`data/exp_structured_comparator_v1/arm_key.json` (unsealed only after scoring).
Pre-reg: `preregs/2026-08-13_structured_comparator_ablation.md`.
Cell metrics: `data/exp_structured_comparator_v1/metrics.json`.

**Join:** 100/100 sheet rows matched on `blind_id` (sheet index = `blind_id` + 1) with
subject/object agreeing against BOTH `arm_key.json` and `blind_sample.json` --
**zero join failures**, arms **exactly 50/50** as designed.

---

## RESULT: NULL -- and, as in the previous cell, the null is FLOOR-LIMITED

| arm | MEANINGFUL | RELATED | NOISE | n | banked facts |
|---|---|---|---|---|---|
| CONTROL (`context_vector_masked`) | **2%** (1/50) | 24% (12/50) | 74% (37/50) | 50 | 384 |
| STRUCTURED (`structural_vector_masked`) | **0%** (0/50) | 10% (5/50) | 90% (45/50) | 50 | 374 |
| **pooled** | **1%** (1/100) | **17%** (17/100) | **82%** (82/100) | 100 | -- |

### Bands applied verbatim

Quoted from `preregs/2026-08-13_structured_comparator_ablation.md` sec 4:

> `delta = MEANINGFUL(STRUCTURED) - MEANINGFUL(CONTROL)`
>
> | band | criterion |
> |---|---|
> | **STRUCTURAL_FIX_WORKS** | `MEANINGFUL(STRUCTURED) >= 0.15` AND `delta >= +0.10` |
> | **PARTIAL** | `delta` in `[+0.05, +0.10)` |
> | **NULL** | `abs(delta) < 0.05` -- pre-declared acceptable and genuinely possible |
> | **HURTS** | `delta <= -0.05` |

Observed `delta = 0.0000 - 0.0200 = **-0.0200**`.

* STRUCTURAL_FIX_WORKS -- not met (STRUCTURED 0.00 < 0.15; delta -0.02 < +0.10).
* PARTIAL -- not met (delta is negative).
* HURTS -- **not met** (-0.02 > -0.05). The observed direction is negative but does not reach
  the HURTS threshold, and see the floor analysis: it cannot, arithmetically.
* **`abs(delta) = 0.02 < 0.05` -> VERDICT: NULL.**

---

## THE FLOOR ANALYSIS -- read this before reading "NULL" as "the arms are equivalent"

**ONE MEANINGFUL row exists in the entire 100-row pooled sample.** With a supply of 1, the
maximum attainable `abs(delta)` over ANY allocation is `1/50 - 0/50 = **0.02**`.

The prereg's own power section (sec 4.1) declared:

> **Minimum detectable delta at 2 SE = +0.11** (i.e. STRUCTURED must reach about 0.14).

**0.02 is 5.5x below the cell's own declared minimum detectable delta. The cell could not have
returned a non-NULL verdict at any allocation of the MEANINGFUL rows it produced.**

### The prereg's power argument FAILED, and this is the design lesson

Sec 4.1 argued explicitly that this cell had fixed the previous cell's defect:

> **For the primary STRUCTURAL_FIX_WORKS band the design CAN return a positive, and this is the
> specific defect it fixes relative to the previous cell.** The 2026-08-12 read-out cell was
> floor-limited: both arms were pinned at 2-4%, so the maximum attainable delta was 3/50 - 0/50 =
> 0.06, INSIDE its own NULL band -- it could not have returned a non-NULL verdict at any
> allocation. Here only CONTROL is pinned; STRUCTURED is unconstrained upward. [...]
> The floor pathology does not recur.

**It recurred, and worse.** `exp_grounding_quality_readout_v1` had 3 pooled MEANINGFUL rows
(max `abs(delta)` 0.06); this cell has 1 (max `abs(delta)` 0.02). The reasoning "only CONTROL is
floor-pinned, so STRUCTURED is free to rise" is not a power argument -- it is a restatement of the
hypothesis. If H1 is false, the treatment arm floors too, and then the discriminator has no range.
A discriminator whose resolution is contingent on the hypothesis being true cannot adjudicate the
hypothesis.

> **DESIGN LESSON, general:** a hand-scored MEANINGFUL discriminator cannot resolve anything
> while the underlying generator sits at 1-3% MEANINGFUL. At n=50/arm the MEANINGFUL supply, not
> the mechanism, sets the measurable range. Do not gate a cell on a MEANINGFUL delta until the
> generator clears roughly 10%; before that, gate on a mechanistic discriminator that has range
> by construction (as sec 5 of this prereg did, correctly -- see below).

### Does the secondary MEANINGFUL+RELATED measure escape the floor? YES -- and it is negative

18 pooled rows, so it has range.

| arm | M+R | rate |
|---|---|---|
| CONTROL | 13/50 | **0.2600** |
| STRUCTURED | 5/50 | **0.1000** |

`delta(M+R) = 0.1000 - 0.2600 = **-0.1600**`. SE at these proportions and n=50/arm is 0.0752, so
`z = -2.13`; Fisher exact two-sided on [[13,37],[5,45]] gives **p = 0.0664**.

This measure is NOT pre-registered as a band and is reported, not banded. Read it with the two
standing caveats:

1. **RELATED certifies ADJACENCY, not REFERENCE.** A drop in M+R means the STRUCTURED arm's
   outputs are less topically adjacent to their subjects. It does not establish that they are
   worse *meanings*, because neither arm produced meanings at any measurable rate.
2. It is a single judge, one sitting, at p = 0.066 -- suggestive, not established.

The honest statement is: **on the one measure with range, structure moved the outputs AWAY from
topical adjacency without moving them TOWARD reference.** That is exactly what a comparator does
when it changes what is compared and the new thing compared is not more meaningful.

---

## THE MECHANISTIC RESULT -- this is the real finding

The comparator **DID bind**. All numbers off `data/exp_structured_comparator_v1/metrics.json`.

| witness | value |
|---|---|
| argmax disagreement, both encoders over the same 3,992-sentence slice | **6145 / 6283 = 0.9780** |
| co-occurrence agreement top1, CONTROL | 0.075521 |
| co-occurrence agreement top5, CONTROL | 0.255208 |
| co-occurrence agreement top1, STRUCTURED | 0.024064 |
| co-occurrence agreement top5, STRUCTURED | **0.074866** |
| `binding_check` | **DIVERGED** |
| S4 `control_reproduces_reference` | **true** (384 facts, digest `836571fa99d5765d`) |
| S3 arms-differ | true (STRUCTURED digest `1ce97a59c1b613d2`) |
| STRUCTURED parse coverage | 31,290 parsed / 124 skipped; 207,138 encodings, 2.726 mean features |

The prereg's sec 5 non-binding rule was:

> **If `cooc_agreement_top5(STRUCTURED) >= cooc_agreement_top5(CONTROL) - 0.05`, the structured
> comparator DID NOT BIND, and that is the headline finding REGARDLESS of the hand-score.**

0.0749 vs 0.2552 - 0.05 = 0.2052. The rule does not fire. The comparator bound, and bound hard:
role-bound dependency features cut agreement with a plain co-occurrence baseline to **29% of
CONTROL's at top5** (0.0749 / 0.2552) and **32% at top1**.

### Reconciliation, stated plainly

**The comparator changed WHAT is compared, moved sharply away from co-occurrence, and did NOT
improve meaning.** CONTROL is verified to be the exact shipped reference (S4 true), so the
comparison is against a known baseline, not a re-implementation. Structure-alone is therefore
**not sufficient** to convert a distributional read-out into a referential one: removing
topical co-occurrence removed the *wrong* answers of one kind and supplied no *right* answers.

### What this does NOT rule out

1. **It does not rule out structure being NECESSARY.** A necessary ingredient shows no effect
   when another necessary ingredient is absent. This cell tests sufficiency of one swap.
2. **It does not rule out a RICHER structural representation.** The prereg declared two costs in
   advance (sec 3.1), both biasing AGAINST the structured arm and neither corrected for:
   * **Starvation.** STRUCTURED sees 2.86 features/encounter vs CONTROL's 11.33 (median 3 vs 11;
     zero-feature rate 0.0214 vs 0.0017) over 7,740 sampled (sentence, target) pairs. ~4x less
     evidence per encounter. The prereg names this in advance as the leading alternative
     explanation for a null: "structure was starved", not "structure is irrelevant".
   * **Out-of-domain parse noise.** The UD front-end is trained on UD EWT web text and run on
     news + OpenStax biology. It is visibly wrong on the very sentence it was probed on --
     `whisky` is mistagged SCONJ and attached as `mark` to `costing`. Parse noise degrades
     STRUCTURED only and never touches CONTROL.
3. It does not rule out 1-hop being the wrong radius, nor the attractor read-out
   (`ca3_match_score` / `cleanup_family`) that the prereg deliberately held out of this cell as a
   second variable.

What it DOES license: **swapping the feature alphabet of the comparator, as a drop-in, is not the
lever.** A cell that only changes the ruler and keeps the same propose/verify/commit loop should
not be expected to produce meaning, because nothing in that loop ever consults a referent.

---

## SIGNATURE-FAILURE CHECK -- the noncircularity witness is CORROBORATED

The witness in `metrics.json:noncircularity_witness.witness_2_worked_example` asserted that
STRUCTURED **cannot** produce `whisky -> wedding` or `checklist -> joe` from this corpus. Both
rows appear in the pooled sheet. Unsealed arm membership:

| sheet row | pair | arm | fid |
|---|---|---|---|
| **[016]** | `whisky -> wedding` | **CONTROL** | 1157 |
| **[021]** | `checklist -> joe` | **CONTROL** | 1345 |

**Both are CONTROL. The noncircularity witness is NOT contradicted -- it is corroborated.** The
two failures the witness predicted structure would exclude are, in the unsealed data, produced by
the bag-of-words arm and absent from the structured arm. This is the one place where the
structured comparator behaved exactly as designed.

It is worth being precise about what that buys: it confirms the mechanism does what it claims at
the feature level, and it confirms the cell is not circular. It does not buy quality, because the
errors STRUCTURED made instead were scored no better.

## Blind test-retest reliability -- an unplanned control that PASSED

Verified off disk: all **50/50** CONTROL rows are identical in `(subject, object)` to the 50
`PBV_BASE` rows of `data/exp_grounding_quality_readout_v1/arm_key.json`, at the same sheet slots
(same shuffle seed, same arm ordering, and S4 confirms the same 384 banked facts). The Director
scored those same 50 rows blind on 2026-08-13 in a separate sitting and returned
**1 MEANINGFUL / 12 RELATED / 37 NOISE** -- **identical marginals to this sitting**.

A single judge scoring the same 50 rows blind twice, in different pooled contexts, reproduced the
marginals exactly. That is a genuine reliability datapoint for every hand-score in this line, and
it was free. Caveat: marginals only -- per-row agreement was not recorded in the earlier document,
so this establishes rate stability, not item-level agreement.

---

## THE WITHHELD WORKED DISAGREEMENT EXAMPLE (released now that scoring is closed)

From `data/exp_structured_comparator_v1/_probe_witness.json`, mirrored in
`metrics.json:noncircularity_witness.witness_2_worked_example`. It was correctly withheld before
scoring because it names lemmas and cites sheet rows.

**Target `whisky`; 6 corpus sentences; `wedding` co-occurs in all 3 shown.**

| corpus sentence | CONTROL bag | STRUCTURED features |
|---|---|---|
| "One buyer ordered nine cases of Japanese whisky costing over $750 a bottle for a **wedding** reception" (int_cont -- **the exact hand-scored row 016**) | bottle, buyer, case, costing, japanese, nine, order, reception, **wedding** | `(^mark, costing)`, `(~mark:obl, bottle)`, `(~mark:obl, reception)` |
| "One super-rich person bought nine boxes of Japanese whisky that cost more than over $750 a bottle for a **wedding** party" (ele_cont) | bottle, box, buy, cost, japanese, more, nine, party, person, rich, super, **wedding** | `(^nmod, box)`, `(acl, cost)`, `(amod, japanese)`, `(~nmod:nummod, nine)` |
| "The attraction of the imported whisky was that no one who came to the **wedding** would be able to find the same drink in India" (ele_cont) | able, attraction, come, drink, find, import, india, same, **wedding** | `(^obj, import)`, `(~obj:conj, come)` |

`wedding` is in the CONTROL bag in all three and in the STRUCTURED feature set in none.

**Corroborating targets, same probe file:**

* `checklist` (4 sentences). "As he reached the correct height, Baumgartner went through a
  checklist of 40 things with his mentor Joe Kittinger" -- CONTROL bag contains `joe`, `kittinger`;
  STRUCTURED features are `(^obl, go)`, `(case, through)`, `(nmod, things)`,
  `(~obl:nsubj, baumgartner)`. `joe` and `kittinger` are `excluded_by_structure` in **both**
  corpus sentences. CONTROL produced `checklist -> joe` (row 021, unsealed CONTROL).
* `banana` (7 sentences). "Bananas have been the most popular fruit in the UK since 1996 --
  adults ate 221g per adult per week in 2014, much more than apples (131g) and oranges (48g)":
  STRUCTURED isolates `(^nsubj, fruit)` -- **the correct hypernym** -- plus
  `(~nsubj:amod, popular)`, from a 12-word bag that also contains
  `adult, apple, ate, more, most, much, orange, per, since, week`.
* `aphotic` (7 sentences). "At depths greater than 200 m, light cannot penetrate; thus, this is
  referred to as the aphotic zone": STRUCTURED yields the single feature `(^amod, zone)` against a
  bag of `cannot, depth, greater, light, penetrate, refer, thus, zone`.

**Note the tension this example now carries.** On `banana` and `aphotic`, structure isolates the
demonstrably better feature (`fruit`, `zone`) -- and the arm built on those features still scored
0/50 MEANINGFUL. Better features per encounter did not become better meanings. Two readings remain
open and this cell does not separate them: (a) 2.86 features/encounter is too thin to accumulate
into a stable argmax (the starvation limitation), or (b) the propose/verify/commit loop downstream
cannot convert good features into reference no matter how good they are. Reading (b) is consistent
with the standing position that the binding constraint is grounding quality, not the read-out.

---

## LIMITS

Single judge, one sitting, blind to arm. n = 50/arm; the prereg pre-declared nothing below
delta +0.11 resolvable at 2 SE, and the observed MEANINGFUL supply (1 pooled) makes even that
generous by 5.5x. The M+R secondary is not a pre-registered band and sits at p = 0.066. STRUCTURED
ran at 2.73 mean features/encoding against CONTROL's ~11 and used an out-of-domain UD front-end;
both are uncorrected and both bias against STRUCTURED. Admission rates differ substantially
(CONTROL 0.3175, STRUCTURED 0.4789), so this is not an admission-matched comparison.

---

## SCOPE -- what this licenses and what it does NOT

**This measures the SUBSTRATE'S OWN `GROUNDED_MEANING` READ-OUT on text it read** -- a live
reading pass proposing a meaning per encounter from a growing `ConceptSpace`, with the comparator
either the shipped bag-of-content-words (`context_vector_masked`) or role-bound dependency pairs
(`structural_vector_masked`, flagged, default-OFF). Everything downstream of the encoder is
identical in both arms.

LICENSED:

1. On this corpus, the read-out's meanings are 1% MEANINGFUL / 17% RELATED / 82% NOISE pooled;
   CONTROL 2/24/74, STRUCTURED 0/10/90.
2. Swapping the comparator's feature alphabet to role-bound dependency structure does not
   measurably improve meaning: delta -0.02, NULL band -- and the sample could not have shown
   otherwise, so the honest statement is "no quality signal was available for structure to move".
3. The swap DID bind mechanically: argmax disagreement 0.9780, co-occurrence agreement top5
   0.2552 -> 0.0749, `binding_check: DIVERGED`. Structure-alone is not sufficient for meaning.
4. The noncircularity witness holds: the two signature co-occurrence failures are both CONTROL.
5. CONTROL is the verified shipped reference (S4 true, 384 facts, digest `836571fa99d5765d`).

**NOT LICENSED -- do not cross-compare:**

* **This is a DIFFERENT PIPELINE from definitional extraction.** The v5 term-boundary hand-score
  (64%), the v6 predicate hand-score (70%), v6.1 (80%) and v6.2 (94%) come from **hand-written
  parsers SUPPLYING facts** from surface syntax. This number comes from the substrate's own
  distributional read-out **ACQUIRING** a meaning. The two are not on one scale, and no ratio,
  delta, percentage, or "gap" between them is meaningful. The prereg refused that comparison in
  advance (sec 8 item 2) and it is refused here. **Nowhere in this document is 1% compared to
  those numbers.**
* No claim that STRUCTURED HURTS: delta -0.02 does not reach the -0.05 HURTS band, and the
  M+R -0.16 is a non-banded secondary at p = 0.066 measuring adjacency, not reference.
* No claim that structure is unnecessary or exhausted as a route -- only that this drop-in swap,
  at 2.86 features/encounter with an out-of-domain parser, is not sufficient.
* No claim that the co-occurrence divergence is itself a quality improvement (prereg sec 8
  item 3 forbids it, and the hand-score independently declines to support it).
* Nothing is promoted or wired ON. `structural_vector_masked` stays default-OFF; growth stays
  paused.

## DISPOSITION

Comparator feature-space swap as a route to better meanings is **CLOSED as a drop-in**. Keep
`structural_vector_masked` flagged default-OFF. The two live continuations, in order of
brain-foundational priority, are (1) whether the propose/verify/commit loop can consult anything
referential at all -- it currently cannot, which is why both rulers floor -- and (2) a structural
representation dense enough not to be starved, on in-domain parses, if (1) is ever unblocked.
The next cell should NOT be gated on a hand-scored MEANINGFUL delta.
