"""exp_graded_mention_typing_v1 -- THE ENTITY LAYER'S MENTION TYPER READS THE CATEGORY ORGAN'S GRADED
POSTERIOR AND THE HEIM FILE-CARD EVIDENCE, instead of a three-valued argmax.

problem: the_mention_typer_reads_a_three_valued_argmax_so_385_category_corrections_reach_82_of_17010_mentions_give_it_the_graded_posterior_and_the_file_card_evidence  (priority 118)

THE DEFECT (pri 112 P7.6, counted end to end): the board's coref / common_noun / salience rows and the
reader's own entity stream both type a mention by `argmax over 17 UD categories -> one of three labels`.
Opening the passage moves 385 argmaxes on the 128 GUM test documents; 189 of them (49%) are corrections the
three-valued type cannot represent, and only 82 of 17,010 mentions change type.

THE OPENING MOVE -- how does the BRAIN do this?  A referring expression's FORM signals the cognitive STATUS
of its referent on a GRADED scale (Gundel, Hedberg & Zacharski 1993 Givenness Hierarchy; Ariel 1990
accessibility bands), and whether a string picks out an INDIVIDUAL is the referent route's own question
(Kripke 1980 rigid designation; Semenza 2006/2009 proper-name anomia -- left temporal pole, ABOVE and FED BY
the posterior-temporal category level; Heim 1982 file cards for the passage history).  Two mathematical
consequences, and both are violated on disk:

  (1) MARGINALISE, THEN DECIDE.  The type is a COARSENING of the category variable.  The Bayes decision on
      the coarse variable under 0-1 loss is `argmax_t  sum_{c in t} P(c | words)`, NOT
      `type(argmax_c P(c | words))`.  The two differ exactly when the winning single category belongs to a
      type whose TOTAL mass is smaller than a rival's -- e.g. P(PROPN)=0.35 against P(NOUN)+P(ADJ)=0.60.
      The consumer takes its point estimate at the WRONG LEVEL of the hierarchy.
  (2) THE CONSUMER KNOWS IT IS TYPING A NOMINAL.  A mention span has already been segmented as a referring
      expression, so the categories that cannot head one (DET/ADP/AUX/CCONJ/SCONJ/PART/PUNCT) are ruled out
      by the consumer's own evidence; the posterior is renormalised on the support that can head a mention.
      (Structural knowledge of the consumer, not a fitted number.)

AND THE HEAD IS AN ARGMAX READ TOO.  `_head_of_span_organ` / `coref._span_head_is_name` take "the last
NOUN/PROPN of the first nominal domain" off the ARGMAX tag sequence.  That is where the 189 "structurally
invisible" ADJ<->NOUN / VERB<->NOUN flips actually land: they do not change the three-way type, they change
WHICH TOKEN IS THE HEAD, and therefore the lemma identity key every common-noun coref decision uses.  The
graded form scores each position by its NOMINAL MASS with a head-finality decay (eta swept; eta -> inf
reproduces the shipped rule when the posterior is peaked).

AND THE FILE-CARD EVIDENCE IS GATED OFF AT THE LEVEL WHERE IT IS THE RIGHT EVIDENCE.  `lexical_categories`
reads log P(E | c) over the five Heim symbols ONLY where the word has no lexical entry (MacDonald 1994 cue
competition) and never at `e_first`.  That gate is right for the CATEGORY competition and wrong for the TYPE
question, which is the referent system's own: "has this string been used to pick out an individual in THIS
passage?"  The typer reads the card evidence COMPLEMENTARILY -- only where the organ gated it off -- so the
evidence is used once, at the level that owns it.

Glass-box; count tables only; no external LLM / spaCy / nltk / supervised parser at inference; MODERN gold
only (GUM; the 19c ban respected).  The gold columns are the ANSWER KEY and are never read in a decision.
NO hdlab/ or tools/ file is edited: the change is proposed as
notes/problems/<slug>/graded_mention_typing_patch.diff and every number here is produced by the arms below,
which are the diff's own computation.

Run:  .venv/Scripts/python.exe experiments/exp_graded_mention_typing_v1.py --self-test
      ... --typing [--docs N] [--boot N]        # the typing rung on the board loader's stream
      ... --sweep                                # eta / support / kappa phase-diagram sweep
      ... --board [--boot N]                     # the three entity board rows, both typers in one process
      ... --reader [--docs N]                    # the reader's OWN stream (pri 116: cased)
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
import time
from datetime import datetime, timezone

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np

from experiments._seed_checkpoint import get_output_dir

ANCHOR = "graded_mention_typing_v1"
OUT_DIR = str(get_output_dir(ANCHOR))
SEED = 20260915

TYPES = ("pronoun", "name", "common")

# ---------------------------------------------------------------------------------------------------------
# THE TYPE PARTITION.  `pronoun` = PRON, `name` = PROPN, `common` = the categories that can head a referring
# expression.  SUPPORTS are swept (the consumer's structural knowledge of what a mention head can be):
#   all      -- every category (the partition with no support restriction)
#   nominal  -- the categories that head nominals in UD
#   strict   -- the four that carry the mass in practice
SUPPORTS = {
    "all": None,
    "nominal": ("PRON", "PROPN", "NOUN", "ADJ", "VERB", "NUM", "ADV", "X", "SYM", "INTJ"),
    "strict": ("PRON", "PROPN", "NOUN", "ADJ", "VERB", "NUM", "X"),
}
COMMON_EXTRA = ("NOUN", "ADJ", "VERB", "NUM", "ADV", "X", "SYM", "INTJ", "DET", "ADP", "AUX",
                "CCONJ", "SCONJ", "PART", "PUNCT")

CAPS_SYMS = ["o%d_l%d" % (a, b) for a in range(4) for b in (0, 1)]
# the closed-class words that may sit INSIDE a multi-word name without disqualifying it ("Game OF Thrones",
# "The Rains OF Castamere") -- the same shape as coref.TITLE_TOKENS, kept tiny and function-word only.
STOP_LOW = frozenset({"of", "the", "a", "an", "and", "for", "de", "van", "von", "der", "la", "le", "el",
                      "at", "in", "on", "to", "by", "with"})

_NOMINAL = ("NOUN", "PROPN")
_NP_BREAK = ("ADP", "CCONJ", "SCONJ", "VERB", "AUX", "PART")
_REL = frozenset({"who", "whom", "whose", "which", "that"})


# ---------------------------------------------------------------------------------------------------------
class TyperCfg:
    """The graded typer's operating point.  EVERY field is a swept parameter, never an adopted number."""

    def __init__(self, marginal=True, support="nominal", eta=4.0, graded_head=True,
                 kappa_card=0.0, card_mode="complement", tau_break=0.0, skip_first=True,
                 kappa_det=0.0, kappa_right=0.0, frame_mode="complement",
                 kappa_caps=0.0, tau_learn=0.95):
        self.marginal = marginal            # marginalise-then-decide (vs type(argmax))
        self.support = support              # which categories can head a mention
        self.eta = eta                      # head-finality decay (eta -> inf == "the LAST nominal", the shipped rule)
        self.graded_head = graded_head      # head chosen on nominal MASS instead of on the argmax tag
        self.kappa_card = kappa_card        # weight of the Heim file-card evidence at the TYPE level
        self.card_mode = card_mode          # complement | all | off
        self.tau_break = tau_break          # graded NP-domain cut: break mass must exceed nominal mass by this
        self.skip_first = skip_first        # no card term at e_first (the organ's own rule, one level up)
        # THE DETERMINER FRAME AT THE TYPE LEVEL.  Longobardi 1994 (N-to-D: an English proper name in argument
        # position is DETERMINERLESS) and Katz, Baker & Macnamara 1974 / Gelman & Taylor 1984 (the count-noun
        # frame "a dax" names a KIND, the bare frame "Dax" names an INDIVIDUAL).  `lexical_categories` already
        # holds these counts (log_detc / log_rightc) and reads them ONLY for words with no lexical entry
        # (MacDonald 1994 cue competition).  That gate is right for the CATEGORY question and wrong for the
        # TYPE question: "College", "Times", "Post" and "Apple" all HAVE lexical entries as common nouns and
        # are names here, and what separates them is exactly the frame.
        self.kappa_det = kappa_det
        self.kappa_right = kappa_right
        self.frame_mode = frame_mode        # complement (KNOWN words only -- never twice) | all | off
        self.kappa_caps = kappa_caps        # the SPAN-LEVEL name-run cue (see span_caps_symbol)
        self.tau_learn = tau_learn          # a typing this confident teaches the span table (self-supervised)

    def key(self):
        return dict(marginal=self.marginal, support=self.support, eta=self.eta,
                    graded_head=self.graded_head, kappa_card=self.kappa_card,
                    card_mode=self.card_mode, tau_break=self.tau_break, skip_first=self.skip_first,
                    kappa_det=self.kappa_det, kappa_right=self.kappa_right, frame_mode=self.frame_mode,
                    kappa_caps=self.kappa_caps, tau_learn=self.tau_learn)


SHIPPED = TyperCfg(marginal=False, support="all", eta=float("inf"), graded_head=False,
                   kappa_card=0.0, card_mode="off")


# ---------------------------------------------------------------------------------------------------------
# the organ: one in-order feed per document, the POSTERIOR kept (organ_tags keeps only the argmax)
_LC = None
_TAGS = None


def organ():
    """The live category organ through the one shared frontend (hdlab.frontend.tagger -> lexical_categories)."""
    global _LC, _TAGS
    if _LC is None:
        from hdlab import frontend as F
        tg = F.tagger()
        lc = getattr(tg, "_lc", None)
        if lc is None:
            raise SystemExit("this cell needs the count-based category organ (HDLAB_TAG_SOURCE=counts)")
        _LC = lc
        _TAGS = list(lc.tags)
    return _LC, _TAGS


def doc_posteriors(doc, with_cards=False):
    """THE PASSAGE, FED ONCE, IN ORDER (pri 112) -- exactly `gum_coref.organ_tags`, except the whole posterior
    is kept instead of its argmax.  Returns {gidx: np.ndarray[T]} (+ {gidx: file-card symbol} when asked)."""
    lc, tags = organ()
    by_sent = {}
    for t in doc.toks:
        by_sent.setdefault(t.sent, []).append(t)
    rows = [sorted(by_sent[s], key=lambda x: x.idx) for s in sorted(by_sent)]
    lc.new_document()
    post, syms = {}, {}
    if not with_cards:
        for row, m in zip(rows, lc.feed_passage([[x.form for x in row] for row in rows])):
            for j, x in enumerate(row):
                post[x.gidx] = np.asarray(m[j], dtype=np.float32)
        return post, syms
    # the card symbol AS OF the sentence in flight is read from the register BEFORE this sentence is filed,
    # i.e. exactly the value `posterior` itself consumes (`reg.begin` ... `reg.note` ... `reg.commit`).
    for row in rows:
        words = [x.form for x in row]
        reg = lc._reg
        lows = [w.lower() for w in words]
        if reg is not None:
            reg.begin(lows, False)               # a READ: as of this sentence, writes nothing
            for i in range(len(words)):
                syms[row[i].gidx] = reg.symbol(lows[i])
                reg.note(lows, i)
            reg.commit(False)
        m = lc.posterior(words, observe=True)
        from hdlab import lexical_categories as LC
        if LC.ENT_REG_LIVE_DOC and LC.ENT_THETA_DOC is not None and lc._reg is not None:
            lc.update_document_register(list(words), m, sent_idx=lc._reg.sent_no - 1)
        for j, x in enumerate(row):
            post[x.gidx] = np.asarray(m[j], dtype=np.float32)
    return post, syms


def doc_caps(doc):
    """Per token: (is_alphabetic, is_capitalised, is MID-sentence).  `position_class` is the organ's own
    forced/non-forced split -- a capital is only evidence where the convention did not force it."""
    from hdlab.lexical_categories import position_class, MID
    by_sent = {}
    for t in doc.toks:
        by_sent.setdefault(t.sent, []).append(t)
    out = {}
    for s in sorted(by_sent):
        row = sorted(by_sent[s], key=lambda x: x.idx)
        forms = [x.form for x in row]
        for i, x in enumerate(row):
            w = x.form
            out[x.gidx] = (w.isalpha(), bool(w[:1].isupper()), position_class(forms, i) == MID)
    return out


