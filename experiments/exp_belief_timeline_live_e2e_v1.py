"""END-TO-END LIVE serve: the belief timeline driven by the LIVE observation-cue extractor
(experiments/perceptual_access_ledger.py -- the integrated ToM front-end) on real-English multi-event
passages, with imperfect extraction IN THE LOOP. This is the capability test (vs the mechanism tests
on construction gold): does composing belief-timeline order with a REAL "did A witness this?" extractor
beat a timeline-agnostic reader on natural prose, and where does live extraction cost accuracy?

Stack: for each move/observe event, the LIVE ledger reads whether the agent witnessed it from the prose
(presence intervals + perceptual field); the belief timeline sample-and-holds over those LIVE bits,
ordered by narration (these passages are chronological -- the LIVE temporal-order register is proven
separately on flashback prose in exp_belief_timeline_flashback_register_v1). Belief decoded on the
belief_partition FHRR organs.

Arms: LIVE (live obs -> timeline) ; ORACLE (gold obs -> timeline, upper bound) ; FLOOR (timeline-
agnostic current-belief on the SAME live obs). LIVE must beat the FLOOR CI-separated; the LIVE-vs-ORACLE
gap localizes the observation-cue extraction residual (the same residual the ToM organ reports at 0.821).
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

from experiments.belief_timeline import (
    WorldEvent, timeline_belief, current_belief_floor, SubstrateReadout,
)

OUTDIR = os.path.join(_REPO, "data", "exp_belief_timeline_live_e2e_v1")

# Real-English multi-event passages. events: (value, sent_idx, gold_observed, kind); sent_idx anchors
# the LIVE ledger call. queries: (event_chrono_k, gold_value) -- belief JUST AFTER event chrono k
# (t = k + 0.5). 'resee' = the agent re-observing the current location. Passages are chronological
# (narration order == event order). Agent aliases = [name, pron_subj, pron_obj].
PASSAGES = [
    {"sid": "keys_reobs", "agent": ["Sam", "he", "his", "him"], "obj": "keys",
     "text": "Sam put his keys on the hook . He went upstairs to shower . "
             "While Sam was upstairs his sister moved the keys to the bowl . "
             "He did not hear her . Sam came down and found the keys in the bowl .",
     "events": [("hook", 0, True, "move"), ("bowl", 2, False, "move"), ("bowl", 4, True, "resee")],
     "vocab": ["hook", "bowl", "drawer", "table"],
     "queries": [(0, "hook"), (1, "hook"), (2, "bowl")]},   # after ev1 (unobserved move) = stale hook
    {"sid": "letter_stale", "agent": ["Nora", "she", "her"], "obj": "letter",
     "text": "Nora placed the letter in the drawer . Then she went out to the garden . "
             "While Nora was outside her brother moved the letter to the shelf . "
             "Nora did not see this . Nora came back inside .",
     "events": [("drawer", 0, True, "move"), ("shelf", 2, False, "move")],
     "vocab": ["drawer", "shelf", "box", "bag"],
     "queries": [(0, "drawer"), (1, "drawer")]},   # she believes drawer throughout (never saw the move)
    {"sid": "ball_reobs", "agent": ["Sally", "she", "her"], "obj": "ball",
     "text": "Sally left the ball in the basket . She walked out to the yard . "
             "While Sally was away Tom moved the ball to the box . "
             "She did not notice . Sally returned and saw the ball in the box .",
     "events": [("basket", 0, True, "move"), ("box", 2, False, "move"), ("box", 4, True, "resee")],
     "vocab": ["basket", "box", "shelf", "crate"],
     "queries": [(0, "basket"), (1, "basket"), (2, "box")]},
    {"sid": "medicine_multi", "agent": ["patient", "he", "him", "his"], "obj": "medicine",
     "text": "The nurse set the medicine on the counter . The patient watched her . "
             "The nurse carried it to the cabinet . The patient watched her again . "
             "The nurse took it to the fridge while the patient watched .",
     "events": [("counter", 0, True, "move"), ("cabinet", 2, True, "move"), ("fridge", 4, True, "move")],
     "vocab": ["counter", "cabinet", "fridge", "shelf"],
     "queries": [(0, "counter"), (1, "cabinet"), (2, "fridge")]},   # past-T discriminates
    {"sid": "phone_reobs", "agent": ["Lena", "she", "her"], "obj": "phone",
     "text": "Lena put her phone on the couch . She stepped into the garden . "
             "While Lena was outside her brother slipped it under the cushion . "
             "She did not notice . Lena came back and found it under the cushion .",
     "events": [("couch", 0, True, "move"), ("cushion", 2, False, "move"), ("cushion", 4, True, "resee")],
     "vocab": ["couch", "cushion", "table", "shelf"],
     "queries": [(0, "couch"), (1, "couch"), (2, "cushion")]},
    {"sid": "book_multi", "agent": ["boy", "he", "his", "him"], "obj": "book",
     "text": "The boy set the book on the desk . He watched his mother pick it up . "
             "His mother put the book on the shelf as he watched . "
             "Then she moved it to the box while the boy looked on .",
     "events": [("desk", 0, True, "move"), ("shelf", 2, True, "move"), ("box", 3, True, "move")],
     "vocab": ["desk", "shelf", "box", "crate"],
     "queries": [(0, "desk"), (1, "shelf"), (2, "box")]},
    {"sid": "watch_stale", "agent": ["Ada", "she", "her"], "obj": "watch",
     "text": "Ada laid the watch on the table . She left for work . "
             "In her absence her son moved the watch to the drawer . "
             "Ada did not know . She was still at work .",
     "events": [("table", 0, True, "move"), ("drawer", 2, False, "move")],
     "vocab": ["table", "drawer", "box", "shelf"],
     "queries": [(0, "table"), (1, "table")]},
    {"sid": "ring_reobs", "agent": ["Mia", "she", "her"], "obj": "ring",
     "text": "Mia placed the ring in the box . She went to the kitchen . "
             "While Mia was in the kitchen her sister moved the ring to the pocket . "
             "She did not see it . Mia returned and found the ring in the pocket .",
     "events": [("box", 0, True, "move"), ("pocket", 2, False, "move"), ("pocket", 4, True, "resee")],
     "vocab": ["box", "pocket", "drawer", "bag"],
     "queries": [(0, "box"), (1, "box"), (2, "pocket")]},
    {"sid": "coin_multi", "agent": ["girl", "she", "her"], "obj": "coin",
     "text": "The girl dropped the coin in the jar . She watched it fall . "
             "Her father moved the coin to the tin as she watched . "
             "He then placed it in the box while she looked on .",
     "events": [("jar", 0, True, "move"), ("tin", 2, True, "move"), ("box", 3, True, "move")],
     "vocab": ["jar", "tin", "box", "cup"],
     "queries": [(0, "jar"), (1, "tin"), (2, "box")]},
    {"sid": "toy_stale", "agent": ["child", "she", "her"], "obj": "toy",
     "text": "The child put the toy in the crib . She fell asleep . "
             "While the child slept the nanny moved the toy to the shelf . "
             "She did not wake . The toy stayed on the shelf .",
     "events": [("crib", 0, True, "move"), ("shelf", 2, False, "move")],
     "vocab": ["crib", "shelf", "box", "chest"],
     "queries": [(0, "crib"), (1, "crib")]},
    {"sid": "hat_reobs", "agent": ["Otto", "he", "his", "him"], "obj": "hat",
     "text": "Otto hung his hat on the peg . He went out to the street . "
             "While Otto was outside his friend moved the hat to the rack . "
             "He did not see it . Otto came back and found the hat on the rack .",
     "events": [("peg", 0, True, "move"), ("rack", 2, False, "move"), ("rack", 4, True, "resee")],
     "vocab": ["peg", "rack", "shelf", "hook"],
     "queries": [(0, "peg"), (1, "peg"), (2, "rack")]},
    {"sid": "cup_multi", "agent": ["man", "he", "his", "him"], "obj": "cup",
     "text": "The man placed the cup on the tray . He watched the waiter lift it . "
             "The waiter set the cup on the bar as the man watched . "
             "Then the waiter carried it to the sink while the man looked on .",
     "events": [("tray", 0, True, "move"), ("bar", 2, True, "move"), ("sink", 3, True, "move")],
     "vocab": ["tray", "bar", "sink", "shelf"],
     "queries": [(0, "tray"), (1, "bar"), (2, "sink")]},
    {"sid": "doll_stale", "agent": ["Kate", "she", "her"], "obj": "doll",
     "text": "Kate set the doll on the bed . She went downstairs for dinner . "
             "While Kate was downstairs her cousin moved the doll to the chest . "
             "She did not notice . Kate stayed at the table .",
     "events": [("bed", 0, True, "move"), ("chest", 2, False, "move")],
     "vocab": ["bed", "chest", "shelf", "box"],
     "queries": [(0, "bed"), (1, "bed")]},
    {"sid": "map_reobs", "agent": ["Reid", "he", "his", "him"], "obj": "map",
     "text": "Reid folded the map into the case . He stepped out to the deck . "
             "While Reid was on the deck his mate moved the map to the locker . "
             "He did not see it . Reid returned and found the map in the locker .",
     "events": [("case", 0, True, "move"), ("locker", 2, False, "move"), ("locker", 4, True, "resee")],
     "vocab": ["case", "locker", "chest", "bag"],
     "queries": [(0, "case"), (1, "case"), (2, "locker")]},
    {"sid": "pen_multi", "agent": ["clerk", "she", "her"], "obj": "pen",
     "text": "The clerk left the pen on the ledger . She watched the manager take it . "
             "The manager put the pen in the tray as she watched . "
             "Then the manager moved it to the drawer while the clerk looked on .",
     "events": [("ledger", 0, True, "move"), ("tray", 2, True, "move"), ("drawer", 3, True, "move")],
     "vocab": ["ledger", "tray", "drawer", "shelf"],
     "queries": [(0, "ledger"), (1, "tray"), (2, "drawer")]},
]


def _run_stack(nlp, led, sc, ro, mode):
    """Build the belief timeline for one passage under `mode` in {live, oracle}; return per-query preds
    and the per-event observation extraction (live vs gold)."""
    from experiments.perceptual_access_ledger import PerceptualAccessLedger  # noqa
    agent = sc["agent"][0]
    events, observed, extraction = [], {}, []
    for chrono, (loc, sent_idx, gold_obs, kind) in enumerate(sc["events"]):
        if mode == "oracle":
            obs_bit = gold_obs
        else:
            if kind == "resee":
                obs_bit = True   # the agent is the one finding/seeing it -> observed by construction
            else:
                tr = led.observed(sc["text"], sc["agent"], event_object=sc["obj"],
                                  event_index=sent_idx, event_location=loc)
                obs_bit = bool(tr.observed)
            extraction.append((obs_bit, gold_obs))
        events.append(WorldEvent(sc["obj"], loc, chrono=chrono, narr=chrono,
                                 kind="initial" if chrono == 0 else "move"))
        observed[(agent, chrono)] = obs_bit
    return events, observed, agent, extraction


def run(seed=20260830, d=1024):
    import spacy
    nlp = spacy.load("en_core_web_sm")
    from experiments.perceptual_access_ledger import PerceptualAccessLedger
    led = PerceptualAccessLedger(nlp)
    ro = SubstrateReadout(d=d, seed=seed)

    live_ok, oracle_ok, floor_ok = [], [], []
    ext_ok = ext_tot = 0
    per_passage = []
    for sc in PASSAGES:
        ev_l, obs_l, agent, extraction = _run_stack(nlp, led, sc, ro, "live")
        ev_o, obs_o, _, _ = _run_stack(nlp, led, sc, ro, "oracle")
        for obit, gbit in extraction:
            ext_tot += 1
            ext_ok += int(obit == gbit)
        p = {"sid": sc["sid"], "live": [], "oracle": [], "floor": []}
        for after_k, gold in sc["queries"]:
            t = after_k + 0.5
            gsym = ro.readout(sc["obj"], gold, sc["vocab"])
            live = ro.readout(sc["obj"], timeline_belief(ev_l, obs_l, agent, sc["obj"], t), sc["vocab"])
            orac = ro.readout(sc["obj"], timeline_belief(ev_o, obs_o, agent, sc["obj"], t), sc["vocab"])
            flr = ro.readout(sc["obj"], current_belief_floor(ev_l, obs_l, agent, sc["obj"], t), sc["vocab"])
            live_ok.append(int(live == gsym)); oracle_ok.append(int(orac == gsym))
            floor_ok.append(int(flr == gsym))
            p["live"].append(live == gsym); p["oracle"].append(orac == gsym); p["floor"].append(flr == gsym)
        per_passage.append(p)

    def ci(v):
        v = np.asarray(v, float)
        rng = np.random.default_rng(seed)
        means = [v[rng.integers(0, len(v), len(v))].mean() for _ in range(2000)]
        return float(v.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))

    lm, llo, lhi = ci(live_ok); om, olo, ohi = ci(oracle_ok); fm, flo, fhi = ci(floor_ok)
    metrics = {
        "seed": seed, "n_passages": len(PASSAGES), "n_queries": len(live_ok),
        "live_end_to_end": {"acc": lm, "ci": [llo, lhi]},
        "oracle_upper_bound": {"acc": om, "ci": [olo, ohi]},
        "timeline_agnostic_floor": {"acc": fm, "ci": [flo, fhi]},
        "observation_cue_extraction_acc": (ext_ok / ext_tot if ext_tot else None),
        "n_extracted_events": ext_tot,
        "verdict": {"live_beats_floor": llo > fhi,
                    "live_vs_oracle_gap": round(om - lm, 3)},
        "per_passage": per_passage,
    }
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    m = run()
    if args.self_test:
        assert m["verdict"]["live_beats_floor"], m
        print("self-test PASS", json.dumps(m["verdict"]))
        return
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    print("=" * 78)
    print("END-TO-END LIVE serve -- belief timeline + LIVE observation-cue extractor on real prose")
    print("=" * 78)
    print(f"  {m['n_passages']} passages, {m['n_queries']} belief queries")
    print(f"  LIVE end-to-end          {m['live_end_to_end']['acc']:.3f}  CI {m['live_end_to_end']['ci']}")
    print(f"  ORACLE (upper bound)     {m['oracle_upper_bound']['acc']:.3f}  CI {m['oracle_upper_bound']['ci']}")
    print(f"  timeline-agnostic FLOOR  {m['timeline_agnostic_floor']['acc']:.3f}  CI {m['timeline_agnostic_floor']['ci']}")
    print(f"  LIVE observation-cue extraction acc: {m['observation_cue_extraction_acc']:.3f} "
          f"(n={m['n_extracted_events']} move events)")
    print(f"  verdict: live beats floor = {m['verdict']['live_beats_floor']}; "
          f"live-vs-oracle gap = {m['verdict']['live_vs_oracle_gap']} (the extraction residual)")
    print(f"written {OUTDIR}/metrics.json")


if __name__ == "__main__":
    main()
