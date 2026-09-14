"""exp_predicate_rescue_bf_cue_v1 -- the PREDICATE RESCUE's lexical-likelihood cue, re-derived from the
BRAIN-FOUNDATIONAL category organ that replaced the supervised perceptron.

problem: the_predicate_rescue_is_dormant_under_the_bf_category_organ_its_lexical_likelihood_cue_still_
         expects_the_perceptrons_margin   (priority 107)

THE DEFECT. The landed rescue organ (hdlab/predicate_detector.py) recovers real verbs the tagger called
nouns -- a whole clause, and every downstream read of it, otherwise disappears. Its noisy-channel LEXICAL
LIKELIHOOD cue was `verb_margin` = the supervised perceptron's emission score(VERB) minus its best
non-VERB score. Since 2026-09-12 the live category organ is the count-based generative model
(hdlab/lexical_categories.py) and there is no perceptron on the live path, so situation_reader's `_rescue`
branch falls through to a 2026-09-13 stand-in: `post[i]["VERB"] >= 0.3`, a BARE POSTERIOR THRESHOLD with
no other cue. It never fires ("presents" in "the lake presents an unbroken sheet of ice" scores 0.022).

THE BRAIN. Predicate-hood is a noisy-channel decision (Gibson 2013): a LEXICAL LIKELIHOOD combined with a
STRUCTURAL PRIOR (one predicate per clause -- Spivey-Knowlton 1993; frequent frames -- Mintz 2003; finite
morphology -- Monaghan 2005). The category organ already computes the lexical likelihood EXACTLY: its
emission channel is log P(word | category) accrued from counts. The perceptron's margin was a
DISCRIMINATIVE stand-in for that same quantity. So the cue is re-derived by EXACT REPLICATION of the
OPERATION (VERB emission minus the best non-VERB non-AUX emission) on the brain-foundational source.

THE SIGNAL-LOSS DIAGNOSIS this cell tests. The stand-in reads the POSTERIOR, which is emission x
transition already settled -- the structural prior is baked in, so the combiner's other six structural
cues double-count it, and the lexical evidence is washed out by a sequence model that has already decided
the token is a noun. Splitting the two factors back apart (emission = likelihood; the six cues = prior) is
the fix. Plus one cue the bare threshold structurally cannot express:

  CLAUSE VERB SHARE -- one-predicate-per-clause competition done as a COMPETITION, not a threshold:
  share(i) = post_i(VERB) / sum_j post_j(VERB) over the clause. An absolute threshold on an unnormalised
  belief cannot see that 'presents' holds 38% of the whole sentence's verb belief while every rival holds
  less; this is exactly Spivey-Knowlton's normalised competition and it is a pure function of the organ's
  own posterior.

COMBINERS. (a) LOGIT, the landed form (sklearn logistic at BUILD time), for comparability; (b) COUNTS, a
naive-Bayes log-likelihood-ratio accumulator over binned cues -- Christiansen & Chater multiple-cue
integration, every weight ONE PURE FUNCTION OF COUNTS, with an online `observe` path. (b) is the plastic,
brain-foundational combiner and is what the shipped asset uses.

GATE. `has_verb_reading` imports nltk WordNet AT INFERENCE in the landed organ. Here it is replaced by the
glass-box morphology organ (hdlab/morphology, an offline WordNet export, byte-identical port of morphy) and
the equivalence is MEASURED on the whole candidate population (control 6).

FLOORS / CONTROLS. (1) the dormant stand-in (bare posterior threshold), swept and at its live 0.3;
(2) predicate_recall OFF (recovery 0 by construction); (3) an information-free twin (random promotion at
the matched rate); paired bootstrap over SENTENCES for every delta. Operating budget: false verbs per
sentence <= 0.5 (the perceptron-era detector's modern budget, 0.466).

POPULATIONS. MODERN UD-EWT test (gold UPOS, held out from the organ's count supply) 5-fold CV over
sentences; QA-SRL dev (modern OOD). 19c is NOT measured (owner ban).

Glass-box, CPU, NO LLM, NO spaCy, no external parser. ASCII. own dir. NOTHING in hdlab/ modified.

Run:
  .venv/Scripts/python.exe experiments/exp_predicate_rescue_bf_cue_v1.py --self-test
  .venv/Scripts/python.exe experiments/exp_predicate_rescue_bf_cue_v1.py --smoke
  .venv/Scripts/python.exe experiments/exp_predicate_rescue_bf_cue_v1.py --full
  .venv/Scripts/python.exe experiments/exp_predicate_rescue_bf_cue_v1.py --reader   (end-to-end reader event recall)

# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-test.conllu
# KB_REFERENT: data/benchmark_trap_check/qasrl/qasrl-v2/orig/dev.jsonl.gz
# KB_REFERENT: data/frontend_assets/lexical_categories_counts_v1.json
# KB_REFERENT: data/frontend_assets/predicate_detector_ud_qasrl.json
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
os.environ.setdefault("MKL_NUM_THREADS", "2")
import argparse
import gzip
import json
import math
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab import lexical_categories as LC
from hdlab.predicate_detector import frame_verb_cue, morph_finite

UD_TEST = os.path.join(_REPO, "data/corpora/ud_english_ewt/en_ewt-ud-test.conllu")
QASRL = os.path.join(_REPO, "data/benchmark_trap_check/qasrl/qasrl-v2/orig/dev.jsonl.gz")
HOOK_STATE = os.path.join(_REPO, "data/hook_state")
NOMINAL = ("NOUN", "PROPN", "PRON")
STANDIN_LIVE_TH = 0.3          # situation_reader.PREDICATE_RESCUE_MIN_P, the dormant stand-in's live threshold
FP_BUDGET = 0.5                # false verbs per sentence -- the perceptron-era detector's modern budget (0.466)

# the cue block the combiner reads. `lex_llr` REPLACES the perceptron's verb_margin.
CUES_STRUCT = ["frame_anchor", "subj_before", "obj_after", "morph_finite", "clause_verbless", "rel_position"]
# the SAME six cues read off the category organ's POSTERIOR instead of its argmax tag (see the graded block below)
CUES_STRUCT_GRADED = ["frame_anchor_g", "subj_before_g", "obj_after_g", "morph_finite",
                      "clause_verbless_g", "clause_local_verbless_g", "rel_position"]
LEX_FORMS = ["lex_llr", "lex_odds", "lex_bias", "stem_bias", "ctx_odds", "post_p"]
SHARE = "verb_share"
CSHARE = "clause_verb_share"


def get_output_dir(default_name: str = "predicate_rescue_bf_cue_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = Path(_REPO) / "data" / ("exp_" + name)
    d.mkdir(parents=True, exist_ok=True)
    return d


# ============================================================================ the glass-box verb-reading gate
_MORPH = None


def has_verb_reading_bf(tok: str) -> bool:
    """GLASS-BOX lexical verbhood: the morphology organ's verb route finds a WordNet verb lemma for this form.
    hdlab.morphology is a byte-identical pure-python port of morphy reading an OFFLINE WordNet export -- so this
    is the SAME decision `wn.synsets(w, pos='v')` makes, with NO nltk at inference (measured: control 6)."""
    global _MORPH
    if _MORPH is None:
        from hdlab.morphology import GlassBoxMorphology, _ASSET_DIR
        _MORPH = GlassBoxMorphology(_ASSET_DIR, mode="morphy")
    return _MORPH.morphy(tok.lower(), "v") is not None


_WN_CACHE = {}


def has_verb_reading_nltk(tok: str) -> bool:
    """The LANDED organ's gate (nltk WordNet at inference) -- reference only, for the equivalence control."""
    low = tok.lower()
    if low in _WN_CACHE:
        return _WN_CACHE[low]
    from hdlab.predicate_detector import has_verb_reading
    v = bool(has_verb_reading(low))
    _WN_CACHE[low] = v
    return v


# ============================================================================ the category organ's two channels
class CategoryChannels:
    """Reads the LIVE category organ and hands back, per sentence, the two quantities the noisy-channel
    decomposition needs and that the posterior conflates:
      EMISSION  le[i, c] = log P(word_i | c)      -- the LEXICAL LIKELIHOOD (counts; the brain's Hebbian accrual)
      POSTERIOR post[i, c]                        -- likelihood x sequential prior, settled by forward-backward
    `posterior` is the organ's OWN public output (byte-identical, verified in --self-test); the emission block
    replays the organ's own `_log_emit` with the same per-sentence state the organ sets up. No hdlab edit."""

    def __init__(self):
        self.m = LC.get()
        self.tags = list(self.m.tags)
        self.vi = self.tags.index("VERB")
        self.ai = self.tags.index("AUX")
        self.non = [j for j in range(len(self.tags)) if j not in (self.vi, self.ai)]
        self.nomi = [self.tags.index(t) for t in NOMINAL if t in self.tags]
        tot = sum(self.m.tag_count.values())
        self.log_prior = np.array([math.log((self.m.tag_count[t] + 0.1) / (tot + 0.1 * len(self.tags)))
                                   for t in self.tags])

    def lex_bias(self, w, le_row):
        """WHAT THIS WORD USUALLY DOES -- the type-level lexical category bias, read straight off the organ's own
        emission COUNTS: log(n(VERB, w) + lam) - log max_{c not VERB/AUX} (n(c, w) + lam).

        WHY NOT the raw emission log-ratio. P(w | c) is a likelihood over the whole vocabulary, so its add-lambda
        floor for an UNSEEN (word, category) cell is an arbitrary constant while a SEEN cell is a real estimate --
        which makes the ratio track the word's overall FREQUENCY instead of its category bias, and it INVERTS on
        exactly this population (measured on the witness: 'sheet', never seen as a verb, scores lex_llr -4.48 while
        'presents', seen as a verb, scores -5.16). Conditioning on the word instead of on the category removes the
        frequency term: this is the graded noun/verb lexical bias the brain carries per lexeme (Lee & Federmeier
        2009, graded category competition), and it is one pure function of the counts the organ already accrues, so
        `observe` updates it for free. A word with NO lexical entry has no bias to read -- it falls back to the
        organ's OWN novel-form (productivity) estimate, which is what its emission row already is."""
        wl = w.lower()
        m = self.m
        if wl not in m.vocab:
            return float(le_row[self.vi] - max(le_row[j] for j in self.non))
        lam = m.lam
        v = math.log(m.emit["VERB"][wl] + lam)
        best = max(math.log(m.emit[self.tags[j]][wl] + lam) for j in self.non)
        return float(v - best)

    def stem_bias(self, w, fallback):
        """WORDS AND RULES (Pinker & Ullman dual route; Rastle & Davis obligatory decomposition). A word's category
        possibilities are not exhausted by the forms it was SEEN in: 'presents' is 'present' + -s, and the stem is a
        known verb. The category organ already carries this table -- P(form category | stem majority category,
        inflection), accrued from its OWN vocabulary counts (`_log_stem_prior`) -- but only consults it for RARE
        forms or on a conflict, so a FREQUENT noun form with a verb stem never gets it. Read here as a cue for the
        rescue decision only. Falls back to `lex_bias` when the form does not decompose to a known stem."""
        row = self.m._log_stem_prior(w.lower())
        if row is None:
            return float(fallback)
        return float(row[self.vi] - max(row[j] for j in self.non))

    def lex_pcw(self, w):
        """P(VERB | word) FROM THE COUNTS -- the frequency-normalised likelihood ratio, written as a probability.

        The emission log-ratio `lex_llr` divides P(w|VERB) by P(w|c): both numerator and denominator carry the
        word's frequency through their category-sized denominators, and the add-lambda floor for an unseen cell is
        an arbitrary constant rather than an estimate, so the ratio INVERTS on rare nouns. Dividing the emission
        count by the WORD's OWN TOTAL instead -- n(VERB, w) / sum_c n(c, w) -- cancels the frequency term exactly:
        it is P(category | word), the quantity a reader actually carries per lexeme (Lee & Federmeier 2009 graded
        category competition). `lex_bias` is the log-odds form of the same thing against the best rival
        (log n(V,w) - log max_c n(c,w)); this is the log-probability form against the whole distribution
        (log n(V,w) - log sum_c n(c,w)). Both are measured; they differ only in the denominator, and the
        difference is exactly how much of the word's mass the best rival holds."""
        wl = w.lower()
        m = self.m
        lam = m.lam
        cnt = [m.emit[t][wl] for t in self.tags]
        tot = sum(cnt)
        if tot == 0:
            return None                       # no lexical entry: the form route answers instead
        T = len(self.tags)
        return float(math.log(cnt[self.vi] + lam) - math.log(tot + lam * T))

    def emission(self, words):
        m = self.m
        m._sent_pos = [LC.position_class(words, i) for i in range(len(words))]
        m._sent_lows = [w.lower() for w in words]
        m._sent_i = 0
        return np.stack([m._log_emit(w) for w in words])

    def read(self, words):
        """(tags, post[n,T], le[n,T]) for one sentence, from the live organ."""
        post = self.m.posterior(words)
        le = self.emission(words)
        tags = [self.tags[int(post[i].argmax())] for i in range(len(words))]
        return tags, post, le


