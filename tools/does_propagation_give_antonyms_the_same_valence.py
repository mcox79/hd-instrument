"""THE ANTONYM TRAP: does propagating valence by SIMILARITY give opposites the SAME value?

THE PREDICTION IS NOT MINE AND IT PREDATES THE MEASUREMENT. notes/SYNTHESIS_grounding_wall_definitive_
2026-08-06.md states that good/bad is not recoverable from text statistics because ANTONYMS ARE
DISTRIBUTIONALLY NEAR-IDENTICAL, and names opposition (OPPOSED_PAIRS) rather than similarity as the
fix. Tonight's seed sweep propagates valence by SIMILARITY ALONE, so it should fail exactly here.
THIS IS A CAN-FAIL TEST OF A STANDING PREDICTION, not a fishing expedition.

SimVerb-3500 ships RELATION LABELS: 111 ANTONYMS, 306 SYNONYMS, 190 COHYPONYMS, 800 HYPER/HYPONYMS,
2093 NONE. So the contrast is GOLD-LABELLED and needs no judgement from me.

WHAT IS MEASURED, per pair (both words covered, and the pair's words NEVER in the seed pool):
  true_dv       abs difference in Warriner valence            -- what the answer IS
  pred_dv       abs difference in PROPAGATED valence          -- what similarity-propagation THINKS
  cos           similarity of the two words in the text space -- the 'distributional twins' claim

THE TRAP IS CONFIRMED IF: antonyms have LARGE true_dv, SMALL pred_dv, and pred_dv does not
distinguish them from synonyms.

TWO POSITIVE CONTROLS, BOTH ABLE TO ABORT THE TEST:
  (A) GOLD CONTROL -- true_dv MUST be much larger for ANTONYMS than SYNONYMS. If Warriner valence
      does not separate SimVerb's own antonym labels, the gold cannot support the question and the
      run REFUSES rather than reporting a null.
  (B) PROPAGATION CONTROL -- propagated valence must correlate with true valence ACROSS ALL WORDS.
      If propagation is broken outright, a failure on antonyms would mean nothing.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import collections
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hdlab.reading_grounding_loop import (        # noqa: E402
    CTX_D, content_words, context_vector_masked, normalize_lemma,
)
from which_norm_dimensions_can_text_recover import (   # noqa: E402
    N_SENT, SEED, _load_norms, _pearson, _rank, _sentences,
)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIMVERB = os.path.join(REPO, "data", "encoder_eval_benchmarks", "simverb3500.txt")
N_SEED_POOL = 2500
K = 25


def main() -> int:
    pairs = []
    with open(SIMVERB, encoding="utf-8") as fh:
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 5:
                pairs.append((p[0].strip().lower(), p[1].strip().lower(), p[4].strip()))
    print(f"SimVerb pairs: {len(pairs)}  (control: first row {pairs[0]})", flush=True)

    sents = _sentences()
    norms = _load_norms()
    val = {w: v["Valence"] for w, v in norms.items() if "Valence" in v}

    by_lemma: dict[str, list[str]] = collections.defaultdict(list)
    for s in sents:
        for w in set(content_words(s)):
            lem = normalize_lemma(w)
            if len(lem) > 2 and len(by_lemma[lem]) < N_SENT:
                by_lemma[lem].append(s)

    covered = {l for l, ss in by_lemma.items() if len(ss) >= N_SENT and l in val}
    test_words = sorted({w for a, b, r in pairs for w in (a, b)} & covered)
    seed_pool = sorted(covered - set(test_words))
    rng = np.random.default_rng(SEED)
    if len(seed_pool) > N_SEED_POOL:
        seed_pool = sorted(rng.choice(seed_pool, size=N_SEED_POOL, replace=False).tolist())
    print(f"covered lemmas {len(covered)} | test words {len(test_words)} | "
          f"seed pool {len(seed_pool)} (DISJOINT: {not set(seed_pool) & set(test_words)})", flush=True)

    vocab = test_words + seed_pool
    print("building profiles ...", flush=True)
    M = np.zeros((len(vocab), CTX_D), dtype=np.float64)
    for i, lem in enumerate(vocab):
        acc = np.zeros(CTX_D, dtype=np.float64)
        for s in by_lemma[lem][:N_SENT]:
            acc += context_vector_masked(s, lem)
        M[i] = acc
    M = (M / np.maximum(np.linalg.norm(M, axis=1, keepdims=True), 1e-12)).astype(np.float32)
    T, S = M[:len(test_words)], M[len(test_words):]

    zseed = np.array([val[w] for w in seed_pool], dtype=np.float64)
    zseed = (zseed - zseed.mean()) / (zseed.std() + 1e-12)
    sims = T @ S.T
    nb = np.argpartition(-sims, K, axis=1)[:, :K]
    pred = {w: float(zseed[nb[i]].mean()) for i, w in enumerate(test_words)}

    true_all = np.array([val[w] for w in test_words], dtype=np.float64)
    true_all = (true_all - true_all.mean()) / (true_all.std() + 1e-12)
    pred_all = np.array([pred[w] for w in test_words], dtype=np.float64)
    ctrl_b = _pearson(_rank(pred_all), _rank(true_all))
    print(f"\n[CONTROL B] propagated vs true valence over {len(test_words)} words: rho {ctrl_b:.4f}",
          flush=True)
    if ctrl_b < 0.10:
        print("REFUSING: propagation itself is not working; a failure on antonyms would mean nothing.")
        return 2

    tv = {w: v for w, v in zip(test_words, true_all)}
    cosidx = {w: i for i, w in enumerate(test_words)}
    rows = collections.defaultdict(list)
    for a, b, rel in pairs:
        if a in tv and b in tv and a != b:
            rows[rel].append((abs(tv[a] - tv[b]), abs(pred[a] - pred[b]),
                              float(T[cosidx[a]] @ T[cosidx[b]])))

    print()
    print(f"{'relation':<18}{'n':>5}{'TRUE dv':>10}{'PRED dv':>10}{'cos':>9}{'rho(true,pred)':>16}")
    print("-" * 68)
    out = {}
    for rel in ("ANTONYMS", "SYNONYMS", "COHYPONYMS", "HYPER/HYPONYMS", "NONE"):
        r = rows.get(rel, [])
        if len(r) < 8:
            print(f"{rel:<18}{len(r):>5}   (too few to read)")
            continue
        t_ = np.array([x[0] for x in r]); p_ = np.array([x[1] for x in r])
        c_ = np.array([x[2] for x in r])
        rho = _pearson(_rank(t_), _rank(p_))
        out[rel] = (len(r), t_.mean(), p_.mean(), c_.mean(), rho)
        print(f"{rel:<18}{len(r):>5}{t_.mean():>10.4f}{p_.mean():>10.4f}{c_.mean():>9.4f}{rho:>16.4f}")

    print()
    if "ANTONYMS" in out and "SYNONYMS" in out:
        a, s = out["ANTONYMS"], out["SYNONYMS"]
        print(f"[CONTROL A -- GOLD] TRUE dv  ANTONYMS {a[1]:.4f} vs SYNONYMS {s[1]:.4f} "
              f"(ratio {a[1]/max(s[1],1e-9):.2f}x)")
        if a[1] < 1.5 * s[1]:
            print("  REFUSING TO READ THE RESULT: the gold does not separate antonyms from synonyms")
            print("  on valence, so this population cannot answer the question.")
            return 2
        print(f"[THE TEST]          PRED dv  ANTONYMS {a[2]:.4f} vs SYNONYMS {s[2]:.4f} "
              f"(ratio {a[2]/max(s[2],1e-9):.2f}x)")
        print(f"[TWINS CLAIM]       cos      ANTONYMS {a[3]:.4f} vs SYNONYMS {s[3]:.4f} "
              f"vs NONE {out.get('NONE',(0,0,0,0,0))[3]:.4f}")
        print(f"[WITHIN ANTONYMS]   rho(true dv, predicted dv) = {a[4]:.4f}  (n={a[0]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
