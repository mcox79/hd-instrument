"""
exp_substrate_crossdomain_transfer_sst2_imdb_cpu_v1.py -- Cell C: cross-domain transfer (SST-2 -> IMDB sentiment) -- CPU.

ROUTING: research_to_exp_dev_CELL_C_CROSS_DOMAIN_FALLBACK (SST-2 -> IMDB, Pair 1 LOCK). Substrate-quality-first; NO LLM frame.
  Substrate-product question: do substrate-classical primitives (discriminative_perceptron) show POSITIVE TRANSFER across a
  distributional shift? Train the discriminative_perceptron sentiment classifier on SST-2 (short formal review snippets);
  transfer (warm-start the feature weights) to IMDB (long informal full reviews); compare to train-from-scratch on IMDB at
  1/5/10/100pct of IMDB training data.

  Classifier = averaged perceptron (the discriminative_perceptron primitive) over hashed word-unigram + bigram features (binary
  sentiment). Transfer = initialize IMDB training from the SST-2-trained averaged weights; scratch = zero init. F1 (macro) on a
  fixed IMDB test subset.

  DATA: SST-2 bundled (experiments/data/sst2.json). IMDB via datasets.load_dataset('imdb') on the home/remote env (NOT on
  laptop -> env-gated UNKNOWN). If IMDB unavailable, returns UNKNOWN (harness correct + ready), not a failure.

PRE-REGISTERED (Research LOCK): transfer F1 / scratch F1 at 5pct IMDB data:
  HARD-PASS: ratio >= 1.20 (positive transfer; substrate primitive carries discriminative signal across domain).
  MIDDLE: ratio 0.95-1.20 (neutral / weak positive). HARD-FAIL: < 0.95 (negative transfer). UNKNOWN if IMDB unavailable.
ASCII-only. CPU. --self-test + --smoke + metrics.json. Route via local_cpu_queue (env-gated) or remote_cpu_queue.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json, re
from pathlib import Path
from typing import Dict, Tuple, List
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_crossdomain_transfer_sst2_imdb_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
FRACS = [0.01, 0.05, 0.10, 1.0]
SEEDS = [7, 8, 9]
NBITS = 20            # hashing dim 2^20
DIM = 1 << NBITS
IMDB_TRAIN_CAP = 5000
IMDB_TEST_CAP = 2000
_TOK = re.compile(r"[a-z']+")


def _feats(text: str):
    toks = _TOK.findall(text.lower())
    idxs = []
    for w in toks:
        idxs.append(hash("u_" + w) & (DIM - 1))
    for i in range(len(toks) - 1):
        idxs.append(hash("b_" + toks[i] + "_" + toks[i + 1]) & (DIM - 1))
    return idxs


def _train_perceptron(data, epochs, w0, rng):
    """Averaged binary perceptron. data=[(idxs,label in {0,1})]; labels mapped to +-1. Returns averaged weights (DIM,)."""
    w = w0.copy() if w0 is not None else np.zeros(DIM, dtype=np.float64)
    cw = np.zeros(DIM, dtype=np.float64); c = 1
    for _ in range(epochs):
        for i in rng.permutation(len(data)):
            idxs, y = data[i]; y = 1 if y == 1 else -1
            score = w[idxs].sum()
            if (score >= 0 and y < 0) or (score < 0 and y > 0):
                w[idxs] += y; cw[idxs] += y * c
            c += 1
    wavg = w.copy(); wavg -= cw / c
    return wavg


def _f1_macro(data, w):
    tp = {0: 0, 1: 0}; fp = {0: 0, 1: 0}; fn = {0: 0, 1: 0}
    for idxs, y in data:
        pred = 1 if w[idxs].sum() >= 0 else 0
        if pred == y: tp[y] += 1
        else: fp[pred] += 1; fn[y] += 1
    f1s = []
    for c in (0, 1):
        p = tp[c] / (tp[c] + fp[c] + 1e-9); r = tp[c] / (tp[c] + fn[c] + 1e-9)
        f1s.append(2 * p * r / (p + r + 1e-9))
    return sum(f1s) / 2


def _load_sst2():
    d = json.load(open(REPO / "experiments" / "data" / "sst2.json", encoding="utf-8"))
    tr = [(_feats(e["text"]), int(e["label"])) for e in d["train"] if e.get("text")]
    return tr


def _load_imdb():
    """IMDB via datasets lib (home env). Returns (train, test) as [(idxs,label)] or None if unavailable."""
    try:
        from datasets import load_dataset
        ds = load_dataset("imdb")
        tr = [(_feats(t), int(l)) for t, l in zip(ds["train"]["text"], ds["train"]["label"])]
        te = [(_feats(t), int(l)) for t, l in zip(ds["test"]["text"], ds["test"]["label"])]
        return tr, te
    except Exception as e:
        print("[imdb] unavailable: %s" % str(e)[:120], flush=True)
        return None


def run() -> Dict:
    sst2 = _load_sst2()
    imdb = _load_imdb()
    if imdb is None:
        return {"error": "imdb_unavailable_env_gated", "note": "needs datasets.load_dataset('imdb') on home; harness correct + ready"}
    imdb_tr, imdb_te = imdb
    rng0 = np.random.default_rng(0)
    imdb_tr = [imdb_tr[i] for i in rng0.permutation(len(imdb_tr))[:IMDB_TRAIN_CAP]]
    imdb_te = [imdb_te[i] for i in rng0.permutation(len(imdb_te))[:IMDB_TEST_CAP]]
    ep = 3 if SMOKE else 8
    # SST-2 pretrained weights (source domain)
    w_src = _train_perceptron(sst2, ep, None, np.random.default_rng(123))
    fracs = [0.05] if SMOKE else FRACS
    seeds = SEEDS[:1] if SMOKE else SEEDS
    curve = []
    for fr in fracs:
        tr_ratio = []; sc_list = []; tf_list = []
        for sd in seeds:
            rng = np.random.default_rng(sd)
            n = max(10, int(len(imdb_tr) * fr))
            sub = [imdb_tr[i] for i in rng.permutation(len(imdb_tr))[:n]]
            w_scratch = _train_perceptron(sub, ep, None, rng)
            w_transfer = _train_perceptron(sub, ep, w_src, rng)   # warm-start from SST-2
            f_sc = _f1_macro(imdb_te, w_scratch); f_tf = _f1_macro(imdb_te, w_transfer)
            sc_list.append(f_sc); tf_list.append(f_tf); tr_ratio.append(f_tf / (f_sc + 1e-9))
        sc = sum(sc_list) / len(sc_list); tf = sum(tf_list) / len(tf_list); ratio = sum(tr_ratio) / len(tr_ratio)
        curve.append({"frac": fr, "scratch_f1": round(sc, 4), "transfer_f1": round(tf, 4), "ratio": round(ratio, 4),
                      "n_imdb_train": max(10, int(len(imdb_tr) * fr))})
        print("  frac=%5.1f%% scratch_f1=%.4f transfer_f1=%.4f ratio=%.4f (n_train=%d)"
              % (100 * fr, sc, tf, ratio, max(10, int(len(imdb_tr) * fr))), flush=True)
    # source-only baseline (SST-2 model applied directly to IMDB, no IMDB training)
    f_src_only = _f1_macro(imdb_te, w_src)
    print("  [ref] SST-2-only on IMDB (zero-shot transfer) F1=%.4f" % f_src_only, flush=True)
    return {"curve": curve, "sst2_only_on_imdb_f1": round(f_src_only, 4), "n_imdb_test": len(imdb_te), "n_sst2_train": len(sst2)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error") == "imdb_unavailable_env_gated":
        return ("UNKNOWN", "UNKNOWN: IMDB unavailable in this env (needs datasets.load_dataset('imdb'); home/remote). Harness correct + ready. " + r.get("note", ""))
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    by = {c["frac"]: c for c in r["curve"]}
    r5 = by.get(0.05, {})
    ratio5 = r5.get("ratio")
    s = ("ratio@5pct=%s (transfer %.4f / scratch %.4f); zero-shot SST-2-on-IMDB F1=%s; curve=%s"
         % (ratio5, r5.get("transfer_f1", 0.0), r5.get("scratch_f1", 0.0), r.get("sst2_only_on_imdb_f1"),
            [(c["frac"], c["scratch_f1"], c["transfer_f1"], c["ratio"]) for c in r["curve"]]))
    if ratio5 is None:
        return ("UNKNOWN", "UNKNOWN: 5pct fraction missing. " + s)
    if ratio5 >= 1.20:
        return ("HARD_PASS", "HARD_PASS: positive cross-domain transfer -- SST-2-pretrained discriminative_perceptron lifts IMDB F1 by >=20pct at 5pct data. Substrate primitive carries discriminative signal across distributional shift (substrate-product generalization). " + s)
    if ratio5 >= 0.95:
        return ("MIDDLE_BAND", "MIDDLE_BAND: neutral/weak transfer (ratio 0.95-1.20 at 5pct) -- SST-2 pretraining neither strongly helps nor hurts IMDB. " + s)
    return ("HARD_FAIL", "HARD_FAIL: negative transfer (ratio <0.95 at 5pct) -- SST-2 pretraining hurts IMDB; the primitive does not generalize across this shift. " + s)


def _selftest():
    f = _feats("great movie loved it")
    assert isinstance(f, list) and len(f) >= 4
    rng = np.random.default_rng(0)
    data = [(_feats("good great love"), 1), (_feats("bad awful hate"), 0)] * 20
    w = _train_perceptron(data, 5, None, rng)
    assert _f1_macro(data, w) > 0.9
    print("[selftest] PASS: crossdomain-transfer (perceptron separates toy sentiment, F1=%.3f)" % _f1_macro(data, w), flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
