"""How much of the archive can be RE-ANALYSED, and how much can only ever answer its original question?

WHY THIS EXISTS. `exp_information_foraging_reading_v1` scored a banked vocabulary against a probe
and persisted **the score but not the vocabulary**. When the probe turned out to carry a 7.6x
register bias, the correct re-analysis became impossible -- 604 strings, a few kilobytes, that would
have made it a one-second recompute, cost a 4,144-second x 5-arm re-run instead.

**THE QUESTION THIS ANSWERS: is that one careless cell, or is it how we build?**

METHOD, and its limits stated up front:
  * a cell COUNTS as scoring a population if its metrics mention coverage/hits/accuracy/precision/
    recall/agreement -- i.e. a number computed OVER A SET OF ITEMS.
  * a cell COUNTS as having persisted outputs if ANY list of >=20 strings appears anywhere in
    metrics.json or units.jsonl, OR a sibling .json/.jsonl file carries one.
  * **THIS UNDER-COUNTS PERSISTENCE.** A cell may write items to a file this does not scan.
    So the "saved only scores" figure is an UPPER BOUND on the defect, and is reported as such.
  * **AND IT IS A HEURISTIC, NOT A CENSUS** -- it is a prompt to go look, not a verdict on any cell.
"""
from __future__ import annotations

import json
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA = os.path.join(_REPO, "data")
SCORE_HINTS = ("coverage", "hits", "accuracy", "precision", "recall", "agreement", "f1")
MIN_LIST = 20


def str_lists(o, depth=0):
    """Yield lengths of every list-of-strings found."""
    if depth > 6:
        return
    if isinstance(o, dict):
        for v in o.values():
            yield from str_lists(v, depth + 1)
    elif isinstance(o, list):
        if o and all(isinstance(x, str) for x in o):
            yield len(o)
        else:
            for v in o[:50]:
                yield from str_lists(v, depth + 1)


def main():
    scored, saved, rows = 0, 0, []
    n_dirs = 0
    for name in sorted(os.listdir(DATA)):
        d = os.path.join(DATA, name)
        mp = os.path.join(d, "metrics.json")
        if not os.path.isdir(d) or not os.path.exists(mp):
            continue
        n_dirs += 1
        try:
            with open(mp, encoding="utf-8") as fh:
                m = json.load(fh)
        except Exception:
            continue
        blob = json.dumps(m).lower()
        if not any(h in blob for h in SCORE_HINTS):
            continue
        scored += 1
        best = max(list(str_lists(m)) or [0])
        if best < MIN_LIST:
            up = os.path.join(d, "units.jsonl")
            if os.path.exists(up):
                try:
                    with open(up, encoding="utf-8") as fh:
                        for i, line in enumerate(fh):
                            if i > 400 or not line.strip():
                                continue
                            best = max(best, max(list(str_lists(json.loads(line))) or [0]))
                except Exception:
                    pass
        if best < MIN_LIST:
            for f in os.listdir(d):
                if f in ("metrics.json", "units.jsonl") or not f.endswith((".json", ".jsonl")):
                    continue
                try:
                    # 🔴 v1 READ ONLY THE FIRST 2 MB HERE, so any sibling file LARGER than that
                    # failed to parse and was swallowed by the except below -- and it was counted
                    # as "no outputs saved". THE BIAS RAN EXACTLY BACKWARDS: the cells that
                    # persisted the MOST data were the ones most likely to be called defective.
                    # Caught on exp_context_vector_signal_v1, whose _pass_encounters.json is
                    # 4,011,507 bytes and DOES contain its scored population -- a cell v1 named in
                    # its "genuinely lost" list. Read the whole file.
                    with open(os.path.join(d, f), encoding="utf-8") as fh:
                        blob_f = fh.read()
                    if f.endswith(".jsonl"):
                        for line in blob_f.splitlines()[:2000]:
                            if line.strip():
                                best = max(best, max(list(str_lists(json.loads(line))) or [0]))
                    else:
                        best = max(best, max(list(str_lists(json.loads(blob_f))) or [0]))
                except Exception:
                    continue
        if best >= MIN_LIST:
            saved += 1
        else:
            rows.append((name, m.get("verdict", "?")))

    print("cell directories with a metrics.json      %d" % n_dirs)
    print("of those, cells scoring a POPULATION      %d" % scored)
    print("  persisted a >=%d-item output list       %d  (%.1f%%)"
          % (MIN_LIST, saved, 100.0 * saved / max(1, scored)))
    print("  NO output list found (UPPER BOUND)      %d  (%.1f%%)"
          % (len(rows), 100.0 * len(rows) / max(1, scored)))
    print("\nUPPER BOUND, because a cell may write items to a file this scan does not read.")
    hp = [r for r in rows if "HARD_PASS" in str(r[1])]
    print("\nof the no-output-found cells, %d are HARD_PASS -- the ones most likely to be cited:" % len(hp))
    for n, v in hp[:25]:
        print("   %-62s %s" % (n[:62], v))
    return 0


if __name__ == "__main__":
    sys.exit(main())
