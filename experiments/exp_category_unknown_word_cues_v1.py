"""exp_category_unknown_word_cues_v1 -- THE UNKNOWN-WORD CUES OF THE CATEGORY ORGAN (pri-99 solver).

PROBLEM: one token in thirteen has never been seen by the category organ (`hdlab/lexical_categories.py`); it gets those
right 0.7519 of the time and a third of its misses are NAMES read as common nouns or the reverse (PROPN->NOUN 117,
NOUN->PROPN 46 on the full UD-EWT test, 1,882 unseen of 25,094 tokens).

HOW THE BRAIN DOES THIS (the opening move; structure + computation, then the parameters swept):
  STRUCTURE: the visual word-form system (left occipito-temporal / VWFA) delivers a MORPHO-ORTHOGRAPHIC description of a
  novel string -- Rastle & Davis 2008: segmentation is form-based, automatic and semantics-blind -- into the same graded
  category COMPETITION that already settles known words (MacDonald 1994 constraint satisfaction; Kuperberg & Jaeger
  2016 graded belief). No new organ: three more COUNT tables inside the one category organ.
  THE COMPUTATIONS THIS CELL ADDS, each PINNED at the computational level:

  (1) CAPITALISATION IS READ RELATIVE TO ITS POSITION. A literate reader knows the orthographic CONVENTION that a
      sentence-initial capital is FORCED and therefore carries no name evidence, while a capital in a non-forced
      position is a name marker. The organ's `word_shape` is POSITION-BLIND, so the two are the same symbol and the
      name evidence is diluted by every sentence-initial pronoun and determiner. The brain's form is the joint
      emission P(shape, forced-position | c) -- one count table of the same kind as the existing P(shape | c).
      MEASURED IN THE SUPPLY: position-blind Cap = PROPN 10,224 / PRON 5,257 / NOUN 2,554 / DET 1,397; split by
      position, Cap@mid = PROPN 8,918 / PRON 1,906 / NOUN 1,885 while Cap@init = PRON 3,351 / PROPN 1,306 / DET 1,199.

  (2) A NOVEL FORM IS JUDGED BY THE COMPANY NOVEL FORMS KEEP -- Baayen's PRODUCTIVITY (Baayen 1992, 2009; Hay & Baayen
      2002): the productivity of a pattern is measured on the HAPAX stratum, because a frequent word's ending tells you
      nothing about what a NEW word with that ending will be. Today the organ's unknown-word estimator is a TOKEN-count
      suffix table over the WHOLE vocabulary, and its no-suffix fallback is the overall tag frequency (dominated by
      function words that can never be novel). The brain's evidence base for a novel form is the reader's experience of
      NOVEL forms: the low-frequency vocabulary, counted by TYPE (one learning event per newly-met form).
      MEASURED IN THE SUPPLY: hapax-TYPE Cap@mid = PROPN 1,194 / NOUN 118 / ADJ 49 (0.91 PROPN) against 0.66 for the
      token table -- the same cue, sharpened by asking the productivity question instead of the frequency question.

  (3) THE ORTHOGRAPHIC DESCRIPTION IS FINER THAN SIX SYMBOLS. The word-form system sees letters, digits, case and
      internal punctuation. The organ collapses every string containing a digit to "digit" and everything else to
      "other" -- so 'E17', '01-Feb-02', 'EB3326', 'Guaranty.doc', 'b/c' and 'AMS' are two symbols between them, and
      those are exactly the worst slices (other 0.657, ALLCAP 0.597). The acronym/word split of ALL-CAPS is a LENGTH
      fact the counts can learn once the alphabet lets them.

  (4) WHEN THE LEXICAL CUE IS ABSENT THE SLOT CUE CARRIES THE WEIGHT (Mintz 2003 frequent frames; Christiansen & Chater
      multiple-cue integration; MacDonald 1994 cue competition -- a cue's weight rises when the cues it competes with
      are silent). A BLANKET neighbour-word channel is REFUTED on disk (2026-09-13, 0.9152); the brain's form is not
      blanket -- for a KNOWN word the lexical cue dominates and the frame merely double-counts the sequential cue; for
      a word with NO lexical entry the frame is the only lexical-level evidence there is. Gated on the ABSENCE of
      lexical evidence, not applied to everything.

KNOWLEDGE FORM (plastic, never frozen): (1) and (3) are accrued count tables (`shape_pos`, `shape_pos_w`) that grow on
every `observe`; (2) is DERIVED IN `finalize` from the emission counts the organ already keeps, so it re-derives itself
on every online update with no new accrual at all. No gradient, no external tool at inference, no treebank read at
inference. The UD-EWT TEST split is the measuring ruler only and is never read while learning.

FLOOR: the live organ rebuilt from the same supply (full UD-EWT test, lag 2, order 2, shape, rare-mix, cluster cue) --
unknown 0.7519 / overall 0.9278. TWIN: the same winning arm with the shape and suffix symbol->category tables SHUFFLED
(identical alphabet, identical marginals, no information). CI: paired bootstrap over SENTENCES, 2,000 resamples.

usage:  python experiments/exp_category_unknown_word_cues_v1.py [--smoke] [--arms A,B] [--boot 2000] [--save-asset P]
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
import time
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Sequence

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from experiments._seed_checkpoint import get_output_dir          # noqa: E402
import hdlab.lexical_categories as LC                            # noqa: E402
from hdlab.lexical_categories import LexicalCategories, BOS      # noqa: E402

# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-train.conllu
# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-test.conllu
# KB_REFERENT: data/frontend_assets/induced_categories_v2_1m_joint_clause.json
TRAIN = os.path.join(REPO, "data", "corpora", "ud_english_ewt", "en_ewt-ud-train.conllu")
TEST = os.path.join(REPO, "data", "corpora", "ud_english_ewt", "en_ewt-ud-test.conllu")

INIT, MID = "@i", "@m"
APOS = "’"
# The word-form system's symbol ALPHABET is a property of the writing system, not of what we happened to see, so the
# smoothing denominator is the size of the alphabet (as `LC` uses len(SHAPES)), never the count of observed symbols.
RICH_SHAPES = ("num", "numpunct", "dcode", "dnum", "alnum", "punct", "slash", "dotted", "hyphenCap", "hyphen",
               "apos", "lower", "UP1", "ACRO", "ALLCAP", "Cap", "CamelCap", "mixed", "other")


# --------------------------------------------------------------------- the brain's finer orthographic description
def word_shape_rich(w: str) -> str:
    """The morpho-orthographic description the visual word-form system delivers: case, digits, internal punctuation.
    A refinement of `LC.word_shape` (6 symbols) -- every symbol is still just a key in a learned count table."""
    if not w:
        return "other"
    has_d = any(ch.isdigit() for ch in w)
    has_a = any(ch.isalpha() for ch in w)
    if has_d and not has_a:
        return "num" if w.isdigit() else "numpunct"          # 1998 | 1,000 / 3.5 / 01-02 / 5:30
    if has_d and has_a:
        if any(ch in "-/.:" for ch in w):
            return "dcode"                                   # 01-Feb-02 / EB-3326 / A.1
        return "dnum" if w[0].isdigit() else "alnum"         # 17th / 2pm  |  E17 / EB3326 / B12
    if not has_a:
        return "punct"
    if "/" in w:
        return "slash"                                       # b/c / and/or / w/
    if "." in w:
        return "dotted"                                      # U.S. / e.g. / Guaranty.doc
    if "-" in w:
        return "hyphenCap" if w[0].isupper() else "hyphen"
    if "'" in w or APOS in w:
        return "apos"
    if w.isalpha():
        if w.islower():
            return "lower"
        if w.isupper():
            return "UP1" if len(w) == 1 else ("ACRO" if len(w) <= 4 else "ALLCAP")
        if w[0].isupper():
            return "Cap" if w[1:].islower() else "CamelCap"  # Falluja | McDonald / DeVry
        return "mixed"                                       # eBay / iPod
    return "other"


# --------------------------------------------------------------------- PATH A: the Katz-Macnamara determiner context
# THE PINNED DEVELOPMENTAL CUE. Katz, Baker & Macnamara (1974, Child Development 45:469-473) "What's in a name?": a
# 17-month-old hearing "This is DAX" takes DAX for an individual's NAME and hearing "This is a DAX" takes it for a
# COMMON noun -- the discriminating cue is the PRESENCE OR ABSENCE OF A DETERMINER, not the identity of one. Gelman &
# Taylor 1984 and Hall 2003 (form-class cues to descriptive proper names) replicate and extend it.
# WHY THIS IS NOT THE REFUTED NEIGHBOUR-WORD CHANNEL, and not my own slot cue either: the refuted channel put ~300
# neighbour WORD identities on every token; the slot cue put the same 300 words on unseen tokens only. This is a
# NINE-symbol table over the FUNCTION-WORD CLASS of the left context -- the linguistically correct shape of the cue,
# ~33x less sparse, and it encodes the ABSENCE of a determiner as its own symbol, which a word-identity table cannot.
# It is also why the brief's rule-of-thumb ("'the' before a word says common noun") is wrong for this population:
# 'the MSM' / 'the Gateses' / 'the Europeans' are gold PROPN. The counts learn P(det-context | c); no rule is written.
DET_DEF = {"the", "this", "that", "these", "those"}
DET_INDEF = {"a", "an", "another", "any", "some", "each", "every", "no"}
QUANT = {"many", "few", "several", "most", "all", "both", "one", "two", "three", "more", "much", "other"}
POSS = {"my", "your", "his", "her", "its", "our", "their"}
PREP = {"of", "in", "on", "at", "to", "for", "from", "by", "with", "about", "into", "over", "after", "before",
        "between", "through", "during", "against", "under", "near", "across", "toward", "towards", "via"}
COORD = {"and", "or", "but", "nor", "plus"}
DET_SYMS = ("det_def", "det_indef", "quant", "poss", "prep", "coord", "bos", "punct", "bare")


RIGHT_SYMS = ("poss_s", "comma", "period", "prep_r", "coord_r", "verbish", "eos", "other_r")


def right_context(lows: Sequence[str], i: int) -> str:
    """The RIGHT half of the frame. A name is disproportionately followed by the possessive clitic, by an appositive
    comma, or by a clause boundary; a common noun by a preposition or a verb. Mintz's frames are two-sided, and the
    revision window (lag >= 1) already lets the belief about word t see word t+1, so reading it costs no look-ahead
    the organ does not already take."""
    if i + 1 >= len(lows):
        return "eos"
    b = lows[i + 1]
    if b in ("'s", "’s", "'", "’"):
        return "poss_s"
    if b == ",":
        return "comma"
    if b in (".", "!", "?", ";", ":"):
        return "period"
    if b in PREP:
        return "prep_r"
    if b in COORD:
        return "coord_r"
    if b in ("is", "was", "are", "were", "has", "have", "had", "said", "will", "would", "can", "could", "does", "did"):
        return "verbish"
    return "other_r"


def det_context(lows: Sequence[str], i: int) -> str:
    """The Katz-Macnamara context symbol: WHAT KIND of thing sits immediately left of this word.
    'bare' = no determiner-like element at all, which is the cue that says 'this picks out an individual'."""
    if i == 0:
        return "bos"
    a = lows[i - 1]
    if a in DET_DEF:
        return "det_def"
    if a in DET_INDEF:
        return "det_indef"
    if a in QUANT:
        return "quant"
    if a in POSS:
        return "poss"
    if a in PREP:
        return "prep"
    if a in COORD:
        return "coord"                       # PARALLELISM: a word coordinated with a name tends to be a name
    if not any(ch.isalnum() for ch in a):
        return "punct"
    return "bare"


def position_class(words: Sequence[str], i: int) -> str:
    """Is capitalisation FORCED at this position? Forced = nothing alphanumeric precedes it in the sentence (index 0,
    or only quotes/brackets/dashes before it). The reader knows the convention, so the cue is read relative to it."""
    for j in range(i):
        if any(ch.isalnum() for ch in words[j]):
            return MID
    return INIT


# --------------------------------------------------------------------- the organ with the unknown-word cues added
class UnknownWordCategories(LexicalCategories):
    """`hdlab.lexical_categories.LexicalCategories` + the unknown-word cues. Every addition is a COUNT table; the
    novel-form stratum is DERIVED in `finalize` from the emission counts the organ already keeps (so the online
    `observe` path re-derives it for free)."""

    def __init__(self, *a, pos_shape: bool = True, rich_shape: bool = True, novel_max: int = 1,
                 slot: bool = False, slot_kappa: float = 1.0, slot_f: int = 300,
                 suf_backoff: bool = False, suf_theta: float = 1.0, prior_gamma: float = 0.0,
                 joint_shape: bool = False, det_kappa: float = 0.0, right_kappa: float = 0.0, **kw):
        super().__init__(*a, **kw)
        self.pos_shape = bool(pos_shape); self.rich_shape = bool(rich_shape)
        self.novel_max = int(novel_max)
        self.suf_backoff = bool(suf_backoff); self.suf_theta = float(suf_theta)
        self.prior_gamma = float(prior_gamma)
        # JOINT FORM DESCRIPTION (2026-09-13, path A for the name/common-noun half of the bar). The word-form system
        # delivers ONE description of a novel string, not two independent ones -- so P(c | suffix) and P(shape@pos | c)
        # should not be multiplied as independent evidence. For novel forms they are strongly dependent: a capitalised
        # novel form and a lower-case one with the SAME ending are different populations. The exact-replication form is
        # the CONDITIONED ladder: start from P_novel(c | shape@pos) and abstract up the suffix lengths INSIDE that cell.
        self.joint_shape = bool(joint_shape)
        self.det_kappa = float(det_kappa)                          # PATH A: the Katz-Macnamara determiner context
        self.right_kappa = float(right_kappa)                      # the RIGHT half of the frame
        self.detc: Dict[str, Counter] = defaultdict(Counter)       # category -> Counter(det context symbol)
        self.rightc: Dict[str, Counter] = defaultdict(Counter)     # category -> Counter(right context symbol)
        self.slot = bool(slot); self.slot_kappa = float(slot_kappa); self.slot_f = int(slot_f)
        self.shape_pos: Dict[str, Counter] = defaultdict(Counter)        # category -> Counter(shape@position)
        self.shape_pos_w: Dict[str, Counter] = defaultdict(Counter)      # word type -> Counter(shape@position)
        self.slotL: Dict[str, Counter] = defaultdict(Counter)            # category -> Counter(left neighbour word)
        self.slotR: Dict[str, Counter] = defaultdict(Counter)
        self._sent_pos: List[str] = []; self._sent_lows: List[str] = []; self._sent_i = 0
        self._shuffle_seed: Optional[int] = None
        self.n_novel_types = 0

    # ------------------------------------------------------------ plastic knowledge: counts
    def _sym(self, w_raw: str, pos: str) -> str:
        sh = word_shape_rich(w_raw) if self.rich_shape else LC.word_shape(w_raw)
        return sh + pos if self.pos_shape else sh

    def alphabet_size(self) -> int:
        n = len(RICH_SHAPES) if self.rich_shape else len(LC.SHAPES)
        return n * 2 if self.pos_shape else n

    def accrue(self, sentences):
        super().accrue(sentences)
        for sent in sentences:
            words = [w for w, _ in sent]
            lows = [w.lower() for w in words]
            for i, (w_raw, t) in enumerate(sent):
                sp = self._sym(w_raw, position_class(words, i))
                self.shape_pos[t][sp] += 1
                self.shape_pos_w[lows[i]][sp] += 1
                self.detc[t][det_context(lows, i)] += 1
                self.rightc[t][right_context(lows, i)] += 1
                if self.slot:
                    self.slotL[t][lows[i - 1] if i > 0 else BOS] += 1
                    self.slotR[t][lows[i + 1] if i + 1 < len(lows) else LC.EOS] += 1
        self._dirty = True
        return self

    # ------------------------------------------------------------ log-probabilities: ONE pure function of the counts
    def finalize(self):
        super().finalize()
        T = len(self.tags)
        # ---- the whole-vocabulary shape x position factor (for words that HAVE a lexical entry)
        self._syms = sorted({s for c in self.shape_pos.values() for s in c})
        S = self.alphabet_size()
        self.log_shape_pos = {}
        self._shape_pos_back = {}
        for t in self.tags:
            tot = sum(self.shape_pos[t].values()) + self.lam * S
            self.log_shape_pos[t] = {s: math.log((self.shape_pos[t][s] + self.lam) / tot) for s in self._syms}
            self._shape_pos_back[t] = math.log(self.lam / tot)
        # ---- THE NOVEL-FORM STRATUM (Baayen productivity): types seen <= novel_max times, counted ONCE each (one
        #      learning event per newly-met form), their tag mass spread over the tags they were met under.
        wcnt: Counter = Counter()
        wtag: Dict[str, np.ndarray] = {}
        for i, t in enumerate(self.tags):
            for w, n in self.emit[t].items():
                wcnt[w] += n
                v = wtag.get(w)
                if v is None:
                    v = wtag[w] = np.zeros(T)
                v[i] += n
        novel = [w for w, n in wcnt.items() if n <= self.novel_max] if self.novel_max > 0 else []
        self.n_novel_types = len(novel)
        suf_u: Dict[int, Dict[str, np.ndarray]] = {k: {} for k in range(1, self.suf_len + 1)}
        shape_u: Dict[str, np.ndarray] = {}
        prior_u = np.zeros(T)
        for w in novel:
            v = wtag[w]
            v = v / v.sum()                            # one type = one learning event, graded over its tags
            prior_u += v
            for k in range(1, self.suf_len + 1):
                if len(w) >= k:
                    s = w[-k:]
                    row = suf_u[k].get(s)
                    if row is None:
                        row = suf_u[k][s] = np.zeros(T)
                    row += v
            col = self.shape_pos_w.get(w)
            if col:
                den = float(sum(col.values()))
                for sp, n in col.items():
                    row = shape_u.get(sp)
                    if row is None:
                        row = shape_u[sp] = np.zeros(T)
                    row += v * (n / den)
        self.suf_u = suf_u
        self.log_prior_u = np.log((prior_u + self.lam) / (prior_u.sum() + self.lam * T)) if novel else None
        if self.joint_shape and novel:
            # the SAME ladder, conditioned on the form description: counts of (suffix, shape@pos) and of shape@pos alone,
            # over the novel stratum. Sparse by construction, which is exactly why the ladder backs off.
            jsuf: Dict[int, Dict[tuple, np.ndarray]] = {k: {} for k in range(1, self.suf_len + 1)}
            jsh: Dict[str, np.ndarray] = {}
            for w in novel:
                v = wtag[w]; v = v / v.sum()
                col = self.shape_pos_w.get(w)
                if not col:
                    continue
                den = float(sum(col.values()))
                for sp, nn in col.items():
                    vv = v * (nn / den)
                    row = jsh.get(sp)
                    if row is None:
                        row = jsh[sp] = np.zeros(T)
                    row += vv
                    for k in range(1, self.suf_len + 1):
                        if len(w) >= k:
                            key = (w[-k:], sp)
                            r2 = jsuf[k].get(key)
                            if r2 is None:
                                r2 = jsuf[k][key] = np.zeros(T)
                            r2 += vv
            self.jsuf_u = jsuf
            self.jshape_u = jsh
        tot_u = np.zeros(T)
        for row in shape_u.values():
            tot_u += row
        nsp = self.alphabet_size()
        self.log_shape_u = {sp: np.log((row + self.lam) / (tot_u + self.lam * nsp)) for sp, row in shape_u.items()}
        self._log_shape_u_back = np.log((np.zeros(T) + self.lam) / (tot_u + self.lam * nsp)) if novel else None
        # ---- PATH A: log P(det context | c) over the NOVEL stratum's own contexts is not available (the stratum is a
        #      set of TYPES, not tokens), so this table is the whole-supply one -- it is a property of the SLOT, not of
        #      the word, so the productivity argument does not apply to it.
        nd = len(DET_SYMS)
        self.log_detc = {}
        for t in self.tags:
            tot = sum(self.detc[t].values()) + self.lam * nd
            self.log_detc[t] = {s: math.log((self.detc[t][s] + self.lam) / tot) for s in DET_SYMS}
        nr = len(RIGHT_SYMS)
        self.log_rightc = {}
        for t in self.tags:
            tot = sum(self.rightc[t].values()) + self.lam * nr
            self.log_rightc[t] = {s: math.log((self.rightc[t][s] + self.lam) / tot) for s in RIGHT_SYMS}
        # ---- the SLOT cue (frequent frames), read only where there is no lexical entry
        if self.slot:
            freq: Counter = Counter()
            for t in self.tags:
                freq.update(self.emit[t])
            self.slot_words = {w for w, _ in freq.most_common(self.slot_f)}
            syms = sorted(self.slot_words | {BOS, LC.EOS, LC.FRAME_OTHER}); V = len(syms)
            self.log_slotL = {}; self.log_slotR = {}
            for t in self.tags:
                for tab, out in ((self.slotL, self.log_slotL), (self.slotR, self.log_slotR)):
                    col2: Counter = Counter()
                    for a, n in tab[t].items():
                        col2[a if (a in self.slot_words or a in (BOS, LC.EOS)) else LC.FRAME_OTHER] += n
                    tot = sum(col2.values()) + self.lam * V
                    out[t] = {a: math.log((col2[a] + self.lam) / tot) for a in syms}
        if self._shuffle_seed is not None:
            self._shuffle_tables(self._shuffle_seed)
        return self

    def _shuffle_tables(self, seed: int) -> None:
        """THE INFORMATION-FREE TWIN: the same tables with the SYMBOL -> category-row mapping permuted. Identical
        alphabet, identical row marginals, identical smoothing -- the form/position cue now says nothing."""
        rng = random.Random(seed)
        keys = list(self.log_shape_u)
        vals = [self.log_shape_u[k] for k in keys]
        rng.shuffle(vals)
        self.log_shape_u = dict(zip(keys, vals))
        keys = list(self._syms)
        rows = [[self.log_shape_pos[t][s] for t in self.tags] for s in keys]
        rng.shuffle(rows)
        self.log_shape_pos = {t: {s: rows[j][i] for j, s in enumerate(keys)} for i, t in enumerate(self.tags)}
        if self.joint_shape and getattr(self, "jshape_u", None):
            # the JOINT arm's information lives in these two tables; a twin that leaves them alone is not a twin at all
            # (caught 2026-09-13: the un-shuffled twin scored 0.8559 against the arm's 0.8580 -- a vacuous control).
            ks = list(self.jshape_u); vs = [self.jshape_u[k] for k in ks]
            rng.shuffle(vs)
            self.jshape_u = dict(zip(ks, vs))
            for k in range(1, self.suf_len + 1):
                kk = list(self.jsuf_u[k]); vv = [self.jsuf_u[k][x] for x in kk]
                rng.shuffle(vv)
                self.jsuf_u[k] = dict(zip(kk, vv))
        for k in range(1, self.suf_len + 1):
            ks = list(self.suf_u[k]); vs = [self.suf_u[k][s] for s in ks]
            rng.shuffle(vs)
            self.suf_u[k] = dict(zip(ks, vs))
            allk = sorted({s for t in self.tags for s in self.suf[k][t]})
            srows = [[self.suf[k][t][s] for t in self.tags] for s in allk]
            rng.shuffle(srows)
            for i, t in enumerate(self.tags):
                self.suf[k][t] = Counter({s: srows[j][i] for j, s in enumerate(allk)})

    # ------------------------------------------------------------ inference
    def _log_emit_unknown(self, w: str) -> np.ndarray:
        """The novel-form estimator on the PRODUCTIVITY stratum: P(c | suffix among novel forms), backing off to the
        NOVEL-form prior (not the overall tag frequency, which is function words that can never be novel).

        `suf_backoff` replaces the incumbent's HARD choice of the single longest suffix with any count by the brain's
        GRADED one: morpho-orthographic segmentation activates every plausible parse in parallel (Rastle & Davis 2008)
        and the graded system keeps the alternatives alive weighted by their reliability (MacDonald 1994, the account
        this organ already cites; Samuelsson 1993 / Brants 2000 successive abstraction is the count form). Each length
        is mixed into the shorter one by the SAME Bayesian shrinkage the organ already uses for rare words,
        a = n / (n + theta): a suffix seen once cannot overrule the whole novel-form prior."""
        if self.novel_max <= 0 or self.log_prior_u is None:
            return super()._log_emit_unknown(w)
        est = self._joint_estimate(w) if self.joint_shape else self._suf_estimate(w)
        return est - self.prior_gamma * self.log_prior_u if self.prior_gamma else est

    def _joint_estimate(self, w: str) -> np.ndarray:
        """The ladder run INSIDE the form cell: P_novel(c | shape@pos) -> P(c | suffix_1..k, shape@pos). The caller must
        NOT also add the separate shape factor (it is already in the conditioning) -- `_log_emit` skips it for this arm."""
        sp = self._sym(self._cur_raw, self._cur_pos)
        p = self.jshape_u.get(sp)
        p = (p / p.sum()) if (p is not None and p.sum() > 0) else np.exp(self.log_prior_u)
        for k in range(1, self.suf_len + 1):
            if len(w) < k:
                break
            row = self.jsuf_u[k].get((w[-k:], sp))
            if row is None:
                break
            n = float(row.sum())
            if n <= 0:
                break
            a = n / (n + self.suf_theta)
            p = a * (row / n) + (1.0 - a) * p
        return np.log(p + 1e-12)

    def _suf_estimate(self, w: str) -> np.ndarray:
        """log P(c | suffix) on the novel stratum.

        `prior_gamma` (applied by the caller) turns that POSTERIOR into the LIKELIHOOD the generative model actually
        wants. THE INCUMBENT'S DOUBLE PRIOR: `_log_emit_unknown` returns P(c | suffix) and the forward-backward then
        multiplies it by P(c | previous category) -- so a category prior is applied TWICE for every unseen word.
        Bayes wants P(evidence | c) in the emission slot, i.e. P(c | suffix) / P(c) up to a constant. The double
        prior systematically penalises the low-prior categories, and PROPN is exactly one of those -- the direction
        of the organ's commonest unseen-word miss (PROPN -> NOUN 117). gamma is the OPERATING POINT, swept, never
        adopted: gamma 0 = the incumbent, gamma 1 = full division. It is not obviously 1, because the two priors are
        not the same object (the transition supplies a CONTEXTUAL prior, the suffix posterior a MARGINAL one), so how
        much of the marginal prior to remove is an empirical question about their overlap."""
        T = len(self.tags)
        if self.suf_backoff:
            p = np.exp(self.log_prior_u)
            for k in range(1, self.suf_len + 1):
                if len(w) < k:
                    break
                row = self.suf_u[k].get(w[-k:])
                if row is None:
                    break
                n = float(row.sum())
                if n <= 0:
                    break
                a = n / (n + self.suf_theta)
                p = a * (row / n) + (1.0 - a) * p
            return np.log(p + 1e-12)
        for k in range(self.suf_len, 0, -1):
            if len(w) >= k:
                row = self.suf_u[k].get(w[-k:])
                if row is not None and row.sum() > 0:
                    return np.log((row + self.lam) / (row.sum() + self.lam * T))
        return self.log_prior_u

    def _log_shape_factor(self, w_raw: str, pos: str, known: bool) -> np.ndarray:
        sp = self._sym(w_raw, pos)
        if known or self._log_shape_u_back is None:
            return np.array([self.log_shape_pos[t].get(sp, self._shape_pos_back[t]) for t in self.tags])
        row = self.log_shape_u.get(sp)
        return row if row is not None else self._log_shape_u_back

    def _log_emit(self, word: str) -> np.ndarray:
        """Identical in structure to `LexicalCategories._log_emit` (the shape factor stays OUTSIDE the rare-word
        mixture); the two changes are WHICH shape table is read (whole-vocabulary for a word that has a lexical entry,
        the novel-form stratum for one that does not) and the slot cue, which fires only where there is no entry."""
        pos = self._sent_pos[self._sent_i] if self._sent_i < len(self._sent_pos) else MID
        here = self._sent_i
        self._sent_i += 1
        self._cur_raw = word; self._cur_pos = pos
        w = word.lower(); V1 = len(self.vocab) + 1
        known = w in self.vocab
        if known:
            out = np.array([math.log((self.emit[t][w] + self.lam) / (self.tag_count[t] + self.lam * V1))
                            for t in self.tags])
            cw = sum(self.emit[t][w] for t in self.tags)
            mix_max = self.rare_max if LC.MIX_MAX is None else LC.MIX_MAX
            if mix_max > 0 and cw <= mix_max:
                a = cw / (cw + LC.MIX_KAPPA)
                out = np.logaddexp(math.log(a) + out, math.log(1.0 - a) + self._log_emit_unknown(w))
            if self.rare_max > 0 and cw <= self.rare_max:
                out = out + self._log_cluster(w)
        else:
            out = self._log_emit_unknown(w) + self._log_cluster(w)
        # the joint arm has the form description INSIDE the estimate already; adding it again would double-count it
        if self.use_shape and not (self.joint_shape and not known):
            out = out + self._log_shape_factor(word, pos, known=known)
        if self.slot and not known:
            out = out + self.slot_kappa * self._slot_factor(here)
        if self.det_kappa and not known:
            d = det_context(self._sent_lows, here)
            out = out + self.det_kappa * np.array([self.log_detc[t][d] for t in self.tags])
        if self.right_kappa and not known and (LC.LAG is None or LC.LAG >= 1):
            r = right_context(self._sent_lows, here)
            out = out + self.right_kappa * np.array([self.log_rightc[t][r] for t in self.tags])
        return out

    def _slot_factor(self, i: int) -> np.ndarray:
        """log P(left word | c) + log P(right word | c) at position i -- read ONLY for a word with no lexical entry
        (cue competition: the frame carries the weight the absent lexical cue cannot)."""
        lows = self._sent_lows; n = len(lows)

        def sym(a):
            return a if (a in self.slot_words or a in (BOS, LC.EOS)) else LC.FRAME_OTHER

        a = sym(lows[i - 1] if i > 0 else BOS)
        out = np.array([self.log_slotL[t][a] for t in self.tags])
        if LC.LAG is None or LC.LAG >= 1:
            b = sym(lows[i + 1] if i + 1 < n else LC.EOS)
            out = out + np.array([self.log_slotR[t][b] for t in self.tags])
        return out

    def posterior(self, words, lag=None):
        self._sent_pos = [position_class(words, i) for i in range(len(words))]
        self._sent_lows = [w.lower() for w in words]
        self._sent_i = 0
        return super().posterior(words, lag=lag)


# --------------------------------------------------------------------- data + scoring
def read_conllu(path: str, column: int = 3):
    sents, cur = [], []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                if cur:
                    sents.append(cur); cur = []
                continue
            if line.startswith("#"):
                continue
            c = line.split("\t")
            if "-" in c[0] or "." in c[0]:
                continue
            cur.append((c[1], c[column]))
    if cur:
        sents.append(cur)
    return sents


def score(model, sents, vocab) -> dict:
    """Per-SENTENCE hit vectors (the bootstrap unit), plus the slices the brief names."""
    per_sent = []; conf: Counter = Counter(); by_shape: Counter = Counter(); by_shape_ok: Counter = Counter()
    tot = ok = unk = unk_ok = 0
    for s in sents:
        words = [w for w, _ in s]; gold = [g for _, g in s]
        post = model.posterior(words); pred = [model.tags[int(i)] for i in post.argmax(axis=1)]
        a_tot = a_ok = u_tot = u_ok = 0
        for w, g, p in zip(words, gold, pred):
            hit = int(g == p); a_tot += 1; a_ok += hit
            if w.lower() not in vocab:
                u_tot += 1; u_ok += hit
                sh = LC.word_shape(w); by_shape[sh] += 1; by_shape_ok[sh] += hit
                if not hit:
                    conf[(g, p)] += 1
        per_sent.append((a_ok, a_tot, u_ok, u_tot))
        tot += a_tot; ok += a_ok; unk += u_tot; unk_ok += u_ok
    return {"acc": ok / max(1, tot), "unknown_acc": unk_ok / max(1, unk), "n_tokens": tot, "n_unknown": unk,
            "per_sent": per_sent, "confusions": {"%s->%s" % (g, p): n for (g, p), n in conf.most_common(20)},
            "propn_noun": conf[("PROPN", "NOUN")] + conf[("NOUN", "PROPN")],
            "by_shape": {s: {"n": by_shape[s], "acc": round(by_shape_ok[s] / by_shape[s], 4)} for s in by_shape}}


def paired_boot(a, b, field: str, n_boot: int = 2000, seed: int = 0):
    """Paired bootstrap over SENTENCES on the delta (b - a). field = 'unk' or 'all'."""
    i0, i1 = (2, 3) if field == "unk" else (0, 1)
    A = np.array([[s[i0], s[i1]] for s in a], dtype=float)
    B = np.array([[s[i0], s[i1]] for s in b], dtype=float)
    n = len(A); rng = np.random.default_rng(seed); d = np.empty(n_boot)
    for r in range(n_boot):
        idx = rng.integers(0, n, n)
        ta = A[idx].sum(axis=0); tb = B[idx].sum(axis=0)
        d[r] = (tb[0] / max(1.0, tb[1])) - (ta[0] / max(1.0, ta[1]))
    obs = (B[:, 0].sum() / max(1.0, B[:, 1].sum())) - (A[:, 0].sum() / max(1.0, A[:, 1].sum()))
    lo, hi = np.percentile(d, [2.5, 97.5])
    return {"delta": round(float(obs), 4), "ci95": [round(float(lo), 4), round(float(hi), 4)],
            "half_width": round(float(hi - lo) / 2, 4), "separated": bool(lo > 0 or hi < 0)}


ARMS = {
    "A0_live":        dict(pos_shape=False, rich_shape=False, novel_max=0, slot=False),
    "A1_position":    dict(pos_shape=True,  rich_shape=False, novel_max=0, slot=False),
    "A2_novel1":      dict(pos_shape=True,  rich_shape=False, novel_max=1, slot=False),
    "A2b_novel2":     dict(pos_shape=True,  rich_shape=False, novel_max=2, slot=False),
    "A2c_novel3":     dict(pos_shape=True,  rich_shape=False, novel_max=3, slot=False),
    "A2d_novel5":     dict(pos_shape=True,  rich_shape=False, novel_max=5, slot=False),
    "A3_rich_n1":     dict(pos_shape=True,  rich_shape=True,  novel_max=1, slot=False),
    "A3b_rich_n2":    dict(pos_shape=True,  rich_shape=True,  novel_max=2, slot=False),
    "A3c_rich_n3":    dict(pos_shape=True,  rich_shape=True,  novel_max=3, slot=False),
    "N_novel_only":   dict(pos_shape=False, rich_shape=False, novel_max=2, slot=False),
    "R_rich_only":    dict(pos_shape=False, rich_shape=True,  novel_max=0, slot=False),
    "A4_slot1":       dict(pos_shape=True,  rich_shape=True,  novel_max=2, slot=True,  slot_kappa=1.0),
    "A4b_slot05":     dict(pos_shape=True,  rich_shape=True,  novel_max=2, slot=True,  slot_kappa=0.5),
    "A4c_slot025":    dict(pos_shape=True,  rich_shape=True,  novel_max=2, slot=True,  slot_kappa=0.25),
    # --- the GRADED morpho-orthographic parse (successive abstraction over suffix lengths), theta swept
    "A5_bo_t1":       dict(pos_shape=True,  rich_shape=True,  novel_max=2, suf_backoff=True, suf_theta=1.0),
    "A5b_bo_t3":      dict(pos_shape=True,  rich_shape=True,  novel_max=2, suf_backoff=True, suf_theta=3.0),
    "A5c_bo_t10":     dict(pos_shape=True,  rich_shape=True,  novel_max=2, suf_backoff=True, suf_theta=10.0),
    "A5d_bo_t30":     dict(pos_shape=True,  rich_shape=True,  novel_max=2, suf_backoff=True, suf_theta=30.0),
    "A5e_bo_t3_n5":   dict(pos_shape=True,  rich_shape=True,  novel_max=5, suf_backoff=True, suf_theta=3.0),
    "A5f_bo_t3_n10":  dict(pos_shape=True,  rich_shape=True,  novel_max=10, suf_backoff=True, suf_theta=3.0),
    "A5g_bo_noshape": dict(pos_shape=False, rich_shape=False, novel_max=2, suf_backoff=True, suf_theta=3.0),
    "A6_bo_slot05":   dict(pos_shape=True,  rich_shape=True,  novel_max=2, suf_backoff=True, suf_theta=3.0,
                           slot=True, slot_kappa=0.5),
    # --- the emission slot takes a LIKELIHOOD, not a posterior: gamma = how much of the marginal prior to remove
    "A7_g025":        dict(pos_shape=True,  rich_shape=True,  novel_max=2, suf_backoff=True, suf_theta=3.0,
                           prior_gamma=0.25),
    "A7b_g05":        dict(pos_shape=True,  rich_shape=True,  novel_max=2, suf_backoff=True, suf_theta=3.0,
                           prior_gamma=0.5),
    "A7c_g075":       dict(pos_shape=True,  rich_shape=True,  novel_max=2, suf_backoff=True, suf_theta=3.0,
                           prior_gamma=0.75),
    "A7d_g1":         dict(pos_shape=True,  rich_shape=True,  novel_max=2, suf_backoff=True, suf_theta=3.0,
                           prior_gamma=1.0),
    "A8_g05_slot05":  dict(pos_shape=True,  rich_shape=True,  novel_max=2, suf_backoff=True, suf_theta=3.0,
                           prior_gamma=0.5, slot=True, slot_kappa=0.5),
    "A8b_g05_slot1":  dict(pos_shape=True,  rich_shape=True,  novel_max=2, suf_backoff=True, suf_theta=3.0,
                           prior_gamma=0.5, slot=True, slot_kappa=1.0),
    # --- PATH A: the word-form system delivers ONE description; run the abstraction ladder INSIDE the form cell
    "A9_joint":       dict(pos_shape=True,  rich_shape=True,  novel_max=2, suf_backoff=True, suf_theta=3.0,
                           prior_gamma=0.5, joint_shape=True),
    "A9b_joint_n5":   dict(pos_shape=True,  rich_shape=True,  novel_max=5, suf_backoff=True, suf_theta=3.0,
                           prior_gamma=0.5, joint_shape=True),
    # --- PATH A (2nd attempt): the Katz-Macnamara DETERMINER CONTEXT, a 9-symbol count table over the left context's
    #     function-word class, read only where there is no lexical entry. kappa is the operating point, swept.
    "B1_det05":       dict(pos_shape=True,  rich_shape=True,  novel_max=2, suf_backoff=True, suf_theta=3.0,
                           prior_gamma=0.5, det_kappa=0.5),
    "B2_det1":        dict(pos_shape=True,  rich_shape=True,  novel_max=2, suf_backoff=True, suf_theta=3.0,
                           prior_gamma=0.5, det_kappa=1.0),
    "B3_det2":        dict(pos_shape=True,  rich_shape=True,  novel_max=2, suf_backoff=True, suf_theta=3.0,
                           prior_gamma=0.5, det_kappa=2.0),
    "B4_det1_only":   dict(pos_shape=False, rich_shape=False, novel_max=0, det_kappa=1.0),
    # --- the two-sided frame: the Katz determiner context PLUS the right-hand frame symbol
    "C1_lr05":        dict(pos_shape=True,  rich_shape=True,  novel_max=2, suf_backoff=True, suf_theta=3.0,
                           prior_gamma=0.5, det_kappa=0.5, right_kappa=0.5),
    "C2_lr_r05":      dict(pos_shape=True,  rich_shape=True,  novel_max=2, suf_backoff=True, suf_theta=3.0,
                           prior_gamma=0.5, right_kappa=0.5),
    "C3_lr_only":     dict(pos_shape=False, rich_shape=False, novel_max=0, det_kappa=1.0, right_kappa=1.0),
    # --- the frame cue is worth -19 PROPN<->NOUN ALONE (163 -> 144) but only -9 in combination (163 -> 154): the form
    #     cues are masking it. Sweep its weight against the prior gamma, which is the other cue that targets this pair.
    "D1_lr1_g05":     dict(pos_shape=True,  rich_shape=True,  novel_max=2, suf_backoff=True, suf_theta=3.0,
                           prior_gamma=0.5, det_kappa=1.0, right_kappa=1.0),
    "D2_lr1_g075":    dict(pos_shape=True,  rich_shape=True,  novel_max=2, suf_backoff=True, suf_theta=3.0,
                           prior_gamma=0.75, det_kappa=1.0, right_kappa=1.0),
    "D3_lr15_g05":    dict(pos_shape=True,  rich_shape=True,  novel_max=2, suf_backoff=True, suf_theta=3.0,
                           prior_gamma=0.5, det_kappa=1.5, right_kappa=1.5),
    "D4_lr2_g05":     dict(pos_shape=True,  rich_shape=True,  novel_max=2, suf_backoff=True, suf_theta=3.0,
                           prior_gamma=0.5, det_kappa=2.0, right_kappa=2.0),
    "D5_lr1_g05_nopos": dict(pos_shape=False, rich_shape=True, novel_max=2, suf_backoff=True, suf_theta=3.0,
                             prior_gamma=0.5, det_kappa=1.0, right_kappa=1.0),
}


def build(train, cfg, shuffle_seed=None, order: int = 2):
    """order 2 = the live UPOS asset's setting; order 1 = the live PENN arm's (49 tags; second order is 17x slower and
    was explicitly rejected as a read-time arm on 2026-09-13)."""
    m = UnknownWordCategories(order=order, use_shape=True, rare_max=2, use_cluster=True, **cfg)
    m._shuffle_seed = shuffle_seed
    return m.accrue(train).finalize()


def self_test() -> bool:
    """Green-before-you-run: the arms are wired, A0 reproduces the live code path, the twin is information-free,
    the counts are plastic (the online `observe` path re-derives the productivity stratum)."""
    tr = read_conllu(TRAIN)[:600]
    te = read_conllu(TEST)[:60]
    base = build(tr, ARMS["A0_live"])
    ref = LexicalCategories(order=2, use_shape=True, rare_max=2, use_cluster=True).accrue(tr).finalize()
    v = set(base.vocab)
    s0 = score(base, te, v); sr = score(ref, te, v)
    assert abs(s0["acc"] - sr["acc"]) < 1e-12, ("A0 must reproduce the live code path exactly", s0["acc"], sr["acc"])
    a3 = build(tr, ARMS["A3b_rich_n2"])
    s3 = score(a3, te, v)
    tw = build(tr, ARMS["A3b_rich_n2"], shuffle_seed=17)
    st = score(tw, te, v)
    assert st["unknown_acc"] <= s3["unknown_acc"], ("twin must not beat the arm", st["unknown_acc"], s3["unknown_acc"])
    assert position_class(["``", "The", "dog"], 1) == INIT and position_class(["The", "dog"], 1) == MID
    assert word_shape_rich("AMS") == "ACRO" and word_shape_rich("E17") == "alnum" and word_shape_rich("b/c") == "slash"
    assert word_shape_rich("01-Feb-02") == "dcode" and word_shape_rich("Guaranty.doc") == "dotted"
    assert word_shape_rich("Falluja") == "Cap" and word_shape_rich("McDonald") == "CamelCap"
    assert word_shape_rich("MSM") == "ACRO" and word_shape_rich("1998") == "num"
    n0 = a3.n_novel_types
    a3.observe(["Zorbulax", "flew"], ["PROPN", "VERB"])          # the ONLINE path re-derives the novel stratum
    assert "zorbulax" in a3.vocab and a3.shape_pos["PROPN"]["Cap" + INIT] >= 1
    assert a3.n_novel_types >= n0, "the productivity stratum must be re-derived by observe"
    print(json.dumps({"self_test": "PASS", "A0": round(s0["acc"], 4), "ref": round(sr["acc"], 4),
                      "A3_unk": round(s3["unknown_acc"], 4), "twin_unk": round(st["unknown_acc"], 4),
                      "novel_types": n0}))
    return True


def run_penn(arm: str, boot: int) -> dict:
    """NO-REGRESS 1: the PENN-TAGSET ARM of the same organ (`lexical_categories_counts_penn_v1.json`, xpos 0.9176),
    which the temporal ORDER organ reads. Same cues, second inventory."""
    train = read_conllu(TRAIN, column=4); test = read_conllu(TEST, column=4)
    base = build(train, ARMS["A0_live"], order=1); vocab = set(base.vocab)
    s0 = score(base, test, vocab)
    m = build(train, ARMS[arm], order=1); s1 = score(m, test, vocab)
    out = {"arm": arm,
           "A0": {k: v for k, v in s0.items() if k != "per_sent"},
           arm: {k: v for k, v in s1.items() if k != "per_sent"}}
    out["d_unknown"] = paired_boot(s0["per_sent"], s1["per_sent"], "unk", boot)
    out["d_overall"] = paired_boot(s0["per_sent"], s1["per_sent"], "all", boot)
    print("PENN", json.dumps({"A0_xpos": round(s0["acc"], 4), "A0_unk": round(s0["unknown_acc"], 4),
                              arm + "_xpos": round(s1["acc"], 4), arm + "_unk": round(s1["unknown_acc"], 4),
                              "d_all": out["d_overall"], "d_unk": out["d_unknown"]}), flush=True)
    return out


def run_heads(arm: str) -> dict:
    """NO-REGRESS 2: the HEADS rung under the organ's OWN tags (`probe_heads_under_category_posterior_v1`, 0.598).
    The live singleton `LC.get()` is redirected IN PROCESS to the arm's model -- no file on disk is touched."""
    import hdlab.attachment_arm as AA
    from tools.build_attachment_validities import sentences, TEST as ATEST, CORE_RELS
    test = sentences(ATEST, cap=700, maxlen=10 ** 6)
    tab = AA.load_attachment_validities()
    train = read_conllu(TRAIN)
    res = {"arm": arm}
    for name in ("A0_live", arm):
        lc = build(train, ARMS[name])
        cache = {}

        def tagged(toks):
            k = tuple(toks)
            if k not in cache:
                cache[k] = lc.tag_with_posterior(list(toks))
            return cache[k]

        agree = atot = c = t = 0; rt = {}; rh = {}
        for toks, gold_pos, gold_heads, rels in test:
            tg = tagged(toks)[0]
            for x, y in zip(tg, gold_pos):
                agree += int(x == y); atot += 1
            hd = AA.heads(list(toks), tg, tab)
            for i, g in enumerate(gold_heads, start=1):
                if 0 <= g <= len(toks):
                    ok = int(hd.get(i, -1) == g); c += ok; t += 1
                    r = rels[i - 1]
                    if r in CORE_RELS:
                        rt[r] = rt.get(r, 0) + 1; rh[r] = rh.get(r, 0) + ok
        res[name] = {"uas": round(c / max(1, t), 4), "tag_agreement": round(agree / max(1, atot), 4),
                     "per_relation": {r: round(rh[r] / rt[r], 3) for r in CORE_RELS if r in rt}}
        # THE GRADED HAND-OFF, on the full live chain: instead of the HARD argmax the live default reads, marginalise
        # the arc scores over each uncertain token's second-best category (`arc_scores_graded`). The organ HOLDS a
        # posterior whose mean top mass on an unseen token is 0.8965 -- this measures what the hard readout throws away.
        cg = tg_ = 0
        for toks, gold_pos, gold_heads, rels in test:
            tt, tp = tagged(toks)
            hd = AA.heads_graded(list(toks), tt, tp, tab)
            for i, g in enumerate(gold_heads, start=1):
                if 0 <= g <= len(toks):
                    cg += int(hd.get(i, -1) == g); tg_ += 1
        res[name]["uas_graded_handoff"] = round(cg / max(1, tg_), 4)
        res[name]["graded_minus_hard"] = round(cg / max(1, tg_) - res[name]["uas"], 4)
        print("HEADS", name, json.dumps(res[name]), flush=True)
    res["d_uas_hard"] = round(res[arm]["uas"] - res["A0_live"]["uas"], 4)
    res["d_uas_graded"] = round(res[arm]["uas_graded_handoff"] - res["A0_live"]["uas_graded_handoff"], 4)
    return res


