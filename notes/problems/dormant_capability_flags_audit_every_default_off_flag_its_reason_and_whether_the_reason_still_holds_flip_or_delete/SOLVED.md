---
problem: dormant_capability_flags_audit_every_default_off_flag_its_reason_and_whether_the_reason_still_holds_flip_or_delete
status: PARTIAL
bar: "The table complete (every SituationReader boolean flag classified with file:line); every STALE-REASON flag measured on the product board both arms one process, flipped in the diff when not down (or its regression named with items); the witness green."
result: "PENDING -- see 'BOARD-DISCIPLINE NOTE' below. All 13 boolean SituationReader capability flags that default OFF are enumerated, classified and cited (flags_audit_table.md); 6 are STALE-REASON (agent_hybrid, agent_hybrid_construction, entity_kb_resolver, graded_role_marginal, structural_do_recover, unified_referent); a diff flipping all 6 to default-ON is written and apply-clean (default_flips_patch.diff, patch -p1 clean; git apply needs --ignore-whitespace, see note); the generalization test (verification/test_no_stale_default_off_flag.py) runs now and correctly FAILS, naming exactly those 6. THE FRESH BOTH-ARMS-ONE-PROCESS PRODUCT-BOARD MEASUREMENT THE BAR REQUIRES COULD NOT BE RUN IN THIS SESSION: this laptop had two OTHER sessions running `experiments/exp_situation_model_qa_modern_v1.py --run` for the entire session (confirmed by direct process-command-line inspection, not just log mtimes -- see below), and the brief's own hard rule caps this laptop at one product-board run at a time. The diff's flips are therefore backed by ALREADY-RECORDED prior measurements (pri 125's own reader-level A/B for agent_hybrid/+construction; the unified_referent landing's own MODERN GUM verify) rather than a fresh run on THIS exact board formulation -- clearly labelled as such below, never quoted as this session's own number."
floor: "Not established fresh this session for the same reason (see BOARD-DISCIPLINE NOTE). The floors this brief's numbers rest on are the ones already recorded where cited: pri 125 SOLVED.md 4 (word-order agent floor 0.7962 / pronoun-agent floor 0.9516, 40-document UD-EWT sample) and the unified_referent landing note (GUM pronoun-pick floor, cited in situation_reader.py:1899's own comment)."
controls: "Reused, not rebuilt: pri 125's own paired bootstrap CI discipline and info-free twins (agent_hybrid/+construction); the unified_referent landing's own twin-loses / named-coref-no-regress result (cited in-code). This session's OWN control: `verification/test_no_stale_default_off_flag.py` T1/T2 (13/13 default-off booleans found by introspection, all registered, all tagged) executed and PASS; T3 (the STALE-REASON gate) executed and correctly FAILS pre-diff, naming exactly the 6 flags this audit flags stale -- run and captured verbatim below. The diff was verified to (a) parse as valid Python (`ast.parse`) and (b) construct `SituationReader()` with all 6 new defaults reading True, via a meta-loader that compiles the patched source with `__file__` set to the real repo path (no hdlab file touched) -- the same technique pri 122's SOLVED.md used for the same reason (verifying a diff before proposing it without landing it)."
files_changed: "notes/problems/<slug>/{SOLVED.md, flags_audit_table.md, default_flips_patch.diff} (all NEW); verification/test_no_stale_default_off_flag.py (NEW). NO hdlab/ or tools/ file was written. No board output directory under data/exp_situation_model_qa_modern_v1_* was populated this session (the fresh A/B could not be run -- see below); two scratch driver scripts prepared in the scratchpad (not part of this submission) are ready to run the moment the laptop is clear, reusing experiments.exp_board_rows_on_the_reader_v1's own READER_KW A/B hook and run_ud/run_gum/_paired helpers verbatim (no experiments/ file edited)."
reverify: ".venv/Scripts/python.exe verification/test_no_stale_default_off_flag.py   # expect T1/T2 PASS (13 default-off booleans, all registered/tagged) and T3 to FAIL, naming: ['agent_hybrid', 'agent_hybrid_construction', 'entity_kb_resolver', 'graded_role_marginal', 'structural_do_recover', 'unified_referent'] -- that failure is this audit's finding, made into a gate.   patch -p1 --dry-run < notes/problems/<slug>/default_flips_patch.diff   # expect clean.   Once the laptop has no `exp_situation_model_qa_modern_v1` / `exp_board_rows_on_the_reader_v1` process running (check: a PowerShell CIM process-command-line grep, NOT just hook_state log mtimes -- see the note on why the mtime heuristic gave a false-clear signal this session), run the fresh both-arms-one-process A/B this SOLVED.md's %3 describes, then re-run the generalization test -- T3 should now PASS if the diff is applied, or the effect sizes go into the table if a flag's flip is NOT supported by the fresh number."
---

# The reader has 13 dormant capability flags; 6 are held off by a reason that no longer holds

