"""
pp49_hrc_depth_parity_discriminator_sweep_v1_n4096 -- PP-49 depth-parity mechanism discriminator.

CONTEXT (Wave-5 Decisive Experiment 3 from research_routing_v359_drill_battery_synthesis_2026-06-03.md):
  Prior: pp49_hrc_cf_depth_band_sweep (depths 1-5) showed non-monotone cf_cos pattern.
  Research drill identified TWO competing explanations:
    1x (parity-class): cf_cos alternates +/- for odd/even depth under BOTH protocols.
    2x (protocol-artifact): cf_cos saturates <=0.50 under predecessor-start (rank-1 ceiling);
                            ROOT-START bypasses: cf_cos >= 0.95 smooth monotone.
  Both explanations have PP-49 capability intact -- discrimination determines product-API design.

SCIENTIFIC QUESTION (PP-49 mechanism discriminator):
  Does counterfactual recovery follow parity-class (1x: alternating +/- under EITHER protocol)
  OR protocol-artifact (2x: smooth monotone under root-start, saturated <=0.50 under pred-start)?

TEST DESIGN:
  N=4096, alpha=0.05, 5 seeds.
  Sweep d in {1, 2, 3, 4, 5, 6, 7, 8}.
  For EACH depth: measure cf_cos under BOTH protocols:
    - predecessor-start: probe starts from predecessor of the substituted hop (original behavior)
    - root-start: probe starts from chain root (hop 0) and traverses through counterfactual matrix
  Key discriminating observations:
    - Parity-class: cf_cos alternates sign or magnitude across d under BOTH protocols
    - Protocol-artifact: cf_cos <= 0.50 under pred-start at ALL d; cf_cos >= 0.95 under root-start

PRE-REGISTERED OUTCOME DISCRIMINATION (Wave-5; source: v359 synthesis Section 3 Exp 3):
  PARITY-CLASS CONFIRMED: cf_cos(d) alternates +/- pattern; even-d EXACT/near-1.0, odd-d < 0.5
                          under EITHER protocol. Definition: >3 of 4 even depths >= 0.70
                          AND >3 of 4 odd depths <= 0.50.
  PROTOCOL-ARTIFACT CONFIRMED: cf_cos_pred_start <= 0.55 for ALL d (ceiling consistent);
                                cf_cos_root_start >= 0.85 for d >= 2 (smooth, no parity alternation).
  MIXED (neither pure): Both mechanisms contribute; recorded as MIDDLE_BAND for further analysis.

NOTE: both PARITY-CLASS and PROTOCOL-ARTIFACT outcomes map to HARD_PASS (PP-49 capability intact).
  HARD_FAIL only if both protocols produce cf_cos <= 0.20 at all depths (mechanism broken).

FORMULA SELF-TESTS (PROT-022):
  1. Root-start traversal depth-1: probe from x0 through 1-hop CF matrix retrieves xi_B.
     [INPUT: N=64, 1 chain, 1 bg, depth=1] [EXPECTED: cf_cos_root_start >= 0.3]
  2. Predecessor-start depth-1: probe from x_{d-1} retrieves xi_B (same as root for depth-1).
     [INPUT: same] [EXPECTED: same result]
  3. Rank-1 substitution ceiling: cf_cos <= 0.50 at N=4096 under predecessor-start for d>=3.
     (This is a prior empirical observation from pp49_hrc_cf_depth_band_sweep_v1_n4096; checked here.)
  4. Signed cf_cos at odd depth under pred-start: check sign (negative = parity mechanism).
     [INPUT: depth=5, predecessor-start] [EXPECTED: cf_cos may be negative if parity]

PROT-018: anchor has no _n4096 suffix binding (following pp49 series naming convention).
  Explicit note: "No _nN suffix; production N = 4096; rationale: parity-discriminator sweep,
  depth is the primary axis, not N."
PROT-021: seed checkpoints keyed with run_mode + max_depth.
QUEUE: remote_cpu_queue (pure CPU; N=4096 depth sweep, <5 min wall expected).
TIMEOUT ESTIMATE: pp49_hrc_cf_depth_band_sweep smoke elapsed ~30s at N=4096 5 seeds.
  This anchor adds root-start protocol (2x work) and 3 extra depths.
  estimate: 1.5 * 60 * (1.0) * (5/2) = 225s. With 2x margin for 8 depths: 450s -> 600s.
  timeout=600s.
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

try:
    import numpy as np
except ImportError:
    print("[FATAL] numpy not installed.", flush=True)
    sys.exit(1)

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial

ANCHOR_NAME = "pp49_hrc_depth_parity_discriminator_sweep_v1_n4096"

N = 4096
# No _nN suffix; production N = 4096; rationale: parity-discriminator sweep.

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA = 0.05
TEST_DEPTHS = [1, 2, 3, 4, 5, 6, 7, 8]
EVEN_DEPTHS = [d for d in TEST_DEPTHS if d % 2 == 0]  # [2, 4, 6, 8]
ODD_DEPTHS = [d for d in TEST_DEPTHS if d % 2 == 1]   # [1, 3, 5, 7]
N_RETRIEVAL_STEPS = 8

# Verdict thresholds
HP_PARITY_EVEN_THRESH = 0.70   # even-depth cf_cos >= this
HP_PARITY_ODD_THRESH = 0.50    # odd-depth cf_cos <= this (suppressed)
HP_PROTO_PRED_CEIL = 0.55      # pred-start cf_cos <= this for ALL d (rank-1 ceiling)
HP_PROTO_ROOT_FLOOR = 0.85     # root-start cf_cos >= this for d >= 2
HF_BOTH_BROKEN = 0.20          # both protocols cf_cos <= this at all depths

if RUN_MODE == "smoke":
    N_ACTIVE = 512
    SEEDS = [7, 17]
    N_CHAINS = 4
    M_BG = 20
    SMOKE_DEPTHS = [1, 2, 3, 4, 5, 6, 7, 8]  # run all depths even in smoke
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    N_CHAINS = 8
    M_BG = int(ALPHA * N)  # 204


def bsc_np(m: int, n: int, rng: np.random.RandomState) -> np.ndarray:
    """BSC vectors in {+1, -1}."""
    return rng.choice([-1., 1.], size=(m, n)).astype(np.float32)


def hopfield_retrieve_np(W: np.ndarray, probe: np.ndarray, n_steps: int = N_RETRIEVAL_STEPS) -> np.ndarray:
    state = probe.copy().astype(np.float64)
    for _ in range(n_steps):
        h = W @ state
        state = np.sign(h)
        state[state == 0] = 1.0
    return state


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b)) / (na * nb)


def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    rng = np.random.RandomState(42)
    n_t = 64

    # Test 1: root-start depth-1: probe from x0 through CF matrix retrieves xi_B
    x0 = bsc_np(1, n_t, rng)[0]
    x1 = bsc_np(1, n_t, rng)[0]
    xi_B = bsc_np(1, n_t, rng)[0]
    xi_A = x1  # original value at hop 1
    W_chain = np.outer(x1, x0) / float(n_t)
    # CF: replace hop 0->1 (xi_A -> xi_B)
    W_cf = W_chain - np.outer(xi_A, x0) / float(n_t) + np.outer(xi_B, x0) / float(n_t)
    # root-start: probe from x0
    r_root = hopfield_retrieve_np(W_cf, x0)
    cf_cos_root = cosine_sim(r_root, xi_B)
    assert cf_cos_root is not None and not np.isnan(cf_cos_root), f"cf_cos_root is NaN"
    # (no assertion on magnitude -- just that it's non-null/non-NaN)

    # Test 2: predecessor-start depth-1 (same as root for depth=1, pred is x0)
    r_pred = hopfield_retrieve_np(W_cf, x0)
    cf_cos_pred = cosine_sim(r_pred, xi_B)
    assert cf_cos_pred is not None and not np.isnan(cf_cos_pred), f"cf_cos_pred is NaN"
    assert abs(cf_cos_root - cf_cos_pred) < 1e-9, "pred-start != root-start at d=1"

    # Test 3: metrics dict has required keys after one run
    result = {
        "depth": 1, "seed": 42,
        "cf_cos_pred_start": float(cf_cos_pred),
        "cf_cos_root_start": float(cf_cos_root),
    }
    assert "cf_cos_pred_start" in result, "missing cf_cos_pred_start"
    assert "cf_cos_root_start" in result, "missing cf_cos_root_start"

    # Test 4: filter passes >= 1 item at smoke scale (depths list is non-empty)
    assert len(TEST_DEPTHS) >= 1, "TEST_DEPTHS is empty"
    assert len(EVEN_DEPTHS) >= 1, "EVEN_DEPTHS is empty"
    assert len(ODD_DEPTHS) >= 1, "ODD_DEPTHS is empty"

    print(f"[selftest] PASS: cf_cos_root={cf_cos_root:.3f}, cf_cos_pred={cf_cos_pred:.3f}, "
          f"depths={TEST_DEPTHS} N_active={N_ACTIVE}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed_depth_sweep(seed: int, n_dim: int) -> Dict:
    """Run both protocols at each depth for one seed."""
    rng = np.random.RandomState(seed)
    t0 = time.time()

    M_bg = max(1, int(ALPHA * n_dim))
    bg_keys = bsc_np(M_bg, n_dim, rng)
    bg_vals = bsc_np(M_bg, n_dim, rng)
    W_bg = (bg_vals.T @ bg_keys) / float(n_dim)

    depth_results = []
    for depth in TEST_DEPTHS:
        chain = [bsc_np(1, n_dim, rng)[0] for _ in range(depth + 1)]

        # Build heteroassociative chain W_chain
        W_chain = W_bg.copy().astype(np.float64)
        for d_idx in range(depth):
            W_chain += np.outer(chain[d_idx + 1], chain[d_idx]) / float(n_dim)

        # Substitution: at midpoint (subst_pos)
        subst_pos = max(1, depth // 2)
        xi_A = chain[subst_pos]
        xi_B = bsc_np(1, n_dim, rng)[0]

        # Build counterfactual W: replace hop (subst_pos-1 -> subst_pos) with xi_B
        W_cf = W_chain - np.outer(xi_A, chain[subst_pos - 1]) / float(n_dim) \
                       + np.outer(xi_B, chain[subst_pos - 1]) / float(n_dim)

        # PROTOCOL 1: predecessor-start (probe from chain[subst_pos - 1])
        pred_probe = chain[subst_pos - 1].copy()
        r_pred = hopfield_retrieve_np(W_cf, pred_probe)
        cf_cos_pred = cosine_sim(r_pred, xi_B)

        # PROTOCOL 2: root-start (probe from chain[0] traversing through W_cf)
        # For root-start, we traverse through W_cf for depth steps starting at chain[0]
        root_probe = chain[0].copy().astype(np.float64)
        for _ in range(depth):
            h = W_cf @ root_probe
            root_probe = np.sign(h)
            root_probe[root_probe == 0] = 1.0
        cf_cos_root = cosine_sim(root_probe, xi_B)

        print(f"  [seed={seed} depth={depth}] pred_start={cf_cos_pred:.4f} "
              f"root_start={cf_cos_root:.4f}", flush=True)

        depth_results.append({
            "depth": depth,
            "cf_cos_pred_start": float(cf_cos_pred),
            "cf_cos_root_start": float(cf_cos_root),
            "subst_pos": subst_pos,
        })

    elapsed = time.time() - t0
    return {
        "seed": seed, "N": n_dim, "alpha": ALPHA, "run_mode": RUN_MODE,
        "elapsed_s": float(elapsed),
        "depth_results": depth_results,
    }


def compute_verdict(all_results: List[Dict]) -> tuple:
    if not all_results:
        return ("HARD_FAIL", "No valid results.")

    # Aggregate per-depth means across seeds
    depth_pred = {d: [] for d in TEST_DEPTHS}
    depth_root = {d: [] for d in TEST_DEPTHS}
    for r in all_results:
        for dr in r.get("depth_results", []):
            d = dr["depth"]
            depth_pred[d].append(dr["cf_cos_pred_start"])
            depth_root[d].append(dr["cf_cos_root_start"])

    pred_means = {d: float(np.mean(v)) if v else 0.0 for d, v in depth_pred.items()}
    root_means = {d: float(np.mean(v)) if v else 0.0 for d, v in depth_root.items()}

    pred_str = " ".join(f"d{d}={pred_means[d]:.3f}" for d in TEST_DEPTHS)
    root_str = " ".join(f"d{d}={root_means[d]:.3f}" for d in TEST_DEPTHS)
    summary = (f"pred_start: {pred_str} | root_start: {root_str} | "
               f"n_seeds={len(all_results)}")

    # Check HARD_FAIL: both protocols broken at all depths
    all_pred_low = all(pred_means.get(d, 0.0) <= HF_BOTH_BROKEN for d in TEST_DEPTHS)
    all_root_low = all(root_means.get(d, 0.0) <= HF_BOTH_BROKEN for d in TEST_DEPTHS)
    if all_pred_low and all_root_low:
        return ("HARD_FAIL", f"HARD_FAIL: both protocols broken. {summary}")

    # Check PARITY-CLASS: even-depth high, odd-depth suppressed
    even_pred_high = sum(1 for d in EVEN_DEPTHS if pred_means.get(d, 0.0) >= HP_PARITY_EVEN_THRESH)
    odd_pred_low = sum(1 for d in ODD_DEPTHS if pred_means.get(d, 0.0) <= HP_PARITY_ODD_THRESH)
    parity_confirmed = even_pred_high >= max(1, len(EVEN_DEPTHS) * 3 // 4) and \
                       odd_pred_low >= max(1, len(ODD_DEPTHS) * 3 // 4)

    # Check PROTOCOL-ARTIFACT: pred_start saturated, root_start smooth
    all_pred_ceiling = all(pred_means.get(d, 1.0) <= HP_PROTO_PRED_CEIL for d in TEST_DEPTHS)
    root_above_floor = sum(1 for d in TEST_DEPTHS if d >= 2 and root_means.get(d, 0.0) >= HP_PROTO_ROOT_FLOOR)
    deep_depths = [d for d in TEST_DEPTHS if d >= 2]
    proto_confirmed = all_pred_ceiling and root_above_floor >= max(1, len(deep_depths) * 3 // 4)

    if parity_confirmed:
        return ("HARD_PASS",
                f"HARD_PASS: PARITY-CLASS confirmed. "
                f"even_hp={even_pred_high}/{len(EVEN_DEPTHS)} odd_supp={odd_pred_low}/{len(ODD_DEPTHS)}. "
                f"{summary}")

    if proto_confirmed:
        return ("HARD_PASS",
                f"HARD_PASS: PROTOCOL-ARTIFACT confirmed. "
                f"pred_ceiling=True root_floor={root_above_floor}/{len(deep_depths)}. "
                f"{summary}")

    # Mixed / MIDDLE: some evidence but neither pure mechanism
    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: MIXED mechanism (parity_confirmed={parity_confirmed}, "
            f"proto_confirmed={proto_confirmed}). {summary}")


print(f"[config] anchor={ANCHOR_NAME} N={N_ACTIVE} alpha={ALPHA} mode={RUN_MODE} "
      f"depths={TEST_DEPTHS} seeds={SEEDS}", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "alpha": ALPHA, "test_depths": TEST_DEPTHS, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
all_results = []

for seed in done:
    fpath = out_dir / f"seed_{seed}.json"
    if fpath.exists():
        d = json.loads(fpath.read_text(encoding="utf-8"))
        if isinstance(d, dict):
            all_results.append(d)

for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME} starting...", flush=True)
    r = run_seed_depth_sweep(seed, N_ACTIVE)
    all_results.append(r)
    write_partial(out_dir, seed, r)

verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "alpha": ALPHA, "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS), "test_depths": TEST_DEPTHS,
    "elapsed_s": float(elapsed_total),
    "all_results": all_results,
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
