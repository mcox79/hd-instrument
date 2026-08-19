# PLAN -- SECTION 7: WHAT THE 2026-08-18 AUDIT CHANGED, AND WHAT IS LEFT

**READ THIS BEFORE `PLAN_ORGAN_STEP_LADDERS_2026-08-17.md` SECTION 6.** Section 6 is the ladder
method and it stands. But the RESULTS it reasons over have since been audited, and most of them did
not survive.

## 7.1 THE ONE-LINE POSITION

**Of 30 claimed HARD_PASS results vetted across five independent passes: 13 REFUTED, 4 SUSPENDED,
12 QUALIFIED, 1 UPHELD.** Full record with dispositions: `notes/VETTING_LEDGER.md`
(`python tools/vetting_ledger.py --cite NAME` answers "may I use this, and with what attached?").

**The single upheld result:** `exp_agreement_depth_productivity_generalization_v1` -- a learned
function-word accumulator supervised ONLY on depth<=1, scoring 0.7324 [0.7154, 0.7494] on 2,597
HELD-OUT depth>1 items against a majority floor of 0.5741 (upper 0.5931); margin **+0.1223 read from
the CI LOWER bound**; still holds at depth 4+ (0.6810 [0.6462, 0.7111]); scramble changes 86.5% of
decisions; split asserted in code. **Its ceiling travels with it: it TIES the hand-written recursive
rule (0.7312) rather than beating it. Parity, not supremacy.** Registered `WIRE`.

## 7.2 WHY SO MANY FAILED -- CAUSE, MEASURED

`tools/verdict_evidence_gate.py --census`, across all 7,788 landed results:

| of 2,678 HARD_PASS | count | share |
|---|---|---|
| carries a confidence interval | 28 | 1.0% |
| carries a null / permutation | 369 | 13.8% |
| carries BOTH | **13** | **0.5%** |
| **EVIDENCE_INSUFFICIENT** | **2,665** | **99.5%** |

**99.5% of our claimed passes cannot be checked from their own files.** The 0-for-30 was not bad
luck -- it was sampling a population where the evidence mostly is not there.

**THE STRONGER PREDICTOR, AND IT IS FREE: DID THE TEST ITEMS EXIST BEFORE THE MECHANISM DID?**
Every survivor was scored on items built independently of the rule. Every pass-5 refutation had its
detectors authored against the very items it was scored on -- one docstring names the exact token
pair its rule was written for. **Ask this BEFORE any statistic.**

## 7.3 THE EIGHT FAILURE PATTERNS, EACH FOUND AT LEAST TWICE

1. **The answer is written in.** A causal-link organ re-ran to a BIT-IDENTICAL 0.9722 with its gold
   links replaced by RANDOM PAIRS. It measured write/read fidelity, not comprehension.
2. **A stronger floor was computable from the cell's own data** and a weaker one was used --
   attestation 1.0000 vs treatment 0.6898; bag-of-words 12/12; a 12-line `Counter` reproducing 8/8.
3. **The gate could not fail** -- treatment a strict superset of baseline by construction, or
   separation margins set to literally 0.0.
4. **"N seeds" that are one measurement** -- bit-identical per-seed numbers because nothing depended
   on the salt.
5. **Tiny-n p-values that are resample degeneracy** -- a "p=0.000" that was (2/7)^7 over SEVEN pairs;
   exact McNemar gave 0.0625 and failed its own alpha.
6. **A "held-out" set that is not held out** -- 16 held-out words sharing ONE hand-written tag vector
   with the seeds, so held-out similarity was exactly 1.0000.
7. **A cited baseline that does not exist as quoted** -- 0.30 cited from a file that reads 0.6000 and
   postdates the run.
8. **A baseline tuned until it failed** -- a comment records sweeping distractor density for "the
   smallest min_dist that keeps mr_control >= the can-fail floor while driving mr_integration to
   0.0000".

## 7.4 "ARE THERE OTHER EXPERIMENTS WE MISSED?" -- YES, ABOUT 5,000 CELLS

Vetting looked ONLY at HARD_PASS. The index holds 8,834 cells:

| population | count | meaning-relevant | status |
|---|---|---|---|
| HARD_PASS | 2,678 | 236 | 30 vetted, 1 upheld |
| **MIDDLE_BAND** | **1,068** | **117** | **NEVER EXAMINED** |
| **NO VERDICT** | **1,265** | -- | **NEVER EXAMINED** |
| **unclassified verdict vocabulary** | **2,007** | -- | **NEVER EXAMINED** |
| **AUTHORED, NEVER LANDED** | **1,042** | **121** | built and never run -- unproven, NOT refuted |
| HARD_FAIL | 1,369 | -- | correctly negative |

