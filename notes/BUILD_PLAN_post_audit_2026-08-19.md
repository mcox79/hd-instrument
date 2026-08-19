# BUILD PLAN -- WHAT TO DO NEXT, POST-AUDIT. START HERE.

**Written 2026-08-18 end of session, at the owner's direction, to be executed after compaction.**
Supersedes the forward-looking parts of `PLAN_ORGAN_STEP_LADDERS_2026-08-17.md`. Its Section 7
(the audit findings) and Section 6 (the ladder METHOD) both still stand as reference.

## THE DECISION THIS PLAN IMPLEMENTS

**Owner:** *"we need to have a current best substrate... we should envision a complete substrate (or
close to) and wire in the best versions of each."* Plus: **mine MIDDLE_BAND**, **parity is
interesting**, and the instrument rebuild is **deferred on the Director's recommendation**.

**Director's recommendation, accepted into this plan: WIRE TIER 0+1, THEN SPEND THE EFFORT ON THE
EMPTY SLOTS, NOT ON POLISHING THE FILLED ONES.** Assembly alone produces a well-organised filing
system. The two empty slots -- **inference** and **producing an answer in words** -- are the
difference between that and something that understands.

---

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

## PHASE 1 -- WIRE THE SUBSTRATE (Tier 0 + Tier 1)

Order from `notes/COMPLETE_SUBSTRATE_DESIGN_2026-08-18.md`:

**Tier 0 (reading):** `corpus_registry` -> `information_foraging` -> `definitional_extraction`
**Tier 1 (memory):** `hippocampal_encoder` -> `ca3_completer` -> `prelim_tier` -> `foundation_persistence`
**Tier 2 (comprehension):** `coreference_resolver` -> `situation_model_accumulate`; `semantic_parser` -> `cortex`

**Cost ~75 s one-time import**, dominated by `definitional_extraction` -- and after 0.1,
`situation_reader` is affordable too.

**WIRE ONLY THE INTERSECTION of self-test-passing AND probe-FUNCTIONAL.**
**⛔ DO NOT WIRE:** `atom_consultation` (`applied` hard-coded `False` -- cannot change a decision),
`definitional_predicate_v61` (fires on 0.27% of its intended population), `goal_achievement`'s
desiderative-negation channel (7/7 on authored exemplars, 4/7 on paraphrases; also the one genuine
self-test failure: `AssertionError: channel 'relation:recur' != 'majority'`). **All three are
self-test-passing. That is exactly why the intersection rule exists.**

---

## PHASE 2 -- THE RISK, AND IT IS THE MOST IMPORTANT STEP IN THIS PLAN

**EVERY ORGAN HERE WAS VALIDATED IN ISOLATION. WIRING TEN TOGETHER IS PRECISELY HOW THE 0-FOR-30
CLAIMS LAYER HAPPENED -- components that each look fine and produce nothing jointly.**

**Before believing the assembled substrate does anything, build ONE end-to-end can-fail test:**
- text in, traceable facts out, on a corpus the mechanism did not see;
- **a REAL floor run standalone** -- the dumbest thing that scores well on this data;
- **a scramble twin** -- if scrambled text produces the same output, the pipeline is not reading;
- **CI + null + the strongest floor**, per the standing bar;
- **and the first question, free and non-statistical: DID THE TEST ITEMS EXIST BEFORE THE MECHANISM
  DID?** That predictor beat every statistical signal in the audit.

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
