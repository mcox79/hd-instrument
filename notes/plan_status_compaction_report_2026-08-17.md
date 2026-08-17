# PLAN / STATUS COMPACTION-PREP REPORT -- 2026-08-17

**Written by an audit-only pass at HEAD `daad41b48`, branch `dataprep/mcguffey-graded-corpus`.**
Scope: this pass rewrote `notes/STATUS.md` and `notes/PLAN_NEXT_24H.md`, appended to
`notes/STATUS_LESSONS.md` and `notes/STATUS_SPEC.md`, and folded four items into
`C:\Users\marsh\.claude\projects\D--AI\memory\MEMORY.md`. **It authored no experiment cell, ran no
cell, spawned no subagent, signalled no process, and demoted or re-labelled nothing.**

Written to `notes/` deliberately: `.claude/scan-out/` refuses file creation (four attempts by other
actors tonight). This file is the report; it is not a fragment.

---

## 1. VERIFICATION TABLE -- EVERY NUMBER THIS PASS USED, AND HOW IT WAS ESTABLISHED

Three classes, never merged: **RECOMPUTED** (this pass opened the artifact and re-derived the number
with `.venv` python), **READ ON DISK** (the artifact records it directly and this pass read the
field), **AGENT MEASUREMENT** (exists only in another actor's fragment; attributed, not adopted).

| figure | value | class | artifact |
|---|---|---|---|
| circular WordNet oracle, exact key | **0.8787** | READ ON DISK | `data/exp_foundation_neighbourhood_purity_v1/metrics.json`, `THE_CURVE...` row `F30_ORACLE_WORDNET_CIRCULAR_rho0.70` |
| same oracle, partial cue | **0.0365** | READ ON DISK | same row; **RECOMPUTED as the MAXIMUM `B_PARTIAL_CUE` over all 47 foundations** |
| partial-cue range across 47 foundations | 0.0064-0.0365 (42 non-null) | RECOMPUTED | same file |
| exact-key range / span | 0.0129-0.8787 = **68.1x** | RECOMPUTED | same file |
| purity -> exact-key retrieval | **rho 0.961** (n=45) | READ ON DISK | `DOES_RETRIEVAL_TRACK_PURITY.B_EXACT_KEY_NATIVE` |
| purity -> partial-cue retrieval | **rho -0.0167** (n=40) | READ ON DISK | `DOES_RETRIEVAL_TRACK_PURITY.B_PARTIAL_CUE` |
| known-answer arms across the grid | **KA 0.9807-1.0000**, 47/47 | RECOMPUTED (min/max) | same file |
| two-stage cue, best | 0.0322 (`F22_FUSE_FASTTEXT_w1.00`) vs incumbent 0.0225 | RECOMPUTED | same file |
| addressing, exact key / partial cue | **1.0000 / 0.0325** | READ ON DISK | `data/exp_cue_to_store_translation_v1/metrics.json`, `A8_MECHANISM_DIAGNOSTICS` |
| partial cue's cosine to its own stored row | **0.1621** | READ ON DISK | same file, `FITTED_MAPS/PARTIAL_CUE` |
| read-out hit@1 vs trigram-only floor | **0.0480 vs 0.0870** (prefix 0.0588), n=4000 items / 5491 anchors | READ ON DISK | `data/exp_orthographic_floor_vet_v1/metrics.json`, `per_arm` |
| bridging B1, FULL | **rho 0.0270 [-0.0737,+0.1251]**, n=394, NOT_SEPARATED, perm p **0.3048** | READ ON DISK | `data/exp_thematic_relation_supply_bridged_grounding_v2/metrics.json` |
| its floors on the identical stratum | ortho 0.0412 / freq 0.0317 / scramble-p95 0.0905 | READ ON DISK | same block |
| its known-answer arms | K1 **0.3301** ABOVE, K2_ORACLE **0.2893** ABOVE | READ ON DISK | same block |
| bridged identity / meaning | distinct **0.9612** / retention **0.0819** | READ ON DISK | same block, `IDENTITY`, `RETENTION_vs_K1` |
| **verb stratum, known-answer arm** | n=**86**, rho 0.2576 [0.0401,0.4524], floor **0.1776**, margin **+0.0801 NOT_SEPARATED** | READ ON DISK | same file, `HILLS_2009_NOUN_VERB_FALSIFIER.known_answer_K1.V` |
| that floor vs the null width at n=86 | 0.1776-0.1814 vs **1.645/sqrt(85) = 0.1784** | RECOMPUTED (arithmetic) | -- |
| SimLex verb pairs available | **222** (N 666, A 111) | RECOMPUTED (counted the file) | `data/encoder_eval_benchmarks/simlex999.txt` |
| constant floor on the bridging stratum | **-0.1959** (optimistic tie; midrank -0.1977) | **AGENT MEASUREMENT** | `.claude/scan-out/collect-completed-runs.json`, script `.claude/scan-out/constfloor/const_floor_bridging.py` |
| constant floor on the selectional stratum | **-0.2253** | READ ON DISK (independent instance of the same effect) | `data/exp_selectional_constraint_bridge_v1/metrics.json`, `floors.F_CONSTANT_PROTOTYPE` |
| corpus bar base rate | **1 of 7,789** MEETS_BAR (`exp_cue_to_store_translation_v1`); FAILS 7,770; NO_EVIDENCE 18 | READ ON DISK | `data/verdict_bar_reports/verdict-bar-20260817T002627Z.json` |
| constant-floor coverage | **12 of 7,789** cells ever recorded one | READ ON DISK | same report |
| cleanup lift over no-cleanup, partial cue | P1_OPEN **+0.0033 [+0.0013,+0.0055] ABOVE**; K49 **+0.0078 [+0.0008,+0.0150] ABOVE**; K15 +0.0046 NOT_SEPARATED | READ ON DISK | `data/exp_cleanup_memory_capability_v1/metrics.json`, `LADDER_vs_A0_NO_CLEANUP_tie_corrected` |
| best cleanup arm vs the binding floor | **-0.1135 [-0.1249,-0.1019] BELOW** the constant floor 0.1390 (open pool) | READ ON DISK + RECOMPUTED (0.0255-0.1390) | same file |
| cleanup organ is not inert | fixed points **1.0000**, idempotent, `d/log d` capacity scale 46.17 | READ ON DISK | same file, `PART_A_ORGAN...FIXED_POINT` |
| sparse-address grid, best partial-cue addressing | **0.0719 [0.0638,0.0796]** at D=2048, **DENSE** address | RECOMPUTED (max over grid) | `data/exp_sparse_address_dense_value_v1/metrics.json` |
| sparse address at 1% with a dense read | **0.0699 [0.0621,0.0779]** at D=8192, 82 of 8192 units active | READ ON DISK | same file |
| the same config read symmetrically | 0.0483 [0.0418,0.0548] -- **1.45x worse** | RECOMPUTED | same file |
| write/read asymmetry, direction | dense read beats symmetric-sparse read in **18 of 24** matched pairs, max **6.27x**, worst 0.99x | **RECOMPUTED** | same file |
| surprise signal degeneracy | median **0.875**, mean 0.853, p90 1.0128 (sampled n=368) | READ ON DISK | `data/exp_surprise_weighted_update_v1/metrics.json`, `ARM_DIAGNOSTICS` |
| surprise selection vs token-matched random subset | **T2 beats C1 in 4 of 18 point comparisons**, best margin +0.0035 | **RECOMPUTED** | same file |
| residual rule vs uniform rule | `mean_cos_to_A0_rows` **0.9771** at every eta -> the pre-registered BOOTSTRAPPING null cause fired | READ ON DISK | same file |
| **selectional-constraint bridge, FULL, LANDED** | verdict `SELECTIONAL_CONSTRAINT_BRIDGE_DOES_NOT_CLEAR_THE_FLOOR`, elapsed 5330 s | READ ON DISK | `data/exp_selectional_constraint_bridge_v1/metrics.json`, mtime 2026-08-17T00:32 |
| its head-to-head vs neighbour-copy | **-0.1049 [-0.2041,-0.0057] BELOW**, n=308 | READ ON DISK | same file, `HEAD_TO_HEAD_S1_minus_I1` |
| its own known-answer arm | K1 rho **0.3311** on the same stratum | READ ON DISK | same file, `RETENTION.rho_K1` |
| selectional vs random-target null | **-0.0015 NOT_SEPARATED** | READ ON DISK | same file, `VS_NULL` |
| MEMORY.md size before / after | 18,227 B -> see section 5 | RECOMPUTED (`wc -c`) | -- |
| STATUS.md size before / after | 9,725 B -> see section 2 | RECOMPUTED (`wc -c`) | -- |

### 1a. NUMBERS IN THE HANDOFF THAT THIS PASS COULD NOT REPRODUCE AS STATED -- LEFT OUT

Both are **directionally confirmed** and **numerically unreproduced**. Neither is used in STATUS,
the plan or MEMORY in the handoff's form; the recomputed form is used instead.

1. **"the asymmetry wins 9 of 9 matched pairs by 1.4x to 6.3x."** Under this pass's pairing rule
   (same regime, D, `a_write`, code type and projection seed; symmetric read vs dense read; sparse
   writes only) there are **24** matched pairs, not 9, and the dense read wins **18**, ties 5 and
   loses 1 (0.99x). The **6.27x maximum reproduces exactly**; the **1.4x lower bound does not** --
   it is the bound of a subset this pass could not identify. **STATUS and the plan carry the
   18-of-24 / 6.27x form.**
2. **"selection never beats a token-matched random subset in 11 of 12 comparisons."** The cell has
   **18** T2-vs-C1 point comparisons (6 conditions x 3 selection rates). Selection loses or ties
   **14 of 18** and its four wins are at most +0.0035. **The claim's direction is confirmed and its
   count is not; the plan carries 4-of-18.**

---

## 2. JOB 1 -- `notes/STATUS.md`

**Rewritten in place. 9,725 B -> 11,571 B, 140 lines.** Header now reads
`AS OF: 2026-08-17 | branch dataprep/mcguffey-graded-corpus | HEAD daad41b48` (the previous header
was stale at `03055c7fa`).

**The four machine-parsed literals are BYTE-IDENTICAL and were never reworded:** `AS OF:` (colon
present), `## POSITION`, `## TOP ITEM`, `## WHAT IS RUNNING`.

**Hook self-test, run after the rewrite:**
`.venv/Scripts/python.exe tools/session_start_hook.py --self-test` -> **ALL PASS, exit 0**, 10 of 10
checks, including the one that matters here: *"PASS: the real notes/STATUS.md parses clean (no
false-positive banner)"*. `tools/board.py self-test` was NOT run, because `board.py` writes into
`notes/BOARD.md`, which is on this pass's do-not-touch list; its four literals are the same four and
all are present.

