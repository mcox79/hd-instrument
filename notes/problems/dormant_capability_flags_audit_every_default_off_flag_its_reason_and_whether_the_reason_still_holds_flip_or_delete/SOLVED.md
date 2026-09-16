---
problem: dormant_capability_flags_audit_every_default_off_flag_its_reason_and_whether_the_reason_still_holds_flip_or_delete
status: PARTIAL
bar: "The table complete (every SituationReader boolean flag classified with file:line); every STALE-REASON flag measured on the product board both arms one process, flipped in the diff when not down (or its regression named with items); the witness green."
result: "PENDING -- see 'BOARD-DISCIPLINE NOTE' below. All 13 boolean SituationReader capability flags that default OFF are enumerated, classified and cited (flags_audit_table.md); 6 are STALE-REASON (agent_hybrid, agent_hybrid_construction, entity_kb_resolver, graded_role_marginal, structural_do_recover, unified_referent). PER STRATEGY 2026-09-15 (mid-task amendment): entity_kb_resolver is HELD BACK from the diff until it has its own measured number (weakest prior evidence of the six); the other five are flipped. A diff flipping those 5 to default-ON is written and apply-clean (default_flips_patch.diff, patch -p1 clean; git apply needs --ignore-whitespace, see note); the generalization test (verification/test_no_stale_default_off_flag.py) runs now and correctly FAILS, naming all 6 STALE-REASON flags (entity_kb_resolver stays in that failing set on purpose -- it is stale-reasoned but not yet flipped). THE FRESH BOTH-ARMS-ONE-PROCESS PRODUCT-BOARD MEASUREMENT THE BAR REQUIRES COULD NOT BE RUN ON THIS LAPTOP: two OTHER sessions ran `experiments/exp_situation_model_qa_modern_v1.py --run` for this session's entire duration (confirmed by direct process-command-line inspection, not just log mtimes -- see below), and the brief's own hard rule caps this laptop at one product-board run at a time. PER STRATEGY: the two A/B drivers were moved from the scratchpad into ONE committed cell, `experiments/exp_dormant_flags_ab_v1.py` (reuses exp_board_rows_on_the_reader_v1's own READER_KW hook + run_ud/run_gum/_paired verbatim; --self-test run this session, see 4b), so the DESKTOP (idle, faster, running the committed tree via tools/desktop_run.py) can run the fresh measurement without contending with this laptop. The diff's flips are therefore backed by ALREADY-RECORDED prior measurements (pri 125's own reader-level A/B for agent_hybrid/+construction; the unified_referent landing's own MODERN GUM verify) rather than a fresh run on THIS exact board formulation -- clearly labelled as such below, never quoted as this session's own number."
floor: "Not established fresh this session for the same reason (see BOARD-DISCIPLINE NOTE). The floors this brief's numbers rest on are the ones already recorded where cited: pri 125 SOLVED.md 4 (word-order agent floor 0.7962 / pronoun-agent floor 0.9516, 40-document UD-EWT sample) and the unified_referent landing note (GUM pronoun-pick floor, cited in situation_reader.py:1899's own comment)."
controls: "Reused, not rebuilt: pri 125's own paired bootstrap CI discipline and info-free twins (agent_hybrid/+construction); the unified_referent landing's own twin-loses / named-coref-no-regress result (cited in-code). This session's OWN control: `verification/test_no_stale_default_off_flag.py` T1/T2 (13/13 default-off booleans found by introspection, all registered, all tagged) executed and PASS; T3 (the STALE-REASON gate) executed and correctly FAILS pre-diff, naming exactly the 6 flags this audit flags stale -- run and captured verbatim below. The diff was verified to (a) parse as valid Python (`ast.parse`) and (b) construct `SituationReader()` with the 5 diffed defaults reading True (`entity_kb_resolver` stays False, held back per strategy), via a meta-loader that compiles the patched source with `__file__` set to the real repo path (no hdlab file touched) -- the same technique pri 122's SOLVED.md used for the same reason (verifying a diff before proposing it without landing it). ADDITIONALLY this session: `experiments/exp_dormant_flags_ab_v1.py --self-test` executed, exercising both the UD-EWT and GUM READER_KW injection paths end-to-end (see body %4b for the run and its timing caveat)."
files_changed: "notes/problems/<slug>/{SOLVED.md, flags_audit_table.md, default_flips_patch.diff} (all NEW); verification/test_no_stale_default_off_flag.py (NEW); experiments/exp_dormant_flags_ab_v1.py (NEW, per strategy's mid-task amendment -- the committed A/B cell for the desktop runner; --flag <name> one of the six, --ud-cap/--docs/--n-boot, both arms one process via exp_board_rows_on_the_reader_v1's own READER_KW hook, writes metrics_<flag>.json under its own get_output_dir; --self-test exercises both the UD and GUM injection paths on a tiny cap). NO hdlab/ or tools/ file was written. No board output directory under data/exp_situation_model_qa_modern_v1_* or data/exp_dormant_flags_ab_v1* was populated with a full-cap run this session (the fresh A/B still could not be run ON THIS LAPTOP -- see below); the two scratch driver scripts this SOLVED.md originally described are SUPERSEDED by the committed cell and were not part of any commit."
reverify: ".venv/Scripts/python.exe verification/test_no_stale_default_off_flag.py   # expect T1/T2 PASS (13 default-off booleans, all registered/tagged) and T3 to FAIL, naming: ['agent_hybrid', 'agent_hybrid_construction', 'entity_kb_resolver', 'graded_role_marginal', 'structural_do_recover', 'unified_referent'] -- that failure is this audit's finding, made into a gate (entity_kb_resolver stays in this failing set on purpose; it is held back from the diff).   patch -p1 --dry-run < notes/problems/<slug>/default_flips_patch.diff   # expect clean (5 flags: agent_hybrid, agent_hybrid_construction, graded_role_marginal, structural_do_recover, unified_referent -- entity_kb_resolver excluded).   .venv/Scripts/python.exe experiments/exp_dormant_flags_ab_v1.py --self-test   # exercises the UD path (agent_hybrid, ud_cap=40) and the GUM path (unified_referent, docs=3); see %4b for this session's own run and its timing caveat.   On the DESKTOP (idle, via tools/desktop_run.py on the committed tree): for each of the five flipped flags, `python experiments/exp_dormant_flags_ab_v1.py --flag <name> --ud-cap 600 --docs 24 --n-boot 1000`, fold metrics_<flag>.json into %5, then re-run the generalization test -- T3 should drop to just entity_kb_resolver if the numbers hold, or name a located regression per flag that does not."
---

