#!/usr/bin/env python
"""
SKUNKWORKS landed-VET for sparse-#2 (exp_sparse_boundary_v2_cpu_v1).
Independent off-DATA recompute of the capacity-vs-sparsity curve from per_unit
(NOT the rolled-up detail/headline). Verify-the-referent discipline:
  - every reported number must reproduce from per_unit
  - dense denom must be BOUNDED (not divide-by-near-zero)
  - cv must be ~0 (seed-robust)
  - cap-flags correct (>=300x is a LOWER BOUND, alpha_c hit LOADS ceiling)
  - monotone Willshaw super-capacity (alpha_c rises as f falls)
  - crosstalk-onset located? (peak/drop inside the swept range)
Tier gate: MEASURED_MECHANISM (curve characterization; onset NOT located => partial).
ASCII-only. Reads a local metrics.json path (scp the remote copy in first).
Usage: python tools/skunkworks_sparse2_landed_vet_v1.py <path/to/metrics.json>
"""
import json, sys, math

DENSE_FLOOR = 0.005          # dense alpha_c below this == divide-by-near-zero risk
CV_MAX = 0.05                # seed-robustness ceiling
LOADS_CEIL = 6.0             # grid LOADS max -> capped alpha_c == lower bound


def recompute(path):
    d = json.load(open(path))
    pu = d.get("per_unit") or []
    assert pu, "no per_unit -- cannot verify off data"

    # group per_unit by f -> seed alpha_c list + cap flags
    by_f = {}
    for r in pu:
        f = r["f"]
        by_f.setdefault(f, {"ac": [], "capped": []})
        by_f[f]["ac"].append(float(r["alpha_c"]))
        by_f[f]["capped"].append(bool(r.get("alpha_c_capped", False)))

    fs = sorted(by_f.keys())
    dense_f = max(fs)  # f=1.0 dense baseline
    dense_ac = sum(by_f[dense_f]["ac"]) / len(by_f[dense_f]["ac"])

    rows, worst_cv = [], 0.0
    for f in fs:
        ac = by_f[f]["ac"]
        m = sum(ac) / len(ac)
        var = sum((x - m) ** 2 for x in ac) / len(ac)
        sd = math.sqrt(var)
        cv = (sd / m) if m else 0.0
        worst_cv = max(worst_cv, cv)
        capped = any(by_f[f]["capped"])
        gain = m / dense_ac if dense_ac else float("inf")
        rows.append({"f": f, "alpha_c": m, "cv": cv, "capped": capped,
                     "gain_vs_dense": gain, "n_seed": len(ac)})
    return d, rows, dense_ac, dense_f, worst_cv


def gate(d, rows, dense_ac, dense_f, worst_cv):
    print("=== sparse-#2 landed-VET (off per_unit) ===")
    print(f"anchor={d['anchor_name']} run_mode={d['run_mode']} N={d['N']} "
          f"n_seeds={d['n_seeds']} elapsed_s={d.get('elapsed_s'):.0f}")
    print(f"dense baseline f={dense_f} alpha_c={dense_ac:.4f}")
    print(f"{'f':>7} {'alpha_c':>8} {'gain':>8} {'capped':>7} {'cv':>6} {'n':>3}  reported_gain  match")
    rep = d["detail"]["gain_vs_dense_by_f"]
    rep_cap = d["detail"]["alpha_c_capped_by_f"]
    all_match = True
    for r in rows:
        key = f"f{r['f']:.3f}"
        rg = rep.get(key)
        rc = rep_cap.get(key)
        match = (rg is not None and abs(rg - r["gain_vs_dense"]) < 1e-6
                 and bool(rc) == r["capped"])
        all_match = all_match and match
        print(f"{r['f']:>7.3f} {r['alpha_c']:>8.3f} {r['gain_vs_dense']:>8.1f}x "
              f"{str(r['capped']):>7} {r['cv']:>6.3f} {r['n_seed']:>3}  "
              f"{rg:>8.1f}x      {'OK' if match else 'MISMATCH'}")

    # gates
    monotone = all(rows[i]["alpha_c"] >= rows[i + 1]["alpha_c"]
                   for i in range(len(rows) - 1))  # rows sorted ascending f => alpha_c descending
    dense_bounded = dense_ac >= DENSE_FLOOR
    seed_robust = worst_cv <= CV_MAX
    capped_are_ceiling = all(abs(r["alpha_c"] - LOADS_CEIL) < 1e-6
                             for r in rows if r["capped"])
    n_capped = sum(1 for r in rows if r["capped"])
    onset_located = d["detail"].get("crosstalk_onset_f") is not None
    peak_gain = max(r["gain_vs_dense"] for r in rows)
    peak_f = min(r["f"] for r in rows if abs(r["gain_vs_dense"] - peak_gain) < 1e-6)

    print("\n=== gates ===")
    print(f"[{'PASS' if all_match else 'FAIL'}] every gain+cap reproduces from per_unit")
    print(f"[{'PASS' if monotone else 'FAIL'}] monotone Willshaw super-capacity (alpha_c rises as f falls)")
    print(f"[{'PASS' if dense_bounded else 'FAIL'}] dense denom BOUNDED ({dense_ac:.4f} >= {DENSE_FLOOR}) "
          f"-> numerator-driven, NOT divide-by-near-zero")
    print(f"[{'PASS' if seed_robust else 'FAIL'}] seed-robust (worst_cv={worst_cv:.4f} <= {CV_MAX})")
    print(f"[{'PASS' if capped_are_ceiling else 'FAIL'}] capped alpha_c == LOADS ceiling {LOADS_CEIL} "
          f"({n_capped} capped) -> peak gain is a LOWER BOUND")
    print(f"[{'INFO' if not onset_located else 'PASS'}] crosstalk-onset located? "
          f"{onset_located} (None => partial deliverable, file MEASURED_MECHANISM as-is)")
    print(f"\npeak gain = >={peak_gain:.0f}x @ f={peak_f} (LOWER BOUND, capped)")

    cert_neutral_ok = all_match and monotone and dense_bounded and seed_robust and capped_are_ceiling
    print("\n=== TIER ===")
    if cert_neutral_ok and not onset_located:
        print("MEASURED_MECHANISM (CERT-neutral): curve genuine + honest; onset NOT located => "
              "partial characterization, not chain-grade. FILE AS-IS.")
    elif cert_neutral_ok and onset_located:
        print("MEASURED_MECHANISM (CERT-neutral): full curve INCLUDING onset boundary located.")
    else:
        print("HOLD: a verification gate FAILED -- do not atomize until resolved.")
    return cert_neutral_ok


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/sparse2_remote_metrics.json"
    d, rows, dense_ac, dense_f, worst_cv = recompute(path)
    gate(d, rows, dense_ac, dense_f, worst_cv)