**CHAIN now reads:** `COMPACTION_HANDOFF_2026-08-17.md` -> `STATUS.md` -> `PLAN_NEXT_24H.md` ->
`LONG_TERM_PLAN.md`. The handoff is first, as instructed.

**What changed in substance:** POSITION is now the partial-cue structural cap (it was the
spelling-floor/two-gaps framing); TOP ITEM is the cap's diagnosis (it was the affect channel);
BRIDGING carries the SECOND null; STORAGE carries the write/read asymmetry; TOOLING carries the
corrected bar base rate. Four never-trim entries were ADDED (DO-NOT-REDO 43, C32-C34, discipline 14)
and **not one existing DO-NOT-REDO entry, caveat, correction or discipline was dropped, merged or
reworded away.** Their full reasoning was appended to `notes/STATUS_LESSONS.md` (+14 KB) so STATUS
carries only stubs, per the spec's escalation step 1.

**The cap, measured and NOT enacted.** 11,571 B against the 8,704 B cap = **2,867 B over**:

| section | bytes | budget | over/under |
|---|---|---|---|
| header | 493 | 450 | +43 |
| `## POSITION` | 509 | 450 | +59 |
| `## TOP ITEM` | 805 | 900 | **-95** |
| PATH STATE (4 subsections) | 3,094 | 3,100 | **-6** |
| `## DO NOT REDO` (+ caveats + corrections) | 3,109 | 1,000 | **+2,109** |
| `## STANDING DISCIPLINES` | 2,011 | 1,400 | **+611** |
| `## WHAT IS RUNNING` | 1,550 | 650 | **+900** |

