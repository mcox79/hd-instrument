"""PROBE v18 (heads rung, first build to the spec in notes/RESEARCH_attachment_organ_spec_2026-09-12.md):
ATTACHMENT AS CUE COMPETITION -- the same structure as the role labeler, applied to "which word heads this word".

For each dependent j and each candidate head h (incl. ROOT): categorical CUE VALUES
    locality   : direction x log-distance bin           (cue-based retrieval decay; Lewis-Vasishth / DLT)
    catpair    : (cat_h, cat_j, dir)                     (distributional attachment tendency)
    frame      : head lemma's recipient/transitivity propensity x dependent class   (lexical frame, learned counts)
    form       : candidate is punctuation / numeral      (cannot head; pre-lexical)
    boundary   : number of punctuation marks the arc spans (prosodic closure)
    agree      : subject-verb number agreement sketch (3sg verb form vs singular/plural nominal)  -- coarse, label-free
    root       : dependent category for the ROOT decision
Strengths = log P(arc is true | cue value) - log P(arc is true) contrasts, LEARNED WITHOUT A TREEBANK by self-supervision: the
OUTCOME for each (j, h) pair is the Matrix-Tree POSTERIOR of the teacher (the cached reading-learned SelfSupEM @ EM r2, itself
treebank-free), i.e. soft counts; then the student's own posterior re-teaches it (EM over the cue strengths). Combination: arc score
= sum of contrasts; exact single-root Matrix-Tree marginals (graded_parser) -> MAP by CLE for UAS only.
Arms (UD-EWT test UAS, gold categories; gold used ONLY as the reference): teacher (cached scorer) plain / +constraints; STUDENT
round 0 (taught by the teacher's posterior) and round 1-2 (self-taught); shuffled-strength twin; adjacent-right floor.
Run: .venv/Scripts/python.exe experiments/probe_attachment_competition_v18.py [--smoke]
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")
import json
import math
import pickle
import sys
import time
from collections import defaultdict

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments.exp_parser_graded_decode_regimes_v1 import load_ud, UD_TRAIN, UD_TEST
from experiments.exp_parser_selfsup_em_v1 import SelfSupEM, _adj_right_uas
from hdlab.graded_parser import single_root_marginals, chu_liu_edmonds
from hdlab.thematic_role_labeler import lemma_verb

TEACHER = os.path.join(_REPO, "data", "_readlearned_models", "em_n11991_r2_lam0.30_pw3.00.pkl")
FORM = {"PUNCT", "NUM", "SYM"}
CUES = ["locality", "catpair", "frame", "form", "boundary", "agree", "root", "lex", "plaus", "constr", "sib"]
FW_FORCE = float(sys.argv[sys.argv.index("--fw-force") + 1]) if "--fw-force" in sys.argv else 0.0   # convention layer bonus at decode
USE_SIB = "--sibling" in sys.argv   # SECOND-ORDER via VALENCE OCCUPANCY (mean-field): the cue includes what the head has already
                                    # attached -- expected number of OTHER dependents of this class on this side under the previous
                                    # pass's posterior (Lewis-Vasishth retrieval cue; sibling factorisation = +13.3 label-free in the field)


def occupancy_table(marg, pos, n):
    """occ[(h, class, side)] = expected number of dependents of `class` on `side` of h under the posterior marg (excl. none)."""
    occ = defaultdict(float)
    for j in range(1, n + 1):
        for h, p in marg.get(j, {}).items():
            if h and p > 0:
                occ[(h, pos[j - 1], "L" if h < j else "R")] += p
    return occ


def sib_value(occ, h, j, pos):
    if occ is None or h == 0:
        return "na"
    dr = "L" if h < j else "R"; pj = pos[j - 1]
    e = occ.get((h, pj, dr), 0.0)
    # remove this arc's own expected contribution if it was counted (mean-field: others only)
    return "occ0" if e < 0.5 else "occ1" if e < 1.5 else "occ2+"
USE_PLAUS = "--plaus" in sys.argv   # MEANING cue: surprisal of the nominal as an argument of the candidate verb (forward-prediction organ)
USE_CONSTR = "--constr" in sys.argv  # CONSTRUCTION coalition cue: which item-based construction (Tomasello) proposes this arc --
                                     # verbarg (Now-or-Never left-corner verb-argument bind), coord, npmod (NP-run head), clausal (pri-2's +0.036 lever)
_CONSTR_CACHE = {}


def construction_arcs(toks, pos):
    """{(h, j): family} for the sentence, from the landed construction detectors (exp_readlearned_construction_stack_v1.CUES)."""
    key = (tuple(toks), tuple(pos))
    if key in _CONSTR_CACHE:
        return _CONSTR_CACHE[key]
    from hdlab.attachment_arm import construction_map as _cm      # the landed organ's constructions (incl. function-word frames)
    out = dict(_cm(list(toks), list(pos)))
    if len(_CONSTR_CACHE) > 20000:
        _CONSTR_CACHE.clear()
    _CONSTR_CACHE[key] = out
    return out
_PRED = None


def _predictor():
    global _PRED
    if _PRED is None:
        from hdlab.composed_hub_predictor import HubComposedPredictor
        _PRED = HubComposedPredictor.load()
    return _PRED


def plaus_bin(toks, pos, j, h):
    """Plausibility of dependent j as an ARGUMENT of verb h: -log P under the forward-prediction organ among the sentence's
    other nominals (the N400 read-out, Altmann-Kamide / McRae thematic fit). Binned; 'none' when the organ abstains."""
    if pos[h - 1] != "VERB" or pos[j - 1] not in ("NOUN", "PRON", "PROPN"):
        return "na"
    P = _predictor(); verb = lemma_verb(toks[h - 1]).lower()
    if not P.has(verb):
        return "none"
    cands = [toks[k - 1].lower() for k in range(1, len(toks) + 1) if k != j and pos[k - 1] in ("NOUN", "PRON", "PROPN")]
    sp = P.surprisal(verb, "PATIENT", toks[j - 1].lower(), cands)
    if sp is None:
        return "none"
    return "low" if sp < 1.0 else "mid" if sp < 2.5 else "high"
USE_LEX = False   # lexical attachment preference: THIS head lemma x dependent category x direction (shrunk toward the catpair config)
                  # smoke @1.5k sentences: r0 0.4386 -> 0.4185, r1 0.4443 -> 0.4292 = too SPARSE at that volume; retest at 60k (probe v20)


def dist_bin(d):
    return "1" if d == 1 else "2" if d == 2 else "3-4" if d <= 4 else "5-8" if d <= 8 else "9+"


def verb_frames(train):
    """Per head-verb lemma: [n_nominal_deps, n_obj-like (post-verbal bare nominal deps)] accrued from the reading; here from the
    training sentences' TOKENS ONLY (no labels): a post-verbal nominal within 3 tokens with no preposition before it."""
    fr = defaultdict(lambda: [0, 0])
    for s in train:
        pos = [t[2] for t in s]; toks = [t[1] for t in s]; n = len(s)
        for v in range(n):
            if pos[v] != "VERB":
                continue
            lem = lemma_verb(toks[v]).lower(); fr[lem][0] += 1
            for j in range(v + 1, min(n, v + 4)):
                if pos[j] in ("NOUN", "PRON", "PROPN") and not (j - 1 > v and pos[j - 1] == "ADP"):
                    fr[lem][1] += 1; break
    return {k: v for k, v in fr.items() if v[0] >= 5}


