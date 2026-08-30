"""exp_mcguffey_migrate_learned_cue_transfer_v1 -- CAN A LEARNED CUE-COMPETITION MECHANISM GENERALISE
ACROSS UNSEEN CONSTRUCTIONS AND UNSEEN CORPORA? (owner: "can we show any generalization here or clear paths?")

The hand-set cue-competition assigner is weight-sensitive; the Competition Model (Bates & MacWhinney) says
cue VALIDITIES are LEARNED from the input. So the brain-faithful test of generalization is: LEARN the cue
weights on one population and show they TRANSFER to a held-out one -- especially to a construction the model
NEVER SAW in training. If learned cues (animacy/case override word order) transfer to unseen inversion, the
mechanism is construction-general, not a per-construction patch.

GLASS-BOX, NO LLM. A numpy logistic regression over 6 INTERPRETABLE cues (the learned coefficients ARE the
Competition Model cue validities): preverbal, animate, nominative-pronoun, accusative-pronoun, passive-voice
context, by-phrase. Label = agent(1)/patient(0). This is the brain's mechanism (Dowty proto-roles integrated
by learned cue validity), transparent end to end.

THREE TRANSFER TESTS (each vs: majority floor recomputed on the TEST pop; the ORDER-ONLY rule = the NVN
first-noun heuristic; and an INFO-FREE TWIN = weights learned on SHUFFLED labels, which must collapse to floor):
  1. IN-DISTRIBUTION   train/test split of modern UD-EWT.
  2. CROSS-CONSTRUCTION train on canonical+passive modern, TEST ON INVERSION (never seen in training).
  3. CROSS-CORPUS      train modern -> test McGuffey, and train McGuffey -> test modern (distribution-invariance).

Writes only to data/exp_mcguffey_migrate_learned_cue_transfer_v1/. Does NOT modify hdlab/.
"""
from __future__ import annotations
import argparse, json, os, sys
from collections import Counter
from datetime import datetime, timezone

import numpy as np
os.environ.setdefault("OMP_NUM_THREADS", "1")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments.exp_wire_organs_endtoend_v1 import _pos, IN_SCOPE_ROLES, _is_animate_head, load_gold  # noqa: E402

MODERN_GOLD = os.path.join(REPO, "data/eval_gold_mention_role_modern_ud_ewt_v1",
                           "gold_situation_modern_ud_ewt_v1.jsonl")
OUTDIR = os.path.join(REPO, "data/exp_mcguffey_migrate_learned_cue_transfer_v1")
# KB_REFERENT: data/eval_gold_mention_role_modern_ud_ewt_v1/gold_situation_modern_ud_ewt_v1.jsonl
# KB_REFERENT: data/eval_gold_mention_role_mcguffey_v1/gold_multiclause_entity_track_v3.jsonl
# KB_REFERENT: data/eval_gold_mention_role_mcguffey_v1/gold_multientity_dense_v1.jsonl

_AUX = {"has", "have", "had", "is", "are", "was", "were", "be", "been", "being", "am",
        "do", "does", "did", "will", "would", "can", "could", "may", "might", "shall", "should", "must"}
_BE = {"is", "are", "was", "were", "be", "been", "being", "am"}
_NOM = {"he", "she", "they", "i", "we", "who"}
_ACC = {"him", "her", "them", "me", "us", "whom"}
CUE_NAMES = ["preverbal", "animate", "nominative", "accusative", "passive_subj", "by_phrase", "bias"]


def _mention_features(clause, mention):
    """6 interpretable cues + bias for the mention's role in this clause (None if the mention is not locatable)."""
    toks = _pos(clause)
    words = [w for w, _ in toks]
    tags = [t for _, t in toks]
    lw = [w.lower() for w in words]
    mtoks = [w.strip(".,\"'").lower() for w in mention.split() if w.strip(".,\"'")]
    if not mtoks:
        return None
    head = mtoks[-1]
    mi = next((i for i, w in enumerate(lw) if w == head), None)
    if mi is None:
        mi = next((i for i, w in enumerate(lw) if w in mtoks), None)
    if mi is None:
        return None
    verbs = [i for i, t in enumerate(tags) if t in ("VBD", "VBZ", "VBP", "VBG", "VBN")]
    content = [i for i in verbs if lw[i] not in _AUX]
    pool = content or verbs
    if not pool:
        return None
    vi = min(pool, key=lambda i: abs(i - mi))
    preverbal = 1.0 if mi < vi else 0.0
    animate = 1.0 if _is_animate_head(words[mi], tags[mi]) else 0.0
    nom = 1.0 if lw[mi] in _NOM else 0.0
    acc = 1.0 if lw[mi] in _ACC else 0.0
    passive = 0.0
    if tags[vi] == "VBN":
        j, steps = vi - 1, 0
        while j >= 0 and steps < 4:
            if lw[j] in _BE:
                passive = 1.0; break
            if lw[j] in _AUX or tags[j] in ("RB", "MD"):
                j -= 1; steps += 1; continue
            break
    passive_subj = 1.0 if (passive and preverbal) else 0.0
    by_phrase = 1.0 if (mi >= 1 and lw[mi - 1] == "by") else 0.0
    return [preverbal, animate, nom, acc, passive_subj, by_phrase, 1.0]


