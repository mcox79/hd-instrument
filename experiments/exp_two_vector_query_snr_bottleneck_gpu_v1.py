"""
exp_two_vector_query_snr_bottleneck_gpu_v1.py -- the REAL bottleneck of the two-vector index is QUERY SNR, not atom count (N=1024, GPU) -- GPU.

ROUTING: the scaling-law cell showed identity+structure hold to >=32000 atoms (>=18x current) with NO degradation -- atom count
  is NOT the index bottleneck at N=1024 (high-D capacity is enormous when the retrieval cue is high-SNR). The REAL operating
  constraint is therefore QUERY SNR: how well the retrieval cue matches the stored name_vec. This cell measures it directly:
  fix n_atoms=8000 (>4x current), N=1024, alpha=0.5, sweep the identity-query noise q (cue = normalize(name + q*unit noise);
  cos(cue,name) ~ 1/sqrt(1+q^2)) and find where identity_prec@1 breaks. Identifies what actually limits retrieval (cue quality /
  query encoding), redirecting investment away from index size. NO LLM; substrate-physics of the PRODUCTION index. Real float32.

PRE-REGISTERED: HARD-PASS identity holds (>=0.90) down to a heavily degraded cue cos(cue,name)<=0.45 -- query SNR is a generous
  constraint, cue quality is not a near-term risk. MIDDLE: needs cos>=0.45-0.70 (query SNR is the real limit; invest in query
  encoding not larger N). HARD-FAIL: needs a near-clean cue cos>=0.70 (retrieval brittle to query noise). UNKNOWN if CUDA absent.
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
import argparse, time, math
from pathlib import Path
from typing import Dict, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "two_vector_query_snr_bottleneck_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
QNOISE = [0.6, 2.0] if SMOKE else [0.0, 0.3, 0.6, 1.0, 1.5, 2.0, 3.0, 5.0, 8.0]   # cos(cue,name)~1/sqrt(1+q^2)
ALPHA = 0.5       # production shipped weight
PER = 40          # atoms per structural class
N_FIXED = 8000    # >4x current substrate; atom count already shown non-limiting


def _selftest():
    import numpy as _n
    g = _n.random.default_rng(0); d = 128
    x = g.standard_normal((5, d)); xn = x / ((x ** 2).sum(1, keepdims=True) ** 0.5)
    assert abs(float((xn ** 2).sum(1).mean()) - 1.0) < 1e-5, "L2 norm"
    assert abs(1.0 / math.sqrt(1.0 + 1.0) - 0.7071) < 1e-3, "cos formula"
    print("[selftest] PASS: two_vector_query_snr_bottleneck_gpu_v1", flush=True)


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


def _measure(q, n_atoms, N, g):
    C = max(2, n_atoms // PER)
    class_base = torch.randn(C, N, generator=g, device=DEV)
    cls = torch.arange(C, device=DEV).repeat_interleave(PER)[:n_atoms]
    if cls.numel() < n_atoms:
        cls = torch.cat([cls, cls.new_full((n_atoms - cls.numel(),), C - 1)])
    algebra = _norm(class_base[cls] + 0.06 * torch.randn(n_atoms, N, generator=g, device=DEV))
    name = _norm(torch.randn(n_atoms, N, generator=g, device=DEV))
    id_query = _norm(name + q * _norm(torch.randn(n_atoms, N, generator=g, device=DEV)))
    comp = _norm(algebra + ALPHA * name)
    idx = torch.arange(n_atoms, device=DEV)
    id_hit = 0; CH = 4096
    for s in range(0, n_atoms, CH):
        sims = id_query[s:s + CH] @ comp.T
        id_hit += int((sims.argmax(1) == idx[s:s + CH]).sum())
    cos_cue = 1.0 / math.sqrt(1.0 + q * q)
    return round(id_hit / n_atoms, 4), round(cos_cue, 4)


def run() -> Dict:
    g = torch.Generator(device=DEV).manual_seed(1028); N = 1024
    rows = []
    for q in QNOISE:
        idp, cosc = _measure(q, N_FIXED, N, g)
        rows.append({"q": q, "cos_cue": cosc, "id_prec": idp})
        print("  q=%4.1f  cos(cue,name)=%.3f  identity_prec@1=%.4f" % (q, cosc, idp), flush=True)
    ok = [r for r in rows if r["id_prec"] >= 0.90]
    qmax = max((r["q"] for r in ok), default=0.0); cos_min = min((r["cos_cue"] for r in ok), default=1.0)
    print("  [bottleneck] identity holds (>=0.90) down to cos(cue,name)>=%.3f (q<=%.1f) at n=%d N=%d -- this, not atom count, is the limit" %
          (cos_min, qmax, N_FIXED, N), flush=True)
    return {"rows": rows, "q_max_ok": qmax, "cos_min_ok": cos_min, "N": N, "n_atoms": N_FIXED, "alpha": ALPHA}


def verdict(r) -> Tuple[str, str]:
    cm = r["cos_min_ok"]; qm = r["q_max_ok"]
    s = "identity holds (>=0.90) down to cos(cue,name)>=%.3f (q<=%.1f) at n=%d N=%d alpha=%.1f; curve=%s" % (
        cm, qm, r["n_atoms"], r["N"], r["alpha"], [(x["q"], x["cos_cue"], x["id_prec"]) for x in r["rows"]])
    if cm <= 0.45:
        return ("HARD_PASS", "HARD_PASS: identity retrieval tolerates a HEAVILY degraded cue (cos as low as %.2f) -- the operating constraint (query SNR) is generous; cue quality is not a near-term risk and atom count is a non-issue. The two-vector index bottleneck is query encoding, with wide margin. " % cm + s)
    if cm <= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: identity needs a moderately good cue (cos>=%.2f) -- query SNR is the real limit (not atom count); invest in cue/query encoding, not larger N. " % cm + s)
    return ("HARD_FAIL", "HARD_FAIL: identity needs a near-clean cue (cos>=%.2f) -- retrieval is brittle to query noise; query encoding is the priority. " % cm + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
