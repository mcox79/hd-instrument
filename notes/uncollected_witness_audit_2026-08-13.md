# Uncollected-witness audit (2026-08-13)

READ-ONLY audit. No code, config, or registry row was modified. Every number below was
produced off disk in this session with `.venv/Scripts/python.exe`.

## 1. The collection rule, confirmed off disk

`pyproject.toml` lines 57-59 (read directly, not taken on report):

```toml
[tool.pytest.ini_options]
testpaths = ["verification"]
python_files = ["test_*.py"]
```

`verification/run_certification.py` line 23 shells out to:

```python
[sys.executable, "-m", "pytest", "verification/", "-v", "--tb=short"]
```

No `--override-ini`, no explicit `-p`, no alternate config path. So certification inherits
`python_files = ["test_*.py"]` verbatim.

**No competing pytest config exists.** Checked and confirmed absent at repo root and in
`verification/`: `pytest.ini`, `setup.cfg`, `tox.ini`, `conftest.py`, `setup.py`. The only
`setup.cfg` files anywhere in the tree are inside `.venv/` site-packages (numpy/f2py,
pkg_resources test fixtures) and are not on the config search path for this run. There is **no
`conftest.py` anywhere in the repo** to override `python_files`. The conclusion stands.

**The defect is not recent.** `git show 721e4215c:pyproject.toml` and
`git show ccffcd50a:pyproject.toml` both already contain `python_files = ["test_*.py"]`.
721e4215c is the initial scaffold commit (2026-05-16), and `pyproject.toml` has not been
touched since ccffcd50a (also 2026-05-16). So the glob predates *every* `verify_*.py` file in
the repo. This is not "latent since 5da76bf34" -- **no `verify_*.py` witness has ever been
collected by certification, at any commit, ever.**

Corroborating: `data/certification.md` (last generated 2026-08-12T01:01:20, exit code 0,
"260 passed, 3 skipped") contains **zero** occurrences of the string `verify_`. The report
itself is the receipt.

## 2. Counts

`verification/*.py` -- 75 files total.

| Class | Count | Collected by certification? |
|---|---|---|
| `test_*.py` | 44 | YES |
| `verify_*.py` | 25 | **NO** |
| `witness_*.py` | 2 | **NO** |
| support modules (`__init__.py`, `run_certification.py`, `oracle.py`, `theory.py`) | 4 | n/a (not witnesses; correctly uncollected) |

**27 witness files are silently not collected** (25 `verify_*` + 2 `witness_*`).

Measured collection counts (CLI override only; `pyproject.toml` untouched):

- current config: **272 tests collected**
- `python_files = "test_*.py verify_*.py witness_*.py"`: **325 tests collected** (+53)

## 3. Do the uncollected ones actually pass?

Each run standalone as `.venv/Scripts/python.exe verification/<name>.py` from the repo root,
120s cap, exit code 0 = PASS.

**18 PASS / 9 FAIL / 0 TIMEOUT.**

| # | file | result | secs |
|---|---|---|---|
| 1 | verify_additive_map_api.py | PASS | 6.0 |
| 2 | verify_affect_state_bridging_production.py | PASS | 6.4 |
| 3 | verify_capability_registry_wired_requires_real_import.py | PASS | 0.1 |
| 4 | verify_context_grounded_valence.py | PASS | 16.4 |
| 5 | verify_coreference_resolver.py | PASS | 1.6 |
| 6 | verify_dialogue_goal_recognition.py | PASS | 5.5 |
| 7 | verify_fact_store_pipeline_provenance.py | PASS | 4.4 |
| 8 | verify_goal_recognition_coverage_expansion.py | PASS | 5.5 |
| 9 | **verify_goal_typing.py** | **FAIL** | 5.7 |
| 10 | **verify_grounded_result_class_tier.py** | **FAIL** | 7.8 |
| 11 | verify_grounded_word_acquisition_increment1.py | PASS | 34.8 |
| 12 | **verify_grounded_word_acquisition_increment1b.py** | **FAIL** | 29.3 |
| 13 | verify_import_graph_scans_all_source_dirs.py | PASS | 94.4 (see note) |
| 14 | verify_integration_health_import_graph.py | PASS | 151.1 (see note) |
| 15 | verify_lemma_verb_no_nonword_stems.py | PASS | 6.7 |
| 16 | **verify_levin_lastresort_backoff.py** | **FAIL** | 5.8 |
| 17 | **verify_path_unification_2a_part1.py** | **FAIL** | 6.3 |
| 18 | verify_propara_official_eval_port.py | PASS | 1.9 |
| 19 | **verify_referent_recurrence_did_it_happen.py** | **FAIL** | 7.3 |
| 20 | **verify_request_response_typing.py** | **FAIL** | 5.6 |
| 21 | verify_self_improving_loop.py | PASS | 1.7 |
| 22 | verify_situation_model_accumulate.py | PASS | 1.7 |
| 23 | verify_situation_model_multibank_dropin.py | PASS | 1.7 |
| 24 | **verify_speaker_attribution_goal_holder_2a_part2.py** | **FAIL** | 6.8 |
| 25 | verify_state_of_mind_overlay.py | PASS | 16.1 |
| 26 | witness_consequence_learning_loop_oov_valence.py | PASS | 9.6 |
| 27 | **witness_did_it_happen_occurrence_gate_v1.py** | **FAIL** | 5.4 |

