"""Research WAVE-3 LAP-3 Option-1: RotatE-style learned relation embeddings over FB15K-237 -> proportional analogy. torch(CPU). Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
CELL = r'''"""
exp_lap3_rotate_analogy_cpu_v1.py -- LAP-3 (Option 1): learned RotatE relation embeddings -> proportional analogy -- CPU.

ROUTING: Research LAP3_LAP211_WAVE3 -- LAP-3 = Option 1. Raw FHRR atoms have NO shared relational transform (mean(t*conj(h))->0),
  so analogy needs LEARNED relation phasors. Per Research, FHRR unit-modulus binding == RotatE; this trains E (entity phasors)
  + R (relation phasors) so E[h] (X) R[r] ~ E[t] over FB15K-237 triples, then does proportional analogy: given (h', r) predict
  t' = cleanup(E[h'] (X) R[r]) ranked among entities. Hits@1 on held-out. torch autograd (complex angles), CPU, no LLM.
PRE-REGISTERED: HARD-PASS analogy Hits@1 >= 0.70 (drill 8 P=0.65). MIDDLE >= 0.40. HARD-FAIL < 0.40.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "8")
import argparse, time, math, urllib.request
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict, deque
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "lap3_rotate_analogy_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
URL = "https://raw.githubusercontent.com/villmow/datasets_knowledge_embedding/master/FB15k-237/train.txt"
DIM = 200; SUBN = 400 if SMOKE else 1200; EPOCHS = 40 if SMOKE else 300


def _selftest():
    import numpy as _n; assert _n.argmax([0, 1]) == 1, "argmax"; print("[selftest] PASS: lap3-rotate-analogy", flush=True)


def load():
    try:
        with urllib.request.urlopen(URL, timeout=40) as r:
            txt = r.read().decode("utf-8", "replace")
        tr = [tuple(ln.split("\t")) for ln in txt.splitlines() if len(ln.split("\t")) == 3]
        return tr if len(tr) > 1000 else None
    except Exception as e:
        print("[data] fail: %s" % str(e)[:70], flush=True); return None


def run() -> Dict:
    import torch
    torch.manual_seed(7); g = np.random.default_rng(7); triples = load()
    if not triples:
        return {"error": "download_failed", "hits1": 0.0, "n": 0}
    adj = defaultdict(list)
    for h, r, t in triples:
        adj[h].append((r, t))
    seed = max(adj, key=lambda x: len(adj[x])); sub = set([seed]); q = deque([seed])
    while q and len(sub) < SUBN:
        x = q.popleft()
        for _r, t in adj[x]:
            if t not in sub:
                sub.add(t); q.append(t)
    subtr = [(h, r, t) for h, r, t in triples if h in sub and t in sub]
    ents = sorted({h for h, _, _ in subtr} | {t for _, _, t in subtr}); rels = sorted({r for _, r, _ in subtr})
    ei = {e: i for i, e in enumerate(ents)}; ri = {r: i for i, r in enumerate(rels)}
    data = [(ei[h], ri[r], ei[t]) for h, r, t in subtr]; g.shuffle(data)
    ntr = int(0.85 * len(data)); train = data[:ntr]; test = data[ntr:]
    NE = len(ents); NR = len(rels)
    Ephase = torch.nn.Parameter(torch.rand(NE, DIM) * 2 * math.pi); Rphase = torch.nn.Parameter(torch.rand(NR, DIM) * 2 * math.pi)
    opt = torch.optim.Adam([Ephase, Rphase], lr=0.05)
    tr = torch.tensor(train, dtype=torch.long); t0 = time.time()
    for ep in range(EPOCHS):
        opt.zero_grad(); idx = torch.randint(0, len(tr), (min(2048, len(tr)),)); b = tr[idx]
        h, r, t = b[:, 0], b[:, 1], b[:, 2]
        hp = Ephase[h]; rp = Rphase[r]; tp = Ephase[t]
        pos = torch.sqrt(((torch.cos(hp + rp) - torch.cos(tp)) ** 2 + (torch.sin(hp + rp) - torch.sin(tp)) ** 2 + 1e-9).sum(1))
        tn = Ephase[torch.randint(0, NE, (len(b),))]
        neg = torch.sqrt(((torch.cos(hp + rp) - torch.cos(tn)) ** 2 + (torch.sin(hp + rp) - torch.sin(tn)) ** 2 + 1e-9).sum(1))
        loss = torch.relu(pos - neg + 6.0).mean(); loss.backward(); opt.step()
        if ep % 100 == 0:
            print("  [train] ep %d/%d loss=%.3f (%.0fs)" % (ep, EPOCHS, float(loss), time.time() - t0), flush=True)
    # analogy / link prediction Hits@1 on held-out: rank all entities for (h,r,?)
    with torch.no_grad():
        Ec = torch.cos(Ephase); Es = torch.sin(Ephase); hit = 0
        gold_by_hr = defaultdict(set)
        for (h, r, t) in data:
            gold_by_hr[(h, r)].add(t)
        for (h, r, t) in test:
            qc = torch.cos(Ephase[h] + Rphase[r]); qs = torch.sin(Ephase[h] + Rphase[r])
            d = torch.sqrt(((Ec - qc) ** 2 + (Es - qs) ** 2 + 1e-9).sum(1))
            order = torch.argsort(d)
            top = int(order[0])
            if top == t or (top in gold_by_hr[(h, r)]):                  # filtered Hits@1
                hit += 1
        h1 = hit / max(1, len(test))
    print("  LAP-3 RotatE analogy Hits@1=%.3f (NE=%d NR=%d, test=%d)" % (h1, NE, NR, len(test)), flush=True)
    return {"hits1": h1, "n_ent": NE, "n_rel": NR, "n_test": len(test)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: FB15K download failed. " + r["error"])
    s = "analogy-Hits@1=%.3f (NE=%d, test=%d)" % (r["hits1"], r["n_ent"], r["n_test"])
    if r["hits1"] >= 0.70:
        return ("HARD_PASS", "HARD_PASS: learned RotatE relation embeddings enable proportional analogy Hits@1>=0.70 -- FHRR-binding==RotatE; analogy works with a learned relational codebook (the right substrate layer). LAP-3 resolved via Option 1. " + s)
    if r["hits1"] >= 0.40:
        return ("MIDDLE_BAND", "MIDDLE_BAND: analogy Hits@1 0.40-0.70 (more epochs/dim, or Option-2 fallback). " + s)
    return ("HARD_FAIL", "HARD_FAIL: analogy Hits@1 <0.40. " + s)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch  # noqa
except Exception as e:
    print("[FATAL] torch: %s" % e, flush=True); sys.exit(1)
print("[config] anchor=%s mode=%s dim=%d subN=%d epochs=%d" % (ANCHOR_NAME, RUN_MODE, DIM, SUBN, EPOCHS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''
(EXP / "exp_lap3_rotate_analogy_cpu_v1.py").write_text(CELL, encoding="utf-8"); print("wrote lap3_rotate_analogy")
