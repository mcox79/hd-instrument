"""exp_coref_agreement_animacy_filter_v1 -- OPTIMIZATION + FIDELITY probe: make the PINNED agreement
pre-filter faithful and measure the effect on competitive pronoun-antecedent resolution (LitBank).

WHY (owner: "is there more to optimize?"). The brain's gender/number/animacy agreement is a
near-categorical PRE-FILTER (PINNED; Nieuwland-VanBerkum ELAN/LAN timing) that prunes the candidate set to
a handful BEFORE cue-based retrieval competes over it. Our filter is LEAKY: a candidate entity that is
never referred to by a pronoun gets gender=None (a WILDCARD compatible with every pronoun), so on LitBank
(which annotates all 6 ACE entity types) a "he" competes against a mean ~40 candidates, ~92% of them
wildcard (places, ships, unnamed groups). The brain knows "Elizabeth" is a woman and "London" is not a
person. This cell adds two glass-box, offline agreement signals and measures the payoff:
  (1) NAME GENDER  -- data/lexicons/name_gender_gazetteer.tsv (NLTK first-names; abstains on ambiguous).
  (2) ANIMACY      -- an entity ever referred to by a PERSON pronoun (he/she/they/who...) is a person; an
                      entity ever referred to by IT and never by a person pronoun is inanimate.
The REFINED filter prunes a candidate for a PERSON pronoun iff it is KNOWN opposite-gender OR KNOWN
inanimate; for IT iff it is KNOWN a person. This is a resolver-mechanism fidelity fix (the agreement
stage), NOT a content/semantics cue -- it composes with the graded retrieval unchanged.

The competitive subset is REDEFINED under the refined filter (>=2 survivors), so it isolates the GENUINELY
hard cases. Both the incumbent tier and the graded retrieval run under each filter; the relative claim
(graded > incumbent) must survive, and the ABSOLUTE accuracy is the optimization.

Run: .venv/Scripts/python.exe experiments/exp_coref_agreement_animacy_filter_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_coref_agreement_animacy_filter_v1.py --run
# KB_REFERENT: data/litbank/who_did_what_events.json
# KB_REFERENT: data/lexicons/name_gender_gazetteer.tsv
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple

import numpy as np

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments.exp_litbank_activation_binder_v1 import PRONOUNS, _gn_compat  # noqa: E402
import experiments.exp_coref_graded_cue_retrieval_litbank_v1 as E1  # noqa: E402

GAZETTEER = os.path.join(REPO_ROOT, "data", "lexicons", "name_gender_gazetteer.tsv")
PERSON_PRON = frozenset({"he", "him", "his", "himself", "she", "her", "hers", "herself",
                         "they", "them", "their", "theirs", "themselves"})
IT_PRON = frozenset({"it", "its", "itself"})


def load_gazetteer() -> Dict[str, str]:
    g = {}
    with open(GAZETTEER, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) >= 2 and parts[1].strip() in ("m", "f", "masc", "fem"):
                g[parts[0].strip().lower()] = "m" if parts[1].strip() in ("m", "masc") else "f"
    return g


def entity_profiles(stream, gaz) -> Dict[int, Dict]:
    """Per gold entity: refined gender (own person-pronouns -> gazetteer name-head -> None) + animacy
    ('person' | 'inanimate' | 'unknown'). Number from own pronouns (else singular)."""
    pers_g, num_c = defaultdict(Counter), defaultdict(Counter)
    person_flag, it_flag = defaultdict(bool), defaultdict(bool)
    name_gender = {}
    for m in stream:
        e = m["gold"]; ht = m["head_text"]
        if ht in PRONOUNS:
            g, n = PRONOUNS[ht]
            num_c[e][n] += 1
            if ht in PERSON_PRON:
                person_flag[e] = True
                if g in ("m", "f"):
                    pers_g[e][g] += 1
            elif ht in IT_PRON:
                it_flag[e] = True
        else:
            if e not in name_gender and ht in gaz:   # first-token name gazetteer hit
                name_gender[e] = gaz[ht]
    out = {}
    for e in {m["gold"] for m in stream}:
        if pers_g[e]:
            gender = pers_g[e].most_common(1)[0][0]
        elif e in name_gender:
            gender = name_gender[e]
        else:
            gender = None
        number = num_c[e].most_common(1)[0][0] if num_c[e] else None
        if person_flag[e] or e in name_gender:
            anim = "person"
        elif it_flag[e]:
            anim = "inanimate"
        else:
            anim = "unknown"
        out[e] = {"gender": gender, "number": number, "animacy": anim}
    return out


def _compatible(prof: Dict, ht: str) -> bool:
    """Refined agreement+animacy compatibility of a candidate entity with pronoun surface ht."""
    pg, pn = PRONOUNS[ht]
    if not _gn_compat(pg, pn, prof["gender"], prof["number"]):
        return False
    if ht in PERSON_PRON and prof["animacy"] == "inanimate":
        return False
    if ht in IT_PRON and prof["animacy"] == "person":
        return False
    return True


def build_instances(streams, refined: bool, gaz) -> Tuple[List[Dict], float]:
    """Competitive instances under the LEAKY (refined=False, E1's own filter) or REFINED filter.
    Returns (instances, mean_pool_size)."""
    if not refined:
        insts = E1.build_instances(streams)
        pools = [len(i["cand_ids"]) for i in insts]
        return insts, (sum(pools) / len(pools) if pools else 0.0)
    out = []
    pools = []
    for rec in streams:
        stream = rec["stream"]
        prof = entity_profiles(stream, gaz)
        prior_by_cluster: Dict[int, List[Tuple[int, str]]] = defaultdict(list)
        for m in stream:
            ht = m["head_text"]; gold = m["gold"]
            if ht in PRONOUNS:
                cand = {}
                for c, pri in prior_by_cluster.items():
                    if pri and _compatible(prof.get(c, {"gender": None, "number": None,
                                                        "animacy": "unknown"}), ht):
                        cand[c] = list(pri)
                if gold in cand and len(cand) >= 2:
                    pools.append(len(cand))
                    out.append({"doc": rec["doc"], "pronoun": ht, "p_sent": m["sent"],
                                "pron_role": m["role"], "gold_cid": gold, "cand_ids": sorted(cand),
                                "prior": {c: cand[c] for c in cand}})
            prior_by_cluster[gold].append((m["sent"], m["role"]))
    return out, (sum(pools) / len(pools) if pools else 0.0)


def _run_arms(insts, n_boot, seed):
    """Split DEV/TEST by doc, tune graded on DEV, report TEST accuracy + graded-vs-incumbent contrast."""
    all_docs = sorted({i["doc"] for i in insts})
    dev = [i for i in insts if i["doc"] in set(all_docs[0::2])]
    test = [i for i in insts if i["doc"] in set(all_docs[1::2])]
    weights, gain, d = E1.tune_graded(dev)
    ev = E1.evaluate(test, weights, gain, d, seed=seed)
    pd = ev["per_doc"]
    acc = {a: E1._ci(E1._pairs(pd[a]), n_boot, seed + i) for i, a in enumerate(E1.ARMS)}
    gms = E1._paired(pd["graded"], pd["strict_cb"], n_boot, seed + 40)
    gmr = E1._paired(pd["graded"], pd["random"], n_boot, seed + 41)
    auc = E1._entropy_error_auc(ev["graded_recs"])
    return {"n_test_instances": len(test), "accuracy": acc, "graded_minus_strict_cb": gms,
            "graded_minus_random": gmr, "entropy_error_AUC": round(auc, 4),
            "tuned_weights": {k: round(v, 3) for k, v in weights.items()}, "tuned_d": d}


def cell(docs: Optional[int] = None, n_boot: int = 1500, seed: int = E1.SEED) -> Dict:
    gaz = load_gazetteer()
    streams = E1.load_streams(docs)
    leaky, pool_leaky = build_instances(streams, False, gaz)
    refined, pool_refined = build_instances(streams, True, gaz)
    return {
        "anchor": "coref_agreement_animacy_filter_v1",
        "gazetteer_names": len(gaz),
        "mean_pool_LEAKY": round(pool_leaky, 2), "mean_pool_REFINED": round(pool_refined, 2),
        "n_competitive_LEAKY": len(leaky), "n_competitive_REFINED": len(refined),
        "LEAKY_filter": _run_arms(leaky, n_boot, seed + 100),
        "REFINED_filter": _run_arms(refined, n_boot, seed + 200),
    }


def self_test():
    gaz = load_gazetteer()
    assert gaz.get("elizabeth") == "f" and gaz.get("john") == "m", "gazetteer basic lookups"
    # a 'he' must prune a KNOWN-female name entity and a KNOWN-inanimate entity
    stream = [
        {"sent": 0, "gold": 0, "role": "SUBJECT", "head_text": "john", "gov_verb": "go"},
        {"sent": 0, "gold": 1, "role": "SUBJECT", "head_text": "elizabeth", "gov_verb": "sit"},
        {"sent": 1, "gold": 2, "role": "OBJECT", "head_text": "london", "gov_verb": "see"},
        {"sent": 1, "gold": 2, "role": "SUBJECT", "head_text": "it", "gov_verb": "lie"},
        {"sent": 2, "gold": 0, "role": "SUBJECT", "head_text": "he", "gov_verb": "walk"},
    ]
    prof = entity_profiles(stream, gaz)
    assert prof[1]["gender"] == "f", "Elizabeth -> female via gazetteer"
    assert prof[2]["animacy"] == "inanimate", "London (it-pronominalized) -> inanimate"
    assert _compatible(prof[0], "he") and not _compatible(prof[1], "he") \
        and not _compatible(prof[2], "he"), "refined filter prunes female name + inanimate for 'he'"
    print("SELF-TEST PASS (gazetteer gender + animacy prune female-name and inanimate candidates for 'he')")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--docs", type=int, default=None)
    ap.add_argument("--n-boot", type=int, default=1500)
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.run:
        print(json.dumps(cell(docs=args.docs, n_boot=args.n_boot), indent=2))
        return
    print("use --self-test | --run")


if __name__ == "__main__":
    main()
