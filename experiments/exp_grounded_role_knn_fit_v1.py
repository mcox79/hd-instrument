"""exp_grounded_role_knn_fit_v1 -- close the fit-generalization gap the brain-faithful way: THEMATIC FIT AS
SIMILARITY TO KNOWN ROLE-FILLERS (McRae, Ferretti & Amyote 1997). problem: grounded_role_assignment_via_verb_keyed_thematic_fit.

The count fit is role-ACCURATE but MEMORISES (its signal does not survive to unseen pairs); a consolidated
distributional space (GloVe) GENERALISES but general similarity is not thematic-role fit (it is topic). The
brain does neither alone: thematic fit is the FEATURE-SIMILARITY of the argument to the verb's typical
role-fillers -- a NOVEL noun inherits the role tendency of the KNOWN fillers it is most similar to. This cell
implements exactly that: for a noun with no role counts, its role log-odds = the (similarity-weighted) mean
role log-odds of its k nearest neighbours -- in GloVe space -- AMONG nouns that DO have role counts. So the
role grounding comes from experience (counts) and the GENERALISATION comes from distributional similarity.

TEST (weak-parser deployment regime; modern role-balanced gold, reader's noisy front-end). The decisive
generalisation split is by whether the PATIENT NOUN is OOV to the count model (never seen as any argument in
train). On OOV nouns the count fit has NOTHING; if k-NN role transfer beats word order AND its info-free twin
there, CI-separated, the fit signal GENERALISES to genuinely novel arguments the brain-faithful way.

GloVe (static asset, no LLM) = the PINNED distributional consolidation, experience-swept; the k-NN transfer is
the McRae feature-similarity read-out. Writes only to data/exp_grounded_role_knn_fit_v1/. NO hdlab writes.
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

import experiments.exp_grounded_role_weak_parser_v1 as W
from experiments._grounded_role_gate import train_fit_model
from experiments._grounded_role_gate import fit_logodds as _flo
from experiments.exp_grounded_role_protofit_generalize_v1 import _pnoun, _paired_boot
from hdlab.relcl_resolver import _cands
from hdlab.graded_role_assigner import hybrid_role_patient

OUTDIR = os.path.join(REPO, "data/exp_grounded_role_knn_fit_v1")
GLOVE = os.path.join(REPO, "data/exp_grounded_role_protofit_generalize_v1/glove_noun_subset.npz")
SEED = 20260830
MIN_COUNT = 3   # a noun with >= this many role observations uses its own counts; else k-NN transfer
K = 10


def _global_lo(model, noun):
    na, npt = model["nn"].get(noun, [0, 0])
    return float(np.log((na + 0.5) / (npt + 0.5)))


def make_knn_fit(model, gemb, k=K, min_count=MIN_COUNT, shuffle=False, seed=SEED):
    """fit_fn(verb, noun) -> role log-odds. Attested noun -> verb-keyed count fit (McRae: known filler).
    Novel noun -> similarity-weighted mean role log-odds of its k GloVe-nearest ATTESTED nouns."""
    known = [n for n, c in model["nn"].items() if sum(c) >= min_count and n in gemb]
    G = np.stack([gemb[n] for n in known]) if known else np.zeros((0, 1))
    lo = np.array([_global_lo(model, n) for n in known], float)
    if shuffle:
        lo = np.random.default_rng(seed).permutation(lo)

    def f(verb, noun):
        na, npt = model["nn"].get(noun, [0, 0])
        if na + npt >= min_count:
            return _flo(model, verb, noun)                 # attested: use experience directly
        v = gemb.get(noun)
        if v is None or G.shape[0] == 0:
            return 0.0
        sims = G @ v                                        # cosine (both L2-normalised)
        idx = np.argpartition(-sims, min(k, len(sims) - 1))[:k]
        w = np.clip(sims[idx], 0, None)
        if w.sum() <= 0:
            return float(lo[idx].mean())
        return float((w * lo[idx]).sum() / w.sum())        # similarity-weighted role tendency of neighbours
    return f


def _split(rows):
    key = [tuple(r["toks"]) for r in rows]
    uniq = sorted(set(key)); rng = np.random.default_rng(SEED)
    perm = rng.permutation(len(uniq)); tr = {uniq[i] for i in perm[: int(0.7 * len(uniq))]}
    return ([r for r, k in zip(rows, key) if k in tr], [r for r, k in zip(rows, key) if k not in tr])


def _vec(rows_, fn):
    o = []
    for r in rows_:
        toks, pos = r["toks"], r["pos"]; v = r["verb_idx"]; g = W._span_set(r["patient"]); c = _cands(pos)
        if not c:
            continue
        p = W.gate_patient_pick(toks, pos, v, c, fn, 1.0) if callable(fn) else (
            W.order_patient_pick(toks, pos, v, c) if fn == "order" else hybrid_role_patient(toks, pos, v, c))
        o.append(int(p is not None and (p - 1) in g))
    return np.array(o, float)


def run():
    z = np.load(GLOVE); gemb = {kk: z[kk] for kk in z.files}
    rows = W._load(); train, test = _split(rows)
    fititems = W._fit_items(train)
    model = train_fit_model(fititems)
    attested = {n for n, c in model["nn"].items() if sum(c) >= MIN_COUNT}

    knn = make_knn_fit(model, gemb); knn_tw = make_knn_fit(model, gemb, shuffle=True)

    pre = [r for r in test if r.get("patient_position") == "pre"]
    # OOV-NOUN split: the patient noun was never an attested argument in train -> count fit has nothing
    oov = [r for r in pre if (_pnoun(r) is not None and _pnoun(r) not in attested)]
    res = {}
    for name, sub in (("PRE_all", pre), ("PRE_OOVnoun", oov)):
        kf = _vec(sub, knn); kt = _vec(sub, knn_tw); od = _vec(sub, "order"); gd = _vec(sub, "graded")
        res[name] = {"n": len(kf), "order": round(float(od.mean()), 4), "graded": round(float(gd.mean()), 4),
                     "knn_fit": round(float(kf.mean()), 4), "knn_twin": round(float(kt.mean()), 4),
                     "knn_vs_order": _paired_boot(kf, od), "knn_vs_graded": _paired_boot(kf, gd),
                     "knn_vs_twin": _paired_boot(kf, kt)}
    O = res["PRE_OOVnoun"]
    verdict = {
        "knn_generalises_to_OOV_nouns_over_order": O["knn_vs_order"][1] > 0,
        "knn_generalises_to_OOV_nouns_over_structure": O["knn_vs_graded"][1] > 0,
        "knn_signal_beats_twin_on_OOV_nouns": O["knn_vs_twin"][1] > 0,
        "GENERALIZATION_SUCCESS": (O["knn_vs_order"][1] > 0 and O["knn_vs_twin"][1] > 0),
    }
    return {"k": K, "min_count": MIN_COUNT, "results": res, "verdict": verdict}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--self-test", action="store_true"); a = ap.parse_args()
    m = run()
    if a.self_test:
        assert m["results"]["PRE_OOVnoun"]["n"] > 40, m["results"]["PRE_OOVnoun"]["n"]
        print("self-test PASS", json.dumps(m["verdict"])); return
    os.makedirs(OUTDIR, exist_ok=True); m["ts_iso"] = datetime.now(timezone.utc).isoformat()
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    print("=" * 96)
    print("THEMATIC FIT AS SIMILARITY TO KNOWN ROLE-FILLERS (GloVe k-NN role transfer) -- generalizes to OOV nouns?")
    print("=" * 96)
    for name, r in m["results"].items():
        print(f"\n{name} (n={r['n']}): order={r['order']} graded={r['graded']} knn_fit={r['knn_fit']} knn_twin={r['knn_twin']}")
        print(f"   knn vs order {r['knn_vs_order']}   vs structure {r['knn_vs_graded']}   vs twin {r['knn_vs_twin']}")
    print("\nVERDICT:", json.dumps(m["verdict"], indent=2))
    print(f"\nwrote {os.path.relpath(os.path.join(OUTDIR,'metrics.json'), REPO)}")


if __name__ == "__main__":
    main()
