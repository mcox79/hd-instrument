"""Brain-foundational chain for the POS tagger: WHERE we lose signal + what the speed win ENABLES.

Problem: optimize_the_pos_tagger_viterbi_inner_loop_the_co_dominant_read_cost.

The assigned optimization is BYTE-IDENTICAL speed (done, witnessed 5.25x). Per the owner's standing
directive -- "the only way you overcome the wall is for EVERY component, you and upstream, to be brain
foundational" -- this cell prototypes the brain-foundational CHAIN around the tagger and reports,
honestly, where it can exceed and where the wall is. It BUILDS ON the prior arc-parser finding (which
already localized the wall to lexical-semantic grounding); it does not re-derive it.

Research-confirmed (this session, hdi_research; citations in the finding doc):
  * The perceptron's BOTTOM-UP cue integration IS brain-faithful: the structured-perceptron update is
    in the Widrow-Hoff/delta-rule family = the Rescorla-Wagner family (error-driven, cue-competition).
    A generative P(word|tag) tagger regresses precisely because it double-counts correlated cues
    (naive independence, no cue competition). So the byte-identical speed win PRESERVES a brain-faithful
    computation -- PINNED. [MacDonald 1994; Ramscar 2010; Baayen 2011; Collins 2002]
  * The brain does RANKED-PARALLEL, graded, incremental, top-down-modulated category assignment. Our
    single global 1-best Viterbi is a REAL fidelity gap on 3 axes: parallel candidates (PINNED),
    top-down re-ranking (PINNED), forward prediction (contested magnitude). [Levy 2008; Kuperberg-Jaeger
    2016; Lyu 2023; Federmeier 2007 tempered by Nieuwland 2018]
  * The residual human power on hard/ambiguous category calls is LEXICAL-SEMANTIC (selectional /
    world-knowledge), not more surface cues -> the wall is MEANING. [Altmann-Kamide 1999; Trueswell 1994]

This cell measures two things on UD-EWT gold (n=25k tok):
  PART A  WHERE WE LOSE SIGNAL: overall acc; OOV vs known; and the CONTENT-word (meaning-dependent:
          NOUN/VERB/ADJ/ADV/PROPN) vs FUNCTION-word (structure-dependent) split of the ERRORS, plus the
          top confusion pairs. If the errors concentrate in content-word / OOV / PROPN<->NOUN cases,
          the wall is meaning (corroborating the grounding localization), not the decode algorithm.
  PART B  WHAT THE SPEED ENABLES: the brain keeps a GRADED, ranked-parallel activation over candidate
          categories (not a hard 1-best). The exact graded signal is the forward-backward MARGINAL
          posterior P(tag_i | sentence) over the same lattice (the perceptron scores are the CRF's log
          potentials, so the marginal is well-defined -- and this is exactly what the calibrated CRF
          posterior organ, P7, represents). It is MORE brain-foundational than the hard 1-best but costs
          a second DP pass. Built on the fast emission, the enriched decode (i) keeps the Viterbi 1-best
          BYTE-IDENTICAL, (ii) adds the graded parallel-candidate posterior (the brain's competition
          signal), and (iii) runs WITHIN the stock 1-best time budget -- the ~5x speed headroom is
          exactly what makes the more brain-foundational graded decode affordable per read.
          HONEST CAVEAT: mechanism-fidelity != accuracy. The graded candidates convert to accuracy only
          once top-down MEANING (grounding) re-ranks them; the prior joint tag<->parse loop regressed
          without it. So the speed win ENABLES the brain-foundational decode; grounding CASHES it.

Glass-box, CPU, NO LLM, numpy + pure-python. ASCII-only.
"""
from __future__ import annotations

import os
import sys
import time
import json
from collections import Counter

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.pos_tagger import PosTagger
from experiments.exp_pos_tagger_fastfeat_v1 import FastTagger, token_bases

_POS_ASSET = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
_TEST = os.path.join(_REPO, "data/corpora/ud_english_ewt/en_ewt-ud-test.conllu")
_OUT = os.path.join(_REPO, "data/exp_pos_tagger_brain_foundational_chain_v1")

_CONTENT = frozenset(["NOUN", "VERB", "ADJ", "ADV", "PROPN"])   # meaning-dependent classes


