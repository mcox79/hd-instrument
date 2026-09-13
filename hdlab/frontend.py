"""hdlab/frontend.py -- THE ONE shared reading frontend: categories and heads for every consumer (the reader AND the board arms),
honouring the substrate's organ switches so a brain-foundational upstream rung reaches every downstream consumer at once.

Landed 2026-09-12 (strategy, overnight plan phase 1b/1c): the board's who-did-what / state / causal-typing arms each loaded their
own supervised tagger + parser, so switching the live reader to the BF category organ / attachment arm never reached them (the
board A/B moved only the STATE dim). This module is the single entry point; the arms instantiate `Tagger()` / `Parser()` here.

  HDLAB_TAG_SOURCE    = "counts"     (default; hdlab.lexical_categories: count-based generative category model, graded posterior)
                      | "perceptron" (hdlab.pos_tagger: the NOT_BF max-margin stand-in -- reproduces the pre-2026-09-12 baseline)
  HDLAB_HEADS_SOURCE  = "attachment_arm" (DEFAULT since 2026-09-13; "arceager" = hdlab.arceager_parser, the supervised stand-in, for baselines)
                      | "attachment_arm" (hdlab.attachment_arm: reading-learned cue competition + semantic bootstrapping = the BF rung;
                                          reads the category POSTERIOR when the tagger provides one -- the graded hand-off)
Glass-box; no LLM / spaCy / nltk at inference.
"""
from __future__ import annotations

import os
from typing import Dict, List, NamedTuple, Optional, Sequence

__bf_status__ = "BF_SPIRIT"   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors notes/bf_status_registry.jsonl
__bf_verified__ = ("2026-09-13 strategy (overnight plan 1b/1c): switchboard with no computation of its own -- routes every consumer to the "
                   "category organ (lexical_categories, BF_SPIRIT; perceptron = NOT_BF stand-in) and the heads source (attachment_arm, "
                   "BF_SPIRIT; arceager = supervised stand-in); live default counts + arceager until the attachment arm's board flips are repaired")
__bf_note__ = "the BF status of the frontend is the status of the organs it routes to; the stand-ins remain selectable only for baselines"

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAG_SOURCE = os.environ.get("HDLAB_TAG_SOURCE", "counts")
# DEFAULT FLIPPED 2026-09-13 10:55 local (Q134; owner rule: a more brain-foundational organ replaces the stand-in on the live path;
# downstream dips are consumers to repair): the attachment arm is the reader's governor. Board under it 0.6223 vs stand-in 0.6378 --
# coref/salience/common-noun/wic identical; patient -0.087 and state -0.140 are LABELS-rung reads (the stand-in parser hands them
# ready-made relation labels) -> repaired at the roles rung, not by reverting. "arceager" stays selectable for baselines.
HEADS_SOURCE = os.environ.get("HDLAB_HEADS_SOURCE", "attachment_arm")
_POS_ASSET = os.path.join(_REPO, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json")


import re as _re
_TOKEN_RE = _re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?|[0-9]+(?:[.,][0-9]+)*|[^\sA-Za-z0-9]")


def tokenize(text: str) -> List[str]:
    """The ONE glass-box tokenizer for raw-text entry points (letters with internal apostrophes, numbers, single punctuation marks).
    Board reads take tokens from the corpus files (instrument convention); raw-text paths should converge on this. No nltk/spaCy."""
    return _TOKEN_RE.findall(text)


class ParseOut(NamedTuple):
    heads: Dict[int, int]                       # dep (1-based) -> head (1-based), 0 = ROOT
    margins: Dict[int, float]                   # per dependent: P(best) - P(second) (attachment arm) or the parser's margin
    marginals: Optional[Dict[int, Dict[int, float]]]   # P(head | dep) when available (attachment arm), else None


class Tagger:
    """`.tag(tokens) -> [category]`; `.tag_with_posterior(tokens) -> ([category], [{category: P}] | None)`."""

    def __init__(self, source: Optional[str] = None):
        self.source = source or TAG_SOURCE
        if self.source == "counts":
            from hdlab import lexical_categories as LC
            self._lc = LC.get(); self._pt = None
        else:
            from hdlab.pos_tagger import PosTagger
            self._pt = PosTagger.load(_POS_ASSET, _raw=True); self._lc = None

    def tag(self, tokens: Sequence[str]) -> List[str]:
        toks = list(tokens)
        return self._lc.tag(toks) if self._lc is not None else list(self._pt.tag(toks))

    def tag_with_posterior(self, tokens: Sequence[str]):
        toks = list(tokens)
        if self._lc is not None:
            return self._lc.tag_with_posterior(toks)
        return list(self._pt.tag(toks)), None


class Parser:
    """`.parse(tokens, categories, tag_posterior=None) -> ParseOut` (heads + margins + marginals)."""

    def __init__(self, source: Optional[str] = None):
        self.source = source or HEADS_SOURCE
        if self.source == "attachment_arm":
            from hdlab import attachment_arm as AA
            self._AA = AA; self._tab = AA.load_attachment_validities(); self._ae = None
        else:
            from hdlab.arceager_parser import load_model, parse_with_conf, MODEL_PATH
            self._ae = (load_model(MODEL_PATH), parse_with_conf); self._AA = None

    def parse(self, tokens: Sequence[str], categories: Sequence[str], tag_posterior=None) -> ParseOut:
        toks = list(tokens); pos = list(categories)
        if self._AA is not None:
            # POINT ESTIMATE = A DECODED TREE (2026-09-13 06:30 local). Until now the point head was each word's ARGMAX MARGINAL:
            # better than the MAP tree on every content relation but not a tree (87/300 test sentences had several roots or cycles;
            # root 0.69 vs 0.81). Now the arm's `decode` (MBR tree by default: the single-root tree maximising the summed marginals,
            # with the punctuation convention) gives the point heads; the marginals stay the graded signal; margin = P(head) - P(best other).
            if tag_posterior:
                A, n = self._AA.arc_scores_graded(toks, pos, tag_posterior, self._tab)
            else:
                A, n = self._AA.arc_scores(toks, pos, self._tab)
            heads, post = self._AA.decode(toks, pos, A, n)
            marg: Dict[int, float] = {}
            for j, d in post.items():
                if not d:
                    continue
                h = heads.get(j, 0); ph = float(d.get(h, 0.0))
                alt = max((v for k, v in d.items() if k != h), default=0.0)
                marg[j] = ph - float(alt)
            return ParseOut(dict(heads), marg, post)
        W, pwc = self._ae
        h, cf, mg = pwc(toks, pos, W)
        return ParseOut(dict(h), dict(mg), None)


_T: Optional[Tagger] = None
_P: Optional[Parser] = None


def tagger() -> Tagger:
    global _T
    if _T is None:
        _T = Tagger()
    return _T


def parser() -> Parser:
    global _P
    if _P is None:
        _P = Parser()
    return _P


def describe() -> str:
    return "frontend: categories=%s heads=%s" % (TAG_SOURCE, HEADS_SOURCE)


__all__ = ["tokenize", "Tagger", "Parser", "ParseOut", "tagger", "parser", "describe", "TAG_SOURCE", "HEADS_SOURCE"]
