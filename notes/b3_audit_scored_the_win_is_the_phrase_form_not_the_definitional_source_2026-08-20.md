# B3 AUDIT SCORED (100 PRE-REGISTERED ROWS, BLIND): THE WIN IS THE **PHRASE FORM**, NOT THE DEFINITIONAL SOURCE

**2026-08-20.** `data/exp_definitional_grounding_v3/b3_audit_sample_{DEF,DIST_LOWINFO}.json` --
50 rows each, `NOT_AUTO_SCORED: true`, **untouched since 2026-08-12**, blocking two landed cells at
`STRUCTURAL_PASS_PENDING_B3`. Scored blind today.

## WHY THIS WAS WORTH DOING AND IS NOT BOOKKEEPING

Today's paired result showed the definitional route beating the distributional read-out 8-to-1. But
its arms differed in **TWO** ways at once -- **SOURCE** (read off the page vs inferred from traces)
and **FORM** (a phrase vs a single word) -- and that design cannot separate them. **The v3 DEF arm
is definitional SOURCE with SINGLE-WORD FORM** (`Definition.head`; 0 of 50 objects multi-word). It
is exactly the missing cell.

## THE RESULT

| same rubric, same scorer, same day | MEANINGFUL | RELATED | NOISE |
|---|---|---|---|
| definitional **PHRASE** (`d.definiens`) | **32%** | 36% | 32% |
| definitional **HEAD** (`d.head`, SAME source) | **4%** | 50% | 46% |
| distributional (`canonicalize`) | **0%** | 44% | 56% |

**DEF-head vs DIST on MEANINGFUL: 2/50 vs 0/50, Fisher one-sided p = 0.2475. NOT DISTINGUISHABLE.**
On NOISE: 23/50 vs 28/50, p = 0.2119. **Also not distinguishable.**

**➡️ READING A DEFINITION OFF THE PAGE AND THEN KEEPING ONLY ITS HEAD NOUN DISCARDS ESSENTIALLY ALL
OF THE TEACHING VALUE: 32% -> 4%.** The definitional source, stripped to one word, performs like the
distributional read-out it was supposed to beat.

**Only 2 MEANINGFUL rows exist in the whole 100: `drosophila -> fly` and `piraeus -> port`.** Both
are the same special case -- **a specific term whose genus is unambiguous and identifying.**

## WHAT THIS MEANS, AND IT IS A CLAIM ABOUT OUTPUT FORMAT, NOT ABOUT MECHANISM

**A SINGLE WORD ALMOST CANNOT TEACH A WORD.** Across everything hand-scored today, ~75 single-word
objects yielded **3** MEANINGFUL (`soccer -> football`, `drosophila -> fly`, `piraeus -> port`) --
all synonyms or unambiguous genus. The format caps out at roughly 2-4%. **The phrase format reaches
32% with the same source material.**

**`substrate.py:538` -- `self._definition_map[lem] = d.definiens` -- looks like an implementation
detail and is where the ENTIRE measured gain lives.** The v3 cell banked `d.head` at the same line.
That one change is worth 28 percentage points of MEANINGFUL.

**AND IT REDIRECTS THE EXTRACTOR WORK.** The known headroom is *recall* -- a definition is returned
for 10.7% of definitional sentences, ~48% of drops recoverable, ~4x supply. **That work is now
clearly worth more than head-selection work**, and today's `_MEASURE_HEAD` fix (`way`, `means`,
`part`; empty heads 7 -> 5) was improving the component this audit says barely matters. *It was a
correct fix to a part that does not carry the result.*

## ⚠️ THE CROSS-SCORER COMPARISON IS THE UNRELIABLE ONE -- USE THE WITHIN-SITTING ONE

The sample file carries a **pre-committed baseline** from the v2 hand-score: **8% M / 26% R /
66% N.** Against it, DEF-head reads 4% M (worse), 50% R (higher), 46% N (better).