Note on rows 13/14: both hit the 120s cap in the batch sweep. Re-run individually with a 600s
cap they **both PASS** (94.4s and 151.1s). The cap was the binding constraint, not a hang.
`verify_additive_map_api.py` also timed out on the very first (cold-cache) invocation and
passes in 6.0s warm -- reported as PASS. No genuine timeouts remain.

**The headline number: 9 of 27 uncollected witnesses (33%) are failing right now.**

### The 9 failures split cleanly into two classes

**Class A -- genuine regression (4 files, one shared root cause).** A promoted organ actually
got worse and nothing caught it.

`hdlab/goal_owner_select.select_outcome_owner` has regressed from 48/48 to **46/48**, misses
`p04_meg_market_foil_amy` and `t04_meg_market_foil_amy`. Four witnesses fail on this single
defect (three of them by importing and calling `test_goal_owner_select.run()`):

- `verify_goal_typing.py` -- `explicit_psych seed=0: owner-selection accuracy 0.8888 != 1.0`,
  misses `['t03_beth_fair_foil_ruth', 't04_meg_market_foil_amy']`. This is the 18/18 claim; the
  true score is **16/18**.
- `verify_levin_lastresort_backoff.py`
- `verify_path_unification_2a_part1.py`
- `verify_speaker_attribution_goal_holder_2a_part2.py`

`t04_meg_market_foil_amy` is common to both symptom sets -- one underlying defect, four red
witnesses.

**Class B -- stale exact-equality pin (5 files). The number moved UP and the witness was never
re-baselined.** These are *not* capability regressions; they are unmaintained assertions. Each
pins `==` against a snapshot that later work improved past:

- `verify_grounded_result_class_tier.py` -- got 18, pinned 17
- `verify_request_response_typing.py` -- got 18, pinned 17
- `verify_referent_recurrence_did_it_happen.py` -- full-44 got 18, pinned 15
- `verify_grounded_word_acquisition_increment1b.py` -- got 18/36, pinned 16/36
- `witness_did_it_happen_occurrence_gate_v1.py` -- prod_sub got 10, pinned 7

Class B is still red and still means "we do not know these hold", but the honest reading is
maintenance debt, not capability loss.

## 4. The certification suite is ALREADY RED on a collected test

This was not in the original scope but it falls straight out of the Class-A root cause, and it
is the most urgent item here.

`verification/test_goal_owner_select.py` **is** collected (it has the `test_` prefix) and it
does expose the 48/48 check through a real test function at line 150,
`test_full_fair_instrument_48_of_48()`. Run directly:

```
.venv/Scripts/python.exe -m pytest verification/test_goal_owner_select.py -q
-> 1 failed, 3 passed in 21.67s
   FAILED test_goal_owner_select.py::test_full_fair_instrument_48_of_48
   AssertionError: select_outcome_owner (promoted, with tie-break) must be 48/48, got 46;
   misses=['p04_meg_market_foil_amy', 't04_meg_market_foil_amy']
```

So `python verification/run_certification.py` would **fail on `main` right now**, independent of
the collection glob. The last green certification report on disk is dated 2026-08-12T01:01:20;
the regression landed after it and no certification run has been done since. The CLAUDE.md
invariant "`python verification/run_certification.py` must pass on `main`" is currently violated.

## 5. Which claims rest on uncollected witnesses

Cross-referenced against `data/capability_registry.jsonl` (123 rows, READ ONLY -- not modified).
**10 rows cite a witness that certification does not collect.** Line numbers are 1-indexed into
the JSONL.

