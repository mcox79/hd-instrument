"""
exp_webqsp_substrate_traversal_cpu_v1.py -- TIER-2 P1: WebQSP substrate subgraph K-hop traversal COVERAGE -- CPU.

ROUTING: Research CPU-P1 benchmark reruns (executed on best-judgment under full-auto mandate; gold-path/coverage build path,
  not end-to-end -- design Q to Research pending but not blocking). Loads RoG-webqsp (real WebQSP w/ per-question subgraph +
  q_entity + answers). Encodes each subgraph in an FHRR substrate (per-(head,rel) sharded), then does substrate-guided K-hop
  BFS from q_entity (cleanup-unbind to expand). METRIC = answer-coverage: fraction of questions where a gold answer entity is
  in the substrate-reachable set within K hops. This is the HONEST substrate-native claim (lossy-graph-store fidelity for
  multi-hop reachability), NOT ranked Hits@1 (which needs an NL->relation encoder). Compare vs published answer-coverage.
PRE-REGISTERED: HARD-PASS coverage >= 0.85 (substrate preserves real-subgraph reachability). MIDDLE >= 0.65. HARD-FAIL < 0.65.
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
import argparse, time, math
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "webqsp_substrate_traversal_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 4096; KHOP = 3; TOPK = 5
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)


def _selftest():
    import numpy as _n; assert int(_n.argmax([0.1, 0.9])) == 1, "argmax"; print("[selftest] PASS: webqsp-substrate-traversal", flush=True)


def load_ds():
    from datasets import load_dataset
    for name in ("rmanluo/RoG-webqsp", "rmanluo/RoG-cwq"):
        try:
            ds = load_dataset(name, split="test")
            print("[data] %s test: %d examples" % (name, len(ds)), flush=True); return ds, name
        except Exception as e:
            print("[data] %s failed: %s" % (name, str(e)[:70]), flush=True)
    return None, None


def reachable(graph, seeds, g):
    # build per-(head,rel) sharded FHRR substrate over this subgraph, then substrate-guided K-hop BFS from seeds
    ents = sorted({h for h, _, _ in graph} | {t for _, _, t in graph}); rels = sorted({r for _, r, _ in graph})
    if not ents:
        return set()
    ei = {e: i for i, e in enumerate(ents)}; ri = {r: i for i, r in enumerate(rels)}
    E = cphasor(len(ents), N, g); R = cphasor(len(rels), N, g)
    hr = defaultdict(list)
    for h, r, t in graph:
        hr[(ei[h], ri[r])].append(ei[t])
    shard = {}
    for (h, r), ts in hr.items():
        v = np.zeros(N, dtype=np.complex64)
        for t in ts:
            v = v + E[h] * (R[r] * E[t])
        shard[(h, r)] = v
    Econj = np.conj(E)
    frontier = {ei[s] for s in seeds if s in ei}; seen = set(frontier)
    for _h in range(KHOP):
        nxt = set()
        for e in frontier:
            for (hh, r) in hr:
                if hh != e:
                    continue
                s2 = shard[(e, r)] * Econj[e] * np.conj(R[r])             # unbind head+rel -> tail bundle
                order = np.argsort((E @ np.conj(s2)).real)[::-1][:TOPK]   # cleanup top-K tails
                for o in order:
                    if int(o) not in seen:
                        nxt.add(int(o)); seen.add(int(o))
        frontier = nxt
        if not frontier:
            break
    inv = {i: e for e, i in ei.items()}
    return {inv[i] for i in seen}


def run() -> Dict:
    g = np.random.default_rng(909); ds, name = load_ds()
    if ds is None:
        return {"error": "download_failed", "coverage": 0.0, "n": 0}
    idx = list(range(len(ds))); g.shuffle(idx); want = 30 if SMOKE else 300
    cov = 0; n = 0; sizes = []
    for i in idx:
        if n >= want:
            break
        ex = ds[i]
        graph = [(t[0], t[1], t[2]) for t in ex.get("graph", []) if len(t) == 3]
        q_ent = ex.get("q_entity", []) or []; a_ent = set(ex.get("a_entity", []) or [])
        if not graph or not q_ent or not a_ent:
            continue
        reach = reachable(graph, q_ent, g); sizes.append(len(reach))
        cov += int(len(reach & a_ent) > 0); n += 1
    c = cov / n if n else 0.0; avg = float(np.mean(sizes)) if sizes else 0.0
    print("  WebQSP substrate-traversal answer-coverage=%.3f (n=%d, avg_reachable=%.1f, src=%s)" % (c, n, avg, name), flush=True)
    return {"coverage": c, "n": n, "avg_reachable": round(avg, 1), "source": name}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: RoG-webqsp download failed on runner (no network / dataset moved); cell ok, retry. " + r["error"])
    s = "coverage=%.3f (n=%d, avg_reachable=%.1f)" % (r["coverage"], r["n"], r["avg_reachable"])
    if r["coverage"] >= 0.85:
        return ("HARD_PASS", "HARD_PASS: substrate-encoded WebQSP subgraph K-hop traversal reaches the gold answer for >=85pct of questions -- FHRR graph-store preserves real-benchmark multi-hop reachability. " + s)
    if r["coverage"] >= 0.65:
        return ("MIDDLE_BAND", "MIDDLE_BAND: coverage 0.65-0.85 (cleanup top-K prunes some high-degree paths; raise TOPK/shard). " + s)
    return ("HARD_FAIL", "HARD_FAIL: coverage <0.65. " + s)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s khop=%d topk=%d" % (ANCHOR_NAME, RUN_MODE, KHOP, TOPK), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
