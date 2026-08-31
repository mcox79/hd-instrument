"""exp_grounded_role_noisy_parse_v1 -- the fit gate in the NATURAL uncertainty regime (a REAL parser).

The gold-parse result is a regime artifact: a gold parse's dependency labels encode the roles already, so
thematic fit is redundant (Gibson noisy-channel: zero noise -> literal parse). The corruption curve confirmed
fit's value rises as structure degrades. This cell is the NATURAL version: it parses the raw clause text with
a REAL dependency parser (spaCy en_core_web_sm -- substrate-native, no LLM) whose structural role assignment
ERRS on hard constructions, and asks whether grounded thematic fit RECOVERS the roles the parser gets wrong.

Setup (no gold leakage into the prediction):
  * GOLD role labels come from the UD gold parse (the ground truth), transferred to spaCy items by
    sentence-local (verb-lemma, noun-lemma) match.
  * PREDICTORS read ONLY spaCy's parse: word order (token position), spaCy's structural role (nsubj->agent,
    obj/nsubjpass->patient) == the realistic "current grammatical-function assigner" floor, and the fit gate
    (thematic fit + spaCy-derived markedness).
Key subset: PARSE-ERROR items -- where spaCy's structural role is WRONG vs gold. That is the natural
uncertainty regime; if fit is a disambiguation-under-uncertainty mechanism it should help THERE.

Writes only to data/exp_grounded_role_noisy_parse_v1/. Does NOT modify hdlab/.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments.exp_mcguffey_migrate_build_modern_gold_v1 import parse_conllu, UD_TRAIN, UD_TEST
from experiments._grounded_role_data import load_items, split_by_sentence
from experiments._grounded_role_gate import (train_fit_model, count_fit_fn, make_noisy_channel_labeler,
                                             order_label)

OUTDIR = os.path.join(REPO, "data/exp_grounded_role_noisy_parse_v1")
SEED = 20260830
N_BOOT = 2000
SUBJ = {"nsubj", "nsubjpass"}
OBJP = {"dobj", "obj", "nsubjpass"}   # patient-ish spaCy deps (nsubjpass = passive subject = patient)
NOMINAL = {"NOUN", "PROPN", "PRON"}


def _sent_text_map(paths):
    """sent_uid -> raw text, matching _grounded_role_data's uid scheme."""
    m = {}
    for pth in paths:
        for di, doc in enumerate(parse_conllu(pth)):
            for si, sent in enumerate(doc):
                m[f"{os.path.basename(pth)}::{di}::{si}"] = sent["text"]
    return m


def _spacy_items(doc, gold_roles, gold_canon, sent_uid):
    """Extract spaCy core-arg items and transfer gold role/canon by (verb,noun) lemma match."""
    forms = [t.text for t in doc]
    pos = [t.pos_ for t in doc]
    out = []
    for v in doc:
        if v.pos_ != "VERB":
            continue
        args = [c for c in v.children if c.dep_ in (SUBJ | OBJP) and c.pos_ in NOMINAL]
        if not args:
            continue
        cand_ids = [c.i + 1 for c in args]
        for c in args:
            key = (v.lemma_.lower(), c.lemma_.lower())
            if key not in gold_roles:
                continue
            spacy_role = "patient" if c.dep_ in OBJP else "agent"
            out.append({
                "sent_uid": sent_uid, "verb": v.lemma_.lower(), "verb_id": v.i + 1, "verb_ix": v.i,
                "noun": c.lemma_.lower(), "noun_id": c.i + 1, "noun_ix": c.i, "upos": c.pos_,
                "role": gold_roles[key], "canon_type": gold_canon.get(key, "canonical"),
                "preverbal": c.i < v.i, "forms": forms, "pos": pos, "cand_ids": cand_ids,
                "spacy_role": spacy_role, "n_args": len(args),
            })
    return out


def _paired_boot(a, b, seed=SEED):
    a = np.asarray(a, float); b = np.asarray(b, float); n = len(a)
    rng = np.random.default_rng(seed)
    d = np.array([a[i].mean() - b[i].mean() for i in (rng.integers(0, n, n) for _ in range(N_BOOT))])
    return round(float(a.mean() - b.mean()), 4), round(float(np.percentile(d, 2.5)), 4), round(float(np.percentile(d, 97.5)), 4)


def _bal(items, fn):
    rec = {"agent": [0, 0], "patient": [0, 0]}
    for it in items:
        ok = int(fn(it) == it["role"]); rec[it["role"]][0] += ok; rec[it["role"]][1] += 1
    parts = [rec[r][0] / rec[r][1] for r in rec if rec[r][1]]
    return round(sum(parts) / len(parts), 4) if parts else None


