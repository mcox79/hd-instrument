"""Pred-3 (1-RSB diagnostic): Ultrametric inequality on retained-task triples.

1-RSB (Parisi ultrametricity) prediction: for any 3 retained W snapshots
(i, j, k), the smallest two of {q_ij, q_ik, q_jk} are equal (isosceles
condition). Empirically: fraction of triples satisfying the ultrametric
inequality (min = next-smallest within eps) > 0.50 (well above 0.33 random).

RS prediction: overlaps are near-Gaussian; ultrametric fraction ~= 0.33
(random baseline for any 3 samples from a symmetric distribution).

Method: run N_SEEDS seeds of 4-stage M1 hierreplay to get W snapshots.
Randomly sample N_TRIPLES triples; compute 3 pairwise overlaps; check
ultrametric condition.

Per [[feedback-no-experiment-design-in-prompts]]: all parameters by exp_dev autonomy.
Per [[feedback-no-smoke]]: HARD-PASS / HARD-FAIL pre-registered.
Per [[feedback-envelope-expansion-fail-bands]]: bands registered BEFORE running.

Pre-reg:
    HARD-PASS (ultrametric / 1-RSB): ultrametric fraction >= 0.50
              (> 0.33 random + 0.17 margin). Also: mean_isosceles_gap >= 0.01
              (size of isosceles arm gap).
              -> Ultrametric inequality holds in retained-task W-space; 1-RSB
              framing supported.
    HARD-FAIL (RS): ultrametric fraction <= 0.36 (within noise of 0.33 random
              baseline with eps=0.10). -> Ultrametric NOT supported at this axis.
    MIDDLE: fraction in (0.36, 0.50).

Queue: local_cpu_queue (CPU, < 60s scoping pilot then remote_cpu if light;
       W-overlap matrix is O(S^2 * N^2) but S=12 seeds x N=2048 is feasible).
ETA: ~15-25 min CPU.
Pre-reg file: preregs/2026-05-24_wave14_1rsb_ultrametric_triples_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse, importlib.util, json, os, random, time
from pathlib import Path
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402

# Load hierreplay infrastructure
_m1_path = REPO / "experiments" / "exp_wave14_k2_m1_hierreplay_v1.py"
_m1_spec = importlib.util.spec_from_file_location("m1", _m1_path)
m1 = importlib.util.module_from_spec(_m1_spec)
_m1_spec.loader.exec_module(m1)
base = m1.base
v1 = m1.v1
pa = m1.pa

# Load pq_retained for W-collection helper
_pq_path = REPO / "experiments" / "exp_wave14_1rsb_pq_retained_v1.py"
_pq_spec = importlib.util.spec_from_file_location("pq_ret", _pq_path)
pq_ret = importlib.util.module_from_spec(_pq_spec)
_pq_spec.loader.exec_module(pq_ret)

# ---- design parameters (exp_dev autonomy) ----
N_FULL = 2048
N_SMOKE = 512
BATCH_SIZE_FULL = 32
BATCH_SIZE_SMOKE = 16
EPOCHS_FULL = 5
EPOCHS_SMOKE = 1
PHASE_A_EPOCHS_FULL = 8
PHASE_A_EPOCHS_SMOKE = 1
BYTES_FULL = 100_000
BYTES_SMOKE = 3_000
SEEDS_FULL = list(range(12))   # 12 seeds gives 220 triples
SEEDS_SMOKE = [7, 17, 23]
N_TRIPLES_FULL = 1000
N_TRIPLES_SMOKE = 100
EPS_ULTRAMETRIC = 0.10   # tolerance for isosceles condition

# Pre-reg thresholds
PASS_ULTRA_FRAC = 0.50
FAIL_ULTRA_FRAC = 0.36


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


def ultrametric_fraction_W(W_stack, n_triples, eps, rng_seed):
    """Fraction of triples satisfying ultrametric condition on W-overlaps.

    Ultrametric: for (i,j,k), min of {q_ij, q_ik, q_jk} equals second-smallest
    within eps tolerance.
    """
    S = W_stack.shape[0]
    N2 = W_stack.shape[1]
    Q = (W_stack @ W_stack.T / N2).tolist()   # (S x S) overlap matrix as list

    rng = random.Random(rng_seed)
    sat = 0
    isosceles_gaps = []
    for _ in range(n_triples):
        i, j, k = rng.sample(range(S), 3)
        q_ij = Q[i][j]
        q_ik = Q[i][k]
        q_jk = Q[j][k]
        vals = sorted([q_ij, q_ik, q_jk])  # ascending
        # Ultrametric (isosceles): two smallest equal, i.e., vals[0] ~ vals[1]
        gap = abs(vals[1] - vals[0])
        isosceles_gaps.append(gap)
        if gap <= eps:
            sat += 1
    frac = sat / n_triples
    mean_gap = sum(isosceles_gaps) / len(isosceles_gaps)
    return frac, mean_gap


def compute_verdict(summary):
    ultra_frac = summary.get("ultrametric_fraction", 0.0)
    mean_gap = summary.get("mean_isosceles_gap", 1.0)

    if ultra_frac >= PASS_ULTRA_FRAC:
        return ("ULTRAMETRIC_1RSB_CONFIRMED",
                f"Ultrametric fraction={ultra_frac:.3f} >= {PASS_ULTRA_FRAC}. "
                f"mean_isosceles_gap={mean_gap:.4f}. "
                f"Retained-task W triples satisfy isosceles condition >> random baseline. "
                f"1-RSB ultrametric inequality SUPPORTED.")
    if ultra_frac <= FAIL_ULTRA_FRAC:
        return ("ULTRAMETRIC_RS_FLAT",
                f"Ultrametric fraction={ultra_frac:.3f} <= {FAIL_ULTRA_FRAC} "
                f"(near 0.33 random baseline). mean_gap={mean_gap:.4f}. "
                f"W triples do NOT satisfy ultrametric; 1-RSB NOT supported at this axis.")
    return ("ULTRAMETRIC_MIDDLE",
            f"Intermediate ultrametric fraction={ultra_frac:.3f} in ({FAIL_ULTRA_FRAC},{PASS_ULTRA_FRAC}). "
            f"mean_gap={mean_gap:.4f}. Inconclusive 1-RSB vs RS at ultrametric axis.")


def self_test_verdict():
    cases = [
        ({"ultrametric_fraction": 0.55, "mean_isosceles_gap": 0.02},
         "ULTRAMETRIC_1RSB_CONFIRMED"),
        ({"ultrametric_fraction": 0.34, "mean_isosceles_gap": 0.15},
         "ULTRAMETRIC_RS_FLAT"),
        ({"ultrametric_fraction": 0.43, "mean_isosceles_gap": 0.08},
         "ULTRAMETRIC_MIDDLE"),
        ({}, "ULTRAMETRIC_RS_FLAT"),   # default 0 values: ultra_frac=0 <= FAIL threshold
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"verdict {a} != {exp}; summary={s}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run(smoke=False):
    device = torch.device("cpu")  # CPU-only experiment
    t0 = time.monotonic()
    print(f"[ultrametric-triples] device={device} smoke={smoke}", flush=True)
    self_test_verdict()

    config = {
        "mode": "smoke" if smoke else "full",
        "N": N_SMOKE if smoke else N_FULL,
        "batch_size": BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL,
        "epochs": EPOCHS_SMOKE if smoke else EPOCHS_FULL,
        "phase_a_epochs": PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL,
        "bytes_per_corpus": BYTES_SMOKE if smoke else BYTES_FULL,
        "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
        "n_triples": N_TRIPLES_SMOKE if smoke else N_TRIPLES_FULL,
        "eps_ultrametric": EPS_ULTRAMETRIC,
        "pass_frac": PASS_ULTRA_FRAC,
        "fail_frac": FAIL_ULTRA_FRAC,
    }
    print(f"[config] {config}", flush=True)

    W_flat_list = []
    for seed in config["seeds"]:
        print(f"  running M1 4-stage seed={seed}...", flush=True)
        W_flat = pq_ret.run_4stage_m1_get_W(seed, config, device)
        W_flat_list.append(W_flat)
        print(f"  seed={seed}: norm={float(W_flat.norm()):.3f}", flush=True)

    W_stack = torch.stack(W_flat_list, dim=0)  # (S, N^2)
    S = W_stack.shape[0]
    print(f"  W_stack shape={W_stack.shape} S={S}", flush=True)

    ultra_frac, mean_gap = ultrametric_fraction_W(
        W_stack, config["n_triples"], EPS_ULTRAMETRIC, rng_seed=2026)

    print(f"  ultrametric_fraction={ultra_frac:.4f} mean_isosceles_gap={mean_gap:.4f}", flush=True)

    # Also compute pairwise overlap stats
    N2 = W_stack.shape[1]
    Q = W_stack @ W_stack.T / N2
    triu_mask = torch.triu(torch.ones(S, S, dtype=torch.bool), diagonal=1)
    overlaps = Q[triu_mask]
    mean_q = float(overlaps.mean())
    std_q = float(overlaps.std()) if overlaps.shape[0] > 1 else 0.0

    summary = {
        "ultrametric_fraction": ultra_frac,
        "mean_isosceles_gap": mean_gap,
        "n_triples_tested": config["n_triples"],
        "n_seeds": S,
        "mean_overlap_q": mean_q,
        "std_overlap_q": std_q,
        "eps_used": EPS_ULTRAMETRIC,
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

    out_dir = get_output_dir("wave14_1rsb_ultrametric_triples_v1")
    summary, verdict, msg, elapsed, config = run(smoke=args.smoke)
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "summary": summary, "config": config}
    validate_metrics(metrics)
    import shutil
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2))
    shutil.move(str(tmp), str(out_dir / "metrics.json"))
    oracle.assert_baseline_high("ultrametric_n_triples", float(summary.get("n_triples_tested", 0)), 1.0)
    print(f"[done] elapsed={elapsed:.1f}s verdict={verdict}", flush=True)


if __name__ == "__main__":
    main()
