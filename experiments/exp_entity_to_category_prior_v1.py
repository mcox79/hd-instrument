"""exp_entity_to_category_prior_v1 -- THE ENTITY LAYER FEEDS A TOP-DOWN PRIOR BACK TO THE CATEGORY ORGAN (pri-104).

PROBLEM (the brief): "the MSM", "the Gateses", "the Europeans" are names WITH a determiner and "the CEO" is not.
No FORM cue separates them. What does is whether the string is being used to pick out an INDIVIDUAL the passage
already knows -- which the entity layer decides DOWNSTREAM of the category decision it should be informing. The
dependency runs both ways and only one direction is wired.

HOW THE BRAIN DOES THIS (the opening move; structure + computation, then the parameters swept):
  STRUCTURE. A proper name is a word that refers to an INDIVIDUAL (Kripke 1980, rigid designation). Proper-name
  processing engages a referent route distinct from the common-noun semantic route -- the left temporal pole /
  anterior temporal lobe (Semenza 2006/2009 proper-name anomia; Damasio et al. 1996; Gorno-Tempini et al. 1998),
  sitting ABOVE the posterior-temporal word-form / category level. The discourse model of who-is-who is a set of
  FILE CARDS (Heim 1982 file-change semantics) built and re-accessed by content-addressable retrieval (Lewis &
  Vasishth 2005) -- exactly the organ the substrate already has in `hdlab/online_entity_cluster.py`.
  COMPUTATION. Comprehension is PREDICTIVE and the prediction runs TOP-DOWN: the higher level's current belief
  re-enters the lower level's competition as a PRIOR (Rao & Ballard 1999 predictive coding; Kuperberg & Jaeger 2016
  "What do we mean by prediction in language comprehension?" -- a graded belief, propagated down). So the referent
  system's belief that a string picks out an individual re-enters the LEXICAL CATEGORY competition as

      log P(c | word, context)  +=  KAPPA * log P(c | E)

  where E is the entity layer's symbol for this string's discourse history. That is ONE additive log-prior term --
  the same shape as every count-based cue already inside `hdlab/lexical_categories.py` (the Katz determiner table,
  the shape x position table). NO new organ: this is the FEEDBACK arm of the category organ, sourced from the
  entity layer's own individuation. ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS.
  AND IT IS A NEXT-MENTION PRIOR, NEVER A SAME-TOKEN LOOP (the brief's constraint, and the brain's: a prediction is
  formed before the input arrives). The register is written strictly IN ORDER, token by token, and the belief about
  word t reads only words 0..t-1 of the document.

THE TWO ARMS, both PINNED at the computational level, both count-based, both plastic:

 (A) THE REFERENT PRIOR  (`entc`: category -> Counter(entity symbol)).  The entity layer's individuation signature
     for a surface type inside ONE document -- Heim's file card, keyed the way the substrate's own entity layer keys
     NAMES (by string; `online_entity_cluster.online_cluster` resolves names through the aliaser and sends only
     common nouns through cue-based retrieval):
        e_first        no earlier mention in this document -> no discourse evidence (the honest majority case)
        e_rep_bare     mentioned before and never under a determiner -> a bare recurring referring expression
        e_rep_def      mentioned before, only under definite/possessive determiners ("the MSM", "the Gateses")
        e_rep_indef    mentioned before under an indefinite or a quantifier ("a DAX", "some DAXes") -> a KIND
                       (Katz, Baker & Macnamara 1974: the indefinite is the cue that the word names a KIND)
        e_rep_plural   a singular/plural variant of it occurs in the document -> a KIND (individuals do not
                       pluralise; Gelman & Taylor 1984 on the count-noun/proper-name distinction)
     MEASURED IN THE SUPPLY'S NOVEL STRATUM (the population the unknown-word read is estimated on, type count <= 2):
     P(PROPN)/P(NOUN) = 0.216/0.365 at e_first, 0.385/0.298 at e_rep_bare, 0.256/0.587 at e_rep_def,
     0.018/0.860 at e_rep_plural. The PROPN:NOUN odds move by 2.2x from e_first to e_rep_bare and collapse 34x at
     e_rep_plural -- a real, count-based, gold-free discourse signal, and the ONE place "the MSM" and "the CEO" can
     be separated (both are `Cap`/`ACRO` after `the`; only the discourse history differs).
     Read ONLY where there is no lexical entry (MacDonald 1994 cue competition: a cue's weight rises when the cues
     it competes with are silent -- the same gate the Katz frame already uses).

 (B) THE DOCUMENT REGISTER  (no new counts at all).  The same top-down path one level coarser: the reader adapts
     the generative model to the CURRENT document's statistics (Fine, Jaeger, Farmer & Qian 2013 rapid expectation
     adaptation; Delaney-Busch, Morgan, Lau & Kuperberg 2019 trial-by-trial Bayesian adaptation of the N400;
     Kuperberg & Jaeger 2016). A reader who has already settled that mid-sentence capitals in THIS document are
     common nouns (an email header block, a price list, a table of contents) lowers P(PROPN | Cap@mid) for the rest
     of it; a reader in a document full of established individuals raises it. Implemented as the organ's OWN
     shrinkage over its OWN GRADED posteriors on the document's earlier sentences:
        P_doc(c | shape@pos) = a * R_d[sym]/|R_d[sym]| + (1-a) * P_novel(c | shape@pos),  a = n_d/(n_d + THETA_DOC)
     R_d accumulates the POSTERIOR (not the argmax), so the alternatives stay alive across the sentence boundary.
     It updates only at a SENTENCE boundary -- a belief can only be fed back once it has settled.
     This is the ONE arm that can reach a FIRST mention, which is 121 of the 154 confusions.

KNOWLEDGE FORM (plastic, never frozen). (A) is a count table accrued from the supply exactly like `detc`/`rightc`,
and `log P(E | c)` is ONE pure function of those counts; `observe_document(sentences, categories)` grows it online.
(B) accrues at READ time from the organ's own beliefs and needs no asset at all. No gradient, no external tool at
inference, no gold coreference read anywhere (the UD-EWT TEST split is the ruler only; the TRAIN split's tag column
is the same offline foundation supply the organ's other tables already come from).

POPULATIONS AND FLOOR (all recomputed in place, never pasted).
  FLOOR = the LIVE organ (`LexicalCategories.load()` on the live asset: lag 2, order 2, shape, rare-mix, cluster
  cue, the pri-99 unknown-word cues) read DOCUMENT BY DOCUMENT: overall 0.9312, unseen 0.8002, PROPN<->NOUN 154
  (90 + 64). Reproduced by this cell's kappa=0 arm to 0.0 (--self-test W4).
  THE BAR'S POPULATION = the REPEATED-MENTION unseen tokens whose gold is PROPN or NOUN. 33 of the 154 confusions
  live there. THE OTHER 121 ARE FIRST MENTIONS -- the population fact the brief's checklist item 4 asks for, and it
  bounds arm (A) honestly before anything is built.
  TWINS. (1) SHUFFLED CHAINS (the brief's own words): each token is given the register symbol of a RANDOM other
  token of the same document -- the document's symbol distribution is preserved exactly, the token<->history
  pairing is destroyed. (2) PERMUTED TABLE: the entity symbol -> category mapping permuted, identical alphabet,
  identical row marginals, identical smoothing.
  CI. Paired bootstrap over DOCUMENTS (the discourse unit; the register is per-document), with the per-sentence
  bootstrap reported alongside for comparability with pri-99's numbers.

usage:
  python experiments/exp_entity_to_category_prior_v1.py --self-test
  python experiments/exp_entity_to_category_prior_v1.py [--smoke] [--arms A,B] [--boot 2000] [--out-name X.json]
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
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from experiments._seed_checkpoint import get_output_dir          # noqa: E402
import hdlab.lexical_categories as LC                            # noqa: E402
from hdlab.lexical_categories import LexicalCategories           # noqa: E402

# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-train.conllu
# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-test.conllu
# KB_REFERENT: data/frontend_assets/lexical_categories_counts_v1.json
# KB_REFERENT: data/frontend_assets/induced_categories_v2_1m_joint_clause.json
TRAIN = os.path.join(REPO, "data", "corpora", "ud_english_ewt", "en_ewt-ud-train.conllu")
TEST = os.path.join(REPO, "data", "corpora", "ud_english_ewt", "en_ewt-ud-test.conllu")
# KB_REFERENT: data/corpora/gum/conllu
GUM_DIR = os.path.join(REPO, "data", "corpora", "gum", "conllu")
# THE POWER FIX, AND IT IS A FACT ABOUT THE INSTRUMENT, NOT ABOUT THE LEVER. The UD-EWT TEST split's "documents"
# are web SNIPPETS: 316 of them for 25,094 tokens = 79 tokens each, so only 18.8% of its unseen tokens have any
# earlier mention of the same string and the bar's population is 288 items. GUM V12 (modern, multi-genre, the
# board's own corpus, entirely held out from this organ's supply) has 275 documents averaging ~993 tokens, where
# 57.1% of unseen tokens are repeat mentions and the bar's population is 7,606 -- 26x the power on the SAME
# ability. GENTLE (26 documents) is the OOD companion. Reported alongside UD-EWT test, never instead of it.

# ------------------------------------------------------------------ the entity layer's individuation alphabet
# KIND evidence: an indefinite article or a quantifier says the word names a KIND of thing, not an individual
# (Katz, Baker & Macnamara 1974: "This is a DAX" -> common noun; "This is DAX" -> a name).
KIND_DET = frozenset({"det_indef", "quant"})
# INDIVIDUAL-COMPATIBLE definite marking: names DO take determiners ("the MSM", "the Gateses", "the Europeans"),
# which is why the determiner-IDENTITY rule is a measured negative on this population -- the counts decide.
DEF_DET = frozenset({"det_def", "poss"})
ENT_SYMS = ("e_first", "e_rep_bare", "e_rep_def", "e_rep_indef", "e_rep_plural")


def _plural_variants(wl: str) -> List[str]:
    out = [wl + "s", wl + "es"]
    if wl.endswith("es") and len(wl) > 3:
        out.append(wl[:-2])
    if wl.endswith("s") and len(wl) > 2:
        out.append(wl[:-1])
    return out


class DiscourseRegister:
    """Heim (1982) FILE CARDS for ONE document, keyed by surface type -- the route the substrate's own entity layer
    already uses for NAMES (`hdlab/online_entity_cluster.online_cluster`: a name is resolved by its string through
    the aliaser; only common nouns go through cue-based retrieval). Purely surface: NO category is read, so accrual
    and inference compute the identical symbol -- there is no train/read mismatch and no circularity."""

    __slots__ = ("h", "rich", "sent_no", "recency_w")

    def __init__(self, rich: bool = False, recency_w: int = 0):
        self.h: Dict[str, dict] = {}
        self.rich = bool(rich)
        self.recency_w = int(recency_w)
        self.sent_no = 0

    def _card(self, wl: str) -> dict:
        c = self.h.get(wl)
        if c is None:
            c = self.h[wl] = {"n": 0, "det": set(), "plural": False, "cases": set(), "last": -1}
        return c

    def symbol(self, wl: str) -> str:
        """The entity layer's symbol for this string GIVEN THE DOCUMENT SO FAR (never the current token)."""
        c = self.h.get(wl)
        if c is None or c["n"] == 0:
            return "e_first"
        if c["plural"]:
            base = "e_rep_plural"
        elif c["det"] & KIND_DET:
            base = "e_rep_indef"
        elif c["det"] & DEF_DET:
            base = "e_rep_def"
        else:
            base = "e_rep_bare"
        if self.rich and c["n"] >= 2 and len(c["cases"]) == 1:
            base += "|t"          # a TOPICAL individual: >= 2 earlier mentions, orthographic form never varied
        if self.recency_w:
            # ACT-R BASE-LEVEL ACTIVATION, discretised (the substrate's own pinned constant lives in
            # `hdlab/salience_binder.actr_activation`): a file card mentioned 40 sentences ago is weak evidence,
            # one mentioned two sentences ago is strong. The prior must be read against the card's ACTIVATION,
            # not merely its existence -- which only matters in a real document (GUM: ~993 tokens; the UD-EWT
            # test snippets are 79, so every card is trivially "recent" there).
            base += "|r" if (self.sent_no - c["last"]) <= self.recency_w else "|d"
        return base

    def observe(self, raw: Sequence[str], lows: Sequence[str], i: int) -> None:
        """Write word i of this sentence INTO the file cards. Called only AFTER the symbol for word i has been
        consumed, so the belief about word t never sees word t (the brief's no-same-token-loop constraint)."""
        wl = lows[i]
        c = self._card(wl)
        c["n"] += 1
        c["det"].add(LC.det_context(lows, i))
        c["cases"].add("U" if raw[i][:1].isupper() else "l")
        c["last"] = self.sent_no
        for alt in _plural_variants(wl):
            if alt == wl:
                continue
            o = self.h.get(alt)
            if o is not None and o["n"] > 0:
                c["plural"] = True
                o["plural"] = True


