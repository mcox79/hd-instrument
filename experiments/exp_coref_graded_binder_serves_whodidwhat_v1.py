"""exp_coref_graded_binder_serves_whodidwhat_v1 -- WIRE-DON'T-ISLAND: the who-did-what decode binds
pronouns with a SINGLE-CUE ACT-R score (recency x role); a proven MULTI-CUE graded cue-based binder
(recency, subjecthood, Centering-Cb, frequency, first-mention, parallelism, ACT-R) already exists but is
ISLANDED. This cell wires a clause-level FOCUS-DRIVEN graded pronoun->event binder into the who-did-what
decode and measures the lift toward the perfect-binding ceiling, holding NAME CLUSTERING + STORE fixed.

THE MEASURED LEVER (prior SOLVED the_name_branch_shatters..., reproduced here): who-did-what pronoun-query
accuracy is capped by pronoun->event binding, NOT name clustering. HEAD (head-token names + ACT-R pronouns)
~= 0.17; HEAD_OPB (SAME names + PERFECT pronoun binding) ~= 0.606 (+0.44 CI-sep). The binder is the cap.

THE BRAIN (research_pronoun_event_binding_mechanism_2026-08-29.md; PINNED vs OUR-INVENTION):
  * PINNED -- pronoun->event binding is FOCUS-DRIVEN (not staged): comprehension maintains a persistent
    attentional focus (Centering backward-looking-center Cb; Grosz/Joshi/Weinstein 1995; Gernsbacher
    Structure Building; Zwaan-Radvansky event indexing) and indexes each clause event onto the focused
    entity; pronoun resolution is a confirmatory cue-weighted READOUT (Repeated-Name-Penalty; Nref).
    Retrieval is CUE-BASED (Lewis & Vasishth 2005): additive weighted cue activation A_i = sum_c w_c *
    support_c(i) -> softmax (McClelland 2013 = the Bayesian/FLMP posterior). Cb is a SEPARABLE cue from
    recency+role (Givon persistence; Cb/subject diverge ~20-27%), partly latent in ACT-R base-level.
    Candidate competition is over a SMALL actively-maintained set (McElree/Cowan focus; Cf window).
  * OUR-INVENTION-UNDER-TEST (swept on DEV, never adopted): the per-cue WEIGHTS (Competition-Model cue
    validities), the ACT-R decay d, the soft focus-window W. We COPY the operation (additive cue
    activation -> argmax) via hdlab.graded_competition.net_activation and SWEEP the parameters.
  * REFUTED-ELSEWHERE, DO NOT REBUILD: the coherence/next-mention SEMANTIC prior (Kehler-Rohde) that would
    reach the anti-typical residual -- the sibling problem the_reader_has_no_coherence_next_mention_prior
    already showed it does NOT beat its info-free twin on the structurally-dominated residual. We build the
    STRUCTURAL binder and FLAG the irreducible semantic core, not chase it.

ARMS (identical mention stream, identical name clustering = HEAD, identical direct symbolic decode; only
the PRONOUN BINDER differs -> isolates the binder from name clustering AND from the register fan effect):
  HEAD            : ACT-R single-cue pronoun binding (the LIVE incumbent) -- the FLOOR (~0.17).
  HEAD_STRICTCB   : hard literal-Centering strict-Cb pick (most-recent-subject-clause) -- the hdlab organ.
  HEAD_GRADED     : OURS -- focus-driven multi-cue graded binder (DEV-tuned weights). the ARM under test.
  HEAD_OPB        : perfect pronoun binding (gold) -- the CEILING (~0.606).
  HEAD_GRADED_SHUFROLE : info-free TWIN -- graded binder with clause_role labels SHUFFLED within-doc
                   (destroys the subject/Cb/focus signal the tracked clause_role carries; keeps recency+
                   freq). Isolates that the LIFT comes from the tracked-but-unused role/Cb signal. MUST LOSE.
  HEAD_RANDBIND   : info-free TWIN -- bind each pronoun to a RANDOM gn-compatible candidate. MUST LOSE.

METRIC = governing-verb decode accuracy on PRONOUN-contributed queries (the bar's population) and FULL;
doc-bootstrap CI; weights tuned on DEV docs, every headline on TEST docs.

Run: .venv/Scripts/python.exe experiments/exp_coref_graded_binder_serves_whodidwhat_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_coref_graded_binder_serves_whodidwhat_v1.py --run [--docs N]
GLASS-BOX, remote-safe (reads pre-parsed caches; NO spaCy, NO torch; pure numpy).
# KB_REFERENT: data/litbank/who_did_what_events.json
# KB_REFERENT: data/lexicons/name_gender_gazetteer.tsv
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

import numpy as np

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments.exp_litbank_activation_binder_v1 import PRONOUNS, ROLE_W, _gn_compat, _dt  # noqa: E402
from experiments.exp_name_clustering_serves_whodidwhat_v1 import (  # noqa: E402
    _assign_name, _new_node, _score_direct, combined_pred, DECAY_D)
from experiments.exp_name_entity_clustering_v1 import (  # noqa: E402
    load_enriched, load_given_gazetteer, parse_name, SEED)
from hdlab.graded_competition import net_activation  # noqa: E402

_G2MF = {"masc": "m", "fem": "f"}
# 1st/2nd-person surfaces that are mis-extracted as 3rd-person-referent candidates (the sibling's +2.2
# pool-cleanup lever): a node whose only name tokens are these is a person-feature agreement artifact.
ARTIFACT_PERSON = set("i we me us my our you your myself ourselves yourself yourselves ours mine".split())


_NG_CACHE: Dict[tuple, Optional[str]] = {}


def _name_gender(span_tokens, gaz) -> Optional[str]:
    """Infer a name mention's gender (a hard morphosyntactic agreement constraint the brain applies in
    pronoun resolution). Layered, all admissible static cues: (1) title + given-name gazetteer via
    parse_name (Mr/Miss/gazetteer given names); (2) NOMINAL gender for common-noun mentions (girl/man/
    king/wife...) via hdlab.state_of_mind.infer_nominal_gender -- the cue parse_name misses on the many
    archaic-prose mentions with no gazetteer given name. Node-level propagation (a bare surname inheriting
    'Mr Darcy's masc) is handled by the caller's per-cluster gender slot."""
    key = tuple(t.lower() for t in span_tokens)
    if key in _NG_CACHE:
        return _NG_CACHE[key]
    g = _G2MF.get(parse_name(span_tokens, gaz)["gender"])
    if g is None:
        from hdlab.state_of_mind import infer_nominal_gender
        g = _G2MF.get(infer_nominal_gender(list(key)))
    _NG_CACHE[key] = g
    return g

