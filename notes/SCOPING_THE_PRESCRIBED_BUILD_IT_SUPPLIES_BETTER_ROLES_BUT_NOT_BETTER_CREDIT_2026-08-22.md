# **SCOPING "REPLACE THE LOCAL WINDOW": IT WOULD SUPPLY GENUINELY BETTER *ROLES*, BUT ITS CAUSAL COMPONENT IS REDUCIBLE TO CONNECTIVE-ELSE-MOST-RECENT BY ITS OWN VET -- SO IT DOES *NOT* SOLVE CREDIT ASSIGNMENT.**

**Read-only scoping of the producer against the consumer, before building anything.**

---

## 1. WHAT THE CONSUMER ACTUALLY DOES

*`hdlab/consequence_learning_loop._credit_targets(window_text, desired_referent)`:*

- takes a **flat string** -- the goal sentence plus up to 3 following
- finds verb-like tokens, bounds each to its **local clause** by coordinator/subordinator
- extracts the **pre-verb subject NP-head** and **post-verb object NP-head** -- ***POSITIONALLY***
- links either to the goal referent via `_referent_links` -- ***STRING MATCHING***
- credits **every** linked verb with the **whole window's** consequence

## 2. ✅ WHAT THE PRODUCER ALREADY EMITS -- **THE ROLE HALF IS A REAL UPGRADE**

| `_credit_targets` derives | `SituationModel` already carries |
|---|---|
| pre-verb subject NP-head *(positional)* | **`agent`, `subj_role`** -- *frame-based; fear/cherish -> EXPERIENCER, kick -> AGENT, verified running* |
| post-verb object NP-head *(positional)* | **`patient`, `obj_role`** |
| -- | **`affect`** -- *already computed (battered -> HARM)* |
| string `_referent_links` | **`CorefResolution`** *(pronoun -> cluster, with `sent_dist`)* |

> ### **ON ROLES THIS IS A GENUINE UPGRADE: FRAME-BASED ASSIGNMENT REPLACING POSITIONAL GUESSING, WHICH IS EXACTLY WHAT THE CHARTER'S "role assignment is FRAME-based not positional" ANCHOR ASKS FOR.**

## 3. 🔻 **BUT THE CAUSAL HALF DOES NOT SOLVE THE PROBLEM -- ITS OWN CAVEAT SAYS SO**

*I was about to report `CausalLink(cause, outcome, method)` as "the situation model already does credit
assignment". **Its own source, line 46-47:***

> *"HONEST CAVEAT (carried from the 29515 VET): this mechanism is **REDUCIBLE to
> connective-else-most-recent**"*

***SO WIRING IT IN WOULD IMPORT A RECENCY HEURISTIC, NOT A SOLUTION.*** **"Use the discourse connective
if there is one, otherwise take the most recent candidate" is not attaching a consequence to the right
verb -- it is the same class of shortcut the whole credit-assignment problem is about.**

⚠️ **I CAUGHT THIS ONLY BECAUSE I OPENED THE FIELD'S DEFINITION.** *The dataclass line reads
`method: str  # connective | bridge | fallback (see 29515 caveat)` -- **the caveat is a comment on a
struct field**, and the headline capability name gives no hint.*

## 4. 🔻 **AND IT IS NOT A WIRING JOB: THE INPUT CONTRACTS DO NOT MEET**

| | |
|---|---|
| **producer** | `SituationReader.read(conll_path)` -- *requires a **CoNLL file with LitBank-style MENTION ANNOTATIONS** (`parse_litbank_conll`), and raises `SENTENCE_MISALIGN` if the two parses disagree* |
| **consumer** | `_credit_targets(window_text, ...)` -- *raw prose strings off the corpus* |

***BRIDGING THEM REQUIRES PRODUCING MENTION-ANNOTATED PARSES FOR ARBITRARY PROSE.*** **That is the real
integration cost, and it is not small -- it is a parse plus mention detection on the reading path.**

## 5. 🎯 THE HONEST SCOPING VERDICT

| what the prescribed build would buy | |
|---|---|
| frame-based roles replacing positional guessing | ✅ **real, and the charter's own anchor** |
| entity identity across sentences replacing string matching | ✅ **real** |
| per-event affect already computed | ✅ **real** |
| **attaching the consequence to the RIGHT verb** | 🔻 **NO -- the causal component is connective-else-most-recent** |
| cost | 🔻 **mention-annotated parsing for arbitrary prose** |

> # **IT FIXES THE HALF THAT WAS NOT THE STATED BOTTLENECK, AND LEAVES THE STATED BOTTLENECK TO A RECENCY HEURISTIC.**

*That does not make it worthless -- better roles may raise attribution precision from its measured
`0.4676`. **But it should not be sold as solving credit assignment, and I nearly did.***

## 6. ⚠️ LIMITS

1. **Read-only scoping.** *Nothing was built or measured; this is contracts and caveats, not behaviour.*
2. **I did not measure how much of the `0.4676` attribution precision is ROLE error vs CREDIT error.**
   *That is the number that would decide whether the role upgrade alone is worth it, and it is unrun.*
3. **The `29515` caveat is quoted from the source comment**, *not from re-reading that VET.*
4. **`CorefResolution` quality is not assessed** *-- the landed centering cells read MIDDLE_BAND.*

## TLDR

Before building the thing both design documents ask for, I read what it would actually plug into.

**Half of it is a real improvement.** The current code guesses who did what by *word position* — whatever
noun sits before the verb is the subject. The situation reader works it out from the verb's grammatical
frame instead, which is what the charter says the brain does and what our own anchor demands. It also
tracks people across sentences properly and already works out whether an event was harmful.

**The other half does not do what I was about to claim.** The component that links a cause to its
outcome carries a note in its own source saying it reduces to "use the joining word if there is one,
otherwise pick the most recent thing". **That is a shortcut, not an answer** — and attaching consequences
to the right verb is precisely the problem we are trying to solve. I nearly reported it as the solution;
I caught it only because I opened the definition of one field.

**And it is not a plug-in job.** The situation reader needs text that has already been parsed and marked
up with who the people are; the learning loop hands it plain sentences. Bridging that is real work on
the reading path.

**So: worth doing for the roles, not sufficient for the credit.** The number that would settle whether
it is worth doing on its own — how much of the current error is bad roles versus bad credit — has never
been measured.

## QUESTIONS

None.

## NEXT STEPS

1. ⭐ **MEASURE THE SPLIT FIRST: of the attribution errors at precision `0.4676`, how many are WRONG ROLE
   versus WRONG VERB?** *That is cheap, it is unrun, and it decides whether the role upgrade alone is
   worth the parsing cost.*
2. **Do not sell the situation-model wiring as solving credit assignment.** *Its causal component is a
   recency heuristic by its own VET.*
3. *Method note: **the caveat that mattered was a comment on a dataclass field**, not in any headline,
   verdict or docstring summary. I found it by opening the definition of the thing I was about to
   recommend.*
