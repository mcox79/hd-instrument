"""experiments/exp_passage_register_in_order_v1.py -- pri 112: THE PASSAGE IS READ ONCE, IN ORDER, AND READ AS OF THE SENTENCE.

THE DEFECT (measured; data/hook_state/diag_w3a4..9.log). The category organ (`hdlab/lexical_categories.py`) keeps a Heim (1982)
FILE-CARD register of the individuals met so far in the passage and reads it as a next-mention prior. Every call to
`posterior` / `tag` / `tag_with_posterior` FILED the sentence into those cards and advanced the ACT-R recency clock. Five
different consumers re-tag the same sentence at five different moments, so one sentence was filed ~5x, out of order, and the
posterior a consumer got depended on which consumer's memo happened to hit: on 1023_bleak_house sentence 59 the organ returned
FOUR DIFFERENT posteriors for token 0 in ONE read (P(first class) 4.3e-2 / 1.3e-3 / 9.3e-4 / 1.3e-2), and a process-global
`@lru_cache` on the reader's affect path (`situation_reader._affect_pos_cached`, whose docstring premise "tag() is a PURE
deterministic function of the token list" has been false since the entity-feedback arm landed) made the SECOND read of the same
document in the same process file fewer sentences -- 236 events against 235.

THE BRAIN'S FORM (the opening move). A passage is read ONCE, in order, and every later process reads what the comprehender knew
AT THAT POINT (Heim 1982 file-change semantics: the file is updated by the utterance being processed, in sequence; Anderson's
ACT-R base-level activation and Lewis & Vasishth 2005: the recency term is the time since the referent was LAST MET, which is a
quantity only if the clock counts SENTENCES OF THE PASSAGE and not calls into the organ). So:
  (a) the READER feeds the register ONCE per sentence, IN ORDER (`posterior(..., observe=True)`, ONE call site);
  (b) every other call is a READ answered AS OF the sentence it is about -- the cards filed by the earlier sentences, nothing
      later (cards carry their filing time; `symbol` counts only mentions with t < k);
  (c) no process-global memo of register-dependent output (the affect memo is keyed on the PASSAGE).

WHAT THIS CELL DOES. It materialises the proposed change as a real patch of `hdlab/lexical_categories.py` and
`hdlab/situation_reader.py` (explicit, asserted string edits -> `passage_register_patch.diff`), installs the PATCHED SOURCE
into the live modules for measurement (so everything measured here is literally the shipped diff), and measures:
  --self-test   witnesses: an as-of read reproduces the feed's own belief; a read files nothing; order-invariance; the FLOOR's
                order-DEPENDENCE; inert without new_document().
  --repeat      THE BAR: 12 LitBank documents read twice by fresh readers in one process, all seven W3a fields compared
                byte-for-byte, floor vs arm. (LitBank is 19c -- repeatability is not an accuracy number.)
  --accuracy    GUM (modern, real documents): the organ's tag accuracy under the POLLUTED multi-consumer call pattern vs the
                in-order feed + as-of reads, with the random-sentence-order twin, paired bootstrap over documents.

Glass-box, counts only; no spaCy / nltk / external LLM anywhere. Writes only data/exp_passage_register_in_order_v1/.
"""
from __future__ import annotations

import argparse
import difflib
import glob
import json
import os
import sys
import time

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from experiments._seed_checkpoint import get_output_dir          # noqa: E402

# KB_REFERENT: data/corpora/gum/conllu
# KB_REFERENT: data/frontend_assets/lexical_categories_counts_v1.json
ANCHOR = "exp_passage_register_in_order_v1"
# Q115 (owner, 2026-08-23): the canonical output directory comes from the shared helper, never from a hand-built
# path, so a re-run cannot replay a saved answer. With HDLAB_EXP_NAME unset this is data/exp_passage_register_in_order_v1/;
# --self-test is isolated to data/exp_passage_register_in_order_v1_selftest/ by the helper's own SH-5 rule.
OUT = str(get_output_dir(ANCHOR))

LC_PATH = os.path.join(REPO, "hdlab", "lexical_categories.py")
SR_PATH = os.path.join(REPO, "hdlab", "situation_reader.py")


# =====================================================================================================================
# 1. THE PATCH -- explicit (old, new) edits, each asserted to fire exactly once.
# =====================================================================================================================