def arc_cues(toks, pos, j, h, frames, occ=None):
    """Cue values for the arc h -> j (1-based; h == 0 is ROOT)."""
    pj = pos[j - 1]
    if h == 0:
        return {"root": pj}
    sibv = sib_value(occ, h, j, pos) if USE_SIB else None
    ph = pos[h - 1]; dr = "L" if h < j else "R"; d = abs(h - j)
    c = {"locality": f"{dr}{dist_bin(d)}", "catpair": f"{ph}>{pj}:{dr}", "form": "formhead" if ph in FORM else "wordhead"}
    lo, hi = (h, j) if h < j else (j, h)
    nb = sum(1 for k in range(lo + 1, hi) if pos[k - 1] == "PUNCT")
    c["boundary"] = "0" if nb == 0 else "1" if nb == 1 else "2+"
    if USE_LEX:
        lem = lemma_verb(toks[h - 1]).lower() if ph in ("VERB", "AUX") else toks[h - 1].lower()
        c["lex"] = f"{lem}:{pj}:{dr}" if ph in ("VERB", "AUX", "ADP", "NOUN", "ADJ") else "na"
    else:
        c["lex"] = "na"
    c["plaus"] = plaus_bin(toks, pos, j, h) if USE_PLAUS else "na"
    if USE_SIB:
        c["sib"] = sibv
    c["constr"] = construction_arcs(toks, pos).get((h, j), "none") if USE_CONSTR else "na"
    if ph == "VERB":
        fr = frames.get(lemma_verb(toks[h - 1]).lower())
        trans = "unk" if not fr else ("trans" if fr[1] / fr[0] >= 0.3 else "intrans")
        c["frame"] = f"{trans}:{pj}:{dr}"
        # agreement sketch: a present-tense 3sg verb form (ends in -s, not -ss) with a plural/singular pre-verbal nominal
        w = toks[h - 1].lower(); wj = toks[j - 1].lower()
        if dr == "R" and pj in ("NOUN", "PRON", "PROPN") and w.endswith("s") and not w.endswith("ss"):
            c["agree"] = "3sgV:" + ("plurN" if (pj == "NOUN" and wj.endswith("s") and not wj.endswith("ss")) or wj in ("they", "we", "you", "i") else "singN")
        else:
            c["agree"] = "na"
    else:
        c["frame"] = "na"; c["agree"] = "na"
    return c


