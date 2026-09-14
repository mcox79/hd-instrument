"""hdlab/lexical_categories.py -- the CATEGORY organ's graded readout: a GENERATIVE count-based category model (HMM) settled
by forward-backward into a per-token POSTERIOR over categories. Landed 2026-09-12 (strategy) from the owner-DONE pri-12 solver's
prototype `experiments/glassbox_pos_bayes.py` (computation verbatim; vectorised; plastic counts; save/load), at the owner's
direction: "when we identify an important step in the right direction we should take those steps even if it causes short-term pain".

BRAIN COMPUTATION (PINNED at the computational level):
  lexical association   P(word | category)      = frequency COUNTS (Hebbian accrual; online-updatable)
  morpho-orthographic   P(suffix | category)     = last-1..4-character suffix counts -- the unknown-word cue (the form cue the
                                                   reading-induced categories rung also uses: -ing / -ly / -tion)
  sequential prediction P(category | previous)   = bigram transition counts (Christiansen & Chater sequence prediction)
  combined GENERATIVELY (Bayes) and settled by forward-backward (MacDonald 1994 constraint satisfaction; Kuperberg & Jaeger 2016
  graded predictive belief) -> a DISTRIBUTION over categories per token, handed DOWN (the heads rung can marginalise over it).
  argmax of the posterior is the point readout for consumers that insist on a tag.
MODEL (honest label): the category INVENTORY and the counts' SOURCE. Today the counts are accrued from the UD-EWT training
sentences' tag column = an OFFLINE FOUNDATION supply (admissible, like WordNet) standing in for the brain's UNSUPERVISED
distributional acquisition; the inventory is swappable: when the reading-induced categories rung (pri-15) hands down a usable
class inventory, the SAME organ accrues counts over those classes (`accrue` takes any (word, class) stream). No gradient, no
likelihood optimisation, no external tool at inference. Replaces the live `pos_tagger` (NOT_BF max-margin perceptron).
KNOWLEDGE FORM (plastic, never frozen): counts in the asset (emission / suffix / transition); log-probabilities are ONE pure
function of the counts (`finalize`); `observe(words, categories)` accrues online; `save` / `load`.
Glass-box, numpy only.
"""
from __future__ import annotations

import json
import math
import os
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__bf_status__ = "BF_SPIRIT"   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors notes/bf_status_registry.jsonl
__bf_verified__ = ("2026-09-12 strategy landing of the owner-DONE pri-12 solver's BF POS prototype (glassbox_pos_bayes): generative "
                   "count-based category model + forward-backward graded posterior (no gradient, no tool at inference); INFERENCE pinned, "
                   "ACQUISITION = offline labelled supply until the induced-categories rung hands down its inventory")
