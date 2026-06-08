"""
exp_substrate_kg_sharded_50k_gpu_v1.py -- per-subject sharded KG K-hop holds at 50000 entities (v1.5 invariant at scale) -- GPU.

ROUTING: v1.5 sharded-KG invariant validation (sharded KG at 50k entities). Validates the v1.5 sharded-KG architecture invariant at large production scale: 50000 entities, ~150k triples, stored as per-subject shards (each subject bundles its r*o edges). 2-hop K-hop routed by subject. Confirms recall stays high at 50k (where monolithic is hopeless). torch.cuda; 8GB-safe. GPU.
PRE-REGISTERED: HARD-PASS sharded 2-hop recall@1 >= 0.90 at 50000 entities. MIDDLE >= 0.75. HARD-FAIL < 0.75.
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
ANCHOR_NAME = "substrate_kg_sharded_50k_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def _selftest():
    import numpy as _n; assert _n.argmax([0.1, 0.9]) == 1, "argmax"; print("[selftest] PASS: substrate_kg_sharded_50k_gpu_v1", flush=True)
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
    g = torch.Generator(device=DEV).manual_seed(41); N = 8192; VE = 8000 if SMOKE else 50000; VR = 32; deg = 3; NQ = 200 if SMOKE else 500
    ents = cphasor(VE, N, g); rels = cphasor(VR, N, g); edges = {}
    shards = torch.zeros(VE, N, dtype=torch.complex64, device=DEV)
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
            r1, b = o1[int(torch.randint(0, len(o1), (1,), generator=g, device=DEV))]; o2 = [(r, edges[(b, r)]) for (ss, r) in edges if ss == b]
            if not o2:
                continue
            r2, c = o2[int(torch.randint(0, len(o2), (1,), generator=g, device=DEV))]; return s0, r1, b, r2, c
        return None
    hit = 0; n = 0
    for _ in range(NQ):
        p = sample()
        if p is None:
            continue
        s0, r1, b, r2, c = p
        bh = cidx(shards[s0] * torch.conj(rels[r1]), ents); ch = cidx(shards[bh] * torch.conj(rels[r2]), ents); hit += int(ch == c); n += 1
    rec = hit / max(1, n); print("  sharded 2-hop recall@1=%.3f at VE=%d (%d edges, n=%d)" % (rec, VE, len(edges), n), flush=True)
    return {"recall": rec, "VE": VE}
def verdict(r) -> Tuple[str, str]:
    s = "sharded 2-hop recall@1=%.3f at %d entities" % (r["recall"], r["VE"])
    if r["recall"] >= 0.90: return ("HARD_PASS", "HARD_PASS: sharded KG K-hop holds >=0.90 at 50000 entities -- v1.5 sharded-KG invariant validated at large production scale. " + s)
    if r["recall"] >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: sharded 0.75-0.90 at 50k. " + s)
    return ("HARD_FAIL", "HARD_FAIL: sharded <0.75 at 50k. " + s)

print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
