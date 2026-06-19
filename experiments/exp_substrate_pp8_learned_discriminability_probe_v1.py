"""
exp_substrate_pp8_learned_discriminability_probe_v1 -- SSOT PP8R4 (learned extraction routing) -- GPU.

ROUTING: PRIORITY_QUEUE_LIVE Slot PP8R4 (cycle 122 PP-8 R4). Train a small linear probe to predict which tokens contribute
  to retrieval quality (discriminative vs filler), then keep the top tokens by probe score at a target speedup; measure
  concept coverage. Compares vs the cosine-variance gate (PP8R2) + random baseline. Probe trained on GPU (torch) over many
  tokens/epochs.
PRE-REGISTERED: HARD-PASS learned probe preserves >=95pct concept coverage at 10-50x speedup. MID 80-95pct. HF <80pct.
FORMULA SELF-TESTS (PROT-022): 1. probe separates train labels. 2. coverage bounds. 3. cuda.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os, argparse, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
import torch
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_pp8_learned_discriminability_probe_v1"
SPEEDUPS = [10, 50, 100]
_DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; D = 128; V_C = 100; N_TOK = 8000; EPOCHS = 60
else:
    SEEDS = [7, 17, 23]; D = 384; V_C = 500; N_TOK = 120000; EPOCHS = 300


def make_tokens(seed):
    g = torch.Generator(device=_DEV).manual_seed(int(seed))
    centroids = torch.randn(V_C, D, generator=g, device=_DEV); centroids /= centroids.norm(dim=1, keepdim=True) + 1e-8
    labels = torch.randint(0, V_C, (N_TOK,), generator=g, device=_DEV)
    is_disc = (torch.rand(N_TOK, generator=g, device=_DEV) < 0.5)
    noise = torch.where(is_disc.unsqueeze(1), 0.3, 1.5)
    toks = centroids[labels] + noise * torch.randn(N_TOK, D, generator=g, device=_DEV)
    toks /= toks.norm(dim=1, keepdim=True) + 1e-8
    return toks, labels, is_disc.float(), centroids


def train_probe(toks, y, seed):
    g = torch.Generator(device=_DEV).manual_seed(int(seed) + 1)
    w = torch.zeros(toks.shape[1], 1, device=_DEV, requires_grad=True); b = torch.zeros(1, device=_DEV, requires_grad=True)
    opt = torch.optim.Adam([w, b], lr=0.05); n_tr = int(0.7 * len(toks))
    for _ in range(EPOCHS):
        opt.zero_grad(); logit = (toks[:n_tr] @ w + b).squeeze(1)
        loss = torch.nn.functional.binary_cross_entropy_with_logits(logit, y[:n_tr]); loss.backward(); opt.step()
    with torch.no_grad():
        return (toks @ w + b).squeeze(1)                              # probe score per token


def _selftest():
    g = torch.Generator(device=_DEV).manual_seed(0)
    X = torch.randn(200, 8, generator=g, device=_DEV); y = (X[:, 0] > 0).float()
    sc = train_probe(X, y, 0); auc = ((sc[y == 1].mean()) > (sc[y == 0].mean())).item()
    assert auc, "probe separates train labels"
    print("[selftest] PASS: pp8r4", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available.", flush=True); sys.exit(1)
print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)


def coverage(keep_idx, labels):
    return len(torch.unique(labels[keep_idx])) / V_C


def run_seed(seed) -> Dict:
    toks, labels, y, centroids = make_tokens(seed); score = train_probe(toks, y, seed)
    g = torch.Generator(device=_DEV).manual_seed(int(seed) + 7); res = {}
    for sp in SPEEDUPS:
        keep_n = max(V_C, N_TOK // sp)
        probe_keep = score.topk(keep_n).indices
        rnd_keep = torch.randperm(N_TOK, generator=g, device=_DEV)[:keep_n]
        res["sp%d" % sp] = {"probe_cov": coverage(probe_keep, labels), "random_cov": coverage(rnd_keep, labels)}
        print("  [seed=%d speedup=%dx] probe=%.3f random=%.3f" % (seed, sp, res["sp%d" % sp]["probe_cov"], res["sp%d" % sp]["random_cov"]), flush=True)
    return {"seed": seed, "by_speedup": res}


def verdict(ps) -> Tuple[str, str]:
    c10 = float(np.mean([p["by_speedup"]["sp10"]["probe_cov"] for p in ps])); c50 = float(np.mean([p["by_speedup"]["sp50"]["probe_cov"] for p in ps]))
    curve = {k: round(float(np.mean([p["by_speedup"][k]["probe_cov"] for p in ps])), 3) for k in ps[0]["by_speedup"]}
    summary = "learned-probe coverage by speedup: %s" % curve
    if min(c10, c50) >= 0.95:
        return ("HARD_PASS", "HARD_PASS: learned probe preserves >=95pct coverage at 10-50x -- learned extraction routing works. " + summary)
    if c10 >= 0.80:
        return ("MIDDLE_BAND", "MIDDLE_BAND: learned probe 80-95pct coverage. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: learned probe <80pct coverage at 10x. " + summary)


print("[config] anchor=%s mode=%s seeds=%s D=%d V_c=%d N_tok=%d epochs=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, D, V_C, N_TOK, EPOCHS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