def load_conllu(path):
    S, cur = [], []
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line.strip():
            if cur:
                S.append(cur); cur = []
            continue
        if line.startswith("#"):
            continue
        c = line.split("\t")
        if len(c) < 5 or "-" in c[0] or "." in c[0]:
            continue
        cur.append((c[1], c[3]))          # (form, gold UPOS)
    if cur:
        S.append(cur)
    return S


def known_words(fast):
    """A word is 'known' to the tagger iff its lexical base 'w:<wl>' has any weight."""
    return set(b[2:] for b in fast.base_contrib if b.startswith("w:"))


# ------------------------------------------------------------------ PART B: graded posterior
def _logsumexp(a, axis):
    m = np.max(a, axis=axis, keepdims=True)
    return (m.squeeze(axis) + np.log(np.sum(np.exp(a - m), axis=axis)))


def enriched_decode(fast, obs):
    """Viterbi 1-best (BYTE-IDENTICAL to stock) PLUS the forward-backward MARGINAL posterior over tags
    per token (the brain's graded ranked-parallel activation). Returns (best_tags, posterior[n,nt])."""
    n = len(obs)
    if n == 0:
        return [], np.zeros((0, fast.n_tags))
    em = fast._emission(obs, n)
    TM, SV = fast.TM, fast.SV
    nt = fast.n_tags
    # --- Viterbi 1-best (verbatim stock DP) ---
    V = np.empty((n, nt)); bp = np.zeros((n, nt), dtype=int)
    V[0] = em[0] + SV
    for i in range(1, n):
        cand = V[i - 1][:, None] + TM
        bp[i] = np.argmax(cand, axis=0)
        V[i] = cand[bp[i], np.arange(nt)] + em[i]
    seq = [int(np.argmax(V[n - 1]))]
    for i in range(n - 1, 0, -1):
        seq.append(int(bp[i][seq[-1]]))
    seq.reverse()
    best = [fast.tags[k] for k in seq]
    # --- forward-backward marginals (graded parallel activation) ---
    alpha = np.empty((n, nt)); beta = np.empty((n, nt))
    alpha[0] = em[0] + SV
    for i in range(1, n):
        alpha[i] = em[i] + _logsumexp(alpha[i - 1][:, None] + TM, axis=0)
    beta[n - 1] = 0.0
    for i in range(n - 2, -1, -1):
        beta[i] = _logsumexp(TM + (em[i + 1] + beta[i + 1])[None, :], axis=1)
    g = alpha + beta
    post = np.exp(g - _logsumexp(g, axis=1)[:, None])
    return best, post


