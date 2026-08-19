# BUILD PLAN -- WHAT TO DO NEXT, POST-AUDIT. START HERE.

> **📖 HOW TO READ THIS FILE (it is 67 KB and every autoloop continuation is told to open it).
> IT IS NEWEST-FIRST. The top ~250 lines are the current position; everything below is the record
> in reverse order, kept so retracted claims stay VISIBLE rather than quietly deleted.**
> **THREE THINGS IN THE LOWER HALF ARE SUPERSEDED AND ARE MARKED AT THE STALE TEXT ITSELF, not
> only corrected above it:** the "~10x" Phase 2 headline (wrong floor, AND its consolidation organ
> never fired), `COOC_floor` described as "strongest" (it is not -- cosine over the same counts
> beats it 0.0300 vs 0.0125), and SR filed as "starved" (refuted by its own re-test).
> *If you are resuming and want only what to DO next, read to the first `---` and stop.*

**Written 2026-08-18 end of session, at the owner's direction, to be executed after compaction.**
Supersedes the forward-looking parts of `PLAN_ORGAN_STEP_LADDERS_2026-08-17.md`. Its Section 7
(the audit findings) and Section 6 (the ladder METHOD) both still stand as reference.

> **⛓️ COUPLING NOTE, BOTH SIDES (CLAUDE.md "a doc parsed by code is coupled to it"): THIS
> FILENAME IS AN API.** `data/hooks/staging/stop_hook.py` `_plan_path()` (~line 1155) matches
> `BUILD_PLAN_post_audit_2026-08-19.md` as the FIRST entry in its priority list, and every autoloop
> continuation tells the session to open it. **If this file is renamed, edit that list in the same
> commit** -- the previous version of that list named two plans that had not existed for weeks, and
> the hook silently emitted a "re-read a file that is not there" instruction on every turn.

> **🤖 AUTOLOOP ARMED 2026-08-19 AT 200 CONTINUATIONS (owner: "200 iterations authorized").**
> Stop it with `python tools/autoloop.py disarm`, or set `armed: false` in
> `data/hook_state/autoloop.json`, or from the dashboard's RUNNING tab. Anything other than exactly
> boolean `true` reads as DISARMED -- the fail-safe direction is OFF.

## THE DECISION THIS PLAN IMPLEMENTS

**Owner:** *"we need to have a current best substrate... we should envision a complete substrate (or
close to) and wire in the best versions of each."* Plus: **mine MIDDLE_BAND**, **parity is
interesting**, and the instrument rebuild is **deferred on the Director's recommendation**.

**Director's recommendation, accepted into this plan: WIRE TIER 0+1, THEN SPEND THE EFFORT ON THE
EMPTY SLOTS, NOT ON POLISHING THE FILLED ONES.** Assembly alone produces a well-organised filing
system. The two empty slots -- **inference** and **producing an answer in words** -- are the
difference between that and something that understands.

---

## ✅ PHASE 0 IS DONE AND MEASURED (`2e8134fd2`, 2026-08-19). DO NOT REDO IT.

- **0.1 `situation_reader` import 205 s -> 30.4 s, and its self-test now PASSES in 102.7 s** where
  it previously TIMED OUT at 240 s. Same induced hypothesis (`ruleind`), so the fix changed cost and
  nothing else. **`situation_reader` IS ON THE WIRE LIST.**
- **0.2 `_scratch_orig_goal_owner_select` removed** from `hdlab/` and from the registry (202 -> 201
  rows, all re-parsed). Git-tracked, so recoverable from history.
- **0.3 The dashboard now says `UNVETTED`, never a blank.** Tab 7 carries a HAS ANYONE CHECKED IT?
  column; a `SHELVED_REFUTED` cell colours its row red regardless of what the run called itself.
  Checked at the RENDERED CELL by the self-test: 0 blank of 14. Lookup is EXACT-match only --
  looser matching mapped `..._selftest` onto the full run's record, and a wrong disposition is worse
  than UNVETTED.
- **⚠️ FOUND WHILE DOING IT, NOT FIXED: `hdlab/ca3_completer.py` (23 KB) IS UNTRACKED.** It is on
  the Tier 1 wire list and exists ONLY in the working tree -- any checkout, reset or clean destroys
  it. Same class as board Q52. **Not committed here: it is not this session's work to sign.**

## PHASE 0 -- ONE HOUR, DO IT FIRST

**0.1 Fix `situation_reader`'s import-time training.** `hdlab/situation_reader.py:108` runs
`_INDUCED_SUBJ_NAME, _INDUCED_SUBJ_HYP = get_induced_subj_hypothesis()` **at module level**, so
merely importing the module trains a frame-induction hypothesis: loads the train split, enumerates
classes, builds a spec, runs `induce()`. That is the whole 204.5 s import and why its self-test
times out at 240 s. **The author already caches it ("trains at most once per process") -- the design
is sound, the PLACEMENT is not.**
**FIX: move it behind a lazy accessor so it fires on first USE, not first IMPORT.** Keep the cache.
**THEN `situation_reader` JOINS the wire list** -- it is genuinely functional (cross-sentence 0.5292
vs a blind baseline of 0.0000). *Excluding a working organ over where one statement sits is the
wrong trade; the earlier "exclude it" recommendation is withdrawn.*

**0.2 Remove `hdlab/_scratch_orig_goal_owner_select.py`** from `hdlab/` and from
`data/capability_registry.jsonl`. 55 KB, a scratch file registered as a capability, 103 s to import.
**Do NOT bundle the deletion with other work in one call -- that pattern is auto-denied here and
destroys whatever is bundled alongside it.**

**0.3 Fix the dashboard's honesty defect** (`PLAN` 7.5b). Tabs `4. SCORES` and `7. LATEST RESULTS`
render verdict strings straight from `metrics.json`, and 99.5% of those cannot be checked from their
own files. **Every verdict must show its ledger disposition beside it, with `UNVETTED` as the
VISIBLE DEFAULT** -- `tools/vetting_ledger.py --cite` already answers this and already refuses
unknown cells. A blank currently reads as endorsement.

---

## ✅ PHASE 1 IS BUILT AND SELF-TESTING (`2f9f3ae95`, 2026-08-19). `hdlab/substrate.py` EXISTS.

**`python -m hdlab.substrate` -> ALL SELF-TESTS PASSED.** Measured on that run: **400 sentences
read from 2 corpora it chose off a 36-corpus shelf, 3,400 lemma flags, 3,400 one-shot episodic
writes, 19 facts grounded WITH PROVENANCE, 124 refused by the consolidation gate**, persisted to
disk, query refuses a nonce and binds a seeded word. 7.9 s. Slots: **9 FILLED / 6 NEEDS_ADAPTER /
8 EMPTY / 3 EXCLUDED**, and the object reports all four itself.

**THE SELF-TEST CAUGHT FOUR DEFECTS IN THE ASSEMBLY CODE ON ITS FIRST RUNS. That is the return on
writing RULE 2 the way it is written, and the two worth carrying forward:**
- **`query()` returned zero facts for EVERY cue** (it scanned `live_facts()` as dicts; they are
  `FactRecord` dataclasses) **and the nonce arm passed anyway.** *A store that refuses everything
  passes a refusal test trivially.* **ALWAYS PAIR A REFUSAL ARM WITH A BINDING ARM.**
- **`gap_detector` was reported never-invoked WHILE RUNNING.** `ReadingLoopState` builds its own,
  so a call counter on the wrapper is structurally blind to it. Fixed by counting the ARTIFACT
  (`gap_cache`), not the call. **Reporting working machinery as dead is the false-negative twin of
  the false coverage this audit exists to catch, and it took 20 minutes to nearly commit.**

### 🔎 PHASE 1 FINDING #2 -- GROUNDING TURNS ON BETWEEN 100 AND 400 SENTENCES, AND THE GATE BINDS HARD
Measured, `scratch/phase1_grounding_scale.py`: **100 sentences -> 0 provenance rows; 400 -> 19.**
Provenance is written ONLY at the consolidation gate, so it is the proof grounding fired at all.
**The gate refused 124 and grounded 19 -- it rejects roughly 87% of what reaches it**, which is the
2026-08-12 grounding-refusal fix working rather than a gate that says yes to everything.
*Observed once and NOT a finding: reading 550 sentences produced FEWER grounded terms than 400
(14 vs 19). Consistent with the measured ACCUMULATE interference result, but n=1 -- do not quote it.*

### 🔎 PHASE 1 FINDING #3 -- THE FORAGER DECIDES WHEN TO LEAVE, NOT WHAT TO OPEN. PATCH ORDER IS ALPHABETICAL.
**It read `alice_in_wonderland` then `anne_of_green_gables` -- the first two names in sorted order --
and found 5 definitions in 400 sentences.** `definitional_extraction` pulled 228,133 definitions
from SimpleWiki; on narrative fiction it has almost nothing to find. **Charnov's theorem is about
WHEN TO LEAVE a patch; WHICH PATCH TO ENTER is a separate decision and we have not made it.**
*The shelf was the point of wiring `corpus_registry`, and we are still reading whatever is
alphabetically first.* **BUILD TARGET, cheap and well-posed: patch CHOICE by expected gain.**

---

## PHASE 1 -- WIRE THE SUBSTRATE (Tier 0 + Tier 1). **BUILT; TIER 2 REMAINS NEEDS_ADAPTER.**

**THE DELIVERABLE IS ONE FILE: `hdlab/substrate.py`.** Not a diagram, not a registry edit -- an
importable object that holds the organs in dependency order and can be run. Until that file exists
and self-tests, "wired" is a word.

**Required shape, so a post-compaction session builds the same thing:**
- `class Substrate` with **LAZY per-organ construction** -- an organ is imported and built on FIRST
  USE, never at `import hdlab.substrate`. *Phase 0 existed because one module trained at import
  time; do not rebuild that defect at the assembly layer.*
- `Substrate.read(source, limit) -> ReadResult` -- the INGEST path (Tier 0 + Tier 1).
- `Substrate.query(question) -> QueryResult` -- the RETRIEVAL path (Tier 2), returning the store
  entry, the confidence, the ACCEPT/CLARIFY/REFUSE decision, and the provenance trace.
- `Substrate.organ_report() -> dict` -- which slots are FILLED, which are EMPTY, which are
  DELIBERATELY EXCLUDED and why. **An empty slot must be visible from the object itself**, not only
  from a note; that is how P1/P2 went unwritten for weeks.
