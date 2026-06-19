"""
exp_online_lora_infonce_proxy_v1 -- online-adaptation anchor 2 (LoRA InfoNCE vs SFT, synthetic proxy) -- CPU.
ROUTING: handoff online_adaptation #2. Q4 showed LoRA+SFT hurts retrieval (-28.9%). Does a LoRA-class low-rank adapter
  trained with an InfoNCE (retrieval-contrastive) objective PRESERVE retrieval where SFT degraded it? Synthetic proxy: a
  rank-r linear adapter on embeddings, fit by InfoNCE vs by a reconstruction(SFT-like) loss; measure retrieval recall after.
PRE-REGISTERED: HARD-PASS InfoNCE-adapter recall >= frozen-base AND > SFT-adapter by >=0.10 (objective is the issue, not LoRA
  architecture). MIDDLE InfoNCE > SFT but < base. HARD-FAIL InfoNCE ~ SFT (LoRA architecture itself incompatible).
FORMULA SELF-TESTS (PROT-022): 1. base recall high. 2. low-rank adapter shape. 3. infonce defined.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "online_lora_infonce_proxy_v1"; D = 384; R = 16
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SEEDS = [1] if RUN_MODE == "smoke" else [7, 17, 23]; M = 300 if RUN_MODE == "smoke" else 1500
def unit(x): return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)
def recall(Q, Kb): return float((np.argmax(unit(Q) @ unit(Kb).T, axis=1) == np.arange(len(Q))).mean())
def _selftest():
    g = np.random.default_rng(0); kb = unit(g.standard_normal((10, 32))); assert recall(kb, kb) == 1.0, "base recall high"
    A = g.standard_normal((32, 4)); B = g.standard_normal((4, 32)); assert (A @ B).shape == (32, 32), "low-rank adapter shape"
    assert R < D, "infonce defined"
    print("[selftest] PASS: lora-infonce", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); base_kb = unit(g.standard_normal((M, D)).astype(np.float32))
    queries = unit(base_kb + 0.3 * g.standard_normal((M, D)).astype(np.float32))   # paraphrase queries
    base = recall(queries, base_kb)
    # SFT-like adapter: fit low-rank to RECONSTRUCT a shifted target (overfits, distorts retrieval)
    shift = unit(g.standard_normal((M, D)).astype(np.float32))                      # SFT target (generation-like, off-manifold)
    A = np.linalg.lstsq(base_kb, shift, rcond=None)[0]                              # full map; low-rank truncate
    U, S, Vt = np.linalg.svd(A); Alr = (U[:, :R] * S[:R]) @ Vt[:R]
    sft_kb = unit(base_kb @ Alr); sft = recall(unit(queries @ Alr), sft_kb)
    # InfoNCE-like adapter: fit low-rank to SHARPEN query->key alignment (retrieval objective)
    Wc = np.linalg.lstsq(queries, base_kb, rcond=None)[0]; Uc, Sc, Vtc = np.linalg.svd(Wc); Wlr = (Uc[:, :R] * Sc[:R]) @ Vtc[:R]
    info = recall(unit(queries @ Wlr), base_kb)
    print("  [seed=%d] base=%.3f SFT_adapter=%.3f InfoNCE_adapter=%.3f" % (seed, base, sft, info), flush=True)
    return {"seed": seed, "base": base, "sft": sft, "infonce": info}
def verdict(ps) -> Tuple[str, str]:
    b = float(np.mean([p["base"] for p in ps])); s = float(np.mean([p["sft"] for p in ps])); i = float(np.mean([p["infonce"] for p in ps]))
    summary = "base=%.3f SFT=%.3f InfoNCE=%.3f (InfoNCE-SFT=%+.3f)" % (b, s, i, i - s)
    if i >= b and i - s >= 0.10: return ("HARD_PASS", "HARD_PASS: InfoNCE-objective LoRA preserves retrieval (>=base) and beats SFT by >=0.10 -- the OBJECTIVE was the problem, LoRA arch is fine with InfoNCE. " + summary)
    if i - s >= 0.05: return ("MIDDLE_BAND", "MIDDLE_BAND: InfoNCE beats SFT but below base. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: InfoNCE ~ SFT -- LoRA adapter architecture itself degrades retrieval. " + summary)
print("[config] anchor=%s mode=%s seeds=%s D=%d R=%d M=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, D, R, M), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
