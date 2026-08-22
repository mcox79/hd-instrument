# **I ASKED THE OWNER TO APPROVE BUILDING SOMETHING WE ALREADY HAVE. THE CREDIT MECHANISM IS ALREADY ROLE-BASED -- ITS REAL HOLE IS A SUFFIX TEST THAT NEVER SEES `39.7%` OF VERBS.**

**Q104 WITHDRAWN BY ME BEFORE THE OWNER SPENT TIME ON IT.** *Second question this month withdrawn for
a premise I could have checked at the source in five minutes. The tell is identical both times: I
described a mechanism from its SEARCH SCOPE instead of from its DECISION RULE.*

---

## 1. 🔻 WHAT I TOLD THE OWNER, AND WHAT THE CODE DOES

> *Q104: "Right now it decides that by looking at a window of a few nearby sentences."*

**`hdlab/consequence_learning_loop._credit_targets` does this instead:** bounds each verb's OWN CLAUSE,
extracts the **pre-verb SUBJECT NP-head** and the **post-verb OBJECT NP-head**, and credits the verb
**only if one of them LINKS to the goal referent.** Its docstring is explicit that bystanders are
excluded *"STRUCTURALLY... never by a stopword list"*.

✅ **CONFIRMED BY RUNNING IT, NOT BY READING IT:**

| window | referent | credited |
|---|---|---|
| *"the girl stumbled badly and the man laughed loudly"* | **girl** | **`['stumble']`** |
| *"the girl stumbled badly and the man laughed loudly"* | **man** | **`['laugh']`** |

> ### **PROXIMITY WOULD HAVE CREDITED BOTH TO WHICHEVER WAS NEARER. IT DOES NOT. THAT IS WHO-DID-WHAT-TO-WHOM -- THE THING I WAS ASKING PERMISSION TO BUILD.**

*And the clause-anchoring alternative was ALSO already tried: `exp_sharpened_credit_assignment_v1`,
`HARD_FAIL`, 2026-08-07. It sharpens to the resolving clause; it never touches roles either.*

## 2. 🎯 SO THE EXPOSURE IS **UPSTREAM** OF THE ROLE LOGIC -- AND IT IS PURELY MORPHOLOGICAL

A verb only reaches the role logic if `_is_verblike` accepts it, and that gate is one line:

```python
lemma_verb(tok) != tok or tok.endswith(("ed", "ing"))
```

**The second probe sentence hit its failure by accident:** *"the man shouted and then the girl wept
quietly"*, referent **girl**, returns **`[]`** -- `wept` is an irregular with no `-ed`/`-ing`, so it is
**invisible**. ***The function's own docstring names `wept` as a known miss.*** **A verb the gate never
sees cannot be credited by ANY downstream rule, however good.**

## 3. ✅ MEASURED AGAINST AN **INDEPENDENT** DETECTOR (3,000 real sentences, 62,065 tokens)

*Independent matters: scoring a morphological heuristic with another morphological heuristic shares
its blind spot. The comparator is the **UD-EWT POS tagger already loaded on the live path**.*

| | |
|---|---|
| **RECALL -- real verbs the gate SEES** | 🔻 **`0.6026`** (5,349 / 8,877) |
| **MISSED -- real verbs it NEVER sees** | 🔻 **`0.3974`** (**3,528**) |
| PRECISION -- accepted things that are verbs | `0.4718` |
| **precision EXCLUDING the AUX tagset convention** | **`0.5816`** |

**THE BIGGEST CONTAMINANT IS NOT A CONVENTION ARTIFACT: `NOUN` 3,092**, ahead of `AUX` 2,140.
*I broke this out rather than quoting the raw 0.4718, because UD calls `was`/`is` AUX and blaming the
gate for that would be blaming it for a tagset.*

> ## 🔑 **AND THE MISSED VERBS ARE THE EXACT WORDS Q104 CALLS THE PROBLEM:** *`see, have, know, get, go, do, come, think, put, make, let, try, say, take, look, give`.* **I HAD THE POPULATION RIGHT AND THE DIRECTION BACKWARDS -- these are BASE FORMS, so they are not being wrongly PICKED, they are never being SEEN.**

## 4. ➡️ WHAT THIS MAKES THE ACTUAL NEXT MOVE

**A trained UD POS tagger is on disk (`data/frontend_assets/`), is loaded by the reading loop already
(`StructuralEncoder`), and the credit path uses a hand-written suffix test instead.** That is the
"REUSE, don't build a parallel organ" case in its purest form -- **a wiring, not a build**, and well
inside standing authority. *Which is also why no replacement board question was filed: asking before
measuring is what produced the wrong premise the first time.*

## 5. ⚠️ WHAT I AM **NOT** CLAIMING

1. 🚫 **THAT FIXING THE GATE MOVES THE WALL. UNTESTED.** *The directly relevant precedent says it may
   not: the `lemma_verb` repair took gold verb-inflection `53.50% -> 99.03%` and the wall reproduced
   to FOUR DECIMAL PLACES (`0.4722` twice, fifteen days apart). **That repair changed labels, not
   decisions.** This one changes WHICH TOKENS ARE CANDIDATES, which is a different intervention -- but
   "different" is a reason to test it, not a reason to expect it to work.*
2. **One tagger, one tagset, 3,000 sentences, one corpus shelf.** The tagger is itself imperfect and
   is a comparator, not truth.
3. **`0.4718` vs `0.5816` -- quote the second, or quote the first WITH the AUX share.**

## TLDR

I asked the owner to approve building a way for the system to work out **who did what to whom**, so it
could tell which action a story's consequence belongs to. **We already have that. I misread our own
code** — I described the area it searches instead of the rule it uses to choose. Running it settles it:
given *"the girl stumbled and the man laughed"*, it correctly gives the girl the stumbling and the man
the laughing. Nearness alone could not do that.

**The actual weak spot is one step earlier, and it is cruder than I realised.** Before any of that
reasoning happens, the system decides "is this word an action at all?" using a spelling rule — roughly,
does it end in *-ed* or *-ing*. **Measured against a proper grammar tool: it misses about four in every
ten real actions**, and about four in ten of the things it does accept are not actions but ordinary
nouns.

**The words it misses are exactly the ones I had already flagged as the problem** — *see, have, know,
get, go, come, give*. I had the right list and the wrong story: they aren't being wrongly chosen, **they
are never even considered.**

**And the proper grammar tool is already built, already trained, already loaded by the reading system —
just not connected to this part.** So the next step is connecting something we own, not building
something new. **What I can't yet say is whether it will help.** A very similar repair earlier this
month improved the underlying word tool from about half right to almost fully right and the final score
did not move at all. So this gets tested, not assumed.

## QUESTIONS

None. **Q104 is withdrawn rather than re-asked** — I will measure first this time.

## NEXT STEPS

1. **Swap the suffix test for the already-loaded tagger, and re-run the wall cell** *(it has no
   `units.jsonl`, so it genuinely recomputes -- verified 08-22, 65.55 s).* **Same corpus, same eval
   bank, same gold, one variable.**
2. **Pre-declare the kill condition:** if primary accuracy stays at `0.4722 +/- noise` with recall
   fixed, then candidate SELECTION is not what limits this line, and that is a real finding that
   retires the whole credit-assignment thread rather than a disappointment.
3. *Method note: **two withdrawn questions, one cause -- describing a mechanism by where it LOOKS
   rather than by how it DECIDES.** Both were five minutes from the source.*
