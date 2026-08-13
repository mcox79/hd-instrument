# `experiments/_seed_checkpoint.py` uncommitted delta — evaluation (2026-08-13)

**Read-only evaluation. Nothing staged, nothing committed, no process touched.**

**HEADLINE: this is NOT orphan/abandoned work. It is a MISSING COMMIT that 60 already-committed
experiment cells depend on. HEAD is the broken state, not the worktree.**

---

## 1. What the change actually is (verified line count)

- Worktree: **1144 lines**. `git show HEAD:experiments/_seed_checkpoint.py`: **1043 lines**.
- `git diff --numstat HEAD`: **104 insertions, 3 deletions** = 107 changed lines, **net +101**.
- The "~100 lines" figure in the brief is accurate.

| # | Symbol | Status | One-line description |
|---|--------|--------|----------------------|
| 1 | `write_metrics()` | MODIFIED (-1/+8) | Final `metrics.json` now written tmp-file + `os.replace()` instead of a direct `write_text()`. |
| 2 | `VacuousSmokeError(AssertionError)` | NEW class | Raised when a smoke/self-test's negative control PASSED the headline gate. |
| 3 | `assert_discriminator_fires(...)` | NEW function | Smoke gate: the must-fail control must actually fail; no-op pass-through on FULL; returns `True` so it folds into `ok &= ...` chains. |
| 4 | `__all__` | MODIFIED (+2) | Exports `assert_discriminator_fires`, `VacuousSmokeError`. |
| 5 | `__main__` self-test | EXTENDED (+~38) | T9 (guard: passes on failing control, raises on passing control, no-ops on FULL, aliases `self_test`/`self-test`/`selftest`) and T10 (atomic write: file present, **no `.tmp` residue**, `elapsed_s`/`summary` injected). Banner 8 -> 10 tests. |

## 2. Date and attribution — ATTRIBUTABLE, not anonymous

- Code self-dates: `# --- Vacuous-smoke discriminator-fires guard (added 2026-07-08, Testbed) ---`,
  naming the two cells that motivated it (`twoband`, `twohead`).
- **Corroborating memory file, same date**:
  `C:\Users\marsh\.claude\projects\D--AI\memory\feedback_saturation_vacuous_smoke_discriminator_must_fire_at_scale_2026-07-08.md`
  — describes exactly the two-head (V~1500 smoke -> V=40000 HARD_FAIL) and two-band
  (every arm incl. `singlecode_native` frontier control passed at V=1500) episodes, and states:
  *"Now enforced by `assert_discriminator_fires()` in `_seed_checkpoint.py`"* and
  *"Enforced in-repo: `from _seed_checkpoint import assert_discriminator_fires`."*
  **The documentation already asserts this code is landed.**
- `tools/orchestrator/agents/exp_dev.md` (COMMITTED) instructs cell authors at line 112:
  `from _seed_checkpoint import assert_discriminator_fires  # already the cell's shared import`.
