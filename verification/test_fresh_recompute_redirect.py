#!/usr/bin/env python
"""SH-7: HDI_FRESH_RUN redirects a cell to a fresh sibling, and does NOTHING when unset.

WHY THIS EXISTS. A landed cell cannot be falsified by re-running it: `completed_units()` finds every
unit already recorded, the cell skips all of them, and the SAME verdict comes back in ~0.0s having
computed nothing. Measured across the archive: 403 of 7,875 landed cells replay. So "I re-ran it and
it matched" is not currently evidence of anything.

SH-7 (`experiments/_seed_checkpoint.get_output_dir`) fixes that by pointing the cell at a different,
EMPTY directory when `HDI_FRESH_RUN=<tag>` is set -- never by deleting checkpoints, which is
separately forbidden here and auto-denied.

THE LOAD-BEARING TEST IS THE NEGATIVE ONE. A redirect that fires when the env is UNSET would
silently orphan every landed directory in the repo -- every cell would write to a sibling nobody
reads, and nothing would error. That failure is far worse than the bug being fixed, and it is
invisible without this assertion. `test_unset_env_changes_nothing` is why this file exists; the
positive tests are the cheap half.

Companion witness: `verification/test_recompute_can_fail.py` proves a fresh re-run can actually
FAIL (corrupt one input, verdict flips) -- that is the mechanism. This file proves the SWITCH is
wired into the shared harness without disturbing it.

    python verification/test_fresh_recompute_redirect.py
"""
from __future__ import annotations

import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "experiments"))

# Real cell names, not fixtures: two that carry a landed data/ directory today and one arbitrary.
NAMES = ["cortical_read_consolidated_v1", "pbv_hypothesis_v1", "k_sweep_e1_v1"]
TAG = "verify_sh7"


def _paths(names):
    from _seed_checkpoint import get_output_dir
    return {n: str(get_output_dir(n)) for n in names}


def test_unset_env_changes_nothing() -> bool:
    """THE ONE THAT MATTERS: no env, no redirect, byte-identical path resolution."""
    os.environ.pop("HDI_FRESH_RUN", None)
    ok = True
    for name, path in _paths(NAMES).items():
        if "__fresh_" in path:
            print(f"[witness] FAIL: redirect fired with HDI_FRESH_RUN unset: {name} -> {path}")
            ok = False
    if ok:
        print("[witness] PASS test_unset_env_changes_nothing (no redirect without the env var)")
    return ok


def test_blank_env_changes_nothing() -> bool:
    """An empty or whitespace value is NOT a tag. `HDI_FRESH_RUN=` must behave like unset."""
    ok = True
    for blank in ("", "   "):
        os.environ["HDI_FRESH_RUN"] = blank
        for name, path in _paths(NAMES).items():
            if "__fresh_" in path:
                print(f"[witness] FAIL: blank env {blank!r} redirected {name} -> {path}")
                ok = False
    os.environ.pop("HDI_FRESH_RUN", None)
    if ok:
        print("[witness] PASS test_blank_env_changes_nothing (empty value is not a tag)")
    return ok


def test_set_env_redirects_to_a_new_sibling() -> bool:
    """With a tag, every cell resolves somewhere ELSE -- and the landed dir is never the target."""
    os.environ.pop("HDI_FRESH_RUN", None)
    base = _paths(NAMES)
    os.environ["HDI_FRESH_RUN"] = TAG
    fresh = _paths(NAMES)
    os.environ.pop("HDI_FRESH_RUN", None)

    ok = True
    for name in NAMES:
        if fresh[name] == base[name]:
            print(f"[witness] FAIL: tag set but path unchanged for {name}")
            ok = False
        elif not fresh[name].endswith(f"__fresh_{TAG}"):
            print(f"[witness] FAIL: unexpected fresh path for {name}: {fresh[name]}")
            ok = False
        elif os.path.dirname(fresh[name]) != os.path.dirname(base[name]):
            print(f"[witness] FAIL: fresh path is not a SIBLING for {name}")
            ok = False
    if ok:
        print("[witness] PASS test_set_env_redirects_to_a_new_sibling")
    return ok


def test_redirect_is_idempotent() -> bool:
    """An already-fresh path must not grow a second suffix on a resumed fresh run."""
    os.environ["HDI_FRESH_RUN"] = TAG
    p = _paths([f"k_sweep_e1_v1__fresh_{TAG}"])[f"k_sweep_e1_v1__fresh_{TAG}"]
    os.environ.pop("HDI_FRESH_RUN", None)
    ok = f"__fresh_{TAG}__fresh_{TAG}" not in p
    print(f"[witness] {'PASS' if ok else 'FAIL'} test_redirect_is_idempotent ({p})")
    return ok


def test_restores_after_unset() -> bool:
    """Setting then unsetting must return EXACTLY the original paths, not an approximation."""
    os.environ.pop("HDI_FRESH_RUN", None)
    before = _paths(NAMES)
    os.environ["HDI_FRESH_RUN"] = TAG
    _paths(NAMES)
    os.environ.pop("HDI_FRESH_RUN", None)
    after = _paths(NAMES)
    ok = before == after
    print(f"[witness] {'PASS' if ok else 'FAIL'} test_restores_after_unset")
    return ok


def test_fresh_dir_is_not_a_landed_dir() -> bool:
    """The redirect target must not be an existing landed directory -- writing there is the hazard.

    Not a tautology: a tag that collided with a real cell name would resolve onto live data. This
    asserts the property that makes byte-identity hold BY CONSTRUCTION rather than by cleanup.
    """
    os.environ["HDI_FRESH_RUN"] = TAG
    fresh = _paths(NAMES)
    os.environ.pop("HDI_FRESH_RUN", None)
    ok = True
    for name, path in fresh.items():
        if os.path.isfile(os.path.join(path, "units.jsonl")):
            print(f"[witness] FAIL: fresh target for {name} already holds units.jsonl: {path}")
            ok = False
    if ok:
        print("[witness] PASS test_fresh_dir_is_not_a_landed_dir")
    return ok


def main() -> int:
    results = [
        test_unset_env_changes_nothing(),
        test_blank_env_changes_nothing(),
        test_set_env_redirects_to_a_new_sibling(),
        test_redirect_is_idempotent(),
        test_restores_after_unset(),
        test_fresh_dir_is_not_a_landed_dir(),
    ]
    ok = all(results)
    print(f"[witness] RESULT: {'PASS' if ok else 'FAIL'} ({sum(results)}/{len(results)})")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
