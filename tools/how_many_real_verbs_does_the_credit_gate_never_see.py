"""THE CREDIT GATE IS ROLE-BASED, NOT PROXIMITY-BASED. ITS WEAK POINT IS A MORPHOLOGICAL FILTER.

WHY THIS EXISTS, AND IT CORRECTS AN OWNER-FACING QUESTION. Board Q104 says the system decides which
word a consequence belongs to "by looking at a window of a few nearby sentences". READ AT THE SOURCE,
THAT IS WRONG. `hdlab/consequence_learning_loop._credit_targets` bounds each verb's OWN CLAUSE,
extracts the PRE-VERB SUBJECT NP-head and the POST-VERB OBJECT NP-head, and credits the verb only if
one of them LINKS to the goal referent. The window is the SEARCH SCOPE; the DECISION RULE is already
who-did-what-to-whom. Confirmed at runtime, not by reading:

    "the girl stumbled badly and the man laughed loudly"
        referent=girl -> ['stumble']      referent=man -> ['laugh']

Proximity would have credited both to whichever was nearer. It does not.

SO THE REAL EXPOSURE IS UPSTREAM OF THE ROLE LOGIC. A verb only reaches that logic if `_is_verblike`
accepts it, and that gate is PURELY MORPHOLOGICAL:

    lemma_verb(tok) != tok or tok.endswith(("ed", "ing"))

Its own docstring names the cost -- "a rare base-form or non-lemmatized irregular verb with no
-ed/-ing (e.g. bare 'praise', irregular 'wept') is missed". The second probe sentence above hit it by
accident: referent=girl in "the man shouted and then the girl wept quietly" returns [] -- `wept` is
invisible. A verb the gate never sees CANNOT be credited by any downstream rule, however good.

WHAT THIS MEASURES: the gate's RECALL and PRECISION against an INDEPENDENT detector -- the UD-EWT
POS tagger already loaded on the live path (`data/frontend_assets/`). Independent matters: scoring a
morphological heuristic with another morphological heuristic would share its blind spot, which is
this repo's most-repeated failure.

STATED BEFORE RUNNING SO IT CAN FAIL: if recall is high (>0.9), the gate is not the bottleneck and
this line is closed. If recall is low, a fixable MISSING PRIMITIVE sits upstream of the wall, and
that is a BUILD, not a ceiling.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")

import collections
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from hdlab.consequence_learning_loop import _is_verblike, _tokens   # noqa: E402
from hdlab.pos_tagger import PosTagger                              # noqa: E402
from hdlab.reading_grounding_loop import _POS_ASSET                 # noqa: E402

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

    tp = fp = fn = tn = 0
    missed = collections.Counter()
    caught_nonverb = collections.Counter()
    acc_tags = collections.Counter()
    for s in sents:
        toks = _tokens(s)
        if not toks:
            continue
        tags = tagger.tag(list(toks))
        for tok, tag in zip(toks, tags):
            is_verb = (tag == "VERB")
            passes = _is_verblike(tok)
            if is_verb and passes:
                tp += 1
            elif is_verb and not passes:
                fn += 1
                missed[tok] += 1
            elif not is_verb and passes:
                fp += 1
                caught_nonverb[tok] += 1
                acc_tags[tag] += 1
            else:
                tn += 1

    tot_verbs = tp + fn
    print(f"\ntokens scored: {tp+fp+fn+tn:,}   UD-VERB tokens: {tot_verbs:,}")
    if tot_verbs < 200:
        print("REFUSING: too few verbs to read a rate.")
        return 2
    rec = tp / tot_verbs
    prec = tp / max(tp + fp, 1)
    print(f"\n=== THE MORPHOLOGICAL GATE vs AN INDEPENDENT TAGGER ===")
    print(f"    RECALL    (real verbs the gate SEES)      = {rec:.4f}   ({tp:,}/{tot_verbs:,})")
    print(f"    MISSED    (real verbs it NEVER sees)      = {1-rec:.4f}   ({fn:,})")
    print(f"    PRECISION (things it accepts that ARE verbs) = {prec:.4f}   ({tp:,}/{tp+fp:,})")
    print(f"    non-verbs wrongly accepted                = {fp:,}")

    # HONESTY CHECK ON THE PRECISION NUMBER. UD tags copulas/auxiliaries as AUX, not VERB, so a raw
    # "non-verb" count would blame the gate for a TAGSET CONVENTION. Broken out rather than quoted.
    print("\n  what the gate ACCEPTS that UD does not call VERB -- BY TAG:")
    for t, c in acc_tags.most_common(8):
        print(f"      {t:8} {c:6,}")
    aux = acc_tags.get("AUX", 0)
    print(f"    AUX share of those: {aux:,}/{fp:,} = {aux/max(fp,1):.1%}"
          f"  -> precision EXCLUDING the AUX convention = {tp/max(tp+fp-aux,1):.4f}")
    print("    (AUX are verbs in the everyday sense, but 'was'/'is' carry no OUTCOME semantics, so")
    print("     accepting them is still noise FOR THIS PURPOSE -- just not a tagging error.)")

    print("\n  most-missed real verbs (invisible to credit assignment, any downstream rule):")
    for w, c in missed.most_common(20):
        print(f"      {w:16} {c:5,}")
    print("\n  most-common NON-verbs the gate accepts (noise it feeds forward):")
    for w, c in caught_nonverb.most_common(12):
        print(f"      {w:16} {c:5,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
