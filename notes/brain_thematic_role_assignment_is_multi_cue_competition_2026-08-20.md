# HOW THE BRAIN ASSIGNS WHO-DID-WHAT-TO-WHOM: MULTI-CUE COMPETITION, NOT ONE SIGNAL

**Owner directive, board Q82, 2026-08-20:** *"you should also drill online what goes into the process
in the brain / what is hypothesized goes into it. **the brain often has many channels that it uses
and combines to result in robust outcomes**"*

**The owner's framing turned out to be the literature's central claim, not an analogy.** Recorded in
full here rather than summarised into the plan, per the standing rule that a scan's report is
persisted as its own note.

⚖️ **QUERY PRIVACY OBSERVED**: searches used generic published terminology only -- no architecture,
metric names, arm names, numbers, or corpus choices left this machine.

---

## 1. THE MECHANISM: THE COMPETITION MODEL (Bates & MacWhinney 1982; MacWhinney & Bates 1989)

Human sentence processing **integrates multiple weighted linguistic cues** to assign roles. The
cues that recur across the literature:

| cue | what it is |
|---|---|
| **word order** | position; "probabilistic cues mainly concerning linear order" |
| **noun-phrase animacy** | an animate noun is a likelier agent |
| **case marking / noun inflection** | morphological role marking |
| **subject-verb agreement** | morphosyntactic agreement |
| **semantic plausibility** | does this filler make sense in this role |

**THE CUES COMPETE.** *"Competition between cues occurs when cues point to diverging
interpretations, such as when English passive sentences subvert canonical SVO word order."* Role
assignment is the winner of that competition, updated progressively as the sentence unfolds.

### THE TWO QUANTITIES THAT MAKE IT A MECHANISM RATHER THAN A LIST

- **CUE VALIDITY = AVAILABILITY x RELIABILITY.** Availability = how often the cue is present in the
  input. Reliability = how often it is correct when present. Commonly formalised as the conditional
  probability `p(interpretation | cue)`.
- **CUE COST** -- perceivability and assignability. *"The more difficult or costly it is to process a
  cue, the less reliance listeners place upon it."*

**🔑 AND THE PART THAT MATTERS MOST FOR THIS PROJECT: CUE WEIGHTS ARE LEARNED FROM INPUT STATISTICS
AND ARE LANGUAGE-SPECIFIC.** English weights word order heavily; German and Italian weight case and
agreement more (Bates, MacWhinney et al., cue validity across English/German/Italian). **The weights
are not supplied -- they are earned from the distribution of the language being read.**

## 2. THE NEURAL DIVISION OF LABOUR

- sentence comprehension sits on a **left fronto-temporo-parietal network**
- **prefrontal** regions: local **morphosyntactic** features
- **temporal and parietal** regions: **thematic** processes, with **parietal areas crucial for
  assigning constituents to the appropriate thematic role** (converging TMS evidence)
- timing: thematic role integration around **300-500 ms**; reanalysis and **conflict resolution
  beyond 500 ms** -- i.e. competition resolution is a measurably separate, later stage
- when semantic information cannot disambiguate, **reliance shifts to grammatical cues** -- word
  order, voice, case marking. *The fallback is explicit in the developmental data.*

## 3. ⛔ WHAT THIS SAYS ABOUT OUR SYSTEM, AND IT IS SHARPER THAN "OUR ROLE ASSIGNMENT IS BROKEN"

Two landed cells found our role signal is **POSITIONAL, NOT STRUCTURAL**
(`exp_agreement_attractor_role_binding_cg_viability_v1` MIDDLE_BAND_POSITIONAL_OR_COUNT_HEURISTIC;
`exp_coherence_role_conflict_crosstalk_v1` HARD_FAIL_SIGNAL_IS_POSITIONAL_NOT_STRUCTURAL). The
numbers: overall 0.7913 against "just pick the first noun" 0.7478; **on the subject-not-first subset
0.5803, losing to majority-class 0.6269 and to a structure-SHUFFLED control 0.6214**; own flag
`structure_used=False`.