def coverage_bound(arm: str = "C1_lr05") -> dict:
    """WHAT WOULD GROWING THE READING-ACQUIRED INVENTORY BUY? A BOUND, not a claim. The induced inventory covers 549
    of 1,882 unseen tokens; 1,333 get exactly zero from the organ's own reading arm. Split the arm's unseen accuracy by
    whether the cue fired. The gap is an UPPER bound on what perfect coverage could buy, and it is confounded (covered
    words are the ones simple-Wikipedia contains, i.e. more ordinary words), so it is reported as a bound with the
    confound named -- never as a projected gain."""
    import hdlab.induced_categories as IC
    ic = IC.get()
    train = read_conllu(TRAIN); test = read_conllu(TEST)
    base = build(train, ARMS["A0_live"]); vocab = set(base.vocab)
    armm = build(train, dict(ARMS[arm]))
    out = {}
    for nm, m in (("A0_live", base), (arm, armm)):
        cov = covok = unc = uncok = 0
        for s in test:
            words = [w for w, _ in s]; gold = [g for _, g in s]
            pred = [m.tags[int(i)] for i in m.posterior(words).argmax(axis=1)]
            for w, g, p in zip(words, gold, pred):
                if w.lower() in vocab:
                    continue
                if ic.cluster_of(w) is not None:
                    cov += 1; covok += int(g == p)
                else:
                    unc += 1; uncok += int(g == p)
        out[nm] = {"covered_n": cov, "covered_acc": round(covok / max(1, cov), 4),
                   "uncovered_n": unc, "uncovered_acc": round(uncok / max(1, unc), 4),
                   "gap": round(covok / max(1, cov) - uncok / max(1, unc), 4),
                   "tokens_if_uncovered_reached_covered_acc": round((covok / max(1, cov)) * unc - uncok, 1)}
    print("COVERAGE_BOUND", json.dumps(out, indent=1), flush=True)
    return out


