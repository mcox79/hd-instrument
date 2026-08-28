"""exp_entity_store_schema_gist_v1 -- the DEEPER, brain-RIGHT fix for the busy-entity fan (Radvansky
2017): the fan tracks the number of separate EVENT MODELS, not fact count. The brain integrates ROUTINE
events into one continuously-updated per-entity GIST (schema; Gilboa & Marlatte 2017 -- regular material
graduates OUT of episodic indexing) and keeps only NOVEL/ATYPICAL events as sharp episodic traces.

This is the frontier follow-on to `the_entity_store_is_a_dense_bundle_that_fans` (whose SOLVED result --
finer conjunctive key + set-return -- is correct-in-SHAPE but a degenerate special case per the deeper
brain drill). Here we test the SYSTEMS-LEVEL fix that the drill named highest-leverage.

THE CLAIM (brain-faithful): what makes a busy character's memory usable is NOT a smarter N-way index --
it is that you remember the DISTINCTIVE things sharply (episodic) while the routine blurs into "they
usually did X" (gist). So the right measurement is: does routing routine events to a gist keep the
ATYPICAL (memorable) events recoverable by UN-CROWDING the episodic store, with the gain CONCENTRATED in
high-routine (coherent) entities?

ARMS (recall of the ATYPICAL event subset -- the memorable ones -- as store load N grows):
  ALL_EPISODIC     : dense FHRR bundle of ALL events (the current organ). The atypical events compete
                     with every routine event -> superposition fan.
  SCHEMA_GIST      : route ROUTINE events (verb == the entity's running gist mode) to a per-entity gist;
                     only ATYPICAL events enter the episodic bundle -> un-crowded -> atypical recall stays
                     sharp. (Radvansky in-place event-model update.)
  RANDOM_ROUTE_TWIN: route a RANDOM matched fraction to the gist (info-free: same number removed, but not
                     by typicality) -> removes atypical events too -> atypical recall LOSES. The control
                     that isolates TYPICALITY-routing from mere store-shrinking.

DECISIVE (pre-registered, from the drill): HARD-PASS = SCHEMA_GIST atypical-recall > ALL_EPISODIC
CI-separated, gain RISING with entity coherence, and > RANDOM_ROUTE_TWIN CI-separated. HARD-FAIL = no
separation, or uniform gain regardless of coherence.

Run: .venv/Scripts/python.exe experiments/exp_entity_store_schema_gist_v1.py --run
     ... --self-test
ASCII only. Synthetic construction proof on the real FHRR organ codes. Writes ONLY to
data/entity_store_sparse_fan/. NO hdlab/ write.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from typing import Dict, List, Tuple

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments.exp_litbank_entity_tracking_end_to_end_v1 import D as FHRR_D  # noqa: E402

OUTDIR = os.path.join(REPO_ROOT, "data", "entity_store_sparse_fan")
SEED = 20260827


def _torch_gen(seed):
    import torch
    g = torch.Generator(); g.manual_seed(seed); return g


def _make_entity(N: int, coherence: float, n_typical: int, rng: np.random.Generator):
    """Build one entity's N events. `coherence` = fraction ROUTINE (verb drawn from a small typical set
    the gist can predict); the rest ATYPICAL (unique, memorable verbs). Returns (events, verb_vocab,
    is_atypical[]). Each event = (slot, verb)."""
    n_routine = int(round(coherence * N))
    typical = [f"typ{i}" for i in range(n_typical)]
    events = []
    is_aty = []
    # routine events: repeats of the typical verbs (the entity's habitual behavior)
    for i in range(n_routine):
        events.append(typical[i % n_typical]); is_aty.append(False)
    # atypical events: unique, one-off memorable actions
    for i in range(N - n_routine):
        events.append(f"aty{i}"); is_aty.append(True)
    # shuffle event order (assign to slots 0..N-1)
    order = rng.permutation(N)
    events = [events[i] for i in order]
    is_aty = [is_aty[i] for i in order]
    verb_vocab = sorted(set(events))
    return events, verb_vocab, is_aty


def _episodic_recall(events: List[str], verb_vocab: List[str], keep_mask: List[bool], seed: int):
    """Dense FHRR bundle of the events where keep_mask is True; decode each KEPT event by its slot.
    Returns {slot: correct?} for kept slots (a slot not kept is not recoverable episodically)."""
    from hdlab.situation_model_accumulate import make_situation_register
    N = len(events)
    reg = make_situation_register(list(verb_vocab), FHRR_D, _torch_gen(seed),
                                  max_event_slots=N, backend="multibank", n_banks=8)
    for s, v in enumerate(events):
        if keep_mask[s]:
            reg.add_event("0", v, s)
    out = {}
    for s, v in enumerate(events):
        if keep_mask[s]:
            try:
                pv, _ = reg.decode("0", s)
            except KeyError:
                pv = None
            out[s] = int(pv == v)
    return out


def _run_arm(events, verb_vocab, is_aty, arm, seed, rng):
    """Return recall accuracy on the ATYPICAL subset for one arm.

    ALL_EPISODIC: keep everything episodic -> atypical events compete with all routine events.
    SCHEMA_GIST : keep only ATYPICAL events episodic (routine -> gist, which answers them by its mode
                  and does NOT crowd the episodic store); atypical recall = episodic recall (un-crowded).
    RANDOM_ROUTE_TWIN: remove a RANDOM matched fraction to the gist; an atypical event routed to the
                  gist is NOT recoverable (the gist holds only the aggregate typical verb) -> counts wrong.
    """
    N = len(events)
    if arm == "ALL_EPISODIC":
        keep = [True] * N
        rec = _episodic_recall(events, verb_vocab, keep, seed)
        aty = [rec[s] for s in range(N) if is_aty[s]]
    elif arm == "SCHEMA_GIST":
        keep = [is_aty[s] for s in range(N)]           # only atypical enter the episodic store
        rec = _episodic_recall(events, verb_vocab, keep, seed)
        aty = [rec[s] for s in range(N) if is_aty[s]]  # every atypical event is kept -> all recoverable
    elif arm == "RANDOM_ROUTE_TWIN":
        n_routine = sum(1 for a in is_aty if not a)
        # remove the SAME number of events as SCHEMA_GIST routes to the gist, but chosen at RANDOM
        remove_idx = set(rng.choice(N, size=n_routine, replace=False).tolist())
        keep = [s not in remove_idx for s in range(N)]
        rec = _episodic_recall(events, verb_vocab, keep, seed)
        # an atypical event routed to the gist (removed) is unrecoverable -> scored 0
        aty = [rec[s] if keep[s] else 0 for s in range(N) if is_aty[s]]
    else:
        raise ValueError(arm)
    return float(np.mean(aty)) if aty else float("nan")


def run(N=800, n_typical=3, coherences=(0.0, 0.5, 0.75, 0.9, 0.97), n_entities=40, n_boot=2000,
        seed=SEED) -> Dict:
    """For each coherence level, build n_entities entities and measure ATYPICAL-event recall per arm,
    bootstrap over entities."""
    arms = ["ALL_EPISODIC", "SCHEMA_GIST", "RANDOM_ROUTE_TWIN"]
    report = {"config": {"N": N, "n_typical": n_typical, "n_entities": n_entities, "n_boot": n_boot},
              "by_coherence": {}}
    for c in coherences:
        if c >= 1.0:
            continue
        per_ent = {a: [] for a in arms}   # per-entity atypical recall
        for e in range(n_entities):
            rng = np.random.default_rng(seed + int(c * 1000) * 1000 + e)
            events, vv, is_aty = _make_entity(N, c, n_typical, rng)
            if not any(is_aty):
                continue
            for a in arms:
                per_ent[a].append(_run_arm(events, vv, is_aty, a, seed + e, rng))
        # bootstrap over entities
        ne = len(per_ent["ALL_EPISODIC"])
        rng_b = np.random.default_rng(seed + 7)
        boot = [rng_b.integers(0, ne, ne) for _ in range(n_boot)]
        means = {a: float(np.nanmean(per_ent[a])) for a in arms}
        arr = {a: np.array(per_ent[a]) for a in arms}
        gist_minus_all = []
        gist_minus_twin = []
        for idx in boot:
            gist_minus_all.append(np.nanmean(arr["SCHEMA_GIST"][idx]) - np.nanmean(arr["ALL_EPISODIC"][idx]))
            gist_minus_twin.append(np.nanmean(arr["SCHEMA_GIST"][idx]) - np.nanmean(arr["RANDOM_ROUTE_TWIN"][idx]))
        gma = np.array(gist_minus_all); gmt = np.array(gist_minus_twin)
        def ci(x):
            return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))]
        report["by_coherence"][f"c={c}"] = {
            "means": means,
            "SCHEMA_GIST_minus_ALL_EPISODIC": {"mean": float(gma.mean()), "ci": ci(gma),
                "hw": float((np.percentile(gma, 97.5) - np.percentile(gma, 2.5)) / 2),
                "sep": "ABOVE" if np.percentile(gma, 2.5) > 0 else ("BELOW" if np.percentile(gma, 97.5) < 0 else "NOT_SEP")},
            "SCHEMA_GIST_minus_RANDOM_TWIN": {"mean": float(gmt.mean()), "ci": ci(gmt),
                "hw": float((np.percentile(gmt, 97.5) - np.percentile(gmt, 2.5)) / 2),
                "sep": "ABOVE" if np.percentile(gmt, 2.5) > 0 else ("BELOW" if np.percentile(gmt, 97.5) < 0 else "NOT_SEP")},
        }
    return report


def self_test() -> Dict:
    # a high-coherence entity: schema-gist must recover atypical events better than all-episodic, and the
    # random-route twin must lose (it removes atypical events too).
    rng = np.random.default_rng(1)
    events, vv, is_aty = _make_entity(N=800, coherence=0.9, n_typical=3, rng=rng)
    all_ep = _run_arm(events, vv, is_aty, "ALL_EPISODIC", 1, np.random.default_rng(2))
    gist = _run_arm(events, vv, is_aty, "SCHEMA_GIST", 1, np.random.default_rng(2))
    twin = _run_arm(events, vv, is_aty, "RANDOM_ROUTE_TWIN", 1, np.random.default_rng(2))
    assert gist > all_ep, f"schema-gist {gist} must beat all-episodic {all_ep} on atypical recall"
    assert gist > twin, f"schema-gist {gist} must beat random-route twin {twin}"
    # a fully-heterogeneous entity (coherence 0): gist has nothing routine to route -> ~no gain
    events0, vv0, aty0 = _make_entity(N=800, coherence=0.0, n_typical=3, rng=np.random.default_rng(3))
    all0 = _run_arm(events0, vv0, aty0, "ALL_EPISODIC", 1, np.random.default_rng(4))
    gist0 = _run_arm(events0, vv0, aty0, "SCHEMA_GIST", 1, np.random.default_rng(4))
    return {"high_coherence": {"ALL_EPISODIC": round(all_ep, 3), "SCHEMA_GIST": round(gist, 3),
                               "RANDOM_ROUTE_TWIN": round(twin, 3)},
            "zero_coherence": {"ALL_EPISODIC": round(all0, 3), "SCHEMA_GIST": round(gist0, 3),
                               "gain": round(gist0 - all0, 3)}}


def _dump(name, obj):
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=float)
    print(f"[wrote] {os.path.join(OUTDIR, name)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--N", type=int, default=800)
    args = ap.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), indent=2, default=float)); return
    if args.run:
        rep = run(N=args.N)
        print(json.dumps(rep, indent=2, default=float)); _dump("schema_gist.json", rep); return
    ap.print_help()


if __name__ == "__main__":
    main()
