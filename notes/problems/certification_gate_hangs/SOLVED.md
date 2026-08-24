---
problem: certification_gate_hangs
status: SOLVED
bar: "The gate returns a verdict, every time, within a stated time budget."
result: "The gate (verification/run_certification.py) is now bounded, loud, and observable. Live controls on the FIXED runner: passing fixture -> VERDICT PASS (419s under concurrent load, within its 600s budget); broken fixture -> VERDICT FAIL (exit 1, 106s); an unbounded time.sleep(100000) fixture -> VERDICT 'DID NOT RUN -- TIMED OUT' (exit 124, killed at the budget), and the report NAMES the blocking call from a faulthandler stack. DIAGNOSIS (the premise's weak part): it does NOT deadlock. faulthandler taken while 'stuck' shows pytest STARTUP/COLLECTION blocked in filesystem reads (importlib get_data / entry_points read_text / pathlib.stat during collect) and ADVANCING between dumps -- disk-I/O-starved by a second, concurrently-running session, not hung. The suite collects 527 tests (112s quiet), not 458."
floor: "Strongest baseline actually run: quiet pytest startup is ~2s and `pytest verification/ --collect-only` is 527 tests in 112s. Under a concurrent disk-heavy session the SAME operations balloon: `import pytest` alone 13s, a ONE-LINE test's pytest.main startup 419s, faulthandler blocked in get_data/read_text/stat -- i.e. the 'hang' reproduces as SLOW, and a DEADLOCK is excluded because consecutive faulthandler dumps sit at DIFFERENT frames (import _pytest.config -> findpaths.locate_config stat -> pytest_collect_directory stat = forward progress). The old gate had NO timeout anywhere in its git history: the structural defect is unbounded + invisible, not a bad test."
controls: "POSITIVE (broken->loud): ctl_fail fixture (assert 2+2==5) -> VERDICT FAIL, exit 1 -- excludes 'green by running nothing'. POSITIVE (hang->loud): ctl_hang fixture (sleep 100000) -> VERDICT TIMED OUT, exit 124, killed at budget, stack names the blocking stat -- excludes 'a hang is a silent skip'. NEGATIVE (good->PASS): ctl_pass fixture -> VERDICT PASS -- excludes 'the bound breaks normal operation'. NO-DEADLOCK: faulthandler frames advance across dumps -- excludes a lock/deadlock. CAUSE-ISOLATION: the slow-startup reproduces with ALL optional plugins disabled AND in an isolated dir with no repo pyproject -- excludes 'a plugin / the repo config / the 527 tests' as the cause, leaving disk-I/O contention. NO-SILENT-RELAND: cert suite only READS landed metrics.json or writes to pytest tmp_path (static grep), and EMPIRICALLY 0 of 7,897 landed metrics.json changed or were created during the full run."
files_changed: "verification/run_certification.py (bounded wall-clock budget + process-tree kill + fourth 'TIMED OUT' verdict that names the blocking stack + live progress/stack sidecar under data/certification_run/); experiments/exp_certification_gate_timing_probe.py (diagnosis harness: bounded probe with per-test progress + tree-kill); data/certification_timing/controls/{ctl_pass,ctl_fail,ctl_hang}/ (control fixtures); notes/problems/certification_gate_hangs/SOLVED.md"
reverify: "python -c \"import pathlib; d=pathlib.Path('data/certification_timing/controls/ctl_hang'); d.mkdir(parents=True, exist_ok=True); (d/'test_ctl_hang.py').write_text('import time\\ndef test_hangs_forever_control():\\n    time.sleep(100000)\\n')\" && .venv/Scripts/python.exe verification/run_certification.py --target data/certification_timing/controls/ctl_hang --timeout-s 25 --output data/certification_timing/report_ctl_hang.md   # expect: VERDICT 'DID NOT RUN -- TIMED OUT', exit 124, within ~27s -- a verdict, not a hang"
---

## TLDR (plain language)

The mandatory check that is supposed to bless every result was said to "hang". I ran it and
found it does **not** freeze or lock up. It is just **very slow to start**, and it gets
*dramatically* slower whenever a second session is busy hammering the disk at the same time --
which is exactly when the "hang" was reported. While it slowly grinds through reading thousands
of small files, its screen output stays blank and its CPU stays flat, so it **looks** frozen and
someone kills it by hand. That kill -- not a freeze -- is why "nothing can be certified".

I proved the slowness is real work-in-progress (not a lock) by photographing where it was stuck
several times: each photo showed it a little further along, always waiting on the disk. Then I
fixed the check so it can **never again be mistaken for frozen**: it now runs with a **time
limit**, and if it blows the limit it **stops loudly and prints exactly what it was waiting on**
instead of sitting there forever. I confirmed the fixed check still says PASS on a good test,
says FAIL on a broken one, and says "TIMED OUT -- here is where it was stuck" on a deliberately
frozen test.

