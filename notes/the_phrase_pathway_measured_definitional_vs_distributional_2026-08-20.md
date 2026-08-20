# THE UNMEASURED HALF, MEASURED: READING A DEFINITION OFF THE PAGE BEATS THE SUBSTRATE'S OWN READ-OUT 8-TO-1 ON THE SAME WORDS

**2026-08-20.** Every quality number this project had -- 78% noise, 3 MEANINGFUL of 100, 1.6-3.0%
precision, loses 2-3x to a trivial baseline -- was measured on the SINGLE-WORD `canonicalize`
pathway. **Roughly half of what `consolidated()` carries is a multi-word definitional phrase, and
nothing had ever scored it.** ConceptNet cannot: its gold is word-to-word edges, so a phrase can
never match one. This is that measurement.

## THE HEADLINE

| | MEANINGFUL | RELATED | NOISE |
|---|---|---|---|
| **definitional route** (phrase read off the page) | **32%** | 36% | 32% |
| **distributional read-out** (`canonicalize`, single word) | **4%** | 68% | 28% |

**Paired -- SAME term, SAME accumulated traces, both read-outs.** n=25 informative pairs.
**McNemar: 8 pairs where only the definitional route taught the word, 1 where only the
distributional one did. Exact one-sided p = 0.020.**

## THE SECOND FINDING, WHICH I DID NOT EXPECT AND WOULD HAVE MISSED BY REPORTING ONLY THE HEADLINE

**The definitional route is NOT less noisy.** 32% NOISE against the distributional 28% -- if
anything marginally worse. What changes is the *other* boundary: **RELATED collapses from 68% to
36%, and that mass moves into MEANINGFUL.**

**So the gain is not "fewer wrong answers". It is "when it is right, it TEACHES the word instead of
gesturing at it".** `algebra -> solve` and `differentiation -> integration` are not wrong; they are
*useless* -- a reader who does not know the word learns nothing. `algebra -> "the study of things
that are found in equations"` teaches it. **A denoising intervention would not have produced this,
and anyone reading only the headline would have gone looking for one.**

## WHY THE PAIRED VERSION EXISTS -- THE FIRST VERSION OF THIS RESULT WAS CONFOUNDED

An unpaired interleaved hand-score (25 phrases + 25 single words, same sitting, same scorer, same
rubric) read **32% vs 0% MEANINGFUL, Fisher p=0.002**. But the arms were not the same TERMS:

- phrase arm drew `drupe, economics, tectonics, archaeologist, electrolysis, antibody, oligarchy`
- word arm drew `previous, other's, useful, populous, silly, new, years`

**Adjectives and function-ish words have no good one-word meaning for ANY system, so that
comparison may have been measuring TERM DIFFICULTY rather than PATHWAY QUALITY** -- the
two-populations trap this project's own banner warns about. The pairing removes it by construction,
and **the result survived it** (32 vs 4 on identical terms). The confound was real; it was not what
produced the effect.

**The pairing is available for free and that is worth knowing for future work.**
`_make_definitional_gate` SHORT-CIRCUITS -- when a definition exists it never calls `inner`, so the
ledger holds no distributional counterfactual. But `reading_grounding_loop.py:1479` computes
`raw_sum` from the item's own traces and `canonicalize` is a pure function of it, so the
counterfactual is exactly recomputable after the fact.

## THE SELECTION RUNS *AGAINST* THE DEFINITIONAL ROUTE, WHICH MAKES THIS CONSERVATIVE

Of **212** definitional facts from a 12,000-sentence read, **151 (71%) have a distributional
counterfactual of NO-MATCH** -- `canonicalize` returns the term itself, which
`reading_grounding_loop.py:770-775` documents as the no-match sentinel ("It is NOT a meaning") and
which `_make_grounding_gate` REFUSES. Those 151 are excluded here because **a refusal cannot be
quality-scored.**

**So the 29% that remain are exactly the terms where the distributional read-out was at its BEST --
it had something to say. It still loses 8-to-1.** And on the other 71% the definitional route is
the ONLY source of a meaning at all: 212 definitional facts against 190 distributional ones, i.e.
the route roughly DOUBLES coverage. *That part is a coverage fact, not a quality one, and coverage
was already one of the four known strengths.*

