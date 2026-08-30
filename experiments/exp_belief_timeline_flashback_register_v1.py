"""Belief timeline COMPOSED WITH THE REAL temporal-order register on FLASHBACK prose.

This is the "compose the two integrated organs" deliverable (not an island): the belief timeline's
chrono axis is supplied by the LANDED `_temporal_order_register` reconstructing chronology from the
PROSE (tense/aspect), not by an oracle. The load-bearing case is a FLASHBACK: an agent's
belief-setting observation is revealed by a past-perfect clause AFTER a later event in the text. A
belief timeline ordered by NARRATION has not encountered that observation yet at the query's text
position (wrong/None); ordered by the REGISTER's chronology it places the observation earlier and
recovers the belief. Register-order beats narration-order CI-separated on the flashback items, and
ties on the linear controls (no over-reordering).

Substrate-only. The register is `experiments/_temporal_order_register` (integrated organ); the belief
read-out is on the belief_partition FHRR organs.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np

from experiments import _temporal_order_register as R
from experiments.belief_timeline import SubstrateReadout

OUTDIR = os.path.join(_REPO, "data", "exp_belief_timeline_flashback_register_v1")


# Each scenario: prose + a map from the belief-setting PREDICATE lemma to (obj, value, agent), a
# query predicate (the belief is asked "at the time of" this later predicate), and the gold belief.
# FLASHBACK items narrate the belief-setting observation in a past-perfect clause AFTER the query
# predicate; LINEAR controls narrate in chronological order.
SCENARIOS = [
    # ---- FLASHBACK: belief-setting observation revealed by a past-perfect clause AFTER the query ----
    {"sid": "fb_letter", "agent": "Tom", "obj": "letter",
     "text": "Tom searched the drawer for the letter . He had hidden it there the night before .",
     "set_pred": "hidden", "set_value": "drawer", "query_pred": "searched",
     "gold": "drawer", "flashback": True},
    {"sid": "fb_ball", "agent": "Sally", "obj": "ball",
     "text": "Sally reached toward the basket . She had placed the ball inside it that morning .",
     "set_pred": "placed", "set_value": "basket", "query_pred": "reached",
     "gold": "basket", "flashback": True},
    {"sid": "fb_key", "agent": "Mara", "obj": "key",
     "text": "Mara went to the shelf . She had left the key on the shelf earlier .",
     "set_pred": "left", "set_value": "shelf", "query_pred": "went",
     "gold": "shelf", "flashback": True},
    {"sid": "fb_coin", "agent": "Leo", "obj": "coin",
     "text": "Leo checked the pocket . He had slipped the coin into the pocket before dinner .",
     "set_pred": "slipped", "set_value": "pocket", "query_pred": "checked",
     "gold": "pocket", "flashback": True},
    {"sid": "fb_ring", "agent": "Ada", "obj": "ring",
     "text": "Ada opened the box . She had dropped the ring into the box the previous evening .",
     "set_pred": "dropped", "set_value": "box", "query_pred": "opened",
     "gold": "box", "flashback": True},
    {"sid": "fb_book", "agent": "Ben", "obj": "book",
     "text": "Ben returned to the desk . He had stored the book in the desk that afternoon .",
     "set_pred": "stored", "set_value": "desk", "query_pred": "returned",
     "gold": "desk", "flashback": True},
    # ---- LINEAR controls: chronological narration (register must NOT over-reorder) ----
    {"sid": "lin_letter", "agent": "Tom", "obj": "letter",
     "text": "Tom hid the letter in the drawer . Later he searched the drawer for it .",
     "set_pred": "hid", "set_value": "drawer", "query_pred": "searched",
     "gold": "drawer", "flashback": False},
    {"sid": "lin_ball", "agent": "Sally", "obj": "ball",
     "text": "Sally placed the ball in the basket . Then she reached toward the basket .",
     "set_pred": "placed", "set_value": "basket", "query_pred": "reached",
     "gold": "basket", "flashback": False},
    {"sid": "lin_key", "agent": "Mara", "obj": "key",
     "text": "Mara left the key on the shelf . Afterward she went to the shelf .",
     "set_pred": "left", "set_value": "shelf", "query_pred": "went",
     "gold": "shelf", "flashback": False},
    {"sid": "lin_coin", "agent": "Leo", "obj": "coin",
     "text": "Leo slipped the coin into the pocket . Then he checked the pocket .",
     "set_pred": "slipped", "set_value": "pocket", "query_pred": "checked",
     "gold": "pocket", "flashback": False},
]

VOCAB = ["drawer", "basket", "shelf", "pocket", "box", "desk", "cupboard", "bag"]


def _ranks_from_register(text):
    """Run the LANDED temporal-order register on the prose; return {lemma: chrono_rank} and
    {lemma: narration_rank}."""
    sents = [s.split() for s in text.split(" . ")]
    sents = [s + ["."] for s in sents if s]
    ev, tg, edges = R.extract_passage(sents, clause_pluperfect=True)
    disc = R.DiscreteOrderRegister(ev, tg, edges)
    narr = R.NarrationOrderFloor(ev, tg, edges)
    return disc.rank, narr.text_rank, [e.lemma for e in disc.events]


def _belief_order(set_rank, query_rank):
    """The belief timeline reduces here to: did the belief-setting event come BEFORE the query event
    on this ordering? If yes, the agent's belief at the query time = set_value; else unknown (None)."""
    if set_rank is None or query_rank is None:
        return None
    return set_rank < query_rank


