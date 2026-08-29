"""exp_coref_binder_wall_diagnostic_v1 -- DRILL the wall: a multi-cue graded structural binder does NOT
beat single-cue ACT-R on who-did-what. Is that because (a) ACT-R is already the best STRUCTURAL binder
(the residual is cue-conflict/anti-typical, needing per-item semantics the sibling already refuted), or
(b) the tuner is myopic / the who-did-what metric hides a real binding win? This cell measures RAW
pronoun-antecedent BINDING accuracy (teacher-forced gold clustering, proper agreement) on the FULL
who-did-what pronoun population, separating binder quality from decode mechanics.

MEASUREMENTS:
  1. Binding accuracy (bound to the gold entity's node) for ACT-R / strict_cb / graded / recency, on ALL
     pronouns and on the COMPETITIVE subset (>=2 gn-compatible prior gold entities). Teacher-forced: each
     pronoun scored against the TRUE prior state (errors do not compound) -> isolates per-decision quality.
  2. HAND-CONFIG probe: is the DEV tuner myopic? Test subject-heavy / cb-heavy / focus-heavy weightings
     directly on TEST -- if none beats ACT-R, the geometry cues genuinely add nothing (not a tuning bug).
  3. Error anatomy: of the graded binder's errors, is the gold structurally FAVORED on some cue (a
     ranking/cue-conflict miss) or structurally DOMINATED (needs semantics -- the irreducible core)?
  4. Anti-typicality: gold's recency rank + how often the binder grabs the most-frequent/most-recent.

Run: .venv/Scripts/python.exe experiments/exp_coref_binder_wall_diagnostic_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_coref_binder_wall_diagnostic_v1.py --run [--docs N]
GLASS-BOX, remote-safe (reads pre-parsed cache; NO spaCy, NO torch; numpy only).
# KB_REFERENT: data/litbank/who_did_what_events.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple

import numpy as np

os.environ.setdefault("OMP_NUM_THREADS", "1")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments.exp_litbank_activation_binder_v1 import PRONOUNS, _gn_compat, _dt  # noqa: E402
from experiments.exp_coref_graded_cue_retrieval_litbank_v1 import (  # noqa: E402
    load_streams, _entity_gn_gold, _supports, arm_actr, arm_strict_cb, arm_graded, arm_recency,
    tune_graded, error_anatomy, CUES, WEIGHT_KEYS, ACTR_D_FLOOR, _ci, _pairs, _paired, SEED)


def build_all_pron_instances(streams, competitive_only: bool = False) -> List[Dict]:
    """Teacher-forced pronoun-antecedent instances over ALL pronouns whose gold has >=1 prior mention and
    >=2 gn-compatible prior gold entities candidates ... optionally relax to ALL (>=1 candidate incl gold).
    Mirrors the sibling build_instances but exposes the competitive filter as a flag."""
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
                cand = {}
                for c, pri in prior_by_cluster.items():
                    if not pri:
                        continue
                    eg, en = egn.get(c, (None, None))
                    if _gn_compat(pg, pn, eg, en):
                        cand[c] = list(pri)
                keep = (gold in cand) and (len(cand) >= 2 if competitive_only else len(cand) >= 1)
                if keep:
                    out.append({"doc": rec["doc"], "pronoun": ht, "p_sent": m["sent"],
                                "pron_role": m["role"], "gold_cid": gold, "cand_ids": sorted(cand),
                                "prior": {c: cand[c] for c in cand}})
            prior_by_cluster[gold].append((m["sent"], m["role"]))
    return out


def _binding_acc(insts, arm_fn) -> Dict[str, list]:
    per_doc = defaultdict(lambda: [0, 0])
    for inst in insts:
        ids, sup, gi = _supports(inst)
        pick = arm_fn(ids, sup, gi, inst)
        per_doc[inst["doc"]][0] += int(pick == gi)
        per_doc[inst["doc"]][1] += 1
    return dict(per_doc)


def _anti_typicality(insts, weights, gain, d) -> Dict:
    ranks = []
    pick_most_freq = pick_most_recent = n = 0
    for inst in insts:
        ids, sup, gi = _supports(inst)
        pick = arm_graded(ids, sup, gi, inst, weights, gain, d)["pick"]
        order = np.argsort(-sup["recency"])
        ranks.append(int(np.where(order == gi)[0][0]))
        pick_most_freq += int(sup["freq"][pick] == sup["freq"].max())
        pick_most_recent += int(sup["recency"][pick] == sup["recency"].max())
        n += 1
    return {"gold_recency_rank_mean": round(float(np.mean(ranks)), 3),
            "gold_recency_rank_median": int(np.median(ranks)),
            "binder_picks_most_frequent_frac": round(pick_most_freq / max(n, 1), 3),
            "binder_picks_most_recent_frac": round(pick_most_recent / max(n, 1), 3)}


def run(docs: Optional[int] = None, n_boot: int = 2000, seed: int = SEED) -> dict:
    streams = load_streams(docs)
    insts_all = build_all_pron_instances(streams, competitive_only=False)
    insts_comp = build_all_pron_instances(streams, competitive_only=True)
    all_docs = sorted({i["doc"] for i in insts_all})
    dev_docs = set(all_docs[0::2])
    dev = [i for i in insts_all if i["doc"] in dev_docs]
    test_all = [i for i in insts_all if i["doc"] not in dev_docs]
    test_comp = [i for i in insts_comp if i["doc"] not in dev_docs]
    weights, gain, d = tune_graded(dev)

    def acc_block(insts, tag, s0):
        arms = {
            "recency": lambda ids, sup, gi, inst: arm_recency(ids, sup, gi)["pick"],
            "actr": lambda ids, sup, gi, inst: arm_actr(ids, sup, gi, inst, ACTR_D_FLOOR)["pick"],
            "strict_cb": lambda ids, sup, gi, inst: arm_strict_cb(ids, sup, gi, inst)["pick"],
            "graded": lambda ids, sup, gi, inst: arm_graded(ids, sup, gi, inst, weights, gain, d)["pick"],
        }
        pd = {a: _binding_acc(insts, fn) for a, fn in arms.items()}
        acc = {a: _ci(_pairs(pd[a]), n_boot, s0 + i) for i, a in enumerate(arms)}
        contr = {"graded_minus_actr": _paired(pd["graded"], pd["actr"], n_boot, s0 + 20),
                 "graded_minus_strict_cb": _paired(pd["graded"], pd["strict_cb"], n_boot, s0 + 21)}
        return {"n": len(insts), "accuracy": acc, "contrasts": contr}

    # HAND-CONFIG probe: is the tuner myopic? Test explicit geometry-heavy weightings on TEST (all pron).
    hand = {
        "pure_actr": {"actr": 1.0},
        "subject_heavy": {"actr": 1.0, "subject": 3.0},
        "cb_heavy": {"actr": 1.0, "cb": 3.0},
        "subject_cb_first": {"actr": 1.0, "subject": 2.0, "cb": 2.0, "first": 1.0},
        "centering_only": {"subject": 2.0, "cb": 2.0, "first": 1.0, "recency": 0.5},
    }
    hand_acc = {}
    for name, wpart in hand.items():
        w = {k: 0.0 for k in WEIGHT_KEYS}; w.update(wpart)
        pd = _binding_acc(test_all, lambda ids, sup, gi, inst, _w=w:
                          arm_graded(ids, sup, gi, inst, _w, gain, d)["pick"])
        arr = np.array(_pairs(pd), float)
        hand_acc[name] = round(float(arr[:, 0].sum() / max(arr[:, 1].sum(), 1)), 4)

    return {
        "anchor": "coref_binder_wall_diagnostic_v1",
        "population": "LitBank pronoun-antecedent BINDING (teacher-forced gold clustering, proper agreement)",
        "tuned_weights": {k: round(v, 3) for k, v in weights.items()}, "tuned_d": d,
        "ALL_pronouns_TEST": acc_block(test_all, "all", seed + 100),
        "COMPETITIVE_only_TEST": acc_block(test_comp, "comp", seed + 200),
        "hand_config_binding_acc_TEST_all": hand_acc,
        "graded_error_anatomy_TEST_all": error_anatomy(test_all, weights, gain, d),
        "graded_error_anatomy_TEST_comp": error_anatomy(test_comp, weights, gain, d),
        "anti_typicality_TEST_comp": _anti_typicality(test_comp, weights, gain, d),
        "verdict_note": ("if graded==actr on ALL and COMPETITIVE, and no hand-config beats pure_actr, then "
                         "ACT-R is already the optimal STRUCTURAL binder and the residual is semantic "
                         "(cue-conflict), NOT a tuning miss."),
    }


def in_harness_binding(docs: Optional[int] = None, seed: int = SEED) -> dict:
    """Decompose the 0.78-clean-binding vs 0.17-who-did-what discrepancy. Runs the ACTUAL who-did-what
    harness binders (combined_pred, weak agreement + head-token clustering) and measures, per pronoun
    query, whether it bound to its GOLD'S ANCHOR cluster (the who-did-what target). Separates who-did-what
    pronoun failures into BIND-WRONG (bound to a non-anchor cluster) vs BOUND-RIGHT-BUT-DECODE-FAILED
    (no-anchor / multi-verb / fragmentation -- the definitional ceiling)."""
    from experiments.exp_name_clustering_serves_whodidwhat_v1 import combined_pred as harness_pred, DECAY_D
    from experiments.exp_name_entity_clustering_v1 import load_enriched, load_given_gazetteer
    gaz = load_given_gazetteer()
    data = load_enriched(docs)
    out = {}
    for arm in ("HEAD", "HEAD_OPB", "ORACLE"):
        bound_right = decode_right = pron_q = bind_but_no_decode = 0
        for di, rec in enumerate(data):
            stream = rec["stream"]; rng = np.random.default_rng(seed + di)
            pred = harness_pred(stream, arm, gaz, DECAY_D, 0.4, rng)
            # anchor: gold -> predicted cluster of its first NAME mention (harness _score_direct logic)
            anchor = {}
            for m, cid in zip(stream, pred):
                g = m["gold"]; is_p = m["head_text"].lower() in PRONOUNS
                if g not in anchor:
                    anchor[g] = [cid, is_p]
                elif anchor[g][1] and not is_p:
                    anchor[g] = [cid, False]
            anchor = {g: cid for g, (cid, _) in anchor.items()}
            has_name = {m["gold"] for m in stream if m["head_text"].lower() not in PRONOUNS}
            reg = defaultdict(lambda: defaultdict(Counter))
            for m, cid in zip(stream, pred):
                if m["gov_verb"] is not None:
                    reg[cid][m["sent"]][m["gov_verb"]] += 1
            for m, cid in zip(stream, pred):
                if m["gov_verb"] is None or m["gold"] not in has_name:
                    continue
                if m["head_text"].lower() not in PRONOUNS:
                    continue
                pron_q += 1
                a = anchor.get(m["gold"])
                br = int(cid == a)
                bound_right += br
                slots = reg.get(a)
                pv = slots[m["sent"]].most_common(1)[0][0] if (slots and m["sent"] in slots) else None
                dr = int(pv == m["gov_verb"])
                decode_right += dr
                if br and not dr:
                    bind_but_no_decode += 1
        out[arm] = {"pron_queries": pron_q,
                    "bound_to_gold_anchor_frac": round(bound_right / max(pron_q, 1), 4),
                    "who_did_what_decode_frac": round(decode_right / max(pron_q, 1), 4),
                    "bound_right_but_decode_failed_frac": round(bind_but_no_decode / max(pron_q, 1), 4)}
    out["note"] = ("bound_to_gold_anchor_frac = the harness binder's REAL binding accuracy (vs the clean "
                   "0.78 teacher-forced). who_did_what_decode_frac = the bar's metric. The GAP between "
                   "them = the decode/anchor/multi-verb definitional ceiling. HEAD_OPB isolates it "
                   "(binding=~1.0 by construction, decode<1 = pure ceiling).")
    return out


def self_test():
    streams = load_streams(3)
    insts = build_all_pron_instances(streams, competitive_only=False)
    comp = build_all_pron_instances(streams, competitive_only=True)
    assert len(insts) >= len(comp), "all-pronoun set must be a superset of the competitive set"
    assert all(len(i["cand_ids"]) >= 2 for i in comp), "competitive instances must have >=2 candidates"
    assert all(i["gold_cid"] in i["cand_ids"] for i in insts), "gold must be in the candidate set"
    print(f"SELF-TEST PASS (all={len(insts)} >= comp={len(comp)}; gold always in candidates).")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--in-harness", action="store_true", dest="in_harness")
    ap.add_argument("--docs", type=int, default=None)
    ap.add_argument("--n-boot", type=int, default=2000)
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.in_harness:
        print(json.dumps(in_harness_binding(docs=args.docs), indent=2)); return
    if args.run:
        print(json.dumps(run(docs=args.docs, n_boot=args.n_boot), indent=2)); return
    print("use --self-test | --run [--docs N] | --in-harness")


if __name__ == "__main__":
    main()
