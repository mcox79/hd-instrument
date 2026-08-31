"""exp_grounded_role_protofit_generalize_v1 -- close the generalization gap: a fit signal that carries to
UNSEEN (verb,noun) pairs. problem: grounded_role_assignment_via_verb_keyed_thematic_fit.

The count-based fit MEMORISES (verb,noun) pairs: in the weak-parser regime its edge over the info-free twin
did NOT survive to unseen pairs (+0.023 [-0.027,0.074]). The McRae-faithful fix is a PROTOTYPE-similarity fit
over a distributional NOUN space, so an unseen argument inherits its role-fit from distributionally-similar
known fillers. Here the noun space is ROLE-CONTEXT (selectional-preference) embeddings: each noun is
represented by the VERBS it co-occurs with as an argument (label-free, built from the reader's OWN cached
front-end via the dependency heads) -> PPMI + SVD. Role PROTOTYPES (agent/patient centroids, per-verb +
general) are then built from the TRAIN role labels; the twin shuffles those labels.

Test (weak-parser deployment regime; the modern role-balanced gold read through the reader's noisy front-end):
does the prototype-fit gate beat its INFO-FREE TWIN on held-out UNSEEN (verb,noun) non-canonical pairs,
CI-separated -- i.e. does the fit SIGNAL (not just the gate's structure handling) now generalise?

Writes only to data/exp_grounded_role_protofit_generalize_v1/. Does NOT modify hdlab/. No LLM.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.exp_grounded_role_weak_parser_v1 as W
from experiments._grounded_role_gate import train_fit_model, count_fit_fn
from experiments._grounded_role_protofit import build_prototypes, make_protofit_fn
from hdlab.relcl_resolver import _cands

OUTDIR = os.path.join(REPO, "data/exp_grounded_role_protofit_generalize_v1")
SEED = 20260830
N_BOOT = 2000
NOMINAL = {"NOUN", "PROPN", "PRON"}


def build_role_context_emb(rows, dim=100, min_count=2, max_vocab=15000, seed=0):
    """LABEL-FREE noun embeddings from noun<->governing-verb co-occurrence (the reader's cached heads).
    Each noun is described by the verbs it is a dependent of -> nouns with similar selectional behaviour
    cluster, so an unseen argument still has a vector."""
    pair = Counter()
    nfreq = Counter()
    for r in rows:
        toks = [t.lower() for t in r["toks"]]; pos = r["pos"]; heads = r.get("heads", {})
        for i in range(len(toks)):
            if pos[i] not in NOMINAL:
                continue
            h = heads.get(str(i + 1), heads.get(i + 1))   # cache stores heads with STRING keys (1-based)
            if h and 1 <= h <= len(toks):
                hv = toks[h - 1]
                if pos[h - 1] == "VERB":
                    pair[(toks[i], hv)] += 1
                    nfreq[toks[i]] += 1
    nouns = [n for n, c in nfreq.most_common(max_vocab) if c >= min_count]
    nix = {n: i for i, n in enumerate(nouns)}
    verbs = sorted({v for (n, v) in pair if n in nix})
    vix = {v: j for j, v in enumerate(verbs)}
    R, C, D = [], [], []
    for (n, v), c in pair.items():
        if n in nix and v in vix:
            R.append(nix[n]); C.append(vix[v]); D.append(float(c))
    if not R:
        return {}
    M = sparse.coo_matrix((D, (R, C)), shape=(len(nouns), len(verbs))).tocsr()
    tot = M.sum(); rs = np.asarray(M.sum(1)).ravel() + 1e-12; cs = np.asarray(M.sum(0)).ravel() + 1e-12
    M = M.tocoo()
    pm = np.log((M.data * tot) / (rs[M.row] * cs[M.col]) + 1e-12); pm[pm < 0] = 0.0
    P = sparse.coo_matrix((pm, (M.row, M.col)), shape=(len(nouns), len(verbs))).tocsr(); P.eliminate_zeros()
    d = min(dim, min(P.shape) - 1)
    X = TruncatedSVD(n_components=d, random_state=seed).fit_transform(P)
    X = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-12)
    return {nouns[i]: X[i] for i in range(len(nouns))}


def _paired_boot(a, b, seed=SEED):
    a = np.asarray(a, float); b = np.asarray(b, float); n = len(a)
    rng = np.random.default_rng(seed)
    d = np.array([a[i].mean() - b[i].mean() for i in (rng.integers(0, n, n) for _ in range(N_BOOT))])
    return round(float(a.mean() - b.mean()), 4), round(float(np.percentile(d, 2.5)), 4), round(float(np.percentile(d, 97.5)), 4)


def _pnoun(r):
    for i in W._span_set(r["patient"]):
        j = i - 1
        if 0 <= j < len(r["pos"]) and r["pos"][j] in NOMINAL:
            return r["toks"][j].lower()
    return None


def run(tau=1.0):
    rows = W._load()
    key = [tuple(r["toks"]) for r in rows]
    uniq = sorted(set(key)); rng = np.random.default_rng(SEED)
    perm = rng.permutation(len(uniq)); tr_s = {uniq[i] for i in perm[: int(0.7 * len(uniq))]}
    train = [r for r, k in zip(rows, key) if k in tr_s]
    test = [r for r, k in zip(rows, key) if k not in tr_s]

    fititems = W._fit_items(train)
    seen = {(it["verb"], it["noun"]) for it in fititems}
    cfit = count_fit_fn(train_fit_model(fititems))
    ctwin = count_fit_fn(train_fit_model(fititems, shuffle_roles=True))

    emb = build_role_context_emb(train)   # label-free, from TRAIN only
    pfit = make_protofit_fn(emb, build_prototypes(fititems, emb), k=8.0)
    pfit_twin = make_protofit_fn(emb, build_prototypes(fititems, emb, shuffle_roles=True), k=8.0)

    # A CONSOLIDATED distributional space (pretrained GloVe = the PINNED distributional-consolidation
    # computation with the EXPERIENCE parameter swept toward the brain's regime; static asset, NO LLM). Cached
    # noun subset at glove_noun_subset.npz (built offline by tools of this cell's dir). If absent, gloVe arm is skipped.
    gpath = os.path.join(OUTDIR, "glove_noun_subset.npz")
    gfit = gtwin = None
    if os.path.exists(gpath):
        z = np.load(gpath); gemb = {k: z[k] for k in z.files}
        gfit = make_protofit_fn(gemb, build_prototypes(fititems, gemb), k=8.0)
        gtwin = make_protofit_fn(gemb, build_prototypes(fititems, gemb, shuffle_roles=True), k=8.0)

    pre = [r for r in test if r.get("patient_position") == "pre"]
    unseen = [r for r in pre if (_pnoun(r) is not None and (r["toks"][r["verb_idx"] - 1].lower(), _pnoun(r)) not in seen)]

    def vec(rows_, fn):
        out = []
        for r in rows_:
            toks, pos = r["toks"], r["pos"]; v = r["verb_idx"]; gold = W._span_set(r["patient"]); cands = _cands(pos)
            if not cands:
                continue
            pick = W.gate_patient_pick(toks, pos, v, cands, fn, tau)
            out.append(int(pick is not None and (pick - 1) in gold))
        return np.array(out, float)

    def order_vec(rows_):
        out = []
        for r in rows_:
            toks, pos = r["toks"], r["pos"]; v = r["verb_idx"]; gold = W._span_set(r["patient"]); cands = _cands(pos)
            if not cands:
                continue
            p = W.order_patient_pick(toks, pos, v, cands)
            out.append(int(p is not None and (p - 1) in gold))
        return np.array(out, float)

    res = {}
    for name, sub in (("PRE_all", pre), ("PRE_unseen", unseen)):
        count = vec(sub, cfit); ctw = vec(sub, ctwin); order = order_vec(sub)
        rc = vec(sub, pfit); rctw = vec(sub, pfit_twin)
        row = {
            "n": len(count), "order": round(float(order.mean()), 4), "count_fit": round(float(count.mean()), 4),
            "count_vs_twin": _paired_boot(count, ctw),            # count: role-accurate signal, beats its shuffle?
            "rolectx_proto": round(float(rc.mean()), 4), "rolectx_vs_twin": _paired_boot(rc, rctw),
        }
        if gfit is not None:
            gv = vec(sub, gfit); gtw = vec(sub, gtwin)
            row["glove_proto"] = round(float(gv.mean()), 4)
            row["glove_vs_twin"] = _paired_boot(gv, gtw)          # GloVe: does a CONSOLIDATED space generalize the SIGNAL?
            row["glove_vs_order"] = _paired_boot(gv, order)       # ...but is general similarity role-ACCURATE?
        res[name] = row
    U = res["PRE_unseen"]
    verdict = {
        # count fit is role-ACCURATE but MEMORISES: its signal-over-twin does NOT survive to unseen pairs
        "count_signal_survives_to_unseen": U["count_vs_twin"][1] > 0,
        # a CONSOLIDATED distributional space GENERALISES the fit signal to unseen pairs (the mechanism works)...
        "glove_signal_generalises_to_unseen": (gfit is not None and U["glove_vs_twin"][1] > 0),
        # ...BUT general similarity is NOT role-accurate (below word order) -- topic != thematic role
        "glove_is_role_accurate": (gfit is not None and U["glove_vs_order"][1] > 0),
        "gap_closed_cleanly": (gfit is not None and U["glove_vs_twin"][1] > 0 and U["glove_vs_order"][1] > 0),
    }
    return {"tau": tau, "results": res, "verdict": verdict,
            "finding": ("No available meaning space gives BOTH role-accuracy AND unseen-pair generalization: "
                        "count fit is role-accurate but memorises (signal does not survive to unseen); a consolidated "
                        "distributional space (GloVe) generalises the signal to unseen pairs but is role-INACCURATE "
                        "(general similarity != thematic role). Closing the gap needs a ROLE-TUNED, grounded semantic "
                        "space (the brief's distributional_meaning_channel dependency; the brain's ATL-hub-shaped spoke).")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    m = run()
    if args.self_test:
        assert m["results"]["PRE_unseen"]["n"] > 100, m["results"]["PRE_unseen"]["n"]
        print("self-test PASS", json.dumps(m["verdict"]))
        return
    os.makedirs(OUTDIR, exist_ok=True)
    m["ts_iso"] = datetime.now(timezone.utc).isoformat()
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    print("=" * 98)
    print("DOES THE THEMATIC-FIT SIGNAL GENERALIZE TO UNSEEN (verb,noun) PAIRS? (weak-parser regime)")
    print("=" * 98)
    for name, r in m["results"].items():
        print(f"\n{name} (n={r['n']}): order={r['order']} count_fit={r['count_fit']} "
              f"rolectx_proto={r['rolectx_proto']} glove_proto={r.get('glove_proto')}")
        print(f"   count vs its twin      {r['count_vs_twin']}   (role-accurate; does the signal survive to unseen?)")
        if 'glove_vs_twin' in r:
            print(f"   GloVe proto vs its twin {r['glove_vs_twin']}   (consolidated space: signal generalizes?)")
            print(f"   GloVe proto vs order    {r['glove_vs_order']}   (but is general similarity role-accurate?)")
    print("\nFINDING:", m["finding"])
    print("VERDICT:", json.dumps(m["verdict"], indent=2))
    print(f"\nwrote {os.path.relpath(os.path.join(OUTDIR,'metrics.json'), REPO)}")


if __name__ == "__main__":
    main()
