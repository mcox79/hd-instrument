"""exp_mcguffey_migrate_passive_cue_fix_v1 -- THE NON-CANONICAL WALL IS A FIXABLE CUE GAP, NOT A CEILING.

Problem: the_reader_eval_is_scored_on_200_year_old_mcguffey_migrate_to_modern_text (p1).

The migration (Cell exp_mcguffey_migrate_revalidate_v1) surfaced a WALL: the reader's role front-end
collapses to 0.277 on modern NON-CANONICAL constructions (below the coin-flip twin) -- McGuffey's ~0%
non-canonical rate structurally hid it. Diagnosis: on a passive ("X has been surrounded by Y"), nltk
tags has/VBZ been/VBN surrounded/VBN; the vargs front-end extracts (X, agent) from the AUXILIARY "has"
BEFORE reaching the content participle, and by_ec.setdefault keeps that first (wrong) binding. The
organ assigns thematic roles from AUXILIARIES instead of the CONTENT verb where voice morphology lives.

BRAIN-FAITHFUL FIX (Competition Model cue-validity, Bates & MacWhinney; lemma/lexeme split, Levelt):
auxiliaries carry tense/aspect/VOICE; the CONTENT verb carries predicate-argument structure. Skip the
auxiliary chain, assign roles from the content verb, and let the PASSIVE-MORPHOLOGY cue (be + past
participle, optional by-phrase) OVERRIDE word order there -- its cue validity in the passive
construction is ~1.0. The brain reads passives; so can we.

CAN-FAIL (the demonstration is a real test, not a fit):
  FIXED must beat BROKEN on NON-CANONICAL, CI-separated.
  FIXED must NOT hurt CANONICAL (no free lunch traded for the fix).
  FIXED must beat its INFO-FREE TWIN (passive cue scrambled -> a coin-flip voice) -- so the gain comes
  FROM the passive cue, not from an unrelated change.

Change the CORPUS is this problem's job; this cell does NOT modify hdlab -- it PROVES the exposed gap is
fixable and hands strategy a proposed organ diff. Writes only to data/exp_mcguffey_migrate_passive_cue_fix_v1/.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

os.environ.setdefault("OMP_NUM_THREADS", "1")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments.exp_wire_organs_endtoend_v1 import (   # noqa: E402
    _pos, _passage_aliases, boot_ci, IN_SCOPE_ROLES, _seed_int, _PRO_ANY, _PRO_F, _PRO_M,
    _extract_clause_roles_vargs, _is_animate_head,
)

MODERN_GOLD = os.path.join(REPO, "data/eval_gold_mention_role_modern_ud_ewt_v1",
                           "gold_situation_modern_ud_ewt_v1.jsonl")
OUTDIR = os.path.join(REPO, "data/exp_mcguffey_migrate_passive_cue_fix_v1")
# KB_REFERENT: data/eval_gold_mention_role_modern_ud_ewt_v1/gold_situation_modern_ud_ewt_v1.jsonl

_AUX = {"has", "have", "had", "is", "are", "was", "were", "be", "been", "being", "am",
        "do", "does", "did", "will", "would", "can", "could", "may", "might", "shall",
        "should", "must", "'s", "'re", "'ve", "'d", "'ll"}
_BE = {"is", "are", "was", "were", "be", "been", "being", "am", "'s", "'re"}


def _content_verb_roles(text, twin=False, rng=None):
    """Passive-aware role assigner: assign roles from the CONTENT verb (skip the aux chain); the
    passive-morphology cue (be-aux + VBN, optional by-phrase) overrides word order. twin=True scrambles
    the voice cue (coin-flip passive) -- the info-free control."""
    toks = _pos(text)
    words = [w for w, _ in toks]
    tags = [t for _, t in toks]
    lw = [w.lower() for w in words]
    # mark quoted spans
    inq = [False] * len(words)
    q = False
    for i, w in enumerate(words):
        if w in ('"', '``', "''", "“", "”"):
            q = not q
        inq[i] = q

    def is_nominal(i):
        return tags[i] in ("NNP", "NN", "NNS", "PRP", "PRP$") or lw[i] in _PRO_ANY

    verb_idxs = [i for i, t in enumerate(tags) if t in ("VBD", "VBZ", "VBP", "VBG", "VBN")]
    # CONTENT verbs = verb tokens whose lemma is not a pure auxiliary (unless nothing else is left)
    content = [i for i in verb_idxs if lw[i] not in _AUX and not inq[i]]
    if not content:
        content = [i for i in verb_idxs if not inq[i]] or verb_idxs
    out = []
    pred = words[content[0]].lower() if content else None
    for vi in content:
        # passive iff a be-aux appears in the immediately preceding aux chain and this verb is a participle
        passive = False
        if tags[vi] == "VBN":
            j = vi - 1
            steps = 0
            while j >= 0 and steps < 4:
                if lw[j] in _BE:
                    passive = True
                    break
                if lw[j] in _AUX or tags[j] in ("RB", "MD"):   # walk back over aux/adverb chain
                    j -= 1
                    steps += 1
                    continue
                break
        if twin and rng is not None:
            passive = bool(rng.integers(0, 2))   # scramble the voice cue (info-free twin)
        subj = next((words[i] for i in range(vi - 1, -1, -1) if is_nominal(i) and not inq[i]
                     and lw[i] not in _AUX), None)
        # object: first nominal after the verb that is NOT the head of a by-phrase agent
        obj = None
        for i in range(vi + 1, len(words)):
            if inq[i] or not is_nominal(i):
                continue
            # skip the by-phrase agent NP in a passive
            if passive and i >= 1 and lw[i - 1] == "by":
                continue
            obj = words[i]
            break
        by_agent = None
        if passive:
            for i in range(vi + 1, len(words)):
                if lw[i] == "by":
                    nxt = next((words[k] for k in range(i + 1, len(words)) if is_nominal(k)), None)
                    by_agent = nxt
                    break
        if not passive:
            if subj:
                out.append((subj, "agent"))
            if obj:
                out.append((obj, "patient"))
        else:
            if subj:
                out.append((subj, "patient"))
            if by_agent:
                out.append((by_agent, "agent"))
    return out, pred


def _extract(text, arm, twin, rng):
    if arm == "BROKEN":
        return _extract_clause_roles_vargs(text, twin=twin, rng=rng)
    return _content_verb_roles(text, twin=twin, rng=rng)


def committed(passage, arm, twin, seed):
    """Replicate live_extract_raw's candidate/recency + recency-resolve, with a pluggable extractor."""
    ent_names = list(passage["entities"].keys())
    alias, gender = _passage_aliases(passage)
    rng = np.random.default_rng(_seed_int("TWIN" + passage["passage_id"], seed)) if twin else None
    seen_order = []
    binds = []
    for ci, clause in enumerate(passage["clauses"]):
        for name in ent_names:
            if any(len(a) > 2 and a in clause.lower() for a in alias[name]):
                if name in seen_order:
                    seen_order.remove(name)
                seen_order.append(name)
        roles, _pred = _extract(clause, arm, twin, rng)
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


