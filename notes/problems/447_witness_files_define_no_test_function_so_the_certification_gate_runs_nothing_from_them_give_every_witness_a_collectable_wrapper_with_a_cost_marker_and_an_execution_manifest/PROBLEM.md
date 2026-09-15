---
priority: 128
slug: 447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest
status: OPEN
review:
review_text:
---

# PROBLEM: 465 of the 622 `verification/test_*.py` files expose only a `main()` and no pytest-collectable test function (447 of them beyond the gate's own allowlist), so `pytest verification/` reports green having run NOTHING from them and the repository's own discovery gate (`test_no_witness_is_islanded_from_the_gate.py::test_no_new_witness_is_islanded`) has been failing -- give every witness a collectable wrapper that calls its `main()` and carries a COST marker (fast / corpus / slow, with the measured wall-clock), keep the discovery gate failing until it is honest, and publish an execution manifest that says which witnesses actually ran in a given check.

**slug:** `447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest` -- **opened:** 2026-09-15 by strategy from the external substrate evaluation (E08; reproduced with the project's own checker: 465 islanded, 447 beyond `KNOWN_ISLANDED`; 622 files, 153 with test functions, 429 main-only).

> ## SOLVER OPERATING PROTOCOL (standing; full text in `notes/problems/README.md`, binding here)
> **THIS IS A MECHANICAL INSTRUMENT BRIEF (a sonnet-class agent):** no organ changes, no metric changes. Do NOT expand `KNOWN_ISLANDED` to make the gate pass; the gate passes when the files are collectable. Do NOT make the default `pytest verification/` run corpus-dependent witnesses (5-40 minutes each on the laptop): the wrapper is marked, and the default selection runs the fast tier only, with the other tiers selectable and listed.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- unaffected here; no inference code is touched.

> ## CHECKLIST (in order)
> 1. **OPEN.** (a) Inventory: for each of the 465 files, its `main()` signature, its exit convention (return code / sys.exit / assert / prints PASS-FAIL), whether it imports corpora or assets, and a measured or recorded wall-clock where the ledger/STATUS has one. (b) Add to each a wrapper of ONE shape: `def test_witness(): assert _run_main_as_test(main) == 0` via a shared helper in `verification/_witness_wrap.py` that captures stdout, maps the file's exit convention to pass/fail, and applies `pytest.mark.<tier>` (fast / corpus / slow) from a per-file annotation; register the markers in `pyproject.toml`. (c) `verification/_witness_manifest.py`: after any run, writes `data/hook_state/witness_manifest_<stamp>.json` (file, tier, ran, result, seconds) via a pytest plugin hook; `tools/witness_status.py` prints the last manifest. (d) Re-run the discovery gate: it must pass because the files are collectable, with `KNOWN_ISLANDED` SHRUNK to the files that genuinely cannot be wrapped (each with a one-line reason).
> 2. **REUSE.** `verification/test_no_witness_is_islanded_from_the_gate.py` (the checker and its allowlist), `verification/test_all_witnesses_exit_clean.py` (the subprocess wrapper for `verify_*.py` / `witness_*.py`), `tools/scorecard_gui.py --parser-smoke` (how a smoke is surfaced), the Q115 hook convention.
> 3. **GENERALIZE.** A pre-commit or gate check that a NEW `test_*.py` without a wrapper fails the discovery gate (it already does; keep it).
> 4. **BAR.** `pytest verification/ -m fast` collects and runs every fast-tier witness green; `-m "corpus or slow"` collects the rest (run a 10-file sample to prove the wrapper works on real witnesses of each exit convention); the discovery gate passes; the manifest lists every witness with its tier; a witness whose assertion is deliberately broken is detected by its tier's run (positive control on three files).
> 5. **FILES.** Write ONLY: `verification/_witness_wrap.py`, `verification/_witness_manifest.py`, `tools/witness_status.py`, the per-file wrapper hunks (as ONE unified diff `notes/problems/<slug>/witness_wrappers_patch.diff`, since it touches 465 tracked files -- strategy applies it), `pyproject.toml` (markers) as a hunk in the same diff, `notes/problems/<slug>/SOLVED.md`. Never edit hdlab/, tools/ (other than the new file), or experiments/.

## 1. THE PROBLEM IN PLAIN LANGUAGE
Most of our checks are scripts you run by hand; the standard test runner does not see them, so a green test run proves less than it looks. Give each one a small handle the runner can see, label how long it takes, and print a list of what actually ran.

## 2. WHY THIS ONE
The outside review reproduced it with our own checker; it costs nothing in capability and makes every 'witnesses green' claim auditable.

## 3. MEASURED vs INFERRED
MEASURED: 465 / 447 / 622 / 153 / 429 (the evaluation, our checker). INFERRED: the tier distribution (item 1a decides).

## 4. ALREADY TRIED / DO NOT REDO
Growing the allowlist.

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read the discovery gate file and `test_all_witnesses_exit_clean.py`; run the gate once to see the list.

## 6. THE BAR (can-fail)
See checklist item 4.

## 7. FILES AND ENTRY POINTS
See checklist item 5.

## 8. DO NOT QUOTE / DO NOT REDO
Retired figures: `notes/reference_retired_claims_never_requote.md`.