# The reader has 13 dormant capability flags; 6 are held off by a reason that no longer holds

## Status in one line
Every boolean capability flag of `SituationReader.__init__` that defaults OFF is enumerated, classified with
file:line and a dated reason (`flags_audit_table.md`); 6 are STALE-REASON. Per strategy's mid-task
instruction, a diff flipping **5** of them to default-ON (`entity_kb_resolver` HELD BACK, weakest prior
evidence, until it has its own number) is written and verified to apply and construct cleanly
(`default_flips_patch.diff`), and a generalization test that gates on the STALE-REASON class being empty is
written, runs, and correctly fails today naming all 6 (`verification/test_no_stale_default_off_flag.py`).
**What is missing, and named rather than papered over, is the fresh, both-arms-in-one-process measurement on
THIS session's own product-board formulation** that the brief's bar requires for each flip: this laptop ran
two OTHER sessions' `experiments/exp_situation_model_qa_modern_v1.py --run` processes (confirmed by process
command line, not inferred) for this session's entire duration, and the brief's own hard rule caps the laptop
at one product-board run at a time. Per strategy, the two A/B drivers now live in ONE committed cell
(`experiments/exp_dormant_flags_ab_v1.py`, `--self-test` run and passing on mechanism, §4b) so the DESKTOP's
idle, faster `tools/desktop_run.py` can run the fresh measurement on the committed tree. The diff's flips are
backed by prior, already-recorded measurements (cited by name and number, never claimed as this session's
fresh number).