**5,120 B of the file is never-trim stubs against a 2,400 B allowance, and every other section is at
or under budget.** The overage is disclosed in STATUS's own `## WHAT IS RUNNING` section, as the
spec requires. **A new subsection was appended to `notes/STATUS_SPEC.md` sec 7 recording the
measurement and TWO options, NEITHER ENACTED and the cap literal untouched:**

1. raise to **12,288 B** (the 2026-08-16 proposal of 9,216 B is now insufficient); or
2. **RECOMMENDED and needing NO raise: move the DO-NOT-REDO / CAVEATS / CORRECTIONS stub index into
   an uncapped `notes/STATUS_CLOSED.md` and leave a pointer.** Measured: 11,571 - 3,109 + ~120 =
   **~8,580 B, UNDER the existing cap**, nothing deleted, nothing demoted, one extra cold read. It
   is the same structural argument that justified splitting `STATUS_LESSONS.md` off, applied one
   level up, and it bounds `STATUS.md` permanently.

**No never-trim entry was evicted to close the gap, and this pass did not grant itself the raise.**

## 3. JOB 2 -- `notes/PLAN_NEXT_24H.md`

**A HAZARD FOUND AND FIXED BEFORE ANY WRITING: the file was UNTRACKED in git.** Rewriting it in
place would have destroyed the 2026-08-16 version (92,629 B, 14 items) with no history to recover it
from. It was committed unchanged first, by explicit path, at **`da678875c`** -- so the supersession
is auditable and the superseded spec is still citable. The new file's header says so, and section 5
points every parked item back at that commit.

