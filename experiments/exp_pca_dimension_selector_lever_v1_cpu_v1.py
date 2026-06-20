"""LEVER #2: PCA dimension-selector (Research prereg; Director amendments 2a/2b/2c).

NON-CIRCULAR design (Director 2a, the load-bearing fix): measure capacity on RECALL out-of-sample, NOT via the
crosstalk-moment formula (using crosstalk to predict capacity is the isotropy-circular trap -- 7315be3c showed crosstalk
IS capacity near-by-construction). 2b: PCA REDUCES dims, so the genuine win is SNR-gain > dim-loss ON RECALL. 2c: dropped
the moment<=0.8 band (near-by-construction).

MECHANISM: KV recall from a NOISED query. PCA-to-top-k is a denoising projection: if the keys are ANISOTROPIC (signal
concentrated in r<<N top eigen-directions), projecting to k~r KEEPS the signal and DROPS the noise dims -> the query noise
in the tail N-k dims is removed -> higher SNR -> better recall. If keys are ISOTROPIC, projecting drops signal -> worse.
So PCA-dim-selection helps IFF the keys are anisotropic enough. The selector picks k from the eigenvalue spectrum
(variance-retention), CALIBRATED on a probe and TESTED on held-out queries.

3 arms: Arm1 selector (k from spectrum), Arm2 naive (k=N/2), Arm3 no-cut (k=N). DISCRIMINATING: Arm1 beats Arm3 (PCA
doesn't lose recall / denoises) AND beats Arm2 (measurement-driven k beats a fixed half) on the anisotropic regime.
data-decides -> chain-grade-eligible on anisotropic regime; MM-negative on isotropic. ASCII; no em-dashes.
"""
import sys
from pathlib import Path
import argparse
import os
import time
import numpy as np

REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_partial_key, aggregate_partials, write_metrics

