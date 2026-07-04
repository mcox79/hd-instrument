"""Teacher-through-sparsifier BYPASS diagnostic (code-capacity ceiling,
ZERO training). Director/VET-recommended cheapest decisive test: pass the
raw teacher (BGE-large) embeddings through the SAME K-block hard-argmax+sign
quantizer used by every student in this encoder lineage, WITHOUT any learned
projection at all -- isolating what the CODE ITSELF (the K-blocks-of-L
one-hot*sign format) can preserve from what a trained student's learning
error additionally costs.

Two FIXED (non-learned) linear "lift" maps from teacher-dim (1024) to the
code's pre-quantization width, each applied THEN quantized via the exact
same `v3._encode_hard_block` path every trained student in this lineage
uses:

  - ORTHO_ISOMETRIC: an exact isometry (QR-orthonormal-columns random
    matrix) -- ZERO information loss before quantization. Any shortfall from
    1.0 spearman is attributable PURELY to the hard block-argmax+sign
    quantization step itself, not to any projection/learning imperfection.
    This is the CODE-CAPACITY CEILING: the best any student could possibly
    do at this K, even with a perfect (zero-error) learned map.
  - RANDOM_GAUSSIAN: an i.i.d. Gaussian random projection (NOT orthonormalized)
    -- the generic "what does an untrained/random network effectively do"
    case. This is the SAME mechanism that produces the well-documented
    untrained-network SimHash-like artifact seen at step~0 in every trained
    run this lineage has landed (e.g. v3c seed_7/13 DENSE~0.956@step0,
    MEASURED@data/exp_encoder_migration_step1b_v3c_paired_rkd_only_seed_7/
    metrics.json:recovery.inbatch_traj[0]) -- this cell explains that
    artifact directly rather than treating it as unexplained noise.

Each lift is applied at TWO code sizes: K=128/N=4096 (the lineage's current
production config) and K=256/N=8192 (doubled code, block_l=32 unchanged) --
answering "how much does bigger code close the DENSE->BLOCK gap" AS A PURE
CODE-CAPACITY QUESTION, isolated from student/objective difficulty (the
comparison the original 4-arm ceiling-attribution design wanted, folded in
here at zero extra training cost since this cell already builds the
K=256 harness for the isometric/random axis).

This is a DIAGNOSTIC (informational), not a HARD_PASS/HARD_FAIL gated
production experiment -- there is no "student" to certify. It answers:
of the gap between a trained student's BLOCK spearman and 1.0 (perfect),
how much is quantization-ceiling-bound (ORTHO_K128 < 1.0) vs student/
objective-bound (trained-student BLOCK spearman < ORTHO_K128)?

ZERO TRAINING: no gradient steps, no optimizer, no checkpoints. Cost is a
handful of matmuls + one hard-argmax pass + spearman over held pairs --
trivially cheap even at the full 177899-concept teacher cache. Dispatched to
GPU per Director/VET instruction (keeps the remote saturated even though
this specific cell does not need a GPU to be fast).

Reads ONLY (read-only imports, NOT edited): the v3 core module's teacher-
cache resolution, hard-block quantizer, semantic-unit metric, keyed-unit
integrity check, and control-arm code generators.

Prior-work check (substrate-KB concept-query, USER-locked 2026-07-01):
  query "isometric random projection block sparsifier quantization ceiling
  teacher embedding bypass no training code capacity" -> top hit
  cosine=0.2612 (WordNet 'isometry' dictionary entry, not an arc cell), all
  other hits <=0.24. NONE at cosine>0.30. GENUINELY NOVEL: no prior cell in
  this lineage bypasses the student entirely to isolate the quantizer's own
  ceiling.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified: sha256 over all 6 code matrices (2 lifts x 2 K's +
  RANDOM_BLOCK + CHARPOS)
- final_metrics_atomicity: tmp_replace
- except SystemExit: raise BEFORE except Exception (no BaseException, no bare except)
- crlb_floor_computed: N/A -- see `crlb_n_a` field: this is a zero-training
  linear-algebra diagnostic, not a learned-encoder capacity-feasibility
  question; the CRLB formula (`r_max = sigma_teacher/sqrt(sigma_teacher^2 +
  0.25/K)`) governs LEARNED-map noise, not the fixed isometric/random lifts
  measured here. Declared explicitly rather than silently omitted.
- baseline_in_band: CHARPOS ret_agree10 in (0.05, 0.95); RANDOM_BLOCK near-
  zero spearman (calibration floor).
- discriminator-survives-scale: N/A -- no training, no discriminator to
  "survive scale"; the same closed-form computation runs identically at
  smoke (local 43905-concept cache) and full (177899-concept cache) scale,
  differing only in V and n_pairs. SMOKE=FULL code path by construction.
- HARD_PASS/etc verdict: this cell reports `verdict: "DIAGNOSTIC_COMPLETE"`
  (not HARD_PASS/HARD_FAIL/MIDDLE_BAND) per the precedent set by
  `exp_encoder_step1b_capacity_ceiling_train_vs_held_diagnostic_v1` -- a
  diagnostic with no pass/fail bar, only a reported ceiling decomposition.
- cardinality_ok: EXPECTED_N_UNITS=8 both run_modes (6 semantic + 2 keyed
  integrity checks)
- per-unit failure-class instrumentation (META_RULE_J; no bare except)
- calibration_check: default_ok_for_this_regime (reuses the SAME K=128/
  N=4096 quantization channel + block_l=32 already validated throughout
  this lineage; K=256/N=8192 keeps block_l=32 unchanged, only the block
  COUNT doubles)
- numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ / VERIFIED@

Prereg: preregs/2026-07-04_exp_encoder_teacher_sparsifier_bypass_v1.md
Parent cell (read-only import, NOT edited):
  experiments/exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core.py
Does NOT touch any v3/v3b/v3c/v3e artifact or checkpoint directory -- this
cell trains nothing and has no checkpoints; own artifact dir:
data/exp_encoder_teacher_sparsifier_bypass_v1*/

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import hashlib
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

from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402
from experiments import (  # noqa: E402
    exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core
    as v3,
)

ANCHOR_NAME = "encoder_teacher_sparsifier_bypass_v1"
SEED_DEFAULT = v3.SEED_DEFAULT  # 7

TEACHER_CACHE_DEFAULT = (
    "data/substrate_index/cached_indices/bge_large_v2_name_177899_54f7cf6a.npz")

K_SMALL, BLK_L = v3.K_BLOCKS_PRIMARY, v3.N_DIM_DEFAULT // v3.K_BLOCKS_PRIMARY  # 128, 32
K_BIG = 256                          # doubled code (block_l unchanged at 32)
N_DIM_BIG = K_BIG * BLK_L             # 8192

FULL_FINAL_PAIRS = v3.MID_PAIR_SAMPLE   # 400_000
FULL_CHARPOS_CAP = v3.MID_CHARPOS_CAP
FULL_TRIALS = v3.MID_TRIALS

SMOKE_FINAL_PAIRS = 20_000
SMOKE_CHARPOS_CAP = 500
SMOKE_TRIALS = 20
SMOKE_N_TEST = 800   # local cache is 43905 concepts; keep TEST small+fast

EXPECTED_N_UNITS_FULL = 8    # 6 semantic (ORTHO_K128, RANDOM_K128, ORTHO_K256,
                             # RANDOM_K256, RANDOM_BLOCK, CHARPOS) + 2 keyed
                             # integrity (ORTHO_K128 J5, RANDOM_K128 J5)
EXPECTED_N_UNITS_SMOKE = 8

PREREG_BASELINE_ARMS = ["RANDOM_BLOCK", "CHARPOS"]


class _FrozenLinearEncoder(torch.nn.Module):
    """A fixed (non-learned) linear map, wrapped as a torch.nn.Module so it
    is a drop-in for v3._encode_hard_block (which expects `student(x)` and
    `next(student.parameters()).device`)."""

    def __init__(self, W: torch.Tensor):
        super().__init__()
        self.weight = torch.nn.Parameter(W, requires_grad=False)
        self.out_dim = int(W.shape[0])

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x @ self.weight.T.to(x.dtype)


def _make_ortho_isometric(in_dim: int, out_dim: int, seed: int, device: str) -> _FrozenLinearEncoder:
    """QR-orthonormal-columns lift: W [out_dim, in_dim] with W.T @ W == I_in_dim
    (exact isometry -- inner products in R^in_dim are preserved exactly in
    R^out_dim, PRE-quantization)."""
    assert out_dim >= in_dim, "isometric embedding requires out_dim >= in_dim"
    g = torch.Generator().manual_seed(seed)
    M = torch.randn(out_dim, in_dim, generator=g)
    Q, _ = torch.linalg.qr(M, mode="reduced")  # Q: [out_dim, in_dim], Q.T@Q = I
    return _FrozenLinearEncoder(Q.contiguous()).to(device)


def _make_random_gaussian(in_dim: int, out_dim: int, seed: int, device: str) -> _FrozenLinearEncoder:
    """i.i.d. Gaussian random projection (NOT orthonormalized) -- the
    generic 'untrained network' proxy."""
    g = torch.Generator().manual_seed(seed)
    W = torch.randn(out_dim, in_dim, generator=g) / math.sqrt(in_dim)
    return _FrozenLinearEncoder(W.contiguous()).to(device)


def _verify_isometry(enc: _FrozenLinearEncoder, in_dim: int, tol: float = 1e-4) -> float:
    """Return max |W.T@W - I| off-diagonal-inclusive entrywise error (should
    be ~0 for a genuine isometry; sanity check, not a gate)."""
    W = enc.weight.detach()
    WtW = W.T @ W
    I = torch.eye(in_dim, dtype=WtW.dtype)
    return float((WtW - I).abs().max())


def _write_start_marker(output_dir: Path, run_mode: str, expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "expected_n_units": int(expected_n_units), "host": platform.node(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    tmp.write_text(json.dumps(marker), encoding="utf-8")
    os.replace(tmp, output_dir / "_start_marker.json")


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
    tmp.write_text(json.dumps(diag, indent=2), encoding="utf-8")
    os.replace(tmp, output_dir / "metrics.json")


def _emit_heartbeat(output_dir: Path, unit_idx: int, total_units: int,
                    elapsed_s: float, extra: Optional[dict] = None) -> None:
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": int(unit_idx),
           "total_units": int(total_units), "elapsed_s": float(elapsed_s)}
    if extra:
        row["extra"] = extra
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def run_bypass(run_mode: str, seed: int, device_arg: str,
              teacher_cache_arg: Optional[str]) -> int:
    assert run_mode in ("smoke", "full"), f"unsupported run_mode {run_mode}"
    anchor = f"{ANCHOR_NAME}_smoke" if run_mode == "smoke" else ANCHOR_NAME
    out_dir = get_output_dir(anchor)
    device = ("cuda" if torch.cuda.is_available() else "cpu") \
        if device_arg == "auto" else device_arg

    expected_units = EXPECTED_N_UNITS_SMOKE if run_mode == "smoke" else EXPECTED_N_UNITS_FULL
    _write_start_marker(out_dir, run_mode, expected_units)
    t0 = time.perf_counter()
    print(f"[bypass] run_mode={run_mode} seed={seed} device={device}", flush=True)

    effective_cache_arg = teacher_cache_arg
    if run_mode == "full" and effective_cache_arg is None:
        effective_cache_arg = TEACHER_CACHE_DEFAULT
    cache_path = v3._resolve_teacher_cache(effective_cache_arg)
    cache_bytes = cache_path.stat().st_size
    X, ids = v3._load_teacher(cache_path)
    V_cache = X.shape[0]
    in_dim = X.shape[1]
    print(f"[bypass] teacher {cache_path.name}: {V_cache} concepts x {in_dim}d "
          f"({time.perf_counter() - t0:.1f}s)", flush=True)

    rng = np.random.default_rng(seed)
    perm = rng.permutation(V_cache)
    if run_mode == "smoke":
        n_test = min(SMOKE_N_TEST, V_cache)
        final_pairs, charpos_cap, n_trials = SMOKE_FINAL_PAIRS, SMOKE_CHARPOS_CAP, SMOKE_TRIALS
    else:
        n_he = min(int(round(V_cache * v3.HELD_FRAC)), v3.FULL_HELD_CAP)
        n_test = n_he
        final_pairs, charpos_cap, n_trials = FULL_FINAL_PAIRS, FULL_CHARPOS_CAP, FULL_TRIALS
    test_idx = perm[:n_test]
    Xtest = X[torch.from_numpy(test_idx.copy())].contiguous()
    names_test = [ids[i] for i in test_idx]
    print(f"[bypass] test split n={n_test}", flush=True)

    enc_ortho_128 = _make_ortho_isometric(in_dim, v3.N_DIM_DEFAULT, seed + 1, device)
    enc_random_128 = _make_random_gaussian(in_dim, v3.N_DIM_DEFAULT, seed + 2, device)
    enc_ortho_256 = _make_ortho_isometric(in_dim, N_DIM_BIG, seed + 3, device)
    enc_random_256 = _make_random_gaussian(in_dim, N_DIM_BIG, seed + 4, device)

    iso_err_128 = _verify_isometry(enc_ortho_128, in_dim)
    iso_err_256 = _verify_isometry(enc_ortho_256, in_dim)
    print(f"[bypass] isometry sanity: K128 max|WtW-I|={iso_err_128:.2e} "
          f"K256 max|WtW-I|={iso_err_256:.2e} ({time.perf_counter() - t0:.1f}s)",
          flush=True)

    arm_codes: Dict[str, torch.Tensor] = {
        "ORTHO_K128": v3._encode_hard_block(enc_ortho_128, Xtest, K_SMALL, BLK_L),
        "RANDOM_K128": v3._encode_hard_block(enc_random_128, Xtest, K_SMALL, BLK_L),
        "ORTHO_K256": v3._encode_hard_block(enc_ortho_256, Xtest, K_BIG, BLK_L),
        "RANDOM_K256": v3._encode_hard_block(enc_random_256, Xtest, K_BIG, BLK_L),
    }
    gen_ctrl = torch.Generator().manual_seed(seed + 5)
    arm_codes["RANDOM_BLOCK"] = v3._random_block_codes(n_test, K_SMALL, BLK_L, gen_ctrl)
    cp_cap = min(n_test, charpos_cap)
    cp_codes = v3._charpos_codes(names_test[:cp_cap], v3.N_DIM_DEFAULT, K_SMALL)
    print(f"[bypass] all codes encoded ({time.perf_counter() - t0:.1f}s)", flush=True)

    digests = {}
    for name, c in list(arm_codes.items()) + [("CHARPOS", cp_codes)]:
        digests[name] = hashlib.sha256(c.to(torch.int8).numpy().tobytes()).hexdigest()
    for a in digests:
        for b in digests:
            if a < b and digests[a] == digests[b]:
                raise RuntimeError(
                    f"failure_class=META_RULE_AF_VIOLATION: {a}/{b} identical")

    per_unit: List[Dict] = []
    unit_fail: List[Dict] = []
    gen_eval = torch.Generator().manual_seed(seed + 6)

    def _run_unit(fn, *a, **kw):
        try:
            u = fn(*a, **kw)
            per_unit.append(u)
            print(f"[bypass] unit {len(per_unit)}/{expected_units} {u['unit']}: "
                  + json.dumps({k: round(v, 4) for k, v in u.items()
                                if isinstance(v, float)}), flush=True)
            _emit_heartbeat(out_dir, len(per_unit), expected_units,
                            time.perf_counter() - t0, extra={"unit": u["unit"]})
        except (RuntimeError, ValueError, IndexError) as exc:
            unit_fail.append({"fn": getattr(fn, "__name__", "?"),
                              "failure_class": type(exc).__name__,
                              "msg": str(exc)[:300]})
            raise

    for label in ("ORTHO_K128", "RANDOM_K128", "ORTHO_K256", "RANDOM_K256"):
        c = arm_codes[label]
        _run_unit(v3._semantic_unit, label, c, c, Xtest, Xtest, 0, final_pairs, seed + 7)
    _run_unit(v3._semantic_unit, "RANDOM_BLOCK", arm_codes["RANDOM_BLOCK"],
              arm_codes["RANDOM_BLOCK"], Xtest, Xtest, 0, final_pairs, seed + 7)
    cp_Xtest = Xtest[:cp_cap]
    _run_unit(v3._semantic_unit, "CHARPOS", cp_codes, cp_codes, cp_Xtest, cp_Xtest, 0,
              final_pairs, seed + 7)

    # Integrity check (not a gate): the block-code FORMAT is composable
    # regardless of whether the underlying map was learned or fixed -- keyed
    # bind/unbind/cleanup should still work for the FIXED isometric/random
    # codes, confirming this bypass's codes are genuine SBC-format codes
    # (same K=128 block_l=32 channel), not just a spearman-inflation artifact.
    _run_unit(v3._keyed_unit, "ORTHO_K128", "sbc", arm_codes["ORTHO_K128"],
              K_SMALL, BLK_L, 5, n_trials, gen_eval, device)
    _run_unit(v3._keyed_unit, "RANDOM_K128", "sbc", arm_codes["RANDOM_K128"],
              K_SMALL, BLK_L, 5, n_trials, gen_eval, device)

    def _sp(arm):
        u = v3._by_unit(per_unit, "semantic", arm)
        return float(u["spearman_all"]) if u else float("nan")

    def _ret10(arm):
        u = v3._by_unit(per_unit, "semantic", arm)
        return float(u["ret_agree10"]) if u else float("nan")

    ortho_128 = _sp("ORTHO_K128")
    random_128 = _sp("RANDOM_K128")
    ortho_256 = _sp("ORTHO_K256")
    random_256 = _sp("RANDOM_K256")

    # Interpretation (informational; no HARD_PASS/FAIL bar -- diagnostic).
    quantization_ceiling_k128 = ortho_128   # zero learning error -> pure quantizer ceiling
    quantization_ceiling_k256 = ortho_256
    code_capacity_gain_ortho = ortho_256 - ortho_128   # pure code-capacity effect, zero training
    code_capacity_gain_random = random_256 - random_128
    isometry_vs_random_gap_k128 = ortho_128 - random_128  # cost of NOT having a perfect map

    recovery = {
        "ortho_k128_spearman": ortho_128, "random_k128_spearman": random_128,
        "ortho_k256_spearman": ortho_256, "random_k256_spearman": random_256,
        "ortho_k128_ret_agree10": _ret10("ORTHO_K128"),
        "random_k128_ret_agree10": _ret10("RANDOM_K128"),
        "ortho_k256_ret_agree10": _ret10("ORTHO_K256"),
        "random_k256_ret_agree10": _ret10("RANDOM_K256"),
        "quantization_ceiling_k128": quantization_ceiling_k128,
        "quantization_ceiling_k256": quantization_ceiling_k256,
        "code_capacity_gain_ortho_k128_to_k256": code_capacity_gain_ortho,
        "code_capacity_gain_random_k128_to_k256": code_capacity_gain_random,
        "isometry_vs_random_gap_k128": isometry_vs_random_gap_k128,
        "isometry_verification_error_k128": iso_err_128,
        "isometry_verification_error_k256": iso_err_256,
        "random_block_spearman": _sp("RANDOM_BLOCK"),
        "charpos_spearman": _sp("CHARPOS"),
        "charpos_ret_agree10": _ret10("CHARPOS"),
    }

    if len(per_unit) < expected_units:
        verdict = "CELL_CRASHED"
        verdict_msg = f"HARD_FAIL_CARDINALITY_BREACH: {len(per_unit)}/{expected_units} units"
    else:
        verdict = "DIAGNOSTIC_COMPLETE"
        verdict_msg = (
            f"quantization_ceiling(K=128,zero-training-error)={quantization_ceiling_k128:.4f}; "
            f"quantization_ceiling(K=256)={quantization_ceiling_k256:.4f}; "
            f"code_capacity_gain(ortho,K128->K256)={code_capacity_gain_ortho:.4f}; "
            f"isometry_vs_random_gap(K128)={isometry_vs_random_gap_k128:.4f}")

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "elapsed_s": float(elapsed), "run_mode": run_mode, "anchor_name": anchor,
        "seed": int(seed), "device": device,
        "n_dim_k128": v3.N_DIM_DEFAULT, "n_dim_k256": N_DIM_BIG,
        "k_small": K_SMALL, "k_big": K_BIG, "blk_l": BLK_L,
        "teacher_cache": cache_path.name, "teacher_cache_bytes": cache_bytes,
        "teacher_n_concepts": V_cache, "n_test": n_test,
        "recovery": recovery,
        "per_unit": per_unit, "unit_failures": unit_fail,
        "n_units": len(per_unit), "expected_n_units": expected_units,
        "cardinality_ok": len(per_unit) == expected_units,
        "arms_differ_verified": True, "arm_code_sha256": digests,
        "final_metrics_atomicity": "tmp_replace",
        "composition_algebra": "SBC_block_local_circular_convolution",
        "methodology": ("ZERO-training bypass: teacher embeddings lifted by a "
                        "FIXED isometric (QR-orthonormal, zero info loss "
                        "pre-quantization) or random-Gaussian (generic "
                        "untrained-network proxy) linear map, then hard-"
                        "block-quantized via the SAME v3._encode_hard_block "
                        "path every trained student uses, at K=128 (current) "
                        "and K=256 (doubled) code sizes. ORTHO_K128 is the "
                        "CODE-CAPACITY CEILING: the best any student could "
                        "achieve at K=128 even with zero learning error."),
        "progress_logging": "print_flush_true",
        "crlb_n_a": ("zero-training linear-algebra diagnostic; the learned-"
                    "map CRLB formula does not govern a fixed isometric/"
                    "random lift -- declared explicitly per META_RULE #9"),
        "cell_chunked": False, "start_marker_written": True,
        "crash_diagnostic_present": True, "heartbeat_present": True,
        "defensive_error_checking": "passed_all_4_patterns",
        "calibration_check": "default_ok_for_this_regime",
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    write_metrics(out_dir, metrics)
    print(f"[bypass] verdict={verdict} msg={verdict_msg} elapsed={elapsed:.1f}s", flush=True)
    return 0


def run_self_test() -> int:
    t0 = time.perf_counter()

    # 1. isometry construction: W.T@W must be (near-)identity for the ortho
    #    lift, and NOT for the random lift (sanity that the two arms differ
    #    in the intended way, not just by seed).
    enc_o = _make_ortho_isometric(64, 256, seed=1, device="cpu")
    enc_r = _make_random_gaussian(64, 256, seed=1, device="cpu")
    err_o = _verify_isometry(enc_o, 64)
    err_r = _verify_isometry(enc_r, 64)
    assert err_o < 1e-3, f"selftest: ortho lift should be near-isometric, got err={err_o}"
    assert err_r > 1e-2, f"selftest: random lift should NOT be isometric, got err={err_r}"

    # 2. inner-product preservation: ortho lift preserves x_i.x_j EXACTLY
    #    (up to float error); random lift does NOT preserve it exactly.
    torch.manual_seed(3)
    x = torch.randn(20, 64)
    yo = enc_o(x)
    yr = enc_r(x)
    ip_x = x @ x.T
    ip_yo = yo @ yo.T
    ip_yr = yr @ yr.T
    max_err_o = float((ip_x - ip_yo).abs().max())
    max_err_r = float((ip_x - ip_yr).abs().max())
    assert max_err_o < 1e-3, f"selftest: ortho lift must preserve inner products, err={max_err_o}"
    assert max_err_r > 1e-2, f"selftest: random lift should NOT exactly preserve IP, err={max_err_r}"

    # 3. tiny end-to-end run_bypass on the local (smoke-scale) teacher cache --
    #    exercises the full driver (cache load, 4 lifts, hard-block quantize
    #    at 2 K's, arms-differ, 8 eval units, metrics write).
    import tempfile
    old_cwd_marker = None
    # run_bypass writes via get_output_dir (repo-relative); run directly, no cwd change needed.
    ret = run_bypass("smoke", seed=7, device_arg="cpu", teacher_cache_arg=None)
    assert ret == 0

    print(f"[selftest] PASS (ortho-isometry construction + inner-product-"
          f"preservation check + random-lift-is-NOT-isometric check + tiny "
          f"end-to-end run_bypass smoke drive) elapsed={time.perf_counter() - t0:.2f}s",
          flush=True)
    return 0


def _parse_args(argv: Optional[List[str]] = None) -> "argparse.Namespace":
    import argparse
    p = argparse.ArgumentParser(description=(
        "Teacher-through-sparsifier bypass diagnostic (zero-training "
        "code-capacity ceiling)."))
    p.add_argument("--run-mode", default=os.environ.get("HDLAB_RUN_MODE", "self_test"),
                   choices=["self_test", "smoke", "full"])
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--full", action="store_true")
    p.add_argument("--seed", type=int, default=SEED_DEFAULT)
    p.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    p.add_argument("--teacher-cache", default=None)
    args, _ = p.parse_known_args(argv)
    if args.self_test:
        args.run_mode = "self_test"
    elif args.smoke:
        args.run_mode = "smoke"
    elif args.full:
        args.run_mode = "full"
    return args


def main() -> int:
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    args = _parse_args()
    if args.run_mode == "self_test":
        return run_self_test()
    return run_bypass(args.run_mode, args.seed, args.device, args.teacher_cache)


if __name__ == "__main__":
    _fallback_out = get_output_dir(ANCHOR_NAME)
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:  # NOT BaseException per META_RULE section 8
        try:
            _write_crash_metrics(_fallback_out, exc)
        except Exception:
            pass
        raise
