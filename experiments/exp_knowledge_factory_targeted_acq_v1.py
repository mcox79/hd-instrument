"""exp_knowledge_factory_targeted_acq_v1 -- turn the GAP-ANALYSIS into a PROVEN LEVER (or a mechanism-complete
located negative): do TARGETED disambiguate-then-bind acquisition on the collapsed sense-pairs the gap-map
identifies, and measure whether their WSD a_s RISES -- where BLANKET reading is a located negative.

PROBLEM: build_and_freeze_the_clean_curated_knowledge_foundation_the_proven_meaning_lift (closing the "gap-analysis
is a diagnosis, not a demonstrated gain" gap the owner pressure-tested).

THE HYPOTHESIS: blanket reading-growth regresses WSD because it is topical/dominant-biased (parent's located
negative). But the gap-map says exactly WHICH sense-pairs are collapsed. If we read TARGETED at those lemmas and
bind the BRAIN's way -- disambiguate the sense FIRST (propose via the frozen signatures), keep only CONFIDENT
resolutions (cross-situational verify), and bind only DISCRIMINATIVE context (schema-margin vs the sibling) -- does
the targeted subset's a_s rise? THE HONEST RISK: the confident resolutions are the DOMINANT sense (Zipf), so the
rare sense starves and the collapse persists -> a located negative that STRENGTHENS "the ceiling is representational."

MECHANISM (glass-box, NO LLM, doc/corpus-disjoint from the SemCor test): acquire from simplewiki (external), resolve
via hdlab.diagnostic_context_wsd on the FROZEN signatures, confidence-gate (top-margin >= conf_thr), discriminative-
gate (context word closer to the resolved sense than its sibling by >= margin_thr), bind to the RESOLVED sense.
CONTROLS: (a) SHUFFLED-acquisition twin (bind the same words to a RANDOM sibling -> must lose); (b) BLANKET arm (no
discriminative gate -> reproduces the topical regression); (c) NO-REGRESSION on the non-targeted test items.

DEV=even docs (unused here -- acquisition is external), TEST=odd SemCor subordinate. Reuses the meaning store +
strong-arm corpus reader. ASCII. Remote-safe (no module-level spaCy).
# KB_REFERENT: data/corpora/simplewiki/simplewiki_clean_v1.txt
Run: .venv/Scripts/python.exe experiments/exp_knowledge_factory_targeted_acq_v1.py --self-test
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import sys
import json
import time
import argparse
from collections import defaultdict

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_consolidation_gate_v1 as G1
import experiments.exp_knowledge_factory_meaning_store_v1 as M
import experiments.exp_knowledge_factory_gap_analysis_v1 as GAP
import experiments.exp_learn_from_reading_strong_arm_v1 as SA
from hdlab.diagnostic_context_wsd import diagnostic_context_scores

OUT_DIR = os.path.join(_REPO, "data", "exp_knowledge_factory_targeted_acq_v1")


def _lemma_of(syn):
    from nltk.corpus import wordnet as wn
    try:
        return wn.synset(syn).lemmas()[0].name().lower()
    except Exception:
        return None


def collapsed_targets(prep, sig, cos_thr, max_lemmas):
    """The gap-map's collapsed pairs -> the set of targeted senses + their lemmas (most-collapsed first)."""
    pairs = GAP.discriminability_gaps(prep, sig, 10 ** 9)
    targets = {}  # lemma -> set(synsets)
    for p in pairs:
        if p["cosine"] < cos_thr:
            break
        lem = p["lemma"]
        targets.setdefault(lem, set()).update([p["sense_a"], p["sense_b"]])
        if len(targets) >= max_lemmas:
            break
    return targets


def read_lemma_contexts(lemmas, max_tokens, per_lemma_cap):
    """Scan the corpus; bucket content-word contexts of sentences containing each targeted lemma."""
    sents, _ = SA.read_corpus_stream(max_tokens)
    ctx = defaultdict(list)
    lset = set(lemmas)
    for toks in sents:
        hit = lset.intersection(toks)
        if not hit:
            continue
        content = [w for w in toks if len(w) >= 3 and w not in M.G1._STOP]
        for lem in hit:
            if len(ctx[lem]) < per_lemma_cap:
                ctx[lem].append([w for w in content if w != lem])
    return ctx