**Rewritten around the handoff's section 9, three items, sequenced by what blocks what:**

| item | question | floor | stop-if | runner | dependency |
|---|---|---|---|---|---|
| **1 diagnose the partial-cue cap** | is the answer in the cue AT ALL, before our machinery compresses it? `U0_UNCOMPRESSED` vs `C0_PROJECTED_256`, one variable | size-matched random-key control CI-separated for addressing; `max(four floors)` on its OWN population for hit@1; both tie conventions; CI half-width + null p95 beside every margin | U0 also lands near the incumbent -> **the information is not in the cue**, ITEM 3's capability claim is void and the programme redirects to the WRITE side. Report loudly | `cpu_runner_local` | none. **Blocks item 3's capability half** |
| **2 re-measure verbs at n=222** | can the EXISTING 12-dim space order verbs when a known-answer arm is handed the answer, at an n that can separate? | `max(four floors)` recomputed on the 222-pair population; report the CI half-width and the scramble p95 (null width ~0.1107 at n=222 vs 0.1784 at n=86) | K1 clears -> retraction 2 confirmed, no channel may cite it. K1 fails with the width now ~0.11 -> the claim is MEASURED and a channel build is licensed. p95 still of the same order as the margin -> `POWER_INSUFFICIENT AT EVERY AVAILABLE n` | `cpu_runner_local` | none |
| **3 sparse address / dense value PER ORGAN** | does a sparse expanded ADDRESS on a DENSE graded VALUE, with `a_write` != `a_read`, beat the flat store under a partial cue? | `max(four floors)` on its own population, **on the partial cue**, both tie conventions, between-projection-draw SD beside every CI | T1 ties A0 with K1 passing -> the address is the limit; C1_SPARSE_BOTH matches T1 -> the key/value split is refuted for our geometry; **whole sweep <= the measured ~0.072 ceiling -> it bought EFFICIENCY, not capability, and must be reported in those words** | local smoke, `cpu_runner_0` full, `gpu_runner_0` only at D=8192 | **capability half HARD-blocked by item 1; efficiency half NOT blocked** |

