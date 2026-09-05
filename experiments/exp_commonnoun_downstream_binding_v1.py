"""exp_commonnoun_downstream_binding_v1 -- the DOWNSTREAM half of the bar: does forming a discourse
referent for common-noun entities lift the AFFECT experiencer-binding? Measured on the exact mention
subpopulation the affect dimension binds to (emotion experiencers), with a REFERENT-IDENTITY metric
(fixing the label-string confound in the affect study's coref_binding_vs_gold, which unfairly penalized
common-noun clusters whose glass-box label != gold's longest-head label).

POPULATION: run the landed affect extractor (experiments/affect_register via exp_affect_chain_signal_loss)
over LitBank; each emotion EXPERIENCER surface is mapped to its GOLD coref mention. Restrict to the
NON-pronoun experiencers (83.5% common-noun -- the measured gap; pronoun experiencers are the ~10%
already-handled slice). Then score how well each clustering regime binds them:
  name_only     proper-name-centric reader: NO common-noun referent (the affect register's CURRENT wiring).
  surface_head  the reader's overlay clustering (already computed, just not wired to the affect canon).
  LINKER        the faithful cue-based common-noun referent former (this problem's build).
  TWIN          LINKER labels permuted within-doc (info-free).
Metrics on the experiencer subpopulation: (1) coref chain-F1 (B3/MUC/CEAFe/CoNLL, doc bootstrap);
(2) LINKING accuracy -- of experiencer re-mentions (a prior same-gold-cluster mention exists), the frac
bound into the right chain (shares a predicted label with a prior same-gold mention) = recall, and of
those bound, frac same gold = precision.

Glass-box, NO LLM, hdlab READ-only. ASCII. own dir. Reuses the landed affect extractor + this problem's
clustering. Run: .venv/Scripts/python.exe experiments/exp_commonnoun_downstream_binding_v1.py --self-test
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
import argparse, glob, json, re, time
from collections import defaultdict
from datetime import datetime, timezone

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.coref import parse_litbank_conll, load_name_gender
import experiments.exp_affect_chain_signal_loss_v1 as AF
import experiments.exp_affect_register_qa_v1 as QA
import experiments.exp_commonnoun_coref_diagnostic_v1 as DIAG
import experiments.exp_commonnoun_referent_linker_v1 as LK

CONLL_DIR = os.path.join(_REPO, "data/litbank/coref_conll")
OUT_DIR = os.path.join(_REPO, "data/exp_commonnoun_downstream_binding_v1")
SEED = 20260904
_PRON = DIAG.ALL_PRON


def _norm(s):
    return re.sub(r"[^a-z0-9]+", " ", str(s).lower()).strip()


def experiencer_gold_midxs(path, gaz):
    """Run the affect extractor; map each NON-pronoun emotion-experiencer surface to its gold coref
    mention(s) in the same sentence (by normalized head). Returns the set of experiencer gold-mention
    midxs (the subpopulation the affect dimension binds to)."""
    sents = QA._conll_sents(path)
    pos = [AF._tagger().tag(list(t)) for t in sents]
    aff = AF.build_affects(sents, pos, AF.gold_coref_canonicalizer(path, gaz))
    ms, _n = parse_litbank_conll(path, name_gender_map=gaz)
    by_sent_head = defaultdict(list)
    for m in ms:
        if not m["is_pronoun"]:
            by_sent_head[(m["sent_idx"], _norm(m["head"]).split()[-1] if _norm(m["head"]) else "")].append(m["midx"])
    exp = set()
    for a in aff:
        surf = a.experiencer
        s = _norm(surf)
        if not s or s in _PRON or s == "?":
            continue
        key = (a.sent_idx, s.split()[-1])
        for mi in by_sent_head.get(key, []):
            exp.add(mi)
    return exp, ms


def _sub_stats(ms, labels_by_arm, exp_midxs, arm, twin_rng=None):
    """CoNLL sufficient-stats on the experiencer subpopulation for one arm."""
    noms = [m for m in ms if not m["is_pronoun"] and m["midx"] in exp_midxs]
    noms.sort(key=lambda m: m["midx"])
    lab = labels_by_arm[arm if arm != "TWIN" else "LINKER"]
    pred = [lab[m["midx"]] for m in noms]
    if twin_rng is not None:
        p2 = pred[:]; twin_rng.shuffle(p2); pred = p2
    gold = ["g%d" % m["cluster"] for m in noms]
    return LK._doc_stats(pred, gold)


def binding_acc(docs_data, arm):
    """Linking recall/precision on experiencer re-mentions (referent-identity): of experiencer mentions
    with a PRIOR same-gold-cluster experiencer mention, frac that share a predicted label with such a
    prior mention (recall); of experiencer mentions that share a predicted label with ANY prior
    experiencer mention, frac same gold (precision)."""
    rec_opp = rec_hit = prec_opp = prec_hit = 0
    for (ms, labels_by_arm, exp_midxs) in docs_data:
        lab = labels_by_arm[arm if arm != "TWIN" else "LINKER"]
        noms = [m for m in ms if not m["is_pronoun"] and m["midx"] in exp_midxs]
        noms.sort(key=lambda m: m["midx"])
        prior_by_gold = defaultdict(list); prior_by_pred = defaultdict(list)
        for m in noms:
            gl = m["cluster"]; pl = lab[m["midx"]]
            if prior_by_gold.get(gl):
                rec_opp += 1
                if any(lab[pm["midx"]] == pl for pm in prior_by_gold[gl]):
                    rec_hit += 1
            if prior_by_pred.get(pl):
                prec_opp += 1
                if any(pm["cluster"] == gl for pm in prior_by_pred[pl]):
                    prec_hit += 1
            prior_by_gold[gl].append(m); prior_by_pred[pl].append(m)
    return {"link_recall": round(rec_hit / max(1, rec_opp), 4), "recall_opps": rec_opp,
            "link_precision": round(prec_hit / max(1, prec_opp), 4), "precision_opps": prec_opp}


def run(n=None, n_boot=1000, window=6):
    import random
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    paths = sorted(glob.glob(os.path.join(CONLL_DIR, "*.conll")))
    if n:
        paths = paths[:n]
    gaz = load_name_gender()
    ggaz = QA.load_given_gazetteer() if hasattr(QA, "load_given_gazetteer") else gaz
    arms = ["name_only", "surface_head", "LINKER"]
    docs_data = []
    per_doc = {a: [] for a in arms + ["TWIN"]}
    rng = random.Random(SEED)
    n_exp_total = 0
    for p in paths:
        exp_midxs, ms = experiencer_gold_midxs(p, ggaz)
        if not exp_midxs:
            continue
        n_exp_total += len(exp_midxs)
        labels_by_arm = {}
        for a in ("name_only", "surface_head"):
            labels_by_arm[a] = DIAG.cluster_labels(ms, gaz, a)
        labels_by_arm["LINKER"] = LK.link_predicted(ms, gaz, mode="access", window=window)
        docs_data.append((ms, labels_by_arm, exp_midxs))
        for a in arms:
            per_doc[a].append(_sub_stats(ms, labels_by_arm, exp_midxs, a))
        per_doc["TWIN"].append(_sub_stats(ms, labels_by_arm, exp_midxs, "TWIN",
                                          twin_rng=random.Random(rng.random())))
    pooled = {a: LK._conll_from_stats(per_doc[a]) for a in per_doc}
    binding = {a: binding_acc(docs_data, a) for a in arms + ["TWIN"]}
    pairs = [("surface_head", "name_only"), ("LINKER", "name_only"),
             ("LINKER", "surface_head"), ("LINKER", "TWIN")]
    deltas = {"%s-%s" % (a, b): LK.bootstrap_delta(per_doc[a], per_doc[b], n_boot) for a, b in pairs}
    res = {"n_docs": len(docs_data), "n_experiencer_mentions": n_exp_total, "window": window,
           "experiencer_subpop_chainF1": pooled, "binding_recall_precision": binding,
           "deltas": deltas, "elapsed_s": round(time.time() - t0, 1)}
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor": "commonnoun_downstream_binding_v1", "results": res,
                   "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    return res


def _print(res):
    print("=" * 86)
    print("DOWNSTREAM: AFFECT-EXPERIENCER coref binding (%d docs, %d experiencer mentions, window=%d)"
          % (res["n_docs"], res["n_experiencer_mentions"], res["window"]))
    print("  coref chain-F1 on the EXPERIENCER subpopulation:")
    print("  %-14s %8s %8s %8s %8s | link_recall link_prec" % ("arm", "MUC", "B3", "CEAFe", "CoNLL"))
    for a, sc in res["experiencer_subpop_chainF1"].items():
        b = res["binding_recall_precision"][a]
        print("  %-14s %8.4f %8.4f %8.4f %8.4f |   %.4f     %.4f"
              % (a, sc["muc_f1"], sc["b3_f1"], sc["ceafe_f1"], sc["conll_avg"],
                 b["link_recall"], b["link_precision"]))
    print("  " + "-" * 82)
    for kk, d in res["deltas"].items():
        print("  %-26s CoNLL %+.4f  CI[%+.4f,%+.4f] hw=%.4f null_p95=%.4f ci_sep=%s"
              % (kk, d["delta"], d["lo"], d["hi"], d["hw"], d["null_p95"], d["ci_sep"]))
    print("=" * 86)


def self_test():
    res = run(n=8, n_boot=200)
    assert res["n_experiencer_mentions"] > 0
    assert "LINKER" in res["experiencer_subpop_chainF1"]
    print("[self-test] PASS  (n_exp=%d over %d docs)" % (res["n_experiencer_mentions"], res["n_docs"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--window", type=int, default=6)
    ap.add_argument("--nboot", type=int, default=1000)
    a = ap.parse_args()
    if a.self_test:
        self_test(); return
    res = run(n=(8 if a.smoke else a.n), n_boot=a.nboot, window=a.window)
    _print(res)


if __name__ == "__main__":
    main()
