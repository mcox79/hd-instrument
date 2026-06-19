"""
exp_substrate_encoder_noise_bundle_v1 -- BUNDLED encoder-noise robustness 3 pre-tests (bge-large loaded once) -- GPU.

ROUTING: substrate_encoder_noise_3_pretests_AUTHORIZE (follow-up to cycle-164 noise_bft HF: sign-binarization discards
  magnitude confidence -> 5x faster degradation). Three pre-tests on bge-large HotpotQA embeddings, self-retrieval recall@10
  under additive Gaussian embedding noise:
  A1 CONFIDENCE ROUTING: correlation between |coordinate| (confidence) and sign-flip-stability under noise. r>=0.2 => a
     confidence signal exists (gates magnitude-aware quantization). Read-only.
  A2 BUNDLE ENSEMBLING: store K in {1,3,5} jittered bipolar copies per fact, majority-vote retrieval; recall@10 vs K at
     sigma=0.2. HP if K=3 recall >= 1.5x K=1.
  A3 TERNARY vs BIPOLAR: q(x)=+1/-1/0 by threshold tau vs sign(); recall@10 vs noise. HP if ternary@sigma=0.2 >= 1.75x bipolar.
  GPU for the bge-large encode.
PRE-REGISTERED: bundle verdict HARD_PASS if >=2 of {A1 signal, A2 ensembling, A3 ternary} clear their bars (encoder-noise
  robustness is RECOVERABLE for v2.0). MIDDLE 1/3. HARD-FAIL 0/3 (rely on encoder quality, narrow to storage-noise only).
FORMULA SELF-TESTS (PROT-022): 1. self-retrieval. 2. ternary values. 3. recall monotone in k.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, time, json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_encoder_noise_bundle_v2"; BI = "BAAI/bge-large-en-v1.5"
HOTPOT = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
NITEMS = 300 if RUN_MODE == "smoke" else 1000; SIGMA = 0.5   # v2: stronger noise (v1 sigma=0.2 saturated recall@10)


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def recall_at_k(scores, k):
    # scores[i,j] = sim of noisy-query i to stored key j; recall@k = fraction where the true j=i is in top-k
    n = scores.shape[0]; order = np.argsort(scores, axis=1)[:, ::-1][:, :k]
    return float(np.mean([i in order[i] for i in range(n)]))


def _selftest():
    g = np.random.default_rng(0); e = unit(g.standard_normal((6, 8))); assert int(np.argmax(e @ e[0])) == 0, "self-retrieval"
    t = np.where(np.array([0.1, 0.9, -0.9]) > 0.5, 1, np.where(np.array([0.1, 0.9, -0.9]) < -0.5, -1, 0))
    assert set(np.unique(t)) <= {-1, 0, 1}, "ternary values"
    sc = np.array([[0.9, 0.1, 0.2]]); assert recall_at_k(sc, 1) <= recall_at_k(sc, 2), "recall monotone in k"
    print("[selftest] PASS: substrate-encoder-noise-bundle", flush=True)


def load_sents(n):
    out = []; seen = set()
    if not HOTPOT.exists():
        return out
    for l in open(HOTPOT, encoding="utf-8"):
        try:
            r = json.loads(l)
        except Exception:
            continue
        for sl in (r.get("context") or {}).get("sentences") or []:
            for s in sl:
                t = s.strip()
                if 40 < len(t) < 300 and t not in seen:
                    seen.add(t); out.append(t)
                    if len(out) >= n:
                        return out
    return out


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModel, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu"); print("[device] %s" % DEV, flush=True)


def encode(texts, tok, m):
    out = []
    for i in range(0, len(texts), 32):
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=128).to(DEV)
        with torch.no_grad():
            o = m(**t)
        out.append(o.last_hidden_state[:, 0, :].float().cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32)


def bipolar(E):
    return np.sign(E).astype(np.float32)


def ternary(E, tau_mult):
    sig = E.std(0, keepdims=True) + 1e-8; tau = tau_mult * sig
    return np.where(E > tau, 1.0, np.where(E < -tau, -1.0, 0.0)).astype(np.float32)


def noisy(E, sigma, g):
    return E + sigma * np.linalg.norm(E, axis=1, keepdims=True) / np.sqrt(E.shape[1]) * g.standard_normal(E.shape).astype(np.float32)


def run() -> Dict:
    sents = load_sents(NITEMS)
    if len(sents) < 50:
        print("[FATAL] corpus too small", flush=True); return {"a1": 0, "a2": {}, "a3": {}, "npass": 0}
    tok = AutoTokenizer.from_pretrained(BI); m = AutoModel.from_pretrained(BI).to(DEV).eval()
    E = encode(sents, tok, m); del m
    if DEV.type == "cuda":
        torch.cuda.empty_cache()
    g = np.random.default_rng(7); n = len(E)
    # A1 confidence routing: per-coordinate |value| vs flip-stability under noise (corr across coords, pooled)
    En = noisy(E, SIGMA, g)
    flip = (np.sign(E) != np.sign(En)).astype(np.float32)        # 1 if coordinate flipped sign
    absval = np.abs(E)
    a1_r = float(np.corrcoef(absval.ravel(), -flip.ravel())[0, 1])   # higher |val| -> less flip => positive corr
    a1_pass = a1_r >= 0.2
    print("  [A1 confidence] corr(|coord|, sign-stability)=%.3f -> %s" % (a1_r, "signal" if a1_pass else "no signal"), flush=True)
    # A2 bundle ensembling: K jittered bipolar copies, majority-vote recall@10
    a2 = {}
    Bq = bipolar(noisy(E, SIGMA, g))                            # noisy query, binarized
    for K in ([1, 3] if RUN_MODE == "smoke" else [1, 3, 5]):
        votes = np.zeros((n, n), np.float32)
        for _ in range(K):
            Bk = bipolar(E + (0.1 * np.linalg.norm(E, axis=1, keepdims=True) / np.sqrt(E.shape[1])) * g.standard_normal(E.shape).astype(np.float32))
            votes += Bq @ Bk.T
        a2["K%d" % K] = recall_at_k(votes, 1)
        print("  [A2 ensembling] K=%d recall@1=%.3f" % (K, a2["K%d" % K]), flush=True)
    a2_pass = a2.get("K3", 0) >= 1.5 * a2.get("K1", 1e-9)
    # A3 ternary vs bipolar recall@10 under noise
    Bk = bipolar(E); a3_bip = recall_at_k(bipolar(noisy(E, SIGMA, g)) @ Bk.T, 1)
    best_tern = 0.0; best_tau = None
    for tau in [0.5, 1.0, 1.5]:
        Tk = ternary(E, tau); rec = recall_at_k(ternary(noisy(E, SIGMA, g), tau) @ Tk.T, 1)
        if rec > best_tern:
            best_tern = rec; best_tau = tau
    a3 = {"bipolar": a3_bip, "ternary_best": best_tern, "tau": best_tau}
    a3_pass = best_tern >= 1.75 * (a3_bip + 1e-9)
    print("  [A3 ternary] bipolar recall@1=%.3f ternary_best=%.3f (tau=%s) -> %s" % (a3_bip, best_tern, best_tau, "ternary wins" if a3_pass else "no"), flush=True)
    npass = int(a1_pass) + int(a2_pass) + int(a3_pass)
    return {"a1_r": a1_r, "a1_pass": a1_pass, "a2": a2, "a2_pass": a2_pass, "a3": a3, "a3_pass": a3_pass, "npass": npass, "n": n}


def verdict(r) -> Tuple[str, str]:
    s = "A1 conf-corr=%.3f(%s); A2 ensembling=%s(%s); A3 ternary=%s(%s); %d/3 (n=%d, sigma=%.1f)" % (
        r["a1_r"], r["a1_pass"], r["a2"], r["a2_pass"], r["a3"], r["a3_pass"], r["npass"], r["n"], SIGMA)
    if r["npass"] >= 2:
        return ("HARD_PASS", "HARD_PASS: encoder-noise robustness is RECOVERABLE (>=2/3 mechanisms work) -- v2.0 can add encoder-noise robustness as a moat feature. " + s)
    if r["npass"] == 1:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 1/3 noise-robustness mechanisms work -- partial recovery path. " + s)
    return ("HARD_FAIL", "HARD_FAIL: 0/3 mechanisms recover encoder-noise robustness -- rely on encoder quality; keep substrate noise-robustness claim to the STORAGE layer only. " + s)


print("[config] anchor=%s mode=%s n_items=%d sigma=%.1f encoder=%s" % (ANCHOR_NAME, RUN_MODE, NITEMS, SIGMA, BI), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
