"""LR envelope dose-response — 2x drill on substrate-novel E4 long-tail win.

Motivation
----------
The wave14 online_W_lr_envelope_duration_v1 experiment found E4 (Robbins-Monro
tau=40, long-tail) dominant over E1 (Robbins-Monro tau=10, baseline) at fixed
integral sum lr = 10.0 — a substrate-NOVEL outcome (the Gong et al. 2026
Science article predicted extended-rectangular E3 should win; E4 won instead).
Per [[feedback-2x-means-depth]] this 2x drill characterizes the long-tail
DOSE-RESPONSE curve by sweeping tau in {10, 20, 40, 80, 160} at fixed integral.

If retention rises monotonically with tau through some optimal, then plateaus
or falls, we have a substrate-native dose-response curve we can map. If
retention is flat in tau, the original E4 win was noise.

Scientific question
-------------------
At fixed integral sum_t lr(t) = 10.0, how does retention accuracy depend on
the Robbins-Monro decay parameter tau? Is there a monotone-increasing region,
an optimum, a plateau, or random fluctuation?

Vertices: LR_DOSE_MONOTONIC / LR_DOSE_PEAKED / LR_DOSE_FLAT / LR_DOSE_INCONCLUSIVE.

Pre-reg: preregs/2026-05-24_wave14_lr_envelope_dose_response_v1.md
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse
import json
import math
import os
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# Tunable
TAU_LIST = [10, 20, 40, 80, 160]
TARGET_LR_SUM = 10.0
LR_SUM_TOLERANCE = 0.05
NOISE_LEVELS = [0.20, 0.30, 0.40]


def envelope_rm_tau(n_writes: int, tau: float) -> list[float]:
    """Robbins-Monro lr(t) = c / (1 + t/tau), scaled to integral = TARGET_LR_SUM."""
    raw = [1.0 / (1.0 + t / tau) for t in range(n_writes)]
    s = sum(raw)
    if s <= 0:
        return [0.0] * n_writes
    c = TARGET_LR_SUM / s
    return [c * x for x in raw]


def make_pattern(N: int, gen: torch.Generator, device) -> torch.Tensor:
    b = (torch.rand(N, generator=gen) > 0.5).to(device).float()
    return 2.0 * b - 1.0


def snap_update(W: torch.Tensor, k: torch.Tensor, v: torch.Tensor,
                lr: float, N: int, snap_threshold: float = 1.0) -> torch.Tensor:
    if lr == 0.0:
        return W
    delta = lr * torch.outer(v, k) / N
    delta_norm = float(delta.abs().max().item())
    if delta_norm > snap_threshold:
        delta = delta * (snap_threshold / delta_norm)
    return W + delta


def apply_bit_flip_noise(k: torch.Tensor, p_flip: float, gen: torch.Generator) -> torch.Tensor:
    if p_flip <= 0.0:
        return k
    mask = (torch.rand(k.shape, generator=gen) < p_flip)
    return k * (~mask).float() + (-k) * mask.float()


def check_retrieval_noisy(W: torch.Tensor, k: torch.Tensor, v: torch.Tensor,
                          p_flip: float, noise_gen: torch.Generator) -> bool:
    k_noisy = apply_bit_flip_noise(k, p_flip, noise_gen)
    pred = torch.sign(W @ k_noisy)
    pred[pred == 0] = 1.0
    overlap = float((pred * v).mean().item())
    return overlap > 0.7


def run_one_cell(N: int, n_writes: int, lr_schedule: list[float],
                 p_flip: float, seed: int, device) -> tuple[float, float]:
    gen = torch.Generator(device=device).manual_seed(seed)
    noise_gen = torch.Generator(device=device).manual_seed(seed + 10007)
    W = torch.zeros((N, N), device=device)
    keys = []
    values = []
    accs_over_time = []
    for step in range(n_writes):
        k = make_pattern(N, gen, device)
        v = make_pattern(N, gen, device)
        lr = lr_schedule[step]
        W = snap_update(W, k, v, lr, N)
        keys.append(k)
        values.append(v)
        n_correct = sum(
            1 for j in range(len(keys))
            if check_retrieval_noisy(W, keys[j], values[j], p_flip, noise_gen)
        )
        acc = n_correct / len(keys)
        accs_over_time.append(acc)
    return min(accs_over_time), accs_over_time[-1]


def self_test_envelopes(n_writes: int = 50) -> None:
    print(f"Envelope self-test (n_writes={n_writes}, target_sum={TARGET_LR_SUM}):", flush=True)
    for tau in TAU_LIST:
        lrs = envelope_rm_tau(n_writes, tau)
        s = sum(lrs)
        rel_err = abs(s - TARGET_LR_SUM) / TARGET_LR_SUM
        peak = max(lrs)
        assert rel_err <= LR_SUM_TOLERANCE, f"tau={tau}: rel_err={rel_err:.4f} > tol"
        print(f"  tau={tau}: sum={s:.4f} rel_err={rel_err:.4f} peak={peak:.4f}", flush=True)
    print("envelope self-test passed", flush=True)


def compute_verdict(summary: dict) -> tuple[str, str]:
    """Tau-vs-retention dose-response classification.

    Compute mean retention (over noise levels and seeds) at each tau.
    Find argmax. Classify shape:
      LR_DOSE_MONOTONIC: monotonically rising over tau (Spearman rho > 0.9, no early peak)
      LR_DOSE_PEAKED: clear peak at intermediate tau (argmax not at endpoint
                      AND gap argmax_value - min_value >= 0.05)
      LR_DOSE_FLAT: max - min across tau values < 0.03 (envelope-insensitive)
      LR_DOSE_INCONCLUSIVE: everything else
    """
    if "cell_table" not in summary:
        return ("LR_DOSE_INCONCLUSIVE", "Missing cell_table.")
    tbl = summary["cell_table"]  # {tau: {p: mean_min_acc}}
    if len(tbl) < 3:
        return ("LR_DOSE_INCONCLUSIVE", f"Need >=3 tau values, got {len(tbl)}.")
    taus_sorted = sorted(int(t) for t in tbl.keys())
    mean_per_tau = []
    for t in taus_sorted:
        ps = tbl[t] if t in tbl else tbl[str(t)]
        if not ps:
            return ("LR_DOSE_INCONCLUSIVE", f"Empty cell at tau={t}.")
        mean = sum(ps.values()) / len(ps)
        mean_per_tau.append((t, mean))

    vals = [v for _, v in mean_per_tau]
    spread = max(vals) - min(vals)
    argmax_idx = max(range(len(vals)), key=lambda i: vals[i])
    argmax_tau = mean_per_tau[argmax_idx][0]
    argmin_idx = min(range(len(vals)), key=lambda i: vals[i])

    series_str = ", ".join(f"tau={t}: {v:.3f}" for t, v in mean_per_tau)

    if spread < 0.03:
        return ("LR_DOSE_FLAT",
                f"All tau within 0.03 retention (spread={spread:.4f}); envelope-insensitive. {series_str}")

    # Spearman-like monotone check: count adjacent-pair increases / total pairs
    n_pairs = len(vals) - 1
    increases = sum(1 for i in range(n_pairs) if vals[i + 1] > vals[i] + 1e-6)
    if increases == n_pairs and argmax_idx == len(vals) - 1:
        return ("LR_DOSE_MONOTONIC",
                f"Retention rises monotonically with tau; argmax at tau={argmax_tau} (endpoint). "
                f"spread={spread:.4f}. {series_str}. "
                f"Substrate prefers longer-tail envelopes; no plateau detected at tau<=160.")

    # Peaked: argmax NOT at endpoint, and peak - endpoint >= 0.03
    is_interior = 0 < argmax_idx < len(vals) - 1
    if is_interior and (vals[argmax_idx] - vals[0] >= 0.03) and (vals[argmax_idx] - vals[-1] >= 0.03):
        return ("LR_DOSE_PEAKED",
                f"Retention peaks at interior tau={argmax_tau} (spread={spread:.4f}). "
                f"Substrate has an optimal tail length; longer is not always better. {series_str}")

    return ("LR_DOSE_INCONCLUSIVE",
            f"Pattern ambiguous: spread={spread:.4f}, argmax at tau={argmax_tau} (idx {argmax_idx}/{len(vals)-1}). "
            f"{series_str}")


def self_test_verdict() -> None:
    # FLAT case
    s_flat = {"cell_table": {10: {0.3: 0.90}, 20: {0.3: 0.91}, 40: {0.3: 0.90}, 80: {0.3: 0.90}, 160: {0.3: 0.91}}}
    v, _ = compute_verdict(s_flat)
    assert v == "LR_DOSE_FLAT", f"FLAT got {v}"

    # MONOTONIC case
    s_mono = {"cell_table": {10: {0.3: 0.55}, 20: {0.3: 0.60}, 40: {0.3: 0.68}, 80: {0.3: 0.75}, 160: {0.3: 0.82}}}
    v, _ = compute_verdict(s_mono)
    assert v == "LR_DOSE_MONOTONIC", f"MONOTONIC got {v}"

    # PEAKED case
    s_peak = {"cell_table": {10: {0.3: 0.55}, 20: {0.3: 0.65}, 40: {0.3: 0.80}, 80: {0.3: 0.65}, 160: {0.3: 0.55}}}
    v, _ = compute_verdict(s_peak)
    assert v == "LR_DOSE_PEAKED", f"PEAKED got {v}"

    # INCONCLUSIVE case (non-monotone, no clean peak — argmax at endpoint with non-monotone rise)
    s_inc = {"cell_table": {10: {0.3: 0.70}, 20: {0.3: 0.65}, 40: {0.3: 0.72}, 80: {0.3: 0.60}, 160: {0.3: 0.78}}}
    v, _ = compute_verdict(s_inc)
    assert v == "LR_DOSE_INCONCLUSIVE", f"INCONCLUSIVE got {v}"

    print("verdict self-test passed (4/4)", flush=True)


def run_experiment(smoke: bool):
    t0 = time.monotonic()
    device = torch.device("cpu")
    cfg = {
        "N": 64 if smoke else 4096,
        "n_writes": 10 if smoke else 50,
        "n_seeds": 1 if smoke else 3,
        "noise_levels": [0.30] if smoke else NOISE_LEVELS,
        "tau_list": [10, 40] if smoke else TAU_LIST,
        "snap_threshold": 1.0,
        "target_lr_sum": TARGET_LR_SUM,
        "lr_sum_tolerance": LR_SUM_TOLERANCE,
        "mode": "smoke" if smoke else "full",
    }
    print(f"Config: N={cfg['N']} n_writes={cfg['n_writes']} n_seeds={cfg['n_seeds']}", flush=True)
    print(f"Tau list: {cfg['tau_list']}", flush=True)
    print(f"Noise levels: {cfg['noise_levels']}", flush=True)

    # Build + verify envelopes
    schedules = {}
    envelope_meta = {}
    for tau in cfg["tau_list"]:
        lrs = envelope_rm_tau(cfg["n_writes"], tau)
        s = sum(lrs)
        rel_err = abs(s - TARGET_LR_SUM) / TARGET_LR_SUM
        if rel_err > LR_SUM_TOLERANCE:
            raise RuntimeError(f"tau={tau}: integral {s:.4f} off target (rel_err {rel_err:.4f} > tol)")
        schedules[tau] = lrs
        peak = max(lrs)
        envelope_meta[tau] = {"sum": s, "peak": peak, "rel_err": rel_err}
        print(f"  tau={tau}: sum={s:.4f} peak={peak:.4f}", flush=True)

    # Run grid
    cell_table = {t: {} for t in cfg["tau_list"]}
    raw_cells = []
    for tau in cfg["tau_list"]:
        for p_flip in cfg["noise_levels"]:
            seed_min_accs = []
            for seed_i in range(cfg["n_seeds"]):
                seed = 17 + seed_i * 31
                min_acc, final_acc = run_one_cell(
                    cfg["N"], cfg["n_writes"], schedules[tau], p_flip, seed, device
                )
                seed_min_accs.append(min_acc)
            mean_min = sum(seed_min_accs) / len(seed_min_accs)
            cell_table[tau][p_flip] = mean_min
            raw_cells.append({
                "tau": tau, "p_flip": p_flip,
                "mean_min_acc": mean_min, "seed_min_accs": seed_min_accs,
            })
            print(f"  tau={tau} p={p_flip:.2f}: mean_min={mean_min:.3f}", flush=True)

    summary = {
        "cell_table": cell_table,
        "raw_cells": raw_cells,
        "envelope_meta": envelope_meta,
        "n_seeds": cfg["n_seeds"],
        "N": cfg["N"],
        "n_writes": cfg["n_writes"],
    }
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    print(f"Elapsed: {elapsed:.1f}s", flush=True)
    return summary, verdict, msg, elapsed, cfg


def get_output_dir(name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    if not required.issubset(d.keys()):
        raise ValueError(f"missing keys: {required - d.keys()}")


def write_metrics(out_dir: Path, summary, verdict, msg, elapsed, config) -> None:
    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "config": config,
    }
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    self_test_envelopes(n_writes=10)
    self_test_verdict()
    out_dir = get_output_dir("wave14_lr_envelope_dose_response_v1_smoke")
    s, v, m, e, c = run_experiment(smoke=True)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nSMOKE OK: {v}", flush=True)


def run_main():
    self_test_envelopes(n_writes=50)
    self_test_verdict()
    out_dir = get_output_dir("wave14_lr_envelope_dose_response_v1")
    s, v, m, e, c = run_experiment(smoke=False)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nDONE: {v}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_envelopes(n_writes=50)
        self_test_verdict()
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
