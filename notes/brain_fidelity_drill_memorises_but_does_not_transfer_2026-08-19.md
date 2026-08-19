# BRAIN-FIDELITY DRILL: the substrate memorises perfectly and transfers nothing

**Owed under standing discipline 17 (owner, 2026-08-18): every negative gets a brain-fidelity
drill, every time -- which brain structure performs this operation, are we REPLICATING it or
SUBSTITUTING something convenient, and what would close the gap?**

**PROVENANCE OF THIS DOCUMENT, STATED FIRST SO NOTHING IN IT IS OVER-TRUSTED.** This is
REASONING FROM KNOWLEDGE plus ON-DISK ENUMERATION. **No web search was run and no literature scan
was performed**, so every biological claim below is marked either PINNED-AS-RECALLED (textbook
level, but not freshly re-verified this session) or NEEDS-A-LIT-CHECK. *A note is a measurement
with a timestamp; this one's timestamp covers the DISK facts, not the biology.* The standing
safety clause also applies to whoever does run the scan: **generic published terminology only, and
never our architecture, organs, operators, dimensionalities or results.**

---

## 1. THE NEGATIVE, AND THE FIRST QUESTION IS WHETHER IT COULD HAVE SUCCEEDED

`data/exp_substrate_end_to_end_readout_v1/metrics.json`, 3 seeds, n=300, pool 2,114:

| | exact key | held-out |
|---|---|---|
| episodic route | **0.9333** | **0.0044** |
| co-occurrence floor | 0.1700 | **0.0233** (credible bar 0.0367) |
| unrelated-sentence cue | 0.0011 (p=0.0005) | 0.0033 (**p up to 1.00**) |

**COULD IT HAVE SUCCEEDED? YES, AND THAT IS ESTABLISHED RATHER THAN ASSUMED** -- discipline 17's
first clause, added because four of one night's "negatives" turned out to be measurement defects.
The exact-key arm reaches 0.9333 and its scramble twin separates at p=0.0005, so **the store, the
encoder and the scorer all demonstrably work**. The task is not impossible either: a plain counter
reaches **50x chance** on it. **So the held-out collapse is a real result.**

---

## 2. WHICH BRAIN STRUCTURE -- AND THE ANSWER REFRAMES THE NEGATIVE AS AN EXPECTED ONE

**PINNED-AS-RECALLED: the hippocampus is NOT SUPPOSED TO GENERALISE.** Its dentate gyrus performs
PATTERN SEPARATION -- it makes similar inputs MORE distinct, deliberately, so that two similar
episodes do not overwrite each other. An episodic store that recalls its own episodes almost
perfectly and transfers nothing to a new context **is behaving exactly like the structure we
copied.** *Our 0.9333 / 0.0044 split is not a malfunction of D3. It is D3 working.*

**PINNED-AS-RECALLED: generalisation is the NEOCORTEX's job, and the two systems are
complementary by design** -- fast, sparse, episode-specific on one side; slow, overlapping,
statistical on the other. The standard argument for why there are two is that a single system
doing both suffers catastrophic interference.

**PINNED-AS-RECALLED: the TRANSFER MECHANISM BETWEEN THEM IS REPLAY** -- stored episodes are
re-activated offline and used to train the slow system, so structure common across many episodes
accumulates in cortex while the episode-specific detail stays hippocampal.

**NEEDS-A-LIT-CHECK before anything is built on it:** the precise replay SELECTION rule (what gets
replayed, in what order, how prioritised) and the ratio of replay to new experience. *ORGAN_MAP
already records D4's selection function as UNPINNED, which is consistent.*

---

## 3. THE GAP, AND IT IS EMBARRASSINGLY CONCRETE: WE BUILT THE FAST STORE AND NEVER RAN THE TRANSFER

**ENUMERATED ON DISK, NOT SEARCHED FOR BY GUESS.** `hdlab/hippocampal_encoder.py` already
contains **`cls_replay_cycle`** ("replay stored CA3 attractors as inputs to a cortical W") and
**`cls_discrete_budget_consolidate`** ("one discrete-budget offline CLS consolidation phase").
A grep across `hdlab/ tools/ experiments/ verification/ notes/` returns them in **exactly two
files: their own module, and one verification witness.**

> **NO EXPERIMENT CALLS THEM. NOTHING ON ANY LIVE PATH CALLS THEM. THE ASSEMBLED SUBSTRATE I BUILT
> TODAY WRITES 3,400 EPISODES AND NEVER CONSOLIDATES ONE.**

**So the honest statement of the Phase 2 negative is not "the substrate does not generalise". It
is: WE MEASURED A HIPPOCAMPUS AND REPORTED THAT IT IS NOT A NEOCORTEX.** *We are REPLICATING the
fast store and SUBSTITUTING nothing at all for the slow one -- the transfer step is simply absent,
and the organ for it has been sitting built and unused.*

---

## 4. WHAT WOULD CLOSE THE GAP -- PRE-REGISTERED, WITH A WAY TO FAIL