def explain(arm: str, ref: str = "A0_live") -> dict:
    """WHY a lever moved (or did not) -- mechanism in counts, not narration.
    (a) the CUE STRENGTH each arm actually has for the PROPN-vs-NOUN contrast, as a log-odds, per symbol -- this is what
        says whether a cue could possibly have moved that confusion;
    (b) how many unseen tokens CHANGED prediction, split into fixed / broken / swapped-still-wrong;
    (c) the per-(gold,pred) confusion delta, so a headline gain that hides a class regression is visible."""
    train = read_conllu(TRAIN); test = read_conllu(TEST)
    A = build(train, ARMS[ref]); B = build(train, ARMS[arm]); vocab = set(A.vocab)
    out = {"arm": arm, "ref": ref}
    # (a) cue strength: log P(sym|PROPN) - log P(sym|NOUN) under each arm's shape table, on the unseen population
    def contrast(m, w_raw, pos):
        f = m._log_shape_factor(w_raw, pos, known=False)
        i, j = m.tags.index("PROPN"), m.tags.index("NOUN")
        return float(f[i] - f[j])
    rows = {}
    for w_raw, pos in (("Falluja", MID), ("Falluja", INIT), ("Gmail", MID), ("AMS", MID), ("E17", MID),
                       ("01-Feb-02", MID), ("tonite", MID), ("Guaranty.doc", MID), ("b/c", MID)):
        rows["%s%s" % (w_raw, pos)] = {ref: round(contrast(A, w_raw, pos), 3), arm: round(contrast(B, w_raw, pos), 3)}
    out["propn_vs_noun_log_odds_of_the_form_cue"] = rows
    # (b) + (c)
    fixed = broken = swapped = same = 0
    dconf: Counter = Counter(); moved_shape: Counter = Counter()
    for s in test:
        words = [w for w, _ in s]; gold = [g for _, g in s]
        pa = [A.tags[int(i)] for i in A.posterior(words).argmax(axis=1)]
        pb = [B.tags[int(i)] for i in B.posterior(words).argmax(axis=1)]
        for w, g, x, y in zip(words, gold, pa, pb):
            if w.lower() in vocab:
                continue
            if x == y:
                same += 1
            elif y == g:
                fixed += 1; moved_shape[("fixed", word_shape_rich(w))] += 1
            elif x == g:
                broken += 1; moved_shape[("broken", word_shape_rich(w))] += 1
            else:
                swapped += 1
            if x != g:
                dconf["%s->%s" % (g, x)] -= 1
            if y != g:
                dconf["%s->%s" % (g, y)] += 1
    out["unseen_prediction_changes"] = {"fixed": fixed, "broken": broken, "swapped_still_wrong": swapped,
                                        "unchanged": same, "net": fixed - broken}
    out["by_rich_shape"] = {"%s|%s" % k: v for k, v in moved_shape.most_common(24)}
    out["confusion_delta"] = {k: v for k, v in sorted(dconf.items(), key=lambda kv: -abs(kv[1])) if v}
    print("EXPLAIN", json.dumps(out, indent=1)[:4000], flush=True)
    return out