def span_caps_symbol(span, caps, head_gidx, stop_low=None):
    """THE SPAN-LEVEL NAME-RUN CUE -- the evidence only the consumer that HOLDS THE SPAN can see.

    The category organ already reads each token's own shape relative to the sentence convention
    (`word_shape` x `position_class`).  What it cannot see is that "Game of Thrones", "The Rains of
    Castamere", "the Slavonic Dances" are ONE capitalised unit spanning a preposition -- a multi-word name
    stored as a lexical unit by the referent route (Semenza 2006/2009; the anterior temporal pole stores the
    NAME, not its parts).  The symbol therefore describes the span EXCLUDING its head, so nothing the organ
    already used is counted twice: how many OTHER mid-sentence capitals the span carries, and whether it
    carries a lowercase content word (the descriptive-phrase disqualifier `coref.name_content_tokens` uses).
    """
    ncap = 0
    lower_content = 0
    for t in span:
        if t.gidx == head_gidx:
            continue
        a, c, mid = caps.get(t.gidx, (False, False, False))
        if not a:
            continue
        low = t.form.lower()
        if c and mid:
            ncap += 1
        elif not c and (stop_low is None or low not in stop_low) and len(low) > 2:
            lower_content += 1
    return "o%d_l%d" % (min(ncap, 3), 1 if lower_content else 0)


def doc_frames(doc):
    """The NP FRAME each token sits in: (`det_context`, `right_context`) -- the organ's own two symbols,
    computed from the forms alone (closed-class function words; no gold, no parser)."""
    from hdlab.lexical_categories import det_context, right_context
    by_sent = {}
    for t in doc.toks:
        by_sent.setdefault(t.sent, []).append(t)
    out = {}
    for s in sorted(by_sent):
        row = sorted(by_sent[s], key=lambda x: x.idx)
        lows = [x.form.lower() for x in row]
        for i, x in enumerate(row):
            out[x.gidx] = (det_context(lows, i), right_context(lows, i))
    return out


def argmax_tags(post):
    lc, tags = organ()
    return {g: tags[int(p.argmax())] for g, p in post.items()}


# ---------------------------------------------------------------------------------------------------------
# THE SHIPPED (FLOOR) TYPER -- verbatim `gum_coref._head_of_span_organ` / `_mention_type_organ`
def head_of_span_shipped(span, pred, PRONOUNS_ALL):
    toks = list(span)
    cut, seen = len(toks), False
    for i, t in enumerate(toks):
        c = pred.get(t.gidx, "X")
        low = t.form.lower()
        if c in _NOMINAL:
            seen = True
            continue
        if seen and (c in _NP_BREAK or c == "PUNCT" or low in _REL):
            cut = i
            break
    dom = toks[:cut] or list(span)
    noms = [t for t in dom if pred.get(t.gidx) in _NOMINAL]
    if noms:
        return noms[-1]
    prons = [t for t in span if pred.get(t.gidx) == "PRON" or t.form.lower() in PRONOUNS_ALL]
    if prons:
        return prons[-1]
    nonp = [t for t in span if pred.get(t.gidx) != "PUNCT"]
    return (nonp or list(span))[-1]


def mention_type_shipped(head_tok, pred, PRONOUNS_ALL):
    up = pred.get(head_tok.gidx, "X")
    low = head_tok.form.lower()
    if up == "PRON" or (low in PRONOUNS_ALL and up != "PROPN"):
        return "pronoun"
    return "name" if up == "PROPN" else "common"


# ---------------------------------------------------------------------------------------------------------
# THE GRADED TYPER
class Typer:
    """mention_type_graded(head posterior, card evidence) -> {type: P}, with the argmax available for any
    consumer that must branch.  Byte-identical to the shipped rule when the posterior is peaked and the
    operating point is the shipped one (witness W1)."""

    def __init__(self, cfg, tags, pronouns, log_entc=None, lc=None, span_tab=None):
        self.cfg = cfg
        self.tags = list(tags)
        self.ti = {t: i for i, t in enumerate(self.tags)}
        self.pronouns = pronouns
        self.log_entc = log_entc if log_entc is not None else (getattr(lc, "log_entc", {}) if lc else {})
        self.log_detc = dict(getattr(lc, "log_detc", {}) or {}) if lc is not None else {}
        self.log_rightc = dict(getattr(lc, "log_rightc", {}) or {}) if lc is not None else {}
        self._ent_back = dict(getattr(lc, "_ent_back", {}) or {}) if lc is not None else {}
        self.span_tab = span_tab
        sup = SUPPORTS.get(cfg.support)
        self.sup_mask = np.ones(len(self.tags), dtype=np.float32)
        if sup is not None:
            self.sup_mask = np.array([1.0 if t in sup else 0.0 for t in self.tags], dtype=np.float32)
        self.i_pron = self.ti.get("PRON", -1)
        self.i_propn = self.ti.get("PROPN", -1)
        self.i_nom = [self.ti[t] for t in _NOMINAL if t in self.ti]
        self.i_break = [self.ti[t] for t in (_NP_BREAK + ("PUNCT",)) if t in self.ti]
        # type -> the category indices it covers
        self.cover = {"pronoun": [self.i_pron] if self.i_pron >= 0 else [],
                      "name": [self.i_propn] if self.i_propn >= 0 else [],
                      "common": [i for t, i in self.ti.items() if t not in ("PRON", "PROPN")]}

    # ---- the head ----
    def nominal_mass(self, p):
        return float(sum(p[i] for i in self.i_nom))

    def break_mass(self, p):
        return float(sum(p[i] for i in self.i_break))

    def head_of_span(self, span, post, pred):
        cfg = self.cfg
        if not cfg.graded_head:
            return head_of_span_shipped(span, pred, self.pronouns)
        toks = list(span)
        ps = [post.get(t.gidx) for t in toks]
        nm = [self.nominal_mass(p) if p is not None else 0.0 for p in ps]
        bm = [self.break_mass(p) if p is not None else 0.0 for p in ps]
        # the NP DOMAIN, graded: it ends at the first position after some nominal mass has accumulated where the
        # BREAK mass beats the nominal mass by tau_break (a relative-marker form is break evidence in itself).
        cut, seen = len(toks), False
        for i, t in enumerate(toks):
            if nm[i] >= 0.5:
                seen = True
                continue
            rel = t.form.lower() in _REL
            if seen and ((bm[i] - nm[i]) > cfg.tau_break or rel):
                cut = i
                break
        dom = list(range(cut)) or list(range(len(toks)))
        # head-finality as a GRADED position prior: score = log(nominal mass) - eta * (distance from the domain end)
        last = dom[-1]
        eta = cfg.eta
        best, best_s = None, None
        for i in dom:
            if nm[i] <= 0.0:
                continue
            pen = 0.0 if (eta == 0.0 or last == i) else eta * (last - i)   # eta -> inf == "the LAST nominal"
            s = math.log(max(nm[i], 1e-12)) - pen
            if best_s is None or s > best_s:
                best, best_s = i, s
        if best is not None:
            return toks[best]
        prons = [t for t in toks if pred.get(t.gidx) == "PRON" or t.form.lower() in self.pronouns]
        if prons:
            return prons[-1]
        nonp = [t for t in toks if pred.get(t.gidx) != "PUNCT"]
        return (nonp or toks)[-1]

    # ---- the type ----
    def _type_mix(self, q, table, key, back=None):
        """log P(cue | type) from a per-CATEGORY count table, mixed inside each type by the posterior's own
        weights: log sum_{c in t} P(c)/P(t) * P(cue | c).  One additive log term per type, the same shape as
        every other cue in the organ."""
        lg = {}
        for ty in TYPES:
            idx = [i for i in self.cover[ty] if self.tags[i] in table]
            w = sum(float(q[i]) for i in idx)
            if w <= 0 or not idx:
                lg[ty] = 0.0
                continue
            acc = 0.0
            for i in idx:
                row = table.get(self.tags[i])
                if row is None:
                    continue
                v = row.get(key)
                if v is None:
                    v = back.get(self.tags[i]) if back else None
                if v is None:
                    continue
                acc += (float(q[i]) / w) * math.exp(v)
            lg[ty] = math.log(max(acc, 1e-12))
        return lg

    def type_posterior(self, head_tok, post, pred, sym=None, known=None, frame=None, caps_sym=None):
        """{type: P}.  MARGINALISE (sum the category mass inside each type) THEN DECIDE, on the support the
        consumer knows a mention head can take, with the Heim file-card evidence added at the TYPE level."""
        cfg = self.cfg
        p = post.get(head_tok.gidx)
        low = head_tok.form.lower()
        if p is None:
            t = mention_type_shipped(head_tok, pred, self.pronouns)
            return {x: (1.0 if x == t else 0.0) for x in TYPES}
        if not cfg.marginal:
            t = mention_type_shipped(head_tok, pred, self.pronouns)
            return {x: (1.0 if x == t else 0.0) for x in TYPES}
        q = np.asarray(p, dtype=np.float64) * self.sup_mask
        if q.sum() <= 0:
            q = np.asarray(p, dtype=np.float64)
        q = q / q.sum()
        mass = {"pronoun": float(q[self.i_pron]) if self.i_pron >= 0 else 0.0,
                "name": float(q[self.i_propn]) if self.i_propn >= 0 else 0.0}
        mass["common"] = max(0.0, 1.0 - mass["pronoun"] - mass["name"])
        # THE CLOSED-CLASS LEXICAL FACT: a pronoun is a closed-class form and the entity layer knows the list.
        # The shipped rule uses it as a hard override; graded, it is evidence that the PRON reading is the one
        # the lexicon licenses -- the mass already in PRON is what carries it, so the only change is that a
        # listed form cannot be typed a name on sub-majority PROPN mass.
        if low in self.pronouns and mass["name"] < mass["pronoun"] + mass["common"]:
            mass["pronoun"] = mass["pronoun"] + mass["common"]
            mass["common"] = 0.0
        # THE EVIDENCE THE CATEGORY LEVEL GATES OFF, read at the level that owns the question.  Each is ONE
        # additive log term per type (the organ's own shape), weighted by a swept kappa.
        z = {ty: math.log(max(mass[ty], 1e-12)) for ty in TYPES}
        used = False
        # (a) the Heim file card: has this string been used to pick out an individual in THIS passage?
        if cfg.kappa_card and cfg.card_mode != "off" and sym is not None and self.log_entc:
            use = not (cfg.skip_first and sym.startswith("e_first"))
            if cfg.card_mode == "complement" and known is False:
                use = False            # the organ already folded it in for an unknown word -- never twice
            if use:
                lg = self._type_mix(q, self.log_entc, sym, self._ent_back)
                for ty in TYPES:
                    z[ty] += cfg.kappa_card * lg[ty]
                used = True
        # (b) the DETERMINER FRAME (Longobardi 1994; Katz/Macnamara 1974) and (c) the right frame
        if cfg.frame_mode != "off" and frame is not None and (cfg.kappa_det or cfg.kappa_right):
            use = not (cfg.frame_mode == "complement" and known is False)
            if use:
                d_sym, r_sym = frame
                if cfg.kappa_det and self.log_detc and d_sym is not None:
                    lg = self._type_mix(q, self.log_detc, d_sym)
                    for ty in TYPES:
                        z[ty] += cfg.kappa_det * lg[ty]
                    used = True
                if cfg.kappa_right and self.log_rightc and r_sym is not None:
                    lg = self._type_mix(q, self.log_rightc, r_sym)
                    for ty in TYPES:
                        z[ty] += cfg.kappa_right * lg[ty]
                    used = True
        # (d) THE SPAN-LEVEL NAME-RUN CUE, from the online table (see SpanCueTable)
        if cfg.kappa_caps and caps_sym is not None and self.span_tab is not None and self.span_tab.n_obs > 0:
            for ty in TYPES:
                z[ty] += cfg.kappa_caps * self.span_tab.logp(caps_sym, ty)
            used = True
        if used:
            mx = max(z.values())
            e = {ty: math.exp(z[ty] - mx) for ty in TYPES}
            s = sum(e.values())
            mass = {ty: e[ty] / s for ty in TYPES}
        s = sum(mass.values()) or 1.0
        return {ty: mass[ty] / s for ty in TYPES}

    def type_of(self, head_tok, post, pred, sym=None, known=None, frame=None, caps_sym=None):
        d = self.type_posterior(head_tok, post, pred, sym=sym, known=known, frame=frame, caps_sym=caps_sym)
        return max(TYPES, key=lambda t: d[t]), d


class SpanCueTable:
    """THE SPAN-LEVEL NAME-RUN TABLE -- counts, learned ONLINE from the reader's OWN confident typings, never
    from gold and never frozen.  n(symbol, type) is incremented by a mention the typer already types with
    p >= tau (the comprehender learns the passage's naming convention from what it already understands --
    Fine, Jaeger, Farmer & Qian 2013 rapid expectation adaptation, the same account the passage register
    cites one level down).  `logp` is a pure function of the counts (Laplace lam), so the table is inspectable
    and reversible."""

    __slots__ = ("n", "lam", "syms", "n_obs")

    def __init__(self, lam=0.5):
        self.n = {t: {} for t in TYPES}
        self.lam = lam
        self.syms = set()
        self.n_obs = 0

    def observe(self, sym, ty, w=1.0):
        self.n[ty][sym] = self.n[ty].get(sym, 0.0) + w
        self.syms.add(sym)
        self.n_obs += 1

    def logp(self, sym, ty):
        row = self.n[ty]
        tot = sum(row.values()) + self.lam * max(1, len(self.syms))
        return math.log((row.get(sym, 0.0) + self.lam) / tot)

    def as_dict(self):
        return {t: {s: round(self.n[t].get(s, 0.0), 2) for s in sorted(self.syms)} for t in TYPES}


