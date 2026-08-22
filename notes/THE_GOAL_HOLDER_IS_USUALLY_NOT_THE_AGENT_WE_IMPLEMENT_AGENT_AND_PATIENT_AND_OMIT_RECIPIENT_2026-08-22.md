# **IN ALL 5 FAILURES, SOMEONE ELSE PERFORMS THE ACT THAT SATISFIES THE GOAL. WE RECOGNISE EXACTLY TWO GRAMMATICAL POSITIONS -- SUBJECT AND DIRECT OBJECT -- AND NARRATIVE GOAL SATISFACTION ARRIVES IN A THIRD.**

**A project about whether GOALS are achieved has implemented the AGENT and PATIENT roles and omitted the
one thematic role literally called RECIPIENT/GOAL.**

---

## 1. FIRST: IS THE EVAL EVEN ANSWERABLE? *(asked before blaming the mechanism)*

**Yes, and not marginally.** *The passages say `"the fulfillment of his greatest wish"`, `"Now you have a
heart that any man might be proud of"`, `"together they got the child out"`.* **The gold is fair and the
system is genuinely wrong.** *Worth establishing -- an unanswerable item set would have made every
number this week meaningless, and it costs five minutes to check.*

## 2. 🔑 THE FIVE `referent_mismatch` ERRORS SHARE ONE EXACT PATTERN

| item | goal holder | **who performs the fulfilling act** | where the goal-holder appears |
|---|---|---|---|
| `woz_scarecrow_brains` | Scarecrow | **the Wizard** *gives* | `"I have given YOU ... brains"` -- **RECIPIENT** |
| `woz_tin_woodman_heart` | Woodman | **Oz** *puts* | `"in the WOODMAN'S breast"` -- **POSSESSOR in a PP** |
| `lw_ice_rescue_amy` | Amy | **Jo** *drags* | `"they got THE CHILD out"` -- object of a DIFFERENT verb |
| `agg_anne_diana_bosom_friend` | Anne | **Diana** *agrees* | addressee of `"I guess so"` -- **BENEFICIARY** |
| `lw_beth_piano_invite` | Beth | **Mr. Laurence** *invites* | `"some of YOUR GIRLS"` -- **GROUP MEMBERSHIP** |

> # **NOT ONE OF THE FIVE HAS THE GOAL-HOLDER AS SUBJECT OR DIRECT OBJECT OF THE OUTCOME VERB. THE TEST ACCEPTS ONLY THOSE TWO POSITIONS.**

## 3. ✅ CONFIRMED AT THE SOURCE, NOT INFERRED FROM THE SYMPTOM

```
hdlab/goal_typing.py:776   SUBJECT_IS_REFERENT_CLASSES = {...}
hdlab/goal_typing.py:777   OBJECT_IS_REFERENT_CLASSES  = {...}
```

**Two categories. That is the entire inventory.** *And the role labeler has no frame for the canonical
recipient verb either -- `frame_slot_role("give", slot)` returns `none` for `S1/S2/S3/SUBJ/OBJ/IOBJ/
RECIPIENT/BENEFICIARY`, all eight.*

**So `referent_mismatch` is not a bug in the sense of a coding error. It is a MISSING PRIMITIVE
reporting itself honestly**: the mechanism looked in the only two places it knows, did not find the
goal-holder, and said so. *The defect is that "not in the two places I check" was then wired to mean
`UNMET`.*

## 4. 🧠 THE BRAIN FRAMING, WHICH SAYS THE SAME THING

**Thematic-role assignment during comprehension is not two-way.** *A reader tracking "Scarecrow wants
brains" and meeting "I have given you a lot of bran-new brains" resolves `you -> Scarecrow` in the
RECIPIENT slot and marks the goal SATISFIED -- the agent being someone else is not merely tolerated, it
is the normal case for goals involving other people.* **In narrative, wanting something usually means
wanting someone else to do something.**

***And a reader who genuinely cannot bind the referent does not conclude the goal FAILED. They hold it
open and read on.*** *That is the same conclusion the previous note reached from the numbers -- a
failure condition is being read as evidence of a negative outcome -- arrived at independently from
comprehension rather than from a contingency table.*

## 5. ⚠️ **AND IT STILL CANNOT CLEAR THE FLOOR ALONE. CEILING FIRST, AS ALWAYS.**

| | |
|---|---|
| fixing all 5 `referent_mismatch` errors | `22/36` = **`0.6111`** 🔻 *below the `0.6389` floor* |
| if it also fixes the 2 `opposed_class` items | `24/36` = `0.6667` ✅ *clears -- **but that reach is UNMEASURED*** |

**This is the same ceiling established two notes ago, and the precision of the diagnosis does not change
the arithmetic.** *A better-understood defect with five items behind it still has five items behind it.*

⚠️ **Whether the missing role also explains some of the 11 items where NO GOAL was recognised at all is
untested, and that is where the reach would come from.** *That is the measurement to do before any
build.*

## 6. LIMITS

1. **5 items, hand-read by me.** The pattern is exact across all five, which is why it is worth
   reporting at n=5 -- but it is n=5.
2. **`frame_slot_role("give") -> none` for all 8 slots may mean "no frame for `give`" rather than "no
   recipient role in the system".** *I checked one verb; I have not enumerated the frame inventory.*
3. **I have NOT built or tested a recipient-role check.** *Everything above is diagnosis. Three times
   this session a confident mechanism story survived until it was measured, and twice it did not.*

## TLDR

The system judges whether a character got what they wanted. To do that it looks for the character in the
sentence describing what happened — but **it only knows how to look in two places: who did the action,
and who it was done to.**

I read the five failing stories by hand. **In every single one, somebody else performs the act that
grants the wish.** The Scarecrow wants brains and *the Wizard* gives them. The Tin Woodman wants a heart
and *Oz* puts one in. Amy is drowning and *Jo* pulls her out. Anne wants a friend and *Diana* says yes.

In each case the character is present in the sentence — as the person *receiving*, or the person the
thing was done *for*. **That position isn't one the system knows how to check**, so it concludes the
character isn't there, and from that concludes the wish did not come true.

**This is the normal case, not an edge case. Wanting something usually means wanting someone else to do
something.** A project built around whether goals get achieved has implemented "who acted" and "who was
acted on", and left out the role that literally means "the one it was for".

**Being honest about size:** fixing this exactly is still not enough to pass. It accounts for five of the
36 questions and we need seven. It only becomes decisive if the same missing piece also explains some of
the 11 questions where the system failed to spot a goal at all — **which I have not checked, and which is
the thing to measure before building anything.**

## QUESTIONS

None.

## NEXT STEPS

1. 🎯 **Hand-read the 11 NO-GOAL items and ask whether the goal-holder sits in a recipient/beneficiary
   position there too.** *That is a 15-minute read and it decides whether this is a 5-item curiosity or
   the main lever.*
2. 🚫 **Do not build the recipient check yet.** *Its measured reach is 5 items and the gap is 7.*
3. *Method note: **checking that the eval was answerable took five minutes and was the right first
   move** -- had the passages been unanswerable, every number from this week would have been about the
   bank rather than the system.*
