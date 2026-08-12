"""Glass-box sentence-completeness checker -- graded, over the front-end parse.

Reader input-validation component. Rides on the persisted front-end
(hdlab.pos_tagger + hdlab.arc_parser); it does NOT rebuild them. Input = raw
tokens; pipeline = pos_tagger.tag -> arc_parser.parse -> an INSPECTABLE
completeness rule that emits a completeness TYPE + a GRADED confidence.

Brain grounding (2-3 sentences, credited):
  A well-formed clause satisfies the PREDICATION requirement -- a SUBJECT bound
  to a FINITE predicate (Chomsky's Extended Projection Principle; the copula
  supplies finiteness when the predicate is nominal/adjectival). A fragment
  "feels unfinished" because sentence WRAP-UP / clause-boundary closure never
  arrives (garden-path & wrap-up reading-time work, Just & Carpenter 1980;
  Warren et al.). But the brain does GOOD-ENOUGH processing (Ferreira 2003):
  in context it ACCEPTS fragments (dialogue, headlines, elliptical answers).
  So this checker is GRADED (a confidence, not a hard binary reject) and
  emits IMPERATIVE as a first-class COMPLETE type (subjectless by design).

Glass-box: every decision is a named rule over the POS + arc structure we HAVE.
The parser is UNLABELED for arcs, so subject/finiteness are inferred
HEURISTICALLY from POS + surface verb-form + arc geometry; this is the main
risk and is reported honestly, not hidden.

Public API:
  CompletenessChecker.from_assets(tagger_path, parser_path) -> checker
  checker.check(tokens) -> CompletenessResult
  classify_completeness(tokens, pos_tags, parse_result, margin_floor=None) -> CompletenessResult

NO LLM. NO nltk. numpy + pure-python only (via the front-end). ASCII-only.
"""
from __future__ import annotations

from typing import Dict, List, NamedTuple, Optional, Sequence

# ---- glass-box lexica (small, inspectable closed sets) --------------------

# Finite auxiliary / copula / modal surface forms (incl. clitics). Presence of
# one of these as (or under) the root makes the clause tensed/finite.
FINITE_AUX = frozenset([
    "is", "are", "am", "was", "were", "'s", "'re", "'m",
    "has", "have", "had", "'ve", "'d",
    "do", "does", "did", "'ll", "will", "wo",  # wo = "wo n't"
    "would", "can", "could", "shall", "should", "may", "might", "must",
    "ai",  # ai = "ai n't"
])

# Non-finite verb/aux forms that must NOT count as a finite head on their own.
NONFINITE_WORDS = frozenset(["be", "been", "being"])

# Common irregular finite past forms (surface has no -ed marker).
IRREGULAR_PAST = frozenset([
    "went", "saw", "came", "took", "made", "said", "got", "gave", "found",
    "told", "became", "left", "felt", "brought", "began", "kept", "held",
    "wrote", "stood", "heard", "let", "meant", "set", "met", "ran", "paid",
    "sat", "spoke", "lost", "sent", "built", "understood", "drew", "broke",
    "spent", "rose", "drove", "bought", "wore", "chose", "grew", "flew",
    "knew", "threw", "fell", "led", "read", "put", "cut", "hit", "shut",
])

NOMINAL_POS = frozenset(["NOUN", "PROPN", "PRON"])
# tokens allowed to precede an imperative verb (leading conj/adverbial/etc.)
PRE_IMPERATIVE_POS = frozenset(["CCONJ", "SCONJ", "ADV", "INTJ", "PUNCT", "PART"])


class CompletenessResult(NamedTuple):
    type: str                 # COMPLETE_CLAUSE | IMPERATIVE | FRAGMENT
    confidence: float         # graded [0,1] confidence in the assigned type
    is_complete: bool         # COMPLETE_CLAUSE or IMPERATIVE
    reasons: List[str]        # inspectable rule trace (glass-box)
    root_idx: int             # 1-based index of the parse root (0 if none)
    root_pos: str
    root_form: str
    has_subject: bool
    is_finite: bool
    finite_kind: str          # which finiteness rule fired
    root_margin: float        # parser head-score margin at the root token
    margin_corroborates: bool # low root margin corroborates a fragment flag
    signals: Dict[str, object]


def _deps_of(head_idx: int, heads: Dict[int, int]) -> List[int]:
    """1-based dep indices whose head is head_idx."""
    return [d for d, h in heads.items() if h == head_idx]