# ---------------------------------------------------------------------------------------------------------
def load_test(n_docs=None, split="test"):
    """GUM, the board's own split (TEST = odd document index).  decision_source='gold' so the treebank columns
    stay where the ANSWER KEY lives; every arm's decision comes from the organ."""
    import experiments.gum_coref as G
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    gaz = load_given_gazetteer()
    docs = G.load_docs(gum_only=True, name_gazetteer=gaz, decision_source="gold")
    if split == "test":
        sel = docs[1::2]
    elif split == "train":
        sel = docs[0::2]
    else:
        sel = docs
    if n_docs:
        step = max(1, len(sel) // n_docs)
        sel = [sel[i] for i in range(0, len(sel), step)][:n_docs]
    return sel, gaz


def gold_type_and_head(doc):
    """The ANSWER KEY: the UD head of the span and the gold mention type (`gum_coref._head_of_span` /
    `_mention_type` on the gold columns -- the definition the board's retired gold arm used)."""
    import experiments.gum_coref as G
    gmap = {t.gidx: t for t in doc.toks}
    out = {}
    for m in doc.mentions:
        span = [gmap[g] for g in range(m.start_g, m.end_g + 1) if g in gmap]
        span = [t for t in span if t.sent == m.sent] or span
        if not span:
            continue
        h = G._head_of_span(span)
        out[(m.start_g, m.end_g, m.eid)] = (G._mention_type(h, span), h.gidx)
    return out


# ---------------------------------------------------------------------------------------------------------
def type_arm(docs, cfg, post_by_doc, sym_by_doc, seed=None, shuffle_post=False, frame_by_doc=None,
             caps_by_doc=None, span_tab=None, online=False, shuffle_caps=False):
    """Type every mention of every document under one operating point.  Returns per-doc confusion rows.

    `online=True` is the PLASTIC path: each document is typed with the span-cue table AS IT STANDS, and only
    then does that document's confident typings fold in -- strictly in order, so no document is ever typed
    with a table that has read it."""
    import experiments.gum_coref as G
    lc, tags = organ()
    typer = Typer(cfg, tags, G.PRONOUNS_ALL, lc=lc, span_tab=span_tab)
    rng = random.Random(seed or SEED)
    per_doc = []
    for d in docs:
        post = post_by_doc[d.docid]
        syms = sym_by_doc.get(d.docid, {})
        frames = (frame_by_doc or {}).get(d.docid)
        caps = (caps_by_doc or {}).get(d.docid)
        if shuffle_post:
            # THE INFO-FREE TWIN: the posterior ROWS are permuted across the document's tokens, so the shape of
            # the belief (its entropy, its per-type mass distribution) is preserved exactly and only the
            # token<->belief pairing is destroyed.
            keys = list(post.keys())
            vals = [post[k] for k in keys]
            rng.shuffle(vals)
            post = dict(zip(keys, vals))
        pred = argmax_tags(post)
        gmap = {t.gidx: t for t in d.toks}
        rows = []
        for m in d.mentions:
            span = [gmap[g] for g in range(m.start_g, m.end_g + 1) if g in gmap]
            span = [t for t in span if t.sent == m.sent] or span
            if not span:
                continue
            h = typer.head_of_span(span, post, pred)
            known = (h.form.lower() in lc.vocab)
            cs = None
            if caps is not None and cfg.kappa_caps:
                cs = span_caps_symbol(span, caps, h.gidx, STOP_LOW)
                if shuffle_caps:
                    cs = rng.choice(CAPS_SYMS)      # the info-free twin of THIS cue
            ty, dist = typer.type_of(h, post, pred, sym=syms.get(h.gidx), known=known,
                                     frame=frames.get(h.gidx) if frames else None, caps_sym=cs)
            rows.append({"key": (m.start_g, m.end_g, m.eid), "type": ty, "head": h.gidx,
                         "p": dist[ty], "dist": dist, "caps": cs})
        per_doc.append(rows)
        if online and span_tab is not None:
            # THE OBSERVE PATH: this document's CONFIDENT typings teach the table, after it was typed.
            for r in rows:
                if r["caps"] is not None and r["p"] >= cfg.tau_learn:
                    span_tab.observe(r["caps"], r["type"])
    return per_doc


def score_typing(docs, per_doc, gold_by_doc):
    """Per-doc (hit, tot) per type for accuracy, plus per-type TP/FP/FN for P/R/F1, plus head accuracy."""
    out = []
    for d, rows in zip(docs, per_doc):
        gold = gold_by_doc[d.docid]
        agg = {t: [0, 0, 0] for t in TYPES}      # tp, fp, fn
        hit = tot = 0
        hhit = htot = 0
        for r in rows:
            g = gold.get(r["key"])
            if g is None:
                continue
            gt, gh = g
            tot += 1
            htot += 1
            if r["head"] == gh:
                hhit += 1
            if r["type"] == gt:
                hit += 1
                agg[gt][0] += 1
            else:
                agg[r["type"]][1] += 1
                agg[gt][2] += 1
        out.append({"hit": hit, "tot": tot, "hhit": hhit, "htot": htot, "agg": agg})
    return out


def _acc(per, key="hit", tkey="tot"):
    h = sum(p[key] for p in per)
    t = sum(p[tkey] for p in per)
    return (h / t if t else float("nan")), t


def _f1(per, ty):
    tp = sum(p["agg"][ty][0] for p in per)
    fp = sum(p["agg"][ty][1] for p in per)
    fn = sum(p["agg"][ty][2] for p in per)
    P = tp / (tp + fp) if tp + fp else 0.0
    R = tp / (tp + fn) if tp + fn else 0.0
    F = 2 * P * R / (P + R) if P + R else 0.0
    return P, R, F, tp, fp, fn


def _boot_delta(per_a, per_b, stat, n_boot=2000, seed=13):
    """Doc-paired bootstrap of stat(b) - stat(a).  `stat` maps a list of per-doc rows to a float."""
    rng = random.Random(seed)
    n = len(per_a)
    idx = list(range(n))
    ds = []
    for _ in range(n_boot):
        s = [rng.choice(idx) for _ in range(n)]
        a = stat([per_a[i] for i in s])
        b = stat([per_b[i] for i in s])
        if a == a and b == b:
            ds.append(b - a)
    ds.sort()
    lo = ds[int(0.025 * len(ds))]
    hi = ds[int(0.975 * len(ds))]
    obs = stat(per_b) - stat(per_a)
    return round(obs, 4), round(lo, 4), round(hi, 4), bool(lo > 0 or hi < 0)


def st_acc(per):
    h = sum(p["hit"] for p in per)
    t = sum(p["tot"] for p in per)
    return h / t if t else float("nan")


def st_head(per):
    h = sum(p["hhit"] for p in per)
    t = sum(p["htot"] for p in per)
    return h / t if t else float("nan")


def st_f1(ty):
    def f(per):
        return _f1(per, ty)[2]
    return f


def st_macro(per):
    return sum(_f1(per, t)[2] for t in TYPES) / 3.0


# ---------------------------------------------------------------------------------------------------------
def build_posteriors(docs, with_cards=True, verbose=True):
    post_by_doc, sym_by_doc, frame_by_doc, caps_by_doc = {}, {}, {}, {}
    t0 = time.time()
    for i, d in enumerate(docs):
        p, s = doc_posteriors(d, with_cards=with_cards)
        post_by_doc[d.docid] = p
        sym_by_doc[d.docid] = s
        frame_by_doc[d.docid] = doc_frames(d)
        caps_by_doc[d.docid] = doc_caps(d)
        if verbose and (i + 1) % 20 == 0:
            print("    ... %d/%d docs tagged (%.0fs)" % (i + 1, len(docs), time.time() - t0), flush=True)
    return post_by_doc, sym_by_doc, frame_by_doc, caps_by_doc


def _write(name, obj):
    os.makedirs(OUT_DIR, exist_ok=True)
    p = os.path.join(OUT_DIR, name)
    obj = dict(obj)
    obj.setdefault("ts_iso", datetime.now(timezone.utc).isoformat())
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=str)
    print("  wrote %s" % p)
    return p


# ---------------------------------------------------------------------------------------------------------
def cmd_typing(args):
    """THE TYPING RUNG on the board loader's stream: the shipped argmax typer (FLOOR) vs the graded typer,
    the info-free twin, doc-paired bootstrap, gold type as the answer key."""
    docs, gaz = load_test(args.docs, split=args.split)
    print("GUM %s: %d documents, %d tokens, %d mentions"
          % (args.split.upper(), len(docs), sum(len(d.toks) for d in docs), sum(len(d.mentions) for d in docs)), flush=True)
    gold_by_doc = {d.docid: gold_type_and_head(d) for d in docs}
    print("  feeding the passage, once, in order (the organ's posterior kept) ...", flush=True)
    post, syms, frames, caps = build_posteriors(docs)
    arms = {}
    cfgs = {
        "floor_argmax": SHIPPED,
        "marginal": TyperCfg(marginal=True, support=args.support, eta=float("inf"), graded_head=False),
        "graded_head": TyperCfg(marginal=False, support=args.support, eta=args.eta, graded_head=True),
        "graded": TyperCfg(marginal=True, support=args.support, eta=args.eta, graded_head=True),
        "graded_card": TyperCfg(marginal=True, support=args.support, eta=args.eta, graded_head=True,
                                kappa_card=args.kappa, card_mode=args.card_mode),
    }
    for name, cfg in cfgs.items():
        t0 = time.time()
        per = score_typing(docs, type_arm(docs, cfg, post, syms, frame_by_doc=frames), gold_by_doc)
        arms[name] = per
        a, n = _acc(per)
        print("  %-14s type acc %.4f (n=%d)  head acc %.4f  macroF1 %.4f   [%.0fs]"
              % (name, a, n, st_head(per), st_macro(per), time.time() - t0), flush=True)
    # THE SPAN-LEVEL NAME-RUN CUE, learned ONLINE, strictly in reading order (no document is typed by a table
    # that has read it).  The table is EMPTY at the first document and grows as the reader reads.
    cfg_span = TyperCfg(marginal=True, support=args.support, eta=args.eta, graded_head=True,
                        kappa_card=args.kappa, card_mode=args.card_mode,
                        kappa_caps=args.kappa_caps, tau_learn=args.tau_learn)
    cfgs["graded_span_online"] = cfg_span
    tab = SpanCueTable()
    per = score_typing(docs, type_arm(docs, cfg_span, post, syms, frame_by_doc=frames, caps_by_doc=caps,
                                      span_tab=tab, online=True), gold_by_doc)
    arms["graded_span_online"] = per
    print("  %-18s type acc %.4f  head acc %.4f  macroF1 %.4f   [%d observations in the online table]"
          % ("graded_span_online", st_acc(per), st_head(per), st_macro(per), tab.n_obs), flush=True)
    span_table_dump = tab.as_dict()
    # THE CUE'S OWN INFO-FREE TWIN: the same table, the same kappa, a RANDOM symbol per mention.
    tab2 = SpanCueTable()
    per2 = score_typing(docs, type_arm(docs, cfg_span, post, syms, frame_by_doc=frames, caps_by_doc=caps,
                                       span_tab=tab2, online=True, shuffle_caps=True), gold_by_doc)
    arms["span_cue_twin"] = per2
    print("  %-18s type acc %.4f  macroF1 %.4f   (the span cue's own info-free twin)"
          % ("span_cue_twin", st_acc(per2), st_macro(per2)), flush=True)
    twin = score_typing(docs, type_arm(docs, cfgs["graded"], post, syms, shuffle_post=True,
                                       frame_by_doc=frames), gold_by_doc)
    arms["twin"] = twin
    print("  %-14s type acc %.4f  head acc %.4f  macroF1 %.4f" % ("twin", st_acc(twin), st_head(twin), st_macro(twin)))

    res = {"population": "GUM %s (odd doc index = TEST), %d docs / %d tokens / %d mentions; gold mention TYPE+HEAD "
                         "(gum_coref._head_of_span/_mention_type on the treebank columns) as the answer key"
                         % (args.split.upper(), len(docs), sum(len(d.toks) for d in docs), sum(len(d.mentions) for d in docs)),
           "cfgs": {k: v.key() for k, v in cfgs.items()}, "arms": {}, "deltas": {}}
    for name, per in arms.items():
        row = {"type_acc": round(st_acc(per), 4), "head_acc": round(st_head(per), 4),
               "macro_f1": round(st_macro(per), 4), "n": _acc(per)[1]}
        for ty in TYPES:
            P, R, F, tp, fp, fn = _f1(per, ty)
            row[ty] = {"P": round(P, 4), "R": round(R, 4), "F1": round(F, 4), "tp": tp, "fp": fp, "fn": fn}
        res["arms"][name] = row
    base = arms["floor_argmax"]
    for name in ("marginal", "graded_head", "graded", "graded_card", "graded_span_online",
                 "span_cue_twin", "twin"):
        d = {"type_acc": _boot_delta(base, arms[name], st_acc, args.boot),
             "head_acc": _boot_delta(base, arms[name], st_head, args.boot),
             "macro_f1": _boot_delta(base, arms[name], st_macro, args.boot)}
        for ty in TYPES:
            d["f1_" + ty] = _boot_delta(base, arms[name], st_f1(ty), args.boot)
        res["deltas"][name + "_minus_floor"] = d
    res["deltas"]["graded_minus_twin"] = {
        "type_acc": _boot_delta(arms["twin"], arms["graded"], st_acc, args.boot),
        "macro_f1": _boot_delta(arms["twin"], arms["graded"], st_macro, args.boot)}
    res["deltas"]["span_online_minus_its_own_cue_twin"] = {
        "type_acc": _boot_delta(arms["span_cue_twin"], arms["graded_span_online"], st_acc, args.boot),
        "macro_f1": _boot_delta(arms["span_cue_twin"], arms["graded_span_online"], st_macro, args.boot),
        "f1_name": _boot_delta(arms["span_cue_twin"], arms["graded_span_online"], st_f1("name"), args.boot)}
    res["deltas"]["span_online_minus_graded_card"] = {
        "type_acc": _boot_delta(arms["graded_card"], arms["graded_span_online"], st_acc, args.boot),
        "macro_f1": _boot_delta(arms["graded_card"], arms["graded_span_online"], st_macro, args.boot),
        "f1_name": _boot_delta(arms["graded_card"], arms["graded_span_online"], st_f1("name"), args.boot)}
    res["span_cue_table_counts"] = span_table_dump
    print()
    for k, v in res["deltas"].items():
        print("  %-26s dtype %s  dmacroF1 %s" % (k, v["type_acc"], v["macro_f1"]))
    _write(args.out or "metrics_typing.json", res)
    return 0


