"""exp_role_margin_weighted_consumers_v1 -- THE ROLE COMPETITION'S MARGIN, READ BY ITS CONSUMERS.

problem: the_role_competitions_margin_is_a_reliability_signal_0_92_accurate_at_40_percent_coverage_and_no_consumer_reads_it
(priority 106; opened from pri 103 round 2: `coarse_role_posterior` exists, the margin separates right from wrong at
AUC 0.716, and every consumer takes the hard label string.)

HOW THE BRAIN DOES THIS (the opening move -- structure, then computation).
  * STRUCTURE 1, the decision itself: the same evidence-accumulation circuit that makes a choice also carries the
    CONFIDENCE in it. Kiani & Shadlen 2009 (Science 324:759) showed that LIP neurons' accumulated evidence predicts
    both the choice AND the opt-out ("sure target") decision -- confidence is READ OFF THE SAME ACCUMULATOR, not
    computed by a second system. Our accumulator is `graded_role_assigner.net_activation`; the balance of evidence is
    the MARGIN between the top two role activations. So the confidence signal already exists inside the organ.
  * STRUCTURE 2, the consumer: downstream integration is RELIABILITY-WEIGHTED. Ernst & Banks 2002 (Nature 415:429)
    -- the MLE rule w_i proportional to 1/sigma_i^2; Fetsch, Pouget, DeAngelis & Angelaki 2011 (Nat Neurosci 15:146)
    -- MSTd neurons reweight cues TRIAL BY TRIAL with the momentary reliability, not with a long-run average; Ma,
    Beck, Latham & Pouget 2006 -- in a probabilistic population code the POPULATION GAIN *is* the precision, so
    adding populations performs the Bayesian product automatically. A consumer that fuses a role label with salience,
    recency and parallelism must therefore weight the role cue by the reliability of THAT decision.
  * THE MATHEMATICS FOR A CATEGORICAL CUE. A downstream cue here is an INDICATOR on a discrete label:
    1[role(c) = role(anaphor)]. Under label uncertainty the correct quantity is not the indicator but its
    EXPECTATION under the posterior over the true role:
        E[1[role(c) = a_role]] = sum over the roles in a_role's class of P(true role of c = r).
    The organ's softmax P_raw is NOT that posterior (pri 103: marginalising the raw head posterior LOST 0.027 because
    it is mis-centred; the brief's instruction is "calibrate, do not marginalise"). The calibrated form keeps the
    organ's SHAPE among the alternatives and fixes the MAP mass to the empirically measured reliability:
        Pcal(MAP)   = r(margin)                                              [the count-calibrated reliability]
        Pcal(other) = (1 - r(margin)) * P_raw(other) / (1 - P_raw(MAP))      [shape preserved, mass corrected]
    r(margin) is a pure function of COUNTS: margin bin -> [n_correct, n_total], add-alpha smoothed toward the base
    rate and made monotone by pool-adjacent-violators. That is the "monotone count-calibrated map" the brief's
    checklist item 1 asks for, and it has an online `observe` path (every comprehension outcome accrues one count).
  * WHY NOT A THRESHOLD. A defer threshold is a hand-set number (and the brief bars adopting one). The fusion form
    needs none: a low-reliability role label simply contributes a small cue activation and the other cues win.

WHAT IS MEASURED (consumers, each on its own population, floor = the hard label, paired bootstrap CIs).
  C1 AFFECTED ENTITY (GUM, `hdlab.affected_entity_resolver`): the Kehler-Rohde fusion
     ln p_salience + gamma_g*1[gram-role match] + gamma_t*1[candidate is PATIENT] -- already a fusion, and the only
     unweighted cues in it are the two ROLE cues. Arms: HARD (today) / RELWEIGHT (gamma * r) / EXPECTED (gamma * Pcal)
     / RAWPOST (gamma * P_raw -- the control that isolates CALIBRATION from gradedness) / TWIN (margins shuffled
     across items, so the reliability carries no per-decision information).
  C2 THE CHAIN'S AGENT READ (UD-EWT test, the board's who_did_what_agent population): a Competition-Model fusion of
     the WORD-ORDER cue (validity learned from train counts) with the role competition's calibrated agent posterior
     and the governor's own P(head = the verb). Floor = the positional nearest-preverbal pick.
  C3 NO-REGRESS: the organ patch is OPT-IN (rel_of=None reproduces the landed arithmetic byte for byte); the cell
     asserts that identity, so every other consumer (state register, harm/help, patient) is unchanged by construction.

FULL-STACK UPSTREAM: the affected-entity arms are measured under the LIVE BF CHAIN (hdlab.frontend: count-based
category organ -> attachment arm -> role competition) AND under GOLD heads/categories, and the gap is reported --
the margin is only as good as the heads.

NO gold at inference (gold scores only, and builds the calibration counts on the TRAIN split). No spaCy / nltk /
supervised parser / external LLM at inference. Glass-box. ASCII.
Run: .venv/Scripts/python.exe experiments/exp_role_margin_weighted_consumers_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_role_margin_weighted_consumers_v1.py --run
"""
from __future__ import annotations

import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
os.environ.setdefault("PYTHONHASHSEED", "0")

import argparse
import json
import pickle
import random
import time
from collections import defaultdict

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments._seed_checkpoint import get_output_dir
import hdlab.graded_role_assigner as GRA
from hdlab import frontend as FE

ANCHOR = "role_margin_weighted_consumers_v1"
OUT_DIR = str(get_output_dir(ANCHOR))
SEED = 20260914
UD_TRAIN = os.path.join(REPO, "data", "corpora", "ud_english_ewt", "en_ewt-ud-train.conllu")
UD_TEST = os.path.join(REPO, "data", "corpora", "ud_english_ewt", "en_ewt-ud-test.conllu")
HOOK_DIR = os.path.join(REPO, "data", "hook_state")
RELIABILITY_ASSET = os.path.join(HOOK_DIR, "role_margin_reliability_v1.json")

# ---------------------------------------------------------------------------------------------------------------
# 1. THE RELIABILITY MAP -- margin bin -> [n_correct, n_total], a pure function of counts, with an observe path.
# ---------------------------------------------------------------------------------------------------------------
BIN_WIDTH = 0.05          # SWEPT (0.02 / 0.05 / 0.10 / 0.20); the phase-diagram parameter of this map
ALPHA = 4.0               # add-alpha pseudo-counts pulling a thin bin toward the base rate (SWEPT 1 / 4 / 16)


def margin_of(p) -> float:
    """The balance of evidence the organ's own accumulator carries: top-1 minus top-2 of the role softmax."""
    q = np.sort(np.asarray(p, dtype=float))
    return float(q[-1] - q[-2]) if len(q) >= 2 else 1.0


def _bin(margin: float, width: float) -> int:
    return int(min(0.999999, max(0.0, float(margin))) / width)


class Reliability:
    """r(margin) = P(the MAP role label is right | this margin), from COUNTS. Monotone by construction after the
    pool-adjacent-violators pass (the reliability of a decision cannot fall as the evidence balance grows -- the
    accumulator account; Kiani & Shadlen 2009). Plastic: `observe(margin, correct)` accrues one outcome."""

    def __init__(self, counts=None, width: float = BIN_WIDTH, alpha: float = ALPHA):
        self.width = float(width)
        self.alpha = float(alpha)
        self.counts = {int(k): [float(v[0]), float(v[1])] for k, v in (counts or {}).items()}
        self._t = None

    def observe(self, margin: float, correct) -> None:
        b = _bin(margin, self.width)
        c = self.counts.setdefault(b, [0.0, 0.0])
        c[0] += float(bool(correct)); c[1] += 1.0
        self._t = None

    @property
    def base(self) -> float:
        tot = sum(c[1] for c in self.counts.values())
        return (sum(c[0] for c in self.counts.values()) / tot) if tot else 0.5

    def table(self):
        """bin -> smoothed accuracy, then a pool-adjacent-violators (isotonic) pass so r is non-decreasing."""
        base = self.base
        bs = sorted(self.counts)
        raw = [((self.counts[b][0] + self.alpha * base) / (self.counts[b][1] + self.alpha)) for b in bs]
        w = [self.counts[b][1] + self.alpha for b in bs]
        vals, wts, idx = [], [], []
        for v, ww, b in zip(raw, w, bs):
            vals.append(v); wts.append(ww); idx.append([b])
            while len(vals) > 1 and vals[-2] > vals[-1]:
                v2 = (vals[-2] * wts[-2] + vals[-1] * wts[-1]) / (wts[-2] + wts[-1])
                w2 = wts[-2] + wts[-1]; i2 = idx[-2] + idx[-1]
                vals[-2:] = [v2]; wts[-2:] = [w2]; idx[-2:] = [i2]
        out = {}
        for v, group in zip(vals, idx):
            for b in group:
                out[b] = float(v)
        return out

    def r(self, margin: float) -> float:
        if self._t is None:
            self._t = self.table()
        t = self._t
        if not t:
            return 1.0
        b = _bin(margin, self.width)
        if b in t:
            return t[b]
        ks = sorted(t)
        return t[ks[0]] if b < ks[0] else t[ks[-1]]

    def to_json(self):
        return {"width": self.width, "alpha": self.alpha, "base": round(self.base, 6),
                "counts": {str(k): [round(v[0], 3), round(v[1], 3)] for k, v in sorted(self.counts.items())},
                "table": {str(k): round(v, 6) for k, v in sorted(self.table().items())}}

    @classmethod
    def from_json(cls, d):
        return cls(counts={int(k): v for k, v in d["counts"].items()}, width=d["width"], alpha=d.get("alpha", ALPHA))


def recalibrated(p_raw, rel):
    """Pcal -- the organ's posterior with its MAP mass replaced by the count-calibrated reliability, the SHAPE of the
    alternatives preserved (calibrate, do not marginalise). Returns (Pcal, MAP index, margin)."""
    p = np.asarray(p_raw, dtype=float)
    k = int(np.argmax(p)); m = margin_of(p)
    r = rel.r(m)
    out = np.array(p, dtype=float)
    rest = 1.0 - float(p[k])
    if rest <= 1e-12:
        out[:] = (1.0 - r) / max(1, len(p) - 1)
    else:
        out *= (1.0 - r) / rest
    out[k] = r
    return out, k, m


