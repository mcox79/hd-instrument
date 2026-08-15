# PLAN — THE NEXT 12 HOURS

**LIVING DOCUMENT, dateless filename on purpose.** Edit in place. Written for a session that may
have no memory of the conversation that produced it.

Read `notes/HANDOFF_full_project_report_for_new_team_2026-08-14.md` first if you have no context.
Then this file. Then `notes/RECOVERY_PROGRAM.md`.

---

## THE ONE RULE THAT GOVERNS THIS PLAN (owner instruction, 2026-08-14, verbatim)

> "the way we lose is by trying fancy available tools. The way we win is by understanding exactly
> how the brain does it (which is NOT necessarily a trigram encoder), and replicating it as exactly
> as we can."

**The incident that produced it.** A character-trigram method — comparing words by shared letter
patterns, with no understanding of meaning at all — outscored our system on the grounding readout.
The Director's instinct was "wire spelling in as a channel." **That was the wrong instinct and is
now barred.** The spelling result is a MEASURING-STICK finding: it shows our score can be inflated
without understanding. It is NOT a build direction.

**The test to apply to any proposal:** are we doing this because the brain does this operation, or
because the tool is lying around? If the second, stop.

Corollary recorded the same day: `char_trigram_encoder` exists in `hdlab/` and its registry row
claims WIRED. A runtime import trace (with a passing positive control) proves it is **NOT** on the
live path. That is a **registry error to correct**, not an asset to wire.

---

## WHERE WE ACTUALLY ARE, IN PLAIN LANGUAGE

The system reads text and tries to say what a word means. Its single best guess is right **4.80%**
of the time.

- Random re-pairing of answers ("scramble") scores **0.80%** or **1.375%**, depending on how the
  scramble is built. Both are real floors; the higher one governs.
- "Always guess the commonest word" scores **1.85%**.
- **Spelling alone scores 8.70%.** This is now measured, on the identical items, candidate pool and
  answer key (`data/exp_orthographic_floor_vet_v1/metrics.json`, commit `58a125c88`). The arm is
  literally one matrix multiply over character-trigram vectors with zero input from our substrate,
  and our own arm in the same file reproduces the 4.80% headline exactly, so the harness is proven
  identical. Even the crudest spelling attack, longest-shared-prefix, scores **5.88%** and beats us.

**So we are below the strongest no-understanding floor, and the gap is real** (difference +0.0390,
uncertainty range excludes zero).

**RETIRED FRAMINGS — never re-quote:** "6x its floor" and "5.2pp short of >=10%". Both measured a
criterion that a method with no understanding in it could clear.

### The one thing that actually explains the shortfall

Look at where the right answer lands, not just whether it is picked first:

| | best guess right | right answer somewhere in its top 50 | right first, GIVEN it was in the top 50 |
|---|---|---|---|
| our read-out | 4.80% | 55.65% | **8.6%** |
| spelling alone | 8.70% | 54.55% | **16.0%** |
| shared-prefix | 5.88% | 57.68% | **10.2%** |

**We find the right neighbourhood as well as spelling does. We pick the right member out of it
roughly half as often.** The defect is not retrieval and it is not supply. It is fine discrimination
between things that are already close together.

**Why the system is crowded, mechanically.** It stores a word's meaning as a flat BAG of the other
words that appeared nearby. `sympathetic` and `parasympathetic` occur in nearly identical sentences,
so their bags look nearly identical. Measured on our own anchors: median nearest-neighbour
similarity **0.4637** against a random-null of **0.2264**.

**GROWTH STAYS PAUSED.** Reading more while meanings are mostly wrong just produces more wrong.

---

## WHAT IS NOT IN DOUBT (do not re-litigate; these measured a different claim)

The growth machinery is clean: no-leak violations **0**, scramble ratio **0.077**, persistence
round-trips **bit-identical** and survived a mid-run process death. Spelling overlap does not touch
any of that. What is in doubt is whether the *meanings* are correct — always a separate question.

---

## WHAT CLOSED THIS PAST CYCLE (do not re-run these)

