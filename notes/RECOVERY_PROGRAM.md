# RECOVERY PROGRAM -- getting the leading systems back up and integrated

**LIVING DOCUMENT. Dateless filename by charter sec 2c. Updated IN PLACE, never re-dated, never
forked into a `_v2`.** Snapshots get dates; this does not. If you are a cold session: read sec 1,
then sec 3 (the rule), then run the two commands in sec 7, then work the ledger in sec 5.

Opened / created 2026-08-14. Last substantive update: 2026-08-14.

> **MERGED 2026-08-14 (late).** The two companion ledgers
> (`notes/recovery_ledger_chaingraded_tier_2026-08-14.md`, 565 rows;
> `notes/recovery_ledger_reading_tier_2026-08-14.md`, 403 rows) **are folded into sec 5 of this
> file.** They remain on disk as the primary-source record and each now carries a MERGED banner;
> **their `STATE:` tokens must NOT be counted any more** -- every row of both is carried here, and
> counting all three files double-counts. **Sec 7a's command runs over THIS FILE ONLY.**
> The merge deduplicated by experiment-DIRECTORY identity, re-checked every row's recorded verdict
> against its artifact on disk, and corrected 21 rows (sec 5.2). It deleted no row.
---

## 1. IN PLAIN LANGUAGE -- what happened and what this document is

Over roughly three months this project ran several thousand experiments. A lot of them worked.
The results were written to disk correctly. But the **way we searched for them was broken**, so
when we later asked "what do we already have?", the answer we got back was much smaller than the
truth -- and we kept rebuilding things we had already built.

The specific breakage is worth understanding, because it is not "we were careless":

> We looked for finished work by searching for **particular words** -- `HARD_PASS`, `scramble`,
> `chain_grade`. Those words changed over time. In June a control experiment was called
> `random_arm_pathology`; in August the same thing is called `scramble`. The word `scramble`
> appears **zero** times in June, yet **33 of 60** June experiments have a proper control. So the
> search said "June has no controls", and that answer was simply wrong. Separately, the highest
> quality tier ("chain-grade") is stored as a **field in a different file**, not as a word in the
> results -- so searching the results found 32 of them when there are about 574.

Four investigations on 2026-08-14 dug this out. Between them they found: a certification ledger of
2,031 rows nobody had opened; 97 fully-run, properly-controlled brain-mechanism experiments of
which 72 appear in **no** plan; a complete five-step recipe for building and reading the memory
store where **every single step is separately proven and the whole chain was never run once**; and
a measurement showing two genuinely different concepts stored with an **identical** memory vector.

**What this document is.** A single ledger, one row per recovered system, saying for each one:
where the evidence is, what it actually claimed, whether it had a proper control, whether we
opened it and confirmed it, whether it exists as real reusable code or only as a one-off
experiment, whether it is switched on today, and which of our four headline numbers it could move.
Each row carries a **STATE** word, and the job is finished when every row has left the starting
state. Section 7 gives the command that counts them, so nobody has to take anyone's word for it.

**What this document is not.** It is not a claim that the shelf is full of treasure. Several
"assets" turned out to be one-off experiment code with no reusable module behind them. Three of
five specially-flagged leads were wrong on inspection. Two thirds of the provenance links between
results are broken. Where something is unverified, this file says UNVERIFIED, and where a whole
tier was never examined, it says how big that tier is. **A plan that oversells the shelf repeats
the failure it exists to fix.**

---

## 2. THE FOUR SOURCES THIS PROGRAM CONSOLIDATES

Every row in sec 5 traces to one of these. They are complete as of 2026-08-14 and are frozen
inputs; this file is now the working surface.

| src | note | commit | what it contributes |
|---|---|---|---|
| **S1** | `notes/cert_ledger_triage_2026-08-14.md` | `c6cd948dc` | the 2,031-row cert ledger: **574 terminal chain-graded** claims, 552 with an artifact on disk, **155 Class-A floors** (a LOWER BOUND, not a rate); the never-run 5-stage recipe; cosine **1.0000** between two distinct concepts; **127 proven-bound reading cells never triaged** |
| **S2** | `notes/vscode_history_archaeology_2026-08-14.md` | `fb9882893` | 21 brain-mechanism families, **97 FULL floored passes, 72 invisible to all four planning docs**; zero-visibility families (k-WTA 17/17, attractor 12/12, Hebbian/STDP 4/4, cleanup 51/53, binding 42/49); the measurement-convention drift tables |
| **S3** | `notes/stack_review_lineage_2026-08-14.md` | `df4f9101a` | 14 whole-stack reviews since 2026-05-22 under 6 names; **57 modules self-test PASS and are off the live path, 24 with no registry row**; the capabilities that fell off across renames |
| **S4** | `notes/result_index_join_design_2026-08-14.md` + `tools/result_index_join.py` | `fa94a18e2` | registry indexes CODE, ledger indexes RESULTS, intersection **zero**; join key = result DIRECTORY NAME (96.4%); **6,566 of 7,623 results (86%) unindexed**; the shape-first drift alarm |
| **S5** | `notes/recovery_ledger_chaingraded_tier_2026-08-14.md` | `da7fe14d4` | the 565-row chain-graded tier: **172 (30%) with a real floor**; **280 rows = ONE auto-generated saturation grid**; the whiten+pinv chain WAS composed (`exp_pb_production_recipe_integration_v1`, 57.3x); the expansion stage CONTRADICTED from inside the tier. **MERGED INTO SEC 5 ON 2026-08-14** |
| **S6** | `notes/recovery_ledger_reading_tier_2026-08-14.md` | `b4e90942a` | the 171-row reading tier + the 232-row brain-mechanism tier: S1's 127 is really **171**, S2's 97 FULL is really **144** and its 72-invisible really **120**; three FULL floored refutations of the separation-geometry route on the real task. **MERGED INTO SEC 5 ON 2026-08-14** |

Supporting, already folded in: `notes/vscode_era_unrecognised_assets_2026-08-14.md` (`6b43be02d`,
the A1-A6 tier-1 shortlist) and `notes/vscode_week_results_validity_audit_2026-08-14.md`
(`0887b54f8`, closed -- attacked results, not re-litigated here).

---

## 3. THE STATE MACHINE -- what "done" means

Five states. Closed vocabulary. Every row in sec 5 carries exactly one, written literally as
`STATE:<WORD>` so it is machine-countable (sec 7).

| STATE | meaning | entry requirement -- what you must have DONE to write it |
|---|---|---|
| **FOUND** | named in a source, nothing checked | it appears in S1-S4. This is the starting state and is **not** evidence of anything |
| **VERIFIED** | opened on disk at HEAD | you opened the primary `metrics.json` (or the module file) with `.venv/Scripts/python.exe`, and recorded VERDICT + RUN_MODE + the floor arm **as they actually read**, not as a note reported them. Any disagreement with the source note is written into the row as a correction |
| **WIRED** | in the substrate and reachable | promoted to `hdlab/`, **observed inside a RUNTIME import closure** (never grep), and carrying a `data/capability_registry.jsonl` row. An opt-in module counts only if the named entry flag/kwarg is written into the row |
| **SHELVED** | verified, deliberately not wired | the row carries an explicit **revival criterion** -- the specific condition that would reopen it. No criterion = not SHELVED, still VERIFIED |
| **REFUTED** | verified and the claim does not hold | its own floor/control kills it, or a later cell replaced it, and the disproving number is quoted in the row |

**Legal transitions:** `FOUND -> VERIFIED -> {WIRED | SHELVED | REFUTED}`. Nothing skips VERIFIED.
`SHELVED -> WIRED` is legal when the revival criterion is met (say which). `WIRED -> SHELVED` is
legal but must cite the measurement that unwired it.

**Two states are terminal-good** (WIRED, REFUTED): the system is either in the substrate or is
provably not worth putting there. SHELVED is terminal-*conditional*. VERIFIED is a work-in-progress
state and a row sitting in it is unfinished business.

**DONE for this program** = zero rows in FOUND, and zero rows in VERIFIED. Not "everything WIRED":
wiring a refuted mechanism would be worse than leaving it alone.

### 3a. Column meanings (read once, then the tables are self-explanatory)

- **evidence** -- the primary artifact path. Result cells: `data/<dir>/metrics.json`. Modules:
  `hdlab/<name>.py`. Commit column omitted per-row because the load-bearing provenance is the
  **path plus the source-note commit in sec 2**; per-cell landing commits are recoverable with
  `git log -1 --format=%h -- <path>` and are not reproduced here (they are tier-1 re-derivable
  per `STATUS_SPEC.md` sec 3).
- **floor** -- the control arm as read from the file. `A` = explicit control/comparison arm.
  `PROSE` = the floor exists but lives inside `verdict_msg` text, not as a key. `ARM` = the floor
  is an arm NAME with no control word in it. `NO FLOOR` = none found and none claimed --
  **an unfloored pass is not evidence**. `UNPINNED` = not checked by me.
- **disk** -- `OK` (metrics.json opened today) / `NO DIR` (no directory resolves).
- **module** -- `HDLAB:<file>` (a reusable module exists) / `EXP-ONLY` (the capability exists only
  as experiment code and one output directory; "wire it" is really **build it**) /
  `NOT LOCATED` (claimed in an index, no artifact found under that name).
- **live** -- membership of the **runtime** import closure measured 2026-08-14 (sec 4). `LIVE` /
  `OFF-PATH`. **`OFF-PATH` means "not on the DEFAULT path", never "does not exist" and never
  "cannot be reached"** -- opt-in and lazily-imported modules are invisible to a default trace.
  EXISTS / IS-REACHED / IS-GOOD are three separate questions and are kept separate here.
- **moves** -- which scoreboard number it could move: `C1` near-neighbour 2AFC 0.698; `C2` context
  gap +0.1005; **`C3` read-out quality 4.80% vs 0.80% floor -- THE GATE, 5.2pp short of 10%**;
  `C4` coref 0.7193; `BOUND` = it constrains C3 rather than moving it; `--` = none.
- **supersede** -- `UNCHECKED` unless stated. This is the honest default: the ledger's supersession
  graph is **52 of 66 edges dangling** (S4) / **93 of 164 raw edges dangling** (S1), so no row here
  may be read as "survives unchallenged to HEAD" without its own check.

---

## 4. THE RUNTIME LIVE-PATH MEASUREMENT (2026-08-14, this session)

Measured, not grepped, per `CLAUDE.md` evidence-discipline sec 3:

```
.venv/Scripts/python.exe -c "import sys; import hdlab.reading_grounding_loop; \
  import hdlab.grounding_acquisition_loop; \
  print(sorted(m for m in sys.modules if m.startswith('hdlab.')))"
```

**39 `hdlab.*` modules** are in the closure of the two live entry points (the acquisition loop adds
**zero** beyond the reading loop's closure). The 39:

`ablation, animacy_lexicon, atoms, binding, bundling, cleanup_family, closed_class_lexicon,
consequence_learning_loop, coreference_resolver, event_bundle, frame_induction, gap_detector,
goal_typing, grounded_similarity, grounding_acquisition_loop, hd_fact_store, iterative_attractor,
learner (+core, +registry, +5 plugins), lexical_similarity, memory, modulators,
reading_grounding_loop, role_slot_summarizer, self_improving_loop, semantic,
situation_model_accumulate, snapshots, state_of_mind, thematic_role_labeler, tracing,
verb_lexical_similarity, working_memory`

**Not one recovered system in sec 5 is in that list.** That is the whole problem stated as one
measurement, and it is why the WIRED count starts at zero.

Registry measured the same session: **`data/capability_registry.jsonl` = 127 rows.** Registry
presence below is a NAME test (substring on `hdlab/<m>.py` or `"<m>"`); it can over- and
under-fire and is labelled as a name test wherever it is used.

---

## 5. THE RECOVERY LEDGER

### 5.0 THE COUNTS -- read these before any other number in any document

**974 rows, one per distinct experiment artifact, after deduplicating 1,063 raw ledger rows drawn
from three files.** This is now the only file that carries them.

| quantity | number | what it means |
|---|---|---|
| raw rows across the three source ledgers | **1,063** | RECOVERY_PROGRAM 95 + chain-graded 565 + reading 403 |
| rows absorbed as duplicates of another row | **90** | the same experiment DIRECTORY written up twice; sec 5.6 names every one |
| **rows carrying a countable STATE after dedup** | **974** | 1,063 - 90 + 1 new row = 974. Sec 7a's command returns exactly this |
| **DISTINCT INVESTIGATIONS** | **~696** | 974 rows minus the 279-row auto-generated saturation grid counted as ONE. **THIS IS THE HONEST SIZE OF THE SHELF -- never quote 974 or 1,063 as "experiments"** |
| ...with a REAL FLOOR (control / reference / prose arm) | **529** | an unfloored pass is NOT evidence. Per tier: chain-graded **172 of 565 = 30%**; reading tier 381 of 403 |
| **WIRED -- in the substrate and runtime-reachable** | **1** | **ZERO of the 968 recovered CELLS is wired.** The single WIRED row is `G4`, the index tool -- infrastructure, not a capability |
| rows whose cited artifact does not resolve on disk (DANGLING) | **12** | sec 5.7. Of these only 8 are cells; 4 are not cells at all |
| rows resolved only onto a SIBLING directory (per-seed / smoke) | **17** | the named cell has no directory of its own; the artifact quoted is a sibling |

**STATE distribution over the 974 rows:** **FOUND 30** / **VERIFIED 881** / **WIRED 1** / **SHELVED 2** / **REFUTED 60**

**The three deflations that must travel with every number above:**

1. **279 of the 974 rows are ONE auto-generated saturation grid**
   (`exp_q_a3_l<N>_cross_layer_composition_v1_n<N>` / `exp_pp48_nkt_*`) reporting EXACT-1.0 at
   every level with no comparison arm, because the result is construction-determined. It is filed
   in **Appendix A** at the end of this file, not in the body, so it cannot pad a skim.
   **"574 chain-graded cells" was never 574 experiments; that tier is ~287 investigations.**
2. **Only 172 of the 565 chain-graded rows (30%) have a real floor.** The rest are contrast-only
   or unfloored. An unfloored pass is not evidence.
3. **NOTHING IS WIRED.** 968 recovered cells, zero in the runtime import closure (sec 4).
   Triaged is not finished; VERIFIED is a work-in-progress state (sec 3).

**Untriaged residue, unchanged by this merge and stated so it cannot look smaller than it is:**
of the cert ledger's ~1,925 distinct atoms these rows cover roughly 745, leaving **~1,180 atoms
NOT-YET-TRIAGED**; of the **7,634 `metrics.json` on disk** these rows cover ~974, leaving
**~7,150 NOT-YET-TRIAGED** (sec 6, rows H4-H10).

### 5.0a HOW TO ANSWER "HAS ANYONE TRIED X?"

```bash
cd /d/AI/hd-instrument
grep -in 'permutation\|whitening\|pattern_separation' notes/RECOVERY_PROGRAM.md | head -40
```

Every row names its experiment DIRECTORY, so any keyword in a directory name will find it.
**If the grep comes back empty that is NOT an absence result** (sec 8 rule 3): naming conventions
drifted, and this merge found 14 rows previously reported as having no directory that resolve the
moment the match is made case-insensitive. Search the SHAPE too:

```bash
grep -coE 'STATE:(REFUTED)' notes/RECOVERY_PROGRAM.md   # proven negatives -- these STOP work
grep -n 'DANGLING' notes/RECOVERY_PROGRAM.md            # write-path defects, not missing work
```

*(the parentheses in that command are load-bearing. `STATE:` followed directly by a state word is
the token sec 7a counts, so writing one in PROSE inflates the ledger's own total by one -- it
happened twice while this section was being drafted. Rule: outside a table row, always break the
token, e.g. with the `(...)` group above. `grep -nE 'STATE:[A-Z_]+' notes/RECOVERY_PROGRAM.md |
grep -vE '^[0-9]+:\|'` returns every violation and must come back empty.)*

| looking for | go to |
|---|---|
| what bears on the read-out gate C3 | sec 5.3 groups A + B, then secs 9b, 9c, 9d |
| what has already FAILED, so it is not re-run | sec 5.3 group E, sec 9e, and every row in state REFUTED |
| the reading / comprehension arc | sec 5.3 group C, sec 5.5 group R |
| brain-mechanism organs (k-WTA, attractor, DG, binding, cleanup) | sec 5.3 group D, sec 5.5 group M, sec 9f |
| June/early-July substrate physics | sec 5.4 groups CG-A .. CG-D |
| modules that exist but are off the live path | sec 5.3 group F, sec 4 |
| why the record went dark in the first place | sec 5.3 group G, sec 8 |
| what has NOT been looked at at all | sec 6 |
| the saturation grid (280 rows, one investigation) | Appendix A |

### 5.1 METHOD -- how identity was resolved, and how floors were detected

**Identity (this merge).** Every row was reduced to an experiment-DIRECTORY name, never to row
text. Resolution order, applied against a fresh `os.scandir('data/')` enumeration of **7,898
top-level directories, 7,634 of them carrying a `metrics.json`**:

1. an explicit `data/<dir>/metrics.json` path written in the row is **AUTHORITATIVE** and overrides
   the cell name. Without that rule a row whose path names the `_smoke` artifact gets fuzzily
   re-attached to its non-smoke sibling and two genuinely distinct artifacts merge -- **that bug
   produced 30 false duplicates in the first pass of this merge and was fixed before any count
   below was taken**;
2. exact directory name;
3. **case-insensitive exact -- this stage alone recovered 11 rows the chain-graded sweep had
   reported as having NO DIRECTORY AT ALL** (`..._k_banks_v2_gpu` vs `..._K_banks_v2_GPU`);
4. brace expansion (`_seed_{7,13,19}` -> three per-seed directories) and the
   `_seed_7_AND_13_AND_19` variant;
5. string-prefix, for names truncated by the atom-id writer;
6. longest-common-TOKEN-prefix, used only where >=4 tokens match and >=2 of them are not generic
   ledger prose (`3seed`, `full`, `chain`, `grade`, ...). 17 rows rest on this stage alone and are
   marked as resolving onto a SIBLING directory.

Rows sharing any resolved directory were merged by union-find. **Dedup is by artifact identity, not
by row text**, which is why two rows with completely different wording (`exp_reader_image_word_grounding_v1`
in group D as "reader image-word grounding" and in the reading tier as row R3) merge correctly.

**Verdict (this merge).** Every merged row's recorded verdict was re-read from its artifact with
`.venv/Scripts/python.exe`. **934 of the 945 readable rows reproduce; 11 do not**, and all 11 are
corrected in place in sec 5.2. That is the "verify off data, never off the report" discipline
applied to the ledgers themselves rather than to the experiments.

**Floors (inherited from both sweeps; restated because it is the anti-recurrence rule).** Detection
is by SHAPE first, vocabulary second. An ARM GROUP is a dict whose children are >=2 sibling dicts
sharing a numeric key, or >=2 sibling numeric keys differing in exactly one token position, or (the
relaxed rule that recovers `{cap_unwhitened, cap_pca_whitened}`) >=2 sibling numeric keys sharing
their first or last token but of unequal length. A group is DISCARDED when its distinguishing
labels are all seed-like or all config levels -- **a replication or a parameter sweep is not a
control.**

| lexical baseline (substring over the whole `metrics.json`) | floored cells it finds | floored cells it MISSES |
|---|---|---|
| `scramble` only -- the convention the August tooling used | 11 | **161** |
| the common six (`scramble/shuffle/random/chance/baseline/control`) | 103 | 69 |
| a broad 31-token vocabulary | 128 | 44 |

**Read the first row. A `scramble`-keyed sweep sees 11 floored cells in the chain-graded tier and
misses 161 that have one.** On the 35 June cells dated by a RELIABLE source, **zero contain the
string `scramble` while 24 have a real floor** -- June names its floors `hebb_alpha_c`,
`cap_unwhitened`, `last_token_raw`, `precision1_plain`, `HA_ONLY`, `NO_CX`, `FHRR` (as the failing
arm), `random_arm_pathology`, `FREQ_NULL`, or states them only in prose.

**Honest limit, so `NO FLOOR` is not over-read:** the detector reads only `metrics.json`. A floor
declared in a pre-registration, a `notes/` writeup or a `_start_marker.json` is invisible to it.
**`NO FLOOR` means "no floor visible in metrics.json", never "no floor"** -- and two of the three
cross-ledger disagreements this merge adjudicated (CG-B14, RP-D3) are exactly that case: a real
floor written as prose.

### 5.2 CORRECTIONS THIS MERGE MADE -- 21 rows, every one re-checked on disk

Per sec 10d rule 4, a corrected claim is struck in place, not quietly fixed. Each row below carries
its correction and its quoted evidence inline; this table is the index to them.

**Symmetric, deliberately.** Nineteen corrections make a result BETTER and one makes a result
WORSE. The standing rule is `STATUS.md` discipline 7 -- **no demotion without a fresh on-disk
re-check** (~11 results were wrongly demoted this month, producing 17 corrections-of-a-correction
in 48h) -- so the single demotion below carries a three-directory enumeration and a quoted error
string, and the nineteen upgrades carry the same.

| row | was | now | why, in one line |
|---|---|---|---|
| **CG-B70** | REFUTED (`HARD_FAIL`) | **VERIFIED** | artifact reads `HARD_PASS`, `rec=1.0000 cv=0.0000 n=3`; the HARD_FAIL belongs to its **v2b sibling**, which had no row in any ledger and is now CG-G1 |
| **CG-B142** | REFUTED (`HARD_FAIL`) | **VERIFIED** | artifact reads `HARD_PASS`: *"DG sparse expansion gives >=10x capacity ... ratio=48.0x"*. The family has exactly one directory, so no sibling mix-up is possible |
| **CG-B74** | REFUTED (`MIDDLE_BAND`) | **VERIFIED** | all three seed artifacts read `HARD_PASS`, run_mode `full`; the `_smoke` siblings read `SMOKE_PASS` |
| **CG-D5** | verdict `CELL_CRASHED` | **verdict `HARD_PASS`** | all three seed artifacts read `HARD_PASS / CHAIN_GRADE_COMMERCIAL_SCALE`. The crash does not reproduce off any artifact. State unchanged |
| **CG-B7** | VERIFIED (`HARD_PASS`) | **FOUND** | **the one demotion.** All three seeds read `HARD_FAIL ... CUDA out of memory`. An INFRASTRUCTURE ABORT: nothing was measured, so it is not REFUTED either |
| **CG-B134** | REFUTED | **FOUND** | `HARD_FAIL_GPU_MANDATE_BREACH ... Refusing.` The run never started, so it refutes nothing. The reading tier already had it at FOUND |
| **CG-F2 / F3 / F5 / F6 / F7 / F8 / F9 / F10 / F11 / F12 / F18** | FOUND, "no directory resolves" | **VERIFIED** (11 rows) | **not absent -- MIS-ENUMERATED.** The earlier matcher was case-SENSITIVE; every one resolves case-insensitively and its `metrics.json` opens at HEAD |
| **CG-F13 / F14 / F15** | FOUND, "no directory resolves" | **VERIFIED** (3 rows) | resolve by longest-common-token-prefix onto the per-seed artifact; verdicts read `MIDDLE_BAND` / `HARD_PASS` / `HARD_PASS` |
| **CG-G1** | *(no row existed)* | **REFUTED -- new row** | the genuine `HARD_FAIL` (v2b, OOM) that CG-B70's verdict had been mis-attached to. A negative that was one edit away from being lost |
| **RP-D22** | "sibling has NO DIRECTORY (confirmed)" | **annotated** | it exists as `data/substrate_C1_entmax_alpha_readout_v1/` -- no `exp_` prefix, capital `C1` -- and reads `HARD_PASS` |
| **CG-B143** | disk `OK` | **annotated DANGLING-BY-FILENAME** | the directory exists but holds `metrics.fresh_2026-06-30.json`, not `metrics.json`. Every `metrics.json` glob in the repo is blind to it |

**Where the two ledgers DISAGREED on a STATE -- all three cases, each resolved by opening the
artifact, none resolved by preferring a file:**

| artifact | chain-graded / RP said | reading tier said | on disk, re-read this session | resolution |
|---|---|---|---|---|
| `exp_hopfield_spurious_minima_cpu_v1` | VERIFIED (RP-D3, PROSE floor) | FOUND (M229, no floor by shape) | `HARD_PASS`, smoke, *"genuine-convergence=0.957"* against a 0.90 bar | **VERIFIED.** The floor is real and lives in prose |
| `exp_substrate_permutation_binding_multiocc_v2_full` | VERIFIED (CG-B14) | FOUND (M140) | `HARD_PASS_CHAIN_GRADE`, full, `perm=1.0000 cv=0.0000 FHRR=0.0629 lift=0.9371` | **VERIFIED.** The `FHRR` arm IS the floor, in prose |
| `exp_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_7` | REFUTED (CG-B134) | FOUND (M226) | `HARD_FAIL_GPU_MANDATE_BREACH ... Refusing.` | **FOUND.** Neither ledger was right that anything had been measured |

**Two of the three disagreements are the same defect: a real floor written as PROSE reads as NO
FLOOR to a shape detector, and the reading tier maps no-floor to FOUND.** That is a detector
limitation, not a weaker result. It is the reason sec 5.1 carries an explicit honest-limit
paragraph, and the reason no row in this file was demoted on a detector's say-so.

### 5.3 GROUPS A-G -- the 95 originally-ledgered systems

Unchanged in substance. Rows now additionally carry merge annotations where another ledger covered
the same artifact, and the corrections listed in sec 5.2.

#### Group A -- read-out / within-neighbourhood separation (bears on C3, THE GATE)

| # | system | evidence | claim (as read on disk) | floor | disk | module | live | moves | supersede | STATE |
|---|---|---|---|---|---|---|---|---|---|---|
| A1 | near-duplicate codebook diagnostic | `data/exp_substrate_codebook_near_duplicate_diagnostic_cpu_v1/metrics.json` | `HARD_PASS`, run_mode **full**, no `ts_iso`. 241 atoms @1024: **49 pairs cos>0.9; 54/241 (22%) have a near-neighbour above threshold; top pair cos = 1.0000 between `probability_space` and `measure_space`, two DISTINCT concepts**. De-dup at 0.95 -> F1 1.0000, F=3 cleanup **+0.1704** | A (near-dup floor 0.1333; de-dup vs full arm; 3 seeds, cv=0) | OK | EXP-ONLY | OFF-PATH | **C3** | UNCHECKED | STATE:VERIFIED |
| A2 | peel / SIC read-out on real codes | `data/exp_encoder_peel_sic_readout_realcodes_v1/metrics.json` | `HARD_PASS_PEEL_SIC_TRANSFERS_TO_REAL_CODES`, **full**, `ts_iso 2026-07-08T17:28:40`, 5 seeds. Flat argmax **0.204** -> peel/SIC **0.940**, lift **+0.736** (bar >=+0.2, cv 0.034) | A (flat argmax declared collapsed if <=0.7) | OK | **EXP-ONLY** -- `hdlab/peel_sic.py` **DOES NOT EXIST** (checked); the one `peel_sic` registry row describes community-bounded routing, a different thing | OFF-PATH | **C3** | UNCHECKED | STATE:VERIFIED |
| A3 | coarse-to-fine retained-trace requery | `data/exp_encoder_retained_trace_requery_coarse_to_fine_v1/metrics.json` | `HARD_PASS_RETAINED_TRACE_RECOVERS`, **full**, `2026-07-08T19:13:00`. Coarse shortlist (rand-proj D=128) then fine read inside it: `final_recall 0.992` against a full-fine **ceiling 0.992** (loses nothing) vs sparse max 0.561; `shortlist_hit@k=0.1 = 1.000` | A (sparse control 0.541 reproducing the v1 wall; Gate-D dense reproduce 0.9933) | OK | EXP-ONLY | OFF-PATH | **C3** | UNCHECKED | STATE:VERIFIED |
| A4 | dense Hopfield read-out, correlated codes | `data/exp_dense_hopfield_readout_capacity_correlated_codes_v1/metrics.json` | `HARD_PASS`, **full**, `2026-07-14T00:42:50`, seeds 7/13/19. **3.25x** capacity lift over pairwise on correlated codes; per-correlation 6.74x mild / 3.12x mod / **1.63x strong** | A (scramble collapses to 0.01; iid positive control 5.48x) | OK | HDLAB:`modern_hopfield_readout.py` (16,478 B, **no registry row** by name test) | OFF-PATH | **C3** | UNCHECKED | STATE:VERIFIED |
| A5 | DG pattern separation at write time | `data/exp_substrate_anisotropy_dg_pattern_separation_prewrite_v1/metrics.json` | `HARD_PASS`, **full**, **no `ts_iso`**, 3 seeds, real Pythia-2.8b keys. `dg_full 0.942` vs bar 0.50; effrank lift **10.08x**; off-diagonal mass 0.179 -> 0.012 **SEC 11 CORRECTION 2026-08-14: DG pattern separation is NOT REFUTED.** The July task-level HARD_FAILs (`dg_pattern_separation_mcscript_purity_v1`, `selfplay_dg_pattern_separation_xfit_v1`) were judged by instruments that have since been ruled invalid. UNTESTED WITH A WORKING RULER. | A (`uniform_no_presep` collapses to 0.083) | OK | HDLAB:`dg_pattern_separation.py` (11,526 B). **The registry's `pattern_separation` row points at `hdlab/hippocampal_encoder.py`, a DIFFERENT module** -- this one has no row | OFF-PATH | **C3** | UNCHECKED | STATE:VERIFIED |
| A6 | synonym-vs-sibling pooling interface | `data/exp_diag_learned_encoder_synonym_sibling_deep_wall_v1/metrics.json` | FULL verdict `MIDDLE_BAND_INTERFACE_SEPARATES_BUT_NOT_LEARNING`, **full**, `2026-08-12T03:10:56`. Trained AUC 0.7064 beats grounding 0.3186 -- **but randinit same-arch scores 0.7452, EQUAL OR BETTER**. Reading: the POOLING INTERFACE separates for free; the LEARNING claim is dead | A (scramble 0.5042 -> chance; randinit control) | OK | EXP-ONLY | OFF-PATH | **C3** | UNCHECKED | STATE:VERIFIED |
| A7 | semantic HD encoder meaning-match | `data/exp_semantic_hd_encoder_meaning_match_v1/metrics.json` | `MEANING_MATCH_PASS`, `2026-07-24T15:37:47`. **`run_mode` key ABSENT -- this may not be a FULL run and must not be quoted as one.** semantic AUC 0.960, separation 0.507 vs lexical floor **-0.400** | A (lexical/surface-form control) | OK | EXP-ONLY | OFF-PATH | C3 | UNCHECKED | STATE:VERIFIED |
| A8 | cue-clamped iterative cleanup | `data/exp_substrate_iterative_cleanup_cue_clamped_v1/metrics.json` | `HARD_PASS`, **`run_mode` ABSENT**, no date. Best clamped arm alpha=0.3 -> **0.2250** vs ARM_SINGLE_STEP 0.1500, lift +0.075. **Absolute numbers are low; the cell's own `WHAT_THIS_DOES_NOT_SHOW` says unproven at N=8192** | ARM (`ARM_SINGLE_STEP` / `ARM_CURRENT` are the floor) | OK | EXP-ONLY (but `hdlab/iterative_attractor.py` IS live -- the mechanism family already has a live home) | OFF-PATH | C3 (weak) | **contested by E11** | STATE:VERIFIED |
| A9 | resonator verifier read-out | `data/exp_resonator_verifier_readout_v1/metrics.json` | `HARD_PASS`, **full**, no date, 3 seeds. K4 harvest **0.806**, +0.353 over plurality 0.453 -- **and `oracle_any` = 0.806, i.e. it harvests EXACTLY the oracle and no more**. Ledger tier is `cert_neutral_*`, **NOT chain-grade** (S1 correction) | A (`baseline_K4` 0.133, plurality 0.453, oracle_any) | OK | EXP-ONLY | OFF-PATH | **BOUND** | UNCHECKED | STATE:VERIFIED |
| A10 | anchor-compose identity shuffle (+ scaling ladder) | `data/exp_anchor_compose_identity_shuffle_cskg_v2/metrics.json`; `..._scaling_ladder_cskg_v3/` | `HARD_PASS_INDUCTIVE_ANCHOR_COMPOSE_IDENTITY...` / `SCALING_HOLDS`, both **full**, `2026-07-13`. ANCHOR **0.1275** vs **ORACLE 0.1374** -- **93% of its own oracle**; ADDITIVE 0.0000, ONESHOT 0.0001 | A, unusually complete: RANDOM 0.0005, SCRAMBLE 0.0087, IDSHUF 0.0025, POPULARITY 0.0001, ORACLE 0.1374, n_q 3000 | OK | EXP-ONLY | OFF-PATH | **BOUND** | UNCHECKED | STATE:VERIFIED |
| A11 | metacognitive abstain / signal thresholding | `data/exp_metacog_abstain_readout_signal_thresholding_v1/metrics.json` | `HARD_PASS_EXISTING_SIGNAL_CARRIES_USABLE_CONFIDENCE`, **full**, `2026-07-20T02:08:36`. S1 reader-best-score HARD_PASS (rel_red 0.327 @ cov 0.5); **S3 and S4 HARD_FAIL -- `S4_cleanup_margin` carried no usable signal a month before the SNR-wall diagnosis** | A (`beats_rand=True, p=0.0, rand_p50 0.732`) | OK | EXP-ONLY | OFF-PATH | C3 (precision at partial coverage, **not** hit@1) | UNCHECKED | STATE:VERIFIED |
| A12 | hallucination detection (MiniLM) | `data/exp_substrate_hallucination_detection_minilm_v1/metrics.json` | `HARD_PASS`, **full**, no date. AUC **0.999** separating grounded from hallucinated; grounded_conf 0.204 vs hall 0.107 | ARM (the grounded-vs-hallucinated contrast IS the floor; **S1's lexical detector scored this Class D -- a detector false negative**) | OK | EXP-ONLY | OFF-PATH | C3 (precision) | UNCHECKED | STATE:VERIFIED |
| A13 | common-mode salience detector | `data/exp_attention_salience_common_mode_detector_v1/metrics.json` | `HARD_PASS_COMMON_MODE_DETECTOR_SEPARATES`, **full**, `2026-07-20T05:42:23`. Gap 0.0829, per-seed 5/5. **Explains why rank-1 common-mode removal returned HARD_FAIL_NO_EFFECT: the detector fires only in the correlated mode** | A (shuffle control quiet in both modes, 0.0001/0.0003) | OK | EXP-ONLY | OFF-PATH | C3 (diagnostic, not a lift) | UNCHECKED | STATE:VERIFIED |
| A14 | resonator peel family siblings | `data/exp_resonator_theta_gamma_peel_v1/`, `data/exp_resonator_deflation_lowsnr_v1/` | both `HARD_PASS`, both **full**, both undated | UNPINNED (not opened beyond verdict/run_mode) | OK | EXP-ONLY | OFF-PATH | C3 | UNCHECKED | STATE:VERIFIED |

#### Group B -- the five-stage store recipe: every stage proven, the CHAIN NEVER RUN

This is S1's headline structural finding and it survives verification: `last-token pool ->
dimensional expansion -> whitening -> pseudoinverse write -> coarse-to-fine read` (A3 is the last
stage). Each stage below is separately terminal-chain-graded with an artifact on disk. **No cell
tests the chain end-to-end.**

| # | system | evidence | claim (as read on disk) | floor | disk | module | live | moves | supersede | STATE |
|---|---|---|---|---|---|---|---|---|---|---|
| B1 | last-token vs mean-pool x whitening | `data/exp_substrate_last_token_vs_whitening_mean_pool_v1/metrics.json` | `HARD_PASS`, **full**, no date, 3 seeds bit-identical. capacity `last_token_raw` **0** / `mean_pool_whiten` **40** / `last_token_whiten` **122**; best-combined **3.05x** | ARM (raw arm is the floor; **no arm name contains a control word -- S1 flagged this as its clearest lexical false negative**) | OK | EXP-ONLY | OFF-PATH | **C3, C1** | UNCHECKED | STATE:VERIFIED |
| B2 | PCA prewhitening of the codebook | `data/exp_substrate_pca_prewhitening_codebook_v1/metrics.json` | `HARD_PASS`, **full**, no date, 3 seeds. cap 3 -> 7 at N=384, ratio 2.33x. **DEFLATE HARD: the absolute capacities are 3 and 7 items.** "Universal real-encoder rescue" is the cell's own framing and n=7 does not support it | ARM (structurally recovered) | OK | EXP-ONLY | OFF-PATH | C3, C1 | UNCHECKED | STATE:VERIFIED |
| B3 | ETF / MiniLM dimensional expansion | `data/exp_substrate_etf_minilm_dim_expansion_v1/metrics.json` | `HARD_PASS`, **full**, no date. whitened cap D384 **844** -> D4096 **9011** (10.68x); within-D whitening gain 3.06x @D384, 1.29x @D1024/4096 | ARM | OK | EXP-ONLY | OFF-PATH | C3, C1 | UNCHECKED | STATE:VERIFIED |
| B4 | expansion + whitening STACK (no subsumption) | `data/exp_substrate_dim_expansion_subsumes_whitening_n_enc_10000_v1/metrics.json` | `HARD_PASS`, **full**, no date. Expansion and whitening **stack**; production rule stated. **The "7000000000x" headline is a divide-by-zero (`expand_only = 0.0`). DO NOT PROPAGATE IT** | ARM | OK | EXP-ONLY | OFF-PATH | C3, C1 | UNCHECKED | STATE:VERIFIED |
| B5 | pinv write rule -- synthetic | `data/exp_hebb_vs_pseudoinverse_long_v1/metrics.json` | `HARD_PASS`, **full**, no date. N=4096: Hebb 0.050 -> pinv 0.550, **11.0x** (theory ~7x) | ARM (`{hebb_*, pinv_*}` pair; the Hebb arm IS the floor) | OK | EXP-ONLY | OFF-PATH | **C3, C1** | UNCHECKED | STATE:VERIFIED |
| B6 | pinv write rule -- Llama-L15 keys | `data/exp_pb_pinv_llama_l15_keys_v1/metrics.json` | `HARD_PASS`, **full**, no date. cap **122 -> 614 = 5.03x**. **This is the non-degenerate anchor of the family** -- not a divide-by-zero | ARM | OK | EXP-ONLY | OFF-PATH | **C3, C1** | UNCHECKED | STATE:VERIFIED |
| B7 | pinv write rule -- BGE-large keys | `data/exp_f6_bge_large_pinv_mmax_reaudit_v1/metrics.json` | `HARD_PASS`, **full**, no date. Hebb **0.000** -> pinv 0.550. Quote as *"Hebb reaches 0 where pinv reaches 0.55"*, **never as a ratio** | ARM | OK | EXP-ONLY | OFF-PATH | **C3, C1** | UNCHECKED | STATE:VERIFIED |
| B8 | pinv write rule -- E5-large keys | `data/exp_pb_e5_vs_bge_pinv_headtohead_v1/metrics.json` | `HARD_PASS`, **full**, no date. Hebb 0.000 -> pinv 0.550 | ARM | OK | EXP-ONLY | OFF-PATH | **C3, C1** | UNCHECKED | STATE:VERIFIED |
| B9 | pinv write rule -- MiniLM keys | `data/exp_pseudoinverse_real_encoder_keys_v1/metrics.json` | `HARD_PASS`, **full**, no date. Hebb 0.000 -> pinv 0.400. **Its own `verdict_msg` contains the literal figure "400000000x" -- an arithmetic artifact of x/0. Never quote it** | ARM | OK | EXP-ONLY | OFF-PATH | **C3, C1** | UNCHECKED | STATE:VERIFIED |
| B10 | learned KV projection | `data/exp_kv_learned_projection_v1/metrics.json` | `HARD_PASS`, **full**, no date. Held-out worst-seed recall **0.827** (std 0.019), key-separation 0.878, vs analytic ceiling 0.080 and **shuffled control 0.015**. This is the *missing-LEARNING* flavour, reusing `hdlab/learner` rather than a parallel build. `n_enc=2` | A (shuffled control 0.015, held-out split) | OK | EXP-ONLY | OFF-PATH | **C3, C1** | UNCHECKED | STATE:VERIFIED |
| B11 | the whitening module itself | `hdlab/whitening.py` | **EXISTS, 5,852 B.** **Not in the 39-module runtime closure. No registry row** by name test. Imported by `substrate/kv_memory.py` and ~28 `experiments/` scripts -- i.e. **the lever B1-B4 all depend on is islanded from the read-out path** | n/a | OK | HDLAB:`whitening.py` | **OFF-PATH** | C3, C1 | n/a | STATE:VERIFIED |

#### Group C -- reading / construction competencies (C4, C2, and the reading arc)

| # | system | evidence | claim (as read on disk) | floor | disk | module | live | moves | supersede | STATE |
|---|---|---|---|---|---|---|---|---|---|---|
| C1 | passive-voice who-did-what | `data/exp_consolidated_reader_passive_mechanism_heldout_v1/metrics.json` | `PASSIVE_MECHANISM_CAPABILITY_EARNED`, **full**, `2026-07-24T00:29:16`. **23/24 = 0.9583 vs naive 0/24**, margin +23, on INDEPENDENT held-out passages; flag ON/OFF **12/13 fired vs 2**; McGuffey composed F1 unchanged 0.5868. **The strongest single invisible result found in any source.** *Caveats: n=24 items / 13 passages; `n_seeds` null; the win is PARSER-side, so file it under reading, not C3* | A (`naive_acc = 0.0`, `naive_hash` for repro; P2 flag-OFF ablation) | OK | EXP-ONLY | OFF-PATH | C4 / reading | UNCHECKED | STATE:VERIFIED |
| C2 | consolidated reader -- in-domain demo | `data/exp_consolidated_reader_chaingrade_demo_v1/metrics.json` | `CHAIN_GRADE_DEMONSTRATED`, **full**, `2026-07-23T21:11:15`. Reader F1 **0.592** vs naive positional 0.3407 (+0.2513); glass-box replay/tamper/causal-edit all held | A (two baselines: naive positional 0.3407, `arm_a_baseline_svo` 0.2708) | OK | EXP-ONLY | OFF-PATH | reading | UNCHECKED | STATE:VERIFIED |
| C3 | consolidated reader -- held-out | `data/exp_consolidated_reader_chaingrade_FULL_v1/metrics.json` | `CHAIN_GRADE_HELDOUT_PARTIAL`, **full**, `2026-07-23T23:24:24`. **`chain_grade_heldout_earned = False`**; 2 of 4 bars held. LitBank held-out **reader 10/13 vs naive 11 -- the reader LOSES**. Together with C2 this is the in-domain-wins / held-out-attenuates shape the project **re-derived in August as the "entity-knowledge wall"** | A | OK | EXP-ONLY | OFF-PATH | reading | UNCHECKED | STATE:VERIFIED |
| C4 | consolidated reader -- hard syntax | `data/exp_consolidated_reader_hardsyntax_heldout_v1/metrics.json` | `CHAIN_GRADE_HARDSYNTAX_EARNED`, **full**, `2026-07-23T23:48:58`. Reader 4/24 vs naive **0/24**. **The cell itself calls this a small-N probe -- cite as a lead, not evidence** | A (true zero) | OK | EXP-ONLY | OFF-PATH | reading | UNCHECKED | STATE:VERIFIED |
| C5 | cross-sentence coref -- local window | `data/exp_read_xsent_coref_scene_protagonist_v1/metrics.json` | `HARD_PASS`, **full**, `2026-07-24T05:45:55`. Same-gender subset 0.4003 vs backbone 0.2462 (+0.1541). **`scene_structure_supported = False`: a dumb fixed-5-sentence window (0.4070) BEATS detected scenes (0.4003).** Commit `cba64a577` (2026-08-14) reached the same conclusion three weeks later from scratch | A (LOCALITY null, two arms: fixed5 0.4070, Kmean-random 0.3710) | OK | EXP-ONLY | OFF-PATH | **C4** | not superseded by the E3 Centering arc (different mechanism; corroborates) | STATE:VERIFIED |
| C6 | leak-proof relational inference | `data/exp_leakproof_relational_inference_heldout_v1/metrics.json` | `HARD_PASS`, **full**, `2026-07-26T20:10:03`. LEARNED 0.6534 vs RAW_GROUNDING 0.5459 (+0.1076); leak witness 0/22299. **NAME CORRECTION: S1 sec 5.2 #15 names the siblings `exp_leakproof_relational_inference_context_sweep_v1` / `_twonew_v1`; those directories DO NOT EXIST. The real names are `data/exp_leakproof_relinfer_context_sweep_v1` and `data/exp_leakproof_relinfer_twonew_v1`** | A, exemplary (RANDOM_INIT 0.5246, STRUCT_2HOP 0.5602, POPULARITY 0.5055, COLLAPSE 0.4978) | OK | EXP-ONLY | OFF-PATH | **C2** | UNCHECKED | STATE:VERIFIED |
| C7 | text-at-scale meaning learning | `data/exp_scale_meaning_learn_arc_heldout_v2/metrics.json` | `HARD_PASS_CLEAN_WIN`, **full**, `2026-07-27T16:01:25`. From-scratch text-at-scale beats grounding on held-out-NEW semantic: zavg 0.6469 vs raw 0.5968 | A (`RAW_TEXT-RANDOM = 0.1034`, per-seed min stated) | OK | EXP-ONLY | OFF-PATH | C3 (supply side) | UNCHECKED | STATE:VERIFIED |
| C8 | grounded inductive concept encoder | `data/exp_grounded_inductive_concept_encoder_heldout_new_v3/metrics.json` | `HARD_PASS`, **full**, `2026-07-26T16:22:42`. enc_poor 0.6741 vs aa_poor 0.4403 (+0.2339 vs bar 0.03), n=2024 power_ok | A | OK | EXP-ONLY | OFF-PATH | C3 | UNCHECKED | STATE:VERIFIED |
| C9 | encoder retrain at scale (assembly) | `data/exp_situation_model_assembly_encoder_retrain_scale_v1/metrics.json` | **CORRECTION: verdict is `CLEAN_PASS` and `run_mode` is `grid`, NOT "full".** `2026-07-31T09:23:53`. Retrain breaks the held-out-entity wall in `d1_div40`/`d1_div80`: all 3 query types >=0.60, `best_loop 0.830`, `name<->name frozen 0.057`. Its own verdict text ends **"ESCALATE TO SCALE"** -- an explicit un-taken next step | A (degenerate `d6` arm FAILS the guard -- a genuine can-fail control) | OK | HDLAB:`encoder_retrain_persist.py` (registered) | **OFF-PATH (opt-in by design -- this is the documented precedent, not an islanding)** | C3 (via anchors), C4 | UNCHECKED | STATE:VERIFIED |
| C10 | encoder transfer stress (harness swap) | `data/exp_encoder_alltype_transfer_stress_v1/metrics.json` | **CORRECTION: `run_mode` is `lite`, NOT "full".** `HARD_PASS`, `2026-08-01T01:27:38`. All 3 stress conditions clear lift >=0.05 on >=2 types incl. non-coref (c1_harder +0.108 / +0.142 / +0.231). It validates C9 rather than adding a lever -- **and a `lite` run is a weaker validation than the source note implies** | A (frozen vs tuned arms, held-out eval-draw, independent harness) | OK | HDLAB:`encoder_retrain_persist.py` | OFF-PATH (opt-in) | C4; C3 indirectly | UNCHECKED | STATE:VERIFIED |
| C11 | frame-order recovery under superposition | `data/exp_frame_order_recovery_hard_comprehension_v2/metrics.json` | `HARD_PASS`, **full**, `2026-07-06T15:05:37`. role->block ORDER recovered at 1.000 vs occupancy control 0.195; parse survives superposition at 0.800 | A (chance 0.167; occupancy control) | OK | EXP-ONLY | OFF-PATH | C4/C3 | UNCHECKED | STATE:VERIFIED |
| C12 | joint operator capstone | `data/exp_joint_operator_capstone_selective_readouts_v1/metrics.json` | `HARD_PASS_JOINT_OPERATOR_CAPSTONE_BOTH_SOLVED...`, **full**, `2026-07-15T23:36:19`. Two operators solved jointly, no interference (rel_drop -0.0061/0.0000); 9 declared gates all True | A (`SHUF 0.4222`, chance 0.52, freq 0.7778) | OK | EXP-ONLY | OFF-PATH | C3 (composition infra) | UNCHECKED | STATE:VERIFIED |
| C13 | read-grow relation identity | `data/exp_read_grow_relation_identity_v3_richness_sweep/metrics.json` | `HARD_PASS`, **full**, `2026-07-17T04:48:28`. failure-rate curve 0.267 -> 0.000; ablation control fired at every level | A | OK | EXP-ONLY | OFF-PATH | C2 | UNCHECKED | STATE:VERIFIED |
| C14 | whitening on the FACT STORE | `data/exp_hd_fact_store_semantic_capacity_whitening_v1/metrics.json` | verdict `MEASURED`, **`run_mode` ABSENT**, `2026-07-24T16:29:41`. **This is the closest thing to B1-B4's whitening lever already touching a live organ** (`hdlab/hd_fact_store.py` IS in the 39-module closure). **Read this before acting on B1** | UNPINNED (verdict is `MEASURED`, not a pass) | OK | related module HDLAB:`hd_fact_store.py` | **the fact store is LIVE; this whitening variant is not** | C3, C1 | UNCHECKED | STATE:VERIFIED |
| C15 | reader component oracle-ablation audit | `data/exp_reader_component_oracle_ablation_audit_v1/metrics.json` | `AUDIT_SANITY_OK`, **full**, `2026-07-23T20:07:04`. An audit artifact, not a capability claim | UNPINNED | OK | EXP-ONLY | OFF-PATH | -- | UNCHECKED | STATE:VERIFIED |
| C16 | multi-turn loop, oracle vs real | `data/exp_multi_turn_loop_realtext_oracle_vs_real_compounding_v1/metrics.json` | **CORRECTION: verdict is `HARD_FAIL`**, **full**, `2026-07-23T04:53:04`. S1 sec 5.3 lists it among cells "a C3 hunt must not skip" without saying it FAILED. It is a closed route, not a lead | UNPINNED | OK | EXP-ONLY | OFF-PATH | -- (closes a route) | UNCHECKED | STATE:REFUTED |

#### Group D -- brain-mechanism organs from the zero-visibility families

| # | system | evidence | claim (as read on disk) | floor | disk | module | live | moves | supersede | STATE |
|---|---|---|---|---|---|---|---|---|---|---|
| D1 | k-WTA / sparsity free axis at production N | `data/exp_substrate_sparsity_free_axis_v5_wm_fixed_n4096_seed_7/metrics.json` | `HARD_PASS`, **full**, `2026-07-02T00:26:04Z`, 7 seed dirs, N=4096. `rho_c <= -0.60` at all 9 (M,alpha) pairs; cross-seed cv < 0.15. **Best-evidenced member of a family that is 17-of-17 invisible and has ZERO registry presence for `kwta`** (measured: 0 rows) | A -- rare explicit KEYS for this era (`hp_random_floor`, `positive_control_wm_ok`) | OK | EXP-ONLY | OFF-PATH | C3 (sparse coding is a first-order brain constraint) | UNCHECKED | STATE:VERIFIED |
| D2 | Hopfield attention inside a real LM | `data/exp_substrate_tier4_hopfield_attention_substitution_pythia160m_v1/metrics.json` | `HARD_PASS`, **full**, no date, 2 seeds. Substrate attention is training-stable inside Pythia-160M; **`ppl_ratio(substrate/baseline) = 0.94`** -- slightly BETTER perplexity than the attention it replaced. A `llama_3_2` sibling exists | A-weak (the baseline it is ratioed against; no separate scramble) | OK | related HDLAB:`modern_hopfield_readout.py` | OFF-PATH | C3 (architecture) | UNCHECKED | STATE:VERIFIED |
| D3 | Hopfield spurious-minima control | `data/exp_hopfield_spurious_minima_cpu_v1/metrics.json` | `HARD_PASS`, **run_mode `smoke`**, undated. genuine-convergence 0.957 (bar 0.90). **This is the specific safety property any Hopfield read-out must pass, and A4/D2 do not cite it** **MERGE NOTE: the two ledgers disagreed on this row** (here VERIFIED, reading-tier row M229 FOUND). Re-read on disk this session: `HARD_PASS`, run_mode `smoke`, *"genuine-convergence=0.957"* against a stated 0.90 bar. The floor is real but lives in PROSE, which the reading tier's shape detector cannot see -- that is why it scored FOUND. **VERIFIED stands.** | PROSE | OK | EXP-ONLY | OFF-PATH | C3 (prerequisite control) | UNCHECKED | STATE:VERIFIED |
| D4 | sharp-wave ripple organ | `data/exp_hippocampal_sharp_wave_ripple_v1/metrics.json` | `HARD_PASS`, **run_mode `smoke`**, undated. `fidelity_fast 1.0000` vs **random 0.0857**; wrong_fidelity 0.0000. Registry term `ripple` = **0 rows** | PROSE (floor lives inside `verdict_msg`) | OK | EXP-ONLY | OFF-PATH | -- | UNCHECKED | STATE:VERIFIED |
| D5 | ACC / EVC adaptive halting | `data/exp_substrate_acc_evc_adaptive_halting_v1_smoke/metrics.json` | `HARD_PASS`, **run_mode `smoke`**, `2026-07-08T13:53:23`. `acc[FIXED 0.133 ADAPT 0.733 ORC 0.733]` -- **the adaptive arm EQUALS ITS ORACLE** with fewer hops; signal-specificity `corr[A=1.000 S=-0.071]`. **There is NO FULL run: `_v1` and `_v1_selftest` are SELFTEST_OK only.** Registry term `acc_evc` = 0 rows. Same decision the newly-landed foraging organ makes, and foraging's prereg does not cite it | ARM, inside `verdict_msg`: `accpc[FIXED ADAPT RAND SCR ORC]` | OK | EXP-ONLY | OFF-PATH | C3 / foraging | UNCHECKED | STATE:VERIFIED |
| D6 | integrated hippocampal stack (DG+CA3+Marr+CLS+replay) | `data/exp_substrate_concept_encoder_spoke3_dg_ca3_marr_cls_replay_v1_smoke/metrics.json` | `HARD_PASS`, **run_mode `smoke`**, `2026-07-02T23:46:48`. Five-way lesion ladder. **`after=0.000` on BOTH `MARR` and `NO_CONSOL` -- the consolidation arm did not retain**, consistent with E1/E2 | ARM (`CORTEX` / `NO_CONSOL` / `NAIVE_WTA` are the lesions; no key contains "control") | OK | EXP-ONLY | OFF-PATH | -- | UNCHECKED | STATE:VERIFIED |
| D7 | multi-hop PFC chunked decomposition | `data/exp_substrate_multihop_pfc_chunked_2hop_decomposition_v1_smoke/metrics.json` | `HARD_PASS_CHAIN_GRADE_BARRIER_1_VIA_CHUNKING`, **run_mode `smoke`** | UNPINNED | OK | EXP-ONLY | OFF-PATH | C2 | UNCHECKED | STATE:VERIFIED |
| D8 | heterogeneous plasticity / STDP fair harness | `data/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness*/metrics.json` (resolved by prefix, 1 match) | `HARD_PASS`, **full**, no date. Built explicitly to be a fair test (see the name). Registry term `stdp` = **0 rows**; family 4-of-4 invisible | UNPINNED | OK | EXP-ONLY | OFF-PATH | learning layer | contested by E12 (the `_v2_RESCUE` HARD_FAILed) | STATE:VERIFIED |
| D9 | multi-scale grid-cell composition | `data/exp_crt_multi_scale_grid_cell_composition_v1/metrics.json` | `HARD_PASS`, **run_mode `smoke`**, undated. **NO FLOOR -- an unfloored pass is not evidence.** The entire entorhinal/grid family is this one cell | **NO FLOOR** | OK | EXP-ONLY | OFF-PATH | -- | UNCHECKED | STATE:VERIFIED |
| D10 | multi-bank working memory (K extension) | `data/exp_substrate_working_memory_multi_bank_K_extension_adversarial_v1/metrics.json` | `HARD_PASS`, **full**, no date. naive random recall 0.0172 vs multi-bank **1.0000**, cv 0.0000, route_acc 1.0000, adversarial within 0.05 | A | OK | HDLAB:`situation_model_multibank.py` (8,044 B, **registered**) | OFF-PATH | C4 | UNCHECKED | STATE:VERIFIED |
| D11 | theory-of-mind Sally-Anne (nested HRR) | `data/exp_theory_of_mind_sally_anne_nested_hrr_v1/metrics.json` | `HARD_PASS`, **full**, `2026-06-28T04:33:44Z`. Gate-decided **WIRE** on 2026-08-05 and never executed. **The registry itself flags a naming defect here: a `state_of_mind.py` row is annotated "MISLABELED NAME, NOT Theory-of-Mind"** -- so this capability's registry trail is actively misleading | UNPINNED (source reports Q2 0.806 vs 0.138, oracle 1.0, 5 seeds -- **not re-read by me**) | OK | EXP-ONLY | OFF-PATH | C4 | UNCHECKED | STATE:VERIFIED |
| D12a | CLIP-era visual grounding coherence | `data/exp_visual_grounding_coherence_v1/metrics.json` | `HARD_PASS`, **`run_mode` ABSENT**, `2026-07-18T13:50:41`. chance 0.050, shuffled 0.074, T1 0.635 | A | OK | **EXP-ONLY -- "wire it" means BUILD it** | OFF-PATH | -- | UNCHECKED | STATE:VERIFIED |
| D12b | vision integrated recognize-bind-ground | `data/exp_vision_integrated_recognize_bind_ground_v1/metrics.json` | `HARD_PASS_INTEGRATED_PIPELINE__NOVEL_CLASS_WALL_CONFIRMED`, **full**, `2026-07-23T12:02:20` | A (chance 0.125, label-shuffle 0.189, SCRAM 0.386, word-scramble 0.143) | OK | EXP-ONLY | OFF-PATH | -- | UNCHECKED | STATE:VERIFIED |
| D12c | reader image-word grounding | `data/exp_reader_image_word_grounding_v1/metrics.json` | `PASS_GROUNDING`, **full**, `2026-07-22T00:28:57`. chance 0.0169; rungs 0.996 / 1.000 / 0.977 | A | OK | EXP-ONLY | OFF-PATH | -- | UNCHECKED | STATE:VERIFIED |
| D13a | MAVEN-ERE gated causal | `data/exp_maven_ere_convergence_gated_causal_v2_fulldev/metrics.json` | **`HARD-PASS` (HYPHEN)**, `run_mode` **`full_dev`**, `2026-08-11T09:19:45`. floor 5.93, scramble 3.48, full_v2 14.78. **Two convention traps in one row: the hyphen AND the `_fulldev` suffix** | A | OK | **EXP-ONLY -- BUILD** | OFF-PATH | C2 | UNCHECKED | STATE:VERIFIED |
| D13b | MAVEN-ERE gated subevent | `data/exp_maven_ere_convergence_gated_subevent_v1_fulldev/metrics.json` | `HARD-PASS`, `full_dev`, `2026-08-11T10:06:27`. floor 2.86, scramble 2.78, full_v2 13.63, transferred=True | A | OK | **EXP-ONLY -- BUILD** | OFF-PATH | C2 | UNCHECKED | STATE:VERIFIED |
| D14 | teacher-free relational encoder | `data/exp_teacher_free_relational_encoder_cn_subgraph_v1/metrics.json` | `HARD_PASS`, **full**, `2026-07-08T15:34:29`, 5 seeds. arm Z **497.90** vs random-init Z 148.97, control Z 21.42; ablation collapses | A | OK | **EXP-ONLY -- BUILD** | OFF-PATH | C3 (supply) | UNCHECKED | STATE:VERIFIED |
| D15 | gated fusion (+0.297) | `data/exp_grounding_gated_fusion_relation_inference_mammal_v1/metrics.json` | `HARD_PASS_GATED_FUSION_RECOVERS_GROUNDING`, **full**, `2026-07-14T03:26:29`. gated MRR **0.6619** vs relational 0.3645. **Gate-decided WIRE on 2026-07-28, tagged "TOP forgotten asset", and named in no plan document since** | A (RANDOM 0.0275, SCRAMBLE 0.5682, ORACLE 1.0) | OK | EXP-ONLY (4 registry rows mention it) | OFF-PATH | C2, C3 | UNCHECKED | STATE:VERIFIED |
| D16 | learned lexicon grounding at scale | `data/exp_lexicon_learned_grounding_scaled_v1/metrics.json` | `HARD_PASS`, **full**, no date. RANDOM 0.010 vs LEARNED 0.940 vs ORACLE 1.000 at V=200 | A | OK | EXP-ONLY | OFF-PATH | C3 (supply) | UNCHECKED | STATE:VERIFIED |
| D17 | social relational grounding axis | `data/exp_social_relational_grounding_axis_v1/metrics.json` | `HARD_PASS`, **full**, `2026-08-07T10:35:52`. scramble 0.483, ablation 0.000, open-vocab 0.833. **UNDERPOWERED: n=12 seed / 6+6 test. Ranked low deliberately** | A | OK | EXP-ONLY (registered) | OFF-PATH | C3 | UNCHECKED | STATE:VERIFIED |
| D18 | cleanup floor (learned encoder) | `data/exp_cleanup_floor_learned_encoder_v1/metrics.json` | `META_BRANCH3_CHAIN_GRADE_ELIGIBLE`, **full**, no date. Shannon floor holds across 3 codebook families (0.0217/0.0267/0.0150). **A negative-shaped positive: it establishes a FLOOR others can be scored against** | it IS a floor | OK | EXP-ONLY (registered) | OFF-PATH | C3 (scoring infra) | UNCHECKED | STATE:VERIFIED |
| D19 | RNS/CRT high-vocabulary decoder | `data/exp_generation_decoder_rns_crt_highvocab_v1/metrics.json` | `HARD_PASS`, **full**, `2026-07-05T18:46:21`. exact-ordered decode **1.000 at V=65536** where correlated single-block falls to 0.160 | A (`scram` collapses to 0.000; iid ceiling 1.000) | OK | EXP-ONLY | OFF-PATH | C3 (scale: 647 -> 5491 anchors) | UNCHECKED | STATE:VERIFIED |
| D20 | GSBC block-local factorizer | `data/exp_generation_decoder_gsbc_native_blocklocal_v1/metrics.json` | `HARD_PASS`, **full**, `2026-07-05T13:32:09`. block-local sparse 1.000 where the **dense bipolar resonator collapses to 0.000 on the same fillers**. Named finding: dense multiply-bind is the encoding mismatch | A (`dense_gsbc_fullreso 0.000` vs `dense_synth_fullreso 1.000`) | OK | EXP-ONLY | OFF-PATH | C3 (architecture) | UNCHECKED | STATE:VERIFIED |
| D21 | learned codebook generalisation gate | `data/exp_learned_codebook_generalization_gate_v1/metrics.json` | `HARD_PASS`, **`run_mode` ABSENT**, `2026-07-20T02:26:34`. ppmi_svd AUC 0.927+-0.001 vs random 0.496; 8M-token corpus, V=10000, N=1024 | A (`random` neg-control 0.496) | OK | EXP-ONLY (registered) | OFF-PATH | C3 (anchor quality) | UNCHECKED | STATE:VERIFIED |
| D22 | entmax sparse read-out envelope | `data/exp_c1_entmax_envelope_sweep_v2/metrics.json` | `HARD_PASS`, **full**, no date. 80/80 discriminating cells win on FLOPs at ISO-recall (median 94% reduction), **recall 1.000 vs 1.000, delta +0.000 -- it EXPLICITLY does not move C3 quality.** Listed so nobody mistakes "read-out WIN" in the title for a quality lift. Its sibling `exp_substrate_c1_entmax_alpha_readout_v1` has **NO DIRECTORY on disk** (confirmed) **MERGE CORRECTION 2026-08-14: the "NO DIRECTORY on disk (confirmed)" claim about the sibling is WRONG.** The directory exists as `data/substrate_C1_entmax_alpha_readout_v1/` -- no `exp_` prefix, capital `C1` -- and reads `HARD_PASS`, run_mode `full`. It is now row CG-F18. A fourth absence-claim-by-search failure for sec 8 rule 3. | B (contrast arms, envelope grid) | OK / sibling **NO DIR** | EXP-ONLY | OFF-PATH | -- (efficiency only) | UNCHECKED | STATE:VERIFIED |

#### Group E -- refutations and closed routes (a negative prevents an expensive repeat; these are assets)

| # | system | evidence | claim (as read on disk) | floor | disk | module | live | moves | supersede | STATE |
|---|---|---|---|---|---|---|---|---|---|---|
| E1 | consolidation schedule -- conjunction | `data/exp_consol_conjunction_replay_v1/metrics.json` | `REFUTE_CONSOLIDATION_NO_SCHEDULE_ADVANTAGE_CONJUNCTION_IS_READOUT_EFFECT`, **full, 5 seeds**, `2026-07-15T12:40:33`. INTERLEAVED 1.0000 = CONTINUAL 1.0000, **schedule gap 0.0000**, compute_matched. Positively attributes the effect **to the READ-OUT** -- a July result pointing at the August C3 diagnosis. **ZERO cert-ledger rows: it never entered the certification system at all** | A, textbook: chance 0.5118, FREQ_NULL 0.4768, SHUFFLE 0.5192, MEMO 0.4768, ORACLE 1.0000 | OK | EXP-ONLY | n/a | closes a route | n/a | STATE:REFUTED (the hypothesis; the CELL is sound) |
| E2 | consolidation schedule -- inductive entity | `data/exp_consol_inductive_entity_replay_cskg_v1/metrics.json` | `REFUTE_REPLAY_NO_INDUCTIVE_ADVANTAGE`, **full, 5 seeds**, `2026-07-15T11:40:51`. Replay beats CONTINUAL (+0.0249) but **FAILS to beat popularity** (`beat_pop -0.0020`) -- and reports the failure rather than headlining the arm it won | A: RANDOM 0.0021, SHUFFLE 0.0026, SCRAMBLE 0.0274, POP_RELFREQ 0.0576, ORACLE 0.1030 | OK | EXP-ONLY | n/a | closes a route | n/a | STATE:REFUTED (the hypothesis) |
| E3 | interleaved replay sibling | `data/exp_consol_interleaved_replay_v1/metrics.json` | **CORRECTION: verdict is `HARD_PASS`, full, `2026-07-15T02:51:27`** -- S1 sec 6.3 groups all three 07-15 replay cells as "three properly-floored July refutations". Two are refutations; **this one is a PASS** | UNPINNED | OK | EXP-ONLY | OFF-PATH | -- | UNCHECKED | STATE:VERIFIED |
| E4 | SSP phase-rotation replay operator fix | `data/exp_course_c_operator_fix_ssp_phase_rotation_replay_v1/metrics.json` | `OPERATOR_FIX_CONFIRMED_CONSOLIDATION_INCONCLUSIVE`, **full**, `2026-07-11T03:46:40`. Third independent July result against consolidation advantage | UNPINNED | OK | EXP-ONLY | n/a | closes a route | n/a | STATE:VERIFIED |
| E5 | ATL hub-and-spoke, gen 1 | `data/exp_substrate_hub_spoke_E1_encoder_v1/metrics.json` | **`HARD_FAIL`**, **full**, no date | A | OK | EXP-ONLY | n/a | -- | n/a | STATE:REFUTED |
| E6 | ATL hub-and-spoke, gen 2 | `data/exp_substrate_hub_spoke_E1_v2_diverse_algorithm/metrics.json` | **`MIDDLE_BAND`**, **full**, no date | A | OK | EXP-ONLY | n/a | -- | n/a | STATE:REFUTED |
| E7 | ATL hub-and-spoke, gen 3 | `data/exp_substrate_hub_spoke_E1_v3_MRC_calibrated_routing/metrics.json` | **`HARD_FAIL`**, **full**, no date. **Three in-house refutations of our own ATL implementations. `notes/lit_scan_atl_hub_and_spoke_2026-08-13.md` was commissioned on the same mechanism and cites NONE of them** -- so the scan could not do its most valuable job, which is to explain WHY they failed. Registry term `hub_spoke` = 0 rows | A | OK | EXP-ONLY | n/a | (ATL is the brain's answer to C3's exact defect -- these say our version of it does not work yet) | n/a | STATE:REFUTED |
| E8 | cerebellum SR rollout | `data/exp_pfc_gate_cerebellum_sr_rollout_v1_smoke/metrics.json` | **`HARD_FAIL_NO_CEREBELLAR_CONSUMER`**, smoke, `2026-07-07T18:16:38`. **The verdict string IS the finding: a machine-readable record of the islanding failure mode.** Registry term `cerebell*` = 0 rows | A | OK | EXP-ONLY | n/a | -- | n/a | STATE:REFUTED |
| E9 | cerebellar random expansion write | `data/exp_substrate_cerebellar_random_expansion_write_v1/metrics.json` | **`HARD_FAIL`**, smoke, no date | A | OK | EXP-ONLY | n/a | -- | n/a | STATE:REFUTED |
| E10 | binding operator x capacity | `data/exp_substrate_binding_op_x_capacity_v1_seed_7/metrics.json` | **`HARD_FAIL`**, **full**, `2026-07-01T04:18:36Z`. HARD_FAIL on all three seeds (7/13/19) -- a well-replicated negative, equally invisible | A | OK | EXP-ONLY | n/a | -- | n/a | STATE:REFUTED |
| E11 | iterative settling with depth | `data/exp_grounding_iterative_settling_cascade_depth_v1/metrics.json` | **`HARD_FAIL_NO_EXTENSION`**, **full**, `2026-07-09T13:05:45`. **This is the closest thing to a prior refutation of A8** (cue-clamped iterative cleanup) and no sweep hunting passes would ever have surfaced it | UNPINNED | OK | EXP-ONLY | n/a | contests A8 | n/a | STATE:REFUTED |
| E12 | PCGrad + CFRPE + STDP rescue | `data/exp_substrate_pcgrad_cfrpe_stdp_v2_RESCUE/metrics.json` | **`HARD_FAIL`**, **full**, no date. The rescue attempt on the STDP arc failed. The `_RESCUE` suffix is itself a convention no current search knows | UNPINNED | OK | EXP-ONLY | n/a | contests D8 | n/a | STATE:REFUTED |

#### Group F -- capabilities that fell off across the six review renames (module plane)

| # | system | evidence | claim | floor | disk | module | live | moves | supersede | STATE |
|---|---|---|---|---|---|---|---|---|---|---|
| F1 | `glass_box_loop` | `hdlab/glass_box_loop.py` | **EXISTS, 19,174 B.** No registry row (name test), **not in the 39-module closure**, zero importers, no `data/*glass_box_loop*` directory. `architecture_audit_2026-08-11` item 7 names it as *exactly* the arbitration/fusion that `three_tier_loop.answer()` lacks (Gap G1), validated on real ConceptNet V=48000. **The capability CLAIM is unverified by me -- only the file's existence and its off-path status are** | UNPINNED | file OK, **no result dir found** | HDLAB:`glass_box_loop.py` | **OFF-PATH** | C2/C3 (arbitration) | n/a | STATE:VERIFIED (existence + off-path) / claim UNVERIFIED |
| F2 | `wordnet_polarity_propagation` | `hdlab/wordnet_polarity_propagation.py` | **EXISTS, 16,922 B.** No registry row, not in closure. Reported (S3) as **the repo's ONLY live dictionary lookup** (`nltk.corpus.wordnet`). Given the open defect is lexical within-neighbourhood separation, a dictionary path no plan knows about is directly on topic | UNPINNED | file OK | HDLAB | **OFF-PATH** | **C3** | n/a | STATE:VERIFIED (existence) / claim UNVERIFIED |
| F3 | `word_learning_tool` | `hdlab/word_learning_tool.py` | **EXISTS, 6,504 B.** Not in closure. Its one landed evaluation **HARD_FAILED**; the tool itself self-tests PASS. Do not read the tool's existence as a capability | UNPINNED | file OK | HDLAB | OFF-PATH | -- | n/a | STATE:VERIFIED (existence) |
| F4 | `sr_routing` multihop (+0.253) | registry row only | Registry status `orphaned_source_not_locatable_retired_2026-08-03`. **I searched `data/*sr_routing*` and found NOTHING; no `hdlab/sr_routing.py`.** The integration ledger says git-recover before reinventing. **Until the source is located this is a CLAIM, not an asset** | UNPINNED | **NOT LOCATED** | **NOT LOCATED** | n/a | C2 | n/a | STATE:FOUND |
| F5 | `scale_win` TinyTransformer encoder | 3 registry rows | Learned from scratch on 237.7M ARC tokens; claimed "+0.050 semantic / +0.071 relational" over grounding; gate=WIRE, status `TRAPPED_SHARED`, zero `hdlab` imports. **No `data/*scale_win*` directory exists.** **EXPERIMENT-ONLY -- "wire it" means BUILD it.** Flagged in `architecture_audit_2026-08-11` as half of the **#1 shore-up** | UNPINNED | **no dir under this name** | **BUILD** | n/a | C3 | n/a | STATE:FOUND |
| F6 | 39,707-word grounding norms | `data/grounding_testbed` | Lancaster sensorimotor + Brysbaert concreteness + Warriner VAD + AoA. The other half of the 08-11 **#1 shore-up**; a grep-confirmed disconnected island. **Directory contents not enumerated by me** | n/a (a data asset, not a claim) | UNVERIFIED | data asset | OFF-PATH | C3 (supply) | n/a | STATE:FOUND |
| F7 | `vamp_ep_deep_chain_solver` | 1 registry row | "The repo's best deep-chain mechanism", acc 1.000 to depth ~200, K=5000, 30% noise. SHELVE with revival = NL causal-chain transfer smoke; never revisited. **`data/*vamp*` returns only SVAMP math cells -- a NAME COLLISION, not this asset.** Source not located under that name | UNPINNED | **NOT LOCATED** | NOT LOCATED | n/a | C2 | n/a | STATE:SHELVED -- revival criterion (from the 08-04 integration ledger): **an NL causal-chain transfer smoke.** Locate the source first |
| F8 | `k_cliff_scaling`, `profiling` | `hdlab/k_cliff_scaling.py` (1,940 B), `hdlab/profiling.py` (2,134 B) | **Both EXIST and both are REGISTERED.** They are the only two modules that have **provably never executed** (S3). Flagged for quarantine on 2026-07-25; still not quarantined | n/a | OK | HDLAB, registered | OFF-PATH | -- | n/a | STATE:SHELVED -- revival criterion: **none. Quarantine candidates; delete only via a deliberate maintenance pass, never bundled with other work** |
| F9 | the "24 unregistered self-test-PASS modules" | `hdlab/*.py` | **CORRECTION, measured today: 8 of the 24 now CARRY a registry row** (`context_retention, coref_distractor_suppress, definitional_predicate_v61, event_centrality_coref, goal_outcome_relation_grounded, outcome_event_extraction, script_grain_acquisition_loop, semantic_parser`). **16 still do not** (`atom_consultation, bayesian_inference, char_positional_encoder, clarify_gate, conformal, dg_pattern_separation, glass_box_loop, late_combine, mcscript_extraction, modern_hopfield_readout, noise_channel, per_item_log, perceptron, temporal_trace, word_learning_tool, wordnet_polarity_propagation`). **All 24 files exist. NONE of the 24 is in the 39-module closure.** *Caveat: registry presence is a NAME substring test and can mis-fire both ways* | n/a | OK (24/24 files exist) | HDLAB x24 | **0 of 24 LIVE** | mixed | n/a | STATE:VERIFIED |
| F10 | `situation_model_multibank`, `encoder_retrain_persist` | `hdlab/*.py` | Both EXIST (8,044 B / 5,639 B), both **REGISTERED**, both **OFF the default path**. `encoder_retrain_persist` is the documented **opt-in-by-design** precedent -- do not report it as islanded | n/a | OK | HDLAB, registered | OFF-PATH (one opt-in, one unclassified) | C4 / C3 | n/a | STATE:VERIFIED |
| F11 | `pipeline_status` field integrity | `data/capability_registry.jsonl` (127 rows measured today) | Wrong in **BOTH** directions (S3): 3 rows claim `WIRED_AND_PIPELINE_USED` and are not in the closure; **19 claim unreachable and ARE reachable, including `reading_grounding_loop` -- the pipeline entry point itself**; 13 modules sit inside the closure with no row, including `grounding_acquisition_loop`. **A compliance audit run against the registry cannot see the live path** | n/a | OK | infrastructure | n/a | -- | n/a | STATE:VERIFIED |
| F12 | measurement columns retired across renames | `notes/research_substrate_load_bearing_capability_assessment_2026-06-25.md` and the 07-25 integration audit | Three columns present in an old review and in **no** current one: **theoretical limit / closed-form bound per capability** (the exact column that settles "ceiling vs impl-bug"); **"truly enabling? YES/PARTIAL/NO"**; **bypass ratio** (4133/5327 = 78% of exp cells bypass `hdlab`, never recomputed). Plus **PP-217/225/226/227/228** (Tier A, 06-11) which have no successor identifier in any current scheme | n/a | note paths exist | n/a | n/a | -- | n/a | STATE:FOUND |

#### Group G -- the index machinery itself (fix these or everything above goes dark again)

| # | system | evidence | claim (as read on disk) | disk | STATE |
|---|---|---|---|---|---|
| G1 | the cert ledger | `data/substrate_index/meta/cert_ledger.jsonl` | 2,031 rows, 0 malformed, **>200 distinct top-level fields, not one present on all rows**. `cert_status` has **357 distinct values** -- not an enum. **574 terminal chain-graded cells; 552 with a live `metrics.json`.** File mtime says 2026-08-03 but the **newest ROW timestamp is 2026-07-25 (21 days stale)** -- the last write was not a last result. Only 157 of 2,031 rows carry a string `ts`. **Recommendation (S4): salvage the 14 resolving `supersedes` edges, freeze the rest read-only with a superseded-by pointer** | OK | STATE:VERIFIED |
| G2 | the supersession graph | same file | 15 fields carry supersession semantics, **164 raw edges; 93 dangle** (32 point at 16-hex content hashes that occur exactly ONCE in the whole 4.5 MB file and resolve to nothing; 61 are self-edges). By S4's count, **52 of 66 edges dangle**. Net effect: supersession removes almost nothing (2 cells). **Liveness must be derived from the LATEST RULING PER CELL, never from the citation graph** | OK | STATE:VERIFIED |
| G3 | the capability registry | `data/capability_registry.jsonl` | **127 rows** (counted today). Indexes CODE. **Intersection with the ledger's result universe = ZERO** -- they were never two views of one thing, so "make them agree" was never the right goal | OK | STATE:VERIFIED |
| G4 | the derived result index | `tools/result_index_join.py`, reports in `data/result_index_reports/` | Join key = result DIRECTORY NAME (96.4%); `atom_id` joins **0/1925**. On disk **7,623** results; **6,566 (86%) unindexed**; 5,136 undated; 53 dangling ledger keys (mostly unexpanded shell brace patterns written literally into the index). **Derived from disk every run -- there is nothing to remember to do, so there is nothing to forget.** Wired into `tools/session_start_hook.py` | OK, runs | **STATE:WIRED** |
| G5 | the 2026-06-25 archaeology tooling | `data/_archaeology_extractor.py`, `_archaeology_synthesize.py`, `_archaeology_inventory_enriched.jsonl` (2.4 MB), `_archaeology_summary.json` | A USER-directed archaeology sweep with almost this exact brief ran on **2026-06-25**; its tooling and its 3,269-experiment enriched inventory are still on disk and **were never read by any 08-14 sweep**. Its own conclusion then: *"2026-06 HARD_PASS NOT in cert ledger at all: 841 (65%)"*. **Today's finding is the same leak one stage downstream and worse.** Its headline numbers are QUOTED, never recomputed | files exist | STATE:FOUND |

### 5.4 GROUPS CG-A .. CG-G -- the chain-graded tier (from S5)

565 rows as written, plus one row this merge added (CG-G1). Column meanings are sec 3a's, with two
deviations stated by the source sweep: **`supersede` is UNCHECKED on every row** (only one edge in
the whole cert ledger resolves onto a live chain-graded cell) and **`live` is inherited from the
39-module runtime closure of sec 4, a MODULE-level statement, not a cell-level one.**

**The 280-row saturation grid that was group CG-E has been MOVED TO APPENDIX A.** It is half the
tier and one investigation; leaving it in the body defeats the cold-read function of this file.

#### Group CG-A -- ranked separation-geometry candidates (26 rows; ranking in sec 9c)

| # | cell | date (src) | verdict (as read) | run_mode | floor | disk | module | moves | STATE |
|---|---|---|---|---|---|---|---|---|---|
| A1 | `exp_substrate_etf_minilm_dim_expansion_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | C3,C1 | state=VERIFIED DUP-OF RP-B3 |
| A2 | `exp_pseudoinverse_real_encoder_keys_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | C3,C1 | state=VERIFIED DUP-OF RP-B9 |
| A3 | `exp_substrate_pca_prewhitening_codebook_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | C3,C1 | state=VERIFIED DUP-OF RP-B2 |
| A4 | `exp_encoder_retained_trace_requery_coarse_to_fine_v1` | 2026-07-08 (ts_iso) | HARD_PASS_RETAINED_TRACE_RECOVERS | full | ARM | OK | EXP-ONLY | C3 | state=VERIFIED DUP-OF RP-A3 |
| A5 | `exp_f6_bge_large_pinv_mmax_reaudit_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | C3,C1 | state=VERIFIED DUP-OF RP-B7 |
| A6 | `exp_kv_learned_projection_v1` | 2026-06-20 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | C3 | state=VERIFIED DUP-OF RP-B10 |
| A7 | `exp_pb_e5_vs_bge_pinv_headtohead_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | C3,C1 | state=VERIFIED DUP-OF RP-B8 |
| A8 | `exp_substrate_codebook_near_duplicate_diagnostic_cpu_v1` | 2026-06-12 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | C3,C1 | state=VERIFIED DUP-OF RP-A1 |
| A9 | `exp_substrate_capacity_cliff_fhrr_constant_derivation_v1` | 2026-07-17 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | C3,C1 | STATE:VERIFIED |
| A10 | `exp_cortex_context_retention_v2_3seed_full_chain_grade_m1p5_milestone_first_cortex_integ` | 2026-07-01 (ledger:ts) | HARD_PASS | full | A | OK | HD:`context_retention.py` | C3,C1,C4,C2 | STATE:VERIFIED |
| A11 | `exp_substrate_encoder_capacity_at_scale_battery_gpu_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | C3,C1 | STATE:VERIFIED |
| A12 | `exp_substrate_last_token_vs_whitening_mean_pool_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | ARM | OK | HD:`whitening.py` | C3,C1 | state=VERIFIED DUP-OF RP-B1 |
| A13 | `exp_hebb_vs_pseudoinverse_long_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | C3,C1 | state=VERIFIED DUP-OF RP-B5 |
| A14 | `exp_attention_salience_common_mode_detector_v1` | 2026-07-20 (ts_iso) | HARD_PASS_COMMON_MODE_DETECTOR_SEPARATES | full | A | OK | EXP-ONLY | C3,C1 | state=VERIFIED DUP-OF RP-A13 |
| A15 | `exp_pb_production_recipe_integration_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | C3,C1 | STATE:VERIFIED |
| A16 | `exp_f8_pinv_padfix_alpha_compound_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | C3,C1 | STATE:VERIFIED |
| A17 | `exp_generation_decode_selfmargin_dupclass_exact_v1` | 2026-07-06 (ts_iso) | HARD_PASS | full | A | OK | HD:`generation.py` | C3,C4 | STATE:VERIFIED |
| A18 | `exp_substrate_dim_expansion_subsumes_whitening_n_enc_10000_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | A | OK | HD:`whitening.py` | C3,C1 | state=VERIFIED DUP-OF RP-B4 |
| A19 | `exp_substrate_hallucination_detection_minilm_v1` | 2026-06-05 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | C3,C1 | state=VERIFIED DUP-OF RP-A12 |
| A20 | `exp_interference_avoidance_conjunctive_vs_additive_v1` | 2026-07-14 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | C3?,C1 | STATE:VERIFIED |
| A21 | `exp_metric_dependence_top_k_semantic_v3_3seed_full_chain_grade_semantic_top_k_cliff_brac` | 2026-07-02 (ledger:ts) | HARD_PASS | full | ARM | OK | HD:`semantic.py` **(in live closure)** | C3?,C1 | STATE:VERIFIED |
| A22 | `exp_substrate_cognitive_core_introspection_toolkit_v1` | 2026-06-05 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | C3? | STATE:VERIFIED |
| A23 | `exp_substrate_decomposition_resonator_alpha05_cpu_v1` | 2026-06-12 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | C3?,C4 | STATE:VERIFIED |
| A24 | `exp_anchor_compose_identity_shuffle_cskg_v2` | 2026-07-13 (ts_iso) | HARD_PASS_INDUCTIVE_ANCHOR_COMPOSE_IDENTITY_CLOSED | full | A | OK | EXP-ONLY | C3?,C4,BOUND | state=VERIFIED DUP-OF RP-A10 |
| A25 | `exp_integration_full_stack_hard_regime_v1` | 2026-07-05 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | C3? | STATE:VERIFIED |
| A26 | `exp_joint_operator_capstone_selective_readouts_v1` | 2026-07-15 (ts_iso) | HARD_PASS_JOINT_OPERATOR_CAPSTONE_BOTH_SOLVED_NO_INTERFERENCE_HEADDISC_CLEAN | full | A | OK | EXP-ONLY | C3? | state=VERIFIED DUP-OF RP-C12 |
#### Group CG-B -- remaining cells WITH A REAL FLOOR (148 rows)

A control arm, reference arm or prose floor reads on disk. Ordered by separation-geometry score descending, so the head of this group is the next place to look after CG-A.

| # | cell | date (src) | verdict (as read) | run_mode | floor | disk | module | moves | STATE |
|---|---|---|---|---|---|---|---|---|---|
| B1 | `exp_metacog_abstain_readout_signal_thresholding_v1` | 2026-07-20 (ts_iso) | HARD_PASS_EXISTING_SIGNAL_CARRIES_USABLE_CONFIDENCE | full | A | OK | EXP-ONLY | C3? | state=VERIFIED DUP-OF RP-A11 |
| B2 | `exp_grounding_bind_chain_systematicity_v1` | 2026-07-09 (ts_iso) | SYS=SYS_HARD_PASS/REACH=REACH_HARD_PASS/ORACLE=READOUT_LIMIT | full | A | OK | EXP-ONLY | C3? | STATE:VERIFIED |
| B3 | `exp_pb_pinv_llama_l15_keys_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | C3?,C1 | state=VERIFIED DUP-OF RP-B6 |
| B4 | `exp_anchor_compose_scaling_ladder_cskg_v3` | 2026-07-13 (ts_iso) | SCALING_HOLDS | full | A | OK | EXP-ONLY | C3? | STATE:VERIFIED |
| B5 | `exp_c1_entmax_envelope_sweep_v2` | UNDATED (none) | HARD_PASS | full | ARM | OK | EXP-ONLY | C3?,C1 | state=VERIFIED DUP-OF RP-D22 |
| B6 | `exp_consolidation_correct_regimes_v1` | 2026-07-16 (ts_iso) | HARD_PASS | full | ARM | OK | EXP-ONLY | C3?,C1 | STATE:VERIFIED |
| B7 | `exp_cortex_hippo_dense_layer_n_sweep_v1_seed_{7,13,19}` | 2026-07-01 (_start_marker) | HARD_PASS -- **MERGE CORRECTION 2026-08-14 -- DEMOTION, and it carries its re-check:** this row records `HARD_PASS`. All three `exp_cortex_hippo_dense_layer_N_sweep_v1_seed_{7,13,19}` directories read **`HARD_FAIL`**, run_mode `full`, message *"N=32768 ARM_STANDARD status: ERROR: OutOfMemoryError: CUDA out of memory"*. Enumerated the family with `os.listdir`: three directories, no `_smoke` sibling that could have carried the PASS. **This is an INFRASTRUCTURE ABORT, not a scientific negative** -- nothing was measured, so it is not REFUTED either. State FOUND. | smoke | A | OK | EXP-ONLY | C3?,C1 | STATE:FOUND |
| B8 | `exp_generation_decoder_gsbc_native_blocklocal_v1` | 2026-07-05 (ts_iso) | HARD_PASS | full | ARM | OK | HD:`generation.py` | C3? | state=VERIFIED DUP-OF RP-D20 |
| B9 | `exp_grounding_by_redundancy_joint_corruption_allometry_v1` | 2026-07-14 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | C3?,C1 | STATE:VERIFIED |
| B10 | `exp_integration_full_stack_full_fidelity_v1` | 2026-07-06 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | C3? | STATE:VERIFIED |
| B11 | `exp_pythia_kv_desat_v2` | 2026-06-21 (ledger:ts) | HARD_PASS | full | A | OK | EXP-ONLY | C3?,C1 | STATE:VERIFIED |
| B12 | `exp_substrate_abduction_f1_weakest_signature_kernel_kgram_xor_groundtruth_cpu_v1` | 2026-06-15 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | C3?,C1 | STATE:VERIFIED |
| B13 | `exp_substrate_cortex_hippo_dense_layer_m_sweep_v3_seed_{7,13,19}` | 2026-07-01 (ledger:ts) | HARD_PASS | full | A | OK | EXP-ONLY | C3?,C1 | STATE:VERIFIED |
| B14 | `exp_substrate_permutation_binding_multiocc_v2_full` | 2026-06-25 (git-first-commit) | HARD_PASS **MERGE NOTE: the two ledgers disagreed** (here VERIFIED, reading-tier row M140 FOUND). Re-read on disk: `HARD_PASS_CHAIN_GRADE`, run_mode `full`, `3-seed mean perm=1.0000 cv=0.0000`, `FHRR=0.0629`, `lift=0.9371`. The floor is the `FHRR` arm, stated in PROSE -- a shape-detector false negative, not an absent floor. **VERIFIED stands**, and this is the top-ranked cell of the chain-graded tier. | full | A | OK | EXP-ONLY | C3? | STATE:VERIFIED |
| B15 | `exp_counterfactual_regret_comparison_vmpfc_v1` | 2026-06-28 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | C3? | STATE:VERIFIED |
| B16 | `exp_cross_axis_m_n_k_discriminating_arm_v2_3seed_full_chain_grade_substrate_axes_m_n_k_f` | 2026-07-02 (ledger:ts) | MIDDLE_BAND | full | A | OK | EXP-ONLY | C3? | STATE:REFUTED |
| B17 | `exp_h_hotpotqa_ingest_v1` | 2026-06-22 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | C3?,C2 | STATE:VERIFIED |
| B18 | `exp_scale_meaning_learn_arc_heldout_v2` | 2026-07-27 (ts_iso) | HARD_PASS_CLEAN_WIN | full | A | OK | EXP-ONLY | C3?,C2 | state=VERIFIED DUP-OF RP-C7 |
| B19 | `exp_substrate_abduction_f1b_confound_break_recoverability_vs_infopreservation_cpu_v1` | 2026-06-15 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | C3?,C2 | STATE:VERIFIED |
| B20 | `exp_substrate_ultrametric_clustering_phase_diagram_v1` | 2026-06-28 (git-first-commit) | HARD_PASS | full | A | OK | HD:`ultrametric_clustering.py` | C3? | STATE:VERIFIED |
| B21 | `exp_substrate_wikipedia_ppmi_svd_scale_up_full_n10k_formal_3seed_cg_honest_negative_supe` | 2026-07-03 (_start_marker) | MEASURED_BOUND_LOW_DELTA | full | A | OK | HD:`char_trigram_encoder.py` | C3?,C4 | STATE:VERIFIED |
| B22 | `exp_visual_grounding_coherence_v1` | 2026-07-18 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | C3? | state=VERIFIED DUP-OF RP-D12a |
| B23 | `exp_b_delta_readout_lever_transfer_v2` | UNDATED (none) | HARD_PASS | full | A | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| B24 | `exp_consolidated_reader_passive_mechanism_heldout_v1` | 2026-07-24 (ts_iso) | PASSIVE_MECHANISM_CAPABILITY_EARNED | full | A | OK | EXP-ONLY | -- | state=VERIFIED DUP-OF RP-C1 |
| B25 | `exp_learned_codebook_generalization_gate_v1` | 2026-07-20 (ts_iso) | HARD_PASS | ABSENT | A | OK | EXP-ONLY | C1 | state=VERIFIED DUP-OF RP-D21 |
| B26 | `exp_multiplicative_composition_lever_v1_cpu_v1` | 2026-06-20 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B27 | `exp_nativelang_svo_vsa_probe_v1` | 2026-07-16 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B28 | `exp_pb_mmr_real_encoder_clustered_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B29 | `exp_srn_shrink_probe_replication_v1` | 2026-07-18 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B30 | `exp_substrate_anchor4_encoder_family_n16384_gpu_v1_seed_{7,13,19}` | 2026-06-30 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B31 | `exp_substrate_anchor4_encoder_family_v4_seed_7` | 2026-06-30 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B32 | `exp_substrate_capacity_composition_full_b2xb4xhier_v1_n2048_gpu` | 2026-06-04 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| B33 | `exp_substrate_hallucination_robustness_hard_negatives_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B34 | `exp_substrate_pp8_learned_discriminability_probe_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B35 | `exp_substrate_real_encoder_capabilities_v1` | 2026-06-05 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | C2 | STATE:VERIFIED |
| B36 | `exp_substrate_wikipedia_ppmi_svd_baseline_smoke_cg_measured_bound_3seed_n500_hp1_cleared` | 2026-07-03 (_start_marker) | HARD_PASS | smoke | A | OK | HD:`char_trigram_encoder.py` | -- | STATE:VERIFIED |
| B37 | `exp_additive_map_acceptance_gate_v1` | 2026-07-14 (ts_iso) | ACCEPTANCE_PASS_ADDITIVE_MAP_REPRODUCES_VET | full | A | OK | HD:`additive_map.py` | -- | STATE:VERIFIED |
| B38 | `exp_attention_salience_reliability_gate_independent_channel_v1` | 2026-07-20 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | BOUND | STATE:VERIFIED |
| B39 | `exp_cortex_schema_exemplar_bayes_importance_sample_v1` | 2026-06-28 (ts_iso) | HARD_PASS | full | A | OK | HD:`schema_exemplar_bayes.py` | -- | STATE:VERIFIED |
| B40 | `exp_cortex_ultrametric_clustering_coarse_grain_v1` | 2026-06-26 (git-first-commit) | HARD_PASS | full | A | OK | HD:`ultrametric_clustering.py` | C1 | STATE:VERIFIED |
| B41 | `exp_generation_grounded_fact_utterance_v1` | 2026-07-05 (ts_iso) | HARD_PASS | full | ARM | OK | HD:`generation.py` | -- | STATE:VERIFIED |
| B42 | `exp_hoc1_word_bigram_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | PROSE | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B43 | `exp_integration_end_to_end_loop_bridge_v1` | 2026-07-05 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | C4,C2 | STATE:VERIFIED |
| B44 | `exp_kmax_ness_envelope_corrected_v1` | UNDATED (none) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B45 | `exp_leakproof_relinfer_context_sweep_v1` | 2026-07-26 (ts_iso) | HOLDS_AND_SCALES | full | A | OK | EXP-ONLY | C2 | STATE:VERIFIED |
| B46 | `exp_multisource_arena_temporal_accrual_fair_v1` | 2026-07-16 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B47 | `exp_q_b1_ab_iterate_3arm_v1_n16384` | 2026-06-19 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B48 | `exp_read_discourse_entitygrid_coherence_v1` | 2026-07-17 (ts_iso) | MIDDLE_BAND | full | A | OK | EXP-ONLY | C4 | STATE:REFUTED |
| B49 | `exp_read_grow_selectional_preference_precision_v2` | 2026-07-17 (ts_iso) | HARD_FAIL | full | A | OK | EXP-ONLY | -- | STATE:REFUTED |
| B50 | `exp_reasoning_depth_exact_order_statistic_self_margin_v1` | 2026-07-06 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B51 | `exp_redundant_soft_shard_router_e2e_seed_robust_boundary_v1` | 2026-07-17 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B52 | `exp_rns_subblock_margin_exact_prefactor_v2` | 2026-07-06 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B53 | `exp_substrate_abduction_f3_hmm_headroom_realgap_deployment_cpu_v1` | 2026-06-15 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B54 | `exp_substrate_anchor3_coarse_grain_phase_diagram_v2_family_overlap` | 2026-06-29 (ledger:ts) | HARD_PASS | full | ARM | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B55 | `exp_substrate_capacity_composition_b2xb4_v1_n2048` | 2026-06-04 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| B56 | `exp_substrate_composed_encoder_v3_smoke_2026_07_03` | 2026-07-03 (ts_iso) | SELFTEST_PASS | self_test | ARM | OK | HD:`composed_encoder_v3.py` | -- | STATE:VERIFIED |
| B57 | `exp_substrate_phase_diagram_subsystem_decoupling_v3` | 2026-07-17 (_start_marker) | HARD_PASS | full | A | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| B58 | `exp_substrate_sparsity_free_axis_v4b_pc_widened_alpha_grid_n4096_3seed_full_chain_grade_` | 2026-07-02 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| B59 | `exp_substrate_wikipedia_ppmi_svd_scale_up_full_n10k_preliminary_cg_honest_negative_2of3_` | 2026-07-03 (_start_marker) | MEASURED_BOUND_LOW_DELTA | full | A | OK | HD:`char_trigram_encoder.py` | C2 | state=VERIFIED DUP-OF CG-B21 |
| B60 | `exp_ternary_arm2_extended_basis_2026_06_16` | UNDATED (none) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B61 | `exp_capacity_multi_bank_alpha_k_high_v1_seed_{7,13,19}` | 2026-07-01 (ledger:ts) | HARD_PASS | full | A | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| B62 | `exp_combo1_p3_dam_implicit_gram_v3_gpu_fix_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B63 | `exp_conceptnet_rerank_parity_multiseed_v1` | 2026-07-07 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B64 | `exp_encoder_alltype_transfer_stress_v1` | 2026-08-01 (ts_iso) | HARD_PASS | lite | ARM | OK | EXP-ONLY | C4 | state=VERIFIED DUP-OF RP-C10 |
| B65 | `exp_generation_decoder_rns_crt_highvocab_v1` | 2026-07-05 (ts_iso) | HARD_PASS | full | A | OK | HD:`generation.py` | -- | state=VERIFIED DUP-OF RP-D19 |
| B66 | `exp_kb_partition_by_source_class_v4_calibrated` | 2026-06-27 (git-first-commit) | HARD_PASS | ABSENT | A | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| B67 | `exp_multisource_arena_conjunction_menu_v1` | 2026-07-16 (ts_iso) | HARD_PASS | ABSENT | ARM | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B68 | `exp_np_head_finder_grounding_gate_break050_v1` | 2026-07-19 (ts_iso) | HARD_PASS_HEADFINDER_BREAKS_050 | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B69 | `exp_pb_crt_real_encoder_atoms_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B70 | `exp_phase_diagram_capacity_multi_bank_k4_envelope_v2c_n8192_gpu` | 2026-06-27 (ledger:ts) | HARD_FAIL -- **MERGE CORRECTION 2026-08-14 (re-read on disk):** this row recorded `HARD_FAIL`. `data/exp_phase_diagram_capacity_multi_bank_K4_envelope_v2c_n8192_gpu/metrics.json` at HEAD (`39cc197ff`, git-clean) reads **`HARD_PASS`**, run_mode `full`, `rec=1.0000 cv=0.0000 n=3 per_seed=[1.0,1.0,1.0]`, and its own text says *"v2c rescue of v2b OOM"*. The HARD_FAIL belongs to the **v2b sibling**, which had no row in any ledger and is now row CG-G1. Wrongly demoted; restored. | full | A | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| B71 | `exp_reasoning_depth_capacity_provisioning_monitor_loop_v1` | 2026-07-08 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| B72 | `exp_reasoning_readout_length_generalization_clutrr_cg_v1` | 2026-07-20 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B73 | `exp_situation_model_assembly_encoder_retrain_scale_v1` | 2026-07-31 (ts_iso) | CLEAN_PASS | grid | A | OK | EXP-ONLY | -- | state=VERIFIED DUP-OF RP-C9 |
| B74 | `exp_substrate_capacity_multibank_alpha_k_phase_diagram_v2_gpu_seed_7` | 2026-06-29 (ledger:ts) | MIDDLE_BAND -- **MERGE CORRECTION 2026-08-14 (re-read on disk):** recorded `MIDDLE_BAND`. All three seed directories (`exp_substrate_capacity_multibank_alpha_K_phase_diagram_v2_GPU_seed_{7,13,19}`) read **`HARD_PASS`**, run_mode `full` (`n_pass=118/119, n_pass_at_full_N=34/35, rail_ok`). The `_smoke` siblings read `SMOKE_PASS`. Wrongly demoted; restored. | full | A | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| B75 | `exp_substrate_concept_encoder_spoke1_stress_test_cell1_apples_to_apples_label_shuffle_v1` | 2026-07-03 (ts_iso) | MIDDLE_BAND | full | A | OK | HD:`concept_encoder.py` | -- | STATE:REFUTED |
| B76 | `exp_substrate_cross_modal_binding_3rd_modality_v1_seeds_13_19_full_chain_grade_extends_s` | 2026-07-01 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B77 | `exp_substrate_schema_exemplar_bayes_capacity_stress_v4_seed_13` | 2026-06-29 (ts_iso) | CHAIN_GRADE_MULTI | full | A | OK | HD:`schema_exemplar_bayes.py` | C1 | STATE:VERIFIED |
| B78 | `exp_substrate_sparse_vs_dense_alpha_sweep_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| B79 | `exp_u1_fb15k237_ingest_eval_v1` | 2026-06-21 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | C2 | STATE:VERIFIED |
| B80 | `exp_csp_first_ship_v1` | 2026-06-19 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B81 | `exp_leakproof_relational_inference_heldout_v1` | 2026-07-26 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | C2 | state=VERIFIED DUP-OF RP-C6 |
| B82 | `exp_leakproof_relinfer_twonew_v1` | 2026-07-26 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | C2 | STATE:VERIFIED |
| B83 | `exp_partof_broad_after` | 2026-06-19 (ledger:ts) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B84 | `exp_quotative_speaker_attribution_stack_break050_v1` | 2026-07-19 (ts_iso) | HARD_PASS_QUOTATIVE_BREAKS_050 | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B85 | `exp_situation_model_assembly_binding_wm_coref_v1` | 2026-07-31 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | C4 | STATE:VERIFIED |
| B86 | `exp_substrate_compose_freq_routing_v5_definitive` | 2026-06-25 (ledger:ts) | HARD_PASS | full | A | OK | HD:`compose_freq_routing.py` | -- | STATE:VERIFIED |
| B87 | `exp_substrate_continual_learning_30day_realistic_stream_v1` | 2026-06-05 (git-first-commit) | HARD_PASS | full | A | OK | HD:`continual.py` | -- | STATE:VERIFIED |
| B88 | `exp_substrate_cross_modal_binding_visual_auditory_v1_cross_seed_agg_3_of_3_hard_pass_sta` | 2026-06-28 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B89 | `exp_substrate_lock_in_amp_phase_diagram_v2_full_3seed_chain_grade_phase_characterization` | 2026-06-29 (ledger:ts) | HARD_PASS | full | A | OK | HD:`lock_in_amp.py` | -- | STATE:VERIFIED |
| B90 | `exp_substrate_position_binding_combined_arch_trigram_v1_n4096` | 2026-06-04 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B91 | `exp_substrate_stage3_integrated_audit_device_demo_v1` | 2026-06-25 (git-first-commit) | HARD_PASS_INTEGRATED_AUDIT_DEVICE | full | ARM | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B92 | `exp_substrate_working_memory_multi_bank_k_extension_adversarial_v1` | 2026-06-26 (ledger:ts) | RAIL_SANITY_BREACH | full | A | OK | HD:`working_memory.py` **(in live closure)** | -- | state=VERIFIED DUP-OF RP-D10 |
| B93 | `exp_t5c_hybrid_3seed_kb10k_v1` | 2026-06-09 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B94 | `exp_theta_gamma_v4_extended_seeds_gpu_7seed_full_chain_grade_lift_of_v3_atom_9_mm_via_re` | 2026-07-01 (ts_iso) | MIDDLE_BAND | full | ARM | OK | EXP-ONLY | -- | STATE:REFUTED |
| B95 | `exp_a1_substrate_intent_classifier_v1_gatecheck` | 2026-06-23 (ledger:ts) | HARD_PASS | full | A | OK | HD:`intent_classifier.py` | -- | STATE:VERIFIED |
| B96 | `exp_c_infty_seb_detection_full_v3` | UNDATED (none) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B97 | `exp_combo3_unified_api_n32768_v1` | 2026-06-02 (git-first-commit) | HARD_PASS | smoke | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B98 | `exp_cskg_foundation_v1` | 2026-07-26 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B99 | `exp_csp_memory_warm_start_full_v3` | UNDATED (none) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B100 | `exp_curriculum_order_ingest_schema_fit_v1` | 2026-07-16 (ts_iso) | HARD_PASS_ORDER_MATTERS_CURRICULUM_RESCUES_SCHEMA_FIT | ABSENT | ARM | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B101 | `exp_deletion_cert_zratio_n32768_v1` | 2026-06-02 (git-first-commit) | HARD_PASS | smoke | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B102 | `exp_exp_p1_action_at_any_position_phase_diagram_v1` | 2026-06-22 (ledger:ts) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B103 | `exp_frame_order_recovery_hard_comprehension_v2` | 2026-07-06 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | -- | state=VERIFIED DUP-OF RP-C11 |
| B104 | `exp_interaction_asymmetric_directed_operators_v1` | 2026-07-15 (ts_iso) | HARD_PASS_BRAIN_ASYMMETRIC_OP_READS_DOMINANCE_TRANSITION_OP | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B105 | `exp_interaction_nonadditive_discovery_v1` | 2026-07-15 (ts_iso) | HARD_PASS_A_INTERACTION_CONSTRUCTION_PROVEN / HARD_PASS_B_SYMMETRY_MATCHED_DISCOVERY_NONADDITIVE_AND_NON | full | A | OK | EXP-ONLY | BOUND | STATE:VERIFIED |
| B106 | `exp_kappa3_sensitivity_sweep_n16384_v3_delta_alpha_protocol_v1` | 2026-06-02 (git-first-commit) | HARD_PASS | full | PROSE | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B107 | `exp_kg_store_dim_scaling_ceiling_v1` | 2026-07-13 (ts_iso) | HARD_PASS_DIMENSION_RELIEVES_CEILING | full | A | OK | EXP-ONLY | BOUND | STATE:VERIFIED |
| B108 | `exp_lln_point_mass_verification_n_v_c_f_sweep_v1` | 2026-07-01 (_start_marker) | CHAIN_GRADE_LLN_POINT_MASS_VERIFIED | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B109 | `exp_metacog_abstain_conformal_transfer_v1` | 2026-07-20 (ts_iso) | HARD_PASS_CONFORMAL_THRESHOLD_TRANSFERS_TO_DISJOINT_TEST | full | A | OK | HD:`conformal.py` | -- | STATE:VERIFIED |
| B110 | `exp_morph_ruleset_wug_v2_cpu` | 2026-07-05 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B111 | `exp_multihop_reasoning_depth_20_to_40_gpu_v1` | 2026-07-01 (git-first-commit) | DEPTH_40_STILL_ABOVE_HALF | full | A | OK | EXP-ONLY | C2 | STATE:VERIFIED |
| B112 | `exp_multihop_reasoning_depth_45_to_60_gpu_v1` | 2026-07-01 (git-first-commit) | DEPTH_60_CROSSED_HALF | full | A | OK | EXP-ONLY | C2 | STATE:VERIFIED |
| B113 | `exp_multihop_reasoning_depth_50_55_crossing_bracket_gpu_v1` | 2026-07-01 (git-first-commit) | CROSSING_BRACKET_50_55 | full | A | OK | EXP-ONLY | C2 | STATE:VERIFIED |
| B114 | `exp_ner_transition_charngram_noise_crosscut_cpu_v1` | 2026-06-12 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B115 | `exp_p1_v2_action_at_any_position_llm_class_v1` | 2026-06-22 (ledger:ts) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B116 | `exp_parietal_relational_v3` | 2026-07-01 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | C2 | STATE:VERIFIED |
| B117 | `exp_phase_diagram_wm_multibank_k_8192_3seed_harvest_v1` | 2026-06-27 (ledger:ts) | CHAIN_GRADE_K_8192_3SEED | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B118 | `exp_pp48_pp46_negative_knowledge_with_deletion_cert_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B119 | `exp_pp49_hrc_counterfactual_depth_8_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B120 | `exp_pp50_kappa3_delta_alpha_n16384_v2_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | PROSE | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B121 | `exp_pp50_kappa3_delta_alpha_n32768_v3_n32768` | 2026-06-03 (git-first-commit) | HARD_PASS | full | PROSE | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B122 | `exp_pp50_kappa3_delta_alpha_n8192_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | PROSE | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B123 | `exp_pp52_exact_rollback_n4096_v1` | 2026-06-02 (git-first-commit) | HARD_PASS | full | PROSE | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B124 | `exp_pp52_exact_rollback_n8192_v1` | 2026-06-02 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B125 | `exp_pp52_one_shot_addition_n8192_v1` | 2026-06-02 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B126 | `exp_provisional_hold_bootstrap_arbitrary_order_v1` | 2026-07-16 (ts_iso) | HARD_PASS_PROVISIONAL_HOLD_RECOVERS_ARBITRARY_ORDER | ABSENT | ARM | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B127 | `exp_refuse_gate_5_graph_health_cpu_v1` | 2026-06-20 (git-first-commit) | HARD_PASS | full | A | OK | HD:`refuse_gate.py` | -- | STATE:VERIFIED |
| B128 | `exp_substrate_arch_ablation_matrix_bigram_v1_n512_gpu` | 2026-06-04 (git-first-commit) | HARD_PASS | full | ARM | OK | HD:`ablation.py` **(in live closure)** | -- | STATE:VERIFIED |
| B129 | `exp_substrate_cfrpe_stdp_heterogeneous_superadditive_bigram_v1_n512` | 2026-06-04 (git-first-commit) | HARD_PASS | full | ARM | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B130 | `exp_substrate_cognitive_core_counterfactual_v1` | 2026-06-05 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | C2 | STATE:VERIFIED |
| B131 | `exp_substrate_narrative_partition_oracle_v_c_sweep_v1_smoke` | 2026-06-28 (ledger:ts) | HARD_FAIL | smoke | A | OK | EXP-ONLY | C4 | STATE:REFUTED |
| B132 | `exp_substrate_novel_assembly_2_tier2_novel_composition_equivalence_checked_cpu_v1` | 2026-06-15 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B133 | `exp_substrate_partition_routing_hierarchical_2level_v1` | 2026-06-25 (git-first-commit) | CHAIN_GRADE_AT_M_10M | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B134 | `exp_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_7` | 2026-06-28 (ts_iso) | HARD_FAIL -- **MERGE CORRECTION 2026-08-14 (re-read on disk):** recorded as a refutation. The artifact reads `HARD_FAIL_GPU_MANDATE_BREACH: FULL run on CPU backend forbidden by Fix #24 ... Refusing.` **The run refused to start; no measurement exists**, so it cannot refute anything. Reclassified REFUTED -> FOUND (test-design/harness abort, not a structural negative). The reading tier had it at FOUND already (row M226) -- the two ledgers disagreed and the artifact settles it. | full | PROSE | OK | EXP-ONLY | -- | STATE:FOUND |
| B135 | `exp_substrate_refuse_gate_near_domain_v2` | 2026-06-25 (git-first-commit) | HARD_PASS_BOTH_WORK | full | A | OK | HD:`refuse_gate.py` | -- | STATE:VERIFIED |
| B136 | `exp_substrate_refuse_gate_v8_conformal_v1_seed_7_smoke` | 2026-07-01 (ts_iso) | HARD_PASS | smoke | A | OK | HD:`refuse_gate.py` | -- | STATE:VERIFIED |
| B137 | `exp_substrate_refuse_gate_v_rel_extension_v1` | 2026-06-25 (git-first-commit) | HARD_PASS | full | A | OK | HD:`refuse_gate.py` | -- | STATE:VERIFIED |
| B138 | `exp_substrate_schema_family_phase_diagram_v1_full_3seed_chain_grade_phase_characterizati` | 2026-06-29 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B139 | `exp_substrate_schema_family_phase_diagram_v1_seed_13` | 2026-06-29 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B140 | `exp_substrate_schema_family_phase_diagram_v1_seed_19` | 2026-06-29 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B141 | `exp_substrate_schema_family_phase_diagram_v1_seed_7` | 2026-06-29 (ts_iso) | HARD_PASS | full | A | OK | EXP-ONLY | -- | state=VERIFIED DUP-OF CG-B138 |
| B142 | `exp_substrate_stage_a_bio_smoke_b2_sparse_fix_v2` | UNDATED (none) | HARD_FAIL -- **MERGE CORRECTION 2026-08-14 (re-read on disk):** recorded `HARD_FAIL`. `data/exp_substrate_stage_a_bio_smoke_B2_sparse_fix_v2/metrics.json` reads **`HARD_PASS`**, run_mode `full`: *"DG sparse expansion gives >=10x capacity. M_crit dense=100 sparse=4800 ratio=48.0x"*. Enumerated the whole `exp_substrate_stage_a_bio_smoke_B2_sparse_fix*` family with `os.listdir` -- **exactly one directory exists**, so this is not a sibling mix-up. Wrongly demoted; restored. NOTE it is a **DG sparse-expansion PASS** and therefore bears on sec 11 correction 2. | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B143 | `exp_substrate_theta_gamma_v2_fhrr_all_complex_seed_7` | 2026-07-01 (ts_iso) | HARD_PASS **MERGE FLAG -- DANGLING BY FILENAME:** `data/exp_substrate_theta_gamma_v2_FHRR_all_complex_seed_7/` exists but contains **no `metrics.json`** -- its artifact is named `metrics.fresh_2026-06-30.json`. Every tool in this repo that globs `metrics.json` is blind to it. Not demoted; flagged. | full | ARM | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B144 | `exp_t5c_c1_3seed_validate_gpu_v1` | 2026-06-08 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B145 | `exp_t5c_c1_5seed_validate_gpu_v1` | 2026-06-10 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B146 | `exp_t5c_d1_3seed_validate_gpu_v1` | 2026-06-08 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B147 | `exp_t5c_multi1_everylayer_3seed_v1` | 2026-06-09 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| B148 | `exp_t5c_multi2_6layer_3seed_v1` | 2026-06-09 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
#### Group CG-C -- contrast arm present, NO identifiable reference arm (70 rows)

**These are the vocabulary-drift alarm at cell level.** Each has a comparison SHAPE whose arm names this pass could not name as a reference. Some are real floors under an unrecognised name (`exp_substrate_encoder_capacity_at_scale_battery_gpu_v1`, promoted to CG-A, was one); most are config sweeps. **Not counted as floored.**

| # | cell | date (src) | verdict (as read) | run_mode | floor | disk | module | moves | STATE |
|---|---|---|---|---|---|---|---|---|---|
| C1 | `exp_substrate_minilm_encoder_fidelity_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | C3? | STATE:VERIFIED |
| C2 | `exp_intent_atis_multiseed_cpu_v1` | 2026-06-11 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | C3? | STATE:VERIFIED |
| C3 | `exp_pp55_vsa_binding_n131072_v6_n131072` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | C3? | STATE:VERIFIED |
| C4 | `exp_t5c_pp225_3seed_v1` | 2026-06-09 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C5 | `exp_a8_continual_writes_no_catastrophic_forgetting_v1` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | HD:`continual.py` | C1 | STATE:VERIFIED |
| C6 | `exp_capacity_cliff_graceful_full_v3` | 2026-06-12 (ledger:ts) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| C7 | `exp_crt_module_scaling_battery_fixed_v1` | UNDATED (none) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| C8 | `exp_crt_module_scaling_battery_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| C9 | `exp_csp_hebbian_coexist_v1` | 2026-06-01 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C10 | `exp_fp16_vs_fp32_parity_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| C11 | `exp_matrix_trace_primitives_full_v3` | UNDATED (none) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C12 | `exp_padding_side_audit_capacity_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| C13 | `exp_pb_kf1_multilang_chain_robustness_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C14 | `exp_substrate_capacity_stress_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| C15 | `exp_tier4_multiseed_sweep_cpu_v1` | 2026-06-11 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C16 | `exp_tr_w1w2_set_intersect_v1` | 2026-06-01 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | C4 | STATE:VERIFIED |
| C17 | `exp_wave1_multiseed_sweep_cpu_v1` | 2026-06-11 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C18 | `exp_deletion_cert_refusal_joint_v1` | 2026-06-01 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C19 | `exp_hnsw_ef_search_calibration_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C20 | `exp_hp12_v1_demo_scale_10k_facts_v1` | 2026-06-05 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C21 | `exp_kf1_paraphrase_robustness_marianmt_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C22 | `exp_pb_multilang_paraphrase_chain_kf1_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C23 | `exp_pp55_vsa_binding_n16384_v3_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C24 | `exp_active_inference_dpefe_h2_cpu_v1` | 2026-06-11 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | C2 | STATE:VERIFIED |
| C25 | `exp_ccc1_extra_fb15k237_kg_multihop_v1` | 2026-06-05 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | C2 | STATE:VERIFIED |
| C26 | `exp_combo2_p4_l3_signed_am_v1_n32768` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C27 | `exp_f4_kappa_n_deviation_snr_cpu_v1` | 2026-06-13 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C28 | `exp_multiagent_coord_full_v3` | UNDATED (none) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C29 | `exp_n1_concept_lm_substrate_native_token_decode_v3` | 2026-06-21 (git-first-commit) | HARD_FAIL | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:REFUTED |
| C30 | `exp_phase_diagram_multihop_depth_ceiling_sweep_20_25_30_v1` | 2026-06-26 (git-first-commit) | CHAIN_GRADE_DEPTH_CEILING_30 | full | CONTRAST-ONLY | OK | EXP-ONLY | C2 | STATE:VERIFIED |
| C31 | `exp_planted_csp_viability_full_v3` | UNDATED (none) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C32 | `exp_pos_tagger_multiseed_cpu_v1` | 2026-06-11 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | HD:`pos_tagger.py` | -- | STATE:VERIFIED |
| C33 | `exp_pp52_exact_rollback_n16384_v1` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C34 | `exp_pp52_one_shot_addition_n16384_v1` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C35 | `exp_q_b1_bisect_d275_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C36 | `exp_q_b1_bisect_d276_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C37 | `exp_q_b1_chain_depth_100_v1_n8192` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C38 | `exp_q_b1_chain_depth_150_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C39 | `exp_q_b1_chain_depth_15_v1_n8192` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C40 | `exp_q_b1_chain_depth_200_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C41 | `exp_q_b1_chain_depth_20_v1_n8192` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C42 | `exp_q_b1_chain_depth_250_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C43 | `exp_q_b1_chain_depth_25_v1_n8192` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C44 | `exp_q_b1_chain_depth_30_v1_n8192` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C45 | `exp_q_b1_chain_depth_35_v1_n8192` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C46 | `exp_q_b1_chain_depth_40_v1_n8192` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C47 | `exp_q_b1_chain_depth_45_v1_n8192` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C48 | `exp_q_b1_chain_depth_50_v1_n8192` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C49 | `exp_q_b1_chain_depth_55_v1_n8192` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C50 | `exp_q_b1_chain_depth_60_v1_n8192` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C51 | `exp_q_b1_chain_depth_70_v1_n8192` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C52 | `exp_q_b1_chain_depth_80_v1_n16384` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C53 | `exp_q_b1_chain_depth_80_v1_n8192` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C54 | `exp_q_b1_chain_depth_90_v1_n8192` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C55 | `exp_q_b1_depth_extended_n32768` | 2026-06-02 (git-first-commit) | MIDDLE_BAND | smoke | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:REFUTED |
| C56 | `exp_r_alpha_throughput_full_v3` | UNDATED (none) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C57 | `exp_substrate_cognitive_core_analogical_v1` | 2026-06-05 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C58 | `exp_substrate_cognitive_core_architectural_advantage_v1` | 2026-06-05 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C59 | `exp_substrate_continual_learning_distshift_v1` | 2026-06-05 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | HD:`continual.py` | -- | STATE:VERIFIED |
| C60 | `exp_substrate_crossdomain_transfer_conll2003_ontonotes_ner_cpu_v1` | 2026-06-12 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C61 | `exp_substrate_extended_context_ceiling_posbind_symw_v1_8192_16384_gpu` | 2026-06-04 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | C2 | STATE:VERIFIED |
| C62 | `exp_substrate_long_conversation_10k_exchanges_v1` | 2026-06-05 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C63 | `exp_substrate_long_conversation_scale_1000_exchanges_v1` | 2026-06-05 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C64 | `exp_substrate_multidoc_synthesis_1000plus_docs_v1` | 2026-06-05 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C65 | `exp_substrate_task_complexity_sweep_v1_512_8192_gpu` | 2026-06-04 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C66 | `exp_symbolic_prim_battery_v1` | 2026-06-01 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C67 | `exp_t5c_pp225_pythia14b_fp32proj_3seed_v1` | 2026-06-09 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C68 | `exp_wave1_tier1_sweep_cpu_v1` | 2026-06-11 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C69 | `exp_wave2_rescue_multiseed_sweep_cpu_v1` | 2026-06-11 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| C70 | `exp_wave4_full_streaming_battery_n8192_v1` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
#### Group CG-D -- no floor shape visible in metrics.json (23 rows)

**`NO FLOOR` = no floor visible in `metrics.json`, NOT 'no floor'.** Two confirmed detector false negatives are already promoted out of this group into CG-A (`exp_substrate_expansion_method_battery_gpu_v1`, `exp_substrate_name_augmented_encoding_recovery_canonical_rerun_v593`), so assume more remain. An unfloored pass is not evidence and none of these may be cited as one.

| # | cell | date (src) | verdict (as read) | run_mode | floor | disk | module | moves | STATE |
|---|---|---|---|---|---|---|---|---|---|
| D1 | `exp_substrate_expansion_method_battery_gpu_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | C3,C1 | STATE:VERIFIED |
| D2 | `exp_substrate_name_augmented_encoding_recovery_canonical_rerun_v593` | 2026-06-12 (ledger:ts) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | C3?,C4 | STATE:VERIFIED |
| D3 | `exp_substrate_sparsity_fine_battery_gpu_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | C3?,C1 | STATE:VERIFIED |
| D4 | `exp_modern_hopfield_n_sweep_v1` | 2026-06-07 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| D5 | `exp_cortex_hippo_dense_commercial_m_100k_1m_gpu_v5_kernel_active_fraction_3seed_full_cha` | 2026-07-01 (ts_iso) | CELL_CRASHED -- **MERGE CORRECTION 2026-08-14 (re-read on disk):** this row records the verdict `CELL_CRASHED`. All three `exp_cortex_hippo_dense_commercial_M_100k_1M_gpu_v5_kernel_active_fraction_seed_{7,13,19}` directories read **`HARD_PASS` / `CHAIN_GRADE_COMMERCIAL_SCALE`**, run_mode `full`. The crash text does not reproduce off any artifact. Verdict corrected; state unchanged. | full* | NO FLOOR | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| D6 | `exp_substrate_capacity_battery_gpu_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| D7 | `exp_substrate_capacity_scaling_sweep_xl_v1` | 2026-06-05 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | C1 | STATE:VERIFIED |
| D8 | `exp_temporal_contextual_multiseed_cpu_v1` | 2026-06-11 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | C2 | STATE:VERIFIED |
| D9 | `exp_substrate_multimodal_binding_text_kg_v1` | 2026-06-05 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| D10 | `exp_combo2_p4_l3_signed_am_v1_n32768_5seed_verification_v1` | 2026-06-02 (git-first-commit) | HARD_PASS | full | BAND-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| D11 | `exp_combo3_unified_api_v1_n16384_l4_alpha_grid_v1` | 2026-06-02 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| D12 | `exp_deletion_cert_z_ratio_n16384_full_alpha_v1` | 2026-06-02 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| D13 | `exp_deletion_cert_z_ratio_n16384_v1` | 2026-06-02 (git-first-commit) | HARD_PASS | full | BAND-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| D14 | `exp_i1_bf16_overflow_n65536_v1` | 2026-06-06 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| D15 | `exp_membership_auroc_mapping_v1` | 2026-06-07 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| D16 | `exp_pp50_kappa3_ultra_fine_sigma_g_v4_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| D17 | `exp_pp52_one_shot_addition_n4096_v1` | 2026-06-02 (git-first-commit) | HARD_PASS | full | BAND-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| D18 | `exp_sql_hd_aggregation_bound_gpu_v1` | 2026-06-07 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| D19 | `exp_substrate_b6_x_sq2_audit_preserving_reasoning_v1_n4096` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| D20 | `exp_substrate_hierarchical_5corpus_meta_v1_n2048_gpu` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| D21 | `exp_substrate_hierarchical_5corpus_meta_v2_n2048_gpu` | 2026-06-08 (ledger:ts) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| D22 | `exp_substrate_hierarchical_aggregator_scale_ext_domains5_10_20_v1_n2048` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| D23 | `exp_substrate_spectral_edge_n_extension_decisive_v1_8192_32768_gpu` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
#### Group CG-F -- rows the chain-graded sweep could not resolve to a directory (18 rows -- **14 of them DO resolve; see below**)

**MERGE CORRECTION 2026-08-14: 14 of these 18 are NOT ABSENT, they were MIS-ENUMERATED, and they are now VERIFIED.** Eleven resolve under a case-insensitive match (the earlier matcher was case-SENSITIVE: `..._k_banks_v2_gpu` on disk is `..._K_banks_v2_GPU`) and three by longest-common-token-prefix onto their per-seed artifact; every one of the 14 has had its `metrics.json` opened at HEAD and its verdict recorded in-row. **Four rows remain unresolved and stay FOUND** (F1, F4, F16, F17), two of which are write-path bugs rather than missing results -- see sec 5.7. This is sec 8 rule 3 costing 14 rows in a single group: an absence claim requires an enumeration, and a case-sensitive `startswith` is not one. The sweep's original framing follows. Nothing on disk was opened for these AT THE TIME, so **none of them was VERIFIED then**. Three sub-classes, and the first two are recoverable: (i) unexpanded shell brace patterns in the write path (`..._seed_{7,13,19}`) -- the artifact is in the per-seed dirs; (ii) atoms whose `referent_pointer.metrics_path` is prose (`"metrics.json (ssh pulled)"`, `"see per_seed_metrics_paths in atom metadata"`) -- the path was never written; (iii) genuinely absent names.

| # | cell | date (src) | verdict (as read) | run_mode | floor | disk | module | moves | STATE |
|---|---|---|---|---|---|---|---|---|---|
| F1 | `exp_chain_grade_barrier1_substrate_native_break_partition_oracle_goal_conditioning_3seed` | 2026-06-28 (ledger:ts) | CHAIN_GRADE_BARRIER_1_BROKEN_PARTITION_ORACLE_GOAL_CONDITIONING_3SEED_VERIFIED_rail_2of3_strict_cv_B_0p0 | ABSENT | UNPINNED | NO DIR | EXP-ONLY | -- | STATE:FOUND |
| F2 | `exp_kb_determinism_sweep_retry_gpu_v1` | UNDATED (none) | PASS -- **MERGE CORRECTION 2026-08-14 -- NOT ABSENT, MIS-ENUMERATED.** The chain-graded sweep reported no directory. A fresh `os.scandir('data/')` enumeration (7,898 dirs) resolves it to **`data/exp_kb_determinism_sweep_RETRY_gpu_v1/`** by case-insensitive exact match (the earlier matcher was case-SENSITIVE); its `metrics.json` opens at HEAD and reads verdict **`HARD_PASS`**, run_mode `full`. State FOUND -> VERIFIED on that read. | ABSENT | UNPINNED | NO DIR | EXP-ONLY | -- | STATE:VERIFIED |
| F3 | `exp_m1_modular_macrocolumn_w_v2` | 2026-06-23 (ledger:ts) | CHAIN_GRADE_cost_path_FULL_3seeds_710s_seeds_7_17_23_N_DIM_total_4096_squared_K_values_1_8_32_M_top_2_no -- **MERGE CORRECTION 2026-08-14 -- NOT ABSENT, MIS-ENUMERATED.** The chain-graded sweep reported no directory. A fresh `os.scandir('data/')` enumeration (7,898 dirs) resolves it to **`data/exp_m1_modular_macrocolumn_W_v2/`** by case-insensitive exact match (the earlier matcher was case-SENSITIVE); its `metrics.json` opens at HEAD and reads verdict **`HARD_PASS`**, run_mode `full`. State FOUND -> VERIFIED on that read. | ABSENT | UNPINNED | NO DIR | EXP-ONLY | -- | STATE:VERIFIED |
| F4 | `exp_narrative_q3_temporal_sequence_replay_k20_3seed_hp_cg_q15_1` | 2026-07-01 (ledger:ts) | HARD_PASS | ABSENT | UNPINNED | NO DIR | EXP-ONLY | -- | STATE:FOUND |
| F5 | `exp_population_coding_3seed_cg_lift_v1` | 2026-07-01 (ledger:ts) | CHAIN_GRADE_3seed_HP_min_gain_25pp_ge_20_threshold_cv_0p085_lt_0p10_threshold_mean_28pp_lifts_lap3_7_n10 -- **MERGE CORRECTION 2026-08-14 -- NOT ABSENT, MIS-ENUMERATED.** The chain-graded sweep reported no directory. A fresh `os.scandir('data/')` enumeration (7,898 dirs) resolves it to **`data/exp_population_coding_3seed_CG_lift_v1/`** by case-insensitive exact match (the earlier matcher was case-SENSITIVE); its `metrics.json` opens at HEAD and reads verdict **`HARD_PASS`**, run_mode `full`. State FOUND -> VERIFIED on that read. | ABSENT | UNPINNED | NO DIR | EXP-ONLY | -- | STATE:VERIFIED |
| F6 | `exp_refuse_gate_v_rel_sweep_v1` | 2026-07-01 (ledger:ts) | CHAIN_GRADE_3seed_HP_CALIBRATION_UNIFORM_45_of_45_units_NEAR_rel_sim_monotonic_in_V_REL_all_3_regimes_pe -- **MERGE CORRECTION 2026-08-14 -- NOT ABSENT, MIS-ENUMERATED.** The chain-graded sweep reported no directory. A fresh `os.scandir('data/')` enumeration (7,898 dirs) resolves it to **`data/exp_refuse_gate_V_REL_sweep_v1/`** by case-insensitive exact match (the earlier matcher was case-SENSITIVE); its `metrics.json` opens at HEAD and reads verdict **`HARD_PASS`**, run_mode `full`. State FOUND -> VERIFIED on that read. | ABSENT | UNPINNED | NO DIR | HD:`refuse_gate.py` | -- | STATE:VERIFIED |
| F7 | `exp_substrate_audit_core_c2_c3_whitened_llama1b_v1_n4096` | UNDATED (none) | PASS -- **MERGE CORRECTION 2026-08-14 -- NOT ABSENT, MIS-ENUMERATED.** The chain-graded sweep reported no directory. A fresh `os.scandir('data/')` enumeration (7,898 dirs) resolves it to **`data/exp_substrate_audit_core_C2_C3_whitened_llama1b_v1_n4096/`** by case-insensitive exact match (the earlier matcher was case-SENSITIVE); its `metrics.json` opens at HEAD and reads verdict **`HARD_PASS`**, run_mode `full`. State FOUND -> VERIFIED on that read. | ABSENT | UNPINNED | NO DIR | EXP-ONLY | C3?,C1 | STATE:VERIFIED |
| F8 | `exp_substrate_audit_core_c2_c3_whitened_pythia160m_v2_n4096` | UNDATED (none) | PASS -- **MERGE CORRECTION 2026-08-14 -- NOT ABSENT, MIS-ENUMERATED.** The chain-graded sweep reported no directory. A fresh `os.scandir('data/')` enumeration (7,898 dirs) resolves it to **`data/exp_substrate_audit_core_C2_C3_whitened_pythia160m_v2_n4096/`** by case-insensitive exact match (the earlier matcher was case-SENSITIVE); its `metrics.json` opens at HEAD and reads verdict **`HARD_PASS`**, run_mode `full`. State FOUND -> VERIFIED on that read. | ABSENT | UNPINNED | NO DIR | EXP-ONLY | C3?,C1 | STATE:VERIFIED |
| F9 | `exp_substrate_compartmentalized_cortex_k_banks_v2_gpu` | 2026-06-30 (ledger:ts) | CHAIN_GRADE_PHASE_CHARACTERIZATION_K_BANK_HOPFIELD_HIPPO_REPLAY_ROUTE_RETAINS_WRITE_PATH -- **MERGE CORRECTION 2026-08-14 -- NOT ABSENT, MIS-ENUMERATED.** The chain-graded sweep reported no directory. A fresh `os.scandir('data/')` enumeration (7,898 dirs) resolves it to **`data/exp_substrate_compartmentalized_cortex_K_banks_v2_GPU/`** by case-insensitive exact match (the earlier matcher was case-SENSITIVE); its `metrics.json` opens at HEAD and reads verdict **`HARD_PASS`**, run_mode `full`. State FOUND -> VERIFIED on that read. | ABSENT | UNPINNED | NO DIR | EXP-ONLY | -- | STATE:VERIFIED |
| F10 | `exp_substrate_compositional_generalization_k10_to_k20_v1_n4096` | UNDATED (none) | PASS -- **MERGE CORRECTION 2026-08-14 -- NOT ABSENT, MIS-ENUMERATED.** The chain-graded sweep reported no directory. A fresh `os.scandir('data/')` enumeration (7,898 dirs) resolves it to **`data/exp_substrate_compositional_generalization_K10_to_K20_v1_n4096/`** by case-insensitive exact match (the earlier matcher was case-SENSITIVE); its `metrics.json` opens at HEAD and reads verdict **`HARD_PASS`**, run_mode `full`. State FOUND -> VERIFIED on that read. | ABSENT | UNPINNED | NO DIR | EXP-ONLY | -- | STATE:VERIFIED |
| F11 | `exp_substrate_kg_capacity_sweep_m_10k_100k_1m_v1` | 2026-06-25 (ledger:ts) | MEASURED_MECHANISM_at_M_cliff_50k_skunkworks_promoted_chain_grade_at_M_10k_with_proven_cliff_at_M_50k_ti -- **MERGE CORRECTION 2026-08-14 -- NOT ABSENT, MIS-ENUMERATED.** The chain-graded sweep reported no directory. A fresh `os.scandir('data/')` enumeration (7,898 dirs) resolves it to **`data/exp_substrate_KG_capacity_sweep_M_10k_100k_1M_v1/`** by case-insensitive exact match (the earlier matcher was case-SENSITIVE); its `metrics.json` opens at HEAD and reads verdict **`MEASURED_MECHANISM`**, run_mode `full`. State FOUND -> VERIFIED on that read. | ABSENT | UNPINNED | NO DIR | EXP-ONLY | C1 | STATE:VERIFIED |
| F12 | `exp_substrate_partition_routing_10m_full_v2` | 2026-06-25 (ledger:ts) | HARD_PASS_PARTIAL_AT_M_1M_skunkworks_chain_grade_at_M_100k_with_proven_bound_at_M_1M_partition_size_2000 -- **MERGE CORRECTION 2026-08-14 -- NOT ABSENT, MIS-ENUMERATED.** The chain-graded sweep reported no directory. A fresh `os.scandir('data/')` enumeration (7,898 dirs) resolves it to **`data/exp_substrate_partition_routing_10M_full_v2/`** by case-insensitive exact match (the earlier matcher was case-SENSITIVE); its `metrics.json` opens at HEAD and reads verdict **`HARD_PASS`**, run_mode `full`. State FOUND -> VERIFIED on that read. | full* | UNPINNED | NO DIR | EXP-ONLY | -- | STATE:VERIFIED |
| F13 | `exp_substrate_sequence_binding_k_cliff_phase_diagram_full_v2_cross_seed_chain_grade_phas` | 2026-06-28 (ledger:ts) | Sequence-binding K-cliff phase diagram v2 CROSS-SEED CHAIN-GRADE phase-characterization (3 seeds 7/13/19 -- **MERGE CORRECTION 2026-08-14 -- NOT ABSENT, MIS-ENUMERATED.** The chain-graded sweep reported no directory. A fresh `os.scandir('data/')` enumeration (7,898 dirs) resolves it to **`data/exp_substrate_sequence_binding_K_cliff_phase_diagram_full_v2_seed_7/`** by longest-common-token-prefix 10/15 token match onto the per-seed artifact; its `metrics.json` opens at HEAD and reads verdict **`MIDDLE_BAND`**, run_mode `full`. State FOUND -> VERIFIED on that read. | full* | UNPINNED | NO DIR | EXP-ONLY | -- | STATE:VERIFIED |
| F14 | `exp_substrate_task_vector_hrr_icl_k_500_extended_v1_3seed_chain_grade_k_of_mechanism_dea` | 2026-07-01 (ledger:ts) | CHAIN_GRADE_3seed_HP_FULL_K_of_mechanism_death_1000_localized_perfectly_across_all_3_seeds_K50_TV_1p00_0 -- **MERGE CORRECTION 2026-08-14 -- NOT ABSENT, MIS-ENUMERATED.** The chain-graded sweep reported no directory. A fresh `os.scandir('data/')` enumeration (7,898 dirs) resolves it to **`data/exp_substrate_task_vector_HRR_ICL_K_500_extended_v1_seed_7/`** by longest-common-token-prefix 10/17 token match onto the per-seed artifact; its `metrics.json` opens at HEAD and reads verdict **`HARD_PASS`**, run_mode `full`. State FOUND -> VERIFIED on that read. | ABSENT | UNPINNED | NO DIR | EXP-ONLY | C1 | STATE:VERIFIED |
| F15 | `exp_substrate_wm_multibank_k_cliff_phase_diagram_v3_gpu_chunked_cross_seed_agg_3_of_3_ha` | 2026-06-28 (ledger:ts) | WM_K_CLIFF_V3_GPU_CROSS_SEED_3_of_3_HARD_PASS_chain_grade_phase_characterization_CERT_plus_1 -- **MERGE CORRECTION 2026-08-14 -- NOT ABSENT, MIS-ENUMERATED.** The chain-graded sweep reported no directory. A fresh `os.scandir('data/')` enumeration (7,898 dirs) resolves it to **`data/exp_substrate_wm_multibank_K_cliff_phase_diagram_v3_GPU_chunked_seed_7/`** by longest-common-token-prefix 11/18 token match onto the per-seed artifact; its `metrics.json` opens at HEAD and reads verdict **`HARD_PASS`**, run_mode `full`. State FOUND -> VERIFIED on that read. | ABSENT | UNPINNED | NO DIR | EXP-ONLY | -- | STATE:VERIFIED |
| F16 | `metrics.json (ssh pulled)` | 2026-07-01 (ledger:ts) | CHAIN_GRADE_3seed_HP_cross_modal_4_5_modality_n_disc_20_21_20_of_27_cv_0p028_disc_frac_0p7407_0p7778_0p7 | ABSENT | UNPINNED | NO DIR | EXP-ONLY | -- | STATE:FOUND |
| F17 | `see per_seed_metrics_paths in atom metadata` | 2026-06-29 (ledger:ts) | CHAIN_GRADE_PHASE_CHARACTERIZATION_3SEED_PARETO_DOMINANCE_VERIFIED | ABSENT | UNPINNED | NO DIR | EXP-ONLY | -- | STATE:FOUND |
| F18 | `substrate_c1_entmax_alpha_readout_v1` | UNDATED (none) | PASS -- **MERGE CORRECTION 2026-08-14 -- NOT ABSENT, MIS-ENUMERATED.** The chain-graded sweep reported no directory. A fresh `os.scandir('data/')` enumeration (7,898 dirs) resolves it to **`data/substrate_C1_entmax_alpha_readout_v1/`** by case-insensitive exact match (the earlier matcher was case-SENSITIVE); its `metrics.json` opens at HEAD and reads verdict **`HARD_PASS`**, run_mode `full`. State FOUND -> VERIFIED on that read. | ABSENT | UNPINNED | NO DIR | EXP-ONLY | C3?,C1 | STATE:VERIFIED |

---

#### Group CG-G -- rows ADDED by the 2026-08-14 merge (1 row)

A negative that existed on disk and in no ledger. Found while re-checking CG-B70's
verdict against its artifact: B70 recorded the HARD_FAIL of a DIFFERENT directory.

| # | cell | date (src) | verdict (as read) | run_mode | floor | disk | module | moves | STATE |
|---|---|---|---|---|---|---|---|---|---|
| G1 | `exp_phase_diagram_capacity_multi_bank_K4_envelope_v2b_gpu` | 2026-06-27 (sibling of B70) | HARD_FAIL -- **ADDED BY MERGE 2026-08-14.** `data/exp_phase_diagram_capacity_multi_bank_K4_envelope_v2b_gpu/metrics.json` reads `HARD_FAIL`, run_mode `full`. Its successor `v2c` describes itself as the *"v2c rescue of v2b OOM"* and HARD_PASSes. **This is the row CG-B70's HARD_FAIL actually belonged to.** Kept as a REFUTED row because a negative that stops work is an asset -- and because losing it is how the same OOM gets re-run. | full | UNPINNED | OK | EXP-ONLY | C1 | STATE:REFUTED |

### 5.5 GROUPS R AND M -- the reading tier and the brain-mechanism tier (from S6)

403 rows. Group R is the `proven-bound` reading/grounding tier dated >= 2026-07-15 (171 rows);
group M is the brain-mechanism families (232 rows, of which 144 are FULL runs and 120 of those are
invisible to every planning document). Three standing caveats from the source sweep, all binding:

- **382 of the 403 carry MACHINE-READ evidence only.** Only 21 cells were additionally hand-read
  for their arm values -- those are the ones quoted in secs 9d-9f. The rest have unquoted margins.
- **Supersession is UNCHECKED on all 403.** No row here may be read as surviving unchallenged.
- **`OFF-PATH` in the `live` column is a NAME join against sec 4's closure, not a fresh import
  trace.** It means "not matched to a module in that closure", never "does not exist" and never
  "cannot be reached".

#### Group R -- the `proven-bound` reading and grounding tier (171 rows) [was S6 sec 9]

Sorted by the sec-4 score, descending. `geometry` is the sign call; `moves` is the scoreboard
number the cell could bear on (`C1` 2AFC 0.698, `C2` context gap +0.1005, **`C3` read-out quality
4.80% vs 0.80% -- THE GATE**, `C4` coref 0.7193).

| # | cell | evidence (metrics.json) | verdict (as read) | run mode | date (src) | floor BY SHAPE | disk | module | live | geometry | moves | doc visibility | supersede | STATE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R1 | `exp_coref_margin_gated_cleanup_local_window_break050_v1` | data/exp_coref_margin_gated_cleanup_local_window_break050_v1/metrics.json | A:HARD_FAIL_A_NET_BREAKAGE / B:HARD_PASS_B_CARRY_SEES_COREF_CONTINUITY | full | 2026-07-19 (metrics.ts_iso) | A (COS_FLOOR) | OK | EXP-ONLY | OFF-PATH | EXPANSIVE+CONTRACTIVE | C3/C4/reading | STRATEGY,STATUS,REGISTRY | UNCHECKED | STATE:REFUTED |
| R2 | `exp_role_filler_factorization_reader_coupled_cg_v1` | data/exp_role_filler_factorization_reader_coupled_cg_v1/metrics.json | HARD_PASS_READING_AXIS_FIRST_CG | full | 2026-07-19 (metrics.ts_iso) | A (chance) | OK | EXP-ONLY | OFF-PATH | FACTORIAL | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R3 | `exp_reader_image_word_grounding_v1` | data/exp_reader_image_word_grounding_v1/metrics.json | PASS_GROUNDING | full | 2026-07-22 (metrics.ts_iso) | A (<ARM CONTAINER arm_digests>) | OK | EXP-ONLY | OFF-PATH | -- | C3/reading | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF RP-D12c |
| R4 | `exp_hd_fact_store_semantic_capacity_whitening_v1` | data/exp_hd_fact_store_semantic_capacity_whitening_v1/metrics.json | MEASURED | ABSENT | 2026-07-24 (metrics.ts_iso) | A (<ARM CONTAINER arm_hashes_head>) | OK | HDLAB:hd_fact_store.py | LIVE | EXPANSIVE | C1/C3 | REGISTRY | UNCHECKED | state=VERIFIED DUP-OF RP-C14 |
| R5 | `exp_grounding_tem_factorized_heldout_concept_v1` | data/exp_grounding_tem_factorized_heldout_concept_v1/metrics.json | MIDDLE_BAND_FACTORIZATION_BEATS_FLAT_STRUCTURE_TRAINING_NOT_THE_LEVER | full | 2026-07-26 (metrics.ts_iso) | A (base_rate_floor,beats_flat_pooled,beats_flat_s) | OK | EXP-ONLY | OFF-PATH | FACTORIAL | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R6 | `exp_agreement_attractor_role_binding_cg_viability_v1` | data/exp_agreement_attractor_role_binding_cg_viability_v1/metrics.json | MIDDLE_BAND_POSITIONAL_OR_COUNT_HEURISTIC | full | 2026-07-22 (metrics.ts_iso) | A (BIN4_ABOVE_CHANCE_MIN) | OK | HDLAB:binding.py | LIVE | CONTRACTIVE+FACTORIAL | C1/reading | REGISTRY | UNCHECKED | STATE:VERIFIED |
| R7 | `exp_single_edge_grounding_hd_binding_verbnet_v1` | data/exp_single_edge_grounding_hd_binding_verbnet_v1_smoke/metrics.json | HARD_PASS_SINGLE_EDGE_GROUNDING | smoke | 2026-07-20 (metrics.ts_iso) | A (<ARM CONTAINER by_arm>) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1/C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R8 | `exp_role_filler_factorization_assembled_reading_axis_v1` | data/exp_role_filler_factorization_assembled_reading_axis_v1/metrics.json | FEASIBILITY_BLOCKED_GOLD_TOO_SPARSE | full | 2026-07-19 (metrics.ts_iso) | A (exploratory_gap_factored_minus_flat,explorator) | OK | EXP-ONLY | OFF-PATH | FACTORIAL | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R9 | `exp_role_filler_factorization_compgen_v1` | data/exp_role_filler_factorization_compgen_v1/metrics.json | HARD_PASS | full | 2026-07-19 (metrics.ts_iso) | A (chance) | OK | EXP-ONLY | OFF-PATH | FACTORIAL | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R10 | `exp_role_filler_factorization_conceptnet_cg_v1` | data/exp_role_filler_factorization_conceptnet_cg_v1/metrics.json | HARD_PASS_READING_AXIS_FIRST_CG | full | 2026-07-19 (metrics.ts_iso) | A (chance) | OK | EXP-ONLY | OFF-PATH | FACTORIAL | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R11 | `exp_resonator_decision_compgen_2factor_v1` | data/exp_resonator_decision_compgen_2factor_v1/metrics.json | HARD_PASS | full | 2026-07-21 (metrics.ts_iso) | A (chance) | OK | EXP-ONLY | OFF-PATH | FACTORIAL | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R12 | `exp_grounding_attn_bind_incremental_curve_v1` | data/exp_grounding_attn_bind_incremental_curve_v1/metrics.json | HARD_PASS_IMPROVING_EXPOSURE_CURVE | full | 2026-07-23 (metrics.ts_iso) | A (flat_color_of_shape,flat_illusory_2afc,label_s) | OK | EXP-ONLY | OFF-PATH | -- | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R13 | `exp_grounded_inductive_concept_encoder_heldout_new_v3` | data/exp_grounded_inductive_concept_encoder_heldout_new_v3/metrics.json | HARD_PASS | full | 2026-07-26 (metrics.ts_iso) | A (base_dim,base_epochs) | OK | HDLAB:concept_encoder.py | OFF-PATH | -- | C3 | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF RP-C8 |
| R14 | `exp_consolidated_reader_chaingrade_demo_v1` | data/exp_consolidated_reader_chaingrade_demo_v1/metrics.json | CHAIN_GRADE_DEMONSTRATED | full | 2026-07-23 (metrics.ts_iso) | A (<ARM CONTAINER arm_a_reader>) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | reading | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF RP-C2 |
| R15 | `exp_consolidated_reader_hardsyntax_heldout_v1` | data/exp_consolidated_reader_hardsyntax_heldout_v1/metrics.json | CHAIN_GRADE_HARDSYNTAX_EARNED | full | 2026-07-23 (metrics.ts_iso) | A (n_naive_correct,naive_acc) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | reading | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF RP-C4 |
| R16 | `exp_wordnet_noun_semantics_kb_who_affected_breadth_v2` | data/exp_wordnet_noun_semantics_kb_who_affected_breadth_v2/metrics.json | MM_NARROW_ENTITY_KB | full | 2026-07-21 (metrics.ts_iso) | A (<ARM CONTAINER arm_decision_digests>) | OK | HDLAB:semantic.py | LIVE | -- | C3/reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R17 | `exp_reader_perception_meaning_grounding_v1` | data/exp_reader_perception_meaning_grounding_v1/metrics.json | AWARE_USES_CONTENT_BUT_NO_GROUNDING_LIFT | full | 2026-07-22 (metrics.ts_iso) | A (<ARM CONTAINER arm_digests>) | OK | EXP-ONLY | OFF-PATH | -- | C3/reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R18 | `exp_reader_perception_meaning_grounding_sharded_v1` | data/exp_reader_perception_meaning_grounding_sharded_v1/metrics.json | SHARDED_RECOVERS_GROUNDING_LIFT_STRONG | full | 2026-07-22 (metrics.ts_iso) | A (<ARM CONTAINER arm_digests>) | OK | EXP-ONLY | OFF-PATH | -- | C3/reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R19 | `exp_reader_perception_meaning_grounding_soft_shard_v1` | data/exp_reader_perception_meaning_grounding_soft_shard_v1/metrics.json | SOFT_SHARD_RECOVERS_GROUNDING_LIFT_STRONG | full | 2026-07-22 (metrics.ts_iso) | A (<ARM CONTAINER arm_digests>) | OK | EXP-ONLY | OFF-PATH | -- | C3/reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R20 | `exp_grounding_multihop_generative_replay_traversal_v1` | data/exp_grounding_multihop_generative_replay_traversal_v1/metrics.json | MIDDLE_BAND_CG_TRAVERSAL_PARTIAL | full | 2026-07-22 (metrics.ts_iso) | A (memoryless_reach2,scrambled_reach2) | OK | HDLAB:kg_traversal.py | OFF-PATH | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R21 | `exp_agreement_learned_depth_accumulator_v1` | data/exp_agreement_learned_depth_accumulator_v1/metrics.json | HARD_PASS_LEARNED_DEPTH_GENERALIZES | full | 2026-07-22 (metrics.ts_iso) | A (<ARM CONTAINER arms>) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R22 | `exp_agreement_depth_productivity_generalization_v1` | data/exp_agreement_depth_productivity_generalization_v1/metrics.json | HARD_PASS_DEPTH_PRODUCTIVE | full | 2026-07-23 (metrics.ts_iso) | A (<ARM CONTAINER arms>) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R23 | `exp_race_meaning_reader_vs_lexical_v2` | data/exp_race_meaning_reader_vs_lexical_v2/metrics.json | PARTIAL_MEANING_LIFT | full | 2026-07-24 (metrics.ts_iso) | A (chance_theoretical,control_majority,control_ra) | OK | EXP-ONLY | OFF-PATH | -- | C3/reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R24 | `exp_wordnet_noun_semantics_kb_who_affected_v1` | data/exp_wordnet_noun_semantics_kb_who_affected_v1/metrics.json | HARD_PASS_ENTITY_KB | full | 2026-07-21 (metrics.ts_iso) | A (<ARM CONTAINER arm_decision_digests>) | OK | HDLAB:semantic.py | LIVE | -- | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R25 | `exp_dependency_context_codebook_weight_sweep_location_artifact_v2` | (none) | (no verdict key) | ABSENT | 2026-07-20 (ledger) | UNPINNED | NO DIR | EXP-ONLY | OFF-PATH | EXPANSIVE | C2/C3 | INVISIBLE | UNCHECKED | STATE:FOUND |
| R26 | `exp_reader_meaning_correction_case_sleep_affectedness_v1` | data/exp_reader_meaning_correction_case_sleep_affectedness_v1/metrics.json | MEMORIZATION_OR_NO_TRANSFER | full | 2026-07-21 (metrics.ts_iso) | A (MUSTFAIL_a_scramble_fix_rate,MUSTFAIL_a_scramb) | OK | EXP-ONLY | OFF-PATH | -- | C3/reading | REGISTRY | UNCHECKED | STATE:VERIFIED |
| R27 | `exp_read_discourse_state_of_mind_wsm_coupling_realcorpus_v2` | data/exp_read_discourse_state_of_mind_wsm_coupling_realcorpus_v2/metrics.json | HARD_PASS | full | 2026-07-17 (metrics.ts_iso) | A (metric_control_acc_with,metric_control_acc_wit) | OK | HDLAB:state_of_mind.py | LIVE | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R28 | `exp_read_grow_adaptor_pyp_kn_breadth_v1` | data/exp_read_grow_adaptor_pyp_kn_breadth_v1/metrics.json | HARD_PASS | full | 2026-07-20 (metrics.ts_iso) | A (<ARM CONTAINER arm_a>) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R29 | `exp_learned_role_assigner_reader_composition_v3` | data/exp_learned_role_assigner_reader_composition_v3/metrics.json | HARD_PASS | full | 2026-07-18 (metrics.ts_iso) | A (<ARM CONTAINER arms>) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R30 | `exp_learned_argstruct_parser_lccp_independent_gold_v1` | data/exp_learned_argstruct_parser_lccp_independent_gold_v1/metrics.json | HARD_PASS_LCCP_REDUCES_MISATTACH_AND_GENERALIZES | full | 2026-07-19 (metrics.ts_iso) | A (<ARM CONTAINER arm_metrics>) | OK | HDLAB:arc_parser.py | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R31 | `exp_mcguffey_whoaffected_wsd_frame_selectional_v1` | data/exp_mcguffey_whoaffected_wsd_frame_selectional_v1/metrics.json | HARD_PASS_WSD | full | 2026-07-21 (metrics.ts_iso) | A (<ARM CONTAINER arm_digests>) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R32 | `exp_breadth_foundation_curriculum_order_mcguffey_v1` | data/exp_breadth_foundation_curriculum_order_mcguffey_v1/metrics.json | HARD_PASS | full | 2026-07-21 (metrics.ts_iso) | A (n_order_shuffles) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R33 | `exp_agreement_glassbox_depth_rule_confirm_v1` | data/exp_agreement_glassbox_depth_rule_confirm_v1/metrics.json | HARD_PASS_DEPTH_RULE_CONFIRMED | full | 2026-07-22 (metrics.ts_iso) | A (scramble_drop,scrambled_acc_mean) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R34 | `exp_pivot_selectional_knowledge_richness_2afc_v1` | data/exp_pivot_selectional_knowledge_richness_2afc_v1/metrics.json | HARD_PASS_KNOWLEDGE_POVERTY_WAS_THE_WALL | full | 2026-07-23 (metrics.ts_iso) | A (acc_random,acc_rich_scrambled) | OK | EXP-ONLY | OFF-PATH | -- | C1/reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R35 | `exp_pivot_pp_attachment_rich_knowledge_v1` | data/exp_pivot_pp_attachment_rich_knowledge_v1/metrics.json | HARD_PASS_PP_ATTACH_IS_ALSO_KNOWLEDGE_LIMITED | full | 2026-07-23 (metrics.ts_iso) | A (acc_random,acc_rich_scrambled) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R36 | `exp_online_knowledge_condenser_selectional_v1` | data/exp_online_knowledge_condenser_selectional_v1/metrics.json | HARD_PASS_CONDENSATION_GENERALIZES | full | 2026-07-23 (metrics.ts_iso) | A (acc_random,acc_shuffle_mean,shuffle_delta) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R37 | `exp_pivot_scaled_seed_knowledge_table_v1` | data/exp_pivot_scaled_seed_knowledge_table_v1/metrics.json | HARD_PASS_SCALED_KNOWLEDGE_HELPS_AT_COVERAGE | full | 2026-07-23 (metrics.ts_iso) | A (acc_random,acc_scaled_scrambled) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R38 | `exp_reader_structural_precision_gate_v1` | data/exp_reader_structural_precision_gate_v1/metrics.json | HARD_PASS | full | 2026-07-23 (metrics.ts_iso) | A (<ARM CONTAINER arms>) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R39 | `exp_multipred_argstruct_relgap_v5` | data/exp_multipred_argstruct_relgap_v5/metrics.json | HARD_PASS_RELGAP_LIFTS_PAST_V4 | full | 2026-07-23 (metrics.ts_iso) | A (n_single_sent_recoverable) | OK | HDLAB:multi_hop.py | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R40 | `exp_multipred_argstruct_enumext_posslot_v5` | data/exp_multipred_argstruct_enumext_posslot_v5/metrics.json | HARD_PASS_SLOT_RECOVERY | full | 2026-07-23 (metrics.ts_iso) | A (<ARM CONTAINER arms>) | OK | HDLAB:multi_hop.py | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R41 | `exp_read_temporal_multiframe_chronology_v1` | data/exp_read_temporal_multiframe_chronology_v1/metrics.json | HARD_PASS | full | 2026-07-24 (metrics.ts_iso) | A (<ARM CONTAINER arms>) | OK | HDLAB:multi_hop.py | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R42 | `exp_read_xsent_coref_scene_protagonist_v1` | data/exp_read_xsent_coref_scene_protagonist_v1/metrics.json | HARD_PASS | full | 2026-07-24 (metrics.ts_iso) | A (no_overall_regress_eps) | OK | EXP-ONLY | OFF-PATH | -- | C4/reading | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF RP-C5 |
| R43 | `exp_read_events_supply_grammar_spacy_pos_litbank_v1` | data/exp_read_events_supply_grammar_spacy_pos_litbank_v1/metrics.json | HARD_PASS | full | 2026-07-24 (metrics.ts_iso) | A (positive_control_tol) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R44 | `exp_arc_retrieval_selection_gate_learned_credit_v1` | data/exp_arc_retrieval_selection_gate_learned_credit_v1/metrics.json | LEARNED_GATE_MIDDLE_BAND | full | 2026-07-25 (metrics.ts_iso) | A (baseline_beta,chance_theoretical,d_cosonly_min) | OK | EXP-ONLY | OFF-PATH | -- | C3 | REGISTRY | UNCHECKED | STATE:VERIFIED |
| R45 | `exp_grounding_cg_compound_divergence_flat_vs_traversal_v1` | data/exp_grounding_cg_compound_divergence_flat_vs_traversal_v1/metrics.json | MIDDLE_BAND_FLAT_BASELINE_VACUOUS | full | 2026-07-22 (metrics.ts_iso) | A (flat_drop,flat_hi,flat_lo) | OK | HDLAB:kg_traversal.py | OFF-PATH | -- | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R46 | `exp_agreement_attractor_select_vsa_v1` | data/exp_agreement_attractor_select_vsa_v1/metrics.json | HARD_FAIL | full | 2026-07-22 (metrics.ts_iso) | A (attractor_snf_shuffle,oracle_morph_snf,shuffle) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | reading | INVISIBLE | UNCHECKED | STATE:REFUTED |
| R47 | `exp_grounding_attn_bind_illusory_conjunction_v1` | data/exp_grounding_attn_bind_illusory_conjunction_v1/metrics.json | MIDDLE_BAND | full | 2026-07-23 (metrics.ts_iso) | A (flat_color_of_shape,flat_illusory_2afc,label_s) | OK | EXP-ONLY | OFF-PATH | -- | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R48 | `exp_scale_meaning_learn_arc_heldout_v1` | data/exp_scale_meaning_learn_arc_heldout_v1/metrics.json | MIDDLE_BAND_TIE_NULL | full | 2026-07-27 (metrics.ts_iso) | A (learning_text_minus_random,relational_populari) | OK | EXP-ONLY | OFF-PATH | -- | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R49 | `exp_read_discourse_state_hd_vs_symbolic_membership_overload_v1` | data/exp_read_discourse_state_hd_vs_symbolic_membership_overload_v1/metrics.json | HARD_FAIL | full | 2026-07-17 (metrics.ts_iso) | A (ba_random,ba_recency_oracle) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:REFUTED |
| R50 | `exp_read_discourse_state_hd_vs_symbolic_coherence_scalar_score_v1` | data/exp_read_discourse_state_hd_vs_symbolic_coherence_scalar_score_v1/metrics.json | HARD_FAIL | full | 2026-07-17 (metrics.ts_iso) | A (n_off) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:REFUTED |
| R51 | `exp_agreement_sigmap_depth_induction_v1` | data/exp_agreement_sigmap_depth_induction_v1/metrics.json | HARD_FAIL_SIGNATURE_INSUFFICIENT_FOR_DEPTH_INDUCTION | full | 2026-07-23 (metrics.ts_iso) | A (<ARM CONTAINER arms>) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:REFUTED |
| R52 | `exp_agreement_mccoy_ambiguous_hier_vs_linear_v1` | data/exp_agreement_mccoy_ambiguous_hier_vs_linear_v1/metrics.json | HARD_FAIL_ACCUM_ALSO_LINEAR | full | 2026-07-23 (metrics.ts_iso) | A (<ARM CONTAINER arms>) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:REFUTED |
| R53 | `exp_base_reader_grounded_relations_coref_v1` | data/exp_base_reader_grounded_relations_coref_v1/metrics.json | HARD_PASS | full | 2026-07-18 (metrics.ts_iso) | A (<ARM CONTAINER arms>) | OK | EXP-ONLY | OFF-PATH | -- | C4/reading | REGISTRY | UNCHECKED | STATE:VERIFIED |
| R54 | `exp_parity_in_context_binding_v1` | data/exp_parity_in_context_binding_v1/metrics.json | HARD_PASS_STRUCTURE_DISCRIMINATES | ABSENT | 2026-07-19 (metrics.ts_iso) | A (recovery_floor,structure_hard_pass_floor,void_) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1/C2 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R55 | `exp_read_xsent_coref_distractor_suppress_v1` | data/exp_read_xsent_coref_distractor_suppress_v1/metrics.json | HARD_PASS | full | 2026-07-24 (metrics.ts_iso) | A (base_acc_xsent) | OK | HDLAB:coref_distractor_suppress.py | OFF-PATH | -- | C4/reading | REGISTRY | UNCHECKED | STATE:VERIFIED |
| R56 | `exp_ud_ewt_semantic_affectedness_independent_scoreboard_v1` | data/exp_ud_ewt_semantic_affectedness_independent_scoreboard_v1/metrics.json | GATE_GENERALIZES_INDEPENDENT | full | 2026-07-21 (metrics.ts_iso) | A (<ARM CONTAINER arm_digests>) | OK | HDLAB:semantic.py | LIVE | -- | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R57 | `exp_vision_integrated_recognize_bind_ground_v1` | data/exp_vision_integrated_recognize_bind_ground_v1/metrics.json | HARD_PASS_INTEGRATED_PIPELINE__NOVEL_CLASS_WALL_CONFIRMED | full | 2026-07-23 (metrics.ts_iso) | A (flat_ill,ground_raw) | OK | EXP-ONLY | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF RP-D12b |
| R58 | `exp_arc_retrieval_multicue_ppr_discriminative_v1` | data/exp_arc_retrieval_multicue_ppr_discriminative_v1/metrics.json | RETRIEVAL_MIDDLE_BAND | full | 2026-07-24 (metrics.ts_iso) | A (chance_theoretical,recall_D_minus_A,recall_lif) | OK | HDLAB:multi_hop.py | OFF-PATH | -- | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R59 | `exp_arc_retrieval_seed_upgrade_ppr_v2` | data/exp_arc_retrieval_seed_upgrade_ppr_v2/metrics.json | SEED_UPGRADE_MIDDLE_BAND | full | 2026-07-24 (metrics.ts_iso) | A (chance_theoretical,mean_seeds_baseline,recall_) | OK | EXP-ONLY | OFF-PATH | -- | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R60 | `exp_arc_retrieval_selection_gate_suppression_v1` | data/exp_arc_retrieval_selection_gate_suppression_v1/metrics.json | GATE_MIDDLE_BAND | full | 2026-07-25 (metrics.ts_iso) | A (chance_theoretical,lure_lift_B_minus_A,nonlure) | OK | EXP-ONLY | OFF-PATH | -- | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R61 | `exp_arc_retrieval_max_recall_ksweep_reretrieval_v1` | data/exp_arc_retrieval_max_recall_ksweep_reretrieval_v1/metrics.json | RECALL_MIDDLE_BAND | full | 2026-07-25 (metrics.ts_iso) | A (baseline_recall_at10_SC,chance_theoretical,e2e) | OK | EXP-ONLY | OFF-PATH | -- | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R62 | `exp_learned_meaning_frontend_differentiation_v1` | data/exp_learned_meaning_frontend_differentiation_v1/metrics.json | MIDDLE | full | 2026-07-25 (metrics.ts_iso) | A (chance_fine,coarse_before_fine_domains,frozen_) | OK | EXP-ONLY | OFF-PATH | -- | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R63 | `exp_learned_meaning_frontend_realslice_v1` | data/exp_learned_meaning_frontend_realslice_v1/metrics.json | MIDDLE | full | 2026-07-25 (metrics.ts_iso) | A (chance_fine,converged_shuffled_fine_invocab,fr) | OK | EXP-ONLY | OFF-PATH | -- | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R64 | `exp_read_discourse_wsm_v2_hierarchical_gated_queryable_v1` | data/exp_read_discourse_wsm_v2_hierarchical_gated_queryable_v1/metrics.json | HARD_FAIL | full | 2026-07-17 (metrics.ts_iso) | A (acc_adjacent_swap_A,acc_adjacent_swap_random,a) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:REFUTED |
| R65 | `exp_read_grow_textbook_multihop_compose_v1` | data/exp_read_grow_textbook_multihop_compose_v1/metrics.json | HARD_FAIL_NOISE | full | 2026-07-18 (metrics.ts_iso) | A (base_rate,compose_precision_raw,compose_precis) | OK | HDLAB:multi_hop.py | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:REFUTED |
| R66 | `exp_read_grow_schema_hierarchy_vs_frequency_v1` | data/exp_read_grow_schema_hierarchy_vs_frequency_v1/metrics.json | HARD_FAIL_STRUCTURE_NO_SELECTION_HEADROOM | full | 2026-07-18 (metrics.ts_iso) | A (subset_isa_minus_freq_mean) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:REFUTED |
| R67 | `exp_read_grow_reread_compounding_kgguided_v1` | data/exp_read_grow_reread_compounding_kgguided_v1/metrics.json | HARD_FAIL_FLAT | full | 2026-07-18 (metrics.ts_iso) | A (freq_baseline_cc_lenient,freq_baseline_cc_stri) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:REFUTED |
| R68 | `exp_oracle_mention_upperbound_reader_v1` | data/exp_oracle_mention_upperbound_reader_v1/metrics.json | STARVATION_REFUTED | full | 2026-07-18 (metrics.ts_iso) | A (<ARM CONTAINER arms>) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:REFUTED |
| R69 | `exp_compress_and_carry_comprehension_loop_ccl_v1` | data/exp_compress_and_carry_comprehension_loop_ccl_v1/metrics.json | HARD_FAIL_CCL | full | 2026-07-19 (metrics.ts_iso) | A (<ARM CONTAINER arm_metrics>) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:REFUTED |
| R70 | `exp_compgen_binding_vs_flat_learned_frontend_v1` | data/exp_compgen_binding_vs_flat_learned_frontend_v1/metrics.json | HARD_PASS | JUNK(exp_compgen_binding_vs) | 2026-07-20 (metrics.ts_iso) | A (<ARM CONTAINER arm_by_size>) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1 | REGISTRY | UNCHECKED | STATE:VERIFIED |
| R71 | `exp_patient_specific_classifier_reader_filter_v1` | data/exp_patient_specific_classifier_reader_filter_v1/metrics.json | HARD_FAIL_CLF_HURTS | full | 2026-07-21 (metrics.ts_iso) | A (max_single_feature_gold_selection_acc) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:REFUTED |
| R72 | `exp_read_discourse_docorder_stateofmind_whoaffected_ud_ewt_v1` | data/exp_read_discourse_docorder_stateofmind_whoaffected_ud_ewt_v1/metrics.json | HARD_FAIL_SELFCONTAINED / COHERENCE_NULL | full | 2026-07-21 (metrics.ts_iso) | A (n_fixed_by_switch) | OK | HDLAB:state_of_mind.py | LIVE | -- | reading | INVISIBLE | UNCHECKED | STATE:REFUTED |
| R73 | `exp_entity_typing_selectional_wsd_v1` | data/exp_entity_typing_selectional_wsd_v1/metrics.json | HARD_FAIL | full | 2026-07-22 (metrics.ts_iso) | A (<ARM CONTAINER arm_digests>) | OK | EXP-ONLY | OFF-PATH | -- | C4/reading | INVISIBLE | UNCHECKED | STATE:REFUTED |
| R74 | `exp_agreement_glassbox_abl_adios_structure_induction_b2_v1` | data/exp_agreement_glassbox_abl_adios_structure_induction_b2_v1/metrics.json | HARD_FAIL_GLASSBOX_INDUCTION_CORROBORATES_CLOSURE | full | 2026-07-22 (metrics.ts_iso) | A (HP_MARGIN_OVER_BASE,HP_SNF_FLOOR) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:REFUTED |
| R75 | `exp_agreement_tem_on_vsa_trained_codes_v1` | data/exp_agreement_tem_on_vsa_trained_codes_v1/metrics.json | HARD_FAIL | full | 2026-07-22 (metrics.ts_iso) | A (fixed_random_snf,flat_snf,oracle_morph_snf) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:REFUTED |
| R76 | `exp_multipred_subcat_argstruct_recall_v1` | data/exp_multipred_subcat_argstruct_recall_v1/metrics.json | HARD_FAIL_MULTIPRED_NEEDS_REAL_PARSE | full | 2026-07-23 (metrics.ts_iso) | A (scrambled_table_size) | OK | HDLAB:multi_hop.py | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:REFUTED |
| R77 | `exp_condenser_as_auditor_selectional_v1` | data/exp_condenser_as_auditor_selectional_v1/metrics.json | HARD_FAIL_CONDENSER_AUDITOR_USELESS | full | 2026-07-23 (metrics.ts_iso) | A (base_rate_injected_fraction,catch_rate_scrambl) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:REFUTED |
| R78 | `exp_multipred_argstruct_kboov_backoff_v1` | data/exp_multipred_argstruct_kboov_backoff_v1/metrics.json | HARD_FAIL_COVERAGE_ARTIFACT_CONFIRMED_EVEN_WITH_BACKOFF | full | 2026-07-23 (metrics.ts_iso) | A (<ARM CONTAINER arms>) | OK | HDLAB:multi_hop.py | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:REFUTED |
| R79 | `exp_multipred_argstruct_denseitem_v1` | data/exp_multipred_argstruct_denseitem_v1/metrics.json | HARD_FAIL_DENSE_COVERAGE_DOES_NOT_HELP | full | 2026-07-23 (metrics.ts_iso) | A (flip_fraction_dense,n_flipped_dense_scheme,n_t) | OK | HDLAB:per_item_log.py | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:REFUTED |
| R80 | `exp_multipred_argstruct_measuredreliability_joint_v1` | data/exp_multipred_argstruct_measuredreliability_joint_v1/metrics.json | HARD_FAIL_KNOWLEDGE_STILL_REDUNDANT_ON_STRONG_BASE | full | 2026-07-23 (metrics.ts_iso) | A (base_gap_vs_v3_integrated,n_diff_arcscramble,n) | OK | HDLAB:multi_hop.py | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:REFUTED |
| R81 | `exp_arc_selection_relational_meaning_v1` | data/exp_arc_selection_relational_meaning_v1/metrics.json | RELATIONAL_SELECTION_HARD_FAIL | full | 2026-07-25 (metrics.ts_iso) | A (A_baseline_test_challenge,SCRAMBLE_insample_pr) | OK | EXP-ONLY | OFF-PATH | -- | C2/C3 | REGISTRY | UNCHECKED | STATE:REFUTED |
| R82 | `exp_semantic_hd_encoder_meaning_match_v1` | data/exp_semantic_hd_encoder_meaning_match_v1/metrics.json | MEANING_MATCH_PASS | ABSENT | 2026-07-24 (metrics.ts_iso) | A (chance,char_trigram_baseline_easy,control_rand) | OK | HDLAB:semantic.py | LIVE | -- | C3 | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF RP-A7 |
| R83 | `exp_read_discourse_coupling_revival_ic_verb_recency_v1` | data/exp_read_discourse_coupling_revival_ic_verb_recency_v1/metrics.json | MIDDLE_BAND | full | 2026-07-17 (metrics.ts_iso) | A (floor) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R84 | `exp_read_grow_textbook_multihop_genus_head_v2` | data/exp_read_grow_textbook_multihop_genus_head_v2/metrics.json | MIDDLE_BAND_CEILING | full | 2026-07-18 (metrics.ts_iso) | A (base_rate) | OK | HDLAB:multi_hop.py | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R85 | `exp_read_grow_textbook_multihop_genus_head_v4` | data/exp_read_grow_textbook_multihop_genus_head_v4/metrics.json | MIDDLE_BAND_CEILING | full | 2026-07-18 (metrics.ts_iso) | A (base_rate) | OK | HDLAB:multi_hop.py | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R86 | `exp_read_grow_knowledge_guided_bootstrap_v1` | data/exp_read_grow_knowledge_guided_bootstrap_v1/metrics.json | MIDDLE_BAND_BEATS_WALL_NO_COMPOUND | full | 2026-07-18 (metrics.ts_iso) | A (fail_no_lift_eps) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R87 | `exp_learned_role_assigner_reader_heldout_v2` | data/exp_learned_role_assigner_reader_heldout_v2/metrics.json | MIDDLE_BAND | full | 2026-07-18 (metrics.ts_iso) | A (<ARM CONTAINER arms>) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R88 | `exp_reader_oracle_parser_upperbound_v1` | data/exp_reader_oracle_parser_upperbound_v1/metrics.json | PARTIAL | full | 2026-07-18 (metrics.ts_iso) | A (<ARM CONTAINER arms>) | OK | HDLAB:arc_parser.py | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R89 | `exp_reader_clauseseg_topical_animate_subject_v2` | data/exp_reader_clauseseg_topical_animate_subject_v2/metrics.json | PARTIAL_PRECISION_STUCK | full | 2026-07-18 (metrics.ts_iso) | A (<ARM CONTAINER arms>) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R90 | `exp_reader_clauseseg_verbclass_filter_v1` | data/exp_reader_clauseseg_verbclass_filter_v1/metrics.json | CLAUSE_SEG_PRECISION_CLEAN | full | 2026-07-18 (metrics.ts_iso) | A (<ARM CONTAINER arms>) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R91 | `exp_read_grow_full_third_reader_clauseseg_generalization_v1` | data/exp_read_grow_full_third_reader_clauseseg_generalization_v1/metrics.json | SCOPE_LIMITED_OR_DEGRADES | full | 2026-07-18 (metrics.ts_iso) | A (no_direct_object) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R92 | `exp_read_deixis_participant_tracking_third_reader_v1` | data/exp_read_deixis_participant_tracking_third_reader_v1/metrics.json | SCOPE_LIMITED_OR_WEAK | full | 2026-07-18 (metrics.ts_iso) | A (n_off) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R93 | `exp_read_argstruct_goal_role_third_reader_v1` | data/exp_read_argstruct_goal_role_third_reader_v1/metrics.json | SCOPE_LIMITED_OR_WEAK | full | 2026-07-19 (metrics.ts_iso) | A (n_goal_fp_off) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R94 | `exp_reader_integration_endtoend_whoaffected_v1_and_v2_extraction_hardened` | data/exp_reader_integration_endtoend_whoaffected_v1/metrics.json | MIDDLE_BAND | full | 2026-07-21 (metrics.ts_iso) | A (candidate_recall_ceiling_labeled_conjfix,endto) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R95 | `exp_reader_endtoend_modern_indomain_construction_gold_v1` | data/exp_reader_endtoend_modern_indomain_construction_gold_v1/metrics.json | DEEPER_BOUND_REGISTER_NOT_LIMITER | full | 2026-07-21 (metrics.ts_iso) | A (MCGUFFEY_baseline_backoff,MCGUFFEY_baseline_v1) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R96 | `exp_reader_parser_swap_struct_endtoend_v1` | data/exp_reader_parser_swap_struct_endtoend_v1/metrics.json | LABELER_WALL_EATS_IT | full | 2026-07-21 (metrics.ts_iso) | A (DELTA_raw_attach_recall_unlabeled,canon_leak_m) | OK | HDLAB:arc_parser.py | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R97 | `exp_reader_selfimprove_artmap_predicted_head_endtoend_v1` | data/exp_reader_selfimprove_artmap_predicted_head_endtoend_v1/metrics.json | IMPROVING_SURVIVES_PREDICTED | full | 2026-07-21 (metrics.ts_iso) | A (PH_ceiling_attach_ok_rate,PH_ee_delta_loop_on_) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R98 | `exp_reader_selfimprove_artmap_posrobust_signature_phpp_v1` | data/exp_reader_selfimprove_artmap_posrobust_signature_phpp_v1/metrics.json | ROBUSTNESS_KILLS_DISCRIMINATION | full | 2026-07-21 (metrics.ts_iso) | A (PHPP_ceiling_attach_ok_rate) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R99 | `exp_mcguffey_ingest_reader_ready_degradation_v1` | data/exp_mcguffey_ingest_reader_ready_degradation_v1/metrics.json | INGEST_HARMLESS_EVEN_NAIVE | full | 2026-07-21 (metrics.ts_iso) | A (<ARM CONTAINER arms>) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R100 | `exp_reader_image_content_recognition_v1` | data/exp_reader_image_content_recognition_v1/metrics.json | GLASSBOX_RECOG_CONTENT_SENSITIVE | full | 2026-07-22 (metrics.ts_iso) | A (<ARM CONTAINER arm_digests>) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R101 | `exp_reader_image_shape_recognition_hog_v1` | data/exp_reader_image_shape_recognition_hog_v1/metrics.json | GLASSBOX_SHAPE_RECOG_STRONG | full | 2026-07-22 (metrics.ts_iso) | A (<ARM CONTAINER arm_digests>) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R102 | `exp_wsd_frame_selectional_gate_v1` | data/exp_wsd_frame_selectional_gate_v1/metrics.json | MIDDLE_BAND | full | 2026-07-22 (metrics.ts_iso) | A (<ARM CONTAINER arm_digests>) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R103 | `exp_pivot_rich_knowledge_full_reader_integration_v1` | data/exp_pivot_rich_knowledge_full_reader_integration_v1/metrics.json | MIDDLE_BAND | full | 2026-07-23 (metrics.ts_iso) | A (F1_random,F1_rich_scrambled,disambig_random) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R104 | `exp_pivot_selectional_independent_kb_2afc_v1` | data/exp_pivot_selectional_independent_kb_2afc_v1/metrics.json | MIDDLE_BAND_PARTIAL_GRANULARITY_RECOVERY | full | 2026-07-23 (metrics.ts_iso) | A (acc_indep_kb_scrambled_mean,acc_indep_kb_scram) | OK | EXP-ONLY | OFF-PATH | -- | C1/reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R105 | `exp_multipred_depparse_argstruct_recall_v2` | data/exp_multipred_depparse_argstruct_recall_v2/metrics.json | MIDDLE_BAND_PARTIAL_PARSER_LIFT | full | 2026-07-23 (metrics.ts_iso) | A (scrambled_table_size) | OK | HDLAB:multi_hop.py | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R106 | `exp_reader_component_oracle_ablation_audit_v1` | data/exp_reader_component_oracle_ablation_audit_v1/metrics.json | AUDIT_SANITY_OK | full | 2026-07-23 (metrics.ts_iso) | A (all_oracle_f1,all_oracle_logic_ceiling_gap) | OK | HDLAB:ablation.py | LIVE | -- | reading | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF RP-C15 |
| R107 | `exp_multipred_argstruct_enumext_v4` | data/exp_multipred_argstruct_enumext_v4/metrics.json | MIDDLE_BAND_PARTIAL_ENUMEXT | full | 2026-07-23 (metrics.ts_iso) | A (n_regressed_vs_baseline,n_single_sent_recovera) | OK | HDLAB:multi_hop.py | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R108 | `exp_reader_role_relabel_emission_preserving_v4` | data/exp_reader_role_relabel_emission_preserving_v4/metrics.json | MIDDLE_BAND_PARTIAL_RELABEL | full | 2026-07-23 (metrics.ts_iso) | A (ablation_forceemit,ablation_lexicon,ablation_n) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R109 | `exp_read_xsent_coref_bundle_focus_v1` | data/exp_read_xsent_coref_bundle_focus_v1/metrics.json | MIDDLE_BAND | full | 2026-07-24 (metrics.ts_iso) | A (baseline_xsent_acc,delta_vs_single_sentence,fl) | OK | HDLAB:bundle_focus_coref.py | OFF-PATH | -- | C4/reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R110 | `exp_read_events_fix_role_reader_litbank_v1` | data/exp_read_events_fix_role_reader_litbank_v1/metrics.json | MEASURED_MECHANISM | full | 2026-07-24 (metrics.ts_iso) | A (naive_f1,naive_prec) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R111 | `exp_read_xsent_coref_learned_centering_cb_continuity_v1` | data/exp_read_xsent_coref_learned_centering_cb_continuity_v1/metrics.json | MIDDLE_BAND | full | 2026-07-24 (metrics.ts_iso) | A (best_single_feature_test_subset_acc,handrule_f) | OK | EXP-ONLY | OFF-PATH | -- | C4/reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R112 | `exp_read_events_supply_ner_entitytype_litbank_v1` | data/exp_read_events_supply_ner_entitytype_litbank_v1/metrics.json | CLEAN_NEGATIVE | full | 2026-07-24 (metrics.ts_iso) | A (no_gate) | OK | EXP-ONLY | OFF-PATH | -- | C4/reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R113 | `exp_read_events_supply_pos_gate_reader_gold_translate_v1` | data/exp_read_events_supply_pos_gate_reader_gold_translate_v1/metrics.json | SUPPLY_POS_NULL_ON_GOLD_HARD_PROSE_ONLY | full | 2026-07-24 (metrics.ts_iso) | A (positive_control_tol) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R114 | `exp_race_reading_comprehension_measure_v1` | data/exp_race_reading_comprehension_measure_v1/metrics.json | READING_RUNG_ESTABLISHED | full | 2026-07-24 (metrics.ts_iso) | A (chance_theoretical,control_majority,control_ra) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R115 | `exp_bge_finemeaning_wall_probe_v1` | data/exp_bge_finemeaning_wall_probe_v1/metrics.json | MIDDLE | full | 2026-07-25 (metrics.ts_iso) | A (bge_zf_fine_lift_over_chance,chance_bge_native) | OK | EXP-ONLY | OFF-PATH | -- | C3 | REGISTRY | UNCHECKED | STATE:VERIFIED |
| R116 | `exp_attachment_coref_lever_lccp_break050_v1` | data/exp_attachment_coref_lever_lccp_break050_v1/metrics.json | HARD_FAIL_ATTACH_RESIDUAL_NOT_COREF_RESOLVABLE | full | 2026-07-19 (metrics.ts_iso) | A (n_fixed_by_B,overall_agent_precision_delta_B_m) | OK | EXP-ONLY | OFF-PATH | -- | C4/reading | REGISTRY | UNCHECKED | STATE:REFUTED |
| R117 | `exp_coref_animacy_prefilter_lccp_break050_v1` | data/exp_coref_animacy_prefilter_lccp_break050_v1/metrics.json | P1:HARD_FAIL_1_ANIMACY_DOES_NOT_HELP / P2:HARD_PASS_2_DISTRIBUTIONAL_INANIMATE_PRECISE / | full | 2026-07-19 (metrics.ts_iso) | A (abstain_off,broke_off,fixed_off) | OK | EXP-ONLY | OFF-PATH | -- | C4/reading | REGISTRY | UNCHECKED | STATE:REFUTED |
| R118 | `exp_compgen_native_bind_role_filler_v1` | data/exp_compgen_native_bind_role_filler_v1/metrics.json | HARD_PASS | full | 2026-07-21 (metrics.ts_iso) | A (chance,gap_native_minus_flat_heldout) | OK | EXP-ONLY | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R119 | `exp_multi_turn_loop_realtext_confidence_abstain_gate_v3` | data/exp_multi_turn_loop_realtext_confidence_abstain_gate_v3/metrics.json | HARD_PASS | full | 2026-07-23 (metrics.ts_iso) | A (beat_scramble,coverage_at_zero_halluc_ceiling) | OK | HDLAB:multi_hop.py | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R120 | `exp_multi_turn_loop_realtext_nphead_gate_v1` | data/exp_multi_turn_loop_realtext_nphead_gate_v1/metrics.json | HARD_PASS | full | 2026-07-23 (metrics.ts_iso) | A (beat_scramble,fixed_threshold) | OK | HDLAB:multi_hop.py | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R121 | `exp_multi_turn_loop_realtext_nphead_correct_v1` | data/exp_multi_turn_loop_realtext_nphead_correct_v1/metrics.json | HARD_PASS | full | 2026-07-23 (metrics.ts_iso) | A (beat_scramble_head_vs_random_noun,fixed_thresh) | OK | HDLAB:multi_hop.py | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R122 | `exp_learner_implicative_sign_supplied_generalization_v1` | data/exp_learner_implicative_sign_supplied_generalization_v1/metrics.json | HARD_PASS_BEYOND_LINEAR_NOT_BEYOND_SIMILARITY | full | 2026-07-23 (metrics.ts_iso) | A (scramble_delta,scramble_module_acc_covered) | OK | EXP-ONLY | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R123 | `exp_analogy_candidate_inference_dense_corpus_v1` | data/exp_analogy_candidate_inference_dense_corpus_v1/metrics.json | HARD_PASS | full | 2026-07-26 (metrics.ts_iso) | A (ablation_interaction,analogy_minus_flat,analog) | OK | EXP-ONLY | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R124 | `exp_grammar_learner_filler_generalization_v1` | data/exp_grammar_learner_filler_generalization_v1/metrics.json | HARD_PASS_FILLER_GENERALIZES_CONFIRMATORY | full | 2026-08-01 (metrics.ts_iso) | A (floor_novel_acc_max) | OK | EXP-ONLY | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R125 | `exp_breadth_foundation_active_growth_loop_ud_ewt_v1` | data/exp_breadth_foundation_active_growth_loop_ud_ewt_v1/metrics.json | HARD_PASS | ABSENT | 2026-07-21 (metrics.ts_iso) | A (auc_delta_real_minus_shuffle_mean,majority_cha) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R126 | `exp_read_causal_chain_on_chain_cause_v1` | data/exp_read_causal_chain_on_chain_cause_v1/metrics.json | HARD_PASS | ABSENT | 2026-07-24 (metrics.ts_iso) | A (<ARM CONTAINER arms>) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R127 | `exp_situation_reader_multisent_demo_v1` | data/exp_situation_reader_multisent_demo_v1/metrics.json | DEMONSTRATED | ABSENT | 2026-07-24 (metrics.ts_iso) | A (single_sentence_xsent_acc) | OK | HDLAB:situation_reader.py | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R128 | `exp_read_comprehension_qa_whodidverb_v1` | data/exp_read_comprehension_qa_whodidverb_v1/metrics.json | DEMONSTRATED | ABSENT | 2026-07-24 (metrics.ts_iso) | A (single_sentence_acc,single_sentence_attempted) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R129 | `exp_multi_competency_coref_ablation_v1` | data/exp_multi_competency_coref_ablation_v1/metrics.json | HARD_PASS | smoke | 2026-07-31 (metrics.ts_iso) | A (tier1_delta_present_ablated) | OK | HDLAB:multi_hop.py | OFF-PATH | -- | C4/reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R130 | `exp_coref_self_confidence_calibration_v1` | data/exp_coref_self_confidence_calibration_v1/metrics.json | HARD_PASS_CALIBRATED_NAME_PATH | ABSENT | 2026-08-02 (metrics.ts_iso) | A (base_error_rate) | OK | EXP-ONLY | OFF-PATH | -- | C4/reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R131 | `exp_reader_selfimprove_case_sleep_udewt_v1` | data/exp_reader_selfimprove_case_sleep_udewt_v1/metrics.json | REAL_IMPROVING_PROPERTY | full | 2026-07-21 (metrics.ts_iso) | A (MUSTFAIL_scramble_fix_rate,MUSTFAIL_scramble_g) | OK | EXP-ONLY | OFF-PATH | -- | reading | REGISTRY | UNCHECKED | STATE:VERIFIED |
| R132 | `exp_reader_selfimprove_artmap_stream_udewt_v1` | data/exp_reader_selfimprove_artmap_stream_udewt_v1/metrics.json | READER_LEARNS | full | 2026-07-21 (metrics.ts_iso) | A (BASE_RATE_override_arc_acc,ENDSTATE_net_fixed,) | OK | EXP-ONLY | OFF-PATH | -- | reading | REGISTRY | UNCHECKED | STATE:VERIFIED |
| R133 | `exp_learned_composition_glue_pun_selectional_generalization_v1` | data/exp_learned_composition_glue_pun_selectional_generalization_v1/metrics.json | MIDDLE_BAND | full | 2026-07-22 (metrics.ts_iso) | A (CG_SCRAMBLE_COLLAPSE_MIN,MM_SCRAMBLE_MIN) | OK | EXP-ONLY | OFF-PATH | -- | reading | REGISTRY | UNCHECKED | STATE:VERIFIED |
| R134 | `exp_read_xsent_coref_event_centrality_v1` | data/exp_read_xsent_coref_event_centrality_v1/metrics.json | MIDDLE_BAND | full | 2026-07-24 (metrics.ts_iso) | A (decision_change_event_vs_off,decision_change_r) | OK | HDLAB:event_centrality_coref.py | OFF-PATH | -- | C4/reading | REGISTRY | UNCHECKED | STATE:VERIFIED |
| R135 | `exp_read_bridge_rolefiller_hd_reasoning_map_v1` | data/exp_read_bridge_rolefiller_hd_reasoning_map_v1/metrics.json | BRIDGE_REASONS_END_TO_END | ABSENT | 2026-07-19 (metrics.ts_iso) | A (bridge_fidelity_single) | OK | EXP-ONLY | OFF-PATH | -- | C2/reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R136 | `exp_read_bridge_noise_tolerance_hd_vs_symbolic_v1` | data/exp_read_bridge_noise_tolerance_hd_vs_symbolic_v1/metrics.json | HD_GRACEFUL_ADVANTAGE | ABSENT | 2026-07-19 (metrics.ts_iso) | A (single) | OK | EXP-ONLY | OFF-PATH | -- | C2/reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R137 | `exp_learned_context_wsd_semcor_verbs_v1` | data/exp_learned_context_wsd_semcor_verbs_v1/metrics.json | HARD_FAIL | full | 2026-07-22 (metrics.ts_iso) | A (scramble_lift) | OK | EXP-ONLY | OFF-PATH | -- | C2 | INVISIBLE | UNCHECKED | STATE:REFUTED |
| R138 | `exp_multi_turn_loop_realtext_oracle_vs_real_compounding_v1` | data/exp_multi_turn_loop_realtext_oracle_vs_real_compounding_v1/metrics.json | HARD_FAIL | full | 2026-07-23 (metrics.ts_iso) | A (compounding_cost_oracle_minus_real) | OK | HDLAB:multi_hop.py | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | state=REFUTED DUP-OF RP-C16 |
| R139 | `exp_multi_turn_loop_realtext_confidence_abstain_gate_v2` | data/exp_multi_turn_loop_realtext_confidence_abstain_gate_v2/metrics.json | HARD_FAIL | full | 2026-07-23 (metrics.ts_iso) | A (beat_scramble,coverage_at_zero_halluc_ceiling) | OK | HDLAB:multi_hop.py | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | STATE:REFUTED |
| R140 | `exp_learner_program_induction_symbolic_extrapolation_v1` | data/exp_learner_program_induction_symbolic_extrapolation_v1/metrics.json | HARD_FAIL_UNSEEN_CELL_UNIDENTIFIABLE | full | 2026-07-23 (metrics.ts_iso) | A (unseen_cell_acc_module_no_proginduction) | OK | EXP-ONLY | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | STATE:REFUTED |
| R141 | `exp_native_meaning_encoder_binder_grounded_v1` | data/exp_native_meaning_encoder_binder_grounded_v1_smoke/metrics.json | CONTEXT-CARRIES-distributional-to-grounded | smoke | 2026-07-25 (metrics.ts_iso) | A (<ARM CONTAINER arm_pk_hashes>) | OK | EXP-ONLY | OFF-PATH | -- | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R142 | `exp_verbnet_affectedness_lexicon_correction_v1` | data/exp_verbnet_affectedness_lexicon_correction_v1/metrics.json | CORRECTION_LIFTS_NO_REGRESSION | full | 2026-07-21 (metrics.ts_iso) | A (ud_primary_fixed_by_correction) | OK | EXP-ONLY | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R143 | `exp_compgen_native_bind_desaturation_sweep_v1` | data/exp_compgen_native_bind_desaturation_sweep_v1/metrics.json | GRACEFUL_EROSION | full | 2026-07-22 (metrics.ts_iso) | A (chance) | OK | EXP-ONLY | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R144 | `exp_compgen_native_bind_real_text_v1` | data/exp_compgen_native_bind_real_text_v1/metrics.json | CG_ROBUST_REAL_TEXT | full | 2026-07-22 (metrics.ts_iso) | A (chance) | OK | EXP-ONLY | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R145 | `exp_compgen_native_bind_attested_real_text_v2` | data/exp_compgen_native_bind_attested_real_text_v2/metrics.json | CG_ATTESTED_REAL_TEXT | full | 2026-07-22 (metrics.ts_iso) | A (chance,flat_oracle_ho) | OK | EXP-ONLY | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R146 | `exp_compgen_geometry_ablation_v1` | data/exp_compgen_geometry_ablation_v1/metrics.json | CG_CANDIDATE_GEOMETRY_FREE | full | 2026-07-22 (metrics.ts_iso) | A (chance,rand_floor,random_off_cos) | OK | HDLAB:ablation.py | LIVE | -- | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R147 | `exp_multi_turn_loop_realtext_confidence_abstain_gate_v1` | data/exp_multi_turn_loop_realtext_confidence_abstain_gate_v1/metrics.json | MIDDLE_BAND | full | 2026-07-23 (metrics.ts_iso) | A (beat_scramble,coverage_at_zero_halluc_ceiling) | OK | HDLAB:multi_hop.py | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R148 | `exp_grammar_learner_encounter_rule_uncover_generalize_v1` | data/exp_grammar_learner_encounter_rule_uncover_generalize_v1/metrics.json | MIDDLE_BAND | full | 2026-08-01 (metrics.ts_iso) | A (floor_acc_max,floor_acc_min,floor_theoretical) | OK | EXP-ONLY | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R149 | `exp_read_nested_clause_relative_third_reader_v1` | data/exp_read_nested_clause_relative_third_reader_v1/metrics.json | NEST_RESOLVES_EMBEDDING | ABSENT | 2026-07-19 (metrics.ts_iso) | A (n_off) | OK | EXP-ONLY | OFF-PATH | -- | reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R150 | `exp_concept_featural_enrichment_v2` | data/exp_concept_featural_enrichment_v2/metrics.json | CONTENT_ENRICHMENT_HARD_FAIL | full | 2026-07-25 (metrics.ts_iso) | A (B_single_insample_precision,RANDOM_insample_pr) | OK | EXP-ONLY | OFF-PATH | -- | -- | REGISTRY | UNCHECKED | STATE:REFUTED |
| R151 | `exp_encoder_generic_vs_entity_addressed_v1` | data/exp_encoder_generic_vs_entity_addressed_v1/metrics.json | MIDDLE | lite | 2026-08-01 (metrics.ts_iso) | ARM (geom_frac_flat) | OK | EXP-ONLY | OFF-PATH | -- | C3/C4 | REGISTRY | UNCHECKED | STATE:VERIFIED |
| R152 | `exp_earn_coref_pronoun_centering_v1` | data/exp_earn_coref_pronoun_centering_v1/metrics.json | NULL_INVESTIGATE | ABSENT | 2026-08-02 (metrics.ts_iso) | A (n_role_flips_baseline_vs_centering) | OK | EXP-ONLY | OFF-PATH | -- | C4/reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R153 | `exp_learner_module_refactor_proof_v1` | data/exp_learner_module_refactor_proof_v1/metrics.json | HARD_PASS_REFACTOR_PROVEN | ABSENT | 2026-07-23 (metrics.ts_iso) | A (banked_CONTROL_ruleind_acc_mean) | OK | EXP-ONLY | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R154 | `exp_hd_fact_store_capacity_and_index_v1` | data/exp_hd_fact_store_capacity_and_index_v1/metrics.json | PASS | ABSENT | 2026-07-24 (metrics.ts_iso) | A | OK | HDLAB:hd_fact_store.py | LIVE | -- | C1 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R155 | `exp_earn_coref_match_or_allocate_v1` | data/exp_earn_coref_match_or_allocate_v1/metrics.json | HARD_FAIL_LEARNABLE_DOES_NOT_BEAT_FLOOR | ABSENT | 2026-08-02 (metrics.ts_iso) | A (<ARM CONTAINER arms>) | OK | EXP-ONLY | OFF-PATH | -- | C4/reading | REGISTRY | UNCHECKED | STATE:REFUTED |
| R156 | `exp_arc_reasoner_entity_linking_upgrade_v1` | data/exp_arc_reasoner_entity_linking_upgrade_v1/metrics.json | MIDDLE | full | 2026-07-25 (metrics.ts_iso) | A (chance,covered_baseline_acc,covered_shuffle_ac) | OK | HDLAB:reasoner.py | OFF-PATH | -- | C4 | REGISTRY | UNCHECKED | STATE:VERIFIED |
| R157 | `exp_coref_candidate_pool_phi_hygiene_v1` | data/exp_coref_candidate_pool_phi_hygiene_v1/metrics.json | MIDDLE_BAND | ABSENT | 2026-07-24 (metrics.ts_iso) | A (baseline_recency_acc) | OK | EXP-ONLY | OFF-PATH | -- | C4/reading | REGISTRY | UNCHECKED | STATE:VERIFIED |
| R158 | `exp_coref_self_confidence_calibration_v2` | data/exp_coref_self_confidence_calibration_v2/metrics.json | MIDDLE_BAND_PRONOUN | ABSENT | 2026-08-02 (metrics.ts_iso) | A (base_error_rate) | OK | EXP-ONLY | OFF-PATH | -- | C4/reading | REGISTRY | UNCHECKED | STATE:VERIFIED |
| R159 | `exp_coref_flag_fix_loop_topic_continuity_v1` | data/exp_coref_flag_fix_loop_topic_continuity_v1/metrics.json | NULL_FIX_MECHANISM | ABSENT | 2026-08-02 (metrics.ts_iso) | A (base_pronoun_error_rate) | OK | EXP-ONLY | OFF-PATH | -- | C4/reading | REGISTRY | UNCHECKED | STATE:VERIFIED |
| R160 | `exp_coref_flag_fix_loop_principle_b_v1` | data/exp_coref_flag_fix_loop_principle_b_v1/metrics.json | PARTIAL_COREF_ONLY | ABSENT | 2026-08-02 (metrics.ts_iso) | A (oracle) | OK | EXP-ONLY | OFF-PATH | -- | C4/reading | REGISTRY | UNCHECKED | STATE:VERIFIED |
| R161 | `exp_coref_loop_cross_clause_discourse_v1` | data/exp_coref_loop_cross_clause_discourse_v1/metrics.json | PARTIAL_QUERY_ONLY | ABSENT | 2026-08-03 (metrics.ts_iso) | A (<ARM CONTAINER arms>) | OK | EXP-ONLY | OFF-PATH | -- | C4/reading | REGISTRY | UNCHECKED | STATE:VERIFIED |
| R162 | `exp_coref_autonomous_fix_router_v1` | data/exp_coref_autonomous_fix_router_v1/metrics.json | REDIRECT_TRACKS_ALWAYS_APPLY_CANNOT_REJECT_TRAP | ABSENT | 2026-08-03 (metrics.ts_iso) | A (auto_keep_oracle_revert_FALSE_KEEP,auto_revert) | OK | EXP-ONLY | OFF-PATH | -- | C4/reading | REGISTRY | UNCHECKED | STATE:VERIFIED |
| R163 | `exp_compgen_native_bind_matched_hard_v3` | data/exp_compgen_native_bind_matched_hard_v3/metrics.json | MEASURED_MECHANISM | JUNK(matched_hard) | 2026-07-22 (metrics.ts_iso) | A (chance,flat_oracle_ho) | OK | EXP-ONLY | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R164 | `exp_learner_module_gam_plugin_proof_v1` | data/exp_learner_module_gam_plugin_proof_v1/metrics.json | MIDDLE_BAND_GAM_PLUGIN | ABSENT | 2026-07-23 (metrics.ts_iso) | A (gam_compression_ratio_shuffled) | OK | EXP-ONLY | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R165 | `exp_learner_implicative_negation_entailment_v1` | data/exp_learner_implicative_negation_entailment_v1/metrics.json | MIDDLE_BAND | self_test | 2026-07-23 (metrics.ts_iso) | A (scramble_delta,scramble_module_acc_seen) | OK | EXP-ONLY | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| R166 | `exp_perceptual_grounding_gap_audit_v1` | (none) | (no verdict key) | ABSENT | 2026-07-19 (ledger) | UNPINNED | NO DIR | EXP-ONLY | OFF-PATH | -- | C3 | INVISIBLE | UNCHECKED | STATE:FOUND |
| R167 | `exp_derived_filler_typing_single_edge_grounding_v1` | (none) | (no verdict key) | ABSENT | 2026-07-20 (ledger) | UNPINNED | NO DIR | EXP-ONLY | OFF-PATH | -- | C3 | INVISIBLE | UNCHECKED | STATE:FOUND |
| R168 | `exp_af43a6dd_grounding_feasibility_probe_atomic2019` | (none) | (no verdict key) | ABSENT | 2026-07-21 (ledger) | UNPINNED | NO DIR | EXP-ONLY | OFF-PATH | -- | C3 | INVISIBLE | UNCHECKED | STATE:FOUND |
| R169 | `exp_native_meaning_encoder_wordnet_mechanism_v1` | data/exp_native_meaning_encoder_wordnet_mechanism_v1_selftest/metrics.json | CELL_CRASHED | ABSENT | 2026-07-25 (metrics.ts_iso) | NO FLOOR | OK | EXP-ONLY | OFF-PATH | -- | C3 | INVISIBLE | UNCHECKED | STATE:FOUND |
| R170 | `exp_probe_fix_tier_verb_semantic_ceiling_flagged_pronouns_v1` | (none) | (no verdict key) | ABSENT | 2026-08-02 (ledger) | UNPINNED | NO DIR | HDLAB:semantic.py | LIVE | -- | C3 | INVISIBLE | UNCHECKED | STATE:FOUND |
| R171 | `exp_hd_fact_store_source_trust_vet_v1` | data/exp_hd_fact_store_source_trust_vet_v1/metrics.json | PASS | ABSENT | 2026-07-24 (metrics.ts_iso) | NO FLOOR | OK | HDLAB:hd_fact_store.py | LIVE | -- | -- | ORGAN_MAP | UNCHECKED | STATE:FOUND |

---
#### Group M -- the brain-mechanism families (232 rows) [was S6 sec 10]

Sorted by the sec-4 score, descending. **144 are `full`; 60 are `smoke`, 5 `self_test`, 15
`ABSENT`, 5 JUNK, 3 null -- the run-mode column is the filter, not the row count.** 120 of the 144
FULL rows are invisible to all four planning artifacts.

| # | cell | evidence (metrics.json) | verdict (as read) | run mode | date (src) | floor BY SHAPE | disk | module | live | geometry | moves | doc visibility | supersede | STATE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| M1 | `exp_novel_atom_generalization_codebook_binding` | data/exp_novel_atom_generalization_codebook_binding_v1_smoke/metrics.json | HARD_PASS | JUNK(exp_novel_atom_general) | 2026-07-20 (metrics.ts_iso) | A (ceiling_check_seen_query_acc_mean) | OK | HDLAB:binding.py | LIVE | EXPANSIVE+FACTORIAL | C1/C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M2 | `exp_novel_atom_generalization_codebook_binding_v1` | data/exp_novel_atom_generalization_codebook_binding_v1/metrics.json | HARD_PASS | JUNK(exp_novel_atom_general) | 2026-07-20 (metrics.ts_iso) | A (ceiling_check_seen_query_acc_mean) | OK | HDLAB:binding.py | LIVE | EXPANSIVE+FACTORIAL | C1/C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M3 | `exp_substrate_anisotropy_dg_pattern_separation_prewrite_v1` | data/exp_substrate_anisotropy_dg_pattern_separation_prewrite_v1/metrics.json | HARD_PASS | full | UNDATED (none) | A (arm_knn_baseline_at_M_sentinel,arm_uniform_no_) | OK | HDLAB:dg_pattern_separation.py | OFF-PATH | EXPANSIVE | C3 | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF RP-A5 |
| M4 | `exp_substrate_pc_sparsity_x_encoder_crossproduct_v1_n8192_seed_7` | data/exp_substrate_pc_sparsity_x_encoder_crossproduct_v1_n8192_seed_7/metrics.json | HARD_PASS | full | 2026-07-01 (metrics.ts_iso) | A (top1_random) | OK | EXP-ONLY | OFF-PATH | EXPANSIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M5 | `exp_substrate_pc_sparsity_x_encoder_crossproduct_v1_n8192_seed_13` | data/exp_substrate_pc_sparsity_x_encoder_crossproduct_v1_n8192_seed_13/metrics.json | HARD_PASS | full | 2026-07-01 (metrics.ts_iso) | A (top1_random) | OK | EXP-ONLY | OFF-PATH | EXPANSIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M6 | `exp_substrate_pc_sparsity_x_encoder_crossproduct_v1_n8192_seed_19` | data/exp_substrate_pc_sparsity_x_encoder_crossproduct_v1_n8192_seed_19/metrics.json | HARD_PASS | full | 2026-07-01 (metrics.ts_iso) | A (top1_random) | OK | EXP-ONLY | OFF-PATH | EXPANSIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M7 | `exp_substrate_pc_sparsity_x_encoder_crossproduct_v2_n8192_seed_7` | data/exp_substrate_pc_sparsity_x_encoder_crossproduct_v2_n8192_seed_7/metrics.json | HARD_PASS | full | 2026-07-01 (metrics.ts_iso) | A (top1_random) | OK | EXP-ONLY | OFF-PATH | EXPANSIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M8 | `exp_substrate_pc_sparsity_x_encoder_crossproduct_v2_n8192_seed_13` | data/exp_substrate_pc_sparsity_x_encoder_crossproduct_v2_n8192_seed_13/metrics.json | HARD_PASS | full | 2026-07-01 (metrics.ts_iso) | A (top1_random) | OK | EXP-ONLY | OFF-PATH | EXPANSIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M9 | `exp_substrate_pc_sparsity_x_encoder_crossproduct_v2_n8192_seed_19` | data/exp_substrate_pc_sparsity_x_encoder_crossproduct_v2_n8192_seed_19/metrics.json | HARD_PASS | full | 2026-07-01 (metrics.ts_iso) | A (top1_random) | OK | EXP-ONLY | OFF-PATH | EXPANSIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M10 | `exp_selfplay_dg_pattern_separation_xfit_v1` | data/exp_selfplay_dg_pattern_separation_xfit_v1/metrics.json | HARD_FAIL_REPRESENTATION_INSUFFICIENT_REDIRECT_EXOGENOUS | full | 2026-07-09 (metrics.ts_iso) | A (<ARM CONTAINER per_arm_agg>) | OK | HDLAB:dg_pattern_separation.py | OFF-PATH | EXPANSIVE | C3 | REGISTRY | UNCHECKED | STATE:REFUTED |
| M11 | `exp_dg_pattern_separation_mcscript_purity_v1` | data/exp_dg_pattern_separation_mcscript_purity_v1/metrics.json | HARD_FAIL | full | UNDATED (none) | A (<ARM CONTAINER arm_hashes>) | OK | HDLAB:dg_pattern_separation.py | OFF-PATH | EXPANSIVE | C3 | INVISIBLE | UNCHECKED | STATE:REFUTED |
| M12 | `exp_substrate_sparsity_free_axis_v4_pc_only_n4096_seed_7` | data/exp_substrate_sparsity_free_axis_v4_pc_only_n4096_seed_7/metrics.json | HARD_PASS | full | 2026-07-01 (metrics.ts_iso) | A (top1_random_mean) | OK | EXP-ONLY | OFF-PATH | EXPANSIVE | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M13 | `exp_substrate_sparsity_free_axis_v4_pc_only_n4096_seed_13` | data/exp_substrate_sparsity_free_axis_v4_pc_only_n4096_seed_13/metrics.json | HARD_PASS | full | 2026-07-01 (metrics.ts_iso) | A (top1_random_mean) | OK | EXP-ONLY | OFF-PATH | EXPANSIVE | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M14 | `exp_substrate_sparsity_free_axis_v5_wm_fixed_n4096_seed_7` | data/exp_substrate_sparsity_free_axis_v5_wm_fixed_n4096_seed_7/metrics.json | HARD_PASS | full | 2026-07-02 (metrics.ts_iso) | A (hf_no_c_lever_count) | OK | EXP-ONLY | OFF-PATH | EXPANSIVE | -- | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF RP-D1 |
| M15 | `exp_substrate_sparsity_free_axis_v5_wm_fixed_n4096_seed_13` | data/exp_substrate_sparsity_free_axis_v5_wm_fixed_n4096_seed_13/metrics.json | HARD_PASS | full | 2026-07-02 (metrics.ts_iso) | A (hf_no_c_lever_count) | OK | EXP-ONLY | OFF-PATH | EXPANSIVE | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M16 | `exp_substrate_sparsity_free_axis_v5_wm_fixed_n4096_seed_19` | data/exp_substrate_sparsity_free_axis_v5_wm_fixed_n4096_seed_19/metrics.json | HARD_PASS | full | 2026-07-02 (metrics.ts_iso) | A (hf_no_c_lever_count) | OK | EXP-ONLY | OFF-PATH | EXPANSIVE | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M17 | `exp_substrate_sparsity_free_axis_v4b_pc_widened_alpha_grid_n4096_seed_7` | data/exp_substrate_sparsity_free_axis_v4b_pc_widened_alpha_grid_n4096_seed_7/metrics.json | HARD_PASS | full | 2026-07-02 (metrics.ts_iso) | A (top1_random_mean) | OK | EXP-ONLY | OFF-PATH | EXPANSIVE | -- | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF CG-B58 |
| M18 | `exp_substrate_sparsity_free_axis_v4b_pc_widened_alpha_grid_n4096_seed_13` | data/exp_substrate_sparsity_free_axis_v4b_pc_widened_alpha_grid_n4096_seed_13/metrics.json | HARD_PASS | full | 2026-07-02 (metrics.ts_iso) | A (top1_random_mean) | OK | EXP-ONLY | OFF-PATH | EXPANSIVE | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M19 | `exp_substrate_sparsity_free_axis_v4b_pc_widened_alpha_grid_n4096_seed_19` | data/exp_substrate_sparsity_free_axis_v4b_pc_widened_alpha_grid_n4096_seed_19/metrics.json | HARD_PASS | full | 2026-07-02 (metrics.ts_iso) | A (top1_random_mean) | OK | EXP-ONLY | OFF-PATH | EXPANSIVE | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M20 | `exp_resonator_verifier_readout_v1` | data/exp_resonator_verifier_readout_v1/metrics.json | HARD_PASS | full | UNDATED (none) | A (<ARM CONTAINER by_arm>) | OK | EXP-ONLY | OFF-PATH | FACTORIAL | C3/reading | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF RP-A9 |
| M21 | `exp_substrate_concept_encoder_spoke3_dg_ca3_marr_cls_replay` | data/exp_substrate_concept_encoder_spoke3_dg_ca3_marr_cls_replay_v1_smoke/metrics.json | HARD_PASS | smoke | 2026-07-02 (metrics.ts_iso) | A (<ARM CONTAINER arm_summary>) | OK | HDLAB:concept_encoder.py | OFF-PATH | EXPANSIVE+CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF RP-D6 |
| M22 | `exp_substrate_sparsity_free_axis_v2_n4096_seed_7` | data/exp_substrate_sparsity_free_axis_v2_n4096_seed_7/metrics.json | HARD_FAIL | full | 2026-07-01 (metrics.ts_iso) | A (top1_random_mean) | OK | EXP-ONLY | OFF-PATH | EXPANSIVE | -- | INVISIBLE | UNCHECKED | STATE:REFUTED |
| M23 | `exp_substrate_sparsity_free_axis_v2_n4096_seed_13` | data/exp_substrate_sparsity_free_axis_v2_n4096_seed_13/metrics.json | HARD_FAIL | full | 2026-07-01 (metrics.ts_iso) | A (top1_random_mean) | OK | EXP-ONLY | OFF-PATH | EXPANSIVE | -- | INVISIBLE | UNCHECKED | STATE:REFUTED |
| M24 | `exp_substrate_sparsity_free_axis_v2_n4096_seed_19` | data/exp_substrate_sparsity_free_axis_v2_n4096_seed_19/metrics.json | HARD_FAIL | full | 2026-07-01 (metrics.ts_iso) | A (top1_random_mean) | OK | EXP-ONLY | OFF-PATH | EXPANSIVE | -- | INVISIBLE | UNCHECKED | STATE:REFUTED |
| M25 | `exp_graded_divisive_comparator_v1` | data/exp_graded_divisive_comparator_v1/metrics.json | HARD_PASS | full | 2026-08-14 (metrics.ts_iso) | A (chance) | OK | EXP-ONLY | OFF-PATH | EXPANSIVE | -- | ORGAN_MAP,REGISTRY | UNCHECKED | STATE:VERIFIED |
| M26 | `exp_grounding_encoder_sparse_block_binding_v1` | data/exp_grounding_encoder_sparse_block_binding_v1/metrics.json | HARD_FAIL_BLOCK_BINDING_INSUFFICIENT | full | 2026-07-09 (metrics.ts_iso) | A (cos_floor_c) | OK | HDLAB:lock_in_amp.py | OFF-PATH | FACTORIAL | C1/C3 | INVISIBLE | UNCHECKED | STATE:REFUTED |
| M27 | `exp_grounding_binding_structured_encoder_multihop_v1` | data/exp_grounding_binding_structured_encoder_multihop_v1/metrics.json | INCONCLUSIVE_NO_ONESHOT_CAP | full | 2026-07-09 (metrics.ts_iso) | A (cos_floor_c) | OK | HDLAB:multi_hop.py | OFF-PATH | FACTORIAL | C1/C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M28 | `exp_resonator_verifier_readout` | data/exp_resonator_verifier_readout_v1_smoke/metrics.json | HARD_PASS | smoke | UNDATED (none) | A (<ARM CONTAINER by_arm>) | OK | EXP-ONLY | OFF-PATH | FACTORIAL | C3/reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M29 | `exp_substrate_spoke3_hippocampal_encoder_episodic_binding_smoke_2026_07_03` | data/exp_substrate_spoke3_hippocampal_encoder_episodic_binding_smoke_2026_07_03/metrics.json | HARD_PASS | smoke | UNDATED (none) | A (<ARM CONTAINER per_arm_aggregate>) | OK | HDLAB:hippocampal_encoder.py | OFF-PATH | FACTORIAL | C1/C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M30 | `exp_stage1_regime_map_storage_x_cleanup_v1_s7` | data/exp_stage1_regime_map_storage_x_cleanup_v1_s7/metrics.json | HARD_PASS | full | 2026-07-03 (metrics.ts_iso) | A (<ARM CONTAINER bundled_arm_stats>) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M31 | `exp_substrate_pc_cleanup_family_phase_diagram_v2_M_sweep_s11` | data/exp_substrate_pc_cleanup_family_phase_diagram_v2_M_sweep_s11/metrics.json | HARD_PASS | full | 2026-07-03 (metrics.ts_iso) | A (top1_random) | OK | HDLAB:cleanup_family.py | LIVE | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M32 | `exp_substrate_pc_cleanup_family_phase_diagram_v2_M_sweep_s17` | data/exp_substrate_pc_cleanup_family_phase_diagram_v2_M_sweep_s17/metrics.json | HARD_PASS | full | 2026-07-03 (metrics.ts_iso) | A (top1_random) | OK | HDLAB:cleanup_family.py | LIVE | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M33 | `exp_substrate_pc_cleanup_family_phase_diagram_v2_M_sweep_s23` | data/exp_substrate_pc_cleanup_family_phase_diagram_v2_M_sweep_s23/metrics.json | HARD_PASS | full | 2026-07-03 (metrics.ts_iso) | A (top1_random) | OK | HDLAB:cleanup_family.py | LIVE | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M34 | `exp_stage1_regime_map_storage_x_cleanup_v1_s13` | data/exp_stage1_regime_map_storage_x_cleanup_v1_s13/metrics.json | HARD_PASS | full | 2026-07-03 (metrics.ts_iso) | A (<ARM CONTAINER bundled_arm_stats>) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M35 | `exp_stage1_regime_map_storage_x_cleanup_v1_s19` | data/exp_stage1_regime_map_storage_x_cleanup_v1_s19/metrics.json | HARD_PASS | full | 2026-07-03 (metrics.ts_iso) | A (<ARM CONTAINER bundled_arm_stats>) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M36 | `exp_substrate_operational_wall_dual_readout_bit_match_and_cleanup_v2c_seed_7` | data/exp_substrate_operational_wall_dual_readout_bit_match_and_cleanup_v2c_seed_7/metrics.json | HARD_PASS | full | UNDATED (none) | A (crlb_floor_computed_bit_match,crlb_floor_compu) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | C3/reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M37 | `exp_substrate_operational_wall_dual_readout_bit_match_and_cleanup_v2c_seed_19` | data/exp_substrate_operational_wall_dual_readout_bit_match_and_cleanup_v2c_seed_19/metrics.json | HARD_PASS | full | UNDATED (none) | A (crlb_floor_computed_bit_match,crlb_floor_compu) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | C3/reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M38 | `exp_substrate_operational_wall_dual_readout_bit_match_and_cleanup_v2c_seed_13` | data/exp_substrate_operational_wall_dual_readout_bit_match_and_cleanup_v2c_seed_13/metrics.json | HARD_PASS | full | UNDATED (none) | A (crlb_floor_computed_bit_match,crlb_floor_compu) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | C3/reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M39 | `exp_stage1_regime_probe_8_algebra_x_cleanup_non_saturated_v1_s7` | data/exp_stage1_regime_probe_8_algebra_x_cleanup_non_saturated_v1_s7/metrics.json | HARD_PASS | full | 2026-07-04 (metrics.ts_iso) | A (h3_null_threshold) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M40 | `exp_stage1_regime_probe_13_L_x_cleanup_non_saturated_v1_s13` | data/exp_stage1_regime_probe_13_L_x_cleanup_non_saturated_v1_s13/metrics.json | HARD_PASS | full | 2026-07-04 (metrics.ts_iso) | A (h3_null_threshold) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M41 | `exp_stage1_regime_probe_13_L_x_cleanup_non_saturated_v1_s7` | data/exp_stage1_regime_probe_13_L_x_cleanup_non_saturated_v1_s7/metrics.json | HARD_PASS | full | 2026-07-04 (metrics.ts_iso) | A (h3_null_threshold) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M42 | `exp_stage1_regime_probe_8_algebra_x_cleanup_non_saturated_v1_s13` | data/exp_stage1_regime_probe_8_algebra_x_cleanup_non_saturated_v1_s13/metrics.json | HARD_PASS | full | 2026-07-04 (metrics.ts_iso) | A (h3_null_threshold) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M43 | `exp_stage1_regime_probe_8_algebra_x_cleanup_non_saturated_v1_s19` | data/exp_stage1_regime_probe_8_algebra_x_cleanup_non_saturated_v1_s19/metrics.json | HARD_PASS | full | 2026-07-04 (metrics.ts_iso) | A (h3_null_threshold) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M44 | `exp_stage1_regime_probe_8_algebra_x_cleanup_non_saturated_v1_s11` | data/exp_stage1_regime_probe_8_algebra_x_cleanup_non_saturated_v1_s11/metrics.json | HARD_PASS | full | 2026-07-04 (metrics.ts_iso) | A (h3_null_threshold) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M45 | `exp_stage1_regime_probe_8_algebra_x_cleanup_non_saturated_v1_s17` | data/exp_stage1_regime_probe_8_algebra_x_cleanup_non_saturated_v1_s17/metrics.json | HARD_PASS | full | 2026-07-04 (metrics.ts_iso) | A (h3_null_threshold) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M46 | `exp_cortex_regenerative_cleanup_vs_analog_accumulate_v2` | data/exp_cortex_regenerative_cleanup_vs_analog_accumulate_v2/metrics.json | HARD_PASS | full | 2026-07-05 (metrics.ts_iso) | A (chance_floor) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M47 | `exp_resonator_deflation_lowsnr_v1` | data/exp_resonator_deflation_lowsnr_v1/metrics.json | HARD_PASS | full | UNDATED (none) | A (<ARM CONTAINER by_arm>) | OK | EXP-ONLY | OFF-PATH | FACTORIAL | -- | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF RP-A14 |
| M48 | `exp_resonator_theta_gamma_peel_v1` | data/exp_resonator_theta_gamma_peel_v1/metrics.json | HARD_PASS | full | UNDATED (none) | A (<ARM CONTAINER by_arm>) | OK | EXP-ONLY | OFF-PATH | FACTORIAL | -- | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF RP-A14 |
| M49 | `exp_substrate_resonator_focus_lever_depth_v2` | data/exp_substrate_resonator_focus_lever_depth_v2/metrics.json | HARD_PASS | full | UNDATED (none) | A (<ARM CONTAINER arm_digests>) | OK | EXP-ONLY | OFF-PATH | FACTORIAL | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M50 | `exp_cortex_attention_binding_router_v1_seed_7` | data/exp_cortex_attention_binding_router_v1_seed_7/metrics.json | HARD_PASS | full | UNDATED (none) | A (HF_class_collapse_floor,HF_mechanism_floor,HP_) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M51 | `exp_cortex_attention_binding_router_v1_seed_13` | data/exp_cortex_attention_binding_router_v1_seed_13/metrics.json | HARD_PASS | full | UNDATED (none) | A (HF_class_collapse_floor,HF_mechanism_floor,HP_) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M52 | `exp_cortex_attention_binding_router_v1_seed_19` | data/exp_cortex_attention_binding_router_v1_seed_19/metrics.json | HARD_PASS | full | UNDATED (none) | A (HF_class_collapse_floor,HF_mechanism_floor,HP_) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M53 | `exp_cortex_attention_binding_router_v2_seed_7` | data/exp_cortex_attention_binding_router_v2_seed_7/metrics.json | HARD_PASS | full | UNDATED (none) | A (HF_class_collapse_floor,HF_mechanism_floor,HP_) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M54 | `exp_cortex_attention_binding_router_v2_seed_13` | data/exp_cortex_attention_binding_router_v2_seed_13/metrics.json | HARD_PASS | full | UNDATED (none) | A (HF_class_collapse_floor,HF_mechanism_floor,HP_) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M55 | `exp_cortex_attention_binding_router_v2_seed_19` | data/exp_cortex_attention_binding_router_v2_seed_19/metrics.json | HARD_PASS | full | UNDATED (none) | A (HF_class_collapse_floor,HF_mechanism_floor,HP_) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M56 | `exp_interference_avoidance_conjunctive_vs_additive_v1` | data/exp_interference_avoidance_conjunctive_vs_additive_v1/metrics.json | HARD_PASS | full | UNDATED (none) | A (hf_control_confound,hf_gap_orth_freq_max,hp_co) | OK | HDLAB:additive_map.py | OFF-PATH | FACTORIAL | -- | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF CG-A20 |
| M57 | `exp_graded_divisive_comparator_v1_SMOKE_n600` | data/exp_graded_divisive_comparator_v1_SMOKE_n600/metrics.json | HARD_PASS | smoke | 2026-08-14 (metrics.ts_iso) | A (chance) | OK | EXP-ONLY | OFF-PATH | EXPANSIVE | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M58 | `exp_graded_divisive_comparator_v1_SELFTEST` | data/exp_graded_divisive_comparator_v1_SELFTEST/metrics.json | SELFTEST_PASS | self_test | UNDATED (none) | A (null_false_positives,null_replicates) | OK | EXP-ONLY | OFF-PATH | EXPANSIVE | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M59 | `exp_wm_addressing_dg_fixed_projection_v1` | data/exp_wm_addressing_dg_fixed_projection_v1/metrics.json | SELFTEST_PASS | self_test | 2026-07-30 (metrics.ts_iso) | A (addr_chance,chance_recall) | OK | EXP-ONLY | OFF-PATH | EXPANSIVE | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M60 | `exp_pfc_controller_softmax_margin_abstain` | data/exp_pfc_controller_softmax_margin_abstain_v2_smoke/metrics.json | HARD_PASS | smoke | 2026-06-27 (metrics.ts_iso) | A (lift_over_argmax,lift_over_random,lift_over_si) | OK | EXP-ONLY | OFF-PATH | EXPANSIVE | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M61 | `exp_stage2_cleanup_latency_operating_curve_v1_seed_7` | data/exp_stage2_cleanup_latency_operating_curve_v1_seed_7/metrics.json | HARD_PASS | full | 2026-07-02 (metrics.ts_iso) | A | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M62 | `exp_stage2_cleanup_latency_operating_curve_v1_seed_13` | data/exp_stage2_cleanup_latency_operating_curve_v1_seed_13/metrics.json | HARD_PASS | full | 2026-07-02 (metrics.ts_iso) | A | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M63 | `exp_stage2_cleanup_latency_operating_curve_v1_seed_19` | data/exp_stage2_cleanup_latency_operating_curve_v1_seed_19/metrics.json | HARD_PASS | full | 2026-07-02 (metrics.ts_iso) | A | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M64 | `exp_dense_hopfield_readout_capacity_correlated_codes_v1` | data/exp_dense_hopfield_readout_capacity_correlated_codes_v1/metrics.json | HARD_PASS | full | 2026-07-14 (metrics.ts_iso) | A (pos_control_iid_lift) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | C1/C3/reading | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF RP-A4 |
| M65 | `exp_resonator_decision_compgen_2factor_v1` | data/exp_resonator_decision_compgen_2factor_v1/metrics.json | HARD_PASS | full | 2026-07-21 (metrics.ts_iso) | A (chance) | OK | EXP-ONLY | OFF-PATH | FACTORIAL | -- | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF RD-R11 |
| M66 | `exp_substrate_cross_modal_binding_visual_auditory_v1_seed_7` | data/exp_substrate_cross_modal_binding_visual_auditory_v1_seed_7/metrics.json | HARD_PASS | full | 2026-06-28 (metrics.ts_iso) | A (positive_control_recall) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1 | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF CG-B88 |
| M67 | `exp_substrate_cross_modal_binding_visual_auditory_v1_seed_13` | data/exp_substrate_cross_modal_binding_visual_auditory_v1_seed_13/metrics.json | HARD_PASS | full | 2026-06-28 (metrics.ts_iso) | A (positive_control_recall) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M68 | `exp_substrate_cross_modal_binding_visual_auditory_v1_seed_19` | data/exp_substrate_cross_modal_binding_visual_auditory_v1_seed_19/metrics.json | HARD_PASS | full | 2026-06-28 (metrics.ts_iso) | A (positive_control_recall) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M69 | `exp_substrate_cross_modal_binding_3rd_modality_v1_seed_7` | data/exp_substrate_cross_modal_binding_3rd_modality_v1_seed_7/metrics.json | HARD_PASS | full | 2026-07-01 (metrics.ts_iso) | A (positive_control_cv,positive_control_recall) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1 | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF CG-B76 |
| M70 | `exp_cross_modal_binding_4_5_modality_v1_seed_13` | data/exp_cross_modal_binding_4_5_modality_v1_seed_13/metrics.json | HARD_PASS | full | 2026-07-01 (metrics.ts_iso) | A (positive_control_cv,positive_control_recall) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M71 | `exp_cross_modal_binding_4_5_modality_v1_seed_7` | data/exp_cross_modal_binding_4_5_modality_v1_seed_7/metrics.json | HARD_PASS | full | 2026-07-01 (metrics.ts_iso) | A (positive_control_cv,positive_control_recall) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M72 | `exp_cross_modal_binding_4_5_modality_v1_seed_19` | data/exp_cross_modal_binding_4_5_modality_v1_seed_19/metrics.json | HARD_PASS | full | 2026-07-01 (metrics.ts_iso) | A (positive_control_cv,positive_control_recall) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M73 | `exp_substrate_cross_modal_binding_3rd_modality_v1_seed_13` | data/exp_substrate_cross_modal_binding_3rd_modality_v1_seed_13/metrics.json | HARD_PASS | full | 2026-07-01 (metrics.ts_iso) | A (positive_control_cv,positive_control_recall) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M74 | `exp_substrate_cross_modal_binding_3rd_modality_v1_seed_19` | data/exp_substrate_cross_modal_binding_3rd_modality_v1_seed_19/metrics.json | HARD_PASS | full | 2026-07-01 (metrics.ts_iso) | A (positive_control_cv,positive_control_recall) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M75 | `exp_object_permanence_binding_stability_v1` | data/exp_object_permanence_binding_stability_v1/metrics.json | HARD_PASS | full | 2026-07-09 (metrics.ts_iso) | A (chance,mean_ratio_iid,mean_rec_naive_iid) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M76 | `exp_parity_in_context_binding_v1` | data/exp_parity_in_context_binding_v1/metrics.json | HARD_PASS_STRUCTURE_DISCRIMINATES | full | 2026-07-19 (metrics.ts_iso) | A (recovery_floor,structure_hard_pass_floor,void_) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1/C2 | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF RD-R54 |
| M77 | `exp_pragmatic_curriculum_dialogue_role_sharded_binding_v1` | data/exp_pragmatic_curriculum_dialogue_role_sharded_binding_v1/metrics.json | HARD_PASS | full | 2026-08-08 (metrics.ts_iso) | A (best_arm_acc,scramble_seed) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M78 | `exp_cortex_regenerative_cleanup_vs_analog_accumulate_v1` | data/exp_cortex_regenerative_cleanup_vs_analog_accumulate_v1/metrics.json | HARD_FAIL | full | 2026-07-05 (metrics.ts_iso) | A (chance_floor,mean_control_d5_at_disc) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:REFUTED |
| M79 | `exp_binding_readcond_encoder_compare_v1` | data/exp_binding_readcond_encoder_compare_v1/metrics.json | SELFTEST_PASS | self_test | 2026-07-30 (metrics.ts_iso) | A (chance) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1/C3/reading | REGISTRY | UNCHECKED | STATE:VERIFIED |
| M80 | `exp_grounding_iterative_settling_cascade_depth_v1` | data/exp_grounding_iterative_settling_cascade_depth_v1/metrics.json | HARD_FAIL_NO_EXTENSION | full | 2026-07-09 (metrics.ts_iso) | A (assort_shuffled) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | state=REFUTED DUP-OF RP-E11 |
| M81 | `exp_substrate_binding_op_x_capacity_v1_seed_7` | data/exp_substrate_binding_op_x_capacity_v1_seed_7/metrics.json | HARD_FAIL | full | 2026-07-01 (metrics.ts_iso) | A (top1_random) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1 | INVISIBLE | UNCHECKED | state=REFUTED DUP-OF RP-E10 |
| M82 | `exp_substrate_binding_op_x_capacity_v1_seed_13` | data/exp_substrate_binding_op_x_capacity_v1_seed_13/metrics.json | HARD_FAIL | full | 2026-07-01 (metrics.ts_iso) | A (top1_random) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1 | INVISIBLE | UNCHECKED | STATE:REFUTED |
| M83 | `exp_substrate_binding_op_x_capacity_v1_seed_19` | data/exp_substrate_binding_op_x_capacity_v1_seed_19/metrics.json | HARD_FAIL | full | 2026-07-01 (metrics.ts_iso) | A (top1_random) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1 | INVISIBLE | UNCHECKED | STATE:REFUTED |
| M84 | `exp_substrate_pc_cleanup_family_phase_diagram_v1_seed_7` | data/exp_substrate_pc_cleanup_family_phase_diagram_v1_seed_7/metrics.json | MIDDLE_BAND | full | 2026-06-29 (metrics.ts_iso) | A (top1_random) | OK | HDLAB:cleanup_family.py | LIVE | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M85 | `exp_grounding_multihop_perhop_cleanup_gate_v1` | data/exp_grounding_multihop_perhop_cleanup_gate_v1/metrics.json | MIDDLE_BAND | full | 2026-07-09 (metrics.ts_iso) | A (cos_floor_c) | OK | HDLAB:multi_hop.py | OFF-PATH | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M86 | `exp_grounding_multihop_generative_replay_traversal_v1` | data/exp_grounding_multihop_generative_replay_traversal_v1/metrics.json | MIDDLE_BAND_CG_TRAVERSAL_PARTIAL | full | 2026-07-22 (metrics.ts_iso) | A (memoryless_reach2,scrambled_reach2) | OK | HDLAB:kg_traversal.py | OFF-PATH | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF RD-R20 |
| M87 | `exp_native_binding_naturalistic_multirelation_v1` | data/exp_native_binding_naturalistic_multirelation_v1/metrics.json | HARD-PASS | full | 2026-07-30 (metrics.ts_iso) | A | OK | HDLAB:multi_hop.py | OFF-PATH | FACTORIAL | C1 | REGISTRY | UNCHECKED | STATE:VERIFIED |
| M88 | `exp_situation_model_assembly_binding_wm_coref_v1` | data/exp_situation_model_assembly_binding_wm_coref_v1/metrics.json | HARD_PASS | full | 2026-07-31 (metrics.ts_iso) | A (chance) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1/C4/reading | REGISTRY | UNCHECKED | state=VERIFIED DUP-OF CG-B85 |
| M89 | `exp_grounding_gated_fusion_relation_inference_mammal_v1` | data/exp_grounding_gated_fusion_relation_inference_mammal_v1/metrics.json | HARD_PASS_GATED_FUSION_RECOVERS_GROUNDING | full | 2026-07-14 (metrics.ts_iso) | A (grounded_only_minus_random,oracle_headroom,ora) | OK | HDLAB:gated_fusion.py | OFF-PATH | -- | C3 | REGISTRY | UNCHECKED | state=VERIFIED DUP-OF RP-D15 |
| M90 | `exp_substrate_concept_encoder_spoke1_v3_D_competitive_hebbian_only_2026_07_02` | data/exp_substrate_concept_encoder_spoke1_v3_D_competitive_hebbian_only_2026_07_02/metrics.json | HARD_PASS | full | 2026-07-02 (metrics.ts_iso) | A (<ARM CONTAINER arm_summary>) | OK | HDLAB:concept_encoder.py | OFF-PATH | -- | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M91 | `exp_substrate_order_binding_family_v2_seed_7` | data/exp_substrate_order_binding_family_v2_seed_7/metrics.json | MIDDLE_BAND | full | 2026-07-01 (metrics.ts_iso) | A (top1_random) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M92 | `exp_substrate_pc_binding_operation_family_phase_diagram_v1_seed_7` | data/exp_substrate_pc_binding_operation_family_phase_diagram_v1_seed_7/metrics.json | MIDDLE_BAND | full | 2026-06-30 (metrics.ts_iso) | A (crlb_bundle_noise_floor,top1_random) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M93 | `exp_substrate_pc_binding_operation_family_phase_diagram_v1_seed_13` | data/exp_substrate_pc_binding_operation_family_phase_diagram_v1_seed_13/metrics.json | MIDDLE_BAND | full | 2026-06-30 (metrics.ts_iso) | A (crlb_bundle_noise_floor,top1_random) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M94 | `exp_substrate_pc_binding_operation_family_phase_diagram_v1_seed_19` | data/exp_substrate_pc_binding_operation_family_phase_diagram_v1_seed_19/metrics.json | MIDDLE_BAND | full | 2026-06-30 (metrics.ts_iso) | A (crlb_bundle_noise_floor,top1_random) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M95 | `exp_visual_grounding_coherence_v1` | data/exp_visual_grounding_coherence_v1/metrics.json | HARD_PASS | full | 2026-07-18 (metrics.ts_iso) | A (<ARM CONTAINER arms>) | OK | EXP-ONLY | OFF-PATH | -- | C3 | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF RP-D12a |
| M96 | `exp_reader_image_word_grounding_v1` | data/exp_reader_image_word_grounding_v1/metrics.json | PASS_GROUNDING | full | 2026-07-22 (metrics.ts_iso) | A (<ARM CONTAINER arm_digests>) | OK | EXP-ONLY | OFF-PATH | -- | C3/reading | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF RP-D12c |
| M97 | `exp_reasoning_storage_4way_cleanup` | data/exp_reasoning_storage_4way_cleanup_v2_smoke/metrics.json | 4WC_HARD_PASS | ABSENT | UNDATED (none) | A (<ARM CONTAINER arm_a_4way>) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M98 | `exp_reasoning_storage_4way_cleanup_v3_hadamard_hopid_v1_n16384` | data/exp_reasoning_storage_4way_cleanup_v3_hadamard_hopid_v1_n16384/metrics.json | 4WC_HARD_PASS | ABSENT | UNDATED (none) | A (<ARM CONTAINER arm_a_4way>) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M99 | `exp_reasoning_storage_4way_cleanup_v2_n16384` | data/exp_reasoning_storage_4way_cleanup_v2_n16384/metrics.json | 4WC_HARD_PASS | ABSENT | UNDATED (none) | A (<ARM CONTAINER arm_a_4way>) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M100 | `exp_substrate_multihop_csp_gated_iterated_cleanup` | data/exp_substrate_multihop_csp_gated_iterated_cleanup_v1_smoke/metrics.json | HARD_PASS_PARTIAL_BARRIER_1_LIFT | smoke | UNDATED (none) | A (baseline_n_chains) | OK | HDLAB:multi_hop.py | OFF-PATH | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M101 | `exp_substrate_cleanup_family_wm_kcliff_v1_seed_7` | data/exp_substrate_cleanup_family_wm_kcliff_v1_seed_7_smoke/metrics.json | HARD_PASS | smoke | 2026-06-30 (metrics.ts_iso) | A (FLOOR) | OK | HDLAB:cleanup_family.py | LIVE | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M102 | `exp_substrate_cleanup_family_wm_kcliff_v1_seed_13` | data/exp_substrate_cleanup_family_wm_kcliff_v1_seed_13_smoke/metrics.json | HARD_PASS | smoke | 2026-06-30 (metrics.ts_iso) | A (FLOOR) | OK | HDLAB:cleanup_family.py | LIVE | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M103 | `exp_substrate_cleanup_family_wm_kcliff_v1p1_seed_7` | data/exp_substrate_cleanup_family_wm_kcliff_v1p1_seed_7_smoke/metrics.json | HARD_PASS | smoke | 2026-06-30 (metrics.ts_iso) | A (FLOOR) | OK | HDLAB:cleanup_family.py | LIVE | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M104 | `exp_substrate_cleanup_family_wm_kcliff_v1p1_seed_13` | data/exp_substrate_cleanup_family_wm_kcliff_v1p1_seed_13_smoke/metrics.json | HARD_PASS | smoke | 2026-06-30 (metrics.ts_iso) | A (FLOOR) | OK | HDLAB:cleanup_family.py | LIVE | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M105 | `exp_substrate_cleanup_family_wm_kcliff_v1p1_seed_19` | data/exp_substrate_cleanup_family_wm_kcliff_v1p1_seed_19_smoke/metrics.json | HARD_PASS | smoke | 2026-06-30 (metrics.ts_iso) | A (FLOOR) | OK | HDLAB:cleanup_family.py | LIVE | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M106 | `exp_stage1_regime_probe_13_L_x_cleanup_non_saturated_v1_s7_smoke` | data/exp_stage1_regime_probe_13_L_x_cleanup_non_saturated_v1_s7_smoke_smoke/metrics.json | HARD_PASS | smoke | 2026-07-03 (metrics.ts_iso) | A (h3_null_threshold) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M107 | `exp_cortex_regenerative_cleanup_vs_analog_accumulate` | data/exp_cortex_regenerative_cleanup_vs_analog_accumulate_v1_smoke/metrics.json | HARD_PASS | smoke | 2026-07-05 (metrics.ts_iso) | A (chance_floor,mean_control_d5_at_disc) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M108 | `exp_cleanup_floor_learned_encoder_v1` | data/exp_cleanup_floor_learned_encoder_v1/metrics.json | META_BRANCH3_CHAIN_GRADE_ELIGIBLE | full | UNDATED (none) | A (recall_random_disc) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | C3 | REGISTRY | UNCHECKED | state=VERIFIED DUP-OF RP-D18 |
| M109 | `exp_substrate_resonator_softchain_beta_sweep` | data/exp_substrate_resonator_softchain_beta_sweep_v1_smoke/metrics.json | HARD_PASS | smoke | UNDATED (none) | A (<ARM CONTAINER ARM_BASELINE_HARD>) | OK | EXP-ONLY | OFF-PATH | FACTORIAL | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M110 | `exp_resonator_glauber_plurality` | data/exp_resonator_glauber_plurality_v1_smoke/metrics.json | HARD_PASS | smoke | UNDATED (none) | A (<ARM CONTAINER by_arm>) | OK | EXP-ONLY | OFF-PATH | FACTORIAL | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M111 | `exp_resonator_theta_gamma_peel` | data/exp_resonator_theta_gamma_peel_v1_smoke/metrics.json | HARD_PASS | smoke | UNDATED (none) | A (<ARM CONTAINER by_arm>) | OK | EXP-ONLY | OFF-PATH | FACTORIAL | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M112 | `exp_resonator_deflation_lowsnr` | data/exp_resonator_deflation_lowsnr_v1_smoke/metrics.json | HARD_PASS | smoke | UNDATED (none) | A (<ARM CONTAINER by_arm>) | OK | EXP-ONLY | OFF-PATH | FACTORIAL | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M113 | `exp_substrate_seqbind_binding_operation_family_phase_diagram_v2_seed_7` | data/exp_substrate_seqbind_binding_operation_family_phase_diagram_v2_seed_7/metrics.json | HARD_PASS | smoke | 2026-06-30 (metrics.ts_iso) | A (top1_random) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M114 | `exp_interference_avoidance_conjunctive_vs_additive` | data/exp_interference_avoidance_conjunctive_vs_additive_v1_smoke/metrics.json | HARD_PASS | smoke | UNDATED (none) | A (hf_control_confound,hf_gap_orth_freq_max,hp_co) | OK | HDLAB:additive_map.py | OFF-PATH | FACTORIAL | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M115 | `exp_substrate_knowledge_promotion_p4_replay_consolidation_cpu_v1` | data/exp_substrate_knowledge_promotion_p4_replay_consolidation_cpu_v1/metrics.json | HARD_PASS | full | UNDATED (none) | A (random_pair_mean,random_pair_p99,random_pair_s) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M116 | `exp_c3_compressed_sequence_replay_v1_timing` | data/exp_c3_compressed_sequence_replay_v1_timing/metrics.json | HARD_PASS | full | UNDATED (none) | A (W_norm_before_sleep) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M117 | `exp_substrate_continual_NREM_replay_v1` | data/exp_substrate_continual_NREM_replay_v1/metrics.json | HARD_PASS | full | UNDATED (none) | A (baseline_cliff_cycle,baseline_curve_max_forget) | OK | HDLAB:continual.py | OFF-PATH | CONTRACTIVE | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M118 | `exp_course_c_operator_fix_ssp_phase_rotation_replay_v1` | data/exp_course_c_operator_fix_ssp_phase_rotation_replay_v1/metrics.json | OPERATOR_FIX_CONFIRMED_CONSOLIDATION_INCONCLUSIVE | full | 2026-07-11 (metrics.ts_iso) | A (achieved_over_ceiling,flat_gap,freq_manufactur) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | -- | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF RP-E4 |
| M119 | `exp_consol_interleaved_replay_v1` | data/exp_consol_interleaved_replay_v1/metrics.json | HARD_PASS | full | 2026-07-15 (metrics.ts_iso) | A (oracle_ceiling,pop,pop_gap) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | -- | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF RP-E3 |
| M120 | `exp_substrate_multihop_consolidation_memory_v1` | data/exp_substrate_multihop_consolidation_memory_v1/metrics.json | HARD_PASS | full | UNDATED (none) | A (<ARM CONTAINER arm_naive>) | OK | HDLAB:multi_hop.py | OFF-PATH | CONTRACTIVE | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M121 | `exp_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_13_GPU` | data/exp_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_13_GPU/metrics.json | HARD_PASS | full | 2026-06-28 (metrics.ts_iso) | A (top1_random) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M122 | `exp_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_19_GPU` | data/exp_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_19_GPU/metrics.json | HARD_PASS | full | 2026-06-28 (metrics.ts_iso) | A (top1_random) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M123 | `exp_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_7_GPU` | data/exp_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_7_GPU/metrics.json | HARD_PASS | full | 2026-06-28 (metrics.ts_iso) | A (top1_random) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M124 | `exp_substrate_tier4_hopfield_attention_substitution_llama_3_2_1b_v1` | data/exp_substrate_tier4_hopfield_attention_substitution_llama_3_2_1b_v1/metrics.json | HARD_PASS | full | UNDATED (none) | A (baseline_ppl,baseline_wall) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M125 | `exp_substrate_tier4_hopfield_attention_substitution_pythia160m_v1` | data/exp_substrate_tier4_hopfield_attention_substitution_pythia160m_v1/metrics.json | HARD_PASS | full | UNDATED (none) | A (baseline_ppl) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | -- | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF RP-D2 |
| M126 | `exp_fuzzy_shard_router_attractor_stage12_v1` | data/exp_fuzzy_shard_router_attractor_stage12_v1/metrics.json | HARD_PASS | full | 2026-07-17 (metrics.ts_iso) | A (k_naive) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M127 | `exp_grounding_multiattribute_fusion_v1` | data/exp_grounding_multiattribute_fusion_v1/metrics.json | MIDDLE_BAND_PARTIAL | full | 2026-07-10 (metrics.ts_iso) | A (fusion_beats_single,scrambled_gap) | OK | HDLAB:multi_hop.py | OFF-PATH | -- | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M128 | `exp_reasoning_storage_4way_cleanup_v1_n16384` | data/exp_reasoning_storage_4way_cleanup_v1_n16384/metrics.json | 4WC_HARD_PASS | ABSENT | UNDATED (none) | A (<ARM CONTAINER arm_a_4way>) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M129 | `exp_pc_cleanup_attractor_v1` | data/exp_pc_cleanup_attractor_v1/metrics.json | HARD_PASS | full | UNDATED (none) | NO FLOOR | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:FOUND |
| M130 | `exp_substrate_iterative_cleanup_cue_clamped_v1` | data/exp_substrate_iterative_cleanup_cue_clamped_v1/metrics.json | HARD_PASS | ABSENT | UNDATED (none) | ARM (acc_single_step) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF RP-A8 |
| M131 | `exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup` | data/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1_smoke/metrics.json | HARD_PASS | smoke | UNDATED (none) | A (<ARM CONTAINER by_arm_agg>) | OK | HDLAB:harness.py | OFF-PATH | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M132 | `exp_dense_hopfield_readout_capacity_correlated_codes` | data/exp_dense_hopfield_readout_capacity_correlated_codes_v1_smoke/metrics.json | HARD_PASS | smoke | 2026-07-14 (metrics.ts_iso) | A (pos_control_iid_lift) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | C1/C3/reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M133 | `exp_resonator_decision_compgen_2factor` | data/exp_resonator_decision_compgen_2factor_v1_smoke/metrics.json | HARD_PASS | smoke | 2026-07-21 (metrics.ts_iso) | A (chance) | OK | EXP-ONLY | OFF-PATH | FACTORIAL | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M134 | `exp_c3_compressed_sequence_replay_v1` | data/exp_c3_compressed_sequence_replay_v1/metrics.json | HARD_PASS | full | UNDATED (none) | A (W_norm_before_sleep) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | -- | ORGAN_MAP | UNCHECKED | STATE:VERIFIED |
| M135 | `exp_cls_interleaved_replay_consolidation_pilot_v1` | data/exp_cls_interleaved_replay_consolidation_pilot_v1/metrics.json | HARD_PASS | full | UNDATED (none) | A (<ARM CONTAINER arm_digests>) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | -- | ORGAN_MAP | UNCHECKED | STATE:VERIFIED |
| M136 | `exp_cls_ca3complete_consolidation_v1` | data/exp_cls_ca3complete_consolidation_v1/metrics.json | HARD_PASS | full | UNDATED (none) | A (gap_full_minus_naive_old) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | -- | REGISTRY | UNCHECKED | STATE:VERIFIED |
| M137 | `exp_ingest_gate_consolidation_loop_pilot_v1` | data/exp_ingest_gate_consolidation_loop_pilot_v1/metrics.json | HARD_PASS | full | 2026-07-16 (metrics.ts_iso) | A (ablation_auc,ablation_partial_perm_p,ablation_) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | -- | REGISTRY | UNCHECKED | STATE:VERIFIED |
| M138 | `exp_e3b_permutation_binding_endtask_cpu_v1` | data/exp_e3b_permutation_binding_endtask_cpu_v1/metrics.json | HARD_PASS | full | UNDATED (none) | NO FLOOR | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1 | INVISIBLE | UNCHECKED | STATE:FOUND |
| M139 | `exp_contextual_encoding_hrr_binding_smoke_v1_smoketest` | data/exp_contextual_encoding_hrr_binding_smoke_v1_smoketest/metrics.json | HARD_PASS | smoke | UNDATED (none) | ARM (<ARM CONTAINER by_arm_agg>) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1/C2 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M140 | `exp_substrate_permutation_binding_multiocc_v2` | data/exp_substrate_permutation_binding_multiocc_v2_full/metrics.json | HARD_PASS | full | UNDATED (none) | NO FLOOR | OK | HDLAB:multi_hop.py | OFF-PATH | FACTORIAL | C1 | INVISIBLE | UNCHECKED | state=FOUND DUP-OF CG-B14 |
| M141 | `exp_cross_modal_binding_4_5_modality_v1_seed_7_smoke` | data/exp_cross_modal_binding_4_5_modality_v1_seed_7_smoke_smoke/metrics.json | HARD_PASS | smoke | 2026-07-01 (metrics.ts_iso) | A (positive_control_cv,positive_control_recall) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M142 | `exp_object_permanence_binding_stability` | data/exp_object_permanence_binding_stability_v1_smoke/metrics.json | HARD_PASS | smoke | 2026-07-09 (metrics.ts_iso) | A (chance,mean_ratio_iid,mean_rec_naive_iid) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M143 | `exp_parity_in_context_binding` | data/exp_parity_in_context_binding_v1_smoke/metrics.json | HARD_PASS_STRUCTURE_DISCRIMINATES | smoke | 2026-07-19 (metrics.ts_iso) | A (recovery_floor,structure_hard_pass_floor,void_) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1/C2 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M144 | `exp_consolidation_correct_regimes_v1` | data/exp_consolidation_correct_regimes_v1/metrics.json | HARD_PASS | full | 2026-07-16 (metrics.ts_iso) | A (margin_hold_vs_flat) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | -- | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF CG-B6 |
| M145 | `exp_consolidated_reader_chaingrade_demo_v1` | data/exp_consolidated_reader_chaingrade_demo_v1/metrics.json | CHAIN_GRADE_DEMONSTRATED | full | 2026-07-23 (metrics.ts_iso) | A (<ARM CONTAINER arm_a_reader>) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | reading | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF RP-C2 |
| M146 | `exp_consolidated_reader_hardsyntax_heldout_v1` | data/exp_consolidated_reader_hardsyntax_heldout_v1/metrics.json | CHAIN_GRADE_HARDSYNTAX_EARNED | full | 2026-07-23 (metrics.ts_iso) | A (n_naive_correct,naive_acc) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | reading | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF RP-C4 |
| M147 | `exp_consolidated_reader_passive_mechanism_heldout_v1` | data/exp_consolidated_reader_passive_mechanism_heldout_v1/metrics.json | PASSIVE_MECHANISM_CAPABILITY_EARNED | full | 2026-07-24 (metrics.ts_iso) | A (n_naive,n_reader_off,naive_acc) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | reading | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF RP-C1 |
| M148 | `exp_cross_span_causal_binding_v1` | data/exp_cross_span_causal_binding_v1/metrics.json | CROSS_SPAN_BINDING_LIFTS_RECALL_AND_SELECTION | full | 2026-08-04 (metrics.ts_iso) | A (<ARM CONTAINER arm_digests>) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1 | REGISTRY | UNCHECKED | STATE:VERIFIED |
| M149 | `exp_sr_additive_score_fusion_cskg_v1` | data/exp_sr_additive_score_fusion_cskg_v1/metrics.json | HARD_PASS_SR_ADDITIVE_FUSION | full | 2026-07-14 (metrics.ts_iso) | A (<ARM CONTAINER must_fail_arm_mrr>) | OK | HDLAB:additive_map.py | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M150 | `exp_substrate_narrative_q2_coref_lappin_leass_drill2_v1_seed_7` | data/exp_substrate_narrative_q2_coref_lappin_leass_drill2_v1_seed_7/metrics.json | HARD_PASS | full | UNDATED (none) | A (<ARM CONTAINER per_arm>) | OK | EXP-ONLY | OFF-PATH | -- | C4/reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M151 | `exp_substrate_narrative_q2_coref_lappin_leass_drill2_v1_seed_13` | data/exp_substrate_narrative_q2_coref_lappin_leass_drill2_v1_seed_13/metrics.json | HARD_PASS | full | UNDATED (none) | A (<ARM CONTAINER per_arm>) | OK | EXP-ONLY | OFF-PATH | -- | C4/reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M152 | `exp_vision_integrated_recognize_bind_ground_v1` | data/exp_vision_integrated_recognize_bind_ground_v1/metrics.json | HARD_PASS_INTEGRATED_PIPELINE__NOVEL_CLASS_WALL_CONFIRMED | full | 2026-07-23 (metrics.ts_iso) | A (flat_ill,ground_raw) | OK | EXP-ONLY | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF RP-D12b |
| M153 | `exp_consol_conjunction_replay_v1` | data/exp_consol_conjunction_replay_v1/metrics.json | REFUTE_CONSOLIDATION_NO_SCHEDULE_ADVANTAGE_CONJUNCTION_IS_READOUT_EFFECT | full | 2026-07-15 (metrics.ts_iso) | A (chance,oracle_headroom,readout_beats_freq) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | -- | INVISIBLE | UNCHECKED | state=REFUTED DUP-OF RP-E1 |
| M154 | `exp_consol_inductive_entity_replay_cskg_v1` | data/exp_consol_inductive_entity_replay_cskg_v1/metrics.json | REFUTE_REPLAY_NO_INDUCTIVE_ADVANTAGE | full | 2026-07-15 (metrics.ts_iso) | A (beat_pop,oracle_headroom,oracle_ratio) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | C4 | INVISIBLE | UNCHECKED | state=REFUTED DUP-OF RP-E2 |
| M155 | `exp_compgen_binding_vs_flat_learned_frontend` | data/exp_compgen_binding_vs_flat_learned_frontend_v1_smoke/metrics.json | HARD_PASS | JUNK(exp_compgen_binding_vs) | 2026-07-20 (metrics.ts_iso) | A (<ARM CONTAINER arm_by_size>) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1 | REGISTRY | UNCHECKED | STATE:VERIFIED |
| M156 | `exp_compgen_binding_vs_flat_learned_frontend_v1` | data/exp_compgen_binding_vs_flat_learned_frontend_v1/metrics.json | HARD_PASS | JUNK(exp_compgen_binding_vs) | 2026-07-20 (metrics.ts_iso) | A (<ARM CONTAINER arm_by_size>) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1 | REGISTRY | UNCHECKED | state=VERIFIED DUP-OF RD-R70 |
| M157 | `exp_bootstrap_passage_context_binding_fade_v4` | data/exp_bootstrap_passage_context_binding_fade_v4/metrics.json | PENDING_PASSAGE_TAG_HANDCHECK | JUNK(bootstrap_passage) | UNDATED (none) | A (<ARM CONTAINER arms>) | OK | HDLAB:binding.py | LIVE | FACTORIAL | C1/C2/reading | REGISTRY | UNCHECKED | STATE:VERIFIED |
| M158 | `exp_grounding_gated_fusion_relation_inference_mammal` | data/exp_grounding_gated_fusion_relation_inference_mammal_v1_smoke/metrics.json | HARD_PASS_GATED_FUSION_RECOVERS_GROUNDING | smoke | 2026-07-14 (metrics.ts_iso) | A (grounded_only_minus_random,oracle_headroom,ora) | OK | HDLAB:gated_fusion.py | OFF-PATH | -- | C3 | REGISTRY | UNCHECKED | STATE:VERIFIED |
| M159 | `exp_coref_encoder_transfer_v1` | data/exp_coref_encoder_transfer_v1/metrics.json | HARD_PASS | lite | 2026-08-01 (metrics.ts_iso) | A (stage_ent_frozen,tier1_abs_frozen,tier1_delta_) | OK | EXP-ONLY | OFF-PATH | -- | C3/C4/reading | REGISTRY | UNCHECKED | STATE:VERIFIED |
| M160 | `exp_situation_model_assembly_encoder_retrain_scale_v1` | data/exp_situation_model_assembly_encoder_retrain_scale_v1/metrics.json | CLEAN_PASS | grid | 2026-07-31 (metrics.ts_iso) | A (chance) | OK | EXP-ONLY | OFF-PATH | -- | C3 | REGISTRY | UNCHECKED | state=VERIFIED DUP-OF RP-C9 |
| M161 | `exp_curriculum_prerequisite_scaffold_consolidation_v1` | data/exp_curriculum_prerequisite_scaffold_consolidation_v1/metrics.json | HARD_PASS_curriculum_prerequisite_scaffold_consolidation | full | 2026-08-12 (metrics.ts_iso) | A (<ARM CONTAINER property_frac_by_arm>) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | -- | REGISTRY | UNCHECKED | STATE:VERIFIED |
| M162 | `exp_visual_grounding_coherence` | data/exp_visual_grounding_coherence_v1_smoke/metrics.json | HARD_PASS | smoke | 2026-07-18 (metrics.ts_iso) | A (<ARM CONTAINER arms>) | OK | EXP-ONLY | OFF-PATH | -- | C3 | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M163 | `exp_substrate_gen_lm_replay_propose_score_commit_v11_unique_path_n8192_gpu` | data/exp_substrate_gen_lm_replay_propose_score_commit_v11_unique_path_n8192_gpu/metrics.json | MIDDLE_BAND | full | UNDATED (none) | A (chance) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M164 | `exp_cls_distributed_protection_heldout_replay_v1` | data/exp_cls_distributed_protection_heldout_replay_v1/metrics.json | HARD_PASS | full | UNDATED (none) | ARM (<ARM CONTAINER arm_digests>) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M165 | `exp_cls_ca3complete_significance_v1` | data/exp_cls_ca3complete_significance_v1/metrics.json | HARD_PASS | full | UNDATED (none) | A (<ARM CONTAINER per_arm>) | OK | EXP-ONLY | OFF-PATH | -- | -- | REGISTRY | UNCHECKED | STATE:VERIFIED |
| M166 | `exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1` | data/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1/metrics.json | HARD_PASS | full | UNDATED (none) | A (fair_harness_hebbian_baseline_bpc,hebbian_bpc,) | OK | HDLAB:harness.py | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF RP-D8 |
| M167 | `exp_cleanup_floor_learned_encoder` | data/exp_cleanup_floor_learned_encoder_v1_smoke/metrics.json | META_BRANCH3_CHAIN_GRADE_ELIGIBLE | smoke | UNDATED (none) | A (recall_random_disc) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | C3 | REGISTRY | UNCHECKED | STATE:VERIFIED |
| M168 | `exp_read_xsent_coref_scene_protagonist_v1` | data/exp_read_xsent_coref_scene_protagonist_v1/metrics.json | HARD_PASS | full | 2026-07-24 (metrics.ts_iso) | A (no_overall_regress_eps) | OK | EXP-ONLY | OFF-PATH | -- | C4/reading | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF RP-C5 |
| M169 | `exp_counterfactual_regret_comparison_vmpfc_v1` | data/exp_counterfactual_regret_comparison_vmpfc_v1/metrics.json | HARD_PASS | full | 2026-06-28 (metrics.ts_iso) | A (R2_baseline,R2_oracle,R2_random_vectors) | OK | EXP-ONLY | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF CG-B15 |
| M170 | `exp_pfc_gate_branching_depth_entropy_grid_v1` | data/exp_pfc_gate_branching_depth_entropy_grid_v1/metrics.json | HARD_PASS | full | 2026-07-06 (metrics.ts_iso) | A (focus_flat_gonogo,spearman_flat_vs_depth,spear) | OK | EXP-ONLY | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M171 | `exp_counterfactual_replay_latency_delta_stack_v2_single_intervention` | data/exp_counterfactual_replay_latency_delta_stack_v2_single_intervention/metrics.json | HARD_PASS | smoke | UNDATED (none) | A (parent_baseline_intervention_ms_MEASURED) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M172 | `exp_wave14c_r7_surprise_closedloop_replay` | data/exp_wave14c_r7_surprise_closedloop_replay_v1_smoke/metrics.json | SMOKE_GATE_PASS | smoke | 2026-07-18 (metrics.ts_iso) | A (mean_delta_cl_vs_random,mean_delta_static_vs_r) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M173 | `exp_substrate_pattern_completion_corruption_cliff_phase_diagram` | data/exp_substrate_pattern_completion_corruption_cliff_phase_diagram_v1_smoke/metrics.json | HARD_PASS | smoke | UNDATED (none) | A (top1_random) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M174 | `exp_fuzzy_shard_router_attractor_stage12` | data/exp_fuzzy_shard_router_attractor_stage12_v1_smoke/metrics.json | HARD_PASS | smoke | 2026-07-17 (metrics.ts_iso) | A (k_naive) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M175 | `exp_pc_cleanup_attractor` | data/exp_pc_cleanup_attractor_v1_smoke/metrics.json | HARD_PASS | smoke | UNDATED (none) | NO FLOOR | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:FOUND |
| M176 | `exp_cortex_iterative_attractor_cleanup_depth_ceiling_v1` | data/exp_cortex_iterative_attractor_cleanup_depth_ceiling_v1_selftest/metrics.json | HARD_PASS | self_test | 2026-07-05 (metrics.ts_iso) | NO FLOOR | OK | HDLAB:iterative_attractor.py | LIVE | CONTRACTIVE | C3 | INVISIBLE | UNCHECKED | STATE:FOUND |
| M177 | `exp_consolidated_reader_chaingrade_FULL_v1` | data/exp_consolidated_reader_chaingrade_FULL_v1/metrics.json | CHAIN_GRADE_HELDOUT_PARTIAL | full | 2026-07-23 (metrics.ts_iso) | A (base_f1,base_rc) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | reading | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF RP-C3 |
| M178 | `exp_cls_read_sleep_foundation_acquire_v1` | data/exp_cls_read_sleep_foundation_acquire_v1/metrics.json | HARD_PASS | full | UNDATED (none) | A (n_control) | OK | EXP-ONLY | OFF-PATH | -- | reading | REGISTRY | UNCHECKED | STATE:VERIFIED |
| M179 | `exp_base_reader_grounded_relations_coref_v1` | data/exp_base_reader_grounded_relations_coref_v1/metrics.json | HARD_PASS | full | 2026-07-18 (metrics.ts_iso) | A (<ARM CONTAINER arms>) | OK | EXP-ONLY | OFF-PATH | -- | C4/reading | REGISTRY | UNCHECKED | state=VERIFIED DUP-OF RD-R53 |
| M180 | `exp_coref_salience_rank_topicality_v1` | data/exp_coref_salience_rank_topicality_v1/metrics.json | HARD_PASS_SALIENCE_RANK_CONFIRMED | full | 2026-07-18 (metrics.ts_iso) | A (<ARM CONTAINER arms>) | OK | EXP-ONLY | OFF-PATH | -- | C4/reading | REGISTRY | UNCHECKED | STATE:VERIFIED |
| M181 | `exp_read_xsent_coref_distractor_suppress_v1` | data/exp_read_xsent_coref_distractor_suppress_v1/metrics.json | HARD_PASS | full | 2026-07-24 (metrics.ts_iso) | A (base_acc_xsent) | OK | HDLAB:coref_distractor_suppress.py | OFF-PATH | -- | C4/reading | REGISTRY | UNCHECKED | state=VERIFIED DUP-OF RD-R55 |
| M182 | `exp_pfc_gate_cfrpe_trained_v2` | data/exp_pfc_gate_cfrpe_trained_v2/metrics.json | HARD_PASS | full | 2026-07-05 (metrics.ts_iso) | A (control_identity,oracle,v1_no_goal) | OK | EXP-ONLY | OFF-PATH | -- | -- | REGISTRY | UNCHECKED | STATE:VERIFIED |
| M183 | `exp_pfc_bg_composed_attention_value_gate_v1` | data/exp_pfc_bg_composed_attention_value_gate_v1/metrics.json | HARD_PASS | full | 2026-07-08 (metrics.ts_iso) | A (focus_scramble_gap) | OK | EXP-ONLY | OFF-PATH | -- | -- | REGISTRY | UNCHECKED | STATE:VERIFIED |
| M184 | `exp_situation_model_accumulate_vs_overwrite_v1` | data/exp_situation_model_accumulate_vs_overwrite_v1/metrics.json | HARD_PASS | full | 2026-08-02 (metrics.ts_iso) | A (chance) | OK | HDLAB:situation_model_accumulate.py | LIVE | -- | -- | REGISTRY | UNCHECKED | STATE:VERIFIED |
| M185 | `exp_situation_model_relation_ablation_v1` | data/exp_situation_model_relation_ablation_v1/metrics.json | HARD_PASS | full | UNDATED (none) | A (memorization_baseline_acc,scramble_control_acc) | OK | HDLAB:ablation.py | LIVE | -- | -- | REGISTRY | UNCHECKED | STATE:VERIFIED |
| M186 | `exp_information_foraging_reading_v1` | data/exp_information_foraging_reading_v1/metrics.json | HARD_PASS | full | 2026-08-14 (metrics.ts_iso) | A (<ARM CONTAINER arms>) | OK | HDLAB:information_foraging.py | OFF-PATH | -- | reading | STRATEGY,REGISTRY | UNCHECKED | STATE:VERIFIED |
| M187 | `exp_c3_compressed_sequence_replay` | data/exp_c3_compressed_sequence_replay_v1_smoke/metrics.json | HARD_PASS | smoke | UNDATED (none) | A (W_norm_before_sleep) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | -- | ORGAN_MAP | UNCHECKED | STATE:VERIFIED |
| M188 | `exp_cls_interleaved_replay_consolidation_pilot` | data/exp_cls_interleaved_replay_consolidation_pilot_v1_smoke/metrics.json | HARD_PASS | smoke | UNDATED (none) | A (<ARM CONTAINER arm_digests>) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | -- | ORGAN_MAP | UNCHECKED | STATE:VERIFIED |
| M189 | `exp_cls_ca3complete_consolidation` | data/exp_cls_ca3complete_consolidation_v1_smoke/metrics.json | HARD_PASS | smoke | UNDATED (none) | A (gap_full_minus_naive_old) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | -- | REGISTRY | UNCHECKED | STATE:VERIFIED |
| M190 | `exp_e3_permutation_binding_multiocc_cpu_v1` | data/exp_e3_permutation_binding_multiocc_cpu_v1/metrics.json | HARD_PASS | smoke | UNDATED (none) | NO FLOOR | OK | HDLAB:multi_hop.py | OFF-PATH | FACTORIAL | C1 | INVISIBLE | UNCHECKED | STATE:FOUND |
| M191 | `exp_e3_permutation_binding_multiocc_cpu` | data/exp_e3_permutation_binding_multiocc_cpu_v1_smoke/metrics.json | HARD_PASS | smoke | UNDATED (none) | NO FLOOR | OK | HDLAB:multi_hop.py | OFF-PATH | FACTORIAL | C1 | INVISIBLE | UNCHECKED | STATE:FOUND |
| M192 | `exp_substrate_permutation_binding_multiocc_v2_full` | data/exp_substrate_permutation_binding_multiocc_v2_full_smoke/metrics.json | HARD_PASS | smoke | UNDATED (none) | NO FLOOR | OK | HDLAB:multi_hop.py | OFF-PATH | FACTORIAL | C1 | INVISIBLE | UNCHECKED | STATE:FOUND |
| M193 | `exp_lap2_9_predictive_coding_cpu_v1` | data/exp_lap2_9_predictive_coding_cpu_v1/metrics.json | HARD_PASS | full | UNDATED (none) | PROSE (baseline) | OK | HDLAB:predictive_coding.py | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M194 | `exp_wave14_betB_ablation_B_replay_sweep` | data/exp_wave14_betB_ablation_B_replay_sweep_v1_smoke/metrics.json | ABLATION_B_HARD_PASS | ABSENT | UNDATED (none) | A (bpc_A_baseline,bpc_B_baseline,retention_A) | OK | HDLAB:ablation.py | LIVE | CONTRACTIVE | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M195 | `exp_wave14_betB_replay_by_norm` | data/exp_wave14_betB_replay_by_norm_v1_smoke/metrics.json | REPLAY_NORM_HARD_PASS | ABSENT | UNDATED (none) | A (bpc_A_baseline,retention_A) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M196 | `exp_wave14_k2_m1_hierreplay` | data/exp_wave14_k2_m1_hierreplay_v1_smoke/metrics.json | K2_M1_HARD_PASS | ABSENT | UNDATED (none) | A (bpc_A_baseline,bpc_B_baseline,bpc_C_baseline) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M197 | `exp_wave14d_multi_task_cl_v10_lowreplay` | data/exp_wave14d_multi_task_cl_v10_lowreplay/metrics.json | BET_B_PASS | ABSENT | UNDATED (none) | A (bpc_A_baseline,bpc_B_baseline,retention_A) | OK | HDLAB:multi_hop.py | OFF-PATH | CONTRACTIVE | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M198 | `exp_wave14_betB_4stage_continual_v2_rehab_phaseA_consolidation` | data/exp_wave14_betB_4stage_continual_v2_rehab_phaseA_consolidation_v1_smoke/metrics.json | FOURSTAGE_HARD_PASS | ABSENT | UNDATED (none) | A (bpc_A_baseline,bpc_B_baseline,bpc_C_baseline) | OK | HDLAB:continual.py | OFF-PATH | CONTRACTIVE | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M199 | `exp_modern_hopfield_pipeline_validation_v1_n2048_n4096` | data/exp_modern_hopfield_pipeline_validation_v1_n2048_n4096/metrics.json | PIPELINE_HARD_PASS | ABSENT | UNDATED (none) | A (n_non_null) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M200 | `exp_substrate_pcgrad_cfrpe_stdp_v2_RESCUE` | data/exp_substrate_pcgrad_cfrpe_stdp_v2_RESCUE/metrics.json | HARD_FAIL | full | UNDATED (none) | A (<ARM CONTAINER by_arm_agg>) | OK | EXP-ONLY | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | state=REFUTED DUP-OF RP-E12 |
| M201 | `exp_substrate_narrative_q2_coref_lappin_leass_drill2` | data/exp_substrate_narrative_q2_coref_lappin_leass_drill2_v1_smoke/metrics.json | HARD_PASS | smoke | UNDATED (none) | A (<ARM CONTAINER per_arm>) | OK | EXP-ONLY | OFF-PATH | -- | C4/reading | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M202 | `exp_substrate_multihop_pfc_chunked_2hop_decomposition` | data/exp_substrate_multihop_pfc_chunked_2hop_decomposition_v1_smoke/metrics.json | HARD_PASS_CHAIN_GRADE_BARRIER_1_VIA_CHUNKING | smoke | UNDATED (none) | A (baseline_n_chains) | OK | HDLAB:multi_hop.py | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF RP-D7 |
| M203 | `exp_substrate_concept_encoder_spoke1_predictive_coding_competitive_allocation` | data/exp_substrate_concept_encoder_spoke1_predictive_coding_competitive_allocation_v1_smoke/metrics.json | HARD_FAIL | smoke | 2026-07-02 (metrics.ts_iso) | A (<ARM CONTAINER arm_summary>) | OK | HDLAB:predictive_coding.py | OFF-PATH | -- | C3 | REGISTRY | UNCHECKED | STATE:REFUTED |
| M204 | `exp_ingest_gate_compositional_surprise_deconf_v1` | data/exp_ingest_gate_compositional_surprise_deconf_v1/metrics.json | INCONCLUSIVE_harness | full | 2026-07-16 (metrics.ts_iso) | A (frac_heldout_base) | OK | EXP-ONLY | OFF-PATH | -- | -- | REGISTRY | UNCHECKED | STATE:VERIFIED |
| M205 | `exp_ingest_gate_compositional_surprise_deconf_v2` | data/exp_ingest_gate_compositional_surprise_deconf_v2/metrics.json | MIDDLE_BAND_partial | full | 2026-07-16 (metrics.ts_iso) | A (frac_heldout_base,pooled_min_class_floor) | OK | EXP-ONLY | OFF-PATH | -- | -- | REGISTRY | UNCHECKED | STATE:VERIFIED |
| M206 | `exp_curriculum_prerequisite_scaffold_consolidation` | data/exp_curriculum_prerequisite_scaffold_consolidation_v1_smoke/metrics.json | HARD_PASS_curriculum_prerequisite_scaffold_consolidation | smoke | 2026-08-12 (metrics.ts_iso) | A (<ARM CONTAINER property_frac_by_arm>) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | -- | REGISTRY | UNCHECKED | STATE:VERIFIED |
| M207 | `exp_cls_distributed_protection_heldout_replay` | data/exp_cls_distributed_protection_heldout_replay_v1_smoke/metrics.json | HARD_PASS | smoke | UNDATED (none) | ARM (<ARM CONTAINER arm_digests>) | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M208 | `exp_substrate_pcgrad_cfrpe_stdp` | data/exp_substrate_pcgrad_cfrpe_stdp_v1_smoke/metrics.json | HARD_PASS | smoke | UNDATED (none) | A (<ARM CONTAINER by_arm_agg>) | OK | EXP-ONLY | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M209 | `exp_hippocampal_sharp_wave_ripple_v1` | data/exp_hippocampal_sharp_wave_ripple_v1/metrics.json | HARD_PASS | smoke | UNDATED (none) | A (mean_fidelity_random) | OK | EXP-ONLY | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF RP-D4 |
| M210 | `exp_wave14_saddle_cascade_plateau_v2` | data/exp_wave14_saddle_cascade_plateau_v2/metrics.json | CASCADE_HARD_PASS | ABSENT | UNDATED (none) | A (bpc_A_baseline,retention_A) | OK | EXP-ONLY | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M211 | `exp_wave14_saddle_cascade_plateau_v3` | data/exp_wave14_saddle_cascade_plateau_v3/metrics.json | CASCADE_HARD_PASS | ABSENT | UNDATED (none) | A (bpc_A_baseline,retention_A) | OK | EXP-ONLY | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M212 | `exp_d2_7_intentional_forgetting_cpu_v1` | data/exp_d2_7_intentional_forgetting_cpu_v1/metrics.json | HARD_PASS | full | UNDATED (none) | NO FLOOR | OK | EXP-ONLY | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | STATE:FOUND |
| M213 | `exp_multi_competency_coref_ablation_v1` | data/exp_multi_competency_coref_ablation_v1/metrics.json | HARD_PASS | smoke | 2026-07-31 (metrics.ts_iso) | A (tier1_delta_present_ablated) | OK | HDLAB:multi_hop.py | OFF-PATH | -- | C4/reading | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF RD-R129 |
| M214 | `exp_coref_self_confidence_calibration_v1` | data/exp_coref_self_confidence_calibration_v1/metrics.json | HARD_PASS_CALIBRATED_NAME_PATH | ABSENT | 2026-08-02 (metrics.ts_iso) | A (base_error_rate) | OK | EXP-ONLY | OFF-PATH | -- | C4/reading | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF RD-R130 |
| M215 | `exp_substrate_acc_evc_adaptive_halting` | data/exp_substrate_acc_evc_adaptive_halting_v1_smoke/metrics.json | HARD_PASS | smoke | 2026-07-08 (metrics.ts_iso) | A (adaptive_vs_fixed_rel,adaptive_vs_random_rel,c) | OK | EXP-ONLY | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | state=VERIFIED DUP-OF RP-D5 |
| M216 | `exp_pfc_gate_cfrpe_trained_v2_smoke` | data/exp_pfc_gate_cfrpe_trained_v2_smoke_smoke/metrics.json | HARD_PASS | smoke | 2026-07-05 (metrics.ts_iso) | A (control_identity,oracle,v1_no_goal) | OK | EXP-ONLY | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M217 | `exp_pfc_gate_cfrpe_deeper_regime` | data/exp_pfc_gate_cfrpe_deeper_regime_v1_smoke/metrics.json | HARD_PASS | smoke | 2026-07-05 (metrics.ts_iso) | A (control_identity,oracle,reach_rank_chance) | OK | EXP-ONLY | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M218 | `exp_pfc_gate_branching_depth_entropy_grid` | data/exp_pfc_gate_branching_depth_entropy_grid_v1_smoke/metrics.json | HARD_PASS | smoke | 2026-07-05 (metrics.ts_iso) | A (focus_flat_gonogo,spearman_flat_vs_depth,spear) | OK | EXP-ONLY | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M219 | `exp_substrate_dopamine_duration_extension_LR_v1` | data/exp_substrate_dopamine_duration_extension_LR_v1/metrics.json | HARD_PASS | smoke | UNDATED (none) | A (BASE_CFRPE_LR,BASE_DURATION) | OK | EXP-ONLY | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | STATE:VERIFIED |
| M220 | `exp_read_xsent_coref_distractor_suppress` | data/exp_read_xsent_coref_distractor_suppress_v1_smoke/metrics.json | HARD_PASS | smoke | 2026-07-24 (metrics.ts_iso) | A (base_acc_xsent) | OK | HDLAB:coref_distractor_suppress.py | OFF-PATH | -- | C4/reading | REGISTRY | UNCHECKED | STATE:VERIFIED |
| M221 | `exp_earn_coref_match_or_allocate_dense_v1` | data/exp_earn_coref_match_or_allocate_dense_v1/metrics.json | HARD_PASS_LEARNABLE_BEATS_BOTH_FLOORS_ON_DENSE_EVAL | ABSENT | 2026-08-02 (metrics.ts_iso) | A (<ARM CONTAINER arms>) | OK | EXP-ONLY | OFF-PATH | -- | C4/reading | REGISTRY | UNCHECKED | STATE:VERIFIED |
| M222 | `exp_pfc_bg_composed_attention_value_gate` | data/exp_pfc_bg_composed_attention_value_gate_v1_smoke/metrics.json | HARD_PASS | smoke | 2026-07-08 (metrics.ts_iso) | A (focus_scramble_gap) | OK | EXP-ONLY | OFF-PATH | -- | -- | REGISTRY | UNCHECKED | STATE:VERIFIED |
| M223 | `exp_situation_model_event_bundle_focus` | data/exp_situation_model_event_bundle_focus_v1_smoke/metrics.json | HARD_PASS | smoke | 2026-07-24 (metrics.ts_iso) | A (<ARM CONTAINER arm_hashes>) | OK | HDLAB:situation_focus.py | OFF-PATH | -- | -- | REGISTRY | UNCHECKED | STATE:VERIFIED |
| M224 | `exp_situation_model_harder_construction_generalization_v1` | data/exp_situation_model_harder_construction_generalization_v1/metrics.json | SELFTEST_PASS | self_test | 2026-07-31 (metrics.ts_iso) | A (chance) | OK | EXP-ONLY | OFF-PATH | -- | -- | REGISTRY | UNCHECKED | STATE:VERIFIED |
| M225 | `exp_situation_model_relation_ablation` | data/exp_situation_model_relation_ablation_v1_smoke/metrics.json | HARD_PASS | smoke | UNDATED (none) | A (floor) | OK | HDLAB:ablation.py | LIVE | -- | -- | REGISTRY | UNCHECKED | STATE:VERIFIED |
| M226 | `exp_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_7` | data/exp_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_7/metrics.json | HARD_FAIL | full | 2026-06-28 (metrics.ts_iso) | NO FLOOR | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | -- | INVISIBLE | UNCHECKED | state=FOUND DUP-OF CG-B134 |
| M227 | `exp_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_13` | data/exp_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_13/metrics.json | HARD_FAIL | full | 2026-06-28 (metrics.ts_iso) | NO FLOOR | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | -- | INVISIBLE | UNCHECKED | STATE:FOUND |
| M228 | `exp_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_19` | data/exp_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_19/metrics.json | HARD_FAIL | full | 2026-06-28 (metrics.ts_iso) | NO FLOOR | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | -- | INVISIBLE | UNCHECKED | STATE:FOUND |
| M229 | `exp_hopfield_spurious_minima_cpu_v1` | data/exp_hopfield_spurious_minima_cpu_v1/metrics.json | HARD_PASS | smoke | UNDATED (none) | NO FLOOR | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | -- | INVISIBLE | UNCHECKED | state=FOUND DUP-OF RP-D3 |
| M230 | `exp_recency_forgetting_curve_cpu_v1` | data/exp_recency_forgetting_curve_cpu_v1/metrics.json | HARD_PASS | smoke | UNDATED (none) | NO FLOOR | OK | EXP-ONLY | OFF-PATH | -- | -- | INVISIBLE | UNCHECKED | STATE:FOUND |
| M231 | `exp_pfc_gate_cfrpe_trained` | data/exp_pfc_gate_cfrpe_trained_v1_smoke/metrics.json | MIDDLE_BAND | smoke | 2026-07-05 (metrics.ts_iso) | A (oracle_headroom) | OK | EXP-ONLY | OFF-PATH | -- | -- | REGISTRY | UNCHECKED | STATE:VERIFIED |
| M232 | `exp_substrate_pattern_completion_corruption_cliff_v2_narrow_regime_seed_7` | data/exp_substrate_pattern_completion_corruption_cliff_v2_narrow_regime_seed_7/metrics.json | SELFTEST_OK | selftest | 2026-06-28 (metrics.ts_iso) | NO FLOOR | OK | EXP-ONLY | OFF-PATH | CONTRACTIVE | -- | INVISIBLE | UNCHECKED | STATE:FOUND |

---

**END. This file needs merging into `notes/RECOVERY_PROGRAM.md` as groups H2 and H3; see sec 1.**

### 5.6 DUPLICATE MAP -- every absorbed row, its state word, and where it went

**90 rows named an experiment that another row already covered.** They are NOT deleted: each is
still present in its own group above with its `STATE:` token rewritten to
`state=<WORD> DUP-OF <row>`, so the state word survives, the evidence pointer survives, and the
count does not double. `*` marks the three cases where two rows disagreed on the state word; all
three are adjudicated against the artifact in sec 5.2.

| absorbed row | its state word | duplicate of | artifact directory |
|---|---|---|---|
| CG-A1 | `VERIFIED` | RP-B3 | `exp_substrate_etf_minilm_dim_expansion_v1` |
| CG-A2 | `VERIFIED` | RP-B9 | `exp_pseudoinverse_real_encoder_keys_v1` |
| CG-A3 | `VERIFIED` | RP-B2 | `exp_substrate_pca_prewhitening_codebook_v1` |
| CG-A4 | `VERIFIED` | RP-A3 | `exp_encoder_retained_trace_requery_coarse_to_fine_v1` |
| CG-A5 | `VERIFIED` | RP-B7 | `exp_f6_bge_large_pinv_mmax_reaudit_v1` |
| CG-A6 | `VERIFIED` | RP-B10 | `exp_kv_learned_projection_v1` |
| CG-A7 | `VERIFIED` | RP-B8 | `exp_pb_e5_vs_bge_pinv_headtohead_v1` |
| CG-A8 | `VERIFIED` | RP-A1 | `exp_substrate_codebook_near_duplicate_diagnostic_cpu_v1` |
| CG-A12 | `VERIFIED` | RP-B1 | `exp_substrate_last_token_vs_whitening_mean_pool_v1` |
| CG-A13 | `VERIFIED` | RP-B5 | `exp_hebb_vs_pseudoinverse_long_v1` |
| CG-A14 | `VERIFIED` | RP-A13 | `exp_attention_salience_common_mode_detector_v1` |
| CG-A18 | `VERIFIED` | RP-B4 | `exp_substrate_dim_expansion_subsumes_whitening_n_enc_10000_v1` |
| CG-A19 | `VERIFIED` | RP-A12 | `exp_substrate_hallucination_detection_minilm_v1` |
| CG-A24 | `VERIFIED` | RP-A10 | `exp_anchor_compose_identity_shuffle_cskg_v2` |
| CG-A26 | `VERIFIED` | RP-C12 | `exp_joint_operator_capstone_selective_readouts_v1` |
| CG-B1 | `VERIFIED` | RP-A11 | `exp_metacog_abstain_readout_signal_thresholding_v1` |
| CG-B3 | `VERIFIED` | RP-B6 | `exp_pb_pinv_llama_l15_keys_v1` |
| CG-B5 | `VERIFIED` | RP-D22 | `exp_c1_entmax_envelope_sweep_v2` |
| CG-B8 | `VERIFIED` | RP-D20 | `exp_generation_decoder_gsbc_native_blocklocal_v1` |
| CG-B18 | `VERIFIED` | RP-C7 | `exp_scale_meaning_learn_arc_heldout_v2` |
| CG-B22 | `VERIFIED` | RP-D12a | `exp_visual_grounding_coherence_v1` |
| CG-B24 | `VERIFIED` | RP-C1 | `exp_consolidated_reader_passive_mechanism_heldout_v1` |
| CG-B25 | `VERIFIED` | RP-D21 | `exp_learned_codebook_generalization_gate_v1` |
| CG-B59 | `VERIFIED` | CG-B21 | `exp_substrate_wikipedia_ppmi_svd_scale_up_full_2026_07_03` |
| CG-B64 | `VERIFIED` | RP-C10 | `exp_encoder_alltype_transfer_stress_v1` |
| CG-B65 | `VERIFIED` | RP-D19 | `exp_generation_decoder_rns_crt_highvocab_v1` |
| CG-B73 | `VERIFIED` | RP-C9 | `exp_situation_model_assembly_encoder_retrain_scale_v1` |
| CG-B81 | `VERIFIED` | RP-C6 | `exp_leakproof_relational_inference_heldout_v1` |
| CG-B92 | `VERIFIED` | RP-D10 | `exp_substrate_working_memory_multi_bank_K_extension_adversarial_v1` |
| CG-B103 | `VERIFIED` | RP-C11 | `exp_frame_order_recovery_hard_comprehension_v2` |
| CG-B141 | `VERIFIED` | CG-B138 | `exp_substrate_schema_family_phase_diagram_v1_seed_7` |
| RD-R3 | `VERIFIED` | RP-D12c | `exp_reader_image_word_grounding_v1` |
| RD-R4 | `VERIFIED` | RP-C14 | `exp_hd_fact_store_semantic_capacity_whitening_v1` |
| RD-R13 | `VERIFIED` | RP-C8 | `exp_grounded_inductive_concept_encoder_heldout_new_v3` |
| RD-R14 | `VERIFIED` | RP-C2 | `exp_consolidated_reader_chaingrade_demo_v1` |
| RD-R15 | `VERIFIED` | RP-C4 | `exp_consolidated_reader_hardsyntax_heldout_v1` |
| RD-R42 | `VERIFIED` | RP-C5 | `exp_read_xsent_coref_scene_protagonist_v1` |
| RD-R57 | `VERIFIED` | RP-D12b | `exp_vision_integrated_recognize_bind_ground_v1` |
| RD-R82 | `VERIFIED` | RP-A7 | `exp_semantic_hd_encoder_meaning_match_v1` |
| RD-R106 | `VERIFIED` | RP-C15 | `exp_reader_component_oracle_ablation_audit_v1` |
| RD-R138 | `REFUTED` | RP-C16 | `exp_multi_turn_loop_realtext_oracle_vs_real_compounding_v1` |
| RD-M3 | `VERIFIED` | RP-A5 | `exp_substrate_anisotropy_dg_pattern_separation_prewrite_v1` |
| RD-M14 | `VERIFIED` | RP-D1 | `exp_substrate_sparsity_free_axis_v5_wm_fixed_n4096_seed_7` |
| RD-M17 | `VERIFIED` | CG-B58 | `exp_substrate_sparsity_free_axis_v4b_pc_widened_alpha_grid_n4096_seed_7` |
| RD-M20 | `VERIFIED` | RP-A9 | `exp_resonator_verifier_readout_v1` |
| RD-M21 | `VERIFIED` | RP-D6 | `exp_substrate_concept_encoder_spoke3_dg_ca3_marr_cls_replay_v1_smoke` |
| RD-M47 | `VERIFIED` | RP-A14 | `exp_resonator_deflation_lowsnr_v1` |
| RD-M48 | `VERIFIED` | RP-A14 | `exp_resonator_theta_gamma_peel_v1` |
| RD-M56 | `VERIFIED` | CG-A20 | `exp_interference_avoidance_conjunctive_vs_additive_v1` |
| RD-M64 | `VERIFIED` | RP-A4 | `exp_dense_hopfield_readout_capacity_correlated_codes_v1` |
| RD-M65 | `VERIFIED` | RD-R11 | `exp_resonator_decision_compgen_2factor_v1` |
| RD-M66 | `VERIFIED` | CG-B88 | `exp_substrate_cross_modal_binding_visual_auditory_v1_seed_7` |
| RD-M69 | `VERIFIED` | CG-B76 | `exp_substrate_cross_modal_binding_3rd_modality_v1_seed_7` |
| RD-M76 | `VERIFIED` | RD-R54 | `exp_parity_in_context_binding_v1` |
| RD-M80 | `REFUTED` | RP-E11 | `exp_grounding_iterative_settling_cascade_depth_v1` |
| RD-M81 | `REFUTED` | RP-E10 | `exp_substrate_binding_op_x_capacity_v1_seed_7` |
| RD-M86 | `VERIFIED` | RD-R20 | `exp_grounding_multihop_generative_replay_traversal_v1` |
| RD-M88 | `VERIFIED` | CG-B85 | `exp_situation_model_assembly_binding_wm_coref_v1` |
| RD-M89 | `VERIFIED` | RP-D15 | `exp_grounding_gated_fusion_relation_inference_mammal_v1` |
| RD-M95 | `VERIFIED` | RP-D12a | `exp_visual_grounding_coherence_v1` |
| RD-M96 | `VERIFIED` | RP-D12c | `exp_reader_image_word_grounding_v1` |
| RD-M108 | `VERIFIED` | RP-D18 | `exp_cleanup_floor_learned_encoder_v1` |
| RD-M118 | `VERIFIED` | RP-E4 | `exp_course_c_operator_fix_ssp_phase_rotation_replay_v1` |
| RD-M119 | `VERIFIED` | RP-E3 | `exp_consol_interleaved_replay_v1` |
| RD-M125 | `VERIFIED` | RP-D2 | `exp_substrate_tier4_hopfield_attention_substitution_pythia160m_v1` |
| RD-M130 | `VERIFIED` | RP-A8 | `exp_substrate_iterative_cleanup_cue_clamped_v1` |
| RD-M140* | `FOUND` | CG-B14 | `exp_substrate_permutation_binding_multiocc_v2_full` |
| RD-M144 | `VERIFIED` | CG-B6 | `exp_consolidation_correct_regimes_v1` |
| RD-M145 | `VERIFIED` | RP-C2 | `exp_consolidated_reader_chaingrade_demo_v1` |
| RD-M146 | `VERIFIED` | RP-C4 | `exp_consolidated_reader_hardsyntax_heldout_v1` |
| RD-M147 | `VERIFIED` | RP-C1 | `exp_consolidated_reader_passive_mechanism_heldout_v1` |
| RD-M152 | `VERIFIED` | RP-D12b | `exp_vision_integrated_recognize_bind_ground_v1` |
| RD-M153 | `REFUTED` | RP-E1 | `exp_consol_conjunction_replay_v1` |
| RD-M154 | `REFUTED` | RP-E2 | `exp_consol_inductive_entity_replay_cskg_v1` |
| RD-M156 | `VERIFIED` | RD-R70 | `exp_compgen_binding_vs_flat_learned_frontend_v1` |
| RD-M160 | `VERIFIED` | RP-C9 | `exp_situation_model_assembly_encoder_retrain_scale_v1` |
| RD-M166 | `VERIFIED` | RP-D8 | `exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1` |
| RD-M168 | `VERIFIED` | RP-C5 | `exp_read_xsent_coref_scene_protagonist_v1` |
| RD-M169 | `VERIFIED` | CG-B15 | `exp_counterfactual_regret_comparison_vmpfc_v1` |
| RD-M177 | `VERIFIED` | RP-C3 | `exp_consolidated_reader_chaingrade_FULL_v1` |
| RD-M179 | `VERIFIED` | RD-R53 | `exp_base_reader_grounded_relations_coref_v1` |
| RD-M181 | `VERIFIED` | RD-R55 | `exp_read_xsent_coref_distractor_suppress_v1` |
| RD-M200 | `REFUTED` | RP-E12 | `exp_substrate_pcgrad_cfrpe_stdp_v2_RESCUE` |
| RD-M202 | `VERIFIED` | RP-D7 | `exp_substrate_multihop_pfc_chunked_2hop_decomposition_v1_smoke` |
| RD-M209 | `VERIFIED` | RP-D4 | `exp_hippocampal_sharp_wave_ripple_v1` |
| RD-M213 | `VERIFIED` | RD-R129 | `exp_multi_competency_coref_ablation_v1` |
| RD-M214 | `VERIFIED` | RD-R130 | `exp_coref_self_confidence_calibration_v1` |
| RD-M215 | `VERIFIED` | RP-D5 | `exp_substrate_acc_evc_adaptive_halting_v1_smoke` |
| RD-M226* | `FOUND` | CG-B134 | `exp_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_7` |
| RD-M229* | `FOUND` | RP-D3 | `exp_hopfield_spurious_minima_cpu_v1` |

`RP` = the original 95 rows, `CG` = chain-graded tier, `RD` = reading + brain-mechanism tiers.

### 5.7 DANGLING -- rows whose cited artifact does not resolve on disk

**12 rows.** Flagged, never dropped: a dangling pointer is a defect in the WRITE path, and
deleting the row hides the defect. **Enumeration method, stated because an absence claim requires
one:** each cited name was expanded (braces, `_AND_` seed forms), then matched against a fresh
`os.scandir('data/')` of 7,898 directories by exact, case-insensitive, string-prefix and
longest-common-token-prefix; a row is DANGLING only when all four stages fail. Four of the twelve
are not cells at all.

| row | cited as | why it does not resolve |
|---|---|---|
| RP-F11 | `pipeline_status field integrity` | **not a cell** -- it is the `data/capability_registry.jsonl` field-integrity audit. Listed for completeness, not a broken pointer |
| RP-G3 | `the capability registry` | **not a cell** -- the capability registry itself (`data/capability_registry.jsonl`, 127 rows). Not a broken pointer |
| RP-G5 | `the 2026-06-25 archaeology tooling` | **not a cell** -- the 2026-06-25 archaeology tooling (`data/_archaeology_*`). The files exist; there is no result directory to resolve |
| CG-F1 | `exp_chain_grade_barrier1_substrate_native_break_partition_oracle_goal_conditioning_3seed` | genuinely absent. The cited name is an ATOM-ID sentence, not a directory; longest token match against 7,898 dirs is 1 |
| CG-F4 | `exp_narrative_q3_temporal_sequence_replay_k20_3seed_hp_cg_q15_1` | genuinely absent under this name. Closest on disk is `exp_narrative_q3_v2_q15_seed{7,13,19}_full` at 3 matched tokens -- **a candidate, not a match.** Whoever next touches this should confirm it or write it off |
| CG-F16 | `metrics.json` | **a WRITE-PATH bug, not a missing result:** the ledger wrote the literal string `metrics.json (ssh pulled)` into the pointer field. The path was never recorded |
| CG-F17 | `see per_seed_metrics_paths in atom metadata` | **a WRITE-PATH bug:** the ledger wrote `see per_seed_metrics_paths in atom metadata` into the pointer field |
| RD-R25 | `exp_dependency_context_codebook_weight_sweep_location_artifact_v2` | genuinely absent under this name; longest token match is 2 |
| RD-R166 | `exp_perceptual_grounding_gap_audit_v1` | genuinely absent under this name; longest token match is 1 |
| RD-R167 | `exp_derived_filler_typing_single_edge_grounding_v1` | genuinely absent under this name; longest token match is 2 |
| RD-R168 | `exp_af43a6dd_grounding_feasibility_probe_atomic2019` | genuinely absent under this name; longest token match is 1 |
| RD-R170 | `exp_probe_fix_tier_verb_semantic_ceiling_flagged_pronouns_v1` | genuinely absent under this name; longest token match is 2 |

**The separately-tracked "53 dangling ledger links" figure is verified and CORRECTED here.**
`tools/result_index_join.py` reports `ledger_dangling=53`. Re-deriving it against disk this
session: **34 of the 53 RECOVER** -- 25 are unexpanded shell brace patterns
(`..._seed_{7,13,19}` written literally into the index, whose artifacts sit in the per-seed
directories), 4 are `_seed_7_AND_13_AND_19` forms, and **4 are literal directory names the join's
`exp_`-prefix alias rule cannot see** (`exp_a2_decisive_test_untuned_auroc_grown_v1_metrics.json`
is a DIRECTORY whose name ends in `_metrics.json`; `lambda_batch_results` and
`substrate_conceptnet_kg_inference_transfer_cpu_v1_metrics.json` carry no `exp_` prefix).
**15 of the 53 are not cells at all** -- `META_RULE_*` atoms, prose strings
(`"LOCAL inline recompute (no metrics.json; preflight)"`), and three `.md` note filenames.
**Only 4 are genuinely-missing cell names:**
`EXP_cortex_hippo_handoff_FULL_seed_17_...`, `exp_edge_importance_stratified_replay_baseline_diagnostic_v2`,
`exp_edge_importance_v3p2_trace_only_with_D1_audit_v2`, `exp_substrate_sparse_recall_capacity_a3f473dd`.
So the honest statement is **"4 genuinely dangling, 34 recoverable by fixing the join's expansion
rules, 15 not cells"** -- not "53 broken links". Fixing brace expansion and the prefix alias in
`result_index_join.py` would retire 38 of the 53 without touching a single experiment.

---

## 6. Group H -- NOT-YET-TRIAGED TIERS (counted, sampled, explicitly NOT examined)

**These are the honesty backstop. Each line states the tier size, how much was actually looked at,
and what remains. Nothing here may be described as reviewed.**

**H1, H2 and H3 have now LEFT this section BY ENUMERATION, and their rows are in sec 5.** Per the
standing rule below, the rows are not deleted -- the zero is recorded.

| # | tier | size | sampled / triaged | NOT-YET-TRIAGED | why it matters |
|---|---|---|---|---|---|
| H1 | terminal chain-graded cells in the cert ledger | **574** (re-derived independently as **565** cells-with-an-identity-on-disk + 14 `META_RULE_*` atoms that are rules, not cells -- treat the two as a bracket, not a discrepancy) | **COMPLETED 2026-08-14 and MERGED into sec 5.4.** 565 of 565 rows written; 547 `metrics.json` opened at HEAD; 48 `verdict_msg` hand-read; **this merge re-checked all 565 verdicts against disk and corrected 6, and recovered 14 rows previously reported as having no directory** | **0 cells.** Residues are qualitative: ~124 floors machine-classified only, 124 contrast-only cells not re-examined, 439 cells dated only by git first-commit, 14 META_RULE atoms | **280 of 565 = HALF the tier is ONE saturation grid** (Appendix A), so this tier is ~287 investigations; the whiten+pinv chain WAS composed (`exp_pb_production_recipe_integration_v1`, 57.3x); the expansion stage is CONTRADICTED from inside the tier. 172 of 565 (30%) carry a real floor; a `scramble`-keyed pass finds 11 and misses 161 |
| H2 | `proven-bound` reading/grounding cells dated >= 07-15 | **127 claimed; 171 on a from-disk re-derivation** | **COMPLETED 2026-08-14 and MERGED into sec 5.5 group R.** 171 of 171 rows written, 164 with a floor (163 Class A + 1 ARM); 5 resolve to no directory | **0 cells.** Residue: 382 of the tier-1+tier-2 403 carry machine-read evidence only; supersession unchecked on all of them | S1 judged this tier RICHER for C3 than the chain-graded tier, and it holds up: positions 1, 3 and 5 of the combined separation-geometry ranking are tier-1 rows |
| H3 | FULL + floored + invisible brain-mechanism passes | **72 claimed; 120 on a from-disk re-derivation** (of 144 FULL, of 232 stems) | **COMPLETED 2026-08-14 and MERGED into sec 5.5 group M.** 232 of 232 rows written. **S2's 97-FULL was an undercount by ~47 stems** because it read the `_smoke` variant as primary wherever a stem had both | **0 cells.** Residue: 60 SMOKE + 5 SELFTEST stems are rows but are not results | families k-WTA / attractor / Hebbian-STDP / cleanup / binding were at or near zero visibility. Verdict on each: sec 9f -- **not weak, MISAIMED** |
| H4 | results on disk absent from every index | **6,566 of 7,623 (86%)** | 0 individually | **6,566** | the derived index (G4) now SEES them; nobody has read them |
| H5 | drift-alarm results: comparison SHAPE, no recognised floor token | **2,009 of 7,623 (26.4%)** | 0 individually | **2,009** | this count IS the vocabulary-drift alarm (sec 8). It is currently FIRING |
| H6 | dangling 16-hex `supersedes` targets | **32** | 0 | **32** | 4 `cert_ledger.jsonl.bak_*` backups (1.2 MB each, 07-01/02) were never searched; they may hold the superseded rows |
| H7 | passes with NO floor anywhere | **1,653** | 0 | **1,653** | **these are NOT evidence** and rank below everything floored. Listed so the tier is visible, not so it is worked |
| H8 | undated results | **5,193 of 7,649 (68%)** | 0 dated | **5,193** | **not a dating gap -- a DIFFERENT HARNESS GENERATION** (leads with `n_seeds`/`per_seed`/`config`, carries `anchor_name` on only 3,053). No current tool matches its conventions |
| H9 | session transcripts | **10,214 `.jsonl`, 6,070 MB** | ~1,000 parsed; the 3.0 GB main file DID complete (658,273 records, continuous 2026-05-31 .. 2026-08-12) | **~9,200 subagent files** | the only source that can answer WHY things were parked. Parser exists: `scratch/arch_scan.py` |
| H10 | whole-stack reviews, content | **14-15 reviews since 2026-05-22** | filenames censused; **1 opened** (2026-06-25, first 3,000 chars) | **~13** | each review started over rather than extending the last. `notes/system_accounting_2026-08-13.md` is the most recent whose content is NOT folded into any current doc |

**The residue in one sentence.** Sec 5 now covers ~974 of the **7,634 `metrics.json` on disk** and
roughly 745 of the cert ledger's ~1,925 atoms; **~7,150 results and ~1,180 atoms have still never
been looked at by anyone**, and rows H4-H10 are where they live.

**Standing rule for this section: a tier moves out of H only by being ENUMERATED, never by being
sampled.** If a pass reads 40 of 127 cells the row becomes "40 triaged / 87 NOT-YET-TRIAGED". It
does not become "reviewed". **Never delete a row when it hits zero -- record the zero**, which is
what H1-H3 above now do.

---

## 7. HOW WE MEASURE PROGRESS -- two commands, no one's word for it

### 7a. The primary number: STATE counts off this file

```bash
cd /d/AI/hd-instrument && grep -oE 'STATE:(FOUND|VERIFIED|WIRED|SHELVED|REFUTED)' notes/RECOVERY_PROGRAM.md | sort | uniq -c
```

**RUN IT OVER THIS FILE ONLY.** Before 2026-08-14 late the rows lived in three files and every
count was wrong depending on which one the reader opened -- `grep` over all three returned 1,063
while this file alone returned 95. That defect is now closed: **the two `recovery_ledger_*` files
still hold their original rows as the primary-source record, and their `STATE:` tokens must not be
added to these.**

**Baseline after the merge (2026-08-14), produced by running exactly that command:**

| STATE | count | of 974 |
|---|---|---|
| FOUND | **30** | 3.1% |
| VERIFIED | **881** | 90.5% |
| WIRED | **1** | 0.1% |
| SHELVED | **2** | 0.2% |
| REFUTED | **60** | 6.2% |

**The arithmetic, so the total reconciles instead of being rounded away:**

```
  95   rows in RECOVERY_PROGRAM.md (unchanged)
 565   rows in the chain-graded ledger
 403   rows in the reading + brain-mechanism ledger
-----
1063   raw rows, which is what grep over all three files returned
- 90   rows absorbed as duplicates of another row (same experiment DIRECTORY; sec 5.6)
+   1   row ADDED by this merge (CG-G1, the v2b HARD_FAIL that had no row anywhere)
-----
 974   rows carrying a countable STATE in this file
```

**There is no gap.** 90 absorbed + 974 counted = 1,064 = 1,063 raw + 1 added. Each absorbed row
is still physically present in its group with its state word preserved as
`state=<WORD> DUP-OF <row>`, which `STATE:[A-Z_]+` deliberately does not match. If the command
above ever returns something other than 974, either a row lost its token or a duplicate was
un-marked; sec 5.6 is the reconciliation table.

**Distinct investigations is a DIFFERENT number and is the one to quote in prose:** 974 rows minus
the 279-row saturation grid counted once = **~696**. Never say "974 experiments".

The two numbers that must move: **WIRED goes UP** and **VERIFIED goes DOWN** (every VERIFIED row
must exit to WIRED, SHELVED or REFUTED). FOUND must reach **0** first -- an unverified row is not
an asset. **WIRED is 1 of 974, and that one row is the index tool, not a capability.**

> **COUPLING NOTICE (per `CLAUDE.md` "a doc parsed by code is coupled to it"):** the literal token
> `STATE:` and the five state words are an **API** for the command above. If they are reworded, the
> counting command in this section must change in the same commit. Do not introduce a sixth state
> without updating sec 3, this section and the baseline table together. The `state=` (lowercase,
> `=` not `:`) form used for absorbed duplicates in sec 5.6 is deliberately outside that API.

### 7b. The disk-derived number: the index that nobody has to remember to update

```bash
cd /d/AI/hd-instrument && .venv/Scripts/python.exe tools/result_index_join.py --hook   # 0.6s, reads the persisted report
cd /d/AI/hd-instrument && .venv/Scripts/python.exe tools/result_index_join.py --scan   # ~290s, recomputes and persists
```

`--hook` output as of this merge, verbatim:

```
[result-index] last join 9.2h ago
    on_disk=7623 undated=5136 orphans=6566 ledger_dangling=53
    DEFECTS: cert_ledger STALE: newest ts 2026-07-25 is 21 days old; FLOOR VOCABULARY DRIFT:
    2009 results have a comparison SHAPE but no recognised floor token
```

**Targets, in priority order:** `orphans` DOWN from 6,566; the `FLOOR VOCABULARY DRIFT` line
resolves as `FLOOR_TOKENS` is widened (sec 8); `ledger_dangling` DOWN from 53 -- and **sec 5.7 now
shows exactly how: 34 of those 53 are recoverable by fixing brace expansion and the `exp_` prefix
alias in the join, 15 are not cells at all, and only 4 are genuinely missing.** This probe is
already in `tools/session_start_hook.py`, so it reports itself at every session start, compaction
included, and its own staleness is part of the report.

**A third number this merge exposes, currently unmeasured by any tool:** an artifact can exist and
still be invisible because it is not named `metrics.json`. Row CG-B143's directory holds
`metrics.fresh_2026-06-30.json`. Nothing in the repo globs for that.

### 7c. What a completed row looks like

A row is only allowed to leave VERIFIED with the evidence attached in the row itself:

- **-> WIRED**: name the `hdlab/` module, name the registry row, and paste the RUNTIME closure line
  showing it (sec 4's command, re-run). Not a grep. Not "it should be imported".
- **-> SHELVED**: write the revival criterion as a testable condition ("when a narrative
  multi-sentence reading pipeline exists", not "later").
- **-> REFUTED**: quote the number that kills it and cite the file it came from. **And check first
  that the artifact is a MEASUREMENT and not an abort** -- two rows in this file recorded a
  refutation where the run had refused to start or died of OOM (sec 5.2, CG-B134 and CG-B7).

---

## 8. ANTI-RECURRENCE -- detect by SHAPE, never by vocabulary

The cause is measured, so the fix is measured too. **The rule is NOT "search harder".**

**What actually happened.** Every sweep searched `metrics.json` by verdict string. That method is
structurally blind to: a `cert_status` **FIELD** in a different file (the whole 574-cell ledger); a
hyphenated `chain-grade` (10 rows, plus `proven_bound` 35 and `honest-negative` 11 -- **56 rows lost
to punctuation inside a single field of a single file**); an anchor **NAME** containing "chaingrade"
(which produced a confidently-reported "07-23 chain-grade reader triple" that **does not exist** --
two of the three are `proven-bound` and the third has no `cert_status` at all); `_fulldev` /
`_smoke` suffixes; and June's floors entirely -- **`scramble` appears ZERO times in June while 33 of
60 June cells have a genuine control arm.** Verdict vocabulary went **13 distinct strings in June to
444 in July** (one new string per four runs), and **1,357 results carry a verdict with no PASS or
FAIL token at all**; **218 have no `verdict` key whatsoever**. Floors are frequently not keys but
PROSE inside `verdict_msg` (`vs random=0.0857`) or bare ARM NAMES (`CORTEX / NO_CONSOL /
NAIVE_WTA`).

**Therefore, four binding rules.**

1. **SHAPE FIRST, VOCABULARY SECOND, AND COMPARE THE TWO.** A floor is detected by
   `shape_arms_dict` (>=2 sibling dicts sharing a numeric key) and `shape_token_pair` (>=2 sibling
   numeric keys differing in exactly one token position). `FLOOR_TOKENS` is **broad, expandable, and
   NEVER used as a filter**. The disagreement between the two detectors is the alarm:
   **`STRUCT_ONLY` = 2,009 of 7,623 (26.4%) right now, and it is FIRING** -- a comparison shape with
   no recognised token means the lexicon has aged. The tool raises this as a defect rather than
   silently under-counting, which is exactly what the old scheme lacked.
2. **DERIVE THE INDEX FROM DISK; NEVER REQUIRE REGISTRATION.** 6,566 results are unindexed because
   registration is a manual step and manual steps get skipped. `tools/result_index_join.py` walks
   `data/` every run. **There is nothing to remember, so there is nothing to forget.** This is
   `CLAUDE.md` evidence-discipline sec 2 ("enumerate from the filesystem, then reconcile to the
   registry, never the reverse") implemented rather than advised.
3. **AN ABSENCE CLAIM REQUIRES AN ENUMERATION, NOT A SEARCH.** "I looked and did not find it" is no
   evidence of absence when the naming convention is unknown -- and this file contains four fresh
   proofs: `exp_leakproof_relational_inference_context_sweep_v1` (C6) does not exist under that
   name but `exp_leakproof_relinfer_context_sweep_v1` does; `sr_routing` and `scale_win` (F4, F5)
   are NOT LOCATED rather than absent; `data/*vamp*` matches only SVAMP math cells (F7). **State
   HOW you enumerated.**
4. **EXISTS / IS-REACHED / IS-GOOD ARE THREE QUESTIONS.** Reachability is measured by RUNTIME import
   closure (sec 4), never by grep -- grep is wrong in both directions in the same file (lazy imports
   inside function bodies are invisible; a module named only in a string constant or a comment reads
   as an import). And a DEFAULT-path trace measures the default path, **not existence**: the
   `encoder_retrain_persist` case is the standing precedent for that error.

**Cadence, deliberately not a cron.** OS scheduled tasks failed silently twice (11 `hd_*` tasks for
~12 days; the KB ingest for 6 days). The enforcement is `tools/session_start_hook.py`, which fires
on every start / clear / **compact** regardless of scheduler state. The `--scan` recompute (~290s)
stays a deliberate act; the hook only reports the persisted result and its age, so **the checker
going quiet is itself visible**.

---

## 9. PRIORITY ORDER -- the rule, then the ranking

### 9a. The rule, stated before it is applied

```
score = C3_WEIGHT x FLOOR_WEIGHT x SURVIVES_WEIGHT x WIRE_COST_WEIGHT
```

| factor | 1.0 | 0.6 | 0.3 |
|---|---|---|---|
| **C3_WEIGHT** -- bears on the gate | moves C3 (read-out quality / within-neighbourhood separation) | bears on C1/C2/C4, or BOUNDS C3 | neither |
| **FLOOR_WEIGHT** -- has a real control | Class A / ARM, read on disk, margin over floor large | floor is PROSE, or margin small, or n small | NO FLOOR / UNPINNED |
| **SURVIVES_WEIGHT** -- survives to HEAD | opened at HEAD today, verdict + run_mode confirmed | opened, but `run_mode` absent / `smoke` / `lite` | not opened |
| **WIRE_COST_WEIGHT** -- module vs build | an `hdlab/` module already exists | EXP-ONLY: experiment code + outputs, a module must be written | NOT LOCATED / must be built from nothing |

**Two overrides, applied after scoring:**
- **A BOUND outranks a lever it invalidates.** A9 and A10 both say the read-out is oracle-bound;
  A11's `S4_cleanup_margin` HARD_FAIL says the same a month earlier. **Three independent results,
  all predating the SNR-wall diagnosis, say C3's 5.2pp gap will not be closed by a better read-out
  RULE.** So anything that only rescores candidates is demoted, and upstream work is promoted.
- **A cheap diagnostic may MEASURE but may never SET DIRECTION** (`CLAUDE.md` non-negotiable 3).
  #1 below is a measurement, ranked first because of what it would settle, not because it is cheap.

### 9b. The top 10

| rank | item | score drivers | what it buys |
|---|---|---|---|
| **1** | **A1 -- re-run the near-duplicate diagnostic over the 5,491 LIVE anchors** (it ran on 241 math atoms) | C3 1.0 x floor 1.0 x survives 1.0 x cost 0.6 | It is the **only** artifact in the corpus that MEASURES C3's exact failure -- right neighbourhood, wrong member -- and it found **22% of a 241-atom codebook with a near-identical neighbour and one pair at cosine 1.0000 between two genuinely distinct concepts**. If that reproduces at 5,491, median rank 84 has a **mechanical** cause that no cleanup rule can fix, and the three oracle-bound results above are explained |
| **2** | **B5-B9 + B11 -- determine the LIVE store's write rule, then the pinv swap** | C3 1.0 x floor 1.0 x survives 1.0 x cost 0.6 | The single most-replicated result in the whole corpus: **4 independent encoder families plus synthetic**, with a non-degenerate anchor (Llama-L15 **122 -> 614**). Three of five say Hebbian sits at **ZERO** capacity on real MiniLM/BGE/E5 keys. **Quote as "Hebb reaches 0 where pinv reaches 0.4-0.55", never as a ratio.** Blocked on one read: what does the live store actually do? |
| **3** | **B1 + B11 -- check what the live read-out pools and whether it whitens** | C3 1.0 x floor 0.6 (ARM) x survives 1.0 x cost 1.0 | `last_token_raw` 0 / `mean_pool_whiten` 40 / `last_token_whiten` **122**. If the live path mean-pools without whitening it is running at 40 where 122 is available -- **no new mechanism required**. `hdlab/whitening.py` EXISTS and is **OFF-PATH** (verified), so the lever is islanded. **Read C14 (`hd_fact_store_semantic_capacity_whitening_v1`) first -- the fact store IS live** |
| **4** | **The five-stage chain, END TO END** (B1 -> B3/B4 -> B2 -> B5-B9 -> A3) | C3 1.0 x floor 1.0 x survives 1.0 x cost 0.6 | Every stage is separately chain-graded, terminal, and on disk. **No cell tests the chain.** It is the clearest un-run experiment in the corpus and it sits **upstream** of the read-out rule -- the only place the SNR wall leaves room |
| **5** | **A2 -- peel/SIC read-out** (`hdlab/peel_sic.py` must be WRITTEN; it does not exist) | C3 1.0 x floor 1.0 x survives 1.0 x cost 0.6 | Flat argmax **0.204 -> 0.940** on REAL codes, 5 seeds, cv 0.034. C3's failure mode is precisely a collapsed argmax over confusable candidates. Demoted below the upstream work by the BOUND override, but it is the strongest read-out-time candidate that exists |
| **6** | **A4 + A5 -- Hopfield-on-correlated-codes and DG separation at write time** (both modules EXIST, both OFF-PATH) | C3 1.0 x floor 1.0 x survives 1.0 x cost 1.0 | **The lowest wire-cost items on the list** -- the code is written. A5 acts at WRITE time (effrank **10.08x** on real Pythia keys), which the BOUND override favours. A4's honest caveat travels: the lift shrinks 6.74x -> **1.63x** exactly as correlation strengthens, i.e. weakest in the regime C3 needs most. **Gate A4 on D3 (spurious-minima 0.957) first** |
| **7** | **H2 -- triage the 127 `proven-bound` reading cells dated >= 07-15** (120 have Class-A floors) | C3 1.0 x floor 1.0 x survives 0.3 (not opened) x cost n/a | **S1's own conclusion: "terminal chain-graded" is the WRONG filter for C3 work** -- only 35 of 574 are dated >= 07-15, while the entire late-July reading/grounding arc is banked as `proven-bound`. This is the largest untouched tier that is topically on-target |
| **8** | **A6 + F2 -- the pooling interface, and the only live dictionary lookup** | C3 1.0 x floor 1.0 x survives 1.0 x cost 0.6/1.0 | A6 is **a positive being carried as a negative**: the distributional-context POOLING INTERFACE separates synonym from sibling at AUC ~0.74 **for free, untrained**, and it is not the interface the read-out uses. The `randinit >= trained` control kills the LEARNING claim, not the INTERFACE claim. F2 (`wordnet_polarity_propagation`, 16,922 B, off-path, unregistered) is a live dictionary path on the same defect |
| **9** | **C1 -- promote the passive-voice competency** | C3 0.6 x floor 1.0 x survives 1.0 x cost 0.6 | **23/24 vs a true 0/24 floor**, held-out, ablated, non-regressing, glass-box, on a NAMED CONSTRUCTION TYPE. The standing anchor *"comprehension is a growing library of construction-competencies"* asks for exactly this artifact and it has existed since 2026-07-24, in no plan and no registry row. Ranked 9th only because it is a PARSER-side win: **file it under reading, not C3** |
| **10** | **G1/G2/G5 -- salvage the 14 resolving supersedes edges, freeze the ledger, read the 06-25 enriched inventory** | C3 0.3 x floor n/a x survives 1.0 x cost 1.0 | Not a capability -- it is what stops rows 1-9 from going dark a third time. The `supersedes` judgements exist **nowhere else**; 52 of 66 edges dangle, so merging as-is would import the breakage. And `data/_archaeology_inventory_enriched.jsonl` (**2.4 MB, 3,269 experiments already joined to the cert ledger**) is a ready-made answer to much of H1/H4, seven weeks stale but structurally intact, **and was never opened** |

**Deliberately NOT in the top 10, and why** (so the omissions are decisions, not oversights):
D13a/D13b (MAVEN-ERE) and D12a-c (CLIP-era vision) are **EXPERIMENT-ONLY** -- "wire it" is really
"build it" -- and neither serves C3; F5 (`scale_win`) is likewise BUILD and its source is
NOT LOCATED; D5/D6/D3/D4 are **SMOKE-ONLY** and must be promoted to FULL before they mean anything;
A11/A12 raise precision at partial coverage, not hit@1 at full coverage, which is the gate;
D22 (entmax) explicitly reports **delta +0.000 on quality**; E5-E12 are refutations -- their value
is that they **stop** work, and it is already banked by being written here.


### 9c. The chain-graded tier ranked against the live problem -- SEPARATION GEOMETRY

*Imported verbatim from S5 on merge. Its ranking criterion is stated before it is applied, which is
why it is reproduced rather than summarised.*
**The ranking criterion, stated before it is applied.** The C3 defect was re-diagnosed on 2026-08-14 and it is **not meaning supply**: wiring 36,810 norms + a 237.7M-token encoder took hit@1 4.80% -> 9.40%, but a **zero-meaning character-trigram control reproduced 9.05%**, crowding never fell, and sister-term conversions were 1-3 of 4000. The defect is **comparison GEOMETRY** -- a bag of co-occurring words cannot separate paradigmatic neighbours that appear in near-identical contexts (`sympathetic`/`parasympathetic`). So a cell ranks high here **only if it bears on separating items that share contexts, or on a representation that is not context-bag cosine.** Refuted downstream and therefore excluded: rank-1 common-mode removal, the forgetting kernel, sharpening read-outs, the composed five-stage chain as a read-out fix.

**Two standing bounds apply to everything below** (RECOVERY_PROGRAM sec 9a): `exp_anchor_compose_identity_shuffle_cskg_v2` harvests **93% of its own oracle** and `exp_resonator_verifier_readout_v1` harvests **exactly** its oracle. Anything that only **re-scores existing candidates** is demoted; anything that changes **what the candidates ARE** is promoted.

##### 4a. THE TOP 15

Ranked, with the floor as it actually reads on disk. Full rows for these are in group CG-A.

| rank | cell | floor, as read | why it bears on SEPARATION GEOMETRY | moves |
|---|---|---|---|---|
| **1** | `exp_substrate_permutation_binding_multiocc_v2_full` | **A by the detector, but for the WRONG reason and this is worth reading**: it matched the token `perm` in `perm_acc_mean`, where `perm` names the TREATMENT, not a control. The REAL reference arm is `FHRR=0.0629` -- the failing conventional binding. 3 seeds, cv=0.0000. *The shape was right; the vocabulary was right by accident.* | **The single most on-target cell in the tier.** It resolves *same-role COLLISION* -- two items occupying the same slot, which is structurally the same failure as two paradigmatic neighbours occupying the same context. Permutation-indexed binding reaches **1.0000 where FHRR reaches 0.0629** (lift 0.9371). It replaces the representation rather than re-scoring it, so the oracle-bound override PROMOTES it. | **C3**, C1 |
| **2** | `exp_interference_avoidance_conjunctive_vs_additive_v1` | A -- `add=0.273`, `freq_oracle=0.654`, `gap_control=0.000` (a clean must-fail control) | **A bag beats nothing; conjunctive/orthogonal storage beats the bag.** At M_HI=256 `orth=1.000` vs `add=0.273` -- and the ADDITIVE arm *is* the bag-of-co-occurrence geometry the C3 diagnosis indicts. It also names the crossover (`crossover_M=48`), i.e. where the bag starts failing. This is the closest thing in the corpus to a direct measurement of the new diagnosis. | **C3**, C1 |
| **3** | `exp_substrate_codebook_near_duplicate_diagnostic_cpu_v1` | A -- near-dup floor **0.1333**; de-dup arm vs full arm; 3 seeds, cv=0 | Measures C3's exact symptom -- right neighbourhood, wrong member. **49 pairs at cos>0.9; 54/241 (22%) of atoms have a near-neighbour above threshold.** Its own words: *"the residual is genuine distinct-but-close atoms needing finer encoding"*. RECOVERY_PROGRAM rank 1 already; confirmed here independently, on disk, run_mode `full`. | **C3**, C1 |
| **4** | `exp_substrate_decomposition_resonator_alpha05_cpu_v1` | ARM -- `plain` (non-augmented) arm is the reference; K=241/F=3/noise=0 | **Same K=241 codebook as the near-dup diagnostic, and it is the FIX side of it.** alpha=0.5 identity-augmented encoding reaches precision@1 >= 0.95 where the plain encoding does not, and the cell's own claim is that the *encoding* fix GENERALIZES from composition cleanup to resonator decomposition ('two-vector architecture, 2nd appearance'). **Encoding-side, not read-out-side, so the oracle bound does not apply to it.** | **C3**, C1 |
| **5** | `exp_substrate_name_augmented_encoding_recovery_canonical_rerun_v593` | NO FLOOR visible in metrics.json -- **but the alpha grid IS the contrast** (alpha=0 is the reference); flagged as a probable detector false negative, VERIFY BY HAND before citing | Third appearance of the same identity-augmentation lever, now at binding scale: cleanup@1 **F10=0.9883, F20=0.9617** at alpha=0.5. Together with the row above this is a **replicated encoding-side separation lever**, which is the shape the new diagnosis asks for. | **C3**, C1 |
| **6** | `exp_pb_production_recipe_integration_v1` | A -- `naive(raw+hebb)=3` is the control arm; full recipe = 172 | **The composed whiten+pinv recipe, measured: 57.3x over naive.** This is two of the five stages RECOVERY_PROGRAM says were never composed. It does not by itself move hit@1, but it removes the largest unknown from rank 4 of that document's priority list and re-prices the whole group-B programme. | **C3**, C1 |
| **7** | `exp_substrate_encoder_capacity_at_scale_battery_gpu_v1` | CONTRAST-ONLY by the detector, but the `raw_sign` arm IS the floor -- `{MiniLM/raw_sign 3.0, MiniLM/zca 7.0, BGE/raw 0.0, BGE/zca 40.0, Llama-3.2-1B/raw 0.0, Llama-3.2-1B/zca 122.0}` | **The encoder-choice lever, measured as a full encoder x recipe grid.** If the live read-out runs MiniLM raw it is at capacity **3** where Llama-3.2-1B + ZCA reaches **122** -- a 40x separation headroom with no new mechanism. This is the supply side of the same geometry question and it is one config change. | **C3**, C1 |
| **8** | `exp_encoder_retained_trace_requery_coarse_to_fine_v1` | ARM -- `sparse_fullV=0.541` reference arm reproducing the v1 wall; full-fine CEILING 0.992 | C3 is a ranking problem (median target rank 84 of 647). Coarse shortlist then fine read inside it costs **zero** recall against the full-fine ceiling (`final_recall 0.992` vs ceiling 0.992, `shortlist_hit@k=0.1 = 1.000`). **Demoted from where its numbers would put it** because it re-scores rather than re-represents -- the oracle-bound override. | **C3** |
| **9** | `exp_generation_decode_selfmargin_dupclass_exact_v1` | A -- beats the falsified PR-gaussian by 2.68x on worst-cell error and the naive-independent birthday model by a factor of 1e+; per-cell ratio-error <= 1.041 | **An exact analytic law for WHEN duplicate classes collapse a decode**: `p1 = n_distinct(codebook)/V` predicts the collapse with mean ratio 1.0021. That is a closed-form predictor of the crowding C3 exhibits -- it says whether 5,491 anchors are ABOVE or BELOW the collapse point before anything is built. | **C3** |
| **10** | `exp_substrate_expansion_method_battery_gpu_v1` | NO FLOOR by the detector -- **detector false negative**, the `native` arm is the reference (`native=0.0065 rp_x4=0.0065 zca_whiten=0.0517`) | **A REFUTATION that must be read before group B is acted on**: *expansion cannot beat rank (rp_x4 ~ native) while whitening helps via decorrelation*. It contradicts the dimensional-expansion stage from inside the same chain-graded tier. Ranked high because it may DELETE a stage, which is worth more than adding one. | **C3**, C1 (bounds) |
| **11** | `exp_substrate_last_token_vs_whitening_mean_pool_v1` | ARM -- `last_token_raw` = **0** is the reference; 3 seeds bit-identical | Pure representation-side lever on the same sentence encoder the read-out uses: capacity `last_token_raw 0` / `mean_pool_whiten 40` / `last_token_whiten 122`. If the live read-out mean-pools without whitening it runs at 40 where 122 is available. | **C3**, C1 |
| **12** | `exp_substrate_pca_prewhitening_codebook_v1` | ARM -- `cap_unwhitened=3` vs `cap_pca_whitened=7`; **recovered ONLY by the relaxed unequal-length sibling rule** | Whitening = decorrelation = the operation that separates items sharing contexts. **Deflate hard: the absolute capacities are 3 and 7 items.** Its own framing ('one-line universal real-encoder rescue') is not supported at n=7. Ranked for the MECHANISM, not the number. | **C3**, C1 |
| **13** | `exp_pseudoinverse_real_encoder_keys_v1 (+ 4 siblings)` | ARM in all five -- the `hebb_*` arm IS the floor; **no arm name contains a control word**, which is why a lexical pass misses the entire family | The write rule that determines what the stored items ARE. Non-degenerate anchor: Llama-L15 **122 -> 614 (5.03x)**. On real MiniLM/BGE/E5 keys Hebb reaches **0** where pinv reaches 0.40-0.55. **Quote it that way -- the `400000000x` in this cell's own `verdict_msg` is an x/0 artifact.** | **C3**, C1 |
| **14** | `exp_kv_learned_projection_v1` | A -- **shuffled control 0.015**, analytic ceiling 0.080, held-out split | The *missing-LEARNING* flavour: a LEARNED contrastive projection that raises **key separation to 0.878** and transfers to held-out facts (worst-seed recall 0.827, std 0.019). A learned metric is the brain-compatible answer to a separation defect and it reuses `hdlab/learner` rather than building in parallel. **Deflation: `n_enc=2`, synthetic KV task.** | **C3**, C1 |
| **15** | `exp_substrate_hallucination_detection_minilm_v1` | ARM -- `grounded_conf` vs `hall_conf` IS the contrast; **the source note's detector scored this Class D and flagged it as its residual false negative -- the NEG_COND rule here catches it** | AUC **0.999** separating grounded from hallucinated (`grounded_conf 0.204` vs `hall 0.107`). It separates a true from a plausible-but-wrong item, which is the C3 error mode -- but it raises **precision**, not hit@1 at full coverage, so it is last of the fifteen. | C3 (precision) |

**Deliberately NOT in the top 15, so the omissions are decisions:** `exp_anchor_compose_identity_shuffle_cskg_v2` and `_scaling_ladder_cskg_v3` (they BOUND C3 at 93% of oracle rather than moving it -- and that bound is the reason ranks 1-5 are representation-side); `exp_metacog_abstain_readout_signal_thresholding_v1` and `exp_attention_salience_common_mode_detector_v1` (precision at partial coverage, and the common-mode detector's own result explains why rank-1 common-mode removal came back HARD_FAIL_NO_EFFECT -- it fires only in the correlated mode); `exp_c1_entmax_envelope_sweep_v2` (reports **delta +0.000 on recall** -- it is a FLOPs win, and its title says 'read-out win'); `exp_substrate_capacity_cliff_fhrr_constant_derivation_v1` (a beautiful closed-form derivation, C_FHRR=1.9934 within 0.33% with zero free parameters, but it predicts capacity rather than changing separation); the `exp_integration_full_stack_*` pair (4-stage composition at compounding_ratio ~1.0 -- infrastructure, not a lever).

### 9d. The reading + brain-mechanism tiers ranked for separation geometry

*Imported verbatim from S6 on merge.*
Scored as `geometry-sign x floor x run-mode x verdict x doc-invisibility`, seed-collapsed, FULL
runs with a pass-flavoured verdict only. **Each candidate is labelled with the sign of its effect,
because the two signs are opposite**: EXPANSIVE mechanisms decorrelate and spread codes apart
(what within-neighbourhood separation needs); CONTRACTIVE mechanisms settle toward stored patterns
and eat weakly-correlated distinctive features (the standing caution); FACTORIAL mechanisms keep
role and filler separable instead of pooling them into one bag.

| # | cell | sign | run/floor | what it actually shows (read on disk) |
|---|---|---|---|---|
| 1 | `exp_role_filler_factorization_compgen_v1` (T1) | **FACTORIAL** | full / A | **FACTORED held-out 1.000 vs FLAT held-out 0.003, gap 0.997**, chance 0.333, `must_fail=True`, `learn_sig=True`, gen_drop F=0.000 vs flat 0.382. The cleanest statement in either tier that a factored code generalises where a flat/pooled one is at zero |
| 2 | `exp_agreement_learned_depth_accumulator_v1` (T1) | **FACTORIAL/EXPANSIVE** | full, **5 seeds** / A | **learned_depth 0.7733 (+-0.0012) vs `local_bag` 0.4533**, held-out buried n=2677, and it **beats its own deterministic ceiling 0.7561**. Shortcut battery all below: nearest_noun 0.5521, first_noun 0.4135, majority 0.6279, fixed_random 0.5690. SCRAMBLE 0.7736 -> 0.5203, DROP +0.2533. **This is the closest thing in the corpus to a direct existence proof of the tonight hypothesis: a learned non-bag representation beats a bag-of-words arm by +0.32 on the same items** |
| 3 | `exp_resonator_decision_compgen_2factor_v1` (T1) | **FACTORIAL** | full / A | RES held-out **1.000** vs FLATjoint 0.180 / FLATfactored 0.229, **gap +0.820**; GEN_GAP res +0.000 vs flat_joint +0.811; pos-control 1.000, chance 0.250, `arms_differ=True`. Resonator factorisation, not cosine over a pooled bag |
| 4 | `exp_substrate_anisotropy_dg_pattern_separation_prewrite_v1` (T2) | **EXPANSIVE** | full, 3 seeds / A | `dg_full 0.942` vs bar 0.50, **effrank lift 10.08x**, off-diagonal mass 0.179 -> 0.012, on real Pythia-2.8b keys; `uniform_no_presep` collapses to 0.083. Module EXISTS (`hdlab/dg_pattern_separation.py`) and is off-path. **Read row 1 of sec 5 before acting on this** |
| 5 | `exp_role_filler_factorization_reader_coupled_cg_v1` (T1) | **FACTORIAL** | full / A | REAL F=0.823 vs **FLAT 0.005**, gap 0.818, chance 0.062, Gate-D control F=0.914, posctrl and mustfail both True. Caveat carried by the cell: `capNOTnoise=False` and the gate itself adds only +0.004 |
| 6 | `exp_substrate_pc_sparsity_x_encoder_crossproduct_v2_n8192_seed_{7,13,19}` (T2) | **EXPANSIVE** | full, 3 seeds / A | k-WTA at production N=8192. `sat_frac` 62.5% -> **43.75% = capacity-lift**, `n_encoders_with_sparsity_range>=0.15` **1/4 -> 4/4**, interaction pairs 4/6, per-encoder sparsity range up to 0.80. The best-evidenced member of a **17-of-17-invisible, zero-registry-row** family |
| 7 | `exp_substrate_sparsity_free_axis_v5_wm_fixed_n4096_seed_{7,13,19}` (T2) | **EXPANSIVE** | full, 7 seed dirs / A | `rho_c <= -0.60` at all 9 (M,alpha) pairs, cross-seed cv < 0.15, with the era's rare EXPLICIT floor keys `hp_random_floor` / `positive_control_wm_ok` |
| 8 | `exp_resonator_verifier_readout_v1` (T2) | **FACTORIAL** | full, 3 seeds / A | K4 harvest **0.806** vs plurality 0.453 and baseline_K4 0.133 -- **and `oracle_any` is also 0.806**. A BOUND, not a lever: it harvests exactly the oracle. Already in `RECOVERY_PROGRAM.md` A9; reconfirmed here from the tier-2 side |
| 9 | `exp_graded_divisive_comparator_v1` (T2) | **EXPANSIVE** | full / A | The 08-14 landed comparator: LIVE(A_SSN) 0.6395 -> PRIMARY(A_GGZ) **0.6997**, d=0.0602 CI [0.0440,0.0762], SCRAM_PRIMARY 0.5065, FREQ 0.4800, self_retrieval 0.8433 -> 0.9233. **This one is already WIRED (`38f7a0d5c`)** and is the only row in either tier that is |
| 10 | `exp_novel_atom_generalization_codebook_binding_v1` (T2) | **EXPANSIVE+FACTORIAL** | **JUNK run_mode** / A | codebook_derived **0.776** vs random_code 0.028 (chance 0.033), margin 0.749, vs handed ceiling 1.000; memorize_prototype and flat_end_to_end both **0.000**. Ranked 10th ONLY because its `run_mode` field contains the cell name -- **run mode is unknown and it may not be a full run** |
| 11 | `exp_resonator_deflation_lowsnr_v1` / `exp_resonator_theta_gamma_peel_v1` (T2) | **FACTORIAL** | full / A | The peel/deflation family. Same mechanism class as `RECOVERY_PROGRAM.md` A2 (peel/SIC, flat argmax 0.204 -> 0.940), which has no `hdlab/peel_sic.py`. Independent corroboration that the peel route exists in more than one cell |
| 12 | `exp_grounding_tem_factorized_heldout_concept_v1` (T1) | **FACTORIAL** | full / A | Factorised (TEM-style) grounding on held-out concepts. The only tier-1 cell that applies a factorised code to the grounding anchors themselves |
| 13 | `exp_substrate_operational_wall_dual_readout_bit_match_and_cleanup_*` (T2, 3 variants) | CONTRACTIVE | full / A | Dual read-out at bit-matched cost. Highest-ranked purely CONTRACTIVE item; the sign caution applies in full |
| 14 | `exp_substrate_pc_cleanup_family_phase_diagram_v2_M_sweep_s11` + `exp_stage1_regime_map_storage_x_cleanup_v1_s7` (T2) | CONTRACTIVE | full / A | The phase-diagram programme -- ~50 floored passes underneath a memory-index entry that records only the DEFERRAL. Maps where cleanup works, does not separate neighbours |
| 15 | `exp_cortex_regenerative_cleanup_vs_analog_accumulate_v2` (T2) | CONTRACTIVE | full / A | Note its **v1 sibling is HARD_FAIL** -- read both or the cliff is invisible |

**Reading the ranking honestly.** Positions 1-3 and 5 are TIER 1, the reading tier, and they beat
the entire brain-mechanism tier on this criterion. They are also the only candidates whose control
arm is *literally the thing tonight's diagnosis blames* -- a FLAT or a `local_bag` arm sitting near
zero while the factored/learned arm is near ceiling. Positions 13-15 are the highest-scoring
CONTRACTIVE items and are listed to be explicit that they are the WRONG SIGN, not to recommend
them.

### 9e. The separation-geometry route has already been attacked on the real task -- and lost

*Imported verbatim from S6. **Read with sec 11 corrections 1 and 2**, which withdraw the inference
that these failures CLOSE the route.*
The most decision-relevant thing in either tier. All FULL, all floored, all invisible to every
planning doc, all quoted from their own `metrics.json`:

| cell | verdict | what it measured |
|---|---|---|
| `exp_dg_pattern_separation_mcscript_purity_v1` | **HARD_FAIL** | DG separation at sparsity 0.05 gives `mean_purity_multi = 0.1013` against a **~0.1999 baseline -- it scores BELOW the baseline.** Its own words: *"the substrate cannot discriminate 195-way online with this keying signal even with DG-style separation"* |
| `exp_selfplay_dg_pattern_separation_xfit_v1` | **HARD_FAIL_REPRESENTATION_INSUFFICIENT_REDIRECT_EXOGENOUS** | 5 seeds. B1_crossfit corr 0.393 -> DG_XFIT corr 0.377; **improvement from DG = +0.015.** `dg_fires=True`, `codes_ok=True` -- the mechanism ran correctly and bought nothing. Verdict explicitly redirects to an EXOGENOUS source |
| `exp_grounding_encoder_sparse_block_binding_v1` | **HARD_FAIL_BLOCK_BINDING_INSUFFICIENT** | 3 seeds. Best block arm recall 0.528 vs DENSE_BINDOBJ floor 0.423; `block_expand_gain=0.105` but `hp_arms=[]` -- no arm cleared. Sparse block binding on the grounding encoder |
| `exp_grounding_iterative_settling_cascade_depth_v1` | **HARD_FAIL_NO_EXTENSION** | Iterative settling does not extend with depth. The closest prior refutation of `RECOVERY_PROGRAM.md` A8 (cue-clamped iterative cleanup), which that ledger lists as a lead with A8 marked *contested by E11* |
| `exp_substrate_binding_op_x_capacity_v1_seed_{7,13,19}` | **HARD_FAIL x3 seeds** | Binding-operator-by-capacity. A well-replicated negative |
| `exp_agreement_attractor_select_vsa_v1` | **HARD_FAIL** | Attractor-based selection on the agreement competency -- the contractive route tried on a reading task |
| `exp_substrate_sparsity_free_axis_v2_n4096_seed_7` | **HARD_FAIL** | The early sparsity axis. v4/v4b/v5 later PASS; **only reading all four tells you the v2 configuration is the one that fails** |

**How to read this, precisely.** Per the standing anchor that a narrow implementation failure is
not an impossibility proof: these refute **those implementations on those tasks**, and what was
tested is stated above -- DG separation at sparsity 0.05 on 195-way MCScript purity, DG cross-fit
inside a self-play loop, block binding on the grounding encoder at n_seeds 3. **They do not refute
expansive separation as a class**, and note the sharp internal split: DG separation PASSES as pure
geometry (`anisotropy_dg_pattern_separation_prewrite_v1`, effrank 10.08x on real Pythia keys, sec 4
#4) and FAILS as discrimination on a real task, twice. **That split is itself the finding: the
geometry improves and the task does not follow.** Anyone proposing a separation-geometry cell
tonight should state which side of that split their design is on, and why it will land on the
other side of it than these three did.

### 9f. The zero-visibility families -- verdict on each

*Imported verbatim from S6.*
The question asked was: is there anything real in these, or were they invisible because they are
weak? Verdict flavours counted over every stem in the family, and again over FULL runs only.

| family | all stems P/F/M/other | FULL only P/F/M/other | verdict |
|---|---|---|---|
| **k-WTA / sparse** (17/17 invisible, **0 registry rows**) | 14/3/0/0 | 14/3/0/0 | **REAL, but one step off-target.** Every pass is FULL and multi-seed at production N (4096-8192), several with explicit floor keys. But they measure sparsity as a **capacity/free-axis** variable, not as a **separation** variable -- no cell asks whether sparsification separates confusable neighbours. The classic decorrelator is present and has never been pointed at the actual defect |
| **attractor / Hopfield** (12/12 invisible) | 12/0/0/0 | 5/0/0/0 | **REAL and unusually clean -- zero failures anywhere in the family** -- and **entirely the wrong sign**. Hopfield attention inside real LMs at `ppl_ratio` 0.94 (Pythia-160M) and 0.98 (Llama-3.2-1B); dense Hopfield read-out 3.25x on correlated codes -- **but 6.74x mild -> 3.12x moderate -> 1.63x STRONG correlation, i.e. weakest exactly where C3 needs it most.** The family's own gradient is an argument against it for this defect |
| **Hebbian / STDP** (4/4 invisible, **0 registry rows**) | 3/1/0/0 | 2/1/0/0 | **THIN.** Three passes, one of them a `_RESCUE` that HARD_FAILs. This family is small enough that "invisible because weak" is a fair description of it |
| **cleanup / resonator** (51/53 invisible) | 44/1/2/2 | 25/1/2/1 | **REAL AND LARGE, and it splits.** The CONTRACTIVE half (phase diagrams, regime maps, ~50 passes) maps where cleanup works and is the wrong sign. The FACTORIAL half -- resonator verifier / deflation / theta-gamma peel -- is the right sign and is the same mechanism class as the top-ranked peel/SIC lead that has **no `hdlab` module**. The family's most decision-relevant member is a BOUND (harvest = oracle = 0.806), not a lever |
| **binding / conjunctive** (42/49 invisible) | 38/4/5/1 | 22/4/5/1 | **REAL but almost all of it is off-task.** The strong passes are routing and capacity (`cortex_attention_binding_router` v1/v2, CM 0.92-1.00, lift_null +0.67 to +0.75, 3 seeds each, FULL). **Both cells that pointed binding at the actual grounding read-out FAILED** (`sparse_block_binding` HARD_FAIL, `binding_structured_encoder_multihop` INCONCLUSIVE with `reach_delta = -0.33`). Role-filler separability lives in TIER 1 instead, where it wins decisively (sec 4 #1, #3, #5) |
| hippocampus CA3/CA1/DG | 7/5/1/0 | 4/5/0/0 | **The only family with more FULL failures than FULL passes.** See sec 5 |

**Summary answer.** Not weak -- **misaimed**. Four of the five zero-visibility families contain
genuine FULL, floored, multi-seed passes. But k-WTA measured capacity rather than separation;
attractor/Hopfield is contractive and weakens as correlation strengthens; binding won at routing
and lost at grounding; cleanup's large half is contractive and its useful half is a bound. Only
Hebbian/STDP is fairly described as thin. **The pattern is that the right mechanisms were built and
pointed at proxy tasks**, which is a different and more fixable problem than "we have nothing".

### 9g. Every REFUTED row in the chain-graded tier, by name

*Imported from S5 sec 6a. A refutation stops work, so these are listed by name rather than left to
be found in a 565-row table.* **THREE OF THESE TWELVE ARE CORRECTED BY THIS MERGE and are NO LONGER
REFUTED** -- see sec 5.2: `exp_phase_diagram_capacity_multi_bank_k4_envelope_v2c_n8192_gpu` (disk
reads HARD_PASS), `exp_substrate_capacity_multibank_alpha_k_phase_diagram_v2_gpu_seed_7` (disk reads
HARD_PASS on all three seeds), `exp_substrate_stage_a_bio_smoke_b2_sparse_fix_v2` (disk reads
HARD_PASS). A fourth, `exp_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid`, is
reclassified to FOUND because its run refused to start. **Eight of the twelve stand.**
A refutation stops work, so these are listed by name rather than left to be found in a 565-row table. Each is a chain-graded cell whose own verdict is a negative.

| cell | date | verdict as read |
|---|---|---|
| `exp_cross_axis_m_n_k_discriminating_arm_v2_3seed_full_chain_grade_substrate_` | 2026-07-02 | MIDDLE_BAND |
| `exp_n1_concept_lm_substrate_native_token_decode_v3` | 2026-06-21 | HARD_FAIL |
| `exp_phase_diagram_capacity_multi_bank_k4_envelope_v2c_n8192_gpu` | 2026-06-27 | HARD_FAIL |
| `exp_q_b1_depth_extended_n32768` | 2026-06-02 | MIDDLE_BAND |
| `exp_read_discourse_entitygrid_coherence_v1` | 2026-07-17 | MIDDLE_BAND |
| `exp_read_grow_selectional_preference_precision_v2` | 2026-07-17 | HARD_FAIL |
| `exp_substrate_capacity_multibank_alpha_k_phase_diagram_v2_gpu_seed_7` | 2026-06-29 | MIDDLE_BAND |
| `exp_substrate_concept_encoder_spoke1_stress_test_cell1_apples_to_apples_labe` | 2026-07-03 | MIDDLE_BAND |
| `exp_substrate_narrative_partition_oracle_v_c_sweep_v1_smoke` | 2026-06-28 | HARD_FAIL |
| `exp_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed` | 2026-06-28 | HARD_FAIL |
| `exp_substrate_stage_a_bio_smoke_b2_sparse_fix_v2` | UNDATED | HARD_FAIL |
| `exp_theta_gamma_v4_extended_seeds_gpu_7seed_full_chain_grade_lift_of_v3_atom` | 2026-07-01 | MIDDLE_BAND |

---

## 10. COMPACTION SURVIVAL

**Requirement:** a session that has lost all context must find this file and continue correctly
without asking anyone.

### 10a. The mechanism that already works

`tools/session_start_hook.py` runs on every session **start / clear / compact** (wired in
`D:/AI/.claude/settings.json`) and injects `notes/STATUS.md`'s `AS OF:` line and its
`## WHAT IS RUNNING` section, plus the `result-index-join` probe. **The probe is the durable
pointer**: it fires at every compaction and prints the orphan count and the drift alarm, which is
this program's disk-derived metric (sec 7b). No new hook wiring is needed.

### 10b. The STATUS.md stub -- TEXT TO APPLY, NOT APPLIED HERE

**I did not edit `notes/STATUS.md`.** A concurrent agent may be writing it, and `STATUS_SPEC.md`
sec 6 forbids the incidental byte-shave: an agent that came to ADD something is the worst-placed
actor to decide what leaves. **This needs applying by whoever owns the next STATUS.md maintenance
pass.**

Add to the **`## OTHER PATH STATE`** section (it is state, not a lesson, so it belongs in the
capped file's re-derivable half, and it costs 232 bytes):

```
RECOVERY: 974 rows / ~696 distinct investigations in notes/RECOVERY_PROGRAM.md (LIVING, the
two recovery_ledger_* files are MERGED INTO IT -- do not count them too). 30 FOUND / 881
VERIFIED / 1 WIRED / 60 REFUTED. 0 of 968 cells WIRED. Count: grep -oE 'STATE:[A-Z]+'.
```

**Constraints on whoever applies it, all binding:**
- **Do NOT reword `AS OF:` or `## WHAT IS RUNNING`** -- both are parsed by
  `tools/session_start_hook.py` (lines 119 and 124). Rewording them silently degraded every
  compaction recovery once already.
- The cap is **8192 bytes** (`STATUS_SPEC.md` sec 7), and the file measured **8,188 B** on
  2026-08-14 -- **4 bytes of headroom**. This stub does not fit without a trim, and per
  `STATUS_SPEC.md` sec 6 the adder may evict **only from tiers 1-4** (recomputable numbers,
  recoverable paths, finished-work status, emphasis prose) and **must STOP rather than descend into
  sections 5-6**. If tiers 1-4 do not free 232 bytes, hand the trim to a maintenance pass -- do not
  shrink the stub by dropping the count, because the count is the whole point.
- If bytes truly cannot be found, the **minimum viable stub is one line**:
  `RECOVERY LEDGER: notes/RECOVERY_PROGRAM.md (LIVING, 974 rows / ~696 investigations, countable in-file).`

### 10c. If this file is the only thing a cold session has

It is self-sufficient by construction: sec 1 says what happened in plain language, sec 3 defines
the states and their transitions, sec 4 records the runtime measurement and the exact command that
reproduces it, sec 5 carries every evidence path, sec 6 states every unexamined tier **with its
size**, sec 7 gives the two progress commands, sec 9 gives the rule and the ranking. **No claim
here depends on a number held only in a session's memory.**

### 10d. Update protocol -- so this file does not rot the way its six predecessors did

The measured failure mode (S3) is that **each review started over rather than extending the last**,
because every rename changed the unit of account (`cycle number -> PP capability -> hdlab module ->
WIRE/SHELVE gate -> brain component -> brain organ`). Anything that did not map onto the new unit
silently vanished.

1. **Unit of account is frozen: one row = one RECOVERED SYSTEM.** Not a cell, not a module, not an
   organ. A system may be an experiment, a module, a data asset, or an index -- and each row says
   which it is in the `module` column. **Do not re-key this ledger.**
2. **Edit rows IN PLACE.** Change the STATE word and append the evidence. Never delete a row: a
   REFUTED row is the cheapest thing in this file and the most expensive to re-learn.
3. **Never let a tier in sec 6 look examined.** Move counts between "triaged" and
   "NOT-YET-TRIAGED"; never delete the row when it hits zero -- record the zero.
4. **A corrected claim gets struck in place, not quietly fixed.** Twenty-one further corrections
   landed with the 2026-08-14 merge and are indexed in sec 5.2, nineteen of them UPWARD -- a
   result restored is the same discipline as a result deflated. Four corrections were already
   embedded (C9 `grid` not full; C10 `lite` not full; C16 is a `HARD_FAIL`; E3 is a PASS not a
   refutation) plus one name correction (C6) and one registry correction (F9, 8 of 24 now
   registered). That visible-correction habit is the difference between a ledger and a brochure.
5. **When you supersede this document, the successor must carry every row forward or say why not.**
   That sentence is the entire lesson of the six-rename lineage.


---

## 11. CORRECTIONS OF 2026-08-14 LATE THAT TOUCH ROWS IN THIS FILE

Four corrections landed after both source ledgers were written. Each one changes how a row in sec 5
must be READ; none of them changes a STATE word, because none is backed by a fresh measurement of
the row's own artifact. **They are recorded here rather than silently applied.**

**1. DO-NOT-REDO 18 ("role-bound structure alone") is NOT REFUTED -- it is UNTESTED WITH A WORKING
RULER.** It was closed on the judgement of instruments that have since been ruled invalid. The rows
it touches are the role-filler factorisation family in group R -- `exp_role_filler_factorization_compgen_v1`
(FACTORED held-out **1.000** vs FLAT **0.003**, gap 0.997, `must_fail=True`),
`exp_role_filler_factorization_reader_coupled_cg_v1` (REAL F=0.823 vs FLAT 0.005),
`exp_resonator_decision_compgen_2factor_v1` (RES 1.000 vs FLATjoint 0.180) -- plus
`exp_role_filler_factorization_conceptnet_cg_v1` and `..._assembled_reading_axis_v1`.
**Read those rows as OPEN, not as closed by DO-NOT-REDO 18.** They are also, on the source sweep's
own ranking, positions 1, 3 and 5 of the entire reading tier.

**2. DG / pattern separation (DO-NOT-REDO 32) is NOT REFUTED -- same reason: judged by instruments
since ruled invalid, UNTESTED WITH A WORKING RULER.** The rows: `A5`
(`exp_substrate_anisotropy_dg_pattern_separation_prewrite_v1`, `dg_full 0.942` vs bar 0.50, effrank
lift **10.08x** on real Pythia-2.8b keys, `uniform_no_presep` collapses to 0.083) and the two
task-level HARD_FAILs in group M (`exp_dg_pattern_separation_mcscript_purity_v1`,
`exp_selfplay_dg_pattern_separation_xfit_v1`). **The internal split is the finding and it stands:
DG PASSES as pure geometry and FAILS as discrimination on a real task.** What is withdrawn is the
inference that the failures CLOSE the route. Note also **merge correction CG-B142**, restored from
REFUTED to VERIFIED this session: *"DG sparse expansion gives >=10x capacity ... ratio=48.0x"*,
run_mode full -- a third DG-family PASS that was being carried as a failure.

**3. The graded switch is NULL on C3 (DO-NOT-REDO 34).** The rows: group M `M25`
(`exp_graded_divisive_comparator_v1`) and its `_SMOKE_n600` / `_SELFTEST` siblings `M57` / `M58`.
The source sweep ranked M25 ninth and called it "the only row in either tier that is WIRED".
**Both halves need correcting.** It is not WIRED by this file's sec-3 definition (no runtime
closure observation was made -- the sweep says so itself), and flipping the switch for a C3 gain is
a **MEASURED NULL**: `+0.0015, CI [-0.0055, +0.0083]` in C3 currency.

**4. `+0.0602` is a 2AFC number and is the WRONG CURRENCY for C3 (DO-NOT-REDO 35).** Same rows.
`0.6395 -> 0.6997, d=0.0602 CI [0.0440, 0.0762]` is a two-alternative forced-choice margin against
a chance of 0.50 over a pool of 2,377. **C3 is open-vocabulary hit@1 against a 5,491-anchor pool.**
The two are not convertible and the 2AFC number must never be quoted as a C3 movement. Anywhere
`0.6395`, `0.6980`, `0.6997` or `0.0602` appears in a row in sec 5, it is a 2AFC figure.

**How these four interact with the rest of the file.** Corrections 1 and 2 REOPEN routes that sec
9's ranking treats as live leads, so they raise, not lower, the value of groups R and A. Corrections
3 and 4 remove a claimed win, and the honest consequence is that **this file still contains zero
WIRED capabilities** -- the one row that looked like an exception is not one.

---


## APPENDIX A -- the `cross_layer_composition` / `pp48_nkt` saturation grid (279 rows)

**This is ONE investigation, not 279.** An auto-generated grid reporting EXACT-1.0 at every level,
with no comparison arm because the result is construction-determined. It is half the chain-graded
tier by row count and it is filed here, out of the body, so that it cannot inflate a skim of sec 5.
Every row keeps its STATE token and is counted in sec 7a -- the deflation is stated, not applied by
deletion.

One row in the source group was NOT part of the grid and has been left here with it:
`exp_q_a3_l19_n_scale_v1_n8192` (row E95) is an `n_scale` cell, not a `cross_layer_composition`
cell. That is why the grid is 279 rows inside a 280-row group.


**280 of 565 cells in the whole tier.** One auto-generated experiment, run at every level of a grid, each level banked as its own chain-graded atom reporting EXACT-1.0. There is no comparison arm because the result is construction-determined; the source note reaches the same conclusion and it is correct. **These are constructions, not capability wins, and they are the single largest distortion in any count of "how much chain-graded work exists".** Rows are written so the tier can never look examined-but-uncounted; nobody should read them individually.

| # | cell | date (src) | verdict (as read) | run_mode | floor | disk | module | moves | STATE |
|---|---|---|---|---|---|---|---|---|---|
| E1 | `exp_pp48_nkt_cross_n_depth13_v1_n8192` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E2 | `exp_pp48_nkt_cross_n_depth17_v1_n8192` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E3 | `exp_pp48_nkt_cross_n_depth19_v1_n16384` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E4 | `exp_pp48_nkt_cross_n_depth19_v1_n8192` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E5 | `exp_pp48_nkt_depth_11_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E6 | `exp_pp48_nkt_depth_13_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E7 | `exp_pp48_nkt_depth_15_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E8 | `exp_pp48_nkt_depth_17_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E9 | `exp_pp48_nkt_depth_19_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E10 | `exp_pp48_nkt_depth_21_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E11 | `exp_pp48_nkt_depth_23_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E12 | `exp_pp48_nkt_depth_3_baseline_verification_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | A | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E13 | `exp_pp48_nkt_depth_5_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E14 | `exp_pp48_nkt_depth_7_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E15 | `exp_pp48_nkt_depth_9_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E16 | `exp_q_a3_l10000_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E17 | `exp_q_a3_l1000_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E18 | `exp_q_a3_l1000_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E19 | `exp_q_a3_l100_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E20 | `exp_q_a3_l100_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E21 | `exp_q_a3_l101_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E22 | `exp_q_a3_l101_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E23 | `exp_q_a3_l102_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E24 | `exp_q_a3_l102_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E25 | `exp_q_a3_l103_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E26 | `exp_q_a3_l103_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E27 | `exp_q_a3_l104_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E28 | `exp_q_a3_l104_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E29 | `exp_q_a3_l105_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E30 | `exp_q_a3_l105_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E31 | `exp_q_a3_l106_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E32 | `exp_q_a3_l106_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E33 | `exp_q_a3_l107_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E34 | `exp_q_a3_l107_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E35 | `exp_q_a3_l108_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E36 | `exp_q_a3_l109_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E37 | `exp_q_a3_l10_cross_layer_composition_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E38 | `exp_q_a3_l110_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E39 | `exp_q_a3_l111_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E40 | `exp_q_a3_l112_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E41 | `exp_q_a3_l113_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E42 | `exp_q_a3_l114_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E43 | `exp_q_a3_l115_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E44 | `exp_q_a3_l116_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E45 | `exp_q_a3_l117_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E46 | `exp_q_a3_l118_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E47 | `exp_q_a3_l119_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E48 | `exp_q_a3_l11_cross_layer_composition_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E49 | `exp_q_a3_l120_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E50 | `exp_q_a3_l121_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E51 | `exp_q_a3_l122_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E52 | `exp_q_a3_l123_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E53 | `exp_q_a3_l124_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E54 | `exp_q_a3_l125_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E55 | `exp_q_a3_l126_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E56 | `exp_q_a3_l127_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E57 | `exp_q_a3_l128_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E58 | `exp_q_a3_l129_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E59 | `exp_q_a3_l12_cross_layer_composition_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E60 | `exp_q_a3_l130_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E61 | `exp_q_a3_l131_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E62 | `exp_q_a3_l132_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E63 | `exp_q_a3_l133_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E64 | `exp_q_a3_l134_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E65 | `exp_q_a3_l135_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E66 | `exp_q_a3_l136_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E67 | `exp_q_a3_l137_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E68 | `exp_q_a3_l138_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E69 | `exp_q_a3_l139_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E70 | `exp_q_a3_l13_cross_layer_composition_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E71 | `exp_q_a3_l140_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E72 | `exp_q_a3_l141_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E73 | `exp_q_a3_l142_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E74 | `exp_q_a3_l143_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E75 | `exp_q_a3_l144_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E76 | `exp_q_a3_l145_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E77 | `exp_q_a3_l146_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E78 | `exp_q_a3_l147_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E79 | `exp_q_a3_l148_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E80 | `exp_q_a3_l149_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E81 | `exp_q_a3_l14_cross_layer_composition_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E82 | `exp_q_a3_l1500_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E83 | `exp_q_a3_l150_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E84 | `exp_q_a3_l151_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E85 | `exp_q_a3_l152_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E86 | `exp_q_a3_l153_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E87 | `exp_q_a3_l154_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E88 | `exp_q_a3_l155_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E89 | `exp_q_a3_l156_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E90 | `exp_q_a3_l15_cross_layer_composition_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E91 | `exp_q_a3_l16_cross_layer_composition_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E92 | `exp_q_a3_l17_cross_layer_composition_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E93 | `exp_q_a3_l18_cross_layer_composition_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E94 | `exp_q_a3_l19_cross_layer_composition_v1_n4096` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E95 | `exp_q_a3_l19_n_scale_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E96 | `exp_q_a3_l2000_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E97 | `exp_q_a3_l200_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E98 | `exp_q_a3_l200_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E99 | `exp_q_a3_l20_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E100 | `exp_q_a3_l20_cross_layer_composition_v1_n4096` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E101 | `exp_q_a3_l21_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E102 | `exp_q_a3_l21_cross_layer_composition_v1_n4096` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E103 | `exp_q_a3_l22_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E104 | `exp_q_a3_l22_cross_layer_composition_v1_n4096` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E105 | `exp_q_a3_l22_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E106 | `exp_q_a3_l23_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E107 | `exp_q_a3_l23_cross_layer_composition_v1_n4096` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E108 | `exp_q_a3_l23_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E109 | `exp_q_a3_l24_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E110 | `exp_q_a3_l24_cross_layer_composition_v1_n4096` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E111 | `exp_q_a3_l24_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E112 | `exp_q_a3_l25_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E113 | `exp_q_a3_l25_cross_layer_composition_v1_n4096` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E114 | `exp_q_a3_l25_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E115 | `exp_q_a3_l26_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E116 | `exp_q_a3_l26_cross_layer_composition_v1_n4096` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E117 | `exp_q_a3_l26_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E118 | `exp_q_a3_l27_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E119 | `exp_q_a3_l27_cross_layer_composition_v1_n4096` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E120 | `exp_q_a3_l27_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E121 | `exp_q_a3_l28_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E122 | `exp_q_a3_l28_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E123 | `exp_q_a3_l29_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E124 | `exp_q_a3_l29_cross_layer_composition_v1_n4096` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E125 | `exp_q_a3_l29_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E126 | `exp_q_a3_l300_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E127 | `exp_q_a3_l300_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E128 | `exp_q_a3_l30_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E129 | `exp_q_a3_l30_cross_layer_composition_v1_n4096` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E130 | `exp_q_a3_l30_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E131 | `exp_q_a3_l31_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E132 | `exp_q_a3_l31_cross_layer_composition_v1_n4096` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E133 | `exp_q_a3_l31_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E134 | `exp_q_a3_l32_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E135 | `exp_q_a3_l32_cross_layer_composition_v1_n4096` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E136 | `exp_q_a3_l32_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E137 | `exp_q_a3_l33_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E138 | `exp_q_a3_l33_cross_layer_composition_v1_n4096` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E139 | `exp_q_a3_l33_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E140 | `exp_q_a3_l34_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E141 | `exp_q_a3_l34_cross_layer_composition_v1_n4096` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E142 | `exp_q_a3_l34_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E143 | `exp_q_a3_l35_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E144 | `exp_q_a3_l35_cross_layer_composition_v1_n4096` | 2026-06-03 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E145 | `exp_q_a3_l35_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E146 | `exp_q_a3_l36_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E147 | `exp_q_a3_l36_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E148 | `exp_q_a3_l37_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E149 | `exp_q_a3_l37_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E150 | `exp_q_a3_l38_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E151 | `exp_q_a3_l38_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E152 | `exp_q_a3_l39_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E153 | `exp_q_a3_l39_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E154 | `exp_q_a3_l400_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E155 | `exp_q_a3_l40_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E156 | `exp_q_a3_l40_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E157 | `exp_q_a3_l41_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E158 | `exp_q_a3_l41_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E159 | `exp_q_a3_l42_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E160 | `exp_q_a3_l42_cross_layer_composition_v1_n8192` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E161 | `exp_q_a3_l43_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E162 | `exp_q_a3_l43_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E163 | `exp_q_a3_l44_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E164 | `exp_q_a3_l44_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E165 | `exp_q_a3_l45_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E166 | `exp_q_a3_l45_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E167 | `exp_q_a3_l46_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E168 | `exp_q_a3_l46_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E169 | `exp_q_a3_l47_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E170 | `exp_q_a3_l47_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E171 | `exp_q_a3_l48_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E172 | `exp_q_a3_l48_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E173 | `exp_q_a3_l49_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E174 | `exp_q_a3_l49_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E175 | `exp_q_a3_l500_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E176 | `exp_q_a3_l500_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E177 | `exp_q_a3_l50_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E178 | `exp_q_a3_l50_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E179 | `exp_q_a3_l51_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E180 | `exp_q_a3_l51_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E181 | `exp_q_a3_l52_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E182 | `exp_q_a3_l52_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E183 | `exp_q_a3_l53_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E184 | `exp_q_a3_l53_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E185 | `exp_q_a3_l54_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E186 | `exp_q_a3_l54_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E187 | `exp_q_a3_l55_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E188 | `exp_q_a3_l55_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E189 | `exp_q_a3_l56_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E190 | `exp_q_a3_l56_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E191 | `exp_q_a3_l57_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E192 | `exp_q_a3_l57_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E193 | `exp_q_a3_l58_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E194 | `exp_q_a3_l58_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E195 | `exp_q_a3_l59_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E196 | `exp_q_a3_l59_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E197 | `exp_q_a3_l5_cross_layer_composition_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E198 | `exp_q_a3_l60_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E199 | `exp_q_a3_l60_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E200 | `exp_q_a3_l61_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E201 | `exp_q_a3_l61_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E202 | `exp_q_a3_l62_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E203 | `exp_q_a3_l62_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E204 | `exp_q_a3_l63_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E205 | `exp_q_a3_l63_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E206 | `exp_q_a3_l64_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E207 | `exp_q_a3_l64_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E208 | `exp_q_a3_l65_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E209 | `exp_q_a3_l65_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E210 | `exp_q_a3_l66_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E211 | `exp_q_a3_l66_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E212 | `exp_q_a3_l67_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E213 | `exp_q_a3_l67_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E214 | `exp_q_a3_l68_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E215 | `exp_q_a3_l68_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E216 | `exp_q_a3_l69_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E217 | `exp_q_a3_l69_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E218 | `exp_q_a3_l6_cross_layer_composition_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E219 | `exp_q_a3_l700_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E220 | `exp_q_a3_l70_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E221 | `exp_q_a3_l70_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E222 | `exp_q_a3_l71_cross_layer_composition_v1_n16384` | 2026-06-03 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E223 | `exp_q_a3_l71_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E224 | `exp_q_a3_l72_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E225 | `exp_q_a3_l72_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E226 | `exp_q_a3_l73_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E227 | `exp_q_a3_l73_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E228 | `exp_q_a3_l74_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E229 | `exp_q_a3_l74_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E230 | `exp_q_a3_l75_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E231 | `exp_q_a3_l75_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E232 | `exp_q_a3_l76_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E233 | `exp_q_a3_l76_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E234 | `exp_q_a3_l77_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E235 | `exp_q_a3_l77_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E236 | `exp_q_a3_l78_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E237 | `exp_q_a3_l78_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E238 | `exp_q_a3_l79_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E239 | `exp_q_a3_l79_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E240 | `exp_q_a3_l7_cross_layer_composition_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E241 | `exp_q_a3_l80_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E242 | `exp_q_a3_l80_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E243 | `exp_q_a3_l81_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E244 | `exp_q_a3_l81_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E245 | `exp_q_a3_l82_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E246 | `exp_q_a3_l82_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E247 | `exp_q_a3_l83_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E248 | `exp_q_a3_l83_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E249 | `exp_q_a3_l84_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E250 | `exp_q_a3_l84_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E251 | `exp_q_a3_l85_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E252 | `exp_q_a3_l85_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E253 | `exp_q_a3_l86_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E254 | `exp_q_a3_l86_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E255 | `exp_q_a3_l87_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E256 | `exp_q_a3_l87_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E257 | `exp_q_a3_l88_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E258 | `exp_q_a3_l88_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E259 | `exp_q_a3_l89_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E260 | `exp_q_a3_l89_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E261 | `exp_q_a3_l8_cross_layer_composition_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E262 | `exp_q_a3_l90_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E263 | `exp_q_a3_l90_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E264 | `exp_q_a3_l91_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E265 | `exp_q_a3_l91_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E266 | `exp_q_a3_l92_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E267 | `exp_q_a3_l92_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E268 | `exp_q_a3_l93_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E269 | `exp_q_a3_l93_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E270 | `exp_q_a3_l94_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E271 | `exp_q_a3_l95_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E272 | `exp_q_a3_l96_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E273 | `exp_q_a3_l96_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E274 | `exp_q_a3_l97_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E275 | `exp_q_a3_l97_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E276 | `exp_q_a3_l98_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E277 | `exp_q_a3_l98_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E278 | `exp_q_a3_l99_cross_layer_composition_v1_n16384` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E279 | `exp_q_a3_l99_cross_layer_composition_v1_n8192` | 2026-06-04 (git-first-commit) | HARD_PASS | full | NO FLOOR | OK | EXP-ONLY | -- | STATE:VERIFIED |
| E280 | `exp_q_a3_l9_cross_layer_composition_v1_n4096` | 2026-06-02 (git-first-commit) | HARD_PASS | full | CONTRAST-ONLY | OK | EXP-ONLY | -- | STATE:VERIFIED |
