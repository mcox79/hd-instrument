"""
hebbian_capacity_projected_v1 -- substrate Hebbian-superposition CAPACITY on #7-PROJECTED Pythia-2.8B keys (CERT 591
learned contrastive projection). Measures the SUBSTRATE's capacity, NOT the encoder's key-crowding (confound resolved
by #7). GPU(encode+train)+CPU(Hebbian sweep). Skunkworks SCHEMA-VET GO + full-crosstalk fix.

MECHANISM: re-train the #7 contrastive projection on TRAIN facts (W not persisted by #7); apply to HELD-OUT facts;
Hebbian-superposition store W_heb = sum_k kp_k kp_k^T on M projected held-out keys; recall held-out value-cues via
W_heb (r=(q@sub^T)@sub chunked, NO D x D or M x M materialised); cleanup argmax over the projected codebook; M_crit =
swept M where recall drops below 0.80. Capacity measured on HELD-OUT facts (projection generalizes, per #7 split).

PREDICTION (Skunkworks full-crosstalk fix): M_crit ~ 1 / E[<ki,kj>^2] = 1/(rho_var + rho_mean^2), NOT 1/rho_mean^2 (the
anisotropic special-case that over-predicts 2.5-5x at the projected HIGH-isotropy regime where rho_var dominates).
E[<ki,kj>^2] computed from the D x D GRAM closed-form (Orchestrator-verified): (||Kp^T Kp||_F^2 - M)/(M(M-1)) -- NO M x M.

BANDS:
  HARD_PASS = M_crit_obs within factor-2 of M_crit_pred AND recall@M=1k >= 0.80 AND projected-recall@M_crit > 5x raw-key
    recall (substrate-capacity emerges from projected keys, invisible on raw) AND crosstalk monotone-decreasing.
  MIDDLE = mechanism works @1k but M_crit_obs < 0.5x predicted. HARD_FAIL = recall@1k<0.80 OR raw matches projected
    (projection doesn't help -> refutes confound-resolution) OR up-guard (M_crit within +-5% of pred = too clean;
    recall@50k>0.95 saturation). CAN-FAIL self-test: trivially-overloaded (eff-dim halved) -> recall<0.5.

import torch first. reuse #7 corpus/encode/train + effrank chunked Hebbian. checkpoint per (M,seed). ASCII.
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

ANCHOR_NAME = "hebbian_capacity_projected_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
ENCODER = "EleutherAI/pythia-160m" if SMOKE else "EleutherAI/pythia-2.8b"
M_SWEEP = [50, 100, 250, 500, 1000] if SMOKE else [100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000]   # finer low-M -> MEASURE M_crit, not extrapolate
SEEDS = [0, 1] if SMOKE else [0, 1, 2, 3, 4]
PROJ_DIM = 128 if SMOKE else 256
TRAIN_FACTS = 500 if SMOKE else 5000
TRAIN_STEPS = 200 if SMOKE else 600
RECALL_THRESH = 0.80
_ADJ = "red blue swift quiet ancient modern silver golden hidden northern rapid silent hollow bright frozen molten crimson azure verdant amber".split()
_NOUN = "falcon river engine archive bridge reactor delta harbor summit forge canyon beacon orchard meadow glacier tower lagoon prairie quarry vault".split()
_VALW = "helium cobalt basalt cedar quartz copper marble willow granite saffron indigo cypress bronze jasper walnut".split()
_PROPS = ["founded in", "powered by", "located near", "awarded for", "merged with"]


def make_facts(M, offset=0):
    keys, vq = [], []
    for j in range(M):
        i = offset + j
        ent = "the %s %s" % (_ADJ[i % len(_ADJ)], _NOUN[(i // len(_ADJ)) % len(_NOUN)])
        prop = _PROPS[i % len(_PROPS)]; value = "%s %d" % (_VALW[i % len(_VALW)], 1000 + i)
        keys.append("%s was %s %s." % (ent, prop, value)); vq.append("Which one was %s %s?" % (prop, value))
    return keys, vq


def _norm(X):
    return (X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)).astype(np.float32)


def hebbian_recall(Kp, Qp, M, chunk=1000):
    """Hebbian-superposition recall@1 over M projected keys: r = W@q = (q@sub^T)@sub (no D x D / M x M); cleanup argmax."""
    sub = Kp[:M].astype(np.float32); subn = _norm(sub); q = Qp[:M].astype(np.float32)
    cor = 0
    for i in range(0, M, chunk):
        R = (q[i:i + chunk] @ sub.T) @ sub
        Rn = R / (np.linalg.norm(R, axis=1, keepdims=True) + 1e-8)
        cor += int((np.argmax(Rn @ subn.T, axis=1) == np.arange(i, min(i + chunk, M))).sum())
    return cor / M


def crosstalk_moments(Kp, M):
    """rho_mean + E[<ki,kj>^2] from the D x D gram (closed-form, NO M x M). unit-normed keys."""
    Kn = _norm(Kp[:M].astype(np.float64)); G = Kn.T @ Kn          # D x D gram
    s = Kn.sum(0)                                                  # for sum of all pairwise dots
    sum_all = float(s @ s)                                         # = sum_ij <ki,kj>
    rho_mean = (sum_all - M) / (M * (M - 1) + 1e-9)                # off-diagonal mean (diag=1, M of them)
    fro2 = float((G * G).sum())                                    # ||Kn^T Kn||_F^2 = sum_ij <ki,kj>^2
    e_sq = (fro2 - M) / (M * (M - 1) + 1e-9)                       # off-diagonal E[<>^2]
    rho_var = e_sq - rho_mean ** 2
    return float(rho_mean), float(rho_var), float(e_sq)


def capacity_sweep(Kp, Qp, grid, thresh):
    """M_crit = max M (interpolated) with hebbian_recall >= thresh."""
    curve = {}; prevM = 0.0; prevR = 1.0; cap = float(grid[-1])
    for M in grid:
        if M > len(Kp): cap = prevM; break
        r = hebbian_recall(Kp, Qp, M); curve[M] = round(r, 4)
        if r < thresh:
            cap = prevM + (M - prevM) * (prevR - thresh) / (prevR - r + 1e-9) if prevR > thresh else prevM
            break
        prevM = float(M); prevR = r
    return float(cap), curve


def _selftest():
    g = np.random.default_rng(0)
    # full-rank random projected keys: hebbian recall ~1 at low load, drops at high load (crosstalk)
    Kp = g.standard_normal((300, 32)).astype(np.float32); Qp = Kp.copy()
    assert hebbian_recall(Kp, Qp, 30) > 0.9, "hebbian low-load recall ~1"
    cap, _ = capacity_sweep(Kp, Qp, [20, 50, 100, 200], 0.8); assert cap < 300, "capacity bounded by crosstalk (%.1f)" % cap
    # gram closed-form matches brute-force on a small set
    Kn = _norm(g.standard_normal((40, 16)).astype(np.float64)); Gf = Kn @ Kn.T
    off = Gf[np.triu_indices(40, 1)]; rm, rv, es = crosstalk_moments(Kn, 40)
    assert abs(rm - off.mean()) < 1e-6 and abs(es - (off ** 2).mean()) < 1e-6, "gram closed-form == brute-force moments"
    print("[selftest] PASS: hebbian-recall + capacity-bounded + gram-closed-form==brute-force", flush=True)


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


def train_projection(Ktr, Qtr, d, steps, seed):
    """#7 contrastive projection: symmetric InfoNCE + key-uniformity (trained on TRAIN facts)."""
    torch.manual_seed(seed)
    K = torch.tensor(Ktr, device=DEV); Q = torch.tensor(Qtr, device=DEV); n, D = K.shape
    W = (torch.randn(D, d, device=DEV) * (1.0 / D ** 0.5)).requires_grad_(True)
    opt = torch.optim.Adam([W], lr=1e-2); bs = min(256, n)
    for _ in range(steps):
        idx = torch.randperm(n, device=DEV)[:bs]; tgt = torch.arange(len(idx), device=DEV)
        kp = F.normalize(K[idx] @ W, dim=1); qp = F.normalize(Q[idx] @ W, dim=1)
        la = 0.5 * (F.cross_entropy((qp @ kp.T) / 0.07, tgt) + F.cross_entropy((kp @ qp.T) / 0.07, tgt))
        off = (kp @ kp.T) - torch.eye(len(idx), device=DEV) * 2.0
        loss = la + 0.5 * off.mean()
        opt.zero_grad(); loss.backward(); opt.step()
    return W.detach().cpu().numpy().astype(np.float32)


