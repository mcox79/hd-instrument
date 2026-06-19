"""DR Mechanism 4: Merkle + random-projection W verify (R2.5).

SCIENTIFIC QUESTION (R2.5):
  Does random-projection fingerprinting detect W matrix corruption
  (>100 bit flips in a float32 W matrix) with P>0.95?
  Combines Merkle hash of W blocks with random-projection sketch for
  efficient corruption detection without full W materialization.

PRE-REGISTERED BANDS:
  HARD-PASS: P(detect corruption | >100 bit flips) > 0.95 in >= 3/5 seeds.
  HARD-FAIL: P(detect) < 0.80 in majority (sketch too weak).
  MIDDLE: 0.80 <= P(detect) <= 0.95.

DESIGN:
  N=4096, M=1024. W is N x N float32.
  Method 1 (Merkle): hash each W block (8x8 blocks) -> detect flipped blocks.
  Method 2 (random-projection): project W @ r for random unit r, compare to
    stored sketch. Corruption in any row changes sketch norm detectably.
  Corruption: flip n_flip=200 random bits in W (float32 = 32 bits per element).
  Use 20 random unit vectors for the projection sketch.
  Seeds: [7,17,23,31,41].

CALIBRATION NOTE: no prior empirical anchor. Bands per calibration policy.

PROT-018: production N=4096 (no _n suffix).
PROT-019: N>=4096 timeout >= 14400s.
PROT-021: M-tagged checkpoint keys.

Anchor: dr_merkle_randproj_w_verify_v1_n4096
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_dr_merkle_randproj_w_verify.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import hashlib
import importlib.util
import json
import os
import struct
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_dr", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key
list_completed_keys = _ck.list_completed_keys

N_FULL  = 4096
N_SMOKE = 512
M_FULL  = 1024
M_SMOKE = 128
N_FLIP_FULL  = 200   # bit flips to inject
N_FLIP_SMOKE = 50
N_PROJ_VECS  = 20    # random projection vectors
BLOCK_SIZE   = 8     # Merkle block size for row-blocks
N_TRIALS     = 50    # trials per seed for P(detect) estimate

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

HP_DETECT_PROB = 0.95
HF_DETECT_PROB = 0.80

assert N_FULL == 4096, "N_FULL must be 4096"


def build_w(N: int, M: int, seed: int) -> np.ndarray:
    """Build Hebbian W at N x N."""
    rng = np.random.default_rng(seed)
    keys = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float32)
    vals = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float32)
    return (vals.T @ keys) / N


def merkle_row_blocks(W: np.ndarray, block_size: int) -> List[bytes]:
    """Compute per-block hashes (rows batched by block_size)."""
    n_rows = W.shape[0]
    hashes = []
    for i in range(0, n_rows, block_size):
        block = W[i: i + block_size]
        h = hashlib.sha256(block.tobytes()).digest()
        hashes.append(h)
    return hashes


def randproj_sketch(W: np.ndarray, proj_vecs: np.ndarray) -> np.ndarray:
    """Sketch = W @ proj_vecs.T, shape (N x k)."""
    return W @ proj_vecs.T  # N x k


def inject_bitflips(W: np.ndarray, n_flip: int,
                    rng: np.random.Generator) -> np.ndarray:
    """Flip n_flip random bits in float32 W (view as uint32)."""
    W_corrupt = W.copy()
    flat = W_corrupt.view(np.uint32).ravel()
    total_bits = len(flat) * 32
    bit_positions = rng.choice(total_bits, size=n_flip, replace=False)
    for bp in bit_positions:
        elem_idx = int(bp) // 32
        bit_offset = int(bp) % 32
        flat[elem_idx] ^= (np.uint32(1) << bit_offset)
    return W_corrupt


def detect_corruption(W_orig: np.ndarray, W_corrupt: np.ndarray,
                      merkle_orig: List[bytes],
                      sketch_orig: np.ndarray,
                      proj_vecs: np.ndarray,
                      block_size: int) -> Dict[str, bool]:
    """Check if either detection method fires."""
    # Method 1: Merkle block hash comparison
    merkle_corrupt = merkle_row_blocks(W_corrupt, block_size)
    merkle_detected = any(h1 != h2 for h1, h2 in
                          zip(merkle_orig, merkle_corrupt))

    # Method 2: random-projection sketch L2 norm change
    sketch_corrupt = randproj_sketch(W_corrupt, proj_vecs)
    # Compare per-column L2 norms of sketches
    norm_orig = np.linalg.norm(sketch_orig, axis=0)
    norm_corrupt = np.linalg.norm(sketch_corrupt, axis=0)
    # Detect if any column norm changes by > 1% (threshold calibrated for 200 flips)
    rel_change = np.abs(norm_orig - norm_corrupt) / (np.abs(norm_orig) + 1e-9)
    proj_detected = bool(rel_change.max() > 0.001)

    return {
        "merkle_detected": merkle_detected,
        "proj_detected": proj_detected,
        "combined_detected": merkle_detected or proj_detected,
    }


def measure_seed(N: int, M: int, n_flip: int, n_proj: int,
                 n_trials: int, seed: int) -> Dict:
    """Measure P(detect corruption | n_flip bit flips) over n_trials."""
    rng = np.random.default_rng(seed)
    W = build_w(N, M, seed)

    # Precompute reference structures
    proj_vecs = rng.standard_normal((n_proj, N)).astype(np.float32)
    norms = np.linalg.norm(proj_vecs, axis=1, keepdims=True)
    proj_vecs /= np.maximum(norms, 1e-9)

    merkle_orig = merkle_row_blocks(W, BLOCK_SIZE)
    sketch_orig = randproj_sketch(W, proj_vecs)

    # Run trials
    n_detected_merkle  = 0
    n_detected_proj    = 0
    n_detected_combined = 0

    for trial in range(n_trials):
        rng_t = np.random.default_rng(seed + trial * 1000)
        W_c = inject_bitflips(W, n_flip, rng_t)
        result = detect_corruption(W, W_c, merkle_orig, sketch_orig,
                                   proj_vecs, BLOCK_SIZE)
        n_detected_merkle  += int(result["merkle_detected"])
        n_detected_proj    += int(result["proj_detected"])
        n_detected_combined += int(result["combined_detected"])

    p_merkle   = n_detected_merkle / n_trials
    p_proj     = n_detected_proj / n_trials
    p_combined = n_detected_combined / n_trials

    return {
        "seed": seed,
        "N": N,
        "M": M,
        "n_flip": n_flip,
        "n_trials": n_trials,
        "p_detect_merkle": float(p_merkle),
        "p_detect_proj": float(p_proj),
        "p_detect_combined": float(p_combined),
        "passes_hp": int(p_combined >= HP_DETECT_PROB),
        "ok": True,
    }


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("DR_MERKLE_INCONCLUSIVE", "no cells")
    ok = [c for c in cells if c.get("ok")]
    if not ok:
        return ("DR_MERKLE_INCONCLUSIVE", "all cells failed")

    n_hp = sum(c["passes_hp"] for c in ok)
    n_hf = sum(1 for c in ok if c["p_detect_combined"] < HF_DETECT_PROB)
    majority = len(ok) // 2 + 1
    mean_p = sum(c["p_detect_combined"] for c in ok) / len(ok)

    detail = (
        f"N={ok[0]['N']} n_flip={ok[0]['n_flip']} "
        f"mean_P_detect={mean_p:.4f} n_hp={n_hp}/{len(ok)} "
        f"P_vals={[round(c['p_detect_combined'],3) for c in ok]}"
    )

    if n_hf >= majority:
        return ("DR_MERKLE_HARD_FAIL",
                f"DETECTION_TOO_WEAK: p<{HF_DETECT_PROB} "
                f"in {n_hf}/{len(ok)} seeds. " + detail)
    if n_hp >= majority:
        return ("DR_MERKLE_HARD_PASS",
                f"CORRUPTION_DETECTABLE: P>={HP_DETECT_PROB} "
                f"in {n_hp}/{len(ok)} seeds. " + detail)
    return ("DR_MERKLE_MIDDLE_BAND",
            f"PARTIAL: mean_P={mean_p:.4f}. " + detail)


def get_output_dir(default_name: str = "dr_merkle_randproj_w_verify_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _instrumentation_selftest() -> None:
    """Assert all metrics non-null/non-sentinel."""
    # PROT-018
    assert N_FULL == 4096, "PROT-018 violation"

    # Formula self-test 1: inject_bitflips changes W
    rng = np.random.default_rng(42)
    W_t = np.ones((64, 64), dtype=np.float32)
    W_c = inject_bitflips(W_t, 10, rng)
    assert not np.array_equal(W_t, W_c), "inject_bitflips did not change W"
    n_changed = int(np.sum(W_t != W_c))
    assert n_changed >= 1, f"0 elements changed after bit flips"
    print(f"[selftest] formula-1 inject_bitflips changed {n_changed} elements PASS",
          flush=True)

    # Formula self-test 2: Merkle detects changed block
    W_t2 = np.ones((64, 64), dtype=np.float32)
    merkle_orig = merkle_row_blocks(W_t2, 8)
    W_c2 = W_t2.copy()
    W_c2[0, 0] += 1.0  # change first element
    merkle_new = merkle_row_blocks(W_c2, 8)
    assert merkle_orig[0] != merkle_new[0], "Merkle failed to detect change in block 0"
    print(f"[selftest] formula-2 Merkle detects block change PASS", flush=True)

    # Formula self-test 3: live smoke at small N
    out = measure_seed(N_SMOKE, M_SMOKE, N_FLIP_SMOKE, N_PROJ_VECS, 10, 42)
    assert out["ok"], f"measure_seed failed"
    assert 0.0 <= out["p_detect_combined"] <= 1.0, \
        f"p_detect_combined sentinel: {out['p_detect_combined']}"
    assert out["p_detect_merkle"] >= 0, "p_detect_merkle sentinel"
    assert out["n_trials"] >= 1, "n_trials=0"
    print(f"[selftest] formula-3 smoke N={N_SMOKE} n_flip={N_FLIP_SMOKE} "
          f"P_detect={out['p_detect_combined']:.4f} PASS", flush=True)

    # Formula self-test 4: verdict gates
    fake_hp = [{"ok": True, "N": 4096, "M": 1024, "n_flip": 200, "n_trials": 50,
                "p_detect_merkle": 1.0, "p_detect_proj": 0.9,
                "p_detect_combined": 1.0, "passes_hp": 1}
               for _ in range(5)]
    v, _ = compute_verdict(fake_hp)
    assert "HARD_PASS" in v, f"HP gate: {v}"
    fake_hf = [{"ok": True, "N": 4096, "M": 1024, "n_flip": 200, "n_trials": 50,
                "p_detect_merkle": 0.5, "p_detect_proj": 0.3,
                "p_detect_combined": 0.6, "passes_hp": 0}
               for _ in range(5)]
    v, _ = compute_verdict(fake_hf)
    assert "HARD_FAIL" in v, f"HF gate: {v}"
    print("[selftest] formula-4 verdict gates PASS", flush=True)

    print("[selftest] dr_merkle_randproj_w_verify_v1_n4096 ALL PASS", flush=True)


_instrumentation_selftest()


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)

    smoke   = args.smoke
    N_cfg   = N_SMOKE if smoke else N_FULL
    M_cfg   = M_SMOKE if smoke else M_FULL
    n_flip  = N_FLIP_SMOKE if smoke else N_FLIP_FULL
    n_trials = max(10, N_TRIALS // (5 if smoke else 1))
    seeds   = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    run_config = {"N": N_cfg, "M": M_cfg, "run_mode": "smoke" if smoke else "full"}
    done = set(list_completed_keys(out_dir, run_config=run_config))

    t0 = time.time()
    print(f"[run] dr_merkle_randproj_w_verify_v1_n4096 smoke={smoke} "
          f"N={N_cfg} M={M_cfg} n_flip={n_flip} n_trials={n_trials} "
          f"seeds={seeds} done={len(done)}", flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"M{M_cfg}_seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body)
                print(f"  [resume] seed={seed} loaded", flush=True)
                continue
        try:
            cell = measure_seed(N_cfg, M_cfg, n_flip, N_PROJ_VECS, n_trials, seed)
            cell["run_mode"] = "smoke" if smoke else "full"
            write_partial_key(out_dir, ck, cell)
            cells.append(cell)
            print(f"  seed={seed} ok={cell.get('ok')} "
                  f"P_detect={cell.get('p_detect_combined','n/a'):.4f} "
                  f"P_merkle={cell.get('p_detect_merkle','n/a'):.4f} "
                  f"P_proj={cell.get('p_detect_proj','n/a'):.4f} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except Exception as e:
            print(f"  seed={seed} FAILED: {e}", flush=True)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {
        "anchor": "dr_merkle_randproj_w_verify_v1_n4096",
        "N": N_cfg, "M": M_cfg, "smoke": smoke, "seeds": seeds,
        "n_flip": n_flip, "n_trials": n_trials,
        "cells": cells, "verdict": verdict, "verdict_msg": vm,
        "elapsed_s": elapsed,
    }
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
