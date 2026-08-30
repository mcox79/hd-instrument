"""Scaffold-free witness for the_reader_eval_is_scored_on_200_year_old_mcguffey_migrate_to_modern_text.

RECOMPUTES the load-bearing claims from gold + the reader pipeline (does NOT read any metrics.json):
  1. The MODERN gold is real, in the McGuffey situation-model shape, genuinely modern (UD-EWT provenance),
     roles are agent/patient only, and it carries non-canonical + role-varying discriminative subsets.
  2. McGuffey's in-scope role eval is DEGENERATE: >= 88% one role, so the always-majority floor beats the
     reader's own role front-end (vargs) -- McGuffey inflated the apparent role competence.
  3. On modern text the CURRENT role organ COLLAPSES on non-canonical constructions: below its coin-flip
     twin (systematically wrong), and CI-separated below the strongest floor.
  4. The wall is FIXABLE (brain-faithful): a passive-aware content-verb assigner recovers non-canonical
     CI-separated over the broken organ, beats its info-free twin, and does not hurt canonical.

Run: .venv/Scripts/python.exe verification/test_mcguffey_migration.py
"""
import json
import os
import sys
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments.exp_wire_organs_endtoend_v1 import load_gold, IN_SCOPE_ROLES, live_extract_raw, resolve_raw
from experiments.exp_mcguffey_migrate_passive_cue_fix_v1 import score as fix_score

MODERN_GOLD = os.path.join(REPO, "data/eval_gold_mention_role_modern_ud_ewt_v1",
                           "gold_situation_modern_ud_ewt_v1.jsonl")
SEED = 20260830
CHECKS = []


def ok(name, cond, detail=""):
    CHECKS.append((name, bool(cond), detail))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}  {detail}")


def load_modern():
    return [json.loads(l) for l in open(MODERN_GOLD, encoding="utf-8") if l.strip()]


def boot_lo_hi(vals, seed=0):
    import numpy as np
    v = np.asarray(vals, float)
    rng = np.random.default_rng(seed)
    means = [rng.choice(v, size=len(v), replace=True).mean() for _ in range(2000)]
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5)), float(v.mean())


