"""hdlab/predicate_detector.py -- REGISTER-ROBUST GLASS-BOX PREDICATE (verbhood) RECALL.

The landed form of the owner-DONE `register_robust_event_detection_the_reader_drops_events_when_the_
tagger_misses_the_verb` solution. The live UPOS==VERB event detector (situation_reader.tense_agnostic)
silently DROPS a whole clause -- who did what to whom, gone -- whenever the POS tagger mistags a real
verb as a noun/adj (common in archaic / register-diverse / noun-flanked prose). This organ recovers the
dropped predicates ADDITIVELY: for every non-VERB non-AUX token with a WordNet verb-reading, a small
7-weight LOGISTIC combiner over REGISTER-INVARIANT cues (the noisy-channel likelihood x structural prior;
Gibson 2013) scores P(dropped-predicate); above threshold the reader fires an extra event. It is
ADDITIVE-ONLY -> the events the reader already detects and their role picks are BYTE-IDENTICAL (no
regression by construction). Glass-box, PARSE-FREE, NO external LLM.

Validated (verification/test_register_predicate_detector.py, 12/12): recovery of tagger-DROPPED verbs
@ FP<=0.5 false-verbs/sentence -- MODERN (UD-EWT test, 5-fold CV) 0.8989, 19c-TRANSFER (LitBank, ZERO
19c labels) 0.5625, both CI-separated over the info-free random-verbhood twin; crosses the parent's
structure-only modern wall (0.16). The threshold in the asset is calibrated to FP<=0.5/sent on MODERN;
on denser 19c candidate space the SAME threshold rises to ~1.4 FP/sent (it is an FP-budget knob).

The 7 features + learned weights (standardized) are the brain's noisy-channel COMBINATION made a LEARNED
weighting (not hand AND/OR logic): verb_margin +1.63 (tagger emission VERB-minus-best-non-VERB = lexical
LIKELIHOOD), morph_finite +0.46, clause_verbless +0.43 (one-predicate-per-clause competition),
subj_before +0.39, frame_anchor +0.21 (Mintz), rel_position -0.32, obj_after -0.12.

All scoring functions are promoted VERBATIM from experiments/exp_register_predicate_detector_v1.py
(feats_parsefree / verb_margin / morph_finite) + experiments/exp_whodidwhat_verb_id_recoverable_v1.py
(has_verb_reading / frame_verb_cue) so this organ carries NO experiments/ dependency. Scoring is pure
Python (no numpy) -- it reproduces sklearn LogisticRegression.predict_proba on standardized features
EXACTLY (sigmoid(coef . standardize(feats) + intercept)).
"""
from __future__ import annotations

__bf_status__ = 'BF_SPIRIT'   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors notes/bf_status_registry.jsonl
__bf_verified__ = '2026-09-09 BF-certification pass (reader CATALOG owner-DONE + BRAIN_FOUNDATIONAL_AUDIT §2b; strategy first-hand cross-ref)'
__bf_note__ = 'noisy-channel logistic over interpretable register cues, additive-only (no gold-fit decision); CAT genuinely-BF'
__bf_corrections__ = []


import json
import math
import os
from typing import Dict, List, Sequence, Tuple

from hdlab.pos_tagger import pos_features
from hdlab.thematic_role_labeler import lemma_verb

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_ASSET = os.path.join(_REPO, "data/frontend_assets/predicate_detector_ud_qasrl.json")

# Feature order MUST match the asset's `feat_names` (and feats_parsefree below).
FEAT_NAMES = ["verb_margin", "frame_anchor", "subj_before", "obj_after",
              "morph_finite", "clause_verbless", "rel_position"]
NOMINAL = ("NOUN", "PROPN", "PRON")


# ---- candidate gate + cues (promoted VERBATIM from the experiment cells; glass-box, register-invariant) ----
_WN = None