1. **The graded switch is dead on this task.** Turning it on changes the score by **+0.0015**, with
   an uncertainty range of [-0.0055, +0.0083] that spans zero, and that is smaller than the spread
   between random re-draws of the same projection. The **+0.0602** that once justified it is a
   number from a **different scorer**: a two-way forced choice against chance 50% over a 2,377-word
   pool, not open-vocabulary best-guess accuracy over 5,491. A gain on one scorer was carried to
   another where it does not exist. (`39f3fe2a1`; DO-NOT-REDO 34 and 35.) The source cell's own
   result is NOT demoted; only the carry-across is.
2. **The structured-code test produced no readable numbers.** Verdict on disk is
   `VOID_PLUMBING_SELF_RETRIEVAL`. The sanity check — can the encoding recognise a held-out sentence
   about the word it belongs to — passed for the flat-bag arm (**0.7860**) and failed for the
   structured arm (**0.6712**, floor 0.70). **This is not "structure failed". It is "structure was
   not measured."** A diagnosis is in flight; do not pre-empt it. One on-disk observation for
   whoever does: the structured encoder recorded **2.82 features per encoding** on average, which is
   very thin next to a context window, so feature starvation is a live candidate explanation.
3. **The gate that was supposed to catch weak floors was itself grading against the weakest one.**
   `tools/c3_gate.py` only ever looked up scramble-shaped comparisons and never read the
   orthographic or frequency comparisons sitting in the same file. Fixed at `c70b8207c`: it now
   takes the worst (highest) floor a cell recorded. **0 of 22 arms pass.**
4. **One ledger now answers "has anyone tried this".** 968 rows merged into
   `notes/RECOVERY_PROGRAM.md` (`2fbd28ea5`): **974 countable rows, ~696 distinct investigations, 21
   rows corrected against disk, 0 WIRED.** Count over THAT FILE ONLY; running the old
   "over all three files" instruction now double-counts to 1,944.
5. **Two things we had written off are not written off.** DO-NOT-REDO 18 (role-bound structure) and
   DG pattern-separation were both judged by instruments the project has since ruled invalid. They
   are **UNTESTED WITH A WORKING RULER**, not refuted.
6. **Our brain justification for structured codes is weaker than we said.** The perirhinal
   conjunction operation is **UNPINNED** — no measured equation exists for real neurons — and the
   feature-ambiguity account it rests on is **CONTESTED with genuine failed replications** (Clark et
   al. 2011: null in rats at all 14 ambiguity levels, with a working positive control in the same
   animals). Structured codes remain OUR ENGINEERING CHOICE justified by OUR OWN floored results,
   not pinned brain fidelity. Say it that way.
7. **Triage: 7,635 results swept mechanically; 6,292 of 6,578 untriaged remain untouched** at record
   level. The 26% floor-vocabulary drift alarm is still live.

---

## THREE CORRECTIONS FOUND WHILE ASSEMBLING THIS PLAN (verified on disk, new)

- **"Meaning supply is refuted" is too broad, and the half that WAS run points the other way.**
  `data/exp_meaning_supply_separation_v1/metrics.json` records: grounding norms **+0.0232**, an
  encoder **+0.0270**, both together **+0.0460** (which would put us at 0.0940). But crowding —
  how similar near-neighbours are — got **WORSE** in every one of those arms (0.4553 -> 0.4602 /
  0.4668 / 0.4697), while the spelling shortcut made it **BETTER** (0.4553 -> 0.3880). And a pure
  spelling shortcut bolted on the same way gained **+0.0425**, more than either meaning asset alone.
  **More meaning of this kind tightens the neighbourhood instead of separating it.**
- **The encoder in that cell is NOT the 237.7M-token encoder.** Its own metrics file says so:
  `"encoder trained on a SYNTHETIC templated slot harness ... it exposes no word-embedding API, so
  this cell mean-pools its contextual token reps"`, with `USE_IS_OUT_OF_DISTRIBUTION: true`. **The
  big encoder has never been tested on this task.** At least three distinct artifacts in the notes
  are called "the encoder"; before any proposal to wire one, NAME IT and prove it loads.
