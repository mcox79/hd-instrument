# **THE BODY-PART GAP HAS A PRINCIPLED FIX: WORDNET'S OWN `body_part` HYPERNYM AT THE TOP SENSE. CATCHES 3/3 OF THE DELIBERATELY-UNCOVERED WORDS AND 0/8 CONTROLS, AT A 1.2% BASE RATE.**

**A candidate fix with its error behaviour MEASURED -- not a demonstrated improvement. Read section 4
before using it.**

---

## 1. WHAT THE GAP ACTUALLY IS -- **I MISCHARACTERISED IT LAST TURN**

*I called the body-part stratum "the live frontier" as if the architecture failed there. **The cell
diagnoses it and it is not a mechanism failure at all.***

**`exp_bridge1_event_assembly_open_vocab_v1`'s own docstring: WordNet routes body-part nouns through
BODY-PART hypernyms rather than person/animal senses, so `lookup_animacy("ankle"/"elbow"/"knee")`
returns nothing.** *v2 patched SIX words via `BODY_PART_SUPPLEMENT` and **deliberately did NOT extend
it to the test words** -- "covering the test items would defeat the point of measuring the gap".*

> ### **SO `Bgap 0.500` IS AN HONESTLY-MEASURED RESOURCE HOLE THE AUTHORS CHOSE TO LEAVE OPEN. THE REAL OPEN-VOCAB RESULT IS `Bopen_two_stage_real 1.000`, lift `0.600`, bow `0.500`.**

⚠️ *The genuine open-vocabulary cost is elsewhere and smaller: `B_real 0.833` vs `B_closed 1.000`, and
`Bgen_real 0.750` vs `Bgen_closed 1.000`.*

## 2. ✅ THE FIX, AND WHY IT IS NOT A BIGGER WHITELIST

***WordNet already encodes the answer -- the same hypernym route that BREAKS the animacy lookup can be
read as a POSITIVE signal.***

```
ankle  -> synovial_joint > gliding_joint > ankle      elbow -> synovial_joint > hinge_joint > elbow
knee   -> synovial_joint > hinge_joint  > knee        hand  -> external_body_part > extremity > hand
```

**RULE: if a noun's TOP WordNet sense has `body_part` or `external_body_part` on any hypernym path ->
`animate`, `agent_capable=False`** *-- exactly the semantics `BODY_PART_SUPPLEMENT` already encodes by
hand, applied to every body part instead of six.*

## 3. 📏 **ITS ERROR BEHAVIOUR, MEASURED BEFORE PROPOSING IT**

| | **TOP-1 sense** | top-3 senses |
|---|---|---|
| the 3 DELIBERATELY-UNCOVERED gap words | ✅ **3/3** | 3/3 |
| 8 unambiguous body parts | ✅ **8/8** | 8/8 |
| **8 controls** (rock, table, dog, teacher, car, idea, river, hammer) | ✅ **0/8** | 🔻 **1/8 -- `hammer`** |
| 20 deliberately POLYSEMOUS words | 7/20 | 🔻 11/20 |
| **base rate, 400 random WordNet nouns** | **1.2%** | 1.2% |

**TOP-1 IS THE RIGHT FORM AND THE COMPARISON SHOWS WHY.** *At top-3 the rule flags `hammer` -- which is
a bone in the middle ear -- and `trunk`, `temple`, `calf`, `iris`. **Widening the sense window buys no
extra coverage (3/3 and 8/8 either way) and costs precision.***

⚠️ *The 7 polysemous words top-1 still flags (`palm, nail, organ, joint, spine, tongue, chest`) are
cases where **WordNet's dominant sense genuinely IS the body part** -- not obviously errors, but
context would decide and this rule has none.*

## 4. ⚠️ LIMITS -- **AND THE FIRST ONE IS THE REASON THIS IS A CANDIDATE, NOT A RESULT**

1. 🔻 **I HAVE NOT SHOWN THIS RAISES `Bgap` FROM `0.500`.** *That needs the cell re-run, and every run
   mode REPLAYS stored checkpoints (`elapsed 0.0s`). **So this is a validated DISCRIMINATOR, not a
   demonstrated improvement.***
2. **A GLOBAL LOOKUP IS STILL A HEURISTIC.** *The cell's context key is patient animacy IN A SENTENCE;
   sense should be resolved by context. This is the same KIND of shortcut as the whitelist it
   replaces -- only principled and complete rather than six words.*
3. **Controls are 8 words and tricky cases 20.** *Enough to reject top-3, not a precision certificate.*
4. **English/WordNet only.**

## TLDR

One category of words was scoring at chance, and last turn I described that as the architecture
failing on realistic vocabulary. **Reading the experiment properly, it is not.** The authors knew a
dictionary lookup misses body parts, patched six of them by hand, and **deliberately left the test
words unpatched so the hole could be measured honestly.** That is good practice and I misread it as a
weakness.

**There is a clean fix.** The same dictionary that fails to say "an ankle belongs to a living thing"
does say "an ankle is a joint, which is a body part" — the information is there, just on a different
shelf. Using that instead catches **all three of the deliberately-uncovered words and every obvious
body part, while flagging none of the eight control words**, and fires on about one noun in eighty
overall.

**Checking the obvious way to make it more thorough showed the opposite.** Letting it consider a word's
second and third meanings gains nothing and starts calling *hammer* a body part — which, in fairness,
is a bone in the ear.

**What I have not done is show that this actually improves the score**, because re-running the
experiment replays its saved workings instead of redoing the work. So this is a fix worth making with a
tested detector behind it, not a demonstrated gain — and I would rather say so than round it up.

## QUESTIONS

None.

## NEXT STEPS

1. **The fix needs a real run to count**, which needs the fresh-units capability already filed.
2. **The genuine open-vocabulary cost is `B 1.000 -> 0.833` and `Bgen 1.000 -> 0.750`** *-- unrelated to
   body parts, and that is the real frontier.*
3. *Method note: **checking the wider rule was what rejected it.** Top-3 looked strictly more thorough
   and was strictly worse.*
