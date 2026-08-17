# QUESTION LOG -- what we asked the owner, and whether it was worth asking

**Written 2026-08-16 by the Director, at the owner's request:** *"It would be nice if you kept a log
of all the questions (maybe just each thrust, not every single one) and how helpful they were and
why."*

Grouped by **thrust**, not one row per question, because several questions were the same enquiry
asked twice. Nine questions have been answered to date (Q1-Q9); they fall into six thrusts.

**Every answer below is quoted verbatim from `notes/BOARD.md` ANSWERED table** (read 2026-08-16,
HEAD `fa38d15a9`). The "what it changed" column is checked against the artifact named beside it, not
against recollection.

**Honesty rule for this file:** a question that changed nothing is rated LOW and the reason is
stated. Two of the six thrusts below are rated LOW or MEDIUM, and one of those was the Director's
fault, not the owner's.

---

## THRUST 1 -- INFRASTRUCTURE AND THE OVERNIGHT LOOP (Q1, Q2)

**The questions.**
- Q1: Remove the duplicate Stop-hook registration from the user-level settings, which registers
  `data/hooks/staging/stop_hook.py` a second time on top of the project-level one?
- Q2: Is UNLIMITED the cap you actually want for the overnight loop, or a large finite number?

**What was blocked.** Nothing scientific. Q1 blocked retiring a dedupe mitigation
(`HD_STOP_DEDUPE_WINDOW_S`). Q2 blocked arming the unattended loop at all.

**The owner's answer, verbatim.**
> Q1: "implement your recommendation"
> Q2: "200 sounds good, as long as that will definitely last untill noon tomorrow - 14 hours from now"

**What it actually changed.** The duplicate hook registration was removed and the loop was armed at
`--max 200`. That is the whole effect. No design, no arm, no floor, no number moved.

**HELPFULNESS: LOW (Q1) / LOW-MEDIUM (Q2).**

**Why, stated plainly.** Q1 is the exact anti-pattern this log exists to name: **it asked the owner
to make a call the evidence had already made.** The recommendation was correct, the owner said
"implement your recommendation", and the only thing the question bought was consent -- which the
permission system would have supplied anyway. It cost the owner an interruption and returned no
information.

Q2 is slightly better and only slightly: the owner's reply carried one thing the Director did not
have -- **a duration requirement ("until noon tomorrow, 14 hours")** -- which is a constraint, not a
preference, and could not have been derived from the repo. That single clause is the entire research
value of both questions combined. The correct form would have been to ask for the *duration* and
choose the cap ourselves.

---

## THRUST 2 -- WHAT COUNTS AS AN ADMISSIBLE FOUNDATION (Q3)

**The question.** Are pretrained static embedding tables (GloVe / word2vec / fastText, already on
disk) admissible as a MEANING SOURCE, or only as a ceiling reference?

**What was blocked.** The entire static-foundation arm. The Director's standing recommendation was
**CEILING REFERENCE ONLY**, on the grounds that co-occurrence tables are not how the brain grounds
meaning and that adopting one would be "reaching for the convenient tool". Under that ruling, no
experiment was permitted to *use* a static table as a foundation ingredient -- only to cite it as a
known-answer arm proving the ruler works.

**The owner's answer, verbatim.**
> "We can build a foundation in whatever way is most efficient. the brain began with hundreds of
> millions of years of evolution instilling a foundation. we can build that foundation however we
> want, as long as it is a strong foundation, and the operation is not llm"

**What it actually changed -- and this is the largest single change any answer has produced.**

The owner **overruled the Director with a better brain argument.** The Director had reasoned from
brain fidelity and got the fidelity wrong: **the brain did not derive its foundation from scratch
either. Evolution installed it over hundreds of millions of years.** Holding our substrate to a
from-scratch standard was holding it to a standard *stricter than the brain itself*. The invariant
that actually matters -- **no language model in the operational flow** -- was untouched by the
owner's ruling and remains the only bar.

Downstream, verified on disk:
- `data/exp_foundation_neighbourhood_purity_v1_smoke_g2/metrics.json`, verdict
  `A_FOUNDATION_CLEARS_THE_BINDING_FLOOR`: a pure static-table foundation lifts top-20 neighbourhood
  synonym purity 0.0046 -> 0.0353 and the exact-key read-out 0.0462 -> **0.3265**, which is
  **+0.1196 [+0.0950,+0.1442]** above that population's constant/prototype floor of 0.2070
  (population n=2358, 14 foundations). *This is the programme's first clearance of the constant
  floor.* Reported by the dispatched agent; the metrics file and verdict string are confirmed on
  disk by the Director, the CI is the agent's computation.