# Cue set: the pinned Lewis-Vasishth ACT-R retrieval activation + the Centering geometry cues + the
# focus-driven additions (focus = match-to-standing-Cb register; streak = Cb persistence; window = soft
# active-set gate). All computable online from each candidate node's (sent, role) history.
CUES = ("recency", "subject", "cb", "freq", "first", "parallel", "actr", "focus", "streak", "window")
D_GRID = (1.0, 2.0, 3.0)
W_GRID = (4, 999)                     # soft focus-window (sentences); 999 == off (all entities compete)
WGRID = (0.0, 0.5, 1.0, 2.0)          # per-cue weight search grid (cue weights are immaterial: graded==ACT-R)
TUNE_SWEEPS = 2


def _actr(hist, p_sent, d):
    s = sum(ROLE_W.get(r, 1.0) * (_dt(p_sent, sent) ** (-d)) for sent, r in hist)
    return math.log(s) if s > 0 else -1e9


def _zscore(v: np.ndarray) -> np.ndarray:
    s = v.std()
    return (v - v.mean()) / s if s > 1e-12 else np.zeros_like(v)


def _cue_supports(cand_hists: List[List[Tuple[int, str]]], cand_nodes: List[int], p_sent: int,
                  pron_role: str, focus_node: Optional[int], d: float, W: int) -> Dict[str, np.ndarray]:
    """Per-candidate z-scored cue supports (higher = stronger antecedent). Computed ONLINE from each
    candidate node's (sent, role) history -- the pinned cue geometry; the caller supplies the weights."""
    n = len(cand_hists)
    prev_sent = max((s for hist in cand_hists for (s, _r) in hist if s < p_sent), default=None)
    earliest = [min(s for s, _r in hist) for hist in cand_hists]
    first_sent = min(earliest)
    rec = np.zeros(n); subj = np.zeros(n); cb = np.zeros(n); freq = np.zeros(n)
    first = np.zeros(n); par = np.zeros(n); actr = np.zeros(n); foc = np.zeros(n)
    streak = np.zeros(n); win = np.zeros(n)
    for k, hist in enumerate(cand_hists):
        nearest = min(_dt(p_sent, s) for s, _r in hist)
        rec[k] = 1.0 / nearest
        subj[k] = max(ROLE_W.get(r, 1.0) for _s, r in hist)
        cb[k] = 1.0 if any(s == prev_sent and r == "SUBJECT" for s, r in hist) else 0.0
        freq[k] = math.log1p(len(hist))
        first[k] = 1.0 if earliest[k] == first_sent else 0.0
        last_role = max(hist, key=lambda sr: sr[0])[1]
        par[k] = 1.0 if last_role == pron_role else 0.0
        actr[k] = _actr(hist, p_sent, d)
        foc[k] = 1.0 if (focus_node is not None and cand_nodes[k] == focus_node) else 0.0
        # Cb-persistence / sustained-topichood: number of distinct clauses in which this node held the
        # SUBJECT (center) role -- Givon persistence / CONTINUE>RETAIN>SHIFT as a graded topichood bonus.
        # Distinct from freq (which counts ALL mentions incl. object/pronoun); this counts CENTERINGS only.
        streak[k] = float(len({s for s, r in hist if r == "SUBJECT" and s < p_sent}))
        win[k] = 1.0 if nearest <= W else 0.0     # soft active-set gate (down-weight, not delete)
    return {"recency": _zscore(rec), "subject": _zscore(subj), "cb": _zscore(cb), "freq": _zscore(freq),
            "first": _zscore(first), "parallel": _zscore(par), "actr": _zscore(actr),
            "focus": _zscore(foc), "streak": _zscore(streak), "window": _zscore(win)}


