"""exp_mcguffey_migrate_grounded_thematic_fit_poc_v1 -- DE-RISK the flagship next problem: does a
CONSTRUCTION-INDEPENDENT grounded thematic-fit signal clear the held-out inversion wall where surface
cues collapsed? (owner 2026-08-30: "can we/should we push into the solution?")

The surface-cue learner walls on unseen constructions (0.05 on held-out inversion; Deepening 3) because it
over-learns word order and never reaches the Competition Model's CONFLICT VALIDITY. The research drill pins
the generalizing mechanism as GROUNDED thematic fit -- verb argument structure + argument plausibility,
CONSTRUCTION-INDEPENDENT (it never encodes "preverbal=agent"). This PoC tests that mechanism with a
DISTRIBUTIONAL PROXY for the (still-unwired) grounded meaning channel: corpus SELECTIONAL PREFERENCES
learned from UD-EWT gold-parse (verb->typical-subject / typical-object; + a per-noun agentivity backoff).
Glass-box, no LLM. It is a PROXY (the real organ consumes `distributional_meaning_channel`, Priority 2), so
a WIN here green-lights the wiring, and a LOSS says the grounding quality is the blocker.

Operates at the UD core-argument level (where thematic fit lives). Random train/test split; the thematic-fit
predictor NEVER sees the test item's word order -- it scores each noun's fit to the verb's subject vs object
slot. CAN-FAIL: thematic-fit must BEAT the surface word-order rule (NVN) ON THE HELD-OUT NON-CANONICAL /
INVERSION items, and BEAT its info-free twin (selectional prefs learned on SHUFFLED roles), WITHOUT hurting
canonical.

Writes only to data/exp_mcguffey_migrate_grounded_thematic_fit_poc_v1/. Does NOT modify hdlab/.
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

from experiments.exp_mcguffey_migrate_build_modern_gold_v1 import parse_conllu, UD_TRAIN, UD_TEST  # noqa: E402

OUTDIR = os.path.join(REPO, "data/exp_mcguffey_migrate_grounded_thematic_fit_poc_v1")
# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-train.conllu
# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-test.conllu

_ABSTRACT = {"thing", "way", "time", "day", "year", "part", "kind", "lot", "number", "fact", "case",
             "point", "reason", "example", "problem", "question", "idea", "issue", "place", "one"}


def core_args(docs):
    """(verb_lemma, noun_lemma, role[agent/patient], canon_type, preverbal) for each nominal core arg."""
    out = []
    for doc in docs:
        for sent in doc:
            byid = {t["id"]: t for t in sent["toks"]}
            for t in sent["toks"]:
                depfull = t["deprel"]; dep = depfull.split(":")[0]
                head = byid.get(t["head"])
                if head is None or head["upos"] != "VERB":
                    continue
                if depfull == "nsubj:pass" or dep == "obj":
                    role = "patient"
                elif dep == "nsubj":
                    role = "agent"
                else:
                    continue
                if t["upos"] not in ("PROPN", "NOUN"):
                    continue
                n = t["lemma"].lower()
                if t["upos"] == "NOUN" and n in _ABSTRACT:
                    continue
                preverbal = t["id"] < t["head"]
                if depfull == "nsubj:pass":
                    ct = "passive"
                elif role == "agent" and not preverbal:
                    ct = "inversion"
                elif role == "patient" and dep == "obj" and preverbal:
                    ct = "fronting"
                else:
                    ct = "canonical"
                out.append({"verb": head["lemma"].lower(), "noun": n, "role": role,
                            "canon_type": ct, "preverbal": preverbal})
    return out


def train_selpref(items):
    vn = defaultdict(lambda: [0, 0])   # (verb,noun) -> [agent, patient]
    nn = defaultdict(lambda: [0, 0])   # noun -> [agent, patient] (agentivity backoff)
    glob = [0, 0]
    for it in items:
        a = 0 if it["role"] == "agent" else 1
        vn[(it["verb"], it["noun"])][a] += 1
        nn[it["noun"]][a] += 1
        glob[a] += 1
    return {"vn": vn, "nn": nn, "glob": glob}


def predict_tf(model, verb, noun, min_count=3):
    """CONSTRUCTION-INDEPENDENT: score the noun's fit to the verb's subject vs object slot (verb-keyed,
    backing off to per-noun agentivity, then global prior). Never uses the test item's word order."""
    ca, cp = model["vn"].get((verb, noun), [0, 0])
    if ca + cp >= min_count:
        return "agent" if ca >= cp else "patient"
    na, npt = model["nn"].get(noun, [0, 0])
    if na + npt >= min_count:
        return "agent" if na >= npt else "patient"
    ga, gp = model["glob"]
    return "agent" if ga >= gp else "patient"


def predict_combined(model, it, min_v=3, min_n=5):
    """BRAIN-FAITHFUL CUE COMPETITION (Competition Model conflict validity): word order is the default
    (high overall validity, wins on canonical); the CONSTRUCTION-INDEPENDENT thematic-fit cue OVERRIDES
    order ONLY when it is confident AND conflicts with order (the conflict case order gets wrong). Order
    and meaning COMPETE -- meaning does not replace order (drill: reversibles fall back to structure)."""
    order = "agent" if it["preverbal"] else "patient"
    ca, cp = model["vn"].get((it["verb"], it["noun"]), [0, 0])
    na, npt = model["nn"].get(it["noun"], [0, 0])
    if ca + cp >= min_v:
        fit = "agent" if ca >= cp else "patient"
    elif na + npt >= min_n:
        fit = "agent" if na >= npt else "patient"
    else:
        fit = None
    if fit is None or fit == order:
        return order
    return fit   # confident conflict -> trust meaning


