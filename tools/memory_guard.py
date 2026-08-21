"""Abort a diagnostic BEFORE it eats the owner's machine.

**WHY THIS EXISTS.** 2026-08-21, owner: *"there was a task that I just killed (python) that was
taking about 8gigs of memory - it was hanging the gui and nimbalyst"*. **A process of mine made the
owner's machine unusable and they had to intervene.** That is an operational harm, not a bug report.

**I COULD NOT IDENTIFY THE CULPRIT AND I AM NOT GOING TO GUESS.** The process was already gone.
Measured afterwards: corpus loading is bounded at 12 MB/corpus (**0.11 GB** across all 28), and the
PPMI co-occurrence dictionary costs **~125 MB** on 8,000 sentences. **Neither explains 8 GB**, and
naming a cause I have not verified is exactly the failure this repo keeps paying for.

**SO THE GUARD DOES NOT DEPEND ON KNOWING THE CAUSE.** It watches RSS and aborts with a legible
message before the machine is affected, whatever the reason. *A control that only works once you
understand the failure is not a control.*

    from memory_guard import guard
    g = guard(limit_gb=2.0)      # call g() inside any loop
    for i, x in enumerate(items):
        g()                      # raises MemoryCeiling with the numbers, well before trouble
"""
from __future__ import annotations

import os
import sys

DEFAULT_LIMIT_GB = float(os.environ.get("DIAG_MEM_LIMIT_GB", "2.0"))


class MemoryCeiling(RuntimeError):
    """Raised INSTEAD of continuing. Carries the numbers so the abort is actionable."""


def _rss_gb():
    try:
        import psutil
        return psutil.Process(os.getpid()).memory_info().rss / 1e9
    except Exception:
        try:                                    # stdlib fallback, POSIX only
            import resource
            return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6
        except Exception:
            return None


def guard(limit_gb: float = DEFAULT_LIMIT_GB, every: int = 200, label: str = ""):
    """Return a callable to invoke inside a loop. Checks every `every` calls (the check itself
    costs a syscall, so calling it 10^6 times unthrottled would be its own problem)."""
    state = {"n": 0, "peak": 0.0}
    if _rss_gb() is None:
        def noop():
            return None
        print("[memory_guard] WARNING: cannot read RSS on this platform -- GUARD IS NOT ACTIVE. "
              "That is a broken guard, not a safe one.", file=sys.stderr)
        return noop

    def check():
        state["n"] += 1
        if state["n"] % every:
            return state["peak"]
        rss = _rss_gb()
        if rss is None:
            return state["peak"]
        state["peak"] = max(state["peak"], rss)
        if rss > limit_gb:
            raise MemoryCeiling(
                "%sRSS %.2f GB exceeded the %.2f GB diagnostic ceiling after %d iterations. "
                "ABORTED DELIBERATELY -- a diagnostic that hangs the owner's machine has already "
                "cost more than its result is worth. Raise DIAG_MEM_LIMIT_GB only if you have a "
                "reason, and prefer streaming or a bounded structure instead."
                % (("[%s] " % label) if label else "", rss, limit_gb, state["n"]))
        return state["peak"]

    return check


def _self_test():
    """The guard must FIRE on a real allocation and must NOT fire on a small one -- a ceiling that
    never trips is decoration, and one that trips immediately gets disabled."""
    fails = []
    # 1 MB: below the RSS of ANY Python process, so this must fire. The first version used
    # 0.05 GB and did NOT fire -- a bare interpreter sits under 50 MB, so the ceiling was above
    # current RSS and the test was wrong, not the guard. Caught by the self-test failing.
    g = guard(limit_gb=0.001, every=1, label="selftest")
    try:
        g()
        fails.append("a 1 MB ceiling did not fire -- no Python process is that small")
    except MemoryCeiling as exc:
        if "ABORTED DELIBERATELY" not in str(exc):
            fails.append("the abort message lost its explanation")
    g2 = guard(limit_gb=10_000.0, every=1, label="selftest-high")
    try:
        for _ in range(5):
            g2()
    except MemoryCeiling:
        fails.append("a 10 TB ceiling fired -- the guard cries wolf and would get disabled")
    if fails:
        print("SELF-TEST FAILED:")
        for f in fails:
            print("   -", f)
        return 1
    print("self-test PASS: fires on a ceiling below current RSS with an actionable message, and "
          "stays silent under a high one")
    return 0


if __name__ == "__main__":
    raise SystemExit(_self_test())
