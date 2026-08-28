"""exp_location_register_hierarchy_v1 -- the HIERARCHICAL / region-based extension: the register answers
SCENE-MEMBERSHIP at multiple granularities ("is X in the house?" when X is in the study) that a FLAT
exact-node register cannot.

BRAIN FRAME: the cognitive map is organized into nested REGIONS, not a flat set of places (region-based
navigation, Wiener & Mallot 2003; hierarchical spatial memory, Hirtle & Jonides 1985; McNamara regional
hierarchies). A reader who knows a character is in the study also knows she is in the house. The register
builds a shallow place-containment relation (curated room/outdoor taxonomy + WordNet part-meronymy) so
`is_in_region(X, 'house')` resolves via ancestry.

THE TEST: an entity moves to a fine location (a ROOM or an OUTDOOR place); query "is X indoors / in the
house?" and "is X outdoors?". Gold by construction (room -> indoors=True/outdoors=False; outdoor place ->
indoors=False/outdoors=True). Arms:
  HIERARCHICAL   region-based containment (mine) -- should resolve both.
  FLAT_EXACT     the fine node must EQUAL the query word (study == 'house' -> False) -- the ablation of the
                 hierarchy; fails every room-in-house / place-outdoors query.
  STRING_MATCH   the query word appears in the sentence with the entity -- a lexical floor.
  TWIN           region assigned at random (info-free) -- must lose.

Writes ONLY to data/exp_location_register_hierarchy_v1[/ _smoke]. NO hdlab writes. spaCy-bound -> INLINE.
ASCII only.
"""
from __future__ import annotations
import argparse, json, os, re, sys, time
from datetime import datetime, timezone
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from experiments.location_register import LocationRegister, INDOORS, OUTDOORS, spatial_region, canon_node

ANCHOR = "location_register_hierarchy_v1"
ROOMS = ["study", "kitchen", "nursery", "library", "parlour", "cellar", "attic", "pantry", "gallery", "hall"]
OUTS = ["garden", "orchard", "meadow", "field", "stable", "barn", "yard", "shore", "wood", "lane"]
MOTION = ["walked", "hurried", "went", "hastened", "strode", "slipped", "crept", "wandered"]
NAMES = ["Anna", "Thomas", "Clara", "Walter", "Susan", "Henry", "Margaret", "Edwin", "Mary", "James"]


def build_items(seed=20260828, n=120, smoke=False):
    rng = np.random.default_rng(seed)
    items = []
    n = 16 if smoke else n
    for k in range(n):
        name = NAMES[k % len(NAMES)]
        indoor = bool(k % 2)
        place = (ROOMS if indoor else OUTS)[int(rng.integers(0, 10))]
        mv = MOTION[k % len(MOTION)]
        prep = "to" if indoor else "out to"
        text = f"{name} sat by the fire. {name} {mv} {prep} the {place}."
        # two queries per item: 'in the house?' and 'outdoors?'
        items.append({"name": name, "place": place, "indoor": indoor, "text": text})
    rng.shuffle(items)
    return items


def run(smoke=False, seed=20260828):
    import spacy
    nlp = spacy.load("en_core_web_sm")
    items = build_items(seed=seed, smoke=smoke)
    rng = np.random.default_rng(seed + 1)
    hier, flat, strm, twin = [], [], [], []
    for it in items:
        name, aliases = it["name"], [it["name"], "he", "she", "him", "her", "his"]
        reg = LocationRegister(nlp); reg.read(it["text"], {name: aliases})
        low = it["text"].lower()
        for q, gold in (("house", it["indoor"]), ("outdoors", not it["indoor"])):
            # HIERARCHICAL
            h = reg.is_in_region(name, q)
            hier.append(int((h is True) == gold))
            # FLAT_EXACT: the fine node must equal the query word (never true for a room vs 'house')
            f = (reg.where_is(name) == canon_node(q))
            flat.append(int(f == gold))
            # STRING_MATCH: the query word co-occurs with the entity's last mention
            sm = bool(re.search(r"\b" + re.escape(q) + r"\b", low))
            strm.append(int(sm == gold))
            # TWIN: random region
            twin.append(int(bool(rng.integers(0, 2)) == gold))

    def boot(v, s):
        a = np.asarray(v, float); r = np.random.default_rng(s)
        m = a[r.integers(0, len(a), size=(2000, len(a)))].mean(1)
        lo, hi = np.percentile(m, [2.5, 97.5]); return float(a.mean()), float(lo), float(hi)
    hm, hlo, hhi = boot(hier, seed + 2)
    fm, flo, fhi = boot(flat, seed + 3)
    sm, slo, shi = boot(strm, seed + 4)
    tm, tlo, thi = boot(twin, seed + 5)
    strongest = max(fm, sm, tm)
    strongest_hi = max(fhi, shi, thi)
    gates = {
        "hierarchical_beats_flat_ci": bool(hlo > fhi),
        "hierarchical_beats_strongest_floor_ci": bool(hlo > strongest_hi),
        "hierarchical_beats_twin_ci": bool(hlo > thi),
    }
    return {"anchor_name": ANCHOR, "verdict": "HARD_PASS" if all(gates.values()) else "MIDDLE_BAND",
            "run_mode": "smoke" if smoke else "full", "seed": seed, "n_queries": len(hier),
            "accuracy": {"HIERARCHICAL": [hm, hlo, hhi], "FLAT_EXACT": [fm, flo, fhi],
                         "STRING_MATCH": [sm, slo, shi], "TWIN": [tm, tlo, thi]},
            "strongest_floor": strongest, "gates": gates, "ts_iso": datetime.now(timezone.utc).isoformat()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true"); ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--mode", default="full"); ap.add_argument("--seed", type=int, default=20260828)
    args = ap.parse_args()
    smoke = bool(args.smoke) or args.self_test or args.mode == "smoke"
    out = os.path.join(REPO, "data", f"exp_{ANCHOR}" + ("_smoke" if smoke else ""))
    os.makedirs(out, exist_ok=True)
    t0 = time.time()
    m = run(smoke=smoke, seed=args.seed); m["elapsed_s"] = round(time.time() - t0, 1)
    tmp = os.path.join(out, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    os.replace(tmp, os.path.join(out, "metrics.json"))
    a = m["accuracy"]
    print(f"=== {ANCHOR} ({m['run_mode']}) {m['elapsed_s']}s  n_queries={m['n_queries']} ===")
    for k in ["HIERARCHICAL", "FLAT_EXACT", "STRING_MATCH", "TWIN"]:
        print(f"  {k:13s} {a[k][0]:.3f} [{a[k][1]:.3f},{a[k][2]:.3f}]")
    print("VERDICT:", m["verdict"], "GATES:", m["gates"])
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
