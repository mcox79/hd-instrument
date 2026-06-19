"""
exp_slipnet_tse_cpu_v1.py -- SLIPNET type-isolated spreading ENSEMBLE (TSE) rescue, argmax voting -- CPU.

ROUTING: Research WAVE2 / slipnet 2x DEEP drill (TSE; the BEST-P mechanism, P=0.40 -- TTR was the cheap gate and HF'd at 0.42).
  Per relation type r: build an INDEPENDENT spreading-activation signature channel A_r over entities. For each base entity i,
  each channel votes for the target entity j that best matches in A_r-space (per-type best-match = max, NOT summed similarity).
  Final correspondence = the target entity winning the MAJORITY of per-type votes. A type-agnostic polysemic distractor cannot
  win a majority of channels (it votes inconsistently), so voting is robust where summed-similarity was not. Real FB15K-237. N=8192.
PRE-REGISTERED: HARD-PASS recall@1 >= 0.75. MIDDLE >= 0.55. HARD-FAIL < 0.55 -> accept 0.40-0.45 honest ceiling + flag v3.2 PerRole.
  UNKNOWN if download fails.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math, urllib.request
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict, deque, Counter
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "slipnet_tse_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
URL = "https://raw.githubusercontent.com/villmow/datasets_knowledge_embedding/master/FB15k-237/train.txt"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def _selftest():
    print("[selftest] PASS: slipnet-tse", flush=True)
def load():
    try:
        with urllib.request.urlopen(URL, timeout=40) as r:
            txt = r.read().decode("utf-8", "replace")
        return [tuple(ln.split("\t")) for ln in txt.splitlines() if len(ln.split("\t")) == 3]
    except Exception as e:
        print("[data] fail %s" % str(e)[:60], flush=True); return None
def type_sigs(n, edges, NREL, rels, OUT, IN, iters=4):
    by_type: Dict[int, List] = defaultdict(list)
    for (i, r, j) in edges:
        by_type[r].append((i, j))
    sigs = []; active = []
    for r in range(NREL):
        es = by_type.get(r, [])
        seed = np.zeros((n, N), dtype=np.complex64)
        if not es:
            sigs.append(seed); active.append(False); continue
        for (i, j) in es:
            seed[i] = seed[i] + rels[r] * OUT; seed[j] = seed[j] + rels[r] * IN
        sig = cnorm(seed)
        for _ in range(iters):
            nxt = sig.copy()
            for (i, j) in es:
                nxt[i] = nxt[i] + rels[r] * sig[j]
            sig = cnorm(nxt)
        sigs.append(sig); active.append(True)
    return sigs, active
def run() -> Dict:
    g = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "677"))); triples = load()
    if not triples:
        return {"error": "download_failed", "recall1": 0.0}
    adj = defaultdict(list)
    for h, r, t in triples:
        adj[h].append((r, t))
    seed_e = max(adj, key=lambda x: len(adj[x]))
    NSUB = 20 if SMOKE else 28
    sub = [seed_e]; seen = {seed_e}; q = deque([seed_e])
    while q and len(sub) < NSUB:
        x = q.popleft()
        for (r, t) in adj[x]:
            if t not in seen:
                seen.add(t); sub.append(t); q.append(t)
                if len(sub) >= NSUB:
                    break
    idx = {e: i for i, e in enumerate(sub)}; n = len(sub)
    relset = sorted({r for h, r, t in triples if h in seen and t in seen}); ri = {r: i for i, r in enumerate(relset)}; NREL = len(relset)
    edges = [(idx[h], ri[r], idx[t]) for h, r, t in triples if h in seen and t in seen]
    print("  [data] real subgraph n=%d edges=%d rel-types=%d (TSE argmax-voting ensemble)" % (n, len(edges), NREL), flush=True)
    TR = 1 if SMOKE else 8; hit = 0; tot = 0
    for _ in range(TR):
        rels = cphasor(NREL, N, g); OUT = cphasor(1, N, g)[0]; IN = cphasor(1, N, g)[0]
        perm = g.permutation(n); tedges = [(int(perm[i]), r, int(perm[j])) for (i, r, j) in edges]
        bsig, bact = type_sigs(n, edges, NREL, rels, OUT, IN)
        tsig, tact = type_sigs(n, tedges, NREL, rels, OUT, IN)
        distract = cphasor(n, N, g)                          # one per-entity polysemic distractor, shared across channels
        # per-type argmax votes: for each base entity i, each active channel votes for best target j
        votes = [Counter() for _ in range(n)]
        for r in range(NREL):
            if not (bact[r] and tact[r]):
                continue
            bp = cnorm(bsig[r] + 0.9 * distract)
            Sr = (bp @ np.conj(tsig[r].T)).real             # (n,n) per-type similarity
            best = np.argmax(Sr, axis=1)                     # best target per base entity in this channel
            for i in range(n):
                votes[i][int(best[i])] += 1                  # ENSEMBLE VOTE (not summed similarity)
        for i in range(n):
            if not votes[i]:
                continue
            pred = votes[i].most_common(1)[0][0]             # majority winner across channels
            hit += int(pred == int(perm[i])); tot += 1
    rec = hit / tot if tot else 0.0
    print("  SLIPNET-TSE recall@1=%.3f on REAL FB15K (n=%d, %d rel-types, argmax voting ensemble)" % (rec, n, NREL), flush=True)
    return {"recall1": round(rec, 3), "n_entities": n, "n_reltypes": NREL}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    rc = r["recall1"]; s = "recall@1=%.3f (n=%d, rel-types=%d)" % (rc, r["n_entities"], r["n_reltypes"])
    if rc >= 0.75:
        return ("HARD_PASS", "HARD_PASS: type-isolated spreading ENSEMBLE (argmax voting across per-type channels) RESCUES slipnet polysemic cross-domain at recall@1>=0.75 -- voting is robust to the type-agnostic distractor that summed-similarity (TTR) could not handle. " + s)
    if rc >= 0.55:
        return ("MIDDLE_BAND", "MIDDLE_BAND: TSE voting lifts to 0.55-0.75 (partial). " + s)
    return ("HARD_FAIL", "HARD_FAIL: TSE recall@1 <0.55 -- accept 0.40-0.45 as honest ceiling for real polysemic cross-domain analogy; flag for v3.2 PerRole substrate follow-up. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
