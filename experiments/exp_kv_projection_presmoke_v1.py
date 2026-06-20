"""
kv_projection_presmoke_v1 -- the 2.8b-keys ANALYTIC-projection pre-flight for learned-projection TIER-2 #7 (Orchestrator/
Research-requested cheap pre-flight before the full contrastive #7 dispatch). GPU(encode)+CPU(projection/recall).

QUESTION: can an ANALYTIC projection de-crowd Pythia-2.8B substrate-KV keys at scale (the v3.1 HARD_FAIL was raw
mean-centered keys crowding to max-cos 0.97-0.99 at 2k-10k -> value-cue recall ~chance)? If an analytic projection gets
keysep<0.95 + recall>0.5 at M=10k, the projection PATH works (full #7 = contrastive). If none, contrastive is REQUIRED.
This is a DIAGNOSTIC pre-flight, NOT the cert (#7 contrastive is the cert).

PROJECTIONS (analytic, no training): raw | mean-center (v3.1) | per-key ZCA (full whitening) | SVD-whiten-topk
(project to top-k SVD comps + scale -- de-crowds without full ZCA over-rotation; the 160m diagnostic showed full-ZCA
OVER-rotates to max-cos 0.003 / recall 0.01, so top-k is the middle ground).

VALUE-CUE per fact (omit entity-id, v3 discipline): "Which one was {prop} {value}?" -> retrieve the fact.
Reports per (projection, M): keysep=median max-cos(key, other-key) + value-cue recall@1. import torch first. ASCII.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import argparse, time, itertools
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "kv_projection_presmoke_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
ENCODER = "EleutherAI/pythia-160m" if SMOKE else "EleutherAI/pythia-2.8b"
M_SWEEP = [200, 500] if SMOKE else [2000, 10000]
SEED = 0
TOPK = 64 if SMOKE else 256                                   # SVD-whiten top-k components
_ADJ = "red blue swift quiet ancient modern silver golden hidden northern rapid silent hollow bright frozen molten crimson azure verdant amber".split()
_NOUN = "falcon river engine archive bridge reactor delta harbor summit forge canyon beacon orchard meadow glacier tower lagoon prairie quarry vault".split()
_VALW = "helium cobalt basalt cedar quartz copper marble willow granite saffron indigo cypress bronze jasper walnut".split()
_PROPS = ["founded in", "powered by", "located near", "awarded for", "merged with"]


def make_facts(M, g):
    keys, vq = [], []
    for i in range(M):
        ent = "the %s %s" % (_ADJ[i % len(_ADJ)], _NOUN[(i // len(_ADJ)) % len(_NOUN)])
        prop = _PROPS[i % len(_PROPS)]; value = "%s %d" % (_VALW[i % len(_VALW)], 1000 + i)
        keys.append("%s was %s %s." % (ent, prop, value)); vq.append("Which one was %s %s?" % (prop, value))
    return keys, vq


def _norm(X):
    return (X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)).astype(np.float32)


def project(K, Q, kind, topk):
    """fit projection on keys K; apply to keys + queries Q. Returns (Kp_norm, Qp_norm)."""
    K = K.astype(np.float32); Q = Q.astype(np.float32); mu = K.mean(0)
    if kind == "raw":
        return _norm(K), _norm(Q)
    if kind == "mean_center":
        return _norm(K - mu), _norm(Q - mu)
    Kc = K - mu; Qc = Q - mu
    U, S, Vt = np.linalg.svd(Kc, full_matrices=False)
    if kind == "zca":
        W = (Vt.T @ np.diag(1.0 / (S / np.sqrt(len(K)) + 1e-3)) @ Vt).astype(np.float32)  # full ZCA whitening
        return _norm(Kc @ W), _norm(Qc @ W)
    if kind == "svd_whiten_topk":
        k = min(topk, len(S)); Wk = (Vt[:k].T / (S[:k] / np.sqrt(len(K)) + 1e-3)).astype(np.float32)  # top-k whiten
        return _norm(Kc @ Wk), _norm(Qc @ Wk)
    raise ValueError(kind)


def keysep(Kn, sample=512, g=None):
    n = len(Kn); idx = (g.permutation(n)[:min(sample, n)] if g is not None else np.arange(min(sample, n)))
    S = Kn[idx]; G = S @ Kn.T
    for r, j in enumerate(idx): G[r, j] = -2.0
    return float(np.median(G.max(1)))


def recall_at(Qn, Kn, chunk=256):
    cor = 0
    for i in range(0, len(Qn), chunk):
        cor += int((np.argmax(Qn[i:i + chunk] @ Kn.T, axis=1) == np.arange(i, min(i + chunk, len(Qn)))).sum())
    return cor / len(Qn)


def _selftest():
    g = np.random.default_rng(0)
    # anisotropic keys (tight cone) -> raw crowds (high max-cos); mean-center/whiten de-crowd
    base = g.standard_normal((1, 32)); K = (base * 5 + g.standard_normal((200, 32))).astype(np.float32)
    Kn_raw, _ = project(K, K, "raw", 16); Kn_mc, _ = project(K, K, "mean_center", 16)
    assert keysep(Kn_raw, g=g) > keysep(Kn_mc, g=g), "mean-center de-crowds an anisotropic cone vs raw"
    # recall machinery: project keys, self-query recovers
    Kn, Qn = project(K, K, "mean_center", 16); assert recall_at(Qn, Kn) > 0.9, "self-recall ~1 post-projection"
    print("[selftest] PASS: projections de-crowd + recall machinery", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)

try:
    import torch
    from transformers import AutoModel, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cuda") if torch.cuda.is_available() else (torch.device("cpu") if SMOKE else None)
if DEV is None:
    print("[FATAL] CUDA required for full run (Pythia-2.8B).", flush=True); sys.exit(1)
print("[dev] %s" % DEV, flush=True)


def encode(texts):
    tok = AutoTokenizer.from_pretrained(ENCODER)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    mdl = AutoModel.from_pretrained(ENCODER, torch_dtype=(torch.float16 if DEV.type == "cuda" else torch.float32)).to(DEV).eval()
    out = []
    for i in range(0, len(texts), 32):
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=48).to(DEV)
        with torch.no_grad():
            h = mdl(**t).last_hidden_state
        m = t["attention_mask"].unsqueeze(-1).float()
        out.append(((h * m).sum(1) / m.sum(1).clamp(min=1)).float().cpu().numpy())
    del mdl
    if DEV.type == "cuda": torch.cuda.empty_cache()
    return np.concatenate(out, 0).astype(np.float32)


KINDS = ["raw", "mean_center", "zca", "svd_whiten_topk"]
print("[config] %s mode=%s encoder=%s M=%s kinds=%s topk=%d" % (ANCHOR_NAME, RUN_MODE, ENCODER, M_SWEEP, KINDS, TOPK), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); rows = []
for M in M_SWEEP:
    g = np.random.default_rng(SEED); keys, vq = make_facts(M, g)
    K = encode(keys); Q = encode(vq)
    for kind in KINDS:
        Kn, Qn = project(K, Q, kind, TOPK)
        ks = keysep(Kn, g=np.random.default_rng(SEED + 1)); rc = recall_at(Qn, Kn)
        rows.append({"M": M, "projection": kind, "keysep_max_cos_other": round(ks, 4), "value_cue_recall": round(rc, 4)})
        print("  M=%-6d %-16s keysep(max-cos-other)=%.4f  value_cue_recall=%.4f" % (M, kind, ks, rc), flush=True)
# pre-flight readout (3-way): de-crowd AND recall (analytic suffices) | de-crowd but NOT recall (contrastive needed for
# ALIGNMENT) | no de-crowd (projection doesn't even separate). The distinction drives #7 design.
bigM = max(M_SWEEP); at_big = [r for r in rows if r["M"] == bigM]
decrowd = [r for r in at_big if r["keysep_max_cos_other"] < 0.95]
viable = [r for r in decrowd if r["value_cue_recall"] > 0.5]
if viable:
    verdict = "PROJECTION_PATH_VIABLE"
    msg = "PROJECTION_PATH_VIABLE @ M=%d: analytic projection suffices: %s" % (bigM, ", ".join(
        "%s(keysep=%.3f,recall=%.3f)" % (r["projection"], r["keysep_max_cos_other"], r["value_cue_recall"]) for r in viable))
elif decrowd:
    verdict = "DECROWD_OK_RECALL_NEEDS_CONTRASTIVE"
    msg = ("DECROWD_OK_RECALL_NEEDS_CONTRASTIVE @ M=%d: analytic projections DE-CROWD keys (keysep<0.95: %s) but recall "
           "stays <0.5 -> de-crowding NECESSARY not SUFFICIENT; the value-cue->key ALIGNMENT needs the LEARNED/CONTRASTIVE "
           "projection (#7 cert). Best recall=%.3f." % (bigM, ", ".join(
           "%s=%.3f" % (r["projection"], r["keysep_max_cos_other"]) for r in decrowd), max(r["value_cue_recall"] for r in at_big)))
else:
    verdict = "NO_ANALYTIC_PROJECTION_DECROWDS"
    msg = "NO_ANALYTIC_PROJECTION_DECROWDS @ M=%d: no analytic projection got keysep<0.95 -> projection itself insufficient." % bigM
print("\n[VERDICT] " + msg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg, "run_mode": RUN_MODE,
           "metrics_source": "measured_gpu_pythia2p8b_kv_projection_presmoke_keysep_recall", "encoder": ENCODER,
           "rows": rows, "note": "DIAGNOSTIC pre-flight for #7 (analytic projections); contrastive = the cert", "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, rows)
print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
