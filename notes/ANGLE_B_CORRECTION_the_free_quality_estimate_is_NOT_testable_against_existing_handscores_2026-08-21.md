# ANGLE B CORRECTION -- **THE DESIGN'S BEST SELLING POINT IS NOT TESTABLE AGAINST WORK ALREADY DONE. I MADE THE SAME MISTAKE I SPENT TONIGHT AUDITING.**

**The claim, from my own Angle B design, presented as its highest-value consequence:**

> *"Accumulated error per term would be a self-generated estimate of how good that term's banked
> meaning is -- computed with no gold, no ConceptNet, no hand-scoring. **AND IT IS IMMEDIATELY
> TESTABLE AGAINST WORK ALREADY DONE.** Tonight produced hand-scores on several hundred facts
> (MEANINGFUL / RELATED / NOISE). If accumulated error ranks those facts in the same order, the
> substrate can grade its own output."*

**THE "SEVERAL HUNDRED HAND-SCORES" DO NOT EXIST IN A USABLE FORM. Verified on disk.**

## WHAT IS ACTUALLY THERE

| file class | what it holds |
|---|---|
| `_handscore_verdict_*.json` x7 | **AGGREGATE COUNTS ONLY** -- `result`, `verdict`, `by_pattern`, plus **2-3 illustrative examples** |
| `b3_audit_sample_DEF.json` | 50 rows, full features (`subject`, `object`, `pattern`, `pmi`, `source_sentences`, `definiens_surface`) -- **and NO label field** |
| `b3_audit_sample_DIST_LOWINFO.json` | 50 rows, likewise -- the only label-shaped field is `schema_score`, **which is the mechanism's own output, not my judgement** |

**➡️ THE PER-ROW MEANINGFUL/RELATED/NOISE JUDGEMENTS WERE NEVER WRITTEN DOWN.** They exist as
counts (*"212 of 402"*, *"32% vs 4%"*) and as a handful of quoted examples. **A count cannot be
joined to a term, so it cannot be correlated with a per-term error signal.**

## 🔁 THIS IS THE THIRD INDEPENDENT INSTANCE TONIGHT OF ONE DEFECT

| where | the score survived | the items did not |
|---|---|---|
| `exp_information_foraging_reading_v1` | `heldout_coverage 0.0617` | which 604 words were banked |
| the archive at large | 3,518 of 3,676 scoring cells | their scored populations |
| **my own hand-scoring, last night** | **"32% vs 4% MEANINGFUL"** | **which of the 100 rows were which** |

**I spent tonight auditing the archive for exactly this, wrote *"an experiment that saves only its
scores can only ever answer the question it was originally asked"*, and had committed the same fault
myself the night before, by hand, on the evidence my own design then leaned on.** *The audit did not
find it. Trying to USE the data found it -- which is the only reliable detector for this class.*

## ✅ THE GOOD NEWS, AND IT IS GENUINELY DIFFERENT FROM THE FORAGING CASE

**THE RAW ROWS SURVIVED.** 50 DEF + 50 DIST rows with full features **and their source sentences**.
So the fix is **a human re-scoring pass, not a re-run** -- no 4,144-second recompute, no corpus, no
seed reconstruction. *Costly in attention, cheap in everything else.*

**AND THE HEADLINE FINDINGS ARE UNAFFECTED.** *"Definitional phrases score ~8x the distributional
half"* rests on the aggregate counts, which are exactly what aggregates are good for. **Only the
per-term CORRELATION is blocked.**

## WHAT THIS CHANGES IN THE ANGLE B DESIGN

1. **The corollary stays in the design -- it is still the most valuable thing there.** *A system that
   can grade its own knowledge without a human is worth more than the mechanism that produces the
   signal.*
2. **But "immediately testable against work already done" is WITHDRAWN.** It requires a re-scoring
   pass first, **with the per-row label persisted this time.**
3. **AND THE RE-SCORE MUST WRITE `{term, verdict}` PER ROW.** *Otherwise the third instance of this
   defect becomes the fourth.*

## ✅ SEPARATE RESULT: **THE LIVE-PATH CHECK, RUN RATHER THAN GREPPED**

*Repo rule: when the question is "is this organ live", RUN THE CODE THAT WOULD USE IT.* A real
60-sentence read loads **44 `hdlab` modules**:

| module the design needs | status |
|---|---|
| **`situation_model_accumulate`** (holds `bind_filler` / `decode_filler`) | ✅ **LIVE** |
| **`predictive_coding`** (the error signal itself) | 🔴 **NOT LOADED** |
| `definitional_extraction` | ✅ LIVE -- *confirms the 212-of-402 finding* |
| `information_foraging` | ✅ LIVE |

**➡️ THE PLACE TO PUT THE MEANING IS LIVE. THE MACHINERY THAT WOULD COMPUTE THE ERROR IS NOT.**
*So Angle B is a build PLUS a wiring, not a build alone -- and the wiring is the half that decides
whether anything is consumed.* **Good news for scoping: neither piece has to be invented.**

## TLDR

My proposed next build had one especially attractive selling point: the system would be able to
**grade its own knowledge** — spotting which of its definitions are rubbish without a human or a
dictionary. And I said we could check that immediately, because I'd hand-graded several hundred of
its facts the night before.

**Those grades aren't there.** I saved the totals — "32% good versus 4%" — and three example
sentences. **I never saved which specific entries I'd marked good or bad.** A total can't be matched
up against individual words, so the check can't be run.

**This is the third time tonight I've found this same problem, and this time I caused it.** I spent
the evening auditing our archive for experiments that saved their scores and threw away their
results, wrote up the lesson — and had done exactly that myself, by hand, the previous night, to the
very data my proposal depends on.

Worth noting: **my audit didn't catch it. Trying to actually use the data caught it.** That seems to
be the only thing that reliably does.

The recoverable part: **the raw entries survive, with their original sentences.** So this costs a
re-reading pass, not a re-run of anything expensive. And the headline result — definitions being
roughly eight times better than the alternative — is unaffected, because that's a total, and totals
are what totals are good for.

## QUESTIONS

None.

## NEXT STEPS

1. **Re-score the 100 surviving rows with `{term, verdict}` persisted per row.** *One pass, and it
   permanently unblocks the self-grading test.*
2. Angle B's mechanism is unchanged; only its "free, immediate" validation is deferred.
