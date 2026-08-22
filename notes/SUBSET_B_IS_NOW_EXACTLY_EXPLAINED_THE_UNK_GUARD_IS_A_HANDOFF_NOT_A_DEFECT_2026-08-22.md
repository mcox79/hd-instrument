# **SUBSET `B`'s `0.833` IS NOW EXACTLY EXPLAINED: TEN OF TWELVE, WITH BOTH ERRORS BEING THE WORD `enemy`. AND THE `== "UNK"` GUARD I FLAGGED AS A SUSPECTED DEFECT IS A DELIBERATE HAND-OFF I SHOULD NOT TOUCH.**

**The arithmetic closes to the reported number. That is what makes this an explanation rather than
another story.**

---

## 1. THE COMBINER, READ RATHER THAN INFERRED

```python
if situation_type is not None: return situation_type, "situation"
if event_type    is not None: return event_type,    "event"
return gov_type, "governor"     # dominance-default, never erased
```

***SITUATION > EVENT > GOVERNOR.*** **So `None` from the event stage is not a failure -- it is the event
stage DECLINING, and the governor supplies the answer.**

## 2. ✅ **EVERY ITEM IN SUBSET `B`, AND THE TOTAL MATCHES**

| item | event stage | winner | final | gold | |
|---|---|---|---|---|---|
| she beat the game | `NEUTRAL` | event | NEUTRAL | NEUTRAL | ✅ |
| **she beat the dog** | `None` | **governor** | BLOCK_HIGH | BLOCK_HIGH | ✅ |
| he broke the record | `NEUTRAL` | event | NEUTRAL | NEUTRAL | ✅ |
| he broke her arm | `BLOCK_HIGH` | event | BLOCK_HIGH | BLOCK_HIGH | ✅ |
| he attacked the problem | `NEUTRAL` | event | NEUTRAL | NEUTRAL | ✅ |
| **he attacked the stranger** | `None` | **governor** | BLOCK_HIGH | BLOCK_HIGH | ✅ |
| 🔻 **she aided the enemy** | `NEUTRAL` | event | **NEUTRAL** | **BLOCK_HIGH** | 🔻 |
| she aided the refugee | `None` | governor | RECIPROCITY | RECIPROCITY | ✅ |
| 🔻 **he comforted the enemy** | `NEUTRAL` | event | **NEUTRAL** | **BLOCK_HIGH** | 🔻 |
| he comforted the widow | `None` | governor | RECIPROCITY | RECIPROCITY | ✅ |
| he shot the film | `NEUTRAL` | event | NEUTRAL | NEUTRAL | ✅ |
| he shot the intruder | `BLOCK_HIGH` | event | BLOCK_HIGH | BLOCK_HIGH | ✅ |

> # ✅ **10 / 12 = `0.8333`. THE CELL REPORTS `B_two_stage_real = 0.833`. THE ARITHMETIC CLOSES, AND BOTH ERRORS ARE THE SAME WORD: `enemy`.**

## 3. 🔑 **SO THE `== "UNK"` GUARD IS A HAND-OFF, NOT A DEFECT -- DO NOT TOUCH IT**

*Last turn I flagged it as "a harm detector that switches off for the most violent verbs" and said it
was worth understanding before changing.* ***Understanding it says: leave it alone.***

**`beat` and `attack` carry narrow class `HARM`, so the event stage DECLINES and the governor -- which
already knows those verbs -- answers correctly.** *The guard exists to stop the event stage
double-handling verbs the governor covers.* ***Removing it would have the event stage overrule the
governor on exactly the two items the governor gets right.***

⚠️ **NOTE WHAT ALMOST HAPPENED: I had it queued as "the more interesting defect". It is not a defect at
all, and two turns ago I would have fixed it.**

## 4. 🎯 **THE ONE REAL DEFECT IN `B`: ANIMACY CANNOT SAY `ADVERSARIAL`**

**`enemy` resolves to `abstract` -> inanimate -> the event stage confidently returns `NEUTRAL` and WINS
over a governor that would have said otherwise.** *Gold is `BLOCK_HIGH`: aiding an enemy is harm.*

**The closed map has an explicit `ADVERSARIAL` class that fires REGARDLESS of governor -- the cell's
docstring says so at line 52.** ***Animacy has no way to express it. That is an EXPRESSIVENESS gap in
the substitution, not a lookup bug, and no amount of better animacy data fixes it.***

## 5. ⚠️ LIMITS

1. **The two governor-supplied rows assume `pred_gov` predicts `HARM` for `beat`/`attack` and
   `HELP`->`RECIPROCITY` for `aid`/`comfort`.** *That is what their narrow classes say and what
   `A_governor = 0.962` implies, but `pred_gov` is a TRAINED classifier I did not re-train.*
   **The total closing to `0.833` is strong evidence, not proof.**
2. **Subset `B` only.** *`Bgen`'s `0.750` is NOT explained by this pass.*
3. **No arm was run.** *Event stages computed by calling the cell's own function with its own maps.*

## TLDR

**The 83% is now fully accounted for: ten of twelve right, and both mistakes are the same word —
"enemy".**

The system decides in layers: if it can work out the event, that wins; otherwise it falls back on what
it knows about the verb. **"She beat the dog" works because the event layer stays quiet and the verb
layer answers.**

**That settles the thing I flagged last turn as the more interesting defect — it is not a defect.** The
rule that looked like "the harm detector switches off for the most violent verbs" actually means "don't
second-guess the verb layer when it already knows this verb". **Two turns ago I would have changed it,
and it would have broken the two items it currently gets right.**

**The one genuine problem is that the stand-in dictionary can say whether something is alive but cannot
say "enemy".** So *"she aided the enemy"* reads as harmless. **No better animacy data fixes that** — it
is a missing concept, not a missing entry.

**What makes this an explanation rather than another story is that the numbers add up to the reported
score.** The last three turns produced accounts that were internally plausible and did not.

## QUESTIONS

None.

## NEXT STEPS

1. **`ADVERSARIAL` is a genuine expressiveness gap** *-- worth stating as a requirement on any lexical
   substitute, not patched with a word list.*
2. **`Bgen`'s `0.750` is the remaining loose end.**
3. *Method note: **the arithmetic closing to `0.833` is what separates this from the last three
   attempts.** None of those summed to the reported number, I never checked, and that check was
   available every time.*