**THE SELECTION BIAS, AND IT IS THE SHARPEST FINDING OF THE WHOLE AUDIT: BUILDING THE QUEUE FROM
HARD_PASS SELECTED FOR OVER-CLAIMING.** Two cells were found this session whose HONEST tier was
MIDDLE_BAND: `exp_outcome_valence_goal_congruence_v2` (reaches 1.0 at N=22 and self-tiered
MIDDLE_BAND -- the tier its over-claimed v1 sibling should have had), and
`exp_context_vector_signal_v1` (prereg-literal tier MIDDLE_BAND; its HARD_PASS was awarded POST-HOC
after the pre-registered ceiling guard fired and was amended away).

**MIDDLE_BAND MAY HOLD BETTER SCIENCE THAN HARD_PASS, BECAUSE IT IS WHERE THE HONEST
SELF-ASSESSMENTS WENT. 117 meaning-relevant MIDDLE_BAND cells have never been read.**

**⚠️ CORRECTION, OWNER-PROMPTED, 2026-08-18 -- "NEVER LANDED" IS A LOCAL-DISK CLAIM AND I
STATED IT AS A FACT ABOUT THE WORLD.** The owner: *"I would be very surprised if those were never
run - many experiments were run on the remote desktop."* They are right. Measured immediately after:

- **1,193 distinct cell names appear in the local remote-queue caches** -- 451 in
  `data/_cache_remote_cpu_queue.json`, 752 in `data/_cache_remote_gpu_queue.json` -- and **112 of
  those are cells this index called NEVER LANDED. THEY WERE DISPATCHED.** A configured remote host
  exists (`marsh@home...`, in `tools/queue_add.sh`).
- **30 more have a `metrics.json` under a DIFFERENT LOCAL DIRECTORY NAME.** My index only scanned
  `data/exp_*`; results also live in `data/results`, `data/lambda_batch_results`,
  `data/skypilot_results`, `data/tier4_llama_results`, and roughly 60 `substrate_*` directories
  carrying no `exp_` prefix at all.
- **The queue caches are SNAPSHOTS, not a dispatch history, so 112 is a FLOOR, not a count.**

**RESOLVED SAME DAY BY GOING TO THE REMOTE (owner-authorised; orchestrator `a74e56c2`, commit
`752bd5b04`). BOTH OF US WERE PARTLY RIGHT, AND THE MAGNITUDE WAS MINE.**
The remote (`marsh@home`, repo at `C:/dev/hd-instrument`) is reachable and holds **4,424
`metrics.json`, dated 2026-05-20 to 2026-08-01**, enumerated by `os.walk` on the REMOTE FILESYSTEM
rather than from any queue file or manifest.

| | count |
|---|---|
| present on remote AND locally | 4,409 |
| **present ONLY on the remote** | **15** |
| present only locally | 3,465 |

**Run two ways -- strict path match and a name-variant matcher covering all four alternate result
roots -- both give remote-only = 15 exactly, with ZERO records rescued by variant matching. It is
not a naming artifact.** All 15 recovered (68 files, 404 KB), additively, nothing overwritten,
nothing deleted, `data/foundation/` untouched. 1.13 GB of checkpoints deliberately left on the
remote: model weights, not results.

**THE OWNER'S INSTINCT FOUND A REAL DEFECT, AND IT IS THE NASTY KIND.** One directory held 8 local
files including 20 MB of checkpoints but **NO `metrics.json`** -- **the sync is partial at the FILE
level inside an otherwise-present directory, which is the version that LOOKS COMPLETE.**

**BUT THE "NEVER RUN" FIGURE SURVIVES ESSENTIALLY INTACT, AND THAT WAS MY CLAIM TO DEFEND OR DROP:**
of the 142 queue-named cells with no local result, **140 have no `metrics.json` ON THE REMOTE
EITHER**; the 2 apparent hits are matcher coarseness and are present locally. **Remote results we
were not counting existed -- there were 15, not 1,042.**

**RECOVERED SUBSTANCE (claims, NOT results -- 30 vetted claims produced 1 upheld, so these enter the
queue, not the record):** only 5 of 15 are `run_mode=full`; 6 are selftest/smoke/gate-only and 2
crashed. The five: `exp_relational_readout_promote_v1` HARD_PASS_MAJORITY, two
`exp_gated_fusion_text_grounding_encoder_seed_*` single-seed passes, and
`exp_scale_meaning_learn_arc_heldout_v3_grounding` / `_v4_breadth` -- both **HARD_FAIL**
(NO_TRANSFER, DATA_LEVER_REFUTED).

**~~SEPARATE FINDING: the remote has produced nothing in 17 days.~~ ANSWERED BY THE OWNER
IMMEDIATELY: "idle by intent." NOT a silent stall, NOT the scheduled-task failure class. Closed.**

