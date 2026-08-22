#!/usr/bin/env python
"""A requested fresh run that did NOT isolate must say so, and must stay silent otherwise.

WHY THIS EXISTS. SH-7 makes `HDI_FRESH_RUN=<tag>` redirect a cell into an empty sibling so a re-run
genuinely recomputes. It only works for cells that route output through
`experiments/_seed_checkpoint.get_output_dir`. Measured 2026-08-22: 87 of the 421 cells carrying a
`units.jsonl` do (~21%), and the share of NEW cells using it fell from 90.8% in June to 27.2% in
August -- so the gap widens on its own.

**THE DANGEROUS CASE IS NOT "the redirect is unavailable". IT IS "the operator BELIEVES THEY ARE
ISOLATED AND ARE NOT."** A bare-`OUTPUT_DIR` cell ignores the variable, runs into the LANDED
directory, and rewrites `metrics.json` with a new timestamp -- so the "reproduction" proves nothing
AND mutates the record it claimed to confirm. `tools/reproduce.py` refuses such cells, but it has a
`--force`, and nothing stops anyone exporting the variable by hand.

THE SILENCE TEST IS AS LOAD-BEARING AS THE WARNING TEST. This guard sits on the hot path of every
multi-unit cell in the repo. If it fired when the variable is unset, or when isolation DID happen,
it would print on every run and be tuned out inside a day -- and this project has the measured
precedent: a detector was abandoned at a 98% firing rate because a flag firing on nearly everything
is not a flag.

    python verification/test_fresh_run_not_isolated_warns.py
"""
from __future__ import annotations

import os
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from tools import exp_checkpoint as ck  # noqa: E402


def _reset():
    ck._warned.clear()
    os.environ.pop("HDI_FRESH_RUN", None)


def test_silent_when_no_fresh_run_requested() -> bool:
    """THE ONE THAT KEEPS IT CREDIBLE: no env var, no noise, on the hot path."""
    _reset()
    with tempfile.TemporaryDirectory() as td:
        fired = ck._warn_if_fresh_run_did_not_take(os.path.join(td, "exp_anything"))
    ok = fired is False
    print(f"[witness] {'PASS' if ok else 'FAIL'} test_silent_when_no_fresh_run_requested")
    return ok


def test_silent_when_isolation_actually_happened() -> bool:
    """A cell that DID redirect must not be warned about -- otherwise the guard punishes correctness."""
    _reset()
    os.environ["HDI_FRESH_RUN"] = "tagx"
    with tempfile.TemporaryDirectory() as td:
        fired = ck._warn_if_fresh_run_did_not_take(os.path.join(td, "exp_foo__fresh_tagx"))
    _reset()
    ok = fired is False
    print(f"[witness] {'PASS' if ok else 'FAIL'} test_silent_when_isolation_actually_happened")
    return ok


def test_warns_when_fresh_run_requested_but_not_isolated() -> bool:
    """The real incident shape: variable set, cell ignored it, run is writing into the landed dir."""
    _reset()
    os.environ["HDI_FRESH_RUN"] = "tagx"
    with tempfile.TemporaryDirectory() as td:
        fired = ck._warn_if_fresh_run_did_not_take(os.path.join(td, "exp_foo"))
    _reset()
    ok = fired is True
    print(f"[witness] {'PASS' if ok else 'FAIL'} test_warns_when_fresh_run_requested_but_not_isolated")
    return ok


def test_a_different_tag_does_not_count_as_isolation() -> bool:
    """`__fresh_other` is somebody ELSE'S run. Matching on the marker alone would pass it wrongly."""
    _reset()
    os.environ["HDI_FRESH_RUN"] = "tagx"
    with tempfile.TemporaryDirectory() as td:
        fired = ck._warn_if_fresh_run_did_not_take(os.path.join(td, "exp_foo__fresh_other"))
    _reset()
    ok = fired is True
    print(f"[witness] {'PASS' if ok else 'FAIL'} test_a_different_tag_does_not_count_as_isolation")
    return ok


def test_warns_once_per_directory() -> bool:
    """A per-unit hot path must not print 12,000 times; the verdict must still be returned every call."""
    _reset()
    os.environ["HDI_FRESH_RUN"] = "tagx"
    with tempfile.TemporaryDirectory() as td:
        d = os.path.join(td, "exp_foo")
        verdicts = [ck._warn_if_fresh_run_did_not_take(d) for _ in range(5)]
        n_recorded = len(ck._warned)
    _reset()
    ok = all(verdicts) and n_recorded == 1
    print(f"[witness] {'PASS' if ok else 'FAIL'} test_warns_once_per_directory "
          f"(verdicts {verdicts}, dirs recorded {n_recorded})")
    return ok


def test_the_real_call_sites_are_wired() -> bool:
    """A helper nobody calls is not a guard. Exercise the PUBLIC functions, not the private one."""
    _reset()
    os.environ["HDI_FRESH_RUN"] = "tagx"
    with tempfile.TemporaryDirectory() as td:
        d = os.path.join(td, "exp_foo")
        os.makedirs(d)
        ck.completed_units(d)
        seen_after_read = set(ck._warned)
        ck._warned.clear()
        ck.record_unit(d, "u1", {"x": 1})
        seen_after_write = set(ck._warned)
    _reset()
    ok = len(seen_after_read) == 1 and len(seen_after_write) == 1
    print(f"[witness] {'PASS' if ok else 'FAIL'} test_the_real_call_sites_are_wired "
          f"(completed_units {len(seen_after_read)}, record_unit {len(seen_after_write)})")
    return ok


def test_data_is_still_written() -> bool:
    """WARN, NEVER RAISE. The unit data is real; only the belief about isolation is wrong."""
    _reset()
    os.environ["HDI_FRESH_RUN"] = "tagx"
    with tempfile.TemporaryDirectory() as td:
        d = os.path.join(td, "exp_foo")
        ck.record_unit(d, "u1", {"x": 1})
        got = ck.load_units(d)
    _reset()
    ok = got.get("u1") == {"x": 1}
    print(f"[witness] {'PASS' if ok else 'FAIL'} test_data_is_still_written ({got})")
    return ok


def main() -> int:
    results = [
        test_silent_when_no_fresh_run_requested(),
        test_silent_when_isolation_actually_happened(),
        test_warns_when_fresh_run_requested_but_not_isolated(),
        test_a_different_tag_does_not_count_as_isolation(),
        test_warns_once_per_directory(),
        test_the_real_call_sites_are_wired(),
        test_data_is_still_written(),
    ]
    ok = all(results)
    print(f"[witness] RESULT: {'PASS' if ok else 'FAIL'} ({sum(results)}/{len(results)})")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
