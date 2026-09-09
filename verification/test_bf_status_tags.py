#!/usr/bin/env python3
"""Registry-driven checker for the BF-STATUS tagging convention (owner 2026-09-09).

Single source of truth: notes/bf_status_registry.jsonl (one JSON object per line).
For every entry this asserts the module file exists and carries a top-of-file tag
block whose __bf_status__ EQUALS the registry status and is one of the allowed
values, and that __bf_verified__ / __bf_note__ are present. It also runs a
POSITIVE-CONTROL self-check proving the guard actually fires on a missing /
mismatched tag, and prints a one-line status-count SUMMARY (the honest
verified-BF denominator).

Side-effect-free: modules are AST-parsed, never imported (safe under a concurrent
detached board run). Standalone -- no test framework.

Run:  python verification/test_bf_status_tags.py     (exit 0 = all PASS, 1 = any FAIL)
"""
from __future__ import annotations

import ast
import json
import os
import sys

ALLOWED = {"BF", "BF_SPIRIT", "NOT_BF", "BF_UNPINNED", "BF_UNVERIFIED"}
STATUS_ORDER = ["BF", "BF_SPIRIT", "NOT_BF", "BF_UNPINNED", "BF_UNVERIFIED"]

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY = os.path.join(REPO_ROOT, "notes", "bf_status_registry.jsonl")


def extract_tags(source):
    """AST-parse module source; return {name: value} for module-level __bf_*__ string
    assignments. Never imports the module (fully side-effect-free)."""
    tags = {}
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id.startswith("__bf_"):
                    try:
                        tags[tgt.id] = ast.literal_eval(node.value)
                    except Exception:
                        tags[tgt.id] = None
    return tags


def check_source(source, expected_status):
    """Return a list of failure reasons (empty list == PASS) for one module's source."""
    fails = []
    tags = extract_tags(source)
    status = tags.get("__bf_status__")
    if status is None:
        fails.append("missing __bf_status__")
    else:
        if status not in ALLOWED:
            fails.append("status %r not in allowed set %s" % (status, sorted(ALLOWED)))
        if expected_status is not None and status != expected_status:
            fails.append("status %r != registry %r" % (status, expected_status))
    if not tags.get("__bf_verified__"):
        fails.append("missing/empty __bf_verified__")
    if not tags.get("__bf_note__"):
        fails.append("missing/empty __bf_note__")
    return fails


def load_registry(path):
    entries = []
    with open(path, "r", encoding="utf-8") as fh:
        for i, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit("FAIL: registry line %d is not valid JSON: %s" % (i, exc))
            entries.append(obj)
    return entries


def positive_control():
    """Prove the checker FAILS on a missing tag and on a mismatched tag (guard fires)."""
    reasons = []
    ok = True

    # (a) a well-formed tag must PASS
    good = (
        '__bf_status__ = "BF"\n'
        '__bf_verified__ = "2026-09-09 test"\n'
        '__bf_note__ = "synthetic control"\n'
    )
    if check_source(good, "BF"):
        ok = False
        reasons.append("well-formed synthetic tag was wrongly rejected")

    # (b) a MISSING tag must FAIL
    missing = '__bf_note__ = "no status here"\n'
    if not check_source(missing, "BF"):
        ok = False
        reasons.append("missing __bf_status__ was NOT caught")

    # (c) a MISMATCHED status must FAIL
    mismatch = (
        '__bf_status__ = "NOT_BF"\n'
        '__bf_verified__ = "2026-09-09 test"\n'
        '__bf_note__ = "wrong status"\n'
    )
    if not check_source(mismatch, "BF"):
        ok = False
        reasons.append("mismatched status was NOT caught")

    # (d) an out-of-vocab status must FAIL
    bogus = (
        '__bf_status__ = "TOTALLY_BF"\n'
        '__bf_verified__ = "2026-09-09 test"\n'
        '__bf_note__ = "bad value"\n'
    )
    if not check_source(bogus, "TOTALLY_BF"):
        ok = False
        reasons.append("out-of-vocab status was NOT caught")

    return ok, reasons


def main():
    n_fail = 0

    # 0. positive control -- the guard must be known to fire.
    ctl_ok, ctl_reasons = positive_control()
    if ctl_ok:
        print("PASS  positive-control: checker rejects missing / mismatched / out-of-vocab tags")
    else:
        n_fail += 1
        for r in ctl_reasons:
            print("FAIL  positive-control: %s" % r)

    # 1. load registry
    if not os.path.exists(REGISTRY):
        print("FAIL  registry not found: %s" % REGISTRY)
        return 1
    entries = load_registry(REGISTRY)
    print("PASS  registry loaded: %s (%d entries)" % (
        os.path.relpath(REGISTRY, REPO_ROOT).replace("\\", "/"), len(entries)))

    # 2. registry-level: every status value must be in the allowed set
    counts = {}
    for e in entries:
        st = e.get("status")
        counts[st] = counts.get(st, 0) + 1
        if st not in ALLOWED:
            n_fail += 1
            print("FAIL  registry status %r (module %s) not in allowed set" % (st, e.get("module")))
    if not n_fail:
        print("PASS  every registry status is in the allowed set %s" % sorted(ALLOWED))

    # 3. per-module tag check
    for e in entries:
        mod = e.get("module")
        expected = e.get("status")
        path = os.path.join(REPO_ROOT, mod.replace("/", os.sep))
        if not os.path.exists(path):
            n_fail += 1
            print("FAIL  %s: file does not exist" % mod)
            continue
        with open(path, "r", encoding="utf-8") as fh:
            src = fh.read()
        try:
            fails = check_source(src, expected)
        except SyntaxError as exc:
            n_fail += 1
            print("FAIL  %s: could not parse (%s)" % (mod, exc))
            continue
        if fails:
            n_fail += 1
            print("FAIL  %s: %s" % (mod, "; ".join(fails)))
        else:
            print("PASS  %s -> %s" % (mod, expected))

    # 4. summary line -- the honest verified-BF denominator
    parts = ["%s=%d" % (s, counts[s]) for s in STATUS_ORDER if counts.get(s)]
    # include any unexpected statuses too, so the summary never silently hides one
    for s in sorted(counts):
        if s not in STATUS_ORDER:
            parts.append("%s=%d" % (s, counts[s]))
    print("SUMMARY  %s | %d organs tagged" % (" ".join(parts), len(entries)))

    if n_fail:
        print("RESULT  %d FAIL" % n_fail)
        return 1
    print("RESULT  all PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
