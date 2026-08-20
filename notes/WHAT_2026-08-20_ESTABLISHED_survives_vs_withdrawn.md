# WHAT 2026-08-20 ESTABLISHED -- A SINGLE LEDGER OF WHAT SURVIVES AND WHAT I WITHDREW

**Why this file exists.** Today produced eleven findings and **six retractions of my own claims**,
several of them corrections *of corrections*. The plan, STATUS and four notes now carry those layers
in the order they happened, which is the right way to keep a record and **the wrong way to read
one.** This is the flat version. **Where this file and an older note disagree, this file is later.**

---

## ✅ SURVIVES -- with the evidence, and with its scope stated

### 1. The definitional-PHRASE half of the output is the good half
**32% MEANINGFUL vs the distributional read-out's 4%**, hand-scored, **PAIRED on identical terms and
identical accumulated traces** (McNemar 8-for / 1-against, exact one-sided **p = 0.020**, n=25
informative pairs of 61). An earlier unpaired version (32% vs 0%, Fisher p=0.002) was **confounded**
-- the arms drew different words -- and the pairing removed that by construction. *Scope: one
corpus, one seed, scored by me.*

### 2. The win is the phrase **FORM**, not the definitional **SOURCE**
100 pre-registered rows scored **blind** (arm not inferable; prediction recorded before the key was
opened; items predate the mechanism by 8 days). **Definitional-HEAD 4% vs distributional 0%,
p = 0.2475 -- NOT DISTINGUISHABLE.** Only **3 of ~75** single-word objects scored MEANINGFUL all day
(`soccer -> football`, `drosophila -> fly`, `piraeus -> port`), all the same special case.
**`substrate.py:538` (`d.head` -> `d.definiens`) looks like an implementation detail and carries the
entire measured gain.** Two landed cells were unblocked by this audit.

### 3. A machine scorer for phrase output exists, and phrase output clears every floor on it
Hit = the phrase **CONTAINS a ConceptNet-attested hypernym**. `tools/score_phrase_output_against_
conceptnet_hypernyms.py`.

| 4 seeds | OURS | strongest length-matched floor |
|---|---|---|
| 7 / 101 / 13 / 29 | **19.4 / 18.9 / 20.3 / 21.3%** | 7.5 / 7.4 / 8.2 / 7.7% |

`CO_SPAN` (contiguous same-length window from the same sentence) **4.4%**, overlapping our words only
12.8% so it is not contaminated. `SHUFFLE` pooled **0.6%**. **`ORACLE` positive control = 100%**, and
a standalone matcher check fires **400/400** at **0.2%** false-fire. **Every floor is
LENGTH-MATCHED**, because a longer phrase mechanically gets more chances to contain a hypernym.

### 4. That percentage is a LOWER BOUND on a deliberately crippled yardstick -- never an accuracy
The gold **drops 218,061 WordNet-provenance edges** (that omission IS its admissibility), so the
taxonomic backbone goes too: **`dog IsA animal` is NOT in this gold.** A further **52.8% of gold
objects are multi-word** and unmatchable. **A correct definition routinely MISSES** -- `piraeus ->
"a port"` is right and scores zero. **Quotable only as "beats the strongest floor".** The
hand-score's 32% is the better quality estimate.

### 5. **Nothing in the read path consumes meaning** -- enumerated, not inferred
Four read routes (`query`, `recall`, `recall_cortical`, `recall_sentence`). `recall`/`recall_sentence`
rank by episodic active-unit overlap. **`build_cortical_index` iterates the consolidated TERMS and
builds each vector from `context_profiles` -- the meaning value is never vectorised, never compared,
never read**; it is attached to the hit for DISPLAY after ranking. `query`'s ACCEPT/CLARIFY/REFUSE
keys on whether a meaning **exists**, not what it says. **Every read of a `GROUNDED_MEANING` object's
content in `hdlab/` is a SELF-TEST ASSERTION.**
**SCOPE COMPLETED (the enumeration now covers the whole repo, not just `hdlab/`):** outside `hdlab/`
exactly **three** files call `consolidated()` -- `exp_cortical_read_consolidated_v1.py` (passes it to
`build_cortical_index`, **keys only**), `exp_predictive_write_gate_v1.py:212` (`for term in cons`,
**keys only**), and `tools/diag_top_anchors_after_the_light_noun_fix.py`, which reads the VALUES but
is a diagnostic that COUNTS which anchors get assigned -- it measures them, it does not consume them.
**So: no read or retrieval path anywhere in the repository consumes the meaning content. The only
value-readers are self-test assertions and one counter.**
**➡️ This mechanically explains the standing inertness finding** (consolidation ablates to zero
effect). **It is a missing piece, not a bug.**

