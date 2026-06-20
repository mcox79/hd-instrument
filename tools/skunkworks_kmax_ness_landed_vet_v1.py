"""Skunkworks INDEPENDENT landed-VET for kmax_ness_envelope_corrected (the K_max NESS CERT-592 candidate).

CORRECTED per the landed-VET disposition: the genuine test is the ARTIFACT-FREE control arm (control K_obs > K_eq),
NOT the mis-spec'd "control recall at cand2's deep_K". Plus the extension-genuineness (ext_hopfrac: fraction of hops where
cleanup snaps to the CORRECT sequential next-node = genuine denoise-and-traverse, vs jumps to a_K = recovery).

Verify-OFF-DATA: recompute K_eq (independent Hopfield), control/K_eq + cand2/K_eq (off k_obs/ctrl_k_obs), the grid-cap
(off cand_curve); READ ext_hopfrac (a runtime per-hop measurement). Read-only, pure-python. ASCII. Run on synced metrics:
  python tools/skunkworks_kmax_ness_landed_vet_v1.py [path/to/metrics.json]

PINNED tier gate (Skunkworks 2026-06-20, data-decides):
  Safe points: 2.5 <= K_eq <= 45 (MODERATE regime).
  HARD_FAIL if control does NOT exceed K_eq on >=4/5 safe (substrate doesn't genuinely exceed equilibrium).
  HARD_PASS_CHAIN_ELIGIBLE (-> rule CERT 592) iff: cand2/K_eq >= 2.0 on >=4/5 safe AND all-extension-genuine
     (ext_hopfrac >= 0.85) AND control/K_eq > 1.0 on >=4/5 safe (genuine depth, cleanup traverses-not-recovers).
  else STRONG MEASURED_MECHANISM (CERT 591): control genuinely exceeds equilibrium (verified floor) but cand2-2x or
     extension-genuine not met on >=4/5 -- the substrate genuinely exceeds equilibrium, not a clean chain-grade.
"""
import sys, json, math

ALPHA_C = 0.138
RECALL_THRESH = 0.9
EXT_GENUINE_FLOOR = 0.85


def k_eq(alpha):
    return 3.3 * (1.0 - alpha / ALPHA_C) ** 2 / alpha


def grid_capped(cand_curve):
    if not cand_curve:
        return False
    ks = sorted(int(k) for k in cand_curve)
    rec = {int(k): v for k, v in cand_curve.items()}
    return rec[ks[-1]] >= RECALL_THRESH  # deepest grid K still passes -> K_obs is floor-capped


def _get(u, *names, default=None):
    for n in names:
        if n in u:
            return u[n]
    return default


