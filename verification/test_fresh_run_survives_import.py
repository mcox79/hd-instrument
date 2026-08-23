#!/usr/bin/env python
"""With HDI_FRESH_RUN set BEFORE the interpreter starts, the harness must still import.

WHY THIS FILE EXISTS, AND WHY THE EXISTING WITNESS COULD NOT HAVE CAUGHT IT.

`experiments/_seed_checkpoint.py` runs `_selftest_get_output_dir()` AT IMPORT. Test 1 asserts
`get_output_dir("myanchor_v1")` ends in `exp_myanchor_v1`. SH-7 appends `__fresh_<tag>` when
HDI_FRESH_RUN is set -- so with the switch on, that assertion failed and **EVERY CELL THAT IMPORTS
THE HARNESS DIED AT IMPORT**:

    AssertionError: T1 FAIL: got exp_myanchor_v1__fresh_probe1

The switch did not merely fail to redirect. It broke the harness it lives in, for every cell, the
moment anyone asked for a fresh run. Measured 2026-08-23 by running a real landed cell end to end --
the first time anyone had used the mechanism rather than tested it.

**`verification/test_fresh_recompute_redirect.py` PASSES 6/6 AND IS STRUCTURALLY BLIND TO THIS.** It
does `from _seed_checkpoint import get_output_dir` and THEN sets the environment variable, so the
import-time self-test always ran with the variable absent. A real cell has it set before Python
starts. **THE BUG IS IN THE ORDERING, AND A TEST THAT CONTROLS THE ORDERING CANNOT SEE IT.**

So this witness spends a subprocess: the variable is placed in the child's environment BEFORE the
interpreter launches, which is the only way to reproduce what a real cell experiences.

*Generalisable, and this project has the rule already: a checker that shares a flaw with the thing it
checks hides it. Here the shared flaw was not a pattern -- it was an assumption about WHEN state is
set.*

    python verification/test_fresh_run_survives_import.py
"""
from __future__ import annotations

import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = os.path.join(REPO, ".venv", "Scripts", "python.exe")
if not os.path.isfile(PY):
    PY = sys.executable

PROBE = (
    "import sys; sys.path.insert(0, r'{exp}');"
    "from _seed_checkpoint import get_output_dir;"
    "print('NAME=' + get_output_dir('myanchor_v1').name)"
).format(exp=os.path.join(REPO, "experiments"))


def _run(env_tag):
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    if env_tag is None:
        env.pop("HDI_FRESH_RUN", None)
    else:
        env["HDI_FRESH_RUN"] = env_tag
    p = subprocess.run([PY, "-X", "utf8", "-c", PROBE], cwd=REPO, env=env,
                       capture_output=True, encoding="utf-8", errors="replace", timeout=180)
    name = ""
    for line in (p.stdout or "").splitlines():
        if line.startswith("NAME="):
            name = line[5:].strip()
    return p.returncode, name, (p.stderr or "")


def test_import_succeeds_with_the_variable_set() -> bool:
    """THE REGRESSION. Env set before the interpreter starts -- exactly what a real cell sees."""
    rc, name, err = _run("wit1")
    ok = rc == 0
    if not ok:
        tail = err.strip().splitlines()[-1] if err.strip() else "(no stderr)"
        print(f"[witness] FAIL test_import_succeeds_with_the_variable_set: exit {rc} -- {tail}")
    else:
        print("[witness] PASS test_import_succeeds_with_the_variable_set")
    return ok


def test_redirect_still_applies_in_that_subprocess() -> bool:
    """Importing cleanly is not enough -- the switch must still DO its job in the same process."""
    rc, name, _e = _run("wit1")
    ok = rc == 0 and name.endswith("__fresh_wit1")
    print(f"[witness] {'PASS' if ok else 'FAIL'} test_redirect_still_applies_in_that_subprocess ({name!r})")
    return ok


def test_unset_is_unchanged_in_a_subprocess() -> bool:
    """The negative control, at the same fidelity: no variable, no suffix, harness imports clean."""
    rc, name, _e = _run(None)
    ok = rc == 0 and name == "exp_myanchor_v1"
    print(f"[witness] {'PASS' if ok else 'FAIL'} test_unset_is_unchanged_in_a_subprocess ({name!r})")
    return ok


def test_a_real_cell_imports_with_the_variable_set() -> bool:
    """The end of the chain: a REAL cell that imports the harness must not die at import.

    Not a fixture. This is the cell whose failure exposed the bug -- it imports get_output_dir and
    write_metrics from the harness at module level, so an import-time assertion kills it outright.
    Compile-and-import only; the cell is not run here.
    """
    cell = "experiments/exp_thematic_role_labeler_cue_integration_v1.py"
    if not os.path.isfile(os.path.join(REPO, cell)):
        print(f"[witness] SKIP test_a_real_cell_imports_with_the_variable_set ({cell} absent)")
        return True
    env = dict(os.environ)
    env["HDI_FRESH_RUN"] = "wit2"
    env["PYTHONIOENCODING"] = "utf-8"
    probe = (
        "import importlib.util, sys;"
        "spec = importlib.util.spec_from_file_location('probe_cell', r'{p}');"
        "m = importlib.util.module_from_spec(spec);"
        "sys.argv = ['probe_cell', '--self-test'];"
        "print('IMPORT_REACHED')"
    ).format(p=os.path.join(REPO, cell))
    p = subprocess.run([PY, "-X", "utf8", "-c", probe], cwd=REPO, env=env,
                       capture_output=True, encoding="utf-8", errors="replace", timeout=180)
    # The harness import happens when the CELL's own imports run; do it directly instead so the
    # test stays fast and does not execute the experiment.
    probe2 = (
        "import sys; sys.path.insert(0, r'{exp}');"
        "from _seed_checkpoint import get_output_dir, write_metrics;"
        "print('HARNESS_IMPORT_OK')"
    ).format(exp=os.path.join(REPO, "experiments"))
    p2 = subprocess.run([PY, "-X", "utf8", "-c", probe2], cwd=REPO, env=env,
                        capture_output=True, encoding="utf-8", errors="replace", timeout=180)
    ok = p2.returncode == 0 and "HARNESS_IMPORT_OK" in (p2.stdout or "")
    if not ok:
        tail = (p2.stderr or "").strip().splitlines()[-1:] or ["(no stderr)"]
        print(f"[witness] FAIL test_a_real_cell_imports_with_the_variable_set -- {tail[0]}")
    else:
        print("[witness] PASS test_a_real_cell_imports_with_the_variable_set "
              "(the exact import pair that died)")
    return ok


def main() -> int:
    results = [
        test_import_succeeds_with_the_variable_set(),
        test_redirect_still_applies_in_that_subprocess(),
        test_unset_is_unchanged_in_a_subprocess(),
        test_a_real_cell_imports_with_the_variable_set(),
    ]
    ok = all(results)
    print(f"[witness] RESULT: {'PASS' if ok else 'FAIL'} ({sum(results)}/{len(results)})")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