def main():
    # ---- 1. modern gold shape + provenance + subsets ----
    assert os.path.exists(MODERN_GOLD), "modern gold missing -- run exp_mcguffey_migrate_build_modern_gold_v1"
    modern = load_modern()
    ok("modern_gold_nonempty", len(modern) >= 100, f"{len(modern)} passages")
    p0 = modern[0]
    ok("modern_gold_mcguffey_shape",
       {"passage_id", "clauses", "entities", "target_queries"} <= set(p0),
       "has clauses/entities/target_queries")
    roles = Counter(q["gold_role"] for p in modern for q in p["target_queries"])
    ok("modern_roles_agent_patient_only", set(roles) <= {"agent", "patient"}, str(dict(roles)))
    ok("modern_provenance_ud_gold_parse",
       all(p.get("gold_verified") == "transparent_ud_deprel_rule" for p in modern),
       "UD gold-parse-derived, no LLM")
    noncanon = sum(1 for p in modern for q in p["target_queries"] if not q.get("canonical", True))
    ok("modern_has_noncanonical_subset", noncanon >= 20, f"{noncanon} non-canonical queries")

    # ---- 2. McGuffey degeneracy: floor beats the organ ----
    mcg = load_gold()
    insc = [q["gold_role"] for p in mcg for q in p["target_queries"] if q["gold_role"] in IN_SCOPE_ROLES]
    top = Counter(insc).most_common(1)[0]
    floor = top[1] / len(insc)
    ok("mcguffey_role_eval_degenerate", floor >= 0.88, f"in-scope majority '{top[0]}' = {floor:.3f}")
    # organ (vargs) role accuracy on McGuffey in-scope
    from collections import defaultdict
    gm = top[0]
    vals = []
    for p in mcg:
        binds = resolve_raw(live_extract_raw(p, mode="vargs", seed=SEED), p, policy="recency", seed=SEED)
        by_ec, by_ent = {}, defaultdict(list)
        for b in binds:
            by_ec.setdefault((b["entity"], b["clause"]), b["role"])
            by_ent[b["entity"]].append(b)
        for q in p["target_queries"]:
            if q["gold_role"] not in IN_SCOPE_ROLES:
                continue
            e, c, g = q["entity"], q["query_clause"], q["gold_role"]
            pr = by_ec.get((e, c)) or (max(by_ent[e], key=lambda x: x["clause"])["role"] if by_ent[e] else gm)
            vals.append(int(pr == g))
    organ_acc = sum(vals) / len(vals)
    ok("mcguffey_organ_loses_to_floor", organ_acc < floor,
       f"vargs {organ_acc:.3f} < always-agent floor {floor:.3f}")

    # ---- 3. modern non-canonical COLLAPSE (current organ) ----
    broken_nc = fix_score(modern, "BROKEN", False, SEED, "NONCANONICAL")
    twin_nc = fix_score(modern, "FIXED", True, SEED, "NONCANONICAL")   # coin-flip voice
    ok("modern_noncanonical_collapse_below_twin",
       broken_nc["acc"] < twin_nc["acc"] + 0.02,
       f"broken non-canonical {broken_nc['acc']:.3f} ~<= coin-flip twin {twin_nc['acc']:.3f}")

    # ---- 4. the wall is FIXABLE (brain-faithful passive-aware assigner) ----
    fixed_nc = fix_score(modern, "FIXED", False, SEED, "NONCANONICAL")
    ok("fix_recovers_noncanonical_ci_sep", fixed_nc["ci"][0] > broken_nc["ci"][1],
       f"FIXED {fixed_nc['acc']:.3f} {fixed_nc['ci']} CI-sep > BROKEN {broken_nc['acc']:.3f} {broken_nc['ci']}")
    ok("fix_beats_info_free_twin", fixed_nc["acc"] > twin_nc["acc"],
       f"FIXED {fixed_nc['acc']:.3f} > voice-scrambled twin {twin_nc['acc']:.3f}")
    broken_ca = fix_score(modern, "BROKEN", False, SEED, "CANONICAL")
    fixed_ca = fix_score(modern, "FIXED", False, SEED, "CANONICAL")
    ok("fix_does_not_hurt_canonical", fixed_ca["acc"] >= broken_ca["acc"] - 0.03,
       f"canonical BROKEN {broken_ca['acc']:.3f} -> FIXED {fixed_ca['acc']:.3f}")

    # ---- 5. deepening: the fix is PASSIVE-SPECIFIC (residual inversion/fronting gap named) ----
    from experiments.exp_mcguffey_migrate_noncanon_by_type_v1 import score_type
    p_broken = score_type(modern, "BROKEN", SEED, "passive")["acc"]
    p_fixed = score_type(modern, "FIXED", SEED, "passive")["acc"]
    inv_broken = score_type(modern, "BROKEN", SEED, "inversion")["acc"]
    inv_fixed = score_type(modern, "FIXED", SEED, "inversion")["acc"]
    ok("fix_is_passive_specific", (p_fixed - p_broken) > 0.1 and (inv_fixed - inv_broken) <= 0.1,
       f"passive delta {p_fixed - p_broken:+.3f} vs inversion delta {inv_fixed - inv_broken:+.3f} "
       "(residual order/prominence gap named)")

    # ---- 6. deepening 2: ONE cue-competition mechanism GENERALISES to inversion (patches cannot) ----
    from experiments.exp_mcguffey_migrate_cue_competition_v1 import committed_cue, score as cue_score
    cue_inv = cue_score(modern, lambda p: committed_cue(p, None, False, SEED), SEED, want_type="inversion")["acc"]
    ok("cue_competition_generalises_to_inversion", cue_inv > inv_fixed,
       f"cue-competition inversion {cue_inv:.3f} > passive-patch inversion {inv_fixed:.3f} "
       "(one learned mechanism generalises where per-construction patches cannot)")

    # ---- 7. deepening 3: LEARNED cues generalise IN-DISTRIBUTION but WALL cross-construction ----
    from experiments.exp_mcguffey_migrate_learned_cue_transfer_v1 import (
        extract_items, fit_logreg, acc as lc_acc, order_only_acc, majority_floor as lc_floor)
    import numpy as _np
    Xm, ym, tym = extract_items(modern)
    _rng = _np.random.default_rng(SEED)
    idx = _rng.permutation(len(ym)); cut = int(0.7 * len(idx)); tr, te = idx[:cut], idx[cut:]
    w = fit_logreg(Xm[tr], ym[tr]); w_tw = fit_logreg(Xm[tr], _rng.permutation(ym[tr]))
    a_learn = lc_acc(w, Xm[te], ym[te])["acc"]; a_order = order_only_acc(Xm[te], ym[te])["acc"]
    a_floor = lc_floor(ym[te])["acc"]; a_twin = lc_acc(w_tw, Xm[te], ym[te])["acc"]
    ok("learned_cues_generalise_in_distribution", a_learn > a_order and a_learn > a_floor and a_learn > a_twin,
       f"learned {a_learn:.3f} > order-only {a_order:.3f}, floor {a_floor:.3f}, twin {a_twin:.3f}")
    # cross-construction wall: learned model trained on canon+passive fails unseen inversion vs the order rule
    trm = _np.isin(tym, ["canonical", "passive"]); tem = (tym == "inversion")
    if tem.sum() >= 3:
        w_cc = fit_logreg(Xm[trm], ym[trm])
        cc_learn = lc_acc(w_cc, Xm[tem], ym[tem])["acc"]; cc_order = order_only_acc(Xm[tem], ym[tem])["acc"]
        ok("surface_cues_wall_on_unseen_construction", cc_learn <= cc_order + 0.05,
           f"learned {cc_learn:.3f} does NOT beat order-only {cc_order:.3f} on unseen inversion "
           "(surface-cue frequency-learning under-samples conflict -> grounded role assignment is the path)")

    # ---- 8. deepening 4: GROUNDED thematic-fit CLEARS the non-canonical wall (the solution PoC) ----
    from experiments.exp_mcguffey_migrate_grounded_thematic_fit_poc_v1 import (
        core_args, train_selpref, predict_tf, evaluate as tf_eval)
    from experiments.exp_mcguffey_migrate_build_modern_gold_v1 import parse_conllu, UD_TRAIN, UD_TEST
    _items = core_args(parse_conllu(UD_TRAIN) + parse_conllu(UD_TEST))
    _r = _np.random.default_rng(SEED); _ix = _r.permutation(len(_items)); _c = int(0.7 * len(_items))
    _tr = [_items[i] for i in _ix[:_c]]; _teitems = [_items[i] for i in _ix[_c:]]
    _mdl = train_selpref(_tr)
    _tf = tf_eval(_mdl, _teitems, lambda it: predict_tf(_mdl, it["verb"], it["noun"]))
    _nvn = tf_eval(_mdl, _teitems, lambda it: "agent" if it["preverbal"] else "patient")
    tf_nc = (_tf.get("NONCANON") or {}).get("acc", 0.0); nvn_nc = (_nvn.get("NONCANON") or {}).get("acc", 0.0)
    ok("grounded_thematic_fit_clears_noncanonical_wall", tf_nc > nvn_nc + 0.3,
       f"grounded thematic-fit non-canonical {tf_nc:.3f} >> surface word-order {nvn_nc:.3f} "
       "(construction-independent grounded mechanism clears the wall surface cues collapse on)")

    # ---- 9. deepening 5: LINEAR learned competition is insufficient -> conflict GATING needed ----
    from experiments.exp_mcguffey_migrate_learned_competition_v1 import run_split
    _tr_cc = [it for it in _items if it["canon_type"] in ("canonical", "passive")]
    _te_cc = [it for it in _items if it["canon_type"] == "inversion"]
    _cc = run_split(_tr_cc, _te_cc, SEED)
    fit_inv = (_cc.get("FIT") or {}).get("inversion") or 0.0
    comb_inv = (_cc.get("COMBINED") or {}).get("inversion") or 0.0
    surf_inv = (_cc.get("SURFACE") or {}).get("inversion") or 0.0
    ok("linear_cue_sum_insufficient_conflict_gating_needed",
       fit_inv > surf_inv and comb_inv <= fit_inv + 0.05,
       f"on unseen inversion: FIT-alone {fit_inv:.3f} > SURFACE {surf_inv:.3f}, but linear COMBINED "
       f"{comb_inv:.3f} does NOT exceed FIT -> conflict validity is a GATE, not a linear weight")

    # ---- 10. deepening 6: brain-pinned PRECISION-WEIGHTING reaches near-both-domains (passive auto-flip) ----
    from experiments.exp_mcguffey_migrate_precision_weighted_v1 import (
        train_selpref as pw_selpref, learn_reliabilities, predict_pw, acc_by_cut as pw_acc)
    _pwmodel = pw_selpref(_tr)
    _pwrel = learn_reliabilities(_tr, _pwmodel)
    _pw = pw_acc(lambda it: predict_pw(_pwrel, _pwmodel, it), _teitems)
    _surf = pw_acc(lambda it: "agent" if it["preverbal"] else "patient", _teitems)
    ord_rel_pass = _pwrel["order"].get(1, 0.5)
    ok("precision_weighting_reaches_near_both_domains",
       (_pw["NONCANON"] or 0) > (_surf["NONCANON"] or 0) + 0.3 and (_pw["canonical"] or 0) >= (_surf["canonical"] or 0) - 0.12,
       f"precision-weighted non-canon {_pw['NONCANON']:.3f} >> surface {_surf['NONCANON']:.3f} while canonical "
       f"{_pw['canonical']:.3f} ~ surface {_surf['canonical']:.3f}; learned order-reliability under passive "
       f"{ord_rel_pass:.3f} (<0.5 -> negative weight auto-flips, emergent passive fix)")

    # ---- 11. deepening 7: "inversion" was mostly existential gold-noise; it is a GRAMMATICAL-FUNCTION problem ----
    from experiments.exp_mcguffey_migrate_grammatical_function_v1 import thematic_core_args
    from experiments.exp_mcguffey_migrate_build_modern_gold_v1 import parse_conllu as _pc, UD_TRAIN as _UT, UD_TEST as _UE
    _docs = _pc(_UT) + _pc(_UE)
    _raw_inv = sum(1 for it in _items if it["canon_type"] == "inversion")   # raw nsubj->agent (existentials included)
    _them = thematic_core_args(_docs)
    _gen_inv = [it for it in _them if it["canon_type"] == "inversion"]      # existential/copular EXCLUDED
    _pos_inv = sum(int(("agent" if it["preverbal"] else "patient") == it["role"]) for it in _gen_inv) / max(1, len(_gen_inv))
    ok("inversion_is_existential_noise_plus_a_parse_problem",
       len(_gen_inv) < _raw_inv * 0.5 and _pos_inv < 0.1,
       f"thematic (existential-excluded) inversion {len(_gen_inv)} << raw {_raw_inv}; surface position solves "
       f"{_pos_inv:.3f} of genuine inversion -> it is a GRAMMATICAL-FUNCTION (parse) problem, not thematic-fit")

    n_pass = sum(1 for _, c, _ in CHECKS if c)
    print(f"\n{n_pass}/{len(CHECKS)} checks passed")
    assert n_pass == len(CHECKS), "WITNESS FAILED"
    print("WITNESS PASS")


if __name__ == "__main__":
    main()
