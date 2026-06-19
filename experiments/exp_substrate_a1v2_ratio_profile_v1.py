"""A1-v2: net_speedup RATIO profiler -- closes A1's OPEN non-monotonicity localization (Bucket D; USER-ratified 6h plan).

A1 measured t_sparse (ABSOLUTE sparse-op cost) and found it MONOTONE in token-count -- but the canonical measured-8a
HARD_FAIL is non-monotonicity in net_speedup = t_dense / t_sparse (the RATIO). A1 had NO t_dense, so it could not say
WHERE the ratio non-monotonicity lives (a ratio can be non-monotone with monotone numerator AND denominator). A1-v2
measures BOTH t_dense and t_sparse across the boundary token-counts, computes net_speedup, and LOCALIZES the
non-monotonicity: numerator (t_dense), denominator (t_sparse), or the ratio-interaction.

Both ops MEASURED via torch.cuda timers + synchronize (NOT cost-model constants):
  t_dense  : every token through ALL e experts (the dense MoE baseline the sparse op speeds up relative to).
  t_sparse : router topk-k dispatch + per-active-expert loop (the measured-8a sparse op; SAME as A1).
  net_speedup = t_dense / t_sparse  (the quantity whose token-count non-monotonicity is the 8a HARD_FAIL).

Noise-guarded non-monotonicity (A1's must-fix carried forward): a reversal counts only if it EXCEEDS the jitter floor
(propagated to the ratio). verdict = ATTRIBUTION (mechanism-WHY; the measured-8a HARD_FAIL STANDS, independent).
Adopts Skunkworks C2 gate0_self_check (producer-side GATE-0). 11th rule: pure torch, no LLM. ASCII-only.
HDLAB_RUN_MODE smoke|full ; --smoke ; --self-test ; --full.
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
from _cell_provenance import provenance_fields, now_utc, gate0_self_check

ANCHOR = "substrate_a1v2_ratio_profile_v1"
_EXP_NAME = os.environ.get("HDLAB_EXP_NAME")          # queue_add contract: data/exp_<HDLAB_EXP_NAME>/metrics.json
OUT = REPO / "data" / (f"exp_{_EXP_NAME}" if _EXP_NAME else ANCHOR)

# 8a flagship config (matches exp_substrate_8a_4channel_attribution_v1 + the break-even cell): sweep T across boundary.
D = 1024
E = 8
K_LIST_FULL = [1, 2, 4]
T_GRID_FULL = [512, 1024, 2048, 4096, 8192, 16384, 32768]
K_LIST_SMOKE = [2]
T_GRID_SMOKE = [1024, 4096]
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


def ratio_cell(T, k, d, e, device):
    """Measure t_dense (all experts) + t_sparse (topk) at (T,k); compute net_speedup + propagated jitter bands."""
    g = _gen(device)
    X = torch.randn(T, d, generator=g, device=device)
    G = torch.randn(d, e, generator=g, device=device) / d ** 0.5
    We = [torch.randn(d, d, generator=g, device=device) / d ** 0.5 for _ in range(e)]
    n_active = expected_distinct_experts(T, k, e)

    def dense():
        # every token through ALL e experts (the dense MoE baseline)
        out = torch.zeros(T, d, device=device)
        for ei in range(e):
            out = out + torch.relu(X @ We[ei])
        return out

    def sparse():
        # router topk + per-active-expert dispatch (the measured-8a sparse op; same as A1)
        topk = (X @ G).topk(k, dim=1).indices
        out = torch.zeros(T, d, device=device)
        for ei in range(e):
            mask = (topk == ei).any(dim=1)
            if bool(mask.any()):
                out[mask] += torch.relu(X[mask] @ We[ei])
        return out

    dd = _timed(dense, device)
    dsp = _timed(sparse, device)
    t_dense, t_sparse = dd["median_s"], dsp["median_s"]
    b_dense = dd["p95_s"] - dd["min_s"]
    b_sparse = dsp["p95_s"] - dsp["min_s"]
    net_speedup = (t_dense / t_sparse) if t_sparse > 0 else 0.0
    # ratio jitter band (first-order propagation): d(a/b) ~ (a/b)*(da/a + db/b)
    b_ratio = net_speedup * ((b_dense / t_dense if t_dense > 0 else 0.0) + (b_sparse / t_sparse if t_sparse > 0 else 0.0))
    return {
        "T": T, "k": k, "n_active": round(n_active, 3),
        "t_dense_ms": round(t_dense * 1e3, 4), "t_sparse_ms": round(t_sparse * 1e3, 4),
        "net_speedup": round(net_speedup, 4),
        "band_ms": {"t_dense_ms": round(b_dense * 1e3, 4), "t_sparse_ms": round(b_sparse * 1e3, 4)},
        "band_net_speedup": round(b_ratio, 4),
    }


def _nonmonotone(seq, bands, rel_eps=0.05):
    """NOISE-GUARDED non-monotonicity (A1 must-fix): a reversal counts ONLY if it EXCEEDS the noise floor
    = max(jitter-band of the two adjacent points, rel_eps*|value|). Returns (is_nonmonotone, n_sig_reversals)."""
    signs = []
    for i in range(len(seq) - 1):
        d = seq[i + 1] - seq[i]
        floor = max(bands[i], bands[i + 1], rel_eps * abs(seq[i]), rel_eps * abs(seq[i + 1]))
        if abs(d) > floor:
            signs.append(1 if d > 0 else -1)
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
        c = ratio_cell(512, 2, D, E, device)
        print(f"[{ANCHOR}] --self-test wiring OK (device={device.type}; t_dense_ms={c['t_dense_ms']} "
              f"t_sparse_ms={c['t_sparse_ms']} net_speedup={c['net_speedup']}); NO metrics written.")
        return 0

    k_list = K_LIST_SMOKE if is_smoke else K_LIST_FULL
    t_grid = T_GRID_SMOKE if is_smoke else T_GRID_FULL
    n_cells_declared = len(k_list) * len(t_grid)

    cells = []
    for k in k_list:
        for T in t_grid:
            cells.append(ratio_cell(T, k, D, E, device))
            c = cells[-1]
            print(f"[{ANCHOR}] k={c['k']} T={c['T']}: t_dense={c['t_dense_ms']}ms t_sparse={c['t_sparse_ms']}ms "
                  f"net_speedup={c['net_speedup']}", flush=True)

    # noise-guarded non-monotonicity ACROSS T (per k) for numerator, denominator, and ratio
    localize = {}
    for k in k_list:
        kc = sorted([c for c in cells if c["k"] == k], key=lambda c: c["T"])
        d_seq = [c["t_dense_ms"] for c in kc]; d_band = [c["band_ms"]["t_dense_ms"] for c in kc]
        s_seq = [c["t_sparse_ms"] for c in kc]; s_band = [c["band_ms"]["t_sparse_ms"] for c in kc]
        r_seq = [c["net_speedup"] for c in kc]; r_band = [c["band_net_speedup"] for c in kc]
        nm_d = _nonmonotone(d_seq, d_band); nm_s = _nonmonotone(s_seq, s_band); nm_r = _nonmonotone(r_seq, r_band)
        localize[f"k{k}"] = {
            "t_dense": {"non_monotone": nm_d[0], "sig_reversals": nm_d[1]},
            "t_sparse": {"non_monotone": nm_s[0], "sig_reversals": nm_s[1]},
            "net_speedup": {"non_monotone": nm_r[0], "sig_reversals": nm_r[1]},
        }

    # ATTRIBUTION of the net_speedup non-monotonicity: which side drives it
    attribution = []
    for k in k_list:
        L = localize[f"k{k}"]
        if L["net_speedup"]["non_monotone"]:
            drivers = [ch for ch in ("t_dense", "t_sparse") if L[ch]["non_monotone"]]
            kind = ("interaction_only" if not drivers else "+".join(drivers))
            attribution.append({"k": k, "net_speedup_nonmonotone": True, "driven_by": kind,
                                "ratio_only": (not drivers)})
    ratio_nonmonotone_any = any(L["net_speedup"]["non_monotone"] for L in localize.values())
    interaction_only = any(a.get("ratio_only") for a in attribution)
    smoke_cant_test = (len(t_grid) < 3)

    verdict = "ATTRIBUTION"   # mechanism-WHY; measured-8a HARD_FAIL STANDS (independent)
    nss = [c["net_speedup"] for c in cells]
    ns_scope = f"net_speedup across cells: min={round(min(nss),3)} median={round(sorted(nss)[len(nss)//2],3)} max={round(max(nss),3)}"
    if smoke_cant_test:
        msg = (f"SMOKE WIRING-CHECK ONLY (NON-test): {len(t_grid)} T-points < 3 cannot test non-monotonicity. The full "
               f"7-T-point run is the real ratio attribution. {ns_scope}. measured-8a HARD_FAIL STANDS.")
    elif ratio_nonmonotone_any:
        parts = "; ".join(f"k={a['k']} driven_by={a['driven_by']}" for a in attribution)
        msg = (f"net_speedup NON-MONOTONE in T (noise-guarded) -> A1's OPEN localization now CLOSED: {parts}. "
               + ("The ratio is non-monotone while BOTH t_dense and t_sparse are monotone (INTERACTION-only: the "
                  "non-monotonicity is an emergent property of the t_dense/t_sparse RATIO, not of either curve alone "
                  "-- exactly the case A1's t_sparse-only measurement could not detect). " if interaction_only else
                  "The ratio non-monotonicity is carried by the named numerator/denominator curve(s). ")
               + f"{ns_scope}. measured-bounds: flagship d={D}/e={E} @ this hardware, NOT fundamental. measured-8a HARD_FAIL STANDS.")
    else:
        msg = (f"net_speedup MONOTONE in T (noise-guarded) at this grid/hardware -> at THIS config the ratio is monotone "
               f"(A1's t_sparse-monotone finding extends to the ratio here). {ns_scope}. The canonical 8a net_speedup "
               f"non-monotonicity may be config/regime-specific (different d/e/k or finer T-grid); measured-8a HARD_FAIL STANDS.")

    g0 = gate0_self_check(run_mode=("smoke" if is_smoke else "full"), metrics_source=src,
                          n_cells_declared=n_cells_declared, n_cells_emitted=len(cells),
                          elapsed_s=round(time.time() - t0, 2), is_smoke=is_smoke)

    metrics = {
        "anchor_name": ANCHOR, "verdict": verdict, "verdict_msg": msg, "summary": msg, "headline": msg,
        "n_seeds": 1,
        **provenance_fields("smoke" if is_smoke else "full", "ratio_profile_dense_vs_sparse", src, run_started_utc),
        "gate0_self_check": g0,                                  # Skunkworks C2 producer-side GATE-0 self-attest
        "n_cells": len(cells),
        "ratio_nonmonotone_any": ratio_nonmonotone_any,
        "interaction_only_nonmonotonicity": interaction_only,   # the key A1-closing finding (ratio non-monotone, both curves monotone)
        "attribution": attribution,
        "net_speedup_localization": ("CLOSED -- " + ("interaction-only (ratio non-monotone, t_dense+t_sparse monotone)"
                                     if interaction_only else "attributed to numerator/denominator curve(s)"))
                                     if (ratio_nonmonotone_any and not smoke_cant_test)
                                     else ("monotone-at-this-config" if not smoke_cant_test else "smoke-non-test"),
        "measures_quantity": "net_speedup = t_dense/t_sparse (the RATIO) -- closes A1's t_sparse-only gap by adding t_dense",
        "smoke_cant_test_nonmonotonicity": smoke_cant_test,
        "localize": localize, "cells": cells,
        "config": {"d": D, "e": E, "k_list": k_list, "T_grid": t_grid, "iters": ITERS},
        "bears_on": "substrate_8a_4channel_attribution_v1 (A1; closes its OPEN net_speedup localization) + "
                    "substrate_active_gating_8a_break_even_v1 (measured HARD_FAIL net_speedup non-monotone)",
        "measured_bounds": f"net_speedup ratio profile @ flagship d={D}/e={E}/this-hardware; NOT fundamental",
        "elapsed_s": round(time.time() - t0, 2),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, OUT / "metrics.json")

    print(f"[{ANCHOR}] run_mode={'smoke' if is_smoke else 'full'} device={device.type} -> {verdict}")
    print(f"  ratio_nonmonotone_any={ratio_nonmonotone_any} interaction_only={interaction_only} gate0_pass={g0['pass']}")
    print(f"  {msg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
