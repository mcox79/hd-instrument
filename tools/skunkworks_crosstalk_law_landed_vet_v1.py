"""Skunkworks INDEPENDENT landed-VET for crosstalk_capacity_law_v1 (reframed isotropy #6).

Verify-OFF-DATA: recompute every correlation/partial/c-spread from per_unit MYSELF (do NOT trust the cell's
reported detail) -> compare to the cell's compute_verdict -> apply the tier gate + cert-owner judgments.
Read-only, pure-python (no venv/torch needed -- just json). ASCII. Run on the synced metrics.json at landing:
  python tools/skunkworks_crosstalk_law_landed_vet_v1.py [path/to/metrics.json]

Tier gate (Skunkworks band ruling 2026-06-20):
  FLOOR MEASURED_MECHANISM = crosstalk-Pearson > BOTH control |Pearson| (dominance) AND Spearman > 0.70. CERT 591.
  HARD_PASS_CHAIN_ELIGIBLE (-> rule 592) = + n>=8 + Spearman>0.80 + crosstalk>0.80 + c_spread<=3.0
     + BOTH partial(control|crosstalk) < 0.30 (controls add NO independent power = rigorous 2-controls-fail).
  HARD_FAIL = crosstalk NOT dominant (a control |r| >= crosstalk) OR Spearman<=0.70.
The partial(control|crosstalk) decides: ~0 = crosstalk-in-disguise (genuinely fails) ; survives = INDEPENDENT predictor (report, don't bury).
"""
import sys, json, math


def pearson(x, y):
    n = len(x)
    if n < 2:
        return 0.0
    mx = sum(x) / n; my = sum(y) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x); syy = sum((b - my) ** 2 for b in y)
    return sxy / math.sqrt(sxx * syy) if sxx > 1e-12 and syy > 1e-12 else 0.0


