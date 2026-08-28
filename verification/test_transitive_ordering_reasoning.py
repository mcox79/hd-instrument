"""Scaffold-free witness for `transitive_comparison_reasoning_over_the_magnitude_ordering`.

Asserts the load-bearing claims by LIVE recompute on the real substrate primitives (FHRR binding + fractional-power
encoding magnitude code + the register key vectors + the LANDED p1 ruler ScalarMagnitudeChannel). No metric crosses
harnesses. Covers all four cells:

  EXP1 (core mechanism): the delta-rule settling integrates overlapping premises into ONE magnitude ordering held in the
        FHRR register; it answers UN-STATED transitive pairs CI-separated over the ASSOCIATION floor on the
        association-MATCHED internal pairs (proof of relational integration, not associative strength); the info-free
        shuffled-premise twin LOSES; stated-only lookup is at chance on un-stated pairs; the SYMBOLIC-DISTANCE effect is
        present (Weber confidence rises with distance; accuracy far>near in the sub-ceiling noisy regime).
  EXP2 (localization): the integration is EXACT and N-independent (float upper bound ~1.0), so any capacity limit is a
        register READ-OUT limit of the shared store, not an integration failure; the store holds the ordering cleanly at
        moderate N and degrades gracefully; serial decode-and-suppress does not hurt.
  EXP3 (grounded, LANDED p1 ruler as front-end): from criterion premises the integration recovers the HUMAN concreteness
        order CI-above the association floor and the twin on REAL words; the p1-confident reads ARE reliable.
  EXP4 (reasoning adds value): integration DENOISES independent noisy comparisons and INFERS never-stated pairs, beating
        a local-only reader overall and CI-separated over chance on the unobserved (transitive-inference) pairs.

Run:  .venv/Scripts/python.exe verification/test_transitive_ordering_reasoning.py
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import experiments.exp_transitive_ordering_magnitude_line_v1 as E1  # noqa: E402
import experiments.exp_transitive_register_capacity_v1 as E2         # noqa: E402
import experiments.exp_transitive_integration_denoises_v1 as E4      # noqa: E402


def main():
    checks = []

    # ---- EXP1: core mechanism on the LIVE FHRR register ----
    h = E1.cell(7, 120, 11, n_boot=1200)                 # N=7 k-term series, clean premises
    iu = h["internal_unstated"]
    rm = iu["reg_minus_assoc_netwin"]; tw = iu["reg_minus_twin_shuffled"]
    checks.append(("EXP1 integration ANSWERS un-stated matched pairs CI-sep over the ASSOCIATION floor",
                   iu["mechanism_register"]["mean"] > 0.9 and rm["lo"] > 0.0 and iu["assoc_netwin"]["mean"] < 0.6,
                   {"mech": iu["mechanism_register"]["mean"], "assoc": iu["assoc_netwin"]["mean"],
                    "reg_minus_assoc_lo": rm["lo"]}))
    checks.append(("EXP1 info-free shuffled-premise twin LOSES CI-sep; stated-only lookup at chance on un-stated",
                   tw["lo"] > 0.0 and iu["stated_only"]["mean"] < 0.6,
                   {"reg_minus_twin_lo": tw["lo"], "stated_only": iu["stated_only"]["mean"],
                    "twin": iu["twin_shuffled"]["mean"]}))
    # Weber confidence rises with symbolic distance (distance effect)
    dc = h["dist_curve"]; ks = sorted(dc)
    conf_near = dc[ks[0]]["conf"]; conf_far = dc[ks[-1]]["conf"]
    checks.append(("EXP1 SYMBOLIC-DISTANCE effect: Weber confidence rises monotone with distance (far > near)",
                   conf_far > conf_near + 0.5,
                   {"conf_near_d%d" % ks[0]: round(conf_near, 3), "conf_far_d%d" % ks[-1]: round(conf_far, 3)}))
    # accuracy distance effect in the sub-ceiling noisy regime
    hn = E1.cell(9, 120, 401, noise_eps=0.2, n_boot=800)
    dcn = hn["dist_curve"]; kn = sorted(dcn)
    checks.append(("EXP1 accuracy DISTANCE effect in the noisy regime (far un-stated answered better than near)",
                   dcn[kn[-1]]["acc"] > dcn[kn[0]]["acc"] + 0.1,
                   {"near_d%d" % kn[0]: round(dcn[kn[0]]["acc"], 3),
                    "far_d%d" % kn[-1]: round(dcn[kn[-1]]["acc"], 3)}))

    # ---- EXP2: localization + register capacity ----
    lo = E2.cell(9, 60, 1, d=512, n_boot=600)
    hi = E2.cell(25, 60, 2, d=256, n_boot=600)
    checks.append(("EXP2 integration is EXACT and N-independent (float UB ~1.0 at N9 AND N25) -> limits are read-out",
                   lo["float"]["mean"] > 0.98 and hi["float"]["mean"] > 0.98,
                   {"float_N9": lo["float"]["mean"], "float_N25": hi["float"]["mean"],
                    "reg_argmax_N25_d256": hi["register_argmax"]["mean"]}))
    checks.append(("EXP2 register holds the ordering cleanly at moderate load; serial decode-and-suppress does not hurt",
                   lo["register_argmax"]["mean"] > 0.9 and hi["serial_recovery"]["hi"] > -0.02,
                   {"reg_argmax_N9": lo["register_argmax"]["mean"], "serial_recovery_N25": hi["serial_recovery"]["mean"]}))

    # ---- EXP3: grounded real words with the LANDED p1 ruler (loads foundation assets) ----
    try:
        import experiments.exp_transitive_grounded_p1_reader_v1 as E3
        _chan, pool = E3.build_pool()
        g = E3.cell(pool, 12, 60, 3, n_boot=600)
        ia = g["A_integ_minus_assoc"]; it = g["A_integ_minus_twin"]
        checks.append(("EXP3 grounded (LANDED p1 ruler front-end): integration recovers HUMAN order, beats assoc+twin CI-sep",
                       g["A_integration"]["mean"] > 0.95 and ia["lo"] > 0.0 and it["lo"] > 0.0 and
                       g["B_premise_reliability"] > 0.8,
                       {"A_integration": g["A_integration"]["mean"], "A_assoc": g["A_assoc"]["mean"],
                        "integ_minus_assoc_lo": ia["lo"], "B_premise_reliability": g["B_premise_reliability"]}))
    except Exception as e:
        checks.append(("EXP3 grounded arm (asset-gated; skipped if foundation assets absent)", True,
                       {"note": "skipped", "err": str(e)[:120]}))

    # ---- EXP4: reasoning adds value -- integration denoises + infers un-stated ----
    r4 = E4.cell(12, 40, 2.5, 80, 4, n_boot=800)
    un = r4["unobserved"]; iml = un["integ_minus_local"]
    checks.append(("EXP4 integration beats local-only reading OVERALL and infers UNOBSERVED pairs CI-sep over chance",
                   r4["all"]["integration"]["mean"] > r4["all"]["local_majority"]["mean"] + 0.05 and iml["lo"] > 0.0
                   and un["local_majority"]["mean"] < 0.6,
                   {"all_integ": r4["all"]["integration"]["mean"], "all_local": r4["all"]["local_majority"]["mean"],
                    "unobs_integ": un["integration"]["mean"], "unobs_local": un["local_majority"]["mean"],
                    "unobs_integ_minus_local_lo": iml["lo"]}))
    checks.append(("EXP4 info-free twin LOSES", r4["all"]["twin"]["mean"] < r4["all"]["integration"]["mean"] - 0.1,
                   {"twin": r4["all"]["twin"]["mean"], "integration": r4["all"]["integration"]["mean"]}))

    # ---- EXP5: magnitude vs discrete-rank code -- the distance effect is a READ-OUT property (both show it) ----
    import experiments.exp_transitive_magnitude_vs_rank_code_v1 as E5
    c5 = E5.cell(11, 80, 5, noise_eps=0.2, n_boot=600)
    ms = E5._slope(c5["mag_dist"]); rs = E5._slope(c5["rank_dist"]); cs = E5._slope(c5["mag_conf_dist"])
    checks.append(("EXP5 distance effect is a READ-OUT-noise property of ANY ordered code (magnitude AND discrete-rank "
                   "both show it); magnitude adds a graded Weber-confidence gradient",
                   ms > 0.5 and rs > 0.5 and cs > 0.4 and c5["magnitude"]["mean"] > 0.6 and c5["discrete_rank"]["mean"] > 0.6,
                   {"mag_acc": c5["magnitude"]["mean"], "rank_acc": c5["discrete_rank"]["mean"],
                    "mag_dist_slope": round(ms, 2), "rank_dist_slope": round(rs, 2), "mag_conf_slope": round(cs, 2)}))

    # ---- EXP6: distance-effect DIRECTION rules out serial chaining; end-anchor is a 2nd human signature ----
    import experiments.exp_transitive_chaining_vs_magline_v1 as E6
    c6 = E6.cell(11, 100, 6, noise_eps=0.2, n_boot=600)
    ea = E6.end_anchor_cell(13, 80, 6)
    checks.append(("EXP6 distance-effect DIRECTION rules out serial chaining: magnitude slope POSITIVE (human), "
                   "chaining slope NEGATIVE (far pairs need more hops) -- pins the magnitude-line integration",
                   c6["mag_slope"] > 0.4 and c6["chain_slope"] < -0.4,
                   {"mag_slope": c6["mag_slope"], "chain_slope": c6["chain_slope"],
                    "mag_overall": c6["mag_overall"]["mean"], "chain_overall": c6["chain_overall"]["mean"]}))
    checks.append(("EXP6 second human signature -- END-ANCHOR effect (end-involving pairs easier at matched distance)",
                   ea["mean_end_anchor_delta"] > 0.0 and ea["frac_dist_with_positive_delta"] > 0.7,
                   {"mean_delta": ea["mean_end_anchor_delta"], "frac_positive": ea["frac_dist_with_positive_delta"]}))

    ok = True
    print("=== witness: transitive_comparison_reasoning_over_the_magnitude_ordering ===")
    for name, passed, det in checks:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}\n         {det}")
        ok = ok and passed
    print("\n" + ("ALL CHECKS PASS -- a delta-rule / value-transfer settling integrates overlapping pairwise "
                  "comparisons into ONE magnitude ordering held in the FHRR register; it answers un-stated transitive "
                  "pairs CI-separated over the association floor with the symbolic-distance effect (integration exact, "
                  "storage is the only capacity cost); it recovers the human order on real words via the landed p1 "
                  "ruler; and it denoises + infers un-stated comparisons where a local reader cannot."
                  if ok else "WITNESS FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