**DO NOT READ THAT AS "DEF HALVED THE NOISE".** My RELATED/NOISE boundary is measurably more
generous than the historic scorer's -- measured directly today, my single-word arm read 44% RELATED
where the historic scorer read 19%, with **MEANINGFUL essentially identical (0% vs 3%, and 4% vs
8% here, both within CI)**. So the M cell survives the scorer change and the R/N boundary does not.
**The valid comparison is DEF vs DIST within this one sitting, and there DEF-head wins nothing at
p = 0.21-0.25.**

## STATUS OF THE TWO BLOCKED CELLS -- REPORTED, NOT REWRITTEN

`exp_definitional_grounding_v3` and `_v5` remain `STRUCTURAL_PASS_PENDING_B3`. **Their landed
`metrics.json` files are deliberately NOT modified** -- same discipline applied to the seven unread
runs on 2026-08-19: the verdict is recorded beside the evidence, not written back into a landed
artifact.

**What the audit says about them:** the structural claim they made stands (the DEF arm banks facts
the distributional path does not produce -- 1749 of 1751). **The QUALITY claim the B3 gate was
holding them open for does NOT clear: definitional-HEAD is not distinguishable from the
distributional control on either MEANINGFUL or NOISE.** That is a genuine negative for the
head-based wire, and it is also the reason the phrase-based wire matters.

## LIMITS

1. **n=50 per arm; 2 MEANINGFUL total.** The MEANINGFUL comparison rests on 2 events. It cannot
   detect a small real difference -- **it can only say the difference is not the 8-to-1 seen for the
   phrase form**, which is the question asked.
2. **Blind on arm, not on hypothesis.** I recorded the prediction ("the arms will be
   indistinguishable and the win is the form") in `scratch/score_b3.py` **before** opening the key,
   and the sheet carried no cue to arm -- both arms are single-word by construction. **This is the
   one genuinely blind score of the day**; the phrase-vs-word comparisons could not be.
3. **The 3 MEANINGFUL single-word rows are all one pattern** (unambiguous identifying genus), which
   suggests the cap is structural rather than a sampling accident -- but that is an observation
   about 3 items.

## TLDR

Eight days ago two experiments finished and were left "pending a human check". I did that check
today, on all one hundred examples, without being able to see which experiment each came from.

**The answer settles something today's earlier result could not.** This system produces meanings in
two shapes: a single word, or a full phrase. Earlier I found the phrase kind teaches you a word
about eight times more often. But there were two possible reasons -- either because those phrases
are lifted off a page that was already explaining the word, or simply because a phrase has room to
say something and one word does not.

**It is the second.** The old experiment took definitions off the page in exactly the same way, then
kept only the single most important noun from each. **That version teaches you a word about as often
as the crude method we already had -- which is to say, almost never.** In one hundred examples, only
two single words taught anything at all: that a drosophila is a fly, and that Piraeus is a port.

**So a single word essentially cannot explain a word**, no matter how well we choose it. The whole
gain came from a one-line difference: keeping the whole explanation instead of one word of it.

**This redirects effort.** We have been improving how the system picks that one word -- including a
fix I made this morning. **That part barely matters.** What matters is getting more explanations off
the page in the first place, where we currently catch only about one in ten.

## QUESTIONS

None. This does not change the fork on the board; it makes the "fix the reading pipeline" side more
concrete by naming which part of the pipeline pays.

## NEXT STEPS

1. **The extractor's RECALL is now the highest-value target in the pipeline** -- 10.7% of
   definitional sentences, ~48% of drops recoverable. Head-selection is not.
2. **Re-check the empty-head backlog before spending more on it** (`thing`, `word`, `idea` needing
   refuse-not-expand). This audit says head quality is a low-value lever; that backlog should be
   re-priced or dropped.
3. **The phrase route has never been run at scale** -- every measurement of it is n=25 on one seed
   and 12,000 sentences. A proper cell with seeds, floors and CIs is the honest next experiment if
   the owner takes the pipeline branch of Q89.