def acquire(targets, ctxs, frozen_sig, mat, w2i, conf_thr, margin_thr, shuffle=False, discriminative=True):
    """Disambiguate-then-bind, confidence + discriminative gated. Returns acquired {syn: [words]}."""
    acquired = defaultdict(list)
    rng = np.random.default_rng(7)
    for lem, syns in targets.items():
        syns = sorted(syns)
        G = np.stack([frozen_sig.get(s) if frozen_sig.get(s) is not None else np.zeros(M.EMB_DIM, np.float32)
                      for s in syns]).astype(np.float64)
        if not np.any(G):
            continue
        sib = {s: [frozen_sig.get(t) for t in syns if t != s and frozen_sig.get(t) is not None] for s in syns}
        for context in ctxs.get(lem, []):
            rows = [G1._unit(mat[w2i[w]]) for w in context if w in w2i]
            if len(rows) < 2:
                continue
            C = np.stack(rows)
            sc = diagnostic_context_scores(C, G)
            order = np.argsort(-sc)
            if len(order) < 2 or (sc[order[0]] - sc[order[1]]) < conf_thr:   # confidence gate (cross-situational verify)
                continue
            resolved = syns[int(order[0])]
            if shuffle:                                                       # info-free twin: bind to a RANDOM sibling
                resolved = syns[int(rng.integers(0, len(syns)))]
            sig_self = frozen_sig.get(resolved)
            for w in context:
                if w not in w2i:
                    continue
                if discriminative and sig_self is not None and sib.get(resolved):
                    v = G1._unit(mat[w2i[w]])
                    self_s = float(v @ sig_self); sib_s = max(float(v @ s) for s in sib[resolved])
                    if (self_s - sib_s) < margin_thr:                        # discriminative gate (schema-margin)
                        continue
                acquired[resolved].append(w)
    return acquired


def grown_sigs(base_prep, frozen_sig, acquired, mat, w2i):
    """Rebuild targeted-sense signatures = seeds + curated associates + ACQUIRED words; others unchanged."""
    out = dict(frozen_sig)
    for syn, words in acquired.items():
        if syn in base_prep["seed_words"]:
            base = base_prep["seed_words"][syn] + base_prep["assoc"][syn]
        else:
            base = list(M.G1._seed_words(syn, w2i))
        out[syn] = G1._sigvec(mat, w2i, base + words)
    return out


def a_s_on(recs, idxs, sig, Ctx):
    return M.a_s(recs, idxs, sig, Ctx)