# --------------------------------------------------------------------------------------------------------------
class EntityPriorCategories(LexicalCategories):
    """The live category organ PLUS the top-down entity prior (A) and the document register (B).

    ent_kappa = 0 and theta_doc = None reproduces the live organ EXACTLY (asserted in --self-test W4)."""

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.ent_kappa = 0.0
        self.theta_doc: Optional[float] = None
        self.ent_rich = False
        self.ent_recency = 0
        self.ent_rare = 0
        self.ent_skip_first = False
        self.ent_decay = 1.0        # PLASTICITY NEEDS FORGETTING: scale the accrued counts before each new passage
        self.ent_prec = 0.0         # PRECISION-WEIGHTING: scale kappa by how sharp the referent belief is
        self.ent_nconf = 0          # CONFIDENCE-WEIGHTING: scale kappa by how many prior mentions the card has
        self.reg_known_only = False  # THE REPAIRED PASSAGE REGISTER: calibrate on words the organ actually KNOWS
        self.ent_local = None        # THE SAME REPAIR ON THE ENTITY TABLE: a passage-local P(E|c) from KNOWN words
        self.reg_offset = False      # correct the known-word calibration for the KNOWN/UNKNOWN bias (measured)
        self.ent_prec_online = None  # PATH 6: the cue's OWN weight set by its ONLINE-ESTIMATED precision
        self.ent_prec_decay = 0.9    # exponential window on the running prediction-error statistic
        self._po_sum = 0.0           # running sum of the cue's informativeness gain (nats)
        self._po_n = 0.0             # its effective count
        self._sp_offset: Dict[str, np.ndarray] = {}
        self._doc_ent: Dict[str, np.ndarray] = {}
        self._sent_syms: List[str] = []
        self._prec: Dict[str, float] = {}
        self._prec_dirty = True
        self._maxprec_cache = None
        self.ent_novel = False
        self.entc: Dict[str, Counter] = defaultdict(Counter)     # category -> Counter(entity symbol), whole vocabulary
        self.entc_u: Dict[str, Counter] = defaultdict(Counter)   # ... restricted to the NOVEL-FORM stratum (Baayen)
        self.log_entc: Dict[str, Dict[str, float]] = {}
        self._ent_back: Dict[str, float] = {}
        self.ent_syms: Tuple[str, ...] = ENT_SYMS
        self._reg: Optional[DiscourseRegister] = None
        self._doc_shape: Dict[str, np.ndarray] = {}
        self._doc_syms: List[str] = []
        self._sent_raw: List[str] = []
        self._twin_perm: Optional[Dict[str, str]] = None
        self._twin_chain: Optional[random.Random] = None

    # -------------------------------------------------------------- plastic knowledge: the entity-symbol counts
    def accrue_entity_counts(self, docs) -> "EntityPriorCategories":
        """Accrue P(entity symbol | category) from the supply, DOCUMENT BY DOCUMENT, in reading order. The same
        offline foundation supply every other table in this organ comes from -- no new source of knowledge.

        TWO evidence bases, exactly as the organ already keeps two for the shape cue: the WHOLE vocabulary, and the
        NOVEL-FORM (productivity) stratum -- word types the organ has met at most UNK_NOVEL_MAX times. Baayen's
        productivity argument (Baayen 1992/2009; Hay & Baayen 2002) applies here with full force: what a FREQUENT
        word's discourse history predicts is not what a NEW word's history predicts, and the unknown-word read is a
        productivity question. MEASURED: the two tables disagree in SIGN on `e_rep_def` -- +0.43 nats toward PROPN
        on the whole vocabulary, -0.31 nats toward NOUN on the novel stratum -- and `e_rep_plural` is 3.6x stronger
        on the novel stratum (-3.4 nats vs -0.95)."""
        wcnt = getattr(self, "_wcnt_cache", None)
        if wcnt is None:
            wcnt = Counter()
            for t in self.tags:
                wcnt.update(self.emit[t])
            self._wcnt_cache = wcnt
        nmax = max(1, LC.UNK_NOVEL_MAX)
        for d in docs:
            reg = DiscourseRegister(rich=self.ent_rich, recency_w=self.ent_recency)
            for s in d:
                raw = [w for w, _ in s]
                lows = [w.lower() for w in raw]
                for i, (_w, t) in enumerate(s):
                    sym = reg.symbol(lows[i])
                    self.entc[t][sym] += 1
                    if wcnt[lows[i]] <= nmax:
                        self.entc_u[t][sym] += 1
                    reg.observe(raw, lows, i)
                reg.sent_no += 1
        self._finalize_entity()
        return self

    def decay_counts(self, lam: float) -> None:
        """FORGETTING. The organ's counts have an accrual rate and NO decay rate, so a reader who has read 200k
        tokens of one register cannot adapt to a new one: 7,308 new counts against 204,578 is 3.5% of the mass
        (measured). The brain's memory strengths DECAY (ACT-R base-level, which this substrate already implements
        for entity files in `hdlab/salience_binder.actr_activation` and applies to no count table in this organ).
        One multiplicative factor per PASSAGE, swept -- the exponential form of a power-law forgetting curve."""
        if lam >= 1.0:
            return
        for tab in (self.entc, self.entc_u):
            for t in list(tab):
                c = tab[t]
                for k in list(c):
                    v = c[k] * lam
                    if v < 1e-6:
                        del c[k]
                    else:
                        c[k] = v

    def observe_document(self, sentences, categories_per_sentence) -> None:
        """THE ONLINE PATH: one comprehended document grows the entity counts and re-derives log P(E | c)."""
        self.decay_counts(self.ent_decay)
        self.accrue_entity_counts([[list(zip(ws, cs)) for ws, cs in zip(sentences, categories_per_sentence)]])

    def _finalize_entity(self) -> None:
        """log P(entity symbol | category) -- ONE pure function of the counts (so `observe_document` re-derives it).
        The emission slot takes a LIKELIHOOD P(E | c), not a posterior -- the same correction pri-99 made for the
        suffix cue (the transition supplies the contextual prior; applying it twice penalises PROPN)."""
        src = self.entc_u if (self.ent_novel and self.entc_u) else self.entc
        syms = sorted({s for c in src.values() for s in c}) or list(ENT_SYMS)
        self.ent_syms = tuple(syms)
        V = len(syms)
        self.log_entc = {}
        self._ent_back = {}
        for t in self.tags:
            tot = sum(src[t].values()) + self.lam * V
            self.log_entc[t] = {s: math.log((src[t][s] + self.lam) / tot) for s in syms}
            self._ent_back[t] = math.log(self.lam / tot)
        # PRECISION-WEIGHTED PREDICTION (Rao & Ballard 1999; Friston; Kuperberg & Jaeger 2016 discuss the RELIABILITY
        # of a prediction explicitly): a top-down message is weighted by its PRECISION, not sent at a fixed gain. The
        # precision of the referent system's message for symbol E is how SHARP its belief over categories is --
        # 1 - H(P(c|E))/log T, one pure function of the same counts. `e_rep_plural` (86% NOUN in the novel stratum) is
        # a confident message; `e_rep_def` (a near coin-flip) is not, and should not be shouted at the same volume.
        T = max(2, len(self.tags))
        self._prec = {}
        for x in syms:
            col = np.array([src[t][x] + self.lam for t in self.tags], dtype=float)
            q = col / col.sum()
            h = float(-(q * np.log(q + 1e-12)).sum())
            self._prec[x] = max(0.0, 1.0 - h / math.log(T))
        self._prec_dirty = True

    # -------------------------------------------------------------- the document boundary
    def online_precision(self) -> float:
        """PATH 6. PRECISION IS THE INVERSE VARIANCE OF THE CUE'S OWN RECENT PREDICTION ERROR, ESTIMATED ONLINE
        (Friston; Feldman & Friston 2010, attention as precision) -- not a constant, and not frozen at training
        time. Every failure in this brief is one cue given a fixed gain in a passage where its reliability is
        different: on GUM P(PROPN | repeat AND Cap@mid) is 0.923 and on GENTLE it is 0.505, and a fixed kappa
        cannot know that. So the reader MEASURES how much the entity symbol is buying, inside this passage, on the
        tokens where it can check itself -- the ones with a lexical entry, where the organ scores 0.93 -- and sets
        the cue's weight to that. Where the cue is uninformative the estimate goes to zero and the prior switches
        itself off; where it is informative it runs at full gain. The estimate is a running exponentially-windowed
        mean of log P(c* | E) - log P(c* | e_first): how much the discourse symbol beats having no discourse
        evidence at all, in nats, on the organ's own settled answer."""
        if self.ent_prec_online is None or self._po_n <= 0:
            return 1.0
        g = max(0.0, self._po_sum / self._po_n)
        return g / (g + float(self.ent_prec_online))

    def new_document(self, twin_chain_seed: Optional[int] = None) -> None:
        self._po_sum = 0.0
        self._po_n = 0.0
        self._reg = DiscourseRegister(rich=self.ent_rich, recency_w=self.ent_recency)
        self._doc_shape = {}
        self._doc_ent = {}
        self._doc_syms = []
        self._twin_chain = random.Random(twin_chain_seed) if twin_chain_seed is not None else None

    def _accrue_online_precision(self, words: Sequence[str], post: np.ndarray) -> None:
        """Fold this sentence's evidence into the running precision estimate. KNOWN tokens only -- the reader can
        only check itself where it is reliable -- and strictly after the belief has settled."""
        if self.ent_prec_online is None or not self.log_entc:
            return
        # THE GAIN MUST BE A LIKELIHOOD RATIO AGAINST THE MARGINAL, NOT A RAW LIKELIHOOD DIFFERENCE. My first
        # version scored log P(E | c*) - log P(e_first | c*), which is dominated by how COMMON the symbol is
        # (e_first is most tokens, so the difference is large and negative for every category whatever the symbol
        # is worth). Measured: it returned -0.63 nats and a precision of 0.015 on GUM, i.e. it switched the cue
        # off on the corpus where the cue WINS -- a frequency measurement wearing an informativeness costume.
        # The right quantity is how much the symbol moves the belief TOWARD the organ's settled answer relative to
        # knowing nothing: q(c) proportional to P(E | c) * prior(c), and gain = log q(c*) - log prior(c*). That is
        # zero for an uninformative symbol and positive exactly when the cue helps.
        tot = sum(self.tag_count.values())
        prior = np.array([self.tag_count[t] / max(1, tot) for t in self.tags])
        lprior = np.log(prior + 1e-12)
        self._po_sum *= self.ent_prec_decay
        self._po_n *= self.ent_prec_decay
        for i, w in enumerate(words):
            if w.lower() not in self.vocab or i >= len(self._sent_syms):
                continue
            sym = self._sent_syms[i]
            if sym.startswith("e_first"):
                continue                      # no discourse evidence: nothing to score
            row = np.array([self.log_entc[t].get(sym, self._ent_back[t]) for t in self.tags])
            lq = row + lprior
            lq = lq - (lq.max() + np.log(np.exp(lq - lq.max()).sum()))       # normalise over categories
            k = int(post[i].argmax())
            self._po_sum += float(lq[k] - lprior[k])
            self._po_n += 1.0

    def update_document_register(self, words: Sequence[str], post: np.ndarray) -> None:
        """ARM (B): fold the SETTLED, GRADED belief about this sentence into the document's shape register. Called
        at the SENTENCE boundary -- a prediction can only be fed back once the belief it comes from has settled."""
        self._accrue_online_precision(words, post)
        if self.ent_local is not None and self._reg is not None:
            # THE SAME REPAIR, ON THE ENTITY TABLE. The out-of-domain failure is that P(category | discourse
            # history) is a CONVENTION and the convention differs by passage (P(PROPN | repeat AND Cap@mid) is
            # 0.923 on GUM and 0.505 on GENTLE). A reader estimates the local convention from the words it KNOWS
            # -- where the organ scores 0.93 -- and blends it into the global table by the organ's own shrinkage.
            # Where the local evidence says the cue is uninformative, the blend flattens the prior towards the
            # local base rate, which is precision-weighting with the precision estimated ONLINE (Feldman &
            # Friston 2010, attention as precision) rather than frozen at training time.
            for i, w in enumerate(words):
                wl = w.lower()
                if wl not in self.vocab:
                    continue
                if i >= len(self._sent_syms):
                    continue
                sym = self._sent_syms[i]
                r = self._doc_ent.get(sym)
                if r is None:
                    r = self._doc_ent[sym] = np.zeros(len(self.tags))
                r += post[i]
        if self.theta_doc is None:
            return
        pos = [LC.position_class(words, i) for i in range(len(words))]
        for i, w in enumerate(words):
            if self.reg_known_only and w.lower() not in self.vocab:
                # THE REPAIR. Arm B was CI-separated NEGATIVE because it fed the organ's OWN errors back: on GUM the
                # organ is right about an unseen word 52% of the time, so the passage table it built was half noise.
                # A reader calibrates the local convention on what it is SURE about. Restricted to tokens that HAVE
                # a lexical entry -- where the organ scores 0.93 -- the register measures the PASSAGE'S OWN
                # capitalisation convention (measured: P(PROPN | Cap@mid) is 0.93 on GUM and 0.51 on GENTLE) and
                # transfers it to the unknown tokens, which is what the convention is FOR.
                continue
            sym = self._unk_sym(w, pos[i])
            r = self._doc_shape.get(sym)
            if r is None:
                r = self._doc_shape[sym] = np.zeros(len(self.tags))
            r += post[i]

    # -------------------------------------------------------------- inference
    def _build_shape_offset(self) -> None:
        """THE KNOWN/UNKNOWN OFFSET, estimated OFFLINE from the supply the organ already has.

        A passage register calibrated on KNOWN words estimates the convention OF KNOWN WORDS, and the two
        populations differ systematically: P(PROPN | Cap@mid) known vs unknown is 0.7374/0.8574 on UD-EWT test,
        0.9259/0.9437 on GUM and 0.4460/0.6100 on GENTLE -- a capitalised word the organ already knows is 2 to 16
        points LESS likely to be a name than one it has never seen. That bias is a property of the LANGUAGE, not of
        the passage, so it can be measured once from the training supply by comparing its KNOWN slice with its
        NOVEL-FORM stratum (the two evidence bases the organ already keeps) and divided out of every local
        estimate. This is the missing piece that made the repaired register win on GENTLE and lose on GUM."""
        T = len(self.tags)
        nmax = max(1, LC.UNK_NOVEL_MAX)
        wcnt: Counter = Counter()
        wtag: Dict[str, np.ndarray] = {}
        for i, t in enumerate(self.tags):
            for w, n in self.emit[t].items():
                wcnt[w] += n
                v = wtag.get(w)
                if v is None:
                    v = wtag[w] = np.zeros(T)
                v[i] += n
        known: Dict[str, np.ndarray] = {}
        novel: Dict[str, np.ndarray] = {}
        for w, col in self.shape_pos_w.items():
            v = wtag.get(w)
            if v is None or v.sum() <= 0:
                continue
            v = v / v.sum()
            tgt = novel if wcnt[w] <= nmax else known
            den = float(sum(col.values()))
            for sp, n in col.items():
                r = tgt.get(sp)
                if r is None:
                    r = tgt[sp] = np.zeros(T)
                r += v * (n / den)
        self._sp_offset = {}
        for sp in set(known) | set(novel):
            k = known.get(sp)
            u = novel.get(sp)
            if k is None or u is None or k.sum() < 5 or u.sum() < 5:
                continue
            kp = (k + self.lam) / (k.sum() + self.lam * T)
            up = (u + self.lam) / (u.sum() + self.lam * T)
            self._sp_offset[sp] = np.log(up) - np.log(kp)

    def _log_shape_factor(self, w_raw: str, pos: str, known: bool) -> np.ndarray:
        base = super()._log_shape_factor(w_raw, pos, known)
        if self.theta_doc is None or known:
            return base
        r = self._doc_shape.get(self._unk_sym(w_raw, pos))
        if r is None:
            return base
        nd = float(r.sum())
        if nd <= 0:
            return base
        a = nd / (nd + float(self.theta_doc))          # the organ's OWN reliability shrinkage, a = n / (n + theta)
        mx = float(base.max())
        loc = r / nd
        if self.reg_offset:
            off = self._sp_offset.get(self._unk_sym(w_raw, pos))
            if off is not None:
                loc = loc * np.exp(off)               # correct the known-word calibration for the measured bias
                loc = loc / loc.sum()
        p = a * loc + (1.0 - a) * np.exp(base - mx)
        p = p / p.sum()
        return np.log(p + 1e-12) + mx

    def _log_emit(self, word: str) -> np.ndarray:
        here = self._sent_i                            # the base class advances it -- capture the index first
        out = super()._log_emit(word)
        if self._reg is None:
            return out
        wl = self._sent_lows[here] if here < len(self._sent_lows) else word.lower()
        sym = self._reg.symbol(wl)
        self._doc_syms.append(sym)
        self._sent_syms.append(sym)
        # CUE COMPETITION IS GRADED, NOT BINARY (MacDonald 1994; and the organ's own rare-word mixing already says
        # so): the lexical cue is ABSENT for an unseen word and merely WEAK for a word seen once or twice. With
        # ent_rare the prior is also read on the known-but-rare stratum, damped by the SAME Bayesian shrinkage the
        # organ uses there -- weight (1 - c/(c + MIX_KAPPA)), so a form seen 20 times gets nothing.
        gate = 0.0
        if wl not in self.vocab:
            gate = 1.0
        elif self.ent_rare:
            cw = sum(self.emit[t][wl] for t in self.tags)
            if cw <= self.ent_rare:
                gate = 1.0 - cw / (cw + LC.MIX_KAPPA)
        # A TOP-DOWN PREDICTION EXISTS ONLY WHERE THE HIGHER LEVEL HAS A BELIEF. At `e_first` the referent system
        # has never seen this string in this passage, so it has nothing to say -- and log P(e_first | c) is then a
        # CATEGORY-MARGINAL-shaped term that perturbs the competition for no reason (the same defect UNK_PRIOR_GAMMA
        # was introduced to remove: a prior applied where it does not belong penalises the low-prior categories).
        # MEASURED on GUM: without this gate the prior cuts repeat-mention confusions but ADDS first-mention ones.
        if self.ent_skip_first and sym.startswith("e_first"):
            gate = 0.0
        if self.ent_kappa and self.log_entc and gate > 0:
            use = sym
            if self._twin_chain is not None:
                use = self._twin_chain.choice(self._doc_syms)      # TWIN 1: SHUFFLED CHAINS
            if self._twin_perm is not None:
                use = self._twin_perm.get(use, use)                # TWIN 2: PERMUTED TABLE
            w = self.ent_kappa * gate
            if self.ent_prec_online is not None:
                w *= self.online_precision()      # PATH 6: the cue sets its own gain from its measured value
            if self.ent_prec:
                # PRECISION-WEIGHTING: kappa scaled by how sharp the referent system's belief for this symbol is.
                w *= (1.0 - self.ent_prec) + self.ent_prec * (self._prec.get(use, 0.0) / self._maxprec())
            if self.ent_nconf:
                # CONFIDENCE-WEIGHTING: a file card with more prior mentions is a more reliable source -- the organ's
                # own reliability shrinkage n/(n+theta) again, now on the CARD rather than on a count row.
                card = self._reg.h.get(wl)
                nprev = card["n"] if card else 0
                w *= nprev / (nprev + float(self.ent_nconf))
            row = np.array([self.log_entc[t].get(use, self._ent_back[t]) for t in self.tags])
            if self.ent_local is not None:
                loc = self._doc_ent.get(use)
                nd = float(loc.sum()) if loc is not None else 0.0
                if nd > 0:
                    a_ = nd / (nd + float(self.ent_local))     # the organ's own shrinkage, a = n / (n + theta)
                    mx = float(row.max())
                    q = a_ * (loc / nd) + (1.0 - a_) * np.exp(row - mx)
                    row = np.log(q / q.sum() + 1e-12) + mx
            out = out + w * row
        raw = self._sent_raw if len(self._sent_raw) == len(self._sent_lows) else list(self._sent_lows)
        self._reg.observe(raw, self._sent_lows, here)
        return out

    def _maxprec(self) -> float:
        if self._prec_dirty or self._maxprec_cache is None:
            self._maxprec_cache = max(self._prec.values()) if self._prec else 1.0
            self._maxprec_cache = max(1e-9, self._maxprec_cache)
            self._prec_dirty = False
        return self._maxprec_cache

    def posterior(self, words, lag=None):
        self._sent_raw = list(words)
        self._sent_syms = []
        out = super().posterior(words, lag=lag)
        if self._reg is not None:
            self._reg.sent_no += 1
        return out

    # -------------------------------------------------------------- twins
    def set_twin_permutation(self, seed: int) -> None:
        """INFORMATION-FREE TWIN 2: permute the entity symbol -> category mapping. Identical alphabet, identical row
        marginals, identical smoothing -- only the symbol<->category pairing is destroyed."""
        syms = list(self.ent_syms)
        rng = random.Random(seed)
        shuf = syms[:]
        for _ in range(10000):                         # a DERANGEMENT: no symbol may keep its own row
            rng.shuffle(shuf)
            if all(a != b for a, b in zip(syms, shuf)):
                break
        self._twin_perm = dict(zip(syms, shuf))

    # -------------------------------------------------------------- persistence of the new counts
    def save_entity_counts(self, path: str) -> str:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"entc": {t: dict(c) for t, c in self.entc.items()},
                       "entc_u": {t: dict(c) for t, c in self.entc_u.items()},
                       "note": "COUNTS only (plastic); log P(entity symbol | category) is recomputed on load"}, f)
        return path

    def load_entity_counts(self, path: str) -> "EntityPriorCategories":
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        for t, c in d["entc"].items():
            self.entc[t] = Counter(c)
        for t, c in d.get("entc_u", {}).items():
            self.entc_u[t] = Counter(c)
        self._finalize_entity()
        return self


