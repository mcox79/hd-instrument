"""Witness for hdlab.conceptual_meaning (landed 2026-08-27, consolidation phase).

Self-contained construction proof of the ATL conceptual/definitional meaning hub (no external similarity gold).
On WordNet directly: SYNONYM / near-synonym pairs (a dog IS a kind of ...) score FAR above UNRELATED pairs, the
gain requires the CORRECT definition (an info-free twin -- comparing a word's definitional bag to a RANDOM other
word's -- LOSES), and the distinctive-feature IDF operation is active (a generic gloss token carries less weight
than a distinctive one; the weighted channel differs from the unweighted ATL WRONG-OP). Glass-box: similarity()
takes no gold, returns None out-of-vocabulary, and is a cosine in [0,1]. The off-WordNet human-gold validation
(SimLex/SimVerb vs steelmanned GloVe, the double dissociation) is the solver's test_conceptual_meaning_channel.py.

First run builds + caches the global IDF (one pass over all WordNet synsets, ~30-60s); later runs load the cache.
"""
from __future__ import annotations

import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hdlab.conceptual_meaning import ConceptualChannel, load_or_build_idf  # noqa: E402

SYN = [("car", "automobile", "N"), ("couch", "sofa", "N"), ("physician", "doctor", "N"),
       ("stone", "rock", "N"), ("infant", "baby", "N")]
UNREL = [("car", "justice", "N"), ("sofa", "physics", "N"), ("doctor", "asphalt", "N"),
         ("stone", "melody", "N"), ("infant", "algebra", "N")]


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else float("nan")


def main() -> int:
    idf, nsyn = load_or_build_idf()   # build+cache on first use
    assert nsyn > 50_000, f"global IDF built over too few synsets ({nsyn}) -- WordNet data missing?"
    chan = ConceptualChannel(idf=idf)                       # weighted = distinctive-feature IDF (default)
    unw = ConceptualChannel(idf=idf, weighted=False)        # ATL WRONG-OP: unweighted feature overlap

    # [1] SYNONYMS score FAR above UNRELATED (the organ computes definitional-identity similarity)
    syn_sims = [chan.similarity(a, p, b, p) for a, b, p in SYN]
    unrel_sims = [chan.similarity(a, p, b, p) for a, b, p in UNREL]
    m_syn, m_unrel = _mean(syn_sims), _mean(unrel_sims)
    print(f"[1] synonyms mean={m_syn:.3f}  unrelated mean={m_unrel:.3f}  (margin {m_syn - m_unrel:+.3f})")
    assert all(s is not None for s in syn_sims), f"a synonym pair was OOV: {list(zip(SYN, syn_sims))}"
    assert m_syn > 0.30, f"synonyms should score high, got {m_syn:.3f}"
    assert m_syn - m_unrel > 0.20, f"synonym-vs-unrelated separation too small ({m_syn - m_unrel:.3f})"

    # [2] INFO-FREE TWIN loses: compare each synonym's FIRST word to a RANDOM unrelated word's bag
    twin = [chan.similarity(a, p, ub, p) for (a, _b, p), (_ua, ub, _up) in zip(SYN, UNREL)]
    m_twin = _mean(twin)
    print(f"[2] info-free twin (real word vs a random other word's definition) mean={m_twin:.3f} "
          f"(must lose to synonyms {m_syn:.3f})")
    assert m_twin < m_syn - 0.20, "[witness] the twin did not lose -> the signal is not definitional matching"

    # [3] GLASS-BOX: no gold in the signature; OOV -> None; cosine in [0,1]
    params = list(inspect.signature(chan.similarity).parameters)
    assert "gold" not in params and "labels" not in params, params
    oov = chan.similarity("qwertzuiop", "N", "car", "N")
    assert oov is None, f"an out-of-vocabulary word must return None, got {oov}"
    assert all(0.0 - 1e-9 <= s <= 1.0 + 1e-9 for s in syn_sims + unrel_sims), "cosine must lie in [0,1]"
    print(f"[3] glass-box PASS (no gold in signature; OOV -> None; cosines in [0,1])")

    # [4] the DISTINCTIVE-FEATURE (IDF) op is active: a generic gloss token weighs LESS than a distinctive one,
    #     and the weighted channel differs from the unweighted ATL WRONG-OP.
    vals = sorted(idf.values())
    median = vals[len(vals) // 2]
    generic = idf.get("large")           # 'large' appears in many glosses -> generic -> LOW idf
    assert generic is not None and generic < median, \
        f"a generic token ('large') should have below-median IDF (got {generic}, median {median:.3f})"
    diff = [abs((chan.similarity(a, p, b, p) or 0.0) - (unw.similarity(a, p, b, p) or 0.0)) for a, b, p in SYN]
    assert max(diff) > 1e-6, "the IDF weighting is inert (weighted == unweighted) -- the op is not applied"
    print(f"[4] distinctive-feature op PASS (generic 'large' idf={generic:.3f} < median {median:.3f}; "
          f"weighted != unweighted, max|d|={max(diff):.3f})")

    print("\nALL WITNESS ASSERTIONS PASSED -- the conceptual/definitional channel scores synonyms far above")
    print("unrelated pairs (the info-free twin loses), privileges distinctive features via IDF, and is a")
    print("glass-box cosine over WordNet definitional-feature bags.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