LEARN_DELTA = float(sys.argv[sys.argv.index("--delta") + 1]) if "--delta" in sys.argv else 0.0   # Smith & Eisner 2006: length penalty in the E-step ONLY
PUNCT_HARD = "--punct-hard" in sys.argv     # Spitkovsky 2011: no arc crosses a punctuation mark during LEARNING (fragments parsed separately)
CURRICULUM = "--curriculum" in sys.argv     # Spitkovsky baby steps: round 0 on short sentences, then longer


def learning_view(A, pos, n):
    """Apply the LEARNING-TIME biases to an arc score matrix (never at decode): -delta * distance on every arc; arcs crossing a
    punctuation mark forbidden when PUNCT_HARD. Returns a modified copy."""
    if not LEARN_DELTA and not PUNCT_HARD:
        return A
    B = A.copy()
    cum = np.concatenate([[0], np.cumsum([1 if p == "PUNCT" else 0 for p in pos])])
    for h in range(1, n + 1):
        for j in range(1, n + 1):
            if h == j or not np.isfinite(B[h][j]):
                continue
            if LEARN_DELTA:
                B[h][j] -= LEARN_DELTA * abs(h - j)
            if PUNCT_HARD:
                lo, hi = (h, j) if h < j else (j, h)
                if cum[hi - 1] - cum[lo] > 0:
                    B[h][j] = -np.inf
    return B


def learn_marginals(score_matrix_fn, toks, pos):
    A, n = score_matrix_fn(toks, pos)
    return single_root_marginals(learning_view(A, pos, n), n, 1.0)


