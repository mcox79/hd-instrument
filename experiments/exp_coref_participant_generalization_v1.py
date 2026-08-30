"""exp_coref_participant_generalization_v1 -- does the DISCOURSE-PARTICIPANT EXCLUSION lever GENERALIZE, or is it a
19c-first-person-novel artifact? (owner: "this needs to generalize too".)

The lever (exp_coref_residual_participant_pool_v1): exclude clusters whose PRIOR mentions are >=50% 1st/2nd-person
(discourse participants) from a 3rd-person pronoun's candidate pool -> +0.079 CI-sep on the LitBank anti-typical
residual. THE RISK: it might only help because 19c novels have a chatty 1st-person NARRATOR ("I") that floods the
pool. If so it would not generalize.

THE BRAIN-FAITHFUL PREDICTION (person-feature agreement / deixis is a UNIVERSAL, not a genre quirk): the PRINCIPLE
(participants I/you are never 3rd-person antecedents) holds everywhere; the BENEFIT scales with how much participant
pollution a text actually has -- large in 1st-person narration + dialogue, ~zero in 3rd-person exposition -- and it
must NEVER HURT (excluding a participant can only remove a wrong 3rd-person antecedent; gold is a participant ~0.5%).
So a clean generalization = helps where pollution exists, neutral where it doesn't, negative NOWHERE.

SPLITS (each computed on the anti-typical residual; paired per-doc bootstrap of participant-exclusion MINUS the
token-recency floor):
  narration_person   1st-person-narrated docs (narrator says "I" in NARRATION, outside quotes) vs 3rd-person-narrated.
  dialogue_density   docs above/below the median fraction of QUOTED (dialogue) sentences.
  pronoun_class      person (he/she/him/her) vs neuter/plural (it/its/they/them) -- person-feature applies to both.
This is a WITHIN-LitBank genre generalization (no modern coref corpus is on disk; the lever is STRUCTURAL /
person-feature, hence far LESS corpus-age-exposed than any lexical/meaning cue -- flagged, not hidden).

Run: .venv/Scripts/python.exe experiments/exp_coref_participant_generalization_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_coref_participant_generalization_v1.py --run
ASCII. Pure numpy. Reads the pre-parsed cache + conll quote meta. Writes only its own dir. NO hdlab/ write.
# KB_REFERENT: data/litbank/who_did_what_events.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from typing import Dict, List, Optional

import numpy as np

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments.exp_coref_focus_stack_oracle_ceiling_v1 import build_rich, is_antitypical, _gpos, _doc_meta  # noqa: E402
from experiments.exp_coref_residual_participant_pool_v1 import (  # noqa: E402
    _cluster_mentions, is_participant, _pick, FIRST_SECOND, PERSONAL)
from experiments.exp_coref_graded_cue_retrieval_litbank_v1 import load_streams, _supports  # noqa: E402

OUTDIR = os.path.join(REPO, "data", "exp_coref_participant_generalization_v1")
SEED = 20260830
NEUTER = set("it its they them their itself themselves".split())
FIRST_ONLY = set("i me my mine we us our ours myself ourselves".split())  # 1st-person (narrator marker)


def _doc_features(streams) -> Dict[str, Dict]:
    """Per-doc: narration-1st-person density (1st-person mentions in NON-quote sentences / n_sent), dialogue density
    (fraction of sentences that are inside a gold quote span)."""
    feats = {}
    for r in streams:
        doc = r["doc"]
        m = _doc_meta(doc)
        qs = m["quote_sents"]
        n_sent = max(m["n_sent"], 1)
        narr_1st = 0
        for mm in r["stream"]:
            if mm["head_text"].lower() in FIRST_ONLY and mm["sent"] not in qs:
                narr_1st += 1
        feats[doc] = {"narr_1st_density": narr_1st / n_sent,
                      "dialogue_density": len(qs) / n_sent,
                      "n_sent": n_sent}
    return feats


def _paired(a, b, n_boot, seed):
    docs = sorted(set(a) & set(b))
    if not docs:
        return {"delta": 0.0, "lo": 0.0, "hi": 0.0, "band": "EMPTY", "n_docs": 0}
    A = np.array([a[d] for d in docs], float)
    B = np.array([b[d] for d in docs], float)
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
            "band": "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEP"), "n_docs": n}


def _eval_split(insts_pop, cl, doc_ok):
    """Per-doc (correct,total) for floor vs participant, restricted to docs where doc_ok(doc)."""
    pd_floor = defaultdict(lambda: [0, 0])
    pd_part = defaultdict(lambda: [0, 0])
    rec = tot = 0
    for inst, sup, gi in insts_pop:
        doc = inst["doc"]
        if not doc_ok(doc):
            continue
        cids = inst["cand_ids"]
        ps, pst = inst["p_sent"], inst["p_start"]
        floor_keep = list(range(len(cids)))
        part_keep = [i for i in range(len(cids)) if not is_participant(cl, doc, cids[i], ps, pst)]
        if not part_keep:
            part_keep = floor_keep
        rec += int(gi in part_keep)
        tot += 1
        pd_floor[doc][0] += int(_pick(inst, floor_keep) == gi); pd_floor[doc][1] += 1
        pd_part[doc][0] += int(_pick(inst, part_keep) == gi); pd_part[doc][1] += 1
    return pd_floor, pd_part, (rec / tot if tot else 0.0), tot


def run(docs=None, n_boot=2000, seed=SEED) -> Dict:
    streams = load_streams(docs)
    insts = build_rich(streams)
    cl = _cluster_mentions(streams)
    feats = _doc_features(streams)

    pop = []
    for inst in insts:
        ids, sup, gi = _supports(inst)
        if is_antitypical(sup, gi):
            pop.append((inst, sup, gi))

    # thresholds: a doc is "1st-person narrated" if the narrator says I/we in narration at a non-trivial rate
    narr_vals = np.array([feats[d]["narr_1st_density"] for d in feats])
    dia_vals = np.array([feats[d]["dialogue_density"] for d in feats])
    narr_thresh = 0.15                      # >=0.15 1st-person narration mentions per sentence -> 1st-person narrator
    dia_med = float(np.median(dia_vals))

    def split_eval(name, doc_ok, seed_off):
        pf, pp, recall, n = _eval_split(pop, cl, doc_ok)
        con = _paired(dict(pp), dict(pf), n_boot, seed + seed_off)
        floor_acc = (sum(v[0] for v in pf.values()) / max(sum(v[1] for v in pf.values()), 1))
        part_acc = (sum(v[0] for v in pp.values()) / max(sum(v[1] for v in pp.values()), 1))
        return {"n": n, "floor_acc": round(floor_acc, 4), "participant_acc": round(part_acc, 4),
                "recall": round(recall, 4), "participant_minus_floor": con}

    splits = {
        "ALL": split_eval("ALL", lambda d: True, 1),
        "narration_1st_person": split_eval("1st", lambda d: feats[d]["narr_1st_density"] >= narr_thresh, 2),
        "narration_3rd_person": split_eval("3rd", lambda d: feats[d]["narr_1st_density"] < narr_thresh, 3),
        "dialogue_high": split_eval("dhi", lambda d: feats[d]["dialogue_density"] >= dia_med, 4),
        "dialogue_low": split_eval("dlo", lambda d: feats[d]["dialogue_density"] < dia_med, 5),
    }

    # pronoun-class split needs per-instance filtering, not per-doc
    def class_eval(name, keepcls, seed_off):
        sub = [(inst, sup, gi) for (inst, sup, gi) in pop if inst["pronoun"].lower() in keepcls]
        pf, pp, recall, n = _eval_split(sub, cl, lambda d: True)
        con = _paired(dict(pp), dict(pf), n_boot, seed + seed_off)
        fa = sum(v[0] for v in pf.values()) / max(sum(v[1] for v in pf.values()), 1)
        pa = sum(v[0] for v in pp.values()) / max(sum(v[1] for v in pp.values()), 1)
        return {"n": n, "floor_acc": round(fa, 4), "participant_acc": round(pa, 4), "recall": round(recall, 4),
                "participant_minus_floor": con}

    splits["pronoun_person"] = class_eval("person", PERSONAL, 6)
    splits["pronoun_neuter"] = class_eval("neuter", NEUTER, 7)

    # threshold robustness: the >=0.5 participant threshold is NOT a tuned knob -- every threshold beats the floor
    def thresh_eval(thr, seed_off):
        pf = defaultdict(lambda: [0, 0]); pp = defaultdict(lambda: [0, 0]); rec = tot = 0
        for inst, sup, gi in pop:
            doc = inst["doc"]; cids = inst["cand_ids"]; ps, pst = inst["p_sent"], inst["p_start"]
            keep = [i for i in range(len(cids)) if not is_participant(cl, doc, cids[i], ps, pst, thresh=thr)] or list(range(len(cids)))
            rec += int(gi in keep); tot += 1
            pf[doc][0] += int(_pick(inst, list(range(len(cids)))) == gi); pf[doc][1] += 1
            pp[doc][0] += int(_pick(inst, keep) == gi); pp[doc][1] += 1
        con = _paired(dict(pp), dict(pf), n_boot, seed + seed_off)
        return {"delta": con["delta"], "band": con["band"], "recall": round(rec / tot, 4)}
    threshold_sweep = {f"thr_{t}": thresh_eval(t, 20 + i) for i, t in enumerate((0.01, 0.3, 0.5, 0.7, 1.0))}
    all_thresholds_above = all(v["band"] == "ABOVE" for v in threshold_sweep.values())

    n_1st = sum(1 for d in feats if feats[d]["narr_1st_density"] >= narr_thresh)
    bands = {k: v["participant_minus_floor"]["band"] for k, v in splits.items()}
    generalizes = all(b != "BELOW" for b in bands.values())          # never HURTS anywhere
    helps_where_pollution = (splits["narration_1st_person"]["participant_minus_floor"]["band"] == "ABOVE"
                             or splits["dialogue_high"]["participant_minus_floor"]["band"] == "ABOVE")

    return {
        "anchor": "coref_participant_generalization_v1",
        "n_antitypical": len(pop),
        "n_docs_1st_person_narrated": n_1st, "n_docs_3rd_person_narrated": len(feats) - n_1st,
        "narr_thresh": narr_thresh, "dialogue_density_median": round(dia_med, 4),
        "splits": splits,
        "threshold_robustness": threshold_sweep,
        "reading": {
            "never_hurts_any_split (no BELOW)": generalizes,
            "helps_where_participant_pollution_exists": helps_where_pollution,
            "all_thresholds_beat_floor (not a tuned knob)": all_thresholds_above,
            "generalizes_as_a_principle": generalizes and helps_where_pollution and all_thresholds_above,
            "verdict": ("PARTICIPANT_LEVER_GENERALIZES_HELPS_WHERE_POLLUTION_NEUTRAL_ELSEWHERE"
                        if (generalizes and helps_where_pollution)
                        else "DOES_NOT_GENERALIZE_CLEANLY"),
        },
    }


def self_test():
    """Fixture: doc feature extraction distinguishes a 1st-person narrator from a 3rd-person one."""
    streams = [{"doc": "__1st", "stream": [
        {"sent": 0, "start": 0, "gold": 0, "role": "SUBJECT", "head_text": "I", "gov_verb": None, "obj_head": None},
        {"sent": 1, "start": 0, "gold": 0, "role": "SUBJECT", "head_text": "my", "gov_verb": None, "obj_head": None},
    ]}, {"doc": "__3rd", "stream": [
        {"sent": 0, "start": 0, "gold": 0, "role": "SUBJECT", "head_text": "John", "gov_verb": None, "obj_head": None},
        {"sent": 1, "start": 0, "gold": 0, "role": "SUBJECT", "head_text": "he", "gov_verb": None, "obj_head": None},
    ]}]
    from experiments.exp_coref_focus_stack_oracle_ceiling_v1 import _META
    _META["__1st"] = {"sents": [[]], "sent_lens": [5, 5], "cum": [0, 5, 10], "quote_sents": set(), "n_sent": 2}
    _META["__3rd"] = {"sents": [[]], "sent_lens": [5, 5], "cum": [0, 5, 10], "quote_sents": set(), "n_sent": 2}
    f = _doc_features(streams)
    assert f["__1st"]["narr_1st_density"] > 0.15, "1st-person narrator must have high narration-1st density"
    assert f["__3rd"]["narr_1st_density"] == 0.0, "3rd-person narrator must have zero narration-1st density"
    del _META["__1st"], _META["__3rd"]
    print("SELF-TEST PASS (1st-person narrator detected; 3rd-person narrator has zero narration-1st density)")


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