**AND THE OWNER SUPPLIED THE MISSING HALF OF THE DIFF: "a lot of these results were SSH'd back to
this laptop."** That explains the **3,465 local-only** results, which I had reported as a bare
asymmetry without accounting for it. **The laptop is not a partial mirror of the remote -- IT IS THE
DESTINATION, deliberately pulled back.** So the sync picture is much healthier than the raw diff
implies: **one file-level gap in one directory, against 4,409 matched and 3,465 deliberately
repatriated.** *I framed a working process as a possible failure twice in the same report -- the
17-day gap and the local-only surplus -- and the owner corrected both. **Ask what the operator
INTENDED before naming something a defect.***

**THE HONEST STATEMENT: 1,042 cells have no local result at the expected path. AT LEAST 142 of
those did run or were shipped to run. THE TRUE NUMBER NEVER RUN IS UNKNOWN AND LOWER.** Settling it
requires SSH to the remote and a metrics sync, which is the orchestrator lane and needs owner
authorization. *This is the same error class the audit exists to catch -- an absence claim made from
a search rather than an enumeration -- committed by me while cataloguing it in others.*

**And 121 meaning-relevant cells have no local result** -- unproven rather than refuted,
including a cross-channel independence gate with a trap arm whose FULL never landed.

## 7.5 THE ORGAN LAYER IS A SEPARATE POPULATION AND MUST NOT BE JUDGED BY 7.1

**Owner, 2026-08-18: "we made a lot of effort to build fully functional organs and we should make
sure we're working off of that significant effort."** That is correct, and it corrects the
Director's focus: the audit had been checking CLAIMS and had never inventoried the MACHINERY.

`hdlab/` holds **147 modules, 3,153,917 bytes**; **~82 carry a self-test** -- NOT the 31 the Director
first reported, which was a too-narrow regex; 81 independently matches
`notes/system_accounting_2026-08-13.md`. **An experiment's claim can be refuted while the organ it
exercised is perfectly good machinery. The claim base rate says NOTHING about the organ layer.**

**IN FLIGHT:** a runtime accounting of all 147 -- isolated import, self-test execution, and live
closure by `sys.modules` inspection. **NOT grep**, which is wrong in BOTH directions here: three live
modules are lazy imports inside function bodies (invisible to grep), and two grep "hits" are a string
constant and a comment. Target: `notes/ORGAN_ACCOUNTING_2026-08-18.md`, verdicts
LIVE_AND_WORKING / GOOD_BUT_UNUSED / BROKEN / CONSTANT_OR_STUB / SCRATCH_REMOVE.

**THE DELIVERABLE THAT MATTERS IS GOOD_BUT_UNUSED.** This project's own record says 33 modules
self-test PASS, are registered WIRED, and are ABSENT FROM THE LIVE CLOSURE -- built, working
capability the substrate is not standing on.

*Hygiene already visible: `hdlab/_scratch_orig_goal_owner_select.py` is 55 KB, lives in the durable
organ directory, and is REGISTERED as a capability.*

## 7.5b THE DASHBOARD IS STALE, AND IT IS SHOWING THE OWNER UNVERIFIED NUMBERS AS RESULTS

**Measured 2026-08-18: ZERO of today's five artifacts are referenced in `tools/status_gui.py`,
`tools/status_state.py` or `tools/inflight_monitor.py`.** Not the vetting ledger, not the organ
accounting, not the experiment index, not the evidence gate.

**THE ACTIVE HARM, not merely a gap: tabs `4. SCORES` and `7. LATEST RESULTS` render verdict strings
straight from `metrics.json`. We now know 99.5% of those cannot be checked from their own files and
that 30 vetted produced 1 upheld. THE DASHBOARD IS PRESENTING CLAIMS AS RESULTS, and it is the
owner's primary window into the project.** `inflight_monitor.py` has not been touched since 07-28.

**MINIMUM FIX (not a redesign):**
1. Every verdict shown must carry its LEDGER DISPOSITION beside it -- `WIRE` / `WIRE_NARROWED` /
   `RERUN_NAMED` / `SHELVED_REFUTED` / **`UNVETTED`**. `tools/vetting_ledger.py --cite` already
   answers this and already refuses unknown cells.
2. **`UNVETTED` must be the visible default**, not a blank. A number with no disposition currently
   reads as endorsed.
3. `5. ORGAN MAP` should read `notes/ORGAN_ACCOUNTING_2026-08-18.md`: 163/163 import, 83/87
   self-tests, **67 built-passing-and-unwired**, and the 6-organ wire list.

## 7.5c OWNER DECISIONS, 2026-08-18 -- THESE SET THE DIRECTION

