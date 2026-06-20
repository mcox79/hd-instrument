"""
kmax_ness_envelope_gpu_v1 -- K_max NESS-correction empirical envelope (Research Component-2, drill plan 3feb7678). GPU.
CLAIM: substrate NESS write-decay dynamics push chain-recall DEPTH K_max ABOVE the independent equilibrium Hopfield ceiling
K_eq = 3.3*(1-alpha/alpha_c)^2/alpha (alpha_c=0.138, classical Hopfield -- INDEPENDENT theory constant, non-circular per
Skunkworks cert-VET). Gate: K_obs/K_eq >= 2.0 across >=4/5 SAFE-regime points.

DESIGN (single-alpha NESS, per drill plan "W <- (1-alpha)W + outer; alpha=write-rate"):
- hetero-assoc chain a_0->a_1->...->a_K; NESS-decayed W = sequential (1-alpha)*W + outer(a_{i+1},a_i) (oldest pair decays most
  -> first hop is the bottleneck -> K_max bounded by decay). Recall: r=a_0, hop K times via W, cleanup-argmax over codebook.
- K_obs(alpha) = max chain-depth K with mean final-node recall >= 0.9 (cleanup-ON). K_eq(alpha) = equilibrium ceiling.

DISCIPLINES (cert-VET, all baked in):
- alpha_c=0.138 INDEPENDENT (Hopfield) -> non-circular baseline (Skunkworks constraint SATISFIED).
- DIVIDE-BY-ZERO GUARD: K_eq->0 as alpha->alpha_c -> gate ONLY where (1-alpha/alpha_c)^2 >= 0.30 (safe regime). SWEEP stays
  alpha in {0.05..0.25}*alpha_c (all (1-a/ac)^2 in [0.56,0.90]) -> >=4 gating points, ratio CAN fail. Report K_eq + (1-a/ac)^2 per-point.
- GENUINE-MULTI-HOP (pre-flag 1): cleanup-OFF (control sign-recall) measured per-depth; cleanup-OFF >= 0.3 = genuine multi-hop
  (PASS); ~chance = cleanup-RECOVERY artifact (FLAG). REPORT the cleanup-OFF curve. (per Research op + Skunkworks add.)
- empirical envelope = LIVE cert; the NESS predictive ALGEBRA (fitted eta/f_c/tau) stays T3-conjecture (kept distinct).
import torch first. checkpoint per (alpha,seed); restartable. ASCII.
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

ANCHOR_NAME = "kmax_ness_envelope_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
ALPHA_C = 0.138  # classical Hopfield critical capacity (Amit-Gutfreund-Sompolinsky) -- INDEPENDENT theory constant
ALPHA_FRACS = [0.10, 0.20] if SMOKE else [0.05, 0.10, 0.15, 0.20, 0.25]  # x alpha_c; all in divide-by-zero-SAFE regime
K_GRID = [4, 8, 16, 28] if SMOKE else [6, 12, 24, 36, 48, 60, 80, 100]
SEEDS = [1] if SMOKE else [1, 2, 3]
N = 1024 if SMOKE else 8192
N_CHAINS = 8 if SMOKE else 24
RECALL_THRESH = 0.90
GENUINE_FLOOR = 0.30  # cleanup-OFF recall floor for genuine-multi-hop (per-hop noise compounds; 0.95^24~0.29)


def k_eq(alpha):
    return 3.3 * (1.0 - alpha / ALPHA_C) ** 2 / alpha


def safe_gate(alpha):
    return alpha < ALPHA_C and (1.0 - alpha / ALPHA_C) ** 2 >= 0.30


def pearson(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    if np.std(x) < 1e-9 or np.std(y) < 1e-9: return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def _selftest():
    # K_eq sanity: at 0.5*alpha_c (=0.069) K_eq~11.96; at 0.1*alpha_c K_eq~193.7
    assert abs(k_eq(0.5 * ALPHA_C) - 11.96) < 0.5, "K_eq(0.5ac)~12 (%.2f)" % k_eq(0.5 * ALPHA_C)
    assert abs(k_eq(0.1 * ALPHA_C) - 193.7) < 2.0, "K_eq(0.1ac)~194 (%.2f)" % k_eq(0.1 * ALPHA_C)
    # divide-by-zero guard: 0.5*ac excluded ((1-0.5)^2=0.25<0.30), 0.25*ac included (0.5625)
    assert not safe_gate(0.5 * ALPHA_C) and safe_gate(0.25 * ALPHA_C), "safe-gate regime"
    print("[selftest] PASS: K_eq formula + divide-by-zero safe-gate", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)

try:
    import torch
except Exception as e:
    print("[FATAL] torch: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cuda") if torch.cuda.is_available() else (torch.device("cpu") if SMOKE else None)
if DEV is None:
    print("[FATAL] CUDA required for full run.", flush=True); sys.exit(1)
print("[dev] %s" % DEV, flush=True)


def bsc(m, n, g):
    return (torch.randint(0, 2, (m, n), generator=g, device=DEV).float() * 2 - 1)


def recall_chain_depth(alpha, K, seed):
    """N_CHAINS chains of depth K; per-chain NESS-decayed W; recall a_0->a_K. Returns (cand2_recall, control_recall) means."""
    g = torch.Generator(device=DEV); g.manual_seed(seed * 100003 + K * 31 + int(alpha * 1e6))
    chains = [bsc(K + 1, N, g) for _ in range(N_CHAINS)]                      # each (K+1, N)
    codebook = torch.cat(chains, 0)                                           # (N_CHAINS*(K+1), N) shared cleanup codebook
    cb_idx0 = [c * (K + 1) for c in range(N_CHAINS)]                          # index of each chain's a_0 in codebook
    cand_ok = 0; ctrl_ok = 0
    for c in range(N_CHAINS):
        nodes = chains[c]                                                     # (K+1, N)
        W = torch.zeros((N, N), device=DEV, dtype=torch.float32)
        for i in range(K):                                                    # NESS decay: oldest pair decays most
            W = (1.0 - alpha) * W + torch.outer(nodes[i + 1], nodes[i]) / N
        tgt = c * (K + 1) + K                                                 # codebook index of a_K
        # cand2 (cleanup-ON): snap to codebook each hop
        r = nodes[0].clone()
        for _h in range(K):
            v = W @ r; r = codebook[int(torch.argmax(codebook @ v))]
        cand_ok += int(int(torch.argmax(codebook @ r)) == tgt)
        # control (cleanup-OFF): sign recall, no snap; final argmax over codebook
        r = nodes[0].clone()
        for _h in range(K):
            v = W @ r; r = torch.sign(v); r[r == 0] = 1.0
        ctrl_ok += int(int(torch.argmax(codebook @ r)) == tgt)
    return cand_ok / N_CHAINS, ctrl_ok / N_CHAINS


def interp_kmax(curve_k, curve_recall):
    """max K with recall>=thresh, linear-interpolated at the crossing."""
    prevK, prevR, kmax = 0.0, 1.0, 0.0
    for K, r in zip(curve_k, curve_recall):
        if r >= RECALL_THRESH:
            kmax = float(K); prevK, prevR = float(K), r
        else:
            if prevR > RECALL_THRESH:
                kmax = prevK + (K - prevK) * (prevR - RECALL_THRESH) / (prevR - r + 1e-9)
            break
    return kmax


def run_unit(alpha_frac, seed):
    alpha = alpha_frac * ALPHA_C
    cand_curve = {}; ctrl_curve = {}
    for K in K_GRID:
        cr, tr = recall_chain_depth(alpha, K, seed)
        cand_curve[K] = round(cr, 4); ctrl_curve[K] = round(tr, 4)
        if cr < RECALL_THRESH and K > K_GRID[0]:
            break                                                            # past the cliff; stop sweeping deeper
    kmax = interp_kmax(list(cand_curve.keys()), list(cand_curve.values()))
    keq = k_eq(alpha); ratio = kmax / (keq + 1e-9)
    # genuine-multi-hop: cleanup-OFF recall at the deepest K where cand2 still passed
    deep_K = max([K for K, r in cand_curve.items() if r >= RECALL_THRESH], default=K_GRID[0])
    ctrl_at_deep = ctrl_curve.get(deep_K, 0.0)
    genuine = ctrl_at_deep >= GENUINE_FLOOR
    print("  [af=%.2f a=%.4f s=%d] K_obs=%.1f K_eq=%.1f ratio=%.2f | (1-a/ac)^2=%.3f safe=%s | ctrl@K%d=%.3f genuine=%s" %
          (alpha_frac, alpha, seed, kmax, keq, ratio, (1 - alpha / ALPHA_C) ** 2, safe_gate(alpha), deep_K, ctrl_at_deep, genuine), flush=True)
    return {"alpha_frac": alpha_frac, "alpha": round(alpha, 5), "seed": seed, "k_obs": round(kmax, 2), "k_eq": round(keq, 2),
            "ratio": round(ratio, 3), "one_minus_frac_sq": round((1 - alpha / ALPHA_C) ** 2, 4), "safe_gate": bool(safe_gate(alpha)),
            "cand_curve": cand_curve, "ctrl_curve": ctrl_curve, "deep_K": deep_K, "ctrl_at_deep": round(ctrl_at_deep, 4),
            "genuine_multihop": bool(genuine), "run_mode": RUN_MODE}


def compute_verdict(units) -> Tuple[str, str, Dict]:
    if not units: return ("HARD_FAIL", "no results", {})
    by = {}
    for u in units:
        by.setdefault(u["alpha_frac"], []).append(u)
    per = {}
    for af, us in by.items():
        per[af] = {"alpha": us[0]["alpha"], "k_obs": float(np.mean([u["k_obs"] for u in us])), "k_eq": us[0]["k_eq"],
                   "ratio": float(np.mean([u["ratio"] for u in us])), "safe_gate": us[0]["safe_gate"],
                   "ctrl_at_deep": float(np.mean([u["ctrl_at_deep"] for u in us])), "genuine": all(u["genuine_multihop"] for u in us)}
    safe = {af: d for af, d in per.items() if d["safe_gate"]}
    n_pass = sum(1 for d in safe.values() if d["ratio"] >= 2.0)
    n_safe = len(safe)
    all_genuine = all(d["genuine"] for d in safe.values())
    afs = sorted(safe.keys()); ratios = [safe[a]["ratio"] for a in afs]
    detail = {"per_alpha_frac": per, "n_safe_points": n_safe, "n_pass_ge_2x": n_pass, "all_genuine_multihop": bool(all_genuine),
              "ratios_safe": {a: round(safe[a]["ratio"], 2) for a in afs},
              "honest_claim": "Substrate NESS chain-recall depth K_obs vs INDEPENDENT Hopfield K_eq=3.3(1-a/ac)^2/a (ac=0.138): "
                              "%d/%d safe-regime points exceed 2x; genuine-multi-hop (cleanup-OFF>=0.3)=%s. Empirical envelope "
                              "(live cert); NESS predictive algebra stays T3." % (n_pass, n_safe, all_genuine)}
    summary = "ratios(safe)=%s | %d/%d >=2x | all_genuine=%s | n_safe=%d" % (detail["ratios_safe"], n_pass, n_safe, all_genuine, n_safe)
    if n_safe < 4:
        return ("UNKNOWN", "need >=4 safe-regime points (got %d)" % n_safe, detail)
    if not all_genuine:
        return ("HARD_FAIL", "HARD_FAIL: cleanup-OFF recall < 0.30 at a safe point -> deep-K is cleanup-RECOVERY artifact, NOT genuine multi-hop (pre-flag-1). " + summary, detail)
    if n_pass >= 4:
        return ("HARD_PASS", "HARD_PASS: NESS K_obs exceeds independent Hopfield K_eq >=2x across >=4 safe-regime points, genuine multi-hop. Empirical envelope = live cert. " + summary, detail)
    if n_pass >= 2:
        return ("MIDDLE_BAND", "MIDDLE_BAND: NESS exceeds K_eq >=2x at 2-3 safe points (not >=4). " + summary, detail)
    return ("HARD_FAIL", "HARD_FAIL: NESS does NOT exceed equilibrium K_eq >=2x in the safe regime (envelope ~ equilibrium). " + summary, detail)


print("[config] %s mode=%s N=%d alpha_fracs=%s K_grid=%s seeds=%s n_chains=%d" % (ANCHOR_NAME, RUN_MODE, N, ALPHA_FRACS, K_GRID, SEEDS, N_CHAINS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); run_config = {"run_mode": RUN_MODE}; t0 = time.time()
for af in ALPHA_FRACS:
    for seed in SEEDS:
        key = "af%.2f_s%d" % (af, seed)
        if key in aggregate_partials(out_dir, [key], run_config=run_config):
            print("[ckpt] %s done; skip" % key, flush=True); continue
        try:
            write_partial_key(out_dir, key, run_unit(af, seed))
        except Exception as e:
            print("[WARN] %s failed: %s" % (key, e), flush=True)
keys = ["af%.2f_s%d" % (af, sd) for af in ALPHA_FRACS for sd in SEEDS]
units = list(aggregate_partials(out_dir, keys, run_config=run_config).values())
verdict, msg, detail = compute_verdict(units)
print("\n[VERDICT] " + msg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg, "run_mode": RUN_MODE, "N": N,
           "alpha_c": ALPHA_C, "alpha_fracs": ALPHA_FRACS, "K_grid": K_GRID, "n_seeds": len(SEEDS), "detail": detail,
           "metrics_source": "measured_gpu_ness_chain_depth_vs_independent_hopfield_keq", "per_unit": units, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, units)
print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
