"""Skunkworks INDEPENDENT landed-VET for kmax_ness_envelope (the K_max NESS chain-grade CERT-592 candidate).

Verify-OFF-DATA: recompute K_eq (independent Hopfield formula), the genuine-multi-hop flag (off ctrl_curve), the
grid-cap check (off cand_curve), and the tier per the PINNED data-decides disposition -- do NOT trust the cell's reported
verdict. Read-only, pure-python. ASCII. Run on the synced metrics at landing:
  python tools/skunkworks_kmax_ness_landed_vet_v1.py [path/to/metrics.json]

PINNED tier gate (Skunkworks 2026-06-20):
  Gate ONLY safe points: 2.5 <= K_eq <= 45 (MODERATE regime; both K_eq limits avoided).
  HARD_FAIL if NOT all-genuine (cleanup-OFF recall < 0.30 at deep_K -> cleanup-RECOVERY artifact, not depth).
  HARD_PASS_CHAIN_ELIGIBLE (-> rule 592) if ratio_to_eq >= 2.0 across >=4/5 safe points AND all-genuine.
  MIDDLE_BAND if >=2x at 2-3 safe points.
  MEASURED_MECHANISM (CERT 591) if matches equilibrium (~1.0, not >=2x) AND all-genuine -- real equilibrium-validation.
  UNKNOWN if <4 safe points.
  GRID-CAP guard: if deep_K == max(K_grid) with recall>=0.9, K_obs is FLOOR-capped (not measured) -> the ratio is invalid.
"""
import sys, json, math

ALPHA_C = 0.138
RECALL_THRESH = 0.9
GENUINE_FLOOR = 0.30


def k_eq(alpha):
    return 3.3 * (1.0 - alpha / ALPHA_C) ** 2 / alpha


def interp_kmax(curve):
    # curve: dict {K(int-or-str): recall}; max depth K with recall>=thresh, linearly interpolated to the first-fail.
    ks = sorted(int(k) for k in curve)
    rec = {int(k): v for k, v in curve.items()}
    last_ok = ks[0]
    for k in ks:
        if rec[k] >= RECALL_THRESH:
            last_ok = k
        else:
            # interpolate between last_ok (>=thresh) and k (<thresh)
            r0, r1 = rec[last_ok], rec[k]
            if r0 > r1:
                frac = (r0 - RECALL_THRESH) / (r0 - r1)
                return last_ok + frac * (k - last_ok), False  # measured (a real cliff in-grid)
            return float(last_ok), False
    return float(last_ok), True  # never dropped below thresh -> GRID-CAPPED at the max K


