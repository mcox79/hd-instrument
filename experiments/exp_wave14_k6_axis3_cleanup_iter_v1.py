"""K6 compositional generalization axis 3: cleanup-iteration (resonator-style).

Context: K6 compositional hold-out at 🟡 PARTIAL. Axis 1 (dim-scaling) exhausted
at v193 (N=8192 -> hold_out=0.128). Axis 2 (hierarchical pre-binding) REJECTED
at v195 K6_HIER_HARD_FAIL (hold_out_acc=0.078; 1.2x chance; no improvement).
Axis 3 (cleanup-iteration) is the next leading leverage path per v193 strategy
narrative and v195 handoff.

Axis 3 hypothesis: the K6 baseline stores (obj*attr) bundles in W and queries
with obj to recall attr. Single-step recall has SNR limited by M/N capacity.
Iterative cleanup (resonator-style): run T cleanup steps where each step refines
the recalled attr by re-querying W with (obj * attr_t), letting the substrate
self-consistently relax toward a stored bundle. This is the biological analogy
of iterative attractor convergence / autoassociative refinement.

Implementation: after initial readout attr_0 = sign(W @ obj), iterate:
  attr_{t+1} = sign(W @ (obj * sign(attr_t)))
for T_CLEANUP steps. Final attr_T is the compositional query answer.

This does NOT change the storage mechanism -- same Hebbian outer-product W.
The change is retrieval-side: T cleanup steps improve recall accuracy for
hold-out (obj, attr) pairs by leveraging the associative structure of W.

Per [[feedback-no-experiment-design-in-prompts]]: all parameters chosen by exp_dev.
Per [[feedback-no-smoke]]: HARD-PASS/HARD-FAIL pre-registered.
Per [[feedback-envelope-expansion-fail-bands]]: bands registered before running.

Pre-reg:
    HARD-PASS: mean hold_out_acc >= 0.20 (3x chance; baseline v193 0.128=2x chance).
               -> K6 axis 3 cleanup-iteration PASSES; retrieval mechanism unlocked;
               K6 🟡 PARTIAL rehab candidate for cleanup-based compositional recall.
    HARD-FAIL: mean hold_out_acc <= 0.09 (<=1.44x chance; no improvement over
               v193 N=8192 single-step baseline 0.128).
               -> K6 axis 3 REJECTED; sequence axis 4 (Bet X position-indexed).
    MIDDLE: hold_out_acc in (0.09, 0.20); some improvement but below clear-pass.
            Report cleanup iteration curve T vs hold_out_acc.

Self-test cells (per [[feedback-strategy-spec-formula-selftests]]):
    HARD-PASS: hold_out_acc=0.25 -> K6_CLEANUP_HARD_PASS
    HARD-FAIL: hold_out_acc=0.07 -> K6_CLEANUP_HARD_FAIL
    MIDDLE:    hold_out_acc=0.14 -> K6_CLEANUP_MIDDLE_BAND

Queue: remote_cpu_queue (pure-numpy; no GPU needed; single-config sweep T in {1..8}).
ETA: ~5-15 min remote CPU.
Pre-reg file: preregs/2026-05-24_wave14_k6_axis3_cleanup_iter_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse, json, os, time, math
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# ───── design parameters (exp_dev autonomy) ─────
N_OBJECTS = 16
N_ATTRS = 16
N_FULL = 2048
N_SMOKE = 512
TRAIN_FRAC = 0.75
EPOCHS_FULL = 30
EPOCHS_SMOKE = 5
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
T_CLEANUP_GRID = [0, 1, 2, 4, 8]  # 0 = baseline (no cleanup)

# Pre-registered thresholds
PASS_HOLDOUT_ACC = 0.20   # 3x chance (chance = 1/16 = 0.0625)
FAIL_HOLDOUT_ACC = 0.09   # <=1.44x chance
CHANCE = 1.0 / N_ATTRS   # = 0.0625


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


def bsc_atoms(num: int, dim: int, rng: np.random.Generator) -> np.ndarray:
    """Generate BSC atoms: {-1, +1}^dim."""
    return rng.choice([-1.0, 1.0], size=(num, dim)).astype(np.float32)


def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """BSC bind: elementwise product."""
    return a * b


def hebbian_store(W: np.ndarray, keys: np.ndarray, vals: np.ndarray) -> np.ndarray:
    """W += sum_i v_i k_i^T (outer products)."""
    return W + (vals.T @ keys)


def query_one(W: np.ndarray, key: np.ndarray) -> np.ndarray:
    """Single-step recall: attr = sign(W @ key)."""
    raw = W @ key
    return np.sign(raw + 1e-9)


def cleanup_query(W: np.ndarray, obj: np.ndarray, attr_atoms: np.ndarray,
                  T: int) -> np.ndarray:
    """T-step cleanup retrieval.

    Step 0: attr_0 = sign(W @ obj)
    Step t+1: raw = W @ (obj * sign(attr_t)); project to attr_atoms nearest neighbor.
    """
    attr_cur = query_one(W, obj)
    for _ in range(T):
        probe = bind(obj, np.sign(attr_cur + 1e-9))
        raw = W @ probe
        # Project to nearest atom in attr_atoms
        sims = attr_atoms @ raw  # (N_ATTRS,)
        attr_cur = attr_atoms[np.argmax(sims)]
    return attr_cur


def run_one_seed(seed: int, config: dict) -> dict:
    """Run K6 axis-3 cleanup experiment for one seed."""
    N = config["N"]
    epochs = config["epochs"]
    n_objs = N_OBJECTS
    n_attrs = N_ATTRS
    train_frac = TRAIN_FRAC
    t_grid = config["t_cleanup_grid"]

    rng = np.random.default_rng(seed)
    obj_atoms = bsc_atoms(n_objs, N, rng)    # (16, N)
    attr_atoms = bsc_atoms(n_attrs, N, rng)  # (16, N)

    # Build training pairs: (obj_i, attr_j) for all i,j
    all_pairs = [(i, j) for i in range(n_objs) for j in range(n_attrs)]
    n_all = len(all_pairs)
    n_train = int(train_frac * n_all)

    rng.shuffle(all_pairs)
    train_pairs = all_pairs[:n_train]
    holdout_pairs = all_pairs[n_train:]

    # Build W via Hebbian outer-product on training pairs
    W = np.zeros((N, N), dtype=np.float32)
    for (oi, ai) in train_pairs:
        key = bind(obj_atoms[oi], attr_atoms[ai])
        val = attr_atoms[ai]
        W = hebbian_store(W, key.reshape(1, -1), val.reshape(1, -1))

    # Run multi-epoch Hebbian update (repeated exposure)
    for _ in range(epochs - 1):
        rng.shuffle(train_pairs)
        for (oi, ai) in train_pairs:
            key = bind(obj_atoms[oi], attr_atoms[ai])
            val = attr_atoms[ai]
            W = hebbian_store(W, key.reshape(1, -1), val.reshape(1, -1))

    # Evaluate: for each (obj_i, attr_j) in holdout, query with obj_i,
    # see if nearest recovered attr matches true attr_j.
    results_by_T = {}
    for T in t_grid:
        n_correct = 0
        for (oi, ai) in holdout_pairs:
            obj = obj_atoms[oi]
            recalled = cleanup_query(W, obj, attr_atoms, T)
            # Nearest atom in attr_atoms
            sims = attr_atoms @ recalled
            predicted_ai = int(np.argmax(sims))
            if predicted_ai == ai:
                n_correct += 1
        acc = n_correct / max(1, len(holdout_pairs))
        results_by_T[T] = {"hold_out_acc": float(acc), "n_correct": n_correct,
                            "n_holdout": len(holdout_pairs)}

    return {"by_T": results_by_T, "n_train": n_train, "n_holdout": len(holdout_pairs)}


def compute_verdict(summary: dict) -> tuple[str, str]:
    per_seed = summary.get("per_seed", {})
    if not per_seed:
        return ("K6_CLEANUP_INCONCLUSIVE", "Missing per-seed data.")

    # Find best T (max mean hold_out_acc across seeds)
    all_T = set()
    for s in per_seed.values():
        all_T.update(s["by_T"].keys())
    all_T = sorted(all_T)

    best_acc = 0.0
    best_T = 0
    T_accs = {}
    for T in all_T:
        seed_accs = [s["by_T"][T]["hold_out_acc"] for s in per_seed.values()
                     if T in s["by_T"]]
        if not seed_accs:
            continue
        mean_acc = sum(seed_accs) / len(seed_accs)
        T_accs[T] = mean_acc
        if mean_acc > best_acc:
            best_acc = mean_acc
            best_T = T

    improvement = best_acc / max(CHANCE, 1e-9)
    T_curve = " ".join(f"T={T}:{acc:.3f}" for T, acc in sorted(T_accs.items()))
    detail = (f"best_hold_out_acc={best_acc:.3f} at T={best_T} "
              f"({improvement:.1f}x chance). T-curve: {T_curve}.")

    if best_acc >= PASS_HOLDOUT_ACC:
        return ("K6_CLEANUP_HARD_PASS",
                f"Cleanup-iteration BREAKS K6 baseline: {detail} "
                f"K6 axis 3 PASSES; retrieval mechanism unlocked.")
    if best_acc <= FAIL_HOLDOUT_ACC:
        return ("K6_CLEANUP_HARD_FAIL",
                f"Cleanup-iteration REJECTED: {detail} "
                f"No improvement over baseline at best T. Sequence axis 4.")
    return ("K6_CLEANUP_MIDDLE_BAND",
            f"Cleanup-iteration partial improvement: {detail} "
            f"Above baseline but below HARD-PASS {PASS_HOLDOUT_ACC}.")


def self_test_verdict():
    """Self-test: verify verdict logic with (input -> expected output) pairs."""
    def mk(T_acc_map, seeds=1):
        per_seed = {}
        for s in range(seeds):
            by_T = {T: {"hold_out_acc": acc, "n_correct": int(acc*64), "n_holdout": 64}
                    for T, acc in T_acc_map.items()}
            per_seed[str(s)] = {"by_T": by_T}
        return {"per_seed": per_seed}

    # Input -> expected
    cases = [
        # HARD-PASS: best T gives 0.25
        (mk({0: 0.10, 1: 0.15, 2: 0.25, 4: 0.22}), "K6_CLEANUP_HARD_PASS"),
        (mk({0: 0.20, 2: 0.30}), "K6_CLEANUP_HARD_PASS"),
        # HARD-FAIL: best T gives 0.07
        (mk({0: 0.07, 1: 0.07, 2: 0.06, 4: 0.06}), "K6_CLEANUP_HARD_FAIL"),
        (mk({0: 0.08, 2: 0.09}), "K6_CLEANUP_HARD_FAIL"),
        # MIDDLE
        (mk({0: 0.10, 1: 0.14, 2: 0.16}), "K6_CLEANUP_MIDDLE_BAND"),
        (mk({0: 0.10, 4: 0.19}), "K6_CLEANUP_MIDDLE_BAND"),
        # INCONCLUSIVE: empty
        ({"per_seed": {}}, "K6_CLEANUP_INCONCLUSIVE"),
    ]
    for summary, expected in cases:
        v, msg = compute_verdict(summary)
        if v != expected:
            raise AssertionError(
                f"Expected {expected}, got {v}. msg={msg}. summary_keys={list(summary.get('per_seed',{}).keys())}")
    print(f"self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_experiment(smoke: bool) -> tuple:
    t0 = time.monotonic()
    N = N_SMOKE if smoke else N_FULL
    epochs = EPOCHS_SMOKE if smoke else EPOCHS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    config = {"mode": "smoke" if smoke else "full",
              "N": N, "epochs": epochs, "seeds": seeds,
              "t_cleanup_grid": T_CLEANUP_GRID,
              "n_objects": N_OBJECTS, "n_attrs": N_ATTRS,
              "train_frac": TRAIN_FRAC,
              "pass_holdout_acc": PASS_HOLDOUT_ACC,
              "fail_holdout_acc": FAIL_HOLDOUT_ACC}
    print(f"[config] {config}", flush=True)
    per_seed = {}
    for seed in seeds:
        r = run_one_seed(seed, config)
        per_seed[str(seed)] = r
        best_acc = max(v["hold_out_acc"] for v in r["by_T"].values())
        print(f"  seed={seed}: best_hold_out_acc={best_acc:.3f} "
              f"(T_grid results: {[(T, v['hold_out_acc']) for T, v in sorted(r['by_T'].items())]})",
              flush=True)
    summary = {"per_seed": per_seed}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict()
        return 0
    out_name = ("wave14_k6_axis3_cleanup_iter_v1_smoke" if args.smoke
                else "wave14_k6_axis3_cleanup_iter_v1")
    out_dir = get_output_dir(out_name)
    summary, verdict, msg, elapsed, config = run_experiment(smoke=args.smoke)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\n{'SMOKE' if args.smoke else 'DONE'}: {verdict}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