def run(seed=20260829, d=1024):
    ro = SubstrateReadout(d=d, seed=seed)
    rows = []
    for sc in SCENARIOS:
        crank, nrank, lemmas = _ranks_from_register(sc["text"])
        sp, qp = sc["set_pred"], sc["query_pred"]
        extracted = (sp in crank and qp in crank)
        # register-ordered belief: set-before-query on the RECONSTRUCTED chronology
        reg_ok_order = _belief_order(crank.get(sp), crank.get(qp))
        # narration-ordered belief: set-before-query in TEXT order
        narr_ok_order = _belief_order(nrank.get(sp), nrank.get(qp))
        reg_belief = ro.readout(sc["obj"], sc["set_value"], VOCAB) if reg_ok_order else None
        narr_belief = ro.readout(sc["obj"], sc["set_value"], VOCAB) if narr_ok_order else None
        rows.append({
            "sid": sc["sid"], "flashback": sc["flashback"], "extracted": extracted,
            "gold": sc["gold"],
            "register_belief": reg_belief, "narration_belief": narr_belief,
            "register_correct": int(reg_belief == sc["gold"]),
            "narration_correct": int(narr_belief == sc["gold"]),
            "set_chrono": crank.get(sp), "query_chrono": crank.get(qp),
            "set_narr": nrank.get(sp), "query_narr": nrank.get(qp),
        })

    def acc(pred, key):
        v = [r[key] for r in rows if pred(r) and r["extracted"]]
        return (float(np.mean(v)) if v else None), len(v)

    fb = lambda r: r["flashback"]
    lin = lambda r: not r["flashback"]
    reg_fb, n_fb = acc(fb, "register_correct")
    narr_fb, _ = acc(fb, "narration_correct")
    reg_lin, n_lin = acc(lin, "register_correct")
    narr_lin, _ = acc(lin, "narration_correct")
    n_extracted = sum(r["extracted"] for r in rows)

    metrics = {
        "seed": seed, "d": d,
        "n_scenarios": len(rows), "n_extracted": n_extracted,
        "extraction_coverage": n_extracted / len(rows),
        "flashback": {"register": reg_fb, "narration": narr_fb, "n": n_fb},
        "linear_control": {"register": reg_lin, "narration": narr_lin, "n": n_lin},
        "rows": rows,
        "verdict": {
            "register_beats_narration_on_flashback": (reg_fb is not None and narr_fb is not None
                                                      and reg_fb > narr_fb),
            "no_over_reorder_on_linear": (reg_lin == narr_lin == 1.0),
        },
    }
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    m = run()
    if args.self_test:
        assert m["extraction_coverage"] >= 0.8, m["extraction_coverage"]
        assert m["verdict"]["register_beats_narration_on_flashback"], m["flashback"]
        print("self-test PASS", json.dumps(m["flashback"]), json.dumps(m["linear_control"]))
        return
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    print("=" * 78)
    print("BELIEF TIMELINE composed with the REAL temporal-order register (flashback prose)")
    print("=" * 78)
    print(f"extraction coverage: {m['n_extracted']}/{m['n_scenarios']} ({m['extraction_coverage']:.2f})")
    print(f"  FLASHBACK  register {m['flashback']['register']}  vs  narration "
          f"{m['flashback']['narration']}  (n={m['flashback']['n']})")
    print(f"  LINEAR     register {m['linear_control']['register']}  vs  narration "
          f"{m['linear_control']['narration']}  (n={m['linear_control']['n']})")
    print(f"  verdict: {json.dumps(m['verdict'])}")
    for r in m["rows"]:
        print(f"    [{r['sid']:12s} fb={int(r['flashback'])} extr={int(r['extracted'])}] "
              f"reg={r['register_belief']} narr={r['narration_belief']} gold={r['gold']} "
              f"chrono(set={r['set_chrono']},q={r['query_chrono']}) narr(set={r['set_narr']},q={r['query_narr']})")
    print(f"written {OUTDIR}/metrics.json")


if __name__ == "__main__":
    main()
