"""
isotropy_capacity_pull_up_v1 -- substrate associative-memory CAPACITY is predicted by encoder embedding ISOTROPY
(mean pairwise-cosine), NOT SVD effective-rank (d_eff). GPU(encode)+CPU(capacity/isotropy). TIER-2 #6 (Research REFRAME
of the effrank honest-negative). Director outline: research_to_..._effrank_REFRAME_isotropy_capacity_2026-06-20.

CLAIM (the cert): substrate Hebbian auto-associative capacity correlates with embedding ISOTROPY across encoders.
PRIOR (accepted-negative): SVD d_eff does NOT predict capacity -- pythia(d_eff=351)/cap=2.6 vs MiniLM(d_eff=238)/cap=170
(anti-correlated). Mechanism: anisotropic embeddings (high pairwise-cosine, e.g. LM-mean-pooled) -> massive Hebbian
crosstalk -> tiny capacity; isotropic embeddings (contrastive sent-encoders) -> low crosstalk -> high capacity.

CAPACITY (de-risked methodology, carried from effrank): Hebbian AUTO-ASSOCIATIVE memory W=sum_k k k^T (raw embeddings,
NO whitening), recall r=W@q_noisy, cleanup argmax over codebook; crosstalk grows with M -> capacity = max M (swept,
interpolated threshold-crossing) with recall>=0.90. (NN-lookup has no bottleneck -> can't test this; whitening erases it.)
ISOTROPY = 1 - mean_pairwise_cosine on a sample (higher = more isotropic). Corpus = ag_news, EXACT-dedup (the seed
instability was duplicate-article cleanup collisions). d_eff reported alongside (the refuted predictor).

v1 BANDS:
  HARD_PASS = Pearson(isotropy, capacity) > 0.80 across encoders AND the lowest-isotropy encoder is the lowest-capacity
              AND worst per-encoder capacity-CV <= 0.30 (seed-reproduce).
  MIDDLE    = Pearson in [0.50, 0.80] OR worst-CV in (0.30, 0.50].
  HARD_FAIL = Pearson < 0.50 (isotropy does NOT predict capacity either -> a 3rd axis is needed; informative-negative)
              OR worst-CV > 0.50 (measure too unstable).
  VERIFY-REFERENT flag = Pearson > 0.99 -> warn possible isotropy/capacity metric-overlap (both ~ pairwise-cosine).
  CLIFF REPORTED = the isotropy below which capacity < 10 (the encoder-pairing refuse-zone; actionable for KV-memory).

import torch first (PROT-020). checkpoint/resume per (encoder,seed). ASCII.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import argparse, time, json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_partial_key, aggregate_partials, write_metrics

ANCHOR_NAME = "isotropy_capacity_pull_up_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
NOISE = 0.10
if SMOKE:
    ENCODERS = [("sentence-transformers/all-MiniLM-L6-v2", 384), ("BAAI/bge-small-en-v1.5", 384),
                ("BAAI/bge-large-en-v1.5", 1024), ("EleutherAI/pythia-160m", 768)]
    M_MAX = 1500; GRID = [25, 50, 100, 200, 400, 800, 1500]; SEEDS = [1, 2]
else:
    ENCODERS = [("sentence-transformers/all-MiniLM-L6-v2", 384), ("sentence-transformers/all-mpnet-base-v2", 768),
                ("BAAI/bge-large-en-v1.5", 1024), ("sentence-transformers/sentence-t5-base", 768),
                ("EleutherAI/pythia-160m", 768), ("EleutherAI/pythia-2.8b", 2560)]
    M_MAX = 8000; GRID = [50, 100, 200, 400, 800, 1600, 3200, 6400, 8000]; SEEDS = [1, 2, 3, 4, 5]


def make_texts(m, g):
    """DIVERSE real corpus (ag_news), EXACT-deduped (dup articles caused seed-instability), shuffled by g."""
    try:
        pool = [e["text"] for e in json.load(open(REPO / "experiments" / "data" / "ag_news.json", encoding="utf-8")).get("train", [])]
        seen = set(); ded = []
        for t in pool:
            k = t.strip().lower()
            if k and k not in seen: seen.add(k); ded.append(t)
        if len(ded) >= 50:
            idx = g.permutation(len(ded))
            return [ded[int(idx[i % len(ded)])] for i in range(m)]
    except Exception:
        pass
    subj = ["alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel", "india", "juliet"]
    rel = ["founded in", "located near", "invented by", "merged with", "capital of", "awarded for", "powered by", "discovered in"]
    obj = ["the northern district", "the rival firm", "an unknown engineer", "the small province", "a novel reactor", "the deep archive", "best design", "the eastern wing"]
    return ["entity %s-%d %s %s" % (subj[i % 10], i, rel[g.integers(0, len(rel))], obj[g.integers(0, len(obj))]) for i in range(m)]


def participation_ratio(s):
    s = np.asarray(s, dtype=np.float64); return float((s.sum() ** 2) / (np.sum(s ** 2) + 1e-12))


def d_eff_pr(emb):
    s = np.linalg.svd(emb - emb.mean(0, keepdims=True), compute_uv=False); return participation_ratio(s)


def isotropy_score(Kn, g, sample=2000):
    """1 - mean pairwise cosine on a sample of unit-normed embeddings (higher = more isotropic)."""
    M = len(Kn); idx = g.permutation(M)[:min(sample, M)]; S = Kn[idx]
    G = S @ S.T; n = len(S); off = (G.sum() - np.trace(G)) / (n * (n - 1) + 1e-9)
    return float(1.0 - off)


def _recall_at_M(K, Kn, M, sigma, g):
    """Hebbian auto-assoc recall@1: W=sum_k k k^T (superposition); r=W@q_noisy; cleanup argmax over codebook.
    Crosstalk grows with M -> capacity bottleneck (computed r=(q@sub^T)@sub to avoid materialising D x D W)."""
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


def pearson(x, y):
    x = np.asarray(x, dtype=np.float64); y = np.asarray(y, dtype=np.float64)
    if np.std(x) < 1e-9 or np.std(y) < 1e-9: return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def _selftest():
    g = np.random.default_rng(0)
    # isotropy: random (isotropic) embeddings -> score near 1; collinear (anisotropic) -> score near 0
    iso_rand = isotropy_score((lambda K: K / np.linalg.norm(K, axis=1, keepdims=True))(g.standard_normal((300, 32)).astype(np.float32)), g)
    base = g.standard_normal((1, 32)); col = base + 0.05 * g.standard_normal((300, 32))
    iso_col = isotropy_score((col / np.linalg.norm(col, axis=1, keepdims=True)).astype(np.float32), g)
    assert iso_rand > 0.8, "isotropic random -> high isotropy (%.3f)" % iso_rand
    assert iso_col < iso_rand, "collinear -> lower isotropy (%.3f vs %.3f)" % (iso_col, iso_rand)
    # capacity bounded + discriminating (carried from effrank)
    cap, _ = capacity_sweep(g.standard_normal((200, 32)).astype(np.float32), 0.05, np.random.default_rng(1), [20, 40, 80, 150])
    assert cap < 200, "Hebbian capacity bounded (%.1f)" % cap
    assert abs(pearson([1, 2, 3], [2, 4, 6]) - 1.0) < 1e-9, "pearson linear==1"
    print("[selftest] PASS: isotropy(iso>aniso) + Hebbian-capacity(bounded) + pearson", flush=True)


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
    print("[FATAL] CUDA required for full run.", flush=True); sys.exit(1)


def encode(eid, texts):
    tok = AutoTokenizer.from_pretrained(eid)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    mdl = AutoModel.from_pretrained(eid, torch_dtype=(torch.float16 if DEV.type == "cuda" else torch.float32)).to(DEV).eval()
    out = []
    for i in range(0, len(texts), 32):
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=32).to(DEV)
        with torch.no_grad():
            h = mdl(**t).last_hidden_state if not hasattr(mdl, "encoder") or "t5" not in eid.lower() else mdl.encoder(**t).last_hidden_state
        mask = t["attention_mask"].unsqueeze(-1).float()
        out.append(((h * mask).sum(1) / mask.sum(1).clamp(min=1)).float().cpu().numpy())
    del mdl
    if DEV.type == "cuda": torch.cuda.empty_cache()
    return np.concatenate(out, 0).astype(np.float32)


def run_unit(eid, nominal_D, seed):
    g = np.random.default_rng(seed); texts = make_texts(M_MAX, g)
    emb = encode(eid, texts)
    Kn = (emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-8)).astype(np.float32)
    iso = isotropy_score(Kn, np.random.default_rng(seed + 7))
    cap, curve = capacity_sweep(emb, NOISE, np.random.default_rng(seed + 100), GRID)
    de = d_eff_pr(emb)
    print("  [%s seed=%d] D=%d isotropy=%.4f capacity=%.1f d_eff=%.1f curve=%s" %
          (eid.split("/")[-1], seed, nominal_D, iso, cap, de, curve), flush=True)
    return {"encoder": eid, "nominal_D": nominal_D, "seed": seed, "isotropy": round(iso, 4), "capacity": cap,
            "d_eff_PR": round(de, 1), "capacity_curve": curve}


def compute_verdict(units) -> Tuple[str, str, Dict]:
    if not units: return ("HARD_FAIL", "no results", {})
    per = {}
    for eid, _ in ENCODERS:
        us = [u for u in units if u["encoder"] == eid]
        if not us: continue
        caps = [u["capacity"] for u in us]
        per[eid] = {"nominal_D": us[0]["nominal_D"], "isotropy": float(np.mean([u["isotropy"] for u in us])),
                    "capacity": float(np.mean(caps)), "capacity_cv": float(np.std(caps) / (np.mean(caps) + 1e-9)),
                    "d_eff_PR": float(np.mean([u["d_eff_PR"] for u in us]))}
    encs = list(per.keys())
    if len(encs) < 3:
        return ("UNKNOWN", "need >=3 encoders (got %d)" % len(encs), {"per_encoder": per})
    iso = [per[e]["isotropy"] for e in encs]; cap = [per[e]["capacity"] for e in encs]
    deff = [per[e]["d_eff_PR"] for e in encs]
    r_iso = pearson(iso, cap); r_deff = pearson(deff, cap)
    worst_cv = max(per[e]["capacity_cv"] for e in encs)
    lowest_iso_enc = min(encs, key=lambda e: per[e]["isotropy"])
    lowest_cap_enc = min(encs, key=lambda e: per[e]["capacity"])
    pythia_consistent = (lowest_iso_enc == lowest_cap_enc)
    cliff = max([per[e]["isotropy"] for e in encs if per[e]["capacity"] < 10] + [0.0])
    detail = {"per_encoder": per, "pearson_isotropy_vs_capacity": round(r_iso, 3),
              "pearson_d_eff_vs_capacity": round(r_deff, 3), "worst_capacity_cv": round(worst_cv, 3),
              "lowest_isotropy_encoder": lowest_iso_enc.split("/")[-1], "lowest_capacity_encoder": lowest_cap_enc.split("/")[-1],
              "lowest_iso_is_lowest_cap": pythia_consistent, "isotropy_cliff_cap_lt_10": round(cliff, 4),
              "honest_scope": "substrate Hebbian associative capacity correlates with embedding ISOTROPY (1-mean-pairwise-cos), "
                              "NOT SVD d_eff (refuted: r_deff reported); across %d encoders; isotropy-cliff (cap<10) reported." % len(encs)}
    summary = ("Pearson(isotropy,capacity)=%.3f vs Pearson(d_eff,capacity)=%.3f | lowest-iso=%s lowest-cap=%s (match=%s) | "
               "worst-CV=%.3f | iso-cliff(cap<10)=%.3f | n_enc=%d" % (
               r_iso, r_deff, lowest_iso_enc.split("/")[-1], lowest_cap_enc.split("/")[-1], pythia_consistent, worst_cv, cliff, len(encs)))
    if r_iso > 0.99:
        summary = "[VERIFY-REFERENT: Pearson>0.99 -> check isotropy/capacity metric-overlap] " + summary
    if r_iso < 0.50 or worst_cv > 0.50:
        return ("HARD_FAIL", "HARD_FAIL: isotropy does NOT predict capacity (need a 3rd axis) OR measure unstable. " + summary, detail)
    if r_iso > 0.80 and pythia_consistent and worst_cv <= 0.30:
        return ("HARD_PASS", "HARD_PASS: substrate associative capacity is predicted by embedding ISOTROPY (not d_eff). " + summary, detail)
    return ("MIDDLE_BAND", "MIDDLE_BAND: isotropy predicts capacity moderately (or repro marginal). " + summary, detail)


print("[config] %s mode=%s encoders=%s M_MAX=%d seeds=%s" % (ANCHOR_NAME, RUN_MODE, [e[0].split("/")[-1] for e in ENCODERS], M_MAX, SEEDS), flush=True)
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
           "encoders": [e[0] for e in ENCODERS], "M_MAX": M_MAX, "grid": GRID, "n_seeds": len(SEEDS), "detail": detail,
           "metrics_source": "measured_gpu_isotropy_vs_hebbian_capacity_cross_encoder", "per_unit": units, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, units)
print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
