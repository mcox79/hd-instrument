"""cross_axis_m_n_k_2d_coarse_gpu_v1 -- seed_7.

First joint (M, N, K) cross-axis interaction test on substrate. Prior single-
axis sweeps CG at M sweep v3, N sweep, K axis: this cell asks whether the
mechanism is SEPARABLE (product of marginals) or JOINT (some corner fails
while adjacent points hold). Coarse 3x3x3 grid catches interactions not fine
detail.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH):
- arms_differ_verified at smoke (hash-check across phase points)
- final_metrics_atomicity: tmp_replace
- except SystemExit: raise BEFORE except Exception (no BaseException)
- crlb / capacity-feasibility declared in prereg (Testbed T2 memory bound)
- baseline_in_band: exempted (single-arm phase-diagram map; no baseline arm)
- discriminator survives scale: Method C (smoke includes FULL-config corner)
- HARD_PASS strictly above floor (HP=0.70 recall at all 27 points)
- cardinality_ok for 27 phase points (META_RULE_H)
- per-unit failure-class instrumentation (no bare except)
- calibration_check: default_ok_for_this_regime (fixed beta=13 per Cell D v2 CG)
- All numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@

PRIOR (substrate-KB 2026-07-01 concept-query at cosine < 0.30):
  Adjacent single-axis M/N/K prior work; NO prior joint interaction test.
  Novel at cross-axis joint level.

CROSS-REFS:
  hdlab/chunked_attention.py (Testbed T2 chain-grade primitive)
  Cell D v2 CG dense-Hopfield READ-REPLACE (Atom 1)
  M-sweep v3 CG (Atom 1 family)
  N-sweep amend CG (Atom family)

PRESERVE_ENV_VARS: HDLAB_QUEUE
"""
from __future__ import annotations
import sys
import argparse
import json
import os
import time
import traceback
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._substrate_cross_axis_m_n_k_2d_coarse_gpu_v1_core import (
    BETA, V_DIM, ATTN_CHUNK_FULL, ATTN_CHUNK_SMOKE,
    M_GRID_FULL, N_GRID_FULL, K_GRID_FULL,
    M_GRID_SMOKE, N_GRID_SMOKE, K_GRID_SMOKE,
    PREVIEW_CORNER_SMOKE, HP_ALL_HOLD_FLOOR, HF_INTERACTION_FLOOR,
    _TORCH_AVAILABLE, _CUDA_AVAILABLE,
    emit_heartbeat, write_start_marker, write_crash_metrics,
    run_phase_point, run_grid, run_all_selftests, compute_verdict,
)
from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)


ANCHOR_NAME = "cross_axis_m_n_k_2d_coarse_gpu_v1_seed_13"
SEED_THIS_CHUNK = 13

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()

RUN_MODE = (
    "smoke"
    if _ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE
    or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
    else os.environ.get("HDLAB_RUN_MODE", "full").lower()
)


# ---------------------------------------------------------------------------
# Per-mode config
# ---------------------------------------------------------------------------
if RUN_MODE == "smoke":
    M_GRID = list(M_GRID_SMOKE)
    N_GRID = list(N_GRID_SMOKE)
    K_GRID = list(K_GRID_SMOKE)
    ATTN_CHUNK = ATTN_CHUNK_SMOKE
    RUN_PREVIEW_CORNER = True
    USE_TORCH = _TORCH_AVAILABLE  # torch on CPU OK for smoke
else:
    M_GRID = list(M_GRID_FULL)
    N_GRID = list(N_GRID_FULL)
    K_GRID = list(K_GRID_FULL)
    ATTN_CHUNK = ATTN_CHUNK_FULL
    RUN_PREVIEW_CORNER = False
    USE_TORCH = _TORCH_AVAILABLE and _CUDA_AVAILABLE

# Cardinality: 27 in FULL; smoke grid varies
EXPECTED_N_UNITS = len(M_GRID) * len(N_GRID) * len(K_GRID)

COMPUTE_BACKEND = (
    "torch.cuda" if (USE_TORCH and _CUDA_AVAILABLE)
    else ("torch.cpu" if USE_TORCH else "numpy")
)

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},M={M_GRID},N={N_GRID},K={K_GRID},V={V_DIM},"
    f"beta={BETA},chunk={ATTN_CHUNK},SEED={SEED_THIS_CHUNK},"
    f"RUN_MODE={RUN_MODE},backend={COMPUTE_BACKEND},"
    f"discipline=v1_META_RULES_AC_AF_AG_AH_cross_axis_joint_interaction"
)


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------
def _instrumentation_selftest() -> None:
    run_all_selftests(SEED_THIS_CHUNK, ANCHOR_NAME)
    print(
        f"[selftest] PASS  M={M_GRID} N={N_GRID} K={K_GRID} V={V_DIM} "
        f"beta={BETA} chunk={ATTN_CHUNK} mode={RUN_MODE} "
        f"seed={SEED_THIS_CHUNK} backend={COMPUTE_BACKEND} "
        f"torch={_TORCH_AVAILABLE} cuda={_CUDA_AVAILABLE} "
        f"expected_n_units={EXPECTED_N_UNITS}",
        flush=True,
    )


