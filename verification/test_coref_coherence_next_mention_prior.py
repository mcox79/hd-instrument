"""Scaffold-free witness for the_reader_has_no_coherence_next_mention_prior.

Asserts the load-bearing claims of the RIGOROUS NEGATIVE without the full run:
  1. MECHANISM WORKS (positive control): the coherence next-mention prior flips constructed coherence-decisive
     minimal pairs -- selectional grounded fit (water>jug etc.) and implicit-causality -- where the structural
     likelihood and an info-free shuffle are at chance. The metric CAN move.
  2. BAYESIAN-PRODUCT FUSION works: a strong prior flips the fused pick (likelihood x prior).
  3. THE RESIDUAL IS FINE-DISTANCE-REACHABLE, NOT COHERENCE-REACHABLE (the diagnosis): on a real LitBank slice,
     the fine-grained token-distance ORACLE recovers a large fraction of the structurally-dominated residual
     while the faithful coherence prior's ORACLE is near-zero -- and the fused coherence prior does NOT beat its
     info-free twin (verdict = RIGOROUS_NEGATIVE).

Run: .venv/Scripts/python.exe verification/test_coref_coherence_next_mention_prior.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from experiments.exp_coref_coherence_next_mention_prior_v1 import (  # noqa: E402
    cell, positive_control, self_test)


def main():
    checks = []

    # 1 + 2: mechanism + fusion (deterministic, fast)
    self_test()
    checks.append(("mechanism+fusion self-test", True))

    pc = positive_control(2026)
    ok_sel = pc["selectional_prior_correct"] >= 7 and pc["selectional_prior_correct"] > pc["selectional_infofree_twin_correct"]
    ok_ic = pc["ic_prior_correct"] == pc["ic_pairs"] and pc["ic_prior_correct"] > pc["ic_structural_chance_correct"]
    checks.append(("positive control: selectional prior flips pairs, beats info-free twin", ok_sel))
    checks.append(("positive control: IC prior flips pairs, beats structural chance", ok_ic))

    # 3: the diagnosis, on a real LitBank slice
    m = cell(docs=24, n_boot=400)
    oc = m["ORACLE_ceilings_on_TEST_residual"]
    fine = oc["fine_distance"]["acc_overall"]
    coh = oc["combined"]["acc_overall"]
    checks.append((f"fine-distance oracle ({fine:.3f}) >> coherence-prior oracle ({coh:.3f}) on the residual",
                   fine > 0.25 and fine > 5 * max(coh, 1e-6)))
    ra = m["residual_accuracy_TEST"]
    prior_acc = ra["plus_coherence_prior"]["acc"]
    twin_acc = ra["plus_prior_infofree_twin"]["acc"]
    checks.append((f"coherence prior ({prior_acc:.3f}) does NOT beat its info-free twin ({twin_acc:.3f})",
                   m["prior_minus_infofree_twin_paired"]["band"] != "ABOVE"))
    checks.append((f"verdict is RIGOROUS_NEGATIVE (got {m['verdict']})", m["verdict"] == "RIGOROUS_NEGATIVE"))

    # 4b: the CROSS-DOMAIN correction -- a CLEAN parse (modern GAP prose) does NOT recover the residual
    import csv
    from experiments.exp_coref_residual_crossdomain_gap_v1 import run as gap_run, GAP
    grows = list(csv.DictReader(open(GAP, encoding="utf-8"), delimiter="\t"))[:300]
    g = gap_run(grows)
    comb = g["residual_clean_parse_structural"]["combined"]
    full_subj = g["full_set"]["subjecthood"]
    checks.append((f"GAP clean parse FIRES on full set (subjecthood {full_subj:.3f} > recency)",
                   full_subj > g["full_set"]["recency"]))
    checks.append((f"GAP residual NOT recovered by clean-parse structure (combined {comb:.3f} < chance 0.5) -> SEMANTIC wall",
                   comb < 0.5 and g["verdict"] == "SEMANTIC_WALL_NOT_PARSE_WALL"))

    # 4c: the WORLD-KNOWLEDGE ceiling -- WordNet selectional + CSKG commonsense are both dead on the residual
    from experiments.exp_coref_residual_world_knowledge_ceiling_v1 import run as wk_run
    wk = wk_run()
    sel = wk["wordnet_selectional_oracle"]["acc"]
    kb = wk["cskg_commonsense_oracle"]["acc"]
    kb_cov = wk["cskg_commonsense_oracle"]["coverage_frac"]
    checks.append((f"WordNet selectional oracle dead on residual ({sel:.3f} << chance)", sel < 0.1))
    checks.append((f"CSKG commonsense oracle dead ({kb:.3f}) DESPITE {kb_cov:.2f} coverage -> KB connects, not discriminates",
                   kb < 0.1 and kb_cov > 0.5 and wk["verdict"] == "WORLD_KNOWLEDGE_DEAD_ON_RESIDUAL"))

    # 5: the MEASURED POSITIVE optimization -- pool cleanup lifts CI-separated, info-free twin loses
    from experiments.exp_coref_pool_cleanup_v1 import run as pc_run
    p = pc_run(n_boot=800)
    checks.append((f"pool cleanup lifts full accuracy CI-separated ({p['drop_artifacts_minus_base']['delta']:+.3f}) and twin loses",
                   p["drop_artifacts_minus_base"]["band"] == "ABOVE"
                   and p["drop_artifacts_minus_random_twin"]["band"] == "ABOVE"))

    print()
    npass = 0
    for name, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        npass += int(ok)
    print(f"\n{npass}/{len(checks)} checks PASS")
    if npass != len(checks):
        sys.exit(1)


if __name__ == "__main__":
    main()
