# PRIOR WORK FOUND -- **A BLIND 100-ROW HAND-SCORE ALREADY EXISTED. I REDID IT UNBLINDED. AND THE SELF-GRADING NEGATIVE NOW REPLICATES ON THE BLIND DATA.**

**Owner: *"remember to ALWAYS look for previous work -- I think we did work on evaluating our
knowledge too -- we did a ton of it. Why haven't you already found all this?"*** **Correct on every
point. The drill I should have run first, run now.**

---

## 1. HOW MUCH PRIOR WORK EXISTS ON EVALUATING OUR OWN KNOWLEDGE

`experiment_index.py query "quality"` -> **126 cells, 116 landed.** The directly relevant ones, none
of which I had opened:

| cell | verdict |
|---|---|
| **`exp_grounding_quality_readout_v1`** (08-12) | *"100 blind rows written for the director's hand-score. **THIS CELL MAKES NO QUALITY CLAIM.**"* |
| `exp_meaning_asset_fair_test_v1` (08-15, **7,228 s**) | **`ASSET_CLEARS_THE_STRONGEST_FLOOR`** |
| `exp_storage_quality_instrument_v1` (08-15, **3,519 s**) | `INSTRUMENT_STILL_LOOSE` -- 10/11 gates; **refused to publish a number** |
| `exp_meaning_asset_handlexicon_scorability_v1` | `NOT_SCORABLE_ON_THE_SEMANTIC_GOLD` -- lexicon covers **3.9%** of the instrument vocabulary; 16 SimLex pairs against a floor of 100 |
| `exp_encoding_quality_instrument_v1/v2`, `exp_extraction_quality_gate_neural_foundation_v1` | unopened |

## 2. 🔴 **THE ONE THAT MATTERS: THE HAND-SCORE WAS ALREADY DONE, BLIND, AND RESOLVED YESTERDAY**

`data/exp_grounding_quality_readout_v1/B3_RESOLVED.md`, written **2026-08-20**:

> *"`_joined_verdicts.json` -- written **10 minutes AFTER** `blind_sample.json` -- contains **all 100
> rows, scored MEANINGFUL / RELATED / NOISE and already joined to their arm.** The hand-score was
> done. Only the verdict field and the downstream docs were never updated."*

| arm | n | MEANINGFUL | RELATED | NOISE |
|---|---|---|---|---|
| PBV_BASE | 50 | 1 | 12 | 37 |
| PBV_F1F3 (read-out fix) | 50 | 2 | 7 | 41 |
| **total** | **100** | **3** | **19** | **78** |

**`BASE - F1F3` = -0.020, CI [-0.080, +0.040] -- NOT separated. The read-out fix did not move
grounding quality.** *0 of 100 are self-tautologies, so this is the cross-grounded population.*

**➡️ AND TONIGHT I HAND-SCORED 100 ROWS UNBLINDED, WHILE A BLIND 100-ROW SET SAT COMPLETED ON DISK.**
*Blinding is not a nicety here: I knew which arm every row came from as I scored it.*

## 3. ✅ **THE PAYOFF: THE SELF-GRADING NEGATIVE REPLICATES ON BLIND DATA -- AND MY "HINT OF INVERSION" DOES NOT**

Joining the blind verdicts to `best_cos` via the arm provenance files (**100 of 100 joined**, no use
of the un-blinding key):

| verdict | n | mean `best_cos` |
|---|---|---|
| MEANINGFUL | 3 | **0.2802** |
| RELATED | 19 | 0.3957 |
| NOISE | 78 | 0.3705 |

| sample | separation (GOOD - NOISE) |
|---|---|
| my unblinded n=50 | **-0.0316** |
| **blind n=100** | **+0.0095** |

**➡️ BOTH ARE INDISTINGUISHABLE FROM ZERO, AND THE SIGN FLIPS BETWEEN THEM. That is what noise looks
like.** **The conclusion holds and is now replicated: `best_cos` carries NO usable signal about
meaning quality.** *And the "hint of inversion" I explicitly declined to claim does **not**
replicate -- flagging it as unclaimed was correct, and testing it killed it.*

## 4. ⚠️ WHAT I CANNOT CLAIM, THOUGH IT IS TEMPTING

**Per 100 rows, my scoring gave ~6 MEANINGFUL / 40 RELATED / 54 NOISE; the blind scorer gave 3 / 19 /
78.** *That LOOKS like I was markedly more lenient -- the textbook unblinded-scorer effect.*
**IT CANNOT BE CLAIMED. The two samples are different populations** -- mine is
`exp_definitional_grounding_v3`'s distributional slice, theirs is `exp_grounding_quality_readout_v1`'s
PBV arms, different corpora and different extraction paths. **Leniency and population are perfectly
confounded here, and separating them would need both scorers on the SAME rows.** *That is a cheap,
worthwhile experiment and it is not this one.*

## 5. WHY I MISSED IT, HONESTLY

I ran the prior-work check **on the thing I was building** (`"information foraging"`, `"cold
placement"`) and **never on the thing I was DOING** -- hand-scoring meanings. **The habit is
attached to BUILDING and not to WORKING.** *`CLAUDE.md`'s rule says "before building OR wiring
anything, query BOTH archives." Hand-scoring is neither building nor wiring, so the rule as written
did not fire -- and I spent hours on it.*

## TLDR

You were right, and the answer is worse than "I didn't look hard enough."

**There is a lot of prior work on judging our own knowledge** — 126 experiments mention quality, 116
finished. Several ran for hours. One of them **already did exactly what I spent tonight doing**: it
produced 100 examples with the source hidden, had them graded, and joined the grades back up. That
was finished on the 12th and written up **yesterday**.

**I graded 100 examples tonight without hiding the source from myself.** That's a weaker method, and
a properly blinded version was sitting on disk.

**The genuine payoff is that having both lets me check my own conclusion.** I reported earlier that
the system's confidence scores are useless for telling good knowledge from bad. **On the blind data,
that holds** — the relationship is essentially zero again. And the one speculative bit I flagged but
declined to claim — that confidence might run *backwards* — **doesn't survive: the direction flips
between the two samples, which is what randomness looks like.** Flagging it as unclaimed was the
right call.

**One tempting comparison I'm refusing to make:** my grades were much more generous than the blind
grades. That's what you'd expect from not hiding the source. But the two sets of examples come from
different places, so I genuinely cannot tell leniency from a different sample. Settling it would take
both scorers on the same rows.

**Why I missed it:** I check for prior work before *building* something. I don't check before *doing*
something. Hand-scoring isn't building, so the habit never fired.

## QUESTIONS

None.

## NEXT STEPS

1. **The prior-work check must fire on WORK, not just on BUILDS** -- that is the rule change this
   earns, and it belongs in `CLAUDE.md`.
2. **Same-rows double-scoring** would settle leniency-vs-population cheaply, and would give the first
   inter-scorer agreement number this project has.
3. `exp_meaning_asset_fair_test_v1` (`ASSET_CLEARS_THE_STRONGEST_FLOOR`, 2 hours) is **unread** and is
   the most promising unopened result in this set.
