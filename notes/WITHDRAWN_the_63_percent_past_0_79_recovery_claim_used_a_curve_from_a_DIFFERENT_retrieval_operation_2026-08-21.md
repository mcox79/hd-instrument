# 🚫 **WITHDRAWN: "63% OF LIVE WRITES LAND IN CONCEPTS PAST THE 0.79-RECOVERY POINT". THE CAPACITY CURVE I GATED ON MEASURES A RETRIEVAL OPERATION THE CONCEPT STORE DOES NOT PERFORM.**

**I reported this one turn ago, put it in the plan, and gave it to the owner as the payoff of the
whole mechanism thread. It does not stand as stated. Caught by doing the thing I said I would do:
re-measuring the capacity curve on the LIVE representation (discipline 16).**

---

## 1. WHAT I CLAIMED

**Live trace loads (median 10, p90 36, max 77) placed against
`vsa_cleanup_memory.capacity_curve`'s numbers -- recovery 0.9967@L=8, 0.7867@L=16, 0.3267@L=32 --
giving "63.0% of live traces sit in concepts above L=16", i.e. past 0.79 recovery.**

## 2. 🔴 THE DEFECT: THE TWO NUMBERS COME FROM DIFFERENT OPERATIONS

**`capacity_curve` BINDS each member to a key and recovers ONE SPECIFIC target by UNBINDING:**
`keys = bipolar_keys(L, d)`, `res = unbind_residue(C, keys, members, 0)`, `tgt = members[:, 0]`.
***That is targeted retrieval of a designated slot from a bound superposition.***

**`ConceptSpace` does none of that.** *It accumulates a PLAIN SUM per lemma (`self._sums[lemma] +=
ctx_vec`, no keys, no binding) and `canonicalize` compares one accumulated bundle against anchor
bundles.* **There is no key to unbind with and no designated slot.**

> **I applied a difficulty threshold from a harder, differently-shaped task to a store that performs
> a different one. Discipline 11 (no number crosses scorers) and 16 (a floor belongs to the
> representation AND operation it was computed on).**

## 3. ✅ WHAT A MATCHED MEASUREMENT SHOWS -- AND IT IS MUCH MORE FORGIVING

**Same d=256, same M=800, 400 probes, ONE VARIABLE (the representation). Protocol: superpose L
items, ask whether the codebook's argmax is a MEMBER of the superposed set.**

| load L | 1 | 8 | 16 | **32** | **64** | **128** |
|---|---|---|---|---|---|---|
| **LIVE context vectors** | 1.0000 | 1.0000 | 0.9900 | **0.9600** | **0.8000** | **0.6025** |
| RANDOM ±1 control | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.9800 | 0.9425 |
| **live − random** | 0 | 0 | −0.0100 | **−0.0400** | **−0.1800** | **−0.3400** |

**➡️ AT THE MEASURED LIVE MEDIAN LOAD OF 10, BOTH ARMS SIT AT 1.0000. At p90 = 36, live is ~0.95.**
***So under the operation that actually resembles what the concept store does, the live loads are
NOT catastrophic, and the "63% past 0.79" framing is wrong in both threshold and direction of
alarm.***

## 4. ✅ WHAT SURVIVES, AND IT IS THE PART I WAS LEAST SURE OF

**The caveat I attached to the claim is the thing that turned out to be measurable and true:
correlation in the live representation costs real capacity, and the cost GROWS with load.**

| | mean cos | **E[cos^2]** | `inv_e_sq` | vs Welch bound |
|---|---|---|---|---|
| **live context vectors** | **+0.0078** | **0.00474** | **211** | **82%** |
| random ±1 | −0.0001 | 0.00390 | 256 | 100% |

**Live vectors carry a small positive common mode and sit at 82% of the theoretical floor -- still
FAR better than any trained encoder measured earlier (best was 17.9% of its own dimension).**
*And the penalty is negligible at low load and severe at high load: −0.04 at L=32 but −0.34 at
L=128.* **So load still matters; the threshold at which it starts mattering is much higher than I
said.**

## 5. ⚠️ AND THE HONEST RESIDUE: NEITHER CURVE IS THE STORE'S OWN OPERATION

**Mine is closer but still not it.** *`ConceptSpace` neither unbinds a slot nor asks "is the argmax
a member" -- it compares ONE accumulated bundle against OTHER accumulated bundles.* **The capacity
question for THIS substrate is: as a lemma's bundle accumulates, does it stay closer to the right
anchor than to a wrong one? That is measurable and has not been measured.** *Recorded as the open
question rather than papered over with the nearest available curve -- which is the mistake being
withdrawn here.*

## TLDR

One turn ago I reported that **63% of what the system writes goes into word-memories too full to
recall reliably**, put it in the plan, and gave it to you as the payoff of the whole night's thread.
**It does not hold up, and I found that by doing the check I'd promised.**

The problem: I measured "how full is too full" using a **different kind of retrieval** than the
system actually does. The yardstick I used tests pulling out one *specific designated* item from a
mixture — genuinely hard. The system does something easier: it just adds things up and compares
whole piles to each other.

**Measured properly, with only the representation changed and everything else held fixed, the picture
is much more forgiving.** At the typical live load of 10 items, recall is **perfect**. At the busy end
(36 items) it's about **95%**. Degradation only becomes serious past 64.

**What does survive is the part I was least confident about.** I'd warned that real word-contexts
overlap more than idealised ones and that this would cost capacity. **That's now measured and true** —
and the cost grows sharply with load: barely anything at 32 items, but a third of the accuracy gone
by 128. Our representation sits at **82% of the theoretical best**, which is still far ahead of any
trained model we compared against.

**And an honest leftover:** my new yardstick is closer to what the system does, but still not exactly
it. The real question — as a word's memory fills up, does it stay closer to the right neighbour than a
wrong one? — **hasn't been measured.** I'm recording that rather than reaching for the nearest
available number, which is precisely the mistake I'm withdrawing.

## QUESTIONS

None.

## NEXT STEPS

1. **Do not quote 0.7867@L=16 or 0.3267@L=32 for the concept store.** *They are bind/unbind numbers.*
2. **The live loads look SAFE at their measured median, so "writing less" is NOT explained by bundle
   saturation** -- which puts the crosstalk/interference account back as the live hypothesis and
   removes a competing story I had started to prefer.
3. **The unmeasured question is the right one to measure next:** bundle-vs-anchor discrimination as
   load grows, which is the store's actual operation.