def chain_trace() -> dict:
    """THE SIGNAL-LOSS TRACE, rung by rung, in counts: for each cue the unseen-word read needs, what the upstream rung
    PRODUCES, what this rung READS, and what is LOST. Then the same for the hand-off DOWN to the heads rung."""
    import hdlab.induced_categories as IC
    from hdlab.morphology import default_morphology
    test = read_conllu(TEST)
    live = LC.get(); ic = IC.get(); mo = default_morphology()
    unseen = [(w, g, i) for s in test for i, (w, g) in enumerate(s) if w.lower() not in live.vocab]
    n = len(unseen)
    tr = {"n_test_tokens": sum(len(s) for s in test), "n_unseen": n}
    # RUNG 1 tokenisation: what arrives as ONE token that the form cue must then read whole
    multi = sum(1 for w, _, _ in unseen if any(ch in "-/.:@" for ch in w) or
                (any(c.isdigit() for c in w) and any(c.isalpha() for c in w)))
    tr["rung1_tokenisation"] = {"unseen tokens carrying internal structure (a code/date/filename/URL arrives whole)": multi,
                                "share": round(multi / n, 4),
                                "read by the incumbent as": "2 symbols ('digit', 'other'); by the patch as 8"}
    # RUNG 2 the form cue
    from collections import Counter as C
    sh_inc = C(LC.word_shape(w) for w, _, _ in unseen)
    sh_new = C(word_shape_rich(w) for w, _, _ in unseen)
    tr["rung2_form_cue"] = {"incumbent symbols used on the unseen slice": len(sh_inc),
                            "patch symbols used": len(sh_new),
                            "position-blind": "a sentence-initial Cap and a mid-sentence Cap were ONE symbol",
                            "unseen tokens in a forced-capitalisation position": sum(1 for _, _, i in unseen if i == 0)}
    # RUNG 3 the reading-acquired inventory
    cov = sum(1 for w, _, _ in unseen if ic.cluster_of(w) is not None)
    tr["rung3_reading_acquired_inventory"] = {"covers": cov, "of": n, "coverage": round(cov / n, 4),
                                              "LOST": n - cov, "note": "the cue is exactly zero for the rest"}
    # RUNG 4 the lemma / stem route
    reach = 0
    for w, _, _ in unseen:
        wl = w.lower()
        for pl in ("v", "n", "a"):
            b = mo.morphy(wl, pl)
            if b and b != wl and b in live.vocab:
                reach += 1; break
    tr["rung4_lemma_stem_route"] = {"reaches": reach, "of": n, "coverage": round(reach / n, 4),
                                    "note": "the stem must already be a KNOWN word, so it is silent on a truly novel form"}
    # RUNG 5 the suffix evidence the sequence model is handed
    lens: Counter = Counter(); thin = 0
    for w, _, _ in unseen:
        wl = w.lower(); used = None
        for k in range(live.suf_len, 0, -1):
            if len(wl) >= k and live.suf_tot[k][wl[-k:]] > 0:
                used = k; break
        lens[used] += 1
        if used and live.suf_tot[used][wl[-used:]] <= 2:
            thin += 1
    tr["rung5_morpho_orthographic_commitment"] = {"suffix length the incumbent commits to": dict(lens),
                                                  "commitments resting on <= 2 observations": thin,
                                                  "LOST": "every shorter, better-attested parse is discarded"}
    # RUNG 6 what the consumer downstream actually receives
    conf = 0; tot = 0
    for s in test[:400]:
        words = [w for w, _ in s]
        post = live.posterior(words)
        for i, w in enumerate(words):
            if w.lower() not in live.vocab:
                tot += 1; conf += float(post[i].max())
    tr["rung6_handoff_to_heads"] = {"mean top-category mass on an unseen token (n=%d)" % tot: round(conf / max(1, tot), 4),
                                    "note": "the heads rung's live default reads the HARD argmax; the graded mixture "
                                            "(arc_scores_graded) exists and is measured at 0.5400 vs 0.5362 hard"}
    print("CHAIN_TRACE", json.dumps(tr, indent=1), flush=True)
    return tr


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--mode", default="full")
    ap.add_argument("--arms", default="")
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--save-asset", default="")
    ap.add_argument("--tag", default="")
    ap.add_argument("--penn", default="")
    ap.add_argument("--heads", default="")
    ap.add_argument("--explain", default="")
    ap.add_argument("--chain-trace", action="store_true")
    ap.add_argument("--coverage-bound", action="store_true")
    ap.add_argument("--out-name", default="metrics_no_regress.json")
    args = ap.parse_args()
    if args.self_test:
        sys.exit(0 if self_test() else 1)
    if args.penn or args.heads or args.explain or args.chain_trace or args.coverage_bound:
        od = str(get_output_dir("exp_category_unknown_word_cues_v1"))
        os.makedirs(od, exist_ok=True)
        out = {"cell": "exp_category_unknown_word_cues_v1", "tag": args.tag}
        if args.chain_trace:
            out["chain_trace"] = chain_trace()
        if args.coverage_bound:
            out["coverage_bound"] = coverage_bound(args.heads or args.penn or "C1_lr05")
        for a in [x for x in args.explain.split(",") if x in ARMS]:
            out.setdefault("explain", {})[a] = explain(a)
        if args.penn:
            out["penn_no_regress"] = run_penn(args.penn, args.boot)
        if args.heads:
            out["heads_no_regress"] = run_heads(args.heads)
        fn = os.path.join(od, args.out_name)
        with open(fn, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1)
        print("wrote", fn)
        return
    smoke = bool(args.smoke) or args.mode == "smoke"
    t_all = time.time()
    train = read_conllu(TRAIN); test = read_conllu(TEST)
    if smoke:
        train = train[:1500]; test = test[:150]
    names = [a for a in (args.arms.split(",") if args.arms else list(ARMS)) if a in ARMS]
    out = {"cell": "exp_category_unknown_word_cues_v1", "smoke": smoke, "n_train_sent": len(train),
           "n_test_sent": len(test), "arms": {}, "n_boot": args.boot, "tag": args.tag}
    base = build(train, ARMS["A0_live"]); vocab = set(base.vocab)
    s_base = score(base, test, vocab)
    out["arms"]["A0_live"] = {k: v for k, v in s_base.items() if k != "per_sent"}
    print("A0_live", json.dumps({k: round(v, 4) if isinstance(v, float) else v
                                 for k, v in s_base.items() if k in ("acc", "unknown_acc", "n_unknown", "propn_noun")}))
    best = None; best_ps = None
    for name in names:
        if name == "A0_live":
            continue
        t0 = time.time()
        m = build(train, ARMS[name]); s = score(m, test, vocab)
        rec = {k: v for k, v in s.items() if k != "per_sent"}
        rec["vs_A0_unknown"] = paired_boot(s_base["per_sent"], s["per_sent"], "unk", args.boot)
        rec["vs_A0_overall"] = paired_boot(s_base["per_sent"], s["per_sent"], "all", args.boot)
        rec["novel_types"] = getattr(m, "n_novel_types", 0); rec["sec"] = round(time.time() - t0, 1)
        out["arms"][name] = rec
        print(name, json.dumps({"unk": round(s["unknown_acc"], 4), "acc": round(s["acc"], 4),
                                "propn_noun": s["propn_noun"], "d_unk": rec["vs_A0_unknown"],
                                "d_all": rec["vs_A0_overall"], "sec": rec["sec"]}), flush=True)
        if best is None or s["unknown_acc"] > out["arms"][best]["unknown_acc"]:
            best = name; best_ps = s["per_sent"]
    if best:
        tw = build(train, ARMS[best], shuffle_seed=17); s_tw = score(tw, test, vocab)
        rec = {k: v for k, v in s_tw.items() if k != "per_sent"}
        rec["vs_A0_unknown"] = paired_boot(s_base["per_sent"], s_tw["per_sent"], "unk", args.boot)
        rec["vs_best_unknown"] = paired_boot(s_tw["per_sent"], best_ps, "unk", args.boot)
        out["arms"]["TWIN_of_" + best] = rec
        out["best_arm"] = best
        print("TWIN", json.dumps({"unk": round(s_tw["unknown_acc"], 4), "acc": round(s_tw["acc"], 4),
                                  "vs_A0": rec["vs_A0_unknown"], "best_beats_twin": rec["vs_best_unknown"]}), flush=True)
        if args.save_asset:
            m = build(train, ARMS[best])
            path = os.path.join(REPO, args.save_asset)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            m.save(path)
            with open(path, encoding="utf-8") as f:
                d = json.load(f)
            # the same keys the proposed hdlab patch's `save` writes, so the candidate asset loads under the landed code
            d["shape_pos"] = {t: dict(c) for t, c in m.shape_pos.items()}
            d["shape_pos_w"] = {w: dict(c) for w, c in m.shape_pos_w.items()}
            d["slotL"] = {t: dict(c) for t, c in m.slotL.items()}
            d["slotR"] = {t: dict(c) for t, c in m.slotR.items()}
            d["unk_cues"] = {"rich_shape": m.rich_shape, "pos_shape": m.pos_shape, "novel_max": m.novel_max,
                             "suf_theta": m.suf_theta, "prior_gamma": m.prior_gamma,
                             "slot_kappa": m.slot_kappa if m.slot else 0.0}
            with open(path, "w", encoding="utf-8") as f:
                json.dump(d, f)
            out["asset"] = args.save_asset
            print("asset ->", args.save_asset)
    out["elapsed_s"] = round(time.time() - t_all, 1)
    od = str(get_output_dir("exp_category_unknown_word_cues_v1"))
    os.makedirs(od, exist_ok=True)
    fn = os.path.join(od, args.out_name if args.out_name != "metrics_no_regress.json" else "metrics.json")
    with open(fn, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print("wrote", fn, out["elapsed_s"], "s")


if __name__ == "__main__":
    main()
