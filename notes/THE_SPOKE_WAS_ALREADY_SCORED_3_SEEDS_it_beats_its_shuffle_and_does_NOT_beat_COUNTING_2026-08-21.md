# THE SPOKE WAS ALREADY SCORED ON 3 SEEDS -- **IT BEATS ITS OWN SHUFFLE EVERY TIME, AND IT DOES NOT BEAT PLAIN CO-OCCURRENCE ANY TIME**

**I was about to recommend building the adapter that lets `read()` consult organ B5.
`exp_sensorimotor_spoke_grounding_v1` already scored it -- 3 seeds, ~40,000 sentences each across 27
corpora, ~20-27 minutes per seed. The answer is a replicated negative, and it saves the build.**

---

## 1. ALL THREE SEEDS, ALL ARMS

| seed | n | **TOP_COOC** *(the pre-registered bar)* | SPOKE_EUCLID | SPOKE_COSINE | SHUFFLED | RANDOM | **SUBSTRATE** | p(spoke vs bar) |
|---|---|---|---|---|---|---|---|---|
| 20260819 | 361 | 0.0499 | 0.0526 | 0.0582 | 0.0166 | 0.0194 | **0.0194** | **1.0** |
| 7 | 327 | 0.0673 | 0.0703 | 0.0887 | 0.0275 | 0.0153 | **0.0275** | **1.0** |
| 101 | 329 | 0.0517 | 0.0699 | 0.0729 | 0.0182 | 0.0182 | **0.0274** | 0.335 |

**The cell pre-registered the right bar and said so:** *"**TOP_COOCCURRENT** (pre-registered).
**Beating RANDOM_CANDIDATE is not the bar.**"*

## 2. ✅ **THE NORMS CARRY REAL SIGNAL -- THE CAN-FAIL CONTROL FIRES 3 OF 3**

`SHUFFLED_NORMS` permutes every profile onto another word with **marginals preserved exactly**.
Paired-permutation p against the spoke: **0.008, 0.014, 0.0025 -- all significant, all three seeds.**
`READING_C_norms_carry_it: [true, true, true]`.

**➡️ THIS IS NOT AN EMPTY ORGAN. Destroy the norm structure and performance collapses, every time.**

## 3. 🔴 **AND IT NEVER BEATS COUNTING**

**Paired-permutation p vs `TOP_COOCCURRENT`: 1.0, 1.0, 0.335. Not significant on any seed.**
The per-seed margins are `+0.0027, +0.0030, +0.0182` -- **consistent in SIGN but `replication_gate`
returns `UNSTABLE_MAGNITUDE` (a 6.7x spread)**, and none is individually significant.

**➡️ FOR THE FIFTH TIME TONIGHT, A COUNTING BASELINE MATCHES THE SOPHISTICATED MECHANISM.**
*Top-co-occurrent is "whichever candidate word appears near the target most often". It ties a
12-dimensional human-rated perceptual profile.*

## 4. 🔴 **AND OUR OWN SUBSTRATE SCORES AT THE RANDOM FLOOR**

| | seed 20260819 | seed 7 | seed 101 |
|---|---|---|---|
| `SUBSTRATE` | **0.0194** | 0.0275 | 0.0274 |
| `RANDOM_CANDIDATE` | **0.0194** | 0.0153 | 0.0182 |

**On the first seed the substrate ties the random floor hit-for-hit (7 of 361 each).** *It is
marginally above random on the other two. **The substrate is the WEAKEST non-control arm in the
table**, well below both the spoke and plain counting.*

## 5. WHAT THIS SETTLES

1. **DO NOT BUILD THE ADAPTER ON THIS EVIDENCE.** *The organ is real -- it beats its own shuffle 3/3
   -- but it does not beat the cheap baseline it was pre-registered against. Wiring it into `read()`
   would be wiring in something that ties counting.*
2. **THE ORGAN IS STILL WORTH KEEPING.** *Beating a marginals-preserved shuffle three times is a
   genuine signal. The failure is comparative, not intrinsic.*
3. **THE TASK IS BRUTAL FOR EVERYONE.** Best precision anywhere in the table is **0.0887**. *Nothing
   here is working well; the spoke is losing a race between slow runners.*
4. **AND THE MOST USEFUL NUMBER IS THE ONE NOBODY WAS TESTING: `SUBSTRATE` ≈ `RANDOM`.**

## TLDR

I was about to recommend building the connector that lets the reading process use the twelve
human-rated perception dimensions. **That was already tested — three separate runs, forty thousand
sentences each, across twenty-seven sources. The answer is no, and finding it saved the build.**

**The good part: the ratings genuinely carry information.** The experiment includes the right check —
shuffle the ratings between words while keeping their overall statistics identical, and performance
collapses. That happened on all three runs. **So this isn't an empty component.**

**The problem: it never beats simply counting which words appear near each other.** Not on any of the
three runs. The experiment had pre-registered exactly that comparison and stated plainly that beating
random guessing wouldn't count.

**That's the fifth time tonight a simple counting method has matched or beaten a sophisticated one.**

**And the most striking number wasn't what the experiment was testing:** our own system scores at the
random-guessing floor — on one run, tied exactly, seven correct out of three hundred and sixty-one.
**It is the weakest real method in the table.**

Worth saying: **everything here is performing badly.** The best result anywhere is under 9% correct.
The perception ratings aren't losing a race between strong contenders — they're losing a slow one.

## QUESTIONS

None.

## NEXT STEPS

1. **The adapter is NOT evidenced. Do not build it on this basis** -- that is the decision this cell
   already supports and it should be recorded against organ B5's `NEEDS_ADAPTER` status.
2. **`SUBSTRATE` ≈ `RANDOM` on a 3-seed, 40k-sentence, pre-registered task deserves its own attention**
   -- it is a harder finding than anything about the spoke.
3. If the spoke is revisited, the bar remains `TOP_COOCCURRENT`, not random.
