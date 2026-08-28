"""exp_coref_graded_cue_retrieval_litbank_v1 -- brain-faithful GRADED cue-based-retrieval pronoun
antecedent resolution on REAL narrative (LitBank, 100 novels), the audit's named "real open case":
COMPETITIVE antecedent resolution among 2+ plausible referents.

WHY THIS CELL (problem: coreference_is_capped_at_065_on_real_narrative). The landed coref organ picks a
pronoun's antecedent by a HARD, TIERED rule (strict-Cb: most-recent grammatical-subject clause, then
recency -- hdlab/coreference_resolver._pick_strict_cb) and emits at most a COARSE integer margin. Two prior
results bound the space and are REUSED here as floors, not re-derived:
  * exp_coref_cue_based_retrieval_actr_activation_v1  -> HARD_FAIL: a pure ACT-R base-level ACTIVATION pick
    (recency + frequency + role) LOST to the tiered rule (-0.135 CI-sep) and even to its own scrambled twin.
    Base-level activation UNDER-weights grammatical subjecthood -- the highest-validity reference cue.
  * exp_coref_cb_tier_error_anatomy_v1 -> RANKING_DOMINATED: 25/25 errors are RANKING (0 retrieval); the
    gold is always in the compatible pool. Error concentrates where the gold is NOT the previous-clause
    subject (0.0 err when it IS) and NOT most-recent -- i.e. exactly where cues CONFLICT.

THE BRAIN (frame; PINNED vs OUR-INVENTION):
  * PINNED -- reference is CUE-BASED RETRIEVAL from working memory: candidate antecedents compete via an
    ADDITIVE weighted sum of graded cue activations, A_i = sum_c w_c * support_c(i) (Lewis & Vasishth 2005;
    McElree 2003 content-addressable retrieval), read out by softmax = the Bayesian/FLMP posterior
    (McClelland 2013). The CUE ORDERING is Centering (Grosz/Joshi/Weinstein 1995): grammatical subjecthood /
    backward-looking-center / advantage-of-first-mention outrank pure recency. This is the SAME graded
    competition currency the parser/role-assigner already uses -- REUSED verbatim: hdlab.graded_competition.
  * OUR-INVENTION-UNDER-TEST (swept, tuned on DEV, reported on TEST): the per-cue WEIGHTS (Competition-Model
    cue validities) and the softmax GAIN. We COPY the operation (additive cue activation -> softmax posterior)
    and SWEEP the weights; we never adopt a number.
  * The value of the graded form is NOT a guaranteed argmax gain (graded_competition's MAP-optimality theorem:
    graded argmax == the discrete argmax of the SAME net). Its value is (a) a DIFFERENT, better-weighted net
    than the hard tiered rule -> a real, testable Track-A accuracy question, and (b) the maintained
    DISTRIBUTION -> a calibrated entropy/margin ABSTAIN (Track B; the brain-faithful "cues conflict -> defer").

TASK (arm-independent construction; only the SCORING differs across arms): every 3rd-person pronoun mention
whose gold entity was introduced earlier AND that has >=2 gender/number-compatible prior gold entities (the
COMPETITIVE subset -- Hobbs single-vs-multi). Exactly one candidate is gold. Each arm scores the candidates
and picks argmax; accuracy = argmax == gold. Population = LitBank 100 novels, split DEV/TEST by document
(weights tuned on DEV only; every headline reported on TEST).

ARMS:
  recency          FLOOR: argmax closeness (the salience/recency default).
  strict_cb        FLOOR = THE INCUMBENT'S PICK RULE recomputed on THIS population: rank by
                   (most-recent-subject-sentence, then recency) -- hdlab _pick_strict_cb.
  actr             the HARD_FAILED base-level activation pick (recency+freq+role), reused as a floor.
  graded           OURS: hdlab.graded_competition additive cue activation (recency, subjecthood, backward-
                   center, frequency, first-mention) -> softmax posterior; argmax = pick; entropy/margin =
                   confidence. Weights + gain tuned on DEV.
  random           INFO-FREE twin: uniform pick among compatible candidates (must LOSE CI-sep).
  graded_shuf      INFO-FREE twin: candidate cue-support vectors permuted (identity scrambled, shape kept).

Run: .venv/Scripts/python.exe experiments/exp_coref_graded_cue_retrieval_litbank_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_coref_graded_cue_retrieval_litbank_v1.py --run
ASCII only. Reads the pre-parsed cache; writes nothing to hdlab/. NO torch (pure numpy).
# KB_REFERENT: data/litbank/who_did_what_events.json
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple

import numpy as np

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments.exp_litbank_activation_binder_v1 import PRONOUNS, ROLE_W, _gn_compat, _dt  # noqa: E402
from hdlab.graded_competition import graded_pick  # noqa: E402

CACHE = os.path.join(REPO_ROOT, "data", "litbank", "who_did_what_events.json")
SEED = 20260828
# The pinned Lewis-Vasishth / ACT-R base-level activation is ITSELF a cue in the graded net (it is the
# retrieval currency: recency*frequency*role); the geometry cues below are the Centering terms added to it.
CUES = ("recency", "subject", "cb", "freq", "first", "parallel")
WEIGHT_KEYS = CUES + ("actr",)
D_GRID = (1.0, 1.5, 2.0, 3.0)          # ACT-R decay swept on DEV (OUR-INVENTION), never adopted
ACTR_D_FLOOR = 2.0                     # the binder cell's own held-out selection, used for the ACT-R FLOOR arm


# --------------------------------------------------------------------------- data
def load_streams(docs: Optional[int] = None) -> List[Dict]:
    with open(CACHE, encoding="utf-8") as fh:
        recs = json.load(fh)
    return recs[:docs] if docs else recs


def _entity_gn_gold(stream) -> Dict[int, Tuple[Optional[str], Optional[str]]]:
    """Stable gender/number per GOLD entity from its own pronoun mentions (an entity property, not a
    resolution cue) -- so the agreement pre-filter and the candidate set are ARM-INDEPENDENT."""
    gv, nv = defaultdict(Counter), defaultdict(Counter)
    for m in stream:
        ht = m["head_text"]
        if ht in PRONOUNS:
            g, n = PRONOUNS[ht]
            gv[m["gold"]][g] += 1
            nv[m["gold"]][n] += 1
    out = {}
    for e in {m["gold"] for m in stream}:
        out[e] = (gv[e].most_common(1)[0][0] if gv[e] else None,
                  nv[e].most_common(1)[0][0] if nv[e] else None)
    return out


def build_instances(streams: List[Dict]) -> List[Dict]:
    """Competitive pronoun-antecedent resolution instances (see module docstring). Each:
    {doc, pronoun, p_sent, gold_cid, cand_ids:[...], prior:{cid:[(sent,role),...]}}."""
    out: List[Dict] = []
    for rec in streams:
        stream = rec["stream"]
        egn = _entity_gn_gold(stream)
        prior_by_cluster: Dict[int, List[Tuple[int, str]]] = defaultdict(list)
        for m in stream:
            ht = m["head_text"]
            gold = m["gold"]
            if ht in PRONOUNS:
                pg, pn = PRONOUNS[ht]
                # candidate = any cluster with >=1 prior mention, agreement-compatible (arm-independent gn)
                cand = {}
                for c, pri in prior_by_cluster.items():
                    if not pri:
                        continue
                    eg, en = egn.get(c, (None, None))
                    if _gn_compat(pg, pn, eg, en):
                        cand[c] = list(pri)
                if gold in cand and len(cand) >= 2:
                    out.append({
                        "doc": rec["doc"], "pronoun": ht, "p_sent": m["sent"],
                        "pron_role": m["role"],
                        "gold_cid": gold, "cand_ids": sorted(cand),
                        "prior": {c: cand[c] for c in cand},
                    })
            # observe this mention into its cluster's running history (after using priors)
            prior_by_cluster[gold].append((m["sent"], m["role"]))
    return out


# --------------------------------------------------------------------------- cue supports
def _supports(inst: Dict) -> Tuple[List[int], Dict[str, np.ndarray], int]:
    """Per-candidate cue-support arrays (higher = stronger antecedent) + gold index. All computable from
    prior mentions -- the graded arm supplies weights, this supplies the pinned cue GEOMETRY."""
    ids = inst["cand_ids"]
    p_sent = inst["p_sent"]
    prior = inst["prior"]
    # backward-looking center: the most recent prior sentence any candidate occupied
    prev_sent = max((s for c in ids for (s, _r) in prior[c] if s < p_sent), default=None)
    earliest = {c: min(s for s, _r in prior[c]) for c in ids}
    first_sent = min(earliest.values())
    pron_role = inst.get("pron_role", "OTHER")
    rec, subj, cb, freq, first, par = [], [], [], [], [], []
    for c in ids:
        pri = prior[c]
        nearest = min(_dt(p_sent, s) for s, _r in pri)          # >=1 sentence distance
        rec.append(1.0 / nearest)                               # recency: closer -> higher
        subj.append(max(ROLE_W.get(r, 1.0) for _s, r in pri))  # Cf prominence (subjecthood)
        cb.append(1.0 if any(s == prev_sent and r == "SUBJECT" for s, r in pri) else 0.0)  # backward center
        freq.append(math.log1p(len(pri)))                      # base-level frequency / topichood
        first.append(1.0 if earliest[c] == first_sent else 0.0)  # advantage-of-first-mention
        # PARALLELISM (Smyth 1994): candidate's MOST-RECENT role == the pronoun's own role
        last_role = max(pri, key=lambda sr: sr[0])[1]
        par.append(1.0 if last_role == pron_role else 0.0)
    sup = {"recency": np.array(rec), "subject": np.array(subj), "cb": np.array(cb),
           "freq": np.array(freq), "first": np.array(first), "parallel": np.array(par)}
    gold_idx = ids.index(inst["gold_cid"])
    return ids, sup, gold_idx


def _zscore(v: np.ndarray) -> np.ndarray:
    s = v.std()
    return (v - v.mean()) / s if s > 1e-12 else np.zeros_like(v)


def _actr_support(inst: Dict, d: float) -> np.ndarray:
    """Per-candidate ACT-R base-level activation A_i = ln(sum_k w_role(k) * dt_k^-d) -- the pinned
    Lewis-Vasishth / Anderson retrieval currency (recency * frequency * role prominence in one term)."""
    p_sent = inst["p_sent"]
    prior = inst["prior"]
    out = []
    for c in inst["cand_ids"]:
        s = sum(ROLE_W.get(r, 1.0) * (_dt(p_sent, sent) ** (-d)) for sent, r in prior[c])
        out.append(math.log(s) if s > 0 else -1e9)
    return np.array(out)


def _zsup(sup: Dict[str, np.ndarray], inst: Dict, d: float) -> Dict[str, np.ndarray]:
    z = {c: _zscore(sup[c]) for c in CUES}
    z["actr"] = _zscore(_actr_support(inst, d))
    return z


# --------------------------------------------------------------------------- arms (return pick index + optional posterior readouts)
def arm_recency(ids, sup, gold_idx) -> Dict:
    return {"pick": int(np.argmax(sup["recency"]))}


def arm_strict_cb(ids, sup, gold_idx, inst) -> Dict:
    """The incumbent's pick rule: (most-recent-subject-sentence, then recency)."""
    p_sent = inst["p_sent"]
    prior = inst["prior"]
    def key(i):
        c = ids[i]
        subj_sents = [s for s, r in prior[c] if r == "SUBJECT" and s < p_sent]
        mrs = max(subj_sents) if subj_sents else -1
        nearest = min(_dt(p_sent, s) for s, _r in prior[c])
        return (mrs, -nearest)
    return {"pick": int(max(range(len(ids)), key=key))}