def combined_pred_binder(stream: List[dict], name_mode: str, weights: Dict[str, float], gaz: Dict[str, str],
                         d: float = DECAY_D, theta: float = 0.4, W: int = 999,
                         mode: str = "graded", rng: Optional[np.random.Generator] = None,
                         role_perm: Optional[Dict[int, str]] = None, agree: bool = False,
                         gender_perm: Optional[Dict[int, Optional[str]]] = None,
                         ng_map: Optional[Dict[int, Optional[str]]] = None,
                         drop_person: bool = False, active_k: Optional[int] = None) -> List[int]:
    """Assign every mention a predicted cluster id. NAMES cluster by name_mode (head|organ|gold); PRONOUNS
    bind by the FOCUS-DRIVEN graded net (mode='graded'), a random gn-compatible candidate (mode='rand'),
    or the hard strict-Cb pick (mode='strictcb'). Maintains a persistent Cb_current focus register.

    agree: infer NAME-node gender from the given-name gazetteer so the agreement pre-filter can exclude
    wrong-gender entities from a pronoun's candidate pool (a hard morphosyntactic constraint the live
    harness binder LACKS -- name nodes are gender-None, so a 'he' competes against every named entity).
    role_perm / gender_perm: optional {global index -> shuffled role/gender} info-free twins that destroy
    the tracked role/Cb signal (role_perm) or the inferred name-gender agreement signal (gender_perm)."""
    nodes: List[dict] = []
    gold2node: dict = {}
    pred = [-1] * len(stream)
    focus_node: Optional[int] = None      # Cb_current: node of the most recent SUBJECT mention seen so far
    for i, m in enumerate(stream):
        ht = m["head_text"].lower()
        role = role_perm[i] if role_perm is not None else m["role"]
        if ht in PRONOUNS:
            pg, pn = PRONOUNS[ht]
            cand = [j for j, nd in enumerate(nodes)
                    if nd["hist"] and _gn_compat(pg, pn, nd["gender"], nd["number"])]
            # Drill-B coverage-independent candidate filters (down-weight-not-delete kept via focus_node
            # rescue): (1) person-exclusion -- drop 1st/2nd-person artifact nodes; (2) active-set window --
            # keep only nodes with a mention within active_k sentences OR the standing focus (Centering Cf).
            if drop_person and len(cand) > 1:
                keep = [j for j in cand if not (nodes[j]["toks"]
                        and nodes[j]["toks"] <= ARTIFACT_PERSON)]
                if keep:
                    cand = keep
            if active_k is not None and len(cand) > 1:
                keep = [j for j in cand
                        if j == focus_node or (m["sent"] - max(s for s, _r in nodes[j]["hist"])) <= active_k]
                if keep:
                    cand = keep
            if not cand:
                nodes.append(_new_node(gender=pg, number=pn, hist=[(m["sent"], role)]))
                j = len(nodes) - 1
            else:
                if mode == "rand":
                    j = cand[int(rng.integers(0, len(cand)))]
                elif mode == "strictcb":
                    j = _strict_cb_pick(cand, nodes, m["sent"])
                else:
                    hists = [nodes[c]["hist"] for c in cand]
                    sup = _cue_supports(hists, cand, m["sent"], role, focus_node, d, W)
                    net = net_activation(sup, weights)
                    j = cand[int(np.argmax(net))]
                nodes[j]["hist"].append((m["sent"], role))
                if nodes[j]["gender"] is None:
                    nodes[j]["gender"] = pg
                if nodes[j]["number"] is None:
                    nodes[j]["number"] = pn
            pred[i] = j
        else:
            j = _assign_name(m, nodes, gold2node, name_mode, gaz, theta, use_gender=(name_mode == "organ"))
            nodes[j]["hist"].append((m["sent"], role))
            if agree and nodes[j]["gender"] is None:
                if gender_perm is not None:
                    fg = gender_perm.get(i)
                elif ng_map is not None:
                    fg = ng_map.get(i)
                else:
                    fg = _name_gender(m["span_tokens"], gaz)
                if fg:
                    nodes[j]["gender"] = fg
            pred[i] = j
        if role == "SUBJECT":
            focus_node = pred[i]           # update the standing focus after a subject mention
    return pred


def _strict_cb_pick(cand: List[int], nodes: List[dict], p_sent: int) -> int:
    """Hard literal-Centering pick (hdlab _pick_strict_cb port): argmax over most-recent SUBJECT sentence
    < p_sent, ties broken by pure recency (nearest mention)."""
    def key(j):
        hist = nodes[j]["hist"]
        subj_sents = [s for s, r in hist if r == "SUBJECT" and s < p_sent]
        mrs = max(subj_sents) if subj_sents else -1
        nearest = min(_dt(p_sent, s) for s, _r in hist)
        return (mrs, -nearest)
    return max(cand, key=key)


# --------------------------------------------------------------------------- scoring helper
def _pron_full(stream, pred) -> Tuple[int, int, int, int]:
    res = _score_direct(stream, pred)
    pc = sum(1 for isp, ok in res if isp and ok); pn = sum(1 for isp, ok in res if isp)
    fc = sum(1 for _, ok in res if ok); fn = len(res)
    return pc, pn, fc, fn


def _role_perm_for_doc(stream, rng) -> Dict[int, str]:
    """Shuffle the clause_role labels across ALL mentions in the doc (info-free clause_role twin)."""
    roles = [m["role"] for m in stream]
    perm = rng.permutation(len(roles))
    return {i: roles[perm[i]] for i in range(len(roles))}


# --------------------------------------------------------------------------- DEV tuning
def _ngmap(stream, gaz) -> Dict[int, Optional[str]]:
    """Precompute inferred name-gender per mention index (once) so tuning does not re-parse names."""
    out = {}
    for i, m in enumerate(stream):
        if m["head_text"].lower() not in PRONOUNS:
            g = _name_gender(m["span_tokens"], gaz)
            if g:
                out[i] = g
    return out


