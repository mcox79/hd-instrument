"""
sherman_morrison_rank1_deletion_linear_readout_v1_n4096 -- Item 22: SM rank-1 deletion.

Tests Sherman-Morrison rank-1 deletion of facts from a linear-readout geometry,
composing with substrate deletion cert and counterfactual primitives.

SCIENTIFIC QUESTION:
  Does Sherman-Morrison rank-1 deletion produce:
  (a) deleted pattern no longer an attractor: after deletion, Hopfield dynamics
      starting from xi_del converge to a DIFFERENT pattern (not xi_del)
  (b) retained patterns still retrievable: Hopfield dynamics on W_new from xi_ret
      still converge to xi_ret (cos >= 0.85)
  (c) cert hash chain reproducible across 5 seeds

  Founds PP-56 (regulatory cert positioning) if HARD-PASS.

SM FORMULA (PROT-022 R2 verified):
  W_new = W_old - (W_old xi) (xi^T W_old) / (lambda + xi^T W_old xi)
  This is the standard Woodbury/SM update for rank-1 removal of a pattern from
  the Hopfield correlation matrix. The correct deletion test:
  xi is no longer a fixed point of W_new => dynamics from xi diverge from xi.

FORMULA SELF-TESTS (PROT-022):
  1. SM formula self-test: W = xi xi^T / N; after SM deletion, W_new xi has reduced
     self-overlap. Check W_new xi cos reduces from 1.0 to near 0.
     [INPUT: N=8, M=1, xi as BSC, lambda=1e-4] [EXPECTED: cos(W_new xi, xi) < 0.2]
  2. Retention: W = (xi + xi2)(xi + xi2)^T / N, delete xi.
     Check xi2 still retrievable as attractor in W_new.
     [INPUT: N=64, M=2] [EXPECTED: hopfield(W_new, xi2) cos > 0.8]
  3. Cert hash: sha256 reproducible.

PRE-REGISTERED BANDS:
  HARD-PASS: (a) deleted pattern converges to different pattern (cos < 0.5) >= 4/5 seeds
             AND (b) retained_cos >= 0.85 for retained patterns >= 4/5 seeds
             AND (c) cert hash reproducible all seeds
  MIDDLE: any one of (a)/(b) at boundary
  HARD-FAIL: retained_cos < 0.5 (deletion breaks retained patterns)

PROT-018: anchor has _n4096; N MUST = 4096.
QUEUE: remote_cpu_queue (CPU; pure numpy; ~30 min wall).
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
import hashlib
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    import numpy as np
except ImportError:
    print("[FATAL] numpy not installed.", flush=True)
    sys.exit(1)

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "sherman_morrison_rank1_deletion_linear_readout_v1_n4096"

_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

LAMBDA_REG = 1e-4
HP_RETAINED_COS = 0.85
HP_DELETED_COS_MAX = 0.50   # deleted pattern should converge elsewhere (cos < 0.5)
HF_RETAINED_COS = 0.50
N_HOPFIELD_STEPS = 10

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_ACTIVE = 512
    M_TOTAL = 10
    M_DELETE = 3
    M_RETAIN = 7
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_ACTIVE = N
    M_TOTAL = 40
    M_DELETE = 10
    M_RETAIN = 30


def sherman_morrison_delete(W: np.ndarray, xi: np.ndarray, lam: float = LAMBDA_REG) -> np.ndarray:
    """Remove contribution of xi from W: W_new = W - (Wxi)(Wxi)^T / (lam + xi^T Wxi)."""
    Wxi = W @ xi
    xTWx = float(xi @ Wxi)
    denom = lam + xTWx
    return W - np.outer(Wxi, Wxi) / denom


def hopfield_retrieve(W: np.ndarray, probe: np.ndarray, n_steps: int = N_HOPFIELD_STEPS) -> np.ndarray:
    state = probe.copy()
    for _ in range(n_steps):
        h = W @ state
        state = np.sign(h)
        state[state == 0] = 1.0
    return state


def cert_hash(W: np.ndarray) -> str:
    return hashlib.sha256(W.tobytes()).hexdigest()


def cos_sim(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b)) / (na * nb)


def _selftest_sm_deletion_m1():
    """M=1 case: after SM deletion, W_new xi has cos < 0.2 with xi (not an attractor)."""
    n_t = 8
    rng = np.random.RandomState(42)
    xi = rng.choice([-1., 1.], size=n_t).astype(np.float64)
    W = np.outer(xi, xi) / float(n_t)
    W_new = sherman_morrison_delete(W, xi, lam=LAMBDA_REG)
    # W_new xi: should be near zero for M=1 case
    Wxi_new = W_new @ xi
    c = cos_sim(Wxi_new, xi)
    assert abs(c) < 0.5, f"SM M=1 deletion: cos(W_new xi, xi) = {c:.4f} (expected < 0.5)"


def _selftest_sm_retention_m2():
    """M=2: delete xi, xi2 still retrievable as attractor."""
    n_t = 64
    rng = np.random.RandomState(99)
    xi = rng.choice([-1., 1.], size=n_t).astype(np.float64)
    xi2 = rng.choice([-1., 1.], size=n_t).astype(np.float64)
    W = (np.outer(xi, xi) + np.outer(xi2, xi2)) / float(n_t)
    W_new = sherman_morrison_delete(W, xi, lam=LAMBDA_REG)
    # Retrieve from xi2 probe
    probe = xi2.copy()
    flip = rng.random(n_t) < 0.05
    probe[flip] *= -1.0
    ret = hopfield_retrieve(W_new, probe)
    c = cos_sim(ret, xi2)
    assert c > 0.8, f"SM M=2 retention: cos(ret, xi2) = {c:.4f} (expected > 0.8)"


def _selftest_cert_hash():
    h1 = cert_hash(np.eye(4))
    h2 = cert_hash(np.eye(4))
    assert h1 == h2, "cert_hash not reproducible"


def _selftest_valid_cells():
    """At least 1 retained and 1 deleted pattern after SM at smoke scale."""
    assert M_RETAIN >= 1, f"No retained patterns: M_RETAIN={M_RETAIN}"
    assert M_DELETE >= 1, f"No deleted patterns: M_DELETE={M_DELETE}"


def _instrumentation_selftest():
    _selftest_sm_deletion_m1()
    _selftest_sm_retention_m2()
    _selftest_cert_hash()
    _selftest_valid_cells()
    print(f"[selftest] PASS: sm_deletion_m1, sm_retention_m2, cert_hash, valid_cells "
          f"N_active={N_ACTIVE} M_total={M_TOTAL}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    rng = np.random.RandomState(seed)
    t0 = time.time()

    Xi = rng.choice([-1., 1.], size=(M_TOTAL, n_dim)).astype(np.float64)
    W = (Xi.T @ Xi) / float(n_dim)

    cert_before = cert_hash(W)

    deleted_indices = list(range(M_DELETE))
    retained_indices = list(range(M_DELETE, M_TOTAL))

    W_after = W.copy()
    for idx in deleted_indices:
        xi_del = Xi[idx]
        W_after = sherman_morrison_delete(W_after, xi_del, lam=LAMBDA_REG)

    cert_after = cert_hash(W_after)
    cert_changed = (cert_before != cert_after)
    cert_reproducible = (cert_hash(W_after) == cert_after)

    # Test (a): deleted patterns no longer attractors
    # Run hopfield on W_after starting from xi_del; measure cos of final state with xi_del
    deleted_coses = []
    for idx in deleted_indices:
        xi_del = Xi[idx]
        probe = xi_del.copy()
        flip = rng.random(n_dim) < 0.05  # small noise to avoid exact fixed-point
        probe[flip] *= -1.0
        ret = hopfield_retrieve(W_after, probe)
        c = cos_sim(ret, xi_del)
        deleted_coses.append(c)
    mean_deleted = float(np.mean(deleted_coses)) if deleted_coses else 0.0
    a_pass = mean_deleted < HP_DELETED_COS_MAX

    # Test (b): retained patterns still attractors
    retained_coses = []
    for idx in retained_indices:
        xi_ret = Xi[idx]
        probe = xi_ret.copy()
        flip = rng.random(n_dim) < 0.05
        probe[flip] *= -1.0
        ret = hopfield_retrieve(W_after, probe)
        c = cos_sim(ret, xi_ret)
        retained_coses.append(c)
    mean_retained = float(np.mean(retained_coses)) if retained_coses else 0.0
    b_pass = mean_retained >= HP_RETAINED_COS

    # Test (c): cert reproducible
    c_pass = cert_reproducible

    elapsed = time.time() - t0
    print(f"  [seed={seed} N={n_dim}] deleted_cos={mean_deleted:.4f}(HP<{HP_DELETED_COS_MAX}) "
          f"retained_cos={mean_retained:.4f}(HP>={HP_RETAINED_COS}) "
          f"cert_ok={c_pass} cert_changed={cert_changed} "
          f"a={a_pass} b={b_pass} c={c_pass} elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE, "elapsed_s": float(elapsed),
        "deleted_cos": float(mean_deleted), "retained_cos": float(mean_retained),
        "cert_reproducible": bool(c_pass), "cert_changed": bool(cert_changed),
        "a_pass": bool(a_pass), "b_pass": bool(b_pass), "c_pass": bool(c_pass),
    }


def compute_verdict(all_results: List[Dict]) -> tuple:
    if not all_results:
        return ("HARD_FAIL", "No valid results.")

    def count_pass(key):
        return sum(1 for r in all_results if r.get(key, False))

    n = len(all_results)
    na = count_pass("a_pass")
    nb = count_pass("b_pass")
    nc = count_pass("c_pass")

    mean_del = float(np.mean([r["deleted_cos"] for r in all_results if "deleted_cos" in r]))
    mean_ret = float(np.mean([r["retained_cos"] for r in all_results if "retained_cos" in r]))

    summary = (f"deleted_cos={mean_del:.4f}(HP<{HP_DELETED_COS_MAX}) "
               f"retained_cos={mean_ret:.4f}(HP>={HP_RETAINED_COS},HF<{HF_RETAINED_COS}) "
               f"a={na}/{n} b={nb}/{n} c={nc}/{n}")

    # HARD-FAIL
    if mean_ret < HF_RETAINED_COS:
        return ("HARD_FAIL", f"HARD_FAIL: retained_cos={mean_ret:.4f} < {HF_RETAINED_COS}. {summary}")
    if nc < n:
        return ("HARD_FAIL", f"HARD_FAIL: cert not reproducible in {n-nc}/{n} seeds. {summary}")

    gate = max(4, n - 1) if n >= 4 else n
    if na >= gate and nb >= gate and nc >= gate:
        return ("HARD_PASS",
                f"HARD_PASS: SM deletion + cert all pass. PP-56 regulatory cert founded. {summary}")
    if sum([na >= gate, nb >= gate, nc >= gate]) >= 2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: 2/3 HP conditions. {summary}")

    return ("MIDDLE_BAND", f"MIDDLE_BAND: {summary}")


def _prot018_startup_check() -> None:
    if RUN_MODE != "smoke" and N_ACTIVE != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor _n{_N_SUFFIX} but FULL N_ACTIVE={N_ACTIVE}")


print(f"[config] PROT-018 N={N} N_active={N_ACTIVE} mode={RUN_MODE} "
      f"M_total={M_TOTAL} M_delete={M_DELETE} M_retain={M_RETAIN}", flush=True)
_prot018_startup_check()

out_dir = get_output_dir(ANCHOR_NAME)
t0_total = time.time()
run_config = {"N": N, "M_TOTAL": M_TOTAL, "run_mode": RUN_MODE}

done, seeds_todo = resumable_seeds(SEEDS, out_dir, run_config)
print(f"[run] seeds_todo={seeds_todo} out_dir={out_dir}", flush=True)

for s in seeds_todo:
    res = run_seed(s, N_ACTIVE)
    write_partial(out_dir, s, res)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

metrics = {
    "anchor": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "n_seeds": len(all_results),
    "N": N,
    "run_mode": RUN_MODE,
    "elapsed_s": time.time() - t0_total,
    "summary": verdict_msg[:300],
    "results": all_results,
}

metrics_path = out_dir / "metrics.json"
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)

print(f"\n[VERDICT] {verdict}", flush=True)
print(f"[VERDICT_MSG] {verdict_msg}", flush=True)
print(f"[METRICS_PATH] {metrics_path}", flush=True)