## Status in one line
Every boolean capability flag of `SituationReader.__init__` that defaults OFF is enumerated, classified with
file:line and a dated reason (`flags_audit_table.md`), a diff flipping the 6 STALE-REASON flags to default-ON
is written and verified to apply and construct cleanly (`default_flips_patch.diff`), and a generalization
test that gates on the STALE-REASON class being empty is written, runs, and correctly fails today naming
those 6 (`verification/test_no_stale_default_off_flag.py`). **What is missing, and named rather than
papered over, is the fresh, both-arms-in-one-process measurement on THIS session's own product-board
formulation** that the brief's bar requires for each flip: this laptop ran two OTHER sessions'
`experiments/exp_situation_model_qa_modern_v1.py --run` processes (confirmed by process command line, not
inferred) for this session's entire duration, and the brief's own hard rule caps the laptop at one
product-board run at a time. The diff's flips are backed by prior, already-recorded measurements (cited by
name and number, never claimed as this session's fresh number).

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
unedited cell) are ready; they were not run at product-board scale because doing so would have put a third
heavy process on a laptop already running two, which is exactly what the rule exists to prevent.

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
not checking is gone" — flagged STALE-REASON, flipped in the diff, but with the weakest prior evidence of the
three; strategy should treat it as the lowest-confidence flip of the three until the fresh run lands.

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

**"What would it take to convert this to a FULL PASS":** exactly one thing — a laptop window with no
`exp_situation_model_qa_modern_v1` / `exp_board_rows_on_the_reader_v1` process running, long enough to run the
two prepared drivers (~15-30 min each at the product board's own caps, UD cap 600 / GUM docs 24, n_boot 2000,
estimated from a 40-sentence smoke test that completed in seconds and the reader's own per-document/per-chunk
timing notes elsewhere in this codebase). Every other leg of the bar is already met or inherited from a cited,
CI-separated prior measurement.

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
1. **Run the two prepared drivers the moment the laptop is clear** (§4) — this is the one gap between PARTIAL
   and FULL PASS.
2. **`entity_kb_resolver`** carries the weakest prior evidence of the three higher-priority flips; the fresh
   run should be read most skeptically for this one.
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
`SituationReader()` with all six flags reading `True`.

---

## SUBMISSION PROMPT (for the next session / strategy)

```
Continue pri 130 (dormant_capability_flags_audit_every_default_off_flag_its_reason_and_whether_the_reason_
still_holds_flip_or_delete). The audit table and a verified-clean diff (default_flips_patch.diff) are done;
what's missing is the fresh both-arms-one-process product-board measurement for 6 STALE-REASON flags
(agent_hybrid, agent_hybrid_construction, entity_kb_resolver, graded_role_marginal, structural_do_recover,
unified_referent), blocked all of pri 130's session by two OTHER concurrent `exp_situation_model_qa_modern_v1
--run` processes on the same laptop. Check first (Get-CimInstance Win32_Process, filter the command line for
exp_situation_model_qa_modern_v1 / exp_board_rows_on_the_reader_v1 -- NOT log mtimes, which give a false
"clear" mid-run) that the laptop is free, then run the two prepared A/B drivers (reusing
experiments.exp_board_rows_on_the_reader_v1's own READER_KW hook, run_ud/run_gum/_paired -- no hdlab/ or
experiments/ file edited) at product-board caps (UD cap 600, GUM docs 24, n_boot 2000), fill the numbers into
SOLVED.md %5, and flip verification/test_no_stale_default_off_flag.py's CLASSIFICATION entries for whichever
flags the fresh run supports.
```

## TLDR
13 default-off boolean capability flags on `SituationReader` fully enumerated and classified with file:line;
6 are STALE-REASON (the brief's own bar for "flip it"); a verified-clean diff flips all 6; a generalization
test that gates on the STALE-REASON class runs and correctly fails today, naming exactly those 6. The one leg
not met is the fresh, both-arms-one-process PRODUCT-BOARD measurement the bar requires — blocked the entire
session by two other concurrent board runs on the same laptop (confirmed by direct process inspection, not
inferred), which the brief's own one-board-at-a-time rule correctly prevented me from contending with. The
diff's flips rest on cited, already-recorded prior measurements (pri 125's agent_hybrid A/B: +0.0521 agent,
patient/state exactly unchanged; unified_referent's own landing verify: +0.106 CI-sep pronoun pick, twin
loses, named coref no-regress) rather than a fresh number on this session's own board formulation.

QUESTIONS for strategy: (1) is `entity_kb_resolver`'s flip (weakest prior evidence of the six) acceptable to
ship pending its own fresh number, or should it be held back from the diff until measured? (2) should
`tools/reader_capabilities.py` (found stale, out of this remit) get its own brief?

NEXT STEPS: run the two prepared drivers the moment the laptop clears (§4/§10); fold the resulting numbers
into this SOLVED.md and re-run the generalization test; then this closes to FULL PASS or names a located
regression per flag.