## ⚠️ WHAT THIS IS NOT -- AND IT MATTERS MORE THAN THE WIN

**THE GOOD HALF IS NOT PRODUCED BY THE SUBSTRATE'S LEARNING MECHANISM.** The definitional route is
a SURFACE PATTERN MATCHER: it recognises "X is a Y that Z" on the page and banks the phrase. It uses
no traces, no bundling, no binding, no consolidation dynamics. **The HDC substrate's own read-out --
accumulate context vectors, sign them, nearest-anchor -- is the arm scoring 4%.**

So this does not overturn the day's conclusion; it sharpens it. *On every controlled test the
substrate's own machinery is at or below co-occurrence counting.* What this adds is that **the
system's best output comes from reading text that already states the answer**, which is the same
shape as the other three things that work (supplied perceptual norms, combining channels, dense
expository text) -- **bring in signal rather than compute it better.**

**NOT CIRCULAR, and the code comment demands this be stated.** `_make_definitional_gate`'s docstring
warns that scoring the wire against the SAME extractor output it was fed is circular with recall 1.0
by construction. That is a warning about RECALL. **This is a hand-score of MEANING QUALITY against
my own semantic judgement of what the words mean -- the extractor is not the gold here, and it
cannot be, because it is the thing under test.**

## RELATED PRIOR WORK FOUND DURING THIS -- AND A PENDING AUDIT NOBODY HAS SCORED

`tools/experiment_index.py query "definitional extraction"` -> 4 cells, 3 landed.

- **`exp_definitional_grounding_v3`** (2026-08-12, STRUCTURAL_PASS_PENDING_B3): DIST_ASIS arm, 634
  facts, `hand_scored_MEANINGFUL_rate = 0.08`. **My distributional arm read 4%, CI [0.7%, 19.5%],
  which contains 8% -- so today's scoring is consistent with the historic measurement.** That 634
  is the same population the ConceptNet precision cell scored.
- **`data/exp_definitional_grounding_v3/b3_audit_sample_DEF.json` and
  `b3_audit_sample_DIST_LOWINFO.json` -- 50 pre-registered rows each, `NOT_AUTO_SCORED: true`,
  untouched since 2026-08-12.** Two landed cells are blocked on them
  (`STRUCTURAL_PASS_PENDING_B3`). Pre-committed baseline to beat, from the v2 hand-score:
  **8% MEANINGFUL / 26% RELATED / 66% NOISE.**
- **THOSE SAMPLES DO NOT MEASURE THIS PATHWAY, WHICH IS WHY IT WAS STILL UNMEASURED.** The v3 DEF
  arm banked `Definition.head` -- **0 of its 50 sampled objects are multi-word** (`catch`, `ion`,
  `indicate`, `opening`). `substrate.py:538` now stores `d.definiens`, the FULL phrase. **The
  pathway changed after the audit sample was drawn, and the audit was never run.**

## LIMITS, STATED PLAINLY

1. **NOT BLIND, AND THE BIAS IS MINE.** I argued the phrases looked better before scoring them, and
   I am the scorer. Both arms were scored in one sitting under one rubric to control scorer drift,
   and the check is partial: my single-word arm read **0% MEANINGFUL against the historic scorer's
   3%**, i.e. I was *harsher*, not more generous -- and my extra generosity went into RELATED (44%
   vs 19%), not into MEANINGFUL. **That rules out a blanket-generosity bias. It does NOT rule out a
   phrase-specific one, and no design I can run alone will.**
2. **n=25 per arm.** The CIs are wide (the 32% is [17.2%, 51.6%]). The *paired* test is what carries
   the claim, and it rests on 9 discordant pairs.
3. **One corpus, one seed, 12,000 sentences.** simplewiki, seed 7.

## REPRODUCTION

`scratch/make_phrase_vs_word_scoring_sheet.py` (unpaired), `scratch/score_phrase_vs_word.py`,
`scratch/paired_definitional_vs_distributional.py`, `scratch/score_paired.py`. Seeds fixed
(`random.Random(20260820)`, substrate seed 7). **Every row-level score is inline below, so no number
in this note depends on a gitignored file.**