class AttachmentCompetition:
    """Cue strengths learned from SOFT arc counts (posterior-weighted), CONFIGURATION-CONDITIONED like the role labeler:
    the dominant cue (catpair for word heads; root for the root decision) is the configuration; every other cue's strength is
    the CONTRAST log-odds(arc | config, value) - log-odds(arc | config), Dirichlet-shrunk toward the configuration's own
    rate -- so correlated cues (locality, frame, boundary...) do not double-count the configuration's evidence (decorrelation
    before combination; Barlow). A value that always fires within its configuration contributes exactly 0."""

    def __init__(self, frames):
        self.frames = frames
        self.cfg = defaultdict(lambda: [0.0, 0.0])                                  # config -> [soft true, total]
        self.count = {c: defaultdict(lambda: [0.0, 0.0]) for c in CUES}           # "cfg|value" -> [soft true, total]
        self.base = [0.0, 0.0]; self.strength = None

    @staticmethod
    def _config(cues):
        return cues["catpair"] if "catpair" in cues else "ROOT:" + cues["root"]

    def accrue(self, toks, pos, marg):
        n = len(toks)
        occ = occupancy_table(marg, pos, n) if USE_SIB else None
        for j in range(1, n + 1):
            for h in range(0, n + 1):
                if h == j:
                    continue
                p = marg.get(j, {}).get(h, 0.0)
                if occ is not None and h:
                    occ[(h, pos[j - 1], "L" if h < j else "R")] -= p          # others only
                cues = arc_cues(toks, pos, j, h, self.frames, occ); cfg = self._config(cues)
                if occ is not None and h:
                    occ[(h, pos[j - 1], "L" if h < j else "R")] += p
                cell = self.cfg[cfg]; cell[0] += p; cell[1] += 1.0
                for c, v in cues.items():
                    if c in ("catpair", "root"):
                        continue
                    cell = self.count[c][cfg + "|" + v]; cell[0] += p; cell[1] += 1.0
                self.base[0] += p; self.base[1] += 1.0

    @staticmethod
    def _lo(p):
        p = min(max(p, 1e-6), 1 - 1e-6); return math.log(p / (1 - p))

    def finalize(self, m=2.0):
        pb = (self.base[0] + 0.5) / (self.base[1] + 1.0)
        self.strength = {"cfg": {}}; self.pcfg = {}
        for cfg, (t, n) in self.cfg.items():
            p = (t + m * pb) / (n + m); self.pcfg[cfg] = p
            self.strength["cfg"][cfg] = self._lo(p) - self._lo(pb)
        for c, vals in self.count.items():
            if c in ("catpair", "root"):
                continue
            self.strength[c] = {}
            for key, (t, n) in vals.items():
                cfg = key.split("|", 1)[0]; base = self.pcfg.get(cfg, pb)
                if n >= self.cfg[cfg][1]:                      # always fires within the configuration -> no information
                    self.strength[c][key] = 0.0
                else:
                    p = (t + m * base) / (n + m)
                    self.strength[c][key] = self._lo(p) - self._lo(base)
        return self

    def arc_score(self, cues):
        cfg = self._config(cues)
        sc = self.strength["cfg"].get(cfg, 0.0)
        for c, v in cues.items():
            if c in ("catpair", "root"):
                continue
            sc += self.strength.get(c, {}).get(cfg + "|" + v, 0.0)
        return sc

    def score_matrix(self, toks, pos, occ=None):
        n = len(toks); A = np.full((n + 1, n + 1), -np.inf)
        fw = construction_arcs(toks, pos) if FW_FORCE else {}
        for j in range(1, n + 1):
            for h in range(0, n + 1):
                if h == j:
                    continue
                if h and pos[h - 1] in FORM:
                    continue                                      # form classes never head (constraint)
                A[h][j] = self.arc_score(arc_cues(toks, pos, j, h, self.frames, occ))
                if FW_FORCE and fw.get((h, j)) == "fw":
                    A[h][j] += FW_FORCE                       # CONVENTION layer: function-word frames applied at decode (UD metric only)
        if USE_SIB and occ is None:
            # two-pass mean-field: first-pass posterior -> occupancy -> second-pass scores
            occ1 = occupancy_table(single_root_marginals(A, n, 1.0), pos, n)
            return self.score_matrix(toks, pos, occ1)
        return A, n

    def marginals(self, toks, pos):
        A, n = self.score_matrix(toks, pos); return single_root_marginals(A, n, 1.0)

    def parse(self, toks, pos):
        A, n = self.score_matrix(toks, pos); return chu_liu_edmonds(A, n)


def uas(parse_fn, test):
    c = t = 0
    for s in test:
        toks = [x[1] for x in s]; pos = [x[2] for x in s]; gold = {x[0]: x[3] for x in s}
        heads = parse_fn(toks, pos)
        for i in range(1, len(s) + 1):
            g = gold.get(i, -99)
            if 0 <= g <= len(s):
                c += int(heads.get(i, -1) == g); t += 1
    return c / max(1, t)