def main(path):
    d = json.load(open(path, encoding="utf-8-sig"))
    det = d.get("detail", {}) or {}
    print("=== Skunkworks INDEPENDENT landed-VET: kmax_ness_envelope CORRECTED ===")
    print("path: %s" % path)
    print("cell-reported verdict : %s" % d.get("verdict"))
    print("run_mode              : %s   (expect 'full')" % d.get("run_mode"))

    units = d.get("per_unit") or det.get("per_unit") or []
    if not units:
        print("NO per_unit -> cannot independently recompute. STOP."); return
    by_af = {}
    for u in units:
        by_af.setdefault(u["alpha_frac"], []).append(u)

    print("\n-- per-alpha_frac (INDEPENDENT recompute) --")
    print("  %-6s %-7s %-8s %-8s %-9s %-9s %-7s %-9s %-8s" % (
        "af", "K_eq", "ctrlK", "candK", "ctrl/eq", "cand/eq", "safe", "ext_hopfr", "ext_gen"))
    agg = {}
    for af in sorted(by_af):
        us = by_af[af]
        alpha = us[0]["alpha"]; ke = k_eq(alpha); safe = 2.5 <= ke <= 45.0
        ctrlK = sum(_get(u, "ctrl_k_obs", "ctrlK", default=0.0) for u in us) / len(us)
        candK = sum(_get(u, "k_obs", "cand_k_obs", default=0.0) for u in us) / len(us)
        ext = sum(_get(u, "ext_hopfrac", "extension_hopfrac", "ext_hop_frac", default=float('nan')) for u in us) / len(us)
        capped = any(grid_capped(u.get("cand_curve", {})) for u in us)
        ctrl_ratio = ctrlK / (ke + 1e-9); cand_ratio = candK / (ke + 1e-9)
        ext_gen = (not math.isnan(ext)) and ext >= EXT_GENUINE_FLOOR
        agg[af] = {"k_eq": ke, "ctrl_ratio": ctrl_ratio, "cand_ratio": cand_ratio, "safe": safe,
                   "ext": ext, "ext_gen": ext_gen, "capped": capped}
        print("  %-6.2f %-7.2f %-8.1f %-8.1f %-9.2f %-9.2f %-7s %-9.3f %-8s" % (
            af, ke, ctrlK, candK, ctrl_ratio, cand_ratio, safe, ext, ext_gen))

    safe_afs = [af for af in agg if agg[af]["safe"]]
    n_safe = len(safe_afs)
    ctrl_exceeds = sum(1 for af in safe_afs if agg[af]["ctrl_ratio"] > 1.0)
    cand_2x = sum(1 for af in safe_afs if agg[af]["cand_ratio"] >= 2.0)
    ctrl_2x = sum(1 for af in safe_afs if agg[af]["ctrl_ratio"] >= 2.0)
    all_ext_gen = all(agg[af]["ext_gen"] for af in safe_afs) if safe_afs else False
    any_capped = any(agg[af]["capped"] for af in safe_afs)

    print("\n-- TIER GATE (independent, corrected discriminator) --")
    print("  n_safe (2.5<=K_eq<=45)                  : %d" % n_safe)
    print("  control EXCEEDS K_eq (genuine) on safe  : %d / %d  (>1.0x)" % (ctrl_exceeds, n_safe))
    print("  control >=2x (artifact-free strong)     : %d / %d" % (ctrl_2x, n_safe))
    print("  cand2 >=2x on safe                      : %d / %d" % (cand_2x, n_safe))
    print("  all extension-genuine (ext_hopfrac>=.85): %s" % all_ext_gen)
    print("  any K_obs grid-capped                   : %s" % any_capped)
    if any_capped:
        print("  ** WARNING: grid-capped K_obs -> ratio is a floor. Extend K-grid. **")

    if n_safe < 4 or ctrl_exceeds < 4:
        tier = "HARD_FAIL (control does NOT exceed K_eq on >=4/5 -> substrate doesn't genuinely exceed equilibrium)"
    elif cand_2x >= 4 and all_ext_gen and ctrl_exceeds >= 4:
        tier = "HARD_PASS_CHAIN_ELIGIBLE -> Skunkworks rules CERT 592 (NESS genuinely exceeds equilibrium >=2x; cleanup TRAVERSES not recovers)"
    else:
        tier = ("STRONG MEASURED_MECHANISM (CERT 591): control genuinely exceeds equilibrium (verified floor) but "
                "cand2-2x / extension-genuine not met on >=4/5 -- genuine exceedance, not a clean chain-grade")
    print("  INDEPENDENT TIER : %s" % tier)
    cv = str(d.get("verdict"))
    print("  cell verdict matches independent : %s" % (cv in tier or tier.split()[0] in cv))

    print("\n-- cert-owner notes --")
    print("  K_eq bounded [2.5,45] on all safe : %s" % all(2.5 <= agg[af]["k_eq"] <= 45 for af in safe_afs))
    print("  The CHAIN-GRADE requires: cand2>=2x (>=4/5) AND ext_hopfrac>=0.85 (cleanup traverses, NOT jumps-to-a_K)")
    print("      AND control>K_eq (>=4/5, the genuine-depth floor). If ext_hopfrac high -> the 2x is GENUINE depth -> 592.")
    print("  If ext_hopfrac < 0.85 -> cleanup is jump-recovery at depth -> NOT chain-grade -> strong MEASURED_MECHANISM (control floor).")
    print("\n=== END landed-VET (verify-off-data; data decides CERT 592 vs STRONG MEASURED_MECHANISM) ===")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/exp_kmax_ness_envelope_corrected_v1/metrics.json")