def has_verb_reading(tok: str) -> bool:
    """Glass-box lexical verbhood: WordNet has a VERB synset for the token or its de-inflected lemma.
    (verbatim from exp_whodidwhat_verb_id_recoverable_v1.has_verb_reading)"""
    global _WN
    if _WN is None:
        from hdlab.lexicon_foundation import wordnet as wn
        _WN = wn
    low = tok.lower()
    if _WN.synsets(low, pos="v"):
        return True
    return bool(_WN.synsets(lemma_verb(low), pos="v"))


def frame_verb_cue(toks: Sequence[str], pos: Sequence[str], ix: int, k: int = 3) -> bool:
    """Mintz frequent-frame verbhood (clause-local, low-FP): the token at ix is the clause's predicate if
    it has a VERB reading, a nominal SUBJECT sits within k tokens BEFORE it, a nominal OBJECT sits within k
    tokens AFTER it, and NO already-VERB-tagged token intervenes between that subject and ix.
    (verbatim from exp_whodidwhat_verb_id_recoverable_v1.frame_verb_cue)"""
    if pos[ix] == "VERB" or not has_verb_reading(toks[ix]):
        return False
    subs = [j for j in range(max(0, ix - k), ix) if pos[j] in NOMINAL]
    if not subs:
        return False
    objs = [j for j in range(ix + 1, min(len(toks), ix + 1 + k)) if pos[j] in NOMINAL]
    if not objs:
        return False
    if any(pos[j] == "VERB" for j in range(subs[-1] + 1, ix)):
        return False   # another verb already occupies this clause's predicate slot
    return True


def verb_margin(obs: Sequence[str], i: int, W: Dict[str, float], tags: Sequence[str]) -> float:
    """emission(VERB) - best emission over non-VERB non-AUX tags (the noisy-channel lexical LIKELIHOOD).
    (verbatim from exp_register_predicate_detector_v1.verb_margin)"""
    s = {t: sum(W.get(f, 0.0) for f in pos_features(obs, i, t)) for t in tags}
    v = s.get("VERB", -1e9)
    best_non = max(val for t, val in s.items() if t not in ("VERB", "AUX"))
    return v - best_non


def morph_finite(w: str) -> float:
    """Finite/participial verb morphology (register-inclusive incl. archaic -eth/-est/'d/-th).
    (verbatim from exp_register_predicate_detector_v1.morph_finite)"""
    wl = w.lower()
    for suf in ("ing", "eth", "est", "ed", "th", "'d", "es", "s", "d", "n"):
        if wl.endswith(suf) and len(wl) > len(suf) + 1:
            return 1.0
    return 0.0


def feats_parsefree(toks: Sequence[str], pos: Sequence[str], i: int,
                    W: Dict[str, float], tags: Sequence[str]) -> List[float]:
    """The 7 register-invariant, parse-free cues in FEAT_NAMES order.
    (verbatim from exp_register_predicate_detector_v1.feats_parsefree)"""
    subj = 1.0 if any(pos[j] in NOMINAL for j in range(max(0, i - 4), i)) else 0.0
    obj = 1.0 if any(pos[j] in NOMINAL for j in range(i + 1, min(len(toks), i + 5))) else 0.0
    frame = 1.0 if frame_verb_cue(toks, pos, i) else 0.0
    verbless = 0.0 if any(p == "VERB" for p in pos) else 1.0
    relpos = i / max(1, len(toks) - 1)
    return [verb_margin(toks, i, W, tags), frame, subj, obj, morph_finite(toks[i]), verbless, relpos]


def _sigmoid(z: float) -> float:
    if z >= 0:
        return 1.0 / (1.0 + math.exp(-z))
    e = math.exp(z)
    return e / (1.0 + e)


