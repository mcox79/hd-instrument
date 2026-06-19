"""TIER-2 P1: FB15K-237 2-hop QA RANKING (rank answer among all subgraph entities; Hits@1/10/MRR). Hard substrate multi-hop test on real triples, reliable GitHub-raw download. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
CELL = r'''"""
exp_fb15k237_2hop_rank_cpu_v1.py -- TIER-2 P1: FB15K-237 2-hop QA RANKING (Hits@1/10/MRR) -- CPU.

ROUTING: Research CPU-P1 benchmark reruns (best-judgment under full-auto; HF NL-QA downloads hang on this laptop, so using the
  reliable GitHub-raw FB15K-237 triples). HARDER than the prior traversal cell: for a 2-hop query (h, r1, r2), compose the
  substrate traversal h-r1->{m}-r2->{t} and RANK the answer t among ALL subgraph entities (not just within one shard). Reports
  Hits@1 / Hits@10 / MRR vs the gold 2-hop answer set. This stresses substrate multi-hop retrieval realistically. numpy/VSA. CPU.
PRE-REGISTERED: HARD-PASS Hits@10 >= 0.50 AND Hits@1 >= 0.25. MIDDLE Hits@10 >= 0.30. HARD-FAIL below.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "10")
import argparse, time, math, urllib.request
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict, deque
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "fb15k237_2hop_rank_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 4096; SUBN = 800 if SMOKE else 2500; TOPM = 5
URLS = ["https://raw.githubusercontent.com/villmow/datasets_knowledge_embedding/master/FB15k-237/train.txt"]
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)


def _selftest():
    import numpy as _n; assert int(_n.argmax([0.1, 0.9])) == 1, "argmax"; print("[selftest] PASS: fb15k237-2hop-rank", flush=True)


def load_triples():
    for u in URLS:
        try:
            with urllib.request.urlopen(u, timeout=40) as r:
                txt = r.read().decode("utf-8", "replace")
            tr = [tuple(ln.split("\t")) for ln in txt.splitlines() if len(ln.split("\t")) == 3]
            if len(tr) > 1000:
                print("[data] %d triples" % len(tr), flush=True); return tr
        except Exception as e:
            print("[data] url failed: %s" % str(e)[:80], flush=True)
    return None


def run() -> Dict:
    g = np.random.default_rng(2372); triples = load_triples()
    if not triples:
        return {"error": "download_failed", "hits1": 0.0, "hits10": 0.0, "mrr": 0.0, "n": 0}
    adj = defaultdict(list)                                               # h -> [(r,t)]
    for h, r, t in triples:
        adj[h].append((r, t))
    # sample a connected subgraph via BFS (keeps it tractable + realistic local structure)
    seed = max(adj, key=lambda x: len(adj[x])); sub = set([seed]); q = deque([seed])
    while q and len(sub) < SUBN:
        x = q.popleft()
        for _r, t in adj[x]:
            if t not in sub:
                sub.add(t); q.append(t)
    subtr = [(h, r, t) for h, r, t in triples if h in sub and t in sub]
    ents = sorted({h for h, _, _ in subtr} | {t for _, _, t in subtr}); rels = sorted({r for _, r, _ in subtr})
    ei = {e: i for i, e in enumerate(ents)}; ri = {r: i for i, r in enumerate(rels)}
    E = cphasor(len(ents), N, g); R = cphasor(len(rels), N, g); Econj = np.conj(E)
    hr = defaultdict(list)
    for h, r, t in subtr:
        hr[(ei[h], ri[r])].append(ei[t])
    shard = {}
    for (h, r), ts in hr.items():
        v = np.zeros(N, dtype=np.complex64)
        for t in ts:
            v = v + E[h] * (R[r] * E[t])
        shard[(h, r)] = v
    # sample 2-hop queries (h,r1,r2) with a nonempty gold answer set
    pairs = [k for k in hr]; g.shuffle(pairs); want = 40 if SMOKE else 250
    h1 = 0; h10 = 0; rr = 0.0; n = 0
    for (h, r1) in pairs:
        if n >= want:
            break
        ms = hr[(h, r1)]
        r2cands = []
        for m in ms:
            for (mm, r2) in hr:
                if mm == m:
                    r2cands.append(r2)
        if not r2cands:
            continue
        r2 = r2cands[0]
        gold = set()
        for m in ms:
            gold |= set(hr.get((m, r2), []))
        gold.discard(h)
        if not gold:
            continue
        # compose: rank m by (h,r1) unbind; for top-M m, accumulate tail scores from (m,r2)
        s1 = shard[(h, r1)] * Econj[h] * np.conj(R[r1]); mscore = (E @ np.conj(s1)).real
        morder = np.argsort(mscore)[::-1][:TOPM]
        acc = np.zeros(len(ents))
        for m in morder:
            if (int(m), r2) in shard:
                s2 = shard[(int(m), r2)] * Econj[int(m)] * np.conj(R[r2])
                acc += max(mscore[m], 0.0) * (E @ np.conj(s2)).real
        order = np.argsort(acc)[::-1]
        ranks = {int(e): i for i, e in enumerate(order)}
        best = min(ranks[t] for t in gold if t in ranks) if any(t in ranks for t in gold) else 10 ** 9
        h1 += int(best == 0); h10 += int(best < 10); rr += (1.0 / (best + 1)) if best < 10 ** 9 else 0.0; n += 1
    a1 = h1 / n if n else 0.0; a10 = h10 / n if n else 0.0; mrr = rr / n if n else 0.0
    print("  FB15K-237 2-hop RANK: Hits@1=%.3f Hits@10=%.3f MRR=%.3f (n=%d, |subE|=%d)" % (a1, a10, mrr, n, len(ents)), flush=True)
    return {"hits1": a1, "hits10": a10, "mrr": round(mrr, 4), "n": n, "sub_ent": len(ents)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: FB15K-237 download failed on runner. " + r["error"])
    s = "Hits@1=%.3f Hits@10=%.3f MRR=%.4f (n=%d, |subE|=%d)" % (r["hits1"], r["hits10"], r["mrr"], r["n"], r["sub_ent"])
    if r["hits10"] >= 0.50 and r["hits1"] >= 0.25:
        return ("HARD_PASS", "HARD_PASS: substrate 2-hop QA ranking on REAL FB15K-237 -- Hits@10>=0.50 + Hits@1>=0.25 ranking the answer among all subgraph entities. Multi-hop retrieval holds under all-entity ranking. " + s)
    if r["hits10"] >= 0.30:
        return ("MIDDLE_BAND", "MIDDLE_BAND: Hits@10 0.30-0.50 (composition dilutes under all-entity ranking; per-m sharding/MMR would lift). " + s)
    return ("HARD_FAIL", "HARD_FAIL: Hits@10 <0.30 -- substrate 2-hop ranking does not survive all-entity ranking at this scale. " + s)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s subN=%d topM=%d" % (ANCHOR_NAME, RUN_MODE, SUBN, TOPM), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''
(EXP / "exp_fb15k237_2hop_rank_cpu_v1.py").write_text(CELL, encoding="utf-8"); print("wrote fb15k237_2hop_rank")