- The same run produced the finding that matters more than the clearance:
  **our own operator, fed the better supply, reaches 0.3083 (+0.1012 over the same floor).** Our
  machinery was **starved, not broken.** That sentence does not exist without Q3.
- `notes/LONG_TERM_PLAN.md` section 4 was rewritten around the answer, and section 6's "GloVe would
  raise our number tomorrow and teach us nothing -- ceiling reference only" is now superseded there
  (the line survives in section 6 and should be read as superseded).

**HELPFULNESS: VERY HIGH.**

**Why, and the honest caveat.** By the criterion this log adopts below -- *do not ask the owner to
make calls the evidence should make* -- Q3 looks like a violation: it is a policy question, not an
introspection question. It earns its rating anyway for a specific reason: **the Director's own
recommendation was WRONG, and wrong in a way no amount of further measurement would have exposed,
because it was an error about the brain, not about the data.** That is precisely the class of
question worth an interruption. The generalisable lesson is not "ask more policy questions" -- it is
**ask when your recommendation rests on a brain claim you have not sourced.**

---

## THRUST 3 -- WHAT A PARTIAL CUE IS ACTUALLY MADE OF (Q4)

**The question.** When you half-remember a word, what is the PARTIAL CUE actually made of? Is it a
few features, a related word, the sound or shape, the situation you met it in, or the role it played
in a sentence?

**What was blocked.** Our completer machinery implements a **degraded copy** of the stored pattern
as its cue. Nothing told us whether that resembles a real partial cue, so every completion negative
was uninterpretable: we could not say whether the mechanism failed or whether we had been feeding it
the wrong kind of cue for months.

**The owner's answer, verbatim.**
> "if I half remember a word, there are two things:
> 1) words that start with a certain sound - like unhelpful, or unhealthy, are all similar to me -
> the starting sound helps me consider what the rest of the word might be
> 2) If i know what the word means, I can think of other words that mean the same thing. Those same
> meaning words are often clumped together in my memory, so thinking of the others can trigger
> remembering the whole word"

**What it actually changed.** This is the answer that looked like a feeling and was a **testable
claim about storage layout**. "Same meaning words are often clumped together in my memory" is not a
mood; it is a statement that in the owner's store, synonyms are near neighbours. We measured whether
that is true of ours.

- `exp_two_channel_cue_*` (fragment `.claude/scan-out/two-channel-cue.json`) turned channel 1 into a
  **narrowing** measurement (self-recovery 0.0711 -> 0.5734 when the candidate set is cut from 5,491
  to about 12 by word onset -- and a **size-matched random set does it marginally better**, so the
  value is the SIZE, not the onset), and channel 2 into a synonym-cue arm that clears all four
  required floors but sits 0.3145 BELOW the reading cue we already had. It then ran the owner's
  clumping claim as a **known-answer arm**: an oracle that clumps synonyms takes the channel from
  0.2417 to **0.7515**, with a measured optimum. That is where the target
  **"raise mean word-to-synonym cosine from 0.127 to about 0.45"** comes from. These are the
  dispatched agent's measurements.
- `exp_synonym_clumping_consolidation_v1` (`b84417941`, fragment
  `.claude/scan-out/synonym-clumping.json`) then **hit the target and it bought nothing**: Hebbian
  replay of the store's own geometry moves word-to-synonym cosine 0.1214 -> **0.4705** and the
  semantic channel is NOT_SEPARATED at every dose, with the reading cue CI-separated BELOW.
  The measured reason is the defining statistic of our store:
  **only 0.46% of a word's top-20 neighbours are its synonyms.**
- That single number is now load-bearing across the programme. It explains a long run of nulls in one
  sentence: **any mechanism that replays, reinforces, re-weights or completes from the store's own
  neighbourhoods is operating on a set that is 99.5% wrong.**

**HELPFULNESS: HIGHEST (joint with Q8).**

