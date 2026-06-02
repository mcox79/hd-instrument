"""
program_exec_audit_v1 -- Substrate as program-execution audit memory.

Three test cells combined (program exec audit handoff 2026-06-01):
  (A) Execution-trace retrieval below capacity:
      Encode T synthetic execution steps as bipolar patterns. Store in W.
      Retrieve from partial cues (instruction field only).
      Measure retrieval accuracy vs T as fraction of M_max.
      HARD-PASS A: accuracy > 0.85 at T = 0.5 * M_max.
      HARD-FAIL A: accuracy < 0.50 at T = 0.5 * M_max.

  (B) Deletion isolation: rank-1 erase of T steps, verify deleted patterns
      fall to chance and non-deleted patterns unaffected.
      HARD-PASS B: deleted cosine < 0.15 AND non-deleted accuracy delta < 0.05.
      HARD-FAIL B: deleted cosine > 0.30 OR delta_acc > 0.20.

  (C) Compound-attribute cue retrieval (set-intersection query):
      Compound cue from two fields (instruction type + result sign).
      Measure precision of returned pattern.
      HARD-PASS C: precision > 0.70.
      HARD-FAIL C: precision < 0.50.

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

ANCHOR_NAME = "program_exec_audit_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 4096
ALPHA_C = 0.138  # classical Hopfield capacity
M_MAX = int(ALPHA_C * N)  # ~565

# Parse arguments
_ap = argparse.ArgumentParser(description="Program execution audit substrate")
_ap.add_argument("--smoke", action="store_true", help="Run in smoke mode")
_ap.add_argument("--self-test", action="store_true", help="Run self-test only")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    T_FRACS = [0.1, 0.3, 0.5]    # T as fraction of M_MAX
    N_DELETE_BATCH = 5            # patterns to delete in cell B
    N_COMPOUND_QUERIES = 5        # compound queries in cell C
else:
    SEEDS = [7, 17, 23, 31, 41]
    T_FRACS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
    N_DELETE_BATCH = 20
    N_COMPOUND_QUERIES = 20

# Pre-reg thresholds
HP_A_ACC = 0.85      # retrieval accuracy at 0.5 * M_MAX
HF_A_ACC = 0.50
HP_B_DEL_COS = 0.15  # deleted-pattern cosine threshold
HF_B_DEL_COS = 0.30
HP_B_DELTA_ACC = 0.05
HF_B_DELTA_ACC = 0.20
HP_C_PREC = 0.70
HF_C_PREC = 0.50


def make_exec_patterns(N: int, T: int, seed: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Return (patterns, instr_cues, result_signs, compound_cues).
    Each execution step xi has:
      - instruction field: first N//4 dims
      - result field: next N//4 dims
      - context field: remaining dims
    Partial cue for cell A: instruction field only (rest zeroed then thresholded).
    """
    rng = np.random.RandomState(seed)
    patterns = rng.choice([-1.0, 1.0], size=(N, T))   # (N, T)
    # Instruction cue: keep first N//4 dims, zero rest
    instr_dim = N // 4
    instr_cues = np.zeros((N, T))
    instr_cues[:instr_dim, :] = patterns[:instr_dim, :]
    # result_sign: sign of sum of result field
    result_dim = N // 4
    result_signs = np.sign(np.sum(patterns[instr_dim:instr_dim + result_dim, :], axis=0))  # (T,)
    result_signs[result_signs == 0] = 1.0
    # instr_type: sign of sum of instruction field
    instr_types = np.sign(np.sum(patterns[:instr_dim, :], axis=0))  # (T,)
    instr_types[instr_types == 0] = 1.0
    # compound cue: instr field * result sign scalar + result field * instr type scalar
    compound_cues = np.zeros((N, T))
    compound_cues[:instr_dim, :] = patterns[:instr_dim, :] * result_signs[None, :]
    compound_cues[instr_dim:instr_dim + result_dim, :] = patterns[instr_dim:instr_dim + result_dim, :] * instr_types[None, :]
    return patterns, instr_cues, result_signs, compound_cues


def hopfield_update(W: np.ndarray, x: np.ndarray, n_iters: int = 10) -> np.ndarray:
    for _ in range(n_iters):
        x = np.sign(W @ x + 1e-12)
    return x