def main():
    smoke = "--smoke" in sys.argv
    t0 = time.time()
    train = load_ud(UD_TRAIN, cap=1500 if smoke else 6000, maxlen=40)
    test = load_ud(UD_TEST, cap=150 if smoke else 700)
    if "--meaning-teacher" in sys.argv:
        # SEMANTIC BOOTSTRAPPING of the head-direction knowledge the hand prior supplied: the knowledge-free co-occurrence teacher
        # (phrase internals) + the MEANING teacher (probe v21: the event predicate heads its plausible participants) as ONE posterior.
        import experiments.probe_semantic_bootstrap_attachment_v21 as V21
        tr = [[(0, t[1], t[2], 0, "_") for t in s] for s in train]
        base = SelfSupEM(lam=0.3, prior_weight=0.0, lex_weight=0.0).learn_raw(tr)
        for _ in range(2):
            base.em_round(tr)
        meaning = V21.MeaningTeacher(beta=float(sys.argv[sys.argv.index("--beta") + 1]) if "--beta" in sys.argv else 2.0)
        GATE = "--meaning-gate" in sys.argv
        GATED = ("NOUN", "PRON", "PROPN", "VERB")   # the predicate-argument SKELETON: participants + predicates are taught by meaning
        class CombinedTeacher:
            lam = base.lam; prior_weight = 0.0; lex_weight = 0.0
            @staticmethod
            def _col_lognorm(M, n):
                # each dependent's head scores as a log-distribution (same scale for both teachers; the tree posterior renormalises)
                C = M.copy()
                for j in range(1, n + 1):
                    col = M[:, j]; fin = np.isfinite(col)
                    if fin.any():
                        m = col[fin].max(); z = m + math.log(np.exp(col[fin] - m).sum())
                        C[fin, j] = col[fin] - z
                return C
            def _score_matrix(self, toks, pos):
                A, n = base._score_matrix(toks, pos); B, _ = meaning._score_matrix(toks, pos)
                if GATE:
                    # SEMANTIC BOOTSTRAPPING as a GATE, not a bonus: a nominal or verb dependent's head distribution is the MEANING
                    # teacher's (plausible predicate heads its participants; root = the predicate with the most plausible arguments);
                    # every other dependent (phrase internals, function words) keeps the co-occurrence teacher's distribution.
                    An = self._col_lognorm(A, n); Bn = self._col_lognorm(B, n); C = An.copy()
                    for j in range(1, n + 1):
                        if pos[j - 1] in GATED and np.isfinite(Bn[:, j]).any():
                            C[:, j] = Bn[:, j]
                    return C, n
                C = A.copy()
                for h in range(0, n + 1):
                    for j in range(1, n + 1):
                        if h != j and np.isfinite(A[h][j]) and np.isfinite(B[h][j]):
                            C[h][j] = A[h][j] + (B[h][j] + meaning.lam * math.log(abs(h - j) + 1.0) if h else B[h][j])   # meaning bonus without double distance
                return C, n
            def parse_cle(self, toks, pos):
                from hdlab.graded_parser import chu_liu_edmonds
                A, n = self._score_matrix(toks, pos); return chu_liu_edmonds(A, n)
        teacher = CombinedTeacher()
        print("teacher = knowledge-free co-occurrence + MEANING (typed selectional association; predicate heads its participants)", flush=True)
    elif "--prior-free-teacher" in sys.argv:
        # LANDING GATE 1 (spec s7): bootstrap from a PRIOR-FREE learner (categories + locality only; NO hand-authored prior),
        # trained on the same sentences for 2 EM rounds -- no knowledge enters except what the reading provides.
        tr = [[(0, t[1], t[2], 0, "_") for t in s] for s in train]
        teacher = SelfSupEM(lam=0.3, prior_weight=0.0, lex_weight=0.0).learn_raw(tr)
        for _ in range(2):
            teacher.em_round(tr)
        print("teacher = prior-free SelfSupEM trained on the fly (pw=0, 2 EM rounds)", flush=True)
    else:
        teacher = pickle.load(open(TEACHER, "rb"))
    frames = verb_frames(train)
    floor = _adj_right_uas([[(i + 1, "x", p, {x[0]: x[3] for x in s}.get(i + 1, 0), "_") for i, p in enumerate([x[2] for x in s])] for s in test])[0]
    out = {"floor": round(floor, 4), "teacher_plain": round(uas(teacher.parse_cle, test), 4)}
    print("floor", out["floor"], "teacher", out["teacher_plain"], flush=True)
    # round 0: the teacher's posterior is the outcome signal
    if CURRICULUM:
        train = sorted(train, key=len)                       # baby steps: short sentences first
        caps = {0: 10, 1: 20}                                # round 0 <= 10 tokens, round 1 <= 20, then all
    else:
        caps = {}
    def subset(r):
        cap = caps.get(r); return [s for s in train if len(s) <= cap] if cap else train
    stu = AttachmentCompetition(frames)
    for s in subset(0):
        toks = [x[1] for x in s]; pos = [x[2] for x in s]
        stu.accrue(toks, pos, learn_marginals(teacher._score_matrix, toks, pos))
    stu.finalize()
    out["student_r0"] = round(uas(stu.parse, test), 4); print("student r0 (taught by the teacher's posterior):", out["student_r0"], flush=True)
    # rounds 1..2: the student re-teaches itself from its OWN posterior (EM over cue strengths)
    ALPHA = float(sys.argv[sys.argv.index("--alpha") + 1]) if "--alpha" in sys.argv else 0.5   # student vs teacher weight in re-estimation
    ROUNDS = int(sys.argv[sys.argv.index("--rounds") + 1]) if "--rounds" in sys.argv else 2
    for r in range(1, ROUNDS + 1):
        nxt = AttachmentCompetition(frames)
        for s in subset(r):
            toks = [x[1] for x in s]; pos = [x[2] for x in s]; n = len(toks)
            mt = learn_marginals(teacher._score_matrix, toks, pos); ms = learn_marginals(stu.score_matrix, toks, pos)
            mix = {j: {h: ALPHA * ms.get(j, {}).get(h, 0.0) + (1 - ALPHA) * mt.get(j, {}).get(h, 0.0) for h in set(ms.get(j, {})) | set(mt.get(j, {}))} for j in range(1, n + 1)}
            nxt.accrue(toks, pos, mix)
        stu = nxt.finalize()
        out["student_r%d" % r] = round(uas(stu.parse, test), 4); print("student r%d (self-taught):" % r, out["student_r%d" % r], flush=True)
        if smoke:
            break
    # CORE-STRUCTURE readout (the consumers' signal): per-relation accuracy for the comprehension-relevant relations
    rel_tot = {}; rel_hit = {}
    for s in test:
        toks = [x[1] for x in s]; pos = [x[2] for x in s]; hd = stu.parse(toks, pos); n = len(s)
        for x in s:
            rel = x[4].split(":")[0]
            if rel in ("nsubj", "obj", "obl", "nmod", "root", "xcomp", "ccomp", "advcl", "conj", "case", "punct") and 0 <= x[3] <= n:
                rel_tot[rel] = rel_tot.get(rel, 0) + 1; rel_hit[rel] = rel_hit.get(rel, 0) + int(hd.get(x[0], -1) == x[3])
    out["per_relation"] = {r: round(rel_hit[r] / rel_tot[r], 3) for r in rel_tot}
    print("per-relation:", out["per_relation"], flush=True)
    # twin: shuffle the strength values within each cue
    rng = np.random.default_rng(1)
    for c in list(stu.strength):
        keys = list(stu.strength[c]); vals = [stu.strength[c][k] for k in keys]; rng.shuffle(vals)
        stu.strength[c] = dict(zip(keys, vals))
    out["twin_shuffled_strengths"] = round(uas(stu.parse, test), 4)
    out["elapsed_s"] = round(time.time() - t0, 1); out["smoke"] = smoke
    print(json.dumps(out, indent=1))
    from experiments._seed_checkpoint import get_output_dir
    od = str(get_output_dir("probe_attachment_competition_v18" + ("_priorfree" if "--prior-free-teacher" in sys.argv else "") + ("_meaningT" if "--meaning-teacher" in sys.argv else "") + ("_gate" if "--meaning-gate" in sys.argv else "") + ("_plaus" if USE_PLAUS else "") + ("_constr" if USE_CONSTR else "") + (("_a%g_r%d" % (ALPHA, ROUNDS)) if ("--alpha" in sys.argv or "--rounds" in sys.argv) else "") + (("_d%g" % LEARN_DELTA) if LEARN_DELTA else "") + ("_punct" if PUNCT_HARD else "") + ("_curr" if CURRICULUM else "") + ("_sib" if USE_SIB else "") + (("_fwf%g" % FW_FORCE) if FW_FORCE else "") + ("_smoke" if smoke else ""))); os.makedirs(od, exist_ok=True)
    json.dump(out, open(os.path.join(od, "metrics.json"), "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
