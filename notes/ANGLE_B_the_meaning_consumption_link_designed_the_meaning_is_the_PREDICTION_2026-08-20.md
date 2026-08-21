# ANGLE B -- THE MEANING-CONSUMPTION LINK, DESIGNED: **THE BANKED MEANING SUPPLIES THE *PREDICTION*, THE CONTEXT SUPPLIES THE *OBSERVATION*, AND THE DIFFERENCE IS THE ERROR**

> # 🚫 ITS **FILTER** IS REFUTED (2026-08-21). **THE ARCHITECTURE BELOW STANDS; SECTION 1 DOES NOT.**
> Section 1 says *"BIND ONLY THE DEFINITIONAL HALF"* and calls the filter settled -- *"one field that
> already exists on every provenance row, no new machinery."* **Measured twice and wrong twice:**
> **(a) COVERAGE** -- definitions exist for only **24.6%** of encountered words, so the filter leaves
> ~75% of words with no prediction, and no prediction means no error signal.
> **(b) QUALITY ON A TASK** -- on the 48 items where both routes fire, scored alone with no mixing:
> **definitional `-0.021`/item, CI `[-0.062, +0.000]` -- NO SIGNAL AT ALL**; distributional on the
> SAME items **`+0.188`, CI `[+0.042, +0.333]`**; paired **`-0.208`, CI `[-0.375, -0.042]`, SEPARATED.**
> **➡️ The 32%-vs-4% hand-score that justifies section 1 is a RUBRIC number. It is real, and it
> pointed the WRONG WAY for this consumer.** *A statistic the mechanism optimises may DIAGNOSE,
> never DECIDE.*
> **SECTIONS 3-5 ARE UNAFFECTED** -- the meaning supplying the PREDICTION, the error being the gap
> against observed context, and the wiring checks. That is the PINNED half of F5.
> *Not "the definitions are bad": a correct definition need not share vocabulary with an arbitrary
> sentence. They may suit a LOOKUP; they do not suit a prediction-error monitor.*
> `notes/THE_DEFINITIONS_CARRY_NO_ANOMALY_SIGNAL_...md`


**The bottleneck all four routes identified is that nothing consumes the banked meanings.** F5 gives
the SITUATION REGISTER a use; **it does not automatically give the `GROUNDED_MEANING` facts one.**
This is the design that closes that gap, and its three questions are WHICH meanings, WHICH role, and
WHEN.

---

## 1. **WHICH MEANINGS: THE DEFINITIONAL HALF ONLY. TONIGHT'S NUMBERS DECIDE THIS.**

`consolidated()` mixes two populations, measured tonight on the same rubric by the same scorer:

| source | share | MEANINGFUL |
|---|---|---|
| **`meaning_source = DEFINITIONAL_EXTRACTION`** (phrases) | 212 of 402 | **32%** |
| distributional `canonicalize` (single words) | 190 of 402 | **4%** |

**➡️ BIND ONLY THE DEFINITIONAL HALF.** Feeding the 4% population into a prediction injects
`artwork -> himself` and `mice -> experiment` as *expectations*, and **a prediction built from noise
generates error everywhere, which is indistinguishable from a broken detector.** *The filter is one
field that already exists on every provenance row -- no new machinery, no classifier.*

**AND IT IS FALSIFIABLE RATHER THAN A PREFERENCE:** if binding the distributional half too makes no
difference to the error signal, the meanings were never entering the prediction and the wiring is
wrong. **That is a positive control on the link itself.**

## 2. **WHICH ROLE: A DEDICATED `MEANING` ROLE, NOT AN EVENT SLOT**

`bind_filler(entity, role, content_vec)` binds a role vector to an **arbitrary** content vector and
is already live carrying open-vocabulary word vectors in `goal_outcome_relation_grounded.py`.
**A dedicated role keeps meaning out of the event-index vocabulary**, so `decode_filler(entity,
"MEANING")` recovers it without competing against event slots.
*Capacity is not a constraint: `multibank_8` (the DEFAULT) holds decode self-consistency >=0.999 at
256 events/entity, where the flat register degrades to 0.6547.*

## 3. ⚡ **WHEN -- AND THIS IS THE ARCHITECTURALLY LOAD-BEARING ANSWER**

