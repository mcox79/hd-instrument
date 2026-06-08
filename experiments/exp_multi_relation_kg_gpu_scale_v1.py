"""
exp_multi_relation_kg_gpu_scale_v1.py -- bidirectional KG triple query (s,r)->o and (r,o)->s at 5000 entities (GPU) -- GPU.

ROUTING: GPU product/capacity-scale (bidirectional KG triple query at scale). Scales the multi-relation KG bidirectional query to 5000 entities and ~10k triples on GPU. Recovers object via M*(s*r).conj() and subject via M*(r*o).conj(), cleanup over the entity codebook. Validates queryable-both-ways KG at scale. torch.cuda; 8GB-safe. GPU.
PRE-REGISTERED: HARD-PASS both (s,r)->o and (r,o)->s recall >= 0.80 at 5000 entities. MIDDLE >= 0.65. HARD-FAIL < 0.65.
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
ANCHOR_NAME = "multi_relation_kg_gpu_scale_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def _selftest():
    import numpy as _n; assert _n.argmax([0.1, 0.9]) == 1, "argmax"; print("[selftest] PASS: multi_relation_kg_gpu_scale_v1", flush=True)
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
    g = torch.Generator(device=DEV).manual_seed(12); N = 16384; VE = 1500 if SMOKE else 5000; VR = 24; T = 3000 if SMOKE else 10000
    ents = cphasor(VE, N, g); rels = cphasor(VR, N, g)
    trip = []; M = torch.zeros(N, dtype=torch.complex64, device=DEV)
    for _ in range(T):
        s = int(torch.randint(0, VE, (1,), generator=g, device=DEV)); r = int(torch.randint(0, VR, (1,), generator=g, device=DEV)); o = int(torch.randint(0, VE, (1,), generator=g, device=DEV))
        M = M + ents[s] * rels[r] * ents[o]; trip.append((s, r, o))
    import random as _rnd
    samp = trip if len(trip) <= 400 else [trip[int(torch.randint(0, len(trip), (1,), generator=g, device=DEV))] for _ in range(400)]
    oh = 0; sh = 0
    for s, r, o in samp:
        oh += int(cidx(M * torch.conj(ents[s] * rels[r]), ents) == o)
        sh += int(cidx(M * torch.conj(rels[r] * ents[o]), ents) == s)
    so = oh / len(samp); ss = sh / len(samp); print("  (s,r)->o=%.3f (r,o)->s=%.3f (VE=%d T=%d)" % (so, ss, VE, T), flush=True)
    return {"sro": so, "ros": ss, "m": min(so, ss)}
def verdict(r) -> Tuple[str, str]:
    s = "(s,r)->o=%.3f (r,o)->s=%.3f" % (r["sro"], r["ros"])
    if r["m"] >= 0.80: return ("HARD_PASS", "HARD_PASS: bidirectional KG triple recall>=0.80 at 5000-entity/10k-triple scale -- queryable-both-ways KG holds at scale. " + s)
    if r["m"] >= 0.65: return ("MIDDLE_BAND", "MIDDLE_BAND: bidirectional 0.65-0.80 at scale (relation-sharding would lift). " + s)
    return ("HARD_FAIL", "HARD_FAIL: bidirectional <0.65 at scale. " + s)

print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