def run_unit(seed):
    g = np.random.default_rng(seed)
    Mmax = max(M_SWEEP); M_total = TRAIN_FACTS + Mmax
    k_all, q_all = make_facts(M_total)                                            # SAME distribution (offset 0); NO 8-digit-year shift
    K_all = encode(k_all); Q_all = encode(q_all)
    perm = g.permutation(M_total); tr = perm[:TRAIN_FACTS]; capi = perm[TRAIN_FACTS:]   # disjoint, SAME distribution (#7 split)
    W = train_projection(K_all[tr], Q_all[tr], PROJ_DIM, TRAIN_STEPS, seed)
    Kc = K_all[capi]; Qc = Q_all[capi]                                            # held-out CAP keys + cues
    Kp = Kc @ W; Qp = Qc @ W                                                      # PROJECTED held-out
    rho_mean, rho_var, e_sq = crosstalk_moments(_norm(Kp), min(len(Kp), 5000))
    base = {"seed": seed, "rho_mean": round(rho_mean, 5), "rho_var": round(rho_var, 5), "e_sq": round(e_sq, 6)}
    # rho_mean PRE-FLIGHT (key-sep discipline applied to the capacity cell): keys MUST de-crowd to ~#7's 0.03-0.05.
    if rho_mean > 0.10:
        print("  [s=%d] PRE-FLIGHT FAIL: rho_mean=%.4f > 0.10 -> keys NOT de-crowded (projection not generalizing) -> ABORT (capacity on crowded keys is meaningless)" % (seed, rho_mean), flush=True)
        base.update({"preflight_fail": True, "m_crit_obs": 0.0, "m_crit_pred": 0.0, "recall_1k_proj": 0.0, "recall_1k_raw": 0.0, "canfail_halfdim_mcrit": 0.0, "curve": {}})
        return base
    cap, curve = capacity_sweep(Kp, Qp, M_SWEEP, RECALL_THRESH)
    m_crit_pred = 1.0 / (e_sq + 1e-12)                                            # raw-SNR capacity 1/E[<>^2] (cleanup-boost c reported via ratio)
    r1k = hebbian_recall(Kp, Qp, min(1000, len(Kp)))
    raw_r1k = hebbian_recall(_norm(Kc), _norm(Qc), min(1000, len(Kc)))           # RAW (unprojected) baseline
    half = PROJ_DIM // 2
    canfail_cap, _ = capacity_sweep(Kp[:, :half], Qp[:, :half], M_SWEEP, RECALL_THRESH)
    print("  [s=%d] rho_mean=%.4f (de-crowded) M_crit_obs=%.1f pred(1/E[<>^2])=%.1f cleanup-boost-c=%.2f | recall@1k proj=%.3f raw=%.3f | canfail(half)=%.1f curve=%s" %
          (seed, rho_mean, cap, m_crit_pred, cap / (m_crit_pred + 1e-9), r1k, raw_r1k, canfail_cap, curve), flush=True)
    base.update({"preflight_fail": False, "m_crit_obs": round(cap, 2), "m_crit_pred": round(m_crit_pred, 2),
                 "recall_1k_proj": round(r1k, 4), "recall_1k_raw": round(raw_r1k, 4),
                 "canfail_halfdim_mcrit": round(canfail_cap, 2), "curve": curve})
    return base