class PredicateDetector:
    """The static logistic predicate detector (asset = data/frontend_assets/predicate_detector_ud_qasrl.json).

    Usage (the reader wire): for each token, `is_candidate` gates it (non-VERB non-AUX + WordNet verb-reading);
    `score` returns P(dropped-predicate); `rescue_indices` returns the (idx, score) pairs above threshold to
    fire additional events for. The tagger weights/tag-set (`W`, `tags`) come from the caller's PosTagger
    (`tagger._perc.weights`, `tagger.tags`) -- the SAME tagger the detector was trained against.
    """

    def __init__(self, feat_names, coef, intercept, mu, sd, threshold,
                 gate="wordnet_verb_reading_and_non_aux", with_parse=False):
        if list(feat_names) != FEAT_NAMES:
            raise ValueError("predicate_detector asset feat order mismatch: %r" % (feat_names,))
        if with_parse:
            raise ValueError("this organ lands the PARSE-FREE detector only (with_parse asset unsupported)")
        self.feat_names = list(feat_names)
        self.coef = [float(c) for c in coef]
        self.intercept = float(intercept)
        self.mu = [float(x) for x in mu]
        self.sd = [float(x) if float(x) != 0.0 else 1.0 for x in sd]
        self.threshold = float(threshold)
        self.gate = gate

    @classmethod
    def load(cls, path: str = DEFAULT_ASSET) -> "PredicateDetector":
        with open(path, encoding="utf-8") as f:
            a = json.load(f)
        return cls(a["feat_names"], a["coef"], a["intercept"], a["mu"], a["sd"],
                   a["operating_threshold_fp_le_0p5_modern"],
                   gate=a.get("gate", "wordnet_verb_reading_and_non_aux"),
                   with_parse=bool(a.get("with_parse", False)))

    def is_candidate(self, toks: Sequence[str], pos: Sequence[str], i: int) -> bool:
        """The register-invariant rescue gate: non-VERB non-AUX token with a WordNet verb-reading."""
        return pos[i] not in ("VERB", "AUX") and has_verb_reading(toks[i])

    def score(self, toks: Sequence[str], pos: Sequence[str], i: int,
              W: Dict[str, float], tags: Sequence[str]) -> float:
        """P(token i is a tagger-dropped event predicate). Reproduces sklearn predict_proba on standardized
        features exactly: sigmoid(coef . (feats - mu)/sd + intercept)."""
        fv = feats_parsefree(toks, pos, i, W, tags)
        z = self.intercept
        for k in range(len(self.coef)):
            z += self.coef[k] * ((fv[k] - self.mu[k]) / self.sd[k])
        return _sigmoid(z)

    def rescue_indices(self, toks: Sequence[str], pos: Sequence[str],
                       W: Dict[str, float], tags: Sequence[str],
                       threshold: float = None) -> List[Tuple[int, float]]:
        """(idx, score) for every gated candidate the detector promotes to an event predicate (score >= th).
        ADDITIVE: excludes tokens already tagged VERB/AUX -> never touches an existing detection."""
        th = self.threshold if threshold is None else float(threshold)
        out = []
        for i in range(len(toks)):
            if pos[i] in ("VERB", "AUX"):
                continue
            if not has_verb_reading(toks[i]):
                continue
            p = self.score(toks, pos, i, W, tags)
            if p >= th:
                out.append((i, p))
        return out


