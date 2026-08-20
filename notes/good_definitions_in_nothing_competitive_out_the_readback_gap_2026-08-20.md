# GOOD DEFINITIONS IN, NOTHING COMPETITIVE OUT: THE READ-BACK GAP THAT DECIDES WHAT TODAY'S WIN IS WORTH

**2026-08-20.** Today established that the substrate's definitional-phrase output is genuinely good
and beats strong independent floors on four seeds. **This note is the qualification that changes
what that is worth, and it is built entirely from evidence already on disk.**

## THE CHAIN, END TO END

| step | status | evidence |
|---|---|---|
| 1. reading produces definitional PHRASES | **GOOD** | 32% MEANINGFUL vs the distributional read-out's 4%, PAIRED on identical terms (McNemar p=0.020); 19.4/18.9/20.3/21.3% on 4 seeds vs a strongest length-matched floor of 7.5/7.4/8.2/7.7% |
| 2. those phrases are BANKED as consolidated facts | works | 212 of 402 provenance rows carry `meaning_source=DEFINITIONAL_EXTRACTION` |
| 3. **something reads consolidated knowledge back out and does something better with it** | ❌ **NOT COMPETITIVE** | `exp_cortical_read_consolidated_v1` spec `v3_floors_at_k` |

**➡️ STEP 3 IS THE GAP. Better definitions go in; nothing measurably better comes out.**

## STEP 3, VERIFIED FROM THE METRICS RATHER THAN CITED FROM A SUMMARY

`data/exp_cortical_read_consolidated_v1/metrics.json`, re-read today:

- **3 seeds** (20260819 / 7 / 101), ~16,600 sentences each, 428-480 consolidated facts per seed.
- **`UNDERPOWERED: false`** on all three -- so a null here is a result, not a width.
- **`items_predate_mechanism: true`** -- this project's strongest free predictor of a non-bogus
  result.
- **`CONTEXT_clears: false` and `BOTH_clears: false` at EVERY k (1, 5, 10, 25, 50), on every seed.**
  The strongest floor is `RANK_COOC_floor` and it is never cleared.
- **`READING_A` fires at every k** -- so the route DOES retrieve; it beats scramble and chance.

The cell's own `floor_note` states the distinction exactly: *"A run where READING_A fires but
nothing clears the floor means the route RETRIEVES and is NOT COMPETITIVE."*

## WHY THIS PARTICULAR ROUTE IS THE ONE THAT MATTERS

`hdlab/cortical_recall.py` was not an optional extra. Its own docstring records **why it was
built**: *"THE ROUTE THAT DID NOT EXIST, and whose absence was this substrate's largest measured
fidelity defect: every other retrieval route addresses the episodic store, so consolidation could
be ablated to zero without moving the read-out at all."*

**So this is the route built specifically to make consolidated knowledge matter -- and it does not
beat word-counting at any k.** That is why the inertness finding survives today's good news:
*consolidation, definitions and foraging are INERT on the read-out; ablations demonstrably fire
(provenance 68 -> 0) and change no arm to four decimals.*

## WHAT I HAD TO CORRECT WHILE ESTABLISHING THIS

**I nearly filed "the cortical read has NO callers -- it is islanded."** That was wrong, and the
way it was wrong is instructive:

- `Grep` for `recall_cortical` returned **2 hits** (a docstring and the `def`).
- `Grep` for `cortical_recall|recall_cortical|cortical_read` returned **1 file**, and did not
  include `substrate.py` at all -- **contradicting the first search.**
- Shell `grep -rn` found the **third** match: `hdlab/substrate.py:1037`, a real call inside a
  self-test (which carries its own positive control). And `experiments/exp_cortical_read_
  consolidated_v1.py` calls it too.

**Two different searches, two different incomplete answers, and the absence claim I was about to
make would have been false.** This is the standing rule earning its keep: *an absence claim requires
an ENUMERATION, not a search -- and state how you enumerated.* Here the enumeration is: shell
`grep -rn` over `hdlab tools verification` plus an `ls` of `experiments/`, cross-checked against
the module's own `used_by` registry field.

## WHAT THIS DOES AND DOES NOT CHANGE

- **DOES NOT change** that the phrase output is good. Four seeds, five floors, an ORACLE positive
  control at 100%, and a SHUFFLE floor at 0.6% pooled. That evidence stands.
- **DOES change what it BUYS.** A better artifact is not better behaviour. **On current evidence
  there is no measured route by which more or better definitions become a system that performs
  better** -- because the one route built to consume them is not competitive.
- **DOES bear on Q89, and against the branch I said was closer.** Last turn I told the owner the
  two branches were "much closer than my original wording implied", on the grounds that the
  pipeline branch would supply 4x more of the GOOD kind of material. **That is still true about the
  material and now looks weaker as a plan**, because the consumer end is unmeasured-to-negative.
  Supplying four times as much of something nothing can use competitively is not four times the
  value. **Correcting that on the board is more useful than leaving it to read as encouragement.**

## THE HONEST OPEN QUESTION THIS RAISES

**Is step 3 failing because the READ is weak, or because the CONTENT is thin?** The cortical read
was measured on the store as it was -- **and that store was ~0% multi-word on the population the
precision cell scored.** If the read-back was tested largely against single-word `canonicalize`
anchors, then **it has never been tested on the good content**, and "not competitive" may be a
verdict on the input rather than on the route.

**That is a genuinely open and cheap-to-settle question, and it is the first thing I would run on
the pipeline branch** -- before spending anything on extractor recall. *Stated as a hypothesis, not
a finding: I have not checked which population that cell's index was built over.*

## TLDR

Today's good news was that the system writes decent definitions. This note checks the next link in
the chain: **does anything actually USE them?**

The answer, from an experiment that already ran: **no.** There is one route built to read that
learned knowledge back out -- it was built precisely because without it the learning could be
switched off entirely without changing any answer. That route does retrieve; it just never beats
plain word-counting, at any setting, on three runs that were not too small to tell.

**So we are writing better notes into a notebook nothing reads competitively.** The quality is real.
The benefit is not yet demonstrated anywhere downstream.

I also nearly reported that this route was completely unused. It is not -- two searches gave me two
different wrong answers, and only listing the files properly found the real caller. Worth saying
because I would have filed a false claim with confidence.

## QUESTIONS

None new. This corrects something I told the owner last turn about Q89 and I have amended it there.

## NEXT STEPS

1. **Settle whether the read-back was ever tested on the phrase content**, which is the open
   question above and is cheap. If it was tested only on single-word anchors, "not competitive" is
   a verdict on the input.
2. **Do NOT spend on extractor recall until 1 is answered.** Four times more material that nothing
   reads competitively is not four times the value.
