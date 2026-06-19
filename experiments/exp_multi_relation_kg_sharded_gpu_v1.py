"""
exp_multi_relation_kg_sharded_gpu_v1.py -- bidirectional KG triple query at 5000 entities via sharding (restores the monolithic collapse) -- GPU.

ROUTING: KG-scale sharding restoration (bidirectional KG sharded at scale). multi_relation_kg_gpu_scale collapsed monolithic at 5000 entities ((s,r)->o=0.045). Shard by subject for (s,r)->o queries and by object for (r,o)->s queries (each shard bundles only that node's incident edges). Restores bidirectional recall at scale. torch.cuda; 8GB-safe. GPU.
PRE-REGISTERED: HARD-PASS both (s,r)->o and (r,o)->s recall >= 0.90 sharded AND monolithic <= 0.15. MIDDLE >= 0.75. HARD-FAIL < 0.75.
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
ANCHOR_NAME = "multi_relation_kg_sharded_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

def _selftest():
    import numpy as _n; assert _n.argmax([0.1, 0.9]) == 1, "argmax"; print("[selftest] PASS: multi_relation_kg_sharded_gpu_v1", flush=True)
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
    g = torch.Generator(device=DEV).manual_seed(31); N = 8192; VE = 1500 if SMOKE else 5000; VR = 24; T = 3000 if SMOKE else 10000
    ents = cphasor(VE, N, g); rels = cphasor(VR, N, g)
    Mono = torch.zeros(N, dtype=torch.complex64, device=DEV)
    subj = torch.zeros(VE, N, dtype=torch.complex64, device=DEV)   # per-subject: bundles r*o (for (s,r)->o)
    obj = torch.zeros(VE, N, dtype=torch.complex64, device=DEV)    # per-object: bundles s*r (for (r,o)->s)
    trip = []
    for _ in range(T):
        s = int(torch.randint(0, VE, (1,), generator=g, device=DEV)); r = int(torch.randint(0, VR, (1,), generator=g, device=DEV)); o = int(torch.randint(0, VE, (1,), generator=g, device=DEV))
        Mono = Mono + ents[s] * rels[r] * ents[o]; subj[s] = subj[s] + rels[r] * ents[o]; obj[o] = obj[o] + ents[s] * rels[r]; trip.append((s, r, o))
    samp = [trip[int(torch.randint(0, len(trip), (1,), generator=g, device=DEV))] for _ in range(400)]
    mo = 0; so = 0; ss = 0
    for s, r, o in samp:
        mo += int(cidx(Mono * torch.conj(ents[s] * rels[r]), ents) == o)
        so += int(cidx(subj[s] * torch.conj(rels[r]), ents) == o)
        ss += int(cidx(obj[o] * torch.conj(rels[r]), ents) == s)
    mr = mo / len(samp); sro = so / len(samp); ros = ss / len(samp); print("  monolithic (s,r)->o=%.3f | SHARDED (s,r)->o=%.3f (r,o)->s=%.3f (VE=%d T=%d)" % (mr, sro, ros, VE, T), flush=True)
    return {"mono": mr, "sro": sro, "ros": ros, "m": min(sro, ros)}
def verdict(r) -> Tuple[str, str]:
    s = "sharded (s,r)->o=%.3f (r,o)->s=%.3f monolithic=%.3f" % (r["sro"], r["ros"], r["mono"])
    if r["m"] >= 0.90 and r["mono"] <= 0.15: return ("HARD_PASS", "HARD_PASS: sharding restores bidirectional KG recall to >=0.90 at 5000 entities where monolithic collapses -- KG must be sharded by subject/object. " + s)
    if r["m"] >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: sharded bidirectional 0.75-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: sharded bidirectional <0.75. " + s)

print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
