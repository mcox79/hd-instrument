"""C1 nonlinear-readout frontier: entmax-alpha sparse readout vs softmax -- SPREAD-REGIME re-design (LOCKED 2026-06-17).

Director STEP-2 LOCK + spread-regime re-sequence. The original clean-i.i.d.-raw-dot smoke was a NON-TEST (self-dominance
-> softmax one-hot -> entmax has nothing to sparsify). RE-DESIGNED to use the shared spread-attention harness
(_spread_attention_harness): COSINE-normalized + CLUSTERED keys + NOISY cue + tuned beta -> softmax genuinely SPREADS
over the ~cluster_size near-neighbours -> the regime where readout-FAMILY (softmax vs entmax) discriminates.

QUESTION: in the SPREAD regime, does a SPARSE readout (entmax alpha>1) MATCH softmax recall at LOWER compute (fewer
nonzero attention weights), AND/OR recall BETTER (sharper concentration on the true match vs the cluster distractors)?
beta TUNED (on softmax, alpha=1.0) to the discriminating sweet-spot (softmax nonzero-count in [2, 2*cluster_size] =
genuine spread, not full-diffuse), then FROZEN across alpha (no per-arm gaming). verify_spread gates: no spread -> NON-TEST.
VERDICT: HARD-PASS = entmax preserves softmax recall at strictly fewer nonzero (lower FLOPs) in the spread regime (OR
recall strictly higher at <= nonzero); MIDDLE = marginal; HARD-FAIL = entmax recall < softmax (sparsity too aggressive
on structured HD codes); HONEST_BOUNDED = no spread regime reachable (NON-TEST, not refutation). T2 (Hu 2023) -> T0 only
on cert. TIER-1 LAPTOP (N=1024). HDLAB_RUN_MODE smoke|full. ASCII-only.
"""
from __future__ import annotations
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _spread_attention_harness import make_clustered_keys, make_noisy_queries, cosine_scores, verify_spread

ANCHOR = "substrate_C1_entmax_alpha_readout_v1"
OUT = REPO / "data" / ANCHOR
RUN_MODE = os.environ.get("HDLAB_RUN_MODE", "smoke")
N = 256 if RUN_MODE == "smoke" else 1024
SEEDS = [7] if RUN_MODE == "smoke" else [7, 17, 23]
M_LIST = [128, 256] if RUN_MODE == "smoke" else [512, 1024, 2048]
ALPHAS = [1.0, 1.5, 2.0]
CLUSTER_SIZE = 8          # spread parameter: queries compete with ~8 near-neighbours
NOISE = 0.15             # noisy cue (degrade exact self-match so cluster-mates genuinely compete)
BETA_GRID = [10.0, 20.0, 40.0, 60.0, 80.0, 120.0]
ACC_THRESH = 0.90


def _rng(seed):
    return np.random.default_rng(seed)


def make_values(M, n, g):
    return (g.integers(0, 2, size=(M, n)).astype(np.float32) * 2 - 1)


def entmax_alpha(Z, alpha, n_iter=30):
    if alpha == 1.0:
        Z = Z - Z.max(axis=1, keepdims=True); E = np.exp(Z); return E / (E.sum(axis=1, keepdims=True) + 1e-12)
    am1 = alpha - 1.0
    Zs = am1 * Z
    tau_hi = Zs.max(axis=1, keepdims=True); tau_lo = Zs.min(axis=1, keepdims=True) - 1.0
    for _ in range(n_iter):
        tau = 0.5 * (tau_lo + tau_hi)
        s = (np.clip(Zs - tau, 0.0, None) ** (1.0 / am1)).sum(axis=1, keepdims=True)
        over = s > 1.0
        tau_lo = np.where(over, tau, tau_lo); tau_hi = np.where(over, tau_hi, tau)
    p = np.clip(Zs - 0.5 * (tau_lo + tau_hi), 0.0, None) ** (1.0 / am1)
    return p / (p.sum(axis=1, keepdims=True) + 1e-12)


def readout(M, n, alpha, beta, g):
    """Spread-regime readout: clustered keys + noisy cue + cosine scores + entmax-alpha. Recall = query's OWN value."""
    keys, _cid = make_clustered_keys(M, n, CLUSTER_SIZE, g)
    V = make_values(M, n, g)
    Q = make_noisy_queries(keys, NOISE, g)
    S = cosine_scores(Q, keys)
    W = entmax_alpha(beta * S, alpha)
    recalls = np.sign(W @ V)                      # (M,n)
    dot = (recalls * V).sum(1); nrm = np.linalg.norm(recalls, axis=1) * np.linalg.norm(V, axis=1) + 1e-12
    exact = float(((dot / nrm) >= ACC_THRESH).mean())
    nz = float((W > 1e-9).sum(1).mean())          # mean nonzero attention weights
    spread = verify_spread(W)["spreads"]
    return exact, nz, spread


def tune_beta():
    """beta tuned on softmax (alpha=1.0) to the DISCRIMINATING spread sweet-spot: softmax nonzero-count in
    [2, 2*CLUSTER_SIZE] (genuine spread, not one-hot, not full-diffuse). Frozen across alpha."""
    g = _rng(99); best_b, best_score = BETA_GRID[0], -1.0
    for b in BETA_GRID:
        _, nz, _ = readout(M_LIST[-1], N, 1.0, b, g)
        # score: prefer nonzero closest to CLUSTER_SIZE (the genuine spread sweet-spot)
        score = -abs(nz - CLUSTER_SIZE) if 2.0 <= nz <= 4.0 * CLUSTER_SIZE else -1e6 - abs(nz - CLUSTER_SIZE)
        if score > best_score:
            best_score, best_b = score, b
    return best_b


