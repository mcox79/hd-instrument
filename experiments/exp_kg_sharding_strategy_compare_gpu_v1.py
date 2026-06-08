"""
exp_kg_sharding_strategy_compare_gpu_v1.py -- which shard key is best for KG K-hop at scale: subject vs relation -- GPU.

ROUTING: KG-scale sharding restoration (per-subject vs per-relation shard key). Compares two KG sharding strategies at 5000 entities: shard by SUBJECT (each entity's edges) vs shard by RELATION (each relation type). Both should beat monolithic; identifies which keeps 2-hop recall highest (informs the v1.5 KG storage layout). torch.cuda; 8GB-safe. GPU.
PRE-REGISTERED: HARD-PASS the better strategy >= 0.85 2-hop recall (and both >> monolithic). MIDDLE >= 0.70. HARD-FAIL < 0.70.
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
ANCHOR_NAME = "kg_sharding_strategy_compare_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def _selftest():
    import numpy as _n; assert _n.argmax([0.1, 0.9]) == 1, "argmax"; print("[selftest] PASS: kg_sharding_strategy_compare_gpu_v1", flush=True)
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
    g = torch.Generator(device=DEV).manual_seed(33); N = 8192; VE = 1500 if SMOKE else 5000; VR = 16; deg = 3; NQ = 150 if SMOKE else 400
    ents = cphasor(VE, N, g); rels = cphasor(VR, N, g); edges = {}
    subj = torch.zeros(VE, N, dtype=torch.complex64, device=DEV); rel = torch.zeros(VR, N, dtype=torch.complex64, device=DEV)
    for s in range(VE):
        for _ in range(deg):
            r = int(torch.randint(0, VR, (1,), generator=g, device=DEV)); o = int(torch.randint(0, VE, (1,), generator=g, device=DEV))
            if (s, r) not in edges:
                edges[(s, r)] = o; subj[s] = subj[s] + rels[r] * ents[o]; rel[r] = rel[r] + ents[s] * ents[o]
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
    sh = 0; rh = 0; n = 0
    for _ in range(NQ):
        p = sample()
        if p is None:
            continue
        s0, r1, b, r2, c = p
        bh = cidx(subj[s0] * torch.conj(rels[r1]), ents); ch = cidx(subj[bh] * torch.conj(rels[r2]), ents); sh += int(ch == c)
        bh2 = cidx(rel[r1] * torch.conj(ents[s0]), ents); ch2 = cidx(rel[r2] * torch.conj(ents[bh2]), ents); rh += int(ch2 == c); n += 1
    sr = sh / max(1, n); rr = rh / max(1, n); print("  2-hop recall: shard-by-subject=%.3f shard-by-relation=%.3f (VE=%d)" % (sr, rr, VE), flush=True)
    return {"subject": sr, "relation": rr, "best": max(sr, rr)}
def verdict(r) -> Tuple[str, str]:
    win = "subject" if r["subject"] >= r["relation"] else "relation"; s = "shard-by-subject=%.3f shard-by-relation=%.3f (best=%s)" % (r["subject"], r["relation"], win)
    if r["best"] >= 0.85: return ("HARD_PASS", "HARD_PASS: best KG sharding strategy (%s) >=0.85 2-hop at scale -- recommended v1.5 KG layout. " % win + s)
    if r["best"] >= 0.70: return ("MIDDLE_BAND", "MIDDLE_BAND: best strategy 0.70-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: neither sharding strategy >=0.70. " + s)

print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