LC_EDITS = [
# ---- imports --------------------------------------------------------------------------------------------------------
("""from collections import Counter, defaultdict""",
 """from bisect import bisect_left as _bisect_left
from collections import Counter, defaultdict"""),

# ---- the new switches + the passage generation counter ----------------------------------------------------------------
('''ENT_SYMS = ("e_first", "e_rep_bare", "e_rep_def", "e_rep_indef", "e_rep_plural")''',
 '''ENT_SYMS = ("e_first", "e_rep_bare", "e_rep_def", "e_rep_indef", "e_rep_plural")
# --- THE PASSAGE IS READ ONCE, IN ORDER, AND READ AS OF THE SENTENCE (2026-09-14, pri-112 solver) ---------------------
# Until now EVERY call to `posterior` / `tag` FILED the sentence into the file cards and advanced the ACT-R clock, and
# five consumers re-tag the same sentence at five different moments -- so one sentence was filed ~5x, out of order, the
# posterior depended on which consumer's memo happened to hit (FOUR distinct posteriors for one token in ONE read;
# data/hook_state/diag_w3a9.log), and the same document read twice in one process gave different events (236 vs 235).
# THE BRAIN'S FORM: a passage is read ONCE, in order (Heim 1982: the file is updated by the utterance being processed,
# in sequence), and every later process reads what the comprehender knew AT THAT POINT. The recency term of ACT-R
# base-level activation (Anderson; Lewis & Vasishth 2005) is a quantity at all only if the clock counts SENTENCES OF
# THE PASSAGE rather than calls into the organ -- under the old path the live clock ran ~5x fast, so a window of five
# sentences was in truth a window of one.
#   `posterior(words, observe=True)`  = THE ONE IN-ORDER FEED (the reader advancing the passage): it files this
#                                       sentence's mentions and advances the clock by exactly one sentence.
#   `posterior(words)` (the default)  = A READ: files nothing, advances nothing, and is answered AS OF the sentence this
#                                       token list is (resolved through the register's own sentence key).
#   ENT_REG_FILE_ALL  a file card is opened for EVERY referring expression the comprehender meets, not only for strings
#                     with no lexical entry. The offline table log P(E | c) is accrued in `accrue_entity_docs` with
#                     EVERY token filed, while the live read filed only UNKNOWN tokens: a train/read mismatch in the
#                     FILING POLICY (the symbol function itself is identical either way). Swept.
#   ENT_REG_GRAIN     'token' = the card is filed the moment the word is read (within-sentence incrementality; a read AS
#                     OF sentence k rebuilds the same within-sentence state in a transient overlay that is never
#                     persisted, so a read reproduces the feed's own belief EXACTLY). 'sentence' = the cards of sentence
#                     k are filed at its boundary, so the organ at sentence k knows exactly sentences 0..k-1. Swept.
#                     DEFAULT ON (2026-09-14 phase 7, strategy: the brain-foundational filing policy ships unless it
#                     costs). Measured on GUM, both arms read IN ORDER, 138 documents, paired bootstrap: all
#                     -0.00001 CI[-0.00008,+0.00006], unseen -0.00006 CI[-0.00054,+0.00034], repeat-mention
#                     +0.00027 CI[-0.00142,+0.00196], FIRST-mention 0.00000 CI[0.0,0.0]. It costs nothing and it
#                     closes the train/read mismatch. Set 0 to reproduce the pre-2026-09-14 filing policy exactly.
ENT_REG_FILE_ALL = os.environ.get("HDLAB_LC_ENT_REG_FILE_ALL", "1") == "1"
ENT_REG_GRAIN = os.environ.get("HDLAB_LC_ENT_REG_GRAIN", "token")
#   ENT_REG_LIVE_DOC  ARM B, the PASSAGE REGISTER, wired to the one in-order feed. `update_document_register` had NO
#                     live caller anywhere in hdlab/ or tools/ (enumerated 2026-09-14), so `_doc_shape` was always
#                     empty and ENT_THETA_DOC=100 was INERT on the live path. It is wired here -- and it needed the
#                     SAME as-of fix one level up, because `_doc_shape` was a single accumulator: a consumer asking
#                     about sentence k would otherwise be handed the convention of the WHOLE passage, which is the
#                     defect this rung exists to remove. The entries are cumulative sums stamped with the sentence
#                     that folded them in (see `_doc_shape_asof`). Exact for ENT_DOC_DECAY == 1.0 (the default).
#                     DEFAULT ON (2026-09-14 phase 7): measured on GUM, 138 documents, both arms read IN ORDER,
#                     paired bootstrap over documents -- repeat-mention 0.5770 -> 0.5823 (+0.00533
#                     CI[+0.00243,+0.00892], CI-SEPARATED) and FIRST-mention 0.8871 -> 0.8907 (+0.00363
#                     CI[+0.00118,+0.00616], CI-SEPARATED), overall -0.00006 and unseen -0.00071 both n.s.,
#                     PROPN<->NOUN 1,240 -> 1,247. It folds 7,584 sentences into 24 shape symbols as 25,959
#                     sentence-stamped entries. Set 0 to leave arm B inert as it was before 2026-09-14.
ENT_REG_LIVE_DOC = os.environ.get("HDLAB_LC_ENT_REG_LIVE_DOC", "1") == "1"
_REG_GEN = 0


def register_generation() -> int:
    """The identity of the passage currently open (bumped by `new_document`); 0 = no passage has ever been opened.
    A memo of anything that depends on the register (the reader's affect-path POS memo) must be keyed on this: the
    tags for a string are constant WITHIN a passage and not across passages."""
    return _REG_GEN'''),

# ---- the register itself ----------------------------------------------------------------------------------------------
('''class DiscourseRegister:
    """Heim (1982) FILE CARDS for one passage, keyed by surface type -- the route the entity layer itself uses for
    NAMES (`hdlab/online_entity_cluster.online_cluster` resolves a name by its string through the aliaser and sends
    only common nouns through cue-based retrieval). Purely SURFACE: no category is read, so the symbol computed
    while ACCRUING and the symbol computed while READING are the same function of the same evidence -- no
    train/read mismatch and no circularity with the decision it informs."""

    __slots__ = ("h", "sent_no")

    def __init__(self):
        self.h = {}
        self.sent_no = 0

    def _card(self, wl):
        c = self.h.get(wl)
        if c is None:
            c = self.h[wl] = {"n": 0, "det": set(), "plural": False, "last": -1}
        return c

    def symbol(self, wl):
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
        if ENT_RECENCY:
            # ACT-R BASE-LEVEL ACTIVATION, discretised (the substrate's own constants live in
            # `hdlab/salience_binder.actr_activation`): a file card last touched 40 sentences ago is weak evidence
            # and one touched two sentences ago is strong, so the prior is read against the card's ACTIVATION and
            # not merely its existence. The window is swept (2 / 5 / 10 measured; 5 is the operating point).
            base += "|r" if (self.sent_no - c["last"]) <= ENT_RECENCY else "|d"
        return base

    def observe(self, lows, i):
        """Write word i into the file cards -- called only AFTER the symbol for word i has been consumed."""
        wl = lows[i]
        c = self._card(wl)
        c["n"] += 1
        c["last"] = self.sent_no
        c["det"].add(det_context(lows, i))
        for alt in _plural_variants(wl):
            if alt == wl:
                continue
            o = self.h.get(alt)
            if o is not None and o["n"] > 0:
                c["plural"] = True
                o["plural"] = True''',
 '''class DiscourseRegister:
    """Heim (1982) FILE CARDS for one passage, keyed by surface type -- the route the entity layer itself uses for
    NAMES (`hdlab/online_entity_cluster.online_cluster` resolves a name by its string through the aliaser and sends
    only common nouns through cue-based retrieval). Purely SURFACE: no category is read, so the symbol computed
    while ACCRUING and the symbol computed while READING are the same function of the same evidence -- no
    train/read mismatch and no circularity with the decision it informs.

    READ ONCE, IN ORDER; READ AS OF THE SENTENCE (2026-09-14, pri-112). Every card carries the FILING TIMES of the
    sentences in which the comprehender met that string, so a consumer that asks about sentence k long after the
    passage was read is answered with the cards filed by sentences 0..k-1 -- what the comprehender knew at that
    point -- and nothing later. Exactly ONE caller FEEDS (`posterior(..., observe=True)`, the reader advancing the
    passage); every other call is a READ that writes nothing and advances nothing. The current sentence's own
    mentions live in a transient OVERLAY that `commit` persists on a feed and throws away on a read, so a read of
    sentence k reproduces the feed's own belief about sentence k exactly (witness W1)."""

    __slots__ = ("h", "sent_no", "sent_key", "_as_of", "_ov", "n_read_miss", "n_read", "n_feed")

    def __init__(self):
        self.h = {}
        self.sent_no = 0
        self.sent_key = {}        # lowered token tuple -> the sentence index at which the reader FED it
        self._as_of = 0           # the sentence the call in flight is being answered as of
        self._ov = None           # the current sentence's own mentions (never persisted by a read)
        self.n_read_miss = 0      # reads of a token list that was never fed (answered as of the passage so far)
        self.n_read = 0
        self.n_feed = 0

    # ---------------------------------------------------------------- the clock
    def begin(self, lows, observe, sent_idx=None):
        """Open one call. FEED -> as of the next unread sentence. READ -> as of the sentence this token list IS."""
        if observe:
            self._as_of = self.sent_no if sent_idx is None else int(sent_idx)
            self.n_feed += 1
        else:
            self.n_read += 1
            k = sent_idx
            if k is None:
                k = self.sent_key.get(tuple(lows))
            if k is None:
                # never fed (a sub-span, or a consumer reading text the comprehender never advanced through):
                # answer with everything the comprehender has read so far. Deterministic either way.
                self.n_read_miss += 1
                k = self.sent_no
            self._as_of = int(k)
        self._ov = {}
        return self._as_of

    def commit(self, observe, lows=None):
        """Close the call. A READ discards the overlay; the FEED persists it at the current sentence and advances the
        ACT-R clock by exactly ONE sentence."""
        ov, self._ov = self._ov, None
        if not observe:
            return
        t = self.sent_no
        self._persist(ov, t)
        if lows is not None:
            self.sent_key.setdefault(tuple(lows), t)
        self.sent_no = t + 1

    def _persist(self, ov, t):
        """Write the sentence's overlay into the file cards at filing time t."""
        if ov:
            for wl, o in ov.items():
                c = self._card(wl)
                ev = c["ev"]
                k = (ev[-1][1] if ev else False) or o["k"]
                d = (ev[-1][2] if ev else False) or o["d"]
                if ev and ev[-1][0] == t:
                    ev[-1] = (t, k, d)
                else:
                    ev.append((t, k, d))
            # the plural pairing is SYMMETRIC (Gelman & Taylor 1984: it is the passage's own evidence that the string
            # names a KIND, and it becomes available to BOTH cards at the moment the pair is met)
            for wl in ov:
                c = self.h[wl]
                for alt in _plural_variants(wl):
                    if alt == wl:
                        continue
                    o = self.h.get(alt)
                    if o is not None and o["ev"]:
                        if c["pf"] is None:
                            c["pf"] = t
                        if o["pf"] is None:
                            o["pf"] = t

    def _card(self, wl):
        c = self.h.get(wl)
        if c is None:
            c = self.h[wl] = {"ev": [], "pf": None}
        return c

    def symbol(self, wl):
        """The entity layer's symbol for this string AS OF the sentence the call in flight is about."""
        k = self._as_of
        c = self.h.get(wl)
        n = 0
        kind = False
        deff = False
        last = -1
        if c is not None and c["ev"]:
            ev = c["ev"]
            j = _bisect_left(ev, (k,))          # the mentions filed STRICTLY BEFORE sentence k
            if j:
                n = j
                last, kind, deff = ev[j - 1]
        ov = self._ov.get(wl) if self._ov else None
        if ov is not None:
            n += 1
            last = k                             # met earlier in THIS sentence
            kind = kind or ov["k"]
            deff = deff or ov["d"]
        if n == 0:
            return "e_first"
        if (c is not None and c["pf"] is not None and c["pf"] < k) or (ov is not None and ov["p"]):
            base = "e_rep_plural"
        elif kind:
            base = "e_rep_indef"
        elif deff:
            base = "e_rep_def"
        else:
            base = "e_rep_bare"
        if ENT_RECENCY:
            # ACT-R BASE-LEVEL ACTIVATION, discretised (the substrate's own constants live in
            # `hdlab/salience_binder.actr_activation`): a file card last touched 40 sentences ago is weak evidence
            # and one touched two sentences ago is strong, so the prior is read against the card's ACTIVATION and
            # not merely its existence. The window is swept (2 / 5 / 10 measured; 5 is the operating point).
            # THE CLOCK IS SENTENCES OF THE PASSAGE (pri-112): before, it counted calls into the organ, so on the live
            # reader path it ran ~5x fast and a five-sentence window was in truth a window of one.
            base += "|r" if (k - last) <= ENT_RECENCY else "|d"
        return base

    def note(self, lows, i):
        """Meet mention i of the sentence being read. It enters the CURRENT sentence's overlay only; the cards
        themselves are written by `commit`, i.e. by the ONE in-order feed and by nothing else. Called strictly AFTER
        the symbol for word i has been consumed."""
        if self._ov is None:
            return
        wl = lows[i]
        d = det_context(lows, i)
        o = self._ov.get(wl)
        if o is None:
            o = self._ov[wl] = {"k": False, "d": False, "p": False}
        o["k"] = o["k"] or (d in KIND_DET)
        o["d"] = o["d"] or (d in DEF_DET)
        if not o["p"]:
            k = self._as_of
            for alt in _plural_variants(wl):
                if alt == wl:
                    continue
                a = self.h.get(alt)
                if (a is not None and a["ev"] and a["ev"][0][0] < k) or (alt in self._ov):
                    o["p"] = True
                    po = self._ov.get(alt)
                    if po is not None:
                        po["p"] = True
                    break

    def observe(self, lows, i):
        """Back-compatible single-mention filing at the CURRENT sentence. It does NOT advance the clock (the caller
        that uses this form advances it itself, one step per sentence)."""
        own = self._ov is None
        if own:
            self._ov = {}
            self._as_of = self.sent_no
        self.note(lows, i)
        if own:
            ov, self._ov = self._ov, None
            self._persist(ov, self.sent_no)'''),

# ---- the OFFLINE ACCRUAL reads the passage through exactly the same in-order API as the reader --------------------------
('''        for d in docs:
            reg = DiscourseRegister()
            for sent in d:
                lows = [w.lower() for w, _ in sent]
                for i, (_w, t) in enumerate(sent):
                    sym = reg.symbol(lows[i])
                    self.entc[t][sym] += 1
                    if wcnt.get(lows[i], 0) <= nmax:
                        self.entc_u[t][sym] += 1
                    reg.observe(lows, i)
                reg.sent_no += 1          # the passage advances (the ACT-R recency clock; mirrors `posterior`)''',
 '''        for d in docs:
            reg = DiscourseRegister()
            for sent in d:
                lows = [w.lower() for w, _ in sent]
                # the accrual reads the passage through the SAME in-order API the reader uses (pri-112: begin / note
                # / commit), so the symbol computed while accruing and the symbol computed while reading are the same
                # function of the same evidence, evaluated by the same code -- witness W10 asserts the resulting
                # counts are byte-identical to the pre-pri-112 accrual.
                reg.begin(lows, True)
                for i, (_w, t) in enumerate(sent):
                    sym = reg.symbol(lows[i])
                    self.entc[t][sym] += 1
                    if wcnt.get(lows[i], 0) <= nmax:
                        self.entc_u[t][sym] += 1
                    reg.note(lows, i)
                reg.commit(True, lows)    # the passage advances (the ACT-R recency clock; mirrors `posterior`)'''),

# ---- ARM B: the passage register is read AS OF the sentence too -----------------------------------------------------------
("""    def update_document_register(self, words: Sequence[str], post: np.ndarray) -> None:
        \"\"\"ARM B: fold the SETTLED, GRADED belief about this sentence into the passage's shape register -- a
        prediction can only be fed back once the belief it came from has settled, so at a sentence boundary.\"\"\"
        if ENT_THETA_DOC is None:
            return
        if ENT_DOC_DECAY != 1.0:
            for r in self._doc_shape.values():
                r *= ENT_DOC_DECAY
        for i, w in enumerate(words):
            if ENT_REG_KNOWN and w.lower() not in self.vocab:
                continue                     # calibrate the passage convention on what the organ is SURE about
            sp = self._unk_sym(w, position_class(words, i))
            r = self._doc_shape.get(sp)
            if r is None:
                r = self._doc_shape[sp] = np.zeros(len(self.tags))
            r += post[i]""",
 """    def update_document_register(self, words: Sequence[str], post: np.ndarray, sent_idx: Optional[int] = None) -> None:
        \"\"\"ARM B: fold the SETTLED, GRADED belief about this sentence into the passage's shape register -- a
        prediction can only be fed back once the belief it came from has settled, so at a sentence boundary.
        STAMPED WITH ITS SENTENCE (2026-09-14, pri-112): the register keeps CUMULATIVE sums per shape symbol, one
        entry per sentence that touched it, so `_doc_shape_asof` can answer a later consumer with the convention the
        comprehender had established BY THAT SENTENCE. Without the stamp a consumer asking about sentence k would be
        handed the whole passage's convention -- the same read-the-future defect as the file cards, one level up.
        Exact for ENT_DOC_DECAY == 1.0 (the default); with a decay the prefix sums are only approximate, because a
        decay touches symbols this sentence did not.\"\"\"
        if ENT_THETA_DOC is None:
            return
        t = sent_idx
        if t is None:
            t = (self._reg.sent_no if self._reg is not None else 0)
        T = len(self.tags)
        delta: Dict[str, np.ndarray] = {}
        for i, w in enumerate(words):
            if ENT_REG_KNOWN and w.lower() not in self.vocab:
                continue
            sp = self._unk_sym(w, position_class(words, i))
            d = delta.get(sp)
            if d is None:
                d = delta[sp] = np.zeros(T)
            d += post[i]
        for sp, d in delta.items():
            ent = self._doc_shape.setdefault(sp, [])
            base = ent[-1][1] if ent else np.zeros(T)
            if ENT_DOC_DECAY != 1.0:
                base = base * ENT_DOC_DECAY
            cum = base + d
            if ent and ent[-1][0] == t:
                ent[-1] = (t, cum)
            else:
                ent.append((t, cum))

    def _doc_shape_asof(self, sp: str):
        \"\"\"The passage's shape register for this symbol AS OF the sentence the call in flight is about: the
        cumulative sum over the sentences folded in STRICTLY BEFORE it. None when the comprehender had nothing yet.\"\"\"
        ent = self._doc_shape.get(sp)
        if not ent:
            return None
        k = self._reg._as_of if self._reg is not None else (ent[-1][0] + 1)
        j = _bisect_left(ent, (k,))
        return ent[j - 1][1] if j else None"""),

# ---- the passage counter on the instance --------------------------------------------------------------------------------
('''        self._reg = None                                              # the current passage's file cards''',
 '''        self._reg = None                                              # the current passage's file cards
        self._reg_gen = 0                                             # which passage (see register_generation)'''),

# ---- new_document bumps the generation; the in-order feed lives here -------------------------------------------------------
('''    def new_document(self) -> None:
        """Passage boundary: open a fresh set of file cards and clear the passage register (Heim: a new file)."""
        self._reg = DiscourseRegister()
        self._doc_shape = {}''',
 '''    def new_document(self) -> None:
        """Passage boundary: open a fresh set of file cards and clear the passage register (Heim: a new file).
        Bumps the PASSAGE GENERATION so a memo of register-dependent output cannot serve one passage's belief into
        another (the reader's affect-path POS memo was exactly that -- see situation_reader._affect_pos)."""
        global _REG_GEN
        _REG_GEN += 1
        self._reg = DiscourseRegister()
        self._reg_gen = _REG_GEN
        self._doc_shape = {}

    def feed_passage(self, sentences, lag: Optional[int] = None):
        """THE ONE IN-ORDER FEED. The comprehender reads the passage once, sentence by sentence, in order; the file
        cards are written HERE and nowhere else, and the ACT-R clock advances one sentence per sentence. Returns the
        per-sentence settled posteriors so the caller can hand the SAME belief to every consumer that later asks for
        that sentence (they would otherwise each re-run forward-backward and each get a different answer)."""
        out = []
        for s in sentences:
            p = self.posterior(list(s), lag=lag, observe=True)
            if ENT_REG_LIVE_DOC and ENT_THETA_DOC is not None and self._reg is not None:
                # ARM B, at the sentence boundary and stamped with the sentence just read (the clock has already
                # advanced), so the belief re-enters the competition for LATER sentences only -- never its own.
                self.update_document_register(list(s), p, sent_idx=self._reg.sent_no - 1)
            out.append(p)
        return out

    def observe_sentence(self, words: Sequence[str], lag: Optional[int] = None) -> np.ndarray:
        """One sentence of the in-order feed (see feed_passage)."""
        return self.posterior(list(words), lag=lag, observe=True)'''),

("""        if ENT_THETA_DOC is not None:
            r = self._doc_shape.get(sp)
            nd = float(r.sum()) if r is not None else 0.0""",
 """        if ENT_THETA_DOC is not None:
            r = self._doc_shape_asof(sp)          # AS OF this sentence (pri-112), never the whole passage
            nd = float(r.sum()) if r is not None else 0.0"""),

# ---- _log_emit no longer writes -----------------------------------------------------------------------------------------
('''        if self._reg is not None:
            self._reg.observe(self._sent_lows, here)   # strictly in order: file the token only after reading it
        return out''',
 '''        return out'''),

# ---- posterior: observe / as-of ------------------------------------------------------------------------------------------
('''    def posterior(self, words: Sequence[str], lag: Optional[int] = None) -> np.ndarray:
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
        if self._reg is not None:
            self._reg.sent_no += 1                     # the passage advances one sentence (ACT-R recency clock)''',
 '''    def posterior(self, words: Sequence[str], lag: Optional[int] = None, observe: bool = False,
                  sent_idx: Optional[int] = None) -> np.ndarray:
        """Forward-backward marginals P(category_i | words): [n, T].
        lag (2026-09-13, owner: organs take data IN ORDER): the belief about word i may use only the words up to i + lag -- lag 0 is
        the running (filtered) belief the reader holds the moment a word arrives, a small lag is revision within a short window as
        the next words come in (reanalysis), None = the whole sentence (smoothing; the offline stand-in). Module default LAG.
        observe (2026-09-14, pri-112): TRUE only at THE ONE IN-ORDER FEED -- the comprehender advancing the passage. It files this
        sentence's mentions into the passage's file cards and advances the ACT-R clock by one sentence. FALSE (the default, and
        every other caller in the substrate) is a READ: it writes nothing, advances nothing, and is answered AS OF the sentence
        this token list is, so a consumer that asks late still gets what the comprehender knew at that sentence."""
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
        reg = self._reg
        if reg is not None:
            reg.begin(self._sent_lows, observe, sent_idx)
            tok_grain = (ENT_REG_GRAIN == "token")
            rows = []
            for i, w in enumerate(words):
                rows.append(self._log_emit(w))
                if tok_grain and (ENT_REG_FILE_ALL or self._sent_lows[i] not in self.vocab):
                    reg.note(self._sent_lows, i)       # strictly in order: file the token only after reading it
            le = np.stack(rows)
            if not tok_grain:
                for i in range(n):
                    if ENT_REG_FILE_ALL or self._sent_lows[i] not in self.vocab:
                        reg.note(self._sent_lows, i)
        else:
            le = np.stack([self._log_emit(w) for w in words])
        if self.use_frame and FRAME and FRAME_KAPPA > 0:
            le = le + FRAME_KAPPA * self._log_frame(words, lag)
        post = self._posterior_le(le, lag)
        if reg is not None:
            reg.commit(observe, self._sent_lows)       # a READ writes nothing; the FEED advances the passage one sentence'''),

# ---- tag / tag_with_posterior pass through ---------------------------------------------------------------------------------
('''    def tag(self, words: Sequence[str]) -> List[str]:
        """Point readout: argmax of the posterior per token (graded marginal, not Viterbi)."""
        if not words:
            return []
        post = self.posterior(words)
        return [self.tags[int(np.argmax(post[i]))] for i in range(len(words))]

    def tag_with_posterior(self, words: Sequence[str]) -> Tuple[List[str], List[Dict[str, float]]]:
        post = self.posterior(words)''',
 '''    def tag(self, words: Sequence[str], observe: bool = False, sent_idx: Optional[int] = None) -> List[str]:
        """Point readout: argmax of the posterior per token (graded marginal, not Viterbi). A READ by default -- see
        `posterior`: it does not write the passage's file cards and does not advance the ACT-R clock."""
        if not words:
            return []
        post = self.posterior(words, observe=observe, sent_idx=sent_idx)
        return [self.tags[int(np.argmax(post[i]))] for i in range(len(words))]

    def tag_with_posterior(self, words: Sequence[str], observe: bool = False,
                           sent_idx: Optional[int] = None) -> Tuple[List[str], List[Dict[str, float]]]:
        post = self.posterior(words, observe=observe, sent_idx=sent_idx)'''),
]