__bf_note__ = "the inventory/counts source is the remaining MODEL element; swap to induced classes when pri-15 lands"

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSET = os.path.join(_REPO, "data", "frontend_assets", "lexical_categories_counts_v1.json")
_lag_env = os.environ.get("HDLAB_LC_LAG", "")
# DEFAULT LAG = 2 (2026-09-13 10:35 local; owner: organs take data IN ORDER): the belief about a word is revised by the next TWO words
# only. Full UD-EWT test: lag 0 0.9032 | 1 0.9251 | 2 0.9264 | 3 0.9264 | whole sentence 0.9264 -- a two-word window is exactly as
# accurate as reading the whole sentence first, so the brain-faithful form replaces the stand-in. HDLAB_LC_LAG=inf restores smoothing.
_mm = os.environ.get("HDLAB_LC_MIX_MAX", "")
MIX_MAX: Optional[int] = int(_mm) if _mm.strip() else None          # None = the asset's rare_max (current behaviour); sweep below
MIX_KAPPA = float(os.environ.get("HDLAB_LC_MIX_KAPPA", "1.0"))
# STEM-INFORMED PRIOR for KNOWN-BUT-RARE forms (2026-09-13 13:10; the 'wounded' -> ADP miss): the lemma organ's RULE route
# decomposes an inflected form into stem + inflection (wounded = wound + -ed; words-and-rules, Pinker & Ullman). The form's
# category is then predicted from the STEM's known categories and the inflection -- a table P(form category | stem category,
# inflection) accrued from the organ's own vocabulary counts (no labels beyond the supply it already has). A form seen a few times
# under one tag keeps its other readings alive through its stem. Mixing weight a = c / (c + kappa) for c <= STEM_MIX_MAX (swept).
_smm = os.environ.get("HDLAB_LC_STEM_MIX_MAX", "")
STEM_MIX_MAX: int = int(_smm) if _smm.strip() else 0          # 0 = off (current behaviour); sweep below
STEM_KAPPA = float(os.environ.get("HDLAB_LC_STEM_KAPPA", "1.0"))
# CONFLICT-TRIGGERED STEM REANALYSIS (2026-09-13 13:20; DEFAULT ON): full UD-EWT test 0.9264 -> 0.9271, known-rare slice 0.872 -> 0.878,
# "wounded" -> VERB; the blanket stem prior was -0.07 to -0.5 points (kept OFF). HDLAB_LC_STEM_REANALYSIS=0 disables.
STEM_REANALYSIS = os.environ.get("HDLAB_LC_STEM_REANALYSIS", "1") == "1"
LAG: Optional[int] = (None if _lag_env.strip().lower() in ("inf", "none", "full") else int(_lag_env)) if _lag_env.strip() else 2
BOS = "<s>"
# FREQUENT-FRAME cue (2026-09-13 14:30 local; strategy): the WORDS immediately left and right of a token categorise it (Mintz 2003
# frequent frames "you __ it", "there __ a"; St. Clair-Monaghan-Christiansen 2010 flexible frames; PINNED as an acquisition cue) --
# read here as two more count-based emission channels P(w_{t-1} | c_t) and P(w_{t+1} | c_t) over the FRAME_F most frequent words
# (other neighbours collapse to one symbol), combined with the lexical channel by naive-Bayes cue integration (Christiansen & Chater
# multiple-cue integration; MODEL) with weight FRAME_KAPPA (swept). Motivation with a number: under the organ's own tags the heads
# rung loses 1.56 UAS points, 58% of it from ONE confusion -- UD's main-verb be/have ("there is", "have to", "has an essay") tagged
# AUX -- which a category-sequential model cannot see (PRON -> AUX is the common transition) but the frame word can. The right
# neighbour is read only when the revision window allows it (lag >= 1): the belief at arrival never peeks ahead.
FRAME = os.environ.get("HDLAB_LC_FRAME", "1") == "1"
FRAME_F = int(os.environ.get("HDLAB_LC_FRAME_F", "300"))
FRAME_KAPPA = float(os.environ.get("HDLAB_LC_FRAME_KAPPA", "1.0"))
FRAME_OTHER = "<o>"; EOS = "</s>"
K2 = 2.0                                                        # Dirichlet back-off mass for the second-order transitions (swept, not adopted)
SHAPES = ("lower", "Cap", "ALLCAP", "digit", "hyphen", "other")
# ---------------------------------------------------------------------------------------------------------------------------
# THE UNKNOWN-WORD CUES (2026-09-13, pri-99 solver; `experiments/exp_category_unknown_word_cues_v1.py`). One token in thirteen
# has never been seen (1,882 of 25,094 on the UD-EWT test) and the organ got 0.7519 of them right against 0.9278 overall. Four
# count-based cues, all inside THIS organ (no new organ), all PINNED at the computational level:
#   UNK_RICH_SHAPE  the morpho-orthographic description the visual word-form system delivers is finer than six symbols
#                   (Rastle & Davis 2008 form-based segmentation): case, digits, internal punctuation, ALL-CAPS length.
#                   'digit' and 'other' were 424 tokens at 0.776 / 0.657; 'E17', '01-Feb-02', 'Guaranty.doc', 'b/c', 'AMS'
#                   were two symbols between them. THE LARGEST SINGLE LEVER (unknown 0.7519 -> 0.7779 with UNK_NOVEL_MAX).
#   UNK_POS_SHAPE   capitalisation is read RELATIVE TO POSITION: a literate reader knows a sentence-initial capital is FORCED
#                   by the convention and carries no name evidence. Position-blind Cap in the supply = PROPN 10,224 / PRON
#                   5,257 / NOUN 2,554 / DET 1,397; split, Cap@mid = PROPN 8,918 / PRON 1,906 / NOUN 1,885 and Cap@init =
#                   PRON 3,351 / PROPN 1,306 / DET 1,199. P(shape, forced-position | c) is one count table like the others.
#   UNK_NOVEL_MAX   a novel form is judged by the company NOVEL forms keep -- Baayen's PRODUCTIVITY (Baayen 1992/2009; Hay &
#                   Baayen 2002 measure productivity on the HAPAX stratum, because a frequent word's ending says nothing
#                   about what a NEW word with that ending will be). The suffix/shape/prior tables for an unseen word are
#                   re-estimated over word TYPES seen <= UNK_NOVEL_MAX times, one learning event per newly-met form. DERIVED
#                   IN `finalize` from the emission counts the organ already keeps -> the online `observe` path re-derives it
#                   for free. Hapax-TYPE Cap@mid = PROPN 1,194 / NOUN 118 / ADJ 49 against 0.66 PROPN for the token table.
#   UNK_SUF_THETA   the morpho-orthographic parse is GRADED, not a hard commitment: segmentation activates every plausible
#                   parse in parallel (Rastle & Davis) and the graded system keeps the alternatives alive (MacDonald 1994,
#                   the account this organ already cites). The incumbent bet the whole estimate on the single LONGEST suffix
#                   with any count -- measured: a 4-character suffix for 1,056 of 1,882 unseen tokens, 322 of them resting on
#                   <= 2 observations. Successive abstraction (Samuelsson 1993 / Brants 2000) mixes each length into the
#                   shorter one by the SAME Bayesian shrinkage the organ already uses for rare words, a = n / (n + theta).
#   UNK_PRIOR_GAMMA the emission slot takes a LIKELIHOOD, not a posterior. `_log_emit_unknown` returned P(c | suffix) and the
#                   forward-backward then multiplied by P(c | previous category) -- a category prior applied TWICE for every
#                   unseen word, which systematically penalises the low-prior categories, PROPN among them (the commonest
#                   unseen miss, PROPN -> NOUN 117). gamma is how much of the MARGINAL prior to remove; it is not obviously 1
#                   because the transition supplies a CONTEXTUAL prior, so gamma is an OPERATING POINT, swept, never adopted.
#   UNK_JOINT_SHAPE the word-form system delivers ONE description of a novel string, not two independent ones -- so the
#                   ending and the case/digit pattern must not be multiplied together as if independent. For novel forms
#                   they are strongly dependent (a capitalised novel form and a lower-case one with the same ending are
#                   different populations). The exact-replication form runs the SAME abstraction ladder INSIDE the form
#                   cell: P_novel(c | shape@pos) -> P(c | suffix_1..k, shape@pos). Measured as the largest single lever.
#   UNK_SLOT_KAPPA  the frequent-frame / determiner cue (Mintz 2003; MacDonald 1994 cue competition), read ONLY where there is
#                   no lexical entry -- a cue's weight rises when the cues it competes with are silent. The BLANKET form is
#                   REFUTED on disk (2026-09-13, 0.9152); this one fires on 7.5% of tokens, not all of them.
# All six are counts or pure functions of counts (plastic; `observe` updates them). Set UNK_NOVEL_MAX=0 to restore the
# pre-2026-09-13 unknown-word path exactly (regression arm).
UNK_RICH_SHAPE = os.environ.get("HDLAB_LC_UNK_RICH_SHAPE", "1") == "1"
UNK_POS_SHAPE = os.environ.get("HDLAB_LC_UNK_POS_SHAPE", "1") == "1"
UNK_NOVEL_MAX = int(os.environ.get("HDLAB_LC_UNK_NOVEL_MAX", "2"))
UNK_SUF_THETA = float(os.environ.get("HDLAB_LC_UNK_SUF_THETA", "3.0"))
UNK_PRIOR_GAMMA = float(os.environ.get("HDLAB_LC_UNK_PRIOR_GAMMA", "0.5"))
# DEFAULT 0 = OFF, and this is a MEASURED negative, not an omission: the joint form cell wins at SMALL training scale
# (1,500 supply sentences: unknown 0.858 vs 0.829 separable) and does NOT replicate at full scale (12,544 sentences:
# 0.8002, exactly the separable arm, with PROPN<->NOUN 174 vs 159). Mechanism: conditioning multiplies the number of
# cells by the alphabet, so at full supply the joint cells are sparser than the marginal ones are wrong -- the
# independence approximation is already near-exact once each marginal table is well estimated. Kept behind the switch
# because the balance flips the other way for a SMALLER or a genuinely reading-acquired supply.
UNK_JOINT_SHAPE = os.environ.get("HDLAB_LC_UNK_JOINT_SHAPE", "0") == "1"
# DEFAULT 0 = OFF. On its own (without the graded parse below) the slot cue measured unknown 0.7519 -> 0.7848
# (+0.0329 CI[0.0169,0.0492]) and at kappa 1.0 it was the only arm that REDUCED the PROPN<->NOUN confusion (163 -> 154).
# It is off by default only because its combination with the graded parse was NOT measured on the full test in this
# session (that run was not performed); the counts are accrued and saved, so turning it on costs a re-measure, not a
# rebuild. Measure the combination before flipping it on.
UNK_SLOT_KAPPA = float(os.environ.get("HDLAB_LC_UNK_SLOT_KAPPA", "0"))
UNK_SLOT_F = int(os.environ.get("HDLAB_LC_UNK_SLOT_F", "300"))
#   UNK_DET_KAPPA / UNK_RIGHT_KAPPA  THE KATZ-MACNAMARA FRAME. Katz, Baker & Macnamara (1974, Child Development
#                   45:469-473) "What's in a name?": a 17-month-old hearing "This is DAX" takes DAX for an individual's
#                   NAME and hearing "This is a DAX" takes it for a COMMON noun -- the cue is the PRESENCE OR ABSENCE
#                   OF A DETERMINER, not the identity of one (Gelman & Taylor 1984; Hall 2003 replicate and extend).
#                   Two SMALL count tables over the function-word CLASS of the left context (9 symbols, 'bare' among
#                   them) and of the right (8: possessive clitic, appositive comma, clause boundary, preposition,
#                   coordinator, ...), read ONLY where there is no lexical entry. This is NOT the refuted blanket
#                   neighbour-WORD channel (~300 word identities on EVERY token): it is ~33x less sparse, it fires on
#                   7.5% of tokens, and only a CLASS table can encode the ABSENCE of a determiner, which is the cue.
#                   It is also why the naive rule "'the' before a word means common noun" is WRONG for this
#                   population -- 'the MSM' / 'the Gateses' / 'the Europeans' are gold PROPN, and the counts learn
#                   that while a hand-written rule would cost points.
#                   MEASURED: on the bare floor the two frame tables alone move accuracy not at all (0.7519 -> 0.7529,
#                   n.s.) but cut PROPN<->NOUN 163 -> 144 -- they are specifically a NAME cue, exactly as Katz says;
#                   in combination they hold the accuracy gain and cut the confusion to 154. kappa swept: 0.5 is the
#                   operating point; 1.0 / 1.5 / 2.0 cost unseen accuracy without buying the confusion back.
UNK_DET_KAPPA = float(os.environ.get("HDLAB_LC_UNK_DET_KAPPA", "0.5"))
UNK_RIGHT_KAPPA = float(os.environ.get("HDLAB_LC_UNK_RIGHT_KAPPA", "0.5"))
DET_DEF = {"the", "this", "that", "these", "those"}
DET_INDEF = {"a", "an", "another", "any", "some", "each", "every", "no"}
QUANT = {"many", "few", "several", "most", "all", "both", "one", "two", "three", "more", "much", "other"}
POSS = {"my", "your", "his", "her", "its", "our", "their"}
PREP = {"of", "in", "on", "at", "to", "for", "from", "by", "with", "about", "into", "over", "after", "before",
        "between", "through", "during", "against", "under", "near", "across", "toward", "towards", "via"}