def extract_items(passages):
    """Per in-scope target query: (feature vector, label agent=1/patient=0, noncanon_type)."""
    X, y, ty = [], [], []
    for p in passages:
        ment = {}
        for name, chain in p["entities"].items():
            for m in chain:
                ment[(name, m["clause"])] = m["mention"]
        for q in p.get("target_queries", []):
            if q["gold_role"] not in IN_SCOPE_ROLES:
                continue
            m = ment.get((q["entity"], q["query_clause"]))
            if m is None:
                continue
            f = _mention_features(p["clauses"][q["query_clause"]], m)
            if f is None:
                continue
            X.append(f); y.append(1 if q["gold_role"] == "agent" else 0)
            ty.append(q.get("noncanon_type", "canonical"))
    return np.array(X, float), np.array(y, int), np.array(ty, object)


def fit_logreg(X, y, l2=1.0, iters=400, lr=0.3):
    w = np.zeros(X.shape[1])
    n = len(y)
    if n == 0 or len(set(y.tolist())) < 2:
        # degenerate: predict the single class via bias
        w[-1] = 4.0 if (n and y.mean() > 0.5) else -4.0
        return w
    for _ in range(iters):
        p = 1.0 / (1.0 + np.exp(-(X @ w)))
        g = X.T @ (p - y) / n + l2 * np.r_[w[:-1], 0.0] / n
        w -= lr * g
    return w


def acc(w, X, y):
    if len(y) == 0:
        return {"acc": 0.0, "ci": [0.0, 0.0], "n": 0}
    pred = (1.0 / (1.0 + np.exp(-(X @ w)))) >= 0.5
    v = (pred.astype(int) == y).astype(float)
    rng = np.random.default_rng(12345)
    boots = [rng.choice(v, size=len(v), replace=True).mean() for _ in range(2000)]
    return {"acc": round(float(v.mean()), 4),
            "ci": [round(float(np.percentile(boots, 2.5)), 4), round(float(np.percentile(boots, 97.5)), 4)],
            "n": int(len(y))}


def majority_floor(y):
    if len(y) == 0:
        return {"acc": 0.0, "n": 0}
    maj = 1 if y.mean() >= 0.5 else 0
    return {"acc": round(float((y == maj).mean()), 4), "n": int(len(y)), "label": "agent" if maj else "patient"}


def order_only_acc(X, y):
    # NVN heuristic: preverbal -> agent, else patient. (X[:,0] is preverbal)
    pred = (X[:, 0] >= 0.5).astype(int)
    return {"acc": round(float((pred == y).mean()), 4), "n": int(len(y))} if len(y) else {"acc": 0.0, "n": 0}


