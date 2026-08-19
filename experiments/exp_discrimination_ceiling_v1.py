"""RETRIEVAL IS NOT THE PROBLEM; DISCRIMINATION IS. Measured properly, with intervals.

WHY THIS CELL. Scratch probes on 2026-08-19 found that a related word sits in the top 50 of a
plain co-occurrence count list for **78.7%** of words (random 16.7%) while top-1 is only 0.150 --
so the information is present and the read-out cannot select it. They also found that **raw counts
beat every representation this project owns at every depth**, and that a textbook unsupervised
normalisation (Dice) lifts top-1 by **+31% relative** on the same candidate set. Those probes had
no confidence intervals, one corpus, and about 31 items separating the best arm from the
incumbent. **This cell is the same measurement with intervals, paired tests, and more than one
corpus, so the finding can be cited instead of merely acted on.**

THE MEASUREMENT IS DELIBERATELY SPLIT IN TWO, because they answer different questions:
  RETRIEVAL     hit@k over the whole vocabulary. Is the answer anywhere in reach?
  DISCRIMINATION re-rank the SAME top-50 candidate set. Given that it is in reach, can we pick it?
*Holding the candidate set fixed is what makes the second number attributable to the ranker rather
than to the retrieval step.*

ARMS (all unsupervised, all glass-box, all from the same counts)
  RAW           the co-occurrence count -- the incumbent, and the thing to beat
  DICE          2c/(f(a)+f(b))
  NPMI          normalised pointwise mutual information
  BAG_COSINE    cosine between full co-occurrence profiles -- what our SEMANTIC route computes
  SECOND_ORDER  cosine between profiles restricted to shared neighbours
  RANDOM        floor
  ORACLE        ceiling diagnostic on the re-rank set. NEVER a capability.

GOLD: `data/conceptnet_gold_v1`, provenance-filtered, no WordNet-sourced edge, paradigmatic
relations only. **Independent of the corpus and of every mechanism here.**

PRE-COMMITTED READINGS, before any number:
  (i)   DICE beats RAW CI-separated on the paired test, on BOTH corpora -> a real, free,
        unsupervised gain the pipeline was not taking. Wire it.
  (ii)  DICE beats RAW on one corpus only -> corpus-specific; report as such, do not wire.
  (iii) BAG_COSINE or SECOND_ORDER beats RAW -> our accumulate/project machinery earns its keep
        after all, and today's five-instrument conclusion is wrong.
  (iv)  every arm ties -> the ranker is not where the loss is, and the 75.6% unexplained
        discrimination needs a different kind of feature entirely.

*** (v) ADDED AFTER THE SMOKE, BEFORE THE FULL RUN, BECAUSE THE SMOKE SAID SO: THE DICE GAIN MAY
BE SCALE-DEPENDENT. *** At 3,000 sentences DICE reads 0.1577 against RAW's 0.1541 with **p = 1.0 --
no effect at all**, where the original probe (a table built from ~737,000 parsed sentences) showed
+31%. Retrieval hit@50 was likewise 0.481 here against 0.787 there. **So the full run reads at a
much larger scale, and if DICE only helps once the counts are dense, THAT IS THE FINDING and it
must be reported as a scale threshold rather than as a free win.** *Recorded here rather than
discovered afterwards: a gain that appears only at scale and is quoted without the scale is the
same defect as a floor quoted without its representation.*

Run: python experiments/exp_discrimination_ceiling_v1.py --mode smoke
     python experiments/exp_discrimination_ceiling_v1.py --mode full
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import collections
import json
import math
import sys
import time
from typing import Dict, List, Sequence

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for _p in (_REPO, os.path.join(_REPO, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from exp_checkpoint import completed_units, load_units, record_unit, unit_key

from hdlab.corpus_registry import CorpusRegistry
from hdlab.reading_grounding_loop import content_lemmas

CELL = "exp_discrimination_ceiling_v1"
OUTPUT_DIR = os.path.join(_REPO, "data", CELL)
SPEC = "v1"
PARA = {"/r/IsA", "/r/Synonym", "/r/SimilarTo", "/r/DefinedAs", "/r/PartOf", "/r/MadeOf",
        "/r/HasA"}
KS = (1, 5, 10, 25, 50, 100)
TOPK = 50
N_BOOT = 2000
N_PERM = 2000


def load_gold() -> Dict[str, set]:
    nb: Dict[str, set] = collections.defaultdict(set)
    with open(os.path.join(_REPO, "data", "conceptnet_gold_v1", "edges.jsonl"),
              encoding="utf-8") as fh:
        for line in fh:
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            if e["rel"] in PARA:
                nb[e["subj"]].add(e["obj"])
                nb[e["obj"]].add(e["subj"])
    return nb


def _ci(x: np.ndarray, rng):
    if x.size == 0:
        return (float("nan"),) * 3
    idx = rng.integers(0, x.size, size=(N_BOOT, x.size))
    m = x[idx].mean(axis=1)
    lo, hi = np.percentile(m, [2.5, 97.5])
    return float(lo), float(hi), float((hi - lo) / 2.0)


def _perm(a: np.ndarray, b: np.ndarray, rng) -> float:
    d = a - b
    obs = abs(d.mean())
    fl = rng.integers(0, 2, size=(N_PERM, d.size)) * 2 - 1
    return float((np.sum(np.abs((fl * d).mean(axis=1)) >= obs) + 1) / (N_PERM + 1))


def _run(corpus: str, n_sent: int, vocab_cap: int, gold: Dict[str, set]) -> dict:
    t0 = time.time()
    reg = CorpusRegistry(max_sentences_per_corpus=max(n_sent + 1000, 20000))
    if corpus not in reg.handles:
        raise SystemExit(f"corpus {corpus!r} not on the shelf")
    sents = reg.handles[corpus].take(n_sent)
    df = collections.Counter()
    toks = []
    for s in sents:
        ls = content_lemmas(s)
        toks.append(ls)
        df.update(set(ls))
    vocab = [w for w, _ in df.most_common(vocab_cap) if w in gold]
    vi = {w: i for i, w in enumerate(vocab)}
    n = len(vocab)
    if n < 50:
        return {"corpus": corpus, "error": "vocabulary too small", "n_vocab": n}

    C = np.zeros((n, n), dtype=np.float64)
    for ls in toks:
        ids = sorted({vi[w] for w in ls if w in vi})
        for a in ids:
            for b in ids:
                if a != b:
                    C[a, b] += 1.0
    freq = C.sum(axis=1) + 1e-9
    total = C.sum() + 1e-9
    Cn = C / (np.linalg.norm(C, axis=1, keepdims=True) + 1e-12)
    rng = np.random.default_rng(20260819)

    scorable = [i for i, w in enumerate(vocab)
                if {x for x in gold.get(w, ()) if x in vi and x != w}]
    out: dict = {"corpus": corpus, "n_sentences": len(sents), "n_vocab": n,
                 "n_scorable": len(scorable), "seconds": 0.0}

    # -- RETRIEVAL: hit@k over the whole vocabulary ------------------------------------------
    def hitk(score_row):
        per = {k: [] for k in KS}
        for i in scorable:
            s = score_row(i).copy()
            s[i] = -np.inf
            order = np.argsort(-s)[:max(KS)]
            g = gold[vocab[i]]
            ranks = [r for r, j in enumerate(order) if vocab[j] in g]
            first = ranks[0] + 1 if ranks else 10 ** 9
            for k in KS:
                per[k].append(int(first <= k))
        return {f"hit@{k}": float(np.mean(per[k])) for k in KS}

    out["retrieval"] = {
        "RAW": hitk(lambda i: C[i]),
        "BAG_COSINE": hitk(lambda i: Cn[i] @ Cn.T),
        "RANDOM": hitk(lambda i: rng.random(n)),
    }

    # -- DISCRIMINATION: re-rank the SAME top-50 candidate set --------------------------------
    arms = ("RAW", "DICE", "NPMI", "BAG_COSINE", "SECOND_ORDER", "RANDOM")
    per_item: Dict[str, List[int]] = {a: [] for a in arms}
    n_inpool = 0
    for i in scorable:
        row = C[i].copy()
        row[i] = -np.inf
        cand = [j for j in np.argsort(-row)[:TOPK] if C[i, j] > 0]
        if not cand:
            continue
        g = gold[vocab[i]]
        if not any(vocab[j] in g for j in cand):
            continue
        n_inpool += 1
        cnt = np.array([C[i, j] for j in cand])
        dice = np.array([2 * C[i, j] / (freq[i] + freq[j]) for j in cand])
        npmi = np.array([
            math.log((C[i, j] * total) / (freq[i] * freq[j]) + 1e-12)
            / (-math.log(C[i, j] / total + 1e-12) + 1e-12) for j in cand])
        bagc = np.array([float(Cn[i] @ Cn[j]) for j in cand])
        sec = np.array([float((Cn[i] * Cn[j]).sum()) for j in cand])
        rnd = rng.random(len(cand))
        for a, s in (("RAW", cnt), ("DICE", dice), ("NPMI", npmi), ("BAG_COSINE", bagc),
                     ("SECOND_ORDER", sec), ("RANDOM", rnd)):
            per_item[a].append(int(vocab[cand[int(np.argmax(s))]] in g))

    disc: dict = {"n_in_pool": n_inpool, "ORACLE_ceiling_diagnostic": 1.0}
    vecs = {a: np.asarray(v, dtype=np.float64) for a, v in per_item.items()}
    for a, x in vecs.items():
        lo, hi, hw = _ci(x, rng)
        disc[a] = {"hit@1": float(x.mean()) if x.size else None, "hits": int(x.sum()),
                   "n": int(x.size), "ci_lo": lo, "ci_hi": hi, "ci_half_width": hw}
    for a in arms:
        if a != "RAW" and vecs[a].size:
            disc[a]["paired_perm_p_vs_RAW"] = _perm(vecs[a], vecs["RAW"], rng)
            disc[a]["delta_vs_RAW"] = float(vecs[a].mean() - vecs["RAW"].mean())
    out["discrimination"] = disc
    out["seconds"] = round(time.time() - t0, 1)
    print("  %-22s vocab %4d  scorable %4d  inpool %4d | RETRIEVAL RAW hit@50 %.3f | "
          "DISC RAW %.4f DICE %.4f (p=%s)"
          % (corpus, n, len(scorable), n_inpool,
             out["retrieval"]["RAW"]["hit@50"], disc["RAW"]["hit@1"], disc["DICE"]["hit@1"],
             round(disc["DICE"].get("paired_perm_p_vs_RAW", float("nan")), 4)), flush=True)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("smoke", "full"), default="smoke")
    a = ap.parse_args()
    smoke = a.mode == "smoke"
    corpora = ("simplewiki",) if smoke else ("simplewiki", "onestop", "mcguffey_graded", "arc")
    # 150,000 sentences in full mode, not 25,000. The smoke measured the effect vanishing at
    # 3,000, and the probe that motivated this cell used a table built from ~737,000 -- so a run
    # at 25,000 would most likely have reported a null that was a statement about corpus size.
    n_sent = 3000 if smoke else 150000
    vocab_cap = 800 if smoke else 2500

    gold = load_gold()
    print(f"[gold] {len(gold)} terms with a paradigmatic edge", flush=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    done = completed_units(OUTPUT_DIR) if not smoke else set()
    t0 = time.time()
    for corpus in corpora:
        key = unit_key(SPEC, a.mode, corpus)
        if key in done:
            print(f"[skip] {key}", flush=True)
            continue
        print(f"[run ] {key}", flush=True)
        try:
            r = _run(corpus, n_sent, vocab_cap, gold)
        except SystemExit as e:
            print(f"  SKIP {corpus}: {e}", flush=True)
            continue
        r["unit_key"] = key
        if smoke:
            print(json.dumps(r, indent=2, default=str)[:2200])
        else:
            record_unit(OUTPUT_DIR, key, r)
    if smoke:
        print("SMOKE OK")
        return 0
    units = load_units(OUTPUT_DIR)
    metrics = {
        "cell": CELL, "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "run_mode": "full", "spec": SPEC, "n_units": len(units),
        "gold": "data/conceptnet_gold_v1, provenance-filtered, NO WordNet source, paradigmatic only",
        "items_predate_mechanism": True,
        "design_note": ("RETRIEVAL and DISCRIMINATION are reported separately. The discrimination "
                        "arms re-rank the SAME top-50 candidate set, so any difference is "
                        "attributable to the ranker and not to retrieval."),
        "units": units,
    }
    path = os.path.join(OUTPUT_DIR, "metrics.json")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        json.dump(metrics, fh, indent=2, default=str)
    os.replace(tmp, path)
    print(f"[done] {len(units)} units in {time.time() - t0:.0f}s -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
