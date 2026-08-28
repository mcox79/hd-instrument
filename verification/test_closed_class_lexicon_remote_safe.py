"""Witness: hdlab.closed_class_lexicon is REMOTE-SAFE (no spaCy) as of 2026-08-28.

The remote CPU runner (marsh@home) has no spaCy. Previously `_spacy_stop_words()` did a hard
`from spacy... import STOP_WORDS` reached at full-run build time -> ModuleNotFoundError crash (it
killed the foraging run). Fix: a FROZEN 326-word snapshot fallback, drift-guarded against live spaCy.

  [1] spaCy PRESENT: _spacy_stop_words returns the LIVE set, and the drift-guard passes (frozen == live).
  [2] spaCy ABSENT (simulated by blocking the import): returns the FROZEN snapshot, identical set, no crash.
  [3] build_closed_class_set() completes WITHOUT spaCy (the path that crashed the foraging run).
"""
from __future__ import annotations

import builtins
import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main() -> int:
    import hdlab.closed_class_lexicon as ccl

    # [1] spaCy present: live path + drift-guard
    live = ccl._spacy_stop_words()
    assert live == set(ccl._FROZEN_SPACY_STOP_WORDS), "frozen snapshot must equal live spaCy (drift-guard)"
    assert len(live) == 326, f"expected 326 stop words, got {len(live)}"
    print(f"[1] spaCy PRESENT: live=={len(live)} words, drift-guard PASS (frozen == live)")

    # [2] spaCy ABSENT: block the import and confirm the frozen fallback returns the identical set
    real_import = builtins.__import__

    def _no_spacy(name, *a, **k):
        if name == "spacy" or name.startswith("spacy."):
            raise ImportError("spaCy blocked for the remote-safety witness")
        return real_import(name, *a, **k)

    builtins.__import__ = _no_spacy
    try:
        # drop any cached spacy submodules so the import is actually re-attempted
        for m in [m for m in sys.modules if m == "spacy" or m.startswith("spacy.")]:
            del sys.modules[m]
        fallback = ccl._spacy_stop_words()
    finally:
        builtins.__import__ = real_import
    assert fallback == set(ccl._FROZEN_SPACY_STOP_WORDS), "fallback must be the frozen snapshot"
    assert fallback == live, "fallback set must be IDENTICAL to the live spaCy set (fidelity preserved)"
    print(f"[2] spaCy ABSENT: fallback=={len(fallback)} words, IDENTICAL to live -> no crash, fidelity preserved")

    # [3] the full build path (what crashed foraging) completes without spaCy
    builtins.__import__ = _no_spacy
    try:
        for m in [m for m in sys.modules if m == "spacy" or m.startswith("spacy.")]:
            del sys.modules[m]
        built = ccl.build_closed_class_set()
    finally:
        builtins.__import__ = real_import
    assert len(built) > 500, f"closed-class build should be substantial, got {len(built)}"
    print(f"[3] build_closed_class_set() WITHOUT spaCy: {len(built)} forms (the path that crashed foraging) PASS")

    print("\nALL WITNESS ASSERTIONS PASSED -- closed_class_lexicon is remote-safe (spaCy-free), fidelity-identical.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
