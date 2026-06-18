"""A3: C1 entmax sparse-readout ENVELOPE SWEEP (Director PHASE-A-closed next-priority 2026-06-18; GPU-1).

Extends the C1 cert (entmax sparse readout MATCHES softmax recall at FEWER nonzero = cheaper, in the spread regime)
from a single config (N=1024/cluster=8/noise=0.15) to the CONFIG ENVELOPE: does the cheaper-at-iso-recall win HOLD
across N x cluster x noise? This is Skunkworks's measured-bounds-config-contingent test ON the C1 cert.

CERT-CONDITIONS (Skunkworks reaffirm 2026-06-18; 12h-plan pre-reg):
  1. METHOD-GATE: every cell is MEASURED (real torch readout on GPU; nonzero-count + recall are computed, NOT modeled).
     metrics_source=measured_torch_gpu (or measured_torch_cpu if no CUDA -> still measured, not cost-model).
  2. SYMMETRIC pre-registered gates (must be able to FALSIFY the envelope, not only confirm):
       HARD_PASS  = the cheaper-at-iso-recall win HOLDS across the discriminating envelope (>= PASS_FRAC of
                    discriminating cells win) -> C1 robustly config-contingent.
       HARD_FAIL  = the win COLLAPSES (<= FAIL_FRAC of discriminating cells win) -> the 8x-ENVELOPE claim FALSIFIED;
                    C1 stays NARROW single-point honest (an ACCEPTED outcome).
       MIDDLE_BAND= config-dependent -> state the valid envelope EXPLICITLY (which N/cluster/noise win).
  3. DEGENERATE-REGIME per-cell guard (self-dominance-wall lesson): a cell where softmax does NOT spread (nonzero<=2 =
     one-hot, sparse==dense) is NON-discriminating -> a per-cell NON_TEST; EXCLUDED from PASS/FAIL counts (does not
     count as a win OR a loss). Report discriminating vs non-discriminating cell counts.
  4. measured-bounds: the result is the win-envelope OF THIS N/cluster/noise GRID, NOT a fundamental claim.

beta is TUNED per cell on softmax (alpha=1.0) to the discriminating spread sweet-spot, then FROZEN across alpha
(no per-arm gaming). 11th rule: pure torch, no LLM. ASCII-only. HDLAB_RUN_MODE smoke|full ; --self-test ; --full.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _cell_provenance import provenance_fields, now_utc

ANCHOR = "substrate_c1_entmax_envelope_sweep_v1"
OUT = REPO / "data" / ANCHOR

# ENVELOPE grid (Director spec) -- full sweep
N_GRID_FULL = [512, 1024, 2048, 4096]
CLUSTER_GRID_FULL = [4, 8, 16, 32]
NOISE_GRID_FULL = [0.05, 0.10, 0.15, 0.20, 0.30]
SEEDS_FULL = [7, 17, 23]
# smoke: reduced grid, 1 seed, fast (gate readiness; not the cert)
N_GRID_SMOKE = [512, 1024]
CLUSTER_GRID_SMOKE = [8]
NOISE_GRID_SMOKE = [0.15]
SEEDS_SMOKE = [7]

ALPHAS = [1.0, 1.5, 2.0]          # 1.0 = softmax baseline; 1.5/2.0 = entmax sparse
BETA_GRID = [10.0, 20.0, 40.0, 60.0, 80.0, 120.0]
FLIP_FRAC = 0.12
ACC_THRESH = 0.90                 # cosine recall threshold (exact-recall fraction)
# pre-registered SYMMETRIC win + envelope thresholds
WIN_FLOPS_RED = 0.05              # a cell "wins" if entmax cuts >=5% nonzero at iso-recall (recall_delta >= -1pp)
WIN_RECALL_DELTA = -0.01
PASS_FRAC = 0.70                  # HARD_PASS: >= 70% of DISCRIMINATING cells win (envelope holds)
FAIL_FRAC = 0.30                  # HARD_FAIL: <= 30% of discriminating cells win (envelope falsified)


def _gen(seed, device):
    return torch.Generator(device=device).manual_seed(seed)


def _bipolar(shape, g, device):
    return (torch.randint(0, 2, shape, generator=g, device=device).float() * 2 - 1)


def _flip_k(x, k_flip, g):
    """Flip k_flip DISTINCT random bits per row of x (vectorized via topk-of-rand; GPU-friendly, no python per-row loop).
    Equivalent construction to the numpy harness's per-key g.choice (k distinct cols/row); deterministic via g."""
    if k_flip <= 0:
        return x
    M, n = x.shape
    r = torch.rand((M, n), generator=g, device=x.device)
    idx = r.topk(min(k_flip, n), dim=1).indices            # k_flip distinct cols per row
    mult = torch.ones_like(x)
    mult.scatter_(1, idx, -1.0)
    return x * mult


