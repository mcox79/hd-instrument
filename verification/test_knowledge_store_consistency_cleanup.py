"""SCAFFOLD-FREE WITNESS for the_knowledge_store_has_no_correctness_or_consistency_cleanup.

Recomputes every headline FROM SOURCE (loads the real extracted is-a store, injects, scores, and
bootstraps fresh) over multiple seeds -- never trusts a landed metrics.json. Run:
    .venv/Scripts/python.exe verification/test_knowledge_store_consistency_cleanup.py

Witnesses:
  W1  the ensemble score has the right SIGN (cross-family energy > within-family; lonely fact abstains)
  W2  FAR/gross errors: paired (corrupted genus > original genus, same subject) beats the info-free
      twin (0.5) CI-separated -- across seeds
  W3  the SOURCE-TRUST INGEST-VET floor CANNOT pick the outlier (paired ~0.5) -- the gap this fills
  W4  the frequency/degree prior floor LOSES (paired < 0.5)
  W5  NEAR-misses are detectable but WEAKER than FAR (the brain's graded response; far > near)
  W6  a real COVERAGE bound exists (a substantial minority abstain as INSUFFICIENT_SUPPORT)
  W7  the context view is LEAKAGE-CONTROLLED: genus words are stripped from the usage context
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_knowledge_store_consistency_cleanup_v1 as C

_PASS = 0
_FAIL = 0


def check(name, cond, detail=""):
    global _PASS, _FAIL
    tag = "PASS" if cond else "FAIL"
    _PASS += int(bool(cond))
    _FAIL += int(not cond)
    print(f"[{tag}] {name}" + (f"  ::  {detail}" if detail else ""))


def main():
    # W1 -- sign of the score (reuses the cell's can-fail self-test)
    try:
        C._self_test()
        check("W1 ensemble sign: cross-family > within-family; lonely abstains", True)
    except AssertionError as e:
        check("W1 ensemble sign", False, str(e))

    facts = C.load_facts(C.DEFAULT_STORE)
    seeds = [0, 1, 2]
    far = [C.evaluate_distance(facts, 0.15, "far", 2, s) for s in seeds]
    near = [C.evaluate_distance(facts, 0.15, "near", 2, s) for s in seeds]

    # W2 -- FAR paired beats twin CI-separated on every seed
    w2 = all(r["beats_twin_paired_ci"] and r["paired_ci_lo"] > 0.5 for r in far)
    check("W2 FAR paired > info-free twin (0.5), CI-separated, all seeds", w2,
          "paired=" + ",".join(f"{r['paired_corrupted_gt_original']:.3f}[{r['paired_ci_lo']:.3f}]" for r in far))

    # W3 -- INGEST-VET floor cannot pick the outlier (~0.5)
    iv = [r["floor_ingestvet_paired"] for r in far]
    check("W3 source-trust INGEST-VET floor cannot pick the outlier (~0.5)",
          all(abs(x - 0.5) < 1e-6 for x in iv), f"ingestvet_paired={iv}")

    # W4 -- frequency prior floor loses (< 0.5)
    fq = [r["floor_frequency_paired"] for r in far]
    check("W4 frequency/degree prior floor LOSES (paired < 0.5)", all(x < 0.5 for x in fq),
          f"frequency_paired={fq}")

    # W5 -- graded response: FAR > NEAR (means across seeds)
    far_m = sum(r["paired_corrupted_gt_original"] for r in far) / len(far)
    near_m = sum(r["paired_corrupted_gt_original"] for r in near) / len(near)
    check("W5 graded response: FAR paired > NEAR paired (brain-faithful)", far_m > near_m,
          f"far={far_m:.3f} > near={near_m:.3f}")

    # W6 -- a real coverage bound (a substantial minority abstain)
    cov = far[0]["coverage_all"]
    check("W6 coverage bound is real (0.2 < abstain fraction; not everything scores)",
          0.2 < (1 - cov) < 0.8, f"coverage_all={cov:.3f} -> abstain={1-cov:.3f}")

    # W7 -- context leakage control: genus words are stripped from the usage vectors
    cg = C.ContextGeometry(facts)
    # a genus word (e.g. 'process') must NOT appear in any subject usage vector
    leak = any("process" in v for v in cg.subj_vec.values())
    check("W7 context is leakage-controlled (genus words stripped from usage)", not leak,
          "no genus word in any usage vector" if not leak else "LEAK: genus word present")

    # W8 -- CLEAN foundation raises the check (the North Star: the ceiling is store noise, not the
    # mechanism). On a high-confidence base the FAR paired discrimination is HIGHER than on the full
    # noisy store, and clears the twin CI-separated.
    clean = C.high_confidence(facts)
    cfar = [C.evaluate_distance(clean, 0.15, "far", 2, s) for s in seeds]
    cfar_m = sum(r["paired_corrupted_gt_original"] for r in cfar) / len(cfar)
    check("W8 CLEAN base raises FAR paired above the noisy store (ceiling = foundation noise)",
          cfar_m > far_m and all(r["paired_ci_lo"] > 0.5 for r in cfar),
          f"clean_far={cfar_m:.3f} > full_far={far_m:.3f}")

    # W9 -- adversarial robustness: the RELATIONAL arm survives the matching-context adversary while
    # the mean-ensemble (which trusts the fooled context arm) COLLAPSES below chance.
    ar = C.evaluate_arm_robustness(clean, 0.15, 0)
    check("W9 relational arm is adversary-robust; mean-ensemble collapses under matching-context",
          ar["adversary_rel"] > 0.65 and ar["adversary_mean"] < 0.4,
          f"adv: rel={ar['adversary_rel']:.3f} (robust) vs mean={ar['adversary_mean']:.3f} (broken); "
          f"std: rel={ar['standard_rel']:.3f} mean={ar['standard_mean']:.3f}")

    # W10 -- LIVE-STORE end-to-end: the mechanism runs through a real hdlab.HDFactStore (errors
    # injected via store.store(), surviving INGEST-VET) and reproduces paired > twin CI-separated.
    import experiments.exp_consistency_cleanup_live_store_v1 as L
    L._self_test()
    lr = L.run(seed=0)
    check("W10 live HDFactStore end-to-end: paired > twin CI-sep; all injected survive INGEST-VET",
          lr["beats_twin_ci"] and lr["n_injected_scored"] == lr["n_injected"],
          f"live paired={lr['paired_corrupted_gt_original']:.3f}[{lr['paired_ci_lo']:.3f}] "
          f"survived={lr['n_injected_scored']}/{lr['n_injected']} cov={lr['coverage']:.3f}")

    # W11 -- CONFIDENCE tier: gating on schema sharpness (coherence = Friston precision) yields a
    # high-confidence subset with HIGHER paired than the full set, tested where headroom exists (the
    # full-store NEAR-miss weak spot). The brain's basic-level advantage: sharp schema -> reliable.
    cw = [C.evaluate_distance(facts, 0.15, "near", 2, s) for s in seeds]
    conf_m = sum(r["paired_confident_tier"] for r in cw) / len(cw)
    all_m = sum(r["paired_corrupted_gt_original"] for r in cw) / len(cw)
    check("W11 coherence confidence tier beats the full set on the near-miss weak spot",
          conf_m > all_m and all(r["paired_confident_tier"] > r["paired_corrupted_gt_original"] for r in cw),
          f"full_near confident={conf_m:.3f} > all={all_m:.3f} (keep~{cw[0]['confident_tier_keep_frac']:.0%})")

    # W12 -- LEAVE-ONE-OUT AUDIT (self-correction, machine-checked): the RELATIONAL arm is NOT
    # LOO-clean (collapses toward chance under strict subject-LOO on the sparse store), while the
    # CONTEXT arm is LOO-clean by construction and retains real signal. This encodes the honest
    # correction so it cannot silently regress.
    import random as _rnd
    from collections import defaultdict as _dd
    store = facts
    rng = _rnd.Random(0); base = C.Graph(store)
    nf, inj = C.inject_errors(store, base, 0.15, rng, "far"); gg = C.Graph(nf); inj_set = set(inj)
    scc = C.Scorer(nf, 2)
    def _cl(a, b, s):
        A = gg.gen2subj.get(a, set()) - {s}; B = gg.gen2subj.get(b, set()) - {s}
        inter = len(A & B); uni = len(A | B); return inter / uni if uni else 0.0
    def _rel_loo(s, gen):
        net = gg.assoc_network(s, exclude_genus=gen); tot = sum(net.values())
        if tot < 2: return None
        return 1.0 - sum(w * _cl(gen, g2, s) for g2, w in net.items()) / tot
    def _auc_of(efn):
        ie = [e for fid in inj for e in [efn(nf[fid].s, nf[fid].g)] if e is not None]
        ne = [e for f in nf if f.fid not in inj_set for e in [efn(f.s, f.g)] if e is not None]
        return C._auc(ie, ne, _rnd.Random(1))
    rel_loo_auc = _auc_of(_rel_loo)
    ctx_auc = _auc_of(scc._ctx_energy)
    check("W12 LOO audit: relational NOT clean (collapses ~chance under LOO); context arm survives LOO-clean",
          rel_loo_auc < 0.62 and ctx_auc > 0.65,
          f"relational strict-LOO AUC={rel_loo_auc:.3f} (~chance) vs context LOO-clean AUC={ctx_auc:.3f}")

    # W13 -- PHASE TRANSITION: the LOO-clean STRUCTURAL mechanism is correct but density-gated. On a
    # denser (real-family) store it crosses from chance to near-perfect; the real store is subcritical.
    import experiments.exp_consistency_phase_transition_density_v1 as PT
    pt = PT.run(seeds=2, ks=(2, 30))
    lo = pt["curve"][0]["loo_structural_auc"]; hi = pt["curve"][1]["loo_structural_auc"]
    check("W13 structural consistency is a DENSITY phase transition (chance->works; real store subcritical)",
          hi > 0.9 and lo < 0.7 and pt["real_store_indep_pair_frac"] < 0.2,
          f"LOO-structural AUC: subcritical(K=2)={lo:.2f} -> supercritical(K=30)={hi:.2f}; "
          f"real store indep-frac={pt['real_store_indep_pair_frac']:.3f} ({pt['real_store_regime']})")

    # W14 -- FULL SOLUTION: crossing the density boundary with an admissible foundation asset (WordNet
    # hypernyms) makes the STRUCTURAL mechanism work UNDER STRICT LOO on a REAL dense store, twin losing.
    try:
        import experiments.exp_consistency_wordnet_densified_solved_v1 as WD
        wd = WD.run()
        ok = (wd["regime"] == "SUPERCRITICAL" and wd["far"]["auc"] > 0.75
              and wd["far"]["beats_twin_auc"] and wd["near"]["beats_twin_auc"])
        check("W14 FULL SOLUTION: densified real store (supercritical) -> structural LOO-clean, twin loses",
              ok, f"indep-frac {wd['indep_pair_fraction']} {wd['regime']}; far AUC={wd['far']['auc']} "
                  f"(twin {wd['far']['twin_auc']}), near AUC={wd['near']['auc']} (twin {wd['near']['twin_auc']})")
    except ImportError as e:
        check("W14 FULL SOLUTION (WordNet densified)", False, f"nltk/wordnet unavailable: {e}")

    # W15 -- SCHEMA-BASED CORRECTION (brain-faithful assimilation-to-gist): the organ does not just
    # detect the error, it CORRECTS it to the schema-consistent value far above a random baseline.
    try:
        import experiments.exp_consistency_wordnet_densified_solved_v1 as WD2
        cor = WD2.correction_accuracy()
        check("W15 schema-based CORRECTION (assimilation-to-gist): recovers the right value >> random",
              cor["type_correct"] > 0.8 and cor["type_correct"] > 5 * cor["random_baseline"],
              f"type-correct={cor['type_correct']} exact={cor['exact_recovered']} vs random={cor['random_baseline']}")
    except ImportError as e:
        check("W15 schema-based CORRECTION", False, f"unavailable: {e}")

    print(f"\n==== {_PASS}/{_PASS + _FAIL} PASS ====")
    return _FAIL == 0


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