**⚠️ MY LAST BRAIN-FIDELITY PREDICTION IN THIS EXACT AREA WAS REFUTED INSIDE ONE RUN, AND THAT IS
WHY THIS ONE IS WRITTEN DOWN BEFORE THE BUILD.** I predicted the accumulated-context "semantic"
route would generalise better than the episodic one because pattern separation is the enemy of
generalisation. **It was 5x WORSE (0.005 vs 0.025).** *What that refutes is a claim about THAT
accumulator. It does not test replay, because that accumulator is never fed by replay -- it is a
parallel sum, not a consolidated store. A NEW prediction is therefore legitimate, and it needs its
own way to be wrong.*

### 🛑 CORRECTION TO THIS SECTION, MADE BEFORE THE BUILD AND NOT AFTER IT

**THE BUILD AS FIRST WRITTEN -- "run `cls_replay_cycle` over the stored episodes and score it" --
WOULD HAVE BEEN AN EXPERIMENT THAT COULD NOT SUCCEED, AND I WOULD HAVE FILED ITS NULL AS
READING (C).** Read at HEAD before writing any cell:

- **`cls_replay_cycle` builds `cortex_W` of shape `[dg_dim, dg_dim]` and trains it Hebbian on
  `outer(code, settle(code))` -- an AUTOASSOCIATOR OVER THE SAME SPARSE, PATTERN-SEPARATED DG
  CODES.** Its own docstring says so plainly: *"This is a minimal composition point; the FULL
  cortex is Spoke1+2 and would receive PROJECTED codes rather than raw DG. Kept minimal to
  selftest replay semantics -- production consolidation is a v2 concern."*
- **Replaying pattern-separated codes into a matrix over the SAME space cannot produce
  generalisation. It re-learns the separation.** A new sentence about a known word gets a
  different context vector, hence a different top-K DG code, hence little overlap with anything
  stored -- which is precisely the 0.0044 we already measured. **A null there would have been a
  property of MY CHOICE OF TARGET REPRESENTATION, not of replay.**

***SO THE ORGAN WE HAVE IS NOT THE ORGAN THIS DRILL CALLS FOR.*** The whole point of the slow
system is that its codes are DENSE AND OVERLAPPING, so structure shared across episodes
superimposes while episode-specific detail cancels. **We have the replay MACHINERY and no
cortical TARGET REPRESENTATION to replay into.** *`cls_discrete_budget_consolidate` is the
certified sibling and is closer -- but it requires a `concept_codebook` of clean concept
attractors, i.e. it presumes you already have the concepts it would be used to form.*

**THE BUILD, CORRECTED:** replay the stored episodes into a **DENSE, OVERLAPPING** target -- the
un-separated context vectors, not their DG codes -- and score the SAME held-out items on the SAME
scorer, pool and gold. **The DG-space arm is kept as a control, not as the treatment**, because it
is the arm that CANNOT WORK and saying so in advance is the difference between a control and an
alibi.
**⚠️ AND NOTE WHAT THAT MAKES THE TREATMENT: an accumulated dense per-word profile. THAT IS VERY
CLOSE TO THE `SEMANTIC` ROUTE THAT ALREADY READ 0.005.** *If the corrected build is only "the
semantic route again, fed by replay", it must be pre-declared as a REPLICATION of a measured null
and not dressed as a new mechanism. The one genuine difference is the SELECTION and REPEAT
structure replay imposes on what gets accumulated -- so THAT, and not the accumulation, is the
variable under test, and a RATE-MATCHED RANDOM-REPLAY twin is what isolates it.*

**PRE-COMMITTED READINGS, before any number exists:**
- **(A)** consolidated route beats the 1-step co-occurrence floor's UPPER bound, CI-separated ->
  **the missing step was consolidation**, and it was built and unwired the whole time.
- **(B)** consolidated route beats the raw episodic route but NOT the floor -> replay helps and is
  **still not the answer**; report the margin and do not headline it.
- **(C)** consolidated route ties the episodic route -> **replay over OUR episode codes carries no
  transferable structure**, which closes a brain-pinned route with a measurement.
- **(D)** it beats the floor ONLY with replay counts far beyond what a night's sleep could
  plausibly supply -> report the required ratio explicitly; **that is an ADMISSION THE MACHINERY
  IS WRONG**, in the same shape as the corpus-scaling criterion.

**MANDATORY CONTROLS, none optional:** a **RATE-MATCHED random-replay twin** (replay the same
NUMBER of episodes, chosen at random, so a gain cannot be credited to "more training"); the
existing scramble twin; all floors recomputed on the consolidated representation, **never imported
across representations**; and CI plus null beside every margin.

**AND THE STANDING WARNING THAT APPLIES DIRECTLY HERE:** when a baseline sits far below chance,
destroying or diluting information moves the score TOWARD chance and reads as progress. Held-out
episodic sits at 0.0044 against a 0.0233 floor. **Any consolidated number between them must be
checked against a rank-matched null before it is called an improvement.**
