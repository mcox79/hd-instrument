"""hdlab/attachment_arm.py -- the ATTACHMENT arm of the Competition-Model organ (graded_role_assigner): "which word heads this
word", decided by cue competition with LEARNED, configuration-conditioned strengths, read out as the exact tree posterior.

Landed 2026-09-12 (strategy; spec notes/RESEARCH_attachment_organ_spec_2026-09-12.md; probes v18/v21/v22). One structure, two arms:
the role competition (graded_role_assigner.coarse_roles) and this head competition share the cue machinery (categorical cue values
-> contrasts learned from counts -> additive activation -> normalised posterior) and the same plastic knowledge form.

BRAIN COMPUTATION (PINNED at the computational level): attachment = constraint-based cue competition (MacDonald-Pearlmutter-Seidenberg
1994) over candidates retrieved under memory-limited decay (Lewis & Vasishth 2005; locality), with alternatives kept alive and
weighted by probability (Hale/Levy); item-based CONSTRUCTIONS (Tomasello 2003) are cue coalitions. MODEL: the exact single-root
Matrix-Tree marginal (graded_parser) = the normative keep-alternatives-alive; soft-count self-supervision = "the posterior teaches the
cue statistics". Pre-lexical FORM knowledge enters as constraints (punctuation/numerals never head; punctuation = written prosody
-> boundary cue). REFUTED (recorded): unconditioned additive cues (drift), a frequency-driven root prior (crowns punctuation), a
hand-authored universal prior (kept OUT of the organ; it was worth ~0.10 and is what meaning should supply).

CUES (values categorical; strengths = contrast log-odds(arc | config, value) - log-odds(arc | config), config = category pair):
  locality (direction x log-distance bin), catpair (config), frame (head verb's transitivity from learned counts x dependent
  class x direction), form (candidate is a form class), boundary (marks spanned), agree (number-agreement sketch), constr (which
  construction proposes the arc: verbarg / coord / npmod / clausal), root (dependent category for the ROOT decision).

KNOWLEDGE FORM (plastic, never frozen): data/frontend_assets/attachment_validities_v1.json carries the COUNTS (soft true / total per
"config|value"); strengths are a pure function of the counts (strengths_from_arc_counts); observe_arc_outcome(...) accrues a
comprehension outcome online; save_attachment_validities() persists. Built offline by tools/build_attachment_validities.py from a
KNOWLEDGE-FREE teacher (no treebank, no hand prior) + anchored self-teaching -- the measured gate (ledger): 0.272 -> 0.43+ UAS.

MEASURED (UD-EWT test 700, gold categories, probe v18): prior-informed bootstrap + constructions 0.5303; knowledge-free bootstrap
+ constructions 0.4316 (rising); adjacent-right floor 0.285; supervised 0.78; brain 0.9+ (the gap: meaning feeding structure,
the argument-structure lexicon at scale, incremental reanalysis). Glass-box, numpy only, NO LLM, NO external parser.
"""
from __future__ import annotations

__bf_status__ = "BF_SPIRIT"   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors notes/bf_status_registry.jsonl
__bf_verified__ = "2026-09-12 strategy: cue competition + tree posterior PINNED/MODEL; strengths LEARNED from soft counts, knowledge-free bootstrap"
__bf_note__ = "attachment arm of the Competition-Model organ; constructions hand-written item-based schemas (induced forms refuted as built); hand prior kept OUT"
__bf_corrections__ = []

import json
import math
import os
from collections import defaultdict
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from hdlab.graded_parser import chu_liu_edmonds, single_root_marginals
from hdlab.thematic_role_labeler import lemma_verb

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSET = os.path.join(_REPO, "data", "frontend_assets", "attachment_validities_v1.json")
FORM = frozenset({"PUNCT", "NUM", "SYM"})
NOMINAL = ("NOUN", "PRON", "PROPN")
CONTENT = frozenset({"NOUN", "PROPN", "PRON", "VERB", "ADJ", "ADV", "NUM"})
NP_RUN = frozenset({"DET", "ADJ", "NUM", "NOUN", "PROPN"})
CUES = ("locality", "frame", "form", "boundary", "agree", "constr")     # secondary cues; catpair / root are the configuration
M_SHRINK = 2.0
# CONVENTION LAYER (labelled honestly, 2026-09-12): the function-word frames (ADP -> its NP head, AUX/copula -> their predicate,
# SCONJ/'to' -> the verb, names left-headed, punctuation -> the clause verb) are ANNOTATION CONVENTIONS of UD-shaped consumers, not
# facts a raw-text statistic determines -- self-supervision cannot learn them (measured: as a learned cue +0.013; applied at decode
# +0.036 on the smoke slice). They are applied as a deterministic decode-time bonus for consumers that read UD-shaped heads; the
# learned competition (the comprehension organ) is untouched. Set CONVENTION_BONUS = 0.0 to read the pure learned organ.
CONVENTION_BONUS = 5.0
BF_TSP_ASSET = os.path.join(_REPO, "data", "frontend_assets", "typed_selectional_preference_bf_v1.json")   # self-grown plausibility
_TABLE: Optional[Dict[str, object]] = None


