# PLAN -- ORGAN-BY-ORGAN STEP LADDERS

**Written 2026-08-17 by the Director, at the owner's direction. This SUPERSEDES the forward-looking
sections of `notes/PLAN_NEXT_24H.md` (its retractions and standing rules remain in force).**

**The owner's instruction, verbatim, and it is the method for everything below:**

> "For all of these multi-step components, we need to know where the signal is, where it's getting
> lost, what's happening with the noise etc. Each is its own problem to solve, and I have yet to see
> a holistic approach to the problem with a mapping of the challenge."

> "breaking down each organ/process into all of its individual steps, then evaluating where along
> those steps we're succeeding and where we're failing, is the best way to break these down. Again,
> brain fidelity is going to help us win here - if we can truly recreate the brain process, it should
> be high performing. And we KNOW the brain works."

---

## 0. WHY THE PROGRAMME CHANGES SHAPE HERE

Until today every experiment asked **"does this change help?"** Eleven landed on 2026-08-17 and the
answer was the same every time: about +0.01, sometimes zero, once negative. That is not a finding,
it is the *absence* of one -- it means we were probing a system we had not mapped.

The first real map landed today (`exp_pipeline_stage_oracle_ladder_v1`, commit `e28d1b8d6`) and it
paid for itself in two ways.

**It found the answer.** Total loss across every processing stage is **~0.038**. The gap we must
close is **~0.079** (best rung 0.0603 against the binding floor 0.1390). **The pipeline destroys less
than half of what we are short by.** Even handed a PERFECT cue and an UNCOMPRESSED store -- every
downstream defect deleted -- the system reads 0.0603 and still fails. The ceiling is upstream of
every stage we have been optimising. In plain terms: we have been timing the relay handoffs, and the
handoffs are fine. **The first runner set off with the wrong baton.**

**It corrected the Director's own model of the machine.** The nine stages in the Director's head are
**five** in the code. "Make a context vector", "project it", and "superpose it into the store" are
not three steps -- they are one physical event. "Find the address" and "compare candidates" are one
cosine, not two. *We had been reasoning about joints the machine does not have.* That is exactly the
error the owner's method exists to prevent, and it was invisible until someone enumerated the steps
from live code instead of from memory.

**The thesis of this document: do that for EVERY organ.** One ladder per organ. Steps enumerated from
LIVE CODE, never from recollection.

---

## 1. THE LADDER METHOD -- THE STANDARD INSTRUMENT FROM NOW ON

For each organ, in this order. **An organ with no ladder does not get a build.**

1. **ENUMERATE THE STEPS FROM THE LIVE CODE.** Runtime evidence, not grep -- lazy imports inside
   function bodies are invisible to static search while string constants and comments read as
   imports. State how you enumerated. Expect the Director's step list to be WRONG; the correction is
   a result in itself.
2. **NAME THE BRAIN COUNTERPART OF EACH STEP** -- a neural system, never a cognitive-theory label.
   Mark each **PINNED BY EVIDENCE** or **OUR INVENTION UNDER TEST**. Presenting an invention as pinned
   is barred. "Unpinned" does not mean stop; it means test the best brain-motivated candidate and say
   which it is.
3. **ORACLE RUNG PER STEP.** Replace everything downstream with a perfect oracle. The accuracy is the
   information still recoverable there. **The drop between rungs is what that step destroyed.**
4. **THREE NUMBERS PER RUNG, never one:**
   - **SIGNAL** -- oracle-downstream accuracy.
   - **NOISE / SEPARATION** -- correct item versus the competing field, in units of that field's own
     spread. *A step can preserve the signal and collapse the separation; those are different
     failures needing different fixes, and reporting only accuracy hides the distinction.*
   - **RANK** -- where the correct answer sits in the full ordering, against random-ranking
     expectation on the same population.
5. **DROP TABLE, RANKED, WITH A PAIRED CI ON EACH DROP** -- not on the endpoints. The ranking is the
   deliverable.
6. **MONOTONICITY ASSERTION.** Signal cannot rise going down a ladder; no step creates information.
   **If it rises, the ladder has a leak -- report the leak, not the ladder.** This matters more than
   any number the ladder produces.
7. **ONE population, ONE scorer, ONE gold, ONE cue regime across every rung.** A number may not cross
   scorers or populations. If a rung cannot be measured on the common population, report it
   **UNMEASURABLE** rather than importing a number from elsewhere.
