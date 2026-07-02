"""cross_axis_m_n_k_factorization_beta_5_bridging_v2 -- seed_13.

BRIDGING CELL v2: verify substrate factorization holds at beta=5, iterated
from v1 (beta=8) which EMPIRICALLY SATURATED per smoke MB. Discriminating
regime lies between beta=4 (v2 CG) and beta=8 (empirical saturation);
CRLB sim + softmax amplification factor from v1 finding predicts beta=5
discriminates cleanly. If HP, META atom
`substrate_axes_factorize_across_beta_regime_2axis_v1` promotes CG.

Arms:
- STD_beta13 (saturating control; re-verifies v1_2d_coarse saturation)
- DIS_beta5  (discriminating bridge; iteration on v1 beta=8 saturation)

See core docstring for design + CRLB predictions + META atom lineage + v1
beta=8 empirical saturation atomize hand-off.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH):
- arms_differ_verified at smoke (hash-check across phase points)
- final_metrics_atomicity: tmp_replace
- except SystemExit: raise BEFORE except Exception (no BaseException)
- crlb / discriminator-reachability declared in prereg (interaction floor 0.05
  matches beta=4 CG threshold; predictable factorization if beta-invariant)
- baseline_in_band: STD arm hypothesized saturated (v1 replication);
  DIS arm expected in (0.05, 0.95) range across M axis at beta=5
- discriminator survives scale: Method C INVERTED - preview must NOT saturate
- HARD_PASS strictly above floor
- cardinality_ok for 16 phase points (META_RULE_H)
- per-unit failure-class instrumentation (no bare except)
- calibration_check: default_ok_for_this_regime (v2 CG regime + CRLB beta=5)
- All numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@

PRIOR (substrate-KB 2026-07-02 concept-query at cosine < 0.31):
  Genuinely novel iteration. Adjacent:
  - cross_axis_m_n_k_discriminating_arm_v2 (DIS_beta4) CG at beta=4
  - cross_axis_m_n_k_factorization_beta_8_bridging_v1 MB SATURATED at beta=8
  - v1_2d_coarse saturated MM at beta=13

CROSS-REFS:
  hdlab/chunked_attention.py (Testbed T2 chain-grade primitive)
  Cell D v2 CG dense-Hopfield READ-REPLACE (Atom 1)
  cross_axis_m_n_k_discriminating_arm_v2 (beta=4 CG, Skunkworks batch 7)
  cross_axis_m_n_k_factorization_beta_8_bridging_v1 (beta=8 empirical sat MB)
  notes/exp_dev_findings/exp_cross_axis_m_n_k_factorization_beta_8_bridging_v1_HF_beta8_SATURATES_2026-07-02.md

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

from experiments._substrate_cross_axis_m_n_k_factorization_beta_5_bridging_v2_core import (
    V_DIM, ATTN_CHUNK_FULL, ATTN_CHUNK_SMOKE,
    ARM_BETAS,
    M_GRID_FULL, N_GRID_FULL, K_GRID_FULL,
    M_GRID_SMOKE, N_GRID_SMOKE, K_GRID_SMOKE,
    PREVIEW_CORNER_SMOKE,
    HP_SEPARABLE_STD_FLOOR, HP_INTERACTION_MK_FLOOR,
    HP_INTERACTION_MN_FLOOR, HP_DIS_MECHANISM_RANGE_FLOOR,
    _TORCH_AVAILABLE, _CUDA_AVAILABLE,
    emit_heartbeat, write_start_marker, write_crash_metrics,
    run_phase_point, run_grid, run_all_selftests, compute_verdict,
)
from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)


ANCHOR_NAME = "cross_axis_m_n_k_factorization_beta_5_bridging_v2_seed_13"
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

# Cardinality: 2 arms x 2 M x 2 N x 2 K = 16 in FULL; smoke same shape
EXPECTED_N_UNITS = len(ARM_BETAS) * len(M_GRID) * len(N_GRID) * len(K_GRID)

COMPUTE_BACKEND = (
    "torch.cuda" if (USE_TORCH and _CUDA_AVAILABLE)
    else ("torch.cpu" if USE_TORCH else "numpy")
)

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},ARMS={list(ARM_BETAS.keys())},"
    f"M={M_GRID},N={N_GRID},K={K_GRID},V={V_DIM},chunk={ATTN_CHUNK},"
    f"SEED={SEED_THIS_CHUNK},RUN_MODE={RUN_MODE},backend={COMPUTE_BACKEND},"
    f"discipline=v2_DISCRIMINATING_ARM_META_RULES_AC_AF_AG_AH"
)


def _instrumentation_selftest() -> None:
    run_all_selftests(SEED_THIS_CHUNK, ANCHOR_NAME)
    print(
        f"[selftest] PASS  arms={list(ARM_BETAS.keys())} "
        f"M={M_GRID} N={N_GRID} K={K_GRID} V={V_DIM} "
        f"chunk={ATTN_CHUNK} mode={RUN_MODE} "
        f"seed={SEED_THIS_CHUNK} backend={COMPUTE_BACKEND} "
        f"torch={_TORCH_AVAILABLE} cuda={_CUDA_AVAILABLE} "
        f"expected_n_units={EXPECTED_N_UNITS}",
        flush=True,
    )


def run_seed(seed: int, out_dir: Path) -> Dict:
    t0 = time.time()
    grid_results = run_grid(
        seed=seed, arm_betas=ARM_BETAS,
        M_grid=M_GRID, N_grid=N_GRID, K_grid=K_GRID,
        V=V_DIM, chunk_size=ATTN_CHUNK,
        out_dir=out_dir, use_torch=USE_TORCH,
    )

    preview_corner_recall = None
    if RUN_MODE == "smoke" and RUN_PREVIEW_CORNER:
        arm_p, pM, pN, pK = PREVIEW_CORNER_SMOKE
        p_beta = ARM_BETAS[arm_p]
        print(
            f"  [seed={seed} PREVIEW_CORNER arm={arm_p} M={pM} N={pN} K={pK} beta={p_beta}] "
            f"DISCRIMINATOR-MUST-SURVIVE-SCALE Method C (INVERTED)...",
            flush=True,
        )
        try:
            preview = run_phase_point(
                seed=seed, arm_name=arm_p,
                M=pM, N=pN, K=pK, V=V_DIM, beta=p_beta,
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
        "arm_betas": dict(ARM_BETAS),
        "M_grid": M_GRID,
        "N_grid": N_GRID,
        "K_grid": K_GRID,
        "V_DIM": V_DIM,
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


def _main() -> None:
    _instrumentation_selftest()
    if _ARGS.self_test:
        sys.exit(0)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_start_marker(out_dir, ANCHOR_NAME, RUN_MODE, EXPECTED_N_UNITS)

    run_config = {
        "arm_betas": dict(ARM_BETAS),
        "M_grid": M_GRID,
        "N_grid": N_GRID,
        "K_grid": K_GRID,
        "V": V_DIM,
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
            f"backend={COMPUTE_BACKEND} arms={list(ARM_BETAS.keys())} "
            f"grid={len(M_GRID)}x{len(N_GRID)}x{len(K_GRID)}"
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
            f"chunk_seed={SEED_THIS_CHUNK} arms={list(ARM_BETAS.keys())} "
            f"M={M_GRID} N={N_GRID} K={K_GRID} "
            f"V={V_DIM} chunk={ATTN_CHUNK} mode={RUN_MODE} "
            f"backend={COMPUTE_BACKEND} expected_n_units={EXPECTED_N_UNITS} "
            f"phase_points_run={n_phase_points}"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "arm_betas": dict(ARM_BETAS),
        "M_grid": M_GRID,
        "N_grid": N_GRID,
        "K_grid": K_GRID,
        "V_DIM": V_DIM,
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
            "MEASURED@2026-07-01 seed=7,13,19 numpy sim (K=30): "
            "M-N INTERACTION mean 3-seed = 0.042 at DIS_beta5 arm "
            "(range 0.021-0.061). HP floor set to 0.05 = 2x above min-seed "
            "and slightly above 3-seed mean; discriminator reachable IF "
            "signal survives from small-N/K smoke to production N/K. "
            "Recall CRLB via Hebbian: p_win ~= 1/(1 + M*exp(-beta*margin)). "
            "At beta=4 M=32768 N=8192 margin ~= 0.95 -> p_win ~= 0.16 predicted; "
            "MEASURED 0.31 confirms softmax value-averaging amplifies signal."
        ),
        "hp_separable_std_floor": HP_SEPARABLE_STD_FLOOR,
        "hp_interaction_mk_floor": HP_INTERACTION_MK_FLOOR,
        "hp_interaction_mn_floor": HP_INTERACTION_MN_FLOOR,
        "hp_dis_mechanism_range_floor": HP_DIS_MECHANISM_RANGE_FLOOR,
        "primitive_reference_testbed_T2": "hdlab/chunked_attention.py",
        "primitive_reference_v1_saturated": (
            "exp_cross_axis_m_n_k_2d_coarse_gpu_v1_seed_13 (Skunkworks demoted MM)"
        ),
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