# ------------------------------------------------------------------------------------------------------ constructions
def verbarg_arcs(toks: Sequence[str], pos: Sequence[str]) -> List[Tuple[int, int]]:
    """Now-or-Never left-corner verb-argument bind (hdlab.incremental_parser), structural."""
    from hdlab.incremental_parser import incremental_build
    frames = incremental_build(list(toks), list(pos), use_revise=True)
    n = len(toks); out = []
    for v, args in frames.items():
        for a in args:
            if 1 <= a <= n and 1 <= v <= n and a != v:
                out.append((v, a))
    return out


def coord_arcs(toks: Sequence[str], pos: Sequence[str]) -> List[Tuple[int, int]]:
    """Coordination parallelism: A cc B with the same category -> B attaches to A, cc to B."""
    n = len(toks); out = []
    for k in range(1, n + 1):
        if pos[k - 1] != "CCONJ":
            continue
        first = max([j for j in range(1, k) if pos[j - 1] in CONTENT], default=None)
        second = min([j for j in range(k + 1, n + 1) if pos[j - 1] in CONTENT], default=None)
        if first and second and pos[first - 1] == pos[second - 1]:
            out.append((first, second)); out.append((second, k))
    return out


def npmod_arcs(toks: Sequence[str], pos: Sequence[str]) -> List[Tuple[int, int]]:
    """NP-internal modifier construction: within a contiguous nominal run every element attaches to the last NOUN/PROPN."""
    n = len(pos); out = []; i = 0
    while i < n:
        if pos[i] not in NP_RUN:
            i += 1; continue
        j = i
        while j < n and pos[j] in NP_RUN:
            j += 1
        run = list(range(i, j)); heads = [k for k in run if pos[k] in ("NOUN", "PROPN")]
        if heads:
            h = heads[-1] + 1
            for k in run:
                if k + 1 != h:
                    out.append((h, k + 1))
        i = j
    return out


def clausal_arcs(toks: Sequence[str], pos: Sequence[str]) -> List[Tuple[int, int]]:
    """Matrix-verb bind: a non-initial VERB not right after a coordinator attaches to the nearest preceding VERB."""
    n = len(pos); out = []; prev = None
    for i in range(n):
        if pos[i] == "VERB":
            if prev is not None and not (i > 0 and pos[i - 1] == "CCONJ"):
                out.append((prev + 1, i + 1))
            prev = i
    return out


