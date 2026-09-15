---
priority: 130
slug: dormant_capability_flags_audit_every_default_off_flag_its_reason_and_whether_the_reason_still_holds_flip_or_delete
status: OPEN
review:
review_text:
---

# PROBLEM: capability flags on `SituationReader` (and the HDLAB_* env switches) that default OFF for a reason that no longer holds are dormant capability -- `agent_hybrid` + `agent_hybrid_construction` have been default-off since 2026-09-06 because a 19th-century test set regressed, 19c has been banned from requirements since then, and the flag is worth +0.0521 on the product's raw-text agent row (pri 125) -- audit EVERY default-off flag: its reason, whether the reason still holds under the current rules (modern gold only; the board scores the reader's raw-text read; no default-off), and the measured effect of flipping it on the product board; flip or delete each one.

**slug:** `dormant_capability_flags_audit_every_default_off_flag_its_reason_and_whether_the_reason_still_holds_flip_or_delete` -- **opened:** 2026-09-15 by strategy from the efficiency review (`notes/EFFICIENCY_REVIEW_2026-09-15.md`, wrong direction 3) and pri 125's lead 7.

> ## SOLVER OPERATING PROTOCOL (standing; full text in `notes/problems/README.md`, binding here)
> **THIS IS AN AUDIT + MEASUREMENT BRIEF (a sonnet-class agent for the audit; the board runs are the measurement).** No new organ. **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- a flag that turns on a stand-in (a supervised parser/tagger, a fitted constant) is NOT flipped on; it is listed for pruning under pri 129/127. **NO DEFAULT-OFF (owner rule):** a capability that helps the product's raw-text read and does not violate BF is ON.
> **A DEFAULT FLIP NEEDS THE FULL BOARD, BOTH ARMS IN ONE PROCESS** (memory rule 09-14); the board is now the reader's raw-text read (pri 122): `HDLAB_EXP_NAME=situation_model_qa_modern_v1_<name> python experiments/exp_situation_model_qa_modern_v1.py --run` (default `--reader-docs 24`; ~2 h on the laptop; cap cores).

> ## CHECKLIST (in order)
> 1. **OPEN.** (a) Enumerate every boolean parameter of `SituationReader.__init__` (`hdlab/situation_reader.py` ~:995-1060) and every `HDLAB_*` env switch under hdlab/ (grep `os.environ.get("HDLAB_`), with: default, the docstring/comment reason, the date, the file:line, and whether the reason cites 19c LitBank / a capped board / a byte-identity landing. (b) Classify each default-OFF flag: STALE-REASON (19c or capped-board or 'byte-identical landing pending a measurement'), STAND-IN (turns on a NOT_BF component -> prune list), DIAGNOSTIC (an instrument mode, keep off, label it), LIVE-REASON (a measured modern regression -> keep off, cite it). (c) For every STALE-REASON flag, measure the flip on the product board, ONE flag per run, both arms in one process (the shipped defaults vs the flag on) -- expect ~2 h per flag; prioritise by the documented effect size (agent_hybrid first). (d) Publish the table; propose the default flips as a diff against `hdlab/situation_reader.py` (defaults only) with each flip's board numbers beside it.
> 2. **REUSE.** `CAPABILITY_FLAGS` and `all_capabilities_off` in the reader; pri 125's SOLVED.md §9 lead 7 and §10 (the hybrid measured +0.0521 on 40 raw-text docs); pri 122's cell for capped reader-driven rows (`experiments/exp_board_rows_on_the_reader_v1.py --ud --ud-cap`); `tools/reader_capabilities.py`.
> 3. **GENERALIZE.** `verification/test_no_stale_default_off_flag.py`: every default-off flag carries a machine-readable reason tag (`# default-off: LIVE-REASON <ref>` or `DIAGNOSTIC`) and the STALE-REASON class is empty.
> 4. **BAR.** The table complete (every flag classified with file:line); every STALE-REASON flag measured on the product board both arms one process, flipped in the diff when not down (or its regression named with items); the witness green.
> 5. **FILES.** Write ONLY: `notes/problems/<slug>/{SOLVED.md, flags_audit_table.md, default_flips_patch.diff}`, `verification/test_no_stale_default_off_flag.py`, board outputs under `data/exp_situation_model_qa_modern_v1_<name>/` (route by HDLAB_EXP_NAME; never the unsuffixed dir). Never edit hdlab/ directly.

## 1. THE PROBLEM IN PLAIN LANGUAGE
Some abilities of the reader are switched off because of a test we no longer use. Go through every switch, write down why it is off, and for the ones whose reason is gone, measure turning them on with the honest scoreboard and turn them on if they help.

## 2. WHY THIS ONE
About five points of plain-text "who did it" are sitting behind one such switch; there are probably more.

## 3. MEASURED vs INFERRED
MEASURED: agent_hybrid +0.0521 on 40 raw-text UD-EWT docs (pri 125). INFERRED: the number and effect of the other stale flags (the audit decides).

## 4. ALREADY TRIED / DO NOT REDO
Flipping on the rebuilt (component) board rows -- the agent row there computes the hybrid directly, so it is exact zeros by construction; measure on the reader-driven rows.

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read `hdlab/situation_reader.py` __init__ and `CAPABILITY_FLAGS`; pri 125 SOLVED.md §9-10; pri 122 SOLVED.md §3 and §9; `tools/reader_capabilities.py` output.

## 6. THE BAR (can-fail)
See checklist item 4.

## 7. FILES AND ENTRY POINTS
See checklist item 5.

## 8. DO NOT QUOTE / DO NOT REDO
Retired figures: `notes/reference_retired_claims_never_requote.md`. 19c numbers are informational only; a 19c regression is not a reason to keep a flag off.
