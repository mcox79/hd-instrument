"""
exp_two_vector_scaling_law_gpu_v1.py -- production two-vector index scaling law: how far can the substrate grow? (N=1024, GPU) -- GPU.

ROUTING: the alpha-plateau cell (v3) showed the two-vector composite is robust to the mixing weight, and that ONLY the
  structural-recall (upper) edge moves with atom crowding. The production-roadmap question is then: at the SHIPPED config
  (alpha=0.5, N=1024), how many atoms can the index hold before identity retrieval or structural recall degrades? Fix
  alpha=0.5, sweep substrate scale n_atoms (classes grow with it, ~40 atoms/class) and measure both objectives. Find the
  capacity where identity_prec@1 drops below 0.90 -- the index's identity capacity at N=1024. Substrate is currently ~1742
  atoms; this quantifies headroom for ingestion. NO LLM; substrate-physics of the PRODUCTION index. Real float32 HRR.

PRE-REGISTERED: HARD-PASS identity_prec@1 >= 0.90 AND struct_recall@5 >= 0.90 at n_atoms >= 8000 (>=4x the current ~1742) --
  ample ingestion headroom at N=1024. MIDDLE: holds to 4000-8000 (2-4x). HARD-FAIL: degrades below 4000 (<2.3x current; the
  index would need a larger N before much more ingestion). UNKNOWN if CUDA absent.
ASCII-only. write_metrics. PROT-018/PROT-020 (import torch). GPU. Route via overnight_queue.
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
from typing import Dict, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "two_vector_scaling_law_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
SIZES = [500, 2400] if SMOKE else [500, 1000, 1742, 2400, 4000, 8000, 16000, 32000]   # 1742 = current substrate atom count
ALPHA = 0.5   # production shipped weight
PER = 40      # atoms per structural class (classes grow with n_atoms)


def _selftest():
    import numpy as _n
    g = _n.random.default_rng(0); d = 128
    x = g.standard_normal((5, d)); xn = x / ((x ** 2).sum(1, keepdims=True) ** 0.5)
    assert abs(float((xn ** 2).sum(1).mean()) - 1.0) < 1e-5, "L2 norm"
    print("[selftest] PASS: two_vector_scaling_law_gpu_v1", flush=True)


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


def _norm(X):
    return X / (X.norm(dim=-1, keepdim=True) + 1e-9)


def _measure(n_atoms, N, g):
    C = max(2, n_atoms // PER)
    class_base = torch.randn(C, N, generator=g, device=DEV)
    cls = torch.arange(C, device=DEV).repeat_interleave(PER)[:n_atoms]
    if cls.numel() < n_atoms:  # pad last class
        cls = torch.cat([cls, cls.new_full((n_atoms - cls.numel(),), C - 1)])
    algebra = _norm(class_base[cls] + 0.06 * torch.randn(n_atoms, N, generator=g, device=DEV))
    name = _norm(torch.randn(n_atoms, N, generator=g, device=DEV))
    id_query = _norm(name + 0.6 * _norm(torch.randn(n_atoms, N, generator=g, device=DEV)))
    comp = _norm(algebra + ALPHA * name)
    idx = torch.arange(n_atoms, device=DEV)
    # identity precision@1 (chunked argmax to bound memory at large n)
    id_hit = 0; CH = 4096
    for s in range(0, n_atoms, CH):
        sims = id_query[s:s + CH] @ comp.T
        id_hit += int((sims.argmax(1) == idx[s:s + CH]).sum())
    id_prec = id_hit / n_atoms
    # structural recall@5 (sample up to 2000 query atoms for speed at large n)
    qn = min(2000, n_atoms); qi = torch.randperm(n_atoms, generator=g, device=DEV)[:qn]
    st = algebra[qi] @ comp.T
    st[torch.arange(qn, device=DEV), qi] = -1e9
    top5 = st.topk(5, dim=1).indices
    st_rec = float((cls[top5] == cls[qi].unsqueeze(1)).float().mean())
    return round(id_prec, 4), round(st_rec, 4), C


def run() -> Dict:
    g = torch.Generator(device=DEV).manual_seed(1028); N = 1024
    rows = []
    for n in SIZES:
        idp, srr, C = _measure(n, N, g)
        rows.append({"n_atoms": n, "C": C, "id_prec": idp, "struct_rec": srr})
        print("  n_atoms=%6d (C=%4d)  identity_prec@1=%.4f  struct_recall@5=%.4f" % (n, C, idp, srr), flush=True)
    ok = [r["n_atoms"] for r in rows if r["id_prec"] >= 0.90 and r["struct_rec"] >= 0.90]
    cap = max(ok) if ok else 0
    print("  [capacity] both>=0.90 holds up to n_atoms=%d (N=%d, alpha=%.1f); current substrate ~1742 -> headroom %.1fx" %
          (cap, N, ALPHA, cap / 1742.0), flush=True)
    return {"rows": rows, "capacity": cap, "N": N, "alpha": ALPHA, "headroom_x": round(cap / 1742.0, 2)}


def verdict(r) -> Tuple[str, str]:
    cap = r["capacity"]; hx = r["headroom_x"]
    s = "capacity(both>=0.90)=%d atoms at N=%d alpha=%.1f -> %.1fx the current ~1742; curve=%s" % (
        cap, r["N"], r["alpha"], hx, [(x["n_atoms"], x["id_prec"], x["struct_rec"]) for x in r["rows"]])
    if cap >= 8000:
        return ("HARD_PASS", "HARD_PASS: the production two-vector index at N=1024/alpha=0.5 holds identity+structure to >=8000 atoms (>=4x the current substrate) -- ample ingestion headroom; no index change needed for substantial growth. " + s)
    if cap >= 4000:
        return ("MIDDLE_BAND", "MIDDLE_BAND: index holds to 4000-8000 atoms (2-4x current) -- moderate headroom; plan an N bump before very large ingestion. " + s)
    return ("HARD_FAIL", "HARD_FAIL: index degrades below 4000 atoms (<2.3x current) -- N=1024 is near its limit; raise N before much more ingestion. " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