def main():
    t0 = time.time()
    beta = tune_beta()
    grid = {f"a{a}": {f"M{m}": {} for m in M_LIST} for a in ALPHAS}
    for s in SEEDS:
        for a in ALPHAS:
            for m in M_LIST:
                ex, nz, sp = readout(m, N, a, beta, _rng(s * 1000 + m + int(a * 10)))
                d = grid[f"a{a}"][f"M{m}"]
                d.setdefault("exact", []).append(ex); d.setdefault("nz", []).append(nz); d.setdefault("sp", []).append(sp)
    for a in ALPHAS:
        for m in M_LIST:
            d = grid[f"a{a}"][f"M{m}"]
            d["exact"] = float(np.mean(d["exact"])); d["nz"] = float(np.mean(d["nz"])); d["spread"] = bool(np.mean(d["sp"]) >= 0.5)

    # discriminating regime = M where softmax (a1.0) genuinely SPREADS (nonzero > 2)
    spread_M = [m for m in M_LIST if grid["a1.0"][f"M{m}"]["spread"] and grid["a1.0"][f"M{m}"]["nz"] > 2.0]
    best = {"alpha": None, "M": None, "flops_reduction": 0.0, "recall_delta": 0.0}
    for a in (1.5, 2.0):
        for m in spread_M:
            sm = grid["a1.0"][f"M{m}"]; em = grid[f"a{a}"][f"M{m}"]
            red = 1.0 - em["nz"] / max(sm["nz"], 1e-9)            # iso-M FLOPs reduction (entmax fewer nonzero)
            rdelta = em["exact"] - sm["exact"]                    # recall delta vs softmax (iso-M)
            # win = recall preserved (>= -1pp) AND fewer nonzero, OR recall strictly higher at <= nonzero
            if (rdelta >= -0.01 and red > best["flops_reduction"]) or (rdelta > 0.02 and red >= -0.01 and rdelta > best["recall_delta"]):
                best = {"alpha": a, "M": m, "flops_reduction": red, "recall_delta": rdelta,
                        "softmax_recall": sm["exact"], "entmax_recall": em["exact"], "softmax_nz": sm["nz"], "entmax_nz": em["nz"]}

    if not spread_M:
        verdict = "HONEST_BOUNDED"
        msg = (f"NON-TEST: softmax does not SPREAD at any M (nonzero<=2 = still one-hot) even with the spread harness; "
               f"re-tune beta/cluster_size. beta={beta}. No readout-family discrimination reachable here (envelope at N={N}).")
    elif best["alpha"] and best["flops_reduction"] >= 0.05 and best["recall_delta"] >= -0.01:
        verdict = "HARD_PASS"
        msg = (f"SPARSE-readout WIN in the spread regime: entmax alpha={best['alpha']} (M={best['M']}) preserves softmax "
               f"recall ({best['entmax_recall']:.3f} vs {best['softmax_recall']:.3f}, delta {best['recall_delta']:+.3f}) "
               f"at {best['flops_reduction']*100:.1f}% fewer nonzero (entmax nz {best['entmax_nz']:.1f} vs softmax "
               f"{best['softmax_nz']:.1f}). Sparse readout matches softmax recall cheaper where attention spreads. "
               f"N={N}; readout-family/config envelope (measured-bounds), NOT fundamental.")
    elif best["alpha"] and (best["flops_reduction"] > 0.01 or best["recall_delta"] > 0.01):
        verdict = "MIDDLE_BAND"
        msg = (f"MARGINAL in spread regime: entmax alpha={best['alpha']} FLOPs reduction {best['flops_reduction']*100:.1f}% "
               f"/ recall delta {best['recall_delta']:+.3f} (M={best['M']}); below the +5%-FLOPs HARD-PASS bar.")
    else:
        verdict = "HARD_FAIL"
        msg = (f"sparse readout does NOT help in the spread regime: entmax recall < softmax or no compute win at iso-recall "
               f"(spread_M={spread_M}); Hu-2023 sparse benefit does not transfer to structured HD codes here (substrate-novel negative).")

    metrics = {
        "anchor_name": ANCHOR, "verdict": verdict, "verdict_msg": msg, "headline": msg, "run_mode": RUN_MODE,
        "N": N, "n_seeds": len(SEEDS), "M_list": M_LIST, "alphas": ALPHAS, "cluster_size": CLUSTER_SIZE, "noise": NOISE,
        "beta_tuned": beta, "spread_M": spread_M, "best": best, "grid": grid,
        "regime": "SPREAD (cosine + clustered + noisy-cue; shared spread-attention harness)",
        "recapture_of": "n/a -- nonlinear-readout FRONTIER (bears_on ARCH-B + nonlinear-readout ceiling)",
        "measured_bounds": f"envelope of entmax readout-family at N={N}/cluster_size={CLUSTER_SIZE}/noise={NOISE}; NOT fundamental",
        "elapsed_s": round(time.time() - t0, 2),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, OUT / "metrics.json")

    print(f"[{ANCHOR}] run_mode={RUN_MODE} N={N} cluster={CLUSTER_SIZE} noise={NOISE} beta*={beta} -> {verdict}")
    print(f"  spread_M (softmax nonzero>2): {spread_M}")
    print(f"  recall + nonzero by alpha x M:")
    for a in ALPHAS:
        print(f"    alpha={a}: " + "  ".join(f"M{m}=(r{grid[f'a{a}'][f'M{m}']['exact']:.2f},nz{grid[f'a{a}'][f'M{m}']['nz']:.1f})" for m in M_LIST))
    print(f"  best: {best}")
    print(f"  {msg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
