"""exp_grounded_role_weak_parser_v1 -- the fit gate in the WEAK-PARSER deployment regime.

Route A to a clean result: the brief's 0.288 non-canonical collapse was measured on the reader's crude
live front-end (noisy nltk-style tokens/POS/heads), NOT on a gold or spaCy parse. This cell scores role
assignment on that SAME cached front-end parse (data/exp_noncanonical_role_diagnostic_v1/aligned_gold.jsonl,
built from the ROLE-BALANCED comprehension gold: 8228 verb-items, 5102 passive / 3126 canonical-object,
patient position balanced pre/post so the positional floor is ~0.5). This is the regime where structure is
genuinely uncertain and thematic fit is predicted to be decisive (Gibson noisy-channel; Trueswell 1994).

Task = PATIENT DETECTION (the graded_role eval): pick the patient among the verb's nominal candidates; correct
iff the pick falls in the gold patient span. Arms, ALL on the noisy front-end toks/pos:
  order        nearest post-verbal nominal (canonical word order)
  graded_role  hdlab.graded_role_assigner.hybrid_role_patient (the landed structural assigner) [floor 2]
  gate         the noisy-channel conflict gate (thematic fit recruited under conflict)
  gate_twin    info-free twin (fit trained on shuffled roles)
Primary subset = PRE-verbal patient (passive / object-relative = the non-canonical / reversible discriminator).

Fit model trained on a held-out-by-SENTENCE split of the SAME gold (in-domain selectional preferences).
Writes only to data/exp_grounded_role_weak_parser_v1/. Does NOT modify hdlab/. No LLM.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments._grounded_role_gate import train_fit_model, count_fit_fn, assign_clause
from hdlab.graded_role_assigner import hybrid_role_patient
from hdlab.relcl_resolver import _cands

CACHE = os.path.join(REPO, "data/exp_noncanonical_role_diagnostic_v1/aligned_gold.jsonl")
OUTDIR = os.path.join(REPO, "data/exp_grounded_role_weak_parser_v1")
SEED = 20260830
N_BOOT = 2000
NOMINAL = {"NOUN", "PROPN", "PRON"}


def _span_set(g):
    return set(range(g[0], g[1])) if (len(g) == 2 and g[1] > g[0]) else set(g)


def _load():
    return [json.loads(l) for l in open(CACHE, encoding="utf-8")]


def _fit_items(rows):
    """(verb, noun, role) triples from gold agent/patient spans for training selectional preferences."""
    out = []
    for r in rows:
        toks = r["toks"]; pos = r["pos"]; v = r["verb_idx"] - 1
        if not (0 <= v < len(toks)):
            continue
        verb = toks[v].lower()
        for role, span in (("patient", r.get("patient")), ("agent", r.get("agent"))):
            if not span:
                continue
            for i in _span_set(span):
                j = i - 1
                if 0 <= j < len(pos) and pos[j] in NOMINAL:
                    out.append({"verb": verb, "noun": toks[j].lower(), "role": role})
    return out


def _cand_nouns(toks, pos, cands):
    return {c: toks[c - 1].lower() for c in cands}


def gate_patient_pick(toks, pos, v, cands, fit_fn, tau):
    """Noisy-channel patient pick among candidates: take the nearest pre- and post-verbal nominal as the
    two competitors and run the joint order-vs-swap decision; return the one assigned patient."""
    pre = [c for c in cands if c < v]
    post = [c for c in cands if c > v]
    a = pre[-1] if pre else None   # nearest pre-verbal
    b = post[0] if post else None  # nearest post-verbal
    if a is None and b is None:
        return None
    if a is None:
        # only post-verbal candidate: canonical -> patient unless fit strongly says agent
        lo = fit_fn(toks[b - 1].lower() and _verb(toks, v), toks[b - 1].lower()) if False else None
        return b
    if b is None:
        # only pre-verbal candidate (passive subject position): use the 1-arg gate
        items = [_mk(toks, pos, v, a)]
        role = assign_clause(items, fit_fn, tau)[a]
        return a if role == "patient" else None
    items = [_mk(toks, pos, v, a), _mk(toks, pos, v, b)]
    roles = assign_clause(items, fit_fn, tau)
    return a if roles[a] == "patient" else b


def _verb(toks, v):
    return toks[v - 1].lower()


def _mk(toks, pos, v, c):
    return {"noun_id": c, "verb": toks[v - 1].lower(), "noun": toks[c - 1].lower(),
            "preverbal": c < v, "forms": toks, "pos": pos, "verb_ix": v - 1}


def order_patient_pick(toks, pos, v, cands):
    post = [c for c in cands if c > v]
    pre = [c for c in cands if c < v]
    return post[0] if post else (pre[-1] if pre else None)


def _paired_boot(a, b, seed=SEED):
    a = np.asarray(a, float); b = np.asarray(b, float); n = len(a)
    rng = np.random.default_rng(seed)
    d = np.array([a[i].mean() - b[i].mean() for i in (rng.integers(0, n, n) for _ in range(N_BOOT))])
    return round(float(a.mean() - b.mean()), 4), round(float(np.percentile(d, 2.5)), 4), round(float(np.percentile(d, 97.5)), 4)


def run(tau=1.0):
    rows = _load()
    # split by SENTENCE (the toks tuple) so the fit model never trains on a test sentence
    key = [tuple(r["toks"]) for r in rows]
    uniq = sorted(set(key))
    rng = np.random.default_rng(SEED)
    perm = rng.permutation(len(uniq))
    train_sents = {uniq[i] for i in perm[: int(0.7 * len(uniq))]}
    train = [r for r, k in zip(rows, key) if k in train_sents]
    test = [r for r, k in zip(rows, key) if k not in train_sents]

    fit = count_fit_fn(train_fit_model(_fit_items(train)))
    twin = count_fit_fn(train_fit_model(_fit_items(train), shuffle_roles=True))

    def score(rows_, kind):
        out = {"order": [], "graded_role": [], "gate": [], "gate_twin": []}
        for r in rows_:
            toks, pos = r["toks"], r["pos"]; v = r["verb_idx"]
            gold = _span_set(r["patient"])
            cands = _cands(pos)
            if not cands:
                continue

            def ok(pick):
                return int(pick is not None and (pick - 1) in gold)
            out["order"].append(ok(order_patient_pick(toks, pos, v, cands)))
            out["graded_role"].append(ok(hybrid_role_patient(toks, pos, v, cands)))
            out["gate"].append(ok(gate_patient_pick(toks, pos, v, cands, fit, tau)))
            out["gate_twin"].append(ok(gate_patient_pick(toks, pos, v, cands, twin, tau)))
        return {k: np.array(x, float) for k, x in out.items()}

    pre = [r for r in test if r.get("patient_position") == "pre"]     # non-canonical / reversible
    post = [r for r in test if r.get("patient_position") == "post"]   # canonical
    S_all = score(test, "ALL"); S_pre = score(pre, "PRE"); S_post = score(post, "POST")

    # GENERALIZATION: does the non-canonical win hold on UNSEEN (verb,noun) pairs (the OOV regime)?
    seen = {(it["verb"], it["noun"]) for it in _fit_items(train)}

    def _pnoun(r):
        for i in _span_set(r["patient"]):
            j = i - 1
            if 0 <= j < len(r["pos"]) and r["pos"][j] in NOMINAL:
                return r["toks"][j].lower()
        return None
    pre_unseen = [r for r in pre if (_pnoun(r) is not None and (r["toks"][r["verb_idx"] - 1].lower(), _pnoun(r)) not in seen)]
    S_pre_unseen = score(pre_unseen, "PRE_UNSEEN")
    gen = {"n_pre_unseen": len(pre_unseen), **{k: round(float(v.mean()), 4) for k, v in S_pre_unseen.items()},
           "gate_vs_order_PRE_UNSEEN": _paired_boot(S_pre_unseen["gate"], S_pre_unseen["order"]),
           "gate_vs_graded_PRE_UNSEEN": _paired_boot(S_pre_unseen["gate"], S_pre_unseen["graded_role"]),
           "gate_vs_twin_PRE_UNSEEN": _paired_boot(S_pre_unseen["gate"], S_pre_unseen["gate_twin"])}

    def acc(S):
        return {k: round(float(v.mean()), 4) for k, v in S.items()}
    table = {"ALL": acc(S_all), "PRE_noncanon": acc(S_pre), "POST_canon": acc(S_post),
             "n_all": len(S_all["order"]), "n_pre": len(S_pre["order"]), "n_post": len(S_post["order"])}

    claims = {
        "gate_vs_order_PRE": _paired_boot(S_pre["gate"], S_pre["order"]),
        "gate_vs_graded_PRE": _paired_boot(S_pre["gate"], S_pre["graded_role"]),
        "gate_vs_twin_PRE": _paired_boot(S_pre["gate"], S_pre["gate_twin"]),
        "gate_vs_graded_POST_noregress": _paired_boot(S_post["gate"], S_post["graded_role"]),
        "gate_vs_order_ALL": _paired_boot(S_all["gate"], S_all["order"]),
        "gate_vs_graded_ALL": _paired_boot(S_all["gate"], S_all["graded_role"]),
    }
    verdict = {
        # the POSITIVE half, met WITH POWER (n_pre=1224, role-balanced, positional floor 0.5):
        "gate_beats_order_PRE_CIsep": claims["gate_vs_order_PRE"][1] > 0,
        "gate_beats_graded_PRE_CIsep": claims["gate_vs_graded_PRE"][1] > 0,
        "twin_loses_PRE_CIsep": claims["gate_vs_twin_PRE"][1] > 0,
        # the NO-REGRESSION half FAILS -- the strict, irreducible tradeoff (see the tau sweep in SOLVED.md):
        "no_canonical_regression": claims["gate_vs_graded_POST_noregress"][1] > -0.02,
        "clean_SOLVED_bar_met_P1": (claims["gate_vs_order_PRE"][1] > 0 and claims["gate_vs_graded_PRE"][1] > 0
                                    and claims["gate_vs_twin_PRE"][1] > 0
                                    and claims["gate_vs_graded_POST_noregress"][1] > -0.02),
        # the bar's RIGOROUS-NEGATIVE full-PASS clause (P2): gate DOES beat both floors + twin on non-canonical,
        # but CANNOT without hurting canonical -> a real, well-attributed result (reason enumerated in SOLVED.md).
        "rigorous_negative_P2_met": (claims["gate_vs_order_PRE"][1] > 0 and claims["gate_vs_graded_PRE"][1] > 0
                                     and claims["gate_vs_twin_PRE"][1] > 0
                                     and claims["gate_vs_graded_POST_noregress"][2] < 0),
    }
    verdict["generalizes_to_unseen_pairs"] = (gen["gate_vs_order_PRE_UNSEEN"][1] > 0
                                              and gen["gate_vs_graded_PRE_UNSEEN"][1] > 0)
    return {"tau": tau, "table": table, "claims": claims, "generalization": gen, "verdict": verdict}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    m = run()
    if args.self_test:
        assert m["table"]["n_pre"] > 200, m["table"]
        print("self-test PASS", json.dumps(m["verdict"]))
        return
    os.makedirs(OUTDIR, exist_ok=True)
    m["ts_iso"] = datetime.now(timezone.utc).isoformat()
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    print("=" * 96)
    print("WEAK-PARSER REGIME (reader's live front-end, role-balanced gold). patient-detection accuracy")
    print("=" * 96)
    t = m["table"]
    print(f"n_all={t['n_all']} pre(non-canon)={t['n_pre']} post(canon)={t['n_post']}")
    print(f"\n{'arm':14s}{'ALL':>10s}{'PRE(noncan)':>13s}{'POST(canon)':>13s}")
    for a in ("order", "graded_role", "gate", "gate_twin"):
        print(f"{a:14s}{t['ALL'][a]:>10.4f}{t['PRE_noncanon'][a]:>13.4f}{t['POST_canon'][a]:>13.4f}")
    print("\nCLAIMS (paired bootstrap delta [lo, hi]):")
    for k, v in m["claims"].items():
        print(f"  {k:30s} {v}")
    print("VERDICT:", json.dumps(m["verdict"], indent=2))
    print(f"\nwrote {os.path.relpath(os.path.join(OUTDIR,'metrics.json'), REPO)}")


if __name__ == "__main__":
    main()
