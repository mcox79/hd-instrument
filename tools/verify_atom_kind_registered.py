"""Pre-write verification: is <kind_name> a registered AtomKind enum member?

Any atomize tool that intends to call Store.add_atom(kind=X) should verify X
is a valid AtomKind FIRST. If X is unregistered, Store.load() (or the newer
fail-closed gate) will refuse the file at re-load time, dropping every atom
after the offending row.

Usage:
    .venv/Scripts/python.exe tools/verify_atom_kind_registered.py <kind_name>

    # returns 0 if kind is registered, prints ok
    # returns 1 if kind is NOT registered, prints registered kinds + hint

    # bulk mode: verify a comma-separated list
    .venv/Scripts/python.exe tools/verify_atom_kind_registered.py foo,bar,baz

Recurrence context: 8+ times this arc, an atomize tool wrote atoms with
kinds that were NOT yet in backend.substrate_index.schema.AtomKind. Store-load
gates then fail-closed on those rows. Skunkworks has repeatedly done orphan-
kind recovery (see schema.py comments around lines 122-155). This tool is
a pre-write check meant to be invoked by every atomize script + templates,
and by META_RULE_BE lint.

Exit codes:
    0 all requested kinds are registered
    1 at least one kind is NOT registered
    2 argument or environment error
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))


def main(argv):
    if len(argv) < 2:
        print(f'usage: {argv[0]} <kind_name>[,<kind_name>...]', file=sys.stderr)
        return 2

    try:
        from backend.substrate_index.schema import AtomKind
    except ImportError as e:
        print(f'ERROR: could not import AtomKind: {e}', file=sys.stderr)
        return 2

    registered = {k.value for k in AtomKind}
    requested = [k.strip() for k in argv[1].split(',') if k.strip()]

    if not requested:
        print('ERROR: no kind names provided', file=sys.stderr)
        return 2

    missing = []
    for k in requested:
        if k in registered:
            print(f'  OK: {k!r} is a registered AtomKind')
        else:
            missing.append(k)
            print(f'  FAIL: {k!r} is NOT a registered AtomKind', file=sys.stderr)

    if missing:
        print('', file=sys.stderr)
        print(f'ERROR: {len(missing)} unregistered kind(s): {missing}', file=sys.stderr)
        print('', file=sys.stderr)
        print('Registered AtomKind values (sorted):', file=sys.stderr)
        for k in sorted(registered):
            print(f'    {k}', file=sys.stderr)
        print('', file=sys.stderr)
        print(
            'HINT: to add a new kind, edit backend/substrate_index/schema.py '
            "class AtomKind(enum.Enum) and add the new member with a comment "
            "citing the Skunkworks/USER decision or cell that motivates it. "
            "The Store-load gate fails closed on unregistered kinds — writing "
            "an atom with an unregistered kind blocks Store.load() until the "
            "enum is extended.",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