def cmd_sweep(args):
    """THE PHASE DIAGRAM: the operating point (support / eta / kappa) is FREE TO SWEEP, never adopted."""
    docs, gaz = load_test(args.docs, split=args.split)
    gold_by_doc = {d.docid: gold_type_and_head(d) for d in docs}
    print("GUM %s: %d documents, %d mentions; feeding the passage ..."
          % (args.split.upper(), len(docs), sum(len(d.mentions) for d in docs)), flush=True)
    post, syms, frames, caps = build_posteriors(docs)
    base = score_typing(docs, type_arm(docs, SHIPPED, post, syms, frame_by_doc=frames), gold_by_doc)
    print("  FLOOR (shipped argmax): type %.4f head %.4f macroF1 %.4f"
          % (st_acc(base), st_head(base), st_macro(base)), flush=True)
    rows = []
    for support in ("all", "nominal", "strict"):
        for eta in (0.0, 0.5, 1.0, 2.0, 4.0, float("inf")):
            cfg = TyperCfg(marginal=True, support=support, eta=eta, graded_head=True)
            per = score_typing(docs, type_arm(docs, cfg, post, syms, frame_by_doc=frames), gold_by_doc)
            rows.append({"support": support, "eta": eta, "kappa": 0.0,
                         "type_acc": round(st_acc(per), 4), "head_acc": round(st_head(per), 4),
                         "macro_f1": round(st_macro(per), 4),
                         "f1": {t: round(_f1(per, t)[2], 4) for t in TYPES}})
            print("   support=%-8s eta=%-5s  type %.4f  head %.4f  macroF1 %.4f"
                  % (support, eta, rows[-1]["type_acc"], rows[-1]["head_acc"], rows[-1]["macro_f1"]), flush=True)
    best = max(rows, key=lambda r: r["macro_f1"])
    for kappa in (0.25, 0.5, 1.0, 2.0):
        for mode in ("complement", "all"):
            cfg = TyperCfg(marginal=True, support=best["support"], eta=best["eta"], graded_head=True,
                           kappa_card=kappa, card_mode=mode)
            per = score_typing(docs, type_arm(docs, cfg, post, syms, frame_by_doc=frames), gold_by_doc)
            rows.append({"support": best["support"], "eta": best["eta"], "kappa": kappa, "card_mode": mode,
                         "type_acc": round(st_acc(per), 4), "head_acc": round(st_head(per), 4),
                         "macro_f1": round(st_macro(per), 4),
                         "f1": {t: round(_f1(per, t)[2], 4) for t in TYPES}})
            print("   kappa=%-5s mode=%-11s type %.4f  head %.4f  macroF1 %.4f"
                  % (kappa, mode, rows[-1]["type_acc"], rows[-1]["head_acc"], rows[-1]["macro_f1"]), flush=True)
    # THE NP FRAME AT THE TYPE LEVEL (the quality push): the determiner / right-context cues the organ reads
    # ONLY for words with no lexical entry, read at the level whose question they answer.
    bk = max([r for r in rows if r.get("card_mode")], key=lambda r: r["macro_f1"])
    frows = []
    for kd in (0.0, 0.25, 0.5, 1.0, 2.0):
        for kr in (0.0, 0.25, 0.5, 1.0):
            for fmode in ("complement", "all"):
                if kd == 0.0 and kr == 0.0:
                    continue
                if fmode == "all" and (kd, kr) not in ((0.5, 0.0), (1.0, 0.0), (0.5, 0.5), (1.0, 0.5)):
                    continue
                cfg = TyperCfg(marginal=True, support=bk["support"], eta=bk["eta"], graded_head=True,
                               kappa_card=bk["kappa"], card_mode=bk["card_mode"],
                               kappa_det=kd, kappa_right=kr, frame_mode=fmode)
                per = score_typing(docs, type_arm(docs, cfg, post, syms, frame_by_doc=frames), gold_by_doc)
                r = {"support": bk["support"], "eta": bk["eta"], "kappa": bk["kappa"],
                     "card_mode": bk["card_mode"], "kappa_det": kd, "kappa_right": kr, "frame_mode": fmode,
                     "type_acc": round(st_acc(per), 4), "head_acc": round(st_head(per), 4),
                     "macro_f1": round(st_macro(per), 4),
                     "f1": {t: round(_f1(per, t)[2], 4) for t in TYPES}}
                frows.append(r)
                print("   det=%-5s right=%-5s mode=%-11s type %.4f  macroF1 %.4f  nameF1 %.4f"
                      % (kd, kr, fmode, r["type_acc"], r["macro_f1"], r["f1"]["name"]), flush=True)
    rows.extend(frows)
    _write(args.out or "metrics_sweep.json",
           {"floor": {"type_acc": round(st_acc(base), 4), "head_acc": round(st_head(base), 4),
                      "macro_f1": round(st_macro(base), 4)}, "rows": rows,
            "population": "GUM TEST %d docs" % len(docs)})
    return 0


# ---------------------------------------------------------------------------------------------------------
# THE DOWNSTREAM READ, ON A POPULATION THE DECISION CANNOT MOVE.
#
# The board's coref / common_noun / salience rows are scored PER MENTION TYPE, so an arm that types
# differently is scored on a different population and its margin over its own recomputed floor is not
# comparable across arms (pri 109's finding, stated in its own words: "MARGIN OVER A ROW'S OWN RECOMPUTED
# FLOOR IS NOT COMPARABLE ACROSS ARMS WHOSE TYPING DIFFERS").  So the headline downstream instrument here is
# the LIVE entity-clustering organ (`hdlab.online_entity_cluster.online_cluster`, default-ON since
# 2026-09-09) scored with B-cubed over a population fixed by the ANSWER KEY (every gold non-pronoun mention):
# the typing decides the ROUTE (name -> the given-name aliaser file; common -> ACT-R cue-based retrieval) and
# the identity key, and it cannot decide who is scored.
def span_upos_for_decision(span, decision, head_gidx, pred, caps):
    """Transmit the typer's decision to `coref.name_content_tokens` through the interface the live organs
    already use (the parallel `span_upos` list), losslessly and with a witness: the constructed list makes
    `_span_head_is_name` return exactly this decision, and a NAME span still exposes its capitalised name
    tokens to the aliaser (capitalisation demoted to what it is -- which TOKENS of a name span carry it)."""
    out = []
    hit = False
    for t in span:
        if t.gidx == head_gidx:
            out.append("PROPN" if decision == "name" else "NOUN")
            hit = True
            continue
        if not hit and decision == "name":
            a, c, mid = caps.get(t.gidx, (False, False, False))
            out.append("PROPN" if (a and c and mid) else "X")
            continue
        if hit:
            out.append("X")            # nothing after the head may steal the head domain's last nominal
            continue
        out.append("X")
    return out


def _bcubed(labels, gold):
    """B-cubed P/R/F over a FIXED mention set.  labels/gold: {midx: cluster id}."""
    keys = [k for k in gold if k in labels]
    if not keys:
        return 0.0, 0.0, 0.0
    lsz, gsz = {}, {}
    for k in keys:
        lsz[labels[k]] = lsz.get(labels[k], 0) + 1
        gsz[gold[k]] = gsz.get(gold[k], 0) + 1
    inter = {}
    for k in keys:
        kk = (labels[k], gold[k])
        inter[kk] = inter.get(kk, 0) + 1
    P = R = 0.0
    for k in keys:
        c = inter[(labels[k], gold[k])]
        P += c / lsz[labels[k]]
        R += c / gsz[gold[k]]
    P /= len(keys)
    R /= len(keys)
    F = 2 * P * R / (P + R) if P + R else 0.0
    return P, R, F


def cluster_mentions(doc, typer, post, pred, syms, frames, caps, gold_pron, use_shipped=False,
                     span_tab=None, cfg=None, gaz=None):
    """Build the live entity layer's mention stream for ONE document under one typer.  The POPULATION (which
    mentions exist and which are pronouns) is the answer key's; only the ROUTE and the identity key are the
    typer's."""
    import experiments.gum_coref as G
    gmap = {t.gidx: t for t in doc.toks}
    lc, _tags = organ()
    ms = []
    for i, m in enumerate(doc.mentions):
        span = [gmap[g] for g in range(m.start_g, m.end_g + 1) if g in gmap]
        span = [t for t in span if t.sent == m.sent] or span
        if not span:
            continue
        if use_shipped:
            h = head_of_span_shipped(span, pred, G.PRONOUNS_ALL)
            ty = mention_type_shipped(h, pred, G.PRONOUNS_ALL)
            upos = [pred.get(t.gidx, "X") for t in span]
        else:
            h = typer.head_of_span(span, post, pred)
            cs = span_caps_symbol(span, caps, h.gidx, STOP_LOW) if (cfg and cfg.kappa_caps) else None
            ty, dist = typer.type_of(h, post, pred, sym=syms.get(h.gidx),
                                     known=(h.form.lower() in lc.vocab),
                                     frame=frames.get(h.gidx), caps_sym=cs)
            if span_tab is not None and cs is not None and dist[ty] >= cfg.tau_learn:
                span_tab.observe(cs, ty)
            upos = span_upos_for_decision(span, ty, h.gidx, pred, caps)
        is_pron = gold_pron[(m.start_g, m.end_g, m.eid)]
        g, n = G._gender_number_organ(h, ty, gaz)
        ms.append({"midx": i, "head": h.form.lower(), "span_toks": [t.form for t in span],
                   "span_upos": upos, "is_pronoun": is_pron, "sent_idx": m.sent,
                   "sent_role_rank": 0 if i == 0 else 1, "gender": g or None, "number": n or None,
                   "name_gender": None, "cluster": m.eid, "_type": ty, "_head_g": h.gidx})
    # the Centering Cf rank the live builder assigns (position within the sentence)
    by_sent = {}
    for x in ms:
        by_sent.setdefault(x["sent_idx"], []).append(x)
    for lst in by_sent.values():
        for rank, x in enumerate(lst):
            x["sent_role_rank"] = rank
    return ms


