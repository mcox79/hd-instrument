"""Shared helper that turns a witness's `main()` (or bare `__main__` execution) into ONE
pytest-collectable test function, of one shape, everywhere:

    def test_witness():
        code, out = _run_main_as_test(main)
        assert code == 0, ...

WHY THIS EXISTS: see notes/problems/447_witness_files_define_no_test_function_.../PROBLEM.md.
465 of the 622 verification/test_*.py files define only a `main()` (or run their checks directly
under `if __name__ == "__main__":`) and no pytest-collectable test function, so
`pytest verification/` reports green having run NOTHING from them.

THE MAPPING IS UNIFORM ACROSS EVERY EXIT CONVENTION FOUND IN THE 465 FILES, WITHOUT PER-FILE
SPECIAL-CASING (measured 2026-09-15 over the islanded set):
  1. main() returns an int                       -> that int is the code (0 = pass)
  2. main() (or the module) raises SystemExit(c) -> c is the code (None/"" -> 0, a str -> 1)
  3. main() (or the module) relies on a bare `assert` to signal failure, returning None on
     success -> the exception propagates UNCHANGED (pytest shows the witness's own traceback,
     not a translated one) and success maps to 0
  4. main() prints "PASS"/"FAIL" text but the underlying check() helper already asserts
     internally -> covered by (3); nothing here parses printed text, because a printed word is
     not a machine-checkable signal (see test_the_detector_can_actually_fire's "a mention is not
     a use" discipline applied to output, not just source).

A witness's own stdout is captured (it is usually the whole point of running it by hand) and
folded into the assertion message on failure, so the diagnostic text is not lost behind pytest's
default output capture -- it re-emits captured stdout on any raised exception too, so a traceback
from a witness's internal check() still shows what led up to it.
"""
from __future__ import annotations

import contextlib
import io
import runpy
import sys


class _CaptureBuffer(io.StringIO):
    """`io.StringIO` plus the handful of real-`sys.stdout` methods witnesses call transitively.

    MEASURED 2026-09-15: several witnesses import (transitively, e.g. via
    `hdlab.frame_induction` -> `hdlab.learner.plugins.ruleind_plugin` ->
    `experiments.exp_parser_ruleinduction_cls_ppattach_v1`) a module whose top level calls
    `sys.stdout.reconfigure(encoding="utf-8", errors="replace")`. Plain `io.StringIO` has no
    `.reconfigure()`, so `contextlib.redirect_stdout(io.StringIO())` turned an unrelated,
    otherwise-passing witness into an `AttributeError` failure -- a bug in this wrapper, not in
    the witness. `reconfigure` is a documented no-op here: the buffer is always plain text.
    """

    def reconfigure(self, *args, **kwargs):
        return None


def _code_from_result(result) -> int:
    """Map a `main()` RETURN VALUE to an exit code. `bool` is checked BEFORE `int` -- `bool` is
    an `int` subclass in Python, so `isinstance(True, int)` is True, and a witness whose main()
    returns `True` for SUCCESS (several do, printing "ALL PASS" first) was being read with
    `True` passed straight through as the code (`True == 0` is False) -- the exact opposite of
    what it meant. Anything else (None -- by far the common case -- or any other type) means
    "no return-code convention here, only the checks inside main() decide" -> success, matching
    the documented convention that a bare witness relies on `assert` to signal failure."""
    if isinstance(result, bool):
        return 0 if result else 1
    if isinstance(result, int):
        return result
    return 0


def _code_from_system_exit(exc: SystemExit) -> int:
    """Map a `SystemExit`/`sys.exit(...)` CODE to an exit code -- same `bool`-before-`int` care
    as `_code_from_result`, but a non-int/non-bool code (e.g. `sys.exit("boom")`) means FAILURE
    here, matching real OS/Python exit-status semantics (a string argument prints to stderr and
    the process exits 1) -- the opposite convention from a plain `main()` return value, so the
    two mappings are kept as separate functions rather than unified into one "non-int -> 0"."""
    code = exc.code
    if code is None:
        return 0
    if isinstance(code, bool):
        return 0 if code else 1
    if isinstance(code, int):
        return code
    return 1


def _run_main_as_test(main, argv=None):
    """Call `main` (a zero-arg callable, or one that takes an argv list) in-process.

    Returns (exit_code, captured_stdout). 0 = pass. Any other int = fail. An exception other
    than SystemExit propagates after re-emitting the captured stdout, so pytest attributes the
    failure to the witness's own line, not to this helper.
    """
    buf = _CaptureBuffer()
    # ISOLATE sys.argv (strategy 2026-09-15, found at landing): witnesses that parse their own command line
    # (`int(sys.argv[1])`, `"--smoke" in sys.argv`) otherwise see pytest's flags ("-q", "-m", "fast"...) and
    # crash or change mode. They run exactly as `python verification/<file>.py` would.
    saved_argv = list(sys.argv)
    sys.argv = [getattr(main, "__module__", "witness") + ".py"]
    try:
        with contextlib.redirect_stdout(buf):
            result = main(argv) if argv is not None else main()
    except SystemExit as exc:
        return _code_from_system_exit(exc), buf.getvalue()
    except BaseException:
        sys.stdout.write(buf.getvalue())
        raise
    finally:
        sys.argv = saved_argv
    return _code_from_result(result), buf.getvalue()


def _run_file_as_test(path):
    """For the witnesses with no `def main():` at all -- their checks sit directly under
    `if __name__ == "__main__":` (the common case) or, rarer, at true top level with no guard.
    `runpy.run_path(path, run_name="__main__")` executes the file in-process with
    `__name__ == "__main__"`, so a guarded block fires exactly as it would from the command line,
    without paying a subprocess's startup cost. Same exit-convention mapping as
    `_run_main_as_test` above.

    NOTE (measured 2026-09-15): for the ~20 files that have NO `__main__` guard at all -- their
    checks run unconditionally at module import, i.e. already during pytest's COLLECTION of the
    file, before any test ever runs -- calling this a second time from inside test_witness() would
    re-run (and re-pay the cost of) the whole file. Those files instead get a trivial
    `def test_witness(): pass` (see the generator's NO_GUARD case): the checks already ran, and
    raised, at import if they were going to fail; the discovery gate only asks that a test
    function exist to see that something ran.
    """
    buf = _CaptureBuffer()
    try:
        with contextlib.redirect_stdout(buf):
            runpy.run_path(path, run_name="__main__")
    except SystemExit as exc:
        return _code_from_system_exit(exc), buf.getvalue()
    except BaseException:
        sys.stdout.write(buf.getvalue())
        raise
    return 0, buf.getvalue()


def _assert_ok(code, out, label="witness"):
    """Shared assertion message shape, used by every generated wrapper."""
    assert code == 0, "%s exited %r:\n%s" % (label, code, out[-4000:])