SR_EDITS = [
('''@lru_cache(maxsize=8192)
def _affect_pos_cached(sentence_text: str):
    """Per-string memo of the frontend UPOS tags for the affect path. EFFICIENCY (2026-09-06): tag() is a
    PURE deterministic function of the token list, and _assign_affect runs once PER EVENT -- many events share
    a sentence, so the identical string was re-tagged repeatedly (the affect path was ~half the read's POS-tag
    calls; tagging is ~40% of read cost). Memoizing by sentence_text is BYTE-IDENTICAL (same split, same
    deterministic tagger, same tags) and safe across reads (the frontend model is process-constant). Returns a
    tuple; callers copy to a fresh list so a downstream mutation cannot corrupt the cache."""
    return tuple(_load_frontend()[0].tag(sentence_text.split(" ")))''',
 '''@lru_cache(maxsize=8192)
def _affect_pos_cached(reg_gen: int, sentence_text: str):
    """Per-PASSAGE memo of the frontend UPOS tags for the affect path. EFFICIENCY (2026-09-06): _assign_affect runs
    once PER EVENT -- many events share a sentence, so the identical string was re-tagged repeatedly (the affect path
    was ~half the read's POS-tag calls; tagging is ~40% of read cost).

    KEYED ON THE PASSAGE (2026-09-14, pri-112). The 2026-09-06 premise -- "tag() is a PURE deterministic function of
    the token list ... safe across reads" -- stopped being true when the entity-feedback arm landed: the category organ
    reads the passage's Heim file cards, so the tags for one string depend on WHICH PASSAGE is open. A process-global
    memo keyed on the string alone served one document's tags into another, which is how the same document read twice
    in one process produced different events (236 vs 235; data/hook_state/diag_w3a9.log). `reg_gen` is the category
    organ's passage counter, which is the unit over which the tags really are constant. Returns a tuple; callers copy
    to a fresh list so a downstream mutation cannot corrupt the cache."""
    return tuple(_load_frontend()[0].tag(sentence_text.split(" ")))


def _affect_pos(sentence_text: str):
    """The affect path's tags for this sentence, memoized per PASSAGE (see _affect_pos_cached)."""
    try:
        from hdlab import lexical_categories as _LC
        g = _LC.register_generation()
    except Exception:
        g = 0
    return _affect_pos_cached(g, sentence_text)'''),

('''    pos = list(_affect_pos_cached(sentence_text))   # hdlab UD UPOS (memoized per string), one category system''',
 '''    pos = list(_affect_pos(sentence_text))   # hdlab UD UPOS (memoized per PASSAGE), one category system'''),

('''            from hdlab import lexical_categories as _LC
            _LC.get().new_document()''',
 '''            from hdlab import lexical_categories as _LC
            import numpy as _np
            _lc = _LC.get()
            _lc.new_document()
            # THE ONE IN-ORDER FEED (pri 112, 2026-09-14). The reader is the one comprehender that advances the
            # passage, so it reads the passage ONCE, sentence by sentence, IN ORDER, and the file cards are written
            # HERE and nowhere else; every other consumer's call to tag / posterior is a READ answered AS OF its own
            # sentence. Before this, five consumers re-tagged each sentence at five different moments and each write
            # changed what the next one saw (FOUR distinct posteriors for one token in ONE read, and 236 vs 235 events
            # on the second read of the same document -- data/hook_state/diag_w3a9.log). The settled belief is cached
            # under the reader's own per-read key, so the consumer that re-asks for a sentence is served THIS pass
            # instead of re-running forward-backward: the feed costs no extra passes.
            _raw = parse_conll_sentences(conll_path, lower=False)
            for _s, _m in zip(_raw, _lc.feed_passage(_raw)):
                _k = tuple(_s)
                self._read_parse_cache[("tag", _k)] = [_lc.tags[int(_np.argmax(_m[i]))] for i in range(len(_s))]
                self._read_parse_cache[("tagpost", _k)] = [
                    {t: float(_m[i, j]) for j, t in enumerate(_lc.tags) if _m[i, j] >= 0.01} for i in range(len(_s))]
                self._read_parse_cache[("tagmat", _k)] = _m'''),
]

GC_PATH = os.path.join(REPO, "experiments", "gum_coref.py")

# THE BOARD'S GUM LOADER IS A CONSUMER OF THE SAME ORGAN, AND IT NEVER OPENED A PASSAGE (2026-09-14 phase 7).
# `organ_tags` already reads the document sentence by sentence IN READING ORDER -- it was only ever missing the
# passage boundary, so with `self._reg is None` the entity-feedback arm was INERT on every board row it feeds
# (coref / common_noun_coref / salience). ONE ORGAN, ONE REGISTER: the loader now opens the passage and feeds it
# once, exactly as the reader does, and takes its tags from that one settled pass.
GC_EDITS = [('    from hdlab import frontend as F\n    tg = F.tagger()\n    by_sent = {}\n    for t in toks:\n        by_sent.setdefault(t.sent, []).append(t)\n    pred = {}\n    for s in sorted(by_sent):\n        row = sorted(by_sent[s], key=lambda x: x.idx)\n        for x, c in zip(row, tg.tag([x.form for x in row])):\n            pred[x.gidx] = c\n    return pred', '    from hdlab import frontend as F\n    tg = F.tagger()\n    by_sent = {}\n    for t in toks:\n        by_sent.setdefault(t.sent, []).append(t)\n    rows = [sorted(by_sent[s], key=lambda x: x.idx) for s in sorted(by_sent)]\n    pred = {}\n    # THE PASSAGE BOUNDARY AND THE ONE IN-ORDER FEED (pri 112, 2026-09-14). This loader already read the document\n    # in reading order; it was only ever missing `new_document()`, so with `self._reg is None` the category organ\'s\n    # entity-feedback arm (pri 104: the Heim file cards that say whether a string has been used to pick out an\n    # INDIVIDUAL in THIS passage) was INERT for every board row this loader feeds -- coref, common_noun_coref and\n    # salience. Measured cost of the inert path on GUM, both arms read in order, 138 documents, paired bootstrap:\n    # repeat-mention -0.01012 CI[-0.01883,-0.00175], unseen -0.00425 CI[-0.00722,-0.00173], overall -0.00119\n    # CI[-0.00181,-0.00066], all CI-separated, PROPN<->NOUN 1,238 -> 1,288. ONE ORGAN, ONE REGISTER: a consumer\n    # that reads a PASSAGE opens one. `feed_passage` returns the settled per-sentence posteriors, so the tags come\n    # from that single in-order pass and no sentence is read twice.\n    lc = getattr(tg, "_lc", None)\n    if lc is not None:\n        lc.new_document()\n        for row, m in zip(rows, lc.feed_passage([[x.form for x in row] for row in rows])):\n            for j, x in enumerate(row):\n                pred[x.gidx] = lc.tags[int(m[j].argmax())]\n        return pred\n    for row in rows:                       # HDLAB_TAG_SOURCE=perceptron: the stand-in keeps no passage register\n        for x, c in zip(row, tg.tag([x.form for x in row])):\n            pred[x.gidx] = c\n    return pred')]

PATCH = [("hdlab/lexical_categories.py", LC_PATH, LC_EDITS), ("hdlab/situation_reader.py", SR_PATH, SR_EDITS),
         ("experiments/gum_coref.py", GC_PATH, GC_EDITS)]
_ORIG = {}


def _orig(path):
    if path not in _ORIG:
        with open(path, encoding="utf-8") as f:
            _ORIG[path] = f.read()
    return _ORIG[path]


def patched_source(path, edits):
    src = _orig(path)
    for old, new in edits:
        k = src.count(old)
        if k != 1:
            raise SystemExit("PATCH ANCHOR matched %d times in %s (expected 1)\n---\n%s\n---" % (k, path, old[:240]))
        src = src.replace(old, new)
    return src


def make_diff() -> str:
    out = []
    for rel, path, edits in PATCH:
        a = _orig(path).splitlines(keepends=True)
        b = patched_source(path, edits).splitlines(keepends=True)
        out.extend(difflib.unified_diff(a, b, fromfile="a/" + rel, tofile="b/" + rel, n=3))
    return "".join(out)


def install():
    """Install the PATCHED SOURCE into the live category organ, so everything measured here IS the shipped diff."""
    import hdlab.lexical_categories as LC
    exec(compile(patched_source(LC_PATH, LC_EDITS), LC_PATH, "exec"), LC.__dict__)
    import hdlab.frontend as FE
    FE._T = None
    FE._P = None
    return LC


def install_reader():
    import hdlab.situation_reader as SR
    exec(compile(patched_source(SR_PATH, SR_EDITS), SR_PATH, "exec"), SR.__dict__)
    return SR


def install_gum_coref():
    """Install the patched board GUM loader (the passage boundary + the one in-order feed)."""
    import experiments.gum_coref as GC
    exec(compile(patched_source(GC_PATH, GC_EDITS), GC_PATH, "exec"), GC.__dict__)
    return GC


def restore_gum_coref():
    import experiments.gum_coref as GC
    exec(compile(_orig(GC_PATH), GC_PATH, "exec"), GC.__dict__)


def restore():
    import hdlab.lexical_categories as LC
    exec(compile(_orig(LC_PATH), LC_PATH, "exec"), LC.__dict__)
    import hdlab.frontend as FE
    FE._T = None
    FE._P = None


def restore_reader():
    import hdlab.situation_reader as SR
    exec(compile(_orig(SR_PATH), SR_PATH, "exec"), SR.__dict__)


# =====================================================================================================================
# 2. WITNESSES (scaffold-free; no corpus needed beyond the live asset)
# =====================================================================================================================

_PASSAGE = [
    "Souter joined the Court in 1990 .".split(),
    "The justice wrote a short opinion .".split(),
    "Souter and the MSM disagreed about the Gateses .".split(),
    "A dax is a kind of thing , and the daxes multiplied .".split(),
    "Souter retired , and the MSM said little about dax .".split(),
    "The CEO of the MSM met Souter again .".split(),
]

PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok)
    FAIL += int(not ok)
    return ok


def _maxdiff(a, b):
    return float(np.max(np.abs(np.asarray(a) - np.asarray(b)))) if len(a) else 0.0


