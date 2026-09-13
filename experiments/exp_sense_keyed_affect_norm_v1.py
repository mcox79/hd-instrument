"""PROTOTYPE (research, experiments/-only): a SENSE-KEYED, PRECISION-WEIGHTED affect value for the verb.

THE PROBLEM (pri-100, opened from the pri-98 solver's located residual). The reader's word-level affect
value is ONE number per WORD FORM: Warriner et al. (2013) rate `treat` +0.46, `handle` +0.18, `hold` +0.26,
`carry` +0.17, `grab` +0.11, `pull` +0.15. So the harm/help read answers HELP on "the guard treated the
prisoner" -- 8 of the 13 remaining errors of the just-solved manner problem are exactly this. The pri-98
solver measured and REFUTED the two obvious repairs: withholding the norm for manner-host verbs (human gold
0.9333 -> 0.9014, live gold 24 -> 23) and withholding it for noun-dominant strings (`treat` is 0.000
noun-dominant in SemCor: the conflation is WITHIN the verb, not cross-POS).

THE BRAIN (the opening move).
  * THE VALUE IS ATTACHED TO THE ACTIVATED MEANING, NOT THE LETTER STRING. The anterior-temporal hub settles
    on a sense from context (Rodd, Gaskell & Marslen-Wilson 2004: the settled semantic vector; Kuperberg's
    graded meaning activation) and the OFC/vmPFC values THAT meaning (Barsalou situated conceptualisation;
    PINNED valuation target, BRAIN_MATH_REFERENCE section D).
        value(verb | context) = SUM_s P(s | context) * value(s)
  * AN UNSPECIFIED OUTCOME HAS NO VALUE. A sense that names no state change for the patient ("interact in a
    certain way", "be in charge of", "move while supporting") contributes ZERO, not "unknown". That is what
    makes treat / handle / hold / carry neutral WITHOUT an abstention rule -- the shape pri-98 refuted.
  * THE WORD-FORM NORM IS NOT DELETED, IT IS WEIGHTED BY ITS OWN PRECISION (Ernst & Banks 2002, w ~ 1/sigma^2
    -- the rung pri-98 named as the one it could NOT crack, "no cue carries a variance"). A rating of a
    letter string estimates the value of the active sense exactly to the degree that the string HAS one
    sense, so its precision is the SIMPSON CONCENTRATION of that string's own sense distribution:
        rho(w) = SUM_i p_i^2 over ALL of w's senses and parts of speech (SemCor resting levels).
    Measured: rho(treat) 0.247, rho(hold) 0.119, rho(carry) 0.216, rho(pull) 0.280 -- against rho(murder)
    0.763, rho(kill) 0.777, rho(protect) 0.936. THE FUSION:
        v_hat(verb | ctx) = [ k_w * rho(verb) * v_warriner + SUM_s P(s|ctx) v(s) ] / [ k_w * rho(verb) + 1 ]
    (the sense posterior carries total precision 1; unvalued senses enter as v(s) = 0.)

ARMS
  floor    hdlab/force_dynamics_valence at HEAD
  pri98    HEAD + the SOLVED-but-not-yet-landed manner diff, applied to a COPY inside this cell's own
           output directory (never to hdlab/) -- the consumer this arm must not regress
  sense    pri98 + the sense-keyed fusion REPLACING the word-norm rung of the endstate cascade
  twins    (1) sense VALUES permuted across the senses OF THE SAME WORD (the brief's named twin)
           (2) rho permuted across words (the precision channel)
           (3) the CONTEXT permuted across prose items (the sense-selection channel)

POPULATIONS  ADVERB_PROSE_GOLD (n=36, pri-98; its NEUTRAL cell holds the 8 target errors) | P_NEUTRAL_BROAD
  (n=36, 0 leaks) | Connotation Frames Effect(o) whole-arm + new decisions (independent human gold) | the
  36-item live modern gold | harm-frame / social-harm / non-prevent-help | the pri-98 named manner slice.

Run:  .venv/Scripts/python.exe experiments/exp_sense_keyed_affect_norm_v1.py
      .venv/Scripts/python.exe experiments/exp_sense_keyed_affect_norm_v1.py --self-test
Glass-box, deterministic, ASCII, no external LLM at inference.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
os.environ.setdefault("MKL_NUM_THREADS", "2")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "2")

import importlib.util
import json
import random
import shutil
import sys
from typing import Dict, List, Optional, Tuple

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments._seed_checkpoint import get_output_dir

ANCHOR = "sense_keyed_affect_norm_v1"
SEED = 20260913
N_BOOT = 2000
CF_NEG, CF_POS = -0.25, 0.25

SENSE_ASSET = os.path.join(REPO, "data", "frontend_assets", "sense_affect_norm_v1.json")
PRI98_DIFF = os.path.join(
    REPO, "notes", "problems",
    "manner_encoded_harm_needs_an_intensity_read_the_verb_tables_are_silent_on_brutally_and_roughly",
    "force_dynamics_valence_patch.diff")

# ---- OPERATING POINT (all SWEPT below; the phase diagram is free to move) --------------------------------
K_W = 2.0          # precision scale of the WORD-FORM norm relative to the sense posterior's total precision
TAU_E = 0.10       # |fused value| below which the rung hands on (the same shape as HEAD's WEAK_VALENCE 0.10)
LAM = 4.0          # sense-posterior temperature on the spreading activation (the organ's blend lambda,
                   # SWEPT: 0.5 is the organ's WSD default and is far too flat for a VALUE read -- at 0.5
                   # the context moves E(treat) by 0.007, at 4.0 by 0.14; plateau from 4.0 to 8.0)
CTX_MIN = 2        # content words the context read needs before it is consulted (HEAD's _CTX_STOP gate)
TAU_OPINION = 0.5  # posterior mass the sense read must have an OPINION about before it may DECIDE neutral
NEUTRAL_RULE = "neutral_mass"   # the opinion is counted on the NON-AFFECTING sense mass (the graded form of
                                # HEAD's own HDLAB_FDV_SENSE_ABSTAIN, which HEAD ships OFF as an argmax)
BASE = dict(mode="substitute", k_w=K_W, tau=TAU_E, tau_opinion=TAU_OPINION, lam=LAM,
            neutral_rule=NEUTRAL_RULE, channels=("R", "C", "M", "H", "S", "T"))


# ==========================================================================================================
# 0. THE pri-98 PATCHED CONSUMER -- applied to a COPY, inside this cell's own output directory
# ==========================================================================================================
def _apply_unified_diff(src_text: str, diff_text: str) -> str:
    """Minimal, exact unified-diff applier (context must match verbatim). Used ONLY to build the patched
    COPY of the consumer organ inside this cell's output dir -- hdlab/ is never written."""
    lines = src_text.split("\n")
    out: List[str] = []
    pos = 0
    dl = diff_text.split("\n")
    i = 0
    while i < len(dl):
        ln = dl[i]
        if not ln.startswith("@@"):
            i += 1
            continue
        head = ln.split("@@")[1].strip()          # -a,b +c,d
        old = head.split(" ")[0]
        start = int(old[1:].split(",")[0]) - 1
        out.extend(lines[pos:start])
        pos = start
        i += 1
        while i < len(dl) and not dl[i].startswith("@@"):
            h = dl[i]
            if h.startswith("diff ") or h.startswith("index ") or h.startswith("--- ") or h.startswith("+++ "):
                break
            if h.startswith("+"):
                out.append(h[1:])
            elif h.startswith("-"):
                if lines[pos] != h[1:]:
                    raise AssertionError("diff context mismatch at %d: %r != %r" % (pos, lines[pos], h[1:]))
                pos += 1
            elif h.startswith(" ") or h == "":
                ctx = h[1:] if h else ""
                if pos < len(lines) and lines[pos] == ctx:
                    out.append(lines[pos]); pos += 1
                elif h == "":
                    pass
                else:
                    raise AssertionError("diff context mismatch at %d" % pos)
            i += 1
    out.extend(lines[pos:])
    return "\n".join(out)


_FDV98 = None