def evaluate(model, test, predictor):
    by_type = defaultdict(lambda: [0, 0])   # type -> [correct, total]
    allc = [0, 0]
    for it in test:
        pred = predictor(it)
        ok = int(pred == it["role"])
        by_type[it["canon_type"]][0] += ok; by_type[it["canon_type"]][1] += 1
        allc[0] += ok; allc[1] += 1
    def acc(x):
        return round(x[0] / x[1], 4) if x[1] else None
    res = {"ALL": {"acc": acc(allc), "n": allc[1]}}
    for ct, x in by_type.items():
        res[ct] = {"acc": acc(x), "n": x[1]}
    # non-canonical aggregate
    nc = [0, 0]
    for ct in ("passive", "inversion", "fronting"):
        if ct in by_type:
            nc[0] += by_type[ct][0]; nc[1] += by_type[ct][1]
    res["NONCANON"] = {"acc": round(nc[0] / nc[1], 4) if nc[1] else None, "n": nc[1]}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--seed", type=int, default=20260830)
    args = ap.parse_args()

    docs = parse_conllu(UD_TRAIN) + parse_conllu(UD_TEST)
    items = core_args(docs)
    rng = np.random.default_rng(args.seed)
    idx = rng.permutation(len(items))
    cut = int(0.7 * len(items))
    train = [items[i] for i in idx[:cut]]
    test = [items[i] for i in idx[cut:]]

    model = train_selpref(train)
    shuf = [dict(it) for it in train]
    roles = [it["role"] for it in shuf]
    rng.shuffle(roles)
    for it, r in zip(shuf, roles):
        it["role"] = r
    model_twin = train_selpref(shuf)

    tf = evaluate(model, test, lambda it: predict_tf(model, it["verb"], it["noun"]))
    nvn = evaluate(model, test, lambda it: "agent" if it["preverbal"] else "patient")
    twin = evaluate(model, test, lambda it: predict_tf(model_twin, it["verb"], it["noun"]))
    comb = evaluate(model, test, lambda it: predict_combined(model, it))
    comb_twin = evaluate(model_twin, test, lambda it: predict_combined(model_twin, it))

    def g(d, k):
        return (d.get(k) or {}).get("acc")

    verdict = {
        "tf_beats_nvn_on_noncanon": (g(tf, "NONCANON") or 0) > (g(nvn, "NONCANON") or 0),
        "tf_beats_twin_on_noncanon": (g(tf, "NONCANON") or 0) > (g(twin, "NONCANON") or 0),
        "COMBINED_beats_nvn_on_noncanon": (g(comb, "NONCANON") or 0) > (g(nvn, "NONCANON") or 0),
        "COMBINED_matches_nvn_on_canonical": (g(comb, "canonical") or 0) >= (g(nvn, "canonical") or 0) - 0.03,
        "COMBINED_beats_nvn_overall": (g(comb, "ALL") or 0) > (g(nvn, "ALL") or 0),
        "COMBINED_beats_twin_overall": (g(comb, "ALL") or 0) > (g(comb_twin, "ALL") or 0),
        "domains": {"order_wins_canonical": [g(nvn, "canonical"), g(tf, "canonical")],
                    "fit_wins_noncanon": [g(tf, "NONCANON"), g(nvn, "NONCANON")]},
        "COMBINED": {"ALL": g(comb, "ALL"), "canonical": g(comb, "canonical"),
                     "NONCANON": g(comb, "NONCANON"), "inversion": g(comb, "inversion")},
    }
    metrics = {"ts_iso": datetime.now(timezone.utc).isoformat(), "seed": args.seed,
               "n_items": len(items), "n_train": len(train), "n_test": len(test),
               "thematic_fit": tf, "nvn_surface": nvn, "info_free_twin": twin, "combined": comb,
               "combined_twin": comb_twin, "verdict": verdict}

    if args.self_test:
        assert len(items) > 1000, len(items)
        print("self-test PASS", json.dumps(verdict["inversion"]))
        return

    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print("=" * 90)
    print("GROUNDED THEMATIC-FIT PoC (distributional selectional preference; construction-independent; no LLM)")
    print("=" * 90)
    print(f"items={len(items)} train={len(train)} test={len(test)}")
    print(f"\n{'cut':12s} {'NVN(order)':>12s} {'thematic-fit':>13s} {'COMBINED':>10s} {'twin':>8s}   n")
    for ct in ("ALL", "canonical", "NONCANON", "passive", "inversion", "fronting"):
        print(f"{ct:12s} {str(g(nvn,ct)):>12s} {str(g(tf,ct)):>13s} {str(g(comb,ct)):>10s} {str(g(twin,ct)):>8s}"
              f"   {(tf.get(ct) or {}).get('n')}")
    print("\nVERDICT:", json.dumps(verdict, indent=2))
    print(f"\nwrote {os.path.relpath(os.path.join(OUTDIR,'metrics.json'), REPO)}")


if __name__ == "__main__":
    main()
