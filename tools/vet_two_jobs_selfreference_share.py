"""VET the load-bearing masked-vs-unmasked finding by adding the arm it is missing.

THE CLAIM UNDER TEST (notes/ONE_REPRESENTATION_TWO_OPPOSITE_JOBS_...md, and board Q102 rests on it):
masked hit@1 0.1417 vs unmasked 0.4750, chance 0.0167 -- "identification needs the word PRESENT".

THE GAP. That note SAYS the unmasked arm is "inflated by self-reference" and does not QUANTIFY it.
It matters, because earlier the same night the form channel scored hit@1 = 1.0000 for exactly one
reason: the query WAS the answer. If the unmasked arm's advantage is entirely the target token's own
identical vector, then 0.4750 is that same artifact wearing different clothes, and the 3.4x is a real
number compared against an artifact rather than against a rival.

THE ARM THAT SETTLES IT is the complement of the masked one:
    MASKED       context WITHOUT the target tokens   (what the live path stores)
    UNMASKED     context WITH them                   (masked + target)
    TARGET_ONLY  the target tokens and NOTHING else  <- pure self-reference ceiling
If TARGET_ONLY >= UNMASKED, the unmasked arm carries no identification signal beyond the word's own
vector, and "identification needs the word present" is a lookup, not a representation doing a job.

GATE ON REPRODUCTION FIRST. If MASKED and UNMASKED do not land near 0.1417 / 0.4750, the setup is
not the note's setup and NOTHING here may be compared to it. That is reported, not worked around.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import collections
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hdlab.reading_grounding_loop import (        # noqa: E402
    CTX_D, content_words, context_vector, context_vector_masked, normalize_lemma,
)

N_LEMMAS = 60
N_SENT = 41
SEED = 7


def _sentences(limit: int = 60000) -> list[str]:
    """Sentences off the real shelf. FAILURES ARE PRINTED, NOT SWALLOWED -- the first version of
    this function caught every exception and returned an empty list, which reported as 'too few
    sentences' and hid the actual cause (a wrong API guess)."""
    from hdlab.corpus_registry import CorpusRegistry
    reg = CorpusRegistry()
    out: list[str] = []
    for name in reg.readable_names():
        h = reg.handles.get(name)
        if h is None:
            continue
        try:
            pool = h.pool()
        except Exception as exc:
            print(f"  [{name}] pool() failed: {type(exc).__name__}: {exc}", flush=True)
            continue
        n0 = len(out)
        for s in pool:
            if 40 < len(s) < 400:
                out.append(s)
            if len(out) >= limit:
                print(f"  [{name}] +{len(out) - n0} (limit reached)", flush=True)
                return out
        if len(out) > n0:
            print(f"  [{name}] +{len(out) - n0}", flush=True)
    return out


def main() -> int:
    sents = _sentences()
    print(f"corpus sentences: {len(sents)}", flush=True)
    if len(sents) < 5000:
        print("REFUSING: too few sentences to select 60 lemmas x 41 -- not the note's population.")
        return 2

    # lemma -> sentences containing it, so every arm sees the SAME (lemma, sentence) pairs.
    by_lemma: dict[str, list[str]] = collections.defaultdict(list)
    for s in sents:
        for w in set(content_words(s)):
            lem = normalize_lemma(w)
            if len(lem) > 2 and len(by_lemma[lem]) < N_SENT:
                by_lemma[lem].append(s)

    eligible = sorted(k for k, v in by_lemma.items() if len(v) >= N_SENT)
    print(f"lemmas with >= {N_SENT} sentences: {len(eligible)}", flush=True)
    if len(eligible) < N_LEMMAS:
        print("REFUSING: fewer than 60 eligible lemmas -- cannot match the note's shape.")
        return 2
    rng = np.random.default_rng(SEED)
    lemmas = sorted(rng.choice(eligible, size=N_LEMMAS, replace=False).tolist())

    def target_only_vec(sent: str, lem: str) -> np.ndarray:
        """EXACTLY the complement of context_vector_masked: only the tokens it removes."""
        kept = [w for w in content_words(sent) if normalize_lemma(w) == lem]
        return context_vector(" ".join(kept), d=CTX_D)

    arms = {
        "MASKED": lambda s, l: context_vector_masked(s, l),
        "UNMASKED": lambda s, l: context_vector_masked(s, "__never_matches__"),
        "TARGET_ONLY": target_only_vec,
    }

    results = {}
    for arm, fn in arms.items():
        vecs = {l: [fn(s, l) for s in by_lemma[l][:N_SENT]] for l in lemmas}
        # LEAVE-ONE-OUT: profile = sum of the lemma's OTHER sentences, so the query is never in it.
        sums = {l: np.sum(vecs[l], axis=0) for l in lemmas}
        hit = tot = 0
        within: list[float] = []
        cross: list[float] = []
        for l in lemmas:
            for i, q in enumerate(vecs[l]):
                qn = np.linalg.norm(q)
                if qn == 0:
                    continue
                best, best_c = None, -2.0
                for m in lemmas:
                    prof = sums[m] - (q if m == l else 0)
                    pn = np.linalg.norm(prof)
                    if pn == 0:
                        continue
                    c = float(np.dot(q, prof) / (qn * pn))
                    (within if m == l else cross).append(c)
                    if c > best_c:
                        best_c, best = c, m
                tot += 1
                hit += int(best == l)
        results[arm] = {"hit@1": hit / max(1, tot), "n": tot,
                        "within": float(np.mean(within)) if within else 0.0,
                        "cross": float(np.mean(cross)) if cross else 0.0}
        r = results[arm]
        print(f"  {arm:12} hit@1={r['hit@1']:.4f}  n={r['n']}  "
              f"within={r['within']:.4f} cross={r['cross']:.4f}", flush=True)

    print(f"\nchance = {1.0 / N_LEMMAS:.4f}")
    m, u, t = (results[k]["hit@1"] for k in ("MASKED", "UNMASKED", "TARGET_ONLY"))
    print(f"MASKED {m:.4f} | UNMASKED {u:.4f} | TARGET_ONLY {t:.4f}")
    print(f"\nreproduction check vs the note (0.1417 / 0.4750):")
    print(f"  MASKED   delta = {m - 0.1417:+.4f}")
    print(f"  UNMASKED delta = {u - 0.4750:+.4f}")
    print(f"\nSELF-REFERENCE SHARE of the unmasked arm: TARGET_ONLY / UNMASKED = "
          f"{(t / u if u else float('nan')):.3f}")
    if t >= u:
        print("  => THE TARGET TOKEN ALONE MATCHES OR BEATS THE FULL UNMASKED ARM.")
        print("     The unmasked advantage is self-reference; context adds nothing on top.")
    else:
        print("  => the unmasked arm beats target-only, so context contributes beyond the word.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