# ---------------------------------------------------------------------------------------------------------------
# 2. THE CHAIN. One pass of tokens -> categories -> heads -> role posteriors, cached per corpus.
# ---------------------------------------------------------------------------------------------------------------
def _conllu(path):
    toks, pos, heads, deps = [], [], {}, {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                if toks:
                    yield toks, pos, heads, deps
                toks, pos, heads, deps = [], [], {}, {}
                continue
            if line.startswith("#"):
                continue
            c = line.split("\t")
            if "-" in c[0] or "." in c[0]:
                continue
            i = int(c[0]); toks.append(c[1]); pos.append(c[3]); heads[i] = int(c[6]); deps[i] = c[7]
    if toks:
        yield toks, pos, heads, deps


_VAL = None


def validities():
    global _VAL
    if _VAL is None:
        _VAL = GRA.load_coarse_validities()
    return _VAL


def chain_sentence(forms, gold_pos=None, gold_heads=None):
    """tokens -> (categories, heads, MAP role dep per index, role posterior per index, P(head) per index).
    gold_pos / gold_heads substitute the corresponding rung (the full-stack-upstream contrast)."""
    tab = validities()
    if gold_pos is None:
        pos, post = FE.tagger().tag_with_posterior(list(forms))
    else:
        pos, post = list(gold_pos), None
    if gold_heads is None:
        po = FE.parser().parse(list(forms), pos, post)
        heads, marg = dict(po.heads), (po.marginals or {})
    else:
        heads, marg = dict(gold_heads), {}
    conf = {i: float((marg.get(i) or {}).get(heads.get(i, 0), 1.0)) for i in heads} if marg else None
    roles = GRA.coarse_roles(list(forms), pos, heads, tab, conf=conf)
    postr, hconf = {}, {}
    for i in roles:
        postr[i] = np.asarray(GRA.coarse_role_posterior(list(forms), pos, heads, i, tab, conf), dtype=float)
        hconf[i] = float((marg.get(i) or {}).get(heads.get(i, 0), 1.0)) if marg else 1.0
    return pos, heads, roles, postr, hconf


# ---------------------------------------------------------------------------------------------------------------
# 3. BUILD THE RELIABILITY COUNTS on UD-EWT TRAIN (the same split, the same perception, as the cue validities).
# ---------------------------------------------------------------------------------------------------------------
def build_reliability(cap=None, width=BIN_WIDTH, alpha=ALPHA, gold_heads=False, verbose=True):
    """Accrue [n_correct, n_total] per margin bin from the organ's own decisions on TRAIN. The outcome is the
    comprehension outcome (the train split's relation), exactly the signal `observe_role_outcome` already takes;
    online this is one `observe` call per understood argument. No gold is read at inference anywhere.

    THREE maps, because RELIABILITY IS A PROPERTY OF THE DECISION THE CONSUMER READS, not of the organ's private
    label alphabet. A downstream area learns how reliable ITS input is (Fetsch 2011: the reweighting is learned on
    the discriminandum the area itself computes), and the affected-entity resolver never reads the 8-way role --
    it reads the coarse SUBJ/OBJ/OTHER parallelism class and the PATIENT flag, on which several 8-way confusions
    (OBJ<->OBL, SUBJ<->PASS_SUBJ) are HARMLESS. Calibrating on the 8-way label therefore under-reports the
    reliability of the cue the consumer actually uses:
        role8      -- the organ's own label is exactly right          (the organ's private reliability)
        aer_class  -- AER.role_class(label) is right                  (the parallelism cue's reliability)
        patient    -- the PATIENT flag is right                       (the thematic cue's reliability)
    """
    import tools.build_coarse_role_validities as B
    import itertools
    maps = {k: Reliability(width=width, alpha=alpha) for k in ("role8", "aer_class", "patient", "match")}
    n = 0; t0 = time.time()
    for si, (toks, gpos, gheads, gdeps) in enumerate(_conllu(UD_TRAIN)):
        if cap and si >= cap:
            break
        pos, heads, roles, postr, _hc = chain_sentence(toks, gold_heads=gheads if gold_heads else None)
        pairs = []
        for i, dep in roles.items():
            gold = B.coarse_of(gdeps.get(i))
            gdep = GRA.ROLE_TO_DEP[gold]
            k = int(np.argmax(postr[i]))
            pred = GRA.ROLE_CLASSES[k]; pdep = GRA.ROLE_TO_DEP[pred]
            m = margin_of(postr[i])
            maps["role8"].observe(m, pred == gold)
            maps["aer_class"].observe(m, AER.role_class(pdep) == AER.role_class(gdep))
            maps["patient"].observe(m, (pdep in AER.PATIENT_DEPS) == (gdep in AER.PATIENT_DEPS))
            pairs.append((AER.role_class(pdep), AER.role_class(gdep), m))
            n += 1
        # THE MATCH MAP. A PARALLELISM consumer never asks "is this label right?" -- it asks "do these two labels
        # AGREE?", and the organ's errors are SYSTEMATIC, so they partly CANCEL in an agreement test (measured:
        # label class 0.803, match 0.748, but only 0.658 if the two errors were independent -- a +0.090 excess).
        # Reliability must therefore be calibrated on the MATCH event, keyed by the WEAKER of the two decisions.
        for a, b in itertools.combinations(pairs, 2):
            maps["match"].observe(min(a[2], b[2]), (a[0] == b[0]) == (a[1] == b[1]))
        if verbose and si and si % 1000 == 0:
            print("  [reliability] %d sents %d decisions %.0fs" % (si, n, time.time() - t0), flush=True)
    if verbose:
        print("  [reliability] DONE %d decisions base role8=%.4f class=%.4f patient=%.4f match=%.4f %.0fs"
              % (n, maps["role8"].base, maps["aer_class"].base, maps["patient"].base, maps["match"].base,
                 time.time() - t0), flush=True)
    return maps


_MAP_KEYS = ("role8", "aer_class", "patient", "match")


def load_or_build_reliability(cap=None, width=BIN_WIDTH, alpha=ALPHA, rebuild=False, verbose=True):
    """The three margin->reliability maps, from the asset when it matches, else rebuilt from TRAIN and written."""
    if not rebuild and os.path.exists(RELIABILITY_ASSET):
        d = json.load(open(RELIABILITY_ASSET, encoding="utf-8"))
        if abs(d.get("width", 0) - width) < 1e-9 and all(k in d.get("maps", {}) for k in _MAP_KEYS):
            return {k: Reliability(counts={int(b): v for b, v in d["maps"][k]["counts"].items()},
                                   width=width, alpha=alpha) for k in _MAP_KEYS}
    maps = build_reliability(cap=cap, width=width, alpha=alpha, verbose=verbose)
    os.makedirs(HOOK_DIR, exist_ok=True)
    doc = {"width": width, "alpha": alpha, "cue_set": validities().get("cue_set"),
           "maps": {k: maps[k].to_json() for k in _MAP_KEYS},
           "source": ("P(the Competition-Model role decision is right | its margin), accrued from the organ's own "
                      "decisions while reading UD-EWT train perceived by the live chain (hdlab.frontend: category "
                      "organ -> attachment arm -> graded_role_assigner). COUNTS ONLY; r = add-alpha smoothed "
                      "accuracy per margin bin, made monotone by pool-adjacent-violators. THREE maps because "
                      "reliability belongs to the decision the CONSUMER reads: role8 = the organ's 8-way label, "
                      "aer_class = the SUBJ/OBJ/OTHER parallelism class, patient = the PATIENT flag. Online path: "
                      "graded_role_assigner.observe_margin_outcome (one call per understood argument).")}
    json.dump(doc, open(RELIABILITY_ASSET, "w", encoding="utf-8"), indent=1)
    return maps


def reliability_curve(rel, margins, correct):
    """The defer curve + AUC of the margin as a reliability signal on an EVALUATION population (pri 103's instrument)."""
    m = np.asarray(margins, dtype=float); c = np.asarray(correct, dtype=float)
    order = np.argsort(-m)
    cur = []
    for cov in (0.2, 0.4, 0.6, 0.8, 1.0):
        k = max(1, int(round(cov * len(m))))
        cur.append([cov, round(float(c[order[:k]].mean()), 4)])
    pos = m[c > 0.5]; neg = m[c <= 0.5]
    if len(pos) and len(neg):
        rk = np.argsort(np.argsort(np.concatenate([pos, neg]))) + 1.0
        auc = float((rk[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2.0) / (len(pos) * len(neg)))
    else:
        auc = float("nan")
    ece = 0.0; tot = len(m)
    for b in sorted(set(_bin(x, rel.width) for x in m)):
        sel = np.array([_bin(x, rel.width) == b for x in m])
        if sel.sum() == 0:
            continue
        ece += (sel.sum() / tot) * abs(float(c[sel].mean()) - rel.r(b * rel.width + rel.width / 2))
    return {"n": int(len(m)), "base": round(float(c.mean()), 4), "auc": round(auc, 4),
            "defer_curve": cur, "calibration_error": round(float(ece), 4)}


# ---------------------------------------------------------------------------------------------------------------
# 4. CONSUMER 1 -- THE AFFECTED-ENTITY RESOLVER (GUM). The Kehler-Rohde fusion, with the role cues weighted by the
#    reliability of the label that produced them. The scoring below is EXACTLY the arithmetic the proposed organ
#    patch adds to hdlab/affected_entity_resolver.score_and_pick (rel_of / pcal_of); mode="hard" is byte-identical
#    to the landed organ and is asserted against it in the self-test.
# ---------------------------------------------------------------------------------------------------------------
import hdlab.affected_entity_resolver as AER
from hdlab.salience_binder import actr_activation, ROLE_PROMINENCE, DEFAULT_DECAY

# ROLE_CLASSES -> the resolver's coarse parallelism class / PATIENT flag, via the organ's own vocabulary
_CLASS_OF = [AER.role_class(GRA.ROLE_TO_DEP[r]) for r in GRA.ROLE_CLASSES]
_PATIENT_OF = [GRA.ROLE_TO_DEP[r] in AER.PATIENT_DEPS for r in GRA.ROLE_CLASSES]

PAR_CLASSES = ("SUBJ", "OBJ", "OTHER")           # the resolver's parallelism alphabet (AER.role_class)


def _pack(pvec, margin):
    """One role decision, reduced to what the CONSUMER reads: the mass of each parallelism class, the PATIENT mass,
    the MAP class / MAP patient flag, and the margin that carries the confidence."""
    p = np.asarray(pvec, dtype=float)
    cm = {c: float(sum(x for x, cc in zip(p, _CLASS_OF) if cc == c)) for c in PAR_CLASSES}
    pm = float(sum(x for x, f in zip(p, _PATIENT_OF) if f))
    k = int(np.argmax(p))
    return {"class_mass": cm, "patient_mass": pm, "map_class": _CLASS_OF[k], "map_patient": bool(_PATIENT_OF[k]),
            "margin": float(margin)}


def _cal_binary(p_map_event, r):
    """Calibrated probability of a binary event whose MAP reading is `p_map_event` (True/False) at reliability r."""
    return float(r) if p_map_event else float(1.0 - r)


def _cal_class(pk, want, r):
    """Calibrated P(true parallelism class = `want`): the MAP class takes the count-calibrated mass r, the remaining
    1-r is distributed over the other classes in the SHAPE the organ's own posterior gives them (calibrate, do not
    marginalise -- pri 103 showed the raw mass itself is mis-centred)."""
    cm, mc = pk["class_mass"], pk["map_class"]
    if want == mc:
        return float(r)
    rest = sum(v for c, v in cm.items() if c != mc)
    return float((1.0 - r) * (cm.get(want, 0.0) / rest)) if rest > 1e-12 else float((1.0 - r) / (len(PAR_CLASSES) - 1))


def _llr(r, k):
    """The EXACT log-likelihood-ratio an observed categorical label of reliability r carries over k alternatives:
    log P(label | true = label) - log P(label | true != label) = log( r (k-1) / (1-r) ). This is the Ernst-Banks
    weight in the discrete case -- the amount of evidence, not merely a shrinkage factor."""
    r = min(max(float(r), 1e-6), 1.0 - 1e-6)
    return float(np.log(r * (k - 1) / (1.0 - r)))


CLASS_PRIOR = None          # the organ's own role prior, collapsed to the consumer's class alphabet (lazy)


def _class_prior():
    """P(class) from the validity table's role prior -- the belief a consumer falls back on when the role decision
    is unreliable (Ma-Beck-Latham-Pouget: an unreliable population leaves the posterior at the prior)."""
    global CLASS_PRIOR
    if CLASS_PRIOR is None:
        pr = np.exp(np.asarray(validities()["prior"], dtype=float))
        pr = pr / max(1e-12, pr.sum())
        CLASS_PRIOR = {c: float(sum(x for x, cc in zip(pr, _CLASS_OF) if cc == c)) for c in PAR_CLASSES}
        CLASS_PRIOR["_patient"] = float(sum(x for x, f in zip(pr, _PATIENT_OF) if f))
    return CLASS_PRIOR


def cue_terms(pk, a_role, a_pk, *, mode="hard", rc=1.0, rp=1.0, a_rc=1.0, norm_g=1.0, norm_t=1.0, rm=1.0):
    """The two ROLE cues of the Kehler-Rohde fusion, in the form the arm under test uses. Returns
    (parallelism_cue, thematic_cue); the resolver then adds gamma_g * cue_g + gamma_t * cue_t to the salience term.
      hard       1[MAP class matches]                                  the LANDED indicator (the FLOOR)
      relweight  r * 1[MAP class matches]                              reliability as a gain on the indicator
      logodds    LLR(r)/norm * 1[MAP class matches]                    the EXACT categorical evidence weight
      expected   Pcal(class = a_role)                                  the expectation of the indicator
      expboth    sum_c Pcal_cand(c) * Pcal_anaphor(c)                  both ends of the match are uncertain
      rawpost    P_raw(class = a_role)                                 graded, NO reliability (isolates the margin)
      shrunk     r * P_raw(class) + (1-r) * prior(class)               precision-weighted shrinkage to the prior
      ppc        (r/rbar) * log P_raw(class)                           population-GAIN form (Ma et al. 2006)
    """
    if pk is None:
        return (1.0 if a_role == "OTHER" else 0.0), 0.0
    if mode in ("hard", "oracle"):
        return float(pk["map_class"] == a_role), float(pk["map_patient"])
    if mode == "oracle_gate":
        g = float(pk.get("_gate", 1.0))
        return g * float(pk["map_class"] == a_role), g * float(pk["map_patient"])
    if mode == "relweight":
        return rc * float(pk["map_class"] == a_role), rp * float(pk["map_patient"])
    if mode == "logodds":
        return ((_llr(rc, len(PAR_CLASSES)) / norm_g) * float(pk["map_class"] == a_role),
                (_llr(rp, 2) / norm_t) * float(pk["map_patient"]))
    if mode == "rawpost":
        return pk["class_mass"].get(a_role, 0.0), pk["patient_mass"]
    if mode == "match":
        # THE RIGHT STATISTIC FOR A PARALLELISM CUE: P(the two labels really AGREE), calibrated on the MATCH event
        # and keyed by the WEAKER of the two decisions' margins. A wrong label is not noise here -- a correlated
        # wrong label still agrees, which is why gating on LABEL reliability measured WORSE than doing nothing.
        pm = float(pk["map_class"] == a_role)
        return (rm * pm + (1.0 - rm) * (1.0 - pm)), rp * float(pk["map_patient"]) + (1.0 - rp) * (1.0 - float(pk["map_patient"]))
    if mode == "shrunk":
        pri = _class_prior()
        return (rc * pk["class_mass"].get(a_role, 0.0) + (1.0 - rc) * pri.get(a_role, 0.33),
                rp * pk["patient_mass"] + (1.0 - rp) * pri["_patient"])
    if mode == "logpost":
        # THE SAME LOG-PROBABILITY FUSION WITH THE GAIN HELD AT 1 -- the control that isolates how much of the
        # ppc arm is the RELIABILITY gain and how much is simply reading the posterior in LOG form.
        return (float(np.log(max(pk["class_mass"].get(a_role, 0.0), 1e-4))),
                float(np.log(max(pk["patient_mass"], 1e-4))))
    if mode == "ppc":
        g_g = rc / max(1e-9, norm_g); g_t = rp / max(1e-9, norm_t)
        return (g_g * float(np.log(max(pk["class_mass"].get(a_role, 0.0), 1e-4))),
                g_t * float(np.log(max(pk["patient_mass"], 1e-4))))
    if mode == "expboth" and a_pk is not None:
        acc = sum(_cal_class(pk, c, rc) * _cal_class(a_pk, c, a_rc) for c in PAR_CLASSES)
        return acc, _cal_binary(pk["map_patient"], rp)
    return _cal_class(pk, a_role, rc), _cal_binary(pk["map_patient"], rp)


MODES = ("hard", "relweight", "logodds", "expected", "expboth", "rawpost", "shrunk", "ppc", "logpost", "match")
CEILING_MODES = ("oracle", "oracle_gate")      # the arithmetic bound: a PERFECT role label in the same fusion


def _load_gum(limit=None, split="test"):
    """GUM documents with the live mention stream. split='test' = the board's odd-index split (every reported
    number); split='dev' = the complementary even-index split, where the fusion weights are SWEPT."""
    import experiments.exp_affected_entity_salience_prior_gum_v1 as B1
    import experiments.exp_hybrid_unified_incumbent_coref_gum_v1 as HYB
    import experiments.gum_coref as GC
    if split == "test":
        docs = B1._load_test(limit)
    else:
        try:
            import experiments.exp_name_entity_clustering_v1 as NEC
            gaz = NEC.load_given_gazetteer()
        except Exception:
            gaz = None
        docs = [d for i, d in enumerate(GC.load_docs(gum_only=True, name_gazetteer=gaz, limit=limit)) if i % 2 == 0]
    out = []
    for doc in docs:
        mlive = HYB.gum_to_live(doc)
        for i, m in enumerate(mlive):
            m.setdefault("order", i)
        out.append((doc, mlive))
    return out


def _chain_overlay(data, *, gold_pos=False, gold_heads=False, cache_path=None, verbose=True):
    """Replace every GUM token's head/deprel with the BF CHAIN's (categories -> heads -> role competition), and
    return {id(doc): {gidx: (posterior, margin, head_conf)}}. Gold rungs can be substituted to expose the
    full-stack-upstream gap. The gold trees are NEVER read by the chain -- only as the substituted rung."""
    if cache_path and os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            cached = pickle.load(f)
    else:
        cached = None
    out = {}
    t0 = time.time(); ns = 0
    fresh = {}
    for doc, _m in data:
        by_sent = defaultdict(list)
        for tok in doc.toks:
            by_sent[tok.sent].append(tok)
        info = {}
        for sent, toks in by_sent.items():
            toks = sorted(toks, key=lambda x: x.idx)
            forms = [x.form for x in toks]
            key = (doc.docid if hasattr(doc, "docid") else id(doc), sent)
            key = "%s|%s" % (key[0], key[1])
            if cached is not None and key in cached:
                pos, heads, roles, postr, hconf = cached[key]
            else:
                gp = [getattr(x, "upos", "X") or "X" for x in toks] if gold_pos else None
                gh = {j + 1: x.head for j, x in enumerate(toks)} if gold_heads else None
                pos, heads, roles, postr, hconf = chain_sentence(forms, gold_pos=gp, gold_heads=gh)
                ns += 1
            fresh[key] = (pos, heads, roles, postr, hconf)
            for j, x in enumerate(toks):
                i1 = j + 1
                x.head = heads.get(i1, x.head)
                x.deprel = roles.get(i1) or "dep"
                if i1 in postr:
                    info[x.gidx] = (postr[i1], margin_of(postr[i1]), hconf.get(i1, 1.0))
            if verbose and ns and ns % 1500 == 0:
                print("  [chain] %d sentences %.0fs" % (ns, time.time() - t0), flush=True)
        out[id(doc)] = info
    if cache_path and ns:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, "wb") as f:
            pickle.dump(fresh, f, protocol=4)
    if verbose:
        print("  [chain] %d sentences parsed %.0fs" % (ns, time.time() - t0), flush=True)
    return out



class RelTokens(AER.EntityTokens):
    """The landed EntityTokens organ with ONE change: the grammatical-parallelism cues enter the fusion weighted by
    the RELIABILITY of the role decision that produced them (Ernst-Banks; Fetsch 2011 trial-by-trial reweighting).
    Every other line -- ACT-R activation, accrual/impletion, the foreground window, Principle A/B -- is the organ's.
    mode="hard" restores the landed arithmetic exactly (asserted in the self-test)."""

    def __init__(self, *a, mode="hard", gamma_g=AER.GAMMA_G, gamma_t=AER.GAMMA_T, norm_g=1.0, norm_t=1.0,
                 sal_norm=False, rel_match=None, **kw):
        super().__init__(*a, gamma_g=gamma_g, gamma_t=gamma_t, **kw)
        self.mode = mode
        self.sal_norm = bool(sal_norm)
        self.rel_match = rel_match
        self.norm_g, self.norm_t = float(norm_g), float(norm_t)
        self.info = {}                      # (key, order) -> (pack, r_class, r_patient)

    def note(self, key, order, pack, rc, rp):
        self.info[(key, float(order))] = (pack, float(rc), float(rp))

    def resolve_pronoun(self, order, sent, *, gender=None, number=None, a_role="OBJ", role="OTHER",
                        coarg_key=None, reflexive=False, accrue=None, a_pk=None, a_rc=1.0):
        compat = self.candidates(gender, number)
        ents = list(compat)
        if not ents:
            return None, 0
        if reflexive and coarg_key is not None and coarg_key in ents:
            pick, margin = coarg_key, 1.0
        else:
            legal = AER.legal_candidates(ents, coarg_key)
            legal = AER.foreground(legal, self.last_ref_sent, float(sent), self.window)
            sal, cg, ct = [], [], []
            for k in legal:
                hist = [(m[0], m[1]) for m in compat[k]]
                if self.accrue if accrue is None else accrue:
                    hist = hist + list(self.pron_hist.get(k, ()))
                a = actr_activation(hist, float(order), decay=self.decay, role_prominence=ROLE_PROMINENCE)
                sal.append(a if a != float("-inf") else -1e9)
                last = max(compat[k], key=lambda m: m[0])
                pk, rc, rp = self.info.get((k, float(last[0])), (None, 1.0, 1.0))
                rm = self.rel_match.r(min(pk["margin"], a_pk["margin"] if a_pk else 1.0)) if (
                    self.rel_match is not None and pk is not None) else 1.0
                g, t = cue_terms(pk, a_role, a_pk, mode=self.mode, rc=rc, rp=rp, a_rc=a_rc,
                                 norm_g=self.norm_g, norm_t=self.norm_t, rm=rm)
                cg.append(g); ct.append(t)
            sv = np.asarray(sal, dtype=float)
            if self.sal_norm:
                # PRODUCT OF EXPERTS: the salience cue enters as a log-POSTERIOR over the candidate set, not as a raw
                # ACT-R activation, so both cues live on the log-probability scale and a reliability weight has a
                # defined meaning (the substrate's convergent_cue_reader form; Ernst-Banks is an MLE over CALIBRATED
                # likelihoods -- fusing a calibrated cue with an unnormalised one is the checklist's item-4 trap).
                z = sv - sv.max()
                sv = z - np.log(np.exp(z).sum())
            tot = sv + self.gamma_g * np.asarray(cg, dtype=float) + self.gamma_t * np.asarray(ct, dtype=float)
            j = int(np.argmax(tot))
            pick = legal[j] if legal else None
            o = np.sort(tot)
            margin = float(o[-1] - o[-2]) if len(o) >= 2 else 1.0
        if pick is not None:
            self.pron_hist.setdefault(pick, []).append((float(order), role))
            self.last_ref_sent[pick] = float(sent)
        return pick, len(ents)


def run_affected_arm(data, info_by_doc, maps, *, mode="hard", gamma_g=AER.GAMMA_G, gamma_t=AER.GAMMA_T,
                     window=2, decay=DEFAULT_DECAY, targets=None, shuffle_margins=False, rng=None,
                     norm_g=1.0, norm_t=1.0, sal_norm=False, oracle_by_doc=None):
    """One configuration over every THIRD-person gold undergoer pronoun. Returns [(hit, form, r_class, margin)].
    Mirrors experiments.exp_affected_entity_token_history_gum_v1.run_arm (accrual + foreground + Principle A), with
    the reliability-weighted fusion substituted for the indicator cue. TWIN = the per-token MARGINS permuted inside
    each document, so the reliabilities are still a valid population but carry no per-decision information."""
    import experiments.exp_affected_entity_salience_prior_gum_v1 as B1
    import experiments.exp_affected_entity_token_history_gum_v1 as TH
    rel_c, rel_p = maps["aer_class"], maps["patient"]
    results = []
    for doc, mlive in data:
        info = info_by_doc.get(id(doc), {})
        packs = {}
        gidxs = list(info)
        margins = [info[g][1] for g in gidxs]
        if shuffle_margins:
            margins = list(margins); rng.shuffle(margins)
        orc = (oracle_by_doc or {}).get(id(doc), {})
        for g, mg in zip(gidxs, margins):
            pk = _pack(info[g][0], mg)
            if mode in ("oracle", "oracle_gate") and g in orc:
                if mode == "oracle":
                    pk = dict(pk); pk["map_class"], pk["map_patient"] = orc[g][0], bool(orc[g][1])
                    pk["class_mass"] = {c: float(c == pk["map_class"]) for c in PAR_CLASSES}
                    pk["patient_mass"] = float(pk["map_patient"])
                else:
                    # THE CEILING OF THE WHOLE RELIABILITY FAMILY: a PERFECT confidence gate. It cannot supply the
                    # right label -- only switch the cue OFF when the label is wrong, which is exactly the most any
                    # reliability weighting can do. The gap between this and the ORACLE arm is the part of the
                    # headroom no confidence signal can reach.
                    pk = dict(pk); pk["_gate"] = float(pk["map_class"] == orc[g][0])
            packs[g] = (pk, rel_c.r(mg), rel_p.r(mg))
        head_to_mi = {doc.mentions[i].head_g: i for i in range(len(doc.mentions))}
        mi2headg = {i: doc.mentions[i].head_g for i in range(len(doc.mentions))}
        gidx2dep = {t.gidx: t.deprel for t in doc.toks}
        gidx2tok = {t.gidx: t for t in doc.toks}
        und = {}
        tset = targets.get(id(doc)) if targets is not None else None
        for t in doc.toks:
            is_target = (t.gidx in tset) if tset is not None else (t.deprel in B1.UND_DEPRELS)
            if is_target and t.gidx in head_to_mi and doc.mentions[head_to_mi[t.gidx]].mtype == "pronoun":
                und[head_to_mi[t.gidx]] = t
        T = RelTokens(window=window, decay=decay, accrue=True, mode=mode, gamma_g=gamma_g, gamma_t=gamma_t,
                      norm_g=norm_g, norm_t=norm_t, sal_norm=sal_norm, rel_match=maps.get("match"))
        for mi, m in enumerate(mlive):
            M = doc.mentions[mi]
            hg = mi2headg.get(mi); tk = gidx2tok.get(hg)
            t_sent = float(tk.sent if tk is not None else 0)
            tclock = float(m["order"])
            role = TH.ROLE_OF_RANK.get(m.get("sent_role_rank", 99), "OTHER")
            is_pron = m["is_pronoun"] or (M.mtype == "pronoun" and TH.is_third(M.text))
            pk, rc, rp = packs.get(hg, (None, 1.0, 1.0))
            if not is_pron:
                T.observe(m["head"], tclock, role, t_sent, m.get("gender") or m.get("name_gender"), m.get("number"),
                          gidx2dep.get(hg, ""), payload=m)
                T.note(m["head"], tclock, pk, rc, rp)
                continue
            ug, un = m.get("gender"), m.get("number")
            coarg = None
            if mi in und:
                cg = AER.coarg_head_gidx(doc.toks, und[mi])
                if cg is not None and cg in head_to_mi and not mlive[head_to_mi[cg]]["is_pronoun"]:
                    coarg = mlive[head_to_mi[cg]]["head"]
            dep = gidx2dep.get(hg, "")
            a_role = AER.role_class(dep) if dep else "OBJ"
            reflexive = M.text.lower() in TH.REFLEXIVE
            pick, n_c = T.resolve_pronoun(tclock, t_sent, gender=ug, number=un, a_role=a_role, role=role,
                                          coarg_key=coarg, reflexive=reflexive, a_pk=pk, a_rc=rc)
            if mi in und and TH.is_third(M.text):
                cm = [x for x in mlive if x["midx"] < mi and not x["is_pronoun"] and B1._gn_ok(m, x)]
                if len(cm) >= 2 and len(set(x["head"] for x in cm)) >= 2:
                    lm = T.last_mention(pick, ug, un) if pick is not None else None
                    hit = int(lm is not None and lm[6] is not None and lm[6]["cluster"] == M.eid)
                    results.append((hit, M.text.lower(), float(rc), float(pk["margin"]) if pk else 1.0))
    return results

def _paired(base_vec, vec, n_boot=2000, seed=SEED):
    b = np.asarray(base_vec, dtype=float); v = np.asarray(vec, dtype=float)
    assert len(b) == len(v), (len(b), len(v))
    d = v - b
    rng = np.random.default_rng(seed); n = len(d)
    boots = np.array([d[rng.integers(0, n, n)].mean() for _ in range(n_boot)])
    lo, hi = float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))
    return {"acc": round(float(v.mean()), 4), "delta": round(float(d.mean()), 4),
            "ci95": [round(lo, 4), round(hi, 4)], "ci_hw": round((hi - lo) / 2, 4),
            "ci_sep": bool(lo > 0 or hi < 0)}