- `python -m hdlab.substrate` self-test: builds, reads a few sentences, queries, asserts each wired
  organ actually ran (count its invocations -- an organ that is imported and never called is not
  wired), prints the organ report.

**Wiring order (dependencies, not preferences) from `notes/COMPLETE_SUBSTRATE_DESIGN_2026-08-18.md` 4.1:**
**Tier 0 (reading):** `corpus_registry` -> `information_foraging` -> `definitional_extraction`
**Tier 1 (memory):** `hippocampal_encoder` -> `ca3_completer` -> `prelim_tier` -> `foundation_persistence`
**Tier 2 (comprehension):** `coreference_resolver` -> `situation_model_accumulate`; `semantic_parser` -> `cortex`

**Cost ~75 s one-time import**, dominated by `definitional_extraction` -- and after Phase 0,
`situation_reader` (30 s) is affordable too.

**WIRE ONLY THE INTERSECTION of self-test-passing AND probe-FUNCTIONAL.**
**⛔ DO NOT WIRE:** `atom_consultation` (`applied` hard-coded `False` -- cannot change a decision),
`definitional_predicate_v61` (fires on 0.27% of its intended population), `goal_achievement`'s
desiderative-negation channel (7/7 on authored exemplars, 4/7 on paraphrases; also the one genuine
self-test failure: `AssertionError: channel 'relation:recur' != 'majority'`). **All three are
self-test-passing. That is exactly why the intersection rule exists.** `cortex` is wired with
`atom_consultation` OFF.

**⚠️ `hdlab/ca3_completer.py` IS UNTRACKED IN GIT** -- 23 KB living only in the working tree, on
this wire list, destroyed by any checkout/reset/clean. Same class as board Q52. Commit it or get an
owner ruling BEFORE any git operation that touches the tree.

### 🔎 PHASE 1 FINDING #1 -- THE ORGANS DO NOT SHARE A DATA FORMAT, AND ONE IS NOT A TEXT ORGAN AT ALL

**Measured 2026-08-19 by runtime signature introspection of all 11 wire-list modules**
(`scratch/phase1_api_survey.py`, `scratch/phase1_glue_check.py`), not by grep and not from a
docstring. **This is exactly the risk Phase 2 was written to catch, arriving one phase early.**

**`hdlab/coreference_resolver.build_mention_stream(passage)` READS `passage["entities"]` -- A GOLD
MENTION INVENTORY KEYED BY GOLD ENTITY NAME**, and the records it emits carry a `gold_entity` field.
It also requires `passage["clauses"]`. **It decides which mention links to which entity GIVEN the
mentions and the entity set; it does not find them in prose.** So the ingest story in
`COMPLETE_SUBSTRATE_DESIGN` 4.3 -- *"`coreference_resolver` decides which later mention is which
earlier entity"* as a step in a text-in pipeline -- **is not runnable on unannotated text as
written.** Its probe score (0.7193 vs recency 0.5614) was measured on gold-annotated LitBank and
remains true OF THAT REGIME.

***TRIPLE-CHECK STATEMENT (CLAUDE.md Evidence discipline 5), because this calls something narrower
than documented:*** right file (`hdlab/coreference_resolver.py` at HEAD, source read directly, not
the docstring); right version (HEAD after `2e8134fd2`); right env (`.venv`); right metric (the
function's own parameter reads, not a summary); right arm (the PUBLIC entry point, not an internal
helper). **What rules out the obvious alternative: there IS a raw-text path and it is a DIFFERENT
organ.** `situation_reader.SituationReader.read(path)` takes a FILE OF PROSE -- verified by running
its self-test this session, which writes plain sentences to a temp file and passes -- and gets its
mentions from our own parser (`_pick_role_mentions(pred_idx, sent_noms)`), reusing `coref` and the
event-bundle codec internally. **So the finding is "the coreference RESOLVER is gold-fed", NOT
"we cannot do coreference on text".**

**THE SAME SHAPE HOLDS ACROSS THE LIST, and it is the thing to design around:**
| organ | what it actually consumes | composes on raw text? |
|---|---|---|
| `corpus_registry` | a directory | **YES** -- hands out sentences |
| `definitional_extraction` | sentences | **YES** |
| `situation_reader` | a file of prose | **YES** (30 s import after Phase 0) |
| `information_foraging` | a stream of GAIN FLOATS the caller defines | needs a gain signal named by us |
| `hippocampal_encoder` | a dense HD vector | needs an encoder in front |
| `ca3_completer` | FHRR bundles + per-spoke codebooks | **a different representation** from the above |
| `prelim_tier`, `foundation_persistence` | a `ReadingLoopState` / `Library` / `HDFactStore` | only via `reading_grounding_loop` |
| `coreference_resolver` | **gold mentions + gold entity set** | **NO** |
| `semantic_parser` | a TRAINED `IntentClassifier` + slot dicts | needs a fitted artifact |
| `cortex` | torch HD tensors + its own codebooks | needs an encoder in front |

**THE CONSEQUENCE FOR THE BUILD, AND IT IS A REUSE RULING, NOT A REWRITE:** `prelim_tier` and
`foundation_persistence` both key off `ReadingLoopState`, which is `reading_grounding_loop`'s --
**a LIVE entry point.** So the adapter layer this substrate needs mostly EXISTS, inside the live
loop. **Build `hdlab/substrate.py` ON TOP of `reading_grounding_loop`'s text->facts path and wire
the unwired organs INTO it. Do NOT author a parallel ingest path** -- that is the WIRE-DON'T-ISLAND
rule and the MISSING-LEARNING rule in the same costume, and a parallel path is how we would get a
second thing to audit instead of one thing that works.

**`organ_report()` MUST DISTINGUISH THREE STATES, not two:** `FILLED` (wired and invoked on the
real path), `NEEDS_ADAPTER` (works, but its input is not produced anywhere upstream -- name the
missing adapter), and `EMPTY` (nothing implements it). **A `NEEDS_ADAPTER` organ counted as FILLED
is precisely the false coverage the organ audit exists to prevent.**

---

## 🧰 "THE CHEAPEST FIX IN THE WHOLE BACKLOG" IS NOW A TOOL: `tools/strongest_floor_audit.py`
The 2026-08-18 audit named it and nobody did it: *"SEVERAL CELLS ALREADY COMPUTED THE RIGHT FLOOR
AND THEN DISCRIMINATED AGAINST SOMETHING ELSE. RE-SCORE EVERY LANDED CELL AGAINST THE FLOOR IT
ALREADY HAS ON DISK."* **It is also personal: I committed that exact defect today**, reporting the
substrate as losing "~10x" against a `COUNT_FLOOR` of 0.0125 while a stronger floor from the same
data read 0.0300. *A rule that is easy to state and evidently hard to follow should be a tool.*

**7,861 `metrics.json` scanned. 286 cells flagged** -- 143 where a floor the cell computed ITSELF
beats its own best treatment, 193 where the verdict text quotes a floor that is NOT the largest
one in its own metrics.

### 🔬 THE NUMBER WENT 1,335 -> 286 BECAUSE ITS MOST EXCITING HIT WAS WRONG, AND I CHECKED IT
**The single most striking flag was `diag_stateful_core_gen_curve_v1`: a RANDOM-INIT CONTROL at
0.6250 beating a TRAINED arm at 0.5000, under a `PASS`.** That is the untrained-beats-trained
shape this project has genuinely recorded once before -- and it was tempting.
**Checked it: `run_mode: "selftest"`, and the cell's own message says "exercised at N~4-16". It
was verifying that code paths RUN, not claiming training worked. NOT A DEFECT.**
*Four false-positive shapes were found and filtered this way, each measured rather than imagined:*
ties at ceiling (`1.0 vs 1.0`), **a DELTA read as a floor** (`real_minus_shuffle` matched on the
word "shuffle"), cells that already declare themselves failures, and self-tests.

**⚠️ AND THE RESIDUAL FALSE-POSITIVE RATE IS STILL REAL AND IS NOT HIDDEN. Two shapes remain
UNFILTERED and visible in the top of the list:** comparing a `max_` statistic against a `mean_`
one, and near-ties across different seeds or subsets (one hit "quotes 0.6319 while holding
0.6337"). **286 IS A READ LIST, NOT 286 DEFECTS**, and the tool says so in its own output.

---

## 📖 MIDDLE_BAND ACTUALLY READ (owner: *"understanding what it was TRYING and the SIGNAL"*)
*I had produced a ranked list and a premise correction and had not read the cells. Owed, now done.*
**Only 26 of 580 carry a self-assessment field and only 31 have a readable docstring -- and ZERO
have both**, which is why the list looked thin. The 26 are the population worth reading.

### ⬇️ CORRECTION TO MY OWN FRAMING BELOW, MADE ONE CONTINUATION LATER AND BEFORE ANYONE BUILT ON IT
**I called this cell "a lead for the empty inference slot with a number attached". IT IS NOT A
REASONING MEASUREMENT.** Read from its metrics: the arms are *"recall vs independent nltk gold"*
over a *"materialized within-5k HYPERNYM+PART_OF backbone"*, by *"deterministic BFS"*. **nltk
hypernym/part-of IS WordNet, and the backbone is a MATERIALIZED COPY of that same relation set.**
So `recall 0.61` at 2 hops means **39% of gold pairs were not reachable in the copy** -- and the
cell says the mechanism itself: *"each hop multiplies out-of-5k-intermediate misses"*.
***THIS MEASURES HOW COMPLETELY A KNOWLEDGE GRAPH WAS COPIED AND HOW BFS DEGRADES WHEN THE COPY HAS
HOLES. The depth "cliff" is coverage decay, not a reasoning boundary.*** *The cell is honest about
this in its own scope line -- "NOT general reasoning", "measured-bounds not fundamental" -- and I
read past that to the part I wanted.*
**⚠️ LIMIT ON THIS CORRECTION, STATED: `experiments/exp_b_alpha_broad_envelope_cpu_v1.py` IS NOT
ON DISK, so I am inferring the backbone's provenance from the metrics rather than reading the
build. If the backbone were materialized from a NON-WordNet source the circularity would not
apply -- but nothing in the metrics suggests that, and the burden is on the claim.**

**🟢 AND THERE *IS* SOMETHING REAL HERE -- IT IS JUST NOT THE RECALL NUMBER.**
**`false_positives: 0` across all five benchmarks; `refuse_rate: 1.0`; 750 negatives verified
GENUINELY UNREACHABLE by exhaustive BFS at build ("not bounded-give-up"); and 4,344 of 4,344
returned path edges trace to a persisted Store tuple -- `n_unverifiable_edges: 0`.**
***The system refuses instead of confabulating, and every answer it gives is fully auditable.***
*That is the glass-box invariant demonstrated at scale, and it is worth more to this project than
a recall figure. Caveat that must travel with it: a system which only ever reports STORED paths
gets "no hallucination" cheaply -- the property is real, the difficulty of achieving it is not.*

**🎯 [SUPERSEDED BY THE CORRECTION ABOVE] THE ONE WITH A LEAD FOR A CURRENTLY-EMPTY SLOT.** `exp_b_alpha_broad_envelope_cpu_v1`:
> *"Characterizes WHERE composed reasoning works (**2-hop MIDDLE**) vs **CLIFFS (3-4 hop
> HARD_FAIL**). NOT general reasoning. Per-benchmark HARD_FAIL = **honest cliff FINDING**."*
**Q2 domain-general inference is a NAMED EMPTY SLOT in the substrate design, and this cell already
measured its boundary: composition survives two hops and falls off a cliff at three.** *That is a
starting point with a number attached, and it was sitting unread. Verify before leaning on it --
it is UNVETTED and the ledger still refuses it.*