### 6. Making the read consume the meaning: THREE variants tried, none pays
- **DOWNGRADED BY MY OWN NEW GATE, THEN RESTORED BY RUNNING THE SEEDS.** *"Index BY the raw
  definiens text is 28 ranks worse"* was **seed 7 only**, and `tools/replication_gate.py` --
  pointed at this very ledger's SURVIVES list within the hour of being written -- returned
  **`SINGLE_SEED_HYPOTHESIS`** for it. **I had filed it under SURVIVES.** *A guard I exempt my own
  favourites from is not a guard.* **Seeds 101 and 13 were then run, and it holds:**

  | DEFINIENS - PROFILE | seed 7 | seed 101 | seed 13 | gate |
  |---|---|---|---|---|
  | (positive = WORSE) | **+28.0** | **+19.5** | **+28.5** | **`REPLICATED`** (3/3 same sign, 1.5x) |

  Leak-controlled (**3,269** cue sentences excluded on seed 7). `SHUFFLE_DEF` is worse than
  `DEFINIENS` on all three seeds (+7.0 / +31.0 / +19.0), so the definiens IS term-specific -- just
  worse than the profile.
- **🔎 AND A THIRD INDEPENDENT SIGN-FLIP ON THE COMBINING QUESTION.** `BOTH - PROFILE` reads
  **+7.0 / -8.0 / +6.5** -- gate verdict **`INCONSISTENT_SIGN`**. **That is now three separate
  datasets showing combining behaves inconsistently across seeds**, and it independently confirms
  the ledger's position that NEITHER of my two opposing boundary claims was ever established.
- **Index by the LOOKED-UP definition (mean of the profiles of the words it names): worse on all
  three seeds** (+12.5 / +16.0 / +26.0).
- **Blend it with the profile: WITHDRAWN as an artifact** (see below).

### 7. The definitions DO carry term-specific signal -- just not enough of it
`SHUFFLE_LOOKUP` is far worse than `DEF_LOOKUP` on **all three seeds** (106/67, 104/69, 113/83). So
they are not noise; **the binding constraint is VOLUME** -- ~7 words against a profile summed over
dozens of encounters.

### 8. Co-occurrence counting crushes every arm, on every task built today
**COOC 5.0 / 3.0 / 4.0** against a best arm of 38-57. **Nothing measured today touches the standing
headline.**

### 8b. A live docstring was describing a different wire than the one running
`reading_grounding_loop.py:1451` (`_make_definitional_gate`) carried three claims that had moved.
**Corrected in place, comment-only, with the original kept verbatim as the design rationale:**
1. *"it is NOT on the live reading path"* -- **no longer true**; `substrate.py:538` passes
   `definition_map` in, and 212 of 402 provenance rows carry the definitional label.
2. **What ships is NOT what the paragraph describes.** It says `Definition.term -> Definition.head`
   (a single head noun); `substrate.py:538` stores `d.definiens` (the full phrase). **Measured the
   same day: phrase 32% MEANINGFUL vs head 4%, and the head form is NOT distinguishable from the
   distributional control (p = 0.2475).**
3. **The 64% does not state which population it measures.** Per the charter it is the EXTRACTOR's
   own output after the v5 term-boundary fix -- *"is the extracted definition right for that
   sentence"* -- **not** a score of the grounding facts the gate banks, which is what the wire's
   value depends on. **The docstring now carries the standing prohibition explicitly**, so the next
   reader does not line it up against the 4% the way I nearly did.

### 9-11. Infrastructure and governance, all verified from disk
- **The registry's do-not-wire gate on the definitional module had been CARRIED PAST** while
  `pipeline_status` read `WIRED_BUT_NOT_PIPELINE_REACHABLE` -- wrong in the safe-looking direction.
  Corrected on **runtime** evidence (212 of 402 provenance rows carry the definitional label).
- **The compaction-recovery path was broken:** STATUS's machine-parsed `## WHAT IS RUNNING` sat under
  2,300 lines of archive, so **every recovery for a day was injected with state naming two runs as
  in-flight that had finished the previous afternoon.** `## POSITION` was terminated at its own first
  line. Both fixed; nothing deleted.
- **Two completed runs had never been recorded:** the 9-seed spoke sweep (**pre-registered
  conjunction FAILS** -- 3 of 9 seeds under the ratio bar; but ratio mean 0.87 / median 0.91, so
  **borderline-at-independence, NOT refuted**) and `exp_predictive_write_gate_v1` (**ACC hit@10
  0.1533 vs COOC 0.3667**).

---

## ⛔ WITHDRAWN -- six of my own claims, in the order I made them