def _rank(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    r = [0] * len(v)
    for pos, i in enumerate(order):
        r[i] = pos
    return r


def spearman(x, y):
    return pearson(_rank(x), _rank(y))


def partial(r_xy, r_xz, r_yz):
    den = (1 - r_xz ** 2) * (1 - r_yz ** 2)
    return (r_xy - r_xz * r_yz) / math.sqrt(den) if den > 1e-12 else float('nan')


def _cmp(label, mine, cell):
    flag = ""
    try:
        if cell is not None and abs(float(mine) - float(cell)) > 0.02:
            flag = "  <-- MISMATCH vs cell (recompute disagrees -> investigate)"
    except (TypeError, ValueError):
        pass
    print("  %-32s mine=%7.3f   cell=%s%s" % (label, mine, cell, flag))


def main(path):
    d = json.load(open(path))
    det = d.get("detail", {}) or {}
    print("=== Skunkworks INDEPENDENT landed-VET: crosstalk_capacity_law_v1 ===")
    print("path: %s" % path)
    print("cell-reported verdict : %s" % d.get("verdict"))
    print("run_mode              : %s   (expect 'full')" % d.get("run_mode"))

    units = d.get("per_unit") or det.get("per_unit")
    if units:
        per = {}
        for u in units:
            per.setdefault(u["encoder"], []).append(u)
        agg = {}
        for eid, us in per.items():
            agg[eid] = {"short": us[0]["short"],
                        "iso": sum(u["isoscore"] for u in us) / len(us),
                        "deff": sum(u["d_eff"] for u in us) / len(us),
                        "mcrit": sum(u["m_crit"] for u in us) / len(us),
                        "inv": sum(u["inv_e_sq"] for u in us) / len(us),
                        "c": sum(u["c_cleanup_boost"] for u in us) / len(us),
                        "D": us[0].get("actual_D", us[0].get("nominal_D")),
                        "n_seeds": len(us)}
        src = "per_unit (INDEPENDENT aggregate, n_units=%d)" % len(units)
    else:
        pe = det.get("per_encoder", {})
        agg = {eid: {"short": v["short"], "iso": v["isoscore"], "deff": v["d_eff"], "mcrit": v["m_crit"],
                     "inv": v["inv_e_sq"], "c": v["c"], "D": v["D"], "n_seeds": "?"} for eid, v in pe.items()}
        src = "detail.per_encoder (agg only; per_unit ABSENT -> can't recheck aggregation)"

    encs = list(agg.keys()); n = len(encs)
    shorts = sorted(agg[e]["short"] for e in encs)
    print("recompute source      : %s" % src)
    print("n_encoders            : %d   (expect >=8 for chain-eligible)" % n)
    print("encoders              : %s" % ", ".join(shorts))
    print("pythia-2.8b present   : %s   (version-marker)" % any(("2.8b" in s or "2p8b" in s) for s in shorts))
    if n < 3:
        print("n<3 -> cannot compute cross-encoder correlation. STOP."); return

    logcap = [math.log(agg[e]["mcrit"] + 1) for e in encs]
    loginv = [math.log(agg[e]["inv"] + 1) for e in encs]
    iso = [agg[e]["iso"] for e in encs]; deff = [agg[e]["deff"] for e in encs]
    cs = [agg[e]["c"] for e in encs]; dd = [agg[e]["D"] for e in encs]

    r_cross = pearson(loginv, logcap)
    sp = spearman([agg[e]["inv"] for e in encs], [agg[e]["mcrit"] for e in encs])
    r_iso = pearson(iso, logcap); r_deff = pearson(deff, logcap)
    p_deff = partial(r_deff, pearson(deff, loginv), r_cross)
    p_iso = partial(r_iso, pearson(iso, loginv), r_cross)
    c_spread = max(cs) / (min(cs) + 1e-9)

    print("\n-- INDEPENDENT recompute vs cell-reported (mismatch flag if |diff|>0.02) --")
    _cmp("Pearson(crosstalk,logMcrit)", r_cross, det.get("pearson_crosstalk_vs_logMcrit"))
    _cmp("Spearman(crosstalk,Mcrit)", sp, det.get("spearman_crosstalk_vs_Mcrit"))
    _cmp("Pearson(d_eff,logMcrit) CTRL", r_deff, det.get("pearson_deff_vs_logMcrit_CONTROL"))
    _cmp("Pearson(IsoScore,logMcrit) CTRL", r_iso, det.get("pearson_isoscore_vs_logMcrit_CONTROL"))
    _cmp("partial(d_eff|crosstalk)", p_deff, det.get("partial_pearson_deff_given_crosstalk"))
    _cmp("partial(IsoScore|crosstalk)", p_iso, det.get("partial_pearson_isoscore_given_crosstalk"))
    _cmp("c_spread (max/min)", c_spread, det.get("c_spread_max_over_min"))

    dominant = r_cross > max(abs(r_iso), abs(r_deff))
    floor = dominant and sp > 0.70
    p_fail = abs(p_deff) < 0.30 and abs(p_iso) < 0.30
    chain = (n >= 8 and sp > 0.80 and r_cross > 0.80 and c_spread <= 3.0 and p_fail)
    tier = ("HARD_FAIL (crosstalk NOT dominant or Spearman<=0.70)" if not floor else
            "HARD_PASS_CHAIN_ELIGIBLE -> Skunkworks rules 592" if chain else
            "MEASURED_MECHANISM (CERT stays 591)")

    print("\n-- TIER GATE (independent) --")
    print("  dominant (crosstalk > both |controls|) : %s" % dominant)
    print("  Spearman > 0.70                        : %s (%.3f)" % (sp > 0.70, sp))
    print("  partial-controls-fail (both |p|<0.30)  : %s" % p_fail)
    print("  chain-criteria (n>=8 & Sp>0.80 & r>0.80 & c-spread<=3 & p-fail): %s" % chain)
    print("  INDEPENDENT TIER : %s" % tier)
    cell_v = str(d.get("verdict"))
    print("  cell verdict matches independent       : %s" % (cell_v in tier or tier.split()[0] in cell_v))

    def _judge(name, r, p):
        if abs(p) < 0.30:
            v = "crosstalk-in-disguise (genuinely FAILS -- partial ~0 controlling for crosstalk)"
        elif n < 8:
            v = ("partial=%+.2f at n=%d is likely DEGENERATE (~1 df small-n -> unstable); NOT a reliable "
                 "independent signal -> DEFER to n>=8 (do NOT conclude independent predictor)" % (p, n))
        else:
            v = "INDEPENDENT predictor -- partial SURVIVES at n=%d -> report as a real 2nd finding, do NOT bury under 'fails'" % n
        print("  %-8s : r=%+.2f partial=%+.2f -> %s" % (name, r, p, v))

    print("\n-- cert-owner judgments --")
    if n < 8:
        print("  [SMALL-N GUARD] n=%d: partial correlations partial 1 var with ~%d df -> EXTREME partials (|p|->1) are "
              "likely degeneracy, not signal. The full n=13 run is the real partial test." % (n, max(0, n - 2)))
    _judge("d_eff", r_deff, p_deff)
    _judge("IsoScore", r_iso, p_iso)
    print("  c bounded (spread<=3x) : %s -> %s" % (
        c_spread <= 3.0, "chain-grade c-criterion MET (c-derivation can formalize)" if c_spread <= 3.0
        else "MEASURED_MECHANISM (c unbounded; not parameter-free)"))
    print("  c_bound pearson(c,D)=%.3f  pearson(c,iso)=%.3f  (is c predictable from an encoder property?)" % (
        pearson(dd, cs), pearson(iso, cs)))
    if r_cross > 0.99:
        print("  UP-GUARD: crosstalk-Pearson>0.99 -> CHECK metric-overlap (E[<>^2] must not be trivially ~ M_crit)")
    print("  worst m_crit CV (seed stability)       : %s" % det.get("worst_m_crit_cv"))
    print("\n=== END landed-VET (verify-off-data; my tier ruling is the chain-grade-592 call) ===")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/exp_crosstalk_capacity_law_v1_gpu_v1/metrics.json")
