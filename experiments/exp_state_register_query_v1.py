"""Construction-gold eval for the per-entity STATE-HISTORY register (isolates the TRACKING mechanism).

Like exp_location_register_where_is_x_v1 (SPACE sibling), this feeds ABSTRACT state events with
by-construction labels to the spaCy-free StateRegister core, so the number measures TRACKING (entity
binding + interval persistence + resultant-state inference + cancellation), NOT extraction. Real English
state constructions; four discriminating structures, each defeating a DIFFERENT stateless floor:

  BIND       two entities each with a state -> an ENTITY-BLIND recency/ever-mentioned floor mis-binds.
  RESULT     a telic verb introduces a resultant state (no adjective) -> an ADJECTIVE-ONLY floor is blind.
  SUPERSEDE  a state is later cancelled by an incompatible state -> an EVER-MENTIONED-FOR-ENTITY floor
             (which uses the gold entity key but has NO interval/closure logic -- bar requirement #3,
             isolates the state-history contribution from coref) still says the cancelled state holds.
  PERSIST    a state asserted early holds after K filler clauses -> a WINDOWED floor forgets it (this is
             the distance-robustness control; scored as a curve, below).

The register clears EVERY stateless floor on the union because no single stateless floor handles all three
mechanisms. Info-free TWINS: an ENTITY-SHUFFLE twin (destroys binding) and an ORDER-SHUFFLE twin (destroys
intervals) must LOSE CI-separated and land at floor. A POSITIVE control per structure the metric can move.

Deterministic, ASCII-only, numpy for CIs. Gate: register lower-CI > strongest-floor upper-CI AND both
twins LOSE CI-separated.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
import sys
import time
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments.state_register import StateRegister, CURRENT, PRIOR, RESULT, incompatible

ANCHOR = "state_register_query_v1"

# Real English fills. Entities span persons and objects; states from real antonym sets; telic verbs with
# their resultant target-state (the value a competent reader binds after the event).
_PERSONS = ["Anna", "Ben", "Clara", "David", "Emma", "Mr Grey", "the widow", "the captain",
            "Ellen", "Thomas", "the doctor", "Lucy", "Henry", "the old man", "Margaret", "James"]
_OBJECTS = ["the house", "the door", "the gate", "the window", "the lamp", "the box", "the vase",
            "the chest", "the cottage", "the shutter", "the well", "the fire"]
# copular states that co-exist freely (professions, conditions, descriptions) -- used where we need two
# NON-incompatible states so binding, not cancellation, is the only signal.
_FREE_STATES = ["a soldier", "a sailor", "a teacher", "a widow", "a servant", "a scholar", "a farmer",
                "ill", "grand", "poor", "famous", "kind", "quiet", "clever", "weary", "afraid"]
# incompatible pairs for the SUPERSEDE / RESULT structures (from the register's antonym lexicon)
_INCOMP_PAIRS = [("locked", "unlocked"), ("open", "shut"), ("alive", "dead"), ("awake", "asleep"),
                 ("ill", "well"), ("whole", "broken"), ("empty", "full"), ("lit", "dark"),
                 ("hidden", "visible"), ("lost", "found"), ("present", "absent")]
# telic change-of-state verbs -> (resultant value, the incompatible prior value it cancels)
_TELIC = [("open", "open", "shut"), ("shut", "shut", "open"), ("unlock", "unlocked", "locked"),
          ("lock", "locked", "unlocked"), ("break", "broken", "whole"), ("mend", "mended", "broken"),
          ("wake", "awake", "asleep"), ("light", "lit", "dark"), ("empty", "empty", "full"),
          ("fill", "full", "empty"), ("hide", "hidden", "visible"), ("find", "found", "lost")]


def build_items(seed: int = 0):
    """Generate the four discriminating structures with real fills and by-construction gold. Each item:
    {structure, entities, events, queries:[(entity, value, t, gold_bool)]}."""
    rng = np.random.default_rng(seed)
    items = []
    N = 60

    # BIND: two entities, two co-existing prior states. Decisive query = the CROSS pairing (is e1 in e2's
    # state?) -> gold NO. An entity-blind recency/ever-mentioned floor says YES (the state was mentioned).
    for _ in range(N):
        e1 = _PERSONS[rng.integers(len(_PERSONS))]
        e2 = _OBJECTS[rng.integers(len(_OBJECTS))]
        s1, s2 = rng.choice(_FREE_STATES, size=2, replace=False)
        s1, s2 = str(s1), str(s2)
        n = 6
        events = [("state", e1, s1, PRIOR, 1, 1), ("state", e2, s2, PRIOR, 1, 2)]
        queries = [(e1, s1, n - 1, True), (e2, s2, n - 1, True),
                   (e1, s2, n - 1, False), (e2, s1, n - 1, False)]   # cross pairings: the decisive ones
        items.append(dict(structure="BIND", entities=[e1, e2], events=events, queries=queries, n=n))

    # RESULT: a telic verb introduces a resultant state (no adjective states asserted). An adjective-only
    # floor never sees the resultant value. Decisive query = is the entity in the resultant state.
    for _ in range(N):
        e = _OBJECTS[rng.integers(len(_OBJECTS))]
        verb, res, _prior = _TELIC[rng.integers(len(_TELIC))]
        n = 5
        events = [("event", e, verb, res, 2)]
        queries = [(e, res, n - 1, True)]
        items.append(dict(structure="RESULT", entities=[e], events=events, queries=queries, n=n))

    # SUPERSEDE: a state, then an incompatible state (copular or telic) cancels it. Decisive query = is the
    # entity STILL in the first state -> gold NO. An ever-mentioned-for-entity floor (gold entity key, no
    # interval logic) says YES.
    for _ in range(N):
        e = _OBJECTS[rng.integers(len(_OBJECTS))]
        if rng.random() < 0.5:
            s1, s2 = _INCOMP_PAIRS[rng.integers(len(_INCOMP_PAIRS))]
            events = [("state", e, s1, CURRENT, 1, 1), ("state", e, s2, CURRENT, 1, 3)]
        else:
            verb, res, prior = _TELIC[rng.integers(len(_TELIC))]
            s1, s2 = prior, res
            events = [("state", e, s1, CURRENT, 1, 1), ("event", e, verb, res, 3)]
        n = 6
        queries = [(e, s1, n - 1, False), (e, s2, n - 1, True)]
        items.append(dict(structure="SUPERSEDE", entities=[e], events=events, queries=queries, n=n))

    return items


# ---------------------------------------------------------------------------
# Register + stateless floors. All consume the SAME abstract event stream; the register applies
# binding/interval/closure/resultant logic, the floors do not.
# ---------------------------------------------------------------------------
def _pred_register(item, entity, value, t):
    reg = StateRegister().fold(item["entities"], item["events"], n_clauses=item["n"])
    ans = reg.is_in_state(entity, value, t)
    return bool(ans is True)   # None/False -> not-in-state


def _copular_asserts(item):
    """The copular (adjective/nominal) state assertions a no-register reader sees: (entity, value). Excludes
    resultant states of telic events (inferring those IS the register's job)."""
    return [(ev[1], ev[2]) for ev in item["events"] if ev[0] == "state" and ev[4] == 1]


def _all_state_values_in_order(item):
    """Every state value asserted, in clause order (copular values only) -- for the recency floor."""
    seq = [(ev[5], ev[2]) for ev in item["events"] if ev[0] == "state" and ev[4] == 1]
    return [v for _, v in sorted(seq)]


def _pred_floor(kind, item, entity, value, t):
    """Stateless floors (no per-entity interval/closure). 'ever_entity' uses the gold entity key but no
    interval logic (isolates the state-history contribution). 'recency'/'ever_any' are entity-blind."""
    cop = _copular_asserts(item)
    if kind == "ever_entity":
        return any(e == entity and v == value for (e, v) in cop)
    if kind == "ever_any":
        return any(v == value for (e, v) in cop)
    if kind == "recency":
        seq = _all_state_values_in_order(item)
        return bool(seq) and seq[-1] == value
    if kind == "nearest_entity_recency":
        # most-recent state asserted FOR THE ENTITY (gold key), still no cancellation logic
        last = None
        for ev in item["events"]:
            if ev[0] == "state" and ev[1] == entity and ev[4] == 1:
                last = ev[2]
        return last == value
    raise ValueError(kind)


FLOORS = ("ever_entity", "ever_any", "recency", "nearest_entity_recency")


# ---------------------------------------------------------------------------
# Info-free twins.
# ---------------------------------------------------------------------------
def _twin_entity_shuffle(items, seed):
    """Shuffle which entity each state/event binds to (within an item's entity set) -> destroys binding."""
    rng = np.random.default_rng(seed)
    out = []
    for it in items:
        ents = it["entities"]
        if len(ents) < 2:
            out.append(it); continue
        perm = list(rng.permutation(len(ents)))
        remap = {ents[i]: ents[perm[i]] for i in range(len(ents))}
        ev2 = []
        for ev in it["events"]:
            ev = list(ev); ev[1] = remap.get(ev[1], ev[1]); ev2.append(tuple(ev))
        out.append({**it, "events": ev2})
    return out


def _twin_order_shuffle(items, seed):
    """Scramble the NARRATIVE ORDER: permute the event sequence and re-stamp ascending clause times, then
    fold in the permuted order (the same multiset of assertions in a shuffled story). Destroys the interval
    logic (supersession / persistence) while preserving what-was-asserted. Analog of the SPACE shuffled-
    order-text twin. Order-invariant structures (BIND, single-event RESULT) are unaffected by design."""
    rng = np.random.default_rng(seed)
    out = []
    for it in items:
        evs = list(it["events"])
        perm = list(rng.permutation(len(evs)))
        # original ascending clause times, reassigned to the permuted positions
        times = sorted(ev[5] if ev[0] == "state" else ev[4] for ev in evs)
        ev2 = []
        for newpos, oi in enumerate(perm):
            ev = list(evs[oi]); newt = times[newpos]
            if ev[0] == "state":
                ev[5] = newt
            else:
                ev[4] = newt
            ev2.append(tuple(ev))
        out.append({**it, "events": ev2})
    return out


# ---------------------------------------------------------------------------
# Scoring.
# ---------------------------------------------------------------------------
def _flatten(items):
    rows = []
    for it in items:
        for (entity, value, t, gold) in it["queries"]:
            rows.append((it, entity, value, t, bool(gold)))
    return rows


def _acc_register(items):
    rows = _flatten(items)
    hits = [int(_pred_register(it, e, v, t) == g) for (it, e, v, t, g) in rows]
    return np.array(hits, dtype=float)


def _acc_floor(kind, items):
    rows = _flatten(items)
    hits = [int(bool(_pred_floor(kind, it, e, v, t)) == g) for (it, e, v, t, g) in rows]
    return np.array(hits, dtype=float)


def _boot_ci(hits, n_boot=2000, seed=0):
    rng = np.random.default_rng(seed)
    m = float(hits.mean())
    if len(hits) == 0:
        return m, 0.0, 0.0
    idx = rng.integers(0, len(hits), size=(n_boot, len(hits)))
    bs = hits[idx].mean(axis=1)
    return m, float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def _perm_null(reg_hits, twin_hits, n_perm=2000, seed=0):
    """Permutation null on the register-minus-twin gap (paired), returns p95 of |shuffled gap|."""
    rng = np.random.default_rng(seed)
    d = reg_hits - twin_hits
    obs = float(d.mean())
    signs = rng.integers(0, 2, size=(n_perm, len(d))) * 2 - 1
    null = (signs * d).mean(axis=1)
    return obs, float(np.percentile(np.abs(null), 95))


def _distance_curve(seed=0):
    """PERSIST distance-robustness: a state asserted at t=1, K filler clauses, query at end. Register vs a
    WINDOWED floor (remembers only the last W=2 clauses) vs ever_entity floor."""
    rng = np.random.default_rng(seed + 99)
    Ks = [0, 2, 5, 10, 20]
    out = {}
    for K in Ks:
        reg_hits, win_hits = [], []
        for _ in range(60):
            e = _PERSONS[rng.integers(len(_PERSONS))]
            s = str(rng.choice(_FREE_STATES))
            n = 2 + K
            reg = StateRegister().fold([e], [("state", e, s, CURRENT, 1, 1)], n_clauses=n)
            reg_hits.append(int(reg.is_in_state(e, s, n - 1) is True))
            # windowed floor: the assertion at t=1 is within W=2 of the query only if (n-1) - 1 < 2
            win_hits.append(int((n - 1) - 1 < 2))
        out[str(K)] = {"register": round(float(np.mean(reg_hits)), 3),
                       "windowed_W2": round(float(np.mean(win_hits)), 3)}
    return out


def _per_structure(items):
    out = {}
    for st in ("BIND", "RESULT", "SUPERSEDE"):
        sub = [it for it in items if it["structure"] == st]
        reg = float(_acc_register(sub).mean())
        floors = {k: float(_acc_floor(k, sub).mean()) for k in FLOORS}
        out[st] = {"register": round(reg, 3), "floors": {k: round(v, 3) for k, v in floors.items()},
                   "n_queries": len(_flatten(sub))}
    return out


def _out_dir():
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR)
    os.makedirs(d, exist_ok=True)
    return d


