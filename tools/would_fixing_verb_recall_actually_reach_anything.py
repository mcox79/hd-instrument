"""BEFORE SWAPPING THE VERB GATE: HOW MANY OF THE MISSED VERBS COULD BECOME CREDIT TARGETS AT ALL?

The gate `_is_verblike` misses 3,528 of 8,877 real verbs (recall 0.6026, measured 2026-08-22). The
obvious next move is to swap it for the UD tagger we already own and re-run the wall cell.

BUT `_credit_targets` SKIPS ANY LEMMA ALREADY IN THE OUTCOME LEXICON:

    if in_lexicon(lemma, "outcome"):
        continue        # already grounded / seed-known -> not a novel credit target

So a missed verb only MATTERS if it would survive that filter. And the module docstring says the
light verbs (`be/go/make/give`) are the PRE-REGISTERED wash-out case -- they co-occur with both met
and unmet outcomes and are designed to land GROUNDED_NEUTRAL. The top of the missed list is exactly
those words. If the recall fix mostly admits verbs that are either already-known or designed to wash
out, IT REACHES NOTHING, and the swap is an expensive no-op.

THIS IS THE RESOURCE-ARITHMETIC GUARD CLAUDE.md REQUIRES: check what a change can possibly touch,
at full size, BEFORE paying for it. A cell that cannot succeed is untestable, not negative.

STATED BEFORE RUNNING: if the novel-and-reachable count is small (say under ~15% of misses), the swap
is not worth running and the credit thread retires on arithmetic rather than on another HARD_FAIL.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")

import collections
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from hdlab.consequence_learning_loop import _is_verblike, _tokens, in_lexicon   # noqa: E402
from hdlab.pos_tagger import PosTagger                                          # noqa: E402
from hdlab.reading_grounding_loop import _POS_ASSET                             # noqa: E402
from hdlab.thematic_role_labeler import lemma_verb                              # noqa: E402

N_SENT = 3000


def _sentences(n):
    from hdlab.corpus_registry import CorpusRegistry
    reg = CorpusRegistry()
    out = []
    for name in reg.readable_names():
        h = reg.handles.get(name)
        if h is None:
            continue
        try:
            pool = [s for s in h.pool() if 40 < len(s) < 300]
        except Exception:
            continue
        out.extend(pool[:max(1, n // 8)])
        if len(out) >= n:
            break
    return out[:n]


def main() -> int:
    tagger = PosTagger.load(os.path.join(REPO, "data/frontend_assets", _POS_ASSET))
    sents = _sentences(N_SENT)
    print(f"sentences: {len(sents):,}", flush=True)

    missed_tokens = 0
    missed_lemmas = collections.Counter()
    seen_lemmas = collections.Counter()
    for s in sents:
        toks = _tokens(s)
        if not toks:
            continue
        for tok, tag in zip(toks, tagger.tag(list(toks))):
            if tag != "VERB":
                continue
            (seen_lemmas if _is_verblike(tok) else missed_lemmas)[lemma_verb(tok)] += 1
            if not _is_verblike(tok):
                missed_tokens += 1

    novel = collections.Counter()
    known = collections.Counter()
    for lem, c in missed_lemmas.items():
        (known if in_lexicon(lem, "outcome") else novel)[lem] = c

    n_novel_tok = sum(novel.values())
    print(f"\nmissed VERB tokens: {missed_tokens:,}   distinct missed lemmas: {len(missed_lemmas):,}")
    print(f"\n=== OF THE MISSES, WHAT COULD ACTUALLY BECOME A NEW CREDIT TARGET? ===")
    print(f"    already in the OUTCOME lexicon (skipped anyway): "
          f"{sum(known.values()):,} tokens / {len(known):,} lemmas")
    print(f"    NOVEL -- would become new candidates:            "
          f"{n_novel_tok:,} tokens / {len(novel):,} lemmas")
    print(f"    novel share of misses: {n_novel_tok/max(missed_tokens,1):.1%}")

    print("\n  top NOVEL missed lemmas (what the swap would actually admit):")
    for w, c in novel.most_common(25):
        print(f"      {w:16} {c:5,}")

    # A CONTENT/LIGHT SPLIT, because the design says light verbs are BUILT to wash out.
    LIGHT = {"be", "have", "do", "go", "come", "get", "give", "make", "take", "put", "let",
             "say", "see", "know", "think", "look", "want", "tell", "try", "like", "keep",
             "leave", "find", "feel", "seem", "become", "turn", "bring", "hold", "call"}
    light_tok = sum(c for w, c in novel.items() if w in LIGHT)
    print(f"\n    of the NOVEL misses, LIGHT verbs: {light_tok:,}/{n_novel_tok:,} = "
          f"{light_tok/max(n_novel_tok,1):.1%}")
    print(f"    CONTENT verbs (the ones that could carry outcome meaning): "
          f"{n_novel_tok-light_tok:,} tokens / "
          f"{len([w for w in novel if w not in LIGHT]):,} lemmas")
    print("\n  top NOVEL CONTENT misses -- THIS is the population the swap exists to rescue:")
    for w, c in [(w, c) for w, c in novel.most_common(200) if w not in LIGHT][:25]:
        print(f"      {w:16} {c:5,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
