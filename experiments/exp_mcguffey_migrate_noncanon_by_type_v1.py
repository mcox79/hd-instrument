"""exp_mcguffey_migrate_noncanon_by_type_v1 -- DOES THE PASSIVE-CUE FIX GENERALISE ACROSS NON-CANONICAL
CONSTRUCTIONS, OR ONLY PASSIVES? (deepening of the migration problem.)

The modern non-canonical population (59 q) is passive 30 / inversion 23 / fronting 6. The passive-aware
content-verb fix (exp_mcguffey_migrate_passive_cue_fix_v1) targets be+VBN morphology. This measures the
BROKEN organ vs the FIXED organ per construction TYPE, so the honest bound is explicit: which
constructions the fix recovers, and which remain a fidelity gap to name as the next problem.

Brain frame: passive is a MORPHOLOGICAL cue (Competition Model: passive morphology overrides word order).
Inversion (postverbal subject) and object-fronting are ORDER/PROSODY cues resolved by animacy + verb-class
prominence (eADM proto-role) + information structure -- a DIFFERENT cue family. So a passive-only fix is
predicted to leave inversion/fronting broken; confirming that names the next cue to build.

Writes only to data/exp_mcguffey_migrate_noncanon_by_type_v1/. Does NOT modify hdlab/.
"""
from __future__ import annotations
import argparse, json, os, sys
from collections import defaultdict, Counter
from datetime import datetime, timezone

os.environ.setdefault("OMP_NUM_THREADS", "1")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments.exp_wire_organs_endtoend_v1 import boot_ci, IN_SCOPE_ROLES, _seed_int   # noqa: E402
from experiments.exp_mcguffey_migrate_passive_cue_fix_v1 import committed, final_role_map   # noqa: E402

MODERN_GOLD = os.path.join(REPO, "data/eval_gold_mention_role_modern_ud_ewt_v1",
                           "gold_situation_modern_ud_ewt_v1.jsonl")
OUTDIR = os.path.join(REPO, "data/exp_mcguffey_migrate_noncanon_by_type_v1")
# KB_REFERENT: data/eval_gold_mention_role_modern_ud_ewt_v1/gold_situation_modern_ud_ewt_v1.jsonl


def score_type(passages, arm, seed, want_type):
    gm = Counter(q["gold_role"] for p in passages for q in p["target_queries"]
                 if q["gold_role"] in IN_SCOPE_ROLES).most_common(1)[0][0]
    vals = []
    for p in passages:
        binds = committed(p, arm, False, seed)
        by_ec, by_ent = {}, defaultdict(list)
        for b in binds:
            by_ec.setdefault((b["entity"], b["clause"]), b["role"])
            by_ent[b["entity"]].append(b)
        fr = final_role_map(p)
        for q in p["target_queries"]:
            if q["gold_role"] not in IN_SCOPE_ROLES:
                continue
            if q.get("noncanon_type", "canonical") != want_type:
                continue
            e, c, g = q["entity"], q["query_clause"], q["gold_role"]
            pr = by_ec.get((e, c)) or (max(by_ent[e], key=lambda x: x["clause"])["role"] if by_ent[e] else gm)
            vals.append(int(pr == g))
    if not vals:
        return {"acc": 0.0, "ci": [0.0, 0.0], "n": 0}
    m, lo, hi, _ = boot_ci(vals, seed=_seed_int(arm + want_type, seed))
    return {"acc": round(m, 4), "ci": [round(lo, 4), round(hi, 4)], "n": len(vals)}


def type_gold_composition(passages, want_type):
    """Each non-canonical type is ROLE-HOMOGENEOUS by construction (inversion=postverbal AGENT subject;
    fronting=preverbal PATIENT object; passive=PATIENT subject) -- so a subtype-conditioned floor is
    trivially ~1.0 and uninformative. The informative quantity is the BROKEN->FIXED delta (does the fix
    generalise?). We report the gold-role composition to make the homogeneity explicit."""
    roles = Counter(q["gold_role"] for p in passages for q in p["target_queries"]
                    if q["gold_role"] in IN_SCOPE_ROLES and q.get("noncanon_type", "canonical") == want_type)
    return dict(roles)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--seed", type=int, default=20260830)
    args = ap.parse_args()
    passages = [json.loads(l) for l in open(MODERN_GOLD, encoding="utf-8") if l.strip()]
    if args.self_test:
        passages = passages[:60]

    types = ("passive", "inversion", "fronting")
    res = {}
    for ty in types:
        res[ty] = {
            "gold_roles": type_gold_composition(passages, ty),
            "BROKEN": score_type(passages, "BROKEN", args.seed, ty),
            "FIXED": score_type(passages, "FIXED", args.seed, ty),
        }

    def improved(ty):
        return res[ty]["FIXED"]["acc"] - res[ty]["BROKEN"]["acc"]

    verdict = {
        "passive_recovered": improved("passive") > 0.1,
        "inversion_recovered": improved("inversion") > 0.1,
        "fronting_recovered": improved("fronting") > 0.1,
        "fix_is_passive_specific": improved("passive") > 0.1 and improved("inversion") <= 0.1,
        "deltas": {ty: round(improved(ty), 4) for ty in types},
        "residual_noncanonical_gap": [ty for ty in types if improved(ty) <= 0.1],
        "residual_gap_reason": "inversion (postverbal subject) + fronting (preverbal object) are ORDER/"
                               "PROMINENCE-cued, not morphology-cued -- they need the eADM animacy + "
                               "verb-class proto-role cue + information structure, a different cue family "
                               "than the passive morphology the fix supplies. Named as the next target.",
    }
    metrics = {"ts_iso": datetime.now(timezone.utc).isoformat(), "seed": args.seed,
               "by_type": res, "verdict": verdict}

    if args.self_test:
        assert res["passive"]["BROKEN"]["n"] > 0
        print("self-test PASS", json.dumps(verdict["deltas"]))
        return

    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print("=" * 80)
    print("NON-CANONICAL FIX GENERALISATION BY CONSTRUCTION TYPE (modern UD-EWT)")
    print("=" * 80)
    for ty in types:
        r = res[ty]
        print(f"  {ty:10s} n={r['BROKEN']['n']:3d} gold={r['gold_roles']} | "
              f"BROKEN {r['BROKEN']['acc']:.3f} {r['BROKEN']['ci']}"
              f"  FIXED {r['FIXED']['acc']:.3f} {r['FIXED']['ci']}  (delta {improved(ty):+.3f})")
    print("\nVERDICT:", json.dumps(verdict, indent=2))
    print(f"\nwrote {os.path.relpath(os.path.join(OUTDIR,'metrics.json'), REPO)}")


if __name__ == "__main__":
    main()