def _dev_pron_acc(dev_data, name_mode, weights, gaz, d, W, agree, ngmaps) -> float:
    c = t = 0
    for rec, ng in zip(dev_data, ngmaps):
        pred = combined_pred_binder(rec["stream"], name_mode, weights, gaz, d, W=W, mode="graded",
                                    agree=agree, ng_map=ng)
        pc, pn, _fc, _fn = _pron_full(rec["stream"], pred)
        c += pc; t += pn
    return c / t if t else 0.0


def tune_binder(dev_data, name_mode, gaz, agree: bool = True,
                ngmaps=None) -> Tuple[Dict[str, float], float, int]:
    """Coordinate-ascent over cue weights + ACT-R decay d + focus-window W on DEV who-did-what
    pronoun-query accuracy. Initialized at pure ACT-R (w_actr=1, rest 0), so the search SUBSUMES the
    incumbent -- the graded binder cannot do worse than ACT-R on DEV by construction. Deterministic."""
    if ngmaps is None:
        ngmaps = [_ngmap(rec["stream"], gaz) for rec in dev_data]
    weights = {c: 0.0 for c in CUES}
    weights["actr"] = 1.0
    d = DECAY_D
    W = 999
    best = _dev_pron_acc(dev_data, name_mode, weights, gaz, d, W, agree, ngmaps)
    for _sweep in range(TUNE_SWEEPS):
        improved = False
        for c in CUES:
            base = weights[c]; bestw = base
            for w in WGRID:
                weights[c] = w
                a = _dev_pron_acc(dev_data, name_mode, weights, gaz, d, W, agree, ngmaps)
                if a > best + 1e-9:
                    best, bestw, improved = a, w, True
            weights[c] = bestw
        for dv in D_GRID:
            a = _dev_pron_acc(dev_data, name_mode, weights, gaz, dv, W, agree, ngmaps)
            if a > best + 1e-9:
                best, d, improved = a, dv, True
        for wv in W_GRID:
            a = _dev_pron_acc(dev_data, name_mode, weights, gaz, d, wv, agree, ngmaps)
            if a > best + 1e-9:
                best, W, improved = a, wv, True
        if not improved:
            break
    return weights, d, W


def _gender_perm_for_doc(stream, gaz, rng) -> Dict[int, Optional[str]]:
    """Shuffle the INFERRED name genders across name mentions (info-free agreement twin): keeps the SAME
    multiset of inferred genders but detaches each from its entity -> destroys the agreement signal."""
    idx = [i for i, m in enumerate(stream) if m["head_text"].lower() not in PRONOUNS]
    gends = [_name_gender(stream[i]["span_tokens"], gaz) for i in idx]
    perm = rng.permutation(len(gends))
    return {idx[k]: gends[perm[k]] for k in range(len(idx))}


# --------------------------------------------------------------------------- bootstrap
def _ci(pairs, n_boot, seed):
    arr = np.array(pairs, float); tot = arr[:, 1].sum()
    acc = arr[:, 0].sum() / tot if tot else 0.0
    r = np.random.default_rng(seed); nd = len(arr); boots = []
    for _ in range(n_boot):
        idx = r.integers(0, nd, nd); c, n = arr[idx, 0].sum(), arr[idx, 1].sum()
        boots.append(c / n if n else 0.0)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {"acc": round(acc, 4), "lo": round(float(lo), 4), "hi": round(float(hi), 4), "n": int(tot)}


def _paired(a_map, b_map, n_boot, seed):
    docs = sorted(set(a_map) & set(b_map))
    a = np.array([a_map[dd] for dd in docs], float); b = np.array([b_map[dd] for dd in docs], float)
    delta = a[:, 0].sum() / max(a[:, 1].sum(), 1) - b[:, 0].sum() / max(b[:, 1].sum(), 1)
    r = np.random.default_rng(seed); nd = len(docs); boots = []
    for _ in range(n_boot):
        idx = r.integers(0, nd, nd)
        boots.append(a[idx, 0].sum() / max(a[idx, 1].sum(), 1) - b[idx, 0].sum() / max(b[idx, 1].sum(), 1))
    boots = np.array(boots); lo, hi = np.percentile(boots, [2.5, 97.5])
    return {"delta": round(float(delta), 4), "lo": round(float(lo), 4), "hi": round(float(hi), 4),
            "half_width": round(float(hi - lo) / 2, 4),
            "null_p95": round(float(np.percentile(np.abs(boots - boots.mean()), 95)), 4),
            "band": "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEP")}