def gold_classes(data):
    """{id(doc): {gidx: (parallelism class, is PATIENT)}} from the GOLD deprels, captured BEFORE the chain overlay --
    used ONLY by the ORACLE arm, which bounds by arithmetic what ANY improvement to the role cue can buy here."""
    out = {}
    for doc, _m in data:
        out[id(doc)] = {t.gidx: (AER.role_class(t.deprel), t.deprel in AER.PATIENT_DEPS) for t in doc.toks}
    return out


def gold_targets(data):
    import experiments.exp_affected_entity_salience_prior_gum_v1 as B1
    return {id(doc): {t.gidx for t in doc.toks if t.deprel in B1.UND_DEPRELS} for doc, _m in data}




# ---------------------------------------------------------------------------------------------------------------
# 5. THE FUSION-WEIGHT SWEEP. Every reliability form CHANGES THE SCALE of the parallelism cue (r < 1 shrinks it,
#    the log-odds form stretches it), so comparing them at the landed gamma=1.0 measures a gain change, not a
#    reliability effect. The brief's phase-diagram note makes the fusion weights free to sweep: gamma is swept for
#    EVERY arm INCLUDING the hard floor, on the GUM DEV split, and the winner of each is reported on TEST. The
#    strongest floor is therefore the BEST hard-label configuration, not the incumbent's operating point.
# ---------------------------------------------------------------------------------------------------------------
GAMMA_GRID = (0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0)
GAMMA_GRID_POE = (0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 4.0)   # the normalised-salience scale is different; swept apart


