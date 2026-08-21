# T2c -- **OUR COREFERENCE "SALIENCE" IS PROVABLY JUST A MENTION-COUNT. THE RECENCY TERM CANNOT OVERTURN A SINGLE VOTE, AND ACROSS 89 COMPETITIVE DECISIONS IT NEVER DID.**

**No run. An analytic result plus one number the cell already recorded and its verdict never
mentioned.** This answers T2b's closing question -- *why is a syntactic constraint beating both
brain-motivated arms?*

---

## 1. THE FORMULA, AT HEAD

`hdlab/coreference_resolver.py:192`

```python
def salience(self, now: int) -> float:
    """Centering salience = count + beta * exp(-lambda * dist) (frequency-primary, recency tie-break)."""
    return self.count + OVERLAY_BETA * math.exp(-OVERLAY_TIEBREAK_LAMBDA * (now - self.last_pos))
```

`hdlab/state_of_mind.py:125-126`

```python
OVERLAY_BETA = 0.5              # recency tie-break weight (frequency counts dominate)
OVERLAY_TIEBREAK_LAMBDA = 0.1   # tie-break decay rate
```

## 2. 🔒 **THE PROOF: THE RECENCY TERM CANNOT CHANGE ANY DECISION UNLESS COUNTS ARE EXACTLY TIED**

For `dist >= 0`, `exp(-0.1 * dist) ∈ (0, 1]`, so the recency bonus lies in **`(0, 0.5]`**.
`count` is an **integer**. Therefore, whenever `count_A >= count_B + 1`:

```
salience_A  >=  count_A            >=  count_B + 1
            >   count_B + 0.5      >=  salience_B
```

**➡️ A ONE-MENTION LEAD IS MATHEMATICALLY UNBEATABLE BY RECENCY. The term is a pure tie-break --
not a weighting, not an integration, not a competition.** *This is the same class as the
divisive-normalisation result `ORGAN_MAP` §3 already records: a mechanism that cannot move the
quantity it is supposed to move. It needs no experiment to establish -- and it is stated in the
code's own comment: **"frequency counts dominate."***

## 3. 📊 **AND THE CELL MEASURED IT, AND ITS VERDICT NEVER SAID SO**

`data/exp_coref_cue_based_retrieval_actr_activation_v1/metrics.json`:

```
"D2_salience_equals_argmax_count_fraction": 1.0
```

**On ALL 89 competitive decisions the salience arm's pick is IDENTICAL to plain argmax-of-count.**
Not "usually" -- **1.0**. *The tie-break never even broke a tie in a way that changed an answer.*
**So `base_salience` is not an approximation of a count. On this evidence it IS a count.**

## 4. 🧠 **WHY THE SYNTACTIC RULE WINS — AND IT IS NOT THE CONTEST ANYONE THOUGHT**

`ORGAN_MAP`'s E3 entry gives the brain-side cue **ORDERING**, explicitly *"an ORDERING, not
numbers"*:

> **agreement > implicit causality > grammatical role > recency > coherence relation**
> (Lewis & Vasishth 2005; McElree SAT; Jäger, Engelmann & Vasishth 2017)

| cue | in our formula? |
|---|---|
| agreement | ❌ (used only as a hard pre-filter for candidacy, not as a graded cue) |
| implicit causality | ❌ |
| grammatical role | ❌ (`clause_role` is tracked and the source says it is **"inert to the salience pick"**) |
| **recency** — 4th of five | ⚠️ **present but PROVABLY INERT** |
| coherence relation | ❌ |
| **mention count** | ✅ **the only live cue — and it is NOT ON THE BRAIN'S LIST AT ALL** |

**➡️ SO `base_principle_b` (0.7191) DID NOT BEAT A CUE-INTEGRATION ACCOUNT. IT BEAT A
MENTION-COUNTER.** *A structural filter that removes an impossible candidate converts a coin flip
into a certainty; a counter that mis-ranks still answers wrong. That is the whole gap.*

**AND IT CORRECTS MY T2 FRAMING FOR THE THIRD TIME.** I called the target *"our invented β=0.5/λ=0.1
arithmetic."* **There is no arithmetic to replace.** There is a count, plus a term that cannot fire.

## 5. WHAT THIS DOES **NOT** SAY

- **NOT that counting is a bad cue.** It scores 0.5618 vs a 0.5281 floor -- *weak, but the point
  here is what it IS, not how it ranks.*
- **NOT that ACT-R would win if the baseline were stronger.** T2b's three defects (n=89, unusable
  scramble, unswept parameters) still stand and still block that inference.
- **NOT that `β` should be raised.** *That would be tuning a number we invented. The brain side
  supplies an ORDERING and we implement none of its top three cues -- **the missing cues are the
  finding, not the coefficient.***

## TLDR

Earlier I asked why a plain grammar rule beats our brain-inspired methods at working out who "he"
refers to. **The answer is that there was never really a contest.**

Our method is described as "salience" — a blend of how often something is mentioned and how recently.
**I checked the arithmetic, and the recency half can never change the answer.** The recency bonus is
capped at half a point, and mention-counts go up in whole numbers — so **anything mentioned even one
extra time wins automatically, no matter how long ago.** Recency can only matter in an exact tie.

**The experiment had already measured this and nobody said it out loud:** across all 89 hard cases,
our "salience" method picked **exactly** the same answer as simply counting mentions. Every single
time.

So what the grammar rule beat was a mention-counter. And the reading research lists five cues that
people actually use — agreement, implicit causality, grammatical role, recency, coherence. **We
implement none of the top three. The fourth is in our code but mathematically inert. And the one
thing we do use — counting mentions — isn't on the list at all.**

**This corrects my own framing for the third time tonight.** I kept describing the thing to replace
as "our invented formula." There is no formula to replace — there is a count and a decoration.

Worth being clear: this doesn't mean counting is useless, and it doesn't rescue the brain-inspired
version, which still has the problems found earlier. **The finding is which cues are missing, not
which number is wrong.**

## QUESTIONS

None.

## NEXT STEPS

1. **The build target is CUES, not coefficients** -- grammatical role is tracked already
   (`clause_role`) and the source says it is *inert to the pick*. **Making an already-tracked field
   actually count is the cheapest real step available.**
2. **Report `D2_salience_equals_argmax_count_fraction` in any future coref cell.** *A treatment that
   is bit-identical to a trivial baseline is a reachability failure, and this one was recorded and
   passed over.*
3. Do not raise `β`. Tuning an invented coefficient is not the gap.
