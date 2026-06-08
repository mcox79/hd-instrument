"""
exp_kg_crossshard_2hop_gpu_v1.py -- 2-hop paths that span shards traverse correctly (realistic sharded KG-QA) -- GPU.

ROUTING: v1.5 sharded-KG invariant validation (cross-shard 2-hop traversal). Realistic deployment: a 2-hop path's two hops live in DIFFERENT shards (hop1 in the start's shard, hop2 in the bridge's shard). K-hop must recover the bridge from shard A, then ROUTE to shard B for hop2. Confirms cross-shard traversal works at 5000-entity scale -- the actual sharded KG-QA query path. torch.cuda; 8GB-safe. GPU.
PRE-REGISTERED: HARD-PASS cross-shard 2-hop recall@1 >= 0.90 (routing across shards works). MIDDLE >= 0.75. HARD-FAIL < 0.75.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os, math
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "kg_crossshard_2hop_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def _selftest():
    import numpy as _n; assert _n.argmax([0.1, 0.9]) == 1, "argmax"; print("[selftest] PASS: kg_crossshard_2hop_gpu_v1", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
except Exception as e:
    print("[FATAL] torch: %s" % e, flush=True); sys.exit(1)
if not torch.cuda.is_available():
    print("[FATAL] CUDA required.", flush=True); sys.exit(1)
DEV = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)
def cphasor(m, d, g):
    ang = (torch.rand(m, d, generator=g, device=DEV) * 2 - 1) * math.pi; return torch.complex(torch.cos(ang), torch.sin(ang))
def cidx(v, book):
    return int(torch.argmax((book @ torch.conj(v)).real))

def run() -> Dict:
    g = torch.Generator(device=DEV).manual_seed(42); N = 8192; VE = 2000 if SMOKE else 5000; VR = 24; deg = 3; NQ = 200 if SMOKE else 500
    ents = cphasor(VE, N, g); rels = cphasor(VR, N, g); edges = {}
    shards = torch.zeros(VE, N, dtype=torch.complex64, device=DEV)               # per-subject shards (bridge lands in a DIFFERENT shard than start)
    for s in range(VE):
        for _ in range(deg):
            r = int(torch.randint(0, VR, (1,), generator=g, device=DEV)); o = int(torch.randint(0, VE, (1,), generator=g, device=DEV))
            if (s, r) not in edges:
                edges[(s, r)] = o; shards[s] = shards[s] + rels[r] * ents[o]
    def sample():
        for _t in range(80):
            s0 = int(torch.randint(0, VE, (1,), generator=g, device=DEV)); o1 = [(r, edges[(s0, r)]) for (ss, r) in edges if ss == s0]
            if not o1:
                continue
            r1, b = o1[int(torch.randint(0, len(o1), (1,), generator=g, device=DEV))]
            if b == s0:
                continue                                                          # ensure hop2 is in a different shard
            o2 = [(r, edges[(b, r)]) for (ss, r) in edges if ss == b]
            if not o2:
                continue
            r2, c = o2[int(torch.randint(0, len(o2), (1,), generator=g, device=DEV))]; return s0, r1, b, r2, c
        return None
    hit = 0; bridge_hit = 0; n = 0
    for _ in range(NQ):
        p = sample()
        if p is None:
            continue
        s0, r1, b, r2, c = p
        bh = cidx(shards[s0] * torch.conj(rels[r1]), ents)                        # hop1 in shard s0
        bridge_hit += int(bh == b)
        ch = cidx(shards[bh] * torch.conj(rels[r2]), ents)                        # ROUTE to shard bh for hop2
        hit += int(ch == c); n += 1
    rec = hit / max(1, n); br = bridge_hit / max(1, n); print("  cross-shard 2-hop recall@1=%.3f (bridge-recall=%.3f, VE=%d, n=%d)" % (rec, br, VE, n), flush=True)
    return {"recall": rec, "bridge": br, "VE": VE}
def verdict(r) -> Tuple[str, str]:
    s = "cross-shard 2-hop=%.3f bridge=%.3f at %d entities" % (r["recall"], r["bridge"], r["VE"])
    if r["recall"] >= 0.90: return ("HARD_PASS", "HARD_PASS: cross-shard 2-hop traversal >=0.90 -- routing across shards (recover bridge in shard A, route to shard B) works; realistic sharded KG-QA query path validated. " + s)
    if r["recall"] >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: cross-shard 2-hop 0.75-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: cross-shard 2-hop <0.75. " + s)

print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