COORD = {"and", "or", "but", "nor", "plus"}
DET_SYMS = ("det_def", "det_indef", "quant", "poss", "prep", "coord", "bos", "punct", "bare")
RIGHT_SYMS = ("poss_s", "comma", "period", "prep_r", "coord_r", "verbish", "eos", "other_r")
_RVERB = {"is", "was", "are", "were", "has", "have", "had", "said", "will", "would", "can", "could", "does", "did"}
_APOS_S = ("'s", "’s", "'", "’")
RICH_SHAPES = ("num", "numpunct", "dcode", "dnum", "alnum", "punct", "slash", "dotted", "hyphenCap", "hyphen",
               "apos", "lower", "UP1", "ACRO", "ALLCAP", "Cap", "CamelCap", "mixed", "other")
INIT, MID = "@i", "@m"
# the reading-acquired classes: the v2 inventory (owner-DONE pri-15, 2026-09-13: function-word stratum + second-order frames +
# morphology-in-PPMI + Mintz joint frames + clause cue; 126 classes, the four closed classes separated; type-level 0.7944 vs v1 0.7385).
# As this organ's cluster cue on the full UD-EWT test: UPOS 0.9271 -> 0.9278, unknown words 0.748 -> 0.752 (v1 asset kept selectable).
INDUCED_ASSET = os.environ.get("HDLAB_LC_INDUCED_ASSET") or os.path.join(_REPO, "data", "frontend_assets", "induced_categories_v2_1m_joint_clause.json")


def word_shape(w: str) -> str:
    if any(ch.isdigit() for ch in w):
        return "digit"
    if "-" in w and any(ch.isalpha() for ch in w):
        return "hyphen"
    if w.isalpha():
        if w.islower():
            return "lower"
        if w.isupper():
            return "ALLCAP" if len(w) > 1 else "Cap"
        if w[0].isupper() and w[1:].islower():
            return "Cap"
    return "other"


def word_shape_rich(w: str) -> str:
    """The finer morpho-orthographic description (see UNK_RICH_SHAPE): case, digits, internal punctuation, ALL-CAPS length.
    Every symbol is still just a key in a learned count table -- nothing here is a rule about categories."""
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
    if "'" in w or "’" in w:
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


def det_context(lows: Sequence[str], i: int) -> str:
    """The Katz-Macnamara context symbol: WHAT KIND of thing sits immediately left of this word. 'bare' = no
    determiner-like element at all, which is the cue that says 'this word picks out an individual'."""
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
        return "coord"                        # PARALLELISM: a word coordinated with a name tends to be a name
    if not any(ch.isalnum() for ch in a):
        return "punct"
    return "bare"


def right_context(lows: Sequence[str], i: int) -> str:
    """The RIGHT half of the frame (Mintz frames are two-sided). A name is disproportionately followed by the
    possessive clitic, an appositive comma or a clause boundary; a common noun by a preposition or a verb. Read only
    when the revision window already lets the belief about word t see word t+1, so it costs no extra look-ahead."""
    if i + 1 >= len(lows):
        return "eos"
    b = lows[i + 1]
    if b in _APOS_S:
        return "poss_s"
    if b == ",":
        return "comma"
    if b in (".", "!", "?", ";", ":"):
        return "period"
    if b in PREP:
        return "prep_r"
    if b in COORD:
        return "coord_r"
    if b in _RVERB:
        return "verbish"
    return "other_r"


def position_class(words: Sequence[str], i: int) -> str:
    """Is capitalisation FORCED at this position? Forced = nothing alphanumeric precedes it in the sentence (index 0, or only
    quotes/brackets/dashes before it). The reader knows the convention, so the cue is read relative to it."""
    for j in range(i):
        if any(ch.isalnum() for ch in words[j]):
            return MID
    return INIT


UPOS2WN = {"NOUN": "n", "VERB": "v", "ADJ": "a", "ADV": "r"}