def final_role_map(passage):
    return {n: max(ch, key=lambda x: x["clause"])["role"] for n, ch in passage["entities"].items()}


def canonical_of(passage):
    return {(q["entity"], q["query_clause"]): q.get("canonical", True) for q in passage["target_queries"]}


def score(passages, arm, twin, seed, subset):
    from collections import Counter
    gm = Counter(q["gold_role"] for p in passages for q in p["target_queries"]
                 if q["gold_role"] in IN_SCOPE_ROLES).most_common(1)[0][0]
    vals = []
    for p in passages:
        binds = committed(p, arm, twin, seed)
        by_ec, by_ent = {}, defaultdict(list)
        for b in binds:
            by_ec.setdefault((b["entity"], b["clause"]), b["role"])
            by_ent[b["entity"]].append(b)
        fr = final_role_map(p)
        cm = canonical_of(p)
        for qq in p["target_queries"]:
            ent, qc, gold = qq["entity"], qq["query_clause"], qq["gold_role"]
            if gold not in IN_SCOPE_ROLES:
                continue
            canon = cm.get((ent, qc), True)
            if subset == "CANONICAL" and not canon:
                continue
            if subset == "NONCANONICAL" and canon:
                continue
            if subset == "ROLE_VARYING" and gold == fr.get(ent):
                continue
            if (ent, qc) in by_ec:
                pr = by_ec[(ent, qc)]
            elif by_ent[ent]:
                pr = max(by_ent[ent], key=lambda x: x["clause"])["role"]
            else:
                pr = gm
            vals.append(int(pr == gold))
    if not vals:
        return {"acc": 0.0, "ci": [0.0, 0.0], "hw": 0.0, "n": 0}
    m, lo, hi, hw = boot_ci(vals, seed=_seed_int(arm + str(twin) + subset, seed))
    return {"acc": round(m, 4), "ci": [round(lo, 4), round(hi, 4)], "hw": round(hw, 4), "n": len(vals)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--seed", type=int, default=20260830)
    args = ap.parse_args()
    passages = [json.loads(l) for l in open(MODERN_GOLD, encoding="utf-8") if l.strip()]
    if args.self_test:
        passages = passages[:40]

    res = {}
    for sub in ("ALL_INSCOPE", "CANONICAL", "NONCANONICAL", "ROLE_VARYING"):
        res[sub] = {
            "BROKEN": score(passages, "BROKEN", False, args.seed, sub),
            "FIXED": score(passages, "FIXED", False, args.seed, sub),
            "FIXED_TWIN": score(passages, "FIXED", True, args.seed, sub),
        }

    def sep(a, b):
        return a["ci"][0] > b["ci"][1]

    nc = res["NONCANONICAL"]
    ca = res["CANONICAL"]
    verdict = {
        "fixed_beats_broken_noncanonical_ci_sep": sep(nc["FIXED"], nc["BROKEN"]),
        "fixed_beats_twin_noncanonical": nc["FIXED"]["acc"] > nc["FIXED_TWIN"]["acc"],
        "fixed_not_hurt_canonical": ca["FIXED"]["acc"] >= ca["BROKEN"]["acc"] - 0.03,
        "noncanon_broken": nc["BROKEN"]["acc"], "noncanon_fixed": nc["FIXED"]["acc"],
        "noncanon_twin": nc["FIXED_TWIN"]["acc"],
    }
    metrics = {"ts_iso": datetime.now(timezone.utc).isoformat(), "seed": args.seed,
               "subsets": res, "verdict": verdict}

    if args.self_test:
        assert nc["FIXED"]["n"] > 0 and nc["BROKEN"]["n"] > 0
        print("self-test PASS", json.dumps({k: verdict[k] for k in
              ("noncanon_broken", "noncanon_fixed", "noncanon_twin")}))
        return

    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print("=" * 84)
    print("PASSIVE-CUE FIX (brain-faithful content-verb role assigner) on modern UD-EWT")
    print("=" * 84)
    for sub in ("ALL_INSCOPE", "CANONICAL", "NONCANONICAL", "ROLE_VARYING"):
        r = res[sub]
        print(f"  {sub:14s} n={r['FIXED']['n']:4d} | BROKEN {r['BROKEN']['acc']:.3f}"
              f"  FIXED {r['FIXED']['acc']:.3f} (+/-{r['FIXED']['hw']:.3f})"
              f"  FIXED_TWIN {r['FIXED_TWIN']['acc']:.3f}")
    print("\nVERDICT:", json.dumps(verdict, indent=2))
    print(f"\nwrote {os.path.relpath(os.path.join(OUTDIR,'metrics.json'), REPO)}")


if __name__ == "__main__":
    main()