# --------------------------------------------------------------------------- top-level cell
def cell(docs: Optional[int] = None, n_boot: int = 2000, seed: int = SEED, name_mode: str = "head",
         split_seed: Optional[int] = None) -> dict:
    gaz = load_given_gazetteer()
    data = load_enriched(docs)
    order = list(range(len(data)))
    if split_seed is not None:
        np.random.default_rng(split_seed).shuffle(order)   # robustness: alternate DEV/TEST partition
    dev_idx = set(order[0::2])
    dev = [rec for i, rec in enumerate(data) if i in dev_idx]
    test = [rec for i, rec in enumerate(data) if i not in dev_idx]
    dev_ng = [_ngmap(rec["stream"], gaz) for rec in dev]
    test_ng = [_ngmap(rec["stream"], gaz) for rec in test]
    # tune the full brain-faithful binder (graded cues + gender agreement) on DEV who-did-what
    weights, d, W = tune_binder(dev, name_mode, gaz, agree=True, ngmaps=dev_ng)

    arms = ("HEAD", "HEAD_GRADED", "HEAD_GRADED_AGREE", "HEAD_OPB",
            "HEAD_GRADED_SHUFROLE", "HEAD_AGREE_SHUFGENDER", "HEAD_RANDBIND")
    pron = {a: {} for a in arms}
    full = {a: {} for a in arms}
    for di, rec in enumerate(test):
        stream = rec["stream"]; doc = rec["doc"]; rng = np.random.default_rng(seed + di); ng = test_ng[di]
        preds = {
            "HEAD": combined_pred(stream, "HEAD", gaz, d, 0.4, rng),          # incumbent ACT-R, no agreement
            "HEAD_OPB": combined_pred(stream, "HEAD_OPB", gaz, d, 0.4, rng),  # perfect-binding ceiling
            "HEAD_GRADED": combined_pred_binder(stream, name_mode, weights, gaz, d, W=W, mode="graded",
                                                agree=False),                # brief's cue lever alone
            "HEAD_GRADED_AGREE": combined_pred_binder(stream, name_mode, weights, gaz, d, W=W, mode="graded",
                                                      agree=True, ng_map=ng),  # full brain-faithful binder
            "HEAD_RANDBIND": combined_pred_binder(stream, name_mode, weights, gaz, d, W=W, mode="rand",
                                                  agree=True, ng_map=ng,
                                                  rng=np.random.default_rng(seed + 1000 + di)),
            "HEAD_GRADED_SHUFROLE": combined_pred_binder(
                stream, name_mode, weights, gaz, d, W=W, mode="graded", agree=True, ng_map=ng,
                role_perm=_role_perm_for_doc(stream, np.random.default_rng(seed + 2000 + di))),
            "HEAD_AGREE_SHUFGENDER": combined_pred_binder(
                stream, name_mode, weights, gaz, d, W=W, mode="graded", agree=True,
                gender_perm=_gender_perm_for_doc(stream, gaz, np.random.default_rng(seed + 3000 + di))),
        }
        for a in arms:
            pc, pn, fc, fn = _pron_full(stream, preds[a])
            pron[a][doc] = (pc, pn); full[a][doc] = (fc, fn)

    acc_p = {a: _ci(list(pron[a].values()), n_boot, seed + 10 + i) for i, a in enumerate(arms)}
    acc_f = {a: _ci(list(full[a].values()), n_boot, seed + 30 + i) for i, a in enumerate(arms)}
    head = acc_p["HEAD"]["acc"]; ceil = acc_p["HEAD_OPB"]["acc"]
    best = acc_p["HEAD_GRADED_AGREE"]["acc"]
    frac = (best - head) / (ceil - head) if ceil > head else 0.0
    contrasts = {
        # the brief's Cb/clause_role cue lever ALONE (graded cues, no agreement) vs the ACT-R incumbent
        "GRADED_over_HEAD_pron": _paired(pron["HEAD_GRADED"], pron["HEAD"], n_boot, seed + 50),
        # the full brain-faithful binder (graded cues + gender agreement) vs the incumbent
        "GRADED_AGREE_over_HEAD_pron": _paired(pron["HEAD_GRADED_AGREE"], pron["HEAD"], n_boot, seed + 51),
        # isolate the AGREEMENT contribution (agree vs no-agree, same cues)
        "AGREE_contribution_pron": _paired(pron["HEAD_GRADED_AGREE"], pron["HEAD_GRADED"], n_boot, seed + 52),
        # info-free twins (must LOSE)
        "GRADED_AGREE_over_SHUFROLE_twin_pron": _paired(pron["HEAD_GRADED_AGREE"],
                                                        pron["HEAD_GRADED_SHUFROLE"], n_boot, seed + 53),
        "GRADED_AGREE_over_SHUFGENDER_twin_pron": _paired(pron["HEAD_GRADED_AGREE"],
                                                          pron["HEAD_AGREE_SHUFGENDER"], n_boot, seed + 54),
        "GRADED_AGREE_over_RANDBIND_twin_pron": _paired(pron["HEAD_GRADED_AGREE"],
                                                        pron["HEAD_RANDBIND"], n_boot, seed + 55),
        "OPB_over_GRADED_AGREE_residual_pron": _paired(pron["HEAD_OPB"], pron["HEAD_GRADED_AGREE"],
                                                       n_boot, seed + 56),
    }
    # PRIMARY claim = the brief's mechanism: the graded Cb/clause_role binder lifts who-did-what over the
    # ACT-R incumbent, with the clause_role-SHUFFLE twin (destroys the tracked Cb/subject signal) and the
    # RANDOM-binding twin both LOSING. (The shuffle-GENDER twin is a secondary control for the agreement
    # add-on and is coverage-limited on this archaic corpus, so it does not gate the primary verdict.)
    cue_lever = contrasts["GRADED_over_HEAD_pron"]["band"]
    role_twin_loses = contrasts["GRADED_AGREE_over_SHUFROLE_twin_pron"]["band"] == "ABOVE"
    rand_twin_loses = contrasts["GRADED_AGREE_over_RANDBIND_twin_pron"]["band"] == "ABOVE"
    verdict = ("BINDER_LIFTS_WHODIDWHAT_CI_SEP_TWINS_LOSE"
               if (cue_lever == "ABOVE" and role_twin_loses and rand_twin_loses)
               else "NULL_OR_UNCONTROLLED")
    return {
        "anchor": "coref_graded_binder_serves_whodidwhat_v1",
        "population": "LitBank pronoun-query who-did-what (TEST docs); direct symbolic decode; name_mode=" + name_mode,
        "n_test_docs": len(test), "n_dev_docs": len(dev),
        "tuned_weights": {k: round(v, 3) for k, v in weights.items()}, "tuned_actr_d": d, "tuned_window_W": W,
        "accuracy_pronoun_TEST": acc_p, "accuracy_full_TEST": acc_f,
        "floor_HEAD": head, "ceiling_HEAD_OPB": ceil, "graded_no_agree": acc_p["HEAD_GRADED"]["acc"],
        "graded_agree_best": best, "fraction_of_headroom_recovered": round(float(frac), 4),
        "brief_Cb_cue_lever_alone_band": cue_lever,
        "contrasts_TEST": contrasts, "verdict": verdict,
    }


