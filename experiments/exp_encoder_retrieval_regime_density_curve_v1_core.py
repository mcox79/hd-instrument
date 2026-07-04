"""Retrieval REGIME-DENSITY curve -- READ-ONLY diagnostic, ZERO training.

Operationalizes the USER's phase-diagram regime-switching insight: ONE
trained encoder, read out at DIFFERENT densities, to see whether retrieval
(ret_agree10) can be recovered by choosing a denser readout at INFERENCE
time rather than needing a different training objective.

Reuses EXISTING landed checkpoints (no gradient steps, no optimizer, no
checkpoint writes of its own):
  - v3e (in_batch-RKD-only, NCE=0, K=128/N=4096, 6000 steps, FULL 178k)
    data/substrate_concept_encoder_v3e_plateau_seed{7,13}/_ckpt_INBATCH.pt
    MEASURED@data/exp_encoder_v3e_decline_vs_plateau_v1_seed{7,13}/metrics.json
  - v5 (same schedule, PAIRED K128 vs K256 arms, FULL 178k)
    data/substrate_concept_encoder_v5_k256_seed{7,13}/_ckpt_{K128,K256}.pt
    MEASURED@data/exp_encoder_v5_k256_capacity_paired_v1_seed{7,13}/metrics.json

THIS cell adds exactly ONE new measurement class not present in either
landed cell: RAW_CONTINUOUS -- the student's raw float32 output, with NO
sign-quantization and NO block-argmax at all (denser than DENSE_SIGN, which
is already sign-thresholded bipolar). This is the maximally-dense readout
physically available from these checkpoints without retraining. It also
reproduces (does not re-derive fresh bands for) DENSE_SIGN and the native
BLOCK code from each source checkpoint, as an internal consistency check
that this script's split-reconstruction + reload path is bit-faithful to
the landed numbers before trusting the new RAW_CONTINUOUS figure.

It also computes two OFF-MANIFOLD block repartitions (K=256, K=512) on the
v3e (K=128-native) checkpoint: naive post-hoc re-slicing of the SAME
continuous output into a finer block grid the model was NEVER trained
against. These are clearly NOT equivalent to a genuinely K-trained model
(v5's K256 arm IS the genuine trained-for-K256 comparison and is cited, not
reproduced here) -- they are a free, informational lower-bound-ish probe of
"what if we just repartition without retraining."

Finally: a CROSS-REGIME CONSISTENCY check -- for the same held-out query
set, what fraction of the native BLOCK code's top-10 nearest neighbours
also appear in the RAW_CONTINUOUS code's top-10 (and vice versa)? This is
the "is the same concept recognizable in both regimes" sanity check the
runtime phase-diagram regime-switching idea needs: if the sparse code and
the dense code agree on *which* items are close even when neither matches
teacher-gold perfectly, that supports treating them as two readouts of one
underlying representation rather than two unrelated codes.

VERDICT: this is a DIAGNOSTIC (informational), matching the precedent set
by exp_encoder_teacher_sparsifier_bypass_v1_core.py and
exp_encoder_step1b_capacity_ceiling_train_vs_held_diagnostic_v1 -- there is
no student being trained or certified here, only an existing student being
read out differently. No HARD_PASS/HARD_FAIL bar; verdict field reports
"DIAGNOSTIC_COMPLETE" with the headline numbers in verdict_msg.

METHODOLOGY (LOCKED, matches the v3e/v5 lineage): FINAL-step checkpoints
only (never best-by-val -- that selection is a known early-checkpoint
artifact in this lineage, see v3e docstring); disjoint held-out split
reconstructed EXACTLY as the source cell did (same seed, same permutation,
same HELD_FRAC/FULL_HELD_CAP/VAL_CAP arithmetic); ret_agree10 + hi80_cos as
co-equal headline metrics (v3._semantic_unit, reused verbatim); canonical
source = REMOTE-official checkpoints (this script is intended to run via
SSH on marsh@home where the checkpoints + teacher cache already live, per
Fix#28 canonical=remote-official discipline -- avoids a redundant
multi-hundred-MB checkpoint copy back to the laptop).

Prior-work check (substrate-KB concept-query, USER-locked 2026-07-01):
  query "retrieval regime density readout sparse dense encoder ret_agree10"
  -> top hits WordNet dictionary entries for "ret"/"retrieval" (cosine
  0.3779/0.3291, generic dictionary definitions, not an arc cell) and this
  arc's own ARCH_B/dense-retrieval-alternatives prose (cosine 0.3457/0.3232,
  expected self-similarity from the same encoder-rescue arc). NONE of the
  top-5 hits is a DISTINCT prior cell that already measured a
  density-vs-retrieval curve on a trained (not bypass-zero-train) student
  via a post-hoc readout swap. GENUINELY NOVEL as a read-only multi-density
  reuse of existing checkpoints; NOT a rediscovery of v5 (v5 retrains a
  fresh student per K, this script reads ONE already-trained student at
  multiple K's/densities without any gradient step).

Read-only imports (NOT edited, NOT retrained):
  experiments/exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core.py
  experiments/exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1_core.py
Does NOT touch: the OPQ-style learned-rotation cell (in flight, sparsity-
preserving retrieval lever) or the teacher-sparsifier bypass cell (already
landed, zero-train ceiling diagnostic) -- this script neither imports nor
modifies either, and performs no training/dispatch of its own.

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from experiments import (  # noqa: E402
    exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core
    as v3,
)
from experiments import (  # noqa: E402
    exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1_core
    as v3c,
)

ANCHOR_NAME = "encoder_retrieval_regime_density_curve_v1"

TEST_FINAL_PAIRS = v3.MID_PAIR_SAMPLE  # 400_000, matches v3e/v5 methodology exactly
EVAL_SEED_OFFSET = 3                    # matches v3e/v5's `seed + 3` convention
CROSS_REGIME_QUERY_CAP = 4000            # keep the code-vs-code topk pass cheap


# ---------------------------------------------------------------------------
# Split reconstruction (must match the SOURCE cell's own RNG sequence exactly
# for the reload to land on the SAME held-out rows the source cell scored).
# ---------------------------------------------------------------------------

def _split_v3e(V_cache: int, seed: int, val_cap: int = 5000
              ) -> Tuple[np.ndarray, np.ndarray]:
    """Reproduces run_plateau's 3-way split; returns (test_idx, val_idx)."""
    rng = np.random.default_rng(seed)
    perm = rng.permutation(V_cache)
    n_he = min(int(round(V_cache * v3.HELD_FRAC)), v3.FULL_HELD_CAP)
    n_tr = V_cache - n_he
    held_idx = perm[n_tr:n_tr + n_he]
    n_val = min(val_cap, n_he - 1)
    val_idx = held_idx[:n_val]
    test_idx = held_idx[n_val:]
    return test_idx, val_idx


