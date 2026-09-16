"""exp_space_where_is_modern_v1 -- MODERN-prose corpus-age CONTROL for the SPACE dimension.

The main SPACE result is on 14 real 19c LitBank passages. The brief flags the corpus-age confound ("prefer a
modern held-out set too if reachable"). Modern NARRATIVE-with-movement + coref is NOT on the shelf (LitBank is
all pre-1923; MAVEN/OntoNotes are Wikipedia/newswire, not character movement). So this set is AUTHOR-CONSTRUCTED
contemporary prose (8 passages, contemporary settings + vocabulary: apartment/subway/office/ER/gym/airport/
campus/cafe), DELIBERATELY including the hard constructions (veridical-embedded, caused-motion theme, stative/
concealment locatives, deixis) so it is not a soft template. It is a WEAKER control than a found corpus and is
labeled as such -- its ONE job is to test whether the reader's extraction (which reads path off age-stable
PREPOSITIONS, per the drill) survives MODERN verbs/vocabulary, i.e. that the LitBank result is not a
19c-vocabulary artifact.

Runs the SAME machinery end-to-end: build CoNLL (protagonist coref cluster) -> reader backbone -> in-substrate
prior_ext extraction -> PROMOTED hdlab.location_register -> where-is vs floors (abstain, last-mention) + info-free
twin null. Glass-box, no LLM. Writes ONLY data/exp_space_where_is_modern_v1[/ _smoke]. ASCII.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab.coref import parse_litbank_conll                        # noqa: E402
from hdlab.location_register import DEICTIC_SCENE, AWAY            # noqa: E402
from experiments._space_reader import (                            # noqa: E402
    build_backbone, extract_events_in_substrate, fold_tracker)
from experiments.exp_space_where_is_end_to_end_v1 import (         # noqa: E402
    cnode, region_of_node, gold_at, floor_lastment, floor_firstloc, _place_positions, _mention_gidx,
    _twin_registers, boot_paired, correct, extraction_quality, TWIN_R)

ANCHOR = "space_where_is_modern_v1"
SEED = 20260831

# (id, name, aliases, sentences[], gold_timeline[(t,node,region,present,kind)])
PASSAGES = [
    ("office_commute", "Dana", ["dana", "she", "her"],
     ["Dana was still in the kitchen when her phone buzzed with the third reminder.",
      "She grabbed her coat and hurried out of the apartment.",
      "Down on the street the air was cold and gray.",
      "She took the stairs to the subway and waited on the platform for the express.",
      "The train was packed, and she read the same headline four times without seeing it.",
      "When she finally reached the office, her manager had already seen her come in.",
      "She dropped her bag at her desk and went straight to the meeting room.",
      "For an hour nobody said anything useful.",
      "Afterward she slipped back to her desk and closed the door."],
     [(0, "kitchen", "indoors", True, "start"), (1, "<away>", "unknown", False, "depart"),
      (3, "platform", "outdoors", True, "stative"), (5, "office", "indoors", True, "arrive"),
      (6, "room", "indoors", True, "arrive"), (8, "desk", "indoors", True, "return")]),

    ("hospital", "Marcus", ["marcus", "he", "him", "his"],
     ["Marcus had been waiting in the lobby for almost an hour.",
      "When his name was called, a nurse walked him back to a small room.",
      "She took his blood pressure and told him the doctor would be right in.",
      "The doctor never came, and eventually an orderly wheeled him down to radiology.",
      "The scan took twenty minutes.",
      "Afterward they brought him up to a ward on the fourth floor.",
      "He lay in the bed by the window and watched the parking lot fill up."],
     [(0, "lobby", "indoors", True, "start"), (1, "room", "indoors", True, "arrive"),
      (3, "radiology", "indoors", True, "arrive"), (5, "ward", "indoors", True, "arrive"),
      (6, "ward", "indoors", True, "stative")]),

    ("gym", "Priya", ["priya", "she", "her"],
     ["Priya finished her last set and dropped the weights on the gym floor.",
      "She headed into the locker room to shower and change.",
      "Her gym bag was exactly where she had left it.",
      "On her way out she stopped at the front desk to renew her membership.",
      "Then she walked down to the parking garage on the lower level.",
      "She could not remember which row she had parked in.",
      "After ten minutes she gave up and went back to the lobby to ask for help."],
     [(0, "gym", "indoors", True, "start"), (1, "room", "indoors", True, "arrive"),
      (4, "garage", "indoors", True, "arrive"), (6, "lobby", "indoors", True, "return")]),

    ("airport", "Tom", ["tom", "he", "him", "his"],
     ["Tom stood in the security line, shuffling forward one shoe at a time.",
      "Once he was through, he found his gate at the far end of the terminal.",
      "He sat by the window and waited for the boarding call.",
      "When the agent finally watched him board, the plane was already late.",
      "A flight attendant showed him to a cramped seat near the back.",
      "The man beside him fell asleep before takeoff."],
     [(1, "gate", "indoors", True, "start"), (2, "gate", "indoors", True, "stative"),
      (3, "plane", "indoors", True, "arrive")]),

    ("party", "Lena", ["lena", "she", "her"],
     ["Lena arrived late and squeezed into the crowded living room.",
      "The music was too loud and she barely knew anyone.",
      "To escape a boring conversation she hid in the pantry for a few minutes.",
      "When she came back to the living room, someone had taken her spot on the couch.",
      "She drifted into the kitchen and poured herself a glass of water.",
      "Her friend found her there and dragged her out to the balcony to talk."],
     [(0, "room", "indoors", True, "start"), (2, "pantry", "indoors", True, "stative"),
      (3, "room", "indoors", True, "return"), (4, "kitchen", "indoors", True, "arrive"),
      (5, "balcony", "outdoors", True, "arrive")]),

    ("campus", "Owen", ["owen", "he", "him", "his"],
     ["Owen woke up late and rushed out of the dorm without breakfast.",
      "He cut across the quad toward the science building.",
      "His lecture had already started, so he slipped into the back of the hall.",
      "He could not follow any of it.",
      "After class he walked over to the library and found a desk on the third floor.",
      "He stayed there until it got dark."],
     [(0, "<away>", "unknown", False, "start"), (2, "hall", "indoors", True, "arrive"),
      (4, "library", "indoors", True, "arrive"), (5, "library", "indoors", True, "stative")]),

    ("cafe", "Sara", ["sara", "she", "her"],
     ["Sara had been sitting in the cafe since noon, nursing a cold coffee.",
      "When her ride texted, she stepped out onto the sidewalk.",
      "It was starting to rain.",
      "She climbed into the car and pulled the door shut behind her.",
      "They drove for a while without saying much.",
      "At the corner she asked them to let her out near the station."],
     [(0, "cafe", "indoors", True, "start"), (1, "sidewalk", "outdoors", True, "arrive"),
      (3, "car", "indoors", True, "arrive")]),

    ("tower", "Ben", ["ben", "he", "him", "his"],
     ["Ben signed in at the front desk and clipped on a visitor badge.",
      "He took the elevator up to the fifth floor.",
      "The receptionist led him down a long corridor to a conference room.",
      "He waited there alone for twenty minutes.",
      "Eventually someone came in and moved him to a smaller office next door.",
      "From the window he could see the whole city."],
     [(0, "desk", "indoors", True, "start"), (1, "floor", "indoors", True, "arrive"),
      (2, "room", "indoors", True, "arrive"), (3, "room", "indoors", True, "stative"),
      (4, "office", "indoors", True, "arrive")]),
]


_TRAIL_PUNCT = ".,;:!?\"')]}"
_LEAD_PUNCT = "\"'([{"


def _tok(s):
    """Whitespace + punctuation tokenization. 2026-09-16 (strategy, pri 137 landing / LOCATED item 17): the docstring
    promised trailing-punct splitting but the body only split on whitespace, so 64 of 615 tokens (10.4%) reached the
    reader as 'room.' / 'hall.' and were tagged PUNCT -- an INSTRUMENT defect (the gold is sentence-indexed, so the key
    does not move). Measured by pri 137: weak reader 0.4255 -> 0.5319 (+0.1064 CI[+0.0213,+0.1915]); the product
    named-ground lever +0.2128 CI-sep on the old tokens, +0.1277 CI[-0.0426,+0.2979] on corrected tokens (same sign,
    not separated) -- both numbers are on the landing record."""
    out = []
    for w in s.split():
        lead = []
        while len(w) > 1 and w[0] in _LEAD_PUNCT:
            lead.append(w[0]); w = w[1:]
        trail = []
        while len(w) > 1 and w[-1] in _TRAIL_PUNCT:
            trail.append(w[-1]); w = w[:-1]
        out.extend(lead); out.append(w); out.extend(reversed(trail))
    return out


def write_conll(passage, outdir):
    """Emit a LitBank-style CoNLL with a single protagonist coref cluster (0) on every alias token."""
    pid, name, aliases, sents, _gold = passage
    alset = set(a.lower() for a in aliases)
    path = os.path.join(outdir, f"{pid}.conll")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(f"#begin document ({pid}); part 0\n")
        for si, s in enumerate(sents):
            for i, tok in enumerate(_tok(s)):
                bare = tok.lower().strip(".,;:!?\"'()")
                coref = "(0)" if bare in alset else "_"
                cols = [pid, "0", str(i), tok] + ["_"] * 8 + [coref]
                f.write("\t".join(cols) + "\n")
            f.write("\n")
    return path


def build_gold(passage):
    pid, name, aliases, sents, timeline = passage
    return [{"book": pid, "cluster": 0, "name": name, "t": t, "node": node, "region": reg,
             "present": pres, "kind": kind, "quote": ""} for (t, node, reg, pres, kind) in timeline]


def build_items(pid, gold_rows, conll_path):
    sents, by_sent, names, persons = build_backbone(conll_path)
    mentions, _ = parse_litbank_conll(conll_path)
    places = _place_positions(sents)
    ev = extract_events_in_substrate(sents, by_sent, person_clusters=persons, realis_gate=True,
                                     discovery_gate=True, embedded_route=True, caused_motion_theme=True,
                                     stative_expand=True)
    reg = fold_tracker(sorted(persons), ev, n_clauses=len(sents), prior_fold=True)
    import zlib
    rng = np.random.default_rng(SEED + (zlib.crc32(pid.encode()) % 100000))
    twins = _twin_registers(sorted(persons), ev, len(sents), rng, TWIN_R)
    rows = sorted(gold_rows, key=lambda r: r["t"])
    first_t = rows[0]["t"]
    last_t = min(len(sents) - 1, rows[-1]["t"] + 20)
    ment_ts = sorted({m["sent_idx"] for m in mentions if m["cluster"] == 0 and first_t <= m["sent_idx"] <= last_t})
    items = []
    gold_tl = {(pid, 0): rows}
    for t in ment_ts:
        g = gold_at(rows, t)
        if g is None:
            continue
        gnode, greg, gpres, gov_t = g
        mgidx = _mention_gidx(sents, mentions, 0, t)
        items.append({
            "book": pid, "cluster": 0, "t": t, "tl_key": pid, "gold_node": gnode, "gold_region": greg,
            "gold_present": gpres, "dist": t - gov_t,
            "REGISTER_prior_ext": reg.where_is("0", t),
            "FLOOR_abstain": None,
            "FLOOR_lastment": floor_lastment(places, mgidx, t),
            "FLOOR_firstloc": floor_firstloc(places, t),
            "TWIN_null": [tw.where_is("0", t) for tw in twins],
        })
    q = extraction_quality(gold_tl, ev)
    return items, q, (1 if len(persons) >= 1 else 0)


def run(smoke=False, n_boot=2000):
    # 2026-09-16 (strategy, pri 137 landing; the owner's Q115 ruling): a NEW cell writes only through the
    # seed-checkpoint helper so every run is re-runnable and isolated by HDLAB_EXP_NAME.
    from experiments._seed_checkpoint import get_output_dir
    outdir = get_output_dir(ANCHOR + ("_smoke" if smoke else ""))
    conlldir = os.path.join(outdir, "conll")
    os.makedirs(conlldir, exist_ok=True)
    passages = PASSAGES[:3] if smoke else PASSAGES
    all_items, gold_all, quals = [], [], []
    with open(os.path.join(outdir, "gold.jsonl"), "w", encoding="utf-8") as gf:
        for p in passages:
            cp = write_conll(p, conlldir)
            grows = build_gold(p)
            for r in grows:
                gf.write(json.dumps(r, ensure_ascii=True) + "\n")
            items, q, _ok = build_items(p[0], grows, cp)
            all_items.extend(items)
            gold_all.extend(grows)
            quals.append(q)
    rng = np.random.default_rng(SEED)

    def pop(arm):
        xs = [correct(it.get(arm), it["gold_node"]) for it in all_items if arm in it]
        return float(np.mean(xs)) if xs else None
    R = len(all_items[0]["TWIN_null"]) if all_items else 0
    null_acc = [float(np.mean([correct(it["TWIN_null"][r], it["gold_node"]) for it in all_items]))
                for r in range(R)] if all_items else [0]
    p95 = float(np.percentile(null_acc, 95))
    reg_acc = pop("REGISTER_prior_ext")
    gate_floor = boot_paired(all_items, "REGISTER_prior_ext", "FLOOR_lastment", n_boot, rng)
    gate_abst = boot_paired(all_items, "REGISTER_prior_ext", "FLOOR_abstain", n_boot, rng)
    # micro extraction quality
    gp = sum(q["gold_change_points"] for q in quals)
    rc = sum(q["recall"] * q["gold_change_points"] for q in quals)
    nr = sum(q["node_recall"] * q["gold_change_points"] for q in quals)
    ne = sum(q["n_events"] for q in quals)
    pr = sum(q["precision"] * q["n_events"] for q in quals)
    reg_region = float(np.mean([region_of_node(it.get("REGISTER_prior_ext")) == it["gold_region"] for it in all_items]))
    reg_present = float(np.mean([(it.get("REGISTER_prior_ext") == DEICTIC_SCENE) == bool(it["gold_present"]) for it in all_items]))
    out = {
        "anchor_name": ANCHOR, "run_mode": "smoke" if smoke else "full", "seed": SEED,
        "note": "AUTHOR-CONSTRUCTED modern prose (corpus-age control; weaker than a found corpus, labeled).",
        "n_passages": len(passages), "n_items": len(all_items),
        "pop_acc": {"REGISTER_prior_ext": reg_acc, "FLOOR_lastment": pop("FLOOR_lastment"),
                    "FLOOR_firstloc": pop("FLOOR_firstloc"), "FLOOR_abstain": pop("FLOOR_abstain")},
        "twin_null": {"R": R, "mean": float(np.mean(null_acc)), "p95": p95,
                      "register_beats_p95": bool(reg_acc > p95)},
        "gates": {"vs_lastment": gate_floor, "vs_abstain": gate_abst},
        "region_acc": reg_region, "present_acc": reg_present,
        "extraction_quality": {"recall": rc / max(gp, 1), "node_recall": nr / max(gp, 1),
                               "precision": pr / max(ne, 1), "gold_change_points": gp, "n_events": ne},
    }
    with open(os.path.join(outdir, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    return out


def _print(o):
    print(f"[MODERN {o['run_mode']}] passages={o['n_passages']} items={o['n_items']}  "
          f"(AUTHOR-CONSTRUCTED corpus-age control)")
    print("  pop_acc:", {k: round(v, 3) for k, v in o["pop_acc"].items() if v is not None})
    g = o["gates"]["vs_lastment"]
    print(f"  REGISTER_prior_ext {g['a_mean']:.3f} vs last-mention {g['b_mean']:.3f}: delta {g['delta']:+.3f} "
          f"[{g['lo']:+.3f},{g['hi']:+.3f}] CI-sep={g['CI_separated']}")
    print(f"  vs abstain: CI-sep={o['gates']['vs_abstain']['CI_separated']}; "
          f"twin null p95={o['twin_null']['p95']:.3f} register_beats={o['twin_null']['register_beats_p95']}")
    print(f"  region={o['region_acc']:.3f} present={o['present_acc']:.3f}  "
          f"extraction recall={o['extraction_quality']['recall']:.3f} "
          f"node={o['extraction_quality']['node_recall']:.3f} prec={o['extraction_quality']['precision']:.3f}")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="full")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--n-boot", type=int, default=2000)
    a = ap.parse_args()
    _print(run(smoke=a.smoke or a.mode == "smoke", n_boot=a.n_boot))