def self_test() -> bool:
    t0 = time.time()
    import hdlab.lexical_categories as LC

    # ---------- the FLOOR (unpatched) is ORDER-DEPENDENT: the defect exists ----------
    lc = LC.get()
    lc.new_document()
    floor_fwd = [lc.posterior(list(s)) for s in _PASSAGE]
    lc.new_document()
    for s in _PASSAGE:                     # a second consumer re-tags the same passage (what the reader does ~5x)
        lc.posterior(list(s))
    floor_2nd = [lc.posterior(list(s)) for s in _PASSAGE]
    d_floor = max(_maxdiff(a, b) for a, b in zip(floor_fwd, floor_2nd))
    chk("W0 THE DEFECT: on the UNPATCHED organ a second consumer's re-tag changes the belief (order-dependent)",
        d_floor > 1e-9, "max |dP| between the 1st and the 2nd consumer's read = %.3e" % d_floor)
    lc_floor_clock = lc._reg.sent_no
    chk("W0b THE DEFECT: the ACT-R clock counts CALLS, not sentences (2 consumers x %d sentences)" % len(_PASSAGE),
        lc_floor_clock == 2 * len(_PASSAGE), "clock=%d after %d sentences" % (lc_floor_clock, len(_PASSAGE)))

    # ---------- install the patch ----------
    LC = install()
    lc = LC.get()

    # W1: a READ as of sentence k reproduces the FEED's own belief about sentence k, byte-identically
    lc.new_document()
    feed = lc.feed_passage(_PASSAGE)
    reads = [lc.posterior(list(s)) for s in _PASSAGE]
    d1 = max(_maxdiff(a, b) for a, b in zip(feed, reads))
    chk("W1 an AS-OF-k READ reproduces the in-order FEED's own belief about sentence k (max |dP| = 0)",
        d1 == 0.0, "max |dP| = %.3e over %d sentences" % (d1, len(_PASSAGE)))

    # W2: a read files nothing and advances nothing
    clock0 = lc._reg.sent_no
    cards0 = {w: (len(c["ev"]), c["pf"]) for w, c in lc._reg.h.items()}
    for s in _PASSAGE * 3:
        lc.tag(list(s))
        lc.tag_with_posterior([w.lower() for w in s])
    cards1 = {w: (len(c["ev"]), c["pf"]) for w, c in lc._reg.h.items()}
    chk("W2 a READ writes nothing and advances nothing (clock and every file card unchanged after 36 reads)",
        lc._reg.sent_no == clock0 and cards0 == cards1,
        "clock %d->%d  cards equal=%s  reads=%d feeds=%d" % (clock0, lc._reg.sent_no, cards0 == cards1,
                                                             lc._reg.n_read, lc._reg.n_feed))

    # W3: ORDER-INVARIANCE -- consumers asking in any order get the same answer
    import random as _r
    order = list(range(len(_PASSAGE)))
    _r.Random(7).shuffle(order)
    shuffled = {i: lc.posterior(list(_PASSAGE[i])) for i in order}
    d3 = max(_maxdiff(feed[i], shuffled[i]) for i in range(len(_PASSAGE)))
    chk("W3 ORDER-INVARIANCE: consumers that ask in a shuffled order get exactly the feed's belief (max |dP| = 0)",
        d3 == 0.0, "max |dP| = %.3e" % d3)

    # W4: strictly in order -- the belief about sentence k cannot see sentence k+1..N
    lc.new_document()
    partial = []
    for k, s in enumerate(_PASSAGE):
        partial.append(lc.posterior(list(s), observe=True))
    lc.new_document()
    prefix = []
    for k in range(len(_PASSAGE)):
        lc.new_document()
        for s in _PASSAGE[:k]:
            lc.posterior(list(s), observe=True)
        prefix.append(lc.posterior(list(_PASSAGE[k]), observe=True))
    d4 = max(_maxdiff(partial[k], prefix[k]) for k in range(len(_PASSAGE)))
    chk("W4 STRICTLY IN ORDER: the belief about sentence k equals the belief of a reader that has read only 0..k-1",
        d4 == 0.0, "max |dP| = %.3e" % d4)

    # W5: INERT without new_document() -- a single-sentence consumer is byte-identical to the unpatched organ
    restore()
    import hdlab.lexical_categories as LC0
    lc0 = LC0.get()
    base = [lc0.posterior(list(s)) for s in _PASSAGE]
    LCp = install()
    lcp = LCp.get()
    pat = [lcp.posterior(list(s)) for s in _PASSAGE]
    d5 = max(_maxdiff(a, b) for a, b in zip(base, pat))
    chk("W5 INERT with no new_document(): byte-identical to the unpatched organ for every single-sentence consumer",
        d5 == 0.0, "max |dP| = %.3e over %d sentences" % (d5, len(_PASSAGE)))

    # W6: the ACT-R clock now counts SENTENCES
    lcp.new_document()
    lcp.feed_passage(_PASSAGE)
    for s in _PASSAGE * 4:
        lcp.tag(list(s))
    chk("W6 the ACT-R clock counts SENTENCES OF THE PASSAGE, not calls into the organ",
        lcp._reg.sent_no == len(_PASSAGE),
        "clock=%d after %d sentences and %d further reads" % (lcp._reg.sent_no, len(_PASSAGE), lcp._reg.n_read))

    # W7: the passage generation changes per passage (the memo key)
    g0 = LCp.register_generation()
    lcp.new_document()
    g1 = LCp.register_generation()
    chk("W7 the passage GENERATION bumps at each passage boundary (the affect memo's key)", g1 == g0 + 1,
        "gen %d -> %d" % (g0, g1))

    # W8: the Katz/Gelman KIND symbols still fire, and the symbol is read BEFORE the token is filed
    lcp.new_document()
    lcp.feed_passage(_PASSAGE)
    reg = lcp._reg
    reg.begin([w.lower() for w in _PASSAGE[4]], False)     # as of sentence 4
    s_souter = reg.symbol("souter")
    s_dax = reg.symbol("dax")
    reg.commit(False)
    reg.begin([w.lower() for w in _PASSAGE[0]], False)     # as of sentence 0 -- nothing filed yet
    s_souter0 = reg.symbol("souter")
    reg.commit(False)
    chk("W8 the file-card symbols are read AS OF the sentence: 'souter' is a repeat at s4 and a FIRST mention at s0",
        s_souter.startswith("e_rep") and s_souter0 == "e_first",
        "s4('souter')=%s  s4('dax')=%s  s0('souter')=%s" % (s_souter, s_dax, s_souter0))

    # W9: THE FLOOR IDENTITY -- `observe=True` on EVERY call reproduces the unpatched organ byte-identically, so
    #     the accuracy harness's floor is the live path and not a re-implementation of it.
    restore()
    import hdlab.lexical_categories as LC0b
    lc0 = LC0b.get()
    lc0.new_document()
    ref = []
    for _p in range(3):
        ref.append([lc0.posterior(list(s)) for s in _PASSAGE])
    LCq = install()
    lcq = LCq.get()
    lcq.new_document()
    sim = []
    for _p in range(3):
        sim.append([lcq.posterior(list(s), observe=True) for s in _PASSAGE])
    d9 = max(_maxdiff(ref[p][k], sim[p][k]) for p in range(3) for k in range(len(_PASSAGE)))
    chk("W9 FLOOR IDENTITY: observe=True on every call reproduces the UNPATCHED organ (3 consumer passes, max |dP| = 0)",
        d9 == 0.0, "max |dP| = %.3e" % d9)

    # W10: THE OFFLINE ACCRUAL IS UNCHANGED -- the entity table log P(E | c) accrued through the new in-order API is
    #      byte-identical to the one the pre-pri-112 accrual builds, on a real multi-document corpus slice. If this
    #      moved, every number pri-104 measured would be measured against a different table.
    def _accrue_counts(mod, docs):
        m = mod.LexicalCategories(order=1, use_shape=False)
        for d in docs:
            m.accrue(d)
        m.finalize()
        m.accrue_entity_docs(docs)
        return ({t: dict(m.entc[t]) for t in sorted(m.entc)}, {t: dict(m.entc_u[t]) for t in sorted(m.entc_u)})

    acc_docs = read_corpus("gum", stride=40)[:6]
    restore()
    import hdlab.lexical_categories as LC0c
    ref_counts = _accrue_counts(LC0c, acc_docs)
    LCr = install()
    pat_counts = _accrue_counts(LCr, acc_docs)
    chk("W10 the OFFLINE ENTITY TABLE accrued through the new in-order API is byte-identical to the incumbent's",
        ref_counts == pat_counts,
        "%d documents; entc symbols %d, entc_u symbols %d" % (
            len(acc_docs), sum(len(v) for v in ref_counts[0].values()), sum(len(v) for v in ref_counts[1].values())))

    # W11: ARM B (the passage register) is ALSO read as of the sentence -- a read about sentence k must see the
    #      convention the comprehender had established by k, never the whole passage's.
    LCb = install()
    LCb.ENT_REG_LIVE_DOC = True
    lcb = LCb.get()
    lcb.new_document()
    fedb = lcb.feed_passage(_PASSAGE)
    readb = [lcb.posterior(list(s)) for s in _PASSAGE]
    d11 = max(_maxdiff(a, b) for a, b in zip(fedb, readb))
    n_stamped = sum(len(v) for v in lcb._doc_shape.values())
    chk("W11 ARM B (the passage register) is read AS OF the sentence: a late read reproduces the feed's own belief",
        d11 == 0.0 and n_stamped > 0,
        "max |dP| = %.3e; %d sentence-stamped entries over %d shape symbols" % (
            d11, n_stamped, len(lcb._doc_shape)))
    prefixb = []
    for k in range(len(_PASSAGE)):
        lcb.new_document()
        lcb.feed_passage(_PASSAGE[:k])
        prefixb.append(lcb.posterior(list(_PASSAGE[k]), observe=True))
    d11b = max(_maxdiff(fedb[k], prefixb[k]) for k in range(len(_PASSAGE)))
    chk("W11b ARM B is STRICTLY IN ORDER: sentence k's belief equals that of a reader that has read only 0..k-1",
        d11b == 0.0, "max |dP| = %.3e" % d11b)
    LCb.ENT_REG_LIVE_DOC = (os.environ.get("HDLAB_LC_ENT_REG_LIVE_DOC", "0") == "1")

    # W12: the board's GUM loader opens a passage and feeds it once, in order (it never did).
    install()
    GCp = install_gum_coref()
    import hdlab.lexical_categories as LCg

    class _Tok:
        __slots__ = ("gidx", "sent", "idx", "form")

        def __init__(self, g, s_, i, f):
            self.gidx, self.sent, self.idx, self.form = g, s_, i, f

    gtoks = []
    g = 0
    for si, sent in enumerate(_PASSAGE):
        for i, w in enumerate(sent):
            gtoks.append(_Tok(g, si, i, w))
            g += 1
    pred = GCp.organ_tags(gtoks)
    reg = LCg.get()._reg
    chk("W12 the board's GUM loader opens the passage and feeds it ONCE in order (clock = sentences, cards written)",
        reg is not None and reg.sent_no == len(_PASSAGE) and len(reg.h) > 0 and len(pred) == len(gtoks),
        "clock=%d for %d sentences, %d file cards, %d tokens tagged" % (
            (reg.sent_no if reg else -1), len(_PASSAGE), (len(reg.h) if reg else 0), len(pred)))
    restore_gum_coref()

    print("\n%d/%d witnesses passed  (%.1fs)" % (PASS, PASS + FAIL, time.time() - t0), flush=True)
    return FAIL == 0


# =====================================================================================================================
# 3. THE ACCURACY HARNESS -- GUM (modern, real documents). Floor = the POLLUTED multi-consumer call pattern.
# =====================================================================================================================

GUM_DIR = os.path.join(REPO, "data", "corpora", "gum", "conllu")
EWT_TEST = os.path.join(REPO, "data", "corpora", "ud_english_ewt", "en_ewt-ud-test.conllu")
# THE LIVE CALL PATTERN, measured (data/hook_state/diag_w3a9.log): FIVE requests for the same sentence in ONE read --
# referent_per_np:122 (via coref.parse_litbank_conll), referent_per_np:149, the reader's affect path, coref:216 via
# space_reader:248, and situation_reader:2679 (predict_revise). Each one FILED the sentence and advanced the clock.
N_CONSUMER_PASSES = 5


def read_docs(path: str, column: int = 3):
    """One UD/GUM file -> its DOCUMENTS (`# newdoc id`), each a list of sentences of (word, gold category)."""
    docs, cur_doc, cur = [], [], []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("# newdoc"):
                if cur:
                    cur_doc.append(cur); cur = []
                if cur_doc:
                    docs.append(cur_doc)
                cur_doc = []
                continue
            if not line:
                if cur:
                    cur_doc.append(cur); cur = []
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


def read_corpus(name: str, stride: int = 1, cap: int = 0):
    """gum / gentle = modern multi-genre documents (the well-powered population); ewt = the UD-EWT TEST split.
    All are the RULER only -- never read while learning."""
    if name == "ewt":
        docs = read_docs(EWT_TEST)
    else:
        pref = "GUM_" if name == "gum" else "GENTLE_"
        docs = []
        for f in sorted(glob.glob(os.path.join(GUM_DIR, pref + "*.conllu"))):
            docs.extend(read_docs(f))
    if stride > 1:
        docs = docs[::stride]
    return docs[:cap] if cap else docs