- **`A5_STRINGCTRL` means two different things in two different cells.** In
  `exp_graded_path_vs_orthographic_floor_v1` it is standalone spelling (0.0870, a floor). In
  `exp_meaning_supply_separation_v1` it is our system PLUS spelling at a weight (a decomposition,
  not a floor). Never compare them. Never quote one for the other.

Also on disk and unverified as a coincidence: the store's failure was independently named a
**k_eff ~= 50** wall, and the read-out's neighbourhood is measured at **top-50**. See step 1-4h.

---

## THE PLAN

Each step states: the question, the artifact, the test that can fail, and what makes us stop.

### 0-1h — CLOSE THE VOID, DO NOT RE-OPEN THE ARGUMENT
- **Question:** why did the structured arm fail to recognise its own held-out sentences when the
  flat-bag arm passed the same check?
- **Artifact:** the in-flight diagnosis, landed as a note, naming a single cause with evidence.
- **Can fail:** the diagnosis finds no single cause, or finds that the sanity check itself is
  mis-specified for a structured encoding. Either is a real answer; write it.
- **Stop if:** the fix would require changing the sanity check's threshold. Moving a positive
  control to accommodate a failing arm is how instruments get bent. Raise it to the owner instead.
- **Note for whoever holds it:** the two arms' checks ran on different sample sizes (299 vs 292).
  That difference is unexplained and is itself a lead.

### 1-4h — MEASURE THE DEFECT DIRECTLY. BUILD NOTHING.
- **Question:** is "the store picks the wrong item from a good shortlist" the SAME defect as "the
  read-out picks the wrong member of a good neighbourhood"? And is either one really a
  fine-discrimination problem, or is there simply no signal in the neighbourhood at all?
- **Why now.** Two independent measurements have the same shape and were never connected:
  - **Store** (`bec359477`, a clean one-variable sweep): retrieves a shortlist containing the right
    item **85-88%** of the time at 1.2M entities, but picks the right single item at most **26.7%**;
    wrong-pick fraction pinned at **0.71-0.77** and **completely insensitive to leaf size** across a
    4-point sweep. The capacity explanation is already falsified. It was named a **k_eff ~= 50**
    discriminability wall.
  - **Read-out** (table above): right answer in the top 50 for **55.65%** of items, picked first for
    **4.80%**.
  Both are "right neighbourhood, wrong member", and both were measured against a candidate set of
  about fifty.
- **Artifact:** ONE number and ONE curve, on the identical items, pool and answer key, for our
  read-out AND every floor: **accuracy as a function of how many candidates it must choose between**
  (k = 2, 5, 10, 20, 50, full pool). This is a re-scoring of similarity scores we have already
  computed, not a new training run. Plus the item-by-item overlap between our correct answers and
  spelling's correct answers.
- **Can fail — and this is the point:**
  - **If the curve is FLAT in k** — if we are about as wrong choosing between 2 candidates as
    between 50, on the same items — then there is no fine-discrimination defect, the neighbourhood
    contains no usable signal, and the unifying hypothesis is DEAD. Supply becomes the lead instead.
  - **If our correct answers and spelling's correct answers are the same items**, then spelling is
    not an independent channel, the 8.70% is partly re-describing our own signal, and the floor
    comparison has to be rebuilt before anything is concluded from it.
  - **If the store's curve and the read-out's curve have different shapes**, they are two defects
    that merely look alike, and treating them as one wastes the next week.
- **A calculation that generated this step, offered as a HYPOTHESIS ONLY — do not cite it as a
  result.** The live near-neighbour two-way score of 0.698 implies a separation strength of about
  0.73. Under that strength, choosing among ~50 candidates predicts 8.5% and among ~108 predicts
  4.8% — that is, spelling's score and our score respectively, from one separation number and a
  count of confusable competitors, with nothing else added. **This is exactly the cross-scorer carry
  that DO-NOT-REDO 35 was written against** (the 0.698 comes from a different cell, a different pool
  and a different scorer), and it assumes a tidy noise model the real data need not obey. It is
  worth precisely one thing: it says what curve to expect, so the measurement above can disagree
  with it. If the measured curve matches, we have one number to move instead of three problems.
