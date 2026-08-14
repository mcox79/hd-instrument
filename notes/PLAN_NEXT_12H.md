# PLAN — THE NEXT 12 HOURS

**LIVING DOCUMENT, dateless filename on purpose.** Edit in place. Written 2026-08-14 by the
Director session, for a session that may have no memory of the conversation that produced it.

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

The system reads text and tries to say what a word means. It gets it right **4.80%** of the time.

- Random re-pairing of answers scores **0.80%**.
- "Always guess the commonest word" scores **1.85%**. We beat that, and the ranges do not overlap.
- **Spelling-alone has NEVER been measured.** The arm previously described as a "spelling control"
  is actually *our score plus spelling*, not spelling by itself. So the claim "we underperform a
  spell-checker" is **NOT established**. Do not repeat it.

**Why the score is untrustworthy either way:** at the declared setting, bolting pure spelling onto
our system gains **+4.25 points** while our trained encoder gains only **+2.70**. About half of what
this number can move is reachable with no understanding. The ruler is bent.

**Why the system fails, mechanically.** It stores a word's meaning as a flat BAG of the other words
that appeared nearby. `sympathetic` and `parasympathetic` occur in nearly identical sentences, so
their bags look nearly identical, so it cannot tell them apart. Measured on our own anchors: median
nearest-neighbour similarity **0.4637** against a random-null of **0.2264** — the crowding is real
and it is semantic.

**GROWTH STAYS PAUSED.** Reading more while meanings are mostly wrong just produces more wrong.

---

## WHAT IS NOT IN DOUBT (do not re-litigate; these measured a different claim)

The growth machinery is clean: no-leak violations **0**, scramble ratio **0.077**, persistence
round-trips **bit-identical** and survived a mid-run process death. Spelling overlap does not touch
any of that. What is in doubt is whether the *meanings* are correct — always a separate question.

---

## THE PLAN

Each step states: the question, the artifact, the test that can fail, and what makes us stop.

### 0-1h — COMPACTION SAFETY
- **Question:** can a session with no memory recover and continue?
- **Artifact:** this file on disk; `notes/STATUS.md` under its 8192-byte cap with a one-line stub
  pointing here; the session-start hook verified BY EXECUTION, not by eyeball.
- **Can fail:** the hook prints `(no AS OF line found)` or `(no WHAT IS RUNNING section found)`.
  Both literals — `AS OF:` with the colon, and the heading `## WHAT IS RUNNING` — are an API
  consumed by `tools/session_start_hook.py`. **Never reword them.**
- **Stop if:** STATUS.md cannot fit the stub by sanctioned eviction. It is at structural cap
  pressure (62 never-trim items occupy ~3,600 bytes against a 2,400 allocation; byte-shaving is
  exhausted). Propose a measured cap raise rather than deleting never-trim material.

### 1-4h — DRILL THE BRAIN MECHANISM. BUILD NOTHING.
- **Question:** exactly how does the brain (a) keep "the artery carries blood" distinct from "blood
  carries the artery" — role binding — and (b) keep two near-identical concepts apart —
  within-neighbourhood separation?
- **Artifact:** a drill note giving, per element, the actual mathematical operation with citation,
  plus SHAPE / POSITION / METRIC, and our gap against each.
- **Can fail:** the literature does not pin the operation. Write **UNPINNED** and say so — that is a
  finding about neuroscience, not a hole to fill with a plausible guess.
- **Reuse before build:** for every mechanism ask which brain structure performs it and whether we
  already own an organ that does that process. The brain reuses circuits; a parallel build is both
  unfaithful and creates an island.
- **This step GATES everything after it.** Do not skip to 4-8h because the answer seems obvious.

### 4-8h — TEST STRUCTURE AGAINST THE BAG, ON THE LIVE SYSTEM
- **Question:** does structured storage — keeping track of which role each part plays — beat the
  flat bag on our real task?
- **Why this and not something else:** three independent, floored, previously-unconnected results
  already say it does, and none was ever connected to the live reader:
  - role-filler factored **1.000** vs flat **0.003**
  - conjunctive/orthogonal **1.000** vs additive **0.273**
  - permutation binding **1.000** vs the scheme we actually use **0.063**
  Sources: `notes/recovery_ledger_reading_tier_2026-08-14.md`,
  `notes/recovery_ledger_chaingraded_tier_2026-08-14.md`.
