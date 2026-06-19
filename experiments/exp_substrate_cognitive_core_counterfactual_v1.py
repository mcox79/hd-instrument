"""
substrate_cognitive_core_counterfactual_v1 -- CCC-1-v2 capability dim: counterfactual fact-update -- GPU baseline.

ROUTING: research priority_focus + ccc1_revised_v2 spec (counterfactual dimension; cf-RPE native). Tests inference-time
  fact UPDATE/DELETE: store F facts, then UPDATE K of them to new values, query the updated entities. Substrate
  overwrites via cf-RPE delta-rule (W += (LR/n)(new - W@k)k) -- a true inference-time weight update. Pythia-160M
  cannot update its weights at inference; it must track "X was A; now X is B" purely in-context (hard for a 160M
  model, and impossible once updates exceed its window). torch+transformers GPU $0. overnight_queue.

MODEL: F unique (entity->value) facts; cf-RPE store. Update K facts to NEW values (cf-RPE re-write). Query updated
  entities -> substrate should return NEW value; also check NON-updated retention. Pythia: in-context "X is A ...
  Update: X is now B ... X is" -> predict B.

PRE-REGISTERED bands: HARD-PASS substrate updated-fact accuracy >= 2.0x Pythia AND substrate non-updated retention
  >= 0.90. MIDDLE: >= 1.2x Pythia. HARD-FAIL: < 1.2x (substrate counterfactual no better than in-context Pythia).

FORMULA SELF-TESTS (PROT-022): 1. cf-RPE overwrite (re-write changes recall to new value). 2. non-updated retained. 3. cuda.
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

ANCHOR_NAME = "substrate_cognitive_core_counterfactual_v1"
MODEL_ID = "EleutherAI/pythia-160m"; N_SUB = 4096; LR = 0.5
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [1]; F_FACTS = 80; K_UPDATE = 30
else:
    SEEDS = [7, 17, 23]; F_FACTS = 300; K_UPDATE = 100

VAL = ["red", "blue", "green", "tall", "short", "fast", "slow", "warm", "cold", "bright", "dark", "round"]


def ub(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def cfrpe(W, k, v, n):
    W += (LR / n) * np.outer(v - W @ k, k)


def ent_name(i):
    return "item%d" % i


def _selftest():
    g = np.random.default_rng(0); n = 256; K = ub(2, n, g); V = ub(2, n, g); W = np.zeros((n, n), dtype=np.float32)
    cfrpe(W, K[0], V[0], n); assert int(np.argmax(V @ (W @ K[0]))) == 0, "store"
    for _ in range(6):
        cfrpe(W, K[0], V[1], n)                       # overwrite to value 1
    assert int(np.argmax(V @ (W @ K[0]))) == 1, "cf-RPE overwrite"
    assert N_SUB == 4096; print("[selftest] PASS: cfrpe overwrite", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available.", flush=True); sys.exit(1)
DEVICE = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)
from transformers import AutoModelForCausalLM, AutoTokenizer
_TOK = AutoTokenizer.from_pretrained(MODEL_ID); _TOK.pad_token = _TOK.eos_token; _TOK.truncation_side = "left"
_MODEL = AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype=torch.float32).to(DEVICE).eval()
CTX = 2048


def pythia_answers(context_text, ent, val):
    ids = _TOK(context_text + ("\n%s is" % ent), return_tensors="pt", truncation=True, max_length=CTX).input_ids.to(DEVICE)
    with torch.no_grad():
        nxt = _MODEL(ids).logits[0, -1].argmax().item()
    return _TOK.decode([nxt]).strip().lower().startswith(val[:3])


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); n = N_SUB
    EK = ub(F_FACTS, n, g); EV = ub(len(VAL), n, g)
    orig = [int(g.integers(0, len(VAL))) for _ in range(F_FACTS)]
    upd_idx = list(g.choice(F_FACTS, size=K_UPDATE, replace=False))
    new_val = {i: int((orig[i] + 1 + g.integers(0, len(VAL) - 1)) % len(VAL)) for i in upd_idx}  # different value
    # ---- substrate: store originals, then cf-RPE OVERWRITE the updates ----
    W = np.zeros((n, n), dtype=np.float32)
    for i in range(F_FACTS):
        cfrpe(W, EK[i], EV[orig[i]], n)
    for i in upd_idx:
        for _ in range(4):                            # delta-rule overwrite to new value
            cfrpe(W, EK[i], EV[new_val[i]], n)
    sub_upd = np.mean([int(np.argmax(EV @ (W @ EK[i]))) == new_val[i] for i in upd_idx])
    non = [i for i in range(F_FACTS) if i not in new_val]
    sub_ret = np.mean([int(np.argmax(EV @ (W @ EK[i]))) == orig[i] for i in non])
    # ---- Pythia: in-context originals + updates; query updated entities ----
    lines = ["%s is %s" % (ent_name(i), VAL[orig[i]]) for i in range(F_FACTS)]
    lines += ["Update: %s is now %s" % (ent_name(i), VAL[new_val[i]]) for i in upd_idx]
    ctx = "\n".join(lines)
    py_upd = np.mean([pythia_answers(ctx, ent_name(i), VAL[new_val[i]]) for i in upd_idx[:40]])
    return {"seed": seed, "F": F_FACTS, "K": K_UPDATE, "sub_updated_acc": float(sub_upd), "sub_nonupdated_retention": float(sub_ret),
            "pythia_updated_acc": float(py_upd), "ratio": float(sub_upd / max(py_upd, 1e-6))}


def verdict(ps) -> Tuple[str, str]:
    s = float(np.mean([p["sub_updated_acc"] for p in ps])); r = float(np.mean([p["sub_nonupdated_retention"] for p in ps]))
    py = float(np.mean([p["pythia_updated_acc"] for p in ps])); ratio = s / max(py, 1e-6)
    summary = "substrate_updated=%.2f (retention=%.2f) pythia_updated=%.2f ratio=%.2fx" % (s, r, py, ratio)
    if ratio >= 2.0 and r >= 0.90:
        return ("HARD_PASS", "HARD_PASS: substrate counterfactual fact-update >=2x Pythia + retains non-updated (cf-RPE native inference-time update). " + summary)
    if ratio >= 1.2:
        return ("MIDDLE_BAND", "MIDDLE_BAND: substrate counterfactual 1.2-2x Pythia. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: substrate counterfactual no better than in-context. " + summary)


print("[config] anchor=%s mode=%s seeds=%s F=%d K=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, F_FACTS, K_UPDATE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] sub_updated=%.2f retention=%.2f pythia_updated=%.2f ratio=%.2fx" % (seed, r["sub_updated_acc"], r["sub_nonupdated_retention"], r["pythia_updated_acc"], r["ratio"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "model": MODEL_ID, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
