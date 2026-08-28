"""exp_location_register_where_is_x_v1 -- validate the per-entity LOCATION REGISTER on "where is entity X
at time T?" against the strongest STATELESS floors, with an info-free twin that must LOSE.

THE MISSING ORGAN (Zwaan & Radvansky event-indexing SPACE dimension; PINNED brain-foundational): a reader
maintains, per entity, WHERE it is over narrative time -- a STATE carried across the whole narrative,
updated only at motion events. The situation-model organs bind (entity, role, event) but track NO location.
This cell tests whether a first-class register (experiments/location_register.LocationRegister) answers
"where is X now?" better than the stateless heuristics a bag-of-mentions reader would use.

THE TEST (construction gold, real motion verbs, by-construction labels -- high n, tight CI):
  Each item is a short narrative about ONE tracked entity moving among NAMED location nodes, built from a
  diverse pool of REAL English motion verbs (went/walked/hurried/hastened/slipped/withdrew/returned/came
  back/...) and real place nouns. Four discriminating STRUCTURES, each defeating a different stateless floor:
    PERSIST  X: L0 -> L1, then a mention of X with NO location -> gold L1 (register carries the state;
             last-mention-loc grabs a misleading nearby scene token).
    REENTRY  X: L0 -> L1 -> back -> gold the scene/L0 (last-KNOWN-named would freeze at L1).
    STALE    X: L0 -> L1 while the narrative dwells on L0 (another entity there) -> gold L1
             (most-recent-scene and last-mention-loc both say L0).
    MULTIHOP X: L0 -> L1 -> L2 -> gold L2 (first-loc / most-frequent say L0).
  Query = "where is X at the final clause?"  Gold = the node by construction. Exact-match node accuracy.

ARMS (recompute every floor on the SAME population):
  REGISTER         the location register (mine).
  FIRST_LOC        X's first stated location node (fails on any move).
  LAST_MENTION_LOC the location token nearest X's most recent mention (strongest stateless floor).
  MOST_FREQ_LOC    the node most frequently near X.
  RECENT_SCENE     the most recently mentioned location anywhere (the narrative's current scene).
  TWIN             the register run on a SHUFFLED-ORDER variant (motion events permuted) -- same mechanism,
                   same clauses, temporal information destroyed. Must LOSE (info-free).
POSITIVE CONTROL: per-STRUCTURE accuracy is reported, so a null is interpretable -- REENTRY/STALE are the
  cases the register must get and LAST_MENTION_LOC must miss.

Writes ONLY to data/exp_location_register_where_is_x_v1[/ _smoke]. NO hdlab writes. ASCII only.
Remote-safe: spaCy import inside run(); bare invocation == FULL; declares its data deps as KB_REFERENT.
# KB_REFERENT: data/mine_presence_phrasings_v1/phrasings.jsonl
"""
from __future__ import annotations
import argparse, json, os, re, sys, time
from collections import Counter, defaultdict
from datetime import datetime, timezone

os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments.location_register import LocationRegister, DEICTIC_SCENE, AWAY, canon_node

ANCHOR = "location_register_where_is_x_v1"

# Named location nodes (topological scene membership -- the situation model's SPACE granularity).
PLACES = ["garden", "kitchen", "study", "cellar", "orchard", "stable", "library", "nursery",
          "meadow", "barn", "attic", "shop", "field", "gallery", "greenhouse", "workshop"]
# REAL English self-motion verbs (diverse; PATH lives in the satellite/PP, not a manner whitelist).
DEPART_VERBS = ["went", "walked", "hurried", "hastened", "slipped", "strode", "wandered", "stepped",
                "crept", "hurried off", "made his way", "set off", "withdrew", "retired", "stole"]
RETURN_VERBS = ["came back", "returned", "came in again", "went back", "hurried back", "made his way back"]
# neutral fillers (no entity alias, no motion) -- must not change any register state.
FILLERS = ["The clock ticked on the mantel.", "Rain fell steadily outside.", "The fire burned low.",
           "It was a grey afternoon.", "A cart rumbled far off.", "The house was very quiet.",
           "Dust settled on the sill.", "A bell tolled the hour.", "The wind stirred the branches.",
           "The day wore on."]