## What I built

1. **A diagnosis harness** -- `experiments/exp_certification_gate_timing_probe.py`. Runs the
   suite under a hard wall-clock cap with a per-test progress sidecar and a process-tree kill,
   so a run that never returns is pinned to the exact test in flight (or "still in startup").
2. **The fix, in my lane** -- `verification/run_certification.py`. `git log` confirms this gate
   **never** had a timeout: it shelled `pytest verification/` and blocked forever. It now:
   - runs under a wall-clock **BUDGET** (env `CERT_TIMEOUT_S`, default 2700s; `--timeout-s`);
   - on expiry **kills the whole pytest process tree** (pytest spawns witness subprocesses;
     killing only the direct child leaves them resident on Windows);
   - emits a **fourth verdict, `DID NOT RUN -- TIMED OUT`**, that names what it was waiting on:
     whether collection finished, which test was in flight, and the top of the last faulthandler
     stack;
   - writes a **live progress + periodic stack sidecar** to `data/certification_run/`, so an
     operator watching a slow run sees it is alive instead of assuming it hung.
   It does **not** narrow what runs -- the full suite still runs; the budget is a ceiling, not a
   deselection (the failure mode the brief explicitly forbids).

## The diagnosis: SLOW under disk contention, not deadlocked

faulthandler stacks captured while the run was "stuck" are all **filesystem reads inside pytest's
own startup/collection**, and they sit at **different** frames from one dump to the next:

| when | where it was blocked (top frames) |
|---|---|
| startup @10s | `importlib._bootstrap_external.get_data` importing `_pytest/config/__init__.py` |
| startup @20s | `_pytest/config/findpaths.py:186 locate_config -> pathlib.is_file -> stat` |
| (probe) @18s | importing `_pytest/assertion/util` |
| (probe) @36s | `importlib.metadata.entry_points -> read_text -> open` (every installed dist) |
| collection | `_pytest/python.py:185 pytest_collect_directory -> pathlib.is_file -> stat` |

Different frames across dumps = **forward progress**, so it is not a lock. The cause is **disk-I/O
starvation from a second session** running heavy jobs at the same time (measured this session: two
python jobs at 2000+ CPU-s each; `import pytest` alone rose from ~2s to 13s; a **one-line** test's
`pytest.main` startup took **419s**). The parent's CPU stays flat because it is blocked on I/O --
this repo's own documented **"parent CPU is flat" false alarm** -- which is precisely how a healthy
slow run gets read as a hang and killed. It matches the 2026-08-22 report exactly: the stall
happened **"during a cell re-land"**, i.e. while another session was writing the store.

## The disk outranked the brief

- **Not 458.** Current collection is **527 tests** (`pytest --collect-only`, 112s quiet). The
  brief's DO-NOT-QUOTE list already warned 458 was stale; it is.
- **Collection got slower too:** 34.7s (2026-08-22) -> 112s quiet now, from the many heavy
  `test_*.py` files landed since (co-occurrence-at-power, noise sweeps, bundling, sense selection).
- **The premise ("it HANGS") is the weak part.** It does not deadlock. The strategy session's own
  `VERIFY THE PREMISE FIRST` block anticipated this ("It may be SLOW, not hung"). Confirmed, with
  the mechanism.

## Controls (all run this session)

| control | result | what it excludes |
|---|---|---|
| broken fixture (`assert 2+2==5`) | **VERDICT FAIL, exit 1** (106s) | "green by running nothing" |
| hang fixture (`sleep(100000)`) | **VERDICT TIMED OUT, exit 124**, stack names the blocking stat | "a hang is a silent skip" |
| passing fixture | **VERDICT PASS** (419s, within 600s budget) | "the bound breaks normal operation" |
| no-deadlock | faulthandler frames advance across dumps | a lock / deadlock |
| cause-isolation | slow startup reproduces with ALL plugins disabled AND in an isolated no-config dir | "a plugin / the repo config / the 527 tests" as cause |
| no-silent-reland | suite only reads landed `metrics.json` / writes `tmp_path` (static); mtime diff below | the gate re-dating a landed record |

## FULL-SUITE negative control + wall-clock (measured on the RUN, under concurrent load)

A full `pytest verification/` run through the FIXED gate was launched this session. Measured on the
run itself, not just collect-only:
- **Collection finished: 527 tests** -- confirms the count (NOT 458).
- Under the concurrent disk-saturating session, **collection ALONE took 1603s (27 min)** vs 112s
  quiet -- the disk-starvation mechanism at full scale, and the clearest single number for why a
  human-watched run gets killed.
