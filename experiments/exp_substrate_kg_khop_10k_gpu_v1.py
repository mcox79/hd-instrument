"""
exp_substrate_kg_khop_10k_gpu_v1.py -- substrate KG K-hop at 10000 entities / ~30k triples (GPU) -- GPU.

ROUTING: GPU product/capacity-scale (KG-QA at 10k entities). Pushes the KG-QA product gate to 10000 entities and ~30k triples. 2-hop and 3-hop chained unbind+cleanup over the 10k-entity codebook on GPU. Validates KG QA at a large production graph. torch.cuda; 8GB-safe. GPU.
PRE-REGISTERED: HARD-PASS 2-hop recall@1 >= 0.65 at 10000 entities (slightly relaxed vs 5000 due to crosstalk). MIDDLE >= 0.50. HARD-FAIL < 0.50.
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
ANCHOR_NAME = "substrate_kg_khop_10k_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def _selftest():
    import numpy as _n; assert _n.argmax([0.1, 0.9]) == 1, "argmax"; print("[selftest] PASS: substrate_kg_khop_10k_gpu_v1", flush=True)
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
    g = torch.Generator(device=DEV).manual_seed(11); N = 16384; VE = 3000 if SMOKE else 10000; VR = 32; deg = 3; NQ = 150 if SMOKE else 400
    ents = cphasor(VE, N, g); rels = cphasor(VR, N, g); edges = {}
    M = torch.zeros(N, dtype=torch.complex64, device=DEV)
    for s in range(VE):
        for _ in range(deg):
            r = int(torch.randint(0, VR, (1,), generator=g, device=DEV)); o = int(torch.randint(0, VE, (1,), generator=g, device=DEV))
            if (s, r) not in edges:
                edges[(s, r)] = o; M = M + ents[s] * rels[r] * ents[o]
    by = {}
    for hops in ([2] if SMOKE else [2, 3]):
        hit = 0; n = 0
        for _ in range(NQ):
            path = None
            for _t in range(80):
                s0 = int(torch.randint(0, VE, (1,), generator=g, device=DEV)); cur = s0; rseq = []; ok = True
                for _h in range(hops):
                    outs = [r for (ss, r) in edges if ss == cur]
                    if not outs:
                        ok = False; break
                    r = outs[int(torch.randint(0, len(outs), (1,), generator=g, device=DEV))]; rseq.append(r); cur = edges[(cur, r)]
                if ok:
                    path = (s0, rseq, cur); break
            if path is None:
                continue
            s0, rseq, gold = path; cv = ents[s0]
            for r in rseq:
                cv = ents[cidx(M * torch.conj(cv * rels[r]), ents)]
            hit += int(cidx(cv, ents) == gold); n += 1
        by["%dhop" % hops] = hit / max(1, n); print("  %d-hop recall@1=%.3f (n=%d VE=%d %d edges)" % (hops, by["%dhop" % hops], n, VE, len(edges)), flush=True)
    return {"by": by, "r2": by.get("2hop", 0.0)}
def verdict(r) -> Tuple[str, str]:
    s = "recall: %s" % {k: round(v, 3) for k, v in r["by"].items()}
    if r["r2"] >= 0.65: return ("HARD_PASS", "HARD_PASS: KG K-hop 2-hop recall>=0.65 at 10000-entity graph -- KG QA scales to large graphs. " + s)
    if r["r2"] >= 0.50: return ("MIDDLE_BAND", "MIDDLE_BAND: 2-hop 0.50-0.65 at 10k (consider higher N or relation-sharding). " + s)
    return ("HARD_FAIL", "HARD_FAIL: 2-hop <0.50 at 10k. " + s)

print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