# --------------------------------------------------------------------- data
def read_docs(path: str, column: int = 3):
    """UD-EWT with its DOCUMENT boundaries kept (`# newdoc id`): 540 train / 316 test documents. The incumbent
    harness flattens them, which is why the discourse context looked unavailable (pri-99 alternate path 2)."""
    docs: List[list] = []
    cur_doc: list = []
    cur: list = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("# newdoc"):
                if cur:
                    cur_doc.append(cur)
                    cur = []
                if cur_doc:
                    docs.append(cur_doc)
                cur_doc = []
                continue
            if not line:
                if cur:
                    cur_doc.append(cur)
                    cur = []
                continue
            if line.startswith("#"):
                continue
            c = line.split("\t")
            if len(c) <= column or "-" in c[0] or "." in c[0]:
                continue
            cur.append((c[1], c[column]))
    if cur:
        cur_doc.append(cur)
    if cur_doc:
        docs.append(cur_doc)
    return docs


# --------------------------------------------------------------------- scoring
def score_docs(model, docs, vocab, twin_chain_seed: Optional[int] = None) -> dict:
    """Read each DOCUMENT sentence by sentence, in order. Per-document AND per-sentence hit vectors (both bootstrap
    units), the unseen slice, the PROPN<->NOUN confusions, and THE BAR POPULATION: the repeated-mention unseen
    tokens whose gold is PROPN or NOUN."""
    per_doc = []
    per_sent = []
    conf: Counter = Counter()
    tot = ok = unk = unk_ok = 0
    rep_tot = rep_ok = rep_conf = first_conf = 0
    first_tot = first_ok = 0
    rep_items: List[tuple] = []
    pn_all = [0]
    for d in docs:
        model.new_document(twin_chain_seed=twin_chain_seed)
        seen: Counter = Counter()
        d_tot = d_ok = d_unk = d_unk_ok = d_rt = d_ro = 0
        for s in d:
            words = [w for w, _ in s]
            gold = [g for _, g in s]
            post = model.posterior(words)
            pred = [model.tags[int(i)] for i in post.argmax(axis=1)]
            a_tot = a_ok = u_tot = u_ok = 0
            for w, g, p in zip(words, gold, pred):
                hit = int(g == p)
                a_tot += 1
                a_ok += hit
                wl = w.lower()
                if not hit and {g, p} == {"PROPN", "NOUN"}:
                    pn_all[0] += 1
                if wl not in vocab:
                    u_tot += 1
                    u_ok += hit
                    if not hit:
                        conf[(g, p)] += 1
                    if g in ("PROPN", "NOUN"):
                        if seen[wl] > 0:
                            d_rt += 1
                            d_ro += hit
                            if not hit and p in ("PROPN", "NOUN"):
                                rep_conf += 1
                                rep_items.append((w, g, p))
                        else:
                            first_tot += 1
                            first_ok += hit
                            if (not hit) and p in ("PROPN", "NOUN"):
                                first_conf += 1
                seen[wl] += 1
            model.update_document_register(words, post)
            per_sent.append((a_ok, a_tot, u_ok, u_tot))
            d_tot += a_tot
            d_ok += a_ok
            d_unk += u_tot
            d_unk_ok += u_ok
        per_doc.append((d_ok, d_tot, d_unk, d_unk_ok, d_rt, d_ro))
        tot += d_tot
        ok += d_ok
        unk += d_unk
        unk_ok += d_unk_ok
        rep_tot += d_rt
        rep_ok += d_ro
    return {"acc": ok / max(1, tot), "unknown_acc": unk_ok / max(1, unk),
            "n_tokens": tot, "n_unknown": unk,
            "propn_noun": conf[("PROPN", "NOUN")] + conf[("NOUN", "PROPN")],
            "propn_noun_all_tokens": pn_all[0],
            "propn_to_noun": conf[("PROPN", "NOUN")], "noun_to_propn": conf[("NOUN", "PROPN")],
            "rep_n": rep_tot, "rep_acc": rep_ok / max(1, rep_tot), "rep_propn_noun": rep_conf,
            "first_n": first_tot, "first_acc": first_ok / max(1, first_tot), "first_propn_noun": first_conf,
            "rep_items": rep_items,
            "confusions": {"%s->%s" % (g, p): n for (g, p), n in conf.most_common(12)},
            "per_doc": per_doc, "per_sent": per_sent}


