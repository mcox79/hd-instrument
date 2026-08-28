"""exp_location_register_distance_v1 -- PROVE the location register is a maintained STATE across the whole
narrative, not a local read: an entity's location is recoverable at ARBITRARY distance from the motion event.

CLAIM (Zwaan incremental situation model; the SPACE dimension is carried across the narrative): once X moves
to L1, "where is X?" stays L1 no matter how many neutral sentences intervene before the query. A reader that
only looks at a LOCAL window loses the location once the motion scrolls out of view -- which is exactly why a
stateless last-mention / recent-scene heuristic fails and a register does not.

DESIGN: X: L0 -> (real motion) -> L1. Insert K neutral fillers between the move and a final locationless
mention of X, sweep K in {0,2,5,10,20}. Score "where is X?" = L1.
  REGISTER   over the whole text -- should stay ~1.0 for all K (the interval opened at the move persists).
  WINDOWED   register over only the last 3 sentences -- loses the move for K>=2, collapses toward chance.
  LAST_MENTION_LOC the strongest stateless floor -- grabs the nearest location token to X's final mention
                   (a filler distractor), collapses as K grows.
  TWIN       register over a shuffled-order variant -- info-free, at floor.

If REGISTER stays high while WINDOWED and LAST_MENTION collapse, the register's value IS the maintained
state, localised (the mechanism, not a lexical artifact). Light, spaCy-bound -> runs INLINE (remote has no
spaCy). Writes ONLY to data/exp_location_register_distance_v1[/ _smoke]. NO hdlab writes. ASCII only.
"""
from __future__ import annotations
import argparse, json, os, sys, time
from datetime import datetime, timezone
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from experiments.location_register import LocationRegister
from experiments import exp_location_register_where_is_x_v1 as W

ANCHOR = "location_register_distance_v1"
KS = [0, 2, 5, 10, 20]
# neutral fillers -- NO entity alias, NO motion, but SOME mention distractor locations (so last-mention has a
# wrong-but-plausible token to grab, the realistic failure mode). Register must ignore them.
FILLERS = ["The clock ticked on the mantel.", "Rain fell steadily outside.", "The fire burned low.",
           "A lamp glowed in the {D}.", "A cart rumbled far off.", "The house was very quiet.",
           "Dust settled in the {D}.", "A bell tolled the hour.", "The wind stirred the branches.",
           "Someone had left a candle in the {D}.", "The day wore on.", "A draught moved through the {D}."]


def build(seed=20260828, n=60, smoke=False):
    rng = np.random.default_rng(seed)
    items = []
    n = 10 if smoke else n
    for k in range(n):
        name = W.NAMES[k % len(W.NAMES)]
        pr = W.PRON.get(name, ("they", "them"))[0]
        places = list(rng.permutation(W.PLACES))
        L0, L1, D = places[0], places[1], places[2]   # D = distractor location for the fillers
        dv = W.DEPART_VERBS[k % len(W.DEPART_VERBS)]
        items.append({"name": name, "aliases": W.aliases_for(name), "pr": pr,
                      "L0": L0, "L1": L1, "D": D, "dv": dv, "gold": L1})
    return items


def assemble(it, K):
    setup = f"{it['name']} sat in the {it['L0']}."
    move = W._depart_sentence(it["name"], it["dv"], it["L1"])
    fills = [W.FILLERS[0]] * 0
    fills = [FILLERS[(i + hash(it["name"]) % len(FILLERS)) % len(FILLERS)].replace("{D}", it["D"])
             for i in range(K)]
    final = f"{it['pr'].capitalize()} sighed and said nothing."   # locationless mention of X
    return [setup, move] + fills + [final]


def loc_tokens(s_low):
    import re
    return [p for p in W.PLACES if re.search(r"\b" + p + r"\b", s_low)]


def last_mention_loc(sents, aliases):
    import re
    low = [s.lower() for s in sents]
    arx = re.compile(r"\b(" + "|".join(re.escape(a.lower()) for a in aliases) + r")\b")
    lm = max((i for i, s in enumerate(low) if arx.search(s)), default=len(low) - 1)
    for radius in range(len(low)):
        for j in (lm - radius, lm + radius):
            if 0 <= j < len(low):
                t = loc_tokens(low[j])
                if t:
                    return t[-1]
    return "<scene>"


def run(smoke=False, seed=20260828):
    import spacy
    nlp = spacy.load("en_core_web_sm")
    items = build(seed=seed, smoke=smoke)
    rng = np.random.default_rng(seed + 1)
    rows = {}
    for K in KS:
        full, win, lastm, twin = [], [], [], []
        for it in items:
            sents = assemble(it, K)
            text = " ".join(sents)
            reg = LocationRegister(nlp); reg.read(text, {it["name"]: it["aliases"]})
            full.append(int(reg.where_is(it["name"]) == it["gold"]))
            wtext = " ".join(sents[-3:])
            wreg = LocationRegister(nlp); wreg.read(wtext, {it["name"]: it["aliases"]})
            win.append(int(wreg.where_is(it["name"]) == it["gold"]))
            lastm.append(int(last_mention_loc(sents, it["aliases"]) == it["gold"]))
            idx = list(range(len(sents))); rng.shuffle(idx)
            treg = LocationRegister(nlp); treg.read(" ".join(sents[i] for i in idx), {it["name"]: it["aliases"]})
            twin.append(int(treg.where_is(it["name"]) == it["gold"]))
        rows[K] = {"REGISTER": float(np.mean(full)), "WINDOWED": float(np.mean(win)),
                   "LAST_MENTION_LOC": float(np.mean(lastm)), "TWIN": float(np.mean(twin)), "n": len(items)}
    kmax = KS[-1]
    gates = {
        "register_robust_at_max_distance": bool(rows[kmax]["REGISTER"] >= 0.90),
        "windowed_collapses": bool(rows[kmax]["WINDOWED"] < rows[0]["WINDOWED"] - 0.2),
        "last_mention_collapses": bool(rows[kmax]["LAST_MENTION_LOC"] < 0.5),
        "register_beats_last_mention_at_max": bool(rows[kmax]["REGISTER"] > rows[kmax]["LAST_MENTION_LOC"] + 0.3),
    }
    return {"anchor_name": ANCHOR, "verdict": "HARD_PASS" if all(gates.values()) else "MIDDLE_BAND",
            "run_mode": "smoke" if smoke else "full", "seed": seed, "Ks": KS,
            "by_distance": rows, "gates": gates, "ts_iso": datetime.now(timezone.utc).isoformat()}


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
    print(f"=== {ANCHOR} ({m['run_mode']}) {m['elapsed_s']}s ===")
    print("  K    REGISTER  WINDOWED  LAST_MENTION  TWIN")
    for K in KS:
        r = m["by_distance"][K]
        print(f"  {K:<4d} {r['REGISTER']:.3f}     {r['WINDOWED']:.3f}     {r['LAST_MENTION_LOC']:.3f}         {r['TWIN']:.3f}")
    print("VERDICT:", m["verdict"], "GATES:", m["gates"])
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
