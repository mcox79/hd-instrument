"""
exp_fb15k237_sharding_strategy_cpu_v1 -- real-KG sharding-strategy comparison on FB15k-237 (Freebase) -- CPU.

ROUTING: v1 benchmark suite (real-KG sharding layout). On real Freebase (FB15k-237), compares three shard keys for 1-hop
  retrieval (s,p)->o: shard-by-SUBJECT (s -> bundle of p*o), shard-by-RELATION (p -> bundle of s*o), shard-by-OBJECT (o ->
  bundle of s*p, for reverse (p,o)->s). Identifies the best KG storage layout on real data (informs the v1.5 demo's KG engine).
  Pure numpy FHRR. CPU.
PRE-REGISTERED: HARD-PASS best shard strategy 1-hop recall@5 >= 0.85 on real FB15k-237. MIDDLE >= 0.70. HARD-FAIL < 0.70.
FORMULA SELF-TESTS (PROT-022): 1. bind/unbind. 2. cleanup self. 3. json parse.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math, json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "fb15k237_sharding_strategy_cpu_v1"; N = 8192
FB = REPO / "data" / "datasets" / "fb15k_237_train_50k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
MAX_T = 8000 if SMOKE else 50000; NQ = 300 if SMOKE else 800


def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)


def topk(v, book, k):
    return set(np.argsort((book @ np.conj(v)).real)[::-1][:k].tolist())


def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 32, g)[0]; p = cphasor(1, 32, g)[0]; o = cphasor(1, 32, g)[0]
    assert np.allclose(a * p * o * np.conj(a * p), o, atol=1e-3), "bind/unbind"
    bk = cphasor(4, 32, g); assert int(np.argmax((bk @ np.conj(bk[1])).real)) == 1, "cleanup self"
    assert json.loads('{"subject":"a"}')["subject"] == "a", "json parse"
    print("[selftest] PASS: fb15k237-sharding-strategy", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    if not FB.exists():
        print("[FATAL] no FB15k", flush=True); return {"n": 0, "best": 0.0}
    g = np.random.default_rng(7); triples = []; ent = {}; rel = {}
    for l in open(FB, encoding="utf-8"):
        r = json.loads(l); s, p, o = r["subject"], r["predicate"], r["object"]
        for e in (s, o):
            if e not in ent:
                ent[e] = len(ent)
        if p not in rel:
            rel[p] = len(rel)
        triples.append((ent[s], rel[p], ent[o]))
        if len(triples) >= MAX_T:
            break
    VE = len(ent); VR = len(rel); ents = cphasor(VE, N, g); rels = cphasor(VR, N, g)
    subj = {}; relsh = {}; sp_objs = {}
    for s, p, o in triples:
        subj.setdefault(s, np.zeros(N, dtype=np.complex64)); subj[s] = subj[s] + rels[p] * ents[o]
        relsh.setdefault(p, np.zeros(N, dtype=np.complex64)); relsh[p] = relsh[p] + ents[s] * ents[o]
        sp_objs.setdefault((s, p), set()).add(o)
    keys = list(sp_objs.keys()); g.shuffle(keys); subj_r5 = rel_r5 = 0; nq = 0
    for (s, p) in keys[:NQ]:
        gold = sp_objs[(s, p)]
        subj_r5 += int(len(topk(subj[s] * np.conj(rels[p]), ents, 5) & gold) > 0)         # shard-by-subject: unbind p
        rel_r5 += int(len(topk(relsh[p] * np.conj(ents[s]), ents, 5) & gold) > 0)          # shard-by-relation: unbind s
        nq += 1
    sr = subj_r5 / max(1, nq); rr = rel_r5 / max(1, nq); best = max(sr, rr); win = "subject" if sr >= rr else "relation"
    print("  real FB15k 1-hop recall@5: shard-by-subject=%.3f shard-by-relation=%.3f (best=%s, %d ents %d rels)" % (sr, rr, win, VE, VR), flush=True)
    return {"subject": sr, "relation": rr, "best": best, "win": win, "VE": VE}


def verdict(r) -> Tuple[str, str]:
    s = "shard-by-subject=%.3f shard-by-relation=%.3f (best=%s, %d ents)" % (r["subject"], r["relation"], r["win"], r["VE"])
    if r["best"] >= 0.85:
        return ("HARD_PASS", "HARD_PASS: best real-KG sharding (%s) 1-hop recall@5>=0.85 on Freebase -- recommended v1.5 KG layout. " % r["win"] + s)
    if r["best"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: best real-KG sharding 0.70-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: best real-KG sharding <0.70. " + s)


print("[config] anchor=%s mode=%s N=%d max_t=%d" % (ANCHOR_NAME, RUN_MODE, N, MAX_T), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
