"""_np_head_signal -- glass-box STRUCTURAL NP-head-consistency signal for the trustworthy abstain gate.

A candidate answer noun is NP-HEAD-CONSISTENT iff, in the passage, it occurs at least once as the HEAD
of its noun phrase -- the RIGHTMOST noun of its contiguous noun-run -- rather than ONLY as a PRE-MODIFIER
(an adjective, a compound-noun modifier, or a proper-noun title preceding a name). The non-head answers
are exactly the residual confabulations the coref-margin + match-conflict gate cannot see:
    "log house"          -> answer "log"  : compound-noun modifier of head "house"
    "Lord Henry"         -> answer "lord" : proper-noun title preceding name head "Henry"
    "the fair young man" -> answer "fair" : adjective preceding head "man"

NP structure is corpus-GENERAL (unlike the McGuffey-tuned coref margin, whose OOD AUC was 0.433), so this
structural signal is DESIGNED TO TRANSFER out-of-domain. It uses ONLY POS tags from the SAME
tokenizer/POS pipeline the reader itself uses (pos_tag_sentence / split_sentences passed in); it NEVER
reads the gold answer (no answer leakage). It is a pure keep/abstain FLAG -- it does not alter any answer.

CONSERVATIVE BIAS (avoids false-abstain): a token is flagged NON-HEAD only when EVERY one of its surface
occurrences is a pre-modifier. If the token appears as a genuine head anywhere in the passage, or does not
appear as a surface token at all (e.g. a coref-resolved head), the signal has NO opinion (consistent).

ASCII-only. Pure functions; no torch/HD/import coupling to the reader (pipeline fns are passed in).
"""
from __future__ import annotations

NOUN_POS = ("NN", "NNS", "NNP", "NNPS")
PROPER_POS = ("NNP", "NNPS")
COMMON_NOUN_POS = ("NN", "NNS")
ADJ_POS = ("JJ", "JJR", "JJS")
_DET_POS = ("DT",)

# Closed class of English HONORIFICS / TITLES that pre-modify a personal name ("Lord Henry" -> head
# "Henry"). Corpus-general (not passage-tuned). Deliberately EXCLUDES noble ranks that routinely head an
# NP on their own ("the duke", "the prince", "the king"): those are flagged as pre-modifiers ONLY by the
# generic rules, never by this title list, so a bare "the duke" head answer is never mis-flagged. Only
# fires in title+PROPER-NAME position (a title directly followed by a proper noun).
TITLES = frozenset({
    "lord", "lady", "sir", "madam", "madame", "mr", "mrs", "miss", "ms", "mister", "master",
    "dr", "doctor", "professor", "prof", "captain", "capt", "major", "colonel", "col",
    "general", "lieutenant", "lt", "sergeant", "sgt", "saint", "dame", "reverend", "rev",
})


def _is_noun(pos):
    return pos in NOUN_POS


def _is_adj(pos):
    return pos in ADJ_POS


def _occurrence_is_head(tagged, i):
    """Is token i the HEAD of its NP (the rightmost noun of its noun-run), or a pre-modifier?
    Glass-box, POS-only, with a title-vs-name distinction:
      - an ADJECTIVE is never a noun head                                    ("fair" in "fair young man")
      - a NOUN whose next token is NOT a noun is the head (rightmost of run)  ("house" before "near")
      - a COMMON-noun pre-modifier of a following noun is a modifier          ("log" in "log house")
      - a PROPER noun followed by a PROPER noun is a multi-token PERSONAL NAME whose parts CO-REFER to
        one entity, so it is head-consistent, UNLESS it is a known TITLE      ("Lord" in "Lord Henry"
        is a modifier; "George" in "George Ellet" is head-consistent)
      - a PROPER noun pre-modifying a following COMMON noun is a modifier     ("New York streets")."""
    surf, low, pos = tagged[i]
    if _is_adj(pos):
        return False
    nxt_pos = tagged[i + 1][2] if (i + 1 < len(tagged)) else None
    nxt_is_noun = nxt_pos in NOUN_POS if nxt_pos is not None else False
    if _is_noun(pos):
        if not nxt_is_noun:
            return True                                  # rightmost noun of the run = head
        if pos in PROPER_POS and nxt_pos in PROPER_POS:
            return low not in TITLES                     # personal-name part = head unless a title
        return False                                     # common-noun compound / title-common modifier
    # non-noun, non-adj surface match (rare): head only if not directly pre-modifying a noun.
    return not nxt_is_noun


def _head_after(tagged, i):
    """Given pre-modifier token i, return the head token string = the last noun of the contiguous
    determiner/adjective/noun run starting at i (before an NP-terminating boundary). None if none."""
    n = len(tagged)
    head = None
    j = i
    while j < n:
        low, pos = tagged[j][1], tagged[j][2]
        if _is_noun(pos):
            head = low
            if not ((j + 1 < n) and _is_noun(tagged[j + 1][2])):
                break                    # this noun is the rightmost of the run -> the head
            j += 1
        elif _is_adj(pos) or pos in _DET_POS:
            j += 1                       # skip a leading adjective / determiner pre-modifier
        else:
            break
    return head


def np_head_status(ans, passage_text, pos_tag_sentence, split_sentences):
    """Return one of {"head", "nonhead", "absent"} for answer token `ans` in `passage_text`.
      head    = `ans` occurs >=1x as an NP head                 -> NP-head-consistent.
      nonhead = `ans` occurs but EVERY occurrence is a pre-modifier -> NOT NP-head-consistent (abstain).
      absent  = `ans` never occurs as a surface token           -> signal has no opinion (consistent).
    pos_tag_sentence(sent) -> list of (surface, low, pos); split_sentences(text) -> list of sentences.
    Uses the SAME pipeline tokenizer/tagger passed in; never inspects any gold."""
    if ans is None:
        return "absent"
    a = str(ans).lower()
    saw = False
    saw_head = False
    for sent in split_sentences(passage_text):
        tagged = pos_tag_sentence(sent)
        for i in range(len(tagged)):
            if tagged[i][1] != a:
                continue
            saw = True
            if _occurrence_is_head(tagged, i):
                saw_head = True
    if not saw:
        return "absent"
    return "head" if saw_head else "nonhead"


def np_head_consistent(ans, passage_text, pos_tag_sentence, split_sentences):
    """True unless `ans` is POSITIVELY detected as an NP non-head (abstain only on positive detection)."""
    return np_head_status(ans, passage_text, pos_tag_sentence, split_sentences) != "nonhead"


def np_head_correction(ans, passage_text, pos_tag_sentence, split_sentences):
    """DIAGNOSTIC ONLY (not gated): if `ans` is a non-head, return the head token that a correct-to-head
    policy would recover (e.g. "log"->"house", "lord"->"henry", "fair"->"man"); else None."""
    if ans is None:
        return None
    a = str(ans).lower()
    for sent in split_sentences(passage_text):
        tagged = pos_tag_sentence(sent)
        for i in range(len(tagged)):
            if tagged[i][1] == a and not _occurrence_is_head(tagged, i):
                h = _head_after(tagged, i)
                if h is not None and h != a:
                    return h
    return None