def function_word_arcs(toks: Sequence[str], pos: Sequence[str]) -> List[Tuple[int, int]]:
    """FUNCTION-WORD frames (Mintz 2003 frequent frames: high precision, narrow reach; the error anatomy 2026-09-12 put a third of
    the gap to the supervised parser here): a preposition attaches to the head of the nominal run that follows it ("ADP _ NOUN");
    an auxiliary attaches to the verb that follows it; a copula (be/become/seem + no following verb) attaches to the non-verbal
    predicate that follows; a subordinator / infinitival 'to' attaches to the following verb; a run of proper nouns is LEFT-headed
    (the first name heads the rest); a punctuation mark attaches to the nearest verb (the clause predicate). Item-based schemas
    learned as form-position templates; deterministic once learned."""
    n = len(pos); out = []; lows = [t.lower() for t in toks]
    COP = {"be", "is", "are", "was", "were", "been", "being", "am", "become", "became", "becomes", "seem", "seems", "seemed"}
    def np_head_after(i):                   # head noun of the nominal run starting at i (0-based) or None
        j = i
        while j < n and pos[j] in NP_RUN:
            j += 1
        heads = [k for k in range(i, j) if pos[k] in ("NOUN", "PROPN")]
        return heads[-1] if heads else None
    def next_verb(i):
        for k in range(i + 1, n):
            if pos[k] == "VERB":
                return k
            if pos[k] == "PUNCT":
                break
        return None
    def next_predicate(i):                  # first ADJ / NOUN / PROPN / PRON before any verb
        for k in range(i + 1, n):
            if pos[k] == "VERB" or pos[k] == "PUNCT":
                return None
            if pos[k] in ("ADJ", "NOUN", "PROPN", "PRON", "NUM"):
                return k if pos[k] != "NOUN" and pos[k] != "PROPN" else (np_head_after(k) if np_head_after(k) is not None else k)
        return None
    for i in range(n):
        p = pos[i]
        if p == "ADP" and i + 1 < n and pos[i + 1] in NP_RUN:
            h = np_head_after(i + 1)
            if h is not None:
                out.append((h + 1, i + 1))
        elif p == "AUX":
            v = next_verb(i)
            if v is not None:
                out.append((v + 1, i + 1))
            elif lows[i] in COP:
                q = next_predicate(i)
                if q is not None:
                    out.append((q + 1, i + 1))
        elif p == "SCONJ" or (p == "PART" and lows[i] == "to"):
            v = next_verb(i)
            if v is not None:
                out.append((v + 1, i + 1))
        elif p == "PROPN" and i > 0 and pos[i - 1] == "PROPN":
            k = i
            while k > 0 and pos[k - 1] == "PROPN":
                k -= 1
            out.append((k + 1, i + 1))       # flat: left-headed name
        elif p == "PUNCT":
            cands = [k for k in range(n) if pos[k] == "VERB"]
            if cands:
                h = min(cands, key=lambda k: (abs(k - i), k))
                out.append((h + 1, i + 1))
    return out


CONSTRUCTIONS = {"verbarg": verbarg_arcs, "coord": coord_arcs, "npmod": npmod_arcs, "clausal": clausal_arcs, "fw": function_word_arcs}


def construction_map(toks: Sequence[str], pos: Sequence[str]) -> Dict[Tuple[int, int], str]:
    out: Dict[Tuple[int, int], str] = {}
    for fam, fn in CONSTRUCTIONS.items():
        try:
            for (h, d) in fn(toks, pos):
                out.setdefault((h, d), fam)
        except Exception:
            pass
    return out


# --------------------------------------------------------------------------------------------------------- cue values
def dist_bin(d: int) -> str:
    return "1" if d == 1 else "2" if d == 2 else "3-4" if d <= 4 else "5-8" if d <= 8 else "9+"


def verb_frames_from_reading(sentences: Sequence[Tuple[Sequence[str], Sequence[str]]]) -> Dict[str, List[int]]:
    """Per verb lemma [n_occurrences, n_with_a_bare_post-verbal_nominal_within_3] -- from TOKENS only (no labels)."""
    fr: Dict[str, List[int]] = defaultdict(lambda: [0, 0])
    for toks, pos in sentences:
        n = len(toks)
        for v in range(n):
            if pos[v] != "VERB":
                continue
            lem = lemma_verb(toks[v]).lower(); fr[lem][0] += 1
            for j in range(v + 1, min(n, v + 4)):
                if pos[j] in NOMINAL and not (j - 1 > v and pos[j - 1] == "ADP"):
                    fr[lem][1] += 1; break
    return {k: v for k, v in fr.items() if v[0] >= 5}


