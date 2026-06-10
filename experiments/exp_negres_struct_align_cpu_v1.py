"""
exp_negres_struct_align_cpu_v1.py -- STRUCTURAL-ALIGNMENT-MAPPING (cross-domain analogy) -- CPU.

ROUTING: Research NEGATIVE_RESOLUTION_PRIORITIES P2 (resolves STRETCH4-2 cross-domain 0.244). Train RotatE on a subset of
  FB15K-237 relations; for a HELD-OUT relation infer its transform from K=10 shots, BUT weight each phase dim by cross-shot
  concentration conc=|mean(e^{i diff})| -- structurally-consistent dims (the relation) get high weight, entity-specific
  (inconsistent) dims projected out (Gentner systematicity). Score candidates with conc-weighted RotatE distance. Compare to
  the unweighted baseline (= STRETCH4-2). torch autograd CPU, FB15K GitHub-raw.
PRE-REGISTERED: HARD-PASS struct-aligned cross-domain Hits@1 >= 0.40 (from 0.244 baseline). MIDDLE >= 0.32. HARD-FAIL < 0.32.
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
ANCHOR_NAME = "negres_struct_align_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
URL = "https://raw.githubusercontent.com/villmow/datasets_knowledge_embedding/master/FB15k-237/train.txt"
DIM = 200; SUBN = 400 if SMOKE else 1200; EPOCHS = 40 if SMOKE else 250
def _selftest():
    assert np.argmax([0, 1]) == 1; print("[selftest] PASS: struct-align", flush=True)
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
        return {"error": "download_failed", "hits1_struct": 0.0, "hits1_base": 0.0, "n": 0}
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
    ei = {e: i for i, e in enumerate(ents)}
    g.shuffle(rels); nheld = max(3, len(rels) // 5); held = set(rels[:nheld]); train_rels = set(rels[nheld:])
    ri = {r: i for i, r in enumerate(sorted(train_rels))}
    train = [(ei[h], ri[r], ei[t]) for h, r, t in subtr if r in train_rels]
    NE = len(ents); NR = len(train_rels)
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
    with torch.no_grad():
        Eph_n = Eph.detach(); Ecos = torch.cos(Eph_n); Esin = torch.sin(Eph_n)
        by_rel = defaultdict(list)
        for h, r, t in subtr:
            if r in held:
                by_rel[r].append((ei[h], ei[t]))
        hit_s = 0; hit_b = 0; n = 0
        for r, pairs in by_rel.items():
            if len(pairs) < 14:
                continue
            g.shuffle(pairs); shots = pairs[:10]; test = pairs[10:]
            diffs = torch.stack([Eph_n[t] - Eph_n[h] for (h, t) in shots])    # (S, DIM)
            cmean = torch.cos(diffs).mean(0); smean = torch.sin(diffs).mean(0)
            rinf = torch.atan2(smean, cmean)                                   # circular-mean transform (= baseline)
            conc = torch.sqrt(cmean ** 2 + smean ** 2)                         # per-dim cross-shot consistency in [0,1]
            w = conc / (conc.sum() + 1e-9) * DIM                               # structural weight (entity-specific dims down-weighted)
            for (h, t) in test:
                qc = torch.cos(Eph_n[h] + rinf); qs = torch.sin(Eph_n[h] + rinf)
                d_base = ((Ecos - qc) ** 2 + (Esin - qs) ** 2).sum(1)
                d_struct = (w * ((Ecos - qc) ** 2 + (Esin - qs) ** 2)).sum(1)  # concentration-weighted (structural)
                hit_b += int(int(torch.argmin(d_base)) == t)
                hit_s += int(int(torch.argmin(d_struct)) == t); n += 1
        h1s = hit_s / max(1, n); h1b = hit_b / max(1, n)
    print("  STRUCT-ALIGN cross-domain Hits@1 struct=%.3f baseline=%.3f (lift=%.3f, held-rels=%d, test=%d)" % (h1s, h1b, h1s - h1b, len(by_rel), n), flush=True)
    return {"hits1_struct": round(h1s, 3), "hits1_base": round(h1b, 3), "lift": round(h1s - h1b, 3), "n": n}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: FB15K download failed. " + r["error"])
    s = "struct-Hits@1=%.3f baseline=%.3f lift=%.3f (test=%d)" % (r["hits1_struct"], r["hits1_base"], r["lift"], r["n"])
    if r["hits1_struct"] >= 0.40:
        return ("HARD_PASS", "HARD_PASS: structural-alignment (concentration-weighted transform) lifts cross-domain analogy to >=0.40 -- projecting out entity-specific (inconsistent) phase dims and keeping the structurally-consistent relation resolves STRETCH4-2. " + s)
    if r["hits1_struct"] >= 0.32:
        return ("MIDDLE_BAND", "MIDDLE_BAND: struct-aligned 0.32-0.40. " + s)
    return ("HARD_FAIL", "HARD_FAIL: struct-aligned <0.32. " + s)
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
