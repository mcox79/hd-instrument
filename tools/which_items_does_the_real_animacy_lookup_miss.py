"""LOCALISE THE OPEN-VOCABULARY COST: which items does the REAL animacy lookup miss?

WHY. exp_bridge1_event_assembly_open_vocab_v1 scores 0.833 on subset B and 0.750 on Bgen with the REAL
lookup, where the CLOSED hand lexicon gives 1.000 on both. The body-part slice is already explained (a
known, deliberately-unpatched WordNet routing hole). THIS ASKS WHETHER THE REMAINING COST IS THE SAME
KIND OF THING -- more lookup holes -- or something else.

READ-ONLY. It imports the cell's own item lists and its own lookup function and reports per word. It
runs no arm, writes no metrics, and edits nothing.

POSITIVE CONTROL, because a lookup that silently returns nothing for everything would print a very
convincing list of misses: unambiguous animates (woman, dog, child) must RESOLVE, and unambiguous
inanimates (rock, table) must resolve too. If those fail, the harness is wrong and no miss below counts.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")

import collections
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "experiments"))


def main() -> int:
    import exp_bridge1_event_assembly_open_vocab_v1 as C

    lookup = C.real_animacy_lookup
    print("[POSITIVE CONTROL] unambiguous words must resolve:")
    ok = True
    for w, expect in (("woman", "animate"), ("dog", "animate"), ("child", "animate"),
                      ("rock", "inanimate"), ("table", "inanimate")):
        try:
            r = lookup(w)
        except Exception as exc:
            r = f"ERROR {type(exc).__name__}: {exc}"
        got = (r or {}).get("animacy") if isinstance(r, dict) else r
        flag = "OK" if got == expect else "MISS"
        if got != expect:
            ok = False
        print(f"    {w:8s} -> {str(got):12s} expected {expect:10s} [{flag}]")
    if not ok:
        print("  REFUSING: the lookup does not resolve unambiguous words; misses below would be "
              "an artifact of a broken harness, not a finding.")
        return 2

    pools = {}
    for name, obj in (("B", getattr(C.conf, "SUBSET_B", None)),
                      ("Bgen", getattr(C.v2, "SUBSET_B_GEN", None)),
                      ("Bopen", C.SUBSET_B_OPEN),
                      ("Bgap", C.SUBSET_B_GAP)):
        if obj:
            pools[name] = obj

    print()
    for name, items in pools.items():
        words = []
        for it in items:
            for k in ("patient_word", "target_word", "patient", "object_word"):
                if isinstance(it, dict) and it.get(k):
                    words.append(str(it[k]).lower())
        words = sorted(set(words))
        misses, resolved = [], []
        for w in words:
            try:
                r = lookup(w)
            except Exception:
                r = None
            got = (r or {}).get("animacy") if isinstance(r, dict) else r
            (resolved if got else misses).append(w)
        n = len(words)
        print(f"{name:6s} n_words={n:3d}  RESOLVED {len(resolved):3d}  "
              f"MISSED {len(misses):3d} ({100*len(misses)/max(n,1):.0f}%)")
        if misses:
            print(f"         misses: {misses}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