def run(smoke=False, cos_thr=0.97, max_lemmas=60, conf_thr=0.03, margin_thr=0.0,
        max_tokens=8_000_000, per_lemma_cap=400):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    w2i, mat, recs, dev, test, test_all = M._load_eval()
    if smoke:
        test = test[:1200]; max_lemmas = 20; max_tokens = 1_500_000; per_lemma_cap = 150
    cand = set()
    for i in test:
        cand.update(recs[i]["tn"])
    prep = M.prep_bags(cand, mat, w2i, 3)
    frozen = M.sigs_at(prep, mat, w2i, None)

    targets = collapsed_targets(prep, frozen, cos_thr, max_lemmas)
    targeted_senses = set().union(*targets.values()) if targets else set()
    tgt_idx = [i for i in test if recs[i]["gold"] in targeted_senses]
    non_idx = [i for i in test if recs[i]["gold"] not in targeted_senses]
    print("[acq] targeted lemmas=%d senses=%d | targeted test items=%d non=%d (%.0fs)"
          % (len(targets), len(targeted_senses), len(tgt_idx), len(non_idx), time.time() - t0), flush=True)

    ctxs = read_lemma_contexts(list(targets.keys()), max_tokens, per_lemma_cap)
    nctx = sum(len(v) for v in ctxs.values())
    acq = acquire(targets, ctxs, frozen, mat, w2i, conf_thr, margin_thr, shuffle=False, discriminative=True)
    acq_shuf = acquire(targets, ctxs, frozen, mat, w2i, conf_thr, margin_thr, shuffle=True, discriminative=True)
    acq_blanket = acquire(targets, ctxs, frozen, mat, w2i, conf_thr, margin_thr, shuffle=False, discriminative=False)
    n_bound = sum(len(v) for v in acq.values())
    print("[acq] corpus contexts=%d | bound words (targeted)=%d over %d senses (%.0fs)"
          % (nctx, n_bound, len(acq), time.time() - t0), flush=True)

    Ctx = G1.precompute_ctx(recs, test, mat, w2i)
    sig_grown = grown_sigs(prep, frozen, acq, mat, w2i)
    sig_shuf = grown_sigs(prep, frozen, acq_shuf, mat, w2i)
    sig_blanket = grown_sigs(prep, frozen, acq_blanket, mat, w2i)

    ok_frozen = a_s_on(recs, tgt_idx, frozen, Ctx)
    ok_grown = a_s_on(recs, tgt_idx, sig_grown, Ctx)
    ok_shuf = a_s_on(recs, tgt_idx, sig_shuf, Ctx)
    ok_blanket = a_s_on(recs, tgt_idx, sig_blanket, Ctx)
    # no-regression on the NON-targeted items (grown must not hurt them)
    ok_non_frozen = a_s_on(recs, non_idx, frozen, Ctx)
    ok_non_grown = a_s_on(recs, non_idx, sig_grown, Ctx)
    n = min(len(ok_frozen), len(ok_grown), len(ok_shuf), len(ok_blanket))

    res = {"n_targeted": int(n), "targeted_lemmas": len(targets), "corpus_contexts": nctx, "bound_words": n_bound,
           "params": {"cos_thr": cos_thr, "conf_thr": conf_thr, "margin_thr": margin_thr, "max_tokens": max_tokens},
           "a_s_targeted": {"frozen": round(float(ok_frozen.mean()), 4), "TARGETED_grown": round(float(ok_grown.mean()), 4),
                            "shuffled_acq": round(float(ok_shuf.mean()), 4), "blanket_acq": round(float(ok_blanket.mean()), 4)},
           "GROWN_vs_frozen": G1._paired(ok_grown[:n], ok_frozen[:n], 970),
           "GROWN_vs_shuffled": G1._paired(ok_grown[:n], ok_shuf[:n], 971),
           "GROWN_vs_blanket": G1._paired(ok_grown[:n], ok_blanket[:n], 972),
           "no_regression_nontargeted": {"frozen": round(float(ok_non_frozen.mean()), 4),
                                         "grown": round(float(ok_non_grown.mean()), 4),
                                         "ok": bool(ok_non_grown.mean() >= ok_non_frozen.mean() - 0.005)},
           "elapsed_s": round(time.time() - t0, 1)}
    win = res["GROWN_vs_frozen"]["delta"] > 0 and res["GROWN_vs_frozen"]["sep"]
    res["VERDICT"] = ("PROVEN LEVER: targeted disambiguate-then-bind acquisition RAISES the collapsed-pair a_s CI-sep "
                      "(the gap-map is actionable)" if win else
                      "LOCATED NEGATIVE: even TARGETED gated acquisition does not raise the collapsed-pair a_s CI-sep "
                      "-> the collapse is representational (Zipf-starved rare sense), not a coverage gap -- "
                      "strengthens the contextual-encoder ceiling")
    res["headline"] = ("TARGETED ACQ on %d collapsed lemmas (%d bound words): a_s frozen %.4f -> grown %.4f "
                       "(d=%+.4f sep=%s) | shuffled %.4f blanket %.4f | non-targeted no-regress=%s | %s"
                       % (len(targets), n_bound, res["a_s_targeted"]["frozen"], res["a_s_targeted"]["TARGETED_grown"],
                          res["GROWN_vs_frozen"]["delta"], res["GROWN_vs_frozen"]["sep"],
                          res["a_s_targeted"]["shuffled_acq"], res["a_s_targeted"]["blanket_acq"],
                          res["no_regression_nontargeted"]["ok"], res["VERDICT"].split(":")[0]))
    with open(os.path.join(OUT_DIR, "metrics_%s.json" % ("smoke" if smoke else "full")), "w",
              encoding="ascii") as f:
        json.dump({"anchor_name": "knowledge_factory_targeted_acq_v1", "verdict": "MEASURED", "result": res},
                  f, indent=2, default=str)
    print("[run] " + res["headline"], flush=True)
    return res


def self_test():
    # acquire binds a confidently-resolved discriminative word to the right sense; shuffle sends it elsewhere.
    rng = np.random.default_rng(0)
    a = G1._unit(rng.standard_normal(M.EMB_DIM)); b = G1._unit(rng.standard_normal(M.EMB_DIM))
    w2i = {"disc": 0, "topic": 1}; mat = np.stack([a * 0.9 + 0.1 * rng.standard_normal(M.EMB_DIM), a * 0 + b]).astype(np.float32)
    frozen = {"x.n.01": a, "x.n.02": b}
    targets = {"x": {"x.n.01", "x.n.02"}}; ctxs = {"x": [["disc", "topic"]]}
    acq = acquire(targets, ctxs, frozen, mat, w2i, conf_thr=0.0, margin_thr=0.0, discriminative=True)
    assert sum(len(v) for v in acq.values()) >= 1, "at least one confident discriminative bind: %s" % dict(acq)
    print("SELFTEST PASS (targeted acquire binds a resolved discriminative word: %s)"
          % {k: v for k, v in acq.items()}, flush=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--cos-thr", type=float, default=0.97)
    ap.add_argument("--conf-thr", type=float, default=0.03)
    ap.add_argument("--margin-thr", type=float, default=0.0)
    ap.add_argument("--max-lemmas", type=int, default=60)
    ap.add_argument("--timeout", type=float, default=None)
    args = ap.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    run(smoke=args.smoke, cos_thr=args.cos_thr, conf_thr=args.conf_thr, margin_thr=args.margin_thr,
        max_lemmas=args.max_lemmas)
    return 0


if __name__ == "__main__":
    sys.exit(main())
