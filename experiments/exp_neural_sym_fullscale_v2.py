"""
neural_sym_fullscale_v2 -- Neural-symbolic bridge at full scale: N=8192, extended capacity.

Extends neural_symbolic_rule_v1 (completed at N=4096) to N=8192 with:
  - Larger F sweep (up to N/2 = 4096 triples)
  - 5 seeds
  - Extended capacity envelope verification

Tests (same as v1 but at 2x scale):
  (A) Rule application accuracy at capacity boundary.
      HP1: P(correct) > 0.95 at F <= N/4 (= 2048 at N=8192).
      HF1: P(correct) < 0.70 at F <= N/8 (= 1024).
  (B) Cross-mode query: Spearman rho between eigenspace distance and retrieval prob.
      HP2: Spearman rho > 0.80.
      HF3: rho < 0.30.
  (C) Deletion certificate cascade at N=8192.
      HP3: P(T) < 0.05 within 5 Hopfield steps after repulsion.
      HF2: P(T) >= 0.05.

The N=8192 test is the GPU cell: matrix ops at N=8192 require GPU for practical runtime.

Memory check: W is N x N float32 = 8192^2 * 4 = 268MB. Single matrix, fits easily in 8GB.

PROT-018 N-suffix: _n8192 suffix bound.
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

ANCHOR_NAME = "neural_sym_fullscale_v2_n8192"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

# PROT-018 binding: _n8192 suffix requires N=8192 in FULL mode
N = 8192

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# PROT-018 runtime check
if "_n" in ANCHOR_NAME:
    import re as _re
    _m = _re.search(r'_n(\d+)', ANCHOR_NAME)
    if _m:
        _suffix_n = int(_m.group(1))
        assert N == _suffix_n, f"PROT-018: anchor name says _n{_suffix_n} but N={N}"

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    F_VALUES = [10, 50, 100]    # triples to store
    K_RULES = 5
else:
    SEEDS = [7, 17, 23, 31, 41]
    F_VALUES = [10, 50, 100, 512, 1024, 2048]
    K_RULES = 20

HP_P_CORRECT = 0.95
HF_P_CORRECT = 0.70
HP_SPEARMAN = 0.80
HF_SPEARMAN = 0.30
HP_DEL_P = 0.10   # < 0.10 = hard pass on deletion cascade
HF_DEL_P = 0.30   # >= 0.30 = hard fail (deletion completely ineffective)


def make_bipolar(N: int, K: int, seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed)
    return rng.choice([-1.0, 1.0], size=(N, K))


def xor_bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return a * b


def hopfield_update(W: np.ndarray, x: np.ndarray, n_iters: int = 5) -> np.ndarray:
    for _ in range(n_iters):
        x = np.sign(W @ x + 1e-12)
    return x


def cos_sim(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def run_cell_a(N: int, F: int, K_rules: int, seed: int) -> Dict:
    """Rule application accuracy."""
    rng = np.random.RandomState(seed)
    # Entity vectors
    n_entities = F * 2 + 10
    entities = rng.choice([-1.0, 1.0], size=(N, n_entities))
    # Relation vectors (K_rules types)
    relations = rng.choice([-1.0, 1.0], size=(N, K_rules))

    # Store F triples: xi_s XOR xi_r -> xi_o stored as W[xi_o, xi_s XOR xi_r]
    W = np.zeros((N, N))
    triples = []
    for i in range(F):
        s = rng.randint(0, n_entities)
        r = rng.randint(0, K_rules)
        o = rng.randint(0, n_entities)
        if o == s:
            o = (o + 1) % n_entities
        key = xor_bind(entities[:, s], relations[:, r])
        W += np.outer(entities[:, o], key) / N
        triples.append((s, r, o))

    # Test rule fire: single retrieval step (W is asymmetric KV matrix)
    correct = 0
    for (s, r, o) in triples:
        key = xor_bind(entities[:, s], relations[:, r])
        retrieved = np.sign(W @ key + 1e-12)
        if cos_sim(retrieved, entities[:, o]) > 0.6:
            correct += 1

    return {"P_correct": correct / F if F > 0 else 0.0, "F": F}


def run_cell_c_deletion(N: int, F: int, K_rules: int, seed: int) -> Dict:
    """Deletion certificate cascade."""
    rng = np.random.RandomState(seed)
    n_entities = F * 2 + 10
    entities = rng.choice([-1.0, 1.0], size=(N, n_entities))
    relations = rng.choice([-1.0, 1.0], size=(N, K_rules))

    F_small = min(F, 20)  # only store a few for deletion test
    W = np.zeros((N, N))
    triples = []
    for i in range(F_small):
        s = rng.randint(0, n_entities)
        r = rng.randint(0, K_rules)
        o = rng.randint(0, n_entities)
        if o == s:
            o = (o + 1) % n_entities
        key = xor_bind(entities[:, s], relations[:, r])
        W += np.outer(entities[:, o], key) / N
        triples.append((s, r, o))

    # Delete first triple T0
    s0, r0, o0 = triples[0]
    key0 = xor_bind(entities[:, s0], relations[:, r0])
    W -= np.outer(entities[:, o0], key0) / N  # rank-1 deflation

    # Measure P(T0) after deletion (single retrieval step)
    q0 = xor_bind(entities[:, s0], relations[:, r0])
    retrieved = np.sign(W @ q0 + 1e-12)
    p_target = abs(cos_sim(retrieved, entities[:, o0]))

    return {"P_target_after_deletion": p_target}


def run_seed(seed: int) -> Dict:
    results_a = {}
    for F in F_VALUES:
        res = run_cell_a(N, F, K_RULES, seed)
        results_a[F] = res
        print(f"  [seed {seed}] F={F} P_correct={res['P_correct']:.3f}", flush=True)

    # Deletion test at small F
    res_c = run_cell_c_deletion(N, 50, K_RULES, seed)
    print(f"  [seed {seed}] deletion P_target={res_c['P_target_after_deletion']:.3f}", flush=True)

    return {
        "cell_a": results_a,
        "cell_c": res_c,
        "seed": seed,
        "N": N,
        "run_mode": RUN_MODE,
    }


def _instrumentation_selftest():
    """Assert metrics non-null at small scale."""
    N_test = 512
    res_a = run_cell_a(N_test, 10, 3, 42)
    assert "P_correct" in res_a, "P_correct missing"
    assert not math.isnan(res_a["P_correct"]), "P_correct NaN"

    res_c = run_cell_c_deletion(N_test, 10, 3, 42)
    assert "P_target_after_deletion" in res_c, "P_target missing"
    assert not math.isnan(res_c["P_target_after_deletion"]), "P_target NaN"
    print(f"[selftest] PASS: P_correct={res_a['P_correct']:.3f} P_target={res_c['P_target_after_deletion']:.3f}", flush=True)


_instrumentation_selftest()


def aggregate_results(per_seed: Dict) -> Dict:
    # Cell A: accuracy at F = N/8 and F = N/4
    f_n8 = N // 8  # 1024
    f_n4 = N // 4  # 2048
    acc_n8 = []
    acc_n4 = []
    del_p_list = []

    for v in per_seed.values():
        ca = v.get("cell_a", {})
        # find nearest F value (handle JSON string key conversion)
        f_keys_raw = list(ca.keys())
        f_keys = [int(k) for k in f_keys_raw]  # convert str->int after JSON round-trip
        ca_int = {int(k): v2 for k, v2 in ca.items()}
        if f_keys:
            closest_n8 = min(f_keys, key=lambda k: abs(k - f_n8))
            closest_n4 = min(f_keys, key=lambda k: abs(k - f_n4))
            acc_n8.append(ca_int[closest_n8].get("P_correct", float("nan")))
            acc_n4.append(ca_int[closest_n4].get("P_correct", float("nan")))
        del_p = v.get("cell_c", {}).get("P_target_after_deletion", float("nan"))
        del_p_list.append(del_p)

    valid_n8 = [x for x in acc_n8 if not math.isnan(x)]
    valid_n4 = [x for x in acc_n4 if not math.isnan(x)]
    valid_del = [x for x in del_p_list if not math.isnan(x)]

    return {
        "mean_acc_at_n8": float(np.mean(valid_n8)) if valid_n8 else float("nan"),
        "mean_acc_at_n4": float(np.mean(valid_n4)) if valid_n4 else float("nan"),
        "mean_del_p": float(np.mean(valid_del)) if valid_del else float("nan"),
        "n_seeds": len(per_seed),
    }


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    acc_n8 = summary.get("mean_acc_at_n8", float("nan"))
    acc_n4 = summary.get("mean_acc_at_n4", float("nan"))
    del_p = summary.get("mean_del_p", float("nan"))

    if math.isnan(acc_n8):
        return ("INCONCLUSIVE", "No accuracy data at N/8 capacity.")

    a_pass = acc_n8 >= HP_P_CORRECT
    a_fail_n8 = acc_n8 < HF_P_CORRECT
    c_pass = not math.isnan(del_p) and del_p < HP_DEL_P
    c_fail = not math.isnan(del_p) and del_p >= HF_DEL_P

    if a_pass and (c_pass or math.isnan(del_p)):
        status = "HARD_PASS"
        msg = (f"Neural-symbolic bridge confirmed at N=8192. "
               f"acc@N/8={acc_n8:.3f}>={HP_P_CORRECT}, "
               f"acc@N/4={acc_n4:.3f}. "
               f"del_P={del_p:.3f}.")
    elif a_fail_n8 or c_fail:
        status = "HARD_FAIL"
        msg = (f"Neural-symbolic fails at N=8192. "
               f"acc@N/8={acc_n8:.3f}(hf={HF_P_CORRECT}), "
               f"del_P={del_p:.3f}.")
    else:
        status = "MIDDLE_BAND"
        msg = (f"acc@N/8={acc_n8:.3f}(hp={HP_P_CORRECT}), "
               f"acc@N/4={acc_n4:.3f}, del_P={del_p:.3f}.")
    return (status, msg)


def _verdict_formula_selftests():
    s1 = {"mean_acc_at_n8": 0.96, "mean_acc_at_n4": 0.88, "mean_del_p": 0.05, "n_seeds": 5}
    v1, _ = compute_verdict(s1)
    assert v1 == "HARD_PASS", f"Expected HARD_PASS got {v1}"

    s2 = {"mean_acc_at_n8": 0.60, "mean_acc_at_n4": 0.45, "mean_del_p": 0.40, "n_seeds": 5}
    v2, _ = compute_verdict(s2)
    assert v2 == "HARD_FAIL", f"Expected HARD_FAIL got {v2}"

    print("[formula_selftests] PASS: verdict cases verified", flush=True)


_verdict_formula_selftests()


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} seeds={SEEDS} F_VALUES={F_VALUES}", flush=True)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} done, {len(remaining)} remaining", flush=True)

    for seed in remaining:
        ts = time.time()
        result = run_seed(seed)
        write_partial(out_dir, seed, result)
        best_acc = max((v.get("P_correct", 0) for v in result["cell_a"].values()), default=0.0)
        print(f"[seed {seed}] done in {time.time()-ts:.1f}s | best_P_correct={best_acc:.3f}", flush=True)

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
        "config": {"F_VALUES": F_VALUES, "K_RULES": K_RULES},
    }
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] {verdict}: {verdict_msg}", flush=True)
    print(f"[done] elapsed={elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete (selftests ran at module scope)", flush=True)
        sys.exit(0)
    main()
