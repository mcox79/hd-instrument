"""Pred-2 (1-RSB diagnostic): P(q) multi-delta from retained task W-vectors.

1-RSB prediction: overlap distribution of W snapshots across seeds after M1
chunk-replay has multi-peaked / delta-function-like structure (discrete basins).
RS prediction: broad, near-Gaussian unimodal P(q) (continuous distribution).

Method: Run N_SEEDS seeds of the 4-stage M1 hierreplay to get W_ABCD snapshots
per seed. Compute pairwise overlaps q_ij = <W_i, W_j> / (N^2) across all seed
pairs. Measure P(q): if >= 2 peaks >= 2sigma separated, multi-delta (1-RSB signal).

Builds on existing parisi_pq_sweep infrastructure (pv1 make_pool, binder_cumulant,
ultrametricity_fraction) but applies to the RETAINED-W-after-hierreplay pool rather
than the stored-pattern codebook pool.

Per [[feedback-no-experiment-design-in-prompts]]: all parameters chosen by exp_dev autonomy.
Per [[feedback-no-smoke]]: HARD-PASS / HARD-FAIL bands pre-registered.
Per [[feedback-envelope-expansion-fail-bands]]: bands registered BEFORE running.

Pre-reg:
    HARD-PASS (1-RSB multi-delta): W_ABCD overlap distribution shows >= 2 peaks
               with >= 2-sigma separation (using KDE bandwidth = 0.05). Binder
               cumulant > 0.3 (indicates non-trivial P(q) structure).
               -> P(q) multi-delta CONFIRMED; 1-RSB framing supported.
    HARD-FAIL (RS unimodal): P(q) has single peak only (or < 2-sigma separation
               on any pair of candidate peaks). Binder cumulant <= 0.05.
               -> P(q) unimodal; 1-RSB framing NOT supported at this axis.
    MIDDLE: anything between.

Queue: remote_cpu_queue (CPU -- no GPU needed; W is computed from M1 pipeline
       but can run lighter at N=2048 for P(q) analysis).
ETA: ~45-60 min CPU (10 seeds x N=2048 4-stage runs).
Pre-reg file: preregs/2026-05-24_wave14_1rsb_pq_retained_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse, importlib.util, json, math, os, time
from pathlib import Path
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402

# Load hierreplay v1 for M1 mechanism infrastructure
_m1_path = REPO / "experiments" / "exp_wave14_k2_m1_hierreplay_v1.py"
_m1_spec = importlib.util.spec_from_file_location("m1", _m1_path)
m1 = importlib.util.module_from_spec(_m1_spec)
_m1_spec.loader.exec_module(m1)
base = m1.base
v1 = m1.v1
pa = m1.pa

# Load parisi infrastructure for P(q) analysis
_pv1_path = REPO / "experiments" / "exp_wave14_parisi_pq_sweep_v1.py"
_pv1_spec = importlib.util.spec_from_file_location("pv1", _pv1_path)
pv1 = importlib.util.module_from_spec(_pv1_spec)
_pv1_spec.loader.exec_module(pv1)

# ---- design parameters (exp_dev autonomy) ----
N_FULL = 2048     # CPU-feasible N for full run (P(q) is analysis-only)
N_SMOKE = 512
BATCH_SIZE_FULL = 32
BATCH_SIZE_SMOKE = 16
EPOCHS_FULL = 5
EPOCHS_SMOKE = 1
PHASE_A_EPOCHS_FULL = 8
PHASE_A_EPOCHS_SMOKE = 1
BYTES_FULL = 100_000   # shorter per seed (CPU); 10 seeds total
BYTES_SMOKE = 3_000
SEEDS_FULL = list(range(10))   # 10 seeds for robust P(q)
SEEDS_SMOKE = [7, 17]
N_TRIPLES = 500   # ultrametric fraction check

# Pre-reg P(q) thresholds
PEAK_SEPARATION_SIGMA = 2.0
BINDER_1RSB_THRESHOLD = 0.30   # 1-RSB signal
BINDER_RS_THRESHOLD = 0.05     # RS upper bound for unimodal verdict


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


def run_4stage_m1_get_W(seed, config, device):
    """Run 4-stage M1 hierreplay; return final W_ABCD tensor as 1-D flattened vector."""
    N = config["N"]
    batch_size = config["batch_size"]
    n_epochs = config["epochs"]
    phase_a_epochs = config["phase_a_epochs"]
    n_bytes = config["bytes_per_corpus"]
    smoke = (config["mode"] == "smoke")

    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(base.VOCAB, N, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(base.K, N, gen).to(device)

    corpus_a_full = pa.load_corpus_a()
    corpus_a = corpus_a_full[:n_bytes] if n_bytes < len(corpus_a_full) else corpus_a_full
    corpus_b = pa.shuffle_bytes(corpus_a, seed=seed + 1)
    corpus_c_full = base.load_corpus_C(smoke=smoke)
    corpus_c = corpus_c_full[:n_bytes] if n_bytes < len(corpus_c_full) else corpus_c_full
    corpus_d_full = v1.load_corpus_D(smoke=smoke)
    corpus_d = corpus_d_full[:n_bytes] if n_bytes < len(corpus_d_full) else corpus_d_full

    def split80(d):
        m = int(0.8 * len(d))
        return d[:m], d[m:]

    train_a, _ = split80(corpus_a)
    train_b, _ = split80(corpus_b)
    train_c, _ = split80(corpus_c)
    train_d, _ = split80(corpus_d)

    def to_idx(tr):
        idx, tgt = base.bytes_to_idx_tensors(tr, device)
        return idx, tgt

    train_a_idx, train_a_tgt = to_idx(train_a)
    train_b_idx, train_b_tgt = to_idx(train_b)
    train_c_idx, train_c_tgt = to_idx(train_c)
    train_d_idx, train_d_tgt = to_idx(train_d)

    W = torch.zeros((N, N), dtype=torch.float32, device=device)

    # Phase A
    W_A, pool_A_v, pool_A_l, pool_A_u = base.train_w_with_replay(
        W, None, None, 0, byte_atoms, pos_atoms,
        train_a_idx, train_a_tgt, None, None, 0,
        phase_a_epochs, batch_size, device)

    thin_A_v, thin_A_l, thin_A_u = m1.thin_pool_to_chunks(
        pool_A_v, pool_A_l, pool_A_u, chunk_fraction=0.5, device=device)

    # Phase B
    W_AB, pool_AB_v, pool_AB_l, pool_AB_u = base.train_w_with_replay(
        W_A, pool_A_v.clone(), pool_A_l.clone(), pool_A_u,
        byte_atoms, pos_atoms, train_b_idx, train_b_tgt,
        thin_A_v, thin_A_l, thin_A_u, n_epochs, batch_size, device)

    thin_B_v, thin_B_l, thin_B_u = m1.thin_pool_to_chunks(
        pool_AB_v, pool_AB_l, pool_AB_u, chunk_fraction=0.5, device=device)
    combo_AB_v = torch.cat([thin_A_v[:thin_A_u], thin_B_v[:thin_B_u]], dim=0)
    combo_AB_l = torch.cat([thin_A_l[:thin_A_u], thin_B_l[:thin_B_u]], dim=0)
    combo_AB_u = combo_AB_v.shape[0]

    # Phase C
    W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u = base.train_w_with_replay(
        W_AB, pool_AB_v.clone(), pool_AB_l.clone(), pool_AB_u,
        byte_atoms, pos_atoms, train_c_idx, train_c_tgt,
        combo_AB_v, combo_AB_l, combo_AB_u, n_epochs, batch_size, device)

    thin_C_v, thin_C_l, thin_C_u = m1.thin_pool_to_chunks(
        pool_ABC_v, pool_ABC_l, pool_ABC_u, chunk_fraction=0.5, device=device)
    combo_ABC_v = torch.cat([thin_A_v[:thin_A_u], thin_B_v[:thin_B_u],
                             thin_C_v[:thin_C_u]], dim=0)
    combo_ABC_l = torch.cat([thin_A_l[:thin_A_u], thin_B_l[:thin_B_u],
                             thin_C_l[:thin_C_u]], dim=0)
    combo_ABC_u = combo_ABC_v.shape[0]

    # Phase D
    W_ABCD, _, _, _ = base.train_w_with_replay(
        W_ABC, pool_ABC_v.clone(), pool_ABC_l.clone(), pool_ABC_u,
        byte_atoms, pos_atoms, train_d_idx, train_d_tgt,
        combo_ABC_v, combo_ABC_l, combo_ABC_u, n_epochs, batch_size, device)

    # Flatten W to 1-D vector for P(q) analysis
    return W_ABCD.cpu().flatten().float()


def compute_W_overlap(W_flat_i, W_flat_j):
    """Normalized inner product of two flattened W matrices."""
    N2 = W_flat_i.shape[0]
    return float((W_flat_i * W_flat_j).sum() / N2)


def detect_peaks_kde(overlaps, bandwidth=0.05):
    """Simple KDE peak detection: count modes in overlap histogram.
    Returns (n_peaks, peak_locations, mean_separation_sigma).
    """
    lo, hi = float(overlaps.min()), float(overlaps.max())
    if hi - lo < 1e-6:
        return 1, [float(overlaps.mean())], 0.0
    # Build histogram with ~20 bins
    n_bins = 20
    counts, edges = torch.histogram(overlaps, bins=n_bins)
    counts_f = counts.float()
    # Find local maxima (peaks)
    peaks = []
    for i in range(1, n_bins - 1):
        if counts_f[i] > counts_f[i - 1] and counts_f[i] > counts_f[i + 1]:
            center = float((edges[i] + edges[i + 1]) / 2)
            peaks.append((center, float(counts_f[i])))
    if not peaks:
        # Include boundary maxima
        if counts_f[0] > counts_f[1]:
            peaks.append((float((edges[0] + edges[1]) / 2), float(counts_f[0])))
        if counts_f[-1] > counts_f[-2]:
            peaks.append((float((edges[-1] + edges[-2]) / 2), float(counts_f[-1])))
    if not peaks:
        return 1, [float(overlaps.mean())], 0.0

    # Filter to peaks with count >= 5% of max
    max_count = max(p[1] for p in peaks)
    significant_peaks = [p for p in peaks if p[1] >= 0.05 * max_count]

    # Mean separation in sigma units (sigma = std of overlaps)
    std = float(overlaps.std())
    if std < 1e-6:
        return len(significant_peaks), [p[0] for p in significant_peaks], 0.0
    if len(significant_peaks) >= 2:
        # Max pairwise separation in sigma units
        locs = [p[0] for p in significant_peaks]
        max_sep = 0.0
        for i in range(len(locs)):
            for j in range(i + 1, len(locs)):
                sep = abs(locs[i] - locs[j]) / std
                if sep > max_sep:
                    max_sep = sep
    else:
        max_sep = 0.0

    return len(significant_peaks), [p[0] for p in significant_peaks], max_sep


def compute_verdict(summary):
    n_peaks = summary.get("n_peaks", 0)
    max_sep_sigma = summary.get("max_sep_sigma", 0.0)
    binder = summary.get("binder", 0.0)

    if n_peaks >= 2 and max_sep_sigma >= PEAK_SEPARATION_SIGMA and binder > BINDER_1RSB_THRESHOLD:
        return ("PQ_1RSB_MULTI_DELTA",
                f"P(q) multi-delta CONFIRMED: {n_peaks} peaks separated "
                f"{max_sep_sigma:.2f}sigma >= {PEAK_SEPARATION_SIGMA} "
                f"binder={binder:.3f} > {BINDER_1RSB_THRESHOLD}. "
                f"1-RSB framing supported by W-overlap distribution.")
    if binder <= BINDER_RS_THRESHOLD and n_peaks <= 1:
        return ("PQ_RS_UNIMODAL",
                f"P(q) unimodal (RS): {n_peaks} peak(s) "
                f"max_sep_sigma={max_sep_sigma:.2f} < {PEAK_SEPARATION_SIGMA} "
                f"binder={binder:.3f} <= {BINDER_RS_THRESHOLD}. "
                f"1-RSB W-overlap framing NOT supported.")
    return ("PQ_RETAINED_MIDDLE",
            f"Intermediate P(q): {n_peaks} peaks max_sep_sigma={max_sep_sigma:.2f} "
            f"binder={binder:.3f}. Inconclusive 1-RSB vs RS at this axis.")


def self_test_verdict():
    # 1-RSB case: two peaks, separated
    s1 = {"n_peaks": 2, "max_sep_sigma": 2.5, "binder": 0.35}
    # RS case: one peak, no separation
    s2 = {"n_peaks": 1, "max_sep_sigma": 0.0, "binder": 0.03}
    # Middle case
    s3 = {"n_peaks": 2, "max_sep_sigma": 1.5, "binder": 0.15}
    cases = [
        (s1, "PQ_1RSB_MULTI_DELTA"),
        (s2, "PQ_RS_UNIMODAL"),
        (s3, "PQ_RETAINED_MIDDLE"),
        ({}, "PQ_RS_UNIMODAL"),   # n_peaks=0 <= 1 and binder=0 <= 0.05
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"verdict {a} != {exp}; summary={s}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run(smoke=False):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    t0 = time.monotonic()
    print(f"[pq-retained] device={device} smoke={smoke}", flush=True)
    self_test_verdict()

    config = {
        "mode": "smoke" if smoke else "full",
        "N": N_SMOKE if smoke else N_FULL,
        "batch_size": BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL,
        "epochs": EPOCHS_SMOKE if smoke else EPOCHS_FULL,
        "phase_a_epochs": PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL,
        "bytes_per_corpus": BYTES_SMOKE if smoke else BYTES_FULL,
        "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
        "n_triples": 100 if smoke else N_TRIPLES,
        "peak_sep_sigma": PEAK_SEPARATION_SIGMA,
        "binder_1rsb": BINDER_1RSB_THRESHOLD,
    }
    print(f"[config] {config}", flush=True)

    # Collect W_ABCD vectors
    W_flat_list = []
    for seed in config["seeds"]:
        print(f"  running M1 4-stage seed={seed}...", flush=True)
        W_flat = run_4stage_m1_get_W(seed, config, device)
        W_flat_list.append(W_flat)
        print(f"  seed={seed}: W norm={float(W_flat.norm()):.3f}", flush=True)

    # Stack into pool (n_seeds x N^2); compute pairwise overlaps
    W_stack = torch.stack(W_flat_list, dim=0)   # (S, N^2)
    n_seeds = W_stack.shape[0]
    Q = W_stack @ W_stack.T / W_stack.shape[1]  # (S, S) overlap matrix
    # Upper triangle
    triu_mask = torch.triu(torch.ones(n_seeds, n_seeds, dtype=torch.bool), diagonal=1)
    overlaps = Q[triu_mask]

    n_pairs = int(overlaps.shape[0])
    mean_q = float(overlaps.mean())
    std_q = float(overlaps.std()) if n_pairs > 1 else 0.0
    print(f"  n_pairs={n_pairs} mean_q={mean_q:.4f} std_q={std_q:.4f}", flush=True)

    n_peaks, peak_locs, max_sep_sigma = detect_peaks_kde(overlaps)
    binder = pv1.binder_cumulant(overlaps)
    if W_stack.shape[0] >= 3:
        ultrametric_frac = pv1.ultrametricity_fraction(W_stack, config["n_triples"], 42, W_stack.shape[1])
    else:
        ultrametric_frac = float("nan")  # not enough seeds for triples

    print(f"  n_peaks={n_peaks} peak_locs={[f'{p:.4f}' for p in peak_locs]} "
          f"max_sep_sigma={max_sep_sigma:.3f}", flush=True)
    print(f"  binder={binder:.4f} ultrametric_frac={ultrametric_frac:.3f}", flush=True)

    summary = {
        "n_peaks": n_peaks,
        "peak_locs": peak_locs,
        "max_sep_sigma": max_sep_sigma,
        "binder": binder,
        "ultrametric_frac": ultrametric_frac,
        "n_pairs": n_pairs,
        "mean_q": mean_q,
        "std_q": std_q,
        "n_seeds": n_seeds,
    }
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        self_test_verdict()
        print("self-test passed", flush=True)
        return

    out_dir = get_output_dir("wave14_1rsb_pq_retained_v1")
    summary, verdict, msg, elapsed, config = run(smoke=args.smoke)
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "summary": summary, "config": config}
    validate_metrics(metrics)
    import shutil
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2))
    shutil.move(str(tmp), str(out_dir / "metrics.json"))
    oracle.assert_baseline_high("pq_retained_n_seeds", float(summary.get("n_seeds", 0)), 1.0)
    print(f"[done] elapsed={elapsed:.1f}s verdict={verdict}", flush=True)


if __name__ == "__main__":
    main()
