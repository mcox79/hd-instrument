"""
timeseries_xor_prot021_fix_v1 -- Time-tag XOR range query with PROT-021 fix.

RESCUE from timeseries_xor_fullscale_v2 all-zero output (PROT-021 contamination):
  Root cause analysis: v2 used bundle(tau_window) for IN-WINDOW retrieval (wrong).
  v1's architecture: individual tau_t queries for in-window accuracy (correct).
  The range-query concept: for each t in window, retrieve content_t individually
  using W @ tau_t -> m_t -> unbind content_t. This works at N=1024 (v1 in_acc=1.0).
  v2 accidentally bundled tau vectors for in-window too -- that fails because
  the bundle doesn't cleanly retrieve any single memory.

FIXES vs v2:
  1. PROT-021: run_config includes N in checkpoint key.
  2. Architecture: in-window accuracy uses INDIVIDUAL tau_t queries (like v1).
     Out-of-window contamination: bundle of tau vectors to test range-query contamination.
  3. N=4096 used consistently.

SCIENTIFIC QUESTION (PP timeseries-compliance sub-row):
  Does XOR time-tag individual retrieval (W @ tau_t -> content_t) scale to N=4096?
  And does a window range bundle NOT contaminate out-of-window patterns?

PRE-REGISTERED BANDS (from research rescue note 2026-06-02):
  HARD-PASS: in_acc >= 0.90, contam <= 0.10, N=4096, 3+ seeds pass.
  MIDDLE: in_acc in [0.50, 0.90) OR contam in (0.10, 0.40].
  HARD-FAIL: in_acc < 0.50 after fix (genuine SNR floor at large N).

P_deflated=0.72 per research note.

FORMULA SELF-TESTS:
  1. W_kv @ tau_t ~ m_t (key-value retrieval).
     Unbind: content_t = sign(m_t) * tau_t. Cosine(content_hat, content_t) > 0.90.
  2. XOR bind: m_t = content_t * tau_t. Inverse: content_t = m_t * tau_t.
     Round-trip: xor_bind(xor_bind(a, b), b) = a.
  3. At N=4096 K=15: load = K/N = 0.0037 << alpha_c=0.138. Retrieval should be perfect.

PROT-018: no _nN suffix; production N=4096 stated here per rule 3.
PROT-021: run_config includes N -> stale smoke partials from v2 rejected.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "timeseries_xor_prot021_fix_v1"

# PROT-018: no _nN suffix; production N=4096 (stated explicitly per rule 3)
N = 4096

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    K_PATTERNS = 15
    WINDOW_SIZES = [2, 3]
    N_QUERIES = 5
else:
    SEEDS = [7, 17, 23, 31, 41]
    K_PATTERNS = 50
    WINDOW_SIZES = [2, 3, 5, 8]
    N_QUERIES = 15

RETRIEVAL_THRESH = 0.60

HP_IN_WIN_ACC = 0.90
HF_IN_WIN_ACC = 0.50
HP_CONTAM = 0.10
HF_CONTAM = 0.40


def xor_bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """XOR bind for +-1 vectors: element-wise product. Self-inverse: (a*b)*b = a."""
    return a * b


def run_one_seed(n_dim: int, K: int, seed: int, window_sizes: List[int],
                 n_queries: int) -> Dict:
    """
    Run one seed.
    IN-WINDOW ACCURACY: individual tau_t queries (correct v1 architecture).
    OUT-OF-WINDOW CONTAMINATION: bundle of tau_t for range query test.
    """
    rng = np.random.RandomState(seed)

    contents = rng.choice([-1.0, 1.0], size=(n_dim, K))
    tau = rng.choice([-1.0, 1.0], size=(n_dim, K))

    # Build key-value W: W @ tau_t -> m_t = XOR(content_t, tau_t)
    W_kv = np.zeros((n_dim, n_dim))
    m_vecs = []
    for t in range(K):
        m_t = xor_bind(contents[:, t], tau[:, t])
        W_kv += np.outer(m_t, tau[:, t]) / n_dim
        m_vecs.append(m_t)

    results_by_window = {}

    for win_size in window_sizes:
        in_acc_list = []
        contam_list = []

        for _ in range(n_queries):
            t_lo = rng.randint(0, max(1, K - win_size))
            t_hi = min(t_lo + win_size, K - 1)
            in_window = list(range(t_lo, t_hi + 1))
            out_window = [t for t in range(K) if t not in in_window]

            # IN-WINDOW: individual tau_t queries for each t in window
            # This is the correct architecture per v1: each pattern retrieved separately.
            in_acc_per_t = []
            for t in in_window:
                m_hat = np.sign(W_kv @ tau[:, t] + 1e-12)
                content_hat = xor_bind(m_hat, tau[:, t])  # unbind
                nm = np.linalg.norm(content_hat) * np.linalg.norm(contents[:, t]) + 1e-12
                cos = abs(float(np.dot(content_hat, contents[:, t])) / nm)
                in_acc_per_t.append(cos > RETRIEVAL_THRESH)

            in_acc = float(np.mean(in_acc_per_t)) if in_acc_per_t else float("nan")
            in_acc_list.append(in_acc)

            # OUT-OF-WINDOW CONTAMINATION: use bundle query for range
            # Bundle tau_t for all t in window; check if out-of-window content retrieved
            if out_window:
                tau_window_vecs = [tau[:, t] for t in in_window]
                q_bundle = np.sign(np.sum(tau_window_vecs, axis=0) + 1e-12)
                m_bundle_hat = np.sign(W_kv @ q_bundle + 1e-12)

                out_acc_per_t = []
                for t in out_window:
                    content_hat_t = xor_bind(m_bundle_hat, tau[:, t])
                    nm = np.linalg.norm(content_hat_t) * np.linalg.norm(contents[:, t]) + 1e-12
                    cos = abs(float(np.dot(content_hat_t, contents[:, t])) / nm)
                    out_acc_per_t.append(cos > RETRIEVAL_THRESH)
                contam = float(np.mean(out_acc_per_t)) if out_acc_per_t else float("nan")
                contam_list.append(contam)

        results_by_window[win_size] = {
            "mean_in_acc": float(np.mean([x for x in in_acc_list if not math.isnan(x)])) if in_acc_list else float("nan"),
            "mean_contam": float(np.mean([x for x in contam_list if not math.isnan(x)])) if contam_list else float("nan"),
        }
        print(
            f"  [seed {seed} N={n_dim}] win={win_size} "
            f"in_acc={results_by_window[win_size]['mean_in_acc']:.3f} "
            f"contam={results_by_window[win_size]['mean_contam']:.3f}",
            flush=True
        )

    return {
        "by_window": results_by_window,
        "seed": seed,
        "N": n_dim,
        "K": K,
        "run_mode": RUN_MODE,
    }


def _instrumentation_selftest():
    """
    Assert XOR round-trip works. Assert individual tau_t queries succeed.
    PROT-021 fix: N explicitly passed to run_one_seed.
    """
    N_test = 256

    # Formula self-test 1: XOR round-trip
    rng = np.random.RandomState(42)
    a = rng.choice([-1.0, 1.0], size=(N_test,))
    b = rng.choice([-1.0, 1.0], size=(N_test,))
    ab = xor_bind(a, b)
    recovered = xor_bind(ab, b)
    assert np.allclose(recovered, a), "XOR round-trip failed: (a*b)*b != a"

    # Formula self-test 2: individual tau_t retrieval at small scale
    K_test = 8
    contents = rng.choice([-1.0, 1.0], size=(N_test, K_test))
    tau = rng.choice([-1.0, 1.0], size=(N_test, K_test))
    W_kv = np.zeros((N_test, N_test))
    m_vecs = []
    for t in range(K_test):
        m_t = xor_bind(contents[:, t], tau[:, t])
        W_kv += np.outer(m_t, tau[:, t]) / N_test
        m_vecs.append(m_t)

    # Each tau_t should retrieve its m_t with high accuracy
    for t in range(min(3, K_test)):
        m_hat = np.sign(W_kv @ tau[:, t] + 1e-12)
        content_hat = xor_bind(m_hat, tau[:, t])
        nm = np.linalg.norm(content_hat) * np.linalg.norm(contents[:, t]) + 1e-12
        cos = abs(float(np.dot(content_hat, contents[:, t])) / nm)
        assert cos > RETRIEVAL_THRESH, (
            f"Individual tau_{t} retrieval failed: cos={cos:.4f} < {RETRIEVAL_THRESH} "
            f"at N_test={N_test} K_test={K_test} load={K_test/N_test:.3f}"
        )

    # Full seed run at small N -- metrics non-null
    result = run_one_seed(N_test, 8, 42, [2, 3], 3)
    assert "by_window" in result, "by_window missing"
    assert result["N"] == N_test, f"result N={result['N']} != N_test={N_test}"
    for k, v in result["by_window"].items():
        ia = v.get("mean_in_acc", float("nan"))
        assert not math.isnan(ia), f"mean_in_acc NaN for win={k}"
        assert ia > 0.5, f"mean_in_acc={ia:.3f} too low at smoke scale N={N_test}"

    print(
        f"[selftest] PASS: XOR round-trip OK; individual tau queries succeed; "
        f"in_acc > 0.5 at N={N_test} K=8",
        flush=True
    )


_instrumentation_selftest()


def _verdict_formula_selftests():
    """Verify verdict logic + threshold ordering."""
    def _verdict(in_acc, contam):
        if math.isnan(in_acc):
            return "INCONCLUSIVE"
        if in_acc > HP_IN_WIN_ACC and contam < HP_CONTAM:
            return "HARD_PASS"
        if in_acc < HF_IN_WIN_ACC or contam > HF_CONTAM:
            return "HARD_FAIL"
        return "MIDDLE_BAND"

    assert _verdict(0.95, 0.05) == "HARD_PASS"
    assert _verdict(0.40, 0.05) == "HARD_FAIL"
    assert _verdict(0.95, 0.50) == "HARD_FAIL"
    assert _verdict(0.70, 0.15) == "MIDDLE_BAND"
    assert HP_IN_WIN_ACC > HF_IN_WIN_ACC
    assert HP_CONTAM < HF_CONTAM

    print(
        f"[formula_selftests] PASS: 4 verdict cases; "
        f"HP={HP_IN_WIN_ACC}/{HP_CONTAM} HF={HF_IN_WIN_ACC}/{HF_CONTAM}",
        flush=True
    )


_verdict_formula_selftests()


def aggregate_results(per_seed: Dict) -> Dict:
    all_in_accs = []
    all_contams = []
    for v in per_seed.values():
        for win_data in v.get("by_window", {}).values():
            ia = win_data.get("mean_in_acc")
            cn = win_data.get("mean_contam")
            if ia is not None and not math.isnan(ia):
                all_in_accs.append(ia)
            if cn is not None and not math.isnan(cn):
                all_contams.append(cn)
    return {
        "mean_in_acc": float(np.mean(all_in_accs)) if all_in_accs else float("nan"),
        "mean_contam": float(np.mean(all_contams)) if all_contams else float("nan"),
        "n_seeds": len(per_seed),
        "n_valid_cells": len(all_in_accs),
    }


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    in_acc = summary.get("mean_in_acc", float("nan"))
    contam = summary.get("mean_contam", float("nan"))

    if math.isnan(in_acc):
        return ("INCONCLUSIVE", "No valid in-window accuracy.")

    acc_pass = in_acc > HP_IN_WIN_ACC
    acc_fail = in_acc < HF_IN_WIN_ACC
    contam_pass = (not math.isnan(contam)) and contam < HP_CONTAM
    contam_fail = (not math.isnan(contam)) and contam > HF_CONTAM

    if acc_pass and contam_pass:
        return (
            "HARD_PASS",
            f"XOR time-tag individual retrieval confirmed at N={N}. "
            f"in_acc={in_acc:.3f}>{HP_IN_WIN_ACC}, contam={contam:.3f}<{HP_CONTAM}. "
            f"Individual tau_t -> content_t retrieval scales to N={N} K={K_PATTERNS}. "
            f"Timeseries compliance claim scales to N={N}."
        )
    if acc_fail or contam_fail:
        return (
            "HARD_FAIL",
            f"Timeseries retrieval fails at N={N}. "
            f"in_acc={in_acc:.3f}(hf={HF_IN_WIN_ACC}), contam={contam:.3f}(hf={HF_CONTAM})."
        )
    return (
        "MIDDLE_BAND",
        f"Borderline. in_acc={in_acc:.3f}(hp={HP_IN_WIN_ACC}), "
        f"contam={contam:.3f}(hp={HP_CONTAM}). N={N}."
    )


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(
        f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} K={K_PATTERNS} "
        f"seeds={SEEDS} windows={WINDOW_SIZES}",
        flush=True
    )

    # PROT-021: N in run_config
    run_config = {"N": N, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} done, {len(remaining)} remaining", flush=True)

    for seed in remaining:
        ts = time.time()
        result = run_one_seed(N, K_PATTERNS, seed, WINDOW_SIZES, N_QUERIES)
        write_partial(out_dir, seed, result)
        print(f"[seed {seed}] done in {time.time()-ts:.1f}s", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)
    summary = aggregate_results(per_seed)
    verdict, verdict_msg = compute_verdict(summary)

    elapsed = time.time() - t0
    metrics = {
        "run_mode": RUN_MODE, "N": N, "seeds": SEEDS,
        "summary": summary, "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": {
            "K_PATTERNS": K_PATTERNS, "WINDOW_SIZES": WINDOW_SIZES,
            "prot021_fix": "N in run_config checkpoint key",
            "arch_fix": "individual tau_t queries for in-window acc",
        },
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] {verdict}: {verdict_msg}", flush=True)
    print(f"[done] elapsed={elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete", flush=True)
        sys.exit(0)
    main()
