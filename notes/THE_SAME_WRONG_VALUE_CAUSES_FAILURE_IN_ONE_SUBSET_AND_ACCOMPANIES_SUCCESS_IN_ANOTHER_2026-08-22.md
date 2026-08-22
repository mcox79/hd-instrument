# **CALLING A BODY PART AN `object` DEMONSTRABLY *CAUSES* THE FAILURE IN ONE SUBSET AND *ACCOMPANIES THE PERFECT SCORE* IN ANOTHER. I CANNOT RESOLVE THAT WITHOUT RUNNING THE ARMS, AND IT WALKS BACK MY LAST CONCLUSION TO A HYPOTHESIS.**

**Read from the cell's own saved per-item witnesses -- the strongest evidence available without a
re-run, and it complicates rather than confirms.**

---

## 1. ✅ **`Bgap` IS NOW FULLY EXPLAINED, FROM THE CELL'S OWN WITNESSES**

*All 6 `Bgap` items, seed 0, identical across seeds:*

```
gov_type: RECIPROCITY | event_type: NEUTRAL | patient_category: object | final_type: NEUTRAL
```

**And the pairs are SAME-VERB, DIFFERENT-PATIENT by construction:**

| non-harm member | harm member |
|---|---|
| "she cracked **the vase**" -> `NEUTRAL` | "she cracked **her ankle**" -> `BLOCK_HIGH` |
| "he wrenched **the lever**" -> `NEUTRAL` | "he wrenched **her elbow**" -> `BLOCK_HIGH` |

> ### **THE PATIENT IS THE ONLY THING THAT DIFFERS, SO THE PATIENT CATEGORY IS THE ONLY POSSIBLE DISCRIMINATOR. `ankle` RESOLVES TO `object`, BOTH MEMBERS COLLAPSE TO `NEUTRAL`, AND THE PAIR SCORES `0.500` BY CONSTRUCTION.**

⚠️ **AND I ALMOST CALLED `gov_type: RECIPROCITY` A SECOND INDEPENDENT CAUSE.** *It does look like a
mis-typing -- `crack`/`wrench`/`twist` are force verbs -- but **it is IDENTICAL for both members of
every pair, so it cannot break a within-pair discrimination.** A mislabel, not the cause. *(The verbs
ARE registered, line 149, so this is a typing question, not a coverage one.)*

## 2. 🔻 **AND THAT CONTRADICTS WHAT I CONCLUDED LAST TURN**

| subset | what the patient lookup returns | score |
|---|---|---|
| **`Bgap`** (`ankle`, `elbow`, `knee`) | **`object`** | 🔻 **`0.500` -- and the witness PROVES `object` causes it** |
| **`B` / `Bgen`** (`arm`, `hand`, `leg`) -- CLOSED | **`object`** | ✅ **`1.000`** |
| **`B` / `Bgen`** (`arm`, `hand`, `leg`) -- REAL | `body_part` | 🔻 `0.833` / `0.750` |

> # 🔻 **THE SAME VALUE -- A BODY PART CALLED `object` -- CAUSES FAILURE IN ONE SUBSET AND ACCOMPANIES A PERFECT SCORE IN ANOTHER. ON ITS FACE THAT IS CONTRADICTORY.**

**LAST TURN I CONCLUDED "the consumer is calibrated on the component's error". THAT IS NOW A
HYPOTHESIS, NOT A FINDING** -- *because in `Bgap` the identical error is demonstrably fatal. **A
consumer calibrated to exploit `object` for `arm` would have to be exploiting it for `ankle` too, and
it plainly is not.***

*Candidate explanations I can state but NOT choose between without running the arms:* **(a)** ~~*B's pairs may not be same-verb/different-patient*~~ **REFUTED, see 4b;** **(b)** *the two
lookups may differ on OTHER fields I did not compare (`agent_capable` matched, but the event assembly
may read more);* **(c)** *the closed lexicon may win B for a reason unrelated to `arm` at all -- **B has
TWO errors and only ONE disagreeing word, so at least one B error already has another cause.***

## 3. ⚠️ WHAT THIS DOES TO THE PROPOSED FIX

✅ **FOR `Bgap` THE FIX IS NOW STRONGLY SUPPORTED, NOT JUST PLAUSIBLE.** *The witness shows the exact
mechanism: wrong patient category -> both members NEUTRAL -> chance. Correcting `ankle` to
`body_part` addresses precisely that, and the verb is controlled within pair.*

🔻 **FOR `B`/`Bgen` IT REMAINS UNSAFE.** *The direction of the association there is unexplained, and
"unexplained" is not "harmless".*

***SO THE DO-NOT-SHIP FLAG STANDS -- but the reason has changed: not "the fix assigns a losing value"
(too strong, `Bgap` refutes it) but "the B/Bgen behaviour is not understood, and shipping into a
mechanism I cannot explain is how the last three hours went".***