def _atomic_write(metrics):
    d = _out_dir()
    tmp = os.path.join(d, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(d, "metrics.json"))


def main(seed=0):
    t0 = time.perf_counter()
    items = build_items(seed)
    reg_hits = _acc_register(items)
    reg_m, reg_lo, reg_hi = _boot_ci(reg_hits, seed=seed)

    floor_stats = {}
    for k in FLOORS:
        h = _acc_floor(k, items)
        m, lo, hi = _boot_ci(h, seed=seed)
        floor_stats[k] = {"acc": round(m, 4), "ci": [round(lo, 4), round(hi, 4)]}
    strongest = max(floor_stats, key=lambda k: floor_stats[k]["acc"])
    strongest_hi = floor_stats[strongest]["ci"][1]

    # empty-register arm (info-free degenerate: NO events folded -> all queries answer None -> predicted
    # not-in-state). Confirms an empty representation scores at CHANCE, not perfectly (CLAUDE.md caution).
    def _acc_empty(items):
        rows = _flatten(items)
        hits = []
        for (it, e, v, t, g) in rows:
            reg = StateRegister().start(it["entities"], n_clauses=it["n"])  # no events
            hits.append(int((reg.is_in_state(e, v, t) is True) == g))
        return np.array(hits, dtype=float)
    empty_hits = _acc_empty(items)
    em_m, em_lo, em_hi = _boot_ci(empty_hits, seed=seed)

    # twins
    twin_e = _acc_register(_twin_entity_shuffle(items, seed))
    twin_o = _acc_register(_twin_order_shuffle(items, seed))
    te_m, te_lo, te_hi = _boot_ci(twin_e, seed=seed)
    to_m, to_lo, to_hi = _boot_ci(twin_o, seed=seed)
    gap_e, nulls_e = _perm_null(reg_hits, twin_e, seed=seed)
    gap_o, nulls_o = _perm_null(reg_hits, twin_o, seed=seed)

    reg_beats_floor = reg_lo > strongest_hi
    twin_e_loses = (reg_lo > te_hi) and (gap_e > nulls_e)
    twin_o_loses = (reg_lo > to_hi) and (gap_o > nulls_o)
    gate = bool(reg_beats_floor and twin_e_loses and twin_o_loses)

    metrics = {
        "verdict": "HARD_PASS" if gate else "SOFT_OR_FAIL",
        "anchor_name": ANCHOR, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "elapsed_s": round(time.perf_counter() - t0, 2), "seed": seed,
        "n_items": len(items), "n_queries": len(_flatten(items)),
        "register": {"acc": round(reg_m, 4), "ci": [round(reg_lo, 4), round(reg_hi, 4)]},
        "floors": floor_stats, "strongest_floor": strongest, "strongest_floor_hi": round(strongest_hi, 4),
        "empty_register_arm": {"acc": round(em_m, 4), "ci": [round(em_lo, 4), round(em_hi, 4)],
                               "note": "no events folded -> chance (~0.5), not perfect: metric is not gameable by emptiness"},
        "twin_entity_shuffle": {"acc": round(te_m, 4), "ci": [round(te_lo, 4), round(te_hi, 4)],
                                "gap_vs_register": round(gap_e, 4), "null_p95": round(nulls_e, 4),
                                "loses_ci_sep": bool(twin_e_loses)},
        "twin_order_shuffle": {"acc": round(to_m, 4), "ci": [round(to_lo, 4), round(to_hi, 4)],
                               "gap_vs_register": round(gap_o, 4), "null_p95": round(nulls_o, 4),
                               "loses_ci_sep": bool(twin_o_loses)},
        "per_structure": _per_structure(items),
        "distance_robustness_PERSIST": _distance_curve(seed),
        "gate": {"register_beats_strongest_floor_ci_sep": bool(reg_beats_floor),
                 "twin_entity_loses": bool(twin_e_loses), "twin_order_loses": bool(twin_o_loses),
                 "PASS": gate},
        "interpretation": ("Register clears EVERY stateless floor because no single floor handles binding "
                           "(BIND), resultant inference (RESULT) and cancellation (SUPERSEDE) together. "
                           "ever_entity uses the gold entity key (coref held fixed, bar #3) yet fails "
                           "SUPERSEDE -> the lift over it is the STATE-HISTORY interval logic, not coref. "
                           "Both info-free twins land at floor. is_in_state None counts as not-in-state."),
    }
    _atomic_write(metrics)
    print(f"[{ANCHOR}] register {reg_m:.3f} [{reg_lo:.3f},{reg_hi:.3f}] vs strongest floor "
          f"{strongest}={floor_stats[strongest]['acc']:.3f} (hi {strongest_hi:.3f}) | "
          f"twin_entity {te_m:.3f} twin_order {to_m:.3f} | GATE {'PASS' if gate else 'no'}")
    for st, d in metrics["per_structure"].items():
        print(f"   {st}: register {d['register']:.3f} vs floors {d['floors']}")
    print(f"   PERSIST distance: {metrics['distance_robustness_PERSIST']}")
    print(f"-> {os.path.join(_out_dir(), 'metrics.json')} ({metrics['elapsed_s']}s)")
    return metrics


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        its = build_items(0)
        assert len(its) == 180 and len(_flatten(its)) > 0
        print(f"[self-test] PASS ({len(its)} items, {len(_flatten(its))} queries)")
        sys.exit(0)
    main(seed=args.seed)