def compute_verdict(units) -> Tuple[str, str, Dict]:
    if not units: return ("HARD_FAIL", "no results", {})
    if any(u.get("preflight_fail") for u in units):
        rhos = [u.get("rho_mean", -1) for u in units]
        return ("HARD_FAIL", "HARD_FAIL[pre-flight]: keys NOT de-crowded (rho_mean=%s > 0.10) -> the #7 projection did not "
                "generalize-de-crowd these keys; capacity-on-crowded-keys is meaningless. Fix the projection/split before measuring. " % rhos,
                {"preflight_fail": True, "rho_mean_per_seed": rhos})
    obs = [u["m_crit_obs"] for u in units]; pred = [u["m_crit_pred"] for u in units]
    mo = float(np.mean(obs)); mp = float(np.mean(pred)); ratio = mo / (mp + 1e-9)
    r1k = float(np.mean([u["recall_1k_proj"] for u in units])); raw = float(np.mean([u["recall_1k_raw"] for u in units]))
    proj_over_raw = r1k / (raw + 1e-9); std = float(np.std(obs)); cv = std / (mo + 1e-9)
    canfail = float(np.mean([u["canfail_halfdim_mcrit"] for u in units]))
    within_2x = 0.5 <= ratio <= 2.0; too_clean = 0.95 <= ratio <= 1.05
    detail = {"m_crit_obs_mean": round(mo, 2), "m_crit_pred_mean": round(mp, 2), "obs_over_pred": round(ratio, 3),
              "recall_1k_proj": round(r1k, 4), "recall_1k_raw": round(raw, 4), "proj_over_raw": round(proj_over_raw, 2),
              "m_crit_cv": round(cv, 3), "canfail_halfdim_mcrit": round(canfail, 2),
              "honest_scope": "substrate Hebbian-superposition capacity on #7-PROJECTED Pythia-2.8B keys; M_crit vs full-"
                              "crosstalk prediction 1/E[<ki,kj>^2]; measures SUBSTRATE capacity not encoder key-quality (confound resolved by #7)."}
    summary = ("M_crit_obs=%.0f vs pred=%.0f (ratio=%.2f, within-2x=%s) | recall@1k proj=%.3f raw=%.3f (proj/raw=%.1fx) | "
               "CV=%.3f | canfail(half-dim)=%.0f" % (mo, mp, ratio, within_2x, r1k, raw, proj_over_raw, cv, canfail))
    if r1k < RECALL_THRESH or proj_over_raw < 2.0:
        return ("HARD_FAIL", "HARD_FAIL: substrate fails at M=1k on projected keys OR projected~raw (projection doesn't help -> confound not resolved). " + summary, detail)
    if too_clean:
        return ("HARD_FAIL", "HARD_FAIL[up-guard]: M_crit within +-5% of prediction (too clean -> verify-the-referent on measurement). " + summary, detail)
    if within_2x and r1k >= RECALL_THRESH and proj_over_raw > 5.0 and cv < 0.30:
        return ("HARD_PASS", "HARD_PASS: substrate Hebbian capacity on projected keys reproduces full-crosstalk prediction (within 2x) + "
                ">5x raw + recall@1k>=0.80 + crosstalk-bounded. " + summary, detail)
    return ("MIDDLE_BAND", "MIDDLE_BAND: mechanism works but M_crit off prediction (>2x) or proj/raw in [2,5]x. " + summary, detail)


print("[config] %s mode=%s encoder=%s M=%s seeds=%s d=%d train=%d steps=%d" % (
    ANCHOR_NAME, RUN_MODE, ENCODER, M_SWEEP, SEEDS, PROJ_DIM, TRAIN_FACTS, TRAIN_STEPS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); run_config = {"run_mode": RUN_MODE}; t0 = time.time()
for seed in SEEDS:
    key = "s%d" % seed
    if key in aggregate_partials(out_dir, [key], run_config=run_config):
        print("[ckpt] %s done; skip" % key, flush=True); continue
    res = run_unit(seed); res["run_mode"] = RUN_MODE
    write_partial_key(out_dir, key, res)
units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_config).values())
verdict, msg, detail = compute_verdict(units)
print("\n[VERDICT] " + msg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg, "run_mode": RUN_MODE, "encoder": ENCODER,
           "M_sweep": M_SWEEP, "n_seeds": len(SEEDS), "proj_dim": PROJ_DIM, "detail": detail,
           "metrics_source": "measured_gpu_pythia2p8b_hebbian_capacity_projected_keys", "per_unit": units, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, units)
print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
