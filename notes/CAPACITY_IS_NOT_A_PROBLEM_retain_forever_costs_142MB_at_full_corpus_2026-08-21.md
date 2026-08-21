# **CAPACITY IS NOT A PROBLEM.** RETAIN-FOREVER COSTS **142 MB** ON EVERY SENTENCE WE OWN -- AND THE GROWTH IS **SATURATING**

**The one version of the capacity question the evidence left open, answered by MEASUREMENT rather
than extrapolation over 80x more data than the claim it corrects.**

| sentences | slots | slots/sentence | accumulator size |
|---|---|---|---|
| 4,096 | 4,250 | 1.038 | 8.7 MB |
| 32,768 | 35,580 | 1.086 | 72.9 MB |
| 131,072 | 45,755 | 0.349 | 93.7 MB |
| **325,798 (every readable sentence on disk)** | **69,171** | **0.212** | **141.7 MB** |

---

## 1. 🚨 **AND IT CORRECTS MY OWN EXPONENT -- THE SAME MISTAKE, A FOURTH TIME**

**One turn ago I wrote: *"`beta = 0.589` does not saturate, so the count keeps climbing."***

**Measured over the last decade of real data: `beta = 0.289`, and falling.** Slots per sentence drop
from **6.19** early to **0.212** at full corpus. **The growth IS saturating.**

**My 0.589 came from the first 4,096 sentences -- the part of the curve dominated by function words
and first encounters.** *Fitting an exponent on the early segment and calling it the asymptote is
the same error as characterising an effect from one seed: a number from a narrow range, quoted as if
it were the limit.* **Fourth instance of that shape this session.**

## 2. THE ANSWER, INCLUDING THE WEAKEST NUMBER LABELLED AS SUCH

**MEASURED: every readable sentence we own -- 325,798 -- costs 141.7 MB of accumulators.**

**EXTRAPOLATED (NOT measured, and the weakest number here):** 10^6 sentences -> ~96,000 slots,
**~0.2 GB**; 10^7 -> ~186,000 slots, **~0.4 GB**.

*A power law fitted over one decade and projected across two more is a guess with a straight line
through it. It is reported because planning needs a figure, and labelled because it is not evidence.
**The measured column is the finding.***

## 3. 🎯 **SO SLEEP-AS-CAPACITY-MANAGEMENT IS DEAD, FOUR WAYS**

| proposed | why it does not apply |
|---|---|
| cascade / graceful decay | our slots are **private**; no shared-synapse interference to defend against |
| cold storage / tiering | **already built and proven** -- a wiring gap, not a build |
| consolidation / dedup | **no duplicates exist** in any frequency band |
| **capacity pressure itself** | **142 MB on everything we own, and saturating.** There is no pressure |

**➡️ THERE IS NO STORAGE PROBLEM FOR A SLEEP MECHANISM TO SOLVE, AT ANY SCALE THIS PROJECT CAN
PLAUSIBLY REACH.** *That is a real finding and it cost four cheap measurements.*

## 4. ✅ **AND IT TURNS THE OWNER'S INSTINCT INTO A MEASURED PERMISSION**

**Owner:** *"we can put that detail into cold storage and not lose it... we should never throw out
useful information."*

**That is not merely allowed -- it is CHEAP, and now measured.** Keeping everything forever costs
**142 MB today** and well under a gigabyte at ten million sentences. **The brain throws detail away
because it is capacity-bound; we have now measured that we are not, by a wide margin.** *Copying
biological forgetting would copy a constraint we have demonstrated we do not share -- which is the
standing rule, with a number attached for the first time.*

## 5. WHAT IS STILL OPEN, HONESTLY

- **Slot count is not the only cost.** Retrieval is `O(n_slots)` per query in the anchor scan, so
  69,171 slots is a **SPEED** question even where it is not a memory one. *The charter already names
  "the O(n_facts) speed wall" as a known frontier -- unmeasured here, and not the same question.*
- **This measures the ACCUMULATOR, not the fact store**, which has its own growth law.
- **Saturation is a property of THESE corpora.** A genuinely open-domain stream might not saturate
  the same way, though `beta` falling with scale is the ordinary pattern.

## TLDR

I said last turn that the real open question was whether our memory blows up at large scale. **I
measured it on every sentence we have — eighty times more than the claim I was correcting — and the
answer is no, by a wide margin.**

Storing everything from all 326,000 sentences we own costs **142 megabytes**. And the growth is
**slowing down**, not keeping pace: early on each sentence added about six new concepts, by the end
it adds about one fifth of one. Projected forward — and this part is a guess, not a measurement —
ten million sentences would cost under half a gigabyte.

**I also had the growth rate wrong.** I quoted a figure measured on the first four thousand
sentences as though it were the long-run trend. On the full data it is half that and still falling.
That is the same mistake I have made three other times today: taking a number from a narrow range
and treating it as the limit.

**So the sleep idea has now failed in a fourth way, and this one is final for the storage argument:
there is no shortage to manage.**

**What that does give you is a measured permission.** Your instinct — never throw useful information
away — is not just reasonable, it is cheap. The brain discards detail because it is short of room. We
now have a number showing we are not, and it is not close.

One thing genuinely still open: **having lots of stored items is a speed problem even when it is not
a memory problem**, because every lookup scans them. That is a different question and it is named in
the project charter as a known wall.

## QUESTIONS

None.

## NEXT STEPS

1. **The speed wall, not the memory wall**, is the live version of "too many slots" -- `O(n_slots)`
   per query at 69,171 slots. Named in the charter, unmeasured here.
2. Sleep-as-capacity-management should not be built. Sleep as something else may still be justified,
   but not on storage grounds.
