# F5 EVALUATION DESIGN -- **HOW WE WOULD KNOW A COHERENCE MONITOR WORKS**, WRITTEN BEFORE ANY CODE EXISTS

**ANGLE A of the owner's standing two-angle rule.** *Pure judgement; no cell, no agent, no compute.*

**WHY THIS BEFORE THE BUILD.** Every organ that failed tonight failed at least partly on a
**badly-posed task**, not on a bad mechanism:

| failure | the task's defect |
|---|---|
| my context-diversity test | the outcome (retrieval rank) **rewarded topical narrowness** -- the opposite of the predictor |
| the sensorimotor channel | its binding floor was **propped by an uncontrolled covariate**, and a query-BLIND score beat every query-dependent one |
| G2's prediction-error gate | the signal was `sign()`-quantised, so **the gate could never fire** -- `skip = 0.00` |

**Three organs, three tasks that could not have answered the question asked of them.** *Posing this
one properly is therefore the highest-leverage work available while the build is blocked.*

---

## 1. THE TASK: **DETECT THE ANOMALOUS WORD IN A PASSAGE**

F5 computes `‖Δ situation_model‖` -- how much an incoming word forces the running discourse state to
change. **The natural, brain-matched read-out of that quantity is semantic-anomaly detection**, which
is what the N400 literature measures. `ORGAN_MAP`'s own F5 entry points here:

> **PHASE-B NOTE: the human baseline is bad -- ~40-50% of subjects fail to notice a controlled
> semantic anomaly** (Barton & Sanford 1993; Erickson & Mattson 1981, the Moses illusion) -- **and
> the undetected error propagates into durable memory. An always-on engineered check can
> STRUCTURALLY BEAT the brain here.**

**SCORED AS:** does the error peak at the anomalous word? Report **rank of the anomalous word by
error magnitude** within its passage -- via `tools/rank_with_ties.py`, both tie conventions, no bare
ranks.

## 2. 🚨 **THE CONFOUND THAT WOULD RUIN IT, AND THE CONSTRUCTION THAT KILLS IT**

**ANOMALOUS WORDS ARE USUALLY RARE WORDS.** A detector that flags low-frequency tokens would score
well **with no comprehension whatsoever** -- the exact shape of the failure that wrecked my
diversity test (an outcome measuring the wrong property) and inflated the sensorimotor floor (an
uncontrolled covariate).

**➡️ MANDATORY CONSTRUCTION: THE ANOMALOUS WORD MUST BE FREQUENCY-MATCHED TO THE COHERENT WORD IT
REPLACES**, and the match reported as a standardized mean difference. **Also matched: length,
part-of-speech, and position in the passage.** *Tonight's lesson from the balance table: match on
means AND report the distributions, because two groups can share a mean and still be trivially
separable.*

## 3. THE FLOORS THAT MUST ACTUALLY BE RUN -- NOT CHANCE

| floor | why it is mandatory |
|---|---|
| **CO-OCCURRENCE SURPRISAL** | **THE ONE THAT MATTERS.** Counting beats every arm this project has built, by ~10x. **If plain co-occurrence surprisal finds the anomaly as well, F5 adds nothing** -- and this is the floor most likely to win. |
| FREQUENCY | the confound above, as an explicit arm rather than only a matching check |
| ORTHOGRAPHIC | **and REPORT ITS TIE MASS** -- measured tonight at 0.90-0.98 across three cells, where it reports an accounting convention rather than a measurement |
| POSITION | anomalies planted late in a passage are found by "flag the last content word" |
| CONSTANT / PROTOTYPE | the query-blind floor that beat every query-dependent arm in the sensorimotor cell |
| SCRAMBLE | the passage's word order destroyed -- if the error still peaks correctly, it is not using discourse structure |

**GATE ON THE FLOOR'S UPPER BOUND, never its point value** -- standing measurement rule.

## 4. THE DIAGNOSTICS THAT MUST PRINT **BEFORE ANY VERDICT IS READ**

*These exist because G2 shipped without them and a dead gate looked like a null result.*

1. **THE ERROR DISTRIBUTION** -- how many distinct values does `‖Δ‖` actually take? *A
   sign-quantised residual collapses to a handful and no threshold can work.*
2. **THE FIRING RATE** at the chosen threshold -- **must not be 0.00 or 1.00.**
3. **A POSITIVE CONTROL** -- a deliberately grotesque anomaly that MUST produce a large error, and a
   verbatim-coherent passage that must not. *An instrument that has never been shown to fire cannot
   support a null.*
4. **TIE MASS on every arm**, treatment included.

## 5. THE CAN-FAIL CONDITION, PRE-COMMITTED

**F5 EARNS ITS PLACE ONLY IF:** the error's rank of the anomalous word beats **the upper bound of
the strongest floor actually run** -- expected to be co-occurrence surprisal -- **on frequency-matched
items, across >=3 seeds, with `tools/replication_gate.py` returning `REPLICATED`.**

**IT FAILS IF:** co-occurrence surprisal matches it (**then the monitor is re-deriving counting**),
or the scramble control performs as well (**then it is not using discourse structure at all**), or
the firing rate is degenerate.

**AND THE HUMAN BASELINE IS NOT THE BAR.** Beating a 40-50% human miss rate is **not** evidence of
comprehension -- an always-on checker beats an inattentive reader trivially. *The floors are the bar.*

## TLDR

Before anyone builds the missing "notice when a sentence does not fit" component, I wrote down how
we would know whether it works — because **every failure tonight came at least partly from a test
that could not have answered its own question.**

The test itself is natural: plant an odd word in a passage and see whether the system's surprise
peaks on that word. That is exactly what the brain research measures.

**The trap is that odd words are usually rare words**, so a system that merely flags unusual
vocabulary would look brilliant while understanding nothing. So the odd word must be swapped in for
one of matching rarity, length and grammatical type — otherwise the test measures vocabulary
statistics wearing a comprehension costume.

**And the comparison that decides it is plain word-counting**, which has beaten everything we have
built by about ten to one. If counting spots the odd word just as well, the new component has earned
nothing, however sophisticated it looks.

I also wrote down three checks that must be printed before anyone reads a result, because the last
attempt at this shipped without them: how varied the surprise signal actually is, how often it
triggers, and proof that it can trigger at all on an obviously broken sentence.

**One thing deliberately excluded as a target: beating people.** Humans miss half of these
anomalies. An always-on checker beats a distracted reader trivially, and that would prove nothing.

## QUESTIONS

None.

## NEXT STEPS

1. **This is a pre-registration in substance** -- it names the discriminator, the floors, the
   controls and the failure conditions before any code. *It is deliberately NOT written to
   `preregs/`, which is harness-denied to me.*
2. **ANGLE B is now: design the meaning-consumption link concretely** -- WHICH banked meanings get
   bound, to WHICH role, at WHAT point in reading. Without it the build gives the situation register
   a use and leaves the `GROUNDED_MEANING` facts outside the loop, which is the bottleneck.
