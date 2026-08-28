"""Landing-verification (WIRE-DON'T-ISLAND) for the SET-RETURN decode landed on the situation-model register.

The p2 integration proved the set-return fix with the solver's own inline code (test_entity_store_fan.py 21/21).
This confirms the LANDED organ path -- `make_situation_register(...).decode_set` -- reproduces the fan-flattening on
the REAL LitBank register in-pipeline (like STEP 12/13 did for the salience binder), so the landed code (not just the
experiment cell) delivers the fix.

Setup mirrors the solver's fan measurement: LitBank, ORACLE linking (gold entity clusters) so the STORE is measured in
isolation. For each who-did-what query (entity E with a governed verb v at sentence s):
  * ARGMAX (incumbent decode)      : decode(E, s)[0] == v      -> shows the FAN (a busy character's co-sentence verbs collide).
  * SET-RETURN (landed decode_set) : v in decode_set(E, s)[0]  -> should FLATTEN the fan (returns the whole co-context set).
Binned by the entity's total event-count (fan level). The landed set-return must cut the fan SLOPE vs argmax.

Run:  .venv/Scripts/python.exe experiments/exp_setreturn_landing_verify_v1.py [--docs N]
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys
from collections import Counter, defaultdict

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "experiments"))

import experiments.exp_litbank_entity_tracking_end_to_end_v1 as H
from experiments.exp_litbank_entity_tracking_end_to_end_v1 import PRONOUNS, D
from hdlab.situation_model_accumulate import make_situation_register

SEED = 20260827
BINS = [(1, 3), (4, 8), (9, 16), (17, 10**9)]


def _bin(n):
    for lo, hi in BINS:
        if lo <= n <= hi:
            return f"{lo}-{hi if hi < 10**9 else '+'}".replace("-1000000000+", "+")
    return "?"


def main():
    docs = 100
    if "--docs" in sys.argv:
        docs = int(sys.argv[sys.argv.index("--docs") + 1])
    recs = H.load_cache()[:docs]

    argmax_by = defaultdict(lambda: [0, 0])   # bin -> [correct, n]
    setret_by = defaultdict(lambda: [0, 0])
    n_q = 0
    for di, rec in enumerate(recs):
        stream = rec["stream"]
        if not stream:
            continue
        slot_map, n_slots = H._slots(stream)
        verb_vocab = sorted({m["gov_verb"] for m in stream if m["gov_verb"] is not None})
        if not verb_vocab:
            continue
        g = H._torch_gen(SEED + di)
        reg = make_situation_register(list(verb_vocab), D, g, max_event_slots=max(n_slots, 1),
                                      backend="multibank", n_banks=8)
        # ORACLE linking: bind each event under its gold entity
        for m in stream:
            if m["gov_verb"] is not None:
                reg.add_event(str(m["gold"]), m["gov_verb"], slot_map[m["sent"]])
        ev_count = Counter(m["gold"] for m in stream if m["gov_verb"] is not None)  # fan level per entity
        for m in stream:
            v = m["gov_verb"]
            if v is None:
                continue
            E = str(m["gold"]); s = slot_map[m["sent"]]
            b = _bin(ev_count[m["gold"]])
            top, _ = reg.decode(E, s)                       # incumbent argmax
            got, _ = reg.decode_set(E, s, rel_margin=0.5)   # landed set-return
            argmax_by[b][0] += int(top == v); argmax_by[b][1] += 1
            setret_by[b][0] += int(v in got); setret_by[b][1] += 1
            n_q += 1

    order = ["1-3", "4-8", "9-16", "17+"]
    print(f"=== SET-RETURN landing-verification on the LANDED register (LitBank oracle linking, "
          f"{len(recs)} docs, {n_q} who-did-what queries) ===\n")
    print(f"  {'fan level':10s}  {'ARGMAX decode':>14s}  {'SET-RETURN decode_set':>22s}")
    a_lo = a_hi = s_lo = s_hi = None
    for b in order:
        a = argmax_by[b]; sr = setret_by[b]
        aa = a[0] / a[1] if a[1] else float("nan")
        ss = sr[0] / sr[1] if sr[1] else float("nan")
        print(f"  {b:10s}  {aa:14.4f}  {ss:22.4f}   (n={a[1]})")
        if b == "1-3":
            a_lo, s_lo = aa, ss
        if b == "17+":
            a_hi, s_hi = aa, ss
    argmax_slope = a_lo - a_hi
    setret_slope = s_lo - s_hi
    print(f"\n  ARGMAX fan slope (1-3 minus 17+)     : {argmax_slope:+.4f}   (the fan)")
    print(f"  SET-RETURN fan slope (1-3 minus 17+) : {setret_slope:+.4f}   (should be ~0 -> flattened)")
    ok = setret_slope < argmax_slope - 0.05 and s_hi > a_hi + 0.05
    print(f"\n  [{'PASS' if ok else 'FAIL'}] landed decode_set FLATTENS the fan vs argmax "
          f"(set-return slope {setret_slope:+.4f} << argmax slope {argmax_slope:+.4f}; "
          f"17+ recovery {s_hi:.4f} >> argmax {a_hi:.4f})")
    print(f"\n{'LANDED SET-RETURN reproduces the fan-flattening in-pipeline' if ok else 'SEE FAILURE'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