def paired_boot(a, b, kind: str, unit: str = "doc", n_boot: int = 2000, seed: int = 0):
    """Paired bootstrap on the delta (b - a). unit 'doc' resamples DOCUMENTS (the discourse unit), 'sent' sentences.
    kind: 'all' | 'unk' | 'rep' (the bar population: repeated-mention unseen PROPN/NOUN tokens)."""
    if unit == "doc":
        i0, i1 = {"all": (0, 1), "unk": (3, 2), "rep": (5, 4)}[kind]
    else:
        i0, i1 = (2, 3) if kind == "unk" else (0, 1)
    A = np.array([[s[i0], s[i1]] for s in a], dtype=float)
    B = np.array([[s[i0], s[i1]] for s in b], dtype=float)
    n = len(A)
    rng = np.random.default_rng(seed)
    d = np.empty(n_boot)
    for r in range(n_boot):
        idx = rng.integers(0, n, n)
        ta = A[idx].sum(axis=0)
        tb = B[idx].sum(axis=0)
        d[r] = (tb[0] / max(1.0, tb[1])) - (ta[0] / max(1.0, ta[1]))
    obs = (B[:, 0].sum() / max(1.0, B[:, 1].sum())) - (A[:, 0].sum() / max(1.0, A[:, 1].sum()))
    lo, hi = np.percentile(d, [2.5, 97.5])
    return {"delta": round(float(obs), 4), "ci95": [round(float(lo), 4), round(float(hi), 4)],
            "half_width": round(float(hi - lo) / 2, 4), "separated": bool(lo > 0 or hi < 0),
            "n_unit": n, "denom": int(A[:, 1].sum())}


