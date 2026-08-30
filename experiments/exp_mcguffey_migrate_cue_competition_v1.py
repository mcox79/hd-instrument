"""exp_mcguffey_migrate_cue_competition_v1 -- DOES ONE BRAIN-FAITHFUL MECHANISM GENERALISE ACROSS ALL
NON-CANONICAL CONSTRUCTIONS? (the owner's "does this need to generalize?" answered with evidence.)

The passive-cue fix (exp_mcguffey_migrate_passive_cue_fix_v1) is construction-SPECIFIC: it recovers
passives (+0.60) but not inversion (-0.09) or fronting (0.0). A stack of per-construction patches is NOT
brain-faithful -- the brain has no "passive module". The Competition Model (Bates & MacWhinney 1989) +
Dowty proto-roles (1991) say role assignment is ONE mechanism: graded, additive, cue-validity-weighted
COMPETITION over a cue set, where each construction is a different cue configuration.

BRAIN-FAITHFUL CUE-COMPETITION ASSIGNER (this cell). For each content verb, score every candidate
nominal for PROTO-AGENT (PA) and PROTO-PATIENT (PP) by summing weighted cues, then ASSIGN by competition
(agent = argmax PA, patient = argmax PP among the rest):
  order cue      preverbal -> +PA, postverbal -> +PP        (English default word order, high validity)
  animacy cue    animate   -> +PA                            (Dowty sentience proto-agent)
  case cue       nominative pronoun -> +PA; accusative -> +PP (very high validity WHEN PRESENT)
  voice cue      passive (be+VBN): the subject NP -> +PP     (morphology overrides order)
This is ONE mechanism; canonical/passive/inversion/fronting are just different cue weightings of it.

CAN-FAIL:
  CUE must beat BROKEN on the WHOLE non-canonical set, CI-separated.
  CUE must GENERALISE where the passive patch does not: help inversion + fronting, not only passive.
  CUE must beat its INFO-FREE TWIN (all cue weights zeroed -> ties / coin-flip).
  CUE must NOT hurt canonical.
The cue weights are OUR-INVENTION-UNDER-TEST parameters (Competition Model validities are language-
specific and learned); a --sweep checks the result is not knife-edge on the weights.

Writes only to data/exp_mcguffey_migrate_cue_competition_v1/. Does NOT modify hdlab/.
"""
from __future__ import annotations
import argparse, json, os, sys
from collections import defaultdict, Counter
from datetime import datetime, timezone

import numpy as np
os.environ.setdefault("OMP_NUM_THREADS", "1")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments.exp_wire_organs_endtoend_v1 import (   # noqa: E402
    _pos, _passage_aliases, boot_ci, IN_SCOPE_ROLES, _seed_int, _PRO_ANY, _PRO_F, _PRO_M, _is_animate_head,
)
from experiments.exp_mcguffey_migrate_passive_cue_fix_v1 import committed as committed_ref, final_role_map   # noqa: E402

MODERN_GOLD = os.path.join(REPO, "data/eval_gold_mention_role_modern_ud_ewt_v1",
                           "gold_situation_modern_ud_ewt_v1.jsonl")
OUTDIR = os.path.join(REPO, "data/exp_mcguffey_migrate_cue_competition_v1")
# KB_REFERENT: data/eval_gold_mention_role_modern_ud_ewt_v1/gold_situation_modern_ud_ewt_v1.jsonl

_AUX = {"has", "have", "had", "is", "are", "was", "were", "be", "been", "being", "am",
        "do", "does", "did", "will", "would", "can", "could", "may", "might", "shall", "should", "must"}
_BE = {"is", "are", "was", "were", "be", "been", "being", "am"}
_NOM = {"he", "she", "they", "i", "we", "who"}          # nominative pronouns -> proto-agent
_ACC = {"him", "her", "them", "me", "us", "whom"}       # accusative pronouns -> proto-patient

# Competition Model cue validities (OUR-INVENTION-UNDER-TEST; swept, not adopted)
W = {"order": 1.0, "animacy": 0.7, "case": 1.3, "voice": 1.6}


