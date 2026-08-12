"""Reusable candidate-GENERATION stage for the reader: raw sentence -> UD tokens -> UPOS ->
arc parse -> the SET of (verb, argument-candidate) pairs the parse licenses.

This is the extraction half of the reader-integration pipeline (candidate GENERATION precedes
the Step-2 DECISION vote). It composes the PERSISTED glass-box front-end:
  hdlab.pos_tagger.PosTagger  (UPOS averaged perceptron; loaded, not retrained)
  hdlab.arc_parser.ArcParser  (hashed arc-factored perceptron; loaded, UAS ~0.79, margins exposed)

The parser is UNLABELED, so verb-argument candidates are INFERRED from arc structure + POS:
a nominal (NOUN/PROPN/PRON) that is a dependent of a verb head -- or the antecedent a verb
modifies (relative-clause gap) -- is a candidate patient. This is HEURISTIC and OVER-GENERATES
(it cannot tell subject from object; the Step-2 vote selects among the candidates). It is written
to recover the constructions a crude positional SVO extractor drops: COORDINATION (2nd conjunct's
args), RELATIVE CLAUSES (gapped/overt object), CONTROL/xcomp (embedded verb's object), PRONOUN
objects.

NO LLM. NO nltk. numpy + pure-python only. ASCII-only.

Public API:
  ud_tokenize(text) -> list[str]                       # UD-consistent tokenizer (splits n't / 's clitics)
  CandidateGenerator.load(pos_path, arc_path)          # load persisted front-end
  gen.generate(text) -> CandResult                     # tokens, pos, heads, margins, candidate pairs
  gen.candidates_from_parse(tokens, pos, heads)        # set of (verb_idx, arg_idx) 1-based, with rule tags
"""
from __future__ import annotations

import re
from typing import Dict, List, NamedTuple, Sequence, Set, Tuple

from hdlab.pos_tagger import PosTagger
from hdlab.arc_parser import ArcParser

NOMINAL = {"NOUN", "PROPN", "PRON"}

# ------------------------------------------------------------------------------------------------
# UD-consistent tokenizer. The a2fd38a0 proxy flagged that the old ASCII tokenizer
# re.findall(r"[a-z']+") kept UD clitics (n't / 's) attached -> token-alignment noise on real
# McGuffey. UD-EWT splits: didn't -> did n't ; can't -> ca n't ; cat's -> cat 's ; I'll -> I 'll ;
# cannot -> can not ; punctuation separated.
# ------------------------------------------------------------------------------------------------
_CLITIC_RE = re.compile(r"^(.*?)('s|'re|'ve|'ll|'d|'m)$", re.IGNORECASE)


def ud_tokenize(text: str) -> List[str]:
    """UD-EWT-consistent tokenizer: split clitics + punctuation. ASCII; deterministic."""
    text = text.replace(chr(0x2019), "'").replace(chr(0x2018), "'")
    text = text.replace(chr(0x201c), '"').replace(chr(0x201d), '"')
    # separate punctuation but keep intra-word apostrophe + hyphen
    text = re.sub(r"([^\w\s'\-])", r" \1 ", text)
    # cannot -> can not (UD splits it)
    text = re.sub(r"\b([Cc])annot\b", r"\1an not", text)
    out: List[str] = []
    for t in text.split():
        low = t.lower()
        if low.endswith("n't") and len(t) > 3:
            out.append(t[:-3])
            out.append(t[-3:])
            continue
        m = _CLITIC_RE.match(t)
        if m and len(m.group(1)) > 0:
            out.append(m.group(1))
            out.append(t[len(m.group(1)):])
            continue
        if t.endswith("'") and len(t) > 1:  # trailing possessive apostrophe (boys')
            out.append(t[:-1])
            out.append("'")
            continue
        out.append(t)
    return [w for w in out if w != ""]


class CandResult(NamedTuple):
    tokens: List[str]
    pos: List[str]
    heads: Dict[int, int]              # 1-based dep_idx -> head_idx (0 = ROOT)
    margins: Dict[int, float]          # 1-based dep_idx -> arc confidence margin
    candidates: Set[Tuple[int, int]]   # (verb_idx, arg_idx) 1-based
    cand_rules: Dict[Tuple[int, int], str]  # pair -> which rule fired (core_dep / relcl_gap / coord / conj_obj)


def candidates_from_parse(
    tokens: Sequence[str],
    pos: Sequence[str],
    heads: Dict[int, int],
    extended: bool = True,
) -> Tuple[Set[Tuple[int, int]], Dict[Tuple[int, int], str]]:
    """Infer (verb_idx, nominal-argument_idx) candidate pairs from an UNLABELED parse. 1-based indices.

    CORE rules (always on):
      (a) direct nominal dependent: heads[n] == v         (direct object; also subject -> over-gen)
      (b) relative-clause gap:      heads[v] == n, n nominal (v modifies antecedent n = gapped arg)
    EXTENDED rules (extended=True):
      (c) coordination verb-sharing: v conj-attached to verb h -> share h's nominal deps and vice versa
      (d) conjoined-object grandchild: heads[n] == m (nominal), heads[m] == v -> (v, n)
    Returns (pairs, rule_tag_per_pair). First rule to fire tags the pair.
    """
    n = len(tokens)
    verbs = [i for i in range(1, n + 1) if pos[i - 1] == "VERB"]
    verbset = set(verbs)
    nominals = [i for i in range(1, n + 1) if pos[i - 1] in NOMINAL]
    pairs: Set[Tuple[int, int]] = set()
    rule: Dict[Tuple[int, int], str] = {}

    def add(v: int, a: int, tag: str) -> None:
        key = (v, a)
        if key not in pairs:
            pairs.add(key)
            rule[key] = tag

    for v in verbs:
        for a in nominals:
            if heads.get(a) == v:
                add(v, a, "core_dep")
            if heads.get(v) == a:
                add(v, a, "relcl_gap")

    if extended:
        for v in verbs:
            hv = heads.get(v)
            if hv in verbset and hv != v:      # v is a verbal dependent/conjunct of verb hv
                for a in nominals:
                    if heads.get(a) == hv:
                        add(v, a, "coord")
                    if heads.get(a) == v:
                        add(hv, a, "coord")
        for v in verbs:                        # (d) conjoined-object grandchild
            for a in nominals:
                m = heads.get(a)
                if m is not None and m != 0 and m <= n and pos[m - 1] in NOMINAL and heads.get(m) == v:
                    add(v, a, "conj_obj")
    return pairs, rule


class CandidateGenerator:
    """Composes persisted UPOS tagger + arc parser + UD tokenizer into a candidate-generation stage."""

    def __init__(self, tagger: PosTagger, parser: ArcParser):
        self.tagger = tagger
        self.parser = parser

    @classmethod
    def load(cls, pos_path: str, arc_path: str) -> "CandidateGenerator":
        return cls(PosTagger.load(pos_path), ArcParser.load(arc_path))

    def generate(self, text: str, extended: bool = True) -> CandResult:
        toks = ud_tokenize(text)
        if not toks:
            return CandResult([], [], {}, {}, set(), {})
        pos = self.tagger.tag(toks)
        pr = self.parser.parse(toks, pos)
        cands, rules = candidates_from_parse(toks, pos, pr.heads, extended=extended)
        return CandResult(tokens=list(toks), pos=list(pos), heads=pr.heads, margins=pr.margins,
                          candidates=cands, cand_rules=rules)
