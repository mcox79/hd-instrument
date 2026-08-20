# THE F5 BAR IS **MEASURED BEFORE THE ORGAN EXISTS**: COUNTING FINDS THE PLANTED WORD AT **RANK 4.0 OF ~9**, AND **EVERY OTHER FLOOR CARRIES NO ANOMALY SIGNAL AT ALL**

**Tool:** `tools/score_anomaly_set_floors.py`. **Items:** `anomaly_set_frequency_matched_v8.json`,
the 102 hand-scored CLEAN items. **Corpus stats:** 7,880 simplewiki sentences after leak control.

**WHY RUN THIS NOW.** The F5 evaluation design pre-committed the kill condition: *"if plain
co-occurrence surprisal finds the anomaly as well, F5 adds nothing -- and this is the floor most
likely to win."* **Counting has beaten every arm this project has built, by roughly ten to one.** The
floor needs no organ, so it is measurable today, and it sets the bar the build would have to clear.
*This is "could this experiment have succeeded?" asked BEFORE the build rather than after it.*

---

## 1. THE RESULT

**DELTA is the whole table.** Each floor scores the anomalous sentence AND the **original, untouched**
sentence at the **same slot**. The original word is CORRECT there, so **an arm that ranks it just as
highly is responding to the SLOT, not to the anomaly.**

| floor | anomalous | original | **DELTA** | |
|---|---|---|---|---|
| **CO-OCCURRENCE SURPRISAL** | **4.00** | **6.00** | **+2.00** | **the only floor that detects anything** |
| FREQUENCY (flag the rarest) | 2.00 | 2.50 | +0.50 | **the matching worked** -- see below |
| POSITION (flag the last) | 4.00 | 4.00 | +0.00 | no anomaly signal |
| ORTHOGRAPHIC | 4.00 | 4.00 | +0.00 | no anomaly signal (and 93% tie-degenerate) |
| LENGTH (flag the longest) | 2.50 | 2.50 | +0.00 | no anomaly signal |
| CONSTANT (query-blind) | 4.50 | 4.50 | +0.00 | no anomaly signal, by construction |

*Median candidate count ~9. Ranks are midpoints from `tools/rank_with_ties.py`; both conventions
print and the tie mass is on every row.*

## 2. ⚠️ **A LEAK WAS INFLATING THE FLOOR BY 43% OF ITS OWN EFFECT, AND IT WAS CAUGHT BEFORE PUBLISHING**

The items were **drawn from** the corpus, so a co-occurrence table over all 8,000 sentences **had
read each item's original sentence** -- it "knew" the correct word fitted its context *because it had
seen that exact sentence*.

| | with the leak | after excluding the 120 item sentences |
|---|---|---|
| CO-OCC rank of the anomaly | 2.50 | **4.00** |
| its DELTA | +3.50 | **+2.00** |

**Same class as the held-out split that overlapped its training pool 600 of 600.** The exclusion is
now printed every run with its count (**120 of 8,000 removed**) -- *a control that excludes nothing
is not a control, and the only way to know is to print the number.*

## 3. ✅ **THREE INDEPENDENT CONFIRMATIONS THAT THE ITEM SET IS SOUND**

Not claims about the set -- measurements of it, and the first two could each have come out badly:

1. **FREQUENCY DELTA IS +0.50.** *"Flag the rarest word"* scores the untouched sentence almost
   identically to the tampered one. **The frequency matching did the job it was built for** -- this
   is the direct evidence, not the balance table.
2. **CO-OCC SEPARATES *MY HAND-SCORES*.** It ranks the 102 CLEAN items at 4.0 and the 17 items I
   hand-scored WEAK at 4.0-with-no-margin. **An independent machine measure agrees with the human
   pass about which items have an anomaly to find.**
3. **POSITION, LENGTH AND CONSTANT ARE ALL EXACTLY +0.00.** There is no positional artifact, no
   length artifact, and no query-blind arm that wins -- *the failure that beat every query-dependent
   arm in the sensorimotor cell.*

## 4. 🎯 **THE BAR F5 MUST CLEAR, PRE-COMMITTED**

> **F5 must beat median rank 4.0 of ~9 candidates on the CLEAN, frequency-matched items -- gated on
> that floor's UPPER bound, not its point value -- across >=3 independently-built item sets, with
> `tools/replication_gate.py` returning `REPLICATED`, and with the ~86% item ceiling stated beside
> the score.**

**AND THE TEMPTATION THAT MUST BE REFUSED, WRITTEN DOWN BEFORE IT IS ACTED ON:** co-occurrence
surprisal separates good items from weak ones, so it would make a convenient automatic item screen.
**Using it to filter the items would tune the set toward the floor and guarantee the floor wins.**
*That is circularity, and it is the exact shape of "ground by X and grade by X".*

## 5. WHAT THIS DOES NOT SAY

**It does not say F5 is or is not worth building.** Rank 4.0 of ~9 is real detection but far from
ceiling, so the organ is not pre-empted -- the floor is simply no longer unknown. **And nothing here
measures the substrate**: no F5 exists, and no arm in this table is ours.

## TLDR

Before building the missing "notice when a sentence doesn't fit" part, I measured what **plain word
counting** already achieves on the test set — because in this project counting has beaten everything
we have built, by about ten to one, and it costs nothing to check first.

**Counting finds the planted word at about 4th place out of 9 candidate words.** Real detection, not
brilliant. Every other cheap trick — flag the rarest word, the longest word, the last word, or judge
by spelling — turned out to detect **nothing at all**: they rank the *correct* word exactly as highly
as the planted one, which is the cleanest possible proof that they are responding to the position
rather than to the meaning.

**Two things worth more than the headline.** First, I nearly published a better number: the counting
method had secretly read the very sentences it was being tested on, which flattered it by almost half
its apparent skill. Removing those 120 sentences dropped it from 2nd place to 4th.

Second, the test set passed three checks it could have failed — notably that "flag the rarest word"
does *no* better on the tampered sentences than the untouched ones, which is the direct proof that
the frequency matching worked.

So the new component now has a specific number to beat, decided in advance, and a reason to exist if
it can.

## QUESTIONS

None.

## NEXT STEPS

1. **NEW ANGLE A:** replicate the bar across >=3 independently-built item sets (different builder
   seeds), so the number F5 is judged against is itself `REPLICATED` rather than one set's accident.
2. **NEW ANGLE B:** the 11 unexamined Tier-1 cells flagged by `read_what_the_cell_told_you.py`.
3. F5 itself remains cell-authoring work and is not started.