CLAUSE_BREAK = {",", ";", ":", "--", "and", "but", "or", "that", "which", "who", "because", "while",
                "when", "if", "though", "although", "so", "then"}


def clause_spans(toks, tags):
    """Segment the sentence into CLAUSE-SIZED competition domains. One-predicate-per-clause competition
    (Spivey-Knowlton 1993) is a CLAUSE-level constraint, and a UD sentence routinely holds several clauses, so
    normalising the verb belief over the whole sentence dilutes it. The boundary cues are the closed-class ones a
    reader has before any parse: punctuation, coordinators and subordinators (no parse, no treebank)."""
    n = len(toks)
    bnds = [0]
    for i in range(1, n):
        if toks[i].lower() in CLAUSE_BREAK or tags[i] in ("SCONJ", "CCONJ"):
            bnds.append(i)
    bnds.append(n)
    span = [0] * n
    for k in range(len(bnds) - 1):
        for i in range(bnds[k], bnds[k + 1]):
            span[i] = k
    return span


def sentence_cues(ch, toks, tags, post, le):
    """Per-token cue dict for every token (candidacy is applied by the caller)."""
    n = len(toks)
    vshare_den = float(post[:, ch.vi].sum()) or 1e-12
    verbless = 0.0 if any(t == "VERB" for t in tags) else 1.0
    span = clause_spans(toks, tags)
    cl_den = {}
    cl_verbless = {}
    cl_verbless_g = {}
    for k in set(span):
        ix = [i for i in range(n) if span[i] == k]
        cl_den[k] = float(post[ix, ch.vi].sum()) or 1e-12
        cl_verbless[k] = 0.0 if any(tags[i] == "VERB" for i in ix) else 1.0
        cl_verbless_g[k] = 1.0 - float(post[ix, ch.vi].max())
    # GRADED STRUCTURAL CUES (2026-09-14). The six structural cues above read the ARGMAX TAG -- a point estimate --
    # so a single upstream mis-tag zeroes them, and an upstream mis-tag is precisely what is going on in the
    # sentences the rescue exists for. Measured on the witness: 'lake' is tagged ADJ, so subj_before reads 0 for
    # 'presents' even though the organ's own posterior puts 0.34 of its belief on a nominal reading of 'lake'.
    # The organ hands DOWN a distribution; these cues read the distribution (owner: pass the GRADED signal, never a
    # point estimate) -- P(nominal) = P(NOUN) + P(PROPN) + P(PRON), and "no verb in the clause" becomes
    # 1 - max_j P(VERB_j) instead of a hard flag.
    pnom = post[:, ch.nomi].sum(axis=1)
    pverb = post[:, ch.vi]
    out = []
    for i in range(n):
        lex_llr = float(le[i, ch.vi] - max(le[i, j] for j in ch.non))
        lex_odds = float((le[i, ch.vi] + ch.log_prior[ch.vi])
                         - max(le[i, j] + ch.log_prior[j] for j in ch.non))
        pv = float(post[i, ch.vi])
        pn = max(float(post[i, j]) for j in ch.non)
        ctx_odds = math.log(max(pv, 1e-12)) - math.log(max(pn, 1e-12))
        subj = 1.0 if any(tags[j] in NOMINAL for j in range(max(0, i - 4), i)) else 0.0
        obj = 1.0 if any(tags[j] in NOMINAL for j in range(i + 1, min(n, i + 5))) else 0.0
        frame = 1.0 if frame_verb_cue(toks, tags, i) else 0.0
        lb = ch.lex_bias(toks[i], le[i])
        lo_j = range(max(0, i - 4), i)
        hi_j = range(i + 1, min(n, i + 5))
        subj_g = max([float(pnom[j]) for j in lo_j], default=0.0)
        obj_g = max([float(pnom[j]) for j in hi_j], default=0.0)
        # the graded frame: a nominal before AND after within k=3, with no verb intervening (all read as beliefs)
        k3l = range(max(0, i - 3), i)
        k3r = range(i + 1, min(n, i + 4))
        sl = max([float(pnom[j]) for j in k3l], default=0.0)
        sr = max([float(pnom[j]) for j in k3r], default=0.0)
        between = [float(pverb[j]) for j in range(max(0, i - 3), i)]
        frame_g = sl * sr * (1.0 - (max(between) if between else 0.0))
        out.append({"lex_llr": lex_llr, "lex_odds": lex_odds, "lex_bias": lb,
                    "subj_before_g": subj_g, "obj_after_g": obj_g, "frame_anchor_g": frame_g,
                    "clause_verbless_g": 1.0 - float(pverb.max()),
                    "clause_local_verbless_g": cl_verbless_g[span[i]],
                    "stem_bias": ch.stem_bias(toks[i], lb),
                    "ctx_odds": ctx_odds, "post_p": pv,
                    SHARE: pv / vshare_den, CSHARE: pv / cl_den[span[i]],
                    "clause_local_verbless": cl_verbless[span[i]],
                    "frame_anchor": frame, "subj_before": subj, "obj_after": obj,
                    "morph_finite": morph_finite(toks[i]), "clause_verbless": verbless,
                    "rel_position": i / max(1, n - 1)})
    return out


# ============================================================================ populations
def load_ud(path, cap=None):
    sents, cur = [], []
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("#"):
            continue
        if not line.strip():
            if cur:
                sents.append(cur)
                cur = []
            continue
        c = line.split("\t")
        if "-" in c[0] or "." in c[0]:
            continue
        cur.append(c)
    if cur:
        sents.append(cur)
    out = [([c[1] for c in s], set(i for i, c in enumerate(s) if c[3] == "VERB")) for s in sents]
    return out[:cap] if cap else out