def arm_actr(ids, sup, gold_idx, inst, d: float) -> Dict:
    """ACT-R base-level activation: ln(sum_k w_role * dt^-d). The prior HARD_FAILED pick, reused as a floor."""
    p_sent = inst["p_sent"]
    prior = inst["prior"]
    def act(c):
        s = sum(ROLE_W.get(r, 1.0) * (_dt(p_sent, sent) ** (-d)) for sent, r in prior[c])
        return math.log(s) if s > 0 else -1e9
    scores = [act(c) for c in ids]
    return {"pick": int(np.argmax(scores))}


def arm_graded(ids, sup, gold_idx, inst, weights: Dict[str, float], gain: float, d: float) -> Dict:
    """OURS: hdlab.graded_competition additive cue activation over the pinned ACT-R retrieval activation
    PLUS the Centering geometry cues -> softmax posterior. argmax = pick (task-triggered collapse);
    normalized entropy + activation margin = the confidence the abstain gate consumes."""
    zsup = _zsup(sup, inst, d)
    g = graded_pick(zsup, weights, gain=gain)
    return {"pick": int(g["win"]), "entropy": float(g["entropy"]), "margin": float(g["margin"]),
            "p_gold": float(g["p"][gold_idx])}


def arm_random(ids, sup, gold_idx, rng: np.random.Generator) -> Dict:
    return {"pick": int(rng.integers(0, len(ids)))}


