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
CUES = ["locality", "catpair", "frame", "form", "boundary", "agree", "root", "lex", "plaus", "constr"]
USE_PLAUS = "--plaus" in sys.argv   # MEANING cue: surprisal of the nominal as an argument of the candidate verb (forward-prediction organ)
USE_CONSTR = "--constr" in sys.argv  # CONSTRUCTION coalition cue: which item-based construction (Tomasello) proposes this arc --
                                     # verbarg (Now-or-Never left-corner verb-argument bind), coord, npmod (NP-run head), clausal (pri-2's +0.036 lever)
_CONSTR_CACHE = {}


def construction_arcs(toks, pos):
    """{(h, j): family} for the sentence, from the landed construction detectors (exp_readlearned_construction_stack_v1.CUES)."""
    key = (tuple(toks), tuple(pos))
    if key in _CONSTR_CACHE:
        return _CONSTR_CACHE[key]
    import experiments.exp_readlearned_construction_stack_v1 as CS
    out = {}
    for fam, fn in CS.CUES.items():
        try:
            for (h, d) in fn(list(toks), list(pos)):
                out.setdefault((h, d), fam)
        except Exception:
            pass
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


def arc_cues(toks, pos, j, h, frames):
    """Cue values for the arc h -> j (1-based; h == 0 is ROOT)."""
    pj = pos[j - 1]
    if h == 0:
        return {"root": pj}
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
        for j in range(1, n + 1):
            for h in range(0, n + 1):
                if h == j:
                    continue
                p = marg.get(j, {}).get(h, 0.0)
                cues = arc_cues(toks, pos, j, h, self.frames); cfg = self._config(cues)
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

    def score_matrix(self, toks, pos):
        n = len(toks); A = np.full((n + 1, n + 1), -np.inf)
        for j in range(1, n + 1):
            for h in range(0, n + 1):
                if h == j:
                    continue
                if h and pos[h - 1] in FORM:
                    continue                                      # form classes never head (constraint)
                A[h][j] = self.arc_score(arc_cues(toks, pos, j, h, self.frames))
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
    if "--prior-free-teacher" in sys.argv:
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
    stu = AttachmentCompetition(frames)
    for s in train:
        toks = [x[1] for x in s]; pos = [x[2] for x in s]
        A, n = teacher._score_matrix(toks, pos)
        stu.accrue(toks, pos, single_root_marginals(A, n, 1.0))
    stu.finalize()
    out["student_r0"] = round(uas(stu.parse, test), 4); print("student r0 (taught by the teacher's posterior):", out["student_r0"], flush=True)
    # rounds 1..2: the student re-teaches itself from its OWN posterior (EM over cue strengths)
    ALPHA = float(sys.argv[sys.argv.index("--alpha") + 1]) if "--alpha" in sys.argv else 0.5   # student vs teacher weight in re-estimation
    ROUNDS = int(sys.argv[sys.argv.index("--rounds") + 1]) if "--rounds" in sys.argv else 2
    for r in range(1, ROUNDS + 1):
        nxt = AttachmentCompetition(frames)
        for s in train:
            toks = [x[1] for x in s]; pos = [x[2] for x in s]
            A, n = teacher._score_matrix(toks, pos); mt = single_root_marginals(A, n, 1.0); ms = stu.marginals(toks, pos)
            mix = {j: {h: ALPHA * ms.get(j, {}).get(h, 0.0) + (1 - ALPHA) * mt.get(j, {}).get(h, 0.0) for h in set(ms.get(j, {})) | set(mt.get(j, {}))} for j in range(1, n + 1)}
            nxt.accrue(toks, pos, mix)
        stu = nxt.finalize()
        out["student_r%d" % r] = round(uas(stu.parse, test), 4); print("student r%d (self-taught):" % r, out["student_r%d" % r], flush=True)
        if smoke:
            break
    # twin: shuffle the strength values within each cue
    rng = np.random.default_rng(1)
    for c in list(stu.strength):
        keys = list(stu.strength[c]); vals = [stu.strength[c][k] for k in keys]; rng.shuffle(vals)
        stu.strength[c] = dict(zip(keys, vals))
    out["twin_shuffled_strengths"] = round(uas(stu.parse, test), 4)
    out["elapsed_s"] = round(time.time() - t0, 1); out["smoke"] = smoke
    print(json.dumps(out, indent=1))
    from experiments._seed_checkpoint import get_output_dir
    od = str(get_output_dir("probe_attachment_competition_v18" + ("_priorfree" if "--prior-free-teacher" in sys.argv else "") + ("_plaus" if USE_PLAUS else "") + ("_constr" if USE_CONSTR else "") + (("_a%g_r%d" % (ALPHA, ROUNDS)) if ("--alpha" in sys.argv or "--rounds" in sys.argv) else "") + ("_smoke" if smoke else ""))); os.makedirs(od, exist_ok=True)
    json.dump(out, open(os.path.join(od, "metrics.json"), "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