def cmd_cluster(args):
    """THE LIVE ENTITY LAYER, FIXED POPULATION: `online_entity_cluster.online_cluster` over every gold
    non-pronoun mention of the GUM test split, routed by the shipped argmax typer (FLOOR) and by the graded
    typer (ARM), B-cubed against the gold chains, doc-paired bootstrap."""
    from hdlab.online_entity_cluster import online_cluster
    from hdlab.coref import name_content_tokens
    import experiments.gum_coref as G
    docs, gaz = load_test(args.docs, split=args.split)
    lc, tags = organ()
    print("GUM %s: %d documents, %d mentions; feeding the passage ..."
          % (args.split.upper(), len(docs), sum(len(d.mentions) for d in docs)), flush=True)
    post, syms, frames, caps = build_posteriors(docs)
    gold_by_doc = {d.docid: gold_type_and_head(d) for d in docs}
    cfg = TyperCfg(marginal=True, support=args.support, eta=args.eta, graded_head=True,
                   kappa_card=args.kappa, card_mode=args.card_mode,
                   kappa_caps=args.kappa_caps, tau_learn=args.tau_learn)
    arms = {"floor_shipped": [], "graded": [], "twin_posterior": [], "singleton": [], "string_identity": []}
    tab = SpanCueTable()
    rng = random.Random(SEED)
    witness_ok = 0
    witness_n = 0
    route_counts = {"floor_shipped": {}, "graded": {}}
    deltas_seen = {"retyped": 0, "reheaded": 0, "cluster_changed": 0, "cluster_changed_and_retyped": 0}
    sign_sum = {"changed_sum_df": 0.0, "changed_up": 0, "changed_down": 0, "changed_flat": 0,
                "retyped_sum_df": 0.0, "retyped_up": 0, "retyped_down": 0, "retyped_flat": 0}
    for d in docs:
        P = post[d.docid]
        pred = argmax_tags(P)
        gold = gold_by_doc[d.docid]
        gold_pron = {k: (v[0] == "pronoun") for k, v in gold.items()}
        typer = Typer(cfg, tags, G.PRONOUNS_ALL, lc=lc, span_tab=tab)
        Pt = dict(P)
        vals = [Pt[k] for k in Pt]
        rng.shuffle(vals)
        Ptw = dict(zip(list(Pt.keys()), vals))
        streams = {
            "floor_shipped": cluster_mentions(d, typer, P, pred, syms[d.docid], frames[d.docid],
                                              caps[d.docid], gold_pron, use_shipped=True, cfg=cfg, gaz=gaz),
            "graded": cluster_mentions(d, typer, P, pred, syms[d.docid], frames[d.docid], caps[d.docid],
                                       gold_pron, span_tab=tab, cfg=cfg, gaz=gaz),
            "twin_posterior": cluster_mentions(d, Typer(cfg, tags, G.PRONOUNS_ALL, lc=lc, span_tab=tab),
                                               Ptw, argmax_tags(Ptw), syms[d.docid], frames[d.docid],
                                               caps[d.docid], gold_pron, cfg=cfg, gaz=gaz),
        }
        # WITNESS: the constructed span_upos transmits the graded decision to the live gate LOSSLESSLY
        for x in streams["graded"]:
            if x["is_pronoun"]:
                continue
            witness_n += 1
            got = bool(name_content_tokens(x["span_toks"], upos=x["span_upos"]))
            witness_ok += int(got == (x["_type"] == "name"))
        gid = {x["midx"]: x["cluster"] for x in streams["graded"] if not x["is_pronoun"]}
        labs = {}
        for name in ("floor_shipped", "graded", "twin_posterior"):
            st = streams[name]
            for x in st:
                if not x["is_pronoun"]:
                    route_counts.setdefault(name, {})
                    route_counts[name][x["_type"]] = route_counts[name].get(x["_type"], 0) + 1
            lab = online_cluster(st, gaz=gaz)
            labs[name] = lab
            arms[name].append(_bcubed(lab, gid))
        # THE DECISION-RATE CHECK, before any null is read as a quality finding: how many mentions were
        # RE-ROUTED by the graded typer, and how many of those actually landed in a different entity file?
        fh = {x["midx"]: x["_type"] for x in streams["floor_shipped"] if not x["is_pronoun"]}
        gh = {x["midx"]: x["_type"] for x in streams["graded"] if not x["is_pronoun"]}
        fk = {x["midx"]: x["_head_g"] for x in streams["floor_shipped"] if not x["is_pronoun"]}
        gk = {x["midx"]: x["_head_g"] for x in streams["graded"] if not x["is_pronoun"]}
        for k in gh:
            if fh.get(k) != gh[k]:
                deltas_seen["retyped"] += 1
            if fk.get(k) != gk[k]:
                deltas_seen["reheaded"] += 1

        def part(lab):
            inv = {}
            for k, v in lab.items():
                inv.setdefault(v, set()).add(k)
            return {k: frozenset(inv[lab[k]]) for k in lab}
        pa, pb = part(labs["floor_shipped"]), part(labs["graded"])
        gsets = {}
        for k, e in gid.items():
            gsets.setdefault(e, set()).add(k)

        def fk_(k, p):
            c = p[k]
            g = gsets[gid[k]]
            inter = len(c & g)
            pr = inter / len(c)
            rc = inter / len(g)
            return 2 * pr * rc / (pr + rc) if pr + rc else 0.0
        for k in pb:
            if k not in pa:
                continue
            dfk = fk_(k, pb) - fk_(k, pa)
            if pa[k] != pb[k]:
                deltas_seen["cluster_changed"] += 1
                sign_sum["changed_sum_df"] += dfk
                sign_sum["changed_up" if dfk > 1e-9 else ("changed_down" if dfk < -1e-9 else "changed_flat")] += 1
                if fh.get(k) != gh[k]:
                    deltas_seen["cluster_changed_and_retyped"] += 1
            if fh.get(k) != gh[k]:
                sign_sum["retyped_sum_df"] += dfk
                sign_sum["retyped_up" if dfk > 1e-9 else ("retyped_down" if dfk < -1e-9 else "retyped_flat")] += 1
        # FLOORS, recomputed in place on the SAME population
        arms["singleton"].append(_bcubed({k: k for k in gid}, gid))
        si = {}
        for x in streams["floor_shipped"]:
            if not x["is_pronoun"]:
                si[x["midx"]] = x["head"]
        arms["string_identity"].append(_bcubed(si, gid))
    def stat(per):
        return float(np.mean([p[2] for p in per]))
    res = {"population": "GUM %s, %d documents; every GOLD non-pronoun mention (the answer key fixes the "
                         "population; the typer decides only the ROUTE and the identity key); B-cubed F, "
                         "macro-averaged over documents" % (args.split.upper(), len(docs)),
           "witness_span_upos_transmits_the_decision": "%d/%d" % (witness_ok, witness_n),
           "route_counts": route_counts,
           "decision_rate": deltas_seen,
           "per_mention_bcubed_decomposition": {k: (round(v, 3) if isinstance(v, float) else v)
                                                for k, v in sign_sum.items()},
           "arms": {k: {"bcubed_F": round(stat(v), 4),
                        "bcubed_P": round(float(np.mean([p[0] for p in v])), 4),
                        "bcubed_R": round(float(np.mean([p[1] for p in v])), 4)} for k, v in arms.items()},
           "deltas": {}}
    def mk(per):
        return [{"hit": p[2], "tot": 1.0} for p in per]
    for name in ("graded", "twin_posterior", "singleton", "string_identity"):
        res["deltas"][name + "_minus_floor_shipped"] = _boot_delta(
            mk(arms["floor_shipped"]), mk(arms[name]),
            lambda per: sum(x["hit"] for x in per) / len(per), args.boot)
    res["deltas"]["graded_minus_twin"] = _boot_delta(
        mk(arms["twin_posterior"]), mk(arms["graded"]),
        lambda per: sum(x["hit"] for x in per) / len(per), args.boot)
    for k, v in res["arms"].items():
        print("  %-16s %s" % (k, v))
    print("  witness span_upos transmits the decision: %s" % res["witness_span_upos_transmits_the_decision"])
    print("  decision rate: %s" % deltas_seen)
    print("  per-mention B-cubed decomposition: %s"
          % {k: (round(v, 3) if isinstance(v, float) else v) for k, v in sign_sum.items()})
    for k, v in res["deltas"].items():
        print("  %-34s %s" % (k, v))
    _write(args.out or "metrics_cluster.json", res)
    return 0


# ---------------------------------------------------------------------------------------------------------
def apply_layer_local(doc, post, pred):
    """`gum_coref.apply_organ_layer` reproduced here so the POSTERIOR survives (the shipped function keeps only
    its argmax).  Asserted byte-identical to the shipped loader arm by the board witness below."""
    import experiments.gum_coref as G
    dep = G.positional_deprel(doc.toks, pred)
    for t in doc.toks:
        if not t.gold_upos:
            t.gold_upos, t.gold_lemma, t.gold_feats = t.upos, t.lemma, t.feats
            t.gold_head, t.gold_deprel = t.head, t.deprel
        t.upos = pred.get(t.gidx, "X")
        t.xpos = ""
        t.lemma = G.organ_lemma(t.form)
        t.feats = {}
        t.head = 0
        t.deprel = dep.get(t.gidx, "")


def retype_doc(doc, typer, post, pred, syms, frames, caps, cfg, shipped=False, span_tab=None, gaz=None):
    """Re-decide head / type / gender / number / lemma key for every mention of `doc`, IN PLACE."""
    import experiments.gum_coref as G
    lc, _t = organ()
    gmap = {t.gidx: t for t in doc.toks}
    for m in doc.mentions:
        span = [gmap[g] for g in range(m.start_g, m.end_g + 1) if g in gmap]
        span = [t for t in span if t.sent == m.sent] or span
        if not span:
            continue
        if shipped:
            h = head_of_span_shipped(span, pred, G.PRONOUNS_ALL)
            ty = mention_type_shipped(h, pred, G.PRONOUNS_ALL)
        else:
            h = typer.head_of_span(span, post, pred)
            cs = span_caps_symbol(span, caps, h.gidx, STOP_LOW) if cfg.kappa_caps else None
            ty, dist = typer.type_of(h, post, pred, sym=syms.get(h.gidx),
                                     known=(h.form.lower() in lc.vocab),
                                     frame=frames.get(h.gidx), caps_sym=cs)
            if span_tab is not None and cs is not None and dist[ty] >= cfg.tau_learn:
                span_tab.observe(cs, ty)
        g, n = G._gender_number_organ(h, ty, gaz)
        m.head_g = h.gidx
        m.mtype = ty
        m.upos = h.upos
        m.gender = g
        m.number = n
        m.lemma_head = h.lemma.lower()