**AND FOUR CELLS THAT EMBODY DISCIPLINES THIS PROJECT KEEPS RE-LEARNING, WRITTEN BY THEIR OWN
AUTHORS:**
- **The strongest-floor rule, applied by a cell to itself.**
  `exp_agreement_attractor_role_binding_cg_viability_v1`: *"Beating nearest-noun is TRIVIAL here
  (nearest is the attractor -> below chance); the HONEST discriminator is beating the FIRST-NOUN
  positional heuristic on the subject-not-first subset."* **It identified that its own obvious
  baseline was the wrong one and named the right one.**
- **A cell refusing to let its own metrics be read as quality.**
  `exp_grounding_quality_readout_v1`: *"**THIS CELL MEASURES NO QUALITY.** Everything it emits is
  structural or a stability/selectivity control."*
- **A cell delimiting what each of its arms licenses.** `exp_grounding_readout_known_answer_v1`:
  *"Convergence with the prior hand-score is evidence ABOUT THE PROXY, never a substitute for
  it"*, and *"STAGE B is a 2-candidate forced choice; it licenses NO statement about the
  open-vocabulary argmax rate."*
- **The circularity trap, flagged by the cell that fell into it.**
  `exp_learned_composition_glue_pun_selectional_generalization_v1_smoke`: *"generalization signal
  is WordNet-hypernym (KB-derived); a full-gate pass is a CANDIDATE for fresh adversarial VET,
  not a self-declared CG."*

**THE HONEST SYNTHESIS, WHICH IS NOT QUITE EITHER STORY: self-assessment is RARE EVERYWHERE
(MIDDLE_BAND 4.5%, HARD_PASS 3.0% -- no real difference, as measured). But the ones that exist
cluster at the TOP of the MIDDLE_BAND ranking, and they are worth reading INDIVIDUALLY rather than
aggregating.** *The owner's instinct was right about the cells and wrong about the population
statistic, and both halves are worth keeping.*

---

## 🧪 THE CELL THAT CAN SETTLE IT IS RUNNING: `experiments/exp_grounding_precision_gold_v1.py`
**IN FLIGHT**, detached, PID `scratch/gp_full.pid`, logs `scratch/gp_full.out` / `.err`.
3 seeds x 40,000 sentences, checkpointed units -> `data/exp_grounding_precision_gold_v1/`.
**DO NOT RESPAWN.** *Smoke clean: 2,000 sentences -> 76 grounded, 648 refused, coverage 98.7%, and
the shelf fix is visible -- SIX corpora visited where the old code reached three.*

**THE DECIDER IS `RANDOM_ANCHOR`, NOT A FLOOR OVER OTHER ITEMS, AND THE CELL SAYS SO IN ITS OWN
DOCSTRING.** *The gate was measured to accept terms with twice the gold degree, so any comparison
against a different item set is confounded by term difficulty. `RANDOM_ANCHOR` holds the TERMS
FIXED and randomises only the ANSWER -- it isolates "is this meaning right" from "is this term
easy". Paired permutation, not two independent CIs.*

**AND READING (iv) IS A REFUSAL TO ISSUE A VERDICT: below 300 scorable items the cell reports
UNDERPOWERED and reports the required n instead.** *At 2,000 sentences it produced 75 scorable and
flagged itself. That is the rule that would have stopped me quoting "6x" yesterday.*

---

## ⬇️ DOWNGRADED BY ITS OWN CONTROL, ONE CONTINUATION LATER: THE GATE'S PRECISION ADVANTAGE IS NOT ESTABLISHED
`scratch/gate_selection_control.py`. **Last continuation I reported the gate's accepted set at
0.0355 vs the raw argmax's 0.0058 -- "roughly 6x, the gate is doing real selection" -- flagged as
a direction rather than a result. The matched controls say even that was generous.**

**THE CONFOUND IS REAL AND NOW MEASURED: the gate accepts terms with TWICE the gold degree
(mean 42.3 vs 21.7; median 16 vs 8).** *Precision is P(anchor is a gold neighbour), so a term with
many neighbours is easier to be right about. The gate was partly selecting EASY TERMS, not good
meanings -- exactly the confound named before the probe ran.*

| arm | precision | n |
|---|---|---|
| RAW, ungated argmax | 0.0058 | 1712 |
| **RAW, DEGREE-MATCHED to the gated set** | **0.0089** | 112 |
| GATED (what we ground) | 0.0446 | 112 |
| **GATED, SAME TERMS, RANDOM ANCHOR** | **0.0179** | 112 |

**AGAINST THE STRONGEST CONTROL -- the same terms with a random anchor from the same pool -- THE
GATE IS 5 HITS AGAINST 2.** ***That is a width, not an effect (discipline 14), and the "6x" should
not be repeated.*** *Degree-matching alone raises the baseline 0.0058 -> 0.0089, so part of the
original gap was the easy-terms confound and the rest is unresolvable at this n.*

**FILED: the gate's precision advantage is NOT ESTABLISHED. It is not refuted either -- 5 vs 2 is
simply too few. The named way to settle it is more grounded items, which means more reading, not a
better argument.** *Fifth time today a matched control changed a reading. The base rate for an
apparent positive surviving its own twin in this project remains grim, and it applies to my
positives too.*

---

## ❌ HUBNESS HYPOTHESIS TESTED AND REFUTED -- AND IT MOVED THE PROBLEM TO A DIFFERENT ORGAN
`scratch/hubness_probe.py`. **I proposed that the generic attractor is HUBNESS in the
anchor-selection argmax, and that this might explain why the constant/prototype floor is the
strongest floor across this whole project.** Tested before building on it.

| | distinct / queries | top-share | gold precision |
|---|---|---|---|
| ARGMAX (what `canonicalize` does) | 205 / 1926 = **0.106** | **2.4%** | 0.0058 |
| hubness-corrected (similarity centering) | 205 / 1926 = 0.106 | 1.8% | **0.0058, identical** |

**THE CORRECTION CHANGES NOTHING**, and the correlation between an anchor's mean similarity to all
queries and how often it wins is only **r = 0.305** -- too weak to be the mechanism. **HYPOTHESIS
REFUTED.** *Cost: one probe, no build.*

### 🎯 AND THE REFUTATION IS MORE USEFUL THAN THE HYPOTHESIS WOULD HAVE BEEN
**THE RAW ARGMAX IS NOT DEGENERATE AT ALL: 205 distinct anchors over 1,926 pending items, top
anchor 2.4%.** *The grounded set was 39 anchors over 96 terms with the top at 17.7%.* **So the
concentration is NOT introduced when the anchor is CHOSEN. It is introduced by WHICH CANDIDATES
THE CONSOLIDATION GATE ACCEPTS.** *I was looking at the wrong organ, and the probe said so in one
run. The next investigation belongs at the gate -- schema consistency, vote margin, min_confirm --
not at `canonicalize`.*

**🟢 AND AN UNEXPECTED POSITIVE FOR THE GATE, STATED WITH ITS LIMIT: the gate's ACCEPTED set scores
0.0355 against the raw argmax's 0.0058 on the same gold -- roughly 6x. The gate is doing real
selection, not just thinning.** ***⚠️ That is 5 hits of 141 against 10 of 1,712, and it is a
SELECTION EFFECT BY CONSTRUCTION -- which is what a gate is for. It is a direction, not a result,
and single-digit hit counts cannot carry more than that.***

**⚠️ NOT A REDISCOVERY OF DO-NOT-REDO 27, and the difference was stated before running:** that
entry closed RANK-1 COMMON-MODE REMOVAL applied to the STORE in the ACCUMULATE-interference
setting on the dissociation instrument. This was applied to the ANCHOR-SELECTION ARGMAX, on
grounding degeneracy, on a different scorer and population. **A second independent negative for
the same family of fix, at a different site.**

---

## 🚨 SECOND DEFECT I BUILT: 25 OF 28 CORPORA WERE UNREACHABLE, AND IT LOOKED EXACTLY LIKE SATURATION
**The degeneracy trajectory was meant to test whether the anchor pool is a cold-start bottleneck.
It first produced a textbook learning ceiling: grounding plateaued at 180 terms, new anchors per
chunk fell 21 -> 9 -> 32 -> 7 -> 1 -> 1 -> 0, and `distinct/grounded` flattened at 0.42.**
*I was one paragraph from writing "the substrate saturates after ~1,600 sentences".*

**IT WAS NOT SATURATION. `readable_names()` IS SORTED, so EVERY `read()` restarted at the
alphabetical head and took the first `max_patches` names -- re-entering the SAME THREE BOOKS until
they drained. MEASURED: 113,649 sentences remained across just 12 of the 28 readable corpora, and
25 of 28 were NEVER OPENED.** *The reader had a 36-corpus shelf and could reach three of it.*
**FIX: skip drained patches, and rotate the start point so the next read continues where the last
stopped.** *This is the concrete cost of Phase 1 Finding #3 -- the forager chooses WHEN to leave
but not WHAT to open -- and the cheapest half of that fix.*

