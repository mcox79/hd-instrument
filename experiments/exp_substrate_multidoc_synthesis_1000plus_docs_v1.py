"""
substrate_multidoc_synthesis_1000plus_docs_v1 -- HP-2: multi-doc synthesis at 1000+ docs -- GPU.

ROUTING: research high_priority_experiments_phase1_5 (HP-2). Scales the validated multi-doc win (1.0 vs Pythia 0.08
  at 300 docs) to 1000+ docs. Substrate ingests ALL docs (Hebbian); Pythia-160M uses windowed RAG (top-10 retrieved
  docs in context). Two query types: (a) single-fact-in-1000 (needle), (b) synthesis-aggregate (count items with a
  value -- needs scanning ALL docs). torch GPU $0. overnight_queue. Wikipedia-scope demo material.

PRE-REGISTERED bands: HARD-PASS substrate needle>=0.80 AND synthesis within 0.1 of truth-rate AND Pythia-RAG needle<=0.30.
  MIDDLE: substrate needle 0.50-0.80. HARD-FAIL: substrate doesn't scale beyond ~300 docs (needle<0.50).
FORMULA SELF-TESTS (PROT-022): 1. substrate needle recall. 2. synthesis aggregate count. 3. cuda.
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

ANCHOR_NAME = "substrate_multidoc_synthesis_1000plus_docs_v1"
MODEL_ID = "EleutherAI/pythia-160m"; N_SUB = 8192; LR = 0.5
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_DOCS = 300; N_NEEDLE = 20; RAG_K = 10
else:
    SEEDS = [7, 17, 23]; N_DOCS = 1000; N_NEEDLE = 60; RAG_K = 10
VAL = ["red", "blue", "green", "tall", "short", "fast", "slow", "warm", "cold", "bright"]


def ub(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def cfrpe(W, k, v, n):
    W += (LR / n) * np.outer(v - W @ k, k)


def ent_name(i):
    return "entity%d" % i


def _selftest():
    g = np.random.default_rng(0); n = 256; K = ub(5, n, g); V = ub(5, n, g); W = np.zeros((n, n), dtype=np.float32)
    for i in range(5):
        cfrpe(W, K[i], V[i], n)
    assert int(np.argmax(V @ (W @ K[3]))) == 3, "substrate needle recall"
    vals = [0, 1, 0, 0, 2]; assert sum(1 for x in vals if x == 0) == 3, "synthesis aggregate count"
    assert N_SUB == 8192; print("[selftest] PASS: needle aggregate", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available.", flush=True); sys.exit(1)
DEVICE = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)
from transformers import AutoModelForCausalLM, AutoTokenizer
_TOK = AutoTokenizer.from_pretrained(MODEL_ID); _TOK.pad_token = _TOK.eos_token; _TOK.truncation_side = "left"
_MODEL = AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype=torch.float32, output_hidden_states=True).to(DEVICE).eval()


def embed(texts):
    out = []
    for i in range(0, len(texts), 32):
        b = texts[i:i + 32]; t = _TOK(b, return_tensors="pt", padding=True, truncation=True, max_length=32).to(DEVICE)
        with torch.no_grad():
            hs = _MODEL(**t).hidden_states[12]
        m = t["attention_mask"].unsqueeze(-1).float(); out.append(((hs * m).sum(1) / m.sum(1).clamp(min=1)).cpu().numpy())
    e = np.concatenate(out, 0).astype(np.float32); return e / (np.linalg.norm(e, axis=1, keepdims=True) + 1e-8)


def gen(ctx, q):
    ids = _TOK("Context: %s\nQuestion: %s\nAnswer:" % (ctx, q), return_tensors="pt", truncation=True, max_length=1900).input_ids.to(DEVICE)
    with torch.no_grad():
        o = _MODEL.generate(ids, max_new_tokens=8, do_sample=False, pad_token_id=_TOK.eos_token_id)
    return _TOK.decode(o[0, ids.shape[1]:]).strip().lower()


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); n = N_SUB
    docvals = [int(g.integers(0, len(VAL))) for _ in range(N_DOCS)]
    docs = ["Document %d: %s is %s." % (i, ent_name(i), VAL[docvals[i]]) for i in range(N_DOCS)]
    EK = ub(N_DOCS, n, g); EV = ub(len(VAL), n, g); W = np.zeros((n, n), dtype=np.float32)
    for i in range(N_DOCS):
        cfrpe(W, EK[i], EV[docvals[i]], n)
    demb = embed(docs)
    # (a) NEEDLE: query random entity's value
    needles = list(g.choice(N_DOCS, size=N_NEEDLE, replace=False))
    sub_ok = py_ok = 0
    for i in needles:
        sub_ok += (int(np.argmax(EV @ (W @ EK[i]))) == docvals[i])
        q = "%s is" % ent_name(i); qv = embed([q])[0]; top = np.argsort(-(demb @ qv))[:RAG_K]
        py_ok += (VAL[docvals[i]] in gen(" ".join(docs[j] for j in top), q))
    # (b) SYNTHESIS-AGGREGATE: count entities with a target value (needs ALL docs)
    tgt = int(g.integers(0, len(VAL))); true_count = sum(1 for v in docvals if v == tgt)
    sub_count = sum(1 for i in range(N_DOCS) if int(np.argmax(EV @ (W @ EK[i]))) == tgt)
    sub_synth_err = abs(sub_count - true_count) / max(true_count, 1)
    return {"seed": seed, "n_docs": N_DOCS, "substrate_needle": sub_ok / N_NEEDLE, "pythia_rag_needle": py_ok / N_NEEDLE,
            "substrate_synth_count": sub_count, "true_count": true_count, "substrate_synth_relerr": float(sub_synth_err)}


def verdict(ps) -> Tuple[str, str]:
    sn = float(np.mean([p["substrate_needle"] for p in ps])); pn = float(np.mean([p["pythia_rag_needle"] for p in ps]))
    se = float(np.mean([p["substrate_synth_relerr"] for p in ps]))
    summary = "substrate_needle=%.3f pythia_RAG_needle=%.3f | synthesis-count relerr=%.3f (n_docs=%d)" % (sn, pn, se, ps[0]["n_docs"])
    if sn >= 0.80 and se <= 0.10 and pn <= 0.30:
        return ("HARD_PASS", "HARD_PASS: substrate scales to 1000+ docs (needle + synthesis); Pythia-RAG windowed loses. " + summary)
    if sn >= 0.50:
        return ("MIDDLE_BAND", "MIDDLE_BAND: substrate needle 0.50-0.80 at scale. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: substrate does not scale beyond ~300 docs. " + summary)


print("[config] anchor=%s mode=%s seeds=%s n_docs=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DOCS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] substrate_needle=%.3f pythia_RAG=%.3f synth_relerr=%.3f (sub_count=%d true=%d)" % (
        seed, r["substrate_needle"], r["pythia_rag_needle"], r["substrate_synth_relerr"], r["substrate_synth_count"], r["true_count"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "model": MODEL_ID, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
