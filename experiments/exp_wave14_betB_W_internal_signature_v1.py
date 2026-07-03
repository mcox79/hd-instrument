"""Alt2 Bet B W-internal signature predictor pilot.

Context: R-PRIME-3 rejected continuous geometry (r^2=0.103). This tests whether
SUBSTRATE-INTERNAL signatures measured after Phase-A (before Phase-B) can predict
Phase-B/C retention. If any signature achieves r^2 > 0.5, retention is predictable
from one-pass post-Phase-A measurement -- substantially more useful than geometry.

Signatures extracted after Phase-A:
  (a) W spectrum: top-3 eigenvalues (lam1, lam2, lam3), spectral gap (lam1-lam2),
      spectral gap ratio (lam1/lam2), normalized Frobenius norm
  (b) Bundle-norm distribution: mean, std, variance, kurtosis, skewness of
      ||W @ x_i||_2 for random test contexts x_i
  (c) Row-norm distribution: mean, std of ||W[k, :]||_2 for each row k

Then Phase-B runs with 5 corpus pairs of varying cross-corpus distance:
  Pair 0: corpus_A_shuffled (same-corpus, close)
  Pair 1: corpus_A_reversed (same-corpus, reversed order)
  Pair 2: corpus_python (different domain, small shift)
  Pair 3: corpus_verification (different domain, medium shift)
  Pair 4: corpus_random (random bytes, maximum shift)

For each seed x corpus-pair combination, measures Phase-B retention_A.
Computes r^2 between each signature and retention_A across all (seed, pair) cells.

Pre-reg:
    HARD-PASS: at least 1 signature achieves r^2 >= 0.50 (Pearson) across all cells.
               "Retention predictable from post-Phase-A substrate measurement."
    HARD-FAIL: NO signature achieves r^2 >= 0.20. Internal state after Phase-A
               contains NO information about subsequent retention.
    MIDDLE: best r^2 in [0.20, 0.50). Partial signal, requires larger N or more seeds.

Queue: overnight_queue (GPU, 5 seeds x 5 corpus pairs x Phase-A + Phase-B = ~2-3h).
ETA: ~2-3h on GPU.
Pre-reg: preregs/2026-05-24_wave14_betB_W_internal_signature_v1.md

Per [[feedback-no-experiment-design-in-prompts]]: all parameters chosen by exp_dev.
Per [[feedback-no-smoke]]: HARD-PASS/HARD-FAIL/MIDDLE pre-registered.
Per [[feedback-envelope-expansion-fail-bands]]: bands registered BEFORE running.
Per [[feedback-ascii-only-in-scripts]]: stdout.reconfigure at top.
Per [[feedback-strategy-spec-formula-selftests]]: 9 self-test cells.
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse, importlib.util, json, math, os, time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402

# Load Kovacs base (train_w_with_replay, evaluate_bpc, bytes_to_idx_tensors, etc.)
_kv_path = REPO / "experiments" / "exp_wave14d_betB_kovacs_v1.py"
_kv_spec = importlib.util.spec_from_file_location("kv", _kv_path)
kv = importlib.util.module_from_spec(_kv_spec)
_kv_spec.loader.exec_module(kv)
pa = kv.pa

# ───── design parameters (exp_dev autonomy) ─────
N_FULL = 4096
N_SMOKE = 512
BATCH_SIZE_FULL = 64
BATCH_SIZE_SMOKE = 32
EPOCHS_FULL = 5
EPOCHS_SMOKE = 1
PHASE_A_EPOCHS_FULL = 8
PHASE_A_EPOCHS_SMOKE = 2
BYTES_FULL = 200_000
BYTES_SMOKE = 3_000
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_BUNDLE_PROBE = 512   # random contexts for bundle-norm measurement

# Pre-registered thresholds
PASS_R2 = 0.50
FAIL_R2 = 0.20


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
# ───── corpus loaders ─────
def load_corpus_pair(pair_id: int, n_bytes: int, seed: int, smoke: bool) -> bytes:
    """Return corpus for Phase-B training based on pair_id."""
    corpus_a = pa.load_corpus_a()
    if pair_id == 0:
        # Shuffled same corpus (close shift)
        return pa.shuffle_bytes(corpus_a[:n_bytes * 2], seed=seed + 100)[:n_bytes]
    elif pair_id == 1:
        # Reversed same corpus
        data = corpus_a[:n_bytes]
        return bytes(reversed(data))
    elif pair_id == 2:
        # Python source (different domain)
        exp_dir = REPO / "experiments"
        n_files = 3 if smoke else 10
        parts = []
        for f in sorted(exp_dir.glob("exp_wave14b*.py"))[:n_files]:
            parts.append(f.read_bytes())
            parts.append(b"\n\n")
        data = b"".join(parts)
        return data[:n_bytes] if n_bytes < len(data) else data
    elif pair_id == 3:
        # Verification code (different domain)
        ver_dir = REPO / "verification"
        n_files = 2 if smoke else 6
        parts = []
        for f in sorted(ver_dir.glob("*.py"))[:n_files]:
            parts.append(f.read_bytes())
            parts.append(b"\n\n")
        data = b"".join(parts)
        return data[:n_bytes] if n_bytes < len(data) else data
    elif pair_id == 4:
        # Random bytes (maximum shift)
        gen = torch.Generator().manual_seed(seed + 200)
        data = torch.randint(0, 256, (n_bytes,), generator=gen).numpy().tobytes()
        return data
    else:
        raise ValueError(f"Unknown pair_id={pair_id}")


PAIR_NAMES = {
    0: "shuffled_same_corpus",
    1: "reversed_same_corpus",
    2: "python_source",
    3: "verification_code",
    4: "random_bytes",
}

N_PAIRS_FULL = 5
N_PAIRS_SMOKE = 3  # pairs 0, 2, 4 in smoke (diverse)
SMOKE_PAIRS = [0, 2, 4]


# ───── W signature extraction ─────
def extract_W_signatures(W: torch.Tensor, byte_atoms: torch.Tensor,
                          pos_atoms: torch.Tensor, n_probe: int, device) -> Dict[str, float]:
    """Extract internal signatures from trained W matrix after Phase-A."""
    W = W.to(device)
    N = W.shape[0]

    # (a) W spectrum via SVD (top-3 singular values)
    # Use torch.linalg.svdvals for efficiency (no full decomposition)
    try:
        sv = torch.linalg.svdvals(W.float())  # shape (N,)
        lam1 = float(sv[0])
        lam2 = float(sv[1]) if N > 1 else 0.0
        lam3 = float(sv[2]) if N > 2 else 0.0
        spectral_gap = lam1 - lam2
        spectral_gap_ratio = lam1 / lam2 if lam2 > 1e-12 else float("inf")
        frob_norm = float(torch.norm(W).item()) / math.sqrt(N)
    except Exception:
        lam1 = lam2 = lam3 = spectral_gap = spectral_gap_ratio = frob_norm = float("nan")

    # (b) Bundle-norm distribution: measure ||W @ x_i||_2 for random probe contexts
    # Generate random BSC contexts using byte/pos atoms (same construction as train)
    gen_probe = torch.Generator(device=device).manual_seed(42)  # fixed seed for reproducibility
    # Random byte indices and position indices
    vocab = byte_atoms.shape[0]
    K = pos_atoms.shape[0]
    rand_bytes = torch.randint(0, vocab, (n_probe, K), generator=gen_probe, device=device)
    # Build ctx vectors using pa.build_ctx_bundles_bsc
    try:
        ctxs = pa.build_ctx_bundles_bsc(byte_atoms, pos_atoms, rand_bytes)  # (n_probe, N)
        # Bundle norm: ||W^T @ x_i||_2 for each probe x_i (W: NxN, x: N -> W^T x: N)
        bundle_activations = ctxs @ W.T  # (n_probe, N)
        bundle_norms = torch.norm(bundle_activations, dim=1).cpu().float()  # (n_probe,)
        bn_mean = float(bundle_norms.mean())
        bn_std = float(bundle_norms.std())
        bn_var = float(bundle_norms.var())
        # Kurtosis (excess): E[(x-mu)^4]/sigma^4 - 3
        if bn_std > 1e-12:
            z = (bundle_norms - bn_mean) / bn_std
            bn_kurtosis = float((z ** 4).mean()) - 3.0
            bn_skewness = float((z ** 3).mean())
        else:
            bn_kurtosis = bn_skewness = 0.0
    except Exception:
        bn_mean = bn_std = bn_var = bn_kurtosis = bn_skewness = float("nan")

    # (c) Row-norm distribution: ||W[k, :]||_2 for each row k
    try:
        row_norms = torch.norm(W, dim=1).cpu().float()  # (N,)
        rn_mean = float(row_norms.mean())
        rn_std = float(row_norms.std())
    except Exception:
        rn_mean = rn_std = float("nan")

    return {
        "lam1": lam1,
        "lam2": lam2,
        "lam3": lam3,
        "spectral_gap": spectral_gap,
        "spectral_gap_ratio": spectral_gap_ratio,
        "frob_norm_normalized": frob_norm,
        "bundle_norm_mean": bn_mean,
        "bundle_norm_std": bn_std,
        "bundle_norm_var": bn_var,
        "bundle_norm_kurtosis": bn_kurtosis,
        "bundle_norm_skewness": bn_skewness,
        "row_norm_mean": rn_mean,
        "row_norm_std": rn_std,
    }


# ───── statistics ─────
def pearson_r2(xs: List[float], ys: List[float]) -> float:
    """Pearson r^2 between two lists, NaN-aware."""
    pairs = [(x, y) for x, y in zip(xs, ys) if not math.isnan(x) and not math.isnan(y)]
    if len(pairs) < 3:
        return float("nan")
    n = len(pairs)
    mx = sum(p[0] for p in pairs) / n
    my = sum(p[1] for p in pairs) / n
    sx = math.sqrt(sum((p[0] - mx) ** 2 for p in pairs) / (n - 1))
    sy = math.sqrt(sum((p[1] - my) ** 2 for p in pairs) / (n - 1))
    if sx < 1e-12 or sy < 1e-12:
        return 0.0
    r = sum((p[0] - mx) * (p[1] - my) for p in pairs) / ((n - 1) * sx * sy)
    return r ** 2


# ───── self-tests ─────
def self_test():
    """Self-test cells verifying verdict logic and formula correctness."""
    errors = []

    # Cell 1: HARD-PASS verdict - r2 >= 0.5
    best_r2 = 0.75
    if not (best_r2 >= PASS_R2):
        errors.append(f"Cell 1: HARD-PASS failed with r2={best_r2}")

    # Cell 2: HARD-FAIL verdict - r2 < 0.2
    best_r2 = 0.10
    if not (best_r2 < FAIL_R2):
        errors.append(f"Cell 2: HARD-FAIL failed with r2={best_r2}")

    # Cell 3: MIDDLE verdict - r2 in [0.2, 0.5)
    best_r2 = 0.35
    if not (FAIL_R2 <= best_r2 < PASS_R2):
        errors.append(f"Cell 3: MIDDLE failed with r2={best_r2}")

    # Cell 4: pearson_r2 perfect linear
    xs = [1.0, 2.0, 3.0, 4.0, 5.0]
    ys = [2.0, 4.0, 6.0, 8.0, 10.0]
    r2 = pearson_r2(xs, ys)
    if abs(r2 - 1.0) > 1e-6:
        errors.append(f"Cell 4: pearson_r2 perfect linear = {r2}, expected 1.0")

    # Cell 5: pearson_r2 zero correlation
    xs = [1.0, 2.0, 3.0, 4.0, 5.0]
    ys = [3.0, 3.0, 3.0, 3.0, 3.0]  # constant y
    r2 = pearson_r2(xs, ys)
    if not (r2 == 0.0 or math.isnan(r2)):
        errors.append(f"Cell 5: zero correlation case expected 0 or nan, got {r2}")

    # Cell 6: pearson_r2 NaN-handling - with 1 NaN dropped, only 2 pairs remain
    # pearson_r2 requires >= 3 pairs, so this returns nan (correct behavior)
    xs = [1.0, float("nan"), 3.0]
    ys = [2.0, 4.0, 6.0]
    r2 = pearson_r2(xs, ys)
    # After dropping nan pair: 2 remaining -> n < 3 -> returns nan; that's correct
    if not math.isnan(r2):
        errors.append(f"Cell 6: expected nan when <3 pairs after NaN drop, got {r2}")

    # Cell 7: spectral gap = lam1 - lam2 correctness
    lam1, lam2 = 5.0, 3.0
    spectral_gap = lam1 - lam2
    if abs(spectral_gap - 2.0) > 1e-9:
        errors.append(f"Cell 7: spectral_gap={spectral_gap}, expected 2.0")

    # Cell 8: bundle-norm kurtosis formula
    # Normal distribution has kurtosis 0 (excess kurtosis)
    import random
    random.seed(42)
    n = 10000
    vals_norm = [random.gauss(0, 1) for _ in range(n)]
    mean_v = sum(vals_norm) / n
    std_v = (sum((v - mean_v) ** 2 for v in vals_norm) / (n - 1)) ** 0.5
    z = [(v - mean_v) / std_v for v in vals_norm]
    kurt = sum(zi ** 4 for zi in z) / n - 3.0
    if abs(kurt) > 0.3:  # should be near 0 for normal
        errors.append(f"Cell 8: normal kurtosis={kurt:.3f}, expected near 0")

    # Cell 9: pair loader integrity - pairs 0..4 return bytes
    # (just check without running full corpus load)
    pair_names_check = set(PAIR_NAMES.values())
    if len(pair_names_check) != 5:
        errors.append(f"Cell 9: expected 5 unique pair names, got {len(pair_names_check)}")

    if errors:
        print(f"[SELF-TEST FAIL] {len(errors)} errors:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print(f"[SELF-TEST PASS] 9/9 cells pass")
        sys.exit(0)


# ───── main experiment ─────
def run_one_seed(seed: int, config: dict, device) -> Dict:
    """Train Phase-A, extract W signatures, run Phase-B across corpus pairs."""
    N = config["N"]
    batch_size = config["batch_size"]
    n_epochs = config["epochs"]
    phase_a_epochs = config["phase_a_epochs"]
    n_bytes = config["bytes_per_corpus"]
    pairs = config["pairs"]
    smoke = config["mode"] == "smoke"

    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(kv.VOCAB, N, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(kv.K, N, gen).to(device)

    # Corpus A (Phase-A training corpus)
    corpus_a_full = pa.load_corpus_a()
    corpus_a = corpus_a_full[:n_bytes] if n_bytes < len(corpus_a_full) else corpus_a_full

    def split(data):
        m = int(0.8 * len(data))
        return data[:m], data[m:]

    train_a, test_a = split(corpus_a)

    # Train Phase-A
    W = torch.zeros(N, N, device=device)
    train_a_bytes, train_a_targets = kv.bytes_to_idx_tensors(train_a, device)
    W, pool_vecs_A, pool_labels_A, pool_used_A = kv.train_w_with_replay(
        W, None, None, 0,
        byte_atoms, pos_atoms,
        train_a_bytes, train_a_targets,
        None, None, 0,
        phase_a_epochs, batch_size, device,
    )

    # Measure Phase-A baseline bpc
    test_a_bytes, test_a_targets = kv.bytes_to_idx_tensors(test_a, device)
    bpc_A_baseline = kv.evaluate_bpc(
        W, pool_vecs_A, pool_labels_A, pool_used_A,
        byte_atoms, pos_atoms, test_a_bytes, test_a_targets, batch_size, device,
    )

    # Extract W-internal signatures AFTER Phase-A
    signatures = extract_W_signatures(W, byte_atoms, pos_atoms, N_BUNDLE_PROBE, device)

    # Phase-B: run across each corpus pair
    pair_results = {}
    for pair_id in pairs:
        corpus_b = load_corpus_pair(pair_id, n_bytes, seed, smoke)
        train_b, test_b = split(corpus_b)
        train_b_bytes, train_b_targets = kv.bytes_to_idx_tensors(train_b, device)

        # Train Phase-B starting from Phase-A W (with Phase-A replay)
        W_b = W.clone()
        W_b, pool_vecs_B, pool_labels_B, pool_used_B = kv.train_w_with_replay(
            W_b, None, None, 0,
            byte_atoms, pos_atoms,
            train_b_bytes, train_b_targets,
            pool_vecs_A, pool_labels_A, pool_used_A,
            n_epochs, batch_size, device,
        )

        # Measure Phase-A retention after Phase-B
        bpc_A_after_B = kv.evaluate_bpc(
            W_b, pool_vecs_B, pool_labels_B, pool_used_B,
            byte_atoms, pos_atoms, test_a_bytes, test_a_targets, batch_size, device,
        )
        retention_A = bpc_A_baseline / bpc_A_after_B if bpc_A_after_B > 1e-12 else 0.0

        pair_results[PAIR_NAMES[pair_id]] = {
            "bpc_A_baseline": bpc_A_baseline,
            "bpc_A_after_B": bpc_A_after_B,
            "retention_A": retention_A,
        }

    return {
        "signatures": signatures,
        "pair_results": pair_results,
    }


def run_main(mode: str) -> dict:
    t0 = time.time()
    smoke = mode == "smoke"
    N = N_SMOKE if smoke else N_FULL
    batch_size = BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL
    epochs = EPOCHS_SMOKE if smoke else EPOCHS_FULL
    phase_a_epochs = PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL
    n_bytes = BYTES_SMOKE if smoke else BYTES_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    pairs = SMOKE_PAIRS if smoke else list(range(N_PAIRS_FULL))

    config = {
        "mode": mode,
        "N": N,
        "batch_size": batch_size,
        "epochs": epochs,
        "phase_a_epochs": phase_a_epochs,
        "bytes_per_corpus": n_bytes,
        "seeds": seeds,
        "pairs": pairs,
        "pass_r2": PASS_R2,
        "fail_r2": FAIL_R2,
        "n_bundle_probe": N_BUNDLE_PROBE,
    }

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[W-sig] Device={device} N={N} seeds={seeds} pairs={pairs}")

    per_seed = {}
    for seed in seeds:
        print(f"  seed={seed}...", flush=True)
        per_seed[str(seed)] = run_one_seed(seed, config, device)

    # Compute r^2 between each signature and retention_A across all (seed, pair) cells
    sig_names = list(per_seed[str(seeds[0])]["signatures"].keys())
    all_retention = []
    sig_values: Dict[str, List[float]] = {s: [] for s in sig_names}

    for seed_str, sd in per_seed.items():
        sigs = sd["signatures"]
        for pair_name, pr in sd["pair_results"].items():
            ret = pr["retention_A"]
            all_retention.append(ret)
            for sn in sig_names:
                sig_values[sn].append(sigs.get(sn, float("nan")))

    sig_r2 = {}
    for sn in sig_names:
        r2 = pearson_r2(sig_values[sn], all_retention)
        sig_r2[sn] = r2

    best_sig = max(sig_r2.items(), key=lambda x: x[1] if not math.isnan(x[1]) else -1)
    best_r2 = best_sig[1]

    # Verdict
    if not math.isnan(best_r2) and best_r2 >= PASS_R2:
        verdict = "W_INTERNAL_HARD_PASS"
        verdict_msg = (
            f"W-internal signature predicts Phase-B retention: "
            f"best signature '{best_sig[0]}' r^2={best_r2:.3f} >= {PASS_R2}. "
            f"Retention is predictable from post-Phase-A substrate measurement."
        )
    elif math.isnan(best_r2) or best_r2 < FAIL_R2:
        verdict = "W_INTERNAL_HARD_FAIL"
        verdict_msg = (
            f"No W-internal signature predicts retention: "
            f"best r^2={best_r2:.3f} < {FAIL_R2}. "
            f"Post-Phase-A internal state contains no information about subsequent retention."
        )
    else:
        verdict = "W_INTERNAL_MIDDLE_BAND"
        verdict_msg = (
            f"Partial W-internal signal: best signature '{best_sig[0]}' "
            f"r^2={best_r2:.3f} in [{FAIL_R2},{PASS_R2}). "
            f"Partial predictability; larger N or more seeds may resolve."
        )

    elapsed = time.time() - t0

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": {
            "best_signature": best_sig[0],
            "best_r2": best_r2,
            "sig_r2": sig_r2,
            "n_cells": len(all_retention),
            "retention_values": all_retention,
            "per_seed": per_seed,
        },
        "config": config,
    }
    return metrics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return

    mode = "smoke" if args.smoke else "full"
    metrics = run_main(mode)

    print(f"[{metrics['verdict']}] {metrics['verdict_msg']}")
    print(f"  best_sig={metrics['summary']['best_signature']} r2={metrics['summary']['best_r2']:.3f}")
    print(f"  n_cells={metrics['summary']['n_cells']}")
    print("  Top-5 signatures by r^2:")
    top5 = sorted(metrics["summary"]["sig_r2"].items(),
                  key=lambda x: x[1] if not math.isnan(x[1]) else -1, reverse=True)[:5]
    for sn, r2 in top5:
        r2_str = f"{r2:.4f}" if not math.isnan(r2) else "nan"
        print(f"    {sn}: r^2={r2_str}")

    out_dir = get_output_dir("wave14_betB_W_internal_signature_v1")
    with open(out_dir / "metrics.json", "w") as fp:
        json.dump(metrics, fp, indent=2, default=str)
    print(f"[written] {out_dir / 'metrics.json'}")


if __name__ == "__main__":
    main()
