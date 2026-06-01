"""REASONING STORAGE 4-WAY BINDING + PER-HOP CLEANUP v2 at N=16384 (5-seed upgrade).

CONTEXT (cap_map v305; v1 = 4WC_HARD_PASS BORDERLINE-OVER-CLAIM 163rd LABEL-VS-HONEST):
  v1 landed 4WC_HARD_PASS at 3 seeds [7, 17, 23] but was labeled BORDERLINE-OVER-CLAIM
  because Arm C per-seed strict <2% gate was borderline: seed 7=2.5%, seed 17=2.5%, seed 23=1.0%.
  Mean gap closure was exactly on the 2% boundary.

  v2 extends to 5 seeds [7, 17, 23, 31, 41] to resolve the borderline with stronger statistics.
  Science is IDENTICAL to v1 -- only the seed list changes.

  If 5-seed run achieves mean ratio >= 0.98 (gap < 2%) and all 5 seeds pass,
  PP-11 row LIFTS further: 0.50-0.65 -> 0.55-0.70 (clean HP upgrade).

SCIENTIFIC QUESTION:
  Does the v1 4WC + cleanup result replicate at 5-seed level with Arm C ratio >= 0.98
  on ALL 5 seeds (not just 3)?

DESIGN:
  All logic identical to v1. Only SEEDS_FULL changes to [7, 17, 23, 31, 41].
  Pre-registered thresholds IDENTICAL to v1.
  Output saved to a v2-specific directory to avoid overwriting v1 checkpoints.

PRE-REGISTERED BANDS (identical to v1):
  Arm C (combined 4-way + cleanup) -- PRIMARY:
    HARD-PASS  : mean structured-key accuracy ratio >= 0.98 (gap < 2%);
                 ALL 5 seeds pass; audit completeness 100% algebraic decomp;
                 cleanup step verification rate >= 0.95.
    HARD-FAIL  : mean ratio < 0.96 (< 1% absolute improvement vs PP-11 ~0.93).
    MIDDLE-BAND: mean ratio 0.96-0.98 (partial closure; 2-3% gap residual).

TIMEOUT ESTIMATE:
  v1 elapsed at remote CPU: ~33s/seed (3 seeds = ~100s total).
  v2: 5 seeds x 33s = 165s. Safety: ceil(1.5 * 165) = 248s -> 300s.
  PROT-019 floor: 14400s. timeout_s = 14400 (floor dominates; actual ~5 min).

PROT-018: _n16384 binds N = 16384.
PROT-019: timeout_s = 14400.

Anchor: reasoning_storage_4way_cleanup_v2_n16384
Queue: remote_cpu_queue (CPU-only; N=16384 BSC substrate 1 GB RAM ~5 min)
Pre-reg: preregs/2026-06-01_reasoning_storage_4way_cleanup_v2_n16384.md
HDLAB_EXP_NAME: reasoning_storage_4way_cleanup_v2_n16384
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import os
import time
from pathlib import Path
from typing import Dict, List

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# ============================================================
# PROT-018: _n16384 binds N = 16384
# ============================================================
N_FULL  = 16384   # PROT-018 binding
assert N_FULL == 16384, f"PROT-018: N_FULL must be 16384; got {N_FULL}"

# Load v1 module to reuse all logic (single source of truth for science)
_v1_path = REPO / "experiments" / "exp_reasoning_storage_4way_cleanup_v1_n16384.py"
_v1_spec = importlib.util.spec_from_file_location("rs4w_v1_for_v2", _v1_path)
_v1 = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(_v1)

# All scientific functions come from v1
run_one_seed    = _v1.run_one_seed
compute_verdict = _v1.compute_verdict

# Checkpoint helpers from v1's import
list_completed_keys = _v1.list_completed_keys
write_partial_key   = _v1.write_partial_key
load_partial_key    = _v1.load_partial_key

# ============================================================
# v2 config: 5 seeds (only change vs v1)
# ============================================================
SEEDS_FULL  = [7, 17, 23, 31, 41]   # extended to 5 seeds
SEEDS_SMOKE = [17]

N_CHAINS_FULL  = _v1.N_CHAINS_FULL
N_CHAINS_SMOKE = _v1.N_CHAINS_SMOKE
N_SMOKE        = _v1.N_SMOKE


# ============================================================
# Instrumentation self-test (delegates to v1 selftest)
# ============================================================

def _instrumentation_selftest() -> None:
    """Delegate to v1 selftest; verifies all v1 logic is importable and callable."""
    _v1._instrumentation_selftest()
    # Additionally verify the 5-seed config is compatible
    assert len(SEEDS_FULL) == 5, f"Expected 5 seeds, got {len(SEEDS_FULL)}"
    assert set(SEEDS_FULL) == {7, 17, 23, 31, 41}, f"Unexpected seeds: {SEEDS_FULL}"
    print("[selftest v2] PASS: v1 logic imported; 5-seed config verified.", flush=True)


_instrumentation_selftest()


def get_output_dir() -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", "reasoning_storage_4way_cleanup_v2_n16384")
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke",     action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)

    device = torch.device("cpu")
    smoke  = args.smoke or os.environ.get("HDLAB_SMOKE", "0") == "1"
    N_cfg  = N_SMOKE        if smoke else N_FULL
    n_ch   = N_CHAINS_SMOKE if smoke else N_CHAINS_FULL
    seeds  = SEEDS_SMOKE    if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done    = set(list_completed_keys(out_dir))
    t0      = time.time()

    print(
        f"[run] reasoning_storage_4way_cleanup_v2_n16384 "
        f"smoke={smoke} N={N_cfg} n_chains={n_ch} seeds={seeds} "
        f"done={len(done)} device={device.type}",
        flush=True,
    )

    per_seed: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                per_seed.append(body)
                print(f"  [ckpt] seed={seed} resumed", flush=True)
                continue
        result = run_one_seed(N_cfg, n_ch, seed, device)
        write_partial_key(out_dir, ck, result)
        per_seed.append(result)

    verdict, vm = compute_verdict(per_seed)
    elapsed     = round(time.time() - t0, 2)

    # Suspicious-result gate
    if per_seed:
        arm_c_accs = [s["arm_c_combined"]["retrieval"]["mean_per_hop_acc"] for s in per_seed]
        rand_accs  = [s["rand"]["mean_per_hop_acc"] for s in per_seed]
        if all(a == 0.0 for a in arm_c_accs + rand_accs):
            print("[INSTRUMENTATION_SUSPECT] all per-hop accuracies are 0.0 -- "
                  "possible retrieval bug", flush=True)

    summary = {
        "anchor":      "reasoning_storage_4way_cleanup_v2_n16384",
        "N":           N_cfg,
        "smoke":       smoke,
        "n_chains":    n_ch,
        "seeds":       seeds,
        "n_seeds":     len(seeds),
        "per_seed":    per_seed,
        "verdict":     verdict,
        "verdict_msg": vm,
        "elapsed_s":   elapsed,
    }
    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)

    print(f"[verdict] {verdict}: {vm}", flush=True)
    print(f"[done] elapsed={elapsed}s metrics={metrics_path}", flush=True)


if __name__ == "__main__":
    main()