### 📈 WITH A VARIED SHELF, THE DEGENERACY ROUGHLY HALVES -- READING (A) FIRES, BUT ONLY PARTLY
| | narrow shelf | rotated shelf |
|---|---|---|
| top-anchor share | 23.6% -> **12.8%** | 23.6% -> **9.5%** |
| distinct anchors / grounded | 0.382 -> 0.428 (**plateau**) | 0.382 -> **0.524, still rising** |
| new anchors per chunk | collapses to **0** | still arriving (**8** in the last chunk) |
| grounded terms | plateaus at 180 | 55 -> **147 and climbing** |

**And the anchors become recognisably meaning-like:** `physics -> biology`,
`discipline -> physics`, `perform -> function`, `institute -> commons` -- against the narrow
shelf's `mouse -> way`, `swim -> way`, `cry -> way`.

**⚠️ BUT IT IS NOT PURELY A COLD START, AND THE STRUCTURAL HALF REPRODUCES: a NEW generic attractor
forms.** `bookstore -> available`, `campus -> available`, `custom -> available`. *One
high-frequency word still absorbs many terms; only its identity changed. `way` remains top at
9.5%.* **So: shelf breadth halves the degeneracy and does not remove it.**

**PRECISION RE-MEASURED on the varied shelf: 0.0215 -> 0.0355 (5 hits of 141), floors 0.0142 and
0.0071. ⚠️ FIVE HITS AGAINST TWO IS NOT A WIN AND IS NOT CLAIMED AS ONE** -- the direction agrees
with the degeneracy result, and that is all it is licensed to say.

---

## 🔴 GROUNDING PRECISION MEASURED FOR THE FIRST TIME -- AND THE ANCHORS ARE DEGENERATE
**Nobody had ever asked whether the terms the substrate grounds are grounded to the RIGHT thing.**
Now measured against the provenance-filtered ConceptNet gold (422,082 edges, no WordNet source).
`scratch/grounding_precision_probe.py`, alice, 750 sentences, 96 grounded pairs, 344 refused.

**✅ THE INSTRUMENT APPLIES: gold coverage is 96.9% -- 93 of 96 grounded terms have gold edges.**
*That was the risk and it did not fire.*

| arm | precision |
|---|---|
| `TOP_COOCCURRENT` floor (the word it co-occurs with most) | **0.0323** |
| **SUBSTRATE GROUNDING** | **0.0215** |
| `MOST_FREQUENT_ANCHOR` floor | 0.0108 |
| `RANDOM_ANCHOR` floor | 0.0108 |

**⚠️ AND THE PRECISION TABLE IS UNDERPOWERED AND MUST BE LABELLED SO: those are 3, 2, 1 and 1 HITS
out of 93. The difference between 2 and 3 hits is not a result.** *Per discipline 18 this is closer
to untestable than to resolved, and quoting "the floor beats the substrate" off single-digit counts
would be the width-as-effect error.*

### 🎯 THE FINDING THAT DOES NOT NEED A CI, AND IT IS THE MECHANISM
**39 DISTINCT ANCHORS FOR 96 GROUNDED TERMS. ONE WORD -- `way` -- IS THE MEANING OF 17.7% OF THEM.**
The top six anchors are `way, know, think, people, use, time`, and **48.5% of all anchors are
seed-vocabulary words**. Actual output: `mouse -> way`, `swim -> way`, `think -> way`,
`hall -> way`, `cry -> way`. ***THESE ARE THE SAME ANSWER TO DIFFERENT QUESTIONS.***
**The grounding gate is not selecting a MEANING, it is selecting a GENERIC ATTRACTOR -- the
constant/prototype floor appearing INSIDE the grounding organ.** *No gold that encodes meaning
could ever score `way` as the meaning of `mouse`, so the low precision is downstream of the
degeneracy and not an independent fact.*

**✅ ONE OLD DEFECT IS GENUINELY GONE, RE-CHECKED RATHER THAN ASSUMED: SELF-ANCHORING IS 0.0%.**
*The 2026-08-18 audit found 2,328 of 3,544 grounded facts had THEMSELVES as their meaning. Not one
of these 96 does.* **A real repair, and worth saying so.**

**NAMED NEXT STEP, and it targets the degeneracy rather than the precision number: the anchor pool
is `ConceptSpace`, which holds SEED words plus already-grounded words -- so early grounding is
forced to choose among ~107 generic seeds. That is a structural cause with a structural fix, and
it predicts the degeneracy should FALL as the grounded vocabulary grows.** *Testable, and it does
not require a bigger n to see.*

---

## 🚨 A DEFECT I BUILT, FOUND BY TRYING TO USE MY OWN SUBSTRATE: IT ONLY CONSOLIDATED WHEN THE FORAGER CHANGED BOOKS

**MEASURED, and the contradiction is what exposed it.** Setting up the replacement task, the
substrate grounded **NOTHING** on 6,000 sentences of simplewiki -- and nothing on 2,000 sentences
of each of FIVE other corpora, narrative included. Yet the self-test grounds 19 on 400 sentences.

**CAUSE: `read()` called `checkpoint()` ONCE PER PATCH.** Grounding needs `min_confirm=4` traces
**across passes**, and one patch is one pass, so **a single-patch read grounded zero at ANY
volume.** Consolidation frequency was tied to the corpus CHANGING, not to how much had been read.

| | before | after |
|---|---|---|
| simplewiki, 750 sentences, 1 patch | **0 grounded / 0 refused** | **38 / 199** |
| alice, 750 sentences, 1 patch | **0 / 0** | **97 / 344** |
| self-test config (400 / 2 patches) | 19 / 124 | 55 / 258 |

**FIX: consolidate on a SCHEDULE (`consolidate_every=200` sentences), which is also the more
faithful shape -- the brain consolidates offline and periodically, not when you pick up a new book.**

### ⚠️ SCOPE CORRECTION TO THE PHASE 2 NEGATIVE -- NOT A RETRACTION, BUT IT MUST TRAVEL WITH IT
**`exp_substrate_end_to_end_readout_v1` ran with `max_patches=1`, so EVERY Phase 2 run grounded
NOTHING. The consolidation organ never fired in the cell that reported on the assembled substrate.**
*The result still stands as measured -- the EPISODIC and SEMANTIC routes read from episodic writes
and Library traces, which happen regardless of consolidation -- but the substrate was running with
one of its central organs effectively OFF and I did not notice.*
**AND THE EVIDENCE WAS IN MY OWN OUTPUT THE WHOLE TIME: the smoke printed `"n_provenance": 0` and
I read past it.** *A zero in a field I chose to emit, in a cell I wrote to catch exactly this class
of thing.* **Re-run the cell with periodic consolidation before quoting its ablation table again.**

### 🔎 AND THE CORPUS-TYPE FINDING SURVIVES, NOW QUANTIFIED INSTEAD OF 0-vs-0
At matched volume (750 sentences, one patch): **narrative grounds 97, encyclopedic grounds 38 --
2.5x.** *The substrate grounds where words RECUR, not where they are DEFINED. That inverts the
naive expectation and it is worth keeping: `definitional_extraction` wants encyclopedias and the
consolidation gate wants stories, and the forager currently serves neither deliberately.*

---

## 🧭 DIRECTOR'S CALL, 2026-08-19: **STOP OPTIMISING INTO THE CLOZE TASK. IT CANNOT SHOW A WIN.**
*Full-auto ruling, made rather than filed, and it changes what the next continuations do.*

**THE ARITHMETIC THAT FORCES IT.** The BEST number anywhere in today's diagnostic is **0.0300**
(exact co-occurrence, cosine-ranked). Our best route is 0.0150. **So the entire prize available
from fixing every representation defect I found is to CLIMB FROM 1.5% TO 3% AND TIE A FLOOR.** A
task whose ceiling is a tie with the dumbest available method is not an instrument for detecting
understanding -- it is a way to spend continuations.

**THIS PLAN ALREADY SAID SO, IN THE DEFERRED SECTION, BEFORE ANY OF TODAY'S RUNS:**
> *"PREFER TASKS WITH LARGE EFFECT SIZES OVER BUYING POWER ON A TASK WITH A TINY ONE. When a
> mechanism genuinely works you see pattern completion 0.20 -> 0.92, or leave@3 vs leave@8 on an
> identical patch. No CI needed. A whole day of gated word-meaning arms fought over 0.63 vs 0.55 --
> THAT GAP IS THE PROBLEM, NOT THE SAMPLE SIZE."*

**0.0075 vs 0.0300 IS THAT SHAPE AGAIN, ONE ORDER OF MAGNITUDE SMALLER.** *I wrote the warning
into this file yesterday and then spent four continuations inside exactly the failure it names.
The cell itself even declared "this task favours the floors by construction" in its own docstring.
I shipped the caveat and ignored it.*

**WHAT STAYS AND WHAT STOPS.**
- **KEEP:** the cell, the harness, the ablation machinery, `readout_verdict.py`, and the negative.
  **The Phase 2 result is real and it stands** -- the substrate memorises and does not transfer.
  That was worth establishing and it is established.
- **KEEP:** the two cheap correctness fixes, because every FUTURE measurement inherits them --
  add an `EXACT_COOC_COSINE` arm as the strongest floor, and fix the query construction (worth 2x).
  **They are hygiene, not a research programme.**
- **STOP:** treating cloze hit@1 as the substrate's report card. **No further mechanism gets built
  to move it.**

### ➡️ THE REPLACEMENT TASK, AND IT TESTS THE CLAIM THE SUBSTRATE ACTUALLY MAKES
The substrate's stated output is **an auditable store of facts, each traceable to the sentence it
came from**. It grounds ~19 terms per 400 sentences and **REFUSES 124** -- a gate that discriminates
7:1. *Nothing has ever asked whether the 19 are RIGHT.*

**BUILD: grounding PRECISION against an INDEPENDENT gold.** For each term the substrate grounds,
does its meaning-anchor match a definition from a source the substrate never read? **Effect size is
plausibly large** (a gate at 0.8-0.9 against a floor near 0.3), which is the whole point of the
switch. **Floors, all runnable from the cell's own data:** most-frequent-co-occurrent, the term's
own nearest neighbour by count, and a random anchor from the grounded set.
**⚠️ AND THE TRAP IS NAMED IN ADVANCE: the gold must not be WordNet if anything on the path
touches WordNet, and `lemma_word` DOES use WordNet morphy.** *Morphology is not meaning, so this is
probably admissible -- but it must be checked and stated, not assumed, and the alternative
(dictionary/Wiktionary definitions already on disk) is cheap.*

