"""Witness for the LANDED hdlab.location_register.LocationRegister (spaCy-free SPACE tracking organ).

Landed 2026-08-28 from the integrated `situation_model_has_no_spatial_location_dimension` (SOLVED/EXCELLENT,
owner-DONE). Confirms, scaffold-free on the ACTUAL hdlab organ, the brain-faithful TRACKING computation the experiment
measured (experiments/location_register.py) -- on the ABSTRACT motion-event API (the prose->events extraction is an
experiment-side spaCy adapter; this organ is spaCy-free). Presence intervals maintained over discourse time; where_is /
region-containment answered from the tracked state.

Asserts (deterministic):
  1. WHERE-IS tracking over a multi-entity motion sequence recovers the gold location at every probe (accuracy 1.000).
  2. SCRAMBLED-EVENT-ORDER TWIN fails (destroying temporal order collapses the tracking -> the skill is correctly-ordered
     tracking, not a lexical/last-mention prior).
  3. PERSISTENCE: location is a maintained STATE -- where_is is flat across filler clauses with no motion event.
  4. DEPARTURE: after a depart event where_is returns AWAY (not the stale last-known place); last_seen still recovers
     the last NAMED place.
  5. REGION CONTAINMENT (hierarchy): 'in the study' => is_in_region('house') True & is_in_region('outdoors') False;
     'in the garden' => is_in_region('house') False & is_in_region('outside') True; an unknown fine node => None.

Run: .venv/Scripts/python.exe verification/test_location_register_organ.py
"""
from __future__ import annotations

import os
import random
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.location_register import LocationRegister, DEICTIC_SCENE, AWAY  # noqa: E402


def _gold_where(events, entity, t):
    """Reference tracker: fold the ORDERED events, return the entity's node at t (mirrors the organ's own semantics,
    computed independently here for the accuracy check)."""
    node = DEICTIC_SCENE
    for (e, kind, nd, te) in sorted(events, key=lambda ev: ev[3]):
        if e != entity or te > t:
            continue
        if kind in ("arrive", "stative"):
            node = nd
        elif kind == "return":
            node = nd if (nd is not None and nd != DEICTIC_SCENE) else DEICTIC_SCENE
        elif kind == "present":
            node = DEICTIC_SCENE
        elif kind in ("depart", "absent"):
            node = AWAY
    return node


def main() -> int:
    checks = []
    entities = ["Anna", "Ben", "Cora"]
    n_clauses = 12
    events = [
        ("Anna", "arrive", "kitchen", 2), ("Anna", "depart", None, 5), ("Anna", "return", DEICTIC_SCENE, 8),
        ("Ben", "arrive", "garden", 3), ("Ben", "arrive", "study", 9),
        ("Cora", "stative", "library", 4), ("Cora", "arrive", "orchard", 10),
    ]

    # (1) where-is accuracy over a probe grid.
    reg = LocationRegister().fold(entities, events, n_clauses=n_clauses)
    probes = [(e, t) for e in entities for t in range(n_clauses)]
    hits = sum(1 for (e, t) in probes if reg.where_is(e, t) == _gold_where(events, e, t))
    acc = hits / len(probes)
    checks.append((acc == 1.0, f"[1] WHERE-IS tracking accuracy over {len(probes)} probes: {acc:.3f} (==1.000)"))

    # (2) scrambled-event-order twin fails.
    rng = random.Random(20260828)
    scrambled = list(events)
    # keep the (entity,kind,node) multiset but reassign the TIMES randomly (destroys the ordering signal)
    times = [ev[3] for ev in scrambled]
    rng.shuffle(times)
    twin_events = [(e, k, nd, tt) for (e, k, nd, _), tt in zip(scrambled, times)]
    reg_tw = LocationRegister().fold(entities, twin_events, n_clauses=n_clauses)
    tw_hits = sum(1 for (e, t) in probes if reg_tw.where_is(e, t) == _gold_where(events, e, t))
    tw_acc = tw_hits / len(probes)
    checks.append((acc - tw_acc > 0.15, f"[2] SCRAMBLED-ORDER TWIN fails: register {acc:.3f} vs twin {tw_acc:.3f} (gap {acc - tw_acc:+.3f} > 0.15)"))

    # (3) persistence across filler clauses (Anna in the kitchen from clause 2 until she departs at 5).
    persist = all(reg.where_is("Anna", t) == "kitchen" for t in (2, 3, 4))
    checks.append((persist, f"[3] PERSISTENCE: Anna flat in 'kitchen' across clauses 2..4 (no event) -> {persist}"))

    # (4) departure -> AWAY, not the stale place; last_seen recovers the last named place.
    away_ok = reg.where_is("Anna", 6) == AWAY and reg.where_is("Anna", 7) == AWAY
    lastseen_ok = reg.last_seen("Anna", 6) == "kitchen"
    checks.append((away_ok and lastseen_ok, f"[4] DEPARTURE: Anna@6/7 -> AWAY ({away_ok}); last_seen -> 'kitchen' ({lastseen_ok})"))

    # (5) region containment hierarchy.
    r = LocationRegister().fold(["S", "G", "U"], [
        ("S", "arrive", "study", 1), ("G", "arrive", "garden", 1), ("U", "arrive", "spaceship", 1),
    ], n_clauses=3)
    study_house = r.is_in_region("S", "house", 2) is True and r.is_in_region("S", "outdoors", 2) is False
    garden_out = r.is_in_region("G", "house", 2) is False and r.is_in_region("G", "outside", 2) is True
    unknown_none = r.is_in_region("U", "house", 2) is None
    checks.append((study_house and garden_out and unknown_none,
                   f"[5] REGION CONTAINMENT: study in-house {study_house}; garden outside {garden_out}; unknown-node None {unknown_none}"))

    print("=== witness: hdlab.location_register.LocationRegister (spaCy-free SPACE tracking organ) ===")
    all_pass = True
    for ok, msg in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {msg}")
        all_pass = all_pass and ok
    print(f"\nRESULT: {'ALL CHECKS PASS' if all_pass else 'FAIL'} ({sum(1 for ok, _ in checks if ok)}/{len(checks)})")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