Each item also carries its brain structure with the replicate-or-substitute call made explicitly --
including ITEM 1's honest **"none is claimed and none should be fabricated; this is an information
audit of our own encoder"**, which is the answer the fidelity gate wants when there is no anatomy.

**Nothing from the superseded plan was dropped silently.** Section 5 parks eleven items with a
one-line reason and a pointer to `da678875c`; section 6 carries the five standing operator decisions
forward unchanged; section 9 reports the four things in `notes/LONG_TERM_PLAN.md` that are now stale
**without editing that file**, headed by its Phase 2 kill condition having FIRED.

## 4. JOB 3 -- THE RETRACTIONS

Recorded in **three places**, each as a dated correction preserving the superseded claim with a
superseded-by line, never a silent rewrite:

- `notes/PLAN_NEXT_24H.md` **section 0**, in full, before anything else in the document;
- `notes/STATUS.md` **CORRECTIONS C32-C34** (stub form, never-trim);
- `notes/STATUS_LESSONS.md` **2026-08-17 additions** (full reasoning + evidence).

**The error pattern leads in all three, as instructed:** *the Director read an UNDERPOWERED NULL as
a CAPABILITY STATEMENT three separate times.* The three retracted claims are: "0 of 7,769 banked
cells meet the bar" (-> 1 of 7,789, survivor itself rejected on four grounds); "our instrument
cannot resolve verbs even when handed the right answer" (SUSPENDED -- at n=86 the floor 0.1776 was
the null distribution's own width, 1.645/sqrt(85) = 0.1784, RECOMPUTED); and "the constant floor is
the binding one" (FALSE in general -- -0.1959 on the bridging stratum, -0.2253 on the selectional
one, the WEAKEST of the four in both).

**The standing rule is now in both required places:** `notes/PLAN_NEXT_24H.md` standing rule 3 and
`notes/STATUS.md` STANDING DISCIPLINE 14 (never-trim), and `MEMORY.md`'s measurement-bar entry as
rule (5): **report the CI half-width and the null p95 at that n beside every margin; a width is not
an effect.**

**One genuinely new result was found while verifying, and it is the session's most consequential
unread finding:** `data/exp_selectional_constraint_bridge_v1/metrics.json` has **LANDED** as a
complete FULL. The owner's own bridging mechanism is the **second measured null**, is **CI-separated
BELOW** the neighbour-copy incumbent it was built to beat (-0.1049 [-0.2041,-0.0057]) and is
**NOT_SEPARATED from a random target** (-0.0015), with its known-answer arm alive (K1 0.3311). It is
recorded as DO-NOT-REDO 43 with a brain-framed revival criterion, and it fires
`LONG_TERM_PLAN.md`'s Phase 2 kill condition. **Caveat carried everywhere it appears: no `.pid` file
on disk names pid 3828 and none was modified on 08-17, so what was read is a complete full; if a
live process rewrites it, re-check the mtime.**

## 5. JOB 4 -- `MEMORY.md`

**Before 18,227 B -> after 18,974 B (+747 B), 8 sections, 59 lines.** All six required items are
folded in and verified present by string search after the last write.