- **This step GATES everything after it.**

### 4-8h — MOVE THE ONE NUMBER, USING AN ORGAN WE ALREADY OWN
- **Question:** does an operation whose explicit job is pushing near-identical patterns apart raise
  the separation number measured in 1-4h?
- **Reuse before build.** `hdlab/dg_pattern_separation.py` exists, is OFF the live path, and has a
  floored result on real data: separation **0.942** against a 0.50 bar, effective-rank lift **10x**,
  and off-diagonal mass — which is the crowding measure the meaning assets made worse — dropping
  **0.179 -> 0.012** (`exp_substrate_anisotropy_dg_pattern_separation_prewrite_v1`). It was written
  off in July by instruments since ruled invalid, so it is OPEN, not closed. The registry's
  `pattern_separation` row points at a DIFFERENT module; fix that before relying on either.
- **Artifact:** a pre-registered cell with bands committed BEFORE the run, judged on the curve from
  1-4h, not on aggregate best-guess accuracy.
- **Can fail — full control battery, non-negotiable:** scramble floor; frequency floor; standalone
  spelling floor; a known-answer arm for EACH treatment arm separately; and the spread between
  random projection re-draws (a gain smaller than that spread is not a gain). Paired uncertainty
  ranges on every difference.
- **Stop if:** separation does not move, or it moves while crowding gets worse (that is the
  meaning-supply signature and it means we bought argmax movement, not separation), or the standalone
  spelling floor reproduces the gain.

### 8-11h — ACT ON THE ANSWER (both branches stated, so neither outcome stalls)
- **If separation moves:** wire it **default-OFF** behind a flag, with a verification witness, then
  re-measure end to end and re-run the structured-code test from step 0-1h on top of it — that test
  becomes interpretable only once we can score discrimination separately from retrieval.
- **If it does not:** the flat bag is not merely crowded, it is empty at the resolution we need, and
  the lead becomes supply — at which point run the cheap pre-check in the parallel lane below FIRST,
  because it decides whether supply is even available.

### 11-12h — RECORD
- Update STATE values in `notes/RECOVERY_PROGRAM.md` (FOUND -> VERIFIED -> WIRED / SHELVED /
  REFUTED). Mark what is verified versus what is merely found.
- Narrow DO-NOT-REDO 31 to what was actually tested (norms, plus an out-of-distribution encoder)
  rather than the whole idea of meaning supply.
- Leave the next session a handoff that does not depend on this one's memory.

### RUNNING ALONGSIDE — TWO CHEAP LANES, NEITHER A BUILD DIRECTION

**(i) Name the encoder.** At least three artifacts are called "the encoder" in the notes and the one
cell that appeared to test the big one recorded in its own metrics that it used a different,
out-of-distribution one. Enumerate the checkpoints on disk, load each, and answer one question:
does it expose a per-word representation at all? Then, without touching the reader, measure whether
it separates our own near-synonym anchor pairs. **If it does, supply is not exhausted and the whole
plan re-orders.** If it does not, DO-NOT-REDO 31 can be narrowed honestly and closed.

**(ii) Chip at the triage residue.** 6,292 results have never been read at record level. Continue
the frontier-keyword-first pass. Also fix the two known blind spots: the shape detector cannot see
comparisons whose two arm names are single words (`dense` vs `sparse`), and at least one real result
is stored under a filename that is not `metrics.json`, which every tool in the repo is blind to.

---

## HOW WE MEASURE A CLAIM NOW (these replaced broken rules; each cost us a result)

1. **A gate is a margin above the STRONGEST no-understanding floor, with non-overlapping uncertainty
   ranges — never a bare absolute number.** Strongest means the largest of spelling, frequency and
   scramble, on the identical scorer, sample size, candidate pool and answer key. The old rule
   ("best guess right >= 10% of the time") was cleared by a method with no understanding in it.
2. **A floor must be STANDALONE.** An arm that adds a shortcut ON TOP of the system under test is a
   decomposition, not a floor. This is why the same arm name in two cells means two different
   things, and why one of them must never be quoted as a floor.
