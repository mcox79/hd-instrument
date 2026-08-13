#!/usr/bin/env python
"""Clear the CONTENTS of <repo>/scratch/, never the directory itself, never anything outside it."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SCRATCH = REPO_ROOT / "scratch"

# Set to False by --_disable_guard (self-test only) to prove the guard is load-bearing.
GUARD_ENABLED = True


class GuardViolation(Exception):
    """Raised when a delete target resolves outside the scratch root."""


def _real(p: Path) -> Path:
    """Fully-resolved absolute path with symlinks followed."""
    return Path(os.path.realpath(str(p)))


def assert_under_root(target: Path, root: Path) -> None:
    """Refuse any target whose real path is not strictly inside the real scratch root."""
    if not GUARD_ENABLED:
        return
    rt, rr = _real(target), _real(root)
    if rt == rr:
        raise GuardViolation(f"refusing to remove the scratch root itself: {rt}")
    try:
        rt.relative_to(rr)
    except ValueError:
        raise GuardViolation(f"refusing target outside scratch root: {rt} (root={rr})") from None


def entries(root: Path) -> list[Path]:
    """Immediate children of root, sorted deterministically."""
    return sorted(root.iterdir(), key=lambda p: p.name)


def clear(root: Path, apply: bool, keep: set[str]) -> int:
    """Dry-run list (apply=False) or delete (apply=True) the contents of root. Returns count."""
    root = Path(root)
    # The root handed in must BE the canonical scratch root -- checking children against the
    # caller's own root would be vacuous (every child is trivially under it).
    if GUARD_ENABLED and _real(root) != _real(DEFAULT_SCRATCH):
        raise GuardViolation(f"root {_real(root)} is not the scratch root {_real(DEFAULT_SCRATCH)}")
    if not root.is_dir():
        print(f"[clear_scratch] nothing to do: {root} does not exist", file=sys.stderr)
        return 0

    n = 0
    for child in entries(root):
        if child.name in keep:
            print(f"  keep    {child.name}")
            continue
        # Every child is validated against the canonical scratch root, not against `root`.
        assert_under_root(child, DEFAULT_SCRATCH)
        # A symlink child is unlinked, never followed into.
        if child.is_symlink():
            kind, action = "symlink", (lambda: child.unlink())
        elif child.is_dir():
            kind, action = "dir", (lambda: shutil.rmtree(child))
        else:
            kind, action = "file", (lambda: child.unlink())
        if apply:
            action()
            print(f"  removed {kind:8s} {child.name}")
        else:
            print(f"  would remove {kind:8s} {child.name}")
        n += 1
    verb = "removed" if apply else "would remove"
    print(f"[clear_scratch] {verb} {n} entr{'y' if n == 1 else 'ies'} under {root}")
    if not apply and n:
        print("[clear_scratch] dry run. re-run with --yes to actually delete.")
    return n


def self_test() -> int:
    """Prove the guard refuses a target outside scratch/. Returns process exit code."""
    ok = True
    outside = Path(tempfile.mkdtemp(prefix="clear_scratch_selftest_"))
    victim = outside / "must_survive.txt"
    victim.write_text("this file must not be deleted\n", encoding="utf-8")
    print(f"[self-test] created outside-scratch dir: {outside}")

    # Point the deleter at a directory that is NOT under scratch/. The guard must refuse.
    try:
        clear(outside, apply=True, keep=set())
    except GuardViolation as e:
        print(f"[self-test] PASS guard refused as expected: {e}")
    else:
        print("[self-test] FAIL guard did NOT refuse an out-of-tree target", file=sys.stderr)
        ok = False

    if not victim.exists():
        print("[self-test] FAIL victim file was deleted", file=sys.stderr)
        ok = False
    else:
        print("[self-test] PASS victim file survived")

    # Guard must also refuse the scratch root itself as a delete target.
    try:
        assert_under_root(DEFAULT_SCRATCH, DEFAULT_SCRATCH)
    except GuardViolation as e:
        print(f"[self-test] PASS guard refused root-itself: {e}")
    else:
        print("[self-test] FAIL guard allowed removing the scratch root", file=sys.stderr)
        ok = False

    # Sanity: a real child of scratch/ IS accepted (guard is not vacuously refusing everything).
    try:
        assert_under_root(DEFAULT_SCRATCH / "probe.py", DEFAULT_SCRATCH)
        print("[self-test] PASS guard accepts a legitimate scratch child")
    except GuardViolation as e:
        print(f"[self-test] FAIL guard refused a legitimate child: {e}", file=sys.stderr)
        ok = False

    print(f"[self-test] leftover temp dir (not auto-removed, by design): {outside}")
    print("[self-test] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--yes", action="store_true", help="actually delete (default is dry-run)")
    ap.add_argument("--root", default=str(DEFAULT_SCRATCH), help="scratch root (default: <repo>/scratch)")
    ap.add_argument("--keep", default="README.md", help="comma-separated names to preserve")
    ap.add_argument("--self-test", action="store_true", help="prove the out-of-tree guard refuses")
    ap.add_argument("--_disable_guard", action="store_true",
                    help="self-test only: disable the guard to confirm the self-test then FAILS")
    args = ap.parse_args(argv)

    if args._disable_guard:
        global GUARD_ENABLED
        GUARD_ENABLED = False
        print("[clear_scratch] WARNING guard DISABLED (self-test negative control)")

    if args.self_test:
        return self_test()

    root = Path(args.root)
    # Outside of --self-test, the root must be the repo's scratch dir.
    if GUARD_ENABLED and _real(root) != _real(DEFAULT_SCRATCH):
        print(f"[clear_scratch] REFUSED: root {_real(root)} is not {_real(DEFAULT_SCRATCH)}", file=sys.stderr)
        return 2

    keep = {s for s in (x.strip() for x in args.keep.split(",")) if s}
    try:
        clear(root, apply=args.yes, keep=keep)
    except GuardViolation as e:
        print(f"[clear_scratch] REFUSED: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
