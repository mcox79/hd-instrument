"""Scaffold-free WITNESS for grounded_role_assignment_via_verb_keyed_thematic_fit.

Recomputes the headline from source (no cached metrics trusted). The result is an HONEST PARTIAL:

  1. AGGREGATE win is STRUCTURAL ROUTING, not thematic fit: recruiting the structural override ONLY on
     reliable strong-passive morphology (else word order) beats BOTH named floors -- word order AND the
     landed graded_role assigner -- on the full held-out set, paired-CI-separated, without regressing
     canonical or reversible. No thematic fit is used.
  2. Grounded thematic fit's GENUINE contribution is confined to the structure-silent / uncertainty
     regime: on the class-imbalanced non-canonical subset the fit gate beats WORD ORDER and its own
     INFO-FREE TWIN on BALANCED accuracy, paired-CI-separated.
  3. The brief's premise is REFUTED for clean parses: the fit gate does NOT beat the structural assigner
     on raw non-canonical accuracy (graded_role's animacy cue already supplies coarse plausibility) --
     exactly what the noisy-channel / Trueswell account predicts (fit is a disambiguation-under-
     uncertainty mechanism; a gold parse removes the uncertainty).

Run: .venv/Scripts/python.exe verification/test_grounded_role_gate_organ.py
"""
from __future__ import annotations

import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import experiments.exp_grounded_role_gate_v1 as EXP  # noqa: E402


def main():
    m = EXP.run()
    t = m["table"]; c = m["claims"]; v = m["verdict"]
    checks = []

    checks.append((f"AGGREGATE: strong-passive routing (no fit) {t['route_only']['ALL']} beats word order "
                   f"{t['order']['ALL']} paired-CI-sep (lo {c['route_vs_order_ALL'][1]}>0)",
                   c["route_vs_order_ALL"][1] > 0))
    checks.append((f"AGGREGATE: routing beats the landed graded_role {t['graded_role']['ALL']} paired-CI-sep "
                   f"(lo {c['route_vs_graded_ALL'][1]}>0)", c["route_vs_graded_ALL"][1] > 0))
    checks.append((f"routing does NOT regress canonical ({t['route_only']['canonical']}>=0.99) or reversible "
                   f"({t['route_only']['reversible']}==1.0)",
                   t["route_only"]["canonical"] >= 0.99 and t["route_only"]["reversible"] == 1.0))

    checks.append((f"thematic fit beats WORD ORDER on BALANCED non-canonical "
                   f"({t['gate_count']['NONCANON_bal']} vs {t['order']['NONCANON_bal']}) paired-CI-sep "
                   f"(lo {c['gateC_vs_order_NONCANON_bal'][1]}>0)", c["gateC_vs_order_NONCANON_bal"][1] > 0))
    checks.append((f"thematic fit beats its INFO-FREE TWIN on BALANCED non-canonical "
                   f"({t['gate_count']['NONCANON_bal']} vs {t['gate_twin']['NONCANON_bal']}) paired-CI-sep "
                   f"(lo {c['gateC_vs_twin_NONCANON_bal'][1]}>0)", c["gateC_vs_twin_NONCANON_bal"][1] > 0))
    checks.append((f"thematic fit beats WORD ORDER on the structure-silent residual "
                   f"({t['gate_count']['resid_nc']} vs {t['order']['resid_nc']}, n={m['n_resid_nc']}) "
                   f"paired-CI-sep (lo {c['gateC_vs_order_residNC'][1]}>0)", c["gateC_vs_order_residNC"][1] > 0))
    checks.append((f"thematic fit beats its TWIN on the structure-silent residual paired-CI-sep "
                   f"(lo {c['gateC_vs_twin_residNC'][1]}>0)", c["gateC_vs_twin_residNC"][1] > 0))

    checks.append((f"BRIEF PREMISE REFUTED (clean parses): fit {t['gate_count']['NONCANON_raw']} does NOT beat "
                   f"the structural assigner {t['graded_role']['NONCANON_raw']} on RAW non-canonical "
                   f"(structure+animacy already wins where morphology is present)",
                   v["brief_premise_refuted_on_clean_parses_raw_noncanon"]))
    checks.append(("HONEST bound: fit does NOT CI-separate from graded_role on the residual "
                   f"(delta {c['gateC_vs_graded_residNC'][0]} lo {c['gateC_vs_graded_residNC'][1]}<=0) -- "
                   "graded_role's animacy cue supplies coarse plausibility; reported, not hidden",
                   c["gateC_vs_graded_residNC"][1] <= 0))

    # WEAK-PARSER DEPLOYMENT REGIME (route A): where the mechanism lives. On the reader's own noisy front-end
    # (modern role-balanced gold), the fit gate beats BOTH floors on non-canonical CI-sep + twin loses, and
    # generalises to unseen (verb,noun) pairs -- but regresses canonical (the irreducible tradeoff = bar's P2).
    import experiments.exp_grounded_role_weak_parser_v1 as WP
    w = WP.run()
    wc = w["claims"]; wt = w["table"]; wg = w["generalization"]
    checks.append((f"WEAK-PARSER: fit gate beats word order on non-canonical ({wt['PRE_noncanon']['gate']} vs "
                   f"{wt['PRE_noncanon']['order']}, n={wt['n_pre']}) CI-sep (lo {wc['gate_vs_order_PRE'][1]}>0)",
                   wc["gate_vs_order_PRE"][1] > 0))
    checks.append((f"WEAK-PARSER: fit gate beats the structural assigner on non-canonical "
                   f"({wt['PRE_noncanon']['gate']} vs {wt['PRE_noncanon']['graded_role']}) CI-sep "
                   f"(lo {wc['gate_vs_graded_PRE'][1]}>0)", wc["gate_vs_graded_PRE"][1] > 0))
    checks.append((f"WEAK-PARSER: info-free twin LOSES on non-canonical (lo {wc['gate_vs_twin_PRE'][1]}>0)",
                   wc["gate_vs_twin_PRE"][1] > 0))
    checks.append((f"WEAK-PARSER: GENERALISES to unseen (verb,noun) pairs (n={wg['n_pre_unseen']}): gate "
                   f"{wg['gate']} beats order (lo {wg['gate_vs_order_PRE_UNSEEN'][1]}>0) AND structure "
                   f"(lo {wg['gate_vs_graded_PRE_UNSEEN'][1]}>0)",
                   wg["gate_vs_order_PRE_UNSEEN"][1] > 0 and wg["gate_vs_graded_PRE_UNSEEN"][1] > 0))
    checks.append((f"WEAK-PARSER: irreducible tradeoff -- gate REGRESSES canonical "
                   f"({wt['POST_canon']['gate']} vs {wt['POST_canon']['order']}), so P1 fails but the bar's "
                   f"rigorous-negative P2 clause is met with power",
                   (not w["verdict"]["clean_SOLVED_bar_met_P1"]) and w["verdict"]["rigorous_negative_P2_met"]))

    print()
    npass = 0
    for name, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        npass += int(ok)
    print(f"\n{npass}/{len(checks)} checks PASS  (brain-faithful noisy-channel conflict gate: on clean parses "
          f"structural routing owns the aggregate; in the WEAK-PARSER deployment regime the fit gate beats both "
          f"floors on non-canonical + generalises, but the canonical tradeoff is irreducible = the bar's P2 pass)")
    if npass != len(checks):
        sys.exit(1)


if __name__ == "__main__":
    main()