**NOT "bind it once at first encounter and leave it in the register."** That would make the meaning
a stored decoration -- present, still unconsumed, still unselectable. **It is the bottleneck in a new
location.**

**THE MEANING MUST SUPPLY THE PREDICTION.** When word `w` arrives:

| | |
|---|---|
| **PREDICTED** contribution to the situation state | derived from **`w`'s banked meaning** |
| **OBSERVED** contribution | derived from **the sentence context** |
| **ERROR** | `‖predicted - observed‖`, precision-weighted -- **this IS `‖Δ situation_model‖`** |

**➡️ THAT IS ORDINARY PREDICTIVE CODING, AND IT IS WHY IT CLOSES THE LOOP: a WRONG banked meaning
produces a LARGE, PERSISTENT error, which is exactly the selection pressure the philosophy says
referential grounding requires and which this substrate has never had.** *Nothing else in the design
does that. Storing the meaning where the monitor can see it is not the same as making the monitor
depend on it.*

## 4. 🎯 **A CONSEQUENCE WORTH MORE THAN THE MECHANISM: THE ERROR SIGNAL IS A FREE QUALITY ESTIMATE**

If a wrong meaning produces persistent error, then **accumulated error per term is a self-generated
estimate of how good that term's banked meaning is** -- computed with no gold, no ConceptNet, no
hand-scoring.

**AND IT IS IMMEDIATELY TESTABLE AGAINST WORK ALREADY DONE.** Tonight produced hand-scores on
several hundred facts (MEANINGFUL / RELATED / NOISE). **If accumulated error ranks those facts in
the same order, the substrate can grade its own output** -- and this project's single most expensive
bottleneck all night was that only a human could tell a good fact from a bad one.

*Stated as a PREDICTION of the design, not a claim: it is exactly the sort of appealing corollary
that tonight repeatedly punished. **It is listed here because it is CHEAP TO FALSIFY** -- the
hand-scores already exist.*

## 5. WHAT WOULD SHOW THE LINK IS WIRED AT ALL (before any quality claim)

1. **ABLATE IT.** Remove the meaning from the prediction; the error distribution **must** change. *If
   it does not, the meanings are decorative -- which is precisely the state we are trying to leave,
   and the ablation is the only thing that would reveal it.*
2. **CORRUPT IT.** Bind a *wrong* term's meaning; error **must** rise. *The `SHUFFLE` control that
   has separated every real result tonight from every artifact.*
3. **REPORT THE FIRING RATE AND THE ERROR DISTRIBUTION** before reading any verdict -- G2's gate
   fired **zero** times and looked like a null.

## TLDR

The recurring problem is that this system writes down what words mean and then never uses those
notes. Building a "notice when a sentence doesn't fit" component does not automatically fix that —
it would give the system a use for its *picture of the passage*, while the *word meanings* sit in a
drawer as before.

So here is how they get used. **Three decisions.**

**Which meanings:** only the good half. The system produces meanings two ways, and tonight measured
one at roughly eight times the quality of the other. Feeding it the bad half would fill its
expectations with nonsense, and a system expecting nonsense is surprised by everything.

**Where they go:** a dedicated slot, using a mechanism that already exists and already carries this
kind of content.

**And the one that actually matters — when.** Not "file the meaning away where the detector can see
it": that is the same drawer in a new cupboard. **The meaning has to be what the system EXPECTS.**
When a word arrives, what it thinks the word means generates a prediction; the sentence supplies the
reality; the gap between them is the surprise. **That way a wrong meaning is actively costly** — it
makes the system wrong about something — which is the entire missing ingredient.

**And one genuinely interesting side effect:** if wrong meanings cause persistent surprise, then
tracking surprise per word gives the system a way to grade its own definitions, with no human and no
dictionary. That is a guess, not a finding — but it is cheap to check, because tonight produced
hundreds of hand-graded examples to check it against.

## QUESTIONS

None.

## NEXT STEPS

1. **NEW ANGLE A:** build the frequency-matched anomaly set the F5 evaluation needs. It is
   constructible inline from existing corpora and is the concrete prerequisite for the build.
2. Both angles stay occupied, per the owner's standing rule.
