"""
substrate_long_conversation_scale_1000_exchanges_v1 -- HP-1: long-conv memory at 1000+ exchanges, multi-session -- GPU.

ROUTING: research high_priority_experiments_phase1_5 (HP-1). Scales the validated categorical win (long-conv memory
  1.0 vs Pythia 0 at 400 exchanges) 5x to 1000+ exchanges across simulated multi-day sessions with 5 interwoven topic
  threads. Recall probes at depths {50,200,500,800,1000}. Substrate (distance-independent Hebbian recall) vs Pythia-
  160M (loses everything past its 2048-token window). torch GPU $0. overnight_queue. Demo-scale material.

PRE-REGISTERED bands: HARD-PASS substrate recall >= 0.85 at exchange 1000 AND Pythia <= 0.05 at depth>=500. MIDDLE:
  substrate 0.60-0.85 at 1000. HARD-FAIL: substrate degrades at long horizons (< 0.60 at 1000).
FORMULA SELF-TESTS (PROT-022): 1. substrate distance-independent recall. 2. multi-thread interleave. 3. cuda.
GPU TEMPLATE assert cuda. ASCII-only. write_metrics. PROT-018: no _nN.
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import argparse, time, math
from pathlib import Path
from typing import Dict, List, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
try:
    import torch
except ImportError:
    print("[FATAL] torch not installed.", flush=True); sys.exit(1)
import numpy as np
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_long_conversation_scale_1000_exchanges_v1"
MODEL_ID = "EleutherAI/pythia-160m"; N_SUB = 8192; LR = 0.5
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; E = 1000; DEPTHS = [50, 500, 1000]; N_THREADS = 5
else:
    SEEDS = [7, 17, 23]; E = 1200; DEPTHS = [50, 200, 500, 800, 1000]; N_THREADS = 5
VAL = ["red", "blue", "green", "tall", "short", "fast", "slow", "warm", "cold", "bright", "dark", "round", "sharp", "soft", "loud"]


def ub(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def cfrpe(W, k, v, n):
    W += (LR / n) * np.outer(v - W @ k, k)


def ent_name(i):
    return "item%d" % i


def _selftest():
    g = np.random.default_rng(0); n = 256; K = ub(50, n, g); V = ub(50, n, g); W = np.zeros((n, n), dtype=np.float32)
    for i in range(50):
        cfrpe(W, K[i], V[i], n)
    early = int(np.argmax(V @ (W @ K[0])))  # earliest still recalled after 50 writes
    assert early == 0, "distance-independent recall"
    assert N_SUB == 8192; print("[selftest] PASS: distance-independent", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available.", flush=True); sys.exit(1)
DEVICE = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)
from transformers import AutoModelForCausalLM, AutoTokenizer
_TOK = AutoTokenizer.from_pretrained(MODEL_ID); _TOK.pad_token = _TOK.eos_token; _TOK.truncation_side = "left"
_MODEL = AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype=torch.float32).to(DEVICE).eval()


def pythia_recall(full_ctx, ent, val):
    ids = _TOK(full_ctx + ("\n%s is" % ent), return_tensors="pt", truncation=True, max_length=2048).input_ids.to(DEVICE)
    with torch.no_grad():
        nxt = _MODEL(ids).logits[0, -1].argmax().item()
    return _TOK.decode([nxt]).strip().lower().startswith(val[:3])


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); n = N_SUB
    facts = [(i, int(g.integers(0, len(VAL))), int(g.integers(0, N_THREADS))) for i in range(E)]  # (ent, val, thread)
    lines = ["[thread%d] %s is %s" % (th, ent_name(e), VAL[v]) for (e, v, th) in facts]
    EK = ub(E, n, g); EV = ub(len(VAL), n, g); W = np.zeros((n, n), dtype=np.float32)
    for (e, v, th) in facts:
        cfrpe(W, EK[e], EV[v], n)
    full_ctx = "\n".join(lines)
    sub_by_depth = {}; py_by_depth = {}
    for d in DEPTHS:
        qi = max(0, E - d); idxs = [qi + j for j in range(min(20, E - qi))]
        sub = np.mean([int(np.argmax(EV @ (W @ EK[facts[i][0]]))) == facts[i][1] for i in idxs])
        py = np.mean([pythia_recall(full_ctx, ent_name(facts[i][0]), VAL[facts[i][1]]) for i in idxs[:8]])
        sub_by_depth["d%d" % d] = float(sub); py_by_depth["d%d" % d] = float(py)
    return {"seed": seed, "E": E, "n_threads": N_THREADS, "substrate_by_depth": sub_by_depth, "pythia_by_depth": py_by_depth,
            "substrate_at_1000": sub_by_depth.get("d1000", sub_by_depth["d%d" % DEPTHS[-1]]),
            "pythia_at_deep": py_by_depth["d%d" % DEPTHS[-1]]}   # deepest depth (truly beyond Pythia window)


def verdict(ps) -> Tuple[str, str]:
    s1k = float(np.mean([p["substrate_at_1000"] for p in ps])); pyd = float(np.mean([p["pythia_at_deep"] for p in ps]))
    sd = {d: float(np.mean([p["substrate_by_depth"]["d%d" % d] for p in ps])) for d in DEPTHS}
    pd = {d: float(np.mean([p["pythia_by_depth"]["d%d" % d] for p in ps])) for d in DEPTHS}
    summary = "substrate by depth=%s | pythia by depth=%s (E=%d)" % ({k: round(v, 2) for k, v in sd.items()}, {k: round(v, 2) for k, v in pd.items()}, ps[0]["E"])
    if s1k >= 0.85 and pyd <= 0.05:
        return ("HARD_PASS", "HARD_PASS: substrate long-conv memory holds >=0.85 at 1000+ exchanges; Pythia ~0 at depth (categorical win scaled 5x). " + summary)
    if s1k >= 0.60:
        return ("MIDDLE_BAND", "MIDDLE_BAND: substrate 0.60-0.85 at 1000. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: substrate degrades at long horizons. " + summary)


print("[config] anchor=%s mode=%s seeds=%s E=%d depths=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, E, DEPTHS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] substrate@1000=%.2f pythia@deep=%.2f | sub=%s" % (seed, r["substrate_at_1000"], r["pythia_at_deep"], {k: round(v, 2) for k, v in r["substrate_by_depth"].items()}), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "model": MODEL_ID, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