### ✅ THE GOLD IS SETTLED, AND CHECKED BEFORE ANY CELL WAS WRITTEN
`scratch/conceptnet_admissibility.py`. **ConceptNet's FULL assertions file carries a `dataset`
provenance field per edge, so WordNet-derived edges are EXCLUDABLE BY CONSTRUCTION.** Measured over
400,000 English-English edges: **78.2% `/d/wiktionary/en`, 18.0% `/d/conceptnet/4/en` (crowd),
and only 0.1% `/d/wordnet/3.1` -- 254 edges, all droppable.** *So an independent, non-WordNet,
non-LLM gold exists on disk and the circularity constraint is satisfiable.*

**🪤 AND THE CONVENIENT FILE IS THE TRAP, CONCRETELY.** `data/datasets/conceptnet5_en_100k.jsonl`
is pre-extracted, small and ready to use -- **and it has NO provenance field at all**, only
subject/predicate/object. **WordNet edges cannot be excluded from it, so it is INADMISSIBLE as a
gold** however convenient it is. *That is "the way we lose is by trying fancy available tools",
in one file, and it would have been invisible after the fact.*

**⚠️ SCOPE OF THAT MEASUREMENT, STATED: the assertions file is sorted by URI, so the 400,000 rows
scanned are an ALPHABETICALLY-ORDERED PREFIX, not a random sample.** *The WordNet share elsewhere
in the file may differ, and `/r/IsA` is likely under-represented by that ordering. A full-file
count is cheap and must be run before the gold is frozen -- do not quote 0.1% as a file-wide fact.*
**PROBES, NOT A CELL: one seed, one corpus, one task, NO CI. Not citable. They exist to pick the
next build.** `scratch/projection_loss_probe.py` + `probe2.py`. Identical items, identical frozen
vocabulary (2,161), identical 12,000-sentence corpus, **matched scale** -- only the
REPRESENTATION and the CUE differ.

| representation | hit@1 |
|---|---|
| **EXACT co-occurrence, cosine-ranked** | **0.0300** |
| random projection of the same, d=1024 | 0.0275 |
| random projection of the same, d=256 | 0.0225 |
| **OUR encoder, cue = sum of the cue words' own profiles** | **0.0150** |
| **`COUNT_FLOOR` -- the floor our cells have been using** | **0.0125** |
| **OUR encoder, cue = whole-sentence vector (what the substrate does)** | **0.0075** |
| random projection, d=64 | 0.0050 |

### 🚨 CORRECTION TO MY OWN PHASE 2 REPORT, AND IT MAKES THE NEGATIVE WORSE, NOT BETTER
**`COUNT_FLOOR` IS NOT THE STRONGEST FLOOR THIS DATA SUPPORTS. Cosine over the SAME co-occurrence
counts scores 0.0300 against its 0.0125 -- 2.4x.** The standing rule is *"run the STRONGEST floor
the cell's own data supports"*, and this archive has already refuted three cells for using a weaker
one. **I did the same thing today.** *The Phase 2 verdict does not flip -- no substrate route was
anywhere near either floor -- but "loses to counting by ~10x" was measured against the weak floor,
and against the right one the gap is larger. **Any re-run of that cell must add an
EXACT_COOC_COSINE arm.***

### 🎯 WHERE THE LOSS ACTUALLY IS, DECOMPOSED
- **projection:** 0.0300 -> 0.0225. Real, ~25%, and **NOT the main cost.** d=1024 recovers almost
  all of it; d=64 is catastrophic. *A d-sweep buys something here, unlike on addressing (C36).*
- **our encoder vs a plain random projection at the SAME d and scale:** 0.0225 -> 0.0150.
  **We lose 33% to a random projection of the same counts.**
- **🔴 CUE CONSTRUCTION: 0.0150 -> 0.0075. THE SINGLE LARGEST FACTOR MEASURED -- A FULL HALVING,
  AND IT IS WHAT THE SUBSTRATE ACTUALLY DOES.** Building the query as a whole-sentence vector
  costs twice as much as any representation choice in the table.
  ***⚠️ DO NOT CROSS THIS WITH "THE CUE SIDE IS CLOSED" (four cells, DO-NOT-REDO 46).*** That
  closure was a DIFFERENT scorer, population and instrument (partial-cue addressing, hit@1
  0.0223 -> 0.0249 NOT_SEPARATED). **This is a new measurement on a new task, not a contradiction
  of that one, and the two numbers may never appear side by side.**

**WHAT THIS CHANGES ABOUT THE NEXT BUILD: the information is present and usable -- our own counts,
ranked properly, beat the floor 2.4x. So the next move is NOT a fifth mechanism. It is to stop
discarding what we already have, and the cheapest lever measured is the QUERY.**

---

## 🔻 RETRACTED, SAME NIGHT, BY MY OWN NAMED RE-TEST: SR WAS **NOT** STARVED. D7 IS A REAL NEGATIVE.
**`exp_sr_scale_ladder_v1`, 3 seeds, 400 items, pool FROZEN at 2,161, nested corpora, only the
transition data varies. 63 s.** *The block below filed SR as UNTESTABLE-AT-THIS-SCALE and named
exactly one way to settle it. It is settled, and against me.*

| transitions/state | SR γ=0.1 | SR γ=0.9 | **COOC floor** | FREQ floor |
|---|---|---|---|---|
| 2.48 | 0.01417 | 0.01167 | 0.01917 | 0.00667 |
| 6.91 | 0.00917 | 0.00417 | 0.03417 | 0.00917 |
| 25.68 | 0.00417 | 0.00333 | 0.04417 | 0.00917 |
| **80.19** | 0.01250 | **0.00167** | **0.05833** | 0.00917 |

**ACROSS A 32x RANGE: THE CO-OCCURRENCE FLOOR TRIPLES (0.019 -> 0.058). SR γ=0.9 FALLS TO A
SEVENTH. SR γ=0.1 IS FLAT.** *The data increase is real and usable -- the floor proves it on the
identical corpus, items and frozen pool. SR simply cannot use it.* **At the top rung SR would have
to move 27.2 CI half-widths to reach the floor. That is RESOLVED, not underpowered.**
**PRE-COMMITTED READING (iii) FIRES: starvation is REFUTED as the explanation, and D7 over lemma
transitions is a REAL NEGATIVE.**

### 🔬 AND THE MECHANISM IS MEASURED, NOT NARRATED -- LONG-HORIZON SR BECOMES A CONSTANT
`scratch/sr_mixing_probe.py`. γ=0.9 is ~100 steps of lookahead; over a word graph that is far past
the mixing time, so `P^k` converges to the STATIONARY DISTRIBUTION, **which does not depend on the
cue.** More text connects the graph better and mixes it FASTER. Distinct top-1 answers over 300
DIFFERENT cues:

| rung | γ | distinct answers / 300 cues | share taken by ONE word |
|---|---|---|---|
| 750 | 0.9 | 160 | 17.7% |
| **40,000** | **0.9** | **31** | **83.7%** |
| 40,000 | 0.1 | 133 | 5.0% |

**AT SCALE, LONG-HORIZON SR ANSWERS THE SAME WORD TO 84% OF ALL QUESTIONS.** *That is the
constant/prototype floor's signature, and this project already knows that floor is often the
strongest thing in the room. We built a pinned equation and it converged into a baseline.*
**γ was SWEPT and the sweep is what made this legible: short horizon keeps cue-specificity (133
distinct) and still loses; long horizon destroys it. Had we ADOPTED one γ we would have learned
neither half.**

### ⚠️ WHAT I GOT WRONG, EXPLICITLY, SO IT IS NOT REPEATED
I filed SR as starved citing "median ONE successor per word" and a dose-response of
**0.00111 -> 0.00556**. *I flagged that comparison as not-a-slope because `n_read` AND `pool` both
moved.* **With the pool held FIXED the effect does not merely shrink -- it REVERSES.** The
apparent rise was the confound, exactly as flagged. **A caveat I wrote and then leaned on anyway.**

---

## 🔴 [SUPERSEDED BY THE RETRACTION ABOVE -- KEPT SO THE OVERCLAIM STAYS VISIBLE] D7 RESULT LANDED (spec `v2_sr`, 30 units, 1,564 s)
**Verdict COMPUTED by `tools/readout_verdict.py`, which encodes the pre-committed readings as code
so the reading cannot be done after seeing the table.** Held-out, 3 seeds, n=300, bar 0.0411:

| route | held-out hit@1 |
|---|---|
| SEMANTIC | 0.00556 |
| EPISODIC | 0.00444 |
| **SR (all three gammas)** | **0.00111 -- the WORST substrate route** |
| COOC floor | **0.02333** |

**Reading (e) did NOT fire: SR clears at NO gamma, so it is not even "the 1-step counter wearing a
matrix" -- it loses everywhere.** Verdict stands at **(c)+(d)**: a real negative, and the pipeline
is not reading the held-out cue.

### ⚠️ BUT FILING THIS AS "SR DOES NOT WORK" WOULD BE THE C33 ERROR AGAIN. MEASURED, NOT ASSERTED:
`scratch/sr_density.py` -- **4,596 observed transitions across 2,114 states, and the MEDIAN NUMBER
OF DISTINCT SUCCESSORS PER WORD IS 1.0.** *Half the vocabulary was seen followed by exactly one
other word.* **That is not a test of a predictive map; it is a test of an empty matrix.** For scale,
this project has twice called a channel STARVED at ~8.6 observations per word and at a median 130
arcs per word. **2.17 transitions per state is far below both.**

### 🎯 AND THE DOSE-RESPONSE IS ALREADY IN THE RUN, AS A NATURAL EXPERIMENT
The `foraging` ablation reads the full budget instead of letting the forager leave early:

| | sentences read | pool | SR_g0.9 | COOC floor |
|---|---|---|---|---|
| forager ON | 1,233 | 2,899 | **0.00111** | 0.02333 |
| forager OFF | 4,000 | 6,094 | **0.00556** | 0.01889 |

**3.2x the text moves SR 5x UP while the floor moves DOWN** (the pool more than doubled, so the
task got harder). *Exactly the direction the starvation hypothesis predicts and the opposite of
the floor's.* **⚠️ NOT a clean one-variable comparison -- `n_read` AND `pool` both changed -- so it
is DIRECTIONAL EVIDENCE, not a measured slope. State it that way or not at all.**

