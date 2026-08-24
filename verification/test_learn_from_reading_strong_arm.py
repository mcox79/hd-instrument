"""Scaffold-free witness for does_learning_from_reading_deserve_to_continue.

Recomputes a modest strong-learned-arm model live (a few million tokens, no scaffold) and asserts the
load-bearing invariants the full curve rests on. These are the claims that must hold for the head-to-
head to mean anything; the full run establishes the exact numbers and the flatten-or-climb verdict.

Invariants (all confirmed at smoke scale, asserted here on SimLex, the broad multi-POS benchmark):
  1. THE SURPRISE LEVER IS REAL: PPMI-SVD (surprise-weighted, brain-motivated) beats RAW additive
     co-occurrence (the substrate's shipped mechanism) by a clear margin -- so the strong arm is a
     genuinely different, stronger mechanism, not a 17th weak repeat.
  2. THE INFO-FREE CONTROLS LOSE: random vectors AND a PPMI-SVD model built on a SHUFFLED corpus
     (same marginals, destroyed co-occurrence) both score near zero, well below the real learned arm.
     A winning arm whose info-free twin also won would be an artifact.
  3. THE LEARNED ARM CLEARS THE SPELLING FLOOR on SimLex: PPMI-SVD > orthographic char-ngram
     similarity -- the "spelling beats meaning" result that motivated the brief does NOT survive a
     properly surprise-weighted learned arm on nouns/adjectives.
  4. SUPPLIED STILL WINS THE HEAD-TO-HEAD: the grounded hub (unclamped Lancaster+Brysbaert) beats the
     learned arm -- the brief's direction holds, and the strong learned arm does not overturn it here.
  5. THE FUSION TEST IS GUARDED: replacing the learned channel with NOISE does not help the supplied
     hub (noise+supplied is not a CI-separated gain over supplied alone) -- so any learned+supplied
     gain elsewhere is not a fusion artifact.

Run:  .venv/Scripts/python.exe verification/test_learn_from_reading_strong_arm.py
ASCII-only. Reads the clean simplewiki file directly; no network, no scaffold.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import scipy.sparse as sp

from experiments.exp_learn_from_reading_strong_arm_v1 import (
    read_corpus_stream, build_vocab, build_cooc, ppmi_matrix, idf_weight, svd_vectors,
    sparse_row_cosine_fn, dense_vec_cosine_fn, ortho_sim_fn, random_vec_cosine_fn,
    load_simlex, load_supplied, supplied_sim_fn, score_arm, covered_pairs, score_fusion,
    benchmark_vocab, WINDOW,
)

SEED = 13
BUDGET = 3_000_000
VOCAB_CAP = 25_000
MIN_COUNT = 5
N_BOOT = 250


def _rho(bench, fn, common):
    return score_arm(bench, fn, restrict_pairs=common, n_boot=N_BOOT, n_null=N_BOOT, seed=SEED)["rho"]


def build():
    bench = load_simlex()
    sents, ntok = read_corpus_stream(BUDGET)
    index = build_vocab(sents, benchmark_vocab(bench), VOCAB_CAP, MIN_COUNT)
    cooc = build_cooc(sents, index, WINDOW)
    ppmi = ppmi_matrix(cooc)
    svec = svd_vectors(ppmi, seed=SEED)
    sh = svd_vectors(ppmi_matrix(build_cooc(sents, index, WINDOW, shuffle_seed=SEED + 7)), seed=SEED)
    supplied, _d = load_supplied(full=False)
    arms = {
        "RAW": sparse_row_cosine_fn(cooc, index),
        "PPMI_SVD": dense_vec_cosine_fn(svec, index),
        "PPMI_SVD_SHUFFLED": dense_vec_cosine_fn(sh, index),
        "IDF": sparse_row_cosine_fn(idf_weight(cooc), index),
        "ORTHO": ortho_sim_fn(),
        "RANDOM": random_vec_cosine_fn(index, seed=SEED),
        "SUPPLIED": supplied_sim_fn(supplied),
    }
    common = covered_pairs(bench, arms["PPMI_SVD"]) & covered_pairs(bench, arms["SUPPLIED"])
    return bench, arms, common, ntok


def main():
    bench, arms, common, ntok = build()
    r = {name: _rho(bench, fn, common) for name, fn in arms.items()}
    print("[witness] tokens=%d common_pairs=%d" % (ntok, len(common)))
    for k in ("PPMI_SVD", "RAW", "PPMI_SVD_SHUFFLED", "IDF", "ORTHO", "RANDOM", "SUPPLIED"):
        print("[witness]   %-18s rho=%.4f" % (k, r[k]))

    ok = True

    def check(cond, msg):
        nonlocal ok
        print(("[witness] PASS " if cond else "[witness] FAIL ") + msg)
        ok = ok and cond

    # 1. surprise lever real: PPMI-SVD beats raw additive co-occurrence
    check(r["PPMI_SVD"] > r["RAW"] + 0.03,
          "surprise lever: PPMI_SVD %.4f > RAW %.4f (+0.03)" % (r["PPMI_SVD"], r["RAW"]))
    # 2. info-free controls lose
    check(r["PPMI_SVD"] > r["RANDOM"] + 0.05 and abs(r["RANDOM"]) < 0.05,
          "random info-free loses: PPMI_SVD %.4f vs RANDOM %.4f" % (r["PPMI_SVD"], r["RANDOM"]))
    check(r["PPMI_SVD"] > r["PPMI_SVD_SHUFFLED"] + 0.05 and r["PPMI_SVD_SHUFFLED"] < 0.05,
          "shuffled-corpus twin loses: real %.4f vs shuffled %.4f" % (r["PPMI_SVD"], r["PPMI_SVD_SHUFFLED"]))
    # 3. learned arm clears the spelling floor on SimLex
    check(r["PPMI_SVD"] > r["ORTHO"] + 0.03,
          "clears spelling floor: PPMI_SVD %.4f > ORTHO %.4f" % (r["PPMI_SVD"], r["ORTHO"]))
    # 4. supplied still wins the head-to-head
    check(r["SUPPLIED"] > r["PPMI_SVD"],
          "supplied wins head-to-head: SUPPLIED %.4f > PPMI_SVD %.4f" % (r["SUPPLIED"], r["PPMI_SVD"]))
    # 5. fusion guarded: noise does not help the supplied hub
    noise = score_fusion(bench, arms["RANDOM"], arms["SUPPLIED"], seed=SEED, n_boot=N_BOOT)
    check(noise is not None and not noise["delta_separated"] and noise["delta"] < 0.02,
          "noise+supplied is not a gain over supplied (delta=%.4f, separated=%s)"
          % (noise["delta"], noise["delta_separated"]))

    print("[witness] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