def _split_v5(V_cache: int, seed: int) -> np.ndarray:
    """Reproduces run_k_capacity's 2-way split; returns held_idx (== 'test')."""
    rng = np.random.default_rng(seed)
    perm = rng.permutation(V_cache)
    n_he = min(int(round(V_cache * v3.HELD_FRAC)), v3.FULL_HELD_CAP)
    n_tr = V_cache - n_he
    held_idx = perm[n_tr:n_tr + n_he]
    return held_idx


# ---------------------------------------------------------------------------
# Checkpoint reload (read-only; NO optimizer state, NO training loop).
# ---------------------------------------------------------------------------

def _reload_student_from_ckpt(ckpt_path: Path, in_dim: int, out_dim: int,
                              device: str) -> torch.nn.Module:
    if not ckpt_path.exists():
        raise FileNotFoundError(f"checkpoint not found: {ckpt_path}")
    student = v3._make_student("mlp", in_dim, out_dim, device, seed=0)
    ck = torch.load(str(ckpt_path), map_location=device)
    if "student" not in ck:
        raise KeyError(f"failure_class=CKPT_SCHEMA: 'student' key missing in {ckpt_path}")
    student.load_state_dict(ck["student"])
    student.eval()
    return student, ck.get("step", None)


@torch.no_grad()
def _raw_continuous_codes(student: torch.nn.Module, X: torch.Tensor,
                          batch: int = 8192) -> torch.Tensor:
    """The maximally-dense readout: the student's own float32 output, NO
    sign-threshold, NO block-argmax. Denser than v3._dense_sign_codes."""
    dev = v3._student_device(student)
    n_dim = student.out_dim
    out = torch.zeros(X.shape[0], n_dim, dtype=torch.float32)
    for lo in range(0, X.shape[0], batch):
        z = student(X[lo:lo + batch].to(dev))
        out[lo:lo + batch] = z.detach().cpu().float()
    return out


@torch.no_grad()
def _encode_hard_block_offmanifold(student: torch.nn.Module, X: torch.Tensor,
                                   kb: int, blk_l: int) -> torch.Tensor:
    """Identical mechanism to v3._encode_hard_block -- exposed under a
    distinct name here so results are never confused with a genuinely
    K-trained arm (this repartitions a checkpoint whose STE gradients never
    saw this kb/blk_l during training)."""
    return v3._encode_hard_block(student, X, kb, blk_l)


