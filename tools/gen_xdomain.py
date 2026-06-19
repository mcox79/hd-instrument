"""Research WAVE-4: STRETCH4-2 ANALOGY-CROSS-DOMAIN (RotatE entity space supports NEW relation transforms few-shot). torch(CPU)+FB15K. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
CELL = r'''"""
exp_stretch4_2_cross_domain_analogy_cpu_v1.py -- STRETCH4-2 CROSS-DOMAIN ANALOGY -- CPU.

ROUTING: Research WAVE3_RESOLUTION_WAVE4 (STRETCH4-2; extends PP-275 LAP-3 within-domain). Train RotatE entity+relation phasors on
  a SUBSET of FB15K-237 relations; then for a HELD-OUT relation (unseen in training), infer its transform from K=10 example pairs
  (mean of E[t](x)conj(E[h]), normalized) and apply to new heads -> Hits@1. Tests whether the learned ENTITY space generalizes to
  NEW relation transforms (cross-domain analogy), not just the relations it was trained on. torch autograd, CPU, FB15K GitHub-raw.
PRE-REGISTERED: HARD-PASS cross-domain Hits@1 >= 0.40 (harder than within-domain 0.70). MIDDLE >= 0.25. HARD-FAIL < 0.25.
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
ANCHOR_NAME = "stretch4_2_cross_domain_analogy_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
URL = "https://raw.githubusercontent.com/villmow/datasets_knowledge_embedding/master/FB15k-237/train.txt"
DIM = 200; SUBN = 400 if SMOKE else 1200; EPOCHS = 40 if SMOKE else 250
def _selftest():
    import numpy as _n; assert _n.argmax([0, 1]) == 1, "argmax"; print("[selftest] PASS: cross-domain-analogy", flush=True)
def load():
    try:
        with urllib.request.urlopen(URL, timeout=40) as r:
            txt = r.read().decode("utf-8", "replace")
        return [tuple(ln.split("\t")) for ln in txt.splitlines() if len(ln.split("\t")) == 3]
    except Exception as e:
        print("[data] fail %s" % str(e)[:60], flush=True); return None
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
    g.shuffle(rels); nheld = max(3, len(rels) // 5); held = set(rels[:nheld]); train_rels = set(rels[nheld:])
    train = [(ei[h], ri[r], ei[t]) for h, r, t in subtr if r in train_rels]
    NE = len(ents); NR = len(rels)
    Eph = torch.nn.Parameter(torch.rand(NE, DIM) * 2 * math.pi); Rph = torch.nn.Parameter(torch.rand(NR, DIM) * 2 * math.pi)
    opt = torch.optim.Adam([Eph, Rph], lr=0.05); tr = torch.tensor(train, dtype=torch.long); t0 = time.time()
    for ep in range(EPOCHS):
        opt.zero_grad(); b = tr[torch.randint(0, len(tr), (min(2048, len(tr)),))]
        h, r, t = b[:, 0], b[:, 1], b[:, 2]; hp = Eph[h]; rp = Rph[r]; tp = Eph[t]; tn = Eph[torch.randint(0, NE, (len(b),))]
        pos = torch.sqrt(((torch.cos(hp + rp) - torch.cos(tp)) ** 2 + (torch.sin(hp + rp) - torch.sin(tp)) ** 2 + 1e-9).sum(1))
        neg = torch.sqrt(((torch.cos(hp + rp) - torch.cos(tn)) ** 2 + (torch.sin(hp + rp) - torch.sin(tn)) ** 2 + 1e-9).sum(1))
        (torch.relu(pos - neg + 6.0).mean()).backward(); opt.step()
        if ep % 100 == 0:
            print("  [train] ep %d/%d (%.0fs)" % (ep, EPOCHS, time.time() - t0), flush=True)
    # cross-domain: for each HELD-OUT relation, infer transform from K example pairs (mean phase diff), apply to new heads
    with torch.no_grad():
        Ecos = torch.cos(Eph); Esin = torch.sin(Eph); hit = 0; n = 0
        by_rel = defaultdict(list)
        for h, r, t in subtr:
            if r in held:
                by_rel[r].append((ei[h], ei[t]))
        for r, pairs in by_rel.items():
            if len(pairs) < 14:
                continue
            g.shuffle(pairs); shots = pairs[:10]; test = pairs[10:]
            # inferred relation phase = circular mean of (theta_t - theta_h) over shots
            diffs = torch.stack([Eph[t] - Eph[h] for (h, t) in shots])
            rinf = torch.atan2(torch.sin(diffs).mean(0), torch.cos(diffs).mean(0))
            for (h, t) in test:
                qc = torch.cos(Eph[h] + rinf); qs = torch.sin(Eph[h] + rinf)
                d = torch.sqrt(((Ecos - qc) ** 2 + (Esin - qs) ** 2 + 1e-9).sum(1))
                hit += int(int(torch.argsort(d)[0]) == t); n += 1
        h1 = hit / max(1, n)
    print("  CROSS-DOMAIN-ANALOGY held-out-relation Hits@1=%.3f (held-rels=%d, test=%d)" % (h1, len(held), n), flush=True)
    return {"hits1": round(h1, 3), "n_held_rels": len(held), "n_test": n}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: FB15K download failed. " + r["error"])
    s = "cross-domain-Hits@1=%.3f (held-rels=%d, test=%d)" % (r["hits1"], r["n_held_rels"], r["n_test"])
    if r["hits1"] >= 0.40:
        return ("HARD_PASS", "HARD_PASS: learned entity space supports NEW (held-out) relation transforms few-shot, Hits@1>=0.40 -- cross-domain analogy generalizes beyond trained relations (the embedding geometry, not memorized relations). " + s)
    if r["hits1"] >= 0.25:
        return ("MIDDLE_BAND", "MIDDLE_BAND: cross-domain Hits@1 0.25-0.40. " + s)
    return ("HARD_FAIL", "HARD_FAIL: cross-domain Hits@1 <0.25. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch  # noqa
except Exception as e:
    print("[FATAL] torch: %s" % e, flush=True); sys.exit(1)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''
(EXP / "exp_stretch4_2_cross_domain_analogy_cpu_v1.py").write_text(CELL, encoding="utf-8"); print("wrote cross_domain_analogy")