def _norms(maps):
    """The mean log-odds weight over the reliability range, so the log-odds arm enters at the same AVERAGE gain as
    the hard indicator and only its VARIATION across decisions can move the result."""
    rc = maps["aer_class"]; rp = maps["patient"]
    tc = rc.table(); tp = rp.table()
    wc = [(_llr(v, len(PAR_CLASSES)), rc.counts[b][1]) for b, v in tc.items()]
    wp = [(_llr(v, 2), rp.counts[b][1]) for b, v in tp.items()]
    ng = sum(w * n for w, n in wc) / max(1e-9, sum(n for _w, n in wc))
    nt = sum(w * n for w, n in wp) / max(1e-9, sum(n for _w, n in wp))
    return float(ng), float(nt)


def _acc(res):
    return float(np.mean([h for h, _f, _r, _m in res])) if res else float("nan")


def sweep_affected(maps, *, limit=None, modes=MODES, sal_norms=(False, True), verbose=True):
    """Sweep the fusion weight gamma (and the salience form) on the GUM DEV split for EVERY arm including the hard
    floor; return {arm: {best_gamma, sal_norm, dev_acc, grid}}. Nothing is selected on the test split."""
    data = _load_gum(limit, split="dev")
    targets = gold_targets(data)
    info = _chain_overlay(data, cache_path=os.path.join(OUT_DIR, "gum_chain_dev.pkl"), verbose=verbose)
    ng, nt = _norms(maps)
    best = {}
    for sn in sal_norms:
        for mode in modes:
            name = mode + ("_poe" if sn else "")
            rows = []
            for g in (GAMMA_GRID_POE if sn else GAMMA_GRID):
                a = _acc(run_affected_arm(data, info, maps, mode=mode, gamma_g=g, gamma_t=g, targets=targets,
                                          norm_g=ng, norm_t=nt, sal_norm=sn))
                rows.append((round(g, 3), round(a, 4)))
            bg, ba = max(rows, key=lambda r: (r[1], -r[0]))
            best[name] = {"best_gamma": bg, "sal_norm": bool(sn), "mode": mode, "dev_acc": ba, "grid": rows}
            if verbose:
                print("  [dev] %-14s best gamma %.2f acc %.4f   %s" % (name, bg, ba, rows), flush=True)
    return best


