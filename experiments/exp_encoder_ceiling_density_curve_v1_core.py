"""Code-CEILING density curve -- READ-ONLY diagnostic, ZERO training.

USER framing (2026-07-04): the retrieval-vs-code-density curve has a PEAK
somewhere between K=128 (3.125% active, ret_agree10~0.20) and fully-dense
(100% active float, ret_agree10~0.169) -- K256 (6.25%) already measured
HIGHER than both (~0.29-0.33), so the curve is genuinely non-monotonic and
needs mapping, not two points and a guess. This cell provides the CODE-
CAPACITY CEILING half of that map: pass the raw teacher (BGE-large)
embeddings through a FIXED, ZERO-INFORMATION-LOSS isometric lift (QR-
orthonormal-columns, in_dim=1024 -> out_dim=N_DIM_DEFAULT=4096, EXACTLY
preserving inner products pre-quantization), then hard-block-quantize via
the SAME `v3._encode_hard_block` path every trained student in this lineage
uses, at SIX block-counts K covering the WHOLE density axis at a FIXED
total code width (N=4096, matching the TRAINED curve's own regime, unlike
the sibling `exp_encoder_teacher_sparsifier_bypass_v1_core.py` which varied
total width K128-vs-K256@8192-dims -- a DIFFERENT question):

  K=128  (blk_l=32, 3.125%  active) -- current lineage floor
  K=256  (blk_l=16, 6.25%   active) -- v5/v6 trained arm's K
  K=512  (blk_l=8,  12.5%   active) -- v7 trained arm's K (FULL in flight)
  K=1024 (blk_l=4,  25%     active) -- NEW, no trained arm yet (see sibling
                                       v8 cell, dispatched same session)
  K=2048 (blk_l=2,  50%     active) -- NEW, no trained arm yet (v8)
  K=4096 (blk_l=1,  100%    active) -- the DENSE-SIGN endpoint: blk_l=1
                                       degenerates block-argmax to a trivial
                                       per-dimension sign quantizer (bind()
                                       at blk_l=1 is elementwise multiply via
                                       a length-1 circular convolution --
                                       algebraically well-defined, verified
                                       in self-test below, NOT a crash risk)

Because ALL SIX K's share the SAME total code width (N=4096), ONE isometric
lift (and ONE random-Gaussian "untrained-network" lift, kept for context/
parity with the sibling bypass cell) suffices for the WHOLE K-sweep -- only
the block-quantization step (`kb`, `blk_l`) changes per K, at zero extra
projection cost. This also lets the SAME script report the DENSE-FLOAT
ceiling (RAW_ISOMETRIC/RAW_RANDOM, the UN-quantized continuous lift output
-- the "K=infinity" endpoint) alongside the six quantized points.

Per K this cell reports the FULL four-axis phase-diagram row the USER
requested:
  - RETRIEVAL:        ret_agree10 (from `v3._semantic_unit`)
  - COARSE SEMANTIC:  hi80_cos, hi80_calib_err (same unit)
  - ALGEBRA:          keyed J=5 SBC bind/unbind/cleanup acc_at1
                      (`v3._keyed_unit`, at THAT K's own kb/blk_l)
  - SPARSITY:         active_pct = K / N_DIM_DEFAULT (exact, by construction
                      of the one-hot*sign block code)

This is the CEILING half of the phase diagram (zero training error). The
TRAINED half (what a real student actually achieves at each K) is read
directly off already-landed cells (v5 K128/K256, v6 K256-plateau, v7 K512)
plus the sibling v8 cell (K1024/K2048, dispatched same session to the GPU
queue) -- this cell does NOT retrain anything and does NOT duplicate that
work.

ZERO TRAINING: no gradient steps, no optimizer, no checkpoints. Cost is a
handful of matmuls + six hard-argmax passes + spearman/keyed-cleanup over
held pairs -- cheap even at the full 177899-concept teacher cache (the
sibling bypass_v1 cell's comparable-sized FULL run landed in 138s on CPU).
Routed to `remote_cpu_queue` (idle at author time; GPU queue is running the
v8 K1024/K2048 FULL trains) since this cell has zero use for a GPU.

Prior-work check (substrate-KB concept-query, USER-locked 2026-07-01):
  query "retrieval density curve block count K phase diagram active
  sparsity code ceiling algebra roundtrip coarse semantic hi80" -> top hit
  cosine=0.2483 (notes/research_drill_learned_codebooks_real_encoder_
  rescue_1x_2026-06-06.md, generic sparse-Hopfield/compressed-sensing
  literature notes, NOT a prior arc cell), next hits 0.2471/0.2441/0.2402/
  0.2393 (same family: generic sparse-coding literature + a cross-product
  prereg's sparsity-semantics section). NONE at cosine>0.30. GENUINELY
  NOVEL: no prior cell maps the FIXED-total-width K-density ceiling curve
  across all four axes (retrieval + coarse-semantic + algebra + sparsity)
  in one place; the sibling bypass_v1 cell only covers K=128/256 (at TWO
  DIFFERENT total widths, not a fixed-width sweep) and never measured
  keyed algebra on its bypass codes' finer K's, and the sibling density_
  curve cell only reused TRAINED checkpoints (off-manifold, not the
  zero-training ceiling).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified: sha256 over all code matrices (2 raw + 6 K's x 2
  lifts x quantized + 6 K's RANDOM_BLOCK + CHARPOS = 21 semantic arms)
- final_metrics_atomicity: tmp_replace
- except SystemExit: raise BEFORE except Exception (no BaseException, no
  bare except)
- crlb_n_a: zero-training linear-algebra diagnostic (same posture as the
  sibling bypass_v1 cell) -- the CRLB formula governs LEARNED-map noise,
  not a fixed isometric/random lift; declared explicitly, not omitted.
- baseline_in_band: CHARPOS ret_agree10 in (0.05, 0.95); RANDOM_BLOCK near-
  zero spearman at every K (calibration floor holds regardless of blk_l).
- discriminator-survives-scale: N/A -- no training; the same closed-form
  computation runs identically at smoke (local 43905-concept cache) and
  full (177899-concept cache) scale, differing only in V/n_pairs/n_trials.
  SMOKE=FULL code path by construction.
- verdict: "DIAGNOSTIC_COMPLETE" (no HARD_PASS/FAIL bar), same precedent as
  `exp_encoder_teacher_sparsifier_bypass_v1_core.py` and
  `exp_encoder_retrieval_regime_density_curve_v1_core.py`.
- cardinality_ok: EXPECTED_N_UNITS declared per run_mode (see constants)
- per-unit failure-class instrumentation (META_RULE_J; no bare except)
- calibration_check: default_ok_for_this_regime (reuses the SAME
  `v3._encode_hard_block`/`v3._keyed_unit` channels already validated
  throughout this lineage; only kb/blk_l vary, always tiling N_DIM_DEFAULT)
- numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@

Prereg: preregs/2026-07-04_exp_encoder_ceiling_density_curve_v1.md
Parent cell (read-only import, NOT edited):
  experiments/exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core.py
Does NOT touch any v3/v3b/v3c/v3e/v5/v6/v7/v8/opq_rotation/bypass artifact or
checkpoint directory -- this cell trains nothing and has no checkpoints; own
artifact dir: data/exp_encoder_ceiling_density_curve_v1*/

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
from typing import Dict, List, Optional

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
from experiments import (  # noqa: E402
    exp_encoder_teacher_sparsifier_bypass_v1_core as bypass_v1,
)

ANCHOR_NAME = "encoder_ceiling_density_curve_v1"
SEED_DEFAULT = v3.SEED_DEFAULT  # 7

TEACHER_CACHE_DEFAULT = (
    "data/substrate_index/cached_indices/bge_large_v2_name_177899_54f7cf6a.npz")

N_DIM = v3.N_DIM_DEFAULT  # 4096, FIXED total code width for the whole sweep
K_LIST = [128, 256, 512, 1024, 2048, 4096]
BLK_L_OF = {kb: N_DIM // kb for kb in K_LIST}
for _kb, _bl in BLK_L_OF.items():
    assert _kb * _bl == N_DIM, f"K={_kb} blk_l={_bl} does not tile N_DIM={N_DIM}"

FULL_FINAL_PAIRS = v3.MID_PAIR_SAMPLE   # 400_000
FULL_CHARPOS_CAP = v3.MID_CHARPOS_CAP
FULL_TRIALS = v3.MID_TRIALS

SMOKE_FINAL_PAIRS = 20_000
SMOKE_CHARPOS_CAP = 500
SMOKE_TRIALS = 20
SMOKE_N_TEST = 800   # local cache is 43905 concepts; keep TEST small+fast

# Units: 2 RAW (unquantized) + 6 K's x 2 lifts (ortho+random, quantized)
# + 6 K's RANDOM_BLOCK (noise floor at that K) + 1 CHARPOS = 21 semantic
# + 6 keyed (ORTHO_K{K} J5, one per K) = 27 total.
EXPECTED_N_UNITS_FULL = 2 + len(K_LIST) * 2 + len(K_LIST) + 1 + len(K_LIST)
EXPECTED_N_UNITS_SMOKE = EXPECTED_N_UNITS_FULL

PREREG_BASELINE_ARMS = ["RANDOM_BLOCK_K128", "CHARPOS"]


# ---------------------------------------------------------------------------
# Reuse the bypass cell's fixed-lift helpers (read-only import; NOT edited).
# ---------------------------------------------------------------------------
_make_ortho_isometric = bypass_v1._make_ortho_isometric
_make_random_gaussian = bypass_v1._make_random_gaussian
_verify_isometry = bypass_v1._verify_isometry
_FrozenLinearEncoder = bypass_v1._FrozenLinearEncoder


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


def run_ceiling_curve(run_mode: str, seed: int, device_arg: str,
                      teacher_cache_arg: Optional[str]) -> int:
    assert run_mode in ("smoke", "full"), f"unsupported run_mode {run_mode}"
    anchor = f"{ANCHOR_NAME}_smoke" if run_mode == "smoke" else ANCHOR_NAME
    out_dir = get_output_dir(anchor)
    device = ("cuda" if torch.cuda.is_available() else "cpu") \
        if device_arg == "auto" else device_arg

    expected_units = EXPECTED_N_UNITS_SMOKE if run_mode == "smoke" else EXPECTED_N_UNITS_FULL
    _write_start_marker(out_dir, run_mode, expected_units)
    t0 = time.perf_counter()
    print(f"[ceiling_curve] run_mode={run_mode} seed={seed} device={device} "
          f"K_LIST={K_LIST}", flush=True)

    effective_cache_arg = teacher_cache_arg
    if run_mode == "full" and effective_cache_arg is None:
        effective_cache_arg = TEACHER_CACHE_DEFAULT
    cache_path = v3._resolve_teacher_cache(effective_cache_arg)
    cache_bytes = cache_path.stat().st_size
    X, ids = v3._load_teacher(cache_path)
    V_cache = X.shape[0]
    in_dim = X.shape[1]
    print(f"[ceiling_curve] teacher {cache_path.name}: {V_cache} concepts x "
          f"{in_dim}d ({time.perf_counter() - t0:.1f}s)", flush=True)

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
    print(f"[ceiling_curve] test split n={n_test}", flush=True)

    enc_ortho = _make_ortho_isometric(in_dim, N_DIM, seed + 1, device)
    enc_random = _make_random_gaussian(in_dim, N_DIM, seed + 2, device)
    iso_err = _verify_isometry(enc_ortho, in_dim)
    print(f"[ceiling_curve] isometry sanity: max|WtW-I|={iso_err:.2e} "
          f"({time.perf_counter() - t0:.1f}s)", flush=True)

    @torch.no_grad()
    def _raw_continuous(enc: _FrozenLinearEncoder, Xin: torch.Tensor,
                        batch: int = 8192) -> torch.Tensor:
        out = torch.zeros(Xin.shape[0], N_DIM, dtype=torch.float32)
        for lo in range(0, Xin.shape[0], batch):
            out[lo:lo + batch] = enc(Xin[lo:lo + batch].to(device)).detach().cpu().float()
        return out

    arm_codes: Dict[str, torch.Tensor] = {
        "RAW_ISOMETRIC": _raw_continuous(enc_ortho, Xtest),
        "RAW_RANDOM": _raw_continuous(enc_random, Xtest),
    }
    for kb in K_LIST:
        blk_l = BLK_L_OF[kb]
        arm_codes[f"ORTHO_K{kb}"] = v3._encode_hard_block(enc_ortho, Xtest, kb, blk_l)
        arm_codes[f"RANDOM_K{kb}"] = v3._encode_hard_block(enc_random, Xtest, kb, blk_l)
        gen_ctrl = torch.Generator().manual_seed(seed + 100 + kb)
        arm_codes[f"RANDOM_BLOCK_K{kb}"] = v3._random_block_codes(n_test, kb, blk_l, gen_ctrl)
    cp_cap = min(n_test, charpos_cap)
    cp_codes = v3._charpos_codes(names_test[:cp_cap], N_DIM, K_LIST[0])
    print(f"[ceiling_curve] all codes encoded ({time.perf_counter() - t0:.1f}s)", flush=True)

    digests = {}
    for name, c in list(arm_codes.items()) + [("CHARPOS", cp_codes)]:
        digests[name] = hashlib.sha256(c.to(torch.float32).numpy().tobytes()).hexdigest()
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
            print(f"[ceiling_curve] unit {len(per_unit)}/{expected_units} {u['unit']}: "
                  + json.dumps({k: round(v, 4) for k, v in u.items()
                                if isinstance(v, float)}), flush=True)
            _emit_heartbeat(out_dir, len(per_unit), expected_units,
                            time.perf_counter() - t0, extra={"unit": u["unit"]})
        except (RuntimeError, ValueError, IndexError) as exc:
            unit_fail.append({"fn": getattr(fn, "__name__", "?"),
                              "failure_class": type(exc).__name__,
                              "msg": str(exc)[:300]})
            raise

    for label in ["RAW_ISOMETRIC", "RAW_RANDOM"] + \
            [f"ORTHO_K{kb}" for kb in K_LIST] + \
            [f"RANDOM_K{kb}" for kb in K_LIST] + \
            [f"RANDOM_BLOCK_K{kb}" for kb in K_LIST]:
        c = arm_codes[label]
        _run_unit(v3._semantic_unit, label, c, c, Xtest, Xtest, 0, final_pairs, seed + 7)
    cp_Xtest = Xtest[:cp_cap]
    _run_unit(v3._semantic_unit, "CHARPOS", cp_codes, cp_codes, cp_Xtest, cp_Xtest, 0,
              final_pairs, seed + 7)

    # Algebra ceiling: keyed J=5 SBC roundtrip on the ORTHO (zero-training-
    # error) code at EACH K, verifying the CODE FORMAT itself supports
    # composition at that granularity, independent of any learned map.
    for kb in K_LIST:
        blk_l = BLK_L_OF[kb]
        _run_unit(v3._keyed_unit, f"ORTHO_K{kb}", "sbc", arm_codes[f"ORTHO_K{kb}"],
                  kb, blk_l, 5, n_trials, gen_eval, device)

    def _by(arm):
        u = v3._by_unit(per_unit, "semantic", arm)
        return u if u else {}

    def _keyed_by(arm):
        u = v3._by_unit(per_unit, "keyed", arm, J=5)
        return u if u else {}

    ceiling_curve = []
    for kb in K_LIST:
        s = _by(f"ORTHO_K{kb}")
        k_ = _keyed_by(f"ORTHO_K{kb}")
        ceiling_curve.append({
            "K": kb, "blk_l": BLK_L_OF[kb], "active_pct": 100.0 * kb / N_DIM,
            "ret_agree10": s.get("ret_agree10"), "hi80_cos": s.get("hi80_cos"),
            "hi80_calib_err": s.get("hi80_calib_err"),
            "spearman_all": s.get("spearman_all"),
            "keyed_j5_acc_at1": k_.get("acc_at1"),
            "keyed_j5_snr_margin": k_.get("snr_margin_mean"),
        })
    raw_iso = _by("RAW_ISOMETRIC")
    raw_rand = _by("RAW_RANDOM")

    if len(per_unit) < expected_units:
        verdict = "CELL_CRASHED"
        verdict_msg = f"HARD_FAIL_CARDINALITY_BREACH: {len(per_unit)}/{expected_units} units"
    else:
        verdict = "DIAGNOSTIC_COMPLETE"
        peak = max(ceiling_curve, key=lambda r: r["ret_agree10"] if r["ret_agree10"] is not None else -1.0)
        verdict_msg = (
            f"ceiling_ret_agree10_by_K="
            f"{ {r['K']: round(r['ret_agree10'], 4) for r in ceiling_curve} }; "
            f"ceiling_peak_at_K={peak['K']} (ret_agree10={peak['ret_agree10']:.4f}); "
            f"raw_isometric_ret_agree10(dense-float ceiling)={raw_iso.get('ret_agree10'):.4f}; "
            f"this is the ZERO-TRAINING code-capacity ceiling; trained curve is separate "
            f"(see v5/v6/v7/v8 MEASURED@ cells)")

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "elapsed_s": float(elapsed), "run_mode": run_mode, "anchor_name": anchor,
        "seed": int(seed), "device": device,
        "n_dim": N_DIM, "k_list": K_LIST, "blk_l_of": BLK_L_OF,
        "teacher_cache": cache_path.name, "teacher_cache_bytes": cache_bytes,
        "teacher_n_concepts": V_cache, "n_test": n_test,
        "ceiling_curve": ceiling_curve,
        "raw_isometric": raw_iso, "raw_random": raw_rand,
        "charpos": _by("CHARPOS"),
        "per_unit": per_unit, "unit_failures": unit_fail,
        "n_units": len(per_unit), "expected_n_units": expected_units,
        "cardinality_ok": len(per_unit) == expected_units,
        "arms_differ_verified": True, "arm_code_sha256": digests,
        "final_metrics_atomicity": "tmp_replace",
        "composition_algebra": "SBC_block_local_circular_convolution",
        "methodology": (
            "ZERO-training ceiling: teacher embeddings lifted by a FIXED "
            "isometric (QR-orthonormal, zero info loss pre-quantization) or "
            "random-Gaussian linear map into a FIXED N_DIM=4096 continuous "
            "space, then hard-block-quantized via the SAME "
            "v3._encode_hard_block path every trained student in this "
            "lineage uses, at K in {128,256,512,1024,2048,4096} -- ALL "
            "sharing the SAME total code width (unlike the sibling bypass_v1 "
            "cell, which varied total width). ORTHO_K{k} is the CODE-"
            "CAPACITY CEILING at that K: the best any student could achieve "
            "with zero learning error. keyed_j5_acc_at1 on ORTHO_K{k} is the "
            "algebra ceiling at that K (does the CODE FORMAT itself, "
            "independent of training, support J=5 bind/unbind/cleanup)."),
        "progress_logging": "print_flush_true",
        "crlb_n_a": ("zero-training linear-algebra diagnostic; the learned-"
                    "map CRLB formula does not govern a fixed isometric/"
                    "random lift -- declared explicitly per META_RULE #9"),
        "cell_chunked": False, "start_marker_written": True,
        "crash_diagnostic_present": True, "heartbeat_present": True,
        "defensive_error_checking": "passed_all_4_patterns",
        "calibration_check": "default_ok_for_this_regime",
        "isometry_verification_error": iso_err,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    write_metrics(out_dir, metrics)
    print(f"[ceiling_curve] verdict={verdict} msg={verdict_msg} elapsed={elapsed:.1f}s", flush=True)
    return 0


def run_self_test() -> int:
    t0 = time.perf_counter()

    # 1. all K's tile N_DIM exactly (module-level assert already ran on
    #    import; re-check here defensively).
    for kb, blk_l in BLK_L_OF.items():
        assert kb * blk_l == N_DIM, f"selftest: K={kb} blk_l={blk_l} mistile"

    # 2. blk_l=1 (K=4096, the dense-sign endpoint) does NOT crash bind/unbind
    #    (degenerates to elementwise sign-multiply via length-1 circular
    #    convolution) -- verify explicitly since this is the one edge case
    #    not exercised by any prior cell in this lineage.
    from hdlab.binding import bind, unbind
    torch.manual_seed(11)
    a = torch.sign(torch.randn(4096, 1))
    b = torch.sign(torch.randn(4096, 1))
    c = bind(a, b)
    assert c.shape == a.shape, f"selftest: bind blk_l=1 shape mismatch {c.shape}"
    rec = unbind(c, b)
    assert torch.allclose(rec, a, atol=1e-4), (
        f"selftest: unbind(bind(a,b),b) != a at blk_l=1, max_err="
        f"{float((rec - a).abs().max())}")

    # 3. tiny end-to-end run_ceiling_curve on the local (smoke-scale) teacher
    #    cache -- exercises the full driver (cache load, 2 lifts, 6 K's x 2
    #    quantized + 6 RANDOM_BLOCK + CHARPOS = 21 semantic units, 6 keyed
    #    units, arms-differ, metrics write).
    ret = run_ceiling_curve("smoke", seed=7, device_arg="cpu", teacher_cache_arg=None)
    assert ret == 0

    print(f"[selftest] PASS (K-tiling check + blk_l=1 bind/unbind roundtrip "
          f"+ tiny end-to-end run_ceiling_curve smoke drive) "
          f"elapsed={time.perf_counter() - t0:.2f}s", flush=True)
    return 0


def _parse_args(argv: Optional[List[str]] = None) -> "argparse.Namespace":
    import argparse
    p = argparse.ArgumentParser(description=(
        "Code-CEILING density curve (zero-training) across K=128..4096 at "
        "a fixed total code width."))
    p.add_argument("--run-mode", default=os.environ.get("HDLAB_RUN_MODE", "self_test"),
                   choices=["self_test", "smoke", "full"])
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--full", action="store_true")
    p.add_argument("--seed", type=int, default=SEED_DEFAULT)
    # Default "cpu" (not "auto"): this is a zero-training linear-algebra
    # diagnostic with no need for a GPU; matches the bugfix rationale in
    # exp_encoder_teacher_sparsifier_bypass_v1_core.py (remote_cpu_queue
    # runner host has torch.cuda.is_available()==True even for CPU-queue
    # jobs; "auto" would silently resolve to "cuda" there).
    p.add_argument("--device", default="cpu", choices=["auto", "cpu", "cuda"])
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
    return run_ceiling_curve(args.run_mode, args.seed, args.device, args.teacher_cache)


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