# =====================================================================================================================
# THE BRAIN-FOUNDATIONAL RESCUE (2026-09-14, pri-107 solver)
# ---------------------------------------------------------------------------------------------------------------------
# `verb_margin` above reads the SUPERVISED PERCEPTRON's emission score. Since 2026-09-12 the live category organ is the
# count-based generative model (hdlab.lexical_categories) and there is no perceptron on the live path, so the reader fell
# through to a bare posterior threshold (P(VERB) >= PREDICATE_RESCUE_MIN_P = 0.3) -- which recovered a quarter of the
# dropped verbs and added ZERO events to the landing witness. Measured 2026-09-14: 72-78% of the real verbs the organ
# drops carry a verb belief BELOW that bar, so the bar, not the evidence, was the binding constraint.
#
# THE BRAIN. Predicate-hood is a noisy-channel decision (Gibson 2013): a LEXICAL LIKELIHOOD (what this word usually does)
# combined with a STRUCTURAL PRIOR (one predicate per clause -- Spivey-Knowlton 1993; frequent frames -- Mintz 2003;
# finite morphology -- Monaghan 2005; morphological decomposition -- Pinker & Ullman words-and-rules). The cue block:
#
#   lex_bias    log(n(VERB, w) + lam) - log max_{c != VERB/AUX} (n(c, w) + lam)  -- the graded per-lexeme noun/verb bias
#               (Lee & Federmeier 2009 graded category competition), straight off the emission COUNTS. Conditioning on
#               the WORD rather than on the CATEGORY is what removes the frequency term: the raw emission log-ratio
#               P(w|VERB)/P(w|c) tracks how frequent the word is (its add-lambda floor for an unseen cell is a constant,
#               not an estimate) and INVERTS on exactly this population -- 'sheet', never seen as a verb, outscored
#               'presents', which is (measured: -4.48 vs -5.16). A word with no lexical entry has no bias to read, so
#               it falls back to the organ's own novel-form (productivity) estimate, which its emission row already is.
#   stem_bias   the SAME bias read through the lemma organ's rule route (`_log_stem_prior`): 'presents' = 'present' + -s
#               and the stem is a known verb. The category organ carries this table but consults it only for rare forms
#               or on a conflict, so a frequent NOUN form with a VERB stem never gets it (Pinker & Ullman dual route;
#               Rastle & Davis obligatory decomposition).
#   verb_share / clause_verb_share    post_i(VERB) / sum_j post_j(VERB) over the sentence and over the CLAUSE --
#               ONE-PREDICATE-PER-CLAUSE COMPETITION expressed as a COMPETITION. An absolute threshold on an
#               unnormalised belief structurally cannot see that 'presents' holds 38% of the sentence's entire verb
#               belief while every rival holds under 3%. Clause domains are cut by the closed-class cues a reader has
#               before any parse (punctuation, coordinators, subordinators) -- no parse, no treebank.
#   ctx_odds    log post_i(VERB) - log max_{c != VERB/AUX} post_i(c) -- the settled belief read as GRADED LOG-ODDS
#               rather than as a probability against a fixed bar.
#   + the six register-invariant structural cues above (frame_anchor / subj_before / obj_after / morph_finite /
#     clause_verbless / rel_position) and clause_local_verbless, unchanged in form.
#
# THE COMBINER IS PLASTIC, NOT A FITTED WEIGHT VECTOR. Two forms are supported, selected by the asset's `kind`:
#   "counts_naive_bayes"  Christiansen & Chater multiple-cue integration as naive Bayes -- every weight is
#                         log((n_pos(cue,bin)+lam)/(N_pos+lam B)) - log((n_neg(cue,bin)+lam)/(N_neg+lam B)), ONE PURE
#                         FUNCTION of two count tables.
#   "rescorla_wagner"     error-driven cue competition -- w += eta * (outcome - expectation) over the PRESENT cue units
#                         (Rescorla & Wagner 1972; Ellis 2006, Ramscar 2010 for language cues). This is the form that
#                         handles REDUNDANT cues: three of the cues are three reads of one channel (the posterior), and
#                         naive Bayes counts that evidence three times while the delta rule blocks it.
# Both take `observe(cues, label)` -- one update per confirmed outcome, no batch fit, no gradient library. The threshold
# is an FP-BUDGET knob, not a parameter of the model.
#
# THE GATE IS GLASS-BOX. `has_verb_reading` above imports nltk WordNet AT INFERENCE. `has_verb_reading_glassbox` asks the
# morphology organ instead (hdlab.morphology -- a byte-identical pure-python port of morphy over an offline WordNet
# export). Measured agreement over the UD-EWT test vocabulary: 5612/5629 word types (0.99698).
# =====================================================================================================================

BF_ASSET = os.path.join(_REPO, "data/frontend_assets/predicate_detector_bf_counts_v1.json")
BF_ASSET_STAGING = os.path.join(_REPO, "data/hook_state/predicate_detector_bf_counts_v1.json")