def learned_coeffs(w):
    return {CUE_NAMES[i]: round(float(w[i]), 3) for i in range(len(CUE_NAMES))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--seed", type=int, default=20260830)
    args = ap.parse_args()

    modern = [json.loads(l) for l in open(MODERN_GOLD, encoding="utf-8") if l.strip()]
    mcg = load_gold()
    if args.self_test:
        modern = modern[:120]; mcg = mcg[:40]

    Xm, ym, tym = extract_items(modern)
    Xg, yg, tyg = extract_items(mcg)
    rng = np.random.default_rng(args.seed)

    # 1. IN-DISTRIBUTION (modern train/test split)
    idx = rng.permutation(len(ym))
    cut = int(0.7 * len(idx))
    tr, te = idx[:cut], idx[cut:]
    w_in = fit_logreg(Xm[tr], ym[tr])
    w_twin = fit_logreg(Xm[tr], rng.permutation(ym[tr]))   # info-free: shuffled labels
    indist = {"learned_cue": acc(w_in, Xm[te], ym[te]), "order_only": order_only_acc(Xm[te], ym[te]),
              "floor": majority_floor(ym[te]), "info_free_twin": acc(w_twin, Xm[te], ym[te]),
              "coeffs": learned_coeffs(w_in)}

    # 2. CROSS-CONSTRUCTION: train on canonical+passive modern, TEST ON INVERSION (unseen construction)
    train_mask = np.isin(tym, ["canonical", "passive"])
    test_mask = (tym == "inversion")
    w_cc = fit_logreg(Xm[train_mask], ym[train_mask])
    w_cc_twin = fit_logreg(Xm[train_mask], rng.permutation(ym[train_mask]))
    crosscon = {"train_on": "canonical+passive", "test_on": "inversion(unseen)",
                "learned_cue": acc(w_cc, Xm[test_mask], ym[test_mask]),
                "order_only": order_only_acc(Xm[test_mask], ym[test_mask]),
                "floor": majority_floor(ym[test_mask]),
                "info_free_twin": acc(w_cc_twin, Xm[test_mask], ym[test_mask]),
                "coeffs": learned_coeffs(w_cc)}

    # 3. CROSS-CORPUS (distribution-invariance)
    w_mod = fit_logreg(Xm, ym)
    w_mcg = fit_logreg(Xg, yg)
    crosscorp = {
        "train_modern_test_mcguffey": {"learned_cue": acc(w_mod, Xg, yg), "order_only": order_only_acc(Xg, yg),
                                       "floor": majority_floor(yg)},
        "train_mcguffey_test_modern": {"learned_cue": acc(w_mcg, Xm, ym), "order_only": order_only_acc(Xm, ym),
                                       "floor": majority_floor(ym)},
        "coeffs_modern": learned_coeffs(w_mod), "coeffs_mcguffey": learned_coeffs(w_mcg),
    }

    def beats(a, b):
        return a["acc"] > b["acc"]

    verdict = {
        "indist_cue_beats_order_and_floor": beats(indist["learned_cue"], indist["order_only"]) and
                                            beats(indist["learned_cue"], indist["floor"]),
        "indist_twin_loses": indist["learned_cue"]["acc"] > indist["info_free_twin"]["acc"],
        "cross_construction_generalises": beats(crosscon["learned_cue"], crosscon["order_only"]),
        "cross_construction_beats_order_by": round(crosscon["learned_cue"]["acc"] - crosscon["order_only"]["acc"], 4),
        "cross_corpus_modern_to_mcguffey_beats_order":
            beats(crosscorp["train_modern_test_mcguffey"]["learned_cue"],
                  crosscorp["train_modern_test_mcguffey"]["order_only"]),
    }
    metrics = {"ts_iso": datetime.now(timezone.utc).isoformat(), "seed": args.seed,
               "n_modern_items": int(len(ym)), "n_mcguffey_items": int(len(yg)),
               "in_distribution": indist, "cross_construction": crosscon, "cross_corpus": crosscorp,
               "verdict": verdict}

    if args.self_test:
        assert len(ym) > 30 and len(yg) > 20, (len(ym), len(yg))
        print("self-test PASS", json.dumps({k: verdict[k] for k in
              ("cross_construction_generalises", "cross_construction_beats_order_by")}))
        return

    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print("=" * 90)
    print("LEARNED CUE-COMPETITION TRANSFER (glass-box logreg over interpretable cues; no LLM)")
    print("=" * 90)
    print(f"items: modern={len(ym)}  mcguffey={len(yg)}")
    print("\n[1] IN-DISTRIBUTION (modern train/test)")
    print(f"    learned {indist['learned_cue']['acc']:.3f} {indist['learned_cue']['ci']}  vs order-only "
          f"{indist['order_only']['acc']:.3f}  floor {indist['floor']['acc']:.3f}  twin {indist['info_free_twin']['acc']:.3f}")
    print(f"    learned cue validities: {indist['coeffs']}")
    print("\n[2] CROSS-CONSTRUCTION (train canonical+passive -> TEST ON UNSEEN INVERSION)")
    cc = crosscon
    print(f"    learned {cc['learned_cue']['acc']:.3f} {cc['learned_cue']['ci']} (n={cc['learned_cue']['n']})  vs "
          f"order-only(NVN) {cc['order_only']['acc']:.3f}  floor {cc['floor']['acc']:.3f}  twin {cc['info_free_twin']['acc']:.3f}")
    print("\n[3] CROSS-CORPUS (distribution-invariance)")
    a = crosscorp["train_modern_test_mcguffey"]; b = crosscorp["train_mcguffey_test_modern"]
    print(f"    train modern -> test McGuffey:  learned {a['learned_cue']['acc']:.3f}  order-only {a['order_only']['acc']:.3f}  floor {a['floor']['acc']:.3f}")
    print(f"    train McGuffey -> test modern:  learned {b['learned_cue']['acc']:.3f}  order-only {b['order_only']['acc']:.3f}  floor {b['floor']['acc']:.3f}")
    print("\nVERDICT:", json.dumps(verdict, indent=2))
    print(f"\nwrote {os.path.relpath(os.path.join(OUTDIR,'metrics.json'), REPO)}")


if __name__ == "__main__":
    main()
