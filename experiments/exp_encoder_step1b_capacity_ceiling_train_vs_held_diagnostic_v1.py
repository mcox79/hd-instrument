"""Read-only capacity-ceiling diagnostic: train-set (in-sample) vs held-out
DENSE spearman for the R1 step-1800 checkpoints (global + in_batch objectives).

Implements Rank-3 of notes/research_drill_encoder_052_to_085_ranked_levers_2026-07-04.md
("cheap decisive test", ~zero cost, uses ALREADY-SAVED checkpoints, no new training).

Question: is the 2-layer MLP student (1024->2048->4096) the CEILING for 0.85,
or a generalization/objective problem?
  - TRAIN >> HELD (e.g. train ~0.8+, held ~0.52): student CAN represent the
    geometry but does not GENERALIZE -> capacity is NOT the ceiling.
  - TRAIN ~= HELD ~= 0.52 (can't even fit the training set): capacity/objective
    IS the ceiling -> a bigger/deeper student is warranted.

This is a DIAGNOSTIC, not a HARD_PASS/HARD_FAIL gated experiment: no sweep axis,
no queue dispatch, no training. It loads two already-finished checkpoints,
encodes the teacher's train-sample and held-sample through each, and computes
the same DENSE-sign spearman metric used by the parent v3 cell's own eval path
(_semantic_unit's pair-sampling + spearman, WITHOUT the expensive O(n^2)
ret_agree10 retrieval-agreement loop, which is not needed to answer this
question and would be ~9x costlier on the ~39.5k-item train set for no benefit).

Reads ONLY (never writes) these upstream artifacts:
  - data/substrate_index/cached_indices/bge_large_v2_name_*.npz (teacher cache)
  - data/substrate_concept_encoder_v1b_v3global_mid/_ckpt_block_global.pt
  - data/substrate_concept_encoder_v1b_v3global_mid/_ckpt_block_in_batch.pt
Both checkpoints are step=1800 (training complete; R1's mid run process had
already moved into its eval phase and died there per prior session diagnosis --
verified no live process holds these files at time of authoring, and neither
file's mtime has changed across writes in this dir since Jul 4 12:39 EDT).

Does NOT import from or write into any v3b (batch-ratio/nce-ablation) cell or
directory -- imports ONLY read-only helpers from the v3 (parent, already-
landed) core module. Does NOT edit any shared helper.

Own artifact dir: data/exp_encoder_step1b_capacity_ceiling_train_vs_held_diagnostic_v1/
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
sys.path.insert(0, str(_REPO))

from experiments.exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core import (  # noqa: E402
    N_DIM_DEFAULT, SEED_DEFAULT, HELD_FRAC, MID_HELD_CAP, MID_PAIR_SAMPLE,
    _resolve_teacher_cache, _load_teacher, _make_student, _dense_sign_codes,
    _spearman,
)

ANCHOR_NAME = "encoder_step1b_capacity_ceiling_train_vs_held_diagnostic_v1"
OUTPUT_DIR = _REPO / "data" / f"exp_{ANCHOR_NAME}"
CKPT_DIR = _REPO / "data" / "substrate_concept_encoder_v1b_v3global_mid"
CKPT_PATHS = {
    "global": CKPT_DIR / "_ckpt_block_global.pt",
    "in_batch": CKPT_DIR / "_ckpt_block_in_batch.pt",
}
TRAIN_SAMPLE_CAP = 8000  # cap train-side encode/pair-sample cost; still >> held (4390)


def _write_start_marker(output_dir: Path) -> None:
    marker = {
        "pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "run_mode": "diagnostic",
        "expected_n_units": 4, "host": platform.node(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    final = output_dir / "_start_marker.json"
    tmp.write_text(json.dumps(marker), encoding="utf-8")
    os.replace(tmp, final)


def _write_crash_metrics(output_dir: Path, exc: BaseException) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(), "anchor_name": ANCHOR_NAME,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    tmp.write_text(json.dumps(diag, indent=2), encoding="utf-8")
    os.replace(tmp, final)


def _dense_spearman_only(codes: torch.Tensor, X: torch.Tensor, n_pairs: int,
                          seed: int) -> dict:
    """Same pair-sample + DENSE-sign spearman/pearson as the parent's
    _semantic_unit, WITHOUT the O(n^2) ret_agree10 retrieval loop (not needed
    to answer the capacity-ceiling question; would dominate cost on the
    larger train sample for zero added information here)."""
    n = X.shape[0]
    rng = np.random.default_rng(seed)
    i = torch.from_numpy(rng.integers(0, n, n_pairs))
    j = torch.from_numpy(rng.integers(0, n, n_pairs))
    keep = i != j
    i, j = i[keep], j[keep]
    tp = (X[i] * X[j]).sum(-1).numpy()
    cn = codes / (codes.norm(dim=-1, keepdim=True) + 1e-8)
    sp = (cn[i] * cn[j]).sum(-1).numpy()
    return {
        "spearman": _spearman(sp, tp),
        "pearson": float(np.corrcoef(sp, tp)[0, 1]),
        "n_pairs_sampled": int(len(tp)),
        "n_items": int(n),
    }


def _arms_must_differ(codes_by_arm: dict) -> dict:
    """META_RULE_AF-style sanity check: global vs in_batch checkpoints must
    produce genuinely different dense codes on the same held input, else the
    two 'arms' are silently the same checkpoint (cheap bug class to rule out)."""
    digests = {}
    for name, codes in codes_by_arm.items():
        digests[name] = hashlib.sha256(codes.numpy().tobytes()).hexdigest()
    names = list(digests)
    for a in range(len(names)):
        for b in range(a + 1, len(names)):
            na, nb = names[a], names[b]
            assert digests[na] != digests[nb], (
                f"ARMS_MUST_DIFFER VIOLATION: {na!r} and {nb!r} bit-identical "
                f"dense codes (hash={digests[na]}) -- checkpoint-loading bug")
    return digests


def main() -> int:
    t0 = time.perf_counter()
    _write_start_marker(OUTPUT_DIR)
    device = "cpu"
    n_dim = N_DIM_DEFAULT
    seed = SEED_DEFAULT

    for name, p in CKPT_PATHS.items():
        if not p.exists():
            raise FileNotFoundError(f"checkpoint missing for arm {name!r}: {p}")

    cache_path = _resolve_teacher_cache(None)
    X, ids = _load_teacher(cache_path)
    V_cache = X.shape[0]
    print(f"[diag] teacher {cache_path.name}: {V_cache} concepts x {X.shape[1]}d "
          f"({time.perf_counter() - t0:.1f}s)", flush=True)

    rng = np.random.default_rng(seed)
    perm = rng.permutation(V_cache)
    n_he = min(int(round(V_cache * HELD_FRAC)), MID_HELD_CAP)
    n_tr = V_cache - n_he
    he_idx = perm[n_tr:n_tr + n_he]
    tr_idx_full = perm[:n_tr]
    # Cap the train-side sample for cost; still 1.8x the held-set size, and a
    # uniform random subsample of the actual training distribution the
    # student optimized against (not a cherry-pick).
    tr_rng = np.random.default_rng(seed + 1000)
    tr_idx = tr_rng.choice(tr_idx_full, size=min(TRAIN_SAMPLE_CAP, n_tr),
                            replace=False)
    print(f"[diag] split replica: n_tr_full={n_tr} n_he={n_he} "
          f"train_sample_used={len(tr_idx)} "
          f"(matches mid_run.log train=39515 held=4390 -> "
          f"{'MATCH' if (n_tr, n_he) == (39515, 4390) else 'MISMATCH'})",
          flush=True)

    Xhe = X[torch.from_numpy(he_idx.copy())].contiguous()
    Xtr = X[torch.from_numpy(tr_idx.copy())].contiguous()

    results = {}
    dense_codes_he = {}
    for arm, ckpt_path in CKPT_PATHS.items():
        student = _make_student("mlp", X.shape[1], n_dim, device, seed)
        ckpt = torch.load(str(ckpt_path), map_location=device)
        student.load_state_dict(ckpt["student"])
        student.eval()
        step = ckpt.get("step")
        codes_he = _dense_sign_codes(student, Xhe)
        codes_tr = _dense_sign_codes(student, Xtr)
        dense_codes_he[arm] = codes_he
        held = _dense_spearman_only(codes_he, Xhe, MID_PAIR_SAMPLE, seed + 3)
        train = _dense_spearman_only(codes_tr, Xtr, MID_PAIR_SAMPLE, seed + 3)
        results[arm] = {"ckpt_step": step, "held": held, "train": train}
        print(f"[diag] arm={arm} step={step} "
              f"HELD_dense_spearman={held['spearman']:.4f} "
              f"TRAIN_dense_spearman={train['spearman']:.4f} "
              f"gap={train['spearman'] - held['spearman']:.4f} "
              f"({time.perf_counter() - t0:.1f}s)", flush=True)

    arm_digests = _arms_must_differ(dense_codes_he)

    # Interpretation per drill's Rank-3 falsifiable framing.
    gaps = {arm: results[arm]["train"]["spearman"] - results[arm]["held"]["spearman"]
            for arm in results}
    max_gap = max(gaps.values())
    max_held = max(results[arm]["held"]["spearman"] for arm in results)
    if max_gap >= 0.15:
        regime = "GENERALIZATION_BOUND"
        implication = ("TRAIN >> HELD: the 2-layer MLP student CAN fit the "
                        "training geometry but does not generalize to held "
                        "concepts -- capacity is NOT the ceiling; a bigger/"
                        "deeper student (Rank 5) is DEPRIORITIZED; stay on "
                        "the objective-side levers (Rank 1/2).")
    elif max_gap <= 0.05 and max_held <= 0.60:
        regime = "CAPACITY_BOUND"
        implication = ("TRAIN ~= HELD ~= ~0.52: the student cannot even fit "
                        "the training set -- capacity/objective IS the "
                        "ceiling; a bigger/deeper student (Rank 5) is "
                        "WARRANTED as the next lever.")
    else:
        regime = "AMBIGUOUS"
        implication = (f"max_gap={max_gap:.4f} max_held={max_held:.4f} falls "
                        "between the two clean regimes; report both numbers "
                        "to Research for judgment rather than auto-classify.")

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": "DIAGNOSTIC_COMPLETE",
        "verdict_msg": f"regime={regime}; max_gap={max_gap:.4f}; max_held={max_held:.4f}",
        "summary": implication,
        "elapsed_s": elapsed,
        "anchor_name": ANCHOR_NAME,
        "run_mode": "diagnostic",
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "config": {
            "n_dim": n_dim, "seed": seed, "n_tr_full": int(n_tr),
            "n_he": int(n_he), "train_sample_cap": TRAIN_SAMPLE_CAP,
            "train_sample_used": int(len(tr_idx)), "n_pairs": MID_PAIR_SAMPLE,
        },
        "arms_differ_verified": True,
        "arm_digests_prefix8": {k: v[:8] for k, v in arm_digests.items()},
        "per_arm": results,
        "gaps": gaps,
        "regime": regime,
        "implication": implication,
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    tmp = OUTPUT_DIR / "metrics.json.tmp"
    final = OUTPUT_DIR / "metrics.json"
    tmp.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    os.replace(tmp, final)
    print(f"[diag] wrote {final} ({elapsed:.1f}s total)", flush=True)
    print("[diag] REGIME=" + regime, flush=True)
    print("[diag] " + implication, flush=True)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001 -- NOT BaseException; preserves SystemExit/KeyboardInterrupt
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