def load_gum(cap=None):
    """GUM/GENTLE (modern, 12+ genres, gold UPOS) -- a THIRD modern population, fully held out from the category
    organ's count supply (UD-EWT train). It buys the modern arm the statistical power UD-EWT test alone lacks
    (112 dropped verbs) and tests genre generalisation inside the modern register (the 19c ban stands)."""
    import glob
    out = []
    for f in sorted(glob.glob(os.path.join(_REPO, "data/corpora/gum/conllu/*.conllu"))):
        cur = []
        for line in open(f, encoding="utf-8"):
            line = line.rstrip("\n")
            if line.startswith("#"):
                continue
            if not line.strip():
                if cur:
                    out.append(([c[1] for c in cur],
                                set(i for i, c in enumerate(cur) if c[3] == "VERB")))
                    cur = []
                continue
            c = line.split("\t")
            if "-" in c[0] or "." in c[0] or len(c) < 4:
                continue
            cur.append(c)
        if cur:
            out.append(([c[1] for c in cur], set(i for i, c in enumerate(cur) if c[3] == "VERB")))
    if cap and len(out) > cap:
        stride = max(1, len(out) // cap)          # a deterministic stride spans ALL genres (a prefix would take only
        out = out[::stride][:cap]                 # the alphabetically-first ones)
    return out


def load_qasrl(path, cap=None):
    out = []
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            out.append((d["sentenceTokens"], set(int(k) for k in d["verbEntries"].keys())))
            if cap and len(out) >= cap:
                break
    return out


def build_rows(sents, ch, gate=has_verb_reading_bf, progress=None, mode="noun"):
    """[(sent_idx, tok_idx, cue_dict, label)] over rescue candidates; label = 1 iff the token is a gold VERB the
    LIVE category organ dropped.

    mode="noun" (the landed remit): non-VERB non-AUX tokens with a verb reading -- a real verb called a noun.
    mode="aux"  (2026-09-14 phase 7): THE SOLE-AUX CLAUSE. UD's AUX/VERB split is an ANNOTATION CONVENTION, not a
      brain category: UD tags main-verb `be`/`have` AUX ("there IS an essay", "she HAS an essay"), and the reader
      fires events only on UPOS==VERB, so a clause whose only verbal token is AUX-tagged emits NO event and the
      whole clause disappears -- the same failure as the noun mis-tag, from the other side. The brain has no such
      convention: the predicate slot is filled by whatever carries the clause's finite core, and when nothing else
      competes for it that is the auxiliary itself (one predicate per clause, Spivey-Knowlton 1993). The arm
      therefore admits an AUX-tagged token as a candidate ONLY when NO VERB-tagged token competes in its clause.
      This is the class that is invisible to the additive rescue by construction (4.7-38.8% of dropped verbs) and
      it is the same VERB-as-AUX confusion that carries 58% of the tag-to-head loss upstream (2026-09-13)."""
    rows = []
    nsent = 0
    n_drop_total = 0
    n_drop_cand = 0
    for k, (toks, gold_verb) in enumerate(sents):
        if not toks:
            continue
        tags, post, le = ch.read(list(toks))
        cues = sentence_cues(ch, list(toks), tags, post, le)
        if mode == "aux":
            span = clause_spans(list(toks), tags)
            has_verb = {c: any(tags[j] == "VERB" for j in range(len(toks)) if span[j] == c) for c in set(span)}
            dropped = set(i for i in gold_verb if tags[i] == "AUX")
        else:
            dropped = set(i for i in gold_verb if tags[i] not in ("VERB", "AUX"))
        n_drop_total += len(dropped)
        for i in range(len(toks)):
            if mode == "aux":
                if tags[i] != "AUX" or has_verb[span[i]]:
                    continue                       # a VERB already occupies this clause's predicate slot
            else:
                if tags[i] in ("VERB", "AUX"):
                    continue
                if not gate(toks[i]):
                    continue
            if i in dropped:
                n_drop_cand += 1
            rows.append((nsent, i, cues[i], 1 if i in dropped else 0))
        nsent += 1
        if progress and k % progress == 0:
            print("    .. %d sentences, %d rows" % (k, len(rows)), flush=True)
    cov = {"mode": mode, "n_dropped_verbs": n_drop_total, "n_dropped_in_gate": n_drop_cand,
           "gate_coverage": round(n_drop_cand / max(1, n_drop_total), 4)}
    return rows, nsent, cov


# ============================================================================ combiners
def _X(rows, names):
    return np.array([[r[2][c] for c in names] for r in rows], dtype=np.float64)


def fit_logit(rows, names):
    from sklearn.linear_model import LogisticRegression
    X = _X(rows, names)
    y = np.array([r[3] for r in rows], dtype=np.int64)
    mu = X.mean(axis=0)
    sd = X.std(axis=0)
    sd[sd == 0] = 1.0
    clf = LogisticRegression(max_iter=2000, class_weight="balanced")
    clf.fit((X - mu) / sd, y)
    return {"kind": "logit", "names": list(names), "coef": [float(c) for c in clf.coef_[0]],
            "intercept": float(clf.intercept_[0]), "mu": [float(x) for x in mu], "sd": [float(x) for x in sd]}


def score_logit(model, rows):
    X = _X(rows, model["names"])
    mu = np.array(model["mu"])
    sd = np.array(model["sd"])
    z = model["intercept"] + ((X - mu) / sd) @ np.array(model["coef"])
    return 1.0 / (1.0 + np.exp(-z))


# ---- the PLASTIC combiner: naive-Bayes cue integration over COUNTS (Christiansen & Chater multiple-cue
#      integration). Every weight is ONE PURE FUNCTION of two count tables; `observe` accrues online.
BIN_SPEC = {
    # cue -> (lo, hi, width) in the cue's own natural units; outside the range clips to the edge bin.
    "lex_llr": (-14.0, 8.0, 1.0), "lex_odds": (-14.0, 8.0, 1.0), "ctx_odds": (-14.0, 8.0, 1.0),
    "lex_bias": (-10.0, 6.0, 1.0), "stem_bias": (-10.0, 6.0, 1.0), "lex_pcw": (-12.0, 0.0, 1.0),
    "post_p": (0.0, 1.0, 0.05), SHARE: (0.0, 1.0, 0.05), CSHARE: (0.0, 1.0, 0.05),
    "rel_position": (0.0, 1.0, 0.2),
    "subj_before_g": (0.0, 1.0, 0.1), "obj_after_g": (0.0, 1.0, 0.1), "frame_anchor_g": (0.0, 1.0, 0.1),
    "clause_verbless_g": (0.0, 1.0, 0.1), "clause_local_verbless_g": (0.0, 1.0, 0.1),
}


def cue_bin(name, x):
    spec = BIN_SPEC.get(name)
    if spec is None:
        return int(round(float(x)))                      # binary cues are their own bins
    lo, hi, w = spec
    return int(math.floor((min(max(float(x), lo), hi) - lo) / w))


class CountCombiner:
    """Naive-Bayes log-likelihood-ratio accumulator over binned cues. KNOWLEDGE = counts; the weights are one
    pure function of them (`_w`); `observe(cues, label)` is the online path. No gradient, no fitted scale."""

    def __init__(self, names, lam=0.5):
        self.names = list(names)
        self.lam = float(lam)
        self.pos = {c: Counter() for c in self.names}
        self.neg = {c: Counter() for c in self.names}
        self.n_pos = 0
        self.n_neg = 0
        self.nbins = {}

    def observe(self, cues, label):
        tab = self.pos if label else self.neg
        for c in self.names:
            tab[c][cue_bin(c, cues[c])] += 1
        if label:
            self.n_pos += 1
        else:
            self.n_neg += 1

    def accrue(self, rows):
        for r in rows:
            self.observe(r[2], r[3])
        return self

    def finalize(self):
        for c in self.names:
            self.nbins[c] = max(2, len(set(self.pos[c]) | set(self.neg[c])))
        return self

    def _w(self, c, b):
        B = self.nbins.get(c, 2)
        lp = math.log((self.pos[c][b] + self.lam) / (self.n_pos + self.lam * B))
        ln = math.log((self.neg[c][b] + self.lam) / (self.n_neg + self.lam * B))
        return lp - ln

    def logodds(self, cues):
        z = math.log((self.n_pos + self.lam) / (self.n_neg + self.lam))
        for c in self.names:
            z += self._w(c, cue_bin(c, cues[c]))
        return z

    def score(self, cues):
        z = self.logodds(cues)
        return 1.0 / (1.0 + math.exp(-z)) if z < 0 else 1.0 - 1.0 / (1.0 + math.exp(z))

    def to_asset(self):
        return {"kind": "counts_naive_bayes", "names": self.names, "lam": self.lam,
                "n_pos": self.n_pos, "n_neg": self.n_neg,
                "bin_spec": {k: list(v) for k, v in BIN_SPEC.items()},
                "pos": {c: {str(b): int(n) for b, n in self.pos[c].items()} for c in self.names},
                "neg": {c: {str(b): int(n) for b, n in self.neg[c].items()} for c in self.names}}

    @classmethod
    def from_asset(cls, a):
        m = cls(a["names"], lam=a.get("lam", 0.5))
        m.n_pos = int(a["n_pos"])
        m.n_neg = int(a["n_neg"])
        for c in m.names:
            m.pos[c] = Counter({int(b): int(n) for b, n in a["pos"][c].items()})
            m.neg[c] = Counter({int(b): int(n) for b, n in a["neg"][c].items()})
        return m.finalize()


def score_counts(model, rows):
    return np.array([model.score(r[2]) for r in rows])


# ---- the ERROR-DRIVEN combiner: RESCORLA-WAGNER cue competition over the SAME binned cue units.
#      Naive-Bayes accumulates every cue's evidence INDEPENDENTLY. Three of the cues here (ctx_odds, verb_share,
#      clause_verb_share) are three reads of ONE channel -- the category organ's posterior -- so naive-Bayes counts
#      that evidence three times, which is exactly the measured gap between the counts arm and the logistic arm on
#      the in-domain population. The brain's account of REDUNDANT CUES is not independent accumulation: it is
#      error-driven cue competition (Rescorla & Wagner 1972; blocking and overshadowing -- a cue that adds nothing
#      beyond the cues already present gains no strength). Ellis 2006 and Ramscar et al. 2010 apply exactly this
#      rule to language-cue learning. The update is w += eta * (outcome - expectation) for every PRESENT cue unit,
#      one update per observation: plastic by construction, no batch fit, no gradient library, and the cue units are
#      the same one-hot bins the count tables use, so the two combiners differ ONLY in the learning rule.
class RWCombiner:
    """Rescorla-Wagner delta-rule combiner over one-hot binned cue units. Knowledge = associative strengths,
    updated ONLINE by `observe`; `accrue` is simply repeated experience of a stream."""

    def __init__(self, names, eta=0.05, passes=8, seed=20260914):
        self.names = list(names)
        self.eta = float(eta)
        self.passes = int(passes)
        self.seed = int(seed)
        self.w = {}
        self.b = 0.0

    def _units(self, cues):
        return [(c, cue_bin(c, cues[c])) for c in self.names]

    def expectation(self, cues):
        z = self.b + sum(self.w.get(u, 0.0) for u in self._units(cues))
        return _sigm(z)

    def observe(self, cues, label):
        u = self._units(cues)
        p = _sigm(self.b + sum(self.w.get(k, 0.0) for k in u))
        d = self.eta * (float(label) - p)
        self.b += d
        for k in u:
            self.w[k] = self.w.get(k, 0.0) + d

    def accrue(self, rows):
        rng = np.random.default_rng(self.seed)
        idx = np.arange(len(rows))
        for _ in range(self.passes):
            rng.shuffle(idx)
            for j in idx:
                self.observe(rows[j][2], rows[j][3])
        return self

    def finalize(self):
        return self

    def score(self, cues):
        return self.expectation(cues)

    def to_asset(self):
        return {"kind": "rescorla_wagner", "names": self.names, "eta": self.eta, "passes": self.passes,
                "bias": self.b, "bin_spec": {k: list(v) for k, v in BIN_SPEC.items()},
                "w": {"%s|%d" % (c, b): v for (c, b), v in self.w.items()}}

    @classmethod
    def from_asset(cls, a):
        m = cls(a["names"], eta=a.get("eta", 0.05), passes=a.get("passes", 8))
        m.b = float(a["bias"])
        for k, v in a["w"].items():
            c, b = k.rsplit("|", 1)
            m.w[(c, int(b))] = float(v)
        return m


def load_combiner(a):
    """Rebuild the shipped combiner from its asset (either plastic form)."""
    return (RWCombiner.from_asset(a) if a.get("kind") == "rescorla_wagner" else CountCombiner.from_asset(a))


def _sigm(z):
    if z >= 0:
        return 1.0 / (1.0 + math.exp(-z))
    e = math.exp(z)
    return e / (1.0 + e)


# ============================================================================ evaluation
def curve(rows, nsent, proba, lo=None, hi=None, npts=200):
    y = np.array([r[3] for r in rows], dtype=np.int64)
    n_pos = max(1, int(y.sum()))
    lo = float(proba.min()) if lo is None else lo
    hi = float(proba.max()) if hi is None else hi
    out = []
    for th in np.linspace(lo, hi, npts):
        p = proba >= th
        out.append({"th": float(th), "recovery": float((p & (y == 1)).sum()) / n_pos,
                    "fp_per_sent": float((p & (y == 0)).sum()) / max(1, nsent), "n_promoted": int(p.sum())})
    return out


def op_point(rows, nsent, proba, budget=FP_BUDGET):
    """The highest-recovery threshold whose false-verbs/sentence stays inside the budget."""
    cv = curve(rows, nsent, proba)
    ok = [c for c in cv if c["fp_per_sent"] <= budget]
    if not ok:
        return None
    return max(ok, key=lambda c: c["recovery"])


def _sent_agg(rows, mask):
    """Per-sentence (hits, promoted) for a promotion mask, plus per-sentence positives. The bootstrap resamples
    SENTENCES, and recovery is a ratio of sums over sentences, so these aggregates are all it needs -- exactly
    the same estimator as resampling the rows of each sentence, at a fraction of the cost."""
    sid = np.array([r[0] for r in rows], dtype=np.int64)
    y = np.array([r[3] for r in rows], dtype=np.int64)
    u = np.unique(sid)
    pos = {s: k for k, s in enumerate(u)}
    idx = np.array([pos[s] for s in sid], dtype=np.int64)
    m = len(u)
    hits = np.bincount(idx, weights=(mask & (y == 1)).astype(float), minlength=m)
    prom = np.bincount(idx, weights=mask.astype(float), minlength=m)
    npos = np.bincount(idx, weights=(y == 1).astype(float), minlength=m)
    ncand = np.bincount(idx, minlength=m)
    return hits, prom, npos, ncand.astype(float)


def _boot_delta(hA, hB, npos, seed, n_boot):
    rng = np.random.default_rng(seed)
    m = len(npos)
    d = np.empty(n_boot)
    for b in range(n_boot):
        pick = rng.integers(0, m, m)
        g = npos[pick].sum()
        d[b] = (hA[pick].sum() - hB[pick].sum()) / (g if g > 0 else 1.0)
    return {"delta_mean": round(float(d.mean()), 4),
            "ci": [round(float(np.percentile(d, 2.5)), 4), round(float(np.percentile(d, 97.5)), 4)],
            "ci_half_width": round(float((np.percentile(d, 97.5) - np.percentile(d, 2.5)) / 2), 4),
            "ci_separated": bool(np.percentile(d, 2.5) > 0)}


def paired_boot(rows, nsent, pa, tha, pb, thb, seed=20260914, n_boot=2000):
    """Paired bootstrap over SENTENCES of (recovery_A - recovery_B), each arm at its own fixed threshold."""
    hA, _pA, npos, _c = _sent_agg(rows, pa >= tha)
    hB, _pB, _n, _c2 = _sent_agg(rows, pb >= thb)
    return _boot_delta(hA, hB, npos, seed, n_boot)


def twin_arm(rows, nsent, k, seed=20260914, n_draw=400):
    """Information-free twin: promote k gated candidates at random; the recovery distribution (reported null)."""
    y = np.array([r[3] for r in rows], dtype=np.int64)
    n_pos = max(1, int(y.sum()))
    rng = np.random.default_rng(seed)
    n = len(y)
    rec = []
    for _ in range(n_draw):
        pick = rng.choice(n, size=min(k, n), replace=False)
        m = np.zeros(n, dtype=bool)
        m[pick] = True
        rec.append(float((m & (y == 1)).sum()) / n_pos)
    return {"n_promoted": int(k), "twin_recovery_mean": round(float(np.mean(rec)), 4),
            "twin_recovery_p95": round(float(np.percentile(rec, 95)), 4)}


def boot_vs_twin(rows, nsent, proba, th, seed=20260914, n_boot=2000):
    """Paired bootstrap over SENTENCES of (recovery - twin recovery) at the matched promotion rate. Inside each
    resample the twin's recovery is its EXACT expectation under random promotion of the same number of gated
    candidates, promoted_b / candidates_b (the information-free null; a sampled draw only adds draw noise to the
    same mean, and the sampled twin's own mean/p95 are reported beside it by `twin_arm`)."""
    mask = proba >= th
    h, prom, npos, ncand = _sent_agg(rows, mask)
    rng = np.random.default_rng(seed)
    m = len(npos)
    d = np.empty(n_boot)
    for b in range(n_boot):
        pick = rng.integers(0, m, m)
        g = npos[pick].sum()
        g = g if g > 0 else 1.0
        nc = ncand[pick].sum()
        rate = (prom[pick].sum() / nc) if nc > 0 else 0.0
        d[b] = (h[pick].sum() - rate * g) / g
    return {"delta_vs_twin_mean": round(float(d.mean()), 4),
            "ci": [round(float(np.percentile(d, 2.5)), 4), round(float(np.percentile(d, 97.5)), 4)],
            "ci_half_width": round(float((np.percentile(d, 97.5) - np.percentile(d, 2.5)) / 2), 4),
            "ci_separated": bool(np.percentile(d, 2.5) > 0)}


def cv_scores(rows, names, kind, k=5, seed=20260914):
    """Held-out score per row: 5-fold CV over SENTENCES (no row is scored by a model that saw its sentence)."""
    sids = sorted(set(r[0] for r in rows))
    rng = np.random.default_rng(seed)
    rng.shuffle(sids)
    fold = {s: (i % k) for i, s in enumerate(sids)}
    out = np.zeros(len(rows))
    for f in range(k):
        tr = [r for r in rows if fold[r[0]] != f]
        te_i = [j for j, r in enumerate(rows) if fold[r[0]] == f]
        if not tr or not te_i or sum(r[3] for r in tr) == 0:
            continue
        te = [rows[j] for j in te_i]
        if kind == "logit":
            mdl = fit_logit(tr, names)
            pr = score_logit(mdl, te)
        elif kind == "rw":
            mdl = RWCombiner(names).accrue(tr).finalize()
            pr = score_counts(mdl, te)
        else:
            mdl = CountCombiner(names).accrue(tr).finalize()
            pr = score_counts(mdl, te)
        for j, p in zip(te_i, pr):
            out[j] = p
    return out


# ============================================================================ arms
def arm_specs():
    """Every arm: (label, cue list, combiner kind). The stand-in arm is scored directly from post_p."""
    S = CUES_STRUCT
    SG = CUES_STRUCT_GRADED
    return [
        # --- CUE-FORM SWEEP: which reading of the category organ is the lexical likelihood? (7 cues, landed shape)
        ("CUE_lex_llr__logit", ["lex_llr"] + S, "logit"),
        ("CUE_lex_odds__logit", ["lex_odds"] + S, "logit"),
        ("CUE_lex_bias__logit", ["lex_bias"] + S, "logit"),
        ("CUE_ctx_odds__logit", ["ctx_odds"] + S, "logit"),
        ("CUE_post_p__logit", ["post_p"] + S, "logit"),
        # --- + the one-predicate-per-clause COMPETITION (normalised share), the cue a threshold cannot express
        ("BF_bias_share__logit", ["lex_bias", SHARE] + S, "logit"),
        ("BF_bias_share__counts", ["lex_bias", SHARE] + S, "counts"),
        ("BF_bias_ctx_share__logit", ["lex_bias", "ctx_odds", SHARE] + S, "logit"),
        ("BF_bias_ctx_share__counts", ["lex_bias", "ctx_odds", SHARE] + S, "counts"),
        ("BF_bias_llr_ctx_share__counts", ["lex_bias", "lex_llr", "ctx_odds", SHARE] + S, "counts"),
        # --- QUALITY PUSH (2026-09-14): the words-and-rules STEM route + CLAUSE-LOCAL competition
        ("Q_stem__counts", ["lex_bias", "stem_bias", "ctx_odds", SHARE] + S, "counts"),
        ("Q_clause__counts", ["lex_bias", "ctx_odds", SHARE, CSHARE, "clause_local_verbless"] + S, "counts"),
        ("Q_stem_clause__counts", ["lex_bias", "stem_bias", "ctx_odds", SHARE, CSHARE,
                                   "clause_local_verbless"] + S, "counts"),
        ("Q_stem_clause__logit", ["lex_bias", "stem_bias", "ctx_odds", SHARE, CSHARE,
                                  "clause_local_verbless"] + S, "logit"),
        # --- ERROR-DRIVEN CUE COMPETITION (Rescorla-Wagner) over the SAME binned units as the counts combiner:
        #     the only difference is the learning rule, so this isolates naive-Bayes' redundant-cue double-count.
        ("Q_stem_clause__rw", ["lex_bias", "stem_bias", "ctx_odds", SHARE, CSHARE,
                               "clause_local_verbless"] + S, "rw"),
        ("BF_bias_ctx_share__rw", ["lex_bias", "ctx_odds", SHARE] + S, "rw"),
        # --- DE-CORRELATED naive-Bayes: ONE read of the posterior channel (the clause competition), so the
        #     independence assumption the count combiner makes is no longer violated by construction.
        ("Q_nb_decorrelated__counts", ["lex_bias", "stem_bias", CSHARE, "clause_local_verbless"] + S, "counts"),
        # --- GRADED STRUCTURAL CUES: the six structural cues read the POSTERIOR instead of the argmax tag, so a
        #     single upstream mis-tag no longer zeroes them (the hand-off that was losing the signal).
        ("G_graded__rw", ["lex_bias", "stem_bias", "ctx_odds", SHARE, CSHARE] + SG, "rw"),
        ("G_graded__counts", ["lex_bias", "stem_bias", "ctx_odds", SHARE, CSHARE] + SG, "counts"),
        ("G_graded__logit", ["lex_bias", "stem_bias", "ctx_odds", SHARE, CSHARE] + SG, "logit"),
        ("G_graded_plus_hard__rw", ["lex_bias", "stem_bias", "ctx_odds", SHARE, CSHARE] + SG + S, "rw"),
        ("ABL_graded_struct_only__rw", SG, "rw"),
        # --- PHASE 7: the FREQUENCY-NORMALISED likelihood ratio written as P(category | word), against the
        #     emission log-ratio it replaces and against the log-odds form already shipped.
        ("P7_pcw__rw", ["lex_pcw", "stem_bias", "ctx_odds", SHARE, CSHARE] + SG, "rw"),
        ("P7_pcw_and_bias__rw", ["lex_pcw", "lex_bias", "stem_bias", "ctx_odds", SHARE, CSHARE] + SG, "rw"),
        ("ABL_lex_pcw_only__counts", ["lex_pcw"], "counts"),
        ("ABL_lex_llr_only__counts", ["lex_llr"], "counts"),
        # --- ABLATIONS: each channel alone (is the COMBINATION earning its keep?)
        ("ABL_share_only__counts", [SHARE], "counts"),
        ("ABL_clause_share_only__counts", [CSHARE], "counts"),
        ("ABL_lex_bias_only__counts", ["lex_bias"], "counts"),
        ("ABL_stem_bias_only__counts", ["stem_bias"], "counts"),
        ("ABL_ctx_odds_only__counts", ["ctx_odds"], "counts"),
        ("ABL_struct_only__counts", S, "counts"),
        ("ABL_bias_share_only__counts", ["lex_bias", SHARE], "counts"),
    ]


BUDGETS = [0.05, 0.10, 0.15, 0.25, 0.50]
CI_BUDGETS = [0.10, 0.50]


def evaluate_population(name, rows, nsent, cov, do_arms=None, n_boot=2000):
    npos = int(sum(r[3] for r in rows))
    print("\n===== %s : %d sentences, %d candidates, %d dropped-verb positives (gate coverage %.3f) ====="
          % (name, nsent, len(rows), npos, cov["gate_coverage"]), flush=True)
    res = {"population": name, "n_sent": nsent, "n_candidates": len(rows), "n_positives": npos,
           "gate": cov, "budgets": BUDGETS, "arms": {}}
    if not rows or npos == 0:
        return res
    y = np.array([r[3] for r in rows])

    # ---- FLOOR 1: the dormant stand-in (bare posterior threshold). Live th=0.3 AND swept to each budget.
    standin = np.array([r[2]["post_p"] for r in rows])
    P = standin >= STANDIN_LIVE_TH
    live_pt = {"th": STANDIN_LIVE_TH, "recovery": round(float((P & (y == 1)).sum()) / max(1, npos), 4),
               "fp_per_sent": round(float((P & (y == 0)).sum()) / max(1, nsent), 4), "n_promoted": int(P.sum())}
    st_op = {b: op_point(rows, nsent, standin, b) for b in BUDGETS}
    res["arms"]["FLOOR_standin_live_th0.3"] = live_pt
    res["arms"]["FLOOR_standin_swept"] = {str(b): st_op[b] for b in BUDGETS}
    res["arms"]["FLOOR_predicate_recall_OFF"] = {"recovery": 0.0, "fp_per_sent": 0.0,
                                                 "note": "a dropped verb emits no event -- deterministic zero"}
    print("  %-30s | %s" % ("arm", "  ".join("rec@fp<=%.2f" % b for b in BUDGETS)), flush=True)
    print("  %-30s | recovery %.4f at fp/sent %.4f (promoted %d)  <-- THE DORMANT LIVE READ"
          % ("FLOOR stand-in th=0.3", live_pt["recovery"], live_pt["fp_per_sent"], live_pt["n_promoted"]), flush=True)
    print("  %-30s | %s   <-- the STRONGEST floor (the same cue, threshold swept)"
          % ("FLOOR stand-in swept",
             "  ".join(("%11.4f" % st_op[b]["recovery"]) if st_op[b] else ("%11s" % "-") for b in BUDGETS)), flush=True)

    specs = [s for s in arm_specs() if (do_arms is None or s[0] in do_arms)]
    for label, names, kind in specs:
        pr = cv_scores(rows, names, kind)
        row = {"cues": list(names), "combiner": kind, "at_budget": {}}
        for b in BUDGETS:
            op = op_point(rows, nsent, pr, b)
            if op is None:
                row["at_budget"][str(b)] = None
                continue
            ent = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in op.items()}
            ent["precision"] = round(op["recovery"] * npos / max(1, op["n_promoted"]), 4)
            if b in CI_BUDGETS:
                ent["twin"] = twin_arm(rows, nsent, op["n_promoted"])
                ent["vs_twin"] = boot_vs_twin(rows, nsent, pr, op["th"], n_boot=n_boot)
                ent["vs_standin_live"] = paired_boot(rows, nsent, pr, op["th"], standin, STANDIN_LIVE_TH, n_boot=n_boot)
                if st_op[b]:
                    ent["vs_standin_swept"] = paired_boot(rows, nsent, pr, op["th"], standin, st_op[b]["th"], n_boot=n_boot)
            row["at_budget"][str(b)] = ent
        res["arms"][label] = row
        cells = []
        for b in BUDGETS:
            e = row["at_budget"][str(b)]
            cells.append("%11.4f" % e["recovery"] if e else "%11s" % "-")
        print("  %-30s | %s" % (label, "  ".join(cells)), flush=True)
    # the CI table at the two decision budgets
    for b in CI_BUDGETS:
        print("\n  --- CI at fp/sent <= %.2f (paired bootstrap over sentences) ---" % b, flush=True)
        for label, _n, _k in specs:
            e = res["arms"][label]["at_budget"].get(str(b))
            if not e or "vs_twin" not in e:
                continue
            vs_sw = e.get("vs_standin_swept")
            print("   %-30s rec %.4f prec %.4f | twin %+.4f CI[%+.4f,%+.4f] %-3s | standin-live %+.4f %-3s | standin-swept %s"
                  % (label, e["recovery"], e["precision"], e["vs_twin"]["delta_vs_twin_mean"], e["vs_twin"]["ci"][0],
                     e["vs_twin"]["ci"][1], "SEP" if e["vs_twin"]["ci_separated"] else "ns",
                     e["vs_standin_live"]["delta_mean"], "SEP" if e["vs_standin_live"]["ci_separated"] else "ns",
                     ("%+.4f CI[%+.4f,%+.4f] %s" % (vs_sw["delta_mean"], vs_sw["ci"][0], vs_sw["ci"][1],
                                                    "SEP" if vs_sw["ci_separated"] else "ns")) if vs_sw else "-"),
                  flush=True)
    return res