### 🪞 THE IRONY, AND IT IS A REAL WIRING FINDING: OUR FORAGER IS STARVING OUR SUCCESSOR MAP
H2's leave rule cut reading to **1,233 of 4,000** requested sentences. **The organ that most needs
data got the least, because another organ decided to move on.** *That is a genuine interaction
between two wired organs, and it is invisible unless both are in the same substrate -- which is
the first concrete argument this session that assembling them was worth doing.*

**FILED AS: `UNTESTABLE-AT-THIS-SCALE`, NOT `REFUTED`. Per discipline 18, if no achievable score
could clear the bar on the data supplied, the point is untestable rather than negative.**
**THE NAMED RE-TEST: rebuild SR on 10-50x the transitions and re-measure. If it still does not
move, THAT is the negative -- and it will be a real one.**

---

## 🧠 BRAIN-FIDELITY DRILL ON THE PHASE 2 NEGATIVE (owed under discipline 17) -- AND IT FOUND THE GAP
`notes/brain_fidelity_drill_memorises_but_does_not_transfer_2026-08-19.md`.

**THE REFRAME: WE MEASURED A HIPPOCAMPUS AND REPORTED THAT IT IS NOT A NEOCORTEX.** An episodic
store that recalls its own episodes almost perfectly (0.9333) and transfers nothing to a new
context (0.0044) **is behaving exactly like the structure we copied** -- pattern separation makes
similar inputs MORE distinct, deliberately. *That is D3 working, not D3 failing.* Generalisation is
the slow system's job and **the transfer mechanism between them is REPLAY.**

**THE GAP IS EMBARRASSINGLY CONCRETE AND WAS ENUMERATED ON DISK, NOT GUESSED:**
`hdlab/hippocampal_encoder.py` ALREADY CONTAINS **`cls_replay_cycle`** and
**`cls_discrete_budget_consolidate`**. A grep across `hdlab/ tools/ experiments/ verification/
notes/` returns them in **exactly two files -- their own module and one witness.**
> **NO EXPERIMENT CALLS THEM. NOTHING LIVE CALLS THEM. THE SUBSTRATE I BUILT TODAY WRITES 3,400
> EPISODES AND CONSOLIDATES NONE OF THEM.** *We replicate the fast store and substitute NOTHING
> for the slow one; the transfer step is simply absent and its organ has sat built and unused.*

**NEXT BUILD, PRE-REGISTERED WITH FOUR WAYS TO FAIL** (A consolidation is the missing step / B it
helps but is not the answer / C replay over our codes carries no transferable structure / D it
needs implausibly many replays, which is an admission the machinery is wrong). **Mandatory: a
RATE-MATCHED RANDOM-REPLAY twin**, floors rebuilt on the consolidated representation, and a
rank-matched null -- *because held-out sits BELOW its floor, and destroying information moves a
sub-chance score TOWARD chance and reads as progress.*

**🛑 AND THE DRILL CORRECTED ITSELF BEFORE THE BUILD, WHICH IS THE POINT OF WRITING IT DOWN FIRST.**
Reading `cls_replay_cycle` at HEAD: it trains `cortex_W [dg_dim, dg_dim]` on
`outer(code, settle(code))` -- **an autoassociator over the SAME sparse pattern-separated codes**,
and its own docstring calls itself a minimal self-test scaffold whose real cortex *"would receive
PROJECTED codes rather than raw DG"*. **Replaying separated codes into their own space re-learns
the separation; it cannot generalise. Running it would have produced a guaranteed null that I
would have filed as reading (C) -- a property of my choice of target, not of replay.**
***WE HAVE THE REPLAY MACHINERY AND NO CORTICAL TARGET REPRESENTATION TO REPLAY INTO.*** The slow
system's whole point is DENSE OVERLAPPING codes, so shared structure superimposes and
episode-specific detail cancels. **Corrected build: replay into the DENSE context vectors, keep
the DG-space arm as the control that CANNOT work.**
**⚠️ HONEST DEFLATION, PRE-DECLARED: a dense accumulated per-word profile is VERY CLOSE to the
`SEMANTIC` route that already read 0.005.** *If the corrected build is only "that route again, fed
by replay", it is a REPLICATION of a measured null and must not be dressed as a new mechanism. The
one real difference is the SELECTION and REPEAT structure replay imposes -- so that is the
variable, and the rate-matched random-replay twin is what isolates it.*
**⚠️ Written before the build precisely because MY LAST PREDICTION IN THIS AREA WAS REFUTED INSIDE
ONE RUN.** *That refutation tested the parallel context accumulator, which is never fed by replay,
so it does not pre-empt this -- but a second bite needs its own stated way to be wrong.*

---

## 🆕 PHASE 3 STARTED -- D7 SUCCESSOR REPRESENTATION IS BUILT: `hdlab/successor_representation.py`
**`M = (I - gamma*P)^-1`. The only slot where the brain hands us a closed form and we had written
none of it.** Five self-tests PASS, and they are can-fail rather than plausibility checks: the
defining identity `M = I + gamma*P*M` to 1e-8 across four gammas; `gamma=0` reduces to `I`;
dead rows do not make the solve singular; **a PLANTED successor is recovered above a
frequency-matched decoy that never follows the cue**; and **the online TD rule converges to the
closed form** (6.1% relative error) -- so the mechanism can be checked against the thing it is
meant to compute rather than against a hope.

**WHY THIS ONE, AND NOT JUST BECAUSE IT WAS TOP OF A LIST.** Phase 2 says the missing ingredient is
a LEARNING SIGNAL. SR supplies one that is actually admissible here: **self-supervised from the
corpus's own transitions, derived from NO gold, NO WordNet, NO LLM** -- and the circularity trap
that disqualifies almost every other supervision candidate does not touch it.

**PINNED vs OURS, stated because presenting an invention as pinned is barred:** the COMPUTATION
(discounted expected future occupancy) is PINNED. **That a "state" is a LEMMA is OUR INVENTION
UNDER TEST** -- the brain's SR runs over places. **`gamma` is SWEPT (0.1 / 0.5 / 0.9) and never
adopted**: our worst result copied a pinned NUMBER, our best copied an OPERATION.

**⚠️ THE UNFLATTERING PREDICTION, PRE-REGISTERED IN THE MODULE BEFORE ANY NUMBER: M IS A
DISCOUNTED MULTI-STEP CO-OCCURRENCE STATISTIC AND OUR FLOOR IS THE 1-STEP ONE.** If SR only wins
at small gamma it is the 1-step counter wearing a matrix and must be reported as such.

**FIRST SMOKE, AND ONE BUG WORTH KEEPING VISIBLE: SR READ EXACTLY 0.0000 IN EVERY CELL.** Not a
result -- an artifact of the equation. `M = I + gamma*P + ...`, so **the IDENTITY TERM puts every
cue word at the top of its own ranking**, and the target is masked out of the cue by construction,
so hit@1 was zero by definition. Excluding the cue's own words fixes it, **and the SAME exclusion
was applied to the COOC floor** so the arms still differ in route and nothing else.
*Smoke after the fix (n=60, nothing resolved): SR 0.25 / 0.28 / 0.20 at exact key against COOC
0.217, and 0.0167 held-out against COOC 0.083.* **SR is the best substrate-side route on held-out
text and is still losing to counting.** **FULL RUN IN FLIGHT**, `scratch/p2_full_v2.pid`.
*Unit keys carry a `SPEC_VERSION`, so the 15 already-checkpointed v1 units cannot be silently
served for a changed specification -- which is exactly what would have happened.*

---

## ✅ PHASE 2 FULL RUN LANDED (`data/exp_substrate_end_to_end_readout_v1/metrics.json`, 15 units, 605 s)
**PRE-COMMITTED READING (c) FIRED: no substrate route beats the strongest floor, and the
instrument is alive.** simplewiki, 3 seeds, n=300 items per regime, pool 2,114, chance 0.00047.

| arm | SEEN (exact key) | **HELD-OUT (the real point)** |
|---|---|---|
| EPISODIC | **0.9333** clears bar, p=0.0005 | **0.0044** -- CI upper ~0.0105, **BELOW the 0.0367 bar** |
| SEMANTIC | 0.2789 clears bar | **0.0056** -- below the bar |
| **COOC floor** (~~strongest~~ **NOT the strongest -- see below**, standalone) | 0.1700 | **0.0233** |
| FREQ floor | 0.0011 | 0.0078 |
| ORTH floor | 0.0000 | 0.0033 |
| **SCRAMBLE twin** | **0.0011**, p=0.0005 vs EPISODIC | **0.0033, p = 0.48 / 0.64 / 1.00** |

**🚨 READING (d) ALSO FIRED, ON THE HELD-OUT REGIME ONLY, AND IT IS THE HEADLINE: FEEDING THE
SUBSTRATE AN UNRELATED SENTENCE SCORES THE SAME AS FEEDING IT THE REAL ONE (0.0033 vs 0.0044,
p up to 1.00). ON NEW TEXT IT IS NOT READING THE CUE AT ALL.** *At exact key the same twin
separates at p=0.0005, so the pipeline demonstrably CAN read -- which is what makes the held-out
tie a result rather than a broken cell.*

**THE ONE-SENTENCE FINDING: THE STORE MEMORISES EPISODES ALMOST PERFECTLY (0.93 at exact key) AND
TRANSFERS NOTHING TO A NEW CONTEXT (0.004, tied with its own scramble, beaten 5x by counting).**
*And the task is NOT impossible: a co-occurrence counter reaches 50x chance on it.*
**This is ORGAN A's conclusion reached end-to-end through the assembled substrate on a different
task and a different instrument -- perfect storage, no generalisation, and the missing ingredient
is the learning signal. Assembly did not supply it, and was never going to.**

### ABLATIONS -- TWO ORGANS CONTRIBUTE EXACTLY NOTHING, AND ONE ARM IS VOID
| ablation | effect |
|---|---|
| `definitions` (R1) | **ZERO change in EVERY number, both regimes, all 3 seeds.** |
| `gap_detector` (H1) | **ZERO change** -- and already known to be untestable while the foundation is near-empty. |
| `episodic` (D3) | exact-key 0.9333 -> **0.0000**. It IS the organ doing the memorising. Held-out 0.0044 -> 0.0000: nothing to lose. |
| `foraging` (H2) | **VOID IN THIS RUN -- DO NOT READ IT.** |