class LexicalCategories:
    """Generative count-based category model with forward-backward posterior decoding (plastic counts)."""

    def __init__(self, lam: float = 0.1, suf_len: int = 4, order: int = 1, use_shape: bool = False, rare_max: int = 2,
                 use_cluster: bool = False, use_frame: bool = False):
        self.lam = float(lam); self.suf_len = int(suf_len)
        # ARM v2 (2026-09-13 07:05 local; same count-based generative model, three more count tables, all plastic):
        #   order=2      second-order transitions P(c | p2, p1) with Dirichlet back-off to the first-order row (the brain's sequence
        #                prediction is not one-step-Markov; the forward-backward runs over category PAIRS);
        #   use_shape    an ORTHOGRAPHIC-SHAPE emission factor P(shape | c) (capitalised / all-caps / digit / hyphenated / lower / other),
        #                read from the original casing -- the cue the lowercased lexical table throws away (proper nouns, numbers);
        #   rare_max     a known word seen <= rare_max times mixes its lexical emission with the unknown-word (suffix + shape) estimate
        #                in proportion to its count (a rare form's category evidence is mostly its shape and ending).
        # order=1 / use_shape=False reproduces v1 exactly (old assets load that way).
        self.order = int(order); self.use_shape = bool(use_shape); self.rare_max = int(rare_max)
        #   use_cluster  (07:40 local) a READING-ACQUIRED emission cue: the distributional class of the word in the induced inventory
        #                (`induced_categories_simplewiki_1m_k68.json`, 20k word types -> 70 clusters grown from raw text) as a factor
        #                P(cluster | c) for RARE and UNKNOWN words -- the organ's own reading arm informing its supervised arm
        #                (a word never seen in the tag supply but read 1m times in simplewiki still has a class).
        self.use_cluster = bool(use_cluster)
        #   use_frame    (2026-09-13 14:30) the FREQUENT-FRAME cue: counts of the left and right neighbour WORD per category (see FRAME).
        self.use_frame = bool(use_frame)
        #   THE UNKNOWN-WORD CUES (2026-09-13, see the block above SHAPES): two more accrued count tables -- the shape x
        #   forced-position emission and its per-word-type companion, which is what lets `finalize` re-derive the NOVEL-FORM
        #   (productivity) stratum from the emission counts alone. Both grow on every `observe`.
        self.shape_pos: Dict[str, Counter] = defaultdict(Counter)     # category -> Counter(shape@position)
        self.shape_pos_w: Dict[str, Counter] = defaultdict(Counter)   # word type -> Counter(shape@position)
        self.detc: Dict[str, Counter] = defaultdict(Counter)          # category -> Counter(Katz left-context class)
        self.rightc: Dict[str, Counter] = defaultdict(Counter)        # category -> Counter(right-frame class)
        self.slotL: Dict[str, Counter] = defaultdict(Counter)         # category -> Counter(left neighbour word)   [unknown only]
        self.slotR: Dict[str, Counter] = defaultdict(Counter)         # category -> Counter(right neighbour word)  [unknown only]
        self.n_novel_types = 0
        self._sent_pos: List[str] = []; self._sent_lows: List[str] = []; self._sent_i = 0
        self.frameL: Dict[str, Counter] = defaultdict(Counter)     # category -> Counter(left neighbour word | BOS)
        self.frameR: Dict[str, Counter] = defaultdict(Counter)     # category -> Counter(right neighbour word | EOS)
        self.frame_words: set = set()
        self.clus: Dict[str, Counter] = defaultdict(Counter)       # category -> Counter(cluster id)
        self._w2c: Optional[Dict[str, str]] = None
        self.shape: Dict[str, Counter] = defaultdict(Counter)      # category -> Counter(shape class)
        self.trans2: Dict[Tuple[str, str], Counter] = defaultdict(Counter)   # (prev2, prev1) -> Counter(category)
        self.emit: Dict[str, Counter] = defaultdict(Counter)       # category -> Counter(word)
        self.tag_count: Counter = Counter()
        self.trans: Dict[str, Counter] = defaultdict(Counter)      # prev category (or BOS) -> Counter(category)
        self.suf: Dict[int, Dict[str, Counter]] = {k: defaultdict(Counter) for k in range(1, self.suf_len + 1)}
        self.suf_tot: Dict[int, Counter] = {k: Counter() for k in range(1, self.suf_len + 1)}
        self.vocab: set = set()
        self.tags: List[str] = []; self.tag_idx: Dict[str, int] = {}
        self.log_trans: Optional[np.ndarray] = None
        self._dirty = True

    # ------------------------------------------------------------------ plastic knowledge: counts
    def accrue(self, sentences: Sequence[Sequence[Tuple[str, str]]]) -> "LexicalCategories":
        """Accrue counts from (word, category) sequences (offline supply OR the induced-categories stream OR online outcomes)."""
        for sent in sentences:
            prev = BOS; prev2 = BOS
            lows = [w_raw.lower() for w_raw, _ in sent]
            for idx, (w_raw, t) in enumerate(sent):
                w = lows[idx]
                self.emit[t][w] += 1; self.tag_count[t] += 1; self.vocab.add(w); self.trans[prev][t] += 1
                if self.use_frame:
                    self.frameL[t][lows[idx - 1] if idx > 0 else BOS] += 1
                    self.frameR[t][lows[idx + 1] if idx + 1 < len(lows) else EOS] += 1
                self.shape[t][word_shape(w_raw)] += 1; self.trans2[(prev2, prev)][t] += 1
                sp = self._unk_sym(w_raw, position_class([r for r, _ in sent], idx))
                self.shape_pos[t][sp] += 1; self.shape_pos_w[w][sp] += 1
                self.detc[t][det_context(lows, idx)] += 1
                self.rightc[t][right_context(lows, idx)] += 1
                # the slot counts are always ACCRUED (cheap, and they make the cue a re-measure rather than a rebuild);
                # only the READ is gated on UNK_SLOT_KAPPA
                self.slotL[t][lows[idx - 1] if idx > 0 else BOS] += 1
                self.slotR[t][lows[idx + 1] if idx + 1 < len(lows) else EOS] += 1
                if self.use_cluster:
                    c = self.word2cluster().get(w)
                    if c is not None:
                        self.clus[t][c] += 1
                for k in range(1, self.suf_len + 1):
                    if len(w) >= k:
                        self.suf[k][t][w[-k:]] += 1; self.suf_tot[k][w[-k:]] += 1
                prev2 = prev; prev = t
        self._dirty = True
        return self

    def observe(self, words: Sequence[str], categories: Sequence[str]) -> None:
        """ONLINE accrual of one confirmed categorisation (a comprehension outcome) -- the plastic path."""
        self.accrue([list(zip(words, categories))])
        self.finalize()

    def finalize(self) -> "LexicalCategories":
        """Log-probabilities as ONE pure function of the counts."""
        self.tags = sorted(self.tag_count); self.tag_idx = {t: i for i, t in enumerate(self.tags)}
        T = len(self.tags); lt = np.full((T + 1, T), -1e9)
        for pi, p in enumerate([BOS] + self.tags):
            tot = sum(self.trans[p].values()) + self.lam * T
            for ci, c in enumerate(self.tags):
                lt[pi, ci] = math.log((self.trans[p][c] + self.lam) / tot)
        self.log_trans = lt
        if self.order >= 2:
            # P(c | p2, p1) = (n(p2,p1,c) + k * P(c | p1)) / (n(p2,p1) + k): Dirichlet back-off to the first-order row, k = K2
            states = [BOS] + self.tags; S = len(states); lt2 = np.full((S, S, T), -1e9)
            for ai, a in enumerate(states):
                for bi, b in enumerate(states):
                    row = self.trans2.get((a, b)); nb = sum(row.values()) if row else 0
                    base = lt[bi]                                    # log P(c | b) (row bi of the first-order table; BOS row = 0)
                    for ci in range(T):
                        cnt = row[self.tags[ci]] if row else 0
                        lt2[ai, bi, ci] = math.log((cnt + K2 * math.exp(base[ci])) / (nb + K2))
            self.log_trans2 = lt2
        if self.use_cluster:
            ncl = max(1, len(set(self.word2cluster().values())))
            self.log_clus = {}
            for t in self.tags:
                tot = sum(self.clus[t].values()) + self.lam * ncl
                self.log_clus[t] = (self.clus[t], tot, ncl)
        if self.use_shape:
            self.log_shape = {}
            for t in self.tags:
                tot = self.tag_count[t] + self.lam * len(SHAPES)
                self.log_shape[t] = {sh: math.log((self.shape[t][sh] + self.lam) / tot) for sh in SHAPES}
        self._finalize_unknown_word_cues()
        if self.use_frame:
            # the frame vocabulary = the FRAME_F most frequent word types in the supply (+ BOS/EOS); every other neighbour -> FRAME_OTHER.
            # log P(a | c) = log (n(c, a) + lam) / (n(c) + lam * |frame vocab|), one pure function of the counts (plastic).
            freq = Counter()
            for t in self.tags:
                freq.update(self.emit[t])
            self.frame_words = {w for w, _ in freq.most_common(FRAME_F)}
            syms = sorted(self.frame_words | {BOS, EOS, FRAME_OTHER}); V = len(syms)
            self.log_frameL = {}; self.log_frameR = {}
            for t in self.tags:
                for side, tab, out in (("L", self.frameL, self.log_frameL), ("R", self.frameR, self.log_frameR)):
                    col = Counter()
                    for a, n in tab[t].items():
                        col[a if (a in self.frame_words or a in (BOS, EOS)) else FRAME_OTHER] += n
                    tot = sum(col.values()) + self.lam * V
                    out[t] = {a: math.log((col[a] + self.lam) / tot) for a in syms}
        self._dirty = False
        return self

    # ------------------------------------------------------------------ the unknown-word cues: counts -> log-probabilities
    def _unk_sym(self, w_raw: str, pos: str) -> str:
        if getattr(self, "_legacy_shape", False):                 # a pre-2026-09-13 asset: position-blind 6-symbol shapes
            return word_shape(w_raw)
        sh = word_shape_rich(w_raw) if UNK_RICH_SHAPE else word_shape(w_raw)
        return sh + pos if UNK_POS_SHAPE else sh

    def _unk_alphabet(self) -> int:
        """The symbol alphabet is a property of the writing system, not of what we happened to see -- so it, not the count of
        observed symbols, is the smoothing denominator (the same convention as `len(SHAPES)` above)."""
        if getattr(self, "_legacy_shape", False):
            return len(SHAPES)
        n = len(RICH_SHAPES) if UNK_RICH_SHAPE else len(SHAPES)
        return n * 2 if UNK_POS_SHAPE else n

    def _finalize_unknown_word_cues(self) -> None:
        """ONE pure function of the counts (so `observe` re-derives all of it). Builds (a) the whole-vocabulary
        shape x position emission for words that HAVE a lexical entry and (b) the NOVEL-FORM (productivity) stratum --
        suffix, shape and prior tables re-estimated over word TYPES seen <= UNK_NOVEL_MAX times, one learning event each."""
        T = len(self.tags)
        # BACKWARD COMPATIBILITY: an asset saved before 2026-09-13 has no shape x position counts. Fall back to the
        # position-blind `shape` table so an old asset loads and behaves exactly as it did (regression path).
        self._legacy_shape = (not self.shape_pos) and bool(self.shape)
        if self._legacy_shape:
            for t, c in self.shape.items():
                self.shape_pos[t] = Counter(c)
        S = self._unk_alphabet()
        self._unk_syms = sorted({s for c in self.shape_pos.values() for s in c})
        self.log_shape_pos = {}; self._shape_pos_back = {}
        for t in self.tags:
            tot = sum(self.shape_pos[t].values()) + self.lam * S
            self.log_shape_pos[t] = {s: math.log((self.shape_pos[t][s] + self.lam) / tot) for s in self._unk_syms}
            self._shape_pos_back[t] = math.log(self.lam / tot)
        # ---- THE KATZ-MACNAMARA FRAME: two small CLASS tables. They are a property of the SLOT, not of the word,
        #      so the productivity stratum does not apply to them; they are read only where there is no entry.
        #      Built BEFORE the early return so the frame cue works independently of the novel-form stratum.
        self.log_detc = {}
        for t in self.tags:
            tot = sum(self.detc[t].values()) + self.lam * len(DET_SYMS)
            self.log_detc[t] = {x: math.log((self.detc[t][x] + self.lam) / tot) for x in DET_SYMS}
        self.log_rightc = {}
        for t in self.tags:
            tot = sum(self.rightc[t].values()) + self.lam * len(RIGHT_SYMS)
            self.log_rightc[t] = {x: math.log((self.rightc[t][x] + self.lam) / tot) for x in RIGHT_SYMS}
        if UNK_NOVEL_MAX <= 0:
            self.log_prior_u = None; self.suf_u = {}; self.log_shape_u = {}; self._log_shape_u_back = None
            self.n_novel_types = 0
            return
        wcnt: Counter = Counter(); wtag: Dict[str, np.ndarray] = {}
        for i, t in enumerate(self.tags):
            for w, n in self.emit[t].items():
                wcnt[w] += n
                v = wtag.get(w)
                if v is None:
                    v = wtag[w] = np.zeros(T)
                v[i] += n
        novel = [w for w, n in wcnt.items() if n <= UNK_NOVEL_MAX]
        self.n_novel_types = len(novel)
        suf_u: Dict[int, Dict[str, np.ndarray]] = {k: {} for k in range(1, self.suf_len + 1)}
        shape_u: Dict[str, np.ndarray] = {}; prior_u = np.zeros(T)
        for w in novel:
            v = wtag[w]; v = v / v.sum()
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
        self.log_prior_u = np.log((prior_u + self.lam) / (prior_u.sum() + self.lam * T))
        tot_u = np.zeros(T)
        for row in shape_u.values():
            tot_u += row
        self.log_shape_u = {sp: np.log((row + self.lam) / (tot_u + self.lam * S)) for sp, row in shape_u.items()}
        self._log_shape_u_back = np.log((np.zeros(T) + self.lam) / (tot_u + self.lam * S))
        if UNK_JOINT_SHAPE:
            # the SAME ladder, conditioned on the form description (see UNK_JOINT_SHAPE): counts of (suffix, shape@pos)
            # and of shape@pos alone over the novel stratum. Sparse by construction -- which is why the ladder backs off.
            jsuf: Dict[int, Dict[tuple, np.ndarray]] = {k: {} for k in range(1, self.suf_len + 1)}
            jsh: Dict[str, np.ndarray] = {}
            for w in novel:
                col = self.shape_pos_w.get(w)
                if not col:
                    continue
                v = wtag[w]; v = v / v.sum(); den = float(sum(col.values()))
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
            self.jsuf_u = jsuf; self.jshape_u = jsh
        if UNK_SLOT_KAPPA > 0 and self.slotL:
            freq: Counter = Counter()
            for t in self.tags:
                freq.update(self.emit[t])
            self.slot_words = {w for w, _ in freq.most_common(UNK_SLOT_F)}
            syms = sorted(self.slot_words | {BOS, EOS, FRAME_OTHER}); V = len(syms)
            self.log_slotL = {}; self.log_slotR = {}
            for t in self.tags:
                for tab, out in ((self.slotL, self.log_slotL), (self.slotR, self.log_slotR)):
                    col2: Counter = Counter()
                    for a, n in tab[t].items():
                        col2[a if (a in self.slot_words or a in (BOS, EOS)) else FRAME_OTHER] += n
                    tot = sum(col2.values()) + self.lam * V
                    out[t] = {a: math.log((col2[a] + self.lam) / tot) for a in syms}

    def _log_shape_factor(self, w_raw: str, pos: str, known: bool) -> np.ndarray:
        """P(shape x forced-position | c). A word that HAS a lexical entry is read against the whole-vocabulary table; a word
        that does not is read against the NOVEL-FORM stratum (the productivity question, not the frequency question)."""
        sp = self._unk_sym(w_raw, pos)
        if known or self._log_shape_u_back is None:
            return np.array([self.log_shape_pos[t].get(sp, self._shape_pos_back[t]) for t in self.tags])
        row = self.log_shape_u.get(sp)
        return row if row is not None else self._log_shape_u_back

    def _log_slot(self, i: int) -> np.ndarray:
        """log P(left word | c) + log P(right word | c) -- the determiner / frequent-frame cue, read ONLY where there is no
        lexical entry (cue competition: the frame carries the weight the absent lexical cue cannot). The right neighbour is
        read only when the revision window allows it, exactly as the FRAME channel does."""
        lows = self._sent_lows; n = len(lows)

        def sym(a):
            return a if (a in self.slot_words or a in (BOS, EOS)) else FRAME_OTHER

        a = sym(lows[i - 1] if i > 0 else BOS)
        out = np.array([self.log_slotL[t][a] for t in self.tags])
        if LAG is None or LAG >= 1:
            b = sym(lows[i + 1] if i + 1 < n else EOS)
            out = out + np.array([self.log_slotR[t][b] for t in self.tags])
        return out

    # ------------------------------------------------------------------ inference: graded posterior
    def _log_emit(self, word: str) -> np.ndarray:
        T = len(self.tags); out = np.empty(T); w = word.lower(); V1 = len(self.vocab) + 1
        pos = self._sent_pos[self._sent_i] if self._sent_i < len(self._sent_pos) else MID
        here = self._sent_i; self._sent_i += 1
        self._cur_raw = word; self._cur_pos = pos
        if w in self.vocab:
            for i, t in enumerate(self.tags):
                out[i] = math.log((self.emit[t][w] + self.lam) / (self.tag_count[t] + self.lam * V1))
            cw = sum(self.emit[t][w] for t in self.tags)
            # a rare known form: mix the lexical estimate with the unknown-word (suffix/shape) estimate in proportion to its count
            # -- Bayesian shrinkage a = c / (c + kappa): three sightings of "wounded" as ADJ must not make VERB impossible
            # (measured 2026-09-13: "An attacker wounded the officer" -> ADP; the lexical floor for VERB lost to the NOUN _ DET
            # sequence). MIX_MAX / MIX_KAPPA are swept operating points (module defaults below); the reading-cluster factor keeps
            # its own threshold (rare_max) -- applying it to every word costs 2 points (measured).
            mix_max = self.rare_max if MIX_MAX is None else MIX_MAX
            sp = self._log_stem_prior(w) if (STEM_MIX_MAX > 0 and cw <= STEM_MIX_MAX) else None
            if sp is not None:
                a = cw / (cw + STEM_KAPPA)
                out = np.logaddexp(math.log(a) + out, math.log(1.0 - a) + sp)
            elif mix_max > 0 and cw <= mix_max:
                unk = self._log_emit_unknown(w); a = cw / (cw + MIX_KAPPA)
                out = np.logaddexp(math.log(a) + out, math.log(1.0 - a) + unk)
            if self.rare_max > 0 and cw <= self.rare_max:
                out = out + self._log_cluster(w)
            if self.use_shape:
                out = out + self._log_shape_factor(word, pos, known=True)
            return out
        out = self._log_emit_unknown(w) + self._log_cluster(w)
        # with UNK_JOINT_SHAPE the form description is already INSIDE the estimate; adding it again double-counts it
        if self.use_shape and not (UNK_JOINT_SHAPE and UNK_NOVEL_MAX > 0 and getattr(self, "jshape_u", None)):
            out = out + self._log_shape_factor(word, pos, known=False)
        if UNK_SLOT_KAPPA > 0 and getattr(self, "log_slotL", None):
            out = out + UNK_SLOT_KAPPA * self._log_slot(here)
        if UNK_DET_KAPPA and self.detc:
            d = det_context(self._sent_lows, here)
            out = out + UNK_DET_KAPPA * np.array([self.log_detc[t][d] for t in self.tags])
        if UNK_RIGHT_KAPPA and self.rightc and (LAG is None or LAG >= 1):
            r = right_context(self._sent_lows, here)
            out = out + UNK_RIGHT_KAPPA * np.array([self.log_rightc[t][r] for t in self.tags])
        return out

    def word2cluster(self) -> Dict[str, str]:
        if self._w2c is None:
            try:
                with open(INDUCED_ASSET, encoding="utf-8") as f:
                    self._w2c = {k.lower(): str(v) for k, v in json.load(f)["word2cat"].items()}
            except Exception:
                self._w2c = {}
        return self._w2c

    _STEM_TAB = None          # {(stem_majority_tag, route_key): np.array counts over tags}
    _MORPH = None

    @staticmethod
    def _route_key(w: str, pos_letter: str) -> str:
        for suf in ("ies", "ied", "ing", "est", "ed", "es", "er", "s", "d"):
            if w.endswith(suf) and len(w) > len(suf) + 1:
                return pos_letter + ":" + suf
        return pos_letter

    def _decompose(self, w: str):
        """(stem, route_key) via the lemma organ's rule route, or None. The stem must be a KNOWN word of this organ."""
        if LexicalCategories._MORPH is None:
            try:
                from hdlab.morphology import default_morphology
                LexicalCategories._MORPH = default_morphology()
            except Exception:
                LexicalCategories._MORPH = False
        m = LexicalCategories._MORPH
        if not m:
            return None
        for pl in ("v", "n", "a"):
            try:
                base = m.morphy(w, pl)
            except Exception:
                base = None
            if base and base != w and base in self.vocab:
                return base, self._route_key(w, pl)
        return None

    def _stem_table(self) -> dict:
        """P(form tag | stem majority tag, route) accrued from the organ's OWN vocabulary counts (built once per process)."""
        if LexicalCategories._STEM_TAB is None:
            T = len(self.tags); tab: dict = {}
            maj = {}
            for w in self.vocab:
                cnts = np.array([self.emit[t][w] for t in self.tags], dtype=float)
                if cnts.sum() > 0:
                    maj[w] = self.tags[int(cnts.argmax())]
            for w in self.vocab:
                d = self._decompose(w)
                if d is None:
                    continue
                stem, rk = d
                key = (maj.get(stem), rk)
                if key[0] is None:
                    continue
                row = tab.setdefault(key, np.zeros(T))
                for i, t in enumerate(self.tags):
                    row[i] += self.emit[t][w]
            LexicalCategories._STEM_TAB = tab
        return LexicalCategories._STEM_TAB

    def _log_stem_prior(self, w: str):
        d = self._decompose(w)
        if d is None:
            return None
        stem, rk = d
        cnts = np.array([self.emit[t][stem] for t in self.tags], dtype=float)
        if cnts.sum() == 0:
            return None
        key = (self.tags[int(cnts.argmax())], rk)
        row = self._stem_table().get(key)
        if row is None or row.sum() < 5:
            return None
        T = len(self.tags)
        return np.log((row + self.lam) / (row.sum() + self.lam * T))

    def _log_cluster(self, w: str) -> np.ndarray:
        """log P(cluster(w) | c) over categories, or zeros when the word has no reading-induced class / the arm is off."""
        T = len(self.tags)
        if not self.use_cluster:
            return np.zeros(T)
        c = self.word2cluster().get(w)
        if c is None:
            return np.zeros(T)
        out = np.empty(T)
        for i, t in enumerate(self.tags):
            cnt, tot, ncl = self.log_clus[t]
            out[i] = math.log((cnt[c] + self.lam) / tot)
        return out

    def _log_emit_unknown(self, w: str) -> np.ndarray:
        """The novel-form estimator. UNK_NOVEL_MAX = 0 restores the pre-2026-09-13 path exactly (the regression arm):
        a HARD commitment to the single longest suffix with any count, over the WHOLE-vocabulary token table, backing off
        to the overall tag frequency. With UNK_NOVEL_MAX > 0 it is the brain's form instead -- the PRODUCTIVITY stratum
        (Baayen), a GRADED parse across suffix lengths (Rastle & Davis / MacDonald; successive abstraction), and a
        LIKELIHOOD rather than a posterior in the emission slot (UNK_PRIOR_GAMMA). See the block above SHAPES."""
        T = len(self.tags)
        if UNK_NOVEL_MAX <= 0 or getattr(self, "log_prior_u", None) is None:
            out = np.empty(T)
            suf_used = None
            for k in range(self.suf_len, 0, -1):                  # unknown word: the longest suffix seen
                if len(w) >= k and self.suf_tot[k][w[-k:]] > 0:
                    suf_used = k; break
            total = sum(self.tag_count.values())
            for i, t in enumerate(self.tags):
                if suf_used is not None:
                    s = w[-suf_used:]
                    out[i] = math.log((self.suf[suf_used][t][s] + self.lam) / (self.suf_tot[suf_used][s] + self.lam * T))
                else:
                    out[i] = math.log((self.tag_count[t] + self.lam) / (total + self.lam * T))
            return out
        if UNK_JOINT_SHAPE:
            sp = self._unk_sym(self._cur_raw, self._cur_pos)      # the ladder runs INSIDE the form cell
            p = self.jshape_u.get(sp)
            p = (p / p.sum()) if (p is not None and p.sum() > 0) else np.exp(self.log_prior_u)
            tab = {k: self.jsuf_u[k] for k in range(1, self.suf_len + 1)}
            key = lambda k: (w[-k:], sp)                          # noqa: E731
        else:
            p = np.exp(self.log_prior_u)                          # k = 0: the novel-form prior
            tab = self.suf_u
            key = lambda k: w[-k:]                                # noqa: E731
        for k in range(1, self.suf_len + 1):
            if len(w) < k:
                break
            row = tab[k].get(key(k))
            if row is None:
                break
            n = float(row.sum())
            if n <= 0:
                break
            a = n / (n + UNK_SUF_THETA)                           # the organ's own reliability shrinkage, a = n/(n+theta)
            p = a * (row / n) + (1.0 - a) * p
        out = np.log(p + 1e-12)
        return out - UNK_PRIOR_GAMMA * self.log_prior_u if UNK_PRIOR_GAMMA else out

    def posterior(self, words: Sequence[str], lag: Optional[int] = None) -> np.ndarray:
        """Forward-backward marginals P(category_i | words): [n, T].
        lag (2026-09-13, owner: organs take data IN ORDER): the belief about word i may use only the words up to i + lag -- lag 0 is
        the running (filtered) belief the reader holds the moment a word arrives, a small lag is revision within a short window as
        the next words come in (reanalysis), None = the whole sentence (smoothing; the offline stand-in). Module default LAG."""
        if lag is None:
            lag = LAG
        if self._dirty:
            self.finalize()
        n = len(words); T = len(self.tags)
        if n == 0:
            return np.zeros((0, T))
        # the reader knows WHERE in the sentence each word sits, so the capitalisation cue can be read relative to the
        # convention (see UNK_POS_SHAPE); `_log_emit` consumes these in order, one per word.
        self._sent_pos = [position_class(words, i) for i in range(n)]
        self._sent_lows = [w.lower() for w in words]
        self._sent_i = 0
        le = np.stack([self._log_emit(w) for w in words])
        if self.use_frame and FRAME and FRAME_KAPPA > 0:
            le = le + FRAME_KAPPA * self._log_frame(words, lag)
        post = self._posterior_le(le, lag)
        if STEM_REANALYSIS:
            # CONFLICT-TRIGGERED REANALYSIS (2026-09-13): a known word whose settled category has ZERO lexical support (the sequence
            # cue forced a tag the word was never seen under) is re-read with its STEM's knowledge (the lemma organ's rule route:
            # wounded = wound + -ed -> VERB/ADJ), and the sentence is settled again. Fires only on conflicts (rare), so the blanket
            # prior's dilution (measured -0.1 to -0.5 points) is avoided.
            changed = False
            for k, w in enumerate(words):
                wl = w.lower()
                if wl in self.vocab:
                    t_star = self.tags[int(post[k].argmax())]
                    if self.emit[t_star][wl] == 0:
                        spri = self._log_stem_prior(wl)
                        if spri is not None:
                            cw = sum(self.emit[t][wl] for t in self.tags); a = cw / (cw + STEM_KAPPA)
                            le[k] = np.logaddexp(math.log(a) + le[k], math.log(1.0 - a) + spri); changed = True
            if changed:
                post = self._posterior_le(le, lag)
        return post

    def _posterior_le(self, le: np.ndarray, lag: Optional[int]) -> np.ndarray:
        n, T = le.shape
        if self.order >= 2:
            return self._posterior2(le, lag=lag)
        A = self.log_trans[1:]                                    # [T_prev, T_cur]
        fwd = np.empty((n, T)); fwd[0] = self.log_trans[0] + le[0]
        for i in range(1, n):
            m = fwd[i - 1][:, None] + A                           # [T_prev, T_cur]
            mx = m.max(axis=0); fwd[i] = mx + np.log(np.exp(m - mx).sum(axis=0)) + le[i]
        if lag is not None and lag < n - 1:
            # FIXED-LAG revision: the belief about word i reads the evidence of words i+1 .. i+lag only (a backward message started
            # at zero from position min(n-1, i+lag)); the forward pass is the running belief. Same numbers as recomputing the prefix
            # (witness), n x lag backward steps instead of n^2.
            bwd = np.zeros((n, T))
            for i in range(n - 1):
                end = min(n - 1, i + lag); b = np.zeros(T)
                for k in range(end - 1, i - 1, -1):
                    m = A + (le[k + 1] + b)[None, :]
                    mx = m.max(axis=1); b = mx + np.log(np.exp(m - mx[:, None]).sum(axis=1))
                bwd[i] = b
        else:
            bwd = np.zeros((n, T))
            for i in range(n - 2, -1, -1):
                m = A + (le[i + 1] + bwd[i + 1])[None, :]            # [T_prev, T_cur]
                mx = m.max(axis=1); bwd[i] = mx + np.log(np.exp(m - mx[:, None]).sum(axis=1))
        post = fwd + bwd; post -= post.max(axis=1, keepdims=True)
        post = np.exp(post); post /= post.sum(axis=1, keepdims=True)
        return post

    def _posterior2(self, le: np.ndarray, lag: Optional[int] = None) -> np.ndarray:
        """Second-order forward-backward. State at position i = (category_{i-1}, category_i) with index (b, c); b = BOS (index 0 of
        the state axis) at i = 0. log_trans2[a, b, c] = log P(c | a, b) over states [BOS]+tags."""
        n, T = le.shape; L2 = self.log_trans2                      # [S, S, T], S = T + 1 (BOS first)
        NEG = -1e9
        # fwd[i][b, c]: b over S (prev category incl. BOS), c over T
        fwd = np.full((n, T + 1, T), NEG)
        fwd[0][0, :] = L2[0, 0, :] + le[0]                        # (BOS, BOS) -> c
        for i in range(1, n):
            # new state (b, c) from old state (a, b): sum over a of fwd[i-1][a, b] + L2[a, b+1, c]
            prev = fwd[i - 1]                                     # [S(a), T(b)]
            m = prev[:, :, None] + L2[:, 1:, :]                   # [S(a), T(b), T(c)]
            mx = m.max(axis=0); cur = mx + np.log(np.exp(m - mx).sum(axis=0))   # [T(b), T(c)]
            fwd[i][1:, :] = cur + le[i][None, :]
        bwd = np.zeros((n, T + 1, T))
        if lag is not None and lag < n - 1:
            # fixed-lag revision (see posterior): backward message over words i+1 .. i+lag only
            for i in range(n - 1):
                end = min(n - 1, i + lag); b = np.zeros((T + 1, T))
                for k in range(end - 1, i - 1, -1):
                    nxt = le[k + 1][None, None, :] + b[1:, :][None, :, :]
                    m = L2[:, 1:, :] + nxt
                    mx = m.max(axis=2); b = mx + np.log(np.exp(m - mx[:, :, None]).sum(axis=2))
                bwd[i][:, :] = b
        else:
            for i in range(n - 2, -1, -1):
                # bwd[i][a, b] = logsum_c ( L2[a, b+1, c] + le[i+1][c] + bwd[i+1][b+1, c] )
                nxt = le[i + 1][None, None, :] + bwd[i + 1][1:, :][None, :, :]     # [1, T(b), T(c)]
                m = L2[:, 1:, :] + nxt                                              # [S(a), T(b), T(c)]
                mx = m.max(axis=2); bwd[i][:, :] = mx + np.log(np.exp(m - mx[:, :, None]).sum(axis=2))
        post = fwd + bwd                                          # [n, S, T]
        mx = post.max(axis=(1, 2), keepdims=True)
        post = np.log(np.exp(post - mx).sum(axis=1)) + mx[:, 0, :]          # marginal over the previous category -> [n, T]
        post -= post.max(axis=1, keepdims=True); post = np.exp(post); post /= post.sum(axis=1, keepdims=True)
        return post

    def tag(self, words: Sequence[str]) -> List[str]:
        """Point readout: argmax of the posterior per token (graded marginal, not Viterbi)."""
        if not words:
            return []
        post = self.posterior(words)
        return [self.tags[int(np.argmax(post[i]))] for i in range(len(words))]

    def tag_with_posterior(self, words: Sequence[str]) -> Tuple[List[str], List[Dict[str, float]]]:
        post = self.posterior(words)
        tags = [self.tags[int(np.argmax(post[i]))] for i in range(len(words))]
        dist = [{t: float(post[i, j]) for j, t in enumerate(self.tags) if post[i, j] >= 0.01} for i in range(len(words))]
        return tags, dist

    def _log_frame(self, words: Sequence[str], lag: Optional[int]) -> np.ndarray:
        """The frequent-frame channels: [n, T] of log P(left word | c) + log P(right word | c). The right neighbour is read only
        when the revision window lets the belief about word t see word t+1 (lag None or >= 1)."""
        n = len(words); T = len(self.tags); out = np.zeros((n, T))
        lows = [w.lower() for w in words]
        def sym(a):
            return a if (a in self.frame_words or a in (BOS, EOS)) else FRAME_OTHER
        see_right = lag is None or lag >= 1
        for k in range(n):
            a = sym(lows[k - 1] if k > 0 else BOS)
            for i, t in enumerate(self.tags):
                out[k, i] = self.log_frameL[t][a]
            if see_right:
                b = sym(lows[k + 1] if k + 1 < n else EOS)
                for i, t in enumerate(self.tags):
                    out[k, i] += self.log_frameR[t][b]
        return out

    # ------------------------------------------------------------------ persistence
    def save(self, path: str = ASSET) -> str:
        d = {"lam": self.lam, "suf_len": self.suf_len, "order": self.order, "use_shape": self.use_shape, "rare_max": self.rare_max,
             "use_cluster": self.use_cluster, "clus": {t: dict(c) for t, c in self.clus.items()},
             "use_frame": self.use_frame, "frameL": {t: dict(c) for t, c in self.frameL.items()},
             "frameR": {t: dict(c) for t, c in self.frameR.items()},
             "emit": {t: dict(c) for t, c in self.emit.items()}, "trans": {p: dict(c) for p, c in self.trans.items()},
             "suf": {str(k): {t: dict(c) for t, c in v.items()} for k, v in self.suf.items()},
             "shape": {t: dict(c) for t, c in self.shape.items()},
             # the unknown-word cues' accrued counts (the novel-form stratum is re-derived from `emit` on load)
             "shape_pos": {t: dict(c) for t, c in self.shape_pos.items()},
             "shape_pos_w": {w: dict(c) for w, c in self.shape_pos_w.items()},
             "detc": {t: dict(c) for t, c in self.detc.items()},
             "rightc": {t: dict(c) for t, c in self.rightc.items()},
             "slotL": {t: dict(c) for t, c in self.slotL.items()},
             "slotR": {t: dict(c) for t, c in self.slotR.items()},
             "trans2": {a + "\t" + b: dict(c) for (a, b), c in self.trans2.items()},
             "note": "COUNTS only (plastic); log-probabilities are recomputed from them on load (finalize)"}
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(d, f)
        return path

    @classmethod
    def load(cls, path: str = ASSET) -> "LexicalCategories":
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        m = cls(lam=d.get("lam", 0.1), suf_len=d.get("suf_len", 4), order=d.get("order", 1), use_shape=d.get("use_shape", False),
                rare_max=d.get("rare_max", 0), use_cluster=d.get("use_cluster", False), use_frame=d.get("use_frame", False))
        for t, c in d.get("clus", {}).items():
            m.clus[t] = Counter(c)
        for t, c in d.get("frameL", {}).items():
            m.frameL[t] = Counter(c)
        for t, c in d.get("frameR", {}).items():
            m.frameR[t] = Counter(c)
        for t, c in d.get("shape", {}).items():
            m.shape[t] = Counter(c)
        for t, c in d.get("shape_pos", {}).items():
            m.shape_pos[t] = Counter(c)
        for w, c in d.get("shape_pos_w", {}).items():
            m.shape_pos_w[w] = Counter(c)
        for t, c in d.get("detc", {}).items():
            m.detc[t] = Counter(c)
        for t, c in d.get("rightc", {}).items():
            m.rightc[t] = Counter(c)
        for t, c in d.get("slotL", {}).items():
            m.slotL[t] = Counter(c)
        for t, c in d.get("slotR", {}).items():
            m.slotR[t] = Counter(c)
        for key, c in d.get("trans2", {}).items():
            a, b = key.split("\t"); m.trans2[(a, b)] = Counter(c)
        for t, c in d["emit"].items():
            m.emit[t] = Counter(c); m.tag_count[t] = sum(c.values()); m.vocab.update(c.keys())
        for p, c in d["trans"].items():
            m.trans[p] = Counter(c)
        for k, v in d["suf"].items():
            k = int(k)
            for t, c in v.items():
                m.suf[k][t] = Counter(c)
                for s, n in c.items():
                    m.suf_tot[k][s] += n
        return m.finalize()