# THE OPERATING POINT IS AN FP-BUDGET KNOB, NOT A MODEL PARAMETER. The asset carries a calibrated threshold for
# each false-verbs-per-sentence budget; HDLAB_PREDICATE_RESCUE_BUDGET selects one. Measured through the LIVE reader
# on modern gold (UD-EWT test, 2077 sentences, 1240 of them with a gold verb) -- event recall / event precision /
# false events per sentence / share of gold-verb sentences that produce NO EVENT AT ALL:
#     budget   thresh   recall  precis  falseEv  blind-clauses
#     (off)        --   0.9186  0.9370   0.0775        0.0444
#     stand-in   0.30   0.9305  0.9263   0.0929        0.0403
#     0.05     0.4352   0.9413  0.9028   0.1271        0.0315
#     0.10     0.2592   0.9501  0.8715   0.1757        0.0266   <- DEFAULT (the board A/B was run here: flat)
#     0.15     0.1712   0.9532  0.8403   0.2273        0.0242
#     0.25     0.0929   0.9585  0.7907   0.3182        0.0210
# Recall rises and precision falls monotonically: 0.10 is the tightest point whose recall gain is CI-separated
# over BOTH floors, and it is the point the 7-dimension modern board was measured flat at (0.6109 -> 0.6109).
BUDGET = os.environ.get("HDLAB_PREDICATE_RESCUE_BUDGET", "")

# THE SOLE-AUX CLAUSE ARM (2026-09-14 phase 7), DEFAULT OFF -- with a measured reason, not an omission.
# UD's AUX/VERB split is an ANNOTATION CONVENTION: UD tags main-verb / copular `be` and `have` as AUX, and the
# reader fires events only on UPOS==VERB, so a clause whose only verbal token is AUX-tagged emits NO event at all.
# That class is 4.7-38.8% of the real verbs the organ "drops" and it is invisible to an ADDITIVE rescue by
# construction. The brain has no such convention -- when nothing else competes for the clause's predicate slot,
# the auxiliary IS the predicate (one predicate per clause, Spivey-Knowlton 1993).
# MEASURED, and the two instruments DISAGREE, which is the whole point:
#   * against UD's own VERB column the arm looks poor -- only 11.6% (UD-EWT) / 10.2% (GUM) / 2.3% (QA-SRL) of
#     sole-AUX candidates are gold VERB, because UD labels the copula AUX in the gold column too. The gold cannot
#     adjudicate a question about its own convention.
#   * on the CONVENTION-FREE instrument -- does the clause produce an event at all? -- the arm removes nearly half
#     the reader's remaining blind clauses: gold-verb sentences yielding ZERO events fall 33 -> 18 of 1240 at the
#     default budget (0.0266 -> 0.0145; OFF is 0.0444), event recall +0.0096 CI[+0.0061,+0.0136] CI-separated.
#     Cost: +0.06 false events/sentence and 3.5 points of event precision (0.8715 -> 0.8364).
# It is OFF by default only because the 7-dimension board A/B was run on the noun arm alone; turn it on with
# HDLAB_PREDICATE_RESCUE_AUX=1 and re-run the board. It preserves the additive contract (it only ever ADDS).
# SUPERSEDED 2026-09-14 (pri 110), AND THE DEFAULT STAYS OFF WITH A MEASURED REASON.  The question this arm asks --
# does the clause's tense carrier hold the predicate slot? -- is now answered ONCE, upstream, where BOTH consumers can
# read it (attachment_arm.predicate_slot_occupancy, applied to the posterior lexical_categories hands down), so a
# carrier that IS its clause's predicate arrives here already tagged VERB and fires its event without any rescue.
# Measured through this same reader on UD-EWT test (2077 sentences, 1240 with a gold verb), at the same budget:
#     arm                             recall  precis  falseEv  blind clauses
#     rescue noun arm only (live)     0.9501  0.8715   0.1757    33 / 1240
#     + THIS boolean sole-AUX arm     0.9597  0.8364   0.2354    18 / 1240
#     upstream predicate slot (110)   0.9812  0.8621   0.1969     9 / 1240
#     both together                   0.9820  0.8305   0.2513     9 / 1240
# The upstream form DOMINATES this arm on recall, precision AND blind clauses at once, and stacking this arm on top
# buys +0.0008 recall for -0.0316 precision.  Left selectable for the ablation; not the recommended operating point.
AUX_ARM = os.environ.get("HDLAB_PREDICATE_RESCUE_AUX", "0") == "1"