3. **A known-answer arm and a floor fail independently, and each treatment arm needs its own.** A
   floor tells you whether the effect is real. A known-answer arm tells you whether the instrument
   is. The structured-code run passed the check on one arm and failed it on the other, and only
   having both per-arm is what stopped a false negative from being written down as "structure lost".
4. **A gain measured on one scorer may not be carried to another.** A two-way forced choice against
   chance 50% over 2,377 words and an open-vocabulary best guess over 5,491 are different tasks. A
   +0.0602 on the first is +0.0015 on the second. If you want the number on the second scorer,
   measure it on the second scorer.
5. **The gate is a function that refuses, not a sentence that gets re-interpreted:**
   `tools/c3_gate.py`, four conditions, and a missing standalone-spelling control returns
   NOT_EVALUABLE rather than PASS. Under it, **0 of 22 arms pass**. Reasoning:
   `notes/c3_gate_hardening_2026-08-14.md`.

---

## FINDING PRIOR WORK (so we stop rediscovering it)

`notes/RECOVERY_PROGRAM.md` is now the single countable ledger: **974 rows, ~696 distinct
investigations, 0 wired.** Count over that file only.

**Search by SHAPE, never by keyword.** Verdict vocabulary went from 13 distinct strings in June to
444 in July; the word "scramble" appears zero times in June while 33 of 60 June cells have a genuine
control arm. Detect a control by its structure — is there a comparison arm — not by its name.

**An absence claim requires an enumeration, not a search.** State HOW you enumerated. Fourteen rows
in one group were reported as having no directory on disk; eleven of them differed only in letter
case.

`tools/result_index_join.py` derives the index from disk, so nothing depends on anyone remembering
to register a result. Its drift alarm currently reads 26%.

**Honest residue:** ~1,180 ledger atoms and 6,292 of 6,578 untriaged results remain untouched, and
**0 of the 968 recovered cells is wired.**

---

## AN OPEN TENSION, RECORDED AND NOT DECIDED

A concurrent session proposes wiring the spelling channel into the system and then demonstrating a
meaning-based margin above 8.70%.

**This is in direct tension with the owner's standing instruction at the top of this file, and with
measurement rule 2.** Once spelling is inside the system under test, the 8.70% is no longer a
standalone floor — it is a component of our own score, and the comparison stops meaning anything.
That is precisely the construction already on disk in `exp_meaning_supply_separation_v1`, where
adding spelling on top gained +0.0425 and taught us nothing about meaning.

**What an honest version would require**, if anyone wants to pursue the underlying question (does
our system carry real meaning signal that the aggregate score is hiding?):

- Do NOT add spelling to our system. Instead, **restrict the ITEMS** to a subset where spelling
  cannot help — where the question word and the right answer share few letters.
- Choose that subset by a rule computed **from the strings alone, registered before running, that
  never looks at any arm's score.**
- Score **every arm on that same subset**, including the standalone spelling floor.
- **Predict in advance that the standalone spelling floor collapses toward the frequency floor on
  that subset.** If it does not, the subset rule failed and the whole test is void.
- Report it **alongside** the full-set number, never instead of it.

That is a difficulty-on restriction of the test set, which is legitimate, rather than a shortcut
bolted onto the system, which is not. It is still ruler work, not a build: it can only reveal a
semantic margin that already exists. **This is written down for the owner to decide, not decided
here.**

---

## STANDING DISCIPLINES THAT APPLY TO EVERY STEP ABOVE

- **No demotion without a fresh on-disk re-check.** ~11 old results were wrongly demoted by later
  audits; 17 corrections-of-a-correction in 48 hours.
- **Runtime evidence beats static search.** Imports inside function bodies are invisible to grep;
  string constants and comments produce false hits. Import the code and observe.
- **Verify the claim, not the summary.** Three claims in the brief that produced this plan changed
  when read off disk. Open the metrics file.
- **A negative about someone else's landed result is itself a claim** and gets the same scrutiny as
  one of your own positives.
- **Word limits belong on the report, never on the work.**