### PAIRED ROWS -- ALL 25, BOTH SIDES SCORED

| term | definitional (phrase) | score | distributional | score |
|---|---|---|---|---|
| infinity | the ordinal numbers | R | word | N |
| kilogram | the mass of the kilogram des archives | R | bipm | R |
| mendeleev | one of the biggest breakthroughs in chemistry | R | dmitri | R |
| testament | an Angel tells The Virgin Mary that she will g... | N | appearance | N |
| encyclopedia | a collection | N | dictionary | R |
| soccer | the most popular sport | R | **football** | **M** |
| trench | the deepest of them all | N | submarine | R |
| **wallonia** | **the name of the southern half of Belgium** | **M** | flemish | R |
| castro | one of the longest-serving heads of state | R | batista | R |
| **dictionary** | **a type of book which explains the meanings of...** | **M** | online | N |
| gfdl | a type of contract between the creator of a co... | R | license | R |
| experiment | a German chemist | N | idea | R |
| **cuba** | **the largest island in the West Indies** | **M** | large | N |
| monarchy | a system of government | R | constitutional | R |
| cricket | the most popular sport in India | R | rugby | R |
| **thomson** | **the first person to discover electrons** | **M** | plum | R |
| **algebra** | **the study of things that are found in equations** | **M** | solve | R |
| theory | a mostly philosophical subject | N | phlogiston | R |
| **displacement** | **the shortest way to travel the distance** | **M** | quantity | R |
| kabul | the capital city | R | turkmeni | N |
| **subduction** | **Trenches form where one tectonic plate goes under...** | **M** | push | N |
| **differentiation** | **This process of working out a slope using limits** | **M** | integration | R |
| device | the same as booting (or starting up) | N | operate | R |
| material | Another new type of material | N | useful | N |
| photo | a software for organizing and editing photos | N | editing | R |

Calls worth disputing, named so they can be: `encyclopedia -> "a collection"` scored NOISE as an
empty genus (same call as `electrolysis -> "a method"`); `gfdl -> license` and
`monarchy -> "a system of government"` scored RELATED because a bare correct genus with no
differentia does not teach the word; `soccer -> football` scored MEANINGFUL for the distributional
arm because a synonym genuinely teaches.

## TLDR

Half of what this system learns is a full phrase like *"a type of book which explains the meanings
of words"*. The other half is a single word like `algebra -> solve`. **Until today only the
single-word half had ever been checked, and it is the half that looks bad.**

I checked the phrase half against the same yardstick, on **the same words**, so neither side got an
easier list. **Where the single-word half teaches you what a word means 1 time in 25, the phrase
half does it 8 times in 25.** On the words where they disagreed, the phrase side won 8 times and
lost once.

Two honest catches. **First, the phrase half is not cleaner -- it produces just as much rubbish.
What it does is turn near-misses into real definitions.** `algebra -> solve` isn't wrong, it's
useless; *"the study of things found in equations"* actually teaches you. **Second, and this is the
one that matters: the good half is not the clever part of the system doing its job.** It is a simple
pattern-spotter noticing that the page already says *"X is a kind of Y"* and copying it down. The
learning machinery we have been building is the half scoring 1 in 25.

**So this is good news about the output and no news about the mechanism.** It also fits the pattern
of everything else that works here: we do better when we bring in information than when we try to
work it out.

## QUESTIONS

None new. This sharpens the fork already on the board rather than adding one -- see Q89, amended.

## NEXT STEPS

1. **Amend Q89** -- it currently says this half is unmeasured. It is measured.
2. **The 100 pre-registered B3 rows are still unscored and block two landed cells.** They are a
   different question (definitional-HEAD vs distributional), both single-word, with a pre-committed
   8/26/66 baseline. Same scorer, same rubric, ~1 hour, and it resolves two PENDING verdicts.
3. **The extractor returns a definition for 10.7% of definitional sentences, with ~48% of drops
   recoverable** (multi-word definienda, `which means`, quoted definiens). That headroom is now
   worth more than it was this morning, because the output it supplies is measured, not assumed.