8. **FLOORS AND WIDTHS.** All four floor roles recomputed on the organ's own population, both tie
   conventions, CI half-width and null p95 beside every margin. A width is not an effect.

---

## 2. THE ORGANS

Ranked by expected value. **Ladder status stated honestly: exactly one organ has one.**

### ORGAN A -- THE WRITE RULE (what relation gets recorded). **LADDER: NONE. HIGHEST PRIORITY.**

- **What we know.** Our store records **co-occurrence**; the task scores **substitutability**. For
  most items the correct answer's median co-occurrence with the query is **exactly zero**. Winners are
  collocates: 79.3% have no close dictionary relation and they co-occur 4.24x more than the right
  answer. `absence -> presence` is the signature failure.
- **What we tried.** Changing the PAYLOAD bought +0.0075 CI-separated, controls clean -- the only
  intervention in 40 that moved read-out at all. Changing the SELECTION bought nothing. Binarising the
  store bought nothing.
- **The step list does not exist.** At least: token filtering, occurrence coding, accumulation across
  occurrences, normalisation, superposition. Nobody has asked which destroys the relation.
- **Brain counterpart.** Complementary learning systems: neocortex extracts **cross-episode
  regularities**, hippocampus keeps the episode. *Adjacency is episodic. Substitutability is the
  regularity.* **We built the hippocampal half and called it cortex.** PINNED: the two systems
  separate; cortical representation is organised by similarity of experience, not temporal adjacency.
  OUR INVENTION: every operator we use to do it.

### ORGAN B -- THE MEANING SPACE / TARGET. **LADDER: NONE. ONE LIVE POSITIVE.**

- Nouns clear (+0.2065 at n=666). Verbs do not (+0.1452 NOT_SEPARATED at n=222). Adjectives flat.
- Affective dimensions lift verbs 0.2696 -> 0.3705, and **both spoiler controls fired the helpful
  way**: rater-noise 0.2550, real-but-wrong scalars 0.2290, both BELOW the narrow incumbent.
  **Widening with junk actively hurts, so the gain is CONTENT, not count.** Concreteness refuted
  (partialling costs 0.0050).
- **Open flaw:** arms scored on DIFFERENT populations (3,161 / 3,317 / 3,303). **+0.1008 is not a
  valid margin** until every arm is rescored on one population with paired bootstrap CIs.
- **Brain counterpart.** Left posterior middle temporal gyrus as verb hub, tuned by **argument
  valency** and **telicity**; left mid-superior temporal cortex holding **agent** and **patient** in
  adjacent distinct subregions -- typed slots holding contents, not magnitudes. **Motor cortex RULED
  OUT** (no motor concordance; pantomime and verb comprehension doubly dissociate; verb-selective
  temporal cortex responds equally to *jump* and *think*).
- **Scope limit, to state in the same breath as any claim:** the winning arm is 15 dims of affect
  ONLY. Consequentiality failed a coverage gate; socialness norms are not on disk. **The owner's Q6
  described a picture PLUS a feeling; we have the feeling half and neither the picture nor the social
  half.**

### ORGAN C -- READ-OUT / SELECTION. **LADDER: DONE. MOSTLY CLOSED.**

- Eight interventions, each ~+0.01 or less, one negative. Total pipeline loss 0.038 against a 0.079
  gap.
- The rejector half of Q8 is real: attestation and Q11 type-violation both beat a random pick from the
  same shortlist, CI-separated. **Independence from the proposer predicts whether a rejector works**
  (attestation r=0.11 works; profile r=0.59 does not) -- necessary, not sufficient; all stayed ~3.5x
  short.
- **Iteration is NOT the missing structure.** Without feedback, bit-identical to one-shot at all ten
  rounds. With feedback, CI-separated BELOW one-shot and NOT_SEPARATED from random.
- Reframe that survives: **when the answer IS in the top 50 (37.6%), our chooser picks it 11% of the
  time.** The headroom is real; nothing we built reaches it.

### ORGAN D -- ENCODER / CUE. **LADDER: DONE. CLOSED.**

- Uncompressed beats the 256-dim projection (+0.0138); 32x more dimensions recovers almost none.
  Presence beats counts on addressing (+0.0383), transfers nothing to read-out (+0.0026).
- **Addressing and read-out are separately capped.**
- **The word-onset cue reads EXACTLY ZERO** -- not weak; we have no representation of how a word
  begins. BOARD Q16, unanswered.