| # | what I claimed | why it is wrong |
|---|---|---|
| 1 | *"SHUFFLE is 0.0% on every seed"* (said twice) | **Seed 29 reads 2.6%.** Pooled 4/621 = 0.6%. Still a real floor, still cleared -- but "zero everywhere" was false. |
| 2 | *"The cortical read has NO callers -- it is islanded"* | **False.** Two Grep calls returned two different INCOMPLETE answers; shell `grep -rn` found the real caller at `substrate.py:1037` plus an experiment. **I nearly filed this.** |
| 3 | *"Combining helps only when channels are comparably strong; a weaker one DILUTES"* | Built on ONE run. |
| 4 | *"...REFUTED; the condition is INDEPENDENCE, not comparable strength"* | Built on the seed-7 artifact below, so **also void.** **NEITHER boundary is established.** *The owner's original 3-seed "combining channels helps" result is untouched; what is withdrawn is MY attempt to say WHEN.* |
| 5 | *"Looking up the definition alongside the profile gains 16 ranks"* | **ARTIFACT.** `BOTH - PROFILE` = **-16.0 / -1.0 / -5.0** across seeds, and on **two of three** an information-free blend matched or beat it -- **a RANDOM VECTOR beat the right definition on seed 101**, the WRONG definition tied it on seed 13. |
| 6 | *"PINNED BY EVIDENCE: schema-congruent items consolidate rapidly"* | **`ORGAN_MAP.md` §G1 says lexical-semantic acquisition is "UNPINNED, deliberately"** and the strong "fast mapping writes directly to cortex" account **"collapsed under replication"** (Warren & Duff 2014; Cooper, Greve & Henson 2019). **Presenting an invention as brain-derived is the barred move -- the same fault already on record for VSA binding.** |

**Also failed: a pre-committed prediction.** I predicted `DEF_LOOKUP` would beat `PROFILE` at LOW
exposure and not HIGH. **It beat it at neither.** Recorded because a prediction reinterpreted after
the fact did not succeed.

---

## 🔁 THE PATTERN WORTH KEEPING, BECAUSE IT REPEATED FOUR TIMES

**Every withdrawal above followed the same shape: a single run produced a clean-looking number and I
led with it.** The rule that names this -- *a single-seed win is a HYPOTHESIS* -- was written in my
own limits section **before** the disconfirming seed ran, in the very note whose headline I then had
to retract.

**What actually caught them was never judgement; it was a control built BEFORE the result existed:**
- `BOTH_NOISE` / `BOTH_SHUFFLE` were added because *a blend beating its own component is where an
  artifact hides*. They fired automatically.
- `ORACLE` was added because *a 0.0% floor is only evidence once the scorer is shown to return
  non-zero*.
- The leak control excluded **3,269** sentences and **printed the count**.

**➡️ THE OPERATIONAL LESSON: WRITE THE CONTROL INTO THE SCRIPT, NOT THE CAUTION INTO THE PROSE.**
Every caution I wrote as prose today, I then violated. Every control I wrote as code, caught me.

### ✅ SO THE LESSON WAS MOVED INTO CODE: `tools/replication_gate.py`

Same escalation the tie rule got (written down in the morning, violated twice by evening, moved into
`rank_with_ties.py`). `replication_verdict(effects, controls=..., lower_is_better=...)` returns
`SINGLE_SEED_HYPOTHESIS` / `ARTIFACT_CONTROL_MATCHES` / `INCONSISTENT_SIGN` / `UNSTABLE_MAGNITUDE` /
`REPLICATED`. **There is no call signature that returns a pass from one seed**, and `controls=` makes
it check whether an information-free arm reproduced **half** the effect on any seed.

**Checked both ways on today's own real data, which is the only test that matters:**

| the day's two candidate results, judged by the new gate | verdict |
|---|---|
| the withdrawn blend (-16.0 / -1.0 / -5.0, controls run) | **`ARTIFACT_CONTROL_MATCHES`** |
| the phrase-floor result (4 seeds, +11.9 / +11.5 / +12.1 / +13.6) | **`REPLICATED`** -- 4/4 same sign, 1.2x spread, no control within half |

**It discriminates rather than flagging everything** -- which is the failure mode that gets a guard
ignored, and is why its self-test includes a genuine effect that must PASS. **It says REPRODUCIBLE,
never GOOD:** the floor/CI bar still applies on top. Recorded in `CLAUDE.md` beside the tie rule.

---

## TLDR

Today the system's output got a proper examination for the first time, and the honest scoreboard is
**mixed, with more corrections than findings.**

**The good news, and it held up to everything I threw at it:** half of what this system learns is a
full descriptive phrase, that half had never been checked, and it is **eight times better** than the
half we had been measuring. The reason turns out to be simple -- **a single word almost cannot
explain a word**, no matter how well chosen. That was worth finding.

**The bad news:** nothing in the system actually reads those definitions to answer anything. I tried
three ways to change that. One made things clearly worse, one made no difference, and one looked
like a 30% improvement until a second run showed a *random vector* doing the same job.

**And the honest part:** I had to withdraw six of my own claims today, including a correction I made
to an earlier correction. The pattern was always the same -- one good-looking run, reported too
early. The safeguards that caught me were the ones I had written into the code beforehand, never the
warnings I had written into the text.

Plain word-counting still beats everything we compute, by roughly ten to one. That has not moved.

## QUESTIONS

None. Q89 remains the only open decision and nothing today changes what it asks.

## NEXT STEPS

1. **Do not try a fourth variant of "make the definitions help retrieval."** Three tried, one
   artifact; the route is not paying.
2. **The phrase-quality result is solid and unexploited.** Its value is as a KNOWLEDGE ARTEFACT, not
   as a read-out improvement -- which is a point for whichever branch of Q89 the owner picks.
3. **Extractor recall stays paused** until something can use the material.
