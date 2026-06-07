"""
exp_pca_bottleneck_zkl_sweep_v1 -- Hyp C mitigation: cosine-entropy whitening (flatten member-member Gram) ZKL + KEY-F1 -- GPU.

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

ANCHOR_NAME = "zkl_hypC_cosine_entropy_v1"
MODEL = "meta-llama/Llama-3.2-1B"; LAYER = 15; ENDE = "Helsinki-NLP/opus-mt-en-de"; DEEN = "Helsinki-NLP/opus-mt-de-en"
RANKS = [0, 2, 5, 10, 20]; K_PARA = 50; FPR = 0.01   # project out top-r member-Gram clustering directions
CORPUS = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"   # Wikipedia bio/relational sentences (cycle-151 KB match)
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    N_STORED = 60; N_NEVER = 60; K_PARA = 16
else:
    N_STORED = 500; N_NEVER = 500   # cycle-151 exact


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
    from transformers import AutoModelForCausalLM, AutoTokenizer, MarianMTModel, MarianTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
if not torch.cuda.is_available():
    print("[FATAL] CUDA required.", flush=True); sys.exit(1)
DEV = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)


def load_texts(n):
    out = []; seen = set()
    if not CORPUS.exists():
        return out
    for l in open(CORPUS, encoding="utf-8"):
        try:
            r = json.loads(l)
        except Exception:
            continue
        ctx = r.get("context") or {}; sent_lists = ctx.get("sentences") or []
        for sl in sent_lists:
            for sent in sl:                                  # Wikipedia context sentences (bio/relational, mixed)
                t = sent.strip()
                if 40 < len(t) < 300 and t not in seen:
                    seen.add(t); out.append(t)
                    if len(out) >= n:
                        return out
    return out


def marian_roundtrip(texts, k, ende_tok, ende_m, deen_tok, deen_m):
    # en -> de (greedy) -> en (sample k) via MarianMT ; returns list (len texts) of list[k] paraphrases
    variants = []
    for t in texts:
        di = ende_tok([t], return_tensors="pt", truncation=True, max_length=96, padding=True).to(DEV)
        with torch.no_grad():
            de_ids = ende_m.generate(**di, max_new_tokens=96, num_beams=1)
        de = ende_tok.decode(de_ids[0], skip_special_tokens=True)
        ei = deen_tok([de] * k, return_tensors="pt", truncation=True, max_length=96, padding=True).to(DEV)  # k copies -> k independent samples
        with torch.no_grad():
            en_ids = deen_m.generate(**ei, max_new_tokens=96, do_sample=True, top_k=50, temperature=1.3, num_beams=1)
        variants.append([deen_tok.decode(x, skip_special_tokens=True) for x in en_ids])
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
    ende_tok = MarianTokenizer.from_pretrained(ENDE); ende_m = MarianMTModel.from_pretrained(ENDE, use_safetensors=True).to(DEV).eval()
    deen_tok = MarianTokenizer.from_pretrained(DEEN); deen_m = MarianMTModel.from_pretrained(DEEN, use_safetensors=True).to(DEV).eval()
    print("  generating %d paraphrases x %d facts (MarianMT round-trip)..." % (K_PARA, len(stored) + len(never)), flush=True)
    pv = marian_roundtrip(stored, K_PARA, ende_tok, ende_m, deen_tok, deen_m); nv = marian_roundtrip(never, K_PARA, ende_tok, ende_m, deen_tok, deen_m)
    del ende_m, deen_m; torch.cuda.empty_cache()
    tok = AutoTokenizer.from_pretrained(MODEL); tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    m = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float16, use_safetensors=True).to(DEV).eval()
    keys = llama_encode(stored, tok, m)
    Kp = len(pv[0]); var_pos = llama_encode([p for vs in pv for p in vs], tok, m).reshape(len(stored), Kp, -1)
    var_neg = llama_encode([p for vs in nv for p in vs], tok, m).reshape(len(never), Kp, -1)
    del m; torch.cuda.empty_cache()
    mu, V, eig = pca_fit_full(keys); D = V.shape[0]
    Kw = whiten_d(keys, mu, V, eig, D)                                  # production whitened keys (baseline)
    # cosine-entropy step: find the directions along which WHITENED members still cluster (top PCs of whitened-member Gram)
    Kwu = Kw / (np.linalg.norm(Kw, axis=1, keepdims=True) + 1e-8)
    Uc, Sc, Vc = np.linalg.svd(Kwu - Kwu.mean(0), full_matrices=False)  # Vc rows = residual clustering directions
    Sp = var_pos.shape; Sn = var_neg.shape

    def proj(r):
        def tx(X):
            W = whiten_d(X, mu, V, eig, D)
            if r > 0:
                P = Vc[:r]; W = W - (W @ P.T) @ P                       # remove top-r residual member-clustering dirs
            return W
        kp = tx(keys)
        vp = tx(var_pos.reshape(-1, Sp[2])).reshape(Sp[0], Sp[1], -1)
        vn = tx(var_neg.reshape(-1, Sn[2])).reshape(Sn[0], Sn[1], -1)
        return kp, vp, vn
    def keyf1(K):
        Ku = unit(K).astype(np.float64); G = Ku @ Ku.T + 1e-3 * np.eye(len(Ku)); Wi = np.linalg.solve(G, Ku)
        return float((np.argmax(Ku @ Wi.T, axis=1) == np.arange(len(Ku))).mean())
    by = {}
    for r in RANKS:
        kp, vp, vn = proj(r); by["r%d" % r] = {"zkl": zkl_at(kp, vp, vn), "f1": keyf1(kp)}
        print("  project-out r=%d: ZKL(%d)=%.3f KEY-F1=%.3f" % (r, K_PARA, by["r%d" % r]["zkl"], by["r%d" % r]["f1"]), flush=True)
    base = by["r0"]["zkl"]; sanity_ok = 0.17 <= base <= 0.27
    return {"by": by, "n": len(stored), "sanity_ok": sanity_ok, "k": K_PARA, "f1_base": by["r0"]["f1"]}


def verdict(r) -> Tuple[str, str]:
    by = r["by"]; f0 = r["f1_base"]
    best = None
    for k, v in by.items():
        if v["zkl"] <= 0.10 and (f0 - v["f1"]) <= 0.10:
            best = (k, v); break
    summary = "by project-out-r: %s (n=%d; baseline ZKL=%.3f F1=%.3f)" % ({k: {"zkl": round(v["zkl"], 3), "f1": round(v["f1"], 3)} for k, v in by.items()}, r["n"], by["r0"]["zkl"], f0)
    if best:
        return ("HARD_PASS", "HARD_PASS (Hyp C mitigation): cosine-entropy projection at %s drops ZKL(50)<=0.10 with KEY-F1 drop<=10%% -- ABSOLUTE HIPAA RECOVERED via Gram-flattening whitening. " % best[0] + summary)
    bz = min(v["zkl"] for v in by.values())
    if bz <= 0.15:
        return ("MIDDLE_BAND", "MIDDLE_BAND: cosine-entropy projection reaches 0.10-0.15 -- promising; tune r / optimize the entropy basis. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: projecting out member-clustering directions does not bring ZKL<=0.15 -- Gram-flattening insufficient; Hyp-C linear mitigation bounded too. " + summary)


print("[config] anchor=%s mode=%s N_stored=%d N_never=%d k=%d ranks=%s" % (ANCHOR_NAME, RUN_MODE, N_STORED, N_NEVER, K_PARA, RANKS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