# ============================================================================ witness
WITNESS = "the lake presents an unbroken sheet of ice"


def witness_report(ch, model, names, th):
    toks = WITNESS.split()
    tags, post, le = ch.read(toks)
    cues = sentence_cues(ch, toks, tags, post, le)
    rows = []
    for i, w in enumerate(toks):
        if tags[i] in ("VERB", "AUX") or not has_verb_reading_bf(w):
            continue
        s = (model.score(cues[i]) if hasattr(model, "score")
             else float(score_logit(model, [(0, i, cues[i], 0)])[0]))
        rows.append({"i": i, "tok": w, "tag": tags[i], "post_VERB": round(float(post[i, ch.vi]), 4),
                     "lex_llr": round(cues[i]["lex_llr"], 3), "verb_share": round(cues[i][SHARE], 4),
                     "score": round(s, 4), "rescued": bool(s >= th)})
    return {"sentence": WITNESS, "tags": tags, "threshold": round(float(th), 4), "candidates": rows,
            "rescues_presents": any(r["tok"] == "presents" and r["rescued"] for r in rows),
            "rejects_distractors": not any(r["tok"] in ("sheet", "ice", "lake") and r["rescued"] for r in rows)}


def augment_rows(rows, sents, ch, extra=("lex_pcw",)):
    """Add WORD-ONLY cues to already-cached rows. These depend on the token alone (the organ's emission counts for
    that word), not on the sentence, so they can be filled in without re-running the organ -- the row's (sent, tok)
    index recovers the token from the same population, in the same order `build_rows` walked it."""
    by = {}
    k = 0
    for toks, _g in sents:
        if not toks:
            continue
        by[k] = toks
        k += 1
    miss = 0
    for r in rows:
        toks = by.get(r[0])
        if toks is None or r[1] >= len(toks):
            miss += 1
            continue
        w = toks[r[1]]
        if "lex_pcw" in extra:
            v = ch.lex_pcw(w)
            # an unknown form has no lexical entry at all: fall back to the same novel-form route lex_bias uses
            r[2]["lex_pcw"] = float(v) if v is not None else float(r[2]["lex_bias"])
    return miss