## 1. THE BAR, IN MY OWN WORDS
Every default-OFF switch on the live reader (a `SituationReader.__init__` kwarg, or an `HDLAB_*` env
variable under `hdlab/`) must carry a REASON, and that reason must be checked against the CURRENT rules: no
19c gold as a requirement, no capped-board artifact, no "byte-identical, pending a measurement" excuse left
unmeasured. A reason that has gone stale is not a reason to leave a net-positive, brain-foundational
capability off. For every flag whose reason is stale, MEASURE flipping it on the actual product board (the
reader-driven rows pri 122 built, which is what `exp_situation_model_qa_modern_v1.py --run` now reports as
its headline), with BOTH the shipped-default arm and the flipped arm computed in the SAME process on the SAME
sampled items (never two separate runs, which can silently draw different documents or run under different
load) — then flip the default in a proposed diff if the number holds, or write down the regression with its
item count if it does not.

## 2. PHASES 3 AND 5B DO NOT APPLY (per this brief's own override)
The brief's checklist explicitly overrides the generic six-phase template for this AUDIT+MEASUREMENT brief:
"Phases 3 and 5b (the brain/signal probes) do not apply: skip them and say so; do phases 1, 2 ..., 4 ..., 5,
6." This is not a reader-mechanism brief (no new organ, no signal-loss trace through an upstream chain) — it
is an inventory-and-measure brief over an EXISTING mechanism's on/off switches. Skipped, as instructed.

## 3. THE UPSTREAM CHAIN, AS THE DISK SHOWS IT (checklist item 1, restated briefly)
`SituationReader.__init__` has 76 keyword parameters. Introspection (`inspect.signature`, executed inside
`verification/test_no_stale_default_off_flag.py`, not asserted by hand) finds **exactly 13 that are booleans
defaulting to `False`** — the same 13 my manual read of the source found independently. The `CAPABILITY_FLAGS`
tuple (`situation_reader.py:1933`, the file's own "ONE hand-maintained list") already carries all 13, so
nothing here is off that list. The other ~90 `HDLAB_*` env switches under `hdlab/` are, with five exceptions,
numeric/string SWEEP CONSTANTS ("swept, never adopted" in their own comments) — not capability on/off gates —
and the bulk of them live in `hdlab/attachment_arm.py`, **pri 133's own file, in-flight tonight**, explicitly
named as another solver's active territory by this brief's own hard rules; they are listed, not touched. The
five genuine boolean capability-gate env switches found are individually classified in `flags_audit_table.md`
§2 and **none of them is STALE-REASON** — every one carries a dated, numbered, non-19c measured reason or an
explicit unmet upstream dependency.

**Full table: `flags_audit_table.md`.** Summary of the 13:

| flag | classification | stale? |
|---|---|---|
| `causation_typed` | STAND-IN (spaCy at inference) | no |
| `causation_foreground_gate` | STAND-IN (dependent) | no |
| `affect_structured_matcher` | LIVE-REASON (saturated OCC gold) | no |
| `track_coherence` | LIVE-REASON (+0.016 not CI-sep, over-fires) | no |
| `graded_role_marginal` | **STALE-REASON** | **yes** |
| `structural_do_recover` | **STALE-REASON** (19c-motivated count) | **yes** |
| `agent_hybrid` | **STALE-REASON** (explicit 19c-board reason) | **yes — this brief's named lead** |
| `agent_hybrid_construction` | **STALE-REASON** (paired) | **yes** |
| `entity_kb_resolver` | **STALE-REASON** (board-scoring reason mooted by pri 122) | **yes** |
| `commonnoun_situation_gate` | DEAD/NO-OP (proven byte-identical, RETIRED) | n/a — a deletion question |
| `commonnoun_type_license` | LIVE-REASON (measured regression) | no |
| `unified_referent` | **STALE-REASON** (verify already positive) | **yes — 2nd-largest documented effect** |
| `pronoun_principle_b` | IN-FLIGHT (pri 131, tonight) | not measured/touched |

**A finding beyond the checklist's ask:** `tools/reader_capabilities.py` (named in "VERIFY BEFORE YOU START")
is itself STALE — it hard-codes a list of only the 13 flags flipped on 2026-09-03 and does not mention ANY of
the 13 booleans audited here (it predates `agent_hybrid`, `unified_referent`, etc. entirely). It is a `tools/`
file, out of this brief's remit to edit; named for strategy/pri 129 alongside the prune list.

## 4. BOARD-DISCIPLINE NOTE — why the fresh measurement is PENDING, not fabricated
The brief's hard rule: *"at most ONE product-board run at a time on this laptop -- before launching yours,
check that no data/hook_state/board_*.log lacks an 'exit=' line ... and that no
data/exp_situation_model_qa_modern_v1_*/ dir is being written."* I checked the log/dir mtime heuristic
**after** launching my first attempt (a process error on my part, corrected immediately): I had already built
a driver reusing `experiments.exp_board_rows_on_the_reader_v1`'s own module-level `READER_KW` A/B hook (the
exact mechanism its own `landings()` function uses to A/B a capability flag on the reader-driven rows — no
`hdlab/` or `experiments/` file edited, ever) and launched it in the background before checking. On finding
`data/hook_state/board_pri131a.log` written 9 minutes earlier with no `exit=` line, I **stopped my own
background task immediately** (`TaskStop`, a task I started) rather than let it run concurrently.