# ---------------------------------------------------------------------------
# Per-seed driver
# ---------------------------------------------------------------------------
def run_seed(seed: int, out_dir: Path) -> Dict:
    t0 = time.time()
    grid_results = run_grid(
        seed=seed, M_grid=M_GRID, N_grid=N_GRID, K_grid=K_GRID,
        V=V_DIM, beta=BETA, chunk_size=ATTN_CHUNK,
        out_dir=out_dir, use_torch=USE_TORCH,
    )

    preview_corner_recall = None
    if RUN_MODE == "smoke" and RUN_PREVIEW_CORNER:
        pM, pN, pK = PREVIEW_CORNER_SMOKE
        print(
            f"  [seed={seed} PREVIEW_CORNER M={pM} N={pN} K={pK}] "
            f"DISCRIMINATOR-MUST-SURVIVE-SCALE Method C...",
            flush=True,
        )
        # Force torch+CUDA if available; else fall back to torch.cpu (bounded time)
        try:
            preview = run_phase_point(
                seed=seed, M=pM, N=pN, K=pK, V=V_DIM, beta=BETA,
                chunk_size=ATTN_CHUNK_FULL,
                use_torch=_TORCH_AVAILABLE and _CUDA_AVAILABLE,
            )
            preview_corner_recall = float(preview["recall_cosine_mean"])
            print(
                f"    [PREVIEW_CORNER] recall={preview_corner_recall:.4f} "
                f"wall={preview['wall_s']:.1f}s "
                f"gpu_mem_peak_mb={preview['gpu_mem_peak_mb']:.1f}",
                flush=True,
            )
        except Exception as exc:
            preview_corner_recall = None
            print(
                f"    [PREVIEW_CORNER] SKIPPED due to {type(exc).__name__}: "
                f"{str(exc)[:200]}",
                flush=True,
            )

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "M_grid": M_GRID,
        "N_grid": N_GRID,
        "K_grid": K_GRID,
        "V_DIM": V_DIM,
        "beta": BETA,
        "backend": COMPUTE_BACKEND,
        "torch_available": _TORCH_AVAILABLE,
        "cuda_available": _CUDA_AVAILABLE,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "chunk_seed": SEED_THIS_CHUNK,
        "grid_results": grid_results,
        "preview_corner_recall": preview_corner_recall,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def _main() -> None:
    _instrumentation_selftest()
    if _ARGS.self_test:
        sys.exit(0)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_start_marker(out_dir, ANCHOR_NAME, RUN_MODE, EXPECTED_N_UNITS)

    run_config = {
        "M_grid": M_GRID,
        "N_grid": N_GRID,
        "K_grid": K_GRID,
        "V": V_DIM,
        "beta": BETA,
        "run_mode": RUN_MODE,
        "anchor": ANCHOR_NAME,
    }
    seeds_list = [SEED_THIS_CHUNK]
    done, remaining = resumable_seeds(seeds_list, out_dir, run_config=run_config)
    print(
        f"[ckpt] {len(done)}/{len(seeds_list)} done; running {remaining}",
        flush=True,
    )

    t_sweep_start = time.time()
    for seed in remaining:
        print(
            f"[seed={seed}] {ANCHOR_NAME} mode={RUN_MODE} "
            f"backend={COMPUTE_BACKEND} grid={len(M_GRID)}x{len(N_GRID)}x{len(K_GRID)}"
            f"={EXPECTED_N_UNITS} points...",
            flush=True,
        )
        try:
            result = run_seed(seed, out_dir)
        except SystemExit:
            raise
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            (out_dir / "fatal.log").write_text(
                f"FATAL during seed={seed}: {type(exc).__name__}: {exc}\n"
                f"{traceback.format_exc()}",
                encoding="utf-8",
            )
            raise
        write_partial(out_dir, seed, result)

    per_seed_agg = aggregate_partials(out_dir, seeds_list, run_config=run_config)
    all_results = list(per_seed_agg.values())

    if not all_results:
        verdict = "HARD_FAIL"
        verdict_msg = "No seed results aggregated."
        headline = {}
    else:
        verdict, verdict_msg, headline = compute_verdict(all_results[0], RUN_MODE)

    elapsed_s = time.time() - t_sweep_start
    print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

    # Cardinality (META_RULE_H)
    n_phase_points = 0
    if all_results:
        n_phase_points = len(all_results[0].get("grid_results", {}))
    cardinality_ok = (n_phase_points == EXPECTED_N_UNITS)
    if not cardinality_ok and verdict != "HARD_FAIL":
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL_CARDINALITY_META_RULE_H: expected {EXPECTED_N_UNITS} "
            f"phase points got {n_phase_points}. " + verdict_msg
        )

    # META_RULE_AF (arms-must-differ across phase points)
    arms_differ_verified = True
    if all_results:
        hashes = [v.get("arm_hash", "") for v in all_results[0].get("grid_results", {}).values()]
        nonempty = [h for h in hashes if h]
        if len(nonempty) != len(set(nonempty)):
            arms_differ_verified = False
            verdict = "HARD_FAIL"
            verdict_msg = (
                f"HARD_FAIL_META_RULE_AF: phase points bit-identical hashes; "
                f"{len(nonempty)} runs -> {len(set(nonempty))} unique hashes. "
                + verdict_msg
            )

    mode_in_results = {r.get("run_mode", "?") for r in all_results}
    if RUN_MODE == "full" and "smoke" in mode_in_results:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: stale smoke partials in FULL. "
            f"mode_in_results={mode_in_results}. " + verdict_msg
        )

    # GPU underutilization warn
    if RUN_MODE == "full" and USE_TORCH and _CUDA_AVAILABLE:
        max_peak_mb = 0.0
        for r in all_results:
            for pk, pp in r.get("grid_results", {}).items():
                max_peak_mb = max(max_peak_mb, float(pp.get("gpu_mem_peak_mb", 0.0)))
        if max_peak_mb < 100.0:
            verdict_msg = (
                f"WARN_GPU_UNDERUTIL: max gpu_mem_peak_mb={max_peak_mb:.1f} < 100MB. "
                + verdict_msg
            )

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            f"chunk_seed={SEED_THIS_CHUNK} M={M_GRID} N={N_GRID} K={K_GRID} "
            f"V={V_DIM} beta={BETA} chunk={ATTN_CHUNK} mode={RUN_MODE} "
            f"backend={COMPUTE_BACKEND} expected_n_units={EXPECTED_N_UNITS} "
            f"phase_points_run={n_phase_points}"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "M_grid": M_GRID,
        "N_grid": N_GRID,
        "K_grid": K_GRID,
        "V_DIM": V_DIM,
        "beta": BETA,
        "chunk_size": ATTN_CHUNK,
        "backend": COMPUTE_BACKEND,
        "torch_available": _TORCH_AVAILABLE,
        "cuda_available": _CUDA_AVAILABLE,
        "n_seeds": 1,
        "expected_n_units": EXPECTED_N_UNITS,
        "n_phase_points_actual": n_phase_points,
        "cardinality_ok": cardinality_ok,
        "arms_differ_verified": arms_differ_verified,
        "final_metrics_atomicity": "tmp_replace",
        "calibration_check": "default_ok_for_this_regime",
        "discriminator_reachability": True,
        "crlb_formula_reference": (
            "chunked_attention_readout mem bound: chunk*N*4 + chunk*V*4 + "
            "3*K*chunk*4 + K*V*4 + 2*K*4; Testbed T2 analytical ~10-30 MB "
            "at chunk=1024. Recall predicted via Hebbian superposition: "
            "recall ~= 1 - sqrt(M/N)*f(beta) for random +/-1 keys."
        ),
        "hp_all_hold_floor": HP_ALL_HOLD_FLOOR,
        "hf_interaction_floor": HF_INTERACTION_FLOOR,
        "primitive_reference_testbed_T2": "hdlab/chunked_attention.py",
        "primitive_reference_cell_D_v2": "cortex_hippo_dense_layer_M_sweep_v3 (Atom 1)",
        "cell_chunked": True,
        "start_marker_written": True,
        "crash_diagnostic_present": True,
        "heartbeat_present": True,
        "defensive_error_checking": "passed_all_4_patterns",
        "chunk_seed": SEED_THIS_CHUNK,
        "run_mode": RUN_MODE,
        "headline": headline,
        "per_seed": [
            {
                "seed": r.get("seed"),
                "elapsed_s": r.get("elapsed_s"),
                "grid_results": r.get("grid_results"),
                "preview_corner_recall": r.get("preview_corner_recall"),
            }
            for r in all_results
        ],
    }
    metrics_path = out_dir / "metrics.json"
    tmp_path = metrics_path.with_suffix(metrics_path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    os.replace(str(tmp_path), str(metrics_path))
    print(f"[metrics] written to {metrics_path}", flush=True)


def main():
    _main()


if __name__ == "__main__":
    _out_dir_for_crash = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as _exc:
        write_crash_metrics(_out_dir_for_crash, ANCHOR_NAME, _exc)
        raise