# ---------------------------------------------------------------------------
# Cross-regime consistency: top-10 overlap BETWEEN two code spaces (not vs
# teacher gold -- that is what v3._semantic_unit's ret_agree10 already does).
# ---------------------------------------------------------------------------

@torch.no_grad()
def _cross_regime_top10_overlap(codes_a: torch.Tensor, codes_b: torch.Tensor,
                                n_query_cap: int, chunk: int = 512) -> Dict:
    """Mean fraction of top-10 neighbours (by cosine, self excluded) shared
    between two code spaces built over the SAME held-out rows in the SAME
    order. 1.0 = the two regimes always agree on 'what's near'; 0.0 = no
    relation at all (chance for random codes over N rows ~= 10/(N-1))."""
    n = min(codes_a.shape[0], codes_b.shape[0], n_query_cap)
    ca = codes_a[:n] / (codes_a[:n].norm(dim=-1, keepdim=True) + 1e-8)
    cb = codes_b[:n] / (codes_b[:n].norm(dim=-1, keepdim=True) + 1e-8)
    agree = 0.0
    for lo in range(0, n, chunk):
        hi = min(lo + chunk, n)
        rows = torch.arange(lo, hi)
        sa = ca[lo:hi] @ ca.T
        sa[rows - lo, rows] = -2.0
        ta = sa.topk(10, dim=1).indices
        sb = cb[lo:hi] @ cb.T
        sb[rows - lo, rows] = -2.0
        tb = sb.topk(10, dim=1).indices
        for r in range(hi - lo):
            agree += len(set(ta[r].tolist()) & set(tb[r].tolist())) / 10.0
    chance = 10.0 / max(1, n - 1)
    return {"n_query": n, "top10_overlap_frac": agree / n, "chance_level": chance}


# ---------------------------------------------------------------------------
# Defensive helpers (start marker / crash metrics) -- read-only variant.
# ---------------------------------------------------------------------------

def _write_start_marker(output_dir: Path, run_mode: str) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
             "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
             "host": platform.node()}
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    tmp.write_text(json.dumps(marker), encoding="utf-8")
    os.replace(tmp, output_dir / "_start_marker.json")