def _doc_stats(pred_per_sent, doc, vocab):
    """Per-document hit counts on four populations: all / unseen / repeat-mention unseen PROPN|NOUN (the pri-104 bar
    population) / first-mention unseen PROPN|NOUN, plus the PROPN<->NOUN confusion count."""
    seen_in_doc = set()
    a_h = a_n = u_h = u_n = r_h = r_n = f_h = f_n = 0
    pn = 0
    for si, sent in enumerate(doc):
        pred = pred_per_sent[si]
        for i, (w, g) in enumerate(sent):
            wl = w.lower()
            p = pred[i]
            hit = int(p == g)
            a_h += hit; a_n += 1
            if wl not in vocab:
                u_h += hit; u_n += 1
                if g in ("PROPN", "NOUN"):
                    if wl in seen_in_doc:
                        r_h += hit; r_n += 1
                    else:
                        f_h += hit; f_n += 1
            if (g == "PROPN" and p == "NOUN") or (g == "NOUN" and p == "PROPN"):
                pn += 1
            seen_in_doc.add(wl)
    return [a_h, a_n, u_h, u_n, r_h, r_n, f_h, f_n, pn]


def _boot(A, B, i_h, i_n, n_boot=2000, seed=0):
    """Paired bootstrap over DOCUMENTS (the discourse unit) on the delta (B - A) of a hits/denominator ratio."""
    A = np.asarray(A, dtype=float); B = np.asarray(B, dtype=float)
    n = len(A)
    rng = np.random.default_rng(seed)
    d = np.empty(n_boot)
    for r in range(n_boot):
        ix = rng.integers(0, n, n)
        ta, tb = A[ix].sum(axis=0), B[ix].sum(axis=0)
        d[r] = tb[i_h] / max(1.0, tb[i_n]) - ta[i_h] / max(1.0, ta[i_n])
    obs = B[:, i_h].sum() / max(1.0, B[:, i_n].sum()) - A[:, i_h].sum() / max(1.0, A[:, i_n].sum())
    lo, hi = np.percentile(d, [2.5, 97.5])
    return {"delta": round(float(obs), 5), "ci95": [round(float(lo), 5), round(float(hi), 5)],
            "half_width": round(float(hi - lo) / 2, 5), "CIsep": bool(lo > 0 or hi < 0), "n_docs": n,
            "denom": int(B[:, i_n].sum())}


def _acc(rows, i_h, i_n):
    R = np.asarray(rows, dtype=float)
    return round(float(R[:, i_h].sum() / max(1.0, R[:, i_n].sum())), 4)


def _tags_of(lc, mat):
    return [lc.tags[int(np.argmax(mat[i]))] for i in range(mat.shape[0])]


def accuracy(corpus="gum", stride=2, cap=0, n_boot=2000, seed=0):
    """FLOOR = the live path: N_CONSUMER_PASSES in-order passes over the document, each FILING the register and
    advancing the clock (what the five consumers do today). ARM = the register fed ONCE in order, everything else a
    read AS OF its sentence. TWIN = the register fed in a RANDOM sentence order (the discourse history destroyed,
    the symbol distribution preserved), then read as of the sentence. The INPUT is identical in every arm (cased
    tokens), so the only thing that differs is the register discipline."""
    import hdlab.lexical_categories as LC
    lc = LC.get()
    vocab = lc.vocab
    docs = read_corpus(corpus, stride=stride, cap=cap)
    rng = np.random.default_rng(seed)
    floor_rows, arm_rows, twin_rows = [], [], []
    consumer_rows = [[] for _ in range(N_CONSUMER_PASSES)]
    n_disagree = n_tok = 0
    t0 = time.time()
    for di, doc in enumerate(docs):
        words = [[w for w, _ in s] for s in doc]
        # ---- FLOOR: the polluted multi-consumer pattern. `observe=True` on EVERY call reproduces the unpatched
        #      organ exactly -- it files the sentence and advances the clock, and the symbol is read against every
        #      card filed so far, which is what the old `symbol` did (asserted byte-identical by witness W9). ----
        lc.new_document()
        passes = []
        for _p in range(N_CONSUMER_PASSES):
            passes.append([_tags_of(lc, lc.posterior(list(s), observe=True)) for s in words])
        for pi in range(N_CONSUMER_PASSES):
            consumer_rows[pi].append(_doc_stats(passes[pi], doc, vocab))
        floor_rows.append(consumer_rows[0][-1])
        for si in range(len(words)):
            for ti in range(len(words[si])):
                n_tok += 1
                n_disagree += int(len({passes[p][si][ti] for p in range(N_CONSUMER_PASSES)}) > 1)
        # ---- ARM: fed once, in order; every consumer reads as of its sentence ----
        lc.new_document()
        fed = [_tags_of(lc, m) for m in lc.feed_passage(words)]
        arm_rows.append(_doc_stats(fed, doc, vocab))
        # ---- TWIN: the register fed in a RANDOM sentence order ----
        lc.new_document()
        order = list(range(len(words)))
        rng.shuffle(order)
        for k in order:
            lc.posterior(list(words[k]), observe=True)
        tw = [_tags_of(lc, lc.posterior(list(s))) for s in words]
        twin_rows.append(_doc_stats(tw, doc, vocab))
        if (di + 1) % 20 == 0:
            print("    %d/%d docs  %.0fs" % (di + 1, len(docs), time.time() - t0), flush=True)
    names = ["all", "unseen", "repeat", "first"]
    idx = {"all": (0, 1), "unseen": (2, 3), "repeat": (4, 5), "first": (6, 7)}
    res = {"corpus": corpus, "stride": stride, "n_docs": len(docs),
           "n_tokens": int(np.asarray(floor_rows)[:, 1].sum()),
           "file_all": os.environ.get("HDLAB_LC_ENT_REG_FILE_ALL", "0"),
           "grain": os.environ.get("HDLAB_LC_ENT_REG_GRAIN", "token"),
           "ent_kappa": os.environ.get("HDLAB_LC_ENT_KAPPA", "2.0"),
           "consumer_disagreement": {"tokens": n_tok, "disagreeing": n_disagree,
                                     "rate": round(n_disagree / max(1, n_tok), 5)},
           "floor": {}, "arm": {}, "twin": {}, "arm_minus_floor": {}, "twin_minus_floor": {},
           "consumer_slots": [], "pn_confusions": {}}
    for nm in names:
        h, n = idx[nm]
        res["floor"][nm] = _acc(floor_rows, h, n)
        res["arm"][nm] = _acc(arm_rows, h, n)
        res["twin"][nm] = _acc(twin_rows, h, n)
        res["arm_minus_floor"][nm] = _boot(floor_rows, arm_rows, h, n, n_boot=n_boot)
        res["twin_minus_floor"][nm] = _boot(floor_rows, twin_rows, h, n, n_boot=n_boot)
    for pi in range(N_CONSUMER_PASSES):
        res["consumer_slots"].append({"pass": pi + 1,
                                      "all": _acc(consumer_rows[pi], 0, 1),
                                      "unseen": _acc(consumer_rows[pi], 2, 3),
                                      "repeat": _acc(consumer_rows[pi], 4, 5),
                                      "pn": int(np.asarray(consumer_rows[pi])[:, 8].sum())})
    for nm, rows in (("floor", floor_rows), ("arm", arm_rows), ("twin", twin_rows)):
        res["pn_confusions"][nm] = int(np.asarray(rows)[:, 8].sum())
    res["seconds"] = round(time.time() - t0, 1)
    return res


# =====================================================================================================================
# 4. THE BAR -- REPEATABILITY through the REAL reader (12 LitBank documents, two fresh readers, one process).
#    LitBank is 19c: this is a DETERMINISM measurement, never an accuracy number.
# =====================================================================================================================

def _fields(sm):
    """Every field the W3a witness compares, plus the goal identity and the coref accuracy."""
    gr = getattr(sm, "goal_register", None)
    return {
        "events": [(str(e.predicate), str(e.agent), str(e.patient), e.global_idx) for e in sm.events],
        "entity_states": [(s.holder, s.property, s.htype, s.sent_idx) for s in sm.entity_states],
        "causal_links": [(cl.sent_idx, cl.cause, cl.outcome, cl.method) for cl in sm.causal_links],
        "timeline_order": list(sm.timeline_order),
        "timeline_frames": [tuple(getattr(f, "chrono_order", [])) for f in sm.timeline_frames],
        "goal_heads": sorted((str(g.goal_head), str(g.goal_text), g.kind, g.status, g.sent_idx, g.negated)
                             for g in gr.goals) if gr is not None else [],
        "coref_acc": None if sm.coref_acc is None else round(float(sm.coref_acc), 10),
    }


def repeat(n_docs=12, patched=True):
    """R1: the same document read TWICE by two fresh readers in ONE process must be byte-identical on every field.
    R2: the W3a witness configuration exactly (graded_pick ON vs OFF): the coref-INDEPENDENT dimensions must be
    byte-identical. Run once per arm, each in its own process."""
    if patched:
        install()
        install_reader()
    from hdlab.situation_reader import SituationReader, MEM_SEED
    from hdlab.event_centrality_coref import EVENT_N_DIM, EventCentralityReader
    import experiments.exp_referent_coref_linking_v1 as L
    gaz = L.load_given_gazetteer()
    conll = sorted(glob.glob(os.path.join(L.NC.CONLL_DIR, "*.conll")))[:n_docs]

    # ---- R1: two identical fresh readers ----
    r1 = SituationReader(gaz=gaz)
    r2 = SituationReader(gaz=gaz)
    same = 0
    diffs = []
    t0 = time.time()
    for p in conll:
        a = _fields(r1.read(p))
        r2._read_parse_cache = {}
        b = _fields(r2.read(p))
        if a == b:
            same += 1
        else:
            diffs.append({"doc": os.path.basename(p),
                          "fields": sorted(k for k in a if a[k] != b[k]),
                          "n_events": [len(a["events"]), len(b["events"])]})
    t_r1 = time.time() - t0

    # ---- R2: the W3a witness configuration (graded_pick ON vs OFF) ----
    r_on = SituationReader(gaz=gaz)
    r_off = SituationReader(gaz=gaz)
    r_off.reader_ec = EventCentralityReader(n_dim=EVENT_N_DIM, mem_seed=MEM_SEED, graded_pick=False)
    assert r_on.reader_ec.graded_pick is True and r_off.reader_ec.graded_pick is False
    indep_keys = ("events", "entity_states", "causal_links", "timeline_order", "timeline_frames")
    w3a = w3b = 0
    w3_diffs = []
    for p in conll:
        a = _fields(r_on.read(p))
        r_off._read_parse_cache = {}
        b = _fields(r_off.read(p))
        ok = all(a[k] == b[k] for k in indep_keys)
        w3a += int(ok)
        w3b += int(a["goal_heads"] == b["goal_heads"])
        if not ok:
            w3_diffs.append({"doc": os.path.basename(p),
                             "fields": sorted(k for k in indep_keys if a[k] != b[k]),
                             "n_events": [len(a["events"]), len(b["events"])]})
    return {"arm": "patched" if patched else "floor", "n_docs": len(conll),
            "R1_identical": same, "R1_diffs": diffs, "R1_seconds": round(t_r1, 1),
            "W3a_identical": w3a, "W3a_diffs": w3_diffs, "W3b_goalheads_identical": w3b,
            "seconds": round(time.time() - t0, 1)}


# ---------------------------------------------------------------------------------------------------------------------
# THE ACT-R LEVER (phase 4). The card's recency is read as ONE BIT off the LAST mention: `|r` if the card was touched
# within ENT_RECENCY sentences, `|d` otherwise. The brain's quantity is not that. Anderson & Schooler (1991) / Anderson
# (2007): the base-level activation of a declarative chunk is
#        B_i = ln SUM_j (t - t_j)^(-d)
# a SUM over EVERY presentation with a power-law decay -- a chunk mentioned five times twenty sentences ago is more
# available than one mentioned once two sentences ago, and the one-bit-off-the-last-mention read cannot express that.
# The incumbent card could not compute it: it stored only `last`. The as-of card stores EVERY filing time (it has to,
# to answer as of sentence k), so the ACT-R sum is now a pure function of what the register already keeps. The symbol
# alphabet must stay a finite set of cells (the table is counts), so B is discretised into ACTR_BINS levels. This
# needs the entity table RE-ACCRUED over the new alphabet, which is an asset build, so it is measured here and
# reported as a lead -- it is not in the shipped diff.
ACTR_ON = False
ACTR_D = 0.5
ACTR_CUTS = (-0.7, 0.0)
ACTR_BINS = 3          # 3 = a three-level activation alphabet; 2 = the incumbent's alphabet SIZE with the ACT-R
                       #     quantity in place of the one-bit recency test (the control that separates 'the sum is
                       #     the wrong quantity' from 'the finer alphabet is too sparse to estimate')
TRAIN = os.path.join(REPO, "data", "corpora", "ud_english_ewt", "en_ewt-ud-train.conllu")