class SentenceCues:
    """ONE cue pass per sentence (shared by every arc): punctuation cumsum for boundaries, construction map, verb lemmas."""

    def __init__(self, toks: Sequence[str], pos: Sequence[str], frames: Dict[str, List[int]]):
        self.toks = list(toks); self.pos = list(pos); self.n = len(toks); self.frames = frames
        self.cum = np.concatenate([[0], np.cumsum([1 if p == "PUNCT" else 0 for p in self.pos])])
        self.constr = construction_map(self.toks, self.pos)
        self.lem = [lemma_verb(t).lower() if p == "VERB" else None for t, p in zip(self.toks, self.pos)]

    def config(self, j: int, h: int) -> str:
        pj = self.pos[j - 1]
        if h == 0:
            return "ROOT:" + pj
        return f"{self.pos[h - 1]}>{pj}:{'L' if h < j else 'R'}"

    def cues(self, j: int, h: int) -> Dict[str, str]:
        if h == 0:
            return {}
        pj = self.pos[j - 1]; ph = self.pos[h - 1]; dr = "L" if h < j else "R"
        lo, hi = (h, j) if h < j else (j, h)
        nb = int(self.cum[hi - 1] - self.cum[lo])
        c = {"locality": f"{dr}{dist_bin(abs(h - j))}", "form": "formhead" if ph in FORM else "wordhead",
             "boundary": "0" if nb == 0 else "1" if nb == 1 else "2+",
             "constr": self.constr.get((h, j), "none")}
        if ph == "VERB":
            fr = self.frames.get(self.lem[h - 1])
            trans = "unk" if not fr else ("trans" if fr[1] / fr[0] >= 0.3 else "intrans")
            c["frame"] = f"{trans}:{pj}:{dr}"
            w = self.toks[h - 1].lower(); wj = self.toks[j - 1].lower()
            if dr == "R" and pj in NOMINAL and w.endswith("s") and not w.endswith("ss"):
                plural = (pj == "NOUN" and wj.endswith("s") and not wj.endswith("ss")) or wj in ("they", "we", "you", "i")
                c["agree"] = "3sgV:" + ("plurN" if plural else "singN")
            else:
                c["agree"] = "na"
        else:
            c["frame"] = "na"; c["agree"] = "na"
        return c


# ------------------------------------------------------------------------------------------------- strengths / table
def _lo(p: float) -> float:
    p = min(max(p, 1e-6), 1 - 1e-6); return math.log(p / (1 - p))


def strengths_from_arc_counts(counts: Dict[str, object]) -> Dict[str, object]:
    """THE ONE implementation: config strength = lo(P(arc|config)) - lo(P(arc)); cue contrast = lo(P(arc|config,value)) -
    lo(P(arc|config)) with Dirichlet shrinkage (m) toward the configuration's own rate; a value that always fires within its
    configuration contributes exactly 0. counts = {"base": [t, n], "config": {cfg: [t, n]}, "cues": {cue: {"cfg|value": [t, n]}}}."""
    t0, n0 = counts["base"]; pb = (t0 + 0.5) / (n0 + 1.0)
    out = {"cfg": {}, "pcfg": {}}
    for cfg, (t, n) in counts["config"].items():
        p = (t + M_SHRINK * pb) / (n + M_SHRINK); out["pcfg"][cfg] = p; out["cfg"][cfg] = _lo(p) - _lo(pb)
    for cue, vals in counts["cues"].items():
        out[cue] = {}
        for key, (t, n) in vals.items():
            cfg = key.split("|", 1)[0]; base = out["pcfg"].get(cfg, pb); ncfg = counts["config"].get(cfg, [0, 0])[1]
            if n >= ncfg:
                out[cue][key] = 0.0
            else:
                p = (t + M_SHRINK * base) / (n + M_SHRINK); out[cue][key] = _lo(p) - _lo(base)
    return out


def load_attachment_validities(path: Optional[str] = None) -> Dict[str, object]:
    global _TABLE
    if path is None and _TABLE is not None:
        return _TABLE
    with open(path or ASSET, encoding="utf-8") as f:
        doc = json.load(f)
    tab = {"counts": doc["counts"], "frames": doc.get("frames", {}), "strength": strengths_from_arc_counts(doc["counts"])}
    if path is None:
        _TABLE = tab
    return tab


def save_attachment_validities(path: Optional[str] = None, table: Optional[Dict[str, object]] = None) -> str:
    tab = table or load_attachment_validities(); p = path or ASSET
    doc = {"source": "attachment arm of the Competition-Model organ: soft arc counts accrued from reading (knowledge-free teacher + "
                     "anchored self-teaching; no treebank, no hand prior); strengths = attachment_arm.strengths_from_arc_counts",
           "counts": tab["counts"], "frames": tab.get("frames", {})}
    with open(p, "w", encoding="utf-8", newline=chr(10)) as f:
        json.dump(doc, f, indent=1)
    return p


def new_counts() -> Dict[str, object]:
    return {"base": [0.0, 0.0], "config": {}, "cues": {c: {} for c in CUES}}


