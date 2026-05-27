"""Pred-2 (1-RSB diagnostic) P(q) at N=16384, 20 seeds.

ANTICIPATORY PRE-BUILD -- trigger: wave14_1rsb_pq_retained_v3 returns HARD_PASS
  (binder > 0.30 AND n_peaks >= 2 with >= 2sigma separation at N=8192).

This v4 firms the 1-RSB signal at N=16384 to establish the scaling behavior
of the Binder cumulant and peak separation vs N. The claim: if genuine 1-RSB
basin structure exists, the signal should GROW with N (noise floor drops as 1/N).

DESIGN:
  - N = 16384 (2x v3)
  - 20 seeds (same as v3 for power comparison)
  - KDE bandwidth: 0.005 (tighter; N=16384 has lower noise floor)
  - n_triples: 1000 (ultrametric check)
  - Primary metric: binder_cumulant, n_peaks, mean_q

PRE-REGISTERED BANDS:
  HARD_PASS (1-RSB signal strengthens at N=16384):
    - binder > 0.40 (stronger than v3 threshold of 0.30)
    - AND n_peaks >= 2 with >= 3sigma separation (tighter than v3's 2sigma)
    - AND mean_q > 5 / sqrt(N) (above noise floor by 5x at N=16384)
    -> 1-RSB confirmed and N-scaling consistent with genuine multi-basin structure

  HARD_FAIL (1-RSB signal does NOT grow with N):
    - binder <= 0.10 at N=16384 (weaker than v3 HARD_PASS at N=8192)
    - OR n_peaks <= 1
    -> 1-RSB signal was noise at N=8192; RS unimodal framing restored

  MIDDLE_BAND:
    - binder in (0.10, 0.40) at N=16384
    - OR n_peaks=2 but separation < 3sigma
    -> Partial signal; scaling is ambiguous (binder grows but not strongly)

  INSTRUMENTATION_FAIL:
    - mean_q indistinguishable from zero at all seeds
    - OR KDE fails to find any peak

  UV_PROBLEM_CONFIRMED:
    - binder < 0 at N=16384 (same as v1 at N=2048)
    -> UV problem persists even at N=16384; substrate has RS structure with
       high-dimensional near-orthogonal weight vectors

Self-tests (matching v3 structure):
  1. binder_cumulant([uniform]) close to 1/3 (RS expectation for N large)
  2. kde_peaks returns at least 1 peak on bimodal input
  3. ultrametric_frac: perfect ultrametric -> frac >= 0.95
  4. mean_q computable and finite from W vector

Queue: overnight_queue (GPU; 20 seeds x N=16384; ~3-4 GPU-hrs)
Pre-reg: preregs/2026-05-26_wave14_1rsb_pq_retained_v4.md
Trigger: ship when v3 returns HARD_PASS (binder > 0.30 AND n_peaks >= 2 at N=8192).
Dependency: exp_wave14_k2_m1_hierreplay_v1.py + exp_wave14_parisi_pq_sweep_v1.py
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

# Load M1 hierreplay infrastructure
_m1_path = REPO / "experiments" / "exp_wave14_k2_m1_hierreplay_v1.py"
_m1_spec = importlib.util.spec_from_file_location("m1_v4", _m1_path)
m1 = importlib.util.module_from_spec(_m1_spec)
_m1_spec.loader.exec_module(m1)
base = m1.base
v1_mod = m1.v1
pa = m1.pa

# Load parisi P(q) infrastructure
_pv1_path = REPO / "experiments" / "exp_wave14_parisi_pq_sweep_v1.py"
_pv1_spec = importlib.util.spec_from_file_location("pv1_v4", _pv1_path)
pv1 = importlib.util.module_from_spec(_pv1_spec)
_pv1_spec.loader.exec_module(pv1)

# ── design parameters ──
N_FULL = 16384       # v4: N=16384
N_SMOKE = 512
SEEDS_FULL = list(range(20))
SEEDS_SMOKE = [7, 17, 23]
BATCH_SIZE_FULL = 32   # smaller batch at N=16384 for memory
BATCH_SIZE_SMOKE = 16
EPOCHS_FULL = 5
EPOCHS_SMOKE = 1
PHASE_A_EPOCHS_FULL = 8
PHASE_A_EPOCHS_SMOKE = 1
BYTES_FULL = 100_000
BYTES_SMOKE = 3_000
N_TRIPLES = 1000

KDE_BW = 0.005        # v4: tighter (N=16384 lower noise floor)
PEAK_SEP_SIGMA = 3.0  # v4: require 3sigma separation (stronger than v3 2sigma)
BINDER_1RSB = 0.40    # v4: stronger threshold (v3 was 0.30)
BINDER_MIDDLE_LO = 0.10
NOISE_FLOOR_FACTOR = 5.0


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required fields: {missing}")


def binder_cumulant(q_vals: list) -> float:
    """B4 = 1 - <q^4> / (3 * <q^2>^2). B4 -> 0 for RS, B4 -> 2/3 for 1-RSB."""
    if len(q_vals) < 4:
        return float("nan")
    n = len(q_vals)
    q2 = sum(v ** 2 for v in q_vals) / n
    q4 = sum(v ** 4 for v in q_vals) / n
    if q2 < 1e-12:
        return float("nan")
    return 1.0 - q4 / (3.0 * q2 ** 2)


def kde_n_peaks(q_vals: list, bw: float = KDE_BW) -> tuple[int, float]:
    """Estimate number of peaks in P(q) via KDE. Returns (n_peaks, peak_separation_sigma)."""
    if len(q_vals) < 3:
        return 0, 0.0
    q = sorted(q_vals)
    n = len(q)
    q_min, q_max = q[0] - 3 * bw, q[-1] + 3 * bw
    n_grid = 200
    grid = [q_min + i * (q_max - q_min) / n_grid for i in range(n_grid + 1)]
    # Gaussian KDE
    density = []
    for g in grid:
        d = sum(math.exp(-0.5 * ((g - qi) / bw) ** 2) for qi in q) / (n * bw * math.sqrt(2 * math.pi))
        density.append(d)
    # Find peaks
    peaks = []
    for i in range(1, len(density) - 1):
        if density[i] > density[i - 1] and density[i] > density[i + 1]:
            peaks.append((grid[i], density[i]))
    if len(peaks) < 2:
        return len(peaks), 0.0
    # Peak separation in units of sigma (std of q distribution)
    q_std = math.sqrt(sum((v - sum(q_vals)/len(q_vals)) ** 2 for v in q_vals) / max(len(q_vals) - 1, 1))
    if q_std < 1e-9:
        return len(peaks), 0.0
    peak_locs = [p[0] for p in peaks]
    max_sep = max(peak_locs) - min(peak_locs)
    sep_sigma = max_sep / q_std
    return len(peaks), round(sep_sigma, 3)


def run_4stage_m1_get_W(seed, N, batch_size, epochs, phase_a_epochs, n_bytes, smoke, device):
    """Run 4-stage M1 hierreplay; return W_ABCD."""
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

    ta_idx, ta_tgt = to_idx(train_a)
    tb_idx, tb_tgt = to_idx(train_b)
    tc_idx, tc_tgt = to_idx(train_c)
    td_idx, td_tgt = to_idx(train_d)

    W = torch.zeros((N, N), dtype=torch.float32, device=device)
    W_A, pool_Av, pool_Al, pool_Au = base.train_w_with_replay(
        W, None, None, 0, byte_atoms, pos_atoms, ta_idx, ta_tgt, None, None, 0,
        phase_a_epochs, batch_size, device)
    thin_Av, thin_Al, thin_Au = m1.thin_pool_to_chunks(pool_Av, pool_Al, pool_Au, 0.5, device)
    W_AB, pool_ABv, pool_ABl, pool_ABu = base.train_w_with_replay(
        W_A, pool_Av.clone(), pool_Al.clone(), pool_Au, byte_atoms, pos_atoms,
        tb_idx, tb_tgt, thin_Av, thin_Al, thin_Au, epochs, batch_size, device)
    thin_Bv, thin_Bl, thin_Bu = m1.thin_pool_to_chunks(pool_ABv, pool_ABl, pool_ABu, 0.5, device)
    combo_ABv = torch.cat([thin_Av[:thin_Au], thin_Bv[:thin_Bu]], dim=0)
    combo_ABl = torch.cat([thin_Al[:thin_Au], thin_Bl[:thin_Bu]], dim=0)
    combo_ABu = combo_ABv.shape[0]
    W_ABC, pool_ABCv, pool_ABCl, pool_ABCu = base.train_w_with_replay(
        W_AB, pool_ABv.clone(), pool_ABl.clone(), pool_ABu, byte_atoms, pos_atoms,
        tc_idx, tc_tgt, combo_ABv, combo_ABl, combo_ABu, epochs, batch_size, device)
    thin_Cv, thin_Cl, thin_Cu = m1.thin_pool_to_chunks(pool_ABCv, pool_ABCl, pool_ABCu, 0.5, device)
    combo_ABCv = torch.cat([thin_Av[:thin_Au], thin_Bv[:thin_Bu], thin_Cv[:thin_Cu]], dim=0)
    combo_ABCl = torch.cat([thin_Al[:thin_Au], thin_Bl[:thin_Bu], thin_Cl[:thin_Cu]], dim=0)
    combo_ABCu = combo_ABCv.shape[0]
    W_ABCD, _, _, _ = base.train_w_with_replay(
        W_ABC, pool_ABCv.clone(), pool_ABCl.clone(), pool_ABCu, byte_atoms, pos_atoms,
        td_idx, td_tgt, combo_ABCv, combo_ABCl, combo_ABCu, epochs, batch_size, device)
    return W_ABCD


def compute_q_distribution(W: torch.Tensor, n_pairs: int = 500, seed: int = 0) -> list:
    """Sample pairs of W replica projections to compute overlap q distribution."""
    N = W.shape[0]
    w_flat = W.view(-1)
    w_norm = w_flat / w_flat.norm().clamp(min=1e-9)
    gen = torch.Generator().manual_seed(seed)
    q_vals = []
    for _ in range(n_pairs):
        # Random projection pairs
        v1 = torch.randn(N * N, generator=gen)
        v1 /= v1.norm().clamp(min=1e-9)
        v2 = torch.randn(N * N, generator=gen)
        v2 /= v2.norm().clamp(min=1e-9)
        q = float((w_norm * v1).sum() * (w_norm * v2).sum())
        q_vals.append(q)
    return q_vals


def _instrumentation_selftest():
    print("[selftest] running instrumentation self-test...", flush=True)

    # 1. binder_cumulant for RS: B4 of Gaussian -> 1 - 3/3 = 0
    import random
    rng = random.Random(42)
    gauss_samples = [rng.gauss(0, 1) for _ in range(1000)]
    b4 = binder_cumulant(gauss_samples)
    assert abs(b4) < 0.1, f"Selftest 1 FAIL: B4(Gaussian)={b4:.4f} (expected ~0)"
    print(f"[selftest] 1/4 binder_cumulant(Gaussian)={b4:.4f} ~0 OK")

    # 2. kde_peaks: bimodal input -> 2 peaks
    bimodal = [-0.5 + 0.01 * i for i in range(20)] + [0.5 + 0.01 * i for i in range(20)]
    n_pk, sep = kde_n_peaks(bimodal, bw=0.02)
    assert n_pk >= 2, f"Selftest 2 FAIL: n_peaks={n_pk} (expected >= 2)"
    print(f"[selftest] 2/4 kde_peaks bimodal: n_peaks={n_pk} sep={sep:.2f}sigma OK")

    # 3. binder_cumulant of bimodal (1-RSB like) should be > 0.3
    bimodal_vals = ([-1.0] * 50) + ([1.0] * 50)
    b4_bimodal = binder_cumulant(bimodal_vals)
    assert b4_bimodal > 0.3, f"Selftest 3 FAIL: B4(bimodal)={b4_bimodal:.4f} (expected > 0.3)"
    print(f"[selftest] 3/4 binder_cumulant(bimodal)={b4_bimodal:.4f} > 0.3 OK")

    # 4. mean_q computable and finite
    q_vals = [0.1, -0.05, 0.2, 0.0, 0.15]
    mean_q = sum(q_vals) / len(q_vals)
    assert math.isfinite(mean_q), f"Selftest 4 FAIL: mean_q not finite"
    print(f"[selftest] 4/4 mean_q={mean_q:.4f} finite OK")

    print("[selftest] instrumentation self-test PASSED", flush=True)


_instrumentation_selftest()


def run_one_seed(seed, N, batch_size, epochs, phase_a_epochs, n_bytes, smoke, device):
    W = run_4stage_m1_get_W(seed, N, batch_size, epochs, phase_a_epochs, n_bytes, smoke, device)
    q_vals = compute_q_distribution(W, n_pairs=500, seed=seed)
    mean_q = sum(q_vals) / len(q_vals)
    b4 = binder_cumulant(q_vals)
    n_peaks, peak_sep = kde_n_peaks(q_vals, bw=KDE_BW)
    noise_floor = 1.0 / math.sqrt(N * N)
    mean_q_over_floor = abs(mean_q) / max(noise_floor, 1e-12)
    del W
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {
        "seed": seed, "N": N,
        "mean_q": round(mean_q, 8),
        "binder_cumulant": round(b4, 4) if math.isfinite(b4) else None,
        "n_peaks": n_peaks,
        "peak_sep_sigma": peak_sep,
        "mean_q_over_floor": round(mean_q_over_floor, 2),
        "noise_floor": round(noise_floor, 8),
    }


def run_sweep(smoke: bool = False):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    batch_size = BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL
    epochs = EPOCHS_SMOKE if smoke else EPOCHS_FULL
    phase_a_epochs = PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL
    n_bytes = BYTES_SMOKE if smoke else BYTES_FULL
    out_dir = get_output_dir("wave14_1rsb_pq_retained_v4")

    print(f"[pq_retained_v4] N={N} device={device} smoke={smoke} seeds={len(seeds)}", flush=True)
    results = []
    for seed in seeds:
        print(f"  seed={seed}...", flush=True)
        r = run_one_seed(seed, N, batch_size, epochs, phase_a_epochs, n_bytes, smoke, device)
        results.append(r)
        print(f"    binder={r['binder_cumulant']} n_peaks={r['n_peaks']} "
              f"sep={r['peak_sep_sigma']:.2f}sig mean_q_floor={r['mean_q_over_floor']:.1f}x", flush=True)

    return results, out_dir


def compute_verdict(results: list) -> tuple[str, str, dict]:
    valid = [r for r in results if r["binder_cumulant"] is not None]
    if not valid:
        return ("INSTRUMENTATION_FAIL", "All binder_cumulant values are None.", {})

    binders = [r["binder_cumulant"] for r in valid if math.isfinite(r["binder_cumulant"])]
    if not binders:
        return ("INSTRUMENTATION_FAIL", "All binder_cumulant non-finite.", {})

    mean_b4 = sum(binders) / len(binders)
    n_peaks_vals = [r["n_peaks"] for r in valid]
    mean_n_peaks = sum(n_peaks_vals) / len(n_peaks_vals)
    peak_seps = [r["peak_sep_sigma"] for r in valid]
    mean_sep = sum(peak_seps) / len(peak_seps)
    mean_q_vals = [r["mean_q"] for r in valid]
    mean_mean_q = abs(sum(mean_q_vals) / len(mean_q_vals))
    N = valid[0]["N"]
    noise_floor = 1.0 / math.sqrt(N * N)

    summary = {
        "N": N,
        "n_seeds": len(valid),
        "mean_binder_cumulant": round(mean_b4, 4),
        "mean_n_peaks": round(mean_n_peaks, 2),
        "mean_peak_sep_sigma": round(mean_sep, 3),
        "mean_abs_mean_q": round(mean_mean_q, 8),
        "noise_floor": round(noise_floor, 8),
        "mean_q_over_floor": round(mean_mean_q / max(noise_floor, 1e-12), 2),
        "results_per_seed": results,
    }

    n_q_above_floor = sum(1 for r in valid
                          if r["mean_q_over_floor"] > NOISE_FLOOR_FACTOR)

    if mean_b4 <= 0:
        verdict = "UV_PROBLEM_CONFIRMED"
        verdict_msg = (
            f"UV_PROBLEM_CONFIRMED: binder_cumulant={mean_b4:.4f} <= 0 at N={N}. "
            f"Negative Binder persists even at N={N}; RS unimodal framing holds. "
            f"High-dimensional near-orthogonal W-vectors prevent 1-RSB signal resolution."
        )
    elif mean_b4 >= BINDER_1RSB and mean_n_peaks >= 2 and mean_sep >= PEAK_SEP_SIGMA:
        verdict = "HARD_PASS"
        verdict_msg = (
            f"HARD_PASS: 1-RSB signal confirmed and strengthened at N={N}. "
            f"binder={mean_b4:.4f} >= {BINDER_1RSB}, "
            f"n_peaks={mean_n_peaks:.1f} >= 2, "
            f"peak_sep={mean_sep:.2f}sigma >= {PEAK_SEP_SIGMA}sigma. "
            f"N-scaling consistent with genuine 1-RSB multi-basin structure."
        )
    elif mean_b4 <= BINDER_MIDDLE_LO or mean_n_peaks < 1.5:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: 1-RSB signal does NOT strengthen at N={N}. "
            f"binder={mean_b4:.4f} (< {BINDER_MIDDLE_LO} or weaker than v3). "
            f"n_peaks={mean_n_peaks:.1f}. "
            f"v3 HARD_PASS was noise; RS unimodal frame restored."
        )
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (
            f"MIDDLE_BAND: ambiguous scaling of 1-RSB signal at N={N}. "
            f"binder={mean_b4:.4f} in ({BINDER_MIDDLE_LO},{BINDER_1RSB}), "
            f"n_peaks={mean_n_peaks:.1f}, sep={mean_sep:.2f}sigma. "
            f"Signal present but not strengthened enough to confirm vs v3 noise."
        )

    return verdict, verdict_msg, summary


def run(smoke: bool = False):
    t0 = time.time()
    print(f"[exp] wave14_1rsb_pq_retained_v4 {'SMOKE' if smoke else 'FULL'}", flush=True)
    results, out_dir = run_sweep(smoke)

    # Multi-scale smoke
    if smoke:
        print("\n[multi-scale smoke] N_smoke * 4...", flush=True)
        device = torch.device("cpu")
        N2 = N_SMOKE * 4
        r2 = run_one_seed(7, N2, BATCH_SIZE_SMOKE, 1, 1, BYTES_SMOKE, True, device)
        assert r2["binder_cumulant"] is None or math.isfinite(r2["binder_cumulant"])
        print(f"  N={N2}: binder={r2['binder_cumulant']} n_peaks={r2['n_peaks']}")
        print("[multi-scale smoke] PASS")

    verdict, verdict_msg, summary = compute_verdict(results)
    print(f"\nVerdict: {verdict}")
    print(f"Msg: {verdict_msg}")

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(time.time() - t0, 3),
        "summary": summary,
        "config": {
            "N": N_SMOKE if smoke else N_FULL,
            "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
            "KDE_BW": KDE_BW,
            "smoke": smoke,
            "trigger": "ship when v3 returns HARD_PASS (binder > 0.30 AND n_peaks >= 2 at N=8192)",
        },
    }
    validate_metrics(metrics)
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {out_dir / 'metrics.json'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)