def _symbol_actr(self, wl):
    """`DiscourseRegister.symbol` with ACT-R base-level activation in place of the one-bit recency test."""
    import math
    k = self._as_of
    c = self.h.get(wl)
    n = 0
    kind = False
    deff = False
    j = 0
    if c is not None and c["ev"]:
        from bisect import bisect_left
        j = bisect_left(c["ev"], (k,))
        if j:
            n = j
            _last, kind, deff = c["ev"][j - 1]
    ov = self._ov.get(wl) if self._ov else None
    if ov is not None:
        n += 1
        kind = kind or ov["k"]
        deff = deff or ov["d"]
    if n == 0:
        return "e_first"
    if (c is not None and c["pf"] is not None and c["pf"] < k) or (ov is not None and ov["p"]):
        base = "e_rep_plural"
    elif kind:
        base = "e_rep_indef"
    elif deff:
        base = "e_rep_def"
    else:
        base = "e_rep_bare"
    tot = 0.0
    if j:
        for t, _a, _b in c["ev"][:j]:
            tot += (k - t + 1.0) ** (-ACTR_D)
    if ov is not None:
        tot += 1.0
    B = math.log(tot) if tot > 0 else -9.9
    lo, hi = ACTR_CUTS
    if ACTR_BINS == 2:
        return base + ("|d" if B < hi else "|r")     # same alphabet SIZE as the incumbent, ACT-R quantity
    return base + ("|a1" if B < lo else ("|a2" if B < hi else "|a3"))


def build_entc(actr: bool, d: float = 0.5, cuts=(-0.7, 0.0), bins: int = 3):
    """Re-accrue the entity table log P(E | c) over the chosen symbol alphabet, from the SAME offline supply the live
    asset was built from (UD-EWT train, document boundaries kept). Everything else in the model is the live asset."""
    global ACTR_ON, ACTR_D, ACTR_CUTS, ACTR_BINS
    import hdlab.lexical_categories as LC
    ACTR_D, ACTR_CUTS, ACTR_BINS = d, cuts, bins
    sym0 = LC.DiscourseRegister.symbol
    if actr:
        LC.DiscourseRegister.symbol = _symbol_actr
    try:
        m = LC.LexicalCategories.load()
        m.entc.clear()
        m.entc_u.clear()
        m.accrue_entity_docs(read_docs(TRAIN))
        m.finalize()
    finally:
        if actr:
            LC.DiscourseRegister.symbol = sym0
    m._actr = bool(actr)
    return m


def score_model(m, docs, vocab, actr: bool = False, d: float = 0.5, cuts=(-0.7, 0.0), bins: int = 3):
    """One in-order feed per document (the arm's own read discipline), scored on the four populations."""
    global ACTR_D, ACTR_CUTS, ACTR_BINS
    import hdlab.lexical_categories as LC
    ACTR_D, ACTR_CUTS, ACTR_BINS = d, cuts, bins
    sym0 = LC.DiscourseRegister.symbol
    if actr:
        LC.DiscourseRegister.symbol = _symbol_actr
    rows = []
    try:
        for doc in docs:
            words = [[w for w, _ in s] for s in doc]
            m.new_document()
            fed = [_tags_of(m, mm) for mm in m.feed_passage(words)]
            rows.append(_doc_stats(fed, doc, vocab))
    finally:
        if actr:
            LC.DiscourseRegister.symbol = sym0
    return rows


def actr_sweep(corpus="gum", stride=2, cap=0, n_boot=2000):
    """FLOOR = the incumbent 2-bin recency alphabet, table RE-ACCRUED here so the two arms differ only in the
    alphabet (never a table pasted from another build). ARMS = the ACT-R base-level activation, decay and cut points
    swept, never adopted."""
    import hdlab.lexical_categories as LC
    docs = read_corpus(corpus, stride=stride, cap=cap)
    m0 = build_entc(False)
    vocab = m0.vocab
    base_rows = score_model(m0, docs, vocab, actr=False)
    _s0 = sorted({x for c in m0.entc.values() for x in c})
    out = {"corpus": corpus, "n_docs": len(docs), "arms": {},
           "floor_cells": {"n_symbols": len(_s0),
                           "counts_per_cell": round(sum(sum(c.values()) for c in m0.entc.values())
                                                    / max(1, len(_s0) * len(m0.tags)), 1)},
           "floor": {"all": _acc(base_rows, 0, 1), "unseen": _acc(base_rows, 2, 3),
                     "repeat": _acc(base_rows, 4, 5), "first": _acc(base_rows, 6, 7),
                     "pn": int(np.asarray(base_rows)[:, 8].sum())}}
    out["cells"] = {}
    for name, d, cuts, bins in (("actr3_d05_c1", 0.5, (-0.7, 0.0), 3), ("actr3_d05_c2", 0.5, (-1.2, -0.3), 3),
                                ("actr3_d10_c1", 1.0, (-1.2, -0.3), 3),
                                ("actr2_d05", 0.5, (-0.7, 0.0), 2), ("actr2_d10", 1.0, (-0.7, -0.3), 2)):
        m1 = build_entc(True, d=d, cuts=cuts, bins=bins)
        rows = score_model(m1, docs, vocab, actr=True, d=d, cuts=cuts, bins=bins)
        syms = sorted({x for c in m1.entc.values() for x in c})
        out["cells"][name] = {"n_symbols": len(syms),
                              "counts_per_cell": round(sum(sum(c.values()) for c in m1.entc.values())
                                                       / max(1, len(syms) * len(m1.tags)), 1)}
        out["arms"][name] = {
            "d": d, "cuts": list(cuts), "bins": bins,
            "all": _acc(rows, 0, 1), "unseen": _acc(rows, 2, 3), "repeat": _acc(rows, 4, 5),
            "first": _acc(rows, 6, 7), "pn": int(np.asarray(rows)[:, 8].sum()),
            "delta_all": _boot(base_rows, rows, 0, 1, n_boot=n_boot),
            "delta_unseen": _boot(base_rows, rows, 2, 3, n_boot=n_boot),
            "delta_repeat": _boot(base_rows, rows, 4, 5, n_boot=n_boot),
            "delta_first": _boot(base_rows, rows, 6, 7, n_boot=n_boot)}
        print("  %s  all %.4f unseen %.4f repeat %.4f pn %d" % (
            name, out["arms"][name]["all"], out["arms"][name]["unseen"],
            out["arms"][name]["repeat"], out["arms"][name]["pn"]), flush=True)
    return out


def file_all_ab(corpus="gum", stride=2, cap=0, n_boot=2000):
    """LEVER: close the TRAIN/READ FILING-POLICY mismatch. `accrue_entity_docs` opens a file card for EVERY token;
    the live read opened one only for tokens with no lexical entry, because the filing sat inside the unknown-word
    branch of `_log_emit`. A file card is a record that the comprehender MET a referring expression -- it does not
    depend on whether that expression is in the lexicon -- so filing every mention is the brain-foundational form AND
    the one the table was estimated on. The policy probe bounds it: 131 of 16,959 prior reads (0.77%) get a different
    symbol, dominated by -> e_rep_plural, the strongest cell in the table (P(PROPN)/P(NOUN) = 0.018/0.860). Both arms
    read IN ORDER; the only difference is which mentions get a card."""
    import hdlab.lexical_categories as LC
    lc = LC.get()
    vocab = lc.vocab
    docs = read_corpus(corpus, stride=stride, cap=cap)
    rows = {}
    for name, flag in (("file_unknown_only", False), ("file_every_mention", True)):
        LC.ENT_REG_FILE_ALL = flag
        rows[name] = []
        t0 = time.time()
        for doc in docs:
            words = [[w for w, _ in s] for s in doc]
            lc.new_document()
            rows[name].append(_doc_stats([_tags_of(lc, m) for m in lc.feed_passage(words)], doc, vocab))
        print("  %s  %.0fs" % (name, time.time() - t0), flush=True)
    LC.ENT_REG_FILE_ALL = False
    # THE ADJACENT DEFECT (checklist item 7). `experiments/gum_coref.organ_tags` -- the loader behind the board's
    # GUM coref / common_noun_coref / salience rows -- tags each document sentence by sentence IN READING ORDER but
    # never calls `new_document()`, so the entity-feedback arm is INERT there (`self._reg is None`) and pri-104's
    # landed capability does not reach those three board dimensions at all. This arm is what that loader gets.
    rows["no_new_document_inert"] = []
    t0 = time.time()
    for doc in docs:
        words = [[w for w, _ in s] for s in doc]
        lc._reg = None
        rows["no_new_document_inert"].append(
            _doc_stats([_tags_of(lc, lc.posterior(list(s))) for s in words], doc, vocab))
    print("  no_new_document_inert  %.0fs" % (time.time() - t0), flush=True)
    idx = {"all": (0, 1), "unseen": (2, 3), "repeat": (4, 5), "first": (6, 7)}
    out = {"corpus": corpus, "n_docs": len(docs), "floor": {}, "arm": {}, "arm_minus_floor": {},
           "pn_floor": int(np.asarray(rows["file_unknown_only"])[:, 8].sum()),
           "pn_arm": int(np.asarray(rows["file_every_mention"])[:, 8].sum())}
    out["inert"] = {}
    out["in_order_minus_inert"] = {}
    out["pn_inert"] = int(np.asarray(rows["no_new_document_inert"])[:, 8].sum())
    for nm, (h, n) in idx.items():
        out["floor"][nm] = _acc(rows["file_unknown_only"], h, n)
        out["arm"][nm] = _acc(rows["file_every_mention"], h, n)
        out["inert"][nm] = _acc(rows["no_new_document_inert"], h, n)
        out["arm_minus_floor"][nm] = _boot(rows["file_unknown_only"], rows["file_every_mention"], h, n, n_boot=n_boot)
        out["in_order_minus_inert"][nm] = _boot(rows["no_new_document_inert"], rows["file_unknown_only"], h, n,
                                                n_boot=n_boot)
    return out


def consumer_ab(corpus="gum", stride=2, cap=0, n_boot=2000):
    """THE HONEST NO-REGRESS NUMBER. Under the patch every consumer is served the IN-ORDER belief (consumer pass 1).
    Before it, consumers 2..5 -- which is four of the five, and includes the reader's affect path, space_reader's
    backbone and predict_revise -- were served a belief computed against a register that had ALREADY been written
    with the whole document (future_probe: 100% of first mentions handed a repeat symbol). This measures, on modern
    gold with a paired bootstrap over documents, exactly what those four consumers gain or lose by being moved onto
    the in-order belief. A loss here is a loss of an ORACLE, not of a capability, and it is reported as the true
    in-order number (checklist item 4)."""
    import hdlab.lexical_categories as LC
    lc = LC.get()
    vocab = lc.vocab
    docs = read_corpus(corpus, stride=stride, cap=cap)
    p1_rows, p2_rows = [], []
    t0 = time.time()
    for di, doc in enumerate(docs):
        words = [[w for w, _ in s] for s in doc]
        lc.new_document()
        p1 = [_tags_of(lc, lc.posterior(list(s), observe=True)) for s in words]      # the in-order belief
        p2 = [_tags_of(lc, lc.posterior(list(s), observe=True)) for s in words]      # what consumers 2..5 got
        p1_rows.append(_doc_stats(p1, doc, vocab))
        p2_rows.append(_doc_stats(p2, doc, vocab))
        if (di + 1) % 30 == 0:
            print("    %d/%d  %.0fs" % (di + 1, len(docs), time.time() - t0), flush=True)
    idx = {"all": (0, 1), "unseen": (2, 3), "repeat": (4, 5), "first": (6, 7)}
    out = {"corpus": corpus, "n_docs": len(docs), "seconds": round(time.time() - t0, 1),
           "consumers_2_to_5_polluted": {}, "all_consumers_in_order": {}, "in_order_minus_polluted": {},
           "pn_polluted": int(np.asarray(p2_rows)[:, 8].sum()), "pn_in_order": int(np.asarray(p1_rows)[:, 8].sum())}
    for nm, (h, n) in idx.items():
        out["consumers_2_to_5_polluted"][nm] = _acc(p2_rows, h, n)
        out["all_consumers_in_order"][nm] = _acc(p1_rows, h, n)
        out["in_order_minus_polluted"][nm] = _boot(p2_rows, p1_rows, h, n, n_boot=n_boot)
    return out