# ============================================================================ DIAGNOSTICS: understand every negative
def reliability(rows, key="post_p", nbin=10):
    """Is the organ's verb belief CALIBRATED on this population? For each decile of the cue, the fraction of
    candidates that really are dropped verbs. A cue that is already calibrated leaves a combiner nothing to add;
    a cue that is mis-ordered is where the multi-cue combination earns its keep."""
    x = np.array([r[2][key] for r in rows])
    y = np.array([r[3] for r in rows])
    q = np.quantile(x, np.linspace(0, 1, nbin + 1))
    out = []
    for k in range(nbin):
        lo, hi = q[k], q[k + 1]
        m = (x >= lo) & (x <= hi if k == nbin - 1 else x < hi)
        if m.sum() == 0:
            continue
        out.append({"bin": k, "lo": round(float(lo), 4), "hi": round(float(hi), 4), "n": int(m.sum()),
                    "p_dropped_verb": round(float(y[m].mean()), 4)})
    return out


def rank_auc(rows, key):
    """AUC of one cue over the candidate population (rank-order quality, threshold-free)."""
    x = np.array([r[2][key] for r in rows], dtype=float)
    y = np.array([r[3] for r in rows], dtype=int)
    o = np.argsort(x)
    ranks = np.empty(len(x))
    ranks[o] = np.arange(1, len(x) + 1)
    npos = int(y.sum())
    nneg = len(y) - npos
    if npos == 0 or nneg == 0:
        return None
    return round(float((ranks[y == 1].sum() - npos * (npos + 1) / 2) / (npos * nneg)), 4)


