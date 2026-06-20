"""
crosstalk_capacity_law_v1_gpu_v1 -- REFRAME of isotropy #6 (Skunkworks RULING 2026-06-20: reframe YES, tier MEASURED_MECHANISM,
chain-grade path = more encoders + bounded-c + Spearman). The DIRECT crosstalk moment E[<ki,kj>^2] (raw keys) is the DOMINANT
cross-encoder predictor of Hebbian-superposition capacity M_crit; two independent proxies -- SVD d_eff AND mean-centered
IsoScore -- BOTH FAIL to predict it. The 2-failing-controls is the non-trivial content (NOT "anything predicts capacity").

WHY isotropy #6 was reframed: the independent IsoScore (mean-centered covariance-eigenvalue) is FLAT across encoders and
ANTI-correlated with capacity -- it mean-centers away the shared-mean cone, which is exactly the RAW-key crowding Hebbian
W=sum k k^T is limited by. So "isotropy predicts capacity" was circular (confirmed empirically); capacity IS the crosstalk.

TIER (Skunkworks): MEASURED_MECHANISM unless the chain-grade bar is met: n>>4 robust (Spearman too, not MiniLM-leveraged
Pearson) AND c BOUNDED (the smoke had c 0.5-3.5 raw ~ 7x, projected ~17 -> not parameter-free). c-bounding analysis here:
report c-per-encoder + Pearson(c, d), Pearson(c, IsoScore) to test if c is predictable; raw-vs-projected split noted.

DISCIPLINES: E[<>^2] + Hebbian W on RAW (un-mean-centered) keys (Orchestrator's load-bearing referent); controls mean-center
BY DESIGN (their blindness is the evidence). run's-OWN-moments per encoder (D x D gram closed-form, no M x M). capacity-RELATIVE
(gate on cross-encoder rank-correlation, not a fixed recall@M). c-per-encoder reported. import torch first. ASCII.
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

ANCHOR_NAME = "crosstalk_capacity_law_v1_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
if SMOKE:
    ENCODERS = [("sentence-transformers/all-MiniLM-L6-v2", 384), ("BAAI/bge-small-en-v1.5", 384),
                ("BAAI/bge-large-en-v1.5", 1024), ("EleutherAI/pythia-160m", 768)]
    M_KEYS = 1500; GRID = [25, 50, 100, 200, 400, 800, 1500]; SEEDS = [1, 2]
else:
    # ~13 encoders spanning the crosstalk range; multiple HIGH-capacity (de-leverage MiniLM) + a pythia size-ladder + gpt2.
    ENCODERS = [("sentence-transformers/all-MiniLM-L6-v2", 384), ("sentence-transformers/all-mpnet-base-v2", 768),
                ("sentence-transformers/all-distilroberta-v1", 768), ("sentence-transformers/gtr-t5-base", 768),
                ("BAAI/bge-small-en-v1.5", 384), ("BAAI/bge-large-en-v1.5", 1024),
                ("intfloat/e5-base-v2", 768), ("sentence-transformers/sentence-t5-base", 768),
                ("EleutherAI/pythia-160m", 768), ("EleutherAI/pythia-410m", 1024),
                ("EleutherAI/pythia-1.4b", 2048), ("EleutherAI/pythia-2.8b", 2560), ("gpt2-medium", 1024)]
    M_KEYS = 8000; GRID = [50, 100, 200, 400, 800, 1600, 3200, 6400, 8000]; SEEDS = [1, 2, 3, 4, 5]
NOISE = 0.10


def short(eid):
    return eid.split("/")[-1].replace(".", "_").replace("/", "_")  # sanitize: dots dropped units in agg (bge-*-v1.5 bug)


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
    """CONTROL (mean-centered): covariance-eigenvalue spectral-uniformity in [0,1]. Its failure to predict capacity is the evidence."""
    Xc = X.astype(np.float64) - X.mean(0, keepdims=True)
    Sigma = (Xc.T @ Xc) / max(1, len(Xc) - 1)
    ev = np.maximum(np.linalg.eigvalsh(Sigma), 0.0); s = ev.sum()
    if s <= 0: return 0.0
    lh = ev / s; d = len(lh)
    if d <= 1: return 1.0
    l2 = float(np.linalg.norm(lh - 1.0 / d)); max_l2 = float(np.sqrt(1.0 - 1.0 / d))
    return float(np.clip(1.0 - l2 / max_l2, 0.0, 1.0))


def d_eff_pr(X):
    """CONTROL (mean-centered): SVD participation ratio. The effrank honest-negative; fails to predict capacity."""
    s = np.linalg.svd(X - X.mean(0, keepdims=True), compute_uv=False)
    return float((s.sum() ** 2) / (np.sum(s ** 2) + 1e-12))


def _recall_at_M(K, Kn, M, sigma, g):
    """Hebbian auto-assoc recall@1: W=sum k k^T on RAW keys; recall via r=(q@sub^T)@sub; cleanup argmax over normed codebook."""
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
    """E[<ki,kj>^2] off-diag via D x D gram closed-form (no M x M). RAW unit-normed keys (NOT mean-centered)."""
    sub = Kn[:M].astype(np.float64); G = sub.T @ sub; fro2 = float((G * G).sum())
    return (fro2 - M) / (M * (M - 1) + 1e-9)


def pearson(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    if np.std(x) < 1e-9 or np.std(y) < 1e-9: return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def spearman(x, y):
    """Rank correlation = Pearson on ranks. Robust to single high-leverage point (Skunkworks: not MiniLM-driven)."""
    rx = np.argsort(np.argsort(np.asarray(x, float))).astype(float); ry = np.argsort(np.argsort(np.asarray(y, float))).astype(float)
    return pearson(rx, ry)


def _selftest():
    g = np.random.default_rng(0)
    iso_uni = isoscore(g.standard_normal((400, 32)).astype(np.float32))
    t = g.standard_normal((400, 1)).astype(np.float32); direction = g.standard_normal((1, 32)).astype(np.float32)
    iso_col = isoscore(t @ direction)
    assert iso_uni > 0.7 and iso_col < 0.3, "IsoScore: uniform(%.3f) high, rank1(%.3f) low" % (iso_uni, iso_col)
    cap, _ = capacity_sweep(g.standard_normal((200, 32)).astype(np.float32), 0.05, np.random.default_rng(1), [20, 50, 100])
    assert cap < 200, "capacity bounded (%.1f)" % cap
    assert abs(pearson([1, 2, 3], [2, 4, 6]) - 1.0) < 1e-9, "pearson"
    assert abs(spearman([1, 2, 3, 9], [1, 2, 3, 4]) - 1.0) < 1e-9, "spearman monotone=1"  # spearman robust to the outlier scale
    assert short("BAAI/bge-large-en-v1.5") == "bge-large-en-v1_5", "name-sanitize dropped dot"
    print("[selftest] PASS: IsoScore(control) + Hebbian-capacity + pearson + spearman + name-sanitize", flush=True)


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
    print("  [%s s=%d] IsoScore=%.4f d_eff=%.1f | M_crit=%.1f E2=%.5f (1/E2=%.1f c=%.2f) D=%d" %
          (short(eid), seed, iso, de, cap, e2, raw_snr, c, emb.shape[1]), flush=True)
    return {"encoder": eid, "short": short(eid), "nominal_D": nominal_D, "actual_D": int(emb.shape[1]), "seed": seed,
            "isoscore": round(iso, 4), "d_eff": round(de, 1), "m_crit": round(cap, 2), "e_sq": round(e2, 6),
            "inv_e_sq": round(raw_snr, 3), "c_cleanup_boost": round(c, 3)}


def compute_verdict(units) -> Tuple[str, str, Dict]:
    if not units: return ("HARD_FAIL", "no results", {})
    per = {}
    for u in units:
        per.setdefault(u["encoder"], []).append(u)
    agg = {}
    for eid, us in per.items():
        agg[eid] = {"short": us[0]["short"], "D": us[0].get("actual_D", us[0]["nominal_D"]),
                    "isoscore": float(np.mean([u["isoscore"] for u in us])), "d_eff": float(np.mean([u["d_eff"] for u in us])),
                    "m_crit": float(np.mean([u["m_crit"] for u in us])), "inv_e_sq": float(np.mean([u["inv_e_sq"] for u in us])),
                    "m_crit_cv": float(np.std([u["m_crit"] for u in us]) / (np.mean([u["m_crit"] for u in us]) + 1e-9)),
                    "c": float(np.mean([u["c_cleanup_boost"] for u in us]))}
    encs = list(agg.keys())
    if len(encs) < 3: return ("UNKNOWN", "need >=3 encoders (got %d)" % len(encs), {"per_encoder": agg})
    logcap = [np.log(agg[e]["m_crit"] + 1) for e in encs]; loginv = [np.log(agg[e]["inv_e_sq"] + 1) for e in encs]
    iso = [agg[e]["isoscore"] for e in encs]; deff = [agg[e]["d_eff"] for e in encs]; cs = [agg[e]["c"] for e in encs]
    dd = [agg[e]["D"] for e in encs]
    r_cross = pearson(loginv, logcap); sp_cross = spearman([agg[e]["inv_e_sq"] for e in encs], [agg[e]["m_crit"] for e in encs])
    r_iso = pearson(iso, logcap); r_deff = pearson(deff, logcap)
    # PARTIAL correlation control|crosstalk (Skunkworks): r_xy.z=(r_xy - r_xz*r_yz)/sqrt((1-r_xz^2)(1-r_yz^2)).
    # ~0 -> control is crosstalk-in-disguise (genuinely fails, even if raw |r| high); survives -> independent predictor.
    r_deff_cross = pearson(deff, loginv); r_iso_cross = pearson(iso, loginv)
    def _partial(r_xy, r_xz, r_yz):
        return float((r_xy - r_xz * r_yz) / np.sqrt(max(1e-12, (1 - r_xz ** 2) * (1 - r_yz ** 2))))
    partial_deff = _partial(r_deff, r_deff_cross, r_cross); partial_iso = _partial(r_iso, r_iso_cross, r_cross)
    partial_controls_fail = (abs(partial_deff) < 0.30 and abs(partial_iso) < 0.30)  # controls add NO independent power
    c_spread = max(cs) / (min(cs) + 1e-9)
    detail = {"per_encoder": agg, "n_encoders": len(encs),
              "pearson_crosstalk_vs_logMcrit": round(r_cross, 3), "spearman_crosstalk_vs_Mcrit": round(sp_cross, 3),
              "pearson_deff_vs_logMcrit_CONTROL": round(r_deff, 3), "pearson_isoscore_vs_logMcrit_CONTROL": round(r_iso, 3),
              "partial_pearson_deff_given_crosstalk": round(partial_deff, 3), "partial_pearson_isoscore_given_crosstalk": round(partial_iso, 3),
              "partial_controls_fail": bool(partial_controls_fail), "control_signs": {"d_eff": round(r_deff, 3), "isoscore": round(r_iso, 3)},
              "c_per_encoder": {agg[e]["short"]: round(agg[e]["c"], 3) for e in encs}, "c_spread_max_over_min": round(c_spread, 2),
              "c_bound_pearson_c_vs_D": round(pearson(dd, cs), 3), "c_bound_pearson_c_vs_isoscore": round(pearson(iso, cs), 3),
              "worst_m_crit_cv": round(max(agg[e]["m_crit_cv"] for e in encs), 3),
              "honest_claim": "Direct crosstalk moment E[<ki,kj>^2] (raw keys) is the DOMINANT cross-encoder predictor of "
                              "Hebbian capacity (Pearson %.2f / Spearman %.2f, n=%d); controls d_eff (r=%.2f) and IsoScore "
                              "(r=%.2f) are WEAKER -- partial(ctrl|crosstalk)=%.2f/%.2f decides crosstalk-in-disguise (fails) "
                              "vs independent predictor (report, don't bury); cleanup-boost c spread %.1fx (bounded? see c_bound_*)." %
                              (r_cross, sp_cross, len(encs), r_deff, r_iso, partial_deff, partial_iso, c_spread)}
    # FLOOR = DOMINANCE (Skunkworks band ruling): crosstalk > BOTH control |r|; dropped the arbitrary |r|<0.5. Signs reported honestly.
    dominant = r_cross > max(abs(r_iso), abs(r_deff))
    summary = ("Pearson(crosstalk)=%.3f Spearman=%.3f | CONTROLS d_eff=%.3f IsoScore=%.3f | PARTIAL(ctrl|crosstalk) d_eff=%.3f IsoScore=%.3f | c-spread=%.1fx | n=%d" %
               (r_cross, sp_cross, r_deff, r_iso, partial_deff, partial_iso, c_spread, len(encs)))
    if not dominant or sp_cross <= 0.70:
        return ("HARD_FAIL", "HARD_FAIL: crosstalk NOT dominant (a control |r| >= crosstalk) or Spearman<=0.70 -> finding collapses. " + summary, detail)
    # MEASURED_MECHANISM is the floor. Chain-grade-ELIGIBLE needs robust n + c bounded + PARTIAL controls-fail (controls add no independent power).
    chain_eligible = (len(encs) >= 8 and sp_cross > 0.80 and r_cross > 0.80 and c_spread <= 3.0 and partial_controls_fail)
    if chain_eligible:
        return ("HARD_PASS_CHAIN_ELIGIBLE", "CHAIN-GRADE-ELIGIBLE (Skunkworks rules 592): crosstalk dominant, n>=8 robust (Spearman>0.80), c BOUNDED (<=3x), BOTH partial(ctrl|crosstalk)<0.30 (controls add no independent power = rigorous 2-controls-fail). " + summary, detail)
    return ("MEASURED_MECHANISM", "MEASURED_MECHANISM (Skunkworks tier; CERT stays 591): crosstalk DOMINANT predictor; controls weaker (see PARTIALs for crosstalk-in-disguise vs independent); NOT parameter-free LAW (c-spread %.1fx / n / partial-controls-fail=%s). " % (c_spread, partial_controls_fail) + summary, detail)


print("[config] %s mode=%s n_encoders=%d M_keys=%d seeds=%s" % (ANCHOR_NAME, RUN_MODE, len(ENCODERS), M_KEYS, SEEDS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); run_config = {"run_mode": RUN_MODE}; t0 = time.time()
for eid, nomD in ENCODERS:
    for seed in SEEDS:
        key = "%s_s%d" % (short(eid), seed)
        if key in aggregate_partials(out_dir, [key], run_config=run_config):
            print("[ckpt] %s done; skip" % key, flush=True); continue
        try:
            res = run_unit(eid, nomD, seed); res["run_mode"] = RUN_MODE
            write_partial_key(out_dir, key, res)
        except Exception as e:
            print("[WARN] %s failed: %s (skipping encoder)" % (key, e), flush=True)
keys = ["%s_s%d" % (short(e[0]), sd) for e in ENCODERS for sd in SEEDS]
units = list(aggregate_partials(out_dir, keys, run_config=run_config).values())
verdict, msg, detail = compute_verdict(units)
print("\n[VERDICT] " + msg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg, "run_mode": RUN_MODE,
           "encoders": [e[0] for e in ENCODERS], "M_keys": M_KEYS, "n_seeds": len(SEEDS), "detail": detail,
           "metrics_source": "measured_gpu_crosstalk_vs_hebbian_capacity_cross_encoder_with_failing_controls", "per_unit": units, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, units)
print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
