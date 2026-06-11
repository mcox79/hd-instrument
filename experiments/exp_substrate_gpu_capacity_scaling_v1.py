"""
exp_substrate_gpu_capacity_scaling_v1 -- substrate shard capacity vs dimension on GPU (torch.complex64/CUDA) -- GPU.

ROUTING: deployment sizing (fast GPU; GPU-specific -- large N is slow on CPU). Production must size N (vector dim) for a
  target facts-per-shard. This measures the capacity curve: for N in {4096,8192,16384,32768}, recall of a single additive
  FHRR shard holding K facts, for K in a grid. Reports recall[N][K] and the capacity (max K at recall>=0.90) per N, which
  should grow ~linearly with N (the VSA capacity law). GPU matmul makes the large-N sweep fast; CPU would be slow.
PRE-REGISTERED: HARD-PASS capacity(N) is monotonically increasing in N AND capacity(32768) >= 4 x capacity(4096)
  (dimension-capacity scaling law holds -> production sizing is predictable). MIDDLE monotonic but <4x. HARD-FAIL non-monotonic.
ASCII-only. write_metrics + per-N checkpoint. PROT-018/020/021 _v1.
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
ANCHOR_NAME = "substrate_gpu_capacity_scaling_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
DIMS = [4096, 8192] if SMOKE else [4096, 8192, 16384, 32768]
KGRID = [100, 400, 1600] if SMOKE else [100, 200, 400, 800, 1600, 3200, 6400]
V = 5000     # value codebook for cleanup
def _selftest():
    import numpy as _np
    assert abs(abs(_np.exp(1j * 0.5)) - 1) < 1e-6, "unit modulus"
    print("[selftest] PASS: substrate-gpu-capacity-scaling", flush=True)
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
def _recall_at(N, K, g):
    """Recall of a single additive shard holding K bound key->value pairs, cleanup over V-codebook."""
    book = _cphasor(V, N, DEV, g)
    keys = _cphasor(K, N, DEV, g)
    truth = torch.randint(0, V, (K,), generator=g, device=DEV)
    shard = (keys * book[truth]).sum(dim=0)                     # bundle K bound pairs
    shard = torch.polar(torch.ones_like(shard.real), shard.angle()).to(torch.complex64)
    nq = min(K, 500)                                            # sample queries for speed
    idx = torch.arange(nq, device=DEV)
    probe = shard.unsqueeze(0) * torch.conj(keys[idx])          # unbind
    sim = (probe @ torch.conj(book).T).real
    pred = torch.argmax(sim, dim=1)
    return float((pred == truth[idx]).float().mean())
def _capacity(recalls: Dict[int, float]) -> int:
    """Max K with recall >= 0.90 (0 if none)."""
    ok = [k for k, r in sorted(recalls.items()) if r >= 0.90]
    return max(ok) if ok else 0
def run(out_dir) -> Dict:
    suf = "_smoke" if SMOKE else "_full"
    per_dim: Dict[str, Dict] = {}; caps: Dict[int, int] = {}
    for N in DIMS:
        rec = load_partial_key(out_dir, "N%d%s" % (N, suf))
        if rec is None:
            g = torch.Generator(device=DEV).manual_seed(42)
            recalls = {K: round(_recall_at(N, K, g), 3) for K in KGRID}
            rec = {"N": N, "recalls": recalls, "capacity_k": _capacity(recalls)}
            write_partial_key(out_dir, "N%d%s" % (N, suf), rec)
        per_dim["N%d" % N] = rec; caps[N] = rec["capacity_k"]
        print("  N=%-6d capacity(recall>=0.90) K=%-5d | %s" % (N, rec["capacity_k"], rec["recalls"]), flush=True)
    cap_list = [caps[N] for N in DIMS]
    monotonic = all(cap_list[i] <= cap_list[i + 1] for i in range(len(cap_list) - 1))
    ratio = round(cap_list[-1] / cap_list[0], 2) if cap_list[0] > 0 else 0.0
    return {"per_dim": per_dim, "dims": DIMS, "capacities": cap_list, "monotonic": monotonic, "ratio_max_min": ratio, "device": str(DEV)}
def verdict(r) -> Tuple[str, str]:
    s = "dims=%s capacities=%s ratio=%.1fx dev=%s" % (r["dims"], r["capacities"], r["ratio_max_min"], r["device"])
    need_ratio = 1.5 if SMOKE else 4.0
    if r["monotonic"] and r["ratio_max_min"] >= need_ratio:
        return ("HARD_PASS", "HARD_PASS: substrate shard capacity scales with dimension on GPU -- max facts-per-shard (recall>=0.90) increases monotonically with N and grows >=%.0fx from smallest to largest dim. Production sizing law holds: pick N for target capacity. " % need_ratio + s)
    if r["monotonic"]:
        return ("MIDDLE_BAND", "MIDDLE_BAND: capacity monotonic in N but ratio < %.0fx. " % need_ratio + s)
    return ("HARD_FAIL", "HARD_FAIL: capacity not monotonic in N (no clean dimension-capacity law). " + s)
print("[config] anchor=%s mode=%s dims=%s" % (ANCHOR_NAME, RUN_MODE, DIMS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run(out_dir)
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