def make_clustered_keys(M, n, cluster_size, g, device):
    """(M,n) bipolar keys in M/cluster_size clusters of near-duplicates (centroid + FLIP_FRAC bits flipped)."""
    cluster_size = max(1, cluster_size)
    n_clusters = max(1, M // cluster_size)
    centroids = _bipolar((n_clusters, n), g, device)
    cid = torch.arange(M, device=device) % n_clusters
    keys = centroids[cid].clone()
    return _flip_k(keys, max(0, int(FLIP_FRAC * n)), g)     # vectorized per-key flip -> near-duplicate of centroid


def make_noisy_queries(keys, noise_frac, g, device):
    kf = max(1, int(noise_frac * keys.shape[1])) if noise_frac > 0 else 0
    return _flip_k(keys.clone(), kf, g)                    # vectorized noisy-cue flip


def cosine_scores(Q, K):
    Qn = Q / (Q.norm(dim=1, keepdim=True) + 1e-12)
    Kn = K / (K.norm(dim=1, keepdim=True) + 1e-12)
    return Qn @ Kn.t()


def entmax_alpha(Z, alpha, n_iter=30):
    """alpha=1 -> softmax; alpha>1 -> entmax (sparse), bisection on the threshold tau (torch port of C1)."""
    if alpha == 1.0:
        Z = Z - Z.max(dim=1, keepdim=True).values
        E = torch.exp(Z)
        return E / (E.sum(dim=1, keepdim=True) + 1e-12)
    am1 = alpha - 1.0
    Zs = am1 * Z
    tau_hi = Zs.max(dim=1, keepdim=True).values
    tau_lo = Zs.min(dim=1, keepdim=True).values - 1.0
    for _ in range(n_iter):
        tau = 0.5 * (tau_lo + tau_hi)
        s = torch.clamp(Zs - tau, min=0.0).pow(1.0 / am1).sum(dim=1, keepdim=True)
        over = s > 1.0
        tau_lo = torch.where(over, tau, tau_lo)
        tau_hi = torch.where(over, tau_hi, tau)
    p = torch.clamp(Zs - 0.5 * (tau_lo + tau_hi), min=0.0).pow(1.0 / am1)
    return p / (p.sum(dim=1, keepdim=True) + 1e-12)


def readout(M, n, cluster, noise, alpha, beta, g, device):
    """Spread-regime readout. Returns (exact_recall, mean_nonzero). Recall = query's OWN value (sign of W@V)."""
    keys = make_clustered_keys(M, n, cluster, g, device)
    V = _bipolar((M, n), g, device)
    Q = make_noisy_queries(keys, noise, g, device)
    S = cosine_scores(Q, keys)
    W = entmax_alpha(beta * S, alpha)
    recalls = torch.sign(W @ V)
    dot = (recalls * V).sum(1)
    nrm = recalls.norm(dim=1) * V.norm(dim=1) + 1e-12
    exact = float(((dot / nrm) >= ACC_THRESH).float().mean().item())
    nz = float((W > 1e-9).sum(1).float().mean().item())
    return exact, nz


def tune_beta(M, n, cluster, noise, g, device):
    """beta tuned on softmax (alpha=1.0) to the discriminating spread sweet-spot (softmax nonzero in [2, 4*cluster]),
    then FROZEN across alpha (no per-arm gaming)."""
    best_b, best_score = BETA_GRID[0], -1e18
    for b in BETA_GRID:
        _, nz = readout(M, n, cluster, noise, 1.0, b, g, device)
        score = -abs(nz - cluster) if 2.0 <= nz <= 4.0 * cluster else -1e6 - abs(nz - cluster)
        if score > best_score:
            best_score, best_b = score, b
    return best_b


def run_cell(n, cluster, noise, seeds, device):
    """One envelope cell. M=N (iso-load). Returns per-cell dict with discrimination + best entmax win at iso-recall."""
    M = n
    acc = {f"a{a}": {"exact": [], "nz": []} for a in ALPHAS}
    betas = []
    for s in seeds:
        g = _gen(s * 100003 + n + cluster * 7 + int(noise * 1000), device)
        beta = tune_beta(M, n, cluster, noise, g, device)
        betas.append(beta)
        for a in ALPHAS:
            ex, nz = readout(M, n, cluster, noise, a, beta, g, device)
            acc[f"a{a}"]["exact"].append(ex)
            acc[f"a{a}"]["nz"].append(nz)
    agg = {a: {"exact": sum(acc[f"a{a}"]["exact"]) / len(seeds), "nz": sum(acc[f"a{a}"]["nz"]) / len(seeds)} for a in ALPHAS}
    sm = agg[1.0]
    discriminates = sm["nz"] > 2.0                      # softmax genuinely spreads -> readout-family discriminates
    best = {"alpha": None, "flops_reduction": -1e9, "recall_delta": 0.0}
    per_alpha = {}                                       # Skunkworks reporting-req: per-alpha (for fixed-vs-best-alpha)
    for a in (1.5, 2.0):
        em = agg[a]
        red = 1.0 - em["nz"] / max(sm["nz"], 1e-9)      # iso-M FLOPs reduction (entmax fewer nonzero)
        rdelta = em["exact"] - sm["exact"]
        per_alpha[f"a{a}"] = {"flops_reduction": round(red, 4), "recall_delta": round(rdelta, 4),
                              "win": bool(discriminates and rdelta >= WIN_RECALL_DELTA and red >= WIN_FLOPS_RED)}
        if rdelta >= WIN_RECALL_DELTA and red > best["flops_reduction"]:
            best = {"alpha": a, "flops_reduction": red, "recall_delta": rdelta,
                    "softmax_recall": sm["exact"], "entmax_recall": em["exact"],
                    "softmax_nz": sm["nz"], "entmax_nz": em["nz"]}
    win = bool(discriminates and best["alpha"] is not None
               and best["flops_reduction"] >= WIN_FLOPS_RED and best["recall_delta"] >= WIN_RECALL_DELTA)
    return {"N": n, "cluster": cluster, "noise": noise, "M": M, "beta_mode": max(set(betas), key=betas.count),
            "softmax_nz": round(sm["nz"], 3), "softmax_recall": round(sm["exact"], 3),
            "discriminates": discriminates, "win": win,
            "best_alpha": best["alpha"], "flops_reduction": round(best["flops_reduction"], 4),
            "recall_delta": round(best["recall_delta"], 4), "per_alpha": per_alpha}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true", help="force FULL (overrides env)")
    args, _ = ap.parse_known_args()
    is_smoke = args.smoke or (os.environ.get("HDLAB_RUN_MODE", "full") == "smoke" and not args.full)
    run_started_utc = now_utc()
    t0 = time.time()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    src = "measured_torch_gpu" if device.type == "cuda" else "measured_torch_cpu"

    if args.self_test:
        # wiring check on a tiny cell; writes NO metrics
        c = run_cell(256, 8, 0.15, [7], device)
        print(f"[{ANCHOR}] --self-test wiring OK (device={device.type}, cell discriminates={c['discriminates']}, "
              f"win={c['win']}); NO metrics written.")
        return 0

    n_grid = N_GRID_SMOKE if is_smoke else N_GRID_FULL
    cluster_grid = CLUSTER_GRID_SMOKE if is_smoke else CLUSTER_GRID_FULL
    noise_grid = NOISE_GRID_SMOKE if is_smoke else NOISE_GRID_FULL
    seeds = SEEDS_SMOKE if is_smoke else SEEDS_FULL

    cells = []
    for n in n_grid:
        for cluster in cluster_grid:
            for noise in noise_grid:
                cells.append(run_cell(n, cluster, noise, seeds, device))
                c = cells[-1]
                print(f"[{ANCHOR}] N={c['N']} cluster={c['cluster']} noise={c['noise']}: "
                      f"discriminates={c['discriminates']} win={c['win']} "
                      f"flops_red={c['flops_reduction']} recall_delta={c['recall_delta']} (sm_nz={c['softmax_nz']})",
                      flush=True)

    discriminating = [c for c in cells if c["discriminates"]]
    non_disc = [c for c in cells if not c["discriminates"]]
    wins = [c for c in discriminating if c["win"]]
    n_disc = len(discriminating)
    win_frac = (len(wins) / n_disc) if n_disc > 0 else 0.0
    med_red = (sorted(c["flops_reduction"] for c in wins)[len(wins) // 2] if wins else 0.0)

    # Skunkworks reporting-req (a): flops_reduction MAGNITUDE distribution (does ~8x HOLD across the envelope or DEGRADE?)
    def _pct(xs, q):
        if not xs:
            return 0.0
        xs = sorted(xs)
        return xs[min(len(xs) - 1, int(q * (len(xs) - 1) + 0.5))]
    disc_reds = [c["flops_reduction"] for c in discriminating]
    win_reds = [c["flops_reduction"] for c in wins]
    magnitude = {
        "discriminating_flops_reduction": {
            "min": round(min(disc_reds), 4) if disc_reds else 0.0, "p25": round(_pct(disc_reds, 0.25), 4),
            "median": round(_pct(disc_reds, 0.5), 4), "p75": round(_pct(disc_reds, 0.75), 4),
            "max": round(max(disc_reds), 4) if disc_reds else 0.0},
        "win_flops_reduction_median": round(_pct(win_reds, 0.5), 4),
        "note": "8x ~= flops_reduction 0.875; HOLDS if median stays ~0.875 across cells, DEGRADES if it falls toward 0.05 at edges",
    }
    # Skunkworks reporting-req (b): fixed-vs-best-alpha (is a SINGLE fixed alpha envelope-robust, or only per-cell-best?)
    fixed_alpha = {}
    for a in ("a1.5", "a2.0"):
        fa_wins = sum(1 for c in discriminating if c["per_alpha"][a]["win"])
        fixed_alpha[a] = {"wins": fa_wins, "win_fraction": round(fa_wins / n_disc, 4) if n_disc else 0.0}
    fixed_alpha["best_of_both"] = {"wins": len(wins), "win_fraction": round(win_frac, 4)}

    if n_disc == 0:
        verdict = "HONEST_BOUNDED"
        msg = (f"NON-TEST envelope: NO cell discriminates (softmax one-hots everywhere; nonzero<=2) across the swept "
               f"grid -- no readout-family discrimination reachable. Re-design harness. (cells={len(cells)})")
    elif win_frac >= PASS_FRAC:
        verdict = "HARD_PASS"
        msg = (f"C1 ENVELOPE HOLDS: entmax cheaper-at-iso-recall WINS in {len(wins)}/{n_disc} discriminating cells "
               f"({win_frac*100:.0f}% >= {PASS_FRAC*100:.0f}%); median FLOPs-reduction {med_red*100:.0f}%. The sparse-"
               f"readout win is ROBUSTLY config-contingent across N x cluster x noise. measured-bounds: THIS grid "
               f"(N{N_GRID_FULL} x cluster{CLUSTER_GRID_FULL} x noise{NOISE_GRID_FULL}), NOT fundamental. "
               f"({len(non_disc)} non-discriminating cells EXCLUDED.)")
    elif win_frac <= FAIL_FRAC:
        verdict = "HARD_FAIL"
        msg = (f"C1 ENVELOPE FALSIFIED: entmax wins in only {len(wins)}/{n_disc} discriminating cells "
               f"({win_frac*100:.0f}% <= {FAIL_FRAC*100:.0f}%) -- the cheaper-at-iso-recall win does NOT generalize "
               f"across the config envelope; C1 stays NARROW single-point honest (win confined to its original config). "
               f"Accepted symmetric outcome. ({len(non_disc)} non-discriminating cells EXCLUDED.)")
    else:
        verdict = "MIDDLE_BAND"
        win_cfgs = [f"N{c['N']}/c{c['cluster']}/no{c['noise']}" for c in wins]
        msg = (f"C1 ENVELOPE CONFIG-DEPENDENT: entmax wins in {len(wins)}/{n_disc} discriminating cells "
               f"({win_frac*100:.0f}%; between {FAIL_FRAC*100:.0f}-{PASS_FRAC*100:.0f}%). Valid win-envelope (explicit): "
               f"{win_cfgs}. measured-bounds: config-dependent across this grid, NOT fundamental.")

    metrics = {
        "anchor_name": ANCHOR, "verdict": verdict, "verdict_msg": msg, "summary": msg, "headline": msg,
        "n_seeds": len(seeds),
        **provenance_fields("smoke" if is_smoke else "full", "envelope_sweep", src, run_started_utc),
        "n_cells": len(cells), "n_discriminating": n_disc, "n_non_discriminating": len(non_disc),
        "n_wins": len(wins), "win_fraction_of_discriminating": round(win_frac, 4),
        "median_flops_reduction_of_wins": round(med_red, 4),
        "magnitude_distribution": magnitude,        # Skunkworks reporting-req (a): does 8x hold or degrade
        "fixed_vs_best_alpha": fixed_alpha,          # Skunkworks reporting-req (b): fixed-alpha-robust vs per-cell-best
        "thresholds": {"WIN_FLOPS_RED": WIN_FLOPS_RED, "WIN_RECALL_DELTA": WIN_RECALL_DELTA,
                       "PASS_FRAC": PASS_FRAC, "FAIL_FRAC": FAIL_FRAC, "ACC_THRESH": ACC_THRESH},
        "grid": {"N": n_grid, "cluster": cluster_grid, "noise": noise_grid, "alphas": ALPHAS, "M": "M=N (iso-load)"},
        "cells": cells,
        "bears_on": "C1_entmax_alpha_readout_v1 (envelope test) + ARCH-B nonlinear-readout lever",
        "measured_bounds": f"entmax cheaper-at-iso-recall WIN-ENVELOPE over THIS N x cluster x noise grid; NOT fundamental",
        "elapsed_s": round(time.time() - t0, 2),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, OUT / "metrics.json")

    print(f"[{ANCHOR}] run_mode={'smoke' if is_smoke else 'full'} device={device.type} -> {verdict}")
    print(f"  cells={len(cells)} discriminating={n_disc} non_disc={len(non_disc)} wins={len(wins)} "
          f"win_frac={win_frac:.2f} median_flops_red={med_red:.2f}")
    print(f"  {msg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