def _root_finiteness(root_idx, tokens, pos, heads):
    """Return (finite_kind, is_finite, has_finite_aux_child). Heuristic over POS+form."""
    n = len(tokens)
    rform = tokens[root_idx - 1].lower()
    rpos = pos[root_idx - 1]
    prev = tokens[root_idx - 2].lower() if root_idx - 2 >= 0 else None
    aux_children = [d for d in _deps_of(root_idx, heads) if pos[d - 1] == "AUX"]
    fin_aux = any(tokens[d - 1].lower() in FINITE_AUX for d in aux_children)

    # Non-verbal root: complete only if a finite COPULA sits before it (cop-drop UD style).
    if rpos not in ("VERB", "AUX"):
        cop = [d for d in aux_children if tokens[d - 1].lower() in FINITE_AUX and d < root_idx]
        if cop:
            return ("copular_finite", True, True)
        return ("nonverbal_no_cop", False, False)

    # Verbal root.
    if prev == "to":
        return ("to_infinitive", False, False)
    if fin_aux:
        return ("finite_via_aux", True, True)   # progressive/perfect/passive: is/has/was/'re + Vform
    if rform in FINITE_AUX:
        return ("finite_aux_root", True, False)
    if rform in NONFINITE_WORDS:
        return ("nonfinite_be", False, False)
    if rform.endswith("ing"):
        return ("gerund_participle", False, False)
    if rform in IRREGULAR_PAST:
        return ("finite_irregular_past", True, False)
    if rform.endswith("ed") or rform.endswith("en"):
        return ("finite_past_or_participle", True, False)  # noisy: participle w/o aux misreads as finite
    if rform.endswith("s") and len(rform) > 2 and not rform.endswith("ss"):
        return ("finite_3sg", True, False)
    return ("base_form", False, False)          # infinitive OR imperative -- decided by classify


def _has_competing_finite_clause(root_idx, tokens, pos, heads):
    """A non-root finite predicate that has its OWN pre-verbal subject -> fragment/garble signal."""
    for i in range(1, len(tokens) + 1):
        if i == root_idx:
            continue
        if pos[i - 1] != "VERB":
            continue
        aux_children = [d for d in _deps_of(i, heads) if pos[d - 1] == "AUX"]
        fin = any(tokens[d - 1].lower() in FINITE_AUX for d in aux_children)
        f = tokens[i - 1].lower()
        fin = fin or f in FINITE_AUX or f in IRREGULAR_PAST or f.endswith("ed") \
            or (f.endswith("s") and len(f) > 2 and not f.endswith("ss"))
        if not fin:
            continue
        subj = [d for d in _deps_of(i, heads) if pos[d - 1] in NOMINAL_POS and d < i]
        if subj:
            return True
    return False


