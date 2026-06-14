"""
exp_substrate_tier2_production_validation_prover_cpu_v1.py -- DECISION 26b PROVER: held-out production-scale validation of the 3 Tier-2 integrated modules -- CPU/local (no heat).

ROUTING: Director DECISION 26b (mirror 24b). Validate Tier-2 modules at real scale, report ACTUAL (10th rule).
  Modules (Testbed-integrated this cycle): hdlab/bayesian_inference.py (bayes_update_categorical + map_estimate + EMMixture);
  backend/substrate_index/intent_classifier.py (IntentClassifier; abstains -> abstain != wrong, R3).
  Data: local public sets (no LLM/learned-vector assist, R2). UCI mushroom not local -> sst2 binary as the NB substitute (flagged: sentiment-NB
  is harder than mushroom, so a sub-0.85 here is dataset-difficulty not module failure -- module arithmetic is also unit-checked exactly).
  ATIS intent (local) for IntentClassifier (its actual use case). EMMixture on synthetic well-separated 3-Gaussian (self-contained).

PRE-REGISTERED (Director bars): NB binary accuracy >= 0.85; EMMixture cluster purity >= 0.80; IntentClassifier acc >= 0.70 (over non-abstained;
  abstain reported separately, R3). Report ACTUAL; a miss flags PRODUCTION-UNVERIFIED (does NOT remove ONLINE counting, R4). Also exact unit-check
  of bayes_update_categorical/map_estimate (module correctness, independent of dataset difficulty). ASCII-only. --self-test + --smoke + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json, math, random
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, Tuple, List
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_tier2_production_validation_prover_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
DATA = REPO / "experiments" / "data"


def _tok(t): return t.lower().split()


def _selftest():
    from hdlab.bayesian_inference import bayes_update_categorical, map_estimate
    post = bayes_update_categorical([0.5, 0.5], [0.9, 0.1])
    assert abs(post[0] - 0.9) < 1e-6 and map_estimate(post) == 0, post     # exact Bayes arithmetic
    post2 = bayes_update_categorical([0.2, 0.8], [0.5, 0.5]); assert abs(post2[0] - 0.2) < 1e-6
    print("[selftest] PASS: substrate_tier2_production_validation_prover_cpu_v1 (bayes arithmetic exact)", flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        sys.exit(0)


def _nb_categorical(train_rows, test_rows, label_of, feats_of):
    """Generic NB via the module's bayes_update_categorical + map_estimate over categorical features."""
    from hdlab.bayesian_inference import bayes_update_categorical, map_estimate
    labels = sorted({label_of(r) for r in train_rows}); li = {l: i for i, l in enumerate(labels)}; L = len(labels)
    fc = [defaultdict(lambda: defaultdict(float)) for _ in range(L)]; clsc = [0] * L
    for r in train_rows:
        y = li[label_of(r)]; clsc[y] += 1
        for j, v in feats_of(r): fc[y][j][v] += 1
    prior = [c / sum(clsc) for c in clsc]
    def pfv(j, v, k): return (fc[k][j].get(v, 0) + 1.0) / (clsc[k] + (len(fc[k][j]) or 1) + 1)
    ok = 0
    for r in test_rows:
        post = list(prior)
        for j, v in feats_of(r): post = bayes_update_categorical(post, [pfv(j, v, k) for k in range(L)])
        ok += int(labels[map_estimate(post)] == label_of(r))
    return round(ok / len(test_rows), 4), len(test_rows)


def nb_eval(smoke):
    """NB via the module on UCI mushroom (Director's spec'd dataset; near-separable). Fallback: local sst2 binary (harder)."""
    # try UCI mushroom (the spec'd dataset)
    try:
        import urllib.request
        raw = urllib.request.urlopen("https://archive.ics.uci.edu/ml/machine-learning-databases/mushroom/agaricus-lepiota.data", timeout=20).read().decode()
        rows = [r.split(",") for r in raw.strip().splitlines() if r]
        random.seed(26); random.shuffle(rows)
        if smoke: rows = rows[:400]
        cut = int(len(rows) * 0.7); tr, te = rows[:cut], rows[cut:]
        acc, n = _nb_categorical(tr, te, lambda r: r[0], lambda r: list(enumerate(r[1:])))
        return {"accuracy": acc, "n_test": n, "n_train": len(tr), "dataset": "uci_mushroom"}
    except Exception:
        pass
    # fallback: sst2 binary text NB (substitute; sentiment is harder)
    p = DATA / "sst2.json"
    if not p.exists():
        return {"error": "no_nb_data"}
    d = json.loads(p.read_text(encoding="utf-8")); labels = d["labels"]
    def lab(r): return r["label"] if isinstance(r.get("label"), int) else labels.index(r.get("label"))
    def feats(r): return [(0, w) for w in set(_tok(r["text"]))]   # bag-of-words as feature j=0 multi-value
    tr = d["train"][: (400 if smoke else 6000)]; te = d["test"][: (100 if smoke else 1500)]
    # sst2 path: keep prior NB (per-word) for fidelity
    from hdlab.bayesian_inference import bayes_update_categorical, map_estimate
    L = len(labels); wc = [defaultdict(float) for _ in range(L)]; ctot = [0.0] * L; clsc = [0] * L
    for r in tr:
        y = lab(r); clsc[y] += 1
        for w in _tok(r["text"]): wc[y][w] += 1; ctot[y] += 1
    V = len({w for c in wc for w in c}); prior = [c / sum(clsc) for c in clsc]
    def pwc(w, k): return (wc[k].get(w, 0) + 1.0) / (ctot[k] + V + 1)
    ok = 0
    for r in te:
        post = list(prior)
        for w in _tok(r["text"]): post = bayes_update_categorical(post, [pwc(w, k) for k in range(L)])
        ok += int(map_estimate(post) == lab(r))
    return {"accuracy": round(ok / len(te), 4), "n_test": len(te), "n_train": len(tr), "dataset": "sst2_binary_FALLBACK"}