ARMS = {
    "F_live":       dict(ent_kappa=0.0, theta_doc=None),
    "E1_k025":      dict(ent_kappa=0.25, theta_doc=None),
    "E2_k05":       dict(ent_kappa=0.5, theta_doc=None),
    "E3_k1":        dict(ent_kappa=1.0, theta_doc=None),
    "E4_k2":        dict(ent_kappa=2.0, theta_doc=None),
    "E5_k4":        dict(ent_kappa=4.0, theta_doc=None),
    "E6_rich_k1":   dict(ent_kappa=1.0, theta_doc=None, ent_rich=True),
    "E7_rich_k2":   dict(ent_kappa=2.0, theta_doc=None, ent_rich=True),
    "R1_d1":        dict(ent_kappa=0.0, theta_doc=1.0),
    "R2_d3":        dict(ent_kappa=0.0, theta_doc=3.0),
    "R3_d10":       dict(ent_kappa=0.0, theta_doc=10.0),
    "R4_d30":       dict(ent_kappa=0.0, theta_doc=30.0),
    "R5_d100":      dict(ent_kappa=0.0, theta_doc=100.0),
    "ER1_k1_d10":   dict(ent_kappa=1.0, theta_doc=10.0),
    "ER2_k2_d10":   dict(ent_kappa=2.0, theta_doc=10.0),
    "ER3_k1_d30":   dict(ent_kappa=1.0, theta_doc=30.0),
    "ER4_k2_d30":   dict(ent_kappa=2.0, theta_doc=30.0),
    # --- the NOVEL-FORM (Baayen productivity) evidence base for the entity table: what a NEW word's discourse
    #     history predicts, not what a frequent word's does. The organ already keeps two evidence bases for the
    #     shape cue for exactly this reason; the two tables disagree in SIGN on e_rep_def.
    "N1_nk05":      dict(ent_kappa=0.5, theta_doc=None, ent_novel=True),
    "N2_nk1":       dict(ent_kappa=1.0, theta_doc=None, ent_novel=True),
    "N3_nk2":       dict(ent_kappa=2.0, theta_doc=None, ent_novel=True),
    "N4_nk4":       dict(ent_kappa=4.0, theta_doc=None, ent_novel=True),
    "N5_nk1_rich":  dict(ent_kappa=1.0, theta_doc=None, ent_novel=True, ent_rich=True),
    "NR1_nk2_d10":  dict(ent_kappa=2.0, theta_doc=10.0, ent_novel=True),
    "NR2_nk2_d30":  dict(ent_kappa=2.0, theta_doc=30.0, ent_novel=True),
    "NR3_nk1_d30":  dict(ent_kappa=1.0, theta_doc=30.0, ent_novel=True),
    "NR4_nk4_d30":  dict(ent_kappa=4.0, theta_doc=30.0, ent_novel=True),
    "N6_nk2_rich":  dict(ent_kappa=2.0, theta_doc=None, ent_novel=True, ent_rich=True),
    "N7_nk3_rich":  dict(ent_kappa=3.0, theta_doc=None, ent_novel=True, ent_rich=True),
    "NR5_nk2r_d30": dict(ent_kappa=2.0, theta_doc=30.0, ent_novel=True, ent_rich=True),
    "NR6_nk2r_d100": dict(ent_kappa=2.0, theta_doc=100.0, ent_novel=True, ent_rich=True),
    # --- ACT-R RECENCY on the file card (the activation of the discourse referent, not merely its existence)
    "A1_k1_w2":     dict(ent_kappa=1.0, theta_doc=None, ent_recency=2),
    "A2_k1_w5":     dict(ent_kappa=1.0, theta_doc=None, ent_recency=5),
    "A3_k1_w10":    dict(ent_kappa=1.0, theta_doc=None, ent_recency=10),
    "A4_k2_w5":     dict(ent_kappa=2.0, theta_doc=None, ent_recency=5),
    "A5_k1_w5_rich": dict(ent_kappa=1.0, theta_doc=None, ent_recency=5, ent_rich=True),
    "A6_k1_w5_d30": dict(ent_kappa=1.0, theta_doc=30.0, ent_recency=5),
    # --- the prior read on the KNOWN-BUT-RARE stratum too, damped by the organ's own rare-word shrinkage
    "B1_k1_w5_rare2": dict(ent_kappa=1.0, theta_doc=None, ent_recency=5, ent_rare=2),
    "B2_k1_w5_rare5": dict(ent_kappa=1.0, theta_doc=None, ent_recency=5, ent_rare=5),
    "B3_k2_w5_rare5": dict(ent_kappa=2.0, theta_doc=None, ent_recency=5, ent_rare=5),
    "B4_k1_w5_rare20": dict(ent_kappa=1.0, theta_doc=None, ent_recency=5, ent_rare=20),
    # --- THE PREDICTION IS SILENT WHERE THE DISCOURSE MODEL HAS NO BELIEF (no prior at e_first)
    "S1_k1_w5":     dict(ent_kappa=1.0, theta_doc=None, ent_recency=5, ent_skip_first=True),
    "S2_k2_w5":     dict(ent_kappa=2.0, theta_doc=None, ent_recency=5, ent_skip_first=True),
    "S3_k2_rich":   dict(ent_kappa=2.0, theta_doc=None, ent_rich=True, ent_skip_first=True),
    "S4_k4_w5":     dict(ent_kappa=4.0, theta_doc=None, ent_recency=5, ent_skip_first=True),
    "S5_k2_w5_rare5": dict(ent_kappa=2.0, theta_doc=None, ent_recency=5, ent_rare=5, ent_skip_first=True),
    # --- PHASE 7 (b): FORGETTING. plasticity with an accrual rate and no decay rate cannot adapt (measured: 13
    #     documents of online reading = 3.5% of the count mass). One multiplicative decay per passage, swept.
    "D0_nodecay":   dict(ent_kappa=2.0, ent_recency=5, ent_skip_first=True, ent_decay=1.0),
    "D1_d099":      dict(ent_kappa=2.0, ent_recency=5, ent_skip_first=True, ent_decay=0.99),
    "D2_d095":      dict(ent_kappa=2.0, ent_recency=5, ent_skip_first=True, ent_decay=0.95),
    "D3_d090":      dict(ent_kappa=2.0, ent_recency=5, ent_skip_first=True, ent_decay=0.90),
    "D4_d070":      dict(ent_kappa=2.0, ent_recency=5, ent_skip_first=True, ent_decay=0.70),
    "D5_d050":      dict(ent_kappa=2.0, ent_recency=5, ent_skip_first=True, ent_decay=0.50),
    "D6_d030":      dict(ent_kappa=2.0, ent_recency=5, ent_skip_first=True, ent_decay=0.30),
    # --- PHASE 7 (c): PRECISION-WEIGHTED PREDICTION + card CONFIDENCE
    "P1_prec1":     dict(ent_kappa=2.0, ent_recency=5, ent_skip_first=True, ent_prec=1.0),
    "P2_prec05":    dict(ent_kappa=2.0, ent_recency=5, ent_skip_first=True, ent_prec=0.5),
    "P3_prec1_k4":  dict(ent_kappa=4.0, ent_recency=5, ent_skip_first=True, ent_prec=1.0),
    "P4_nconf1":    dict(ent_kappa=2.0, ent_recency=5, ent_skip_first=True, ent_nconf=1),
    "P5_nconf2":    dict(ent_kappa=2.0, ent_recency=5, ent_skip_first=True, ent_nconf=2),
    "P6_prec1_nc1": dict(ent_kappa=2.0, ent_recency=5, ent_skip_first=True, ent_prec=1.0, ent_nconf=1),
    "P7_prec1_k4_nc1": dict(ent_kappa=4.0, ent_recency=5, ent_skip_first=True, ent_prec=1.0, ent_nconf=1),
    # --- PHASE 7 (d): THE REPAIRED PASSAGE REGISTER -- calibrate the passage convention on KNOWN words only
    "K1_reg10":     dict(ent_kappa=0.0, theta_doc=10.0, reg_known_only=True),
    "K2_reg30":     dict(ent_kappa=0.0, theta_doc=30.0, reg_known_only=True),
    "K3_reg100":    dict(ent_kappa=0.0, theta_doc=100.0, reg_known_only=True),
    "K4_reg300":    dict(ent_kappa=0.0, theta_doc=300.0, reg_known_only=True),
    "KS1_k2_reg30": dict(ent_kappa=2.0, ent_recency=5, ent_skip_first=True, theta_doc=30.0, reg_known_only=True),
    "KS2_k2_reg100": dict(ent_kappa=2.0, ent_recency=5, ent_skip_first=True, theta_doc=100.0, reg_known_only=True),
    # --- PHASE 7 (A): the SAME repair on the ENTITY table -- a passage-local P(E|c) from KNOWN words, blended in
    "L1_k2_loc10":  dict(ent_kappa=2.0, ent_recency=5, ent_skip_first=True, ent_local=10.0),
    "L2_k2_loc30":  dict(ent_kappa=2.0, ent_recency=5, ent_skip_first=True, ent_local=30.0),
    "L3_k2_loc100": dict(ent_kappa=2.0, ent_recency=5, ent_skip_first=True, ent_local=100.0),
    "L4_k2_loc30_reg100": dict(ent_kappa=2.0, ent_recency=5, ent_skip_first=True, ent_local=30.0,
                               theta_doc=100.0, reg_known_only=True),
    "L5_k2_loc10_reg30": dict(ent_kappa=2.0, ent_recency=5, ent_skip_first=True, ent_local=10.0,
                              theta_doc=30.0, reg_known_only=True),
    # --- PHASE 7 (final): the repaired register WITH the offline known/unknown bias correction
    "O1_reg30_off":  dict(ent_kappa=0.0, theta_doc=30.0, reg_known_only=True, reg_offset=True),
    "O2_reg100_off": dict(ent_kappa=0.0, theta_doc=100.0, reg_known_only=True, reg_offset=True),
    "O3_reg300_off": dict(ent_kappa=0.0, theta_doc=300.0, reg_known_only=True, reg_offset=True),
    "O4_k2_reg100_off": dict(ent_kappa=2.0, ent_recency=5, ent_skip_first=True, theta_doc=100.0,
                             reg_known_only=True, reg_offset=True),
    # --- PATH 6: the entity cue's OWN weight set by its ONLINE-ESTIMATED precision (lambda_p swept)
    "X1_po005":  dict(ent_kappa=2.0, ent_recency=5, ent_skip_first=True, ent_prec_online=0.05),
    "X2_po02":   dict(ent_kappa=2.0, ent_recency=5, ent_skip_first=True, ent_prec_online=0.2),
    "X3_po05":   dict(ent_kappa=2.0, ent_recency=5, ent_skip_first=True, ent_prec_online=0.5),
    "X4_po02_d1": dict(ent_kappa=2.0, ent_recency=5, ent_skip_first=True, ent_prec_online=0.2, ent_prec_decay=1.0),
    "X5_po02_d07": dict(ent_kappa=2.0, ent_recency=5, ent_skip_first=True, ent_prec_online=0.2, ent_prec_decay=0.7),
    "X6_po02_full": dict(ent_kappa=2.0, ent_recency=5, ent_skip_first=True, ent_prec_online=0.2,
                         ent_prec_decay=1.0, theta_doc=100.0, reg_known_only=True, reg_offset=True),
}

def online_adapt(model, docs, verbose: bool = True, oracle: bool = False) -> int:
    """THE PLASTIC PATH MADE LOAD-BEARING (the brief: knowledge as counts with an online observe path).

    The organ READS real documents and accrues the entity-symbol counts from ITS OWN SETTLED CATEGORIES -- no gold
    tag column, no gold coreference, no external tool. That is the brain's acquisition path for this table: a
    comprehension outcome is a learning event (Christiansen & Chater; the organ's own `observe`). It matters here
    for a measured reason: the offline supply is UD-EWT TRAIN, whose "documents" are 79-token web snippets in which
    a repeated unseen string is usually a NAME (65% PROPN), while in a real document it is usually a domain term
    (63% NOUN on GUM). A reader who reads real documents accrues real-document statistics.
    The adaptation set is DISJOINT from the scored set, so nothing is transductive."""
    n = 0
    for d in docs:
        model.new_document()
        sents = []
        cats = []
        for s in d:
            words = [w for w, _ in s]
            post = model.posterior(words)
            model.update_document_register(words, post)
            sents.append(words)
            cats.append([g for _, g in s] if oracle
                        else [model.tags[int(i)] for i in post.argmax(axis=1)])
            n += len(words)
        model.observe_document(sents, cats)
    if verbose:
        print("  online-adapt%s: %d documents, %d tokens read; entity counts now %d"
              % (" [ORACLE TEACHER]" if oracle else "", len(docs), n,
                 sum(sum(c.values()) for c in model.entc.values())), flush=True)
    return n


def read_corpus(name: str, cap_docs: int = 0, stride: int = 1):
    """'ewt' = the UD-EWT TEST split (the brief's named population). 'gum' / 'gentle' = the modern multi-genre
    documents, one conllu file per document. All are the RULER only -- never read while learning."""
    import glob
    if name == "ewt":
        docs = read_docs(TEST)
    else:
        pref = "GUM_" if name == "gum" else "GENTLE_"
        docs = []
        for f in sorted(glob.glob(os.path.join(GUM_DIR, pref + "*.conllu"))):
            docs.extend(read_docs(f))
    if stride > 1:
        docs = docs[::stride]        # every k-th document -- GUM's files are genre-ordered, so a stride keeps the
    return docs[:cap_docs] if cap_docs else docs      # genre mix that a head-slice would destroy