def future_probe(corpus="gum", stride=2, cap=0):
    """WHY THE POLLUTED REGISTER LOOKED BETTER ON SOME SLICES: IT WAS READING THE FUTURE. Consumer pass 1 meets each
    string for the first time in reading order, so a first mention reads `e_first` and the prior is SILENT there
    (ENT_SKIP_FIRST). By the time consumer pass 2 asks about sentence 0, pass 1 has already filed the WHOLE document,
    so every string that recurs ANYWHERE in the passage -- including later -- reads as a REPEAT at its first mention.
    That is not a discourse model; it is an oracle telling the organ 'this string comes back', which is precisely the
    fact the next-mention prior is supposed to PREDICT. This counts it: the share of prior reads that are `e_first`
    on each consumer pass, and the number of FIRST mentions handed a repeat symbol.

    It also measures the ORDER TWIN at the SYMBOL level, where the power is (the tag-level twin is diluted by every
    other cue in the organ): how many prior reads get a different symbol when the passage is fed in a random
    sentence order instead of in reading order."""
    import hdlab.lexical_categories as LC
    from collections import Counter
    lc = LC.get()
    vocab = lc.vocab
    docs = read_corpus(corpus, stride=stride, cap=cap)
    rng = np.random.default_rng(0)
    n = 0
    first_true = 0                       # prior reads that are genuinely a FIRST mention in reading order
    e_first_by_pass = Counter()
    future_leak = 0                      # a genuine first mention handed a REPEAT symbol by the polluted register
    twin_diff = 0
    for doc in docs:
        lows_doc = [[w.lower() for w, _ in s] for s in doc]
        # -- pass 1 (in order, fresh) and pass 2 (the same register, second consumer) --
        r = LC.DiscourseRegister()
        syms1 = []
        seen = set()
        for si, lows in enumerate(lows_doc):
            r.begin(lows, True)
            row = []
            for i, wl in enumerate(lows):
                if wl not in vocab:
                    row.append(r.symbol(wl))
                    r.note(lows, i)
                else:
                    row.append(None)
            syms1.append(row)
            r.commit(True, lows)
        for si, lows in enumerate(lows_doc):        # consumer pass 2 on the SAME (already fully written) register
            r.begin(lows, True)
            for i, wl in enumerate(lows):
                if wl not in vocab:
                    s2 = r.symbol(wl)
                    e_first_by_pass[("p2", s2.startswith("e_first"))] += 1
                    s1 = syms1[si][i]
                    e_first_by_pass[("p1", s1.startswith("e_first"))] += 1
                    n += 1
                    if s1.startswith("e_first"):
                        first_true += 1
                        if not s2.startswith("e_first"):
                            future_leak += 1
                    r.note(lows, i)
            r.commit(True, lows)
        # -- the ORDER TWIN at the symbol level --
        rt = LC.DiscourseRegister()
        order = list(range(len(lows_doc)))
        rng.shuffle(order)
        for k in order:
            lows = lows_doc[k]
            rt.begin(lows, True)
            for i, wl in enumerate(lows):
                if wl not in vocab:
                    rt.symbol(wl)
                    rt.note(lows, i)
            rt.commit(True, lows)
        for si, lows in enumerate(lows_doc):
            rt.begin(lows, False)
            for i, wl in enumerate(lows):
                if wl not in vocab:
                    if rt.symbol(wl) != syms1[si][i]:
                        twin_diff += 1
                    rt.note(lows, i)
            rt.commit(False)
    return {"corpus": corpus, "n_docs": len(docs), "n_prior_reads": n,
            "e_first_share_pass1_in_order": round(e_first_by_pass[("p1", True)] / max(1, n), 4),
            "e_first_share_pass2_polluted": round(e_first_by_pass[("p2", True)] / max(1, n), 4),
            "true_first_mentions": first_true,
            "first_mentions_handed_a_repeat_symbol_by_the_polluted_register": future_leak,
            "future_leak_rate_of_first_mentions": round(future_leak / max(1, first_true), 4),
            "order_twin_symbol_differences": twin_diff,
            "order_twin_symbol_difference_rate": round(twin_diff / max(1, n), 4)}


def gum_loader_ab(n_docs=None, n_boot=1000):
    """PHASE 7 (2i). THE BOARD'S GUM LOADER IS A CONSUMER OF THIS ORGAN AND IT NEVER OPENED A PASSAGE.
    `experiments/gum_coref.organ_tags` is the decision source for the board's `coref`, `common_noun_coref` and
    `salience` rows (HDLAB_GUM_DECISION defaults to "organ" since 2026-09-14, so those rows are gold-free and read
    the live organ). It tags each document sentence by sentence in reading order but never calls `new_document()`,
    so `self._reg is None` and pri-104's entity-feedback arm is INERT for all three. Both arms run in ONE process on
    the same documents; the only difference is the passage boundary + the one in-order feed."""
    install()
    import experiments.exp_board_coref_gum_v1 as BCG
    out = {}
    for name in ("inert_no_new_document", "passage_opened_and_fed_in_order"):
        if name.startswith("passage"):
            install_gum_coref()
        else:
            restore_gum_coref()
        t0 = time.time()
        row, detail = BCG.board_coref_modern_dimension(n_docs=n_docs)
        sal, _sd = BCG.board_salience_modern_dimension(n_docs=n_docs, n_boot=n_boot)
        out[name] = {"coref": row, "common_noun_coref": detail["common_noun"], "salience": sal,
                     "seconds": round(time.time() - t0, 1)}
        print("  %s  coref=%s common=%s salience=%s  %.0fs" % (
            name, row.get("model_acc"), detail["common_noun"].get("model_acc"), sal.get("model_acc"),
            time.time() - t0), flush=True)
    restore_gum_coref()
    return out


def armb_ab(corpus="gum", stride=2, cap=0, n_boot=2000):
    """PHASE 7 (2iii). ARM B -- the PASSAGE REGISTER -- wired to the in-order feed and read AS OF the sentence.
    `update_document_register` had no live caller anywhere in hdlab/ or tools/, so `_doc_shape` was always empty and
    ENT_THETA_DOC=100 was inert. Both arms read IN ORDER; the only difference is whether the settled belief is
    folded back into the passage's shape convention at each sentence boundary."""
    import hdlab.lexical_categories as LC
    lc = LC.get()
    vocab = lc.vocab
    docs = read_corpus(corpus, stride=stride, cap=cap)
    rows = {}
    touched = {"sentences": 0, "shape_symbols": set(), "stamped_entries": 0, "prior_reads_with_a_convention": 0}
    for name, flag in (("arm_b_off_inert", False), ("arm_b_on_as_of", True)):
        LC.ENT_REG_LIVE_DOC = flag
        rows[name] = []
        t0 = time.time()
        for doc in docs:
            words = [[w for w, _ in s] for s in doc]
            lc.new_document()
            rows[name].append(_doc_stats([_tags_of(lc, m) for m in lc.feed_passage(words)], doc, vocab))
            if flag:
                touched["sentences"] += len(words)
                touched["shape_symbols"] |= set(lc._doc_shape)
                touched["stamped_entries"] += sum(len(v) for v in lc._doc_shape.values())
        print("  %s  %.0fs" % (name, time.time() - t0), flush=True)
    LC.ENT_REG_LIVE_DOC = (os.environ.get("HDLAB_LC_ENT_REG_LIVE_DOC", "0") == "1")
    idx = {"all": (0, 1), "unseen": (2, 3), "repeat": (4, 5), "first": (6, 7)}
    out = {"corpus": corpus, "n_docs": len(docs), "floor": {}, "arm": {}, "arm_minus_floor": {},
           "pn_floor": int(np.asarray(rows["arm_b_off_inert"])[:, 8].sum()),
           "pn_arm": int(np.asarray(rows["arm_b_on_as_of"])[:, 8].sum()),
           "what_it_touches": {"sentences_folded_back": touched["sentences"],
                               "distinct_shape_symbols": len(touched["shape_symbols"]),
                               "sentence_stamped_entries": touched["stamped_entries"]}}
    for nm, (h, n) in idx.items():
        out["floor"][nm] = _acc(rows["arm_b_off_inert"], h, n)
        out["arm"][nm] = _acc(rows["arm_b_on_as_of"], h, n)
        out["arm_minus_floor"][nm] = _boot(rows["arm_b_off_inert"], rows["arm_b_on_as_of"], h, n, n_boot=n_boot)
    return out


def twin_arithmetic(corpus="gum", stride=2, cap=0):
    """PHASE 7 (1b). THE ARITHMETIC BEHIND 'the tag-level twin cannot separate'. Three quantities, measured, not
    asserted: (a) how much POSTERIOR MASS the entity prior actually moves per prior read, and on how many tokens it
    moves the ARGMAX at all -- that is the total tag-level budget the prior has; (b) how much of that budget the
    ORDER of the feed is responsible for (the shuffled-order twin's argmax flips against the in-order read); (c) the
    population and the bootstrap half-width, so the required effect size can be compared with the observed one.
    Each document is read three ways IN ORDER: with the prior inert, with the prior on, and with the register fed in
    a random sentence order and then read as of the sentence."""
    import hdlab.lexical_categories as LC
    lc = LC.get()
    docs = read_corpus(corpus, stride=stride, cap=cap)
    rng = np.random.default_rng(0)
    n_tok = n_unseen = 0
    flips_prior = flips_twin = 0
    mass = 0.0
    mass_n = 0
    pmax_off = pmax_on = 0.0
    t0 = time.time()
    for di, doc in enumerate(docs):
        words = [[w for w, _ in s] for s in doc]
        lc._reg = None                                    # the prior inert (exactly kappa 0)
        off = [lc.posterior(list(s)) for s in words]
        lc.new_document()
        on = lc.feed_passage(words)
        lc.new_document()                                 # the ORDER twin: same passage, shuffled feed order
        order = list(range(len(words)))
        rng.shuffle(order)
        for k in order:
            lc.posterior(list(words[k]), observe=True)
        tw = [lc.posterior(list(s)) for s in words]
        for si, sent in enumerate(doc):
            a, b, c = off[si], on[si], tw[si]
            for i, (w, _g) in enumerate(sent):
                n_tok += 1
                if w.lower() in lc.vocab:
                    continue                              # the prior is read only where there is no lexical entry
                n_unseen += 1
                mass += 0.5 * float(np.abs(b[i] - a[i]).sum())   # total variation distance, prior on vs inert
                mass_n += 1
                pmax_off += float(a[i].max())
                pmax_on += float(b[i].max())
                if int(a[i].argmax()) != int(b[i].argmax()):
                    flips_prior += 1
                if int(b[i].argmax()) != int(c[i].argmax()):
                    flips_twin += 1
        if (di + 1) % 30 == 0:
            print("    %d/%d  %.0fs" % (di + 1, len(docs), time.time() - t0), flush=True)
    return {"corpus": corpus, "n_docs": len(docs), "n_tokens": n_tok, "n_prior_reads": n_unseen,
            "mean_total_variation_moved_by_the_prior": round(mass / max(1, mass_n), 5),
            "mean_P_argmax_prior_inert": round(pmax_off / max(1, mass_n), 5),
            "mean_P_argmax_prior_on": round(pmax_on / max(1, mass_n), 5),
            "argmax_flips_caused_by_the_prior": flips_prior,
            "argmax_flip_rate_of_prior_reads": round(flips_prior / max(1, n_unseen), 5),
            "argmax_flips_caused_by_SHUFFLING_the_feed_order": flips_twin,
            "order_share_of_the_prior_budget": round(flips_twin / max(1, flips_prior), 4),
            "seconds": round(time.time() - t0, 1)}


def typing_handoff(n_docs=None):
    """THE HAND-OFF THE CATEGORY ORGAN'S GAIN DIES IN, counted end to end (2026-09-14 phase 7).

    The board's GUM rows do not read the category organ's posterior, or even its tag. They read a THREE-WAY
    mention type produced by `gum_coref._mention_type` / `_mention_type_organ`, which is a pure function of the
    argmax: PRON (or a pronoun-list form) -> "pronoun", PROPN -> "name", everything else -> "common". So every
    category distinction the organ makes among {NOUN, VERB, ADJ, ADV, NUM, ...} collapses to ONE symbol before
    the board sees it, and the only gain that can survive is one that moves a token ACROSS the PROPN / PRON /
    other boundary AND that token is a mention head.

    This measures each link: tokens whose argmax the passage register moves, how many of those are mention
    heads, and how many mention TYPES change as a result -- the three numbers that turn a +0.0101 tag-accuracy
    gain into nothing on a 3,024-item board row. Both arms are loaded in ONE process; the only difference is
    whether the loader opens a passage."""
    install()
    import experiments.gum_coref as G
    from experiments.exp_board_coref_gum_v1 import load_given_gazetteer
    gaz = load_given_gazetteer()
    out = {}
    tags = {}
    types = {}
    for name in ("inert_no_new_document", "passage_opened_and_fed_in_order"):
        if name.startswith("passage"):
            install_gum_coref()
        else:
            restore_gum_coref()
        t0 = time.time()
        docs = G.load_docs(gum_only=True, limit=n_docs, name_gazetteer=gaz, decision_source="organ")
        docs = [d for i, d in enumerate(docs) if i % 2 == 1]          # the board's TEST split (odd docs)
        tg = {}
        ty = {}
        for di, d in enumerate(docs):
            for t in d.toks:
                tg[(di, t.gidx)] = t.upos
            for mi, m in enumerate(d.mentions):
                ty[(di, mi)] = m.mtype
        tags[name] = tg
        types[name] = ty
        out[name] = {"n_docs": len(docs), "n_tokens": len(tg), "n_mentions": len(ty),
                     "seconds": round(time.time() - t0, 1)}
        print("  %s  %d docs / %d tokens / %d mentions  %.0fs" % (
            name, len(docs), len(tg), len(ty), time.time() - t0), flush=True)
    restore_gum_coref()
    a, b = tags["inert_no_new_document"], tags["passage_opened_and_fed_in_order"]
    ta, tb = types["inert_no_new_document"], types["passage_opened_and_fed_in_order"]
    from collections import Counter
    tag_flips = Counter()
    for k in a:
        if k in b and a[k] != b[k]:
            tag_flips[(a[k], b[k])] += 1
    type_flips = Counter()
    for k in ta:
        if k in tb and ta[k] != tb[k]:
            type_flips[(ta[k], tb[k])] += 1
    n_tag = sum(tag_flips.values())
    n_type = sum(type_flips.values())
    # how many of the argmax flips CAN cross the typing boundary at all
    crossing = sum(v for (x, y), v in tag_flips.items()
                   if ("PROPN" in (x, y)) or ("PRON" in (x, y)))
    out["handoff"] = {
        "tokens_compared": len(a),
        "argmax_flips_from_opening_the_passage": n_tag,
        "argmax_flip_rate": round(n_tag / max(1, len(a)), 6),
        "flips_that_cross_the_PROPN_or_PRON_boundary": crossing,
        "flips_invisible_to_the_typing_rule": n_tag - crossing,
        "mentions_compared": len(ta),
        "mention_TYPES_changed": n_type,
        "mention_type_change_rate": round(n_type / max(1, len(ta)), 6),
        "top_tag_flips": [["%s -> %s" % k, v] for k, v in tag_flips.most_common(8)],
        "mention_type_flips": [["%s -> %s" % k, v] for k, v in type_flips.most_common(8)],
        "note": ("the board's three GUM rows read ONLY this three-way type; every other category distinction the "
                 "organ makes is discarded at this hand-off"),
    }
    return out