# --------------------------------------------------------------------------- RE-INSTRUMENTED decode
# The live who-did-what metric scores "most-common verb per (entity, sentence)" -- a lossy aggregation
# that discards all but one event when an entity does several things in a clause (NOT how the brain's
# situation model works: it stores ALL (entity, event) bindings; Zwaan-Radvansky event indexing). This
# re-instrumentation reads out the SITUATION-MODEL EVENT SET: is the queried (sentence, verb) event bound
# to the entity's cluster? -> the faithful readout, and it removes the decode-collapse ceiling.
def _score_event_set(stream: List[dict], pred: List[int]) -> tuple:
    """Situation-model event-set readout. Returns (pron_recall_correct, pron_total, tp, fp, fn):
    pron_recall = for each PRONOUN query (gold g, sent s, verb v), is (s,v) in g's anchor cluster's event
    set? (comparable to the 0.161 headline). tp/fp/fn = micro precision/recall over ALL named-entity
    (sent,verb) events (predicted cluster events vs gold entity events) -> penalizes BOTH mis-bound-away
    (fn) and polluting mis-bindings (fp), so it is not merely a lenient recall."""
    reg: Dict[int, set] = defaultdict(set)
    for m, cid in zip(stream, pred):
        if m["gov_verb"] is not None:
            reg[cid].add((m["sent"], m["gov_verb"]))
    anchor: Dict[int, list] = {}
    for m, cid in zip(stream, pred):
        g = m["gold"]; is_p = m["head_text"].lower() in PRONOUNS
        if g not in anchor:
            anchor[g] = [cid, is_p]
        elif anchor[g][1] and not is_p:
            anchor[g] = [cid, False]
    anchor = {g: cid for g, (cid, _) in anchor.items()}
    has_name = {m["gold"] for m in stream if m["head_text"].lower() not in PRONOUNS}
    gold_ev: Dict[int, set] = defaultdict(set)
    for m in stream:
        if m["gov_verb"] is not None and m["gold"] in has_name:
            gold_ev[m["gold"]].add((m["sent"], m["gov_verb"]))
    pc = pn = 0
    for m in stream:
        v = m["gov_verb"]
        if v is None or m["gold"] not in has_name or m["head_text"].lower() not in PRONOUNS:
            continue
        pn += 1
        pset = reg.get(anchor.get(m["gold"]), set())
        pc += int((m["sent"], v) in pset)
    tp = fp = fn = 0
    for g, gset in gold_ev.items():
        pset = reg.get(anchor.get(g), set())
        tp += len(gset & pset); fn += len(gset - pset); fp += len(pset - gset)
    return pc, pn, tp, fp, fn


def reinstrument(docs: Optional[int] = None, n_boot: int = 2000, seed: int = SEED,
                 name_mode: str = "head") -> dict:
    """PROVE that the 0.606 perfect-binding ceiling is a METRIC ARTIFACT of the most-common-verb-per-
    sentence collapse, by re-scoring the SAME arms under the situation-model event-set readout. Shows the
    ceiling jumps toward 1.0 and re-measures the binder lift + info-free twin under the faithful metric."""
    gaz = load_given_gazetteer()
    data = load_enriched(docs)
    dev_idx = set(range(0, len(data), 2))
    dev = [rec for i, rec in enumerate(data) if i in dev_idx]
    test = [rec for i, rec in enumerate(data) if i not in dev_idx]
    dev_ng = [_ngmap(rec["stream"], gaz) for rec in dev]
    weights, d, W = tune_binder(dev, name_mode, gaz, agree=True, ngmaps=dev_ng)
    test_ng = [_ngmap(rec["stream"], gaz) for rec in test]

    arms = ("HEAD", "HEAD_GRADED_AGREE", "HEAD_OPB", "HEAD_RANDBIND")
    old = {a: {} for a in arms}                 # live most-common-verb-per-sentence metric (pron)
    newp = {a: {} for a in arms}                # re-instrumented event-set pron-recall
    f1acc = {a: [0, 0, 0] for a in arms}        # micro tp, fp, fn for F1
    for di, rec in enumerate(test):
        stream = rec["stream"]; doc = rec["doc"]; rng = np.random.default_rng(seed + di); ng = test_ng[di]
        preds = {
            "HEAD": combined_pred(stream, "HEAD", gaz, d, 0.4, rng),
            "HEAD_OPB": combined_pred(stream, "HEAD_OPB", gaz, d, 0.4, rng),
            "HEAD_GRADED_AGREE": combined_pred_binder(stream, name_mode, weights, gaz, d, W=W,
                                                      mode="graded", agree=True, ng_map=ng),
            "HEAD_RANDBIND": combined_pred_binder(stream, name_mode, weights, gaz, d, W=W, mode="rand",
                                                  agree=True, ng_map=ng,
                                                  rng=np.random.default_rng(seed + 1000 + di)),
        }
        for a in arms:
            pc, pn, fc, fn = _pron_full(stream, preds[a])        # OLD metric (pron)
            old[a][doc] = (pc, pn)
            rc, rn, tp, fp, fnn = _score_event_set(stream, preds[a])
            newp[a][doc] = (rc, rn)
            f1acc[a][0] += tp; f1acc[a][1] += fp; f1acc[a][2] += fnn

    def f1(a):
        tp, fp, fn = f1acc[a]
        p = tp / (tp + fp) if tp + fp else 0.0
        r = tp / (tp + fn) if tp + fn else 0.0
        return {"precision": round(p, 4), "recall": round(r, 4),
                "f1": round(2 * p * r / (p + r), 4) if p + r else 0.0}
    acc_old = {a: _ci(list(old[a].values()), n_boot, seed + 10 + i) for i, a in enumerate(arms)}
    acc_new = {a: _ci(list(newp[a].values()), n_boot, seed + 20 + i) for i, a in enumerate(arms)}
    return {
        "anchor": "coref_reinstrument_whodidwhat_v1",
        "population": "LitBank pronoun-query who-did-what (TEST, even/odd split); name_mode=" + name_mode,
        "n_test_docs": len(test),
        "OLD_metric_most_common_verb_per_sentence": {a: acc_old[a]["acc"] for a in arms},
        "NEW_metric_situation_model_event_set_pron_recall": {a: acc_new[a]["acc"] for a in arms},
        "NEW_metric_pron_recall_CI": acc_new,
        "NEW_metric_entity_event_micro_F1": {a: f1(a) for a in arms},
        "ceiling_OLD_HEAD_OPB": acc_old["HEAD_OPB"]["acc"],
        "ceiling_NEW_HEAD_OPB": acc_new["HEAD_OPB"]["acc"],
        "binder_lift_NEW": _paired(newp["HEAD_GRADED_AGREE"], newp["HEAD"], n_boot, seed + 60),
        "binder_over_randtwin_NEW": _paired(newp["HEAD_GRADED_AGREE"], newp["HEAD_RANDBIND"], n_boot, seed + 61),
        "note": ("if ceiling_NEW >> ceiling_OLD (~0.61), the perfect-binding ceiling was a METRIC ARTIFACT "
                 "of the per-sentence most-common-verb collapse; the faithful situation-model event-set "
                 "readout removes it, and the binder's real headroom (0.23 -> ~1.0) opens up."),
    }