def accrue_sentence(counts: Dict[str, object], sc: "SentenceCues", marg: Dict[int, Dict[int, float]]) -> None:
    """Accrue SOFT outcomes: for every (j, h) the posterior probability that h heads j (the tree marginal) -- the comprehension
    outcome the organ learns from; online-capable (plastic)."""
    n = sc.n
    for j in range(1, n + 1):
        mj = marg.get(j, {})
        for h in range(0, n + 1):
            if h == j:
                continue
            p = float(mj.get(h, 0.0)); cfg = sc.config(j, h)
            cell = counts["config"].setdefault(cfg, [0.0, 0.0]); cell[0] += p; cell[1] += 1.0
            counts["base"][0] += p; counts["base"][1] += 1.0
            for c, v in sc.cues(j, h).items():
                cell = counts["cues"].setdefault(c, {}).setdefault(cfg + "|" + v, [0.0, 0.0]); cell[0] += p; cell[1] += 1.0


def observe_arc_outcome(toks: Sequence[str], pos: Sequence[str], j: int, h: int, table: Optional[Dict[str, object]] = None,
                        weight: float = 1.0) -> None:
    """PLASTICITY: one confirmed comprehension outcome -- word j was understood to depend on h -- accrues into the counts (the
    competing candidates of j accrue a zero outcome) and the strengths are recomputed."""
    tab = table or load_attachment_validities(); sc = SentenceCues(toks, pos, tab.get("frames", {}))
    marg = {j: {hh: (weight if hh == h else 0.0) for hh in range(0, sc.n + 1) if hh != j}}
    accrue_sentence(tab["counts"], sc, marg)
    tab["strength"] = strengths_from_arc_counts(tab["counts"])


# ----------------------------------------------------------------------------------------------------------- readout
def arc_scores(toks: Sequence[str], pos: Sequence[str], table: Optional[Dict[str, object]] = None) -> Tuple[np.ndarray, int]:
    """Additive cue activation per arc (row = head incl. 0 = ROOT, col = dependent); form classes never head or root."""
    tab = table or load_attachment_validities(); st = tab["strength"]; sc = SentenceCues(toks, pos, tab.get("frames", {}))
    n = sc.n; A = np.full((n + 1, n + 1), -np.inf)
    words = [j for j in range(1, n + 1) if pos[j - 1] not in FORM]
    for j in range(1, n + 1):
        for h in range(0, n + 1):
            if h == j or (h and pos[h - 1] in FORM):
                continue
            if h == 0 and pos[j - 1] in FORM and words:
                continue
            cfg = sc.config(j, h); s = st["cfg"].get(cfg, 0.0)
            for c, v in sc.cues(j, h).items():
                s += st.get(c, {}).get(cfg + "|" + v, 0.0)
            if CONVENTION_BONUS and h and sc.constr.get((h, j)) == "fw":
                s += CONVENTION_BONUS
            A[h][j] = s
    return A, n


def head_posterior(toks: Sequence[str], pos: Sequence[str], table: Optional[Dict[str, object]] = None,
                   temp: float = 1.0) -> Dict[int, Dict[int, float]]:
    """The graded signal handed DOWN: exact single-root Matrix-Tree marginals P(head | dependent)."""
    A, n = arc_scores(toks, pos, table); return single_root_marginals(A, n, temp)


def heads(toks: Sequence[str], pos: Sequence[str], table: Optional[Dict[str, object]] = None) -> Dict[int, int]:
    """MAP heads (CLE) -- for consumers that insist on a point; prefer head_posterior."""
    A, n = arc_scores(toks, pos, table); return chu_liu_edmonds(A, n)