NAMES = ["Anna", "Thomas", "Clara", "Walter", "Susan", "Henry", "Margaret", "Edwin", "Mary", "James"]
OTHERS = ["the old woman", "the maid", "his cousin", "the boy", "a neighbour", "her aunt"]
PRON = {"Anna": ("she", "her"), "Clara": ("she", "her"), "Susan": ("she", "her"), "Margaret": ("she", "her"),
        "Mary": ("she", "her"), "Thomas": ("he", "him"), "Walter": ("he", "him"), "Henry": ("he", "him"),
        "Edwin": ("he", "him"), "James": ("he", "him")}


def aliases_for(name):
    p = PRON.get(name, ("they", "them"))
    return [name, p[0], p[1], "his", "her", "their"]


def _depart_sentence(name, verb, place):
    """A real motion verb + a GOAL PP naming the destination (Goal-over-Source)."""
    if verb in ("withdrew", "retired", "stole"):
        return f"{name} {verb} to the {place}."
    if verb == "made his way":
        return f"{name} made his way to the {place}."
    if verb == "set off":
        return f"{name} set off for the {place}."
    return f"{name} {verb} out to the {place}." if verb in ("went", "hurried", "slipped", "stepped", "crept") \
        else f"{name} {verb} to the {place}."


def build_items(seed=20260828, n_per_type=60):
    rng = np.random.default_rng(seed)
    items = []
    types = ["PERSIST", "REENTRY", "STALE", "MULTIHOP"]
    for ti, typ in enumerate(types):
        for k in range(n_per_type):
            name = NAMES[(ti * n_per_type + k) % len(NAMES)]
            other = OTHERS[k % len(OTHERS)]
            pr = PRON.get(name, ("they", "them"))[0]
            places = list(rng.permutation(PLACES))
            L0, L1, L2 = places[0], places[1], places[2]
            dv = DEPART_VERBS[k % len(DEPART_VERBS)]
            dv2 = DEPART_VERBS[(k + 5) % len(DEPART_VERBS)]
            rv = RETURN_VERBS[k % len(RETURN_VERBS)]
            fill = FILLERS[k % len(FILLERS)]
            start = f"{name} sat in the {L0}."          # stative locative sets the starting node
            if typ == "PERSIST":
                # a DISTRACTOR location (L2) glows right before X's final, locationless mention -> last-
                # mention-loc grabs L2 (wrong); the register carries L1 forward.
                sents = [start, _depart_sentence(name, dv, L1),
                         f"A lamp glowed in the {L2}.",
                         f"{pr.capitalize()} sighed and said nothing."]  # locationless mention of X
                gold = L1
            elif typ == "REENTRY":
                sents = [start, _depart_sentence(name, dv, L1), f"{name} {rv}.", fill]
                gold = DEICTIC_SCENE
            elif typ == "STALE":
                sents = [start, _depart_sentence(name, dv, L1),
                         f"{other.capitalize()} remained in the {L0}, tidying the room.",  # scene dwells on L0
                         f"{other.capitalize()} lit a candle in the {L0}."]
                gold = L1
            else:  # MULTIHOP
                sents = [start, _depart_sentence(name, dv, L1), _depart_sentence(name, dv2, L2), fill]
                gold = L2
            items.append({"id": f"{typ}_{k:03d}", "type": typ, "name": name, "aliases": aliases_for(name),
                          "L0": L0, "L1": L1, "L2": L2, "sents": sents, "gold": gold,
                          "text": " ".join(sents)})
    rng.shuffle(items)
    return items


# ---- stateless floors (each a function item -> predicted node) --------------------------------------
def _loc_tokens_in(s_low):
    return [p for p in PLACES if re.search(r"\b" + p + r"\b", s_low)]


def floor_first_loc(item, sents_low):
    for s in sents_low:
        toks = _loc_tokens_in(s)
        if toks:
            return toks[0]
    return DEICTIC_SCENE


def floor_last_mention_loc(item, sents_low):
    """Location token nearest the entity's MOST RECENT mention (the strongest stateless heuristic)."""
    al = [a.lower() for a in item["aliases"]]
    arx = re.compile(r"\b(" + "|".join(re.escape(a) for a in al) + r")\b")
    last_ment = None
    for i, s in enumerate(sents_low):
        if arx.search(s):
            last_ment = i
    if last_ment is None:
        return floor_first_loc(item, sents_low)
    # search outward from the mention sentence for the nearest location token
    for radius in range(0, len(sents_low)):
        for j in (last_ment - radius, last_ment + radius):
            if 0 <= j < len(sents_low):
                toks = _loc_tokens_in(sents_low[j])
                if toks:
                    return toks[-1]
    return DEICTIC_SCENE