**1. BUILD A CURRENT-BEST SUBSTRATE. Owner: *"we need to have a current best substrate is my
assumption... we should envision a complete substrate (or close to) and wire in the best versions of
each."*** This REPLACES the piecemeal framing the Director was using. **Do not wire six organs into
an unnamed pipeline. DESIGN THE COMPLETE ORGAN SET FIRST, then fill each slot with the best
available implementation from the 147, and NAME THE EMPTY SLOTS.** An empty slot is a finding.

**2. MINE MIDDLE_BAND. Owner: *"it's worth it. understanding what it was trying and the signal may
be very important for the harder to obtain capabilities."*** **The value is NOT the verdict -- it is
the ATTEMPT and the SIGNAL.** 117 meaning-relevant cells, never read, in a population selected for
honest self-assessment rather than over-claiming.

**3. PARITY IS INTERESTING.** The one upheld result TIES the hand-written recursive rule (0.7312) at
0.7324. **The owner considers parity worth pursuing** -- and the learned version generalises to
embedding depths it never saw, which the hand-written rule does not have to earn.

**4. INSTRUMENT REBUILD -- DIRECTOR'S RECOMMENDATION: DEFER, WITH A TRIGGER. NOT NOW.**
The dissociation instrument's bars both carry CIs that include chance (0.5431 CI [0.4922, 0.5953];
0.5943 CI [0.4937, 0.6911]), and at n=242 the CI half-width (~0.05) is as large as the whole
chance-to-bar interval (~0.04). **It structurally cannot resolve a real, moderate effect.**
**BUT NOTHING IN 7.6 STEPS 1-3 USES IT.** Wiring uses organ-level discriminators, and mining
MIDDLE_BAND is reading, not gating. **REBUILD IT BEFORE THE NEXT GATED WORD-MEANING EXPERIMENT, NOT
BEFORE THE WIRING.**
***AND THE DEEPER POINT, WHICH IS WORTH MORE THAN THE POWER FIX: PREFER TASKS WITH LARGE EFFECT
SIZES OVER BUYING POWER ON A TASK WITH A TINY ONE.*** The organ probes are the evidence -- when a
mechanism genuinely works you see **pattern completion 0.20 -> 0.92**, or **leave@3 vs leave@8 on an
identical patch**. No confidence interval is needed to see those. **A whole day of gated
word-meaning arms fought over 0.63 vs 0.55. THAT GAP IS THE PROBLEM, NOT THE SAMPLE SIZE.**

## 7.6 NEXT STEPS, IN PRIORITY ORDER

1. **LAND THE ORGAN ACCOUNTING AND ACT ON `GOOD_BUT_UNUSED`.** Recovering working machinery beats
   building new machinery, and it is the owner's explicit ask.
2. **MINE MIDDLE_BAND, NOT HARD_PASS.** 117 meaning-relevant cells in a population selected for
   honest self-assessment rather than over-claiming. **Highest expected yield in the archive.**
3. **RE-RANK THE REMAINING QUEUE BY ITEM-PRIORITY** (7.2) rather than by evidence-carrying. Free,
   and the stronger filter.
4. **Vet the remaining 7 best-evidenced HARD_PASS** (13 carry both a CI and a null; 6 are done).
5. **Triage the 121 meaning-relevant NEVER-LANDED cells.** Unproven, not refuted.
6. **Fix the method so this does not regenerate:** no verdict without a CI, a null, a declared
   STRONGEST floor, and an explicit statement of whether the items predate the mechanism.

## 7.7 TOOLING BUILT 2026-08-18 -- INCLUDING THE ONE THAT FAILED

- **`tools/experiment_index.py`** -- indexes all 8,834 cells, answers in ~1 s, and **prints how many
  rows it scanned BEFORE its results**, so an empty answer can never again pass for an established
  absence. Replaces `tools/substrate_query.sh`, which **RETURNS ZERO BYTES AND EXITS 0** and thereby
  rendered every "no prior work found" report -- from every agent and from the Director -- vacuous.
  **Dates read `ts_iso`, never file mtime:** 60 metrics files share one minute from a bulk touch, and
  mtime-ranking produced a false "25 results landed the day before this session" claim.
- **`tools/verdict_evidence_gate.py`** -- the 7.2 census; `--cell NAME` for a single result.
- **`tools/vetting_ledger.py`** -- the durable categorized record; **refuses to bless an unvetted
  cell** and returns the base rate instead of silence.
- **`tools/refloor_sweep.py`** -- **BUILT, SPOT-CHECKED, FAILED, MARKED UNRELIABLE.** It compared a
  baseline to itself and a law coefficient to an error term. Kept, with the failing spot-check
  recorded inline, so the next person to have the idea finds the evidence against it first.