def classify_completeness(
    tokens: Sequence[str],
    pos_tags: Sequence[str],
    parse_result,
    margin_floor: Optional[float] = None,
) -> CompletenessResult:
    """Glass-box completeness classification over a front-end ParseResult."""
    tokens = list(tokens)
    pos = list(pos_tags)
    heads = dict(parse_result.heads)
    margins = dict(parse_result.margins)
    reasons: List[str] = []

    roots = [i for i in range(1, len(tokens) + 1) if heads.get(i, -1) == 0]
    any_verb = any(p in ("VERB", "AUX") for p in pos)

    if not roots:
        reasons.append("no parse root (head-0) found")
        return CompletenessResult("FRAGMENT", 0.85, False, reasons, 0, "", "",
                                  False, False, "no_root", 0.0, False,
                                  {"any_verb": any_verb, "n_roots": 0})

    # Prefer a VERB/AUX root if the greedy parse produced several head-0 tokens.
    verb_roots = [r for r in roots if pos[r - 1] in ("VERB", "AUX")]
    root_idx = verb_roots[0] if verb_roots else roots[0]
    if len(roots) > 1:
        reasons.append("multi-root parse (%d) -> weak structure" % len(roots))
    root_pos = pos[root_idx - 1]
    root_form = tokens[root_idx - 1]
    root_margin = float(margins.get(root_idx, 0.0))

    # Subject inference (unlabeled parser): a pre-root nominal dependent of the root.
    subj = [d for d in _deps_of(root_idx, heads)
            if pos[d - 1] in NOMINAL_POS and d < root_idx]
    has_subject = len(subj) > 0
    if has_subject:
        reasons.append("subject inferred: pre-root nominal dep '%s'" % tokens[subj[0] - 1])

    finite_kind, is_finite, _fin_aux = _root_finiteness(root_idx, tokens, pos, heads)

    # Subject licenses finiteness (standard predication): a VERB root bound to an
    # overt pre-root nominal subject IS a finite clause, even when surface
    # morphology is opaque (irregular pasts 'sang'/'ran' etc.). Guarded against
    # genuinely non-finite roots (to-infinitive / bare gerund / 'be').
    nonfinite_marked = finite_kind in ("to_infinitive", "gerund_participle", "nonfinite_be")
    if (not is_finite) and has_subject and root_pos == "VERB" and not nonfinite_marked:
        is_finite = True
        finite_kind = finite_kind + "+subject_licensed"
        reasons.append("subject-licensed finiteness (overt subject binds verb root)")
    reasons.append("root '%s'/%s finiteness=%s (finite=%s)"
                   % (root_form, root_pos, finite_kind, is_finite))

    # Imperative: sentence-initial base-form VERB, no subject, not a to-infinitive.
    lead_ok = all(pos[j] in PRE_IMPERATIVE_POS for j in range(root_idx - 1))
    imperative = (root_pos == "VERB" and finite_kind == "base_form"
                  and not has_subject and lead_ok)
    # do-support emphatic imperative: "do/does/did" root, no subject, with a base
    # VERB dependent ("do tell me") -> imperative, not a subjectless-finite fragment.
    if (not imperative and not has_subject and lead_ok
            and root_form.lower() in ("do", "does", "did")
            and any(pos[d - 1] == "VERB" for d in _deps_of(root_idx, heads))):
        imperative = True
        reasons.append("do-support emphatic imperative (do/did + base verb)")

    competing = _has_competing_finite_clause(root_idx, tokens, pos, heads)

    if imperative:
        typ, is_complete, conf = "IMPERATIVE", True, 0.75
        reasons.append("imperative: initial base-form verb, no overt subject")
        if competing:
            conf = 0.45
            reasons.append("competing finite clause present -> possible fragment/garble (ambiguous)")
    elif is_finite and has_subject:
        typ, is_complete, conf = "COMPLETE_CLAUSE", True, 0.90
        reasons.append("predication satisfied: finite predicate + subject")
    elif is_finite and not has_subject:
        typ, is_complete, conf = "FRAGMENT", False, 0.55
        reasons.append("finite predicate but NO subject (subordinate/elliptical -> graded fragment)")
    else:
        typ, is_complete = "FRAGMENT", False
        conf = 0.90 if not any_verb else 0.70
        reasons.append("no finite predicate at root%s" % ("" if any_verb else " (no verb at all)"))

    # Independent margin signal: low root margin corroborates a fragment flag.
    margin_corroborates = False
    if margin_floor is not None and root_margin < margin_floor:
        margin_corroborates = True
        reasons.append("low parse margin (%.3f < %.3f) corroborates weak structure"
                       % (root_margin, margin_floor))
        if not is_complete:
            conf = min(1.0, conf + 0.05)

    signals = {
        "any_verb": any_verb, "n_roots": len(roots), "lead_ok": lead_ok,
        "competing_finite_clause": competing, "n_subj_candidates": len(subj),
    }
    return CompletenessResult(typ, round(conf, 3), is_complete, reasons, root_idx,
                              root_pos, root_form, has_subject, is_finite,
                              finite_kind, root_margin, margin_corroborates, signals)


class CompletenessChecker:
    """Loads the front-end assets once and exposes check(tokens)."""

    def __init__(self, tagger, parser, margin_floor: Optional[float] = None):
        self.tagger = tagger
        self.parser = parser
        self.margin_floor = margin_floor

    @classmethod
    def from_assets(cls, tagger_path: str, parser_path: str,
                    margin_floor: Optional[float] = None) -> "CompletenessChecker":
        from hdlab.pos_tagger import PosTagger
        from hdlab.arc_parser import ArcParser
        return cls(PosTagger.load(tagger_path), ArcParser.load(parser_path), margin_floor)

    def check(self, tokens: Sequence[str]) -> CompletenessResult:
        tokens = list(tokens)
        pos = self.tagger.tag(tokens)
        parse = self.parser.parse(tokens, pos)
        return classify_completeness(tokens, pos, parse, self.margin_floor)
