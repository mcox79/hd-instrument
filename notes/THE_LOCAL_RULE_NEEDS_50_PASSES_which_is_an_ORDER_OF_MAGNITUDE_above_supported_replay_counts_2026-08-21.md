# **THE LOCAL RULE NEEDS ~50 PASSES TO BE WORTH USING. THE REPLAY LITERATURE SUPPORTS SINGLE DIGITS. THAT GAP IS THE HONEST COST OF LAST TURN'S RESULT.**

**Last turn the biologically plausible local rule beat both the incumbent and the pseudo-inverse, and
I flagged the open question myself: 200 epochs is not one-shot, and one-shot encoding is the
hippocampus's signature. This measures how few passes it actually needs. The answer is not
encouraging, and it is better to have it now than after building on it.**

---

## 1. THE SWEEP

*d=256, dg=1024, N=400, within-family overlap high, cue = 20% of units. Metric = the ungameable
margin (target minus nearest same-family sibling).*

| passes | 1 | 2 | 3 | 5 | 8 | 13 | **21** | **50** | 100 | 200 |
|---|---|---|---|---|---|---|---|---|---|---|
| **margin** | **−0.1019** | −0.0927 | −0.0853 | −0.0700 | −0.0487 | −0.0147 | **+0.0294** | **+0.0860** | +0.0973 | +0.0975 |

**Reference points: the raw cue scores +0.0723; the one-shot Hebbian incumbent scores −0.1021.**

- **crosses zero (stops merging) at ~15-21 passes**
- **beats the raw cue at ~50 passes**
- **saturates by 100**

## 2. ✅ **A CONSTRAINT CHECK THAT PASSES, AND IT IS A GOOD ONE**

**At 1 pass the local rule scores −0.1019. The one-shot Hebbian incumbent scores −0.1021.**

***They agree to 2 in 10,000 -- because one delta step from `W = 0` IS the Hebbian outer product.***
**So the incumbent is exactly the one-pass special case of the local rule, confirmed numerically
rather than asserted.** *That is reassuring about both implementations: they are the same family, and
the difference between them is purely how many times the update is applied.*

## 3. 🚫 **THE COST, STATED PLAINLY**

**`ORGAN_MAP`'s D4 entry, restated after its own drill's corrections, is explicit that replay COUNT
is a free parameter to sweep and NOT the "1-3 times" the doc had previously asserted unsourced -- and
the schedules it names from the literature are Landauer & Bjork's `0,3,10` and `1,4,10`.**

> ### **THOSE ARE SINGLE DIGITS TO LOW TENS. THE RULE NEEDS ~50 TO BEAT THE RAW CUE -- AN ORDER OF MAGNITUDE MORE.**

***So "replay supplies the extra passes" is NOT currently supported at the count required.*** *That
does not kill the route, and I am not filing it as dead: the sweep was run at one scale, one overlap
level and one cue fraction, and the pass count required may fall sharply with any of them. But as it
stands the biological account of WHERE 50 passes come from does not exist.*

## 4. ⚖️ WHAT THIS DOES AND DOES NOT CHANGE

| claim | status |
|---|---|
| the incumbent Hebbian rule MERGES correlated memories (margin −0.1021) | ✅ **stands** |
| a local error-driven rule fixes it and beats the pseudo-inverse | ✅ **stands** (+0.0975 vs +0.0839) |
| **"and it is biologically plausible because it is local"** | ⚠️ **QUALIFIED -- locality is not the only constraint. 50 passes is a biological cost too, and it is unaccounted for.** |
| the fix is one-shot, like the hippocampus | 🚫 **FALSE. One pass is exactly the broken incumbent.** |

## TLDR

Last turn I found a biologically realistic learning rule that fixes our memory component, and I
flagged one worry myself: it needed two hundred passes over the data, while the brain's version of
this structure is famous for learning things in **one**. **I've now measured how few passes it
actually needs, and the answer is awkward.**

**It needs about fifty.** Below roughly fifteen it is still actively blurring memories together.
Around twenty it stops doing harm. **It only becomes better than doing nothing at all at about
fifty**, and it plateaus after a hundred.

**Fifty is far more than the brain is thought to do.** Our own reference notes give the supported
figures for memory replay as single digits — schedules like "0, 3, 10" — so "replay provides the
extra passes" doesn't hold at the number actually required. **That's an order of magnitude gap, and I
would rather record it now than after building on it.**

**One genuinely satisfying detail.** At a single pass, the new rule scores −0.1019 and the old broken
rule scores −0.1021 — **the same number.** That's because one step of the new rule *is* the old rule.
**So the thing we've been using is simply the new rule stopped after one repetition**, which is a
tidy confirmation that both implementations are what I think they are.

**What survives:** the old rule really does blur memories, and the local fix really does work and
beats the mathematically ideal alternative. **What I have to withdraw:** the implication that being
"local" made it biologically plausible. **Locality isn't the only constraint — how many times you
repeat it is a biological cost too, and ours isn't paid for.**

## QUESTIONS

None.

## NEXT STEPS

1. **Do not describe the local rule as biologically plausible without the pass count.** *Locality is
   necessary, not sufficient.*
2. **The pass count may fall with scale, overlap or cue fraction -- all unmeasured.** *That is the
   cheap next sweep, and it is the one that decides whether this route survives.*
3. *One pass = the incumbent, numerically confirmed. Useful for framing: we are not choosing between
   two rules, we are choosing how long to run one.*
