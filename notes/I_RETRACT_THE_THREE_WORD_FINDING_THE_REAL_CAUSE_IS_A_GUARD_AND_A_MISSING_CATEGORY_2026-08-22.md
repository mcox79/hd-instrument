# **I RETRACT "THE OPEN-VOCABULARY COST IS THREE WORDS". `arm` SCORES *CORRECTLY*. THE REAL CAUSES ARE A `== "UNK"` GUARD AND A MISSING `ADVERSARIAL` CATEGORY -- AND I FOUND THEM BY CALLING THE CELL'S OWN SCORER INSTEAD OF GUESSING AT IT.**

**Third correction in this thread, and the root fault was the same every time: I compared against a
function the arm does not use, and never checked that it was the right one.**

---

## 1. 🔻 **THE RETRACTION**

*I published: **"the whole open-vocabulary cost is three words -- `arm`, `hand`, `leg` -- where the real
lookup gives the more correct answer and scores worse"**, and built two further conclusions on it (a
"consumer calibrated on the component's error", and a do-not-ship verdict reasoned from that).*

***IT IS WRONG. `he broke her arm` RETURNS `BLOCK_HIGH`, WHICH IS THE GOLD ANSWER. `arm` IS NOT A
FAILURE AT ALL.***

**THE FAULT: I compared `v2.lookup_animacy` against `real_animacy_lookup`. The closed arm does not
consume `lookup_animacy`.** *It consumes `object_event_class` -- a hand map over
`GOAL_OBJECT` / `ADVERSARIAL` / `ANIMATE_HARMABLE`, a different type system entirely.* **`lookup_animacy`
was an auxiliary I found by name-matching and never verified as the arm's input.**

## 2. ✅ **THE ACTUAL PER-ITEM RESULT, from `event_type_for_item_real` with the cell's own maps**

| sentence | gold | real event stage | |
|---|---|---|---|
| she beat the game | NEUTRAL | NEUTRAL | ✅ |
| **she beat the dog** | BLOCK_HIGH | **`None`** | 🔻 |
| he broke the record | NEUTRAL | NEUTRAL | ✅ |
| **he broke her arm** | BLOCK_HIGH | **BLOCK_HIGH** | ✅ *(the word I blamed)* |
| he attacked the problem | NEUTRAL | NEUTRAL | ✅ |
| **he attacked the stranger** | BLOCK_HIGH | **`None`** | 🔻 |
| **she aided the enemy** | BLOCK_HIGH | **NEUTRAL** | 🔻 |
| **she aided the refugee** | RECIPROCITY | **`None`** | 🔻 |
| **he comforted the enemy** | BLOCK_HIGH | **NEUTRAL** | 🔻 |
| **he comforted the widow** | RECIPROCITY | **`None`** | 🔻 |
| he shot the film | NEUTRAL | NEUTRAL | ✅ |
| he shot the intruder | BLOCK_HIGH | BLOCK_HIGH | ✅ |

⚠️ **THIS IS THE EVENT STAGE, NOT THE FINAL ARM.** *6 of 12 miss here while the two-stage arm scores
`0.833`, because a `None` falls back to the governor stage which rescues some. **So these are the
localisation, not the score.***

## 3. 🔑 **THE TWO REAL CAUSES**

**(A) THE HARM ROUTE REQUIRES THE GOVERNOR TO BE *UNCLASSIFIED*.**

```python
if a["animacy"] == "inanimate":                              return "NEUTRAL"
if gov_word in force_class and gclass_narrow == "UNK":       return "BLOCK_HIGH"
return None
```

*`beat` and `attack` carry narrow class `HARM`, so `gclass_narrow != "UNK"` and the route is BLOCKED --
on the two verbs most obviously about harm.* **`break` and `shoot` are `UNK` and pass, which is exactly
why the items I blamed are the ones that work.**

**(B) ANIMACY CANNOT EXPRESS `ADVERSARIAL`.** *`enemy` resolves to `abstract`/inanimate, so
"she aided the enemy" returns `NEUTRAL` where gold is `BLOCK_HIGH`.* **The closed map has an explicit
`ADVERSARIAL` class that overrides a HELP-class governor; the animacy substitution has no way to say
it.** *The cell's own docstring says so at line 52 -- **I read past it.***

## 4. ✅ **AND THIS RESTORES THE BODY-PART FIX**

*`crack`/`wrench`/`twist` are all `UNK` **and** in `force_class`, so **the harm route WOULD fire for
`Bgap` if the patient were animate.** It is blocked only by `ankle -> inanimate -> NEUTRAL` at step 1.*

> ### **SO CORRECTING `ankle` TO ANIMATE SHOULD FIX `Bgap`, AND MY "IT ASSIGNS THE LOSING VALUE" OBJECTION WAS BUILT ON THE RETRACTED FINDING.** *The do-not-ship flag is LIFTED as to its stated reason -- though it still has not been run.*

⚠️ *And the `gov_type: RECIPROCITY` in the Bgap witness is a DIFFERENT field from `gclass_narrow`
(`crack` is `UNK` there). I flagged it as a possible cause and it is not one.*

## 5. ⚠️ LIMITS

1. **Event stage only** *(see the box in section 2).*
2. **Subset B only** -- *`Bgen` not recomputed the same way.*
3. **Computed by calling the cell's function with its module-level maps** *-- not by running the arm, so
   seed-dependent behaviour is not exercised.*
4. **Nothing here is a fix.** *Both causes are diagnosed, neither is repaired or tested.*

## TLDR

**I was wrong, and I retract it.** I told you the open-vocabulary shortfall came down to three words and
that a *more accurate* dictionary was making the system worse. **Checking properly, the word I blamed —
"arm" — comes out exactly right.**

The mistake was mine and it was basic: **I compared two lookup functions, one of which the system does
not actually use.** I found it by name, it looked right, and I never checked that it was the one feeding
the machine. Two further conclusions were then stacked on top of it.

**The real causes are quite different and more interesting.** First, the rule that detects harm only
fires when the verb is *not already recognised* — so it works for "broke" and "shot" but is switched off
for "beat" and "attacked", the two most obviously violent verbs in the set. Second, the substitute
dictionary can say whether something is alive but has no way to say "enemy", so *"she aided the enemy"*
reads as harmless.

**And this reverses my objection to the fix I parked.** For the failing group the verbs do pass that
gate, so correcting "ankle" to count as part of a living thing should work after all. **My reason for
blocking it was built on the finding I have just retracted.**

**What made the difference was calling the system's own scoring function with its own data instead of
reasoning about what it probably does.** Every wrong turn in this stretch came from the latter.

## QUESTIONS

None.

## NEXT STEPS

1. **The `== "UNK"` guard is the more interesting defect** *-- a harm detector that switches off for
   verbs already known to be harmful is worth understanding before it is changed.*
2. **`ADVERSARIAL` cannot be derived from animacy** *-- that is a genuine expressiveness gap in the
   substitution, not a lookup bug.*
3. **Re-check `Bgen` the same way** *(limit 2).*
4. *Method note: **three corrections in three turns, one root cause -- an unverified assumption about
   which function the arm consumes.** The fix was to call the arm's own code, which was available the
   whole time.*