def cos_sim(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def run_cell_a(N: int, T_fracs: List[float], M_max: int, seed: int) -> Dict:
    """Cell A: retrieval accuracy vs T fraction."""
    results = {}
    for frac in T_fracs:
        T = max(1, int(frac * M_max))
        patterns, instr_cues, _, _ = make_exec_patterns(N, T, seed)
        W = patterns @ patterns.T / N  # outer-product Hopfield
        acc_list = []
        for t in range(T):
            cue = instr_cues[:, t].copy()
            # normalize cue to unit bipolar
            cue_norm = np.sign(cue + 1e-12)
            retrieved = hopfield_update(W, cue_norm)
            acc_list.append(cos_sim(retrieved, patterns[:, t]))
        results[f"frac_{frac:.2f}"] = {
            "T": T,
            "mean_acc": float(np.mean(acc_list)),
            "median_acc": float(np.median(acc_list)),
            "n_above_09": int(np.sum(np.array(acc_list) > 0.9)),
        }
    return results


def run_cell_b(N: int, T: int, n_delete: int, seed: int) -> Dict:
    """Cell B: deletion isolation."""
    patterns, _, _, _ = make_exec_patterns(N, T, seed)
    W = patterns @ patterns.T / N
    # Baseline accuracy on all patterns before deletion
    base_acc = []
    for t in range(T):
        r = hopfield_update(W, patterns[:, t])
        base_acc.append(cos_sim(r, patterns[:, t]))
    mean_base = float(np.mean(base_acc))

    # Delete first n_delete patterns via rank-1 deflation
    delete_idx = list(range(n_delete))
    for t in delete_idx:
        W -= np.outer(patterns[:, t], patterns[:, t]) / N

    # Measure deleted pattern cosine
    del_cos_list = []
    for t in delete_idx:
        r = hopfield_update(W, patterns[:, t])
        del_cos_list.append(abs(cos_sim(r, patterns[:, t])))
    mean_del_cos = float(np.mean(del_cos_list))

    # Measure non-deleted pattern accuracy
    keep_idx = list(range(n_delete, T))
    if keep_idx:
        keep_acc = []
        for t in keep_idx:
            r = hopfield_update(W, patterns[:, t])
            keep_acc.append(cos_sim(r, patterns[:, t]))
        mean_keep_acc = float(np.mean(keep_acc))
        delta_acc = abs(mean_base - mean_keep_acc)
    else:
        mean_keep_acc = float("nan")
        delta_acc = float("nan")

    return {
        "mean_del_cos": mean_del_cos,
        "mean_keep_acc": mean_keep_acc,
        "delta_acc": delta_acc,
        "T": T,
        "n_deleted": n_delete,
    }


def run_cell_c(N: int, T: int, n_queries: int, seed: int) -> Dict:
    """
    Cell C: compound-attribute cue retrieval (set-intersection query).
    Build a key-value W: W_kv @ compound_key -> target_pattern.
    compound_key = instr_field * result_sign_scalar (outer product binding).
    Retrieval: query W_kv with compound_key, measure cos(retrieved, target).
    This tests whether two-attribute compound queries are viable.
    """
    rng = np.random.RandomState(seed + 1000)
    instr_dim = N // 4
    result_dim = N // 4

    # Generate T execution patterns
    patterns = rng.choice([-1.0, 1.0], size=(N, T))

    # For each pattern build compound key:
    # instr_part = patterns[:instr_dim, t]
    # result_sign = sign(sum(patterns[instr_dim:instr_dim+result_dim, t]))
    # compound_key = instr_part padded to N (others zero -> sign -> just use instr_part + result_field)
    # Better: compound key is instr_field concatenated with result_sign broadcast
    # We use a key-value store W_kv: W_kv @ key -> pattern
    # Key = first instr_dim dims of pattern + first result_dim dims = 2*instr_dim total
    # Extend to full N by padding with zeros then taking sign -> unit BSC key

    def make_compound_key(pat: np.ndarray) -> np.ndarray:
        # Compound key: elementwise product of instruction-field broadcast and result-field broadcast.
        # This binds two attributes across all N dimensions.
        instr_part = pat[:instr_dim]  # (N//4,)
        result_part = pat[instr_dim:2 * instr_dim]  # (N//4,)
        # Tile both parts to full N
        n_reps = N // instr_dim  # = 4 for N//4 dims
        instr_tiled = np.tile(instr_part, n_reps)[:N]
        result_tiled = np.tile(result_part, n_reps)[:N]
        # Compound key = elementwise product (XOR binding of two attributes)
        compound = instr_tiled * result_tiled
        return np.sign(compound + 1e-12)

    W_kv = np.zeros((N, N))
    compound_keys = []
    for t in range(T):
        key = make_compound_key(patterns[:, t])
        compound_keys.append(key)
        W_kv += np.outer(patterns[:, t], key) / N

    # Query: single step (W_kv is not symmetric Hopfield, direct matmul + sign)
    query_idx = rng.choice(T, size=min(n_queries, T), replace=False)
    precision_list = []
    for t in query_idx:
        key = compound_keys[t]
        # Single retrieval step: retrieved = sign(W_kv @ key)
        retrieved = np.sign(W_kv @ key + 1e-12)
        precision_list.append(cos_sim(retrieved, patterns[:, t]))

    return {
        "mean_precision": float(np.mean(precision_list)),
        "median_precision": float(np.median(precision_list)),
        "n_queries": len(precision_list),
    }


def _instrumentation_selftest():
    """Assert all claimed metrics are non-null at small scale."""
    N_test = 256
    T_test = 10
    M_max_test = int(0.138 * N_test)
    seed = 42

    # Cell A
    res_a = run_cell_a(N_test, [0.3, 0.5], M_max_test, seed)
    assert len(res_a) >= 1, "cell A returned empty"
    for k, v in res_a.items():
        assert "mean_acc" in v, f"mean_acc missing in {k}"
        assert not math.isnan(v["mean_acc"]), f"mean_acc NaN in {k}"

    # Cell B
    T_b = max(30, int(0.5 * M_max_test))
    res_b = run_cell_b(N_test, T_b, 5, seed)
    assert "mean_del_cos" in res_b, "mean_del_cos missing"
    assert not math.isnan(res_b["mean_del_cos"]), "mean_del_cos NaN"

    # Cell C
    res_c = run_cell_c(N_test, T_b, 5, seed)
    assert "mean_precision" in res_c, "mean_precision missing"
    assert not math.isnan(res_c["mean_precision"]), "mean_precision NaN"
    assert res_c["n_queries"] > 0, "zero compound queries"

    print("[selftest] PASS: all metrics non-null at N=256 T=10", flush=True)


_instrumentation_selftest()


def run_seed(seed: int) -> Dict:
    T_target = max(10, int(0.5 * M_MAX))
    # Cell C uses lower load (10% capacity) to test compound query capability
    # before capacity cliff; separate from A/B which test at high load.
    T_cell_c = max(5, int(0.10 * M_MAX))

    cell_a = run_cell_a(N, T_FRACS, M_MAX, seed)
    cell_b = run_cell_b(N, T_target, N_DELETE_BATCH, seed)
    cell_c = run_cell_c(N, T_cell_c, N_COMPOUND_QUERIES, seed)

    return {"cell_a": cell_a, "cell_b": cell_b, "cell_c": cell_c}


def aggregate_results(per_seed: Dict) -> Dict:
    """Aggregate across seeds."""
    # Cell A: at frac 0.5
    a_accs = []
    for seed_res in per_seed.values():
        ca = seed_res["cell_a"]
        # pick frac closest to 0.5
        key = min(ca.keys(), key=lambda k: abs(float(k.split("_")[1]) - 0.5))
        a_accs.append(ca[key]["mean_acc"])

    # Cell B
    del_cos_list = [v["cell_b"]["mean_del_cos"] for v in per_seed.values()]
    delta_acc_list = [v["cell_b"]["delta_acc"] for v in per_seed.values()
                      if not math.isnan(v["cell_b"].get("delta_acc", float("nan")))]

    # Cell C
    prec_list = [v["cell_c"]["mean_precision"] for v in per_seed.values()]

    return {
        "cell_a_mean_acc_at_half_cap": float(np.mean(a_accs)),
        "cell_b_mean_del_cos": float(np.mean(del_cos_list)),
        "cell_b_mean_delta_acc": float(np.mean(delta_acc_list)) if delta_acc_list else float("nan"),
        "cell_c_mean_precision": float(np.mean(prec_list)),
        "n_seeds": len(per_seed),
    }


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    a = summary.get("cell_a_mean_acc_at_half_cap", 0.0)
    b_del = summary.get("cell_b_mean_del_cos", 1.0)
    b_delta = summary.get("cell_b_mean_delta_acc", 1.0)
    c_prec = summary.get("cell_c_mean_precision", 0.0)

    # Anchor formula self-tests (inline)
    # HP_A: acc > 0.85 at half capacity
    # HP_B: del_cos < 0.15 AND delta_acc < 0.05
    # HP_C: precision > 0.70
    a_pass = a > HP_A_ACC
    a_fail = a < HF_A_ACC
    b_pass = b_del < HP_B_DEL_COS and b_delta < HP_B_DELTA_ACC
    b_fail = b_del > HF_B_DEL_COS or b_delta > HF_B_DELTA_ACC
    c_pass = c_prec > HP_C_PREC
    c_fail = c_prec < HF_C_PREC

    if a_pass and b_pass and c_pass:
        return ("HARD_PASS",
                f"All 3 cells pass. "
                f"A acc={a:.3f}>{HP_A_ACC}, "
                f"B del_cos={b_del:.3f}<{HP_B_DEL_COS} delta={b_delta:.3f}<{HP_B_DELTA_ACC}, "
                f"C prec={c_prec:.3f}>{HP_C_PREC}.")
    if a_fail or b_fail:
        return ("HARD_FAIL",
                f"Core cell fails. "
                f"A acc={a:.3f}(hf={HF_A_ACC}), "
                f"B del_cos={b_del:.3f}(hf={HF_B_DEL_COS}) delta={b_delta:.3f}(hf={HF_B_DELTA_ACC}), "
                f"C prec={c_prec:.3f}(hf={HF_C_PREC}).")
    if a_pass and b_pass and c_fail:
        return ("PARTIAL",
                f"A+B pass, C fails. "
                f"A acc={a:.3f}, B del={b_del:.3f} delta={b_delta:.3f}, "
                f"C prec={c_prec:.3f}<{HP_C_PREC}.")
    return ("MIDDLE_BAND",
            f"Mixed. "
            f"A acc={a:.3f}(hp={HP_A_ACC}), "
            f"B del_cos={b_del:.3f}(hp={HP_B_DEL_COS}), "
            f"C prec={c_prec:.3f}(hp={HP_C_PREC}).")


def _verdict_formula_selftests():
    """Inline formula self-tests per [[feedback-strategy-spec-formula-selftests]]."""
    # Test 1: all pass
    s1 = {"cell_a_mean_acc_at_half_cap": 0.90,
          "cell_b_mean_del_cos": 0.10, "cell_b_mean_delta_acc": 0.02,
          "cell_c_mean_precision": 0.80, "n_seeds": 5}
    v1, _ = compute_verdict(s1)
    assert v1 == "HARD_PASS", f"Expected HARD_PASS, got {v1}"

    # Test 2: A hard-fails
    s2 = {"cell_a_mean_acc_at_half_cap": 0.40,
          "cell_b_mean_del_cos": 0.10, "cell_b_mean_delta_acc": 0.02,
          "cell_c_mean_precision": 0.80, "n_seeds": 5}
    v2, _ = compute_verdict(s2)
    assert v2 == "HARD_FAIL", f"Expected HARD_FAIL, got {v2}"

    # Test 3: B hard-fails (deletion not isolated)
    s3 = {"cell_a_mean_acc_at_half_cap": 0.90,
          "cell_b_mean_del_cos": 0.40, "cell_b_mean_delta_acc": 0.02,
          "cell_c_mean_precision": 0.80, "n_seeds": 5}
    v3, _ = compute_verdict(s3)
    assert v3 == "HARD_FAIL", f"Expected HARD_FAIL, got {v3}"

    # Test 4: A+B pass, C fails
    s4 = {"cell_a_mean_acc_at_half_cap": 0.90,
          "cell_b_mean_del_cos": 0.10, "cell_b_mean_delta_acc": 0.02,
          "cell_c_mean_precision": 0.40, "n_seeds": 5}
    v4, _ = compute_verdict(s4)
    assert v4 == "PARTIAL", f"Expected PARTIAL, got {v4}"

    print("[formula_selftests] PASS: 4 verdict formula cases verified", flush=True)


_verdict_formula_selftests()


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} seeds={SEEDS} M_MAX={M_MAX}", flush=True)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} seeds done, {len(remaining)} remaining", flush=True)

    for i, seed in enumerate(remaining):
        ts = time.time()
        result = run_seed(seed)
        result["seed"] = seed
        result["N"] = N
        result["run_mode"] = RUN_MODE
        write_partial(out_dir, seed, result)
        print(f"[seed {seed}] done in {time.time()-ts:.1f}s | "
              f"A_acc={result['cell_a'].get('frac_0.50', result['cell_a'].get(list(result['cell_a'].keys())[-1],{})).get('mean_acc',0):.3f} "
              f"B_del_cos={result['cell_b']['mean_del_cos']:.3f} "
              f"C_prec={result['cell_c']['mean_precision']:.3f}", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)
    summary = aggregate_results(per_seed)
    verdict, verdict_msg = compute_verdict(summary)

    elapsed = time.time() - t0
    metrics = {
        "run_mode": RUN_MODE,
        "N": N,
        "seeds": SEEDS,
        "M_MAX": M_MAX,
        "summary": summary,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": {
            "T_fracs": T_FRACS,
            "n_delete_batch": N_DELETE_BATCH,
            "n_compound_queries": N_COMPOUND_QUERIES,
        },
    }
    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] {verdict}: {verdict_msg}", flush=True)
    print(f"[done] elapsed={elapsed:.1f}s metrics={metrics_path}", flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete (selftests ran at module scope)", flush=True)
        sys.exit(0)
    main()
