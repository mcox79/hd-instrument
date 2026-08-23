"""The source-trust vet reports 1.000/1.000/1.000 with no floor. Here is the floor.

WHY THIS ROW. The Q115 triage narrowed 4,908 landed results to one worth acting on, and
`ORGAN_MAP.md` says why, verbatim:

    `exp_hd_fact_store_source_trust_vet_v1` reports **1.000/1.000/1.000, verdict PASS, no floor.**
    **BLOCKS:** every claim that rests on "the foundation knows N things."

**AND THE TRIAGE'S OWN CONCLUSION WAS THAT RE-RUNNING IT WOULD NOT HELP.** A result with no floor
re-runs and still has no floor. The useful action is to run the floor, which is this file.

WHAT THE CELL ACTUALLY ASKS, read from `_build_scenario()`. It constructs 160 trials, sets
`gt_conflict` and the `expected` resolution **at the moment each fact is added**, and then measures
whether the HD store recovers them. Everything needed to recover them is SUPPLIED alongside:

  * **conflict** is defined as *same subject, same relation, different object* -- the detection rule
    IS the definition;
  * `trust_ladder` = `{TRUST_HIGH: 1.0, TRUST_MID: 0.6, TRUST_LOW: 0.3}` -- so REPLACE (higher trust
    arrives) vs DROP (lower trust arrives) is a comparison of two supplied numbers;
  * `relation_cardinality` = `{capital_of: FUNCTIONAL, speaks: MULTIVALUED, ...}` -- so the only
    genuinely interesting call, **FLAG vs COMBINE between two EQUAL-trust sources, is also supplied.**

**SO THE FLOOR IS A DICTIONARY AND FOUR IF-STATEMENTS.** No hypervectors, no store, no encoder --
just the same inputs the cell gets, and the rules its own docstring states. If that scores 1.000 too,
the cell's PASS is measuring the scenario's construction rather than the store.

⚠️ **WHAT THIS WOULD AND WOULD NOT MEAN.** It would NOT mean the HD store is broken or that the cell
is dishonest -- the cell calls itself a DEMONSTRATION in its first line and states its honest frame
("does NOT verify factual truth"). It would mean the number cannot support the weight ORGAN_MAP says
rests on it, because a method with none of the machinery reaches the same score.

    .venv/Scripts/python.exe verification/test_source_trust_vet_has_a_trivial_floor.py
"""
import io
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
LANDED = os.path.join(REPO, "data", "exp_hd_fact_store_source_trust_vet_v1", "metrics.json")


def trivial_vet(trials, trust_ladder, cardinality):
    """The floor: a dict of what has been seen, and the rules the cell's own docstring states.

    Deliberately has NOTHING the cell has beyond its inputs -- no HD store, no encoder, no vectors.
    It is fair in the other direction too: it gets exactly what the cell gets and nothing more.
    """
    seen = {}                        # (subject, relation) -> list of (obj, trust_name)
    pred_conflict, pred_resolution = [], []
    for t in trials:
        key = (t["subject"], t["relation"])
        prior = seen.get(key, [])
        clash = [p for p in prior if p[0] != t["obj"]]
        if not clash:
            pred_conflict.append(False)
            pred_resolution.append("CLEAN_STORE")
        else:
            pred_conflict.append(True)
            new_trust = trust_ladder[t["trust"]]
            old_trust = max(trust_ladder[p[1]] for p in clash)
            if cardinality.get(t["relation"]) == "MULTIVALUED":
                pred_resolution.append("COMBINE")
            elif new_trust > old_trust:
                pred_resolution.append("REPLACE")
            elif new_trust < old_trust:
                pred_resolution.append("DROP")
            else:
                pred_resolution.append("FLAG")
        seen.setdefault(key, []).append((t["obj"], t["trust"]))
    return pred_conflict, pred_resolution


