"""DIAG (strategy 2026-09-13 20:50): is the red in verification/test_reader_frontend_cache_shared.py [1] ORDER-DEPENDENT STATE?
The witness reads the same document twice in ONE process (positional/lazy frontend first, then the capable/wired reader) and asserts
identical entity_states. Under the applied integration wave it fails (49 vs 47 states) with every organ switch OFF, so the cause is
either an unconditional code change that makes the two routes compute differently, or STATE the first read leaves behind (an in-process
cache or an online-learning path) that the second read inherits. This script runs EACH read in a FRESH interpreter and writes the key
sets, then compares: identical across processes => order-dependent state inside one process (find the cache); different => the two
routes really compute differently (find the route difference).
Run: python experiments/_diag_cache_shared_order.py            (spawns two child processes; ~2-4 min)
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = os.path.join(REPO, ".venv", "Scripts", "python.exe")
OUT = os.path.join(REPO, "data", "hook_state")
CHILD = r'''
import os, sys, json
sys.path.insert(0, %(repo)r); os.chdir(%(repo)r)
import experiments.exp_situation_model_qa_v1 as SITQA
from hdlab.situation_reader import SituationReader
gaz = SITQA.load_given_gazetteer(); path = os.path.join(SITQA.CONLL_DIR, "1023_bleak_house_brat.conll")
mode = %(mode)r
if mode == "positional":
    sm = SituationReader.all_capabilities_off(gaz=gaz, bind_entity_states=True).read(path)
elif mode == "wired":
    sm = SituationReader(gaz=gaz).read(path)
elif mode == "both_pos_then_wired":
    SituationReader.all_capabilities_off(gaz=gaz, bind_entity_states=True).read(path)
    sm = SituationReader(gaz=gaz).read(path)
elif mode == "both_wired_then_pos":
    SituationReader(gaz=gaz).read(path)
    sm = SituationReader.all_capabilities_off(gaz=gaz, bind_entity_states=True).read(path)
key = sorted((s.sent_idx, s.holder.lower(), s.property.lower(), s.htype) for s in sm.entity_states)
json.dump(key, open(%(out)r, "w", encoding="utf-8"))
print(mode, len(key))
'''


def run(mode):
    out = os.path.join(OUT, "_diag_cache_%s.json" % mode)
    env = dict(os.environ, OMP_NUM_THREADS="2", OPENBLAS_NUM_THREADS="2", MKL_NUM_THREADS="2", PYTHONHASHSEED="0")
    r = subprocess.run([PY, "-c", CHILD % {"repo": REPO, "mode": mode, "out": out}], capture_output=True, text=True, env=env, cwd=REPO)
    tail = [l for l in (r.stdout + r.stderr).splitlines() if not l.startswith("[SH-")][-2:]
    print(mode, "->", tail)
    return json.load(open(out, encoding="utf-8")) if os.path.exists(out) else None


def main():
    import importlib
    # sanity: the witness's import names
    try:
        importlib.import_module("experiments.exp_situation_model_qa_v1")
    except Exception as e:
        print("import check:", e)
    pos = run("positional"); wired = run("wired")
    both1 = run("both_pos_then_wired"); both2 = run("both_wired_then_pos")
    def cmp(a, b, la, lb):
        if a is None or b is None:
            print("  %s vs %s: missing" % (la, lb)); return
        sa, sb = set(map(tuple, a)), set(map(tuple, b))
        print("  %s (%d) vs %s (%d): identical=%s | only-%s=%d only-%s=%d" % (la, len(sa), lb, len(sb), sa == sb, la, len(sa - sb), lb, len(sb - sa)))
        for x in sorted(sa - sb)[:6]: print("     only", la, x)
        for x in sorted(sb - sa)[:6]: print("     only", lb, x)
    print("FRESH-PROCESS comparison:")
    cmp(pos, wired, "positional", "wired")
    print("ORDER comparison (second read of a pair vs the same read fresh):")
    cmp(both1, wired, "wired-after-positional", "wired-fresh")
    cmp(both2, pos, "positional-after-wired", "positional-fresh")
    print("DONE")


if __name__ == "__main__":
    main()