def arm_graded_shuf(ids, sup, gold_idx, inst, weights, gain, d, rng) -> Dict:
    """INFO-FREE twin: permute each cue's per-candidate support (identity scrambled, shape kept)."""
    perm = rng.permutation(len(ids))
    zsup = _zsup(sup, inst, d)
    shuf = {c: zsup[c][perm] for c in WEIGHT_KEYS}
    g = graded_pick(shuf, weights, gain=gain)
    return {"pick": int(g["win"]), "entropy": float(g["entropy"]), "margin": float(g["margin"])}


# --------------------------------------------------------------------------- tuning (DEV only)
def tune_gain_for_calibration(dev_insts, weights, d, gains=(1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0)) -> float:
    """Pick the softmax gain maximizing DEV entropy->error AUC (Track-B calibration). GAIN-INVARIANT for
    argmax, so Track-A accuracy is untouched -- a sharper posterior makes normalized entropy a better
    gold-free error predictor. Copies the operation; SWEEPS the precision parameter, never adopts it."""
    best_g, best_auc = 2.0, -1.0
    for g in gains:
        recs = []
        for inst in dev_insts:
            ids, sup, gi = _supports(inst)
            r = arm_graded(ids, sup, gi, inst, weights, g, d)
            recs.append({"correct": int(r["pick"] == gi), "entropy": r["entropy"]})
        auc = _entropy_error_auc(recs)
        if auc == auc and auc > best_auc:   # skip NaN
            best_auc, best_g = auc, g
    return best_g