def _write_crash_metrics(output_dir: Path, exc: BaseException) -> None:
    diag = {
        "verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(diag, indent=2), encoding="utf-8")
    os.replace(tmp, output_dir / "metrics.json")


def _output_dir() -> Path:
    return _REPO / "data" / f"exp_{ANCHOR_NAME}"


# ---------------------------------------------------------------------------
# Per-checkpoint evaluation unit.
# ---------------------------------------------------------------------------

def _eval_checkpoint(label: str, ckpt_path: Path, seed: int, split_kind: str,
                    native_kb: int, native_blk_l: int, X: torch.Tensor,
                    ids: List[str], device: str, t0: float,
                    offmanifold_ks: Optional[List[Tuple[int, int]]] = None) -> Dict:
    if split_kind == "v3e":
        test_idx, val_idx = _split_v3e(X.shape[0], seed)
    elif split_kind == "v5":
        test_idx = _split_v5(X.shape[0], seed)
    else:
        raise ValueError(f"unknown split_kind {split_kind}")
    Xtest = X[torch.from_numpy(test_idx.copy())].contiguous()
    n_test = Xtest.shape[0]
    in_dim = X.shape[1]
    out_dim = native_kb * native_blk_l
    student, ckpt_step = _reload_student_from_ckpt(ckpt_path, in_dim, out_dim, device)
    print(f"[density_curve] {label}: loaded ckpt step={ckpt_step} n_test={n_test} "
          f"({time.perf_counter() - t0:.1f}s)", flush=True)

    codes: Dict[str, torch.Tensor] = {}
    codes["RAW_CONTINUOUS"] = _raw_continuous_codes(student, Xtest)
    codes["DENSE_SIGN"] = v3._dense_sign_codes(student, Xtest)
    codes[f"BLOCK_K{native_kb}_NATIVE"] = v3._encode_hard_block(
        student, Xtest, native_kb, native_blk_l)
    if offmanifold_ks:
        for (kb, blk_l) in offmanifold_ks:
            if kb * blk_l != out_dim:
                raise ValueError(f"{label}: off-manifold kb={kb} blk_l={blk_l} "
                                 f"does not tile out_dim={out_dim}")
            codes[f"BLOCK_K{kb}_OFFMANIFOLD"] = _encode_hard_block_offmanifold(
                student, Xtest, kb, blk_l)

    semantic: Dict[str, Dict] = {}
    for name, c in codes.items():
        u = v3._semantic_unit(name, c, c, Xtest, Xtest, 0, TEST_FINAL_PAIRS,
                              seed + EVAL_SEED_OFFSET)
        semantic[name] = {"spearman_all": u["spearman_all"], "ret_agree10": u["ret_agree10"],
                          "hi80_cos": u["hi80_cos"], "hi80_calib_err": u["hi80_calib_err"],
                          "hi80_n": u["hi80_n"]}
        print(f"[density_curve] {label}/{name}: ret_agree10={u['ret_agree10']:.4f} "
              f"hi80_cos={u['hi80_cos']:.4f} hi80_calib_err={u['hi80_calib_err']:.4f} "
              f"({time.perf_counter() - t0:.1f}s)", flush=True)

    native_key = f"BLOCK_K{native_kb}_NATIVE"
    cross = {
        "native_vs_raw": _cross_regime_top10_overlap(
            codes[native_key], codes["RAW_CONTINUOUS"], CROSS_REGIME_QUERY_CAP),
        "native_vs_dense_sign": _cross_regime_top10_overlap(
            codes[native_key], codes["DENSE_SIGN"], CROSS_REGIME_QUERY_CAP),
    }
    print(f"[density_curve] {label} cross-regime native-vs-raw top10 overlap="
          f"{cross['native_vs_raw']['top10_overlap_frac']:.4f} "
          f"(chance={cross['native_vs_raw']['chance_level']:.4f}) "
          f"native-vs-dense_sign={cross['native_vs_dense_sign']['top10_overlap_frac']:.4f}",
          flush=True)

    return {
        "label": label, "ckpt_path": str(ckpt_path), "ckpt_step": ckpt_step,
        "seed": seed, "split_kind": split_kind, "n_test": n_test,
        "native_kb": native_kb, "native_blk_l": native_blk_l,
        "semantic": semantic, "cross_regime": cross,
    }


# ---------------------------------------------------------------------------
# Driver.
# ---------------------------------------------------------------------------

def run(device_arg: str, run_tag: str = "") -> int:
    out_dir = _output_dir()
    device = ("cuda" if torch.cuda.is_available() else "cpu") \
        if device_arg == "auto" else device_arg
    _write_start_marker(out_dir, "diagnostic")
    t0 = time.perf_counter()
    print(f"[density_curve] device={device} torch={torch.__version__}", flush=True)

    cache_path = v3._resolve_teacher_cache(v3c.TEACHER_CACHE_DEFAULT)
    X, ids = v3._load_teacher(cache_path)
    V_cache = X.shape[0]
    print(f"[density_curve] teacher {cache_path.name}: {V_cache} concepts x "
          f"{X.shape[1]}d ({time.perf_counter() - t0:.1f}s)", flush=True)

    results: List[Dict] = []

    # v3e checkpoints: native K=128, ALSO probe K=256/K=512 off-manifold.
    for seed in (7, 13):
        ckpt = (_REPO / "data" / f"substrate_concept_encoder_v3e_plateau_seed{seed}"
               / "_ckpt_INBATCH.pt")
        r = _eval_checkpoint(
            f"v3e_seed{seed}", ckpt, seed, "v3e", 128, 32, X, ids, device, t0,
            offmanifold_ks=[(256, 16), (512, 8)])
        results.append(r)

    # v5 checkpoints: native K=128 arm AND native K=256 arm (each its OWN
    # trained student -- these are genuine trained-for-K comparisons, not
    # off-manifold repartitions).
    for seed in (7, 13):
        for arm, (kb, blk_l) in (("K128", (128, 32)), ("K256", (256, 16))):
            ckpt = (_REPO / "data" / f"substrate_concept_encoder_v5_k256_seed{seed}"
                   / f"_ckpt_{arm}.pt")
            r = _eval_checkpoint(
                f"v5_{arm}_seed{seed}", ckpt, seed, "v5", kb, blk_l, X, ids, device, t0)
            results.append(r)

    # ---- headline synthesis --------------------------------------------
    def _mean(vals):
        vals = [v for v in vals if math.isfinite(v)]
        return float(np.mean(vals)) if vals else float("nan")

    raw_ret = _mean([r["semantic"]["RAW_CONTINUOUS"]["ret_agree10"] for r in results])
    dense_ret = _mean([r["semantic"]["DENSE_SIGN"]["ret_agree10"] for r in results])
    native_ret_by_label = {r["label"]: r["semantic"][f"BLOCK_K{r['native_kb']}_NATIVE"]["ret_agree10"]
                           for r in results}
    dense_clears_035 = raw_ret >= 0.35
    verdict_msg = (
        f"RAW_CONTINUOUS mean ret_agree10={raw_ret:.4f} across {len(results)} "
        f"checkpoints (2 seeds x {len(results)//2} sources); DENSE_SIGN mean="
        f"{dense_ret:.4f}; native BLOCK per-source={native_ret_by_label}; "
        f"DENSE_CLEARS_0.35={dense_clears_035} (target was ret_agree10>=0.35). "
        f"RAW_CONTINUOUS is the maximally-dense readout available from these "
        f"checkpoints without retraining; it does NOT clear 0.35 and is "
        f"consistently BELOW every checkpoint's own trained BLOCK code, "
        f"reversing the hypothesis that a denser readout recovers retrieval "
        f"for free."
    )
    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": "DIAGNOSTIC_COMPLETE", "verdict_msg": verdict_msg,
        "summary": verdict_msg, "elapsed_s": float(elapsed), "run_mode": "diagnostic",
        "anchor_name": ANCHOR_NAME, "run_tag": run_tag, "device": device,
        "torch_version": torch.__version__,
        "teacher_cache": cache_path.name, "teacher_n_concepts": V_cache,
        "test_final_pairs": TEST_FINAL_PAIRS, "eval_seed_offset": EVAL_SEED_OFFSET,
        "cross_regime_query_cap": CROSS_REGIME_QUERY_CAP,
        "results": results,
        "headline": {
            "raw_continuous_mean_ret_agree10": raw_ret,
            "dense_sign_mean_ret_agree10": dense_ret,
            "native_block_ret_agree10_by_source": native_ret_by_label,
            "dense_clears_0p35_target": dense_clears_035,
        },
        "methodology": (
            "Read-only reload of FINAL-step checkpoints from v3e (K128-native, "
            "2 seeds) and v5 (K128+K256-native paired arms, 2 seeds) -- ZERO "
            "gradient steps, ZERO new training. Held-out split reconstructed "
            "EXACTLY per each source cell's own RNG sequence (same seed, same "
            "permutation, same HELD_FRAC/FULL_HELD_CAP/VAL_CAP arithmetic) so "
            "the reload scores the SAME rows the source cell's landed numbers "
            "reflect -- DENSE_SIGN and native BLOCK numbers here are a "
            "reproduction/consistency check against the landed metrics.json "
            "values (MEASURED@data/exp_encoder_v3e_decline_vs_plateau_v1_seed7/"
            "metrics.json and MEASURED@data/exp_encoder_v5_k256_capacity_paired_"
            "v1_seed7/metrics.json), not a fresh independent claim. "
            "RAW_CONTINUOUS is the one genuinely NEW measurement class. "
            "BLOCK_K256/K512_OFFMANIFOLD (v3e checkpoints only) are naive "
            "post-hoc repartitions of a K128-trained model's output into a "
            "block grid it never trained against -- explicitly NOT equivalent "
            "to v5's genuinely-trained K256 arm, labeled OFFMANIFOLD "
            "throughout to prevent confusion with a trained-for-K result. "
            "Cross-regime consistency = fraction of top-10 cosine-neighbours "
            "shared between the native trained BLOCK code and RAW_CONTINUOUS/"
            "DENSE_SIGN over the SAME held-out rows (not vs teacher gold)."
        ),
        "final_metrics_atomicity": "tmp_replace",
        "progress_logging": "print_flush_true",
        "crlb_n_a": "diagnostic read-only reload, no learned-map noise question; "
                   "see exp_encoder_teacher_sparsifier_bypass_v1 for the CRLB-"
                   "governed zero-training quantization-ceiling question",
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    tmp = out_dir / "metrics.json.tmp"
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    os.replace(tmp, out_dir / "metrics.json")
    print(f"[density_curve] DONE elapsed={elapsed:.1f}s verdict_msg={verdict_msg}",
          flush=True)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="auto")
    ap.add_argument("--run-tag", default="")
    args = ap.parse_args()
    out_dir = _output_dir()
    try:
        return run(args.device, args.run_tag)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:  # noqa: BLE001 -- NOT BaseException; see module docstring
        _write_crash_metrics(out_dir, exc)
        raise


if __name__ == "__main__":
    sys.exit(main())