def gate_gap_breakdown(ch, sents, cap=700):
    """WHERE THE DROPPED VERBS THE RESCUE CANNOT EVEN SEE GO. The rescue is ADDITIVE by construction: it only
    considers tokens the category organ did NOT call VERB or AUX, and only those with a verb reading. So a gold
    VERB the organ called AUX is invisible to it -- and that is UD's main-verb be/have convention, the single
    confusion already named upstream (2026-09-13: 58% of the tag->head loss). Counted here so the boundary of this
    organ's remit is a number, not an assumption."""
    n_drop = 0
    aux = 0
    no_reading = 0
    covered = 0
    examples = []
    ss = list(sents)
    ss = ss[::max(1, len(ss) // cap)][:cap]          # a stride, not a prefix: the prefix is one genre
    for toks, gold in ss:
        if not toks:
            continue
        tags = ch.m.tag(list(toks))
        for i in gold:
            if i >= len(tags) or tags[i] == "VERB":
                continue
            n_drop += 1
            if tags[i] == "AUX":
                aux += 1
            elif not has_verb_reading_bf(toks[i]):
                no_reading += 1
                if len(examples) < 25:
                    examples.append((toks[i], tags[i]))
            else:
                covered += 1
    return {"n_sentences": len(ss), "no_verb_reading_examples": examples, "n_dropped_verbs": n_drop,
            "tagged_AUX_invisible_to_an_additive_rescue": aux,
            "no_verb_reading_in_the_lexicon": no_reading,
            "inside_the_rescue_gate": covered,
            "share_lost_to_AUX": round(aux / max(1, n_drop), 4),
            "share_lost_to_the_lexicon": round(no_reading / max(1, n_drop), 4)}


def diagnose(name, rows, nsent, sents, model=None, th=None):
    npos = int(sum(r[3] for r in rows))
    d = {"population": name, "n_sent": nsent, "n_candidates": len(rows), "n_positives": npos,
         "base_rate_positives_among_candidates": round(npos / max(1, len(rows)), 4),
         "cue_auc": {k: rank_auc(rows, k) for k in (LEX_FORMS + [SHARE, CSHARE])},
         "post_p_reliability_deciles": reliability(rows, "post_p"),
         "verb_share_reliability_deciles": reliability(rows, SHARE)}
    # unknown-word rate among candidates (the organ has no lexical entry -> lex_bias falls back to the form route)
    lc = LC.get()
    toks_by = {}
    k = 0
    for toks, _g in sents:
        if not toks:
            continue
        toks_by[k] = toks
        k += 1
    unk = sum(1 for r in rows if k > 0 and r[0] in toks_by and toks_by[r[0]][r[1]].lower() not in lc.vocab)
    unk_pos = sum(1 for r in rows if r[3] and r[0] in toks_by and toks_by[r[0]][r[1]].lower() not in lc.vocab)
    d["unknown_form_rate_among_candidates"] = round(unk / max(1, len(rows)), 4)
    d["unknown_form_rate_among_positives"] = round(unk_pos / max(1, npos), 4)
    # THE HAND-OFF LOSS. The category organ's posterior reaches consumers through `tag_with_posterior`, which keeps
    # only categories with P >= 0.01. For a rescue candidate that truncation is the difference between "a small but
    # real verb belief" and "no verb belief at all" -- so count the dropped verbs the hand-off silently zeroes.
    pv = np.array([r[2]["post_p"] for r in rows])
    yy = np.array([r[3] for r in rows])
    d["handoff_truncation_at_0p01"] = {
        "candidates_below_0.01": int((pv < 0.01).sum()),
        "dropped_verbs_below_0.01": int(((pv < 0.01) & (yy == 1)).sum()),
        "share_of_positives_zeroed_by_the_handoff": round(float(((pv < 0.01) & (yy == 1)).sum() / max(1, npos)), 4),
        "dropped_verbs_below_the_live_threshold_0.3": int(((pv < 0.3) & (yy == 1)).sum()),
        "share_of_positives_below_the_live_threshold": round(float(((pv < 0.3) & (yy == 1)).sum() / max(1, npos)), 4)}
    if model is not None and th is not None:
        pr = np.array([model.score(r[2]) for r in rows])
        miss = [(toks_by.get(r[0], [""] * 99)[r[1]], round(float(p), 4), round(r[2]["lex_bias"], 2),
                 round(r[2][SHARE], 3), round(r[2][CSHARE], 3))
                for r, p in zip(rows, pr) if r[3] == 1 and p < th]
        d["n_missed_at_operating_point"] = len(miss)
        d["missed_examples"] = sorted(miss, key=lambda t: -t[1])[:30]
        fps = [(toks_by.get(r[0], [""] * 99)[r[1]], round(float(p), 4))
               for r, p in zip(rows, pr) if r[3] == 0 and p >= th]
        d["n_false_promotions_at_operating_point"] = len(fps)
        d["top_false_promotions"] = [w for w, _p in Counter(w for w, _ in fps).most_common(25)]
    return d


def truncation_analysis(rows, nsent, budget=0.10):
    """WHAT THE CATEGORY ORGAN'S HAND-OFF COSTS. `tag_with_posterior` keeps only categories with P >= 0.01, and
    that dict is what every graded consumer downstream receives. For a consumer that reads P(VERB) the truncation
    is a HARD FLOOR on its operating point: it cannot set a threshold below eps, because everything below eps
    arrives as an exact zero. Measured here by capping the achievable threshold at eps -- exactly what the
    truncation does -- for eps in {0.01 (today), 0.001, 0 (the full distribution)}."""
    p = np.array([r[2]["post_p"] for r in rows])
    y = np.array([r[3] for r in rows])
    npos = max(1, int(y.sum()))
    out = {}
    for eps in (0.01, 0.001, 0.0):
        cv = [c for c in curve(rows, nsent, p) if c["th"] >= eps and c["fp_per_sent"] <= budget]
        best = max(cv, key=lambda c: c["recovery"]) if cv else None
        out[str(eps)] = {
            "best_recovery_at_budget": round(best["recovery"], 4) if best else None,
            "threshold": round(best["th"], 6) if best else None,
            "fp_per_sent": round(best["fp_per_sent"], 4) if best else None,
            "positives_zeroed_by_the_handoff": int((p < eps).sum() and ((p < eps) & (y == 1)).sum()),
            "share_of_positives_zeroed": round(float(((p < eps) & (y == 1)).sum() / npos), 4),
            "candidate_entries_kept": int((p >= eps).sum())}
    return out


def truncation_cost(ch, sents, cap=400):
    """The RUNTIME and SIZE cost of widening the truncation: how many category entries per token survive each eps,
    and what the dict build costs. The posterior itself is computed either way -- only the dict changes."""
    import time as _t
    out = {}
    ss = [s for s, _g in list(sents)[:cap] if s]
    posts = [ch.m.posterior(list(s)) for s in ss]                 # the shared cost, paid once, excluded below
    for eps in (0.01, 0.001, 0.0):
        t0 = _t.time()
        ntok = 0
        nent = 0
        for post in posts:
            for i in range(post.shape[0]):
                d = {ch.tags[j]: float(post[i, j]) for j in range(len(ch.tags)) if post[i, j] >= eps}
                ntok += 1
                nent += len(d)
        out[str(eps)] = {"dict_build_s_per_1000_tokens": round(1000.0 * (_t.time() - t0) / max(1, ntok), 4),
                         "entries_per_token": round(nent / max(1, ntok), 3), "n_tokens": ntok}
    return out


def blocking_dump(rows, names, cues_of_interest):
    """THE REDUNDANCY, NAMED. Pearson correlation between the cues, and the naive-Bayes vs Rescorla-Wagner weight
    each gives the SAME bin. Naive Bayes accumulates every cue independently; the delta rule stops learning about a
    cue once the cues already present predict the outcome (Rescorla & Wagner 1972, blocking)."""
    X = {c: np.array([r[2][c] for r in rows], dtype=float) for c in cues_of_interest}
    corr = {}
    for a in cues_of_interest:
        for b in cues_of_interest:
            if a < b:
                corr["%s~%s" % (a, b)] = round(float(np.corrcoef(X[a], X[b])[0, 1]), 4)
    nb = CountCombiner(names).accrue(rows).finalize()
    rw = RWCombiner(names).accrue(rows).finalize()
    tab = []
    for c in cues_of_interest:
        bins = sorted(set(nb.pos[c]) | set(nb.neg[c]))
        for b in bins:
            n_pos = nb.pos[c].get(b, 0)
            if n_pos < 20:
                continue
            tab.append({"cue": c, "bin": b, "n_pos": int(n_pos), "n_neg": int(nb.neg[c].get(b, 0)),
                        "naive_bayes_w": round(nb._w(c, b), 4), "rescorla_wagner_w": round(rw.w.get((c, b), 0.0), 4)})
    return {"cue_correlations": corr, "weights": tab}


# ============================================================================ END-TO-END: the LIVE reader
def bf_rescue_indices(ch, toks, model, th):
    """THE PROPOSED LIVE RESCUE, exactly as the patch ships it: read the category organ's posterior AND its
    emission counts, build the cue block, score with the count combiner, promote above threshold. ADDITIVE --
    a token the organ already called VERB/AUX is never touched."""
    tags, post, le = ch.read(list(toks))
    cues = sentence_cues(ch, list(toks), tags, post, le)
    out = []
    for i in range(len(toks)):
        if tags[i] in ("VERB", "AUX") or not has_verb_reading_bf(toks[i]):
            continue
        s = model.score(cues[i])
        if s >= th:
            out.append((i, s))
    return tags, out


def reader_end_to_end(ch, sents, model, th, cap=400):
    """Event detection through the LIVE reader path on modern gold. The reader fires one event per token the
    category organ calls VERB, plus (predicate_recall) one per rescued token. Three arms:
      OFF       predicate_recall=False           -- the base detector
      STANDIN   the dormant live read            -- post[i]['VERB'] >= 0.3
      BF        the proposed rescue              -- the count combiner over the BF cue block
    Reported: event RECALL against gold VERB tokens, event PRECISION, false events per sentence. A live
    SituationReader is run alongside on the same sentences to prove the arms match the real reader."""
    from hdlab.situation_reader import SituationReader
    r_off = SituationReader(predicate_recall=False)
    r_on = SituationReader(predicate_recall=True)
    ARMS = ("OFF", "STANDIN", "BF", "BF_AUX")
    per = {a: [] for a in ARMS}          # per-sentence (hits, fires)
    zero_ev = {a: 0 for a in ARMS}       # sentences that produce NO event at all
    zero_ev_gold = {a: 0 for a in ARMS}  # ... among sentences that DO have a gold verb
    n_gold_sent = 0
    gold_n = []
    live_off = live_on = mismatch = mism_standin = 0
    nsent = 0
    for toks, gold_verb in sents[:cap]:
        if not toks or any((" " in t) for t in toks):
            continue
        text = " ".join(toks)
        tags, post, le = ch.read(list(toks))
        cues = sentence_cues(ch, list(toks), tags, post, le)
        base = set(i for i in range(len(toks)) if tags[i] == "VERB")
        cand = [i for i in range(len(toks))
                if tags[i] not in ("VERB", "AUX") and has_verb_reading_bf(toks[i])]
        standin = set(i for i in cand if float(post[i, ch.vi]) >= STANDIN_LIVE_TH)
        bf = set(i for i in cand if model.score(cues[i]) >= th)
        # THE SOLE-AUX CLAUSE (phase 7): an AUX-tagged token with no VERB competing in its clause, scored by the
        # same combiner. Measured as its OWN arm so its cost is never hidden inside the headline one.
        span = clause_spans(list(toks), tags)
        hv = {c: any(tags[j] == "VERB" for j in range(len(toks)) if span[j] == c) for c in set(span)}
        aux = set(i for i in range(len(toks))
                  if tags[i] == "AUX" and not hv[span[i]] and model.score(cues[i]) >= th)
        for a, s in (("OFF", base), ("STANDIN", base | standin), ("BF", base | bf),
                     ("BF_AUX", base | bf | aux)):
            per[a].append((len(s & gold_verb), len(s)))
            if not s:
                zero_ev[a] += 1
                if gold_verb:
                    zero_ev_gold[a] += 1
        if gold_verb:
            n_gold_sent += 1
        gold_n.append(len(gold_verb))
        nsent += 1
        if nsent <= 300:
            # CROSS-CHECK (first 300 sentences): the arms above must reproduce the LIVE SituationReader exactly,
            # so the arm numbers below are the reader's numbers and not a re-implementation's.
            eo, _ = r_off._extract_events(text)
            en, _ = r_on._extract_events(text)
            live_off += len(eo)
            live_on += len(en)
            if set(e.idx for e in eo) != base:
                mismatch += 1
            if set(e.idx for e in en) != (base | standin):
                mism_standin += 1
    G = np.array(gold_n, dtype=float)
    out = {"n_sent": nsent, "n_gold_verbs": int(G.sum()),
           "live_reader_crosscheck_sentences": min(300, nsent),
           "live_reader_events_off": live_off, "live_reader_events_standin_on": live_on,
           "arm_OFF_vs_live_reader_mismatched_sents": mismatch,
           "arm_STANDIN_vs_live_reader_mismatched_sents": mism_standin, "arms": {}}
    H = {a: np.array([x[0] for x in per[a]], dtype=float) for a in ARMS}
    F = {a: np.array([x[1] for x in per[a]], dtype=float) for a in ARMS}
    out["n_sentences_with_a_gold_verb"] = n_gold_sent
    for a in ARMS:
        out["arms"][a] = {"event_recall": round(float(H[a].sum() / max(1.0, G.sum())), 4),
                          "event_precision": round(float(H[a].sum() / max(1.0, F[a].sum())), 4),
                          "events_per_sent": round(float(F[a].sum() / max(1, nsent)), 4),
                          "false_events_per_sent": round(float((F[a].sum() - H[a].sum()) / max(1, nsent)), 4),
                          # THE CONVENTION-FREE INSTRUMENT: a sentence that produces NO event at all is a whole
                          # clause that every downstream organ never sees. It does not depend on whether UD calls
                          # the predicate VERB or AUX, which is exactly the question the AUX arm is about.
                          "sentences_with_zero_events": zero_ev[a],
                          "share_of_sentences_with_zero_events": round(zero_ev[a] / max(1, nsent), 4),
                          "gold_verb_sentences_with_zero_events": zero_ev_gold[a],
                          "share_of_gold_verb_sentences_with_zero_events":
                              round(zero_ev_gold[a] / max(1, n_gold_sent), 4)}
    rng = np.random.default_rng(20260914)
    for a, b in (("BF", "OFF"), ("BF", "STANDIN"), ("STANDIN", "OFF"), ("BF_AUX", "BF")):
        d = np.empty(2000)
        for k in range(2000):
            pick = rng.integers(0, nsent, nsent)
            g = max(1.0, G[pick].sum())
            d[k] = (H[a][pick].sum() - H[b][pick].sum()) / g
        out["arms"]["%s_minus_%s_event_recall" % (a, b)] = {
            "delta": round(float(d.mean()), 4),
            "ci": [round(float(np.percentile(d, 2.5)), 4), round(float(np.percentile(d, 97.5)), 4)],
            "ci_separated": bool(np.percentile(d, 2.5) > 0)}
    return out


# ============================================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--reader", action="store_true", help="end-to-end reader event recall ON vs OFF")
    ap.add_argument("--gate-control", action="store_true", dest="gate_control")
    ap.add_argument("--rebuild", action="store_true", help="ignore the cached candidate rows")
    ap.add_argument("--reader-cap", type=int, default=600, dest="reader_cap")
    ap.add_argument("--ship-arm", default="BF_bias_ctx_share__counts", dest="ship_arm")
    ap.add_argument("--ship-budget", type=float, default=0.10, dest="ship_budget")
    ap.add_argument("--arms", default=None, help="comma-separated arm labels to run (default: all)")
    ap.add_argument("--aux", action="store_true", help="phase 7: the SOLE-AUX clause arm")
    ap.add_argument("--phase7", action="store_true", help="phase 7: cue-form, truncation, blocking and gold audits")
    ap.add_argument("--ship-only", action="store_true", dest="ship_only",
                    help="skip the arm sweep; rebuild the shipped asset + witness + diagnostics from the cached rows")
    args = ap.parse_args()
    t0 = time.time()
    out_dir = get_output_dir()
    ch = CategoryChannels()

    if args.self_test:
        # (1) the emission replay + the organ's own posterior agree with the organ's public tag()
        toks = WITNESS.split()
        tags, post, le = ch.read(toks)
        assert tags == ch.m.tag(toks), "replayed tags != organ tag()"
        assert le.shape == post.shape
        # (2) the graded cue actually separates the witness verb from its noun-flanked distractors
        cues = sentence_cues(ch, toks, tags, post, le)
        print("witness cues:", flush=True)
        for i, w in enumerate(toks):
            print("   %-10s tag=%-6s P(VERB)=%.4f lex_llr=%+.3f share=%.4f"
                  % (w, tags[i], post[i, ch.vi], cues[i]["lex_llr"], cues[i][SHARE]), flush=True)
        # (3) the glass-box gate agrees with nltk WordNet on this sentence
        for w in toks:
            assert has_verb_reading_bf(w) == has_verb_reading_nltk(w), "gate mismatch on %r" % w
        print("[self-test] PASS (emission replay, cue block, glass-box gate == nltk on the witness)", flush=True)
        return

    if args.reader:
        ap_path = os.path.join(HOOK_STATE, "predicate_detector_bf_counts_v1.json")
        a = json.loads(open(ap_path, encoding="ascii").read())
        model = load_combiner(a)
        ud = load_ud(UD_TEST, cap=None)
        # THE OPERATING POINT IS A MEASURED CHOICE, NOT A KNOB. Every candidate FP budget is run through the LIVE
        # reader and scored on what the reader's consumers actually receive -- event recall, event precision, F1 --
        # so the deployed threshold is the one that maximises the reader's event F1, not the one that flatters a
        # single sentence. All candidates stay inside the perceptron-era detector's budget (0.466 false verbs/sent).
        out = {"asset": ap_path, "arm": a.get("arm"), "by_budget": {}}
        for b, ent in sorted(a["thresholds_by_fp_budget_modern"].items(), key=lambda kv: float(kv[0])):
            if not ent["threshold"]:
                continue
            r = reader_end_to_end(ch, ud, model, float(ent["threshold"]), cap=args.reader_cap)
            out["by_budget"][b] = {"threshold": ent["threshold"], "reader": r}
            arms = r["arms"]
            f1 = lambda d: (2 * d["event_recall"] * d["event_precision"]   # noqa: E731
                            / max(1e-9, d["event_recall"] + d["event_precision"]))
            print("  budget %-5s th %.4f | BF r %.4f p %.4f F1 %.4f falseEv %.4f zeroEvSent %.4f | "
                  "BF+AUX r %.4f p %.4f falseEv %.4f zeroEvSent %.4f | BF-STANDIN %+.4f %s"
                  % (b, float(ent["threshold"]), arms["BF"]["event_recall"], arms["BF"]["event_precision"],
                     f1(arms["BF"]), arms["BF"]["false_events_per_sent"],
                     arms["BF"]["share_of_gold_verb_sentences_with_zero_events"],
                     arms["BF_AUX"]["event_recall"], arms["BF_AUX"]["event_precision"],
                     arms["BF_AUX"]["false_events_per_sent"],
                     arms["BF_AUX"]["share_of_gold_verb_sentences_with_zero_events"],
                     arms["BF_minus_STANDIN_event_recall"]["delta"],
                     "SEP" if arms["BF_minus_STANDIN_event_recall"]["ci_separated"] else "ns"), flush=True)
            print("        OFF r %.4f p %.4f falseEv %.4f zeroEvSent %.4f | STANDIN r %.4f p %.4f falseEv %.4f zeroEvSent %.4f"
                  % (arms["OFF"]["event_recall"], arms["OFF"]["event_precision"],
                     arms["OFF"]["false_events_per_sent"],
                     arms["OFF"]["share_of_gold_verb_sentences_with_zero_events"],
                     arms["STANDIN"]["event_recall"], arms["STANDIN"]["event_precision"],
                     arms["STANDIN"]["false_events_per_sent"],
                     arms["STANDIN"]["share_of_gold_verb_sentences_with_zero_events"]), flush=True)
        with open(out_dir / "reader_end_to_end.json", "w", encoding="ascii") as fh:
            json.dump({"anchor_name": "predicate_rescue_bf_cue_v1_reader", "results": out,
                       "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
        print("\n[done] %.0fs -> %s" % (time.time() - t0, out_dir / "reader_end_to_end.json"), flush=True)
        return

    cap = 200 if args.smoke else (None if args.full else 800)
    qcap = 200 if args.smoke else (2000 if not args.full else 4000)
    gcap = 200 if args.smoke else (4000 if args.full else 800)
    tag = "smoke" if args.smoke else ("full" if args.full else "mid")

    # -------------------------------------------------------------------- PHASE 7: the audits
    if args.phase7:
        import re as _re
        pops = [("modern", load_ud(UD_TEST, cap=cap)), ("gum", load_gum(cap=gcap)),
                ("qasrl", load_qasrl(QASRL, cap=qcap))]
        res = {}
        for name, sents in pops:
            p = out_dir / ("rows_%s_%s.json" % (name, tag))
            d = json.loads(p.read_text(encoding="ascii"))
            rows = [(r[0], r[1], r[2], r[3]) for r in d["rows"]]
            ns = d["nsent"]
            augment_rows(rows, sents, ch)
            ent = {"n_sent": ns, "n_candidates": len(rows), "n_positives": int(sum(r[3] for r in rows))}
            # (a) the cue-form question: does P(category | word) beat the emission log-ratio it replaces?
            ent["cue_auc"] = {c: rank_auc(rows, c) for c in ("lex_llr", "lex_odds", "lex_bias", "lex_pcw",
                                                             "stem_bias", "ctx_odds", "post_p", SHARE, CSHARE)}
            # (b) the hand-off truncation, and what widening it would buy / cost
            ent["truncation"] = truncation_analysis(rows, ns)
            # (c) the redundancy that blocks
            ent["blocking"] = blocking_dump(rows, ["lex_bias", "stem_bias", "ctx_odds", SHARE, CSHARE] +
                                            CUES_STRUCT_GRADED, ["ctx_odds", SHARE, CSHARE])
            # (d) ALTERNATE PATH A's population: the 'presents' class -- clauses the organ leaves with NO predicate
            vless = np.array([r[2]["clause_verbless"] for r in rows])
            clvl = np.array([r[2]["clause_local_verbless_g"] for r in rows])
            y = np.array([r[3] for r in rows])
            ent["path_A_population"] = {
                "positives_in_a_WHOLLY_VERBLESS_sentence": int(((vless > 0.5) & (y == 1)).sum()),
                "share_of_positives": round(float(((vless > 0.5) & (y == 1)).sum() / max(1, y.sum())), 4),
                "positives_whose_CLAUSE_has_no_verb_belief_above_0.5": int(((clvl > 0.5) & (y == 1)).sum()),
                "share_of_positives_clause": round(float(((clvl > 0.5) & (y == 1)).sum() / max(1, y.sum())), 4)}
            # (g) LABEL-PERMUTATION NULL. The cue block is rich (12 cues, one-hot binned) and the combiner is fitted
            #     under cross-validation -- so the sharpest check that it is reading predicate-hood and not fitting
            #     the population is to destroy the label and refit the WHOLE pipeline unchanged. If the machinery
            #     can manufacture recovery from nothing, this arm will show it.
            perm_rows = []
            rng = np.random.default_rng(20260914)
            ylab = np.array([r[3] for r in rows])
            rng.shuffle(ylab)
            for r, yy in zip(rows, ylab):
                perm_rows.append((r[0], r[1], r[2], int(yy)))
            pr = cv_scores(perm_rows, ["lex_bias", "stem_bias", "ctx_odds", SHARE, CSHARE] + CUES_STRUCT_GRADED, "rw")
            op = op_point(perm_rows, ns, pr, 0.10)
            ent["label_permutation_null"] = {
                "recovery_at_fp_le_0p10": round(op["recovery"], 4) if op else None,
                "note": "the same cue block, the same combiner, the same CV -- labels shuffled"}
            print("   label-permutation null recovery @fp<=0.10: %s"
                  % ent["label_permutation_null"]["recovery_at_fp_le_0p10"], flush=True)
            res[name] = ent
            print("== %s  AUC %s" % (name, {k: v for k, v in ent["cue_auc"].items()}), flush=True)
            print("   truncation %s" % json.dumps(ent["truncation"]), flush=True)
            print("   path-A population %s" % json.dumps(ent["path_A_population"]), flush=True)
            print("   cue correlations %s" % json.dumps(ent["blocking"]["cue_correlations"]), flush=True)
        # (e) the GUM gold-blank audit over the WHOLE population, not a sample
        gall = load_gum()
        blank = _re.compile(r"^[_—\-]+$")
        nb_tot = sum(1 for toks, gold in gall for i in gold if blank.match(toks[i]))
        ng_tot = sum(len(gold) for _t2, gold in gall)
        res["gum_gold_blank_audit"] = {"n_gold_verbs": ng_tot, "n_gold_verbs_that_are_blanks": nb_tot,
                                       "share": round(nb_tot / max(1, ng_tot), 4), "n_sentences": len(gall)}
        print("GUM gold blanks: %d of %d gold VERB tokens (%.4f)"
              % (nb_tot, ng_tot, nb_tot / max(1, ng_tot)), flush=True)
        # (f) the runtime/size cost of widening the truncation
        res["truncation_cost"] = truncation_cost(ch, load_ud(UD_TEST, cap=None), cap=400)
        print("truncation cost %s" % json.dumps(res["truncation_cost"]), flush=True)
        with open(out_dir / "phase7_audits.json", "w", encoding="ascii") as fh:
            json.dump({"anchor_name": "predicate_rescue_bf_cue_v1_phase7", "results": res,
                       "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
        print("\n[done] %.0fs -> %s" % (time.time() - t0, out_dir / "phase7_audits.json"), flush=True)
        return

    # -------------------------------------------------------------------- PHASE 7: the SOLE-AUX clause arm
    if args.aux:
        pops = [("modern", load_ud(UD_TEST, cap=cap)), ("gum", load_gum(cap=gcap)),
                ("qasrl", load_qasrl(QASRL, cap=qcap))]
        res = {}
        for name, sents in pops:
            p = out_dir / ("rows_%s_%s_aux.json" % (name, tag))
            if p.exists() and not args.rebuild:
                d = json.loads(p.read_text(encoding="ascii"))
                rows, ns, cov = [(r[0], r[1], r[2], r[3]) for r in d["rows"]], d["nsent"], d["cov"]
                print("  [cache] %s -> %d rows" % (p.name, len(rows)), flush=True)
            else:
                print("building SOLE-AUX rows for %s ..." % name, flush=True)
                rows, ns, cov = build_rows(sents, ch, progress=400, mode="aux")
                p.write_text(json.dumps({"rows": rows, "nsent": ns, "cov": cov}), encoding="ascii")
            augment_rows(rows, sents, ch)
            res[name] = evaluate_population("SOLE-AUX (%s)" % name, rows, ns, cov,
                                            n_boot=(400 if args.smoke else 2000),
                                            do_arms=["G_graded__rw", "P7_pcw__rw", "ABL_graded_struct_only__rw",
                                                     "ABL_lex_bias_only__counts", "ABL_ctx_odds_only__counts"])
            # the ALWAYS-FIRE arm: every sole-AUX token becomes the clause's predicate, no scoring at all.
            y = np.array([r[3] for r in rows])
            res[name]["arms"]["ALWAYS_FIRE_sole_aux"] = {
                "recovery": 1.0, "n_promoted": len(rows), "n_positives": int(y.sum()),
                "precision": round(float(y.mean()), 4),
                "fp_per_sent": round(float((len(rows) - y.sum()) / max(1, ns)), 4)}
            a = res[name]["arms"]["ALWAYS_FIRE_sole_aux"]
            print("  ALWAYS-FIRE sole-AUX: recovery 1.0000  precision %.4f  fp/sent %.4f  (n_cand %d, n_pos %d)"
                  % (a["precision"], a["fp_per_sent"], len(rows), a["n_positives"]), flush=True)
        with open(out_dir / "aux_arm.json", "w", encoding="ascii") as fh:
            json.dump({"anchor_name": "predicate_rescue_bf_cue_v1_aux_arm", "results": res,
                       "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
        print("\n[done] %.0fs -> %s" % (time.time() - t0, out_dir / "aux_arm.json"), flush=True)
        return

    def cached(label, builder):
        p = out_dir / ("rows_%s_%s.json" % (label, tag))
        if p.exists() and not args.rebuild:
            d = json.loads(p.read_text(encoding="ascii"))
            print("  [cache] %s -> %d rows / %d sentences" % (p.name, len(d["rows"]), d["nsent"]), flush=True)
            return [(r[0], r[1], r[2], r[3]) for r in d["rows"]], d["nsent"], d["cov"]
        rows, ns, cov = builder()
        p.write_text(json.dumps({"rows": rows, "nsent": ns, "cov": cov}), encoding="ascii")
        return rows, ns, cov

    print("building MODERN rows (UD-EWT test, live category organ) ...", flush=True)
    ud = load_ud(UD_TEST, cap=cap)
    mod_rows, mod_ns, mod_cov = cached("modern", lambda: build_rows(ud, ch, progress=400))
    print("building GUM rows (modern, 12+ genres, held out) ...", flush=True)
    g = load_gum(cap=(200 if args.smoke else (4000 if args.full else 800)))
    g_rows, g_ns, g_cov = cached("gum", lambda: build_rows(g, ch, progress=400))
    print("building QA-SRL rows (modern OOD) ...", flush=True)
    q = load_qasrl(QASRL, cap=qcap)
    q_rows, q_ns, q_cov = cached("qasrl", lambda: build_rows(q, ch, progress=400))
    for _rows, _s in ((mod_rows, ud), (g_rows, g), (q_rows, q)):
        augment_rows(_rows, _s, ch)          # the word-only cues (lex_pcw): no organ pass needed

    nb = 400 if args.smoke else 2000
    if args.ship_only:
        prev = {}
        mp = out_dir / "metrics.json"
        if mp.exists():
            prev = json.loads(mp.read_text(encoding="ascii")).get("results", {})
        results = {k: prev.get(k, {}) for k in ("modern_ud_ewt_test", "modern_gum", "qasrl_dev_modern_ood")}
        print("  [ship-only] arm tables carried over from the previous metrics.json", flush=True)
    else:
        only = args.arms.split(",") if args.arms else None
        results = {"modern_ud_ewt_test": evaluate_population("MODERN (UD-EWT test)", mod_rows, mod_ns, mod_cov, n_boot=nb, do_arms=only),
                   "modern_gum": evaluate_population("MODERN (GUM/GENTLE, 12+ genres)", g_rows, g_ns, g_cov, n_boot=nb, do_arms=only),
                   "qasrl_dev_modern_ood": evaluate_population("QA-SRL dev (modern OOD)", q_rows, q_ns, q_cov, n_boot=nb, do_arms=only)}

    # ---- gate-equivalence control: the glass-box morphology gate vs the landed nltk WordNet gate
    if args.gate_control or args.full:
        print("\ngate control: glass-box morphology vs nltk WordNet over the candidate vocabulary ...", flush=True)
        vocab = sorted({t for toks, _ in ud for t in toks})
        agree = sum(1 for w in vocab if has_verb_reading_bf(w) == has_verb_reading_nltk(w))
        results["gate_equivalence_control"] = {"n_types": len(vocab), "n_agree": agree,
                                               "agreement": round(agree / max(1, len(vocab)), 6)}
        print("  %d/%d word types agree (%.6f)" % (agree, len(vocab), agree / max(1, len(vocab))), flush=True)

    # ---- SHIP: the plastic count combiner trained on ALL modern rows (UD test + QA-SRL), threshold on modern
    spec_by = dict((s[0], (s[1], s[2])) for s in arm_specs())
    ship_names, ship_kind = spec_by[args.ship_arm]
    _MK = {"counts": CountCombiner, "rw": RWCombiner}
    ship = _MK[ship_kind](ship_names).accrue(mod_rows + g_rows + q_rows).finalize()
    held = cv_scores(mod_rows, ship_names, ship_kind)
    # the threshold is an FP-BUDGET KNOB. It is set on the SHIPPED (all-data) model so the deployed scorer keeps the
    # budget it is calibrated to; the held-out (CV) threshold is recorded beside it as the honest generalisation check.
    full_scores = score_counts(ship, mod_rows)
    ths = {}
    for b in BUDGETS:
        o_full = op_point(mod_rows, mod_ns, full_scores, b)
        o_held = op_point(mod_rows, mod_ns, held, b)
        ths[str(b)] = {"threshold": round(float(o_full["th"]), 6) if o_full else None,
                       "recovery_full_fit": round(o_full["recovery"], 4) if o_full else None,
                       "heldout_threshold": round(float(o_held["th"]), 6) if o_held else None,
                       "heldout_recovery": round(o_held["recovery"], 4) if o_held else None}
    th_ship = ths[str(args.ship_budget)]["threshold"] or 0.5
    asset = ship.to_asset()
    asset.update({"operating_threshold": round(float(th_ship), 6),
                  "operating_budget_fp_per_sent": args.ship_budget,
                  "thresholds_by_fp_budget_modern": ths,
                  "gate": "glassbox_morphology_verb_lemma_and_non_aux",
                  "arm": args.ship_arm,
                  "cue_source": ("hdlab.lexical_categories emission counts (lex_bias) + the lemma organ's stem route "
                                 "(stem_bias) + the posterior read as clause competition (verb_share / "
                                 "clause_verb_share) and graded log-odds (ctx_odds) + 6 structural cues"),
                  "trained_on": "UD-EWT-test + GUM/GENTLE + QA-SRL-dev under the LIVE category organ (self-supervised auto-labels)",
                  "built": datetime.now(timezone.utc).isoformat()})
    os.makedirs(HOOK_STATE, exist_ok=True)
    ap_path = os.path.join(HOOK_STATE, "predicate_detector_bf_counts_v1.json")
    with open(ap_path, "w", encoding="ascii") as fh:
        json.dump(asset, fh)
    print("\n  shipped asset -> %s  (threshold %.4f)" % (ap_path, th_ship), flush=True)

    wit = witness_report(ch, ship, ship_names, th_ship)
    results["witness"] = wit
    print("  WITNESS %r -> rescues 'presents': %s ; rejects distractors: %s"
          % (WITNESS, wit["rescues_presents"], wit["rejects_distractors"]), flush=True)
    for r in wit["candidates"]:
        print("     %-10s tag=%-5s P(VERB)=%.4f lex_llr=%+.3f share=%.4f score=%.4f %s"
              % (r["tok"], r["tag"], r["post_VERB"], r["lex_llr"], r["verb_share"], r["score"],
                 "RESCUED" if r["rescued"] else ""), flush=True)

    results["shipped"] = {"arm": args.ship_arm, "cues": list(ship_names), "budget": args.ship_budget,
                          "threshold": th_ship, "thresholds_by_fp_budget": ths}

    # ---- DIAGNOSTICS: why the two populations behave differently, and what the residual misses ARE
    print("\ndiagnostics ...", flush=True)
    results["diagnostics"] = {
        "modern": diagnose("MODERN (UD-EWT test)", mod_rows, mod_ns, ud, ship, th_ship),
        "gum": diagnose("MODERN (GUM)", g_rows, g_ns, g, ship,
                        op_point(g_rows, g_ns, score_counts(ship, g_rows), args.ship_budget)["th"]
                        if op_point(g_rows, g_ns, score_counts(ship, g_rows), args.ship_budget) else th_ship),
        "qasrl": diagnose("QA-SRL dev (modern OOD)", q_rows, q_ns, q, ship,
                          op_point(q_rows, q_ns, score_counts(ship, q_rows), args.ship_budget)["th"]
                          if op_point(q_rows, q_ns, score_counts(ship, q_rows), args.ship_budget) else th_ship)}
    for k, ss in (("modern", ud), ("gum", g), ("qasrl", q)):
        results["diagnostics"][k]["gate_gap_breakdown"] = gate_gap_breakdown(ch, ss)
        print("  %-8s gate gap: %s" % (k, results["diagnostics"][k]["gate_gap_breakdown"]), flush=True)
    for k in ("modern", "gum", "qasrl"):
        dd = results["diagnostics"][k]
        print("  %-8s base-rate %.4f  unknown-form(cand) %.4f  unknown-form(pos) %.4f  cue AUC %s"
              % (k, dd["base_rate_positives_among_candidates"], dd["unknown_form_rate_among_candidates"],
                 dd["unknown_form_rate_among_positives"],
                 {c: v for c, v in dd["cue_auc"].items()}), flush=True)
        print("     missed at op point: %d ; false promotions: %d ; commonest false promotions: %s"
              % (dd.get("n_missed_at_operating_point", -1), dd.get("n_false_promotions_at_operating_point", -1),
                 ", ".join(dd.get("top_false_promotions", [])[:12])), flush=True)

    payload = {"anchor_name": "predicate_rescue_bf_cue_v1", "results": results,
               "asset": os.path.relpath(ap_path, _REPO),
               "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}
    with open(out_dir / "metrics.json", "w", encoding="ascii") as fh:
        json.dump(payload, fh, indent=2)
    print("\n[done] %.0fs -> %s" % (time.time() - t0, out_dir / "metrics.json"), flush=True)


if __name__ == "__main__":
    main()