def _precompute_zsup(insts) -> List[Dict]:
    """Per-instance z-scored cue supports (geometry cues d-independent; ACT-R z-support per d in D_GRID)
    + gold index. Cached ONCE so DEV tuning is a vectorized dot product, not a re-parse per config.
    NOTE: argmax(net) is GAIN-INVARIANT, so accuracy tuning ignores the softmax gain (gain only sharpens
    the Track-B posterior); we tune weights + decay d for accuracy and keep the pinned gain for read-out."""
    cache = []
    for inst in insts:
        ids, sup, gi = _supports(inst)
        z = {c: _zscore(sup[c]) for c in CUES}
        z_actr = {dv: _zscore(_actr_support(inst, dv)) for dv in D_GRID}
        cache.append({"z": z, "z_actr": z_actr, "gi": gi})
    return cache


def _acc_cached(cache, weights, d) -> float:
    ok = 0
    for e in cache:
        net = e["z_actr"][d] * weights["actr"]
        for c in CUES:
            wc = weights[c]
            if wc:
                net = net + e["z"][c] * wc
        if int(np.argmax(net)) == e["gi"]:
            ok += 1
    return ok / len(cache) if cache else 0.0


def tune_graded(dev_insts) -> Tuple[Dict[str, float], float, float]:
    """Coordinate-ascent over cue weights (incl. the pinned ACT-R activation) + ACT-R decay d on DEV
    accuracy (OUR-INVENTION swept, never adopted). Deterministic. Copies the OPERATION; only the cue
    VALIDITIES / decay are fit. The search space SUBSUMES pure ACT-R (all geometry weights 0, w_actr>0),
    so the graded arm cannot do worse than ACT-R on DEV by construction. Gain is the read-out precision
    (Track B), not an accuracy knob -- it is gain-invariant for argmax, so we keep the pinned DEFAULT."""
    cache = _precompute_zsup(dev_insts)
    weights = {c: 0.0 for c in CUES}
    weights["actr"] = 1.0
    d = ACTR_D_FLOOR
    grid = [0.0, 0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0]
    best = _acc_cached(cache, weights, d)
    for _sweep in range(5):
        improved = False
        for c in WEIGHT_KEYS:
            base = weights[c]
            for w in grid:
                weights[c] = w
                a = _acc_cached(cache, weights, d)
                if a > best + 1e-9:
                    best, base, improved = a, w, True
            weights[c] = base
        for dv in D_GRID:
            a = _acc_cached(cache, weights, dv)
            if a > best + 1e-9:
                best, d, improved = a, dv, True
        if not improved:
            break
    return weights, 2.0, d


