# THE GAP SIGNAL IS A **MEMBERSHIP TEST**, NOT A DISTANCE -- MEASURED BEFORE WIRING, NOT AFTER

**Owner's description of what they remember building:** *"something that tried to sense the
**~distance** from any new fact to the grounded foundation."*

**The mechanism exists and works. But it does not measure a distance.** Measured on the real
`reading_grounding_v1` foundation (4,322 anchors), before any wiring -- *because "could this
succeed?" is cheaper asked first.*

---

## 1. IT DISCRIMINATES -- GENUINELY, AND ON THE HARD VERSION OF THE TEST

| test | `is_gap` rate | |
|---|---|---|
| known anchors | **0.000** | want low ✅ |
| invented strings (`dravithex0`...) | **1.000** | want high ✅ |
| **REAL English words the foundation KNOWS** | **0.000** | want low ✅ |
| **REAL English words it does NOT know** | **1.000** | want high ✅ |

*The second pair is the one that matters -- separating `kidney` from `dravithex0` could be done
orthographically; separating real words it knows from real words it doesn't cannot.* **Separation
1.000, n=80 each.** **The organ is not dead on arrival.**

## 2. 🚨 **BUT IT IS BINARY, AND ITS CONFIDENCE IS DEGENERATE**

Probed 240 base-vocabulary words and compared `is_gap` against **plain anchor-set membership**:

| | |
|---|---|
| **disagreements between `is_gap` and `w in anchors`** | **3 of 240 (1.25%)** |
| `margin` on KNOWN words | **1.0000 for all 67 -- ONE distinct value** |
| `margin` on GAP words | 0.5459 - 0.5742, 28 distinct values, **a band 0.028 wide** |

**➡️ `is_gap` REPRODUCES A DICTIONARY LOOKUP 98.75% OF THE TIME, AND THE CONFIDENCE VALUE IS PINNED
AT EXACTLY 1.0 ON EVERY KNOWN WORD.** *A quantity with one distinct value across 67 observations is
not a measurement; it is a constant.*

**SO THERE IS NO "DISTANCE TO THE FRONTIER" HERE. THERE IS AN IN/OUT TEST.** The graded,
nearest-first quantity the owner describes -- and which `MEMORY.md` records as the ZPD idea, *"add
DISTANCE (nearest-frontier first)"* -- **is not what the code computes.**

*Honest qualifier: it is not LITERALLY membership -- 3 probes disagreed, and 28 distinct margins
exist on the gap side. But a 0.028-wide band is very unlikely to rank candidates usefully, and I
have not tested whether it correlates with anything, so I am not claiming it is useless -- only that
it is not a distance.*

## 3. WHAT THIS MEANS FOR THE BUILD, CONCRETELY

**It does NOT kill the plan. It relocates where the intelligence comes from.**

| the ordering could come from | status |
|---|---|
| the gap signal (nearest-frontier-first) | 🔴 **NOT AVAILABLE** -- binary, no usable gradation |
| **co-occurrence consistency** (`count / n_occurrences`, in `identify_missing_prerequisites`) | ✅ **this is what actually ranks** |
| lexical occurrence in candidate docs (`rank_material`) | ✅ available -- **but it is a word counter** |

**➡️ WIRED AS-IS, THE ORGAN READS: *"among words that co-occur with what I am stuck on, pick the
ones I do not already have an anchor for, and prefer whichever co-occurs most consistently."***
**That is a reasonable, defensible policy** -- it is recognisably the right instinct -- **but its
ranking is driven by CO-OCCURRENCE COUNTING, with the gap signal acting only as a FILTER.**

**AND THAT MATTERS FOR HOW THE RESULT MUST BE READ:** counting has beaten our mechanisms by ~10x all
night. **A win here would need the counting-only arm (same policy, gap filter removed) run beside
it**, or the win is unattributable. *That control is one boolean -- `use_gap_signal=False` already
exists in the signature.*

## 4. THE BRAIN-FOUNDATIONAL STATUS, CORRECTED AGAIN

I have now had to revise this organ's label **three times in one night**:

| I said | truth |
|---|---|
| "organ MISSING, math UNPINNED" | **built, and PINNED** (Charnov MVT) -- for the *leaving* half |
| "`rank_material` is the missing half" | it is a **word counter**; the sensing is 2 functions upstream |
| *(implied)* "the gap signal is a distance" | **binary membership, margin pinned at 1.0** |

***Every correction came from opening the file rather than reading a description of it.***

## TLDR

Before connecting the "what should I read next" instinct, I checked whether it actually works on our
real knowledge base. **It does — and it isn't what its description says.**

**The good news:** it reliably tells apart words we understand from words we don't. Not just real
words versus gibberish, which would be easy, but **real English words we know versus real English
words we don't** — perfectly, on 160 test words. It's a working instrument.

**The catch:** you described it as sensing *how far* a new fact is from what we understand. **It
doesn't measure distance. It answers yes or no.** I compared it against simply checking whether a
word is in our list of known concepts, and **they agree 98.75% of the time.** Its confidence score is
**exactly 1.0 for every single known word** — one value, 67 times. That's a constant, not a
measurement.

**This doesn't sink the plan, it just relocates the cleverness.** Wired up as it stands, the system
would say: *"among words that keep appearing next to whatever I'm stuck on, pick ones I don't
already know, favouring the ones that show up most consistently."* **That is a sensible instinct** —
but the ranking is being done by **counting how often words appear together**, with the
know/don't-know test acting only as a filter.

That matters because **plain counting has been beating our sophisticated methods roughly ten to one
all night.** So if this works, we have to run it again with the know/don't-know filter switched off,
or we won't know which half did the work. Conveniently, that switch already exists.

**This is the third time tonight I've had to correct what I said about this one component** — and
every correction came from opening the file instead of trusting a description of it.

## QUESTIONS

None.

## NEXT STEPS

1. **Proceed with the wiring** -- the organ discriminates and the policy is defensible.
2. **Mandatory control: the same policy with `use_gap_signal=False`.** One boolean, already in the
   signature, and without it a win cannot be attributed.
3. **Do not describe this as distance-to-frontier in any writeup.** It is a membership filter.
