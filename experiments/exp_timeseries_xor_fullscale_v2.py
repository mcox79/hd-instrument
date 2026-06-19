"""
timeseries_xor_fullscale_v2 -- Time-tag XOR range query correctness at full scale.

Extends timeseries_xor_range_v1 (completed) to:
  - N=4096 (vs N=1024 in v1)
  - More seeds (5)
  - Extended K sweep (K=50 patterns)
  - Multiple window sizes

Same pre-reg thresholds as v1 (confirmed by v1 PASS):
  HARD-PASS: in-window accuracy > 85% AND out-of-window contamination < 20%.
  MIDDLE:    in-window [50%, 85%] OR contamination [20%, 40%].
  HARD-FAIL: in-window < 50% OR contamination > 40%.

The question now: do the same thresholds hold at N=4096 with more patterns?
If YES: time-series compliance claim scales beyond smoke-scale.
If NO: identify the N-dependent degradation pattern.

No _nN suffix; production N=4096 per rule 3.
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

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "timeseries_xor_fullscale_v2"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 4096

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

HP_IN_WIN_ACC = 0.85
HF_IN_WIN_ACC = 0.50
HP_CONTAM = 0.20
HF_CONTAM = 0.40


def xor_bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return a * b


def hopfield_update_kv(W_kv: np.ndarray, x: np.ndarray, n_iters: int = 1) -> np.ndarray:
    """Single-step KV retrieval: sign(W_kv @ query). W_kv is asymmetric."""
    raw = W_kv @ x
    return np.sign(raw + 1e-12)


def run_one_seed(N: int, K: int, seed: int, window_sizes: List[int], n_queries: int) -> Dict:
    rng = np.random.RandomState(seed)

    contents = rng.choice([-1.0, 1.0], size=(N, K))
    tau = rng.choice([-1.0, 1.0], size=(N, K))

    # Key-value W: W @ tau_t -> m_t = content_t XOR tau_t
    W_kv = np.zeros((N, N))
    m_vecs = []
    for t in range(K):
        m_t = xor_bind(contents[:, t], tau[:, t])
        W_kv += np.outer(m_t, tau[:, t]) / N
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

            # Build range query by bundling tau vectors in window
            tau_window_vecs = [tau[:, t] for t in in_window]
            if not tau_window_vecs:
                continue
            bundle = np.sign(np.sum(tau_window_vecs, axis=0) + 1e-12)

            retrieved = hopfield_update_kv(W_kv, bundle)

            # Check in-window patterns
            in_sims = []
            for t in in_window:
                m_t = m_vecs[t]
                s = abs(np.dot(retrieved, m_t)) / (np.linalg.norm(retrieved) * np.linalg.norm(m_t) + 1e-12)
                in_sims.append(s)
            in_acc = float(np.mean([s > RETRIEVAL_THRESH for s in in_sims]))
            in_acc_list.append(in_acc)

            # Check out-of-window patterns
            if out_window:
                out_sims = []
                for t in out_window:
                    m_t = m_vecs[t]
                    s = abs(np.dot(retrieved, m_t)) / (np.linalg.norm(retrieved) * np.linalg.norm(m_t) + 1e-12)
                    out_sims.append(s)
                contam = float(np.mean([s > RETRIEVAL_THRESH for s in out_sims]))
                contam_list.append(contam)

        results_by_window[win_size] = {
            "mean_in_acc": float(np.mean(in_acc_list)) if in_acc_list else float("nan"),
            "mean_contam": float(np.mean(contam_list)) if contam_list else float("nan"),
        }
        print(f"  [seed {seed}] win={win_size} in_acc={results_by_window[win_size]['mean_in_acc']:.3f} "
              f"contam={results_by_window[win_size]['mean_contam']:.3f}", flush=True)

    return {"by_window": results_by_window, "seed": seed, "N": N, "K": K, "run_mode": RUN_MODE}


def _instrumentation_selftest():
    """Assert metrics non-null."""
    result = run_one_seed(256, 8, 42, [2, 3], 3)
    assert "by_window" in result, "by_window missing"
    assert len(result["by_window"]) >= 1, "no window results"
    for k, v in result["by_window"].items():
        assert "mean_in_acc" in v, f"mean_in_acc missing for win={k}"
        assert not math.isnan(v["mean_in_acc"]), f"in_acc NaN for win={k}"
    print("[selftest] PASS: timeseries metrics non-null at N=256 K=8", flush=True)


_instrumentation_selftest()


def aggregate_results(per_seed: Dict) -> Dict:
    all_in_accs = []
    all_contams = []
    for v in per_seed.values():
        for win_data in v["by_window"].values():
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
    }


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    in_acc = summary.get("mean_in_acc", 0.0)
    contam = summary.get("mean_contam", 1.0)

    if math.isnan(in_acc):
        return ("INCONCLUSIVE", "No valid in-window accuracy.")

    acc_pass = in_acc > HP_IN_WIN_ACC
    acc_fail = in_acc < HF_IN_WIN_ACC
    contam_pass = contam < HP_CONTAM
    contam_fail = contam > HF_CONTAM

    if acc_pass and contam_pass:
        return ("HARD_PASS",
                f"XOR time-tag range query confirmed at N={N}. "
                f"in_acc={in_acc:.3f}>{HP_IN_WIN_ACC}, "
                f"contam={contam:.3f}<{HP_CONTAM}. "
                f"Time-series compliance claim scales to N=4096.")
    if acc_fail or contam_fail:
        return ("HARD_FAIL",
                f"Range query fails at N={N}. "
                f"in_acc={in_acc:.3f}(hf={HF_IN_WIN_ACC}), "
                f"contam={contam:.3f}(hf={HF_CONTAM}).")
    return ("MIDDLE_BAND",
            f"Borderline. in_acc={in_acc:.3f}(hp={HP_IN_WIN_ACC}), "
            f"contam={contam:.3f}(hp={HP_CONTAM}).")


def _verdict_formula_selftests():
    s1 = {"mean_in_acc": 0.90, "mean_contam": 0.12, "n_seeds": 5}
    v1, _ = compute_verdict(s1)
    assert v1 == "HARD_PASS", f"Expected HARD_PASS got {v1}"

    s2 = {"mean_in_acc": 0.40, "mean_contam": 0.12, "n_seeds": 5}
    v2, _ = compute_verdict(s2)
    assert v2 == "HARD_FAIL", f"Expected HARD_FAIL got {v2}"

    s3 = {"mean_in_acc": 0.70, "mean_contam": 0.25, "n_seeds": 5}
    v3, _ = compute_verdict(s3)
    assert v3 == "MIDDLE_BAND", f"Expected MIDDLE_BAND got {v3}"

    print("[formula_selftests] PASS: 3 verdict cases verified", flush=True)


_verdict_formula_selftests()


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} K={K_PATTERNS} seeds={SEEDS}", flush=True)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} done, {len(remaining)} remaining", flush=True)

    for seed in remaining:
        ts = time.time()
        result = run_one_seed(N, K_PATTERNS, seed, WINDOW_SIZES, N_QUERIES)
        result["seed"] = seed
        result["N"] = N
        result["run_mode"] = RUN_MODE
        write_partial(out_dir, seed, result)
        print(f"[seed {seed}] done in {time.time()-ts:.1f}s", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)
    summary = aggregate_results(per_seed)
    verdict, verdict_msg = compute_verdict(summary)

    elapsed = time.time() - t0
    metrics = {
        "run_mode": RUN_MODE,
        "N": N,
        "seeds": SEEDS,
        "summary": summary,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": {"K_PATTERNS": K_PATTERNS, "WINDOW_SIZES": WINDOW_SIZES},
    }
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] {verdict}: {verdict_msg}", flush=True)
    print(f"[done] elapsed={elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    main()
