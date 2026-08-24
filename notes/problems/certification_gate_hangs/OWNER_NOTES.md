---
owner_verdict: DONE
---

PROBLEM: certification_gate_hangs
STATUS: SOLVED  (premise refined — it does NOT deadlock; it is disk-starved slowness)
BAR (verbatim): "The gate returns a verdict, every time, within a stated time budget."

WHAT WAS WRONG
The mandatory gate `python verification/run_certification.py` (CLAUDE.md: "must pass on main")
was reported to "hang." It does not. It shelled `pytest verification/` with NO timeout and NO
live output. pytest's own startup/collection is disk-I/O heavy (importing the package,
enumerating every installed distribution's entry-point metadata, stat-ing the tree). When a
SECOND session runs heavy disk work at the same time — exactly the 2026-08-22 case, "during a
cell re-land" — those file reads are starved and take minutes. The process sits with flat CPU
(blocked on I/O = this repo's documented "parent CPU flat" false alarm), so a healthy-slow run
looks frozen and gets killed by hand. That kill, not a freeze, is why "nothing can be certified."

EVIDENCE IT IS SLOW, NOT DEADLOCKED
faulthandler stacks captured while "stuck" are all filesystem reads (importlib.get_data /
entry_points→read_text / pathlib.stat during collect), and consecutive dumps sit at DIFFERENT
frames = forward progress, not a lock. Measured: `import pytest` 0.2s quiet → 13s under load; a
one-line test's startup 419s under load; full-suite collection 1603s (27 min) under load vs 112s
quiet. Reproduces with all plugins disabled AND in an isolated dir with no repo config → it is
disk contention, not a plugin / the config / the 527 tests. The old runner had NO timeout
anywhere in its git history — the real defect is unbounded + invisible.

THE FIX (verification/run_certification.py — my lane; backward-compatible)
- runs under a wall-clock BUDGET (env CERT_TIMEOUT_S, default 2700s; --timeout-s);
- on expiry kills the whole pytest PROCESS TREE (witness subprocesses included);
- emits a 4th verdict, "DID NOT RUN — TIMED OUT", that NAMES what it was waiting on: collection
  state, the in-flight test, and the top of the last faulthandler stack;
- writes live progress + periodic stacks to data/certification_run/ so a slow run is visibly
  alive. It does NOT narrow what runs — the budget is a ceiling, not a deselection.

CONTROLS (all run, live)
- broken test → VERDICT FAIL, exit 1        (excludes "green by running nothing")
- unbounded hang → VERDICT TIMED OUT, exit 124, stack names the blocking stat  (excludes "a hang
  is a silent skip")
- passing test → VERDICT PASS, no stack section   (excludes "the bound breaks normal operation")
- full REAL suite under load → TIMED OUT naming the in-flight witness; collected 527; 33/34
  passed; the 1 "fail" = the ~94s witness verify_import_graph_scans_all_source_dirs hitting the
  suite's OWN 600s cap (persisted timed_out:True, secs:600.2) = contention artifact, not a defect
- full REAL suite once the box freed: collected 527, 0 failures across the tests run (in progress)
- no-deadlock: faulthandler frames advance across dumps
- no-silent-reland: 0 of 7,897 landed metrics.json changed or created during a full run

DISK OUTRANKED THE BRIEF: 527 tests collected, not 458 (and collection 34.7s → 112s quiet).

NOT ESTABLISHED
- A perfectly-uncontended full-suite green wall-clock. The box was contended (concurrent
  session, then the autoloop) throughout; every quiet window closed before a ~20-40 min full run
  could finish. This gap is environment-blocked, not solution-blocked, and is the strategy
  session's to close at integration.
- A speedup is out of scope by the brief ("do not narrow what it runs"). Follow-ups for the
  strategy session: a two-tier gate (fast subset in the loop, full suite at land — not by
  deselecting slow tests), and pre-warming pytest's entry-point/plugin scan (the exact starving
  step the stacks show).

WITHDRAW FIRST IF WRONG
The "no deadlock" claim, which rests on faulthandler dumps advancing across frames. If a future
run shows IDENTICAL stacks parked at the same lock for minutes, that is a real deadlock. The fix
is correct either way (it turns a deadlock into a loud named timeout too), so the diagnosis
withdraws before the fix.

HAND-BACK
hdlab/ needs no change — the defect and fix live entirely in verification/ (my lane) and the
pytest environment. One knob for the strategy session: set CERT_TIMEOUT_S from a measured quiet
full-run once the box is idle; under load the gate will correctly TIME OUT loud rather than hang.

REVERIFY (returns a verdict within budget instead of hanging)
python -c "import pathlib;d=pathlib.Path('data/certification_timing/controls/ctl_hang');d.mkdir(parents=True,exist_ok=True);(d/'test_ctl_hang.py').write_text('import time\ndef test_hangs_forever_control():\n    time.sleep(100000)\n')" && .venv/Scripts/python.exe verification/run_certification.py --target data/certification_timing/controls/ctl_hang --timeout-s 25 --output data/certification_timing/report_ctl_hang.md
# expect: VERDICT "DID NOT RUN — TIMED OUT", exit 124, within ~27s

FILES CHANGED
- verification/run_certification.py                      (the fix)
- experiments/exp_certification_gate_timing_probe.py     (diagnosis harness)
- data/certification_timing/controls/{ctl_pass,ctl_fail,ctl_hang}/  (control fixtures)
- notes/problems/certification_gate_hangs/SOLVED.md

VALIDATION: python tools/problem_ledger.py --check  →  malformed/incomplete: 0