# --------------------------------------------------------------------------- Drill-B candidate levers
def measure_levers(docs: Optional[int] = None, n_boot: int = 2000, seed: int = SEED,
                   name_mode: str = "head", active_k: int = 3) -> dict:
    """Test Drill-B's coverage-independent candidate levers (person-exclusion + active-set window) composed
    with the graded+agreement binder, under BOTH the live metric and the re-instrumented event-set metric.
    These attack the 'competes against every entity' bottleneck directly (Centering Cf; the sibling's +2.2
    person-cleanup), independent of gender coverage."""
    gaz = load_given_gazetteer()
    data = load_enriched(docs)
    dev = [rec for i, rec in enumerate(data) if i % 2 == 0]
    test = [rec for i, rec in enumerate(data) if i % 2 == 1]
    dev_ng = [_ngmap(rec["stream"], gaz) for rec in dev]
    test_ng = [_ngmap(rec["stream"], gaz) for rec in test]
    weights, d, W = tune_binder(dev, name_mode, gaz, agree=True, ngmaps=dev_ng)

    def binder(stream, ng, **kw):
        return combined_pred_binder(stream, name_mode, weights, gaz, d, W=W, mode="graded", agree=True,
                                    ng_map=ng, **kw)
    arms = ("HEAD", "BINDER", "BINDER_person", "BINDER_active", "BINDER_both", "HEAD_OPB", "RANDBIND")
    oldm = {a: {} for a in arms}; newm = {a: {} for a in arms}
    for di, rec in enumerate(test):
        stream = rec["stream"]; doc = rec["doc"]; rng = np.random.default_rng(seed + di); ng = test_ng[di]
        preds = {
            "HEAD": combined_pred(stream, "HEAD", gaz, d, 0.4, rng),
            "HEAD_OPB": combined_pred(stream, "HEAD_OPB", gaz, d, 0.4, rng),
            "BINDER": binder(stream, ng),
            "BINDER_person": binder(stream, ng, drop_person=True),
            "BINDER_active": binder(stream, ng, active_k=active_k),
            "BINDER_both": binder(stream, ng, drop_person=True, active_k=active_k),
            "RANDBIND": combined_pred_binder(stream, name_mode, weights, gaz, d, W=W, mode="rand",
                                             agree=True, ng_map=ng, rng=np.random.default_rng(seed + 1000 + di)),
        }
        for a in arms:
            pc, pn, _fc, _fn = _pron_full(stream, preds[a]); oldm[a][doc] = (pc, pn)
            rc, rn, _tp, _fp, _fn2 = _score_event_set(stream, preds[a]); newm[a][doc] = (rc, rn)
    acc_old = {a: _ci(list(oldm[a].values()), n_boot, seed + i)["acc"] for i, a in enumerate(arms)}
    acc_new = {a: _ci(list(newm[a].values()), n_boot, seed + 20 + i)["acc"] for i, a in enumerate(arms)}
    contrasts = {
        "person_over_binder_OLD": _paired(oldm["BINDER_person"], oldm["BINDER"], n_boot, seed + 50),
        "active_over_binder_OLD": _paired(oldm["BINDER_active"], oldm["BINDER"], n_boot, seed + 51),
        "both_over_binder_OLD": _paired(oldm["BINDER_both"], oldm["BINDER"], n_boot, seed + 52),
        "both_over_HEAD_OLD": _paired(oldm["BINDER_both"], oldm["HEAD"], n_boot, seed + 53),
        "both_over_binder_NEW": _paired(newm["BINDER_both"], newm["BINDER"], n_boot, seed + 54),
        "both_over_HEAD_NEW": _paired(newm["BINDER_both"], newm["HEAD"], n_boot, seed + 55),
        "both_over_RANDBIND_NEW": _paired(newm["BINDER_both"], newm["RANDBIND"], n_boot, seed + 56),
    }
    return {
        "anchor": "coref_binder_candidate_levers_v1", "active_k": active_k,
        "tuned_weights": {k: round(v, 3) for k, v in weights.items()},
        "accuracy_OLD_metric": acc_old, "accuracy_NEW_metric_eventset": acc_new,
        "contrasts": contrasts,
        "note": "person-exclusion + active-set window composed with the graded+agreement binder; NEW metric "
                "is the situation-model event-set readout (ceiling 1.0).",
    }


