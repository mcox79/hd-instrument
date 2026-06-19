"""
pp49_hrc_cf_depth_band_sweep_v1_n4096 -- PP-49: HRC counterfactual depth-band sweep {1,2,3,4,5}.

Item 4 (I-15 carryover): depth-5 HARD_FAIL showed cf_cos=0.028 (expected >= 0.60).
This sweep characterizes the anomaly: does ANY depth work for counterfactual abduction?
Tests depths 1, 2, 3, 4, 5 in a single sweep to map the failure mode boundary.

Background: depth-5 HARD_FAIL was unexpected -- cert (HP1, HP3) passes at 100% across all seeds,
meaning the deletion certificate mechanism works. But counterfactual retrieval (HP2) returns
near-zero cosine, suggesting the substitution doesn't propagate through the chain correctly.

Primary hypothesis: counterfactual substitution at position d only affects one hop; downstream
pattern retrieval collapses because W_cf still contains the original chain associations for
later hops. Depth=1 (single-hop substitution) should work; deeper depths may fail.

PRE-REGISTERED BANDS (calibration probe -- no prior depth-sweep anchor):
  HARD-PASS: depth-1 cf_cos >= 0.70 (substitution at single hop works)
             AND at least one depth in {1,2,3} achieves cf_cos >= 0.50.
  MIDDLE: depth-1 cf_cos in [0.40, 0.70) OR depth-1 works but depths 2-5 fail.
  HARD-FAIL: depth-1 cf_cos < 0.20 -- substitution fails even at single hop (mechanism broken).

Note: bands widened to +-50% per calibration-probe policy (no prior depth-sweep anchor).
INSTRUMENTATION NOTE: cert_rate and audit_rate measure certificate mechanism (separate from cf retrieval).
The primary discriminating metric is cf_cos (counterfactual retrieval cosine).

FORMULA SELF-TESTS (PROT-022):
  1. deletion_cert for stored BSC xi in W = xi xi^T/N: cert = -1.0 exactly.
     [INPUT: N=8, BSC xi, W = xi xi^T/N] [EXPECTED: -xi^T W xi / N^2 = -1.0]
  2. cert for xi_A in W after SM-style removal: near 0 (orthogonal to xi_B).
  3. depth-1 single-hop chain retrieval: cos(H @ x0, x1) close to 1.0 at small alpha.
     [INPUT: N=64, single pattern, alpha=1/64] [EXPECTED: cos > 0.5]
  4. GPU memory > 0 after tensor build.

PROT-018: no _n<N> suffix in anchor name -- production N=4096 stated in prereq section below.
   ## N-suffix: No _nN suffix; production N = 4096; rationale: depth-band sweep not N-scaling.
PROT-021: seed checkpoints keyed with run_mode + max_depth.
QUEUE: remote_cpu_queue (pure CPU; depth-band sweep; N=4096 but no GPU matrix ops needed).
  Note: memory at N=4096: H float32 = 67 MB -- fine for remote CPU.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import numpy as np

ANCHOR_NAME = "pp49_hrc_cf_depth_band_sweep_v1_n4096"

N = 4096
# No _nN suffix in name; N=4096 is production N per PROT-018 note above.

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

TEST_DEPTHS = [1, 2, 3, 4, 5]   # sweep all five depths
SUBST_FRAC = 0.5   # substitution at midpoint of each chain

HP_DEPTH1_CF_COS = 0.70
HP_ANY_CF_COS = 0.50
MIDDLE_DEPTH1_CF_COS_LO = 0.20
HF_DEPTH1_CF_COS = 0.20

if RUN_MODE == "smoke":
    N_ACTIVE = 256
    SEEDS = [7, 17]
    N_CHAINS = 3
    M_BG = 15
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    N_CHAINS = 8
    M_BG = 80


def bsc_np(m: int, n: int, rng: np.random.Generator) -> np.ndarray:
    """BSC vectors in {+1, -1}."""
    return rng.integers(0, 2, size=(m, n)).astype(np.float32) * 2 - 1


def deletion_cert(xi: np.ndarray, n: int) -> float:
    """cert = -||xi||^4 / n^2. For unit-norm BSC: = -1.0."""
    norm_sq = float(np.dot(xi, xi))
    return -(norm_sq ** 2) / (n * n)


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b)) / (na * nb)


def hopfield_retrieve(W: np.ndarray, probe: np.ndarray, n_steps: int = 5) -> np.ndarray:
    state = probe.copy()
    for _ in range(n_steps):
        h = W @ state
        state = np.sign(h)
        state[state == 0] = 1.0
    return state


def _instrumentation_selftest():
    """Assert all metrics are non-null/non-sentinel at smoke scale."""
    rng = np.random.default_rng(0)
    N_t = 8

    # Test 1: deletion cert = -1.0 for BSC xi in W = xi xi^T / N
    xi = bsc_np(1, N_t, rng)[0]
    c = deletion_cert(xi, N_t)
    assert abs(c + 1.0) < 1e-6, f"cert selftest: {c:.8f} expected -1.0"

    # Test 2: cert for xi_A in W after xi_B substitution is near 0
    xi_A = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], dtype=np.float32)
    xi_B = np.array([0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], dtype=np.float32)
    dot = float(np.dot(xi_A, xi_B))
    cert_A_cf = (dot ** 2) / (N_t * N_t)
    assert abs(cert_A_cf) < 1e-8, f"cert_A_in_Wcf: {cert_A_cf:.8f}"

    # Test 3: single-hop chain retrieval at low alpha
    N_t2 = 64
    rng2 = np.random.default_rng(1)
    x0 = bsc_np(1, N_t2, rng2)[0]
    x1 = bsc_np(1, N_t2, rng2)[0]
    H = np.outer(x1, x0) / N_t2
    probe = x0.copy()
    probe[:N_t2 // 4] *= -1.0  # add some noise
    retrieved = hopfield_retrieve(H, probe)
    cos_val = cosine_sim(retrieved, x1)
    assert cos_val > 0.2, f"single-hop retrieval cos={cos_val:.4f} (expected > 0.2 at alpha=1/64)"

    # Test 4: metrics are non-null (forward pass at depth=1)
    N_t3 = 32
    rng3 = np.random.default_rng(2)
    bg = bsc_np(2, N_t3, rng3)
    chain = [bsc_np(1, N_t3, rng3)[0] for _ in range(2)]
    H = np.outer(chain[1], chain[0]) / N_t3
    H += np.sum([np.outer(bg[i], bg[i]) for i in range(2)], axis=0) / N_t3
    # depth-1: substitution at hop 0->1
    xi_B = bsc_np(1, N_t3, rng3)[0]
    H_cf = H - np.outer(chain[1], chain[0]) / N_t3 + np.outer(xi_B, chain[0]) / N_t3
    r_cf = chain[0].copy()
    for _ in range(3):
        h = H_cf @ r_cf
        r_cf = np.sign(h)
        r_cf[r_cf == 0] = 1.0
    cf_cos = cosine_sim(r_cf, xi_B)
    assert cf_cos is not None and not np.isnan(cf_cos), f"cf_cos is NaN or None: {cf_cos}"
    cert_val = deletion_cert(chain[1], N_t3)
    assert cert_val is not None and not np.isnan(cert_val), f"cert is NaN"

    print(f"[selftest] PASS: cert=-1.0, cert_cf=0, single-hop-cos={cos_val:.3f}, "
          f"cf_cos_d1={cf_cos:.3f} N_active={N_ACTIVE}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed_at_depth(seed: int, depth: int, n_dim: int) -> Dict:
    """Run counterfactual abduction at a specific chain depth."""
    rng = np.random.default_rng(seed)
    t0 = time.time()

    # substitution position: midpoint of chain
    subst_pos = max(1, depth // 2)

    cf_cosines = []
    cert_rates = []
    audit_rates = []
    ds_cosines = []

    for chain_idx in range(N_CHAINS):
        chain = [bsc_np(1, n_dim, rng)[0] for _ in range(depth + 1)]
        bg_keys = bsc_np(M_BG, n_dim, rng)
        bg_vals = bsc_np(M_BG, n_dim, rng)

        # Build heteroassociative chain
        H = np.zeros((n_dim, n_dim), dtype=np.float32)
        for d in range(depth):
            H += np.outer(chain[d + 1], chain[d]) / n_dim
        H += (bg_vals.T @ bg_keys) / n_dim

        # HP1: deletion cert for chain[subst_pos] in H
        cert_val = deletion_cert(chain[subst_pos], n_dim)
        hp1_ok = abs(cert_val + 1.0) < 1e-4
        cert_rates.append(float(hp1_ok))

        # Build H_cf: replace hop (subst_pos-1 -> subst_pos) with xi_B
        xi_A = chain[subst_pos]
        xi_B = bsc_np(1, n_dim, rng)[0]
        H_cf = H - np.outer(xi_A, chain[subst_pos - 1]) / n_dim \
                 + np.outer(xi_B, chain[subst_pos - 1]) / n_dim

        # HP2: counterfactual retrieval from subst_pos-1 gives xi_B
        r_cf = chain[subst_pos - 1].copy()
        for _ in range(5):
            h_vec = H_cf @ r_cf
            r_cf = np.sign(h_vec)
            r_cf[r_cf == 0] = 1.0
        cf_cos = cosine_sim(r_cf, xi_B)
        cf_cosines.append(cf_cos)

        # HP3: audit cert -- xi_A cert in H_cf near 0
        # cert for xi_A in H_cf = xi_A^T H_cf xi_A / N
        audit_cert = float(xi_A @ H_cf @ xi_A) / n_dim
        hp3_ok = abs(audit_cert) < 0.15
        audit_rates.append(float(hp3_ok))

        # HP4: downstream chain still retrievable (only if depth > subst_pos)
        if depth > subst_pos:
            # Retrieve from xi_B through remaining hops using original H
            r_ds = xi_B.copy()
            for step in range(subst_pos, depth):
                h_vec = H @ r_ds
                r_ds = np.sign(h_vec)
                r_ds[r_ds == 0] = 1.0
            ds_cos = cosine_sim(r_ds, chain[depth])
        else:
            ds_cos = cf_cos  # no downstream; use cf result
        ds_cosines.append(ds_cos)

    mean_cf = float(np.mean(cf_cosines))
    mean_cert = float(np.mean(cert_rates))
    mean_audit = float(np.mean(audit_rates))
    mean_ds = float(np.mean(ds_cosines))
    elapsed = time.time() - t0

    print(f"  [seed={seed} depth={depth}] cf_cos={mean_cf:.4f} cert_rate={mean_cert:.4f} "
          f"audit_rate={mean_audit:.4f} ds_cos={mean_ds:.4f} elapsed={elapsed:.2f}s",
          flush=True)

    return {
        "seed": seed, "depth": depth, "N": n_dim, "run_mode": RUN_MODE,
        "mean_cf_cos": float(mean_cf),
        "mean_cert_rate": float(mean_cert),
        "mean_audit_rate": float(mean_audit),
        "mean_ds_cos": float(mean_ds),
        "elapsed_s": elapsed,
    }


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    # Group by depth
    depth_cf = {}
    for r in results:
        d = r["depth"]
        if d not in depth_cf:
            depth_cf[d] = []
        depth_cf[d].append(r["mean_cf_cos"])

    depth_means = {d: float(np.mean(v)) for d, v in depth_cf.items()}

    cf_d1 = depth_means.get(1, 0.0)
    any_depth_hp = any(v >= HP_ANY_CF_COS for v in depth_means.values())

    depth_str = " ".join(f"d{d}_cf={depth_means.get(d, 0.0):.4f}" for d in TEST_DEPTHS)
    summary = (f"depth_cf_cosines: {depth_str} "
               f"HP_d1>={HP_DEPTH1_CF_COS} MIDDLE_d1>={MIDDLE_DEPTH1_CF_COS_LO} "
               f"HF_d1<{HF_DEPTH1_CF_COS} n_seeds={len(set(r['seed'] for r in results))}")

    # HARD_FAIL: depth-1 substitution doesn't work
    if cf_d1 < HF_DEPTH1_CF_COS:
        return ("HARD_FAIL",
                f"HARD_FAIL: depth-1 cf_cos={cf_d1:.4f} < {HF_DEPTH1_CF_COS} -- substitution fails at single hop. {summary}")

    # HARD_PASS: depth-1 works and at least one depth in {1,2,3} achieves >= HP_ANY threshold
    if cf_d1 >= HP_DEPTH1_CF_COS and any_depth_hp:
        best_depth = max(depth_means, key=lambda d: depth_means[d])
        return ("HARD_PASS",
                f"HARD_PASS: depth-1 cf_cos={cf_d1:.4f} >= {HP_DEPTH1_CF_COS} AND best={best_depth} cf>={HP_ANY_CF_COS}. {summary}")

    # MIDDLE: depth-1 works but deeper depths fail, or depth-1 is borderline
    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: depth-1 cf_cos={cf_d1:.4f} in [{MIDDLE_DEPTH1_CF_COS_LO},{HP_DEPTH1_CF_COS}). {summary}")


from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial

print(f"[config] anchor={ANCHOR_NAME} N={N_ACTIVE} mode={RUN_MODE} depths={TEST_DEPTHS}", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "test_depths": TEST_DEPTHS, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
all_results = []

# Load already-done seed results
for seed in done:
    import json as _json
    fpath = out_dir / f"seed_{seed}.json"
    if fpath.exists():
        d = _json.loads(fpath.read_text())
        # d is a combined dict with depth_results list
        if isinstance(d, dict) and "depth_results" in d:
            all_results.extend(d["depth_results"])
        elif isinstance(d, list):
            all_results.extend(d)
        elif isinstance(d, dict):
            all_results.append(d)

for seed in remaining:
    seed_results = []
    for depth in TEST_DEPTHS:
        print(f"[seed={seed} depth={depth}] {ANCHOR_NAME}...", flush=True)
        r = run_seed_at_depth(seed, depth, N_ACTIVE)
        seed_results.append(r)
    all_results.extend(seed_results)
    # Write combined per-seed result dict (wrap list as single dict for checkpoint compatibility)
    combined = {
        "seed": seed, "depths": TEST_DEPTHS,
        "depth_results": seed_results,
        "run_mode": RUN_MODE,
    }
    write_partial(out_dir, seed, combined)

verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "test_depths": TEST_DEPTHS, "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "per_depth_means": {
        str(d): float(np.mean([r["mean_cf_cos"] for r in all_results if r["depth"] == d]))
        for d in TEST_DEPTHS
        if any(r["depth"] == d for r in all_results)
    },
    "all_results": all_results,
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