| line | id | integration_status | cited witness | witness state |
|---|---|---|---|---|
| 52 | `encoder_retrain_persist_generalizing_lever_reusable_v1` | WIRED | `verify_encoder_retrain_persist_loader_v1.py` | **NOT IN `verification/`** -- lives in `experiments/`, outside `testpaths` entirely |
| 53 | `situation_model_accumulate_register_organ` | WIRED | `verify_situation_model_accumulate.py` (+ `_v1.py` in `experiments/`) | PASS |
| 54 | `coreference_resolver_match_or_allocate_strict_cb_principle_b` | WIRED | `verify_coreference_resolver.py` (+ `_v1.py` in `experiments/`) | PASS |
| 55 | `self_improving_loop_coherence_gated_keep_revert_controller` | WIRED | `verify_self_improving_loop.py` | PASS |
| 65 | `context_grounded_valence` | WIRED | `verify_context_grounded_valence.py` | PASS |
| **66** | **`goal_typing_desiderative_purpose_infinitival`** | **WIRED** | **`verify_goal_typing.py`** | **FAIL** |
| **67** | **`goal_owner_full_selector_enumerate_argmax_tiebreak`** | **WIRED** | **`verify_goal_typing.py`** | **FAIL** |
| 69 | `grounded_word_acquisition_loop_increment1` | WIRED / gate SHELVE | `verify_grounded_word_acquisition_increment1.py` | PASS |
| 97 | `propara_official_eval_port` | ISLAND | `verify_propara_official_eval_port.py` | PASS |
| 103 | `maven_ere_convergence_gated_learned_causal_relation_classification` | ISLAND | `verify_integration_health_import_graph.py` | PASS |

**2 registry rows (66, 67) are backed by a witness that is failing right now.** Both are marked
`WIRED` and `promoted_wire_dont_island_2026-08-05`. Row 67's status string literally reads
`..._full_selector_pytest_certified` -- that phrase is the false claim; the pytest file it names
is the one now failing.

Three further rows (52, 53, 54) cite `verify_*_v1.py` files that live in `experiments/`, not
`verification/`. Those are outside `testpaths` and so were never collectable regardless of the
`python_files` glob -- a second, independent hole in the same gate.

`tools/capability_registry_audit.py` does **not** check that a cited witness exists, is
collected, or passes (grepped: no `python_files`/`pytest` collection logic, no witness-existence
check). So the registry audit could not have caught any of this.

None of tonight's four witnesses appear anywhere in the registry (grepped for `lemma_verb`,
`fact_store_pipeline_provenance`, `import_graph_scans`, `registry_wired_requires_real_import` --
0 matches). They are unregistered.

## 6. Tonight's four witnesses -- ALL FOUR PASS

Run cleanly, standalone, this session:

| witness | claim | result |
|---|---|---|
| `verify_capability_registry_wired_requires_real_import.py` | registry gate, 6/6 | **PASS** (rc=0, 0.1s; pytest collects 6 tests under the widened glob) |
| `verify_import_graph_scans_all_source_dirs.py` | 10/10 | **PASS** (rc=0, 94.4s; pytest collects 10 tests) |
| `verify_fact_store_pipeline_provenance.py` | provenance gate PASS | **PASS** (rc=0, 4.4s) |
| `verify_lemma_verb_no_nonword_stems.py` | PASS post-fix | **PASS** (rc=0, 6.7s) |

**Tonight's conclusions do not need revising on witness-failure grounds.** All four hold when
actually executed.

Two caveats that are worth stating rather than burying:

1. `verify_import_graph_scans_all_source_dirs.py` takes ~95-120s and exceeded a 120s cap under
   parallel load. If it is ever added to certification it roughly doubles suite runtime and sits
   close to any CI timeout.
2. `verify_fact_store_pipeline_provenance.py` and `verify_lemma_verb_no_nonword_stems.py` expose
   **zero** pytest-collectable test functions (see section 7). They pass as scripts, but adding
   `verify_*.py` to `python_files` would *not* make certification actually check them.

## 7. The proposed fix -- and why it does NOT do what it looks like it does

**NOT APPLIED. Owner's call.** The obvious repair:

```toml
python_files = ["test_*.py", "verify_*.py"]   # NOT APPLIED
```

Measured consequence, via CLI override (`-o python_files=...`), config file untouched:

- collection goes 272 -> 325 tests (**+53**)
- those 53 tests come from exactly **9 files**:

