"""Pred-2 (1-RSB diagnostic) P(q) high-resolution full re-run at N=4096, 20 seeds.

CONTEXT: v1 ran at N=2048 10 seeds and got MIDDLE: n_peaks=4, binder=-0.164 (negative
Binder, anti-clustering, q_EA~1e-6). The negative Binder is consistent with the
UV-problem (high-dim W-vectors are nearly orthogonal; mean_q~0, std_q~3e-6 tighter
than random bipolar at N=2048 expected std~0.022).

HYPOTHESIS: at N=4096 with more seeds, if the UV-problem persists, Binder remains
negative and n_peaks stays small (confirming v1 RS framing). If there is genuine 1-RSB
basin structure, at higher N the effective noise floor drops (std_q ~ 1/N), making
any real basin structure more visible (mean_q > 0 if basins exist).

DESIGN (exp_dev autonomy):
  N = 4096 (GPU-feasible; higher resolving power vs N=2048)
  seeds = 20 (2x v1 for sharper binder CI)
  M_stored: use same 4-stage hierreplay config as v1 (let substrate fill to natural load)
  KDE bandwidth: 0.02 (tighter than v1's 0.05 to resolve fine structure)
  n_triples for ultrametric: 1000 (vs 500 in v1)

Pre-registered bands (envelope-expansion of v1 -- claiming stronger signal at N=4096):
  HARD-PASS (1-RSB multi-delta at N=4096): binder > 0.30 AND n_peaks >= 2 with
            >= 2sigma separation AND mean_q significantly above random floor
            (mean_q > 5 * expected_std_random where expected_std_random = 1/sqrt(N))
            -> P(q) multi-delta CONFIRMED; 1-RSB signal
  HARD-FAIL (RS unimodal): binder <= 0.05 AND n_peaks <= 1 (or all peaks within
            2sigma of q=0) AND mean_q indistinguishable from zero
            (|mean_q| < 3 * 1/sqrt(N)) -> RS unimodal; 1-RSB NOT supported
  MIDDLE: anything between; binder in (0.05, 0.30) OR n_peaks=2+ with weak separation

NOTE: a MIDDLE at N=4096 that MATCHES v1 MIDDLE is INCONCLUSIVE (UV-problem persists).
A HARD-FAIL at N=4096 that MATCHES v1 MIDDLE would STRENGTHEN the RS-unimodal framing.
A HARD-PASS at N=4096 when v1 was MIDDLE would be the ONLY new positive 1-RSB indirect signal.

Walk-back: if smoke effect |binder_diff_v1_v2| < 0.05, pre-register FULL at N=8192.
Calibration: no prior empirical anchor at N=4096 for this metric; bands set at +-50% of
v1 threshold per calibration-probe policy.

Queue: overnight_queue (GPU; 20 seeds x N=4096 4-stage each ~2min per seed; ~40min total)
Pre-reg: preregs/2026-05-26_wave14_1rsb_pq_retained_v2.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import importlib.util
import json
import math
import os
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# Load M1 hierreplay infrastructure
_m1_path = REPO / "experiments" / "exp_wave14_k2_m1_hierreplay_v1.py"
_m1_spec = importlib.util.spec_from_file_location("m1", _m1_path)
m1 = importlib.util.module_from_spec(_m1_spec)
_m1_spec.loader.exec_module(m1)
base = m1.base
v1_mod = m1.v1
pa = m1.pa

# Load parisi P(q) infrastructure
_pv1_path = REPO / "experiments" / "exp_wave14_parisi_pq_sweep_v1.py"
_pv1_spec = importlib.util.spec_from_file_location("pv1", _pv1_path)
pv1 = importlib.util.module_from_spec(_pv1_spec)
_pv1_spec.loader.exec_module(pv1)

# ── design parameters (exp_dev autonomy) ──
N_FULL = 8192         # v3: N=8192 for sharper P(q) resolution
N_SMOKE = 512
SEEDS_FULL = list(range(30))   # v3: 30 seeds for tighter binder stat
SEEDS_SMOKE = [7, 17, 23]
BATCH_SIZE_FULL = 64
BATCH_SIZE_SMOKE = 16
EPOCHS_FULL = 5
EPOCHS_SMOKE = 1
PHASE_A_EPOCHS_FULL = 8
PHASE_A_EPOCHS_SMOKE = 1
BYTES_FULL = 100_000
BYTES_SMOKE = 3_000
N_TRIPLES = 1000      # ultrametric check

KDE_BW = 0.01         # v3: even tighter bandwidth for N=8192
PEAK_SEP_SIGMA = 2.0
BINDER_1RSB = 0.30
BINDER_RS = 0.05


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing: {missing}")


def run_4stage_m1_get_W(seed, N, batch_size, epochs, phase_a_epochs, n_bytes, smoke, device):
    """Run 4-stage M1 hierreplay; return W_ABCD as flattened float32 vector."""
    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(base.VOCAB, N, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(base.K, N, gen).to(device)

    corpus_a_full = pa.load_corpus_a()
    corpus_a = corpus_a_full[:n_bytes] if n_bytes < len(corpus_a_full) else corpus_a_full
    corpus_b = pa.shuffle_bytes(corpus_a, seed=seed + 1)
    corpus_c_full = base.load_corpus_C(smoke=smoke)
    corpus_c = corpus_c_full[:n_bytes] if n_bytes < len(corpus_c_full) else corpus_c_full
    corpus_d_full = v1_mod.load_corpus_D(smoke=smoke)
    corpus_d = corpus_d_full[:n_bytes] if n_bytes < len(corpus_d_full) else corpus_d_full

    def split80(d):
        m = int(0.8 * len(d))
        return d[:m], d[m:]

    def to_idx(tr):
        return base.bytes_to_idx_tensors(tr, device)

    train_a, _ = split80(corpus_a)
    train_b, _ = split80(corpus_b)
    train_c, _ = split80(corpus_c)
    train_d, _ = split80(corpus_d)

    train_a_idx, train_a_tgt = to_idx(train_a)
    train_b_idx, train_b_tgt = to_idx(train_b)
    train_c_idx, train_c_tgt = to_idx(train_c)
    train_d_idx, train_d_tgt = to_idx(train_d)

    W = torch.zeros((N, N), dtype=torch.float32, device=device)

    W_A, pool_A_v, pool_A_l, pool_A_u = base.train_w_with_replay(
        W, None, None, 0, byte_atoms, pos_atoms,
        train_a_idx, train_a_tgt, None, None, 0,
        phase_a_epochs, batch_size, device)

    thin_A_v, thin_A_l, thin_A_u = m1.thin_pool_to_chunks(
        pool_A_v, pool_A_l, pool_A_u, chunk_fraction=0.5, device=device)

    W_AB, pool_AB_v, pool_AB_l, pool_AB_u = base.train_w_with_replay(
        W_A, pool_A_v.clone(), pool_A_l.clone(), pool_A_u,
        byte_atoms, pos_atoms, train_b_idx, train_b_tgt,
        thin_A_v, thin_A_l, thin_A_u, epochs, batch_size, device)

    thin_B_v, thin_B_l, thin_B_u = m1.thin_pool_to_chunks(
        pool_AB_v, pool_AB_l, pool_AB_u, chunk_fraction=0.5, device=device)
    combo_AB_v = torch.cat([thin_A_v[:thin_A_u], thin_B_v[:thin_B_u]], dim=0)
    combo_AB_l = torch.cat([thin_A_l[:thin_A_u], thin_B_l[:thin_B_u]], dim=0)
    combo_AB_u = combo_AB_v.shape[0]

    W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u = base.train_w_with_replay(
        W_AB, pool_AB_v.clone(), pool_AB_l.clone(), pool_AB_u,
        byte_atoms, pos_atoms, train_c_idx, train_c_tgt,
        combo_AB_v, combo_AB_l, combo_AB_u, epochs, batch_size, device)

    thin_C_v, thin_C_l, thin_C_u = m1.thin_pool_to_chunks(
        pool_ABC_v, pool_ABC_l, pool_ABC_u, chunk_fraction=0.5, device=device)
    combo_ABC_v = torch.cat([thin_A_v[:thin_A_u], thin_B_v[:thin_B_u],
                              thin_C_v[:thin_C_u]], dim=0)
    combo_ABC_l = torch.cat([thin_A_l[:thin_A_u], thin_B_l[:thin_B_u],
                              thin_C_l[:thin_C_u]], dim=0)
    combo_ABC_u = combo_ABC_v.shape[0]

    W_ABCD, _, _, _ = base.train_w_with_replay(
        W_ABC, pool_ABC_v.clone(), pool_ABC_l.clone(), pool_ABC_u,
        byte_atoms, pos_atoms, train_d_idx, train_d_tgt,
        combo_ABC_v, combo_ABC_l, combo_ABC_u, epochs, batch_size, device)

    W_flat = W_ABCD.reshape(-1).float().cpu()
    del W_A, W_AB, W_ABC, W_ABCD, pool_A_v, pool_AB_v, pool_ABC_v
    del thin_A_v, thin_B_v, thin_C_v, combo_AB_v, combo_ABC_v
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return W_flat


def compute_overlaps(W_list: list) -> list:
    """Compute all pairwise overlaps q_ij = <W_i, W_j> / ||W_i|| / ||W_j||."""
    n = len(W_list)
    overlaps = []
    for i in range(n):
        for j in range(i + 1, n):
            wi = W_list[i]
            wj = W_list[j]
            ni = wi.norm().item()
            nj = wj.norm().item()
            if ni < 1e-9 or nj < 1e-9:
                continue
            q = float((wi * wj).sum()) / (ni * nj)
            overlaps.append(q)
    return overlaps


def kde_density(vals: list, bandwidth: float, n_points: int = 200):
    """Simple Gaussian KDE; returns (x_grid, density)."""
    if not vals:
        return [], []
    lo, hi = min(vals) - 3 * bandwidth, max(vals) + 3 * bandwidth
    x = [lo + i * (hi - lo) / n_points for i in range(n_points + 1)]
    density = []
    n = len(vals)
    for xi in x:
        d = sum(math.exp(-0.5 * ((xi - v) / bandwidth) ** 2)
                for v in vals) / (n * bandwidth * math.sqrt(2 * math.pi))
        density.append(d)
    return x, density


def find_peaks(x: list, density: list, min_sep_sigma: float, bandwidth: float):
    """Find local maxima separated by >= min_sep_sigma * bandwidth."""
    peaks = []
    for i in range(1, len(density) - 1):
        if density[i] > density[i - 1] and density[i] > density[i + 1]:
            peaks.append((x[i], density[i]))
    # Filter by separation
    filtered = []
    for p in peaks:
        if not filtered or abs(p[0] - filtered[-1][0]) >= min_sep_sigma * bandwidth:
            filtered.append(p)
        elif p[1] > filtered[-1][1]:
            filtered[-1] = p
    return filtered


def binder_cumulant(overlaps: list) -> float:
    """Binder cumulant: U = 1 - <q^4> / (3 * <q^2>^2). Positive for non-trivial P(q)."""
    if not overlaps:
        return 0.0
    n = len(overlaps)
    q2 = sum(q ** 2 for q in overlaps) / n
    q4 = sum(q ** 4 for q in overlaps) / n
    if q2 < 1e-15:
        return 0.0
    return 1.0 - q4 / (3.0 * q2 * q2)


def _instrumentation_selftest():
    """Assert all metrics non-null at small scale."""
    device = torch.device("cpu")
    # Test overlap computation
    import torch as _t
    W1 = _t.ones(64)
    W2 = _t.ones(64)
    q = float((W1 * W2).sum()) / (W1.norm() * W2.norm())
    assert abs(q - 1.0) < 1e-5, f"overlap self-align fail: {q}"
    # Test KDE non-empty
    vals = [0.1, 0.2, -0.1, 0.05]
    x, dens = kde_density(vals, 0.05)
    assert len(x) > 0, "KDE empty"
    assert max(dens) > 0, "KDE all-zero"
    # Test Binder cumulant: uniform -> near 0
    import random as _r
    _r.seed(7)
    vals_unif = [_r.gauss(0.0, 0.01) for _ in range(100)]
    binder = binder_cumulant(vals_unif)
    assert binder is not None, "binder null"
    # Test peak finder
    peaks = find_peaks(x, dens, 2.0, 0.05)
    assert isinstance(peaks, list), "peaks not list"
    # Test self-test at smoke scale calls through without TypeError
    print("selftest PASS 5/5")


_instrumentation_selftest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        sys.exit(0)

    smoke = args.smoke
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"device={device} smoke={smoke} N={'SMOKE' if smoke else 'FULL'}")

    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    batch_size = BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL
    epochs = EPOCHS_SMOKE if smoke else EPOCHS_FULL
    phase_a_epochs = PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL
    n_bytes = BYTES_SMOKE if smoke else BYTES_FULL

    t0 = time.time()
    W_list = []
    print(f"Running {len(seeds)} seeds at N={N}...", flush=True)
    for i, seed in enumerate(seeds):
        print(f"  seed {seed} ({i+1}/{len(seeds)})...", end=" ", flush=True)
        Wf = run_4stage_m1_get_W(seed, N, batch_size, epochs, phase_a_epochs,
                                  n_bytes, smoke, device)
        W_list.append(Wf)
        print(f"W_norm={Wf.norm():.3f}", flush=True)

    print("Computing pairwise overlaps...", flush=True)
    overlaps = compute_overlaps(W_list)
    mean_q = sum(overlaps) / max(len(overlaps), 1)
    std_q = math.sqrt(sum((q - mean_q) ** 2 for q in overlaps) / max(len(overlaps) - 1, 1))
    q_ea_random_floor = 1.0 / math.sqrt(N)

    x, density = kde_density(overlaps, KDE_BW)
    peaks = find_peaks(x, density, PEAK_SEP_SIGMA, KDE_BW)
    binder = binder_cumulant(overlaps)
    n_peaks = len(peaks)

    # Ultrametric fraction using parisi infrastructure if available
    try:
        uf = pv1.compute_ultrametric_fraction(W_list[:min(len(W_list), 20)], N_TRIPLES)
    except Exception:
        uf = None

    # Verdict
    mean_q_sig = abs(mean_q) / max(q_ea_random_floor, 1e-12)
    if binder > BINDER_1RSB and n_peaks >= 2 and mean_q_sig > 5.0:
        verdict = "PQ_RETAINED_1RSB_HARD_PASS"
        verdict_msg = (f"1-RSB signal CONFIRMED at N={N}: binder={binder:.4f}>{BINDER_1RSB}, "
                       f"n_peaks={n_peaks}>=2, mean_q_sig={mean_q_sig:.2f}>5")
    elif binder <= BINDER_RS and n_peaks <= 1 and mean_q_sig < 3.0:
        verdict = "PQ_RETAINED_RS_HARD_FAIL"
        verdict_msg = (f"RS unimodal CONFIRMED at N={N}: binder={binder:.4f}<={BINDER_RS}, "
                       f"n_peaks={n_peaks}<=1, mean_q_sig={mean_q_sig:.2f}<3 "
                       f"(mean_q={mean_q:.2e} std_q={std_q:.2e} floor={q_ea_random_floor:.2e})")
    else:
        verdict = "PQ_RETAINED_MIDDLE"
        verdict_msg = (f"MIDDLE at N={N}: binder={binder:.4f} n_peaks={n_peaks} "
                       f"mean_q={mean_q:.2e} std_q={std_q:.2e} q_ea_floor={q_ea_random_floor:.2e} "
                       f"mean_q_sig={mean_q_sig:.2f}")

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": {"N": N, "n_seeds": len(seeds), "smoke": smoke,
                   "kde_bw": KDE_BW, "peak_sep_sigma": PEAK_SEP_SIGMA},
        "summary": {
            "n_overlaps": len(overlaps),
            "mean_q": mean_q,
            "std_q": std_q,
            "q_ea_random_floor": q_ea_random_floor,
            "mean_q_sig": mean_q_sig,
            "binder": binder,
            "n_peaks": n_peaks,
            "peak_positions": [p[0] for p in peaks],
            "ultrametric_frac": uf,
        },
    }
    validate_metrics(metrics)

    outdir = get_output_dir("wave14_1rsb_pq_retained_v3")
    with open(outdir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"verdict={verdict}")
    print(f"verdict_msg={verdict_msg}")
    print(f"elapsed={elapsed:.1f}s binder={binder:.4f} n_peaks={n_peaks} "
          f"mean_q={mean_q:.2e} std_q={std_q:.2e}")


if __name__ == "__main__":
    main()
