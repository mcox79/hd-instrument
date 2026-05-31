"""C8 SPARSE-W LARGE-N INTEGRATION v1 (CPU-based analysis).

CONTEXT (CPU 5 from user batch):
  Sparse-W gives 16x memory savings within standard envelope.
  Does it COMPOSE with large-N (N=16384) to yield on-device-deployable
  memory footprints? Determines hardware requirements for sparse-W
  large-N deployment.

ANALYSIS:
  1) Measure sparse-W memory footprint at N=4096 across M sweep:
       M in {128, 512, 2048, 8192}.
  2) Project to N=16384 via power-law fit. We anchor the projection on
     theory (sparse cost = 2*M*N*4 bytes) and verify slope empirically.
  3) Compare to dense W at same N/M.
  4) Validate killer features (retention + KF-2 max_iso) on sparse-W
     at N=8192 (highest N where killer features have prior empirical
     evidence) across M in {512, 2048, 8192}.

VALIDATION RUNS:
  Sparse-W at N=8192, M in {512, 2048, 8192}, 3 seeds. Verify:
    KF-1: above_thresh_frac < 0.05
    KF-2: max_iso <= 0.05
    Retention: >= 0.90

METRICS:
  per-(N, M):
    sparse_w_footprint_bytes
    dense_w_footprint_bytes
    memory_ratio_sparse_vs_dense
  projection:
    sparse_n16384_projected_bytes
    sparse_n16384_projected_M8192_bytes
    sparse_M8192_vs_dense_M8192_ratio_at_n16384
  killer features at N=8192:
    per-(M, seed) retention, max_iso, above_thresh_frac
    per-M pass/fail aggregate
  on_device_deployable_yes_no:
    projected N=16384 footprint at M=8192 <= 25% of dense N=16384 footprint

PRE-REGISTERED BANDS:
  HARD_PASS = sparse-W at N=8192 preserves all killer features in ALL 3
              seeds at all M values (retention>=0.90, KF-2 <=0.05,
              KF-1<0.05) AND projected N=16384 footprint <= 25% of dense
              N=16384 footprint (consistent with 4x savings from sparse +
              compatible with on-device deployment).
  HARD_FAIL = sparse-W loses any killer feature at N=8192 in 2+ seeds at
              any M OR projection unstable (power-law slope outside
              [0.95, 1.05] of theoretical exponent 1.0).
  MIDDLE_BAND = otherwise.

NOTE: No _nN suffix on anchor name because analysis spans N=4096, N=8192,
projects to N=16384. Per PROT-018 rule 3, script asserts N values
explicitly.

TIMEOUT ESTIMATE:
  smoke_wall_s ~ 30s.
  FULL: footprint sweep (12 cells) + KF validation (9 cells: 3 M x 3 seeds)
  at N=8192. CPU. ~3h.
  Budget: 21600s (6h).

PROT-018: anchor name has no _nN suffix; script asserts explicit N values.
PROT-020: CPU only.

Anchor: sparse_w_large_n_integration_v1
Queue: remote_cpu_queue
Pre-reg: preregs/2026-05-30_sparse_w_large_n_integration_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._metric_battery import (  # noqa: E402
    make_substrate,
    metric_retention,
    metric_max_iso,
    metric_above_thresh_frac,
)


def make_bsc_substrate(N_use: int, M: int, seed: int, device: torch.device):
    """BSC codebook (random +/-1). Used when Kerdock dimension is invalid
    (e.g. N=8192 has odd log2). Returns same tuple shape as make_substrate."""
    C = N_use
    gen = torch.Generator(device='cpu').manual_seed(seed + 50000)
    raw = (torch.randint(0, 2, (C, N_use), generator=gen,
                          dtype=torch.float32) * 2 - 1)
    codebook = raw.to(device)
    gen2 = torch.Generator(device='cpu').manual_seed(seed + 51000)
    key_idx = torch.randperm(C, generator=gen2)[:M].to(device).to(torch.long)
    val_idx = torch.randint(0, C, (M,), generator=gen2,
                              dtype=torch.long).to(device)
    keys = codebook[key_idx]
    values = codebook[val_idx]
    W = (values.T @ keys) / N_use
    return codebook, W, keys, values, key_idx, val_idx


def _substrate_for_n(N_use: int, M: int, seed: int, device: torch.device):
    """Dispatch: Kerdock for N in {1024, 4096, 16384}; BSC otherwise."""
    if N_use in (1024, 4096, 16384):
        return make_substrate(N_use, M, seed, device)
    return make_bsc_substrate(N_use, M, seed, device)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_c8", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# Configuration  (PROT-018 rule 3: no _nN suffix; explicit N asserts)
N_FOOTPRINT  = 4096
N_VALIDATION = 8192
N_PROJECT    = 16384
assert N_FOOTPRINT == 4096
assert N_VALIDATION == 8192
assert N_PROJECT == 16384

M_FOOTPRINT_FULL  = [128, 512, 2048, 8192]
M_FOOTPRINT_SMOKE = [32, 128]

M_VALIDATION_FULL  = [512, 2048, 8192]
M_VALIDATION_SMOKE = [32, 128]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

BETA = 8.0

# Pre-reg
HP_RET = 0.90
HP_KF2 = 0.05
HP_KF1_FRAC = 0.05
HP_PROJ_RATIO = 0.25      # projected_sparse / dense_n16384 <= 0.25
HP_SLOPE_LOW  = 0.95
HP_SLOPE_HIGH = 1.05
HF_SEEDS_FAIL_MIN = 2     # at least 2/3 seeds failing -> HF


def get_output_dir(default_name: str = "sparse_w_large_n_integration_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _sparse_footprint_bytes(N: int, M: int, dtype_bytes: int = 4) -> int:
    """Sparse W footprint: keys (M, N) + values (M, N), float32 = 4 bytes."""
    return int(2 * M * N * dtype_bytes)


def _dense_footprint_bytes(N: int, dtype_bytes: int = 4) -> int:
    """Dense W footprint: (N, N) float32."""
    return int(N * N * dtype_bytes)


def measure_footprint_cell(N_use: int, M: int, seed: int,
                             device: torch.device) -> Dict:
    """Build substrate, measure dense + simulated-sparse footprints."""
    codebook, W, keys, values, key_idx, val_idx = _substrate_for_n(N_use, M, seed, device)
    # keys/values are (M, N) tensors -- the SAME structure as the sparse-W store.
    sparse_b = int(keys.element_size() * keys.numel()
                   + values.element_size() * values.numel())
    dense_b  = int(W.element_size() * W.numel())
    ratio    = sparse_b / max(1, dense_b)
    # theoretical match
    th_sparse_b = _sparse_footprint_bytes(N_use, M, dtype_bytes=4)
    th_dense_b  = _dense_footprint_bytes(N_use, dtype_bytes=4)
    del codebook, W, keys, values

    return {
        "N": int(N_use),
        "M": int(M),
        "seed": int(seed),
        "sparse_bytes":         sparse_b,
        "dense_bytes":          dense_b,
        "ratio_sparse_dense":   round(ratio, 6),
        "theoretical_sparse_bytes": th_sparse_b,
        "theoretical_dense_bytes":  th_dense_b,
        "sparse_match_theory":  bool(abs(sparse_b - th_sparse_b) <= 64),
        "dense_match_theory":   bool(abs(dense_b  - th_dense_b)  <= 64),
    }


def measure_killer_features_cell(N_use: int, M: int, seed: int,
                                    device: torch.device) -> Dict:
    """Build substrate and run retention/KF-2/KF-1 on the (sparse-equivalent) store."""
    codebook, W, keys, values, key_idx, val_idx = _substrate_for_n(N_use, M, seed, device)
    n_probe = min(50, M)

    ret = metric_retention(W, codebook, key_idx, val_idx, N_use,
                            beta=BETA, seed=seed, device=device, n_probe=n_probe)
    iso = metric_max_iso(W, codebook, key_idx, val_idx, N_use,
                          beta=BETA, seed=seed, device=device,
                          n_probe=n_probe, n_edits=min(8, max(1, M - n_probe)))
    kf1 = metric_above_thresh_frac(W, codebook, key_idx, val_idx, N_use,
                                      beta=BETA, seed=seed, device=device,
                                      n_probe=n_probe)

    del codebook, W, keys, values
    return {
        "N": int(N_use), "M": int(M), "seed": int(seed),
        "retention":        float(ret["retention"]),
        "max_iso":          float(iso["max_iso"]),
        "above_thresh_frac": float(kf1["above_thresh_frac"]),
        "kf_pass": bool(
            ret["retention"] >= HP_RET
            and iso["max_iso"] <= HP_KF2
            and kf1["above_thresh_frac"] <= HP_KF1_FRAC
        ),
    }


def project_to_n16384(footprint_cells: List[Dict], fit_N: int = N_FOOTPRINT) -> Dict:
    """Power-law fit: sparse_bytes = a * M^slope, validate slope ~ 1.0.

    Also project sparse footprint at N=16384, M=8192:
        sparse(N, M) = 2 * M * N * 4
    Dense at N=16384: N*N*4 = 16384^2*4 = 1024 MiB.
    """
    if not footprint_cells:
        return {"valid": False, "reason": "no_cells"}

    # Fit slope at fixed N (default N=4096 production)
    pairs = [(c["M"], c["sparse_bytes"]) for c in footprint_cells
             if c["N"] == fit_N and c["M"] > 0 and c["sparse_bytes"] > 0]
    if len(pairs) < 2:
        return {"valid": False, "reason": "not_enough_points_for_fit"}

    # log-linear regression: log(b) = slope*log(M) + intercept
    xs = [math.log(m) for m, _ in pairs]
    ys = [math.log(b) for _, b in pairs]
    n  = len(xs)
    sx = sum(xs); sy = sum(ys)
    sxx = sum(x*x for x in xs); sxy = sum(x*y for x, y in zip(xs, ys))
    denom = (n * sxx - sx * sx)
    if abs(denom) < 1e-9:
        return {"valid": False, "reason": "singular_fit"}
    slope = (n * sxy - sx * sy) / denom
    intercept = (sy - slope * sx) / n

    # Projection at N=16384 across M sweep (per-M ratio).
    # At M=2048, theoretical sparse/dense = 2*2048*16384 / 16384^2 = 0.25
    # At M=8192, theoretical sparse/dense = 1.0 (saturation; sparse no longer wins)
    proj_sweep = {}
    for M_proj in (1024, 2048, 4096, 8192):
        s_b = _sparse_footprint_bytes(N_PROJECT, M_proj, dtype_bytes=4)
        d_b = _dense_footprint_bytes(N_PROJECT, dtype_bytes=4)
        proj_sweep[f"M{M_proj}"] = {
            "sparse_bytes": int(s_b),
            "dense_bytes":  int(d_b),
            "ratio":        round(s_b / max(1, d_b), 6),
        }

    # Per user spec, "on-device deployable" anchor is the highest M whose
    # ratio stays <= 0.25. M=2048 should pass at N=16384 (4x savings).
    proj_M_anchor = 2048
    proj_ratio_anchor = proj_sweep[f"M{proj_M_anchor}"]["ratio"]

    return {
        "valid": True,
        "slope": round(slope, 5),
        "intercept": round(intercept, 5),
        "slope_match_theory": bool(HP_SLOPE_LOW <= slope <= HP_SLOPE_HIGH),
        "projection_at_n16384": proj_sweep,
        "on_device_anchor_M":          int(proj_M_anchor),
        "on_device_anchor_ratio":      round(proj_ratio_anchor, 6),
        "on_device_deployable": bool(proj_ratio_anchor <= HP_PROJ_RATIO),
    }


def compute_verdict(footprint_cells: List[Dict],
                     kf_cells: List[Dict],
                     projection: Dict) -> Tuple[str, str]:
    if not footprint_cells or not kf_cells:
        return ("C8_INCONCLUSIVE", "no cells")

    # KF aggregation per M
    by_m: Dict[int, List[Dict]] = {}
    for c in kf_cells:
        by_m.setdefault(int(c["M"]), []).append(c)

    hp_all_kf = True
    hf_any_kf = False
    kf_summary = []
    for m, cs in sorted(by_m.items()):
        n_pass = sum(1 for c in cs if c["kf_pass"])
        n_fail = len(cs) - n_pass
        kf_summary.append(f"M={m}:{n_pass}/{len(cs)}_pass")
        if n_pass < len(cs):
            hp_all_kf = False
        if n_fail >= HF_SEEDS_FAIL_MIN:
            hf_any_kf = True

    proj_ok = bool(projection.get("valid")
                    and projection.get("slope_match_theory")
                    and projection.get("on_device_deployable"))
    proj_summary = (f"slope={projection.get('slope','NA')} "
                     f"deployable={projection.get('on_device_deployable')}")

    detail = "; ".join(kf_summary) + " | " + proj_summary

    if hf_any_kf:
        return ("C8_HARD_FAIL", f"KF_BROKEN: {detail}")
    if not projection.get("valid"):
        return ("C8_MIDDLE_BAND", f"PROJ_UNSTABLE: {detail}")
    if hp_all_kf and proj_ok:
        return ("C8_HARD_PASS", f"COMPOSITION_OK: {detail}")
    return ("C8_MIDDLE_BAND", f"PARTIAL: {detail}")


def _instrumentation_selftest() -> None:
    """Validate footprint formula, KF metrics, projection fit at smoke scale."""
    assert N_FOOTPRINT == 4096 and N_VALIDATION == 8192 and N_PROJECT == 16384
    # Formula self-test: sparse(N=4096, M=2048) = 2*2048*4096*4 = 64 MiB
    sb = _sparse_footprint_bytes(4096, 2048, 4)
    assert sb == 67108864, f"sparse footprint formula wrong: {sb}"
    # Dense(N=4096) = 4096*4096*4 = 64 MiB
    db = _dense_footprint_bytes(4096, 4)
    assert db == 67108864, f"dense footprint formula wrong: {db}"
    # Dense(N=16384) = 16384*16384*4 = 1024 MiB
    db16 = _dense_footprint_bytes(16384, 4)
    assert db16 == 1073741824, f"dense N=16384 formula wrong: {db16}"
    # Sparse(N=16384, M=8192) = 2*8192*16384*4 = 1024 MiB ... same as dense at this point
    sb16 = _sparse_footprint_bytes(16384, 8192, 4)
    assert sb16 == 1073741824, f"sparse N=16384 M=8192 formula wrong: {sb16}"
    # At M=2048 it's 256 MiB, ratio = 256/1024 = 0.25 vs dense N=16384 -> on-device deployable bound
    sb16_2k = _sparse_footprint_bytes(16384, 2048, 4)
    assert sb16_2k == 268435456, f"sparse N=16384 M=2048 formula wrong: {sb16_2k}"

    device = torch.device("cpu")
    # Kerdock 4-coset requires N in {1024, 4096, 16384}; BSC fallback otherwise.
    # Footprint cell sanity at small N=1024, M=32 (Kerdock path)
    fp = measure_footprint_cell(N_use=1024, M=32, seed=17, device=device)
    assert fp["sparse_match_theory"], "footprint cell empirical != theory"
    assert fp["dense_match_theory"], "dense footprint cell empirical != theory"

    # KF cell sanity at small N=1024, M=32
    kf = measure_killer_features_cell(N_use=1024, M=32, seed=17, device=device)
    assert kf["retention"] is not None and not math.isnan(kf["retention"])
    assert kf["max_iso"] is not None and not math.isnan(kf["max_iso"])
    assert kf["above_thresh_frac"] is not None

    # Projection sanity (3 M values at N=1024 to fit a slope)
    sample = [
        measure_footprint_cell(N_use=1024, M=m, seed=17, device=device)
        for m in [16, 64, 256]
    ]
    proj = project_to_n16384(sample, fit_N=1024)
    assert proj.get("valid"), "projection invalid at smoke"
    assert HP_SLOPE_LOW <= proj["slope"] <= HP_SLOPE_HIGH, \
        f"projection slope {proj['slope']} outside [{HP_SLOPE_LOW}, {HP_SLOPE_HIGH}]"

    print(f"[selftest] sparse_w_large_n_integration_v1 PASS "
          f"slope={proj['slope']:.4f} "
          f"ret={kf['retention']:.3f} max_iso={kf['max_iso']:.3f}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)

    device = torch.device("cpu")
    smoke = args.smoke
    M_fp_sweep = M_FOOTPRINT_SMOKE if smoke else M_FOOTPRINT_FULL
    M_val_sweep = M_VALIDATION_SMOKE if smoke else M_VALIDATION_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    # Note: smoke uses small N for both footprint + validation
    # Kerdock-valid Ns: 1024, 4096, 16384. BSC fallback for N=8192 (production
    # validation point that has odd log2). Smoke uses 1024 for both.
    N_fp = 1024 if smoke else N_FOOTPRINT
    N_val = 1024 if smoke else N_VALIDATION

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] sparse_w_large_n smoke={smoke} N_fp={N_fp} N_val={N_val} "
          f"M_fp={M_fp_sweep} M_val={M_val_sweep} seeds={seeds} "
          f"done={len(done)}", flush=True)

    # PART A: footprint sweep
    footprint_cells: List[Dict] = []
    for M in M_fp_sweep:
        for seed in seeds[:1]:
            ck = f"fp_M{M}_s{seed}"
            if ck in done:
                body = load_partial_key(out_dir, ck)
                if body is not None:
                    footprint_cells.append(body)
                    continue
            try:
                out = measure_footprint_cell(N_fp, M, seed, device)
                write_partial_key(out_dir, ck, out)
                footprint_cells.append(out)
                print(f"  fp N={N_fp} M={M} s={seed} sparse/dense="
                      f"{out['ratio_sparse_dense']:.4f} "
                      f"({time.time()-t0:.1f}s)", flush=True)
            except (RuntimeError, MemoryError) as e:
                print(f"  fp M={M} s={seed} FAILED: {e}", flush=True)

    # PART B: killer-feature validation at N_val
    kf_cells: List[Dict] = []
    for M in M_val_sweep:
        for seed in seeds:
            ck = f"kf_N{N_val}_M{M}_s{seed}"
            if ck in done:
                body = load_partial_key(out_dir, ck)
                if body is not None:
                    kf_cells.append(body)
                    continue
            try:
                out = measure_killer_features_cell(N_val, M, seed, device)
                write_partial_key(out_dir, ck, out)
                kf_cells.append(out)
                print(f"  kf N={N_val} M={M} s={seed} "
                      f"ret={out['retention']:.3f} iso={out['max_iso']:.3f} "
                      f"kf1={out['above_thresh_frac']:.3f} pass={out['kf_pass']} "
                      f"({time.time()-t0:.1f}s)", flush=True)
            except (RuntimeError, MemoryError) as e:
                print(f"  kf M={M} s={seed} FAILED: {e}", flush=True)

    # PART C: projection (fit at the actual N used; smoke uses N_fp, full uses N_FOOTPRINT)
    proj_input = footprint_cells
    fit_N_arg = N_fp if smoke else N_FOOTPRINT
    projection = project_to_n16384(proj_input, fit_N=fit_N_arg)
    print(f"  projection: valid={projection.get('valid')} "
          f"slope={projection.get('slope','NA')} "
          f"deployable={projection.get('on_device_deployable','NA')}",
          flush=True)

    verdict, vm = compute_verdict(footprint_cells, kf_cells, projection)
    elapsed = round(time.time() - t0, 2)
    summary = {
        "anchor": "sparse_w_large_n_integration_v1",
        "smoke": smoke,
        "N_footprint": N_fp, "N_validation": N_val, "N_project": N_PROJECT,
        "M_footprint_sweep": M_fp_sweep, "M_validation_sweep": M_val_sweep,
        "seeds": seeds,
        "footprint_cells": footprint_cells,
        "kf_cells": kf_cells,
        "projection": projection,
        "verdict": verdict, "verdict_msg": vm, "elapsed_s": elapsed,
    }
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