def read_docs_full(path: str):
    """Documents with the gold heads and relations kept as well (for the HEADS no-regress rung)."""
    docs: List[list] = []
    cur_doc: list = []
    toks: list = []
    pos: list = []
    heads: list = []
    rels: list = []

    def flush_sent():
        nonlocal toks, pos, heads, rels
        if toks:
            cur_doc.append((toks, pos, heads, rels))
        toks, pos, heads, rels = [], [], [], []

    def flush_doc():
        nonlocal cur_doc
        if cur_doc:
            docs.append(cur_doc)
        cur_doc = []

    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("# newdoc"):
                flush_sent()
                flush_doc()
                continue
            if not line:
                flush_sent()
                continue
            if line.startswith("#"):
                continue
            c = line.split("\t")
            if "-" in c[0] or "." in c[0]:
                continue
            toks.append(c[1])
            pos.append(c[3])
            heads.append(int(c[6]))
            rels.append(c[7].split(":")[0])
    flush_sent()
    flush_doc()
    return docs


def forward_wire(arms=("gold", "caps", "cat_floor", "cat"), n_docs=None) -> dict:
    """THE FORWARD WIRE (phase 7, lead 1): make the ENTITY LAYER read the CATEGORY ORGAN instead of deciding
    name-vs-common on its own.

    WHAT I FOUND WHILE BUILDING IT, AND IT CHANGES THE QUESTION. The board's coref rows come from
    `experiments/exp_board_coref_gum_v1.board_coref_modern_dimension`, whose mentions are typed by
    `experiments/gum_coref._mention_type`, which branches on `head_tok.upos` -- and that upos is `cols[3]` of the
    GUM CoNLL-U, i.e. THE GOLD CATEGORY COLUMN. The board's `coref` and `common_noun_coref` dimensions are
    therefore scored with a GOLD name/common/pronoun split. The LIVE reader has no such column: eight organs
    decide it with `hdlab/coref.name_content_tokens`, a capitalisation rule. So the board cannot show the wire's
    value -- it is already being handed the answer -- and the honest live number is lower than the board says.

    The three-way comparison that does answer it, on the SAME populations:
      gold       the board as it stands today (gold UPOS -> mtype)
      caps       `name_content_tokens` on the span -- what the LIVE reader actually does
      cat_floor  the category organ own predicted UPOS, entity prior OFF (the live organ)
      cat        the category organ own predicted UPOS, entity prior ON (the full stack)
    THE PRONOUN BRANCH IS HELD FIXED across arms, so the `coref` (pronoun) and `common_noun` populations are
    identical in every arm and only the NAME-vs-COMMON decision varies. That is the wire, isolated."""
    import experiments.gum_coref as G                      # noqa: F401
    import experiments.exp_board_coref_gum_v1 as BCG
    from hdlab.coref import name_content_tokens

    tr = read_docs(TRAIN)
    cache: dict = {}
    orig_load_test = BCG._load_test
    out: dict = {"n_docs": n_docs, "arms": {}}

    def tag_doc(model, doc):
        """The organ predicted UPOS for every token of one GUM document, read IN ORDER, passage-aware."""
        by_sent = {}
        for t in doc.toks:
            by_sent.setdefault(t.sent, []).append(t)
        pred = {}
        model.new_document()
        for sidx in sorted(by_sent):
            row = sorted(by_sent[sidx], key=lambda t: t.idx)
            words = [t.form for t in row]
            post = model.posterior(words)
            model.update_document_register(words, post)
            for t, j in zip(row, post.argmax(axis=1)):
                pred[(t.sent, t.idx)] = model.tags[int(j)]
        return pred

    for arm in arms:
        model = None
        if arm.startswith("cat"):
            cfg = dict(ARMS["F_live" if arm == "cat_floor" else "S2_k2_w5"])
            model = build(cfg, docs=tr, entc_cache=cache)

        def patched_load_test(nd=None, _arm=arm, _model=model):
            docs, test, gaz = orig_load_test(nd)
            if _arm == "gold":
                return docs, test, gaz
            for doc in docs:
                pred = tag_doc(_model, doc) if _model is not None else None
                gmap = {t.gidx: t for t in doc.toks}
                for m in doc.mentions:
                    if m.mtype == "pronoun":
                        continue                       # the pronoun branch is a CONSTANT across arms
                    span = [gmap[g] for g in range(m.start_g, m.end_g + 1) if g in gmap]
                    head = gmap.get(m.head_g)
                    if head is None:
                        continue
                    if _arm == "caps":
                        is_name = bool(name_content_tokens([t.form for t in span]))
                    else:
                        up = pred.get((head.sent, head.idx), "X")
                        is_name = (up == "PROPN")
                        m.upos = up
                    m.mtype = "name" if is_name else "common"
            return docs, test, gaz

        BCG._load_test = patched_load_test
        t0 = time.time()
        try:
            row, detail = BCG.board_coref_modern_dimension(n_docs=n_docs)
        finally:
            BCG._load_test = orig_load_test
        keys = ("n", "model_acc", "strongest_floor", "twin_acc", "model_minus_strongest", "ci_sep_over_strongest")
        rec = {"coref_pronoun": {k: row.get(k) for k in keys},
               "common_noun": {k: detail["common_noun"].get(k) for k in keys},
               "elapsed_s": round(time.time() - t0, 1)}
        out["arms"][arm] = rec
        print("FWD %-10s coref n=%s acc=%s floor=%s | common_noun n=%s acc=%s floor=%s  (%ss)"
              % (arm, rec["coref_pronoun"]["n"], rec["coref_pronoun"]["model_acc"],
                 rec["coref_pronoun"]["strongest_floor"], rec["common_noun"]["n"],
                 rec["common_noun"]["model_acc"], rec["common_noun"]["strongest_floor"], rec["elapsed_s"]),
              flush=True)
    return out


def name_decision(corpus: str = "ewt", stride: int = 1, arm: str = "S2_k2_w5") -> dict:
    """THE NAME DECISION ITSELF, scored token-by-token and span-by-span against the same gold, for the three
    deciders. This is what the forward wire is worth BEFORE any downstream consumer is involved."""
    from hdlab.coref import name_content_tokens
    tr = read_docs(TRAIN)
    te = read_corpus(corpus, 0, stride)
    cache: dict = {}
    m_floor = build(dict(ARMS["F_live"]), docs=tr, entc_cache=cache)
    m_arm = build(dict(ARMS[arm]), docs=tr, entc_cache=cache)
    NP = frozenset({"DET", "ADJ", "NUM", "NOUN", "PROPN"})
    ctr = {k: Counter() for k in ("caps", "organ_floor", "organ_arm")}
    sctr = {k: Counter() for k in ("caps", "organ_floor", "organ_arm")}
    gvals: List[tuple] = []            # (P(individual) at the span head, gold-is-PROPN) for the graded sweep

    def bump(c, pr, gp):
        c["tp" if (pr and gp) else ("fp" if pr else ("fn" if gp else "tn"))] += 1

    for d in te:
        m_floor.new_document()
        m_arm.new_document()
        for s in d:
            words = [w for w, _ in s]
            gold = [g for _, g in s]
            p0 = m_floor.posterior(words)
            m_floor.update_document_register(words, p0)
            p1 = m_arm.posterior(words)
            m_arm.update_document_register(words, p1)
            t0 = [m_floor.tags[int(i)] for i in p0.argmax(axis=1)]
            t1 = [m_arm.tags[int(i)] for i in p1.argmax(axis=1)]
            caps = [bool(name_content_tokens([w])) for w in words]
            for i, g in enumerate(gold):
                gp = (g == "PROPN")
                bump(ctr["caps"], caps[i], gp)
                bump(ctr["organ_floor"], t0[i] == "PROPN", gp)
                bump(ctr["organ_arm"], t1[i] == "PROPN", gp)
            # SPAN level: maximal contiguous nominal runs ending in a NOUN/PROPN head (the NP_RUN shape the
            # attachment arm uses), built from EACH decider own categories so no arm gets a better span boundary.
            for k, tags in (("caps", gold), ("organ_floor", t0), ("organ_arm", t1)):
                i = 0
                while i < len(words):
                    if tags[i] in NP:
                        j = i
                        while j + 1 < len(words) and tags[j + 1] in NP:
                            j += 1
                        heads = [q for q in range(i, j + 1) if tags[q] in ("NOUN", "PROPN")]
                        if heads:
                            h = heads[-1]
                            gp = (gold[h] == "PROPN")
                            if k == "caps":
                                pr = bool(name_content_tokens(words[i:j + 1]))
                            elif k == "organ_floor":
                                pr = (t0[h] == "PROPN")
                            else:
                                pr = (t1[h] == "PROPN")
                                ip = m_arm.tag_idx.get("PROPN"); inn = m_arm.tag_idx.get("NOUN")
                                if ip is not None and inn is not None:
                                    a_, b_ = float(p1[h, ip]), float(p1[h, inn])
                                    gvals.append((a_ / max(1e-9, a_ + b_), gp))
                            bump(sctr[k], pr, gp)
                        i = j + 1
                    else:
                        i += 1

    def prf(c):
        p = c["tp"] / max(1, c["tp"] + c["fp"])
        r = c["tp"] / max(1, c["tp"] + c["fn"])
        return {"precision": round(p, 4), "recall": round(r, 4),
                "f1": round(2 * p * r / max(1e-9, p + r), 4), "tp": c["tp"], "fp": c["fp"], "fn": c["fn"]}

    # THE GRADED NAME BELIEF (phase 7 round 2, lead 2): the boolean the forward-wire patch returns is an argmax
    # over the head's category posterior. The brain's referent route is engaged to a DEGREE, so hand the consumers
    # P(individual) = P(PROPN) / (P(PROPN) + P(NOUN)) at the span head and let them threshold or weight it. Sweeping
    # the threshold says whether the boolean is sitting at the right operating point or merely at the argmax.
    graded = {}
    for thr in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9):
        c = Counter()
        for pn, gp in gvals:
            bump(c, pn >= thr, gp)
        graded["thr_%.1f" % thr] = prf(c)

    return {"corpus": corpus, "arm": arm, "span_graded": graded, "n_graded_spans": len(gvals),
            "token": {k: prf(v) for k, v in ctr.items()},
            "span": {k: prf(v) for k, v in sctr.items()}}