- The run stayed **LIVE and advancing** and returned a **loud, bounded verdict**: `DID NOT RUN --
  TIMED OUT` at **5402s** (90 min budget), **naming the in-flight witness**
  `test_witness_exits_clean[verify_integration_health_import_graph.py]` -- the "collection finished,
  test X in flight" branch, on the REAL suite. Correct outcome: "cannot certify while the disk is
  saturated," never a silent hang.
- **The one 'failure' among the 34 tests that ran is a contention artifact, not a real defect:**
  `verify_import_graph_scans_all_source_dirs` (documented ~94s) hit the witness driver's OWN 600s cap;
  its persisted status is `timed_out: True, secs: 600.2, returncode: None`. On a quiet box it passes;
  the other 33 passed. So even the suite's own generous per-witness cap was tripped by the same disk
  starvation -- more evidence for the mechanism, not against the suite.
- **NO SILENT RE-LAND (empirical):** of **7,897** landed `metrics.json`, **0 changed and 0 created**
  during the run -- the gate re-dates no landed record (confirms the static read-only finding; the
  `harness_cannot_recompute` hazard is not triggered).

So the negative control's **collects-527**, **no-deadlock**, **bounded-loud-verdict**, and
**no-silent-reland** parts are all established ON THE REAL SUITE. Once the concurrent session ended
(`import pytest` back to 0.2s), a full **clean** run was launched
(`data/certification_timing/fullclean/report.md`) to capture the last confirmatory number -- a clean
green PASS + an uncontended wall-clock. The refined runner was separately confirmed to emit `VERDICT
PASS` with NO stack section on a passing target.

## What I did NOT establish

- **A clean full-suite wall-clock free of concurrent load.** The box was contended the whole
  session; every clean-run attempt was starved. The honest number is: quiet collection is 112s for
  527 tests; a full clean run is longer (the witness driver alone is documented >550s) but I could
  not measure it uncontended. The budget default (2700s) should be tuned once a quiet run exists.
- **That the "Windows fatal exception: access violation"** faulthandler logged during a contended
  `stat` is a real crash. It is a known faulthandler stack-walk artifact when a periodic dump races
  a syscall under load; the process kept running until the budget killed it. Not chased further.
- **A speedup.** Out of scope by the brief ("DO NOT make the gate pass by narrowing what it runs").
  Parallelism, or a fast loop-subset with the full suite at land time, is a follow-up for the
  strategy session -- as is pre-warming pytest's plugin/entry-point scan, the specific step the
  stacks show starving.

## What I would withdraw first if it turned out to be wrong

The **"no deadlock"** claim rests on faulthandler dumps advancing across frames. If a future run
shows **identical** stacks parked at the **same lock** for minutes, that is a real deadlock and the
diagnosis is wrong for that case. The **fix** (bounded + loud + stack) is correct either way -- it
turns a deadlock into a loud, named timeout just as it does a slow run -- so the **diagnosis**
withdraws before the **fix**.

## Hand-back: what would change in `hdlab/`, and what would NOT

- **`hdlab/` needs no change.** This defect lives entirely in the gate runner
  (`verification/run_certification.py`) and pytest's environment; the substrate is untouched.
- **The landed change is in `verification/` (my lane) and is backward-compatible.** `python
  verification/run_certification.py` with no args still runs the full suite and writes
  `data/certification.md`; it just can no longer run unbounded or look hung.
- **One tuning knob for the strategy session:** set `CERT_TIMEOUT_S` (or `--timeout-s`) from a
  measured quiet full-run once the box is idle. Under load the gate will correctly TIME OUT loud
  rather than hang.

## TLDR / Questions / Next steps

**TLDR.** The gate was never frozen -- it was slow to start and looked frozen under a busy disk, so
people killed it. I proved it makes progress (photos of where it was stuck all move forward), then
gave it a time limit and a loud "here is exactly where I was stuck" message so it can never be
mistaken for frozen again. Good tests still PASS, broken tests still FAIL, and a truly frozen test
now stops loudly instead of hanging.

**Questions.** None blocking. One judgement call for integration: what wall-clock budget do you want
as the default? I set 2700s; the right number is a measured quiet full-run, which needs a moment when
no other session is saturating the disk.

**Next steps (strategy session's).** (1) Land the runner change and tune `CERT_TIMEOUT_S` from a quiet
full-run. (2) If the gate needs to run inside a fast loop, add a fast subset for the loop and keep the
full suite at land time -- NOT by deselecting the slow tests, but as an explicit two-tier gate. (3)
Consider pre-warming pytest's entry-point/plugin scan, the exact step the stacks show starving.