def floor_most_freq_loc(item, sents_low):
    c = Counter()
    for s in sents_low:
        for p in _loc_tokens_in(s):
            c[p] += 1
    return c.most_common(1)[0][0] if c else DEICTIC_SCENE


def floor_recent_scene(item, sents_low):
    """Most recently mentioned location anywhere = the narrative's current scene."""
    for s in reversed(sents_low):
        toks = _loc_tokens_in(s)
        if toks:
            return toks[-1]
    return DEICTIC_SCENE


def shuffled_twin_text(item, rng):
    """Info-free twin: permute the ORDER of the entity's motion/stative sentences (keep fillers in place).
    Same mechanism, same clauses, temporal information destroyed -> register ends at a random node."""
    sents = item["sents"]
    idx = list(range(len(sents)))
    rng.shuffle(idx)
    return " ".join(sents[i] for i in idx)


def boot_ci(vals, n_boot=2000, seed=0):
    if not vals:
        return (0.0, 0.0, 0.0, 0.0)
    a = np.asarray(vals, float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(a), size=(n_boot, len(a)))
    m = a[idx].mean(axis=1)
    lo, hi = np.percentile(m, [2.5, 97.5])
    return float(a.mean()), float(lo), float(hi), float((hi - lo) / 2.0)


def run(smoke=False, seed=20260828):
    import spacy
    nlp = spacy.load("en_core_web_sm")
    items = build_items(seed=seed, n_per_type=8 if smoke else 60)

    reg_hit, first_hit, lastm_hit, freq_hit, recent_hit = ([] for _ in range(5))
    per_type = defaultdict(lambda: defaultdict(list))
    R_NULL = 6 if smoke else 25   # population reshuffles for the info-free null band
    twin_pred_by_item = []        # per item: list of R shuffled-order predictions
    rng = np.random.default_rng(seed + 3)
    for it in items:
        sents_low = [s.lower() for s in it["sents"]]
        reg = LocationRegister(nlp)
        reg.read(it["text"], {it["name"]: it["aliases"]})
        pred = reg.where_is(it["name"])
        g = it["gold"]
        reg_hit.append(int(pred == g))
        first = floor_first_loc(it, sents_low); lastm = floor_last_mention_loc(it, sents_low)
        freq = floor_most_freq_loc(it, sents_low); recent = floor_recent_scene(it, sents_low)
        first_hit.append(int(first == g)); lastm_hit.append(int(lastm == g))
        freq_hit.append(int(freq == g)); recent_hit.append(int(recent == g))
        # twin: register on R shuffled orders -> R predictions (info-free: same clauses, order destroyed)
        preds = []
        for _ in range(R_NULL):
            treg = LocationRegister(nlp)
            treg.read(shuffled_twin_text(it, rng), {it["name"]: it["aliases"]})
            preds.append(int(treg.where_is(it["name"]) == g))
        twin_pred_by_item.append(preds)
        per_type[it["type"]]["REGISTER"].append(int(pred == g))
        per_type[it["type"]]["LAST_MENTION_LOC"].append(int(lastm == g))
        per_type[it["type"]]["RECENT_SCENE"].append(int(recent == g))

    rm, rlo, rhi, rhw = boot_ci(reg_hit, seed=seed + 1)
    fm = float(np.mean(first_hit)); flo, fhi = boot_ci(first_hit, seed=seed + 6)[1:3]
    lm, llo, lhi, lhw = boot_ci(lastm_hit, seed=seed + 2)
    qm = float(np.mean(freq_hit)); rcm, rclo, rchi, rchw = boot_ci(recent_hit, seed=seed + 4)
    # TWIN population accuracy = mean over the R reshuffles (a per-reshuffle population accuracy each);
    # null band = 95th pct of the R population accuracies (the info-free ceiling the register must clear).
    tw_arr = np.asarray(twin_pred_by_item, float)          # (n_items, R)
    twin_pop_by_shuffle = tw_arr.mean(axis=0)              # (R,) population accuracy per reshuffle
    tm = float(twin_pop_by_shuffle.mean())
    tlo, thi = float(twin_pop_by_shuffle.min()), float(twin_pop_by_shuffle.max())
    null_p95 = float(np.percentile(twin_pop_by_shuffle, 95))
    strongest_floor = max(lm, fm, qm, rcm)
    strongest_floor_hi = max(lhi, fhi, boot_ci(freq_hit, seed=seed + 7)[2], rchi)

    gates = {
        "register_beats_strongest_floor_ci": bool(rlo > strongest_floor_hi),
        "register_beats_last_mention_ci": bool(rlo > lhi),
        "register_beats_infofree_twin_ci": bool(rlo > thi),          # twin's BEST reshuffle < register lo
        # info-free twin collapses to FLOOR level (destroying temporal order removes the register's entire
        # advantage) -- the register's win is 100% correctly-ordered tracking, not a lexical artifact.
        "twin_at_floor_not_signal": bool(abs(tm - strongest_floor) < 0.12 and tm < rlo),
    }
    verdict = "HARD_PASS" if all(gates.values()) else ("MIDDLE_BAND" if gates["register_beats_last_mention_ci"] else "HARD_FAIL")
    metrics = {
        "anchor_name": ANCHOR, "verdict": verdict, "run_mode": "smoke" if smoke else "full",
        "seed": seed, "n_items": len(items),
        "accuracy": {
            "REGISTER": {"acc": rm, "ci": [rlo, rhi], "hw": rhw},
            "FIRST_LOC": {"acc": fm, "ci": [flo, fhi]},
            "LAST_MENTION_LOC": {"acc": lm, "ci": [llo, lhi], "hw": lhw},
            "MOST_FREQ_LOC": {"acc": qm},
            "RECENT_SCENE": {"acc": rcm, "ci": [rclo, rchi]},
            "TWIN_shuffled": {"acc": tm, "range": [tlo, thi], "R": R_NULL},
        },
        "strongest_floor": strongest_floor, "strongest_floor_hi": strongest_floor_hi,
        "null_p95_shuffled": null_p95,
        "per_type": {t: {a: float(np.mean(v)) for a, v in d.items()} | {"n": len(d["REGISTER"])}
                     for t, d in per_type.items()},
        "gates": gates,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    return metrics, items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true"); ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--mode", default="full"); ap.add_argument("--seed", type=int, default=20260828)
    args = ap.parse_args()
    smoke = bool(args.smoke) or args.self_test or args.mode == "smoke"   # bare invocation == FULL
    out = os.path.join(REPO, "data", f"exp_{ANCHOR}" + ("_smoke" if smoke else ""))
    os.makedirs(out, exist_ok=True)
    t0 = time.time()
    metrics, items = run(smoke=smoke, seed=args.seed)
    metrics["elapsed_s"] = round(time.time() - t0, 1)
    tmp = os.path.join(out, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(out, "metrics.json"))
    with open(os.path.join(out, "gold_items.jsonl"), "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it) + "\n")
    a = metrics["accuracy"]
    print(f"=== {ANCHOR} ({metrics['run_mode']}) {metrics['elapsed_s']}s  n={metrics['n_items']} ===")
    print(f"WHERE-IS-X node accuracy:")
    for k in ["REGISTER", "LAST_MENTION_LOC", "RECENT_SCENE", "FIRST_LOC", "MOST_FREQ_LOC", "TWIN_shuffled"]:
        ci = a[k].get("ci")
        cis = f" [{ci[0]:.3f},{ci[1]:.3f}]" if ci else ""
        print(f"  {k:18s} {a[k]['acc']:.3f}{cis}")
    print(f"  strongest_floor={metrics['strongest_floor']:.3f} (hi={metrics['strongest_floor_hi']:.3f})  "
          f"null_p95(shuffled)={metrics['null_p95_shuffled']:.3f}")
    print("PER-TYPE (register / last_mention / recent_scene):")
    for t, d in metrics["per_type"].items():
        print(f"  {t:9s} n={d['n']:3d}  reg={d['REGISTER']:.3f}  lastm={d['LAST_MENTION_LOC']:.3f}  recent={d['RECENT_SCENE']:.3f}")
    print(f"VERDICT: {metrics['verdict']}   GATES:")
    for k, v in metrics["gates"].items():
        print(f"  {'PASS' if v else 'fail'}  {k}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
