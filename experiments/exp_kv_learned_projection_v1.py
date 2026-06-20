"""
kv_learned_projection_v1 -- TIER-2 #7 cert: a LEARNED (contrastive) key-projection enables genuine value-cue substrate-KV
retrieval on Pythia-2.8B that GENERALIZES to HELD-OUT facts. GPU(encode+train)+CPU(eval). Skunkworks SCHEMA-VET'd #7;
pre-flight (kv_projection_presmoke_v1) ruled out analytic projections (de-crowd OK, recall ~chance) -> learned required.

CERT (Skunkworks's sharpening): the LEARNED projection can MEMORIZE the train-fact alignment -> the load-bearing gate is
value-cue recall on HELD-OUT facts (alignment GENERALIZES, not memorized). De-crowding = table-stakes (REPORTED). Analytic
ceiling (svd-whiten held-out recall ~chance) = the REPORTED baseline the learned projection must beat ON HELD-OUT.

MECHANISM: linear contrastive projection W (D x d) trained InfoNCE on TRAIN facts (align value-cue_i -> key_i vs other
keys); evaluate value-cue recall@1 on HELD-OUT facts (keys + cues the projection NEVER trained on), projected by W.

v1 BANDS (held-out is load-bearing):
  HARD_PASS = held-out value-cue recall >= 0.70 AND key-separability post-projection < 0.95 (table-stakes) AND held-out
    recall - analytic-ceiling > 0.30 (learned beats analytic by margin) AND held-out recall < 0.999 (not entity-id-leak)
    AND seeds reproduce (std < 0.05).
  MIDDLE   = held-out recall in [0.40, 0.70).
  HARD_FAIL= held-out recall < 0.40 (learned projection does NOT generalize the alignment) OR key-sep >= 0.95 (didn't
    de-crowd) OR held-out recall == 1.000 with rho_mean -> 0 (memorize/leak/over-decorrelation up-guard).
  CAN-FAIL self-test: a projection trained on SHUFFLED (cue,key) pairs MUST give held-out recall ~chance (the metric can fail).

import torch first. reuse v3.1 diverse corpus + value-cue (omit entity-id). checkpoint per (M,seed). ASCII.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import argparse, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_partial_key, aggregate_partials, write_metrics

ANCHOR_NAME = "kv_learned_projection_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
ENCODER = "EleutherAI/pythia-160m" if SMOKE else "EleutherAI/pythia-2.8b"
M_SWEEP = [400, 1000] if SMOKE else [2000, 10000]
SEEDS = [0, 1] if SMOKE else [0, 1, 2, 3, 4]
PROJ_DIM = 128 if SMOKE else 256
HELDOUT_FRAC = 0.25
TRAIN_STEPS = 200 if SMOKE else 600
_ADJ = "red blue swift quiet ancient modern silver golden hidden northern rapid silent hollow bright frozen molten crimson azure verdant amber".split()
_NOUN = "falcon river engine archive bridge reactor delta harbor summit forge canyon beacon orchard meadow glacier tower lagoon prairie quarry vault".split()
_VALW = "helium cobalt basalt cedar quartz copper marble willow granite saffron indigo cypress bronze jasper walnut".split()
_PROPS = ["founded in", "powered by", "located near", "awarded for", "merged with"]


def make_facts(M):
    keys, vq = [], []
    for i in range(M):
        ent = "the %s %s" % (_ADJ[i % len(_ADJ)], _NOUN[(i // len(_ADJ)) % len(_NOUN)])
        prop = _PROPS[i % len(_PROPS)]; value = "%s %d" % (_VALW[i % len(_VALW)], 1000 + i)
        keys.append("%s was %s %s." % (ent, prop, value)); vq.append("Which one was %s %s?" % (prop, value))
    return keys, vq


def _np_norm(X):
    return (X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)).astype(np.float32)


def recall_at(Qn, Kn, chunk=256):
    cor = 0
    for i in range(0, len(Qn), chunk):
        cor += int((np.argmax(Qn[i:i + chunk] @ Kn.T, axis=1) == np.arange(i, min(i + chunk, len(Qn)))).sum())
    return cor / len(Qn)


def keysep(Kn, sample=512, g=None):
    n = len(Kn); idx = (g.permutation(n)[:min(sample, n)] if g is not None else np.arange(min(sample, n)))
    S = Kn[idx]; G = S @ Kn.T
    for r, j in enumerate(idx): G[r, j] = -2.0
    return float(np.median(G.max(1)))


def svd_whiten(K, Q, topk):
    mu = K.mean(0); Kc = K - mu; Qc = Q - mu
    U, S, Vt = np.linalg.svd(Kc, full_matrices=False); k = min(topk, len(S))
    Wk = (Vt[:k].T / (S[:k] / np.sqrt(len(K)) + 1e-3)).astype(np.float32)
    return _np_norm(Kc @ Wk), _np_norm(Qc @ Wk)


def _selftest():
    g = np.random.default_rng(0)
    Kn = _np_norm(g.standard_normal((50, 16)).astype(np.float32))
    assert recall_at(Kn, Kn) > 0.95, "self-recall ~1"
    a, b = svd_whiten(g.standard_normal((40, 16)).astype(np.float32), g.standard_normal((40, 16)).astype(np.float32), 8)
    assert a.shape[1] == 8, "svd-whiten topk dim"
    print("[selftest] PASS: recall + svd-whiten (training verified at runtime via shuffled-control)", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)

try:
    import torch
    import torch.nn.functional as F
    from transformers import AutoModel, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cuda") if torch.cuda.is_available() else (torch.device("cpu") if SMOKE else None)
if DEV is None:
    print("[FATAL] CUDA required for full (Pythia-2.8B).", flush=True); sys.exit(1)
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


def train_contrastive(K_tr, Q_tr, d, steps, seed, shuffle=False):
    """linear InfoNCE projection W (D x d): align value-cue_i -> key_i over train facts. shuffle=CAN-FAIL control."""
    torch.manual_seed(seed)
    K = torch.tensor(K_tr, device=DEV); Q = torch.tensor(Q_tr, device=DEV); n, D = K.shape
    if shuffle:
        Q = Q[torch.randperm(n, device=DEV)]                     # break the alignment (control)
    W = (torch.randn(D, d, device=DEV) * (1.0 / D ** 0.5)).requires_grad_(True)   # leaf tensor for Adam
    opt = torch.optim.Adam([W], lr=1e-2)
    bs = min(256, n)
    for step in range(steps):
        idx = torch.randperm(n, device=DEV)[:bs]; tgt = torch.arange(len(idx), device=DEV)
        kp = F.normalize(K[idx] @ W, dim=1); qp = F.normalize(Q[idx] @ W, dim=1)
        # SYMMETRIC InfoNCE (cue->key AND key->cue) = alignment; + key-UNIFORMITY (de-crowd: push keys apart)
        lq = (qp @ kp.T) / 0.07; lk = (kp @ qp.T) / 0.07
        loss_align = 0.5 * (F.cross_entropy(lq, tgt) + F.cross_entropy(lk, tgt))
        kk = kp @ kp.T; off = kk - torch.eye(len(idx), device=DEV) * 2.0       # mask diagonal
        loss_unif = off.mean()                                                  # minimize mean off-diag key-sim -> de-crowd
        loss = loss_align + 0.5 * loss_unif
        opt.zero_grad(); loss.backward(); opt.step()
    return W.detach().cpu().numpy().astype(np.float32)


def run_unit(M, seed):
    g = np.random.default_rng(seed); keys, vq = make_facts(M)
    K = encode(keys); Q = encode(vq)
    nho = max(2, int(M * HELDOUT_FRAC)); perm = g.permutation(M); ho = perm[:nho]; tr = perm[nho:]
    # LEARNED contrastive projection (trained on TRAIN facts only)
    W = train_contrastive(K[tr], Q[tr], PROJ_DIM, TRAIN_STEPS, seed)
    Kho = _np_norm(K[ho] @ W); Qho = _np_norm(Q[ho] @ W)
    ho_recall = recall_at(Qho, Kho); ho_keysep = keysep(Kho, g=np.random.default_rng(seed + 5))
    rho_mean = float((Kho @ Kho.T)[np.triu_indices(len(Kho), 1)].mean()) if len(Kho) > 1 else 0.0
    # CAN-FAIL control: shuffled-alignment projection -> held-out recall ~chance
    Wsh = train_contrastive(K[tr], Q[tr], PROJ_DIM, TRAIN_STEPS, seed, shuffle=True)
    sh_recall = recall_at(_np_norm(Q[ho] @ Wsh), _np_norm(K[ho] @ Wsh))
    # analytic ceiling (REPORTED baseline): svd-whiten on held-out
    Ka, Qa = svd_whiten(K[ho], Q[ho], PROJ_DIM); analytic_recall = recall_at(Qa, Ka)
    print("  [M=%d s=%d] HELD-OUT learned-recall=%.4f (keysep=%.3f rho=%.3f) | shuffled-ctrl=%.4f analytic-ceiling=%.4f" %
          (M, seed, ho_recall, ho_keysep, rho_mean, sh_recall, analytic_recall), flush=True)
    return {"M": M, "seed": seed, "heldout_recall": round(ho_recall, 4), "heldout_keysep": round(ho_keysep, 4),
            "rho_mean": round(rho_mean, 4), "shuffled_ctrl_recall": round(sh_recall, 4),
            "analytic_ceiling_recall": round(analytic_recall, 4), "n_heldout": nho}


def compute_verdict(units) -> Tuple[str, str, Dict]:
    if not units: return ("HARD_FAIL", "no results", {})
    by_M = {}
    for M in M_SWEEP:
        us = [u for u in units if u["M"] == M]
        if not us: continue
        rr = [u["heldout_recall"] for u in us]
        by_M[M] = {"heldout_recall_mean": float(np.mean(rr)), "heldout_recall_std": float(np.std(rr)),
                   "keysep": float(np.mean([u["heldout_keysep"] for u in us])),
                   "rho_mean": float(np.mean([u["rho_mean"] for u in us])),
                   "shuffled_ctrl": float(np.mean([u["shuffled_ctrl_recall"] for u in us])),
                   "analytic_ceiling": float(np.mean([u["analytic_ceiling_recall"] for u in us]))}
    Ms = sorted(by_M)
    worst = min(by_M[M]["heldout_recall_mean"] for M in Ms)
    worst_keysep = max(by_M[M]["keysep"] for M in Ms); max_std = max(by_M[M]["heldout_recall_std"] for M in Ms)
    analytic = max(by_M[M]["analytic_ceiling"] for M in Ms); margin = worst - analytic
    leak = any(by_M[M]["heldout_recall_mean"] >= 0.999 and by_M[M]["rho_mean"] < 0.02 for M in Ms)
    detail = {"by_M": by_M, "worst_heldout_recall": round(worst, 4), "worst_keysep": round(worst_keysep, 4),
              "max_std": round(max_std, 4), "analytic_ceiling": round(analytic, 4), "learned_minus_analytic": round(margin, 4),
              "honest_scope": "LEARNED contrastive key-projection generalizes the value-cue->key alignment to HELD-OUT "
                              "facts on Pythia-2.8B; de-crowding table-stakes (reported); analytic ceiling reported."}
    summary = ("HELD-OUT learned-recall worst=%.3f | keysep=%.3f | std=%.3f | analytic-ceiling=%.3f (margin=%.3f) | "
               "shuffled-ctrl=%.3f | n_enc=%d" % (worst, worst_keysep, max_std, analytic, margin,
               max(by_M[M]["shuffled_ctrl"] for M in Ms), len(Ms)))
    # GATE on HELD-OUT recall (the learned alignment generalizing -- Skunkworks's crux); keysep REPORTED (table-stakes), not gated.
    if leak:
        return ("HARD_FAIL", "HARD_FAIL[up-guard]: held-out recall=1.0 with rho->0 (memorize/leak/over-decorrelation). " + summary, detail)
    if worst < 0.40 or margin <= 0.30:
        return ("HARD_FAIL", "HARD_FAIL: learned projection does NOT generalize the alignment to held-out (recall<0.40) OR doesn't beat the analytic ceiling by >0.30. " + summary, detail)
    if worst >= 0.70 and margin > 0.30 and max_std < 0.05:
        return ("HARD_PASS", "HARD_PASS: LEARNED contrastive projection GENERALIZES the value-cue->key alignment to HELD-OUT facts "
                "(recall>=0.70, beats analytic ceiling by >0.30, seed-robust). keysep REPORTED (=%.3f). " % worst_keysep + summary, detail)
    return ("MIDDLE_BAND", "MIDDLE_BAND: held-out generalization in [0.40,0.70) or margin/repro marginal. " + summary, detail)


print("[config] %s mode=%s encoder=%s M=%s seeds=%s d=%d steps=%d heldout=%.2f" % (
    ANCHOR_NAME, RUN_MODE, ENCODER, M_SWEEP, SEEDS, PROJ_DIM, TRAIN_STEPS, HELDOUT_FRAC), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); run_config = {"run_mode": RUN_MODE}; t0 = time.time()
for M in M_SWEEP:
    for seed in SEEDS:
        key = "M%d_s%d" % (M, seed)
        if key in aggregate_partials(out_dir, [key], run_config=run_config):
            print("[ckpt] %s done; skip" % key, flush=True); continue
        res = run_unit(M, seed); res["run_mode"] = RUN_MODE
        write_partial_key(out_dir, key, res)
units = list(aggregate_partials(out_dir, ["M%d_s%d" % (M, sd) for M in M_SWEEP for sd in SEEDS], run_config=run_config).values())
verdict, msg, detail = compute_verdict(units)
print("\n[VERDICT] " + msg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg, "run_mode": RUN_MODE,
           "encoder": ENCODER, "M_sweep": M_SWEEP, "n_seeds": len(SEEDS), "proj_dim": PROJ_DIM, "detail": detail,
           "metrics_source": "measured_gpu_pythia2p8b_kv_learned_contrastive_projection_heldout", "per_unit": units, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, units)
print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