### ORGAN E -- STORAGE / ADDRESSING REGIME. **LADDER: PARTIAL. LARGELY CLOSED.**

- Sparse-address/dense-value: neither capability nor efficiency.
- Per-organ regimes EVIDENCED: sparsity ~1% wins for store-and-recall; fully dense wins for
  partial-cue addressing. Same knob, two operations, opposite optima.
- **The phase diagram the owner remembered DOES NOT EXIST**: 23 of 42 parameter-by-operation squares
  never measured.
- **The binding operator has never been varied on any task this programme runs.** "Unfalsified" means
  "never tested".

### ORGAN F -- CONSOLIDATION / ACCUMULATION. **LADDER: NONE. THE ONLY POSITIVE GRADIENT WE OWN.**

- **+0.0263 [+0.0186,+0.0343] from accumulating ~72 sentences per anchor instead of 1** -- the largest
  positive effect measured anywhere, and **nobody has studied it as an organ.**
- If the gradient is still climbing at 72, that is a lever; if saturated, it bounds what more reading
  can buy. Neither is known.
- Brain counterpart: systems consolidation and replay, PINNED as a process. The basin explanation is
  **refuted** (cleanup helps in the CLOSEST stratum, not the furthest).

---

## 3. ORDER OF WORK

1. **Land the verb rescore.** Converts our one live positive from unquotable to quotable, or exposes
   it as a population artifact.
2. **Ladder ORGAN F (accumulation).** Cheapest, and the only positive gradient we have.
3. **Ladder ORGAN A (the write rule).** The ceiling lives here.
4. **Ladder ORGAN B (the meaning space)** once the rescore lands.
5. **Answer BOARD Q16 and Q17.** Both carry recommended defaults so silence is safe.

**Not doing:** more read-out choosers; more cue engineering; sparsifying anything; adopting a brain
PARAMETER as a value; wiring a spelling channel in to clear a spelling floor.

---

## 4. THE FRAME, IN THE OWNER'S WORDS

> "brain fidelity is going to help us win here - if we can truly recreate the brain process, it should
> be high performing. And we KNOW the brain works."

The brain grounds new word meanings from a small sensory core plus experience, on a fraction of our
text budget. **The capability is demonstrated.** Every null here is a fact about our implementation
and never about the capability -- and before any direction is called exhausted we write down what was
actually tested and what the stronger, more brain-faithful version would be, then test THAT.

With the refinement this week earned, applied in the same breath: **"do it the way the brain does" is
TWO instructions.** Copy the COMPUTATION exactly -- it is derived from a problem we share (separation
before completion; a dense cue addressing a sparse store; an error residual as the learning signal; a
verifier that is not the generator). Treat every PARAMETER as a hypothesis to sweep -- derived from
constraints we do not share (0.2% sparsity, seven gamma cycles, a five-hour tagging window). **Our
worst result copied a NUMBER. Our best copied an OPERATION.**

Honest caveat on fidelity as a predictor: **supported at low fidelity**, **bounded at high fidelity**
(two studies find it inverting at the top), and **untested here for power reasons** (1 positive in 6
cannot yield p below 1/6). It is our best heuristic for choosing what to build; it is not yet a
measured predictor of our performance. Both halves are load-bearing.

---

## 5. WHAT WOULD MAKE THIS PLAN WRONG

- **If Organ A's ladder shows ONE step dominating**, the deficit is NOT distributed, the Director's
  2026-08-17 conclusion is wrong, and that step gets rebuilt.
- **If the verb rescore collapses to NOT_SEPARATED**, the programme has ZERO live positives and no
  organ we have built beats its floors.
- **If accumulation is still climbing steeply at 72 sentences**, "more reading" is a lever we ignored
  while optimising everything downstream, and the order above is wrong.

---

## 6. RESULTS SINCE THIS PLAN WAS WRITTEN -- TWO LADDERS LANDED THE SAME NIGHT

**Both stop-ifs in section 5 FIRED. The plan's own order of work was wrong, in the way it predicted.**

### 6.1 ORGAN A LADDER LANDED (`exp_writerule_step_ladder_v1`, commit `ab3555eb6`)

- **The write rule is FOUR live steps, not five.** "Superposition" is not a separate step -- it is the
  SAME EVENT as coding. Same class of correction as the read side's 9 -> 5. **The Director's model of
  the machine has now been wrong about the joints twice; enumerate from live code, always.**