**Why.** It converted a subjective report into a **measurable property of our store**, and that
property turned out to be the thing that was wrong. Note the shape of the win: the owner's claim was
**confirmed about their memory and refuted as a lever for ours** -- reaching the clumping target was
worth less than nothing (participation ratio collapsed 171 -> 31). A question is not valuable because
its answer is adopted. It is valuable because it produced a number that decided something, and this
one decided that **the defect is SUPPLY, not stirring.**

---

## THRUST 4 -- HOW A NEW WORD GETS ITS MEANING (Q5, Q7)

**The questions.**
- Q5: When you meet a new word in a sentence, what do you actually take from it? (Worked example:
  *"the tove ran across the road"*.)
- Q7: When you meet an unknown word while reading, are you RETRIEVING a word you already know, or
  CREATING a new entry?

**What was blocked.** Our bridging mechanism builds a new word's code by **copying / averaging its
graph neighbours' codes**. Nothing told us whether that is what a person does. And our read-out
scores "infer a novel word" and "recall a known word" on **one metric**, which is only legitimate if
they are one operation.

**The owner's answers, verbatim.**
> Q5: "Since the tove ran - it must be an animal (or at least something that has legs). Since it ran
> accross the road, I think of rabbits and deer which I've seen cross roads, and so I assume it's a
> smallish animal, most likely a mammel but it could also be a reptile."
> Q7: "I searched my vocabulary first. Many words have origins that indicate potential meaning. Then,
> after confirming I didn't know it, I started determining what it could be from the sentence, by the
> most helpful being 'ran accross the road'. It can run, and it exists in nature and can be found
> near roads."

**What it actually changed.** Three things, and the first is the sharpest observation in the whole
board:

1. **The owner never copied a neighbour word.** They used the **verb's selectional constraint**
   ("ran" implies legs, implies animal), then **episodic recall** ("rabbits and deer which I've
   SEEN cross roads"), then produced a **distribution over categories** ("most likely a mammal but
   it could also be a reptile"). Our bridge does the one thing they did not do. That mismatch is now
   the design of `exp_selectional_bridge_*` (fragment `.claude/scan-out/bridge-via-selectional.json`,
   running as PID 27644 at the time of writing). **NO SCORE EXISTS YET.**
2. **Retrieval is tried FIRST, and creation happens only after retrieval FAILS** (Q7), with
   **morphology and word origins used inside the retrieval attempt.** That is a two-stage
   architecture with a failure detector between the stages. We have neither the stages nor the
   detector; we have one scorer over both.
3. The answer is a **distribution, not an argmax** -- which is the same finding Q8 produces from a
   different direction, and their agreement is what makes it credible.

**HELPFULNESS: HIGH IN DESIGN, UNCASHED IN RESULT -- rated MEDIUM-HIGH and it cannot be rated
higher yet.**

**Why the deflation.** Q5 and Q7 changed what we are building, which is real. But the cell is still
running and **no arm has been scored**, so on this project's own standard -- a CI-separated margin
over the strongest floor -- these questions have so far bought a design and not a result. The
Director will re-rate this thrust when a number lands, in either direction. Recording the rating as
provisional is the point: a question's value is not established by the enthusiasm of the person who
asked it.

---

## THRUST 5 -- WHAT A VERB'S MEANING IS, AND IS IT SPECIFIC OR GENERIC (Q6, Q9)

**The questions.**
- Q6: What IS a verb's meaning to you -- a picture, a body feeling, a before/after change, or a slot
  structure?
- Q9: When you picture 'pour', is it a SPECIFIC remembered pouring, or a generic one?

**What was blocked.** Q6 blocked deciding whether verbs and nouns land in the **same representational
space**. Q9 blocked the episodic-versus-schematic storage question (complementary learning systems).

**The owner's answers, verbatim.**
> Q6: "I think you're right it needds a different slot structure.
> When I think of pour I defiitely think of pouring a liquid.
> Pursuade is more thinking of talking to someone and convincing them - I picture the conversation.
> For both, it's a picture that I think of first, and also a feeling for pursuade"
> Q9: "It's generic pouring - definitely not specific."

**What it actually changed.**

- Q6 **corroborated** an independent measurement rather than redirecting anything. On the same day,
  the target-space drill (`03055c7fa`, fragment `.claude/scan-out/target-space-drill.json`) measured
  that adding an AFFECT channel to our 12-dimensional landing space lifts the hand-rated SimLex
  ceiling **+0.1013 [+0.0615,+0.1419]** overall on 977 paired items, with **verbs +0.1228
  [+0.0150,+0.2314]** and **adjectives +0.3399 [+0.1919,+0.4978]** separated while **nouns +0.0253
  are NOT separated** -- and the negative control fired (widening by 11 rater-SD columns *lowers* the
  score). The owner's "and also a feeling for persuade" is the same finding reported from the inside.
  Corroboration from an independent source is worth something. It is worth less than a redirection.
- Q9's "GENERIC" combined with Q5's **episodic** answer for a NOVEL word is the finding: **episodic
  for novel inference, schematic for known concepts.** That is the complementary-learning-systems
  split, arrived at by introspection. It has been **filed to Phase 5 and explicitly not built**
  (`.claude/scan-out/propose-reject-retrieval.json`, `Q9_FILED_NOT_BUILT`).

**HELPFULNESS: MEDIUM.**

**Why, and this is the honest part.** Q6 largely **confirmed a hypothesis the Director already
held** and had already written into the plan ("verbs need a different representation from nouns
entirely"). The question was phrased with the recommendation attached -- *"If it is mostly the
slot-structure, verbs need a different representation"* -- and the owner opened with "I think you're
right". **A question that leads with your own conclusion is a weak question**, because agreement is
the likely reply whether or not the conclusion is sound. Its saving grace is that the owner's
*unprompted* addition ("and also a feeling") pointed at a channel the recommendation had not named,
and that channel is the one the measurement independently found.

Q9 is well-formed and cleanly answered and has so far changed **nothing that runs**, because it was
correctly deferred. It will be re-rated if and when Phase 5 uses it.

---

## THRUST 6 -- HOW THE ANSWER ARRIVES (Q8)

**The question.** When a word finally arrives after being on the tip of your tongue, does it ARRIVE
or do you FIND it? Do wrong candidates come up and get rejected (iterative search with a reject
step), or does the right word simply appear (one-shot addressing), or does it arrive later unbidden
(a slow background process)?

**What was blocked.** Our read-out is a **single `argmax`** over a 5,491-anchor store. That is
one-shot addressing with no reject step and no second attempt. Every selection intervention we have
run assumed that shape.

**The owner's answer, verbatim.**
> "wrong candidates definitely come up and get rejected. It's often iterative - if I cant bring up
> the word at the beginning - I either can figure it out through thinking it through, or I have to
> ask someone. I often have a sense of what the first letter is, but htat could just be me."

**What it actually changed. This answer contradicts our architecture.**

`exp_propose_reject_retrieval_v1` exists because of it
(`.claude/scan-out/propose-reject-retrieval.json`, cell being authored at the time of writing;
**no number yet**). The redirection is specific and cheap to state: a **PROPOSE -> TEST -> REJECT ->
RE-PROPOSE** loop is a different algorithm from `argmax`, it has a **failure detector** (the thing
that decides a candidate is wrong), and it terminates on a test rather than on a maximum. We had
never built a component that can say "that one is wrong, try again".

Two supporting facts already measured make this more than a suggestion:
- our storage cannot currently *support* a second attempt from the cue it has -- the sparse key
  addresses the store **1.0000 from the store's own rows and 0.0325 from the partial cue**
  (`data/exp_cue_to_store_translation_v1/metrics.json`, n=1997, verified by the Director on disk).
  A propose-reject loop needs a proposer that is right sometimes; ours is right 3.25% of the time.
- the owner's "I often have a sense of what the first letter is" is the **form channel**, and the
  same cell measured that combining the form channel and the meaning channel **at the decision**
  beats our read-out in all four pools (+0.0376 / +0.0512 / +0.0191 / +0.0171) where the additive
  union of the two channels had *lost* (-0.0612). The channels were being combined in the wrong
  place. That is the owner's own two-part description of tip-of-the-tongue, reproduced as an
  architecture.
  **Honest label carried from the source: that arm does NOT clear the floor set** -- its form
  channel IS the spelling floor, so beating our own read-out with a speller attached is an
  ingredient's score, not a clearance.

**HELPFULNESS: HIGHEST (joint with Q4).**

**Why.** It converted a subjective report into a **measurable property of our algorithm** -- one
argmax versus an iterate-and-reject loop -- and the property it named is one we had never questioned
and never tested. It is the only answer on the board that **contradicted** the architecture rather
than adding to it. Deflation, stated: like Thrust 4, its cell has produced no number, so what it has
bought so far is a corrected assumption. Corrected assumptions are worth a great deal in a programme
whose last six months of interventions all measured null on the assumption Q8 broke.

---

## WHAT MAKES A GOOD QUESTION HERE

Derived from the nine above, not from a style guide.

**1. Ask what a mental state is MADE OF, or what they actually DID. Never ask what they think we
should do.** Q4 ("what is the partial cue made of") and Q8 ("does it arrive or do you find it") are
the two highest-value questions asked to date, and they share exactly one property: **each turned a
subjective report into a measurable property of our store or our algorithm.** Q4 became "0.46% of a
word's top-20 store neighbours are its synonyms" and a target of 0.45 cosine. Q8 became "our read-out
is a single argmax and the brain's is a loop with a reject step". Neither could have been derived
from the repository, and both were falsifiable within a day.

**2. Do not ask them to make calls the evidence should make.** Q1 is the clean failure. The
recommendation was right, the evidence was already in hand, and the reply was "implement your
recommendation". The cost was an interruption; the return was zero.

**3. The exception, and it is narrow: ask when your recommendation rests on a brain claim you have
not sourced.** Q3 is formally a policy question and would fail rule 2, except that the Director's
recommendation contained a **wrong claim about the brain** -- that a foundation must be derived from
scratch -- and no further measurement would ever have surfaced it. The owner's correction (evolution
installed the brain's foundation over hundreds of millions of years) unblocked the arm that produced
the programme's first floor clearance. **Test before asking: is my recommendation resting on
something I can cite? If not, ask.**

**4. Never attach your own conclusion to the question.** Q6 is the counter-example: it was phrased
"if it is mostly the slot-structure, verbs need a different representation", and the reply opened "I
think you're right". Agreement is the likely reply to a leading question whether the conclusion is
sound or not, so an agreeing answer carries almost no information. What *did* carry information was
the owner's unprompted addition ("and also a feeling for persuade"), which no part of the question
had invited.

**5. Ask for the CONSTRAINT, not the SETTING.** Q2 asked for a number and got a number plus the
thing that mattered: "as long as that will definitely last until noon tomorrow". The duration was the
requirement; the cap was ours to compute. Asking for the setting nearly lost the requirement.

**6. A question's value is measured by what CHANGED, not by how interesting the answer was.** Q9's
answer ("generic pouring, definitely not specific") is genuinely interesting and has so far changed
nothing that runs, because it was correctly deferred to Phase 5. It is rated MEDIUM for that reason
and will be re-rated if Phase 5 uses it. Symmetrically, Q4's greatest contribution was a **null** --
the clumping target was reached and bought nothing -- which redirected the whole programme from
stirring the store to supplying it.

**7. Rate a thrust as provisional until a number lands.** Thrusts 4 and 6 (Q5/Q7 and Q8) changed what
we are building and have produced no scored arm yet. They are logged at MEDIUM-HIGH and HIGHEST
respectively on the strength of a corrected assumption, and both ratings are explicitly open to
revision downward.

---

## SCOREBOARD

| thrust | questions | what it changed | rating |
|---|---|---|---|
| 1 Infrastructure | Q1, Q2 | one hook removed, loop cap 200; one real constraint (14 h) | LOW / LOW-MEDIUM |
| 2 Admissible foundation | Q3 | unblocked the static-foundation arm -> first constant-floor clearance (+0.1196) | VERY HIGH |
| 3 What a partial cue is made of | Q4 | target 0.127 -> ~0.45; the 0.46% synonym-purity statistic; supply-not-stirring | HIGHEST |
| 4 How a new word gets meaning | Q5, Q7 | selectional-constraint bridging; retrieve-then-create split; no score yet | MEDIUM-HIGH (provisional) |
| 5 What a verb's meaning is | Q6, Q9 | corroborated the affect channel; CLS split filed to Phase 5 | MEDIUM |
| 6 How the answer arrives | Q8 | contradicted single-argmax; propose-and-reject loop being built | HIGHEST |

**Open questions on the board right now: none.** `notes/BOARD.md` QUESTIONS FOR YOU is empty.

**CURRENCY NOTE (2026-08-16, later).** The six thrusts above cover Q1-Q9. Q10 (what a rejection is
checking), Q11 (judging unseen combinations), Q12 (what makes you give up) and Q13 (the phase-diagram
answer, recovered -- see below) have since been answered and are **NOT yet rated**. They are named
here so this log does not read as complete when it is not.

---

# PART 2 -- THREE RULES THE QUESTIONS THEMSELVES MUST FOLLOW

**Written 2026-08-16 after a question the owner could not answer.** Part 1 rates questions by what
their ANSWERS changed. This part is about the questions we ASK, and it exists because one of them
failed before it ever got an answer. That is a different kind of defect and it was costing the only
introspective instrument this project has.

**The incident.** Asked to look at the standing decisions, the owner replied:

> *"For OP1: I don't know what you're asking - are you saying these have already been copied in
> saying they work really well?"*

And separately, while answering Q12:

> *"In general, you should include context in these questions. I do not remember what Q7 was."*

**Neither is a failure of the owner.** Both are defects in the question. A question the owner cannot
answer wastes the instrument entirely -- it is worse than the Q1 anti-pattern in Part 1, because Q1
at least returned consent.

---

## RULE 8. NEVER USE A BARE IDENTIFIER AS THOUGH IT CARRIED CONTEXT. RESTATE IT INLINE, EVERY TIME.

`D1`, `OP1`, `Q7`, `C30`, `A8`, "the floor", "this branch", "the same checkpoint fault" -- every one
of these is a pointer, and **the owner is not holding the thing it points at.** They read this on a
phone, hours later, with none of the session's context. "I do not remember what Q7 was" is the whole
argument: we asked a follow-up that required the reader to remember a question from earlier that day.

The identifier may stay as a LABEL. It may never stand in for the CONTENT. Write
"Q7 -- when you meet an unknown word while reading, are you retrieving a word you already know or
creating a new entry? -- you said you searched your vocabulary first", not "For Q7...". The cost of
restating is one sentence. The cost of not restating is an unanswerable question.

**This applies to project vocabulary too.** "Spoke", "floor", "tier", "collision-affected",
"pre-registration", "the live path" are our words, not the owner's. Gloss them in the question or do
not use them. CLAUDE.md and MEMORY.md both already say plain language, twice on the owner's own
instruction; a bare project term is the same violation in a smaller package.

## RULE 9. STATE WHAT IS CURRENTLY TRUE BEFORE ASKING ANYTHING.

**OP1 failed on exactly this.** Its question was *"What do we do about 238 results whose claim does
not survive the standard, and which have ALREADY been cited by the certificate ledger or the
capability list?"* -- and the owner could not tell **whether it was asserting something already done
or proposing something new**: *"are you saying these have already been copied in saying they work
really well?"*

That ambiguity is structural, not a wording slip. The question opens with a judgement ("overstated",
"does not survive the standard") that the reader has to accept before the question makes sense, and
it never separately says what the CURRENT STATE OF THE WORLD is. So the reader cannot tell where the
factual part ends and the proposal begins.

**The fix is an ordering, and it is mechanical:**

1. **WHAT IS TRUE NOW** -- plainly, with no judgement words, no jargon, and the numbers named
   including their metric. "X exists. It says Y. Nothing has been done to it."
2. **WHAT HAPPENS IF NOBODY DOES ANYTHING** -- silence is a choice; say what it chooses.
3. **THEN THE QUESTION.**

If step 1 cannot be written without a project term, the question is not ready to be asked.

## RULE 10. ASK ONE THING. IF THE READER MUST WORK OUT WHAT IS BEING ASKED, THE QUESTION IS THE DEFECT.

Not "one sentence" -- **one decision**. "Do we wire a learned transformer encoder into the
representation at all?" carries at least three (should we measure it, should we wire it, does it
count as a legitimate ingredient) and its own recommended default answers a different one from the
one asked. A reader who has to disentangle that will either answer a sub-question we did not mean or
answer nothing, and both outcomes look like silence.

**The test, applied before asking:** can the answer be a single choice or a single description? If
answering well requires the reader to first decide WHICH question they are answering, split it. And
note the asymmetry with rule 9 -- offering two named options ("authorise X, or drop Y") is still ONE
question; asking about two different subjects in one row is not.

**These three sit alongside rules 1-7 above, which are about what to ask. Rules 8-10 are about
whether the question is answerable at all, and they are checked FIRST -- an unanswerable question
cannot be a valuable one.**

---

# PART 3 -- AUDIT OF EVERY OPEN QUESTION AND DECISION AGAINST RULES 8-10

**Done 2026-08-16.** Enumerated from the live collectors rather than from recollection:
`status_state.collect_board()` for board questions and `status_plan.collect()` for the plan's
section-9 decisions and the standing operator rows -- the same calls the status window's
WAITING ON YOU tab makes, so this audit covers exactly what the owner is shown and nothing else.

**Population: 0 open board questions, 7 plan decisions (D1-D7), 4 standing rows (OP1-OP4) = 11.**
**8 of 11 FAIL at least one rule.** Rewrites below.

| item | R8 bare identifier | R9 current truth | R10 one thing | verdict |
|---|---|---|---|---|
| D1 dimensionality 256 -> 1024 | "the live path" ungloss | number given with NO metric named | one | **REWRITE** |
| D2 wire a learned encoder | "the representation" | never says it is currently unwired AND unmeasured | **three decisions in one** | **REWRITE** |
| D3 does it count as a "spoke" | "spoke", "the floor" -- both bare | conditional on unresolved D2 | one | **REWRITE** |
| D4 migrate 38 experiment files | "the old checkpoint contract" | states it ("warning, not protection") | one | **REWRITE** |
| D5 re-run 98 archive-tier cells | "ARCHIVE-tier", "collision-affected" | "lowest value at highest cost" is a judgement, not a fact | one | **REWRITE** |
| D6 merge branch to origin/main | "this branch" | states it | one | **light rewrite** |
| D7 is growth still paused | "growth" | its own WHY answers the question | **not a question at all** | **REWRITE** |
| OP1 238 overstated results | "the standard", "certificate ledger", "capability list" | **the named failure** | one | **REWRITE (priority)** |
| OP2 4 missing pre-registrations | "collision-affected" | states it well | one (two named options is fine) | **PASSES**, light gloss |
| OP3 98 archive-tier experiments | "the same checkpoint fault" -- bare back-reference | judgement before fact | one | **REWRITE + it duplicates D5** |
| OP4 status file over its cap | described, not named -- acceptable | states it well, with numbers | one | **PASSES** |

**Where the rewrites live, and why they are not applied in place.** D1-D7 are owned by
`notes/PLAN.md` section 9 and OP1-OP4 by `notes/STATUS.md`; both documents are outside this agent's
write scope, and both are parsed by `tools/status_plan.py`, so an edit to either is a parser-coupled
change belonging to whoever owns them (CLAUDE.md: *"a doc parsed by code is coupled to it"*). The
corrected text is therefore written out below, ready to paste, with the shape preserved.

---

## OP1 -- THE ONE THE OWNER COULD NOT ANSWER. REWRITTEN.

**As asked (verbatim, and it failed):**
> *238 overstated results have already been copied into an index.* What do we do about 238 results
> whose claim does not survive the standard, and which have ALREADY been cited by the certificate
> ledger or the capability list?

**Why it failed, precisely.** It leads with a verdict ("overstated") that the reader has to accept
before the sentence parses; it names two internal documents the owner has never opened; it never
says what "the standard" IS; and it gives no way to tell an assertion from a proposal -- which is
exactly what the owner asked about.

**REWRITTEN:**

> **What is true now.** We have 238 recorded experiment results whose written conclusion claims more
> than the numbers in that same result support. In each case the result beat nothing it had to beat:
> our bar is that a score must be clearly above the best "no understanding" baseline -- a
> spell-checker, or word-frequency, or scrambled input -- and these 238 were written up as wins
> without that comparison being made or passed.
>
> **They have already spread.** Two lists that the rest of the project reads and quotes -- our
> record of certified results, and our list of what the system can do -- already cite them. So any
> new work that consults those lists inherits the overstatement without knowing it.
>
> **What happens if nobody does anything.** Nothing changes. The 238 stay in both lists, unmarked,
> and continue to be quoted. The tool that found them deliberately changed nothing.
>
> **The question.** Do we mark all 238 in place as "claim not supported -- do not quote", which
> takes hours and stops the spread but does not decide whether any individual one was right? The
> alternative is re-examining them one at a time, which is weeks of work.
>
> **My recommendation:** mark them. Stopping the spread is the urgent part; re-adjudication is not.

**Note it now passes what it failed:** no bare identifier, no project jargon, the current state is
stated in plain words BEFORE any proposal, the assertion and the proposal are visibly separate, and
there is exactly one decision.

## D2 -- REWRITTEN (it was three questions)

**As asked:** *Do we wire a learned transformer encoder into the representation at all?*

**Split into the three decisions it was carrying, of which only the first is live:**

> **What is true now.** We trained our own text encoder from scratch -- 27 million parameters, no
> outside language model involved. It is finished and it is NOT connected to anything, and we have
> never scored it against the baselines it would have to beat.
>
> **What happens if nobody does anything.** It stays disconnected and unmeasured.
>
> **The question (the only live one):** do we spend the compute to score it against the baselines?
>
> Two further decisions follow ONLY if it scores well, and are deliberately not being asked yet:
> whether to connect it, and whether a text-trained encoder counts as a legitimate source of meaning
> for our purposes. Asking all three at once is what made this unanswerable.

## D3 -- REWRITTEN (two bare terms, and it asked for a ruling on our own vocabulary)

**As asked:** *If the learned encoder does clear the floor, does it count as a "spoke"?*

> **What is true now.** We describe our sources of meaning as connected to real experience -- seeing,
> touching, moving. The encoder above learns only from text. The research literature is consistent
> that text alone recovers abstract meaning fairly well, sensory meaning poorly, and physical-action
> meaning barely at all.
>
> **The question.** If the text-only encoder scores well, should we describe it as a source of
> grounded meaning, or record it as a text-derived source and keep it labelled as our own untested
> invention?
>
> **My recommendation:** the second. It costs nothing and it keeps the claim honest.

Note the removal of "clear the floor" and "spoke" -- neither survives contact with a reader who does
not already know what we mean, and neither was necessary.

## D1, D4, D5 / OP3, D6, D7 -- THE REMAINING REWRITES, IN BRIEF

- **D1** (raise dimensionality 256 -> 1024): state the metric. "+0.0843" is meaningless without it,
  and "the live path" must become "the parts of the system that are actually running". Rewritten
  opening: *"We currently run at 256 dimensions everywhere. A test at 1024 scored 0.0843 higher on
  [NAME THE METRIC AND THE POPULATION]. Nothing is at 1024 today."*
- **D4** (migrate 38 experiment files): "the old checkpoint contract" must say what it means and what
  it costs. Rewritten opening: *"38 experiment files still save their progress the old way. If one is
  interrupted it loses more work than it needs to. They currently print a warning and nothing else."*
- **D5 and OP3 are the same decision asked twice**, in two documents, with different wording -- the
  duplication is itself a defect and Part 1 already flagged repeat-asking. **Merge them into one.**
  Rewritten: *"98 old experiments were run with a fault that let two runs overwrite each other's
  saved progress, so their numbers may be wrong. They have all been superseded by newer work.
  Re-running them is the single largest block of compute left. If nobody does anything they stay in
  place, unmarked. Do we mark them 'may be wrong, do not quote' and move on?"* Delete the other copy.
- **D6** (merge the branch): "this branch" -> name it, and say what merging would and would not
  change. One added sentence.
- **D7** (is growth still paused): **this is not a question and should not be on a list of things
  waiting on the owner.** Its own supporting text answers it ("It is"). It is a status line. Move it
  to the status display and take it off the decision list, or replace it with the real question,
  which is *"what would have to be true for us to restart it?"*
- **OP2** and **OP4** pass. OP2 should gloss "collision-affected" once. OP4 is well-formed, and its
  only weakness is a Part-1 rule-2 issue rather than a rule 8-10 one: the evidence has arguably
  already made this call.

---

## WHAT THIS AUDIT COST, STATED PLAINLY

**8 of 11 items the owner is shown were not answerable as written.** They have been sitting on the
WAITING ON YOU panel being counted as things the owner had not gotten round to. At least one of
them -- OP1 -- the owner actively tried to engage with and could not.

That is the honest reading of *"I don't know what you're asking"*: it was never a slow answer. It was
an unanswerable question, and we counted it as an unanswered one.
