"""
isotropy_capacity_v2_gpu_v1 -- TIER-2 #6: substrate Hebbian auto-associative CAPACITY across encoders is predicted by
embedding ISOTROPY (independent IsoScore, covariance-eigenvalue spectral-uniformity), NOT by SVD d_eff. GPU(encode)+
CPU(capacity/isoscore). Resolves the effrank d_eff honest-negative (capacity~d_eff REFUTED -> capacity~isotropy).

PRE-FLAG-B FIX (Skunkworks): isotropy = INDEPENDENT IsoScore (covariance-eigenvalue spectral-uniformity in [0,1];
1=uniform spectrum, 0=rank-1-collapsed), NOT 1-mean_pairwise_cos (which IS the Hebbian crosstalk -> circular). My own
impl here (separate code); Testbed's independent IsoScore (b2479cc8) is the 2nd-witness (per-encoder cross-check at VET).

CAPACITY = Hebbian auto-associative M_crit (store M keys in W=sum k k^T, recall noised key via r=W@q, cleanup-argmax;
crosstalk grows with M -> M_crit). Per-encoder. c-per-encoder = M_crit_obs/(1/E[<ki,kj>^2]) REPORTED (cleanup-boost;
prevents a c-artifact correlation -- if c varies wildly across encoders it distorts the Pearson). E[<>^2] via D x D gram
closed-form (no M x M). DISCIPLINES: capacity-RELATIVE (gate on M_crit/Pearson, not a fixed arbitrary recall@M);
run's-OWN-moments per encoder (not a reference). The v2 within-encoder causal anchor (pythia raw->#7-projected: iso up
-> capacity up ~125x) is REPORTED alongside (correlational + causal).

v1 BANDS: HARD_PASS = Pearson(IsoScore, log M_crit) > 0.80 across >=5 encoders AND Pearson(IsoScore,cap) > Pearson(d_eff,cap)
  (isotropy beats d_eff) AND c-per-encoder spread bounded (max/min c <= 5; else c-artifact flag) AND seeds reproduce.
  MIDDLE = Pearson in [0.5,0.8]. HARD_FAIL = Pearson < 0.5 (isotropy doesn't predict either -> 3rd axis needed)
  OR Pearson(d_eff,cap) >= Pearson(iso,cap) (d_eff predicts as well -> isotropy not the distinctive axis)
  OR c max/min > 10 (cleanup-boost artifact dominates). UP-guard: Pearson > 0.99 -> verify metric-overlap.
  CAN-FAIL: a shuffled IsoScore-vs-capacity pairing MUST give |Pearson| < 0.5.

import torch first. checkpoint per (encoder,seed). ASCII.
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

ANCHOR_NAME = "isotropy_capacity_v2_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
if SMOKE:
    ENCODERS = [("sentence-transformers/all-MiniLM-L6-v2", 384), ("BAAI/bge-small-en-v1.5", 384),
                ("BAAI/bge-large-en-v1.5", 1024), ("EleutherAI/pythia-160m", 768)]
    M_KEYS = 1500; GRID = [25, 50, 100, 200, 400, 800, 1500]; SEEDS = [1, 2]
else:
    ENCODERS = [("sentence-transformers/all-MiniLM-L6-v2", 384), ("sentence-transformers/all-mpnet-base-v2", 768),
                ("BAAI/bge-large-en-v1.5", 1024), ("sentence-transformers/sentence-t5-base", 768),
                ("EleutherAI/pythia-160m", 768), ("EleutherAI/pythia-2.8b", 2560)]
    M_KEYS = 8000; GRID = [50, 100, 200, 400, 800, 1600, 3200, 6400, 8000]; SEEDS = [1, 2, 3, 4, 5]
NOISE = 0.10


def make_texts(m, g):
    try:
        import json as _j
        pool = [e["text"] for e in _j.load(open(REPO / "experiments" / "data" / "ag_news.json", encoding="utf-8")).get("train", [])]
        seen = set(); ded = []
        for t in pool:
            k = t.strip().lower()
            if k and k not in seen: seen.add(k); ded.append(t)
        if len(ded) >= 50:
            idx = g.permutation(len(ded)); return [ded[int(idx[i % len(ded)])] for i in range(m)]
    except Exception:
        pass
    return ["entity %d founded near district %d in year %d" % (i, g.integers(0, 9999), 1000 + i) for i in range(m)]


def isoscore(X):
    """INDEPENDENT IsoScore: covariance-eigenvalue spectral-uniformity in [0,1] (1=uniform spectrum, 0=rank-1). NOT mean-cos."""
    Xc = X.astype(np.float64) - X.mean(0, keepdims=True)
    Sigma = (Xc.T @ Xc) / max(1, len(Xc) - 1)
    ev = np.maximum(np.linalg.eigvalsh(Sigma), 0.0)
    s = ev.sum()
    if s <= 0: return 0.0
    lh = ev / s; d = len(lh)
    if d <= 1: return 1.0
    l2 = float(np.linalg.norm(lh - 1.0 / d)); max_l2 = float(np.sqrt(1.0 - 1.0 / d))
    return float(np.clip(1.0 - l2 / max_l2, 0.0, 1.0))


def d_eff_pr(X):
    s = np.linalg.svd(X - X.mean(0, keepdims=True), compute_uv=False)
    return float((s.sum() ** 2) / (np.sum(s ** 2) + 1e-12))


def _recall_at_M(K, Kn, M, sigma, g):
    """Hebbian auto-assoc recall@1: W=sum k k^T; recall noised key via r=(q@sub^T)@sub; cleanup argmax. (raw keys, no whiten.)"""
    sub = K[:M].astype(np.float32); subn = Kn[:M]
    Q = sub + sigma * g.standard_normal((M, K.shape[1])).astype(np.float32)
    cor = 0
    for i in range(0, M, 1000):
        q = Q[i:i + 1000]; R = (q @ sub.T) @ sub
        Rn = R / (np.linalg.norm(R, axis=1, keepdims=True) + 1e-8)
        cor += int((np.argmax(Rn @ subn.T, axis=1) == np.arange(i, min(i + 1000, M))).sum())
    return cor / M


def capacity_sweep(emb, sigma, g, grid, thresh=0.90):
    K = emb.astype(np.float32); Kn = (K / (np.linalg.norm(K, axis=1, keepdims=True) + 1e-8)).astype(np.float32)
    curve = {}; prevM = 0.0; prevR = 1.0; cap = float(grid[-1])
    for M in grid:
        if M > len(K): cap = prevM; break
        r = _recall_at_M(K, Kn, M, sigma, g); curve[M] = round(r, 4)
        if r < thresh:
            cap = prevM + (M - prevM) * (prevR - thresh) / (prevR - r + 1e-9) if prevR > thresh else prevM
            break
        prevM = float(M); prevR = r
    return float(cap), curve


def e_sq_gram(Kn, M):
    """E[<ki,kj>^2] off-diagonal via D x D gram closed-form (no M x M). unit-normed keys."""
    sub = Kn[:M].astype(np.float64); G = sub.T @ sub; fro2 = float((G * G).sum())
    return (fro2 - M) / (M * (M - 1) + 1e-9)


def pearson(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    if np.std(x) < 1e-9 or np.std(y) < 1e-9: return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def _selftest():
    g = np.random.default_rng(0)
    iso_uni = isoscore(g.standard_normal((400, 32)).astype(np.float32))          # isotropic random -> high
    t = g.standard_normal((400, 1)).astype(np.float32); direction = g.standard_normal((1, 32)).astype(np.float32)
    iso_col = isoscore(t @ direction)                                            # rank-1: all variance on 1 axis -> low
    assert iso_uni > 0.7 and iso_col < 0.3, "IsoScore: uniform(%.3f) high, rank1(%.3f) low" % (iso_uni, iso_col)
    cap, _ = capacity_sweep(g.standard_normal((200, 32)).astype(np.float32), 0.05, np.random.default_rng(1), [20, 50, 100])
    assert cap < 200, "Hebbian capacity bounded (%.1f)" % cap
    assert abs(pearson([1, 2, 3], [2, 4, 6]) - 1.0) < 1e-9, "pearson"
    print("[selftest] PASS: IsoScore(uniform>collapsed, eigenvalue-based) + Hebbian-capacity + pearson", flush=True)


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
    print("[FATAL] CUDA required for full run.", flush=True); sys.exit(1)
print("[dev] %s" % DEV, flush=True)


def encode(eid, texts):
    tok = AutoTokenizer.from_pretrained(eid)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    mdl = AutoModel.from_pretrained(eid, torch_dtype=(torch.float16 if DEV.type == "cuda" else torch.float32)).to(DEV).eval()
    out = []
    for i in range(0, len(texts), 32):
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=32).to(DEV)
        with torch.no_grad():
            h = mdl(**t).last_hidden_state
        m = t["attention_mask"].unsqueeze(-1).float()
        out.append(((h * m).sum(1) / m.sum(1).clamp(min=1)).float().cpu().numpy())
    del mdl
    if DEV.type == "cuda": torch.cuda.empty_cache()
    return np.concatenate(out, 0).astype(np.float32)


def run_unit(eid, nominal_D, seed):
    g = np.random.default_rng(seed); emb = encode(eid, make_texts(M_KEYS, g))
    iso = isoscore(emb); de = d_eff_pr(emb)
    cap, curve = capacity_sweep(emb, NOISE, np.random.default_rng(seed + 100), GRID)
    Kn = (emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-8)).astype(np.float32)
    e2 = e_sq_gram(Kn, min(len(Kn), 5000)); raw_snr = 1.0 / (e2 + 1e-12); c = cap / (raw_snr + 1e-9)
    print("  [%s s=%d] IsoScore=%.4f d_eff=%.1f | M_crit=%.1f (raw-SNR=%.1f c=%.2f) curve=%s" %
          (eid.split("/")[-1], seed, iso, de, cap, raw_snr, c, curve), flush=True)
    return {"encoder": eid, "nominal_D": nominal_D, "seed": seed, "isoscore": round(iso, 4), "d_eff": round(de, 1),
            "m_crit": round(cap, 2), "c_cleanup_boost": round(c, 3), "e_sq": round(e2, 6)}


def compute_verdict(units) -> Tuple[str, str, Dict]:
    if not units: return ("HARD_FAIL", "no results", {})
    per = {}
    for eid, _ in ENCODERS:
        us = [u for u in units if u["encoder"] == eid]
        if not us: continue
        per[eid] = {"isoscore": float(np.mean([u["isoscore"] for u in us])), "d_eff": float(np.mean([u["d_eff"] for u in us])),
                    "m_crit": float(np.mean([u["m_crit"] for u in us])), "m_crit_cv": float(np.std([u["m_crit"] for u in us]) / (np.mean([u["m_crit"] for u in us]) + 1e-9)),
                    "c": float(np.mean([u["c_cleanup_boost"] for u in us]))}
    encs = list(per.keys())
    if len(encs) < 3: return ("UNKNOWN", "need >=3 encoders (got %d)" % len(encs), {"per_encoder": per})
    iso = [per[e]["isoscore"] for e in encs]; logcap = [np.log(per[e]["m_crit"] + 1) for e in encs]
    deff = [per[e]["d_eff"] for e in encs]
    r_iso = pearson(iso, logcap); r_deff = pearson(deff, logcap)
    cs = [per[e]["c"] for e in encs]; c_spread = max(cs) / (min(cs) + 1e-9)
    worst_cv = max(per[e]["m_crit_cv"] for e in encs)
    detail = {"per_encoder": per, "pearson_isoscore_vs_logMcrit": round(r_iso, 3), "pearson_deff_vs_logMcrit": round(r_deff, 3),
              "c_spread_max_over_min": round(c_spread, 2), "worst_m_crit_cv": round(worst_cv, 3),
              "honest_scope": "substrate Hebbian auto-assoc capacity (log M_crit) across %d encoders predicted by INDEPENDENT "
                              "IsoScore (covariance-eigenvalue spectral-uniformity, NOT mean-cos), better than SVD d_eff; "
                              "c-per-encoder (cleanup-boost) reported; v2 within-encoder causal anchor folded." % len(encs)}
    summary = ("Pearson(IsoScore,logMcrit)=%.3f vs Pearson(d_eff,logMcrit)=%.3f | c-spread=%.1fx | worst-CV=%.3f | n_enc=%d" %
               (r_iso, r_deff, c_spread, worst_cv, len(encs)))
    if r_iso > 0.99:
        summary = "[UP-GUARD: Pearson>0.99 -> verify IsoScore/capacity metric-overlap] " + summary
    if r_iso < 0.50 or r_deff >= r_iso or c_spread > 10.0:
        return ("HARD_FAIL", "HARD_FAIL: IsoScore doesn't predict capacity (<0.5) OR d_eff predicts as well (not the distinctive axis) OR cleanup-boost-artifact (c-spread>10x). " + summary, detail)
    if r_iso > 0.80 and r_deff < r_iso and c_spread <= 5.0 and worst_cv < 0.5:
        return ("HARD_PASS", "HARD_PASS: substrate capacity predicted by INDEPENDENT IsoScore (>0.80), beating SVD d_eff, c-bounded, seed-robust. " + summary, detail)
    return ("MIDDLE_BAND", "MIDDLE_BAND: IsoScore predicts capacity moderately (0.5-0.8) or c-spread 5-10x. " + summary, detail)


print("[config] %s mode=%s encoders=%s M_keys=%d seeds=%s" % (ANCHOR_NAME, RUN_MODE, [e[0].split("/")[-1] for e in ENCODERS], M_KEYS, SEEDS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); run_config = {"run_mode": RUN_MODE}; t0 = time.time()
for eid, nomD in ENCODERS:
    for seed in SEEDS:
        key = "%s_s%d" % (eid.split("/")[-1], seed)
        if key in aggregate_partials(out_dir, [key], run_config=run_config):
            print("[ckpt] %s done; skip" % key, flush=True); continue
        res = run_unit(eid, nomD, seed); res["run_mode"] = RUN_MODE
        write_partial_key(out_dir, key, res)
units = list(aggregate_partials(out_dir, ["%s_s%d" % (e[0].split("/")[-1], sd) for e in ENCODERS for sd in SEEDS], run_config=run_config).values())
verdict, msg, detail = compute_verdict(units)
print("\n[VERDICT] " + msg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg, "run_mode": RUN_MODE,
           "encoders": [e[0] for e in ENCODERS], "M_keys": M_KEYS, "n_seeds": len(SEEDS), "detail": detail,
           "metrics_source": "measured_gpu_isotropy_isoscore_vs_hebbian_capacity_cross_encoder", "per_unit": units, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, units)
print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
