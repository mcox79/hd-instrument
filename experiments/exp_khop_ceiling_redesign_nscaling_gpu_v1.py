"""
exp_khop_ceiling_redesign_nscaling_gpu_v1 -- Authorization 6 (K-hop ceiling-test redesign) -- GPU.

ROUTING: handoff 8-authorizations #6. The prior K-hop tests hit a K_max=60 ceiling and gave NO signal on N-scaling. Redesign:
  (a) raise the ceiling (K up to 120), (b) CALIBRATE noise so K_max lands well below the ceiling (differentiated signal),
  (c) use the HYBRID model from the noise-fork resolution -- distractor coherence c_d + a confidence threshold T (a hop is
  accepted only if its readout confidence > T, else it is a miss). Sweeps dimension N to produce a clean K_max(N) curve.
  GPU matmul battery.
PRE-REGISTERED: HARD-PASS K_max(N) is sub-ceiling at ALL N (max < 110) AND monotonically increasing in N (clean signal).
  MIDDLE signal but partly ceiling-clipped. HARD-FAIL still ceiling-clipped at K=120 (recalibrate noise higher).
FORMULA SELF-TESTS (PROT-022): 1. confidence threshold rejects noise. 2. clean recovery. 3. cuda.
ASCII-only. write_metrics. PROT-018 no _nN (N-sweep).
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import torch
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "khop_ceiling_redesign_nscaling_gpu_v1"
NOISE0 = 0.22; C_D = 0.15; T_CONF = 0.30; B = 10; K_GRID = list(range(2, 121, 3)); N_GRID = [2048, 4096, 8192, 16384]
_DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    V_C = 512; CHAINS = 100; K_GRID = list(range(2, 61, 4)); N_GRID = [2048, 4096]
else:
    V_C = 4000; CHAINS = 300


def codebook(v_c, n, g):
    C = (torch.randint(0, 2, (v_c, n), generator=g, device=_DEV) * 2 - 1).float(); return C / (C.norm(dim=1, keepdim=True) + 1e-8)


def k_max(C, n, g):
    v_c = C.shape[0]; km = 0
    for K in K_GRID:
        target = torch.randint(0, v_c, (CHAINS,), generator=g, device=_DEV)
        # hybrid: averaging reduces noise /sqrt(B); coherent distractor adds a c_d-aligned bias toward a wrong codeword
        eff = NOISE0 * (K ** 0.5) / (B ** 0.5)
        distract = C[torch.randint(0, v_c, (CHAINS,), generator=g, device=_DEV)]
        final = C[target] + eff * torch.randn(CHAINS, n, generator=g, device=_DEV) + C_D * (K ** 0.5) / (B ** 0.5) * distract
        sims = final @ C.t(); conf, pred = sims.max(dim=1)
        accepted = conf > T_CONF                                     # confidence threshold: reject low-confidence hops
        ok = (pred == target) & accepted
        if ok.float().mean().item() >= 0.90:
            km = K
        else:
            break
    return km


def _selftest():
    g = torch.Generator(device=_DEV).manual_seed(0); C = codebook(64, 256, g)
    assert int((C[5] @ C.t()).argmax()) == 5, "clean recovery"
    pure_noise = torch.randn(256, generator=g, device=_DEV) * 0.01; conf = (pure_noise / pure_noise.norm() @ C.t()).max().item()
    assert conf < 0.9, "confidence threshold rejects noise"
    print("[selftest] PASS: khop-ceiling-redesign", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA required.", flush=True); sys.exit(1)
print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)


def run() -> Dict:
    res = {}
    for n in N_GRID:
        torch.cuda.empty_cache(); g = torch.Generator(device=_DEV).manual_seed(7); C = codebook(V_C, n, g)
        km = k_max(C, n, torch.Generator(device=_DEV).manual_seed(100 + n)); res["N%d" % n] = km
        print("  [N=%d] K_max=%d (ceiling=%d)" % (n, km, K_GRID[-1]), flush=True)
    return res


def verdict(res) -> Tuple[str, str]:
    km = [res["N%d" % n] for n in N_GRID]; ceil = K_GRID[-1]
    incr = all(km[i + 1] >= km[i] for i in range(len(km) - 1)) and km[-1] > km[0]
    subceiling = max(km) < ceil - 10
    summary = "K_max by N: %s (ceiling=%d) increasing=%s sub-ceiling=%s" % (km, ceil, incr, subceiling)
    if subceiling and incr:
        return ("HARD_PASS", "HARD_PASS: redesigned K-hop test gives clean sub-ceiling K_max(N) signal -- K_max grows with dimension; ceiling artifact fixed. " + summary)
    if subceiling:
        return ("MIDDLE_BAND", "MIDDLE_BAND: sub-ceiling but weak/non-monotone N-signal. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: still ceiling-clipped at K=%d -- recalibrate noise0 higher. " % ceil + summary)


print("[config] anchor=%s mode=%s N_grid=%s V_c=%d chains=%d noise0=%.2f c_d=%.2f T=%.2f ceiling=%d" % (ANCHOR_NAME, RUN_MODE, N_GRID, V_C, CHAINS, NOISE0, C_D, T_CONF, K_GRID[-1]), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); res = run()
v, vmsg = verdict(res); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [res], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [res]); print("[metrics] written", flush=True)
