"""exp_name_clustering_serves_whodidwhat_v1 -- WIRE-DON'T-ISLAND: does the brain-faithful name/entity
clustering LIFT the downstream who-did-what decode toward the oracle-coref ceiling?

THE CHAIN (measured by the prior coref SOLVED): a pronoun bound CORRECTLY still cannot retrieve its
referent's actions when the referent's NAME mentions are SHATTERED across many predicted entities -- the
who-did-what decode sits at ~0.17 (commit/abstain/random alike) vs ORACLE-coref ~0.62. The pronoun LINK
is not the bottleneck; the NAME CLUSTERING is. This cell swaps the incumbent head-token name clustering
for the content-addressable complete-or-separate ORGAN (exp_name_entity_clustering_v1) and measures the
who-did-what lift, holding the pronoun binder (ACT-R, the just-integrated coref win) FIXED.

ARMS (identical mention stream, identical events, identical ACT-R pronoun binding; only NAME clustering
differs -> isolates the clustering contribution):
  HEAD          : name mentions cluster by head-token Jaccard (the LIVE incumbent _resolve_name_branch).
  ORGAN         : name mentions cluster by the person-node complete-or-separate organ (+ inferred gender).
  ORGAN_NOGENDER: the organ clustering with name-node gender withheld from the pronoun filter (ablation:
                  isolates the CLUSTERING channel from the gender-inference channel).
  ORACLE        : name AND pronoun = gold cluster (the CEILING).
  SHUF_NAME     : the organ's name-cluster ids PERMUTED among name mentions (info-free twin: correct
                  GROUPING destroyed, cluster-count preserved -> must collapse).

DECODE = a LINK-BOTTLENECKED direct symbolic register (per predicted cluster, slot->verb tally; no FHRR
capacity loss) -- isolates link/cluster correctness from the register fan effect (a separate problem).
METRIC = governing-verb decode accuracy on PRONOUN-contributed queries (only correct clustering makes the
event reachable) and the FULL set; bootstrap over DOCUMENTS.

Run: .venv/Scripts/python.exe experiments/exp_name_clustering_serves_whodidwhat_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_name_clustering_serves_whodidwhat_v1.py --run [--docs N]
GLASS-BOX, remote-safe (reads pre-parsed caches; NO spaCy, NO torch).
# KB_REFERENT: data/litbank/who_did_what_events.json
# KB_REFERENT: data/lexicons/name_gender_gazetteer.tsv
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections import Counter, defaultdict
from typing import Dict, List, Optional

import numpy as np

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments.exp_litbank_activation_binder_v1 import PRONOUNS, ROLE_W, _gn_compat, _dt  # noqa: E402
from experiments.exp_name_entity_clustering_v1 import (  # noqa: E402
    load_enriched, load_given_gazetteer, parse_name, STOP, SEED,
)

DECAY_D = 2.0
# arm -> (name_mode, pron_mode, use_gender). name_mode: head|organ|gold. pron_mode: actr|oracle|shuf.
ARM_SPEC = {
    "HEAD":            ("head",  "actr",   False),   # the LIVE incumbent
    "ORGAN":           ("organ", "actr",   True),    # organ name clustering + inferred gender
    "ORGAN_NOGENDER":  ("organ", "actr",   False),   # ablation: clustering only, no gender to pron filter
    "ORACLE":          ("gold",  "oracle", False),   # ceiling (gold names + gold pronouns)
    "GOLDNAME_ACTR":   ("gold",  "actr",   False),   # gold names + ACT-R pronouns -> ISOLATES pronoun-binding cost
    "HEAD_OPB":        ("head",  "oracle", False),   # head names + perfect pronoun binding -> name-clustering cost
    "ORGAN_OPB":       ("organ", "oracle", True),    # organ names + perfect pronoun binding
    "SHUF_NAME":       ("organ", "shuf",   True),    # info-free twin (name-cluster ids permuted)
}
ARMS = tuple(ARM_SPEC)
_G2MF = {"masc": "m", "fem": "f"}


def _actr(hist, p_sent, d):
    s = sum(ROLE_W.get(r, 1.0) * (_dt(p_sent, sent) ** (-d)) for sent, r in hist)
    return math.log(s) if s > 0 else -1e9


def _mf_conflict(a: Optional[str], b: Optional[str]) -> bool:
    return a is not None and b is not None and a != b


def _new_node(**kw):
    nd = {"given": set(), "surname": set(), "titles": set(), "gender": None, "number": "s",
          "toks": set(), "hist": []}
    nd.update(kw)
    return nd


def _assign_name(m: dict, nodes: List[dict], gold2node: dict, name_mode: str,
                 gaz: Dict[str, str], theta: float, use_gender: bool) -> int:
    """Assign one NAME (non-pronoun) mention to a cluster node; returns the node index."""
    if name_mode == "gold":
        g = m["gold"]
        if g not in gold2node:
            nodes.append(_new_node()); gold2node[g] = len(nodes) - 1
        return gold2node[g]
    if name_mode == "head":
        toks = {m["head_text"].lower()} - STOP - {""}
        best, bo = None, 0.0
        for j, nd in enumerate(nodes):
            if not nd["toks"] or not toks:
                continue
            ov = len(toks & nd["toks"]) / len(toks | nd["toks"])
            if ov > bo:
                bo, best = ov, j
        if best is not None and bo > 0.0:
            nodes[best]["toks"] |= toks; return best
        nodes.append(_new_node(toks=set(toks))); return len(nodes) - 1
    # organ
    f = parse_name(m["span_tokens"], gaz)
    gender = _G2MF.get(f["gender"]) if use_gender else None
    best, best_s = None, -1e9
    for j, nd in enumerate(nodes):
        if _mf_conflict(gender, nd["gender"]):
            continue
        given_match = bool(f["given"] & nd["given"])
        if f["given"] and nd["given"] and not given_match:
            continue   # given-name conflict -> separate
        surname_match = bool(f["surname"] & nd["surname"])
        tok_ov = (len(f["toks"] & nd["toks"]) / len(f["toks"] | nd["toks"])
                  if (f["toks"] and nd["toks"]) else 0.0)
        s = 1.0 * given_match + 0.5 * surname_match + 0.4 * tok_ov
        if given_match and surname_match:
            s += 0.5
        if s > best_s:
            best_s, best = s, j
    if (best is None or best_s < theta) and not f["proper"]:
        compat = [j for j, nd in enumerate(nodes) if not _mf_conflict(gender, nd["gender"])]
        if len(compat) == 1:
            best, best_s = compat[0], theta
    if best is not None and best_s >= theta:
        nd = nodes[best]
        nd["given"] |= f["given"]; nd["surname"] |= f["surname"]; nd["toks"] |= f["toks"]
        if nd["gender"] is None:
            nd["gender"] = gender
        return best
    nodes.append(_new_node(given=set(f["given"]), surname=set(f["surname"]),
                           gender=gender, toks=set(f["toks"])))
    return len(nodes) - 1


def combined_pred(stream: List[dict], arm: str, gaz: Dict[str, str], d: float = DECAY_D,
                  theta: float = 0.4, rng: Optional[np.random.Generator] = None) -> List[int]:
    """Assign every mention a predicted cluster id under (name_mode, pron_mode). NAMES cluster by
    name_mode (head|organ|gold); PRONOUNS bind by pron_mode (actr online | oracle=to their gold's name
    anchor | shuf=info-free)."""
    name_mode, pron_mode, use_gender = ARM_SPEC[arm]
    if pron_mode == "shuf":
        base = combined_pred(stream, "ORGAN", gaz, d, theta, rng)
        name_idx = [i for i, m in enumerate(stream) if m["head_text"].lower() not in PRONOUNS]
        vals = [base[i] for i in name_idx]
        perm = rng.permutation(len(vals))
        out = list(base)
        for k, i in enumerate(name_idx):
            out[i] = vals[perm[k]]
        return out
    nodes: List[dict] = []
    gold2node: dict = {}
    pred = [-1] * len(stream)
    if pron_mode == "actr":
        for i, m in enumerate(stream):
            ht = m["head_text"].lower(); role = m["role"]
            if ht in PRONOUNS:
                pg, pn = PRONOUNS[ht]
                compat = [j for j, nd in enumerate(nodes)
                          if nd["hist"] and _gn_compat(pg, pn, nd["gender"], nd["number"])]
                if not compat:
                    nodes.append(_new_node(gender=pg, number=pn, hist=[(m["sent"], role)]))
                    pred[i] = len(nodes) - 1
                else:
                    j = max(compat, key=lambda j: (_actr(nodes[j]["hist"], m["sent"], d), -j))
                    nodes[j]["hist"].append((m["sent"], role))
                    if nodes[j]["gender"] is None:
                        nodes[j]["gender"] = pg
                    if nodes[j]["number"] is None:
                        nodes[j]["number"] = pn
                    pred[i] = j
            else:
                j = _assign_name(m, nodes, gold2node, name_mode, gaz, theta, use_gender)
                nodes[j]["hist"].append((m["sent"], role)); pred[i] = j
        return pred
    # pron_mode == "oracle": cluster names first, then bind each pronoun to its GOLD's name anchor.
    for i, m in enumerate(stream):
        if m["head_text"].lower() in PRONOUNS:
            continue
        j = _assign_name(m, nodes, gold2node, name_mode, gaz, theta, use_gender)
        nodes[j]["hist"].append((m["sent"], m["role"])); pred[i] = j
    anchor: dict = {}
    for i, m in enumerate(stream):
        if pred[i] >= 0:
            anchor.setdefault(m["gold"], pred[i])
    next_new = len(nodes)
    for i, m in enumerate(stream):
        if m["head_text"].lower() in PRONOUNS:
            g = m["gold"]
            if g in anchor:
                pred[i] = anchor[g]
            else:
                pred[i] = next_new; next_new += 1
    return pred


def _score_direct(stream: List[dict], pred: List[int]) -> List[tuple]:
    """Direct symbolic register: per predicted cluster, slot(sent)->verb tally. Decode who-did-what for
    each mention with a gov_verb whose GOLD has a name anchor. Returns [(is_pron, ok)]."""
    reg: Dict[int, Dict[int, Counter]] = defaultdict(lambda: defaultdict(Counter))
    for m, cid in zip(stream, pred):
        v = m["gov_verb"]
        if v is None:
            continue
        reg[cid][m["sent"]][v] += 1
    # name anchor: gold -> predicted cluster of its first NAME mention (else first mention)
    anchor: Dict[int, tuple] = {}
    for m, cid in zip(stream, pred):
        g = m["gold"]; is_p = m["head_text"].lower() in PRONOUNS
        if g not in anchor:
            anchor[g] = (cid, is_p)
        elif anchor[g][1] and not is_p:
            anchor[g] = (cid, False)
    anchor = {g: cid for g, (cid, _) in anchor.items()}
    has_name = {m["gold"] for m in stream if m["head_text"].lower() not in PRONOUNS}
    out = []
    for m in stream:
        v = m["gov_verb"]
        if v is None or m["gold"] not in has_name:
            continue
        cid = anchor.get(m["gold"])
        ok = 0
        if cid is not None:
            slots = reg.get(cid)
            pv = slots[m["sent"]].most_common(1)[0][0] if (slots and m["sent"] in slots) else None
            ok = int(pv == v)
        out.append((m["head_text"].lower() in PRONOUNS, bool(ok)))
    return out


def _score_fhrr(stream, pred, backend, gen_seed):
    """Score who-did-what via the ACTUAL FHRR situation register (backend='flat' dense superposition vs
    'multibank' sparse sharded), holding clustering + binding fixed -> isolates the STORE as the lever."""
    from experiments.exp_litbank_entity_tracking_end_to_end_v1 import _slots, _torch_gen, D
    from hdlab.situation_model_accumulate import make_situation_register
    slot_map, n_slots = _slots(stream)
    verb_vocab = sorted({m["gov_verb"] for m in stream if m["gov_verb"] is not None})
    if not verb_vocab:
        return []
    gen = _torch_gen(gen_seed)
    reg = make_situation_register(list(verb_vocab), D, gen, max_event_slots=max(n_slots, 1),
                                  backend=backend, n_banks=8)
    for m, cid in zip(stream, pred):
        v = m["gov_verb"]
        if v is not None:
            reg.add_event(str(cid), v, slot_map[m["sent"]])
    anchor: Dict[int, tuple] = {}
    for m, cid in zip(stream, pred):
        g = m["gold"]; is_p = m["head_text"].lower() in PRONOUNS
        if g not in anchor:
            anchor[g] = (cid, is_p)
        elif anchor[g][1] and not is_p:
            anchor[g] = (cid, False)
    anchor = {g: cid for g, (cid, _) in anchor.items()}
    has_name = {m["gold"] for m in stream if m["head_text"].lower() not in PRONOUNS}
    out = []
    for m in stream:
        v = m["gov_verb"]
        if v is None or m["gold"] not in has_name:
            continue
        cid = anchor.get(m["gold"]); ok = 0
        if cid is not None:
            try:
                pv, _ = reg.decode(str(cid), slot_map[m["sent"]])
            except KeyError:
                pv = None
            ok = int(pv == v)
        out.append((m["head_text"].lower() in PRONOUNS, bool(ok)))
    return out


def prove_register(docs: Optional[int] = None, n_boot: int = 2000, theta: float = 0.4,
                   seed: int = SEED) -> dict:
    """PROVE the right solution: does swapping the FLAT FHRR register for the built sparse MULTIBANK register
    LIFT who-did-what, where better NAME CLUSTERING did not? Holds clustering + binding fixed, varies ONLY
    the store backend. ORACLE config isolates the register (gold names + gold pronouns); HEAD config is the
    live system (head-token names + ACT-R pronouns)."""
    gaz = load_given_gazetteer()
    data = load_enriched(docs)
    configs = ("ORACLE", "HEAD"); backends = ("flat", "multibank")
    per_doc = {(c, b): {"pron": [], "full": []} for c in configs for b in backends}
    for di, rec in enumerate(data):
        stream = rec["stream"]; rng = np.random.default_rng(seed + di)
        for c in configs:
            pred = combined_pred(stream, c, gaz, DECAY_D, theta, rng)
            for b in backends:
                res = _score_fhrr(stream, pred, b, seed + di)   # same vectors both backends (fair)
                pc = sum(1 for isp, ok in res if isp and ok); pn = sum(1 for isp, ok in res if isp)
                fc = sum(1 for _, ok in res if ok); fn = len(res)
                per_doc[(c, b)]["pron"].append((pc, pn)); per_doc[(c, b)]["full"].append((fc, fn))

    def ci(key, s):
        arr = np.array(per_doc[key]["pron"], float); tot = arr[:, 1].sum()
        acc = arr[:, 0].sum() / tot if tot else 0.0
        r = np.random.default_rng(s); nd = len(arr); boots = []
        for _ in range(n_boot):
            idx = r.integers(0, nd, nd); c, n = arr[idx, 0].sum(), arr[idx, 1].sum()
            boots.append(c / n if n else 0.0)
        lo, hi = np.percentile(boots, [2.5, 97.5])
        return {"acc": round(acc, 4), "lo": round(float(lo), 4), "hi": round(float(hi), 4), "n": int(tot)}

    def paired(mb, fl, s):
        A = np.array(per_doc[mb]["pron"], float); B = np.array(per_doc[fl]["pron"], float)
        r = np.random.default_rng(s); nd = len(A); boots = []
        for _ in range(n_boot):
            idx = r.integers(0, nd, nd)
            boots.append(A[idx, 0].sum() / max(A[idx, 1].sum(), 1) - B[idx, 0].sum() / max(B[idx, 1].sum(), 1))
        boots = np.array(boots); lo, hi = np.percentile(boots, [2.5, 97.5])
        return {"delta": round(float(A[:, 0].sum() / max(A[:, 1].sum(), 1) - B[:, 0].sum() / max(B[:, 1].sum(), 1)), 4),
                "lo": round(float(lo), 4), "hi": round(float(hi), 4), "hw": round(float(hi - lo) / 2, 4),
                "band": "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEP")}

    return {
        "anchor": "prove_register_lever_v1",
        "question": "does the built sparse MultiBankRegister LIFT who-did-what over the flat register? (the real fix)",
        "accuracy_pronoun": {f"{c}/{b}": ci((c, b), seed + i) for i, (c, b) in
                             enumerate((c, b) for c in configs for b in backends)},
        "multibank_over_flat_ORACLE": paired(("ORACLE", "multibank"), ("ORACLE", "flat"), seed + 50),
        "multibank_over_flat_HEAD": paired(("HEAD", "multibank"), ("HEAD", "flat"), seed + 51),
    }


def cell(docs: Optional[int] = None, n_boot: int = 2000, theta: float = 0.4, seed: int = SEED) -> dict:
    gaz = load_given_gazetteer()
    data = load_enriched(docs)
    per_doc = {a: {"pron": [], "full": []} for a in ARMS}
    for di, rec in enumerate(data):
        stream = rec["stream"]
        rng = np.random.default_rng(seed + di)
        for a in ARMS:
            pred = combined_pred(stream, a, gaz, DECAY_D, theta, rng)
            res = _score_direct(stream, pred)
            pc = sum(1 for isp, ok in res if isp and ok); pn = sum(1 for isp, ok in res if isp)
            fc = sum(1 for _, ok in res if ok); fn = len(res)
            per_doc[a]["pron"].append((pc, pn)); per_doc[a]["full"].append((fc, fn))

    def ci(pairs, s):
        arr = np.array(pairs, float); tot = arr[:, 1].sum()
        acc = arr[:, 0].sum() / tot if tot else 0.0
        r = np.random.default_rng(s); nd = len(arr); boots = []
        for _ in range(n_boot):
            idx = r.integers(0, nd, nd); c, n = arr[idx, 0].sum(), arr[idx, 1].sum()
            boots.append(c / n if n else 0.0)
        lo, hi = np.percentile(boots, [2.5, 97.5])
        return {"acc": round(acc, 4), "lo": round(float(lo), 4), "hi": round(float(hi), 4), "n": int(tot)}

    def paired(a, b, s):
        A = np.array(per_doc[a]["pron"], float); B = np.array(per_doc[b]["pron"], float)
        r = np.random.default_rng(s); nd = len(A); boots = []
        for _ in range(n_boot):
            idx = r.integers(0, nd, nd)
            boots.append(A[idx, 0].sum() / max(A[idx, 1].sum(), 1) - B[idx, 0].sum() / max(B[idx, 1].sum(), 1))
        boots = np.array(boots); lo, hi = np.percentile(boots, [2.5, 97.5])
        delta = A[:, 0].sum() / max(A[:, 1].sum(), 1) - B[:, 0].sum() / max(B[:, 1].sum(), 1)
        return {"delta": round(float(delta), 4), "lo": round(float(lo), 4), "hi": round(float(hi), 4),
                "hw": round(float(hi - lo) / 2, 4),
                "null_p95": round(float(np.percentile(np.abs(boots - boots.mean()), 95)), 4),
                "band": "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEP")}

    return {
        "anchor": "name_clustering_serves_whodidwhat_v1",
        "decode": "direct symbolic (link-bottlenecked)", "theta": theta, "n_docs": len(data),
        "accuracy_pronoun": {a: ci(per_doc[a]["pron"], seed + i) for i, a in enumerate(ARMS)},
        "accuracy_full": {a: ci(per_doc[a]["full"], seed + 10 + i) for i, a in enumerate(ARMS)},
        # the SERVE bar: organ clustering lifts who-did-what over the head-token incumbent
        "ORGAN_over_HEAD_pron": paired("ORGAN", "HEAD", seed + 40),
        "ORGAN_NOGENDER_over_HEAD_pron": paired("ORGAN_NOGENDER", "HEAD", seed + 41),
        "ORGAN_over_SHUF_NAME_pron": paired("ORGAN", "SHUF_NAME", seed + 43),
        # DECOMPOSITION of the oracle gap -> is the cap name-clustering or pronoun-binding?
        "ORACLE_over_GOLDNAME_ACTR_pron": paired("ORACLE", "GOLDNAME_ACTR", seed + 45),   # PRONOUN-BINDING cost (gold names)
        "HEAD_OPB_over_HEAD_pron": paired("HEAD_OPB", "HEAD", seed + 46),                 # what PERFECT pronouns alone buy
        "ORGAN_OPB_over_HEAD_OPB_pron": paired("ORGAN_OPB", "HEAD_OPB", seed + 47),       # NAME-CLUSTERING cost, given perfect pronouns
        "ORACLE_over_ORGAN_OPB_pron": paired("ORACLE", "ORGAN_OPB", seed + 48),           # residual name-cluster gap to gold
    }


def self_test():
    gaz = {"elizabeth": "fem", "jane": "fem"}
    # Elizabeth is named, then acts via pronoun; head-token shatters "Elizabeth"/"Miss Bennet" so the
    # pronoun event is not reachable from the "Bennet" anchor; the organ unifies them so it IS.
    stream = [
        {"head_text": "bennet", "span_tokens": ["Elizabeth", "Bennet"], "gold": 0, "sent": 0, "start": 0, "role": "SUBJECT", "gov_verb": "enter", "ent_type": "PER"},
        {"head_text": "she", "span_tokens": ["she"], "gold": 0, "sent": 1, "start": 0, "role": "SUBJECT", "gov_verb": "smile", "ent_type": "PER"},
        {"head_text": "bennet", "span_tokens": ["Miss", "Bennet"], "gold": 0, "sent": 2, "start": 0, "role": "SUBJECT", "gov_verb": "walk", "ent_type": "PER"},
    ]
    for arm in ("HEAD", "ORGAN", "ORACLE"):
        pred = combined_pred(stream, arm, gaz)
        assert len(pred) == 3 and all(p >= 0 for p in pred), f"{arm} pred malformed: {pred}"
    org = combined_pred(stream, "ORGAN", gaz)
    assert org[0] == org[2], f"organ must unify Elizabeth's name forms: {org}"
    print(f"SELF-TEST PASS: combined_pred runs all arms; organ unifies name forms (pred={org}).")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--prove-register", action="store_true", dest="prove_register")
    ap.add_argument("--docs", type=int, default=None)
    ap.add_argument("--theta", type=float, default=0.4)
    ap.add_argument("--n-boot", type=int, default=2000)
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.prove_register:
        print(json.dumps(prove_register(docs=args.docs, n_boot=args.n_boot, theta=args.theta), indent=2)); return
    if args.run:
        print(json.dumps(cell(docs=args.docs, n_boot=args.n_boot, theta=args.theta), indent=2)); return
    print("use --self-test | --run | --prove-register [--docs N --theta T]")


if __name__ == "__main__":
    main()