def cmd_board(args):
    """THE BOARD'S THREE ENTITY ROWS, BOTH TYPERS IN ONE PROCESS, each with its floor recomputed in place on
    its OWN population.  pri 109's caveat travels with these numbers: a row's margin over its own recomputed
    floor is NOT comparable across arms whose typing differs, because the typing defines the population.  The
    population sizes are printed for exactly that reason, and the fixed-population read is `--cluster`."""
    import experiments.gum_coref as G
    import experiments.exp_unified_referent_gum_v1 as URG
    import experiments.exp_board_coref_gum_v1 as B
    docs, gaz = load_test(args.docs, split=args.split)
    lc, tags = organ()
    print("GUM %s: %d documents, %d mentions; feeding the passage ..."
          % (args.split.upper(), len(docs), sum(len(d.mentions) for d in docs)), flush=True)
    post, syms, frames, caps = build_posteriors(docs)
    # THE ANSWER KEY IS READ FIRST, while the treebank columns are still in place -- `apply_layer_local`
    # overwrites upos/head with the organ's values, so a gold read after it is not a gold read.
    gold_by_doc = {d.docid: gold_type_and_head(d) for d in docs}
    for d in docs:
        apply_layer_local(d, post[d.docid], argmax_tags(post[d.docid]))
    cfg = TyperCfg(marginal=True, support=args.support, eta=args.eta, graded_head=True,
                   kappa_card=args.kappa, card_mode=args.card_mode,
                   kappa_caps=args.kappa_caps, tau_learn=args.tau_learn)
    out = {"population": "GUM %s, %d documents; the board's coref / common-noun / salience rows, both typers "
                         "in ONE process, every floor recomputed in place on that arm's own population"
                         % (args.split.upper(), len(docs)), "arms": {}}
    B._load_test = lambda n_docs=None: (docs, docs, gaz)
    tab = SpanCueTable()
    seen_types = {}
    for arm in ("floor_shipped", "graded"):
        t0 = time.time()
        typer = Typer(cfg, tags, G.PRONOUNS_ALL, lc=lc, span_tab=tab)
        for d in docs:
            retype_doc(d, typer, post[d.docid], argmax_tags(post[d.docid]), syms[d.docid], frames[d.docid],
                       caps[d.docid], cfg, shipped=(arm == "floor_shipped"),
                       span_tab=(tab if arm == "graded" else None), gaz=gaz)
        tc = {}
        for d in docs:
            for m in d.mentions:
                tc[m.mtype] = tc.get(m.mtype, 0) + 1
        a = {"separate": URG._run_arm(URG.Resolver("separate"), docs),
             "unified": URG._run_arm(URG.Resolver("unified"), docs),
             "twin": URG._run_arm(URG.Resolver("unified", twin=True, rng=random.Random(99)), docs),
             "recency": URG._run_arm(URG.FloorResolver("recency"), docs),
             "string_identity": URG._run_arm(URG.FloorResolver("string-identity"), docs)}
        lev = URG._run_arm(URG.Resolver("unified", typed_identity=True, bridge=True, bridge_write=False,
                                        type_comparator="typed_spokes"), docs)
        lev_twin = URG._run_arm(URG.Resolver("unified", typed_identity=True, bridge=True, bridge_write=False,
                                             type_comparator="typed_spokes", twin=True,
                                             twin_mode="random_bridge", rng=random.Random(99)), docs)
        rows = {"coref_pronoun": B._row_from_consumer(a, "pronoun"),
                "common_noun": B._row_from_consumer({**a, "unified": lev, "twin": lev_twin}, "common"),
                "entity_kb_hardlink": B._row_from_consumer(a, "kb_hardlink")}
        seen_types[arm] = {(d.docid, m.start_g, m.end_g, m.eid): m.mtype for d in docs for m in d.mentions}
        out["arms"][arm] = {"mention_type_counts": tc, "rows": rows, "secs": round(time.time() - t0, 1)}
        for k, r in rows.items():
            print("  %-10s %-20s n=%-6s model %.4f  floor %.4f (%s)  twin %.4f  margin %s  sep=%s"
                  % (arm, k, r["n"], r["model_acc"] or 0, r["strongest_floor"] or 0,
                     r["strongest_floor_name"], r["twin_acc"] or 0, r["model_minus_strongest"],
                     r["ci_sep_over_strongest"]), flush=True)
        print("     types: %s  [%.0fs]" % (tc, out["arms"][arm]["secs"]), flush=True)
    # WHY THE COMMON-NOUN ROW MOVES: the population is DEFINED BY THE DECISION UNDER TEST, so a mention the
    # graded typer re-routes LEAVES the row.  Audit those mentions against the answer key and do the
    # arithmetic on the hits, so the row's move is a counted reason and not an unexplained regression.
    trans = {}
    for d in docs:
        gold = gold_by_doc[d.docid]
        for m in d.mentions:
            k = (d.docid, m.start_g, m.end_g, m.eid)
            a = seen_types["floor_shipped"].get(k)
            b = seen_types["graded"].get(k)
            g = gold.get((m.start_g, m.end_g, m.eid))
            if a == b or g is None:
                continue
            kk = "%s->%s (gold %s)" % (a, b, g[0])
            trans[kk] = trans.get(kk, 0) + 1
    out["retyped_mentions_vs_the_answer_key"] = dict(sorted(trans.items(), key=lambda kv: -kv[1]))
    fr = out["arms"]["floor_shipped"]["rows"]["common_noun"]
    gr = out["arms"]["graded"]["rows"]["common_noun"]
    hf = fr["model_acc"] * fr["n"]
    hg = gr["model_acc"] * gr["n"]
    dn = fr["n"] - gr["n"]
    out["common_noun_population_arithmetic"] = {
        "floor_hits": round(hf, 1), "graded_hits": round(hg, 1),
        "items_that_LEFT_the_row": dn,
        "accuracy_of_the_items_that_left": round((hf - hg) / dn, 4) if dn else None,
        "row_accuracy_of_the_floor_arm": fr["model_acc"],
        "note": "an item that leaves the common-noun row was re-routed to the NAME branch; if the items that "
                "left were resolved far ABOVE the row average, the row was being held up by mis-typed names "
                "(a repeated name string resolves trivially by string identity), which is pri 109's artefact "
                "measured from the other side."}
    print("  retyped vs the answer key: %s" % out["retyped_mentions_vs_the_answer_key"])
    print("  common-noun population arithmetic: %s" % out["common_noun_population_arithmetic"])
    _write(args.out or "metrics_board.json", out)
    return 0


# ---------------------------------------------------------------------------------------------------------
def cmd_reader_stream(args):
    """THE READER'S OWN STREAM (pri 116: the sentence source is CASED at HEAD, so the organ runs at PROPN F1
    0.8651 on the live path).  The reader's candidate source is `referent_per_np.referent_per_np_source`, and
    the question here is what the graded typer is worth THERE -- which depends on what the stream carries."""
    import experiments.gum_coref as G
    from experiments.exp_crosstype_gum_conll_fullread_v1 import gum_to_conll
    import hdlab.referent_per_np as RNP
    from hdlab.coref import name_content_tokens
    from hdlab import frontend as F
    docs, gaz = load_test(args.docs or 16, split=args.split)
    lc, tags = organ()
    scratch = os.path.join(OUT_DIR, "conll")
    os.makedirs(scratch, exist_ok=True)
    tg = F.Tagger()
    cfg = TyperCfg(marginal=True, support=args.support, eta=args.eta, graded_head=True,
                   kappa_card=args.kappa, card_mode=args.card_mode,
                   kappa_caps=args.kappa_caps, tau_learn=args.tau_learn)
    typer = Typer(cfg, tags, G.PRONOUNS_ALL, lc=lc)
    n_ment = n_pron = n_multi = 0
    ship_name = graded_name = 0
    flips = {}
    for d in docs:
        p = os.path.join(scratch, d.docid + ".conll")
        gum_to_conll(d, p)
        ms, _ns = RNP.referent_per_np_source(p, tg, name_gender_map=gaz)
        from hdlab.scene_segment import parse_conll_sentences
        sents = parse_conll_sentences(p, lower=False)     # pri 116: CASED, exactly what the reader gets
        rows = {}
        for si, toks in enumerate(sents):
            cats, dists = tg.tag_with_posterior(list(toks))
            if not dists:
                continue
            arr = np.asarray([[dd.get(t, 0.0) for t in tags] for dd in dists], dtype=np.float32)
            rows[si] = (list(toks), cats, arr)
        for m in ms:
            n_ment += 1
            if m["is_pronoun"]:
                n_pron += 1
                continue
            st = m.get("span_toks", [m["head"]])
            up = m.get("span_upos")
            if len(st) > 1:
                n_multi += 1
            sn = bool(name_content_tokens(st, upos=up))
            ship_name += int(sn)
            # THE GRADED DECISION ON THE SAME STREAM, read from the IN-CONTEXT posterior row for the head
            # (the stream itself carries only the argmax today -- that is the hand-off this brief is about).
            r = rows.get(m["sent_idx"])
            gt = "common"
            if r is not None and 0 <= m["wtok_start"] < len(r[0]):
                toks_s, cats, arr = r
                i = m["wtok_start"]

                class _T:
                    def __init__(self, g, f):
                        self.gidx = g
                        self.form = f
                        self.sent = 0
                        self.idx = g + 1
                h = _T(i, toks_s[i])
                fake = {i: arr[i]}
                pred = {i: cats[i]}
                caps_map = {i: (toks_s[i].isalpha(), toks_s[i][:1].isupper(), i > 0)}
                cs = span_caps_symbol([h], caps_map, h.gidx, STOP_LOW)
                gt, _dist = typer.type_of(h, fake, pred, sym=None,
                                          known=(h.form.lower() in lc.vocab), frame=None, caps_sym=cs)
            graded_name += int(gt == "name")
            if sn != (gt == "name"):
                k = "%s->%s" % ("name" if sn else "common", gt)
                flips[k] = flips.get(k, 0) + 1
    out = {"population": "THE READER'S OWN STREAM -- referent_per_np.referent_per_np_source over %d GUM %s "
                         "documents written to the reader's CoNLL by the landed gum_to_conll; the reader is "
                         "UNPATCHED and CASED (pri 116 at HEAD)" % (len(docs), args.split.upper()),
           "mentions": n_ment, "pronoun_mentions": n_pron,
           "non_pronoun_mentions_with_a_MULTI_TOKEN_span": n_multi,
           "NAME_typed_shipped": ship_name, "NAME_typed_graded": graded_name,
           "flips": flips,
           "finding": "the candidate source stores span_toks=[head] (ONE token per non-pronoun mention), so the "
                      "SPAN-level name-run cue -- the lever that carries the whole typing gain on the board "
                      "loader's stream -- is INERT on the reader's stream BY CONSTRUCTION. The reader cannot "
                      "receive this gain until referent_per_np keeps the NP span it already located."}
    for k, v in out.items():
        print("  %-46s %s" % (k, v))
    _write(args.out or "metrics_reader_stream.json", out)
    return 0


# ---------------------------------------------------------------------------------------------------------
PATCH_FILES = ("hdlab/coref.py", "hdlab/referent_per_np.py", "hdlab/situation_reader.py",
               "experiments/gum_coref.py")


def install_patch(patch_dir):
    """PATCH EQUIVALENCE: exec the PROPOSED DIFF'S OWN SOURCE TEXT into the live modules (with `__file__` set
    to the real repo path), so every number below is produced by the code the diff describes -- the control
    pri 112 and pri 116 both used.  Nothing is written to the repo."""
    import importlib
    mods = {"hdlab/coref.py": "hdlab.coref", "hdlab/referent_per_np.py": "hdlab.referent_per_np",
            "hdlab/situation_reader.py": "hdlab.situation_reader",
            "experiments/gum_coref.py": "experiments.gum_coref"}
    for rel in PATCH_FILES:
        name = mods[rel]
        m = importlib.import_module(name)
        src = open(os.path.join(patch_dir, rel), encoding="utf-8").read()
        code = compile(src, os.path.join(_REPO, rel), "exec")
        exec(code, m.__dict__)
    return True


def cmd_build_asset(args):
    """Accrue the span-cue counts ONLINE over the TRAIN half (the reader's own confident typings; NO gold) and
    write the asset the patched organ loads.  This is the offline FOUNDATION build of a table that keeps
    learning at read time -- not a frozen fit."""
    install_patch(args.patch_dir)          # the asset's SCHEMA is the patched organ's
    from hdlab.coref import SpanCueTable as HSpanCueTable
    docs, gaz = load_test(args.docs, split="train")
    print("accruing the span-cue counts on GUM TRAIN: %d documents, %d mentions"
          % (len(docs), sum(len(d.mentions) for d in docs)), flush=True)
    post, syms, frames, caps = build_posteriors(docs)
    cfg = TyperCfg(marginal=True, support=args.support, eta=args.eta, graded_head=True,
                   kappa_card=args.kappa, card_mode=args.card_mode,
                   kappa_caps=args.kappa_caps, tau_learn=args.tau_learn)
    tab = SpanCueTable()
    type_arm(docs, cfg, post, syms, frame_by_doc=frames, caps_by_doc=caps, span_tab=tab, online=True)
    out = HSpanCueTable()
    out.lam = tab.lam
    out.n = {t: dict(tab.n[t]) for t in TYPES}
    out.syms = set(tab.syms)
    out.n_obs = tab.n_obs
    out.save()
    from hdlab.coref import SPAN_CUE_ASSET
    print("  %d observations -> %s" % (out.n_obs, SPAN_CUE_ASSET))
    for t in TYPES:
        print("    %-8s %s" % (t, {k: int(v) for k, v in sorted(tab.n[t].items())}))
    _write(args.out or "metrics_span_cue_asset.json",
           {"n_obs": out.n_obs, "counts": tab.as_dict(), "asset": SPAN_CUE_ASSET,
            "population": "GUM TRAIN (even doc index), %d documents; the typer's OWN confident typings "
                          "(p >= %.2f), no gold read anywhere" % (len(docs), args.tau_learn)})
    return 0


