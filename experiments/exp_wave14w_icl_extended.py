"""ICL saturation extension - test the validated Bet 1 envelope at higher ICTX.

wave14d_icl_via_pool_v3_scaling closed at ICL_SATURATION_VALIDATED with slope
+0.1425 through ICTX=16384. v4 extends to ICTX in {4096, 16384, 32768, 65536}
to find the saturation point (if any).

Reuses v3 infrastructure: corpus assembly, train_phase_a, augment_pool_dynamic,
eval_with_pool. New: extended ICTX range + saturation-characterizing verdict.

Pre-reg: preregs/2026-05-21_wave14w_icl_extended.md
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import sys
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402

try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(event_type, **fields):
        pass


_v3_path = REPO / "experiments" / "exp_wave14d_icl_via_pool_v3_scaling.py"
spec = importlib.util.spec_from_file_location("icl_v3", _v3_path)
v3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v3)


N_FULL = 4096
N_SMOKE = 1024
ICTX_FULL = [4096, 16384, 32768, 65536]
ICTX_SMOKE = [256, 1024]
SEEDS_FULL = [17, 23, 31]
SEEDS_SMOKE = [17]
MAX_EPOCHS_FULL = 10
MAX_EPOCHS_SMOKE = 1
BATCH_SIZE_FULL = 64
BATCH_SIZE_SMOKE = 64
TRAIN_A_BYTES_SMOKE = 4000
TEST_B_CAP_FULL = 16_000
TEST_B_CAP_SMOKE = 1500

SLOPE_NO_SAT_THRESHOLD = 0.10
SLOPE_SOFT_SAT_THRESHOLD = 0.05
ENTROPY_FLOOR = 1.0
ALPHA = 1.0


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")
    if not d.get("verdict") or not d.get("verdict_msg"):
        raise ValueError("empty verdict")


def _least_squares_slope(xs, ys) -> float:
    n = len(xs)
    if n < 2:
        return 0.0
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    num = sum((xs[i] - mean_x) * (ys[i] - mean_y) for i in range(n))
    den = sum((xs[i] - mean_x) ** 2 for i in range(n))
    return num / den if abs(den) > 1e-12 else 0.0


def compute_verdict(summary: dict) -> tuple[str, str]:
    ictx_list = summary.get("ictx_list")
    mean_gain = summary.get("mean_gain")
    std_gain = summary.get("std_gain")
    entropy_per_ictx = summary.get("mean_entropy_per_ictx")
    distinct_floor_ok = summary.get("distinct_chunks_floor_ok")

    if not ictx_list or mean_gain is None:
        return ("ICL_EXTENDED_INCONCLUSIVE", "Missing summary data.")

    # Kill: corpus too small
    if distinct_floor_ok is False:
        return ("ICL_CORPUS_TOO_SMALL",
                f"Corpus B exhausted at one or more ICTX values; distinct_chunks "
                f"floor not met. Re-run with larger Corpus B.")

    # Kill: pool collapse at any ICTX
    if entropy_per_ictx:
        for i, ictx in enumerate(ictx_list):
            ent = entropy_per_ictx[i] if i < len(entropy_per_ictx) else None
            if ent is not None and ent < ENTROPY_FLOOR:
                return (f"ICL_POOL_COLLAPSE_AT_{ictx}",
                        f"Pool retrieval entropy {ent:.3f} < {ENTROPY_FLOOR} at "
                        f"ICTX={ictx}. Saturation here is retrieval saturation, "
                        f"not substrate plateau.")

    idx_max = len(ictx_list) - 1
    idx_16k = None
    for i, x in enumerate(ictx_list):
        if x == 16384:
            idx_16k = i
            break
    gain_max = mean_gain[idx_max]
    gain_16k = mean_gain[idx_16k] if idx_16k is not None else mean_gain[0]
    sigma_arr = std_gain or [0] * len(ictx_list)
    sigma_max = sigma_arr[idx_max]
    sigma_16k = sigma_arr[idx_16k] if idx_16k is not None else 0.0

    # 1. DECAY: gain at largest ICTX < gain at 16k by more than 1 sigma
    if gain_max < gain_16k - max(sigma_16k, sigma_max):
        return ("ICL_EXTENDED_DECAY_AT_HIGH_ICTX",
                f"gain at ICTX={ictx_list[idx_max]} = {gain_max:.4f} is lower than "
                f"gain at ICTX=16384 = {gain_16k:.4f} by more than 1 sigma "
                f"({sigma_16k:.4f}). Capability reverses at high ICTX.")

    log_ictx = [math.log2(x) for x in ictx_list]
    slope = _least_squares_slope(log_ictx, mean_gain)
    upper_pts = [(log_ictx[i], mean_gain[i]) for i, x in enumerate(ictx_list) if x >= 16384]
    slope_upper = (_least_squares_slope([p[0] for p in upper_pts],
                                           [p[1] for p in upper_pts])
                    if len(upper_pts) >= 2 else slope)

    # 2. PEAK detection: find argmax of mean_gain. If peak is mid-curve and
    # subsequent points stay within 1*sigma_peak below it (i.e., no recovery),
    # call it saturation.
    peak_idx = max(range(len(mean_gain)), key=lambda i: mean_gain[i])
    peak_gain = mean_gain[peak_idx]
    sigma_peak = sigma_arr[peak_idx]
    if peak_idx < len(mean_gain) - 1:
        after_peak = mean_gain[peak_idx + 1:]
        if all(g <= peak_gain + sigma_peak for g in after_peak):
            return (f"ICL_EXTENDED_SATURATION_AT_{ictx_list[peak_idx]}",
                    f"Gain peaks at ICTX={ictx_list[peak_idx]} (gain={peak_gain:.4f}); "
                    f"subsequent ICTX values stay within 1 sigma of peak. Slope upper="
                    f"{slope_upper:+.4f}, full slope={slope:+.4f}.")

    # 3. SOFT_SATURATION: upper-half slope below threshold (plateau starting,
    # but no actual peak yet within tested range)
    if slope_upper < SLOPE_SOFT_SAT_THRESHOLD:
        return ("ICL_EXTENDED_SOFT_SATURATION",
                f"No hard saturation point yet but slope across ICTX>=16384 = "
                f"{slope_upper:+.4f} < {SLOPE_SOFT_SAT_THRESHOLD}. Plateau starting; "
                f"capability still growing but pace is dropping. Full slope = {slope:+.4f}, "
                f"gain at largest ICTX = {gain_max:.4f}.")

    # 4. NO_SATURATION: slope healthy and gain still growing
    if slope >= SLOPE_NO_SAT_THRESHOLD:
        return ("ICL_EXTENDED_NO_SATURATION",
                f"No saturation through ICTX={ictx_list[idx_max]}. Full slope on "
                f"log2(ICTX) = {slope:+.4f} >= {SLOPE_NO_SAT_THRESHOLD}; upper-half slope = "
                f"{slope_upper:+.4f}. Gain at ICTX={ictx_list[idx_max]} = {gain_max:.4f}.")

    # 5. Slope healthy upper but full slope just below threshold: treat as SOFT
    return ("ICL_EXTENDED_SOFT_SATURATION",
            f"Mixed: full slope={slope:+.4f} (below {SLOPE_NO_SAT_THRESHOLD}); "
            f"upper-half slope={slope_upper:+.4f}; gain_max={gain_max:.4f}. "
            f"Capability nominally continues but pace below NO_SAT threshold.")


def self_test_verdict() -> None:
    cases = [
        # 1. NO_SATURATION
        ({"ictx_list": [4096, 16384, 32768, 65536],
          "mean_gain": [1.0, 1.4, 1.7, 2.0],
          "std_gain": [0.05, 0.05, 0.05, 0.05],
          "mean_entropy_per_ictx": [2.0, 2.5, 2.7, 3.0],
          "distinct_chunks_floor_ok": True},
         "ICL_EXTENDED_NO_SATURATION"),
        # 2. SOFT_SATURATION: upper-half slope below 0.05 but still growing.
        # gain at 32768/65536 grows by 0.03 per log2 step (slope_upper = 0.03 < 0.05).
        # Peak is at last index so no SATURATION_AT label.
        ({"ictx_list": [4096, 16384, 32768, 65536],
          "mean_gain": [1.0, 1.4, 1.43, 1.46],
          "std_gain": [0.01, 0.01, 0.01, 0.01],
          "mean_entropy_per_ictx": [2.0, 2.5, 2.7, 3.0],
          "distinct_chunks_floor_ok": True},
         "ICL_EXTENDED_SOFT_SATURATION"),
        # 3. SATURATION_AT_32768
        ({"ictx_list": [4096, 16384, 32768, 65536],
          "mean_gain": [1.0, 1.4, 1.5, 1.45],
          "std_gain": [0.05, 0.05, 0.05, 0.05],
          "mean_entropy_per_ictx": [2.0, 2.5, 2.7, 3.0],
          "distinct_chunks_floor_ok": True},
         "ICL_EXTENDED_SATURATION_AT_32768"),
        # 4. DECAY_AT_HIGH_ICTX
        ({"ictx_list": [4096, 16384, 32768, 65536],
          "mean_gain": [1.0, 1.4, 1.3, 0.8],
          "std_gain": [0.05, 0.05, 0.05, 0.05],
          "mean_entropy_per_ictx": [2.0, 2.5, 2.7, 3.0],
          "distinct_chunks_floor_ok": True},
         "ICL_EXTENDED_DECAY_AT_HIGH_ICTX"),
        # 5. POOL_COLLAPSE at largest ICTX
        ({"ictx_list": [4096, 16384, 32768, 65536],
          "mean_gain": [1.0, 1.4, 1.5, 1.6],
          "std_gain": [0.05, 0.05, 0.05, 0.05],
          "mean_entropy_per_ictx": [2.0, 2.5, 2.7, 0.5],
          "distinct_chunks_floor_ok": True},
         "ICL_POOL_COLLAPSE_AT_65536"),
        # 6. CORPUS_TOO_SMALL
        ({"ictx_list": [4096, 16384, 32768, 65536],
          "mean_gain": [1.0, 1.4, 1.5, 1.6],
          "std_gain": [0.05, 0.05, 0.05, 0.05],
          "mean_entropy_per_ictx": [2.0, 2.5, 2.7, 3.0],
          "distinct_chunks_floor_ok": False},
         "ICL_CORPUS_TOO_SMALL"),
        # 7. INCONCLUSIVE
        ({}, "ICL_EXTENDED_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"FAIL: actual={actual} != expected={expected}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_full(smoke: bool):
    t_start = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    n_dim = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    ictx_list = ICTX_SMOKE if smoke else ICTX_FULL
    max_epochs = MAX_EPOCHS_SMOKE if smoke else MAX_EPOCHS_FULL
    batch_size = BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL
    max_ictx = max(ictx_list)
    min_corpus_b = max(max_ictx * (v3.K + 1) * 4, 200_000) if not smoke else 8_000

    corpus_a = v3.load_corpus_a()
    corpus_b = v3.load_corpus_b_code(min_corpus_b)
    split_a = int(0.8 * len(corpus_a))
    train_a = corpus_a[:split_a]
    if smoke:
        train_a = train_a[:TRAIN_A_BYTES_SMOKE]
    split_b = int(0.7 * len(corpus_b))
    train_b = corpus_b[:split_b]
    test_b_full = corpus_b[split_b:]
    test_b_cap = TEST_B_CAP_FULL if not smoke else TEST_B_CAP_SMOKE
    test_b = test_b_full[:test_b_cap]

    print(f"[config] n_dim={n_dim}, seeds={seeds}, ictx={ictx_list}, alpha={ALPHA}",
          flush=True)
    print(f"[corpus] A={len(corpus_a)}B (train {len(train_a)}B), "
          f"B={len(corpus_b)}B (train {len(train_b)}B, test {len(test_b)}B)", flush=True)

    per_seed_results = []
    distinct_floor_ok = True

    for seed in seeds:
        gen = torch.Generator().manual_seed(seed)
        byte_atoms = v3.make_bsc_atoms(v3.VOCAB_SIZE, n_dim, gen).to(device)
        pos_atoms = v3.make_bsc_atoms(v3.K, n_dim, gen).to(device)

        print(f"\n[seed={seed}] Phase A training...", flush=True)
        W_A, pool_A, labels_A, used_A = v3.train_phase_a(
            byte_atoms, pos_atoms, train_a, n_dim, max_epochs, batch_size)
        print(f"[seed={seed}] Phase A done. pool_used={used_A}", flush=True)

        off_bpc, _ = v3.eval_with_pool(W_A, byte_atoms, pos_atoms, test_b,
                                          pool_A, labels_A, used_A, 0.0,
                                          batch_size, n_dim)
        pool_A_bpc, pool_A_ent = v3.eval_with_pool(W_A, byte_atoms, pos_atoms, test_b,
                                                     pool_A, labels_A, used_A, ALPHA,
                                                     batch_size, n_dim, return_entropy=True)
        print(f"[seed={seed}] off={off_bpc:.4f}  pool_A(alpha=1)={pool_A_bpc:.4f}  "
              f"entropy={pool_A_ent:.3f}", flush=True)

        per_ictx = {}
        for ictx in ictx_list:
            irr_idx, irr_tgts, irr_n = v3.chunk_bytes_to_K_positions(
                train_a, ictx, seed=seed * 100 + 1)
            rel_idx, rel_tgts, rel_n = v3.chunk_bytes_to_K_positions(
                train_b, ictx, seed=seed * 100 + 2)
            if rel_n < ictx:
                distinct_floor_ok = False
            irr_ctxs = v3.build_ctx(byte_atoms, pos_atoms, irr_idx)
            rel_ctxs = v3.build_ctx(byte_atoms, pos_atoms, rel_idx)
            aug_v_irr, aug_l_irr, used_irr = v3.augment_pool_dynamic(
                pool_A, labels_A, used_A, irr_ctxs, irr_tgts)
            aug_v_rel, aug_l_rel, used_rel = v3.augment_pool_dynamic(
                pool_A, labels_A, used_A, rel_ctxs, rel_tgts)
            irr_bpc, _ = v3.eval_with_pool(W_A, byte_atoms, pos_atoms, test_b,
                                              aug_v_irr, aug_l_irr, used_irr, ALPHA,
                                              batch_size, n_dim)
            rel_bpc, rel_ent = v3.eval_with_pool(W_A, byte_atoms, pos_atoms, test_b,
                                                    aug_v_rel, aug_l_rel, used_rel, ALPHA,
                                                    batch_size, n_dim, return_entropy=True)
            gain = irr_bpc - rel_bpc
            per_ictx[ictx] = {"irr_bpc": irr_bpc, "rel_bpc": rel_bpc, "gain": gain,
                                "entropy": rel_ent, "distinct_irr": irr_n,
                                "distinct_rel": rel_n}
            print(f"[seed={seed}] ICTX={ictx:6d}  irr={irr_bpc:.4f}  rel={rel_bpc:.4f}  "
                  f"gain={gain:+.4f}  ent={rel_ent:.3f}  distinct_rel={rel_n}",
                  flush=True)

        per_seed_results.append({
            "seed": seed, "off_bpc": off_bpc, "pool_A_bpc": pool_A_bpc,
            "pool_A_entropy": pool_A_ent, "per_ictx": per_ictx,
        })

    mean_gain = []
    std_gain = []
    mean_entropy_per_ictx = []
    for ictx in ictx_list:
        gains = [r["per_ictx"][ictx]["gain"] for r in per_seed_results]
        ents = [r["per_ictx"][ictx]["entropy"] for r in per_seed_results
                 if r["per_ictx"][ictx]["entropy"] is not None]
        n = len(gains)
        mg = sum(gains) / n
        var = sum((g - mg) ** 2 for g in gains) / max(n - 1, 1) if n > 1 else 0.0
        mean_gain.append(mg)
        std_gain.append(math.sqrt(var))
        mean_entropy_per_ictx.append(sum(ents) / len(ents) if ents else None)

    elapsed = time.monotonic() - t_start

    summary = {
        "ictx_list": ictx_list,
        "mean_gain": mean_gain,
        "std_gain": std_gain,
        "mean_entropy_per_ictx": mean_entropy_per_ictx,
        "distinct_chunks_floor_ok": distinct_floor_ok,
        "n_seeds": len(seeds),
        "alpha": ALPHA,
        "n_dim": n_dim,
    }
    verdict, msg = compute_verdict(summary)

    print("\n========= AGGREGATE =========", flush=True)
    for i, ictx in enumerate(ictx_list):
        ent_str = (f" entropy={mean_entropy_per_ictx[i]:.3f}"
                    if mean_entropy_per_ictx[i] is not None else "")
        print(f"  ICTX={ictx:6d}  mean_gain={mean_gain[i]:+.4f} +/- {std_gain[i]:.4f}"
              + ent_str, flush=True)
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)

    return summary, verdict, msg, elapsed, per_seed_results


def write_metrics(out_dir, summary, verdict, msg, elapsed, per_seed_results, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
                "summary": summary, "config": config, "per_seed": per_seed_results}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14w_icl_extended_smoke")
    log_event("experiment_started", name="wave14w_icl_extended", mode="smoke")
    summary, verdict, msg, elapsed, per_seed = run_full(smoke=True)

    # Oracle: bpc values plausible at smoke max ICTX
    rel_bpc_max = per_seed[0]["per_ictx"][ICTX_SMOKE[-1]]["rel_bpc"]
    oracle.assert_in_range("rel_bpc_smoke", rel_bpc_max, (0.5, 8.0))
    distinct_rel = per_seed[0]["per_ictx"][ICTX_SMOKE[-1]]["distinct_rel"]
    if distinct_rel < ICTX_SMOKE[-1]:
        raise AssertionError(
            f"SANITY FAIL [distinct_chunks_smoke]: requested {ICTX_SMOKE[-1]}, got "
            f"{distinct_rel}. Smoke corpus too small.")

    write_metrics(out_dir, summary, verdict, msg, elapsed, per_seed, {
        "mode": "smoke", "n_dim": N_SMOKE, "ictx": ICTX_SMOKE, "seeds": SEEDS_SMOKE,
        "max_epochs": MAX_EPOCHS_SMOKE, "alpha": ALPHA,
    })
    log_event("experiment_outcome", name="wave14w_icl_extended",
              verdict=verdict, verdict_msg=msg, elapsed_s=elapsed, mode="smoke")
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14w_icl_extended")
    log_event("experiment_started", name="wave14w_icl_extended", mode="full")
    summary, verdict, msg, elapsed, per_seed = run_full(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, per_seed, {
        "mode": "full", "n_dim": N_FULL, "ictx": ICTX_FULL, "seeds": SEEDS_FULL,
        "max_epochs": MAX_EPOCHS_FULL, "alpha": ALPHA,
    })
    log_event("experiment_outcome", name="wave14w_icl_extended",
              verdict=verdict, verdict_msg=msg, elapsed_s=elapsed, mode="full")
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict()
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