**➡️ READ THROUGH THE COMPETITION MODEL, THAT IS NOT A BUG IN OUR CUE. WORD ORDER IS A REAL CUE AND
IT IS THE HIGHEST-VALIDITY CUE IN ENGLISH. THE DEFECT IS THAT IT IS OUR *ONLY* CUE.**
**We fail precisely on the subset where the single channel is uninformative -- which is exactly the
subset the brain covers by having the OTHER channels take over.** The owner's sentence -- *"the brain
often has many channels that it uses and combines to result in robust outcomes"* -- is the diagnosis.

## 4. THE BUILD TARGET THIS NAMES, AND WHY IT FITS THIS PROJECT'S INVARIANTS

**Add the competing cues, with weights LEARNED from the corpus rather than supplied, and let them
compete.** Concretely: animacy, morphosyntactic agreement, and semantic plausibility alongside
position, each carrying a validity estimated as availability x reliability **measured on the text we
actually read**.

Three reasons this is the right shape here rather than a convenient one:
1. **It is EARNED, not supplied.** Cue validity is a statistic of the input. That satisfies the
   charter's earn-don't-supply invariant, which a hand-set weight table would violate.
2. **It has a can-fail test already built.** The subject-not-first subset plus the structure-shuffled
   control are what caught the current failure; a multi-cue version must beat majority-class AND
   shuffled-structure **on that subset**, not in aggregate where position carries it.
3. **It is a MISSING COMPONENT, not a re-tuning.** This project's own routing rule says a
   missing-PRIMITIVE gets BUILT while a used-ability-wrong gets looped. Animacy and agreement as
   *competing weighted cues* do not exist in the role path today.

## ⚠️ WHAT THIS NOTE DOES NOT ESTABLISH

- **It is a literature scan, not a measurement of our system.** The claim "we have one channel where
  the brain has several" follows from two landed cells plus this reading; it has not been tested by
  adding a second cue and observing the subset improve.
- **Cue validity across languages is pinned; the exact combination rule is not.** The Competition
  Model specifies competition and weighting; it does not hand us an equation for how activations
  combine. **That part would be OUR-INVENTION-UNDER-TEST and must be labelled so** -- the same
  discipline that applies to VSA binding, whose brain math ORGAN_MAP records as UNPINNED and
  contested three ways.
- Per this project's lit-scan calibration rule, treat any probability-of-success read off this note
  as deflated by 0.15-0.25.

## SOURCES

- [Thematic role assignment in the posterior parietal cortex: A TMS study](https://www.sciencedirect.com/science/article/abs/pii/S002839321530141X)
- [Semantic Influences on Thematic Role Assignment: Evidence from Normals and Aphasics](https://www.sciencedirect.com/science/article/abs/pii/S0093934X97919180)
- [Conflict and cognitive control during sentence comprehension](https://oa.upm.es/id/eprint/12141/contents)
- [Distinct neural correlates of morphosyntactic and thematic comprehension processes in aphasia](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11930358/)
- [Neuroanatomical Distinctions within the Semantic System during Sentence Comprehension](https://pmc.ncbi.nlm.nih.gov/articles/PMC3141816/)
- [Passive Voice Comprehension during Thematic-Role Assignment in Russian-Speaking Children](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9220815/)
- [Cue validity and sentence interpretation in English, German, and Italian](https://www.sciencedirect.com/science/article/abs/pii/S0022537184900938)
- [Sentence Processing within the Competition Model](https://journals.library.columbia.edu/index.php/SALT/article/download/1633/677/4037)
- [Extending the Competition Model](https://www.researchgate.net/publication/240732453_Extending_the_Competition_Model)
- [Revisiting the competition model: From formation to pedagogical implications](https://www.tandfonline.com/doi/full/10.1080/23311983.2023.2249631)