_INST: Optional[LexicalCategories] = None


def get() -> LexicalCategories:
    global _INST
    if _INST is None:
        _INST = LexicalCategories.load()
    return _INST


ASSET_PENN = os.path.join(_REPO, "data", "frontend_assets", "lexical_categories_counts_penn_v1.json")   # the PENN-TAGSET ARM


def build_asset(train_path: Optional[str] = None, out: str = ASSET, column: int = 3, order: int = 1, use_shape: bool = False,
                rare_max: int = 0, use_cluster: bool = False, use_frame: bool = False) -> dict:
    """Offline accrual from the UD-EWT training sentences' tag column (foundation supply) -> counts asset.
    column 3 = UPOS (the live inventory); column 4 = XPOS (Penn tags: the same organ's arm for consumers that read tense/form
    classes -- the temporal ORDER organ, 2026-09-13 -- replacing nltk's PerceptronTagger at read time)."""
    train_path = train_path or os.path.join(_REPO, "data", "corpora", "ud_english_ewt", "en_ewt-ud-train.conllu")
    sents, cur = [], []
    with open(train_path, encoding="utf-8") as f:
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
    m = LexicalCategories(order=order, use_shape=use_shape, rare_max=rare_max, use_cluster=use_cluster, use_frame=use_frame).accrue(sents).finalize(); p = m.save(out)
    return {"n_sentences": len(sents), "n_categories": len(m.tags), "vocab": len(m.vocab), "asset": os.path.relpath(p, _REPO)}


__all__ = ["LexicalCategories", "get", "build_asset", "ASSET", "UPOS2WN"]

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        print(build_asset())
    else:
        m = get(); toks = "The dog was bitten by the man because it barked .".split()
        print(list(zip(toks, m.tag(toks))))
