"""exp_mcguffey_migrate_revalidate_v1 -- REVALIDATE THE READER'S ROLE / SITUATION-MODEL ORGAN ON A
MODERN POPULATION AND QUANTIFY THE McGUFFEY-vs-MODERN CORPUS-AGE DELTA.

Problem: the_reader_eval_is_scored_on_200_year_old_mcguffey_migrate_to_modern_text (p1).

Runs the IDENTICAL reader pipeline (the exp_wire_organs_endtoend_v1 front-end + resolver + role scorer,
imported unchanged) on TWO populations under ONE scorer:
  McGUFFEY  = the 57 hand-authored 1830s passages (data/eval_gold_mention_role_mcguffey_v1, 178 q).
  MODERN    = the UD-EWT gold-parse-derived situation-model gold (this problem's Cell 1, 266 p / 572 q).

ARMS (same for both populations):
  FLOOR_MAJORITY : predict the population's majority in-scope role for every query (recomputed per
                   subset -- the strongest trivial floor).
  POSITION       : the naive POS subject/object front-end (Bever NVN-ish: first nominal before the verb
                   = agent). This is the shallow heuristic McGuffey's canonical SVO cannot punish.
  VARGS          : the brain-faithful verb-argument-structure assigner (Competition Model cue-validity:
                   speech-verb + quotative inversion + animacy prominence).
  VARGS_TWIN     : info-free control -- VARGS with the verb-class cue SCRAMBLED (coin-flip). MUST LOSE.

SUBSETS (each floor + CI recomputed on its OWN sub-population, per the measurement bar):
  ALL_INSCOPE    : agent/patient gold queries.
  ROLE_VARYING   : queries whose gold role != the entity's FINAL-clause role (floor cannot coast on
                   "most-recent role"; the genuine situation-model-tracking population).
  CANONICAL / NONCANONICAL (modern only): the brain-fidelity discriminator -- does the role organ hold
                   where a shallow first-noun heuristic must fail (passive / inversion / fronting)?

DELTA = same organ, McGuffey population vs modern population, each vs its own floor. A drop on modern is
the corpus-age confound made numeric; a hold says the organ generalises (brain-faithful, not a McGuffey
artefact). Info-free twin LOSING on modern says the signal is real on modern text.

Writes only to data/exp_mcguffey_migrate_revalidate_v1/. Does NOT modify hdlab/.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

import numpy as np

os.environ.setdefault("OMP_NUM_THREADS", "1")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

# Import the reader pipeline UNCHANGED (this IS the organ under test).
from experiments.exp_wire_organs_endtoend_v1 import (   # noqa: E402
    live_extract_raw, resolve_raw, boot_ci, IN_SCOPE_ROLES, _seed_int, load_gold, repo_path,
)

MODERN_GOLD = os.path.join(REPO, "data/eval_gold_mention_role_modern_ud_ewt_v1",
                           "gold_situation_modern_ud_ewt_v1.jsonl")
OUTDIR = os.path.join(REPO, "data/exp_mcguffey_migrate_revalidate_v1")

# KB_REFERENT: data/eval_gold_mention_role_mcguffey_v1/gold_multiclause_entity_track_v3.jsonl
# KB_REFERENT: data/eval_gold_mention_role_mcguffey_v1/gold_multientity_dense_v1.jsonl
# KB_REFERENT: data/eval_gold_mention_role_modern_ud_ewt_v1/gold_situation_modern_ud_ewt_v1.jsonl


def load_modern():
    return [json.loads(l) for l in open(MODERN_GOLD, encoding="utf-8") if l.strip()]


def final_role_map(passage):
    """entity -> its role at its LAST-seen clause (the 'most-recent role' the floor could coast on)."""
    out = {}
    for name, chain in passage["entities"].items():
        m = max(chain, key=lambda x: x["clause"])
        out[name] = m["role"]
    return out


def canonical_map(passage):
    """(entity, query_clause) -> canonical? If the gold carries a per-query 'canonical' flag (modern),
    use it; else (McGuffey) default True (canonical SVO schoolbook prose)."""
    out = {}
    for q in passage.get("target_queries", []):
        out[(q["entity"], q["query_clause"])] = q.get("canonical", True)
    return out


def committed_by_pid(passages, mode, twin, seed):
    out = {}
    for p in passages:
        raw = live_extract_raw(p, mode=mode, twin=twin, seed=seed)
        out[p["passage_id"]] = resolve_raw(raw, p, policy="recency", seed=seed)
    return out


def population_majority(passages):
    inv = [q["gold_role"] for p in passages for q in p.get("target_queries", []) if q["gold_role"] in IN_SCOPE_ROLES]
    return Counter(inv).most_common(1)[0][0] if inv else "agent"


def score_arm(passages, binds_by_pid, gm, qfilter, seed, floor_label=None):
    """Mirror of exp_wire_organs_endtoend_v1.score_endtoend, with an arbitrary per-query filter and an
    optional FLOOR mode (predict gm for every query). Returns mean/CI/n over the filtered in-scope pop."""
    vals = []
    for p in passages:
        pid = p["passage_id"]
        fr = final_role_map(p)
        cm = canonical_map(p)
        by_ec, by_ent = {}, defaultdict(list)
        for b in binds_by_pid[pid]:
            by_ec.setdefault((b["entity"], b["clause"]), b["role"])
            by_ent[b["entity"]].append(b)
        for q in p.get("target_queries", []):
            ent, qc, gold = q["entity"], q["query_clause"], q["gold_role"]
            if gold not in IN_SCOPE_ROLES:
                continue
            ctx = {"rolevar": (gold != fr.get(ent)), "canonical": cm.get((ent, qc), True)}
            if not qfilter(ctx):
                continue
            if floor_label is not None:
                pr = floor_label
            elif (ent, qc) in by_ec:
                pr = by_ec[(ent, qc)]
            elif by_ent[ent]:
                pr = max(by_ent[ent], key=lambda x: x["clause"])["role"]
            else:
                pr = gm
            vals.append(int(pr == gold))
    if not vals:
        return {"acc": 0.0, "ci": [0.0, 0.0], "hw": 0.0, "n": 0}
    m, lo, hi, hw = boot_ci(vals, seed=seed)
    return {"acc": round(m, 4), "ci": [round(lo, 4), round(hi, 4)], "hw": round(hw, 4), "n": len(vals)}


FILTERS = {
    "ALL_INSCOPE": lambda c: True,
    "ROLE_VARYING": lambda c: c["rolevar"],
    "CANONICAL": lambda c: c["canonical"],
    "NONCANONICAL": lambda c: not c["canonical"],
}


def run_population(name, passages, seed):
    gm = population_majority(passages)
    res = {"population": name, "n_passages": len(passages), "majority_role": gm, "subsets": {}}
    # precompute committed bindings per arm once
    binds = {
        "POSITION": committed_by_pid(passages, mode="position", twin=False, seed=seed),
        "VARGS": committed_by_pid(passages, mode="vargs", twin=False, seed=seed),
        "VARGS_TWIN": committed_by_pid(passages, mode="vargs", twin=True, seed=seed),
    }
    for sub, qf in FILTERS.items():
        row = {}
        row["FLOOR_MAJORITY"] = score_arm(passages, binds["POSITION"], gm, qf, _seed_int("FL" + sub, seed),
                                          floor_label=gm)
        for arm in ("POSITION", "VARGS", "VARGS_TWIN"):
            row[arm] = score_arm(passages, binds[arm], gm, qf, _seed_int(arm + sub, seed))
        res["subsets"][sub] = row
    return res


def sep(a, b):
    """Does arm a beat arm/floor b, CI-separated (a.lo > b.hi)?"""
    return a["ci"][0] > b["ci"][1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--seed", type=int, default=20260830)
    args = ap.parse_args()

    mcg = load_gold()
    modern = load_modern()
    if args.self_test:
        mcg = mcg[:12]
        modern = modern[:20]

    R_mcg = run_population("MCGUFFEY_1830s", mcg, args.seed)
    R_mod = run_population("MODERN_UD_EWT", modern, args.seed)

    # headline: best real arm (VARGS) vs floor, per population, on ALL_INSCOPE + ROLE_VARYING
    def headline(R):
        out = {}
        for sub in ("ALL_INSCOPE", "ROLE_VARYING"):
            row = R["subsets"][sub]
            out[sub] = {
                "vargs": row["VARGS"]["acc"], "position": row["POSITION"]["acc"],
                "floor": row["FLOOR_MAJORITY"]["acc"], "twin": row["VARGS_TWIN"]["acc"],
                "vargs_beats_floor_ci_sep": sep(row["VARGS"], row["FLOOR_MAJORITY"]),
                "vargs_beats_twin_ci_sep": sep(row["VARGS"], row["VARGS_TWIN"]),
            }
        return out

    H_mcg, H_mod = headline(R_mcg), headline(R_mod)
    delta = {}
    for sub in ("ALL_INSCOPE", "ROLE_VARYING"):
        delta[sub] = {
            "vargs_modern_minus_mcguffey": round(H_mod[sub]["vargs"] - H_mcg[sub]["vargs"], 4),
            "vargs_over_floor_mcguffey": round(H_mcg[sub]["vargs"] - H_mcg[sub]["floor"], 4),
            "vargs_over_floor_modern": round(H_mod[sub]["vargs"] - H_mod[sub]["floor"], 4),
        }
    # brain-fidelity discriminator (modern only): canonical vs non-canonical
    fid = {
        "vargs_canonical": R_mod["subsets"]["CANONICAL"]["VARGS"]["acc"],
        "vargs_noncanonical": R_mod["subsets"]["NONCANONICAL"]["VARGS"]["acc"],
        "position_canonical": R_mod["subsets"]["CANONICAL"]["POSITION"]["acc"],
        "position_noncanonical": R_mod["subsets"]["NONCANONICAL"]["POSITION"]["acc"],
        "floor_canonical": R_mod["subsets"]["CANONICAL"]["FLOOR_MAJORITY"]["acc"],
        "floor_noncanonical": R_mod["subsets"]["NONCANONICAL"]["FLOOR_MAJORITY"]["acc"],
        "n_noncanonical": R_mod["subsets"]["NONCANONICAL"]["VARGS"]["n"],
    }

    metrics = {
        "ts_iso": datetime.now(timezone.utc).isoformat(), "seed": args.seed,
        "populations": {"MCGUFFEY_1830s": R_mcg, "MODERN_UD_EWT": R_mod},
        "headline": {"MCGUFFEY_1830s": H_mcg, "MODERN_UD_EWT": H_mod},
        "corpus_age_delta": delta,
        "brain_fidelity_noncanonical_discriminator": fid,
    }

    if args.self_test:
        assert R_mcg["subsets"]["ALL_INSCOPE"]["VARGS"]["n"] > 0
        assert R_mod["subsets"]["ALL_INSCOPE"]["VARGS"]["n"] > 0
        print("self-test PASS",
              json.dumps({"mcg_vargs": H_mcg["ALL_INSCOPE"]["vargs"],
                          "mod_vargs": H_mod["ALL_INSCOPE"]["vargs"],
                          "delta": delta["ALL_INSCOPE"]}))
        return

    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print("=" * 90)
    print("CORPUS-AGE REVALIDATION: reader role/situation-model organ, McGuffey 1830s vs modern UD-EWT")
    print("=" * 90)
    for name, R in (("MCGUFFEY_1830s", R_mcg), ("MODERN_UD_EWT", R_mod)):
        print(f"\n[{name}]  passages={R['n_passages']}  majority_role={R['majority_role']}")
        for sub in ("ALL_INSCOPE", "ROLE_VARYING", "CANONICAL", "NONCANONICAL"):
            row = R["subsets"][sub]
            print(f"  {sub:14s} n={row['VARGS']['n']:4d} | floor {row['FLOOR_MAJORITY']['acc']:.3f}"
                  f"  position {row['POSITION']['acc']:.3f}"
                  f"  VARGS {row['VARGS']['acc']:.3f} (+/-{row['VARGS']['hw']:.3f})"
                  f"  twin {row['VARGS_TWIN']['acc']:.3f}")
    print("\nCORPUS-AGE DELTA (VARGS):")
    for sub, d in delta.items():
        print(f"  {sub:14s} modern-mcguffey={d['vargs_modern_minus_mcguffey']:+.4f}"
              f"  | over-floor mcg={d['vargs_over_floor_mcguffey']:+.4f} modern={d['vargs_over_floor_modern']:+.4f}")
    print("\nBRAIN-FIDELITY (modern, canonical vs non-canonical):")
    print(f"  VARGS   canonical {fid['vargs_canonical']:.3f}  non-canonical {fid['vargs_noncanonical']:.3f}"
          f"  (n_noncanon={fid['n_noncanonical']})")
    print(f"  POSITION canonical {fid['position_canonical']:.3f}  non-canonical {fid['position_noncanonical']:.3f}")
    print(f"\nwrote {os.path.relpath(os.path.join(OUTDIR,'metrics.json'), REPO)}")


if __name__ == "__main__":
    main()