# --------------------------------------------------------------------------- evaluation
ARMS = ("recency", "strict_cb", "actr", "graded", "random", "graded_shuf")


def evaluate(insts, weights, gain, d, d_actr=ACTR_D_FLOOR, seed=SEED) -> Dict:
    """Per-doc (correct,total) per arm + per-instance graded records (entropy/margin/correct/difficulty)."""
    rng = np.random.default_rng(seed)
    per_doc = {a: defaultdict(lambda: [0, 0]) for a in ARMS}
    graded_recs = []
    disagree = {"graded_right_cb_wrong": 0, "cb_right_graded_wrong": 0, "example": None}
    for inst in insts:
        ids, sup, gi = _supports(inst)
        doc = inst["doc"]
        res = {
            "recency": arm_recency(ids, sup, gi),
            "strict_cb": arm_strict_cb(ids, sup, gi, inst),
            "actr": arm_actr(ids, sup, gi, inst, d_actr),
            "graded": arm_graded(ids, sup, gi, inst, weights, gain, d),
            "random": arm_random(ids, sup, gi, rng),
            "graded_shuf": arm_graded_shuf(ids, sup, gi, inst, weights, gain, d, rng),
        }
        for a in ARMS:
            ok = int(res[a]["pick"] == gi)
            per_doc[a][doc][0] += ok
            per_doc[a][doc][1] += 1
        gok = int(res["graded"]["pick"] == gi)
        cok = int(res["strict_cb"]["pick"] == gi)
        graded_recs.append({"doc": doc, "correct": gok, "entropy": res["graded"]["entropy"],
                            "margin": res["graded"]["margin"], "n_cand": len(ids),
                            "p_sent": inst["p_sent"], "pronoun": inst["pronoun"]})
        if gok and not cok:
            disagree["graded_right_cb_wrong"] += 1
            if disagree["example"] is None:
                disagree["example"] = {"doc": doc, "pronoun": inst["pronoun"], "n_cand": len(ids)}
        if cok and not gok:
            disagree["cb_right_graded_wrong"] += 1
    return {"per_doc": {a: dict(per_doc[a]) for a in ARMS}, "graded_recs": graded_recs,
            "disagree": disagree}


def _pairs(per_doc_arm) -> List[Tuple[int, int]]:
    return [tuple(v) for v in per_doc_arm.values()]


def _ci(pairs, n_boot, seed):
    arr = np.array(pairs, float)
    tot = arr[:, 1].sum()
    acc = arr[:, 0].sum() / tot if tot else 0.0
    r = np.random.default_rng(seed)
    nd = len(arr)
    boots = []
    for _ in range(n_boot):
        idx = r.integers(0, nd, nd)
        c, n = arr[idx, 0].sum(), arr[idx, 1].sum()
        boots.append(c / n if n else 0.0)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {"acc": round(acc, 4), "lo": round(float(lo), 4), "hi": round(float(hi), 4),
            "n": int(tot)}


def _paired(a_pairs_map, b_pairs_map, n_boot, seed):
    """Paired bootstrap over the SHARED doc set (docs are the resampling unit)."""
    docs = sorted(set(a_pairs_map) & set(b_pairs_map))
    a = np.array([a_pairs_map[d] for d in docs], float)
    b = np.array([b_pairs_map[d] for d in docs], float)
    delta = a[:, 0].sum() / max(a[:, 1].sum(), 1) - b[:, 0].sum() / max(b[:, 1].sum(), 1)
    r = np.random.default_rng(seed)
    nd = len(docs)
    boots = []
    for _ in range(n_boot):
        idx = r.integers(0, nd, nd)
        boots.append(a[idx, 0].sum() / max(a[idx, 1].sum(), 1)
                     - b[idx, 0].sum() / max(b[idx, 1].sum(), 1))
    boots = np.array(boots)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    null_p95 = float(np.percentile(np.abs(boots - boots.mean()), 95))
    return {"delta": round(float(delta), 4), "lo": round(float(lo), 4), "hi": round(float(hi), 4),
            "half_width": round(float(hi - lo) / 2, 4), "null_p95": round(null_p95, 4),
            "band": "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEP")}