def main(path):
    d = json.load(open(path, encoding="utf-8-sig"))
    det = d.get("detail", {}) or {}
    print("=== Skunkworks INDEPENDENT landed-VET: kmax_ness_envelope ===")
    print("path: %s" % path)
    print("cell-reported verdict : %s" % d.get("verdict"))
    print("run_mode              : %s   (expect 'full')" % d.get("run_mode"))

    units = d.get("per_unit") or det.get("per_unit") or []
    if not units:
        print("NO per_unit -> cannot independently recompute. STOP."); return
    by_af = {}
    for u in units:
        by_af.setdefault(u["alpha_frac"], []).append(u)

    print("\n-- per-alpha_frac (INDEPENDENT recompute off cand/ctrl curves) --")
    print("  %-7s %-8s %-7s %-7s %-7s %-9s %-8s %-7s" % ("af", "K_eq", "K_obs", "ratio", "safe", "genuine", "capped", "ctrl@dp"))
    agg = {}
    for af in sorted(by_af):
        us = by_af[af]
        alpha = us[0]["alpha"]
        ke = k_eq(alpha)
        safe = 2.5 <= ke <= 45.0
        kobs_list, ratio_list, genuine_list, capped_list, ctrl_list = [], [], [], [], []
        for u in us:
            cand = u.get("cand_curve", {}); ctrl = u.get("ctrl_curve", {})
            if cand:
                kobs, capped = interp_kmax(cand)
            else:
                kobs, capped = u.get("k_obs", 0.0), False
            ratio = kobs / (ke + 1e-9)
            # genuine: cleanup-OFF recall at the deepest K where cand still passed
            deep_K = max((int(k) for k, r in cand.items() if r >= RECALL_THRESH), default=None) if cand else u.get("deep_K")
            ctrl_at = (ctrl.get(str(deep_K), ctrl.get(deep_K, 0.0)) if (ctrl and deep_K is not None) else u.get("ctrl_at_deep", 0.0))
            genuine = ctrl_at >= GENUINE_FLOOR
            kobs_list.append(kobs); ratio_list.append(ratio); genuine_list.append(genuine)
            capped_list.append(capped); ctrl_list.append(ctrl_at)
        mk = sum(kobs_list) / len(kobs_list); mr = sum(ratio_list) / len(ratio_list)
        mctrl = sum(ctrl_list) / len(ctrl_list)
        all_gen = all(genuine_list); any_capped = any(capped_list)
        agg[af] = {"k_eq": ke, "k_obs": mk, "ratio": mr, "safe": safe, "genuine": all_gen, "capped": any_capped}
        print("  %-7.2f %-8.2f %-7.1f %-7.2f %-7s %-9s %-8s %-7.3f" % (
            af, ke, mk, mr, safe, all_gen, any_capped, mctrl))

    safe_afs = [af for af in agg if agg[af]["safe"]]
    n_safe = len(safe_afs)
    all_genuine = all(agg[af]["genuine"] for af in safe_afs) if safe_afs else False
    any_capped = any(agg[af]["capped"] for af in safe_afs)
    ge2 = sum(1 for af in safe_afs if agg[af]["ratio"] >= 2.0)

    print("\n-- TIER GATE (independent, pinned data-decides) --")
    print("  n_safe_points (2.5<=K_eq<=45)        : %d  (expect >=4)" % n_safe)
    print("  all safe points genuine (ctrl>=0.30) : %s" % all_genuine)
    print("  ratio>=2x across safe points         : %d / %d" % (ge2, n_safe))
    print("  any K_obs GRID-CAPPED (invalid ratio): %s" % any_capped)
    if any_capped:
        print("  ** WARNING: grid-capped K_obs -> ratio is a FLOOR, not measured. Extend K-grid / re-run before ruling. **")
    if n_safe < 4:
        tier = "UNKNOWN (<4 safe points)"
    elif not all_genuine:
        tier = "HARD_FAIL (a safe point is NOT genuine -> cleanup-recovery artifact, not depth)"
    elif ge2 >= 4:
        tier = "HARD_PASS_CHAIN_ELIGIBLE -> Skunkworks rules CERT 592 (NESS genuinely exceeds equilibrium >=2x)"
    elif ge2 >= 2:
        tier = "MIDDLE_BAND (>=2x at 2-3 safe points -- partial)"
    else:
        tier = "MEASURED_MECHANISM (CERT 591): matches equilibrium (~1.0), genuine -- single-substrate ~ Hopfield"
    print("  INDEPENDENT TIER : %s" % tier)
    cv = str(d.get("verdict"))
    print("  cell verdict matches independent : %s" % (cv in tier or tier.split()[0] in cv))

    print("\n-- cert-owner checks --")
    print("  K_eq bounded [~2.5,45] on all safe points: %s" % all(2.5 <= agg[af]["k_eq"] <= 45 for af in safe_afs))
    print("  mean ratio (safe)                        : %.2f  [cell: %s]" % (
        (sum(agg[af]["ratio"] for af in safe_afs) / max(1, n_safe)), det.get("mean_ratio_to_eq")))
    print("  all_genuine_multihop                     : %s  [cell: %s]" % (all_genuine, det.get("all_genuine_multihop")))
    print("  If chain-eligible: the 2x is GENUINE depth (not cleanup-recovery) -- the load-bearing tie-in.")
    print("\n=== END landed-VET (verify-off-data; data decides CERT 592 vs MEASURED_MECHANISM) ===")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/exp_kmax_ness_envelope_gpu_v1/metrics.json")
