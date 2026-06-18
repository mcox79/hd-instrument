"""A1: 8a 4-channel cost ATTRIBUTION profiler (Director PHASE-A-closed GPU-2; Skunkworks design-CONFIRM + 5 refinements).

The canonical measured-8a verdict is HARD_FAIL (boundary NON-MONOTONE in token-count). A1 explains the WHY: attribute the
MEASURED GPU wall-time of the MoE-top-k sparse op to 4 cost channels, ACROSS the token-count points around the boundary,
to localize WHICH channel drives the non-monotonicity -- and whether the RESIDUAL (the non-additive part the additive
cost-model cannot represent) carries it (which would EXPLAIN the 8a cost-model-vs-measured inversion the METHOD-GATE caught).

Channels (MEASURED via torch.cuda timers + synchronize; NOT the cost-model PEAK_FLOP/PEAK_BW/TAU_LAUNCH constants):
  1. COMPUTE  : a fused matmul VOLUME-MATCHED to the sparse op's FLOPs (flops_sparse) -> the compute-bound floor.
  2. MEM_BW   : a memory op VOLUME-MATCHED to the sparse op's bytes (bytes_sparse) -> the bandwidth-bound floor.
  3. LAUNCH   : n_active small per-expert kernel launches (VOLUME-MATCHED launch count) -> the dispatch/launch tax.
  4. RESIDUAL : measured_total - [max(COMPUTE, MEM_BW) + LAUNCH]  <- the cost-model's STRUCTURE is max(compute,membw)+launch
                (roofline + additive launch); the residual is exactly what that additive/roofline model CANNOT represent
                (scheduling / overlap-imperfection / contention). Reported HONESTLY (refinement 2; never forced to zero).

5 Skunkworks refinements: (1) VOLUME-MATCH each isolation to the real op (verify + REPORT each isolation volume vs real);
(2) RESIDUAL is the key finding (vs the cost-model's max+launch); (3) localize the NON-MONOTONE channel ACROSS the boundary
token-counts; (4) any cheap-channel = a drill-2 RECOVERY-CANDIDATE HYPOTHESIS (T2/T3), NOT a recovery claim; (5) measured +
scoped (measured-bounds @ flagship config/hardware; verdict = ATTRIBUTION, NOT pass/fail -- the measured-8a HARD_FAIL STANDS).
11th rule: pure torch, no LLM. ASCII-only. HDLAB_RUN_MODE smoke|full ; --smoke ; --self-test ; --full.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _cell_provenance import provenance_fields, now_utc

ANCHOR = "substrate_8a_4channel_attribution_v1"
_EXP_NAME = os.environ.get("HDLAB_EXP_NAME")          # queue_add contract: data/exp_<HDLAB_EXP_NAME>/metrics.json
OUT = REPO / "data" / (f"exp_{_EXP_NAME}" if _EXP_NAME else ANCHOR)

# 8a flagship config (matches exp_substrate_active_gating_8a_break_even_v1): d, e, k; sweep T ACROSS the break-even boundary
D = 1024
E = 8
K_LIST_FULL = [1, 2, 4]
T_GRID_FULL = [512, 1024, 2048, 4096, 8192, 16384, 32768]   # token-counts spanning the break-even boundary (T*~4096)
K_LIST_SMOKE = [2]
T_GRID_SMOKE = [1024, 4096]
BYTES = 4                                            # fp32
ITERS = 20
WARMUP = 5


def _gen(device):
    return torch.Generator(device=device).manual_seed(0)


def expected_distinct_experts(T, k, e):
    return e * (1.0 - (1.0 - k / e) ** T) if T > 0 else 0.0


def _timed(fn, device):
    is_cuda = device.type == "cuda"
    for _ in range(WARMUP):
        fn()
    if is_cuda:
        torch.cuda.synchronize()
    ts = []
    for _ in range(ITERS):
        if is_cuda:
            torch.cuda.synchronize()
        s = time.perf_counter()
        fn()
        if is_cuda:
            torch.cuda.synchronize()
        ts.append(time.perf_counter() - s)
    ts.sort()
    return {"median_s": ts[len(ts) // 2], "p95_s": ts[min(len(ts) - 1, int(0.95 * (len(ts) - 1)))], "min_s": ts[0]}


def attribute_cell(T, k, d, e, device):
    """Measure the real sparse MoE-top-k op + the 4 VOLUME-MATCHED channel isolations at (T,k). All torch-measured."""
    g = _gen(device)
    X = torch.randn(T, d, generator=g, device=device)
    G = torch.randn(d, e, generator=g, device=device) / d ** 0.5
    We = [torch.randn(d, d, generator=g, device=device) / d ** 0.5 for _ in range(e)]
    n_active = expected_distinct_experts(T, k, e)

    # REAL sparse op (the measured-8a op): router + topk dispatch + per-expert loop (the small-batch launch tax).
    def sparse():
        topk = (X @ G).topk(k, dim=1).indices
        out = torch.zeros(T, d, device=device)
        for ei in range(e):
            mask = (topk == ei).any(dim=1)
            if bool(mask.any()):
                out[mask] += torch.relu(X[mask] @ We[ei])
        return out

    # REAL op volumes (what the isolations must MATCH; refinement 1):
    flops_router = T * 2 * d * e
    flops_expert = T * k * 2 * d * d
    flops_sparse = flops_router + flops_expert
    bytes_sparse = n_active * d * d * BYTES + T * d * BYTES + T * k * BYTES
    launch_count = max(1, int(round(n_active)))

    # CH1 COMPUTE: a fused matmul volume-matched to flops_sparse. A (T x d)@(d x w) matmul = T*2*d*w FLOPs -> w = flops_sparse/(2*T*d).
    w = max(1, int(round(flops_sparse / (2.0 * T * d))))
    Wc = torch.randn(d, w, generator=g, device=device) / d ** 0.5
    compute_flops = T * 2 * d * w
    def ch_compute():
        return torch.relu(X @ Wc)

    # CH2 MEM_BW: read bytes_sparse bytes with minimal compute (sum over a buffer of matched byte volume).
    n_elem = max(1, int(round(bytes_sparse / BYTES)))
    Mbuf = torch.randn(n_elem, generator=g, device=device)
    membw_bytes = n_elem * BYTES
    def ch_membw():
        return Mbuf.sum()

    # CH3 LAUNCH: launch_count tiny kernels (volume-matched launch count), trivial work each = the per-expert dispatch tax.
    tiny = [torch.ones(8, device=device) for _ in range(launch_count)]
    def ch_launch():
        s = 0.0
        for t in tiny:
            s = s + t.sum()          # one tiny kernel launch each (the launch overhead, not the work)
        return s

    t_sparse = _timed(sparse, device)["median_s"]
    t_compute = _timed(ch_compute, device)["median_s"]
    t_membw = _timed(ch_membw, device)["median_s"]
    t_launch = _timed(ch_launch, device)["median_s"]

    cost_model_pred = max(t_compute, t_membw) + t_launch       # the cost-model's STRUCTURE: roofline(max) + additive launch
    residual = t_sparse - cost_model_pred                       # what the additive/roofline cost-model CANNOT represent
    return {
        "T": T, "k": k, "n_active": round(n_active, 3), "launch_count": launch_count,
        "t_sparse_ms": round(t_sparse * 1e3, 4),
        "compute_ms": round(t_compute * 1e3, 4), "membw_ms": round(t_membw * 1e3, 4),
        "launch_ms": round(t_launch * 1e3, 4), "cost_model_pred_ms": round(cost_model_pred * 1e3, 4),
        "residual_ms": round(residual * 1e3, 4),
        "residual_frac_of_measured": round(residual / t_sparse, 4) if t_sparse > 0 else 0.0,
        # refinement 1: volume-match verification (isolation volume vs the real op's volume; ratio ~1.0 = matched)
        "volume_match": {"compute_flops_ratio": round(compute_flops / max(flops_sparse, 1), 3),
                         "membw_bytes_ratio": round(membw_bytes / max(bytes_sparse, 1), 3),
                         "launch_count_match": launch_count},
    }


def _nonmonotone(seq):
    """Is the per-T sequence non-monotone (has a local dip/rise reversing direction)? Returns (is_nonmonotone, n_reversals)."""
    diffs = [b - a for a, b in zip(seq, seq[1:])]
    signs = [1 if d > 0 else (-1 if d < 0 else 0) for d in diffs if d != 0]
    rev = sum(1 for a, b in zip(signs, signs[1:]) if a != b)
    return (rev > 0, rev)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    args, _ = ap.parse_known_args()
    is_smoke = args.smoke or (os.environ.get("HDLAB_RUN_MODE", "full") == "smoke" and not args.full)
    run_started_utc = now_utc()
    t0 = time.time()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    src = "measured_torch_gpu" if device.type == "cuda" else "measured_torch_cpu"

    if args.self_test:
        c = attribute_cell(512, 2, D, E, device)
        print(f"[{ANCHOR}] --self-test wiring OK (device={device.type}; t_sparse_ms={c['t_sparse_ms']} "
              f"residual_frac={c['residual_frac_of_measured']}); NO metrics written.")
        return 0

    k_list = K_LIST_SMOKE if is_smoke else K_LIST_FULL
    t_grid = T_GRID_SMOKE if is_smoke else T_GRID_FULL

    cells = []
    for k in k_list:
        for T in t_grid:
            cells.append(attribute_cell(T, k, D, E, device))
            c = cells[-1]
            print(f"[{ANCHOR}] k={c['k']} T={c['T']}: t_sparse={c['t_sparse_ms']}ms compute={c['compute_ms']} "
                  f"membw={c['membw_ms']} launch={c['launch_ms']} residual={c['residual_ms']} "
                  f"({c['residual_frac_of_measured']*100:.0f}% of measured)", flush=True)

    # refinement 3: per-channel non-monotonicity ACROSS T (per k), to localize the channel driving the non-monotone boundary
    localize = {}
    for k in k_list:
        kc = sorted([c for c in cells if c["k"] == k], key=lambda c: c["T"])
        chans = {ch: [c[ch] for c in kc] for ch in ("t_sparse_ms", "compute_ms", "membw_ms", "launch_ms", "residual_ms")}
        nm = {ch: _nonmonotone(seq) for ch, seq in chans.items()}
        localize[f"k{k}"] = {ch: {"non_monotone": v[0], "reversals": v[1]} for ch, v in nm.items()}

    # which non-sparse channel is non-monotone where t_sparse is non-monotone (the channel driving the boundary)
    driving = []
    for k in k_list:
        L = localize[f"k{k}"]
        if L["t_sparse_ms"]["non_monotone"]:
            chans_nm = [ch.replace("_ms", "") for ch in ("compute_ms", "membw_ms", "launch_ms", "residual_ms")
                        if L[ch]["non_monotone"]]
            driving.append({"k": k, "sparse_nonmonotone": True, "nonmonotone_channels": chans_nm})
    # residual-carries-the-nonmonotonicity check (the inversion explanation, refinement 2)
    residual_drives = any(d["k"] and "residual" in d["nonmonotone_channels"] for d in driving)
    max_residual_frac = max((c["residual_frac_of_measured"] for c in cells), default=0.0)
    vol_ok = all(0.5 <= c["volume_match"]["compute_flops_ratio"] <= 2.0
                 and 0.5 <= c["volume_match"]["membw_bytes_ratio"] <= 2.0 for c in cells)

    if driving:
        chset = sorted({ch for d in driving for ch in d["nonmonotone_channels"]})
        verdict = "ATTRIBUTION"
        msg = (f"8a non-monotonicity ATTRIBUTED: t_sparse is non-monotone in T for k={[d['k'] for d in driving]}; "
               f"the non-monotone channel(s) = {chset}. "
               + ("RESIDUAL carries the non-monotonicity -> EXPLAINS the cost-model-vs-measured inversion (the additive "
                  "max+launch cost-model structurally cannot represent the non-additive residual where the non-monotonicity "
                  "lives -> predicted clean-monotone HARD_PASS; measurement non-monotone HARD_FAIL). "
                  if residual_drives else "")
               + f"max residual={max_residual_frac*100:.0f}% of measured. measured-bounds: flagship d={D}/e={E} @ this "
               f"hardware, NOT fundamental. The measured-8a HARD_FAIL STANDS (A1 explains, does not re-verdict).")
    else:
        verdict = "ATTRIBUTION"
        msg = (f"8a attribution: t_sparse MONOTONE in T at this run's grid/hardware (no reversal); dominant channel by "
               f"share reported per-cell. max residual={max_residual_frac*100:.0f}% of measured. (If monotone here but the "
               f"canonical HARD_FAIL was non-monotone, the boundary non-monotonicity is config/hardware-sensitive -- "
               f"measured-bounds; flag for cross-config.) measured-8a HARD_FAIL STANDS.")

    metrics = {
        "anchor_name": ANCHOR, "verdict": verdict, "verdict_msg": msg, "summary": msg, "headline": msg,
        "n_seeds": 1,
        **provenance_fields("smoke" if is_smoke else "full", "4channel_attribution", src, run_started_utc),
        "n_cells": len(cells), "residual_drives_nonmonotonicity": residual_drives,
        "max_residual_frac_of_measured": round(max_residual_frac, 4), "volume_match_ok": vol_ok,
        "driving": driving, "localize": localize, "cells": cells,
        "config": {"d": D, "e": E, "k_list": k_list, "T_grid": t_grid, "iters": ITERS},
        "bears_on": "substrate_active_gating_8a_break_even_v1 (measured HARD_FAIL, boundary non-monotone) -- mechanism WHY",
        "recovery_candidate_note": "drill-2: any cheap-attackable dominant channel (e.g. launch-tax via kernel fusion) is a "
                                   "T2/T3 RECOVERY-CANDIDATE HYPOTHESIS to be TESTED, NOT a recovery claim (refinement 4)",
        "measured_bounds": f"4-channel attribution of the 8a sparse op @ flagship d={D}/e={E}/this-hardware; NOT fundamental",
        "elapsed_s": round(time.time() - t0, 2),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, OUT / "metrics.json")

    print(f"[{ANCHOR}] run_mode={'smoke' if is_smoke else 'full'} device={device.type} -> {verdict}")
    print(f"  residual_drives_nonmonotonicity={residual_drives} max_residual_frac={max_residual_frac:.2f} volume_match_ok={vol_ok}")
    print(f"  {msg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