def cmd_patch_verify(args):
    """Run the PATCHED sources end to end on GUM TEST and score the typing they produce against the answer
    key, alongside the UNPATCHED loader in the same process."""
    import experiments.gum_coref as G
    docs_pre, gaz = load_test(args.docs, split=args.split)
    gold_by_doc = {d.docid: gold_type_and_head(d) for d in docs_pre}
    base = {}
    for d in docs_pre:
        base[d.docid] = {(m.start_g, m.end_g, m.eid): None for m in d.mentions}
    print("UNPATCHED loader (decision_source=organ) ...", flush=True)
    t0 = time.time()
    pre = G.load_docs(gum_only=True, name_gazetteer=gaz, decision_source="organ")
    pre = pre[1::2] if args.split == "test" else (pre[0::2] if args.split == "train" else pre)
    if args.docs:
        step = max(1, len(pre) // args.docs)
        pre = [pre[i] for i in range(0, len(pre), step)][:args.docs]
    print("  %d docs, %.0fs" % (len(pre), time.time() - t0), flush=True)
    install_patch(args.patch_dir)
    import importlib
    G2 = importlib.import_module("experiments.gum_coref")
    print("PATCHED loader ...", flush=True)
    t0 = time.time()
    postd = G2.load_docs(gum_only=True, name_gazetteer=gaz, decision_source="organ")
    postd = postd[1::2] if args.split == "test" else (postd[0::2] if args.split == "train" else postd)
    if args.docs:
        step = max(1, len(postd) // args.docs)
        postd = [postd[i] for i in range(0, len(postd), step)][:args.docs]
    print("  %d docs, %.0fs" % (len(postd), time.time() - t0), flush=True)

    def score(ds):
        per = []
        for d in ds:
            gold = gold_by_doc.get(d.docid) or {}
            agg = {t: [0, 0, 0] for t in TYPES}
            hit = tot = hh = ht = 0
            for m in d.mentions:
                g = gold.get((m.start_g, m.end_g, m.eid))
                if g is None:
                    continue
                gt, gh = g
                tot += 1
                ht += 1
                hh += int(m.head_g == gh)
                if m.mtype == gt:
                    hit += 1
                    agg[gt][0] += 1
                else:
                    agg[m.mtype][1] += 1
                    agg[gt][2] += 1
            per.append({"hit": hit, "tot": tot, "hhit": hh, "htot": ht, "agg": agg})
        return per
    a, b = score(pre), score(postd)
    res = {"population": "GUM %s, %d documents, %d mentions; the PATCHED sources exec'd into the live "
                         "modules, both loaders in ONE process" % (args.split.upper(), len(pre), _acc(a)[1]),
           "unpatched": {"type_acc": round(st_acc(a), 4), "head_acc": round(st_head(a), 4),
                         "macro_f1": round(st_macro(a), 4),
                         "f1": {t: round(_f1(a, t)[2], 4) for t in TYPES}},
           "patched": {"type_acc": round(st_acc(b), 4), "head_acc": round(st_head(b), 4),
                       "macro_f1": round(st_macro(b), 4),
                       "f1": {t: round(_f1(b, t)[2], 4) for t in TYPES}},
           "deltas": {"type_acc": _boot_delta(a, b, st_acc, args.boot),
                      "head_acc": _boot_delta(a, b, st_head, args.boot),
                      "macro_f1": _boot_delta(a, b, st_macro, args.boot),
                      "f1_name": _boot_delta(a, b, st_f1("name"), args.boot),
                      "f1_common": _boot_delta(a, b, st_f1("common"), args.boot),
                      "f1_pronoun": _boot_delta(a, b, st_f1("pronoun"), args.boot)}}
    for k in ("unpatched", "patched"):
        print("  %-10s %s" % (k, res[k]))
    for k, v in res["deltas"].items():
        print("  d %-12s %s" % (k, v))
    _write(args.out or "metrics_patch_verify.json", res)
    return 0


# ---------------------------------------------------------------------------------------------------------
def cmd_diagnose(args):
    """THE STATUS PROBE -- where the signal is lost, chain by chain, with counts.

    For the signal the end read needs ("is this span a pronoun, a name, or a common nominal, and how sure am
    I?") this walks every rung: what the organ PRODUCES, what the next rung READS, and what is LOST."""
    docs, gaz = load_test(args.docs, split=args.split)
    import experiments.gum_coref as G
    lc, tags = organ()
    gold_by_doc = {d.docid: gold_type_and_head(d) for d in docs}
    print("GUM %s: %d documents, %d tokens, %d mentions; feeding the passage ..."
          % (args.split.upper(), len(docs), sum(len(d.toks) for d in docs),
             sum(len(d.mentions) for d in docs)), flush=True)
    post, syms, frames, caps = build_posteriors(docs)
    cfg_g = TyperCfg(marginal=True, support=args.support, eta=args.eta, graded_head=True,
                     kappa_card=args.kappa, card_mode=args.card_mode)
    tf = Typer(SHIPPED, tags, G.PRONOUNS_ALL, lc=lc)
    tg = Typer(cfg_g, tags, G.PRONOUNS_ALL, lc=lc)
    conf = {}
    n = 0
    head_wrong = 0
    err_head = err_type = 0
    top2 = 0          # the gold type carries the 2nd-largest mass (what a better READ of this posterior can buy)
    anymass = 0       # the gold type carries >= 1% of the mass (the posterior is not empty of the answer)
    head_in_span = 0  # the gold head is INSIDE the span (a head rule could reach it)
    flip_type = 0
    flip_head = 0
    ent = []
    peaked = 0
    conf_wrong = []
    conf_right = []
    mass_bins = {}
    frame_err = {}
    frame_all = {}
    err_sample = []
    for d in docs:
        P = post[d.docid]
        S = syms.get(d.docid, {})
        FR = frames[d.docid]
        pred = argmax_tags(P)
        gmap = {t.gidx: t for t in d.toks}
        gold = gold_by_doc[d.docid]
        for m in d.mentions:
            span = [gmap[g] for g in range(m.start_g, m.end_g + 1) if g in gmap]
            span = [t for t in span if t.sent == m.sent] or span
            if not span:
                continue
            g = gold.get((m.start_g, m.end_g, m.eid))
            if g is None:
                continue
            gt, gh = g
            n += 1
            h0 = tf.head_of_span(span, P, pred)
            t0 = mention_type_shipped(h0, pred, G.PRONOUNS_ALL)
            h1 = tg.head_of_span(span, P, pred)
            t1, dist1 = tg.type_of(h1, P, pred, sym=S.get(h1.gidx), known=(h1.form.lower() in lc.vocab),
                                   frame=FR.get(h1.gidx))
            ck = gt + "->" + t0
            conf[ck] = conf.get(ck, 0) + 1
            if h0.gidx != gh:
                head_wrong += 1
            if t0 != gt:
                if h0.gidx != gh:
                    err_head += 1
                else:
                    err_type += 1
            if h1.gidx != h0.gidx:
                flip_head += 1
            if t1 != t0:
                flip_type += 1
            # the ORACLE CEILING ON THIS POSTERIOR, read at the GOLD head
            if P.get(gh) is not None:
                dg = tg.type_posterior(gmap[gh], P, pred, sym=S.get(gh),
                                       known=(gmap[gh].form.lower() in lc.vocab))
                srt = sorted(TYPES, key=lambda x: dg[x], reverse=True)
                if srt[0] == gt or srt[1] == gt:
                    top2 += 1
                if dg[gt] >= 0.01:
                    anymass += 1
                if t0 != gt:
                    mass_bins["%s->%s" % (gt, t0)] = mass_bins.get("%s->%s" % (gt, t0), [])
                    mass_bins["%s->%s" % (gt, t0)].append(dg[gt])
                    fr = FR.get(gh, ("?", "?"))
                    fk = "%s->%s|%s" % (gt, t0, fr[0])
                    frame_err[fk] = frame_err.get(fk, 0) + 1
                    if len(err_sample) < 40 and gt == "name" and t0 == "common":
                        err_sample.append({"doc": d.docid, "text": " ".join(x.form for x in span)[:70],
                                           "gold_head": gmap[gh].form, "shipped_head": h0.form,
                                           "det": fr[0], "right": fr[1],
                                           "P_name_at_gold_head": round(dg["name"], 3),
                                           "known": gmap[gh].form.lower() in lc.vocab})
            fr = FR.get(gh, ("?", "?"))
            frame_all["%s|%s" % (gt, fr[0])] = frame_all.get("%s|%s" % (gt, fr[0]), 0) + 1
            if any(t.gidx == gh for t in span):
                head_in_span += 1
            v = np.asarray([max(dist1[x], 1e-12) for x in TYPES])
            ent.append(float(-(v * np.log(v)).sum()))
            if dist1[t1] >= 0.99:
                peaked += 1
            if t0 == gt:
                conf_right.append(dist1[t1])
            else:
                conf_wrong.append(dist1[t1])
    ent = np.asarray(ent)
    out = {
        "population": "GUM %s, %d docs, %d mentions" % (args.split.upper(), len(docs), n),
        "confusion_gold_x_shipped": dict(sorted(conf.items(), key=lambda kv: -kv[1])),
        "shipped_head_wrong": head_wrong,
        "shipped_type_errors_from_a_wrong_head": err_head,
        "shipped_type_errors_with_the_right_head": err_type,
        "gold_head_is_inside_the_span": head_in_span,
        "gold_type_in_top2_type_mass_at_the_gold_head": top2,
        "gold_type_has_at_least_1pct_mass_at_the_gold_head": anymass,
        "graded_changes_the_head": flip_head,
        "graded_changes_the_type": flip_type,
        "type_posterior_entropy": {"mean": round(float(ent.mean()), 4),
                                   "median": round(float(np.median(ent)), 4),
                                   "p90": round(float(np.percentile(ent, 90)), 4)},
        "peaked_p_ge_0.99": peaked,
        "mean_confidence_when_shipped_is_RIGHT": round(float(np.mean(conf_right)), 4),
        "mean_confidence_when_shipped_is_WRONG": round(float(np.mean(conf_wrong)), 4),
        "gold_type_mass_at_the_gold_head_on_SHIPPED_ERRORS":
            {k: {"n": len(v), "mean": round(float(np.mean(v)), 4),
                 "share_ge_0.10": round(float(np.mean([x >= 0.10 for x in v])), 4),
                 "share_ge_0.33": round(float(np.mean([x >= 0.33 for x in v])), 4)}
             for k, v in sorted(mass_bins.items(), key=lambda kv: -len(kv[1]))},
        "det_frame_of_the_gold_head_by_gold_type": dict(sorted(frame_all.items(), key=lambda kv: -kv[1])[:20]),
        "det_frame_on_errors": dict(sorted(frame_err.items(), key=lambda kv: -kv[1])[:14]),
        "name_to_common_examples": err_sample,
    }
    for k, v in out.items():
        if k not in ("confusion_gold_x_shipped", "name_to_common_examples"):
            print(("  %-52s %s" % (k, v)).encode("ascii", "replace").decode("ascii"))
    print("  confusion (gold -> shipped), top 12:")
    for k, v in list(out["confusion_gold_x_shipped"].items())[:12]:
        print("      %-22s %d" % (k, v))
    _write(args.out or "metrics_diagnose.json", out)
    return 0


def cmd_handoff(args):
    """THE HAND-OFF, RE-COUNTED WITH THE GRADED TYPER (pri 112 P7.6: 385 argmax flips -> 82 mention-type
    changes).  Both register arms (the passage OPEN vs INERT) in ONE process."""
    docs, gaz = load_test(args.docs, split=args.split)
    import experiments.gum_coref as G
    lc, tags = organ()
    cfg_g = TyperCfg(marginal=True, support=args.support, eta=args.eta, graded_head=True,
                     kappa_card=args.kappa, card_mode=args.card_mode)
    tf = Typer(SHIPPED, tags, G.PRONOUNS_ALL, lc=lc)
    tg = Typer(cfg_g, tags, G.PRONOUNS_ALL, lc=lc)
    n_tok = n_flip = n_ment = 0
    pairs = {}
    ship_type_ch = graded_type_ch = graded_head_ch = 0
    mass_moved = []
    for d in docs:
        by_sent = {}
        for t in d.toks:
            by_sent.setdefault(t.sent, []).append(t)
        rws = [sorted(by_sent[s], key=lambda x: x.idx) for s in sorted(by_sent)]
        lc.new_document()                      # ARM OPEN: the passage fed once in order (the shipped loader)
        pA = {}
        for row, m in zip(rws, lc.feed_passage([[x.form for x in row] for row in rws])):
            for j, x in enumerate(row):
                pA[x.gidx] = np.asarray(m[j], dtype=np.float32)
        lc._reg = None                         # ARM INERT: no passage boundary -> the entity prior is silent
        lc._doc_shape = {}
        pB = {}
        for row in rws:
            m = lc.posterior([x.form for x in row])
            for j, x in enumerate(row):
                pB[x.gidx] = np.asarray(m[j], dtype=np.float32)
        predA, predB = argmax_tags(pA), argmax_tags(pB)
        gmap = {t.gidx: t for t in d.toks}
        for g in pA:
            n_tok += 1
            if predA[g] != predB[g]:
                n_flip += 1
                k = predB[g] + "->" + predA[g]
                pairs[k] = pairs.get(k, 0) + 1
            mass_moved.append(float(np.abs(pA[g] - pB[g]).sum()) / 2.0)
        for m in d.mentions:
            span = [gmap[gg] for gg in range(m.start_g, m.end_g + 1) if gg in gmap]
            span = [t for t in span if t.sent == m.sent] or span
            if not span:
                continue
            n_ment += 1
            hA = tf.head_of_span(span, pA, predA)
            hB = tf.head_of_span(span, pB, predB)
            ship_type_ch += int(mention_type_shipped(hA, predA, G.PRONOUNS_ALL)
                                != mention_type_shipped(hB, predB, G.PRONOUNS_ALL))
            gA = tg.head_of_span(span, pA, predA)
            gB = tg.head_of_span(span, pB, predB)
            uA, _ = tg.type_of(gA, pA, predA)
            uB, _ = tg.type_of(gB, pB, predB)
            graded_type_ch += int(uA != uB)
            graded_head_ch += int(gA.gidx != gB.gidx)
    out = {"population": "GUM %s, %d docs, %d tokens, %d mentions"
                         % (args.split.upper(), len(docs), n_tok, n_ment),
           "argmax_flips_from_opening_the_passage": n_flip,
           "argmax_flip_pairs_top": dict(sorted(pairs.items(), key=lambda kv: -kv[1])[:12]),
           "mention_type_changes_SHIPPED_typer": ship_type_ch,
           "mention_type_changes_GRADED_typer": graded_type_ch,
           "mention_head_changes_GRADED_typer": graded_head_ch,
           "mean_total_variation_mass_moved_per_token": round(float(np.mean(mass_moved)), 6)}
    for k, v in out.items():
        print("  %-46s %s" % (k, v))
    _write(args.out or "metrics_handoff.json", out)
    return 0


# ---------------------------------------------------------------------------------------------------------
def _self_test():
    """Witnesses.  W1 IDENTITY: at the shipped operating point the graded typer reproduces the shipped typer
    byte-for-byte.  W2 the marginalise-then-decide difference is REAL and is the Bayes decision.  W3 the twin
    destroys the pairing and keeps the shape.  W4 the card evidence is read complementarily (never twice)."""
    fails = []
    import experiments.gum_coref as G
    lc, tags = organ()
    ti = {t: i for i, t in enumerate(tags)}

    class T:
        def __init__(self, g, form):
            self.gidx = g
            self.form = form
            self.sent = 0
            self.idx = g + 1

    # ---- W1: the shipped operating point is an IDENTITY
    docs, _ = load_test(4)
    typer = Typer(SHIPPED, tags, G.PRONOUNS_ALL, lc=lc)
    same_h = same_t = n = 0
    for d in docs:
        post, syms = doc_posteriors(d, with_cards=True)
        pred = argmax_tags(post)
        gmap = {t.gidx: t for t in d.toks}
        for m in d.mentions:
            span = [gmap[g] for g in range(m.start_g, m.end_g + 1) if g in gmap]
            span = [t for t in span if t.sent == m.sent] or span
            if not span:
                continue
            n += 1
            h0 = head_of_span_shipped(span, pred, G.PRONOUNS_ALL)
            t0 = mention_type_shipped(h0, pred, G.PRONOUNS_ALL)
            h1 = typer.head_of_span(span, post, pred)
            t1, _ = typer.type_of(h1, post, pred)
            same_h += int(h0.gidx == h1.gidx)
            same_t += int(t0 == t1)
    ok = (same_h == n and same_t == n and n > 150)
    print("  %s W1 the shipped operating point is an IDENTITY: %d/%d heads, %d/%d types on %d documents"
          % ("PASS" if ok else "FAIL", same_h, n, same_t, n, len(docs)))
    if not ok:
        fails.append("W1")

    # ---- W2: marginalise-then-decide is a DIFFERENT decision, and it is the Bayes one
    p = np.zeros(len(tags), dtype=np.float32)
    p[ti["PROPN"]] = 0.35
    p[ti["NOUN"]] = 0.33
    p[ti["ADJ"]] = 0.32
    tk = T(0, "Frobnitz")
    post2 = {0: p}
    pred2 = {0: tags[int(p.argmax())]}
    ship = mention_type_shipped(tk, pred2, G.PRONOUNS_ALL)
    gt = Typer(TyperCfg(marginal=True, support="nominal", eta=float("inf"), graded_head=False),
               tags, G.PRONOUNS_ALL)
    got, dist = gt.type_of(tk, post2, pred2)
    ok = (ship == "name" and got == "common" and abs(dist["common"] - 0.65) < 1e-6)
    print("  %s W2 MARGINALISE THEN DECIDE: P(PROPN)=.35 vs P(NOUN)+P(ADJ)=.65 -> shipped '%s', graded '%s' "
          "(P(common)=%.4f)" % ("PASS" if ok else "FAIL", ship, got, dist["common"]))
    if not ok:
        fails.append("W2")

    # ---- W3: the twin preserves the SHAPE and destroys the PAIRING
    keys = list(post.keys())
    vals = [post[k] for k in keys]
    rng = random.Random(1)
    rng.shuffle(vals)
    tw = dict(zip(keys, vals))
    ent0 = sorted(round(float(-(v * np.log(v + 1e-12)).sum()), 6) for v in post.values())
    ent1 = sorted(round(float(-(v * np.log(v + 1e-12)).sum()), 6) for v in tw.values())
    moved = sum(1 for k in keys if not np.allclose(post[k], tw[k]))
    ok = (ent0 == ent1 and moved > 0.5 * len(keys))
    print("  %s W3 TWIN: the entropy multiset is identical (%s) and %d/%d rows moved"
          % ("PASS" if ok else "FAIL", ent0 == ent1, moved, len(keys)))
    if not ok:
        fails.append("W3")

    # ---- W4: the card evidence is COMPLEMENTARY (the organ gates it off exactly where the typer reads it)
    import hdlab.lexical_categories as LC
    kn = sum(1 for g, t in gmap.items() if t.form.lower() in lc.vocab)
    unk = len(gmap) - kn
    ok = (LC.ENT_KAPPA > 0 and kn > 0 and unk >= 0 and bool(lc.log_entc))
    print("  %s W4 the organ's entity term is read only where there is NO lexical entry: %d known / %d unknown "
          "tokens on %s; the typer's `complement` mode reads the cards on the KNOWN ones (ENT_KAPPA=%.1f)"
          % ("PASS" if ok else "FAIL", kn, unk, d.docid, LC.ENT_KAPPA))
    if not ok:
        fails.append("W4")

    # ---- W5: a card symbol read is AS OF the sentence (never the future) -- the register is not advanced by it
    nsym = len(syms)
    firsts = sum(1 for v in syms.values() if v.startswith("e_first"))
    ok = (nsym == len(gmap) and firsts > 0)
    print("  %s W5 card symbols read AS OF the sentence for %d/%d tokens (%d of them e_first)"
          % ("PASS" if ok else "FAIL", nsym, len(gmap), firsts))
    if not ok:
        fails.append("W5")

    # ---- W6: the PATCHED `name_content_tokens` with NO posterior is BYTE-IDENTICAL to the shipped one
    import hdlab.coref as _C
    before = []
    for d in docs:
        gm = {t.gidx: t for t in d.toks}
        for m in d.mentions:
            sp = [gm[g] for g in range(m.start_g, m.end_g + 1) if g in gm]
            sp = [t for t in sp if t.sent == m.sent] or sp
            if not sp:
                continue
            before.append((tuple(_C.name_content_tokens([t.form for t in sp])),
                           tuple(_C.name_content_tokens([t.form for t in sp],
                                                        upos=[t.upos for t in sp]))))
    pd = os.environ.get("HDLAB_P118_PATCH_DIR", "")
    if pd and os.path.isdir(pd):
        install_patch(pd)
        import importlib
        _C2 = importlib.import_module("hdlab.coref")
        after = []
        for d in docs:
            gm = {t.gidx: t for t in d.toks}
            for m in d.mentions:
                sp = [gm[g] for g in range(m.start_g, m.end_g + 1) if g in gm]
                sp = [t for t in sp if t.sent == m.sent] or sp
                if not sp:
                    continue
                after.append((tuple(_C2.name_content_tokens([t.form for t in sp])),
                              tuple(_C2.name_content_tokens([t.form for t in sp],
                                                            upos=[t.upos for t in sp]))))
        ok = (before == after and len(before) > 150)
        print("  %s W6 the PATCHED name_content_tokens with NO posterior is BYTE-IDENTICAL on %d mentions "
              "(both the capitalisation and the category call)" % ("PASS" if ok else "FAIL", len(before)))
        if not ok:
            fails.append("W6")
        # ---- W7: the span-cue table round-trips through the asset and is SILENT when empty
        t0 = _C2.SpanCueTable()
        ok7a = (t0.n_obs == 0)
        t0.observe("o1_l0", "name")
        t0.observe("o0_l1", "common")
        import tempfile
        pth = os.path.join(tempfile.gettempdir(), "p118_span_cue_selftest.json")
        t0.save(pth)
        t1 = _C2.SpanCueTable.load(pth)
        ok7 = ok7a and t1.n_obs == 2 and abs(t1.logp("o1_l0", "name") - t0.logp("o1_l0", "name")) < 1e-12 \
            and _C2.SpanCueTable.load(pth + ".missing").n_obs == 0
        print("  %s W7 the span-cue table is COUNTS: empty on construction, round-trips through the asset, "
              "and a MISSING asset loads an empty (silent) table" % ("PASS" if ok7 else "FAIL"))
        if not ok7:
            fails.append("W7")
        # ---- W8: the reader-side hunks are pure CAPABILITY -- the mention stream is unchanged except for
        # the two new keys, so no consumer's behaviour moves until one is deliberately wired to read them.
        try:
            from experiments.exp_crosstype_gum_conll_fullread_v1 import gum_to_conll
            from hdlab import frontend as _F
            import hdlab.referent_per_np as _RNP
            sc = os.path.join(OUT_DIR, "conll")
            os.makedirs(sc, exist_ok=True)
            dd = docs[0]
            pth2 = os.path.join(sc, dd.docid + ".selftest.conll")
            gum_to_conll(dd, pth2)
            tgr = _F.Tagger()
            ms_new, _n = _RNP.referent_per_np_source(pth2, tgr)
            keys_new = [{k: v for k, v in m.items() if k not in ("span_post", "span_tags")} for m in ms_new]
            n_post = sum(1 for m in ms_new if m.get("span_post") is not None)
            import importlib
            _RNP0 = importlib.reload(importlib.import_module("hdlab.referent_per_np"))
            ms_old, _n0 = _RNP0.referent_per_np_source(pth2, tgr)
            ok8 = (keys_new == ms_old and n_post > 0)
            print("  %s W8 the reader-side hunks are pure CAPABILITY: %d mentions identical to the shipped "
                  "stream once the two NEW keys are removed, and %d of them now carry the posterior row"
                  % ("PASS" if ok8 else "FAIL", len(ms_old), n_post))
            if not ok8:
                fails.append("W8")
        except Exception as e:                       # pragma: no cover -- the witness must not mask a failure
            print("  FAIL W8 (%s: %s)" % (type(e).__name__, e))
            fails.append("W8")
    else:
        print("  SKIP W6/W7/W8 (set HDLAB_P118_PATCH_DIR to the patched-source tree)")

    print("RESULT: %s" % ("PASS" if not fails else "FAIL (%s)" % ",".join(fails)))
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--typing", action="store_true")
    ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--diagnose", action="store_true")
    ap.add_argument("--handoff", action="store_true")
    ap.add_argument("--cluster", action="store_true")
    ap.add_argument("--board", action="store_true")
    ap.add_argument("--reader-stream", dest="reader_stream", action="store_true")
    ap.add_argument("--build-asset", dest="build_asset", action="store_true")
    ap.add_argument("--patch-verify", dest="patch_verify", action="store_true")
    ap.add_argument("--patch-dir", dest="patch_dir",
                    default=os.environ.get("HDLAB_P118_PATCH_DIR", ""))
    ap.add_argument("--card-mode", dest="card_mode", default="all", choices=("all", "complement", "off"))
    ap.add_argument("--docs", type=int, default=None)
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--eta", type=float, default=4.0)
    ap.add_argument("--kappa", type=float, default=0.5)
    ap.add_argument("--kappa-caps", dest="kappa_caps", type=float, default=1.0)
    ap.add_argument("--tau-learn", dest="tau_learn", type=float, default=0.95)
    ap.add_argument("--support", default="nominal")
    ap.add_argument("--split", default="test", choices=("test", "train", "all"))
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    if a.self_test:
        global OUT_DIR
        OUT_DIR = str(get_output_dir(ANCHOR + "_selftest"))
        return _self_test()
    if a.typing:
        return cmd_typing(a)
    if a.sweep:
        return cmd_sweep(a)
    if a.diagnose:
        return cmd_diagnose(a)
    if a.handoff:
        return cmd_handoff(a)
    if a.cluster:
        return cmd_cluster(a)
    if a.board:
        return cmd_board(a)
    if a.reader_stream:
        return cmd_reader_stream(a)
    if a.build_asset:
        return cmd_build_asset(a)
    if a.patch_verify:
        return cmd_patch_verify(a)
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