def _cue_competition_roles(text, weights=None, twin=False, rng=None):
    w = dict(W if weights is None else weights)
    if twin:
        w = {k: 0.0 for k in w}            # info-free: zero all cues -> order-tie coin-flip
    toks = _pos(text)
    words = [x for x, _ in toks]
    tags = [t for _, t in toks]
    lw = [x.lower() for x in words]
    inq = [False] * len(words)
    q = False
    for i, x in enumerate(words):
        if x in ('"', '``', "''", "“", "”"):
            q = not q
        inq[i] = q

    def is_nominal(i):
        return (tags[i] in ("NNP", "NN", "NNS", "PRP", "PRP$") or lw[i] in _PRO_ANY) and lw[i] not in _AUX

    verb_idxs = [i for i, t in enumerate(tags) if t in ("VBD", "VBZ", "VBP", "VBG", "VBN")]
    content = [i for i in verb_idxs if lw[i] not in _AUX and not inq[i]] or \
              [i for i in verb_idxs if not inq[i]] or verb_idxs
    out = []
    pred = words[content[0]].lower() if content else None
    for vi in content:
        passive = False
        if tags[vi] == "VBN":
            j, steps = vi - 1, 0
            while j >= 0 and steps < 4:
                if lw[j] in _BE:
                    passive = True; break
                if lw[j] in _AUX or tags[j] in ("RB", "MD"):
                    j -= 1; steps += 1; continue
                break
        # candidate nominals within a window around the verb (skip aux, quotes, by-phrase agent handled via case/order)
        cands = [i for i in range(len(words)) if is_nominal(i) and not inq[i] and abs(i - vi) <= 8]
        if not cands:
            continue
        pa, pp = {}, {}
        for i in cands:
            preverbal = i < vi
            a = w["order"] if preverbal else 0.0
            p = w["order"] if not preverbal else 0.0
            if _is_animate_head(words[i], tags[i]):
                a += w["animacy"]
            if lw[i] in _NOM:
                a += w["case"]
            elif lw[i] in _ACC:
                p += w["case"]
            if passive and preverbal:          # passive subject -> proto-patient (voice overrides order)
                p += w["voice"]; a -= w["voice"]
            # by-phrase agent in a passive -> proto-agent
            if passive and i >= 1 and lw[i - 1] == "by":
                a += w["voice"]; p -= w["voice"]
            pa[i], pp[i] = a, p
        if twin and rng is not None:
            # info-free twin: assign roles by a coin flip over candidates
            order = list(cands); rng.shuffle(order)
            if order:
                out.append((words[order[0]], "agent"))
            if len(order) > 1:
                out.append((words[order[1]], "patient"))
            continue
        agent_i = max(cands, key=lambda i: pa[i])
        rest = [i for i in cands if i != agent_i]
        out.append((words[agent_i], "agent"))
        if rest:
            patient_i = max(rest, key=lambda i: pp[i])
            out.append((words[patient_i], "patient"))
    return out, pred


def committed_cue(passage, weights, twin, seed):
    ent_names = list(passage["entities"].keys())
    alias, gender = _passage_aliases(passage)
    rng = np.random.default_rng(_seed_int("TWIN" + passage["passage_id"], seed)) if twin else None
    seen_order, binds = [], []
    for ci, clause in enumerate(passage["clauses"]):
        for name in ent_names:
            if any(len(a) > 2 and a in clause.lower() for a in alias[name]):
                if name in seen_order:
                    seen_order.remove(name)
                seen_order.append(name)
        roles, _ = _cue_competition_roles(clause, weights=weights, twin=twin, rng=rng)
        for head, role in roles:
            hl = head.strip(".,\"'").lower()
            name_c = [n for n in ent_names if hl in alias[n]]
            if name_c:
                cands = name_c[:]
            elif hl in _PRO_ANY:
                want = "fem" if hl in _PRO_F else ("masc" if hl in _PRO_M else None)
                cands = [n for n in ent_names if (want is None or gender.get(n) in (want, None))]
            else:
                cands = []
            if not cands:
                continue
            cands_ranked = sorted(cands, key=lambda n: -(seen_order.index(n) if n in seen_order else -1))
            binds.append({"entity": cands_ranked[0], "clause": ci, "role": role})
    return binds