## 4. 🔻 **AND THE RE-ANALYSIS I NEED IS BLOCKED BY A DOCUMENTED PATTERN**

***`witness_Bopen` and `witness_Bgap` are saved. `witness_B` and `witness_Bgen` ARE NOT.*** *The cell
saved per-item detail for the two subsets it was ABOUT and not for the reference subsets -- which is
`CLAUDE.md`'s "save the population you scored" failure, now with a fourth instance and a concrete
cost: **the contradiction in section 2 is unresolvable from disk and needs a re-run, which resume
turns into a no-op.***

## 4b. 🔎 **EXPLANATION (a) IS REFUTED -- CHECKED IMMEDIATELY, AND IT SHARPENS THE PUZZLE**

***`B`'s pairs ARE same-verb / different-patient, exactly like `Bgap`:***

| non-harm | harm |
|---|---|
| "he broke **the record**" -> `NEUTRAL` | "he broke **her arm**" -> `BLOCK_HIGH` |
| "she beat **the game**" -> `NEUTRAL` | "she beat **the dog**" -> `BLOCK_HIGH` |
| "he shot **the film**" -> `NEUTRAL` | "he shot **the intruder**" -> `BLOCK_HIGH` |

**So the patient IS the discriminator in `B` too, and the contradiction is REAL rather than an artifact
of different designs.** *12 items = 6 pairs; `0.833` = exactly ONE pair wrong, and `arm` is the only
word whose value differs between the lookups -- so **the `broke` pair is the failing one**.*

### ➡️ **THE REFINED HYPOTHESIS -- STATED AS A HYPOTHESIS, NOT ADOPTED**

*The one account that fits BOTH subsets: **the harm route may fire on FORCE-VERB + `object`, not on
patient animacy.***

| case | patient | governor | outcome |
|---|---|---|---|
| "broke her arm", CLOSED | `object` | `break` = force | ✅ harm |
| "broke her arm", REAL | `body_part`, `agent_capable=False` | `break` = force | 🔻 fails |
| "cracked her ankle" | `object` | `crack` typed **`RECIPROCITY`** | 🔻 fails |

***If that is right, the `RECIPROCITY` mis-typing IS causally relevant after all -- not as a within-pair
discriminator, but because it disables the same force route that carries `B`.*** ⚠️ **I HAVE NOT READ
THE ARM CODE AND AM NOT ASSERTING THIS.** *It is the first account consistent with every measurement
here, which is exactly when a story is most seductive and least verified.*

## 5. ⚠️ LIMITS

1. **Everything here is READ from saved witnesses.** *No arm was run.*
2. **Seed 0 shown; the six entries are identical across all five seeds** *(checked).*
3. **I did not compare every field of the two lookups** -- *only `animacy`, `category`, `agent_capable`.*
4. **The `RECIPROCITY` mis-typing is noted, NOT investigated.** *It is not the cause of this failure but
   it may matter elsewhere.*

## TLDR

I found the exact reason one group of tests scores at chance, from the experiment's own saved records.
**The test pairs use the same verb and change only the object** — "she cracked the vase" versus "she
cracked her ankle". So the only thing that can tell them apart is what the system thinks an ankle is.
**It thinks it is an inanimate object, so both sentences come out identical and the pair scores exactly
50%.**

**But that directly contradicts what I told you last turn.** In the other group, calling an arm an
inanimate object — the same mistake — goes with a *perfect* score. **The identical error is fatal in one
place and harmless in another.** I said last turn that the rest of the system had been built around the
mistake; **that is now a guess rather than a finding**, because if it were exploiting the mistake it
would be exploiting it for ankles too, and it clearly is not.

**So the fix I parked stays parked, but for a better reason.** For the failing group it is now strongly
supported — I can see the exact mechanism. For the other group the behaviour is simply not understood,
and shipping into a mechanism I cannot explain is precisely how the last three hours have gone.

**And I cannot settle it from what is on disk.** The experiment saved per-item records for the two
groups it was studying and not for the two it used as reference — a pattern already documented here as
a recurring cost, now with a concrete one: the contradiction needs a re-run, and re-runs replay their
saved workings instead of redoing them.

## QUESTIONS

None.

## NEXT STEPS

1. **The contradiction in section 2 is the thing to resolve**, and it needs either a real re-run or
   reading the arm code closely enough to say what B's discriminator actually is.
2. **Check whether B's pairs are same-verb/different-patient** *-- if they are not, explanation (a)
   resolves it immediately and cheaply.*
3. *Method note: **the witnesses that existed answered one subset completely and the ones that were not
   saved left the contradiction unresolvable.** The asymmetry was invisible until I needed the missing half.*