def error_anatomy(insts, weights, gain, d) -> Dict:
    """Characterize the GRADED arm's residual ERRORS: is the gold antecedent STRUCTURALLY recoverable
    (most-recent / max-subjecthood / most-frequent -> our cue weighting had a chance) or structurally
    NON-salient (only SEMANTIC/coherence cues -- implicit causality, world knowledge -- could pick it;
    the brain-can-we-can't residual our glass-box STRUCTURAL resolver cannot reach)?"""
    n_err = 0
    gold_most_recent = gold_max_subject = gold_most_freq = 0
    gold_structurally_favored = 0   # gold is best on AT LEAST ONE structural cue
    gold_structurally_dominated = 0  # gold is best on NONE (needs semantics)
    for inst in insts:
        ids, sup, gi = _supports(inst)
        pick = arm_graded(ids, sup, gi, inst, weights, gain, d)["pick"]
        if pick == gi:
            continue
        n_err += 1
        rec_best = int(np.argmax(sup["recency"])) == gi
        subj_best = sup["subject"][gi] == sup["subject"].max()
        freq_best = sup["freq"][gi] == sup["freq"].max()
        gold_most_recent += int(rec_best)
        gold_max_subject += int(subj_best)
        gold_most_freq += int(freq_best)
        if rec_best or subj_best or freq_best:
            gold_structurally_favored += 1
        else:
            gold_structurally_dominated += 1
    r = (lambda x: round(x / n_err, 4) if n_err else 0.0)
    return {"n_errors": n_err,
            "frac_gold_most_recent": r(gold_most_recent),
            "frac_gold_max_subjecthood": r(gold_max_subject),
            "frac_gold_most_frequent": r(gold_most_freq),
            "frac_gold_structurally_favored_on_some_cue": r(gold_structurally_favored),
            "frac_gold_structurally_DOMINATED_needs_semantics": r(gold_structurally_dominated)}


def _strict_cb_margin(inst) -> float:
    """The INCUMBENT's own pronoun confidence signal recomputed: the integer gap in most-recent-subject-
    sentence between the top-2 candidates (0.0 on a tie) -- hdlab _pronoun_strict_cb_margin. Higher =
    more confident. This is the landed signal downstream metacognition currently reads."""
    p_sent = inst["p_sent"]; prior = inst["prior"]; ids = inst["cand_ids"]
    def mrs(c):
        ss = [s for s, r in prior[c] if r == "SUBJECT" and s < p_sent]
        return max(ss) if ss else -1
    def key(c):
        return (mrs(c), -min(_dt(p_sent, s) for s, _r in prior[c]))
    ranked = sorted(ids, key=key, reverse=True)
    if len(ranked) < 2:
        return 1.0
    return float(mrs(ranked[0]) - mrs(ranked[1]))


def incumbent_confidence_auc(insts) -> float:
    """AUC of the INCUMBENT strict-Cb margin predicting the strict-Cb arm's OWN errors on THIS population
    (apples-to-apples vs the graded posterior entropy, same LitBank competitive set, no number crossing)."""
    recs = []
    for inst in insts:
        ids, sup, gi = _supports(inst)
        pick = arm_strict_cb(ids, sup, gi, inst)["pick"]
        recs.append({"correct": int(pick == gi), "entropy": -_strict_cb_margin(inst)})  # low margin -> error
    return _entropy_error_auc(recs)