def run(tau=1.0, limit=None):
    import spacy
    nlp = spacy.load("en_core_web_sm", disable=["ner", "lemmatizer"])
    # keep default lemmatizer (needed for lemma match) -> re-enable
    nlp = spacy.load("en_core_web_sm", disable=["ner"])

    items = load_items()
    train, test = split_by_sentence(items)
    fit = count_fit_fn(train_fit_model(train))
    twin = count_fit_fn(train_fit_model(train, shuffle_roles=True))

    # gold role/canon maps per test sentence
    gr = defaultdict(dict); gc = defaultdict(dict)
    test_uids = set()
    for it in test:
        test_uids.add(it["sent_uid"])
        gr[it["sent_uid"]][(it["verb"], it["noun"])] = it["role"]
        gc[it["sent_uid"]][(it["verb"], it["noun"])] = it["canon_type"]
    text_map = _sent_text_map((UD_TRAIN, UD_TEST))

    uids = sorted(test_uids)
    if limit:
        uids = uids[:limit]
    sp_items = []
    for uid in uids:
        txt = text_map.get(uid, "")
        if not txt:
            continue
        sp_items.extend(_spacy_items(nlp(txt), gr[uid], gc[uid], uid))

    gate = make_noisy_channel_labeler(sp_items, fit, tau=tau)
    gate_tw = make_noisy_channel_labeler(sp_items, twin, tau=tau)
    arms = {
        "word_order": order_label,
        "spacy_struct": lambda it: it["spacy_role"],   # realistic structural floor (the parser's own roles)
        "fit_gate": gate,
        "fit_gate_twin": gate_tw,
    }
    nc = [it for it in sp_items if it["canon_type"] in ("passive", "inversion", "fronting")]
    canon = [it for it in sp_items if it["canon_type"] == "canonical"]
    # PARSE-ERROR subset: spaCy's own structural role is wrong -> the natural uncertainty regime
    err = [it for it in sp_items if it["spacy_role"] != it["role"]]

    def acc(pop, fn):
        return round(float(np.mean([fn(it) == it["role"] for it in pop])), 4) if pop else None
    table = {name: {"ALL": acc(sp_items, fn), "canonical": acc(canon, fn), "NONCANON_raw": acc(nc, fn),
                    "NONCANON_bal": _bal(nc, fn), "parse_error": acc(err, fn)} for name, fn in arms.items()}

    def cv(pop, fn):
        return np.array([int(fn(it) == it["role"]) for it in pop], float)
    claims = {
        # on the parse-error subset, does fit recover what the parser got wrong?
        "gate_vs_spacy_parseerr": _paired_boot(cv(err, gate), cv(err, arms["spacy_struct"])),
        "gate_vs_order_parseerr": _paired_boot(cv(err, gate), cv(err, order_label)),
        "gate_vs_twin_parseerr": _paired_boot(cv(err, gate), cv(err, gate_tw)),
        # aggregate: does the fit gate beat the realistic structural floor + word order?
        "gate_vs_spacy_ALL": _paired_boot(cv(sp_items, gate), cv(sp_items, arms["spacy_struct"])),
        "gate_vs_order_ALL": _paired_boot(cv(sp_items, gate), cv(sp_items, order_label)),
    }
    verdict = {
        "n_items": len(sp_items), "n_noncanon": len(nc), "n_parse_error": len(err),
        "spacy_parse_error_rate": round(len(err) / max(1, len(sp_items)), 4),
        "fit_recovers_parse_errors_over_structure": claims["gate_vs_spacy_parseerr"][1] > 0,
        "fit_beats_order_on_parse_errors": claims["gate_vs_order_parseerr"][1] > 0,
        "twin_loses_on_parse_errors": claims["gate_vs_twin_parseerr"][0] > 0,
        "fit_beats_structure_aggregate": claims["gate_vs_spacy_ALL"][1] > 0,
    }
    return {"tau": tau, "table": table, "claims": claims, "verdict": verdict}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    m = run(limit=(200 if args.self_test else args.limit))
    if args.self_test:
        assert m["verdict"]["n_items"] > 100, m["verdict"]
        print("self-test PASS", json.dumps({k: m["verdict"][k] for k in ("n_items", "n_parse_error")}))
        return
    os.makedirs(OUTDIR, exist_ok=True)
    m["ts_iso"] = datetime.now(timezone.utc).isoformat()
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    print("=" * 96)
    print("NOISY-PARSE REGIME (spaCy real parser; gold roles transferred by lemma). No LLM.")
    print("=" * 96)
    v = m["verdict"]
    print(f"n_items={v['n_items']} noncanon={v['n_noncanon']} parse_errors={v['n_parse_error']} "
          f"(spaCy structural error rate {v['spacy_parse_error_rate']})")
    cols = ["ALL", "canonical", "NONCANON_raw", "NONCANON_bal", "parse_error"]
    print(f"\n{'arm':16s}" + "".join(f"{c[:12]:>13s}" for c in cols))
    for name, r in m["table"].items():
        print(f"{name:16s}" + "".join(f"{str(r[c]):>13s}" for c in cols))
    print("\nCLAIMS (paired bootstrap delta [lo, hi]):")
    for k, val in m["claims"].items():
        print(f"  {k:28s} {val}")
    print("VERDICT:", json.dumps(m["verdict"], indent=2))
    print(f"\nwrote {os.path.relpath(os.path.join(OUTDIR,'metrics.json'), REPO)}")


if __name__ == "__main__":
    main()