# ---------------------------------------------------------------------------------------------------------------------------------
# SEMANTIC BOOTSTRAPPING TEACHER (2026-09-12). The knowledge-free co-occurrence teacher learns phrase internals but never that the
# VERB HEADS ITS ARGUMENTS (landed anatomy: obj 0.19, obl 0.12, root 0.41). The brain gets that knowledge from MEANING: the event
# predicate takes its participants as arguments, so the word naming the predicate heads the words naming plausible participants
# (semantic bootstrapping, Pinker 1984/1989 -- PINNED as the acquisition account; Abend, Kwiatkowski, Smith, Goldwater & Steedman
# 2017 as a computational model). MODEL here: plausibility = the typed selectional association organ (Resnik class association; an
# OFFLINE FOUNDATION asset standing in for experiential event knowledge -- its store was extracted with a UD-shaped parse of
# simplewiki, so this teacher is foundation-informed, not knowledge-free; only verb-noun ASSOCIATION is read, never slot position).
# The teacher's arc score for a verb->nominal arc is beta * association, the root score of a verb is beta * its best argument's
# association; everything else is locality. It is combined with the co-occurrence teacher's log-scores as ONE tree posterior
# (beta is a SWEPT operating point: smoke 1.5k/150 -- beta 0: obj 0.08 obl 0.04 root 0.34; beta 2: obj 0.13; beta 5: obj 0.72
# obl 0.44 root 0.83; beta 10: obj 0.76 obl 0.56 root 0.79, UAS 0.540 -- above the prior-informed path it replaces).
class SemanticBootstrapTeacher:
    def __init__(self, beta: float = 10.0, lam: float = 0.3, tsp_asset: Optional[str] = None):
        from hdlab.typed_selectional_preference import get, TypedSelectionalPreference
        # PLAUSIBILITY SOURCE (2026-09-12 late): by default the store GROWN BY THE SUBSTRATE'S OWN CHAIN (induced categories ->
        # attachment arm -> role competition over 60k simplewiki lines; tools/grow_selectional_store_bf.py -> typed asset
        # BF_TSP_ASSET). Measured equal to the August parser-extracted store on the heads rung (smoke UAS 0.5642 vs 0.5640;
        # root 0.793 nsubj 0.719 obj 0.71 obl 0.459 xcomp 0.606) -- so the rung's last non-BF dependency is removed at no
        # cost. Falls back to the organ's default asset only if the self-grown one is absent. tsp_asset overrides.
        path = tsp_asset or (BF_TSP_ASSET if os.path.isfile(BF_TSP_ASSET) else None)
        self.tsp = TypedSelectionalPreference.load(path) if path else get()
        self.tsp_source = os.path.basename(path) if path else "default typed_selectional_preference asset"
        self.beta = float(beta); self.lam = float(lam); self._cache: Dict[Tuple[str, str], float] = {}

    def plausibility(self, verb_tok: str, noun_tok: str) -> float:
        key = (verb_tok.lower(), noun_tok.lower())
        if key not in self._cache:
            v = lemma_verb(verb_tok).lower(); s = None
            try:
                s = self.tsp.score(v, noun_tok.lower()) if self.tsp.covers(v) else None
            except Exception:
                s = None
            self._cache[key] = float(s) if s is not None else 0.0
        return self._cache[key]

    def score_matrix(self, toks: Sequence[str], pos: Sequence[str]) -> Tuple[np.ndarray, int]:
        n = len(toks); A = np.full((n + 1, n + 1), -np.inf); best_arg = np.zeros(n + 1)
        for j in range(1, n + 1):
            for h in range(1, n + 1):
                if h == j or pos[h - 1] in FORM:
                    continue
                sc = -self.lam * math.log(abs(h - j) + 1.0)
                if pos[h - 1] == "VERB" and pos[j - 1] in NOMINAL:
                    p = self.plausibility(toks[h - 1], toks[j - 1]); sc += self.beta * p; best_arg[h] = max(best_arg[h], p)
                A[h][j] = sc
        for j in range(1, n + 1):
            if pos[j - 1] in FORM:
                A[0][j] = -np.inf if any(pos[k] not in FORM for k in range(n)) else 0.0
            else:
                A[0][j] = (self.beta * best_arg[j] if pos[j - 1] == "VERB" else -1.0) - 0.5
        return A, n

    def combined_scores(self, A: np.ndarray, n: int, toks: Sequence[str], pos: Sequence[str]) -> np.ndarray:
        """ONE posterior: the co-occurrence teacher's log-scores A + this teacher's meaning scores (distance counted once)."""
        B, _ = self.score_matrix(toks, pos); C = A.copy()
        for h in range(0, n + 1):
            for j in range(1, n + 1):
                if h != j and np.isfinite(A[h][j]) and np.isfinite(B[h][j]):
                    C[h][j] = A[h][j] + (B[h][j] + self.lam * math.log(abs(h - j) + 1.0) if h else B[h][j])
        return C


__all__ = ["SentenceCues", "CONSTRUCTIONS", "construction_map", "verb_frames_from_reading", "strengths_from_arc_counts",
           "load_attachment_validities", "save_attachment_validities", "new_counts", "accrue_sentence", "observe_arc_outcome",
           "arc_scores", "head_posterior", "heads", "SemanticBootstrapTeacher", "ASSET", "FORM"]