- **Artifact:** a pre-registered cell with bands committed BEFORE the run.
- **Can fail — full control battery, non-negotiable:** scramble floor; frequency floor; the
  no-understanding string baseline; and a **between-random-draw spread** (a gain smaller than the
  variation between random projection draws is not a gain). Paired bootstrap CIs on deltas.
- **Stop if:** the gain does not exceed the between-draw spread, or the string baseline reproduces
  it. Both have happened this week; neither was caught by intuition.

### 8-11h — ACT ON THE ANSWER (both branches stated, so neither outcome stalls)
- **If structure wins:** wire it **default-OFF** behind a flag, with a verification witness, then
  re-measure end to end. Turning the default on is a separate decision after a verdict.
- **If it does not:** the 1-4h drill names what the brain does that we still do not. That becomes
  the next build. A negative here is a real result — it closes the best-evidenced remaining lead.

### 11-12h — RECORD
- Update STATE values in the ledgers (FOUND -> VERIFIED -> WIRED / SHELVED / REFUTED).
- Mark what is verified versus what is merely found.
- Leave the next session a handoff that does not depend on this one's memory.

### RUNNING ALONGSIDE — RULER REPAIR ONLY
Measure what **spelling alone** actually scores. Draft exists at
`scratch/ortho_floor_vet_trigram_only.py` (~10 minutes, candidate pool identical by construction).
**This fixes the measuring stick. It is NOT a build direction.** Until it runs, the strongest
no-understanding baseline is UNMEASURED and no floor claim is settled.

---

## HOW WE MEASURE A CLAIM NOW (this replaced a broken rule)

A gate is a **CI-separated margin above the strongest baseline that involves no understanding** —
`max(orthographic, frequency, scramble)` on the identical scorer, n and candidate pool. **Never a
bare absolute number.** The old rule ("hit@1 >= 10%") was clearable by a method with no
understanding in it, which is how we learned this.

The gate is now a function that refuses: `tools/c3_gate.py`, four conditions, and a **missing string
control returns NOT_EVALUABLE rather than PASS**. Under it, **0 of 13 arms pass** — including the
gate's own cell, which is simply unmeasured on three of the four conditions. Full reasoning:
`notes/c3_gate_hardening_2026-08-14.md`.

---

## FINDING PRIOR WORK (so we stop rediscovering it)

968 experiments now carry a one-line status each:
`notes/recovery_ledger_chaingraded_tier_2026-08-14.md` (565) and
`notes/recovery_ledger_reading_tier_2026-08-14.md` (403). **Both still need merging into
`notes/RECOVERY_PROGRAM.md`** — until then, any count must run over all three files.

**Search by SHAPE, never by keyword.** Verdict vocabulary went from 13 distinct strings in June to
444 in July; the word "scramble" appears **zero** times in June while 33 of 60 June cells have a
genuine control arm. A keyword filter found 11 controlled experiments in one tier and **missed 161**.
Detect a control by its structure — is there a comparison arm — not by its name.

`tools/result_index_join.py` derives the index from disk, so nothing depends on anyone remembering
to register a result. Its drift alarm fires when shape and vocabulary disagree; it is currently at
26%.

**Honest residue:** ~1,180 ledger atoms and ~7,660 metrics files remain untriaged, and **0 of the
968 are wired**.

---

## STANDING DISCIPLINES THAT APPLY TO EVERY STEP ABOVE

- **No demotion without a fresh on-disk re-check.** ~11 old results were wrongly demoted by later
  audits; 17 corrections-of-a-correction in 48 hours.
- **An absence claim requires an enumeration, not a search.** Name-searching is what hid everything.
- **Runtime evidence beats static search.** Imports inside function bodies are invisible to grep;
  string constants and comments produce false hits. Import the code and observe.
- **A known-answer arm and a floor fail independently.** A floor tells you whether the effect is
  real; a known-answer arm tells you whether the *instrument* is. Two cells were saved by one this
  week — including an estimator that returned a confident interval that **excluded the truth**.
- **Word limits belong on the report, never on the work.**
