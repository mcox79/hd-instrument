# **NOT ONE STRUCTURAL RULE EVER VARIES ITS ANSWER. THE `UNMET` BRANCHES FIRE AT `36.4%` PRECISION AGAINST A `63.9%` BASE RATE -- THEY ARE WORSE THAN NOT FIRING AT ALL.**

**The cascade is at chance because it is not judging items. It is ROUTING them into buckets that each
carry a fixed conclusion, and two of the three buckets carry the wrong one.**

---

## 1. WHAT EACH DECIDING RULE ACTUALLY EMITS

| deciding rule | n | right | acc | predictions emitted |
|---|---|---|---|---|
| `abstain_fallback_to_lexicon` | 16 | 6 | `0.375` | UNMET 10, AMBIG 2, NONE 3, MET 1 |
| **`same_class_same_referent`** | 9 | **7** | **`0.778`** | 🔒 **`MET` x9 -- CONSTANT** |
| **`referent_mismatch`** | 8 | 3 | `0.375` | 🔒 **`UNMET` x8 -- CONSTANT** |
| **`opposed_class_same_referent`** | 2 | 0 | `0.000` | 🔒 **`UNMET` x2 -- CONSTANT** |
| **`grounded_result_class`** | 1 | 1 | `1.000` | 🔒 **`UNMET` x1 -- CONSTANT** |

> # **EVERY STRUCTURAL RULE IS A CONSTANT WITHIN ITS OWN POPULATION. THERE IS NO PER-ITEM JUDGEMENT ANYWHERE IN THE CASCADE -- ALL OF THE SIGNAL IS IN *WHICH RULE FIRES*.**

*I initially wrote that `same_class_same_referent` was "the only rule that varies". **It emits `MET`
nine times out of nine.** Corrected before it left this note.*

**AND THIS IS BY DESIGN, NOT A BUG.** *A rule named "same verb class, same referent" exists precisely to
conclude MET. The finding is not that the branches are constant -- it is what follows from it.*

## 2. 🔑 **WHAT FOLLOWS: A BRANCH THAT FIRES MUST BEAT THE ANSWER YOU GET BY NOT FIRING**

**The bank is `23/36` = `63.9%` MET. "Say MET and go home" IS the majority floor.** *So any branch that
fires and says `UNMET` is only worth having if it is right more often than `63.9%`.*

| | precision | verdict |
|---|---|---|
| **MET branch** (`same_class_same_referent`) | **`7/9` = `77.8%`** | ✅ **beats the base rate -- this rule earns its place** |
| **UNMET branches** (3 rules, 11 items) | 🔻 **`4/11` = `36.4%`** | 🔻 **WORSE THAN NOT FIRING** |

> ## **THE ONE RULE THAT CONCLUDES "IT WENT WELL" WORKS. ALL THREE RULES THAT CONCLUDE "IT WENT BADLY" ARE WORSE THAN SILENCE.**

*That is the `52.6%` from the previous note, decomposed: a good branch and three bad ones, averaged.*

## 3. 🚫 **THE OBVIOUS "FIX" IS TEST-SET FITTING AND I AM RECORDING IT SO NOBODY PROPOSES IT LATER**

*"The UNMET branches are backwards -- flip them to MET."* **Two reasons no:**

1. **It does not even work: `20/36` = `0.5556`, still below the `0.6389` floor.**
2. **It is fitting the evaluation.** *Choosing a branch's label by which label scores better ON THE BANK
   YOU ARE SCORED ON is not a repair; it is memorising the answer key. The label has to follow from the
   mechanism.*

## 4. WHAT THIS SAYS TO DO

| | |
|---|---|
| ✅ **the `MET` branch is the working part of this system** | *`77.8%` on 9 items -- small, but it is the ONLY component on this line that beats its own base rate* |
| 🔻 **the `UNMET` branches should be examined for whether they should fire AT ALL** | *not "flip the label" -- ask what evidence a rule has that an outcome was NEGATIVE, given that `referent_mismatch` fires precisely when the mechanism FAILED TO ESTABLISH who the outcome belongs to* |
| ⚠️ **and note the shape of that** | ***`referent_mismatch` is a FAILURE CONDITION being read as EVIDENCE OF A NEGATIVE OUTCOME.*** *"I could not work out whose outcome this was" is not the same fact as "the outcome was bad", and the code treats them as one.* |

## 5. ⚠️ LIMITS

1. **n = 9 / 8 / 2 / 1 per branch.** *The two smallest branches carry almost no information. `77.8%` vs
   `36.4%` rests on 9 and 11 items.*
2. **"Constant within its population" is measured on 36 items**, not proven in general -- though for
   `same_class` (9/9 one label) and `referent_mismatch` (8/8) coincidence is unlikely (~0.2%, ~0.4%),
   and the source docstring independently confirms `referent_mismatch -> UNMET` is structural.
3. **One bank. Every number this session comes from the same 36 items.**
4. **I have not shown the UNMET branches would be better SILENT** -- items falling to the lexicon score
   `0.375`, statistically indistinguishable from the `0.364` they get now. *Removing them is a
   hypothesis, not an established improvement.*

## TLDR

Yesterday I found the judging machinery is no better than a coin flip. Today I took it apart to see
why, and the answer is that **it never actually judges anything.**

It works by sorting each story into one of four bins, and **every bin has a fixed answer written on it.**
Nothing looks at the individual story and decides. All of the intelligence is in the sorting.

**One bin works well.** The bin meaning "the same kind of action happened to the same person" always
answers "it went well", and it is right about 78% of the time — better than the 64% you get by simply
always answering "it went well". That bin is earning its keep.

**The three bins that answer "it went badly" are right 36% of the time.** That is worse than saying
nothing at all, because the safe default already beats them. **They are actively costing us.**

**The most revealing one:** a bin fires whenever the system *fails to work out whose outcome it is
looking at* — and that failure is written down as evidence that things went badly. **"I couldn't tell"
and "it went wrong" are being treated as the same fact.** They are not.

**One tempting shortcut that I want on the record as refused:** just relabel the bad bins. It doesn't
even work (it lands at 56 out of 100, still short of 64), and worse, choosing labels because they score
better on the very test you're graded on is memorising the answer key, not fixing anything.

## QUESTIONS

None.

## NEXT STEPS

1. 🎯 **Ask what positive evidence any `UNMET` branch has.** *`referent_mismatch` is the clear case: it is
   a FAILURE CONDITION serving as EVIDENCE. The brain-framed question is what a reader actually
   concludes when they cannot tell whose outcome a sentence describes -- and the answer is not "it went
   badly", it is "keep reading".*
2. **Do not touch the `MET` branch.** *It is the only thing on this line beating its own base rate.*
3. *Method note: **I called a rule "the only one that varies" while its own printout showed nine
   identical predictions.** The table was correct and I read a summary of it instead of the row.*