**⚠️ THE FORAGING ARM IS UNMATCHED AGAIN, IN THE OPPOSITE DIRECTION, AND IT IS THE SAME DEFECT I
"FIXED" ONE CONTINUATION EARLIER.** The forager LEFT its patch after **1,233** of 4,000 requested
sentences; my frozen quota is the whole budget, so FROZEN read **4,000**. *Last time frozen read
too LITTLE; I matched on the budget instead of on what the live arm actually consumes, and it now
reads too MUCH.* **FIX: run the live arm FIRST, then give the frozen twin exactly its sentence
count.** *Twice in two days on the same control. Rate-matching is not a step to add at the end.*

---

## 🧪 PHASE 2 CELL BUILT AND SMOKE-CLEAN: `experiments/exp_substrate_end_to_end_readout_v1.py`
**FULL RUN IN FLIGHT** on `simplewiki`, detached, PID in `scratch/p2_full.pid`, logs
`scratch/p2_full.out` / `.err`, 3 seeds x 5 ablations = 15 checkpointed units -> `data/<cell>/`.
**DO NOT RESPAWN IT** -- a duplicate is the more expensive error.

### 🚨 PHASE 2 FINDING #2 -- THE OBVIOUS SCRAMBLE CONTROL IS A NO-OP, AND IT TIED THE REAL CUE EXACTLY
**A word-ORDER scramble against a BAG-OF-WORDS cue is the same vector.** Measured: shuffled cue
`hit@1 0.7` vs real cue `0.7`, **permutation p = 1.0000**. *That is not a weak control, it is a
no-op wearing a control's name* -- the same class as the corruption control that was
near-rank-preserving and "incapable of failing", and as the coverage control that dropped 0 of 242.
**Pre-committed reading (d) fired on it as designed, which is the only reason it was caught.**
**THE FIX, AND IT IS THE RECIPE THE READING LOOP ALREADY OWNS** (`scramble_context_source`):
destroy the cue's CONTENT, not its ORDER -- swap in an unrelated sentence, keeping the target.
**Rebuilt that way it BINDS HARD: exact-key EPISODIC 0.667 vs SCRAMBLE 0.017, perm p = 0.0005.**
**🔎 LEAD CHASED, AND IT IS GOOD NEWS -- THE DEFECT IS NOT WIDESPREAD. `tools/scramble_control_audit.py`.**
Enumerated by `os.walk` over `experiments/ hdlab/ tools/ verification/`, **all 13,553 `.py` files,
no sampling, rows-scanned printed before results.** Of 66 files that declare a scramble control AND
carry an order-invariant scorer: **HIGH = 0**, 26 already use the CORRECT content-destroying
recipe, 23 CHECK (they scramble by a route the token regex cannot see -- index arrays, `sample` --
and need reading), 17 declare a scramble with no visible shuffle (several are prose mentions).
**No landed cell pairs a word-order shuffle with a bag scorer and nothing order-sensitive. The
defect was mine, in a cell written today, and it did not propagate.**
***SCOPE OF THAT ABSENCE CLAIM, STATED: `HIGH` requires the word "scramble" to appear. A cell that
scrambles without naming it would not be seen.*** *The tool's own first version keyed on the
shuffle's TARGET NAME and found 1 file in 13,553 -- it would have reported this defect as absent
because my regex was narrow, not because the code was clean. Rebuilt LABEL-FIRST, and the
self-test now asserts it still catches a shuffle of an INDEX ARRAY.*

### ✅ AND THE UNBIASED ITEM SELECTION MOVED THE FLOORS EXACTLY AS PREDICTED
Replacing "first known lemma" with a seeded RANDOM known lemma dropped the COOC floor from
**0.255 to 0.083** -- confirming the selection bias I named was inflating it. **The substrate did
not benefit: both its routes read 0.000 on held-out cues under the fair selection.** *At smoke n=60
the margin vs floor is `perm p = 0.065`, so this is a WIDTH, not yet a resolved negative. That is
what the full run is for.*

---

## 🚨 [SUPERSEDED TWICE -- READ THE TWO CORRECTIONS BEFORE THE NUMBERS] PHASE 2 FINDING #1 -- THE ASSEMBLED SUBSTRATE LOSES TO WORD-COUNTING BY ~10x ON HELD-OUT TEXT
> **⛔ SUPERSEDED-BY, added 2026-08-19 rather than left for the next reader to trip over:**
> **(1) THE "~10x" IS AGAINST THE WRONG FLOOR.** `COUNT_FLOOR` is NOT the strongest floor the data
> supports -- cosine over the SAME co-occurrence counts scores **0.0300 against its 0.0125**. The
> real gap is LARGER, not smaller. See the diagnostic block above.
> **(2) THE CONSOLIDATION ORGAN NEVER FIRED IN THIS CELL.** It ran `max_patches=1`, and the
> substrate only consolidated when the forager changed corpus, so **every Phase 2 run grounded
> NOTHING**. The retrieval result stands -- both routes read from episodic writes and Library
> traces, which happen regardless -- but the ablation table must be re-run before it is quoted.

**The first end-to-end measurement of the assembly, and it is a clean negative that INDEPENDENTLY
REPLICATES THIS PROJECT'S CENTRAL DOCUMENTED RESULT on a different task, a different instrument
and a different route.** `scratch/recall_route_compare.py`, 400 sentences read, 200 items,
pool 996, one corpus, one seed. **No CI yet, so these are measurements and not yet a verdict.**

| route | SEEN (exact key) hit@1 | **HELD-OUT hit@1** |
|---|---|---|
| EPISODIC (DG code overlap after CA3 settling) | **0.795** | **0.025** |
| SEMANTIC (cosine to the accumulated context profile) | 0.165 | **0.005** |
| **COOC floor** (raw co-occurrence counting) | **0.320** | **0.255** |
| **FREQ floor** (ignores the cue entirely) | 0.170 | **0.265** |

**⛔ NEVER QUOTE 0.795 AS A CAPABILITY.** The cue at exact key IS the vector the episode was
written from -- the same write-then-read-a-register shape that refuted
`exp_causal_link_comprehension_fuller_v2` ("no comprehension was tested"). **It is a CEILING
DIAGNOSTIC and it is doing one useful job: it proves the store, the encoder and the scorer all
work, so the held-out collapse is a REAL NEGATIVE and not a broken instrument.**

**THE NUMBER THAT MATTERS: on sentences it never read, the substrate scores 0.025 where COUNTING
WORDS SCORES 0.255, and where a floor that DOES NOT LOOK AT THE CUE AT ALL scores 0.265.**

### ❌ AND MY OWN BRAIN-FIDELITY PREDICTION WAS REFUTED IN THE SAME RUN, BEFORE IT COULD BE QUOTED
I predicted the episodic collapse was us asking the WRONG ORGAN -- the dentate gyrus exists to make
similar inputs DISSIMILAR, so pattern separation is the enemy of generalisation, and the
consolidated semantic route should therefore do better. **IT DOES NOT. SEMANTIC IS 5x WORSE THAN
EPISODIC ON HELD-OUT CUES (0.005 vs 0.025), and raw co-occurrence counting beats it in BOTH
regimes, including at exact key (0.320 vs 0.165).** *The elegant story was wrong and its own
control killed it inside one run. Recorded because the reasoning will look attractive again.*

### 🎯 WHAT IT ACTUALLY CONVERGES ON, AND THIS IS THE VALUABLE PART
**Our "semantic profile" is a SUM of context bags, and it is beaten by literally counting the same
co-occurrences.** That is exactly the ORGAN A write-rule result -- summing raises interference,
single-occurrence beats the sum, and no unsupervised transform extracts substitutability --
**reached again end-to-end through the assembled substrate on a retrieval task, rather than on the
dissociation instrument.** *Two instruments, two tasks, two populations, one diagnosis: the
missing ingredient is the LEARNING SIGNAL, and assembling the organs did not supply it.*