- **ONE STEP DOMINATES: ACCUMULATE, at 64% of total drop mass.** This **REFUTES the Director's
  2026-08-17 "the deficit is distributed" conclusion FOR THIS ORGAN.** Recorded as a correction, not
  softened.
- **The composition measurement is the real finding.** Across that single step the share of top-1
  winners that have EVER co-occurred with the query jumps **66.0% -> 94.4%**. *Unweighted summation is
  the operation that converts our store into a record of adjacency.*
- **`sign()` NORMALISE has been OFF BY DEFAULT since 2026-08-14.** Every headline number in this arc,
  including 79.3% no-relation and 4.24x co-occurrence, was measured with quantisation NOT FIRING.
  Anyone who believed it was in the live path was wrong.
- Its coded verdict string and its written conclusion disagree (stop-if iii fired mechanically; its
  precondition of flat accuracy does not hold). The author disowned the string in the note. **Do not
  quote that verdict.**

### 6.2 ORGAN F LADDER LANDED (`exp_organ_f_accumulation_depth_ladder_v1`, commit `379c42833`)

- **DEPTH IS STILL CLIMBING PAST OUR OPERATING POINT.** 72 -> 128 sentences per anchor is **+0.0503
  [+0.0139,+0.0861]** CI-separated on the best-powered population; gold median rank falls **4-6x**
  with depth (38 -> 9). Past 128 is UNDERPOWERED, **not** a measured plateau -- say "underpowered",
  never "saturated".
- **All three spoiler controls failed to explain it:** token-matched (+0.039 ABOVE), random-occurrence
  (+0.1057 ABOVE), and a deliberately lower-frequency stratum showing the same late-rise shape. It is
  not tokens, not any-material, not frequency in disguise.
- **THE "72" IS AN ARBITRARY CODE CONSTANT** (`K_SENT_TOTAL=90` in `build_buckets`), **not a corpus
  limit.** Uncapped, the most frequent anchor reaches **k=2,019**. *We have been operating at a
  ceiling nobody chose.*
- **A REAL LEAK WAS FOUND AND FIXED BEFORE IT CONTAMINATED ANYTHING.** The held-out evaluation
  sentence sits INSIDE the first-90 window, so naively reading deeper pulls the answer into the store.
  A leak-safe profile pool was built and self-tested against a hand-built example with a real gap.
  **Any future depth work MUST reuse that pool.** This catch alone justifies the ladder method.

### 6.3 THE RECONCILIATION, AND THE BUILD TARGET IT PRODUCES

The two ladders report the SAME MAGNITUDES WITH OPPOSITE SIGNS (accumulation +0.0263 as a gain,
-0.0263 as a drop; projection 0.0123 either way). They are not in conflict -- they answer different
questions, and **both are true**:

> **MORE EVIDENCE HELPS. COLLAPSING IT INTO ONE UNWEIGHTED SUM THROWS PART OF IT BACK AWAY AND BIASES
> WHAT SURVIVES TOWARD CO-OCCURRENCE.**

**So accumulation is simultaneously our best lever and our worst destroyer, and the build target is
ACCUMULATE WITHOUT COLLAPSING** -- keep episodes distinguishable (multi-vector, per-occurrence
normalisation, or downweighting the high-frequency context words that carry adjacency rather than
identity) instead of averaging them into one point. That is the first genuinely actionable design
instruction this programme has produced, and it is brain-framed rather than tool-framed: **PINNED**
that neocortex extracts cross-episode REGULARITIES while hippocampus keeps the EPISODE; adjacency is
episodic, substitutability is the regularity; **we built the hippocampal half and called it cortex.**

*In flight: `accumulate-no-collapse`, with a RANDOM-PARTITION control so a multi-vector store cannot
win merely by having more vectors to match against, and matched-storage as well as matched-depth
comparisons so it cannot win by being bigger.*

### 6.4 REVISED ORDER OF WORK

1. Land the verb rescore (in flight; 4 of 5 arms scored on the common n=3161 -- A0 0.2711, A1 0.3705,
   A2 0.3081, A3_noise 0.2543 BELOW baseline; paired CIs outstanding).
2. **Accumulate-without-collapsing** (in flight). Promoted above everything else on the strength of
   6.3.
3. **Raise the arbitrary depth cap** and re-measure end to end, using the leak-safe pool. We are
   leaving measured, controlled gains on the table at 72.
4. Ladder ORGAN B (the meaning space) once the rescore lands.
5. BOARD Q16 and Q17 remain unanswered; both carry recommended defaults so silence is safe.
