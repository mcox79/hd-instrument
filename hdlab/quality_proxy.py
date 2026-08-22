"""hdlab/quality_proxy.py -- THE VALIDATED AUTOMATIC QUALITY PROXY for learned (subject, object) facts.

WHAT IT IS. A cheap, glass-box check on whether a fact the substrate learned is likely to mean
anything: the two terms must both appear in one sentence AND within PROXIMITY_WINDOW tokens of each
other, with each match covering at least MIN_STEM_COVERAGE of its token.

WHY IT IS HERE (promoted 2026-08-22, WIRE-or-SHELVE gate). Measured against 100 BLIND human-scored
facts (MEANINGFUL / RELATED / NOISE):

    criterion                          human GOOD   human NOISE   Fisher exact
    same-sentence anywhere (v1/v3)        0.864        0.846        p = 1.0000   <- cannot discriminate
    PROXIMITY WINDOW 6 (this)             0.591        0.244        p = 0.0038   <- separates

It rejects 76% of what a person called noise while keeping 59% of what they called good, and the
result survives Bonferroni correction for all seven tests run against those rows that day. It is the
only quality proxy in this project with a validation against a human judgement.

PROVENANCE, WHICH IS WHY THIS ONE AND NOT ANOTHER. The window was NOT tuned on the human labels: it
comes from corpus structure (median_sentence_len 18 / 3 ~= 6), fixed in
experiments/exp_foundation_validation_harness_v4_proximity_v1.py before any result existed, as the
THIRD repair attempt of that instrument. A graded-count alternative invented while searching reached
only p = 0.1745 corrected and was retired unused (tools/graded_cooccurrence_quality.py).

THE COVERAGE RATIO IS LOAD-BEARING, NOT DECORATION. `_prefix_covers` demands the query explain >= 60%
of the matched token, which kills "com" -> "company" (0.43) while keeping "com" -> "comes" (0.60).
Without it, short terms match long words and counts inflate with vocabulary rather than meaning --
measured on real data at rho -0.1492 between term length and match count.

WHAT A PASS DOES NOT MEAN. This scores the LIKELIHOOD A FACT IS MEANINGFUL, not whether it is true,
and it is a filter rather than an oracle: it discards about 4 in 10 genuinely good facts. It does NOT
retrospectively validate anything that rested on the same-sentence criterion, which is refuted. The
underlying facts remain mostly noise (blind score: 3 MEANINGFUL / 19 RELATED / 78 NOISE).

NON-FORK CONTROL: verification/test_quality_proxy_matches_the_validated_cell.py asserts this module
agrees ITEM-FOR-ITEM with the experiment's own cooccurs_v4 on the real corpus. If the cell changes and
this does not, that witness fails.
"""
from __future__ import annotations

import re
from typing import List, Sequence

# All three constants are PINNED to the validated cell. Changing one invalidates the p = 0.0038
# validation above, which was measured at exactly these values.
PROXIMITY_WINDOW = 6        # median_sentence_len(18) / 3, corpus-derived BEFORE any result existed
MIN_STEM_COVERAGE = 0.6     # "com"->"company" 0.43 rejected; "com"->"comes" 0.60 kept (boundary, >=)
TOKEN_RE = re.compile(r"[A-Za-z']+")


def sentence_tokens(sentence: str) -> List[str]:
    """Tokenise one sentence exactly as the validated cell does."""
    return TOKEN_RE.findall(sentence)


def tokenize_corpus(sentences: Sequence[str]) -> List[List[str]]:
    """Pre-tokenise a corpus once. `is_meaningful_fact` needs TOKEN LISTS, not raw strings --
    passing raw strings silently scores 0 for everything (it iterates characters). That mistake
    produced a 0/100 result during this proxy's own validation and was caught only because the
    landed cell reports a non-zero precision."""
    return [sentence_tokens(s) for s in sentences]


def _prefix_covers(prefix: str, token: str, min_coverage: float = MIN_STEM_COVERAGE) -> bool:
    """True iff `token` starts with `prefix` (case-insensitive) AND `prefix` explains at least
    `min_coverage` of `token`'s characters."""
    tl, pl = token.lower(), prefix.lower()
    if not pl or not tl.startswith(pl):
        return False
    return (len(pl) / len(tl)) >= min_coverage


def _covering_positions(query: str, tokens: Sequence[str],
                        min_coverage: float = MIN_STEM_COVERAGE) -> List[int]:
    return [i for i, t in enumerate(tokens) if _prefix_covers(query, t, min_coverage)]


def is_meaningful_fact(subject: str, obj: str, tokenized_sentences: Sequence[List[str]],
                       window: int = PROXIMITY_WINDOW) -> bool:
    """THE proxy. True iff `subject` and `obj` both occur in one sentence within `window` tokens.

    `tokenized_sentences` must come from `tokenize_corpus`."""
    for tokens in tokenized_sentences:
        sp = _covering_positions(subject, tokens)
        if not sp:
            continue
        op = _covering_positions(obj, tokens)
        if not op:
            continue
        if any(abs(i - j) <= window for i in sp for j in op):
            return True
    return False


def _self_test() -> int:
    ok = True
    corpus = tokenize_corpus([
        "The cat sat quietly on the warm mat by the fire.",
        "A dog barked, and much later in this same long sentence the moon appeared.",
        "Company profits rose sharply this year.",
    ])

    # POSITIVE: near terms in one sentence.
    if not is_meaningful_fact("cat", "mat", corpus):
        print("  FAIL: 'cat'/'mat' are 6 tokens apart and must pass")
        ok = False
    else:
        print("  PASS: near co-occurrence accepted")

    # NEGATIVE: same sentence but far apart -- the whole point of the repair.
    if is_meaningful_fact("dog", "moon", corpus):
        print("  FAIL: 'dog'/'moon' are same-sentence but far apart and must be REJECTED")
        ok = False
    else:
        print("  PASS: distant same-sentence pair rejected (this is what v3 got wrong)")

    # COVERAGE RATIO: the documented boundary cases, both directions.
    if _prefix_covers("com", "company"):
        print("  FAIL: 'com'->'company' (0.43) must be rejected by the coverage ratio")
        ok = False
    elif not _prefix_covers("com", "comes"):
        print("  FAIL: 'com'->'comes' (0.60) must be kept")
        ok = False
    else:
        print("  PASS: coverage ratio rejects 'company', keeps 'comes'")

    # THE TOKENISATION TRAP that produced a 0/100 during validation.
    if is_meaningful_fact("cat", "mat", ["The cat sat on the mat."]):
        print("  FAIL: raw strings must NOT silently score as a match")
        ok = False
    else:
        print("  PASS: raw strings do not silently pass (use tokenize_corpus)")

    print("SELF-TEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    raise SystemExit(_self_test() if "--self-test" in sys.argv else (print(__doc__) or 0))