# clause boundaries: the closed-class cues a reader has BEFORE any parse
CLAUSE_BREAK = {",", ";", ":", "--", "and", "but", "or", "that", "which", "who", "because", "while",
                "when", "if", "though", "although", "so", "then"}

_MORPH = None


def has_verb_reading_glassbox(tok: str) -> bool:
    """The rescue gate with NO nltk at inference: the morphology organ's verb route finds a WordNet verb lemma for this
    surface form (exception store + affix detachment + lexical check -- the decision wn.synsets(w, 'v') makes)."""
    global _MORPH
    if _MORPH is None:
        from hdlab.morphology import GlassBoxMorphology, _ASSET_DIR
        _MORPH = GlassBoxMorphology(_ASSET_DIR, mode="morphy")
    return _MORPH.morphy(tok.lower(), "v") is not None


def category_emission(lc, toks: Sequence[str]):
    """The category organ's EMISSION rows log P(word_i | c) -- its lexical / morpho-orthographic channel BEFORE the
    sequential prior. Replays the organ's own `_log_emit` with the per-sentence state `posterior` sets up, so these are
    the organ's numbers, not a re-implementation."""
    import numpy as _np

    from hdlab import lexical_categories as _LC
    words = list(toks)
    lc._sent_pos = [_LC.position_class(words, i) for i in range(len(words))]
    lc._sent_lows = [w.lower() for w in words]
    lc._sent_i = 0
    return _np.stack([lc._log_emit(w) for w in words])


def clause_spans(toks: Sequence[str], tags: Sequence[str]) -> List[int]:
    """Clause-sized competition domains (Spivey-Knowlton one-predicate-per-clause is a CLAUSE constraint, and a
    sentence routinely holds several). Boundaries from punctuation, coordinators and subordinators only."""
    n = len(toks)
    b = [0]
    for i in range(1, n):
        if toks[i].lower() in CLAUSE_BREAK or tags[i] in ("SCONJ", "CCONJ"):
            b.append(i)
    b.append(n)
    span = [0] * n
    for k in range(len(b) - 1):
        for i in range(b[k], b[k + 1]):
            span[i] = k
    return span