def consumer_affected_entity(maps, *, limit=None, n_boot=2000, gold_pos=False, gold_heads=False,
                             sweep=None, verbose=True, ceilings=True):
    """C1: the affected-entity resolver on GUM TEST, every arm on the SAME fixed gold target set, under the BF chain.
    `sweep` = the dev-selected gamma per mode (None -> the landed gamma 1.0 for every arm)."""
    data = _load_gum(limit, split="test")
    targets = gold_targets(data)                                   # from the GOLD deprels, BEFORE the overlay
    gold_classes_cache = gold_classes(data) if ceilings else None  # ditto; read ONLY by the CEILING arms
    cache = os.path.join(OUT_DIR, "gum_chain_test%s%s.pkl" % ("_gp" if gold_pos else "", "_gh" if gold_heads else ""))
    info = _chain_overlay(data, gold_pos=gold_pos, gold_heads=gold_heads, cache_path=cache, verbose=verbose)
    ng, nt = _norms(maps)
    rng = random.Random(SEED)

    def gam(mode):
        return (sweep or {}).get(mode, {}).get("best_gamma", 1.0)

    incumbent = run_affected_arm(data, info, maps, mode="hard", gamma_g=1.0, gamma_t=1.0, targets=targets)
    ivec = np.array([h for h, _f, _r, _m in incumbent], dtype=float)
    floor = run_affected_arm(data, info, maps, mode="hard", gamma_g=gam("hard"), gamma_t=gam("hard"), targets=targets)
    fvec = np.array([h for h, _f, _r, _m in floor], dtype=float)
    out = {"n": int(len(fvec)), "gold_pos": gold_pos, "gold_heads": gold_heads,
           "incumbent_hard_gamma1": round(float(ivec.mean()), 4),
           "strongest_floor_hard_swept": round(float(fvec.mean()), 4), "floor_gamma": gam("hard"),
           "llr_norms": [round(ng, 4), round(nt, 4)]}
    arms = {}
    for mode in [m for m in MODES if m != "hard"]:
        g = gam(mode)
        res = run_affected_arm(data, info, maps, mode=mode, gamma_g=g, gamma_t=g, targets=targets,
                               norm_g=ng, norm_t=nt)
        v = [h for h, _f, _r, _m in res]
        arms[mode] = {"gamma": g, "vs_strongest_floor": _paired(fvec, v, n_boot=n_boot),
                      "vs_incumbent": _paired(ivec, v, n_boot=n_boot),
                      "flips_vs_floor": int(np.sum(np.asarray(v, float) != fvec))}
    # CEILINGS (gold read ONLY to bound the lever, never in a shipped arm):
    #   oracle      = a PERFECT role label in the same fusion -> what ANY improvement to the role cue can buy
    #   oracle_gate = a PERFECT confidence gate (cue off exactly when the label is wrong) -> the ceiling of the
    #                 whole RELIABILITY family, which can only switch a cue off, never supply the right class
    gc = gold_classes_cache if gold_classes_cache is not None else None
    if gc is not None:
        for mode in CEILING_MODES:
            best_c = None
            for g in GAMMA_GRID:
                res = run_affected_arm(data, info, maps, mode=mode, gamma_g=g, gamma_t=g, targets=targets,
                                       oracle_by_doc=gc)
                v = [h for h, _f, _r, _m in res]
                if best_c is None or np.mean(v) > np.mean(best_c[1]):
                    best_c = (g, v)
            arms["CEILING_" + mode] = {"gamma": best_c[0], "vs_strongest_floor": _paired(fvec, best_c[1], n_boot=n_boot),
                                       "vs_incumbent": _paired(ivec, best_c[1], n_boot=n_boot)}
    bestmode = max([m for m in arms if not m.startswith("CEILING")],
                   key=lambda m: arms[m]["vs_strongest_floor"]["acc"])
    # TWIN 1: the MARGINS permuted across tokens -- destroys the RELIABILITY signal, keeps the posterior.
    tw = run_affected_arm(data, info, maps, mode=bestmode, gamma_g=gam(bestmode), gamma_t=gam(bestmode),
                          targets=targets, norm_g=ng, norm_t=nt, shuffle_margins=True, rng=rng)
    arms["TWIN_margins_shuffled"] = {"of_mode": bestmode,
                                     "vs_strongest_floor": _paired(fvec, [h for h, _f, _r, _m in tw], n_boot=n_boot),
                                     "vs_incumbent": _paired(ivec, [h for h, _f, _r, _m in tw], n_boot=n_boot)}
    # TWIN 2: the whole POSTERIOR permuted across tokens -- info-free for the graded cue as well.
    rng2 = random.Random(SEED + 1)
    info_sh = {}
    for did, inf in info.items():
        ks = list(inf); vs = [inf[k] for k in ks]; rng2.shuffle(vs)
        info_sh[did] = {k: vs[j] for j, k in enumerate(ks)}
    tw2 = run_affected_arm(data, info_sh, maps, mode=bestmode, gamma_g=gam(bestmode), gamma_t=gam(bestmode),
                           targets=targets, norm_g=ng, norm_t=nt)
    arms["TWIN_posteriors_shuffled"] = {"of_mode": bestmode,
                                        "vs_strongest_floor": _paired(fvec, [h for h, _f, _r, _m in tw2], n_boot=n_boot),
                                        "vs_incumbent": _paired(ivec, [h for h, _f, _r, _m in tw2], n_boot=n_boot)}
    out["arms"] = arms
    out["best_mode"] = bestmode
    out["mean_reliability_class"] = round(float(np.mean([r for _h, _f, r, _m in floor])), 4)
    return out


# ---------------------------------------------------------------------------------------------------------------
# 6. CONSUMER 2 -- THE CHAIN'S AGENT READ (UD-EWT test; the board's who_did_what_agent population).
#    Today the board's agent dimension is an ISLAND (word-order default + marked-cue override) and the live chain
#    ties the positional floor. The Competition Model says word order is itself a CUE with a learned validity, so
#    the brain-faithful read is a FUSION of three cues, each entering at its own reliability:
#       A(i) = log P_order(agent | rank of i relative to the verb, voice)          [word-order cue, train counts]
#            + w_role * log Pcal(role(i) = the agent role)                          [the role competition, calibrated]
#            + w_gov  * log P(head(i) = this verb)                                  [the governor's own marginal]
#    w_role = 0 recovers the positional floor. The margin enters through Pcal -- an unreliable role decision
#    contributes a flat log-probability and the order cue decides.
# ---------------------------------------------------------------------------------------------------------------
def _order_cue_counts(cap=None, verbose=True):
    """P(this nominal is the agent | its rank among the clause's nominals relative to the verb, voice) -- the
    WORD-ORDER cue's validity, learned by counting on UD-EWT TRAIN exactly as the other cue validities are."""
    import experiments.exp_board_agent_slot_ud_v1 as AG
    from experiments.exp_whodidwhat_ud_structural_v1 import load_ud
    tg = FE.tagger()
    sents = load_ud(os.path.join(REPO, "data", "corpora", "ud_english_ewt", "en_ewt-ud-train.conllu"))
    if cap:
        sents = sents[:cap]
    items = AG.gold_agent_items(sents)
    cnt = defaultdict(lambda: [0.0, 0.0])
    t0 = time.time()
    for si, (toks, v, ag, passive) in enumerate(items):
        up = tg.tag(list(toks))
        cands = AG._clause_local_nominals(toks, up, v)
        if not cands:
            continue
        pre = [c for c in cands if c["wtok_start"] < v - 1]
        post = [c for c in cands if c["wtok_start"] > v - 1]
        for c in cands:
            i0 = c["wtok_start"]
            if i0 < v - 1:
                rank = len([x for x in pre if x["wtok_start"] > i0])       # 0 = nearest preverbal
                key = ("pre", min(rank, 3), bool(passive))
            else:
                rank = len([x for x in post if x["wtok_start"] < i0])
                key = ("post", min(rank, 3), bool(passive))
            k = "%s|%d|%d" % key
            cnt[k][1] += 1.0
            cnt[k][0] += float(i0 == ag - 1)
        if verbose and si and si % 5000 == 0:
            print("  [order-cue] %d items %.0fs" % (si, time.time() - t0), flush=True)
    return {k: [round(v0, 2), round(v1, 2)] for k, (v0, v1) in cnt.items()}


def _order_key(toks, up, v, i0, cands, passive):
    pre = [c for c in cands if c["wtok_start"] < v - 1]
    post = [c for c in cands if c["wtok_start"] > v - 1]
    if i0 < v - 1:
        rank = len([x for x in pre if x["wtok_start"] > i0]); side = "pre"
    else:
        rank = len([x for x in post if x["wtok_start"] < i0]); side = "post"
    return "%s|%d|%d" % (side, min(rank, 3), int(bool(passive)))


def _agent_role_prob(pk, want_role, maps):
    """P(this nominal really bears the AGENT role) from the role competition, CALIBRATED by its own margin: the MAP
    role takes the count-measured reliability r(margin), the rest keeps the organ's shape. This is the quantity the
    marked-cue override should be betting on, and today nothing reads it."""
    p = np.asarray(pk, dtype=float)
    k = int(np.argmax(p)); m = margin_of(p)
    r = maps["role8"].r(m)
    w = GRA.ROLE_CLASSES.index(want_role)
    if k == w:
        return float(r), m
    rest = 1.0 - float(p[k])
    return (float((1.0 - r) * float(p[w]) / rest) if rest > 1e-12
            else float((1.0 - r) / (len(GRA.ROLE_CLASSES) - 1))), m