def fdv98(out_dir=None):
    """hdlab/force_dynamics_valence.py + the pri-98 SOLVED-but-unlanded manner diff, imported from a copy
    under this cell's output directory. hdlab/ is untouched; the asset paths are repointed to the repo."""
    global _FDV98
    if _FDV98 is not None:
        return _FDV98
    out_dir = str(out_dir or get_output_dir(ANCHOR))
    pdir = os.path.join(out_dir, "patched_pri98")
    os.makedirs(pdir, exist_ok=True)
    src = open(os.path.join(REPO, "hdlab", "force_dynamics_valence.py"), encoding="utf-8").read()
    patched = _apply_unified_diff(src, open(PRI98_DIFF, encoding="utf-8").read())
    path = os.path.join(pdir, "fdv_pri98.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write(patched)
    spec = importlib.util.spec_from_file_location("fdv_pri98", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["fdv_pri98"] = mod
    spec.loader.exec_module(mod)
    # repoint the module-level asset paths (its _REPO is the copy's directory)
    mod.RESULT_STATE_ASSET = os.path.join(REPO, "data", "frontend_assets", "verbnet_result_state_v1.json")
    mod.MANNER_ASSET = os.path.join(REPO, "data", "frontend_assets", "manner_intensity_v1.json")
    mod._RS_TABLE = None
    mod._MANNER = None
    _FDV98 = mod
    return mod




AL_DIFF = os.path.join(REPO, "notes", "problems",
                       "the_verbs_affect_value_is_one_number_across_its_senses_treat_handle_hold_read_as_"
                       "pleasant_a_sense_keyed_norm", "affect_lexicon_patch.diff")


def patched_affect_lexicon(out_dir=None):
    """hdlab/affect_lexicon.py + THE PROPOSED DIFF, imported from a copy under this cell's output dir, so
    the shipped patch is proved to reproduce the cell's numbers rather than asserted to."""
    out_dir = str(out_dir or get_output_dir(ANCHOR))
    pdir = os.path.join(out_dir, "patched_pri100")
    os.makedirs(pdir, exist_ok=True)
    src = open(os.path.join(REPO, "hdlab", "affect_lexicon.py"), encoding="utf-8").read()
    patched = _apply_unified_diff(src, open(AL_DIFF, encoding="utf-8").read())
    path = os.path.join(pdir, "al_pri100.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write(patched)
    spec = importlib.util.spec_from_file_location("al_pri100", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["al_pri100"] = mod
    spec.loader.exec_module(mod)
    mod.WARRINER = os.path.join(REPO, "data", "frontend_assets", "Ratings_Warriner_et_al.csv")
    mod.SENSE_ASSET = SENSE_ASSET
    mod._SENSE_TABLE = None
    return mod


# ==========================================================================================================
# 1. THE SENSE-KEYED AFFECT NORM (the read; the asset is built by tools/build_sense_affect_norm_asset.py)
# ==========================================================================================================
_ASSET: Optional[Dict] = None


def asset() -> Dict:
    global _ASSET
    if _ASSET is None:
        try:
            with open(SENSE_ASSET, encoding="utf-8") as f:
                _ASSET = json.load(f)
        except Exception:
            _ASSET = {"senses": {}, "words": {}, "meta": {}}
    return _ASSET


CHANNELS = ("R", "C", "M", "H", "S", "T")   # channel precedence inside one sense (SWEPT: see push_grid)
# ON "M". The pri-98 solver measured that promoting the verb's lexicalised MANNER above the word norm is
# REFUTED by the human gold (whole-arm 0.9333 -> 0.9111), and this cell reproduces the reason: read as a
# WORD-level cue the manner channel is the least accurate of the five (dominant-channel CF agreement 0.778
# against 0.959 for the superordinate and 1.000 for the result state). But read INSIDE the sense value it
# is POSTERIOR-WEIGHTED, and that removes exactly the failure: a manner attached to a sense the context
# never activated cannot fire (`hold` was answered HARM from hold.v.29, resting level 0; `pull` from
# attract.v.01, 8 of 200+). Measured: dropping M costs the pri-98 manner slice 6/6 -> 4-5/6 and the named
# manner verbs 15 -> 13-14, and gains nothing anywhere. The channel is right; the KEYING was wrong.


def observe_sense(lemma: str, synset: str, n: int = 1) -> None:
    """THE ONLINE PATH (plastic, never frozen). Meeting `lemma` used in sense `synset` raises that sense's
    RESTING LEVEL by one presentation -- the same count the offline SemCor tally holds, in the same units.
    The expectation is one pure function of these counts, so a reader that reads more shifts its own prior."""
    rows = asset().setdefault("senses", {}).setdefault(lemma, [])
    for r in rows:
        if r[0] == synset:
            r[1] += n
            return
    rows.append([synset, n, 1, {}])


def sense_rows(verb: str) -> List:
    return asset().get("senses", {}).get(verb, [])


def row_value(row, channels=CHANNELS, values: Optional[Dict] = None, key: str = "") -> Optional[float]:
    """value(sense): the first channel that fires, in precedence order. A NON-AFFECTING sense predicts no
    outcome for a patient, so it contributes nothing (value 0), never 'unknown'."""
    if values is not None and key in values:
        return values[key]
    if not row[2]:
        return None
    ch = row[3] or {}
    for c in channels:
        if c in ch:
            return float(ch[c])
    return None


def sense_prior(rows, alpha: float = 0.5) -> List[float]:
    """The RESTING LEVEL over ALL of the verb's senses (SemCor presentation counts + smoothing); ACT-R /
    Anderson-Schooler base-level activation read as a distribution. The affecting gate is on the VALUE, not
    on this distribution -- gating the probability puts mass ~1 on a rare sense (`buy` -> bribe.v.01)."""
    c = [float(r[1]) + alpha for r in rows]
    t = sum(c)
    return [x / t for x in c]


_GSG = None


def gsg():
    global _GSG
    if _GSG is None:
        from hdlab.grounded_semantic_graph import GroundedSemanticGraph
        _GSG = GroundedSemanticGraph().build()
    return _GSG


_CTX_STOP = None


def context_words(tokens, gov_idx: int) -> List[str]:
    global _CTX_STOP
    if _CTX_STOP is None:
        _CTX_STOP = fdv98()._CTX_STOP
    return [str(t).lower() for i, t in enumerate(tokens) if i != gov_idx and str(t).isalpha()]


def enough_context(ctx) -> bool:
    global _CTX_STOP
    if _CTX_STOP is None:
        _CTX_STOP = fdv98()._CTX_STOP
    ws = [w if isinstance(w, str) else w[0] for w in ctx]
    return sum(1 for w in ws if len(w) > 2 and w not in _CTX_STOP) >= CTX_MIN


_PPR_CACHE: Dict = {}


def weighted_sense_ppr(wn, ctx, g, tgt, tn):
    """Spreading activation seeded by the context, with each context word's seed mass set by HOW STRONGLY
    THE READER BINDS IT TO THIS PREDICATE.

    hdlab.grounded_semantic_graph._sense_ppr seeds UNIFORMLY over every context word: the agent, the
    patient and a sentence adverbial all push equally hard on which sense of the verb is active. That is
    not how sense selection works. The verb's ARGUMENTS -- above all its direct object -- are the dominant
    cue to which sense is in play (Roland & Jurafsky 2002: verb sense is largely a function of its argument
    realisation; McRae & Matsuki 2009 / Elman generalized event knowledge: the arguments and the event
    schema activate each other, PINNED as graded, immediate and bidirectional). So the seed mass of a
    context word is (1 + W_ARG * P(head = the predicate | that word)), read from the reader's OWN governor
    marginals -- the same graded hand-off pri-98 showed is worth +0.194 on the manner read. `ctx` may be a
    plain word list (all weights 1) or a list of (word, weight) pairs.
    Everything else is byte-identical to the organ's own read: the same graph, the same damping, the same
    iteration count, the same seed construction, only the personalisation vector is non-uniform."""
    import numpy as np
    pairs = [(w, 1.0) if isinstance(w, str) else (w[0], float(w[1])) for w in ctx]
    ck = (tuple(pairs), tuple(tn))
    if ck in _PPR_CACHE:
        return _PPR_CACHE[ck]
    tgt_set = set(tn)
    acc = {}
    for w, wt in pairs:
        for gsn in wn.synsets(w):
            j = g.syn2idx.get(gsn.name())
            if j is not None and gsn.name() not in tgt_set:
                acc[j] = acc.get(j, 0.0) + wt
    if not acc:
        return None
    n = len(g.syn2idx)
    pvec = np.zeros(n, np.float32)
    tot = sum(acc.values())
    for j, wt in acc.items():
        pvec[j] = wt / tot
    from hdlab.grounded_semantic_graph import DAMPING, PPR_ITERS
    r = pvec.copy()
    for _ in range(PPR_ITERS):
        r = (1.0 - DAMPING) * pvec + DAMPING * (g.T @ r)
    res = np.array([float(r[g.syn2idx[t.name()]]) if t.name() in g.syn2idx else 0.0 for t in tgt])
    _PPR_CACHE[ck] = res
    return res


W_ARG = 0.0     # extra seed mass for a word the reader BINDS to the predicate (0 = the organ's own uniform read)


def bound_context(tokens, gov_idx: int, w_arg: float = None):
    """(word, seed weight) for every context word, the weight read from the reader's own governor
    MARGINALS: P(head of this word = the predicate). Falls back to the flat context on any parse failure."""
    w_arg = W_ARG if w_arg is None else w_arg
    ctx = context_words(tokens, gov_idx)
    if not w_arg:
        return ctx
    try:
        fe = frontend()
        toks = list(tokens)
        pos, post = fe["T"].tag_with_posterior(toks)
        out = fe["P"].parse(toks, pos, post)
        marg = getattr(out, "marginals", None) or {}
        wts = []
        for i, t in enumerate(toks):
            if i == gov_idx or not str(t).isalpha():
                continue
            m = float(marg.get(i + 1, {}).get(gov_idx + 1, 0.0)) if marg else \
                (1.0 if out.heads.get(i + 1, -1) == gov_idx + 1 else 0.0)
            wts.append((str(t).lower(), 1.0 + w_arg * m))
        return wts or ctx
    except Exception:
        return ctx


def sense_posterior(verb: str, rows, ctx: Optional[List[str]] = None, lam: float = LAM) -> List[float]:
    """P(s | context) over ALL of the verb's senses = the organ's own log-linear blend of the frequency
    RESTING LEVEL with the settled SPREADING ACTIVATION -- read as a DISTRIBUTION, not an argmax:
        P(s|ctx) ~ P_freq(s) * PPR(s)^lam        (hdlab.grounded_semantic_graph, graded)
    Falls back to the resting level alone when the context is too thin for the activation to settle."""
    p = sense_prior(rows)
    if not ctx or not enough_context(ctx) or len(rows) == 1:
        return p
    try:
        import numpy as np
        from nltk.corpus import wordnet as wn
        g = gsg()
        tgt = [wn.synset(r[0]) for r in rows]
        tn = [r[0] for r in rows]
        ppr = weighted_sense_ppr(wn, ctx, g, tgt, tn)
        if ppr is None:
            return p
        pp = np.asarray(ppr, float) + 1e-6
        pp = pp / pp.sum()
        lg = np.log(np.asarray(p, float)) + lam * np.log(pp)
        lg = lg - lg.max()
        q = np.exp(lg)
        return list(q / q.sum())
    except Exception:
        return p


def sense_expectation(verb: str, ctx: Optional[List[str]] = None, values: Optional[Dict] = None,
                      lam: float = LAM, channels=CHANNELS):
    """(E, coverage, posterior, opinion). E = SUM_s P(s|ctx) v(s).

    THREE KINDS OF SENSE, and the distinction is load-bearing:
      VALUED       an affecting-animate sense whose outcome the foundation names -> contributes p_s * v(s)
      NEUTRAL      a sense that is NOT an affecting-animate event ("be in charge of", "move while
                   supporting", "regard as") -> it predicts NO outcome for a patient, so its value is
                   genuinely 0. This is EVIDENCE OF NEUTRALITY, and it is why treat/hold/carry can come out
                   neutral without an abstention RULE (the shape pri-98 refuted).
      UNKNOWN      an affecting-animate sense our channels cannot value -> IGNORANCE, not neutrality. It
                   must not be counted as evidence either way.
    `opinion` = valued + neutral mass = the posterior mass on which the sense read actually has an opinion,
    i.e. the PRECISION of this cue. None when the lemma is not in the asset at all."""
    rows = sense_rows(verb)
    if not rows:
        return None
    p = sense_posterior(verb, rows, ctx, lam)
    e = cov = neutral = 0.0
    for pi, r in zip(p, rows):
        v = row_value(r, channels, values, verb + "|" + r[0])
        if v is None:
            if not r[2]:
                neutral += pi                     # a non-affecting sense: a real zero
            continue                              # an affecting-but-unvalued sense: ignorance
        e += pi * float(v)
        cov += pi
    return e, cov, p, cov + neutral, neutral


def fused_value(verb: str, ctx: Optional[List[str]] = None, k_w: float = K_W,
                values: Optional[Dict] = None, rho_over: Optional[Dict] = None,
                lam: float = LAM, mode: str = "substitute", channels=CHANNELS,
                tau_cov: float = 0.0) -> Optional[float]:
    """FUSE the word-form norm with the sense-keyed expectation. The measured shapes:
      substitute  v_hat = (k*rho*v_w + E) / (k*rho + 1)   -- precision-weighted (Ernst & Banks), rho = the
                  unambiguity of the letter string the raters rated
      shift       v_hat = v_w + (E_ctx - E_prior)         -- the word norm carries the word-level average,
                  the posterior carries only how far THIS context moves it (a word-level identity)
      gated       v_hat = E if coverage >= tau_cov else v_w
      sense_only  v_hat = E ; word_only  v_hat = v_w      -- the two isolating ablations
    """
    se = sense_expectation(verb, ctx, values, lam, channels)
    if se is None:
        return None
    e, cov, _p, _op, _nm = se
    w = asset().get("words", {}).get(verb, {})
    rho = (rho_over or {}).get(verb, w.get("rho", 1.0))
    vw = w.get("v")
    if mode == "sense_only" or vw is None:
        return e
    if mode == "word_only":
        return float(vw)
    if mode == "shift":
        se0 = sense_expectation(verb, None, values, lam, channels)
        return float(vw) + (e - (se0[0] if se0 else 0.0))
    if mode == "gated":
        return e if cov >= tau_cov else float(vw)
    pw = k_w * float(rho)
    return (pw * float(vw) + e) / (pw + 1.0)


def sense_endstate_sign(verb: str, ctx=None, tau: float = TAU_E, tau_opinion: float = 0.0,
                        lam: float = LAM, channels=CHANNELS, values=None,
                        neutral_rule: str = "opinion", **kw):
    """(sign, verdict). verdict is one of:
         'sign'    the fused value clears tau -> HARM/HELP
         'neutral' the sense read HAS an opinion (opinion mass >= tau_opinion) and it is that the active
                   meaning leaves the patient's condition unchanged -> DECIDE neutral and STOP. Handing on
                   to the verb-level residual rungs here is how the conflation re-enters one rung later:
                   measured, `pull` and `hold` fall through and the verb-level manner arm answers HARM from
                   attract.v.01 / hold.v.29, senses the context never selected.
         'pass'    no opinion -> hand on to the superordinate / manner / genus rungs, unchanged
         'na'      the lemma is not in the asset -> the HEAD word-norm rung stands, unchanged"""
    se = sense_expectation(verb, ctx, values, lam, channels)
    if se is None:
        return None, "na"
    v = fused_value(verb, ctx, lam=lam, channels=channels, values=values, **kw)
    if v is not None and abs(v) >= tau:
        return (1 if v > 0 else -1), "sign"
    if tau_opinion > 0.0:
        if neutral_rule == "opinion" and se[3] >= tau_opinion:
            return 0, "neutral"
        if neutral_rule == "neutral_mass" and se[4] >= tau_opinion:
            return 0, "neutral"
        if neutral_rule == "argmax":
            # THE POINT-ESTIMATE VERSION OF THE SAME RULE -- this is hdlab HEAD's own HDLAB_FDV_SENSE_ABSTAIN,
            # which HEAD ships OFF because it "cost 6 verdicts: on short sentences the spreading activation
            # settles on a wrong sense". Measured here beside the graded rule: the same rung, point estimate
            # vs posterior.
            rows = sense_rows(verb)
            if rows:
                pp = sense_posterior(verb, rows, ctx, lam)
                j = max(range(len(rows)), key=lambda i: pp[i])
                if not rows[j][2]:
                    return 0, "neutral"
    return None, "pass"


# ==========================================================================================================
# 2. THE ARMS -- the endstate cascade with the word-norm rung replaced by the sense-keyed fusion
# ==========================================================================================================
def make_endstate(F, ctx_get=None, tau: float = TAU_E, **kw):
    """The proposed cascade for module F (the pri-98-patched consumer):
         1 RESULT STATE (unchanged)                2 SENSE-KEYED FUSION  (replaces the word-form norm)
         3 SUPERORDINATE (unchanged)               4 MANNER   5 GENUS    (pri-98, unchanged)
    Rung 2 falls back to the HEAD word norm for a verb with no affecting-animate sense."""
    def endstate(verb, afx=None, states=None):
        v = F.lemmatize_verb(verb)
        afx_l = F._afx() if afx is None else afx
        rs = F.result_state_value(v, None if afx_l is F._AFX else afx_l, states)
        if rs is not None and abs(rs) >= F.STATE_MIN:
            return 1 if rs > 0 else -1
        ctx = ctx_get() if ctx_get is not None else None
        sgn, verdict = sense_endstate_sign(v, ctx, tau=tau, **kw)
        if verdict == "sign":
            return sgn
        if verdict == "neutral":
            return 0                                     # a DECIDED neutral: 0 stops the cascade
        if verdict == "na":                              # not in the asset -> HEAD's word norm, unchanged
            val = afx_l.valence(v)
            if val is not None and abs(val) >= F.WEAK_VALENCE:
                return 1 if val > 0 else -1
        hs = F.hyper_state_sign(v, None if afx_l is F._AFX else afx_l)
        if hs is not None:
            return hs
        if getattr(F, "MANNER_READ", False):
            ms = F.manner_state_sign(v, None if afx_l is F._AFX else afx_l)
            if ms is not None:
                return ms
            return F.genus_state_sign(v, None if afx_l is F._AFX else afx_l)
        return None
    return endstate


def make_isaffecting(F, tau: float = TAU_E, **kw):
    """A verb whose SENSES carry an affective outcome IS an affecting event -- the same categorisation that
    signs it admits it, guarded exactly as the landed admissions are."""
    base = F.is_affecting

    def isaff(verb, lexicon=None, afx=None, tau_a=None):
        if base(verb, lexicon, afx, tau_a):
            return True
        v = F.lemmatize_verb(verb)
        if F._is_subject_experiencer(v):
            return False
        if F.verb_first_supersense(v) in F._NON_AFFECTING_DOMINANT:
            return False
        sgn, verdict = sense_endstate_sign(v, None, tau=tau, **kw)
        return verdict == "sign"
    return isaff


def arm(F, endstate_fn=None, isaff_fn=None):
    """Run F.harm_help_arithmetic with the given cascade swapped in (restored afterwards)."""
    def run(verb, animacy="animate", **kw):
        F._EV_CACHE.clear()
        oe, oa = F.endstate_valence_sign, F.is_affecting
        if endstate_fn is not None:
            F.endstate_valence_sign = endstate_fn
        if isaff_fn is not None:
            F.is_affecting = isaff_fn
        try:
            return F.harm_help_arithmetic(verb, animacy, **kw)
        finally:
            F.endstate_valence_sign, F.is_affecting = oe, oa
            F._EV_CACHE.clear()
    return run


# ==========================================================================================================
# 3. THE PROSE PATH (the pri-98 RUNG-5 manner fusion, with the sense-keyed endstate underneath)
# ==========================================================================================================
_FE: Dict = {}


def frontend():
    if not _FE:
        from hdlab import frontend as FE
        _FE["T"] = FE.Tagger(); _FE["P"] = FE.Parser()
    return _FE


def prose_manner_value(F, tokens, gov_idx: int, graded: bool = True) -> Optional[float]:
    """pri-98's manner-in-prose read, verbatim in behaviour: the posterior-mass-weighted mean valence of the
    de-adjectival adverbs the reader's own governor binds to this predicate."""
    fe = frontend()
    toks = list(tokens)
    pos, post = fe["T"].tag_with_posterior(toks)
    out = fe["P"].parse(toks, pos, post)
    afx = F._afx()
    num = den = 0.0
    for i, t in enumerate(toks):
        if not str(t).isalpha():
            continue
        if pos[i] not in ("ADV", "ADJ") and not str(t).lower().endswith("ly"):
            continue
        st = F._adverb_stem(str(t))
        if st is None:
            continue
        x = afx.valence(st)
        if x is None or abs(x) < F.TAU_MANNER_VAL:
            continue
        inten = F.manner_intensity(st, afx)
        if inten is None or inten < F.TAU_INTENSITY:
            continue
        if graded and out.marginals:
            mass = float(out.marginals.get(i + 1, {}).get(gov_idx + 1, 0.0))
        else:
            mass = 1.0 if out.heads.get(i + 1, -1) == gov_idx + 1 else 0.0
        if mass < F.TAU_HEAD_MASS:
            continue
        num += float(x) * mass
        den += mass
    return (num / den) if den else None


def harm_help_prose(F, base_arm, verb, tokens, gov_idx, animacy="animate", graded=True):
    """The pri-98 RUNG-5 precision-weighted fusion, unchanged: result state > this event's MANNER > the
    verb-level value. `base_arm` supplies the verb-level value (floor / pri98 / sense-keyed)."""
    v = F.lemmatize_verb(verb)
    base = base_arm(v, animacy)
    if animacy == "inanimate":
        return base
    mval = prose_manner_value(F, tokens, gov_idx, graded)
    if mval is None:
        return base
    rs = F.result_state_value(v)
    if rs is not None and abs(rs) >= F.STATE_MIN:
        return base
    if not F.is_affecting(v):
        ss = F.verb_first_supersense(v)
        if F._is_subject_experiencer(v) or ss in ("perception", "cognition", "stative", "motion"):
            return base
        if abs(mval) < F.TAU_STRONG:
            return base
    return "HARM" if mval < 0 else "HELP"


# ==========================================================================================================
# 4. metrics helpers
# ==========================================================================================================
def boot_ci(corr, n_boot=N_BOOT, seed=SEED):
    if not corr:
        return 0.0, 0.0
    rng = random.Random(seed)
    n = len(corr); ms = []
    for _ in range(n_boot):
        ms.append(sum(corr[rng.randrange(n)] for _ in range(n)) / n)
    ms.sort()
    return sum(corr) / n, (ms[int(0.975 * n_boot)] - ms[int(0.025 * n_boot)]) / 2.0


def paired_boot(a, b, n_boot=N_BOOT, seed=SEED):
    rng = random.Random(seed + 1)
    n = len(a); d = [a[i] - b[i] for i in range(n)]
    ms = []
    for _ in range(n_boot):
        ms.append(sum(d[rng.randrange(n)] for _ in range(n)) / n)
    ms.sort()
    return (sum(d) / n, ms[int(0.025 * n_boot)], ms[int(0.975 * n_boot)])


def prose_correct(pred, gold) -> int:
    if gold == "NEUTRAL":
        return 1 if pred not in ("HARM", "HELP") else 0
    return 1 if pred == gold else 0


# ==========================================================================================================
# 5. TWINS
# ==========================================================================================================
def twin_values_within_word(seed=SEED + 3) -> Dict[str, Optional[float]]:
    """THE BRIEF'S NAMED TWIN: the sense VALUES permuted across the senses OF THE SAME WORD. The multiset of
    values a word's senses carry is preserved exactly; only WHICH SENSE carries WHICH VALUE is destroyed."""
    rng = random.Random(seed)
    out: Dict[str, Optional[float]] = {}
    for lemma, rows in sorted(asset().get("senses", {}).items()):
        vals = [row_value(r) for r in rows]
        idx = list(range(len(rows)))
        rng.shuffle(idx)
        for r, j in zip(rows, idx):
            out[lemma + "|" + r[0]] = vals[j]
    return out


def twin_values_global(seed=SEED + 5) -> Dict[str, Optional[float]]:
    """Values permuted across ALL senses (the stronger, lower-power-loss twin)."""
    rng = random.Random(seed)
    keys, vals = [], []
    for lemma, rows in sorted(asset().get("senses", {}).items()):
        for r in rows:
            keys.append(lemma + "|" + r[0]); vals.append(row_value(r))
    rng.shuffle(vals)
    return dict(zip(keys, vals))


def twin_rho(seed=SEED + 7) -> Dict[str, float]:
    """rho permuted across words: the PRECISION channel scrambled, the values intact."""
    rng = random.Random(seed)
    ws = asset().get("words", {})
    keys = sorted(ws)
    vals = [ws[k].get("rho", 1.0) for k in keys]
    rng.shuffle(vals)
    return dict(zip(keys, vals))


# ==========================================================================================================
# 6. run
# ==========================================================================================================
def run() -> Dict:
    out_dir = get_output_dir(ANCHOR)
    os.makedirs(out_dir, exist_ok=True)
    F = fdv98(out_dir)

    import hdlab.force_dynamics_valence as HEAD
    import experiments.exp_fd_harm_help_arithmetic_v1 as A
    import experiments.exp_manner_intensity_harm_v1 as M98
    from experiments.fetch_connotation_frames_v1 import load_effect_o

    gold = load_effect_o()

    def glabel(v):
        e = gold.get(HEAD.lemmatize_verb(v))
        if e is None:
            return None
        return "HARM" if e < CF_NEG else ("HELP" if e > CF_POS else "NEUTRAL")

    res: Dict = {"_meta": {"anchor": ANCHOR, "seed": SEED, "out_dir": str(out_dir),
                           "k_w": K_W, "tau_e": TAU_E, "lam": LAM,
                           "asset_meta": asset().get("meta", {}),
                           "cf_gold_verbs": len(gold),
                           "n_sense_lemmas": len(asset().get("senses", {}))}}

    # ---- the three verb-level arms -----------------------------------------------------------------
    floor = arm(HEAD)                                     # hdlab at HEAD
    pri98 = arm(F)                                        # HEAD + the unlanded manner diff
    es_sense = make_endstate(F, **BASE)
    ia_sense = make_isaffecting(F, **BASE)
    sense = arm(F, es_sense, ia_sense)

    res["_meta"]["pri98_patch_applied"] = bool(getattr(F, "MANNER_READ", False))

    # ---- 1. THE TARGET: the adverb-in-prose gold, and its NEUTRAL cell ------------------------------
    res["adverb_prose_gold"] = prose_report(F, floor, pri98, es_sense, ia_sense, M98)

    # ---- 2. NEUTRAL PRECISION (0 new leaks required) ------------------------------------------------
    def leaks(fn):
        return [(v, fn(v, "animate")) for v in A.P_NEUTRAL_BROAD if fn(v, "animate") in ("HARM", "HELP")]
    res["neutral_precision"] = {"n": len(A.P_NEUTRAL_BROAD), "floor": leaks(floor),
                                "pri98": leaks(pri98), "sense": leaks(sense)}

    # ---- 3. the brief's no-regress populations -------------------------------------------------------
    def cnt(pop, target, fn):
        return sum(fn(v, "animate") == target for v in pop)
    res["populations"] = {
        "harm_frame_HARM": [cnt(A.P_HARM_FRAME, "HARM", f) for f in (floor, pri98, sense)] + [len(A.P_HARM_FRAME)],
        "social_harm_HARM": [cnt(A.P_SOCIAL_HARM, "HARM", f) for f in (floor, pri98, sense)] + [len(A.P_SOCIAL_HARM)],
        "nonprevent_help_HELP": [cnt(A.P_NONPREVENT_HELP, "HELP", f) for f in (floor, pri98, sense)] + [len(A.P_NONPREVENT_HELP)],
        "named_manner_HARM_of_15": [cnt(M98.NAMED_HARM, "HARM", f) for f in (floor, pri98, sense)] + [len(M98.NAMED_HARM)],
        "manner_slice_HARM_of_6": [cnt(M98.MANNER_SLICE, "HARM", f) for f in (floor, pri98, sense)] + [len(M98.MANNER_SLICE)],
    }

    # ---- 4. the INDEPENDENT HUMAN GOLD: whole-arm agreement + every new/changed decision --------------
    lem = candidate_verbs(F, ia_sense)
    res["cf"] = cf_report(lem, gold, glabel, {"floor": floor, "pri98": pri98, "sense": sense})

    # ---- 4b. THE DECISIVE CUE DIAGNOSTIC + every fusion SHAPE ---------------------------------------
    res["cue_accuracy"] = cue_report(lem, gold, glabel)
    res["fusion_modes"] = fusion_modes_report(F, lem, gold, glabel, A, M98)
    res["levers"] = lever_report(F, lem, gold, glabel, A, M98, BASE)
    res["push_grid"] = push_grid(F, lem, glabel, A, M98)

    # ---- 5. TWINS -----------------------------------------------------------------------------------
    tw_word = twin_values_within_word()
    tw_glob = twin_values_global()
    tw_rho = twin_rho()
    arms_twin = {
        "twin_values_within_word": arm(F, make_endstate(F, values=tw_word, **BASE), make_isaffecting(F, values=tw_word, **BASE)),
        "twin_values_global": arm(F, make_endstate(F, values=tw_glob, **BASE), make_isaffecting(F, values=tw_glob, **BASE)),
        "twin_rho": arm(F, make_endstate(F, rho_over=tw_rho, **BASE), make_isaffecting(F, rho_over=tw_rho, **BASE)),
    }
    res["twins"] = cf_report(lem, gold, glabel, arms_twin)
    res["twins"]["neutral_leaks"] = {k: len(leaks(fn)) for k, fn in arms_twin.items()}
    res["twins"]["prose"] = {}
    real_corr = [prose_correct(r["sense_ctx"], r["gold"]) for r in res["adverb_prose_gold"]["rows"]]
    for k, _fn in arms_twin.items():
        vals = tw_word if k == "twin_values_within_word" else (tw_glob if k == "twin_values_global" else None)
        rho_o = tw_rho if k == "twin_rho" else None
        iak = make_isaffecting(F, values=vals, rho_over=rho_o, **BASE)
        holder = {"ctx": None}
        ack = arm(F, make_endstate(F, ctx_get=lambda: holder["ctx"], values=vals, rho_over=rho_o, **BASE), iak)
        corr, tw_, tn_ = [], 0, 0
        for agent, verb, patient, adverb, label in M98.ADVERB_PROSE_GOLD:
            toks = M98.prose_sentence(agent, verb, patient, adverb)
            holder["ctx"] = bound_context(toks, 2)
            pred = harm_help_prose(F, ack, verb, toks, 2)
            holder["ctx"] = None
            corr.append(prose_correct(pred, label))
            if label == "NEUTRAL" and floor(F.lemmatize_verb(verb), "animate") in ("HARM", "HELP"):
                tn_ += 1
                tw_ += int(pred in ("HARM", "HELP"))
        m, h = boot_ci(corr)
        d, lo, hi = paired_boot(real_corr, corr)
        res["twins"]["prose"][k] = {"acc": [round(m, 4), round(h, 4)],
                                    "target_errors_remaining": [tw_, tn_],
                                    "real_minus_twin": [round(d, 4), round(lo, 4), round(hi, 4)]}

    res["twins"]["prose_context_scrambled"] = context_twin_report(
        F, lambda h: make_endstate(F, ctx_get=lambda: h["ctx"], **BASE), ia_sense, M98)
    res["cf_paired"] = cf_paired(lem, glabel, {"pri98": pri98, "sense": sense, "floor": floor})
    # the twins, PAIRED against the real arm, and again restricted to the verbs the twin actually
    # perturbs (a twin that is the identity on a monosemous verb cannot lose on it -- including those
    # items only dilutes the comparison)
    perturbed = set()
    for lemma, rows in asset().get("senses", {}).items():
        for r in rows:
            k = lemma + "|" + r[0]
            if tw_word.get(k) != row_value(r, BASE["channels"]):
                perturbed.add(lemma)
                break
    res["twins"]["cf_paired_all"] = cf_paired(lem, glabel, dict({"sense": sense}, **arms_twin))
    res["twins"]["cf_paired_perturbed_only"] = cf_paired(
        lem, glabel, dict({"sense": sense}, **arms_twin), restrict=perturbed)
    res["twins"]["n_perturbed_lemmas"] = len(perturbed)
    res["residual_2x2"] = residual_2x2(F, M98)
    res["semcor_probe"] = semcor_probe(F)

    # ---- 6. the 36-item LIVE MODERN GOLD (no-regress) ------------------------------------------------
    res["live_modern_gold"] = live_gold_report(floor, pri98, sense)

    # ---- 7. OPERATING-POINT SWEEP (the phase diagram) ------------------------------------------------
    res["sweep"] = sweep_report(F, lem, gold, glabel, A, M98, BASE)

    # ---- 8. the ONLINE PATH ---------------------------------------------------------------------------
    res["online"] = online_report(F, M98)

    with open(os.path.join(out_dir, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, default=str)
    return res




def evaluate(F, lem, glabel, A, M98, prose: bool = True, **kw) -> Dict:
    """Every population for ONE configuration of the sense rung. Used by every grid row so no operating
    point is ever chosen on the target population alone."""
    es = make_endstate(F, **kw)
    ia = make_isaffecting(F, **kw)
    a = arm(F, es, ia)
    p = t = 0
    for v in lem:
        pr = a(v, "animate")
        g = glabel(v)
        if g in ("HARM", "HELP") and pr in ("HARM", "HELP"):
            t += 1
            p += (g == pr)
    lk = sum(1 for v in A.P_NEUTRAL_BROAD if a(v, "animate") in ("HARM", "HELP"))
    try:
        import experiments.exp_fd_harm_help_live_modern_v1 as LIVE
        lg = sum(1 for g in LIVE.GOLD if g[3] in ("HARM", "HELP") and a(g[1], "animate") == g[3])
    except Exception:
        lg = -1
    out = {"cf_whole_arm": [p, t, round(p / max(1, t), 4)], "leaks": lk, "live_gold_24": lg,
           "named_manner_15": sum(1 for v in M98.NAMED_HARM if a(v, "animate") == "HARM"),
           "slice6": sum(1 for v in M98.MANNER_SLICE if a(v, "animate") == "HARM"),
           "social_harm_16": sum(1 for v in A.P_SOCIAL_HARM if a(v, "animate") == "HARM"),
           "nonprevent_help_16": sum(1 for v in A.P_NONPREVENT_HELP if a(v, "animate") == "HELP")}
    if not prose:
        return out
    holder = {"ctx": None}
    esc = make_endstate(F, ctx_get=lambda: holder["ctx"], **kw)
    ac = arm(F, esc, ia)
    corr, tw, tn = [], 0, 0
    floor_arm = arm(F)
    for agent, verb, patient, adverb, label in M98.ADVERB_PROSE_GOLD:
        toks = M98.prose_sentence(agent, verb, patient, adverb)
        holder["ctx"] = bound_context(toks, 2)
        pred = harm_help_prose(F, ac, verb, toks, 2)
        holder["ctx"] = None
        corr.append(prose_correct(pred, label))
        if label == "NEUTRAL" and floor_arm(F.lemmatize_verb(verb), "animate") in ("HARM", "HELP"):
            tn += 1
            tw += int(pred in ("HARM", "HELP"))
    m, h = boot_ci(corr)
    out["prose_acc"] = [round(m, 4), round(h, 4)]
    out["prose_correct"] = corr
    out["target_errors_remaining"] = [tw, tn]
    return out



def push_grid(F, lem, glabel, A, M98) -> Dict:
    """THE FOCUSED GRID. Three things move together and must be chosen together on EVERY population:
      lam         how sharply the settled spreading activation is allowed to reshape the resting level
      channels    whether the verb's lexicalised MANNER is read INSIDE the sense value (posterior-weighted,
                  so a manner attached to a sense the context never activated cannot fire -- measured: at
                  the verb level `hold` and `pull` answer HARM from hold.v.29 and attract.v.01, senses with
                  ~0 posterior mass)
      tau_opinion / neutral_rule  how much opinion the sense read needs before it may DECIDE neutral, and
                  whether that decision is taken on the posterior MASS or on the ARGMAX (HEAD's own
                  SENSE_ABSTAIN, shipped OFF because the argmax settles on the wrong sense)."""
    out = {}
    for ch in (("R", "C", "H", "S", "T"), ("R", "C", "M", "H", "S", "T")):
        for lam in (2.0, 4.0):
            for rule, op in (("opinion", 0.3), ("opinion", 0.5), ("opinion", 0.7), ("opinion", 0.9),
                             ("neutral_mass", 0.3), ("neutral_mass", 0.5), ("argmax", 1.0)):
                for k_w in (1.0, 2.0):
                    name = "ch%s_lam%.0f_%s%.1f_kw%.0f" % ("".join(ch), lam, rule, op, k_w)
                    out[name] = evaluate(F, lem, glabel, A, M98, mode="substitute", k_w=k_w,
                                         tau=TAU_E, lam=lam, channels=ch, tau_opinion=op,
                                         neutral_rule=rule)
    return out



def context_twin_report(F, es_ctx_factory, ia, M98, seed=SEED + 13) -> Dict:
    """THE SELECTION-CHANNEL TWIN: each item keeps its own verb but is given ANOTHER item's context. The
    sense values, the word norms, rho and every threshold are untouched -- only the evidence about WHICH
    sense is active is destroyed. If the read is really doing sense selection this must lose."""
    rows = list(M98.ADVERB_PROSE_GOLD)
    perm = list(range(len(rows)))
    rng = random.Random(seed)
    rng.shuffle(perm)
    holder = {"ctx": None}
    ac = arm(F, es_ctx_factory(holder), ia)
    corr = []
    for i, (agent, verb, patient, adverb, label) in enumerate(rows):
        toks = M98.prose_sentence(agent, verb, patient, adverb)
        j = perm[i]
        other = M98.prose_sentence(*rows[j][:4])
        holder["ctx"] = bound_context(other, 2)          # another scene's context, this scene's verb
        pred = harm_help_prose(F, ac, verb, toks, 2)
        holder["ctx"] = None
        corr.append(prose_correct(pred, label))
    m, h = boot_ci(corr)
    return {"acc": [round(m, 4), round(h, 4)], "correct": corr}


def cf_paired(lem, glabel, arms: Dict, restrict=None) -> Dict:
    """The human-gold comparison done PAIRED, on the items BOTH arms decide -- the honest form. A whole-arm
    ratio over different denominators can move because coverage moved; this cannot."""
    names = list(arms)
    preds = {n: {v: arms[n](v, "animate") for v in lem} for n in names}
    pool = lem if restrict is None else [v for v in lem if v in restrict]
    shared = [v for v in pool if glabel(v) in ("HARM", "HELP")
              and all(preds[n][v] in ("HARM", "HELP") for n in names)]
    out = {"n_shared": len(shared)}
    corr = {n: [int(preds[n][v] == glabel(v)) for v in shared] for n in names}
    for n in names:
        m, h = boot_ci(corr[n])
        out[n] = {"acc": round(m, 4), "ci_half": round(h, 4),
                  "n_decided_overall": sum(1 for v in lem if preds[n][v] in ("HARM", "HELP"))}
    base = names[0]
    for n in names[1:]:
        d, lo, hi = paired_boot(corr[n], corr[base])
        out["delta_%s_minus_%s" % (n, base)] = [round(d, 4), round(lo, 4), round(hi, 4)]
    return out



def residual_2x2(F, M98) -> Dict:
    """THE BRIEF'S ITEM 4, with counts: for every NEUTRAL-cell item the floor answers HELP on, is the
    remaining error a SELECTION failure (the posterior puts mass on a sense the context does not license)
    or a VALUATION failure (the right sense carries the wrong value)? Reported per item with the posterior
    itself, so the diagnosis is a number and not a story."""
    import hdlab.force_dynamics_valence as HEAD
    floor = arm(HEAD)
    ia = make_isaffecting(F, **BASE)
    holder = {"ctx": None}
    ac = arm(F, make_endstate(F, ctx_get=lambda: holder["ctx"], **BASE), ia)
    out = []
    for agent, verb, patient, adverb, label in M98.ADVERB_PROSE_GOLD:
        if label != "NEUTRAL":
            continue
        v = HEAD.lemmatize_verb(verb)
        if floor(v, "animate") not in ("HARM", "HELP"):
            continue
        toks = M98.prose_sentence(agent, verb, patient, adverb)
        holder["ctx"] = bound_context(toks, 2)
        pred = harm_help_prose(F, ac, verb, toks, 2)
        rows = sense_rows(v)
        post = sense_posterior(v, rows, holder["ctx"], BASE["lam"]) if rows else []
        holder["ctx"] = None
        top = sorted(zip(post, rows), key=lambda x: -x[0])[:4]
        # the mass that is BOTH affecting-animate AND carries a non-zero value = the mass driving the sign
        driving = [(r[0], round(pi, 3), row_value(r, BASE["channels"])) for pi, r in top]
        out.append({"sent": " ".join(toks), "verb": v, "pred": pred,
                    "fixed": pred not in ("HARM", "HELP"),
                    "top_senses": driving,
                    "diagnosis": ("fixed" if pred not in ("HARM", "HELP") else
                                  ("selection: the driving sense is not the one this context licenses"
                                   if any(x[2] is not None and x[1] > 0.05 for x in driving)
                                   else "downstream: the value came from a rung below this one"))})
    return {"n": len(out), "n_fixed": sum(1 for x in out if x["fixed"]), "items": out}



# ==========================================================================================================
# THE POWERED INSTRUMENT FOR SENSE KEYING (added after the first verdict check: the brief's named twin does
# NOT lose on the Connotation-Frames gold, and it CANNOT -- CF rates a VERB OUT OF CONTEXT, so it is a
# word-level answer key and is blind to which sense is active, by construction. Move 9 of
# HOW_WALLS_WERE_BROKEN: change the gold to what the ability actually is.)
#
# SemCor (Miller et al. 1993) is running prose in which a human annotator marked WHICH SENSE each content
# word carries. It is used here strictly as a MEASURING instrument -- exactly the standing UD-EWT has for
# the parser -- never read while deciding. It gives two independent, high-powered questions:
#   SELECTION  does P(s | context) put the human-annotated sense on top, better than the resting level?
#   VALUE      does SUM_s P(s|ctx) v(s) agree with the value of the sense the HUMAN says is active?
# The second is the one the brief's twin needs: permuting the values across the senses of the same word
# must destroy it. NOTE the dependency, stated honestly: the resting-level counts in the asset ARE SemCor
# tallies, so the MFS floor here is a STRONG floor (it is the corpus's own frequency), which biases this
# comparison AGAINST the context read, not for it.
# ==========================================================================================================
def semcor_probe(F, cap: int = 1000, seed: int = SEED + 21) -> Dict:
    """SELECTION and VALUE against a human sense annotation, with the spreading activation computed ONCE per
    token and the blend temperature swept over it (lam changes only the blend, never the activation)."""
    ch = BASE["channels"]
    try:
        import numpy as np
        from nltk.corpus import semcor, wordnet as wn
        from hdlab.grounded_semantic_graph import _sense_ppr
    except Exception as e:
        return {"error": repr(e)}
    items = []
    for sent in semcor.tagged_sents(tag="sem"):
        toks, marks = [], []
        for chunk in sent:
            lemma = None
            if hasattr(chunk, "label"):
                lb = chunk.label()
                if hasattr(lb, "synset"):
                    lemma = lb
                words = chunk.leaves()
            else:
                words = list(chunk)
            if lemma is not None and len(words) == 1:
                marks.append((len(toks), lemma))
            toks.extend(words)
        for idx, lm in marks:
            try:
                syn = lm.synset()
            except Exception:
                continue
            if syn.pos() != "v":
                continue
            name = lm.name().split(".")[-1].lower()
            rows = sense_rows(name)
            if len(rows) < 2 or syn.name() not in [r[0] for r in rows]:
                continue
            vals = [row_value(r, ch) for r in rows]
            if len({("" if v is None else round(v, 3)) for v in vals}) < 2:
                continue
            items.append((name, syn.name(), toks, idx))
            if len(items) >= cap:
                break
        if len(items) >= cap:
            break
    if not items:
        return {"n": 0}

    tw = twin_values_within_word()
    rng = random.Random(seed)
    perm = list(range(len(items)))
    rng.shuffle(perm)
    g = gsg()

    def ppr_of(toks, idx, name, rows):
        ctx = context_words(toks, idx)
        if not enough_context(ctx):
            return None
        tgt = [wn.synset(r[0]) for r in rows]
        tn = [r[0] for r in rows]
        return _sense_ppr(wn, name, "V", ctx, g.syn2idx, g.T, len(g.syn2idx), tgt, tn)

    def blend(prior, ppr, lam):
        if ppr is None:
            return prior
        pp = np.asarray(ppr, float) + 1e-6
        pp = pp / pp.sum()
        lg = np.log(np.asarray(prior, float)) + lam * np.log(pp)
        lg = lg - lg.max()
        q = np.exp(lg)
        return list(q / q.sum())

    cache = []
    for i, (name, goldsyn, toks, idx) in enumerate(items):
        rows = sense_rows(name)
        oth = items[perm[i]]
        cache.append((name, goldsyn, rows, sense_prior(rows), ppr_of(toks, idx, name, rows),
                      ppr_of(oth[2], oth[3], name, rows)))

    out: Dict = {"n_tokens": len(items),
                 "note": "SemCor is a MEASURING instrument here (never read while deciding). The resting "
                         "levels in the asset ARE SemCor tallies, so the MFS floor is the corpus's own "
                         "frequency -- a STRONG floor that biases this comparison against the context read."}
    per_lam = {}
    for lam in (0.5, 1.0, 2.0, 4.0, 8.0):
        sel, sel_tw, val, val_tw, val_mfs, val_word = [], [], [], [], [], []
        diff_real, diff_twin = [], []
        for name, goldsyn, rows, prior, ppr, ppr_tw in cache:
            names = [r[0] for r in rows]
            j = names.index(goldsyn)
            post = blend(prior, ppr, lam)
            post_tw = blend(prior, ppr_tw, lam)
            sel.append(int(max(range(len(rows)), key=lambda k: post[k]) == j))
            sel_tw.append(int(max(range(len(rows)), key=lambda k: post_tw[k]) == j))
            gv = row_value(rows[j], ch)
            if gv is None or abs(gv) < 0.05:
                continue
            gsign = 1 if gv > 0 else -1
            e = sum(pi * (row_value(r, ch) or 0.0) for pi, r in zip(post, rows))
            et = sum(pi * (tw.get(name + "|" + r[0]) or 0.0) for pi, r in zip(post, rows))
            em = sum(pi * (row_value(r, ch) or 0.0) for pi, r in zip(prior, rows))
            wv = asset().get("words", {}).get(name, {}).get("v")
            sg = lambda x: (1 if x > 0 else -1) if abs(x) > 1e-9 else 0
            val.append(int(sg(e) == gsign))
            val_tw.append(int(sg(et) == gsign))
            val_mfs.append(int(sg(em) == gsign))
            val_word.append(int(sg(wv or 0.0) == gsign))
            if sg(e) != sg(et):                 # the twin is the IDENTITY on most tokens; a twin that does
                diff_real.append(int(sg(e) == gsign))    # not perturb an item cannot lose on it, so the
                diff_twin.append(int(sg(et) == gsign))   # powered comparison is the perturbed subset
        row = {"n_value_testable": len(val)}
        for k, v in (("selection", sel), ("selection_ctx_scrambled_twin", sel_tw),
                     ("value_sense_keyed", val), ("value_twin_within_word", val_tw),
                     ("value_resting_level_only", val_mfs), ("value_word_form_norm", val_word)):
            m, h = boot_ci(v)
            row[k] = [round(m, 4), round(h, 4), len(v)]
        for a_, b_, A, B in (("selection", "selection_ctx_scrambled_twin", sel, sel_tw),
                             ("value_sense_keyed", "value_word_form_norm", val, val_word),
                             ("value_sense_keyed", "value_resting_level_only", val, val_mfs),
                             ("value_sense_keyed", "value_twin_within_word", val, val_tw)):
            d, lo, hi = paired_boot(A, B)
            row["delta_%s_minus_%s" % (a_, b_)] = [round(d, 4), round(lo, 4), round(hi, 4),
                                                   "CI-SEPARATED" if lo > 0 else "not separated"]
        if diff_real:
            d, lo, hi = paired_boot(diff_real, diff_twin)
            row["twin_perturbed_subset"] = {"n": len(diff_real),
                                            "real": round(sum(diff_real) / len(diff_real), 4),
                                            "twin": round(sum(diff_twin) / len(diff_twin), 4),
                                            "delta": [round(d, 4), round(lo, 4), round(hi, 4),
                                                      "CI-SEPARATED" if lo > 0 else "not separated"]}
        else:
            row["twin_perturbed_subset"] = {"n": 0}
        per_lam["lam%.1f" % lam] = row
    out["by_lam"] = per_lam
    out["shipped"] = per_lam["lam%.1f" % BASE["lam"]]
    return out


def cue_report(lem, gold, glabel) -> Dict:
    """THE DECISIVE DIAGNOSTIC (the brief's item 4, split as a 2x2 on the human gold): where the WORD-FORM
    norm and the SENSE-KEYED expectation both fire, which one agrees with the independent human gold? And
    which sense-value CHANNEL carries the disagreement? An arm that substitutes a noisier estimator for a
    better one loses even when the theory is right, so this is measured before anything is shipped."""
    import collections
    rows = []
    for v in lem:
        g = glabel(v)
        if g not in ("HARM", "HELP"):
            continue
        se = sense_expectation(v, None)
        if se is None:
            continue
        e, cov, p, _op, _nm = se
        w = asset().get("words", {}).get(v, {})
        best = None
        for pi, r in zip(p, sense_rows(v)):
            if row_value(r) is None:
                continue
            if best is None or pi > best[0]:
                ch = [c for c in CHANNELS if c in (r[3] or {})]
                best = (pi, ch[0] if ch else "?", row_value(r), r[0])
        rows.append((v, g, w.get("v"), w.get("rho", 1.0), e, cov, best))

    def ag(x, g):
        return None if x is None else int((x > 0) == (g == "HELP"))
    out: Dict = {"n_cf_covered_with_senses": len(rows), "mean_coverage": round(
        sum(r[5] for r in rows) / max(1, len(rows)), 4)}
    for name, get in (("word_norm", lambda r: r[2] if (r[2] is not None and abs(r[2]) >= TAU_E) else None),
                      ("sense_E", lambda r: r[4] if abs(r[4]) >= TAU_E else None)):
        a = [ag(get(r), r[1]) for r in rows]
        a = [x for x in a if x is not None]
        out[name] = {"fires": len(a), "cf_agree": round(sum(a) / max(1, len(a)), 4)}
    sh = [r for r in rows if r[2] is not None and abs(r[2]) >= TAU_E and abs(r[4]) >= TAU_E]
    wr = sum(ag(r[2], r[1]) for r in sh)
    sr = sum(ag(r[4], r[1]) for r in sh)
    dis = [r for r in sh if ag(r[2], r[1]) != ag(r[4], r[1])]
    out["shared_subset"] = {"n": len(sh), "word_norm": round(wr / max(1, len(sh)), 4),
                            "sense_E": round(sr / max(1, len(sh)), 4),
                            "disagreements": len(dis),
                            "word_right": sum(ag(r[2], r[1]) for r in dis),
                            "sense_right": sum(ag(r[4], r[1]) for r in dis),
                            "sample": [(r[0], r[1], round(r[2], 2), round(r[3], 2), round(r[4], 3),
                                        r[6][1] if r[6] else None) for r in sorted(dis)[:20]]}
    per = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        if r[6] is None or abs(r[4]) < TAU_E:
            continue
        per[r[6][1]][1] += 1
        per[r[6][1]][0] += ag(r[4], r[1])
    out["by_dominant_channel"] = {k: [v[0], v[1], round(v[0] / v[1], 4)] for k, v in sorted(per.items())}
    # the same, with M admitted -- the measured re-run of the refuted L1 ordering
    perM = collections.defaultdict(lambda: [0, 0])
    for v, g, _vw, _rho, _e, _cov, _b in rows:
        seM = sense_expectation(v, None, channels=("R", "C", "M", "H", "S"))
        if seM is None or abs(seM[0]) < TAU_E:
            continue
        best = None
        for pi, r in zip(seM[2], sense_rows(v)):
            rv = row_value(r, ("R", "C", "M", "H", "S"))
            if rv is None:
                continue
            if best is None or pi > best[0]:
                ch = [c for c in ("R", "C", "M", "H", "S") if c in (r[3] or {})]
                best = (pi, ch[0] if ch else "?")
        if best is None:
            continue
        perM[best[1]][1] += 1
        perM[best[1]][0] += ag(seM[0], g)
    out["by_dominant_channel_with_M"] = {k: [v[0], v[1], round(v[0] / v[1], 4)] for k, v in sorted(perM.items())}
    return out


def fusion_modes_report(F, lem, gold, glabel, A, M98) -> Dict:
    """Every fusion SHAPE and every operating point, measured on every population, so the shape is chosen
    by the numbers and not by argument (the pri-98 lesson: the "obviously right" reordering was refuted)."""
    cfgs = {
        "word_only": dict(mode="word_only"),
        "sense_only": dict(mode="sense_only"),
        "shift": dict(mode="shift"),
        "substitute_kw1": dict(mode="substitute", k_w=1.0),
        "substitute_kw2": dict(mode="substitute", k_w=2.0),
        "substitute_kw4": dict(mode="substitute", k_w=4.0),
        "gated_cov0.5": dict(mode="gated", tau_cov=0.5),
    }
    # the DECIDED-NEUTRAL rule on top of the best-behaved substitute shape
    for op in (0.2, 0.3, 0.5, 0.7):
        cfgs["substitute_kw1_op%.1f" % op] = dict(mode="substitute", k_w=1.0, tau_opinion=op)
    for tau in (0.15, 0.20):
        cfgs["substitute_kw1_op0.3_tau%.2f" % tau] = dict(mode="substitute", k_w=1.0,
                                                          tau_opinion=0.3, tau=tau)
    out = {}
    for name, kw in cfgs.items():
        full = dict(lam=LAM, channels=CHANNELS, neutral_rule=NEUTRAL_RULE, tau_opinion=0.0)
        full.update(kw)
        out[name] = evaluate(F, lem, glabel, A, M98, **full)
    return out


def lever_report(F, lem, gold, glabel, A, M98, base) -> Dict:
    """THE UPSTREAM LEVERS on the sense-SELECTION half (pri-98 measured that selection, not keying, is the
    weak half): the posterior temperature, the argument-weighted seeding, and the channel inventory."""
    out = {}
    global W_ARG
    for lam in (0.5, 1.0, 2.0, 4.0, 8.0):
        kw = dict(base); kw["lam"] = lam
        out["lam%.1f" % lam] = evaluate(F, lem, glabel, A, M98, **kw)
    old = W_ARG
    try:
        for wa in (0.0, 2.0, 4.0, 8.0, 16.0):
            W_ARG = wa
            out["w_arg%.0f" % wa] = evaluate(F, lem, glabel, A, M98, **base)
    finally:
        W_ARG = old
    for ch in (("R", "C", "H", "S"), ("R", "C", "H", "S", "T"), ("R", "H", "T"), ("R", "H"),
               ("R", "C", "M", "H", "S", "T"), ("R", "H", "S", "T"), ("R", "C", "M", "H", "T")):
        kw = dict(base); kw["channels"] = ch
        out["ch_" + "".join(ch)] = evaluate(F, lem, glabel, A, M98, **kw)
    return out


def candidate_verbs(F, isaff) -> List[str]:
    from nltk.corpus import wordnet as wn
    afx = F._afx()
    cand = [w for w in afx.val if " " not in w and wn.synsets(w, "v")]
    return sorted(set(F.lemmatize_verb(v) for v in cand if isaff(v)))


def cf_report(lem, gold, glabel, arms: Dict) -> Dict:
    out: Dict = {"n_candidates": len(lem)}
    for name, fn in arms.items():
        a = t = 0
        disc = []
        dec = 0
        for v in lem:
            p = fn(v, "animate")
            if p in ("HARM", "HELP"):
                dec += 1
            g = glabel(v)
            if g in ("HARM", "HELP") and p in ("HARM", "HELP"):
                t += 1
                if g == p:
                    a += 1
                else:
                    disc.append((v, p, g, round(gold[v], 2)))
        out[name] = {"whole_arm": [a, t, round(a / max(1, t), 4)], "n_decided": dec,
                     "discordant_sample": sorted(disc)[:15]}
    return out


def prose_accuracy(F, es, ia, M98) -> float:
    a = arm(F, es, ia)
    c = [prose_correct(harm_help_prose(F, a, g[1], M98.prose_sentence(g[0], g[1], g[2], g[3]), 2), g[4])
         for g in M98.ADVERB_PROSE_GOLD]
    return round(sum(c) / len(c), 4)


def prose_report(F, floor, pri98, es_sense, ia_sense, M98) -> Dict:
    """The n=36 adverb-in-prose gold. The 8 target errors are the NEUTRAL-cell items the FLOOR answers HELP."""
    import hdlab.force_dynamics_valence as HEAD
    rows = []
    holder = {"ctx": None}
    es_ctx = make_endstate(F, ctx_get=lambda: holder["ctx"], **BASE)
    sense_ctx = arm(F, es_ctx, ia_sense)
    sense_noctx = arm(F, es_sense, ia_sense)
    for agent, verb, patient, adverb, label in M98.ADVERB_PROSE_GOLD:
        toks = M98.prose_sentence(agent, verb, patient, adverb)
        gov = 2
        holder["ctx"] = bound_context(toks, gov)
        v = HEAD.lemmatize_verb(verb)
        se_prior = sense_expectation(v, None)
        se_ctx = sense_expectation(v, holder["ctx"])
        rows.append({
            "sent": " ".join(toks), "gold": label, "verb": verb, "adverb": adverb,
            "floor": floor(v, "animate"),
            "pri98": harm_help_prose(F, pri98, verb, toks, gov),
            "sense_prior": harm_help_prose(F, sense_noctx, verb, toks, gov),
            "sense_ctx": harm_help_prose(F, sense_ctx, verb, toks, gov),
            "rho": asset().get("words", {}).get(v, {}).get("rho"),
            "warriner": asset().get("words", {}).get(v, {}).get("v"),
            "E_prior": None if se_prior is None else round(se_prior[0], 3),
            "E_ctx": None if se_ctx is None else round(se_ctx[0], 3),
            "cov": None if se_ctx is None else round(se_ctx[1], 3),
            "opinion": None if se_ctx is None else round(se_ctx[3], 3),
            "fused_ctx": None if se_ctx is None else round(fused_value(v, holder["ctx"]) or 0.0, 3),
        })
        holder["ctx"] = None
    out: Dict = {"n": len(rows), "rows": rows}
    cols = ("floor", "pri98", "sense_prior", "sense_ctx")
    corr = {c: [prose_correct(r[c], r["gold"]) for r in rows] for c in cols}
    for c in cols:
        m, h = boot_ci(corr[c])
        out[c + "_acc"] = [round(m, 4), round(h, 4)]
    for c in ("sense_prior", "sense_ctx"):
        for base in ("floor", "pri98"):
            d, lo, hi = paired_boot(corr[c], corr[base])
            out["delta_%s_minus_%s" % (c, base)] = [round(d, 4), round(lo, 4), round(hi, 4),
                                                    "CI-SEPARATED" if lo > 0 else "not separated"]
    out["by_cell"] = {cell: {c: sum(prose_correct(r[c], r["gold"]) for r in rows if r["gold"] == cell)
                             for c in cols} | {"n": sum(1 for r in rows if r["gold"] == cell)}
                      for cell in ("HARM", "HELP", "NEUTRAL")}
    # THE 8 TARGET ERRORS: NEUTRAL-cell items the FLOOR answers HARM/HELP on
    tgt = [r for r in rows if r["gold"] == "NEUTRAL" and r["floor"] in ("HARM", "HELP")]
    out["target_errors"] = {
        "n_floor": len(tgt),
        "n_still_wrong_pri98": sum(1 for r in tgt if r["pri98"] in ("HARM", "HELP")),
        "n_still_wrong_sense_prior": sum(1 for r in tgt if r["sense_prior"] in ("HARM", "HELP")),
        "n_still_wrong_sense_ctx": sum(1 for r in tgt if r["sense_ctx"] in ("HARM", "HELP")),
        "detail": [(r["verb"], r["floor"], r["pri98"], r["sense_prior"], r["sense_ctx"],
                    r["E_prior"], r["E_ctx"], r["fused_ctx"]) for r in tgt],
    }
    return out


def live_gold_report(floor, pri98, sense) -> Dict:
    try:
        import experiments.exp_fd_harm_help_live_modern_v1 as LIVE
    except Exception as e:
        return {"error": repr(e)}
    out = {}
    for name, fn in (("floor", floor), ("pri98", pri98), ("sense", sense)):
        n = tot = 0
        broke = []
        for g in LIVE.GOLD:
            verb, label = g[1], g[3]
            if label not in ("HARM", "HELP"):
                continue
            tot += 1
            ok = fn(verb, "animate") == label
            n += ok
            if not ok:
                broke.append((verb, fn(verb, "animate"), label))
        nl = [(g[1], fn(g[1], "animate")) for g in LIVE.GOLD if g[3] == "NEUTRAL"
              and fn(g[1], "animate") in ("HARM", "HELP")]
        out[name] = {"correct": n, "n": tot, "wrong": broke, "neutral_items_decided": nl}
    return out


def sweep_report(F, lem, gold, glabel, A, M98, base) -> Dict:
    """The phase diagram: the word-norm precision scale k_w x the decision threshold tau, at the shipped
    opinion gate. Reported on EVERY population so the operating point is not picked on the target."""
    sw = {}
    for k_w in (0.5, 1.0, 2.0, 4.0, 8.0):
        for tau in (0.05, 0.10, 0.15, 0.20, 0.30):
            kw = dict(base)
            kw.update(k_w=k_w, tau=tau)
            sw["kw%.1f_tau%.2f" % (k_w, tau)] = evaluate(F, lem, glabel, A, M98, prose=True, **kw)
    return sw


def online_report(F, M98) -> Dict:
    """PLASTIC, NEVER FROZEN -- exercised, not asserted. Reading `treat` used in its medical sense raises
    that sense's resting level; the expectation is one pure function of those counts, so the value moves."""
    before = sense_expectation("treat", None)
    rows0 = [list(r) for r in sense_rows("treat")]
    for _ in range(200):
        observe_sense("treat", "treat.v.03")
    after = sense_expectation("treat", None)
    fused_after = fused_value("treat", None)
    asset()["senses"]["treat"] = rows0          # restore
    back = sense_expectation("treat", None)
    return {"E_before": round(before[0], 4), "cov_before": round(before[1], 4),
            "E_after_200_medical_observations": round(after[0], 4),
            "fused_after": round(fused_after, 4),
            "E_restored": round(back[0], 4),
            "mechanism": "observe_sense increments the SemCor-unit resting-level count; the expectation is "
                         "SUM_s P(s) v(s) with P from those counts -- one pure function, no second path"}


# ==========================================================================================================
# self-test
# ==========================================================================================================
def self_test() -> bool:
    ok = True
    out_dir = get_output_dir(ANCHOR)
    F = fdv98(out_dir)
    # 1. the pri-98 diff really applied to the copy, and hdlab is untouched
    import hdlab.force_dynamics_valence as HEAD
    assert getattr(F, "MANNER_READ", None) is True, "pri-98 patch did not apply"
    assert not hasattr(HEAD, "MANNER_READ"), "hdlab/ was modified -- ABORT"
    assert F.manner_state_sign("brutalize") == -1, "patched copy does not reproduce pri-98"
    assert HEAD.harm_help("brutalize", "animate") is None, "HEAD floor changed"
    print("  [ok] pri-98 patch applied to the COPY only; HEAD unchanged")
    # 2. the asset is sense-keyed and carries counts
    a = asset()
    assert a["senses"], "no sense asset -- run tools/build_sense_affect_norm_asset.py"
    assert all(len(r) == 4 and isinstance(r[3], dict) for r in a["senses"]["treat"]), "row shape"
    print("  [ok] sense asset: %d lemmas, %d words" % (len(a["senses"]), len(a["words"])))
    # 3. the fusion is a pure function of the counts (the online path moves it and restores)
    rows0 = [list(r) for r in sense_rows("treat")]
    e0 = sense_expectation("treat", None)[0]
    observe_sense("treat", "treat.v.03", 500)
    e1 = sense_expectation("treat", None)[0]
    asset()["senses"]["treat"] = rows0
    e2 = sense_expectation("treat", None)[0]
    assert e1 > e0 and abs(e2 - e0) < 1e-9, "online path not a pure function of counts"
    print("  [ok] online observe path moves the value (%.3f -> %.3f) and is count-pure" % (e0, e1))
    # 4. rho really discriminates
    w = asset()["words"]
    assert w["treat"]["rho"] < w["murder"]["rho"], "rho does not discriminate"
    print("  [ok] rho(treat)=%.3f < rho(murder)=%.3f" % (w["treat"]["rho"], w["murder"]["rho"]))
    # 5. the twin preserves the value multiset
    tw = twin_values_within_word()
    for lemma in ("treat", "kill", "help"):
        rows = sense_rows(lemma)
        assert sorted([str(row_value(r)) for r in rows]) == sorted(
            [str(tw[lemma + "|" + r[0]]) for r in rows]), "twin multiset"
    print("  [ok] within-word twin preserves each word's value multiset")
    # 6. THE PROPOSED hdlab DIFF REPRODUCES THIS CELL (not asserted -- computed side by side)
    AL = patched_affect_lexicon(out_dir)
    assert (AL.SENSE_TAU_NEUTRAL == TAU_OPINION and AL.SENSE_K_W == K_W
            and AL.SENSE_LAM == LAM), "patch operating point drift"
    assert tuple(AL.SENSE_CHANNELS) == tuple(BASE["channels"]), "patch channel drift"
    n = same = 0
    for v in sorted(asset()["senses"])[:600]:
        a1 = fused_value(v, None, k_w=K_W, channels=BASE["channels"], mode="substitute")
        a2 = AL.fused_sense_value(v)
        n += 1
        same += int((a1 is None and a2 is None) or (a1 is not None and a2 is not None and abs(a1 - a2) < 1e-9))
        s1 = sense_endstate_sign(v, None, **BASE)
        s2 = AL.sense_endstate_sign(v)
        assert s1 == s2, "patched module disagrees on %s: %s vs %s" % (v, s1, s2)
    assert same == n, "patched fused value differs on %d/%d verbs" % (n - same, n)
    print("  [ok] the proposed affect_lexicon diff reproduces the cell on %d verbs (value AND verdict)" % n)
    return ok


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        print("SELF-TEST")
        print("PASS" if self_test() else "FAIL")
        sys.exit(0)
    r = run()
    p = r["adverb_prose_gold"]
    print("\n=== ADVERB-IN-PROSE GOLD (n=%d) ===" % p["n"])
    for c in ("floor", "pri98", "sense_prior", "sense_ctx"):
        print("  %-12s %.4f +- %.4f" % (c, p[c + "_acc"][0], p[c + "_acc"][1]))
    for k in sorted(k for k in p if k.startswith("delta_")):
        print("  %-34s %s" % (k, p[k]))
    print("  target errors: floor %d -> pri98 %d -> sense_prior %d -> sense_ctx %d"
          % (p["target_errors"]["n_floor"], p["target_errors"]["n_still_wrong_pri98"],
             p["target_errors"]["n_still_wrong_sense_prior"], p["target_errors"]["n_still_wrong_sense_ctx"]))
    print("\n=== NO-REGRESS ===")
    print("  neutral leaks:", {k: len(v) for k, v in r["neutral_precision"].items() if k != "n"})
    print("  populations  :", r["populations"])
    print("  live gold    :", {k: (v.get("correct"), v.get("n")) for k, v in r["live_modern_gold"].items()})
    print("  CF whole-arm :", {k: v["whole_arm"] for k, v in r["cf"].items() if isinstance(v, dict)})
    print("  twins        :", {k: v["whole_arm"] for k, v in r["twins"].items() if isinstance(v, dict) and "whole_arm" in v})
    print("  twin prose   :", r["twins"]["prose"])
    print("  ctx twin     :", r["twins"]["prose_context_scrambled"]["acc"])
    print("  twin cf pair (all)      :", {k: v for k, v in r["twins"]["cf_paired_all"].items()})
    print("  twin cf pair (perturbed):", {k: v for k, v in r["twins"]["cf_paired_perturbed_only"].items()})
    print("\n=== SEMCOR SENSE-VALUE PROBE (the powered instrument) ===")
    sp = r["semcor_probe"]
    for lam, row in sp.get("by_lam", {}).items():
        print("  %s n_val=%d sel=%.4f sel_twin=%.4f | value: keyed=%.4f word=%.4f mfs=%.4f twin=%.4f"
              % (lam, row["n_value_testable"], row["selection"][0], row["selection_ctx_scrambled_twin"][0],
                 row["value_sense_keyed"][0], row["value_word_form_norm"][0],
                 row["value_resting_level_only"][0], row["value_twin_within_word"][0]))
    for k, v in sp.get("shipped", {}).items():
        if str(k).startswith("delta") or k == "twin_perturbed_subset":
            print("    SHIPPED %-52s %s" % (k, v))
    print("  residual 2x2 fixed %d/%d" % (r["residual_2x2"]["n_fixed"], r["residual_2x2"]["n"]))
    for it in r["residual_2x2"]["items"]:
        print("     %-44s %-6s %s" % (it["sent"], it["pred"], it["diagnosis"]))
    print("  cf paired    :", {k: v for k, v in r["cf_paired"].items() if not isinstance(v, dict)
                               or "acc" in v or "delta" in str(k)})
    print("  online       :", r["online"])
    print("\n=== CUE DIAGNOSTIC (independent human gold) ===")
    c = r["cue_accuracy"]
    print("  word_norm", c["word_norm"], " sense_E", c["sense_E"])
    print("  shared   ", c["shared_subset"]["n"], "word %.4f sense %.4f | disagree %d word-right %d sense-right %d"
          % (c["shared_subset"]["word_norm"], c["shared_subset"]["sense_E"], c["shared_subset"]["disagreements"],
             c["shared_subset"]["word_right"], c["shared_subset"]["sense_right"]))
    print("  by channel", c["by_dominant_channel"])
    print("  with M    ", c["by_dominant_channel_with_M"])
    print("\n=== LEVERS (selection half) ===")
    for k, v in r["levers"].items():
        print("  %-14s cf=%-18s leaks=%d live=%d prose=%.4f target=%s"
              % (k, v["cf_whole_arm"], v["leaks"], v["live_gold_24"], v["prose_acc"][0],
                 v["target_errors_remaining"]))
    print("\n=== PUSH GRID (rows that hold every no-regress bar first) ===")
    def _ok(v):
        return (v["leaks"] == 0 and v["live_gold_24"] == 24 and v["named_manner_15"] == 15
                and v["slice6"] == 6)
    for k, v in sorted(r["push_grid"].items(), key=lambda kv: (not _ok(kv[1]),
                                                               kv[1]["target_errors_remaining"][0],
                                                               -kv[1]["cf_whole_arm"][2])):
        print("  %-38s %s cf=%-18s leaks=%d live=%d named=%d slice=%d prose=%.4f target=%s"
              % (k, "OK " if _ok(v) else "   ", v["cf_whole_arm"], v["leaks"], v["live_gold_24"],
                 v["named_manner_15"], v["slice6"], v["prose_acc"][0], v["target_errors_remaining"]))
    print("\n=== FUSION SHAPES ===")
    for k, v in r["fusion_modes"].items():
        print("  %-26s cf=%-18s leaks=%d live=%d prose=%.4f target=%s named15=%d"
              % (k, v["cf_whole_arm"], v["leaks"], v["live_gold_24"], v["prose_acc"][0],
                 v["target_errors_remaining"], v["named_manner_15"]))