def score(passages, binder, seed, want_type=None, canonical=None):
    gm = Counter(q["gold_role"] for p in passages for q in p["target_queries"]
                 if q["gold_role"] in IN_SCOPE_ROLES).most_common(1)[0][0]
    vals = []
    for p in passages:
        binds = binder(p)
        by_ec, by_ent = {}, defaultdict(list)
        for b in binds:
            by_ec.setdefault((b["entity"], b["clause"]), b["role"])
            by_ent[b["entity"]].append(b)
        fr = final_role_map(p)
        for q in p["target_queries"]:
            if q["gold_role"] not in IN_SCOPE_ROLES:
                continue
            if want_type is not None and q.get("noncanon_type", "canonical") != want_type:
                continue
            if canonical is True and not q.get("canonical", True):
                continue
            if canonical is False and q.get("canonical", True):
                continue
            e, c, g = q["entity"], q["query_clause"], q["gold_role"]
            pr = by_ec.get((e, c)) or (max(by_ent[e], key=lambda x: x["clause"])["role"] if by_ent[e] else gm)
            vals.append(int(pr == g))
    if not vals:
        return {"acc": 0.0, "ci": [0.0, 0.0], "n": 0}
    m, lo, hi, _ = boot_ci(vals, seed=_seed_int(str(want_type) + str(canonical), seed))
    return {"acc": round(m, 4), "ci": [round(lo, 4), round(hi, 4)], "n": len(vals)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--seed", type=int, default=20260830)
    args = ap.parse_args()
    passages = [json.loads(l) for l in open(MODERN_GOLD, encoding="utf-8") if l.strip()]
    if args.self_test:
        passages = passages[:60]

    binders = {
        "BROKEN": lambda p: committed_ref(p, "BROKEN", False, args.seed),
        "PASSIVE_FIX": lambda p: committed_ref(p, "FIXED", False, args.seed),
        "CUE": lambda p: committed_cue(p, None, False, args.seed),
        "CUE_TWIN": lambda p: committed_cue(p, None, True, args.seed),
    }
    cuts = {"NONCANON": dict(canonical=False), "CANONICAL": dict(canonical=True),
            "passive": dict(want_type="passive"), "inversion": dict(want_type="inversion"),
            "fronting": dict(want_type="fronting")}
    res = {}
    for cut, kw in cuts.items():
        res[cut] = {arm: score(passages, b, args.seed, **kw) for arm, b in binders.items()}

    def sep(a, b):
        return a["ci"][0] > b["ci"][1]

    nc = res["NONCANON"]
    verdict = {
        "cue_beats_broken_noncanon_ci_sep": sep(nc["CUE"], nc["BROKEN"]),
        "cue_beats_twin_noncanon": nc["CUE"]["acc"] > nc["CUE_TWIN"]["acc"],
        "cue_not_hurt_canonical": res["CANONICAL"]["CUE"]["acc"] >= res["CANONICAL"]["BROKEN"]["acc"] - 0.03,
        "cue_generalises_beyond_passive": (res["inversion"]["CUE"]["acc"] - res["inversion"]["BROKEN"]["acc"] > 0.1)
                                          or (res["fronting"]["CUE"]["acc"] - res["fronting"]["BROKEN"]["acc"] > 0.1),
        "per_type_cue_vs_passivefix": {ty: {"broken": res[ty]["BROKEN"]["acc"], "passive_fix": res[ty]["PASSIVE_FIX"]["acc"],
                                            "cue": res[ty]["CUE"]["acc"]} for ty in ("passive", "inversion", "fronting")},
    }
    metrics = {"ts_iso": datetime.now(timezone.utc).isoformat(), "seed": args.seed, "weights": W,
               "cuts": res, "verdict": verdict}

    if args.sweep:
        sweeps = {}
        for name, ww in {"low_voice": {**W, "voice": 0.8}, "high_order": {**W, "order": 1.6},
                         "no_case": {**W, "case": 0.0}, "eq": {"order": 1.0, "animacy": 1.0, "case": 1.0, "voice": 1.0}}.items():
            b = lambda p, ww=ww: committed_cue(p, ww, False, args.seed)
            sweeps[name] = {"NONCANON": score(passages, b, args.seed, canonical=False)["acc"],
                            "CANONICAL": score(passages, b, args.seed, canonical=True)["acc"]}
        metrics["weight_sweep"] = sweeps

    if args.self_test:
        assert nc["CUE"]["n"] > 0
        print("self-test PASS", json.dumps(verdict["per_type_cue_vs_passivefix"]))
        return

    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print("=" * 88)
    print("CUE-COMPETITION ROLE ASSIGNER (one brain-faithful mechanism) vs BROKEN vs PASSIVE-only fix")
    print("=" * 88)
    for cut in ("CANONICAL", "NONCANON", "passive", "inversion", "fronting"):
        r = res[cut]
        print(f"  {cut:10s} n={r['CUE']['n']:3d} | BROKEN {r['BROKEN']['acc']:.3f}  PASSIVE_FIX "
              f"{r['PASSIVE_FIX']['acc']:.3f}  CUE {r['CUE']['acc']:.3f} {r['CUE']['ci']}  twin {r['CUE_TWIN']['acc']:.3f}")
    print("\nVERDICT:", json.dumps(verdict, indent=2))
    if "weight_sweep" in metrics:
        print("WEIGHT SWEEP (non-canon / canonical):", json.dumps(metrics["weight_sweep"], indent=2))
    print(f"\nwrote {os.path.relpath(os.path.join(OUTDIR,'metrics.json'), REPO)}")


if __name__ == "__main__":
    main()
