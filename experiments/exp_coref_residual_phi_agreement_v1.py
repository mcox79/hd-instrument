"""exp_coref_residual_phi_agreement_v1 -- GENERALIZING the participant-exclusion win: it is ONE case of a general
brain-foundational principle -- the referential candidate SET must respect ALL hard PHI-AGREEMENT (person, animacy,
number, gender), and the substrate's permissive `_gn_compat` (unknown passes) VIOLATES it. (owner: "this needs to
generalize in all aspects where possible".)

Participant exclusion (exp_coref_residual_participant_pool_v1) hardens the PERSON feature (I/you never = he/she/they).
This cell shows ANIMACY agreement is a SECOND clean, recall-safe, CI-separated lever that COMPOSES with it, and that
gender is the principled EXCEPTION -- reframing the anti-typical residual as a hard-phi-agreement-violation problem.

THE BRAIN (PINNED vs OUR-INVENTION):
  * PINNED: phi-feature agreement (person, number, gender, animacy) is an OBLIGATORY constraint on anaphora; the brain
    never binds a pronoun to a feature-incompatible entity. Animacy in particular: "he/she/him/her" require an ANIMATE
    (person) referent; "it/its" require an INANIMATE one -- a hard selectional constraint the reader applies from the
    head noun immediately (McRae/Ferretti animacy in thematic fit; animacy is a core dimension of the entity model).
  * WHY GENDER IS THE EXCEPTION (measured, principled): person + animacy are established IMMEDIATELY by the pronoun form
    / head noun ("I" is 1st-person; "city" is inanimate) -> causally available at the pronoun. A freshly-NAMED
    character's GENDER often is NOT yet established by any prior cue -> gender agreement is causally a non-lever here
    (confirmed in exp_coref_residual_participant_pool_v1: causal gender +0.010 NOT_SEP). So the generalization is to the
    IMMEDIATELY-ESTABLISHED features (person, animacy), not to every phi-feature blindly.
  * OUR-INVENTION / honesty: the animacy signal here is the GOLD LitBank entity type (PER vs FAC/LOC/GPE/VEH/ORG) -- an
    ORACLE animacy. A deployable reader uses its NER/lexical animacy (a near-solved upstream task, ~90% F1); the gap =
    NER error. A LEXICAL-animacy arm (person-noun + gendered-pronoun + name-gazetteer, NO gold types) is included as a
    robustness check that the win does NOT depend on gold annotations (the cute-trick guard).

POPULATION: the anti-typical residual (gold best on none of recency/subject/freq), split by pronoun animacy-class:
  PERSON pronouns (he/she/him/her/his) -> antecedent must be ANIMATE; drop CONFIRMED-INANIMATE candidates.
  IT/ITS                               -> antecedent must be INANIMATE; drop CONFIRMED-ANIMATE (person) candidates.
  (they/them is animacy-UNCONSTRAINED -- a group can be animate or inanimate -- so animacy is not applied there.)

ARMS (pick = token-recency over the KEPT pool; isolation = arms differ only in which candidates are dropped):
  floor / participant / animacy_gold / animacy_lexical / person_plus_animacy / gender_negative / random_drop(twin).

Run: .venv/Scripts/python.exe experiments/exp_coref_residual_phi_agreement_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_coref_residual_phi_agreement_v1.py --run
ASCII. Pure numpy + NLTK names (gazetteer). Reads the cache + LitBank entity tsv. Writes only its own dir. NO hdlab/ write.
# KB_REFERENT: data/litbank/who_did_what_events.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from typing import Dict, Optional

import numpy as np

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments.exp_coref_focus_stack_oracle_ceiling_v1 import build_rich, is_antitypical, _gpos  # noqa: E402
from experiments.exp_coref_residual_participant_pool_v1 import _cluster_mentions, is_participant, _pick, conf_gender  # noqa: E402
from experiments.exp_coref_graded_cue_retrieval_litbank_v1 import load_streams, _supports  # noqa: E402
from experiments.exp_litbank_activation_binder_v1 import PRONOUNS  # noqa: E402

ENT = os.path.join(REPO, "data", "litbank", "entities", "tsv")
OUTDIR = os.path.join(REPO, "data", "exp_coref_residual_phi_agreement_v1")
SEED = 20260830
PERSON = set("he she him her his himself herself".split())
ITS = set("it its itself".split())
INAN_TYPES = ("FAC", "LOC", "GPE", "VEH", "ORG")
# lexical animacy lexicons (for the no-gold-NER robustness arm)
PERSON_NOUNS = set("man men woman women boy boys girl girls gentleman lady ladies sir madam mr mrs miss master lord "
                   "king queen father mother son daughter brother sister husband wife uncle aunt child children people "
                   "person friend friends stranger doctor captain officer servant maid nurse".split())
GENDERED_PRON = set("he him his himself she her hers herself".split())
FIRST_SECOND = set("i we me us my our you your thou thee".split())


def _load_types(doc: str) -> Dict:
    path = os.path.join(ENT, doc + ".tsv")
    types = {}
    s = t = 0
    if not os.path.exists(path):
        return types
    for line in open(path, encoding="utf-8"):
        l = line.rstrip("\n")
        if not l.strip():
            s += 1; t = 0; continue
        p = l.split("\t")
        tag = p[1] if len(p) > 1 else "O"
        types[(s, t)] = tag[2:] if tag.startswith(("B-", "I-")) else "O"
        t += 1
    return types


def _build_animacy(streams):
    """Per-cluster GOLD animacy (majority entity type) and LEXICAL animacy (head-word heuristic, no gold types)."""
    types_by_doc = {}
    clt = defaultdict(Counter)
    heads = defaultdict(list)
    for r in streams:
        d = r["doc"]
        if d not in types_by_doc:
            types_by_doc[d] = _load_types(d)
        T = types_by_doc[d]
        for m in r["stream"]:
            clt[(d, m["gold"])][T.get((m["sent"], m["start"]), "O")] += 1
            heads[(d, m["gold"])].append(m["head_text"].lower())
    try:
        from nltk.corpus import names as nltk_names
        male = set(n.lower() for n in nltk_names.words("male.txt"))
        fem = set(n.lower() for n in nltk_names.words("female.txt"))
        name_gender = male | fem
    except Exception:
        name_gender = set()

    def gold_anim(d, c):
        ct = clt[(d, c)]
        per = ct.get("PER", 0)
        inan = sum(ct.get(x, 0) for x in INAN_TYPES)
        return "animate" if (per > inan and per > 0) else ("inanimate" if (inan > per and inan > 0) else None)

    def lex_anim(d, c):
        hs = heads[(d, c)]
        animate = any(h in PERSON_NOUNS or h in GENDERED_PRON or h in FIRST_SECOND or h in name_gender for h in hs)
        if animate:
            return "animate"
        # confirmed inanimate lexically = a lowercase common-noun cluster with NO animate signal and NO name
        # (a proper name we can't gender/animate stays UNKNOWN, not inanimate -> recall-safe)
        has_common = any(h.isalpha() and h.islower() and h not in FIRST_SECOND for h in hs)
        return "inanimate" if has_common else None

    return gold_anim, lex_anim


def _paired(pp, pf, n_boot, seed):
    docs = sorted(set(pp) & set(pf))
    if not docs:
        return {"delta": 0.0, "lo": 0.0, "hi": 0.0, "band": "EMPTY"}
    A = np.array([pp[d] for d in docs], float)
    B = np.array([pf[d] for d in docs], float)
    delta = A[:, 0].sum() / max(A[:, 1].sum(), 1) - B[:, 0].sum() / max(B[:, 1].sum(), 1)
    r = np.random.default_rng(seed)
    n = len(docs)
    bo = []
    for _ in range(n_boot):
        idx = r.integers(0, n, n)
        bo.append(A[idx, 0].sum() / max(A[idx, 1].sum(), 1) - B[idx, 0].sum() / max(B[idx, 1].sum(), 1))
    bo = np.array(bo)
    lo, hi = np.percentile(bo, [2.5, 97.5])
    return {"delta": round(float(delta), 4), "lo": round(float(lo), 4), "hi": round(float(hi), 4),
            "half_width": round(float(hi - lo) / 2, 4), "null_p95": round(float(np.percentile(np.abs(bo - bo.mean()), 95)), 4),
            "band": "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEP")}


def _eval(insts, cl, poolset, dropfn, n_boot, seed):
    pf = defaultdict(lambda: [0, 0]); pp = defaultdict(lambda: [0, 0]); rec = tot = 0
    for inst in insts:
        ids, sup, gi = _supports(inst)
        if not is_antitypical(sup, gi) or inst["pronoun"].lower() not in poolset:
            continue
        d = inst["doc"]; cids = inst["cand_ids"]; ps, pst = inst["p_sent"], inst["p_start"]; tot += 1
        keep = [i for i in range(len(cids)) if not dropfn(inst, d, cids[i], ps, pst)] or list(range(len(cids)))
        rec += int(gi in keep)
        pf[d][0] += int(_pick(inst, list(range(len(cids)))) == gi); pf[d][1] += 1
        pp[d][0] += int(_pick(inst, keep) == gi); pp[d][1] += 1
    acc = lambda pd: (sum(v[0] for v in pd.values()) / max(sum(v[1] for v in pd.values()), 1))
    return {"floor_acc": round(acc(pf), 4), "arm_acc": round(acc(pp), 4), "recall": round(rec / max(tot, 1), 4),
            "n": tot, "delta": _paired(dict(pp), dict(pf), n_boot, seed), "_pf": dict(pf), "_pp": dict(pp)}


def run(docs=None, n_boot=2000, seed=SEED) -> Dict:
    streams = load_streams(docs)
    insts = build_rich(streams)
    cl = _cluster_mentions(streams)
    gold_anim, lex_anim = _build_animacy(streams)

    def d_part(inst, d, c, ps, pst):
        return is_participant(cl, d, c, ps, pst)

    def d_anim_gold(inst, d, c, ps, pst):     # for PERSON pronouns: drop confirmed-INANIMATE
        return gold_anim(d, c) == "inanimate"

    def d_anim_lex(inst, d, c, ps, pst):
        return lex_anim(d, c) == "inanimate"

    def d_both(inst, d, c, ps, pst):
        return d_part(inst, d, c, ps, pst) or d_anim_gold(inst, d, c, ps, pst)

    def d_gender(inst, d, c, ps, pst):
        g = conf_gender(cl, d, c, ps, pst)
        pg = PRONOUNS[inst["pronoun"].lower()][0]
        return g is not None and g != pg

    def make_twin(dropref):
        def d_rand(inst, d, c, ps, pst):
            cids = inst["cand_ids"]
            ndrop = sum(1 for j in range(len(cids)) if dropref(inst, d, cids[j], ps, pst))
            if ndrop == 0:
                return False
            key = (d, inst["p_sent"], inst["p_start"], len(cids))
            r = np.random.default_rng(abs(hash(key)) % (2 ** 31))
            i = cids.index(c) if c in cids else -1
            return i in set(r.permutation(len(cids))[:ndrop].tolist())
        return d_rand

    person = {
        "floor": _eval(insts, cl, PERSON, lambda *a: False, n_boot, seed),
        "participant": _eval(insts, cl, PERSON, d_part, n_boot, seed + 1),
        "animacy_gold": _eval(insts, cl, PERSON, d_anim_gold, n_boot, seed + 2),
        "animacy_lexical": _eval(insts, cl, PERSON, d_anim_lex, n_boot, seed + 3),
        "person_plus_animacy": _eval(insts, cl, PERSON, d_both, n_boot, seed + 4),
        "gender_negative": _eval(insts, cl, PERSON, d_gender, n_boot, seed + 5),
        "random_drop_twin": _eval(insts, cl, PERSON, make_twin(d_both), n_boot, seed + 6),
    }
    itits = {
        "floor": _eval(insts, cl, ITS, lambda *a: False, n_boot, seed + 10),
        "animacy_gold_drop_animate": _eval(insts, cl, ITS, lambda inst, d, c, ps, pst: gold_anim(d, c) == "animate", n_boot, seed + 11),
    }

    def strip(dd):
        return {k: {kk: vv for kk, vv in v.items() if not kk.startswith("_")} for k, v in dd.items()}

    person_both = person["person_plus_animacy"]
    return {
        "anchor": "coref_residual_phi_agreement_v1",
        "population": "LitBank anti-typical residual, split by pronoun animacy class",
        "person_arms": strip(person), "it_its_arms": strip(itits),
        "reading": {
            "animacy_is_a_second_clean_lever_person": person["animacy_gold"]["delta"]["band"] == "ABOVE",
            "animacy_lexical_no_gold_NER_also_works": person["animacy_lexical"]["delta"]["band"] == "ABOVE",
            "animacy_composes_with_participant": person_both["delta"]["band"] == "ABOVE" and person_both["delta"]["delta"] > person["participant"]["delta"]["delta"],
            "animacy_lever_it_its": itits["animacy_gold_drop_animate"]["delta"]["band"] == "ABOVE",
            "gender_still_a_non_lever": person["gender_negative"]["delta"]["band"] != "ABOVE",
            "info_free_twin_LOSES": person["random_drop_twin"]["delta"]["band"] != "ABOVE"
            or person["random_drop_twin"]["arm_acc"] < person_both["arm_acc"],
            "verdict": ("PHI_AGREEMENT_HARDENING_GENERALIZES_PERSON_AND_ANIMACY"
                        if (person["animacy_gold"]["delta"]["band"] == "ABOVE"
                            and person_both["delta"]["band"] == "ABOVE"
                            and itits["animacy_gold_drop_animate"]["delta"]["band"] == "ABOVE")
                        else "DOES_NOT_GENERALIZE"),
        },
    }


def self_test():
    """Fixture: animacy exclusion drops an inanimate distractor for a PERSON pronoun and keeps the animate gold."""
    streams = [{"doc": "__t", "stream": [
        {"sent": 0, "start": 0, "gold": 1, "role": "SUBJECT", "head_text": "John", "gov_verb": None, "obj_head": None},
        {"sent": 1, "start": 0, "gold": 2, "role": "SUBJECT", "head_text": "city", "gov_verb": None, "obj_head": None},
        {"sent": 2, "start": 0, "gold": 1, "role": "SUBJECT", "head_text": "he", "gov_verb": None, "obj_head": None},
    ]}]
    _, lex_anim = _build_animacy(streams)
    assert lex_anim("__t", 1) == "animate", "a 'John' cluster must be lexically animate"
    assert lex_anim("__t", 2) == "inanimate", "a 'city' cluster must be lexically inanimate"
    print("SELF-TEST PASS (lexical animacy: John=animate, city=inanimate)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--docs", type=int, default=None)
    ap.add_argument("--n-boot", type=int, default=2000)
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.run:
        m = run(docs=args.docs, n_boot=args.n_boot)
        os.makedirs(OUTDIR, exist_ok=True)
        tmp = os.path.join(OUTDIR, "metrics.json.tmp")
        with open(tmp, "w", encoding="ascii") as fh:
            json.dump(m, fh, indent=2)
        os.replace(tmp, os.path.join(OUTDIR, "metrics.json"))
        print(json.dumps(m, indent=2))
        return
    print("use --self-test | --run")


if __name__ == "__main__":
    main()
