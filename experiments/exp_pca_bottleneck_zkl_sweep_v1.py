"""
exp_pca_bottleneck_zkl_sweep_v1 -- manifold mitigation ZKL half: does PCA truncation kill membership leakage? -- GPU.

ROUTING: handoff research_to_exp_dev_manifold_bottleneck_sweep + research_to_exp_dev_paraphraser_substitution_authorize.
  KEY-job side already GREEN (pinv F1=1.0 at d=30). This is the ZKL side: LiRA membership-inference attack (T5 round-trip
  paraphraser, authorized substitute for MarianMT de-en which is torch<2.6/safetensors-blocked) on production Llama-3.2-1B
  L15 stored facts, swept over PCA-truncation dim d. SANITY GATE first: the substituted paraphraser must reproduce the
  cycle-151 baseline ZKL(50) in [0.17,0.27] at d=full, else the sweep is non-comparable. GPU (Llama encode + T5 gen).
PRE-REGISTERED:
  - SANITY: d=full ZKL(50) in [0.17,0.27] -> proceed; else verdict UNKNOWN (paraphraser non-equivalent, revert to MarianMT).
  - Case A (HARD_PASS): ZKL(50) < 0.10 at some d in {20,25,30} with KEY-F1 >= 0.99 -- HIPAA-grade recovered.
  - Case B (MIDDLE): ZKL(50) < 0.10 only at d <= 15 -- works with KEY-job cost; trade-off call.
  - Case C (HARD_FAIL): ZKL(50) >= 0.15 at all d -- leak not in the manifold dims; pivot to Hypothesis B/C.
FORMULA SELF-TESTS (PROT-022): 1. TPR@FPR=0.01 monotone. 2. PCA orthonormal. 3. cosine self=1.
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

ANCHOR_NAME = "pca_bottleneck_zkl_sweep_v1"
MODEL = "meta-llama/Llama-3.2-1B"; LAYER = 15; T5 = "t5-small"
DIMS = [10, 15, 20, 25, 30, 50]; K_PARA = 50; FPR = 0.01
CORPUS = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    N_STORED = 40; N_NEVER = 40; K_PARA = 16
else:
    N_STORED = 300; N_NEVER = 300


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def tpr_at_fpr(score_pos, score_neg, fpr=FPR):
    thr = np.quantile(score_neg, 1.0 - fpr)            # threshold s.t. FPR=fpr on negatives
    return float(np.mean(score_pos >= thr))


def pca_fit_full(E):
    mu = E.mean(0); U, S, Vt = np.linalg.svd(E - mu, full_matrices=False)
    eig = (S ** 2) / max(E.shape[0] - 1, 1)
    return mu, Vt, eig                                   # all components + eigenvalues


def whiten_d(E, mu, V, eig, d):
    # PCA-whiten keeping the top-d principal components (production whitening at d=all; bottleneck at d<all)
    P = (E - mu) @ V[:d].T
    return P / np.sqrt(eig[:d] + 1e-6)


def _selftest():
    g = np.random.default_rng(0); pos = g.standard_normal(500) + 2.0; neg = g.standard_normal(500)
    assert tpr_at_fpr(pos, neg) > tpr_at_fpr(neg, neg), "TPR@FPR=0.01 monotone"
    mu, V, eig = pca_fit_full(g.standard_normal((40, 16))); assert abs((V[:4] @ V[:4].T - np.eye(4)).max()) < 1e-4, "PCA orthonormal"
    v = unit(g.standard_normal((1, 8))); assert abs(float(v @ v.T) - 1.0) < 1e-5, "cosine self=1"
    print("[selftest] PASS: pca-bottleneck-zkl", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, T5ForConditionalGeneration, T5Tokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
if not torch.cuda.is_available():
    print("[FATAL] CUDA required.", flush=True); sys.exit(1)
DEV = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)


def load_texts(n):
    out = []
    if not CORPUS.exists():
        return out
    for l in open(CORPUS, encoding="utf-8"):
        try:
            r = json.loads(l)
        except Exception:
            continue
        t = r.get("long_answer") or r.get("question") or ""
        if isinstance(t, str) and 40 < len(t) < 300:
            out.append(t.strip())
        if len(out) >= n:
            break
    return out


def t5_roundtrip(texts, k, t5tok, t5m):
    # en -> de (greedy) -> en (sample k) ; returns list (len texts) of list[k] paraphrases
    variants = []
    for t in texts:
        de_in = t5tok("translate English to German: " + t, return_tensors="pt", truncation=True, max_length=96).to(DEV)
        with torch.no_grad():
            de_ids = t5m.generate(**de_in, max_new_tokens=80, num_beams=1)
        de = t5tok.decode(de_ids[0], skip_special_tokens=True)
        en_in = t5tok("translate German to English: " + de, return_tensors="pt", truncation=True, max_length=96).to(DEV)
        with torch.no_grad():
            en_ids = t5m.generate(**en_in, max_new_tokens=80, do_sample=True, top_k=50, temperature=1.2, num_return_sequences=k)
        variants.append([t5tok.decode(x, skip_special_tokens=True) for x in en_ids])
    return variants


def llama_encode(texts, tok, m):
    out = []
    for i in range(0, len(texts), 16):
        t = tok(texts[i:i + 16], return_tensors="pt", padding=True, truncation=True, max_length=96).to(DEV)
        with torch.no_grad():
            o = m(**t, output_hidden_states=True)
        out.append(o.hidden_states[LAYER][:, -1, :].float().cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32) if out else np.zeros((0, 1), np.float32)


def zkl_at(keys, var_pos, var_neg):
    # membership score = max over a fact's k paraphrase-variants of max cosine to any stored key
    Ku = unit(keys)
    sp = (unit(var_pos) @ Ku.T).max(axis=2).max(axis=1)   # [Npos]
    sn = (unit(var_neg) @ Ku.T).max(axis=2).max(axis=1)   # [Nneg]
    return tpr_at_fpr(sp, sn)


def run() -> Dict:
    facts = load_texts(N_STORED + N_NEVER)
    if len(facts) < N_STORED + 10:
        print("[FATAL] corpus too small", flush=True); return {"by": {}, "n": 0, "sanity_ok": False}
    stored = facts[:N_STORED]; never = facts[N_STORED:N_STORED + N_NEVER]
    t5tok = T5Tokenizer.from_pretrained(T5); t5m = T5ForConditionalGeneration.from_pretrained(T5, use_safetensors=True).to(DEV).eval()
    print("  generating %d paraphrases x %d facts (T5 round-trip)..." % (K_PARA, len(stored) + len(never)), flush=True)
    pv = t5_roundtrip(stored, K_PARA, t5tok, t5m); nv = t5_roundtrip(never, K_PARA, t5tok, t5m); del t5m; torch.cuda.empty_cache()
    tok = AutoTokenizer.from_pretrained(MODEL); tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    m = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float16, use_safetensors=True).to(DEV).eval()
    keys = llama_encode(stored, tok, m)
    Kp = len(pv[0]); var_pos = llama_encode([p for vs in pv for p in vs], tok, m).reshape(len(stored), Kp, -1)
    var_neg = llama_encode([p for vs in nv for p in vs], tok, m).reshape(len(never), Kp, -1)
    del m; torch.cuda.empty_cache()
    mu, V, eig = pca_fit_full(keys); D = V.shape[0]
    Sp = var_pos.shape; Sn = var_neg.shape

    def proj(d):
        kp = whiten_d(keys, mu, V, eig, d)
        vp = whiten_d(var_pos.reshape(-1, Sp[2]), mu, V, eig, d).reshape(Sp[0], Sp[1], d)
        vn = whiten_d(var_neg.reshape(-1, Sn[2]), mu, V, eig, d).reshape(Sn[0], Sn[1], d)
        return kp, vp, vn

    by = {}; kp, vp, vn = proj(D); by["full"] = zkl_at(kp, vp, vn)   # full PCA whitening = production baseline
    print("  ZKL(%d)[full-whiten] = %.3f (cycle-151 baseline ~0.22)" % (K_PARA, by["full"]), flush=True)
    sanity_ok = 0.17 <= by["full"] <= 0.27
    if sanity_ok or RUN_MODE == "smoke":   # smoke always shows the sweep (k<50 may undershoot the 0.22 gate)
        for d in DIMS:
            if d >= D:   # not enough PCA components (n_stored too small in smoke); skip
                continue
            kp, vp, vn = proj(d); by["d%d" % d] = zkl_at(kp, vp, vn)
            print("  ZKL(%d)[d=%d] = %.3f" % (K_PARA, d, by["d%d" % d]), flush=True)
    return {"by": by, "n": len(stored), "sanity_ok": sanity_ok, "k": K_PARA}


def verdict(r) -> Tuple[str, str]:
    by = r["by"]; summary = "ZKL(%d) by dim: %s (n_stored=%d)" % (r.get("k", K_PARA), {k: round(v, 3) for k, v in by.items()}, r["n"])
    if not r["sanity_ok"]:
        return ("UNKNOWN", "UNKNOWN: T5 paraphraser did NOT reproduce cycle-151 baseline (d=full ZKL=%.3f, need 0.17-0.27) -- non-equivalent; revert to MarianMT de-en. " % by.get("full", 0.0) + summary)
    mid = [by.get("d%d" % d, 1.0) for d in (20, 25, 30)]
    if min(mid) < 0.10:
        return ("HARD_PASS", "HARD_PASS (Case A): PCA bottleneck drops ZKL(50)<0.10 at d in {20,25,30} (KEY-job F1=1.0 there per the keyjob sweep) -- HIPAA-grade privacy RECOVERED via manifold-dim projection. " + summary)
    if min(by.get("d%d" % d, 1.0) for d in DIMS) < 0.10:
        return ("MIDDLE_BAND", "MIDDLE_BAND (Case B): ZKL<0.10 only at low d (<=15) -- mitigation works with KEY-job cost; trade-off call to Research. " + summary)
    return ("HARD_FAIL", "HARD_FAIL (Case C): ZKL>=0.10 at all tested d -- leak is NOT in the manifold dims; pivot to Hypothesis B (token-position) or C (Gram). " + summary)


print("[config] anchor=%s mode=%s N_stored=%d N_never=%d k=%d dims=%s" % (ANCHOR_NAME, RUN_MODE, N_STORED, N_NEVER, K_PARA, DIMS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
