# **THE ENCODING GAP HAS A NAME: ONE REPRESENTATION IS BEING ASKED TO DO TWO JOBS THAT REQUIRE OPPOSITE THINGS. GROUNDING NEEDS THE WORD REMOVED; IDENTIFICATION NEEDS IT PRESENT. THE BRAIN HAS TWO SYSTEMS; WE HAVE ONE.**

**Three separate lines tonight dead-ended on the same measurement: two encounters with the same word
barely resemble each other. This finds the cause, and it is architectural rather than a defect.**

---

## 1. THE MEASUREMENT

*60 lemmas x 41 real sentences, same code path both arms (`context_vector_masked`, with a
never-matching target for the unmasked arm so nothing is removed). Chance = 0.0167.*

| | within-lemma | cross-lemma | margin | **hit@1** |
|---|---|---|---|---|
| **MASKED -- what the live path stores** | 0.0182 | 0.0079 | +0.0104 | **0.1417** |
| **UNMASKED -- word included** | 0.0705 | 0.0089 | **+0.0616** | **0.4750** |
| ratio | **3.9x** | 1.1x | **5.9x** | **3.4x** |

**`context_vector_masked` removes every token whose lemma matches the target -- its docstring calls
it "the no-leak fix" -- and `ConceptSpace.observe` accumulates exactly that.** ***So a word's stored
representation contains no trace of the word itself.***

## 2. ⚠️ **THIS IS NOT AN ARGUMENT TO UNMASK. SAYING SO PLAINLY.**

***0.4750 is inflated by self-reference: the word's own vector is identical across all its
encounters, so including it makes identification partly circular.*** **And the mask exists for a
sound reason -- without it, grounding learns that "artery" means "artery". The no-leak fix is
correct for the job it was built for.**

## 3. 🎯 **THE ACTUAL FINDING: TWO JOBS, OPPOSITE REQUIREMENTS, ONE REPRESENTATION**

| job | what it needs |
|---|---|
| **GROUNDING** -- learn what a word MEANS from its contexts | **the word REMOVED**, or the answer is written into the question |
| **IDENTIFICATION / EPISODIC** -- recognise that two encounters are of the SAME word | **the word PRESENT** -- it is by far the strongest cue |

> ### **THE SAME ACCUMULATED CONTEXT VECTOR IS BEING ASKED TO DO BOTH. THE FIRST REQUIREMENT DESTROYS THE SECOND, BY CONSTRUCTION.**

**🧠 THE BRAIN DOES NOT FACE THIS CONFLICT BECAUSE IT DOES NOT USE ONE REPRESENTATION.** *Word
identification runs through the visual word form area to a lexical entry; semantic grounding is the
ATL hub with its modality spokes. **The brain identifies the word FIRST and then binds meaning to an
already-identified item.*** **We collapse identification and grounding into a single vector and then
remove the identity half to protect the grounding half.**

## 4. 🔗 **AND IT EXPLAINS TONIGHT'S OTHER THREE DEAD ENDS**

| dead end | now explained |
|---|---|
| **CA3 cannot complete** -- same-word codes at 0.0056, 40x below the useful regime | the cue that would make them resemble each other **is masked out before storage** |
| **surprise is uninformative about value** (r = +0.24, spans zero) | a representation without word identity cannot register "same thing again", so novelty-of-form is all that is left |
| **12-dim feature context is flat** -- does not improve with more traces | it also lacks word identity, and adds a coarse scene signal instead |

***One cause, three symptoms. That is worth more than any of the three separately.***

## 5. WHAT WOULD FOLLOW (NOT PROPOSED, NOT MEASURED)

*The brain-shaped move is two representations rather than one: a lexical/identity code that is
STABLE across encounters, and a context accumulation that is masked and feeds grounding.* **That is
`ORGAN_MAP`'s hub-and-spokes shape, and it is not what the live path does.** ⚠️ ***I have not
measured whether splitting them helps, and I am not claiming it would. This note names a cause;
proposing the fix is a separate step that needs its own can-fail test.***

## TLDR

Three separate investigations tonight ran into the same wall: our system barely registers that two
sentences are about the same word. **I found the cause, and it isn't a bug — it's a design decision
doing exactly what it was meant to do.**

When the system reads a sentence to learn what a word means, it **deliberately deletes that word from
the sentence first.** That's correct: otherwise it would "learn" that *artery* means *artery* —
learning nothing from a question containing its own answer.

**But that deleted word is by far the strongest clue that two sentences are about the same thing.**
Put it back and the system's ability to recognise which word a sentence concerns **more than triples**.

**So one thing is being asked to do two jobs that need opposite treatment.** Working out what a word
*means* requires hiding the word. Recognising *which word this is* requires seeing it. **Our system
uses a single representation for both, so protecting the first destroys the second.**

**The brain doesn't have this problem because it doesn't use one representation.** Recognising a
written word and understanding what it means are separate systems, and the brain identifies the word
first, then attaches meaning to something it has already identified.

**And this explains all three of tonight's dead ends at once** — why the memory-completion component
has nothing to work with, why "surprise" can't tell useful notes from useless ones, and why the
sensory-feature version never improves with practice. **All three are downstream of the same missing
piece.**

**What I'm not claiming:** that we should stop hiding the word — that would break the learning it
protects. And I haven't tested whether splitting into two representations helps. **This note
identifies a cause; proposing a fix is a separate job needing its own test.**

## QUESTIONS

None.

## NEXT STEPS

1. **The encoding gap is now named, not just measured:** *one representation, two opposite
   requirements. It is architectural, and it is upstream of three separate dead ends.*
2. **Do NOT unmask.** *The 3.4x is partly self-reference, and the mask is correct for grounding.*
3. **The brain-shaped alternative is two representations -- a stable identity code plus a masked
   context accumulation.** *UNMEASURED. Any proposal needs its own can-fail test, and this note is
   not that test.*
