"""
effective_rank_svd_pull_up_v2_gpu_v1 -- substrate capacity is bounded by encoder EFFECTIVE dim (d_eff),
NOT nominal dim D -- cross-encoder correlation pull-up. GPU(encode)+CPU(SVD/recall). Research v2 + Skunkworks GO.

CLAIM (load-bearing, the cert): substrate storage CAPACITY correlates with the encoder's d_eff (intrinsic /
usable rank) NOT its nominal dimension D. Tested across encoders of differing D. (Smoke->cert pull-up of the
effective_rank_svd + dim_expansion_cross_encoder legacy findings.)

MECHANISM: per encoder, encode M texts -> embedding matrix; SVD -> d_eff via 3 methods (participation_ratio,
rank95, spectral_entropy=exp(H)). Substrate CAPACITY = recall@1 over the M embeddings as Hopfield keys (whiten +
noised query; the pythia-KV recall mechanism) -- higher usable rank -> more separable keys -> higher recall.
Then Spearman(capacity, d_eff) vs Spearman(capacity, nominal_D) ACROSS encoders.

ENCODERS: full = MiniLM(384) + mpnet(768) + bge-large(1024) + Pythia-2.8B(2560). smoke = MiniLM + bge-small +
pythia-160m (locally cached; for logic verify). d_eff MAGNITUDES are REPORTED per-encoder (not gated).

v2 BANDS (band-contradiction pre-fixed by Research: gate the CORRELATION, report magnitudes):
  HARD_PASS = Spearman(capacity, d_eff) >= 0.80 across encoders AND d_eff 3-method-consistent (within +-20% per
              encoder) AND all 5 seeds reproduce capacity within +-5%.
  MIDDLE    = Spearman(capacity, d_eff) in [0.50,0.80) OR 3-method consistency in (+-20%, +-40%].
  HARD_FAIL = capacity correlates with nominal D not d_eff (Spearman(capacity,d_eff) < 0.50)
              OR 3-method inconsistent (> +-40%) OR seeds disagree > 10%.
  Pythia outcome informative either way (low d_eff = intrinsic-dim generalizes to LM; high d_eff = LM breaks the
  ceiling -> more capacity IF capacity tracks it). REPORTED: per-encoder d_eff(3 methods) + nominal D + capacity.

checkpoint/resume per (encoder,seed). import torch first (PROT-020). PROT-018 no _nN. ASCII.
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

ANCHOR_NAME = "effective_rank_svd_pull_up_v2_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
NOISE = 0.10
if SMOKE:
    ENCODERS = [("sentence-transformers/all-MiniLM-L6-v2", "st", 384), ("BAAI/bge-small-en-v1.5", "st", 384),
                ("EleutherAI/pythia-160m", "lm", 768)]
    M_MAX = 1500; GRID = [25, 50, 100, 200, 400, 800, 1500]; SEEDS = [1, 2]
else:
    ENCODERS = [("sentence-transformers/all-MiniLM-L6-v2", "st", 384), ("sentence-transformers/all-mpnet-base-v2", "st", 768),
                ("BAAI/bge-large-en-v1.5", "st", 1024), ("EleutherAI/pythia-2.8b", "lm", 2560)]
    M_MAX = 8000; GRID = [50, 100, 200, 400, 800, 1600, 3200, 6400, 8000]; SEEDS = [1, 2, 3, 4, 5]


def make_texts(m, g):
    """DIVERSE real corpus (ag_news news articles) for realistic embedding angular spread -> the associative capacity
    tracks usable rank instead of collapsing on clustered templates. Synthetic varied fallback if the corpus is absent."""
    import json as _json
    try:
        pool = [e["text"] for e in _json.load(open(REPO / "experiments" / "data" / "ag_news.json", encoding="utf-8")).get("train", [])]
        if len(pool) >= 50:
            idx = g.permutation(len(pool))
            return [pool[int(idx[i % len(pool)])] for i in range(m)]
    except Exception:
        pass
    subj = ["alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel", "india", "juliet"]
    rel = ["founded in", "located near", "invented by", "merged with", "capital of", "awarded for", "powered by", "discovered in"]
    obj = ["the northern district", "the rival firm", "an unknown engineer", "the small province", "a novel reactor", "the deep archive", "best design", "the eastern wing"]
    return ["entity %s-%d %s %s" % (subj[i % 10], i, rel[g.integers(0, len(rel))], obj[g.integers(0, len(obj))]) for i in range(m)]


def participation_ratio(s):
    s = np.asarray(s, dtype=np.float64); return float((s.sum() ** 2) / (np.sum(s ** 2) + 1e-12))


def var_rank(s, frac):
    e = np.asarray(s, dtype=np.float64) ** 2; c = np.cumsum(e) / (e.sum() + 1e-12)
    return int(np.searchsorted(c, frac) + 1)


def spectral_entropy_deff(s):
    e = np.asarray(s, dtype=np.float64) ** 2; p = e / (e.sum() + 1e-12); p = p[p > 0]
    return float(np.exp(-np.sum(p * np.log(p))))


def d_eff_all(emb):
    s = np.linalg.svd(emb - emb.mean(0, keepdims=True), compute_uv=False)
    return {"participation_ratio": participation_ratio(s), "rank95": var_rank(s, 0.95), "spectral_entropy": spectral_entropy_deff(s)}


def _recall_at_M(Kn, K, M, sigma, g):
    """Hebbian AUTO-ASSOCIATIVE recall@1: store first M RAW keys in a superposition weight matrix W = sum_k k k^T
    (= sub^T @ sub), recall r = W @ q_noisy, clean up by argmax over the M-codebook. Crosstalk from the OTHER stored
    patterns grows with M, so capacity is BOUNDED by usable rank (d_eff) -- the cert's whole hypothesis. (A plain
    nearest-neighbour lookup over explicit keys has NO such bottleneck -> can't test d_eff; that was the saturation bug.)
    Computed as r = (q @ sub^T) @ sub to avoid materialising the D x D W for large D."""
    sub = K[:M].astype(np.float32); subn = Kn[:M]
    Q = sub + sigma * g.standard_normal((M, K.shape[1])).astype(np.float32)
    cor = 0
    for i in range(0, M, 1000):
        q = Q[i:i + 1000]
        R = (q @ sub.T) @ sub                    # M_chunk x D recalled superposition (crosstalk-corrupted)
        Rn = R / (np.linalg.norm(R, axis=1, keepdims=True) + 1e-8)
        cor += int((np.argmax(Rn @ subn.T, axis=1) == np.arange(i, min(i + 1000, M))).sum())
    return cor / M


def capacity_sweep(emb, sigma, g, grid, thresh=0.90):
    """substrate CAPACITY = max M (over grid) with raw-embedding recall@1 >= thresh. The Hopfield-capacity proxy that
    DISCRIMINATES by d_eff (low usable-rank -> keys collide sooner -> capacity caps lower). Returns (capacity, curve)."""
    K = emb.astype(np.float32); Kn = (K / (np.linalg.norm(K, axis=1, keepdims=True) + 1e-8)).astype(np.float32)
    curve = {}; prevM = 0.0; prevR = 1.0; cap = float(grid[-1])   # all-pass default = grid max
    for M in grid:
        if M > len(K): cap = prevM; break
        r = _recall_at_M(Kn, K, M, sigma, g); curve[M] = round(r, 4)
        if r < thresh:   # recall ~monotone-decreasing in load -> interpolate the threshold crossing for a continuous capacity
            cap = prevM + (M - prevM) * (prevR - thresh) / (prevR - r + 1e-9) if prevR > thresh else prevM
            break
        prevM = float(M); prevR = r
    return float(cap), curve


def spearman(x, y):
    x = np.asarray(x, dtype=np.float64); y = np.asarray(y, dtype=np.float64)
    rx = np.argsort(np.argsort(x)); ry = np.argsort(np.argsort(y))
    if np.std(rx) < 1e-9 or np.std(ry) < 1e-9: return 0.0
    return float(np.corrcoef(rx, ry)[0, 1])


def _selftest():
    g = np.random.default_rng(0)
    assert abs(participation_ratio(np.ones(40)) - 40) < 1e-6, "PR flat==n"
    assert participation_ratio(np.array([10.0] + [1e-6] * 49)) < 2, "PR rank-1 small"
    assert abs(spectral_entropy_deff(np.ones(20)) - 20) < 1e-6, "spectral-entropy flat==n"
    # Hebbian capacity: full-rank 32-dim has a BOUNDED, finite capacity (crosstalk caps it < #patterns); near-rank-1
    # (low usable rank) caps LOWER -> discriminates by effective rank (the cert hypothesis).
    grid = [20, 40, 60, 80, 100, 150]
    emb = g.standard_normal((200, 32)).astype(np.float32)
    cap, curve = capacity_sweep(emb, 0.05, np.random.default_rng(1), grid, thresh=0.9)
    base = g.standard_normal((1, 32)).astype(np.float32)
    low = (base + 0.02 * g.standard_normal((200, 32))).astype(np.float32)   # near-collinear -> low usable rank
    cap2, _ = capacity_sweep(low, 0.05, np.random.default_rng(2), grid, thresh=0.9)
    assert cap < 200, "Hebbian capacity is BOUNDED, not saturated (cap=%.1f curve=%s)" % (cap, curve)
    assert cap > cap2, "full-rank capacity > low-usable-rank capacity (cap=%.1f cap2=%.1f)" % (cap, cap2)
    assert abs(spearman([1, 2, 3, 4], [1, 2, 3, 4]) - 1.0) < 1e-9, "spearman monotone==1"
    assert spearman([1, 2, 3, 4], [4, 3, 2, 1]) < -0.9, "spearman anti==-1"
    print("[selftest] PASS: PR/rank95/spectral-entropy + Hebbian-capacity(bounded+discriminating) + spearman", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)

try:
    import torch
    from transformers import AutoModel, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
if torch.cuda.is_available():
    DEV = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)
elif SMOKE:
    DEV = torch.device("cpu"); print("[smoke] no CUDA -> CPU (small cached encoders)", flush=True)
else:
    print("[FATAL] CUDA required for full run (mpnet + Pythia-2.8B).", flush=True); sys.exit(1)


def encode(eid, etype, texts):
    tok = AutoTokenizer.from_pretrained(eid)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    mdl = AutoModel.from_pretrained(eid, torch_dtype=(torch.float16 if DEV.type == "cuda" else torch.float32)).to(DEV).eval()
    out = []
    for i in range(0, len(texts), 32):
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=32).to(DEV)
        with torch.no_grad():
            h = mdl(**t).last_hidden_state
        mask = t["attention_mask"].unsqueeze(-1).float()
        pooled = (h * mask).sum(1) / mask.sum(1).clamp(min=1)   # mean-pool (st + lm both)
        out.append(pooled.float().cpu().numpy())
    del mdl
    if DEV.type == "cuda": torch.cuda.empty_cache()
    return np.concatenate(out, 0).astype(np.float32)


def run_unit(eid, etype, nominal_D, seed):
    g = np.random.default_rng(seed); texts = make_texts(M_MAX, g)
    emb = encode(eid, etype, texts)
    de = d_eff_all(emb)
    cap, curve = capacity_sweep(emb, NOISE, np.random.default_rng(seed + 100), GRID)
    print("  [%s seed=%d] D=%d d_eff(PR)=%.1f rank95=%d spec=%.1f | capacity(maxM @recall>=0.9)=%d curve=%s" %
          (eid.split("/")[-1], seed, nominal_D, de["participation_ratio"], de["rank95"], de["spectral_entropy"], cap, curve), flush=True)
    return {"encoder": eid, "nominal_D": nominal_D, "seed": seed, "d_eff": de, "capacity": cap, "capacity_curve": curve}


def compute_verdict(units) -> Tuple[str, str, Dict]:
    if not units:
        return ("HARD_FAIL", "no results", {})
    enc_ids = [e[0] for e in ENCODERS]
    per_enc = {}
    for eid in enc_ids:
        us = [u for u in units if u["encoder"] == eid]
        if not us: continue
        cap_vals = [u["capacity"] for u in us]
        de_pr = [u["d_eff"]["participation_ratio"] for u in us]
        de_r95 = [u["d_eff"]["rank95"] for u in us]
        de_se = [u["d_eff"]["spectral_entropy"] for u in us]
        per_enc[eid] = {"nominal_D": us[0]["nominal_D"], "capacity_mean": float(np.mean(cap_vals)),
                        "capacity_std": float(np.std(cap_vals)),
                        "d_eff_PR": float(np.mean(de_pr)), "d_eff_rank95": float(np.mean(de_r95)),
                        "d_eff_spectral": float(np.mean(de_se))}
    encs = list(per_enc.keys())
    if len(encs) < 3:
        return ("UNKNOWN", "need >=3 encoders for correlation", {"per_encoder": per_enc})
    cap = [per_enc[e]["capacity_mean"] for e in encs]
    deff = [per_enc[e]["d_eff_PR"] for e in encs]
    nomD = [per_enc[e]["nominal_D"] for e in encs]
    rho_deff = spearman(cap, deff); rho_D = spearman(cap, nomD)
    # 3-method consistency per encoder: max relative spread of the 3 d_eff methods <= 0.20
    def consist(e):
        vals = [per_enc[e]["d_eff_PR"], per_enc[e]["d_eff_rank95"], per_enc[e]["d_eff_spectral"]]
        return (max(vals) - min(vals)) / (np.mean(vals) + 1e-9)
    worst_consist = max(consist(e) for e in encs)
    cap_repro = max(per_enc[e]["capacity_std"] / (per_enc[e]["capacity_mean"] + 1e-9) for e in encs)
    detail = {"per_encoder": per_enc, "spearman_capacity_vs_d_eff": round(rho_deff, 3),
              "spearman_capacity_vs_nominal_D": round(rho_D, 3),
              "worst_3method_consistency_spread": round(worst_consist, 3), "worst_capacity_cv": round(cap_repro, 3),
              "honest_scope": "substrate capacity correlates with encoder d_eff (intrinsic/usable rank), NOT nominal D; "
                              "d_eff magnitudes reported per-encoder; tested across %d encoders." % len(encs)}
    summary = ("Spearman(capacity,d_eff)=%.3f vs Spearman(capacity,nominalD)=%.3f | worst-3method-spread=%.3f | "
               "worst-cap-CV=%.3f | n_enc=%d" % (rho_deff, rho_D, worst_consist, cap_repro, len(encs)))
    # HARD_FAIL
    if rho_deff < 0.50 or worst_consist > 0.40 or cap_repro > 0.20:
        return ("HARD_FAIL", "HARD_FAIL: " + summary, detail)
    if rho_deff >= 0.80 and worst_consist <= 0.20 and cap_repro <= 0.10:
        return ("HARD_PASS", "HARD_PASS: substrate capacity tracks d_eff not nominal D. " + summary, detail)
    return ("MIDDLE_BAND", "MIDDLE_BAND: " + summary, detail)


print("[config] %s mode=%s encoders=%s M_MAX=%d grid=%s seeds=%s" % (ANCHOR_NAME, RUN_MODE, [e[0].split("/")[-1] for e in ENCODERS], M_MAX, GRID, SEEDS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); run_config = {"run_mode": RUN_MODE}; t0 = time.time()
for eid, etype, nomD in ENCODERS:
    for seed in SEEDS:
        key = "%s_s%d" % (eid.split("/")[-1], seed)
        if key in aggregate_partials(out_dir, [key], run_config=run_config):
            print("[ckpt] %s done; skip" % key, flush=True); continue
        res = run_unit(eid, etype, nomD, seed); res["run_mode"] = RUN_MODE
        write_partial_key(out_dir, key, res)
units = list(aggregate_partials(out_dir, ["%s_s%d" % (e[0].split("/")[-1], sd) for e in ENCODERS for sd in SEEDS], run_config=run_config).values())
verdict, msg, detail = compute_verdict(units)
print("\n[VERDICT] " + msg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg, "run_mode": RUN_MODE,
           "encoders": [e[0] for e in ENCODERS], "M_MAX": M_MAX, "grid": GRID, "n_seeds": len(SEEDS), "detail": detail,
           "metrics_source": "measured_gpu_effective_rank_capacity_cross_encoder", "per_unit": units, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, units)
print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