def em_eval(smoke):
    from hdlab.bayesian_inference import EMMixture
    rng = np.random.RandomState(26)
    centers = np.array([[0, 0], [6, 6], [0, 8]], dtype=float); n = (60 if smoke else 300)
    X = []; y = []
    for k, c in enumerate(centers):
        X.append(rng.randn(n, 2) * 0.7 + c); y += [k] * n
    X = np.vstack(X); y = np.array(y)
    em = EMMixture(K=3, n_features=2); em.fit(X, max_iter=(20 if smoke else 100))
    pred = np.array(em.predict(X))
    # purity: for each predicted cluster, majority true label
    pur = 0
    for c in set(pred.tolist()):
        mask = pred == c
        if mask.sum(): pur += Counter(y[mask].tolist()).most_common(1)[0][1]
    return {"purity": round(pur / len(y), 4), "n": len(y), "K": 3}


def intent_eval(smoke):
    from backend.substrate_index.intent_classifier import IntentClassifier
    p = DATA / "atis_intent.json"
    if not p.exists():
        return {"error": "no_atis"}
    d = json.loads(p.read_text(encoding="utf-8"))
    tr = [(r["text"], r["intent"]) for r in d["train"][: (200 if smoke else 4000)]]
    te = [(r["text"], r["intent"]) for r in (d["test"][: (60 if smoke else 800)])]
    labset = sorted({l for _, l in tr})
    clf = IntentClassifier(labels=labset) if "labels" in IntentClassifier.__init__.__code__.co_varnames else IntentClassifier()
    try:
        clf.fit(tr, epochs=(3 if smoke else 6))
    except TypeError:
        clf.fit(tr)
    ok = 0; abstain = 0; n = 0
    for text, gold in te:
        n += 1
        pred = clf.predict(text)
        if pred is None: abstain += 1; continue
        ok += int(pred == gold)
    answered = n - abstain
    acc = round(ok / answered, 4) if answered else 0.0
    return {"accuracy_on_answered": acc, "abstain_rate": round(abstain / n, 4), "n_test": n, "n_answered": answered,
            "overall_acc": round(ok / n, 4), "n_labels": len(labset)}


def run() -> Dict:
    smoke = (RUN_MODE == "smoke")
    nb = nb_eval(smoke); em = em_eval(smoke); intent = intent_eval(smoke)
    print("  NB (bayes_update_categorical+map_estimate, %s): acc=%s" % (nb.get("dataset", "?"), nb.get("accuracy", nb.get("error"))), flush=True)
    print("  EMMixture (synthetic 3-Gaussian): purity=%s" % em.get("purity", em.get("error")), flush=True)
    print("  IntentClassifier (ATIS): acc_on_answered=%s abstain_rate=%s overall=%s" % (
        intent.get("accuracy_on_answered"), intent.get("abstain_rate"), intent.get("overall_acc")), flush=True)
    return {"nb": nb, "em": em, "intent": intent}


def verdict(r) -> Tuple[str, str]:
    nb = r["nb"].get("accuracy"); pur = r["em"].get("purity"); ia = r["intent"].get("accuracy_on_answered")
    nb_p = (nb is not None and nb >= 0.85); em_p = (pur is not None and pur >= 0.80); in_p = (ia is not None and ia >= 0.70)
    s = ("DECISION 26b Tier-2 production check (R2 substrate-on-its-own; R3 abstain!=wrong). NB acc=%s on %s (bar 0.85; bayes arithmetic also "
         "unit-checked exact in selftest; if dataset=sst2_binary_FALLBACK note sentiment-NB is harder than the spec'd mushroom). EMMixture "
         "purity=%s (bar 0.80). IntentClassifier acc-on-answered=%s abstain=%s (bar 0.70; abstains excluded per R3). FAIL flags "
         "PRODUCTION-UNVERIFIED, does NOT remove ONLINE counting (R4).") % (
        nb, r["nb"].get("dataset", "?"), pur, ia, r["intent"].get("abstain_rate"))
    n_pass = sum([nb_p, em_p, in_p])
    if n_pass == 3:
        return ("HARD_PASS", "HARD_PASS: all 3 Tier-2 modules meet production bars (NB %s, EM purity %s, intent %s). " % (nb, pur, ia) + s)
    flagged = [m for m, ok in [("NB", nb_p), ("EMMixture", em_p), ("IntentClassifier", in_p)] if not ok]
    if n_pass >= 1:
        return ("MIDDLE_BAND", "MIDDLE_BAND: %d/3 meet bar; PRODUCTION-UNVERIFIED: %s. " % (n_pass, flagged) + s)
    return ("HARD_FAIL", "HARD_FAIL: 0/3 Tier-2 modules meet production bars -- PRODUCTION-UNVERIFIED. " + s)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
