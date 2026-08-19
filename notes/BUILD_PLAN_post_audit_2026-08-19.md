# BUILD PLAN -- WHAT TO DO NEXT, POST-AUDIT. START HERE.

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

## PHASE 1 -- WIRE THE SUBSTRATE (Tier 0 + Tier 1). **IN PROGRESS.**

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