def bf_cue_block(lc, toks: Sequence[str], tags: Sequence[str], post, le) -> List[Dict[str, float]]:
    """The per-token cue dict (see the block comment). `post` = the organ's forward-backward posterior [n, T];
    `le` = its emission rows [n, T]."""
    vi = lc.tags.index("VERB")
    ai = lc.tags.index("AUX")
    non = [j for j in range(len(lc.tags)) if j not in (vi, ai)]
    nom = [lc.tags.index(t) for t in NOMINAL if t in lc.tags]
    n = len(toks)
    den = float(post[:, vi].sum()) or 1e-12
    verbless = 0.0 if any(t == "VERB" for t in tags) else 1.0
    span = clause_spans(toks, tags)
    cl_den, cl_verbless, cl_verbless_g = {}, {}, {}
    for k in set(span):
        ix = [i for i in range(n) if span[i] == k]
        cl_den[k] = float(post[ix, vi].sum()) or 1e-12
        cl_verbless[k] = 0.0 if any(tags[i] == "VERB" for i in ix) else 1.0
        cl_verbless_g[k] = 1.0 - float(post[ix, vi].max())
    # GRADED STRUCTURAL CUES. The six structural cues above read the ARGMAX TAG -- a point estimate -- so one
    # upstream mis-tag zeroes them, and an upstream mis-tag is exactly what is going on in the sentences this organ
    # exists for (measured on the witness: 'lake' is tagged ADJ, so subj_before reads 0 for 'presents' although the
    # organ's own posterior puts 0.34 of its belief on a nominal reading of 'lake'). The organ hands DOWN a
    # distribution; these read the distribution. P(nominal) = P(NOUN) + P(PROPN) + P(PRON); "no verb in the clause"
    # becomes 1 - max_j P(VERB_j) rather than a hard flag.
    pnom = post[:, nom].sum(axis=1)
    pverb = post[:, vi]
    lam = lc.lam
    out = []
    for i in range(n):
        wl = toks[i].lower()
        if wl in lc.vocab:
            bias = float(math.log(lc.emit["VERB"][wl] + lam)
                         - max(math.log(lc.emit[lc.tags[j]][wl] + lam) for j in non))
        else:
            bias = float(le[i, vi] - max(le[i, j] for j in non))
        srow = lc._log_stem_prior(wl)
        stem = bias if srow is None else float(srow[vi] - max(srow[j] for j in non))
        pv = float(post[i, vi])
        pn = max(float(post[i, j]) for j in non)
        subj_g = max([float(pnom[j]) for j in range(max(0, i - 4), i)], default=0.0)
        obj_g = max([float(pnom[j]) for j in range(i + 1, min(n, i + 5))], default=0.0)
        sl = max([float(pnom[j]) for j in range(max(0, i - 3), i)], default=0.0)
        sr = max([float(pnom[j]) for j in range(i + 1, min(n, i + 4))], default=0.0)
        btw = [float(pverb[j]) for j in range(max(0, i - 3), i)]
        out.append({
            "lex_bias": bias,
            "stem_bias": stem,
            "verb_share": pv / den,
            "clause_verb_share": pv / cl_den[span[i]],
            "clause_local_verbless": cl_verbless[span[i]],
            "subj_before_g": subj_g,
            "obj_after_g": obj_g,
            "frame_anchor_g": sl * sr * (1.0 - (max(btw) if btw else 0.0)),
            "clause_verbless_g": 1.0 - float(pverb.max()),
            "clause_local_verbless_g": cl_verbless_g[span[i]],
            "ctx_odds": math.log(max(pv, 1e-12)) - math.log(max(pn, 1e-12)),
            "frame_anchor": 1.0 if frame_verb_cue(toks, tags, i) else 0.0,
            "subj_before": 1.0 if any(tags[j] in NOMINAL for j in range(max(0, i - 4), i)) else 0.0,
            "obj_after": 1.0 if any(tags[j] in NOMINAL for j in range(i + 1, min(n, i + 5))) else 0.0,
            "morph_finite": morph_finite(toks[i]),
            "clause_verbless": verbless,
            "rel_position": i / max(1, n - 1),
        })
    return out