# --------------------------------------------------------------------------- positive control
def positive_control() -> dict:
    """Cb-decisive constructed stream: the sustained SUBJECT topic (gold) acts via a pronoun, but a
    MORE-RECENT OBJECT distractor of the same gender intervenes. ACT-R (recency-weighted) is pulled to the
    recent object; the focus-driven graded binder holds the Cb. The metric CAN move."""
    gaz = {"john": "masc", "mark": "masc"}
    # John is the discourse CENTER (subject/topic, sent 0). Mark intervenes as a MORE-RECENT OBJECT
    # (sent 3, same gender). "he" (sent 4, leave) binds to John, the grammatical center -- NOT the recent
    # object. ACT-R over-weights the recent object Mark (dt=1, obj) over the older subject John (dt=4) and
    # MISPICKS; the subject/Cb/focus cues hold the center. Gold anchor for John = his name cluster.
    stream = [
        {"head_text": "john", "span_tokens": ["John"], "gold": 0, "sent": 0, "start": 0, "role": "SUBJECT", "gov_verb": "enter", "ent_type": "PER"},
        {"head_text": "mark", "span_tokens": ["Mark"], "gold": 1, "sent": 3, "start": 3, "role": "OBJECT", "gov_verb": "greet", "ent_type": "PER"},
        {"head_text": "he", "span_tokens": ["he"], "gold": 0, "sent": 4, "start": 0, "role": "SUBJECT", "gov_verb": "leave", "ent_type": "PER"},
    ]
    w = {c: 0.0 for c in CUES}
    w.update({"actr": 0.5, "subject": 1.0, "cb": 2.0, "focus": 2.0, "streak": 1.0})
    pred_g = combined_pred_binder(stream, "head", w, gaz, DECAY_D, W=999, mode="graded")
    pred_a = combined_pred(stream, "HEAD", gaz, DECAY_D, 0.4, np.random.default_rng(0))
    g_ok = bool(_pron_full(stream, pred_g)[0])
    a_ok = bool(_pron_full(stream, pred_a)[0])
    return {"graded_binds_Cb_correct": g_ok, "actr_binds_Cb_correct": a_ok,
            "metric_can_move": g_ok and not a_ok}


# --------------------------------------------------------------------------- self-test
def self_test():
    # Cue geometry: a sustained subject (Cb) must outscore a more-recent object on subject/cb/focus cues.
    hists = [[(0, "SUBJECT"), (2, "SUBJECT")], [(3, "OBJECT")]]
    sup = _cue_supports(hists, [0, 1], 4, "SUBJECT", 0, 2.0, 999)
    assert sup["subject"][0] > sup["subject"][1], "sustained subject must win the subjecthood cue"
    assert sup["focus"][0] > sup["focus"][1], "the standing focus node must win the focus cue"
    assert sup["streak"][0] > sup["streak"][1], "the subject with a longer Cb streak must win the streak cue"
    # net_activation with a Cb-heavy weight must pick the sustained subject (index 0)
    w = {c: 0.0 for c in CUES}; w.update({"subject": 1.0, "cb": 2.0, "focus": 2.0})
    assert int(np.argmax(net_activation(sup, w))) == 0, "Cb-weighted net must pick the sustained subject"
    pc = positive_control()
    assert pc["graded_binds_Cb_correct"], "graded binder must bind the Cb-decisive pronoun correctly"
    assert pc["metric_can_move"], "positive control must MOVE (graded right where ACT-R is wrong)"
    print("SELF-TEST PASS (Cb/focus/streak cues fire; graded net picks the sustained topic; "
          "positive control moves).")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--positive-control", action="store_true", dest="pc")
    ap.add_argument("--reinstrument", action="store_true", dest="reinstrument")
    ap.add_argument("--levers", action="store_true", dest="levers")
    ap.add_argument("--docs", type=int, default=None)
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--split-seed", type=int, default=None, dest="split_seed")
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.pc:
        print(json.dumps(positive_control(), indent=2)); return
    if args.reinstrument:
        print(json.dumps(reinstrument(docs=args.docs, n_boot=args.n_boot), indent=2)); return
    if args.levers:
        print(json.dumps(measure_levers(docs=args.docs, n_boot=args.n_boot), indent=2)); return
    if args.run:
        print(json.dumps(cell(docs=args.docs, n_boot=args.n_boot, split_seed=args.split_seed), indent=2)); return
    print("use --self-test | --run [--docs N] | --positive-control")


if __name__ == "__main__":
    main()