ANCHOR_NAME = "pca_dimension_selector_lever_v1_cpu_v1"
_P = argparse.ArgumentParser(); _P.add_argument("--self-test", action="store_true", dest="self_test"); _ARGS, _ = _P.parse_known_args()
RUN_MODE = os.environ.get("HDLAB_RUN_MODE", "full" if not _ARGS.self_test else "smoke")
N = 1024 if RUN_MODE == "full" else 256
M = 600 if RUN_MODE == "full" else 150                    # number of stored keys
SIGNAL_AMP = 3.0                                          # signal amplitude (vs 0.3 all-dim noise) so the spectrum drops sharply at `rank` -> select_k isolates the signal subspace
SIGMA_FRAC = 3.0                                          # query noise NORM as a fraction of the unit key norm (per-dim sigma = SIGMA_FRAC/sqrt(N)); the thing PCA denoises
VAR_RETAIN = 0.90                                         # selector keeps the top-k capturing this fraction of variance
RANKS = [N // 16, N // 4, N // 2, N] if RUN_MODE == "full" else [N // 16, N // 2, N]   # signal rank: small=anisotropic, =N isotropic
SEEDS = [1, 2, 3] if RUN_MODE == "full" else [1]


def make_keys(m, n, rank, seed):
    """m keys = low-rank SIGNAL (rank directions, strong) + isotropic NOISE (all n dims, weak). rank=n -> isotropic."""
    g = np.random.default_rng(seed)
    basis, _ = np.linalg.qr(g.standard_normal((n, n)))            # orthonormal directions
    coeff = g.standard_normal((m, rank))
    sig = SIGNAL_AMP * (coeff @ basis[:, :rank].T)                # signal in the top-`rank` subspace (amp so spectrum drops at `rank`)
    noise = 0.3 * g.standard_normal((m, n))                       # isotropic structural noise (all dims)
    K = sig + noise
    return (K / (np.linalg.norm(K, axis=1, keepdims=True) + 1e-9)).astype(np.float32)


def pca_basis(K):
    """eigendecomposition of the key covariance -> (eigvals desc, eigvecs (n x n) cols sorted desc)."""
    Kc = K - K.mean(0)
    cov = Kc.T @ Kc / len(K)
    w, V = np.linalg.eigh(cov)
    order = np.argsort(w)[::-1]
    return w[order], V[:, order]


def select_k(eigvals, var_retain):
    """smallest k capturing >= var_retain of total variance (measurement-driven dim selection)."""
    csum = np.cumsum(eigvals) / (eigvals.sum() + 1e-12)
    return int(np.searchsorted(csum, var_retain) + 1)


def recall_at_k(K, V, k, sigma_frac, seed):
    """KV recall from a NOISED query, in the top-k PCA subspace (k=N -> full space). out-of-sample noise.
    sigma_frac = query-noise NORM as a fraction of the unit key norm (per-dim sigma = sigma_frac/sqrt(n))."""
    g = np.random.default_rng(seed * 31 + 9)
    n = K.shape[1]; sigma = sigma_frac / np.sqrt(n)              # so total noise norm ~ sigma_frac of the unit key
    Pk = V[:, :k]                                                 # n x k projection
    Kp = K @ Pk
    Q = K + sigma * g.standard_normal(K.shape).astype(np.float32)
    Qp = Q @ Pk
    # nearest-key by cosine in the k-subspace
    Kn = Kp / (np.linalg.norm(Kp, axis=1, keepdims=True) + 1e-9)
    Qn = Qp / (np.linalg.norm(Qp, axis=1, keepdims=True) + 1e-9)
    pred = np.argmax(Qn @ Kn.T, axis=1)
    return float((pred == np.arange(len(K))).mean())


def run_unit(rank, seed):
    K = make_keys(M, N, rank, seed * 7 + 1)
    eigvals, V = pca_basis(K)
    k_sel = select_k(eigvals, VAR_RETAIN)
    r_sel = recall_at_k(K, V, k_sel, SIGMA_FRAC, seed)                 # Arm1: selector k
    r_half = recall_at_k(K, V, max(1, N // 2), SIGMA_FRAC, seed)       # Arm2: naive k=N/2
    r_full = recall_at_k(K, V, N, SIGMA_FRAC, seed)                    # Arm3: no-cut k=N
    return {"rank": rank, "seed": seed, "k_sel": k_sel, "recall_selector": round(r_sel, 4),
            "recall_naive_half": round(r_half, 4), "recall_full": round(r_full, 4)}


def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})
    by_rank = {}
    for u in units:
        by_rank.setdefault(u["rank"], []).append(u)
    per_rank = {}
    for r, us in sorted(by_rank.items()):
        def col(key): return [u[key] for u in us]
        m_sel = float(np.mean(col("recall_selector"))); m_half = float(np.mean(col("recall_naive_half"))); m_full = float(np.mean(col("recall_full")))
        # per-seed margins (robust beat = mean > 2*std, the LEVER #4 discipline)
        mg_full = [u["recall_selector"] - u["recall_full"] for u in us]
        mg_half = [u["recall_selector"] - u["recall_naive_half"] for u in us]
        def robust(mg): return bool(np.mean(mg) > 0.03 and np.mean(mg) > 2 * np.std(mg))
        per_rank[r] = {"anisotropy": ("isotropic" if r >= N else ("anisotropic" if r <= N // 8 else "mid")),
                       "k_sel_mean": round(float(np.mean(col("k_sel"))), 1), "recall_selector": round(m_sel, 3),
                       "recall_naive_half": round(m_half, 3), "recall_full": round(m_full, 3),
                       "margin_vs_full_mean": round(float(np.mean(mg_full)), 4), "margin_vs_half_mean": round(float(np.mean(mg_half)), 4),
                       "ROBUST_beats_full": robust(mg_full), "ROBUST_beats_half": robust(mg_half),
                       "never_worse_than_full": bool(np.mean(mg_full) >= -0.03),
                       "seed_cv": round(float(np.std(col("recall_selector")) / (np.mean(col("recall_selector")) + 1e-9)), 4)}
    aniso = [r for r in per_rank if per_rank[r]["anisotropy"] == "anisotropic"]
    iso = [r for r in per_rank if per_rank[r]["anisotropy"] == "isotropic"]
    win_aniso = [r for r in aniso if per_rank[r]["ROBUST_beats_full"] and per_rank[r]["ROBUST_beats_half"]]
    never_worse_all = all(per_rank[r]["never_worse_than_full"] for r in per_rank)
    seed_stable = all(per_rank[r]["seed_cv"] < 0.10 for r in per_rank)
    detail = {"per_rank": {("rank%d" % r): per_rank[r] for r in per_rank},
              "anisotropic_ranks": aniso, "isotropic_ranks": iso, "ranks_PCA_robustly_helps": win_aniso,
              "never_worse_than_full_all": never_worse_all, "seed_stable": seed_stable, "N": N, "sigma_frac": SIGMA_FRAC,
              "honest_claim": ("PCA dimension-selector measured on RECALL (non-circular). PCA-to-top-k denoises a noised query "
                               "by dropping tail noise dims; it HELPS iff keys are ANISOTROPIC (signal in r<<N dims). The selector "
                               "picks k from the variance spectrum. Win = robustly beats full-N (denoise) AND naive-half on the "
                               "anisotropic regime; on isotropic keys PCA loses (no noise-only dims to drop) = honest negative bound.")}
    summary = "PCA_robustly_helps(aniso)=%s | never_worse_full_all=%s seed_stable=%s | per_rank=%s" % (
        win_aniso, never_worse_all, seed_stable,
        {("r%d" % r): (per_rank[r]["anisotropy"], "k=%.0f" % per_rank[r]["k_sel_mean"], "sel=%.2f full=%.2f half=%.2f" % (
            per_rank[r]["recall_selector"], per_rank[r]["recall_full"], per_rank[r]["recall_naive_half"])) for r in per_rank})
    if not aniso:
        return ("UNKNOWN", "no anisotropic rank tested. " + summary, detail)
    if win_aniso and never_worse_all and seed_stable:
        return ("HARD_PASS", "HARD_PASS (PCA dim-selector; data-decides -> Skunkworks): on the ANISOTROPIC regime %s the selector "
                "ROBUSTLY beats both full-N (genuine denoising: drops tail noise dims of the query) AND naive-half (measurement-driven "
                "k beats a fixed cut), per-seed margin > seed-noise; NEVER worse than full-N on any regime. PCA-dim-selection genuinely "
                "improves noised-query recall when keys are anisotropic. " % win_aniso + summary, detail)
    if never_worse_all and not win_aniso:
        return ("MEASURED_MECHANISM", "MEASURED_MECHANISM (Director realistic peg): PCA-selector never HURTS recall but does not robustly "
                "BEAT full-N even on anisotropic keys -> no genuine denoising win in the tested regime (or the win is within seed-noise). " + summary, detail)
    return ("MIDDLE_BAND", "MIDDLE_BAND: partial (PCA helps some regimes but worse on others, or not seed-stable). " + summary, detail)


def _selftest():
    K = make_keys(80, 64, 4, 1)                                  # strongly anisotropic (rank 4 of 64)
    eig, V = pca_basis(K)
    k = select_k(eig, 0.90)
    assert 1 <= k <= 64, "selected k in range, got %d" % k
    r_full = recall_at_k(K, V, 64, 0.7, 1); r_k = recall_at_k(K, V, k, 0.7, 1)
    assert r_k >= r_full - 0.05, "on rank-4 keys PCA-k should not hurt recall vs full (denoising), got k=%.2f full=%.2f" % (r_k, r_full)
    print("[selftest] PASS: make_keys + pca_basis + select_k(%d) + recall (k>=full-eps on anisotropic)" % k, flush=True)


_selftest()
if _ARGS.self_test:
    raise SystemExit(0)

print("[config] %s mode=%s N=%d M=%d sigma_frac=%.1f var_retain=%.2f ranks=%s seeds=%s" % (
    ANCHOR_NAME, RUN_MODE, N, M, SIGMA_FRAC, VAR_RETAIN, RANKS, SEEDS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); run_config = {"run_mode": RUN_MODE}; t0 = time.time()
for r in RANKS:
    for sd in SEEDS:
        key = "rank%d_s%d" % (r, sd)
        if key in aggregate_partials(out_dir, [key], run_config=run_config):
            print("[ckpt] %s done; skip" % key, flush=True); continue
        res = run_unit(r, sd)
        write_partial_key(out_dir, key, res)
        print("[unit] rank=%d s=%d k_sel=%d sel=%.3f full=%.3f half=%.3f" % (r, sd, res["k_sel"], res["recall_selector"], res["recall_full"], res["recall_naive_half"]), flush=True)
keys = ["rank%d_s%d" % (r, sd) for r in RANKS for sd in SEEDS]
units = list(aggregate_partials(out_dir, keys, run_config=run_config).values())
verdict, msg, detail = compute_verdict(units)
print("\n[VERDICT] " + msg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg, "run_mode": RUN_MODE, "N": N, "M": M,
           "sigma_frac": SIGMA_FRAC, "var_retain": VAR_RETAIN, "ranks": RANKS, "n_seeds": len(SEEDS), "detail": detail,
           "metrics_source": "measured_cpu_pca_dim_selector_recall_anisotropy", "per_unit": units, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, units)
print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