def consumer_chain_agent(maps, order_counts=None, *, cap=None,
                         w_roles=(0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 6.0, 1e9), bias=None,
                         n_boot=2000, verbose=True, shuffle_margins=False, seed=SEED, split="test",
                         return_rows=False):
    """C2: the board's who-did-what AGENT population (UD-EWT test, gold nsubj / obl:agent), with the role
    competition's CONFIDENCE deciding whether the marked-cue override is taken.

    THE STRUCTURE. The board's agent arm keeps the high-validity WORD-ORDER default and overrides it when a marked
    cue fires (passive / PP-governed / non-nominative). That override is UNCONDITIONAL today: it fires whether the
    competition is sure or guessing, and the board shows it 0.0197 BELOW the positional floor. The brain does not
    let an unreliable decision overturn a high-validity default -- an override is a cue like any other and enters at
    its reliability (Ernst-Banks; Fetsch 2011). So:
        take the override  iff  w_role * [ log P_agent(override cand) - log P_agent(positional cand) ] > 0
    with P_agent the calibrated agent probability above. w_role = 0 keeps the positional default always (the FLOOR);
    w_role -> inf is the landed unconditional override. Nothing else changes.
    """
    import experiments.exp_board_agent_slot_ud_v1 as AG
    from experiments.exp_whodidwhat_ud_structural_v1 import load_ud
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    from hdlab.thematic_role_labeler import is_passive_clause as _is_passive
    tab = validities()
    gaz = load_given_gazetteer()
    sents = load_ud(UD_TRAIN if split == "train" else UD_TEST)
    if cap:
        sents = sents[:cap]
    items = AG.gold_agent_items(sents)
    rng = random.Random(seed)
    cache = {}
    rows = []
    t0 = time.time()
    _rowcache = os.path.join(OUT_DIR, "agent_rows_%s%s.pkl" % (split, ("_cap%d" % cap) if cap else ""))
    if os.path.exists(_rowcache):
        with open(_rowcache, "rb") as _f:
            rows = pickle.load(_f)
        items = []
    for si, (toks, v, ag, passive_gold) in enumerate(items):
        key = tuple(toks)
        if key not in cache:
            forms = list(toks)
            pos, tpost = FE.tagger().tag_with_posterior(forms)
            po = FE.parser().parse(forms, pos, tpost)
            heads, marg = dict(po.heads), (po.marginals or {})
            conf = {i: float((marg.get(i) or {}).get(heads.get(i, 0), 1.0)) for i in heads} if marg else None
            postr = {i: np.asarray(GRA.coarse_role_posterior(forms, pos, heads, i, tab, conf), dtype=float)
                     for i in range(1, len(forms) + 1)
                     if i - 1 < len(pos) and GRA.is_arg_head(forms, pos, i)}
            cache[key] = (pos, tpost, heads, marg, postr)
        pos, tpost, heads, marg, postr = cache[key]
        cands = AG._clause_local_nominals(toks, pos, v, post=tpost)
        if not cands:
            continue
        cf = [c for c in cands if str(c["head"]).lower() not in GRA._AGENT_ANIM_PRON
              or str(c["head"]).lower() in GRA.NOMINATIVE_PRON]
        cm_cands = cf or cands
        gold = toks[ag - 1]
        base_i = AG._floor_positional_idx(v, cands)
        base = toks[base_i] if base_i is not None else None
        cm = GRA.agent_competition_pick(toks, pos, v - 1, cm_cands, cluster_freq=None, gaz=gaz)
        hyb = AG.hybrid_agent_pick(toks, pos, v, cands, cm_cands, gaz)
        marked = (hyb != base)
        want_role = "BY_AGENT" if _is_passive(toks, pos) else "SUBJ"
        # the two competing candidates' calibrated agent probabilities
        def prob_of(head_str):
            if head_str is None:
                return 1e-6, 0.0
            for c in cands:
                if str(c["head"]).lower() == str(head_str).lower():
                    pk = postr.get(c["wtok_start"] + 1)
                    if pk is None:
                        return 1.0 / len(GRA.ROLE_CLASSES), 0.0
                    return _agent_role_prob(pk, want_role, maps)
            return 1.0 / len(GRA.ROLE_CLASSES), 0.0
        p_base, m_base = prob_of(base)
        p_cm, m_cm = prob_of(cm)

        def order_lp(head_str):
            """log P(agent | this nominal's rank relative to the verb) -- the WORD-ORDER cue's own learned validity,
            the thing the override has to beat. Counts from UD-EWT train (tools-free, this cell's _order_cue_counts)."""
            if not order_counts or head_str is None:
                return 0.0
            for c in cands:
                if str(c["head"]).lower() == str(head_str).lower():
                    ok = order_counts.get(_order_key(toks, pos, v, c["wtok_start"], cands,
                                                     want_role == "BY_AGENT"), [0.0, 0.0])
                    return float(np.log(max((ok[0] + 0.25) / (ok[1] + 1.0), 1e-4)))
            return float(np.log(1e-4))
        rows.append({"gold": gold, "base": base, "cm": cm, "hyb": hyb, "marked": bool(marked),
                     "lp_base": float(np.log(max(p_base, 1e-6))), "lp_cm": float(np.log(max(p_cm, 1e-6))),
                     "lo_base": order_lp(base), "lo_cm": order_lp(cm),
                     "m_base": m_base, "m_cm": m_cm, "sent": key})
        if verbose and si and si % 2000 == 0:
            print("  [agent] %d items %.0fs" % (si, time.time() - t0), flush=True)
    if rows and not os.path.exists(_rowcache):
        os.makedirs(OUT_DIR, exist_ok=True)
        with open(_rowcache, "wb") as _f:
            pickle.dump(rows, _f, protocol=4)
    if shuffle_margins:                       # TWIN: the confidences are permuted across items
        perm = list(range(len(rows))); rng.shuffle(perm)
        for r, j in zip(rows, perm):
            r["lp_base"], r["lp_cm"] = rows[j]["lp_base"], rows[j]["lp_cm"]

    bias_v = 0.0 if bias is None else float(bias)

    def score(arm, wr=0.0):
        hits = []
        for r in rows:
            if arm == "floor":
                pick = r["base"]
            elif arm == "hybrid":
                pick = r["hyb"]
            elif arm == "cm":
                pick = r["cm"]
            else:                                    # reliability-gated override
                # TWO CUES, EACH AT ITS VALIDITY: the marked-cue override is taken only when the role
                # competition's calibrated evidence for it OUTWEIGHS the word-order cue's evidence for the
                # positional default. w_role = 0 never overrides (the floor); w_role -> inf always does (landed).
                # THE OVERRIDE'S OWN VALIDITY IS THE BIAS. A marked cue proposing to overturn the word-order
                # default is a cue with a learned validity like any other: on UD-EWT TRAIN the override is right
                # only a minority of the times it is decisive, so the default carries prior odds the override must
                # OVERCOME. bias = log odds P(override right | it is decisive), learned from train counts; the
                # confidence difference is the per-decision evidence added to it (Ernst-Banks in log-odds form).
                fuse = bias_v + wr * (r["lp_cm"] - r["lp_base"]) + (r["lo_cm"] - r["lo_base"])
                pick = r["hyb"] if (r["marked"] and fuse > 0) else r["base"]
            hits.append(int(AG._match(pick, r["gold"])))
        return np.asarray(hits, dtype=float)

    fl = score("floor"); hy = score("hybrid"); cmv = score("cm")
    out = {"n": len(rows), "n_marked": int(sum(r["marked"] for r in rows)),
           "floor_positional": round(float(fl.mean()), 4),
           "landed_hybrid": round(float(hy.mean()), 4),
           "full_competition": round(float(cmv.mean()), 4),
           "hybrid_vs_floor": _paired(fl, hy, n_boot=n_boot), "grid": {}}
    best = None
    for wr in w_roles:
        v = score("gated", wr)
        out["grid"]["w_role=%.2f" % wr] = round(float(v.mean()), 4)
        if best is None or v.mean() > best[1].mean():
            best = (wr, v)
    # WHAT A PERFECT GATE COULD BUY: among the marked items, how many overrides FIX the positional pick and how
    # many BREAK it -- the arithmetic bound on any confidence gate, and the population the margin must rank.
    W = L = 0; gate_lab, gate_sig = [], []
    for r in rows:
        if not r["marked"]:
            continue
        fo = AG._match(r["base"], r["gold"]); ho = AG._match(r["hyb"], r["gold"])
        W += int(ho and not fo); L += int(fo and not ho)
        if ho != fo:
            gate_lab.append(int(ho)); gate_sig.append(r["lp_cm"] - r["lp_base"])
    auc = float("nan")
    if gate_lab and 0 < sum(gate_lab) < len(gate_lab):
        pos_ = [x for x, y in zip(gate_sig, gate_lab) if y]; neg_ = [x for x, y in zip(gate_sig, gate_lab) if not y]
        rk = np.argsort(np.argsort(np.asarray(pos_ + neg_))) + 1.0
        auc = float((rk[:len(pos_)].sum() - len(pos_) * (len(pos_) + 1) / 2.0) / (len(pos_) * len(neg_)))
    out["override_anatomy"] = {"n_marked": out["n_marked"], "override_fixes": W, "override_breaks": L,
                               "perfect_gate_acc": round(float(fl.mean() + W / max(1, len(rows))), 4),
                               "margin_auc_on_override_outcome": round(auc, 4) if auc == auc else None,
                               "n_decisive": len(gate_lab)}
    out["best"] = {"w_role": best[0], "bias": bias_v, "acc": round(float(best[1].mean()), 4),
                   "vs_floor": _paired(fl, best[1], n_boot=n_boot),
                   "vs_landed_hybrid": _paired(hy, best[1], n_boot=n_boot)}
    if return_rows:
        out["_rows"] = rows
        out["_score"] = score
    return out


def fit_agent_gate(maps, order_counts, *, cap=None, verbose=True):
    """Fit the override gate on UD-EWT TRAIN (never on the evaluation split): the BIAS is the log odds that a
    marked-cue override is right when it is decisive -- a count, like every other cue validity -- and w_role is
    swept over the train items. Returns (bias, w_role, train grid)."""
    import experiments.exp_board_agent_slot_ud_v1 as AG
    tr = consumer_chain_agent(maps, order_counts, cap=cap, split="train", n_boot=200, verbose=verbose,
                              return_rows=True)
    rows = tr["_rows"]
    W = L = 0
    for r in rows:
        if not r["marked"]:
            continue
        fo = AG._match(r["base"], r["gold"]); ho = AG._match(r["hyb"], r["gold"])
        W += int(ho and not fo); L += int(fo and not ho)
    a = 1.0
    pr = (W + a) / (W + L + 2 * a)
    bias = float(np.log(pr / (1.0 - pr)))
    grid = {}
    best = None
    for wr in (0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 6.0, 1e9):
        v = tr["_score"]("gated", wr) if False else None
        grid[wr] = None
    # rescore on the train rows with the fitted bias
    tr2 = consumer_chain_agent(maps, order_counts, cap=cap, split="train", n_boot=200, verbose=False, bias=bias,
                               return_rows=False)
    for k, v in tr2["grid"].items():
        grid[k] = v
        wr = float(k.split("=")[1])
        if best is None or v > best[1]:
            best = (wr, v)
    return {"bias": round(bias, 4), "override_fixes_train": W, "override_breaks_train": L,
            "prior_override_right": round(pr, 4), "w_role": best[0], "train_acc": best[1],
            "train_floor": tr2["floor_positional"], "train_landed_hybrid": tr2["landed_hybrid"], "grid": grid}


