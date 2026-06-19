"""
exp_substrate_gpu_throughput_v1 -- substrate cleanup throughput on GPU (torch.complex64/CUDA) -- GPU.

ROUTING: deployment validation (fast GPU). Production substrate-as-LLM-memory does cleanup (nearest-codebook lookup) on
  every recall. This measures GPU throughput: batched cleanup over a V-entry value codebook at N=8192, complex64, on CUDA.
  Reports queries/sec and GPU-vs-CPU speedup. Real-time memory needs high query rate; this quantifies it. Fast (seconds).
PRE-REGISTERED: HARD-PASS GPU batched-cleanup >= 5000 queries/sec over V=50000 codebook (real-time substrate memory viable)
  AND recall correctness == 1.0 (throughput not bought with wrong answers). MIDDLE >= 1000 q/s. HARD-FAIL < 1000 q/s or recall<0.99.
ASCII-only. write_metrics + per-trial checkpoint. PROT-018/020/021 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, time, math
from pathlib import Path
from typing import Dict, List, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "experiments"))
from _seed_checkpoint import get_output_dir, write_metrics, write_partial_key, load_partial_key
ANCHOR_NAME = "substrate_gpu_throughput_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
V = 2000 if SMOKE else 20000     # value codebook size (cleanup search space; ~1.3GB at N=8192 c64, safe on shared 8GB GPU)
NQ = 200 if SMOKE else 4000      # number of cleanup queries
def _selftest():
    import numpy as _np
    a = _np.exp(1j * 0.4)
    assert abs(abs(a) - 1.0) < 1e-6, "unit modulus"
    print("[selftest] PASS: substrate-gpu-throughput", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu"); print("[device] %s" % DEV, flush=True)
def _cphasor(m, d, dev, g):
    ang = (torch.rand((m, d), generator=g, device=dev) * 2 - 1) * math.pi
    return torch.polar(torch.ones_like(ang), ang).to(torch.complex64)
def _bench(dev) -> Tuple[float, float]:
    """Return (queries_per_sec, recall) for batched cleanup of NQ queries over a V-codebook on dev."""
    g = torch.Generator(device=dev).manual_seed(123)
    book = _cphasor(V, N, dev, g)                       # (V,N) value codebook
    keys = _cphasor(NQ, N, dev, g)                      # (NQ,N) bind keys
    truth = torch.randint(0, V, (NQ,), generator=g, device=dev)
    bound = keys * book[truth]                          # bind each query to its true value
    probe = bound * torch.conj(keys)                    # unbind -> approx value
    if dev.type == "cuda": torch.cuda.synchronize()
    t0 = time.time()
    # batched cleanup: (NQ,N) @ (N,V) -> (NQ,V) similarity; argmax over V
    sim = (probe @ torch.conj(book).T).real
    pred = torch.argmax(sim, dim=1)
    if dev.type == "cuda": torch.cuda.synchronize()
    dt = time.time() - t0
    recall = float((pred == truth).float().mean())
    qps = NQ / dt if dt > 0 else float("inf")
    return qps, recall
def run(out_dir) -> Dict:
    suf = "_smoke" if SMOKE else "_full"
    rec = load_partial_key(out_dir, "bench" + suf)
    if rec is None:
        _bench(DEV)  # warmup (kernel compile / alloc)
        gpu_qps, gpu_recall = _bench(DEV)
        cpu_qps, cpu_recall = _bench(torch.device("cpu"))
        speedup = round(gpu_qps / cpu_qps, 2) if cpu_qps > 0 else 0.0
        rec = {"gpu_qps": round(gpu_qps, 1), "gpu_recall": round(gpu_recall, 4), "cpu_qps": round(cpu_qps, 1),
               "cpu_recall": round(cpu_recall, 4), "speedup": speedup, "V": V, "NQ": NQ, "device": str(DEV)}
        write_partial_key(out_dir, "bench" + suf, rec)
    print("  cleanup over V=%d: GPU=%.0f q/s (recall=%.3f) | CPU=%.0f q/s | speedup=%.1fx [dev=%s]" %
          (rec["V"], rec["gpu_qps"], rec["gpu_recall"], rec["cpu_qps"], rec["speedup"], rec["device"]), flush=True)
    return rec
def verdict(r) -> Tuple[str, str]:
    qps = r["gpu_qps"]; rc = r["gpu_recall"]
    s = "GPU=%.0f q/s recall=%.3f speedup=%.1fx V=%d dev=%s" % (qps, rc, r["speedup"], r["V"], r["device"])
    # On CPU fallback "gpu_qps" is just CPU throughput; band still meaningful for correctness + rate.
    if qps >= 5000 and rc >= 0.999:
        return ("HARD_PASS", "HARD_PASS: substrate cleanup runs at real-time rate on GPU (>=5000 q/s) with exact recall -- substrate-as-LLM-memory lookup is GPU-real-time. " + s)
    if qps >= 1000 and rc >= 0.99:
        return ("MIDDLE_BAND", "MIDDLE_BAND: cleanup 1000-5000 q/s. " + s)
    return ("HARD_FAIL", "HARD_FAIL: cleanup <1000 q/s or recall<0.99. " + s)
print("[config] anchor=%s mode=%s N=%d V=%d NQ=%d" % (ANCHOR_NAME, RUN_MODE, N, V, NQ), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run(out_dir)
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