**CAVEATS THAT TRAVEL WITH EVERY NUMBER ABOVE:** n=200, ONE corpus (children's fiction), ONE seed,
NO confidence interval and NO null yet -- that is what the Phase 2 cell is for. **And a named
selection bias: items are the FIRST content lemma of each sentence that the store has seen, which
skews toward frequent words and INFLATES both floors.** *It does not rescue the mechanism -- the
gap is ~10x, not marginal -- but the cell must select items without that bias.*

---

## 🔬 PHASE 2 IN PROGRESS -- THE ABLATION HARNESS EXISTS AND IT HAS ALREADY PAID FOR ITSELF

`Substrate(ablate=[...])` supports four one-organ-at-a-time ablations. **Smoke run, 400 sentences,
2 corpora, one seed -- OBSERVATIONS, NOT RESULTS: no CI, no null, n=1, and they are not to be
quoted as findings until the cell runs.** They already change what to build.

| ablation | what moved | reading |
|---|---|---|
| `episodic` (D3 off) | **ONLY its own counter** (3400 -> 0) | **I WIRED THE EPISODIC STORE AS A WRITE-ONLY SINK.** 3,400 encounters written, nothing reads them. Provenance, refusals, profiles all bit-identical. *This is MY wiring defect, not the organ's -- `hippocampal_encoder.retrieve` exists and I never call it.* **BUILD TARGET.** |
| `definitions` (R1 off) | **ONLY its own counter** (5 -> 0) | the `definition_map` handed to `checkpoint()` changed NOTHING about what grounded. **Under-powered on fiction (5 definitions in 400 sentences) -- re-run on SimpleWiki before concluding anything.** |
| `gap_detector` (H1 off) | **NOTHING AT ALL** | **AND IT IS UNINFORMATIVE, NOT A NULL -- READ THE NEXT BLOCK BEFORE QUOTING IT.** |
| `foraging` (H2 off, rate-matched) | 7 of 8 counters | **FROZEN reads the SAME 400 sentences and grounds 9 where the forager grounds 19.** It touches MORE lemmas (1,320 vs 1,137) and grounds FEWER -- spreading thinner, which is what MVT says foraging avoids. |

**⚠️ THE H1 ABLATION CANNOT SUCCEED AND MUST NOT BE FILED AS A NEGATIVE.** Verified rather than
assumed (`scratch/gapcache_values.py`): the real detector and a stub that always answers GAP agree
on **all 1,137 shared lemmas, zero disagreements**. The 19 lemmas the cache marks known are
**exactly the 19 grounded words**, written back by the consolidation path, not by the detector.
**But the foundation starts with 107 seed words and nothing else, so every content word in
children's fiction genuinely IS a gap. The detector is answering correctly; the question has one
true answer at this scale.** *Discipline 17's first clause: establish the experiment could have
succeeded before concluding anything from it.* **RE-TEST H1 AGAINST A POPULATED FOUNDATION.**

**AND TWO OF MY OWN CONTROLS WERE DEFECTIVE BEFORE THEY WERE FIXED, WHICH IS THE POINT OF RUNNING
CONTROLS ON CONTROLS:**
1. **The foraging twin was NOT rate-matched.** A fixed harvests-per-patch constant let FROZEN read
   **150 sentences against the forager's 400**, so every downstream difference was attributable to
   reading LESS rather than to choosing worse. **That is the unmatched-twin defect that killed four
   apparent wins in this project's own record, rebuilt from scratch by me.** Now splits the same
   budget across the same patches; both arms read exactly 400.
2. **Ablating H1 by setting `state.gap_detector = None` CRASHED** (`is_gap` calls `.familiarity()`
   unconditionally) -- and would have been the wrong control anyway, since removing the call
   changes the PATH rather than the ANSWER. Replaced by a stub with the interface intact and the
   discrimination removed.

---

## PHASE 2 -- THE RISK, AND IT IS THE MOST IMPORTANT STEP IN THIS PLAN

**EVERY ORGAN HERE WAS VALIDATED IN ISOLATION. WIRING TEN TOGETHER IS PRECISELY HOW THE 0-FOR-30
CLAIMS LAYER HAPPENED -- components that each look fine and produce nothing jointly.**

**THE DELIVERABLE IS ONE CELL: `experiments/exp_substrate_end_to_end_readout_v1.py`.**
Per CLAUDE.md this is `hdi_exp_dev`'s lane; if agent dispatch is unavailable in the running session,
author it in the main thread **with every gate below intact** -- the gates are the point, the lane
is not.

**The gates, and none is optional:**
- text in, traceable facts out, **on a corpus the mechanism did not see**;
- **a REAL floor run STANDALONE** -- the dumbest thing that scores well on this data. Run the
  STRONGEST floor the cell's own data supports, not the most convenient one. Report how many items
  each control actually removed: **a control that excludes nothing is not a control.**
- **a scramble twin** -- if scrambled text produces the same output, the pipeline is not reading;
- **CI half-width AND the null p95 beside every margin**, and gate on the FLOOR'S UPPER BOUND
  (floor + its own half-width), never its point value;
- **an ORGAN-ABLATION arm per wired organ** -- turn one off, re-run, report the delta. *This is the
  only thing that distinguishes an assembled substrate from an expensive `Counter`, and no cell in
  this archive has ever run it.*
- **and the first question, free and non-statistical: DID THE TEST ITEMS EXIST BEFORE THE MECHANISM
  DID?** State the answer in the metrics. That predictor beat every statistical signal in the audit.

**PRE-COMMIT THE READINGS BEFORE ANY NUMBER EXISTS:** (α) beats the floor CI-separated AND at least
one ablation degrades it -> the assembly is doing work, name which organ. (β) beats the floor but NO
ablation moves anything -> **the floor is what is scoring, the organs are decoration** -- report it
that way, do not soften it. (γ) does not beat the floor -> a real negative; go to the brain-fidelity
drill (discipline 17), and ask FIRST whether the experiment could have succeeded at all.

**This test does not currently exist. Nothing downstream should be trusted until it does.**

---

## PHASE 3 -- BUILD THE EMPTY SLOTS (this is where the real gain is)

Ranked. **The first is the only slot where the brain hands us a closed form and we wrote none of it.**

1. **D7 successor representation -- EQUATION FULLY PINNED: `M = (I - gamma*P)^-1`.** Highest
   value-per-effort in the document.
2. **Q2 domain-general inference -- EMPTY, and it is a WHOLE NETWORK.** `multi_hop`'s default
   `beta = n_dim` collapses its softmax to a Dirac delta (identical to argmax); its own code says
   two prior cells were confounded by this. **This explains `reasoner` matching a similarity
   baseline on 38 of 40 questions -- not a broken reasoner, a missing network.**
3. **P1/P2 answer production -- EMPTY.** `generation.py` returns codebook INDICES: no lemma stage,
   no morphology, no string. Its docstring admits its test regime "cannot fail by construction."
   **This is the slot the no-LLM invariant created and nobody wrote down.**
4. **D5 working memory -- EMPTY, and the filename is a trap.** `working_memory.py` is 116 lines of
   assertion guards, and it is LIVE.
5. F5 coherence monitor, F6 multi-sentence integration.
**NOT a build target: E4 discourse bridging** -- two measured nulls, one the owner's own mechanism,
CI-separated BELOW neighbour-copying.

**FREE LEAD, hypothesis-pending-VET:** `information_foraging.SurpriseSegmenter` (`:194-224`) is a
literal Event Segmentation Theory boundary detector **already built**, sitting in a module nobody
imports, never run on discourse. It fills the "no prediction-error segmentation" gap the organ map
lists as missing.

---

## ✅ MIDDLE_BAND MINED -- `tools/middle_band_miner.py`. TWO CORRECTIONS TO THIS PLAN'S OWN PREMISE.

**CORRECTION 1 -- THE POPULATION IS 580, NOT 117.** Enumerated by walking **all 8,148 result
directories** under `data/` (the 117 figure came from the index's `data/exp_*` scan; results also
live under `data/results`, `data/lambda_batch_results`, `data/skypilot_results` and ~60
`substrate_*` directories). **Meaning-relevant MIDDLE_BAND: 580. HARD_PASS: 1,359.**

**CORRECTION 2 -- AND IT IS THE ONE THAT MATTERS, BECAUSE THE OWNER AUTHORISED WORK ON THIS
RATIONALE. THE STATED MECHANISM IS NOT SUPPORTED.** This plan said MIDDLE_BAND "is where the
HONEST SELF-ASSESSMENTS went". Measured with the **IDENTICAL detector on both tiers** (same
directories, same fields, only the tier pattern differs -- a cross-tool comparison would have been
the very thing discipline 11 forbids):

| property | MIDDLE_BAND | HARD_PASS | |
|---|---|---|---|
| **states a limitation about itself** | **4.5%** | **3.0%** | **NO REAL DIFFERENCE -- the stated rationale fails** |
| carries a CI | 10.3% | 5.4% | MB nearly 2x |
| carries a floor | 76.4% | 69.2% | MB higher |
| carries a scramble | 24.1% | 19.5% | MB higher |
| carries a held-out split | 23.6% | 20.2% | MB higher |
| carries a null | 4.0% | 2.7% | no real difference |

**SO THE PREMISE IS HALF RIGHT AND THE HALF THAT SURVIVES IS NOT THE HALF WE ARGUED.** MIDDLE_BAND
IS modestly better-evidenced -- **twice as likely to carry a confidence interval** -- but **it is
NOT a population characterised by honest self-assessment: 4.5% is not a culture of caveats, it is
a rounding error, and HARD_PASS is at 3.0%.** *The mining stays worth doing on the evidence
gradient. The story we told about WHY must not be repeated.*

**THE READ LIST IS RANKED BY HOW MUCH MECHANISM IS IN THE CELL, and the top of it is substantive:**
`exp_bootstrap_passage_context_binding_fade_v4` (discourse-level passage-context binding under a
fairness lockdown), `exp_agreement_attractor_role_binding_cg_viability_v1` -- **whose own
`honest_scope` names its real discriminator and rejects the trivial one**: *"Beating nearest-noun
is trivial here... the HONEST discriminator is beating the FIRST-NOUN positional heuristic on the
subject-not-first subset"* -- and `exp_grounding_quality_readout_v1`, which opens its limitations
with ***"THIS CELL MEASURES NO QUALITY."*** *Those three are exactly the honesty the premise
predicted; the measurement says they are the 4.5%, not the norm.*

**NOTHING MINED HERE IS CITABLE.** `tools/vetting_ledger.py --cite` still governs and still
refuses every one of them.

---

## PARALLEL TRACK -- MINE MIDDLE_BAND (owner: "it's worth it")

**117 meaning-relevant cells, never read.** Owner's framing, and it changes the brief:
*"understanding what it was trying and the signal may be very important for the harder to obtain
capabilities."* **READ FOR THE ATTEMPT AND THE SIGNAL, NOT FOR THE VERDICT.**
**Why this population and not HARD_PASS: selecting on HARD_PASS SELECTED FOR OVER-CLAIMING.** Two
cells were found whose honest tier was MIDDLE_BAND while an over-claimed sibling took HARD_PASS.

---

## DEFERRED, WITH A TRIGGER

**Instrument rebuild.** Both bars carry CIs including chance (0.5431 CI [0.4922, 0.5953]; 0.5943 CI
[0.4937, 0.6911]); at n=242 the half-width (~0.05) is as large as the whole chance-to-bar interval
(~0.04). **Nothing in Phases 0-3 uses it.** **TRIGGER: rebuild before the next GATED WORD-MEANING
experiment.**
***AND THE DEEPER POINT, WORTH MORE THAN THE POWER FIX: PREFER TASKS WITH LARGE EFFECT SIZES OVER
BUYING POWER ON A TASK WITH A TINY ONE.*** When a mechanism genuinely works you see pattern
completion **0.20 -> 0.92**, or **leave@3 vs leave@8 on an identical patch**. No CI needed. A whole
day of gated word-meaning arms fought over **0.63 vs 0.55** -- that gap is the problem, not n.

---

## STANDING RULES THAT MUST SURVIVE COMPACTION

- **`tools/substrate_query.sh` RETURNS ZERO BYTES AND EXITS 0.** Use `tools/experiment_index.py`,
  which prints rows scanned BEFORE results.
- **A HARD_PASS is an UNVERIFIED CLAIM** (30 vetted, 1 upheld). Check `tools/vetting_ledger.py
  --cite NAME` before citing anything.
- **The organ layer is a DIFFERENT population** -- 163/163 import, 83/87 self-tests pass. Do not
  import the claims base rate into it.
- **AN ABSENCE CLAIM REQUIRES AN ENUMERATION, NEVER A SEARCH.** Four of my errors this session were
  this one fault.
- **ASK WHAT THE OPERATOR INTENDED BEFORE NAMING SOMETHING A DEFECT.** The remote is idle BY INTENT;
  results were deliberately SSH'd back. I called both defects.
- Never bundle a deletion with real work. Never `git add -A`. `data/foundation/` is READ-ONLY, one
  disk, no backup. Origin push needs USER AUTH.
