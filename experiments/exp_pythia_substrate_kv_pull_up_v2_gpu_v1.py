"""
pythia_substrate_kv_pull_up_v2_gpu_v1 -- Pythia-2.8B substrate-KV-memory pull-up (Research v2 pre-reg +
Skunkworks GO 2026-06-19). Smoke->cert pull-up of the n1/n1b/n1d 2.8B LEGACY HARD_PASS evidence.

MECHANISM (from n1_pythia2p8b_substrate_kv): Pythia last-token hidden states key an external substrate-KV
memory. encode facts -> ZCA-whiten -> store key->value(id); recall by re-encoding a NOISED query +
nearest-key argmax. recall@1 = the substrate's external-memory capacity (scales BEYOND the context window).

v2 DISCRIMINATING REGIME: fact-bank SWEEP {2k,5k,10k,25k,50k,100k} x noise sigma {0.05,0.10,0.20} x 5 seeds.
PINNED to Pythia-2.8B (1.4B = separate event). Primary capacity recall = sigma=0.05 (clean); sigma=0.10 =
robustness; sigma=0.20 = stress.

v2 BANDS (LOCKED; cliff-band FIX = no-cliff-through-100k is the STRONGER result, not MIDDLE):
  HARD_PASS = recall(10k)>=0.80 AND graceful(recall(10k)-recall(2k) <= 0.05) AND noise sigma=0.10 recall(10k)>=0.60
              AND (cliff in [10k,100k] OR recall>=0.50 through 100k) AND all 5 seeds reproduce within +-0.03.
  MIDDLE    = HP except sigma=0.10 recall in [0.40,0.60) OR non-graceful drop(2k->10k) in (0.05,0.20] (strict >0.05; no overlap w/ HP).
  HARD_FAIL = recall(10k)<0.50 OR drop(2k->10k)>0.20 OR sigma=0.10 recall<0.40 OR seeds disagree >0.05.
  honest-scope LOCKED: "Pythia 2.8B hidden states are viable substrate-KV keys; recall>=0.80 over a fact-bank
  at the MEASURED capacity boundary; noise-robust at sigma=0.10. NOT a 1.4B claim."

DISPATCH-READINESS (BLOCKING, USER directive): checkpoint per (size,seed) [write_partial_key] + DEMONSTRATE
resume (kill-restart; the smoke is local-runnable on pythia-160m) + GPU-memory pre-check (model + KV table;
recall is CHUNKED so M=100k never materializes a 100k x 100k matrix). smoke=pythia-160m (cached; local-testable),
full=pythia-2.8b (GPU). PROT-018 no _nN (model-keyed). ASCII; import torch first (PROT-020).
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"; os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_partial_key, aggregate_partials, write_metrics

ANCHOR_NAME = "pythia_substrate_kv_pull_up_v2_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
SIGMAS = [0.05, 0.10, 0.20]
RECALL_CHUNK = 2000
if SMOKE:
    MODEL = "EleutherAI/pythia-160m"; SIZES = [500, 1000]; SEEDS = [7, 17]
else:
    MODEL = "EleutherAI/pythia-2.8b"; SIZES = [2000, 5000, 10000, 25000, 50000, 100000]; SEEDS = [7, 17, 23, 31, 41]


def make_facts(m, g):
    subjects = ["alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel", "india", "juliet"]
    rels = ["was founded in", "is located near", "was invented by", "merged with", "is the capital of",
            "won the award for", "is powered by", "was discovered in"]
    return [("entity %s-%d %s what" % (subjects[i % len(subjects)], i, rels[g.integers(0, len(rels))]), i) for i in range(m)]


def whiten_fit(K):
    mu = K.mean(0); Kc = K - mu
    cov = Kc.T @ Kc / len(K) + 1e-3 * np.eye(K.shape[1], dtype=np.float32)
    w, V = np.linalg.eigh(cov); W = (V @ np.diag(1.0 / np.sqrt(w)) @ V.T).astype(np.float32)
    Kw = Kc @ W; Kw = Kw / (np.linalg.norm(Kw, axis=1, keepdims=True) + 1e-8)
    return mu, W, Kw.astype(np.float32)


def recall_chunked(Qw, Kw, gold, chunk=RECALL_CHUNK):
    """argmax nearest-key recall WITHOUT materializing M x M (handles M=100k). chunk queries."""
    correct = 0
    for i in range(0, len(Qw), chunk):
        pred = np.argmax(Qw[i:i + chunk] @ Kw.T, axis=1)
        correct += int((pred == gold[i:i + chunk]).sum())
    return correct / max(1, len(Qw))


def _selftest():
    g = np.random.default_rng(0)
    K = g.standard_normal((200, 16)).astype(np.float32)
    mu, W, Kw = whiten_fit(K)
    gold = np.arange(200)
    # zero-noise recall must be ~1.0 (each key recalls itself)
    Qw = ((K - mu) @ W); Qw = (Qw / (np.linalg.norm(Qw, axis=1, keepdims=True) + 1e-8)).astype(np.float32)
    r0 = recall_chunked(Qw, Kw, gold, chunk=64)
    assert r0 > 0.99, "zero-noise recall should be ~1.0, got %.3f" % r0
    # chunked == full
    full = float((np.argmax(Qw @ Kw.T, axis=1) == gold).mean())
    assert abs(full - r0) < 1e-9, "chunked != full"
    assert len(make_facts(5, g)) == 5
    print("[selftest] PASS: whiten + zero-noise-recall~1.0 + chunked==full + make_facts", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)

try:
    import torch
    from transformers import AutoModel, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
if torch.cuda.is_available():
    DEV = torch.device("cuda")
    print("[GPU] %s total=%.1fGB" % (torch.cuda.get_device_name(0), torch.cuda.get_device_properties(0).total_memory / 1e9), flush=True)
elif SMOKE:
    DEV = torch.device("cpu")
    print("[smoke] no CUDA -> CPU fallback (pythia-160m; for resume-demo + logic verify only)", flush=True)
else:
    print("[FATAL] CUDA required for the full Pythia-2.8B run.", flush=True); sys.exit(1)


def memory_precheck(hidden_dim):
    """GPU-memory feasibility (Skunkworks BLOCKING item): model on GPU; KV table + recall on CPU (chunked)."""
    model_gb = {"EleutherAI/pythia-2.8b": 5.6, "EleutherAI/pythia-160m": 0.4}.get(MODEL, 6.0)
    if DEV.type != "cuda":
        print("[mem-precheck] CPU smoke -> GPU feasibility check skipped (full run on GPU does it).", flush=True); return
    gpu_total = torch.cuda.get_device_properties(0).total_memory / 1e9
    max_m = max(SIZES)
    kv_cpu_gb = max_m * hidden_dim * 4 * 3 / 1e9     # K + Kw + Q (CPU numpy)
    chunk_gb = RECALL_CHUNK * max_m * 4 / 1e9        # chunked sims temp (CPU)
    print("[mem-precheck] model~%.1fGB (GPU, total %.1fGB) | KV+recall CPU ~%.1fGB + chunk-temp ~%.2fGB (M=%d, dim=%d). "
          "recall is CHUNKED -> no MxM matrix." % (model_gb, gpu_total, kv_cpu_gb, chunk_gb, max_m, hidden_dim), flush=True)
    if model_gb > gpu_total - 0.5:
        raise RuntimeError("model %.1fGB will not fit GPU %.1fGB" % (model_gb, gpu_total))


def encode(texts, tok, m):
    out = []
    for i in range(0, len(texts), 32):
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=32).to(DEV)
        with torch.no_grad():
            h = m(**t).last_hidden_state
        lens = t["attention_mask"].sum(1) - 1
        out.append(h[torch.arange(h.shape[0]), lens].float().cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32)


def run_unit(size, seed, tok, mdl):
    g = np.random.default_rng(seed)
    facts = make_facts(size, g); texts = [f[0] for f in facts]
    K = encode(texts, tok, mdl)
    mu, W, Kw = whiten_fit(K)
    gold = np.arange(size)
    rec = {}
    for sigma in SIGMAS:
        Q = K + sigma * g.standard_normal(K.shape).astype(np.float32)
        Qw = (Q - mu) @ W; Qw = (Qw / (np.linalg.norm(Qw, axis=1, keepdims=True) + 1e-8)).astype(np.float32)
        rec["%.2f" % sigma] = round(recall_chunked(Qw, Kw, gold), 4)
    print("  [size=%d seed=%d] recall: " % (size, seed) + " ".join("s%.2f=%.3f" % (s, rec["%.2f" % s]) for s in SIGMAS), flush=True)
    return {"size": size, "seed": seed, "model": MODEL, "run_mode": RUN_MODE, "recall_by_sigma": rec}


def compute_verdict(units) -> Tuple[str, str, Dict]:
    if not units:
        return ("HARD_FAIL", "no results", {})
    # mean recall per (size, sigma) across seeds + per-size std
    by = {}
    stds = {}
    for size in SIZES:
        for s in SIGMAS:
            vals = [u["recall_by_sigma"]["%.2f" % s] for u in units if u["size"] == size and "%.2f" % s in u["recall_by_sigma"]]
            if vals:
                by[(size, s)] = float(np.mean(vals)); stds[(size, s)] = float(np.std(vals))
    def R(size, s): return by.get((size, s))
    PRIMARY = 0.05  # clean-capacity sigma
    r10 = R(10000, PRIMARY); r2 = R(2000, PRIMARY); r10_n = R(10000, 0.10)
    if r10 is None or r2 is None or r10_n is None:
        return ("UNKNOWN", "missing 10k/2k measurements", {"by": {str(k): v for k, v in by.items()}})
    drop = r2 - r10  # graceful if small (recall should not DROP much from 2k to 10k)
    # cliff: smallest size>=10k where primary recall < 0.50; else no-cliff-through-100k (the stronger result)
    cliff = next((sz for sz in SIZES if sz >= 10000 and (R(sz, PRIMARY) or 0) < 0.50), None)
    no_cliff_through_max = all((R(sz, PRIMARY) or 0) >= 0.50 for sz in SIZES if sz >= 10000)
    max_std = max((stds.get((sz, PRIMARY), 0.0) for sz in SIZES), default=0.0)
    seeds_reproduce = max_std <= 0.03
    detail = {"recall_primary_s0.05": {str(sz): R(sz, PRIMARY) for sz in SIZES},
              "recall_s0.10": {str(sz): R(sz, 0.10) for sz in SIZES},
              "recall_s0.20": {str(sz): R(sz, 0.20) for sz in SIZES},
              "recall_10k_clean": r10, "recall_2k_clean": r2, "drop_2k_to_10k": round(drop, 4),
              "recall_10k_noise0.10": r10_n, "cliff_size": cliff, "no_cliff_through_100k": no_cliff_through_max,
              "max_seed_std": round(max_std, 4), "seeds_reproduce": seeds_reproduce,
              "honest_scope": "Pythia 2.8B substrate-KV; recall>=0.80 to the measured-capacity boundary; "
                              "noise-robust sigma=0.10. NOT a 1.4B claim."}
    summary = ("recall(10k,clean)=%.3f recall(2k,clean)=%.3f drop=%.3f recall(10k,s0.10)=%.3f cliff=%s "
               "no_cliff_through_100k=%s max_std=%.3f" % (r10, r2, drop, r10_n, cliff, no_cliff_through_max, max_std))
    # HARD_FAIL
    if r10 < 0.50 or drop > 0.20 or r10_n < 0.40 or max_std > 0.05:
        return ("HARD_FAIL", "HARD_FAIL: " + summary, detail)
    # HARD_PASS
    cap_ok = (cliff is not None) or no_cliff_through_max
    if r10 >= 0.80 and drop <= 0.05 and r10_n >= 0.60 and cap_ok and seeds_reproduce:
        return ("HARD_PASS", "HARD_PASS: Pythia-2.8B viable substrate-KV keys. " + summary, detail)
    # MIDDLE (strict >0.05 for non-graceful so no overlap with HP <=0.05; nit-fix)
    if (0.40 <= r10_n < 0.60) or (0.05 < drop <= 0.20):
        return ("MIDDLE_BAND", "MIDDLE_BAND: " + summary, detail)
    return ("MIDDLE_BAND", "MIDDLE_BAND (other partial): " + summary, detail)


print("[config] %s mode=%s model=%s sizes=%s sigmas=%s seeds=%s" % (ANCHOR_NAME, RUN_MODE, MODEL, SIZES, SIGMAS, SEEDS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"run_mode": RUN_MODE}
t0 = time.time()
tok = AutoTokenizer.from_pretrained(MODEL); tok.pad_token = tok.eos_token
mdl = AutoModel.from_pretrained(MODEL, torch_dtype=torch.bfloat16).to(DEV).eval()
memory_precheck(mdl.config.hidden_size)
for size in SIZES:
    for seed in SEEDS:
        key = "size%d_s%d" % (size, seed)
        if key in aggregate_partials(out_dir, [key], run_config=run_config):
            print("[ckpt] %s done; skip" % key, flush=True); continue
        res = run_unit(size, seed, tok, mdl); res["run_mode"] = RUN_MODE
        write_partial_key(out_dir, key, res)
del mdl
units = list(aggregate_partials(out_dir, ["size%d_s%d" % (sz, sd) for sz in SIZES for sd in SEEDS], run_config=run_config).values())
verdict, msg, detail = compute_verdict(units)
print("\n[VERDICT] " + msg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg, "run_mode": RUN_MODE, "model": MODEL,
           "sizes": SIZES, "sigmas": SIGMAS, "n_seeds": len(SEEDS), "detail": detail,
           "metrics_source": "measured_gpu_pythia2p8b_substrate_kv_sweep_noise", "per_unit": units,
           "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, units)
print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
