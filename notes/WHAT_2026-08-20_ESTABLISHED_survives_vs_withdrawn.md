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

### 8c. Swept for more of the same: CLEAN, and the clean result is deliberately not over-read
Having found one live docstring describing a dead route, I checked whether others do
(`scratch/audit_docstrings_vs_live_closure.py`): read with the substrate, snapshot `sys.modules`
for `hdlab.*` -- **that IS the live closure, and CLAUDE.md says it is knowable no other way** --
then scan each live module's docstring region for a claim of its own unreachability.

**Result: NO live module falsely claims to be unreachable.** Two flags, both FALSE POSITIVES on
inspection and reported rather than quietly dropped: `consequence_learning_loop` says *"never
imported here"* about OTHER mechanisms it declines to import, and `substrate` QUOTES the 2026-08-13
accounting finding as background. *Opt-in levers ("default OFF", "NOT wired into `<fn>`'s
precedence") are deliberately excluded -- there are dozens, they are legitimate design statements,
and flagging them would bury the real cases.*

**⚠️ THE CLEAN RESULT IS WEAK EVIDENCE AND THE SCOPE WAS WRITTEN BEFORE THE RUN:** today's actual
defect was in a **FUNCTION** docstring inside a module that never claimed unreachability, so this
scan **structurally could not have caught it**. It also cannot check the *other* half of that defect
-- whether a docstring describes the arm that actually ships -- which is not machine-checkable.

### 8d. RECONCILED: "35 of 141 modules are live" is a LOWER BOUND FROM ONE PROBE, not a census
I flagged a possible discrepancy (my trace read 45-46, the standing figure is 35) and said it needed
the original method before it meant anything. **It did, and the answer is better than either
reading.**

- **The original method REPRODUCES EXACTLY today** -- eager-import trace of
  `reading_grounding_loop` + `grounding_acquisition_loop` gives **40 entries / 32 top-level**,
  identical to 2026-08-13. **The 35 figure is NOT stale.**
- **But a probe that actually RUNS the substrate loads 6 modules the import trace never sees:**
  `corpus_registry, cortical_recall, definitional_extraction, hippocampal_encoder,
  information_foraging, substrate`.
- **And my running probe MISSES all three lazy modules the 2026-08-13 note added BY HAND**
  (`pos_tagger`, `arc_parser`, `arc_labeler`) -- they load on a path it never exercised.

**➡️ NEITHER PROBE IS COMPLETE. EVERY PUBLISHED LIVE-CLOSURE COUNT IS A LOWER BOUND FROM ONE
PROBE, AND THE UNION IS LARGER THAN EITHER.**

**AND THIS IS THE ROOT CAUSE OF 8b.** `_make_definitional_gate` said *"it is NOT on the live reading
path"* and cited this accounting. **It was faithfully quoting a method that structurally cannot see
a lazily-imported module** -- and `definitional_extraction` is responsible for **212 of 402** banked
facts. **The two organs the standard trace misses -- `definitional_extraction` and `cortical_recall`
-- are the two that today's entire investigation is about.** The docstring was not careless; the
instrument was blind in exactly the place that mattered. *Corrected in CLAUDE.md's evidence-
discipline section, which quotes the 35 as the scope of every capability claim.*

### 8e. TEN LANDED CELLS ARE STILL BLOCKED ON HUMAN SCORES NOBODY DID -- now a list, not a lucky grep
I found two of these BY ACCIDENT today, and each was **the only missing input to a landed verdict**,
and each **answered a question the project was still treating as open**:

- `exp_definitional_grounding_v3` (8 days) -> the definitional HEAD route is NOT distinguishable
  from the distributional control.
- `exp_structured_comparator_v1` (7 days) -> the structured comparator is **significantly WORSE**
  than the bag-of-words it was built to replace.

**Finding the second one by accident is the signal that this should be enumerated.**
`tools/find_pending_handscores.py` walks `data/*/metrics.json` FROM DISK (never an index), and
reports cells whose verdict names a pending human score, which sample artefacts exist, and whether
anything score-shaped sits beside them. **It never opens an `arm_key*` file** -- reading a key
before its sample is scored destroys the blinding as thoroughly as editing it.

**RESULT: 10 cells still unscored** (`called_boundary_v7_smoke`, `definitional_grounding_v4`,
`_v5`, `definitional_predicate_v6/_v61/_v62`, `grounding_quality_readout_v1_smoke`,
`grounding_text_vs_mechanism`, `reading_grounding_loop_cycle3_groundingfix_v1`,
`structured_comparator_v1_smoke`). **Each is a landed cell whose question may already be answerable
from data sitting on disk.**

**AND THE COMPLETED ONES ARE NOW DISCOVERABLE.** Both scores I did today are written beside their
evidence as `_handscore_verdict_2026-08-20.json` -- **additive; the landed `metrics.json` is NOT
rewritten**, per the standing discipline -- and the tool recognises that filename, so the worklist
shrinks as work is done instead of rotting. *Verified: both moved out of the worklist on re-run.*

> **⚠️ ONE UNRESOLVED WRINKLE, SURFACED RATHER THAN DECIDED.** `.gitignore:53` is `data/*/**`, so
> those verdict files are **LOCAL-ONLY**. Specific audit artefacts (`metrics.json`,
> `blind_sample.json`, `arm_key.json`, `b3_audit_sample_*`) are tracked by exception -- but the
> existing completed score, `_joined_verdicts.json`, is **also untracked**, so the precedent for
> verdicts is local-only. **CONSEQUENCE: on a fresh clone the worklist reads 12 again, because the
> evidence that two are done does not travel.** *The durable record is in `notes/`, which is
> tracked, so nothing is lost -- but the TOOL's shrink-as-you-go property is local.* **Making them
> travel is a one-line `.gitignore` exception, and changing a deliberate repo policy is the owner's
> call, not one to take unilaterally at 3am inside an autoloop.**

### 8f. THIRD PENDING AUDIT SCORED, AND THIS ONE IS **POSITIVE**: 96% EXTRACTION PRECISION
`exp_definitional_predicate_v62` -- *"keep the predicate the definitional extractor discards"*, i.e.
for *"X is a process in which Y is broken down"*, keep the **doing** as well as the genus. Pending
since 2026-08-13.

**48 of 50 extracted triples are faithful to their source sentence -- 96%.** Against the cell's
recorded v6.1 prior of **40/2/8**, its four defect fixes moved precision from roughly 80% to 96%.

**BOTH failures are the SAME SHAPE -- the wrong verb pulled out of a complex clause:**
`(cellular respiration, PROCESS_PATIENT, energy)` where the sentence is *"the process of making ATP
using the chemical energy"* (the patient of MAKING is ATP); and `(neurotransmitter release,
ENABLING_CONDITION, alter)` where the sentence is *"occurs when an action potential TRAVELS...
resulting in ALTERED permeability"* (the when-clause event is TRAVELS). **Not random noise -- a
named, fixable class.**

**🚫 SCOPE, AND IT IS SEVERE ENOUGH THAT THE HEADLINE MUST NOT TRAVEL WITHOUT IT:**
1. **SINGLE ARM. No control, no floor.** A precision figure, **not** a floor-cleared comparison; it
   cannot clear this project's measurement bar and must never be quoted as though it had.
2. **IT SCORES FIDELITY-TO-SENTENCE, NOT TRUTH.** Row 30, `(nitrification, PROCESS_PATIENT,
   nitrite)`, is faithful to a source sentence that is itself **chemically backwards** -- and I
   scored it CORRECT, because the question is whether we read the sentence right. **Extraction
   accuracy is not knowledge accuracy.**
3. **THE CORPUS IS DENSE EXPOSITORY BIOLOGY -- measured today as the EASY case** (dense expository
   text grounds 3.4x better than ordinary prose, Fisher p=0.002). **96% here does NOT transfer to
   simplewiki**, which is where every other number in this ledger was measured.
4. Single scorer, n=50.

**➡️ CONSISTENT WITH THE DAY'S STORY RATHER THAN AGAINST IT: the READING is accurate; the
GROUNDING READ-OUT is not.** We are good at extracting what a page says and bad at deciding what a
word means from statistics. **Worklist now 9.**

### 8g. FOURTH AUDIT SCORED -- **BETTER TEXT DOES NOT RESCUE THE READ-OUT** (`grounding_text_vs_mechanism`)
The cell asks the question Q89 turns on: **is grounding limited by the TEXT we feed it, or by the
MECHANISM?** Arms are NEWS vs TEXTBOOK read streams, with a SEALED co-occurrence control. Its own
prereg names `MECHANISM_IS_BINDING` an expected, acceptable outcome.

| n=50 per arm | MEANINGFUL | RELATED | NOISE |
|---|---|---|---|
| NEWS | **0%** | 24% | 76% |
| TEXTBOOK | **0%** | 36% | 64% |

**NEITHER ARM PRODUCED A SINGLE MEANINGFUL GROUNDING.** Textbook is directionally better on RELATED
and NOISE (Fisher one-sided p=0.1376 on NOISE) -- **underpowered, not null** -- but **the
discriminating cell is empty, so switching from news to textbook does not rescue the read-out.**

**🔓 AND THE SEALED CO-OCCURRENCE CONTROL IS THE SHARPEST PART:**

| arm | either_top1 (floor) | top5 containment (floor) | band |
|---|---|---|---|
| NEWS | 0.12 (0.02) | 0.44 (0.04) | **COOC_PARTIAL** |
| TEXTBOOK | 0.04 (0.00) | 0.20 (0.02) | **COOC_DOES_NOT_EXPLAIN** |

**On TEXTBOOK the substrate DEPARTS from plain co-occurrence far more than on NEWS -- and still
produced ZERO meaningful groundings.**
**➡️ DIVERGENCE FROM THE BASELINE IS NOT QUALITY.** *Exactly the shape of the structured comparator
scored hours earlier: it could not reproduce a known baseline error, and was still worse. Two
independent cells, same lesson -- **"not doing what the baseline does" is not evidence of doing
better**, and this project has repeatedly read it as though it were.*

**⚠️ TENSION TO RECORD, NOT RESOLVE:** the charter carries a different text-kind result (`bio_new`
9/17 = 52.9% MEANINGFUL vs 13/83 = 15.7% elsewhere, p=0.00204). That is a WITHIN-read segment
comparison on another cell; this is a BETWEEN-stream comparison with 0 MEANINGFUL in both arms.
**Do not merge them** -- different populations and samples, and the standing prohibition on
juxtaposing hand-score figures applies.
**⚠️ BLINDING LIMIT:** this design *cannot* be fully blind -- the arms differ BY CORPUS, so the
vocabulary reveals the arm (`spermatogonia`/`operon` are obviously textbook). Mitigated by scoring
from the (subject -> object) PAIRS ALONE with sentences withheld. **Worklist now 8.**

### 8h. 🟢 **THE BEST RESULT OF THE NIGHT, AND IT NAMES A SPECIFIC PATTERN: `GLOSSARY_COLON` IS 92% MEANINGFUL**
`exp_definitional_grounding_v5` (term-boundary repair), pending since 2026-08-12. Scored on the
**same field, same rubric, same scorer, same night** as the v3 sample:

| | MEANINGFUL | RELATED | NOISE |
|---|---|---|---|
| **v3 DEF** (scored earlier tonight) | **4%** (2/50) | 50% | 46% |
| **v5 DEF_V5_TERM_BOUNDARY** | **60%** (30/50) | 20% | 20% |

**A 15x difference, by one scorer in one sitting, on the same `subject -> object` field.**

**BY EXTRACTION PATTERN -- this is the actionable part:**

| pattern | n | MEANINGFUL |
|---|---|---|
| **`GLOSSARY_COLON`** (*"ecology: the study of..."*) | 13 | **12 = 92%, ZERO noise** |
| `COPULA` | 12 | 50% |
| `APPOSITIVE` | 15 | 47% |
| `CALLED` | 9 | 44% |

**CONFOUND CHECKED AND REJECTED: it is NOT a corpus difference.** Segment mixes are near-identical
(v3 `bio_new` 33 / `adv_new` 8; v5 `bio_new` 30 / `adv_new` 8).
**MECHANISM:** the pattern mix shifted (`GLOSSARY_COLON` 2 -> 13, `CALLED` 19 -> 9), **but that
alone cannot explain the gap** -- if v3's patterns ran at their v5 rates (~44-50%) v3 would have
scored ~45%, not 4%. **The dominant cause is the TERM-BOUNDARY corruption v5 repaired (16.1% ->
1.0%): in v3 the patterns fired correctly on WRONG SPANS, which is exactly how you get
`afghanistan -> catch`.**

**⚠️ UNRECONCILED, FLAGGED NOT MERGED:** the cell cites baselines of *v3 DEF 38%* and *v4 DEF 40%*,
and the charter attributes *64%* to this v5 fix -- while my v3 score of the OBJECT field is 4%.
**The likely explanation is that the historical scores judged the DEFINIENS SURFACE (the full
extracted phrase) rather than the banked head object** -- the same which-population ambiguity
flagged tonight in `reading_grounding_loop.py:1451`. **The standing prohibition on juxtaposing
hand-score figures applies; I am not merging them.**

**➡️ STRONG EVIDENCE FOR THE PIPELINE BRANCH OF Q89** -- but see the immediate retraction below
before treating "glossary lines" as the target. *Limits: single arm, no floor, n=50, one scorer,
dense-expository corpus (the easy case).* **Worklist now 7.**

### ⛔ 8i. **I TESTED MY OWN BEST FINDING BEFORE BUILDING ON IT, AND THE 92% DID NOT SURVIVE**
The 92% rests on **13 rows**, so I re-extracted with the code at HEAD and measured both quality AND
supply. **Neither held up.**

| fresh extraction, 6,000 sentences per corpus | GLOSSARY_COLON yield |
|---|---|
| `textbook_psychology_2e` | 48 (8.00 per 1,000) -- 12% of its definitional patterns |
| `simplewiki` | 7 (1.17 per 1,000) -- 1% |
| `textbook_biology_2e` | **4** (0.67 per 1,000) -- **1%** |

**QUALITY ON FRESH PSYCHOLOGY TEXT: 4 MEANINGFUL / 3 RELATED / 23 NOISE = 13%, NOT 92%.**

**AND THE CAUSE IS PLAIN FROM THE ROWS: the pattern is matching BIBLIOGRAPHY ENTRIES.**
`genie -> tragedy` *[A Scientific Tragedy]*, `drug -> introduction` *[An introduction to behavioral
pharmacology, 7th edition]*, `mcn -> journal` *[The American Journal of Maternal Child Nursing,
30]*. **A reference list is `Title: Subtitle`, which is exactly the shape of `term: definition`, and
the pattern cannot tell them apart.**

**➡️ THE CORRECTED CLAIM: `GLOSSARY_COLON` IS 92% ACCURATE *WHEN IT FIRES INSIDE A REAL GLOSSARY*
AND ~13% WHEN IT FIRES IN A BIBLIOGRAPHY -- AND NOTHING IN THE EXTRACTOR DISTINGUISHES THE TWO.**
The v5 sample drew from a genuine glossary region (`ecology: the study of...`); fresh extraction
over the psychology textbook body hits its reference list instead. **The v5 result stands for its
population. The generalisation to "glossary lines are the target" does not, and I made that
generalisation one turn earlier.**

**WHAT THIS IS WORTH: more than the fragile 92% was.** It names a specific, fixable defect (a
region/genre filter, or refusing colon-matches whose definiens looks like a citation) and it sizes
the prize honestly -- **supply is 0.67-8.00 per 1,000 sentences, so even a perfect fix is a small
lever, not a plan.** *Prevalence measured BEFORE proposing the fix, which is the rule that killed
two other proposals today.*

**🔧 AND A TOOLING NOTE, BECAUSE IT NEARLY BECAME THE FINDING:** my first two attempts at the corpus
API (`.stream()`, then `.available()`) each returned **a clean ZERO for every corpus** -- which
reads exactly like *"no glossary lines exist in any corpus"*. **A zero from a wrong call is
indistinguishable from a zero from the data.** Caught only by inspecting the handle's real
attributes.

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