def main():
    ok = True

    def chk(label, cond, detail=""):
        nonlocal ok
        print("[witness] %-56s %s %s" % (label, "PASS" if cond else "FAIL", detail))
        ok = ok and bool(cond)

    landed = json.load(io.open(LANDED, encoding="utf-8"))
    lm = landed["metrics"]
    print("[witness] LANDED: detection P/R %.3f/%.3f, resolution acc %.3f, on %d trials"
          % (lm["detection_precision"], lm["detection_recall"], lm["resolution_accuracy"],
             lm["n_trials"]))

    import importlib
    cell = importlib.import_module("experiments.exp_hd_fact_store_source_trust_vet_v1")
    built = cell._build_scenario()
    trials = built[-1] if isinstance(built, tuple) else built
    if isinstance(trials, dict):
        trials = trials.get("trials", trials)
    chk("rebuilt the cell's own scenario", len(trials) == lm["n_trials"],
        "(%d trials vs landed %d)" % (len(trials), lm["n_trials"]))

    trust = landed["trust_ladder"]
    card = landed["relation_cardinality"]
    pc, pr = trivial_vet(trials, trust, card)

    gt_c = [bool(t["gt_conflict"]) for t in trials]
    tp = sum(1 for a, b in zip(pc, gt_c) if a and b)
    fp = sum(1 for a, b in zip(pc, gt_c) if a and not b)
    fn = sum(1 for a, b in zip(pc, gt_c) if not a and b)
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    res_idx = [i for i, t in enumerate(trials) if t["gt_conflict"]]
    res_acc = (sum(1 for i in res_idx if pr[i] == trials[i]["expected"]) / len(res_idx)
               if res_idx else 0.0)

    print()
    print("[witness] %-26s %-10s %-10s" % ("", "LANDED", "TRIVIAL FLOOR"))
    print("[witness] %-26s %-10.3f %-10.3f" % ("detection precision",
                                               lm["detection_precision"], prec))
    print("[witness] %-26s %-10.3f %-10.3f" % ("detection recall", lm["detection_recall"], rec))
    print("[witness] %-26s %-10.3f %-10.3f" % ("resolution accuracy",
                                               lm["resolution_accuracy"], res_acc))

    matched = (abs(prec - lm["detection_precision"]) < 1e-9
               and abs(rec - lm["detection_recall"]) < 1e-9
               and abs(res_acc - lm["resolution_accuracy"]) < 1e-9)
    print()
    if matched:
        print("[witness] \U0001f53b A DICTIONARY AND FOUR IF-STATEMENTS MATCH THE LANDED RESULT EXACTLY.")
        print("  The task supplies everything needed to solve it: conflict IS same-(s,r)-different-o,")
        print("  the trust ladder decides REPLACE vs DROP, and relation_cardinality decides FLAG vs")
        print("  COMBINE. **The 1.000/1.000/1.000 measures the scenario's construction, not the")
        print("  store.** It cannot carry the weight ORGAN_MAP says rests on it.")
    else:
        print("[witness] ✅ The trivial floor does NOT reach the landed result -- the store is doing")
        print("  something the supplied rules do not. That is a real finding in the other direction.")
    chk("the floor was actually computed on the cell's own trials", len(pc) == len(trials))

    # NEGATIVE CONTROL: break the floor's access to trust and it must get WORSE, or the comparison
    # above proves only that both arms print 1.000 for unrelated reasons.
    flat = {k: 1.0 for k in trust}
    _pc2, pr2 = trivial_vet(trials, flat, card)
    res2 = (sum(1 for i in res_idx if pr2[i] == trials[i]["expected"]) / len(res_idx)
            if res_idx else 0.0)
    print()
    print("[witness] NEGATIVE CONTROL -- floor with the trust ladder FLATTENED: resolution %.3f"
          % res2)
    chk("removing trust degrades the floor (so trust is what it uses)", res2 < res_acc,
        "(%.3f -> %.3f)" % (res_acc, res2))

    print("[witness] RESULT: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