def population_decomposition() -> dict:
    """THE POPULATION FACTS THAT BOUND THIS LEVER, counted before anything is claimed (checklist item 4).
    Of the unseen tokens, how many have ANY earlier mention of the same string in their document? Of the
    PROPN<->NOUN confusions, how many are first mentions, and how many are document SINGLETONS (the string occurs
    exactly once in the whole document, so no discourse-history route -- forward OR backward -- can ever reach them)?"""
    from hdlab.coref import name_content_tokens          # the rule the ENTITY LAYER actually uses for name/common
    tr = read_docs(TRAIN)
    te = read_docs(TEST)
    vocab = set(w.lower() for d in tr for s in d for w, _ in s)
    m = LexicalCategories.load(LC.ASSET)
    n_unseen = n_rep = 0
    conf_first = conf_rep = conf_later_only = conf_singleton = 0
    pn = 0
    # THE FORWARD WIRE THAT DOES NOT EXIST: 8 live organs decide NAME vs COMMON with `coref.name_content_tokens`
    # (capitalisation + a stop-list), and NONE of them reads this organ's PROPN posterior -- `hdlab/coref.py`,
    # `hdlab/entity_resolver.py` and `hdlab/lexical_utils.py` contain the strings "upos"/"PROPN" ZERO times.
    # Score both decisions against the same gold so the size of the missing hand-off is a number, not a claim.
    cap_tp = cap_fp = cap_fn = 0
    org_tp = org_fp = org_fn = 0
    for d in te:
        strings: Counter = Counter()
        for s in d:
            for w, _ in s:
                strings[w.lower()] += 1
        seen: Counter = Counter()
        for s in d:
            words = [w for w, _ in s]
            gold = [g for _, g in s]
            pred = [m.tags[int(i)] for i in m.posterior(words).argmax(axis=1)]
            for w, g, p in zip(words, gold, pred):
                wl = w.lower()
                cap = bool(name_content_tokens([w]))
                gp = (g == "PROPN")
                op = (p == "PROPN")
                cap_tp += int(cap and gp); cap_fp += int(cap and not gp); cap_fn += int(gp and not cap)
                org_tp += int(op and gp); org_fp += int(op and not gp); org_fn += int(gp and not op)
                if wl not in vocab:
                    n_unseen += 1
                    if seen[wl] > 0:
                        n_rep += 1
                    if g != p and {g, p} == {"PROPN", "NOUN"}:
                        pn += 1
                        if seen[wl] > 0:
                            conf_rep += 1
                        else:
                            conf_first += 1
                            if strings[wl] > 1:
                                conf_later_only += 1
                            else:
                                conf_singleton += 1
                seen[wl] += 1
    def prf(tp, fp, fn):
        p_ = tp / max(1, tp + fp)
        r_ = tp / max(1, tp + fn)
        return {"precision": round(p_, 4), "recall": round(r_, 4),
                "f1": round(2 * p_ * r_ / max(1e-9, p_ + r_), 4), "tp": tp, "fp": fp, "fn": fn}

    return {"forward_wire_gap": {
                "capitalisation_rule_name_content_tokens": prf(cap_tp, cap_fp, cap_fn),
                "category_organ_PROPN_argmax": prf(org_tp, org_fp, org_fn),
                "note": ("The entity layer's name/common decision is the capitalisation row. The category organ's "
                         "row is what it would get by reading this organ instead. NO organ reads it today: "
                         "hdlab/coref.py, hdlab/entity_resolver.py and hdlab/lexical_utils.py contain 'upos' and "
                         "'PROPN' zero times, and 8 live organs route name/common through name_content_tokens.")},
            "n_unseen": n_unseen, "n_unseen_repeat": n_rep,
            "repeat_share": round(n_rep / max(1, n_unseen), 4),
            "propn_noun_total": pn, "conf_repeat": conf_rep, "conf_first": conf_first,
            "conf_first_but_recurs_later": conf_later_only, "conf_document_singleton": conf_singleton,
            "note": ("conf_document_singleton is the ARITHMETIC CEILING of every string-history route: those strings "
                     "occur exactly once in the whole document, so no register -- incremental or re-reading -- can "
                     "carry evidence about them. conf_repeat bounds the FORWARD (incremental) prior; "
                     "conf_repeat + conf_first_but_recurs_later bounds a RE-READING (second-pass) reader.")}


def run_heads(arm: str, cap_docs: int = 0) -> dict:
    """NO-REGRESS: the HEADS rung under the organ's OWN tags. The category organ is read DOCUMENT BY DOCUMENT (so the
    register is live), the attachment arm then reads its tags sentence by sentence exactly as it does today."""
    import hdlab.attachment_arm as AA
    from tools.build_attachment_validities import CORE_RELS
    tab = AA.load_attachment_validities()
    docs = read_docs_full(TEST)
    if cap_docs:
        docs = docs[:cap_docs]
    tr = read_docs(TRAIN)
    cache: dict = {}
    res: dict = {"arm": arm, "n_docs": len(docs)}
    for name in ("F_live", arm):
        lc = build(dict(ARMS[name]), docs=tr, entc_cache=cache)
        agree = atot = c = t = 0
        rt: dict = {}
        rh: dict = {}
        for d in docs:
            lc.new_document()
            for toks, gold_pos, gold_heads, rels in d:
                if len(toks) > 60:
                    post = lc.posterior(list(toks))
                    lc.update_document_register(list(toks), post)
                    continue
                post = lc.posterior(list(toks))
                tg = [lc.tags[int(i)] for i in post.argmax(axis=1)]
                lc.update_document_register(list(toks), post)
                for x, y in zip(tg, gold_pos):
                    agree += int(x == y)
                    atot += 1
                hd = AA.heads(list(toks), tg, tab)
                for i, g in enumerate(gold_heads, start=1):
                    if 0 <= g <= len(toks):
                        ok = int(hd.get(i, -1) == g)
                        c += ok
                        t += 1
                        r = rels[i - 1]
                        if r in CORE_RELS:
                            rt[r] = rt.get(r, 0) + 1
                            rh[r] = rh.get(r, 0) + ok
        res[name] = {"uas": round(c / max(1, t), 4), "n_arcs": t,
                     "tag_agreement": round(agree / max(1, atot), 4),
                     "per_relation": {r: round(rh[r] / rt[r], 3) for r in CORE_RELS if r in rt}}
        print("HEADS", name, json.dumps(res[name]), flush=True)
    res["d_uas"] = round(res[arm]["uas"] - res["F_live"]["uas"], 4)
    res["d_tag_agreement"] = round(res[arm]["tag_agreement"] - res["F_live"]["tag_agreement"], 4)
    return res


_TRAIN_DOCS = None


def train_docs():
    global _TRAIN_DOCS
    if _TRAIN_DOCS is None:
        _TRAIN_DOCS = read_docs(TRAIN)
    return _TRAIN_DOCS


def build(cfg: dict, docs=None, entc_cache: Optional[dict] = None) -> EntityPriorCategories:
    """LOAD the LIVE asset (so the floor is the live organ byte-for-byte) and accrue ONLY the new entity counts."""
    m = EntityPriorCategories.load(LC.ASSET)
    m.ent_kappa = float(cfg.get("ent_kappa", 0.0))
    m.theta_doc = cfg.get("theta_doc")
    m.ent_rich = bool(cfg.get("ent_rich", False))
    m.ent_novel = bool(cfg.get("ent_novel", False))
    m.ent_recency = int(cfg.get("ent_recency", 0))
    m.ent_rare = int(cfg.get("ent_rare", 0))
    m.ent_skip_first = bool(cfg.get("ent_skip_first", False))
    m.ent_decay = float(cfg.get("ent_decay", 1.0))
    m.ent_prec = float(cfg.get("ent_prec", 0.0))
    m.ent_nconf = int(cfg.get("ent_nconf", 0))
    m.reg_known_only = bool(cfg.get("reg_known_only", False))
    m.reg_offset = bool(cfg.get("reg_offset", False))
    m.ent_prec_online = cfg.get("ent_prec_online")
    m.ent_prec_decay = float(cfg.get("ent_prec_decay", 0.9))
    if m.reg_offset:
        m._build_shape_offset()
    m.ent_local = cfg.get("ent_local")
    key = ("rich" if m.ent_rich else "plain") + "|w%d" % m.ent_recency
    if entc_cache is not None and key in entc_cache:
        a, b = entc_cache[key]
        m.entc = defaultdict(Counter, {t: Counter(c) for t, c in a.items()})
        m.entc_u = defaultdict(Counter, {t: Counter(c) for t, c in b.items()})
        m._finalize_entity()
    else:
        m.accrue_entity_counts(docs if docs is not None else train_docs())
        if entc_cache is not None:
            entc_cache[key] = ({t: dict(c) for t, c in m.entc.items()},
                               {t: dict(c) for t, c in m.entc_u.items()})
    return m