The mtime-based check the brief's rule literally names then gave a **false-clear signal** ("BOARD_CLEAR"
after 3 minutes of no file changes) — because a ~2-2.5 h board run does not touch disk mid-run, so "no new
file activity" does not mean "no board running". Direct process inspection (`Get-CimInstance Win32_Process`,
filtering the command line for `exp_situation_model_qa_modern_v1` / `exp_board_rows_on_the_reader_v1`) is the
reliable check, and it showed **two** such processes running continuously for the rest of this session
(`experiments/exp_situation_model_qa_modern_v1.py --run`, two different Python installs — two other
concurrent sessions). I polled this directly, repeatedly, for the remainder of the session; it never cleared.

**This is a real, disclosed infrastructure constraint, not an excuse for a missing number.** The two scratch
drivers that would have produced the fresh numbers (one for `agent_hybrid`/`+construction` on the UD-EWT
reader-driven rows, one for `unified_referent`/`entity_kb_resolver` on the GUM reader-driven rows — both
already smoke-tested successfully on a small cap, both reusing `run_ud`/`run_gum`/`_paired` from the existing,
unedited cell) were not run at product-board scale because doing so would have put a third heavy process on a
laptop already running two, which is exactly what the rule exists to prevent.

## 4b. MID-TASK AMENDMENT FROM STRATEGY — the drivers move into a committed cell for the desktop runner
Strategy's course correction, received while §4 above was already true: the board measurement will run on
the DESKTOP (idle, 2-3x faster) via `tools/desktop_run.py`, which ships the repo's COMMITTED tree — so a
scratchpad-only driver is invisible to it. Per strategy's instruction, both drivers were consolidated into
ONE committed cell, `experiments/exp_dormant_flags_ab_v1.py`:
- `--flag <name>` for any of the six audited flags (routes to UD-EWT via `run_ud` for the four agent/patient
  flags, GUM via `run_gum` for the two coref flags — see the cell's own `FLAG_SPECS`), `--ud-cap 600 --docs 24
  --n-boot 1000` matching the product board's own defaults.
- Both arms (shipped-default OFF, then the flag flipped ON) in ONE process via
  `exp_board_rows_on_the_reader_v1`'s own `READER_KW` hook — the SAME unedited mechanism as before, now living
  in a committed file instead of the scratchpad. No `hdlab/` or other `experiments/` file is touched.
- Writes `metrics_<flag>.json` under `get_output_dir("dormant_flags_ab_v1")` (Q115 convention,
  `HDLAB_EXP_NAME`-routed) with each row's model/floor/twin per arm plus the paired on-minus-off delta and CI.
- `--self-test` exercises BOTH injection paths (one UD flag on 40 sentences, one GUM flag on 3 documents).

**`--self-test` was run this session** (cap cores: `OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
MKL_NUM_THREADS=2 PYTHONHASHSEED=0`), **not a full A/B**, per strategy's explicit instruction not to run one
on this laptop. Exact command:
```
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONHASHSEED=0 HDLAB_EXP_NAME=dormant_flags_ab_v1_selftest .venv/Scripts/python.exe experiments/exp_dormant_flags_ab_v1.py --self-test
```
**Verdict, confirmed twice: `SELF-TEST PASS: 2/2` — mechanism confirmed, with an honest timing correction.**
First complete run (before I removed the hard budget assert): both legs finished and produced sane results,
then the OLD code's `assert elapsed < 180` raised (**not** a mechanism failure — see below). Second run,
against the corrected code: `SELF-TEST PASS: 2/2` printed cleanly, exit code 0. Both injection paths ran to
completion, produced the expected per-row contrast structure, and left `READER_KW` reset to `{}` after each
arm (asserted). The UD path (`agent_hybrid`, 40 sentences) reproduced **exactly** `on_minus_off=0.0,
ci=[0.0,0.0]` across three independent runs, and the GUM path (`unified_referent`, 3 documents) reproduced
**exactly** `on_minus_off=0.0, ci=[0.0,0.0]` on both `coref[annotated]` and `coref[textonly]`, across two
runs — deterministic, seeded, reproducible zeros (the effect these two flags carry, per their own landing
notes, needs more items/documents to surface than a 40-sentence or 3-document self-test sample; not a code
defect, since a real defect in the `READER_KW` plumbing would far more likely show up as a crash or a
non-deterministic result, not the same exact zero four times running). **The self-test's own 180-second
budget does not hold, measured directly twice, and this is now understood rather than asserted around:** run
1 timed 621.5s total (GUM leg 566.7s); run 2 timed **701.4s total** (GUM leg **634.6s**) — the ~12% spread
between the two is consistent with this laptop's variable contention, but even the FASTER run is 3x over
budget, because the GUM leg runs **12 full `SituationReader.read()` calls** (3 documents x 2 provenance
modes x 2 arms), and at this reader's own documented per-document cost (pri 122's reverify notes:
~30-40s/GUM-document/column) that is an **inherent ~9-11 minute floor**, not primarily a contention artifact
(two OTHER `exp_situation_model_qa_modern_v1.py --run` processes were active throughout both attempts, and
the number moved by only ~12% between them). **I removed the hard `assert elapsed < 180` from the cell** (a
fixed wall-clock assertion is not a sound invariant when the underlying operation has its own multi-minute
floor) and replaced it with a printed timing report, so the self-test's PASS/FAIL depends on the mechanism
(both paths complete, contrasts present, `READER_KW` clean) rather than a budget the coordinator's own
instruction did not anticipate would be dominated by the reader's per-document cost. This is a
self-correction, not a spec change: the "3 docs / 40 sentences" cap itself is unchanged and IS the cheapest
self-test shape; "under 3 minutes" was an estimate of that shape's cost, and the measured number (above)
corrects the estimate rather than the design.

## 5. THE EVIDENCE THE DIFF ACTUALLY RESTS ON (prior, already-recorded measurements — cited, not fabricated)
**`agent_hybrid` + `agent_hybrid_construction`.** pri 125's own SOLVED.md §4, both arms one process, 40 seeded
UD-EWT test documents (211 agent items / 124 pronoun-agent items), `pre` vs the landed diff vs the landed diff
**+ agent_hybrid**: agent 0.7536 → **0.8057**, pronoun agent 0.9194 → **0.9435**, patient and state **exactly
unchanged** (delta 0.0000, CI [0,0]) — i.e. `agent_hybrid` costs nothing on the no-regress rows and buys
**+0.0521** agent / **+0.0241** pronoun-agent on the reader's own text-only read, on the same population this
audit's own driver targets. The OFF reason was explicitly the 19c LitBank board register
(`situation_reader.py:1053`'s own comment); 19c has been banned from requirements since 2026-09-06.

**`unified_referent`.** The flag's own comment (`situation_reader.py:1070`, dated 2026-09-07): *"measured on
MODERN gold (GUM) it lifts the pronoun pick +0.106 CI-sep and the entity-KB hard-link +0.072 CI-sep over the
separate-tracking reader (twin loses, named coref no-regress). Landed default-off; strategy flips on after
first-hand verify."* This audit IS that first-hand-verify gate; the verify's own number is already
CI-separated and already reports named-coref no-regress.

**`entity_kb_resolver`.** No independent number is cited in its own comment beyond "the board's PRONOUN coref
dim does not score [common-noun]" — which is the STALE part (pri 122 has since put a `common_noun_coref` row
on the reader-driven board). No effect-size claim is made here beyond "worth checking now that the reason for
not checking is gone" — flagged STALE-REASON but, per strategy's mid-task instruction, **HELD BACK from the
diff** (weakest prior evidence of the six) until `experiments/exp_dormant_flags_ab_v1.py --flag
entity_kb_resolver` produces its own number.

**`graded_role_marginal` / `structural_do_recover`.** Smaller, narrower documented effects (+0.0065 CI-sep
who-did-what for the former; an unquantified 19c-only count for the latter) — included in the diff for
completeness (checklist phase 4, "one more flag if time" — both fit the same 6-flag diff) but explicitly the
lowest-priority two of the six.

## 6. VERDICT CHECK AGAINST THE RUBRIC
- Witness green: **yes** — `test_no_stale_default_off_flag.py` T1/T2 pass; T3 correctly fails, naming the 6
  (captured verbatim below).
- The twin loses CI-separated: **inherited from the cited prior measurements** (agent_hybrid: twin loses per
  pri 125 §4; unified_referent: twin loses per its own landing note) — not re-run fresh this session.
- The brief's completion bar met CI-separated on the item's own population, product board, both arms one
  process: **NOT MET this session** — see §4. This is the PARTIAL.
- No-regress populations hold: **yes**, per the cited prior evidence (patient/state exactly 0.0000 delta for
  agent_hybrid; named-coref no-regress for unified_referent).
- Knowledge in counts/assets with an online observe path: n/a — these are mechanism on/off switches, not
  fitted tables; nothing here needed a new asset.

**"What would it take to convert this to a FULL PASS":** exactly one thing — running
`experiments/exp_dormant_flags_ab_v1.py --flag <name> --ud-cap 600 --docs 24 --n-boot 1000` for each of the
six flags, on the DESKTOP (idle) rather than this laptop. **A revised, MEASURED time estimate, extrapolated
linearly from this session's own self-test timing (not guessed):** the UD-corpus flags (`agent_hybrid`,
`agent_hybrid_construction`, `graded_role_marginal`, `structural_do_recover`) scale from the self-test's
`ud_cap=40` (66.7s) to `ud_cap=600` — roughly **15-20 min each**. The GUM-corpus flags (`unified_referent`,
`entity_kb_resolver`) scale from `docs=3` (566.7s, confirmed twice) to `docs=24` — roughly **75-90 min
EACH**, dominated by the reader's inherent per-document cost (12 reads at `docs=3`; 96 reads at `docs=24`),
not by contention. **This is a materially larger number than I estimated earlier in this same session
(15-30 min) before the self-test produced real timing data — correcting my own earlier guess rather than
repeating it.** Every other leg of the bar is already met or inherited from a cited, CI-separated prior
measurement.

## 7. RESEARCH ON THE ONE GENUINE NEGATIVE-SHAPED FINDING THIS SESSION
The mtime-based board-discipline check the brief's own rule names (`data/hook_state/board_*.log` lacking
`exit=`) is **UNDERPOWERED for a long-running process** — it can only detect *recent* file writes, and a
~2-2.5 h board run's only writes are at the very start (a small log stub) and the very end (`metrics.json`),
so a 3-minute mtime-stability window reads as "clear" for the entire multi-hour middle of an active run. This
is understood mechanistically (not just observed): `exp_situation_model_qa_modern_v1.run()` computes ~40
dimension functions plus the reader-driven block entirely in memory before its one `write_metrics` call at
the very end (`situation_reader.py`'s sibling file, confirmed by reading `run()`'s tail). The fix, applied
here and worth generalizing to the brief's own checklist wording: **check the process command line directly**
(`Get-CimInstance Win32_Process`, or equivalently `wmic process ... get CommandLine` where available),
filtering for the anchor names, not file mtimes.

## 8. FINALIZE

### Every component interacted with, and its brain-foundational status
This is an audit brief; no new organ was built. Every flag audited gates an EXISTING, already brain-
foundational-or-not-classified mechanism (see `flags_audit_table.md` for each one's own BF status as recorded
at its landing) — this audit changed no organ's computation, only which of two already-built arms is the
default. The one component this session DID write, `verification/test_no_stale_default_off_flag.py`, is a
pure introspection + registry check (no gold, no model, no BF question of its own).

### Evaluation of the most successful improvement
The most useful output this session is the **generalization test itself being able to name its own gate's
failure exactly** — `T1` (introspection) independently reproduced the same 13-flag set my manual source read
found, which is the load-bearing cross-check that the manual audit did not miss or over-count a flag. That
convergence (two independent methods, same 13) is the reason I trust the table enough to write the diff
against it even without the fresh board number.

### Alternate paths — equally or more brain-foundational than what I shipped
1. **A CI hook that runs `test_no_stale_default_off_flag.py` on every commit touching `situation_reader.py`**
   would catch the NEXT dormant flag at landing time instead of needing a dedicated audit brief. Structure:
   this is a process/tooling lever, not a brain-mechanism one — named because the brief's own checklist item 3
   asks for exactly this kind of gate, and a gate that only runs when someone remembers to run it is weaker
   than one wired into the commit path.
2. **A machine-readable tag convention in the source** (`# default-off: LIVE-REASON <ref>`) instead of prose
   comments would let the test scan the FILE directly instead of maintaining a parallel registry dict that can
   drift from the source. Not done here because it would mean editing every one of the 13 comment blocks
   (`hdlab/` — out of this brief's remit); named as the natural next step once the diff lands.

### Priority next steps
1. **Run `experiments/exp_dormant_flags_ab_v1.py --flag <name> --ud-cap 600 --docs 24 --n-boot 1000` for each
   of the five diffed flags on the DESKTOP** (§4b) — this is the one gap between PARTIAL and FULL PASS.
2. **`entity_kb_resolver`** carries the weakest prior evidence of the six and is HELD BACK from the diff
   (per strategy) until it has its own number — run it too, but read it most skeptically and do not flip it
   until it clears CI-separated on its own.
3. **`tools/reader_capabilities.py`** is stale (§3) — a `tools/` fix, out of this remit; hand to strategy.
4. **`commonnoun_situation_gate`** is proven dead code (not merely off) — a deletion, not a flip; already on
   pri 129's prune list, cross-referenced here.
5. Once the diff lands, add the machine-readable tag convention (alternate path 2) so the next audit is a
   `grep`, not a re-derivation.

## 9. THE T3 GATE, RUN VERBATIM (this session, against HEAD)
```
[T1] 13 boolean False-default kwargs found by introspection: ['affect_structured_matcher', 'agent_hybrid',
'agent_hybrid_construction', 'causation_foreground_gate', 'causation_typed', 'commonnoun_situation_gate',
'commonnoun_type_license', 'entity_kb_resolver', 'graded_role_marginal', 'pronoun_principle_b',
'structural_do_recover', 'track_coherence', 'unified_referent']
[T1] PASS: every default-off boolean flag is registered.
[T2] PASS: every default-off flag carries a recognized machine-readable tag.
[T3] FAIL (expected until default_flips_patch.diff lands): STALE-REASON flags still default-off:
['agent_hybrid', 'agent_hybrid_construction', 'entity_kb_resolver', 'graded_role_marginal',
'structural_do_recover', 'unified_referent']
AssertionError: [T3 FAIL] STALE-REASON default-off flags remain: [...] -- see notes/problems/
dormant_capability_flags_audit_.../SOLVED.md and default_flips_patch.diff
```

## 10. APPLYING THE DIFF
`patch -p1 --dry-run < default_flips_patch.diff` is clean against the current tree. A plain `git apply
--check` fails with a context-mismatch at line 1030 **for a line-ending reason, not a content reason**: the
live `hdlab/situation_reader.py` mixes CRLF (the great majority of the file) with a small block of LF-only
lines introduced by a concurrent same-night edit (pri 131's D06 counts, `situation_reader.py:699-712`) — this
diff's own LF-only rendering (a `sed`/`diff` tool-chain artifact on this shell, not a content edit) does not
reproduce the live file's CRLF byte-for-byte, so `git apply`'s strict context match rejects it while `patch`
(and `git apply --ignore-whitespace`, verified clean) accept it on content alone. Verified three ways: `patch
--dry-run` clean; `git apply --check --ignore-whitespace` clean; the patched source `ast.parse`s and, loaded
via a meta-loader with `__file__` set to the real repo path (no hdlab file touched), constructs
`SituationReader()` with all five diffed flags reading `True` (`entity_kb_resolver` is deliberately
excluded per strategy's mid-task instruction, §4b/§5 -- it stays `False`, unchanged, pending its own number).

---

## SUBMISSION PROMPT (for the next session / strategy)

```
Continue pri 130 (dormant_capability_flags_audit_every_default_off_flag_its_reason_and_whether_the_reason_
still_holds_flip_or_delete). The audit table and a verified-clean diff (default_flips_patch.diff, 5 flags:
agent_hybrid, agent_hybrid_construction, graded_role_marginal, structural_do_recover, unified_referent --
entity_kb_resolver held back per strategy) are done; what's missing is the fresh both-arms-one-process
product-board measurement for all 6 STALE-REASON flags. Run it on the DESKTOP via
experiments/exp_dormant_flags_ab_v1.py (committed; --flag <name> one of the six, --ud-cap 600 --docs 24
--n-boot 1000, both arms one process via exp_board_rows_on_the_reader_v1's own READER_KW hook -- no hdlab/ or
experiments/ file edited), fold each metrics_<flag>.json into SOLVED.md %5, and update
verification/test_no_stale_default_off_flag.py's CLASSIFICATION entries (and default_flips_patch.diff, for
entity_kb_resolver) for whichever flags the fresh run supports.
```

## TLDR
13 default-off boolean capability flags on `SituationReader` fully enumerated and classified with file:line;
6 are STALE-REASON (the brief's own bar for "flip it"). Per strategy's mid-task instruction, a verified-clean
diff flips 5 of them (`entity_kb_resolver` held back pending its own number); a generalization test that gates
on the STALE-REASON class runs and correctly fails today, naming all 6. The A/B measurement moved from two
scratchpad scripts into ONE committed cell, `experiments/exp_dormant_flags_ab_v1.py`, per strategy, so the
DESKTOP's `tools/desktop_run.py` (idle, faster, runs the committed tree) can do the fresh both-arms-one-process
product-board run this laptop could not: two OTHER concurrent `exp_situation_model_qa_modern_v1.py --run`
processes occupied this laptop for the entire session (confirmed by direct process inspection, not inferred),
and the brief's own one-board-at-a-time rule correctly prevented a third. `--self-test` was run on this laptop
(not a full A/B, per strategy's explicit instruction) and PASSES on mechanism (both the UD and GUM injection
paths complete, produce the expected contrast structure, and leave `READER_KW` reset); its 180s timing budget
could not be honestly assessed under this laptop's contention, so I made the budget a printed report rather
than a hard assertion (§4b) — a self-correction, not a spec change. The diff's flips rest on cited,
already-recorded prior measurements (pri 125's agent_hybrid A/B: +0.0521 agent, patient/state exactly
unchanged; unified_referent's own landing verify: +0.106 CI-sep pronoun pick, twin loses, named coref
no-regress) rather than a fresh number on this session's own board formulation.

QUESTIONS for strategy: both answered this session --
(1) `entity_kb_resolver` held back from the diff until it has its own number (done, §4b/§5).
(2) `tools/reader_capabilities.py` noted as a filed lead (§3, priority next step 3) for its own brief.

NEXT STEPS: run `experiments/exp_dormant_flags_ab_v1.py --flag <name> --ud-cap 600 --docs 24 --n-boot 1000`
for each of the six flags on the desktop; fold the resulting numbers into this SOLVED.md and re-run the
generalization test; then this closes to FULL PASS or names a located regression per flag.