- Commit history of the file: `10d5f6f9c` **2026-08-13 13:22:30** (SH-6, today),
  `0e871ff2a` 2026-07-05, `8a28cd58b` 2026-07-03. **No commit at all between 07-05 and today.**
  So the 07-08 work had exactly one commit opportunity (today's SH-6) and was partially
  staged around, as the SH-6 author documented they intended.
- Worktree mtime is **today 13:17:38** — that is the SH-6 edit (committed 13:22:30); it does
  **not** date the delta. Do not read mtime as evidence the delta is new.
- Not in any branch, stash, or reflog: `git log --all -S 'assert_discriminator_fires' -- experiments/_seed_checkpoint.py` -> empty.

## 3. Does it work? — YES, both green

- `.venv/Scripts/python.exe experiments/_seed_checkpoint.py` -> exit 0,
  `[selftest] T9 PASS: assert_discriminator_fires gates vacuous smoke; no-ops on FULL`,
  `[selftest] T10 PASS: write_metrics atomic (tmp+replace, no residue)`,
  `ALL 10 TESTS PASS`. T1-T8 (pre-existing) also pass -> no regression in existing behaviour.
- `pytest verification/test_selftest_output_isolation.py -q` -> **4 passed**, exit 0.
  (This is today's SH-6 suite; it exercises the module and is unaffected by the delta.)
- Beyond "it works in test": the guard has been **executing in production for 36 days** —
  `data/exp_cls_ca3complete_consolidation_v1/metrics.json` mtime **Jul 8 11:53** (the day it was
  written), `data/exp_script_grain_acquisition_loop_v1/metrics.json` mtime **Aug 9**.

## 4. Dependents — and what is actually running

- `from experiments._seed_checkpoint import ...` appears in **3708** files under
  `experiments/ hdlab/ verification/` (module-wide, not this delta).
- **`assert_discriminator_fires` specifically: 61 files under `experiments/` — 60 caller cells
  plus the module itself.** Spot-checked callers (`exp_script_grain_acquisition_loop_v1`,
  `exp_cls_ca3complete_consolidation_v1`, `exp_predictive_coding_relative_threshold_v1`) are
  **git-tracked and CLEAN**, and import the symbol in a **hard `from ... import (...)` tuple with
  no try/except fallback**.
- **`git show HEAD:experiments/_seed_checkpoint.py | grep -c assert_discriminator_fires` -> 0.**
  So a clean checkout of HEAD **ImportErrors at module load on all 60 cells**.
- Other importers: `hdlab/harness.py` (re-exports the module as SHARED HARNESS),
  `verification/test_selftest_output_isolation.py`.

### Are the two live runs using it? — **NO. Verified negative.**

- PID **30436 / 29384** ALIVE (started 13:32:39 today):
  `.venv\Scripts\python.exe experiments/exp_wire_definitional_v1.py --mode full --arm all`.
- PID **9260 / 29624** (`exp_anchor_pool_expansion_v1`) **not in the process table** — that run has
  already exited; its `metrics.json` is on disk.
- `exp_wire_definitional_v1.py`: **0** matches for `_seed_checkpoint` / `write_metrics` /
  `assert_discriminator_fires`. It uses `tools.exp_checkpoint` instead.
- Transitive check of all its local imports — `tools/exp_checkpoint.py`,
  `experiments/exp_anchor_pool_expansion_v1.py`, `exp_reading_grounding_loop_cycle1_v1.py`,
  `exp_reading_grounding_loop_cycle2_v1.py`, `exp_definitional_grounding_v5.py`,
  `hdlab/reading_grounding_loop.py`, `hdlab/hd_fact_store.py`, `hdlab/closed_class_lexicon.py`
  — **all 0 matches for `_seed_checkpoint`.**
- **Conclusion: neither live run touches this module. Editing/committing it cannot disturb them.
  This is NOT time-critical.**

## 5. The atomic-write change — precise assessment

What it does: replaces `(out_dir/"metrics.json").write_text(...)` with write-to-`metrics.json.tmp`
then `os.replace(tmp, final)`. **This is genuinely atomic**, not atomic-in-name-only: `os.replace`
is an atomic rename within a filesystem on POSIX and an atomic overwrite on Windows. It also
matches a convention **already established in this same module since 2026-05-28** — `write_partial`
has used tmp + `os.replace` for per-seed partials all along (HEAD has 1 occurrence, worktree has 2).
So the delta closes an inconsistency rather than introducing a new pattern.

**Would it have prevented today's clobbering? NO.** Per `10d5f6f9c`'s own message, the damage was a
**self-test run writing a complete, valid metrics.json to the SAME path** as a prior full run —
because those four cells hold a bare module-level `OUTPUT_DIR` and never called `get_output_dir()`,
and SH-5 keyed off the literal string `--self-test` in argv while a bare `python exp_foo.py`
defaults to self-test with no flag present. Atomicity is orthogonal to that: it would have made the
overwrite cleanly atomic. The correct fix for that class is the **path isolation** already landed
today as `isolate_selftest_output_dir` (SH-6). Likewise the fifth cell's **NaN/zero** state was a
degenerate-input defect (`load_provenance_glosses` returning `({}, [])`), also a complete write.

What the atomic write DOES prevent is the **torn-read** class its comment claims: a concurrent
metrics-sync tar / `verify_landing` catching a half-written `metrics.json` and framing a landed FULL
as unreadable. That is a real but different failure mode, and no evidence of it was gathered here.
**Do not credit this change for today's incident.**

## 6. The vacuous-smoke guard vs the known failure class

Direct match, and it is the *enforcement* of that class. What it detects: at the smoke's V/N, the
arm that MUST fail (frontier / negative control) instead PASSED the headline gate -> the
discriminator does not fire -> the smoke tests nothing -> the FULL later HARD_FAILs. It raises
`VacuousSmokeError` only in `smoke`/`self_test`/`selftest` modes, and is a **no-op on FULL**.

Relation to recorded notes: it is the coded form of
`feedback_saturation_vacuous_smoke_discriminator_must_fire_at_scale_2026-07-08` (which explicitly
names it), in the family of `feedback_discriminator_must_survive_scale_before_full_dispatch_USER_2026-06-26`
and `feedback_discriminator_must_be_telemetry_sensitive_not_analytically_pinned_2026-07-08`.

**Tension checked, and it is clean:** `feedback_smoke_gates_null_hypothesis_should_not_gate_on_discriminator_firing_2026-07-03`
says a null-hypothesis cell must NOT gate its smoke on the discriminator firing. The guard does
**not** auto-gate anything — it is opt-in, called explicitly by the cell author with an explicit
control bool. A null-under-test cell simply does not call it. No conflict.

## 7. Risk

**If we commit it:**
- Breakage risk: **very low, arguably negative risk.** Both self-tests pass; T1-T8 unchanged;
  no live run imports it; the code has been the executing version for 36 days across 60 cells.
- Only new artifact is a transient `data/exp_*/metrics.json.tmp`. Checked: no tooling globs
  `metrics.json*`, and `.json.tmp` does not match a `*.json` glob. `.json.tmp` residue is already an
  understood, documented artifact of `write_partial`.
- Regression evidence available: the 10-test module self-test (T9/T10 cover the new code directly)
  and `verification/test_selftest_output_isolation.py` (4 passed). Note T9/T10 were authored
  alongside the change, so they are author-written, not independent — but T10 does assert the
  can-fail property (no `.tmp` residue) and T9's middle branches are genuine can-fail assertions.

**If we leave it:**
- **HEAD is a non-buildable state for 60 committed cells.** Any fresh clone, `git checkout` of
  HEAD, worktree, or remote/GPU dispatch that ships HEAD's `_seed_checkpoint.py` ImportErrors those
  cells at module load. The remote runners are the live hazard here, not the local box.
- Committed documentation (`tools/orchestrator/agents/exp_dev.md` line 112) and a USER-filed memory
  file both instruct authors to import a symbol that does not exist in HEAD. Every new cell written
  to spec inherits a latent ImportError.
- Every future partial-stage of this shared file (this already happened once, today) risks the
  delta being reverted by a `git checkout`/`git restore` — which would silently disarm the
  #1-experiment-error-class guard across 60 cells.
- The atomic-write half stays unlanded, leaving the torn-read window open.

## 8. Recommendation: **COMMIT** (as one commit, both hunks)

Reasoning:
1. **This is not adoption of speculative work — it is restoring the repo to a consistent state.**
   60 committed, clean cells already import `assert_discriminator_fires`; HEAD does not define it.
   Leaving it uncommitted keeps HEAD broken for a fifth of `experiments/`.
2. It is fully attributable to a dated, USER-filed methodology episode (2026-07-08), and the
   documentation of record already asserts it is landed. Committing makes docs true.
3. Both self-tests pass and the code has been the de-facto executing version for 36 days.
4. Nothing currently running imports it, so there is no window to wait for.

Do **not** SPLIT: the two hunks share the self-test block (T9 and T10 are in the same `with tempfile`
scope and one banner line), and splitting invites a repeat of the partial-stage that created this.

Do **not** REVERT: reverting deletes the enforcement of the recorded #1 experiment-error class and
breaks 60 cells outright.

**Two caveats to carry into the commit message, not to block on:**
- Do **not** claim the atomic write fixes today's clobbering. It does not. SH-6 does.
- T9/T10 are author-written alongside the change; an independent can-fail check of the atomic write
  (e.g. a torn-read reproduction) has never been run. State that plainly rather than implying it.

---

### What was checked before concluding (per the triple-check standing instruction)

Right file (`D:\AI\hd-instrument\experiments\_seed_checkpoint.py`, branch
`dataprep/mcguffey-graded-corpus`), right comparison (`git diff HEAD` on that path only, plus
`git show HEAD:` of the same path). The brief's "sitting uncommitted for over a month" framing was
tested and **partly corrected**: the *content* is ~36 days old (corroborated independently by a
same-dated memory file and by Jul-8 production metrics on disk), but HEAD's version of the file was
committed **today**, and the delta's claim to be load-bearing was verified by finding 60 committed
callers and proving the symbol is absent from HEAD (`grep -c` -> 0). The mtime was explicitly ruled
out as a dating signal. The live-run question was answered by process-table command lines plus a
transitive import walk, not by assumption.