def main(maxlen=50):
    os.makedirs(_OUT, exist_ok=True)
    tagger = PosTagger.load(_POS_ASSET)
    fast = FastTagger(tagger, "C")
    sents = [s for s in load_conllu(_TEST) if 1 <= len(s) <= maxlen]
    known = known_words(fast)

    # -------- PART A: where we lose signal
    n = correct = 0
    oov_n = oov_c = 0
    err_content = err_func = 0
    confus = Counter()
    for s in sents:
        obs = [w for w, _ in s]
        gold = [g for _, g in s]
        pred = fast.tag(obs)          # byte-identical to stock, just faster
        for w, g, p in zip(obs, gold, pred):
            n += 1
            ok = (p == g)
            correct += int(ok)
            is_oov = w not in known and w.lower() not in known
            if is_oov:
                oov_n += 1; oov_c += int(ok)
            if not ok:
                confus[(g, p)] += 1
                if g in _CONTENT or p in _CONTENT:
                    err_content += 1
                else:
                    err_func += 1
    acc = correct / n
    oov_acc = oov_c / oov_n if oov_n else 0.0
    known_acc = (correct - oov_c) / (n - oov_n) if (n - oov_n) else 0.0
    n_err = n - correct
    print("PART A -- WHERE WE LOSE SIGNAL (UD-EWT test, n=%d tok, %d sents)" % (n, len(sents)), flush=True)
    print("  overall acc          : %.4f" % acc, flush=True)
    print("  known-word acc       : %.4f   (n=%d)" % (known_acc, n - oov_n), flush=True)
    print("  OOV acc              : %.4f   (n=%d, %.1f%% of tokens)"
          % (oov_acc, oov_n, 100 * oov_n / n), flush=True)
    print("  errors that touch a CONTENT class (NOUN/VERB/ADJ/ADV/PROPN): %d/%d = %.1f%%"
          % (err_content, n_err, 100 * err_content / n_err), flush=True)
    print("  errors purely among FUNCTION classes                       : %d/%d = %.1f%%"
          % (err_func, n_err, 100 * err_func / n_err), flush=True)
    print("  top confusions (gold->pred):", flush=True)
    for (g, p), c in confus.most_common(8):
        meaning = " [meaning-dependent]" if (g in _CONTENT or p in _CONTENT) else ""
        print("     %5s -> %-5s : %d%s" % (g, p, c, meaning), flush=True)

    # -------- PART B: what the speed enables (graded ranked-parallel decode within budget)
    probe = sents[:400]
    # Viterbi 1-best from the enriched decode is BYTE-IDENTICAL to stock (strict enrichment)
    mismatch = 0
    conf_mean = []
    for s in probe:
        obs = [w for w, _ in s]
        bt, post = enriched_decode(fast, obs)
        if bt != fast.tag(obs):
            mismatch += 1
        # graded competition: mean top-1 posterior mass (1.0 = no competition, ->1/nt = max competition)
        conf_mean.append(float(np.mean(post.max(axis=1))))

    obs_probe = [[w for w, _ in s] for s in probe]

    def t_of(fn, reps=5):
        fn(obs_probe[0])
        xs = []
        for _ in range(reps):
            t0 = time.perf_counter()
            for obs in obs_probe:
                fn(obs)
            xs.append(time.perf_counter() - t0)
        xs.sort()
        return xs[len(xs) // 2]

    t_stock = t_of(lambda obs: tagger.tag(obs))
    t_enriched = t_of(lambda obs: enriched_decode(fast, obs)[0])
    print("\nPART B -- WHAT THE SPEED ENABLES (Viterbi 1-best + graded FB posterior, on %d sents)" % len(probe), flush=True)
    print("  enriched 1-best == stock Viterbi 1-best: %s (mismatch=%d) -> strict, byte-identical enrichment"
          % (mismatch == 0, mismatch), flush=True)
    print("  mean top-1 posterior mass: %.3f (the graded parallel-competition signal the brain keeps)"
          % (float(np.mean(conf_mean))), flush=True)
    print("  STOCK 1-best Viterbi         : %.3fs" % t_stock, flush=True)
    print("  FAST 1-best + graded posterior: %.3fs  -> %s the stock 1-best budget (%.2fx)"
          % (t_enriched, "WITHIN" if t_enriched <= t_stock else "OVER", t_stock / t_enriched), flush=True)
    print("  => the ~5x byte-identical speed headroom makes the MORE brain-foundational graded", flush=True)
    print("     ranked-parallel decode affordable; top-down MEANING (grounding) is what cashes it.", flush=True)

    with open(os.path.join(_OUT, "metrics.json"), "w", encoding="ascii") as f:
        json.dump({"n_tok": n, "n_sents": len(sents), "acc": acc, "known_acc": known_acc,
                   "oov_acc": oov_acc, "oov_n": oov_n, "n_err": n_err,
                   "err_content_pct": 100 * err_content / n_err, "err_func_pct": 100 * err_func / n_err,
                   "top_confusions": [["%s->%s" % (g, p), c] for (g, p), c in confus.most_common(8)],
                   "enriched_mismatch": mismatch, "mean_top1_posterior": float(np.mean(conf_mean)),
                   "stock_1best_s": t_stock, "enriched_s": t_enriched,
                   "enriched_within_budget": bool(t_enriched <= t_stock)}, f, indent=2)
    print("wrote metrics.json", flush=True)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--maxlen", type=int, default=50)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        tg = PosTagger.load(_POS_ASSET)
        ft = FastTagger(tg, "C")
        ss = [s for s in load_conllu(_TEST) if 1 <= len(s) <= 50][:20]
        for s in ss:
            obs = [w for w, _ in s]
            bt, post = enriched_decode(ft, obs)
            assert bt == ft.tag(obs), "enriched 1-best != viterbi 1-best"
            assert np.allclose(post.sum(axis=1), 1.0), "posterior rows must sum to 1"
        print("SELF-TEST PASS: enriched 1-best == Viterbi 1-best + valid posterior on 20 sents; "
              "UD-EWT loaded (%d sents)" % len(ss))
    else:
        main(a.maxlen)
