# **BOTH OPEN-VOCABULARY SHORTFALLS NOW CLOSE EXACTLY, ON ONE CAUSE: FOUR ITEMS, ALL WITH AN *ADVERSARIAL* PATIENT -- `enemy`, `enemy`, `rival`, `thief`. AND THE CELL'S DOCSTRING NAMED THOSE EXACT THREE WORDS, WHICH I READ PAST TWICE.**

**`B` and `Bgen` are both accounted for item by item, and both totals match the reported scores.**

---

## 1. ✅ `Bgen` -- **6 / 8 = `0.750`, EXACTLY AS REPORTED**

| item | gold | event stage | what happens | |
|---|---|---|---|---|
| he crushed the deadline | NEUTRAL | `NEUTRAL` | event correct | ✅ |
| **he crushed her leg** | BLOCK_HIGH | **`BLOCK_HIGH`** | event correct | ✅ |
| 🔻 **she helped the rival** | **BLOCK_HIGH** | `None` | *declines (`help` = HELP, not UNK)* -> governor says HELP | 🔻 |
| she helped the neighbor | RECIPROCITY | `None` | -> governor | ✅ |
| he smashed the puzzle | NEUTRAL | `NEUTRAL` | event correct | ✅ |
| **he smashed her hand** | BLOCK_HIGH | **`BLOCK_HIGH`** | event correct | ✅ |
| 🔻 **she comforted the thief** | **BLOCK_HIGH** | `None` | *declines* -> governor says HELP | 🔻 |
| she comforted the neighbor | RECIPROCITY | `None` | -> governor | ✅ |

## 2. 🎯 **ONE CAUSE ACCOUNTS FOR ALL FOUR ERRORS ACROSS BOTH SUBSETS**

| subset | errors | patient | mechanism |
|---|---|---|---|
| `B` | 2 | `enemy`, `enemy` | -> `abstract` -> event says **NEUTRAL and WINS** |
| `Bgen` | 2 | `rival`, `thief` | -> `person` -> event **DECLINES**, governor says HELP |

> ### **DIFFERENT ROUTES, IDENTICAL CAUSE: THE ANIMACY MAP CANNOT SAY *ADVERSARIAL*. THE CLOSED MAP HAS AN EXPLICIT CLASS THAT RETURNS `BLOCK_HIGH` REGARDLESS OF GOVERNOR; ANIMACY HAS NO SUCH CONCEPT.**

***THE ENTIRE OPEN-VOCABULARY COST IS FOUR ITEMS, AND EVERY ONE OF THEM HAS AN ADVERSARIAL PATIENT.***

## 3. 🔻 **AND MY RETRACTED THREE-WORD CLAIM IS NOW REFUTED ON ALL THREE WORDS**

*I claimed the cost was `arm`, `hand`, `leg`.*

| | |
|---|---|
| `he broke her arm` | ✅ **`BLOCK_HIGH`, correct** |
| `he crushed her leg` | ✅ **`BLOCK_HIGH`, correct** |
| `he smashed her hand` | ✅ **`BLOCK_HIGH`, correct** |

**All three are handled correctly by the very lookup I accused of breaking them.**

## 4. ⚠️ **AND THE ANSWER WAS IN THE DOCSTRING, NAMING THE EXACT WORDS**

*`exp_bridge1_event_assembly_open_vocab_v1`, line 52:*

> *"(**enemy/rival/thief** -> BLOCK_HIGH regardless of governor class, overriding a HELP-class governor
> like aid/comfort)"*

***THE CELL NAMES `enemy`, `rival` AND `thief` -- THE EXACT THREE WORDS BEHIND ALL FOUR FAILURES -- AND
STATES THE OVERRIDE THEY NEED. I READ PAST IT TWICE AND SPENT FOUR TURNS REDISCOVERING IT.***

**That is this project's standing prior-work rule failing at its smallest scale: not a missed archive
query, but an unread line in the file I already had open.**

## 5. ⚠️ LIMITS

1. **The governor-decided rows assume `pred_gov` types `help`/`comfort` as HELP and `beat`/`attack` as
   HARM.** *Their narrow classes say so and both totals close, but `pred_gov` is TRAINED and I did not
   re-train it.* **Both subsets closing exactly is strong evidence, not proof.**
2. **Event stages computed by calling the cell's own function with its own maps** *-- no arm was run.*
3. **`Bopen` (`1.000`) and `Bgap` (`0.500`) were explained earlier and are unchanged by this.**
4. **This diagnoses; it repairs nothing.**

## TLDR

**Both shortfalls now add up exactly, and they have a single cause: four sentences, every one of them
about helping or hurting an adversary — an enemy, a rival, a thief.**

The substitute dictionary can say whether something is alive. **It cannot say "this is an enemy."** So
*"she helped the rival"* and *"she comforted the thief"* come out as kindly acts, when the point of the
test is that they are not.

**And the three words I blamed two turns ago all work perfectly** — arm, leg and hand are each handled
correctly by the lookup I accused.

**The most uncomfortable part: the experiment's own notes name enemy, rival and thief explicitly, and
say precisely what handling they need.** It was in the file I had open, and I read past it twice while
spending four turns rediscovering it by measurement.

## QUESTIONS

None.

## NEXT STEPS

1. **State `ADVERSARIAL` as a REQUIREMENT on any lexical substitute** *-- it is a concept the source must
   carry, not a word list to extend. WordNet has no adversarial-role class; this may be a genuine reason
   the substitution cannot be complete.*
2. **The open-vocabulary frontier is now fully diagnosed** *-- `B`, `Bgen`, `Bopen` and `Bgap` all
   accounted for. Nothing here is repaired.*
3. *Method note: **read the docstring of the thing you are measuring before measuring it.** Four turns,
   three retractions, and the answer was one line above the code I was already calling.*