# ---------------------------------------------------------------------------------------------------------------
# 7. THE SIGNAL-LOSS LEDGER -- where, chain by chain, the reliability signal the end read needs is lost.
# ---------------------------------------------------------------------------------------------------------------
def signal_trace(maps, cap=300):
    """For the ONE signal the end read needs -- 'how much should I trust this role label?' -- walk every hand-off
    and count what is PRODUCED, what the next rung READS, and what is LOST."""
    import tools.build_coarse_role_validities as B
    rel8, relc, relp = maps["role8"], maps["aer_class"], maps["patient"]
    n = 0
    prod = {"tag_posterior": 0, "head_marginal": 0, "role_posterior": 0}
    read = {"role_label_string": 0}
    mg, corr8, corrc, corrp = [], [], [], []
    hconf = []
    for si, (toks, gpos, gheads, gdeps) in enumerate(_conllu(UD_TEST)):
        if cap and si >= cap:
            break
        forms = list(toks)
        pos, post = FE.tagger().tag_with_posterior(forms)
        po = FE.parser().parse(forms, pos, post)
        heads, marg = dict(po.heads), (po.marginals or {})
        conf = {i: float((marg.get(i) or {}).get(heads.get(i, 0), 1.0)) for i in heads} if marg else None
        tab = validities()
        roles = GRA.coarse_roles(forms, pos, heads, tab, conf=conf)
        for i, dep in roles.items():
            n += 1
            prod["tag_posterior"] += int(bool(post))
            prod["head_marginal"] += int(bool(marg.get(i)))
            p = np.asarray(GRA.coarse_role_posterior(forms, pos, heads, i, tab, conf), dtype=float)
            prod["role_posterior"] += 1
            read["role_label_string"] += 1
            gold = B.coarse_of(gdeps.get(i)); gdep = GRA.ROLE_TO_DEP[gold]
            k = int(np.argmax(p)); pdep = GRA.ROLE_TO_DEP[GRA.ROLE_CLASSES[k]]
            mg.append(margin_of(p))
            corr8.append(int(GRA.ROLE_CLASSES[k] == gold))
            corrc.append(int(AER.role_class(pdep) == AER.role_class(gdep)))
            corrp.append(int((pdep in AER.PATIENT_DEPS) == (gdep in AER.PATIENT_DEPS)))
            hconf.append(float((marg.get(i) or {}).get(heads.get(i, 0), 1.0)))
    out = {"n_decisions": n, "produced": prod, "read_by_consumers_today": read,
           "role8": reliability_curve(rel8, mg, corr8),
           "aer_class": reliability_curve(relc, mg, corrc),
           "patient": reliability_curve(relp, mg, corrp)}
    hc = np.asarray(hconf); m = np.asarray(mg)
    out["head_confidence"] = {"mean_P_map_head": round(float(hc.mean()), 4),
                              "corr_headconf_rolemargin": round(float(np.corrcoef(hc, m)[0, 1]), 4)}
    return out


# ---------------------------------------------------------------------------------------------------------------
# 8. DRIVER
# ---------------------------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------------------------
# 9. THE WIRE PRICE (strategy integration step, 2026-09-14). The board never scores the reader's affected-entity
#    output, so the largest effect in this record is board-INVISIBLE and needs its own instrument arm.
#    `situation_reader._read_affected_entity` fed the resolver rank2dep = {0:'nsubj', 1:'obj'} -- the first nominal
#    of the sentence is the subject, the second the object -- i.e. the raw WORD-ORDER proxy, so the
#    Competition-Model role organ's decision never reached this consumer at all (landed != live). Three arms on the
#    SAME population and the SAME fixed GOLD targets, differing ONLY in what the role cue is fed:
#      A  the reader's own rank proxy          (what runs today)
#      B  the role competition's LABEL          (what the patch supplies to the cue)
#      C  the role competition's DECISION       (the cue reads the posterior; the ppc form)
# ---------------------------------------------------------------------------------------------------------------
RANK2DEP = {0: "nsubj", 1: "obj"}          # the reader's own positional proxy, verbatim from situation_reader


def wire_price(maps, *, limit=None, n_boot=2000, splits=("dev", "test"), verbose=True):
    """Price the reader-wire repair on the affected-entity read. Returns {split: {arms, paired CIs}}."""
    out = {}
    ng, nt = _norms(maps)
    for split in splits:
        data = _load_gum(limit, split=split)
        targets = gold_targets(data)                      # from the GOLD deprels, BEFORE any overlay
        info = _chain_overlay(data, cache_path=os.path.join(OUT_DIR, "gum_chain_%s.pkl" % split), verbose=verbose)
        chain_dep = {id(doc): {t.gidx: t.deprel for t in doc.toks} for doc, _m in data}   # the chain's labels
        rank_dep = {}
        for doc, mlive in data:
            mi2headg = {i: doc.mentions[i].head_g for i in range(len(doc.mentions))}
            d = {t.gidx: "" for t in doc.toks}
            for mi, m in enumerate(mlive):
                hg = mi2headg.get(mi)
                if hg is not None:
                    d[hg] = RANK2DEP.get(m.get("sent_role_rank", 99), "")
            rank_dep[id(doc)] = d

        def set_deps(src):
            for doc, _m in data:
                dd = src[id(doc)]
                for t in doc.toks:
                    t.deprel = dd.get(t.gidx, "") or "dep"

        set_deps(rank_dep)
        A = np.array([h for h, _f, _r, _m in run_affected_arm(data, info, maps, mode="hard", gamma_g=1.0,
                                                              gamma_t=1.0, targets=targets)], float)
        set_deps(chain_dep)
        B = np.array([h for h, _f, _r, _m in run_affected_arm(data, info, maps, mode="hard", gamma_g=1.0,
                                                              gamma_t=1.0, targets=targets)], float)
        C = np.array([h for h, _f, _r, _m in run_affected_arm(data, info, maps, mode="ppc", gamma_g=1.0,
                                                              gamma_t=1.0, targets=targets,
                                                              norm_g=ng, norm_t=nt)], float)
        out[split] = {"n": int(len(A)),
                      "A_reader_rank_proxy": round(float(A.mean()), 4),
                      "B_role_competition_label": round(float(B.mean()), 4),
                      "C_role_competition_decision": round(float(C.mean()), 4),
                      "B_vs_A": _paired(A, B, n_boot=n_boot), "C_vs_A": _paired(A, C, n_boot=n_boot),
                      "C_vs_B": _paired(B, C, n_boot=n_boot)}
        if verbose:
            d = out[split]
            print("  [wire] %s n=%d | A %.4f -> B %.4f (%+.4f CI[%+.4f,%+.4f] sep=%s) -> C %.4f "
                  "(%+.4f CI[%+.4f,%+.4f] sep=%s over A)"
                  % (split, d["n"], d["A_reader_rank_proxy"], d["B_role_competition_label"],
                     d["B_vs_A"]["delta"], d["B_vs_A"]["ci95"][0], d["B_vs_A"]["ci95"][1], d["B_vs_A"]["ci_sep"],
                     d["C_role_competition_decision"], d["C_vs_A"]["delta"], d["C_vs_A"]["ci95"][0],
                     d["C_vs_A"]["ci95"][1], d["C_vs_A"]["ci_sep"]), flush=True)
    return out


# ---------------------------------------------------------------------------------------------------------------
# 10. THE SAME REPAIR THROUGH THE LIVE READER (strategy integration step, 2026-09-14).
#     Section 9 prices the wire on the resolver organ. This runs the actual `SituationReader.read()` over the GUM
#     test documents under HDLAB_AER_ROLE_CUE=hard vs ppc and scores `sm.affected_entity`, so the number is the
#     LIVE reader's own rather than a re-implementation of it. read() takes a CoNLL PATH (that was the
#     "reader-configuration matter": raw text is interpreted as a path), so each document is written to a temp
#     CoNLL with the gold coref column via hdlab.situation_reader._write_temp_conll -- the same mention regime the
#     cell's own arms use (gold mention SPANS, gold-free DECISIONS).
#
#     SCORING (stated plainly because it is not the cell's metric): the reader hands back head-individuated entity
#     KEYS, not clusters. A record counts as a hit when the resolved key matches the surface head of some earlier
#     gold mention of the undergoer pronoun's OWN gold cluster. Absolute levels are therefore NOT comparable with
#     section 9's; the A/B between the two cue modes on the identical population is what this arm measures.
# ---------------------------------------------------------------------------------------------------------------
def _gum_doc_to_conll_rows(doc):
    """(sent_idx, wtok, token, coref_col) for one GUM doc, with the GOLD coref column (mention spans only)."""
    opens, closes, singles = {}, {}, {}
    for m in doc.mentions:
        if m.start_g == m.end_g:
            singles.setdefault(m.start_g, []).append(m.eid)
        else:
            opens.setdefault(m.start_g, []).append(m.eid)
            closes.setdefault(m.end_g, []).append(m.eid)
    rows, wt, prev = [], 0, None
    for t in sorted(doc.toks, key=lambda x: x.gidx):
        if prev is not None and t.sent != prev:
            wt = 0
        prev = t.sent
        parts = ["(%d" % e for e in opens.get(t.gidx, [])] + ["(%d)" % e for e in singles.get(t.gidx, [])] \
            + ["%d)" % e for e in closes.get(t.gidx, [])]
        rows.append((t.sent, wt, t.form, "|".join(parts) if parts else "_"))
        wt += 1
    return rows


