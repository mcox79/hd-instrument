"""Concurrent-save self-test for the save_atoms/save_relations UNIQUE-tmp fix (Skunkworks VET condition, 2026-06-19).

Proves: two writers saving the SAME partition CONCURRENTLY never produce a corrupt/unloadable file (the 2026-06-19
concept-corruption root cause) -- last-writer-wins, always one COMPLETE valid set. Includes an OLD-fixed-tmp CONTROL
that demonstrates the pre-fix behavior CAN corrupt (sensitivity check; demonstrate-don't-assert).

Thread-based (file open/write release the GIL -> the I/O interleaves, reproducing the shared-tmp collision). ASCII.
Run: .venv/Scripts/python.exe tools/test_save_atoms_concurrent_unique_tmp_2026-06-19.py
"""
from __future__ import annotations
import json
import os
import sys
import threading
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier, save_atoms, load_atoms


def _atoms(tag: str, n: int):
    return [Atom(id=f'CN_{tag}_{i}', name=f'{tag} {i}', corpus=Corpus.CONCEPT, tier=Tier.TIER_NA,
                 kind=AtomKind.CONCEPT_NODE, description=f'concurrent-test atom {tag} {i}',
                 metadata={'provenance_quality': 'RESEARCH_FINDING', 'tag': tag}) for i in range(n)]


def _save_atoms_OLD(atoms, path: Path):
    """Pre-fix behavior: FIXED tmp filename (the bug). For the control only."""
    path = Path(path)
    tmp = path.with_suffix(path.suffix + ".tmp")          # SHARED tmp -> concurrent collision
    with open(tmp, "w", encoding="utf-8") as f:
        for a in atoms:
            f.write(json.dumps(a.to_dict(), ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def _hammer(save_fn, path: Path, n_atoms: int, iters: int, rounds: int):
    """Two threads concurrently save distinct sets to the SAME path; after each round, check the file LOADS + is a
    COMPLETE valid set (one writer's, last-writer-wins). Returns (load_failures, partial_or_mixed)."""
    set_a = _atoms('A', n_atoms)
    set_b = _atoms('B', n_atoms)
    ids_a = {str(x.id) for x in set_a}
    ids_b = {str(x.id) for x in set_b}
    load_failures = 0
    partial_or_mixed = 0
    write_failures = [0]                                    # per-save exceptions (caught; counted)
    for _ in range(rounds):
        barrier = threading.Barrier(2)
        def w(atoms):
            barrier.wait()
            for _ in range(iters):
                try:
                    save_fn(atoms, path)
                except Exception:
                    write_failures[0] += 1                  # OLD: shared-tmp collision raises (WinError 32); FIXED: retry absorbs it
        ta = threading.Thread(target=w, args=(set_a,)); tb = threading.Thread(target=w, args=(set_b,))
        ta.start(); tb.start(); ta.join(); tb.join()
        # the final on-disk file must LOAD + equal exactly one writer's complete set
        try:
            loaded = load_atoms(path)
        except Exception:
            load_failures += 1
            continue
        got = {str(x.id) for x in loaded}
        if got != ids_a and got != ids_b:
            partial_or_mixed += 1  # truncated / interleaved / mixed = corruption signature
    return load_failures, partial_or_mixed, write_failures[0]


def main() -> int:
    d = Path(tempfile.mkdtemp(prefix='savetest_'))
    try:
        N, ITERS, ROUNDS = 400, 40, 8
        # FIXED (the patched save_atoms from schema) -- MUST be clean (no corruption AND no raised write-failures)
        fix_lf, fix_pm, fix_wf = _hammer(save_atoms, d / 'fixed.jsonl', N, ITERS, ROUNDS)
        fixed_ok = (fix_lf == 0 and fix_pm == 0 and fix_wf == 0)
        # OLD control -- demonstrate the pre-fix behavior breaks under concurrency (shared-tmp collision)
        old_lf, old_pm, old_wf = _hammer(_save_atoms_OLD, d / 'old.jsonl', N, ITERS, ROUNDS)
        old_broke = (old_lf + old_pm + old_wf) > 0
        print(f'[concurrent-save-test] FIXED (unique-tmp + replace-retry): load_failures={fix_lf} partial_or_mixed={fix_pm} write_failures={fix_wf} -> {"CLEAN" if fixed_ok else "FAIL"}')
        print(f'[concurrent-save-test] OLD control (fixed-tmp): load_failures={old_lf} partial_or_mixed={old_pm} write_failures={old_wf} -> {"BROKE under concurrency (test is sensitive; old code unsafe)" if old_broke else "did-not-reproduce-this-run (timing)"}')
        # the ASSERTION is on the FIX; the control is informational (timing-dependent)
        result = 'PASS' if fixed_ok else 'FAIL'
        print(f'[concurrent-save-test] RESULT: {result} (fix prevents concurrent-save corruption across {ROUNDS} rounds x {ITERS} iters x 2 writers x {N} atoms)')
        return 0 if fixed_ok else 1
    finally:
        import shutil
        shutil.rmtree(d, ignore_errors=True)


if __name__ == '__main__':
    raise SystemExit(main())
