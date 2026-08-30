"""COMBINED end-to-end: BOTH live extractors in ONE passage (closes the 'proven separately' caveat).
The belief timeline is driven by the LIVE temporal-order register (chronology from tense/aspect) AND
the LIVE observation-cue extractor (did the agent witness it?) on FLASHBACK prose, where an agent's
belief-relevant event is revealed by a past-perfect clause AFTER the query point in the text.

Two sub-types give a clean dissociation:
  FB_OBSERVED  -- the belief-setting observation is in a flashback the agent DID witness. LIVE ORDER is
                 load-bearing: a narration-order timeline has not reached it at the query's text
                 position (wrong); the register places it earlier (right).
  FB_UNOBSERVED-- the flashback reveals a move the agent did NOT witness (absent). LIVE OBSERVATION is
                 load-bearing: an observation-blind timeline updates to the flashback value (wrong);
                 the gated timeline keeps the prior belief (right).
Arms: LIVE (register order + live obs) ; ORACLE (gold order + gold obs) ; NARRATION-order (live obs) ;
OBS-BLIND (register order, ignore observation) ; timeline-agnostic FLOOR. The combined LIVE beats every
floor; each floor fails a DIFFERENT sub-type; the gap to oracle localizes the joint extraction residual.
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

OUTDIR = os.path.join(_REPO, "data", "exp_belief_timeline_live_flashback_e2e_v1")

# COMBINED structure: BOTH live components load-bearing in ONE passage. Each passage has, revealed in a
# past-perfect FLASHBACK after the query point: a belief-setting PLACEMENT the agent DID observe
# (put_pred/put_value) and a later MOVE the agent did NOT observe (move_pred/move_value, with an
# explicit "did not see" marker for the RULE-0 epistemic route). Query = a simple-past return/look.
# gold belief = put_value (the agent missed the move). LIVE ORDER is load-bearing (both flashback
# events are narrated AFTER the query -> a narration-order timeline has not seen the placement, wrong);
# LIVE OBSERVATION is load-bearing (obs-blind takes the latest flashback event = the unobserved move,
# wrong). Only register-order + observation-gating gets it.
PASSAGES = [
    {"sid": "cb_pie", "agent": ["Nora", "she", "her"], "obj": "pie",
     "text": "Nora came back and looked at the counter . She had placed the pie on the counter herself . "
             "But while she had been outside her son had carried it to the pantry . She did not see this .",
     "put_pred": "placed", "put_value": "counter", "put_sent": 1,
     "move_pred": "carried", "move_value": "pantry", "move_sent": 2,
     "query_pred": "looked", "gold": "counter"},
    {"sid": "cb_hat", "agent": ["Otto", "he", "his", "him"], "obj": "hat",
     "text": "Otto returned and turned toward the peg . He had hung the hat on the peg himself . "
             "But while he had been away his friend had moved it to the rack . He did not notice this .",
     "put_pred": "hung", "put_value": "peg", "put_sent": 1,
     "move_pred": "moved", "move_value": "rack", "move_sent": 2,
     "query_pred": "turned", "gold": "peg"},
    {"sid": "cb_doll", "agent": ["Kate", "she", "her"], "obj": "doll",
     "text": "Kate came home and went to the bed . She had placed the doll on the bed herself . "
             "But while she had been downstairs her cousin had taken it to the chest . She did not see this .",
     "put_pred": "placed", "put_value": "bed", "put_sent": 1,
     "move_pred": "taken", "move_value": "chest", "move_sent": 2,
     "query_pred": "went", "gold": "bed"},
    {"sid": "cb_map", "agent": ["Reid", "he", "his", "him"], "obj": "map",
     "text": "Reid returned and looked in the case . He had folded the map into the case himself . "
             "But while he had been on deck his mate had shifted it to the locker . He did not see this .",
     "put_pred": "folded", "put_value": "case", "put_sent": 1,
     "move_pred": "shifted", "move_value": "locker", "move_sent": 2,
     "query_pred": "looked", "gold": "case"},
    {"sid": "cb_watch", "agent": ["Ada", "she", "her"], "obj": "watch",
     "text": "Ada came in and glanced at the table . She had laid the watch on the table herself . "
             "But while she had been at work her son had put it in the drawer . She did not see this .",
     "put_pred": "laid", "put_value": "table", "put_sent": 1,
     "move_pred": "put", "move_value": "drawer", "move_sent": 2,
     "query_pred": "glanced", "gold": "table"},
    {"sid": "cb_book", "agent": ["Ben", "he", "his", "him"], "obj": "book",
     "text": "Ben returned and reached for the desk . He had stored the book in the desk himself . "
             "But while he had been out his sister had moved it to the shelf . He did not notice this .",
     "put_pred": "stored", "put_value": "desk", "put_sent": 1,
     "move_pred": "moved", "move_value": "shelf", "move_sent": 2,
     "query_pred": "reached", "gold": "desk"},
    {"sid": "cb_ring", "agent": ["Mia", "she", "her"], "obj": "ring",
     "text": "Mia came back and opened the box . She had dropped the ring into the box herself . "
             "But while she had been away her sister had moved it to the pocket . She did not see this .",
     "put_pred": "dropped", "put_value": "box", "put_sent": 1,
     "move_pred": "moved", "move_value": "pocket", "move_sent": 2,
     "query_pred": "opened", "gold": "box"},
    {"sid": "cb_key", "agent": ["Mara", "she", "her"], "obj": "key",
     "text": "Mara returned and went to the shelf . She had left the key on the shelf herself . "
             "But while she had been outside her brother had moved it to the drawer . She did not see this .",
     "put_pred": "left", "put_value": "shelf", "put_sent": 1,
     "move_pred": "moved", "move_value": "drawer", "move_sent": 2,
     "query_pred": "went", "gold": "shelf"},
    {"sid": "cb_coin", "agent": ["Leo", "he", "his", "him"], "obj": "coin",
     "text": "Leo came in and checked the pocket . He had slipped the coin into the pocket himself . "
             "But while he had been away his friend had moved it to the tin . He did not notice this .",
     "put_pred": "slipped", "put_value": "pocket", "put_sent": 1,
     "move_pred": "moved", "move_value": "tin", "move_sent": 2,
     "query_pred": "checked", "gold": "pocket"},
    {"sid": "cb_letter", "agent": ["Tom", "he", "his", "him"], "obj": "letter",
     "text": "Tom came back and searched the drawer . He had hidden the letter in the drawer himself . "
             "But while he had been out his brother had moved it to the box . He did not see this .",
     "put_pred": "hidden", "put_value": "drawer", "put_sent": 1,
     "move_pred": "moved", "move_value": "box", "move_sent": 2,
     "query_pred": "searched", "gold": "drawer"},
]
VOCAB = ["drawer", "box", "shelf", "pocket", "desk", "counter", "pantry", "peg", "rack", "bed",
         "chest", "case", "locker", "table", "tin"]


def _register_ranks(text):
    sents = [s.split() for s in text.split(" . ")]
    sents = [s + ["."] for s in sents if s]
    ev, tg, edges = R.extract_passage(sents, clause_pluperfect=True)
    disc = R.DiscreteOrderRegister(ev, tg, edges)
    narr = R.NarrationOrderFloor(ev, tg, edges)
    return disc.rank, narr.text_rank


def _live_obs(led, sc, pred_key, val_key, sent_key):
    tr = led.observed(sc["text"], sc["agent"], event_object=sc["obj"],
                      event_index=sc[sent_key], event_location=sc[val_key])
    return bool(tr.observed)


def _belief(sc, order_rank, obs_put, obs_move, obs_blind=False):
    """Belief at the query = value of the latest belief-relevant event BEFORE the query on `order_rank`
    that is OBSERVED (put: obs_put; move: obs_move). obs_blind ignores observation (takes the latest
    event, = the unobserved move). Missing extraction -> None."""
    pp, mp, qp = sc["put_pred"], sc["move_pred"], sc["query_pred"]
    if qp not in order_rank:
        return None, False
    cands = []   # (order, value, observed)
    if pp in order_rank and order_rank[pp] < order_rank[qp]:
        cands.append((order_rank[pp], sc["put_value"], obs_put))
    if mp in order_rank and order_rank[mp] < order_rank[qp]:
        cands.append((order_rank[mp], sc["move_value"], obs_move))
    if not cands:
        return None, (pp in order_rank and mp in order_rank)
    usable = cands if obs_blind else [c for c in cands if c[2]]
    if not usable:
        return None, True
    usable.sort(key=lambda c: c[0])
    return usable[-1][1], True


def run(seed=20260830, d=1024):
    import spacy
    nlp = spacy.load("en_core_web_sm")
    from experiments.perceptual_access_ledger import PerceptualAccessLedger
    led = PerceptualAccessLedger(nlp)
    ro = SubstrateReadout(d=d, seed=seed)

    arms = {"live": [], "oracle": [], "narration": [], "obs_blind": [], "floor": []}
    cov = 0
    obs_ok = obs_tot = 0
    per = []
    for sc in PASSAGES:
        crank, nrank = _register_ranks(sc["text"])
        # the agent OBSERVES its OWN placement trivially (it is the actor) -- not the ledger's job;
        # the ledger's genuine task is whether A witnessed the OTHER agent's MOVE (A is absent).
        obs_put = True
        obs_move = _live_obs(led, sc, "move_pred", "move_value", "move_sent")  # expect False (absent)
        obs_tot += 1
        obs_ok += int(obs_move is False)
        gsym = ro.readout(sc["obj"], sc["gold"], VOCAB)
        bl, ok = _belief(sc, crank, obs_put, obs_move)                       # LIVE
        cov += int(ok)
        bo, _ = _belief(sc, crank, True, False)                             # ORACLE (gold obs)
        bn, _ = _belief(sc, nrank, obs_put, obs_move)                        # NARRATION order + live obs
        bb, _ = _belief(sc, crank, obs_put, obs_move, obs_blind=True)        # OBS-BLIND
        bf = sc["move_value"]                                               # FLOOR = last-mentioned
        preds = {"live": bl, "oracle": bo, "narration": bn, "obs_blind": bb, "floor": bf}
        for a, p in preds.items():
            arms[a].append(int(ro.readout(sc["obj"], p, VOCAB) == gsym) if p is not None else 0)
        per.append({"sid": sc["sid"], "obs_put": obs_put, "obs_move": obs_move,
                    "live": preds["live"], "gold": sc["gold"]})

    def ci(v):
        v = np.asarray(v, float)
        rng = np.random.default_rng(seed)
        m = [v[rng.integers(0, len(v), len(v))].mean() for _ in range(2000)]
        return float(v.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))

    res = {a: {"acc": ci(v)[0], "ci": list(ci(v)[1:])} for a, v in arms.items()}
    metrics = {
        "seed": seed, "n_passages": len(PASSAGES), "extraction_coverage": cov / len(PASSAGES),
        "observation_cue_acc": obs_ok / obs_tot, "n_obs_events": obs_tot,
        "arms": res, "per_passage": per,
        "verdict": {
            "live_beats_floor": res["live"]["ci"][0] > res["floor"]["ci"][1],
            "live_beats_narration": res["live"]["acc"] > res["narration"]["acc"] + 0.1,
            "live_beats_obs_blind": res["live"]["acc"] > res["obs_blind"]["acc"] + 0.1,
            "oracle_perfect": res["oracle"]["acc"] == 1.0,
        },
    }
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    m = run()
    if args.self_test:
        v = m["verdict"]
        assert v["live_beats_narration"] and v["live_beats_obs_blind"] and v["oracle_perfect"], (v, m["arms"])
        print("self-test PASS", json.dumps(v))
        return
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    a = m["arms"]
    print("=" * 78)
    print("COMBINED live serve -- LIVE order + LIVE observation on flashback prose")
    print("=" * 78)
    print(f"  extraction coverage {m['extraction_coverage']:.2f}  observation-cue acc {m['observation_cue_acc']:.2f}")
    for name in ("live", "oracle", "narration", "obs_blind", "floor"):
        print(f"  {name:10s} {a[name]['acc']:.3f}  CI {a[name]['ci']}")
    print("  (narration = live obs + narration order; obs_blind = register order, no obs gate;")
    print("   floor = last-mentioned value. Both live components are load-bearing in EACH passage.)")
    print(f"  verdict: {json.dumps(m['verdict'])}")
    print(f"written {OUTDIR}/metrics.json")


if __name__ == "__main__":
    main()