| folded in | where it went |
|---|---|
| the underpowered-null error pattern | banner, as the flagged 🚨 line, with all three retractions named |
| the standing rule (CI half-width + null p95) | the merged **📏 MEASUREMENT BAR** entry, as rule (5) |
| the partial-cue structural cap (0.8787 / 0.0365; rho 0.961 / -0.0167) | banner, as the leading position statement |
| **VSA binding is UNPINNED, two live published rivals, invention-under-test** | a **new FOUNDATIONAL ANCHOR**, placed high in that section beside the brain-fidelity anchor |
| copy the COMPUTATION exactly, sweep every PARAMETER | a **new FOUNDATIONAL ANCHOR** immediately after it, labelled hypothesis-pending-VET |
| the owner's per-process regime ruling + foundation-is-free-to-build, **NO LLM AT INFERENCE surviving** | folded into the existing PIVOT anchor, which already owned that invariant |
| `verdict_bar_check.py` false-passed FOUR times | banner |

**What was collapsed to pay for it (~2,000 B), all of it superseded tails or worked examples whose
detail now lives in a topic file:** the banner's GAP 1 / GAP 2 / ADDRESS_ABSENT narrative (superseded
tonight, and `STATUS.md` is injected every session); the four scattered measurement rules merged into
ONE `📏 MEASUREMENT BAR` entry with all five rules kept and their worked examples left in
`STATUS_LESSONS.md`; the registry-leak measurement detail reduced to "the standing 61 does NOT
reproduce -- re-measure before quoting"; and prose-only compression of the ALWAYS-ASK-FIRST,
FULL-AUTO, hard-blocking, absence-claim, research and wire-don't-island entries.

**It is ~1,474 B over the ~17,500 B soft target and I did not close that gap, deliberately.** Doing
so would have required thinning live USER-locked anchors or dropping one of the six items above,
which the instruction forbids. **No rule, no USER quotation and no `[[slug]]` pointer was dropped
anywhere in the file.**

**Concurrency note, disclosed rather than papered over:** midway through the compaction pass the
Edit tool reported *"the file had been modified on disk since you last read it"* -- something outside
this pass wrote to `MEMORY.md` (a sibling agent or a hook). The edit applied cleanly, all six
fold-ins verify present, and I stopped byte-shaving at that point rather than risk a write race
clobbering another actor's edit. **A further ~1,400 B of prose compression is available and safe;
it should be done by whoever owns the file when nothing else is writing to it.**

## 6. DISCLOSURE

**No tool call in this pass was denied at any point.** Nothing was retried as a variant, no step was
silently skipped. (One `bash` heredoc failed to parse -- a shell quoting error, not a denial -- and
the same content was written with the `Edit` tool instead.)

**Constraints honoured.** No subagent spawned. No cell authored, smoked or dispatched. No process
signalled, inspected or polled -- every liveness statement rests on `.pid` files, directory listings
and mtimes. **No metrics.json, atom or registry row was re-labelled, demoted or deleted.** No
deletion token was issued, alone or bundled. No `git add -A`. No origin push. Nothing was written to
`.claude/scan-out/`.

**Do-not-touch paths, read-only, none written:** `notes/LONG_TERM_PLAN.md`, `notes/BOARD.md`,
`notes/COMPACTION_HANDOFF_2026-08-17.md`, `CLAUDE.md`, `data/foundation/**` (never opened),
`preregs/**`, `experiments/**`, `hdlab/**`, `tools/**`, `data/capability_registry.jsonl`.

**Files written:** `notes/STATUS.md`, `notes/STATUS_LESSONS.md`, `notes/STATUS_SPEC.md`,
`notes/PLAN_NEXT_24H.md`, `notes/plan_status_compaction_report_2026-08-17.md`,
`C:\Users\marsh\.claude\projects\D--AI\memory\MEMORY.md`.

**Commits, both by explicit path list:** `da678875c` (preserve the superseded plan verbatim) and the
docs commit recorded in the final line of this report.