def self_test() -> bool:
    print("SELF-TEST exp_entity_to_category_prior_v1")
    fails = []
    t0 = time.time()
    tr = read_docs(TRAIN)
    te = read_docs(TEST)
    print("  docs: train %d (%d sents) | test %d (%d sents)" % (
        len(tr), sum(len(d) for d in tr), len(te), sum(len(d) for d in te)))
    ok = len(tr) == 540 and len(te) == 316
    print("  %s W1 document boundaries recovered from `# newdoc` (540 / 316)" % ("PASS" if ok else "FAIL"))
    if not ok:
        fails.append("W1")

    reg = DiscourseRegister()
    raw = "The MSM said the MSM was wrong".split()
    lows = [w.lower() for w in raw]
    syms = []
    for i in range(len(raw)):
        syms.append(reg.symbol(lows[i]))
        reg.observe(raw, lows, i)
    ok2 = syms[1] == "e_first" and syms[4] == "e_rep_def"
    print("  %s W2 'MSM' is e_first at mention 1 and e_rep_def at mention 2 (no same-token loop): %s"
          % ("PASS" if ok2 else "FAIL", syms))
    if not ok2:
        fails.append("W2")

    reg = DiscourseRegister()
    raw = "a dax and some daxes".split()
    lows = [w.lower() for w in raw]
    for i in range(len(raw)):
        reg.observe(raw, lows, i)
    ok3 = reg.symbol("dax") == "e_rep_plural"
    print("  %s W3 Katz/Gelman KIND evidence: 'a dax' + 'daxes' -> %s" % ("PASS" if ok3 else "FAIL", reg.symbol("dax")))
    if not ok3:
        fails.append("W3")

    live = LexicalCategories.load(LC.ASSET)
    m0 = build(ARMS["F_live"], docs=tr[:40])
    mx = 0.0
    ndiff = ntok = 0
    for d in te[:12]:
        m0.new_document()
        for s in d:
            words = [w for w, _ in s]
            p1 = live.posterior(words)
            p2 = m0.posterior(words)
            mx = max(mx, float(np.abs(p1 - p2).max()))
            t1 = [live.tags[int(i)] for i in p1.argmax(axis=1)]
            t2 = [m0.tags[int(i)] for i in p2.argmax(axis=1)]
            ndiff += sum(1 for a, b in zip(t1, t2) if a != b)
            ntok += len(words)
            m0.update_document_register(words, p2)
    ok4 = mx < 1e-12 and ndiff == 0
    print("  %s W4 kappa=0 reproduces the LIVE organ (max posterior diff %.2e, %d/%d tag diffs)"
          % ("PASS" if ok4 else "FAIL", mx, ndiff, ntok))
    if not ok4:
        fails.append("W4")

    m1 = build(dict(ent_kappa=1.0, theta_doc=None), docs=tr)
    n_ent = sum(sum(c.values()) for c in m1.entc.values())
    lr = {s: round(m1.entc["PROPN"][s] / max(1, m1.entc["NOUN"][s]), 3) for s in ENT_SYMS}
    ok5 = n_ent > 100000 and lr["e_rep_bare"] > lr["e_first"] and lr["e_rep_plural"] < lr["e_first"]
    print("  %s W5 entity counts accrued (%d); PROPN:NOUN odds order e_rep_plural < e_first < e_rep_bare: %s"
          % ("PASS" if ok5 else "FAIL", n_ent, lr))
    if not ok5:
        fails.append("W5")

    before = sum(sum(c.values()) for c in m1.entc.values())
    tbl_before = dict(m1.log_entc["PROPN"])
    m1.observe_document([["Souter", "wrote", "again"]], [["PROPN", "VERB", "ADV"]])
    after = sum(sum(c.values()) for c in m1.entc.values())
    ok6 = after == before + 3 and m1.log_entc["PROPN"] != tbl_before
    print("  %s W6 ONLINE observe_document grows the counts (%d -> %d) and re-derives log P(E|c)"
          % ("PASS" if ok6 else "FAIL", before, after))
    if not ok6:
        fails.append("W6")

    m1.set_twin_permutation(17)
    ok7 = (sorted(m1._twin_perm.keys()) == sorted(m1._twin_perm.values())
           and any(k != v for k, v in m1._twin_perm.items()))
    print("  %s W7 permuted twin is a non-identity bijection on the alphabet: %s"
          % ("PASS" if ok7 else "FAIL", m1._twin_perm))
    if not ok7:
        fails.append("W7")

    p = os.path.join(REPO, "data", "hook_state", "lexical_categories_entity_counts_selftest.json")
    m1.save_entity_counts(p)
    m2 = build(dict(ent_kappa=1.0, theta_doc=None), docs=tr[:5])
    m2.entc = defaultdict(Counter)
    m2.load_entity_counts(p)
    ok8 = sum(sum(c.values()) for c in m2.entc.values()) == after
    print("  %s W8 entity counts save/load round-trip (%d)" % ("PASS" if ok8 else "FAIL", after))
    if not ok8:
        fails.append("W8")
    try:
        os.remove(p)
    except OSError:
        pass

    print("RESULT: %s  (%.1fs)" % ("PASS" if not fails else "FAIL (%s)" % ",".join(fails), time.time() - t0))
    return not fails


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--mode", default="full")
    ap.add_argument("--arms", default="")
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--twin-of", default="", help="arm name: also run its SHUFFLED-CHAINS and PERMUTED-TABLE twins")
    ap.add_argument("--out-name", default="metrics.json")
    ap.add_argument("--save-entity-counts", default="")
    ap.add_argument("--base-cache", default="", help="cache the F_live floor's per-unit hit vectors here and reuse")
    ap.add_argument("--corpus", default="ewt", choices=("ewt", "gum", "gentle"),
                    help="ewt = the brief's UD-EWT TEST population; gum/gentle = the well-powered modern documents")
    ap.add_argument("--cap-docs", type=int, default=0)
    ap.add_argument("--doc-stride", type=int, default=1)
    ap.add_argument("--online-adapt", default="", help="corpus to ADAPT on (the organ's own reads, no gold); the "
                                                       "scored corpus stays disjoint")
    ap.add_argument("--adapt-oracle", action="store_true",
                    help="ORACLE-CEILING PROBE ONLY: teach the online adaptation with the GOLD tags instead of the "
                         "organ's own reads, to separate 'the adaptation machinery is wrong' from 'the only "
                         "available teacher is wrong'. Never a shippable arm.")
    ap.add_argument("--population", action="store_true", help="the population arithmetic that bounds the lever")
    ap.add_argument("--heads", default="", help="arm name: HEADS no-regress rung under the organ's own tags")
    ap.add_argument("--forward-wire", type=int, default=0, help="n_docs for the forward-wire board measurement")
    ap.add_argument("--name-decision", action="store_true", help="score the name decision itself, 3 deciders")
    ap.add_argument("--timeout", type=float, default=0.0)
    args = ap.parse_args()

    if args.self_test:
        sys.exit(0 if self_test() else 1)

    if args.population:
        r = population_decomposition()
        print(json.dumps(r, indent=1))
        od = str(get_output_dir("exp_entity_to_category_prior_v1"))
        os.makedirs(od, exist_ok=True)
        with open(os.path.join(od, args.out_name), "w", encoding="utf-8") as f:
            json.dump({"cell": "exp_entity_to_category_prior_v1", "population": r}, f, indent=1)
        return

    if args.name_decision:
        r = name_decision(args.corpus, args.doc_stride)
        print(json.dumps(r, indent=1))
        od = str(get_output_dir("exp_entity_to_category_prior_v1"))
        os.makedirs(od, exist_ok=True)
        with open(os.path.join(od, args.out_name), "w", encoding="utf-8") as f:
            json.dump({"cell": "exp_entity_to_category_prior_v1", "name_decision": r}, f, indent=1)
        return

    if args.forward_wire:
        r = forward_wire(n_docs=args.forward_wire)
        print(json.dumps(r, indent=1))
        od = str(get_output_dir("exp_entity_to_category_prior_v1"))
        os.makedirs(od, exist_ok=True)
        with open(os.path.join(od, args.out_name), "w", encoding="utf-8") as f:
            json.dump({"cell": "exp_entity_to_category_prior_v1", "forward_wire": r}, f, indent=1)
        return

    if args.heads:
        r = run_heads(args.heads)
        print(json.dumps(r, indent=1))
        od = str(get_output_dir("exp_entity_to_category_prior_v1"))
        os.makedirs(od, exist_ok=True)
        with open(os.path.join(od, args.out_name), "w", encoding="utf-8") as f:
            json.dump({"cell": "exp_entity_to_category_prior_v1", "heads_no_regress": r}, f, indent=1)
        return

    smoke = bool(args.smoke) or args.mode == "smoke"
    tr = read_docs(TRAIN)
    te = read_corpus(args.corpus, args.cap_docs, args.doc_stride)
    vocab = set(w.lower() for d in tr for s in d for w, _ in s)
    if smoke:
        tr = tr[:120]
        te = te[:40]
    names = [a for a in (args.arms.split(",") if args.arms else list(ARMS)) if a]
    cache: dict = {}
    t0 = time.time()
    out = {"cell": "exp_entity_to_category_prior_v1", "smoke": smoke, "boot": args.boot,
           "corpus": args.corpus, "n_train_docs": len(tr), "n_test_docs": len(te),
           "n_test_sents": sum(len(d) for d in te), "n_test_tokens": sum(len(x) for d in te for x in d),
           "arms": {}}
    base = None

    def report(name, r, base_r):
        rec = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()
               if k not in ("per_doc", "per_sent", "rep_items")}
        if base_r is not None:
            rec["boot_rep_doc"] = paired_boot(base_r["per_doc"], r["per_doc"], "rep", "doc", args.boot)
            rec["boot_unk_doc"] = paired_boot(base_r["per_doc"], r["per_doc"], "unk", "doc", args.boot)
            rec["boot_all_doc"] = paired_boot(base_r["per_doc"], r["per_doc"], "all", "doc", args.boot)
            rec["boot_unk_sent"] = paired_boot(base_r["per_sent"], r["per_sent"], "unk", "sent", args.boot)
            rec["boot_all_sent"] = paired_boot(base_r["per_sent"], r["per_sent"], "all", "sent", args.boot)
        out["arms"][name] = rec
        print("%-14s overall %.4f | unseen %.4f | PN %3d (%d+%d) | REP n=%3d acc %.4f conf %2d | "
              "FIRST n=%4d acc %.4f conf %3d"
              % (name, r["acc"], r["unknown_acc"], r["propn_noun"], r["propn_to_noun"], r["noun_to_propn"],
                 r["rep_n"], r["rep_acc"], r["rep_propn_noun"],
                 r["first_n"], r["first_acc"], r["first_propn_noun"]))
        sys.stdout.flush()

    if args.base_cache and os.path.exists(args.base_cache):
        with open(args.base_cache, encoding="utf-8") as f:
            base = json.load(f)
        base["per_doc"] = [tuple(x) for x in base["per_doc"]]
        base["per_sent"] = [tuple(x) for x in base["per_sent"]]
        out["arms"]["F_live"] = {k: v for k, v in base.items() if k not in ("per_doc", "per_sent")}
        print("F_live (from cache)  overall %.4f | unseen %.4f | PN %d | REP n=%d conf %d | FIRST conf %d"
              % (base["acc"], base["unknown_acc"], base["propn_noun"], base["rep_n"],
                 base["rep_propn_noun"], base["first_propn_noun"]))
        names = [n for n in names if n != "F_live"]

    adapt_docs = None
    if args.online_adapt:
        # the ODD documents of the same corpus are the reading experience; the EVEN ones (te) are the ruler
        alld = read_corpus(args.online_adapt, 0, 1)
        adapt_docs = alld[1::args.doc_stride] if args.doc_stride > 1 else alld
        out["n_adapt_docs"] = len(adapt_docs)

    for name in names:
        m = build(dict(ARMS[name]), docs=tr, entc_cache=cache)
        if adapt_docs is not None and name != "F_live":
            online_adapt(m, adapt_docs, oracle=args.adapt_oracle)
        r = score_docs(m, te, vocab)
        if name == "F_live":
            base = r
            if args.base_cache:
                os.makedirs(os.path.dirname(args.base_cache) or ".", exist_ok=True)
                with open(args.base_cache, "w", encoding="utf-8") as f:
                    json.dump({k: v for k, v in r.items() if k != "rep_items"}, f)
        report(name, r, None if r is base else base)
        if args.save_entity_counts and name != "F_live":
            m.save_entity_counts(args.save_entity_counts)

    if args.twin_of:
        cfg = dict(ARMS[args.twin_of])
        m = build(cfg, docs=tr, entc_cache=cache)
        r = score_docs(m, te, vocab, twin_chain_seed=17)
        report("TWINchain_" + args.twin_of, r, base)
        m2 = build(cfg, docs=tr, entc_cache=cache)
        m2.set_twin_permutation(17)
        r2 = score_docs(m2, te, vocab)
        report("TWINperm_" + args.twin_of, r2, base)

    out["elapsed_s"] = round(time.time() - t0, 1)
    od = str(get_output_dir("exp_entity_to_category_prior_v1"))
    os.makedirs(od, exist_ok=True)
    p = os.path.join(od, args.out_name)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print("wrote", p, "in", out["elapsed_s"], "s")


if __name__ == "__main__":
    main()