def live_reader_ab(n_docs=None, n_boot=2000, verbose=True):
    """A/B the LIVE reader's affected-entity read under the two role-cue modes on the GUM test split."""
    import importlib
    import hdlab.situation_reader as HSR
    import hdlab.affected_entity_resolver as AER
    import experiments.exp_affected_entity_salience_prior_gum_v1 as B1
    docs = B1._load_test(None)
    if n_docs:
        docs = docs[:n_docs]
    out = {"n_docs": len(docs), "mode_results": {}}
    per_mode = {}
    errors = []
    for mode in ("hard", "ppc"):
        AER.GRADED_ROLE_CUE = mode
        hits, keys = [], []
        t0 = time.time()
        for di, doc in enumerate(docs):
            rows = _gum_doc_to_conll_rows(doc)
            path = HSR._write_temp_conll(rows)
            try:
                sm = HSR.SituationReader().read(path)
            except Exception as e:                       # report, never fabricate
                errors.append("%s: %s: %s" % (doc.docid, type(e).__name__, e))
                continue
            finally:
                try:
                    os.remove(path)
                except OSError:
                    pass
            # gold: for each pronoun mention, the surface heads of the EARLIER mentions of its own cluster
            by_gidx = {t.gidx: t for t in doc.toks}
            sent_first = {}
            for t in sorted(doc.toks, key=lambda x: x.gidx):
                sent_first.setdefault(t.sent, t.gidx)
            legal = {}
            for m in doc.mentions:
                if m.mtype != "pronoun":
                    continue
                prior = [x for x in doc.mentions if x.order < m.order and x.eid == m.eid and x.mtype != "pronoun"]
                legal[(m.sent, (by_gidx[m.head_g].form or "").lower())] = {
                    (by_gidx[x.head_g].form or "").lower() for x in prior}
            for rec in (getattr(sm, "affected_entity", None) or []):
                k = (rec.get("sent_idx"), str(rec.get("undergoer") or "").lower())
                if k not in legal or not legal[k]:
                    continue                              # no recoverable gold antecedent -> outside the population
                hits.append(int(str(rec.get("resolved") or "").lower() in legal[k]))
                keys.append((doc.docid, k))
            if verbose and di and di % 10 == 0:
                print("  [live] %s doc %d/%d %.0fs" % (mode, di, len(docs), time.time() - t0), flush=True)
        per_mode[mode] = (hits, keys)
        if verbose:
            print("  [live] %s: n=%d acc=%.4f (%.0fs)"
                  % (mode, len(hits), (float(np.mean(hits)) if hits else float("nan")), time.time() - t0), flush=True)
    AER.GRADED_ROLE_CUE = "hard"
    h_hits, h_keys = per_mode["hard"]
    p_hits, p_keys = per_mode["ppc"]
    out["errors"] = errors[:10]
    out["n_errors"] = len(errors)
    if h_keys == p_keys and h_hits:
        out["hard"] = round(float(np.mean(h_hits)), 4)
        out["ppc"] = round(float(np.mean(p_hits)), 4)
        out["ppc_vs_hard"] = _paired(h_hits, p_hits, n_boot=n_boot)
        out["n_items"] = len(h_hits)
    else:
        out["hard"] = round(float(np.mean(h_hits)), 4) if h_hits else None
        out["ppc"] = round(float(np.mean(p_hits)), 4) if p_hits else None
        out["note"] = ("the two modes produced DIFFERENT item sets (%d vs %d) -- the reader's affected-entity "
                       "record set is itself cue-dependent, so a paired CI over a fixed population is not "
                       "available from this arm" % (len(h_hits), len(p_hits)))
    return out

def run(smoke=False, n_boot=2000, verbose=True):
    """The whole measurement: the reliability maps, the signal-loss ledger, the fusion-weight sweep on DEV, the two
    consumers on their own populations, and the full-stack-upstream contrast."""
    t0 = time.time()
    os.makedirs(OUT_DIR, exist_ok=True)
    maps = load_or_build_reliability(cap=(300 if smoke else None), verbose=verbose)
    res = {"anchor": ANCHOR, "seed": SEED, "smoke": bool(smoke),
           "reliability_maps": {k: {"base": round(v.base, 4), "n": int(sum(c[1] for c in v.counts.values())),
                                    "r_min": round(min(v.table().values()), 4),
                                    "r_max": round(max(v.table().values()), 4)} for k, v in maps.items()}}
    if verbose:
        print("[1/5] signal-loss ledger", flush=True)
    res["signal_trace"] = signal_trace(maps, cap=(40 if smoke else 700))
    if verbose:
        print("[2/5] fusion-weight sweep on the GUM DEV split", flush=True)
    sweep = sweep_affected(maps, limit=(20 if smoke else None), sal_norms=(False,), verbose=verbose)
    res["dev_sweep"] = sweep
    if verbose:
        print("[3/5] C1 affected entity, LIVE BF chain", flush=True)
    res["C1_affected_entity_live_chain"] = consumer_affected_entity(maps, limit=(20 if smoke else None),
                                                                    n_boot=n_boot, sweep=sweep, verbose=verbose)
    if verbose:
        print("[4/5] C1 affected entity, GOLD categories + GOLD heads (the upstream contrast)", flush=True)
    res["C1_affected_entity_gold_upstream"] = consumer_affected_entity(
        maps, limit=(20 if smoke else None), n_boot=n_boot, sweep=sweep, gold_pos=True, gold_heads=True,
        verbose=verbose)
    if verbose:
        print("[5/5] C2 the agent read, confidence-licensed override", flush=True)
    oc_path = os.path.join(OUT_DIR, "order_cue_counts.json")
    if os.path.exists(oc_path):
        order_counts = json.load(open(oc_path, encoding="utf-8"))
    else:
        order_counts = _order_cue_counts(cap=(200 if smoke else None), verbose=verbose)
        json.dump(order_counts, open(oc_path, "w", encoding="utf-8"), indent=1)
    res["C2_gate_fit_on_train"] = fit_agent_gate(maps, order_counts, cap=(200 if smoke else None), verbose=verbose)
    res["C2_chain_agent"] = consumer_chain_agent(maps, order_counts, cap=(40 if smoke else None),
                                                 bias=res["C2_gate_fit_on_train"]["bias"],
                                                 n_boot=n_boot, verbose=verbose)
    for f in ("c1_test_live.json", "c1_test_goldupstream.json", "c2_final.json", "c2_patch_fidelity.json",
              "c1_logpost.json", "c1_oracle_gate.json", "match_reliability.json"):
        fp = os.path.join(OUT_DIR, f)
        if os.path.exists(fp):
            res.setdefault("artifacts", {})[f] = json.load(open(fp, encoding="utf-8"))
    if verbose:
        print("[6/6] the wire price (the board-invisible instrument arm)", flush=True)
    res["wire_price"] = wire_price(maps, limit=(20 if smoke else None), n_boot=n_boot, verbose=verbose)
    res["elapsed_s"] = round(time.time() - t0, 1)
    return res


def self_test():
    """(a) the three+one reliability maps are monotone and separate; (b) mode='hard' reproduces the LANDED organ's
    picks item for item (so every other consumer is untouched); (c) the calibrated class posterior is a
    distribution; (d) the log-odds weight is monotone; (e) the match map is the one a PARALLELISM consumer needs --
    its base rate must sit BELOW the label's, which is the measured correlated-error fact."""
    import experiments.exp_affected_entity_token_history_gum_v1 as TH
    maps = load_or_build_reliability(cap=400, verbose=False)
    for k, m in maps.items():
        t = m.table(); ks = sorted(t)
        assert all(t[ks[i]] <= t[ks[i + 1]] + 1e-9 for i in range(len(ks) - 1)), "%s not monotone" % k
        assert t[ks[-1]] > t[ks[0]], "%s does not separate: %.3f vs %.3f" % (k, t[ks[0]], t[ks[-1]])
    assert maps["patient"].base > maps["aer_class"].base > maps["role8"].base,         "reliability must RISE as the decision the consumer reads gets coarser"
    data = _load_gum(20, split="test")
    targets = gold_targets(data)
    info = _chain_overlay(data, cache_path=os.path.join(OUT_DIR, "selftest_chain.pkl"), verbose=False)
    a = run_affected_arm(data, info, maps, mode="hard", targets=targets)
    b = TH.run_arm(data, accrue=True, window=2, principle_a=True, targets=targets)
    va = [h for h, _f, _r, _m in a]; vb = [h for h, _f in b]
    assert va == vb, "mode='hard' is NOT the landed organ (%d vs %d items)" % (len(va), len(vb))
    pk = _pack(np.array([0.5, 0.2, 0.1, 0.1, 0.05, 0.03, 0.01, 0.01]), 0.3)
    tot = sum(_cal_class(pk, c, 0.7) for c in PAR_CLASSES)
    assert abs(tot - 1.0) < 1e-6, "the calibrated class posterior is not a distribution: %.6f" % tot
    assert abs(_cal_class(pk, pk["map_class"], 0.7) - 0.7) < 1e-9
    assert _llr(0.9, 3) > _llr(0.6, 3) > 0
    assert cue_terms(pk, pk["map_class"], None, mode="hard") == (1.0, float(pk["map_patient"]))
    print("[SELFTEST PASS] role-margin reliability: four count-calibrated monotone maps (role8 %.3f < class %.3f < "
          "patient %.3f, match %.3f), mode='hard' is item-identical to the landed affected-entity organ on %d GUM "
          "items, the calibrated class posterior sums to 1, and the log-odds weight is monotone."
          % (maps["role8"].base, maps["aer_class"].base, maps["patient"].base, maps["match"].base, len(va)))
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--wire-price", action="store_true", dest="wire_price",
                    help="the board-invisible instrument arm: price the reader-wire repair (section 9)")
    ap.add_argument("--live-reader", action="store_true", dest="live_reader",
                    help="the same repair through the LIVE SituationReader.read() (section 10)")
    ap.add_argument("--docs", type=int, default=None, help="cap GUM documents for --live-reader")
    a = ap.parse_args()
    if a.self_test:
        self_test(); return
    if a.wire_price:
        maps = load_or_build_reliability()
        r = wire_price(maps, n_boot=a.n_boot)
        os.makedirs(OUT_DIR, exist_ok=True)
        json.dump(r, open(os.path.join(OUT_DIR, "p7_reader_wire_price.json"), "w", encoding="utf-8"), indent=1)
        print(json.dumps(r, indent=1))
        print("DONE ->", os.path.join(OUT_DIR, "p7_reader_wire_price.json")); return
    if a.live_reader:
        r = live_reader_ab(n_docs=a.docs, n_boot=a.n_boot)
        os.makedirs(OUT_DIR, exist_ok=True)
        json.dump(r, open(os.path.join(OUT_DIR, "p7_live_reader_ab.json"), "w", encoding="utf-8"), indent=1)
        print(json.dumps(r, indent=1))
        print("DONE ->", os.path.join(OUT_DIR, "p7_live_reader_ab.json")); return
    res = run(smoke=a.smoke, n_boot=a.n_boot)
    os.makedirs(OUT_DIR, exist_ok=True)
    json.dump(res, open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="utf-8"), indent=1)
    print(json.dumps(res, indent=1)[:8000])
    print("DONE ->", os.path.join(OUT_DIR, "metrics.json"))


if __name__ == "__main__":
    main()