def _entropy_error_auc(graded_recs) -> float:
    """AUC of normalized entropy predicting the graded arm's own ERROR (gold-free error estimate)."""
    ent = np.array([r["entropy"] for r in graded_recs])
    err = np.array([1 - r["correct"] for r in graded_recs])
    pos, neg = ent[err == 1], ent[err == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    # rank-based AUC = P(entropy_err > entropy_correct)
    wins = sum((pos[:, None] > neg[None, :]).sum(axis=1))
    ties = sum((pos[:, None] == neg[None, :]).sum(axis=1))
    return float((wins + 0.5 * ties) / (len(pos) * len(neg)))


def _abstain_curve(graded_recs):
    """Kept-subset accuracy as a function of coverage: abstain on the highest-entropy items first.
    Returns coverage->kept_acc, and the full (no-abstain) accuracy."""
    recs = sorted(graded_recs, key=lambda r: r["entropy"])   # keep LOW entropy first
    n = len(recs)
    full = sum(r["correct"] for r in recs) / n if n else 0.0
    curve = {}
    for cov in (1.0, 0.9, 0.8, 0.7, 0.6, 0.5):
        k = max(1, int(round(cov * n)))
        kept = recs[:k]
        curve[cov] = round(sum(r["correct"] for r in kept) / k, 4)
    return {"full_acc": round(full, 4), "coverage_curve": curve, "n": n}


def track_b_abstain(dev_recs, test_recs, target_abstain=0.30, n_boot=2000, seed=SEED):
    """Track B: pick an entropy threshold on DEV so ~target_abstain of items are deferred; apply to TEST.
    Report kept-subset acc vs full acc (paired over docs on the KEPT items), abstain rate, and a
    RANDOM-abstain twin at the matched rate (must not raise kept acc)."""
    dent = np.array(sorted(r["entropy"] for r in dev_recs))
    thr = float(np.quantile(dent, 1.0 - target_abstain))   # abstain if entropy > thr
    kept = [r for r in test_recs if r["entropy"] <= thr]
    abst = [r for r in test_recs if r["entropy"] > thr]
    n = len(test_recs)
    full_acc = sum(r["correct"] for r in test_recs) / n
    kept_acc = sum(r["correct"] for r in kept) / len(kept) if kept else 0.0
    abst_acc = sum(r["correct"] for r in abst) / len(abst) if abst else 0.0
    abstain_rate = len(abst) / n
    # random-abstain twin: defer the SAME NUMBER of items at random -> kept acc ~ full acc
    rng = np.random.default_rng(seed)
    twin_kept_accs = []
    for _ in range(200):
        idx = rng.permutation(n)[:len(kept)]
        twin_kept_accs.append(np.mean([test_recs[i]["correct"] for i in idx]))
    twin_kept = float(np.mean(twin_kept_accs))
    # paired bootstrap over docs: kept-acc minus full-acc (per doc)
    by_doc_kept = defaultdict(lambda: [0, 0])
    by_doc_full = defaultdict(lambda: [0, 0])
    for r in test_recs:
        by_doc_full[r["doc"]][0] += r["correct"]; by_doc_full[r["doc"]][1] += 1
        if r["entropy"] <= thr:
            by_doc_kept[r["doc"]][0] += r["correct"]; by_doc_kept[r["doc"]][1] += 1
    delta = _paired(dict(by_doc_kept), dict(by_doc_full), n_boot, seed + 7)
    return {"entropy_thr": round(thr, 4), "abstain_rate": round(abstain_rate, 4),
            "full_acc": round(full_acc, 4), "kept_acc": round(kept_acc, 4),
            "abstained_acc": round(abst_acc, 4), "random_abstain_twin_kept_acc": round(twin_kept, 4),
            "kept_minus_full_paired": delta, "n_test": n, "n_kept": len(kept)}


# --------------------------------------------------------------------------- top-level cell
def cell(docs: Optional[int] = None, n_boot: int = 2000, seed: int = SEED) -> Dict:
    streams = load_streams(docs)
    insts = build_instances(streams)
    # DEV/TEST split by DOCUMENT (deterministic: sort docs, alternate)
    all_docs = sorted({i["doc"] for i in insts})
    dev_docs = set(all_docs[0::2])
    test_docs = set(all_docs[1::2])
    dev = [i for i in insts if i["doc"] in dev_docs]
    test = [i for i in insts if i["doc"] in test_docs]
    weights, _gain0, d = tune_graded(dev)
    # Track-B calibration: the softmax GAIN is a PRECISION term (graded_competition: swept, not adopted).
    # argmax is gain-invariant, so this does NOT touch Track-A accuracy -- it sharpens the posterior so its
    # entropy is a better gold-free error predictor. Tuned on DEV to maximize entropy->error AUC.
    gain = tune_gain_for_calibration(dev, weights, d)
    ev_test = evaluate(test, weights, gain, d, seed=seed)
    ev_dev = evaluate(dev, weights, gain, d, seed=seed + 1)
    pd = ev_test["per_doc"]
    acc = {a: _ci(_pairs(pd[a]), n_boot, seed + 10 + i) for i, a in enumerate(ARMS)}
    contrasts = {
        "graded_minus_strict_cb": _paired(pd["graded"], pd["strict_cb"], n_boot, seed + 40),
        "graded_minus_actr": _paired(pd["graded"], pd["actr"], n_boot, seed + 41),
        "graded_minus_recency": _paired(pd["graded"], pd["recency"], n_boot, seed + 42),
        "graded_minus_random": _paired(pd["graded"], pd["random"], n_boot, seed + 43),
        "graded_minus_graded_shuf": _paired(pd["graded"], pd["graded_shuf"], n_boot, seed + 44),
        "strict_cb_minus_recency": _paired(pd["strict_cb"], pd["recency"], n_boot, seed + 45),
    }
    return {
        "anchor": "coref_graded_cue_retrieval_litbank_v1",
        "population": "LitBank competitive pronoun antecedent resolution (>=2 gn-compatible prior entities)",
        "n_docs_total": len(all_docs), "n_dev_docs": len(dev_docs), "n_test_docs": len(test_docs),
        "n_dev_instances": len(dev), "n_test_instances": len(test),
        "tuned_weights": {k: round(v, 3) for k, v in weights.items()}, "tuned_gain": gain,
        "tuned_actr_decay_d": d, "actr_floor_decay_d": ACTR_D_FLOOR,
        "accuracy_TEST": acc,
        "dev_graded_acc": round(sum(r["correct"] for r in ev_dev["graded_recs"]) / max(len(dev), 1), 4),
        "contrasts_TEST": contrasts,
        "entropy_predicts_error_AUC_TEST": round(_entropy_error_auc(ev_test["graded_recs"]), 4),
        "incumbent_margin_error_AUC_TEST_SAME_POP": round(incumbent_confidence_auc(test), 4),
        "graded_error_anatomy_TEST": error_anatomy(test, weights, gain, d),
        "abstain_curve_TEST": _abstain_curve(ev_test["graded_recs"]),
        "track_b_abstain": track_b_abstain(ev_dev["graded_recs"], ev_test["graded_recs"],
                                           target_abstain=0.30, n_boot=n_boot, seed=seed),
        "positive_control_disagreement": ev_test["disagree"],
    }


# --------------------------------------------------------------------------- self-test
def self_test():
    """Can-fail fixture: subjecthood must OUTRANK recency. Two instances:
    (A) gold is a LESS-recent SUBJECT; a distractor is a MORE-recent OBJECT -> recency floor MUST miss,
        strict_cb and a subject-weighted graded MUST hit.
    (B) gold is the more-recent subject -> everyone hits (guards against 'always pick oldest')."""
    instA = {"doc": "t", "pronoun": "he", "p_sent": 5, "gold_cid": 1, "cand_ids": [1, 2],
             "prior": {1: [(1, "SUBJECT"), (2, "SUBJECT")], 2: [(4, "OBJECT")]}}
    instB = {"doc": "t", "pronoun": "he", "p_sent": 5, "gold_cid": 2, "cand_ids": [1, 2],
             "prior": {1: [(1, "OBJECT")], 2: [(4, "SUBJECT")]}}
    w = {"recency": 0.2, "subject": 2.0, "cb": 2.0, "freq": 0.2, "first": 0.5, "actr": 0.5}
    for inst, who in ((instA, "A"), (instB, "B")):
        ids, sup, gi = _supports(inst)
        rec = arm_recency(ids, sup, gi)["pick"]
        cb = arm_strict_cb(ids, sup, gi, inst)["pick"]
        gr = arm_graded(ids, sup, gi, inst, w, 3.0, 2.0)
        if who == "A":
            assert rec != gi, "recency floor MUST miss the less-recent subject on A"
            assert cb == gi, f"strict_cb MUST hit the subject on A (got {cb} want {gi})"
            assert gr["pick"] == gi, f"subject-weighted graded MUST hit on A (got {gr['pick']})"
        else:
            assert cb == gi and gr["pick"] == gi, "both must hit the recent subject on B"
    # entropy is a real number in [0,1] and margin >= 0
    ids, sup, gi = _supports(instA)
    g = arm_graded(ids, sup, gi, instA, w, 3.0, 2.0)
    assert 0.0 <= g["entropy"] <= 1.0 and g["margin"] >= 0.0, "posterior readouts malformed"
    print("SELF-TEST PASS (subjecthood outranks recency on A; both hit on B; posterior readouts valid)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--docs", type=int, default=None)
    ap.add_argument("--n-boot", type=int, default=2000)
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.run:
        print(json.dumps(cell(docs=args.docs, n_boot=args.n_boot), indent=2))
        return
    print("use --self-test | --run [--docs N] [--n-boot B]")


if __name__ == "__main__":
    main()
