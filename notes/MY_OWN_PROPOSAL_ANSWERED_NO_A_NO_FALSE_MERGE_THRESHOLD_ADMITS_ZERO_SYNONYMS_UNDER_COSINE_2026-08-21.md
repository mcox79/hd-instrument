# **I PROPOSED A METRIC CHANGE WITH THE CAP RE-DERIVED. MEASURED ON 999 PAIRS, THE ANSWER IS NO: A THRESHOLD THAT ADMITS NO RELATED PAIR ADMITS `0 of 120` TRUE SYNONYMS UNDER COSINE, AND ONLY `8 of 120` UNDER EUCLID. THE CAP STAYS UNDER EITHER METRIC.**

**Two turns ago I said the testable proposal was a metric change with the no-false-merge guarantee
re-established on the new scale. This is that measurement, and it refuses my own proposal.**

---

## 1. THE STRATA, FROM HUMAN RATINGS RATHER THAN HAND-PICKED PAIRS

*SimLex-999 graded 0-10. **All 999 pairs are covered by the norms**, so nothing is dropped.*

| stratum | n | cosine mean | euclid mean |
|---|---|---|---|
| **SYNONYM** (rating >= 8) | 120 | **0.627** | **2.712** |
| **RELATED** (4-6) | 235 | 0.551 | 3.804 |
| **UNRELATED** (< 2) | 217 | 0.360 | 4.456 |

**Both metrics order the three strata correctly** *(cosine rising, euclid falling as relatedness
rises)*. **The graded signal below the ceiling is real on both, exactly as
`grounded_similarity.py` says.**

## 2. 🔻 **THE GUARANTEE TEST -- AND IT REFUSES MY PROPOSAL**

***The cap exists so that no NON-synonym can ever reach the 0.50 same-idea/merge threshold. So ask
each metric: set the bar high enough to admit ZERO related pairs -- how many TRUE SYNONYMS still get
through?***

| metric | bar that admits no RELATED pair | TRUE SYNONYMS admitted |
|---|---|---|
| **cosine** | must exceed **0.979** | **0 of 120 -- `0.0%`** |
| **euclid** | must be under **1.526** | **8 of 120 -- `6.7%`** |

> ### **UNDER COSINE, A NO-FALSE-MERGE THRESHOLD ADMITS NOTHING AT ALL. The module's *"not something a different threshold on this SAME metric can fix"* is now confirmed on 999 pairs instead of 6 -- and it is STRONGER than it claimed: the survivable threshold has an empty pass set.**

**Euclid is better and still nowhere near enough.** *`6.7%` of synonyms is not a basis for identity
merges.* ***So the cap stays under either metric, and my proposal to re-derive it is answered NO for
its stated purpose.***

## 3. 🎯 WHAT EUCLID IS STILL FOR

**Its advantage is in the GRADED sub-ceiling band, which is the part the module says is genuine:**
*rho `0.2876` vs cosine's `0.2176` on 829 shared pairs.* **That is a better RELATEDNESS signal, not a
licence to assert identity.** *The two claims were always separate and I had been running them
together.*

## 4. ⚠️ ONE MORE THING THE NUMBERS SAY ABOUT COSINE

**UNRELATED pairs reach a 95th percentile cosine of `0.912`.** *Pairs humans rate below 2 out of 10.*
**That is the "dominant shared concreteness axis" the module warns about, measured: cosine on these
12 dims is compressed into a narrow high band where almost everything looks similar.** *Euclid's
unrelated mean of `4.456` against a synonym mean of `2.712` is a far wider working range.*

## TLDR

Two turns ago I suggested that if we measured distance a better way, we might be able to lift a
safety limit that stops the system claiming two words are the same thing. **I measured it, and the
answer is no.**

The test is simple: set the bar high enough that **no merely-related pair** sneaks through, then count
how many genuine synonyms still make it. **Under the current measure, the answer is none at all —
zero out of a hundred and twenty.** Under the better measure it's eight. **Neither is a basis for
deciding two words mean the same thing.**

**So the safety limit stays, whichever way we measure.** My own proposal is refused by its own test.

**What the better measure is still good for** is the softer question — *how related are these two
things* — where it scores meaningfully higher. Those were always two different jobs and I'd been
running them together.

**One striking thing fell out of it:** under the current measure, word pairs that humans rate as
almost completely unrelated still score 0.91 out of 1. **Almost everything looks similar to
everything.** That is a real, measured reason the safety limit was needed in the first place.

## QUESTIONS

None. *A proposal of mine, answered by measurement.*

## NEXT STEPS

1. **Do not propose lifting or re-deriving the `0.45` cap via a metric change.** *Measured: `0.0%`
   and `6.7%` synonym pass rates under a no-false-merge bar.*
2. **Euclid's case is the GRADED band only** -- `0.2876` vs `0.2176`. *Keep that claim separate from
   identity.*
3. *Method note: **the module's own six example pairs suggested euclid might rescue the ceiling; 999
   human-graded pairs say it does not.** Six pairs chosen to illustrate a problem are not a sample
   for testing a fix to it.*