class BFPredicateDetector:
    """The rescue's PLASTIC combiner over the brain-foundational cue block. Asset (built by
    experiments/exp_predicate_rescue_bf_cue_v1.py): data/frontend_assets/predicate_detector_bf_counts_v1.json.
    `kind` selects naive-Bayes cue integration over counts or Rescorla-Wagner error-driven cue competition; both
    expose `observe(cues, label)` as the online path."""

    def __init__(self, a):
        self.kind = a.get("kind", "counts_naive_bayes")
        self.names = list(a["names"])
        self.bin_spec = {k: tuple(v) for k, v in a["bin_spec"].items()}
        self.threshold = float(a["operating_threshold"])
        self.budget = float(a.get("operating_budget_fp_per_sent", -1.0))
        # the threshold is an FP-BUDGET KNOB: the asset carries the calibrated threshold for each budget so a
        # consumer that needs recall rather than precision can select its own operating point explicitly.
        self.thresholds_by_budget = dict(a.get("thresholds_by_fp_budget_modern", {}))
        if self.kind == "rescorla_wagner":
            self.eta = float(a.get("eta", 0.05))
            self.b = float(a["bias"])
            self.w = {}
            for k, v in a["w"].items():
                c, bb = k.rsplit("|", 1)
                self.w[(c, int(bb))] = float(v)
        else:
            self.lam = float(a.get("lam", 0.5))
            self.pos = {c: {int(b): int(v) for b, v in a["pos"][c].items()} for c in self.names}
            self.neg = {c: {int(b): int(v) for b, v in a["neg"][c].items()} for c in self.names}
            self.n_pos = int(a["n_pos"])
            self.n_neg = int(a["n_neg"])
            self._rebin()

    def _rebin(self):
        self.nbins = {c: max(2, len(set(self.pos[c]) | set(self.neg[c]))) for c in self.names}

    @classmethod
    def load(cls, path: str = None) -> "BFPredicateDetector":
        p = path or (BF_ASSET if os.path.exists(BF_ASSET) else BF_ASSET_STAGING)
        with open(p, encoding="utf-8") as f:
            d = cls(json.load(f))
        if BUDGET:                                  # select a calibrated operating point by FP budget
            ent = d.thresholds_by_budget.get(BUDGET) or d.thresholds_by_budget.get(str(float(BUDGET)))
            if ent and ent.get("threshold"):
                d.threshold = float(ent["threshold"])
                d.budget = float(BUDGET)
        return d

    def _bin(self, name: str, x: float) -> int:
        spec = self.bin_spec.get(name)
        if spec is None:
            return int(round(float(x)))                 # binary cues are their own bins
        lo, hi, w = spec
        return int(math.floor((min(max(float(x), lo), hi) - lo) / w))

    def _units(self, cues):
        return [(c, self._bin(c, cues[c])) for c in self.names]

    def logodds(self, cues: Dict[str, float]) -> float:
        if self.kind == "rescorla_wagner":
            return self.b + sum(self.w.get(u, 0.0) for u in self._units(cues))
        z = math.log((self.n_pos + self.lam) / (self.n_neg + self.lam))
        for c, b in self._units(cues):
            B = self.nbins.get(c, 2)
            z += (math.log((self.pos[c].get(b, 0) + self.lam) / (self.n_pos + self.lam * B))
                  - math.log((self.neg[c].get(b, 0) + self.lam) / (self.n_neg + self.lam * B)))
        return z

    def score(self, cues: Dict[str, float]) -> float:
        return _sigmoid(self.logodds(cues))

    def observe(self, cues: Dict[str, float], label: int) -> None:
        """ONLINE accrual of one confirmed rescue outcome -- the plastic path (never a frozen weight vector)."""
        u = self._units(cues)
        if self.kind == "rescorla_wagner":
            d = self.eta * (float(label) - _sigmoid(self.b + sum(self.w.get(k, 0.0) for k in u)))
            self.b += d
            for k in u:
                self.w[k] = self.w.get(k, 0.0) + d
            return
        tab = self.pos if label else self.neg
        for c, b in u:
            tab[c][b] = tab[c].get(b, 0) + 1
        if label:
            self.n_pos += 1
        else:
            self.n_neg += 1
        self._rebin()

    def rescue_indices(self, toks: Sequence[str], tags: Sequence[str], lc,
                       threshold: float = None, post=None) -> List[Tuple[int, float]]:
        """(idx, score) for every gated candidate promoted to an event predicate. ADDITIVE: a token the category organ
        already called VERB/AUX is never touched, so the existing detections stay byte-identical."""
        th = self.threshold if threshold is None else float(threshold)
        post = lc.posterior(list(toks)) if post is None else post   # the reader hands its cached matrix (one pass per read)
        le = category_emission(lc, list(toks))
        cues = bf_cue_block(lc, list(toks), list(tags), post, le)
        span = hv = None
        if AUX_ARM:
            span = clause_spans(list(toks), list(tags))
            hv = {c: any(tags[j] == "VERB" for j in range(len(toks)) if span[j] == c) for c in set(span)}
        out = []
        for i in range(len(toks)):
            if tags[i] == "AUX":
                # the SOLE-AUX clause (see AUX_ARM): admitted only when no VERB competes for the predicate slot
                if not (AUX_ARM and not hv[span[i]]):
                    continue
            elif tags[i] == "VERB" or not has_verb_reading_glassbox(toks[i]):
                continue
            p = self.score(cues[i])
            if p >= th:
                out.append((i, p))
        return out