def board(patched=True, n_boot=1000, caps=None):
    """THE BOARD A/B (phase 5). The board's `run()` is in-process, so the patch is installed BEFORE the board module
    is imported and every arm it builds therefore routes through the patched organs. Floor and arm are run in
    SEPARATE processes so no module-level state is shared between them."""
    if patched:
        install()
        install_reader()
    import experiments.exp_situation_model_qa_modern_v1 as B
    t0 = time.time()
    res = B.run(caps=caps or {"wic_mode": "full"}, n_boot=n_boot, write_metrics=False)
    rows = {}
    for k, v in (res.get("per_dimension") or {}).items():
        if isinstance(v, dict):
            rows[k] = {kk: v.get(kk) for kk in ("value", "score", "acc", "n", "ci", "ci95") if kk in v}
    return {"arm": "patched" if patched else "floor", "n_boot": n_boot, "caps": caps,
            "per_dimension": rows, "aggregate": res.get("aggregate_19c_free"),
            "new_board_arms": res.get("new_board_arms"), "seconds": round(time.time() - t0, 1)}


def policy_probe(corpus="gum", stride=2, cap=0):
    """THE TRAIN/READ FILING-POLICY MISMATCH, counted. `accrue_entity_docs` builds log P(E | c) with EVERY token
    filed into the file cards; the live read filed a card only for tokens with NO LEXICAL ENTRY (the prior's own
    read gate sits in the unknown-word branch of `_log_emit`, and the filing sat inside that branch too). The symbol
    function is the same either way -- what differs is which mentions ever get a card, so the symbol DISTRIBUTION at
    read time is not the one the table was estimated on. This counts the gap on the tokens where the prior is
    actually read (unseen tokens), with no forward-backward at all."""
    import hdlab.lexical_categories as LC
    lc = LC.get()
    vocab = lc.vocab
    docs = read_corpus(corpus, stride=stride, cap=cap)
    from collections import Counter
    read_sym, accr_sym, disagree = Counter(), Counter(), Counter()
    n = 0
    for doc in docs:
        r_read = LC.DiscourseRegister()
        r_all = LC.DiscourseRegister()
        for sent in doc:
            lows = [w.lower() for w, _ in sent]
            r_read.begin(lows, True)
            r_all.begin(lows, True)
            for i, (w, _g) in enumerate(sent):
                wl = lows[i]
                if wl not in vocab:                       # where the entity prior is actually read
                    sr = r_read.symbol(wl); sa = r_all.symbol(wl)
                    read_sym[sr] += 1
                    accr_sym[sa] += 1
                    n += 1
                    if sr != sa:
                        disagree[(sr, sa)] += 1
                    r_read.note(lows, i)                  # today's policy: only unknown tokens get a card
                r_all.note(lows, i)                       # the accrual's policy: every token gets a card
            r_read.commit(True, lows)
            r_all.commit(True, lows)
    def share(c):
        t = max(1, sum(c.values()))
        return {k: round(v / t, 4) for k, v in sorted(c.items(), key=lambda kv: -kv[1])}
    def base(c):
        b = Counter()
        for k, v in c.items():
            b[k.split("|")[0]] += v
        return share(b)
    return {"corpus": corpus, "n_docs": len(docs), "n_prior_reads": n,
            "read_policy_unknown_only": share(read_sym), "accrual_policy_file_all": share(accr_sym),
            "read_policy_base": base(read_sym), "accrual_policy_base": base(accr_sym),
            "symbol_disagreements": int(sum(disagree.values())),
            "symbol_disagreement_rate": round(sum(disagree.values()) / max(1, n), 5),
            "top_disagreements": [["%s -> %s" % k, v] for k, v in disagree.most_common(8)],
            "e_first_share_read": round(sum(v for k, v in read_sym.items() if k.startswith("e_first")) / max(1, n), 4),
            "e_first_share_accrual": round(sum(v for k, v in accr_sym.items() if k.startswith("e_first")) / max(1, n), 4)}


def trace(n_docs=3):
    """THE CHAIN TRACE, with counts. Read real documents through the REAL reader under the patch and count, per
    document: how many calls into the category organ are the ONE in-order FEED, how many are READS, how many reads
    asked about a token list the comprehender never advanced through (answered as of the passage so far), and how
    many of the reader's own tag-cache lookups the feed served."""
    install()
    install_reader()
    import hdlab.lexical_categories as LC
    from hdlab.situation_reader import SituationReader
    import experiments.exp_referent_coref_linking_v1 as L
    gaz = L.load_given_gazetteer()
    conll = sorted(glob.glob(os.path.join(L.NC.CONLL_DIR, "*.conll")))[:n_docs]
    r = SituationReader(gaz=gaz)
    rows = []
    for p in conll:
        t0 = time.time()
        sm = r.read(p)
        reg = LC.get()._reg
        n_sent = len(reg.sent_key)
        rows.append({"doc": os.path.basename(p), "sentences_fed": reg.n_feed, "distinct_sentences": n_sent,
                     "reads": reg.n_read, "reads_as_of_a_fed_sentence": reg.n_read - reg.n_read_miss,
                     "reads_never_fed": reg.n_read_miss, "clock": reg.sent_no,
                     "calls_per_sentence": round((reg.n_feed + reg.n_read) / max(1, n_sent), 2),
                     "events": len(sm.events), "seconds": round(time.time() - t0, 1)})
        print(json.dumps(rows[-1]), flush=True)
    return {"rows": rows,
            "total": {k: sum(x[k] for x in rows) for k in ("sentences_fed", "reads", "reads_never_fed", "events")}}


# =====================================================================================================================
# 5. main
# =====================================================================================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--diff", action="store_true", help="write the unified diff to --diff-out")
    ap.add_argument("--diff-out", default="")
    ap.add_argument("--accuracy", action="store_true")
    ap.add_argument("--repeat", action="store_true")
    ap.add_argument("--trace", action="store_true")
    ap.add_argument("--policy-probe", action="store_true")
    ap.add_argument("--board", action="store_true")
    ap.add_argument("--actr", action="store_true")
    ap.add_argument("--future-probe", action="store_true")
    ap.add_argument("--consumer-ab", action="store_true")
    ap.add_argument("--file-all-ab", action="store_true")
    ap.add_argument("--gum-loader-ab", action="store_true")
    ap.add_argument("--armb-ab", action="store_true")
    ap.add_argument("--twin-arithmetic", action="store_true")
    ap.add_argument("--typing-handoff", action="store_true")
    ap.add_argument("--board-smoke", action="store_true")
    ap.add_argument("--floor-arm", action="store_true", help="--repeat WITHOUT the patch (the floor)")
    ap.add_argument("--corpus", default="gum")
    ap.add_argument("--stride", type=int, default=2)
    ap.add_argument("--cap", type=int, default=0)
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--docs", type=int, default=12)
    ap.add_argument("--out-name", default="metrics.json")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)

    if a.diff:
        d = make_diff()
        p = a.diff_out or os.path.join(OUT, "passage_register_patch.diff")
        # the hdlab sources are CRLF on disk and the repo has core.autocrlf=false, so the patch's context lines must
        # carry CRLF too or `git apply` rejects every hunk. `_orig` reads in universal-newline mode (the anchors are
        # written with "\n"), so the diff is translated back on the way out.
        with open(p, "w", encoding="utf-8", newline="\r\n") as f:
            f.write(d)
        print("wrote %s (%d bytes)" % (p, len(d)))
        return

    if a.self_test:
        ok = self_test()
        with open(os.path.join(OUT, "metrics_selftest.json"), "w", encoding="utf-8") as f:
            json.dump({"result": {"passed": PASS, "failed": FAIL}}, f, indent=1)
        sys.exit(0 if ok else 1)

    if a.typing_handoff:
        r = typing_handoff(n_docs=a.cap or None)
        print(json.dumps(r, indent=1), flush=True)
        with open(os.path.join(OUT, "metrics_typing_handoff.json"), "w", encoding="utf-8") as f:
            json.dump({"result": r}, f, indent=1)
        return

    if a.gum_loader_ab:
        r = gum_loader_ab(n_docs=a.cap or None, n_boot=a.boot)
        print(json.dumps(r, indent=1), flush=True)
        with open(os.path.join(OUT, a.out_name), "w", encoding="utf-8") as f:
            json.dump({"result": r}, f, indent=1)
        return

    if a.armb_ab:
        install()
        r = armb_ab(corpus=a.corpus, stride=a.stride, cap=a.cap, n_boot=a.boot)
        print(json.dumps(r, indent=1), flush=True)
        with open(os.path.join(OUT, a.out_name), "w", encoding="utf-8") as f:
            json.dump({"result": r}, f, indent=1)
        return

    if a.twin_arithmetic:
        install()
        r = twin_arithmetic(corpus=a.corpus, stride=a.stride, cap=a.cap)
        print(json.dumps(r, indent=1), flush=True)
        with open(os.path.join(OUT, "metrics_twin_arithmetic.json"), "w", encoding="utf-8") as f:
            json.dump({"result": r}, f, indent=1)
        return

    if a.file_all_ab:
        install()
        r = file_all_ab(corpus=a.corpus, stride=a.stride, cap=a.cap, n_boot=a.boot)
        print(json.dumps(r, indent=1), flush=True)
        with open(os.path.join(OUT, a.out_name), "w", encoding="utf-8") as f:
            json.dump({"result": r}, f, indent=1)
        return

    if a.consumer_ab:
        install()
        r = consumer_ab(corpus=a.corpus, stride=a.stride, cap=a.cap, n_boot=a.boot)
        print(json.dumps(r, indent=1), flush=True)
        with open(os.path.join(OUT, a.out_name), "w", encoding="utf-8") as f:
            json.dump({"result": r}, f, indent=1)
        return

    if a.future_probe:
        install()
        r = future_probe(corpus=a.corpus, stride=a.stride, cap=a.cap)
        print(json.dumps(r, indent=1), flush=True)
        with open(os.path.join(OUT, "metrics_future_probe.json"), "w", encoding="utf-8") as f:
            json.dump({"result": r}, f, indent=1)
        return

    if a.actr:
        install()
        r = actr_sweep(corpus=a.corpus, stride=a.stride, cap=a.cap, n_boot=a.boot)
        print(json.dumps(r, indent=1), flush=True)
        with open(os.path.join(OUT, a.out_name), "w", encoding="utf-8") as f:
            json.dump({"result": r}, f, indent=1)
        return

    if a.board:
        caps = {"gum": 40, "ud": 300, "state": 300, "wic_mode": "smoke"} if a.board_smoke else {"wic_mode": "full"}
        r = board(patched=not a.floor_arm, n_boot=a.boot if a.board_smoke else 1000, caps=caps)
        print(json.dumps(r, indent=1), flush=True)
        with open(os.path.join(OUT, a.out_name), "w", encoding="utf-8") as f:
            json.dump({"result": r}, f, indent=1)
        return

    if a.policy_probe:
        install()
        r = policy_probe(corpus=a.corpus, stride=a.stride, cap=a.cap)
        print(json.dumps(r, indent=1), flush=True)
        with open(os.path.join(OUT, "metrics_policy_probe.json"), "w", encoding="utf-8") as f:
            json.dump({"result": r}, f, indent=1)
        return

    if a.trace:
        r = trace(n_docs=a.docs)
        print(json.dumps(r, indent=1), flush=True)
        with open(os.path.join(OUT, "metrics_trace.json"), "w", encoding="utf-8") as f:
            json.dump({"result": r}, f, indent=1)
        return

    if a.repeat:
        r = repeat(n_docs=a.docs, patched=not a.floor_arm)
        print(json.dumps(r, indent=1)[:4000], flush=True)
        with open(os.path.join(OUT, a.out_name), "w", encoding="utf-8") as f:
            json.dump({"result": r}, f, indent=1)
        return

    if a.accuracy:
        install()
        r = accuracy(corpus=a.corpus, stride=a.stride, cap=a.cap, n_boot=a.boot)
        print(json.dumps(r, indent=1), flush=True)
        with open(os.path.join(OUT, a.out_name), "w", encoding="utf-8") as f:
            json.dump({"result": r}, f, indent=1)
        return

    ap.print_help()


if __name__ == "__main__":
    main()