| file | tests added | current standalone result |
|---|---|---|
| verify_import_graph_scans_all_source_dirs.py | 10 | PASS |
| verify_coreference_resolver.py | 8 | PASS |
| verify_state_of_mind_overlay.py | 8 | PASS |
| verify_capability_registry_wired_requires_real_import.py | 6 | PASS |
| verify_self_improving_loop.py | 5 | PASS |
| verify_situation_model_accumulate.py | 5 | PASS |
| verify_situation_model_multibank_dropin.py | 5 | PASS |
| verify_integration_health_import_graph.py | 3 | PASS |
| verify_propara_official_eval_port.py | 3 | PASS |

**The remaining 18 witness files (16 `verify_*` + 2 `witness_*`) define zero collectable test
functions or `Test*` classes** (verified by AST parse of all 27). All of their real work sits
behind `if __name__ == "__main__":` guards, which pytest never executes.

**And here is the trap: all 9 currently-FAILING files are in that zero-test group, and all 9
files that would contribute tests currently PASS.** The split is exact, with no overlap.

So the honest answer to "how many currently-failing witnesses would start failing the
certification run" is:

> **ZERO. Adding `verify_*.py` to `python_files` would turn the suite GREENER, not redder --
> it would add 53 passing tests while still not executing a single one of the 9 real failures.**

That config change alone would manufacture a *second* false-green: 18 more files would appear
under `verification/` collection, contribute nothing, and look covered. It is worse than the
status quo, because the status quo at least does not pretend.

The real fix has to make the `__main__` bodies run -- e.g. a collected driver that shells each
uncollected witness and asserts exit code 0, or refactoring each witness's `run()` into a
`test_*` function. Either way it is a real change with a real red suite behind it, and it is
the owner's decision, not mine.

**What WOULD turn the suite red, today, with no config change at all:** the already-failing
collected test `test_goal_owner_select.py::test_full_fair_instrument_48_of_48` (section 4).
That is the honest current state of certification.

### Honest measure of "verified" status

- 27 witness files have never been executed by certification, ever.
- 9 of them (33%) fail when executed today.
- 4 of those 9 trace to one genuine regression in `select_outcome_owner` (48/48 -> 46/48).
- 5 are stale pins against numbers that later improved.
- 2 registry rows marked WIRED rest on a witness that is failing.
- 1 registry row cites a witness file that is not in `verification/` at all.
- The suite is red right now on a collected test, and the newest certification report on disk
  (2026-08-12, exit 0) is stale with respect to that.

## 8. What I could NOT verify

- **Whether the widened glob actually stays green when RUN.** I measured collection
  (`--collect-only`, 325 collected, no collection errors) but did not execute the full widened
  suite. Import-time side effects and pytest-vs-script environment differences could still
  surface failures I have not seen. The `+53 all currently pass` claim rests on those 9 files
  passing *as standalone scripts*, which is strong but not identical evidence.
- **When the `select_outcome_owner` 48/48 -> 46/48 regression landed.** I did not bisect. I know
  only that `data/certification.md` was green at 2026-08-12T01:01:20 and the test fails now.
  The responsible commit is unidentified.
- **Whether the 5 Class-B stale pins are truly "improvements".** I read the assertion messages
  (numbers moved up) and classified on that basis. I did not verify that the higher numbers are
  correct rather than a scoring change or a leak. Class B is *plausibly* benign; it is not
  *proven* benign.
- **Anything under `data/exp_structured_comparator_v1/`.** Left untouched per instruction; a run
  is in flight there. Not read, not counted.
- **Whether the standalone runs had side effects on `data/`.** All 27 witnesses were executed as
  scripts from the repo root. They are intended to be run this way, but I did not diff `data/`
  before and after, so I cannot certify the runs were side-effect-free.
- **Registry rows whose witnesses are named in prose rather than as a `.py` filename.** My
  cross-reference matched the regex `(verify|witness)_[a-z0-9_]+\.py` over each row's full JSON.
  A row that cites its evidence only narratively would not have matched.
- **`git` archaeology beyond `pyproject.toml`.** I confirmed the glob is unchanged since the
  scaffold commit; I did not audit whether `run_certification.py` ever invoked pytest differently
  in the past.

## Provenance

All numbers produced 2026-08-13 in this session, off disk, via
`D:\AI\hd-instrument\.venv\Scripts\python.exe`. No file in the repo was modified except the
creation of this notes file. `pyproject.toml` and `data/capability_registry.jsonl` were read
only. No `git add`, no `git commit`.
